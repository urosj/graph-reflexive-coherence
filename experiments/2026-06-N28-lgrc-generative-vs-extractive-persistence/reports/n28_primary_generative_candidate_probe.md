# N28 Iteration 4 - Primary Generative Candidate Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_primary_source_current_ge3_generative_candidate_pending_replay_controls`
- Output digest: `daa25e4694929b11af38d7b044f4b4f5a4e70f6c2fbcae954db6a84854c08e5d`
- Provisional GE rung: `GE3`
- GE4 or stronger supported: `false`
- Shared policy status: `partially_supported`
- Shared policy scope: `provisionally_primary_only_pending_alternative_and_contrast_rows`
- Ready for I4-A strengthening: `true`

I4 opens the first source-current positive N28 row, but only as a provisional GE3 primary generative candidate. Replay, full controls, contrasts, stress, and final closeout remain blocked.

## Candidate Metrics

```text
focal_stability_preserved = true
neighbor_distinguishability_delta = 0.133
neighbor_support_delta = 0.082
neighbor_boundary_delta = 0.126
environment_capacity_delta = 0.123
merge_leakage_score = 0.012
merge_leakage_ceiling = 0.025
```

## Interpretation

The row passes the three-axis I2 classifier locally: focal persistence is stable, neighborhood capacity improves, and extraction/leakage remains below ceiling. This supports a primary generative candidate, not final generative persistence and not shared-policy closeout.

In geometric dynamics terms, the focal basin keeps its shape and viability while the surrounding geometry becomes more basin-capable. The original basin does not survive by draining or flattening its neighborhood. Its support, coherence, and stability remain above floor, so the focal basin remains valid. At the same time, the adjacent shell becomes more structured: it separates more clearly from the focal basin, gains support, gains boundary integrity, and has higher capacity to hold basin-like organization.

The dynamics are therefore not one basin persisting by absorbing the surrounding field, nor focal survival while nearby geometry becomes less organized. They are persistence with neighboring capacity increase: a stable basin preserves itself while nearby geometry becomes more capable of holding distinct organized structure.

The `shared_regime_policy_status = partially_supported` field is scoped only to this primary generative row. It does not settle the shared policy family until the generative strengthening row, extractive contrasts, and competitive/neutral contrasts exist.

The artifact manifest uses bundled trace files. The row-local `artifact_role_alias_map` records that `neighbor_capacity_trace` covers neighbor distinguishability, support floor, boundary integrity, environment capacity, and neighborhood capacity delta traces, while `extraction_leakage_trace` covers focal extraction cost, extractive flattening, and merge/leakage traces.

I4 also inherits the I3 active-null matrix as a fail-closed false-positive boundary. Its row-local controls are only the primary GE3-applicable controls; the full replay/control matrix remains pending for GE4+.

## Checks

| Check | Passed |
|---|---|
| `i3_active_nulls_passed` | `true` |
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
| `shared_policy_status_bounded_to_primary_row` | `true` |
| `n27_context_not_consumed_as_n28_evidence` | `true` |
| `medium_debt_and_producer_residue_not_success` | `true` |
| `ge4_and_stronger_blocked_pending_replay_controls` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

I4 does not support GE4+, GE5+, GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, or ant ecology.
