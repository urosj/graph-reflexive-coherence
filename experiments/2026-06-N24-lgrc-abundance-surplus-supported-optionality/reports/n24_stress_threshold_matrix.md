# N24 Iteration 7 - Stress And Threshold Matrix

Status: `passed`

Acceptance state: `accepted_narrow_at_bound_stress_threshold_backed_ab5_candidate`

Output digest: `03ec855cec08cc8838599b77356d9b8d132245a68eec276987b15273c663060f`

## Summary

Iteration 7 maps the stress boundary around the I6 AB4 candidate. The
result is narrow but positive: N24 reaches an at-bound AB5 candidate,
not broad abundance robustness.

## Geometric Interpretation

I7 supports a narrow, at-bound AB5 candidate. The support-budget axis can tolerate small joint branch costs, and a combined row passes when flux stress is exactly at the frozen 1e-9 bound. Stress above that bound fails closed, so this is not broad abundance robustness.

The maintenance basin has only 0.15 support/coherence margin over the floor. It can absorb small support-cost stress and even leave two branches jointly admissible under a support-budget-only view, but the margin is narrow.

The flux/leakage bound remains 1e-9. The original I5 optional set is quiet at zero drain, and one at-bound stress row remains clean. Stress above that bound fails closed, making the AB5 claim narrow.

AB5 is supported only as a narrow artifact-level threshold candidate pending I8 closeout, with reward, semantic choice, agency, native support, sentience, Phase 8, and ant ecology blocked.

## Stress Boundaries

```text
base_support_margin = 0.150000000000
base_coherence_margin = 0.150000000000
highest_stress_preserving_minimum_surplus_margin = 0.050000000000
highest_stress_preserving_floor = 0.150000000000
support_budget_can_reach_ab5_count_gate = true
any_nonzero_flux_stress_preserves_bound = true
best_combined_per_branch_support_cost = 0.050000000000
best_combined_optional_flux_stress = 0.000000001000
best_combined_joint_count = 2
ab5_blocker = none
```

## Branch Capacity Rows

| Per-branch cost | Max joint count by support budget | AB5 count gate |
| --- | --- | --- |
| `0.000000000000` | `3` | `true` |
| `0.025000000000` | `3` | `true` |
| `0.050000000000` | `2` | `true` |
| `0.075000000000` | `1` | `false` |
| `0.076000000000` | `1` | `false` |
| `0.100000000000` | `1` | `false` |

## Flux Rows

| Flux stress | Bound preserved | Classification |
| --- | --- | --- |
| `0.000000000000` | `true` | `quiet_or_at_bound` |
| `0.000000001000` | `true` | `quiet_or_at_bound` |
| `0.000000010000` | `false` | `flux_leakage_fail_closed` |
| `0.000001000000` | `false` | `flux_leakage_fail_closed` |

## Boundary

```text
provisional_ab_ladder_rung = AB5
ab4_candidate_supported = true
ab5_candidate_supported = true
ab5_or_stronger_supported = true
provisional_n24_closeout_ceiling = N24-C5
ready_for_iteration_8_closeout = true
```

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_passed` | `true` |
| `i4_surplus_probe_passed` | `true` |
| `i5_optional_probe_passed` | `true` |
| `i6_ab4_candidate_ready` | `true` |
| `surplus_margin_thresholds_mapped` | `true` |
| `optional_branch_capacity_thresholds_mapped` | `true` |
| `maintenance_floor_boundary_mapped` | `true` |
| `flux_leakage_boundary_mapped` | `true` |
| `stress_controls_fail_closed_or_scope_clean` | `true` |
| `ab5_classification_narrow_at_bound` | `true` |
| `artifact_manifest_non_empty_and_sha_match` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
| `no_absolute_paths` | `true` |
