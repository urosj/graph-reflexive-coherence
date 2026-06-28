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
build_n25_2_replay_persistence_matrix.py
build_n25_2_multi_window_persistence_replay.py
build_n25_2_fail_closed_control_matrix.py
build_n25_2_stress_variant_matrix.py
build_n25_2_mb6_support_blocker_matrix.py
build_n25_2_closeout_and_n26_handoff.py
render_n25_2_native_visual_gallery.py
```

The native visual gallery script copies selected LGRC9V3 example visual assets
into experiment-local outputs and records source/copy hashes. It is a
visualization/provenance helper only; visual-only MB6 proof remains blocked.
