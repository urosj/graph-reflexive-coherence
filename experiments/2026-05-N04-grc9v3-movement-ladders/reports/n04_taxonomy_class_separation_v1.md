# N04 Iteration 14 Taxonomy Class Separation

Status: **passed**

Claim ceiling: `taxonomy_schema_freeze_only`

Iteration 14 freezes class boundaries and tag fields. It does not run new probes or promote claims.

## Checks

- `inventory_status_passed`: `True`
- `centroid_displacement_separated`: `True`
- `boundary_response_separated`: `True`
- `traveling_deformation_separated`: `True`
- `same_fixture_self_renewal_separated`: `True`
- `fixed_topology_separated`: `True`
- `tag_schema_frozen`: `True`
- `orthogonal_readme_tags_declared`: `True`
- `persistence_enum_complete`: `True`
- `orthogonal_values_not_backfilled_from_unmeasured_artifacts`: `True`
- `m1_m3_origin_recorded`: `True`
- `implementation_surface_transition_documented`: `True`
- `d_to_m_projection_rules_frozen`: `True`
- `d5_runtime_basin_promotion_blocked`: `True`
- `claim_boundary_rules_frozen`: `True`
- `invalid_combinations_declared`: `True`
- `current_inventory_rows_validate_under_schema`: `True`
- `visual_sources_rejected`: `True`
- `same_fixture_m6_locomotion_invalid`: `True`
- `m6_feedback_level_conservative`: `True`
- `measured_identity_levels_assigned`: `True`
- `frozen_rows_retain_source_provenance`: `True`
- `m6_resilience_extension_tags_frozen`: `True`
- `fixture_topology_tag_frozen`: `True`
- `iter16_corridor_transfer_tags_frozen`: `True`
- `iter16b_corridor_perturbation_tags_frozen`: `True`
- `iter16c_high_shock_capacity_tags_frozen`: `True`
- `iter17_ring_transfer_tags_frozen`: `True`
- `iter17a_ring_unwrap_robustness_tags_frozen`: `True`
- `iter17b_circular_ring_motion_tags_frozen`: `True`
- `iter17c_ring_geometry_closeout_tags_frozen`: `True`
- `iter18_grid_transfer_tags_frozen`: `True`
- `iter18b_grid_two_axis_turn_tags_frozen`: `True`
- `iter18c_grid_state_gated_routing_tags_frozen`: `True`
- `iter18d_grid_geometry_selection_tags_frozen`: `True`
- `iter18e_composed_1d_fork_competition_tags_frozen`: `True`
- `iter18f_balanced_local_preference_fork_tags_frozen`: `True`
- `iter18g_integrated_2d_composed_gate_tags_frozen`: `True`
- `iter18h_s3_grid_series_closeout_tags_frozen`: `True`
- `iter19_s7_mapping_contract_tags_frozen`: `True`
- `iter19a_s7_fixed_port_execution_tags_frozen`: `True`
- `iter19b_topology_lineage_boundary_tags_frozen`: `True`
- `iter19c_adaptive_topology_entry_tags_frozen`: `True`
- `iter19d_topology_mutating_movement_boundary_tags_frozen`: `True`
- `iter19e_topology_mutating_movement_candidate_tags_frozen`: `True`
- `iter20_topology_mutating_repeatability_stress_tags_frozen`: `True`
- `iter21_native_lgrc_choice_selection_boundary_tags_frozen`: `True`
- `iter21b_native_route_arbitration_support_tags_frozen`: `True`
- `iter22_identity_through_topology_mutation_boundary_tags_frozen`: `True`
- `iter22b_identity_through_native_route_arbitrated_topology_boundary_tags_frozen`: `True`
- `no_claim_promotion`: `True`

## Class Separation Rules

- `centroid_displacement_not_identity_movement`: Current M1 rows are classifier/observable-fixture controls, not empirical native runtime movement lanes.
- `boundary_response_not_basin_movement`: M4/M5 boundary-response rows are real boundary-fixture evidence, but remain separate from basin-identity movement.
- `traveling_deformation_not_runtime_basin`: Lane D rows stay first-class deformation evidence and cannot be collapsed into M-level basin movement.
- `same_fixture_self_renewal_not_locomotion`: Current M6 is bounded native same-fixture S0 evidence. It is not topology transfer, adaptive topology, or locomotion-like behavior.
- `fixed_topology_not_topology_mutating`: All Iteration 13 rows remain fixed-topology/same-fixture evidence until Iterations 16-19 explicitly transfer geometry or open topology controls.

## D-To-M Projection Rules

- `D0` -> `M0`; promotion=`False`; blocker=`no_deformation`
- `D1` -> `None`; promotion=`False`; blocker=`no_boundary_coordination`
- `D2` -> `M4`; promotion=`candidate_only`; blocker=`local_geometry_response_not_boundary_movement`
- `D3` -> `M5`; promotion=`candidate_only`; blocker=`deformation_surface_is_not_runtime_coherence_basin`
- `D4` -> `M3_shape_gate_analog`; promotion=`False`; blocker=`shape_profile_analog_not_direct_m3_promotion`
- `D5` -> `M5_style_control_evidence`; promotion=`False`; blocker=`deformation_token_not_runtime_coherence_basin`

## Claim Boundary Rules

- `tags_are_descriptors_not_claims`: Taxonomy tags describe evidence surfaces and gates. They do not set movement, locomotion, adaptive-topology, agency, biology, or identity-acceptance claim flags.
- `blocked_claims_are_row_local`: A row may inherit global blocked claims, but stronger evidence in one row does not unblock claims in another row.
- `visual_references_are_not_sources`: Visual reference artifacts may support review, but cannot be used as source_artifacts for taxonomy evidence rows.
- `m6_same_fixture_requires_locomotion_block`: A same_fixture M6 row must keep locomotion-like, adaptive topology, and unrestricted movement claims blocked unless a later closeout explicitly opens them.
- `deformation_token_blocks_strict_movement`: A deformation_token row on deformation_surface cannot allow strict runtime coherence-basin movement.

## Invalid Combinations

- `deformation_token_strict_movement_claim`: expected=`invalid`, blocker=`deformation_token_not_runtime_coherence_basin`
- `d5_deformation_without_projection_blocker`: expected=`invalid`, blocker=`d5_requires_runtime_basin_blocker`
- `same_fixture_m6_locomotion_claim`: expected=`invalid_without_later_closeout`, blocker=`same_fixture_self_renewal_not_locomotion`
- `adaptive_topology_claim_without_topology_scope`: expected=`invalid`, blocker=`fixed_topology_not_topology_mutating`
- `visual_reference_as_source_artifact`: expected=`invalid`, blocker=`visual_reference_not_authoritative`

## Orthogonal Taxonomy Policy

Iteration 14 freezes fields before geometry probes. It does not infer unmeasured R/B/G/Q/F/H/E levels from visuals or prose.

## Conservative Assignments

- Current same-fixture M6 uses `feedback_level = F2`, not `F5`, because feedback-triggered regenerated pulse work is supported while closed locomotion-like cycle claims remain blocked.
- Identity continuity is assigned only where current source artifacts explicitly measured identity/mass or identity/shape gates.

## M6 Resilience And Transfer Extension Tags

The 15-C/15-D/15-E and Iteration 16 rows are frozen as M6 resilience/transfer extensions with scoped claim ceilings. They remain descriptors of evidence, not broad movement or locomotion claims.

| Row | Persistence | Geometry | R | Feedback | Claim ceiling |
|---|---|---|---|---|---|
| `M6_s0_perturbation_tolerance_profile` | `tested_negative` | `same_fixture` | `R6` | `F2` | `s0_same_fixture_perturbation_tolerance_profile` |
| `M6_shock_resistant_same_family_geometry_recovery_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `shock_resistant_same_family_geometry_recovery_candidate` |
| `M6_large_shock_absorber_same_family_recovery_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `large_shock_absorber_same_family_recovery_candidate` |
| `M6_s4_corridor_transfer_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s4_corridor_m6_transfer_candidate` |
| `M6_s4_corridor_perturbation_envelope` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s4_corridor_perturbation_envelope_profile` |
| `M6_s4_corridor_high_shock_capacity_requirement` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s4_corridor_high_shock_capacity_requirement_probe` |
| `M6_s1_ring_declared_unwrap_transfer_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s1_ring_m6_transfer_candidate_under_declared_unwrap` |
| `M6_s1_ring_unwrap_robust_transfer_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s1_ring_unwrap_robust_transfer_candidate` |
| `M6_s1_ring_circular_motion_evidence_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s1_ring_circular_motion_evidence_candidate` |
| `M6_s1_ring_circular_motion_with_unwrap_robustness_closeout` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness` |
| `M6_s3_grid_route_defined_transfer_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s3_grid_route_defined_m6_transfer_candidate` |
| `M6_s3_grid_two_axis_turn_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s3_grid_two_axis_turn_m6_transfer_candidate` |
| `M6_s3_grid_state_gated_routing_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s3_grid_state_gated_two_input_two_output_routing_candidate` |
| `M6_s3_grid_geometry_scored_selection_design_prototype` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s3_grid_geometry_scored_selection_design_prototype` |
| `M6_s3_grid_composed_1d_fork_competition_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s3_grid_composed_1d_fork_competition_candidate` |
| `M6_s3_grid_balanced_local_preference_fork_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s3_grid_balanced_local_preference_fork_competition_candidate` |
| `M6_s3_grid_integrated_2d_composed_gate_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s3_grid_integrated_2d_composed_gate_candidate` |
| `M6_s3_grid_series_closeout_fixed_topology_2d_gate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s3_grid_integrated_2d_composed_gate_candidate` |
| `M6_s7_fixed_port_composed_gate_candidate` | `T6_candidate` | `transferred_geometry` | `R6` | `F2` | `s7_fixed_port_composed_gate_candidate` |

## Implementation Surface Transition

| Surface | Claim limit |
|---|---|
| `mapped_e3_fixture` | `fixture_validation_not_native_runtime_movement` |
| `native_lgrc_telemetry` | `direction_parity_boundary_response_not_locomotion` |
| `native_causal_pulse_substrate_surface` | `same_fixture_self_renewal_not_adaptive_topology` |
| `native_causal_pulse_substrate_surface_plus_topology_state_reabsorption` | `topology_mutating_movement_candidate_not_identity_or_choice` |
| `native_route_arbitration_plus_surface_lineage_and_topology_state_reabsorption` | `native_route_arbitration_not_semantic_choice_or_identity_acceptance` |

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_taxonomy_tag_schema_v1.py
```
