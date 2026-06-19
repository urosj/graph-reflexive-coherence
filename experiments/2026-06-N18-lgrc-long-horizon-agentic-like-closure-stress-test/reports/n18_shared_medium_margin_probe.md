# N18 Iteration 8-A - Shared-Medium Margin Robustness Probe

## Summary

```text
status = passed
acceptance_state = accepted_shared_medium_margin_probe_h4_l5_no_ap8
highest_positive_stress_ladder_rung = L5
primary_stress_anchor = h4
max_supported_horizon = h4
margin_candidate_supported = true
b4c5_original_reverse_replay_relabel_blocked = true
resource_shared_medium_merge_relabel_blocked = true
current_bottleneck_axis = loop_feedback
current_bottleneck_link = boundary_to_loop_feedback
min_supported_h4_budget_headroom = 0.06
min_supported_h4_continuity_margin = 0.022
ap8_candidate_allowed = false
final_ap8_supported = false
output_digest = 997bbcfa45c10cfd3a51fa61553a7df56337aa60b969c231a90848cca7723c0b
```

## Row Results

| Row | Stress | Decision | Limiting Axis | Min Axis | Limiting Link | Cross-Axis | Drift | Budget Headroom |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| n18_i8a_row_01_h4_shared_medium_margin_candidate | alternative_shared_medium_margin_candidate | supported | loop_feedback | 0.822 | boundary_to_loop_feedback | 0.823 | 0.078 | 0.060 |
| n18_i8a_row_02_h4_shared_medium_margin_pressure_limit | alternative_shared_medium_merge_pressure_limit | partial | loop_feedback | 0.793 | boundary_to_loop_feedback | 0.793 | 0.109 | 0.060 |
| n18_i8a_row_03_h4_hidden_budget_relief_control | hidden_budget_relief_control | rejected | loop_feedback | 0.822 | boundary_to_loop_feedback | 0.823 | 0.078 | -0.010 |
| n18_i8a_row_04_h4_threshold_relaxation_control | threshold_relaxation_control | rejected | loop_feedback | 0.792 | boundary_to_loop_feedback | 0.792 | 0.088 | 0.060 |
| n18_i8a_row_05_h4_horizon_shortening_control | horizon_shortening_control | rejected | loop_feedback | 0.822 | boundary_to_loop_feedback | 0.823 | 0.078 | 0.060 |
| n18_i8a_row_06_dropped_boundary_to_loop_feedback_control | dropped_boundary_to_loop_feedback_control | rejected | loop_feedback | 0.822 | boundary_to_loop_feedback | 0.823 | 0.078 | 0.060 |
| n18_i8a_row_07_merge_as_success_control | merge_as_success_control | rejected | loop_feedback | 0.822 | boundary_to_loop_feedback | 0.823 | 0.078 | 0.060 |
| n18_i8a_row_08_b4c5_backfill_relabel_control | b4c5_backfill_relabel_control | rejected | loop_feedback | 0.822 | boundary_to_loop_feedback | 0.823 | 0.078 | 0.060 |

## Interpretation

Iteration 8-A consumes the I8 h4/L5 shared-medium result and
adds an alternative margin probe without changing the horizon,
stress ladder, threshold policy, budget ceiling, or claim boundary.

The positive row is additional evidence, not a replacement for I8.
It preserves the same shared-medium perturbation size as the I8
minimal row while recording higher continuity and budget margin:
budget headroom is 0.06 and the minimum continuity margin is 0.022.

The active bottleneck is still `loop_feedback`, specifically the
`boundary_to_loop_feedback` link. That is intentional: I8-A
strengthens the margin while preserving the same limiting link.

Controls fail closed. Hidden budget relief, threshold relaxation,
horizon shortening, dropped boundary-to-loop feedback, merge as
success, and original B4/C5 backfill are all rejected. Merge
pressure remains a partial limit rather than positive evidence.

I9 should classify I8 and I8-A together as narrow shared-medium
evidence: I8 is the honest minimal edge case, and I8-A is an
additional higher-margin source-backed variant. Neither row opens
AP8 by itself.

I8-A does not support final AP8, general shared-medium robustness,
original B4/C5 reverse replay, agency, semantic action/perception,
native support, Phase 8, organism/life claims, or unrestricted
autonomy.

## Checks

| Check | Passed |
| --- | --- |
| iteration8_minimal_shared_medium_anchor_ready | true |
| margin_shared_medium_positive_row_supported | true |
| margin_candidate_has_positive_budget_and_continuity_margin | true |
| margin_probe_fail_closed_controls | true |
| merge_pressure_limit_remains_partial | true |
| b4c5_caveat_and_i8_role_preserved | true |
| supported_h4_rows_preserve_linked_stack_continuity | true |
| boundary_to_loop_feedback_bottleneck_preserved_for_iteration9 | true |
| same_horizon_budget_threshold_policy_preserved | true |
| all_rows_l5_with_no_horizon_extension | true |
| all_rows_keep_ap8_false | true |
| budget_valid_gate_matches_budget_surface | true |
| supported_envelope_membership_matches_thresholds | true |
| unsafe_claim_flags_false | true |
| no_absolute_paths | true |
| source_digest_matches_n18_i8_shared_medium | true |
| source_digest_matches_n18_i7_environment_resource | true |
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
