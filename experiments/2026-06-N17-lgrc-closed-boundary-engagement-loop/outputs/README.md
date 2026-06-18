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
- `n17_loop_replay_and_control_matrix.json` - Iteration 5 replay and control
  matrix. Status: `passed`; acceptance state:
  `accepted_loop_replay_and_control_matrix_g4_candidate_no_final_ap7`.
- `n17_claim_boundary_record.json` - Iteration 6 MVP claim-boundary record.
  Status: `passed`; acceptance state:
  `accepted_mvp_ap7_claim_boundary_clean_pending_extensions_and_closeout`.
  Current evidence rung remains `G4`; G5 challenge stability is handled by
  `n17_mvp_challenge_stability_probe.json`.
- `n17_mvp_challenge_stability_probe.json` - Iteration 6-A bounded MVP
  challenge-stability probe. Status: `passed`; acceptance state:
  `accepted_bounded_g5_mvp_challenge_stability_no_final_ap7`.
- `n17_alternative_g5_challenge_probe.json` - Iteration 6-B alternative
  target-band-gated G5 challenge probe. Status: `passed`; acceptance state:
  `accepted_alternative_target_band_g5_mvp_challenge_stability_no_final_ap7`.

Planned artifacts:

- `n17_resource_support_modulation_loop.json`
- `n17_shared_medium_reciprocal_loop.json`
- `n17_closed_loop_requirements_matrix.json`
- `n17_closeout_and_handoff.json`

Generated outputs must use relative paths, include source digests, and keep
claim flags explicit. Any absolute path in an output is a portability failure.
