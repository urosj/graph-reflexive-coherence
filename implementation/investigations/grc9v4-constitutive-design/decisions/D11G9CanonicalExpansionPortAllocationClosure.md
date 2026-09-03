# D11-G9 Canonical GRC9 Expansion Port-Allocation Closure

**Gate:** D11-G9
**Status:** Queued, preregistered
**Predecessor:** `GRC9V4-CD-D11-OPEN-v1`
**Preregistration digest:** `856e3db9ffa6a09080f7af0b9753be222ab986599855168a4fe9d218490c1635`
**Inherited authority:** [`GRC9V4-CD-D11-CLAIM-DEBT-ROUTING-v1`](D11ClaimDebtAndAuthorityRouting.md)
**Local debt:** `D11-G9-DEBT-CANONICAL-PORT-ALLOCATION`
**Activation:** Requires an accepted D11-C result
**Result selected:** No

## Gate Question

What exact, collision-free GRC9V4 expansion map preserves the intended
column-family semantics while deterministically allocating:

- the three core-to-satellite internal edges;
- the nine redirected old boundary edges; and
- every additional-node attachment edge?

The accepted GRC9 source fixes column-preserving redirection but places the
internal endpoint `(s_2, 5)` on the same live endpoint used by redirected old
port 5. It therefore does not define a valid canonical saturated-node
expansion.

This queued debt is additive to the complete D10.2 claim, debt, and
verification topology. Its claim bearings are consistency constraints only;
no inherited claim changes status while D11-G9 remains queued.

## Scope Boundary

This is a GRC9V4 specialization investigation. It is not graph-generic GRCV4,
and it is not a repair to GRC9 or GRC9V3. The historical paper and legacy
specification remain read-only provenance and reduction targets.

The earliest reopened contract is
`D10.2-EC-PARENT-GRC9-MECHANICAL-EXPANSION`. Consequences are limited to
GRC9V4 ordered endpoint allocation, capacity accounting, deterministic event
identity, resource/history transport, hierarchy receipts, and target
readmission. The generic V4 topology-event contract remains unchanged.

## Required Closure Surface

An accepted result must freeze:

1. every core and satellite internal endpoint;
2. all nine old-edge redirected endpoints;
3. the additional-node column, parent, parent-port, child-port, stable-ID,
   edge-ID, and orientation rules;
4. exact one-edge-per-live-endpoint occupancy;
5. capacity accounting for the base module and arbitrary admitted target size;
6. column-family preservation for old boundary edges;
7. internal-edge mobility initialization;
8. resource, Candidate A history, Candidate C reconstruction, and persistent
   $K_4$ history dispositions;
9. deterministic replay and hierarchy receipts; and
10. target reconstruction and readmission before atomic commit.

At minimum, the selected map must prove

$$
\text{every live target endpoint }(v,r)\text{ occurs in at most one edge}.
$$

## Preregistered Candidates

The candidates are alternatives. Their order is not a ranking.

### G9-P1 — Cyclic-successor satellite derangement

This is the solution already written in the provisional GRC9V4 spec:

$$
(c,2)\leftrightarrow(s_1,5),\qquad
(c,5)\leftrightarrow(s_2,6),\qquad
(c,8)\leftrightarrow(s_3,4).
$$

Every old port $r\in\mathcal C_b$ remains redirected to `(s_b, r)`. The
satellite internal ports use the center row and the cyclic successor column,
so none lies in its satellite's old-boundary column. Its preregistered identity
is `grc9v4_collision_free_v1`.

### G9-P2 — Cyclic-predecessor satellite derangement

Use the inverse center-row cycle:

$$
(c,2)\leftrightarrow(s_1,6),\qquad
(c,5)\leftrightarrow(s_2,4),\qquad
(c,8)\leftrightarrow(s_3,5).
$$

This preserves the same old-boundary column rule but reverses the chosen
derangement orientation. Its event-identity and coarse/chart consequences must
be compared with G9-P1 rather than treated as equivalent by inspection.

### G9-P3 — Minimal center-port collision repair

Retain the historical satellite-center attachments for $s_1$ and $s_3$ and
move only the colliding $s_2$ endpoint:

$$
(c,2)\leftrightarrow(s_1,5),\qquad
(c,5)\leftrightarrow(s_2,4),\qquad
(c,8)\leftrightarrow(s_3,5).
$$

This minimizes endpoint edits but gives up the three-satellite derangement
symmetry. The investigation must decide whether minimal historical change or
uniform chart semantics controls canonicality.

### G9-P0 — Bounded unresolved disposition

If no candidate earns the complete map, GRC9V4 mechanical expansion remains
non-implementation-ready. No implementation may invent a port repair under the
same expansion-policy identity.

## Pressure and Acceptance Tests

Each positive candidate must be expanded into a complete deterministic event
fixture and pressure-tested for:

- unique target endpoint occupancy;
- preservation of all nine old boundary edges and their column families;
- exact base and larger-module capacity accounting;
- stable output under replay, input edge ordering, and graph serialization;
- explicit stable node/edge IDs, tie-breaking, and orientation;
- complete resource, mobility, candidate/history, reset, and charge receipts;
- Candidate C target reconstruction using the accepted D11-C result;
- target-profile readmission and failure atomicity; and
- isolation from every GRC9 and GRC9V3 source file.

The accepted result must state why the chosen map, rather than another
collision-free map, owns the canonical GRC9V4 policy identity. Collision
freedom alone is necessary but does not select a canonical representative.

## Propagation Rule

Only an accepted D11-G9 successor may be propagated. The order is:

```text
accepted D11-G9 record
  -> GRC-v4 substrate paper Appendix A
  -> GRC9V4 specialization clauses
  -> source manifest and expansion fixtures
  -> final specification audit
```

Until then, `grc9v4_collision_free_v1` remains visible in the specification
solely as candidate G9-P1 and is not conformance authority.
