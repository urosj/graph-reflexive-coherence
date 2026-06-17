# N16 Outputs

Generated JSON artifacts for N16 belong here.

Generated artifacts:

- `n16_boundary_source_inventory.json`
- `n16_boundary_schema_v1.json`
- `n16_quiet_boundary_calibration.json`
- `n16_challenge_sweep_matrix.json`
- `n16_boundary_state_sweep_matrix.json`
- `n16_selected_interaction_probe_matrix.json`
- `n16_basin_boundary_requirements_matrix.json`
- `n16_claim_boundary_record.json`
- `n16_closeout_and_handoff.json`

Generated outputs must use relative paths, include source digests, and keep
claim flags explicit. Any absolute path in an output is a portability failure.
