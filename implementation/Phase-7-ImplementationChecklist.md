# Phase 7 Implementation Checklist

This document tracks execution of **Phase 7: `GRC9V3` Hybrid**.

It is intentionally separate from
[`Phase-7-ImplementationPlan.md`](./Phase-7-ImplementationPlan.md):

- the plan defines scope, ownership, workstreams, and acceptance criteria,
- this checklist records how the work is executed iteration by iteration.

Required companion documents:

- [`Phase-7-EquationMap.md`](./Phase-7-EquationMap.md)
- [`Phase-7-StepLoop.md`](./Phase-7-StepLoop.md)

Required mid-phase review artifact:

- `Phase-7-MidGate-Review.md`

## Usage Rules

- Treat `GRC9V3` as a hybrid, not as `GRC9` plus metadata.
- Every runtime field must declare ownership: GRC9 mechanical, GRCV3 semantic,
  or genuinely GRC9V3 hybrid.
- Do not reopen GRC9 mechanics unless the Phase 7 plan explicitly says why.
- Do not import GRCV3 semantics without adapting them to the nine-port chart.
- Keep mechanical expansion distinct from completed hybrid spark.
- Keep choice/collapse/learning runtime-backed; do not source-inject outcomes.
- Capability-gate boundary barrier, causal layer, anisotropic edges, and
  multiscale sigma claims.
- Update the plan and equation map before making a code change that changes
  semantics.

## Iteration Template

Copy this section for each new iteration.

```markdown
## Iteration N. <Short Name>

### Goal

<What this iteration is intended to complete>

### Checks

- [ ] <Concrete task 1>
- [ ] <Concrete task 2>
- [ ] <Concrete task 3>

### Implementation Notes

- <Important implementation detail, decision, or constraint>

### Verification

- [ ] <Import / test / review check>
- [ ] <Boundary / acceptance check>

### Summary

<Short outcome summary once iteration is complete>
```

## Iteration 0. Planning Bootstrap

### Goal

Create the Phase 7 planning documents and lock the hybrid ownership boundary
before code changes begin.

### Checks

- [x] Create `Phase-7-ImplementationPlan.md`
- [x] Create `Phase-7-ImplementationChecklist.md`
- [x] Create `Phase-7-EquationMap.md`
- [x] Create `Phase-7-StepLoop.md`
- [x] Record that the bootstrap-time `GRC9V3` code was still a
      non-executable stub
- [x] Record that Phase T/V-GRC9V3, phenomenology discovery, and GRCL/source
      seeds are downstream of core Phase 7

### Implementation Notes

- Phase 7 starts from a completed GRC9 substrate and a completed GRCV3 semantic
  family.
- This does not allow silent inheritance. Hybrid behavior must still be mapped
  explicitly.

### Verification

- [x] All kickoff docs exist under `implementation/`
- [x] The equation map includes ownership columns
- [x] The step loop reconciles Phase 5 and Phase 6 order explicitly

### Summary

Planning bootstrap is complete when the four kickoff docs exist. No runtime
code is changed in Iteration 0.

## Iteration 1. State, Params, And Capability Surface

### Goal

Replace the `GRC9V3` stub with a typed nontrivial family surface.

### Checks

- [x] Add `GRC9V3NodeState`
- [x] Add `GRC9V3State`
- [x] Parse hybrid params and modes
- [x] Validate `frame_mode`, `boundary_mode`, `expansion_distribution_mode`,
      `edge_label_selection`, and `curvature_backend`
- [x] Record parent-family provenance for default thresholds and rates
- [x] Advertise required capabilities from `grc-9-v3-spec.md`
- [x] Do not advertise optional capabilities unless implemented
- [x] Snapshot/save/load round trip carries hybrid fields

### Verification

- [x] State construction tests pass
- [x] Capability tests pass
- [x] Serialization tests pass
- [x] Stub-specific tests are replaced or updated

### Summary

Implemented the first executable Phase 7 surface boundary:

- `GRC9V3NodeState`
- `GRC9V3State`
- real `GRC9V3` model construction, validation, capability listing,
  snapshot/save/load, and reset support
- explicit `hessian_backend` parsing with `row_basis_diagonal` default and
  `weighted_least_squares` comparison mode
- default-threshold provenance: GRCV3 supplies metric, basin, spark,
  temporal-label, and choice/collapse defaults; GRC9 supplies mechanical
  refinement and growth defaults

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_state`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_family_stubs`

## Iteration 2. Row-Basis Differential Layer

### Goal

Implement the fixed-port-chart differential summary layer.

### Checks

- [x] Compute row-basis gradient summary
- [x] Compute signed Hessian row-basis summary with explicit
      `hessian_backend`
- [x] Implement `row_basis_diagonal` Hessian backend as the Phase 7 baseline
      form from Eq. G3
- [x] Allow `weighted_least_squares` Hessian backend for comparison against
      the GRCV3 Appendix A.3 geometry
- [x] Lock run-fixed Hessian sign convention
- [x] Compute net-flux summary in row basis
- [x] Materialize hybrid node tensors
- [x] Keep row and column semantics distinct

### Implementation Notes

- The default Hessian is the GRC9V3 row-basis diagonal form from Eq. G3. It is
  not the full weighted least-squares Hessian from GRCV3 Appendix A.3.
- The weighted least-squares Hessian should be available as a named backend so
  representative lanes can compare how the two geometries affect basin and
  spark behavior.

### Verification

- [x] Gradient row-basis tests pass
- [x] Signed Hessian tests pass for `row_basis_diagonal`
- [x] Signed Hessian tests pass for `weighted_least_squares`
- [x] Backend comparison test records different geometry when the two Hessian
      backends diverge
- [x] Hessian sign tie-break tests pass
- [x] Pre-flux and post-flux net-flux summaries differ when flux changes
- [x] Tensor construction tests pass

### Summary

Implemented the row-basis differential layer in
`src/pygrc/models/grc_9_v3_runtime.py` and exposed it through
`GRC9V3.rebuild_differential_state()`.

The default Hessian backend implements Eq. G3 as a signed row-basis diagonal.
The `weighted_least_squares` backend is available as a comparison geometry and
records the full comparison Hessian in `cached_quantities`.

Tensor construction follows GRC9 Eq. (1): diagonal row-local squared mismatch
for the `xi_c` term and isotropic total-flux feedback for the `zeta_c` term.
It intentionally does not use the GRCV3 outer-product tensor form.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_differential`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_family_stubs`

## Iteration 3. Transport, Edge Labels, And Identity

### Goal

Bring GRC9 transport together with GRCV3 identity seed semantics.

### Checks

- [x] Update scalar base conductance on occupied port-pairs
- [x] Compute selected analytic edge labels
- [x] Compute potential
- [x] Compute flux
- [x] Extract sinks and basins
- [x] Validate or seed basins from gradient/Hessian conditions
- [x] Implement the two-part basin seed condition from Eq. G7
- [x] Expose both flux-topology identity and geometric identity diagnostics
- [x] Recompute effective basin mass `M_i` from current basin membership

### Verification

- [x] Conductance tests pass
- [x] Edge-label tests pass
- [x] Potential/flux tests pass
- [x] Identity-layer tests pass
- [x] Eq. G7 basin-seed pass/fail tests cover both required clauses
- [x] Basin-mass tests prove `M_i` updates after basin membership changes

### Summary

Implemented the transport and identity layer in
`src/pygrc/models/grc_9_v3_runtime.py` and exposed it through
`GRC9V3.rebuild_transport_state()` and `GRC9V3.rebuild_identity_state()`.

The layer now computes scalar `base_conductance`, selected analytic edge
labels, potential, antisymmetric port-edge flux, flux-topology sinks/basins,
and Eq. G7 geometric seed diagnostics.

Correctness update, May 2026: downstream landscape-inference review found that
the original Iteration 3 implementation did not fully satisfy the GRC9V3
basin-attribute bundle from Appendix G. `basin_mass` is currently preserved
from prior node state or seed payloads instead of recomputed from current
basin membership. This leaves GRC9V3 full-geometric-basin and child-basin-mass
evidence incomplete until Iteration 9.1 is implemented.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_transport`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_state tests.models.test_family_stubs`

## Iteration 4. Hybrid Spark And Mechanical Expansion

### Goal

Implement hybrid spark candidates and mechanical expansion with child-basin
stabilization.

### Checks

- [x] Detect saturation-gated hybrid spark candidates
- [x] Require basin-interior and signed-Hessian degeneracy evidence
- [x] Capability-gate the optional signed criterion
      `H_s^(b)(k) * H_s^(b)(k-1) < 0`
- [x] Reuse or adapt GRC9 mechanical expansion
- [x] Evaluate post-expansion child-basin stabilization
- [x] Log candidate, expansion, and completed-spark evidence distinctly
- [x] Update hierarchy on successful stabilization

### Verification

- [x] Candidate-only case stays incomplete
- [x] Mechanical expansion without child-basin gain is not a completed spark
- [x] Stabilized child-basin case completes
- [x] Optional signed-criterion fixture is skipped or marked unavailable unless
      its capability is enabled
- [x] Hierarchy update is deterministic

### Summary

Implemented in `src/pygrc/models/grc_9_v3_sparks.py` and exposed through
`GRC9V3.detect_hybrid_spark_candidates()` and `GRC9V3.apply_hybrid_sparks()`.
Candidate, mechanical-expansion, and completed-spark evidence are emitted as
distinct events. Mechanical expansion adapts the GRC9 column-preserving module
pattern and records replay state in `GRC9V3State.expansion_registry`; completion
is withheld until post-expansion geometric child-basin evidence is present.
Signed-Hessian crossing history is carried by the differential rebuild cache,
and mechanical expansion records explicit unit-measure budget
before/after/error evidence. The default expansion core coherence is zero, but
`expansion_core_coherence_fraction` can assign a nonzero core share while
preserving the expansion budget.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_state tests.models.test_family_stubs
```

Result: 30 tests OK.

## Iteration 5. Choice, Collapse, Learning, Boundary, Budget

### Goal

Implement the remaining required hybrid runtime semantics.

### Checks

- [x] Implement sink compatibility scoring
- [x] Detect choice regimes
- [x] Detect collapse when one continuation dominates
- [x] Record learning as post-collapse state change
- [x] Apply configured boundary behavior
- [x] Enforce quadrature budget `sum_i mu_i C_i`
- [x] Implement uniform-shift budget correction
- [x] Implement positivity-preserving simplex projection budget correction
- [x] Refresh coarse cache and observables

### Verification

- [x] Choice event tests pass
- [x] Collapse event tests pass
- [x] Learning persistence tests pass
- [x] Boundary mode validation tests pass
- [x] Quadrature budget tests pass
- [x] Positivity-preserving simplex projection tests pass

### Summary

Implemented in `src/pygrc/models/grc_9_v3_choice.py` and exposed through
`GRC9V3.rebuild_choice_state()`, `GRC9V3.apply_boundary_behavior()`,
`GRC9V3.enforce_quadrature_budget()`, and
`GRC9V3.refresh_coarse_cache()`. Pure GRC9 supplies flux successors, sinks, and
basins; GRC9V3 adds the GRCV3-style choice/collapse/learning semantic layer on
top of those GRC9V3 port-flux diagnostics. Baseline boundary behavior remains
`prune_noop`; barrier/ghost remain capability-gated and are rejected during
parameter resolution until a concrete boundary-barrier runtime is implemented.
The quadrature budget target is fixed during state initialization from
`sum_i C_i^(0)` when no explicit target is supplied, so delayed enforcement does
not silently adopt a drifted value.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_state tests.models.test_family_stubs
```

Result: 36 tests OK.

## Iteration 6. Executable Step Loop

### Goal

Close the Phase 7 runtime loop by implementing `GRC9V3.step()` as the ordered
execution of the documented hybrid stages.

### Checks

- [x] Replace the `step()` placeholder with executable semantics
- [x] Run pre-flux differential refresh
- [x] Run transport, edge labels, potential, and flux
- [x] Run post-flux differential refresh
- [x] Run flux-topology identity and geometric basin validation
- [x] Run hybrid spark candidate, expansion, stabilization, and hierarchy
      registration
- [x] Run choice/collapse/learning update
- [x] Apply configured boundary behavior
- [x] Apply continuity update
- [x] Enforce fixed quadrature budget
- [x] Refresh final runtime state and invalidate coarse cache
- [x] Increment step/time deterministically
- [x] Record the step trace in cached diagnostics

### Verification

- [x] `step()` executes without `NotImplementedError`
- [x] Step trace matches `Phase-7-StepLoop.md`
- [x] Step index and time advance deterministically
- [x] Budget remains fixed after continuity
- [x] Choice/spark event rows are appended only when their predicates fire
- [x] Snapshot replay after a step is deterministic

### Summary

Implemented `GRC9V3.step()` as the executable Phase 7 loop. The step performs
pre-flux differential refresh, transport/labels/potential/flux, post-flux
differential refresh, identity validation, hybrid spark/expansion completion,
choice/collapse/learning, boundary behavior, continuity, fixed-budget
enforcement, final runtime refresh, coarse-cache invalidation, observables, and
deterministic step/time advancement. The executed order is recorded in
`cached_quantities["last_step_trace"]` and returned in `StepResult.bookkeeping`.
Follow-up alignment closed the paper-facing gaps: the trace now records the
pre-flux differential substeps separately, growth is an explicit inactive-port
stage, expansion triggers immediate quadrature budget enforcement, signed
Hessian history is pruned against the live topology, and topology-changing
helpers invalidate coarse caches directly.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_state tests.models.test_family_stubs
```

Result: 44 tests OK.

## Iteration 7. Mid-Gate Review

### Goal

Review whether the implementation is still a truthful hybrid before broader
artifact lanes are built.

### Checks

- [x] Create `Phase-7-MidGate-Review.md`
- [x] Confirm GRC9 mechanics remain separately inspectable
- [x] Confirm GRCV3 semantic fields remain separately inspectable
- [x] Confirm hybrid-only behavior is named explicitly
- [x] Confirm optional capabilities are not over-claimed
- [x] Record any deferred runtime surface

### Verification

- [x] Mid-gate review exists
- [x] Any follow-up checklist items are added before closeout

### Summary

Added [Phase-7-MidGate-Review.md](./Phase-7-MidGate-Review.md). The review
confirms that GRC9 mechanics, GRCV3 semantic fields, and hybrid-only behavior
remain separately inspectable. Optional capabilities remain unclaimed unless
runtime support exists, and deferred surfaces are recorded before representative
runtime evidence begins.

## Iteration 8. Representative Runtime Evidence

### Goal

Create artifact-backed evidence for core GRC9V3 runtime behavior.

### Checks

- [x] Add representative hybrid seed/state fixture
- [x] Add representative cell-division fixture from Appendix E:
      one spark producing two daughter sinks
- [x] Run deterministic representative lane
- [x] Capture steps, events, run summary, and snapshot/checkpoint artifacts
- [x] Verify hybrid spark or choice/collapse behavior if expected
- [x] Record replay command

### Verification

- [x] Representative lane is replayable
- [x] Event rows and run summary agree
- [x] Snapshot replay is deterministic

### Summary

Added the representative GRC9V3 runtime lane:

- [Phase-7-RepresentativeRuntime.md](./Phase-7-RepresentativeRuntime.md)
- [scripts/run_grc9v3_representative_runtime.py](../scripts/run_grc9v3_representative_runtime.py)
- [tests/models/test_grc_9_v3_representative_runtime.py](../tests/models/test_grc_9_v3_representative_runtime.py)

The lane writes artifacts under
`outputs/phase7-grc9v3-representative/grc9v3/appendix_e_cell_division/`.
The representative run produced one hybrid spark candidate, one mechanical
expansion, one completed hybrid spark, two stabilized daughter sinks, one
collapse event, matching event/run-summary counts, preserved budget, and a
matching replay digest.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_state tests.models.test_family_stubs
```

Result: 46 tests OK.

Replay command:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_grc9v3_representative_runtime.py --outputs-root outputs --experiment-id phase7-grc9v3-representative --steps 3
```

## Iteration 9. Core Closeout

### Goal

Close core Phase 7 and prepare for Phase T-GRC9V3.

### Checks

- [x] Create `Phase-7-Closeout.md`
- [x] Record implemented runtime semantics
- [x] Record deferred surfaces
- [x] Record representative evidence
- [x] State Phase T/V/phenomenology/GRCL-GRC9V3 as downstream

### Verification

- [x] Focused model tests pass
- [x] Serialization tests pass
- [x] Representative replay tests pass
- [x] Closeout preserves parent/hybrid ownership boundaries

### Summary

Added [Phase-7-Closeout.md](./Phase-7-Closeout.md). The closeout records the
implemented core runtime semantics, the representative Appendix E-style runtime
evidence, the focused verification command, and the deferred boundary to Phase
T-GRC9V3, Phase V-GRC9V3, GRC9V3 phenomenology discovery, reviewed motif
catalogs, and GRCL/source-seed lowering.

Post-core update: those downstream tracks are now complete through
Phase T-GRC9V3 telemetry, Phase V-GRC9V3 visualization, GRC9V3 phenomenology
discovery, reviewed motif cataloging, and GRCL-9V3 Revision 1. The final
source/lowering handoff is [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md), and
the reviewed lowered-source catalog is `outputs/grcl9v3/lowering/sessions/S0072/`.

Correctness qualification: a later landscape-inference pass identified a core
Phase 7 defect in GRC9V3 basin mass maintenance. The closeout remains useful
for the implemented step loop and runtime surfaces, but it is not final for
claims that depend on `M_i`, full geometric basins, or child-basin-mass
evidence until Iteration 9.1 below is closed.

## Iteration 9.1. Basin-Mass Correctness Repair

### Goal

Repair the GRC9V3 basin-attribute lift so Appendix G's effective basin mass
`M_i` is a current derived runtime quantity, not stale seed metadata.

### Checks

- [x] Add a basin-mass derivation helper in the GRC9V3 identity layer
- [x] Compute mass from current basin membership using `sum_i mu_i C_i`
- [x] Use unit-measure fallback for the current baseline `quadrature_mode`
- [x] Cache `basin_mass_by_basin_id` in `geometric_identity`
- [x] Cache a mass source/mode such as `unit_measure_basin_membership`
- [x] Update representative basin-chart nodes so `GRC9V3NodeState.basin_mass`
      reflects current effective basin mass
- [x] Preserve local coherence separately from basin mass
- [x] Do not reorder the canonical `GRC9V3.step()` loop
- [x] Export basin mass in GRC9V3 graph checkpoints
- [x] Mark previous GRC9V3 basin-mass fallback evidence as superseded or
      incomplete where appropriate

### Verification

- [x] Unit test: multi-node basin mass equals member coherence sum under
      unit measure
- [x] Unit test: basin mass changes when basin membership changes
- [x] Unit test: geometric basin cache includes `basin_mass_by_basin_id`
- [x] Unit test: representative checkpoint node records include `basin_mass`
- [x] Regression test: non-basin step-loop event ordering is unchanged
- [x] Rerun a GRC9V3 landscape-inference probe and verify it no longer needs
      `coherence_mass_fallback` when checkpoint basin mass is available

### Summary

Implemented in `src/pygrc/models/grc_9_v3_runtime.py` and the GRC9V3
checkpoint exporters.

`rebuild_grc9v3_identity_state()` now calls `compute_effective_basin_masses()`
after flux-topology identity extraction and Eq. G7 geometric seed validation.
The helper computes unit-measure effective basin mass from current basin
membership, caches `basin_mass_by_basin_id`, `basin_mass_by_node`, and
`basin_mass_source = "unit_measure_basin_membership"` in `geometric_identity`,
and updates representative basin-chart nodes while leaving local coherence as a
separate value field.

GRC9V3 graph checkpoints now include `basin_mass` in node overlays and node
records for both representative telemetry and GRCL-9V3 lowered-source replay.
The fresh landscape-inference probe `outputs/landscape_inference/sessions/S0006/`
records `basin_mass_sources = ["checkpoint_basin_mass"]` and
`evidence_modes = ["full_geometric_basin"]`, replacing the prior GRC9V3
coherence-mass fallback limitation for newly generated checkpoint evidence.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_step tests.telemetry.test_grc9v3_representative_telemetry tests.telemetry.test_grcl9v3_replay`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.telemetry.test_grc9v3_extensions tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_representative_telemetry tests.telemetry.test_grcl9v3_replay`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_landscape_inference_basin tests.landscapes.test_landscape_inference_substrate`

## Iteration 9.2. Column Coarse-Graining Operator Repair

### Goal

Repair the mismatch between the `GRC9V3` capability profile and the runtime
surface. `GRC9V3` declares `column_coarse_graining`, inherited from GRC9, but
previously only implemented coarse-cache invalidation. The actual Section 9
operator/Split surface is now added.

### Checks

- [x] Add `GRC9V3.coarse_grain_columns(field_name)`
- [x] Add `GRC9V3.split_columns(coarse_state)`
- [x] Reuse `src/pygrc/models/grc_9_coarse.py` pure helpers
- [x] Support exact nonnegative fields:
  - `conductance`
  - `geometric_length`
  - `temporal_delay`
  - `flux_coupling`
  - `abs_flux`
- [x] Support exact signed flux via `signed_flux_split`
- [x] Build GRC9V3 port-attached fields from live port-edge topology
- [x] Preserve GRC9 mode names:
  - `exact_column_profile`
  - `signed_flux_split`
- [x] Populate `state.coarse_cache` with operator-backed coarse states
- [x] Keep `refresh_coarse_cache()` and `_invalidate_coarse_cache()` as cache
      hygiene, not substitutes for the operator
- [x] Invalidate operator-backed coarse cache after:
  - transport value changes
  - flux recomputation
  - growth topology changes
  - spark/expansion rewiring
  - semantic maintenance refresh
- [x] Update GRC9V3 telemetry to distinguish:
  - empty cache
  - invalidated cache
  - warm operator-backed coarse fields
- [x] Add direct reconstruction tests parallel to `tests/models/test_grc_9_coarse.py`
- [x] Add capability-alignment test proving required `column_coarse_graining`
      has a public operator surface
- [x] Add a runnable usage example for GRC9 and GRC9V3 coarse-graining

### Verification

- [x] `Split(G(conductance)) = conductance` on the live GRC9V3 port field
- [x] `Split(G(signed_flux)) = signed_flux` with exact `J+ / J-` reconstruction
- [x] Nonnegative edge-label fields reconstruct exactly
- [x] Unsupported fields fail explicitly
- [x] Coarse cache is warmed by the operator and invalidated by value/topology
      mutation
- [x] Telemetry reports warm coarse fields when the operator has populated the
      cache
- [x] Existing Phase 7 step-loop tests remain deterministic

### Summary

Closed. `GRC9V3` now has a public Section 9-compatible column
coarse-graining/Split surface:

- `GRC9V3.coarse_grain_columns(field_name)`
- `GRC9V3.split_columns(coarse_state)`

The implementation reuses the pure GRC9 helpers, builds live GRC9V3
port-attached fields from occupied port edges, supports exact nonnegative
fields plus signed flux via `J+ / J-`, and stores operator-backed coarse states
in `state.coarse_cache`. Cache hygiene still invalidates stale operator states
after transport recomputation, topology mutation, expansion rewiring, and
semantic maintenance refresh. Post-expansion transport refreshes preserve the
more informative topology-change invalidation reason when the topology stage
already cleared the cache.

Phase T-GRC9V3 telemetry now distinguishes empty/invalidation-only cache state
from warm operator-backed fields through `coarse_fields_list` and
`coarse_field_types`.

A runnable example was added at
`scripts/demo_grc9_coarse_graining.py`. It demonstrates pure GRC9
`conductance` coarse-graining and GRC9V3 `signed_flux` coarse-graining, then
prints exact Split reconstruction checks for both.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_coarse`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_extensions`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_extensions tests.core.test_capabilities`
- `PYTHONPATH=src ./.venv/bin/python scripts/demo_grc9_coarse_graining.py`
