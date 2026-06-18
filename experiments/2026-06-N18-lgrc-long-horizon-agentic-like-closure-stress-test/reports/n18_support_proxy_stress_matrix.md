# N18 Iteration 5 - Support And Proxy Stress Matrix

## Summary

```text
status = passed
acceptance_state = accepted_support_proxy_stress_matrix_h4_l3_no_ap8
highest_positive_stress_ladder_rung = L3
primary_stress_anchor = h4
max_supported_horizon = h4
support_withdrawal_restoration_supported = true
proxy_perturbation_supported = true
current_bottleneck_axis = loop_feedback
current_bottleneck_link = boundary_to_loop_feedback
min_supported_h4_budget_headroom = 0.24
ap8_candidate_allowed = false
final_ap8_supported = false
output_digest = ecaa439bdfc20cd416d3b9405c9ed9b04b1aa0871dfce82f27ad966fba13b352
```

## Row Results

| Row | Window | Stress | Decision | Limiting Axis | Min Axis | Cross-Axis | Drift | Budget Headroom |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| n18_i5_row_01_h4_support_withdrawal_restoration_bounded | h4 | support_withdrawal_restoration | supported | loop_feedback | 0.812 | 0.812 | 0.094 | 0.280 |
| n18_i5_row_02_h4_support_withdrawal_overdraw_limit | h4 | support_withdrawal_restoration | partial | support | 0.775 | 0.786 | 0.118 | 0.160 |
| n18_i5_row_03_h4_proxy_perturbation_bounded | h4 | proxy_perturbation | supported | loop_feedback | 0.808 | 0.808 | 0.098 | 0.240 |
| n18_i5_row_04_h4_proxy_target_band_crossing_limit | h4 | proxy_perturbation | rejected | proxy | 0.760 | 0.764 | 0.126 | 0.070 |
| n18_i5_row_05_h2_fallback_compound_support_proxy_control | h2 | h2_fallback_compound_support_proxy_control | supported | loop_feedback | 0.828 | 0.828 | 0.088 | 0.320 |
| n18_i5_row_06_hidden_native_support_relabel_control | h4 | hidden_native_support_relabel_control | rejected | loop_feedback | 0.812 | 0.812 | 0.094 | 0.280 |
| n18_i5_row_07_semantic_goal_ownership_relabel_control | h4 | semantic_goal_ownership_relabel_control | rejected | loop_feedback | 0.808 | 0.808 | 0.098 | 0.240 |

## Interpretation

Iteration 5 stresses the I4-supported `h4` L2 envelope rather than
retuning the horizon or trying to recover `h8`. The bounded support
withdrawal/restoration row and the bounded proxy perturbation row are
both supported at L3, but both remain narrow and pending replay/control
validation.

The supported h4 stress rows preserve linked continuity across the
full stack, not only local support/proxy fields. All trace axes and
all trace links remain source-current in the two supported h4 rows.
The current bottleneck is `loop_feedback`, specifically the
`boundary_to_loop_feedback` link. This is the main risk to carry into
I6 route/context reversal and memory relaxation.

The support overdraw row is partial because support and loop-feedback
floors are not preserved. The proxy target-band crossing row is
rejected because proxy continuity and loop feedback fail closed when
the target deviation exceeds the declared ceiling.

`h2` is included only as a fallback/control row. It confirms the
stress configuration itself is not intrinsically overdrawn, but it
does not widen the `h4` envelope or replace `h4` as the anchor.

The relabel controls reject hidden native support and semantic goal
ownership. Bounded restoration is not native support, and bounded
proxy perturbation is not semantic goal ownership.

I6 should use the h4/L3 support-proxy envelope as-is. It should not
widen the horizon, use h2 success to replace h4, or change the budget
policy. Route/context reversal and memory relaxation should be
interpreted against the existing loop-feedback bottleneck.

I5 supports a bounded artifact-level L3 support/proxy stress candidate
under the h4 horizon envelope. It does not support final AP8, agency,
semantic action/perception, semantic goal ownership, identity
acceptance, native support, Phase 8, organism/life claims, or
unrestricted autonomy.

## Checks

| Check | Passed |
| --- | --- |
| iteration4_h4_anchor_ready | true |
| h4_primary_anchor_used_for_positive_rows | true |
| support_withdrawal_and_proxy_positive_rows_supported | true |
| stress_limits_fail_closed | true |
| h2_is_fallback_control_not_primary_anchor | true |
| hidden_native_and_goal_ownership_relabels_fail_closed | true |
| supported_h4_rows_preserve_linked_stack_continuity | true |
| loop_feedback_bottleneck_recorded_for_iteration6 | true |
| all_rows_l3_with_no_horizon_extension | true |
| all_rows_keep_ap8_false | true |
| budget_valid_gate_matches_budget_surface | true |
| supported_envelope_membership_matches_thresholds | true |
| unsafe_claim_flags_false | true |
| no_absolute_paths | true |
| source_digest_matches_n18_i4_horizon_sweep | true |
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
