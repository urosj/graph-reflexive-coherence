# Phase 4 Implementation Checklist

This document tracks the execution of **Phase 4: `GRCV2` Baseline**.

It is intentionally separate from [`Phase-4-ImplementationPlan.md`](./Phase-4-ImplementationPlan.md):

- the plan defines scope, workstreams, boundaries, and acceptance criteria,
- this checklist records how the Phase 4 work is actually executed iteration by iteration.

Each iteration should contain:

- a bounded implementation slice,
- concrete checkboxes that can be ticked off during execution,
- implementation notes recorded alongside the work,
- verification steps tied to the iteration output,
- and a short summary when the iteration closes.

## Usage Rules

- Keep iterations small enough that verification remains clear.
- Update checkboxes during implementation, not after the fact.
- Record design decisions near the affected work rather than in a separate log.
- If a plan change is needed, update the plan document first or in the same change.
- If an item is deferred, leave it unchecked and add a short reason in the notes or summary.
- Keep `GRCV2` implementation notes aligned with:
  - [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
  - [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)
  - [`Phase-4-ImplementationPlan.md`](./Phase-4-ImplementationPlan.md)
  - [`../specs/grc-v2-spec.md`](../specs/grc-v2-spec.md)

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

Create the Phase 4 execution checklist and align it with the Phase 4 implementation plan.

### Checks

- [x] Create `Phase-4-ImplementationChecklist.md`
- [x] Link the checklist from `ImplementationPhases.md`
- [x] Align the checklist structure with the Phase 4 workstreams
- [x] Decide whether Phase 4 needs any additional companion planning docs before implementation starts

### Implementation Notes

- The execution checklist follows the same separation-of-concerns pattern used in earlier phases.
- The Phase 4 plan remains the normative planning document; this file is the execution tracker.
- Possible companion docs for this phase were already identified in the plan:
  - `Phase-4-EquationMap.md`
  - `Phase-4-EventOrdering.md`
  - `Phase-4-TestMatrix.md`
- Those companion docs are optional and should only be created if the implementation work outgrows the main checklist and plan.
- No additional companion docs are needed at the start of Phase 4.

### Verification

- [x] The checklist file exists under `implementation/`
- [x] `ImplementationPhases.md` points to the checklist
- [x] The checklist iterations map cleanly onto the Phase 4 plan

### Summary

Phase 4 now has a paired plan and execution checklist. Additional companion docs remain optional until implementation pressure makes them necessary, but none are needed yet.

## Iteration 1. `GRCV2State` And Construction Surface

### Goal

Replace the `GRCV2` stub with a real v2-specific state dataclass and construction surface.

### Checks

- [x] Implement `GRCV2State` as a dedicated `@dataclass` subclass of `GRCState`
- [x] Add explicit `GRCV2` construction validation for the required parameter catalogue
- [x] Validate constitutive mode values:
  - [x] `curvature_backend`
  - [x] `frame_mode`
  - [x] `boundary_mode`
  - [x] `split_distribution_mode`
- [x] Implement or update `from_config(...)`
- [x] Implement or update `from_state(...)`
- [x] Implement or update `get_state()` / `set_state(...)`
- [x] Keep `list_capabilities()` truthful and frame-mode aligned

### Implementation Notes

- `GRCV2State` should expose the spec-locked fields directly:
  - `nodes`
  - `edges`
  - `geometric_length`
  - `temporal_delay`
  - `flux_coupling`
  - `flux`
  - `potential`
  - `sink_set`
  - `basins`
  - `split_registry`
  - `rng_state`
- `OrientedEdgeId` needs one explicit deterministic representation before flux storage is finalized.
- `split_registry` should be treated as structured progress state, not an opaque convenience dict.
- `set_state(...)` should reject incompatible state objects explicitly.
- Added `src/pygrc/models/grc_v2_state.py` with:
  - `GRCV2State`
  - `OrientedEdgeId = tuple[EdgeId, NodeId]`
- Replaced the generic stub in `src/pygrc/models/grc_v2.py` with a real `GRCV2` construction/state surface:
  - strict v2 parameter validation
  - constitutive mode validation
  - `from_config(...)`
  - `from_state(...)`
  - `get_state()` / `set_state(...)`
  - frame-mode-aware `list_capabilities()`
  - deterministic `reset()`
- Chosen construction-time parameter naming:
  - site potential fields are currently validated as:
    - `site_potential_selection`
    - `site_potential_params`
- Chosen host-frame rule:
  - `frame_mode="host_embedding"` requires non-empty `host_geometry_fields`
- Chosen state-validation boundary:
  - `GRCV2State.topology` must be a `WeightedGraphBackend`
  - node/edge/label/potential/basin references must point to live topology IDs
  - coherence values must be non-negative
- Added basic `snapshot()` / `save()` / `load()` support for the v2 state surface early so construction/state tests can already roundtrip through the shared serializer, even though the fuller runtime integration work remains a later iteration.
- Exported `GRCV2State` and `OrientedEdgeId` from `src/pygrc/models/__init__.py`.
- Added focused tests in:
  - `tests/models/test_grc_v2_construction.py`
- Updated `tests/models/test_family_stubs.py` so the shared family-contract checks still hold now that `GRCV2` advertises a frame capability in addition to its required baseline claims.

### Verification

- [x] `GRCV2.from_config(...)` constructs a valid non-stub model
- [x] `GRCV2.from_state(...)` reconstructs a runnable model from explicit state and params
- [x] Invalid params/state/mode values are rejected early

### Summary

Implemented the Phase 4 `GRCV2` construction/state surface. `GRCV2` is no longer a generic family stub: it now has a real `GRCV2State` dataclass, strict v2 parameter and mode validation, frame-aware capability advertising, validated state installation/restoration, and early shared-serializer roundtrip support, while `step()` remains deferred to Iteration 2.

## Iteration 2. Step Skeleton And Internal Hook Surface

### Goal

Implement the executable step skeleton with the spec-locked 14-step order and named internal hooks.

### Checks

- [x] Replace `NotImplementedError` stub stepping with a real ordered step path
- [x] Implement or mirror the internal hook surface:
  - [x] `_compute_geometry(...)`
  - [x] `_compute_metric(...)`
  - [x] `_compute_potential(...)`
  - [x] `_compute_flux(...)`
  - [x] `_detect_identities(...)`
  - [x] `_detect_events(...)`
  - [x] `_apply_topology_changes(...)`
  - [x] `_apply_continuity(...)`
  - [x] `_enforce_budget(...)`
- [x] Encode the required 14-step order explicitly in the implementation
- [x] Make `step()` return a real `StepResult`
- [x] Keep `run(...)` on the shared contract surface working against the executable model

### Implementation Notes

- This iteration is about control-flow shape first, not full numerical fidelity.
- The implementation should make the ordered step pipeline inspectable and testable before all kernels are finalized.
- Event ordering and topology mutation ordering must be deterministic from the start.
- Replaced the remaining `NotImplementedError` in `src/pygrc/models/grc_v2.py` with a real executable step skeleton.
- Chosen explicit step trace/order:
  - `compute_geometry`
  - `compute_metric`
  - `compute_edge_labels`
  - `build_laplacian`
  - `compute_potential`
  - `compute_flux`
  - `detect_identities`
  - `detect_events`
  - `apply_topology_changes`
  - `apply_front_birth`
  - `apply_boundary_behavior`
  - `apply_continuity`
  - `enforce_budget`
  - `compute_observables`
- Mirrored the common-interface internal decomposition with executable v2 helpers:
  - `_compute_geometry(...)`
  - `_compute_metric(...)`
  - `_compute_edge_labels(...)`
  - `_build_laplacian_if_required(...)`
  - `_compute_potential(...)`
  - `_compute_flux(...)`
  - `_detect_identities(...)`
  - `_detect_events(...)`
  - `_apply_topology_changes(...)`
  - `_apply_front_birth(...)`
  - `_apply_boundary_behavior(...)`
  - `_apply_continuity(...)`
  - `_enforce_budget(...)`
- Chosen Iteration 2 scope boundary:
  - hook implementations are intentionally minimal and deterministic
  - no real split/birth/spark topology mutation has been introduced yet
  - `_detect_events(...)` currently returns an empty list
  - `_apply_topology_changes(...)` rejects non-empty event lists until later iterations implement real topology events
- Chosen step bookkeeping surface:
  - `StepResult.bookkeeping["step_order"]` records the executed order
  - `StepResult.bookkeeping["expected_step_order"]` stores the canonical order tuple
  - `GRCV2State.cached_quantities["last_step_trace"]` mirrors the executed order for debugging/tests
- Chosen step progression rule:
  - `step()` now increments:
    - `state.step_index`
    - `state.time += dt`
  - `run(...)` now works against the real executable step surface through the shared base contract
- Added early baseline observable computation in `compute_observables(...)` so the step result is already meaningful:
  - required observables plus recommended counters/defaults
- Added focused tests in:
  - `tests/models/test_grc_v2_step_skeleton.py`

### Verification

- [x] One step executes without stub failures on a minimal valid model
- [x] The step order is explicit enough to test directly
- [x] No family logic from `GRCV3` or `GRC9` leaks into the skeleton

### Summary

Implemented the executable `GRCV2` step skeleton. The model now steps through the full spec-locked ordered pipeline with named internal hooks, deterministic bookkeeping, state/time progression, baseline observables, and no-op topology-event behavior until later iterations fill in the actual numerical and event semantics.

## Iteration 3. Conductance And Analytic Edge Labels

### Goal

Implement the baseline node-tensor / scalar conductance layer and the shared analytic edge-label family.

### Checks

- [x] Implement node-tensor computation `K_i`
- [x] Implement scalar dynamical conductance `w_ij`
- [x] Implement selected edge labels:
  - [x] `geometric_length`
  - [x] `temporal_delay`
  - [x] `flux_coupling`
- [x] Implement `edge_label_computation_mode`
- [x] Implement `edge_label_params`
- [x] Preserve the baseline rule that only `w_ij` drives the actual update equations

### Implementation Notes

- `flux_coupling := abs(J_ij)` should be explicit in the implementation.
- `temporal_delay` should use the transport-ratio form from the spec.
- Label availability must follow the shared common-interface contract.
- `frame_mode` should drive how geometry/label surrogates are built.
- Extended `src/pygrc/models/grc_v2.py` to replace the placeholder metric/label hooks with deterministic baseline behavior.
- Chosen node-tensor baseline:
  - `_compute_geometry(...)` now caches one per-node tensor summary containing:
    - `coherence`
    - `neighbor_mean`
    - `local_pressure`
    - `curvature_term`
- Chosen scalar conductance baseline:
  - `_compute_metric(...)` now computes `w_ij` from:
    - node coherence mean
    - local-pressure gap
    - optional curvature contribution
  - current reference formula is deterministic and parameterized by:
    - `alpha`
    - `beta`
    - `gamma`
    - `delta`
    - `eta`
    - `kappa_c`
  - `w_ij` remains the single dynamical conductance used by the step loop
- Chosen curvature baseline:
  - `curvature_backend = "none"` gives zero curvature term
  - `forman` and `ollivier` were initially introduced as baseline placeholders
  - later remediation upgraded them to real in-house weighted-substrate backends
  - this iteration should therefore be read as the first metric/label landing point, not
    the final curvature state
- Chosen edge-label behavior:
  - `geometric_length`
    - `ambient_metric` for `host_embedding`
    - `induced_intrinsic` for `induced_local_frame`
    - `intrinsic_surrogate` for `combinatorial`
  - `flux_coupling = abs(J_ij)` using the primary oriented edge entry
  - `temporal_delay` uses the transport-ratio formula with:
    - `temporal_v0`
    - `temporal_rho`
    - `eps_tau`
- Chosen selection behavior:
  - unselected label families are cleared each step
  - selected labels are populated deterministically
  - `temporal_delay` computes its internal prerequisites even if `geometric_length` or `flux_coupling` were not selected for export
- Chosen metadata placement:
  - `edge_label_computation_mode` currently lives in:
    - `GRCV2State.cached_quantities["edge_label_computation_mode"]`
  - `edge_label_params` currently lives in:
    - `GRCV2State.cached_quantities["edge_label_params"]`
- Added focused tests in:
  - `tests/models/test_grc_v2_metric_labels.py`

### Verification

- [x] The model computes stable `w_ij` values for a fixed state
- [x] Edge-label selection works for `"all"` and subset cases
- [x] Label computation metadata is present and reproducible

### Summary

Implemented the baseline conductance and analytic edge-label layer for `GRCV2`. The executable model now computes deterministic node-tensor summaries, scalar conductances, frame-dependent geometric lengths, transport-ratio temporal delays, absolute-flux coupling labels, and reproducible label metadata while keeping `w_ij` as the only actual dynamical edge weight.

## Iteration 4. Potential, Flux, Sinks, And Basins

### Goal

Implement the deterministic potential/flux layer and identity extraction from the directed flux graph.

### Checks

- [x] Implement node potentials `Phi_i`
- [x] Implement directed edge fluxes `J_ij`
- [x] Preserve directed-flux antisymmetry explicitly
- [x] Implement directed-edge interpretation `i -> j` when `J_ij > 0`
- [x] Implement sink-set detection
- [x] Implement basin extraction by repeated successor composition

### Implementation Notes

- Sink ordering, successor choice, and basin ordering all need deterministic tie-break rules.
- Identity extraction must remain flux-topology based and avoid `GRCV3` basin attributes.
- Extended `src/pygrc/models/grc_v2.py` to replace the placeholder potential/identity logic with a deterministic flux-topology layer.
- Chosen runtime potential rule:
  - `_compute_potential(...)` now implements:
    - `Phi_i = kappa_c * sum_j w_ij (C_i - C_j) - V'(C_i)`
  - currently supported site-potential selections:
    - `quadratic`
    - `linear`
  - the site-potential derivative term depends only on:
    - local coherence
    - explicit `site_potential_params`
  - neighbor interaction remains separated into the `kappa_c`-weighted conductance sum
- Chosen directed-flux rule:
  - `_compute_flux(...)` computes one antisymmetric pair per live edge:
    - `J_ij = -eta * w_ij * (Phi_i - Phi_j)`
    - `(edge_id, node_a) = J`
    - `(edge_id, node_b) = -J`
  - flux direction therefore remains recoverable directly from the oriented-edge map
- Chosen identity-extraction rule:
  - a directed edge `i -> j` exists when the stored flux from node `i` along that edge is positive
  - sinks are nodes with:
    - no incident neighbor contributing negative incoming flux
    - strictly positive total incoming flux
  - each node chooses at most one successor:
    - highest positive outgoing flux
    - ties broken deterministically by neighbor ID, then edge ID
  - basins are built from repeated successor composition until a sink is reached
- Chosen deterministic identity bookkeeping:
  - the unique-successor map is cached in:
    - `GRCV2State.cached_quantities["successor_map"]`
  - basin membership is accumulated deterministically by sink ID
- This iteration still keeps identity extraction flux-topology based only:
  - no basin-attribute objects
  - no hierarchy labels
  - no `GRCV3` differential summary state
- Extended focused tests in:
  - `tests/models/test_grc_v2_step_skeleton.py`
  - `tests/models/test_grc_v2_metric_labels.py`

### Verification

- [x] Potentials and fluxes are reproducible for a fixed state
- [x] Sink sets and basins are reproducible for a fixed state
- [x] Flux antisymmetry is preserved by the implementation

### Summary

Implemented the deterministic potential/flux/identity layer for `GRCV2`. The executable model now computes `kappa_c`-weighted interaction potentials plus site-potential derivatives, stores antisymmetric `-eta`-scaled directed flux per edge, derives sinks using the stricter per-neighbor inflow rule, and extracts basins by deterministic unique-successor composition while remaining within the baseline flux-topology semantics of the v2 family.

## Iteration 5. Spark Backend And Event Detection

### Goal

Implement the v2 proxy spark backend and event detection surface.

### Checks

- [x] Implement at least one spark backend:
  - Cheeger conductance proxy
  - or restricted Laplacian eigenvalue trigger
- [x] Expose the supported backend through public config
- [x] Order spark candidates deterministically before topology changes
- [x] Emit structured spark/topology events suitable for the later topology-application pass

### Implementation Notes

- The spec requires support for at least one backend and public selection where multiple backends exist.
- The plan currently prefers the Cheeger proxy as the baseline default if it is the simpler stable path, but that is implementation guidance rather than a spec mandate.
- Extended `src/pygrc/models/grc_v2.py` with the first concrete spark backend:
  - `spark_backend = "cheeger_proxy"`
  - unsupported backend selections are rejected during parameter validation
- Chosen threshold policy:
  - `h_thr` is used when present
  - otherwise the current implementation falls back to `eps_spark` as the public threshold input for the Cheeger proxy
- Chosen deterministic candidate ordering:
  - lower Cheeger score first
  - ties broken by sink node ID
  - then by deterministic basin-member tuple
- Chosen event surface:
  - `GRCEvent(kind="spark", ...)`
  - event payload includes:
    - `backend`
    - `sink_node_id`
    - `basin_members`
    - `score`
    - `threshold`
    - `threshold_source`
    - `boundary_cut`
    - `basin_volume`
    - `complement_volume`
    - `candidate_rank`
    - `topology_event_kind = "soft_split"`
- Spark events are currently topology-deferred:
  - `_apply_topology_changes(...)` accepts spark events as structured no-op requests
  - pending records are cached in:
    - `GRCV2State.cached_quantities["pending_topology_events"]`
  - Iteration 6 will consume that structure for real split initialization
- Updated observable bookkeeping so current-step spark events are reflected immediately in:
  - `spark_count`
- Added focused tests in:
  - `tests/models/test_grc_v2_sparks.py`

### Verification

- [x] Spark detection is deterministic for fixed params and fixed state
- [x] Public config selects the supported spark backend explicitly
- [x] Event records are structured enough for split/birth handling

### Summary

Implemented the first real v2 spark backend using a deterministic Cheeger conductance proxy. `GRCV2` now accepts explicit `spark_backend` selection, emits ordered `spark` events with enough payload for later soft-split handling, and surfaces current-step spark counts without yet mutating topology.

## Iteration 6. Soft Split, Front Birth, And Boundary Handling

### Goal

Implement the v2 topology events and baseline boundary/pruning behavior.

### Checks

- [x] Implement soft split initialization from spark events
- [x] Implement split progression over `tau_split`
- [x] Use the Phase 0 baseline split rule:
  - `split_distribution_mode = "equal"`
- [x] Make split completion condition explicit and testable
- [x] Implement front birth from outward flux pressure
- [x] Implement baseline `prune` boundary behavior
- [x] Reject unsupported `barrier` / `ghost` behavior explicitly if not fully implemented yet
- [x] Preserve deterministic ID allocation through all topology changes

### Implementation Notes

- Parent removal must happen only after split completion.
- `eps_prune` should be a validated required parameter with explicit threshold behavior.
- The weighted backend’s tombstoned-slot policy must remain intact through topology mutation.
- Extended `src/pygrc/models/grc_v2.py` so spark events now drive real split initialization.
- Chosen split initialization rule:
  - only `split_distribution_mode = "equal"` is accepted
  - parent coherence is transferred immediately into two equal child masses
  - parent node remains in topology until split completion
  - child IDs come from the weighted backend monotone counters
- Chosen split progression rule:
  - each active split registry entry advances once per step
  - child-neighbor and parent-child edge weights ramp linearly over `tau_split`
  - completion happens when `progress_step / ceil(tau_split) >= 1.0`
  - only then is the parent node removed
- Chosen split registry shape:
  - `parent_node_id`
  - `child_node_ids`
  - `split_ratio`
  - `progress_step`
  - `progress_fraction`
  - `total_steps`
  - `complete`
  - `parent_removed`
  - edge-target metadata for replayable progression
- Chosen front-birth baseline:
  - deterministic, not probabilistic
  - a node births one child when its positive outgoing flux exceeds `lambda_birth`
  - seed mass is `min(parent_mass, alpha_seed * outward_flux * dt)`
  - seed edge enters with deterministic weight derived from `alpha_seed * outward_flux`
- Chosen prune baseline:
  - only isolated nodes below `eps_prune` are removed
  - removed mass is redistributed uniformly across survivors
  - prune order follows ascending node ID
- Chosen event surface additions:
  - `split_init`
  - `split_progress`
  - `split_complete`
  - `birth`
  - `prune`
- Current-step event bookkeeping is now cumulative through:
  - spark detection
  - topology changes
  - front birth
  - boundary pruning
- Added focused tests in:
  - `tests/models/test_grc_v2_topology_events.py`
  - and updated `tests/models/test_grc_v2_sparks.py` for the real topology-event surface

### Verification

- [x] Split progression is deterministic across successive steps
- [x] Birth adds nodes/edges without ID reuse
- [x] Baseline prune behavior works without silent degradation of richer boundary modes

### Summary

Implemented the first real topology-mutation layer for `GRCV2`. Spark events now initialize structured equal splits, active splits progress deterministically until explicit parent removal, deterministic front birth adds nodes and seed edges from outward flux pressure, baseline `prune` removes isolated low-mass nodes with explicit redistribution, and unsupported richer boundary modes still fail explicitly instead of degrading silently.

## Iteration 7. Continuity Update, Budget Enforcement, And Observables

### Goal

Implement the continuity update, exact budget closure, and the required observable surface.

### Checks

- [x] Implement the continuity update to node coherence
- [x] Implement explicit budget target bookkeeping
- [x] Implement budget remainder handling per the shared guidance
- [x] Preserve non-negativity of coherence after budget correction
- [x] Implement required observables:
  - `abundance`
  - `weighted_abundance`
  - `sink_count`
  - `budget_current`
  - `budget_error`
  - `num_nodes`
  - `num_edges`
- [x] Add recommended observables where practical:
  - `spark_count`
  - `birth_count`
  - `prune_count`
  - average conductance

### Implementation Notes

- Budget preservation is a core semantic, not a best-effort correction.
- Remainder should be explicit, bounded, and cleared as soon as practical rather than allowed to drift.
- Observable computation should be derived from post-step state only.
- Extended `src/pygrc/models/grc_v2.py` with the first real continuity update:
  - `C_i <- C_i - dt * sum_j J_ij`
  - continuity deltas are cached in:
    - `GRCV2State.cached_quantities["last_continuity_delta"]`
- Chosen budget-target policy:
  - `budget_target` is initialized from the first step abundance if still zero
  - later steps correct back to that explicit target
- Chosen budget-correction policy:
  - positive missing mass is added deterministically to the lowest live node ID
  - excess mass is removed deterministically from live nodes in ascending ID order
  - the remaining mismatch, if any, is stored in `remainder`
  - when the corrected mismatch is below `1e-12`, `remainder` is cleared to zero
- Chosen identity/observable refresh rule:
  - after continuity and budget enforcement, the model refreshes identity state once more
  - this keeps:
    - `sink_count`
    - `weighted_abundance`
    - basin-dependent observables
    aligned with the post-step topology/state rather than the pre-mutation graph
- Current observable surface now includes:
  - required:
    - `abundance`
    - `weighted_abundance`
    - `sink_count`
    - `budget_current`
    - `budget_error`
    - `num_nodes`
    - `num_edges`
  - recommended:
    - `spark_count`
    - `birth_count`
    - `prune_count`
    - `average_conductance`
- Added focused tests in:
  - `tests/models/test_grc_v2_budget_observables.py`

### Verification

- [x] Budget error is zero or within the explicitly accepted bounded remainder policy
- [x] Coherence remains non-negative after correction
- [x] Observables match the actual post-step graph/state

### Summary

Implemented the first real continuity/budget closure for `GRCV2`. The model now updates node coherence from flux divergence, corrects back to an explicit budget target with deterministic remainder handling, preserves non-negativity through correction, refreshes identity state after topology and coherence changes, and computes the required and recommended observables from the actual post-step graph/state.

## Iteration 8. Runtime Surface, Snapshot Integration, And Reset

### Goal

Finish the executable `GRCV2` runtime surface on top of the shared Phase 3 persistence layer.

### Checks

- [x] Implement `snapshot()` on the executable model with the v2-required groups/fields
- [x] Route `save(...)` through `save_snapshot(...)`
- [x] Route `load(...)` through `load_snapshot(...)`
- [x] Route substrate restoration through `restore_weighted_graph(...)`
- [x] Preserve `params_hash` as the serialized canonical identity marker
- [x] Route RNG persistence through:
  - `serialize_rng_state(...)`
  - `deserialize_rng_state(...)`
- [x] Implement `reset()` to restore the construction baseline deterministically

### Implementation Notes

- The executable model should not create a separate persistence path from the common serializer.
- Save/load must preserve IDs, counters, params identity, ordering, and resumable state.
- Snapshot shape must stay aligned with `specs/grc-v2-spec.md`.
- `src/pygrc/models/grc_v2.py` already had the shared persistence path wired in; this iteration tightened it for the executable runtime state.
- Chosen executable snapshot shape:
  - top-level groups remain:
    - `metadata`
    - `topology`
    - `dynamics`
    - `observables`
    - `events`
  - executable state continues to live under:
    - `dynamics["state"]`
- Runtime snapshot additions now preserved cleanly:
  - `split_registry`
  - `cached_quantities`
  - `event_log`
  - `observables`
  - `budget_target`
  - `remainder`
  - `params_identity`
- Snapshot event policy:
  - top-level `events` now mirrors the accumulated runtime `event_log`
  - the resumable state still preserves the same event history inside `dynamics["state"]`
- Fixed one executable persistence bug:
  - custom `GRCV2` state restore had been dropping `event_log`
  - the load/from-state path now restores accumulated events as real `GRCEvent` instances
- Fixed one executable snapshot bug:
  - runtime `cached_quantities` can contain non-string dict keys
  - the v2 state payload now stringifies cache-map keys recursively before JSON serialization
- Added focused tests in:
  - `tests/models/test_grc_v2_runtime_persistence.py`

### Verification

- [x] Save/load roundtrip preserves the ability to continue stepping deterministically
- [x] Snapshot groups/fields match the v2 spec and the common serializer contract
- [x] `reset()` restores the construction baseline deterministically

### Summary

Finished the executable `GRCV2` runtime surface on the shared Phase 3 persistence layer. Snapshots now expose the expected v2 groups, preserve executable state including event history and split progress, save/load resumes deterministic stepping without losing IDs or params identity, and `reset()` restores a nontrivial construction baseline exactly.

## Iteration 9. Deterministic Tests And Smoke Coverage

### Goal

Build the deterministic test and smoke suite for the first executable family.

### Checks

- [x] Add focused tests for:
  - parameter validation
  - invalid topology/state handling
  - one-step update behavior
  - sink/basin extraction
  - spark detection
  - split/birth behavior
  - prune/budget enforcement
  - save/load and replay
- [x] Cover the required common-interface error paths:
  - invalid topology
  - invalid parameter ranges
  - negative coherence after correction
  - unsupported capability requests
  - incompatible state deserialization
- [x] Add at least one end-to-end deterministic smoke scenario for the full v2 loop
- [x] Verify fixed seed + fixed params + fixed initial state produces repeatable step sequences

### Implementation Notes

- The default placement should stay aligned with the existing repo pattern:
  - `tests/models/test_grc_v2_*.py` for focused tests
  - `tests/models/` for larger deterministic scenarios when they remain unittest-shaped
  - repo-root smoke scripts only when the scenario is intentionally manual/operator-facing
- Tests should remain free of `GRCV3` and `GRC9` semantics.
- Added one focused validation matrix in:
  - `tests/models/test_grc_v2_validation_matrix.py`
  covering:
  - invalid parameter ranges
  - unsupported capability requests
  - incompatible state deserialization
  - multi-step save/load replay determinism
- Added one operator-facing end-to-end smoke script:
  - `tests/smoke/smoke_tests_phase4_grcv2.py`
- Added one paper-facing loop-validation smoke script:
  - `tests/smoke/smoke_tests_phase4_grcv2_paper_alignment.py`
- The Phase 4 smoke script currently checks:
  - repeatable multi-step records across equivalent builds
  - topology-event production in the executable loop
  - budget preservation across the loop
  - snapshot repeatability
  - digest repeatability
  - save/load resume determinism
  - monotone counter preservation across resume
  - reset-to-baseline behavior
- The paper-alignment smoke currently checks:
  - canonical 14-step ordering
  - Eq. (4) potential evaluation on a controlled graph
  - Eq. (5) flux sign and antisymmetry
  - sink/basin extraction from directed flux
  - spark to soft-split progression across multiple steps
  - birth, continuity, and budget closure in one executable loop
  - persistence/replay after nontrivial runtime evolution
- The paper-alignment smoke also exposed one real loop issue during implementation:
  - split progression could drive parent coherence negative on the next step
  - the deterministic budget-correction path was tightened to clip negative coherence first and rebalance afterward
- The focused test surface now spans:
  - construction/state validation
  - step skeleton
  - metric/label formulas
  - sink/basin semantics
  - spark backend/event payloads
  - split/birth/prune behavior
  - continuity/budget/observables
  - runtime persistence
  - validation/replay matrix

### Verification

- [x] The `GRCV2` baseline is covered by focused tests and at least one end-to-end smoke scenario
- [x] Replay/save/load tests prove deterministic persistence across actual model steps
- [x] Tests do not depend on third-party graph or persistence frameworks

### Summary

Built the deterministic validation layer for the executable `GRCV2` baseline. The focused tests now cover the full family surface from construction through replay, the explicit common-interface error paths are exercised directly, and the repo now has an end-to-end `GRCV2` smoke script that proves repeatable multi-step behavior, stable persistence, and reset correctness without relying on any external graph or persistence framework.

## Iteration 10. Validation Gate

### Goal

Validate the executable `GRCV2` baseline against the plan, the specs, and the earlier determinism/boundary documents, and use that validation to decide whether remediation is still required before closeout.

### Checks

- [x] Run the full test suite relevant to Phase 4
- [x] Run the end-to-end executable `GRCV2` smoke
- [x] Run the paper-facing `GRCV2` smoke
- [x] Verify `src/pygrc/models/grc_v2.py` is fully executable and no longer a stub
- [x] Verify the model uses `WeightedGraphBackend` and shared core contracts only
- [x] Verify the required 14-step semantics are represented explicitly in the implementation
- [x] Verify save/load/reset/from_state/set_state are all working on the executable model
- [x] Verify budget preservation and non-negativity invariants hold
- [x] Verify backend-derived serialization order remains deterministic
- [x] Verify stable integer IDs remain monotone and tombstoned-slot policy is preserved
- [x] Verify Phase 4 implementation notes do not contradict the `specs/` corpus at the executable-baseline level
- [x] Compare the executable baseline against `papers/2025-12-GRC-V2.md` and record constitutive blockers explicitly
- [x] Decide whether any remaining Phase 4 blockers require a dedicated remediation iteration before closeout

### Implementation Notes

- This gate is explicit, not implied by earlier passing tests.
- The main question at this gate is whether `GRCV2` is already trustworthy as the reference executable baseline for later family lift, or whether constitutive remediation is still required.
- If Phase 4 produces companion docs during implementation, they should also be checked here for consistency with the plan and specs.
- Detailed gate findings are recorded in:
  - [`Phase-4-ValidationGate.md`](./Phase-4-ValidationGate.md)
- Validation runs performed at this gate:
  - `./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
  - `./.venv/bin/python tests/smoke/smoke_tests_phase4_grcv2.py`
  - `./.venv/bin/python tests/smoke/smoke_tests_phase4_grcv2_paper_alignment.py`
- Observed gate results:
  - unit suite: `Ran 149 tests ... OK`
  - executable smoke: passed
  - paper-alignment smoke: passed
- The gate found a split/continuity stability issue during stronger smoke development:
  - split progression could drive parent coherence negative on the following step
  - `_enforce_budget(...)` was tightened so negative coherence is clipped first and mass is then rebalanced deterministically
- Gate conclusion:
  - executability, determinism, persistence, and shared-runtime alignment are strong enough to proceed
  - constitutive paper alignment is not yet strong enough to close Phase 4
- Confirmed constitutive blockers recorded by the gate:
  - paper Eq. (1) node tensor is not yet the true geometry object
  - paper Eq. (2) conductance law is still implemented as a surrogate baseline
  - `lambda_c`, `xi_c`, and `zeta_c` are not yet in their paper-defined roles
  - `abundance` semantics still differ from the paper
  - birth remains a constitutive deviation requiring an explicit retention-or-remediation decision
  - curvature backends remain acknowledged placeholders

### Verification

- [x] The validation gate itself is fully recorded and reproducible
- [x] The executable `GRCV2` baseline remains consistent with:
  - [x] `Phase-0-DeterminismConventions.md`
  - [x] `Phase-0-BoundaryDecisions.md`
  - [x] `specs/` corpus at the executable-baseline level
- [x] A clear gate decision is recorded:
  - [ ] close Phase 4 immediately
  - [x] continue into paper-alignment remediation
- [x] The gate distinguishes:
  - [x] what already passes strongly
  - [x] what remains a constitutive blocker
  - [x] what is still an accepted placeholder or explicit deviation candidate

### Summary

Completed the detailed Phase 4 validation gate. The executable `GRCV2` baseline now has strong evidence for determinism, persistence, shared-runtime alignment, explicit step ordering, and functional loop behavior, including end-to-end and paper-facing smoke coverage. The gate does not authorize closeout, however, because the constitutive paper core still has confirmed blockers around the Eq. (1) tensor path, the Eq. (2) conductance law, `lambda_c` / `xi_c` / `zeta_c` roles, abundance semantics, and the birth-rule deviation. Iteration 11 is therefore required before Phase 4 can close.

## Iteration 11. Paper-Alignment Remediation

### Goal

Remediate constitutive gaps between the executable `GRCV2` baseline and `papers/2025-12-GRC-V2.md`, and record any remaining deliberate deviations explicitly.

### Checks

- [x] Reconcile the node-tensor path against paper Eq. (1)
- [x] Reconcile the conductance law against paper Eq. (2)
- [x] Wire `lambda_c`, `xi_c`, and `zeta_c` into their paper-defined roles, or document the exact retained deviation
- [x] Reconcile `abundance` and `weighted_abundance` semantics against the paper
- [x] Decide whether birth remains a documented deterministic baseline deviation or is moved closer to the paper’s probabilistic rule
- [x] Revalidate the paper-facing smoke after constitutive changes
- [x] Record any remaining accepted deviations explicitly in the checklist and plan

### Implementation Notes

- This iteration exists because the validation gate identified constitutive paper-alignment gaps that are too important to leave implicit.
- The main concern is not mere executability; it is whether `GRCV2` is the correct reference baseline for later family lift work.
- Remediation work here should prefer:
  - correcting the implementation to the paper where feasible
  - over preserving an expedient surrogate that would become the wrong inherited baseline
- If a deviation is retained intentionally, it must be:
  - named,
  - justified,
  - narrow in scope,
  - and reflected in smoke/test expectations honestly
- Remediation completed in the executable family implementation:
  - `src/pygrc/models/grc_v2.py`
- Targeted paper-alignment tests were strengthened in:
  - `tests/models/test_grc_v2_metric_labels.py`
  - `tests/models/test_grc_v2_budget_observables.py`
  - `tests/models/test_grc_v2_topology_events.py`
  - `tests/models/test_grc_v2_runtime_persistence.py`
- Smoke expectations were updated in:
  - `tests/smoke/smoke_tests_phase4_grcv2.py`
  - `tests/smoke/smoke_tests_phase4_grcv2_paper_alignment.py`
- Remediated constitutive core:
  - `_compute_geometry(...)` now builds a paper-aligned three-term node-tensor bookkeeping object:
    - density term
    - gradient-pressure term
    - flux-feedback term
  - `_compute_metric(...)` now uses the paper-aligned exponential conductance law with:
    - mean coherence term
    - squared coherence-gap term
    - squared prior-flux term
    - edge-curvature term
  - `lambda_c`, `xi_c`, and `zeta_c` now participate in the tensor path rather than an ad hoc conductance surrogate
  - `compute_observables()` now uses the paper semantics:
    - `abundance = |S|`
    - `weighted_abundance = sum_s |B_s|^gamma`
  - `_apply_front_birth(...)` now follows the Bernoulli rule with:
    - explicit `birth_probability = 1 - exp(-lambda_birth * F_out)`
    - deterministic replay via `rng_seed` and serialized `rng_state`
  - `curvature_backend="forman"` and `curvature_backend="ollivier"` now resolve to real
    in-house weighted-substrate curvature implementations rather than placeholders
- Validation run after remediation:
  - `./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
  - `./.venv/bin/python tests/smoke/smoke_tests_phase4_grcv2.py`
  - `./.venv/bin/python tests/smoke/smoke_tests_phase4_grcv2_paper_alignment.py`
- Observed remediation results:
  - unit suite: `Ran 153 tests ... OK`
  - executable smoke: `9 passed, 0 failed`
  - paper-facing smoke: `24 passed, 0 failed`

### Verification

- [x] Paper-facing smoke passes on the remediated implementation
- [x] No unresolved birth-law or declared-curvature placeholders remain after remediation
- [x] The executable baseline is now acceptable for later family lift work

### Summary

Completed the paper-alignment remediation pass for `GRCV2`. The executable baseline now carries a paper-aligned node-tensor bookkeeping path, the paper-aligned exponential conductance law, correct `lambda_c` / `xi_c` / `zeta_c` roles, paper-aligned abundance semantics, Bernoulli front birth with deterministic replay via RNG seed/state, and real in-house `forman` / `ollivier` curvature backends. After remediation, the full unit suite, the executable smoke, and the paper-facing smoke all pass, so the family is ready for final Phase 4 closeout review.

## Iteration 12. Validation And Phase Closeout

### Goal

Close Phase 4 after the validation gate and any required paper-alignment remediation are complete.

### Checks

- [x] Run the full test suite relevant to Phase 4
- [x] Run the end-to-end `GRCV2` smoke coverage
- [x] Run the paper-facing `GRCV2` smoke coverage
- [x] Verify `src/pygrc/models/grc_v2.py` is fully executable and no longer a stub
- [x] Verify the model uses `WeightedGraphBackend` and shared core contracts only
- [x] Verify the required 14-step semantics are represented explicitly in the implementation
- [x] Verify save/load/reset/from_state/set_state are all working on the executable model
- [x] Verify budget preservation and non-negativity invariants hold
- [x] Verify backend-derived serialization order remains deterministic
- [x] Verify stable integer IDs remain monotone and tombstoned-slot policy is preserved
- [x] Verify Phase 4 implementation notes do not contradict the `specs/` corpus at the executable-baseline level
- [x] Verify no unresolved Phase 4 blockers remain for strict paper-equivalence closeout

### Implementation Notes

- Closeout should happen only after Iteration 11 is either completed or explicitly judged unnecessary.
- The final question is whether `GRCV2` is now trustworthy as the reference executable baseline for later family lift.
- Validation runs performed at closeout:
  - `./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
  - `./.venv/bin/python tests/smoke/smoke_tests_phase4_grcv2.py`
  - `./.venv/bin/python tests/smoke/smoke_tests_phase4_grcv2_paper_alignment.py`
- Observed closeout results:
  - unit suite: `Ran 153 tests ... OK`
  - executable smoke: `9 passed, 0 failed`
  - paper-facing smoke: `24 passed, 0 failed`
- Closeout findings:
  - structurally, the family is executable, deterministic, persistent, and aligned with the shared runtime/substrate contracts
  - the constitutive core now matches the paper on:
    - node-tensor bookkeeping structure
    - exponential conductance law
    - potential
    - flux
    - sink/basin extraction
    - abundance semantics
    - Bernoulli front birth with deterministic replay via `rng_seed` / `rng_state`
    - real in-house `forman` and `ollivier` curvature backends
- Closeout interpretation:
  - the implementation is acceptable as the deterministic executable reference baseline for later family lift work
  - no unresolved constitutive blocker remains from the earlier birth-law or curvature-backend gaps

### Verification

- [x] Phase 4 outputs satisfy the acceptance criteria in `Phase-4-ImplementationPlan.md`
- [x] The executable `GRCV2` baseline remains consistent with:
  - [x] `Phase-0-DeterminismConventions.md`
  - [x] `Phase-0-BoundaryDecisions.md`
  - [x] `specs/` corpus at the executable-baseline level
  - [x] `papers/2025-12-GRC-V2.md` at the level of the remediated constitutive baseline
- [x] No unresolved Phase 4 blockers remain for strict paper-equivalence closeout at the level targeted by Phase 4
- [x] No unresolved Phase 4 blockers remain for using `GRCV2` as the executable reference baseline

### Summary

Completed the final Phase 4 closeout audit. On the implementation, test, determinism, persistence, and shared-runtime fronts, `GRCV2` is in good shape: the full unit suite passes, both executable smoke layers pass, and the constitutive core has been remediated against the paper on the previously open blockers. Bernoulli front birth is now preserved with deterministic replay through explicit RNG seed/state, and the declared curvature backends are real in-house weighted-substrate implementations. Phase 4 therefore closes as the first executable family baseline with the paper-facing gaps from the validation gate resolved.
