# N21 Iteration 6 - Replay And Control Matrix

## Summary

Status: `passed`

Acceptance state: `accepted_replay_control_matrix_consumed_all_candidates_no_closeout`

Output digest: `d4b25c36f84d0300dd7a41f19cbdcfe47d771281ba9a25fbac30b16d346b941f`

Iteration 6 consumes every provisional WR/ND candidate family and asks
whether replay, artifact admissibility, and fail-closed controls demote
or preserve each candidate for closeout.

```text
candidate_row_count = 15
wr5_consumable_rows = 8
wr_floor_boundary_rows_consumed = 1
wr_rejected_boundary_rows_consumed = 3
nd3_consumable_rows = 1
nd4_consumable_rows = 2
failed_open_controls = 0
not_run_controls = 0
final_withdrawal_resistance_supported = false
final_naturalization_depth_supported = false
final_closeout_pending_iteration7 = true
```

## Consumed Rows

| Candidate | Source | Role | Decision | Source Rung | I6 Consumable Rung | Demotion |
| --- | --- | --- | --- | --- | --- | --- |
| `n21_i4_row_01_withdrawal_resistance_lgrc9v3_support_weakening` | `I4` | `i4_reference_support_weakening_wr4_row` | `supported` | `WR4` | `WR5` | `None` |
| `n21_i4a_row_amount_0_09` | `I4-A` | `i4a_positive_severity_row` | `supported` | `WR4` | `WR5` | `None` |
| `n21_i4a_row_amount_0_07` | `I4-A` | `i4a_positive_severity_row` | `supported` | `WR4` | `WR5` | `None` |
| `n21_i4a_row_amount_0_06` | `I4-A` | `i4a_floor_boundary_or_fail_closed_boundary_evidence` | `partial` | `WR3_floor_boundary_partial` | `WR3_floor_boundary_evidence` | `WR4_to_WR3_floor_boundary_evidence` |
| `n21_i4a_row_amount_0_05` | `I4-A` | `i4a_floor_boundary_or_fail_closed_boundary_evidence` | `rejected` | `None` | `None` | `WR_candidate_rejected_by_floor_or_removal_boundary` |
| `n21_i4a_row_amount_0_03` | `I4-A` | `i4a_floor_boundary_or_fail_closed_boundary_evidence` | `rejected` | `None` | `None` | `WR_candidate_rejected_by_floor_or_removal_boundary` |
| `n21_i4a_row_amount_0_00` | `I4-A` | `i4a_floor_boundary_or_fail_closed_boundary_evidence` | `rejected` | `None` | `None` | `WR_candidate_rejected_by_floor_or_removal_boundary` |
| `n21_i4b_row_reference_single_route` | `I4-B` | `i4b_transfer_schedule_shape_wr4_row` | `supported` | `WR4` | `WR5` | `None` |
| `n21_i4b_row_alternate_single_route` | `I4-B` | `i4b_transfer_schedule_shape_wr4_row` | `supported` | `WR4` | `WR5` | `None` |
| `n21_i4b_row_delayed_single_route` | `I4-B` | `i4b_transfer_schedule_shape_wr4_row` | `supported` | `WR4` | `WR5` | `None` |
| `n21_i4b_row_split_same_route` | `I4-B` | `i4b_transfer_schedule_shape_wr4_row` | `supported` | `WR4` | `WR5` | `None` |
| `n21_i4b_row_mixed_route_split` | `I4-B` | `i4b_transfer_schedule_shape_wr4_row` | `supported` | `WR4` | `WR5` | `None` |
| `n21_i5_row_01_naturalization_depth_lgrc9v3_probe_absence` | `I5` | `i5_no_probe_initial_fixture_nd3_row` | `supported` | `ND3` | `ND3_initial_fixture_no_probe_replay_candidate` | `not_promoted_beyond_ND3_initial_fixture_scope` |
| `n21_i5a_row_01_post_probe_derived_state_persistence` | `I5-A` | `i5a_post_probe_derived_static_nd3_row` | `supported` | `ND3` | `ND4` | `None` |
| `n21_i5b_row_01_eventful_post_probe_continuation` | `I5-B` | `i5b_eventful_post_probe_derived_nd3_row` | `supported` | `ND3` | `ND4` | `None` |

Note: the plan-required `final_consumable_rung` field is retained in
the JSON for compatibility, but it means I6-consumable by I7. It is
not a final N21 closeout decision.

## Status Semantics

```text
passed = positive required condition passed for the row's declared scope
failed_closed = false-positive claim path was rejected; the candidate may be retained
failed_open = false-positive claim path passed when it should not; candidate invalid
not_run = required status was not executed; dependent rung is blocked
not_applicable = control or replay mode is outside the row's declared scope
```


## Control Matrix

| Candidate | Failed Open | Not Run | Failed Closed | Passed | Not Applicable |
| --- | ---: | ---: | ---: | ---: | ---: |
| `n21_i4_row_01_withdrawal_resistance_lgrc9v3_support_weakening` | 0 | 0 | 9 | 1 | 3 |
| `n21_i4a_row_amount_0_09` | 0 | 0 | 9 | 1 | 3 |
| `n21_i4a_row_amount_0_07` | 0 | 0 | 9 | 1 | 3 |
| `n21_i4a_row_amount_0_06` | 0 | 0 | 9 | 1 | 3 |
| `n21_i4a_row_amount_0_05` | 0 | 0 | 8 | 2 | 3 |
| `n21_i4a_row_amount_0_03` | 0 | 0 | 8 | 2 | 3 |
| `n21_i4a_row_amount_0_00` | 0 | 0 | 8 | 2 | 3 |
| `n21_i4b_row_reference_single_route` | 0 | 0 | 9 | 1 | 3 |
| `n21_i4b_row_alternate_single_route` | 0 | 0 | 9 | 1 | 3 |
| `n21_i4b_row_delayed_single_route` | 0 | 0 | 9 | 1 | 3 |
| `n21_i4b_row_split_same_route` | 0 | 0 | 9 | 1 | 3 |
| `n21_i4b_row_mixed_route_split` | 0 | 0 | 9 | 1 | 3 |
| `n21_i5_row_01_naturalization_depth_lgrc9v3_probe_absence` | 0 | 0 | 9 | 2 | 2 |
| `n21_i5a_row_01_post_probe_derived_state_persistence` | 0 | 0 | 9 | 2 | 2 |
| `n21_i5b_row_01_eventful_post_probe_continuation` | 0 | 0 | 9 | 2 | 2 |

## Replay Matrix

| Candidate | Artifact | Snapshot/Load | Duplicate | Multi-Window |
| --- | --- | --- | --- | --- |
| `n21_i4_row_01_withdrawal_resistance_lgrc9v3_support_weakening` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4a_row_amount_0_09` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4a_row_amount_0_07` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4a_row_amount_0_06` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4a_row_amount_0_05` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4a_row_amount_0_03` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4a_row_amount_0_00` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4b_row_reference_single_route` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4b_row_alternate_single_route` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4b_row_delayed_single_route` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4b_row_split_same_route` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i4b_row_mixed_route_split` | `passed` | `passed` | `passed` | `not_applicable` |
| `n21_i5_row_01_naturalization_depth_lgrc9v3_probe_absence` | `passed` | `passed` | `passed` | `passed` |
| `n21_i5a_row_01_post_probe_derived_state_persistence` | `passed` | `passed` | `not_applicable` | `passed` |
| `n21_i5b_row_01_eventful_post_probe_continuation` | `passed` | `passed` | `passed` | `passed` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_artifacts_present_and_clean` | `true` | {"experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_eventful_post_probe.json": "5cdb24a076ae5a4e814a523663ad460754937f3650f3359da86d3c9f5147cec6", "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation.json": "311440952d246a6fa1748f3a215ae8d8513c4bd8c29eb0fcce346ecf76060dc2", "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe.json": "076461e9779b024e0633810be35e78359b8e36cd88bbb9ea655aa8b5c9bf7df2", "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_source_contract_inventory.json": "d7b7a37bc0781aedbe6f83c5b55ff8805bf559fe7d684c5e1d2a9be8a7cef3ee", "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_active_nulls.json": "154d10eb14dc54289154f28e9eb0107343f6e02939bc9905f35c30a09f041cf2", "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe.json": "6d80c4dd915c0c5d2b1f67c2af69881d88ab3d632acf828013389f90c53cfb36", "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_schema_and_thresholds.json": "49ec439aa4d3f2bb895dc11d8c7613a0f18f75d4f78fa38aead2282ebbf78bb7", "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_severity_boundary_probe.json": "611de6672537df3a27c5a259fe53c09f302771eaceb1d40fac4284cea08558e8", "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_transfer_shape_probe.json": "8179871ea16bd6243c46e28249c1f1e8f12246158d873763fa9ee5909cc64a1f"} |
| `required_candidate_inputs_consumed` | `true` | {"i4_reference_support_weakening_wr4_row": 1, "i4a_floor_boundary_or_fail_closed_boundary_evidence": 4, "i4a_positive_severity_row": 2, "i4b_transfer_schedule_shape_wr4_row": 5, "i5_no_probe_initial_fixture_nd3_row": 1, "i5a_post_probe_derived_static_nd3_row": 1, "i5b_eventful_post_probe_derived_nd3_row": 1} |
| `per_row_required_output_fields_present` | `true` | ["candidate_id", "source_iteration", "source_output_digest", "control_statuses", "replay_statuses", "demoted_rung_if_any", "final_consumable_rung", "i6_consumable_rung", "claim_boundary_result"] |
| `control_and_replay_status_values_valid` | `true` | ["failed_closed", "not_applicable", "passed"] |
| `no_not_run_controls_or_replays` | `true` | {"all_artifact_paths_exist": true, "all_artifact_sha256_match_file_contents": true, "candidate_row_count": 15, "failed_open_controls": 0, "failed_open_replays": 0, "final_closeout_pending_iteration7": true, "final_naturalization_depth_supported": false, "final_withdrawal_resistance_supported": false, "nd3_consumable_rows": 1, "nd4_consumable_rows": 2, "nd_candidate_rows_consumed": 3, "no_absolute_paths": true, "not_run_controls": 0, "not_run_replays": 0, "ready_for_iteration7_closeout": true, "wr5_consumable_rows": 8, "wr_candidate_rows_consumed": 12, "wr_floor_boundary_rows_consumed": 1, "wr_rejected_boundary_rows_consumed": 3} |
| `no_failed_open_controls_or_replays` | `true` | {"all_artifact_paths_exist": true, "all_artifact_sha256_match_file_contents": true, "candidate_row_count": 15, "failed_open_controls": 0, "failed_open_replays": 0, "final_closeout_pending_iteration7": true, "final_naturalization_depth_supported": false, "final_withdrawal_resistance_supported": false, "nd3_consumable_rows": 1, "nd4_consumable_rows": 2, "nd_candidate_rows_consumed": 3, "no_absolute_paths": true, "not_run_controls": 0, "not_run_replays": 0, "ready_for_iteration7_closeout": true, "wr5_consumable_rows": 8, "wr_candidate_rows_consumed": 12, "wr_floor_boundary_rows_consumed": 1, "wr_rejected_boundary_rows_consumed": 3} |
| `negative_controls_fail_closed_or_pass` | `true` | ["failed_closed", "not_applicable", "passed"] |
| `all_artifact_paths_exist` | `true` | {"all_artifact_paths_exist": true, "all_artifact_sha256_match_file_contents": true, "candidate_row_count": 15, "failed_open_controls": 0, "failed_open_replays": 0, "final_closeout_pending_iteration7": true, "final_naturalization_depth_supported": false, "final_withdrawal_resistance_supported": false, "nd3_consumable_rows": 1, "nd4_consumable_rows": 2, "nd_candidate_rows_consumed": 3, "no_absolute_paths": true, "not_run_controls": 0, "not_run_replays": 0, "ready_for_iteration7_closeout": true, "wr5_consumable_rows": 8, "wr_candidate_rows_consumed": 12, "wr_floor_boundary_rows_consumed": 1, "wr_rejected_boundary_rows_consumed": 3} |
| `all_artifact_sha256_match_file_contents` | `true` | all stored artifact SHA-256 values were computed from current file contents |
| `no_absolute_paths` | `true` | {"all_artifact_paths_exist": true, "all_artifact_sha256_match_file_contents": true, "candidate_row_count": 15, "failed_open_controls": 0, "failed_open_replays": 0, "final_closeout_pending_iteration7": true, "final_naturalization_depth_supported": false, "final_withdrawal_resistance_supported": false, "nd3_consumable_rows": 1, "nd4_consumable_rows": 2, "nd_candidate_rows_consumed": 3, "no_absolute_paths": true, "not_run_controls": 0, "not_run_replays": 0, "ready_for_iteration7_closeout": true, "wr5_consumable_rows": 8, "wr_candidate_rows_consumed": 12, "wr_floor_boundary_rows_consumed": 1, "wr_rejected_boundary_rows_consumed": 3} |
| `unsafe_claim_flags_false` | `true` | all consumed row unsafe flags remain false |
| `i4b_not_consumed_as_robust_or_removal` | `true` | I4-B rows consume only as bounded control-backed WR candidates |
| `i5a_aftereffect_bound_to_geometry` | `true` | 5-A aftereffect means geometric post-probe-derived state persistence only |
| `i5b_eventful_nd_not_promoted_to_nd5` | `true` | 5-B is eventful ND4-consumable after I6 controls, not ND5 or final ND |
| `final_closeout_deferred_to_i7` | `true` | {"all_artifact_paths_exist": true, "all_artifact_sha256_match_file_contents": true, "candidate_row_count": 15, "failed_open_controls": 0, "failed_open_replays": 0, "final_closeout_pending_iteration7": true, "final_naturalization_depth_supported": false, "final_withdrawal_resistance_supported": false, "nd3_consumable_rows": 1, "nd4_consumable_rows": 2, "nd_candidate_rows_consumed": 3, "no_absolute_paths": true, "not_run_controls": 0, "not_run_replays": 0, "ready_for_iteration7_closeout": true, "wr5_consumable_rows": 8, "wr_candidate_rows_consumed": 12, "wr_floor_boundary_rows_consumed": 1, "wr_rejected_boundary_rows_consumed": 3} |

## Interpretation

I6 preserves the positive WR rows as control-backed WR5-consumable
candidates, while keeping I4-A floor and below-floor rows as boundary
or fail-closed evidence. I4-B remains bounded transfer/schedule-shape
evidence only; it does not become robust withdrawal or support-removal
resistance.

For ND, I5 remains an ND3 no-probe initial-fixture replay baseline.
The post-probe-derived rows, 5-A and 5-B, become ND4-consumable
because active probe residue, hidden support, support-annotation,
post-hoc trace, and unsafe relabel controls all fail closed or pass
within scope. They do not become ND5/ND6 or final naturalization
depth; producer debt and final closeout remain for Iteration 7.

No final WR or ND closeout is made here. I6 only produces the
controlled consumable matrix that Iteration 7 must classify.
