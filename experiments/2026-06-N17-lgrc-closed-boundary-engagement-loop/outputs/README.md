# N17 Outputs

Generated JSON artifacts for N17 belong here.

Generated artifacts:

- `n17_loop_source_inventory.json` - Iteration 1 source inventory and loop
  contract. Status: `passed`; acceptance state:
  `accepted_loop_source_inventory_only_no_ap7`.
- `n17_loop_schema_v1.json` - Iteration 2 loop schema and AP7 gate. Status:
  `passed`; acceptance state: `accepted_loop_schema_v1_no_ap7_evidence`.
- `n17_one_way_crossing_active_null.json` - Iteration 3 one-way crossing
  active null. Status: `passed`; acceptance state:
  `accepted_one_way_crossing_active_null_no_ap7`.
- `n17_perturbation_response_recovery_loop.json` - Iteration 4 minimal
  perturbation-response-recovery G3 candidate. Status: `passed`; acceptance
  state:
  `accepted_perturbation_response_recovery_g3_candidate_pending_controls_no_ap7`.

Planned artifacts:

- `n17_loop_replay_and_control_matrix.json`
- `n17_claim_boundary_record.json`
- `n17_resource_support_modulation_loop.json`
- `n17_shared_medium_reciprocal_loop.json`
- `n17_closed_loop_requirements_matrix.json`
- `n17_closeout_and_handoff.json`

Generated outputs must use relative paths, include source digests, and keep
claim flags explicit. Any absolute path in an output is a portability failure.
