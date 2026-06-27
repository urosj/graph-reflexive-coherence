# N23 Live-Continuation Collapse And Selection Geometry Implementation Checklist

## Initialization

- [x] Create `experiment-N23` branch.
- [x] Create N23 experiment directory.
- [x] Add top-level N23 `README.md`.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add `configs/`, `hypotheses/`, `outputs/`, `reports/`, and `scripts/`
      scaffolds.
- [x] Add hypothesis records.
- [x] Keep N23 scoped to live-continuation collapse / selection geometry.
- [x] Confirm N23 starts from N20/N22 handoff evidence, not N23 primitive
      evidence.

## Global Rules

- [x] Use source IDs, titles, and relative paths only.
- [x] Confirm generated records contain no local absolute paths.
- [x] Consume N20 `live_continuation_collapse` contract without redefinition.
- [x] Consume N22 closeout as prerequisite context only.
- [x] Confirm N22 susceptibility-update evidence is not used as selection
      evidence.
- [x] Treat N19 as AP-gap boundary only, not live-continuation evidence.
- [x] Record `n19_native_readiness_boundary_consumption =
      ap_gap_boundary_only`.
- [x] Record `n20_source_downstream_consumption_status` when inherited.
- [x] Record `n22_source_closeout_status` when inherited.
- [x] Declare row-specific thresholds before use.
- [x] Record `source_current_inputs` in every candidate row.
- [x] Require `artifact_manifest` in every candidate row.
- [x] Require `all_artifact_sha256_match_file_contents = true` for positive
      support.
- [x] Require actual LGRC/source-current run artifacts for positive collapse
      evidence.
- [x] Reject report-only or synthetic-row success as insufficient evidence.
- [x] Separate source-current branch geometry from selected-branch labels and
      producer preferences.
- [x] Treat producer-mediated branch ranking or selected labels as producer
      residue unless source-backed naturalization evidence is produced.
- [x] Treat naturalization-debt fields as debt unless source-backed evidence is
      produced.
- [x] Reject blocked relabel fields when used as evidence.
- [x] Carry AP4 dependency row-locally when route or branch selection
      participates.
- [x] Carry conditional AP5 dependency when proxy or target formation
      participates.
- [x] Use closed AP4/AP5 dependency status enums.
- [x] Record `ap4_condition_reason` and `ap5_condition_reason` per row.
- [x] Freeze live branch alternatives separately from collapsed continuation.
- [x] Require counterfactual branch retention for collapse support.
- [x] Define counterfactual retention as immutable pre-collapse audit evidence,
      not continued dynamic activity after collapse.
- [x] Require `selection_not_label_reassignment = true`.
- [x] Require live branches to be same-run, same-window, and pre-collapse.
- [x] Require `branch_record_origin = source_current_same_run` for LC2+.
- [x] Reject independent-run, replay-fork, report-side, or post-hoc
      alternatives as original live-branch-set evidence.
- [x] Require branch-specific support/coherence and boundary/flux traces.
- [x] Require branch/collapse temporal ordering gates.
- [x] Freeze selected-branch source-current reason as a closed enum.
- [x] Block producer labels, producer preference, random ties, post-hoc report
      selection, single-branch relabels, and semantic-choice labels as selected
      branch reasons.
- [x] Block inherited N22 susceptibility from counting as N23 selection evidence
      unless expressed in N23 source-current branch geometry.
- [x] Freeze artifact roles for N23 evidence.
- [x] Reject positive LC support when artifacts are only reports, inherited
      context, source contracts, or closeouts.
- [x] Block rows when out-of-scope drift exceeds the declared collapse scope.
- [x] Require replay-window survival for collapse support.
- [x] Require fake-alternative controls to fail closed.
- [x] Require single-branch relabel controls to fail closed.
- [x] Require post-hoc selected-branch controls to fail closed.
- [x] Require producer preference injection controls to fail closed.
- [x] Require random-tie-as-collapse controls to fail closed.
- [x] Force unsafe claim flags false in every row.
- [x] Do not modify `src/*`.
- [x] Do not write ant-ecology implementation specs in N23.
- [x] Keep semantic choice, intention, agency, native support, sentience, and
      Phase 8 claims blocked.

## Iteration 1. Source Handoff Inventory

- [x] Build N23 source handoff inventory.
- [x] Read N20 closeout and same-basin continuation contract.
- [x] Read N20 live-continuation collapse contract row.
- [x] Read N22 closeout and N23 handoff.
- [x] Record N22 producer-mediated SU5 context.
- [x] Record AP4/AP5 gap discipline.
- [x] Record required source-current branch/collapse fields.
- [x] Record producer-mediated fields and naturalization-debt fields.
- [x] Record required controls.
- [x] Confirm no live-continuation collapse evidence is opened.
- [x] Confirm no semantic choice, intention, agency, native support, sentience,
      Phase 8, or ant-ecology claim is opened.

Expected artifacts:

```text
outputs/n23_source_handoff_inventory.json
reports/n23_source_handoff_inventory.md
scripts/build_n23_source_handoff_inventory.py
```

Iteration 1 result:

```text
status = passed
acceptance_state = accepted_source_handoff_inventory_no_live_continuation_evidence
failed_checks = []
source_contract_row = n20_i4_row_04_live_continuation_collapse
source_consumable_contract_row = n20_i5_row_04_live_continuation_collapse
n22_source_closeout_status = passed
n22_context = N22-C6, SU5 producer-mediated bounded susceptibility-update context
n19_boundary = AP4/AP5 NAT4 gaps preserved
lc_ladder_rung_assigned = false
n23_closeout_ladder_rung = N23-C0_inventory_only
ap4_bridge_status = not_supported_inventory_only
planned_canonical_controls_ready_for_i2_i3 = true
```

Iteration 1 interpretation:

```text
I1 is an inventory artifact only. It confirms that N23 has a complete N20
live-continuation-collapse contract, that N22 is consumable only as bounded
producer-mediated susceptibility context, and that AP4/AP5 gap discipline is
still active. It does not support a live branch set, collapse,
counterfactual-retention, AP4 bridge, semantic choice, agency, native support,
sentience, Phase 8, or ant ecology.
```

## Iteration 2. Schema, Ladder, And Control Freeze

- [x] Freeze N23 candidate evidence row schema.
- [x] Freeze `source_current_inputs` candidate field.
- [x] Freeze `row_specific_thresholds_declared_before_use` candidate field.
- [x] Freeze `n19_native_readiness_boundary_consumption` with allowed value
      `ap_gap_boundary_only`.
- [x] Freeze `n20_source_downstream_consumption_status`.
- [x] Freeze `n22_source_closeout_status`.
- [x] Split N20 I4 primitive contract row digest from N20 I5 consumable
      same-basin/control contract row digest.
- [x] Freeze source-current branch-set definition.
- [x] Freeze operational live-branch acceptance: same source-current run, same
      declared branch window, before collapse-window start.
- [x] Freeze trace status/origin fields for live branch, collapse, and
      counterfactual-retention traces.
- [x] Freeze `branch_record_origin` enum.
- [x] Freeze that LC2+ requires `branch_record_origin =
      source_current_same_run`.
- [x] Freeze run-artifact admissibility.
- [x] Freeze artifact manifest schema.
- [x] Freeze artifact path and SHA equality with manifest path and SHA fields.
- [x] Freeze artifact role enum and positive-support artifact role restrictions.
- [x] Freeze branch window schema.
- [x] Freeze collapse window schema.
- [x] Freeze branch/collapse temporal ordering gates.
- [x] Freeze live branch set schema.
- [x] Freeze collapsed continuation schema.
- [x] Freeze counterfactual branch retention schema.
- [x] Freeze that counterfactual retention is immutable pre-collapse audit
      evidence, not continued dynamic activity after collapse.
- [x] Freeze selected-branch source-current reason schema.
- [x] Freeze selected-branch source-current reason allowed and blocked values.
- [x] Freeze AP4-relevant selected-branch reason subset and required
      route/branch-conditioned comparisons.
- [x] Freeze that `susceptibility_delta_conditioned` cannot pass when the
      susceptibility delta is inherited only from N22 and not expressed in N23
      source-current branch geometry.
- [x] Freeze row-local N22-inherited-delta blocker and N23 susceptibility
      expression trace requirement.
- [x] Freeze producer preference absence schema.
- [x] Freeze fake-alternative, single-branch, post-hoc, producer-preference,
      random-tie, and semantic-choice controls.
- [x] Freeze canonical I3 control IDs, including random-tie,
      missing-counterfactual-retention, N22-susceptibility-as-choice,
      route-missing-AP4, proxy-missing-AP5, AP-gap-prose-only, agency,
      native-support, and Phase-8 relabel controls.
- [x] Freeze numeric threshold fields before positive probes:
      `support_floor_value`, `coherence_floor_value`,
      `boundary_integrity_floor_value`, `flux_or_leakage_bound`,
      `collapse_persistence_ratio_threshold`,
      `branch_distinguishability_threshold`, and `same_basin_drift_bound`.
- [x] Freeze support/coherence/boundary/flux result schema.
- [x] Freeze that `not_applicable` support/coherence/boundary/flux results
      block LC2+ candidate support.
- [x] Freeze artifact replay, snapshot/load replay, and duplicate replay
      requirements.
- [x] Freeze `failed_closed` semantics as a satisfied negative control, not
      automatic positive-candidate demotion.
- [x] Freeze active-null comparability rule.
- [x] Freeze local `LC0...LC6` ladder.
- [x] Freeze `LC0...LC6` rung support requirements.
- [x] Freeze that rows below `LC3` cannot support collapse.
- [x] Freeze that `LC6` is an N24 handoff rung, not an agency or semantic
      choice claim.
- [x] Freeze N23 closeout ladder `N23-C0...N23-C6`.
- [x] Freeze AP4/AP5 dependency policy.
- [x] Freeze AP4/AP5 dependency status enums.
- [x] Confirm inventory/meta AP status values are not valid candidate-row AP
      dependency statuses.
- [x] Freeze AP4 bridge status enum.
- [x] Freeze expanded AP4 bridge blocker reasons.
- [x] Freeze row decision policy.
- [x] Freeze claim boundary and unsafe flags.
- [x] Confirm no positive N23 evidence is opened.

Expected artifacts:

```text
outputs/n23_live_continuation_schema_and_controls.json
reports/n23_live_continuation_schema_and_controls.md
scripts/build_n23_live_continuation_schema_and_controls.py
```

Iteration 2 result:

```text
status = passed
acceptance_state = accepted_live_continuation_schema_frozen_no_positive_evidence
failed_checks = []
check_count = 34
candidate_evidence_field_count = 80
lc_ladder_count = 7
n23_closeout_ladder_count = 7
ap4_bridge_status = not_supported
n23_closeout_ceiling = N23-C0_schema_freeze_only
```

Iteration 2 interpretation:

```text
I2 freezes candidate-row schema, branch/collapse ordering, source-current branch
origin, counterfactual-retention meaning, selected-branch reason enums,
artifact roles, canonical controls, AP dependency enums, AP4 bridge blockers,
threshold surfaces, replay/control policy, row decisions, and claim boundaries.
It also clarifies that required negative controls satisfy the control gate when
they fail closed; only `failed_open`, `not_run`, or explicit `rung_effect`
demotion blocks the dependent positive row.
It opens no live branch set, collapse, counterfactual-retention, AP4 bridge,
semantic choice, agency, native support, sentience, Phase 8, or ant ecology
evidence.
```

## Iteration 3. Active Nulls And Failure Baselines

- [ ] Instantiate fake-alternative active null.
- [ ] Instantiate single-branch relabel active null.
- [ ] Instantiate post-hoc selected branch active null.
- [ ] Instantiate producer preference injection active null.
- [ ] Instantiate random-tie-as-collapse active null.
- [ ] Instantiate missing-counterfactual-retention active null.
- [ ] Instantiate N22-susceptibility-as-choice relabel active null.
- [ ] Instantiate route-conditioned missing-AP4 active null.
- [ ] Instantiate proxy-conditioned missing-AP5 active null.
- [ ] Instantiate AP-gap prose-only active null.
- [ ] Instantiate semantic-choice relabel active null.
- [ ] Instantiate agency/native-support/Phase-8 relabel active nulls.
- [ ] Confirm all active nulls fail closed.
- [ ] Confirm no LC rung is assigned above null/control scope.

Expected artifacts:

```text
outputs/n23_active_nulls_and_failure_baselines.json
reports/n23_active_nulls_and_failure_baselines.md
scripts/build_n23_active_nulls_and_failure_baselines.py
```

## Iteration 4. Minimal Live-Branch Collapse Probe

- [ ] Build the first source-current live branch set probe.
- [ ] Record at least two live branch alternatives.
- [ ] Record branch support/coherence traces.
- [ ] Record branch boundary/flux traces.
- [ ] Record collapse from live branch set to one continuation.
- [ ] Record counterfactual branch retention.
- [ ] Keep result provisional pending replay/control validation.
- [ ] Keep semantic choice, intention, agency, and native support blocked.

Expected artifacts:

```text
outputs/n23_minimal_live_branch_collapse_probe.json
reports/n23_minimal_live_branch_collapse_probe.md
scripts/build_n23_minimal_live_branch_collapse_probe.py
```

## Iteration 5. Collapse Replay And Counterfactual Controls

- [ ] Replay minimal collapse artifact.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay where applicable.
- [ ] Run order-inversion control.
- [ ] Run post-hoc stitching control.
- [ ] Run fake-alternative control.
- [ ] Run single-branch relabel control.
- [ ] Run producer preference injection control.
- [ ] Run random-tie-as-collapse control.
- [ ] Classify LC4 eligibility.

Expected artifacts:

```text
outputs/n23_collapse_replay_and_counterfactual_controls.json
reports/n23_collapse_replay_and_counterfactual_controls.md
scripts/build_n23_collapse_replay_and_counterfactual_controls.py
```

## Iteration 6. AP4-Relevant Selection Geometry Probe

- [ ] Test route/branch-conditioned source-current selection geometry.
- [ ] Record AP4 dependency row-locally.
- [ ] Preserve AP5 as conditional only.
- [ ] Verify selected branch is geometry-conditioned, not producer-preference
      conditioned.
- [ ] Verify counterfactual branches remain auditable.
- [ ] Classify AP4 bridge status as candidate, blocked, or not supported.
- [ ] Keep semantic choice and agency blocked.

Expected artifacts:

```text
outputs/n23_ap4_selection_geometry_probe.json
reports/n23_ap4_selection_geometry_probe.md
scripts/build_n23_ap4_selection_geometry_probe.py
```

## Iteration 7. Replay And Control Matrix

- [ ] Consume all provisional N23 candidate rows.
- [ ] Consume all active-null and failure-baseline rows.
- [ ] Run required replay and negative controls.
- [ ] Record every required control status as `passed`, `failed_closed`,
      `failed_open`, `not_run`, or `not_applicable`.
- [ ] Demote or block rows with failed-open or not-run required controls.
- [ ] Assign I7-consumable LC rungs only after controls.
- [ ] Keep closeout pending Iteration 8.

Expected artifacts:

```text
outputs/n23_replay_and_control_matrix.json
reports/n23_replay_and_control_matrix.md
scripts/build_n23_replay_and_control_matrix.py
```

## Iteration 8. Closeout And N24 Handoff

- [ ] Classify final N23 live-continuation collapse result.
- [ ] Record final LC ladder rung.
- [ ] Record AP4 bridge status.
- [ ] Record producer residue.
- [ ] Record naturalization debt.
- [ ] Record AP4/AP5 dependency status.
- [ ] Record final claim ceiling.
- [ ] Record unsafe claim blockers.
- [ ] Confirm semantic choice, intention, agency, native support, sentience,
      Phase 8, and ant-ecology implementation remain blocked.
- [ ] Confirm `src_diff_empty`.
- [ ] Record N24 handoff for abundance / surplus-supported optionality.

Expected artifacts:

```text
outputs/n23_closeout_and_n24_handoff.json
reports/n23_closeout_and_n24_handoff.md
scripts/build_n23_closeout_and_n24_handoff.py
```
