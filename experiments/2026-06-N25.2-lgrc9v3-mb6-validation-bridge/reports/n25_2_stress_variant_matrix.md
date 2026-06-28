# N25.2 Iteration 7 - Stress / Threshold / Variant Matrix

Status: passed.

Acceptance state:

```text
accepted_stress_variant_matrix_mb5_retained_multi_window_ready_pending_gate
```

## Summary

I7 consumes the I6 MB5 control-backed candidates and stresses the source-current
runtime records without modifying implementation code.

```text
i6_output_digest = 62d1213a2a31b2704a064cb53a23cf1838e08850b92508a5cf6b592cfeee4011
stress_candidate_count = 2
mb5_retained_candidate_count = 2
source_threshold_pass_count = 2
tightened_threshold_fail_closed_count = 2
source_merge_leakage_pass_count = 2
injected_pressure_fail_closed_count = 2
source_one_window_replay_pass_count = 2
extended_multi_window_blocker_count = 0
extended_multi_window_pass_count = 4
mb6_supported = false
```

## Candidate Rows

```text
i4_reference_child_basin_core_0:
  source_iteration = I4
  source_level_stress_clean = true
  extended_window_blocker_count = 0
  extended_window_pass_count = 2
  stress_result = mb5_retained_with_multi_window_replay_input_ready_for_i8_gate

i4a_route_variant_child_basin_core_2:
  source_iteration = I4-A
  source_level_stress_clean = true
  extended_window_blocker_count = 0
  extended_window_pass_count = 2
  stress_result = mb5_retained_with_multi_window_replay_input_ready_for_i8_gate
```

## Interpretation

I7 retains both MB5 candidates under source-threshold replay, source
merge/leakage ceiling, fail-closed tightened-threshold stress, fail-closed
injected-pressure stress, and source-backed route-variant comparison.

The result does not support MB6 by itself because I8 still has to apply the
MB6 gate. I7 now consumes I5-A multi-window replay evidence: each candidate has
a three-window closed-runtime persistence trace with exact replay ratios.

The front-capacity / boundary-birth companion remains provenance context only.
It cannot backfill child-basin stress, MB5, or MB6.

## Checks

| Check | Passed |
|---|---|
| `i6_control_matrix_ready_for_stress` | `true` |
| `flow_window_thresholds_stressed` | `true` |
| `merge_leakage_pressure_stressed` | `true` |
| `child_basin_persistence_window_stressed` | `true` |
| `front_capacity_boundary_birth_scope_preserved` | `true` |
| `source_backed_variant_axis_recorded` | `true` |
| `mb5_retained_and_mb6_blocker_recorded` | `true` |
| `no_unexpected_failed_open_stress` | `true` |
| `existing_runtime_executed_without_source_edits` | `true` |
| `embedded_artifact_manifest_has_json_pointers` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Digest

```text
output_digest = 1759dbb4d8c85c27bc056108f04fea3cfcc1c59b5ee9518ebb7f641e60949627
```
