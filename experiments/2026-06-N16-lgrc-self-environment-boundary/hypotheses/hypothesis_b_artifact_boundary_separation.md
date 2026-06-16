# Hypothesis B - Artifact Basin-Boundary Stability

## Claim

An artifact-level basin-boundary candidate can remain distinguishable across
selected boundary-state/challenge interaction cells under bounded drift,
freshness, budget, dependency-trace, and replay constraints.

## Required Evidence

- A frozen boundary policy defining internal-state fields, external-state
  fields, boundary-crossing trace fields, budget surface, and replay digest
  scope.
- Common matrix-cell rows for quiet boundary calibration, challenge sweep,
  boundary-state sweep, and selected interaction probes.
- Boundary-state axis values B0-B4 and challenge-class axis values C0-C5.
- Row-level `row_decision` values: `supported`, `blocked`, `partial`,
  `rejected`, or `not_applicable`.
- Enum-frozen `external_state_role` values: `background`, `resource`,
  `perturbation`, `structured_external_state`, `shared_medium`,
  `coupling_channel`, `mixed`, and `not_applicable`.
- Explicit `row_decision` / `boundary_claim_allowed` constraints, including
  fail-closed `blocked`, `rejected`, and `not_applicable` rows.
- Field-level dependency traces for all emitted boundary fields.
- Controls showing that relabels, hidden state injection, missing side state,
  stale state, and untracked crossings fail closed.
- Artifact-only, snapshot/load, and order-inversion replay.
- A native boundary requirements synthesis recording coherence margin,
  internal support, leakage, repair/reabsorption, flux balance,
  structured-external-coherence rejection, and inter-basin separation
  requirements.
- B3 repair/reabsorption rows unlocked only after B2 has been evaluated under
  C0, C1, and C2, or after those B2 rows produce explicit blockers.
- B4 directional-flux rows treated as partial or not applicable when the
  multi-basin substrate is not sufficiently source-backed.
- Requirements synthesis mode fields:
  `synthesis_mode`, `included_iterations`, `deferred_iterations`, and
  `final_ap6_closeout_allowed`.

## Controls

- Resource relabel as self blocked.
- Self-support relabel as external state blocked.
- Untracked boundary crossing blocked.
- Boundary drift outside frozen policy blocked.
- Structured external coherence relabel blocked.
- Multi-basin merge or leakage relabel blocked.

## Non-Claims

This hypothesis supports only an artifact-level AP6 basin-boundary stability
candidate if validated. It does not claim porous uptake, semantic selfhood,
identity acceptance, agency, native support, or fully native integration.
