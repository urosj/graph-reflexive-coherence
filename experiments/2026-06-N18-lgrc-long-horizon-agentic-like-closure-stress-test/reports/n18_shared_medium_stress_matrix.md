# N18 Iteration 8 - Shared-Medium Stress Matrix

## Summary

```text
status = passed
acceptance_state = accepted_minimal_shared_medium_stress_matrix_h4_l5_no_ap8
highest_positive_stress_ladder_rung = L5
primary_stress_anchor = h4
max_supported_horizon = h4
minimal_shared_medium_separability_supported = true
b4c5_original_reverse_replay_relabel_blocked = true
resource_shared_medium_merge_relabel_blocked = true
current_bottleneck_axis = loop_feedback
current_bottleneck_link = boundary_to_loop_feedback
min_supported_h4_budget_headroom = 0.01
ap8_candidate_allowed = false
final_ap8_supported = false
output_digest = f2e0d7f8b8c88bb85f7bf5d588819e83043d3ff17c4bdfad306955fd8fcd9b60
```

## Row Results

| Row | Stress | Decision | Limiting Axis | Min Axis | Limiting Link | Cross-Axis | Drift | Budget Headroom |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| n18_i8_row_01_h4_minimal_shared_medium_separability_bounded | minimal_shared_medium_separability_bounded | supported | loop_feedback | 0.800 | boundary_to_loop_feedback | 0.800 | 0.099 | 0.010 |
| n18_i8_row_02_h4_shared_medium_merge_pressure_limit | shared_medium_merge_pressure_limit | partial | loop_feedback | 0.786 | boundary_to_loop_feedback | 0.786 | 0.114 | 0.010 |
| n18_i8_row_03_h4_shared_medium_budget_limit | shared_medium_budget_limit | rejected | loop_feedback | 0.800 | boundary_to_loop_feedback | 0.800 | 0.099 | -0.010 |
| n18_i8_row_04_h4_compound_shared_medium_limit | compound_shared_medium_limit | rejected | loop_feedback | 0.773 | boundary_to_loop_feedback | 0.771 | 0.128 | -0.030 |
| n18_i8_row_05_b4c5_original_reverse_replay_relabel_control | b4c5_original_reverse_replay_relabel_control | rejected | loop_feedback | 0.800 | boundary_to_loop_feedback | 0.800 | 0.099 | 0.010 |
| n18_i8_row_06_derived_paired_as_original_b4c5_relabel_control | derived_paired_as_original_b4c5_relabel_control | rejected | loop_feedback | 0.800 | boundary_to_loop_feedback | 0.800 | 0.099 | 0.010 |
| n18_i8_row_07_resource_shared_medium_merge_relabel_control | resource_shared_medium_merge_relabel_control | rejected | loop_feedback | 0.800 | boundary_to_loop_feedback | 0.800 | 0.099 | 0.010 |

## Interpretation

Iteration 8 stresses the h4/L5 environment-resource envelope
without changing the horizon or the budget policy. The only positive
row is a minimal bounded shared-medium separability row, supported
at L5 with very small remaining budget headroom.

The supported row preserves linked continuity across the full stack.
All trace axes and trace links remain source-current. The current
bottleneck remains
`loop_feedback`, specifically the `boundary_to_loop_feedback` link.
The positive row is exactly at the inclusive `0.800` floor for
`closed_loop_feedback_trace`, `boundary_to_loop_feedback`, and
cross-axis continuity, so I9 must replay the canonical numeric
values without rounding drift or threshold-policy changes.

The merge-pressure limit is partial because shared-medium pressure
breaks boundary-to-loop-feedback continuity before budget is
exhausted. The shared-medium budget row is rejected because budget
fails while trace continuity is still source-current. The compound
shared-medium row is rejected because both separability and budget
leave the envelope.

The relabel controls preserve the N17 caveat: original B4/C5 reverse
replay remains blocked, derived paired-perspective evidence cannot
backfill the original B4/C5 source, and bounded shared-medium
separability is not a resource/shared-medium merge.

I9 should classify and replay this narrow h4/L5 stress stack as-is.
It should not widen the horizon, recover h8, change the budget
policy, or promote the local shared-medium row into general
shared-medium robustness.

I8 supports only a bounded artifact-level L5 shared-medium stress
candidate under the h4 envelope. It does not support final AP8,
general shared-medium robustness, original B4/C5 reverse replay,
agency, semantic action/perception, native support, Phase 8,
organism/life claims, or unrestricted autonomy.

## Checks

| Check | Passed |
| --- | --- |
| iteration7_h4_l5_anchor_ready | true |
| minimal_shared_medium_positive_row_supported | true |
| shared_medium_limits_fail_closed | true |
| shared_medium_relabels_and_b4c5_caveat_fail_closed | true |
| supported_h4_rows_preserve_linked_stack_continuity | true |
| boundary_to_loop_feedback_bottleneck_preserved_for_iteration9 | true |
| minimal_shared_medium_budget_headroom_positive | true |
| floor_sensitivity_recorded_for_i9 | true |
| all_rows_l5_with_no_horizon_extension | true |
| all_rows_keep_ap8_false | true |
| budget_valid_gate_matches_budget_surface | true |
| supported_envelope_membership_matches_thresholds | true |
| unsafe_claim_flags_false | true |
| no_absolute_paths | true |
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
