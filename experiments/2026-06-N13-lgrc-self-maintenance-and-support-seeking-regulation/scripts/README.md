# N13 Scripts

This directory holds N13 artifact builders, validators, and closeout helpers.

Generated scripts:

- `build_n13_support_condition_inventory.py`: builds the source-backed support
  condition inventory.
- `build_n13_support_schema_v1.py`: builds the support-condition schema, AP
  mapping, control flags, claim flags, budget/replay fields, and fail-closed
  blockers.

Planned scripts:

- `build_n13_support_derived_target_candidate.py`: evaluates the support-state
  derived target candidate.
- `build_n13_support_seeking_regulation_candidate.py`: evaluates the bounded
  support-seeking regulation candidate.
- `build_n13_external_proxy_control_matrix.py`: builds external proxy, hidden
  target, post-hoc label, stale source, budget, and claim relabel controls.
- `build_n13_support_disruption_restoration_matrix.py`: builds the support
  disruption and restoration stress matrix.
- `build_n13_claim_boundary_record.py`: records identity, goal-ownership,
  intention, agency, native-support, and integration blockers.
- `build_n13_closeout_and_handoff.py`: closes N13, freezes the supported AP
  level, records blockers, and decides whether the next step is N14 or
  targeted Phase 8.
