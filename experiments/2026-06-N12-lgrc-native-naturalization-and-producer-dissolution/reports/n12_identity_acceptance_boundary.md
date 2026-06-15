# N12 Iteration 5 Identity Acceptance Boundary

## Status

Status: `passed`.

```text
primary_disposition = theory_sensitive_blocker
nat_level = NAT2
phase8_ready = false
phase8_opened = false
native_support_opened = false
identity_acceptance_claim_opened = false
```

Iteration 5 records identity acceptance as a theory-sensitive blocked
boundary. It preserves N07/N10/N11 support-survival evidence, but does
not promote support survival, continuity, or explicit restoration into
identity acceptance, runtime acceptance, RC identity collapse, native
support, or agency.

The JSON artifact is the source of truth for the full boundary row,
source artifacts, digests, missing gates, controls, and replay rules.

## Source Decision

N07 supplies source-backed support withdrawal/restoration lanes. N10
shows bounded support-sensitive composition and defines a future
identity-support validator contract. N11 keeps the identity acceptance
validator blocked until theory is precise.

```json
{
  "n07_claim_boundary_identity_acceptance_allowed": false,
  "n07_general_identity_acceptance_supported": false,
  "n07_status": "passed",
  "n10_contract_phase8_readiness": "defer_until_identity_acceptance_theory_is_precise",
  "n10_hypothesis_b_positive_scope": "bounded_artifact_only_support_sensitive_full_composition",
  "n10_hypothesis_b_runtime_state_used": false,
  "n11_gap_native_support_scope": "support_survival_only_not_identity_acceptance",
  "n11_gap_phase8_readiness": "defer_until_identity_acceptance_theory_is_precise"
}
```

## Support Vs Acceptance Boundary

```json
{
  "boundary_status": "identity_acceptance_blocked",
  "identity_acceptance_meaning": "not formalized in N05-N11 or N12",
  "identity_continuity_meaning": "lineage-current support history can be replayed but does not imply runtime acceptance",
  "n10_support_matrix_states": [
    "support_intact_survives",
    "mild_withdrawal_survives",
    "n09_matched_withdrawal_disrupts_support",
    "explicit_restoration_recovers_support"
  ],
  "rc_identity_collapse_meaning": "blocked theory claim, not a validator result",
  "runtime_acceptance_meaning": "blocked until acceptance event semantics exist",
  "support_lanes": [
    {
      "claim_boundary": "support retention/disruption classification only; no runtime identity acceptance or agency claim",
      "identity_support_outcome_tag": "support_intact_bounded_exchange_reference",
      "lane_id": "support_intact_reference",
      "restoration_fraction": 0.0,
      "support_survival_passed": true,
      "support_survival_threshold": 0.85,
      "withdrawal_depth": 0.0
    },
    {
      "claim_boundary": "support retention/disruption classification only; no runtime identity acceptance or agency claim",
      "identity_support_outcome_tag": "support_withdrawal_survival_baseline",
      "lane_id": "mild_support_weakening",
      "restoration_fraction": 0.0,
      "support_survival_passed": true,
      "support_survival_threshold": 0.85,
      "withdrawal_depth": 0.1
    },
    {
      "claim_boundary": "support retention/disruption classification only; no runtime identity acceptance or agency claim",
      "identity_support_outcome_tag": "support_disrupted_by_withdrawal_without_restoration",
      "lane_id": "n09_matched_partial_support_withdrawal",
      "restoration_fraction": 0.0,
      "support_survival_passed": false,
      "support_survival_threshold": 0.85,
      "withdrawal_depth": 0.25
    },
    {
      "claim_boundary": "support retention/disruption classification only; no runtime identity acceptance or agency claim",
      "identity_support_outcome_tag": "explicit_restoration_recovers_support_survival_baseline",
      "lane_id": "restored_after_n09_partial_withdrawal",
      "restoration_fraction": 0.8,
      "support_survival_passed": true,
      "support_survival_threshold": 0.85,
      "withdrawal_depth": 0.25
    }
  ],
  "support_survival_evidence_available": true,
  "support_survival_evidence_source": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_13_identity_support_withdrawal_baseline.json",
  "support_survival_meaning": "support retention/disruption/restoration classification under serialized withdrawal lanes",
  "support_survival_threshold": 0.85
}
```

## Theory Entry Gates

```json
[
  {
    "gate_id": "identity_acceptance_semantics_formalized",
    "required_before": "NAT3_or_NAT4_for_identity_acceptance",
    "status": "missing"
  },
  {
    "gate_id": "runtime_acceptance_event_schema",
    "required_before": "native_identity_acceptance_validator_design",
    "status": "missing"
  },
  {
    "gate_id": "identity_continuity_acceptance_split",
    "required_before": "support_evidence_can_feed_acceptance_validator",
    "status": "missing"
  },
  {
    "gate_id": "rc_identity_collapse_claim_boundary",
    "required_before": "any_rc_identity_collapse_validator",
    "status": "missing"
  }
]
```

## Deferred Phase 8 Requirements

```json
{
  "minimum_before_nat4": [
    "native policy name with accepted semantics",
    "record schema for acceptance event and validator result",
    "idempotent digest over support, continuity, event, and budget",
    "snapshot/replay validator that rejects report-side acceptance",
    "compatibility tests preserving forced-false agency claims"
  ],
  "minimum_before_reconsidering_nat3": [
    "formal semantics for identity acceptance",
    "runtime-visible acceptance event schema",
    "acceptance-vs-continuity separation rule",
    "negative controls for acceptance relabeling",
    "default-off telemetry contract under src/pygrc/telemetry"
  ],
  "status": "blocked"
}
```

## Record Schema Sketch

```json
{
  "forbidden_fields": [
    "semantic_identity_acceptance",
    "runtime_self_acceptance",
    "rc_identity_collapse_flag",
    "identity_personhood_state",
    "hidden_restoration_state",
    "report_side_acceptance_override"
  ],
  "record_type": "identity_acceptance_boundary_record",
  "records_available": [
    "native_identity_support_validator_record",
    "support_state_history_record",
    "withdrawal_restoration_history_record"
  ],
  "records_missing_before_phase8_entry": [
    "identity_acceptance_event_record",
    "runtime_acceptance_validator_record",
    "rc_identity_collapse_validator_record"
  ],
  "status": "blocked_theory_boundary_not_native_policy",
  "version": "v1"
}
```

## Non-RC Quantity Audit

```json
{
  "audit_status": "blocked_theory_sensitive_not_nat4",
  "candidate_specific_questions": {
    "can_acceptance_be_added_as_report_side_label": false,
    "does_rc_identity_collapse_have_formal_validator": false,
    "is_identity_continuity_runtime_acceptance": false,
    "is_restoration_history_identity_acceptance": false,
    "is_support_survival_identity_acceptance": false
  },
  "does_identity_acceptance_require_semantics_not_yet_formalized": true,
  "extra_unaccounted_quantity_allowed": false,
  "field_required": true,
  "is_identity_acceptance_derived_observable": false,
  "is_support_survival_rc_observable": true,
  "nat4_blocker_if_extra_quantity_required": "identity_acceptance_semantics_not_formalized",
  "would_acceptance_require_new_unaccounted_quantity_without_theory": true
}
```

## Mutation Boundary

```json
{
  "producer_or_policy_may_schedule_only": null,
  "reason": "support history replay can be recorded, but no native acceptance state mutation or validator semantics are defined",
  "status": "blocked_until_identity_acceptance_theory_is_formalized",
  "step_or_topology_event_owns_state_mutation": null
}
```

## Telemetry And Replay Requirements

```json
{
  "compatibility_tests": [
    "support_survival_not_identity_acceptance",
    "identity_continuity_not_runtime_acceptance",
    "restoration_history_not_acceptance",
    "rc_identity_collapse_claim_blocked",
    "identity_acceptance_claim_flags_false",
    "phase8_ready_false_for_identity_boundary",
    "native_supported_flags_false",
    "hidden_restoration_rejected",
    "support_history_erasure_rejected"
  ],
  "snapshot_replay_requirements": [
    "replay reconstructs support lanes and support survival outcomes",
    "replay preserves disruption and explicit restoration history",
    "replay keeps support survival distinct from identity acceptance",
    "replay rejects hidden restoration",
    "replay rejects report-side identity acceptance labels"
  ],
  "telemetry_requirements": [
    "future_identity_support_telemetry_must_remain_separate_from_acceptance",
    "identity_acceptance_flags_exported_false_until_theory_gate_passes",
    "support_state_digest_and_restoration_history_digest",
    "withdrawal_event_digest_and_restoration_event_digest",
    "claim_flags_forced_false_snapshot",
    "default_off_native_identity_acceptance_records",
    "src_pygrc_telemetry_namespace_required_if_phase8_later_opens"
  ]
}
```

## Schema Alignment

```json
{
  "candidate_extension_field_meaning": {
    "deferred_phase8_requirements": "Minimum future requirements before reconsidering NAT3/NAT4.",
    "source_evidence_summary": "Short source-backed boundary summary.",
    "support_acceptance_boundary": "Iteration 5 support survival, identity continuity, runtime acceptance, and RC identity collapse separation.",
    "theory_entry_gates": "Theory gates required before identity acceptance can move beyond a blocked boundary."
  },
  "candidate_extension_fields": [
    "deferred_phase8_requirements",
    "source_evidence_summary",
    "support_acceptance_boundary",
    "theory_entry_gates"
  ],
  "final_row_field_count": 56,
  "missing_final_row_fields": []
}
```

## Source Digest Policy

```json
{
  "all_source_file_sha256_present": true,
  "output_digest_used_when_source_exposes_it": true,
  "row_source_report_sha256": "784e6a10654058e3e367957dc9910e61a14cbfdebd5d0403629712abf7418ef1",
  "row_source_sha256": "22c5ba0797cbbea75d06e138c6e570a3a446e31381fe4d0c4716093868de4f01"
}
```

## Checks

```json
{
  "claim_flags_all_false": true,
  "identity_continuity_separated_from_runtime_acceptance": true,
  "missing_formal_acceptance_semantics_recorded": true,
  "n07_support_baseline_passed": true,
  "n10_contract_identity_support_validator_found": true,
  "n10_support_matrix_passed": true,
  "n11_identity_gap_found": true,
  "nat_level_is_nat2_not_nat4": true,
  "native_supported_flags_false": true,
  "no_identity_acceptance_claim_opens": true,
  "phase8_opened_false": true,
  "phase8_ready_false": true,
  "primary_disposition_theory_sensitive_blocker": true,
  "rc_identity_collapse_claims_blocked": true,
  "schema_alignment_complete": true,
  "source_file_sha256_all_present": true,
  "src_clean": true,
  "support_survival_separated_from_identity_acceptance": true,
  "validator_local_support_fields_identified": true
}
```

## Claim Boundary

```text
support survival != identity acceptance
identity continuity != runtime acceptance
restoration history != identity acceptance
identity validator candidate != identity acceptance
identity acceptance != native support
native support != agency
RC identity collapse remains blocked
phase8_ready = false
```

## Output Digest

```text
22637fb4210725ac87cd5be283294d1f252ee4584058fe83acb68ad9270c9295
```
