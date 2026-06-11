# Phase 6 Implementation Checklist

This document tracks the execution of **Phase 6: `GRC9` Mechanical
Substrate**.

It is intentionally separate from
[`Phase-6-ImplementationPlan.md`](./Phase-6-ImplementationPlan.md):

- the plan defines scope, workstreams, constraints, and acceptance criteria,
- this checklist records how the Phase 6 work will be executed iteration by
  iteration.

Required companion documents:

- [`Phase-6-EquationMap.md`](./Phase-6-EquationMap.md)
- [`Phase-6-StepLoop.md`](./Phase-6-StepLoop.md)

Required mid-phase review artifact:

- `Phase-6-MidGate-Review.md`

## Usage Rules

- Keep `GRC9` mechanically explicit; do not silently drift into `GRC9V3`.
- Keep rows and columns distinct in both runtime code and notes.
- Lock deterministic tie-breaks before topology logic becomes large.
- Record constitutive compromises near the iteration that introduces them.
- If implementation pressure changes the plan, update
  [`Phase-6-ImplementationPlan.md`](./Phase-6-ImplementationPlan.md) first or
  in the same change.
- Before substantive runtime implementation begins, complete the kickoff doc
  set:
  - `Phase-6-ImplementationChecklist.md`
  - `Phase-6-EquationMap.md`
  - `Phase-6-StepLoop.md`

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

## Iteration 0. Checklist Bootstrap

### Goal

Create the Phase 6 execution checklist and align it with the revised Phase 6
plan.

### Checks

- [x] Create `Phase-6-ImplementationChecklist.md`
- [x] Align the checklist structure with `Phase-6-ImplementationPlan.md`
- [x] Record the required kickoff companion docs:
  - `Phase-6-EquationMap.md`
  - `Phase-6-StepLoop.md`
- [x] Record the required mid-phase review artifact:
  - `Phase-6-MidGate-Review.md`
- [x] Link the Phase 6 checklist from `ImplementationPhases.md`

### Implementation Notes

- The Phase 6 plan remains the normative planning document; this file is the
  execution tracker.
- Unlike some earlier phases, the equation map and step-loop docs are not
  optional for Phase 6. They are part of the kickoff rule.
- The checklist should track the pure `GRC9` baseline only.

### Verification

- [x] The checklist file exists under `implementation/`
- [x] `ImplementationPhases.md` points to the checklist
- [x] The iteration structure maps cleanly onto the Phase 6 workstreams

### Summary

Phase 6 now has a paired plan and execution checklist, with the required
kickoff documents and mid-phase review artifact called out explicitly.

## Iteration 1. Kickoff Companion Docs

### Goal

Create the Phase 6 paper-to-code traceability docs required before substantive
runtime implementation begins.

### Checks

- [x] Create `Phase-6-EquationMap.md`
- [x] Create `Phase-6-StepLoop.md`
- [x] Align the equation map with:
  - `specs/grc-9-spec.md`
  - `papers/2026-04-GRC-9.md`
- [x] Lock the spec-facing step order in the step-loop document
- [x] Record the current deterministic decisions already fixed by the plan:
  - sequential multi-sink spark handling
  - ascending-neighbor successor tie-break
  - canonical `PortEdge` storage direction

### Implementation Notes

- Do not start runtime code that depends on ambiguous equation ownership before
  these docs exist.
- The equation map should keep `GRC9` and `GRC9V3` semantics separate from the
  first line.

### Verification

- [x] The equation map covers the row tensor, spark trigger, expansion, growth,
  and coarse-graining equations
- [x] The step-loop doc matches the spec-locked order from the plan

### Summary

Phase 6 kickoff traceability docs are complete and the constitutive execution
order is fixed before runtime code expands.

## Iteration 2. `GRC9` Surface And Port Helpers

### Goal

Replace the stub family surface with the real `GRC9` model shell and define the
typed state/port helper boundary.

### Checks

- [x] Replace the `BaseFamilyStub`-based `GRC9` surface in `src/pygrc/models/grc_9.py`
- [x] Add `src/pygrc/models/grc_9_ports.py`
- [x] Implement pure helpers for:
  - `port_to_rc(...)`
  - `rc_to_port(...)`
  - row membership over occupied ports
  - column membership over occupied ports
- [x] Add `PortEdge`
- [x] Add `GRC9State`
- [x] Ensure `GRC9State` carries `rng_state` explicitly and that the family
  surface treats it as deterministic replay state rather than incidental data
- [x] Define the typed schema for:
  - `expansion_registry`
  - previous-step column diagnostics
  - any adiabatic expansion schedule state
- [x] Resolve the baseline parameter surface:
  - `frame_mode`
  - `curvature_backend`
  - `boundary_mode`
  - `expansion_distribution_mode`
  - `edge_label_selection`

### Implementation Notes

- `GRC9State` should be a real dataclass, not a dict-shaped compatibility
  wrapper.
- The helper module should stay pure and easily testable.
- Keep `GRC9` capabilities truthful and free of `GRC9V3` features.
- Implemented the dedicated nine-slot helper surface in:
  - `src/pygrc/models/grc_9_ports.py`
- Implemented the typed family state carriers in:
  - `src/pygrc/models/grc_9_state.py`
- Replaced the old stub-only `GRC9` family shell in:
  - `src/pygrc/models/grc_9.py`
- Exported the new Phase 6 public surface through:
  - `src/pygrc/models/__init__.py`
- Added focused Iteration 2 state/constructor coverage in:
  - `tests/models/test_grc_9_state.py`
- Updated the shared family-surface contract checks in:
  - `tests/models/test_family_stubs.py`
- Chosen Iteration 2 construction/default policy:
  - `GRC9.from_config({"dt": ...})` is allowed and resolves the family
    baseline defaults automatically
  - `frame_mode = fixed_port_chart`
  - `curvature_backend = none`
  - `boundary_mode = prune`
  - `expansion_distribution_mode = equal`
  - `edge_label_selection = all`
- Chosen deterministic replay/state policy:
  - `rng_state` is explicit `GRC9State` runtime state, not incidental metadata
  - the family surface restores it from snapshots and seeds it deterministically
    when omitted
  - `params_identity` is recorded directly on state for replay compatibility
- Chosen typed-registry/state-vocabulary policy:
  - occupied port-pair runtime state uses `PortEdge`
  - `expansion_registry` entries use `ExpansionRecord`
  - optional gradualization state uses `AdiabaticExpansionSchedule`
  - previous-step sign-crossing support is reserved through
    `prev_column_diagnostic`
- Chosen Iteration 2 execution boundary:
  - `GRC9` is now a real `GRCModel` surface with typed load/save/snapshot/reset
  - `step()` intentionally remains deferred until later iterations

### Verification

- [x] `GRC9.from_config(...)` constructs a non-stub family surface
- [x] Port helper tests cover forward and inverse conversion plus invalid input
- [x] State installation/replacement rejects incompatible objects

Focused verification run:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_state tests.models.test_family_stubs`
- result:
  - `Ran 15 tests`
  - `OK`

### Summary

Completed the real `GRC9` family shell. Phase 6 now has explicit nine-slot port
helpers, typed state carriers, deterministic replay state, and shared snapshot
integration, while full stepping remains intentionally deferred to the later
runtime iterations.

## Iteration 3. Row Tensor And Metric Surface

### Goal

Implement the row-based tensor and occupied-port-pair conductance update.

### Checks

- [x] Implement row-organized neighborhood aggregation
- [x] Implement the row-based tensor from:
  - density term
  - row-wise mismatch term
  - flux feedback term
- [x] Choose and document the compact row-diagonal tensor representation
- [x] Implement the `tensor_exponential` metric update on occupied port-pairs
- [x] Integrate `curvature_backend` selection into the conductance formula:
  - `none`
  - `forman`
  - `ollivier`
- [x] Implement the selected analytic edge-label families:
  - `geometric_length`
  - `temporal_delay`
  - `flux_coupling`
- [x] Serialize edge-label computation mode metadata

### Implementation Notes

- Do not materialize the tensor as an unnecessary dense 3x3 matrix if the
  runtime object remains diagonal in the row basis.
- Preserve the distinction between the dynamical conductance and analytic edge
  labels.
- Implemented the executable geometry/metric/label surface in:
  - `src/pygrc/models/grc_9.py`
- Added focused Iteration 3 tensor/metric coverage in:
  - `tests/models/test_grc_9_tensor.py`
- Chosen compact tensor representation:
  - the row tensor is stored as a deterministic row-diagonal list of three
    floats per node under `cached_quantities["row_tensor_diagonal"]`
  - no dense `3 x 3` matrix object is materialized in the runtime state
- Chosen inspectability/cache surface:
  - row-organized neighborhoods are exposed through
    `cached_quantities["row_neighborhoods"]`
  - row mismatch terms are exposed through
    `cached_quantities["row_mismatch_terms"]`
  - scalar tensor contributions are exposed through
    `cached_quantities["tensor_terms"]`
- Chosen metric/backend policy:
  - conductance updates remain attached to occupied `PortEdge` pairs
  - `curvature_backend` is wired into the conductance formula with explicit
    branches for `none`, `forman`, and `ollivier`
  - topology hydration keeps `port_edges` aligned with live topology when the
    caller omits explicit edge runtime state
- Chosen analytic-label policy:
  - `geometric_length`, `temporal_delay`, and `flux_coupling` remain separate
    state fields rather than collapsing into one generic edge-label mapping
  - `edge_label_computation_mode` and `edge_label_params` are serialized
    explicitly so label provenance stays inspectable in snapshots
- Chosen Iteration 3 execution boundary:
  - the geometry-to-metric surface is executable and testable
  - the end-to-end `step()` loop still remains deferred

### Verification

- [x] Tensor tests cover row-wise mismatch accumulation and deterministic output
- [x] The conductance update uses only the intended occupied port-pair inputs
- [x] Edge labels are explicit and separately serialized

Focused verification run:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_state tests.models.test_grc_9_tensor tests.models.test_family_stubs`
- result:
  - `Ran 19 tests`
  - `OK`

### Summary

Completed the row-tensor and metric slice. `GRC9` now exposes deterministic
row-basis tensor diagnostics, curvature-aware conductance updates on occupied
port-pairs, and explicit analytic edge labels with serialized provenance.

## Iteration 4. Potential, Flux, Successor Map, And Basins

### Goal

Close the pre-topology reflexive loop and make sink/basin extraction
deterministic.

### Checks

- [x] Implement potential computation
- [x] Implement flux computation
- [x] Fix the canonical `PortEdge` storage direction
- [x] Implement oriented flux views with antisymmetry checks
- [x] Implement successor-map extraction
- [x] Lock successor-map tie-breaking to ascending neighbor node ID
- [x] Implement sink-set extraction
- [x] Implement basin extraction

### Implementation Notes

- The state should expose conductance and flux on occupied port-pairs without
  collapsing back to a weighted-edge-only mental model.
- Keep sink/basin extraction free of `GRCV3` semantic lift.
- Extended the executable runtime surface in:
  - `src/pygrc/models/grc_9.py`
- Added focused Iteration 4 runtime coverage in:
  - `tests/models/test_grc_9_runtime.py`
- Chosen Iteration 4 numerical defaults:
  - `kappa_c = 1.0`
  - `eta = 1.0`
  - `site_potential_selection = quadratic`
  - `site_potential_params = {"mu": 0.0, "scale": 1.0}`
- Chosen oriented-flux/runtime policy:
  - `PortEdge.flux_uv` remains the canonical stored scalar on the ordered
    occupied port-pair
  - oriented node-local views are reconstructed through `_oriented_flux(...)`
  - `_assert_flux_antisymmetry()` records inspectable oriented views under
    `cached_quantities["oriented_flux"]`
- Chosen identity-extraction policy:
  - successor extraction uses positive outgoing flux only
  - ties break by ascending neighbor node ID, then edge ID
  - zero-outflow nodes map to themselves in the successor map
  - sinks require no positive outflow and at least one positive inflow
- Chosen Iteration 4 inspectability surface:
  - successor structure is exposed through `cached_quantities["successor_map"]`
  - sink/basin structure is mirrored under `cached_quantities["flux_identity"]`
- Chosen Iteration 4 execution boundary:
  - the baseline reflexive loop is closed through potential, flux, successor,
    sink, and basin extraction
  - topology events and spark semantics remain deferred to later iterations

### Verification

- [x] Runtime checks enforce the antisymmetry contract for oriented flux views
- [x] Successor-map tests cover ties and zero-outflow cases
- [x] Sink/basin extraction is deterministic on fixed inputs

Focused verification run:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_state tests.models.test_grc_9_tensor tests.models.test_grc_9_runtime tests.models.test_family_stubs`
- result:
  - `Ran 23 tests`
  - `OK`

### Summary

Completed the pre-topology reflexive loop. `GRC9` now computes potential and
occupied-port-pair flux, enforces oriented antisymmetry, and extracts
deterministic successor, sink, and basin structure without any hybrid
`GRC9V3` semantics.

## Iteration 5. Mechanical Spark Trigger

### Goal

Implement the baseline `GRC9` spark rule and lock its deterministic taxonomy.

### Checks

- [x] Implement the saturation gate `deg_act(s) == 9`
- [x] Record explicitly that the optional near-saturation relaxation
  `deg_act >= 8` is deferred unless Phase 6 later re-scopes it
- [x] Implement column diagnostic `H^(b)`
- [x] Implement the baseline instability proxy and parameterize `tau_instability`
- [x] Record the exact instability-proxy formula in implementation-facing notes
  or code comments close to the spark trigger
- [x] Define `SparkKind`:
  - `saturation_instability`
  - `saturation_column_proxy`
  - `saturation_sign_crossing`
- [x] Implement deterministic trigger ordering across sinks
- [x] Implement previous-step column-diagnostic storage if sign-crossing support
  is enabled
- [x] Keep the baseline trigger free of Hessian-based `GRC9V3` logic

### Implementation Notes

- `GRC9` spark detection is intentionally mechanical; do not tighten it into
  hybrid semantics here.
- If sign-crossing support is deferred, leave the storage and tests for that
  branch unchecked and record the deferral explicitly.
- Extended the runtime spark surface in:
  - `src/pygrc/models/grc_9.py`
- Exported the public spark taxonomy through:
  - `src/pygrc/models/__init__.py`
- Added focused Iteration 5 spark coverage in:
  - `tests/models/test_grc_9_sparks.py`
- Chosen baseline spark taxonomy:
  - `SparkKind.SATURATION_INSTABILITY`
  - `SparkKind.SATURATION_COLUMN_PROXY`
  - `SparkKind.SATURATION_SIGN_CROSSING`
- Chosen baseline trigger policy:
  - only saturated sinks with `deg_act(s) == 9` are eligible in the Phase 6
    baseline
  - the optional near-saturation relaxation `deg_act >= 8` is explicitly
    deferred and recorded in cached diagnostics
  - trigger ordering across sinks is deterministic by ascending sink node ID
  - spark classification precedence is intentional:
    `instability > column_proxy > sign_crossing`
- Chosen baseline instability proxy:
  - `U(s) = {s} ∪ N(s)`
  - `cut_out(U)` sums conductances on occupied port-pairs with exactly one
    endpoint in `U`
  - `support_in(U)` sums conductances on occupied port-pairs with both
    endpoints in `U`
  - `Instability(s) = cut_out(U) / max(cut_out(U) + support_in(U), eps)`
- Chosen column-diagnostic/sign-crossing policy:
  - `H^(b)` is computed by fixed-port-chart column grouping via `rc_to_port(...)`
  - `prev_column_diagnostic` is the explicit previous-step persistence surface
  - Phase 6 documentation policy is to refresh it on each spark-detection pass
    for replay/debugging symmetry
  - sign-crossing consumption remains optional behind
    `enable_sign_crossing_spark`
- Chosen Iteration 5 inspectability surface:
  - per-sink diagnostics are stored under `cached_quantities["spark_diagnostics"]`
  - deterministic trigger order is stored under
    `cached_quantities["spark_trigger_order"]`
  - emitted events carry only mechanical spark payloads and no `GRC9V3`
    Hessian semantics
- Chosen Iteration 5 execution boundary:
  - spark detection is implemented
  - expansion, rewiring, and growth remain deferred to Iteration 6

### Verification

- [x] Trigger tests cover instability, column-proxy, and non-trigger cases
- [x] Spark classification is deterministic under tied candidates
- [x] No `GRC9V3` semantic dependency leaks into the trigger path

Focused verification run:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_sparks tests.models.test_grc_9_runtime tests.models.test_grc_9_tensor tests.models.test_grc_9_state tests.models.test_family_stubs`
- result:
  - `Ran 28 tests`
  - `OK`

### Summary

Completed the mechanical spark-trigger slice. `GRC9` now classifies saturated
sink sparks deterministically, exposes inspectable per-sink diagnostics, and
keeps the entire trigger path purely mechanical rather than importing
`GRC9V3`-style semantics.

## Iteration 6. Expansion, Rewiring, And Growth

### Goal

Implement the canonical topology event path for `GRC9`.

### Checks

- [x] Implement sequential multi-sink spark handling
- [x] Implement expansion-size calculation with
  `n = max(1, ceil((D_eff - 2) / 7))`
- [x] Implement the canonical expansion module:
  - core node
  - three primary satellites
  - canonical internal spine wiring:
    - `(c,2) <-> (s1,5)`
    - `(c,5) <-> (s2,5)`
    - `(c,8) <-> (s3,5)`
- [x] If `n > 4`, implement additional expansion nodes as a tree under the
  satellites:
  - round-robin by column
  - using port `5` on the new node
  - and the lowest-index available port on the existing tree node
- [x] Implement column-preserving boundary reassignment
- [x] Implement state transfer and bond initialization with the baseline
  defaults:
  - `C_c = 0`
  - default `p_b = 1/3`
- [x] Handle empty-column satellites using the fixed `w_bond` fallback when
  needed
- [x] Distinguish parent-selection policy from chosen-port selection for growth
- [x] Implement lowest-index inactive-port selection
- [x] Implement optional adiabatic expansion schedule if included in the first
  baseline
- [x] Distinguish post-expansion budget verification from correction

### Implementation Notes

- Expansion must remain mechanical and column-preserving.
- The event should refine the substrate and then let later reflexive flow decide
  what identities emerge.
- If adiabatic expansion is deferred, keep the typed schedule state ready or
  document the deferral explicitly.
- Implemented the pure expansion/growth helpers in:
  - `src/pygrc/models/grc_9_expansion.py`
- Extended the executable `GRC9` topology-event surface in:
  - `src/pygrc/models/grc_9.py`
- Added focused Iteration 6 topology-event coverage in:
  - `tests/models/test_grc_9_expansion.py`
- Chosen sequential spark-application rule:
  - `_apply_topology_changes(...)` sorts spark events deterministically by sink
    node ID and applies them one at a time
  - sink/basin structure is recomputed after each local refinement before later
    candidates are considered
- Chosen expansion-size/runtime policy:
  - Eq. (13) is implemented as the lower-bound helper
    `compute_expansion_node_count(...)`
  - the runtime still enforces the canonical core-plus-three-satellites module,
    so actual module size is `max(4, n)` before any additional helper nodes are
    introduced
- Chosen internal-bond initialization policy:
  - spine and tree bonds use a local geometric-mean aggregate of inherited
    column conductances when defined
  - empty-column cases fall back deterministically to `w_bond`
- Chosen expansion-node coherence policy:
  - `C_c = 0` follows the paper baseline directly
  - additional tree/helper nodes also start at `0.0` coherence in the Phase 6
    baseline
  - these nodes represent newly created inactive capacity rather than inherited
    child identities
- Chosen boundary-reassignment policy:
  - reassignment remains column-preserving and deterministic
  - when exact port preservation is impossible under the canonical center-port
    spine rule, the implementation falls back to the lowest available port in
    the same column tree
  - this is the concrete resolution of the center-port conflict rather than a
    hidden random choice
- Chosen growth policy:
  - parent selection uses seeded stochastic outward-flux pressure
  - chosen-port selection remains a separate deterministic lowest-index rule
  - new child nodes attach through parent lowest inactive port and child port 1
- Chosen budget-handling policy:
  - `budget_target` is initialized lazily from the first live state if needed
  - expansion/growth first verify preservation by construction
  - correction is only applied if measurable drift appears
  - May 2026 robustness note: this lazy target inference is not known to make
    normal Phase 6 results numerically wrong, because the target is inferred
    before budget-sensitive topology events on ordinary step paths. It is
    nevertheless weaker invariant discipline than an explicitly locked initial
    target and is superseded by Iteration 12 below.
- Chosen schedule-state policy:
  - `adiabatic_expansion_substeps > 1` records typed schedule state on the
    expansion registry entry
  - the actual phased substep loop remains deferred to later step-loop work
- Updated validation policy:
  - `ExpansionRecord.parent_sink_id` is treated as historical event metadata and
    no longer has to remain a live node after refinement

### Verification

- [x] Expansion and rewiring are deterministic on fixed inputs
- [x] Multi-sink handling is sequential and test-backed
- [x] Growth fills the lowest-index inactive port on the selected parent
- [x] Budget survives every topology-event path

Focused verification run:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_expansion tests.models.test_grc_9_sparks tests.models.test_grc_9_runtime tests.models.test_grc_9_tensor tests.models.test_grc_9_state tests.models.test_family_stubs`
- result:
  - `Ran 34 tests`
  - `OK`

### Summary

Completed the first mechanical topology-event slice. `GRC9` now supports
sequential spark expansion, deterministic column-preserving rewiring,
fixed-spine module construction, target-capacity tree growth, and seeded
outward-flux birth with lowest-port attachment, while the full ordered step loop
still remains deferred to Iteration 8.

## Iteration 7. Coarse-Graining And Split

### Goal

Implement the family’s invertible local multiscale interface.

### Checks

- [x] Implement coarse-graining for supported nonnegative fields
- [x] Implement intra-column mode profiles
- [x] Implement exact `Split(...)` reconstruction
- [x] Expose the required public family methods:
  - `coarse_grain_columns(...)`
  - `split_columns(...)`
- [x] Implement exact signed-flux support via positive/negative decomposition
- [x] Decide whether compressed signed-flux mode is included in the baseline
- [x] If compressed mode is included, label it explicitly as non-exact
- [x] Implement deterministic coarse-cache invalidation for:
  - conductance recomputation
  - flux recomputation
  - expansion rewiring
  - growth events
  - any other occupied-port topology mutation

### Implementation Notes

- Exactness claims must stay honest.
- If compressed signed-flux mode is deferred, do not imply that the baseline
  supports it fully.
- Implemented the pure coarse-graining helpers in:
  - `src/pygrc/models/grc_9_coarse.py`
- Extended the public `GRC9` coarse interface in:
  - `src/pygrc/models/grc_9.py`
- Added focused Iteration 7 coverage in:
  - `tests/models/test_grc_9_coarse.py`
- Chosen baseline supported nonnegative fields:
  - `conductance`
  - `geometric_length`
  - `temporal_delay`
  - `flux_coupling`
  - `abs_flux`
- Chosen exact coarse-state shape:
  - nonnegative fields use `mode = exact_column_profile`
  - signed flux uses `mode = signed_flux_split`
  - both public methods return explicit `field_name` and `port_field` payloads
    rather than silently mutating family state
- Chosen exact signed-flux policy:
  - signed flux is represented exactly through `J+` / `J-` decomposition
  - compressed signed-flux mode is explicitly **not** part of the Phase 6
    baseline
  - the related checklist item is therefore satisfied by an explicit deferral,
    not by a hidden partial implementation
- Chosen coarse-cache policy:
  - public coarse states may be cached under `state.coarse_cache`
  - `_compute_metric(...)` invalidates on conductance recomputation
  - `_compute_edge_labels(...)` invalidates on label recomputation
  - `_compute_flux(...)` invalidates on flux recomputation
  - topology mutation paths invalidate through
    `_prune_runtime_state_after_topology_change(...)`
  - the current invalidation reason is recorded in
    `cached_quantities["coarse_cache_invalidation_reason"]`

### Verification

- [x] Supported nonnegative fields satisfy `Split(G(X)) == X`
- [x] Signed flux has one exact supported representation
- [x] Coarse-cache invalidation covers both value and topology triggers

Focused verification run:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_coarse tests.models.test_grc_9_expansion tests.models.test_grc_9_sparks tests.models.test_grc_9_runtime tests.models.test_grc_9_tensor tests.models.test_grc_9_state tests.models.test_family_stubs`
- result:
  - `Ran 39 tests`
  - `OK`

### Summary

Completed the exact coarse-graining slice. `GRC9` now exposes public
`coarse_grain_columns(...)` and `split_columns(...)` methods, supports exact
nonnegative reconstruction plus exact signed-flux decomposition, and invalidates
coarse cache state deterministically after both value and topology changes.

## Iteration 8. Step Loop, Serialization, And Family Tests

### Goal

Make the executable family reproducible and lock the spec-facing step order in
code.

### Checks

- [x] Implement the named internal hook surface from the plan:
  - `_compute_geometry(...)`
  - `_compute_column_diagnostic(...)`
  - `_compute_metric(...)`
  - `_compute_potential(...)`
  - `_compute_flux(...)`
  - `_detect_identities(...)`
  - `_detect_events(...)`
  - `_apply_topology_changes(...)`
  - `_apply_growth(...)`
  - `_apply_continuity(...)`
  - `_enforce_budget(...)`
  - `_refresh_coarse_cache(...)`
- [x] Add `_compute_column_diagnostic(...)`
- [x] Implement the spec-locked step order in `GRC9.step()`
- [x] Implement snapshot/save/load support for the nine-slot state surface
- [x] Serialize:
  - port occupancy
  - port-edge structure
  - selected edge-label families
  - `edge_label_computation_mode`
  - `edge_label_params`
  - expansion in-progress state
  - optional coarse-cache metadata
- [x] Add deterministic step and digest tests
- [x] Add save/load roundtrip tests

### Implementation Notes

- The spec-level discrete ordering is authoritative for implementation.
- The paper’s compact algorithmic statement is not a substitute for the
  explicit step-loop contract.
- Implemented the full Iteration 8 executable step and replay surface in:
  - `src/pygrc/models/grc_9.py`
- Added focused Iteration 8 coverage in:
  - `tests/models/test_grc_9_step.py`
- Updated the generic family contract to reflect the now-executable `GRC9`
  surface in:
  - `tests/models/test_family_stubs.py`
- Chosen baseline boundary behavior:
  - `boundary_mode = prune` remains the only executable Phase 6 baseline
  - `barrier` and `ghost` are now rejected during config/state validation
    rather than being accepted and failing later in `step()`
  - enabling `barrier` or `ghost` later requires explicit boundary-behavior
    implementation plus honest `boundary_barrier` capability advertisement
- Chosen continuity and budget policy:
  - `apply_continuity` uses the paper/spec `dt`-weighted flux divergence
  - `enforce_budget` clamps negative coherence first, then closes the budget
    against `budget_target`
  - positive budget deficit is repaired by deterministic uniform shift across
    all live nodes rather than an arbitrary single-node patch
- Chosen coarse-cache refresh policy:
  - the end-of-step hook is invalidate-only in the Phase 6 baseline
  - public coarse states can be recomputed on demand after the step
- Fixed one replay-critical runtime detail during Iteration 8:
  - raw Python `random.Random.getstate()` tuples supplied through
    `from_state(...)` are now restored back to tuple form instead of being left
    as canonicalized lists, so save/load replay remains `random.Random`
    compatible

### Verification

- [x] `GRC9.step()` follows the full locked 14-step order directly:
  1. row tensor
  2. conductance update
  3. selected analytic edge labels
  4. potential
  5. flux
  6. successor map / sinks / basins
  7. spark detection
  8. expansion
  9. growth
  10. configured boundary behavior
  11. continuity update
  12. exact budget preservation
  13. coarse-cache refresh / invalidation
  14. observables
- [x] Same state + same params + same RNG state => same snapshot digest
- [x] Save/load preserves occupied-port runtime semantics without semantic loss

Focused verification run:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_step tests.models.test_grc_9_coarse tests.models.test_grc_9_expansion tests.models.test_grc_9_sparks tests.models.test_grc_9_runtime tests.models.test_grc_9_tensor tests.models.test_grc_9_state tests.models.test_family_stubs`
- result:
  - `Ran 43 tests`
  - `OK`

### Summary

The executable `GRC9` step loop and replay surface are deterministic and
restorable.

## Iteration 9. Mid-Phase Constitutive Gate

### Goal

Pause for the required written constitutive review before later evidence lanes
and source-facing work grow around the runtime baseline.

### Checks

- [x] Create `Phase-6-MidGate-Review.md`
- [x] Review row/column separation in the current implementation
- [x] Review tensor representation against the paper intent
- [x] Review spark semantics to confirm they remain purely `GRC9`
- [x] Review expansion wiring and reassignment determinism
- [x] Review coarse-graining exactness claims
- [x] Review observability strength for later artifact lanes

### Implementation Notes

- This iteration is a required artifact, not an optional retrospective.
- Do not move on to stronger evidence claims while major constitutive ambiguity
  remains unresolved.
- Completed the required written review artifact in:
  - `implementation/Phase-6-MidGate-Review.md`
- Mid-gate verdict:
  - the executable baseline remains recognizably pure mechanical `GRC9`
  - Iteration 10 may proceed
  - one constitutive runtime issue is still carried forward explicitly:
    the `abundance` observable contract is still ambiguous because
    `compute_observables()` currently reads the step-6 `sink_set` while
    topology may still change later in the same step
  - the carried-forward decision must preserve the locked 14-step loop rather
    than inserting a new named public phase ad hoc
- Explicit deferred boundaries carried forward by the review:
  - `boundary_mode = barrier`
  - `boundary_mode = ghost`
  - artifact-backed telemetry/report lanes

### Verification

- [x] The mid-gate review exists as a written artifact
- [x] Open constitutive gaps are documented explicitly rather than implied away

Review validation context:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_step tests.models.test_grc_9_coarse tests.models.test_grc_9_expansion tests.models.test_grc_9_sparks tests.models.test_grc_9_runtime tests.models.test_grc_9_tensor tests.models.test_grc_9_state tests.models.test_family_stubs`
- result:
  - `Ran 44 tests`
  - `OK`

### Summary

The Phase 6 runtime baseline has been reviewed in writing before closeout-style
claims expand.

## Iteration 10. Observables, Telemetry, And Artifact Lanes

### Goal

Make Phase 6 observable through saved outputs rather than tests alone.

### Checks

- [x] Implement required observables:
  - `abundance`
  - `budget_current`
  - `budget_error`
  - `num_nodes`
  - `num_port_edges`
  - `spark_count`
  - `active_degree_histogram`
- [x] Implement recommended observables if feasible:
  - column profile sparsity
  - expansion count
  - sink-module sizes
- [x] Lock baseline observable encodings:
  - `budget_error = abs(budget_current - budget_target)`
  - `active_degree_histogram: dict[int, int]` over degrees `0..9`
- [x] Resolve the Iteration 9 carried-forward `abundance` ambiguity:
  - compute a non-persisted topology-updated sink diagnostic from the current
    stored flux field inside `compute_observables()`
  - document the chosen contract in `Phase-6-StepLoop.md`
  - keep the public step loop at the locked 14 phases
- [x] Add telemetry/report surfaces sufficient for at least one representative
  artifact-backed lane
- [x] Ensure expansion and growth are visible in saved outputs

### Implementation Notes

- Phase 6 should reuse the shared telemetry/report infrastructure, not rebuild
  it.
- Saved outputs should make the event sequence legible, not only the final
  state.
- Implemented the Iteration 10 observable and telemetry slice in:
  - `src/pygrc/models/grc_9.py`
  - `src/pygrc/telemetry/experiments.py`
  - `src/pygrc/telemetry/_experiment_defaults.py`
  - `src/pygrc/telemetry/_experiment_results.py`
  - `src/pygrc/telemetry/schema.py`
- Added focused Iteration 10 coverage in:
  - `tests/models/test_grc_9_step.py`
  - `tests/telemetry/test_experiments.py`
- Chosen `abundance` contract:
  - compute a local non-persisted topology-updated sink diagnostic from the
    current stored flux field inside `compute_observables()`
  - do not mutate the persisted `sink_set`
  - do not add a 15th named step to the public loop
  - do not claim a second full reflexive pass after continuity
- Chosen representative artifact-backed lane:
  - `telemetry.run_grc9_representative_experiment(...)`
  - lane default: `phase6_mechanical_baseline`
  - path default: `outputs/representative/grc9/<lane>/{primary,replay}`
  - baseline trajectory emits spark/expansion on the first step and growth on
    later steps
- Implemented recommended observables that were cheap and constitutively clear:
  - `column_profile_sparsity`
  - `expansion_count`
  - `sink_module_sizes`
- Kept the shared telemetry stack authoritative rather than building a
  Phase-6-only reporting path
- Remaining explicit Phase 6 limitation after Iteration 10:
  - `boundary_mode = barrier` and `boundary_mode = ghost` remain unavailable in
    the executable Phase 6 baseline and should be treated as a real remaining
    family limitation, not a merely mid-phase-acceptable omission
  - this is now enforced honestly at config/state validation time rather than
    being left to fail later inside `step()`

### Verification

- [x] Artifact outputs expose event sequence rather than only final state
- [x] Observables distinguish runtime health from topology evolution
- [x] The chosen `abundance` contract is explicit and stable across saved
  outputs, tests, and documentation
- [x] At least one representative artifact-backed lane exists

Focused verification run:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_step tests.models.test_grc_9_coarse tests.models.test_grc_9_expansion tests.models.test_grc_9_sparks tests.models.test_grc_9_runtime tests.models.test_grc_9_tensor tests.models.test_grc_9_state tests.models.test_family_stubs tests.telemetry.test_schema tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grc9_representative_experiment_emits_artifacts_and_eventful_reports`
- result:
  - `Ran 52 tests`
  - `OK`

### Summary

Phase 6 now has an honest observability surface and at least one saved
artifact-backed lane.

## Iteration 11. Real-Seed Lane And Closeout Readiness

### Goal

Push the family through the full validation ladder and confirm closeout
readiness.

### Checks

- [x] Run pure-runtime control probes
- [x] Run a representative artifact-backed lane
- [x] Run at least one real-seed or real-experiment lane
- [x] Decide whether a rich-source dense artifact lane is needed in Phase 6 or
  deferred pending source-surface expansion
- [x] Record what remains explicitly deferred to `GRC9V3`
- [x] Review Phase 6 exit criteria against the implementation plan

### Implementation Notes

- Do not treat passing tests as closeout on their own.
- If the real-seed lane exposes a source/projector gap, record it explicitly
  rather than muddying the runtime closure claim.
- Implemented the seed-driven structural lowering and closeout-facing artifact
  surface in:
  - `src/pygrc/models/grc_9_landscape.py`
  - `src/pygrc/telemetry/experiments.py`
  - `src/pygrc/telemetry/_experiment_defaults.py`
  - `src/pygrc/telemetry/_experiment_results.py`
  - `src/pygrc/telemetry/__init__.py`
- Added closeout-facing reconstruction entrypoints in:
  - `scripts/run_grc9_representative_telemetry.py`
  - `scripts/run_grc9_landscape_telemetry.py`
- Added focused Iteration 11 model/telemetry coverage in:
  - `tests/models/test_grc_9_landscape.py`
  - `tests/telemetry/test_experiments.py`
- Recorded the closeout state and concrete artifact evidence in:
  - `implementation/Phase-6-Closeout.md`
- Chosen real-seed lowering policy:
  - Phase 6 uses a structural `LandscapeSeed -> GRC9` graph graft
  - it reuses the validated `GRCV2` landscape blueprint boundary
  - it preserves node priors, carrier edges, and transport-intent multipliers
    where mechanically meaningful
  - it is a useful bridge for Phase 6 evidence, not a full family-native
    `GRCL-9` implementation
  - it does not claim `GRC9V3` semantic lowering
- Chosen rich-source closeout policy:
  - the representative eventful lane and the real-seed structural lane are
    sufficient for honest Phase 6 closeout
  - the dense rich-source lane is explicitly deferred because Phase 6 still
    does not open a family-local source semantics surface
- Recorded explicit deferred boundary to `GRC9V3`:
  - rich semantic/source lifts
  - choice/collapse semantics
  - source-conditioned dense artifact lanes
  - a true family-native `GRCL-9` lowering layer
- Executed closeout-facing artifact runs:
  - representative lane:
    `outputs/representative/grc9/phase6_mechanical_baseline/{primary,replay}`
  - real-seed lane:
    `outputs/representative/grc9_landscape/phase6_seed_baseline/{cell-1,cell-4}`

### Verification

- [x] `GRC9` runs end to end without `GRCV3` semantic dependency
- [x] Expansion and rewiring are deterministic in saved evidence, not just tests
- [x] Supported coarse-grain / Split operations are invertible on the claimed
  field set
- [x] Deferred work is named explicitly and not silently carried into Phase 7

Focused validation runs performed at closeout:

- pure-runtime and representative/telemetry validation:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_state tests.models.test_grc_9_tensor tests.models.test_grc_9_runtime tests.models.test_grc_9_sparks tests.models.test_grc_9_expansion tests.models.test_grc_9_coarse tests.models.test_grc_9_step tests.models.test_grc_9_landscape tests.models.test_family_stubs tests.telemetry.test_schema tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grc9_representative_experiment_emits_artifacts_and_eventful_reports tests.telemetry.test_experiments.TelemetryLandscapeExperimentTest.test_run_grc9_landscape_experiment_emits_artifacts_and_reports`
  - result:
    - `Ran 55 tests`
    - `OK`
- representative artifact lane:
  - `./.venv/bin/python scripts/run_grc9_representative_telemetry.py --outputs-root outputs --lane-name phase6_mechanical_baseline --steps 4`
- real-seed artifact lane:
  - `./.venv/bin/python scripts/run_grc9_landscape_telemetry.py --outputs-root outputs --profile phase6_seed_baseline --steps 3`

### Summary

Phase 6 closeout is now justified. The family has:

- pure-runtime control evidence
- a representative eventful artifact lane
- a real-seed structural artifact lane
- explicit closeout documentation
- an honest remaining boundary to `GRC9V3`

## Iteration 12. Scalar Budget Target Robustness Repair

### Goal

Strengthen pure GRC9 budget correctness discipline by locking the scalar
budget target from the initial live state during construction / `from_state(...)`
normalization, while preserving lazy inference only as a compatibility fallback.

This is not the Phase 7 GRC9V3 `M_i` basin-mass repair. Pure GRC9 has no
GRCV3 basin-attribute mass field. The invariant here is the paper's mechanical
scalar budget:

```text
B = sum_i C_i
```

### Checks

- [x] Keep pure GRC9 free of GRC9V3 basin-mass semantics
- [x] Initialize `budget_target` from the initial live `node_coherence` sum when
      no explicit target is provided
- [x] Preserve explicitly provided nonzero `budget_target`
- [x] Define and test the policy for explicit zero-budget states
- [x] Record `budget_target_source` in `cached_quantities`
- [x] Keep `_ensure_budget_target()` as a compatibility fallback only
- [x] Ensure expansion, growth, continuity, and `_enforce_budget()` close
      against the fixed initial target
- [x] Ensure save/load round trips preserve the fixed target and source
- [x] Document that existing normal-path Phase 6 results are not automatically
      invalidated by the former lazy inference policy

### Verification

- [x] Unit test: omitted target is fixed at construction/from_state
- [x] Unit test: direct coherence mutation after construction does not change
      the target
- [x] Unit test: explicit target survives construction and save/load
- [x] Unit test: explicit zero-target policy is unambiguous
- [x] Regression test: expansion budget preservation still closes to the fixed
      target
- [x] Regression test: growth budget preservation still closes to the fixed
      target
- [x] Regression test: step-loop budget enforcement still closes to the fixed
      target

### Summary

Implemented. Pure GRC9 now locks `budget_target` during state construction /
`from_state(...)` normalization when the target is omitted, preserves explicit
nonzero and explicit zero targets, and records `budget_target_source` in
`cached_quantities`. `_ensure_budget_target()` remains only as a compatibility
fallback for pre-normalized states that lack the source tag.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.models.test_grc_9_state \
  tests.models.test_grc_9_runtime \
  tests.models.test_grc_9_tensor \
  tests.models.test_grc_9_sparks \
  tests.models.test_grc_9_expansion \
  tests.models.test_grc_9_coarse \
  tests.models.test_grc_9_step \
  tests.models.test_grc_9_landscape \
  tests.models.test_grc_9_grcl9_lowering \
  tests.telemetry.test_grc9_contract \
  tests.telemetry.test_grc9_extensions
```

Result: 75 tests OK.
