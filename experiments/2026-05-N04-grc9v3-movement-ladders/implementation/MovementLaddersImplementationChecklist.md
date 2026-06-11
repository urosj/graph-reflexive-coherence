# N04 Movement Ladders Implementation Checklist

This checklist tracks implementation of
`2026-05-N04-grc9v3-movement-ladders`.

Status keys:

```text
Pending     not started
In Progress work has begun
Complete    implemented, run, and recorded
Blocked     cannot proceed without a decision or upstream result
Deferred    intentionally postponed
```

## Global Constraints

- [ ] Keep N04 experiment-local unless a separate core task is opened.
- [ ] Stop before changing `src/*`.
- [ ] Treat N03/E3 as pulse-substrate evidence, not movement evidence.
- [ ] Keep topology disabled for first fixed-substrate movement tranches.
- [ ] Preserve exact budget, identity, and topology audits for every run.
- [ ] Record exact replay commands for every generated report.

## Iteration 0. Planning And Handoff Record

Status: Complete.

- [x] Create implementation plan.
- [x] Create implementation checklist.
- [x] Record N03/E3 handoff boundary.
- [x] Record that E3 heartbeat does not imply movement.
- [x] Link plan/checklist from implementation README.

Acceptance statement:

```text
N04 starts from a clean handoff: N03/E3 supplies a native LGRC9V3
self-rearming packetized pulse substrate, while movement remains unopened and
must be tested independently.
```

## Iteration 1. Hypothesis And Baseline Inventory

Status: Complete.

- [x] Create `hypotheses/movement_ladders_hypothesis_v1.md`.
- [x] Record null hypothesis for U0/B0.
- [x] Record movement-response hypothesis for B1/K1.
- [x] Record loop-driven movement hypothesis for E3 pulse lanes.
- [x] Inventory N03/E3 artifact paths used as input references.
- [x] Record baseline commands and environment.
- [x] Verify no `src/*` changes are needed.

Expected artifacts:

- [x] `hypotheses/movement_ladders_hypothesis_v1.md`
- [x] `outputs/n04_baseline_inventory.json`
- [x] `reports/n04_baseline_inventory.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_baseline_inventory.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_baseline_inventory.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_baseline_inventory.md", "status": "passed"}
```

Notes:

- The first local run exposed an incorrect repository-root calculation in the
  inventory script. The script was fixed before the successful recorded run.
- `git status --short src` returned no `src/*` status entries.
- N03/E3 is recorded as pulse-substrate evidence only:
  `movement_claim_inherited_from_n03 = false`.

## Iteration 2. Fixture Manifest And Metric Defaults

Status: Complete.

- [x] Define `S0_chain_v1`.
- [x] Define `S1_ring_v1`.
- [x] Record optional later `S3_grid_v1` scope.
- [x] Define lane manifests for U0, B0, B1, K1, and reversed controls.
- [x] Define metric defaults:
  - [x] `epsilon_budget`
  - [x] `configured_displacement_min`
  - [x] effective displacement threshold rule
  - [x] null-calibrated displacement envelope
  - [x] `identity_mass_ratio_min`
  - [x] `width_relative_change_max = 0.15`
  - [x] `profile_similarity_min = 0.8`
- [x] Define topology policy:
  - [x] `fixed_substrate_required = true`
  - [x] `topology_changed_required = false`
  - [x] `topology_changed_allowed = false`
- [x] Define coordinate policy:
  - [x] `node_coordinate_policy`
  - [x] `centroid_coordinate_frame`
  - [x] `coordinate_periodic`
  - [x] `ring_unwrap_policy`
- [x] Define front/rear direction source:
  - [x] packet route is reserved for later E3 pulse lanes
  - [x] centroid velocity is reserved for measured-direction observables
  - [x] configured direction is used by B1/B1 reversed
  - [x] perturbation direction is used by K1/K1 reversed
- [x] Add manifest validator.
- [x] Record validator command and output.

Expected artifacts:

- [x] `configs/movement_fixture_manifest_v1.json`
- [x] `outputs/movement_fixture_manifest_validation.json`
- [x] `reports/movement_fixture_manifest_validation.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_fixture_manifest.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_fixture_manifest_validation.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_fixture_manifest_validation.md", "status": "passed"}
```

Notes:

- `S0_chain_v1` and `S1_ring_v1` are active first-tranche fixtures.
- `S3_grid_v1` is declared but deferred until S0/S1 observables and classifier
  are validated.
- Ring centroid movement must use the declared `tracked_basin_representative`
  unwrap policy.
- Even-N ring antipodal ties use `negative_signed_distance_for_even_N`; this
  intentionally gives the uniform 24-node ring an unwrapped centroid of `-0.5`
  relative to center node `0`, so ring movement diagnostics compare against the
  symmetric baseline instead of absolute zero.
- Edge weights, base conductance, temporal delay, and proper-time delay are
  explicitly declared as unit defaults and per-edge fixture properties.
- B1/B1 reversed specify `bump_amplitude = 0.4` and `tilt_epsilon = 0.02`.
- K1/K1 reversed specify `kick_mask_node_count = 1`.
- Topology events remain disabled.

## Iteration 3. Initializers And Projection

Status: Complete.

- [x] Implement uniform initializer.
- [x] Implement symmetric canonical bump initializer.
- [x] Implement locally tapered asymmetric bump initializer.
- [x] Implement zero-sum kick initializer.
- [x] Implement conserved nonnegative projection.
- [x] Verify `sum_i C_i = B`.
- [x] Verify `C_i >= 0`.
- [x] Verify asymmetric tilt is locally tapered.
- [x] Verify reversed controls are deterministic.

Expected artifacts:

- [x] `scripts/validate_movement_initializers.py`
- [x] `outputs/movement_initializer_validation.json`
- [x] `reports/movement_initializer_validation.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_initializers.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_initializer_validation.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_initializer_validation.md", "status": "passed"}
```

Additional validation:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_fixture_manifest.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_fixture_manifest_validation.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_fixture_manifest_validation.md", "status": "passed"}
```

Notes:

- Projection uses conserved nonnegative simplex projection.
- Projection delta norm is reported per lane.
- Raw centroid, projected centroid, projection-induced centroid shift, and
  post-projection stimulus survival diagnostics are reported per lane.
- S0/S1 U0, B0, B1, B1 reversed, K1, and K1 reversed all preserve budget and
  nonnegativity.
- B1/B1 reversed centroid offsets have opposite signs relative to the
  symmetric B0 baseline.
- K1/K1 reversed centroid offsets have opposite signs relative to the
  symmetric B0 baseline.
- The first initializer validation exposed an invalid ring reversal check that
  used linear centroid offset from node 0. The validator now uses the declared
  tracked-basin unwrapped centroid and compares reversals to the symmetric B0
  baseline.

Iteration 1-3 lock summary:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_iteration_1_3_lock_summary.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iteration_1_3_lock_summary.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iteration_1_3_lock_summary.md", "status": "passed"}
```

Locked before Iteration 4:

- fixtures, lanes, metric defaults, initializer formulas, projection policy,
  coordinate/unwrap policy, claim flags, and no-`src/*` boundary.

## Iteration 4. Movement Observables

Status: Complete.

- [x] Add centroid observable.
- [x] Add support/boundary assignment observable.
- [x] Add boundary flip observable.
- [x] Add front/rear mask observable.
- [x] Add mass and width observable.
- [x] Add profile similarity observable.
- [x] Add front/rear curvature or Hessian proxy if available.
- [x] Add movement cost observable.
- [x] Add budget audit.
- [x] Add topology audit.
- [x] Add synthetic positive and negative tests.
- [x] Add identity-replacement negative test.
- [x] Add topology-changed apparent-displacement negative test.
- [x] Add ring wrap forward/reverse synthetic tests.
- [x] Add directional boundary flip decomposition.
- [x] Add observable-level reversal cross-check.
- [x] Emit explicit budget surface.
- [x] Emit identity candidate/gate thresholds separately.
- [x] Emit documented profile/support alignment windows.
- [x] Ensure time-series evidence is emitted for replay.

Expected artifacts:

- [x] `scripts/validate_movement_observables.py`
- [x] `outputs/movement_observables_validation.json`
- [x] `reports/movement_observables_validation.md`
- [x] `outputs/movement_observables_timeseries/*.jsonl`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_observables.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_observables_validation.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_observables_validation.md", "status": "passed"}
```

Notes:

- Synthetic traces validate observables only; they are not movement evidence.
- Centroid, support mask, mass, width, and budget are serialized as time-series
  evidence in JSONL artifacts.
- `null_static` rejects displacement.
- `uniform_jitter` rejects displacement and is treated as a no-basin/no-shape
  null rather than a movement support case.
- `shape_preserving_shift` passes displacement and shape gates on S0/S1.
- `reversed_shape_preserving_shift` verifies direction reversal on S0/S1.
- `boundary_reassignment_front_gain_rear_loss` verifies directional boundary
  decomposition, not only a total boundary-flip count.
- The forward/reverse shape-preserving synthetic pair is cross-checked for
  opposite displacement signs and matched boundary handoff evidence.
- `smeared_shift` fails shape gates even if ring antipodal convention crosses
  the displacement threshold.
- `basin_replacement` blocks movement promotion through identity failure even
  when apparent displacement exists.
- Identity levels now distinguish `I1_candidate_continuity` from
  `I2_gate_passed`; the gate threshold is the manifest
  `identity_mass_ratio_min = 0.95`.
- `conservation.budget_surface = node_only` is explicit for Iteration 4
  synthetic traces.
- Movement-cost per displacement is emitted as `null` when displacement is
  effectively zero, with `displacement_too_small_for_cost_ratio = true`.
- Profile alignment and support-identity alignment windows are serialized as
  `profile_alignment_max_shift = 6` and `identity_alignment_max_shift = 3`.
- `budget_drift` fails budget gates even when displacement is present.
- `topology_changed_apparent_displacement` blocks movement promotion through
  the fixed-substrate topology gate.
- `ring_wrap_forward` and `ring_wrap_reverse` validate that tracked-basin ring
  unwrap produces small stepwise displacement across the index boundary rather
  than a wrap artifact.
- Time-series JSONL artifacts are emitted for every synthetic case.
- All Iteration 4 claim flags remain false.

## Iteration 5. Fixed-Substrate Nulls And One-Time Response

Status: Complete.

- [x] Run U0 uniform field.
- [x] Run B0 symmetric basin bump.
- [x] Run B1 asymmetric basin bump.
- [x] Run K1 one-time zero-sum kick.
- [x] Run reversed B1/K1 controls.
- [x] Verify U0/B0 reject directed movement.
- [x] Verify B1/K1 claims are limited to movement response if gates pass.
- [x] Verify no loop-driven or locomotion-like claim is emitted.
- [x] Record budget, identity, topology, and shape gates.

Expected artifacts:

- [x] `scripts/run_fixed_substrate_tranche_a.py`
- [x] `outputs/fixed_substrate_tranche_a_report.json`
- [x] `reports/fixed_substrate_tranche_a_report.md`
- [x] `outputs/fixed_substrate_tranche_a_timeseries/*.jsonl`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_fixed_substrate_tranche_a.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/fixed_substrate_tranche_a_report.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/fixed_substrate_tranche_a_report.md", "status": "passed"}
```

Notes:

- The runner is `experiment_local_fixed_topology_diffusive_response_runner_v1`;
  this is not a native GRC9V3 or LGRC9V3 movement run.
- U0/B0 nulls reject directed movement on S0/S1.
- All budgets, topology gates, identity gates, and shape gates pass.
- The displacement threshold policy is frozen and serialized:
  `effective_displacement_min = max(configured_min, null_mean + k * null_std)`.
- The empirical null threshold is far below the configured minimum, so
  `configured_min` is the active threshold source for Iteration 5.
- The null envelope max is sourced by the S1 ring antipodal unwrap convention,
  not stochastic jitter.
- B1/B1 reversed show coherent opposite-sign subthreshold directional bias,
  but both remain below the effective displacement threshold.
- B1/B1 reversed diagnostic notes record that symmetric diffusion relaxes
  opposite the initial mass bias; this is not directed movement.
- The S1 B1/B1 reversed magnitude asymmetry is recorded as a below-threshold
  ring-unwrap interaction, not a movement effect.
- K1/K1 reversed kick audits show the one-time zero-sum stimulus was applied,
  survived projection, and still produced no threshold-level displacement.
- S1 K1/K1 reversed show same-sign tiny drift at the null floor and are
  recorded as `below_threshold_substrate_bias_possible`, not movement evidence.
- Lane reports now include `substrate` and `taxonomies` objects for
  `movement_ladder_report_v1` schema alignment.
- The first-tranche drive type `none_after_initialization` is defined in the
  manifest and plan.
- The diffusion runner records a nonnegativity guard and stability note.
- Iteration 5 markdown records Python environment, `git diff --check`, and
  `git status --short src experiments/.../N04`.
- No movement-response candidates were produced.
- No loop-driven movement, locomotion-like movement, adaptive-topology
  movement, or inherited N03 movement claim is emitted.
- First-tranche null displacement envelope is recorded in the report.

## Iteration 6. M0-M3 Classifier Freeze

Status: Complete.

- [x] Implement deterministic M0-M3 classifier.
- [x] Emit `blocked_claims`.
- [x] Emit primary blocked reason.
- [x] Verify budget failure blocks movement promotion.
- [x] Verify identity failure blocks movement promotion.
- [x] Verify shape failure blocks M3 promotion.
- [x] Verify M2 shape-blocked transition with an adversarial classifier case.
- [x] Verify nonnegative coherence failure as a hard blocker.
- [x] Verify boundary churn alone does not promote to M2.
- [x] Emit secondary gate failures for diagnostic transparency.
- [x] Freeze report schema v1 for early movement runs.

Expected artifacts:

- [x] `scripts/validate_movement_classifier.py`
- [x] `outputs/movement_classifier_m0_m3_validation.json`
- [x] `reports/movement_classifier_m0_m3_validation.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_classifier.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_classifier_m0_m3_validation.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_classifier_m0_m3_validation.md", "status": "passed"}
```

Notes:

- Classifier version: `movement_m0_m3_classifier_v1`.
- M0 means no threshold displacement or hard-gate blocked, with diagnostic
  subtypes preserving null, subthreshold bias, no-kick-response, budget,
  topology, and nonnegative-failure cases.
- M1 means apparent centroid displacement with budget/topology/nonnegative
  gates, but identity or boundary reassignment may fail.
- M2 means M1 plus identity and directed boundary reassignment, but shape may
  fail.
- M3 means M2 plus shape/profile gates passed.
- Budget, topology, and nonnegative coherence failures are hard blockers.
- Identity failure caps evidence at M1.
- Boundary churn without threshold displacement or coherent front/rear handoff
  is not M2. A classifier-adversarial case now verifies this with displacement
  and identity gates passing, so the blocker is boundary reassignment rather
  than displacement.
- Shape/profile failure caps evidence below M3.
- The M2 transition is now exercised by
  `iteration_6_adversarial_m2_shape_failure`, which reaches
  `M2_identity_preserving_displacement` and is blocked from M3 by
  `shape_gate_failed`.
- The nonnegative hard-blocker path is now exercised by
  `iteration_6_adversarial_nonnegative_failure`, producing
  `M0_nonnegative_failure`.
- Classifications now include `secondary_gate_failures` and
  `all_gate_failures`, so lower-priority failures remain visible when a
  higher-priority gate blocks promotion.
- Iteration 5 tranche A regression now requires any M0-level classification,
  rather than the single exact `M0_no_threshold_displacement` string.
- M0 subtype selection is driven by explicit diagnostic signals and lane/drive
  metadata where available, with `M0_no_threshold_response` as the fallback.
- Iteration 6 validates Iteration 4/5 movement-observable artifacts plus
  classifier-adversarial cases. Iteration 7 E3 pulse import is not a movement
  run and is validated separately.
- Iteration 5 fixed-substrate tranche A remains M0 for every lane.
- Iteration 5 B1/B1 reversed are preserved as
  `M0_subthreshold_directional_bias`.
- Iteration 5 paired controls are frozen:
  S0/S1 B1 pairs are `subthreshold_opposite_sign_bias`, S0 K1 is
  `no_threshold_response`, and S1 K1 is `possible_substrate_bias`.
- Movement claim flags remain false; this freezes evidence classification, not
  movement promotion policy.

## Iteration 7. E3 Pulse Import Adapter

Status: Complete.

- [x] Import or reproduce native LGRC9V3 E3 pulse metadata.
- [x] Record E3 source artifact paths.
- [x] Record `movement_claim_inherited = false`.
- [x] Record `runtime_family = LGRC9V3`.
- [x] Record `budget_surface = node_plus_packet`.
- [x] Record node budget, in-flight packet budget, and total budget.
- [x] Support pulse disabled control.
- [x] Support pulse active with boundary coupling disabled control.
- [x] Support pulse direction reversal control.
- [x] Support scrambled/non-self-rearming pulse control.
- [x] Verify pulse import does not modify movement state by itself.

Expected artifacts:

- [x] `scripts/validate_e3_pulse_import.py`
- [x] `outputs/e3_pulse_import_validation.json`
- [x] `reports/e3_pulse_import_validation.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_e3_pulse_import.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/e3_pulse_import_validation.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/e3_pulse_import_validation.md", "status": "passed"}
```

Notes:

- Iteration 7 imports the native LGRC9V3 E3 pulse as a drive candidate only.
- Imported E3 source classification is
  `E3_native_LGRC9V3_D2_3_equivalent_packet_loop` with loop ladder level `L5`.
- Positive clockwise and counter-clockwise E3 rows are present, each with
  `cycle_count = 3`, `self_rearm_count = 12`, fixed topology, and
  `max_event_budget_error = 0.0`.
- The movement state digest before and after import is unchanged; E3 import
  does not mutate N04 movement observables or classifier state.
- The import report uses `schema = movement_ladder_report_v1` and
  `report_kind = e3_pulse_import_validation_v1`, with claim ceiling
  `e3_pulse_import_validation_only`.
- `report_kind` is documented in the plan as a movement-report schema
  extension for validation/report subtypes.
- Pulse-disabled control loads E3 metadata but keeps pulse activation off;
  pulse-active/boundary-coupling-disabled control observes packet-loop activity
  but keeps boundary coupling off. Both controls leave movement state unchanged.
- Direction reversal and scrambled/non-self-rearming controls are available.
  Direction reversal now verifies structural pole-cycle reversal in addition
  to count symmetry.
- Required E3 control classes are available: no-surplus, subthreshold,
  threshold-too-high, wrong-direction, forward-only, broken-return, and
  scrambled-order.
- The adapter role is import/control definition only:
  `adapter_required_for_e3_pulse_semantics = false`,
  `adapter_trigger_used_as_execution_engine = false`, and direct boundary,
  support-mask, and centroid writes are all false.
- Iteration 5/6 fixed-substrate classification remains unchanged:
  `fixed_substrate_tranche_a_result = no_movement_response_candidates` and
  `movement_m0_m3_classifier_v1` remains frozen.
- Budget surface is recorded as `node_plus_packet`. The imported E3 closeout
  rows expose packet amount and per-event budget errors; exact node and
  in-flight packet totals are not serialized in those closeout rows, so
  Iteration 7 records that limitation rather than inventing totals.
- The import mutation audit is explicitly documented as read-only/no-op by
  design.
- Source artifacts are pinned by SHA-256, but the E3 source seed is not
  serialized in the imported closeout.
- A local pulse taxonomy P0-P5 is documented in the report and plan for
  Iteration 7 import classification.
- Route digest scopes are documented: `route_aspect_digest`,
  `pole_region_digest`, and `channel_sequence_digest`.
- The E3-to-N04 fixture compatibility gap is recorded: E3's positive pulse
  fixture is a 4-node route-aspect loop, while active N04 substrates are
  `S0_chain_v1` and `S1_ring_v1`. Iteration 8 must define this mapping before
  boundary coupling can be tested.
- Iteration 7-B may need additional E3 telemetry or reconstruction to validate
  exact node/in-flight budget split during geometry coupling.
- Movement, loop-driven movement, adaptive topology, locomotion-like, and
  N03-inherited movement claims remain blocked.

## Iteration 7-B. Packet-Loop Geometry Coupling Audit

Status: Complete.

- [x] Measure pole mass oscillation.
- [x] Measure node coherence changes near route vs off-route.
- [x] Measure edge delay/proper-time asymmetry where available.
- [x] Measure conductance/coupling changes where available.
- [x] Run E3 pulse active with boundary coupling disabled.
- [x] Verify pulse activity alone does not claim movement.
- [x] Verify no boundary displacement is directly scripted.
- [x] Record whether packet-loop activity changes movement-relevant geometry.
- [x] Record whether exact node/in-flight budget split is available or must be
  reconstructed from additional E3 telemetry.
- [x] Set claim ceiling to `packet_loop_geometry_coupling_audit`.

Expected artifacts:

- [x] `scripts/validate_packet_loop_geometry_coupling.py`
- [x] `outputs/packet_loop_geometry_coupling_audit.json`
- [x] `reports/packet_loop_geometry_coupling_audit.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_packet_loop_geometry_coupling.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/packet_loop_geometry_coupling_audit.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/packet_loop_geometry_coupling_audit.md", "status": "passed"}
```

Notes:

- E3 pulse telemetry shows movement-relevant state changes on the native
  four-node source fixture: pole coherence oscillates and node proper-time
  phases separate.
- The report separates three layers: native E3 source fixture, imported pulse
  telemetry, and N04 movement substrate. The positive finding is only on the
  first two layers; the N04 movement substrate remains unchanged.
- Exact node/in-flight packet budget split is available from E3 animation
  telemetry. Node budget ranges from `4.75` to `5.0`, in-flight packet budget
  ranges from `0.0` to `0.25`, total budget remains `5.0`, and max event and
  checkpoint budget errors are `0.0`.
- Proper-time phase separation is recorded as a timing-geometry surface:
  `proper_time_phase_separation_observed = true` with
  `final_node_proper_time_range = 3.0`.
- Edge delay and conductance audits are available as explicit negatives. Edge
  delays remain uniform, edge-delay asymmetry is not observed, and
  conductance/coupling does not change in the E3 source fixture.
- Near-route versus off-route comparison is marked unavailable, not failed,
  because all four source-fixture nodes are route nodes. This blocks
  route-localized geometry-coupling claims while allowing a route-wide pulse
  state-coupling audit.
- Boundary coupling remains disabled, no boundary/support/centroid writes are
  scripted, and pulse activity alone emits no movement, boundary-coupled
  movement, loop-driven movement, locomotion-like movement, adaptive-topology,
  or inherited-N03 movement claim.
- N04 movement-fixture state remains unchanged because the E3 four-pole route
  is still not mapped onto `S0_chain_v1` or `S1_ring_v1`.
- Iteration 8 entry is blocked until route-to-movement-substrate mapping is
  defined: `boundary_coupled_pulse_fixture_ready = false`.
- Iteration 8 must define the route-to-movement-substrate mapping before any
  boundary-coupled pulse fixture can be tested.

## Iteration 8. Boundary-Coupled Pulse Fixture

Status: Complete.

- [x] Define front/rear boundary masks.
- [x] Define mapping from the 4-node E3 route-aspect loop onto the N04 movement
  substrate before testing boundary coupling.
- [x] Define symmetric boundary-coupling null.
- [x] Define asymmetric boundary-coupling lane.
- [x] Confirm boundary coupling is state-mediated, not directly scripted.
- [x] Measure front advance mass.
- [x] Measure rear retraction mass.
- [x] Measure boundary coupling score.
- [x] Verify symmetric coupling does not produce net movement claim.
- [x] Verify coupling metrics are serialized.
- [x] Verify mapping is region-based and not node-id preserving.
- [x] Verify positive direction is frozen before the run.
- [x] Verify centroid response is replayable from serialized node coherence.
- [x] Verify forward/reverse coupling symmetry.
- [x] Set claim ceiling to `boundary_coupled_pulse_fixture_validation`.
- [x] Record that reversed Iteration 8 lane reverses coupling direction only,
  not E3 pulse telemetry direction.
- [x] Compare Iteration 8 displacement against the frozen Iteration 5
  effective displacement threshold.
- [x] Emit per-lane timeseries as JSONL with digest verification.
- [x] Use schema-aligned `budget_surface = node_only` for movement fixture
  lanes while keeping `e3_pulse_budget_surface = node_plus_packet`.
- [x] Document `coupling_strength = 0.5` rationale and sensitivity deferral.
- [x] Document that K2/S2 are mapped but unused by `coupling_signal_v1`.

Expected artifacts:

- [x] `configs/boundary_coupled_pulse_fixture_v1.json`
- [x] `scripts/run_boundary_coupled_pulse_fixture.py`
- [x] `outputs/boundary_coupled_pulse_report.json`
- [x] `reports/boundary_coupled_pulse_report.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_boundary_coupled_pulse_fixture.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_report.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/boundary_coupled_pulse_report.md", "status": "passed"}
```

Notes:

- The first route-to-substrate mapping is
  `e3_four_pole_to_s0_chain_boundary_v1`, targeting `S0_chain_v1`.
- The mapping is region-based rather than node-id preserving because E3 has
  four route nodes while `S0_chain_v1` has 21 movement-substrate nodes.
- E3 route poles map to S0 regions:
  `S1 -> [10]`, `K2 -> [11, 12]`, `S2 -> [13, 14]`, and `K1 -> [6, 7]`.
- Boundary masks are explicit: front `[13, 14]`, rear `[6, 7]`, center
  reservoir `[9, 10, 11]`.
- Positive direction is frozen as increasing `S0_chain_v1` index, with
  `direction_source = mapped_e3_route`.
- Coupling is state-mediated through mapped E3 pole coherence signal. The
  fixture changes movement node coherence only; it does not directly write
  support masks, centroids, displacement, or topology.
- Pulse-disabled control is negative.
- Symmetric boundary-coupling null is negative for net displacement:
  `dX ~= 0`.
- Asymmetric forward coupling is measurable:
  `front_advance_mass = 0.25`, `rear_retraction_mass = 0.25`,
  `boundary_coupling_score = 0.25`, and `dX = 0.083333333`.
- Reversed asymmetric coupling reverses centroid sign:
  `dX = -0.083333333`, with reversed boundary coupling score `0.25`.
- The reversed asymmetric lane reverses coupling direction only and reuses the
  same positive E3 pulse telemetry. A true reversed-E3-pulse lane is deferred
  to Iteration 9.
- The frozen Iteration 5 effective displacement threshold is `0.05`; the
  Iteration 8 max absolute centroid delta is `0.083333333`. This threshold
  comparison is recorded for audit only because M4/M5 classification is still
  deferred.
- The `0.25` boundary mass transfer is both the configured coupling quantum
  and the measured front/rear exchange in the asymmetric lanes.
- The symmetric null has nonzero front+rear boundary mass accumulation because
  it redistributes mass from the center reservoir to both boundaries; this is
  not a conservation error and does not create net displacement.
- Per-lane timeseries are stored under
  `outputs/boundary_coupled_pulse_timeseries/*.jsonl`; the report stores paths
  and verifies each digest.
- `budget_surface` is `node_only` for the movement fixture lanes, with the
  imported E3 pulse source separately marked as `node_plus_packet`.
- `coupling_strength = 0.5` is documented as a first fixture-validation value
  chosen to create measurable bounded coupling. Sensitivity analysis is
  deferred.
- K2 and S2 are mapped for route completeness and later multi-pole coupling
  designs, but `coupling_signal_v1` uses only S1 and K1.
- Centroid displacement is recomputed from serialized node coherence for every
  lane; the adapter does not write centroid or displacement values.
- The report records `primary_blocked_reason =
  movement_classification_deferred_to_iteration_9`.
- Budget and nonnegative gates pass for all lanes.
- Movement, boundary-coupled movement, loop-driven movement, locomotion-like
  movement, adaptive-topology, and inherited-N03 claims remain blocked.
- `S1_ring_v1` pulse-boundary mapping remains deferred because it needs a
  separate unwrap/front-rear policy.
- Iteration 8 measures the fixture and coupling surface only. M4/M5 movement
  classification remains Iteration 9 work.

## Iteration 9. Loop-Driven Movement Classifier M4-M5

Status: Complete.

- [x] Implement M4 gate for coordinated front/rear boundary change.
- [x] Implement M5 gate for repeated loop-driven displacement.
- [x] Verify E3 pulse remains budget-conserving in movement context.
- [x] Verify pulse disabled control remains negative.
- [x] Verify symmetric boundary null remains negative.
- [x] Verify reversed coupling direction reverses response while recording that
  true reversed-E3-pulse telemetry is unavailable.
- [x] Verify scrambled pulse order blocks loop-driven movement.
- [x] Keep full movement and loop-driven movement claims blocked when required
  direction-parity controls are incomplete.

Expected artifacts:

- [x] `scripts/classify_loop_driven_movement_m4_m5.py`
- [x] `outputs/loop_driven_movement_m4_m5_report.json`
- [x] `reports/loop_driven_movement_m4_m5_report.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/classify_loop_driven_movement_m4_m5.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/loop_driven_movement_m4_m5_report.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/loop_driven_movement_m4_m5_report.md", "status": "passed"}
```

Notes:

- The classifier finds M5-style repeated boundary-response candidates in the
  asymmetric forward and coupling-reversed lanes.
- Forward lane: `dX = 0.083333333`, distinct pulse-locked response count `4`,
  response window `12.0`, M4/M5 candidate gates pass.
- Coupling-reversed lane: `dX = -0.083333333`, distinct pulse-locked response
  count `4`, response window `12.0`, M4/M5 candidate gates pass.
- Diagnostic threshold-sample counts are also retained (`31` forward, `37`
  coupling-reversed), but persistent samples on a plateau are counted as one
  distinct pulse-locked response window for the M5 candidate gate.
- Pulse-disabled and symmetric boundary-coupling null lanes remain negative.
- Scrambled-order control blocks loop-driven movement despite reusing the
  magnitude profile.
- Scrambled-order is recorded as a synthetic classifier sanity check, not an
  empirical scrambled telemetry fixture lane. The empirical scrambled-pulse
  fixture remains deferred.
- Control blockers are recorded separately: pulse disabled, balanced front/rear
  coupling, and scrambled loop order.
- Coupling reversal symmetry passes, but its scope is coupling-direction
  reversal only and does not use reversed E3 telemetry.
- Native true reversed-E3-pulse telemetry is not available in the current
  artifact set. This blocks full direction-parity support.
- Claim ceiling is `m5_candidate_control_limited`.
- The report includes schema-required `budget_surface = node_only`,
  `native_grc9v3_proposal_flux_loop_claim = false`, and
  `native_grc9v3_proposal_flux_control_used = false`.
- Pulse-locked window detection derives its coupling threshold as
  `0.9 * max_observed_coupling` per lane, rather than using an absolute magic
  number.
- Response threshold comparisons use `response_threshold_epsilon = 1e-12` to
  avoid threshold-edge floating-point asymmetry.
- The M4/M5 gates are documented as a boundary-response ladder, not a
  replacement for the M0-M3 identity/shape ladder. A full movement claim would
  require both identity/shape support and completed M4/M5 direction-parity
  controls.
- The distinct pulse-locked window count is documented as coupled to the E3
  pulse-cycle structure. It validates repeated pulse-locked response, not
  substrate response between pulses or post-pulse persistence.
- Window deduplication currently uses telemetry `time`; co-temporal distinct
  pulse peaks would be collapsed by this policy, though current E3 peak windows
  occur at distinct times.
- The report records the SHA-256 of the corrected Iteration 8 boundary report
  it consumed and verifies that external JSONL timeseries are available.
- `movement_claim_allowed`, `boundary_coupled_movement_claim_allowed`, and
  `loop_driven_movement_claim_allowed` remain `false`.
- Locomotion-like, adaptive-topology, biological, agency, and inherited-N03
  claims remain blocked.

## Iteration 10. Self-Renewing Movement Candidate M6

Status: Complete, fail-closed.

- [x] Open only if full M5 movement support passes, including required
  direction-parity controls.
- [x] Measure whether movement restores pulse-generating conditions.
- [x] Measure polarity regeneration.
- [x] Measure repeated-cycle persistence window.
- [x] Measure bounded movement cost.
- [x] Verify identity continuity reaches required threshold.
- [x] Keep biological/agency claims blocked.

Result:

```text
status = passed_fail_closed
claim_ceiling = m6_not_opened_feedback_path_absent
m6_opened = false
m6_gate_passed = false
primary_blocker = no_feedback_path_from_boundary_response_to_pulse_generation
```

Interpretation:

```text
Lane B supplies native direction-parity-controlled repeated boundary response,
but the S0 boundary fixture consumes E3 pulse telemetry without feeding the
boundary response back into native E3 surplus-trigger or pulse-generating
conditions. Repeated boundary-response windows are pulse-driven, not
self-renewed by movement. M6, locomotion-like, adaptive-topology, biological,
agency, and inherited-N03 claims remain blocked.
```

Expected artifacts:

- `outputs/self_renewing_movement_candidate_report.json`
- `reports/self_renewing_movement_candidate_report.md`

## Iteration 11. Visualization And Replay

Status: Complete, visual reference generated.

Iteration 11 renders a shareable M-taxonomy visual reference pack for the best
available M0-M6 candidates. These visuals are supporting references only; they
do not promote claims or change the current N04 ceiling.

Iteration 11 question:

```text
Can N04 provide a compact visual reference for the best current M0-M6
candidates, while preserving the provenance boundary between experiment-local
fixtures, classifier-adversarial evidence, mapped E3 boundary fixtures, and
native LGRC9V3 same-fixture replay?
```

Result:

```text
status = passed
visual_count = 7
claim_boundary = visual_reference_only_claims_come_from_n04_reports_not_from_visuals
current_gap = M0-M4 lack native LGRC telemetry packs; M2 runtime gap cleared in Iteration 11-B
native_lgrc_visuals = M5 and M6
```

Evidence cleared:

- [x] M0 visual rendered from fixed-substrate subthreshold B1 timeseries.
- [x] M1 visual rendered from existing apparent-centroid/identity-blocked
  observable fixture.
- [x] M2 visual initially rendered from the adversarial classifier case and
  marked as lacking a runtime timeseries/native visual artifact.
- [x] M3 visual rendered from existing shape-preserving identity-displacement
  observable fixture.
- [x] M4 visual rendered from existing boundary-coupled pulse fixture
  timeseries.
- [x] M5 native LGRC9V3 telemetry pack generated for true-reversed E3 boundary
  response and rendered through the standard `pygrc.visualization` run bundle.
- [x] M6 native LGRC9V3 telemetry pack generated from a same-fixture replay
  using native causal pulse-substrate surface and feedback producer logic, then
  rendered through the standard `pygrc.visualization` run bundle.
- [x] Index HTML and SVG reference panels emitted for sharing.
- [x] Manifest records claim boundary, source artifacts, evidence status,
  native telemetry paths, visual paths, and per-rung implementation surface.

Expected artifacts:

- [x] `scripts/render_m_taxonomy_visual_reference.py`
- [x] `outputs/m_taxonomy_visual_reference.json`
- [x] `outputs/m_taxonomy_visual_reference/manifest.json`
- [x] `outputs/m_taxonomy_visual_reference/index.html`
- [x] `outputs/m_taxonomy_visual_reference/*.svg`
- [x] `outputs/m_taxonomy_native_lgrc_runs/*/telemetry/*.json*`
- [x] `outputs/m_taxonomy_visual_reference/native_lgrc_visualizations/*/visualization/*.png`
- [x] `reports/m_taxonomy_visual_reference.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/render_m_taxonomy_visual_reference.py
```

Result:

```json
{"status": "passed", "visual_count": 7, "index": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/m_taxonomy_visual_reference/index.html"}
```

Acceptance statement:

```text
Iteration 11 creates a visual reference pack for M0-M6 without promoting
claims. M0, M1, M3, and M4 render from existing N04 timeseries/reference
artifacts. M5 and M6 now have generated native LGRC9V3 telemetry packs and
standard pygrc visualization outputs. The initial pack identified M2 as the
remaining weak visual rung; Iteration 11-B below replaces that card with a
runtime shape-blocked timeseries. The pack is suitable as a sharing reference,
with the claim boundary preserved.
```

## Iteration 11-B. M2 Runtime Shape-Blocked Fixture

Status: Complete.

Iteration 11-B resolves the weak M2 visual rung by generating an actual
runtime-style S0 timeseries that classifies as M2 under the frozen M0-M3
classifier.

Result:

```text
status = passed
movement_level = M2_identity_preserving_displacement
diagnostic_subtype = M2_boundary_reassignment_shape_blocked
primary_blocked_reason = shape_gate_failed
claim_ceiling = M2_identity_preserving_displacement_evidence_only
```

Evidence cleared:

- [x] Runtime timeseries emitted for `S0_chain_v1_M2_shape_degraded_boundary_handoff`.
- [x] Budget, displacement, identity, topology, and directed boundary
  reassignment gates pass.
- [x] Shape gate fails by profile similarity, so M3 remains blocked.
- [x] Movement and broader claim flags remain blocked.
- [x] Visual reference pack regenerated so M2 uses the new runtime timeseries
  instead of the classifier-adversarial card.

Metrics:

```text
centroid_displacement = 0.17167957557684588
effective_displacement_min = 0.05
front_entered_mass = 3.3150981035444347
rear_left_mass = 1.034370396895702
identity_mass_ratio_min = 1.0
width_relative_change_max = 0.008893340751886612
profile_similarity_aligned = 0.7614634487196019
profile_similarity_min = 0.8
```

Expected artifacts:

- [x] `scripts/run_m2_runtime_shape_blocked_fixture.py`
- [x] `outputs/m2_runtime_shape_blocked_fixture.json`
- [x] `outputs/m2_runtime_shape_blocked_timeseries/M2_shape_degraded_boundary_handoff.jsonl`
- [x] `reports/m2_runtime_shape_blocked_fixture.md`
- [x] regenerated `outputs/m_taxonomy_visual_reference.json`
- [x] regenerated `reports/m_taxonomy_visual_reference.md`

Run records:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_m2_runtime_shape_blocked_fixture.py
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/render_m_taxonomy_visual_reference.py
```

Acceptance statement:

```text
Iteration 11-B provides replayable runtime-style M2 evidence. The S0 lane
passes budget, displacement, identity, topology, and directed boundary
reassignment while failing the profile similarity shape gate. The frozen
classifier labels the lane M2_identity_preserving_displacement with
shape_gate_failed as the blocker. The result does not promote M3 or any
movement-like claim, and the visual reference pack now uses the M2 runtime
timeseries.
```

## Iteration 12. Tranche Closeout And Taxonomy-Handoff Decision

Status: Complete.

Iteration 12 closes the initial N04 fixed-substrate movement-ladder tranche and
hands off to Iterations 13-19 for movement-taxonomy/topology search. It is a
boundary marker, not the end of N04.

- [x] Write initial N04 tranche closeout.
- [x] Record strongest current ceiling:
  `native_m6_same_fixture_self_renewal_candidate`.
- [x] Record that `native_m6 = true` only for the bounded same-fixture
  candidate; movement, locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, and unrestricted movement claims remain
  blocked.
- [x] Preserve M0-M6 source-of-truth artifact pointers, including Iteration
  11-B M2 runtime evidence and the visual reference pack.
- [x] Open Iterations 13-19 as the next taxonomy/topology search sequence.
- [x] State that adaptive topology remains blocked until Iterations 13-19 earn
  it under explicit topology controls.
- [x] If core changes are needed, open a separate implementation task rather
  than editing them inside N04 closeout.
- [x] Decide whether output cleanup is needed after replay is preserved.

Expected artifacts:

- [x] `reports/n04_initial_tranche_closeout.md`
- [x] `outputs/n04_initial_tranche_closeout.json`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_initial_tranche_closeout.py
```

Result:

```json
{"next_iteration": "13_taxonomy_inventory", "status": "passed"}
```

Acceptance statement:

```text
Iteration 12 closes the initial N04 fixed-substrate/M0-M6 tranche and opens
Iterations 13-19 as a movement-taxonomy/topology search sequence. The closeout
preserves the bounded native M6 same-fixture candidate and the M0-M6 evidence
ladder, but it does not permit adaptive-topology, locomotion-like, biological,
agency, identity-acceptance, inherited-N03, or unrestricted movement claims.
```

## Lane A. Retrospective Evidence Clearing

Lane A is a retrospective analysis lane opened after Iteration 9 reached the
current claim ceiling. It does not replace Iterations 1-12 and does not open
Iteration 10. Its purpose is to clear evidence from M0 upward using the frozen
reports and gates.

### A1. Evidence Ladder Audit

Status: Complete.

- [x] Inventory all Iteration 1-9 artifacts used by the audit.
- [x] Re-state the frozen N04 claim boundary:
  - [x] N03/E3 heartbeat is pulse-substrate evidence, not movement evidence.
  - [x] movement claims are not inherited from N03.
  - [x] Iteration 10/M6 remains blocked.
- [x] Reclassify M0/M1 fixed-substrate evidence:
  - [x] U0 and B0 nulls.
  - [x] B1/B1 reversed subthreshold directional bias.
  - [x] K1/K1 reversed no threshold-level response.
- [x] Reclassify M2/M3 identity and shape evidence:
  - [x] identity/shape gates passed where applicable.
  - [x] no identity-preserving displacement claim from fixed-substrate lanes.
- [x] Reclassify Iteration 8 boundary-coupling fixture evidence:
  - [x] region-based E3-to-S0 mapping.
  - [x] state-mediated node-coherence coupling.
  - [x] no direct support/centroid/displacement/topology writes.
  - [x] fixture-level positive, not movement.
- [x] Reclassify Iteration 9 M4/M5 candidate evidence:
  - [x] distinct pulse-locked response windows.
  - [x] pulse-disabled, symmetric-null, and scrambled-order controls.
  - [x] coupling-reversal scope limited to coupling direction.
  - [x] true reversed-E3-pulse telemetry missing.
- [x] Emit allowed evidence labels and blocked claim labels.
- [x] Identify the next evidence gap:
  - [x] native true reversed-E3-pulse telemetry direction parity, or
  - [x] close current N04 tranche as `M5_candidate_control_limited`.

Expected artifacts:

- [x] `scripts/build_n04_evidence_ladder_audit.py`
- [x] `outputs/n04_evidence_ladder_audit.json`
- [x] `reports/n04_evidence_ladder_audit.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_evidence_ladder_audit.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_evidence_ladder_audit.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_evidence_ladder_audit.md", "status": "passed"}
```

Notes:

- Allowed evidence labels are `fixed_substrate_negative`,
  `subthreshold_directional_bias`,
  `state_mediated_boundary_coupling_fixture_positive`, and
  `m5_candidate_control_limited`.
- Fixed-substrate lanes remain movement-negative, with B1/B1 reversed preserved
  as subthreshold directional bias.
- Iteration 8 remains fixture-positive only.
- Iteration 9 remains `m5_candidate_control_limited`.
- Full movement, boundary-coupled movement, loop-driven movement,
  locomotion-like, adaptive-topology, M6, biological, agency, and inherited-N03
  claims remain blocked.
- Next evidence gap is native true reversed-E3-pulse direction parity, or the
  current tranche can be closed as `M5_candidate_control_limited`.

Acceptance statement:

```text
Lane A1 clears the existing N04 evidence ladder without promoting new claims:
fixed-substrate lanes remain movement-negative, Iteration 8 remains a
state-mediated boundary-coupling fixture positive, Iteration 9 remains an
M5-style candidate/control-limited result, and full movement, loop-driven
movement, locomotion-like, adaptive-topology, M6, biological, agency, and
inherited-N03 claims remain blocked.
```

### A2. Post-Lane-B / Post-Iteration-10 Review

Status: Complete.

- [x] Preserve A1 fixed-substrate and Iteration 8 classifications.
- [x] Promote the Iteration 9 ceiling from `m5_candidate_control_limited` to
  Lane B's locked `m5_direction_parity_supported_boundary_response`.
- [x] Record true reversed-E3 telemetry direction parity as resolved for the
  S0 boundary-response fixture.
- [x] Fold Iteration 10 into the ladder as
  `m6_not_opened_feedback_path_absent`.
- [x] Keep movement, boundary-coupled movement, loop-driven movement,
  locomotion-like, adaptive-topology, M6, biological, agency, and inherited-N03
  claims blocked.

Expected artifacts:

- [x] `scripts/build_n04_lane_a_post_iteration10_review.py`
- [x] `outputs/n04_lane_a_post_iteration10_review.json`
- [x] `reports/n04_lane_a_post_iteration10_review.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_lane_a_post_iteration10_review.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_lane_a_post_iteration10_review.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_lane_a_post_iteration10_review.md", "status": "passed"}
```

Acceptance statement:

```text
Lane A2 updates the retrospective evidence ladder after Lane B and Iteration
10. Lane B is promoted from control-limited M5 candidate to
direction-parity-supported boundary response. Iteration 10 then fails closed
for M6 because the S0 boundary response does not feed back into native E3
pulse-generating conditions. The strongest current N04 ceiling is
m5_direction_parity_supported_boundary_response with M6 blocked.
```

### A3. Iteration 10 Failure Review

Status: Complete.

- [x] Review Iteration 10 as a failure, not only as a blocked claim.
- [x] Separate gates that passed before failure:
  - [x] Lane B locked baseline available.
  - [x] Direction-parity-supported boundary response available.
  - [x] Repeated boundary-response windows measured.
  - [x] Bounded boundary-fixture cost measured.
  - [x] Identity continuity passed for the boundary fixture.
  - [x] Shape/economy gates passed for the boundary fixture.
- [x] Identify the failed M6 gates:
  - [x] no feedback path from S0 movement substrate to native E3 producer;
  - [x] movement does not restore pulse-generating conditions;
  - [x] polarity regeneration is not measured;
  - [x] repeated windows are pulse-schedule-driven, not self-renewed.
- [x] Record that the failure is not due to budget, identity, shape/economy, or
  direction-parity failure.
- [x] Record the mechanism needed to reopen M6:
  movement-substrate state must feed back into pulse-generation conditions.

Expected artifacts:

- [x] `scripts/build_n04_iteration10_failure_review.py`
- [x] `outputs/n04_iteration10_failure_review.json`
- [x] `reports/n04_iteration10_failure_review.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_iteration10_failure_review.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iteration10_failure_review.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iteration10_failure_review.md", "status": "passed"}
```

Acceptance statement:

```text
Iteration 10 failed for the right reason: the current fixture has
direction-parity-supported repeated boundary response, but no feedback from the
S0 movement substrate back into native E3 pulse-generating conditions. Budget,
identity, shape/economy, and direction parity were not the limiting failures.
The limiting failure is causal closure of the drive loop.
```

## Lane B. True Reversed-E3-Pulse Direction Parity

Lane B is the direct blocker-clearing lane after Lane A. Iteration 9 reached
`M5_candidate_control_limited` because coupling-direction reversal was
available, but native true reversed-E3-pulse telemetry was not available in the
artifact set. Lane B tests that specific missing control before opening broader
mechanism work.

```text
Current blocker:
    native true reversed-E3-pulse telemetry unavailable

Lane B question:
    Does true reversed E3 telemetry produce direction-parity behavior through
    the existing Iteration 8 S0 boundary-coupled fixture under frozen Iteration
    9 M4/M5 gates?
```

Claim boundary:

```text
Lane B tests M5 direction parity, not M6.
The safe promotion target is m5_direction_parity_supported_boundary_response,
not unrestricted movement.
Movement, locomotion-like, adaptive topology, biological, and agency claims
remain blocked.
```

Lane B result:

```text
status = passed
claim_ceiling = m5_direction_parity_supported_boundary_response
true_reversed_e3_telemetry_available = true
lock_audit_status = passed
movement_claim_allowed = false
loop_driven_movement_claim_allowed = false
Iteration 10/M6 remains blocked
```

Lane B lock:

```text
status = locked
locked_on = 2026-05-16
lock_artifact = outputs/n04_lane_b_lock_audit.json
lock_report = reports/n04_lane_b_lock_audit.md
acceptance = m5_direction_parity_supported_boundary_response
movement_claim_allowed = false
m6_opened = false
```

### B1. Locate Or Generate Reversed-E3 Telemetry

Status: Complete.

- [x] Locate existing native counter-clockwise or pole-reversed E3 telemetry.
- [x] If absent, generate native reversed-E3-pulse telemetry from the N03/E3
  native LGRC9V3 runtime path.
- [x] Verify reversed telemetry has native LGRC9V3 packet-loop status:
  `native_lgrc9v3_execution = true`,
  `native_d2_3_equivalent = true`,
  `native_self_rearm_evidence = true`.
- [x] Verify route order is structurally reversed, not only count-symmetric.
- [x] Verify node-plus-packet budget conservation and topology unchanged.
- [x] Record source artifacts, commands, digests, runtime family, and seed if
  available.
- [x] If reversed telemetry cannot be produced, record that blocker and route
  N04 toward Iteration 12 closeout as `M5_candidate_control_limited`.

Expected artifacts:

- `outputs/reversed_e3_pulse_telemetry_validation.json`
- `reports/reversed_e3_pulse_telemetry_validation.md`

### B2. Run Reversed Telemetry Through Boundary Fixture

Status: Complete.

- [x] Use the existing Iteration 8
  `e3_four_pole_to_s0_chain_boundary_v1` fixture.
- [x] Replace coupling-direction reversal with true reversed-E3 pulse telemetry.
- [x] Preserve the same S0 substrate, mapping, coupling strength, thresholds,
  response window policy, and frozen Iteration 9 gates.
- [x] Verify no direct support, boundary, centroid, displacement, topology, or
  claim writes.
- [x] Verify S0 movement-fixture budget is `node_only` and the E3 source budget
  remains `node_plus_packet`.
- [x] Verify pulse-disabled, symmetric-null, and scrambled-order controls remain
  negative or are explicitly carried forward by digest.

Expected artifacts:

- `outputs/reversed_e3_pulse_boundary_coupling_report.json`
- `reports/reversed_e3_pulse_boundary_coupling_report.md`

### B3. Frozen M4/M5 Direction-Parity Classification

Status: Complete.

- [x] Classify the true reversed-E3 lane with frozen Iteration 9 M4/M5 gates.
- [x] Verify opposite-sign displacement relative to forward E3 telemetry.
- [x] Verify matched or tolerance-bounded boundary coupling score.
- [x] Verify distinct pulse-locked window count and response window are
  comparable to the forward lane.
- [x] Verify response-count policy remains derived from coupling policy, not a
  hard-coded peak threshold.
- [x] Verify report distinguishes:
  `M5_candidate_gate_passed`,
  `M5_full_direction_parity_gate_passed`, and
  final claim ceiling.

Expected artifacts:

- `outputs/reversed_e3_pulse_m4_m5_classification.json`
- `reports/reversed_e3_pulse_m4_m5_classification.md`

### B4. Lane B Closeout Decision

Status: Complete.

- [x] If true reversed-E3 direction parity passes, update the N04 ceiling to
  `m5_direction_parity_supported_boundary_response`.
- [x] If true reversed-E3 telemetry is unavailable or fails parity, preserve
  `m5_candidate_control_limited`.
- [x] Keep `movement_claim_allowed = false` unless the closeout explicitly
  integrates M0-M3 identity/shape movement gates with the M4/M5 boundary
  response result.
- [x] Keep Iteration 10/M6 blocked unless full M5 movement support is opened by
  a separate closeout decision.

Expected artifacts:

- `outputs/n04_lane_b_direction_parity_closeout.json`
- `reports/n04_lane_b_direction_parity_closeout.md`
- `outputs/n04_lane_b_lock_audit.json`
- `reports/n04_lane_b_lock_audit.md`

## Lane C. Feedback-Coupled Pulse Regeneration

Status: Complete, experiment-local candidate.

Lane C is the targeted unlock lane for Iteration 10. It starts from the locked
Lane B boundary-response fixture and asks whether S0 movement-substrate state
can feed back into pulse-generation conditions. This lane does not reopen the
failed Iteration 10 result in place; it defines the missing mechanism required
to run a new M6 gate.

Lane C question:

```text
Can boundary response change runtime-visible pulse eligibility or polarity
state so that the next pulse is generated from the changed movement substrate,
not from the pre-existing E3 schedule?
```

Claim boundary:

```text
Lane C tests feedback-coupled pulse regeneration.
It does not claim movement, locomotion-like dynamics, biology, or agency.
M6 can reopen only if the feedback path is serialized, budget-conserving,
artifact-replayable, and control-passing.
```

Lane C result:

```text
status = passed
claim_ceiling = m6_feedback_coupled_self_renewal_candidate
m6_feedback_candidate_gate_passed = true
feedback_adapter_scope = experiment_local
native_feedback_producer = false
movement_claim_allowed = false
loop_driven_movement_claim_allowed = false
locomotion_like_claim_allowed = false
adaptive_topology_entry_allowed = false
```

### C1. Feedback Contract

Status: Complete.

- [x] Define the feedback path from S0 movement-substrate state to pulse
  eligibility.
- [x] Declare the runtime-visible state read by the feedback path:
  boundary mass, support mass, polarity score, surplus proxy, or another
  serialized surface.
- [x] Declare which pulse-generation condition is affected:
  surplus threshold, reference mass, route-aspect polarity, producer
  eligibility, or pulse schedule gate.
- [x] Verify feedback reads serialized movement-substrate state, not hidden
  fixture internals.
- [x] Verify feedback does not directly write support masks, centroids,
  displacement, topology, or claim flags.
- [x] Declare budget surface and mutation owner.
- [x] Claim ceiling: `feedback_contract_defined`.

Expected artifacts:

- [x] `configs/feedback_coupled_pulse_regeneration_v1.json`
- [x] `outputs/feedback_contract_validation.json`
- [x] `reports/feedback_contract_validation.md`

### C2. Post-Boundary Response Pulse-Condition Restoration

Status: Complete.

- [x] Run the Lane B boundary-response fixture with feedback measurement
  enabled.
- [x] Measure pre-response pulse condition.
- [x] Measure post-response pulse condition.
- [x] Verify boundary response changes the condition in the expected direction.
- [x] Verify the changed condition crosses or approaches the declared next-pulse
  threshold without external rescheduling.
- [x] Verify forward and true reversed lanes regenerate opposite polarity.
- [x] Verify pulse-disabled and symmetric-null controls do not restore pulse
  conditions.
- [x] Claim ceiling: `pulse_condition_restoration_candidate`.

Expected artifacts:

- [x] `outputs/pulse_condition_restoration_report.json`
- [x] `reports/pulse_condition_restoration_report.md`

### C3. Feedback-Triggered Pulse Regeneration

Status: Complete.

- [x] Let the feedback path schedule or authorize the next pulse only after the
  boundary response has committed.
- [x] Verify ordering:
  boundary response -> post-response state measurement -> feedback eligibility
  -> regenerated pulse scheduling -> regenerated pulse execution.
- [x] Verify regenerated pulse is not copied from the original E3 schedule.
- [x] Verify regenerated pulse has route polarity consistent with the measured
  post-response state.
- [x] Verify exact budget conservation and nonnegativity.
- [x] Verify controls:
  pulse disabled, feedback disabled, subthreshold feedback, wrong polarity,
  scrambled timing/order, and budget-violating synthetic blocker.
- [x] Claim ceiling: `feedback_triggered_pulse_regeneration`.

Expected artifacts:

- [x] `outputs/feedback_triggered_pulse_regeneration_report.json`
- [x] `reports/feedback_triggered_pulse_regeneration_report.md`

### C4. Reopened M6 Gate

Status: Complete, candidate only.

- [x] Re-run the Iteration 10 M6 gate using the feedback-triggered pulse
  regeneration artifacts.
- [x] Verify movement restores pulse-generating conditions.
- [x] Verify polarity regeneration is measured.
- [x] Verify repeated-cycle persistence is self-renewed, not inherited from the
  original pulse schedule.
- [x] Verify bounded movement cost.
- [x] Verify identity continuity and shape/economy gates.
- [x] Keep locomotion-like, adaptive-topology, biological, agency, and
  inherited-N03 claims blocked unless explicitly opened by a later closeout.
- [x] Claim ceiling if successful:
  `m6_feedback_coupled_self_renewal_candidate`.

Expected artifacts:

- [x] `outputs/reopened_m6_feedback_gate_report.json`
- [x] `reports/reopened_m6_feedback_gate_report.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_feedback_coupled_pulse_regeneration.py
```

Result:

```json
{"claim_ceiling": "m6_feedback_coupled_self_renewal_candidate", "m6_feedback_candidate_gate_passed": true, "status": "passed"}
```

Interpretation:

```text
Lane C demonstrates an experiment-local feedback-coupled self-renewal
candidate: serialized S0 boundary polarity can restore pulse eligibility,
authorize regenerated pulses, and sustain repeated feedback cycles under
controls. This opens an M6 feedback candidate, but not a native M6 claim:
the feedback adapter is not a native LGRC9V3 producer, and movement,
loop-driven movement, locomotion-like, adaptive-topology, biological, agency,
and inherited-N03 claims remain blocked.
```

Native LGRC decision record:

```text
decision = Lane C is compatible with the Lane E causal pulse-substrate surface
candidate_core_extension = native_causal_pulse_substrate_surface
candidate_specialization = policy_gated_feedback_producer
reason = Lane C shows the smallest feedback primitive that can reopen M6, and
         the Lane E compatibility probe shows this primitive can be represented
         as a policy-gated producer specialization over the broader causal
         pulse-substrate surface instead of a separate Lane-C-only core addon.
do_not_change_src_now = true
```

Lane C / Lane E compatibility record:

```text
command = .venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_hybrid_lgrc_lane_c_feedback_surface_compatibility.py
status = passed
claim_ceiling = lane_c_feedback_policy_compatible_with_causal_pulse_substrate_surface
shared_surface = native_causal_pulse_substrate_surface
lane_c_projection = feedback_policy_specialization
lane_c_feedback_surface = boundary_polarity_score
lane_c_specific_core_primitive_needed = false
native_specialization_if_promoted = policy_gated_feedback_producer
native_lgrc_pulse_substrate_supported = false
native_feedback_producer_supported = false
movement_claim_allowed = false
```

Deferred native acceptance criteria:

- [x] Decide after Lane D/Lane E whether the reusable primitive should be:
  feedback-coupled pulse producer, pulse-substrate coupling producer, or a
  more general causal pulse substrate surface. Result:
  `native_causal_pulse_substrate_surface`, with feedback as a policy-gated
  producer specialization.
- [ ] If promoted, keep it default-off and policy-gated.
- [ ] Producer reads only runtime-visible state and emits eligibility evidence.
- [ ] Producer schedules work only through native LGRC scheduling surfaces.
- [ ] `step()` remains the only packet/budget mutation boundary.
- [ ] Evidence is visible in ledger, telemetry, and snapshots.
- [ ] Native support does not itself imply movement, locomotion-like dynamics,
  biology, or agency.

## Lane D. Pulse-Substrate Coupling Mechanism

Status: Deferred.

Lane D preserves the broader mechanistic question previously tracked as Lane C.
It is not the immediate N04 blocker-clearing path. It should be pursued only if
Lane C needs native follow-up, or after N04 closes and a follow-up mechanistic
branch is opened. Lane D is broader than the Iteration 10 unlock path.

Lane D separates two questions:

```text
Mechanism question:
    Can pulse transport produce a traveling local deformation?

Movement-ladder question:
    Does that traveling deformation satisfy frozen movement gates?
```

Claim boundary:

```text
Lane D starts from mechanism, not movement.
Traveling deformation is not movement until D5 reclassification.
N03/E3 remains pulse-substrate evidence only unless explicitly imported.
Lane A's current ceiling is m5_direction_parity_supported_boundary_response.
Lane C supplies an experiment-local feedback-coupled M6 candidate, but native
M6 remains blocked until feedback is promoted to a native runtime producer.
Native LGRC promotion is deferred to Lane E after Lane D closes.
```

Every D-lane report must preserve this separation:

```text
pulse_transport_observed
local_geometry_response_observed
traveling_deformation_observed
tracked_basin_identity_moved
movement_claim_allowed
```

### D1. Pulse Transport Series

Status: Complete.

#### D1.1 Substrate And Pulse State

- [x] Define a simple pulse-conducting chain or ring fixture using
  `runtime_family = experiment_local` for the first pass.
- [x] Declare `budget_surface = node_only`.
- [x] Declare pulse state separately from geometry/support state.
- [x] Declare pulse mass, pulse peak, pulse width, pulse direction, and pulse
  injection site.
- [x] Freeze fixture coordinates and boundary conditions.

#### D1.2 Local Transport Rule

- [x] Use a concrete local transport rule: pulse mass transfers to adjacent
  nodes through declared local coupling weights, with exact budget
  conservation and nonnegativity.
- [x] Verify pulse location at `t+1` is derived from local transport rules, not
  copied from a preauthored pulse itinerary.
- [x] Emit pulse peak location, pulse mass, and per-step local transfer audit.
- [x] Verify no nonlocal pulse jump exceeds declared adjacency.

#### D1.3 Budget And Nonnegativity Audit

- [x] Verify exact pulse budget conservation.
- [x] Verify substrate node budget conservation if the pulse is represented as
  node state.
- [x] Verify nonnegative pulse and substrate state at every step.
- [x] Record budget error and minimum state value per step.

#### D1.4 Transport Controls

- [x] Pulse-disabled control remains negative.
- [x] Static-pulse/no-propagation control remains local.
- [x] Wrong-direction or blocked-edge control fails for the declared reason.
- [x] Budget-violating synthetic blocker is rejected.

#### D1.5 Transport Lock

- [x] Emit claim flags:
  `native_lgrc9v3_e3_pulse_used = false`,
  `movement_claim_inherited_from_n03 = false`, and
  `movement_claim_allowed = false`.
- [x] Claim ceiling: `pulse_transport_only`.
- [x] Blocked claims: `pulse_local_geometry_coupling`,
  `traveling_deformation`, `movement_response`, and `loop_driven_movement`.

Expected artifacts:

- [x] `configs/pulse_substrate_coupling_manifest_v1.json`
- [x] `outputs/pulse_conducting_substrate_baseline.json`
- [x] `reports/pulse_conducting_substrate_baseline.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_pulse_transport_baseline.py
```

Result:

```text
status = passed
claim_ceiling = pulse_transport_only
peak_sequence = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
peak_source = argmax_post_transfer_pulse_field
max_hop_distance = 1
nonlocal_jump_detected = false
max_budget_error = 0.0
pulse_width_max = 1
pulse_peak_mass_min = 1.0
nonnegative_passed = true
wrong_direction_control_negative = true
updates_n04_claim_ceiling = false
native_m6_status_changed = false
```

Interpretation:

```text
D1 proves only local pulse transport. The pulse peak advances by one-hop local
transfers on the S0 chain with exact pulse-budget conservation and nonnegative
state. The pulse peak is computed as argmax of the post-transfer pulse field,
not from a preauthored itinerary. Geometry/support state is unchanged or not
enabled, direct support/centroid/displacement/topology/claim writes are false,
and pulse-disabled, static, wrong-direction, blocked-edge, and budget-violating
controls fail for declared reasons. Geometry coupling, traveling deformation,
movement, loop-driven movement, locomotion-like, adaptive-topology, and native
LGRC pulse-substrate claims remain blocked.
```

### D2. Local Geometry Coupling Series

Status: Complete.

#### D2.1 Geometry Surface Selection

- [x] Define exactly one primary local geometry/support state changed by pulse
  passage.
- [x] Primary state surface: local support mass.
- [x] Define support mass as the sum of node coherence over the support
  reference mask centered on the pulse peak.
- [x] Declare secondary state surfaces as deferred:
  local delay/proper-time phase, local conductance/transport preference,
  local stiffness/width parameter, and reservoir depletion/refill.

#### D2.2 Coupling Rule

- [x] Candidate coupling rule: pulse passage increases support mass by
  `coupling_strength * pulse_signal` at the leading edge and decreases it at
  the trailing edge, with exact budget conservation.
- [x] Verify coupling reads local pulse state and local substrate state only.
- [x] Verify coupling writes geometry/support state only through the declared
  state update, not support masks or centroids.

#### D2.3 Pulse-Contact Response

- [x] Verify geometry/support response occurs only near pulse contact.
- [x] Verify response amplitude tracks pulse amplitude.
- [x] Verify no response occurs away from the pulse beyond declared locality.
- [x] Emit local response time series.

#### D2.4 Direct-Movement Guard

- [x] Verify the pulse changes geometry state locally without direct movement
  writes.
- [x] Verify no direct support mask, centroid, displacement, topology, or claim
  writes.
- [x] Verify geometry coupling disabled control.

#### D2.5 Geometry Coupling Lock

- [x] Emit `pulse_local_geometry_coupling_observed`,
  `local_state_surface_changed`, `movement_claim_allowed = false`, and
  `claim_ceiling = pulse_local_geometry_coupling`.
- [x] Claim ceiling: `pulse_local_geometry_coupling`.

Expected artifacts:

- [x] `outputs/pulse_local_geometry_coupling_report.json`
- [x] `reports/pulse_local_geometry_coupling_report.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_local_geometry_coupling.py
```

Result:

```text
status = passed
claim_ceiling = pulse_local_geometry_coupling
primary_surface = local_support_mass
coupling_strength = 0.1
coupling_count = 11
response_rows = 11
max_support_delta = 0.10000000000000009
max_locality_distance = 1
max_off_contact_delta = 0.0
geometry_budget_abs_error_max = 0.0
min_geometry_state = 0.9
```

Interpretation:

```text
D2 proves local geometry/support response to pulse contact only. The declared
geometry surface is local support mass at the pulse peak. The update is local,
budget-conserving, nonnegative, and does not directly write support masks,
centroid, displacement, topology, or claim flags. Geometry coupling disabled
and pulse-disabled controls remain negative; a static pulse produces local
response without transport. Traveling deformation, movement, loop-driven
movement, locomotion-like, adaptive-topology, and native LGRC pulse-substrate
claims remain blocked.
```

### D3. Traveling Deformation Series

Status: Complete.

#### D3.1 Time-Series Extraction

- [x] Measure pulse peak location over time.
- [x] Measure geometry/support deformation peak location over time.
- [x] Measure deformation mass, width, and profile over time.
- [x] Emit replayable pulse and deformation time series.

#### D3.2 Phase-Lag Measurement

- [x] Measure phase lag between pulse peak and geometry peak.
- [x] Verify deformation peak follows pulse peak with a declared causal
  one-step time lag.
- [x] Verify deformation does not precede pulse peak except within declared
  tolerance.

#### D3.3 Direction Reversal

- [x] Verify reversed pulse direction reverses deformation direction.
- [x] Verify reversal uses the same substrate, coupling rule, thresholds, and
  observables.
- [x] Verify direction reversal is not a sign-convention relabel.

#### D3.4 Width/Profile Preservation

- [x] Measure front advance and rear release from derived support only.
- [x] Measure width/profile preservation of the deformation.
- [x] Separate traveling deformation from smearing/diffusion.

#### D3.5 Traveling Deformation Lock

- [x] Verify static pulse can produce local deformation but not traveling
  deformation.
- [x] Verify pulse transport without geometry coupling produces pulse motion
  but no deformation motion.
- [x] Freeze D-lane deformation gates:
  - [x] `D0`: no deformation;
  - [x] `D1`: local deformation at pulse contact;
  - [x] `D2`: deformation peak tracks pulse peak;
  - [x] `D3`: reversed pulse reverses deformation direction;
  - [x] `D4`: deformation preserves width/profile envelope;
  - [x] `D5`: deformation survives controls and is replayable.
- [x] Claim ceiling: `traveling_deformation_candidate`.

Expected artifacts:

- [x] `outputs/traveling_deformation_audit.json`
- [x] `reports/traveling_deformation_audit.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_traveling_deformation_audit.py
```

Result:

```text
status = passed
claim_ceiling = traveling_deformation_candidate
geometry_response_policy = causal_one_step_lagged_local_support_coupling
pulse_peak_sequence = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
deformation_peak_sequence = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
phase_lag_nodes = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
causal_time_lag_steps = 1
causal_lag_matches = true
deformation_displacement = 10
reversed_deformation_displacement = -4
width_profile_preserved = true
instantaneous_reference_phase_lag_nodes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

Interpretation:

```text
D3 supports a traveling deformation candidate: the local support deformation
peak tracks the pulse peak through an explicit one-step causal lag rather than
only through same-step contact. The original instantaneous D2 response remains
serialized as a reference lane. Reversed pulse direction reverses the
deformation direction. Static pulse and geometry/pulse disabled controls block
traveling deformation for distinct reasons. This is not yet a movement claim;
movement-ladder reclassification is deferred to D5.
```

### D4. Direction And Null Control Series

Status: Complete.

#### D4.1 Disabled Controls

- [x] Pulse disabled.
- [x] Geometry coupling disabled.
- [x] Static pulse / no propagation.

#### D4.2 Direction Controls

- [x] Reversed pulse direction.
- [x] Wrong-direction fixture.
- [x] Direction sign convention audit.

#### D4.3 Scrambled Timing/Order Controls

- [x] Scrambled pulse timing/order.
- [x] For scrambled timing/order, preserve pulse mass profile, event count,
  total budget, and observation window while destroying route/order/phase
  relation.

#### D4.4 Symmetry And Budget Controls

- [x] Symmetric coupling null.
- [x] Budget-violating synthetic blocker.
- [x] Nonnegative violation synthetic blocker.

#### D4.5 Control Matrix Lock

- [x] Verify controls fail for distinct gate reasons.
- [x] Verify negative controls preserve budget unless budget failure is the
  intended blocker.
- [x] Emit control matrix with primary blockers and blocked claims.

Expected artifacts:

- [x] `outputs/pulse_substrate_direction_null_controls.json`
- [x] `reports/pulse_substrate_direction_null_controls.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_pulse_substrate_direction_null_controls.py
```

Result:

```text
status = passed
claim_ceiling = direction_controlled_traveling_deformation_supported
disabled_controls_negative = true
direction_controls_passed = true
scrambled_order_negative = true
scrambled_preserves_mass_event_window = true
symmetric_null_negative = true
budget_blocker_negative = true
nonnegative_blocker_negative = true
```

Control findings:

```text
pulse_disabled -> pulse_absent
geometry_coupling_disabled -> deformation_absent
static_pulse -> local_deformation_without_travel
reversed_pulse -> direction_reversal_positive_control
scrambled_timing_order -> canonical_pulse_order_failed
symmetric_coupling_null -> balanced_symmetric_geometry_response
budget_violating_synthetic -> budget_gate_failed
nonnegative_violating_synthetic -> nonnegative_gate_failed
```

Interpretation:

```text
D4 upgrades D3 from traveling deformation mechanism evidence to
direction-controlled traveling deformation mechanism evidence. Scrambled order
is an empirical generated control that preserves pulse mass profile, event
count, pulse budget, and observation window while breaking canonical order.
Symmetric coupling is negative because the local response is balanced. Budget
and nonnegative controls fail only by their intended gates. Movement,
loop-driven movement, M6, native LGRC pulse-substrate, locomotion-like, and
adaptive-topology claims remain blocked pending D5 reclassification.
```

### D5. Movement-Ladder Reclassification Series

Status: Complete.

#### D5.1 D-Level Classifier

- [x] Implement or freeze D0-D5 deformation classifier.
- [x] Reclassify D-lane evidence with D-level gates before M-level gates.
- [x] Verify D-level labels are artifact-replayable.

#### D5.2 D-To-M Mapping

- [x] Apply explicit D-to-M mapping:
  - [x] `D0` no deformation -> `M0`;
  - [x] `D1` local deformation at pulse contact -> local response only, no
    M4/M5 without boundary coordination;
  - [x] `D2` deformation peak tracks pulse peak -> M4 candidate only if
    boundary coordination also passes;
  - [x] `D3` reversed pulse reverses deformation -> direction-parity control
    for M5 candidate;
  - [x] `D4` deformation preserves width/profile -> M3 shape-gate analog;
  - [x] `D5` deformation survives controls -> M5 control-gate analog.

#### D5.3 Movement Claim Audit

- [x] Separate:
  - [x] pulse transport only;
  - [x] local geometry response only;
  - [x] traveling deformation candidate;
  - [x] direction-controlled traveling deformation;
  - [x] substrate-carried deformation without basin identity movement;
  - [x] movement candidate if gates pass.
- [x] Map D-level evidence to frozen M-ladder evidence without treating
  traveling deformation as movement by default.

#### D5.4 Native LGRC Extension Decision Input

- [x] Compare Lane C feedback-coupled producer need against Lane D
  pulse-substrate coupling need.
- [x] Recommend that Lane E test, in hybrid form, whether a broader causal
  pulse-substrate surface covers both feedback-coupled regeneration and
  pulse-substrate coupling.
- [x] Keep `src/*` changes deferred unless a separate core implementation task
  is opened.

#### D5.5 Lane D Closeout

- [x] Emit final Lane D classification.
- [x] Record implications for native LGRC extension decision.
- [x] Keep M6/native movement closed unless full gates pass under the declared
  runtime scope.

Expected artifacts:

- [x] `outputs/pulse_substrate_movement_reclassification.json`
- [x] `reports/pulse_substrate_movement_reclassification.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_pulse_substrate_movement_reclassification.py
```

Result:

```text
status = passed
claim_ceiling = substrate_carried_deformation_movement_candidate
d_level_label = D5_direction_controlled_traveling_deformation_supported
movement_level_projection = M3_shape_preserving_identity_displacement_candidate_on_deformation_surface
m5_style_deformation_candidate = true
strict_movement_claim_allowed = false
primary_full_claim_blocker = deformation_surface_is_not_runtime_coherence_basin
```

Interpretation:

```text
D5 finds a real movement-style candidate on the deformation surface. The
direction-controlled traveling deformation passes the deformation-surface
projection of displacement, identity-token, boundary-reassignment,
width/profile, repeated-response, direction, budget, nonnegative, and topology
gates. It remains blocked as a full movement claim because the moved identity
is a causal geometry-deformation token, not a runtime coherence basin. Lane E
should decide whether a native LGRC causal pulse-substrate surface is broad
enough to unify Lane C feedback regeneration with Lane D pulse-substrate
coupling. No `src/*` change is opened by D5.
```

## Lane E. Hybrid LGRC Pulse-Substrate Surface Probe

Status: Complete.

Lane E uses LGRC9V3 as it exists today. It should not change core LGRC. It is
the hybrid proof-of-contract lane:

```text
existing native LGRC9V3 pulse telemetry
+ experiment-local native_causal_pulse_substrate_surface driver
+ D5 classifier/replay stack
```

The driver may model the proposed `native_causal_pulse_substrate_surface`, but
its status remains experiment-local. Lane E should prove that one broad surface
contract can cover both Lane C feedback regeneration and Lane D pulse-substrate
deformation before any native implementation is opened.

### E1. Hybrid Surface Contract Definition

Status: Complete.

- [x] Lane D D5 closeout exists.
- [x] Candidate primitive is named:
  `native_causal_pulse_substrate_surface`.
- [x] Hybrid surface contract is explicit and serialized:
  `causal_pulse_substrate_surface_contract_v1`.
- [x] Contract status is `experiment_local_driver`, not native LGRC.
- [x] Direct-write policy blocks native LGRC state, support mask, centroid,
  displacement, topology, and claim-flag writes.
- [x] Producer/step boundary is preserved:
  producer observes/records/declares eligibility; `step()` remains the only
  coherence and packet-budget mutation surface.
- [x] Budget surfaces are separated:
  native LGRC input uses `node_plus_packet`; experiment-local surface uses
  `node_only`; the report records `budget_surfaces_are_not_merged = true`.

Theory alignment:

```text
LGRC paper: causal availability, event-ordered mutation, node-plus-packet
budget.
Native packet-loop paper: producer/step boundary and default-off producers.
Causal pulse-substrate paper: non-axiomatic implementation-specialization
surface, not a new coherence or identity primitive.
```

### E2. Native LGRC Input Import

Status: Complete.

- [x] Import/replay existing native LGRC9V3 E3 pulse artifacts read-only.
- [x] Verify native LGRC9V3 input status:
  `native_lgrc9v3_execution = true`.
- [x] Verify native self-rearm evidence remains present.
- [x] Verify native D2.3-equivalent packet loop remains present.
- [x] Verify native packet budget evidence remains conserved:
  `native_lgrc_final_budget_error = 0.0`.
- [x] Verify no `src/*` changes are required or made by Lane E.

### E3. Lane D-Style Deformation Reproduction

Status: Complete.

- [x] Drive an experiment-local `native_causal_pulse_substrate_surface`
  contract from native LGRC pulse-contact artifacts.
- [x] Verify surface event count matches native contact count.
- [x] Verify causal one-step lag is declared:
  LGRC local update at step `t` drives surface response at `t+1`.
- [x] Verify Lane D-style surface deformation is reproduced:
  `surface_displacement = 12`.
- [x] Verify width profile is preserved.
- [x] Verify max surface budget error is `0.0`.
- [x] Preserve identity boundary: the deformation surface is not a runtime
  coherence basin and cannot by itself promote strict movement.

### E4. Lane C-Style Feedback Eligibility

Status: Complete.

- [x] Reproduce Lane C-style feedback eligibility through the same surface
  contract.
- [x] Verify eligible feedback windows are emitted.
- [x] Verify feedback eligibility remains experiment-local and does not
  schedule native LGRC packets.
- [x] Run focused Lane C compatibility probe.
- [x] Verify Lane C feedback can be represented as
  `feedback_policy_specialization` over the same surface.
- [x] Verify Lane-C-specific core primitive is not required.
- [x] Verify native specialization, if promoted later, is
  `policy_gated_feedback_producer`.
- [x] Verify Lane C controls remain negative.

### E5. D5 Classifier/Replay Stack And Claim Boundary

Status: Complete.

- [x] Run D5 classifier/replay stack against hybrid outputs.
- [x] Emit `hybrid_lgrc_surface_probe = true`.
- [x] Keep `native_lgrc_pulse_substrate_supported = false`.
- [x] Keep `native_feedback_producer_supported = false`.
- [x] Keep `movement_claim_allowed = false`.
- [x] Keep loop-driven movement, locomotion-like, adaptive-topology, biology,
  agency, and inherited-N03 movement claims blocked.
- [x] Verify artifact-only replay inputs are present.

### E6. Theory Alignment Audit

Status: Complete.

| Theory constraint | Source | Lane E audit |
|---|---|---|
| Producer observes/schedules; `step()` mutates. | LGRC paper, packet-loop paper. | Direct-write policy and surface contract preserve producer/step boundary. |
| Native packet budget remains node-plus-packet. | LGRC paper. | `native_lgrc_input_budget_surface = node_plus_packet`; final budget error `0.0`. |
| Derived surface budget is separate. | Causal pulse-substrate paper. | `experiment_local_surface_budget_surface = node_only`; budgets are not merged. |
| Causal availability/order is explicit. | LGRC paper. | Event link records LGRC event at `t` drives surface response at `t+1`. |
| Lane E is implementation-specialization, not native support. | LGRC paper, causal pulse-substrate paper. | Contract status is `experiment_local_driver`; `native_lgrc_pulse_substrate_supported = false`. |
| Deformation token is not coherence-basin identity. | RC identity framing, causal pulse-substrate paper. | Strict movement remains blocked; deformation surface is not a runtime coherence basin. |
| Producer eligibility is not agency or choice. | RC identity framing. | Producer records are mechanical scheduling eligibility only; agency/biology claims blocked. |

Lane E run record:

```text
command = .venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_hybrid_lgrc_pulse_substrate_surface_probe.py
status = passed
claim_ceiling = hybrid_lgrc_causal_pulse_substrate_surface_contract_supported
native_lgrc_input_budget_surface = node_plus_packet
experiment_local_surface_budget_surface = node_only
native_contact_count = 13
surface_displacement = 12
surface_width_profile_preserved = true
max_surface_budget_error = 0.0
feedback_eligible_windows = 10
feedback_regeneration_candidate = true
hybrid_lgrc_surface_probe = true
native_lgrc_pulse_substrate_supported = false
movement_claim_allowed = false
```

Lane C compatibility run record:

```text
command = .venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_hybrid_lgrc_lane_c_feedback_surface_compatibility.py
status = passed
claim_ceiling = lane_c_feedback_policy_compatible_with_causal_pulse_substrate_surface
same_surface_can_host_lane_c_feedback_policy = true
lane_c_controls_remain_negative = true
lane_c_specific_core_primitive_needed = false
native_specialization_if_promoted = policy_gated_feedback_producer
native_feedback_producer_supported = false
```

Lane E interpretation:

```text
Existing native LGRC9V3 E3 pulse-contact artifacts can drive an experiment-local
causal pulse-substrate surface that reproduces Lane D-style deformation and
represents Lane C-style feedback eligibility. This validates the hybrid surface
contract only. It does not claim native LGRC pulse-substrate support and does
not open movement, locomotion-like, adaptive-topology, biology, or agency
claims.
```

Expected artifacts:

- `outputs/hybrid_lgrc_pulse_substrate_surface_probe.json`
- `reports/hybrid_lgrc_pulse_substrate_surface_probe.md`
- `outputs/hybrid_lgrc_lane_c_feedback_surface_compatibility.json`
- `reports/hybrid_lgrc_lane_c_feedback_surface_compatibility.md`

## Lane F. Native LGRC Pulse-Substrate Semantics

Status: Complete as native surface support; movement and native M6 claims
remain blocked.

Lane F is where core LGRC changes may be opened, if Lane E proves the surface
contract is worth promoting.

Lane F entry requirements:

- [x] Lane E hybrid proof passes.
- [x] LGRC paper extension records the causal pulse-substrate surface:
  `papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md`.
- [x] Phase 8 implementation plan/checklist is updated for native support:
  `implementation/Phase-8-LGRC9-CausalPulseSubstratePlan.md` and
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateChecklist.md`.
- [x] Native claim boundary is defined before implementation:
  default-off, enabled/validated/support flags separated, producers emit
  evidence only, and movement/M6/identity/agency claims remain blocked.
- [x] Phase 8 Iteration 56 Lane F bridge artifact produced:
  `outputs/native_lgrc_lane_f_surface_bridge.json`.
- [x] Lane F N04 closeout artifact produced:
  `outputs/n04_lane_f_native_surface_closeout.json`.
- [x] Native causal pulse-substrate surface support is artifact-validatable:
  `native_lgrc_pulse_substrate_supported = true`.
- [x] Lane F closeout consumes the Phase 8 bridge artifact and verifies:
  source artifact digest, full causal-chain reconstruction, controls passed,
  native support flags, fixed-topology status, and blocked claims.
- [x] Native regenerated pulse work is sourced from feedback eligibility, not
  copied from the original E3 schedule.
- [x] Native support is limited to pulse-substrate surface evidence and
  scheduling; movement, loop-driven movement, native M6, locomotion-like,
  adaptive-topology, agency, biology, and identity-acceptance claims remain
  blocked.

Possible native implementation choices:

```text
native_causal_pulse_substrate_surface
native_pulse_substrate_coupling_producer
native_feedback_coupled_pulse_producer
```

Preferred hypothesis:

```text
Implement native_causal_pulse_substrate_surface first, with coupling and
feedback producers as policy-gated specializations, if Lane E validates the
contract.
```

## Lane G. Native M6 Evidence Review

Status: Complete, fail-closed.

Lane G reopens the M6 question after Phase 8 Iteration 57. It does not run a
new movement fixture. It checks whether existing Lane C and Lane F artifacts are
already enough to promote native M6, or whether a same-fixture native validator
is still required.

Lane G question:

```text
After native causal pulse-substrate support exists, do current artifacts
already validate native M6, or only provide prerequisites for a native M6
validator?
```

Result:

```text
status = passed_fail_closed
claim_ceiling = native_m6_prerequisites_supported_validator_absent
native_m6 = false
next_step = run_native_m6_same_fixture_validator
```

Evidence cleared:

- [x] Lane C experiment-local M6 feedback candidate is available.
- [x] Lane C measures movement restoring pulse conditions.
- [x] Lane C measures polarity regeneration.
- [x] Lane C measures repeated self-renewed feedback cycles.
- [x] Lane F validates native causal pulse-substrate surface support.
- [x] Lane F native feedback producer schedules from feedback eligibility.
- [x] Lane F reconstructs the artifact-only native causal chain.
- [x] Lane F controls pass.

Remaining blockers:

- [x] No native same-fixture M6 validator has replayed Lane C's self-renewal
  gate on the S0 movement substrate using native Lane F producer records.
- [x] Repeated native self-renewed cycles are not yet measured on the movement
  fixture.
- [x] Native identity/shape/movement gates have not yet been integrated with
  the native feedback cycle artifact chain.

Expected artifacts:

- [x] `scripts/review_native_m6_evidence.py`
- [x] `outputs/native_m6_evidence_review.json`
- [x] `reports/native_m6_evidence_review.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/review_native_m6_evidence.py
```

Result:

```json
{"claim_ceiling": "native_m6_prerequisites_supported_validator_absent", "output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_m6_evidence_review.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/native_m6_evidence_review.md", "status": "passed_fail_closed"}
```

Acceptance statement:

```text
Lane G shows that the M6 blocker has moved. It is no longer absence of a
native feedback producer: Phase 8/Lane F supports native feedback scheduling
from feedback eligibility. Native M6 remains blocked because no same-fixture
native validator has replayed Lane C's self-renewal gate on the S0 movement
substrate using native producer artifacts. The next N04 step is a native M6
same-fixture validator.
```

## Lane H. Native M6 Same-Fixture Validator

Status: Complete, candidate supported.

Lane H runs the validator opened by Lane G. It uses native LGRC9V3 causal
pulse-substrate surface rows and the native feedback producer on the S0 chain.
The first packet contact is seeded; subsequent pulse work must be authorized
from native feedback eligibility rows and scheduled by the native feedback
producer.

Lane H question:

```text
Can the native LGRC9V3 pulse-substrate surface and feedback producer reproduce
Lane C's self-renewal gate on the same S0 movement substrate with native
artifact replay?
```

Result:

```text
status = passed
claim_ceiling = native_m6_same_fixture_self_renewal_candidate
native_m6_candidate_gate_passed = true
native_m6 = true
movement_claim_allowed = false
locomotion_like_claim_allowed = false
adaptive_topology_entry_allowed = false
```

Evidence cleared:

- [x] Native same-fixture validator exists.
- [x] Native M6 validation checklist audit exists.
- [x] Forward native self-renewed cycles pass.
- [x] Reversed native self-renewed cycles pass.
- [x] Native repeated self-renewed cycles are measured.
- [x] Movement-substrate state restores pulse conditions through native
  feedback eligibility.
- [x] Polarity regeneration is measured with opposite-sign centroid response.
- [x] Artifact-only native surface validation passes.
- [x] Budget, nonnegative, topology, identity, and shape gates pass.
- [x] Negative controls pass for pulse-disabled, feedback-disabled,
  subthreshold, wrong-polarity, and budget-violation cases.

Expected artifacts:

- [x] `scripts/run_native_m6_same_fixture_validator.py`
- [x] `scripts/audit_native_m6_validation_list.py`
- [x] `outputs/native_m6_same_fixture_validator.json`
- [x] `outputs/native_m6_validation_checklist_audit.json`
- [x] `reports/native_m6_same_fixture_validator.md`
- [x] `reports/native_m6_validation_checklist_audit.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_native_m6_same_fixture_validator.py
```

Result:

```json
{"claim_ceiling": "native_m6_same_fixture_self_renewal_candidate", "native_m6_candidate_gate_passed": true, "output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_m6_same_fixture_validator.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/native_m6_same_fixture_validator.md", "status": "passed"}
```

Acceptance statement:

```text
Lane H supports a bounded native M6 same-fixture self-renewal candidate. On
S0_chain_v1, after one seeded packet contact, native feedback eligibility rows
authorize regenerated packet work through the native feedback producer for
both forward and reversed boundary polarity. Forward dX is positive, reversed
dX is negative with matched magnitude, and each direction records three
self-renewed native feedback cycles. This opens native M6 candidate evidence,
but not locomotion-like behavior, adaptive topology, biology, agency,
identity-acceptance, inherited-N03 movement, or unrestricted movement claims.
```

## Iteration 13. Taxonomy Inventory

Status: Passed.

Iteration 13 starts the taxonomy continuation after all retrospective,
mechanism, and native-support lanes. Its first job is inventory, not promotion.

The taxonomy continuation keeps M0-M6 as the primary ladder and adds
orthogonal tags for transfer scope:

```text
movement_level = M0|M1|M2|M3|M4|M5|M6
geometry_scope = same_fixture | transferred_geometry | topology_mutating
substrate_class = chain | corridor | ring | grid | port_graph
identity_kind = coherence_basin | deformation_token | boundary_signal | null
identity_surface = fixed_substrate | boundary_fixture | deformation_surface | native_causal_pulse_substrate_surface
implementation_surface = experiment_local | mapped_e3_fixture | native_lgrc_telemetry | native_causal_pulse_substrate_surface
d_level = D0|D1|D2|D3|D4|D5|null
m_level_projection = M0|M1|M2|M3|M4|M5|M6|null
projection_blocker = ...
```

- [x] Build taxonomy inventory from existing N04 reports.
- [x] Include M0 fixed-substrate nulls and blocked classes.
- [x] Include M1 apparent centroid-displacement classes.
- [x] Include M2 runtime shape-blocked boundary-reassignment evidence.
- [x] Include M3 shape-preserving identity-displacement evidence.
- [x] Include M4 coordinated boundary response.
- [x] Include M5 direction-parity-supported boundary response.
- [x] Include M6 native same-fixture self-renewal candidate.
- [x] Include 15-C/15-D/15-E M6 resilience-extension rows after those probes
  completed:
  - [x] `M6_s0_perturbation_tolerance_profile`;
  - [x] `M6_shock_resistant_same_family_geometry_recovery_candidate`;
  - [x] `M6_large_shock_absorber_same_family_recovery_candidate`.
- [x] Include Iteration 16/17 geometry-transfer rows after those probes
  completed:
  - [x] `M6_s4_corridor_transfer_candidate`;
  - [x] `M6_s4_corridor_perturbation_envelope`;
  - [x] `M6_s4_corridor_high_shock_capacity_requirement`;
  - [x] `M6_s1_ring_declared_unwrap_transfer_candidate`;
  - [x] `M6_s1_ring_unwrap_robust_transfer_candidate`;
  - [x] `M6_s1_ring_circular_motion_evidence_candidate`;
  - [x] `M6_s1_ring_circular_motion_with_unwrap_robustness_closeout`;
  - [x] `M6_s3_grid_route_defined_transfer_candidate`;
  - [x] `M6_s3_grid_two_axis_turn_candidate`;
  - [x] `M6_s3_grid_state_gated_routing_candidate`;
  - [x] `M6_s3_grid_geometry_scored_selection_design_prototype`;
  - [x] `M6_s3_grid_composed_1d_fork_competition_candidate`;
  - [x] `M6_s3_grid_balanced_local_preference_fork_candidate`;
  - [x] `M6_s3_grid_integrated_2d_composed_gate_candidate`;
  - [x] `M6_s3_grid_series_closeout_fixed_topology_2d_gate`.
- [x] Include Lane D deformation and Lane C/E feedback/surface evidence as
  non-M-axis supporting classes.
- [x] Inventory D-level deformation evidence as first-class rows with
  `d_level`, `m_level_projection`, and `projection_blocker`.
- [x] Record `identity_kind` separately from `identity_surface`.
- [x] Every inventory row must cite source artifact path and claim ceiling.
- [x] Every inventory row cites source report path in addition to source JSON.
- [x] Visual references are recorded as supporting references only, not
  evidence sources.
- [x] Every inventory row records row-specific claim flags and blocked claims.
- [x] Persistence tags are present without claiming perturbation-recovery/T6.
- [x] Current M6 row is scoped to same-fixture S0 chain evidence only.

Expected artifacts:

- `outputs/n04_taxonomy_inventory_v1.json`
- `reports/n04_taxonomy_inventory_v1.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_taxonomy_inventory_v1.py",
  "status": "passed",
  "inventory_rows": 36,
  "movement_rows": 28,
  "deformation_rows": 5,
  "supporting_rows": 3,
  "checks": {
    "all_m0_m6_present": true,
    "d1_d5_present": true,
    "d_rows_have_projection_fields": true,
    "identity_kind_surface_split_present": true,
    "substrate_class_values_declared": true,
    "all_rows_have_sources": true,
    "all_rows_have_source_reports": true,
    "all_rows_have_claim_ceiling": true,
    "all_rows_have_row_specific_claim_flags": true,
    "all_rows_have_persistence_fields": true,
    "visual_references_are_not_evidence_sources": true,
    "no_unrestricted_claims_promoted": true,
    "no_persistence_t6_claimed": true,
    "m6_scoped_to_same_fixture_chain": true,
    "d5_blocked_from_runtime_basin_movement": true,
    "lane_c_d_e_supporting_rows_present": true,
    "m6_resilience_extension_rows_present": true,
    "fixture_topology_change_distinguished_from_runtime_topology": true,
    "iter16_corridor_transfer_row_present": true,
    "iter16b_corridor_perturbation_row_present": true,
    "iter16c_high_shock_capacity_row_present": true,
    "iter17_ring_transfer_row_present": true,
    "iter17a_ring_unwrap_robustness_row_present": true,
    "iter17b_circular_ring_motion_row_present": true,
    "iter17c_ring_geometry_closeout_row_present": true,
    "iter18_grid_transfer_row_present": true,
    "iter18b_grid_two_axis_turn_row_present": true,
    "iter18c_grid_state_gated_routing_row_present": true,
    "iter18d_grid_geometry_selection_row_present": true,
    "iter18e_composed_1d_fork_competition_row_present": true,
    "iter18f_balanced_local_preference_fork_row_present": true,
    "iter18g_integrated_2d_composed_gate_row_present": true,
    "iter18h_s3_grid_series_closeout_row_present": true
  },
  "next_iteration": "14_class_separation_and_tag_freeze"
}
```

Post-15-E taxonomy refresh:

```json
{
  "m6_resilience_and_transfer_extension_rows": [
    "M6_s0_perturbation_tolerance_profile",
    "M6_shock_resistant_same_family_geometry_recovery_candidate",
    "M6_large_shock_absorber_same_family_recovery_candidate",
    "M6_s4_corridor_transfer_candidate",
    "M6_s4_corridor_perturbation_envelope",
    "M6_s4_corridor_high_shock_capacity_requirement",
    "M6_s1_ring_declared_unwrap_transfer_candidate",
    "M6_s1_ring_unwrap_robust_transfer_candidate",
    "M6_s1_ring_circular_motion_evidence_candidate",
    "M6_s1_ring_circular_motion_with_unwrap_robustness_closeout",
    "M6_s3_grid_route_defined_transfer_candidate",
    "M6_s3_grid_two_axis_turn_candidate",
    "M6_s3_grid_state_gated_routing_candidate",
    "M6_s3_grid_geometry_scored_selection_design_prototype",
    "M6_s3_grid_composed_1d_fork_competition_candidate",
    "M6_s3_grid_balanced_local_preference_fork_candidate",
    "M6_s3_grid_integrated_2d_composed_gate_candidate",
    "M6_s3_grid_series_closeout_fixed_topology_2d_gate"
  ],
  "claim_boundary": "scoped_m6_resilience_extensions_not_broad_geometry_transfer_or_locomotion"
}
```

## Iteration 14. Class Separation And Tag Freeze

Status: Passed.

- [x] Separate centroid displacement from identity-preserving movement.
- [x] Separate boundary response from basin movement.
- [x] Separate traveling deformation from runtime coherence-basin movement.
- [x] Separate same-fixture self-renewal from locomotion-like movement.
- [x] Separate M6 resilience extensions from broad geometry-transfer,
  locomotion-like, and adaptive-topology claims.
- [x] Separate fixed topology from topology-mutating evidence.
- [x] Freeze the taxonomy tag schema before geometry probes.
- [x] Freeze whether Iteration 14 carries full orthogonal README taxonomy tags
  (`R`, `B`, `G`, `Q`, `F`, `H`, `E`, `T`) per row, or records them as
  explicitly deferred with rationale.
- [x] Record that M1 and M3 current rows are classifier/observable-fixture
  evidence rather than empirical native runtime movement lanes.
- [x] Explain the M4 `mapped_e3_fixture` to M5 `native_lgrc_telemetry`
  implementation-surface transition.
- [x] Freeze claim-boundary rules so taxonomy tags remain descriptors, not
  claim emitters.
- [x] Declare invalid tag/claim combinations, including deformation-token
  strict movement, same-fixture M6 locomotion, topology claims without topology
  scope, and visuals as source artifacts.
- [x] Validate current inventory rows under the frozen schema.
- [x] Expand `persistence_level` enum to cover `T0`-`T6`, `not_measured`,
  `not_applicable`, candidate values, and tested-negative outcomes before
  Iteration 15.
- [x] Assign conservative feedback levels: current same-fixture M6 is `F2`,
  not `F5`, because locomotion-like cycle claims remain blocked.
- [x] Assign identity-continuity levels only where source artifacts explicitly
  measured identity/mass or identity/shape gates.
- [x] Preserve source-artifact and source-report provenance in frozen row tags.
- [x] Preserve 15-C/15-D/15-E M6 resilience-extension tags in the frozen schema
  with scoped claim ceilings.
- [x] Preserve Iteration 16/17 geometry-transfer tags in the frozen schema with
  scoped corridor/ring claim ceilings.
- [x] Freeze D-to-M projection rules:
  - [x] `D0` -> `M0` only;
  - [x] `D1` -> local response only, no M promotion without boundary coordination;
  - [x] `D2` -> `M4` candidate only if boundary coordination passes;
  - [x] `D3` -> direction-parity evidence for `M5` candidate;
  - [x] `D4` -> shape/profile analog, not direct `M3` promotion;
  - [x] `D5` -> M5-style control evidence, blocked from coherence-basin
    movement when `identity_kind = deformation_token`.

Expected artifacts:

- `outputs/n04_taxonomy_tag_schema_v1.json`
- `reports/n04_taxonomy_class_separation_v1.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_taxonomy_tag_schema_v1.py",
  "status": "passed",
  "checks": {
    "inventory_status_passed": true,
    "centroid_displacement_separated": true,
    "boundary_response_separated": true,
    "traveling_deformation_separated": true,
    "same_fixture_self_renewal_separated": true,
    "fixed_topology_separated": true,
    "tag_schema_frozen": true,
    "orthogonal_readme_tags_declared": true,
    "persistence_enum_complete": true,
    "orthogonal_values_not_backfilled_from_unmeasured_artifacts": true,
    "m1_m3_origin_recorded": true,
    "implementation_surface_transition_documented": true,
    "d_to_m_projection_rules_frozen": true,
    "d5_runtime_basin_promotion_blocked": true,
    "claim_boundary_rules_frozen": true,
    "invalid_combinations_declared": true,
    "current_inventory_rows_validate_under_schema": true,
    "visual_sources_rejected": true,
    "same_fixture_m6_locomotion_invalid": true,
    "m6_feedback_level_conservative": true,
    "measured_identity_levels_assigned": true,
    "frozen_rows_retain_source_provenance": true,
    "m6_resilience_extension_tags_frozen": true,
    "fixture_topology_tag_frozen": true,
    "iter16_corridor_transfer_tags_frozen": true,
    "iter16b_corridor_perturbation_tags_frozen": true,
    "iter16c_high_shock_capacity_tags_frozen": true,
    "iter17_ring_transfer_tags_frozen": true,
    "iter17a_ring_unwrap_robustness_tags_frozen": true,
    "iter17b_circular_ring_motion_tags_frozen": true,
    "iter17c_ring_geometry_closeout_tags_frozen": true,
    "iter18_grid_transfer_tags_frozen": true,
    "iter18b_grid_two_axis_turn_tags_frozen": true,
    "iter18c_grid_state_gated_routing_tags_frozen": true,
    "iter18d_grid_geometry_selection_tags_frozen": true,
    "iter18e_composed_1d_fork_competition_tags_frozen": true,
    "iter18f_balanced_local_preference_fork_tags_frozen": true,
    "iter18g_integrated_2d_composed_gate_tags_frozen": true,
    "iter18h_s3_grid_series_closeout_tags_frozen": true,
    "no_claim_promotion": true
  },
  "next_iteration": "15_s0_chain_replay_and_longer_window_stress"
}
```

Post-Iteration-16 taxonomy schema refresh:

```json
{
  "m6_resilience_and_transfer_extension_tags": {
    "M6_s0_perturbation_tolerance_profile": {
      "persistence_level": "tested_negative",
      "claim_ceiling": "s0_same_fixture_perturbation_tolerance_profile"
    },
    "M6_shock_resistant_same_family_geometry_recovery_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "shock_resistant_same_family_geometry_recovery_candidate"
    },
    "M6_large_shock_absorber_same_family_recovery_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "large_shock_absorber_same_family_recovery_candidate"
    },
    "M6_s4_corridor_transfer_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s4_corridor_m6_transfer_candidate"
    },
    "M6_s4_corridor_perturbation_envelope": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s4_corridor_perturbation_envelope_profile"
    },
    "M6_s4_corridor_high_shock_capacity_requirement": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s4_corridor_high_shock_capacity_requirement_probe"
    },
    "M6_s1_ring_declared_unwrap_transfer_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s1_ring_m6_transfer_candidate_under_declared_unwrap"
    },
    "M6_s1_ring_unwrap_robust_transfer_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s1_ring_unwrap_robust_transfer_candidate"
    },
    "M6_s1_ring_circular_motion_evidence_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s1_ring_circular_motion_evidence_candidate"
    },
    "M6_s1_ring_circular_motion_with_unwrap_robustness_closeout": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness"
    },
    "M6_s3_grid_route_defined_transfer_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s3_grid_route_defined_m6_transfer_candidate"
    },
    "M6_s3_grid_two_axis_turn_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s3_grid_two_axis_turn_m6_transfer_candidate"
    },
    "M6_s3_grid_state_gated_routing_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s3_grid_state_gated_two_input_two_output_routing_candidate"
    },
    "M6_s3_grid_geometry_scored_selection_design_prototype": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s3_grid_geometry_scored_selection_design_prototype"
    },
    "M6_s3_grid_composed_1d_fork_competition_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s3_grid_composed_1d_fork_competition_candidate"
    },
    "M6_s3_grid_balanced_local_preference_fork_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s3_grid_balanced_local_preference_fork_competition_candidate"
    },
    "M6_s3_grid_integrated_2d_composed_gate_candidate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s3_grid_integrated_2d_composed_gate_candidate"
    },
    "M6_s3_grid_series_closeout_fixed_topology_2d_gate": {
      "persistence_level": "T6_candidate",
      "claim_ceiling": "s3_grid_integrated_2d_composed_gate_candidate"
    }
  },
  "claim_boundary": "tags_are_descriptors_not_claims"
}
```

## Iteration 15. S0 Chain Replay And Longer-Window Stress

Status: Passed.

- [x] Replay current M5/M6 chain candidates with the same gates and policies.
- [x] Extend repeated-cycle window and measure boundedness/cost scaling.
- [x] Use `cost_metric = total_redistribution_load_per_cycle`, following the
  Q3 movement cost/economy convention in the N04 README.
- [x] Use boundedness criterion: cost per cycle does not grow superlinearly
  with cycle count.
- [x] Treat as failure or downgrade if cost per cycle doubles between cycle 3
  and cycle 5, or if budget error accumulates beyond `epsilon_budget`.
- [x] Verify seeded-first-contact vs native feedback-renewed cycles remains
  separated.
- [x] Record that T6/R6 recovery remains untested and blocked, and route the
  explicit perturbation/recovery probe to Iteration 15-B.
- [x] Keep broader movement and adaptive-topology claims blocked.
- [x] Go/no-go for Iteration 15-B: if M6 does not sustain at least five
  feedback-renewed cycles with bounded cost, either stop and reopen the S0
  mechanism question or run perturbation recovery with a degraded ceiling
  explicitly stated.

Expected artifacts:

- `outputs/n04_iter15_s0_chain_stress_report.json`
- `reports/n04_iter15_s0_chain_stress_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15_s0_chain_stress.py",
  "status": "passed",
  "claim_ceiling": "native_m6_same_fixture_self_renewal_candidate_stress_passed",
  "forward_self_renewed_cycles": 5,
  "reversed_self_renewed_cycles": 5,
  "cost_scaling_status": "bounded",
  "recovery_status": "not_tested_blocked_until_perturbation_recovery_probe",
  "checks": {
    "tag_schema_passed": true,
    "m5_replay_passed": true,
    "baseline_m6_available": true,
    "forward_five_feedback_cycles": true,
    "reversed_five_feedback_cycles": true,
    "seeded_vs_feedback_cycles_separated": true,
    "direction_parity_preserved": true,
    "budget_error_bounded": true,
    "nonnegative_gate_passed": true,
    "identity_shape_gates_passed": true,
    "artifact_validators_passed": true,
    "cost_scaling_bounded": true,
    "cycle3_to_cycle5_cost_not_doubled": true,
    "recovery_status_recorded": true,
    "broader_claims_blocked": true
  },
  "go_no_go_for_iteration_16": {
    "iteration_16_allowed": true,
    "entry_ceiling_for_geometry_transfer": "native_m6_same_fixture_self_renewal_candidate_stress_passed"
  },
  "next_iteration": "15b_s0_perturbation_recovery_probe"
}
```

Note: the Iteration 15 artifact records geometry-transfer readiness from the
five-cycle stress result. The checklist sequence now routes through Iteration
15-B before Iteration 16 so T6/R6 recovery is explicitly tested or closed as
blocked.

## Iteration 15-B. S0 Perturbation Recovery Probe

Status: Complete.

- [x] Declare perturbation policy before the run:
  - [x] perturbation timing;
  - [x] affected nodes or surface rows;
  - [x] mass amount;
  - [x] whether the perturbation targets polarity, support, or feedback
    eligibility.
- [x] Verify perturbation is budget-neutral and topology-fixed.
- [x] Verify perturbation does not directly write support masks, centroid,
  displacement, topology, or claim flags.
- [x] Start from a pre-perturbation baseline with at least five
  feedback-renewed cycles from Iteration 15.
- [x] Declare finite post-perturbation recovery window before the run.
- [x] Test whether front/rear polarity resets or re-establishes (`R6`).
- [x] Test whether displacement/self-renewal cycle recovers (`T6`).
- [x] If recovery fails, record `T6 = tested_negative` or equivalent and keep
  geometry-transfer entry ceiling at the Iteration 15 stress ceiling.
- [x] If recovery passes, record `T6_candidate` / `R6_candidate`; this run did
  not pass recovery, so no recovery candidate was recorded and no
  locomotion-like, adaptive-topology, biological, agency, identity-acceptance,
  inherited-N03, or unrestricted movement claim was promoted.
- [x] Go/no-go for Iteration 16: geometry transfer may proceed with the
  strongest explicitly recorded S0 ceiling from Iteration 15 or 15-B.

Expected artifacts:

- [x] `outputs/n04_iter15b_s0_perturbation_recovery_report.json`
- [x] `reports/n04_iter15b_s0_perturbation_recovery_report.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15b_s0_perturbation_recovery.py
```

Result:

```json
{"output": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter15b_s0_perturbation_recovery_report.json", "report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter15b_s0_perturbation_recovery_report.md", "status": "passed", "persistence_level": "tested_negative", "r6_level": "tested_negative"}
```

Notes:

- The perturbation policy was
  `s0_threshold_preserving_front_rear_polarity_damping_v1`.
- The run starts after five native feedback-renewed S0 cycles, then transfers
  `0.15` budget-neutral mass from the expected boundary side to the opposite
  boundary side.
- Both forward and reversed lanes recover two feedback-authorized native
  cycles, then the third recovery attempt fails closed with
  `feedback_source_budget_exhausted`.
- The stronger out-of-envelope perturbation control remains negative.
- T6/R6 perturbation recovery is therefore recorded as `tested_negative`; the
  geometry-transfer entry ceiling remains
  `native_m6_same_fixture_self_renewal_candidate_stress_passed`.

## Iteration 15-C. S0 Perturbation Tolerance Envelope

Status: Complete.

- [x] Declare perturbation sweep values before the run.
- [x] Reuse the same native S0 surface, feedback policy, recovery window,
  budget, topology, and claim gates as Iteration 15-B.
- [x] Record each sweep point as recovered, partially recovered, or failed
  closed.
- [x] Record a primary blocker for each failed point:
  - [x] `subthreshold`;
  - [x] `wrong_polarity`;
  - [x] `source_budget_exhausted`;
  - [x] other blocker only if declared in the report.
- [x] Record the largest perturbation that recovers within the declared
  window.
- [x] Record the smallest perturbation that fails.
- [x] Verify every perturbation is budget-neutral and topology-fixed.
- [x] Verify no direct support, centroid, displacement, topology,
  producer-claim, or claim-flag writes occur.
- [x] Keep claim ceiling at
  `s0_same_fixture_perturbation_tolerance_profile`.
- [x] Go/no-go for Iteration 15-D: use the first failing S0 perturbation as
  the resilience challenge unless the full sweep recovers, in which case use
  the largest tested perturbation and record that the failure threshold remains
  open.

Expected artifacts:

- [x] `outputs/n04_iter15c_s0_perturbation_tolerance_profile.json`
- [x] `reports/n04_iter15c_s0_perturbation_tolerance_profile.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15c_s0_perturbation_tolerance.py
```

Result:

```json
{
  "status": "passed",
  "claim_ceiling": "s0_same_fixture_perturbation_tolerance_profile",
  "largest_t6_recoverable_perturbation": null,
  "smallest_positive_t6_failed_perturbation": 0.02,
  "largest_r6_recoverable_perturbation": 0.1,
  "smallest_positive_r6_failed_perturbation": 0.125,
  "dominant_t6_blocker": "source_budget_exhausted",
  "challenge_perturbation_for_15d": 0.02
}
```

Notes:

- T6 recovery fails at every tested sweep point, including the zero-perturbation
  reservoir control, because the three-cycle recovery window hits
  `source_budget_exhausted` after two feedback-authorized recovery cycles.
- R6 polarity recovery is narrower but real for small perturbations: both
  directions recover polarity through `0.10`; the first positive R6 failure is
  `0.125`.
- Perturbations `0.30` and `0.35` fail closed as `subthreshold` with no
  recovery cycles scheduled.
- Iteration 15-D should target the `source_budget_exhausted` failure mode. The
  smallest positive T6 failure is `0.02`, though `0.15` remains the stronger
  stress point from Iteration 15-B.

Rationale for Iteration 15-D:

```text
Iteration 15-C shows that current S0 does not fail T6 primarily because the
shock is too large. It fails the declared three-cycle recovery window even at
the zero-perturbation reservoir control because the source reservoir can fund
only two recovery cycles after the five-cycle baseline. R6 polarity recovery
still survives for small perturbations, so feedback sensing and causal ordering
remain active. Iteration 15-D therefore asks whether geometry/reservoir design
can fix source-budget exhaustion without directly scripting support, centroid,
displacement, topology, or claims.
```

## Iteration 15-D. Shock-Resistant Recovery Geometry Probe

Status: Complete.

- [x] Declare candidate recovery geometry before the run:
  - [x] reservoir, corridor, buffer, or other recovery-capacity structure;
  - [x] why it targets the Iteration 15-B/C failure mode;
  - [x] whether it remains same-family chain/corridor geometry or opens a
    distinct substrate class.
- [x] Inherit the challenge perturbation from Iteration 15-C, preferably the
  smallest perturbation that broke S0.
- [x] Reuse the native causal pulse-substrate surface and feedback producer
  where possible.
- [x] Declare any policy differences before execution.
- [x] Verify recovery occurs only through native packet event -> surface row ->
  feedback eligibility -> scheduled packet work -> `step()` mutation.
- [x] Verify no direct support, centroid, displacement, topology,
  producer-claim, or claim-flag writes occur.
- [x] Compare recovery against S0 at the same perturbation amount.
- [x] Record whether the geometry improves:
  - [x] recovery cycle count;
  - [x] source-budget exhaustion behavior;
  - [x] front/rear polarity restoration;
  - [x] displacement/self-renewal restoration.
- [x] If successful, record only a scoped resilience result such as
  `shock_resistant_same_family_geometry_recovery_candidate`.
- [x] Keep locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, unrestricted movement, and broad geometry
  transfer claims blocked.
- [x] Go/no-go for Iteration 16: formal geometry transfer proceeds with the
  strongest explicit S0/resilience ceiling, and the Iteration 16 fixture must
  state whether it tests ordinary transfer or resilience-informed geometry.

Expected artifacts:

- [x] `outputs/n04_iter15d_shock_resistant_recovery_geometry_report.json`
- [x] `reports/n04_iter15d_shock_resistant_recovery_geometry_report.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15d_shock_resistant_geometry.py
```

Result:

```json
{
  "status": "passed",
  "claim_ceiling": "shock_resistant_same_family_geometry_recovery_candidate",
  "challenge_perturbation": 0.02,
  "challenge_recovered": true,
  "stress_perturbation": 0.15,
  "stress_recovered": false,
  "source_budget_exhaustion_avoided_at_challenge": true,
  "source_budget_exhaustion_avoided_at_stress": true
}
```

Notes:

- The candidate geometry is `s0_chain_source_reservoir_buffer_v1`, a
  same-family chain variant with symmetric source-reservoir boosts at nodes
  `8` and `12`, budget-balanced by debits at nodes `9` and `11`.
- The native causal pulse-substrate surface and feedback producer semantics
  are unchanged.
- At the Iteration 15-C challenge perturbation `0.02`, the buffered geometry
  schedules all three recovery cycles in both directions, avoids source-budget
  exhaustion, and passes R6/T6 candidate criteria.
- At the stronger Iteration 15-B stress perturbation `0.15`, the buffered
  geometry schedules all three recovery cycles and avoids source-budget
  exhaustion, but it does not satisfy the T6 centroid-restoration criterion.
- This is therefore a scoped shock-resistant same-family geometry recovery
  candidate, not a broad geometry-transfer, locomotion-like, adaptive-topology,
  biological, agency, identity-acceptance, inherited-N03, or unrestricted
  movement claim.

## Iteration 15-E. Large-Shock Absorber Geometry Probe

Status: Complete.

Rationale:

```text
Iteration 15-D shows that a source-reservoir buffer fixes the first positive S0
T6-failing perturbation and avoids source-budget exhaustion at the stronger
0.15 stress point, but 0.15 still fails the T6 centroid-restoration criterion.
So the remaining design question is whether same-family geometry can absorb a
large boundary-polarity shock, not merely fund additional recovery cycles.
```

- [x] Declare candidate absorber geometry before the run:
  - [x] source reservoir structure;
  - [x] boundary absorber/buffer nodes;
  - [x] compensating budget debits;
  - [x] why the design targets the `0.15` failure mode.
- [x] Use challenge perturbation `0.15` from Iterations 15-B and 15-D.
- [x] Reuse native causal pulse-substrate surface semantics unchanged.
- [x] Reuse native feedback producer semantics unchanged.
- [x] Verify absorber initialization is budget-neutral and topology-fixed during
  runtime.
- [x] Record fixture-defined recovery-channel topology separately from runtime
  topology mutation.
- [x] Record centroid coordinate/sign convention for forward and reversed lanes.
- [x] Record recovery cost as inherited from the Iteration 15 native feedback
  packet cost metric.
- [x] Verify no direct support, centroid, displacement, topology,
  producer-claim, or claim-flag writes occur.
- [x] Verify recovery occurs only through native packet event -> surface row ->
  feedback eligibility -> scheduled packet work -> `step()` mutation.
- [x] Compare against plain S0 at perturbation `0.15`.
- [x] Compare against the Iteration 15-D source-reservoir geometry at
  perturbation `0.15`.
- [x] Pass criteria:
  - [x] source-budget exhaustion avoided;
  - [x] R6 polarity restoration passes;
  - [x] T6 centroid-restoration passes at `0.15`.
- [x] If successful, record only a scoped result such as
  `large_shock_absorber_same_family_recovery_candidate`.
- [x] If unsuccessful, record the new blocker and carry the 15-D scoped ceiling
  into Iteration 16.
- [x] Keep locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, unrestricted movement, and broad geometry
  transfer claims blocked.
- [x] Go/no-go for Iteration 16: formal geometry transfer should state whether
  it uses source-reservoir-only resilience from 15-D or absorber-informed
  resilience from 15-E.

Expected artifacts:

- [x] `outputs/n04_iter15e_large_shock_absorber_geometry_report.json`
- [x] `reports/n04_iter15e_large_shock_absorber_geometry_report.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15e_large_shock_absorber_geometry.py
```

Result:

```json
{
  "status": "passed",
  "claim_ceiling": "large_shock_absorber_same_family_recovery_candidate",
  "challenge_perturbation": 0.15,
  "full_recovery_window_scheduled": true,
  "source_budget_exhaustion_avoided": true,
  "directions_recovered": ["forward", "reversed"],
  "fixture_topology_changed_before_run": true,
  "no_runtime_topology_mutation_observed": true,
  "centroid_delta_frame": "direction_normalized_recovery_delta",
  "cost_metric": "total_redistribution_load_per_cycle",
  "cost_per_feedback_cycle": 0.1,
  "r6_polarity_restoration_passed": true,
  "t6_centroid_restoration_passed": true
}
```

Notes:

- The candidate geometry is `s0_chain_large_shock_absorber_v1`.
- It keeps the S0 node count but defines fixed recovery-channel edges from a
  central reservoir node `10` to front/rear absorber nodes `14` and `6`.
- Those recovery-channel edges are fixture-defined before execution; runtime
  topology remains fixed and no topology-mutating evidence is claimed.
- Reservoir initialization is budget-neutral: node `10` receives `0.25`,
  balanced by debits at nodes `9` and `11`.
- At perturbation `0.15`, both directions schedule all three recovery cycles,
  avoid source-budget exhaustion, restore R6 polarity, and pass the T6
  centroid-restoration criterion.
- Signed centroid deltas are direction-normalized, so positive means recovery
  in the lane's declared direction for both forward and reversed lanes. Raw
  centroid deltas remain available in the JSON artifact.
- Recovery cost uses the Iteration 15 native feedback packet cost metric
  `total_redistribution_load_per_cycle` with `0.1` per feedback cycle.
- Native causal pulse-substrate surface semantics and native feedback producer
  semantics are unchanged. Recovery still proceeds through packet events,
  surface rows, feedback eligibility, scheduled packet work, and `step()`
  mutation.
- This is a scoped same-family absorber recovery candidate, not a broad
  geometry-transfer, locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, or unrestricted movement claim.

## Iteration 16. S4 Corridor Or Widened-Chain Geometry Transfer

Status: Complete.

- [x] Define corridor/widened-chain fixture with frozen front/rear direction.
- [x] Transfer the same native pulse-substrate and feedback policy where
  possible.
- [x] Verify direction parity, budget, nonnegativity, identity, shape, and
  self-renewal gates under transferred geometry.
- [x] Record `geometry_scope = transferred_geometry`.
- [x] Distinguish fixture-defined corridor rails from runtime topology
  mutation.
- [x] Record raw and direction-normalized centroid deltas for forward and
  reversed lanes.
- [x] Record recovery cost as inherited from the Iteration 15 native feedback
  packet cost metric.
- [x] Go/no-go for Iteration 17: if corridor transfer does not reach at least
  M4, ring transfer must inherit the corridor-achieved ceiling rather than
  assume an M5/M6 transfer.

Expected artifacts:

- [x] `outputs/n04_iter16_corridor_transfer_report.json`
- [x] `reports/n04_iter16_corridor_transfer_report.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter16_corridor_transfer.py
```

Result:

```json
{
  "status": "passed",
  "claim_ceiling": "s4_corridor_m6_transfer_candidate",
  "achieved_movement_level": "M6",
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s4_corridor_transfer_recovers_0_15",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "forward_and_reversed_three_cycle_recovery_on_s4_corridor",
    "recovery_status": "recovers_0_15_corridor_transfer",
    "recovery_tested": true,
    "recovery_passed": true,
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "single_corridor_fixture_only_no_broader_perturbation_envelope"
  },
  "geometry_scope": "transferred_geometry",
  "substrate_class": "corridor",
  "directions_recovered": ["forward", "reversed"],
  "fixture_topology_changed_before_run": true,
  "no_runtime_topology_mutation_observed": true,
  "cost_metric": "total_redistribution_load_per_cycle",
  "cost_per_feedback_cycle": 0.1,
  "iteration_17_allowed": true
}
```

Notes:

- The fixture is `S4_widened_chain_absorber_corridor_v1`.
- The result transfers the 15-E absorber-informed candidate to a non-identical
  fixed corridor fixture while keeping native surface and feedback producer
  semantics unchanged.
- Both forward and reversed lanes schedule all three recovery cycles, preserve
  exact budget, pass identity/shape gates, and satisfy the M6 transfer-candidate
  checks.
- Corridor rails are fixture-defined before execution; runtime topology remains
  fixed and no adaptive-topology claim is opened.
- This is a scoped corridor transfer candidate, not a ring, grid, port-graph,
  broad geometry-transfer, locomotion-like, adaptive-topology, biological,
  agency, identity-acceptance, inherited-N03, or unrestricted movement claim.

## Iteration 16-B. S4 Corridor Perturbation Probe

Status: Complete.

- [x] Reuse the Iteration 16 corridor fixture and native feedback policy.
- [x] Sweep declared budget-neutral front/rear polarity perturbations.
- [x] Record the strongest M4/M5/M6-style recovery boundary on the corridor.
- [x] Expose the T-axis persistence result directly in the report.
- [x] Keep full T6, ring/grid/port-graph transfer, broad geometry-transfer,
  locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, and unrestricted movement claims blocked.

Expected artifacts:

- [x] `outputs/n04_iter16b_corridor_perturbation_probe.json`
- [x] `reports/n04_iter16b_corridor_perturbation_probe.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter16b_corridor_perturbation_probe.py
```

Result:

```json
{
  "status": "passed",
  "claim_ceiling": "s4_corridor_perturbation_envelope_profile",
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s4_corridor_perturbation_envelope",
    "largest_t6_candidate_recoverable_perturbation": 0.15,
    "smallest_positive_t6_candidate_failed_perturbation": 0.175,
    "largest_m5_recoverable_perturbation": 0.25,
    "largest_m4_recoverable_perturbation": 0.35,
    "recovery_window_cycles": 3,
    "t6_full_claim_allowed": false
  },
  "dominant_failure_blocker": "centroid_not_restored",
  "iteration_17_allowed": true
}
```

Notes:

- The S4 corridor recovers T6-candidate centroid restoration through
  perturbation `0.15` in both directions.
- Above that boundary, feedback response remains informative but below the
  full M6/T6-candidate ceiling: M5-style response persists through `0.25` and
  M4-style boundary response through `0.35`.
- The zero-perturbation point is recorded as a neutral control, not as a T6
  failure.
- This strengthens the scoped corridor T-axis envelope but does not promote
  full T6, broad geometry-transfer, locomotion-like, adaptive-topology,
  biological, agency, identity-acceptance, inherited-N03, or unrestricted
  movement claims.

## Iteration 16-C. High-Shock Corridor Resilience Probe

Status: Complete.

- [x] Use the Iteration 16-B `0.175` T6-candidate failure boundary as the first
  challenge.
- [x] Keep geometry-only changes separate from changed feedback capacity.
- [x] Test declared recovery-capacity variants without promoting them to the
  default corridor policy.
- [x] Record the minimum recovery capacity needed to recover higher shocks.
- [x] Keep full T6, ring/grid/port-graph transfer, broad geometry-transfer,
  locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, and unrestricted movement claims blocked.

Expected artifacts:

- [x] `outputs/n04_iter16c_high_shock_corridor_resilience.json`
- [x] `reports/n04_iter16c_high_shock_corridor_resilience.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter16c_high_shock_corridor_resilience.py
```

Result:

```json
{
  "status": "passed",
  "claim_ceiling": "s4_corridor_high_shock_capacity_requirement_probe",
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s4_corridor_high_shock_capacity_requirement",
    "three_cycle_reference_largest_t6_candidate_from_16b": 0.15,
    "three_cycle_probe_above_boundary_largest_t6_candidate": null,
    "four_cycle_largest_t6_candidate": 0.2,
    "five_cycle_largest_t6_candidate": 0.25,
    "t6_full_claim_allowed": false
  },
  "claim_interpretation": "capacity_requirement_evidence_not_default_policy_promotion"
}
```

Notes:

- The high-shock boundary is capacity-limited under the declared three-cycle,
  `0.1`-packet native feedback window.
- Discovery rule: `required_boundary_recovery_load = 2 * perturbation_amount`;
  `available_capacity = recovery_window_cycles * native_feedback_packet_amount`.
  The `0.175` failure is expected because it needs `0.35` recovery load while
  the default three-cycle policy supplies only `0.30`.
- Geometry-only corridor changes do not lift the 16-B `0.15`
  T6-candidate limit.
- Four recovery cycles recover `0.20`; five recovery cycles recover `0.25`.
- This is useful guidance for Iteration 17: ring transfer should explicitly
  declare whether it keeps the three-cycle policy from 16-B or opens
  capacity-extended variants from 16-C.
- Full T6, ring/grid/port-graph transfer, broad geometry-transfer,
  locomotion-like, adaptive-topology, biological, agency, identity-acceptance,
  inherited-N03, and unrestricted movement claims remain blocked.

## Iteration 17. S1 Ring With Explicit Unwrap Policy

Status: Passed.

- [x] Define unwrap, front/rear, centroid, and direction policy before running.
- [x] Verify ring antipodal/tie-breaking artifacts cannot create promotion.
- [x] Run M0-M6 candidate checks only after the ring policy is frozen.
- [x] Keep ring claims scoped to the declared unwrap convention.
- [x] Go/no-go for Iteration 18: grid transfer opens as M5/M6 transfer only if
  corridor transfer reached M5+; otherwise grid inherits the weaker
  corridor/ring ceiling.

Expected artifacts:

- [x] `outputs/n04_iter17_ring_unwrap_policy.json`
- [x] `outputs/n04_iter17_ring_transfer_report.json`
- [x] `reports/n04_iter17_ring_transfer_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter17_ring_transfer.py",
  "status": "passed",
  "claim_ceiling": "s1_ring_m6_transfer_candidate_under_declared_unwrap",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "ring",
  "movement_substrate": "S1_ring_absorber_corridor_v1",
  "unwrap_policy_id": "s1_ring_unwrap_policy_v1",
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s1_ring_declared_unwrap_recovers_0_15",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "forward_and_reversed_three_cycle_recovery_on_s1_ring_declared_unwrap",
    "recovery_status": "recovers_0_15_ring_declared_unwrap",
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "single_declared_unwrap_policy_no_wrap_crossing_or_grid_transfer"
  },
  "checks": {
    "iteration_16c_available": true,
    "unwrap_policy_available": true,
    "ring_fixture_declared_before_run": true,
    "front_rear_direction_frozen_before_run": true,
    "route_does_not_cross_unwrap_seam": true,
    "antipodal_tie_cannot_promote": true,
    "wrap_jump_promotion_blocked": true,
    "native_surface_semantics_unchanged": true,
    "native_feedback_producer_semantics_unchanged": true,
    "fixture_topology_changed_before_run": true,
    "topology_fixed_during_run": true,
    "no_runtime_topology_mutation_observed": true,
    "ring_initialization_budget_neutral": true,
    "artifact_validators_passed": true,
    "budget_and_nonnegative_gates_passed": true,
    "identity_shape_gates_passed": true,
    "direction_parity_passed": true,
    "m4_boundary_response_passed": true,
    "m5_direction_control_passed": true,
    "m6_ring_transfer_candidate_passed": true,
    "feedback_authorized_not_schedule_copied": true,
    "broader_claims_blocked": true
  },
  "go_no_go_for_iteration_18": {
    "iteration_18_allowed": true,
    "grid_transfer_ceiling_to_test": "s1_ring_m6_transfer_candidate_under_declared_unwrap",
    "grid_transfer_guidance": "grid transfer may test M5/M6 under route-defined front/rear masks"
  },
  "next_iteration": "18_s3_grid_route_defined_front_rear"
}
```

Notes:

- Iteration 17 transfers the corridor candidate to an S1 ring only under the
  declared unwrap policy. The active route does not cross the seam `[20, 0]`.
- Forward and reversed directions both recover the `0.15` perturbation with
  three native feedback-authorized cycles.
- `raw_final_centroid_delta` reverses sign across forward/reversed lanes; the
  reported signed centroid delta is direction-normalized for recovery scoring.
- Circular locomotion, wrap-crossing movement, broad geometry-transfer,
  adaptive topology, biological, agency, identity-acceptance, inherited-N03,
  and unrestricted movement claims remain blocked.

## Iteration 17-A. Ring Unwrap-Robustness Probe

Status: Passed.

- [x] Declare multiple unwrap origins before execution.
- [x] Verify accepted unwrap policies keep the active route away from the seam.
- [x] Freeze front/rear masks, positive direction, centroid policy, and
  tie-breaking policy per unwrap before scoring.
- [x] Recompute forward/reversed M4/M5/M6 candidate gates from native surface
  artifacts for every unwrap.
- [x] Verify matched achieved levels, direction parity, and recovery status
  across equivalent unwraps.
- [x] Record seam-intersecting unwraps as seam-sensitive controls, not
  robustness evidence.
- [x] Keep circular locomotion, wrap-crossing movement, broad geometry-transfer,
  adaptive topology, biological, agency, identity-acceptance, inherited-N03,
  and unrestricted movement claims blocked.

Expected artifacts:

- [x] `outputs/n04_iter17a_ring_unwrap_robustness_report.json`
- [x] `reports/n04_iter17a_ring_unwrap_robustness_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter17a_ring_unwrap_robustness.py",
  "status": "passed",
  "claim_ceiling": "s1_ring_unwrap_robust_transfer_candidate",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "ring",
  "accepted_unwrap_origins": [0, 1, 2, 3, 4, 5, 6, 15, 16, 17, 18, 19, 20],
  "seam_control_origins": [7, 8, 9, 10, 11, 12, 13, 14],
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s1_ring_multiple_unwraps_recover_0_15",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "forward_and_reversed_three_cycle_recovery_across_equivalent_unwraps",
    "recovery_status": "recovers_0_15_across_equivalent_unwraps",
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "unwrap_robustness_only_no_circular_metric_or_grid_transfer"
  },
  "checks": {
    "iteration_17_available": true,
    "multiple_unwrap_origins_declared": true,
    "accepted_unwraps_keep_route_off_seam": true,
    "seam_intersecting_controls_recorded": true,
    "candidate_gates_recomputed_per_origin": true,
    "all_accepted_origins_reach_m6": true,
    "direction_parity_passed_all_accepted_origins": true,
    "artifact_validators_passed": true,
    "budget_and_nonnegative_gates_passed": true,
    "identity_shape_gates_passed": true,
    "feedback_authorized_not_schedule_copied": true,
    "signed_centroid_magnitude_stable": true,
    "broader_claims_blocked": true
  },
  "go_no_go_for_iteration_17b": {
    "iteration_17b_allowed": true,
    "circular_motion_ceiling_to_test": "s1_ring_unwrap_robust_transfer_candidate"
  },
  "next_iteration": "17b_circular_ring_motion_evidence_probe"
}
```

Notes:

- Iteration 17-A improves the ring evidence from a single declared unwrap to
  unwrap-robust transfer evidence.
- All 13 accepted unwrap origins recover the `0.15` perturbation in both
  directions with native feedback-authorized cycles.
- The 8 seam-intersecting unwrap origins are controls and cannot promote
  robustness, circular motion, or wrap-crossing claims.

## Iteration 17-B. Circular Ring Motion Evidence Probe

Status: Passed.

- [x] Declare circular phase/centroid metric before execution.
- [x] Test seam-crossing and wrap-crossing routes with circular distances,
  not linear unwrap shortcuts.
- [x] Declare circular front/rear or phase-leading/trailing policy before
  scoring.
- [x] Run static, wrong-direction, seam-artifact, and unwrap-only controls with
  distinct primary blockers.
- [x] Verify native surface and feedback producer semantics remain unchanged.
- [x] Verify no direct centroid, support, topology, displacement, or claim
  writes occur.
- [x] Run artifact-only validators over the circular evidence chain.
- [x] Keep locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, and unrestricted movement claims blocked
  unless a later explicit closeout opens them.

Expected artifacts:

- [x] `outputs/n04_iter17b_circular_ring_motion_evidence_report.json`
- [x] `reports/n04_iter17b_circular_ring_motion_evidence_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter17b_circular_ring_motion.py",
  "status": "passed",
  "claim_ceiling": "s1_ring_circular_motion_evidence_candidate",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "ring",
  "movement_substrate": "S1_ring_wrap_only_v1",
  "circular_metric_policy": {
    "policy_id": "s1_ring_circular_phase_metric_v1",
    "metric": "shortest_signed_ring_distance",
    "phase_metric": "positive_excess_mass_circular_mean",
    "forward_route": [20, 0],
    "reversed_route": [0, 20],
    "wrap_edge": [20, 0],
    "phase_tolerance_nodes": 0.25
  },
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s1_ring_circular_wrap_route_recovers_0_15",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "forward_and_reversed_three_cycle_recovery_on_circular_wrap_route",
    "recovery_status": "recovers_0_15_on_circular_wrap_route",
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "single_ring_fixture_no_grid_or_port_graph_transfer"
  },
  "circular_motion_summary": {
    "forward_circular_displacement_nodes": 1.0,
    "reversed_circular_displacement_nodes": -1.0,
    "forward_final_phase_error_to_target_nodes": 0.0,
    "reversed_final_phase_error_to_target_nodes": 0.0
  },
  "controls": {
    "static": "no_committed_packet_contact",
    "wrong_direction": "feedback_wrong_polarity",
    "seam_artifact": "linear_unwrap_seam_intersects_active_route",
    "unwrap_only": "unwrap_robustness_has_no_circular_metric_or_seam_crossing_positive_lane"
  },
  "checks": {
    "iteration_17a_available": true,
    "circular_metric_declared_before_run": true,
    "seam_crossing_routes_tested": true,
    "circular_distance_sign_reversal_passed": true,
    "circular_phase_target_passed": true,
    "m4_boundary_response_passed": true,
    "m5_direction_control_passed": true,
    "m6_circular_motion_candidate_passed": true,
    "artifact_validators_passed": true,
    "budget_and_nonnegative_gates_passed": true,
    "identity_shape_gates_passed": true,
    "feedback_authorized_not_schedule_copied": true,
    "controls_fail_for_distinct_blockers": true,
    "native_surface_semantics_unchanged": true,
    "native_feedback_producer_semantics_unchanged": true,
    "no_direct_writes": true,
    "broader_claims_blocked": true
  },
  "go_no_go_for_iteration_18": {
    "iteration_18_allowed": true,
    "grid_transfer_ceiling_to_test": "s1_ring_circular_motion_evidence_candidate"
  },
  "next_iteration": "18_s3_grid_route_defined_front_rear"
}
```

Notes:

- Iteration 17-B is the first ring result that directly tests the wrap edge
  under a circular metric rather than relying on a linear unwrap.
- Forward `20 -> 0` gives circular displacement `+1.0`; reversed `0 -> 20`
  gives `-1.0`; both final positive-excess phases land on the target with
  zero phase error.
- This supports a scoped circular motion evidence candidate on one ring
  fixture. It does not yet allow circular locomotion, broad geometry-transfer,
  adaptive topology, biological, agency, identity-acceptance, inherited-N03, or
  unrestricted movement claims.

## Iteration 17-C. Ring Geometry Closeout

Status: Passed.

- [x] Consume Iteration 17, 17-A, and 17-B artifacts as source inputs.
- [x] Record the combined ring-series ceiling.
- [x] Preserve single-unwrap, unwrap-robustness, and circular wrap-route
  evidence as distinct source layers.
- [x] Verify all ring-series rows remain M6/T6-candidate scoped evidence.
- [x] Keep broad geometry-transfer, locomotion-like, adaptive-topology,
  biological, agency, identity-acceptance, inherited-N03, and unrestricted
  movement claims blocked.
- [x] Route Iteration 18 to test whether the ring-series ceiling transfers to
  S3 grid route-defined front/rear geometry.

Expected artifacts:

- [x] `outputs/n04_iter17c_ring_geometry_closeout.json`
- [x] `reports/n04_iter17c_ring_geometry_closeout.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_iter17c_ring_geometry_closeout.py",
  "status": "passed",
  "claim_ceiling": "s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "ring",
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s1_ring_circular_motion_with_unwrap_robustness",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "ring_series_forward_reversed_three_cycle_recovery",
    "recovery_status": "recovers_0_15_single_unwrap_multi_unwrap_and_circular_wrap_route",
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "ring_series_only_no_grid_or_port_graph_transfer"
  },
  "ring_series_summary": {
    "iteration_17_ceiling": "s1_ring_m6_transfer_candidate_under_declared_unwrap",
    "iteration_17a_ceiling": "s1_ring_unwrap_robust_transfer_candidate",
    "iteration_17b_ceiling": "s1_ring_circular_motion_evidence_candidate",
    "accepted_unwrap_origin_count": 13,
    "seam_control_origin_count": 8,
    "forward_circular_displacement_nodes": 1.0,
    "reversed_circular_displacement_nodes": -1.0,
    "forward_phase_error_to_target_nodes": 0.0,
    "reversed_phase_error_to_target_nodes": 0.0
  },
  "checks": {
    "iteration_17_passed": true,
    "iteration_17a_passed": true,
    "iteration_17b_passed": true,
    "single_unwrap_ring_transfer_passed": true,
    "unwrap_robustness_passed": true,
    "circular_motion_evidence_passed": true,
    "all_ring_results_m6_candidate": true,
    "all_ring_results_t6_candidate": true,
    "unwrap_robustness_has_seam_controls": true,
    "circular_result_has_controls": true,
    "circular_forward_reversed_signs_passed": true,
    "broader_claims_blocked": true,
    "summary_only_no_new_probe": true
  },
  "go_no_go_for_iteration_18": {
    "iteration_18_allowed": true,
    "grid_transfer_ceiling_to_test": "s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness"
  },
  "next_iteration": "18_s3_grid_route_defined_front_rear"
}
```

Notes:

- Iteration 17-C is summary-only and runs no new probe.
- It combines the ring evidence into one scoped ceiling:
  `s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness`.
- The combined ceiling remains ring-only. Grid, port-graph, broad
  geometry-transfer, locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, and unrestricted movement claims remain
  blocked.

## Iteration 18. S3 Grid Route-Defined Front/Rear

Status: Passed.

- [x] Define route-based direction and front/rear masks on the grid.
- [x] Test whether boundary response and self-renewal survive a 2D substrate.
- [x] Check that diagonal/route shortcuts do not become hidden displacement
  scripts.

Expected artifacts:

- [x] `outputs/n04_iter18_grid_transfer_report.json`
- [x] `reports/n04_iter18_grid_transfer_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18_grid_transfer.py",
  "status": "passed",
  "claim_ceiling": "s3_grid_route_defined_m6_transfer_candidate",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "grid",
  "movement_substrate": "S3_grid_route_defined_front_rear_v1",
  "grid_route_policy": {
    "policy_id": "s3_grid_route_defined_front_rear_policy_v1",
    "grid_width": 5,
    "grid_height": 5,
    "coordinate_frame": "grid_xy",
    "route_axis": "x",
    "center_node": 12,
    "front_nodes": [13],
    "rear_nodes": [11],
    "forward_route": [12, 13],
    "reversed_route": [12, 11],
    "diagonal_edges_enabled": false,
    "route_shortcuts_enabled": false
  },
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s3_grid_route_defined_front_rear_recovers_0_15",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "forward_and_reversed_three_cycle_recovery_on_s3_grid_route",
    "recovery_status": "recovers_0_15_grid_route_defined_front_rear",
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "single_grid_route_no_port_graph_or_adaptive_topology_transfer"
  },
  "grid_transfer_summary": {
    "entry_ceiling": "s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness",
    "achieved_level": "M6",
    "forward_final_x_delta": 0.03571428571428581,
    "reversed_final_x_delta": -0.03571428571428559,
    "forward_signed_final_x_delta": 0.03571428571428581,
    "reversed_signed_final_x_delta": 0.03571428571428559,
    "max_abs_y_drift": 0.0
  },
  "controls": {
    "wrong_direction": "feedback_wrong_polarity",
    "diagonal_shortcut": "diagonal_route_shortcuts_disabled_by_fixture_policy"
  },
  "checks": {
    "iteration_17c_available": true,
    "route_based_direction_declared": true,
    "front_rear_masks_declared_before_run": true,
    "grid_fixture_declared_before_run": true,
    "local_unit_route_edges_only": true,
    "diagonal_route_shortcuts_disabled": true,
    "m4_boundary_response_passed": true,
    "m5_direction_control_passed": true,
    "m6_grid_transfer_candidate_passed": true,
    "grid_direction_parity_passed": true,
    "no_y_axis_drift": true,
    "artifact_validators_passed": true,
    "budget_and_nonnegative_gates_passed": true,
    "identity_shape_gates_passed": true,
    "feedback_authorized_not_schedule_copied": true,
    "controls_fail_for_distinct_blockers": true,
    "native_surface_semantics_unchanged": true,
    "native_feedback_producer_semantics_unchanged": true,
    "no_direct_writes": true,
    "broader_claims_blocked": true
  },
  "go_no_go_for_iteration_19": {
    "iteration_19_allowed": true,
    "port_graph_ceiling_to_test": "s3_grid_route_defined_m6_transfer_candidate"
  },
  "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate"
}
```

Notes:

- Iteration 18 transfers the ring-series ceiling to a 5x5 grid with
  route-defined east/west front/rear masks.
- This is a grid-substrate survival result, not a completed 2D movement result:
  the active evidence is still a one-axis route embedded in a 2D substrate.
- Forward/reversed x displacement signs are opposite, and route-normalized
  signed displacement is positive in both directions.
- The result uses local unit route edges only; diagonal shortcuts and route
  shortcuts are disabled.
- Port-graph, topology-mutating, adaptive-topology, broad geometry-transfer,
  locomotion-like, biological, agency, identity-acceptance, inherited-N03, and
  unrestricted movement claims remain blocked.

## Iteration 18-B. S3 Grid Two-Axis Turn Route

Status: Passed.

Reasoning:

- Iteration 18 proved the M6/T6 candidate survives a 2D grid substrate, but the
  active route was still one-axis and ring/chain-like.
- A stronger grid probe must require a route episode whose active displacement
  changes grid axis under a declared L-shaped route.
- This remains conservative: the route is declared before execution, topology
  stays fixed, and success would support a two-axis route candidate rather than
  adaptive routing or broad 2D movement.

- [x] Declare an L-shaped turn route, ingress/egress gates, and turn node
  before the run.
- [x] Verify the route episode has nonzero x-axis and y-axis displacement
  components.
- [x] Verify output after the turn is feedback-authorized from committed native
  surface evidence, not copied from a preauthored schedule.
- [x] Run reversed/paired turn parity with the same thresholds and route
  policy.
- [x] Keep diagonal shortcuts, post-hoc masks, direct displacement writes,
  locomotion-like, adaptive-topology, port-graph, and unrestricted movement
  claims blocked.

Expected artifacts:

- [x] `outputs/n04_iter18b_grid_two_axis_turn_report.json`
- [x] `reports/n04_iter18b_grid_two_axis_turn_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18b_grid_two_axis_turn.py",
  "status": "passed",
  "claim_ceiling": "s3_grid_two_axis_turn_m6_transfer_candidate",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "grid",
  "movement_substrate": "S3_grid_two_axis_turn_route_v1",
  "two_axis_turn_policy": {
    "policy_id": "s3_grid_two_axis_turn_policy_v1",
    "grid_width": 5,
    "grid_height": 5,
    "coordinate_frame": "grid_xy",
    "turn_node": 12,
    "lanes": {
      "west_to_north": {"ingress": [11, 12], "egress": [12, 7]},
      "north_to_west": {"ingress": [7, 12], "egress": [12, 11]}
    },
    "diagonal_edges_enabled": false,
    "route_shortcuts_enabled": false,
    "declared_before_run": true
  },
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s3_grid_two_axis_turn_recovers_0_15",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "paired_two_axis_turn_recovery_on_s3_grid",
    "recovery_status": "recovers_0_15_two_axis_turn_route",
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "declared_two_axis_route_no_state_gated_gate_selection_or_port_graph_transfer"
  },
  "two_axis_turn_summary": {
    "entry_ceiling": "s3_grid_route_defined_m6_transfer_candidate",
    "achieved_level": "M6",
    "forward_final_delta": {"x": 0.011904761904762085, "y": -0.004761904761904967},
    "reversed_final_delta": {"x": -0.004761904761904745, "y": 0.011904761904761862},
    "forward_route_progress": 0.011785113019776063,
    "reversed_route_progress": 0.011785113019775749
  },
  "controls": {
    "wrong_polarity": "feedback_wrong_polarity",
    "diagonal_shortcut": "diagonal_route_shortcuts_disabled_by_fixture_policy"
  },
  "checks": {
    "two_axis_turn_reasoning_recorded": true,
    "l_route_declared_before_run": true,
    "route_turns_axis": true,
    "two_axis_centroid_components_observed": true,
    "m6_two_axis_turn_candidate_passed": true,
    "paired_turn_parity_passed": true,
    "feedback_authorized_not_schedule_copied": true,
    "controls_fail_for_distinct_blockers": true,
    "no_direct_writes": true,
    "broader_claims_blocked": true
  },
  "go_no_go_for_iteration_18c": {
    "iteration_18c_allowed": true,
    "state_gated_routing_ceiling_to_test": "s3_grid_two_axis_turn_m6_transfer_candidate"
  },
  "next_iteration": "18c_s3_grid_state_gated_two_input_two_output_routing"
}
```

Notes:

- Iteration 18-B is stronger than Iteration 18 because the active route episode
  crosses axes: committed ingress reaches the center on one grid axis, then
  native feedback eligibility authorizes egress on the orthogonal axis.
- It remains a declared L-route candidate, not state-gated routing. Iteration
  18-C is still needed to test whether local pulse/contact history selects
  among multiple output gates.
- State-gated 2D routing, port-graph, topology-mutating, adaptive-topology,
  broad geometry-transfer, locomotion-like, biological, agency,
  identity-acceptance, inherited-N03, and unrestricted movement claims remain
  blocked.

## Iteration 18-C. S3 Grid State-Gated Two-Input/Two-Output Routing

Status: Passed.

Reasoning:

- A one-phase 1D pulsar can be drawn on a grid without becoming a 2D pulse
  mechanism.
- The next stricter question is whether a fixed-topology grid junction can
  expose two input gates and two output gates, then select the output gate from
  serialized pulse-contact history and feedback eligibility.
- This probes 2D pulsation and route choice while keeping topology fixed and
  preserving the producer/step boundary.
- The current implementation is a design prototype over native LGRC
  primitives. Packet work, surface rows, feedback eligibility, feedback
  scheduling, and artifact validation are native; the gate-selection decision
  is still experiment-level serialized policy.
- The intended native direction is geometry-driven gate selection: declared
  junction geometry and committed pulse-substrate surface evidence should select
  the output gate, not an external decision function.

- [x] Declare two input gates, two output gates, and a serialized
  gate-selection policy before the run.
- [x] Verify different committed pulse/contact histories select different
  output gates under the same fixed grid topology.
- [x] Verify disabled gate policy, wrong-polarity, scrambled-order, and diagonal
  shortcut controls fail with distinct blockers.
- [x] Verify regenerated pulse work is feedback-authorized and not copied from
  an original schedule.
- [x] Record that gate selection is experiment-level design-prototype logic,
  not yet native geometry-driven LGRC behavior.
- [x] Keep topology mutation, adaptive-topology, locomotion-like, biological,
  agency, identity-acceptance, inherited-N03, and unrestricted movement claims
  blocked.

Expected artifacts:

- [x] `outputs/n04_iter18c_grid_state_gated_routing_report.json`
- [x] `reports/n04_iter18c_grid_state_gated_routing_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18c_grid_state_gated_routing.py",
  "status": "passed",
  "claim_ceiling": "s3_grid_state_gated_two_input_two_output_routing_candidate",
  "result_role": "design_prototype_over_native_lgrc_primitives",
  "native_support_boundary": {
    "native_lgrc_packet_work_used": true,
    "native_causal_pulse_substrate_surface_used": true,
    "native_feedback_eligibility_surface_used": true,
    "native_feedback_producer_used": true,
    "native_artifact_validator_used": true,
    "gate_selection_native_lgrc_producer": false,
    "gate_selection_source": "experiment_level_serialized_design_policy",
    "geometry_driven_gate_selection_supported": false,
    "native_gate_selection_blocker": "gate selection is performed by experiment script policy; a native geometry-driven gate-selection producer or equivalent surface mechanism is not implemented yet"
  },
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "grid",
  "movement_substrate": "S3_grid_state_gated_two_input_two_output_v1",
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s3_grid_state_gated_routing_recovers_0_15",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "two_input_histories_select_distinct_outputs_with_three_cycle_recovery",
    "recovery_status": "recovers_0_15_state_gated_output_routes",
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "fixed_topology_state_gated_routing_no_port_graph_or_adaptive_topology_transfer"
  },
  "state_gated_routing_summary": {
    "entry_ceiling": "s3_grid_two_axis_turn_m6_transfer_candidate",
    "achieved_level": "M6",
    "selected_outputs": {
      "west_input_selects_north": 7,
      "south_input_selects_east": 13
    },
    "route_progress": {
      "west_input_selects_north": 0.011785113019775906,
      "south_input_selects_east": 0.011785113019775906
    },
    "final_deltas": {
      "west_input_selects_north": {"x": 0.011904761904761862, "y": -0.004761904761904967},
      "south_input_selects_east": {"x": 0.004761904761904745, "y": -0.011904761904762085}
    }
  },
  "controls": {
    "gate_policy_disabled": "gate_policy_disabled",
    "wrong_history_gate": "gate_selection_rejected_by_committed_ingress_history",
    "wrong_polarity": "feedback_wrong_polarity",
    "diagonal_shortcut": "diagonal_route_shortcuts_disabled_by_fixture_policy",
    "scrambled_order": "gate_selection_requires_committed_ingress_history"
  },
  "checks": {
    "state_gated_reasoning_recorded": true,
    "two_input_two_output_policy_declared_before_run": true,
    "same_fixed_grid_topology_used": true,
    "different_histories_select_different_outputs": true,
    "gate_selection_uses_committed_ingress_history": true,
    "m6_state_gated_routing_candidate_passed": true,
    "feedback_authorized_not_schedule_copied": true,
    "controls_fail_for_distinct_blockers": true,
    "no_direct_writes": true,
    "broader_claims_blocked": true
  },
  "go_no_go_for_iteration_19": {
    "iteration_19_allowed": true,
    "port_graph_ceiling_to_test": "s3_grid_state_gated_two_input_two_output_routing_candidate"
  },
  "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate"
}
```

Notes:

- Iteration 18-C is the first fixed-topology two-input/two-output grid routing
  design prototype. The same grid junction selects different output gates from
  different committed ingress histories under one serialized experiment-level
  policy.
- The result is stronger than 18-B because route choice is state/history-gated,
  not only a declared single L-route.
- It remains fixed-topology routing over native LGRC primitives, not native
  geometry-driven gate selection. Port-graph transfer, topology mutation,
  adaptive-topology, broad geometry-transfer, locomotion-like, biological,
  agency, identity-acceptance, inherited-N03, and unrestricted movement claims
  remain blocked.

## Iteration 18-D. S3 Grid Geometry-Scored Competing Basin Selection

Status: Passed.

Reasoning:

- Iteration 18-C uses native packet/surface/feedback machinery, but the gate
  selection itself is an experiment-level ingress-to-output policy.
- Iteration 18-D should move the design closer to geometry: two output basins
  compete, the input pulse carries a flux-shape signature, and the selected
  basin is the one with stronger geometry/flux compatibility.
- This is a selection/collapse analogue only. It is not RC identity collapse,
  semantic choice, agency, native LGRC gate selection, adaptive topology, or
  locomotion-like movement.

- [x] Declare competing output basins, flux-shape fields, and compatibility
  scoring rule before the run.
- [x] Verify output choice is derived from serialized input flux-shape evidence
  and declared basin geometry, not a direct input-to-output lookup.
- [x] Verify two distinct input flux shapes resolve to different output basins.
- [x] Verify tie/ambiguous flux, disabled competition, wrong-output, and
  diagonal shortcut controls fail with distinct blockers.
- [x] Verify selected output pulse work is scheduled through native LGRC
  feedback machinery and is not copied from an original schedule.
- [x] Record that the current implementation is a geometry-scored design
  prototype, not native geometry-driven LGRC selection/collapse.
- [x] Record the stricter blocker: 18-D uses external experiment scoring logic
  that evaluates competing futures, not just a native LGRC scheduling policy
  over already-declared packet work.
- [x] Keep RC identity-collapse, agency, adaptive-topology, port-graph,
  locomotion-like, biological, inherited-N03, and unrestricted movement claims
  blocked.

Expected artifacts:

- [x] `outputs/n04_iter18d_grid_geometry_selection_report.json`
- [x] `reports/n04_iter18d_grid_geometry_selection_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18d_grid_geometry_selection.py",
  "status": "passed",
  "claim_ceiling": "s3_grid_geometry_scored_selection_design_prototype",
  "result_role": "geometry_scored_selection_design_prototype_over_native_lgrc_primitives",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "grid",
  "movement_substrate": "S3_grid_geometry_scored_competing_output_basins_v1",
  "native_support_boundary": {
    "native_lgrc_packet_work_used": true,
    "native_causal_pulse_substrate_surface_used": true,
    "native_feedback_eligibility_surface_used": true,
    "native_feedback_producer_used": true,
    "native_artifact_validator_used": true,
    "selection_native_lgrc_producer": false,
    "selection_source": "experiment_level_geometry_competition_score",
    "selection_logic_kind": "external_experiment_scoring_logic",
    "different_from_prior_lgrc_policy_extensions": true,
    "prior_policy_extension_distinction": "Earlier native policy extensions ordered or scheduled already declared packet work from committed evidence. Iteration 18-D adds an experiment-level compatibility scorer that evaluates competing futures and suppresses the non-selected basin.",
    "geometry_driven_selection_supported": false,
    "native_selection_blocker": "compatibility scoring is performed by experiment script logic; a native geometry-driven selection/collapse producer or equivalent surface mechanism is not implemented yet",
    "compositional_lgrc_fork_direction": "Compose two native one-dimensional LGRC route elements into a shared fork and measure whether branch eligibility, budget, and feedback dynamics select a branch without external argmax or compatibility scoring."
  },
  "persistence_axis": {
    "persistence_level": "T6_candidate",
    "persistence_basis": "s3_grid_geometry_scored_selection_recovers_0_15",
    "self_renewed_cycle_count": 3,
    "repeatability_status": "two_flux_shapes_select_distinct_output_basins_with_three_cycle_recovery",
    "recovery_status": "recovers_0_15_geometry_selected_output_routes",
    "recovery_perturbation": 0.15,
    "t6_full_claim_allowed": false,
    "t6_full_claim_blocker": "design_prototype_not_native_selection_collapse_or_port_graph_transfer"
  },
  "geometry_selection_summary": {
    "entry_ceiling": "s3_grid_state_gated_two_input_two_output_routing_candidate",
    "selected_basins": {
      "north_curved_flux": "north_output_basin",
      "east_curved_flux": "east_output_basin"
    },
    "selected_outputs": {
      "north_curved_flux": 7,
      "east_curved_flux": 13
    },
    "compatibility_scores": {
      "north_curved_flux": {
        "north_output_basin": 0.9805806756909201,
        "east_output_basin": 0.19611613513818402
      },
      "east_curved_flux": {
        "north_output_basin": 0.19611613513818402,
        "east_output_basin": 0.9805806756909201
      }
    }
  },
  "controls": {
    "competition_disabled": "competition_selection_disabled",
    "ambiguous_tie_flux": "ambiguous_competing_basin_scores",
    "wrong_output_basin": "geometry_score_rejects_wrong_output_basin",
    "diagonal_shortcut": "diagonal_route_shortcuts_disabled_by_fixture_policy"
  },
  "checks": {
    "selection_collapse_reasoning_recorded": true,
    "competing_output_basins_declared_before_run": true,
    "compatibility_scoring_rule_declared_before_run": true,
    "selection_derived_from_flux_shape_and_geometry": true,
    "distinct_flux_shapes_select_distinct_basins": true,
    "m6_geometry_selection_candidate_passed": true,
    "selection_not_identity_collapse_or_agency": true,
    "native_geometry_selection_not_yet_supported": true,
    "external_selection_logic_blocker_recorded": true,
    "compositional_lgrc_fork_direction_recorded": true,
    "broader_claims_blocked": true
  },
  "go_no_go_for_iteration_19": {
    "iteration_19_allowed": true,
    "port_graph_ceiling_to_test": "s3_grid_geometry_scored_selection_design_prototype"
  },
  "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate"
}
```

Notes:

- Iteration 18-D is closer to the theory's selection/collapse intuition than
  18-C: both output basins exist, and input flux shape resolves to the basin
  with stronger geometry/flux compatibility.
- This is still a design prototype. Compatibility scoring is experiment-level
  logic over native LGRC packet/surface/feedback primitives.
- This is different from the prior native LGRC policy extensions: those
  ordered or scheduled already-declared packet work from committed evidence,
  while 18-D evaluates competing output futures and suppresses the losing
  basin with experiment-level scoring logic.
- Native geometry-driven selection/collapse, RC identity collapse, semantic
  choice, agency, port-graph transfer, adaptive-topology, locomotion-like,
  biological, identity-acceptance, inherited-N03, and unrestricted movement
  claims remain blocked.

## Iteration 18-E. S3 Grid Composed 1D Fork Competition

Status: Passed.

Reasoning:

- Iteration 18-D is a useful example of the geometry/flux relation we want, but
  its scorer is external experiment logic.
- The next stricter probe should compose two native one-dimensional LGRC route
  elements into a fork and measure whether branch eligibility, budget, and
  feedback dynamics select one branch without external argmax or compatibility
  scoring.
- If both branches remain equally eligible, that is a meaningful negative
  result: current LGRC composition does not yet provide branch arbitration.

- [x] Declare two 1D LGRC branch elements and their shared fork source before
  the run.
- [x] Use the same native causal pulse-substrate surface and feedback producer
  semantics on both branches.
- [x] Prohibit external geometry compatibility scoring, direct argmax
  selection, direct branch suppression, and preauthored input-to-output lookup.
- [x] Measure branch dominance, branch survival, feedback-renewed cycle count,
  budget exhaustion, or failed arbitration as observables.
- [x] Run symmetric-tie, single-branch-disabled, swapped-flux, and
  budget-limited controls with distinct blockers.
- [x] Record whether the result is native branch competition, no-arbitration,
  or requires a new native branch-competition primitive.
- [x] Keep RC identity-collapse, semantic choice, agency, adaptive-topology,
  port-graph, locomotion-like, biological, inherited-N03, and unrestricted
  movement claims blocked.

Expected artifacts:

- [x] `outputs/n04_iter18e_grid_composed_1d_fork_competition_report.json`
- [x] `reports/n04_iter18e_grid_composed_1d_fork_competition_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18e_grid_composed_1d_fork_competition.py",
  "status": "passed",
  "claim_ceiling": "s3_grid_composed_1d_fork_competition_candidate",
  "result_role": "compositional_lgrc_fork_competition_probe",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "grid",
  "movement_substrate": "S3_grid_composed_1d_fork_v1",
  "native_support_boundary": {
    "native_lgrc_packet_work_used": true,
    "native_causal_pulse_substrate_surface_used": true,
    "native_feedback_eligibility_surface_used": true,
    "native_feedback_producer_used": true,
    "native_artifact_validator_used": true,
    "external_geometry_scorer_used": false,
    "external_argmax_used": false,
    "native_branch_competition_supported": true,
    "native_branch_arbitration_supported": false,
    "selection_mechanism": "branch_eligibility_differentiation_from_composed_1d_elements",
    "arbitration_blocker": "When both branches are eligible, current LGRC producer semantics expose a tie/no-arbitration state rather than choosing one branch."
  },
  "composition_summary": {
    "entry_ceiling": "s3_grid_geometry_scored_selection_design_prototype",
    "positive_result": "Composed 1D branch elements can produce branch differentiation by native feedback eligibility without an external scorer.",
    "remaining_blocker": "A symmetric eligible fork produces no native arbitration; selection is supported only when geometry/capacity makes one branch eligible and the other subthreshold.",
    "selected_branches": {
      "north_branch_capacity_dominant": "north_branch",
      "east_branch_capacity_dominant": "east_branch"
    }
  },
  "controls": {
    "symmetric_tie_no_arbitration": "both_branches_eligible_no_native_arbitration",
    "single_branch_disabled": "east_branch_producer_disabled",
    "budget_limited_subthreshold": "branch_polarity_below_feedback_threshold",
    "wrong_polarity": "feedback_wrong_polarity"
  },
  "checks": {
    "two_1d_branch_elements_declared": true,
    "shared_fork_source_declared": true,
    "native_surface_and_feedback_used_on_both_branches": true,
    "external_geometry_scorer_absent": true,
    "external_argmax_absent": true,
    "direct_branch_suppression_absent": true,
    "preauthored_input_to_output_lookup_absent": true,
    "branch_selection_by_native_eligibility": true,
    "native_arbitration_not_supported": true,
    "symmetric_tie_exposes_no_arbitration": true,
    "m6_composed_fork_candidate_passed": true,
    "broader_claims_blocked": true
  },
  "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate"
}
```

Notes:

- Iteration 18-E is the first composition-to-2D result: two native 1D branch
  elements form a fork and branch differentiation comes from native feedback
  eligibility, not an external scorer.
- The result is still bounded. It supports branch competition only when
  geometry/capacity makes one branch eligible and the other subthreshold.
- Symmetric eligible forks remain a blocker: current LGRC records
  no-arbitration rather than choosing one branch.
- Native branch arbitration, native LGRC choice selection, RC identity
  collapse, semantic choice, agency, port-graph transfer, adaptive-topology,
  locomotion-like, biological, identity-acceptance, inherited-N03, and
  unrestricted movement claims remain blocked.

## Iteration 18-F. Balanced Local Preference Fork Tie-Breaking

Status: Passed.

Reasoning:

- Iteration 18-E showed native branch differentiation by composed 1D
  eligibility, but exact/symmetric eligible forks still had no native
  arbitration.
- A single global epsilon would be a hidden selector. Iteration 18-F therefore
  uses paired local preferences whose global branch-preference sum is zero.
- The local epsilon may break near-ties, but it must not override real branch
  evidence or become native choice/collapse.

- [x] Declare the balanced local preference policy before the run, including
  epsilon, local preference sites, and global preference sum.
- [x] Verify no-preference fork still reproduces the 18-E no-arbitration
  blocker.
- [x] Verify paired local preferences resolve local near-ties in opposite
  directions.
- [x] Verify the global branch-preference sum is zero.
- [x] Verify a dominant opposing branch overrides local preference.
- [x] Verify epsilon does not force a choice when both branches remain strongly
  eligible.
- [x] Verify recovery still uses native packet event -> surface row -> feedback
  eligibility -> scheduled packet work -> `step()` mutation.
- [x] Keep native LGRC choice selection, RC identity collapse, semantic choice,
  agency, adaptive-topology, port-graph, locomotion-like, biological,
  inherited-N03, and unrestricted movement claims blocked.

Expected artifacts:

- [x] `outputs/n04_iter18f_balanced_local_preference_fork_report.json`
- [x] `reports/n04_iter18f_balanced_local_preference_fork_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18f_balanced_local_preference_fork.py",
  "status": "passed",
  "claim_ceiling": "s3_grid_balanced_local_preference_fork_competition_candidate",
  "result_role": "balanced_local_preference_composed_fork_probe",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "grid",
  "movement_substrate": "S3_grid_balanced_local_preference_composed_fork_v1",
  "preference_policy": {
    "epsilon": 0.03,
    "epsilon_role": "local_near_tie_symmetry_breaker_only",
    "global_preference_sum": {
      "north_branch": 0.0,
      "east_branch": 0.0
    },
    "global_directional_preference": "none"
  },
  "balanced_preference_summary": {
    "entry_ceiling": "s3_grid_composed_1d_fork_competition_candidate",
    "positive_result": "Balanced local preferences remove the 18-E no-arbitration tie for near-threshold local forks while keeping global preference sum zero.",
    "remaining_blocker": "This is local symmetry breaking by declared epsilon, not native LGRC choice selection, RC identity collapse, or agency.",
    "selected_branches": {
      "north_local_preference_tie_break": "north_branch",
      "east_local_preference_tie_break": "east_branch",
      "east_dominant_overrides_north_preference": "east_branch"
    }
  },
  "controls": {
    "no_preference_remains_no_arbitration": "both_branches_eligible_no_native_arbitration",
    "north_local_preference_resolves_tie": "east_branch_damped_below_threshold_by_local_epsilon",
    "east_local_preference_resolves_tie": "north_branch_damped_below_threshold_by_local_epsilon",
    "epsilon_not_global_override": "both_strong_branches_remain_eligible_epsilon_does_not_force_choice"
  },
  "checks": {
    "global_preference_sum_zero": true,
    "north_and_east_preferences_resolve_local_ties": true,
    "unbiased_tie_still_exposes_18e_blocker": true,
    "epsilon_does_not_force_global_choice": true,
    "dominant_signal_overrides_local_preference": true,
    "m6_balanced_preference_candidate_passed": true,
    "broader_claims_blocked": true
  },
  "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate"
}
```

Notes:

- Iteration 18-F reduces the 18-E tie/no-arbitration blocker for near-threshold
  forks without using a global selector or external argmax.
- The local preferences are balanced across declared local sites, so the
  aggregate branch-preference sum is zero.
- This is still not native LGRC choice selection, RC identity collapse,
  semantic choice, agency, port-graph transfer, adaptive-topology,
  locomotion-like, biological, identity-acceptance, inherited-N03, or
  unrestricted movement evidence.

## Iteration 18-G. Integrated Fixed-Topology 2D Composed Gate

Status: Passed.

Reasoning:

- Iteration 18-C supplied the two-input/two-output gate shape.
- Iteration 18-D supplied the geometry/flux selection target, but with an
  external scorer.
- Iteration 18-E removed the scorer by composing native 1D branch elements.
- Iteration 18-F added balanced local preferences to reduce near-tie
  no-arbitration without global bias.
- Iteration 18-G integrates those pieces into a fixed-topology 2D composed-gate
  candidate while keeping native choice/collapse and adaptive topology blocked.

- [x] Declare two input gates and two output branches before the run.
- [x] Compose the gate from native one-dimensional LGRC branch elements.
- [x] Use balanced local preferences with zero global branch-preference sum.
- [x] Verify west/south inputs select distinct output branches by native branch
  eligibility, not external scoring or argmax.
- [x] Verify no-preference still reproduces 18-E no-arbitration.
- [x] Verify dominant branch evidence overrides local preference.
- [x] Verify epsilon does not force a choice when both branches remain strongly
  eligible.
- [x] Verify recovery still uses native packet event -> surface row -> feedback
  eligibility -> scheduled packet work -> `step()` mutation.
- [x] Keep native LGRC choice selection, RC identity collapse, semantic choice,
  agency, adaptive-topology, port-graph, locomotion-like, biological,
  inherited-N03, and unrestricted movement claims blocked.

Expected artifacts:

- [x] `outputs/n04_iter18g_integrated_2d_composed_gate_report.json`
- [x] `reports/n04_iter18g_integrated_2d_composed_gate_report.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18g_integrated_2d_composed_gate.py",
  "status": "passed",
  "claim_ceiling": "s3_grid_integrated_2d_composed_gate_candidate",
  "result_role": "integrated_fixed_topology_2d_composed_gate_probe",
  "achieved_movement_level": "M6",
  "geometry_scope": "transferred_geometry",
  "substrate_class": "grid",
  "movement_substrate": "S3_grid_integrated_2d_composed_gate_v1",
  "integrated_gate_summary": {
    "entry_ceiling": "s3_grid_balanced_local_preference_fork_competition_candidate",
    "positive_result": "The 18-C two-input/two-output gate structure is integrated with 18-E composed 1D branch competition and 18-F balanced local preferences, using native branch eligibility rather than external scoring.",
    "remaining_blocker": "The result is fixed-topology 2D composed-gate evidence, not native LGRC choice selection, RC collapse, port-graph, or adaptive topology.",
    "selected_branches": {
      "west_input": "north_branch",
      "south_input": "east_branch"
    }
  },
  "controls": {
    "no_preference_reproduces_18e_no_arbitration": "both_branches_eligible_no_native_arbitration",
    "dominant_branch_overrides_local_preference": "dominant_east_branch_remains_eligible_despite_north_local_preference",
    "epsilon_does_not_force_strong_two_branch_choice": "both_strong_branches_remain_eligible",
    "global_preference_sum_zero": "paired_local_preferences_cancel_globally"
  },
  "checks": {
    "two_input_gates_declared": true,
    "two_output_branches_declared": true,
    "composed_1d_branches_used": true,
    "balanced_local_preferences_used": true,
    "global_preference_sum_zero": true,
    "external_scorer_absent": true,
    "external_argmax_absent": true,
    "west_and_south_inputs_select_distinct_outputs": true,
    "native_branch_eligibility_selects_outputs": true,
    "no_preference_reproduces_18e_no_arbitration": true,
    "dominant_branch_overrides_local_preference": true,
    "epsilon_does_not_force_strong_two_branch_choice": true,
    "m6_integrated_2d_gate_candidate_passed": true,
    "broader_claims_blocked": true
  },
  "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate"
}
```

Notes:

- Iteration 18-G is the first integrated fixed-topology 2D composed-gate
  candidate: two inputs, two outputs, composed 1D branch competition, and
  balanced local preference tie-breaking.
- It is still not native LGRC choice selection, RC identity collapse, semantic
  choice, agency, port-graph transfer, adaptive-topology, locomotion-like,
  biological, identity-acceptance, inherited-N03, or unrestricted movement
  evidence.

## Iteration 18-H. S3 Grid Series Closeout

Status: Passed.

Iteration 18-H is a summary-only closeout for the S3 grid series. It runs no
new probe.

- [x] Consume Iterations 18, 18-B, 18-C, 18-D, 18-E, 18-F, and 18-G artifacts as
  source inputs.
- [x] Record the strongest scoped S3 ceiling as
  `s3_grid_integrated_2d_composed_gate_candidate`.
- [x] Preserve the progression from route-defined grid survival through
  fixed-topology integrated 2D composed gate.
- [x] Explicitly record that 18-D used an external scorer and that
  18-E/18-F/18-G remove that scorer by composition plus balanced local
  preferences.
- [x] Keep native LGRC choice selection, RC identity collapse, semantic choice,
  agency, port-graph transfer, adaptive topology, locomotion-like, biological,
  inherited-N03, and unrestricted movement claims blocked.
- [x] Route Iteration 19 to test whether the S3 fixed-topology 2D composed-gate
  ceiling transfers to S7 port mechanics.

Expected artifacts:

- [x] `outputs/n04_iter18h_s3_grid_series_closeout.json`
- [x] `reports/n04_iter18h_s3_grid_series_closeout.md`

Run record:

```json
{
  "command": ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_iter18h_s3_grid_series_closeout.py",
  "status": "passed",
  "claim_ceiling": "s3_grid_integrated_2d_composed_gate_candidate",
  "achieved_movement_level": "M6",
  "persistence_level": "T6_candidate",
  "strongest_scoped_ceiling": "s3_grid_integrated_2d_composed_gate_candidate",
  "integration_path": [
    "route_defined_grid_survival",
    "two_axis_turn",
    "two_input_two_output_design",
    "geometry_flux_selection_prototype_external_scorer_blocked",
    "composed_1d_fork_competition_without_external_scorer",
    "balanced_local_preference_tie_breaking_without_global_bias",
    "integrated_fixed_topology_2d_composed_gate"
  ],
  "blocked_claims": [
    "native_lgrc_choice_selection",
    "rc_identity_collapse",
    "semantic_choice",
    "agency",
    "port_graph_transfer",
    "adaptive_topology_movement",
    "topology_mutating_movement",
    "broad_geometry_transfer",
    "locomotion_like_basin_dynamics",
    "biological_behavior",
    "identity_acceptance",
    "movement_inherited_from_n03",
    "unrestricted_movement"
  ],
  "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate"
}
```

## Iteration 19. S7 Port-Graph Mapping Contract

Status: Passed.

- [x] Consume Iteration 18-H as the source ceiling.
- [x] Define `s3_integrated_2d_gate_to_s7_fixed_port_graph_v1` as a
  role-based port mapping, not node-id preserving.
- [x] Declare west/south input ports, north/east output ports, shared fork,
  branch ports, and balance ports.
- [x] Freeze balanced local preference representation with zero global
  preference sum.
- [x] Record topology mutation, edge rewiring, port creation, and port deletion
  as disabled by default.
- [x] Run no behavior probe and preserve the claim boundary.
- [x] Keep port-graph transfer, adaptive topology, topology-mutating movement,
  native LGRC choice selection, RC identity collapse, semantic choice, agency,
  locomotion-like behavior, biological, inherited-N03, and unrestricted
  movement claims blocked.

Artifacts:

- `outputs/n04_iter19_s7_port_graph_mapping_contract.json`
- `reports/n04_iter19_s7_port_graph_mapping_contract.md`

Result:

```json
{
  "status": "passed",
  "claim_ceiling": "s7_port_graph_mapping_contract_only",
  "mapping_id": "s3_integrated_2d_gate_to_s7_fixed_port_graph_v1",
  "mapping_type": "role_based_port_mapping",
  "node_id_preserving": false,
  "topology_mutation_enabled": false,
  "next_iteration": "19a_s7_fixed_port_execution"
}
```

Acceptance:

Iteration 19 freezes the role-based S3-to-S7 fixed-port mapping before
execution. It runs no behavior probe and does not promote claims. Topology
mutation, port rewiring, adaptive topology, native LGRC choice selection, RC
identity collapse, locomotion-like behavior, agency, and unrestricted movement
remain blocked.

## Iteration 19-A. S7 Fixed-Port Composed-Gate Execution

Status: Passed.

- [x] Consume Iteration 19 mapping contract.
- [x] Execute `west_in -> north_out` and `south_in -> east_out` fixed-port
  lanes.
- [x] Verify output selection is produced by native branch eligibility, not an
  external scorer or argmax.
- [x] Verify artifact-only validators pass for native packet event -> surface
  row -> feedback eligibility -> scheduled packet -> processed packet chains.
- [x] Verify budget, nonnegative, identity/shape, and recovery gates pass.
- [x] Preserve no-preference, dominant-branch, and strong-two-branch controls
  from the S3 composed-gate series.
- [x] Verify topology mutation and port rewiring remain disabled and no
  topology events are emitted.
- [x] Keep adaptive topology, topology-mutating movement, native LGRC choice
  selection, RC identity collapse, semantic choice, agency, locomotion-like
  behavior, biological, inherited-N03, and unrestricted movement claims
  blocked.

Artifacts:

- `outputs/n04_iter19a_s7_fixed_port_execution_report.json`
- `reports/n04_iter19a_s7_fixed_port_execution_report.md`

Result:

```json
{
  "status": "passed",
  "claim_ceiling": "s7_fixed_port_composed_gate_candidate",
  "achieved_movement_level": "M6",
  "persistence_level": "T6_candidate",
  "west_port_selects_north_output": true,
  "south_port_selects_east_output": true,
  "topology_mutation_disabled": true,
  "no_topology_events": true,
  "no_port_rewiring": true,
  "adaptive_topology_entry_allowed": false,
  "topology_mutating_movement_claim_allowed": false
}
```

Acceptance:

Iteration 19-A transfers the S3 fixed-topology 2D composed-gate result to an
S7 fixed-port graph. West input selects the north output and south input
selects the east output by native branch eligibility under the frozen mapping.
The result is a fixed-port port-graph candidate only. It does not support
adaptive topology, topology-mutating movement, native LGRC choice selection,
RC identity collapse, semantic choice, agency, locomotion-like behavior,
biological behavior, identity acceptance, inherited-N03 movement, or
unrestricted movement.

## Iteration 19-B. S7 Topology-Lineage / Adaptive Gate

Status: Passed as fail-closed boundary probe; external runtime blocker resolved by Phase 8.

- [x] Preserve Iteration 19-A as the topology-disabled fixed-port baseline.
- [x] Verify native LGRC-3 topology/lineage replay is available and budget
  conserving.
- [x] Attempt causal pulse-substrate surface lineage transport.
- [x] Record the blocker: causal pulse-substrate surface rows v1 require
  `fixed_topology` lineage status.
- [x] Reject topology-only displacement promotion.
- [x] Keep `adaptive_topology_entry_allowed = false`.
- [ ] Decide whether M6 should remain one rung with geometry tags, or split
  into evidence-driven subtypes such as:

```text
M6a same-fixture self-renewal
M6b geometry-transferred self-renewal
M6c topology-lineage-preserving self-renewal
```

- [x] Do not introduce subtype names as claims until evidence exists.
- [ ] Regenerate the M-taxonomy visual reference pack with accepted geometry
  transfer evidence, preserving the visual-reference claim boundary.
- [x] Record taxonomy-continuation closeout:
  - [x] all declared geometry probes completed or explicitly deferred with
    rationale;
  - [x] tag schema validated on S0 plus at least two of S1, S3, or S4 before
    any broad geometry-transfer claim is considered;
  - [x] strongest ceiling per geometry recorded;
  - [x] adaptive-topology open/blocked decision recorded.

Artifacts:

- `outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json`
- `reports/n04_iter19b_topology_lineage_adaptive_gate_report.md`

Result:

```json
{
  "status": "passed",
  "result_kind": "expected_fail_closed_boundary_probe",
  "claim_ceiling": "s7_fixed_port_composed_gate_candidate",
  "promotion_result": "blocked",
  "primary_blocker": "causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status",
  "primary_blocker_current_status": "resolved_externally_by_phase8_lineage_closeout",
  "native_lgrc3_topology_lineage_replay_passed": true,
  "surface_v1_rejects_lineage_transport_rows": true,
  "adaptive_topology_gate_passed": false,
  "topology_mutating_movement_gate_passed": false,
  "next_iteration": "19-C_s7_topology_lineage_adaptive_gate_with_native_surface_lineage"
}
```

Acceptance:

Iteration 19-B is a useful negative boundary result. Native LGRC-3 topology
lineage evidence is available and replay-valid with conserved budget, but the
native causal pulse-substrate surface v1 cannot transport surface rows through
topology lineage because its row schema requires `fixed_topology` lineage
status. The current ceiling remains `s7_fixed_port_composed_gate_candidate`.
Adaptive topology, topology-mutating movement, native pulse-surface topology
lineage transport, native LGRC choice selection, RC identity collapse,
locomotion-like behavior, agency, identity acceptance, and unrestricted
movement remain blocked.

Post-Phase 8 closeout:

```text
phase8_claim_ceiling = native_causal_pulse_substrate_surface_lineage_transport_supported
phase8_closeout = implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md
full_regression_after_phase8 = 1529 passed, 684 subtests passed
```

The original 19-B adaptive-topology promotion remains blocked. The runtime
blocker it exposed is now resolved externally, so the next N04 task is
Iteration 19-C.

## N04 Taxonomy Continuation Closeout And Phase 8 Return

Status: Passed; Phase 8 return path is now active.

- [x] Consume taxonomy inventory and tag schema artifacts.
- [x] Consume Iteration 19-A fixed-port candidate and Iteration 19-B
  fail-closed topology-lineage boundary probe.
- [x] Preserve current ceiling as `s7_fixed_port_composed_gate_candidate`.
- [x] Record the Phase 8 blocker:
  `causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status`.
- [x] Route next runtime work to
  `Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md` and
  `Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md`.
- [x] Record return path to N04 Iteration 19-C after Phase 8.
- [x] Record Phase 8 surface-lineage closeout:
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md`.
- [x] Record that N04 resumed at Iteration 19-C and the adaptive-topology
  entry candidate is now supported.

Artifacts:

- `outputs/n04_taxonomy_continuation_closeout.json`
- `reports/n04_taxonomy_continuation_closeout.md`

Result:

```json
{
  "status": "passed",
  "current_claim_ceiling": "s7_fixed_port_composed_gate_candidate",
  "primary_blocker": "causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status",
  "primary_blocker_current_status": "resolved_externally_by_phase8_lineage_closeout",
  "phase8_closeout": "native causal pulse-substrate surface lineage transport supported",
  "return_to_n04_after_phase8": "N04 Iteration 19-C",
  "iteration_19c_status": "passed",
  "current_claim_ceiling": "adaptive_topology_entry_candidate",
  "current_next_step": "topology-mutating movement review or N04 closeout"
}
```

Acceptance:

N04 has a clean post-Phase 8 return point and Iteration 19-C has now consumed
it. The current ceiling is `adaptive_topology_entry_candidate`. Full
topology-mutating movement remains blocked until a stricter follow-up gate is
opened and validated.

## Iteration 19-C. S7 Adaptive Gate With Native Surface Lineage

Status: Passed.

- [x] Consume Phase 8 surface-lineage closeout:
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md`.
- [x] Preserve Iteration 19-A as the fixed-port baseline.
- [x] Enable native causal pulse-substrate surface lineage transport under
  LGRC-3 topology-changing causal history.
- [x] Rerun the S7 topology-lineage/adaptive gate.
- [x] Verify topology events produce transported or superseded surface rows.
- [x] Verify producers read transported surface digests, not stale source
  digests.
- [x] Verify artifact-only lineage replay passes on the 19-C artifacts.
- [x] Verify topology-only claim promotion remains blocked.
- [x] Preserve budget, identity/shape, and producer/step boundary audits.
- [x] Decide whether `adaptive_topology_entry_candidate` is supported or still
  blocked by a new reason.
- [x] Keep topology-mutating movement, native LGRC choice selection, RC
  identity collapse, agency, locomotion-like behavior, biological behavior,
  identity acceptance, and unrestricted movement blocked unless independently
  validated.

Artifacts:

- `outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json`
- `reports/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.md`

Result:

```json
{
  "iteration": "19-C",
  "input_ceiling": "s7_fixed_port_composed_gate_candidate",
  "phase8_lineage_transport_supported": true,
  "adaptive_topology_entry_allowed": true,
  "claim_ceiling": "adaptive_topology_entry_candidate",
  "producer_reads_transported_digest": true,
  "artifact_only_lineage_replay_passed": true,
  "superseded_source_read_blocked": true,
  "movement_claim_allowed": false,
  "topology_mutating_movement_claim_allowed": false
}
```

Acceptance:

Iteration 19-C closes the runtime blocker exposed by 19-B and supports an
`adaptive_topology_entry_candidate`. Native causal pulse-substrate surface
lineage transport is enabled under LGRC-3, committed topology events transport
or supersede surface rows, producers read transported surface digests rather
than stale source digests, stale source reads are blocked, and artifact-only
lineage replay passes. This is adaptive-topology entry evidence only: it does
not validate post-topology packet scheduling as movement, topology-mutating
movement, native LGRC choice selection, RC identity collapse, agency,
locomotion-like behavior, biological behavior, identity acceptance, inherited
N03 movement, or unrestricted movement.

## Iteration 19-D. Topology-Mutating Movement Probe

Status: Passed, fail-closed boundary.

- [x] Consume Iteration 19-C adaptive-topology entry evidence.
- [x] Attempt the stricter promotion to
  `topology_mutating_movement_candidate`.
- [x] Require a committed topology event and transported native
  pulse-substrate surface row.
- [x] Attempt post-topology packet work through the native coupling producer.
- [x] Verify whether the producer can schedule and `step()` can process the
  post-topology packet work.
- [x] Preserve artifact-only lineage replay for the transported surface row.
- [x] Preserve stale-source-read and topology-only claim-promotion controls.
- [x] Keep topology-mutating movement, native LGRC choice selection, RC
  identity collapse, agency, locomotion-like behavior, biological behavior,
  identity acceptance, and unrestricted movement blocked unless the strict
  post-topology packet-work gate passes.

Artifacts:

- `outputs/n04_iter19d_topology_mutating_movement_probe.json`
- `reports/n04_iter19d_topology_mutating_movement_probe.md`

Result:

```json
{
  "iteration": "19-D",
  "input_ceiling": "adaptive_topology_entry_candidate",
  "attempted_promotion": "topology_mutating_movement_candidate",
  "promotion_result": "blocked",
  "primary_blocker": "packet_ledger_state_reabsorption_mismatch_after_topology_event",
  "topology_event_logged": true,
  "active_graph_topology_mutated": false,
  "transported_surface_row_emitted": true,
  "artifact_only_lineage_replay_passed": true,
  "post_topology_packet_scheduled": false,
  "post_topology_packet_processed_by_step": false,
  "claim_ceiling": "adaptive_topology_entry_candidate",
  "topology_mutating_movement_claim_allowed": false
}
```

Acceptance:

Iteration 19-D is the first strict topology-mutating movement probe after the
19-C adaptive-entry result. It confirms that native surface lineage remains
valid but actual topology-mutating movement is still blocked: current LGRC
records the topology/lineage event and transports surface evidence, but does
not yet complete native active-state plus packet-ledger reabsorption needed
for post-topology packet work. The required next runtime mechanism is native
topology-state reabsorption that updates/rebases active graph state and packet
ledger totals together.

## Iteration 19-E. Topology-Mutating Movement After State Reabsorption

Status: Passed, candidate supported.

- [x] Consume Phase 8 topology-state reabsorption closeout:
  `implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`.
- [x] Rerun the 19-D strict topology-mutating movement probe with native
  topology-state reabsorption enabled.
- [x] Require a committed topology event and transported native
  pulse-substrate surface row.
- [x] Require a topology-state reabsorption record for the same topology event.
- [x] Require producer scheduling from the transported surface digest and
  matching topology-state reabsorption record digest.
- [x] Require `step()` to process the scheduled post-topology packet work.
- [x] Preserve artifact-only replay over packet, surface, topology,
  reabsorption, producer, and scheduled/processed packet evidence.
- [x] Preserve stale-source-read and disabled-reabsorption controls.
- [x] Keep native LGRC choice selection, RC identity collapse, agency,
  locomotion-like behavior, biological behavior, identity acceptance,
  inherited-N03 movement, and unrestricted movement blocked.

Artifacts:

- `outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json`
- `reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md`

Result:

```json
{
  "iteration": "19-E",
  "input_ceiling": "adaptive_topology_entry_candidate",
  "attempted_promotion": "topology_mutating_movement_candidate",
  "promotion_result": "supported_candidate",
  "claim_ceiling": "topology_mutating_movement_candidate",
  "topology_state_reabsorption_record_emitted": true,
  "ledger_state_reabsorption_gap_resolved": true,
  "post_topology_packet_work_scheduled": true,
  "post_topology_packet_work_processed_by_step": true,
  "post_topology_packet_budget_exact": true,
  "artifact_only_replay_passed": true,
  "topology_mutating_movement_claim_allowed": true,
  "native_lgrc_choice_selection_claim_allowed": false,
  "rc_identity_collapse_claim_allowed": false,
  "agency_claim_allowed": false,
  "locomotion_like_claim_allowed": false
}
```

Acceptance:

Iteration 19-E closes the runtime blocker recorded by 19-D and supports a
`topology_mutating_movement_candidate`: the committed topology event transports
the native surface row, active state and packet ledger are reabsorbed together,
the coupling producer schedules post-topology packet work from the transported
surface plus matching reabsorption record, `step()` processes the scheduled
departure/arrival, and node-plus-packet budget remains exact. This is still not
native LGRC choice selection, RC identity collapse, agency, locomotion-like
behavior, biological behavior, identity acceptance, inherited-N03 movement, or
unrestricted movement.

## Iteration 19 Closeout. Port-Graph And Topology-Mutating Movement Tranche

Status: Complete.

- [x] Close the Iteration 19 / S7 port-graph tranche.
- [x] Record current N04 ceiling:
  `topology_mutating_movement_candidate`.
- [x] Preserve claim boundary:
  native LGRC choice selection, RC identity collapse, agency,
  locomotion-like behavior, biological behavior, identity acceptance,
  inherited-N03 movement, and unrestricted movement remain blocked.
- [x] Record next exploration topics as future iterations, not as implicit
  promotions inside Iteration 19.

Result:

```json
{
  "iteration": "19_closeout",
  "status": "complete",
  "current_claim_ceiling": "topology_mutating_movement_candidate",
  "closed_tranche": "s7_port_graph_and_topology_mutating_movement",
  "next_iterations": [
    "20_topology_mutating_repeatability_and_stress",
    "21_native_lgrc_choice_selection_boundary",
    "22_identity_through_topology_mutation_boundary",
    "23_topology_mutating_taxonomy_closeout"
  ]
}
```

## Iteration 20. Topology-Mutating Repeatability And Stress

Status: Complete.

Question:

```text
Does the 19-E topology-mutating movement candidate survive repeated cycles,
reversed direction, perturbation, and multiple topology events?
```

Initial checks:

- [x] Consume Iteration 19-E as baseline.
- [x] Run repeated topology-mutating cycles, not one isolated event.
- [x] Run reversed-direction or matched-opposite topology-mutating lane.
- [x] Add perturbation before or after topology mutation.
- [x] Test multiple committed topology events in one run.
- [x] Preserve exact node-plus-packet budget.
- [x] Preserve artifact-only replay for repeatability, reversed, perturbation,
  and multi-topology-event lanes after Phase 8 time-scoped lineage replay
  hardening.
- [x] Keep choice, agency, identity-collapse, locomotion-like, biological,
  inherited-N03, and unrestricted movement claims blocked.

Run record:

```json
{
  "iteration": "20",
  "status": "passed",
  "claim_ceiling": "topology_mutating_movement_candidate",
  "stress_result": "repeatability_stress_supported",
  "repeatability_runs": "3/3",
  "reversed_matched_lane": "passed",
  "lineage_accounted_perturbation_lane": "passed",
  "multiple_topology_events_runtime": "passed",
  "multiple_topology_events_artifact_replay": "passed",
  "primary_blocker": null,
  "next_iteration": "21_native_lgrc_choice_selection_boundary"
}
```

Artifacts:

- `outputs/n04_iter20_topology_mutating_repeatability_stress.json`
- `reports/n04_iter20_topology_mutating_repeatability_stress.md`

Iteration 20 strengthens the 19-E result across repeatability, reversed, and
lineage-accounted perturbation lanes. It also validates a multi-topology-event
single run after Phase 8 time-scoped lineage replay hardening: the runtime
handles multiple committed topology events with exact budget and post-topology
packet processing, and artifact-only replay now accepts historically valid
producer reads that happened before a later topology transport.

## Iteration 21. Native LGRC Choice Selection Boundary

Status: Complete.

Question:

```text
Can topology mutation resolve competing available routes without external
selection logic?
```

Initial checks:

- [x] Start from the 19-E/20 topology-mutating movement candidate.
- [x] Construct competing eligible topology-mutating routes.
- [x] Require route resolution to come from native LGRC state, lineage,
  budget, timing, or local geometry, not experiment-level if/else logic.
- [x] Distinguish deterministic local preference from genuine native choice.
- [x] Preserve no-choice controls where competing branches remain unresolved.
- [x] Keep agency, semantic choice, RC identity collapse, locomotion-like,
  biological, inherited-N03, and unrestricted movement claims blocked unless
  separately validated.

Run record:

```json
{
  "iteration": "21",
  "status": "passed",
  "attempted_promotion": "native_lgrc_choice_selection_candidate",
  "promotion_result": "blocked",
  "claim_ceiling": "topology_mutating_movement_candidate",
  "primary_blocker": "native_lgrc_topology_route_selection_not_exposed",
  "candidate_routes_executable_when_supplied": true,
  "route_a_artifact_replay_passed": true,
  "route_b_artifact_replay_passed": true,
  "next_iteration": "22_identity_through_topology_mutation_boundary"
}
```

Artifacts:

- `outputs/n04_iter21_native_lgrc_choice_selection_boundary.json`
- `reports/n04_iter21_native_lgrc_choice_selection_boundary.md`

Iteration 21 shows that multiple topology-mutating continuations are
executable and artifact-valid when supplied, but current LGRC does not natively
choose among unresolved competing topology routes. Route selection still enters
through experiment-supplied topology-event arguments (`selected_sink_id` and
lineage map). Balanced local preference remains deterministic bias, not native
choice selection, semantic choice, agency, or RC identity collapse.

## Iteration 21-B. Native LGRC Route-Arbitration Rerun

Status: Complete.

Question:

```text
After Phase 8 native route arbitration, can the route-selection boundary be
rerun with a native route-arbitration record as the causal selection source?
```

Initial checks:

- [x] Consume Iteration 20 and Phase 8 native route-arbitration closeout.
- [x] Emit candidate topology-route records from committed runtime-visible
  evidence.
- [x] Emit a candidate-set record with two competing topology-mutating routes.
- [x] Select exactly one route through a native route-arbitration record.
- [x] Commit the selected topology event from that route-arbitration record.
- [x] Verify surface lineage, topology-state reabsorption, producer scheduling,
  and `step()` processing consume the selected topology event.
- [x] Validate the selected-route chain artifact-only.
- [x] Preserve unresolved-tie and hidden-input controls.
- [x] Keep semantic choice, agency, RC identity collapse, identity acceptance,
  locomotion-like, biological, inherited-N03, and unrestricted movement claims
  blocked.

Run record:

```json
{
  "iteration": "21-B",
  "status": "passed",
  "attempted_promotion": "native_lgrc_route_arbitration_selection_candidate",
  "promotion_result": "runtime_route_arbitration_supported_choice_claim_blocked",
  "claim_ceiling": "topology_mutating_movement_candidate",
  "previous_primary_blocker": "native_lgrc_topology_route_selection_not_exposed",
  "primary_blocker": null,
  "native_route_arbitration_supported": true,
  "old_route_selection_blocker_resolved": true,
  "artifact_only_route_arbitration_replay_passed": true,
  "unresolved_tie_control_blocks_selection": true,
  "hidden_input_control_blocks_selection": true,
  "next_iteration": "22-B_or_23_topology_mutating_taxonomy_closeout"
}
```

Artifacts:

- `outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json`
- `reports/n04_iter21b_native_lgrc_route_arbitration_rerun.md`
- `scripts/run_n04_iter21b_native_lgrc_route_arbitration_rerun.py`

Iteration 21-B resolves the old route-selection exposure blocker as runtime
route arbitration: candidate routes are formed from committed runtime-visible
evidence, serialized policy selects one route, the selected topology event
cites the arbitration record, and artifact-only replay reconstructs the
downstream lineage/reabsorption/producer/step chain. This is not semantic
choice, agency, or RC identity collapse.

## Iteration 22. Identity Through Topology Mutation Boundary

Status: Complete.

Question:

```text
Does the moved entity remain a runtime coherence basin through topology
mutation, or is the evidence still a boundary/surface signal?
```

Initial checks:

- [x] Consume Iterations 20 and 21 and the RC identity boundary rules.
- [x] Audit identity kind and identity surface before topology mutation.
- [x] Audit identity kind and identity surface after topology mutation.
- [x] Verify whether the moved entity is a runtime coherence basin or only a
  transported surface/boundary signal.
- [x] Preserve deformation-token and boundary-signal blockers where applicable.
- [x] Keep RC identity collapse, identity acceptance, agency, locomotion-like,
  biological, inherited-N03, and unrestricted movement claims blocked unless
  separately validated.

Run record:

```json
{
  "iteration": "22",
  "status": "passed",
  "attempted_promotion": "rc_identity_through_topology_mutation_candidate",
  "promotion_result": "blocked",
  "claim_ceiling": "topology_mutating_movement_candidate",
  "primary_blocker": "rc_identity_basin_invariance_not_validated_across_topology_mutation",
  "topology_lineage_continuity_passed": true,
  "reabsorbed_state_continuity_passed": true,
  "producer_schedules_from_current_reabsorbed_evidence": true,
  "artifact_only_replay_passed": true,
  "rc_identity_through_topology_supported": false,
  "identity_acceptance_supported": false,
  "next_iteration": "23_topology_mutating_taxonomy_closeout"
}
```

Artifacts:

- `outputs/n04_iter22_identity_through_topology_mutation_boundary.json`
- `reports/n04_iter22_identity_through_topology_mutation_boundary.md`

Iteration 22 shows that native artifacts prove topology-aware continuity of
surface evidence, active state, packet ledger, and producer scheduling through
topology mutation. The result does not serialize a stable RC coherence-basin
identity or validate attractor-basin invariance, so RC identity through
topology mutation, RC identity collapse, and identity acceptance remain blocked.

## Iteration 22-B. Identity Through Native Route-Arbitrated Topology

Status: Complete.

Question:

```text
After native route arbitration selects the topology-mutating route, does the
moved entity now satisfy RC identity through topology mutation?
```

Initial checks:

- [x] Consume Iteration 21-B selected native route-arbitrated topology event.
- [x] Verify native route arbitration, selected topology event, surface
  lineage, topology-state reabsorption, producer scheduling, and `step()`
  processing replay artifact-only.
- [x] Audit identity kind and identity surface before and after the selected
  topology event.
- [x] Check whether native route arbitration adds stable RC coherence-basin
  identity or attractor-basin invariance evidence.
- [x] Keep semantic choice, agency, RC identity collapse, identity acceptance,
  locomotion-like, biological, inherited-N03, and unrestricted movement claims
  blocked.

Run record:

```json
{
  "iteration": "22-B",
  "status": "passed",
  "attempted_promotion": "rc_identity_through_native_route_arbitrated_topology_candidate",
  "promotion_result": "blocked",
  "claim_ceiling": "topology_mutating_movement_candidate",
  "primary_blocker": "rc_identity_basin_invariance_not_validated_across_topology_mutation",
  "native_route_arbitration_supported": true,
  "native_route_arbitrated_topology_continuity_supported": true,
  "route_artifact_replay_passed": true,
  "surface_lineage_artifact_replay_passed": true,
  "rc_identity_through_native_route_arbitrated_topology_supported": false,
  "identity_acceptance_supported": false,
  "next_iteration": "23_topology_mutating_taxonomy_closeout"
}
```

Artifacts:

- `outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json`
- `reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md`
- `scripts/run_n04_iter22b_identity_through_native_route_arbitrated_topology.py`

Iteration 22-B shows that native route arbitration removes the
experiment-supplied route-selection caveat from the identity boundary probe:
the selected topology event is native-arbitrated and the route, lineage,
topology-state reabsorption, producer scheduling, and `step()` chain replay
from artifacts. The result still does not serialize a stable RC
coherence-basin identity or validate attractor-basin invariance through
topology mutation. RC identity collapse, identity acceptance, semantic choice,
agency, locomotion-like behavior, biological behavior, inherited-N03 movement,
and unrestricted movement remain blocked.

## Iteration 23. Topology-Mutating Taxonomy Closeout

Status: Complete.

Question:

```text
Should `topology_mutating_movement_candidate` be frozen as the current N04
ceiling before opening a new semantic choice, RC identity, or locomotion-like
work tranche?
```

Initial checks:

- [x] Consume Iterations 19-E, 20, 21, 21-B, 22, and 22-B.
- [x] Update taxonomy inventory and tag schema with the final topology-mutating
  evidence rows.
- [x] Decide whether the ceiling remains
  `topology_mutating_movement_candidate` or is strengthened/limited by stress,
  route-arbitration, or identity results.
- [x] Produce a closeout/handoff that names the next tranche explicitly.
- [x] Preserve claim boundaries and blocked claims row-by-row.

Run record:

```json
{
  "iteration": "23",
  "status": "passed",
  "closed_tranche": "s7_port_graph_and_topology_mutating_movement",
  "current_claim_ceiling": "topology_mutating_movement_candidate",
  "strongest_supported_result": {
    "achieved_movement_level": "M6",
    "geometry_scope": "topology_mutating",
    "substrate_class": "port_graph",
    "persistence_level": "T5_candidate"
  },
  "native_lgrc_route_arbitration_supported": true,
  "rc_identity_through_topology_supported": false,
  "semantic_choice_claim_allowed": false,
  "agency_claim_allowed": false,
  "identity_acceptance_claim_allowed": false,
  "next_work": "handoff_ready_for_new_tranche"
}
```

Artifacts:

- `outputs/n04_taxonomy_continuation_closeout.json`
- `reports/n04_taxonomy_continuation_closeout.md`
- `outputs/n04_taxonomy_inventory_v1.json`
- `reports/n04_taxonomy_inventory_v1.md`
- `outputs/n04_taxonomy_tag_schema_v1.json`
- `reports/n04_taxonomy_class_separation_v1.md`

Iteration 23 closes the topology-mutating taxonomy tranche. The final N04
ceiling is `topology_mutating_movement_candidate`: stress, reversal,
perturbation, native route arbitration, surface lineage, topology-state
reabsorption, producer scheduling, `step()` processing, and artifact-only
replay are recorded. Native route arbitration is runtime support, not semantic
choice or agency. RC identity through topology, RC identity collapse, identity
acceptance, locomotion-like behavior, biological behavior, inherited-N03
movement, and unrestricted movement remain blocked.

## Claim Flag Requirements

Every report should include:

```text
schema = movement_ladder_report_v1
runtime_family
budget_surface
movement_claim_allowed
loop_driven_movement_claim_allowed
locomotion_like_claim_allowed
adaptive_topology_entry_allowed
native_grc9v3_proposal_flux_loop_claim
native_lgrc9v3_e3_pulse_used
native_grc9v3_proposal_flux_control_used
movement_claim_inherited_from_n03
```

Expected default for early reports:

```text
movement_claim_inherited_from_n03 = false
adaptive_topology_entry_allowed = false
```

For LGRC9V3 E3 pulse lanes:

```text
budget_surface = node_plus_packet
native_lgrc9v3_e3_pulse_used = true
movement_claim_inherited_from_n03 = false
```

## Deferred Items

- [x] LGRC paper extension for causal pulse-substrate surfaces:
  `papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md`.
- [x] Phase 8 native pulse-substrate surface implementation plan:
  `implementation/Phase-8-LGRC9-CausalPulseSubstratePlan.md` and
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateChecklist.md`.
- [x] Lane F native LGRC pulse-substrate surface bridge and N04 closeout.
- [x] Phase 8 native pulse-substrate surface closeout:
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`.
- [x] Phase 8 native causal pulse-substrate surface lineage transport:
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md`
  and
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md`.
- [x] Phase 8 native causal pulse-substrate surface lineage transport closeout:
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md`.
- [x] Native M6 evidence review:
  `outputs/native_m6_evidence_review.json`.
- [x] Native M6 same-fixture validator:
  `outputs/native_m6_same_fixture_validator.json`.
- [x] Adaptive topology entry candidate.
- [x] Topology-mutating movement strict probe, fail-closed at
  `packet_ledger_state_reabsorption_mismatch_after_topology_event`.
- [x] Native topology-state reabsorption support for post-topology packet work:
  `implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`.
- [ ] Full GRC9V3 port-graph S7 movement.
- [ ] Highway/path aftereffect beyond first fixed-substrate result.
- [ ] Movement across changing substrates.
- [ ] Output cleanup after replay artifacts stabilize.

## Current Next Step

N04 has closed the Iteration 19 port-graph/topology-mutating movement tranche
and completed Iteration 20 repeatability/stress, Iteration 21 choice boundary,
Iteration 21-B native route-arbitration rerun, and Iteration 22
identity-through-topology boundary. Iteration 22-B has now rerun the identity
boundary with native route-arbitrated topology. Iteration 23 has closed the
topology-mutating taxonomy tranche.

```text
Iteration 19 produced
outputs/n04_iter19_s7_port_graph_mapping_contract.json and
reports/n04_iter19_s7_port_graph_mapping_contract.md. Iteration 19-A produced
outputs/n04_iter19a_s7_fixed_port_execution_report.json and
reports/n04_iter19a_s7_fixed_port_execution_report.md. The current ceiling is
`s7_fixed_port_composed_gate_candidate`: a fixed-port S7 transfer candidate,
not adaptive topology, topology-mutating movement, native LGRC choice
selection, RC identity collapse, locomotion-like behavior, agency, or
unrestricted movement. Iteration 19-B confirmed native LGRC-3 topology lineage
replay is available, but adaptive topology remains blocked because causal
pulse-substrate surface rows v1 require fixed-topology lineage status.

Phase 8 closed that runtime capability gap with
`native_causal_pulse_substrate_surface_lineage_transport_supported`, and
Iteration 19-C has now rerun the S7 topology-lineage/adaptive gate with native
pulse-surface lineage transport enabled. The current ceiling is
`adaptive_topology_entry_candidate`: transported and superseded surface rows
work, producers read transported digests instead of stale source digests, and
artifact-only lineage replay passes.

Iteration 19-D opened the stricter topology-mutating movement probe and failed
closed at
`packet_ledger_state_reabsorption_mismatch_after_topology_event`. The runtime
could record a committed topology event and transport the native surface row,
but post-topology packet work could not yet be scheduled/processed as movement
evidence because the active state and packet ledger were not
reabsorbed/rebased together.

Phase 8 has now closed that runtime capability gap with
`native_topology_state_reabsorption_supported`, and Iteration 19-E has rerun
the strict probe with topology-state reabsorption enabled. The current ceiling
is `topology_mutating_movement_candidate`: post-topology packet work schedules
and processes from lineage-current, reabsorbed native state. Native LGRC choice
selection, RC identity collapse, agency, locomotion-like behavior, identity
acceptance, inherited-N03 movement, and unrestricted movement remain blocked.

Iteration 20 has now stressed the 19-E topology-mutating candidate. Three
matched native repeats passed, the reversed lane passed, and a
lineage-accounted perturbation lane passed. A single-run multi-topology lane
also passed with exact node-plus-packet accounting, post-topology packet
processing, and artifact-only replay. Phase 8 time-scoped lineage replay
hardening ensures later topology transports do not invalidate earlier
historically valid producer reads.

Iteration 21 attempted to promote the result to
`native_lgrc_choice_selection_candidate` and blocked that promotion at
`native_lgrc_topology_route_selection_not_exposed`. Competing
topology-mutating continuations are executable and artifact-valid when
supplied, but route selection still enters through experiment-supplied
topology-event arguments. Deterministic local preference remains bias, not
native choice.

Iteration 21-B reran that boundary after Phase 8 native route arbitration. The
old route-selection exposure blocker is resolved as runtime route arbitration:
candidate route sets are emitted from committed runtime-visible evidence,
native route arbitration selects exactly one route, and the selected topology
event replays artifact-only through surface lineage, topology-state
reabsorption, producer scheduling, and `step()` processing. This does not
promote semantic choice, agency, RC identity collapse, identity acceptance,
locomotion-like behavior, biological behavior, inherited-N03 movement, or
unrestricted movement.

Iteration 22 attempted to promote the result to
`rc_identity_through_topology_mutation_candidate` and blocked that promotion at
`rc_identity_basin_invariance_not_validated_across_topology_mutation`.
Topology-aware continuity of surface evidence, active state, packet ledger,
and producer scheduling passes, but the artifacts do not serialize a stable RC
coherence-basin identity or validate attractor-basin invariance through
topology mutation.

Iteration 22-B reran the identity boundary with the native route-arbitrated
topology event from Iteration 21-B. Native route arbitration, selected
topology event, surface lineage, topology-state reabsorption, producer
scheduling, and `step()` processing all replay artifact-only. The result still
does not serialize stable RC coherence-basin identity or validate
attractor-basin invariance, so the same RC identity blocker remains.

The next planned topic is a new tranche decision:

1. Choose whether to open semantic choice, RC identity, locomotion-like,
   highway/path-aftereffect, or another post-topology-mutating tranche.
```
