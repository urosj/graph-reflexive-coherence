# N17 Outputs

Generated JSON artifacts for N17 belong here.

Generated artifacts:

- `n17_loop_source_inventory.json` - Iteration 1 source inventory and loop
  contract. Status: `passed`; acceptance state:
  `accepted_loop_source_inventory_only_no_ap7`.

Planned artifacts:

- `n17_loop_schema_v1.json`
- `n17_one_way_crossing_active_null.json`
- `n17_perturbation_response_recovery_loop.json`
- `n17_loop_replay_and_control_matrix.json`
- `n17_claim_boundary_record.json`
- `n17_resource_support_modulation_loop.json`
- `n17_shared_medium_reciprocal_loop.json`
- `n17_closed_loop_requirements_matrix.json`
- `n17_closeout_and_handoff.json`

Generated outputs must use relative paths, include source digests, and keep
claim flags explicit. Any absolute path in an output is a portability failure.
