# N21 Iteration 1 - Source Contract Inventory

## Summary

Status: `passed`

Acceptance state: `accepted_source_contract_inventory_no_primitive_evidence`

Output digest: `d7b7a37bc0781aedbe6f83c5b55ff8805bf559fe7d684c5e1d2a9be8a7cef3ee`

Iteration 1 is inventory-only. It consumes N20 closeout and I5 contract
rows, records readiness gates, and does not assign WR, ND, or N21-C
ladder rungs.

## Source Artifacts

| Role | Path | Status | SHA-256 |
| --- | --- | --- | --- |
| n20_closeout_and_n21_handoff | `experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_closeout_and_n21_handoff.json` | `passed` | `f6897b0bd39d716e3f8de33ff1818d7b71cf59d9da957197dccd247e7ec438e9` |
| n20_i5_same_basin_contract | `experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_same_basin_continuation_contract.json` | `passed` | `72c4297b923a5dc0226e67be97ff368d0b586278f8b93ef4bd6fa7b79d1fb4d0` |
| n20_n29_handoff | `experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md` | `not_json` | `2a26c4600a0c55e36f42812548a60e4ea5cf6bfc7b44c1c25ad0301d1c7f4c80` |
| n20_n29_roadmap | `experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md` | `not_json` | `3939f9945d5656d7720e517d106b3c3cd1533f1f8505c339dfd4192940418e84` |

## Contract Rows

| Primitive | Source row | Contract | Source fields | Controls | Evidence opened |
| --- | --- | --- | ---: | ---: | --- |
| `withdrawal_resistance` | `n20_i5_row_01_withdrawal_resistance` | `complete` | 4 | 10 | `false` |
| `naturalization_depth` | `n20_i5_row_02_naturalization_depth` | `complete` | 4 | 10 | `false` |

## Readiness Gate

```json
{
  "may_redefine_n20_contract_to_pass": false,
  "must_consume_i5_contract": true,
  "must_declare_row_specific_thresholds_before_use": true,
  "must_fail_closed_on_hidden_support": true,
  "must_fail_closed_on_proxy_only_success": true,
  "must_keep_agency_native_phase8_sentience_claims_blocked": true,
  "must_keep_primitive_evidence_separate_from_contract": true,
  "must_produce_source_backed_pass_fail_evidence": true
}
```

## Evidence Boundary

```text
primitive_evidence_opened = false
withdrawal_resistance_supported = false
naturalization_depth_supported = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
```

N20 contract completeness defines N21 eligibility only. WR, ND, and
N21-C rungs require later source-backed N21 evidence rows.

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `n20_closeout_passed_and_ready_for_n21` | `true` | {"acceptance_state": "closed_n20_contract_and_n21_handoff_no_primitive_evidence", "ready_for_n21": true, "status": "passed"} |
| `n21_handoff_scope_matches_required_primitives` | `true` | ["withdrawal_resistance", "naturalization_depth"] |
| `readiness_gate_matches_expected` | `true` | {"may_redefine_n20_contract_to_pass": false, "must_consume_i5_contract": true, "must_declare_row_specific_thresholds_before_use": true, "must_fail_closed_on_hidden_support": true, "must_fail_closed_on_proxy_only_success": true, "must_keep_agency_native_phase8_sentience_claims_blocked": true, "must_keep_primitive_evidence_separate_from_contract": true, "must_produce_source_backed_pass_fail_evidence": true} |
| `n20_i5_contract_artifact_passed` | `true` | {"acceptance_state": "accepted_same_basin_control_contract_complete_no_primitive_evidence", "status": "passed"} |
| `required_i5_contract_rows_present` | `true` | ["naturalization_depth", "withdrawal_resistance"] |
| `required_i5_rows_contract_complete` | `true` | {"naturalization_depth": "complete", "withdrawal_resistance": "complete"} |
| `contract_rows_consumed_without_redefinition` | `true` | {"naturalization_depth": true, "withdrawal_resistance": true} |
| `primitive_evidence_not_opened` | `true` | {"n20_closeout": false, "n20_i5": false, "n21_rows": {"naturalization_depth": false, "withdrawal_resistance": false}} |
| `primitive_support_not_claimed` | `true` | {"naturalization_depth": false, "withdrawal_resistance": false} |
| `ladder_rungs_not_assigned_by_contract_inventory` | `true` | {"naturalization_depth": {"nd_ladder_rung": "not_assigned_contract_inventory_only", "wr_ladder_rung": "not_applicable"}, "withdrawal_resistance": {"nd_ladder_rung": "not_applicable", "wr_ladder_rung": "not_assigned_contract_inventory_only"}} |
| `source_current_fields_recorded` | `true` | {"naturalization_depth": ["naturalization_depth.post_probe_basin_signature_trace", "naturalization_depth.post_probe_support_floor_trace", "naturalization_depth.post_probe_coherence_floor_trace", "naturalization_depth.multi_window_replay_trace"], "withdrawal_resistance": ["withdrawal_resistance.basin_signature_trace", "withdrawal_resistance.support_coherence_floor_trace", "withdrawal_resistance.boundary_integrity_trace", "withdrawal_resistance.withdrawal_window_trace"]} |
| `producer_and_debt_fields_recorded` | `true` | {"naturalization_depth": {"naturalization_debt_fields": ["naturalization_depth.source_current_producer_removal_observation", "naturalization_depth.multi_window_without_probe_replay", "naturalization_depth.naturalization_depth_budget_surface"], "producer_mediated_fields": ["naturalization_depth.naturalization_depth_score_formula", "naturalization_depth.support_source_annotation", "naturalization_depth.depth_rank_label"]}, "withdrawal_resistance": {"naturalization_debt_fields": ["withdrawal_resistance.source_current_support_withdrawal_surface", "withdrawal_resistance.producer_independent_withdrawal_replay", "withdrawal_resistance.native_support_decay_owner"], "producer_mediated_fields": ["withdrawal_resistance.declared_withdrawal_schedule", "withdrawal_resistance.withdrawal_amount_policy", "withdrawal_resistance.pass_fail_threshold_label"]}} |
| `blocked_relabel_fields_recorded` | `true` | {"naturalization_depth": 19, "withdrawal_resistance": 19} |
| `required_controls_recorded` | `true` | {"naturalization_depth": ["label_only_success_control", "proxy_only_success_control", "hidden_producer_support_control", "post_hoc_trace_construction_control", "semantic_relabel_control", "native_support_relabel_control", "phase8_relabel_control", "probe_present_only_control", "probe_residue_control", "support_source_annotation_relabel_control"], "withdrawal_resistance": ["label_only_success_control", "proxy_only_success_control", "hidden_producer_support_control", "post_hoc_trace_construction_control", "semantic_relabel_control", "native_support_relabel_control", "phase8_relabel_control", "withdrawal_schedule_removed_control", "hidden_support_margin_control", "support_floor_crossing_control"]} |
| `global_unsafe_claim_flags_cover_blocked_claims` | `true` | {"naturalization_depth": ["agency", "consciousness", "fully_native_integration", "identity_acceptance", "native_ant_agency", "native_colony_agency", "native_support", "organism_life", "phase8_implementation", "selfhood", "semantic_action", "semantic_choice", "semantic_goal_ownership", "semantic_intention", "semantic_perception", "sentience", "unrestricted_autonomy"], "withdrawal_resistance": ["agency", "consciousness", "fully_native_integration", "identity_acceptance", "native_ant_agency", "native_colony_agency", "native_support", "organism_life", "phase8_implementation", "selfhood", "semantic_action", "semantic_choice", "semantic_goal_ownership", "semantic_intention", "semantic_perception", "sentience", "unrestricted_autonomy"]} |
| `global_and_source_unsafe_claim_flags_false_per_row` | `true` | {"naturalization_depth": {"global_unsafe_claim_flags": {"agency": false, "consciousness": false, "fully_native_integration": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false}, "row_specific_blocked_relabel_count": 19, "source_unsafe_claim_flags": {"agency": false, "consciousness": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false}}, "withdrawal_resistance": {"global_unsafe_claim_flags": {"agency": false, "consciousness": false, "fully_native_integration": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false}, "row_specific_blocked_relabel_count": 19, "source_unsafe_claim_flags": {"agency": false, "consciousness": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false}}} |
| `row_specific_blocked_relabels_separated_from_global_flags` | `true` | {"naturalization_depth": {"global_unsafe_claim_flags": "N21-wide unsafe claim family; every listed claim is forced false.", "row_specific_blocked_relabels": "Primitive-specific blocked relabel fields inherited from N20; they are not required to appear as global unsafe flag keys."}, "withdrawal_resistance": {"global_unsafe_claim_flags": "N21-wide unsafe claim family; every listed claim is forced false.", "row_specific_blocked_relabels": "Primitive-specific blocked relabel fields inherited from N20; they are not required to appear as global unsafe flag keys."}} |
| `inventory_decision_uses_standard_row_decision` | `true` | {"naturalization_depth": {"inventory_decision": "supported_as_contract_input_only", "row_decision": "not_applicable"}, "withdrawal_resistance": {"inventory_decision": "supported_as_contract_input_only", "row_decision": "not_applicable"}} |
| `controls_declared_not_executed_in_inventory` | `true` | {"naturalization_depth": {"control_execution_status": "not_run", "controls_declared_fail_closed_in_contract": true}, "withdrawal_resistance": {"control_execution_status": "not_run", "controls_declared_fail_closed_in_contract": true}} |
| `agency_native_phase8_sentience_ant_ecology_unopened` | `true` | {"agency_claim_opened": false, "ant_ecology_spec_opened": false, "native_support_opened": false, "phase8_opened": false, "sentience_opened": false} |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

Iteration 1 passes as a source contract inventory. It confirms that the
two required N20 I5 rows are complete contract inputs for N21 and that
the N20 handoff marks N21 ready. It does not support withdrawal
resistance, naturalization depth, agency, native support, sentience,
Phase 8, or ant-ecology implementation.
