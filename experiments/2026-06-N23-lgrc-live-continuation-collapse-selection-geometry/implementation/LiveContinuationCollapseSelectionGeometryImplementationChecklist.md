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

- [x] Instantiate fake-alternative active null.
- [x] Instantiate single-branch relabel active null.
- [x] Instantiate post-hoc selected branch active null.
- [x] Instantiate producer preference injection active null.
- [x] Instantiate random-tie-as-collapse active null.
- [x] Instantiate missing-counterfactual-retention active null.
- [x] Instantiate N22-susceptibility-as-choice relabel active null.
- [x] Instantiate route-conditioned missing-AP4 active null.
- [x] Instantiate proxy-conditioned missing-AP5 active null.
- [x] Instantiate AP-gap prose-only active null.
- [x] Instantiate semantic-choice relabel active null.
- [x] Instantiate agency/native-support/Phase-8 relabel active nulls.
- [x] Confirm all active nulls fail closed.
- [x] Confirm no LC rung is assigned above null/control scope.

Expected artifacts:

```text
outputs/n23_active_nulls_and_failure_baselines.json
reports/n23_active_nulls_and_failure_baselines.md
scripts/build_n23_active_nulls_and_failure_baselines.py
```

Iteration 3 result:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_evidence
failed_checks = []
check_count = 22
active_null_row_count = 14
failed_closed_rows = 14
failed_open_rows = 0
candidate_required_field_count = 80
active_null_extension_field_count = 24
positive_live_continuation_evidence_opened = false
lc_ladder_rung_assigned_above_control_scope = false
n23_closeout_ceiling = N23-C1_active_null_control_discipline_established
n23_closeout_ladder_rung_assigned = false
ap4_bridge_status = not_supported
ready_for_iteration_4_positive_probe = true
output_digest = 05b65af917c90a8b16286c9c8b78386199188a23fa4dffa1ea3d503c165777dd
```

Iteration 3 interpretation:

```text
I3 instantiates the frozen I2 schema as pre-positive active nulls only. The
rows can reject false-positive paths, but they do not provide source-current
live branch evidence, collapse evidence, counterfactual retention, replay-
backed LC rungs, AP4 bridge support, semantic choice, agency, native support,
sentience, Phase 8, or ant-ecology implementation.

failed_closed means the false-positive blocker triggered and the unsafe/null
claim was rejected. It satisfies the negative-control gate and does not
automatically demote future positive rows.

Rows that contain source-current-shaped traces are active-null fixtures only:
`trace_admissibility = active_null_fixture_only_not_positive_evidence`,
`positive_evidence_admissible = false`, and `control_execution_kind =
schema_instantiation_only`. They cannot be consumed as LC2/LC3 source-current
evidence by I4/I7.

I3 rows use all 80 I2 candidate fields plus 24 declared active-null metadata
extension fields. The artifact validates exact row field-set equality against
`I2 required fields U active_null_extension_fields`, so active-null metadata is
acknowledged and bounded rather than silent schema drift.
```

Iteration 3 geometric reading:

```text
The active nulls show what is not enough geometrically: alternative labels are
not branch geometry; one branch is not a live branch set; post-hoc selection is
not in-collapse selection; producer preference and random ties are not source-
current geometric dominance; missing counterfactual retention makes collapse
indistinguishable from a single-path history; inherited N22 susceptibility is
context, not N23 branch-choice evidence; AP4/AP5 dependencies must be row-
local; semantic choice, agency, native support, and Phase 8 labels add no LGRC
branch/collapse geometry.
```

## Iteration 4. Minimal Live-Branch Collapse Probe

- [x] Build the first source-current live branch set probe.
- [x] Record at least two live branch alternatives.
- [x] Record branch support/coherence traces.
- [x] Record branch boundary/flux traces.
- [x] Record collapse from live branch set to one continuation.
- [x] Record counterfactual branch retention.
- [x] Keep result provisional pending replay/control validation.
- [x] Keep semantic choice, intention, agency, and native support blocked.

Result:

```text
status = passed
acceptance_state = accepted_minimal_source_current_lc3_candidate_pending_replay_controls
output_digest = 720890f8a556409625b83bdade1f3d21fa92368a2ffc5a7ce87dd35148220626
candidate_rows = 1
failed_checks = []
row_decision = partial
provisional_lc_ladder_rung = LC3
live_continuation_collapse_claim_allowed = false
ready_for_iteration_5_replay_controls = true
```

Geometric interpretation:

I4 creates a live branch set inside one LGRC9V3 runtime state rather than
constructing a branch set after the fact. Two distinct candidate continuations
are recorded:

```text
branch_edge_0_node_1:
  edge_id = 0
  source_node_coherence = 13.000000000000
  support_gradient_score = 1.500000000000

branch_edge_4_node_5:
  edge_id = 4
  source_node_coherence = 11.000000000000
  support_gradient_score = 2.000000000000
```

The selected continuation is `branch_edge_4_node_5`, because its
source-current support-gradient score exceeds the runner-up by the frozen
margin:

```text
selection_reason = support_gradient_dominance
selected_branch_score = 2.000000000000
runner_up_score = 1.500000000000
score_margin = 0.500000000000
minimum_required_margin = 0.250000000000
selected_packet_amount = 0.060000000000
```

The producer schedules one packet along the selected branch and records the
actual departure, arrival, eligibility, local update, and causal-spark events.
The non-selected branch remains as an immutable pre-collapse counterfactual
record, so I4 has both:

```text
source-current live branch set exists before collapse
one branch collapses into the continued trace
non-selected branch remains auditable as a counterfactual record
```

The geometric gates pass only at provisional LC3 scope:

```text
support_floor_result = changed_within_allowed_delta_above_floor
coherence_floor_result = changed_within_allowed_delta_above_floor
boundary_integrity_result = preserved
flux_or_leakage_result = preserved
collapse_persistence_ratio = 1.000000000000
```

Claim boundary:

```text
LC4/LC5/LC6 = blocked pending I5 replay and I7 controls
AP4 bridge = not supported
semantic choice = false
semantic intention = false
agency = false
native support = false
sentience = false
Phase 8 = false
ant ecology implementation = false
```

Expected artifacts:

```text
outputs/n23_minimal_live_branch_collapse_probe.json
reports/n23_minimal_live_branch_collapse_probe.md
scripts/build_n23_minimal_live_branch_collapse_probe.py
```

## Iteration 4-A. Multi-Branch Live-Set Collapse Probe

- [x] Build an additive source-current live branch set probe with 3+ branches.
- [x] Preserve I4 as the minimal two-branch path.
- [x] Record branch support/coherence traces for every branch.
- [x] Record branch boundary/flux traces for every branch.
- [x] Record collapse from the multi-branch set to one continuation.
- [x] Retain all non-selected branches as counterfactual audit records.
- [x] Keep result provisional pending I5-A replay/control validation.
- [x] Keep semantic choice, intention, agency, and native support blocked.

Result:

```text
status = passed
acceptance_state = accepted_multibranch_source_current_lc3_candidate_pending_i5a
output_digest = 1c52af46ebbedadf8cd0bee091ad14785c58b21e412f8c01a06c315261ce5339
candidate_rows = 1
failed_checks = []
i4_replaced = false
branch_count = 4
retained_non_selected_branch_count = 3
row_decision = partial
provisional_lc_ladder_rung = LC3
live_continuation_collapse_claim_allowed = false
ready_for_iteration_5a_replay_controls = true
```

Geometric interpretation:

I4-A keeps the same single-basin framing as I4, but strengthens the live-set
breadth from two branch alternatives to four source-current alternatives:

```text
branch_edge_0_node_1:
  edge_id = 0
  source_node_coherence = 13.000000000000
  support_gradient_score = 1.500000000000

branch_edge_4_node_5:
  edge_id = 4
  source_node_coherence = 11.000000000000
  support_gradient_score = 2.000000000000

branch_edge_6_node_7:
  edge_id = 6
  source_node_coherence = 10.250000000000
  support_gradient_score = 1.000000000000

branch_edge_8_node_9:
  edge_id = 8
  source_node_coherence = 12.000000000000
  support_gradient_score = 0.500000000000
```

The selected continuation remains `branch_edge_4_node_5` because the same
source-current support-gradient dominance rule selects it over three retained
counterfactual branches:

```text
selection_reason = support_gradient_dominance
selected_branch_score = 2.000000000000
runner_up_score = 1.500000000000
score_margin = 0.500000000000
minimum_required_margin = 0.250000000000
selected_packet_amount = 0.060000000000
```

I4-A therefore adds:

```text
source-current multi-branch live set exists before collapse
one branch collapses into the continued trace
three non-selected branches remain auditable as counterfactual records
```

Claim boundary:

```text
I4 replaced = false
LC4/LC5/LC6 = blocked pending I5-A replay and I7 controls
AP4 bridge = not supported
semantic choice = false
semantic intention = false
agency = false
native support = false
sentience = false
Phase 8 = false
ant ecology implementation = false
```

Expected artifacts:

```text
outputs/n23_multibranch_live_set_collapse_probe.json
reports/n23_multibranch_live_set_collapse_probe.md
scripts/build_n23_multibranch_live_set_collapse_probe.py
```

## Iteration 5. Collapse Replay And Counterfactual Controls

- [x] Replay minimal collapse artifact.
- [x] Run snapshot/load replay.
- [x] Run duplicate replay where applicable.
- [x] Run order-inversion control.
- [x] Run post-hoc stitching control.
- [x] Run fake-alternative control.
- [x] Run single-branch relabel control.
- [x] Run missing-counterfactual-retention control.
- [x] Run producer preference injection control.
- [x] Run random-tie-as-collapse control.
- [x] Classify LC4 eligibility.

Result:

```text
status = passed
acceptance_state = accepted_collapse_replay_controls_lc4_candidate_pending_i6_i7
output_digest = cf4be49967d53453a71659e9a1db182f41d63db78a1d88ea4fcc9206646114b7
failed_checks = []
replay_rows = 1
replay_backed_lc4_candidate_count = 1
negative_control_failed_closed_count = 7
failed_open_control_count = 0
provisional_lc_ladder_rung = LC4
lc5_or_stronger_supported = false
ap4_bridge_status = not_supported
live_continuation_collapse_claim_allowed = false
replay_rows_are_candidate_evidence_rows = false
replay_rows_are_replay_control_records = true
ready_for_iteration_6_ap4_probe = true
ready_for_iteration_7_full_control_matrix = true
```

Replay interpretation:

```text
artifact_replay = passed
snapshot_load_replay = passed
duplicate_replay = passed
order_inversion_control = failed_closed
post_hoc_stitching_control = failed_closed
fake_alternative_control = failed_closed
single_branch_relabel_control = failed_closed
missing_counterfactual_retention_control = failed_closed
producer_preference_injection_control = failed_closed
random_tie_as_collapse_control = failed_closed
```

Geometric interpretation:

I5 tests whether the I4 branch collapse remains the same when reconstructed
from source artifacts instead of trusted as a single generated record.

Artifact replay rehashes every I4 runtime, branch-set, collapse, and
counterfactual-retention artifact. Snapshot/load replay reloads the saved
pre-collapse and post-collapse LGRC9V3 states and confirms that the basin
signatures match the recorded I4 signatures. Duplicate replay starts from the
I4 pre-collapse snapshot, recomputes the selected branch from the loaded
pre-collapse branch geometry, schedules the recomputed selected branch packet,
drains the LGRC event queue, and reproduces the collapse observables:

```text
selected_branch_id = branch_edge_4_node_5
selection_reason = support_gradient_dominance
selected_score = 2.000000000000
runner_up_score = 1.500000000000
score_margin = 0.500000000000
selected_packet_amount = 0.060000000000
collapse_persistence_ratio = 1.000000000000
```

The negative controls fail closed. This means the control narratives are
rejected by constructed negative-control evaluation, not that the positive
replay failed:

```text
order inversion cannot place collapse before branch evidence
post-hoc stitching cannot assemble branches after observing collapse
fake alternatives cannot replace source-current branch records
a single branch cannot be relabeled as a live branch set
missing counterfactual retention cannot support collapse
producer preference cannot replace support-gradient dominance
random tie cannot be relabeled as collapse
```

Schema note:

```text
I5 replay rows are replay/control records, not 80-field candidate evidence
rows. They consume the full I4 candidate row by reference and defer full
candidate-schema revalidation to the I7 control matrix.
```

Claim boundary:

```text
LC4 = replay/control-backed provisional collapse candidate
LC5/LC6 = false
AP4 bridge = not supported
semantic choice = false
semantic intention = false
agency = false
native support = false
sentience = false
Phase 8 = false
ant ecology implementation = false
```

Expected artifacts:

```text
outputs/n23_collapse_replay_and_counterfactual_controls.json
reports/n23_collapse_replay_and_counterfactual_controls.md
scripts/build_n23_collapse_replay_and_counterfactual_controls.py
```

## Iteration 5-A. Multi-Branch Collapse Replay And Controls

- [x] Replay I4-A multi-branch collapse artifact.
- [x] Preserve I5 as the minimal two-branch replay path.
- [x] Run snapshot/load replay for the multi-branch row.
- [x] Run duplicate replay for the multi-branch row.
- [x] Run order-inversion control.
- [x] Run post-hoc stitching control.
- [x] Run fake-alternative control.
- [x] Run single-branch relabel control.
- [x] Run missing-counterfactual-retention control.
- [x] Run producer preference injection control.
- [x] Run random-tie-as-collapse control.
- [x] Classify multi-branch LC4 eligibility.

Result:

```text
status = passed
acceptance_state = accepted_multibranch_collapse_replay_controls_lc4_candidate_pending_i6_i7
output_digest = 1f2ba760cb372fb27f50380adf61ef46c1e89b770b469f3f863c3e2d1d489773
failed_checks = []
replay_rows = 1
i4_replaced = false
i5_replaced = false
branch_count = 4
retained_non_selected_branch_count = 3
replay_backed_multibranch_lc4_candidate_count = 1
negative_control_failed_closed_count = 7
failed_open_control_count = 0
provisional_lc_ladder_rung = LC4
lc5_or_stronger_supported = false
ap4_bridge_status = not_supported
live_continuation_collapse_claim_allowed = false
replay_rows_are_candidate_evidence_rows = false
replay_rows_are_replay_control_records = true
ready_for_iteration_6_ap4_probe = true
ready_for_iteration_7_full_control_matrix = true
```

Replay interpretation:

```text
artifact_replay = passed
snapshot_load_replay = passed
duplicate_replay = passed
order_inversion_control = failed_closed
post_hoc_stitching_control = failed_closed
fake_alternative_control = failed_closed
single_branch_relabel_control = failed_closed
missing_counterfactual_retention_control = failed_closed
producer_preference_injection_control = failed_closed
random_tie_as_collapse_control = failed_closed
```

Geometric interpretation:

I5-A tests whether the I4-A four-branch collapse remains stable under
artifact reconstruction, snapshot/load replay, and duplicate runtime replay.
The duplicate replay starts from the I4-A pre-collapse snapshot, recomputes
the selected branch from the loaded pre-collapse four-branch geometry,
schedules the recomputed selected branch packet, drains the LGRC event queue,
and reproduces the collapse observables while preserving the four-branch
source-current live set and three retained counterfactual branches.

The negative controls fail closed in the multi-branch setting:

```text
order inversion cannot place collapse before branch evidence
post-hoc stitching cannot assemble four branches after observing collapse
fake alternatives cannot replace source-current branch records
a single branch cannot be relabeled as a four-branch live set
missing counterfactual retention cannot support collapse
producer preference cannot replace support-gradient dominance
random tie cannot be relabeled as collapse
```

Schema note:

```text
I5-A replay rows are replay/control records, not 80-field candidate evidence
rows. They consume the full I4-A candidate row by reference and defer full
candidate-schema revalidation to the I7 control matrix.
```

Claim boundary:

```text
I4 replaced = false
I5 replaced = false
LC4 = additive replay/control-backed multi-branch collapse candidate
LC5/LC6 = false
AP4 bridge = not supported
semantic choice = false
semantic intention = false
agency = false
native support = false
sentience = false
Phase 8 = false
ant ecology implementation = false
```

Expected artifacts:

```text
outputs/n23_multibranch_collapse_replay_and_controls.json
reports/n23_multibranch_collapse_replay_and_controls.md
scripts/build_n23_multibranch_collapse_replay_and_controls.py
```

## Iteration 6. AP4-Relevant Selection Geometry Probe

- [x] Test route/branch-conditioned source-current selection geometry.
- [x] Record AP4 dependency row-locally.
- [x] Preserve AP5 as conditional only.
- [x] Verify selected branch is geometry-conditioned, not producer-preference
      conditioned.
- [x] Verify counterfactual branches remain auditable.
- [x] Classify AP4 bridge status as candidate, blocked, or not supported.
- [x] Keep semantic choice and agency blocked.

Result:

```text
status = passed
acceptance_state = accepted_ap4_selection_geometry_lc5_candidate_pending_i7
output_digest = ff20018f3546c0567a03d840c14d2e924b9aca162ff25e74b912579c33a24422
ap4_selection_geometry_rows = 2
failed_checks = []
provisional_lc_ladder_rung = LC5
n23_closeout_rung_candidate = N23-C5
ap4_bridge_status = bridge_candidate_supported
ap4_bridge_candidate_supported = true
final_ap4_supported = false
final_n23_supported = false
ready_for_iteration_7_full_control_matrix = true
```

Rows:

```text
n23_i6_row_01_minimal_ap4_selection_geometry_bridge:
  source_variant = minimal_two_branch_replay_backed_collapse
  branch_count = 2
  retained_non_selected_branch_count = 1
  selected_branch_id = branch_edge_4_node_5
  selection_reason = support_gradient_dominance
  selected_support_gradient_score = 2.000000000000
  runner_up_branch_id = branch_edge_0_node_1
  runner_up_support_gradient_score = 1.500000000000
  score_margin = 0.500000000000
  minimum_score_margin = 0.250000000000
  ap4_bridge_status = bridge_candidate_supported
  provisional_lc_ladder_rung = LC5

n23_i6_row_02_multibranch_ap4_selection_geometry_bridge:
  source_variant = four_branch_replay_backed_collapse
  branch_count = 4
  retained_non_selected_branch_count = 3
  selected_branch_id = branch_edge_4_node_5
  selection_reason = support_gradient_dominance
  selected_support_gradient_score = 2.000000000000
  runner_up_branch_id = branch_edge_0_node_1
  runner_up_support_gradient_score = 1.500000000000
  score_margin = 0.500000000000
  minimum_score_margin = 0.250000000000
  ap4_bridge_status = bridge_candidate_supported
  provisional_lc_ladder_rung = LC5
```

Geometric interpretation:

I6 consumes the replay/control-backed I5 and I5-A rows by reference and asks
whether their selected continuation is explained by source-current branch
geometry. In both cases the selected branch is `branch_edge_4_node_5`, selected
by the frozen `support_gradient_dominance` rule:

```text
branch score =
  base_conductance(edge)
* max(source_node_coherence - center_node_coherence, 0)

selected branch score = 2.000000000000
runner-up branch score = 1.500000000000
score margin = 0.500000000000
minimum required margin = 0.250000000000
```

The minimal row shows source-current selection over one retained
counterfactual branch. The multi-branch row shows the same selection geometry
over a four-branch live set with three retained counterfactual branches. That
matters because AP4-relevant support comes from branch-conditioned geometry and
auditable alternatives, not from a selected-branch label.

AP4 bridge gates:

```text
source_current_live_branch_set = true
source_current_collapse_trace = true
counterfactual_retention = true
replay_and_controls_pass = true
route_or_branch_conditioned_source_current_reason = true
ap4_dependency_status_required_recorded = true
ap5_not_applicable_when_no_proxy_or_target = true
producer_preference_absent = true
random_tie_absent = true
n22_context_not_used_as_selection_proof = true
branch_window_order_valid = true
score_margin_valid = true
```

AP4-specific negative controls fail closed:

```text
producer_preference_as_selection_control
random_tie_as_selection_control
branch_label_only_selection_control
missing_ap4_dependency_control
n22_susceptibility_as_selection_control
semantic_choice_label_as_selection_control
missing_replay_control_backing_control
missing_counterfactual_retention_control
```

Schema note:

```text
I6 rows are AP4 bridge records by reference. They consume I4/I5 and I4-A/I5-A
source-current/replay-backed artifacts rather than creating a fresh live-branch
run. Full matrix-level revalidation remains pending I7.

row_schema_role is declared as an I6 extension field for bridge-by-reference
records. I6 artifact roles use the I2 frozen enum with artifact_subrole values
for specificity:
  replay_trace / minimal_ap4_selection_geometry_trace
  replay_trace / multibranch_ap4_selection_geometry_trace
  negative_control_trace / ap4_negative_control_trace
```

Claim boundary:

```text
LC5 = provisional AP4-relevant selection-geometry bridge candidate
LC6 = false pending I7/I8
final AP4 supported = false
semantic choice = false
semantic intention = false
agency = false
native support = false
sentience = false
Phase 8 = false
ant ecology implementation = false
```

Expected artifacts:

```text
outputs/n23_ap4_selection_geometry_probe.json
reports/n23_ap4_selection_geometry_probe.md
scripts/build_n23_ap4_selection_geometry_probe.py
```

## Iteration 6-A. AP4 Selection-Geometry Robustness Probe

- [x] Preserve I6 as the primary AP4 bridge candidate.
- [x] Run bounded source-current branch-geometry stress cases.
- [x] Include a reference four-branch stress row.
- [x] Include an eroded-margin stress row.
- [x] Include an alternate-winner stress row.
- [x] Fail closed below the predeclared score margin.
- [x] Fail closed on equalized/random-tie selection geometry.
- [x] Confirm supported stress rows duplicate-replay stable.
- [x] Keep general AP4 robustness, semantic choice, agency, and native support
      blocked.

Result:

```text
status = passed
acceptance_state = accepted_ap4_selection_geometry_robustness_stress_evidence_pending_i7
output_digest = 69541623939689724ca04c248125995f4c2ab5a5a51faf2e8e9153b62a18e0f5
i6_replaced = false
ap4_bridge_robustness_status = bounded_stress_evidence_supported
supported_stress_rows = 3
failed_closed_stress_rows = 2
general_ap4_robustness_supported = false
final_ap4_supported = false
final_n23_supported = false
ready_for_iteration_7_full_control_matrix = true
```

Stress rows:

```text
reference_four_branch_geometry:
  row_decision = supported
  selected_branch_id = branch_edge_4_node_5
  selected_score = 2.000000000000
  runner_up_branch_id = branch_edge_0_node_1
  runner_up_score = 1.500000000000
  score_margin = 0.500000000000

eroded_margin_still_supported:
  row_decision = supported
  selected_branch_id = branch_edge_4_node_5
  selected_score = 2.000000000000
  runner_up_branch_id = branch_edge_0_node_1
  runner_up_score = 1.700000000000
  score_margin = 0.300000000000

alternate_branch_wins_supported:
  row_decision = supported
  selected_branch_id = branch_edge_0_node_1
  selected_score = 2.500000000000
  runner_up_branch_id = branch_edge_4_node_5
  runner_up_score = 2.000000000000
  score_margin = 0.500000000000

below_margin_rejected:
  row_decision = rejected
  selected_branch_id = branch_edge_4_node_5
  selected_score = 2.000000000000
  runner_up_branch_id = branch_edge_0_node_1
  runner_up_score = 1.900000000000
  score_margin = 0.100000000000
  minimum_score_margin = 0.250000000000

equalized_tie_rejected:
  row_decision = rejected
  selected_branch_id = branch_edge_4_node_5
  selected_score = 2.000000000000
  runner_up_branch_id = branch_edge_0_node_1
  runner_up_score = 2.000000000000
  score_margin = 0.000000000000
  random_tie_status = random_tie
```

Geometric interpretation:

I6-A makes the AP4 candidate quality more honest. I6 showed that the selected
branch was source-current geometry-conditioned in the original minimal and
multi-branch rows. I6-A asks whether that candidate is only a fixed selected
label or whether it tracks branch geometry under bounded stress.

The result is stronger than a single-label result:

```text
reference:
  branch_edge_4_node_5 wins by margin 0.5

eroded margin:
  branch_edge_4_node_5 still wins when branch_edge_0_node_1 is strengthened,
  but margin narrows to 0.3

alternate winner:
  branch_edge_0_node_1 wins when its source-current support-gradient rises
  above branch_edge_4_node_5
```

The result is still bounded:

```text
below-margin selection fails closed at margin 0.1
equalized tie fails closed at margin 0.0
general AP4 robustness is not claimed
```

Claim boundary:

```text
I6 remains the primary AP4 bridge candidate
I6-A adds bounded robustness/stress evidence
LC5 remains provisional pending I7
LC6 = false
final AP4 supported = false
semantic choice = false
semantic intention = false
agency = false
native support = false
sentience = false
Phase 8 = false
ant ecology implementation = false
```

Schema note:

```text
I6-A row_schema_role is declared as an extension field for robustness stress
rows. I6-A artifact roles also use the I2 frozen enum with artifact_subrole
values for stress-specific snapshot, event-log, branch, collapse, replay, and
negative-control traces.
```

Expected artifacts:

```text
outputs/n23_ap4_selection_geometry_robustness_probe.json
reports/n23_ap4_selection_geometry_robustness_probe.md
scripts/build_n23_ap4_selection_geometry_robustness_probe.py
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
