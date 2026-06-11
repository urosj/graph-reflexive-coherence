# Phase T GRC9 Implementation Checklist

This document tracks execution of **Phase T-GRC9: GRC9 Mechanical Telemetry
Extension**.

It is intentionally separate from
[`Phase-T-GRC9-ImplementationPlan.md`](./Phase-T-GRC9-ImplementationPlan.md):

- the plan defines scope, phenomenology targets, workstreams, and acceptance
  criteria,
- this checklist records how the paper-facing GRC9 telemetry work is executed
  iteration by iteration.

## Usage Rules

- Keep Phase 6 closed. This phase expands telemetry, not the core Phase 6
  runtime claim.
- Start from the GRC9 paper phenomena, not only from existing easy-to-export
  implementation fields.
- Preserve the shared Phase T telemetry architecture:
  - common rows stay common,
  - GRC9-specific data goes under `family_extensions["grc9"]`,
  - graph checkpoints remain optional and explicit,
  - `GRC9.step()` remains telemetry-agnostic.
- Keep rows and columns distinct in every telemetry payload:
  - rows are local directional geometry,
  - columns are interface families, spark diagnostics, rewiring, and scale.
- Do not promote `GRC9V3`, `GRCL-9`, Lorentzian, FRC sigma, or observer-local
  semantics into core `GRC9` telemetry claims.
- Mark unavailable theory-facing fields explicitly as:
  - implemented and artifact-backed,
  - diagnostic-only,
  - reserved/future,
  - or out of scope.
- Use typed contract dataclasses and focused tests before wiring richer
  payloads into experiment lanes.
- Preserve the historical meaning of the Phase 6 `phase6_iter10_v1` GRC9
  telemetry artifacts. New extended artifacts should use a new contract version
  and new lane/profile names.

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

Create the Phase T-GRC9 execution plan and checklist, and lock the phase
boundary as telemetry expansion rather than Phase 6 runtime expansion.

### Checks

- [x] Create `Phase-T-GRC9-ImplementationPlan.md`
- [x] Create `Phase-T-GRC9-ImplementationChecklist.md`
- [x] Record that Phase 6 remains closed
- [x] Record that this phase is paper-facing telemetry for GRC9-specific
  mechanics
- [x] Include the GRC9 paper phenomena, not just current implementation fields
- [x] Include explicit future boundaries for:
  - `GRC9V3`
  - `GRCL-9`
  - Lorentzian causal layer
  - FRC sigma field
  - observer-local unpredictability
- [x] Record the relationship to existing Phase 6 GRC9 telemetry
- [x] Record the current telemetry code structure and migration strategy

### Implementation Notes

- Phase T-GRC9 begins because the compact Phase 6 telemetry contract was
  sufficient for closeout but not sufficient for GRC9-specific phenomenology.
- The plan explicitly names signals from `papers/2026-04-GRC-9.md`, including:
  - 3x3 port chart state
  - row tensor diagnostics
  - column diagnostics
  - spark calibration
  - expansion module details
  - effective degree policy
  - bond initialization
  - growth birth probability
  - coarse-grain / Split integrity
  - scale-weighted abundance
  - identity fission persistence
- The first implementation slice is intentionally contract-first.
- The Phase 6 telemetry contract remains historical:
  - `phase6_iter10_v1`
- Phase T-GRC9 starts a new extended contract:
  - `phase_t_grc9_iter1_v1`
- The shared recorder already supports per-step, per-event, and summary family
  extensions, so the migration should mostly add typed GRC9 builders rather
  than change the common telemetry schema.

### Verification

- [x] The plan/checklist pair exists under `implementation/`
- [x] The plan states that Phase 6 should not be reopened for telemetry
- [x] The plan records theory-facing targets and explicit out-of-scope
  semantics
- [x] The plan explains how the new contract relates to
  `Phase-6-GRC9-RepresentativeTelemetry.md`

### Summary

Phase T-GRC9 now has a dedicated plan and checklist. The work is scoped as a
GRC9-specific telemetry extension layered on the existing shared telemetry
architecture, not as a Phase 6 runtime expansion.

## Iteration 1. Telemetry Contract Document

### Goal

Write the explicit GRC9 telemetry contract before implementation begins.

### Checks

- [x] Create `Phase-T-GRC9-TelemetryContract.md`
- [x] Set the first contract version:
  - `phase_t_grc9_iter1_v1`
- [x] Define the family key:
  - `grc9`
- [x] State that `phase6_iter10_v1` remains the compact historical Phase 6
  closeout contract
- [x] State that `phase_t_grc9_iter1_v1` is the extended Phase T-GRC9 contract
- [x] Record required step-row extension groups:
  - backend/config summary
  - port chart summary
  - row tensor summary
  - column diagnostic summary
  - transport summary
  - identity/abundance summary
  - coarse-graining summary
  - budget correction summary
- [x] Record required event-row extension groups:
  - event taxonomy
  - spark trigger evidence
  - expansion module evidence
  - growth evidence
  - budget correction evidence
- [x] Record required run-summary extension groups:
  - lifecycle counts
  - final mechanical summaries
  - expansion/growth summaries
  - identity fission summaries
  - calibration summaries when applicable
- [x] Record optional graph-checkpoint extension groups:
  - node overlays
  - port overlays
  - edge overlays
  - module overlays
- [x] Record migration from current ad hoc GRC9 dict payloads in
  `experiments.py` to typed contract builders

### Implementation Notes

- The contract document should be the source of truth for field names before
  `grc9_contract.py` is added.
- The contract document should explicitly reference the Phase 6 contract and
  explain which fields are retained, replaced, or expanded.
- Any paper-facing field that cannot yet be computed must be labeled explicitly
  rather than omitted silently.
- The contract should distinguish:
  - configured policy,
  - actual per-step path,
  - and event-local evidence.
- Implemented the contract document in:
  - `implementation/Phase-T-GRC9-TelemetryContract.md`
- Chosen Iteration 1 contract identity:
  - family key: `grc9`
  - version: `phase_t_grc9_iter1_v1`
- Preserved historical Phase 6 interpretation:
  - `phase6_iter10_v1` remains the compact closeout contract
  - Phase 6 artifacts should not be retroactively interpreted as extended
    Phase T-GRC9 artifacts
- Chosen payload structure:
  - step rows use typed groups for lane context, backend/config, port chart,
    row tensor, column diagnostics, transport, identity/abundance,
    coarse-graining, and budget correction
  - event rows use a stable domain/stage taxonomy plus evidence groups for
    spark, expansion, growth, and budget events
  - run summaries use fixed lifecycle counts plus final mechanical summaries,
    expansion/growth summaries, identity fission, and optional calibration
  - graph checkpoints remain optional and carry node/port/edge/module overlays
- Chosen migration strategy:
  - leave `capture_run_telemetry(...)` as the shared recorder
  - move GRC9 contract constants and validation into `grc9_contract.py`
  - add optional private builders in `_grc9_extensions.py`
  - pass richer payloads through existing recorder extension hooks

### Verification

- [x] Contract maps each major plan surface to concrete field names
- [x] Contract preserves row/column distinction
- [x] Contract does not claim `GRC9V3` or `GRCL-9` semantics
- [x] Contract keeps Phase 6 artifact interpretation stable

### Summary

Completed the explicit Phase T-GRC9 telemetry contract document. The phase now
has a concrete extended contract version, payload structure, graph-checkpoint
shape, and migration rule from the current compact Phase 6 dictionary payloads
to typed GRC9 contract builders.

## Iteration 2. Typed Contract Module

### Goal

Implement the typed GRC9 telemetry extension contract and focused tests.

### Checks

- [x] Add `src/pygrc/telemetry/grc9_contract.py`
- [x] Export the public contract through `src/pygrc/telemetry/__init__.py`
- [x] Add `tests/telemetry/test_grc9_contract.py`
- [x] Define contract constants:
  - `GRC9_TELEMETRY_FAMILY`
  - `GRC9_TELEMETRY_CONTRACT_VERSION`
- [x] Define step extension dataclasses for:
  - backend/config summary
  - port chart summary
  - row tensor summary
  - column diagnostic summary
  - transport summary
  - identity summary
  - coarse-graining summary
  - budget correction summary
- [x] Define event extension dataclasses and classifier
- [x] Define lifecycle event count dataclass
- [x] Define run-summary extension dataclass
- [x] Implement wrapper helpers:
  - `grc9_step_family_extensions(...)`
  - `grc9_event_family_extensions(...)`
  - `grc9_run_summary_family_extensions(...)`
  - `classify_grc9_event_extension(...)`

### Implementation Notes

- Follow the GRCV3 contract-module pattern where it fits, but do not copy
  GRCV3 semantics into GRC9.
- Validation should catch:
  - negative counts,
  - non-finite floats,
  - invalid enum-like values,
  - malformed row/column totals,
  - invalid transfer-ratio sums when provided.
- Unknown event kinds should classify to `other` without breaking capture.
- Implemented the typed public contract in:
  - `src/pygrc/telemetry/grc9_contract.py`
- Exported the contract surface from:
  - `src/pygrc/telemetry/__init__.py`
- Added focused contract coverage in:
  - `tests/telemetry/test_grc9_contract.py`
- Chosen Iteration 2 classifier mapping for currently emitted GRC9 events:
  - `spark` -> domain `spark`, stage `confirmed`
  - `expansion` -> domain `expansion`, stage `module_created`
  - `growth` -> domain `growth`, stage `child_attached`
  - `budget_correction` -> domain `budget`, stage `corrected`
  - `coarse_cache_invalidation` -> domain `coarse`, stage `invalidated`
  - unknown events -> domain `other`, stage `other`
- Chosen validation boundary:
  - the shared telemetry schema remains family-agnostic
  - GRC9 payload validation lives in the contract dataclasses
  - builders from live runtime state remain deferred to Iteration 3

### Verification

- [x] Contract tests cover step extension mapping
- [x] Contract tests cover event classification
- [x] Contract tests cover run-summary extension mapping
- [x] Contract tests cover validation failures
- [x] Existing telemetry schema tests still pass

Focused verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_contract tests.telemetry.test_grcv3_contract tests.telemetry.test_schema`
- result:
  - `Ran 18 tests`
  - `OK`

Broader telemetry verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest discover tests/telemetry`
- result:
  - `Ran 110 tests`
  - `OK`

### Summary

Completed the typed GRC9 telemetry contract module. Phase T-GRC9 now exports a
public `grc9` contract surface with typed step/event/run-summary payloads,
validated lifecycle counts and mechanical summaries, event classification for
current GRC9 runtime events, and focused contract tests.

## Iteration 3. Step Extension Builders

### Goal

Build deterministic GRC9 step extensions from live runtime state without
mutating the model.

### Checks

- [x] Add GRC9 step-extension builder helpers
- [x] Populate backend/config summary from resolved params
- [x] Populate port chart summary from topology and occupied ports
- [x] Populate row tensor summary from cached row tensor diagnostics
- [x] Populate column diagnostic summary from current column diagnostics
- [x] Populate transport summary from conductance, potential, flux, and labels
- [x] Populate identity/abundance summary from sink/basin state
- [x] Populate coarse-graining summary from coarse cache and supported fields
- [x] Populate budget correction summary from observables / cached diagnostics
- [x] Add tests for deterministic builder output on fixed representative state

### Implementation Notes

- Builders should degrade explicitly when optional caches are unavailable.
- Full port occupancy should remain a checkpoint concern, not a step-row dump.
- `scale_weighted_abundance` should record the gamma used if emitted.
- Successor tie counts should use the same deterministic tie policy as Phase 6.

### Verification

- [x] Builder output is deterministic
- [x] Builder output is JSON-safe through the telemetry schema
- [x] Builder does not mutate `GRC9State`
- [x] Missing optional caches are represented explicitly

Focused verification:

- command:
  `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_extensions tests.telemetry.test_grc9_contract tests.telemetry.test_schema`
- result:
  - `Ran 16 tests`
  - `OK`

### Summary

Completed private GRC9 step-extension builders in
`src/pygrc/telemetry/_grc9_extensions.py`. The builder now extracts the
Iteration 1 typed step contract from live `GRC9` state and caches, including
backend policy, port-chart occupancy, row tensor diagnostics, spark column
diagnostics, transport labels/flux, sink/basin identity summaries,
coarse-cache summaries, and budget correction state. Experiment-lane wiring is
still deferred to the planned migration iteration.

Follow-up review fixes completed before Iteration 4:

- `successor_tie_count` is computed from the same positive-outflow argmax
  policy used by Phase 6 successor selection, with deterministic
  neighbor/edge tie-breaking recorded in telemetry.
- `scale_weighted_abundance` and `scale_weighted_abundance_gamma` are emitted
  when an abundance gamma is configured on the resolved GRC9 evolution params.

## Iteration 4. Event Extension Builders

### Goal

Classify GRC9 mechanical events into stable telemetry domains and lifecycle
stages.

### Checks

- [x] Classify spark events
- [x] Classify expansion events
- [x] Classify growth events
- [x] Classify budget correction events if present
- [x] Classify coarse-cache invalidation events if represented as events
- [x] Extract spark trigger evidence:
  - active degree
  - instability score
  - column proxy minimum
  - sign-crossing gate
  - predicted module size
- [x] Extract expansion evidence:
  - target effective degree
  - module-size formula
  - module shape
  - reassignment counts by column
  - coherence transfer ratios
  - bond mode / bond weight
  - internal conductance stats
  - expansion substeps
- [x] Extract growth evidence:
  - selected parent port
  - birth rule
  - birth probability
  - outward flux pressure

### Implementation Notes

- Event classification should not replace raw event payloads.
- `fission_confirmed` is an event/report stage only when persistence criteria
  are actually evaluated.
- Expansion telemetry should distinguish the spark trigger from the resulting
  topology mutation.

### Verification

- [x] Event classifier handles known GRC9 event kinds
- [x] Unknown event kinds classify to `other`
- [x] Spark event tests distinguish instability, column proxy, and sign
  crossing
- [x] Expansion event tests cover transfer ratios and reassignment counts
- [x] Growth event tests cover selected inactive port and birth probability

Focused verification:

- command:
  `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_extensions tests.telemetry.test_grc9_contract tests.telemetry.test_schema`
- result:
  - `Ran 19 tests`
  - `OK`

### Summary

Completed event extension builders and classifier enrichment. The public
`classify_grc9_event_extension` now consumes richer spark, expansion, growth,
budget, and coarse invalidation payloads when available. The private
`_build_grc9_event_extension` builder enriches raw runtime `GRCEvent` payloads
from live `GRC9` params/state before classification, including spark predicted
module size, expansion reassignment-by-column counts, transfer ratios, bond
weight mode/stats, expansion schedule/substeps, and growth birth-rule context.

## Iteration 5. Run-Summary Builders

### Goal

Summarize GRC9 mechanical trajectories without requiring downstream code to
parse raw event payloads.

### Checks

- [x] Build lifecycle event counts
- [x] Build final backend/config summary
- [x] Build final port/tensor/column/transport/identity/coarse summaries
- [x] Build expansion summary
- [x] Build growth summary
- [x] Build calibration summary when calibration data exists
- [x] Build identity-fission candidate summary
- [x] Build identity-fission confirmed summary when persistence windows are
  evaluated
- [x] Split budget correction counts into:
  - uniform correction count
  - simplex/projection correction count

### Implementation Notes

- Identity fission is not a hard-coded split event. It is a post-expansion
  diagnostic based on later sink/basin persistence.
- The run summary should be fixed-width enough for comparison reports.
- Calibration summaries should record whether thresholds are absolute or
  calibrated fractions.

### Verification

- [x] Run-summary tests cover lifecycle counts
- [x] Run-summary tests cover expansion/growth totals
- [x] Run-summary tests cover identity fission candidate vs confirmed fields
- [x] Run-summary tests cover budget correction count split

Focused verification:

- command:
  `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_extensions tests.telemetry.test_grc9_contract tests.telemetry.test_schema`
- result:
  - `Ran 21 tests`
  - `OK`

### Summary

Completed private GRC9 run-summary builders. The builder composes final
step-surface summaries from live `GRC9` state and aggregates trajectory
lifecycle counts from `StepResult.events`, including spark kind splits,
expansion/growth totals, budget uniform vs simplex/projection counts,
calibration threshold/rate summary, and identity-fission candidate vs confirmed
fields. Confirmed fission remains artifact-backed only when persistence-window
diagnostics are already present in runtime caches; otherwise it remains zero
and marked reserved-future in the diagnostic status summary.

## Iteration 6. Representative Lane Wiring

### Goal

Wire the richer GRC9 contract into the representative mechanical replay lane.

### Checks

- [x] Update representative GRC9 telemetry capture to use typed step extensions
- [x] Update representative GRC9 telemetry capture to use typed event extensions
- [x] Update representative GRC9 telemetry capture to use typed run-summary
  extensions
- [x] Keep primary/replay comparison behavior unchanged
- [x] Preserve reconstruction of the compact Phase 6 lane where needed
- [x] Save under a new lane name so Phase 6 baseline artifacts remain
  historically interpretable
- [x] Update or add reconstruction script support if needed

### Implementation Notes

- Do not mutate the meaning of `phase6_mechanical_baseline`.
- The representative lane should visibly include spark, expansion, growth,
  coarse-grain / Split diagnostics, and budget correction summaries.

### Verification

- [x] Representative telemetry test covers richer `grc9` extension payloads
- [x] Primary/replay final digests still match
- [x] Saved artifacts include step, event, run summary, report, and comparison
  outputs

Focused verification:

- command:
  `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grc9_phase_t_representative_lane_emits_richer_extensions tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grc9_representative_experiment_emits_artifacts_and_eventful_reports tests.telemetry.test_grc9_extensions tests.telemetry.test_grc9_contract tests.telemetry.test_schema`
- result:
  - `Ran 23 tests`
  - `OK`

### Summary

Completed representative lane wiring. The existing
`phase6_mechanical_baseline` lane remains on the compact historical
`phase6_iter10_v1` extension, while the new
`phase_t_grc9_iter6_representative` lane emits typed Phase T-GRC9 step,
event, and run-summary extensions. No reconstruction script change was needed
because the richer lane is additive and saved under a new lane name.

## Iteration 7. Real-Seed Structural Lane Wiring

### Goal

Wire the richer GRC9 contract into the seed-driven structural bridge lane.

### Checks

- [x] Update `cell-1` / `cell-4` GRC9 landscape telemetry capture
- [x] Preserve `source_lowering_mode = structural_graph_graft_v1`
- [x] Preserve the explicit non-`GRCL-9` and non-`GRC9V3` interpretation
- [x] Emit richer step/event/run-summary extensions for both seeds
- [x] Save under a new profile name so Phase 6 baseline artifacts remain
  historically interpretable

### Implementation Notes

- This lane is still a structural bridge through the existing landscape
  boundary.
- Source/lowering claims must remain weaker than the mechanical telemetry
  claims.

### Verification

- [x] Seed-driven telemetry test covers richer `grc9` extension payloads
- [x] `cell-1` and `cell-4` runs complete with saved artifacts
- [x] Reports expose GRC9-specific summaries without claiming `GRCL-9`

Focused verification:

- command:
  `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryLandscapeExperimentTest.test_run_grc9_phase_t_landscape_profile_emits_richer_extensions tests.telemetry.test_experiments.TelemetryLandscapeExperimentTest.test_run_grc9_landscape_experiment_emits_artifacts_and_reports tests.telemetry.test_grc9_extensions tests.telemetry.test_grc9_contract tests.telemetry.test_schema`
- result:
  - `Ran 23 tests`
  - `OK`

### Summary

Completed seed-driven structural lane wiring. The existing
`phase6_seed_baseline` profile remains compact and historically interpretable,
while the new `phase_t_grc9_iter7_seed` profile emits typed Phase T-GRC9 step,
event, and run-summary extensions for both `cell-1` and `cell-4`. The richer
profile keeps `source_lowering_mode = structural_graph_graft_v1` in the lane
context and does not claim `GRCL-9` or `GRC9V3` semantics.

## Iteration 8. Graph Checkpoint Extension

### Goal

Add optional graph-checkpoint payloads for GRC9 port charts, row/column
overlays, and expansion modules.

### Checks

- [x] Define GRC9 checkpoint extension payload shape
- [x] Export node overlays:
  - active degree
  - row occupancy
  - column occupancy
  - sink/basin role
  - module membership
- [x] Export port overlays:
  - occupied flag
  - row
  - column
  - incident edge id
- [x] Export edge overlays:
  - endpoint ports
  - conductance
  - oriented flux
  - analytic labels
  - internal-module / reassigned-boundary flags
- [x] Export module overlays:
  - parent sink id
  - core/satellite/helper nodes
  - internal edges
  - reassigned boundary edges by column
- [x] Keep checkpoint export opt-in
- [x] Wire opt-in checkpoint capture into representative and seed-driven lanes

### Implementation Notes

- This is the graph-visible input surface for later GRC9 visualization.
- Behavior-only telemetry must remain valid when checkpoint export is disabled.

### Verification

- [x] Checkpoint tests cover deterministic GRC9 payloads
- [x] Behavior-only runs still work without checkpoint artifacts
- [x] Saved checkpoint payloads are JSON-safe
- [x] Representative lane can write checkpoint artifacts when requested
- [x] Seed-driven lane can write checkpoint artifacts when requested

Focused verification:

- command:
  `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grc9_phase_t_representative_lane_emits_richer_extensions tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grc9_representative_experiment_can_emit_checkpoint_artifacts tests.telemetry.test_experiments.TelemetryLandscapeExperimentTest.test_run_grc9_phase_t_landscape_profile_emits_richer_extensions tests.telemetry.test_experiments.TelemetryLandscapeExperimentTest.test_run_grc9_landscape_experiment_can_emit_checkpoint_artifacts tests.telemetry.test_checkpoints.TelemetryCheckpointTest.test_grc9_phase_t_behavior_only_lane_does_not_emit_checkpoints tests.telemetry.test_checkpoints.TelemetryCheckpointTest.test_export_grc9_graph_checkpoint_surface`
- result:
  - `Ran 6 tests`
  - `OK`

### Summary

Completed opt-in GRC9 graph checkpoint export. The new
`export_grc9_graph_checkpoint` helper emits `port_graph` checkpoints with
canonical node/edge records and GRC9-specific `port_chart_module_overlay_v1`
payloads under `family_extensions["grc9"]`. The representative and seed-driven
Phase T-GRC9 lanes now expose opt-in checkpoint-capture controls while behavior
only runs remain unchanged by default.

## Iteration 9. Theory-Facing Diagnostic Probe

### Goal

Exercise paper phenomena that may not appear strongly in the representative or
seed-driven lanes.

### Checks

- [x] Define a diagnostic probe lane
- [x] Exercise scale-weighted abundance
- [x] Exercise identity fission candidate detection
- [x] Exercise confirmed fission if persistence criteria can be met honestly
- [x] Exercise sign-crossing diagnostics if configured
- [x] Exercise spark calibration summaries if calibration is configured
- [x] Exercise coarse-grain reconstruction checks
- [x] Record any runtime gaps that prevent honest observation

### Implementation Notes

- This lane may be synthetic.
- Runtime gaps should be recorded as future work, not patched into Phase 6
  silently.

### Verification

- [x] Diagnostic lane emits the intended GRC9-specific payloads
- [x] Any unavailable paper-facing fields are marked explicitly
- [x] No deferred semantic layer is over-claimed

Focused verification:

- command:
  `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_build_grc9_diagnostic_probe_exercises_paper_facing_diagnostics tests.telemetry.test_grc9_extensions tests.telemetry.test_grc9_contract tests.telemetry.test_schema`
- result:
  - `Ran 22 tests`
  - `OK`

### Summary

Completed a synthetic theory-facing diagnostic probe via
`build_grc9_diagnostic_probe`. The probe emits typed GRC9 step and run-summary
payloads plus a sign-crossing event-extension payload, exercises
scale-weighted abundance, identity-fission candidate detection, calibrated
spark-threshold metadata, and coarse-grain reconstruction checks. Confirmed
identity fission remains `reserved_future` because Phase 6 GRC9 does not
implement the Appendix E persistence-window evaluator; the probe records this
and other deferred semantic layers explicitly under `runtime_gaps`.

## Iteration 10. Closeout Review

### Goal

Review the completed telemetry phase against the GRC9 paper and decide what
remains future-facing.

### Checks

- [x] Review every theory-to-telemetry row in the implementation plan
- [x] Mark each major field as:
  - artifact-backed,
  - diagnostic-only,
  - reserved/future,
  - out of scope
- [x] Record representative lane artifact identities
- [x] Record seed-driven lane artifact identities
- [x] Record diagnostic probe artifact identities if present
- [x] Record deferred boundaries for:
  - `GRC9V3`
  - `GRCL-9`
  - boundary barrier/ghost runtime
  - Lorentzian causal layer
  - FRC sigma field
  - observer-local views

### Implementation Notes

- Closeout should not reduce the paper to current implementation details.
- Closeout should not imply that every paper-facing reserved diagnostic is now
  a core runtime feature.

### Verification

- [x] Focused GRC9 telemetry tests pass
- [x] Representative and seed-driven artifact lanes can be reconstructed
- [x] Closeout notes distinguish telemetry evidence from deferred runtime
  semantics

Focused verification:

- command:
  `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grc9_phase_t_representative_lane_emits_richer_extensions tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_build_grc9_diagnostic_probe_exercises_paper_facing_diagnostics tests.telemetry.test_experiments.TelemetryLandscapeExperimentTest.test_run_grc9_phase_t_landscape_profile_emits_richer_extensions tests.telemetry.test_checkpoints.TelemetryCheckpointTest.test_export_grc9_graph_checkpoint_surface tests.telemetry.test_checkpoints.TelemetryCheckpointTest.test_grc9_phase_t_behavior_only_lane_does_not_emit_checkpoints tests.telemetry.test_grc9_extensions tests.telemetry.test_grc9_contract tests.telemetry.test_schema`
- result:
  - `Ran 26 tests`
  - `OK`

### Summary

Completed closeout review in `implementation/Phase-T-GRC9-Closeout.md`. The
closeout records artifact identities for the representative lane, seed-driven
profile, diagnostic probe, and opt-in checkpoint exporter; marks theory-facing
phenomena as artifact-backed, diagnostic-only, reserved/future, or out of
scope; and preserves explicit deferred boundaries for `GRC9V3`, `GRCL-9`,
boundary barrier/ghost runtime, Lorentzian causal layer, FRC sigma field, and
observer-local views.

## Iteration 11. Appendix E Identity-Fission Persistence Diagnostic

### Goal

Implement confirmed identity-fission telemetry as a non-mutating Appendix E
diagnostic over completed GRC9 trajectories.

### Checks

- [x] Add persistence-window evaluator helper
- [x] Track expansion modules across post-expansion step summaries or
  snapshots
- [x] Detect windows where the same two-sink pair persists inside one
  expansion module
- [x] Enforce configured minimum basin mass threshold
- [x] Enforce configured persistence window `Delta`
- [x] Populate `identity_fission_confirmed_count`
- [x] Populate `identity_fission_max_persistence_steps`
- [x] Keep `identity_fission_candidate_count` distinct from confirmed count
- [x] Update diagnostic status from `reserved_future` to artifact-backed when
  evaluator runs
- [x] Preserve candidate-only behavior when the window is not satisfied

### Implementation Notes

- This is telemetry/evaluator work, not a topology mutation.
- Do not add a `fission_confirmed` lifecycle event unless the evaluator has an
  explicit event/report row surface.
- Do not claim GRCV3 hierarchy, GRCL-9 lowering, observer-local views,
  Lorentzian causal semantics, FRC sigma fields, or boundary barrier/ghost
  runtime.
- The evaluator should be deterministic and replay-safe.

### Verification

- [x] Candidate-only case stays unconfirmed
- [x] Confirmed case satisfies same-pair sink persistence and basin-mass threshold
- [x] Sink-pair swap case stays unconfirmed
- [x] Below-threshold case stays unconfirmed
- [x] Run-summary builder records max persistence window
- [x] Existing Phase T-GRC9 focused tests still pass

### Summary

Implemented in Iteration 11. `_capture_grc9_identity_fission_observation`
records compact non-mutating per-step module/sink/basin observations, and
`_evaluate_grc9_identity_fission_persistence` evaluates Appendix E-style
persistence windows with configurable `Delta` and minimum basin mass. Rich
Phase T-GRC9 representative and seed-driven lanes pass captured observations
into the run-summary builder. The diagnostic probe now exercises a confirmed
two-step fission window while preserving candidate-only and below-threshold
test cases.

Verification:
`PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_extensions tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_build_grc9_diagnostic_probe_exercises_paper_facing_diagnostics tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grc9_phase_t_representative_lane_emits_richer_extensions tests.telemetry.test_experiments.TelemetryLandscapeExperimentTest.test_run_grc9_phase_t_landscape_profile_emits_richer_extensions`

Broader focused verification:
`PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_extensions tests.telemetry.test_grc9_contract tests.telemetry.test_schema tests.telemetry.test_experiments tests.telemetry.test_checkpoints`
ran 104 tests successfully.

## Post-GRCL-9 Collapse Observability Review

### Goal

As part of the next GRCL-9 work batch, decide whether collapse-adjacent
structural probes justify any GRC9-native diagnostic telemetry.

### Checks

- [x] Review `implementation/GRCL-9-CollapseAdjacentNextBatch.md`
- [x] Create `implementation/Phase-T-GRC9-CollapseAdjacentObservabilityReview.md`
- [x] Keep GRCV3 choice/collapse semantics out of GRC9
- [x] Determine whether basin merge candidates are observable from existing
      basin/sink summaries and checkpoints
- [x] Determine whether sink loss or sink dominance loss is observable without
      changing runtime equations
- [x] Determine whether membrane/ridge rupture can be represented as
      structural boundary loss from checkpoints
- [x] Determine whether support-loss candidates can be summarized from
      transport/support telemetry
- [x] Determine whether failed identity-fission persistence is sufficient as a
      collapse-adjacent diagnostic
- [x] Decide whether any accepted surface belongs in a diagnostic-only
      extension or a new telemetry contract version

### Implementation Notes

- Current `phase_t_grc9_iter1_v1` has no `collapse` event domain and no
  `collapse_evidence` group.
- Do not reinterpret `identity_fission_candidate_count` or
  `identity_fission_confirmed_count` as collapse.
- Decision: use selector-backed existing Phase T-GRC9 fields and checkpoints
  for GRCL-9 Iteration 8.1. Do not add compact collapse-adjacent fields yet.
- Placeholder names from the collapse-adjacent next-batch review, such as
  `structural_integrity_summary`, `basin_merge_candidate_count`,
  `sink_loss_candidate_count`, `membrane_rupture_candidate_count`,
  `support_loss_candidate_count`, and `collapse_candidate_summary`, remain
  reserved until GRCL-9 probes show that compact fields are needed.

### Verification

- [x] Review result states accepted, structural-only, or deferred status
- [x] Existing Phase T-GRC9 artifacts retain their original interpretation
- [x] Any new diagnostic fields are deferred, so no new contract/dataclass tests
      are required in this pass

### Summary

Completed as a review-only Phase T pass. GRCL-9 Iteration 8.1 should use
existing `identity_abundance`, `transport`, identity-fission summary, and graph
checkpoint evidence for structural probes. Compact collapse-adjacent fields are
reserved for a later contract extension only if selector failures justify them.
