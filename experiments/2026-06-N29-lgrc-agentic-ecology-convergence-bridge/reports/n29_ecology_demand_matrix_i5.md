# N29 Iteration 5 - Ecology Demand Matrix

## Summary

- status: `passed`
- acceptance_state: `accepted_ecology_demand_matrix`
- demand rows: `30`
- current_lgrc_grc_surface_evaluation_status: `deferred_to_iteration_6_and_7`
- n05_n28_evidence_imported: `false`
- coverage_status_assigned: `false`
- demand_supply_matching_opened: `false`
- bridge_motifs_created: `false`
- prototype_rows_opened: `false`
- ready_for_iteration_6: `true`
- output_digest: `2503831622cdfc99d9f6083bfc841481a06c6fd67bcba1a9ad840c1e1c069fe9`

Iteration 5 is demand-only. It turns I1 ecology target demands into a
grouped matrix of required dynamics, state surfaces, trace surfaces, and
controls. It does not import N05-N28 capability evidence, perform supply
matching, create motifs, or open prototype rows.

## Demand Groups

| Group | Demand Count | Description |
| --- | ---: | --- |
| `parent_basin_and_subbasin` | 3 | parent/colony/nest context, modulation, and contained sub-basin surfaces |
| `shared_medium_and_medium_surface` | 4 | shared medium, medium surface, message scaffold, and medium debt target surfaces |
| `trace_pressure_and_affordance` | 7 | trace, pressure, route support, affordance, reserve, and alarm surfaces |
| `susceptibility_and_resonance` | 4 | susceptibility, cargo-shaped response, resonance, and role-capture surfaces |
| `perturbation_co_response_loop` | 3 | perturbation, co-response, and parent-modulation loop target surfaces |
| `role_labor_and_task_differentiation` | 6 | role, labor, isolation, construction, congestion, and mobile-boundary target surfaces |
| `reserve_surplus_and_reproduction_split` | 3 | resource, reserve, surplus, and split/reproduction target surfaces |
| `debt_and_naturalization_conditions` | 4 | producer residue, medium debt, scaffold, and naturalization-condition demand rows |

## Surface Inventory

- unique state surfaces: `75`
- unique trace surfaces: `59`
- unique controls: `60`
- unique blocked relabels: `59`

## Source Index

| Source | Demand Count |
| --- | ---: |
| `FromStateToBecoming` | 2 |
| `RCAgenticEcology` | 16 |
| `README` | 9 |
| `SharedMediumCoordinationSpec` | 21 |
| `TheSharedMedium` | 9 |

## Recurring Runtime Surfaces

| Kind | Top Entries |
| --- | --- |
| State | `reserve_condition` (2), `cost_surface` (2), `reserve_deficit` (2), `target_medium_surface` (2), `nest_reserve` (2) |
| Trace | `local_shift_trace` (2), `event_history` (1), `parent_pressure_trace` (1), `trace_field` (1), `pressure_field` (1) |
| Control | `parent_label_only_relabel_control` (1), `central_controller_as_parent_basin_control` (1), `direct_message_scaffold_control` (1), `hidden_global_variable_control` (1), `surface_label_only_control` (1) |
| Blocked relabel | `native_colony_agency` (2), `central_manager_as_parent_basin` (1), `native_shared_medium_coordination` (1), `message_bus_as_medium` (1), `surface_annotation_as_native_medium` (1) |

## Unresolved Demand Ledger

All I5 demand rows remain unresolved until I6/I7 by design. The JSON
contains the full ledger; this report lists the first probe clusters
through the family index rather than a flat Cartesian table.

| Family | Demand IDs |
| --- | --- |
| `parent_basin_and_subbasin` | `general_parent_basin, rc_ant_colony_parent_basin, rc_ant_nest_home_basin` |
| `shared_medium_and_medium_surface` | `general_shared_medium, general_medium_surface, general_message_scaffold, general_medium_debt` |
| `trace_pressure_and_affordance` | `general_trace, general_pressure, rc_ant_route_support_trace, rc_ant_foodward_affordance_surface, rc_ant_homeward_affordance_surface, rc_ant_reserve_hunger_pressure, rc_ant_alarm_threat_pressure` |
| `susceptibility_and_resonance` | `general_susceptibility, general_resonance, rc_ant_cargo_shaped_susceptibility, rc_ant_role_susceptibility_division_of_labor` |
| `perturbation_co_response_loop` | `general_perturbation, general_co_response, general_parent_basin_modulation` |
| `role_labor_and_task_differentiation` | `rc_ant_mobile_boundary_expression, rc_ant_nursery_demand, rc_ant_waste_isolation, rc_ant_construction_tension, rc_ant_crowding_congestion_cost, rc_ant_role_susceptibility_division_of_labor` |
| `reserve_surplus_and_reproduction_split` | `rc_ant_food_resource_coupling, rc_ant_reserve_hunger_pressure, rc_ant_surplus_supported_split_reproduction` |
| `debt_and_naturalization_conditions` | `general_message_scaffold, general_medium_debt, general_producer_residue, general_naturalization_condition` |

## Checks

| Check | Passed |
| --- | --- |
| `i1_ecology_demand_model_passed` | `true` |
| `i2_agency_method_constraints_passed` | `true` |
| `i4_bridge_schema_passed` | `true` |
| `i1_source_digest_matches` | `true` |
| `uses_i1_as_only_demand_source` | `true` |
| `i2_used_only_for_blocked_claim_language` | `true` |
| `i5_phase_b_separation_rule_consumed` | `true` |
| `only_i1_i2_i4_sources_consumed` | `true` |
| `demand_row_count_matches_i1` | `true` |
| `all_i4_ecology_demand_schema_fields_present` | `true` |
| `all_i5_row_extensions_are_namespaced` | `true` |
| `required_group_families_present` | `true` |
| `every_demand_has_runtime_surfaces_and_controls` | `true` |
| `all_rows_have_claim_ceiling_target_requirement_only` | `true` |
| `all_rows_have_blocked_relabels` | `true` |
| `current_surfaces_marked_unresolved_pending_i6_i7` | `true` |
| `all_rows_with_missing_surfaces_enter_unresolved_ledger` | `true` |
| `source_roles_are_target_requirement_not_evidence` | `true` |
| `coverage_status_assigned_false` | `true` |
| `i3_capability_matching_attempted_false` | `true` |
| `no_n05_n28_evidence_imported` | `true` |
| `no_demand_supply_matching_or_coverage_rows_opened` | `true` |
| `no_bridge_motifs_or_prototype_rows_opened` | `true` |
| `positive_ecology_and_implementation_evidence_closed` | `true` |
| `native_shared_medium_coordination_opened_false` | `true` |
| `native_ant_and_colony_agency_opened_false` | `true` |
| `phase8_completion_opened_false` | `true` |
| `claim_boundary_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
| `ready_for_iteration_6` | `true` |

## Interpretation

I5 supports the ecology demand matrix as a target-requirement artifact.
All rows remain unresolved as of I5 because the phase boundary forbids
current LGRC/GRC coverage evaluation until I6/I7. This is intentional:
I5 defines what the ecology side asks for; it does not answer what the
N05-N28 stack can supply.
