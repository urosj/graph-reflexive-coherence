# N24 Scripts

This directory will hold reconstruction scripts for N24 artifacts.

Planned scripts:

```text
build_n24_source_handoff_inventory.py
build_n24_abundance_schema_and_controls.py
build_n24_active_nulls_and_failure_baselines.py
build_n24_minimal_surplus_probe.py
build_n24_optional_continuation_set_probe.py
build_n24_replay_and_control_matrix.py
build_n24_stress_threshold_matrix.py
build_n24_closeout_and_n25_handoff.py
render_n24_abundance_optionality_visualization.py
```

Scripts must keep generated paths relative and must not use local absolute
paths in committed records.

The visualization renderer creates supporting artifact-level graph, sequence,
and animation assets from the N24 high-margin optional continuation row. It
preserves the native flux-debt and producer-scaffold distinction and does not
add reward, semantic choice, agency, native support, sentience, Phase 8, or
ant-ecology evidence.
