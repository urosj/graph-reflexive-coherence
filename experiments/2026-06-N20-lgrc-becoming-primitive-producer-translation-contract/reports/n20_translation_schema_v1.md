# N20 Iteration 2 - Translation Schema V1

Status:

```text
status = passed
acceptance_state = accepted_translation_schema_frozen_no_primitive_evidence
candidate_rows_classified = false
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
```

Source precedence:

```text
N12-N18 = historical prerequisite context
N19 = current classification boundary
```

Frozen enums:

```json
{
  "contract_status": [
    "complete",
    "incomplete_missing_producer_residue_classification",
    "incomplete_missing_continuation_function",
    "incomplete_missing_proxy_metric",
    "incomplete_missing_support_scaffold_declaration",
    "incomplete_missing_same_basin_rule",
    "incomplete_missing_controls",
    "incomplete_missing_claim_ceiling",
    "incomplete_missing_unsafe_claim_flags",
    "incomplete_missing_variable_classification",
    "incomplete_missing_debt_subtype",
    "blocked_by_relabel"
  ],
  "expected_primitive_ids": [
    "withdrawal_resistance",
    "naturalization_depth",
    "susceptibility_update",
    "live_continuation_collapse",
    "surplus_supported_optionality",
    "spark_sub_basin_new_basin_formation",
    "proxy_divergence_proxy_collapse",
    "configuration_substrate_transfer",
    "generative_extractive_persistence"
  ],
  "naturalization_debt_type": [
    "telemetry_debt",
    "policy_debt",
    "state_mutation_debt",
    "replay_debt",
    "budget_debt",
    "source_currentness_debt",
    "claim_boundary_debt"
  ],
  "row_decision": [
    "supported",
    "partial",
    "blocked",
    "rejected",
    "not_applicable"
  ],
  "source_roles": [
    "method_source",
    "diagnostic_vocabulary_source",
    "boundary_source",
    "implementation_boundary_source",
    "roadmap_source",
    "future_application_context"
  ],
  "unsafe_claim_flags": [
    "agency",
    "semantic_intention",
    "semantic_choice",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy"
  ],
  "variable_classification": [
    "substrate_carried",
    "producer_mediated",
    "naturalization_debt",
    "blocked_relabel"
  ]
}
```

Primitive row required fields:

```json
[
  "primitive_id",
  "primitive_name",
  "roadmap_target",
  "diagnostic_source_titles",
  "source_inventory_row_ids",
  "source_role_dependencies",
  "LGRC_visible_fields",
  "producer_mediated_fields",
  "naturalization_debt_fields",
  "blocked_relabel_fields",
  "variable_classification_records",
  "continuation_function_descriptor",
  "native_function_descriptor_alias",
  "proxy_metric_definition",
  "support_scaffold_declaration",
  "same_basin_continuation_rule",
  "contract_status",
  "row_decision",
  "minimum_controls",
  "ap_gap_dependencies",
  "conditional_gap_dependencies",
  "expected_first_positive_experiment",
  "claim_ceiling",
  "unsafe_claim_flags",
  "artifact_invariants",
  "source_consumption_rules"
]
```

Contract object schemas:

```json
{
  "continuation_function_descriptor_required_fields": [
    "descriptor_id",
    "basin_signature",
    "support_floor",
    "coherence_floor",
    "boundary_condition",
    "flux_condition",
    "continuation_condition",
    "withdrawal_condition",
    "transfer_condition",
    "proxy_metric",
    "proxy_divergence_blocker",
    "claim_ceiling"
  ],
  "minimum_controls": [
    "label_only_success_control",
    "proxy_only_success_control",
    "hidden_producer_support_control",
    "post_hoc_trace_construction_control",
    "semantic_relabel_control",
    "native_support_relabel_control",
    "phase8_relabel_control"
  ],
  "producer_definition": "explicit implementation surface that introduces, updates, routes, schedules, labels, or preserves a quantity not yet carried by LGRC source-current geometry",
  "producer_required_fields": [
    "producer_surface_name",
    "introduced_quantity",
    "update_rule_owner",
    "source_current_visibility",
    "replay_visibility",
    "budget_surface",
    "claim_boundary",
    "naturalization_debt",
    "negative_controls"
  ],
  "proxy_metric_definition_required_fields": [
    "proxy_id",
    "measured_quantity",
    "source_current_inputs",
    "producer_inputs",
    "expected_relation_to_continuation_function",
    "divergence_condition",
    "collapse_condition",
    "proxy_only_success_blocker"
  ],
  "same_basin_continuation_required_fields": [
    "basin_signature_fields",
    "allowed_drift",
    "required_support_floor",
    "required_coherence_floor",
    "boundary_integrity_floor",
    "flux_balance_bounds",
    "replay_requirement",
    "failure_modes",
    "blocked_relabels"
  ],
  "support_scaffold_declaration_required_fields": [
    "support_id",
    "support_source",
    "support_surface",
    "withdrawal_condition",
    "producer_role",
    "naturalization_debt",
    "hidden_support_control"
  ]
}
```

Source consumption evidence gates:

```json
{
  "boundary_source": {
    "may_define": [
      "claim_boundary",
      "blocked_claim",
      "historical_context"
    ],
    "may_not_satisfy": [
      "primitive_evidence_gate",
      "agency_claim_gate"
    ]
  },
  "diagnostic_vocabulary_source": {
    "may_define": [
      "field_names",
      "diagnostic_terms",
      "control_targets"
    ],
    "may_not_satisfy": [
      "primitive_evidence_gate",
      "implementation_gate",
      "native_support_gate",
      "agency_claim_gate"
    ]
  },
  "future_application_context": {
    "may_define": [
      "future_context",
      "deferred_medium_debt_placeholder"
    ],
    "may_not_satisfy": [
      "primitive_evidence_gate",
      "implementation_gate",
      "ant_ecology_spec_gate_before_N29"
    ]
  },
  "implementation_boundary_source": {
    "may_define": [
      "current_classification_boundary",
      "implementation_gap",
      "gap_propagation_rule"
    ],
    "may_not_satisfy": [
      "primitive_evidence_gate",
      "Phase_8_implementation_gate",
      "native_support_gate"
    ]
  },
  "method_source": {
    "may_define": [
      "method_step",
      "probe_design_rule",
      "control_design_rule"
    ],
    "may_not_satisfy": [
      "primitive_evidence_gate",
      "native_support_gate",
      "agency_claim_gate"
    ]
  },
  "roadmap_source": {
    "may_define": [
      "experiment_order",
      "claim_boundary",
      "handoff_target"
    ],
    "may_not_satisfy": [
      "primitive_evidence_gate",
      "implementation_gate"
    ]
  }
}
```

AP4/AP5 dependency rules:

```json
{
  "conditional_gap_dependencies": {
    "ap4": [
      {
        "condition": "route-conditioned selection is part of transfer",
        "primitive": "configuration_substrate_transfer",
        "required_action": "carry AP4/N14 gap until source-backed route-conditioned naturalization result exists"
      }
    ],
    "ap5": [
      {
        "condition": "proxy or target formation participates in branch valuation",
        "primitive": "live_continuation_collapse",
        "required_action": "carry AP5/N15 gap until source-backed proxy/target naturalization result exists"
      }
    ]
  },
  "gap_resolution_rule": "A primitive may remove an AP4/AP5 gap only by recording a source-backed naturalization result; a label, roadmap reference, or essay citation cannot remove the gap.",
  "propagation_rule": "Any later primitive depending on route selection, proxy derivation, target formation, or lower-stack source-currentness must carry the relevant N19 gap until source-backed naturalization evidence removes it.",
  "required_gap_dependencies": {
    "ap4": [
      "susceptibility_update",
      "live_continuation_collapse"
    ],
    "ap5": [
      "proxy_divergence_proxy_collapse"
    ]
  },
  "row_local_dependency_rule": "Every affected primitive row must carry its own AP4/AP5 dependency record; global gap maps are not sufficient for later support.",
  "source_map": {
    "ap4_gap_carried_forward": true,
    "ap5_gap_carried_forward": true,
    "gap_status": "carried_forward_not_resolved",
    "output_digest": "07a827ef3cade00882e9b04f53cadea75ca277df8ec12e04e4db60b99b0e0aa3",
    "path": "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_source_method_inventory.json"
  }
}
```

Validator rules:

```json
[
  "source inventory must have passed",
  "primitive rows cannot be classified before schema freeze",
  "every future artifact must include the N20 invariant block",
  "every source row must expose may_consume_as and must_not_consume_as",
  "diagnostic vocabulary cannot satisfy evidence gates",
  "N19 is the current classification boundary; N12-N18 are historical context",
  "every variable receives exactly one classification",
  "the same variable cannot appear in multiple classification field buckets",
  "naturalization_debt variables require a debt subtype",
  "blocked_relabel fields cannot be producer_mediated variables",
  "every primitive row has continuation_function_descriptor",
  "every primitive row has proxy_metric_definition",
  "every primitive row has support_scaffold_declaration",
  "every primitive row has same_basin_continuation_rule",
  "every primitive row has minimum_controls",
  "applicable AP4/AP5 gaps must be carried forward",
  "affected primitives must carry AP4/AP5 dependencies row-locally",
  "every primitive has an expected N21-N28 handoff target",
  "unsafe claim flags must remain false per row",
  "absolute local paths are rejected"
]
```

Checks:

| Check | Passed |
| --- | --- |
| source_inventory_passed | true |
| source_inventory_ready_for_iteration2 | true |
| no_primitive_rows_classified_before_schema_freeze | true |
| source_rows_have_positive_and_negative_consumption_fields | true |
| diagnostic_vocabulary_cannot_satisfy_evidence_gates | true |
| n19_is_current_boundary_n12_n18_historical | true |
| ap4_ap5_gap_dependencies_frozen | true |
| ap4_ap5_dependencies_are_row_local | true |
| contract_object_schemas_present | true |
| variable_classification_enum_exactly_one | true |
| variable_field_partition_rule_frozen | true |
| blocked_relabel_is_variable_classification | true |
| continuation_function_alias_rule_frozen | true |
| contract_status_complete_gate_hard_to_earn | true |
| all_primitives_have_handoff_targets | true |
| unsafe_claim_flags_required_per_row | true |
| artifact_invariants_preserved | true |
| no_absolute_paths | true |

Claim boundary:

```text
N20 Iteration 2 freezes schema only. It does not classify primitive rows, open primitive evidence, use diagnostic vocabulary as proof, open Phase 8, open native support, open agency, or open sentience.
```
