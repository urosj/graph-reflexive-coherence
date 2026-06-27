# N24 Iteration 2 - Abundance Schema And Controls

## Summary

Status: `passed`

Acceptance state: `accepted_abundance_schema_and_controls_frozen_no_surplus_optionality_evidence`

Output digest: `df1725c0e726ad233bd57751393e7aa6b0bcf18f7a0d67cdf220e8e3e0e6c503`

Iteration 2 freezes the N24 candidate evidence schema, surplus
formulas, optionality acceptance gates, control matrix, ladders,
AP gap discipline, and claim boundary. It opens no N24 primitive
evidence and assigns no AB rung.

## Source Artifacts

| Role | Path | Status | SHA-256 |
| --- | --- | --- | --- |
| n24_i1_source_handoff_inventory | `experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/outputs/n24_source_handoff_inventory.json` | `passed` | `ee62e0c2152019d0731ff7c40fd9068ca3c5f610c9fc45bf24c0dd7026462627` |
| n24_i1_source_handoff_report | `experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/reports/n24_source_handoff_inventory.md` | `markdown_context_only` | `ce656892e9e378e0d6a74ecfda27967eacbf197f18190c80f1b045b810a5d1bb` |
| n20_i4_native_function_proxy_contract | `experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_native_function_proxy_contract.json` | `passed` | `23e87346e05bb32347630b7ea3c688bf83096dfdb9ca11f99a35a82a2e602760` |
| n20_i5_same_basin_contract | `experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_same_basin_continuation_contract.json` | `passed` | `72c4297b923a5dc0226e67be97ff368d0b586278f8b93ef4bd6fa7b79d1fb4d0` |
| n23_closeout_and_n24_handoff_context | `experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_closeout_and_n24_handoff.json` | `passed` | `469f00b25d8bc7d56a582ffd7f9dbbe313d064c8ef9d54eaf98ba86688040eef` |

## I1 Reference

```text
i1_status = passed
i1_acceptance_state = accepted_source_handoff_inventory_no_surplus_optionality_evidence
i1_output_digest = f9293344b8ca23ec14438c3762cd681d9543aaa528f45182b638631af7abde57
n23_closeout_validated = true
n23_context_consumption = n23_bridge_candidate_consumed
```

## Frozen Contract Digests

```text
source_contract_row = n20_i4_row_05_surplus_supported_optionality
source_contract_row_digest = 7f962755c36a8ae6b0acdc831bbdcbecdc6ed6169ac8d7176954cbd900cede84
source_consumable_contract_row = n20_i5_row_05_surplus_supported_optionality
source_consumable_contract_row_digest = daf53d4eed625cbdda0c391a5371748859f89552ce4bd3bd8aff6f55132e3233
digests_are_distinct = true
```

## Core Freeze

```text
candidate_evidence_required_field_count = 104
AB ladder frozen = true
N24-C ladder frozen = true
surplus formulas frozen = true
optional branch record schema frozen = true
original optional set same-run only = true
declared replay family cannot create AB3 original set = true
surplus budget owner rung ceilings frozen = true
final_global_ap4_reclassification_supported = false
unsafe claim flags false = true
```

## Surplus Formulas

```text
support_surplus_margin = observed_support - support_floor_value
coherence_surplus_margin = observed_coherence - coherence_floor_value
residual_support_margin_under_optionality = min_support_during_optionality_window - support_floor_value
residual_coherence_margin_under_optionality = min_coherence_during_optionality_window - coherence_floor_value
optional_flux_drain_margin = flux_or_leakage_bound - observed_optional_flux_drain
```

## Required Controls

```text
hidden_budget_relief_control
floor_crossing_as_abundance_control
surplus_without_optional_continuation_control
optionality_without_surplus_control
proxy_only_optional_branch_gain_control
optional_branch_label_only_control
single_optional_branch_relabel_control
independent_run_optional_assembly_control
maintenance_basin_shift_control
floor_renormalization_as_surplus_control
post_hoc_surplus_construction_control
n23_selection_context_relabel_as_abundance_control
reward_maximization_relabel_control
semantic_choice_relabel_control
agency_relabel_control
native_support_relabel_control
phase8_relabel_control
ap4_final_reclassification_relabel_control
ap5_proxy_gap_omission_control
```

## Evidence Boundary

```text
primitive_evidence_opened = false
surplus_supported_optionality_supported = false
ab_ladder_rung_assigned = false
n24_closeout_ladder_rung_assigned = false
candidate_rows_classified = false
ready_for_iteration_3_active_nulls = true
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_inventory_consumed_and_passed` | `true` | {"ab_ladder_rung_assigned":false,"acceptance_state":"accepted_source_handoff_inventory_no_surplus_optionality_evidence","n23_closeout_validated":true,"n23_context_consumption":"n23_bridge_candidate_consumed","output_digest":"f9293344b8ca23ec14438c3762cd681d9543aaa528f45182b638631af7abde57","path":"experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/outputs/n24_source_handoff_inventory.json","status":"passed"} |
| `n23_closeout_context_gate_preserved` | `true` | {"claim_ceiling":"bounded artifact-level live-continuation collapse / selection-geometry evidence, N24-ready; not semantic choice, agency, native support, sentience, Phase 8, or ant ecology implementation","consumption_boundary":"bounded LC6/N23-C6 selection-geometry context only; not N24 surplus, optionality, reward, choice, agency, native support, sentience, Phase 8, or ant ecology evidence","final_global_ap4_reclassification_supported":false,"final_n23_closeout_ladder_rung":"N23-C6","final_supported_lc_ladder_rung":"LC6","n23_ap4_bridge_status":"bridge_candidate_supported","n23_closeout_artifact_present":true,"n23_closeout_required":true,"n23_closeout_validated":true,"n23_context_consumption":"n23_bridge_candidate_consumed","n23_source_ap4_bridge_status":"bridge_candidate_supported","n23_source_closeout_acceptance_state":"accepted_n23_lc6_closeout_n24_handoff_ready","n23_source_closeout_status":"passed","n24_claim_ceiling":"source inventory only; bounded N23 bridge context available","n24_may_consume_as":["bounded_live_branch_set_and_collapse_evidence","counterfactual_retention_evidence","ap4_bridge_candidate_context","bounded_selection_geometry_context"],"n24_must_not_consume_as":["semantic_choice","semantic_intention","agency","free_will","native_support","sentience","Phase8_implementation","ant_ecology_implementation"],"ready_for_n24":true,"source_artifact":"experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_closeout_and_n24_handoff.json"} |
| `candidate_schema_required_fields_complete` | `true` | {"i1_required_future_fields":["source_current_inputs","row_specific_thresholds_declared_before_use","maintenance_floor_policy","support_floor_value","coherence_floor_value","boundary_integrity_floor_value","flux_or_leakage_bound","optionality_window","support_surplus_margin_trace","coherence_surplus_margin_trace","residual_support_margin_under_optionality","residual_coherence_margin_under_optionality","optional_flux_drain_margin","maintenance_floor_trace","optional_continuation_set_trace","optional_continuation_availability_count","jointly_admissible_optional_continuation_count","optional_branch_records","boundary_integrity_under_optionality_trace","optional_flux_does_not_drain_maintenance_support","surplus_budget_owner","hidden_budget_relief_absent","same_basin_continuation_rule","artifact_manifest","artifact_sha256","all_artifact_sha256_match_file_contents"],"required_field_count":104} |
| `direct_n23_closeout_source_recorded` | `true` | [{"acceptance_state":"accepted_n23_lc6_closeout_n24_handoff_ready","output_digest":"f890de4685a08a1735cc1cac8e752b2f98d0cc7ab26ec268a6e516b47e2a5ef1","path":"experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_closeout_and_n24_handoff.json","sha256":"469f00b25d8bc7d56a582ffd7f9dbbe313d064c8ef9d54eaf98ba86688040eef","source_role":"n23_closeout_and_n24_handoff_context","status":"passed"}] |
| `source_contract_digests_split` | `true` | {"digests_are_distinct":true,"source_consumable_contract_row":"n20_i5_row_05_surplus_supported_optionality","source_consumable_contract_row_digest":"daf53d4eed625cbdda0c391a5371748859f89552ce4bd3bd8aff6f55132e3233","source_contract_row":"n20_i4_row_05_surplus_supported_optionality","source_contract_row_digest":"7f962755c36a8ae6b0acdc831bbdcbecdc6ed6169ac8d7176954cbd900cede84"} |
| `surplus_formulas_frozen` | `true` | {"coherence_surplus_margin":"observed_coherence - coherence_floor_value","optional_flux_drain_margin":"flux_or_leakage_bound - observed_optional_flux_drain","residual_coherence_margin_under_optionality":"min_coherence_during_optionality_window - coherence_floor_value","residual_support_margin_under_optionality":"min_support_during_optionality_window - support_floor_value","support_surplus_margin":"observed_support - support_floor_value"} |
| `optional_branch_record_schema_frozen` | `true` | {"admissibility_status_values":["admissible","blocked_by_floor","blocked_by_boundary","blocked_by_flux","blocked_by_label_only","blocked_by_independent_run_assembly","blocked_by_hidden_budget"],"optional_branch_evidence_mode_rung_effects":{"deterministic_replay_validation":"eligible for AB4+ as replay validation","source_current_available_unexecuted":"can support AB3 if same-window and floors hold","source_current_cost_projection":"can support only bounded/provisional AB3 unless replay validates it","source_current_executed":"eligible for AB4+ if replay/control gates pass"},"optional_branch_evidence_mode_values":["source_current_available_unexecuted","source_current_executed","source_current_cost_projection","deterministic_replay_validation"],"producer_enumeration_used_is_producer_residue":true,"required_fields":["branch_id","source_node_id","target_node_id","edge_id_or_route_id","trace_origin","trace_status","optionality_window_step_range","support_before","support_after_or_projected_after","coherence_before","coherence_after_or_projected_after","support_surplus_margin_before","support_surplus_margin_after","coherence_surplus_margin_before","coherence_surplus_margin_after","boundary_integrity_result","flux_or_leakage_result","optional_flux_cost","maintenance_floor_preserved","reward_or_proxy_label_used","producer_enumeration_used","admissibility_status"],"reward_or_proxy_label_used_must_be_false_for_support":true,"trace_origin_allowed_values":["source_current_same_run","deterministic_replay_of_source_run","declared_replay_family","producer_label","report_derived","independent_run_assembly"],"trace_status_allowed_values":["present","missing","not_applicable"]} |
| `source_current_inputs_split_from_required_fields` | `true` | {"source_current_inputs":{"constraint":"actual LGRC runtime, replay, snapshot, event-log, optional branch, or trace artifact inputs consumed by this row; not limited to the canonical primitive fields","type":"list[string]"},"source_current_required_fields":{"constraint":"canonical N20 surplus-supported optionality fields that candidate rows must map from their source_current_inputs","required_values":["surplus_supported_optionality.support_surplus_margin_trace","surplus_supported_optionality.optional_continuation_set_trace","surplus_supported_optionality.maintenance_floor_trace","surplus_supported_optionality.boundary_integrity_under_optionality_trace"],"type":"list[string]"}} |
| `surplus_channel_policy_frozen` | `true` | {"allowed_values":["support_surplus_required_and_coherence_floor_preserved","support_and_coherence_surplus_required","support_or_coherence_surplus_with_other_floor_preserved"],"constraint":"AB2 requires support surplus above floor while coherence floor remains preserved","required_value":"support_surplus_required_and_coherence_floor_preserved","type":"enum"} |
| `optional_branch_evidence_mode_frozen` | `true` | {"deterministic_replay_validation":"eligible for AB4+ as replay validation","source_current_available_unexecuted":"can support AB3 if same-window and floors hold","source_current_cost_projection":"can support only bounded/provisional AB3 unless replay validates it","source_current_executed":"eligible for AB4+ if replay/control gates pass"} |
| `control_results_record_schema_frozen` | `true` | {"constraint":"failed_open invalidates row; not_run blocks dependent rung","required_control_ids":["hidden_budget_relief_control","floor_crossing_as_abundance_control","surplus_without_optional_continuation_control","optionality_without_surplus_control","proxy_only_optional_branch_gain_control","optional_branch_label_only_control","single_optional_branch_relabel_control","independent_run_optional_assembly_control","maintenance_basin_shift_control","floor_renormalization_as_surplus_control","post_hoc_surplus_construction_control","n23_selection_context_relabel_as_abundance_control","reward_maximization_relabel_control","semantic_choice_relabel_control","agency_relabel_control","native_support_relabel_control","phase8_relabel_control","ap4_final_reclassification_relabel_control","ap5_proxy_gap_omission_control"],"required_item_fields":["control_id","control_status","blocked_condition","expected_result","actual_result","claim_allowed_when_control_triggers","control_satisfied_for_positive_row","rung_effect"],"status_values":["passed","failed_closed","failed_open","not_run","not_applicable"],"type":"list[object]"} |
| `row_local_reward_and_ap4_blockers_frozen` | `true` | {"final_global_ap4_reclassification_supported":{"constraint":"N24 may consume local N23 AP4 context but cannot finalize global AP4 reclassification","required_value":false,"type":"boolean"},"reward_maximization_claim_allowed":{"constraint":"reward maximization remains blocked row-locally","required_value":false,"type":"boolean"}} |
| `n23_ap4_context_invariants_frozen` | `true` | {"if_n23_ap4_bridge_status_bridge_candidate_supported":{"ap4_context_status_may_be":["n23_bridge_candidate_consumed"]},"if_n23_ap4_bridge_status_not_consumable":{"ap4_context_status_must_not_be":["n23_bridge_candidate_consumed"]},"if_n23_context_consumption_bounded_lower_rung_context_only":{"ap4_context_status_must_be":"lower_n23_context_consumed"},"if_n23_context_consumption_not_available":{"ap4_context_status_must_be":"missing_blocks_row"}} |
| `support_measurement_scope_frozen` | `true` | {"maintenance_basin_id_required":true,"maintenance_basin_shift_blocks_surplus_claim":true,"maintenance_basin_signature_digest_required":true,"measurement_scope_frozen_before_surplus_calculation":true,"support_aggregation_method_values":["min","sum","mean","declared_rule"],"support_measurement_scope_values":["maintenance_basin_node_set","maintenance_basin_min_node","declared_support_region","route_local_support"]} |
| `optional_continuation_count_descriptive_only` | `true` | {"constraint":"descriptive count of optional continuation records; does not by itself satisfy AB3 or AB5","rung_effect":"AB3 uses optional_continuation_availability_count; AB5 uses jointly_admissible_optional_continuation_count","type":"integer"} |
| `same_basin_rule_content_frozen` | `true` | {"must_be_consumed_without_redefinition":true,"rule":{"allowed_drift":"optional branches may open only while maintenance basin remains above floor","basin_signature_fields":["surplus_supported_optionality.support_surplus_margin_trace","surplus_supported_optionality.optional_continuation_set_trace","surplus_supported_optionality.maintenance_floor_trace"],"blocked_relabels":["surplus_supported_optionality.blocked.abundance_as_goal","surplus_supported_optionality.blocked.agency","surplus_supported_optionality.blocked.consciousness","surplus_supported_optionality.blocked.identity_acceptance","surplus_supported_optionality.blocked.native_ant_agency","surplus_supported_optionality.blocked.native_colony_agency","surplus_supported_optionality.blocked.native_support","surplus_supported_optionality.blocked.organism_life","surplus_supported_optionality.blocked.phase8_implementation","surplus_supported_optionality.blocked.reward_maximization","surplus_supported_optionality.blocked.selfhood","surplus_supported_optionality.blocked.semantic_action","surplus_supported_optionality.blocked.semantic_choice","surplus_supported_optionality.blocked.semantic_goal","surplus_supported_optionality.blocked.semantic_goal_ownership","surplus_supported_optionality.blocked.semantic_intention","surplus_supported_optionality.blocked.semantic_perception","surplus_supported_optionality.blocked.sentience","surplus_supported_optionality.blocked.unrestricted_autonomy"],"boundary_integrity_floor":"boundary remains coherent while optional branches are open","failure_modes":["hidden budget relief","maintenance floor crossing","optional branch label without geometry","reward/proxy gain mistaken for abundance"],"flux_balance_bounds":"optional branch flux cannot drain maintenance support below floor","hidden_producer_support_allowed":false,"label_only_continuation_allowed":false,"proxy_only_success_allowed":false,"replay_requirement":"surplus and optional branch set replay under same budget surface","required_coherence_floor":"maintenance coherence floor preserved","required_support_floor":"maintenance support floor preserved","rule_id":"n20_i5_surplus_supported_optionality_same_basin_rule","source_contract_row":"n20_i4_row_05_surplus_supported_optionality"},"source":"N20 I5 same-basin rule from I1"} |
| `control_not_applicable_policy_frozen` | `true` | {"affected_rung_required":true,"allowed_only_with_scope_reason":true,"not_applicable_cannot_satisfy_required_control":true,"not_applicable_for_required_ab4_or_ab5_control_blocks_dependent_rung":true,"scope_reason_required":true} |
| `ab3_replay_interaction_frozen` | `true` | {"ab3_without_replay_status":"provisional_source_current_optionality_candidate","declared_replay_family_cannot_create_original_ab3_set":true,"failed_open_invalidates_row":true,"not_run_blocks_dependent_rung":true,"replay_required_for_ab3":false,"required_modes_for_ab4_plus":["artifact_replay","snapshot_load_replay","duplicate_replay"]} |
| `same_run_original_optionality_rule_frozen` | `true` | {"availability_vs_joint_admissibility":{"ab3_minimum_availability_count":2,"ab5_minimum_jointly_admissible_count":2,"jointly_admissible_optional_continuation_count":"alternatives jointly admissible under same maintenance surplus and budget envelope","optional_continuation_availability_count":"same-window source-current optional alternatives"},"declared_replay_family":{"may_create_original_ab3_optional_set":false,"may_validate_repeatability":true,"may_validate_replay_stability":true,"may_validate_stress_behavior":true},"optional_branch_evidence_mode_policy":{"source_current_available_unexecuted_can_support_ab3":true,"source_current_cost_projection_is_provisional_until_replay":true,"source_current_executed_or_replay_validated_needed_for_ab4_plus":true},"optional_branch_record_schema":{"admissibility_status_values":["admissible","blocked_by_floor","blocked_by_boundary","blocked_by_flux","blocked_by_label_only","blocked_by_independent_run_assembly","blocked_by_hidden_budget"],"optional_branch_evidence_mode_rung_effects":{"deterministic_replay_validation":"eligible for AB4+ as replay validation","source_current_available_unexecuted":"can support AB3 if same-window and floors hold","source_current_cost_projection":"can support only bounded/provisional AB3 unless replay validates it","source_current_executed":"eligible for AB4+ if replay/control gates pass"},"optional_branch_evidence_mode_values":["source_current_available_unexecuted","source_current_executed","source_current_cost_projection","deterministic_replay_validation"],"producer_enumeration_used_is_producer_residue":true,"required_fields":["branch_id","source_node_id","target_node_id","edge_id_or_route_id","trace_origin","trace_status","optionality_window_step_range","support_before","support_after_or_projected_after","coherence_before","coherence_after_or_projected_after","support_surplus_margin_before","support_surplus_margin_after","coherence_surplus_margin_before","coherence_surplus_margin_after","boundary_integrity_result","flux_or_leakage_result","optional_flux_cost","maintenance_floor_preserved","reward_or_proxy_label_used","producer_enumeration_used","admissibility_status"],"reward_or_proxy_label_used_must_be_false_for_support":true,"trace_origin_allowed_values":["source_current_same_run","deterministic_replay_of_source_run","declared_replay_family","producer_label","report_derived","independent_run_assembly"],"trace_status_allowed_values":["present","missing","not_applicable"]},"optional_flux_does_not_drain_maintenance_support_required":true,"original_optional_continuation_set_trace":{"must_be_inside_declared_optionality_window":true,"must_be_same_source_current_run":true,"must_not_be_created_by_declared_replay_family":true,"must_not_be_independent_run_assembly":true,"must_not_be_label_only":true}} |
| `ab3_ab5_count_requirements_frozen` | `true` | {"ab3_minimum_availability_count":2,"ab5_minimum_jointly_admissible_count":2,"jointly_admissible_optional_continuation_count":"alternatives jointly admissible under same maintenance surplus and budget envelope","optional_continuation_availability_count":"same-window source-current optional alternatives"} |
| `surplus_budget_owner_rung_ceilings_frozen` | `true` | {"allowed_values":["source_current_geometry","declared_producer_surface","mixed_declared","hidden_budget_relief_blocks_row","not_recorded_blocks_row"],"rung_ceilings":{"declared_producer_surface":"may support producer-mediated AB2/AB3/AB4 candidate only; cannot support native support, Phase 8, or naturalized abundance","hidden_budget_relief_blocks_row":"blocks positive support","mixed_declared":"must record producer residue and naturalization debt; cannot exceed bounded producer-mediated candidate without source-backed naturalization evidence","not_recorded_blocks_row":"blocks positive support","source_current_geometry":"may support AB2..AB6 if all other gates pass"}} |
| `canonical_controls_frozen` | `true` | ["hidden_budget_relief_control","floor_crossing_as_abundance_control","surplus_without_optional_continuation_control","optionality_without_surplus_control","proxy_only_optional_branch_gain_control","optional_branch_label_only_control","single_optional_branch_relabel_control","independent_run_optional_assembly_control","maintenance_basin_shift_control","floor_renormalization_as_surplus_control","post_hoc_surplus_construction_control","n23_selection_context_relabel_as_abundance_control","reward_maximization_relabel_control","semantic_choice_relabel_control","agency_relabel_control","native_support_relabel_control","phase8_relabel_control","ap4_final_reclassification_relabel_control","ap5_proxy_gap_omission_control"] |
| `artifact_admissibility_fail_closed` | `true` | {"all_artifact_sha256_match_file_contents_required":true,"artifact_digests_must_match_file_contents":true,"artifact_manifest_schema":{"artifact_role_values":["source_contract","inherited_context","runtime_trace","surplus_margin_trace","maintenance_floor_trace","optional_continuation_set_trace","optional_branch_trace","boundary_integrity_trace","flux_leakage_trace","replay_trace","snapshot_load_replay_trace","duplicate_replay_trace","negative_control_trace","active_null_trace","report","closeout"],"digest_algorithm":"sha256","path_policy":"repository_relative_paths_only","required_item_fields":["path","sha256","artifact_role"],"type":"list[object]"},"artifact_paths_equal_manifest_paths_required":true,"artifact_paths_must_exist":true,"artifact_sha256_equal_manifest_sha256_required":true,"derived_report_only_true_blocks_positive_support":true,"digest_mismatch_blocks_ab_assignment":true,"missing_required_artifact_blocks_ab_assignment":true,"positive_ab_support_forbidden_if_only_artifact_roles":["report","inherited_context","source_contract","closeout"]} |
| `ladders_frozen` | `true` | {"ab_ladder":[{"meaning":"no source-current surplus optionality evidence","rung":"AB0"},{"meaning":"run artifact with possible surplus or optionality context","rung":"AB1"},{"meaning":"source-current surplus above declared maintenance floor","rung":"AB2"},{"meaning":"surplus opens source-current optional continuation set while floors hold","rung":"AB3"},{"meaning":"replay/control-backed surplus-supported optionality candidate","rung":"AB4"},{"meaning":"stress/threshold-backed abundance candidate with hidden-budget, proxy, and floor controls clean","rung":"AB5"},{"meaning":"N25-ready bounded surplus-supported optionality evidence","rung":"AB6"}],"ab_rung_rules":{"ab6_is_handoff_not_agency_or_semantic_choice":true,"rows_below_ab3_cannot_support_optionality":true,"rows_below_ab4_cannot_support_replay_control_backed_abundance":true},"closeout_ladder_claim_boundary":"tranche classification only; not semantic choice, agency, native support, sentience, Phase 8, or ant ecology","n24_closeout_ladder":[{"meaning":"contract-only closeout","rung":"N24-C0"},{"meaning":"active-null/control discipline established","rung":"N24-C1"},{"meaning":"surplus partial","rung":"N24-C2"},{"meaning":"source-current optional continuation candidate","rung":"N24-C3"},{"meaning":"replay/control-backed surplus optionality candidate","rung":"N24-C4"},{"meaning":"stress/threshold-backed abundance candidate","rung":"N24-C5"},{"meaning":"N25-ready bounded surplus-supported optionality evidence","rung":"N24-C6"}]} |
| `ap_gap_schema_frozen` | `true` | {"ap4_condition_reason_required":true,"ap4_context_status_from_i1":"n23_bridge_candidate_consumed","ap4_context_status_values":["n23_bridge_candidate_consumed","lower_n23_context_consumed","not_applicable","missing_blocks_row"],"ap4_dependency_status_values":["required_recorded","not_applicable","missing_blocks_row"],"ap5_condition_reason_required":true,"ap5_dependency_status_values":["conditional_required_recorded","not_applicable","missing_blocks_row"],"ap_gap_prose_only_allowed":false,"final_global_ap4_reclassification_supported":false,"proxy_reward_target_conditioned_optionality_requires_ap5":true,"route_or_branch_conditioned_optionality_requires_ap4":true} |
| `claim_boundary_forces_unsafe_false` | `true` | {"agency_claim_allowed":false,"all_unsafe_claim_flags_required_false":true,"ant_ecology_implementation_opened":false,"hypothesis_a_or_b_demoted_if_hypothesis_c_fails":true,"native_support_claim_allowed":false,"phase8_opened":false,"reward_maximization_claim_allowed":false,"semantic_choice_claim_allowed":false,"sentience_claim_allowed":false,"surplus_supported_optionality_claim_allowed_requires_all_ab_gates":true,"unsafe_claim_flags":{"agency":false,"ant_ecology_implementation":false,"consciousness":false,"free_will":false,"fully_native_integration":false,"identity_acceptance":false,"native_ant_agency":false,"native_colony_agency":false,"native_support":false,"organism_life":false,"phase8_implementation":false,"reward_maximization":false,"selfhood":false,"semantic_action":false,"semantic_choice":false,"semantic_goal":false,"semantic_goal_ownership":false,"semantic_intention":false,"semantic_perception":false,"sentience":false,"unrestricted_autonomy":false}} |
| `no_positive_n24_evidence_opened` | `true` | {"ab_ladder_rung_assigned":false,"candidate_rows_classified":false,"n24_closeout_ladder_rung_assigned":false,"primitive_evidence_opened":false,"ready_for_iteration_3_active_nulls":true,"surplus_supported_optionality_supported":false} |
| `no_absolute_paths` | `true` | "all stored paths are repository-relative" |

## Interpretation

Iteration 2 is a schema/control freeze only. It makes it impossible
for later N24 rows to pass by using hidden budget relief, floor
crossing, proxy gain, optional labels, independent-run assembly,
maintenance basin shift, floor renormalization, or N23 selection
context relabeling as abundance. Positive evidence remains unopened
until later source-current probes.
