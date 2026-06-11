# Phase 5 Constitutive Review

## Purpose

Iteration 10 is the mid-phase validation gate for `GRCV3`. Its job is to make
the current constitutive baseline explicit before runtime integration work
continues in Iteration 11.

This note records what the current code means relative to the paper and spec,
which parts are aligned, which parts are deliberate numerical realizations, and
which paper-facing capabilities remain intentionally deferred.

## Reviewed Anchors

The review was carried out against:

- [papers/2026-02-GRC-V3.md](../papers/2026-02-GRC-V3.md)
- [specs/grc-v3-spec.md](../specs/grc-v3-spec.md)
- [implementation/Phase-5-EquationMap.md](./Phase-5-EquationMap.md)
- [src/pygrc/models/grc_v3.py](../src/pygrc/models/grc_v3.py)
- [src/pygrc/models/grc_v3_differential.py](../src/pygrc/models/grc_v3_differential.py)
- `tests/models/test_grc_v3_*.py`

## Review Outcome

The current `GRCV3` baseline is semantically coherent enough to proceed into
runtime integration work. The main remaining issues are not hidden paper/spec
misreads, but explicit constitutive scope limits that must stay documented:

- the Hessian realization is the spec Appendix A.3 weighted least-squares
  backend, not the literal raw moment form of paper Eq. (3)
- the first choice backend is a flux-routed sink-compatibility score, not the
  full Appendix A family of possible compatibility constructions
- collapse persistence is currently `registry_only`, not yet a geometric
  deformation feedback path
- the budget-closure rule is deterministic but still heuristic rather than a
  uniquely theory-derived redistribution law

## 1. Gradient And Hessian Semantics

### Outcome

Aligned with the Phase 5 constitutive baseline.

### Findings

- The implemented differential backend is
  `differential_summary = weighted_least_squares`.
- This matches the canonical reference backend defined in
  [specs/grc-v3-spec.md](../specs/grc-v3-spec.md), Appendix A.2-A.3.
- The code computes:
  - weighted least-squares gradient
  - weighted least-squares Hessian on the quadratic residual after subtracting
    the gradient term
  - post-flux `net_flux` summaries during basin-attribute rebuild

### Constitutive Position

This is a deliberate realization choice:

- paper Eq. (3) remains the conceptual anchor for the Hessian summary
- spec Appendix A.3 is the canonical implementation backend actually used by
  the code

This means the baseline does not claim literal Eq. (3) transcription. It
claims paper-faithful semantics realized through the spec's reference numerical
backend.

### Resolved Baseline Rule

- local differential dimension comes from the selected geometry backend params,
  with `geometry.params.dimension` defaulting to `2`
- `net_flux` is treated as a post-flux quantity, not a lagged previous-step
  cache

## 2. Signed Hessian Convention `s_H`

### Outcome

Aligned with the signed-Hessian appendix.

### Findings

- `hessian_sign` is calibrated from candidate seed nodes using gradient norm,
  signed-Hessian positivity, and seed membership agreement
- calibration uses a deterministic tuple score
  `(positive_count, total_margin, satisfied_ids)`
- the chosen sign is stored in
  `state.cached_quantities["hessian_sign"]`
- the sign is serialized and restored as explicit snapshot metadata
- once a valid sign has been established, later basin-attribute rebuilds reuse
  it rather than recalibrating silently

### Constitutive Position

The baseline follows the intended contract:

- choose one global sign convention
- serialize it once
- keep it fixed for the run
- if both sign candidates score identically, `+1` wins the tie

No hidden recalibration behavior remains in the runtime baseline.

### Runtime Implication

The `+1` tie-break is now an initialization or restore-time constitutive rule,
not a per-step runtime drift mechanism. It matters when the sign is first
chosen, but the Phase 5 step loop reuses the stored sign on later differential
rebuilds.

## 3. Spark Completion Logic

### Outcome

Aligned with the attractor-gain requirement.

### Findings

- the active spark backend is
  `spark = signed_hessian_plus_attractor_delta`
- local signed-Hessian degeneracy is only the candidate trigger
- confirmed spark completion requires a post-split attractor gain:
  - `validated_basin_count` increase by at least `min_child_basins`, or
  - `sink_count` increase by at least `1`
- soft-split refresh now recomputes:
  - potential
  - flux
  - basin attributes
  - identity state
  before evaluating completion

### Constitutive Position

This matches the intended paper-facing rule that local degeneracy alone is not
enough. Topology change must produce an actual increase in attractor structure.

## 4. Hierarchy Semantics

### Outcome

Aligned with the basin-attribute contract.

### Findings

- the active hierarchy backend is
  `hierarchy_update = basin_parent_child`
- hierarchy is maintained as a basin-id keyed tree, not a sink-node keyed tree
- split-created children receive:
  - `basin_id = child_node_id`
  - `parent_id = parent_attributes.basin_id`
  - `depth = parent.depth + 1`
- `basin_mass` is recomputed from current basin membership rather than left as
  stale inherited payload
- explicit parent ids without live node carriers remain represented as roots in
  the serialized hierarchy map

### Constitutive Position

The Phase 5 baseline has now resolved the earlier ambiguity:

- hierarchy is a basin hierarchy
- the stored tree is keyed by basin ids
- sink/node ids can still participate in diagnostics, but they are not the
  primary hierarchy keys

## 5. Backend Naming Audit

### Outcome

Current backend names are acceptable and do not materially overclaim, provided
their constitutive scope remains documented.

### Findings

- `weighted_least_squares` is accurate
- `tensor_exponential` is accurate for the implemented conductance law
- `signed_hessian_plus_attractor_delta` is accurate and preferable to a looser
  name because it exposes the two-part confirmation rule
- `basin_parent_child` is accurate
- `sink_compatibility` is acceptable because the current score is compatibility
  with reachable sink continuations, but it must be read as the flux-routed
  baseline backend, not as the entire Appendix A design space
- the current choice lifecycle has three distinct public events:
  - `choice_detected`
  - `choice_resolved`
  - `collapse`

## 6. Explicit Remaining Constitutive Gaps

These are real scope limits, but they are no longer hidden or ambiguous:

1. No paper-literal raw-moment Hessian backend exists yet.
   The baseline uses the Appendix A.3 weighted least-squares realization only.

2. No alternative choice-score backends exist yet.
   Potential-based, temporal-delay-based, or weighted hybrid compatibility
   backends remain future work.

3. Learning is not yet a persistent geometric deformation path.
   The baseline records collapse outcomes in `collapse_registry` with
   `persistence_mode = "registry_only"`.

4. Budget correction uses a deterministic node-order heuristic.
   Positive correction is assigned to the first live node, while deficit
   removal proceeds in sorted node-id order. This is explicit and replayable,
   but it is still a heuristic constitutive choice rather than a theory-derived
   unique rule.

## 7. Iteration 10 Decision

Iteration 10 is satisfied.

What is now fixed for the Phase 5 baseline:

- differential summaries use the spec reference weighted least-squares backend
- `s_H` is calibrated once and serialized
- spark completion is attractor-count-gated
- hierarchy is basin-id keyed parent/child structure
- `sink_compatibility` is the first explicit flux-routed choice backend

What remained for the next iteration at the time of this review:

- build the first representative runtime lane
- implement `step()`
- produce runtime evidence rather than only unit-level semantic evidence

That follow-on runtime closure was completed in Iteration 11.
