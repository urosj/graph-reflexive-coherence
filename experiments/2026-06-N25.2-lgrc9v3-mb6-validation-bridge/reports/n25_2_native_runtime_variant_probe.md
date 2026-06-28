# N25.2 Iteration 4-A - Native Runtime Variant / Companion Probe

Status: passed.

Acceptance state:

```text
accepted_native_runtime_variant_and_front_capacity_companion_mb3_scope_no_mb6
```

## Summary

I4-A adds runtime variety without replacing I4. It runs two closed-runtime
companions:

```text
i4_output_digest = 1a38c59b8e3149a4cdde1861237e45a0e9f2da8ecca6f548bf462313149527f1
i4_replaced = false
i4_mb5_or_mb6_backfilled = false
route_variant_candidate = MB3_source_current_child_basin_candidate_emission_variant
front_capacity_companion_candidate = not_assigned_topology_birth_companion_only
mb6_supported = false
n26_unscoped_consumption_allowed = false
artifact_manifest_scope = embedded_payloads_only
```

## Route Child-Basin Variant

The route variant keeps the I4 fixture family and runtime policies but changes
the selected native route sink. It emits a comparable flow-window and
child-basin state record with a different child-basin core.

```text
child_basin_id = child-basin-state:2e193a6afab8971da75108ef9ae5ac03
child_basin_core_ids = [2]
basin_signature_digest = 376154b4a3c009ca84ca53d005cfa9d628f749d61217a143a2f9a711c9ce8def
trace_digest = 51a23e105d32a15f61f794b2901ab3a44cc78e124798bf591bb30dc18eb3aca7
topology_provenance_shape = collapse_reabsorption_shaped_existing_graph
```

## Front-Capacity Companion

The front-capacity companion runs the corrected front-capacity boundary-birth
path. It is useful because it shows visible topology growth through the closed
runtime, but it is companion context only: it does not backfill I4's child-basin
record and does not support MB5 or MB6.

```text
initial_node_count = 13
final_node_count = 14
initial_edge_count = 12
final_edge_count = 13
visible_topology_growth = true
parent_eligibility_mode = grcl9v3_front_capacity
```

## Boundary

I4-A strengthens the evidence base by adding one native child-basin variant and
one topology-growth companion. It remains below replay-backed MB4,
control-backed MB5, MB6, and N26 unscoped consumption. I5 must replay
runtime-emitted child-basin records; I6 must still run fail-closed controls.

## Checks

| Check | Passed |
|---|---|
| `i4_mb3_candidate_available_for_variant_probe` | `true` |
| `existing_runtime_executed_without_source_edits` | `true` |
| `route_variant_emits_comparable_child_basin_record` | `true` |
| `front_capacity_companion_emits_visible_topology_growth` | `true` |
| `front_capacity_uses_corrected_parent_eligibility` | `true` |
| `variant_evidence_cannot_backfill_unrelated_mb5_or_mb6` | `true` |
| `embedded_artifact_manifest_has_json_pointers` | `true` |
| `replay_controls_stress_mb6_and_n26_pending` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

Output digest:

```text
f2a49eab162893564433286d8e12bad8c3f4b3891f2f0007857ec23ae2d83d07
```
