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
- `n17_resource_support_modulation_loop.json` - Iteration 7 resource/support
  modulation extension. Status: `passed`; acceptance state:
  `accepted_resource_support_modulation_extension_candidate_no_final_ap7`.
- `n17_resource_support_challenge_stability_probe.json` - Iteration 7-A
  local G5 challenge-stability probe for the fixed Iteration 7 route_b
  resource/support loop. Status: `passed`; acceptance state:
  `accepted_resource_support_challenge_stability_g5_candidate_no_final_ap7`.
- `n17_alternative_resource_support_g5_probe.json` - Iteration 7-B
  alternative low-margin resource/support G5 setup. Status: `passed`;
  acceptance state:
  `accepted_alternative_resource_support_g5_setup_no_final_ap7`.
- `n17_shared_medium_reciprocal_loop.json` - Iteration 8 local one-sided
  shared-medium reciprocal loop extension. Status: `passed`; acceptance state:
  `accepted_local_one_sided_shared_medium_g6_candidate_no_final_ap7`.
- `n17_shared_medium_reverse_perspective_probe.json` - Iteration 8-A
  shared-medium reverse-perspective/alternate-source probe. Status: `passed`;
  acceptance state:
  `accepted_alternate_source_shared_medium_g6_candidate_b4c5_reverse_blocked_no_final_ap7`.
- `n17_b4c5_reverse_perspective_replay_probe.json` - Iteration 8-B B4/C5
  reverse-perspective replay probe. Status: `passed`; acceptance state:
  `accepted_b4c5_reverse_perspective_blocked_multi_source_context_preserved_no_final_ap7`.
- `n17_paired_perspective_shared_medium_probe.json` - Iteration 8-C local
  paired-perspective shared-medium probe. Status: `passed`; acceptance state:
  `accepted_local_paired_perspective_shared_medium_g6_candidate_no_final_ap7`.
- `n17_b4c5_derived_paired_perspective_probe.json` - Iteration 8-D
  B4/C5-derived two-cycle paired-perspective probe. Status: `passed`;
  acceptance state:
  `accepted_b4c5_derived_two_cycle_paired_perspective_g6_candidate_no_original_relabel_no_final_ap7`.
- `n17_closed_loop_requirements_matrix.json` - Iteration 9 comparative
  requirements and AP7 classification matrix. Status: `passed`; acceptance
  state:
  `accepted_full_comparative_ap7_classification_pending_i10_closeout`.
- `n17_closeout_and_handoff.json` - Iteration 10 final closeout and N18
  handoff. Status: `passed`; acceptance state:
  `closed_claim_clean_ap7_artifact_level_closed_boundary_engagement_loop_candidate`.

Generated outputs must use relative paths, include source digests, and keep
claim flags explicit. Any absolute path in an output is a portability failure.
