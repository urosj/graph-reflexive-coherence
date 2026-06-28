# N25.2 Iteration 5-A - Multi-Window Persistence Replay

Status: passed.

Acceptance state:

```text
accepted_multi_window_persistence_replay_mb4_extension_no_mb6
```

## Summary

I5-A extends I5 by replaying each runtime-emitted child-basin candidate across
three closed-runtime snapshot windows.

```text
i5_output_digest = 8d9163901e664ba8217ebe72389f99c34141dfbff76c81ee5f57f6e4e4484699
declared_replay_window_count = 3
candidate_count = 2
multi_window_passed_candidate_count = 2
all_window_child_basin_records_present = true
all_window_replay_results_passed = true
all_window_replay_ratios_exact = true
duplicate_replay_suppression_observed = true
eventful_stress_window_supported = false
mb6_supported = false
```

## Candidate Rows

```text
i4_reference_child_basin_core_0:
  runtime_snapshot_window_count = 3
  multi_window_persistence_replay_status = passed
  window_trace_digest = b7962e16fefdbd882039b38bff454161c17998ab83fd30ef2f1a3686da4e3140

i4a_route_variant_child_basin_core_2:
  runtime_snapshot_window_count = 3
  multi_window_persistence_replay_status = passed
  window_trace_digest = 19a9b150d775ed8aff8a76c1e60c03376ebe1eecc8921e4d5a68091a0915e94f
```

## Interpretation

I5-A supplies the missing multi-window replay evidence at the experiment layer:
the emitted child-basin records remain present across three closed-runtime
snapshot/replay windows and replay ratios remain exact in every window.

This does not change the native replay validator shape. Each native validation
record still has `window_count = 1.0`; I5-A is the aggregate source-current
multi-window replay trace built from repeated closed-runtime snapshots. It is
therefore valid as multi-window replay evidence for I8 gate classification, but
it is not eventful stress persistence, MB5 by itself, MB6 by itself, native
support, agency, or Phase 8 completion.

## Checks

| Check | Passed |
|---|---|
| `i5_replay_matrix_available` | `true` |
| `multi_window_snapshots_recorded_for_each_candidate` | `true` |
| `child_basin_records_present_across_windows` | `true` |
| `window_replay_results_passed` | `true` |
| `window_replay_ratios_exact` | `true` |
| `duplicate_replay_suppression_preserved` | `true` |
| `multi_window_persistence_allowed_for_i8_gate` | `true` |
| `existing_runtime_executed_without_source_edits` | `true` |
| `embedded_artifact_manifest_has_json_pointers` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Digest

```text
output_digest = c297e0ef20296c37d54717df4d4d0adc3c44944e5fc2f828fd22ff789e67ec0a
```
