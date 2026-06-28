# N25.2 Scripts

N25.2 scripts should build validation and classification artifacts only.

They may read existing source artifacts and rerun focused validation commands,
but they should not implement new Phase 8 runtime surfaces. If validation
discovers a runtime defect, record it as a blocker or open a separate
implementation task before modifying runtime code.

Current builders:

```text
build_n25_2_source_inventory_and_admissibility_audit.py
build_n25_2_mb6_gate_schema_and_controls.py
build_n25_2_phase8_mb5_evidence_chain_audit.py
build_n25_2_native_runtime_positive_probe.py
build_n25_2_native_runtime_variant_probe.py
```
