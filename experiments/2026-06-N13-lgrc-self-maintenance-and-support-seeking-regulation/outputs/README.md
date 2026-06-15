# N13 Outputs

This directory holds machine-readable N13 output artifacts.

Generated artifacts:

- `n13_support_condition_inventory.json`: source-backed inventory of support,
  disruption, restoration, regulation, integration, and N12 readiness/blocker
  records.
- `n13_support_schema_v1.json`: frozen support-condition row schema, AP
  mapping, control flags, claim flags, budget/replay fields, and fail-closed
  blockers.

Planned artifacts:

- `n13_support_derived_target_candidate.json`: support-state derived target
  candidate with source-current fields, derivation rule, and claim controls.
- `n13_support_seeking_regulation_candidate.json`: support-seeking regulation
  candidate with bounded response, budget debit, trend/stability fields, and
  controls.
- `n13_external_proxy_control_matrix.json`: external proxy, hidden target,
  post-hoc label, stale source, budget, and claim relabel controls.
- `n13_support_disruption_restoration_matrix.json`: support-present,
  support-disrupted, restoration, neutral perturbation, and no-support-control
  stress matrix.
- `n13_claim_boundary_record.json`: blocked identity, goal-ownership,
  intention, agency, native-support, and fully native integration claims.
- `n13_closeout_and_handoff.json`: final N13 AP ceiling, hypothesis
  resolutions, blockers, roadmap update decision, and handoff target.
