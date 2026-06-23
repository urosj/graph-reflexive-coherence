# N22 Susceptibility Update And Durable Geometry Implementation Checklist

## Initialization

- [x] Create `experiment-N22` branch.
- [x] Create N22 experiment directory.
- [x] Add top-level N22 `README.md`.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add `configs/`, `hypotheses/`, `outputs/`, `reports/`, and `scripts/`
      scaffolds.
- [x] Add hypothesis records.
- [x] Keep N22 scoped to susceptibility update / durable geometry
      modification.
- [x] Confirm N22 starts from N20/N21 handoff evidence, not N22 primitive
      evidence.

## Global Rules

- [x] Use source IDs, titles, and relative paths only.
- [x] Confirm generated records contain no local absolute paths.
- [x] Consume N20 I5 `susceptibility_update` row without redefinition.
- [x] Consume N21 closeout as prerequisite context only.
- [x] Confirm N21 WR/ND evidence is not used as susceptibility evidence.
- [x] Preserve N21 as closed at bounded local `ND5`; do not reopen N21.
- [x] Record N21 `ND6` bridge status only as a candidate bridge field, not as
      direct N21 closeout.
- [x] Treat N19 as AP-gap boundary only, not susceptibility evidence.
- [x] Record `n19_native_readiness_boundary_consumption =
      ap_gap_boundary_only`.
- [x] Mirror inherited N20 source status as
      `n20_source_downstream_consumption_status`.
- [x] Declare row-specific thresholds before use.
- [x] Record `source_current_inputs` in every candidate row.
- [x] Record `row_specific_thresholds_declared_before_use` in every candidate
      row.
- [x] Require `artifact_manifest` in every candidate row.
- [x] Require `all_artifact_sha256_match_file_contents = true` for positive
      support.
- [x] Require actual LGRC/source-current run artifacts for positive
      susceptibility evidence.
- [x] Reject report-only or synthetic-row success as insufficient evidence.
- [x] Separate source-current geometry from route labels and producer
      reinforcement schedules.
- [x] Treat producer-mediated fields as producer residue unless source-backed
      naturalization evidence is produced.
- [x] Treat naturalization-debt fields as debt unless source-backed evidence is
      produced.
- [x] Reject blocked relabel fields when used as evidence.
- [x] Separate historical interaction provenance from active producer
      reinforcement.
- [x] Require `historical_interaction_provenance_present` when prior
      interaction is claimed.
- [x] Require `active_reinforcement_schedule_disabled = true` for source-current
      durable-delta support.
- [x] Require `active_reinforcement_queue_empty = true` for source-current
      durable-delta support.
- [x] Require `reinforcement_budget_in_flight = 0.0` for source-current
      durable-delta support.
- [x] Require `reinforcement_schedule_not_used_as_evidence = true`.
- [x] Freeze active reinforcement rung effects: SU1/SU2 descriptive, SU3
      replay-limited, SU4/SU5/SU6 and N22-C4/N22-C5/N22-C6 blocked.
- [x] Carry AP4 dependency row-locally when route-conditioned selection
      participates.
- [x] Carry conditional AP5 dependency when proxy or target formation
      participates.
- [x] Use closed AP4/AP5 dependency status enums.
- [x] Record `ap4_condition_reason` and `ap5_condition_reason` per row.
- [x] Freeze allowed delta fields separately from same-basin invariant fields.
- [x] Block rows when out-of-scope drift exceeds the declared update scope.
- [x] Require `delta_not_label_reassignment = true`.
- [x] Include peer/same-budget comparison for route- or region-conditioned
      susceptibility rows.
- [x] Allow peer comparison `not_applicable` only for
      `non_route_conditioned_SU2_only`.
- [x] Block SU5/SU6 when route- or region-conditioned rows lack peer
      same-budget comparison.
- [x] Freeze field-specific allowed gate statuses for support, coherence,
      boundary, and flux/leakage.
- [x] Record durability metrics and delta digests before closeout.
- [x] Declare `delta_persistence_ratio` floor before use.
- [x] Require replay-window survival for durable-delta support.
- [x] Require later re-entry survival for durable-delta support.
- [x] Require global-drift rejection for route- or region-conditioned
      susceptibility support.
- [x] Fail closed on route-label-only success.
- [x] Fail closed on reinforcement-schedule hidden support.
- [x] Fail closed on one-window transient success.
- [x] Fail closed on post-hoc delta construction.
- [x] Treat `artifact_only_replay` only as an alias for canonical
      `artifact_replay`.
- [x] Require I3 active nulls for missing AP4, missing AP5, and AP-gap
      prose-only handling.
- [x] Force unsafe claim flags false in every row.
- [x] Do not modify `src/*`.
- [x] Do not write ant-ecology implementation specs in N22.
- [x] Keep semantic learning, choice, agency, native support, sentience, and
      Phase 8 claims blocked.

## Iteration 1. Source Handoff Inventory

- [x] Build N22 source handoff inventory.
- [x] Read N20 closeout and N21 handoff.
- [x] Read N20 I5 same-basin continuation contract.
- [x] Read N21 closeout and N22 handoff.
- [x] Record susceptibility-update source row.
- [x] Record N21 WR6/ND5/N21-C6 context.
- [x] Record N21 `ND6` blocker and N22 bridge question.
- [x] Record required source-current fields.
- [x] Record producer-mediated fields and naturalization-debt fields.
- [x] Record AP4/AP5 dependency rules.
- [x] Record required controls.
- [x] Confirm no susceptibility evidence is opened.
- [x] Confirm no semantic learning, choice, agency, native support, sentience,
      Phase 8, or ant-ecology claim is opened.

Expected artifacts:

```text
outputs/n22_source_handoff_inventory.json
reports/n22_source_handoff_inventory.md
scripts/build_n22_source_handoff_inventory.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_source_handoff_inventory_no_susceptibility_evidence
output_digest = 8c470a09056834437fe19bbbe170c5eb8e0a95284212fd73bf7e1427e76625f5
check_count = 19
failed_checks = []
source_contract_row = n20_i5_row_03_susceptibility_update
source_contract_status = complete
n21_closeout_ladder_rung = N21-C6
n21_context = WR6, ND5, ready_for_n22
n21_nd6_bridge_status = not_supported
n21_reopened = false
su_ladder_rung_assigned = false
susceptibility_evidence_opened = false
susceptibility_update_supported = false
durable_geometry_modification_supported = false
positive_run_artifacts_consumed = false
ready_for_iteration_2_schema_freeze = true
```

Artifact hashes:

```text
1ea13c1d9fcdaa75ba284aa1041dd08b18f8e8c1a6d73f24c45512b639e9773f  outputs/n22_source_handoff_inventory.json
de70051ee105253b3ebbb8686de378a0f62fefe810f5bf223aa0fa430d53b8f5  reports/n22_source_handoff_inventory.md
d16f03b40878ef092af7e6faae2e3e099463a3036ab4afa30989c1b79812e31a  scripts/build_n22_source_handoff_inventory.py
```

Interpretation:

```text
Iteration 1 is source/handoff inventory only. It consumes N20 I5's
susceptibility_update contract as the current N22 primitive contract, and N21
WR6/ND5/N21-C6 only as prerequisite context. N21 remains closed; the N21 ND6
bridge is recorded as not_supported until N22 produces source-backed durable
susceptibility evidence in later iterations.

I1 does not open susceptibility evidence, assign an SU rung, support durable
geometry modification, or consume N21 WR/ND rows as susceptibility evidence.
Semantic learning, choice, agency, native support, sentience, Phase 8, and
ant-ecology implementation claims remain blocked.
```

## Iteration 2. Schema, Ladder, And Control Freeze

- [x] Freeze N22 candidate evidence row schema.
- [x] Freeze `source_current_inputs` candidate field.
- [x] Freeze `row_specific_thresholds_declared_before_use` candidate field.
- [x] Freeze `n19_native_readiness_boundary_consumption` with allowed value
      `ap_gap_boundary_only`.
- [x] Freeze `n20_source_downstream_consumption_status` as inherited N20 status.
- [x] Freeze source-current definition.
- [x] Freeze run-artifact admissibility.
- [x] Freeze artifact manifest schema.
- [x] Freeze interaction window schema.
- [x] Freeze later re-entry window schema.
- [x] Freeze susceptibility delta schema.
- [x] Freeze allowed delta fields.
- [x] Freeze same-basin invariant fields.
- [x] Freeze `out_of_scope_drift_blocks_row`.
- [x] Freeze `delta_not_label_reassignment`.
- [x] Freeze historical interaction provenance schema.
- [x] Freeze active reinforcement absence schema.
- [x] Freeze active reinforcement demotion/blocking rung effects.
- [x] Freeze peer/same-budget comparison schema.
- [x] Freeze peer comparison as mandatory when route or region conditioned.
- [x] Freeze peer comparison `not_applicable` scope reason.
- [x] Freeze durability metric schema: interaction, replay, re-entry delta
      digests, persistence ratio, threshold/rule, and transient rejection.
- [x] Freeze global-drift rejection as part of durability/conditioning schema.
- [x] Freeze support/coherence/boundary/flux result schema.
- [x] Freeze field-specific support/coherence/boundary/flux acceptance statuses.
- [x] Freeze artifact replay, snapshot/load replay, and duplicate replay
      requirements.
- [x] Freeze `artifact_only_replay` as alias for `artifact_replay`.
- [x] Freeze active-null comparability rule.
- [x] Freeze local `SU0...SU6` ladder.
- [x] Freeze `SU0...SU6` rung support requirements.
- [x] Freeze that rows below `SU3` cannot support durable geometry
      modification.
- [x] Freeze that `SU6` is an N23 handoff rung, not an agency claim.
- [x] Freeze N22 closeout ladder `N22-C0...N22-C6`.
- [x] Freeze that N22-C rungs classify the whole tranche, not individual row
      labels.
- [x] Freeze that N22-C rungs cannot open semantic learning, choice, agency,
      native support, sentience, or Phase 8 claims.
- [x] Freeze AP4/AP5 dependency policy.
- [x] Freeze AP4/AP5 dependency status enums.
- [x] Freeze `ap4_condition_reason` and `ap5_condition_reason`.
- [x] Freeze I3 AP-gap active-null expectations.
- [x] Freeze N21 `ND6` bridge status enum.
- [x] Freeze N21 `ND6` wording as bridge candidate only.
- [x] Freeze row decision policy.
- [x] Freeze claim boundary and unsafe flags.
- [x] Confirm no positive N22 evidence is opened.

Expected artifacts:

```text
outputs/n22_susceptibility_schema_and_controls.json
reports/n22_susceptibility_schema_and_controls.md
scripts/build_n22_susceptibility_schema_and_controls.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_susceptibility_schema_frozen_no_positive_evidence
output_digest = a6d4e478b1e29f31007bb965c97a838764e196f18ca7ac8e1c78a7ccfc03680f
check_count = 26
failed_checks = []
required_candidate_field_count = 61
su_ladder_count = 7
n22_closeout_ladder_count = 7
n19_native_readiness_boundary_consumption = ap_gap_boundary_only
n20_source_downstream_consumption_status = contract_complete_pending_iteration6_closeout
n21_nd6_bridge_status = not_supported
artifact_manifest_required = true
field_specific_gate_acceptance = true
active_reinforcement_remaining_blocks_SU4_SU5_SU6 = true
active_reinforcement_remaining_blocks_N22_C4_N22_C5_N22_C6 = true
active_reinforcement_remaining_blocks_ND6_bridge_by_producer_residue = true
artifact_replay_alias = artifact_only_replay
ap_gap_active_null_expectations = missing_AP4, missing_AP5, prose_only
schema_freeze_only = true
susceptibility_evidence_opened = false
su_ladder_rung_assigned = false
n22_closeout_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
ready_for_iteration_3_active_nulls = true
```

Artifact hashes:

```text
221dae0353bdb5a04c2a324cd9d94b3634de5c66e8ffef3721df1f5791e0f4e5  outputs/n22_susceptibility_schema_and_controls.json
7d3cc839c20d10554ec6143fcd48e2da806b891ac1544dff5e6ec0d3f9c40cbe  reports/n22_susceptibility_schema_and_controls.md
474446f231f92061d447f464a363bbf58931f0a2e8721158b97e2dc512444ce1  scripts/build_n22_susceptibility_schema_and_controls.py
```

Interpretation:

```text
Iteration 2 freezes the N22 schema and control contract. It defines the local
SU0...SU6 susceptibility-update ladder and the tranche-level N22-C0...N22-C6
closeout ladder, but assigns neither. The freeze makes source-current
geometry, threshold declaration, artifact manifests, AP4/AP5 dependency
handling, durable-delta metrics, active-reinforcement absence and rung effects,
field-specific gate acceptance, peer same-budget comparison, replay aliases,
controls, and unsafe-claim boundaries fail-closed requirements for later rows.

I2 does not support susceptibility update, durable geometry modification,
semantic learning, choice, agency, native support, sentience, Phase 8, or
ant-ecology implementation.
```

## Iteration 3. Active Nulls And Failure Baselines

- [x] Show route-label-only change cannot pass.
- [x] Show reinforcement-schedule-only change cannot pass.
- [x] Show one-window flux transient cannot pass as durable modification.
- [x] Show global drift cannot pass as route- or region-conditioned
      susceptibility.
- [x] Show same-budget peer route/region change cannot be ignored when it
      carries the same delta.
- [x] Show missing later re-entry blocks durable susceptibility evidence.
- [x] Show post-hoc delta construction fails closed.
- [x] Show hidden producer reinforcement fails closed.
- [x] Show AP4 dependency omission fails closed when route-conditioned.
- [x] Show AP5 dependency omission fails closed when proxy-conditioned.
- [x] Show AP-gap prose-only handling fails closed.
- [x] Show semantic learning/choice/agency relabels fail closed.
- [x] Confirm active nulls do not assign SU rungs above control scope.

Expected artifacts:

```text
outputs/n22_active_nulls_and_failure_baselines.json
reports/n22_active_nulls_and_failure_baselines.md
scripts/build_n22_active_nulls_and_failure_baselines.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_evidence
output_digest = 4843f5661908cc612d71df1957bc16929ed199b7c2c72134c4f0d67bea750138
check_count = 15
failed_checks = []
row_count = 14
failed_closed_rows = 14
failed_open_rows = 0
required_nulls_present = route_label_only_delta, reinforcement_schedule_only_delta,
  one_window_flux_transient, missing_later_reentry, post_hoc_delta_construction,
  hidden_reinforcement, route_conditioned_row_missing_AP4,
  proxy_or_target_conditioned_row_missing_AP5, AP_gap_prose_only,
  peer_same_budget_missing, global_drift_not_rejected,
  semantic_learning_relabel, native_support_relabel, phase8_relabel
route_label_only_delta_violated_gate = route_label_only_delta
route_label_only_delta_not_label_reassignment = false
schema_instantiation_only = true
schema_expansion = false
positive_susceptibility_evidence_opened = false
susceptibility_update_supported = false
durable_geometry_modification_supported = false
su_ladder_rung_assigned_above_control_scope = false
n22_closeout_ladder_rung_assigned = false
n21_nd6_bridge_status = not_supported
ready_for_iteration_4_positive_probe = true
```

Artifact hashes:

```text
599fc7ee6616714cb48aecab7fc04564f00ad94b5a66063869c631e206935f50  outputs/n22_active_nulls_and_failure_baselines.json
a274d825a863bcc4fcc8c7328446b4894d8ffcddd747e2beb41e7d189c0c636c  reports/n22_active_nulls_and_failure_baselines.md
15b71627a3dd233e789c24686b05211ad9c3bfab4553c48b107de0dc554aa7b8  scripts/build_n22_active_nulls_and_failure_baselines.py
```

Interpretation:

```text
Iteration 3 instantiates the frozen I2 schema as a fail-closed active-null
matrix. It rejects route labels, producer reinforcement labels, one-window flux
transients, missing re-entry, post-hoc deltas, hidden reinforcement, AP4/AP5
omissions, AP-gap prose-only handling, missing peer comparison, unrejected
global drift, semantic learning relabels, native support relabels, and Phase 8
relabels.

The `route_label_only_delta` row explicitly violates the label-reassignment
gate with `delta_not_label_reassignment = false`. `failed_closed` means the
blocker triggered and the claim was rejected; `failed_open` would mean the
blocker triggered but the claim still passed.

I3 supports only false-positive rejection discipline. It does not support
susceptibility update, durable geometry modification, semantic learning,
choice, agency, native support, sentience, Phase 8, or ant-ecology
implementation.
```

## Iteration 4. Minimal Susceptibility Update Probe

- [x] Run first source-backed susceptibility-update candidate.
- [x] Record pre-interaction geometry trace.
- [x] Record source-current inputs.
- [x] Record row-specific thresholds declared before use.
- [x] Record artifact manifest and validate artifact SHA-256 values.
- [x] Record interaction trace.
- [x] Record post-interaction geometry trace.
- [x] Record susceptibility delta trace.
- [x] Record later route or region re-entry trace.
- [x] Record allowed delta fields and same-basin invariant fields.
- [x] Record peer/same-budget comparison when route or region conditioning is
      claimed.
- [x] Record peer comparison scope reason if not applicable.
- [x] Confirm same-basin continuation.
- [x] Confirm support/coherence/boundary/flux gates using field-specific
      acceptance statuses.
- [x] Confirm `derived_report_only = false`.
- [x] Assign only provisional SU rung pending replay/control matrix.
- [x] Keep final N22 support blocked pending later iterations.

Expected artifacts:

```text
outputs/n22_minimal_susceptibility_update_probe.json
reports/n22_minimal_susceptibility_update_probe.md
scripts/build_n22_minimal_susceptibility_update_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_minimal_source_current_su2_candidate_pending_replay_controls
output_digest = 9bee91dba55414c1be3b63dd299b9d3c2629743adf2796cbf4da911a3db769ae
check_count = 24
failed_checks = []
candidate_row = n22_i4_row_01_minimal_route_b_susceptibility_update_probe
row_decision = partial
provisional_su_ladder_rung = SU2
su3_or_stronger_supported = false
susceptibility_update_claim_allowed = false
durable_geometry_modification_supported = false
derived_report_only = false
artifact_manifest_entries = 19
target_route_b_delta = 0.08000000000000007
peer_route_b_delta_under_same_peer_budget = 0.0
target_over_peer_route_delta_margin = 0.08000000000000007
reentry_delta_persistence_ratio = 0.5000000000000111
support_floor_result = preserved
coherence_floor_result = changed_within_allowed_delta_above_floor
boundary_integrity_result = preserved
flux_or_leakage_result = preserved
global_drift_rejected = true
one_window_transient_rejected = false
ap4_dependency_status = required_recorded
ap5_dependency_status = not_applicable
n21_nd6_bridge_status = not_supported
ready_for_iteration_5_durability_replay = true
```

Artifact hashes:

```text
0c3a8246410d48377a44491e0033dc49aada5add42273440599d83573f34a1f8  outputs/n22_minimal_susceptibility_update_probe.json
6e9b922d8ea71d65a592d69345808e008019021930c6b7d9d140714e046d9363  reports/n22_minimal_susceptibility_update_probe.md
5fd3191ca6c2aca6d313fc4e0c46326f2afc69f0f125b9b8037ec769ac2c6e8c  scripts/build_n22_minimal_susceptibility_update_probe.py
```

Interpretation:

```text
Iteration 4 is the first source-backed N22 susceptibility probe. It uses the
LGRC9V3 column-H fixture rather than report-only rows. The target run applies a
prior packet interaction on route_b edge 0 from the center into route_b node 1,
then later re-enters the center through the same route. The same-budget peer
run spends the prior interaction budget on peer edge 1 and then uses the same
route_b re-entry.

Geometrically, the target prior interaction moves 0.08 coherence from the
center into route_b node 1. The peer prior interaction spends the same budget
on node 2, leaving route_b node 1 unchanged. The target route therefore has a
source-current route-local delta of 0.08 while the same-budget peer has 0.0 on
route_b, rejecting a global-budget or scheduler-drift interpretation at I4
scope.

The later route_b re-entry preserves a route_b delta relative to the peer run
with persistence ratio 0.5. That is enough for a provisional SU2
source-current pre/post geometry delta candidate with later re-entry trace, but
not enough for SU3 or durable geometry modification. I5 still must replay the
delta, I7 still must run controls, and final N22 support remains blocked.

The result is not semantic learning, choice, agency, native support, sentience,
Phase 8, ant-ecology implementation, or an N21 ND6 bridge.
```

## Iteration 4-A. Susceptibility Dose / Boundary Probe

- [x] Keep I4 fixture and threshold policy fixed.
- [x] Keep I4 peer/same-budget comparison rule fixed.
- [x] Declare dose ladder before use.
- [x] Run no-prior-interaction control.
- [x] Run below-delta-floor dose row.
- [x] Reproduce I4 reference dose row.
- [x] Run stronger bounded dose row.
- [x] Run high-dose out-of-scope drift row.
- [x] Record source-current artifacts for every target and peer dose run.
- [x] Record artifact manifest and validate SHA-256 values.
- [x] Preserve same-basin gates for positive dose rows.
- [x] Reject no-prior and below-threshold rows fail-closed.
- [x] Block high-dose row when support/coherence/boundary/flux leaves scope.
- [x] Keep all supporting rows provisional SU2 only.
- [x] Keep SU3, durable geometry modification, final N22 support, and N21 ND6
      bridge blocked pending later iterations.

Expected artifacts:

```text
outputs/n22_susceptibility_dose_boundary_probe.json
reports/n22_susceptibility_dose_boundary_probe.md
scripts/build_n22_susceptibility_dose_boundary_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_dose_boundary_su2_extension_pending_replay_controls
output_digest = bfc7856e5685fab47383f3e03e0311f6f140841667a5f36a75b7e6f2b5cd5d6d
check_count = 16
failed_checks = []
dose_rows = 5
artifact_manifest_entries = 87
positive_su2_dose_count = 2
failed_closed_dose_count = 3
highest_bounded_positive_dose = 0.14
first_blocked_high_dose = 0.20
dose_00 = rejected, no_prior_interaction_control_failed_closed
dose_03 = rejected, below_delta_floor_failed_closed
dose_08 = partial, bounded_source_current_SU2_candidate
dose_14 = partial, bounded_source_current_SU2_candidate
dose_20 = blocked, out_of_scope_drift_failed_closed
su3_or_stronger_supported = false
durable_geometry_modification_supported = false
n22_closeout_ladder_rung_assigned = false
n21_nd6_bridge_status = not_supported
ready_for_iteration_5_durability_replay = true
```

Artifact hashes:

```text
a5309761cc68ea297e418a9e94b4e6628368f708a9e229200d5538aa2634d9f6  outputs/n22_susceptibility_dose_boundary_probe.json
cf4ff309be1b4e311f9f9b1954dc24ee82383eedf3108f6a3b34cebe027bb900  reports/n22_susceptibility_dose_boundary_probe.md
851a5a1652527f8dbbea020a25e9505ab01c41cfdf0d7e31929a95c54a0a8559  scripts/build_n22_susceptibility_dose_boundary_probe.py
```

Interpretation:

```text
Iteration 4-A strengthens I4 without replacing it. It keeps the same LGRC9V3
fixture, same threshold policy, same route_b target route, same same-budget peer
rule, and same claim boundary. The only new variable is the declared
prior-interaction dose.

Geometrically, no prior interaction produces no route-local susceptibility
delta. A 0.03 packet dose produces a visible route_b change, but it remains
below the declared route-local delta and re-entry floors, so it fails closed.
The 0.08 I4 reference dose and the 0.14 stronger dose both produce source-
current route_b deltas with same-budget peer route_b delta still at 0.0, so they
remain provisional SU2 candidates. The 0.20 dose produces an even larger route
delta, but it pushes center coherence below the declared floor and is blocked as
out-of-scope drift rather than counted as stronger evidence.

I4-A therefore shows a bounded susceptibility-dose region: 0.00 is rejected as
no-prior control, 0.03 is rejected below floor, 0.08 and 0.14 are provisional
SU2, and 0.20 is blocked by the high-dose same-basin gate.

The result supports only additional provisional SU2 input evidence for I5. It
does not support replay-backed SU3, durable SU4, transfer SU5, SU6, final N22,
N21 ND6 bridge, semantic learning, choice, agency, native support, sentience,
Phase 8, or ant-ecology implementation.
```

## Iteration 4-B. Multi-Path Susceptibility Shape Probe

- [x] Keep I4/I4-A fixture and threshold policy fixed.
- [x] Keep I4/I4-A peer/same-budget comparison rule fixed.
- [x] Declare path rows before use.
- [x] Run single route_b reference path.
- [x] Run competing alternate route path.
- [x] Run complementary split route_b + adjacent route path.
- [x] Run insufficient target-component split path.
- [x] Run over-coupled split path.
- [x] Record source-current artifacts for every target and peer path run.
- [x] Record artifact manifest and validate SHA-256 values.
- [x] Preserve same-basin gates for positive path rows.
- [x] Reject competing route row fail-closed.
- [x] Reject insufficient split row fail-closed.
- [x] Block over-coupled split row when support/coherence/boundary/flux leaves
      scope.
- [x] Keep complementary path evidence geometric only, not cooperation,
      strategy, choice, or agency.
- [x] Keep all supporting rows provisional SU2 only.
- [x] Keep SU3, durable geometry modification, final N22 support, and N21 ND6
      bridge blocked pending later iterations.

Expected artifacts:

```text
outputs/n22_multipath_susceptibility_shape_probe.json
reports/n22_multipath_susceptibility_shape_probe.md
scripts/build_n22_multipath_susceptibility_shape_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_multipath_shape_su2_extension_pending_replay_controls
output_digest = 4ac32cc56502ebc9f4723f171fdc40bb2b059e6a5c167f0d1e837b873064f266
check_count = 20
failed_checks = []
path_rows = 5
artifact_manifest_entries = 87
positive_su2_path_count = 2
failed_closed_path_count = 3
single_route_positive = true
complementary_split_positive = true
competing_route_rejected = true
insufficient_split_rejected = true
overcoupled_split_blocked = true
single_route_b_reference = partial, bounded_single_target_route_SU2_candidate
competing_alternate_route_same_budget = rejected, path_shape_control_failed_closed
complementary_split_route_b_adjacent = partial, bounded_complementary_split_SU2_candidate
split_unrelated_insufficient_route_b = rejected, path_shape_control_failed_closed
overcoupled_multipath_gate_block = blocked, out_of_scope_multipath_drift_failed_closed
positive_rows_consumable_role = source_current_SU2_shape_evidence_only
rejected_su1_rows_role = failure_baseline_only
durability_controls_deferred = true
one_window_transient_rejected_required_in_I5 = true
su3_or_stronger_supported = false
durable_geometry_modification_supported = false
n22_closeout_ladder_rung_assigned = false
n21_nd6_bridge_status = not_supported
ready_for_iteration_5_durability_replay = true
```

Artifact hashes:

```text
c586893462527bd588cce791f7a630ed65782efc0175a254dc36428af85a76a4  outputs/n22_multipath_susceptibility_shape_probe.json
509c5d8338b75d3f961d2384493587222def0d3a6ed12d3ed1be0f745988c11b  reports/n22_multipath_susceptibility_shape_probe.md
0ff8adfe5bdf0c365680464a7e2924d7db6adbf3ab9c647cc8cb3516b9d20b6b  scripts/build_n22_multipath_susceptibility_shape_probe.py
```

Interpretation:

```text
Iteration 4-B strengthens I4 and I4-A by testing path shape while keeping the
same fixture, thresholds, peer comparison rule, and claim boundary. It asks
whether source-current susceptibility depends on where the prior interaction
passes through the graph, not whether the system chooses or cooperates.

Geometrically, the single route_b row reproduces the I4 source-current delta:
route_b node 1 receives the route-local prior interaction and later re-entry
still shows a bounded route_b delta. The competing alternate route spends the
same budget away from route_b and fails closed because route_b susceptibility
delta is absent. The complementary split keeps a sufficient route_b component
while adding adjacent-route flux, so it remains a provisional SU2 multi-path
candidate. The insufficient split spends total budget across paths but leaves
the route_b component below floor, so it is rejected. The over-coupled split
produces a larger route_b delta but crosses the center coherence floor, so it is
blocked as out-of-scope drift.

I4-B therefore shows that route/path shape matters:

single route_b support and complementary route_b+adjacent support can satisfy
the provisional SU2 geometry gates, while competing, insufficient, and
over-coupled paths fail closed. Complementary here means multi-edge geometry
only; it is not cooperation, strategy, choice, agency, native support, or
semantic behavior.

The two positive rows use `row_decision = partial` only in the narrow sense of
`provisional_SU2_input_evidence_pending_I5_I7`; their consumable role is
`source_current_SU2_shape_evidence_only`, and `susceptibility_update_claim_allowed`
remains false. The two rejected `SU1` rows are `failure_baseline_only`, not
positive susceptibility evidence. The complementary split is valid but narrow:
its coherence margin is approximately 0.05 and boundary margin is 0, so I5 must
preserve it under replay or demote it. `one_window_transient_rejected` remains
false until I5 runs durability replay.

The result supports only additional provisional SU2 input evidence for I5. It
does not support replay-backed SU3, durable SU4, transfer SU5, SU6, final N22,
N21 ND6 bridge, semantic learning, choice, agency, native support, sentience,
Phase 8, or ant-ecology implementation.
```

## Iteration 5. Durability Replay Probe

- [x] Replay the provisional susceptibility delta.
- [x] Consume positive provisional SU2 rows from I4.
- [x] Consume positive provisional SU2 rows from I4-A.
- [x] Consume positive provisional SU2 rows from I4-B.
- [x] Treat non-positive I4-A/I4-B rows as controls/context only.
- [x] Record interaction delta digest.
- [x] Record post-replay delta digest.
- [x] Record re-entry delta digest.
- [x] Record delta persistence ratio.
- [x] Record delta threshold or rule.
- [x] Run artifact-only replay.
- [x] Run snapshot/load replay.
- [x] Use stable state signatures when source geometry schemas differ.
- [x] Run duplicate replay where applicable.
- [x] Remove or neutralize producer reinforcement schedule where required.
- [x] Confirm post-snapshot re-entry begins with no active prior-interaction
      queue.
- [x] Confirm delta persists without hidden reinforcement.
- [x] Confirm one-window transient control fails closed.
- [x] Confirm `one_window_transient_rejected = true`.
- [x] Track narrow-margin complementary row.
- [x] Assign only replay-backed provisional SU3 pending I7 controls.
- [x] Keep SU4, final N22, N21 ND6 bridge, semantic learning, and agency
      claims blocked.

Expected artifacts:

```text
outputs/n22_durability_replay_probe.json
reports/n22_durability_replay_probe.md
scripts/build_n22_durability_replay_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_replay_backed_su3_candidates_pending_i7_controls
output_digest = f46306e4550bf4e172a4dae074ccba3096cfdd2e65730fe68c0858b1fee41177
check_count = 19
failed_checks = []
positive_candidate_count = 5
replay_backed_su3_candidate_count = 5
demoted_candidate_count = 0
narrow_margin_candidate_count = 1
one_window_transient_rejected_count = 5
artifact_manifest_entries = 112
i4_minimal_route_b = SU3, artifact/snapshot/duplicate/post-snapshot-reentry passed
dose_08_i4_reference = SU3, artifact/snapshot/duplicate/post-snapshot-reentry passed
dose_14_stronger_bounded = SU3, artifact/snapshot/duplicate/post-snapshot-reentry passed
single_route_b_reference = SU3, artifact/snapshot/duplicate/post-snapshot-reentry passed
complementary_split_route_b_adjacent = SU3, artifact/snapshot/duplicate/post-snapshot-reentry passed, narrow_margin_candidate = true
su4_or_stronger_supported = false
durable_geometry_modification_supported = false
n22_closeout_ladder_rung_assigned = false
n21_nd6_bridge_status = not_supported
ready_for_iteration_6_transfer_reentry_probe = true
ready_for_iteration_7_control_matrix = true
```

Artifact hashes:

```text
fabc510447d3a98c1545c1a2b4c00acb79112c1aec9c47f015af9b4694ba3af0  outputs/n22_durability_replay_probe.json
46898048efc34f50ba5389cd048ffa02466111f5c705e2bc5febbb2a82645418  reports/n22_durability_replay_probe.md
4dc37d6a0c1785eb0c1a17cda6433dc227e67831b7d4802be3aefc8847467ef0  scripts/build_n22_durability_replay_probe.py
```

Interpretation:

```text
Iteration 5 consumes the five positive provisional SU2 rows from I4, I4-A, and
I4-B: the original minimal route_b row, the 0.08 and 0.14 dose rows, the
single-route path row, and the complementary split path row. Non-positive I4-A
and I4-B rows remain controls or blockers only.

Each candidate passes artifact rehashing, snapshot/load replay, duplicate
target/peer replay, and post-snapshot route_b re-entry replay. The post-snapshot
re-entry begins from the saved post-interaction state with no active prior-
interaction event queue and no in-flight reinforcement budget, so the later
route_b expression is not carried by a still-active producer schedule.

Snapshot/load replay uses a stable source-current state signature rather than a
script-specific geometry digest because I4, I4-A, and I4-B emitted slightly
different geometry record schemas. The stable signature still compares the
source-current fields that matter: center support/coherence, route_b coherence,
peer-route coherence, topology/boundary signature, packet budget, and in-flight
packet state.

I5 rejects the one-window-transient reading for these five rows: the route-local
delta survives artifact reconstruction, snapshot loading, duplicate replay, and
post-snapshot re-entry replay. This supports replay-backed provisional SU3
candidate evidence only. The complementary split row remains narrow-margin and
must survive I7 controls.

I5 does not support control-backed durable SU4, transfer SU5, SU6, final N22,
N21 ND6 bridge, semantic learning, choice, agency, native support, sentience,
Phase 8, or ant-ecology implementation.
```

## Iteration 5-A. Replay Durability Stress Probe

- [x] Consume all five I5 replay-backed SU3 candidates.
- [x] Keep the I5 threshold policy unchanged.
- [x] Start from each saved post-interaction state.
- [x] Run baseline post-snapshot re-entry stress.
- [x] Run delayed idle-window re-entry stress.
- [x] Run repeated re-entry stress.
- [x] Run mild unrelated peer-flux-before-re-entry stress.
- [x] Record source-current stress artifacts for every candidate and mode.
- [x] Record artifact manifest and validate SHA-256 values.
- [x] Separate SU3 preservation stress from repeated-reentry depletion.
- [x] Confirm baseline, delayed, and mild-peer-flux modes preserve SU3.
- [x] Record repeated re-entry depletion as fail-closed boundary.
- [x] Track narrow-margin complementary row.
- [x] Keep all rows stress-limited SU3 pending I7 controls.
- [x] Keep SU4, transfer SU5, SU6, final N22, and N21 ND6 bridge blocked.
- [x] Keep semantic learning, choice, agency, native support, sentience,
      Phase 8, and ant-ecology implementation blocked.

Expected artifacts:

```text
outputs/n22_replay_durability_stress_probe.json
reports/n22_replay_durability_stress_probe.md
scripts/build_n22_replay_durability_stress_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_replay_stress_limited_su3_candidates_pending_i7_controls
output_digest = 2602c7b3fb99b19521b5a72f0615f0ff401aa2cb532674df7eeae2875c48ff27
check_count = 13
failed_checks = []
source_i5_su3_candidate_count = 5
stress_mode_count_per_row = 4
su3_preservation_stress_supported_candidate_count = 5
stress_supported_su3_candidate_count = 0
stress_limited_su3_candidate_count = 5
repeated_reentry_depletion_boundary_count = 5
narrow_margin_candidate_count = 1
i4_minimal_route_b = SU3_stress_limited, baseline/delayed/mild-peer passed, repeated re-entry failed closed
dose_08_i4_reference = SU3_stress_limited, baseline/delayed/mild-peer passed, repeated re-entry failed closed
dose_14_stronger_bounded = SU3_stress_limited, baseline/delayed/mild-peer passed, repeated re-entry failed closed
single_route_b_reference = SU3_stress_limited, baseline/delayed/mild-peer passed, repeated re-entry failed closed
complementary_split_route_b_adjacent = SU3_stress_limited, baseline/delayed/mild-peer passed, repeated re-entry failed closed, narrow_margin_candidate = true
su4_or_stronger_supported = false
durable_geometry_modification_supported = false
n22_closeout_ladder_rung_assigned = false
n21_nd6_bridge_status = not_supported
ready_for_iteration_6_transfer_reentry_probe = true
ready_for_iteration_7_control_matrix = true
```

Artifact hashes:

```text
c7da8eb8349a6f6bc9331b309fffe623269ddbe840b516e9d7d7d042b050df8d  outputs/n22_replay_durability_stress_probe.json
c986837720c1a34ce775d26cc1a80ae0cc2542061ca151ec51d4a71640ff550c  reports/n22_replay_durability_stress_probe.md
e22f606d0c050f7e32c37e6f00818661cf434d9970ae039893e749b3670e2622  scripts/build_n22_replay_durability_stress_probe.py
```

Interpretation:

```text
Iteration 5-A strengthens I5 by adding replay stress without changing the I5
threshold policy or opening SU4. It starts each stress run from the saved
post-interaction state that I5 used for post-snapshot re-entry, with no active
prior-interaction queue and no in-flight reinforcement budget.

Geometrically, the I5 route-local susceptibility delta remains visible when
the later route_b re-entry is repeated from the post-interaction snapshot,
delayed by two idle windows, or preceded by a mild unrelated peer flux. Those
three preservation modes keep the route-local delta above the declared
SU3 persistence ratio and preserve support, coherence, boundary degree, flux
budget, and empty in-flight packet state.

Repeated re-entry exposes the boundary. The first repeated re-entry preserves
the route-local delta, but the second re-entry drains the route_b delta below
the SU3 preservation ratio for every candidate. That is recorded as a
fail-closed depletion boundary, not as a failure of I5 and not as stronger
durable geometry evidence. The result is therefore stress-limited SU3 evidence:
stronger than clean replay alone, but still below control-backed SU4.

I5-A does not support durable SU4, transfer SU5, SU6, final N22, the N21 ND6
bridge, semantic learning, choice, agency, native support, sentience, Phase 8,
or ant-ecology implementation.
```

## Iteration 6. Transfer / Re-entry Probe

- [ ] Declare later route, boundary, corridor, or region re-entry context.
- [ ] Consume I5 replay-backed SU3 rows and I5-A stress-limited SU3 rows.
- [ ] Preserve repeated-reentry depletion as a boundary, not a success.
- [ ] Test whether susceptibility delta is expressed in later re-entry.
- [ ] Confirm same-budget peer route/region does not show the same delta unless
      the row is demoted to global drift.
- [ ] Confirm re-entry result is not a label swap.
- [ ] Confirm re-entry result is not producer schedule carryover.
- [ ] Confirm replay and same-basin gates remain in scope.
- [ ] Keep general learning, choice, agency, native support, and Phase 8
      blocked.

Expected artifacts:

```text
outputs/n22_transfer_reentry_probe.json
reports/n22_transfer_reentry_probe.md
scripts/build_n22_transfer_reentry_probe.py
```

## Iteration 7. Replay And Control Matrix

- [ ] Consume all provisional N22 candidate rows.
- [ ] Consume all active-null and failure-baseline rows.
- [ ] Run required replay and negative controls.
- [ ] Record every required control status as `passed`, `failed_closed`,
      `failed_open`, `not_run`, or `not_applicable`.
- [ ] Demote or block rows with failed-open or not-run required controls.
- [ ] Assign I7-consumable SU rungs only after controls.
- [ ] Keep closeout pending Iteration 8.

Expected artifacts:

```text
outputs/n22_replay_and_control_matrix.json
reports/n22_replay_and_control_matrix.md
scripts/build_n22_replay_and_control_matrix.py
```

## Iteration 8. Closeout And N23 Handoff

- [ ] Classify final N22 susceptibility-update result.
- [ ] Record final SU ladder rung.
- [ ] Record producer residue.
- [ ] Record naturalization debt.
- [ ] Record AP4/AP5 dependency status.
- [ ] Record N21 `ND6` bridge status.
- [ ] Record final claim ceiling.
- [ ] Record unsafe claim blockers.
- [ ] Confirm semantic learning, choice, agency, native support, sentience,
      Phase 8, and ant-ecology implementation remain blocked.
- [ ] Confirm `src_diff_empty`.
- [ ] Record N23 handoff for live-continuation collapse / selection geometry.

Expected artifacts:

```text
outputs/n22_closeout_and_n23_handoff.json
reports/n22_closeout_and_n23_handoff.md
scripts/build_n22_closeout_and_n23_handoff.py
```
