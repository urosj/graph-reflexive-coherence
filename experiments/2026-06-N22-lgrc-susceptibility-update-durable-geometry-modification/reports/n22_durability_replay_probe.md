# N22 Iteration 5 - Durability Replay Probe

Status: `passed`

Acceptance state: `accepted_replay_backed_su3_candidates_pending_i7_controls`

Output digest: `f46306e4550bf4e172a4dae074ccba3096cfdd2e65730fe68c0858b1fee41177`

## Summary

Iteration 5 replays the positive provisional SU2 rows from I4, I4-A,
and I4-B. Each row must pass artifact rehashing, snapshot/load replay,
duplicate replay, and post-snapshot route_b re-entry without active
prior-interaction reinforcement.

The route-local delta is not only a single in-memory window: it survives artifact reconstruction, duplicate replay, and a post-snapshot re-entry replay. Full control-backed SU4 still waits for I7.

## Replay Rows

| Row | Source | Rung | Artifact | Snapshot | Duplicate | Post-Snapshot Re-entry | Ratio | Narrow |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| `i4_minimal_route_b` | `I4` | `SU3` | `passed` | `passed` | `passed` | `passed` | 0.500000000000 | `false` |
| `dose_08_i4_reference` | `I4-A` | `SU3` | `passed` | `passed` | `passed` | `passed` | 0.500000000000 | `false` |
| `dose_14_stronger_bounded` | `I4-A` | `SU3` | `passed` | `passed` | `passed` | `passed` | 0.714285714286 | `false` |
| `single_route_b_reference` | `I4-B` | `SU3` | `passed` | `passed` | `passed` | `passed` | 0.500000000000 | `false` |
| `complementary_split_route_b_adjacent` | `I4-B` | `SU3` | `passed` | `passed` | `passed` | `passed` | 0.500000000000 | `true` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_inventory_passed` | `true` | accepted_source_handoff_inventory_no_susceptibility_evidence |
| `i2_schema_passed` | `true` | accepted_susceptibility_schema_frozen_no_positive_evidence |
| `i3_active_nulls_passed` | `true` | accepted_active_nulls_fail_closed_no_positive_evidence |
| `i4_minimal_probe_passed` | `true` | accepted_minimal_source_current_su2_candidate_pending_replay_controls |
| `i4a_dose_probe_passed` | `true` | accepted_dose_boundary_su2_extension_pending_replay_controls |
| `i4b_multipath_probe_passed` | `true` | accepted_multipath_shape_su2_extension_pending_replay_controls |
| `positive_candidate_count` | `true` | ["i4_minimal_route_b", "dose_08_i4_reference", "dose_14_stronger_bounded", "single_route_b_reference", "complementary_split_route_b_adjac... |
| `artifact_manifest_non_empty` | `true` | 112 |
| `artifact_hashes_match` | `true` | 112 |
| `all_candidates_artifact_replay_passed` | `true` | [{"artifact_replay": "passed", "delta_persistence_ratio": 0.5000000000000111, "duplicate_replay": "passed", "i5_consumable_role": "replay... |
| `all_candidates_snapshot_load_passed` | `true` | [{"artifact_replay": "passed", "delta_persistence_ratio": 0.5000000000000111, "duplicate_replay": "passed", "i5_consumable_role": "replay... |
| `all_candidates_duplicate_replay_passed` | `true` | [{"artifact_replay": "passed", "delta_persistence_ratio": 0.5000000000000111, "duplicate_replay": "passed", "i5_consumable_role": "replay... |
| `all_candidates_post_snapshot_reentry_passed` | `true` | [{"artifact_replay": "passed", "delta_persistence_ratio": 0.5000000000000111, "duplicate_replay": "passed", "i5_consumable_role": "replay... |
| `all_candidates_one_window_transient_rejected` | `true` | [{"artifact_replay": "passed", "delta_persistence_ratio": 0.5000000000000111, "duplicate_replay": "passed", "i5_consumable_role": "replay... |
| `all_candidates_promoted_only_to_su3` | `true` | [{"artifact_replay": "passed", "delta_persistence_ratio": 0.5000000000000111, "duplicate_replay": "passed", "i5_consumable_role": "replay... |
| `narrow_complementary_row_tracked` | `true` | [{"artifact_replay": "passed", "delta_persistence_ratio": 0.5000000000000111, "duplicate_replay": "passed", "i5_consumable_role": "replay... |
| `all_claims_still_blocked` | `true` | [{"artifact_replay": "passed", "delta_persistence_ratio": 0.5000000000000111, "duplicate_replay": "passed", "i5_consumable_role": "replay... |
| `unsafe_flags_all_false` | `true` | all replay rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |

## Claim Boundary

I5 supports replay-backed provisional SU3 candidates only. It does not support durable SU4, transfer SU5, SU6, final N22, the N21 ND6 bridge, semantic learning, choice, agency, native support, sentience, Phase 8, or ant-ecology implementation.

I5 does not run the full I7 control matrix. Every row keeps
`susceptibility_update_claim_allowed = false` and
`durable_geometry_modification_supported = false`.
