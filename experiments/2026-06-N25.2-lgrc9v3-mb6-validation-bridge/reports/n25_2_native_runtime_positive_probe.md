# N25.2 Iteration 4 - Native LGRC9V3 Runtime Positive Probe

Status: passed.

Acceptance state:

```text
accepted_native_runtime_positive_mb3_candidate_pending_replay_controls_no_mb6
```

## Summary

Iteration 4 runs the closed LGRC9V3 runtime and emits the first N25.2
source-current positive multi-basin candidate. It stops before replay and
controls, so the ceiling is MB3 candidate emission.

```text
i3_output_digest = 7ef81dc80600d0fee487804efc3b022a2547b71b7a63bacdd761a41691f0dc6d
runtime_execution_performed = true
flow_window_record_count = 1
child_basin_state_record_count = 1
replay_validation_record_count = 0
merge_leakage_control_record_count = 0
mb_ladder_candidate = MB3_source_current_child_basin_candidate_emission
mb6_gate_status = not_applied
mb6_supported = false
n26_consumption_effect = unscoped_consumption_blocked
runtime_execution_from_closed_implementation = true
artifact_manifest_scope = embedded_payloads_only
topology_provenance_shape = collapse_reabsorption_shaped_existing_graph
```

## Child-Basin Candidate

```text
child_basin_id = child-basin-state:556450a8434944316a25f18c2eb05eb6
basin_signature_digest = 1f712f5dc0717650ade3bd6e2e94f860e6e3323fc320e9ddb7d6be2fb719b535
trace_digest = a2d1b64b98da8d584c9c8f736e4503495376330fd6313bb5811ab34901ab5e37
producer_native_mutation_owner = native_source_current
producer_residue_status = not_load_bearing_for_claim
source_current_status = native_runtime_emitted
flow_window_id = 556450a8434944316a25f18c2eb05eb614e12d91858f55183d5d9008052edb84
```

## Boundary

I4 does not validate persistence and does not run fail-closed controls. I5 must
consume this artifact for replay/persistence, I6 must consume it for controls,
and I8 must apply the MB6 gate.

The emitted topology/refinement provenance is collapse/reabsorption-shaped over
the existing graph. That is admissible for MB3 candidate emission, but I6 must
fail-close collapse/reabsorption relabel, old-basin thickening relabel,
transient-flow-sink relabel, and label-only basin formation before this row can
contribute to anything stronger.

Blocked in I4:

```text
MB5_control_backed_candidate
MB6
N26_unscoped_consumption
native_support
agency
semantic_learning
sentience
Phase_8_completion
```

## Checks

| Check | Passed |
|---|---|
| `i3_mb5_chain_validated` | `true` |
| `existing_runtime_executed_without_source_edits` | `true` |
| `runtime_execution_trace_emitted` | `true` |
| `flow_window_records_emitted` | `true` |
| `child_basin_state_records_emitted` | `true` |
| `snapshot_contains_runtime_emitted_records` | `true` |
| `topology_refinement_provenance_present` | `true` |
| `collapse_reabsorption_shape_recorded_and_controls_deferred` | `true` |
| `producer_native_mutation_ownership_recorded` | `true` |
| `implementation_digests_recorded` | `true` |
| `child_basin_required_fields_recorded` | `true` |
| `embedded_artifact_manifest_has_json_pointers` | `true` |
| `replay_controls_stress_mb6_and_n26_pending` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

Output digest:

```text
1a38c59b8e3149a4cdde1861237e45a0e9f2da8ecca6f548bf462313149527f1
```
