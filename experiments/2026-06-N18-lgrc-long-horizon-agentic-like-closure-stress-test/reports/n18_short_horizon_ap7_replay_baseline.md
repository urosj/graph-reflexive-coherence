# N18 Iteration 3 - Short-Horizon AP7 Replay Baseline

## Summary

```text
status = passed
acceptance_state = accepted_short_horizon_ap7_replay_baseline_no_ap8
highest_positive_stress_ladder_rung = L1
row_count = 10
baseline_ap7_replay_supported = true
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
long_horizon_continuity_tested = false
output_digest = 9a7a01ed47991bd8ca631d36fa427c8365dc9ae7324c6984c8fc41b5e37aa7fe
```

## Row Results

| Row | Rung | Dimension | Decision | AP8 Allowed |
| --- | --- | --- | --- | --- |
| n18_i3_row_01_n17_ap7_short_horizon_replay_baseline | L1 | baseline_ap7_replay | supported | false |
| n18_i3_row_02_baseline_ap7_as_ap8_relabel_control | L1 | baseline_ap7_replay | rejected | false |
| n18_i3_row_03_stale_state_replay_control | L6 | stale_state_control | rejected | false |
| n18_i3_row_04_stale_support_state_control | L6 | stale_support_state_control | rejected | false |
| n18_i3_row_05_stale_memory_context_control | L6 | stale_memory_context_control | rejected | false |
| n18_i3_row_06_stale_selection_context_control | L6 | stale_selection_context_control | rejected | false |
| n18_i3_row_07_stale_proxy_target_control | L6 | stale_proxy_target_control | rejected | false |
| n18_i3_row_08_stale_boundary_state_control | L6 | stale_boundary_state_control | rejected | false |
| n18_i3_row_09_stale_loop_feedback_control | L6 | stale_loop_feedback_control | rejected | false |
| n18_i3_row_10_hidden_native_support_relabel_control | L1 | baseline_ap7_replay | rejected | false |

## Interpretation

Iteration 3 confirms that the N17 AP7 stack can be replayed at the
short baseline horizon as source-current artifact evidence. This is
an active null for N18: AP7 replay remains valid, but it is not
long-horizon AP8 evidence.

The positive row is only `L1`. The `L6` rows are controls, not
positive ladder progress. They show stale whole-state and stale
single-axis variants fail closed instead of becoming AP8 continuity.

The baseline row keeps support, memory, regulation, selection, proxy,
boundary, and closed-loop feedback traces present and source-current
only at the N17 closeout horizon. It records
`long_horizon_continuity_evidence = false`, so Iteration 4 remains
the first possible positive AP8 evidence point.

## Review Follow-Up

Post-review cleanup keeps `ap8_outcome_classification` aligned with
the Iteration 2 taxonomy by using `AP8_blocked` for AP8 outcome
classification, while row-specific diagnostic detail is recorded in
`ap8_outcome_detail`. Row 02 uses only schema-defined controls;
the baseline-as-AP8 rejection is represented by the row ID, decision,
gates, and outcome detail. Stale single-axis rows mark only the
links touching the stale trace as non-source-current.

## Claim Boundary

This artifact supports only a short-horizon AP7 replay baseline. It
does not support AP8, agency, semantic action/perception, semantic
goal ownership, identity acceptance, native support, Phase 8, organism
or life claims, or unrestricted autonomy.

## Checks

| Check | Passed |
| --- | --- |
| required_source_rows_selected | true |
| baseline_row_supported_at_l1 | true |
| baseline_trace_axes_source_current | true |
| baseline_ap7_replay_not_promoted_to_ap8 | true |
| stale_controls_fail_closed | true |
| hidden_native_support_relabel_fails_closed | true |
| all_rows_keep_ap8_false | true |
| unsafe_claim_flags_false | true |
| source_digest_matches_n18_i1_row_01_n17_closeout_ap7 | true |
| source_digest_matches_n18_i1_row_02_n17_requirements_matrix | true |
| source_digest_matches_n18_i1_row_03_n17_replay_control_matrix | true |
| source_digest_matches_n18_i1_row_04_n17_claim_boundary_record | true |
| source_digest_matches_n18_i1_row_05_n16_closeout_ap6 | true |
| source_digest_matches_n18_i1_row_06_n15_closeout_ap5 | true |
| source_digest_matches_n18_i1_row_07_n14_closeout_ap4 | true |
| source_digest_matches_n18_i1_row_08_n13_closeout_ap3 | true |
| source_digest_matches_n18_i1_row_11_n08_memory_closeout | true |
| source_digest_matches_n18_i1_row_12_n09_regulation_closeout | true |
| no_absolute_paths | true |
