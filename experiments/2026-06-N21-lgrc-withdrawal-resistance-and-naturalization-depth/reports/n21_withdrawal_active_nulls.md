# N21 Iteration 3 - Active Nulls And Failure Baselines

## Summary

Status: `passed`

Acceptance state: `accepted_active_nulls_fail_closed_no_primitive_evidence`

Output digest: `154d10eb14dc54289154f28e9eb0107343f6e02939bc9905f35c30a09f041cf2`

Iteration 3 runs pre-positive active nulls only. It does not open
withdrawal-resistance or naturalization-depth evidence and assigns no
WR, ND, or N21-C ladder rungs.

## Active Null Summary

```text
row_count = 14
failed_closed_rows = 14
failed_open_rows = 0
primitive_claim_allowed_any = false
positive_primitive_evidence_opened = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
```

## Rows

| Row | Primitive | Blocker | Decision | Claim Allowed | Controls |
| --- | --- | --- | --- | --- | --- |
| `n21_i3_row_01_withdrawal_resistance_no_declared_withdrawal` | `withdrawal_resistance` | `no_withdrawal_no_removal` | `rejected` | `false` | `withdrawal_schedule_removed_control` |
| `n21_i3_row_02_withdrawal_resistance_label_only_continuation` | `withdrawal_resistance` | `label_only_continuation` | `rejected` | `false` | `label_only_success_control` |
| `n21_i3_row_03_withdrawal_resistance_proxy_only_improvement` | `withdrawal_resistance` | `proxy_only_success` | `rejected` | `false` | `proxy_only_success_control` |
| `n21_i3_row_04_withdrawal_resistance_hidden_producer_support` | `withdrawal_resistance` | `hidden_producer_support` | `rejected` | `false` | `hidden_producer_support_control, hidden_support_margin_control` |
| `n21_i3_row_05_withdrawal_resistance_post_hoc_trace_construction` | `withdrawal_resistance` | `post_hoc_trace_construction` | `rejected` | `false` | `post_hoc_trace_construction_control` |
| `n21_i3_row_06_withdrawal_resistance_support_floor_crossing` | `withdrawal_resistance` | `floor_crossing` | `rejected` | `false` | `support_floor_crossing_control` |
| `n21_i3_row_07_withdrawal_resistance_unsafe_native_support_relabel` | `withdrawal_resistance` | `producer_mediated_native_support_relabel` | `rejected` | `false` | `semantic_relabel_control, native_support_relabel_control, phase8_relabel_control` |
| `n21_i3_row_08_naturalization_depth_probe_present_only` | `naturalization_depth` | `no_probe_absence` | `rejected` | `false` | `probe_present_only_control` |
| `n21_i3_row_09_naturalization_depth_label_only_continuation` | `naturalization_depth` | `label_only_continuation` | `rejected` | `false` | `label_only_success_control` |
| `n21_i3_row_10_naturalization_depth_proxy_only_improvement` | `naturalization_depth` | `proxy_only_success` | `rejected` | `false` | `proxy_only_success_control` |
| `n21_i3_row_11_naturalization_depth_hidden_producer_support` | `naturalization_depth` | `hidden_producer_support` | `rejected` | `false` | `hidden_producer_support_control` |
| `n21_i3_row_12_naturalization_depth_post_hoc_trace_construction` | `naturalization_depth` | `post_hoc_trace_construction` | `rejected` | `false` | `post_hoc_trace_construction_control` |
| `n21_i3_row_13_naturalization_depth_probe_residue_only` | `naturalization_depth` | `probe_residue` | `rejected` | `false` | `probe_residue_control` |
| `n21_i3_row_14_naturalization_depth_support_annotation_native_support_relabel` | `naturalization_depth` | `producer_mediated_native_support_relabel` | `rejected` | `false` | `support_source_annotation_relabel_control, semantic_relabel_control, native_support_relabel_control, phase8_relabel_control` |

## Blockers Covered

```text
floor_crossing
hidden_producer_support
label_only_continuation
no_probe_absence
no_withdrawal_no_removal
post_hoc_trace_construction
probe_residue
producer_mediated_native_support_relabel
proxy_only_success
```

## Covered Controls

```text
hidden_producer_support_control
hidden_support_margin_control
label_only_success_control
native_support_relabel_control
phase8_relabel_control
post_hoc_trace_construction_control
probe_present_only_control
probe_residue_control
proxy_only_success_control
semantic_relabel_control
support_floor_crossing_control
support_source_annotation_relabel_control
withdrawal_schedule_removed_control
```

## Boundary

```text
active_nulls_only = true
primitive_evidence_opened = false
withdrawal_resistance_supported = false
naturalization_depth_supported = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_i1_inventory_passed` | `true` | {"acceptance_state": "accepted_source_contract_inventory_no_primitive_evidence", "failed_checks": [], "status": "passed"} |
| `source_i2_schema_passed` | `true` | {"acceptance_state": "accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence", "failed_checks": [], "ready_for_iteration_3_active_nulls": true, "status": "passed"} |
| `active_null_row_count_complete` | `true` | {"row_count": 14, "summary": {"active_nulls_ready_before_positive_probes": true, "blocker_classes": ["floor_crossing", "hidden_producer_support", "label_only_continuation", "no_probe_absence", "no_withdrawal_no_removal", "post_hoc_trace_construction", "probe_residue", "producer_mediated_native_support_relabel", "proxy_only_success"], "covered_controls": ["hidden_producer_support_control", "hidden_support_margin_control", "label_only_success_control", "native_support_relabel_control", "phase8_relabel_control", "post_hoc_trace_construction_control", "probe_present_only_control", "probe_residue_control", "proxy_only_success_control", "semantic_relabel_control", "support_floor_crossing_control", "support_source_annotation_relabel_control", "withdrawal_schedule_removed_control"], "failed_closed_rows": 14, "failed_open_rows": 0, "nd_ladder_rung_assigned": false, "positive_primitive_evidence_opened": false, "primitive_claim_allowed_any": false, "row_count": 14, "wr_ladder_rung_assigned": false}} |
| `candidate_evidence_fields_present_in_all_rows` | `true` | {"required_field_count": 33} |
| `active_nulls_use_same_contract_and_digest` | `true` | [{"row_id": "n21_i3_row_01_withdrawal_resistance_no_declared_withdrawal", "source_contract_row": "n20_i5_row_01_withdrawal_resistance", "source_contract_row_digest": "db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5"}, {"row_id": "n21_i3_row_02_withdrawal_resistance_label_only_continuation", "source_contract_row": "n20_i5_row_01_withdrawal_resistance", "source_contract_row_digest": "db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5"}, {"row_id": "n21_i3_row_03_withdrawal_resistance_proxy_only_improvement", "source_contract_row": "n20_i5_row_01_withdrawal_resistance", "source_contract_row_digest": "db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5"}, {"row_id": "n21_i3_row_04_withdrawal_resistance_hidden_producer_support", "source_contract_row": "n20_i5_row_01_withdrawal_resistance", "source_contract_row_digest": "db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5"}, {"row_id": "n21_i3_row_05_withdrawal_resistance_post_hoc_trace_construction", "source_contract_row": "n20_i5_row_01_withdrawal_resistance", "source_contract_row_digest": "db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5"}, {"row_id": "n21_i3_row_06_withdrawal_resistance_support_floor_crossing", "source_contract_row": "n20_i5_row_01_withdrawal_resistance", "source_contract_row_digest": "db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5"}, {"row_id": "n21_i3_row_07_withdrawal_resistance_unsafe_native_support_relabel", "source_contract_row": "n20_i5_row_01_withdrawal_resistance", "source_contract_row_digest": "db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5"}, {"row_id": "n21_i3_row_08_naturalization_depth_probe_present_only", "source_contract_row": "n20_i5_row_02_naturalization_depth", "source_contract_row_digest": "9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda"}, {"row_id": "n21_i3_row_09_naturalization_depth_label_only_continuation", "source_contract_row": "n20_i5_row_02_naturalization_depth", "source_contract_row_digest": "9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda"}, {"row_id": "n21_i3_row_10_naturalization_depth_proxy_only_improvement", "source_contract_row": "n20_i5_row_02_naturalization_depth", "source_contract_row_digest": "9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda"}, {"row_id": "n21_i3_row_11_naturalization_depth_hidden_producer_support", "source_contract_row": "n20_i5_row_02_naturalization_depth", "source_contract_row_digest": "9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda"}, {"row_id": "n21_i3_row_12_naturalization_depth_post_hoc_trace_construction", "source_contract_row": "n20_i5_row_02_naturalization_depth", "source_contract_row_digest": "9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda"}, {"row_id": "n21_i3_row_13_naturalization_depth_probe_residue_only", "source_contract_row": "n20_i5_row_02_naturalization_depth", "source_contract_row_digest": "9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda"}, {"row_id": "n21_i3_row_14_naturalization_depth_support_annotation_native_support_relabel", "source_contract_row": "n20_i5_row_02_naturalization_depth", "source_contract_row_digest": "9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda"}] |
| `active_null_comparability_complete` | `true` | all rows preserve I2 active-null comparability requirements |
| `required_i3_blockers_fail_closed` | `true` | {"present_blockers": ["floor_crossing", "hidden_producer_support", "label_only_continuation", "no_probe_absence", "no_withdrawal_no_removal", "post_hoc_trace_construction", "probe_residue", "producer_mediated_native_support_relabel", "proxy_only_success"], "required_blockers": ["hidden_producer_support", "label_only_continuation", "no_probe_absence", "no_withdrawal_no_removal", "post_hoc_trace_construction", "producer_mediated_native_support_relabel", "proxy_only_success"]} |
| `all_required_controls_covered` | `true` | {"covered_controls": ["hidden_producer_support_control", "hidden_support_margin_control", "label_only_success_control", "native_support_relabel_control", "phase8_relabel_control", "post_hoc_trace_construction_control", "probe_present_only_control", "probe_residue_control", "proxy_only_success_control", "semantic_relabel_control", "support_floor_crossing_control", "support_source_annotation_relabel_control", "withdrawal_schedule_removed_control"], "required_controls": ["hidden_producer_support_control", "hidden_support_margin_control", "label_only_success_control", "native_support_relabel_control", "phase8_relabel_control", "post_hoc_trace_construction_control", "probe_present_only_control", "probe_residue_control", "proxy_only_success_control", "semantic_relabel_control", "support_floor_crossing_control", "support_source_annotation_relabel_control", "withdrawal_schedule_removed_control"]} |
| `all_controls_fail_closed_without_failed_open` | `true` | active null controls reject the tested false-positive paths |
| `not_applicable_replay_has_scope_reason` | `true` | pre-positive null rows do not claim replay-backed rungs |
| `no_positive_primitive_evidence_or_ladder_rungs_opened` | `true` | {"nd_ladder_rung_assigned": false, "primitive_claim_allowed_any": false, "wr_ladder_rung_assigned": false} |
| `unsafe_claim_flags_all_false` | `true` | all active null rows keep unsafe claim flags false |
| `active_nulls_admit_iterations_4_and_5` | `true` | {"ready_for_iteration_4_withdrawal_probe": true, "ready_for_iteration_5_naturalization_probe": true} |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

Iteration 3 establishes pre-positive control discipline. The rows
are deliberately derived-report active nulls, so they can only
reject false-positive paths; they cannot support WR, ND, or any
stronger claim. The result admits Iterations 4 and 5 because the
no-withdrawal/no-probe-absence, label-only, proxy-only, hidden
support, post-hoc construction, probe-residue, floor-crossing,
and unsafe relabel paths all fail closed.
