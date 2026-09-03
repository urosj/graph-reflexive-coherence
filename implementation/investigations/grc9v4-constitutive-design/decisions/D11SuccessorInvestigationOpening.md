# D11 Successor Investigation Opening

**Gate:** D11-OPEN
**Status:** Accepted bounded successor opening
**Predecessor:** `GRC9V4-CD-D10.2-v1`
**Decision digest:** `51ba66d5404dee29f7b2a7dcd9501b43711fce0d47d466118945b5a0f71ac23a`
**Scientific result:** None

## Purpose

This append-only record opens two source-level investigations exposed by the
September 2026 GRCV4 specification-stack audit. It does not alter the accepted
D10.2 payload, promote either proposed solution, or reopen unrelated D10
claims.

The accepted forensic surface was queried before this opening. It confirmed
that the relevant D10.2 contracts remain
`indeterminate_requires_review`; no accepted graph node supplies the missing
Candidate C baseline-current law or a collision-free GRC9V4 port allocation.
The external audit is therefore a finding and routing input, not backward
scientific evidence.

The opening is paired with the machine-auditable
[D11 claim/debt/authority routing record](D11ClaimDebtAndAuthorityRouting.md).
That record carries the exact 39 current claims, 29 historical claim nodes, 29
debt transformations, 11 verification obligations, and the full D10.2
current-population contract counts into both successor gates. The D11 findings
are additive debts; they do not erase or reclassify inherited debt or claims.

## Authorized Sequence

```text
D11-C
  -> D11-G9
  -> accepted-result propagation into the GRC-v4 paper
  -> affected V4 specification extraction
  -> final specification audit
```

The gates remain separate:

- [D11-C](D11CCandidateCBaselineTransportAndMobilityClosure.md) is the active,
  graph-generic GRCV4 constitutive investigation.
- [D11-G9](D11G9CanonicalExpansionPortAllocationClosure.md) is a queued,
  GRC9V4-only mechanical specialization investigation. It may become active
  only after an accepted D11-C result is recorded.

## Reopened Boundaries

D11-C starts at the missing Candidate C direct-transport authority. Its
bounded consequences reach the Candidate C current and realization contracts,
but it does not reopen Candidate A, the common resource ledger, or unrelated
D10 claims.

D11-G9 starts at
`D10.2-EC-PARENT-GRC9-MECHANICAL-EXPANSION`. Its bounded consequences reach
GRC9V4 port identity, capacity, event transport, and target readmission. It is
not a repair to GRC9, GRC9V3, or their historical records.

## Existing Specification Text

The formulas already present in `specs/grc-v4-spec.md` and
`specs/grc-9-v4-spec.md` are retained as preregistered candidates:

- `candidate_c_log_sector_potential_flow_v1`; and
- `grc9v4_collision_free_v1`.

They are not accepted authority while the corresponding D11 gate is open.
If a gate selects a different result, the paper and affected V4 spec clauses
will be changed during the ordered propagation step. No candidate is removed
merely because the investigation has opened.

## Authority Boundary

```text
D11-C investigation authorized = true
D11-G9 investigation authorized now = false
D11-G9 authorized after accepted D11-C = true
paper correction authorized before accepted D11 results = false
D11-dependent specification authority = provisional only
implementation plan authorized = false
implementation authorized = false
runtime or src/tests change authorized = false
older GRC/GRC9/GRC9V3 artifacts mutable = false
```

This opening accepts a research route, not a constitutive or mechanical
answer. Each scientific result requires its own successor decision record and
human acceptance.
