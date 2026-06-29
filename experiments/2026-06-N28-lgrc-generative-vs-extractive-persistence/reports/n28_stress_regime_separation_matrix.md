# N28 Iteration 6 - Stress / Regime-Separation Matrix

## Summary

- Status: `passed`
- Acceptance state: `accepted_stress_variant_backed_ge5_regime_separation_candidate_pending_claim_classification`
- Output digest: `fe051d860391bdbceddc2892abd49dc117b8a5797b3802d77609b1578e1ad756`
- Provisional GE rung: `GE5`
- GE5 supported: `true`
- GE6 supported: `false`
- Shared regime policy status: `supported`

I6 stresses the I4-family rows already admitted by I5. The stress matrix
does not retune thresholds and does not mutate source rows. It applies
fixed overlays to focal stability, neighbor capacity, extraction cost,
merge/leakage, and boundary integrity, then replays the same regime
classifier.

## Stress Summary

```text
stress_variant_count = 5
stress_row_count = 40
stress_passed_row_count = 40
stress_failed_row_count = 0
rows_demoted = []
shared_policy_ids = ['n28_shared_regime_policy_v1']
thresholds_retuned_for_stress = false
source_rows_mutated = false
```

## Stress Axes

| Stress ID | Axis | Rows | Passed | Failed | Minimum Margin |
|---|---:|---:|---:|---:|---:|
| `focal_stability_softening` | `focal_stability` | 8 | 8 | 0 | 0.003000000000 |
| `neighbor_capacity_compression` | `neighbor_capacity` | 8 | 8 | 0 | 0.003000000000 |
| `extraction_cost_pressure` | `extraction_cost` | 8 | 8 | 0 | 0.002000000000 |
| `merge_leakage_pressure` | `merge_leakage` | 8 | 8 | 0 | 0.002000000000 |
| `boundary_integrity_compression` | `boundary_integrity` | 8 | 8 | 0 | 0.001000000000 |

## Regime Results

| Regime | Stress Rows | Passed | Failed | Minimum Margin |
|---|---:|---:|---:|---:|
| `competitive` | 5 | 5 | 0 | 0.002000000000 |
| `extractive` | 15 | 15 | 0 | 0.003000000000 |
| `generative` | 15 | 15 | 0 | 0.010000000000 |
| `neutral` | 5 | 5 | 0 | 0.001000000000 |

## Interpretation

I6 upgrades I5 from replay/control-backed GE4 to a provisional GE5
candidate because all generative, extractive, and competitive/neutral
rows preserve their regime labels under the declared bounded stress
overlays. The important point is not that the rows were made easier;
the same shared policy family is preserved and thresholds are not
retuned.

Geometrically, the stress matrix compresses the regime axes without
changing the regime rules: generative rows keep focal persistence while
their neighboring capacity shell remains enriched; extractive rows keep
focal persistence while the neighborhood remains depleted/flattened with
extraction present; competitive/neutral rows keep mixed redistribution
or circulation without becoming aggregate enrichment or depletion.

This remains below GE6 and final N28. I7 still has to classify AP4/AP5
dependencies and unsafe claim boundaries, and I8 still has to freeze
closeout and the N29 handoff.

## Checks

| Check | Passed |
|---|---|
| `i5_replay_matrix_pinned_and_passed` | `true` |
| `all_stress_axes_present` | `true` |
| `all_i4_family_rows_stressed` | `true` |
| `all_stress_rows_passed` | `true` |
| `single_shared_policy_family_preserved` | `true` |
| `thresholds_not_retuned_for_stress` | `true` |
| `source_rows_not_mutated` | `true` |
| `paired_regime_coverage_present` | `true` |
| `ge5_supported_ge6_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
