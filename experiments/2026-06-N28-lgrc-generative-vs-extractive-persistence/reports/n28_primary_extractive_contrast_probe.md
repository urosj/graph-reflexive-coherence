# N28 Iteration 4-B - Primary Extractive Persistence Contrast Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_primary_extractive_ge3_measured_contrast_pending_replay_controls`
- Output digest: `5015b7f5a148db75c7513b8fa8f249d1ac1fb0fc5fe4c6150d28d4ae644f84d3`
- Provisional GE rung: `GE3`
- GE4 or stronger supported: `false`
- Shared policy status: `partially_supported`
- Shared policy scope: `generative_primary_and_strengthening_plus_primary_extractive_contrast_pending_alternative_extractive_and_neutral_contrasts`
- Promoted to generative: `false`
- Ready for I4-C: `true`

I4-B adds the first source-current extractive measured contrast. The focal basin remains stable, but neighboring capacity degrades and the degradation is explained by exposed extraction, flattening, and merge/leakage. The row is valid contrast evidence, not generative evidence.

## Candidate Metrics

```text
focal_stability_preserved = true
neighbor_distinguishability_delta = -0.077
neighbor_support_delta = -0.063
neighbor_boundary_delta = -0.081
environment_capacity_delta = -0.069
focal_extraction_cost = 0.046
focal_extraction_cost_ceiling = 0.035
extractive_flattening_score = 0.041
extractive_flattening_ceiling = 0.03
merge_leakage_score = 0.033
merge_leakage_ceiling = 0.025
```

## Interpretation

Geometrically, I4-B is the first measured contrast against the I4/I4-A generative pattern. The focal gamma basin stays above support, coherence, and stability floors, but the adjacent gamma shell loses distinguishability, support, boundary integrity, and basin-forming capacity. The focal basin persists by drawing down or flattening the neighboring geometry, rather than co-preserving it.

The geometric difference is the direction of capacity change around a stable focal basin. In the generative cases, I4 and I4-A, the focal basin stays stable while the neighbor shell becomes more basin-capable and extraction/flattening/merge-leakage stay low. Nearby geometry gains distinguishability, support, boundary integrity, and basin-forming capacity. In the extractive case, I4-B, the focal basin also stays stable, but the neighbor shell becomes less basin-capable while extraction, flattening, and merge/leakage rise above generative ceilings. The focal basin's persistence is therefore coupled to neighbor capacity loss.

Compactly: generative means focal persistence with neighbor capacity gain; extractive means focal persistence with neighbor capacity loss.

Topology-wise, this is not a failed I4-A and not a new-basin birth row. It is a third local basin/shell configuration, gamma, where the focal basin remains viable while the neighboring shell becomes less capable of distinct basin-like organization. That makes it extractive persistence: focal continuation with neighbor capacity degradation.

I4-B consumes I4 and I4-A only as generative context for the contrast. It does not replace them, retune thresholds, or promote extractive behavior to generative support. Replay/control validation remains pending for GE4+.

The row keeps the I2-required `generative_classification_*` fields for schema compatibility, but also records `regime_classification_*` aliases because this row is an extractive measured contrast, not a generative candidate.

## Contrast Record

```text
regime_label = extractive
regime_evidence_role = measured_contrast
neighborhood_capacity_degrades = true
extractive_mechanism_present = true
thresholds_retuned_to_force_extractive = false
classified_as_generative = false
```

## Checks

| Check | Passed |
|---|---|
| `i3_active_nulls_passed` | `true` |
| `i4_primary_generative_candidate_consumed_for_comparison` | `true` |
| `i4a_generative_strengthening_candidate_consumed_as_context` | `true` |
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
| `shared_policy_status_bounded_to_primary_extractive_contrast` | `true` |
| `extractive_contrast_not_promoted_to_generative` | `true` |
| `n27_context_not_consumed_as_n28_evidence` | `true` |
| `medium_debt_and_producer_residue_not_success` | `true` |
| `ge4_and_stronger_blocked_pending_replay_controls` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

I4-B does not support GE4+, GE5+, GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, or ant ecology.
