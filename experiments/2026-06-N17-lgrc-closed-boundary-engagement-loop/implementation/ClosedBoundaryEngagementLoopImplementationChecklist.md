# N17 Closed Boundary Engagement Loop Implementation Checklist

## Global Rules

- [ ] Preserve the N17 claim boundary.
- [ ] Do not edit `src/*`.
- [ ] Use `.venv/bin/python` for local script/test runs.
- [ ] Use source-backed artifacts and SHA-256 digests.
- [ ] Do not promote N16 AP6 boundary evidence into agency, selfhood, identity
      acceptance, native support, or closed-loop support by relabel.
- [ ] Do not promote one-way boundary crossing trace into closed loop.
- [ ] Do not prove action by naming an outbound change action.
- [ ] Prove closure only through ordered trace dependence:
      `external -> internal -> external -> later internal`.
- [ ] Treat G3 as the first closed-loop admissibility rung.
- [ ] Confirm G0-G2 rows cannot support AP7.
- [ ] Require monotonic loop phase ordering:
      `t0 external`, `t1 internal`, `t2 external`, `t3 later internal`.
- [ ] Run feedback-removed control before accepting loop closure.
- [ ] Do not promote N15 AP5 endogenous proxy formation into semantic goal
      ownership, intention, identity acceptance, agency, or native support.
- [ ] Do not promote N14 AP4 route selection into intention, semantic choice,
      agency, or goal ownership.
- [ ] Do not promote N13 AP3 support regulation into selfhood, agency, or
      native support.
- [ ] Do not promote N12 NAT4 readiness records into native support.
- [ ] Use direct historic closed-loop evidence when it exists and is
      source-backed, claim-clean, order-clean, replay-clean, and control-clean.
- [ ] Treat N17 as artifact-level closed boundary engagement loop evidence,
      not as semantic action/perception or agency.
- [ ] Keep perturbation-response-recovery first; postpone resource/support and
      shared-medium reciprocal loops until the minimal loop contract is clear.
- [ ] Distinguish MVP AP7 classification from full comparative AP7
      classification.
- [ ] Allow Iterations 7-8 to be explicitly included or deferred before
      closeout.
- [ ] Keep `phase8_opened = false` unless a separate Phase 8 task is explicitly
      opened.
- [ ] Record all paths as portable relative paths.
- [ ] Before closing any turn that edits files, run `git diff --check`.
- [ ] Before closing any turn that edits files, run `git diff -- src`.

## Setup

- [x] Create N17 experiment root.
- [x] Create `README.md`.
- [x] Create `configs/`, `hypotheses/`, `implementation/`, `outputs/`,
      `reports/`, and `scripts` directories.
- [x] Create N17-specific hypotheses.
- [x] Create implementation plan.
- [x] Create implementation checklist.

## Hypotheses

- [ ] Hypothesis A: source-current loop trace exists.
- [ ] Hypothesis B: loop is replay/control clean, not post-hoc stitched.
- [ ] Hypothesis C: closed loop classification preserves claim boundary.

## Iteration 1. Source Inventory And Loop Contract

- [x] Pin N16 AP6 boundary closeout artifacts.
- [x] Pin N16 claim-boundary and requirements artifacts.
- [x] Pin N16 B3/C4 breach-reclosure and B4/C5 shared-medium source artifacts.
- [x] Pin N15 AP5 endogenous proxy formation closeout artifacts.
- [x] Pin N14 AP4 consequence-sensitive route selection closeout artifacts.
- [x] Pin N13 AP3 support-seeking regulation closeout artifacts.
- [x] Pin N08/N09 memory and bounded-regulation context if used.
- [x] Pin N12 NAT4 readiness records if used.
- [x] Record whether direct historic AP7 closed-loop evidence exists.
- [x] Classify source rows by loop phase contribution.
- [x] Record old-best construction inputs.
- [x] Record that N16 boundary-crossing trace is not closed loop by itself.
- [x] Record claim-boundary blockers for every source row.
- [x] Confirm no final AP7 claim is made.

Expected artifacts:

- [x] `outputs/n17_loop_source_inventory.json`
- [x] `reports/n17_loop_source_inventory.md`
- [x] `scripts/build_n17_loop_source_inventory.py`

Result:

```text
status = passed
acceptance_state = accepted_loop_source_inventory_only_no_ap7
output_digest = 5d5c8ec793278cb0e2d88e52fdb17497ab7c6fb96dc0e49aa113e3dd32168fbd
artifact_sha256 = b814f3bd21e3d4203ac9f2e1c647ecb3111b9c37bae1cc40e31ecd3cac1c4db1
direct_historic_ap7_evidence_exists = false
final_ap7_supported = false
closed_loop_demonstrated = false
ready_for_iteration_2_schema = true
review_gap_closure_checks = source_json_parseable, output_digest_recorded, expected_final_ap_match, valid_phase_values, source_consumption_rules, construction_role_mvp_alignment, derived_direct_ap7_admissibility, report_matches_json_summary
```

Iteration 1 source-phase map:

```text
external_to_internal = yes_fragment_only
internal_response = yes_fragment_only
response_to_external_change = partial
external_feedback_to_internal = partial_context_but_missing_ordered_response_caused_feedback
```

Iteration 1 interpretation:

```text
N16 closeout is present and AP6 is frozen. N16 contributes boundary substrate
only; it does not supply direct AP7 evidence. All historic rows remain below
G3 or act as blockers. Iteration 2 must freeze the schema and AP7 gate around
the missing ordered closure trace:

external -> internal -> external -> later internal
```

## Iteration 2. Loop Schema And AP7 Gate

- [x] Freeze loop row schema.
- [x] Freeze loop ladder values G0-G7.
- [x] Freeze the rule that G3 is the first AP7-admissible rung.
- [x] Freeze the rule that G0-G2 cannot support AP7.
- [x] Freeze monotonic phase ordering fields.
- [x] Freeze trace fields:
      `external_to_internal_trace`, `internal_response_trace`,
      `response_to_external_change_trace`,
      `external_feedback_to_internal_trace`, and `loop_closure_evidence`.
- [x] Freeze one-way crossing active-null rules.
- [x] Freeze feedback-removed control.
- [x] Freeze replay digest scope and algorithm.
- [x] Freeze budget validity fields.
- [x] Freeze dependency trace fields.
- [x] Freeze AP7 gates.
- [x] Freeze negative controls.
- [x] Materialize `configs/n17_source_registry.json`.
- [x] Materialize `configs/n17_loop_policy_v1.json`.
- [x] Materialize `configs/n17_budget_limits_v1.json`.
- [x] Materialize `configs/n17_control_variants_v1.json`.
- [x] Materialize `configs/n17_replay_policy_v1.json`.
- [x] Confirm no final AP7 claim is made.

Expected artifacts:

- [x] `outputs/n17_loop_schema_v1.json`
- [x] `reports/n17_loop_schema_v1.md`
- [x] `scripts/build_n17_loop_schema_v1.py`
- [x] `scripts/validate_n17_loop_row.py`

Result:

```text
status = passed
acceptance_state = accepted_loop_schema_v1_no_ap7_evidence
output_digest = 911f2910da5cb5899f9bc4b87e52e71177a013725b48b0356a6087a2e237ad72
artifact_sha256 = 55b0f8c32c72018f8c8392c950ecc37a6184373af953984ba46e905a347e9f67
rows = 0
loop_schema_frozen = true
ap7_gates_frozen = true
one_way_null_rules_frozen = true
replay_and_controls_frozen = true
closed_loop_demonstrated = false
final_ap7_supported = false
ready_for_iteration_3_one_way_crossing_active_null = true
review_gap_closure_checks = one_way_null_family_classified_as_null_not_evidence_family, extension_controls_frozen, replay_controls_status_backed, config_schema_policy_consistency, row_type_validator_self_test
```

Highest-value double-check:

```text
A G2 row with crossing, internal response, and outbound external change cannot
pass as AP7 without later internal dependence on the changed external state.
Validator self-test status = passed.
```

## Iteration 3. One-Way Crossing Active Null

- [x] Generate or replay a one-way crossing trace.
- [x] Show external-to-internal pressure/crossing.
- [x] Show internal support update if present.
- [x] Block closed-loop classification when no changed external state feeds
      back into later internal support.
- [x] Run one-way crossing relabel control.
- [x] Confirm `closed_loop_claim_allowed = false`.

Expected artifacts:

- [x] `outputs/n17_one_way_crossing_active_null.json`
- [x] `reports/n17_one_way_crossing_active_null.md`
- [x] `scripts/build_n17_one_way_crossing_active_null.py`

Result:

```text
status = passed
acceptance_state = accepted_one_way_crossing_active_null_no_ap7
output_digest = 3f70a70db68edf537d20f4b1478e0b53a7012510c7357539b3af8385fef30635
artifact_sha256 = b9d60944babac53f31573ba662b8799ee1f4b8775c6ad5ac25c9020c3945c09d
row_decision = supported
row_type = active_null
active_null_decision = supported_as_active_null_rejection
loop_ladder_rung = G2
closed_loop_claim_allowed = false
final_ap7_supported = false
failure_mode = one_way_crossing_is_not_closed_loop
row_replay_digest = 4c985072a0a5acf670677d4586689d380e4ff897a87a439a73484424245d08fa
review_gap_closure_checks = row_decision_schema_enum_aligned, replay_digest_binds_schema_and_loop_policy
```

Iteration 3 interpretation:

```text
The row demonstrates boundary crossing and internal update fragments, but it
does not demonstrate closed boundary engagement because no response-caused
external change feeds back into later internal support.
```

## Iteration 4. Perturbation-Response-Recovery Loop

- [x] Build the minimal perturbation-response-recovery loop candidate.
- [x] Record external perturbation crossing.
- [x] Record internal support shift.
- [x] Record bounded response or reclosure.
- [x] Record response-caused external perturbation-field change candidate.
- [x] Record later internal support dependence candidate on changed external
      state.
- [x] Record monotonic `t0 -> t1 -> t2 -> t3` phase ordering.
- [x] Distinguish closed loop from one-step recovery.
- [x] Preserve claim boundary.

Expected artifacts:

- [x] `outputs/n17_perturbation_response_recovery_loop.json`
- [x] `reports/n17_perturbation_response_recovery_loop.md`
- [x] `scripts/build_n17_perturbation_response_recovery_loop.py`

Result:

```text
status = passed
acceptance_state = accepted_perturbation_response_recovery_g3_candidate_pending_controls_no_ap7
output_digest = 66bd43b80a31c08dd5b8106430cbf4623f0cebc9bbf505c986e2a617846b993f
artifact_sha256 = d6b2fdd68e03b2132c2fa300e9560115cc7419609f35cf2554e6985fcaa981ec
row_decision = supported
row_type = loop_candidate
loop_family = perturbation_response_recovery_loop
loop_ladder_rung = G3_candidate
closed_loop_candidate = true
closed_loop_claim_allowed = false
final_ap7_supported = false
row_replay_digest = 4ee4687d9a45d0fcc627faa26a85bb2ced6608d64dd07c85e5b00696804cc756
review_gap_closure_checks = causality_and_counterfactual_gates_false_until_i5, feedback_removed_control_result_pending_not_false, hidden_state_dependent_feedback_gate_false_until_i5
```

Iteration 4 interpretation:

```text
I4 crosses the line that I3 deliberately did not cross at candidate level: it
records response-caused external perturbation-field change candidate evidence
and later internal support dependence candidate evidence. The AP7 gates for
validated response causation, counterfactual external-change blocking, hidden
state exclusion, feedback removal, replay, and controls remain false until I5.
This is a G3 candidate only.
```

Iteration 4 geometric and flux candidate interpretation:

```text
The internal-support dependence candidate is measured as a contrast in minimum
observed support on the derived internal side:

internal side = b3_c4_0, b3_c4_1, b3_c4_2
external side = b3_c4_3, b3_c4_4

B2_C4 baseline minimum_internal_support = 0.830
B3_C4 bounded-reclosure surface minimum_internal_support = 0.851
support_floor = 0.850
support_delta_vs_b2_c4 = +0.021

t0:
  breach pressure crosses the boundary:
  b3_c4_2 internal -> b3_c4_3 external
  weight = 0.13
  breach_pressure = 0.38

t1:
  internal support shifts under that breach.
  The B2_C4 breach baseline is below floor:
  0.830 < 0.850

t2:
  bounded reclosure response candidate appears:
  b3_c4_3 external -> b3_c4_1 internal
  weight = 0.12
  reclosure_score = 0.76
  reclosure_latency_steps = 1

t3:
  later internal support is evaluated on the B3_C4 bounded-reclosure surface,
  which is the candidate response-modified external perturbation surface:
  B3_C4 support = 0.851
  floor preserved: 0.851 >= 0.850

Flux comparison:
  leakage_ratio      0.148 -> 0.118   delta = -0.030
  outbound_flux      0.160 -> 0.130
  retained_flux      1.050 -> 1.220
  boundary_stability 0.550 -> 0.740
  coherence_margin   0.472 -> 0.524
  internal_support   0.830 -> 0.851

So the narrow dependency candidate recorded by I4 is:

without the bounded-reclosure-associated perturbation surface:
  support remains below floor under the B2_C4 breach baseline

with the B3_C4 bounded-reclosure surface:
  leakage is reduced, retention improves, and later internal support is above
  floor

This is still a constructed G3 candidate. I4 does not assert the AP7
causality/counterfactual/dependence gates as validated. I5 must test whether
the B2_C4 vs B3_C4 contrast is a validated causal dependence, rather than a
candidate dependence produced by hidden carryover, order effects,
post-hoc stitching, independent external change, or feedback-removal failure.
```

Iteration 4 review non-gaps:

```text
Extra row fields such as candidate_rung_label, loop_policy_digest,
schema_version, contrast_with_i3_one_way_null, minimal_loop_scope,
pending_controls, and row_replay_digest are generated traceability fields.
The I2 validator treats row_schema_fields as required fields, not an exclusive
field whitelist.

The broader plan's initial common-row fields are superseded for generated rows
by the I2 schema artifact and plan_to_schema_field_mapping. Missing plan-era
field names such as loop_id, phase_order_trace, and case_id are therefore not
I4 artifact gaps when the I2 schema fields and mappings are present.
```

## Iteration 5. Replay And Order Controls

- [ ] Run artifact-only replay.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay.
- [ ] Run order-inversion replay.
- [ ] Run post-hoc loop stitching control.
- [ ] Run hidden external-state memory control.
- [ ] Run hidden internal-state carryover control.
- [ ] Run external change not caused by internal response control.
- [ ] Run feedback-removed control.
- [ ] Run outbound response relabel control.
- [ ] Run resource depletion as goal-pursuit relabel control if resource rows
      are present.
- [ ] Run semantic agency, intention, and semantic action/perception relabel
      controls.
- [ ] Confirm one-way crossing cannot pass as closed loop.

Expected artifacts:

- [ ] `outputs/n17_loop_replay_and_control_matrix.json`
- [ ] `reports/n17_loop_replay_and_control_matrix.md`
- [ ] `scripts/build_n17_loop_replay_and_control_matrix.py`

## Iteration 6. MVP Claim Boundary Record

- [ ] Resolve MVP perturbation-loop AP7 classification gates.
- [ ] Record that this is not full comparative AP7 classification unless
      Iterations 7-8 are explicitly included later.
- [ ] Classify Hypothesis A.
- [ ] Classify Hypothesis B.
- [ ] Classify Hypothesis C.
- [ ] Force unsafe claim flags false.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `fully_native_integration_opened = false`.
- [ ] Confirm agency, intention, semantic perception/action, selfhood, identity
      acceptance, organism/life, and unrestricted-agency claims remain blocked.

Expected artifacts:

- [ ] `outputs/n17_claim_boundary_record.json`
- [ ] `reports/n17_claim_boundary_record.md`
- [ ] `scripts/build_n17_claim_boundary_record.py`

## Iteration 7. Resource/Support Modulation Loop

- [ ] Test resource/support modulation loop only after MVP loop contract is
      stable.
- [ ] Record external resource/support condition change.
- [ ] Record internal support-relevant update.
- [ ] Record response-caused access/path/pressure change.
- [ ] Record later internal support conditioned by modified resource state.
- [ ] Block resource depletion as semantic goal pursuit.

Expected artifacts:

- [ ] `outputs/n17_resource_support_modulation_loop.json`
- [ ] `reports/n17_resource_support_modulation_loop.md`
- [ ] `scripts/build_n17_resource_support_modulation_loop.py`

## Iteration 8. Shared-Medium Reciprocal Loop

- [ ] Test shared-medium reciprocal loop only after MVP and resource/support
      contracts are stable or explicitly deferred.
- [ ] Record basin A and basin B shared-medium state.
- [ ] Record A response changing shared medium.
- [ ] Record changed shared medium affecting B or later A.
- [ ] Preserve basin separability and boundary exclusivity.
- [ ] Block merge/leakage as reciprocal-loop success.

Expected artifacts:

- [ ] `outputs/n17_shared_medium_reciprocal_loop.json`
- [ ] `reports/n17_shared_medium_reciprocal_loop.md`
- [ ] `scripts/build_n17_shared_medium_reciprocal_loop.py`

## Iteration 9. Comparative Requirements And AP7 Classification

- [ ] Synthesize loop requirements.
- [ ] Compare one-way null, perturbation loop, resource loop, and shared-medium
      loop if available.
- [ ] Record deferred iterations if extensions are not run.
- [ ] Record `extension_mode = extensions_deferred | extensions_included`.
- [ ] Resolve AP7 classification only within artifact-level claim ceiling.
- [ ] Keep final closeout pending until Iteration 10.

Expected artifacts:

- [ ] `outputs/n17_closed_loop_requirements_matrix.json`
- [ ] `reports/n17_closed_loop_requirements_matrix.md`
- [ ] `scripts/build_n17_closed_loop_requirements_matrix.py`

## Iteration 10. Closeout And N18 Handoff

- [ ] Freeze final supported AP level if warranted.
- [ ] Record final claim ceiling.
- [ ] Record final controls.
- [ ] Record final blockers.
- [ ] Record final N18 handoff.
- [ ] Record whether targeted Phase 8 is optional, required, or deferred.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `fully_native_integration_opened = false`.

Expected artifacts:

- [ ] `outputs/n17_closeout_and_handoff.json`
- [ ] `reports/n17_closeout_and_handoff.md`
- [ ] `scripts/build_n17_closeout_and_handoff.py`

## Setup Verification

- [x] `git diff --check`
- [x] `git diff -- src`
