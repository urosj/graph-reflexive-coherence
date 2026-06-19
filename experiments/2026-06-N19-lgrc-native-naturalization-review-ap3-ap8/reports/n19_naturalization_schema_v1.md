# N19 Iteration 2 - Naturalization Schema V1

Status:

```text
status = passed
candidate_rows_classified = false
phase8_opened = false
native_support_opened = false
```

Frozen enums:

```json
{
  "nat_level": [
    "NAT0",
    "NAT1",
    "NAT2",
    "NAT3",
    "NAT4",
    "NAT5",
    "NAT6"
  ],
  "primary_disposition": [
    "scaffold",
    "native_contract_candidate",
    "phase8_ready_native_policy_candidate",
    "implementation_gap_blocker",
    "theory_sensitive_blocker",
    "unsafe_relabel_rejected",
    "not_applicable"
  ],
  "row_decision": [
    "supported",
    "partial",
    "blocked",
    "rejected",
    "not_applicable"
  ]
}
```

Required row fields:

```json
[
  "row_id",
  "source_experiment",
  "source_iteration_or_closeout",
  "source_artifacts",
  "source_reports",
  "source_sha256",
  "source_output_digest",
  "source_final_supported_ap_level",
  "source_final_claim_ceiling",
  "artifact_supported",
  "artifact_claim_scope",
  "native_question",
  "primary_disposition",
  "nat_level",
  "phase8_ready",
  "phase8_ready_derivation",
  "native_policy_or_telemetry_surface_name",
  "runtime_visible_inputs",
  "native_state_needed",
  "state_mutation_owner",
  "record_schema_sketch",
  "default_off_flags",
  "enabled_validated_supported_separation",
  "budget_surface",
  "telemetry_requirements",
  "snapshot_replay_requirements",
  "negative_controls",
  "non_rc_quantity_audit",
  "minimal_producer_code_needed",
  "implementation_boundary",
  "claim_flags",
  "blocked_claims",
  "phase8_opened",
  "native_support_opened",
  "src_diff_empty",
  "row_decision"
]
```

Claim flag mapping:

```json
{
  "agency_claim_allowed": "agency",
  "ap9_opened": "AP9",
  "choice_claim_allowed": "choice",
  "fully_native_agentic_like_integration_claim_allowed": "fully native agentic-like integration",
  "identity_acceptance_claim_allowed": "identity acceptance",
  "intention_claim_allowed": "intention",
  "native_support_opened": "native support",
  "organism_life_claim_allowed": "organism/life behavior",
  "phase8_opened": "Phase 8 opened",
  "selfhood_claim_allowed": "selfhood",
  "semantic_action_claim_allowed": "semantic action",
  "semantic_goal_ownership_claim_allowed": "semantic goal ownership",
  "semantic_perception_claim_allowed": "semantic perception",
  "unrestricted_autonomy_claim_allowed": "unrestricted autonomy"
}
```

NAT4 gates:

```json
[
  "native_policy_or_telemetry_surface_name_present",
  "record_schema_sketch_present",
  "default_off_flags_present",
  "enabled_validated_supported_separation_present",
  "runtime_visible_inputs_source_backed",
  "state_mutation_owner_specified",
  "budget_surface_specified",
  "telemetry_requirements_specified",
  "snapshot_replay_requirements_specified",
  "negative_controls_specified",
  "non_rc_quantity_audit_passes",
  "claim_flags_forced_false",
  "phase8_opened_false",
  "native_support_opened_false",
  "src_diff_empty_true"
]
```

Controls:

| Control | Blocked Claim |
| --- | --- |
| artifact_replay_as_native_support_rejected | native_support |
| nat3_as_nat4_rejected | phase8_ready_without_all_nat4_gates |
| nat4_as_native_implementation_rejected | phase8_implementation |
| phase8_opened_by_classification_flag_rejected | phase8_opened |
| direct_native_support_flag_write_rejected | native_support_opened |
| ap_evidence_as_agency_rejected | agency |
| response_as_semantic_action_rejected | semantic_action |
| feedback_as_semantic_perception_rejected | semantic_perception |
| proxy_as_semantic_goal_rejected | semantic_goal_ownership |
| boundary_as_selfhood_rejected | selfhood |
| identity_acceptance_relabel_rejected | identity_acceptance |
| organism_life_relabel_rejected | organism_life |
| limited_h4_l5_as_general_ap8_rejected | general_ap8 |
| derived_b4c5_as_original_b4c5_rejected | original_b4c5_reverse_replay |
| non_rc_quantity_inserted_to_pass_rejected | non_rc_quantity |
| src_diff_non_empty_rejected | native_implementation_inside_n19 |
| absolute_path_in_record_rejected | non_portable_record |

Checks:

| Check | Passed |
| --- | --- |
| source_inventory_available | true |
| primary_disposition_enum_frozen | true |
| nat_level_enum_frozen | true |
| phase8_ready_derivation_frozen | true |
| nat4_gates_frozen | true |
| row_decision_enum_frozen | true |
| claim_flags_forced_false_schema_present | true |
| non_rc_quantity_audit_required | true |
| minimal_producer_code_needed_required | true |
| unsafe_relabel_controls_frozen | true |
| no_candidate_rows_classified_in_iteration_2 | true |
