# N25.2 Outputs

Generated N25.2 JSON artifacts will be written here.

Outputs should remain validation/classification artifacts. They should not
modify Phase 8 runtime behavior or relabel Phase 8 MB5 evidence as MB6 without
passing the N25.2 MB6 gate matrix.

Current outputs:

```text
n25_2_source_inventory_and_admissibility_audit.json
n25_2_mb6_gate_schema_and_controls.json
n25_2_phase8_mb5_evidence_chain_audit.json
n25_2_native_runtime_positive_probe.json
n25_2_native_runtime_variant_probe.json
```

Planned outputs:

```text
n25_2_replay_persistence_matrix.json
n25_2_fail_closed_control_matrix.json
n25_2_stress_variant_matrix.json
n25_2_mb6_support_blocker_matrix.json
n25_2_closeout_and_n26_handoff.json
```
