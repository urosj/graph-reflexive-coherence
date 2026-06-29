# N28 Iteration 4-E - Competitive / Neutral Mechanism-Diversity Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_competitive_neutral_mechanism_diversity_ge3_measured_contrast_pending_replay_controls`
- Output digest: `d760e55481c2d84e554c5089863c725c3b57ee7da1dedbf5b919f201c3c754cd`
- Provisional GE rung: `GE3`
- GE4 or stronger supported: `false`
- Shared policy status: `partially_supported`
- Shared policy scope: `generative_primary_i4a_i4a2_plus_extractives_i4b_i4c_i4c2_plus_competitive_i4d_and_neutral_i4e_pending_replay_controls`
- Competitive promoted to generative: `false`
- Competitive promoted to extractive: `false`
- Ready for I5: `true`

I4-E adds a source-current competitive/neutral mechanism-diversity contrast. The focal basin remains viable while neighboring capacity circulates through three shell lobes rather than the direct two-lobe competitive pair used by I4-D. The row strengthens the middle regime boundary without promoting the neutral result to generative or extractive support.

## Candidate Metrics

```text
focal_stability_preserved = true
neighbor_distinguishability_delta = 0.008
neighbor_support_delta = -0.006
neighbor_boundary_delta = 0.007
environment_capacity_delta = -0.002
focal_extraction_cost = 0.027
focal_extraction_cost_ceiling = 0.035
extractive_flattening_score = 0.023
extractive_flattening_ceiling = 0.03
merge_leakage_score = 0.02
merge_leakage_ceiling = 0.025
inflow_lobe_capacity_delta = 0.047
outflow_lobe_capacity_delta = -0.045
buffer_lobe_capacity_delta = 0.002
```

## Interpretation

Geometrically, I4-E sits in the same middle regime as I4-D but uses a different mechanism. The focal theta basin remains above support, coherence, and stability floors. The surrounding theta neighbor field does not become broadly more basin-capable, and it also does not collapse into the extractive loss pattern. Instead, capacity circulates through three shell lobes: an inflow lobe gains, an outflow lobe loses, and a buffer lobe remains near stable.

This is not failed generativity and not weak extraction. It is a separate neutral processing regime: focal persistence with balanced environmental circulation. One part of the environment becomes more capable, another loses capacity, and a third carries the buffer, while aggregate neighbor capacity stays below material generative and extractive thresholds.

In that sense I4-E can be read as a bounded processing or changing regime. The focal basin does not simply enrich its surroundings or deplete them. It reshapes the local capacity field: one adjacent region is strengthened, one is reduced, and one buffers the exchange. The result is environmental circulation around a persisting basin, not net basin-forming enrichment and not broad extractive collapse.

Compactly: generative rows show focal persistence with neighbor capacity gain; extractive rows show focal persistence with neighbor capacity loss; I4-D shows focal persistence with direct competitive redistribution; I4-E shows focal persistence with neutral three-lobe capacity circulation.

I4-E consumes earlier generative, extractive, and I4-D competitive rows only as context for boundary separation. It does not import those outcomes as evidence, replace them, widen thresholds, or promote neutral circulation to generative support. Replay/control validation remains pending for GE4+.

The row keeps the I2-required `generative_classification_*` fields for schema compatibility, but also records `regime_classification_*` aliases because this row is a neutral measured contrast, not a generative candidate.

## Contrast Record

```text
regime_label = neutral
regime_evidence_role = measured_contrast_alternative
neighborhood_capacity_mixed_or_redistributed = true
material_generative_gain_present = false
material_extractive_loss_present = false
thresholds_retuned_to_force_competitive = false
thresholds_retuned_to_force_neutral = false
classified_as_generative = false
classified_as_extractive = false
classified_as_neutral = true
```

## Competitive / Neutral Mechanism Boundary

```text
mechanism_class = three_lobe_circulatory_capacity_exchange
different_from_generative_cases = true
different_from_extractive_cases = true
different_from_i4d_competitive_case = true
neutral_circulation_detected = true
direct_two_lobe_competitive_pair_used = false
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
| `i4d_primary_competitive_contrast_consumed_for_comparison` | `true` |
| `artifact_manifest_valid` | `true` |
| `artifact_role_alias_map_present` | `true` |
| `required_evidence_fields_present` | `true` |
| `core_digest_matches_payload` | `true` |
| `focal_stability_preserved` | `true` |
| `neighborhood_capacity_mixed_not_materially_generative_or_extractive` | `true` |
| `neutral_circulatory_exchange_present` | `true` |
| `extraction_flattening_merge_leakage_below_extractive_ceiling` | `true` |
| `classification_policy_declared_before_use` | `true` |
| `no_policy_retuning_label_threshold_or_post_hoc_boundary` | `true` |
| `false_positive_controls_not_triggered` | `true` |
| `i3_active_null_reference_bounded` | `true` |
| `shared_policy_status_bounded_to_competitive_neutral_mechanism_diversity` | `true` |
| `competitive_neutral_boundary_not_threshold_gap_or_label_only` | `true` |
| `competitive_neutral_mechanism_diversity_not_i4d_relabel` | `true` |
| `neutral_contrast_not_promoted_to_generative_or_extractive` | `true` |
| `n27_context_not_consumed_as_n28_evidence` | `true` |
| `medium_debt_and_producer_residue_not_success` | `true` |
| `ge4_and_stronger_blocked_pending_replay_controls` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

I4-E does not support GE4+, GE5+, GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, or ant ecology.
