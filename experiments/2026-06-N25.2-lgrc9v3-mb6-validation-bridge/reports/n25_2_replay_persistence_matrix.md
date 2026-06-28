# N25.2 Iteration 5 - Replay And Persistence Matrix

Status: passed.

Acceptance state:

```text
accepted_replay_persistence_matrix_mb4_candidates_no_mb5_no_mb6
```

## Summary

I5 replays the child-basin records emitted by I4 and the I4-A route variant.
Both pass artifact replay, snapshot/load replay, duplicate replay, time-order
replay, and exact persistence-ratio checks.

```text
i4_output_digest = 1a38c59b8e3149a4cdde1861237e45a0e9f2da8ecca6f548bf462313149527f1
i4a_output_digest = f2a49eab162893564433286d8e12bad8c3f4b3891f2f0007857ec23ae2d83d07
candidate_row_count = 2
mb4_replay_candidate_count = 2
multi_window_child_basin_persistence_replay_status = passed
persistence_claim_kind = replay_persistence_of_emitted_child_basin_records
long_horizon_persistence_supported = false
extended_multi_window_survival_under_stress_supported = false
mb_ladder_candidate = MB4_replay_backed_child_basin_persistence_candidate
mb5_or_stronger_supported = false
mb6_supported = false
n26_unscoped_consumption_allowed = false
```

## Replay Rows

```text
i4_reference_child_basin_core_0:
  replay_digest = fab53c21405e54a4eefb76d25632807d25f448f622880fb3479fbd6219d5f303
  artifact/snapshot/duplicate/time_order = passed/passed/passed/passed
  duplicate_first_emitted/second_emitted = true/false
  membership/support/coherence/boundary/flux = 1.0/1.0/1.0/1.0/1.0

i4a_route_variant_child_basin_core_2:
  replay_digest = 14856a9080bda75c8ac5a4a56d884f9db2b226d6b60457f5af8e6efe3cec2f4c
  artifact/snapshot/duplicate/time_order = passed/passed/passed/passed
  duplicate_first_emitted/second_emitted = true/false
  membership/support/coherence/boundary/flux = 1.0/1.0/1.0/1.0/1.0
```

The matrix-level multi-window status means I5 covers two source-current
child-basin candidate windows. Each native replay record remains a one-window
runtime replay record, matching the current runtime contract. I5 therefore
supports replay persistence of emitted child-basin records, not extended
multi-window survival under stress or long-horizon child-basin persistence.

For duplicate replay, `first_emitted=true` and `second_emitted=false` means
idempotency worked: the first replay emitted the validation record, while the
second replay suppressed a duplicate and returned the same digest.

## Scope Boundary

The I4-A front-capacity boundary-birth companion is not replayed as a
child-basin row:

```text
front_capacity_replay_scope = not_applicable
reason = front_capacity_companion_emits_topology_birth_not_child_basin_state_record
```

I5 supports MB4 replay-backed child-basin persistence candidates only. It does
not run fail-closed controls, does not support MB5, does not apply the MB6
gate, and does not open N26 unscoped consumption. I6 must still fail-close
label-only basin formation, old-basin thickening, transient sink,
collapse/reabsorption relabel, visual-only success, hidden producer insertion,
producer-as-native, front-capacity backfill, MB5-as-MB6, and unsafe relabel
controls.

## Checks

| Check | Passed |
|---|---|
| `i4_and_i4a_sources_ready_for_replay` | `true` |
| `artifact_snapshot_duplicate_and_time_order_replay_passed` | `true` |
| `persistence_ratios_exact_for_all_child_basin_candidates` | `true` |
| `duplicate_replay_stable_for_all_child_basin_candidates` | `true` |
| `runtime_emitted_records_only` | `true` |
| `front_capacity_companion_not_replayed_as_child_basin` | `true` |
| `missing_or_failed_replay_would_block_mb6` | `true` |
| `existing_runtime_executed_without_source_edits` | `true` |
| `embedded_artifact_manifest_has_json_pointers` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

Output digest:

```text
8d9163901e664ba8217ebe72389f99c34141dfbff76c81ee5f57f6e4e4484699
```
