# Phase 5 Equation Map

This document maps the `GRCV3` paper/spec objects onto the planned code
structure.

Its purpose is to answer, before the implementation expands:

- where each major paper object will live,
- which backend category owns any constitutive variation,
- which runtime hook produces the object,
- how it is serialized,
- and how it is tested directly.

This is the paper-to-code anchor for Phase 5.

## Scope

This map covers the baseline `GRCV3` realization defined by:

- [`../papers/2026-02-GRC-V3.md`](../papers/2026-02-GRC-V3.md)
- [`../specs/grc-v3-spec.md`](../specs/grc-v3-spec.md)
- [`Common-BackendStrategyPlan.md`](./Common-BackendStrategyPlan.md)

It does not define every future backend. It defines the first implementation
surface that later backends must fit into.

## Phase 5 Backend Categories

These are the Phase 5 public backend categories and defaults:

| Category | Default | Other public names currently reserved |
| --- | --- | --- |
| `geometry` | `induced_local_frame` | `host_embedding`, `combinatorial` |
| `differential_summary` | `weighted_least_squares` | `combinatorial_surrogate` |
| `metric` | `tensor_exponential` | none reserved yet |
| `curvature` | `none` | `forman`, `ollivier` |
| `spark` | `signed_hessian_plus_attractor_delta` | `signed_hessian_degeneracy` |
| `hierarchy_update` | `basin_parent_child` | none reserved yet |
| `choice` | `disabled` | `sink_compatibility` |

Shared config surfaces kept outside the backend registry:

- `boundary_mode`
- `split_distribution_mode`
- `edge_label_selection`

## Planned Code Ownership

The default ownership plan is:

| Concern | Planned owner |
| --- | --- |
| Common backend-selection datatypes | `src/pygrc/core/backends.py` |
| `BasinAttributes` and `GRCV3State` | `src/pygrc/models/grc_v3_state.py` |
| Public `GRCV3` model class / step order | `src/pygrc/models/grc_v3.py` |
| Backend registries and dispatch tables | `src/pygrc/models/grc_v3_backends.py` |
| Gradient / Hessian / frame helpers | `src/pygrc/models/grc_v3_differential.py` |
| Hierarchy maintenance | `src/pygrc/models/grc_v3_hierarchy.py` |
| Choice / collapse helpers | `src/pygrc/models/grc_v3_choice.py` |
| Shared snapshot encoding / decoding | existing Phase 3 serializer path |

Exact filenames may still change, but this ownership boundary should remain.

## State Carrier Map

## Eq. (1) Basin-Attribute Bundle

Paper object:

$$
\mathcal B_i=
\big(C_i,\mathbf g_i,H_i,\mathbf J_i^{\mathrm{net}},M_i,\mathrm{id}_i,\mathrm{parent}_i,\mathrm{depth}_i\big)
$$

Planned code carrier:

```python
@dataclass
class BasinAttributes:
    coherence: float
    gradient: ArrayLike
    hessian: ArrayLike
    net_flux: ArrayLike
    basin_mass: float
    basin_id: str | int
    parent_id: str | int | None
    depth: int
```

Owner:

- `src/pygrc/models/grc_v3_state.py`

Serialized as:

- structured node state inside the `GRCV3` snapshot

Direct tests:

- `tests/models/test_grc_v3_state.py`

## Operator Map

| Paper object | Paper anchor | Planned hook | Backend category | Planned owner | Serialized evidence | Direct test target |
| --- | --- | --- | --- | --- | --- | --- |
| Local frame / edge directions `e_ij` | discussion around Eqs. (2) and (3) | `_compute_geometry()` / `_compute_differential_summary()` | `geometry` | `grc_v3_differential.py` | backend selection + any required geometry metadata | `test_grc_v3_differential.py` |
| Gradient summary `g_i` | Eq. (2) | `_compute_differential_summary()` | `differential_summary` | `grc_v3_differential.py` | node `gradient` + backend selection | `test_grc_v3_differential.py` |
| Hessian summary `H_i` | Eq. (3), realized by spec Appendix A.3 in the reference backend | `_compute_differential_summary()` | `differential_summary` | `grc_v3_differential.py` | node `hessian` + `hessian_sign` + differential backend metadata | `test_grc_v3_differential.py` |
| Net flux summary `J_i^net` | Eq. (4) | `_compute_differential_summary()` after flux stage | family-fixed baseline | `grc_v3.py` or `grc_v3_differential.py` | node `net_flux` | `test_grc_v3_step.py` |
| Basin mass `M_i` | Eq. (5) | `_detect_identities()` / hierarchy update | `hierarchy_update` | `grc_v3_hierarchy.py` | node `basin_mass` + hierarchy snapshot | `test_grc_v3_hierarchy.py` |
| Node tensor `K_i` | Eq. (6) | `_compute_metric()` | family-fixed baseline under `metric` surface | `grc_v3.py` or `grc_v3_backends.py` | optional snapshot metadata / recomputable from node state | `test_grc_v3_step.py` |
| Base conductance `w_ij` | Eq. (7) | `_compute_metric()` | `metric` + `curvature` | `grc_v3_backends.py` | `base_conductance` | `test_grc_v3_step.py` |
| Geometric length `ell^(d)` | Eq. (8) | `_compute_metric()` | `metric` + `geometry` | `grc_v3_backends.py` | `geometric_length` + label computation mode metadata | `test_grc_v3_step.py` |
| Temporal delay `tau_ij` | Eq. (9) | `_compute_metric()` | `metric` | `grc_v3_backends.py` | `temporal_delay` + label computation mode metadata | `test_grc_v3_step.py` |
| Flux coupling `F_ij` | Eq. (10) | `_compute_metric()` or post-flux label refresh | family-fixed baseline under `metric` surface | `grc_v3.py` | `flux_coupling` | `test_grc_v3_step.py` |
| Functional `P[C]` | Eq. (11) | `_compute_potential()` | family-fixed baseline | `grc_v3.py` | not required as stored state | `test_grc_v3_step.py` |
| Potential `Phi_i` | Eq. (12) | `_compute_potential()` | family-fixed baseline | `grc_v3.py` | `potential` | `test_grc_v3_step.py` |
| Flux `J_ij` | Eq. (13) | `_compute_flux()` | family-fixed baseline | `grc_v3.py` | `flux` + edge overlays | `test_grc_v3_step.py` |
| Continuity update | Eq. (14) | `_apply_continuity()` | family-fixed baseline | `grc_v3.py` | node coherence after step | `test_grc_v3_step.py` |
| Spark predicate | Eq. (15), Appendix B.3 | `_detect_events()` | `spark` | `grc_v3_backends.py` | event log + backend selection | `test_grc_v3_step.py` |
| Signed Hessian convention `s_H` | Appendix B.1 | first differential-summary build, then reused | family-fixed baseline | `grc_v3_differential.py` | `metadata.hessian_sign` | `test_grc_v3_differential.py` |
| Basin criterion | Appendix B.2 | `_detect_identities()` | `spark` + differential summary semantics | `grc_v3.py` | sink/basin state, optional diagnostics | `test_grc_v3_step.py` |
| Spark completion by attractor-count gain | Appendix B.4 | `_detect_events()` + `_apply_topology_changes()` + post-check | `spark` | `grc_v3_backends.py` | event log + post-event basin structure | `test_grc_v3_step.py` |
| Choice compatibility score `pi(i -> s)` | Appendix A.1 | `_update_choice_state()` | `choice` | `grc_v3_choice.py` | `choice_registry` + events | `test_grc_v3_choice.py` |
| Choice regime detection | Appendix A.2 | `_update_choice_state()` | `choice` | `grc_v3_choice.py` | `choice_detected` events | `test_grc_v3_choice.py` |
| Collapse detection | Appendix A.3 | `_update_choice_state()` | `choice` | `grc_v3_choice.py` | `collapse_registry` + `collapse` events | `test_grc_v3_choice.py` |
| Learning as persistent deformation | Appendix A.4 | post-collapse update path | `choice` | `grc_v3_choice.py` plus main step loop | choice/collapse state and later-step geometry | `test_grc_v3_choice.py` |

## Choice Backend Semantics Note

For the first implemented `choice = sink_compatibility` backend, the baseline
contract is:

- compatibility is computed from normalized positive outgoing flux aggregated by
  reachable sink
- `choice_detected` is emitted when at least two sink continuations remain
  viable within `epsilon_choice`
- `collapse` is emitted only when a previously ambiguous node resolves to one
  dominant sink with winner margin at least `epsilon_collapse`
- `choice_resolved` is emitted when a previously ambiguous node falls to a
  single viable sink but the winner margin remains below `epsilon_collapse`

The sharp-edge parameter semantics are intentional and should be treated as part
of the constitutive contract unless a later backend supersedes them:

- `epsilon_choice = 0` means only exactly tied best scores remain jointly viable
  as a choice regime; near-ties do not count
- `epsilon_collapse = 0` means any positive winner margin is sufficient to
  trigger collapse from a previously ambiguous state

These are mathematically valid but intentionally strict. If later comparison
work shows they are too discontinuous for experiments, add another explicit
choice backend rather than silently weakening this baseline.

For the signed-Hessian convention, the baseline rule is:

- calibrate `s_H` once from the first valid basin-attribute build or restored
  snapshot state
- reuse the stored sign for later rebuilds
- when the calibration scores for `+1` and `-1` tie exactly, choose `+1`

## Hook Order Map

The exact Phase 5 baseline runtime order is recorded in
[Phase-5-StepLoop.md](./Phase-5-StepLoop.md).

At a high level, the loop preserves the `GRCV2` reflexive structure while
making two `GRCV3`-specific commitments explicit:

1. differential state is rebuilt once before flux and once after flux because
   `net_flux` is a post-flux quantity in the baseline semantics
2. the stored state is refreshed again after continuity and budget correction
   so post-step diagnostics are genuinely post-step rather than mixed-time
   leftovers

That exactness matters more than keeping the runtime lane visually rich. A
simple seed may be used for evidence, but it still runs the full reference
loop.

## Hessian Realization Note

The Phase 5 baseline deliberately distinguishes between:

- the paper-level Eq. (3), which presents `H_i` as a direct weighted moment of
  coherence differences in the local edge basis, and
- the reference implementation backend, which follows
  [specs/grc-v3-spec.md](../specs/grc-v3-spec.md)
  Appendix A.3 and materializes `H_i` through a weighted least-squares fit of
  the quadratic residual after subtracting the first-order gradient term.

This is a constitutive numerical choice, not a claim that the current code is a
literal line-by-line transcription of Eq. (3). The rationale is:

- the raw moment mixes linear-trend and curvature contributions,
- the Appendix A.3 backend isolates curvature more cleanly,
- regularized least squares is materially more stable on sparse or weakly
  conditioned local neighborhoods.

For Phase 5, the audit position is therefore:

- Eq. (3) remains the conceptual paper anchor for the Hessian summary,
- Appendix A.3 is the canonical reference backend used to realize it in code.

If strict paper-literal comparison becomes important later, add a second
`differential_summary` backend implementing the raw weighted-moment form so the
two realizations can be compared explicitly under the same runtime.

## Serialization Map

The following pieces must be serialized explicitly rather than left implicit:

- backend selections by category
- backend params for each selected backend
- `frame_mode`
- `boundary_mode`
- `split_distribution_mode`
- `edge_label_selection`
- `hessian_sign`
- node basin attributes
- hierarchy structure
- choice / collapse registries if present

The following may remain recomputable if clearly documented:

- node tensor `K_i`
- the functional `P[C]`

The exact snapshot builder may choose to store them as diagnostics, but the
baseline contract should not require them if they can be regenerated
deterministically from stored state and params.

## Test Class Map

The minimum direct test surface should include:

| Test file | Primary evidence |
| --- | --- |
| `tests/models/test_grc_v3_state.py` | state dataclasses, invariants, param resolution |
| `tests/models/test_grc_v3_backends.py` | backend selection validation and serialization |
| `tests/models/test_grc_v3_differential.py` | frame, gradient, Hessian, `s_H` |
| `tests/models/test_grc_v3_hierarchy.py` | basin mass, parent/depth, hierarchy updates |
| `tests/models/test_grc_v3_choice.py` | choice / collapse / learning semantics |
| `tests/models/test_grc_v3_step.py` | ordered step-loop behavior and event integration |
| `tests/models/test_grc_v3_serialization.py` | snapshot roundtrip and replay identity |

## Explicit Open Questions To Resolve During Implementation

These are acceptable implementation-time decisions, but they must not remain
implicit:

1. whether `weighted_least_squares` needs one baseline dimensionality rule for
   the local frame or multiple explicit variants
2. whether net-flux summary is stored strictly as a post-flux quantity or as a
   lagged previous-step quantity during the update
3. whether the first baseline stores hierarchy as:
   - basin-id keyed tree structure,
   - or sink-node keyed structure with basin-id projections
4. whether the first real `choice = sink_compatibility` backend scores from:
   - potential-only cost,
   - temporal-delay cost,
   - or a serialized weighted combination

If any of these choices materially changes semantics, the chosen rule should be
recorded in the checklist iteration that introduces it.

## Resolved Baseline Answers After Iteration 10

The Phase 5 constitutive review resolved the current baseline as follows:

1. `weighted_least_squares` uses one explicit baseline dimensionality rule:
   the local frame dimension is taken from `geometry.params.dimension`, with a
   default of `2`
2. `net_flux` is a post-flux quantity rebuilt from the current flux field, not
   a lagged previous-step cache
3. hierarchy is stored as a basin-id keyed parent/child tree
4. the first implemented `choice = sink_compatibility` backend scores from
   normalized positive outgoing flux aggregated by reachable sink

The remaining open work is not hidden choice of meaning, but additional
backends that may be added later for comparison.
