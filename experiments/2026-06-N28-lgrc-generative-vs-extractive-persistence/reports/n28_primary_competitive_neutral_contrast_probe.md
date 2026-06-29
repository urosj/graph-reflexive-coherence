# N28 Iteration 4-D - Primary Competitive / Neutral Persistence Contrast Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_primary_competitive_neutral_ge3_measured_contrast_pending_replay_controls`
- Output digest: `f124a1afe8aff1a54a44157290e053d748e5545e1a9afcff1d1accbebef6c173`
- Provisional GE rung: `GE3`
- GE4 or stronger supported: `false`
- Shared policy status: `partially_supported`
- Shared policy scope: `generative_primary_i4a_i4a2_plus_extractives_i4b_i4c_i4c2_plus_primary_competitive_contrast_pending_alternative_neutral_contrast`
- Competitive promoted to generative: `false`
- Competitive promoted to extractive: `false`
- Ready for I4-E: `true`

I4-D adds the first source-current competitive/neutral measured contrast. The focal basin remains viable while neighboring capacity is redistributed across lobes rather than clearly enriched or depleted. The row sharpens the regime boundary without promoting the mixed result to generative or extractive support.

## Candidate Metrics

```text
focal_stability_preserved = true
neighbor_distinguishability_delta = 0.018
neighbor_support_delta = 0.006
neighbor_boundary_delta = -0.012
environment_capacity_delta = 0.004
focal_extraction_cost = 0.028
focal_extraction_cost_ceiling = 0.035
extractive_flattening_score = 0.024
extractive_flattening_ceiling = 0.03
merge_leakage_score = 0.019
merge_leakage_ceiling = 0.025
route_lobe_a_capacity_delta = 0.055
route_lobe_b_capacity_delta = -0.05
```

## Interpretation

Geometrically, I4-D sits between the enrichment and depletion cases. The focal eta basin remains above support, coherence, and stability floors. The surrounding eta neighbor field does not become broadly more basin-capable, and it also does not collapse into the extractive loss pattern. Instead, capacity is redistributed: route lobe A gains while route lobe B loses, leaving aggregate neighbor capacity below the material generative and extractive thresholds.

This is not failed generativity and not weak extraction. It is a separate competitive/neutral regime: focal persistence with mixed environmental exchange. One part of the environment becomes more capable while another loses capacity, and extraction, flattening, and merge/leakage remain below extractive ceilings.

In that sense I4-D can be read as a bounded processing or changing regime. The focal basin does not simply enrich its surroundings or deplete them. It reshapes the local capacity field: one adjacent region is thinned, reduced, or competitively drained while another adjacent region is strengthened. The result is environmental redistribution around a persisting basin, not net basin-forming enrichment and not broad extractive collapse.

Compactly: generative rows show focal persistence with neighbor capacity gain; extractive rows show focal persistence with neighbor capacity loss; I4-D shows focal persistence with competitive redistribution and no material aggregate gain/loss.

I4-D consumes earlier generative and extractive rows only as context for boundary separation. It does not import those outcomes as evidence, replace them, widen thresholds, or promote competitive behavior to generative support. Replay/control validation remains pending for GE4+.

The row keeps the I2-required `generative_classification_*` fields for schema compatibility, but also records `regime_classification_*` aliases because this row is a competitive measured contrast, not a generative candidate.

## Contrast Record

```text
regime_label = competitive
regime_evidence_role = measured_contrast
neighborhood_capacity_mixed_or_redistributed = true
material_generative_gain_present = false
material_extractive_loss_present = false
thresholds_retuned_to_force_competitive = false
classified_as_generative = false
classified_as_extractive = false
```

## Competitive / Neutral Boundary

```text
mechanism_class = competitive_capacity_redistribution
different_from_generative_cases = true
different_from_extractive_cases = true
competitive_redistribution_detected = true
aggregate_neighbor_capacity_not_materially_generative = true
aggregate_neighbor_capacity_not_materially_extractive = true
```

## Checks

| Check | Passed |
|---|---|
| `i3_active_nulls_passed` | `true` |
| `i4_primary_generative_candidate_consumed_for_comparison` | `true` |
| `i4a_generative_strengthening_candidate_consumed_as_context` | `true` |
| `i4a2_generative_mechanism_diversity_candidate_consumed_as_context` | `true` |
| `i4b_primary_extractive_contrast_consumed_for_comparison` | `true` |
| `i4c_extractive_strengthening_contrast_consumed_as_context` | `true` |
| `i4c2_extractive_mechanism_diversity_contrast_consumed_as_context` | `true` |
| `artifact_manifest_valid` | `true` |
| `artifact_role_alias_map_present` | `true` |
| `required_evidence_fields_present` | `true` |
| `core_digest_matches_payload` | `true` |
| `focal_stability_preserved` | `true` |
| `neighborhood_capacity_mixed_not_materially_generative_or_extractive` | `true` |
| `competitive_redistribution_present` | `true` |
| `extraction_flattening_merge_leakage_below_extractive_ceiling` | `true` |
| `classification_policy_declared_before_use` | `true` |
| `no_policy_retuning_label_threshold_or_post_hoc_boundary` | `true` |
| `false_positive_controls_not_triggered` | `true` |
| `i3_active_null_reference_bounded` | `true` |
| `shared_policy_status_bounded_to_primary_competitive_neutral` | `true` |
| `competitive_neutral_boundary_not_threshold_gap_or_label_only` | `true` |
| `competitive_contrast_not_promoted_to_generative_or_extractive` | `true` |
| `n27_context_not_consumed_as_n28_evidence` | `true` |
| `medium_debt_and_producer_residue_not_success` | `true` |
| `ge4_and_stronger_blocked_pending_replay_controls` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

I4-D does not support GE4+, GE5+, GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, or ant ecology.
