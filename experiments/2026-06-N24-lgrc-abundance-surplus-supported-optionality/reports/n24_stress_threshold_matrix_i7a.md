# N24 Iteration 7-A - Alternative Stress And Threshold Matrix

Status: `passed`

Acceptance state: `accepted_alternative_higher_margin_ab5_candidate_flux_bottleneck_remains`

Output digest: `ea9893c6ec5b195f0ebd11eb20d57f92ea3eb4494495e2f45eb27b9a187f248e`

## Summary

Iteration 7-A stress-tests the I5-A/I6-A high-margin optionality variant.
It strengthens the support-budget side of the AB5 result but confirms the
flux/leakage bottleneck remains at the frozen 1e-9 bound.

```text
best_combined_per_branch_support_cost = 0.500000000000
best_combined_optional_flux_stress = 0.000000001000
best_combined_joint_count = 2
ab5_candidate_supported = true
support_axis_stronger_than_i7 = true
flux_axis_bottleneck_remains = true
```

## Interpretation

I7-A strengthens the support-budget side of N24: the alternative variant keeps two branches jointly admissible at per-branch cost 0.5, much wider than I7's 0.05. The flux axis still only passes at the frozen 1e-9 bound.

This corroborates AB5 across a higher-margin support setup but does not broaden flux robustness and does not replace I7. Reward, semantic choice, agency, native support, sentience, Phase 8, and ant ecology remain blocked.

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_passed` | `true` |
| `i4_surplus_probe_passed` | `true` |
| `i5a_optional_probe_passed` | `true` |
| `i6a_ab4_candidate_ready` | `true` |
| `original_i7_preserved` | `true` |
| `higher_margin_support_axis_mapped` | `true` |
| `flux_bottleneck_still_at_bound` | `true` |
| `ab5_supported_as_alternative_not_replacement` | `true` |
| `artifact_manifest_non_empty_and_sha_match` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
| `no_absolute_paths` | `true` |
