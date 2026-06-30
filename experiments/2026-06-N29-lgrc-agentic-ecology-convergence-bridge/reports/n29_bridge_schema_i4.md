# N29 Iteration 4 - Bridge Schema And Claim Boundary Freeze

## Summary

- status: `passed`
- acceptance_state: `accepted_bridge_schema_frozen_no_positive_prototypes`
- schema_version: `n29_bridge_schema_v1`
- schema_status: `frozen_for_phase_b`
- bridge_schema_frozen: `true`
- negative_fixture_rows: `10`
- positive_fixture_rows: `5`
- positive_prototype_rows_opened: `false`
- positive_ecology_evidence_opened: `false`
- ready_for_iteration_5: `true`
- output_digest: `e2e093b4cd143c1f5173391923d4707e2d2f9c48467b1e0c4052ba89d5b61131`

Iteration 4 closes Phase A by freezing the bridge schemas, enum values,
source-of-truth policy, controls, and blocked claim list. It does not build
coverage rows, motifs, prototype rows, or ecology evidence.

## Frozen Schema Sections

| Schema | Required Field Count |
| --- | --- |
| `ecology_demand_row_schema` | `9` |
| `capability_card_schema` | `13` |
| `coverage_debt_row_schema` | `16` |
| `bridge_motif_row_schema` | `14` |
| `prototype_row_schema` | `18` |
| `handoff_ledger_row_schema` | `11` |

## Frozen Enums

- coverage_status_enum: `source_backed, prototype_candidate, producer_mediated, medium_debt, naturalization_debt, native_ready_surface, control_only, blocked_relabel, missing_runtime_surface, not_applicable`
- motif_family_enum: `trace_pressure_loop, reserve_optionality_formation, boundary_shared_medium_unit, proxy_susceptibility_reentry, transfer_replay_role_relocation, generative_extractive_medium_reshaping, composition`
- prototype_status_enum: `runnable_runtime, source_backed_reconstruction, visual_diagnostic_only, mapping_only_no_runtime_surface, blocked_by_missing_source, blocked_by_claim_boundary`
- handoff_direction_enum: `outbound_to_agentic_ecology, inbound_to_n30_plus_core_primitives`

## Source Of Truth Policy

- capability_cards_are_full_data_source: `false`
- source_artifacts_required_for_full_data: `true`
- phase_b_c_rule: I5-I16 rows may use I3 cards as an index, but source-backed coverage, motif, prototype, and handoff claims must cite original artifacts or runtime records directly.

## Executable Gates

| Gate | Rejects |
| --- | --- |
| `source_backed_coverage_requires_original_artifact` | `only_I3_capability_card_cited` |
| `prototype_candidate_requires_full_data_source` | `motif_uses_mapping_only_or_card_only_source` |
| `visual_only_blocks_source_backed_claim` | `source_backed_or_native_ready_surface_claim` |

## Fixture Rows

Negative fixtures are fail-closed examples for source, producer, medium,
visual, composition, AP-gap, and prototype relabel failures. Positive
fixtures are schema-shape examples only; they open no ecology evidence.

| Fixture Family | Count | Claim Allowed |
| --- | --- | --- |
| `ap_gap_control` | `1` | `false` |
| `composition_control` | `1` | `false` |
| `medium_debt_control` | `1` | `false` |
| `motif_control` | `1` | `false` |
| `native_readiness_control` | `1` | `false` |
| `prototype_relabel_control` | `1` | `false` |
| `review_gate_control` | `1` | `false` |
| `source_of_truth_control` | `1` | `false` |
| `unsafe_ecology_relabel_control` | `1` | `false` |
| `visual_relabel_control` | `1` | `false` |

## Phase B Separation

| Iteration | Job | Must Not |
| --- | --- | --- |
| `I5` | `ecology_demand_matrix_only` | `import_N05_N28_evidence, match_demand_to_supply, create_bridge_motifs, open_prototype_rows` |
| `I6` | `capability_supply_atlas_only` | `create_coverage_debt_matches, create_bridge_motifs, open_prototype_rows` |
| `I7` | `demand_supply_coverage_debt_matching_only` | `create_bridge_motifs, open_prototype_rows, claim_native_ecology` |

## Blocked Claim Boundary

- `native_agency_claim_opened` = `false`
- `native_ant_agency_opened` = `false`
- `native_colony_agency_opened` = `false`
- `biological_agency_opened` = `false`
- `organism_life_opened` = `false`
- `consciousness_opened` = `false`
- `sentience_opened` = `false`
- `semantic_choice_claim_opened` = `false`
- `semantic_intention_claim_opened` = `false`
- `semantic_goal_claim_opened` = `false`
- `semantic_cooperation_claim_opened` = `false`
- `native_shared_medium_coordination_opened` = `false`
- `fully_native_ecology_opened` = `false`
- `phase8_completion_opened` = `false`
- `unrestricted_autonomy_opened` = `false`
- `prototype_as_native_ecology_opened` = `false`

## Checks

| Check | Passed |
| --- | --- |
| `i1_ecology_demand_model_passed` | `true` |
| `i2_agency_method_constraints_passed` | `true` |
| `i3_capability_atlas_passed` | `true` |
| `all_required_schema_sections_present` | `true` |
| `coverage_status_enum_complete` | `true` |
| `motif_family_enum_complete` | `true` |
| `prototype_status_enum_complete` | `true` |
| `source_of_truth_policy_requires_original_artifacts` | `true` |
| `blocked_claim_list_matches_claim_boundary_audit_keys` | `true` |
| `coverage_schema_matches_hypothesis_b_required_context` | `true` |
| `why_not_stronger_required_for_downstream_rows` | `true` |
| `unknown_field_policy_frozen` | `true` |
| `negative_fixture_rows_fail_closed` | `true` |
| `positive_fixture_rows_are_shape_only` | `true` |
| `phase_b_separation_rules_frozen` | `true` |
| `executable_source_of_truth_gates_frozen` | `true` |
| `cross_enum_rules_frozen` | `true` |
| `handoff_validation_rules_frozen` | `true` |
| `source_fidelity_audit_requires_original_sources_for_phase_b_claims` | `true` |
| `claim_boundary_flags_false` | `true` |
| `positive_prototypes_remain_closed` | `true` |
| `controls_fail_closed_policy_frozen` | `true` |
| `ready_for_iteration_5` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Interpretation

I4 is a schema freeze, not a positive evidence pass. It makes Phase B
safe to start by fixing the row shapes and enums that coverage/debt rows
must obey. Capability cards remain orientation records; later rows must
return to original experiment artifacts for full data.
