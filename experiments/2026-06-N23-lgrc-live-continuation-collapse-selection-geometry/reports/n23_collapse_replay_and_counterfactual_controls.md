# N23 Iteration 5 - Collapse Replay And Counterfactual Controls

Status: `passed`

Acceptance state: `accepted_collapse_replay_controls_lc4_candidate_pending_i6_i7`

Output digest: `cf4be49967d53453a71659e9a1db182f41d63db78a1d88ea4fcc9206646114b7`

## Summary

Iteration 5 replays the I4 minimal live-branch collapse artifact and runs local counterfactual controls. The result is a provisional LC4 candidate only; AP4 bridge support and final N23 closeout remain pending.

## Geometric Interpretation

Artifact replay rehashes every I4 runtime/branch/collapse artifact. Snapshot/load replay reloads the saved pre/post LGRC9V3 states and confirms the recorded basin signatures. Duplicate replay starts from the I4 pre-collapse snapshot, recomputes the selected branch from the loaded branch geometry, schedules the recomputed selected branch packet, and reproduces the collapse observables.

Order inversion, post-hoc stitching, fake alternatives, single-branch relabeling, missing counterfactual retention, producer preference, and random-tie relabels all fail closed through constructed negative-control evaluation. They reject false collapse narratives without becoming positive evidence.

## Replay Rows

| Row | Source | Rung | Artifact | Snapshot | Duplicate | Failed-Closed Controls | Claim Allowed |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| `n23_i5_row_01_i4_minimal_collapse_replay_controls` | `n23_i4_row_01_minimal_live_branch_collapse_probe` | `LC4` | `passed` | `passed` | `passed` | 7 | `false` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_inventory_passed` | `true` | "accepted_source_handoff_inventory_no_live_continuation_evidence" |
| `i2_schema_passed` | `true` | "accepted_live_continuation_schema_frozen_no_positive_evidence" |
| `i3_active_nulls_passed` | `true` | "accepted_active_nulls_fail_closed_no_positive_evidence" |
| `i4_minimal_probe_passed` | `true` | "accepted_minimal_source_current_lc3_candidate_pending_replay_controls" |
| `single_i4_candidate_consumed` | `true` | 1 |
| `artifact_manifest_non_empty` | `true` | 6 |
| `artifact_hashes_match` | `true` | [{"artifact_role": "replay_trace", "path": "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_collapse_replay_... |
| `artifact_paths_repository_relative` | `true` | [{"artifact_role": "replay_trace", "path": "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_collapse_replay_... |
| `artifact_replay_passed` | `true` | "a2caaa423b6770d05619410eb2cf5bd82c458dc0f4a4162b04818e98a8b9e26f" |
| `snapshot_load_replay_passed` | `true` | "2c4523bea12a875044356841e21d0c242595f2da75758683f353b992badc0c9a" |
| `duplicate_replay_passed` | `true` | "474e749aca6ff1ea233f9d1466810c102069b3e79d9450138f4221b789912d5d" |
| `all_required_lc4_replays_passed` | `true` | [{"artifact_replay": "passed", "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_rung": "LC4", "repla... |
| `negative_controls_fail_closed` | `true` | [{"actual_result": {"claim_allowed": false, "scenario": {"branch_window": {"end_step": 0, "start_step": 0, "window_id": "n23_i4_branch_window"}, "c... |
| `negative_controls_are_constructed_evaluations` | `true` | [{"actual_result": {"claim_allowed": false, "scenario": {"branch_window": {"end_step": 0, "start_step": 0, "window_id": "n23_i4_branch_window"}, "c... |
| `order_inversion_control_failed_closed` | `true` | {"actual_result": {"claim_allowed": false, "scenario": {"branch_window": {"end_step": 0, "start_step": 0, "window_id": "n23_i4_branch_window"}, "co... |
| `post_hoc_stitching_control_failed_closed` | `true` | {"actual_result": {"claim_allowed": false, "scenario": {"mutated_branch_record_origin": "post_hoc_report_selection", "source_branch_record_origin":... |
| `missing_counterfactual_retention_control_failed_closed` | `true` | [{"actual_result": {"claim_allowed": false, "scenario": {"branch_window": {"end_step": 0, "start_step": 0, "window_id": "n23_i4_branch_window"}, "c... |
| `lc4_only_no_lc5_or_lc6` | `true` | [{"artifact_replay": "passed", "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_rung": "LC4", "repla... |
| `claims_still_blocked` | `true` | [{"artifact_replay": "passed", "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_rung": "LC4", "repla... |
| `unsafe_flags_all_false` | `true` | "all replay rows" |
| `replay_rows_declared_not_candidate_evidence_rows` | `true` | [{"artifact_replay": "passed", "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_rung": "LC4", "repla... |

## Claim Boundary

I5 supports only a replay/control-backed provisional LC4 candidate. It does not support LC5, LC6, AP4 bridge closeout, semantic choice, agency, native support, sentience, Phase 8, or ant-ecology implementation.

I5 keeps `live_continuation_collapse_claim_allowed = false` and `semantic_choice_claim_allowed = false`.
