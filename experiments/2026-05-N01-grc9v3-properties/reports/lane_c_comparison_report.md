# Lane C Lane A / Lane B Comparison

Status: complete.

Lane C is an analysis pass, not a runtime spark lane. It compares
`current_hybrid_signed_hessian` against opt-in
`grc9v3_column_h_assisted` on selected clean fixtures.

## Result

- comparison rows: `60`
- Lane A candidates: `25`
- Lane B candidates: `40`
- Lane A refinements: `25`
- Lane B refinements: `40`
- direct Lane B column-H proxy-branch rows: `15`
- candidate delta rows: `15`
- refinement delta rows: `15`
- degree-8 near-saturation blocked: `true`

Classification:

`lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`

## Source Slices

- `experiment_b_column_interface_cancellation`: `15` rows; `15` direct column-H proxy-branch rows.
- `experiment_c_saturation`: `20` rows; `0` direct column-H proxy-branch rows.
- `experiment_d_refinement_identity`: `25` rows; `0` direct column-H proxy-branch rows.

## Branch Attribution

| Condition | Transform | Gate reasons | Evidence label |
| --- | --- | --- | --- |
| b_column_1_near_cancellation_near_zero_seed_0 | identity | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_1_near_cancellation_near_zero_seed_0__column_permutation_312 | column_permutation_312 | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_1_near_cancellation_near_zero_seed_0__row_permutation_231 | row_permutation_231 | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_1_near_cancellation_near_zero_seed_0__row_column_transpose | row_column_transpose | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_1_near_cancellation_near_zero_seed_0__degree_preserving_random_relabel | degree_preserving_random_relabel | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_2_near_cancellation_near_zero_seed_0 | identity | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_2_near_cancellation_near_zero_seed_0__column_permutation_312 | column_permutation_312 | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_2_near_cancellation_near_zero_seed_0__row_permutation_231 | row_permutation_231 | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_2_near_cancellation_near_zero_seed_0__row_column_transpose | row_column_transpose | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_2_near_cancellation_near_zero_seed_0__degree_preserving_random_relabel | degree_preserving_random_relabel | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_3_near_cancellation_near_zero_seed_0 | identity | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_3_near_cancellation_near_zero_seed_0__column_permutation_312 | column_permutation_312 | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_3_near_cancellation_near_zero_seed_0__row_permutation_231 | row_permutation_231 | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_3_near_cancellation_near_zero_seed_0__row_column_transpose | row_column_transpose | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| b_column_3_near_cancellation_near_zero_seed_0__degree_preserving_random_relabel | degree_preserving_random_relabel | `["column_h_threshold_hit"]` | `direct_runtime_proxy_branch` |
| C3_degree_9_stressed | identity | `["signed_hessian_hit"]` | `direct_runtime_non_branch_diagnostic` |
| C3_degree_9_stressed | row_permutation_231 | `["signed_hessian_hit"]` | `direct_runtime_non_branch_diagnostic` |
| C3_degree_9_stressed | column_permutation_312 | `["signed_hessian_hit"]` | `direct_runtime_non_branch_diagnostic` |
| C3_degree_9_stressed | row_column_transpose | `["signed_hessian_hit"]` | `direct_runtime_non_branch_diagnostic` |
| C3_degree_9_stressed | degree_preserving_random_relabel | `["signed_hessian_hit"]` | `direct_runtime_non_branch_diagnostic` |

## Boundaries

- Lane A column evidence remains `derived_non_gating`.
- Lane B direct evidence means direct runtime evidence that the
  column-H proxy branch fired; `H_s[b]` remains a proxy.
- Degree-8 near-saturation and virtual stubs remain blocked in Lane B v1.
- Mechanical expansion remains separate from identity acceptance.
- This is a clean fixture comparison, not landscape-general validation.
