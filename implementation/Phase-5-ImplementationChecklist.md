# Phase 5 Implementation Checklist

This document tracks the execution of **Phase 5: `GRCV3` Semantic Lift**.

It is intentionally separate from
[`Phase-5-ImplementationPlan.md`](./Phase-5-ImplementationPlan.md):

- the plan defines scope, workstreams, backend vocabulary, and acceptance
  criteria,
- this checklist records how Phase 5 will be executed iteration by iteration.

Companion document:

- [`Phase-5-EquationMap.md`](./Phase-5-EquationMap.md)
- [`GRCV3-Landscape-ProjectorProposal.md`](./GRCV3-Landscape-ProjectorProposal.md)
- [`Phase-5-LandscapeProjectorChecklist.md`](./Phase-5-LandscapeProjectorChecklist.md)

## Usage Rules

- Do not add `GRCV3` backend branches before the backend-selection contract is
  explicit.
- Keep theory-facing notes close to the iteration that introduces a formula or a
  constitutive choice.
- Record compromises as implementation notes rather than letting them hide
  behind passing tests.
- Keep shared semantics inherited from `GRCV2` explicit rather than silently
  redefining them.

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

Create the Phase 5 execution documents and lock the first public `GRCV3`
backend vocabulary before code changes begin.

### Checks

- [x] Create `Phase-5-ImplementationPlan.md`
- [x] Create `Phase-5-ImplementationChecklist.md`
- [x] Create `Phase-5-EquationMap.md`
- [x] Link the new Phase 5 docs from `ImplementationPhases.md`
- [x] Link the new Phase 5 docs from `Phase-5-Handoff.md`
- [x] Record the initial backend categories and public names:
  - `geometry`
  - `differential_summary`
  - `metric`
  - `curvature`
  - `spark`
  - `hierarchy_update`
  - `choice`

### Implementation Notes

- The backend vocabulary is a prerequisite for the rest of the phase.
- The baseline defaults must remain visible from the beginning:
  - `geometry = induced_local_frame`
  - `differential_summary = weighted_least_squares`
  - `metric = tensor_exponential`
  - `curvature = none`
  - `spark = signed_hessian_plus_attractor_delta`
  - `hierarchy_update = basin_parent_child`
  - `choice = disabled`

### Verification

- [x] The plan/checklist/equation-map trio exists under `implementation/`
- [x] The handoff and phase registry point to the new docs
- [x] The initial public names are consistent across all three docs

### Summary

Phase 5 documentation bootstrap is complete and the public backend vocabulary is
locked before implementation begins.

## Iteration 1. Common Backend Selection Surface

### Goal

Implement or extend the common backend-selection infrastructure that `GRCV3`
will use.

### Checks

- [x] Add or extend `src/pygrc/core/backends.py`
- [x] Define backend-selection datatypes
- [x] Define backend-category validation helpers
- [x] Decide how backend selections participate in canonical params identity
- [x] Decide how backend selections appear in snapshots

### Implementation Notes

- This iteration should change the common layer only as much as needed to make
  `GRCV3` selection explicit.
- Family formulas should not be implemented here.
- Implemented the common backend-selection surface in:
  - `src/pygrc/core/backends.py`
- Added the first shared primitives:
  - `BackendSelection`
  - `build_backend_selection(...)`
  - `build_backend_selection_payload(...)`
  - `restore_backend_selections(...)`
  - `validate_supported_backend_selections(...)`
- Added the first common backend-category vocabulary and exported it through
  `pygrc.core`.
- Chosen canonical params-identity rule:
  - families should include backend selections under the reserved key
    `backend_selections`
  - the canonical payload is a mapping keyed by category
  - because the payload is canonical JSON-safe, it participates in
    `GRCParams.resolved_config` hashing without any special-case digest path
- Chosen snapshot rule:
  - backend selections do not require a new top-level snapshot field
  - they should be serialized through canonical `params` / `resolved_params`
    payloads
  - backend-selection restoration is therefore compatible with the existing
    Phase 3 snapshot contract

### Verification

- [x] Unknown backend names fail early
- [x] Backend selections are deterministic and hash-stable
- [x] No family-specific formulas leak into `src/pygrc/core/`

Focused verification run:

- `./.venv/bin/python -m unittest tests.core.test_backends tests.core.test_params tests.core.test_canonical_serialization tests.core.test_module_imports tests.core.test_import_smoke`
- result:
  - `Ran 19 tests`
  - `OK`

### Summary

Completed the common backend-selection foundation. Phase 5 now has a shared
core representation for backend choices, a canonical payload shape that can be
embedded directly into params and snapshots, and validation helpers that keep
category/name checking out of family model code.

## Iteration 2. `GRCV3` State And Params Surface

### Goal

Create the public `GRCV3` dataclasses and resolved parameter surface.

### Checks

- [x] Add `BasinAttributes`
- [x] Add `GRCV3State`
- [x] Add `GRCV3` params resolution for:
  - thresholds
  - edge-label parameters
  - quadrature mode
  - backend selections
  - family modes still kept as config
- [x] Define the `GRCV3` capability profile

### Implementation Notes

- `GRCV3State` should be a real dataclass, not a loosely typed dict wrapper.
- `frame_mode`, `boundary_mode`, `split_distribution_mode`, and
  `edge_label_selection` remain explicit config surfaces even when backend
  selections are also present.
- Implemented new family-specific state datatypes in:
  - `src/pygrc/models/grc_v3_state.py`
- Replaced the old Phase 1 `GRCV3` stub with a real family surface in:
  - `src/pygrc/models/grc_v3.py`
- Added explicit state carriers for:
  - basin attributes
  - base conductance and analytic edge labels
  - hierarchy
  - choice / collapse registries
  - edge-label computation metadata
- Chosen baseline parameter defaults for the non-executable `GRCV3` surface:
  - `frame_mode = induced_local_frame`
  - `boundary_mode = prune`
  - `split_distribution_mode = equal`
  - `edge_label_selection = all`
  - `curvature_backend = none`
  - `budget_measure_mode = measure_absorbed`
  - backend selections under `backend_selections`:
    - `geometry = induced_local_frame`
    - `differential_summary = weighted_least_squares`
    - `metric = tensor_exponential`
    - `curvature = none`
    - `spark = signed_hessian_plus_attractor_delta`
    - `hierarchy_update = basin_parent_child`
    - `choice = disabled`
- Chosen Iteration 2 parameter-surface policy:
  - `GRCV3.from_config({"dt": ...})` is allowed and resolves the family baseline
    defaults automatically
  - host-embedding mode already validates `host_geometry_fields`
  - snapshot/load now use family-specific `basin_attributes` and `edge_labels`
    groups rather than hiding everything in the old stub-only shape
- Chosen state-vocabulary clarification:
  - `GRCV3` does **not** introduce a second `edges: dict[EdgeId, float]` field
    alongside `base_conductance`
  - this is deliberate rather than an omission
  - rationale:
    - `GRCV2` uses `edges` because there is one effective edge-weight concept in
      the baseline family
    - `GRCV3` explicitly separates:
      - `base_conductance`
      - `geometric_length`
      - `temporal_delay`
      - `flux_coupling`
    - once that separation exists, the generic name `edges` becomes ambiguous
      about which edge quantity is meant
    - therefore `base_conductance` is the authoritative runtime edge-weight
      field in `GRCV3`, matching the family spec directly
  - if later common-layer tooling needs a generic edge-value alias, that should
    be treated as a compatibility projection from `base_conductance`, not as a
    second independent family state field

### Verification

- [x] State fields match the `GRCV3` spec
- [x] Params resolve to explicit backend selections and explicit family modes
- [x] Capabilities reflect the actual selected implementation

Focused verification run:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_state tests.models.test_family_stubs tests.core.test_capabilities tests.core.test_module_imports`
- result:
  - `Ran 22 tests`
  - `OK`

### Summary

Completed the `GRCV3` state and parameter surface. The family now has real
dataclasses, baseline parameter resolution with explicit backend selections,
configuration-sensitive capability claims, and family-specific snapshot/load
behavior. Runtime semantics are still intentionally deferred to Iteration 3 and
later.

## Iteration 3. Geometry And Differential Summary Baseline

### Goal

Implement the first baseline for local frame, gradient, Hessian, and net-flux
summary construction.

### Checks

- [x] Implement `geometry = induced_local_frame`
- [x] Implement `differential_summary = weighted_least_squares`
- [x] Implement gradient summary materialization
- [x] Implement Hessian summary materialization
- [x] Implement net-flux summary materialization
- [x] Implement basin-mass summary materialization
- [x] Implement global Hessian sign calibration `s_H`

### Implementation Notes

- The sign convention must be fixed once per run and serialized.
- If any part of the first baseline is still a surrogate, record it here rather
  than using paper-final names without qualification.
- Implemented the Iteration 3 reference backend in:
  - `src/pygrc/models/grc_v3_differential.py`
- Added the first direct math helpers for:
  - canonical induced local frame displacements from a normalized weighted ego-graph Laplacian
  - weighted least-squares gradient
  - weighted least-squares Hessian
  - node-level net-flux summary
  - signed-Hessian calibration
- Chosen implementation strategy:
  - pure-Python small-matrix linear algebra
  - deterministic Jacobi eigensolver for symmetric local matrices
  - deterministic Gaussian-elimination solver for regression systems
  - no new numerical dependency introduced at this phase
- Integrated the backend into `GRCV3` through:
  - `rebuild_basin_attributes()`
  - `_coherence_by_node()`
  - `_base_conductance_by_edge()`
  - `_neighbor_weights()`
  - `_basin_mass_for_node()`
- Chosen Iteration 3 baseline defaults:
  - induced local frame dimension:
    - `2`
  - gradient regularization:
    - `1e-9`
  - Hessian regularization:
    - `1e-9`
- Chosen sign-calibration policy for the current baseline:
  - prefer `sink_set` as candidate basin seeds when available
  - otherwise fall back deterministically to all live nodes
  - keep the chosen sign in `state.cached_quantities["hessian_sign"]` so later
    iterations can serialize it as authoritative run metadata
- Theory-facing Hessian note:
  - the implementation does **not** use the literal raw weighted-moment form of
    paper Eq. (3) as the executable backend
  - instead it uses the reference backend from `specs/grc-v3-spec.md`
    Appendix A.3:
    - subtract the fitted linear term
    - fit the quadratic residual by weighted least squares
    - reconstruct the symmetric Hessian from that fit
  - this is a constitutive numerical refinement for stability and curvature
    isolation and must remain documented as such
- Current limitation:
  - the differential backend is implemented and materializes state, but the full
    `GRCV3.step()` still remains intentionally unimplemented until later
    iterations reconnect it to metric, identity, and event logic

### Verification

- [x] Direct tests exist for gradient output
- [x] Direct tests exist for Hessian output
- [x] Direct tests exist for Hessian sign handling
- [x] Differential summaries are visible in public state

Focused verification run:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_differential tests.models.test_grc_v3_state tests.models.test_family_stubs tests.core.test_capabilities tests.core.test_module_imports`
- result:
  - `Ran 28 tests`
  - `OK`

### Summary

Completed the first real `GRCV3` mathematics slice. The family now has a
reference induced-local-frame backend, weighted least-squares gradient/Hessian
materialization, node-level flux/basin summaries, and deterministic Hessian-sign
calibration, all wired into a model-level `rebuild_basin_attributes()` path and
covered by direct tests.

## Iteration 4. Metric, Labels, Potential, And Flux

### Goal

Reconnect basin attributes to the reflexive update loop.

### Checks

- [x] Implement node tensor construction from basin attributes
- [x] Implement `metric = tensor_exponential`
- [x] Implement `base_conductance`
- [x] Implement `geometric_length`
- [x] Implement `temporal_delay`
- [x] Implement `flux_coupling`
- [x] Implement potential update
- [x] Implement flux update
- [x] Implement edge-label computation mode metadata

### Implementation Notes

- `base_conductance` remains the sole dynamical edge weight.
- Analytic labels must stay separate in state and serialization.
- `GRCV3` now carries the inherited `site_potential_selection` and
  `site_potential_params` surface from `GRCV2`; the baseline defaults are
  `quadratic` with `{mu: 0.0, scale: 1.0}`.
- Iteration 4 introduced `rebuild_transport_state()` as the model-level helper
  that materializes the transport slice without claiming a full `step()` loop
  yet. Its order is:
  - node tensors
  - base conductance
  - pre-flux labels
  - potential
  - flux
  - post-flux labels
- Node tensors are stored in `cached_quantities["node_tensors"]` as explicit
  dense matrices derived from the basin-attribute bundle:
  - `lambda_c * C_i * I`
  - `xi_c * g_i ⊗ g_i`
  - `zeta_c * J_i^net ⊗ J_i^net`
- `metric = tensor_exponential` now implements the paper form:
  - `exp[-alpha*(Ci+Cj)/2 - beta*||gi-gj||^2/2 - gamma*Jij^2/2 - delta*Ricci_ij]`
- Curvature backend handling is now available on the `GRCV3` transport path:
  - `none`
  - `forman`
  - `ollivier`
  using the same reference surrogate strategy already established for the shared
  graph runtime.
- Geometric-length computation modes are now explicit and serialized:
  - `ambient_metric` when host geometry is complete for the whole selected run
  - `induced_intrinsic` for intrinsic local-frame geometry
  - `intrinsic_surrogate` when strong geometry is unavailable
- Host-embedding geometric length prefers edge-level `ambient_length`, then
  falls back to distances derived from host-declared node coordinate fields.
- `temporal_delay` uses the canonical transport-ratio law and records the
  geometric-length mode it depends on.
- `cached_quantities` is now normalized to a JSON-safe shape during snapshot
  emission so materialized tensor caches do not break canonical serialization.

### Verification

- [x] Flux remains antisymmetric
- [x] Edge labels are stable under save/load
- [x] Label availability / surrogate metadata is present when needed

- verification command:
- `./.venv/bin/python -m unittest tests.models.test_grc_v3_metric_labels tests.models.test_grc_v3_state tests.models.test_grc_v3_differential tests.models.test_family_stubs tests.core.test_module_imports`
- result:
  - `Ran 25 tests`
  - `OK`

### Summary

Completed the first real `GRCV3` transport slice. The family now materializes
node tensors, tensor-exponential base conductance, analytic edge labels, node
potential, and antisymmetric flux using the basin-attribute state rather than
the old scalar-only v2 proxies. The label-availability contract is now explicit
in runtime metadata, host geometry can fall back deterministically to intrinsic
surrogates, and the full transport state survives snapshot/save/load without
losing reproducibility.

## Iteration 5. Identity Layers And Hierarchy

### Goal

Implement both the flux-topology and geometric identity layers, plus
deterministic hierarchy updates.

### Checks

- [x] Implement sink-set extraction
- [x] Implement attraction basins
- [x] Implement basin validation from gradient / Hessian summaries
- [x] Implement `hierarchy_update = basin_parent_child`
- [x] Materialize `basin_id`, `parent_id`, and `depth`
- [x] Serialize hierarchy state

### Implementation Notes

- The two identity layers must remain inspectable rather than being merged into
  one opaque label assignment.
- If the implementation requires agreement or staged validation between them,
  record that explicitly.
- Chosen Iteration 5 baseline policy:
  - keep the two identity layers separate and queryable
  - use the flux-topology layer to compute:
    - `state.sink_set`
    - `state.basins`
    - `cached_quantities["flux_identity"]`
  - use the geometric layer to compute:
    - `cached_quantities["geometric_identity"]["seed_nodes"]`
    - signed-Hessian diagnostics
    - validated basin assignments
- Chosen validation rule:
  - build flux attraction basins first
  - detect geometric seeds by the tightened Appendix B.2 criterion
  - if a flux basin contains exactly one geometric seed, that seed becomes the
    validated `basin_id` for all members of the basin
  - otherwise the implementation falls back deterministically to the flux sink
    as the basin identifier
- `rebuild_identity_state()` is now the model-level helper for the Iteration 5
  slice. It performs:
  - sink extraction
  - attraction-basin routing
  - geometric seed validation from gradient / signed Hessian summaries
  - deterministic hierarchy refresh
- `hierarchy_update = basin_parent_child` currently preserves existing
  `parent_id` and `depth` assignments while refreshing:
  - `basin_id`
  - `basin_mass`
  - `state.hierarchy`
- External parent identifiers that are not themselves live basin nodes are now
  preserved as hierarchy roots rather than being dropped during serialization or
  refresh.
- Hierarchy restoration now converts int-like serialized identifiers back to
  integers so save/load preserves mixed string/int basin identifiers exactly.

### Verification

- [x] Both identity layers are queryable from state or events
- [x] Parent/depth updates are deterministic
- [x] Save/load preserves hierarchy fields exactly

- verification command:
- `./.venv/bin/python -m unittest tests.models.test_grc_v3_hierarchy tests.models.test_grc_v3_state tests.models.test_grc_v3_metric_labels tests.models.test_grc_v3_differential tests.models.test_family_stubs tests.core.test_module_imports`
- result:
  - `Ran 28 tests`
  - `OK`

### Summary

Completed the first real `GRCV3` identity slice. The model now exposes both
identity layers explicitly: flux-topology sinks/basins and geometric
gradient/Hessian seed validation. Basin identifiers are assigned by a recorded
staged policy rather than ad hoc inference, hierarchy refresh is deterministic,
and save/load preserves the hierarchy and mixed identifier types without
silently coercing them.

## Iteration 6. Spark Completion And Split Integration

### Goal

Implement the direct `GRCV3` spark path and its interaction with split logic.

### Checks

- [x] Implement `spark = signed_hessian_plus_attractor_delta`
- [x] Detect spark candidates from signed-Hessian degeneracy
- [x] Confirm completed sparks through attractor-count change
- [x] Integrate soft split with child basin initialization
- [x] Ensure child basins inherit ancestry and depth updates correctly

### Implementation Notes

- Degeneracy alone is not enough for completed spark registration.
- This iteration should make the difference between spark candidate and
  completed spark explicit in code and tests.
- Chosen Iteration 6 model surface:
  - `detect_spark_candidates()`
  - `apply_spark_candidates(...)`
  - `advance_split_state()`
  - `rebuild_spark_state()`
  - `_refresh_after_topology_change()`
  - `_evaluate_split_completion()`
- The backend now distinguishes explicitly between:
  - `spark_candidate`
  - `split_init`
  - `spark_pending`
  - `spark`
  - `split_progress`
  - `split_complete`
- Candidate rule for the current baseline:
  - use the signed-Hessian Appendix B.3 criterion
  - require the node to be a current basin interior in the practical discrete
    sense:
    - either a geometric seed from Iteration 5
    - or the current basin representative (`basin_id == node_id`)
  - skip nodes already owned by an active split
- Completed-spark rule for the current baseline:
  - initialize the soft split first
  - refresh local transport and identity state on the modified graph
  - compare pre/post attractor metrics
  - register `spark` only when one of the following holds:
    - validated geometric basin count increases by at least
      `spark.params.min_child_basins`
    - sink count increases by at least one
  - otherwise register `spark_pending`
  - re-evaluate the same completion rule on later `advance_split_state()` calls
    until the split is confirmed or completed structurally
- Child-basin initialization now:
  - splits coherence equally under the current `equal` rule
  - assigns fresh child basin IDs from the new node IDs
  - sets `parent_id` to the parent basin ID
  - increments `depth`
  - stabilizes the weakest curvature direction so the child basins can become
    valid post-split basin charts
  - zeros inherited off-diagonal Hessian terms instead of copying them blindly
- Soft split progression reuses the v2-style deterministic registry idea, but
  stores split state in `cached_quantities["split_registry"]` rather than
  introducing a new family-owned state field before it is justified by the
  formal `GRCV3` surface.
- Split conductance accounting was tightened after theory review:
  - parent-neighbor external edges now decay toward zero while child-neighbor
    edges grow toward their split targets
  - this preserves the external coupling budget of the split region instead of
    inflating it during overlap
  - the parent-child split links remain explicit new internal refinement edges
- Post-topology refresh policy was tightened after theory review:
  - split init / progress now recompute:
    - potential
    - flux
    - basin attributes
    - node tensors
    - analytic edge labels
    - identity / hierarchy state
  - this refresh intentionally preserves the currently interpolated
    `base_conductance` values instead of rerunning the full metric law, because
    split interpolation is itself part of the active constitutive state during
    soft refinement
- Iteration 6 also extended the geometric identity baseline so standalone
  geometric seed nodes become singleton validated basins when they are not part
  of any current flux basin. This is necessary for explicit post-split child
  basin representation in the pre-step-loop phase.

### Verification

- [x] Transient flattening does not register as a completed spark
- [x] Post-split child basins are represented explicitly
- [x] Event ordering remains deterministic

- verification command:
- `./.venv/bin/python -m unittest tests.models.test_grc_v3_sparks tests.models.test_grc_v3_hierarchy tests.models.test_grc_v3_state tests.models.test_grc_v3_metric_labels tests.models.test_grc_v3_differential tests.models.test_family_stubs tests.core.test_module_imports`
- result:
  - `Ran 31 tests`
  - `OK`

### Summary

Completed the first direct `GRCV3` spark/event path. The code now separates
curvature-side spark candidacy from completed spark registration, initializes
soft splits with explicit child basin ancestry, and advances split state
deterministically until parent removal. Child basins are represented explicitly
before the full `step()` loop exists, and the event log now captures the
difference between a local degeneracy, a pending split, and a completed
attractor-count change.

## Iteration 7. Choice, Collapse, And Learning Layer

### Goal

Implement the optional event layer for choice / collapse / learning.

### Checks

- [x] Add `choice = disabled`
- [x] Add `choice = sink_compatibility`
- [x] Implement compatibility scoring surface
- [x] Emit `choice_detected` events when multiple continuations remain viable
- [x] Emit `collapse` events when one continuation dominates
- [x] Record persistent post-collapse deformation bookkeeping if enabled

### Implementation Notes

- If the first implementation only supports disabled mode plus one baseline
  compatibility backend, keep the surface narrow and explicit.
- Do not add observer-limited epistemic semantics here unless they are truly
  part of the family dynamics.
- Recorded edge semantics for the baseline backend:
  - `epsilon_choice = 0` means only exact best-score ties remain jointly viable
    as a choice regime
  - `epsilon_collapse = 0` means any positive winner margin collapses a
    previously ambiguous node
  - when ambiguity disappears without reaching collapse threshold, emit
    `choice_resolved` rather than silently dropping the node from choice state

### Verification

- [x] Disabled mode leaves no partial choice state behind
- [x] Enabled mode emits deterministic event sequences under fixed replay inputs
- [x] Choice / collapse semantics are documented in tests rather than implied

### Summary

Implemented the first `GRCV3` choice/collapse backend without widening the
surface beyond the planned baseline. `choice=disabled` now actively clears
choice/collapse state, while `choice=sink_compatibility` evaluates positive
outgoing flux by reachable sink, emits `choice_detected` when multiple sinks
remain viable within `epsilon_choice`, emits `collapse` when a previously
ambiguous node resolves to one dominant sink by `epsilon_collapse`, and emits
`choice_resolved` when ambiguity disappears without meeting the collapse
threshold. The strict edge semantics of `epsilon_choice = 0` and
`epsilon_collapse = 0` are now recorded explicitly rather than left implicit in
the code. Persistent post-collapse bookkeeping is recorded in
`collapse_registry` with an explicit `persistence_mode="registry_only"` marker
so later learning semantics can build on a visible baseline rather than hidden
state.

Verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_choice`

## Iteration 8. Serialization, Replay, And Snapshot Contracts

### Goal

Make the richer family reproducible and loadable.

### Checks

- [x] Define `GRCV3` snapshot payload structure
- [x] Serialize backend selections and backend params
- [x] Serialize `hessian_sign`
- [x] Serialize hierarchy and choice/collapse state
- [x] Implement `from_state`, `snapshot`, `save`, and `load`
- [x] Add save/load roundtrip tests

### Implementation Notes

- This iteration should not invent a parallel persistence layer.
- Reuse the common serializer/digest infrastructure from Phases 1 through 3.

### Verification

- [x] Roundtrip restore preserves `GRCV3` semantics
- [x] Backend selections survive load without ambiguity
- [x] Snapshot identity remains deterministic

### Summary

Closed the reproducibility path for the richer family without adding a second
persistence stack. `GRCV3` now restores serialized `event_log` and `rng_state`
instead of dropping them or leaving RNG payloads in encoded form, and `load()`
falls back to top-level snapshot events when the dynamics-state copy is absent.
Backend selections remain round-trippable through resolved params, `hessian_sign`
is preserved in snapshot metadata, and hierarchy plus choice/collapse state stay
intact across save/load. Digest-level replay identity is now covered directly in
tests rather than inferred from group presence alone.

Verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_serialization`

## Iteration 9. Theory-Facing Test Surface

### Goal

Lock the direct mathematical and semantic checks before larger experiments or
optimization work begin.

### Checks

- [x] Add direct tests for gradient formulas
- [x] Add direct tests for Hessian formulas
- [x] Add direct tests for signed-Hessian basin criteria
- [x] Add direct tests for spark completion semantics
- [x] Add direct tests for hierarchy updates
- [x] Add direct tests for choice / collapse event meaning

### Implementation Notes

- This iteration is specifically about tests that can fail even when a more
  implementation-shaped smoke still passes.

### Verification

- [x] The test suite distinguishes theory mismatch from runtime regression
- [x] Core formulas are covered without going through only end-to-end smokes
- [x] The direct tests are readable enough to serve as paper-to-code evidence

### Summary

Locked the direct evidence layer before larger experiments. The Phase 5 test
surface now separates theory-facing checks from serialization or runtime smoke:
`test_grc_v3_differential.py` covers the baseline gradient and Hessian formulas,
`test_grc_v3_hierarchy.py` and `test_grc_v3_choice.py` cover hierarchy and
choice/collapse semantics directly, and `test_grc_v3_step.py` now adds explicit
tests for the signed-Hessian basin criterion and spark completion as an
attractor-gain rule. The result is a readable paper-to-code audit surface that
can fail on semantic drift even when broader runtime-shaped tests still pass.

Verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_differential tests.models.test_grc_v3_hierarchy tests.models.test_grc_v3_choice tests.models.test_grc_v3_sparks tests.models.test_grc_v3_step`

## Iteration 10. Mid-Phase Constitutive Validation Gate

### Goal

Pause and review the baseline against the paper before declaring the family
substantially complete.

### Checks

- [x] Compare implemented gradient/Hessian semantics against the source paper
- [x] Verify `s_H` handling against the signed-Hessian appendix
- [x] Verify spark completion logic against the attractor-count requirement
- [x] Verify hierarchy semantics against the basin-attribute contract
- [x] Verify backend names do not overclaim implementation completeness
- [x] Record any remaining constitutive gaps explicitly

### Implementation Notes

- This iteration should produce a review outcome, not more hidden technical
  debt.

### Verification

- [x] No known mismatch remains only in conversation history
- [x] Any open compromises are recorded in the checklist or a dedicated note
- [x] The family can proceed to representative execution without semantic doubt

### Summary

Completed via [Phase-5-ConstitutiveReview.md](./Phase-5-ConstitutiveReview.md).
The baseline is now semantically pinned down before runtime integration:

- differential summaries are paper-facing through the spec Appendix A.3
  weighted least-squares backend rather than a literal Eq. (3) raw-moment
  transcription
- `hessian_sign` is calibrated once, serialized, and treated as run-fixed
- spark completion is confirmed only by attractor gain, not by local
  degeneracy alone
- hierarchy is explicitly basin-id keyed parent/child structure
- `sink_compatibility` is retained as the flux-routed baseline choice backend
  and `registry_only` learning remains an explicit deferred limit

No hidden constitutive ambiguity remains in conversation-only form. Iteration
11 can focus on runtime closure rather than semantics recovery.

## Iteration 11. Representative Runtime And Artifact Check

### Goal

Run the first representative `GRCV3` lane with enough evidence to support
future family work.

### Checks

- [x] Define the first representative `GRCV3` runtime lane
- [x] Run deterministic smokes for the initial lane
- [x] Record telemetry / snapshot evidence requirements
- [x] Verify save/load and replay on representative runs
- [x] Decide whether the Phase 5 closeout requires a dedicated reconstruction script

### Implementation Notes

- This iteration should remain evidence-oriented.
- Phase 5 does not need a fully developed experiment program before closeout,
  but it does need enough runtime evidence that the family is more than a unit
  test artifact.

### Verification

- [x] Representative `GRCV3` runs step deterministically under fixed inputs
- [x] Artifact generation remains reproducible
- [x] The family is ready to support later `GRC9V3` hybridization work

### Summary

Completed with a real baseline runtime lane and evidence bundle.

What landed:

- `GRCV3.step()` now executes the baseline semantic loop instead of raising
  `NotImplementedError`
- continuity and exact-budget correction are now implemented for basin-attribute
  node state
- the exact Phase 5 reference runtime order is now recorded in
  [Phase-5-StepLoop.md](./Phase-5-StepLoop.md)
- a representative deterministic lane is documented in
  [Phase-5-RepresentativeRuntime.md](./Phase-5-RepresentativeRuntime.md)
- runtime/replay coverage now exists in
  [tests/models/test_grc_v3_runtime.py](../tests/models/test_grc_v3_runtime.py)
- a dedicated reconstruction script now exists at
  [scripts/run_grcv3_representative_smoke.py](../scripts/run_grcv3_representative_smoke.py)

Verification performed:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_runtime tests.models.test_grc_v3_state tests.models.test_grc_v3_differential tests.models.test_grc_v3_metric_labels tests.models.test_grc_v3_hierarchy tests.models.test_grc_v3_sparks tests.models.test_grc_v3_choice tests.models.test_grc_v3_step tests.models.test_grc_v3_serialization`
- `./.venv/bin/python scripts/run_grcv3_representative_smoke.py --experiment-id phase5-grcv3-smoke-check --steps 3`

The runtime seed is intentionally conservative:

- intrinsic three-node chain
- `choice = disabled`
- spark effectively suppressed for the smoke
- save/load replay verified from an intermediate snapshot

That seed simplicity does not imply a reduced loop. The run uses the full Phase
5 reference step order and is enough to treat `GRCV3` as an executable baseline
family and to move Phase 5 toward closeout.

## Iteration 12. Phase Closeout

### Goal

Close Phase 5 only when `GRCV3` is a real semantic reference family rather than
an unfinished scaffold.

### Checks

- [x] Verify no unresolved Phase 5 blockers remain for the baseline family
- [x] Write a closeout note or handoff update summarizing what `GRCV3` now guarantees
- [x] Link the closeout from the next-phase handoff
- [x] Record non-blocking future work separately from baseline blockers

### Implementation Notes

- Closeout should be evidence-based, not aspirational.

### Verification

- [x] The family is operational, reproducible, and semantically explicit
- [x] Later phases can inherit `GRCV3` rather than reopening it casually

### Summary

Completed via [GRCV3-Closeout.md](./GRCV3-Closeout.md).

Closeout evidence used:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_runtime tests.models.test_grc_v3_state tests.models.test_grc_v3_differential tests.models.test_grc_v3_metric_labels tests.models.test_grc_v3_hierarchy tests.models.test_grc_v3_sparks tests.models.test_grc_v3_choice tests.models.test_grc_v3_step tests.models.test_grc_v3_serialization`
  - result: `Ran 38 tests ... OK`
- `./.venv/bin/python scripts/run_grcv3_representative_smoke.py --experiment-id phase5-grcv3-closeout --steps 3`
  - digest:
    `09364e2b22779d26185666d767a3dc54e512992301bc5a4f9ad53efc45594dd9`

Phase 5 now closes with:

- executable `GRCV3.step()` runtime semantics
- deterministic signed-Hessian handling
- explicit hierarchy and choice/collapse state
- deterministic persistence and replay
- a written baseline boundary separating guarantees from future comparative work

Future phases should inherit `GRCV3` from the closeout documents rather than
reopening its baseline semantics casually.

## Iteration 13. Landscape Projector Follow-On Bootstrap

### Goal

Track the seed-driven `GRCV3` projector revision explicitly as a Phase 5
follow-on rather than leaving it as an orphan proposal.

### Checks

- [x] Create `Phase-5-LandscapeProjectorChecklist.md`
- [x] Link the projector proposal and checklist from the Phase 5 plan
- [x] Link the projector proposal and checklist from `ImplementationPhases.md`
- [x] Record that this follow-on keeps runtime equations fixed first and works
  only through the family-local projector boundary

### Implementation Notes

- This iteration does not reopen the baseline Phase 5 runtime closeout.
- It creates the explicit execution surface for the next seed-driven `GRCV3`
  corrective step:
  - richer basin motifs
  - richer valley/channel realization
  - richer routing junction realization
  - exact motif-level budget partition

### Verification

- [x] The projector follow-on is no longer conversation-only
- [x] The main phase registry shows that seed-driven `GRCV3` still has an open
  family-local projector lane

### Summary

Completed. The GRCV3 landscape-projector revision is now tracked explicitly as
a Phase 5 follow-on through
[GRCV3-Landscape-ProjectorProposal.md](./GRCV3-Landscape-ProjectorProposal.md)
and
[Phase-5-LandscapeProjectorChecklist.md](./Phase-5-LandscapeProjectorChecklist.md),
with the boundary and execution order linked from both the Phase 5 plan and the
top-level implementation registry.
