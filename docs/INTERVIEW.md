# INTERVIEW — BGP questions this lab prepares you for

Concise model answers, written to be said out loud. Every answer is
backed by something you actually configured in Lab 9 — if an answer
below goes beyond the lab, it says so.

## 1. What is an Autonomous System?

A network under one organisation's control, with one routing policy,
identified by an AS number. Inside my lab, AS 65001 is "the enterprise"
and AS 65002 is "the peer/ISP". Routing *inside* an AS is the owner's
business; BGP is how ASes tell each other which prefixes they can reach.

## 2. eBGP vs iBGP — what's the difference?

Same protocol, different relationship. **eBGP** runs between routers in
*different* ASes — in the lab, R2 (AS 65001) ↔ R3 (AS 65002). **iBGP**
runs between routers in the *same* AS so they can share what eBGP
learned. The lab uses eBGP only; iBGP is the honest boundary of what
I've built so far.

## 3. Why BGP between organisations but OSPF inside them?

They solve different problems. OSPF is fast, detailed and trusting — it
floods the full topology and assumes one administration. BGP is slow,
policy-driven and sceptical: it exchanges *reachability* ("I can reach
192.168.12.0/24 via AS 65002"), not topology, and it scales to the whole
internet. You would never give an ISP your internal topology, and OSPF
would never scale between providers.

## 4. Walk me through the BGP neighbour states.

**Idle** — BGP is configured but not even trying (usually the peer is
unreachable or not yet configured). **Active** — it's trying to open
the TCP session (port 179) and failing or waiting; a wrong remote-AS
holds you here. **Established** — the session is up and routes are
being exchanged. In the lab's drill, changing R3's remote-as to 65003
drops the session out of Established immediately.

## 5. What does `show ip bgp summary` tell you?

One line per neighbour: the peer's IP and AS number, how long the
session has been up, how many prefixes were received, and — the column
that matters most — the **state**. A number in the state column means
Established and shows the prefix count; the word Idle or Active means
the session is down and tells you which stage to troubleshoot.

## 6. How does a prefix get into BGP with the `network` statement?

The router advertises the prefix **only if it already has that exact
prefix, with that exact mask, in its own routing table**. In the lab,
R2 advertises 192.168.11.0/24 because OSPF taught it that route from
R1 — the OSPF→BGP hand-off. If OSPF breaks, the BGP advertisement
silently disappears, which is why "Established but prefix missing"
means "check the IGP first".

## 7. What is the next hop of a route learned over eBGP?

The neighbouring border router's transit address. On R2, the route to
192.168.12.0/24 has next hop 172.16.100.2 (R3). The router must be able
to *reach* that next hop for the route to be usable — one reason the
transit link uses a small dedicated subnet.

## 8. Why is the eBGP link a /30?

A point-to-point link needs exactly two addresses; a /30 provides them
(two usable, one network, one broadcast) and wastes nothing. It also
makes intent obvious: this subnet exists only to carry the session
between the two ASes, which is why it is deliberately kept *out* of
OSPF in the lab — it belongs to BGP, not to either AS's interior.

## 9. Name some BGP path attributes. (awareness level)

**AS_PATH** — the list of ASes a route has crossed; used for loop
prevention and path choice (you can see it in `show ip bgp`: the lab's
routes show a single-AS path). **LOCAL_PREF** — how an AS prefers to
*exit* toward a prefix (iBGP only). **MED** — a hint to a neighbour
about how you'd like traffic to *enter*. I know what they do; tuning
them is beyond this lab, and I'd say exactly that in an interview.

## 10. Tell me about a time you troubleshot a routing problem.

Use the drill (VERIFICATION step 5) as the story: "I deliberately
misconfigured the remote AS on one side of an eBGP peering. The session
dropped out of Established, the far LAN's route disappeared, and
`show ip bgp summary` plus the BGP notification messages pointed at a
session-level cause rather than a link problem. I compared the
`remote-as` values on both borders, found the mismatch, fixed it, and
verified the session re-established and the route returned." Symptom →
state → evidence → fix → verification. That structure is the answer,
whatever the technology.

---

*Scope reminder: these answers cover the lab as built — single eBGP
session, OSPF inside each AS, `network`-statement advertisement.
Anything deeper (route reflectors, confederations, communities,
production ISP peering) is study material, not lab experience, and is
labelled that way here on purpose.*
