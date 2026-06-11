# N04 Iteration 13 Taxonomy Inventory

Status: **passed**

Claim ceiling: `taxonomy_inventory_only`

Iteration 13 inventories existing evidence only. It does not run new probes and does not promote claims.

## Checks

- `all_m0_m6_present`: `True`
- `d1_d5_present`: `True`
- `d_rows_have_projection_fields`: `True`
- `identity_kind_surface_split_present`: `True`
- `substrate_class_values_declared`: `True`
- `all_rows_have_sources`: `True`
- `all_rows_have_source_reports`: `True`
- `all_rows_have_claim_ceiling`: `True`
- `all_rows_have_row_specific_claim_flags`: `True`
- `all_rows_have_persistence_fields`: `True`
- `visual_references_are_not_evidence_sources`: `True`
- `no_unrestricted_claims_promoted`: `True`
- `no_persistence_t6_claimed`: `True`
- `m6_scoped_to_same_fixture_chain`: `True`
- `d5_blocked_from_runtime_basin_movement`: `True`
- `lane_c_d_e_supporting_rows_present`: `True`
- `m6_resilience_extension_rows_present`: `True`
- `iter16_corridor_transfer_row_present`: `True`
- `iter16b_corridor_perturbation_row_present`: `True`
- `iter16c_high_shock_capacity_row_present`: `True`
- `iter17_ring_transfer_row_present`: `True`
- `iter17a_ring_unwrap_robustness_row_present`: `True`
- `iter17b_circular_ring_motion_row_present`: `True`
- `iter17c_ring_geometry_closeout_row_present`: `True`
- `iter18_grid_transfer_row_present`: `True`
- `iter18b_grid_two_axis_turn_row_present`: `True`
- `iter18c_grid_state_gated_routing_row_present`: `True`
- `iter18d_grid_geometry_selection_row_present`: `True`
- `iter18e_composed_1d_fork_competition_row_present`: `True`
- `iter18f_balanced_local_preference_fork_row_present`: `True`
- `iter18g_integrated_2d_composed_gate_row_present`: `True`
- `iter18h_s3_grid_series_closeout_row_present`: `True`
- `iter19c_adaptive_topology_entry_row_present`: `True`
- `iter19d_topology_mutating_movement_boundary_row_present`: `True`
- `iter19e_topology_mutating_movement_candidate_row_present`: `True`
- `iter20_topology_mutating_repeatability_stress_row_present`: `True`
- `iter21_native_lgrc_choice_selection_boundary_row_present`: `True`
- `iter21b_native_route_arbitration_support_row_present`: `True`
- `fixture_topology_change_distinguished_from_runtime_topology`: `True`
- `iter22_identity_through_topology_mutation_boundary_row_present`: `True`
- `iter22b_identity_through_native_route_arbitrated_topology_boundary_row_present`: `True`

## Counts

- `inventory_rows`: `47`
- `movement_rows`: `29`
- `deformation_rows`: `5`
- `supporting_rows`: `3`

## M6 Resilience Extensions

Iterations 15-C/15-D/15-E extend the M taxonomy with source-backed resilience rows. They do not promote broad geometry-transfer, locomotion-like, adaptive-topology, agency, biology, identity-acceptance, inherited-N03, or unrestricted movement claims.

| Row | Persistence | Geometry scope | Recovery status | Claim ceiling |
|---|---|---|---|---|
| `M6_s0_perturbation_tolerance_profile` | `tested_negative` | `same_fixture` | `t6_recovery_failed_source_budget_exhausted` | `s0_same_fixture_perturbation_tolerance_profile` |
| `M6_shock_resistant_same_family_geometry_recovery_candidate` | `T6_candidate` | `transferred_geometry` | `recovers_0_02_fails_t6_centroid_restoration_at_0_15` | `shock_resistant_same_family_geometry_recovery_candidate` |
| `M6_large_shock_absorber_same_family_recovery_candidate` | `T6_candidate` | `transferred_geometry` | `recovers_0_15_large_shock` | `large_shock_absorber_same_family_recovery_candidate` |

## Inventory

| Row | M | D | Projection | Persistence | Identity | Surface | Claim ceiling |
|---|---:|---:|---:|---|---|---|---|
| `M0_fixed_substrate_negative_chain` | `M0` | `None` | `None` | `not_applicable` | `null` | `fixed_substrate` | `no_movement_response_candidate` |
| `M0_fixed_substrate_negative_ring` | `M0` | `None` | `None` | `not_applicable` | `null` | `fixed_substrate` | `no_movement_response_candidate` |
| `M1_apparent_centroid_displacement_chain_identity_blocked` | `M1` | `None` | `None` | `not_applicable` | `coherence_basin` | `fixed_substrate` | `apparent_centroid_displacement_only` |
| `M1_apparent_centroid_displacement_ring_identity_blocked` | `M1` | `None` | `None` | `not_applicable` | `coherence_basin` | `fixed_substrate` | `apparent_centroid_displacement_only` |
| `M2_boundary_reassignment_shape_blocked` | `M2` | `None` | `None` | `not_applicable` | `coherence_basin` | `fixed_substrate` | `identity_preserving_boundary_reassignment_shape_blocked` |
| `M3_shape_preserving_identity_displacement_chain` | `M3` | `None` | `None` | `not_applicable` | `coherence_basin` | `fixed_substrate` | `shape_preserving_identity_displacement_fixture_evidence` |
| `M3_shape_preserving_identity_displacement_ring` | `M3` | `None` | `None` | `not_applicable` | `coherence_basin` | `fixed_substrate` | `shape_preserving_identity_displacement_fixture_evidence` |
| `M4_boundary_coupled_response_fixture` | `M4` | `None` | `None` | `not_applicable` | `boundary_signal` | `boundary_fixture` | `boundary_coupled_pulse_fixture_validation` |
| `M5_direction_parity_boundary_response` | `M5` | `None` | `None` | `not_applicable` | `boundary_signal` | `boundary_fixture` | `m5_direction_parity_supported_boundary_response` |
| `M6_native_same_fixture_self_renewal_candidate` | `M6` | `None` | `None` | `T5_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `native_m6_same_fixture_self_renewal_candidate` |
| `M6_s0_perturbation_tolerance_profile` | `M6` | `None` | `None` | `tested_negative` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s0_same_fixture_perturbation_tolerance_profile` |
| `M6_shock_resistant_same_family_geometry_recovery_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `shock_resistant_same_family_geometry_recovery_candidate` |
| `M6_large_shock_absorber_same_family_recovery_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `large_shock_absorber_same_family_recovery_candidate` |
| `M6_s4_corridor_transfer_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s4_corridor_m6_transfer_candidate` |
| `M6_s4_corridor_perturbation_envelope` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s4_corridor_perturbation_envelope_profile` |
| `M6_s4_corridor_high_shock_capacity_requirement` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s4_corridor_high_shock_capacity_requirement_probe` |
| `M6_s1_ring_declared_unwrap_transfer_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s1_ring_m6_transfer_candidate_under_declared_unwrap` |
| `M6_s1_ring_unwrap_robust_transfer_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s1_ring_unwrap_robust_transfer_candidate` |
| `M6_s1_ring_circular_motion_evidence_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s1_ring_circular_motion_evidence_candidate` |
| `M6_s1_ring_circular_motion_with_unwrap_robustness_closeout` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness` |
| `M6_s3_grid_route_defined_transfer_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s3_grid_route_defined_m6_transfer_candidate` |
| `M6_s3_grid_two_axis_turn_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s3_grid_two_axis_turn_m6_transfer_candidate` |
| `M6_s3_grid_state_gated_routing_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s3_grid_state_gated_two_input_two_output_routing_candidate` |
| `M6_s3_grid_geometry_scored_selection_design_prototype` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s3_grid_geometry_scored_selection_design_prototype` |
| `M6_s3_grid_composed_1d_fork_competition_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s3_grid_composed_1d_fork_competition_candidate` |
| `M6_s3_grid_balanced_local_preference_fork_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s3_grid_balanced_local_preference_fork_competition_candidate` |
| `M6_s3_grid_integrated_2d_composed_gate_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s3_grid_integrated_2d_composed_gate_candidate` |
| `M6_s3_grid_series_closeout_fixed_topology_2d_gate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s3_grid_integrated_2d_composed_gate_candidate` |
| `S7_port_graph_mapping_contract_only` | `None` | `None` | `None` | `not_applicable` | `null` | `native_causal_pulse_substrate_surface` | `s7_port_graph_mapping_contract_only` |
| `M6_s7_fixed_port_composed_gate_candidate` | `M6` | `None` | `None` | `T6_candidate` | `coherence_basin` | `native_causal_pulse_substrate_surface` | `s7_fixed_port_composed_gate_candidate` |
| `S7_topology_lineage_adaptive_gate_blocked` | `None` | `None` | `None` | `not_applicable` | `null` | `native_causal_pulse_substrate_surface` | `s7_fixed_port_composed_gate_candidate` |
| `S7_adaptive_topology_entry_candidate_native_surface_lineage` | `None` | `None` | `None` | `not_applicable` | `boundary_signal` | `native_causal_pulse_substrate_surface` | `adaptive_topology_entry_candidate` |
| `S7_topology_mutating_movement_probe_blocked` | `None` | `None` | `None` | `not_applicable` | `boundary_signal` | `native_causal_pulse_substrate_surface` | `adaptive_topology_entry_candidate` |
| `S7_topology_mutating_movement_candidate_after_state_reabsorption` | `None` | `None` | `M6` | `not_applicable` | `boundary_signal` | `native_causal_pulse_substrate_surface` | `topology_mutating_movement_candidate` |
| `S7_topology_mutating_repeatability_stress_boundary` | `None` | `None` | `M6` | `T5_candidate` | `boundary_signal` | `native_causal_pulse_substrate_surface` | `topology_mutating_movement_candidate` |
| `S7_native_lgrc_choice_selection_boundary_blocked` | `None` | `None` | `M6` | `not_applicable` | `boundary_signal` | `native_causal_pulse_substrate_surface` | `topology_mutating_movement_candidate` |
| `S7_native_route_arbitration_runtime_support` | `None` | `None` | `M6` | `not_applicable` | `boundary_signal` | `native_causal_pulse_substrate_surface` | `topology_mutating_movement_candidate` |
| `S7_identity_through_topology_mutation_boundary_blocked` | `None` | `None` | `M6` | `not_applicable` | `boundary_signal` | `native_causal_pulse_substrate_surface` | `topology_mutating_movement_candidate` |
| `S7_identity_through_native_route_arbitrated_topology_boundary_blocked` | `None` | `None` | `M6` | `not_applicable` | `boundary_signal` | `native_causal_pulse_substrate_surface` | `topology_mutating_movement_candidate` |
| `D1_local_pulse_transport` | `None` | `D1` | `None` | `not_applicable` | `null` | `fixed_substrate` | `pulse_transport_only` |
| `D2_local_geometry_coupling` | `None` | `D2` | `M4` | `not_applicable` | `deformation_token` | `deformation_surface` | `pulse_local_geometry_coupling` |
| `D3_traveling_deformation_candidate` | `None` | `D3` | `M5` | `not_applicable` | `deformation_token` | `deformation_surface` | `traveling_deformation_candidate` |
| `D4_direction_controlled_deformation` | `None` | `D4` | `M3` | `not_applicable` | `deformation_token` | `deformation_surface` | `direction_controlled_traveling_deformation_supported` |
| `D5_deformation_surface_movement_reclassification` | `None` | `D5` | `M3` | `not_applicable` | `deformation_token` | `deformation_surface` | `substrate_carried_deformation_movement_candidate` |
| `C_feedback_coupled_self_renewal_candidate` | `None` | `None` | `M6` | `T5_candidate` | `boundary_signal` | `boundary_fixture` | `m6_feedback_coupled_self_renewal_candidate` |
| `E_hybrid_causal_pulse_substrate_surface` | `None` | `None` | `None` | `not_applicable` | `null` | `native_causal_pulse_substrate_surface` | `hybrid_lgrc_causal_pulse_substrate_surface_contract_supported` |
| `F_native_causal_pulse_substrate_surface_support` | `None` | `None` | `None` | `not_applicable` | `null` | `native_causal_pulse_substrate_surface` | `native_lgrc_pulse_substrate_surface_supported` |

## Source Artifacts

- `fixed_substrate_tranche_a`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/fixed_substrate_tranche_a_report.json`
- `m0_m3_classifier`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_classifier_m0_m3_validation.json`
- `m2_runtime_shape_blocked`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/m2_runtime_shape_blocked_fixture.json`
- `boundary_coupled_pulse_fixture`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_report.json`
- `m4_m5_classifier`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/loop_driven_movement_m4_m5_report.json`
- `lane_b_direction_parity`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_lane_b_direction_parity_closeout.json`
- `native_m6_validator`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_m6_same_fixture_validator.json`
- `native_m6_audit`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_m6_validation_checklist_audit.json`
- `d1_pulse_transport`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/pulse_conducting_substrate_baseline.json`
- `d2_local_geometry`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/pulse_local_geometry_coupling_report.json`
- `d3_traveling_deformation`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/traveling_deformation_audit.json`
- `d4_direction_controls`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/pulse_substrate_direction_null_controls.json`
- `d5_reclassification`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/pulse_substrate_movement_reclassification.json`
- `lane_c_feedback`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/reopened_m6_feedback_gate_report.json`
- `lane_c_feedback_surface`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/hybrid_lgrc_lane_c_feedback_surface_compatibility.json`
- `lane_e_hybrid_surface`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/hybrid_lgrc_pulse_substrate_surface_probe.json`
- `lane_f_native_surface`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_lane_f_native_surface_closeout.json`
- `iter15c_tolerance_profile`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter15c_s0_perturbation_tolerance_profile.json`
- `iter15d_shock_resistant_geometry`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter15d_shock_resistant_recovery_geometry_report.json`
- `iter15e_large_shock_absorber`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter15e_large_shock_absorber_geometry_report.json`
- `iter16_corridor_transfer`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter16_corridor_transfer_report.json`
- `iter16b_corridor_perturbation`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter16b_corridor_perturbation_probe.json`
- `iter16c_high_shock_corridor`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter16c_high_shock_corridor_resilience.json`
- `iter17_ring_transfer`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter17_ring_transfer_report.json`
- `iter17a_ring_unwrap_robustness`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter17a_ring_unwrap_robustness_report.json`
- `iter17b_circular_ring_motion`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter17b_circular_ring_motion_evidence_report.json`
- `iter17c_ring_geometry_closeout`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter17c_ring_geometry_closeout.json`
- `iter18_grid_transfer`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter18_grid_transfer_report.json`
- `iter18b_grid_two_axis_turn`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter18b_grid_two_axis_turn_report.json`
- `iter18c_grid_state_gated_routing`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter18c_grid_state_gated_routing_report.json`
- `iter18d_grid_geometry_selection`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter18d_grid_geometry_selection_report.json`
- `iter18e_composed_1d_fork_competition`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter18e_grid_composed_1d_fork_competition_report.json`
- `iter18f_balanced_local_preference_fork`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter18f_balanced_local_preference_fork_report.json`
- `iter18g_integrated_2d_composed_gate`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter18g_integrated_2d_composed_gate_report.json`
- `iter18h_s3_grid_series_closeout`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter18h_s3_grid_series_closeout.json`
- `iter19_s7_port_graph_mapping_contract`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19_s7_port_graph_mapping_contract.json`
- `iter19a_s7_fixed_port_execution`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19a_s7_fixed_port_execution_report.json`
- `iter19b_topology_lineage_adaptive_gate`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json`
- `iter19c_adaptive_gate_native_surface_lineage`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json`
- `iter19d_topology_mutating_movement_probe`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19d_topology_mutating_movement_probe.json`
- `iter19e_topology_mutating_after_reabsorption`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json`
- `iter20_topology_mutating_repeatability_stress`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter20_topology_mutating_repeatability_stress.json`
- `iter21_native_lgrc_choice_selection_boundary`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter21_native_lgrc_choice_selection_boundary.json`
- `iter21b_native_route_arbitration_rerun`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json`
- `iter22_identity_through_topology_mutation_boundary`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22_identity_through_topology_mutation_boundary.json`
- `iter22b_identity_through_native_route_arbitrated_topology`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json`

## Source Reports

- `fixed_substrate_tranche_a`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/fixed_substrate_tranche_a_report.md`
- `m0_m3_classifier`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_classifier_m0_m3_validation.md`
- `m2_runtime_shape_blocked`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/m2_runtime_shape_blocked_fixture.md`
- `boundary_coupled_pulse_fixture`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/boundary_coupled_pulse_report.md`
- `m4_m5_classifier`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/loop_driven_movement_m4_m5_report.md`
- `lane_b_direction_parity`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_lane_b_direction_parity_closeout.md`
- `native_m6_validator`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/native_m6_same_fixture_validator.md`
- `native_m6_audit`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/native_m6_validation_checklist_audit.md`
- `d1_pulse_transport`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/pulse_conducting_substrate_baseline.md`
- `d2_local_geometry`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/pulse_local_geometry_coupling_report.md`
- `d3_traveling_deformation`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/traveling_deformation_audit.md`
- `d4_direction_controls`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/pulse_substrate_direction_null_controls.md`
- `d5_reclassification`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/pulse_substrate_movement_reclassification.md`
- `lane_c_feedback`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/reopened_m6_feedback_gate_report.md`
- `lane_c_feedback_surface`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/hybrid_lgrc_lane_c_feedback_surface_compatibility.md`
- `lane_e_hybrid_surface`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/hybrid_lgrc_pulse_substrate_surface_probe.md`
- `lane_f_native_surface`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_lane_f_native_surface_closeout.md`
- `iter15c_tolerance_profile`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter15c_s0_perturbation_tolerance_profile.md`
- `iter15d_shock_resistant_geometry`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter15d_shock_resistant_recovery_geometry_report.md`
- `iter15e_large_shock_absorber`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter15e_large_shock_absorber_geometry_report.md`
- `iter16_corridor_transfer`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter16_corridor_transfer_report.md`
- `iter16b_corridor_perturbation`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter16b_corridor_perturbation_probe.md`
- `iter16c_high_shock_corridor`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter16c_high_shock_corridor_resilience.md`
- `iter17_ring_transfer`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter17_ring_transfer_report.md`
- `iter17a_ring_unwrap_robustness`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter17a_ring_unwrap_robustness_report.md`
- `iter17b_circular_ring_motion`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter17b_circular_ring_motion_evidence_report.md`
- `iter17c_ring_geometry_closeout`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter17c_ring_geometry_closeout.md`
- `iter18_grid_transfer`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter18_grid_transfer_report.md`
- `iter18b_grid_two_axis_turn`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter18b_grid_two_axis_turn_report.md`
- `iter18c_grid_state_gated_routing`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter18c_grid_state_gated_routing_report.md`
- `iter18d_grid_geometry_selection`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter18d_grid_geometry_selection_report.md`
- `iter18e_composed_1d_fork_competition`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter18e_grid_composed_1d_fork_competition_report.md`
- `iter18f_balanced_local_preference_fork`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter18f_balanced_local_preference_fork_report.md`
- `iter18g_integrated_2d_composed_gate`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter18g_integrated_2d_composed_gate_report.md`
- `iter18h_s3_grid_series_closeout`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter18h_s3_grid_series_closeout.md`
- `iter19_s7_port_graph_mapping_contract`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19_s7_port_graph_mapping_contract.md`
- `iter19a_s7_fixed_port_execution`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19a_s7_fixed_port_execution_report.md`
- `iter19b_topology_lineage_adaptive_gate`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19b_topology_lineage_adaptive_gate_report.md`
- `iter19c_adaptive_gate_native_surface_lineage`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.md`
- `iter19d_topology_mutating_movement_probe`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19d_topology_mutating_movement_probe.md`
- `iter19e_topology_mutating_after_reabsorption`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md`
- `iter20_topology_mutating_repeatability_stress`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter20_topology_mutating_repeatability_stress.md`
- `iter21_native_lgrc_choice_selection_boundary`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter21_native_lgrc_choice_selection_boundary.md`
- `iter21b_native_route_arbitration_rerun`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter21b_native_lgrc_route_arbitration_rerun.md`
- `iter22_identity_through_topology_mutation_boundary`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter22_identity_through_topology_mutation_boundary.md`
- `iter22b_identity_through_native_route_arbitrated_topology`: `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md`

## Supporting Visual References

Visuals are review/share references only and are not evidence sources.

- `m_taxonomy_visual_reference`: `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/m_taxonomy_visual_reference.json`

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_taxonomy_inventory_v1.py
```
