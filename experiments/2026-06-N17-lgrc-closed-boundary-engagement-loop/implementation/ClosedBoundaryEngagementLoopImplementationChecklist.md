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
- [ ] Distinguish Iteration 6-B alternative G5 configuration from Iteration
      6-A threshold refinement or rescue.
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

- [x] Run artifact-only replay.
- [x] Run snapshot/load replay.
- [x] Run duplicate replay.
- [x] Run order-inversion replay.
- [x] Run feedback-order inversion control.
- [x] Run post-hoc loop stitching control.
- [x] Run hidden external-state memory control.
- [x] Run hidden internal-state carryover control.
- [x] Run external change not caused by internal response control.
- [x] Run feedback-removed control.
- [x] Run outbound response relabel control.
- [x] Run resource depletion as goal-pursuit relabel control if resource rows
      are present.
- [x] Run semantic agency, intention, and semantic action/perception relabel
      controls.
- [x] Confirm one-way crossing cannot pass as closed loop.

Expected artifacts:

- [x] `outputs/n17_loop_replay_and_control_matrix.json`
- [x] `reports/n17_loop_replay_and_control_matrix.md`
- [x] `scripts/build_n17_loop_replay_and_control_matrix.py`

Result:

```text
status = passed
acceptance_state = accepted_loop_replay_and_control_matrix_g4_candidate_no_final_ap7
output_digest = 919af53a36661c52439a7be65bbb0ea18770cdec28c118043e12c399bce5bb8a
artifact_sha256 = b5d988c38e646a9c622e3452d4896384d559809459979357530fcfae8bb50ee4
source_loop_digest = 66bd43b80a31c08dd5b8106430cbf4623f0cebc9bbf505c986e2a617846b993f
source_row_replay_digest = 4ee4687d9a45d0fcc627faa26a85bb2ced6608d64dd07c85e5b00696804cc756
row_replay_digest = 3d324e9ed012957979466813dd620fe880b52f20f75ab6ab693a2192c7468a10
candidate_trace_legs_unchanged = true
loop_ladder_rung = G4_replay_control_clean_candidate
closed_loop_claim_allowed = false
final_ap7_supported = false
missing_gate = claim_boundary_clean
review_gap_closure_checks = pre_i5_pending_controls_resolved, duplicate_replay_schema_scope_explained, stable_replay_status_semantics_documented, control_details_completed, feedback_order_inversion_control_checked
```

Iteration 5 interpretation:

```text
I5 does not add new loop evidence. It reuses the exact I4 G3 candidate and
tries to break it. Artifact-only replay, snapshot/load replay, duplicate
replay, and order-inversion replay are stable. For artifact-only,
snapshot/load, and duplicate replay, stable means the serialized candidate
digest or row replay digest is preserved. For order-inversion replay, stable
means the false-order variant is reproducibly blocked, not that inverted order
supports closure. Invalid variants are blocked: post-hoc stitching, hidden
external memory, hidden internal carryover, external-change-not-caused-by-
response, feedback order inversion, feedback removal, outbound-response relabel,
one-way crossing relabel, and unsafe semantic/native/selfhood/life relabels.

Replay is artifact-level digest and variant-control verification, not a full
pipeline rerun. Duplicate replay is recorded as a run-level digest check;
`schema_backed_like_row_controls = false` because it compares deterministic row
replay digests rather than materializing a separate schema-backed row control
case.

The highest-value result is that the candidate does not pass when
response-caused external change is removed or when changed external state no
longer feeds back into later internal support. That upgrades the I4 candidate
to a G4 replay/control-clean candidate, not final AP7.

Resource/support and shared-medium extension controls are marked
not_applicable because I4 did not open those extension rows.

The stale I4 `pending_controls` row field is not carried forward. I5 records
completed controls and not-applicable controls explicitly.

I6 must still perform the claim-boundary record before AP7 classification can
be allowed.
```

Iteration 5 geometric/control interpretation:

```text
I5 does not reinterpret the B3_C4 geometry from I4. It verifies that the same
I4 trace geometry is preserved under artifact-level replay and fails closed
under invalid geometric/control variants.

Preserved canonical geometry:
  source_loop_digest = 66bd43b80a31c08dd5b8106430cbf4623f0cebc9bbf505c986e2a617846b993f
  candidate_trace_legs_unchanged = true
  source_trace_digest = controlled_trace_digest

No new boundary or flux surface is introduced. The G4 upgrade is therefore not
a new geometric event. It is a control result over the I4 geometry.

Invalid geometric/control variants:
  order inversion:
    false-order geometry is reproducibly blocked

  feedback removal:
    removing the t3 external-feedback-to-internal-support leg blocks the loop
    claim

  external change not caused by response:
    independent external perturbation change cannot support loop causality

  one-way crossing relabel:
    I3 crossing geometry remains G2 and cannot pass as closed loop

  post-hoc stitching:
    compatible boundary fragments cannot be assembled after the fact into
    closure

So I5's geometric result is:
  the I4 geometry is replay/control stable under canonical ordering, and the
  invalid geometries that would fake closure are rejected.
```

## Iteration 6. MVP Claim Boundary Record

- [x] Resolve MVP perturbation-loop AP7 classification gates.
- [x] Record that this is not full comparative AP7 classification unless
      Iterations 7-8 are explicitly included later.
- [x] Classify Hypothesis A.
- [x] Classify Hypothesis B.
- [x] Classify Hypothesis C.
- [x] Force unsafe claim flags false.
- [x] Confirm `native_support_opened = false`.
- [x] Confirm `phase8_opened = false`.
- [x] Confirm `fully_native_integration_opened = false`.
- [x] Confirm agency, intention, semantic perception/action, selfhood, identity
      acceptance, organism/life, and unrestricted-agency claims remain blocked.

Expected artifacts:

- [x] `outputs/n17_claim_boundary_record.json`
- [x] `reports/n17_claim_boundary_record.md`
- [x] `scripts/build_n17_claim_boundary_record.py`

Result:

```text
status = passed
acceptance_state = accepted_mvp_ap7_claim_boundary_clean_pending_extensions_and_closeout
output_digest = cfefe6fba20ea64e1db132f8f3f5d024fdab5397f11c036d7cb5a96508068611
artifact_sha256 = a362b9b9f84fbbeb753050d7e00d27ebd1a41d8be1cc9d6f5ac017a20c52a8b6
classified_ap_level = AP7_MVP
current_evidence_rung = G4_replay_control_clean_candidate
claim_classification = AP7_MVP_claim_clean_candidate
ap7_classification_supported = true
artifact_level_ap7_candidate_supported = true
mvp_ap7_classification_supported = true
g5_challenge_stability_supported = false
g5_challenge_stability_pending_iteration_6a = true
full_comparative_ap7_classification_supported = false
closed_loop_claim_allowed = true
final_ap7_supported = false
extension_mode = extensions_deferred
boundary_row_count = 13
row_replay_digest = e4ce656ed1ea38149f2b1440a7055fea9ecdda5610f51cec1419bcbbb00a437a
```

Interpretation:

```text
I6 resolves the MVP perturbation-response-recovery claim boundary. The I5 G4
replay/control-clean candidate advances to an artifact-level AP7 MVP candidate,
because all AP7 gates are true after claim-boundary classification and the
allowed claim ceiling is only:

artifact_level_closed_boundary_engagement_loop_candidate_mvp_only

This does not advance the evidence rung beyond G4, does not support G5
challenge stability, and does not freeze final AP7. G5 is reserved for
Iteration 6-A and the alternative Iteration 6-B probe. It also does not
classify resource/support modulation or shared-medium reciprocal loops, because
Iterations 7-8 remain deferred extensions in this record.
```

Claim boundary record:

```text
Hypothesis A = supported at artifact-level ordered-loop-trace scope
Hypothesis B = supported at replay/control-clean MVP loop scope
Hypothesis C = supported at artifact-level AP7 MVP scope with unsafe promotions
               blocked

agency = blocked
intention = blocked
semantic action/perception = blocked
semantic goal ownership = blocked
selfhood / identity acceptance = blocked
native support = blocked
organism/life = blocked
fully native integration = blocked
unrestricted agency = blocked
resource/support extension AP7 = blocked
shared-medium extension AP7 = blocked
final AP7 closeout = blocked
```

Handoff:

```text
Iteration 6-A should test G5 challenge stability for the MVP loop.
Iteration 6-B may test an independent alternative G5 configuration if a
stronger bounded MVP G5 claim is useful before extensions.
Iteration 7 may open the resource/support modulation extension.
Iteration 8 may open the shared-medium reciprocal extension.
Iteration 9 must synthesize comparative requirements/classification with
extension_mode recorded.
Iteration 10 must freeze final closeout if warranted.
```

## Iteration 6-A. MVP Challenge-Stability Probe

- [x] Keep the loop family fixed to perturbation-response-recovery.
- [x] Vary challenge pressure without retuning the loop to win.
- [x] Test at least perturbation magnitude and perturbation duration/window.
- [x] Test at least one external noise, flux, leakage, delay, or feedback
      attenuation pressure.
- [x] Preserve the four ordered trace legs in every supported row.
- [x] Preserve response-caused external change in every supported row.
- [x] Preserve later internal dependence on changed external state in every
      supported row.
- [x] Record row decisions independently from AP7 closeout.
- [x] Confirm G0-G2 relabels still fail closed under challenge variation.
- [x] Confirm unsafe claim flags remain false.
- [x] Keep final AP7 blocked.
- [x] Record whether G5 challenge stability is supported, partial, or blocked.

Expected artifacts:

- [x] `outputs/n17_mvp_challenge_stability_probe.json`
- [x] `reports/n17_mvp_challenge_stability_probe.md`
- [x] `scripts/build_n17_mvp_challenge_stability_probe.py`

Directive:

```text
Iteration 6-A is the targeted G5 bridge. It must not introduce resource/support
modulation or shared-medium reciprocal loops. It should ask whether the same
MVP perturbation-response-recovery loop that passed I4-I6 remains closed-loop
under controlled challenge variation.

A supported G5 row must keep:
  external_to_internal_trace
  internal_response_trace
  response_to_external_change_trace
  external_feedback_to_internal_trace

and must keep:
  response-caused external change
  later internal dependence on changed external state
  replay/control cleanliness or inherited replay/control compatibility
  unsafe claim flags false

If the loop survives only the canonical I4/I5/I6 case, record G5 as partial or
blocked rather than weakening the G5 definition.
```

Result:

```text
status = passed
acceptance_state = accepted_bounded_g5_mvp_challenge_stability_no_final_ap7
output_digest = 4c795ca09ec6d7b557f5d1f8d1f7d0624f4eb7cfea99a43f383f40d68068ebc4
artifact_sha256 = cc34f5bbb06521271341f334c1ed9db4276d0af020d396f85b1334eb9553d726
current_evidence_rung = G5_bounded_challenge_stable_candidate
g5_challenge_stability_supported = true
g5_support_scope = bounded_source_backed_breach_flux_envelope
full_comparative_ap7_classification_supported = false
final_ap7_supported = false
```

Row decisions:

```text
supported:
  canonical_c4_breach_reclosure
  c2_directional_flux_repair_anchor
  bounded_breach_flux_composite_envelope

partial / claim not allowed:
  feedback_attenuation_control
  feedback_delay_control

rejected / claim not allowed:
  overpressure_control
```

Interpretation:

```text
6-A supports G5 only in a bounded MVP envelope. The source-backed envelope is
formed from I6 AP7_MVP claim-clean closure, N16 B3_C4 breach/reclosure, and N16
B3_C2 directional-flux repair. The composite row remains exactly at the frozen
support, coherence, and leakage floors, so the result is strong but narrow.

The attenuation, delay, and overpressure controls fail closed. That means 6-A
does not support a general challenge-stable loop, delayed feedback tolerance,
attenuated-response tolerance, resource/support modulation, shared-medium
reciprocal closure, full comparative AP7, or final AP7 closeout.
```

## Iteration 6-B. Alternative G5 Challenge Probe

- [x] Treat 6-B as an alternative configuration, not a 6-A retune.
- [x] Keep the loop family fixed to perturbation-response-recovery.
- [x] Use old-best source-backed values from N13/N09/N15.
- [x] Freeze the target-band pass/fail rule before row evaluation.
- [x] Preserve the four ordered trace legs in every supported row.
- [x] Preserve response-caused external change in every supported row.
- [x] Preserve later internal dependence on changed external state in every
      supported row.
- [x] Test mild feedback attenuation under the alternative target-band config.
- [x] Test source-window feedback delay under the alternative target-band
      config.
- [x] Test compound mild attenuation plus source-window delay.
- [x] Fail closed when projected support crosses below the target band.
- [x] Fail closed when the response budget exceeds the N13 bounded response.
- [x] Confirm unsafe claim flags remain false.
- [x] Keep final AP7 blocked.

Expected artifacts:

- [x] `outputs/n17_alternative_g5_challenge_probe.json`
- [x] `reports/n17_alternative_g5_challenge_probe.md`
- [x] `scripts/build_n17_alternative_g5_challenge_probe.py`

Directive:

```text
Iteration 6-B is not envelope refinement for 6-A. It asks whether a separate
target-band-gated support-buffer configuration can produce a stronger bounded
G5 claim for the same MVP perturbation-response-recovery loop. It must use
source values that were already present before 6-B evaluation and must fail
closed outside the generated target band or outside the N13 response budget.
```

Result:

```text
status = passed
acceptance_state = accepted_alternative_target_band_g5_mvp_challenge_stability_no_final_ap7
output_digest = cecfc28625e871c4d7d12ba0a1904a9ef7866c2230206c1b033b316b9b2564ab
artifact_sha256 = ff1306a22857c9509ea526e715a0b99e640d3e2631519a632cd9376e9584d33b
current_evidence_rung = G5_alternative_target_band_challenge_stable_candidate
alternative_g5_configuration_supported = true
g5_support_scope = target_band_gated_mvp_perturbation_loop
full_comparative_ap7_classification_supported = false
final_ap7_supported = false
```

Source values:

```text
target_center = 0.887594607287
target_band = [0.817594607287, 0.957594607287]
support_floor = 0.85
n13_bounded_response_amount = 0.120134817816
n09_recovery_in_band = true
n15_bounded_drift_replay_passed = true
```

Row decisions:

```text
supported:
  target_band_anchor_replay
  mild_feedback_attenuation_target_band
  source_window_feedback_delay_target_band
  compound_mild_attenuation_delay_target_band

rejected / claim not allowed:
  target_band_lower_bound_crossing_control
  response_budget_exceeds_n13_control
```

Interpretation:

```text
6-B is stronger than 6-A only within its alternative target-band configuration.
Mild attenuation, a source-backed one-window delay, and their compound case
remain inside the generated target band and above the support floor. The result
still fails closed below the target band and beyond the N13 response budget.

This supports an alternative bounded G5 MVP configuration. It does not replace
6-A, does not generalize to arbitrary challenge stability, does not open
resource/support or shared-medium extensions, and does not support final AP7.
Iteration 9 must compare 6-A and 6-B before any final classification.
```

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
