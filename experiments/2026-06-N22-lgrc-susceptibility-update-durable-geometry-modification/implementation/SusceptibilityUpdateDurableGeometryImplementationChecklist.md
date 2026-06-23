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

- [ ] Show route-label-only change cannot pass.
- [ ] Show reinforcement-schedule-only change cannot pass.
- [ ] Show one-window flux transient cannot pass as durable modification.
- [ ] Show global drift cannot pass as route- or region-conditioned
      susceptibility.
- [ ] Show same-budget peer route/region change cannot be ignored when it
      carries the same delta.
- [ ] Show missing later re-entry blocks durable susceptibility evidence.
- [ ] Show post-hoc delta construction fails closed.
- [ ] Show hidden producer reinforcement fails closed.
- [ ] Show AP4 dependency omission fails closed when route-conditioned.
- [ ] Show AP5 dependency omission fails closed when proxy-conditioned.
- [ ] Show AP-gap prose-only handling fails closed.
- [ ] Show semantic learning/choice/agency relabels fail closed.
- [ ] Confirm active nulls do not assign SU rungs above control scope.

Expected artifacts:

```text
outputs/n22_active_nulls_and_failure_baselines.json
reports/n22_active_nulls_and_failure_baselines.md
scripts/build_n22_active_nulls_and_failure_baselines.py
```

## Iteration 4. Minimal Susceptibility Update Probe

- [ ] Run first source-backed susceptibility-update candidate.
- [ ] Record pre-interaction geometry trace.
- [ ] Record source-current inputs.
- [ ] Record row-specific thresholds declared before use.
- [ ] Record artifact manifest and validate artifact SHA-256 values.
- [ ] Record interaction trace.
- [ ] Record post-interaction geometry trace.
- [ ] Record susceptibility delta trace.
- [ ] Record later route or region re-entry trace.
- [ ] Record allowed delta fields and same-basin invariant fields.
- [ ] Record peer/same-budget comparison when route or region conditioning is
      claimed.
- [ ] Record peer comparison scope reason if not applicable.
- [ ] Confirm same-basin continuation.
- [ ] Confirm support/coherence/boundary/flux gates using field-specific
      acceptance statuses.
- [ ] Confirm `derived_report_only = false`.
- [ ] Assign only provisional SU rung pending replay/control matrix.
- [ ] Keep final N22 support blocked pending later iterations.

Expected artifacts:

```text
outputs/n22_minimal_susceptibility_update_probe.json
reports/n22_minimal_susceptibility_update_probe.md
scripts/build_n22_minimal_susceptibility_update_probe.py
```

## Iteration 5. Durability Replay Probe

- [ ] Replay the provisional susceptibility delta.
- [ ] Record interaction delta digest.
- [ ] Record post-replay delta digest.
- [ ] Record re-entry delta digest.
- [ ] Record delta persistence ratio.
- [ ] Record delta threshold or rule.
- [ ] Run artifact-only replay.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay where applicable.
- [ ] Remove or neutralize producer reinforcement schedule where required.
- [ ] Confirm delta persists without hidden reinforcement.
- [ ] Confirm one-window transient control fails closed.
- [ ] Confirm `one_window_transient_rejected = true`.
- [ ] Keep semantic learning and agency claims blocked.

Expected artifacts:

```text
outputs/n22_durability_replay_probe.json
reports/n22_durability_replay_probe.md
scripts/build_n22_durability_replay_probe.py
```

## Iteration 6. Transfer / Re-entry Probe

- [ ] Declare later route, boundary, corridor, or region re-entry context.
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
