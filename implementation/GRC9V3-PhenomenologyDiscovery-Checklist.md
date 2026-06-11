# GRC9V3 Phenomenology Discovery Checklist

This document tracks execution of the **GRC9V3 Phenomenology Discovery** track.

It is intentionally separate from
[`GRC9V3-PhenomenologyDiscovery-Plan.md`](./GRC9V3-PhenomenologyDiscovery-Plan.md):

- the plan defines the theory-first runtime discovery boundary, seed strategy,
  evidence surfaces, selector mapping, and reviewed-catalog path,
- this checklist records execution iteration by iteration.

## Usage Rules

- Start from Phase 7 equations, the Phase 7 step loop, and the parent-family
  specs.
- Treat the current Appendix E lane as representative telemetry/visualization
  evidence, not as the whole discovery catalog.
- Build deterministic pure `GRC9V3` runtime seeds before any GRCL/source
  claims.
- Preserve the inverse-design chain:
  - Phase 7 mechanism,
  - hybrid graph/state precondition,
  - predicted telemetry signature,
  - deterministic runtime seed,
  - observed telemetry validation.
- Keep ownership explicit:
  - `grc9_mechanical`,
  - `grcv3_semantic`,
  - `grc9v3_hybrid`.
- Use Phase T-GRC9V3 telemetry fields as primary evidence.
- Use Phase V-GRC9V3 visualization outputs only as inspection aids linked to
  telemetry.
- Record every test session in
  `outputs/grc9v3/phenomenology_discovery/ExperimentalLog.md`.
- Store replayable session artifacts under
  `outputs/grc9v3/phenomenology_discovery/sessions/S0001/`.
- Keep session ids stable and zero-padded.
- Record runtime gaps explicitly as `capability_gated`, `deferred`, or
  `out_of_scope`.
- Keep rejected, failed, and duplicate hypotheses.
- Do not claim GRCL/source-language semantics, Lorentzian behavior,
  observer-local views, FRC sigma behavior, or unsupported boundary modes.

Post-completion note: GRCL-9V3 source/lowering has since been implemented and
closed as a downstream track. This discovery checklist remains runtime-facing;
the final source/lowering closeout is [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md).

## Iteration Template

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

## Iteration 1. Discovery Planning Bootstrap

### Goal

Create the GRC9V3 discovery plan/checklist pair and lock the boundary as
theory-first pure-runtime discovery before source-language claims.

### Checks

- [x] Create `GRC9V3-PhenomenologyDiscovery-Plan.md`
- [x] Create `GRC9V3-PhenomenologyDiscovery-Checklist.md`
- [x] Record that the representative Appendix E lane is a reference artifact,
  not the whole discovery catalog
- [x] Record that discovery uses deterministic pure `GRC9V3` runtime seeds
- [x] Record the `outputs/grc9v3/phenomenology_discovery/sessions/S0001/`
  session convention
- [x] Record the inverse-design chain from Phase 7 mechanism to observed
  telemetry validation
- [x] Record ownership tagging for GRC9 mechanical, GRCV3 semantic, and GRC9V3
  hybrid evidence
- [x] Record that GRCL/source-seed work is a later handoff
- [x] Link discovery from `ImplementationPhases.md`

### Implementation Notes

- Discovery begins after Phase 7 core, Phase T-GRC9V3 telemetry, and
  Phase V-GRC9V3 visualization.
- The first useful implementation artifact after this bootstrap is the
  mechanism ledger.
- Existing Appendix E artifacts can validate tooling, but new runtime seeds
  must broaden the catalog.

### Verification

- [x] The plan keeps visuals secondary to telemetry evidence
- [x] The plan requires replayable `S0001`-style experiment sessions
- [x] The plan includes runtime constraints, seed catalog, generator contract,
  selector field mapping, manifest schema, scoring, and reviewed catalog path
- [x] The plan excludes GRCL/source claims from runtime discovery

### Summary

The GRC9V3 discovery track now has a plan/checklist pair. The scope is
theory-first inverse design over pure `GRC9V3` runtime seeds, with
Phase T-GRC9V3 telemetry as primary evidence and Phase V-GRC9V3 visualization
as a downstream inspection surface.

Current status: the downstream GRCL-9V3 source/lowering layer is complete, but
that later completion does not change this discovery boundary.

## Iteration 2. Mechanism Ledger

### Goal

Build a Phase 7 mechanism ledger that becomes the authoritative source for
runtime status, ownership, graph/state preconditions, and predicted telemetry
fields.

### Checks

- [x] Create a mechanism ledger artifact
- [x] Include `ledger_version = "grc9v3_phenomenology_mechanism_ledger_v1"`
- [x] Record one entry per mechanism with:
  - `mechanism_id`
  - `phenomenon`
  - `ownership`
  - `phase7_sources`
  - `parent_family_sources`
  - `equations`
  - `step_loop_refs`
  - `thresholds`
  - `policy_choices`
  - `graph_preconditions`
  - `state_preconditions`
  - `parameter_knobs`
  - `predicted_telemetry_fields`
  - `predicted_event_sequence`
  - `visual_evidence_surfaces`
  - `runtime_status`
  - `runtime_blockers`
- [x] Cover hybrid spark gate
- [x] Cover spark-to-expansion
- [x] Cover column diagnostic proxy
- [x] Cover Appendix E cell division
- [x] Cover choice/collapse
- [x] Cover growth
- [x] Cover quadrature budget preservation
- [x] Cover Hessian backend comparison
- [x] Cover signed-crossing spark as capability-gated when needed
- [x] Cover transport/basin rerouting
- [x] Cover coarse-cache invalidation
- [x] Cover quiescent controls
- [x] Mark deferred and out-of-scope mechanisms explicitly
- [x] Record that hypothesis runtime status is copied from the ledger unless a
  later runtime change is explicitly documented

### Implementation Notes

- The ledger should live under
  `outputs/grc9v3/phenomenology_discovery/mechanism_ledger.json` once
  generated.
- The ledger is allowed to include non-testable paper-facing mechanisms, but
  selectors must not accept motifs for them.
- The standalone paper Eq. 11 column diagnostic proxy is preserved in the
  ledger, but remains capability-gated until Phase T exposes direct
  per-column `H_s^(b)` telemetry rather than only downstream hybrid/tensor
  effects.
- Implemented mechanism ledger contract module:
  - `src/pygrc/discovery/grc9v3_mechanism_ledger.py`
- Exported ledger helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_mechanism_ledger.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/ExperimentalLog.md`
  - `outputs/grc9v3/phenomenology_discovery/mechanism_ledger.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0001/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0001/reports/mechanism_ledger.json`
- Runtime status constants:
  - `testable`
  - `capability_gated`
  - `deferred`
  - `out_of_scope`

### Verification

- [x] Ledger entries round-trip through JSON
- [x] Every testable entry maps to at least one Phase T-GRC9V3 telemetry field
- [x] Every entry has at least one ownership tag
- [x] Capability-gated entries name the missing capability
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_mechanism_ledger`

### Summary

Iteration 2 is complete. GRC9V3 discovery now has a typed mechanism ledger with
Phase 7 source references, parent-family source references, ownership tags,
equations, step-loop references, thresholds, policy choices, graph and state
preconditions, parameter knobs, predicted telemetry fields, predicted event
sequences, visual evidence surfaces, runtime status, blockers, and JSON-safe
serialization. The default ledger separates currently testable mechanisms from
capability-gated, deferred, and out-of-scope mechanisms. The Eq. 11 column
diagnostic proxy is represented as capability-gated because current telemetry
does not directly expose `H_s^(b)`. S0001 records the replayable session for
this iteration.

## Iteration 3. Runtime Structure Hypothesis Catalog

### Goal

Define deterministic pure-runtime seed families and predicted signatures for
all testable ledger mechanisms.

### Checks

- [x] Create a hypothesis catalog artifact or module
- [x] Include seed families for:
  - hybrid spark gate
  - spark-to-expansion
  - Appendix E cell division
  - choice/collapse
  - growth pressure
  - budget preservation
  - Hessian backend comparison
  - signed-crossing spark when capability-enabled
  - transport/basin rerouting
  - coarse-cache invalidation
  - quiescent hybrid control
- [x] For each seed family, record:
  - graph preconditions
  - state preconditions
  - ownership tags
  - parameter knobs
  - positive controls
  - negative controls
  - predicted telemetry signatures
  - predicted event sequence
  - required checkpoint overlays
- [x] Ensure every scheduled seed family points back to a ledger mechanism
- [x] Ensure deferred mechanisms are present but not scheduled for generation

### Implementation Notes

- These are runtime seeds, not source-language seeds.
- Seeds may initialize basin, hierarchy, or choice state only as runtime state,
  not as solved source claims.
- The column diagnostic proxy family is present for ledger completeness but is
  not scheduled until direct `H_s^(b)` telemetry exists.
- Implemented hypothesis catalog module:
  - `src/pygrc/discovery/grc9v3_hypothesis_catalog.py`
- Exported catalog helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_hypothesis_catalog.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/hypothesis_catalog.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0002/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0002/reports/hypothesis_catalog.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0002/reports/structure_hypotheses.json`
- GRC9V3 discovery profile naming is:
  - `grc9v3_discovery_<phenomenon>_v<integer>`
- Generated lane naming follows the shared control-role convention:
  - `<seed_family>_<control_role>`

### Verification

- [x] Hypothesis ids are stable and token-safe
- [x] Duplicate seed families are rejected or explicitly versioned
- [x] Predicted telemetry field paths match the telemetry contract
- [x] Positive and negative controls differ in documented parameters
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_mechanism_ledger tests.discovery.test_grc9v3_hypothesis_catalog`

### Summary

Iteration 3 is complete. GRC9V3 discovery now has a typed pure-runtime
structure hypothesis catalog linked to the mechanism ledger. Scheduled families
cover hybrid spark, spark-to-expansion, Appendix E cell division,
choice/collapse, growth, budget preservation, Hessian backend comparison,
transport/basin rerouting, coarse-cache invalidation, and quiescent controls.
The column diagnostic proxy is preserved but not scheduled until direct
`H_s^(b)` telemetry exists.
Capability-gated, deferred, and out-of-scope ledger mechanisms are preserved in
the catalog but not scheduled for generation. S0002 records the replayable
session for this iteration.

## Iteration 4. Deterministic Runtime Seed Builders

### Goal

Implement deterministic `GRC9V3` seed builders for the hypothesis catalog.

### Checks

- [x] Implement a public `generate_grc9v3_seed(...)` style helper
- [x] Implement a perturbation helper for controlled parameter changes
- [x] Validate nine-port topology constraints
- [x] Validate basin/sink consistency
- [x] Validate hierarchy consistency
- [x] Validate fixed quadrature budget target
- [x] Validate capability requirements
- [x] Preserve seed parameters in session manifests
- [x] Verify generated lane names follow `<seed_family>_<control_role>`
- [x] Ensure generated graphs are connected unless the fixture explicitly tests
  a boundary case
- [x] Add unit tests for deterministic generation and JSON round-trip

### Implementation Notes

- Builders should not call GRCL or source-lowering code.
- Builders may reuse existing `GRC9V3` model/state helpers where possible, but
  must keep ownership metadata explicit.
- Implemented seed generator module:
  - `src/pygrc/discovery/grc9v3_seed_generator.py`
- Exported seed generator helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_seed_generator.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/generated_seed_catalog.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0003/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0003/reports/generated_seed_catalog.json`
- Generated seed catalog:
  - `19` seed payloads
  - `10` scheduled seed families
- The first seed builders emit valid `GRC9V3.from_state(...)` constructor
  payloads and preserve catalog metadata. They do not yet claim that lifecycle
  events occur; runtime trajectories begin in Iteration 5.
- The builder now performs explicit pre-constructor validation for graph
  connectivity, port-structure metadata, sink/basin consistency, hierarchy
  consistency, budget-target metadata, and capability-gated modes.
- `budget_preservation_positive_control` carries a controlled initial budget
  error of `0.25` so later runtime sessions can exercise correction behavior
  instead of trivially starting with a closed budget.
- Topology payloads include `port_structure.port_to_edge` and
  `port_structure.node_port_occupancy` for selector and visualization use.

### Verification

- [x] Same seed parameters produce the same payload
- [x] Invalid port assignments fail before running
- [x] Missing capability requests fail before running
- [x] Seed payloads can construct a `GRC9V3` model
- [x] Perturbation tests verify the parameter value changes, not only the lane
  name
- [x] State-payload tests verify sink, basin, hierarchy, budget, and port
  metadata consistency across scheduled families
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_mechanism_ledger tests.discovery.test_grc9v3_hypothesis_catalog tests.discovery.test_grc9v3_seed_generator`

### Summary

Iteration 4 is complete. GRC9V3 discovery now has deterministic pure-runtime
seed builders for the scheduled hypothesis catalog. Generated payloads validate
through `GRC9V3.from_state(...)`, preserve seed parameters, ownership tags,
runtime config, graph/state preconditions, predicted telemetry signatures, and
checkpoint overlay requirements. S0003 records the replayable seed-generation
session and the generated seed catalog.

## Iteration 5. First Control Sessions

### Goal

Run small positive/negative control sessions for each testable seed family and
capture replayable telemetry/checkpoint evidence.

### Checks

- [x] Create `outputs/grc9v3/phenomenology_discovery/ExperimentalLog.md`
- [x] Create session root:
  `outputs/grc9v3/phenomenology_discovery/sessions/S0004/`
- [x] Run hybrid spark positive and negative controls
- [x] Run spark-to-expansion controls
- [x] Run Appendix E division control
- [x] Run choice/collapse controls
- [x] Run growth controls
- [x] Run budget controls
- [x] Run Hessian backend comparison controls
- [x] Run transport/basin rerouting controls
- [x] Run coarse invalidation controls
- [x] Run quiescent controls
- [x] Capture telemetry, graph checkpoints, experiment reports, replay flags,
  and final digests

### Implementation Notes

- Keep early runs short enough to inspect by hand.
- Longer windows can wait until selector behavior is known.
- Implemented discovery runner:
  - `src/pygrc/discovery/grc9v3_discovery_runner.py`
- Exported runner helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_discovery_runner.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0004/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0004/reports/run_report.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0004/reports/initial_results.md`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0004/generated_lanes/`
- `S0004` ran `19` generated control lanes for `47` total steps and captured
  `12` lifecycle events.
- All `S0004` replay checks passed:
  - step rows match
  - event rows match
  - final digests match
- Eventful lanes in the low-step window:
  - `hybrid_spark_gate_positive_control`
  - `spark_to_expansion_positive_control`
  - `appendix_e_cell_division_positive_control`
  - `appendix_e_cell_division_negative_control`
- Choice/collapse, growth, budget, Hessian backend, transport, coarse-cache,
  and quiescent controls produced replayable diagnostic telemetry but no
  lifecycle events in this short first window.

### Verification

- [x] Every session has `session_manifest.json`
- [x] Every session records the exact replay command
- [x] Every session records the replay environment note
- [x] Every session records seed parameters
- [x] Replay flags are present for telemetry rows and final digest where
  supported
- [x] Session ids are monotonic and zero-padded
- [x] Checkpoint surface names use the current Phase T-GRC9V3 contract surface
- [x] Default runs update `ExperimentalLog.md` idempotently
- [x] First-pass reports explicitly confirm quiescent no-event controls
- [x] First-pass reports flag eventful negative controls as selector-scoring
  inputs, not accepted/rejected mechanism evidence
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_discovery_runner`

### Summary

Iteration 5 is complete. GRC9V3 discovery now has a replayable generated-run
session for every scheduled seed control. `S0004` records telemetry rows, event
rows, run summaries, experiment reports, graph checkpoints, replay flags, final
digests, seed parameters, and the exact replay command for all `19` lanes.

## Iteration 5.1. Theory-First Seed Refinement

### Goal

Refine the seed families that did not yet express their intended runtime
behavior in `S0004`, then rerun a replayable refined control session before
field-backed selector implementation.

### Checks

- [x] Keep `S0004` as the first generated-control smoke session
- [x] Refine `choice_collapse` so the positive control emits choice/collapse
  evidence or is explicitly reclassified
- [x] Refine `growth_pressure` so the positive control emits growth evidence
  or records the runtime blocker
- [x] Refine `budget_preservation` so the positive control observes budget
  correction evidence
- [x] Refine `coarse_cache_invalidation` so the positive control observes
  coarse invalidation evidence
- [x] Refine `transport_basin_rerouting` so positive/negative controls expose
  distinct transport signatures
- [x] Verify `hessian_backend_comparison` as a diagnostic family with an
  explicit divergence surface
- [x] Preserve quiescent no-event behavior
- [x] Run refined controls as `S0005`
- [x] Capture telemetry, graph checkpoints, experiment reports, replay flags,
  final digests, and seed parameters
- [x] Record `S0005` in `ExperimentalLog.md`

### Implementation Notes

- Seed refinements must follow the Phase 7 gates rather than random
  perturbation.
- The goal is not to force every family into a lifecycle event. Diagnostic
  families are acceptable only when their selector surface is explicit.
- Selectors in Iteration 6 should consume both `S0004` smoke evidence and
  `S0005` refined evidence.
- Implemented refined seed generation by passing `refined_fixture=True` through
  the discovery runner, preserving the default S0004 replay path.
- Implemented refined discovery runner mode:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_discovery_runner --session-id S0005 --refined-controls`
- `S0005` ran `19` generated control lanes for `47` total steps and captured
  `18` lifecycle events.
- Refinement outcomes:
  - `choice_collapse_positive_control` emits `collapse`
  - `choice_collapse_negative_control` emits `choice_detected` but no collapse
  - `growth_pressure_positive_control` emits `growth`
  - `growth_pressure_negative_control` emits no growth
  - `budget_preservation_positive_control` records correction from
    `budget_before = 72.0` to `budget_target = 71.75`
  - `coarse_cache_invalidation_positive_control` records
    `coarse_cache_invalidated = true` on the first step
  - `coarse_cache_invalidation_negative_control` remains not invalidated
  - `transport_basin_rerouting` controls expose distinct transport summaries
  - `hessian_backend_comparison_positive_control` records
    `weighted_least_squares_hessian_available = true`
  - `quiescent_hybrid_control_no_event_control` remains event-free

### Verification

- [x] Refined runner/session tests pass
- [x] At least one formerly diagnostic lifecycle-facing family emits its
  intended evidence
- [x] `S0005` replay step rows match
- [x] `S0005` replay event rows match
- [x] `S0005` replay final digests match
- [x] Scoped diff check passes for touched source/docs

### Summary

Iteration 5.1 is complete. The refined session keeps S0004 as the smoke
baseline and adds S0005 as theory-first repaired evidence. The new run preserves
all replay guarantees while adding runtime-backed collapse and growth evidence
and making the remaining diagnostic surfaces explicit for Iteration 6 selectors.

## Iteration 5.2. Appendix E Pass/Fail Separation

### Goal

Repair the Appendix E negative control before selector implementation. `S0005`
showed that `appendix_e_cell_division_negative_control` still completed the
same division as the positive lane, making it unusable as a pass/fail selector
case.

### Checks

- [x] Keep `S0004` and `S0005` replay paths stable
- [x] Preserve the Appendix E positive lane as a completed division control
- [x] Refine the Appendix E negative lane into an explicit no-completion
  control
- [x] Avoid claiming a runtime daughter-min-mass evaluator unless it is actually
  implemented
- [x] Run refined controls as `S0006`
- [x] Verify `appendix_e_cell_division_positive_control` still emits completed
  Appendix E evidence
- [x] Verify `appendix_e_cell_division_negative_control` has
  `hybrid_spark_completed_count == 0` or no representative Appendix E completion
  summary
- [x] Capture telemetry, graph checkpoints, experiment reports, replay flags,
  final digests, and seed parameters
- [x] Record `S0006` in `ExperimentalLog.md`

### Implementation Notes

- The negative lane should fail a real Phase 7 runtime precondition. Current
  Phase 7 does not expose a separate Appendix E daughter-min-mass stabilization
  gate, so the negative control must not be described as a solved min-mass
  failure.
- Selectors in Iteration 6 should use `S0006` for Appendix E pass/fail scoring.
- Implemented S0006 mode:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_discovery_runner --session-id S0006 --appendix-e-pass-fail-controls`
- `S0006` ran `19` generated control lanes for `47` total steps and captured
  `15` lifecycle events.
- Appendix E pass/fail outcomes:
  - `appendix_e_cell_division_positive_control` emits one
    `hybrid_spark_completed` event and records `daughter_sink_count = 2`
  - `appendix_e_cell_division_negative_control` emits no Appendix E lifecycle
    events and has no `representative_appendix_e_summary`
- The no-completion negative currently removes the saturated-parent
  precondition. This is intentionally narrower than daughter-min-mass failure
  because the current Phase 7 runtime does not implement a daughter-min-mass
  stabilization evaluator.

### Verification

- [x] `S0006` replay step rows match
- [x] `S0006` replay event rows match
- [x] `S0006` replay final digests match
- [x] Focused runner tests pass
- [x] Scoped diff check passes for touched source/docs

### Summary

Iteration 5.2 is complete. S0006 replaces S0005 as the Appendix E selector
input because it has a clean positive completed-division lane and a separated
negative no-completion lane. The refinement is explicit about the current
runtime boundary: it verifies pass/fail completion evidence without claiming a
daughter-min-mass evaluator that is not implemented.

## Iteration 6. Field-Backed Selectors

### Goal

Implement selectors over saved GRC9V3 discovery sessions and score predicted
vs observed signatures.

### Checks

- [x] Implement selectors for spark candidates and completed sparks
- [x] Implement selectors for expansion
- [x] Implement selectors for Appendix E daughter sinks and hierarchy
- [x] Implement selectors for choice/collapse
- [x] Implement selectors for growth
- [x] Implement selectors for budget correction
- [x] Implement selectors for Hessian backend comparison
- [x] Implement selectors for hybrid tensor anisotropy, trace, row mismatch,
  and hotspot samples when available
- [x] Implement selectors for transport flux, potential, and positive/negative
  flux edge counts
- [x] Implement selectors for identity/basin sink count, basin count,
  geometric seed count, and validated basin count
- [x] Implement capability-gated selectors for signed-crossing prerequisites:
  previous signed-Hessian availability and signed-crossing status
- [x] Implement selectors for transport/basin rerouting
- [x] Implement selectors for coarse-cache state and invalidation
- [x] Implement selectors for no-event controls
- [x] Verify `contract_version == "phase_t_grc9v3_iter1_v1"` in loaded step,
  event, and run-summary artifacts
- [x] Report missing telemetry surfaces explicitly
- [x] Write selector reports under the session or discovery report root

### Implementation Notes

- Selectors must read saved artifacts, not live model state.
- Images are never selector inputs.
- Implemented field-backed selector validation module:
  - `src/pygrc/discovery/grc9v3_selector_validation.py`
- Exported selector validation helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_selector_validation.py`
- Wrote replayable selector-validation session:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0007/selector_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0007/reports/selector_validation_report.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0007/reports/selector_validation_summary.md`
- S0007 uses S0006 as its source because S0006 contains the Appendix E
  pass/fail-separated controls needed for selector scoring.
- Negative controls are scored against their expected absence or fail-mode
  telemetry, so a correct negative control can also score as a strong
  candidate for the negative-control motif record.
- Selector results now record `failure_kind` (`passed`, `missing_surface`, or
  `predicate_failed`). Missing surfaces cap the confidence score at weak
  candidate unless no expected selectors can be evaluated.
- Signed-crossing selectors validate capability-status telemetry only. A
  `capability_disabled` value is valid status evidence and does not claim a
  successful signed-crossing event.
- Transport/basin rerouting selectors include paired positive/negative
  predicates over flux magnitude and potential span so both controls can score
  strongly while preserving distinct signatures.
- `appendix_e_cell_division_negative_control` is documented as absence of
  completed Appendix E evidence caused by the refined negative precondition; it
  does not claim a runtime daughter-min-mass evaluator.

### Verification

- [x] Expected pass controls and their paired fail controls score according to
  their control-specific predicted signatures
- [x] Missing fields are represented as failed selector results with concrete
  field paths in the report
- [x] Selector output is deterministic
- [x] Confidence scores follow the plan rubric
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_selector_validation`
- [x] Determinism test verifies repeated validation produces identical selector,
  validation, and motif payloads
- [x] Negative-control and no-event motif records preserve `control_role` and
  `evidence_mode`

### Summary

Iteration 6 is complete. S0007 validates 19 lanes from S0006 with field-backed
selectors over persisted run summaries, step rows, and event rows. All 19 lanes
score as `strong_candidate`, no selector expectations are missing, and the
selector manifest records 19 candidate motif records for later review.

## Iteration 7. Complex Hybrid Examples

### Goal

Compose multiple mechanisms into longer connected runtime examples.

### Checks

- [x] Build a connected spark -> expansion -> completed-spark hierarchy-state
  example
- [x] Build a connected spark -> expansion -> choice -> collapse example
- [x] Build a connected expansion -> growth -> budget -> coarse invalidation
  example
- [x] Build a Hessian-backend comparison pair on the same graph
- [x] Add targeted perturbations around the complex examples
- [x] Keep every run replayable under session roots

### Implementation Notes

- Complex examples should remain pure runtime fixtures.
- Disjoint graph unions are not valid evidence unless the mechanism explicitly
  describes disconnected components.
- Implemented complex example generation in:
  - `src/pygrc/discovery/grc9v3_seed_generator.py`
- Implemented replayable complex session runner in:
  - `src/pygrc/discovery/grc9v3_discovery_runner.py`
- Added CLI replay flag:
  - `--complex-hybrid-examples`
- Added complex lane selector expectations in:
  - `src/pygrc/discovery/grc9v3_selector_validation.py`
- Preserved coarse-cache invalidation telemetry across multi-stage steps so
  topology-change invalidation is not overwritten by the final empty-cache
  refresh.
- Added predicted-vs-observed event sequence analysis to lane reports so
  composed examples can preserve the target chain while explicitly recording
  additional lifecycle side effects.
- Added a selector for `coarse_cache_invalidation_reason`, which is the primary
  coarse-cache invalidation signal in the mechanism ledger.
- Added focused tests:
  - `tests/discovery/test_grc9v3_seed_generator.py`
  - `tests/discovery/test_grc9v3_discovery_runner.py`
- Wrote replayable complex example session:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0008/reports/run_report.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0008/reports/initial_results.md`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0008/session_manifest.json`
- Wrote selector validation over the complex examples:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0009/selector_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0009/reports/selector_validation_report.json`

### Verification

- [x] Complex examples still pass topology validation
- [x] Event sequences match predicted order or record an explicit miss
- [x] Selectors can score complex examples without fixture-specific hacks
- [x] Extra choice/collapse events in composed lanes are recorded in
  `event_sequence_analysis` and propagated into selector motif notes
- [x] Coarse-cache invalidation selectors check both the invalidation boolean
  and `coarse_cache_invalidation_reason`
- [x] S0008 replay step rows match
- [x] S0008 replay event rows match
- [x] S0008 replay final digests match
- [x] S0009 reports 7/7 complex lanes as `strong_candidate`
- [x] Missing selector expectation count is zero
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_seed_generator tests.discovery.test_grc9v3_discovery_runner tests.discovery.test_grc9v3_selector_validation`

### Summary

Iteration 7 is complete. S0008 records 7 connected complex GRC9V3 runtime
examples over 19 total steps with 22 lifecycle events and replay-matching step
rows, event rows, and final digests. S0009 validates the complex lanes with
field-backed selectors; all 7 score as `strong_candidate` with no missing
surfaces or selector expectations. The complex examples include spark ->
expansion -> completed-spark hierarchy-state evidence, spark -> expansion ->
choice -> collapse, expansion -> growth -> budget -> coarse-cache invalidation,
paired Hessian backends on the same graph, and two targeted perturbation
controls. Composed lanes that emit additional lifecycle events preserve those
differences in `event_sequence_analysis` for Iteration 9 review.

## Iteration 8. Visual Review

### Goal

Generate visualization artifacts for candidate motifs and link graph evidence
to telemetry windows.

### Checks

- [x] Render behavior panels for candidate sessions
- [x] Render graph sequences for candidate sessions
- [x] Render graph animations where checkpoint cadence supports them
- [x] Render final interactive graph views
- [x] Link motif windows to exact checkpoint ids when available
- [x] Record nearest-before/after checkpoints when exact checkpoints are
  missing
- [x] Write a visual index for reviewed candidates

### Implementation Notes

- Visuals are secondary evidence. They cannot promote a motif without matching
  telemetry.
- Implemented visual review module:
  - `src/pygrc/discovery/grc9v3_visual_review.py`
- Exported visual review helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_visual_review.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0010/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0010/visual_index.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0010/reports/visual_review_report.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0010/reports/visual_review_summary.md`
- S0010 renders visuals into each S0008 candidate lane artifact root and then
  indexes the saved visual paths.
- Replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_visual_review --session-id S0010 --selector-session-id S0009`
- Visual artifacts per lane:
  - `visualization/graph_sequence.png`
  - `visualization/graph_animation.gif`
  - `visualization/graph_layouts.json`
  - `visualization/graph_html/final_graph.html`
  - `visualization/trajectories.png`
  - `visualization/events.png`
  - `visualization/report_panel.png`

### Verification

- [x] Every visual artifact path exists
- [x] Graph visuals use GRC9V3 overlays when available
- [x] Missing checkpoint coverage is reported
- [x] S0010 reports 7/7 motif records with `rendered_complete` visuals
- [x] S0010 reports 7/7 motif records with `enabled` overlays
- [x] S0010 reports zero missing exact checkpoint steps
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_visual_review`

### Summary

Iteration 8 is complete. S0010 renders complete Phase V-style behavior and
graph visual suites for the seven S0009 complex GRC9V3 motif candidates and
links those motifs to 20 exact graph checkpoints from S0008. Every indexed
record has complete visual artifacts, enabled GRC9V3 overlays, and zero missing
exact checkpoint steps. Visuals remain secondary evidence and do not promote a
motif without matching telemetry.

## Iteration 8.1. Hessian Comparator Review

### Goal

Separate Hessian backend diagnostic comparators from lifecycle event
phenomenology before reviewed motif cataloging.

### Checks

- [x] Reclassify current S0008 Hessian lanes as diagnostic comparators
- [x] Preserve current S0008 Hessian lanes as useful backend/tensor evidence
- [x] Mark current S0008 Hessian lanes as not eligible for lifecycle motif
  acceptance
- [x] Run a paired eventful Hessian backend probe on matching graph/state inputs
- [x] Record whether the eventful probe finds a backend-dependent event delta
- [x] Preserve no-delta eventful probe evidence without over-claiming
- [x] Write a replayable Hessian comparator review session

### Implementation Notes

- Implemented review/probe module:
  - `src/pygrc/discovery/grc9v3_hessian_comparator_review.py`
- Exported review helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_hessian_comparator_review.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0011/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0011/hessian_comparator_review.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0011/reports/hessian_comparator_review_report.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0011/reports/hessian_comparator_review_summary.md`
- Replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_hessian_comparator_review --session-id S0011`
- Review rule for Iteration 9:
  - Hessian backend/tensor evidence alone is `diagnostic_comparator`.
  - A Hessian lifecycle motif requires a backend-dependent event sequence or
    backend-dependent lifecycle outcome.
  - Eventful probes with identical backend event sequences are preserved as
    negative delta evidence, not promoted to Hessian event motifs.

### Verification

- [x] S0008 Hessian pair has no lifecycle events and is classified as
  `diagnostic_comparator`
- [x] S0008 Hessian pair has matching initial topology and node state
- [x] S0011 eventful probe emits spark/expansion/completed-spark under both
  Hessian backends
- [x] S0011 eventful probe reports `eventful_no_backend_event_delta`
- [x] Backend event delta count is zero
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_hessian_comparator_review`

### Summary

Iteration 8.1 is complete. S0011 records two S0008 Hessian lanes as diagnostic
comparators, not lifecycle motifs, and runs a paired eventful Hessian backend
probe. The probe emits the same spark -> expansion -> completed-spark sequence
under both `row_basis_diagonal` and `weighted_least_squares`, so no
backend-dependent lifecycle event delta was found. Iteration 9 should preserve
these as diagnostic/negative-delta evidence unless a later fixture produces a
backend-dependent lifecycle outcome.

## Iteration 9. Reviewed Motif Catalog

### Goal

Review scored candidates and publish the first GRC9V3 motif catalog.

### Checks

- [x] Build reviewed motif catalog JSON
- [x] Build reviewed motif catalog Markdown
- [x] Preserve accepted candidates
- [x] Preserve strong candidates
- [x] Preserve rejected candidates
- [x] Preserve duplicates
- [x] Preserve needs-rerun entries
- [x] Record review history
- [x] Deduplicate by phenomenon, seed family, predicted signature, and observed
  event sequence
- [x] Record non-claims for every accepted motif

### Implementation Notes

- A rejected motif is still useful evidence and should stay in the catalog.
- The catalog should identify motifs suitable for later source-language
  expression, but not implement that expression.
- Implemented reviewed catalog module:
  - `src/pygrc/discovery/grc9v3_reviewed_motif_catalog.py`
- Exported reviewed catalog helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_reviewed_motif_catalog.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0012/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0012/reviewed_motif_catalog.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0012/reviewed_motif_catalog.md`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0012/reports/reviewed_motif_catalog_report.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0012/reports/reviewed_motif_catalog_summary.md`
- Replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_reviewed_motif_catalog --session-id S0012`
- Review policy:
  - Eventful complex-control motifs with telemetry, selector, run-summary, and
    visual/checkpoint support are promoted to `accepted`.
  - Perturbation controls are preserved as `strong_candidate` /
    `negative_control`, not promoted to event motifs.
  - Hessian backend/tensor records are preserved as `diagnostic_comparator`
    unless a backend-dependent lifecycle event delta exists.
  - Visuals are supporting evidence only; no record can be accepted from visuals
    alone.

### Verification

- [x] Catalog round-trips through JSON
- [x] Markdown summary matches JSON counts
- [x] Accepted motifs have telemetry, event, run-summary, and visual links when
  applicable
- [x] No accepted motif depends only on a visual image
- [x] S0012 records 3 accepted lifecycle motifs
- [x] S0012 records 2 strong negative-control candidates
- [x] S0012 records 2 Hessian diagnostic comparators
- [x] S0012 records 0 rejected, 0 duplicate, and 0 needs-rerun records
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_reviewed_motif_catalog`

### Summary

Iteration 9 is complete. S0012 publishes the first reviewed GRC9V3 runtime
motif catalog with 7 records: 3 accepted lifecycle motifs, 2 strong
negative-control candidates, and 2 Hessian diagnostic comparators. The catalog
links selector evidence from S0009, visual/checkpoint evidence from S0010, and
Hessian comparator review evidence from S0011. Accepted motifs carry explicit
non-claims for source lowering, Lorentzian causal semantics, and visual-only
promotion.

## Iteration 9.1. Catalog Breadth Expansion

### Goal

Fold the successful simple-control selector evidence back into the reviewed
catalog so GRC9V3 breadth is comparable to the GRC9 discovery catalog rather
than represented only by the complex-control subset.

### Checks

- [x] Import S0007 simple-control selector evidence
- [x] Import S0012 reviewed complex-control catalog records
- [x] Deduplicate records by lane name
- [x] Promote eventful positive simple controls to accepted runtime motifs
- [x] Preserve no-event and negative controls as strong candidates
- [x] Preserve Hessian backend comparison controls as diagnostic comparators
- [x] Preserve rejected and needs-rerun counts
- [x] Write replayable S0013 session artifacts
- [x] Update the experimental log

### Implementation Notes

- Implemented catalog breadth expansion module:
  - `src/pygrc/discovery/grc9v3_catalog_breadth_expansion.py`
- Exported helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_catalog_breadth_expansion.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0013/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0013/expanded_motif_catalog.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0013/expanded_motif_catalog.md`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0013/reports/catalog_breadth_expansion_report.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0013/reports/catalog_breadth_expansion_summary.md`
- Replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_catalog_breadth_expansion --session-id S0013`

### Verification

- [x] S0013 records 26 total motifs
- [x] S0013 records 11 accepted motifs
- [x] S0013 records 11 strong candidates
- [x] S0013 records 4 diagnostic comparators
- [x] S0013 records 0 rejected and 0 needs-rerun records
- [x] S0013 includes 19 simple-control records from S0007
- [x] S0013 includes 7 base catalog records from S0012
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_catalog_breadth_expansion`

### Summary

Iteration 9.1 is complete. S0013 expands the GRC9V3 reviewed motif surface from
7 complex-control records to 26 total records by adding the validated S0007
simple controls. The resulting catalog is still more compact than the GRC9
catalog, but it is no longer thin: it now preserves lifecycle motifs,
mechanism-diagnostic motifs, negative controls, quiescent controls, and Hessian
diagnostic comparators in one replayable catalog.

## Iteration 10. Source-Language Handoff

### Goal

Prepare the then-later GRCL/source-seed track using reviewed runtime motifs.

### Checks

- [x] Create a source-language handoff note
- [x] List runtime motifs suitable for source expression
- [x] List runtime motifs that require new source vocabulary
- [x] List runtime motifs that should remain runtime-only
- [x] Preserve the distinction between runtime evidence and source claims

### Implementation Notes

- This is a planning handoff only. It should not implement GRCL/source lowering.
- Implemented source-language handoff module:
  - `src/pygrc/discovery/grc9v3_source_handoff.py`
- Exported handoff helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9v3_source_handoff.py`
- Wrote replayable session record:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0014/session_manifest.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0014/source_language_handoff.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0014/source_language_handoff.md`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0014/reports/source_language_handoff_report.json`
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0014/reports/source_language_handoff_summary.md`
- Replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_source_handoff --session-id S0014`

### Verification

- [x] Every handoff motif links to a reviewed runtime motif
- [x] No source construct is claimed without runtime evidence
- [x] S0014 reviews all 26 S0013 expanded catalog records
- [x] S0014 lists 8 source-expression candidates
- [x] S0014 lists 12 records that require new source vocabulary
- [x] S0014 lists 6 runtime-only records
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_source_handoff`

### Summary

Iteration 10 is complete. S0014 closes the pure-runtime discovery track by
turning the expanded S0013 catalog into a source-language planning handoff. It
identifies 8 accepted lifecycle motifs as source-expression candidates, 12
control/transport records that need explicit source vocabulary, and 6
runtime-only diagnostic or backend records. The handoff keeps every entry in
`runtime_evidence_only` status and does not implement GRCL/source lowering.

Post-completion status: the downstream GRCL-9V3 implementation used this
handoff and is now closed through reviewed lowered-source catalog `S0072`.
