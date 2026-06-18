# N17 Iteration 8-C - Paired-Perspective Shared-Medium Probe

Artifact: `n17_paired_perspective_shared_medium_probe`
Status: `passed`
Acceptance state: `accepted_local_paired_perspective_shared_medium_g6_candidate_no_final_ap7`
Output digest: `79072b1bede778958e94e940229f77be7ba846c064539c20a9769aa53c2ef81e`

## Main Result

Iteration 8-C constructs an explicit local paired-perspective shared-medium G6 candidate. Unlike 8-A, it does not only broaden the source base. It records basin A perspective, basin B perspective, and a joint paired row in one protocol. Unlike 8-B, it does not try to rescue the original B4_C5 row; B4_C5 reverse replay remains blocked.

```text
paired_perspective_shared_medium_g6_candidate_supported = true
local_paired_perspective_replay_supported = true
b4c5_perspective_paired_supported = false
b4c5_reverse_perspective_replay_supported = false
general_shared_medium_g6_supported = false
symmetric_shared_medium_replay_supported = false
final_ap7_supported = false
```

## Paired Envelope

```text
A_support_retention_level = 0.9731535762447039
B_support_retention_level = 0.9753907782243119
dual_basin_survival_threshold = 0.85
A_support_margin = 0.123153576245
B_support_margin = 0.125390778224
paired_support_min_margin = 0.123153576245
support_balance_delta = 0.00223720198
basin_separability_level = 0.9731535762447039
basin_separability_margin = 0.073153576245
wrong_basin_leakage_level = 0.07457339932026706
wrong_basin_leakage_margin_to_threshold = 0.02542660068
destructive_interference_level = 0.02684642375529611
bounded_exchange_level = 0.07457339932026706
exchange_margin_to_cap = 0.00042660068
budget_error_level = 0.0
```

## Rows

| Row | Probe | Decision | Claim Allowed |
| --- | --- | --- | --- |
| `n17_i8c_row_01_basin_a_perspective_shared_medium_loop` | `basin_a_perspective_shared_medium_loop` | `supported` | `true` |
| `n17_i8c_row_02_basin_b_perspective_shared_medium_loop` | `basin_b_perspective_shared_medium_loop` | `supported` | `true` |
| `n17_i8c_row_03_joint_paired_perspective_shared_medium_candidate` | `joint_paired_perspective_shared_medium_candidate` | `supported` | `true` |
| `n17_i8c_row_04_one_sided_i8_promotion_control` | `one_sided_i8_promotion_control` | `rejected` | `false` |
| `n17_i8c_row_05_b4c5_reverse_replay_reuse_control` | `b4c5_reverse_replay_reuse_control` | `blocked` | `false` |
| `n17_i8c_row_06_label_swap_as_paired_perspective_control` | `label_swap_as_paired_perspective_control` | `rejected` | `false` |
| `n17_i8c_row_07_missing_a_perspective_control` | `missing_a_perspective_control` | `rejected` | `false` |
| `n17_i8c_row_08_missing_b_perspective_control` | `missing_b_perspective_control` | `rejected` | `false` |
| `n17_i8c_row_09_hidden_reservoir_routing_control` | `hidden_reservoir_routing_control` | `rejected` | `false` |
| `n17_i8c_row_10_merge_leakage_as_reciprocity_control` | `merge_leakage_as_reciprocity_control` | `rejected` | `false` |
| `n17_i8c_row_11_asymmetric_perspective_preference_control` | `asymmetric_perspective_preference_control` | `rejected` | `false` |
| `n17_i8c_row_12_final_ap7_relabel_control` | `final_ap7_relabel_control` | `rejected` | `false` |

## Interpretation

8-C adds a cleaner local G6 basis than 8-A because the two basin perspectives are represented explicitly in the same generated artifact. The geometric read is two separable basins coupled through a neutral shared medium: A-facing and B-facing wrong-basin flux is absorbed into the medium, bounded exchange changes the medium, and later support for both basins remains conditioned by that changed medium while separability and leakage stay inside the source-backed envelope. The result remains local and artifact-level; it is not general G6, not B4_C5 reverse replay, not symmetric native multi-basin replay, and not final AP7.

## Checks

- `i8c_distinct_from_8a`: pass
- `b4c5_reverse_blocker_preserved`: pass
- `paired_perspective_rows_supported`: pass
- `paired_metrics_inside_envelope`: pass
- `one_sided_and_label_swap_controls_fail_closed`: pass
- `unsafe_claim_flags_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
