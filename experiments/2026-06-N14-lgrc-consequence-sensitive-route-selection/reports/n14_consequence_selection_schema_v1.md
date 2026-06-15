# N14 Consequence Selection Schema V1

Status: `passed`.

## Acceptance State

```text
accepted_schema_freeze_no_row_validation
```

## Interpretation

```json
{
  "acceptance_state": "accepted_schema_freeze_no_row_validation",
  "next_required_step": "Build pre-selection route consequence records in Iteration 3 and validate them against this schema before route selection is classified.",
  "plain_language_interpretation": "Iteration 2 converts the N14 definition into a strict validation contract. It says what later rows must contain, including candidate-set completeness, derivation basis, immediate-affordance versus consequence rank conflict, replay/snapshot controls, and claim-boundary flags. It does not validate any AP4 candidate row.",
  "record_id": "n14_i2_interpretation_schema_gate_v1",
  "supported_interpretation": "N14 has a frozen AP4 row schema, AP4 gate, replay requirements, control list, and false claim flags for later candidate rows.",
  "unsupported_interpretations": [
    "AP4 consequence-sensitive selection support",
    "validated route consequence records",
    "validated consequence-sensitive selected route",
    "intention",
    "agency",
    "semantic goal ownership",
    "identity acceptance",
    "native support",
    "fully native integration"
  ]
}
```

Iteration 2 freezes the N14 row schema, AP4 gate, controls, replay
requirements, and claim flags. It does not validate AP4 candidate rows;
row validation starts in Iterations 3-7.

## AP4 Gate

```json
[
  "candidate_route_set_present",
  "eligible_candidate_completeness_record_present",
  "pre_selection_consequence_record_for_each_candidate",
  "source_artifact_report_digest_for_each_consequence_record",
  "prediction_basis_declared",
  "derivation_policy_declared",
  "source_window_declared",
  "downstream_support_effect_descriptor_present",
  "downstream_memory_effect_descriptor_present",
  "downstream_regulation_effect_descriptor_present",
  "observed_downstream_effect_descriptor_present_when_horizon_evaluated",
  "prediction_match_status_present",
  "immediate_affordance_rank_present",
  "consequence_rank_present",
  "selected_rank_present",
  "affordance_consequence_conflict_case_present",
  "affordance_consequence_conflict_resolved_by_consequence_true",
  "budget_cost_surface_present",
  "bounded_consequence_horizon_present",
  "deterministic_selection_rule_present",
  "tie_policy_present",
  "missing_consequence_record_rejection_present",
  "idempotency_digest_plan_present",
  "artifact_only_replay_requirement_present",
  "snapshot_load_equivalence_requirement_present",
  "order_inversion_replay_requirement_present",
  "runtime_state_used_false",
  "stale_record_policy_present",
  "negative_controls_present",
  "compatibility_checks_present",
  "claim_flags_forced_false",
  "src_diff_empty_true",
  "native_supported_flags_false",
  "phase8_opened_false"
]
```

## Row Schema Fields

```json
[
  "row_id",
  "source_experiment",
  "source_iteration",
  "source_artifact",
  "source_report",
  "source_sha256",
  "source_report_sha256",
  "mechanism_name",
  "mechanism_role",
  "route_candidate_id",
  "route_alternative_surface",
  "eligible_candidate_set_id",
  "candidate_set_completeness_status",
  "rejected_candidate_record",
  "immediate_affordance_surface",
  "immediate_affordance_rank",
  "consequence_record_source",
  "consequence_record_timing",
  "bounded_consequence_horizon",
  "prediction_basis",
  "derivation_policy",
  "source_window",
  "expected_support_effect",
  "expected_memory_effect",
  "expected_regulation_effect",
  "observed_downstream_effect",
  "prediction_match_status",
  "consequence_rank",
  "selected_rank",
  "affordance_consequence_conflict_resolved_by_consequence",
  "budget_cost_surface",
  "budget_validity",
  "selection_rationale_surface",
  "tie_policy",
  "missing_consequence_record_rejection",
  "hidden_outcome_table_control",
  "post_hoc_scoring_control",
  "stale_record_policy",
  "artifact_only_replay_status",
  "snapshot_load_status",
  "order_inversion_replay_status",
  "runtime_state_used",
  "provisional_ap_level",
  "provisional_claim_ceiling",
  "blocked_claims",
  "missing_gates"
]
```

## Consequence Record Schema

```json
{
  "projection_fields": [
    "prediction_basis",
    "derivation_policy",
    "source_window",
    "bounded_consequence_horizon",
    "expected_support_effect",
    "expected_memory_effect",
    "expected_regulation_effect",
    "observed_downstream_effect",
    "prediction_match_status"
  ],
  "source_requirements": [
    "source_artifact",
    "source_report",
    "source_sha256",
    "source_report_sha256",
    "output_digest_when_available"
  ],
  "timing": {
    "post_hoc_records_supported": false,
    "required": "pre_selection"
  }
}
```

## Route Candidate Schema

```json
{
  "candidate_set_fields": [
    "route_candidate_id",
    "eligible_candidate_set_id",
    "candidate_set_completeness_status",
    "rejected_candidate_record",
    "missing_consequence_record_rejection"
  ],
  "missing_record_policy": "reject_or_mark_unsupported",
  "ranking_fields": [
    "immediate_affordance_rank",
    "consequence_rank",
    "selected_rank",
    "affordance_consequence_conflict_resolved_by_consequence"
  ],
  "tie_policy_required": true
}
```

## Replay Requirements

```json
{
  "artifact_only_replay_required": true,
  "duplicate_replay_required": true,
  "order_inversion_replay_required": true,
  "runtime_state_used_required_value": false,
  "snapshot_load_equivalence_required": true
}
```

## Controls

```json
[
  "hidden_outcome_table_blocked",
  "post_hoc_consequence_scoring_blocked",
  "stale_consequence_record_blocked",
  "budget_invalid_route_blocked",
  "missing_consequence_record_blocked",
  "candidate_set_cherry_picking_blocked",
  "tie_policy_ambiguity_blocked",
  "immediate_affordance_only_relabel_blocked",
  "matched_affordance_conflict_resolved_by_consequence",
  "fixture_label_preference_blocked",
  "semantic_intention_relabel_blocked",
  "agency_relabel_blocked",
  "native_support_relabel_blocked",
  "identity_acceptance_relabel_blocked",
  "selfhood_relabel_blocked",
  "personhood_relabel_blocked",
  "biological_behavior_relabel_blocked",
  "semantic_choice_relabel_blocked",
  "unrestricted_agency_relabel_blocked"
]
```

## Checks

```json
{
  "all_required_fields_declared": true,
  "ap4_gate_contains_affordance_conflict": true,
  "candidate_set_completeness_declared": true,
  "derivation_projection_fields_declared": true,
  "final_ap4_requires_later_controls": true,
  "full_claim_flags_declared_false": true,
  "inventory_rows_available": true,
  "inventory_rows_satisfy_schema": true,
  "inventory_schema_not_extra_only": true,
  "inventory_source_passed": true,
  "native_supported_flags_false": true,
  "phase8_opened_false": true,
  "replay_snapshot_fields_declared": true,
  "required_controls_declared": true,
  "src_diff_empty": true
}
```

## Claim Boundary

```text
schema freeze != AP4 support
AP4 support requires Iterations 3-7 controls
consequence-sensitive selection != intention
expected downstream effect != semantic goal ownership
artifact-level AP4 != native support
```

## Output Digest

```text
56a2080a76f941e77e7a822874fa62e292f34452c06f02cbb8e971bccc540217
```
