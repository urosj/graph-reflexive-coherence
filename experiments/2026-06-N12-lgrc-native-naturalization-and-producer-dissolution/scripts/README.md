# N12 Scripts

This directory holds N12 artifact builders, validators, and closeout helpers.

Generated scripts:

- `build_n12_native_naturalization_inventory.py`: builds the source-backed
  N05-N11 mechanism inventory using the provisional Iteration 1 row shape.
- `build_n12_naturalization_schema_v1.py`: builds the NAT ladder, schema,
  tags, claim flags, native-readiness criteria, rejection rules, and
  RC-compatibility fields, including non-RC quantity audit fields and NAT3/NAT4
  gates.
- `build_n12_route_conductance_memory_candidate.py`: evaluates the route memory
  candidate, geometry-vs-bookkeeping split, mutation boundary, non-RC audit,
  controls, NAT4 gates, and supported NAT level.
- `build_n12_response_magnitude_candidate.py`: evaluates the response
  magnitude candidate, trend/stability fields, mutation boundary, non-RC audit,
  controls, and supported NAT level.
- `build_n12_identity_acceptance_boundary.py`: records blocked identity
  acceptance theory gates and rationale.
- `build_n12_agentic_like_integration_boundary.py`: records blocked native
  agentic-like integration meta-policy gates and rationale.
- `build_n12_phase8_readiness_matrix.py`: builds the Phase 8 readiness matrix
  for native route conductance memory, response magnitude policy, blocked
  theory-sensitive rows, controls, telemetry requirements, test gates, and
  explicit no-implementation flags.
- `build_n12_closeout_and_handoff.py`: closes N12, freezes NAT levels, records
  roadmap update decisions, and decides whether the next step is targeted
  Phase 8 or N13.
