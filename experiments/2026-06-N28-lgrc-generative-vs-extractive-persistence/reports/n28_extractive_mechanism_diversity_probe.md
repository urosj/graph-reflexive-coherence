# N28 Iteration 4-C2 - Extractive Mechanism-Diversity Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_extractive_mechanism_diversity_ge3_measured_contrast_pending_replay_controls`
- Output digest: `cd099229fa37dcdf1c497555fd6ace7d4435035c87e58c1eec9bac6acb7e7067`
- Provisional GE rung: `GE3`
- GE4 or stronger supported: `false`
- Shared policy status: `partially_supported`
- Shared policy scope: `generative_primary_i4a_i4a2_plus_primary_strengthening_and_mechanism_diverse_extractive_contrasts_pending_neutral_contrasts`
- Promoted to generative: `false`
- Mechanism diversity supported: `true`
- Ready for I4-D: `true`

I4-C2 adds source-current extractive mechanism-diversity evidence. It does not try to be a stronger-margin copy of I4-B or I4-C. Instead, it preserves focal viability while neighboring capacity degrades under a merge/leakage-dominant boundary-flattening mechanism. The row is extractive contrast evidence, not generative evidence.

## Candidate Metrics

```text
focal_stability_preserved = true
neighbor_distinguishability_delta = -0.075
neighbor_support_delta = -0.055
neighbor_boundary_delta = -0.104
environment_capacity_delta = -0.065
focal_extraction_cost = 0.038
focal_extraction_cost_ceiling = 0.035
extractive_flattening_score = 0.048
extractive_flattening_ceiling = 0.03
merge_leakage_score = 0.043
merge_leakage_ceiling = 0.025
```

## Interpretation

Geometrically, I4-C2 repeats the extractive predicate through a different mechanism class. The focal zeta basin remains above support, coherence, and stability floors, but the neighboring shell loses distinguishability, support, boundary integrity, and basin-forming capacity as boundary flattening and merge/leakage rise above the generative ceilings.

This differs from both earlier extractive rows. I4-B used a gamma local shell drain. I4-C used a delta cross-shell directional drain. I4-C2 uses zeta boundary flattening where merge/leakage dominates. The result strengthens the extractive side by mechanism diversity, not by optimizing the same trace for larger margins.

Compactly: I4-C2 shows focal persistence with neighbor capacity loss through merge/leakage and boundary flattening, while keeping the same frozen classifier and claim boundary.

I4-C2 consumes I4-B and I4-C only as context for mechanism comparison. It does not import either row as evidence, replace them, widen thresholds, or promote extractive behavior to generative support. Replay/control validation remains pending for GE4+.

The row keeps the I2-required `generative_classification_*` fields for schema compatibility, but also records `regime_classification_*` aliases because this row is an extractive measured contrast, not a generative candidate.

## Contrast Record

```text
regime_label = extractive
regime_evidence_role = measured_contrast_alternative
neighborhood_capacity_degrades = true
extractive_mechanism_present = true
strengthens_extractives_by_mechanism_diversity = true
thresholds_retuned_to_force_extractive = false
classified_as_generative = false
```

## Mechanism Diversity

```text
mechanism_class = merge_leakage_dominant_boundary_flattening
different_from_i4b = true
different_from_i4c = true
not_margin_optimization_only = true
merge_leakage_dominant = true
boundary_flattening_dominant = true
```

## Checks

| Check | Passed |
|---|---|
| `i3_active_nulls_passed` | `true` |
| `i4_primary_generative_candidate_consumed_for_comparison` | `true` |
| `i4a_generative_strengthening_candidate_consumed_as_context` | `true` |
| `i4b_primary_extractive_contrast_consumed_for_comparison` | `true` |
| `i4c_extractive_strengthening_contrast_consumed_as_context` | `true` |
| `artifact_manifest_valid` | `true` |
| `artifact_role_alias_map_present` | `true` |
| `required_evidence_fields_present` | `true` |
| `core_digest_matches_payload` | `true` |
| `focal_stability_preserved` | `true` |
| `neighborhood_capacity_degrades` | `true` |
| `extractive_mechanism_present` | `true` |
| `classification_policy_declared_before_use` | `true` |
| `no_policy_retuning_label_threshold_or_post_hoc_boundary` | `true` |
| `false_positive_controls_not_triggered` | `true` |
| `i3_active_null_reference_bounded` | `true` |
| `shared_policy_status_bounded_to_extractive_mechanism_diversity` | `true` |
| `extractive_mechanism_diversity_not_margin_optimization_only` | `true` |
| `extractive_contrast_not_promoted_to_generative` | `true` |
| `n27_context_not_consumed_as_n28_evidence` | `true` |
| `medium_debt_and_producer_residue_not_success` | `true` |
| `ge4_and_stronger_blocked_pending_replay_controls` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

I4-C2 does not support GE4+, GE5+, GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, or ant ecology.
