# N29 Iteration 1 - Ecology Demand Extraction

## Summary

- Status: `passed`
- Acceptance state: `accepted_ecology_demand_model_no_implementation_claims`
- Source count: `5`
- General demand rows: `14`
- RC-Ant demand rows: `16`
- Output digest: `509f808f69b6ac33682c1f4396fd8a421d6d9372130c8edc357e102bb7b513e3`
- Ready for Iteration 2: `true`

Iteration 1 extracts ecology demands as target requirements only. It does not match
those demands to N05-N28 capability evidence, does not open prototype rows, and
does not claim implementation evidence from the ecology repository.

## Source Role Audit

| Source | Role | Exists | Digest policy | Claim ceiling |
| --- | --- | --- | --- | --- |
| `reflexive-coherence-agentic-ecology/README.md` | `target_orientation_and_claim_boundary_source` | `true` | `sha256_of_external_target_source` | `target_requirement_and_vocabulary_source_only` |
| `reflexive-coherence-agentic-ecology/papers/2026-06-FromStateToBecoming.md` | `state_to_geometry_transition_method_source` | `true` | `sha256_of_external_target_source` | `target_requirement_and_vocabulary_source_only` |
| `reflexive-coherence-agentic-ecology/papers/2026-06-RC-AgenticEcology.md` | `rc_ant_worked_domain_target_source` | `true` | `sha256_of_external_target_source` | `target_requirement_and_vocabulary_source_only` |
| `reflexive-coherence-agentic-ecology/papers/2026-06-TheSharedMedium.md` | `shared_medium_transition_method_source` | `true` | `sha256_of_external_target_source` | `target_requirement_and_vocabulary_source_only` |
| `reflexive-coherence-agentic-ecology/papers/2026-06-SharedMediumCoordination-EngineeringSpec.md` | `shared_medium_engineering_vocabulary_source` | `true` | `sha256_of_external_target_source` | `target_requirement_and_vocabulary_source_only` |

## Demand Row Counts

| Family | Count |
| --- | ---: |
| General ecology demands | 14 |
| RC-Ant worked-domain demands | 16 |
| Total | 30 |

## General Demand Rows

| Demand | Component | First probe relevance |
| --- | --- | --- |
| `general_parent_basin` | `parent_basin` | required for any colony-level or shared-medium probe |
| `general_shared_medium` | `shared_medium` | central surface for relation and coordination probes |
| `general_medium_surface` | `medium_surface` | needed before medium participation can be probed |
| `general_perturbation` | `perturbation` | required for any shared-medium cause/effect probe |
| `general_trace` | `trace` | basis for route-support and aftereffect prototypes |
| `general_pressure` | `pressure` | basis for reserve/hunger and threat-pressure probes |
| `general_susceptibility` | `susceptibility` | required for role and differentiated-response probes |
| `general_co_response` | `co_response` | needed for shared-medium coordination probes |
| `general_resonance` | `resonance` | useful for distinguishing shared perturbation from arbitrary signal |
| `general_parent_basin_modulation` | `parent_basin_modulation` | needed for colony-demand and reserve-pressure probes |
| `general_message_scaffold` | `message_scaffold` | needed when early ecology probes require explicit relation scaffolds |
| `general_medium_debt` | `medium_debt` | required for all message-mediated ecology prototypes |
| `general_producer_residue` | `producer_residue` | required for any ecology probe using scaffolding |
| `general_naturalization_condition` | `naturalization_condition` | defines when future ecology behavior can become native claim |

## RC-Ant Demand Rows

| Demand | Component | First probe relevance |
| --- | --- | --- |
| `rc_ant_colony_parent_basin` | `colony_parent_basin` | root demand for RC-Ant-style probe |
| `rc_ant_mobile_boundary_expression` | `mobile_boundary_expression` | needed for any mobile ecology element |
| `rc_ant_nest_home_basin` | `nest_home_basin` | needed for food-return and reserve probes |
| `rc_ant_food_resource_coupling` | `food_resource_coupling` | basis for resource-coupling probe |
| `rc_ant_route_support_trace` | `route_support_trace` | central trace/aftereffect prototype demand |
| `rc_ant_foodward_affordance_surface` | `foodward_affordance_surface` | needed for foraging-like probe without goal labels |
| `rc_ant_homeward_affordance_surface` | `homeward_affordance_surface` | needed for food-return/cargo probe |
| `rc_ant_cargo_shaped_susceptibility` | `cargo_shaped_susceptibility` | needed for support transport and role-capture probes |
| `rc_ant_reserve_hunger_pressure` | `reserve_hunger_pressure` | pressure/reserve prototype demand |
| `rc_ant_alarm_threat_pressure` | `alarm_threat_pressure` | tests pressure/co-response under boundary perturbation |
| `rc_ant_nursery_demand` | `nursery_demand` | role susceptibility and demand-field probe |
| `rc_ant_waste_isolation` | `waste_isolation` | negative-basin and leakage-control probe |
| `rc_ant_construction_tension` | `construction_tension` | tests geometry modification as ecology demand |
| `rc_ant_crowding_congestion_cost` | `crowding_congestion_cost` | shared cost surface and co-response probe |
| `rc_ant_role_susceptibility_division_of_labor` | `role_susceptibility_division_of_labor` | role differentiation and susceptibility probe |
| `rc_ant_surplus_supported_split_reproduction` | `surplus_supported_split_reproduction` | future reproduction/split probe target, not I1 evidence |

## Checks

| Check | Passed |
| --- | --- |
| `all_five_target_ecology_sources_inventoried` | `true` |
| `source_roles_are_target_not_implementation_evidence` | `true` |
| `general_demand_families_complete` | `true` |
| `rc_ant_component_demand_families_complete` | `true` |
| `every_demand_row_has_source_role_and_reference` | `true` |
| `implementation_evidence_closed_per_row` | `true` |
| `no_n05_n28_capability_coverage_claimed` | `true` |
| `no_prototype_rows_opened` | `true` |
| `no_positive_ecology_evidence_opened` | `true` |
| `producer_residue_and_naturalization_debt_visible` | `true` |
| `medium_debt_visible` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

All blocked claim flags remain `false`. The ecology repository sources are
consumed as demand, vocabulary, target ontology, and claim-boundary sources
only.

Closeout interpretation:

```text
Iteration 1 supports an ecology demand model extracted from RC-agentic-ecology sources as target requirements only. It opens no implementation evidence, no positive ecology evidence, no prototype rows, and no native ant, colony, biological, sentience, or Phase 8 claim.
```
