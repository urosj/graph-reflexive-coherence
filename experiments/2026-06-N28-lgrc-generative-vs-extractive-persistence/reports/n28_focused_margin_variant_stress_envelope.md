# N28 Iteration 6-C - Focused Margin Variant Stress Envelope

## Summary

- Status: `passed`
- Acceptance state: `accepted_focused_margin_variants_ge5_stress_envelope_supported_pending_claim_classification`
- Output digest: `0dc3cc97695338d5f54719e993a4dd2912d5983eb03f066c3de04e027f3c06b3`
- Provisional GE rung: `GE5`
- Focused GE5 supported: `true`
- GE6 supported: `false`

I6-C stress-tests the replay-backed focused variants from I5-B using the
same I6 stress family and I6-B multiplier envelope. It is targeted at the
competitive/neutral bottlenecks identified in I6-B; it does not replace
the paired-regime I6 result, does not claim broad robustness, and does
not open GE6.

## Focused Envelope Summary

```text
stress_row_count = 10
current_stress_rows_preserved = 10
targeted_bottleneck_row_count = 3
targeted_bottleneck_improvement_count = 3
critical_current_margin_count = 0
narrow_current_margin_count = 0
minimum_current_margin = 0.005
margin_interpretation = targeted_current_multiplier_margin_improvement_not_broad_robustness
broad_margin_robustness_supported = false
order_of_magnitude_robustness_supported = false
```

## Targeted Improvements

| Row | Source | Regime | Stress | Current Margin | Limiting Field | Improved |
|---|---|---|---|---:|---|---|
| `n28_i6c_n28_i4f_row_higher_margin_neutral_circulation_contrast_merge_leakage_pressure` | `4-F` | `neutral` | `merge_leakage_pressure` | 0.007000000000 | `merge_leakage_margin` | `true` |
| `n28_i6c_n28_i4f_row_higher_margin_neutral_circulation_contrast_boundary_integrity_compression` | `4-F` | `neutral` | `boundary_integrity_compression` | 0.010000000000 | `flattening_margin` | `true` |
| `n28_i6c_n28_i4g_row_higher_margin_competitive_redistribution_contrast_extraction_cost_pressure` | `4-G` | `competitive` | `extraction_cost_pressure` | 0.007000000000 | `flattening_margin` | `true` |

## Axis Results

| Stress ID | Axis | Rows | Preserved | Critical | Narrow | Minimum Current Margin | Minimum Max Passed |
|---|---|---:|---:|---:|---:|---:|---:|
| `focal_stability_softening` | `focal_stability` | 2 | 2 | 0 | 0 | 0.008000000000 | 3.0 |
| `neighbor_capacity_compression` | `neighbor_capacity` | 2 | 2 | 0 | 0 | 0.008000000000 | 3.0 |
| `extraction_cost_pressure` | `extraction_cost` | 2 | 2 | 0 | 0 | 0.006000000000 | 2.5 |
| `merge_leakage_pressure` | `merge_leakage` | 2 | 2 | 0 | 0 | 0.005000000000 | 2.5 |
| `boundary_integrity_compression` | `boundary_integrity` | 2 | 2 | 0 | 0 | 0.008000000000 | 3.0 |

## Interpretation

I6-C shows targeted current-multiplier margin improvement for the
focused neutral circulation and competitive redistribution variants.
The result should be read as focused optimization of the weak
competitive/neutral transition rows, not as broad margin robustness.
The geometric change is not a new regime label: I4-F remains neutral
circulation and I4-G remains competitive redistribution.

The stronger evidence is narrow: their circulation, leakage, route-lobe,
and flattening margins no longer sit on the I6-B critical edge under the
current stress multiplier. The absolute normalized margins remain small
(minimum current margin 0.005), so this is not order-of-magnitude
robustness and not GE6.

This supports focused GE5 evidence for the competitive/neutral transition
region only. It does not upgrade GE6, final N28, semantic cooperation,
agency, native support, Phase 8 completion, or ant ecology.

## Checks

| Check | Passed |
|---|---|
| `i5b_replay_matrix_pinned_and_passed` | `true` |
| `i6b_bottleneck_map_pinned_and_passed` | `true` |
| `both_focused_replay_sources_consumed` | `true` |
| `all_stress_axes_applied` | `true` |
| `all_current_focused_stress_rows_preserved` | `true` |
| `targeted_bottleneck_margins_improved` | `true` |
| `no_critical_current_margins_remaining` | `true` |
| `no_narrow_current_margins_remaining` | `true` |
| `failure_brackets_recorded_where_present` | `true` |
| `thresholds_not_retuned_for_focused_sweep` | `true` |
| `source_rows_not_mutated` | `true` |
| `broad_margin_robustness_not_claimed` | `true` |
| `order_of_magnitude_robustness_not_claimed` | `true` |
| `ge5_supported_ge6_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
