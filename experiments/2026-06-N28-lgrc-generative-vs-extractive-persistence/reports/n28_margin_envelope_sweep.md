# N28 Iteration 6-B - Margin Envelope Sweep

## Summary

- Status: `passed`
- Acceptance state: `accepted_margin_envelope_sweep_ge5_preserved_bottlenecks_identified`
- Output digest: `f91f4cb675b39e0fa87f5ebfbbb842e52129d42c2fbe7d4586bbe2bcd54c5fab`
- I6 GE5 result preserved: `true`
- I6-B new GE support opened: `false`
- GE6 supported: `false`

I6-B sweeps the multiplier of each I6 stress vector to identify current
margin bottlenecks and failure brackets. It does not retune thresholds,
mutate source rows, or open new source-current N28 evidence.

## Envelope Summary

```text
envelope_row_count = 40
current_i6_rows_preserved = 40
critical_current_margin_count = 3
narrow_current_margin_count = 9
failed_within_sweep_count = 7
```

## Critical Bottlenecks

| Row | Regime | Stress | Current Margin | Limiting Field | Max Passed | First Failed |
|---|---|---|---:|---|---:|---|
| `n28_i6b_n28_i4d_row_primary_competitive_neutral_contrast_extraction_cost_pressure` | `competitive` | `extraction_cost_pressure` | 0.002000000000 | `flattening_margin` | 1.5 | `2.0` |
| `n28_i6b_n28_i4e_row_competitive_neutral_mechanism_diversity_contrast_merge_leakage_pressure` | `neutral` | `merge_leakage_pressure` | 0.002000000000 | `merge_leakage_margin` | 1.5 | `2.0` |
| `n28_i6b_n28_i4e_row_competitive_neutral_mechanism_diversity_contrast_boundary_integrity_compression` | `neutral` | `boundary_integrity_compression` | 0.001000000000 | `outflow_lobe_margin` | 1.25 | `1.5` |

## Axis Results

| Stress ID | Axis | Critical Current Margins | Narrow Current Margins | Failed Within Sweep | Minimum Current Margin | Minimum Max Passed |
|---|---|---:|---:|---:|---:|---:|
| `focal_stability_softening` | `focal_stability` | 0 | 1 | 0 | 0.003000000000 | 3.0 |
| `neighbor_capacity_compression` | `neighbor_capacity` | 0 | 1 | 1 | 0.003000000000 | 2.5 |
| `extraction_cost_pressure` | `extraction_cost` | 1 | 2 | 2 | 0.002000000000 | 1.5 |
| `merge_leakage_pressure` | `merge_leakage` | 1 | 3 | 2 | 0.002000000000 | 1.5 |
| `boundary_integrity_compression` | `boundary_integrity` | 1 | 2 | 2 | 0.001000000000 | 1.25 |

## Recommendation

```text
generic_more_i5_i6_runs_recommended = false
higher_margin_neutral_circulation_variant_recommended = true
higher_margin_competitive_redistribution_variant_recommended = true
reason = critical current margins are localized to competitive/neutral transition rows rather than the full paired-regime matrix
```

## Interpretation

I6-B preserves the I6 GE5 result at the current multiplier, but shows where
the margin is thin. The bottlenecks are localized to competitive/neutral
transition rows rather than the whole generative/extractive matrix. That
means generic extra replay/stress rows are not the highest-value next
step. If we strengthen N28 further, the useful additions are focused
higher-margin neutral circulation and competitive redistribution source
rows, followed by replay and stress of those rows.

This remains GE5 envelope characterization only. GE6, final N28, semantic
cooperation, agency, native support, Phase 8 completion, and ant ecology
remain blocked pending claim classification and closeout.

## Checks

| Check | Passed |
|---|---|
| `i6_stress_matrix_pinned_and_passed` | `true` |
| `all_source_rows_swept` | `true` |
| `all_stress_axes_swept` | `true` |
| `current_i6_point_preserved` | `true` |
| `critical_bottlenecks_identified` | `true` |
| `failure_brackets_recorded` | `true` |
| `thresholds_not_retuned_for_sweep` | `true` |
| `source_rows_not_mutated` | `true` |
| `no_new_source_current_evidence_opened` | `true` |
| `ge5_preserved_ge6_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
