#!/usr/bin/env python3
"""
LAB 9 - BGP Fundamentals: build Lab-9-BGP-Fundamentals.pkt

Generates the Packet Tracer topology for the Lab 9 eBGP lab using pktlib
(pure-Python .pkt writer for Packet Tracer 8.2):

    PC-A - SW-A - R1 --- R2 ===(eBGP)=== R3 --- R4 - SW-B - PC-B
           AS 65001 (OSPF inside)   |   AS 65002 (OSPF inside)
                                172.16.100.0/30

Startup configs are read from ../configs/*.txt so the .pkt and the
paste-ready configs can never drift apart. After saving, the script
re-opens the generated file and lists what it finds (round-trip check).

Usage:
    pip install pktlib
    python3 scripts/build_topology.py

Output: ../Lab-9-BGP-Fundamentals.pkt

NOTE: generation + round-trip parsing prove the file is well-formed.
They do NOT prove the topology runs in real Cisco Packet Tracer - see
docs/VERIFICATION.md for the in-Packet-Tracer checklist.
"""

from pathlib import Path
import pktlib

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = ROOT / "configs"
OUT = ROOT / "Lab-9-BGP-Fundamentals.pkt"

# Lines that belong to a paste session, not to config mode itself.
WRAPPER_LINES = {"enable", "configure terminal", "end", "write memory"}


def load_config(filename: str) -> str:
    """Read a paste-ready config file and return the config-mode body."""
    lines = []
    for raw in (CONFIGS / filename).read_text().splitlines():
        if raw.strip() in WRAPPER_LINES:
            continue
        lines.append(raw)
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    net = pktlib.new(edition="8.2")

    # ---- Devices (left to right: AS 65001 -> AS 65002) -------------------
    pca = net.pc("PC-A", at=(100, 320), ip="192.168.11.10/24",
                 gateway="192.168.11.1")
    swa = net.switch("SW-A", "2960-24TT", at=(230, 320))
    r1 = net.router("R1", "2911", at=(370, 260))
    r2 = net.router("R2", "2911", at=(520, 260))
    r3 = net.router("R3", "2911", at=(700, 260))
    r4 = net.router("R4", "2911", at=(850, 260))
    swb = net.switch("SW-B", "2960-24TT", at=(990, 320))
    pcb = net.pc("PC-B", at=(1120, 320), ip="192.168.12.10/24",
                 gateway="192.168.12.1")

    # ---- Startup configs (single source of truth: configs/*.txt) --------
    r1.config(load_config("R1-Enterprise-Internal.txt"))
    r2.config(load_config("R2-Enterprise-Border.txt"))
    r3.config(load_config("R3-Peer-Border.txt"))
    r4.config(load_config("R4-Peer-Internal.txt"))

    # ---- Links (per the addressing table in README.md) -------------------
    net.connect(pca, "FastEthernet0", swa, "FastEthernet0/1", cable="straight")
    net.connect(swa, "FastEthernet0/24", r1, "GigabitEthernet0/0", cable="straight")
    net.connect(r1, "GigabitEthernet0/1", r2, "GigabitEthernet0/0", cable="cross")
    net.connect(r2, "GigabitEthernet0/1", r3, "GigabitEthernet0/0", cable="cross")
    net.connect(r3, "GigabitEthernet0/1", r4, "GigabitEthernet0/0", cable="cross")
    net.connect(r4, "GigabitEthernet0/1", swb, "FastEthernet0/24", cable="straight")
    net.connect(swb, "FastEthernet0/1", pcb, "FastEthernet0", cable="straight")

    net.save(OUT)
    print(f"saved: {OUT} ({OUT.stat().st_size} bytes)")

    # ---- Round-trip verification -----------------------------------------
    check = pktlib.load(OUT, strict=False)
    print(f"round-trip: {len(check.devices)} devices, {len(check.links)} links")
    for d in check.devices:
        print(f"  device: {d.name} ({d.model})")
    for link in check.links:
        print(f"  link:   {link}")
    r2cfg = "\n".join(check.device("R2").running_config)
    assert "router bgp 65001" in r2cfg, "BGP block missing from R2 after round-trip"
    assert "neighbor 172.16.100.2 remote-as 65002" in r2cfg, "eBGP neighbour missing"
    print("round-trip: R2 BGP config present (AS 65001, neighbour 172.16.100.2)")


if __name__ == "__main__":
    main()
