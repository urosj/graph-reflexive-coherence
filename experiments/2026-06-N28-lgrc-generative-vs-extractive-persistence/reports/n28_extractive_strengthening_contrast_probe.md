# N28 Iteration 4-C - Extractive Strengthening Contrast Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_extractive_strengthening_ge3_measured_contrast_pending_replay_controls`
- Output digest: `013286de4bfa88838412d757a47c76b09f6f98381f71bddfa21cd1f5f70ba9d6`
- Provisional GE rung: `GE3`
- GE4 or stronger supported: `false`
- Shared policy status: `partially_supported`
- Shared policy scope: `generative_primary_and_strengthening_plus_primary_and_strengthening_extractive_contrasts_pending_neutral_contrasts`
- Promoted to generative: `false`
- I4-B strengthened, not replaced: `true`
- Ready for I4-D: `true`

I4-C adds a second source-current extractive measured contrast whose job is to strengthen I4-B. It preserves focal viability while a distinct neighboring shell loses distinguishability, support, boundary integrity, and basin-forming capacity under exposed extraction, flattening, and merge/leakage. The row is corroborating extractive contrast evidence, not generative evidence.

## Candidate Metrics

```text
focal_stability_preserved = true
neighbor_distinguishability_delta = -0.086
neighbor_support_delta = -0.07
neighbor_boundary_delta = -0.09
environment_capacity_delta = -0.078
focal_extraction_cost = 0.049
focal_extraction_cost_ceiling = 0.035
extractive_flattening_score = 0.044
extractive_flattening_ceiling = 0.03
merge_leakage_score = 0.036
merge_leakage_ceiling = 0.025
```

## Interpretation

Geometrically, I4-C repeats the I4-B extractive predicate in a distinct delta focal/shell configuration. The focal basin remains above support, coherence, and stability floors, but the neighboring shell loses basin-forming capacity more strongly or comparably on every load-bearing extractive axis. The focal basin persists through a cross-shell drain: local support and coherence stay viable inside the focal basin while neighboring distinguishability, support, boundary integrity, and environment capacity are drawn down.

This strengthens I4-B because it does not merely change labels or rerun the same trace. I4-B used the gamma shell. I4-C uses a separate delta cross-shell geometry and still lands in the same extractive regime under the same frozen policy family. The result is stronger evidence that extractive persistence is a measurable regime boundary, not a single fixture artifact.

Compactly: I4-B establishes focal persistence with neighbor capacity loss once; I4-C shows the same extractive relation again with a distinct topology/shell setup and comparable or stronger margins.

I4-C consumes I4-B only for margin comparison. It does not import I4-B as evidence, replace it, widen thresholds, or promote extractive behavior to generative support. Replay/control validation remains pending for GE4+.

The row keeps the I2-required `generative_classification_*` fields for schema compatibility, but also records `regime_classification_*` aliases because this row is an extractive measured contrast, not a generative candidate.

## Contrast Record

```text
regime_label = extractive
regime_evidence_role = measured_contrast_alternative
neighborhood_capacity_degrades = true
extractive_mechanism_present = true
strengthens_i4b = true
thresholds_retuned_to_force_extractive = false
classified_as_generative = false
```

## I4-B Comparison

- All load-bearing extractive margins comparable or stronger: `true`
- Thresholds widened relative to I4-B: `false`
- I4-B imported as evidence: `false`
- I4-B replaced: `false`

| Axis | I4-B | I4-C | Relation |
|---|---:|---:|---|
| `focal_stability` | `0.873` | `0.878` | `stronger_or_comparable` |
| `neighbor_distinguishability_loss` | `-0.077` | `-0.086` | `stronger_or_comparable` |
| `neighbor_support_loss` | `-0.063` | `-0.07` | `stronger_or_comparable` |
| `neighbor_boundary_loss` | `-0.081` | `-0.09` | `stronger_or_comparable` |
| `environment_capacity_loss` | `-0.069` | `-0.078` | `stronger_or_comparable` |
| `focal_extraction_cost` | `0.046` | `0.049` | `stronger_or_comparable` |
| `extractive_flattening` | `0.041` | `0.044` | `stronger_or_comparable` |
| `merge_leakage` | `0.033` | `0.036` | `stronger_or_comparable` |

## Checks

| Check | Passed |
|---|---|
| `i3_active_nulls_passed` | `true` |
| `i4_primary_generative_candidate_consumed_for_comparison` | `true` |
| `i4a_generative_strengthening_candidate_consumed_as_context` | `true` |
| `i4b_primary_extractive_contrast_consumed_for_comparison` | `true` |
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
| `shared_policy_status_bounded_to_extractive_strengthening` | `true` |
| `i4c_strengthens_i4b_without_replacement` | `true` |
| `extractive_contrast_not_promoted_to_generative` | `true` |
| `n27_context_not_consumed_as_n28_evidence` | `true` |
| `medium_debt_and_producer_residue_not_success` | `true` |
| `ge4_and_stronger_blocked_pending_replay_controls` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

I4-C does not support GE4+, GE5+, GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, or ant ecology.
