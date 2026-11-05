# TROUBLESHOOTING — Lab 9

Work top to bottom; the rows are ordered the way symptoms usually appear
while building the lab. Every check is a command you can run on the
router in front of you — no guesswork.

| # | Symptom | Likely cause | Check |
|---|---------|--------------|-------|
| 1 | Neighbour stuck in **Idle** | Peer IP unreachable or wrong: interface down, wrong transit address, cable on the wrong port | Ping the transit-link address from the border router (`ping 172.16.100.2` from R2). Then `show ip interface brief` — the transit interface must be up/up with the exact /30 address from the addressing table |
| 2 | Neighbour stuck in **Active** | `remote-as` mismatch — this is exactly what the drill in VERIFICATION step 5 creates — or BGP is not configured on the far side at all | Compare the `neighbor … remote-as` line on both borders side by side (R2 must say 65002, R3 must say 65001). `show logging` for `%BGP-3-NOTIFICATION` — a remote-AS mismatch shows up there |
| 3 | Session **Established**, but a LAN prefix is missing from `show ip bgp` | The `network` statement does not exactly match a route in the advertising router's own routing table | On the border that should advertise it: `show ip route` — the prefix *and mask* must match the `network` statement exactly (192.168.11.0 **/24**, learned via OSPF). BGP never advertises a prefix it cannot already reach |
| 4 | BGP healthy on both borders, but the PC ping fails | The internal routers (R1/R4) have no route to the far LAN and no default — only the borders learn BGP routes in the base design | `show ip route` on R1: no far-LAN route. Apply `configs/OPTIONAL-end-to-end-defaults.txt` (static default toward the border), or redistribute BGP into OSPF at the borders. Also confirm each PC's default gateway (192.168.11.1 / 192.168.12.1) |
| 5 | An OSPF route is missing inside an AS | Wrong wildcard mask in a `network` statement, or the transit link was added to OSPF by mistake | `show ip ospf interface brief` — only the internal link, LAN and loopback should appear. Wildcards: /24 → `0.0.0.255`, /30 → `0.0.0.3`, /32 host → `0.0.0.0` |
| 6 | Neighbour flaps Established ↔ Idle | Physical/link instability on the transit link, or the config was edited mid-session (the drill does this on purpose) | `show ip interface brief` on both borders; check the cable connects R2 Gig0/1 ↔ R3 Gig0/0 and nothing else. Re-check after any config change with `show ip bgp summary` — give it a few seconds to renegotiate |
| 7 | `show ip bgp` lists the prefix but `show ip route bgp` is empty | The route was received but not installed as best path (e.g. it is also known via another source with better administrative distance) | `show ip bgp` — a `>` marks the best path; only best paths are installed. Compare with `show ip route` to see which source won |

## The habit this table is teaching

State first, cause second: `show ip bgp summary` tells you *which stage*
failed (never connected = Idle, connecting = Active, working =
Established), and each stage has a short list of causes. That is the
same discipline as reading any NOC alarm — identify the layer and state
before changing anything.
