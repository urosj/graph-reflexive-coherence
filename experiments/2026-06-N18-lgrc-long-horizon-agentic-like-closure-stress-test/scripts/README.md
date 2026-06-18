# N18 Scripts

Deterministic builders and validators for N18 are written here.

Current scripts:

```text
build_n18_long_horizon_source_inventory.py
build_n18_long_horizon_schema_v1.py
build_n18_short_horizon_ap7_replay_baseline.py
build_n18_horizon_window_sweep.py
validate_n18_stress_row.py
```

Expected builders:

```text
build_n18_long_horizon_source_inventory.py
build_n18_long_horizon_schema_v1.py
build_n18_short_horizon_ap7_replay_baseline.py
build_n18_horizon_window_sweep.py
build_n18_support_proxy_stress_matrix.py
build_n18_route_memory_stress_matrix.py
build_n18_environment_resource_stress_matrix.py
build_n18_shared_medium_stress_matrix.py
build_n18_long_horizon_control_and_classification_matrix.py
build_n18_closeout_and_handoff.py
```

Expected validator:

```text
validate_n18_stress_row.py
```

Scripts should write only experiment-local outputs/reports unless a later task
explicitly asks for broader updates.
