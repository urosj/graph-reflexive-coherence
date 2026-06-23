# N21 Iteration 2 - Withdrawal And Naturalization Schema Freeze

## Summary

Status: `passed`

Acceptance state: `accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence`

Output digest: `49ec439aa4d3f2bb895dc11d8c7613a0f18f75d4f78fa38aead2282ebbf78bb7`

Iteration 2 freezes schema only. It opens no primitive evidence and
assigns no WR, ND, or N21-C ladder rungs.

## Frozen Schema Sections

| Section | Key Constraint |
| --- | --- |
| source current | runtime/replay emitted, not report-built |
| candidate evidence row | all required row fields frozen, including same-basin rule, claim allowed, and claim ceiling |
| run artifact admissibility | paths exist, sha256 digests match, report-only blocked |
| thresholds | declared before use, no post-outcome retuning |
| withdrawal | modes/targets/window/floor policy frozen |
| probe absence | runtime absence, residue absence, annotation not evidence |
| replay/control | status enum and demotion effects frozen |
| ladders | WR0-WR6, ND0-ND6, N21-C0-N21-C6 |
| active nulls | comparable seed/topology/envelope/digests required |

## Candidate Evidence Row Required Fields

```text
primitive_id
source_contract_row
contract_consumed_without_redefinition
row_specific_thresholds_declared_before_use
run_artifact_id
source_commit_or_source_digest
runtime_config_digest
source_contract_row_digest
baseline_artifact_path
withdrawn_or_probe_absent_artifact_path
event_log_or_trace_path
snapshot_or_replay_artifact_path
artifact_digest
derived_report_only
source_current_inputs
producer_mediated_fields
naturalization_debt_fields
blocked_relabel_fields
same_basin_continuation_rule
support_floor_result
coherence_floor_result
boundary_integrity_result
flux_or_leakage_result
replay_result
replay_result_status
control_results
control_result_statuses
wr_ladder_rung
nd_ladder_rung
row_decision
primitive_claim_allowed
unsafe_claim_flags
claim_ceiling
```

## Read-Only I1 Contract References

| Primitive | Same-Basin Rule | Support Scaffold | Handoff Primitive |
| --- | --- | --- | --- |
| `withdrawal_resistance` | `n20_i5_withdrawal_resistance_same_basin_rule` | `n20_i4_withdrawal_resistance_support_scaffold` | `withdrawal_resistance` |
| `naturalization_depth` | `n20_i5_naturalization_depth_same_basin_rule` | `n20_i4_naturalization_depth_support_scaffold` | `naturalization_depth` |

## Run-Artifact Required Fields

```text
run_artifact_id
source_commit_or_source_digest
runtime_config_digest
source_contract_row_digest
baseline_artifact_path
withdrawn_or_probe_absent_artifact_path
event_log_or_trace_path
snapshot_or_replay_artifact_path
artifact_digest
derived_report_only
```

## Replay Requirements

```json
{
  "ND3": [
    "declared_multi_window_replay_without_original_probe_scaffold"
  ],
  "WR4": [
    "artifact_replay",
    "snapshot_load_replay",
    "duplicate_replay"
  ]
}
```

## Ladders

| Ladder | Rungs | Scope |
| --- | ---: | --- |
| WR | 7 | withdrawal-resistance primitive evidence |
| ND | 7 | N21-local artifact naturalization-depth evidence |
| N21-C | 7 | combined closeout classification |

## Boundary

```text
primitive_evidence_opened = false
withdrawal_resistance_supported = false
naturalization_depth_supported = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_i1_inventory_passed` | `true` | {"acceptance_state": "accepted_source_contract_inventory_no_primitive_evidence", "failed_checks": [], "status": "passed"} |
| `i1_boundary_kept_no_primitive_evidence` | `true` | {"n21_closeout_ladder_rung_assigned": false, "naturalization_depth_supported": false, "nd_ladder_rung_assigned": false, "positive_run_artifacts_consumed": false, "primitive_evidence_opened": false, "ready_for_iteration_2_schema_freeze": true, "source_contract_inventory_only": true, "withdrawal_resistance_supported": false, "wr_ladder_rung_assigned": false} |
| `candidate_evidence_row_schema_complete` | `true` | {"field_constraint_count": 33, "required_field_count": 33} |
| `candidate_schema_explicitly_freezes_missing_review_fields` | `true` | {"claim_ceiling": {"constraint": "must state bounded artifact-level N21 primitive ceiling; cannot permit agency, native support, sentience, Phase 8, or ant-ecology implementation", "type": "string"}, "primitive_claim_allowed": {"constraint": "true only when row decision, rung gates, replay, controls, thresholds, artifacts, same-basin rule, and unsafe flags all pass", "type": "boolean"}, "same_basin_continuation_rule": {"constraint": "must be consumed from I1 without redefinition", "required_keys": ["rule_id", "basin_signature_fields", "required_support_floor", "required_coherence_floor", "boundary_integrity_floor", "flux_balance_bounds", "replay_requirement", "failure_modes", "proxy_only_success_allowed", "hidden_producer_support_allowed", "label_only_continuation_allowed"], "source": "frozen_i1_same_basin_rule", "type": "object"}} |
| `run_artifact_required_fields_frozen` | `true` | ["run_artifact_id", "source_commit_or_source_digest", "runtime_config_digest", "source_contract_row_digest", "baseline_artifact_path", "withdrawn_or_probe_absent_artifact_path", "event_log_or_trace_path", "snapshot_or_replay_artifact_path", "artifact_digest", "derived_report_only"] |
| `artifact_admissibility_fail_closed` | `true` | {"artifact_digests_must_match_file_contents": true, "artifact_paths_must_exist": true, "derived_report_only_true_blocks_positive_support": true, "digest_algorithm": "sha256", "digest_mismatch_blocks_rung_assignment": true, "fail_closed_on_missing_or_mismatch": true, "missing_required_artifact_blocks_rung_assignment": true, "path_policy": "repository_relative_paths_only", "report_only_artifacts_may_summarize_but_not_assign_rungs": true, "required_fields": ["run_artifact_id", "source_commit_or_source_digest", "runtime_config_digest", "source_contract_row_digest", "baseline_artifact_path", "withdrawn_or_probe_absent_artifact_path", "event_log_or_trace_path", "snapshot_or_replay_artifact_path", "artifact_digest", "derived_report_only"], "source_contract_row_digest_must_match_i1": true} |
| `threshold_policy_declared_before_use` | `true` | {"failure_policy": "missing_or_post_hoc_threshold_blocks_support", "outcome_inspection_before_threshold_declaration_allowed": false, "required_threshold_surfaces": ["support_floor", "coherence_floor", "boundary_integrity_floor", "flux_or_leakage_bound", "replay_requirement", "control_requirement"], "retune_after_outcome_allowed": false, "row_specific_thresholds_declared_before_use": true, "threshold_record_required_fields": ["threshold_id", "primitive_id", "source_contract_row", "source_contract_row_digest", "threshold_declared_before_use", "threshold_value_or_rule", "threshold_owner", "failure_policy"]} |
| `withdrawal_schema_frozen` | `true` | {"declared_before_outcome_inspection_required": true, "floor_crossing_policy_required": true, "post_outcome_retuning_allowed": false, "producer_surface_claim_restriction": {"allowed_support": "producer_dependence_or_residue_analysis", "blocked_support": "source-current substrate-carried withdrawal resistance unless basin continuation persists in declared source-current fields", "if_withdrawal_target": "producer_surface"}, "required_fields": ["withdrawal_mode", "withdrawal_target", "withdrawal_start", "withdrawal_end", "withdrawal_amount", "recovery_window", "floor_crossing_policy"], "withdrawal_mode_allowed": ["weaken", "remove", "ramp_down", "step_down"], "withdrawal_target_allowed": ["support", "scaffold", "producer_surface"]} |
| `producer_surface_claim_restricted` | `true` | {"allowed_support": "producer_dependence_or_residue_analysis", "blocked_support": "source-current substrate-carried withdrawal resistance unless basin continuation persists in declared source-current fields", "if_withdrawal_target": "producer_surface"} |
| `probe_absence_schema_frozen` | `true` | {"probe_residue_present_blocks_nd4_and_stronger": true, "report_label_only_absence_allowed": false, "required_fields": ["probe_absent_runtime_input", "probe_residue_digest_absent", "support_annotation_not_used_as_evidence", "producer_probe_schedule_disabled"], "required_values": {"probe_absent_runtime_input": true, "probe_residue_digest_absent": true, "producer_probe_schedule_disabled": true, "support_annotation_not_used_as_evidence": true}, "support_annotation_as_evidence_blocks_nd4_and_stronger": true} |
| `replay_control_status_enum_frozen` | `true` | ["passed", "failed_closed", "failed_open", "not_run", "not_applicable"] |
| `wr4_and_nd3_replay_requirements_frozen` | `true` | {"ND3": ["declared_multi_window_replay_without_original_probe_scaffold"], "WR4": ["artifact_replay", "snapshot_load_replay", "duplicate_replay"]} |
| `active_null_comparability_frozen` | `true` | {"expected_result": "fail_closed", "no_declared_withdrawal_or_no_probe_absence": true, "same_basin_signature_fields": true, "same_budget_schedule_digest_where_applicable": true, "same_budget_schedule_family_where_applicable": true, "same_runtime_envelope_digest": true, "same_seed_or_declared_seed_pairing_rule": true, "same_source_contract_row": true, "same_source_contract_row_digest": true, "same_topology_config_family": true, "weak_or_noncomparable_null_blocks_null_use": true} |
| `classification_ladders_complete` | `true` | {"closeout_count": 7, "nd_count": 7, "nd_ladder_scope": "N21-local artifact ladder only; not the full cross-scale theoretical naturalization-depth ladder", "wr_count": 7} |
| `demotion_precedence_frozen` | `true` | {"control_failed_closed_blocks_control_backed_and_stronger": true, "control_failed_open_invalidates_row": true, "final_wr_nd_rungs_assigned_after_i6_only": true, "hypothesis_c_failure_demotes_or_blocks_a_b": true, "i4_i5_probe_rungs_are_provisional_until_i6": true, "not_run_blocks_dependent_rung": true, "replay_failure_blocks_replay_backed_and_stronger": true, "unrecorded_producer_residue_or_debt_blocks": ["WR6", "ND5", "ND6"]} |
| `row_decision_policy_frozen` | `true` | {"blocked_blocks_primitive_support": true, "inventory_contract_support_field": "inventory_decision", "inventory_rows_keep_row_decision": "not_applicable", "partial_blocks_primitive_support": true, "rejected_blocks_primitive_support": true, "row_decision_enum": ["supported", "partial", "blocked", "rejected", "not_applicable"], "supported_does_not_permit_unsafe_claims": true} |
| `claim_boundary_and_flag_split_frozen` | `true` | {"blocked_claims": ["agency", "semantic_action", "semantic_perception", "semantic_goal_ownership", "semantic_intention", "semantic_choice", "selfhood", "identity_acceptance", "native_support", "phase8_implementation", "fully_native_integration", "organism_life", "sentience", "consciousness", "native_ant_agency", "native_colony_agency", "unrestricted_autonomy"], "global_unsafe_claim_flags": {"agency": false, "consciousness": false, "fully_native_integration": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false}, "markdown_sources_context_only": true, "naturalization_debt_fields_are_not_native_support": true, "producer_mediated_fields_are_not_substrate_carried": true, "row_specific_blocked_relabels_separate": true} |
| `closeout_status_enums_frozen` | `true` | {"naturalization_depth_status": ["naturalization_depth_supported_bounded_N21_candidate", "naturalization_depth_rung_limited_candidate", "naturalization_depth_partial_or_blocked", "naturalization_depth_rejected"], "withdrawal_resistance_status": ["withdrawal_resistance_supported_artifact_level_candidate", "withdrawal_resistance_partial_or_blocked", "withdrawal_resistance_rejected"]} |
| `primitive_schema_rows_frozen_from_i1` | `true` | [{"claim_ceiling": "source contract input only; no N21 primitive evidence, agency, native support, Phase 8, sentience, or ant-ecology implementation", "contract_consumed_without_redefinition_required": true, "derived_report_only_true_blocks_support": true, "handoff_inputs": {"coherence_floor": "coherence remains above declared withdrawal floor", "declared_supports": ["support_coherence_floor_trace", "boundary_integrity_trace"], "hidden_support_blocker": "fail closed if support or scaffold is preserved by an undeclared producer surface", "primitive_id": "withdrawal_resistance", "probe_absent_condition": "declared support/scaffold weakened or absent after withdrawal", "probe_present_condition": "declared support/scaffold present before withdrawal", "proxy_only_success_blocker": "proxy improves while basin continuation fails -> primitive not supported", "support_floor": "support remains above declared withdrawal floor", "withdrawal_condition": "declared support is weakened or removed in a bounded window"}, "i1_contract_structures_read_only": true, "naturalization_debt_fields": ["withdrawal_resistance.source_current_support_withdrawal_surface", "withdrawal_resistance.producer_independent_withdrawal_replay", "withdrawal_resistance.native_support_decay_owner"], "positive_evidence_requires_run_artifacts": true, "primitive_id": "withdrawal_resistance", "producer_mediated_fields": ["withdrawal_resistance.declared_withdrawal_schedule", "withdrawal_resistance.withdrawal_amount_policy", "withdrawal_resistance.pass_fail_threshold_label"], "required_control_ids": ["label_only_success_control", "proxy_only_success_control", "hidden_producer_support_control", "post_hoc_trace_construction_control", "semantic_relabel_control", "native_support_relabel_control", "phase8_relabel_control", "withdrawal_schedule_removed_control", "hidden_support_margin_control", "support_floor_crossing_control"], "row_specific_blocked_relabels": ["withdrawal_resistance.blocked.agency", "withdrawal_resistance.blocked.consciousness", "withdrawal_resistance.blocked.identity_acceptance", "withdrawal_resistance.blocked.native_ant_agency", "withdrawal_resistance.blocked.native_colony_agency", "withdrawal_resistance.blocked.native_support", "withdrawal_resistance.blocked.organism_life", "withdrawal_resistance.blocked.phase8_implementation", "withdrawal_resistance.blocked.resilience_as_identity", "withdrawal_resistance.blocked.selfhood", "withdrawal_resistance.blocked.semantic_action", "withdrawal_resistance.blocked.semantic_choice", "withdrawal_resistance.blocked.semantic_goal", "withdrawal_resistance.blocked.semantic_goal_ownership", "withdrawal_resistance.blocked.semantic_intention", "withdrawal_resistance.blocked.semantic_perception", "withdrawal_resistance.blocked.sentience", "withdrawal_resistance.blocked.unrestricted_autonomy", "withdrawal_resistance.blocked.willpower"], "row_specific_thresholds_required_before_use": true, "same_basin_continuation_rule": {"basin_signature_fields": ["withdrawal_resistance.basin_signature_trace", "withdrawal_resistance.boundary_integrity_trace", "withdrawal_resistance.support_coherence_floor_trace"], "boundary_integrity_floor": "boundary remains distinguishable during withdrawal", "failure_modes": ["basin signature changes", "support floor crosses below declared floor", "coherence floor crosses below declared floor", "hidden support preserves margin", "label-only resistance"], "flux_balance_bounds": "leakage cannot explain apparent persistence under support reduction", "hidden_producer_support_allowed": false, "label_only_continuation_allowed": false, "proxy_only_success_allowed": false, "replay_requirement": "withdrawal run replays from declared support schedule without hidden producer support", "required_coherence_floor": "coherence remains above declared withdrawal floor", "required_support_floor": "support remains above declared withdrawal floor", "rule_id": "n20_i5_withdrawal_resistance_same_basin_rule"}, "schema_row_status": "frozen_from_i1_contract_inventory", "source_contract_row": "n20_i5_row_01_withdrawal_resistance", "source_contract_row_digest": "db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5", "source_current_fields": ["withdrawal_resistance.basin_signature_trace", "withdrawal_resistance.support_coherence_floor_trace", "withdrawal_resistance.boundary_integrity_trace", "withdrawal_resistance.withdrawal_window_trace"], "support_scaffold": {"declared_supports": ["withdrawal_resistance.support_coherence_floor_trace", "withdrawal_resistance.boundary_integrity_trace"], "hidden_support_allowed": false, "hidden_support_blocker": "fail closed if support or scaffold is preserved by an undeclared producer surface", "producer_role": "producer may declare, schedule, or expose the support/scaffold surface, but producer support cannot count as native support", "producer_supplied_scaffolds": ["withdrawal_resistance.declared_withdrawal_schedule", "withdrawal_resistance.withdrawal_amount_policy"], "required_supports": ["support floor", "coherence floor", "boundary integrity floor"], "support_id": "n20_i4_withdrawal_resistance_support_scaffold", "withdrawable_supports": ["declared support surface"]}}, {"claim_ceiling": "source contract input only; no N21 primitive evidence, agency, native support, Phase 8, sentience, or ant-ecology implementation", "contract_consumed_without_redefinition_required": true, "derived_report_only_true_blocks_support": true, "handoff_inputs": {"coherence_floor": "post-probe coherence remains above declared residual floor", "declared_supports": ["post_probe_support_floor_trace", "post_probe_coherence_floor_trace"], "hidden_support_blocker": "fail closed if support or scaffold is preserved by an undeclared producer surface", "primitive_id": "naturalization_depth", "probe_absent_condition": "original probe/scaffold absent with residual replay", "probe_present_condition": "original probe/scaffold present", "proxy_only_success_blocker": "proxy improves while basin continuation fails -> primitive not supported", "support_floor": "post-probe support remains above declared residual floor", "withdrawal_condition": "original probe/scaffold is removed or disabled"}, "i1_contract_structures_read_only": true, "naturalization_debt_fields": ["naturalization_depth.source_current_producer_removal_observation", "naturalization_depth.multi_window_without_probe_replay", "naturalization_depth.naturalization_depth_budget_surface"], "positive_evidence_requires_run_artifacts": true, "primitive_id": "naturalization_depth", "producer_mediated_fields": ["naturalization_depth.naturalization_depth_score_formula", "naturalization_depth.support_source_annotation", "naturalization_depth.depth_rank_label"], "required_control_ids": ["label_only_success_control", "proxy_only_success_control", "hidden_producer_support_control", "post_hoc_trace_construction_control", "semantic_relabel_control", "native_support_relabel_control", "phase8_relabel_control", "probe_present_only_control", "probe_residue_control", "support_source_annotation_relabel_control"], "row_specific_blocked_relabels": ["naturalization_depth.blocked.agency", "naturalization_depth.blocked.consciousness", "naturalization_depth.blocked.identity_acceptance", "naturalization_depth.blocked.native_absorption_by_label", "naturalization_depth.blocked.native_ant_agency", "naturalization_depth.blocked.native_colony_agency", "naturalization_depth.blocked.native_support", "naturalization_depth.blocked.organism_life", "naturalization_depth.blocked.phase8_implementation", "naturalization_depth.blocked.selfhood", "naturalization_depth.blocked.semantic_action", "naturalization_depth.blocked.semantic_choice", "naturalization_depth.blocked.semantic_goal", "naturalization_depth.blocked.semantic_goal_ownership", "naturalization_depth.blocked.semantic_intention", "naturalization_depth.blocked.semantic_perception", "naturalization_depth.blocked.sentience", "naturalization_depth.blocked.support_memory_as_selfhood", "naturalization_depth.blocked.unrestricted_autonomy"], "row_specific_thresholds_required_before_use": true, "same_basin_continuation_rule": {"basin_signature_fields": ["naturalization_depth.post_probe_basin_signature_trace", "naturalization_depth.post_probe_support_floor_trace", "naturalization_depth.post_probe_coherence_floor_trace"], "boundary_integrity_floor": "post-probe boundary remains distinguishable", "failure_modes": ["probe residue preserves row", "post-probe signature absent", "support annotation replaces source-current support", "depth score without replay"], "flux_balance_bounds": "residual persistence cannot be imported by hidden support flux", "hidden_producer_support_allowed": false, "label_only_continuation_allowed": false, "proxy_only_success_allowed": false, "replay_requirement": "multi-window replay without original probe/scaffold", "required_coherence_floor": "post-probe coherence remains above residual floor", "required_support_floor": "post-probe support remains above residual floor", "rule_id": "n20_i5_naturalization_depth_same_basin_rule"}, "schema_row_status": "frozen_from_i1_contract_inventory", "source_contract_row": "n20_i5_row_02_naturalization_depth", "source_contract_row_digest": "9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda", "source_current_fields": ["naturalization_depth.post_probe_basin_signature_trace", "naturalization_depth.post_probe_support_floor_trace", "naturalization_depth.post_probe_coherence_floor_trace", "naturalization_depth.multi_window_replay_trace"], "support_scaffold": {"declared_supports": ["naturalization_depth.post_probe_support_floor_trace", "naturalization_depth.post_probe_coherence_floor_trace"], "hidden_support_allowed": false, "hidden_support_blocker": "fail closed if support or scaffold is preserved by an undeclared producer surface", "producer_role": "producer may declare, schedule, or expose the support/scaffold surface, but producer support cannot count as native support", "producer_supplied_scaffolds": ["naturalization_depth.naturalization_depth_score_formula", "naturalization_depth.depth_rank_label"], "required_supports": ["post-probe support floor", "post-probe coherence floor", "multi-window replay trace"], "support_id": "n20_i4_naturalization_depth_support_scaffold", "withdrawable_supports": ["original probe/scaffold"]}}] |
| `i1_same_basin_support_handoff_references_frozen` | `true` | {"naturalization_depth": {"handoff_primitive_id": "naturalization_depth", "read_only": true, "same_basin_rule_id": "n20_i5_naturalization_depth_same_basin_rule", "support_scaffold_id": "n20_i4_naturalization_depth_support_scaffold"}, "withdrawal_resistance": {"handoff_primitive_id": "withdrawal_resistance", "read_only": true, "same_basin_rule_id": "n20_i5_withdrawal_resistance_same_basin_rule", "support_scaffold_id": "n20_i4_withdrawal_resistance_support_scaffold"}} |
| `no_positive_primitive_evidence_opened` | `true` | {"nd_ladder_rung_assigned": false, "positive_run_artifacts_consumed": false, "primitive_evidence_opened": false, "wr_ladder_rung_assigned": false} |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

Iteration 2 closes the schema freeze needed before active nulls and
positive probes. It makes source-current evidence, artifact
admissibility, thresholds, withdrawal/probe absence, replay/control
status, ladder assignment, and demotion precedence fail-closed.
It remains schema-only and does not support WR, ND, agency, native
support, sentience, Phase 8, or ant-ecology implementation.
