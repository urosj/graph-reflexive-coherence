# N28 Iteration 4-A - Generative Strengthening Candidate Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_generative_strengthening_ge3_candidate_pending_replay_controls`
- Output digest: `07f15756b0584cbc91e4b765e4e96a07de0e62a772e0b0a49f1723f83d68b85c`
- Provisional GE rung: `GE3`
- GE4 or stronger supported: `false`
- Shared policy status: `partially_supported`
- Shared policy scope: `strengthened_by_primary_and_i4a_pending_extractives_and_neutral_contrasts`
- I4 strengthened, not replaced: `true`
- Ready for I4-B: `true`

I4-A strengthens the I4 generative evidence by producing a distinct source-current GE3 generative row under the same frozen policy family. It does not replace I4 and does not retune thresholds.

## Candidate Metrics

```text
focal_stability_preserved = true
neighbor_distinguishability_delta = 0.154
neighbor_support_delta = 0.087
neighbor_boundary_delta = 0.145
environment_capacity_delta = 0.134
merge_leakage_score = 0.011
merge_leakage_ceiling = 0.025
```

## Interpretation

The row passes the three-axis I2 classifier locally and compares against I4 on every load-bearing margin. Focal stability, neighbor distinguishability, neighbor support, neighbor boundary integrity, and environment capacity are comparable or stronger than I4, while extraction, flattening, and merge/leakage are lower or equal. This corroborates I4 as a generative pattern, but still does not support final generative persistence or shared-policy closeout.

In geometric dynamics terms, I4-A shows the same kind of persistence with neighboring capacity increase in a distinct local setup. The focal basin remains viable while the adjacent shell gains separation, support, boundary integrity, and basin-forming capacity without being drained, flattened, or merged into the focal basin.

Topology-wise, I4 is the primary alpha case: focal basin alpha remains stable while neighbor capacity shell alpha becomes more basin-capable and extraction/flattening/merge-leakage stay low. I4-A repeats the same kind of event in a distinct beta setup: focal basin beta remains stable while neighbor capacity shell beta becomes more basin-capable, again without absorption, drainage, or merge/leakage masquerading as support.

The topology difference is not new basin birth and not a replay-backed topology transition. It is a different local basin/shell configuration: different focal basin id, different neighbor shell id, different runtime fixture digest, and a stronger capacity margin profile.

The `shared_regime_policy_status = partially_supported` field is scoped to the primary I4 row plus this I4-A strengthening row. It does not settle the shared policy family until extractive contrasts and competitive/neutral contrasts exist.

I4-A inherits the I3 active-null matrix as a fail-closed false-positive boundary and consumes I4 only as the comparison target. Its row-local controls are only the strengthening GE3-applicable controls; the full replay/control matrix remains pending for GE4+.

## I4 Comparison

| Axis | I4 | I4-A | Relation |
|---|---:|---:|---|
| `focal_stability` | `0.878` | `0.889` | `stronger_or_comparable` |
| `neighbor_distinguishability_delta` | `0.133` | `0.154` | `stronger_or_comparable` |
| `neighbor_support_delta` | `0.082` | `0.087` | `stronger_or_comparable` |
| `neighbor_boundary_delta` | `0.126` | `0.145` | `stronger_or_comparable` |
| `environment_capacity_delta` | `0.123` | `0.134` | `stronger_or_comparable` |
| `focal_extraction_cost` | `0.018` | `0.016` | `stronger_or_comparable` |
| `extractive_flattening` | `0.014` | `0.013` | `stronger_or_comparable` |
| `merge_leakage` | `0.012` | `0.011` | `stronger_or_comparable` |

```text
thresholds_widened_relative_to_i4 = false
i4_imported_as_evidence = false
i4_replaced = false
```

## Checks

| Check | Passed |
|---|---|
| `i3_active_nulls_passed` | `true` |
| `i4_primary_generative_candidate_consumed_for_comparison` | `true` |
| `artifact_manifest_valid` | `true` |
| `artifact_role_alias_map_present` | `true` |
| `required_evidence_fields_present` | `true` |
| `core_digest_matches_payload` | `true` |
| `focal_stability_preserved` | `true` |
| `neighborhood_capacity_improves` | `true` |
| `extraction_flattening_merge_leakage_below_ceiling` | `true` |
| `classification_policy_declared_before_use` | `true` |
| `no_policy_retuning_label_threshold_or_post_hoc_boundary` | `true` |
| `false_positive_controls_not_triggered` | `true` |
| `i3_active_null_reference_bounded` | `true` |
| `shared_policy_status_bounded_to_strengthening_evidence` | `true` |
| `i4a_strengthens_i4_without_replacement` | `true` |
| `n27_context_not_consumed_as_n28_evidence` | `true` |
| `medium_debt_and_producer_residue_not_success` | `true` |
| `ge4_and_stronger_blocked_pending_replay_controls` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

I4-A does not support GE4+, GE5+, GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, or ant ecology.
