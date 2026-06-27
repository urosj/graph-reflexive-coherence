# N23 Iteration 5-A - Multi-Branch Collapse Replay And Controls

Status: `passed`

Acceptance state: `accepted_multibranch_collapse_replay_controls_lc4_candidate_pending_i6_i7`

Output digest: `1f2ba760cb372fb27f50380adf61ef46c1e89b770b469f3f863c3e2d1d489773`

## Summary

Iteration 5-A replays the I4-A four-branch live-set collapse row. It is additive breadth evidence and does not replace the I4/I5 minimal path.

## Geometric Interpretation

Artifact replay rehashes every I4-A runtime/branch/collapse artifact. Snapshot/load replay reloads the saved pre/post LGRC9V3 states and confirms the recorded basin signatures. Duplicate replay starts from the I4-A pre-collapse snapshot, recomputes the selected branch from the loaded four-branch geometry, schedules the recomputed selected branch packet, and reproduces the collapse observables.

The replayed live set contains four source-current branch records and three retained non-selected counterfactual branches. This strengthens breadth relative to I4/I5 without replacing them.

## Replay Rows

| Row | Source | Branches | Retained | Rung | Artifact | Snapshot | Duplicate | Claim Allowed |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| `n23_i5a_row_01_i4a_multibranch_collapse_replay_controls` | `n23_i4a_row_01_multibranch_live_set_collapse_probe` | 4 | 3 | `LC4` | `passed` | `passed` | `passed` | `false` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_inventory_passed` | `true` | "accepted_source_handoff_inventory_no_live_continuation_evidence" |
| `i2_schema_passed` | `true` | "accepted_live_continuation_schema_frozen_no_positive_evidence" |
| `i3_active_nulls_passed` | `true` | "accepted_active_nulls_fail_closed_no_positive_evidence" |
| `i4_minimal_probe_preserved` | `true` | "accepted_minimal_source_current_lc3_candidate_pending_replay_controls" |
| `i5_minimal_replay_preserved` | `true` | "accepted_collapse_replay_controls_lc4_candidate_pending_i6_i7" |
| `i4a_multibranch_probe_passed` | `true` | "accepted_multibranch_source_current_lc3_candidate_pending_i5a" |
| `single_i4a_candidate_consumed` | `true` | 1 |
| `artifact_manifest_non_empty` | `true` | 6 |
| `artifact_hashes_match` | `true` | [{"artifact_role": "replay_trace", "path": "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_multibranch_coll... |
| `artifact_paths_repository_relative` | `true` | [{"artifact_role": "replay_trace", "path": "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_multibranch_coll... |
| `artifact_replay_passed` | `true` | "e3b37c1587e2c592643de25b720336e2e71193eed84dd8db37e950070f3e4abb" |
| `snapshot_load_replay_passed` | `true` | "7ee81922f7ebe0345e550bfb9d5168d344de167fa6dc2f0a71db0b85035cdd2e" |
| `duplicate_replay_passed` | `true` | "3f65eaa1b2df31d6b8604d814ff22b1bff0298bac3abbad989bb66f5df8f5e72" |
| `all_required_lc4_replays_passed` | `true` | [{"artifact_replay": "passed", "branch_count": 4, "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_r... |
| `negative_controls_fail_closed` | `true` | [{"actual_result": {"claim_allowed": false, "scenario": {"branch_window": {"end_step": 0, "start_step": 0, "window_id": "n23_i4a_branch_window"}, "... |
| `negative_controls_are_constructed_evaluations` | `true` | [{"actual_result": {"claim_allowed": false, "scenario": {"branch_window": {"end_step": 0, "start_step": 0, "window_id": "n23_i4a_branch_window"}, "... |
| `missing_counterfactual_retention_control_failed_closed` | `true` | [{"actual_result": {"claim_allowed": false, "scenario": {"branch_window": {"end_step": 0, "start_step": 0, "window_id": "n23_i4a_branch_window"}, "... |
| `multibranch_breadth_preserved` | `true` | [{"artifact_replay": "passed", "branch_count": 4, "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_r... |
| `lc4_only_no_lc5_or_lc6` | `true` | [{"artifact_replay": "passed", "branch_count": 4, "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_r... |
| `claims_still_blocked` | `true` | [{"artifact_replay": "passed", "branch_count": 4, "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_r... |
| `unsafe_flags_all_false` | `true` | "all replay rows" |
| `replay_rows_declared_not_candidate_evidence_rows` | `true` | [{"artifact_replay": "passed", "branch_count": 4, "duplicate_replay": "passed", "negative_control_failed_closed_count": 7, "provisional_lc_ladder_r... |

## Claim Boundary

I5-A supports only an additive replay/control-backed provisional LC4 multi-branch candidate. It does not support LC5, LC6, AP4 bridge closeout, semantic choice, agency, native support, sentience, Phase 8, or ant-ecology implementation.
