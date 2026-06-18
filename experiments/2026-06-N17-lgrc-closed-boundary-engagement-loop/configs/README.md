# N17 Configs

Configuration files for N17 belong here.

Generated configs:

- `n17_source_registry.json` - Source rows and digests pinned from Iteration 1.
- `n17_loop_policy_v1.json` - G0-G7 loop ladder, G3 admissibility rule,
  trace-leg policy, MVP/extension policy, and row-decision policy.
- `n17_budget_limits_v1.json` - Fail-closed budget validity limits for loop
  rows.
- `n17_control_variants_v1.json` - Loop-specific controls, including
  feedback removal and one-way crossing relabel controls.
- `n17_replay_policy_v1.json` - Replay digest scope and admissibility rules.

Config files must use portable relative paths and deterministic JSON.
