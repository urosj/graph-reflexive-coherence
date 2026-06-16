# N15 Configs

Configuration files for N15 endogenous proxy formation fixtures and controls
belong here.

Initial setup recorded no config fixtures. Iteration 1 pinned source artifacts
before any generated config was treated as evidence.

Generated config files:

- `n15_source_registry.json`: portable relative source artifact references and
  expected SHA-256 values.
- `n15_derivation_policy_v1.json`: frozen derivation policy, codebooks,
  weights or rule order, drift bounds, and clamp rules.
- `n15_budget_limits_v1.json`: budget units and validity limits for source
  rows, transforms, serialized bytes, replays, and validations.
- `n15_control_variants_v1.json`: adversarial control variants and expected
  fail-closed blockers.
- `n15_replay_policy_v1.json`: canonical JSON digest scope, replay modes, and
  order-inversion policy.

These files are materialized Iteration 2 config contracts. They are not
independent evidence for `AP5`; later iterations must still generate and
validate candidate rows.

Config files must not record absolute filesystem paths.
