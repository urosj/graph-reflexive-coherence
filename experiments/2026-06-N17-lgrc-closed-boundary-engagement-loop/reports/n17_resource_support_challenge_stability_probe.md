# N17 Iteration 7-A - Resource/Support Challenge-Stability Probe

Artifact: `n17_resource_support_challenge_stability_probe`
Status: `passed`
Acceptance state: `accepted_resource_support_challenge_stability_g5_candidate_no_final_ap7`
Output digest: `c643181eef667d0e7d8ebb65410af363bc2650403b09a11f689be394b8580728`

## Main Result

Iteration 7-A keeps the I7 route_b resource/support row fixed and tests local G5 challenge stability for the resource/support family. It does not retune route_b, does not change the I7 resource/support claim ceiling, and does not open shared-medium reciprocal closure.

```text
current_evidence_rung = G5_resource_support_challenge_stable_candidate
resource_support_family_challenge_stability_supported = true
shared_medium_extension_supported = false
full_comparative_ap7_classification_supported = false
final_ap7_supported = false
```

## Challenge Envelope

```text
attenuation_max_supported = 0.2
access_delay_max_supported_windows = 1
route_b_support_reduction_max_supported = 0.05
response_budget_margin_min_supported = 0.080134817816
support_margin_min_supported = 0.004495897432
target_band_floor_crossing_status = rejected
budget_exceedance_status = rejected
```

## Rows

| Row | Challenge | Decision | Claim Allowed | Projected Later Support |
| --- | --- | --- | --- | --- |
| `n17_i7a_row_01_route_b_resource_support_anchor_replay` | `route_b_resource_support_anchor_replay` | `supported` | `true` | `0.924495897432` |
| `n17_i7a_row_02_resource_support_attenuation_20` | `resource_support_attenuation_20` | `supported` | `true` | `0.904495897432` |
| `n17_i7a_row_03_access_path_delay_one_window` | `access_path_delay_one_window` | `supported` | `true` | `0.894495897432` |
| `n17_i7a_row_04_route_b_support_reduction_005` | `route_b_support_reduction_005` | `supported` | `true` | `0.874495897432` |
| `n17_i7a_row_05_compound_resource_support_stress` | `compound_resource_support_stress` | `supported` | `true` | `0.854495897432` |
| `n17_i7a_row_06_route_a_depletion_pressure_control` | `route_a_depletion_pressure_control` | `partial` | `false` | `0.85` |
| `n17_i7a_row_07_target_band_lower_bound_crossing_control` | `target_band_lower_bound_crossing_control` | `rejected` | `false` | `0.812594607287` |
| `n17_i7a_row_08_response_budget_exceedance_control` | `response_budget_exceedance_control` | `rejected` | `false` | `0.884495897432` |
| `n17_i7a_row_09_missing_modified_resource_feedback_control` | `missing_modified_resource_feedback_control` | `rejected` | `false` | `0.729865182184` |
| `n17_i7a_row_10_resource_label_only_relabel_control` | `resource_label_only_relabel_control` | `rejected` | `false` | `0.924495897432` |
| `n17_i7a_row_11_resource_depletion_goal_pursuit_relabel_control` | `resource_depletion_goal_pursuit_relabel_control` | `rejected` | `false` | `0.924495897432` |

## Interpretation

The supported rows show that the fixed route_b resource/support loop survives mild attenuation, one-window access delay, route_b support reduction, and their bounded compound case while preserving closure and claim boundaries. The controls fail closed for route_a depletion pressure, target-band crossing, response-budget exceedance, missing modified-resource feedback, resource label-only relabeling, and resource depletion as goal pursuit.

This supports local G5 for the resource/support family only under the recorded envelope while preserving the I7 claim ceiling. It does not support shared-medium reciprocal closure, semantic goal pursuit, intention, agency, native support, selfhood, full comparative AP7, or final AP7.

## Checks

- `fixed_i7_source_row_used`: pass
- `no_retuning_of_route_b`: pass
- `supported_local_g5_rows_present`: pass
- `controls_fail_closed`: pass
- `supported_rows_keep_trace_contract`: pass
- `challenge_envelope_recorded`: pass
- `unsafe_claim_flags_false`: pass
- `final_ap7_still_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
