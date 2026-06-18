# N17 Iteration 7-B - Alternative Resource/Support G5 Probe

Artifact: `n17_alternative_resource_support_g5_probe`
Status: `passed`
Acceptance state: `accepted_alternative_resource_support_g5_setup_no_final_ap7`
Output digest: `b0f6df9ed0a79e6e93243fdfbfcc8b65d9fcc8374e6fbd1a5775871632e91f06`

## Main Result

Iteration 7-B tests an alternative low-margin resource/support setup. It is not a 7-A refinement: 7-A thresholds are not reused, and the base support source is N13 `mild_support_weakening` rather than the fixed I7 route_b row.

```text
current_evidence_rung = G5_alternative_resource_support_challenge_stable_candidate
resource_support_family_challenge_stability_supported = true
shared_medium_extension_supported = false
full_comparative_ap7_classification_supported = false
final_ap7_supported = false
```

## Alternative Setup

```text
alternative_setup_id = low_margin_route_b_resource_support_bridge
base_support_source_lane = mild_support_weakening
base_projected_support = 0.87583821862
support_floor = 0.85
support_margin_above_floor = 0.02583821862
target_band = [0.817594607287, 0.957594607287]
iteration_7a_used_as_threshold_source = false
```

## Challenge Envelope

```text
attenuation_max_supported = 0.1
access_delay_max_supported_windows = 1
route_b_support_reduction_max_supported = 0.015
compound_support_cost_max_supported = 0.02
response_budget_margin_min_supported = 0.100134817816
support_margin_min_supported = 0.00583821862
support_floor_crossing_status = rejected
target_band_floor_crossing_status = rejected
budget_exceedance_status = rejected
```

## Rows

| Row | Challenge | Decision | Claim Allowed | Projected Later Support |
| --- | --- | --- | --- | --- |
| `n17_i7b_row_01_low_margin_resource_support_anchor` | `low_margin_resource_support_anchor` | `supported` | `true` | `0.87583821862` |
| `n17_i7b_row_02_low_margin_resource_attenuation_010` | `low_margin_resource_attenuation_010` | `supported` | `true` | `0.86583821862` |
| `n17_i7b_row_03_low_margin_access_delay_one_window` | `low_margin_access_delay_one_window` | `supported` | `true` | `0.86383821862` |
| `n17_i7b_row_04_low_margin_route_b_support_reduction_015` | `low_margin_route_b_support_reduction_015` | `supported` | `true` | `0.86083821862` |
| `n17_i7b_row_05_low_margin_compound_resource_support_stress` | `low_margin_compound_resource_support_stress` | `supported` | `true` | `0.85583821862` |
| `n17_i7b_row_06_low_margin_support_floor_crossing_control` | `low_margin_support_floor_crossing_control` | `rejected` | `false` | `0.845` |
| `n17_i7b_row_07_low_margin_target_band_crossing_control` | `low_margin_target_band_crossing_control` | `rejected` | `false` | `0.812594607287` |
| `n17_i7b_row_08_low_margin_response_budget_exceedance_control` | `low_margin_response_budget_exceedance_control` | `rejected` | `false` | `0.86583821862` |
| `n17_i7b_row_09_route_a_burden_switch_control` | `route_a_burden_switch_control` | `partial` | `false` | `0.85` |
| `n17_i7b_row_10_missing_modified_resource_feedback_control` | `missing_modified_resource_feedback_control` | `rejected` | `false` | `0.729865182184` |
| `n17_i7b_row_11_resource_label_only_relabel_control` | `resource_label_only_relabel_control` | `rejected` | `false` | `0.87583821862` |
| `n17_i7b_row_12_resource_depletion_goal_pursuit_relabel_control` | `resource_depletion_goal_pursuit_relabel_control` | `rejected` | `false` | `0.87583821862` |

## Interpretation

7-B supports a second, narrower local G5 resource/support setup. The supported rows preserve closure for a low-margin support bridge under small attenuation, one-window access delay, route_b support reduction, and a bounded compound case. The controls fail closed for support-floor crossing, target-band crossing, budget exceedance, route_a burden switching, missing modified-resource feedback, resource label-only relabeling, and resource depletion as goal pursuit.

This strengthens the resource/support story by adding an alternative configuration, not by widening the 7-A envelope. It preserves the I7 claim ceiling and does not support shared-medium reciprocal closure, semantic goal pursuit, intention, agency, native support, selfhood, full comparative AP7, or final AP7.

## I9 Comparative Role

```text
resource_support_alternative_g5_probe:
  status: supported
  role: alternative low-margin configuration
  scope: narrower envelope than 7-A
  does_not_expand_7A_envelope: true
  final_ap7_supported: false

resource/support closure requirement:
  supported_by: I7, I7-A, I7-B
  strongest_envelope: I7-A
  alternative_low_margin_support: I7-B
  blocked_by: support-floor crossing, target-band crossing,
              budget exceedance, missing feedback, label-only relabel,
              goal-pursuit relabel
```

## Checks

- `alternative_setup_frozen_before_challenges`: pass
- `i7_claim_ceiling_preserved_not_fixed_row_reused`: pass
- `supported_alternative_g5_rows_present`: pass
- `controls_fail_closed`: pass
- `supported_rows_keep_trace_contract`: pass
- `challenge_envelope_recorded`: pass
- `unsafe_claim_flags_false`: pass
- `final_ap7_still_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
