# N25.2 Iteration 6 - Fail-Closed Control Matrix

Status: passed.

Acceptance state:

```text
accepted_fail_closed_controls_mb5_candidates_no_mb6
```

## Summary

I6 consumes the I5 clean replay rows and runs fail-closed controls over both
runtime-emitted child-basin candidates.

```text
i5_output_digest = 8d9163901e664ba8217ebe72389f99c34141dfbff76c81ee5f57f6e4e4484699
i5a_output_digest = c297e0ef20296c37d54717df4d4d0adc3c44944e5fc2f828fd22ff789e67ec0a
control_candidate_count = 2
mb5_control_backed_candidate_count = 2
runtime_required_control_count = 17
supplemental_experiment_control_count = 4
multi_window_replay_passed_candidate_count = 2
failed_open_control_count = 0
mb_ladder_candidate = MB5_control_backed_native_multi_basin_candidate
mb6_supported = false
n26_unscoped_consumption_allowed = false
```

## Control Rows

```text
i4_reference_child_basin_core_0:
  control_record_count = 21
  clean_replay_present = true
  all_controls_failed_closed = true
  mb5_control_backed_candidate_allowed = true

i4a_route_variant_child_basin_core_2:
  control_record_count = 21
  clean_replay_present = true
  all_controls_failed_closed = true
  mb5_control_backed_candidate_allowed = true
```

I6 is the first N25.2 point where the two child-basin candidates reach an MB5
control-backed candidate ceiling. It remains bounded: MB6 is not applied,
stress/window variation is still pending I7, and N26 unscoped consumption
remains blocked.

## Front-Capacity Boundary

The I4-A front-capacity topology-birth companion remains provenance context
only:

```text
front_capacity_control_scope = provenance_context_only
front_capacity_backfill_control_status = failed_closed
mb5_or_mb6_backfill_allowed = false
```

## Checks

| Check | Passed |
|---|---|
| `i5_replay_matrix_ready_for_controls` | `true` |
| `clean_replay_consumed_for_each_control_row` | `true` |
| `multi_window_replay_available_for_each_control_row` | `true` |
| `all_runtime_required_controls_failed_closed` | `true` |
| `supplemental_n25_2_controls_failed_closed` | `true` |
| `no_failed_open_controls` | `true` |
| `control_idempotency_stable` | `true` |
| `front_capacity_backfill_failed_closed` | `true` |
| `mb5_candidate_allowed_but_mb6_blocked` | `true` |
| `existing_runtime_executed_without_source_edits` | `true` |
| `embedded_artifact_manifest_has_json_pointers` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

Output digest:

```text
62d1213a2a31b2704a064cb53a23cf1838e08850b92508a5cf6b592cfeee4011
```
