# N26 Iteration 2 - Proxy Divergence / Collapse Schema And Controls

Status: `passed`

Acceptance state: `accepted_proxy_divergence_collapse_schema_frozen_no_proxy_evidence`

## Scope

Iteration 2 freezes schema and controls only. It assigns no PD rung and opens no positive proxy evidence.

## Frozen Ladders

| Ladder | Rungs |
| --- | --- |
| `PD` | `PD0, PD1, PD2, PD3, PD4, PD5, PD6` |
| `N26-C` | `N26-C0, N26-C1, N26-C2, N26-C3, N26-C4, N26-C5, N26-C6` |

## Source Digests

```text
source_inventory_output_digest = b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a
source_contract_row_digest = 5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61
source_consumable_contract_row_digest = 99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec
```

## Candidate Row Schema

Required field count: `38`

Required scoped substrate fields:

```text
scoped_mb6_substrate_consumption_record
multi_basin_scope_id
basin_ids_or_child_basin_ids
n25_2_unscoped_consumption_allowed
n25_2_unscoped_multi_basin_consumption_allowed
front_capacity_companion_backfill_used
```

Artifact roles are rung-specific:

| Rung | Required Roles |
| --- | --- |
| `PD2` | `runtime_trace, lower_stack_input_trace, proxy_metric_trace, basin_persistence_capacity_trace, support_coherence_floor_trace, report` |
| `PD3` | `runtime_trace, lower_stack_input_trace, proxy_metric_trace, basin_persistence_capacity_trace, support_coherence_floor_trace, basin_deepening_comparison_trace, proxy_vs_basin_delta_trace, replay_trace, report` |
| `PD4` | `runtime_trace, lower_stack_input_trace, proxy_metric_trace, basin_persistence_capacity_trace, support_coherence_floor_trace, basin_deepening_comparison_trace, proxy_vs_basin_delta_trace, peer_or_control_basin_trace, replay_trace, control_trace, report` |
| `PD5` | `runtime_trace, lower_stack_input_trace, proxy_metric_trace, basin_persistence_capacity_trace, support_coherence_floor_trace, basin_deepening_comparison_trace, proxy_vs_basin_delta_trace, proxy_optimized_path_trace, basin_deepened_path_trace, perturbation_challenge_trace, proxy_collapse_result_trace, peer_or_control_basin_trace, replay_trace, control_trace, report` |
| `PD6` | `runtime_trace, lower_stack_input_trace, proxy_metric_trace, basin_persistence_capacity_trace, support_coherence_floor_trace, basin_deepening_comparison_trace, proxy_vs_basin_delta_trace, proxy_optimized_path_trace, basin_deepened_path_trace, perturbation_challenge_trace, proxy_collapse_result_trace, peer_or_control_basin_trace, replay_trace, control_trace, report, closeout` |

AP5 `not_applicable` is blocked for positive proxy rows:

```text
PD2...PD6 require required_recorded or missing_blocks_row
not_applicable is limited to inventory/schema/null rows without proxy or target claims
```

## Controls

Required control count: `25`

```text
lower_stack_input_missing_control
proxy_metric_not_replayable_control
support_coherence_floor_missing_control
proxy_basin_measurement_not_independent_control
scoped_mb6_scope_id_missing_control
derived_report_only_positive_row_control
artifact_manifest_failure_control
proxy_label_only_control
post_hoc_target_digest_control
hidden_proxy_policy_control
proxy_only_improvement_control
basin_degradation_hidden_by_proxy_control
unscoped_mb6_consumption_control
front_capacity_backfill_control
peer_basin_missing_control
perturbation_mismatch_control
basin_deepened_survivor_missing_control
AP5_gap_prose_only_control
semantic_goal_relabel_control
semantic_choice_relabel_control
agency_relabel_control
native_support_relabel_control
sentience_relabel_control
phase8_completion_relabel_control
ant_ecology_relabel_control
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_source_inventory_passed` | `true` | `{"acceptance_state": "accepted_source_inventory_scoped_substrate_admission_no_proxy_evidence", "status": "passed"}` |
| `source_inventory_digest_matches_expected` | `true` | `{"output_digest": "b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a"}` |
| `source_contract_digests_match_i1` | `true` | `{"source_consumable_contract_row_digest": "99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec", "source_contract_row_digest": "5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61"}` |
| `source_role_split_frozen` | `true` | `{"source_row_count": 13}` |
| `pd_ladder_frozen` | `true` | `{"rungs": ["PD0", "PD1", "PD2", "PD3", "PD4", "PD5", "PD6"]}` |
| `n26_closeout_ladder_frozen` | `true` | `{"rungs": ["N26-C0", "N26-C1", "N26-C2", "N26-C3", "N26-C4", "N26-C5", "N26-C6"]}` |
| `candidate_row_required_fields_present` | `true` | `{"field_count": 38}` |
| `scoped_mb6_consumption_rules_frozen` | `true` | `{"front_capacity_companion_backfill_used": false, "n25_2_unscoped_consumption_allowed": false, "n25_2_unscoped_multi_basin_consumption_allowed": false}` |
| `ap5_dependency_enum_frozen` | `true` | `{"allowed_statuses": ["required_recorded", "missing_blocks_row", "not_applicable"], "ap5_gap_prose_only_control_required": true, "condition_reason_required": true, "missing_status_effect": "row_blocks_at_AP5_gate", "n15_n19_context_counts_as_native_ap5": false, "not_applicable_allowed_only_for": ["inventory_rows", "schema_rows", "active_null_rows_without_proxy_or_target_formation_claim"], "positive_proxy_rungs_require_ap5_dependency": ["PD2", "PD3", "PD4", "PD5", "PD6"]}` |
| `proxy_definition_rules_frozen` | `true` | `{"proxy_collapse_requires": ["proxy_optimized_path_fails_under_declared_perturbation", "basin_deepened_path_survives_same_perturbation_envelope", "perturbation_envelope_digest_identical_across_rows", "negative_controls_fail_closed"], "proxy_divergence_requires": ["proxy_metric_improves", "basin_persistence_or_deepening_stalls_or_degrades", "proxy_and_basin_measured_independently", "thresholds_and_target_declared_before_outcome_inspection", "negative_controls_fail_closed"], "proxy_improvement_alone_effect": "blocked_below_PD4", "semantic_target_label_effect": "blocked_relabel"}` |
| `proxy_policy_owner_enum_frozen` | `true` | `["source_current_runtime", "declared_analysis_policy", "producer_mediated_blocks_substrate_claim", "hidden_policy_blocks_row"]` |
| `artifact_roles_and_manifest_rules_frozen` | `true` | `{"per_artifact_required_fields": ["path", "sha256", "artifact_role"], "positive_support_blockers": ["artifact_missing", "sha256_mismatch", "artifact_role_missing", "derived_report_only_true", "absolute_path_present"], "required_artifact_roles_by_pd_rung": {"PD2": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "report"], "PD3": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "replay_trace", "report"], "PD4": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "peer_or_control_basin_trace", "replay_trace", "control_trace", "report"], "PD5": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "proxy_optimized_path_trace", "basin_deepened_path_trace", "perturbation_challenge_trace", "proxy_collapse_result_trace", "peer_or_control_basin_trace", "replay_trace", "control_trace", "report"], "PD6": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "proxy_optimized_path_trace", "basin_deepened_path_trace", "perturbation_challenge_trace", "proxy_collapse_result_trace", "peer_or_control_basin_trace", "replay_trace", "control_trace", "report", "closeout"]}, "required_roles": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "proxy_optimized_path_trace", "basin_deepened_path_trace", "perturbation_challenge_trace", "proxy_collapse_result_trace", "peer_or_control_basin_trace", "replay_trace", "control_trace", "report", "closeout"]}` |
| `artifact_roles_by_pd_rung_frozen` | `true` | `{"PD2": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "report"], "PD3": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "replay_trace", "report"], "PD4": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "peer_or_control_basin_trace", "replay_trace", "control_trace", "report"], "PD5": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "proxy_optimized_path_trace", "basin_deepened_path_trace", "perturbation_challenge_trace", "proxy_collapse_result_trace", "peer_or_control_basin_trace", "replay_trace", "control_trace", "report"], "PD6": ["runtime_trace", "lower_stack_input_trace", "proxy_metric_trace", "basin_persistence_capacity_trace", "support_coherence_floor_trace", "basin_deepening_comparison_trace", "proxy_vs_basin_delta_trace", "proxy_optimized_path_trace", "basin_deepened_path_trace", "perturbation_challenge_trace", "proxy_collapse_result_trace", "peer_or_control_basin_trace", "replay_trace", "control_trace", "report", "closeout"]}` |
| `ap5_not_applicable_constrained_for_positive_rows` | `true` | `{"allowed_statuses": ["required_recorded", "missing_blocks_row", "not_applicable"], "ap5_gap_prose_only_control_required": true, "condition_reason_required": true, "missing_status_effect": "row_blocks_at_AP5_gate", "n15_n19_context_counts_as_native_ap5": false, "not_applicable_allowed_only_for": ["inventory_rows", "schema_rows", "active_null_rows_without_proxy_or_target_formation_claim"], "positive_proxy_rungs_require_ap5_dependency": ["PD2", "PD3", "PD4", "PD5", "PD6"]}` |
| `replay_requirements_frozen` | `true` | `{"pd3_if_any_required_replay_fails": "PD3_or_stronger_blocked", "pd3_required_replay_modes": ["artifact_replay", "snapshot_load_replay", "duplicate_replay", "order_control"], "pd4_pd5_required_control_summary": {"failed_open_controls": 0, "negative_controls_fail_closed": true, "not_run_required_controls": 0}}` |
| `fail_closed_controls_frozen` | `true` | `{"control_count": 25}` |
| `control_satisfied_for_positive_row_frozen` | `true` | `["control_id", "control_status", "blocked_condition", "expected_result", "actual_result", "claim_allowed_when_control_triggers", "rung_effect", "control_satisfied_for_positive_row"]` |
| `source_current_derivation_blockers_frozen` | `true` | `{"control_ids": ["lower_stack_input_missing_control", "proxy_metric_not_replayable_control", "support_coherence_floor_missing_control", "proxy_basin_measurement_not_independent_control", "scoped_mb6_scope_id_missing_control", "derived_report_only_positive_row_control", "artifact_manifest_failure_control", "proxy_label_only_control", "post_hoc_target_digest_control", "hidden_proxy_policy_control", "proxy_only_improvement_control", "basin_degradation_hidden_by_proxy_control", "unscoped_mb6_consumption_control", "front_capacity_backfill_control", "peer_basin_missing_control", "perturbation_mismatch_control", "basin_deepened_survivor_missing_control", "AP5_gap_prose_only_control", "semantic_goal_relabel_control", "semantic_choice_relabel_control", "agency_relabel_control", "native_support_relabel_control", "sentience_relabel_control", "phase8_completion_relabel_control", "ant_ecology_relabel_control"]}` |
| `no_positive_proxy_evidence_opened` | `true` | `"schema freeze only; no proxy derivation/divergence/collapse rows are produced"` |
| `unsafe_claim_flags_false` | `true` | `{"agency_claim_allowed": false, "ant_ecology_claim_allowed": false, "identity_acceptance_claim_allowed": false, "native_support_claim_allowed": false, "organism_life_claim_allowed": false, "phase8_completion_claim_allowed": false, "semantic_choice_claim_allowed": false, "semantic_goal_claim_allowed": false, "semantic_learning_claim_allowed": false, "semantic_target_ownership_claim_allowed": false, "sentience_claim_allowed": false, "unrestricted_autonomy_claim_allowed": false, "unscoped_multi_basin_claim_allowed": false}` |
| `no_absolute_paths_in_records` | `true` | `"all paths are repository-relative"` |

## Claim Boundary

schema/control freeze only; no proxy derivation, proxy divergence, proxy collapse, AP5 bridge, semantic goal, agency, native support, sentience, Phase 8, ant ecology, or unscoped multi-basin claim
