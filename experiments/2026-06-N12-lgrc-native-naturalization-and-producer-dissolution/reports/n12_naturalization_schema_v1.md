# N12 Naturalization Schema V1

Status: `passed`.

## Summary

Iteration 2 freezes the N12 NAT ladder, row schema, dispositions,
NAT3/NAT4 gates, non-RC audit fields, mutation boundary fields,
and rejection rules before candidate evaluation or Phase 8 work.

## NAT Ladder

```json
{
  "NAT0": {
    "definition": "producer-only artifact scaffold",
    "name": "producer_only_artifact_scaffold",
    "native_support": false,
    "phase8_ready": false
  },
  "NAT1": {
    "definition": "source-backed producer pattern",
    "name": "source_backed_producer_pattern",
    "native_support": false,
    "phase8_ready": false
  },
  "NAT2": {
    "definition": "replayable producer pattern with controls",
    "name": "replayable_producer_pattern_with_controls",
    "native_support": false,
    "phase8_ready": false
  },
  "NAT3": {
    "definition": "native contract candidate; policy surface is named and plausible but one or more readiness gates remain missing",
    "name": "native_contract_candidate",
    "native_support": false,
    "phase8_ready": false
  },
  "NAT4": {
    "definition": "Phase 8-ready native policy candidate with all readiness gates explicit, no implementation, and no native support claim",
    "name": "phase8_ready_native_policy_candidate",
    "native_support": false,
    "phase8_ready": true
  },
  "NAT5": {
    "definition": "native implementation exists but is not integrated into agentic-like composition",
    "name": "native_implementation_not_integrated",
    "native_support": "requires_separate_phase8_source",
    "phase8_ready": null
  },
  "NAT6": {
    "definition": "native implementation validates within composition replay",
    "name": "native_implementation_validates_in_composition",
    "native_support": "requires_separate_phase8_source",
    "phase8_ready": null
  }
}
```

## Primary Dispositions

```json
[
  "scaffold",
  "native_absorption_candidate",
  "theory_sensitive_blocker",
  "blocked_missing_source_or_gate"
]
```

## NAT4 Gates

```json
{
  "meaning": "Phase 8-ready native policy candidate, no implementation.",
  "required": [
    "native_policy_name",
    "record_schema_sketch",
    "default_off_flags",
    "enabled_validated_supported_separation",
    "idempotency_digest_plan",
    "runtime_visible_inputs",
    "budget_surfaces",
    "telemetry_requirements",
    "snapshot_replay_requirements",
    "negative_controls",
    "compatibility_tests",
    "claim_flags_forced_false",
    "non_rc_quantity_audit",
    "mutation_boundary",
    "producer_or_policy_may_schedule_only",
    "step_or_topology_event_owns_state_mutation",
    "src_diff_empty",
    "native_supported_flags_false",
    "phase8_opened_false"
  ]
}
```

## Preserved Traceability Fields

```json
[
  "secondary_tags",
  "thresholds_to_serialize",
  "source_gap_rows",
  "source_contract_rows",
  "source_gap_row_summaries",
  "source_row_digest",
  "n11_native_supported",
  "n11_native_support_scope",
  "phase8_decision_source",
  "phase8_order_source",
  "phase8_readiness_source",
  "artifact_replay_requirements",
  "claim_boundary_controls",
  "contract_runtime_visible_inputs",
  "covered_policy_records",
  "ordering_requirements",
  "stale_context_blockers"
]
```

## Non-RC Quantity Audit

```json
{
  "candidate_specific_questions": {
    "response_magnitude": [
      "is proxy measurement a derived observable or new state?",
      "is target band exogenous or runtime-visible policy?",
      "is response gain serialized and replayable?",
      "does correction debit node-plus-packet budget?",
      "does response sizing require hidden optimization or external controller state?"
    ],
    "route_conductance_memory": [
      "is memory a coherence, geometry, or flux effect?",
      "is it only producer bookkeeping?",
      "does decay or relaxation conserve an accounted quantity?",
      "does it require a new scalar state outside RC accounting?"
    ]
  },
  "nat4_rejection_rule": "unaccounted_non_rc_quantity_required",
  "questions": [
    "is mechanism expressible as RC causality/coherence/geometry/flux/scheduling/lineage/budget?",
    "is mechanism only producer bookkeeping?",
    "does decay, relaxation, or response sizing conserve or debit an accounted quantity?",
    "does candidate require a new scalar state outside RC accounting?",
    "if extra quantity is required, what NAT4 blocker prevents readiness?"
  ],
  "required": true
}
```

## Mutation Boundary

```json
{
  "fields": [
    "mutation_boundary",
    "producer_or_policy_may_schedule_only",
    "step_or_topology_event_owns_state_mutation"
  ],
  "required_for_nat4": true,
  "rule": "Native policy may schedule or record only unless the committed step/topology event boundary owns the state mutation."
}
```

## Rejection Rules

```json
{
  "artifact_only_replay_relabelled_native": "blocked",
  "budget_surface_ambiguity": "blocked",
  "claim_promotion": "blocked",
  "hidden_producer_mutation": "blocked",
  "native_absorption_candidate_relabelled_native_support": "blocked",
  "non_rc_quantity_required": "blocked",
  "phase8_opened_inside_n12": "blocked",
  "producer_scaffold_relabelled_native": "blocked"
}
```

## Validation Scope

```json
{
  "candidate_row_validation_starts_in_iterations_3_to_7": true,
  "iteration_2_freezes_schema_only": true,
  "note": "Iteration 2 validates that schema fields, gates, and rejection rules are declared. It does not yet validate candidate rows against the final schema."
}
```

## Checks

```json
{
  "claim_flags_forced_false": true,
  "final_row_fields_declared": true,
  "iteration_1_passed": true,
  "iteration_1_traceability_fields_preserved": true,
  "nat4_gates_represented_in_field_schema": true,
  "nat4_has_mutation_boundary": true,
  "nat4_has_no_implementation_flags": true,
  "non_rc_quantity_audit_required": true,
  "phase8_ready_is_derived_from_nat4": true,
  "primary_disposition_non_overlapping": true,
  "src_clean": true
}
```

## Output Digest

```text
f6e025deff124593dee73891fa15a196338d0c05351119556e905ebf6e525327
```
