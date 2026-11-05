# VERIFICATION — Lab 9 checklist

Run these **in Cisco Packet Tracer** (open `Lab-9-BGP-Fundamentals.pkt`,
or your own build from [BUILD.md](BUILD.md)). Tick each box only when you
have actually seen the expected output — checked results are what turn a
generated topology into a verified lab.

> Status: **this checklist has NOT been run in Packet Tracer yet.**
> The `.pkt` was generated programmatically and round-trip parsed
> (8 devices, 7 links), which proves the file is well-formed — not that
> the session comes up. Record the date and results here once run.

## 1. OSPF inside each AS

- [ ] **R2:** `show ip route` — 192.168.11.0/24 appears as an **O** (OSPF)
      route via 10.1.12.1.
- [ ] **R3:** `show ip route` — 192.168.12.0/24 appears as an **O** route
      via 10.2.34.2.
- [ ] **R1 and R4:** `show ip ospf neighbor` — the internal neighbour is
      in state **FULL**.
- [ ] **R2 and R3:** the 172.16.100.0/30 transit network is **not** in
      OSPF on either border router (by design — it is BGP-only).

## 2. eBGP session

- [ ] **R2:** `show ip bgp summary` — neighbour 172.16.100.2, AS 65002,
      state **Established** (a prefix count in the last column, not
      Idle/Active).
- [ ] **R3:** `show ip bgp summary` — neighbour 172.16.100.1, AS 65001,
      state **Established**.

## 3. BGP routes exchanged

- [ ] **R2:** `show ip bgp` — 192.168.12.0/24 is present, next hop
      172.16.100.2, AS path `65002`.
- [ ] **R3:** `show ip bgp` — 192.168.11.0/24 is present, next hop
      172.16.100.1, AS path `65001`.
- [ ] **R2:** `show ip route bgp` — 192.168.12.0/24 installed as a **B**
      route.
- [ ] **R3:** `show ip route bgp` — 192.168.11.0/24 installed as a **B**
      route.

Steps 1–3 are the pass mark for the base lab: OSPF healthy inside both
ASes, one eBGP session Established, and each border holding the other
AS's LAN prefix.

## 4. End-to-end (needs one deliberate extra step)

Before the extra step, check what the internal routers know:

- [ ] **R1:** `show ip route` — there is **no** route to 192.168.12.0/24
      and no default route. Same on **R4** for 192.168.11.0/24.

That is by design, and it is the most instructive moment in the lab:
only the border routers speak BGP, so only they learn the far LAN.
A PC-to-PC ping stops at the internal router, which has nowhere to send
it. Real networks solve this in one of two standard ways:

1. **Default route toward the border** (used here), or
2. **Redistribute BGP into OSPF** at the border routers.

Apply the defaults from `configs/OPTIONAL-end-to-end-defaults.txt`
(one static route on R1, one on R4), then:

- [ ] **PC-A:** `ping 192.168.12.10` (PC-B) — replies received.
- [ ] **PC-B:** `ping 192.168.11.10` (PC-A) — replies received.
- [ ] **R1:** `show ip route` — the far LAN is reached via the static
      default (`S*`) toward R2. Same idea on R4 toward R3.

If a ping still fails, work [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
row by row — and write down where the packet stopped. That trace *is*
the troubleshooting skill this lab exists to teach.

## 5. The misconfiguration drill (guided exercise)

Purpose: see a BGP failure, name its state, fix it. Do this **after**
steps 1–4 pass, so you have a known-good baseline.

1. On **R3**, change the neighbour's remote AS to a wrong value:
   ```
   configure terminal
   router bgp 65002
    neighbor 172.16.100.1 remote-as 65003
   end
   ```
2. - [ ] **R3 and R2:** `show ip bgp summary` — the session drops out of
      **Established** (expect Idle/Active cycling). Note the state and
      any `%BGP-3-NOTIFICATION` messages in the log (`show logging`).
3. - [ ] Confirm the data-plane symptom: the far LAN's route disappears
      from `show ip route bgp`.
4. Fix it — put the correct AS back:
   ```
   configure terminal
   router bgp 65002
    neighbor 172.16.100.1 remote-as 65001
   end
   ```
5. - [ ] Session returns to **Established** and the far LAN route is back.
6. Write up, in your own words: the symptom, the state you saw, the
   command that identified the cause, and the fix. That paragraph is the
   answer to "tell me about a time you troubleshot a routing problem."

## Results log

| Date | Run by | Steps passed | Notes |
|------|--------|--------------|-------|
| — | — | — | Not yet run in Packet Tracer. |
