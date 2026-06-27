# N24 Configs

This directory will hold N24 configuration records for surplus, maintenance
floor, optionality-window, replay, and control probes.

Config records must use relative paths only and must declare thresholds before
positive evidence rows consume them.

Expected config families:

```text
source_handoff_inventory
schema_and_controls
active_nulls
minimal_surplus_probe
optional_continuation_probe
replay_and_control_matrix
stress_threshold_matrix
closeout_and_n25_handoff
```

