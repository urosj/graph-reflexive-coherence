# GRC9 Phenomenology Discovery Checklist

This document tracks execution of the **GRC9 Phenomenology Discovery** track.

It is intentionally separate from
[`GRC9-PhenomenologyDiscovery-Plan.md`](./GRC9-PhenomenologyDiscovery-Plan.md):

- the plan defines the theory-first discovery boundary, seed strategy,
  manifest shape, evidence surfaces, and acceptance criteria,
- this checklist records how that discovery work is executed iteration by
  iteration.

## Usage Rules

- Start from the GRC9 paper mathematics and spec, not from existing smoke lanes.
- Treat current GRC9 representative and landscape lanes as telemetry and
  visualization checks only.
- Build deterministic pure GRC9 mechanical graph seeds.
- Do not use GRCL-9 source objects, source lowering, or high-level semantic
  constructs in the discovery seeds.
- Preserve the inverse-design chain:
  - paper mechanism,
  - graph-local precondition,
  - predicted telemetry signature,
  - deterministic GRC9 seed,
  - observed telemetry validation.
- Use Phase T-GRC9 telemetry fields as primary evidence.
- Use Phase V visualization outputs only as inspection aids linked to telemetry.
- Record every test session in
  `outputs/grc9/phenomenology_discovery/ExperimentalLog.md`.
- Store replayable session artifacts under
  `outputs/grc9/phenomenology_discovery/sessions/S0001/`.
- Keep session ids stable and zero-padded; put categories in metadata and
  indexes.
- Record runtime gaps explicitly as `deferred`, `reserved_future`, or
  `out_of_scope`.
- Keep rejected, failed, and duplicate hypotheses; they remain evidence about
  the mechanism.
- Treat pre-correction broad-growth discovery outputs as historical diagnostics
  only. Paper-facing growth evidence must come from corrected
  `grc9_front_capacity` sessions and the corrected catalog `S0035`.
- Do not claim GRCV3, GRCL-9, Lorentzian, FRC, observer-local,
  boundary-horizon, or ghost semantics.

## Iteration Template

Copy this section for each new iteration if the checklist grows beyond the
planned sequence.

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

## Iteration 0. Discovery Planning Bootstrap

### Goal

Create the discovery plan/checklist pair and lock the boundary as theory-first
pure GRC9 seed discovery, not artifact mining and not GRCL-9 translation.

### Checks

- [x] Create `GRC9-PhenomenologyDiscovery-Plan.md`
- [x] Create `GRC9-PhenomenologyDiscovery-Checklist.md`
- [x] Create `outputs/grc9/phenomenology_discovery/ExperimentalLog.md`
- [x] Create categorized `outputs/grc9/phenomenology_discovery/` session root
- [x] Record that existing GRC9 lanes are smoke/regression fixtures only
- [x] Record that discovery uses deterministic pure GRC9 mechanical seeds
- [x] Record the `S0001` replayable session naming convention
- [x] Record the inverse-design chain from paper mechanism to observed
  telemetry validation
- [x] Record that GRCL-9 translation is a later handoff, not part of seed
  discovery
- [x] Link discovery from the Phase V GRC9 downstream documentation

### Implementation Notes

- Existing `cell-1` / `cell-4` lanes are structural graft fixtures and remain
  noncanonical for GRC9 discovery.
- Discovery seeds may reuse the GRCV2/GRCV3 seed-lane artifact pattern, but not
  their semantics.
- The first useful implementation artifact after this checklist is the
  mechanism ledger.

### Verification

- [x] The plan states that there are no canonical GRC9 discovery lanes yet
- [x] The plan keeps visuals secondary to telemetry evidence
- [x] The plan requires replayable `S0001`-style experiment sessions
- [x] The plan includes runtime constraints, seed catalog, generator contract,
  selector field mapping, checkpoint requirements, and manifest schema

### Summary

The discovery track now has a plan/checklist pair. The work is scoped as
theory-first inverse design over pure GRC9 mechanical seeds, with Phase T-GRC9
telemetry as primary evidence and Phase V visualization as a downstream
inspection surface.

## Iteration 1. Manifest Schema And Naming Contract

### Goal

Lock the discovery artifact schema and naming conventions before implementing
mechanism or seed generation code.

### Checks

- [x] Define a typed or schema-validated manifest representation
- [x] Include `manifest_version = "grc9_phenomenology_discovery_v1"`
- [x] Define `source_artifacts` with `used_for_discovery`
- [x] Define discovery profile naming:
  - `grc9_discovery_<phenomenon>_v<integer>`
- [x] Define generated lane naming:
  - `<seed_family>_<control_role>`
- [x] Define perturbation lane naming:
  - `<seed_family>_<control_role>_<parameter>_<delta>`
- [x] Define `structure_hypotheses[]`
- [x] Define structured `graph_preconditions`
- [x] Define `seed_family` and `seed_parameters`
- [x] Define `predicted_signatures`
- [x] Define `selectors[]`
- [x] Define motif records with:
  - `hypothesis_id`
  - `step_window`
  - `event_ids`
  - `checkpoint_ids`
  - grouped `evidence_fields`
  - compact predicted/observed evidence lists
  - `confidence_score`
  - `confidence_label`
  - `review_status`
  - `rejection_reason`
  - `rerun_requested`
- [x] Define `review_history[]`
- [x] Define output paths under:
  - `outputs/grc9/phenomenology_discovery/`
- [x] Define session links to:
  - `outputs/grc9/phenomenology_discovery/sessions/S0001/`

### Implementation Notes

- Consumers should prefer grouped `evidence_fields`.
- Compact `predicted_evidence_fields` and `observed_evidence_fields` remain
  compatibility lists.
- Smoke and regression lanes may be listed in `source_artifacts`, but must set
  `used_for_discovery = false` unless generated by this discovery track.
- Implemented manifest contract module:
  - `src/pygrc/discovery/grc9_manifest.py`
- Added discovery package export:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9_manifest.py`
- Implemented naming helpers:
  - `profile_name(...)`
  - `generated_lane_name(...)`
  - `perturbation_lane_name(...)`
  - `is_discovery_profile_name(...)`
  - `is_generated_lane_name(...)`
  - `is_session_id(...)`
- Chosen session id validator:
  - `S0001`-style zero-padded ids
- Chosen generated-lane control-role vocabulary:
  - `positive_control`
  - `negative_control`
  - `neutral_control`
  - `baseline_control`
  - `no_event_control`

### Verification

- [x] Manifest round-trips through JSON
- [x] Missing optional fields are handled deterministically
- [x] Review status transitions can be represented without deleting rejected
  hypotheses
- [x] Naming conventions distinguish generated discovery lanes from smoke lanes
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest`

### Summary

Iteration 1 is complete. GRC9 discovery now has a typed manifest contract with
JSON-safe mapping/load helpers, stable naming helpers, session-id validation,
structured hypothesis and motif records, review history, and tests covering
round-trip behavior, deterministic defaults, review transitions, and naming
boundaries.

## Iteration 2. Mechanism Ledger

### Goal

Build a paper/spec mechanism ledger that becomes the authoritative source for
runtime status, graph preconditions, and predicted telemetry fields.

### Checks

- [x] Read GRC9 paper and spec mechanism by mechanism
- [x] Create `mechanism_ledger.json`
- [x] Record one entry per mechanism with:
  - `mechanism_id`
  - `phenomenon`
  - `paper_sources`
  - `spec_sources`
  - `equations`
  - `inequalities`
  - `thresholds`
  - `policy_choices`
  - `graph_preconditions`
  - `predicted_telemetry_fields`
  - `runtime_status`
  - `runtime_blockers`
  - `testable_with_current_runtime`
- [x] Mark testable mechanisms
- [x] Mark deferred mechanisms
- [x] Mark reserved-future mechanisms
- [x] Mark out-of-scope mechanisms
- [x] Record that `structure_hypotheses[].runtime_status` is copied from the
  matching ledger entry unless an explicit runtime change is recorded

### Implementation Notes

- Runtime status is not a reviewer opinion; it is a constraint from the current
  implementation and telemetry contract.
- Adiabatic expansion, boundary barrier/ghost modes, ternary identity tree
  extraction, and compressed profile storage should not be promoted to testable
  motifs without runtime changes.
- Implemented mechanism ledger contract module:
  - `src/pygrc/discovery/grc9_mechanism_ledger.py`
- Exported ledger helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9_mechanism_ledger.py`
- Wrote replayable session record:
  - `outputs/grc9/phenomenology_discovery/sessions/S0001/session_manifest.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0001/reports/mechanism_ledger.json`
- Runtime status constants:
  - `testable`
  - `deferred`
  - `reserved_future`
  - `out_of_scope`

### Verification

- [x] Ledger covers all phenomena named in the plan purpose
- [x] Every ledger mechanism cites paper/spec source locations
- [x] Every testable mechanism maps to telemetry fields
- [x] Deferred/reserved mechanisms cannot produce accepted motifs
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger`

### Summary

Iteration 2 is complete. GRC9 discovery now has a typed mechanism ledger with
paper/spec source references, equations, inequalities, thresholds, policy
choices, graph preconditions, predicted telemetry fields, runtime status,
runtime blockers, and JSON-safe serialization. The default ledger separates
currently testable mechanisms from deferred, reserved-future, and out-of-scope
mechanisms, and S0001 records the replayable session for this iteration.

## Iteration 3. Seeded Structure Hypothesis Catalog

### Goal

Define minimal deterministic GRC9 seed families for each target phenomenon,
including positive controls, negative controls, and perturbation families.

### Checks

- [x] Define spark precursor seed family
- [x] Define expansion module seed family
- [x] Define column-preserving reassignment seed family
- [x] Define growth pressure seed family
- [x] Define row-tensor and column-diagnostic seed family
- [x] Define coarse-graining/profile-sparsity seed family
- [x] Define budget-correction seed family
- [x] Define quiescent basin seed family
- [x] Define transport pathway seed family
- [x] Define fission candidate seed family
- [x] For each seed family, record:
  - node count
  - row/column occupancy
  - active/inactive port pattern
  - conductance assignment
  - coherence placement
  - boundary edge pattern
  - expected lifecycle
  - positive controls
  - negative controls
  - perturbations
  - predicted telemetry signatures
- [x] Copy `runtime_status` from the mechanism ledger

### Implementation Notes

- Seed hypotheses are pure GRC9 mechanical graph hypotheses.
- They are not GRCL-9 source objects and not source-level programs.
- Negative controls should differ from positives in the smallest useful number
  of parameters.
- Implemented hypothesis catalog contract module:
  - `src/pygrc/discovery/grc9_hypothesis_catalog.py`
- Exported catalog helpers from:
  - `src/pygrc/discovery/__init__.py`
- Added focused tests:
  - `tests/discovery/test_grc9_hypothesis_catalog.py`
- Wrote replayable session record:
  - `outputs/grc9/phenomenology_discovery/sessions/S0002/session_manifest.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0002/reports/hypothesis_catalog.json`
- Row tensor and column diagnostic regimes are split into separate seed
  families because they map to separate ledger mechanisms.
- Deferred adiabatic expansion is present in the catalog but is not scheduled
  for generation.
- Review hardening:
  - hypothesis ids now use lowercase snake_case, not hyphenated ids
  - mismatched ledger entries raise before structure hypotheses are emitted
  - runtime-status mismatches raise before structure hypotheses are emitted
  - duplicate hypothesis ids raise at catalog construction
  - the three selector-sensitive telemetry paths called out in review are
    guarded against the current GRC9 telemetry contract:
    - `family_extensions.grc9.budget_evidence.budget_error_before`
    - `family_extensions.grc9.coarse_graining.profile_compression_mode`
    - `family_extensions.grc9.transport.label_availability`

### Verification

- [x] Every hypothesis references a mechanism ledger entry
- [x] Every testable hypothesis has predicted telemetry fields
- [x] Every testable hypothesis has at least one positive or negative control
- [x] Deferred hypotheses are present but not scheduled for generated runs
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog`
- [x] Negative validation tests cover ledger mismatch, runtime-status mismatch,
  duplicate hypothesis ids, and hyphenated hypothesis ids
- [x] Telemetry field guard tests cover the reviewed Iteration 6 selector paths

### Summary

Iteration 3 is complete. GRC9 discovery now has a typed seeded-structure
hypothesis catalog that covers the planned seed families, records graph shape
requirements, controls, perturbations, predicted telemetry signatures, and
runtime status copied from the mechanism ledger. The default catalog can emit
manifest-compatible `GRC9StructureHypothesis` records and S0002 records the
replayable session for this iteration.

## Iteration 4. Deterministic GRC9 Seed Generators

### Goal

Implement deterministic seed generators for the testable hypothesis catalog.

### Checks

- [x] Choose the generator module location
- [x] Implement `generate_grc9_seed(...)` or equivalent public entrypoint
- [x] Return GRC9-ready initial state or constructor input
- [x] Return seed metadata:
  - `seed_family`
  - `seed_name`
  - `seed_parameters`
  - `expected_runtime_config`
  - `graph_preconditions`
  - `predicted_signatures`
  - `negative_control_of`
  - `perturbation_of`
- [x] Support common parameters:
  - `node_count`
  - row/column occupancy
  - active/inactive port pattern
  - edge and boundary edge list
  - conductance assignment mode
  - coherence placement and total budget
  - `D_eff`
  - expansion transfer ratios
  - internal bond mode and weight
  - spark threshold and mode
  - birth rule and lambda
  - budget preservation policy
  - scale-weighted abundance gamma
  - fission persistence delta
  - fission minimum basin mass
- [x] Implement pre-run validation
- [x] Implement deterministic perturbation generation

### Implementation Notes

- Validation should fail before a generated run starts if the requested seed
  violates nine-port constraints or depends on unsupported runtime behavior.
- Perturbations should record parent seed and changed parameters.
- Implemented generator module:
  - `src/pygrc/discovery/grc9_seed_generator.py`
- Added discovery package exports:
  - `GRC9_SEED_GENERATOR_VERSION`
  - `GRC9GeneratedSeed`
  - `generate_grc9_seed(...)`
  - `generate_grc9_seed_perturbation(...)`
- Generated seeds return JSON-safe GRC9 constructor payloads and are validated
  with `GRC9.from_state(...)`.
- Descriptive catalog node counts are resolved in seed metadata as
  `resolved_node_count`.
- `column_diagnostic_regime` uses a dedicated seed geometry with column-2
  near-cancellation in the runtime `H_s^(b)` diagnostic instead of reusing the
  spark-like column-imbalance seed.
- `quiescent_basin` derives active degree from the catalog
  `active_inactive_port_pattern.active_ports` list.
- `budget_error_magnitude` is an explicit seed parameter. The default `0.25`
  is a minimal testable perturbation magnitude for Iteration 5 budget
  correction runs.
- Generated topology payloads include `edge_roles` for selector and review
  visibility.
- Replayable session record:
  - `outputs/grc9/phenomenology_discovery/sessions/S0003/`

### Verification

- [x] Same seed parameters produce identical seed metadata and graph structure
- [x] Every generated seed passes port-graph validation
- [x] Positive and negative controls differ only in documented parameters where
  practical
- [x] Unsupported runtime requests fail explicitly
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator`
- [x] Discovery test suite passes:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog tests.discovery.test_grc9_seed_generator`
- [x] Review hardening tests cover perturbation lane naming, column-diagnostic
  near-cancellation, explicit edge roles, quiescent active-port derivation, and
  configurable budget perturbation magnitude

### Summary

Iteration 4 is complete. GRC9 discovery now has deterministic seed generation
for every scheduled testable hypothesis family, including positive and negative
controls, GRC9-ready state payloads, expected runtime config, graph
preconditions, predicted signatures, explicit deferred-family failure, and
deterministic perturbation lanes. Review hardening added a dedicated
column-diagnostic seed, catalog-derived quiescent active degree, explicit budget
perturbation magnitude, and edge-role visibility. S0003 records the generated
seed catalog for replay and review.

## Iteration 5. Generated Runs And Telemetry Capture

### Goal

Run generated seeds through Phase T-GRC9 telemetry and capture graph
checkpoints and Phase V visuals.

### Checks

- [x] Define discovery output root:
  - `outputs/grc9/phenomenology_discovery/sessions/S0004/generated_lanes/`
- [x] Allocate the next `S0001`-style session id before running
- [x] Add the session entry to
  `outputs/grc9/phenomenology_discovery/ExperimentalLog.md`
- [x] Create
  `outputs/grc9/phenomenology_discovery/sessions/S0004/session_manifest.json`
- [x] Record exact replay commands
- [x] Run each testable positive-control seed
- [x] Run each required negative-control seed
- [x] Run selected perturbation seeds
- [x] Capture `steps.jsonl`
- [x] Capture `events.jsonl`
- [x] Capture `run_summary.json`
- [x] Capture graph checkpoint index
- [x] Capture `port_graph` checkpoints
- [x] Capture Phase V visual outputs after telemetry succeeds
- [x] Record missing runtime surfaces in the manifest
- [x] Link generated discovery artifacts to the `S0001`-style session root

### Implementation Notes

- Short generated seeds should default to every-step checkpoints.
- Longer perturbation sweeps should capture initial, event-adjacent, final, and
  fallback every-10-step checkpoints.
- Visual generation must be downstream of saved telemetry and checkpoint
  artifacts.
- The `S0001`-style session root is the stable reference for discussion,
  review, and replay even when detailed artifacts also live under
  `outputs/discovery/`.
- Session category fields such as iteration, session kind, phenomenon, seed
  family, and control role belong in `session_manifest.json` and `indexes/`.
- Implemented low-step control runner:
  - `src/pygrc/discovery/grc9_discovery_runner.py`
- Replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0004`
- Low-step counts used:
  - `spark_precursor`: 8
  - `expansion_module`: 10
  - `column_reassignment`: 10
  - `growth_pressure`: 15
  - `row_tensor_regime`: 5
  - `column_diagnostic_regime`: 5
  - `coarse_profile_sparsity`: 3
  - `budget_correction`: 3
  - `quiescent_basin`: 20
  - `transport_pathway`: 8
  - `fission_candidate`: 12
- S0004 low-step control pass result:
  - 22 generated control lanes
  - 198 total steps
  - 220 graph checkpoints
  - 6 total events, all `growth`, both fission-candidate lanes
  - spark and expansion lanes did not emit lifecycle events at these counts

### Verification

- [x] Every generated lane records step rows, event rows, run summary, and
  checkpoint index
- [x] Every generated lane has a replayable `S0001`-style session id
- [x] Checkpoint cadence meets motif-specific requirements
- [x] Generated lanes are separate from smoke/regression lanes
- [x] Visual outputs have corresponding telemetry artifacts

### Summary

Initial low-step control pass is complete in S0004. All scheduled positive and
negative/no-event controls produced telemetry artifacts and every-step GRC9
graph checkpoints. The first empirical result is that only the fission-candidate
lanes emitted events, and those events were `growth`; spark, expansion,
reassignment, and growth-pressure seed lanes produced telemetry but no lifecycle
events. Selected lifecycle-emitter perturbation runs are now covered by S0006;
the original S0004 Phase V visualization follow-up is superseded by later
checkpoint-backed Phase V and GRCL-9 visualization sessions, including S0024
and S0025.

## Iteration 5.1. Theory-First Lifecycle Emitter Repair

### Goal

Replace generic generated control structures with theory-first emitter
structures that satisfy the GRC9 paper predicates and current runtime gates.

### Checks

- [x] Preserve S0004 as negative evidence in docs and session reports
- [x] Add a written failure note for each missing lifecycle family:
  - spark precursor
  - expansion module
  - column-preserving reassignment
  - growth pressure
  - fission candidate
- [x] Define `spark_column_proxy_emitter`
- [x] Define `spark_instability_emitter`
- [x] Define `spark_to_expansion_emitter`
- [x] Define `growth_pressure_emitter`
- [x] Define `post_expansion_fission_emitter`
- [x] For spark emitters, enforce runtime predicates:
  - center remains an identity sink after `_detect_identities`
  - active degree is exactly 9
  - either `min_b |H_s^(b)| < eps_spark` or instability gate passes
  - runtime metric/potential parameters preserve the intended flux orientation
- [x] For expansion/reassignment emitters:
  - derive from a spark-emitting saturated sink
  - preserve old boundary edges by column
  - set `D_eff_target`, transfer ratios, and bond policy explicitly
  - require observed `expansion` events before claiming reassignment evidence
- [x] For growth emitters:
  - parent has inactive ports
  - parent has positive outward flux pressure
  - `lambda_birth` makes low-step birth effectively deterministic
  - fission geometry is not used as the growth source
- [x] For fission emitters:
  - disable unrelated growth with `lambda_birth = 0`
  - construct or record post-expansion module context
  - construct two persistent sink basins
  - run for at least `identity_fission_persistence_delta + buffer`
- [x] Keep budget correction and coarse-cache invalidation as diagnostic
  selector targets unless runtime event rows are added
- [x] Allocate S0005 for repaired emitter runs
- [x] Run repaired emitters with the same low-step policy
- [x] Record concrete remaining predicate failures for any emitter that still
  does not fire

### Implementation Notes

- This is not a perturbation sweep. Do not start with random parameter
  perturbations.
- The correct workflow is:
  - paper mechanism,
  - runtime predicate,
  - graph/coherence/parameter construction,
  - predicted telemetry fields,
  - run and compare.
- S0004 should remain available as the baseline showing why generic valid
  graphs are insufficient.
- Implemented repaired emitter entrypoint:
  - `generate_grc9_lifecycle_emitter(...)`
- Implemented runner mode:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0005 --emitter-repair`
- S0005 result:
  - 5 repaired emitter lanes
  - 22 total steps
  - 27 graph checkpoints
  - 11 lifecycle event rows
  - spark emitters produced `spark` and `expansion`
  - growth emitter produced `growth`
  - fission emitter produced confirmed fission summary with no growth events

### Verification

- [x] Repaired spark lanes emit `spark` events or record exact failed gate
- [x] Repaired expansion lanes emit `spark` and `expansion` events or record
  exact failed gate
- [x] Repaired growth lanes emit `growth` events from the intended parent
- [x] Repaired fission lanes do not emit accidental growth
- [x] S0005 has replayable telemetry, checkpoints, and a result report
- [x] Discovery tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog tests.discovery.test_grc9_seed_generator`

### Summary

Iteration 5.1 is complete. The repaired theory-first emitters produced the
missing spark, expansion, and growth lifecycle events, and the post-expansion
fission emitter produced confirmed fission telemetry without unrelated growth.
S0005 is the replayable repaired-emitter session; S0004 remains the baseline
negative evidence for the earlier generic seed approach.

## Iteration 5.2. Lifecycle Emitter Perturbation Sweep

### Goal

Run one deterministic perturbation envelope around the repaired lifecycle
emitters to verify that threshold-preserving and threshold-breaking variants
separate cleanly in telemetry.

### Checks

- [x] Define perturbation variants for column-proxy spark threshold
- [x] Define perturbation variants for instability spark threshold
- [x] Define perturbation variants for `D_eff_target` module-size response
- [x] Define perturbation variants for growth `lambda_birth`
- [x] Define perturbation variants for fission minimum basin mass
- [x] Export perturbation generator entrypoint
- [x] Add runner mode and CLI flag:
  - `--emitter-perturbation`
- [x] Allocate S0006 for the perturbation sweep
- [x] Run perturbation sweep and capture telemetry
- [x] Record perturbation parent, runtime overrides, and expected effect
- [x] Verify pass variants preserve expected lifecycle signatures
- [x] Verify fail variants suppress targeted lifecycle signatures

### Implementation Notes

- These perturbations are predicate-driven, not random:
  - `eps_spark` crosses the strict column-proxy gate,
  - `tau_instability` crosses the constructed instability ratio,
  - `D_eff_target` changes expansion module size,
  - `lambda_birth` moves birth probability between deterministic and
    suppressed regimes,
  - `identity_fission_min_basin_mass` crosses the constructed basin masses.
- Implemented perturbation entrypoint:
  - `generate_grc9_lifecycle_emitter_perturbation(...)`
- Implemented runner mode:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0006 --emitter-perturbation`
- S0006 result:
  - 10 perturbation lanes
  - 44 total steps
  - 54 graph checkpoints
  - 13 lifecycle event rows
  - pass spark variants produced `spark` and `expansion`
  - fail spark variants emitted no lifecycle events
  - `D_eff` low/high variants produced module sizes `5` and `6`
  - high birth-rate growth emitted 5 `growth` events
  - low birth-rate growth emitted no events
  - fission min-mass pass confirmed one fission window
  - fission min-mass fail suppressed fission confirmation

### Verification

- [x] Focused seed-generator tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator`
- [x] Discovery tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog tests.discovery.test_grc9_seed_generator`
- [x] S0006 has replayable telemetry, checkpoints, and a result report
- [x] Perturbation pass/fail pairs are suitable selector fixtures for
  Iteration 6

### Summary

Iteration 5.2 is complete. The repaired emitter perturbation sweep cleanly
separated threshold-preserving variants from threshold-breaking variants and
produced replayable telemetry under S0006. These paired lanes are now good
selector fixtures for the prediction-validation pass.

## Iteration 5.3. Lifecycle Combination Examples

### Goal

Create composed examples before selector implementation so Iteration 6 can
validate coexistence, ordering, and summary effects across multiple GRC9
lifecycle mechanisms in the same run.

### Checks

- [x] Define `spark_growth_combo`
- [x] Define `dual_spark_combo`
- [x] Define `spark_fission_combo`
- [x] Define `growth_fission_combo`
- [x] Define `spark_growth_fission_combo`
- [x] Record component names in seed parameters
- [x] Record predicted telemetry signatures for each combo
- [x] Export combo generator entrypoint
- [x] Add runner mode and CLI flag:
  - `--lifecycle-combo`
- [x] Allocate S0007 for combination examples
- [x] Run combination examples and capture telemetry
- [x] Preserve S0005 isolated emitters and S0006 perturbations as separate
  fixture classes
- [x] Repair combo graph topology after visual review found disconnected
  components
- [x] Replay connected combo fixtures as S0021
- [x] Rebuild downstream selector/checkpoint/review/handoff evidence from
  connected replacement sessions

### Implementation Notes

- Combination examples are pure GRC9 mechanical seeds, not GRCL-lowered
  structures.
- The original S0007 examples composed separate mechanism regions as
  disconnected components. S0007 remains historical telemetry, but is
  superseded for graph-valid evidence.
- Connected combo fixtures use negligible-conductance bridge edges between
  regions so each fixture is a single GRC9 graph while preserving mechanism
  isolation for telemetry purposes.
- Growth combinations produce cascades under deterministic high
  `lambda_birth`; this is useful event-count noise for selector validation.
- Expansion-induced fission summaries are observed under the current runtime
  and are recorded as expected cross-surface behavior for combo fixtures.
- Implemented combo entrypoint:
  - `generate_grc9_lifecycle_combo(...)`
- Implemented runner mode:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0007 --lifecycle-combo`
- S0007 result:
  - 5 combination lanes
  - 24 total steps
  - 29 graph checkpoints
  - 156 lifecycle event rows
  - `spark_growth_combo`: `spark`, `expansion`, and 27 `growth` events
  - `dual_spark_combo`: 2 `spark` and 2 `expansion` events
  - `spark_fission_combo`: `spark`, `expansion`, and confirmed fission
  - `growth_fission_combo`: 34 `growth` events and confirmed fission
  - `spark_growth_fission_combo`: `spark`, `expansion`, 85 `growth` events,
    and two confirmed fission windows
- S0021 connected replay:
  - replay command:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0021 --lifecycle-combo`
  - 5 combination lanes
  - 24 total steps
  - 29 connected graph checkpoints
  - 130 lifecycle event rows
  - every lane passed checkpoint connectivity validation
- Downstream connected evidence replay:
  - S0022 selector validation from `S0004`, `S0005`, `S0006`, `S0021`,
    `S0010`, and `S0020`
  - S0023 checkpoint visual index from S0022
  - S0024 selector feedback from S0022
  - S0025 reviewed motif catalog from S0022
  - S0026 GRCL-9 planning handoff from S0025

### Verification

- [x] Focused seed-generator tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator`
- [x] Discovery tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog tests.discovery.test_grc9_seed_generator`
- [x] S0007 has replayable telemetry, checkpoints, and a result report
- [x] S0021 has replayable connected telemetry, checkpoints, and a result
  report
- [x] S0022-S0026 replace downstream evidence that depended on S0007/S0012
  disconnected graph checkpoints

### Summary

Iteration 5.3 is complete with a topology correction. S0007 added composed
lifecycle examples but used disconnected components; S0021 is the connected
replacement for graph-valid evidence. S0022-S0026 rebuild selector, checkpoint,
review, and handoff artifacts using S0021 and the connected S0020 complex
replay.

## Iteration 6. Prediction Validation And Candidate Selectors

### Goal

Implement field-backed selectors over generated telemetry and compare predicted
signatures with observed evidence.

### Checks

- [x] Implement selector loading over saved artifacts only
- [x] Implement spark selectors
- [x] Implement expansion selectors
- [x] Implement growth selectors
- [x] Implement row/column regime selectors
- [x] Implement identity/fission selectors
- [x] Implement budget/coarse selectors
- [x] Implement transport selectors
- [x] Implement no-lifecycle negative-control selectors
- [x] Implement threshold-suppression selectors
- [x] Implement combination/coexistence selectors
- [x] Use the selector field mapping from the plan
- [x] Report missing evidence fields in motif records
- [x] Compare predicted signatures with observed fields
- [x] Apply confidence scoring:
  - `0`: no evidence or missing required telemetry
  - `1`: contradicted or absent primary predicted fields
  - `2`: one primary predicted field matches
  - `3`: primary fields match and timing is plausible
  - `4`: fields, events, summary, and checkpoints agree
  - `5`: score `4` plus controls/perturbations separate cleanly
- [x] Write motif candidates into the manifest

### Implementation Notes

- Selectors must not infer evidence from graph images or live model state.
- Controls and perturbations should influence confidence when available.
- Implemented selector module:
  - `src/pygrc/discovery/grc9_selector_validation.py`
- Implemented replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id S0008`
- S0008 source sessions:
  - `S0004`
  - `S0005`
  - `S0006`
  - `S0007`
- S0008 result:
  - 42 validated lanes
  - 23 selector definitions
  - 36 motif candidates
  - 10 strong candidates
  - 26 candidates
  - 6 rejected lanes
- Selector fixture interpretation:
  - S0004 generic positive lanes are rejected when expected lifecycle
    signatures do not appear
  - S0004 negative/no-event lanes are retained as no-lifecycle candidates
  - S0005 isolated emitters are candidates
  - S0006 threshold pass/fail pairs are strong candidates
  - S0007 combination examples are candidates for coexistence validation
- Diagnostic selectors are surface-availability and diagnostic-signal checks in
  this pass; deeper paper-level acceptance for those regimes should be refined
  during motif review.

### Verification

- [x] Selector queries match current GRC9 telemetry field names
- [x] Candidates record predicted, observed, and missing evidence fields
- [x] Confidence labels derive from confidence scores
- [x] Failed hypotheses remain represented in the manifest
- [x] Discovery tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog tests.discovery.test_grc9_seed_generator tests.discovery.test_grc9_selector_validation`

### Summary

Iteration 6 is complete. S0008 validates saved telemetry from S0004-S0007,
writes a selector manifest, and records candidate motifs with predicted,
observed, and missing evidence fields. Lifecycle selectors are predicate-level;
diagnostic selectors currently assert field-backed surface availability and
observable signal, with deeper paper-level diagnostic review deferred to the
motif review pass.

## Iteration 6.1. Selector Feedback Targeting

### Goal

Apply the selector feedback loop to S0008: classify misses and ambiguities,
reuse existing targeted fixtures where they already cover lifecycle failures,
and name only the targeted diagnostic examples needed next.

### Checks

- [x] Load saved S0008 selector validation report
- [x] Identify selector misses
- [x] Identify selector ambiguities
- [x] Classify lifecycle misses covered by existing targeted fixtures
- [x] Avoid random perturbation recommendations
- [x] Propose targeted diagnostic examples only where selectors are ambiguous
- [x] Write replayable S0009 feedback report
- [x] Record feedback session in `ExperimentalLog.md`

### Implementation Notes

- Implemented feedback module:
  - `src/pygrc/discovery/grc9_selector_feedback.py`
- Implemented replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_feedback --session-id S0009`
- S0009 result:
  - 11 feedback items
  - 6 `covered_by_existing_targeted_examples`
  - 5 `selector_ambiguity_needs_targeted_examples`
- Lifecycle misses already covered:
  - spark precursor:
    `S0005/spark_column_proxy_emitter`,
    `S0005/spark_instability_emitter`,
    `S0006/spark_column_proxy_eps_pass`,
    `S0006/spark_column_proxy_eps_fail`
  - expansion/reassignment:
    `S0005/spark_to_expansion_emitter`,
    `S0006/spark_to_expansion_d_eff_low`,
    `S0006/spark_to_expansion_d_eff_high`,
    `S0007/dual_spark_combo`
  - growth:
    `S0005/growth_pressure_emitter`,
    `S0006/growth_pressure_lambda_high`,
    `S0006/growth_pressure_lambda_low`,
    `S0007/growth_fission_combo`
  - fission:
    `S0005/post_expansion_fission_emitter`,
    `S0006/post_expansion_fission_min_mass_pass`,
    `S0006/post_expansion_fission_min_mass_fail`,
    `S0007/spark_fission_combo`,
    `S0007/spark_growth_fission_combo`
- Targeted diagnostic examples proposed:
  - `row_tensor_strong_anisotropy_control`
  - `row_tensor_flat_control`
  - `column_proxy_near_zero_control`
  - `column_proxy_nonzero_control`
  - `coarse_cache_populated_sparse_profile_control`
  - `coarse_cache_populated_dense_profile_control`
  - `budget_uniform_shift_trigger_control`
  - `budget_simplex_projection_trigger_control`
  - `transport_short_path_dominant_control`
  - `transport_long_path_dominant_control`

### Verification

- [x] Feedback tests pass
- [x] Discovery tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog tests.discovery.test_grc9_seed_generator tests.discovery.test_grc9_selector_validation tests.discovery.test_grc9_selector_feedback`
- [x] S0009 has replayable report and summary artifacts

### Summary

Iteration 6.1 is complete. S0009 confirms the lifecycle misses from S0008 do
not need broad new examples because existing repaired emitters, perturbations,
and combinations already cover them. The remaining work is targeted diagnostic
fixture generation for row/column, coarse/profile, budget, and transport
selector ambiguity.

## Iteration 6.2. Targeted Diagnostic Fixture Generation

### Goal

Implement the diagnostic fixture pairs proposed by S0009, run them as a
replayable session, and rerun selector validation with the new fixtures included.

### Checks

- [x] Add targeted diagnostic fixture generator entrypoint
- [x] Add row tensor strong/flat contrast fixtures
- [x] Add column proxy near-zero/nonzero contrast fixtures
- [x] Add coarse/profile sparse/dense warm-cache contrast fixtures
- [x] Add budget uniform/negative correction contrast fixtures
- [x] Add transport short-path/long-path dominance contrast fixtures
- [x] Add `--targeted-diagnostic` runner mode
- [x] Capture replayable S0010 generated-run session
- [x] Add lane-specific selector expectations for targeted fixtures
- [x] Rerun selector validation over S0004-S0007 plus S0010 as S0011
- [x] Record S0010 and S0011 in `ExperimentalLog.md`

### Implementation Notes

- Implemented fixture generator:
  - `src/pygrc/discovery/grc9_seed_generator.py`
  - `GRC9_TARGETED_DIAGNOSTIC_NAMES`
  - `generate_grc9_targeted_diagnostic_fixture`
- Implemented runner flag:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0010 --targeted-diagnostic`
- Implemented selector replay:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id S0011 --source-session-id S0004 --source-session-id S0005 --source-session-id S0006 --source-session-id S0007 --source-session-id S0010`
- S0010 result:
  - 10 fixture lanes
  - 14 total simulation steps
  - 24 GRC9 graph checkpoints
  - 2 lifecycle events from the column-proxy near-zero fixture
- S0011 result:
  - 52 validated lanes
  - 46 motif candidates
  - 10 strong candidates
  - all 10 targeted diagnostic fixtures pass their lane-specific selectors
- Coarse/profile fixtures intentionally use zero simulation steps so that warm
  initial coarse caches remain visible; normal runtime steps invalidate the
  cache by design.

### Verification

- [x] Targeted fixture tests pass
- [x] Selector validation tests pass
- [x] Discovery tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator tests.discovery.test_grc9_selector_validation`
- [x] S0010 has replayable telemetry and checkpoint artifacts
- [x] S0011 has replayable selector report and manifest artifacts

### Summary

Iteration 6.2 is complete. S0010 adds field-backed diagnostic contrast fixtures
for the ambiguity classes reported by S0009, and S0011 verifies those fixtures
through saved telemetry selectors.

## Iteration 6.3. Complex All-Event Stability Probe

### Goal

Combine all event-producing GRC9 mechanisms into one complex graph and verify
that spark, expansion, growth, and fission-summary evidence remains present
under a few node and parameter perturbations.

### Checks

- [x] Add complex all-event fixture generator entrypoint
- [x] Include column-proxy spark component
- [x] Include instability spark component
- [x] Include growth pressure component
- [x] Include pre-registered fission component
- [x] Add node perturbation fixture
- [x] Add coherence perturbation fixture
- [x] Add runtime threshold perturbation fixture
- [x] Add runtime effective-degree perturbation fixture
- [x] Add `--complex-event-stability` runner mode
- [x] Capture replayable S0012 generated-run session
- [x] Add selector expectations for all complex lanes
- [x] Rerun selector validation with S0012 included as S0013
- [x] Record S0012 and S0013 in `ExperimentalLog.md`
- [x] Repair complex fixture topology after visual review found disconnected
  components
- [x] Capture connected replay as S0020 and mark S0012/S0013 complex visuals
  superseded for graph visualization

### Implementation Notes

- Implemented generator:
  - `src/pygrc/discovery/grc9_seed_generator.py`
  - `GRC9_COMPLEX_EVENT_STABILITY_NAMES`
  - `generate_grc9_complex_event_stability_fixture`
- Implemented runner flag:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0012 --complex-event-stability`
- Implemented selector replay:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id S0013 --source-session-id S0004 --source-session-id S0005 --source-session-id S0006 --source-session-id S0007 --source-session-id S0010 --source-session-id S0012`
- Connected topology repair:
  - S0012/S0013 remain historical selector artifacts
  - S0012 graph checkpoints are superseded for visualization because the
    original complex fixture regions were disconnected components
  - S0020 reruns the same fixture family with low-conductance bridge edges
    between regions
  - corrected replay command:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0020 --complex-event-stability`
- S0012 result:
  - 5 complex lanes
  - 30 total simulation steps
  - 35 GRC9 graph checkpoints
  - 406 event rows
  - every lane emitted at least two sparks, two expansions, growth, and
    confirmed fission-summary evidence
- S0013 result:
  - 57 validated lanes
  - 51 motif candidates
  - 10 strong candidates
  - all 5 complex fixtures pass all 6 lane-specific selectors
- S0020 connected replay result:
  - 5 complex lanes
  - 30 total simulation steps
  - 35 connected GRC9 graph checkpoints
  - 406 event rows
  - every lane retained spark, expansion, growth, and fission-summary evidence

### Verification

- [x] Complex fixture tests pass
- [x] Selector validation tests pass
- [x] Discovery tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator tests.discovery.test_grc9_selector_validation`
- [x] S0012 has replayable telemetry and checkpoint artifacts
- [x] S0013 has replayable selector report and manifest artifacts
- [x] S0020 has replayable connected telemetry, checkpoint, and visualization
  artifacts

### Summary

Iteration 6.3 is complete with a topology correction. The original S0012/S0013
selector evidence remains useful, but the disconnected S0012 graph visuals are
superseded by S0020. S0020 keeps the same all-event evidence while making every
saved checkpoint a connected GRC9 graph.

## Iteration 6.4. Discovery Harness Hardening

### Goal

Fix small implementation gaps in the discovery harness before moving review and
catalog work forward.

### Checks

- [x] Reject perturbation deltas on non-numeric seed parameters
- [x] Reject perturbations of unknown seed parameters
- [x] Validate planned lane step-count coverage before running a session
- [x] Add selector report fields for lanes without expectations
- [x] Add selector summary section for missing lane expectations
- [x] Re-run selector validation as S0015
- [x] Record S0015 in `ExperimentalLog.md`

### Implementation Notes

- Perturbation hardening:
  - `src/pygrc/discovery/grc9_seed_generator.py`
- Step-count coverage hardening:
  - `src/pygrc/discovery/grc9_discovery_runner.py`
- Selector expectation visibility:
  - `src/pygrc/discovery/grc9_selector_validation.py`
- S0015 replay:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id S0015 --source-session-id S0004 --source-session-id S0005 --source-session-id S0006 --source-session-id S0007 --source-session-id S0010 --source-session-id S0012`
- S0015 result:
  - 57 validated lanes
  - 51 motif candidates
  - 0 lanes without selector expectations

### Deferred

- Manifest mutation helpers belong to Iteration 8.
- Motif deduplication and cross-session linkage belong to Iteration 8.
- Port-structure population remains a future selector requirement, not a 6.4
  blocker.

### Verification

- [x] Focused hardening tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator tests.discovery.test_grc9_selector_validation`

### Summary

Iteration 6.4 is complete. The discovery harness now fails fast for unsupported
perturbations and missing step-count mappings, and selector reports make missing
lane expectations explicit.

## Iteration 7. Checkpoint Evidence And Visual Index

### Goal

Link motif windows to graph checkpoints and generated Phase V visual outputs.

### Checks

- [x] Build checkpoint index lookup by step
- [x] Link exact checkpoint ids to motif windows
- [x] Link nearest before/after checkpoints when exact matches are absent
- [x] Record missing exact checkpoint limitations
- [x] Build `visual_index.json`
- [x] Link visual artifacts only after telemetry evidence exists
- [x] Distinguish graph evidence from visual inspection aids
- [x] Write replayable S0014 checkpoint/visual index session
- [x] Record S0014 in `ExperimentalLog.md`
- [x] Export Iteration 7 helpers from `pygrc.discovery`
- [x] Use clear missing-file errors for top-level selector inputs
- [x] Skip and report malformed individual motif records
- [x] Keep nearest checkpoint step keys typed internally
- [x] Report missing checkpoint totals and nearest-distance summary
- [x] Record targeted-example availability in selector feedback
- [x] Write replayable S0016 checkpoint/visual hardening session
- [x] Write replayable S0017 selector-feedback availability session
- [x] Mark S0014/S0016/S0017 as historical after S0007/S0012 topology issue
  was found
- [x] Rebuild checkpoint/visual index from connected selector session S0022 as
  S0023
- [x] Rebuild selector feedback from connected selector session S0022 as S0024
- [x] Record S0023 and S0024 in `ExperimentalLog.md`

### Implementation Notes

- Spark, growth, and fission motifs usually need denser checkpoint cadence than
  coarse-graining or budget motifs.
- Checkpoint links should preserve whether the match is exact or nearest.
- Implemented module:
  - `src/pygrc/discovery/grc9_checkpoint_visual_index.py`
- Implemented replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_checkpoint_visual_index --session-id S0014 --selector-session-id S0013`
- S0014 input:
  - `outputs/grc9/phenomenology_discovery/sessions/S0013/selector_manifest.json`
- S0014 outputs:
  - `outputs/grc9/phenomenology_discovery/sessions/S0014/visual_index.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0014/reports/checkpoint_visual_index_report.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0014/reports/checkpoint_visual_index_summary.md`
- S0014 result:
  - 51 motif records indexed
  - 145 checkpoint links recorded
  - 0 records with missing exact checkpoint coverage
  - 51 records with `visual_status = not_rendered`
- Hardening implementation:
  - `src/pygrc/discovery/__init__.py` uses lazy exports for
    `run_grc9_checkpoint_visual_index` and `run_grc9_selector_feedback`
  - `src/pygrc/discovery/grc9_checkpoint_visual_index.py` now records
    `skipped_motifs`, `missing_exact_step_count`, and
    `nearest_distance_summary`
  - `src/pygrc/discovery/grc9_selector_feedback.py` now records
    `proposed_examples_available` and `proposed_examples_missing`
- S0016 replay:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_checkpoint_visual_index --session-id S0016 --selector-session-id S0015`
- S0016 result:
  - 51 motif records indexed
  - 145 checkpoint links recorded
  - 0 skipped motifs
  - 0 missing exact checkpoint steps
- S0017 replay:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_feedback --session-id S0017 --source-session-id S0015`
- S0017 result:
  - 11 feedback items
  - 5 diagnostic ambiguity families
  - all 10 proposed diagnostic examples available in S0015
- Connected replacement:
  - S0014, S0016, and S0017 remain historical/replayable, but they depended on
    selector surfaces that included disconnected S0007 and/or S0012 graph
    fixtures
  - S0023 replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_checkpoint_visual_index --session-id S0023 --selector-session-id S0022`
  - S0023 result:
    51 motif records, 145 checkpoint links, 0 skipped motifs, and 0 missing
    exact checkpoint steps
  - S0024 replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_feedback --session-id S0024 --source-session-id S0022`
  - S0024 result:
    11 feedback items, 6 covered lifecycle misses, and 5 diagnostic ambiguity
    families
- This iteration indexes saved checkpoint artifacts and existing visual
  artifacts only. It intentionally does not render new images.

### Verification

- [x] Every visual link has a corresponding telemetry window
- [x] Exact and nearest checkpoint matches are distinguished
- [x] Graph evidence limitations are explicit
- [x] No visual-only motif claims are introduced
- [x] Connected replacement index S0023 references S0021 and S0020 instead of
  disconnected S0007/S0012 graph fixtures
- [x] Connected replacement feedback S0024 references S0021 for combo coverage
- [x] Checkpoint/visual index tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_checkpoint_visual_index`
- [x] Selector feedback hardening tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_selector_feedback`

### Summary

Iteration 7 is complete with a connected-evidence replacement. S0014/S0016/S0017
remain historical, but S0023 and S0024 are the current graph-valid checkpoint
index and selector-feedback sessions because they are built from S0022, which
uses connected S0021 combo fixtures and connected S0020 complex fixtures.

## Iteration 8. Reviewed Motif Catalog

### Goal

Promote reviewed, validated candidates to a stable GRC9-native motif catalog.

### Checks

- [x] Define review statuses:
  - `unreviewed`
  - `candidate`
  - `weak_candidate`
  - `strong_candidate`
  - `accepted`
  - `rejected`
  - `duplicate`
  - `needs-rerun`
- [x] Implement or document review transition rules
- [x] Add immutable manifest update helpers
- [x] Record every status transition in `review_history`
- [x] Preserve rejected motifs with `rejection_reason`
- [x] Preserve duplicate motifs with duplicate target
- [x] Preserve `needs-rerun` motifs with `rerun_requested = true`
- [x] Promote accepted motifs into a stable motif catalog
- [x] Write replayable S0018 reviewed motif catalog session
- [x] Record S0018 in `ExperimentalLog.md`
- [x] Mark S0018 as historical after downstream topology issue was found
- [x] Rebuild reviewed motif catalog from connected selector session S0022 as
  S0025
- [x] Record S0025 in `ExperimentalLog.md`

### Implementation Notes

- Accepted motifs should normally have confidence score `5`; lower-score
  acceptance requires explicit reviewer override.
- Rejected motifs should remain queryable because they document failed
  mechanism hypotheses.
- Implemented manifest helpers:
  - `GRC9DiscoveryManifest.add_motif`
  - `GRC9DiscoveryManifest.update_motif`
  - `GRC9DiscoveryManifest.add_review_history`
- Implemented module:
  - `src/pygrc/discovery/grc9_reviewed_motif_catalog.py`
- Implemented replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_reviewed_motif_catalog --session-id S0018 --selector-session-id S0015`
- S0018 inputs:
  - `outputs/grc9/phenomenology_discovery/sessions/S0015/selector_manifest.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0015/reports/selector_validation_report.json`
- S0018 outputs:
  - `outputs/grc9/phenomenology_discovery/sessions/S0018/reviewed_manifest.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0018/reviewed_motif_catalog.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0018/reports/reviewed_motif_catalog_report.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0018/reports/reviewed_motif_catalog_summary.md`
- S0018 result:
  - 57 motifs reviewed
  - 57 review-history entries
  - 10 accepted motifs
  - 41 strong candidates
  - 6 rejected motifs
  - 0 duplicates
  - 0 needs-rerun records
- Review policy:
  - score `5` becomes `accepted` with confidence label
    `accepted_after_review`
  - score `4` becomes `strong_candidate`
  - rejected selector validations are restored as rejected motif records
  - duplicate structural signatures are preserved as `duplicate` with
    `notes.duplicate_of`
  - missing telemetry surfaces become `needs-rerun` with
    `rerun_requested = true`
- Review metadata:
  - `reviewer` and `review_timestamp_utc` are configurable runner/CLI
    parameters
  - the deterministic defaults remain `phase_i08_review_policy` and
    `2026-04-25T00:00:00Z`
- Duplicate semantics:
  - duplicate detection is structural-signature dedupe, not artifact-level
    dedupe
  - the current key is `(phenomenon, seed_name, predicted_evidence_fields)`
  - repeated artifacts of the same seed and predicted field family are
    duplicates; distinct seed names remain separate
- Connected replacement:
  - S0018 remains historical/replayable, but it was built from S0015, which
    depended on disconnected S0007/S0012 graph fixtures
  - S0025 replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_reviewed_motif_catalog --session-id S0025 --selector-session-id S0022`
  - S0025 result:
    57 motifs reviewed, 57 review-history entries, 10 accepted motifs,
    41 strong candidates, 6 rejected motifs, 0 duplicates, and 0 needs-rerun
    records

### Verification

- [x] Review history records every status transition
- [x] Rejected motifs include rejection reasons
- [x] Accepted motifs cite seed family, parameters, predicted evidence, and
  observed validation fields
- [x] Catalog contains only pure GRC9-native motifs
- [x] Current reviewed catalog S0025 is built from connected selector evidence
  S0022
- [x] Reviewed catalog tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_reviewed_motif_catalog`
- [x] Review policy tests use synthetic fixtures instead of depending on
  exact S0015 artifact counts
- [x] Full discovery suite passes:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog tests.discovery.test_grc9_seed_generator tests.discovery.test_grc9_selector_validation tests.discovery.test_grc9_selector_feedback tests.discovery.test_grc9_checkpoint_visual_index tests.discovery.test_grc9_reviewed_motif_catalog`

### Summary

Iteration 8 is complete with a connected-evidence replacement. S0018 remains
historical, while S0025 is the current reviewed motif catalog because it is
built from connected selector evidence in S0022. The accepted/strong/rejected
counts are preserved: 10 accepted motifs, 41 strong candidates, and 6 rejected
motifs.

## Iteration 9. GRCL-9 Translation Handoff

### Goal

Summarize accepted GRC9-native motifs for a later GRCL-9 translation plan
without implementing translation in this discovery track.

### Checks

- [x] Create `grcl9_suitability_catalog.md`
- [x] Create machine-readable `grcl9_suitability_catalog.json`
- [x] List accepted motif ids
- [x] List GRC9 graph preconditions
- [x] List seed families and seed parameters
- [x] List structural properties a future lowering would need to preserve
- [x] List telemetry fields that validated each motif
- [x] List explicit non-claims
- [x] State that no GRCL-9 lowering is implemented here
- [x] Write replayable S0019 GRCL-9 handoff session
- [x] Record S0019 in `ExperimentalLog.md`
- [x] Mark S0019 as historical after reviewed catalog S0018 was superseded
- [x] Rebuild GRCL-9 planning handoff from connected reviewed catalog S0025 as
  S0026
- [x] Record S0026 in `ExperimentalLog.md`

### Implementation Notes

- This handoff should start from reviewed GRC9-native motifs, not from
  hand-picked visualization images.
- The handoff artifact can discuss future lowering requirements, but must not
  claim that a source-language construct already exists.
- Implemented module:
  - `src/pygrc/discovery/grc9_grcl9_handoff.py`
- Implemented replay command:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_grcl9_handoff --session-id S0019 --reviewed-session-id S0018`
- S0019 input:
  - `outputs/grc9/phenomenology_discovery/sessions/S0018/reviewed_motif_catalog.json`
- S0019 outputs:
  - `outputs/grc9/phenomenology_discovery/sessions/S0019/grcl9_suitability_catalog.md`
  - `outputs/grc9/phenomenology_discovery/sessions/S0019/grcl9_suitability_catalog.json`
  - `outputs/grc9/phenomenology_discovery/sessions/S0019/reports/grcl9_handoff_report.json`
- S0019 result:
  - 10 accepted GRC9-native motifs included
  - 0 strong candidates included
  - 0 rejected motifs included
  - every motif cites seed family, seed parameter path, telemetry paths,
    observed validation fields, GRC9 graph preconditions, future preservation
    requirements, and explicit non-claims
- Connected replacement:
  - S0019 remains historical/replayable, but it was built from superseded
    reviewed catalog S0018
  - S0026 replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_grcl9_handoff --session-id S0026 --reviewed-session-id S0025`
  - S0026 result:
    10 accepted GRC9-native motifs included, 0 strong candidates included,
    0 rejected motifs included, and every motif remains marked as a future
    translation candidate after source-lowering design

### Verification

- [x] Handoff contains accepted motifs only
- [x] Handoff references telemetry validation fields
- [x] Handoff keeps GRCL-9 implementation out of scope
- [x] Handoff preserves GRC9 terminology
- [x] Current handoff S0026 is built from connected reviewed catalog S0025
- [x] Handoff tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_grcl9_handoff`
- [x] Full discovery suite passes:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_manifest tests.discovery.test_grc9_mechanism_ledger tests.discovery.test_grc9_hypothesis_catalog tests.discovery.test_grc9_seed_generator tests.discovery.test_grc9_selector_validation tests.discovery.test_grc9_selector_feedback tests.discovery.test_grc9_checkpoint_visual_index tests.discovery.test_grc9_reviewed_motif_catalog tests.discovery.test_grc9_grcl9_handoff`

### Summary

Iteration 9 is complete with a connected-evidence replacement. S0019 remains
historical, while S0026 is the current GRCL-9 planning handoff because it is
built from connected reviewed catalog S0025. It still makes no GRCL-9 lowering
claim and preserves the boundary that accepted motifs are native GRC9 mechanical
graph motifs.
