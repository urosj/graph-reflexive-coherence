# N17 Iteration 8-A - Shared-Medium Reverse-Perspective Probe

Artifact: `n17_shared_medium_reverse_perspective_probe`
Status: `passed`
Acceptance state: `accepted_alternate_source_shared_medium_g6_candidate_b4c5_reverse_blocked_no_final_ap7`
Output digest: `b2e03d7fb8cf70bcf7b8b6e0cf36114651e8faecbf67fdeca6f3ff8875f239d0`

## Main Result

Iteration 8-A separates two questions. B4/C5 reverse-perspective replay from N16 alone remains blocked because N16 explicitly deferred it. However, N07 Iterations 11-B and 12 supply an alternate artifact-only dual-basin bounded-exchange setup where both basin supports survive, separability remains above floor, nonzero leakage is bounded, controls replay, and budget remains exact.

```text
alternate_source_shared_medium_g6_candidate_supported = true
alternate_source_reverse_side_survival_supported = true
b4_c5_reverse_perspective_replay_supported = false
general_shared_medium_g6_supported = false
symmetric_shared_medium_replay_supported = false
final_ap7_supported = false
```

## Alternate Shared-Medium Envelope

```text
A_support_retention_min_supported = 0.9731535762447039
B_support_retention_min_supported = 0.9753907782243119
support_survival_threshold = 0.85
basin_separability_min_supported = 0.9731535762447039
basin_separability_floor = 0.9
wrong_basin_leakage_max_supported = 0.07457339932026706
wrong_basin_leakage_threshold = 0.1
destructive_interference_max_supported = 0.02684642375529611
destructive_interference_threshold = 0.15
bounded_exchange_max_supported = 0.07457339932026706
exchange_cap = 0.075
post_transient_wrong_basin_slope = 0.0008716360195236764
budget_error_level = 0.0
```

## Margins

```text
A_support_margin = 0.123153576245
B_support_margin = 0.125390778224
basin_separability_margin = 0.073153576245
wrong_basin_leakage_margin_to_threshold = 0.02542660068
destructive_interference_margin_to_threshold = 0.123153576245
exchange_margin_to_cap = 0.00042660068
```

## Rows

| Row | Probe | Decision | Claim Allowed |
| --- | --- | --- | --- |
| `n17_i8a_row_01_n07_dual_basin_alternate_shared_medium_candidate` | `n07_dual_basin_alternate_shared_medium_candidate` | `supported` | `true` |
| `n17_i8a_row_02_n07_reverse_side_survival_candidate` | `n07_reverse_side_survival_candidate` | `supported` | `true` |
| `n17_i8a_row_03_b4_c5_reverse_perspective_from_n16_only_control` | `b4_c5_reverse_perspective_from_n16_only_control` | `blocked` | `false` |
| `n17_i8a_row_04_general_g6_from_i8_only_relabel_control` | `general_g6_from_i8_only_relabel_control` | `rejected` | `false` |
| `n17_i8a_row_05_zero_leakage_requirement_misframed_control` | `zero_leakage_requirement_misframed_control` | `rejected` | `false` |
| `n17_i8a_row_06_reservoir_absorption_missing_control` | `reservoir_absorption_missing_control` | `rejected` | `false` |
| `n17_i8a_row_07_hidden_reservoir_routing_control` | `hidden_reservoir_routing_control` | `rejected` | `false` |
| `n17_i8a_row_08_asymmetric_absorber_preference_control` | `asymmetric_absorber_preference_control` | `rejected` | `false` |
| `n17_i8a_row_09_support_destroyed_by_allowed_exchange_control` | `support_destroyed_by_allowed_exchange_control` | `rejected` | `false` |
| `n17_i8a_row_10_budget_discontinuity_after_absorption_control` | `budget_discontinuity_after_absorption_control` | `rejected` | `false` |
| `n17_i8a_row_11_native_identity_relabel_control` | `native_identity_relabel_control` | `rejected` | `false` |

## Interpretation

8-A improves the I8 state from single-source local B4/C5 evidence to multi-source artifact-level shared-medium evidence. The improvement comes from N07's alternate dual-basin bounded exchange, not from pretending B4/C5 had reverse replay. The clean I9 role is therefore multi-source artifact-level shared-medium G6 candidate evidence while B4/C5 reverse replay, general G6 robustness, symmetric/native multi-basin claims, and final AP7 remain blocked.

## Checks

- `i8_local_one_sided_limit_preserved`: pass
- `n16_b4_c5_reverse_perspective_deferred_recorded`: pass
- `n07_artifact_only_replay_passed`: pass
- `alternate_source_supported_rows_present`: pass
- `reverse_b4_c5_and_general_g6_remain_blocked`: pass
- `controls_fail_closed`: pass
- `unsafe_claim_flags_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
