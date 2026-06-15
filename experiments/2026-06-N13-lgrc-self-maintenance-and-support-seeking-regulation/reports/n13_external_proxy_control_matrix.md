# N13 External Proxy And Hidden Target Control Matrix

## Status

Status: `passed`.

```text
external_proxy_controls_passed = true
hidden_target_controls_passed = true
post_hoc_label_controls_passed = true
support_disrupted_pre_stress_control_passed = true
candidate_ap_level = AP3
provisional_ap_level = AP3_candidate_control_clean_pending_stress_and_boundary
final_ap3_supported = false
self_maintenance_candidate_supported = false
phase8_opened = false
native_support_opened = false
```

Iteration 5 runs fail-closed controls around the Iteration 4
support-seeking regulation candidate. Passing these controls means the
candidate is not merely an external proxy, hidden target, post-hoc
label, budget-ambiguous correction, or unsafe claim relabel. It does
not freeze final AP3 support; support-disruption/restoration stress
and the final claim-boundary record remain pending.

## Control Summary

```json
{
  "all_controls_fail_closed": true,
  "control_count": 10,
  "failed_controls": [],
  "native_support_without_phase8_control_included": true,
  "passed_control_count": 10,
  "required_control_count": 9,
  "required_controls_present": true
}
```

## Controls

| Control | Expected rejection | Observed | Passed |
| --- | --- | --- | --- |
| `external_proxy_only_control` | `external_proxy_only` | `rejected` | `true` |
| `hidden_support_target_control` | `hidden_support_target` | `rejected` | `true` |
| `post_hoc_support_label_control` | `post_hoc_support_label` | `rejected` | `true` |
| `support_disrupted_regulation_control` | `support_disrupted_but_regulation_counted` | `rejected` | `true` |
| `stale_source_replay_control` | `stale_source_replay` | `rejected` | `true` |
| `budget_ambiguous_correction_control` | `budget_surface_ambiguity` | `rejected` | `true` |
| `identity_acceptance_relabel_control` | `identity_acceptance_relabel` | `rejected` | `true` |
| `semantic_goal_ownership_relabel_control` | `semantic_goal_ownership_relabel` | `rejected` | `true` |
| `agency_relabel_control` | `agency_relabel` | `rejected` | `true` |
| `native_support_without_phase8_control` | `native_support_without_phase8` | `rejected` | `true` |

## Interpretation Record

```json
{
  "ap_state": {
    "candidate_ap_level": "AP3",
    "final_ap3_supported": false,
    "provisional_ap_level": "AP3_candidate_control_clean_pending_stress_and_boundary",
    "self_maintenance_candidate_supported": false
  },
  "blocked_alternative_explanations": [
    "external_proxy_only",
    "hidden_support_target",
    "post_hoc_support_label",
    "support_disrupted_but_regulation_counted",
    "stale_source_replay",
    "budget_surface_ambiguity",
    "identity_acceptance_relabel",
    "semantic_goal_ownership_relabel",
    "agency_relabel",
    "native_support_without_phase8"
  ],
  "claim_boundary": {
    "artifact_level_candidate_is_native_support": false,
    "bounded_response_is_intention": false,
    "candidate_ap3_is_final_supported_ap3": false,
    "support_error_is_semantic_goal_ownership": false,
    "support_seeking_regulation_candidate_is_agency": false,
    "support_survival_is_identity_acceptance": false
  },
  "phase8_and_native_state": {
    "native_support_opened": false,
    "phase8_opened": false,
    "src_implementation_changed": false
  },
  "plain_language_meaning": "Iteration 5 makes the Iteration 4 support-seeking regulation candidate control-clean against external-proxy, hidden-target, post-hoc-label, stale-source, budget-ambiguity, and unsafe claim-relabel explanations. It does not make final AP3 support.",
  "record_id": "n13_i5_interpretation_external_proxy_controls_v1",
  "record_type": "n13_iteration_5_interpretation_record",
  "remaining_required_work": [
    "support_disruption_restoration_stress_matrix_iteration_6",
    "identity_goal_ownership_agency_boundary_record_iteration_7",
    "n13_closeout_handoff_iteration_8"
  ],
  "source_candidate": "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/outputs/n13_support_seeking_regulation_candidate.json",
  "source_candidate_output_digest": "a6c367246eaeba14953b87c4a89862238b5bde4568308f1ee4c7ef1d9c85116b",
  "source_control_matrix": "n13_external_proxy_hidden_target_control_matrix",
  "supported_interpretation": "The candidate may be carried forward as an artifact-level, source-current support-error bounded-response candidate whose target and error are derived from recorded support state rather than N09 external proxy fields.",
  "unsupported_interpretations": [
    "the candidate is final supported AP3",
    "the candidate proves self-maintenance",
    "support survival is identity acceptance",
    "support error is semantic goal ownership",
    "bounded response is intention",
    "support-seeking regulation is agency",
    "artifact-level support regulation is native support",
    "N12 response magnitude readiness is Phase 8 implementation"
  ]
}
```

## AP3 Gate State After Iteration 5

```json
{
  "agency_relabel_blocked": true,
  "budget_control_passed": true,
  "claim_boundary_record_pending_iteration7": true,
  "external_proxy_control_passed": true,
  "final_ap3_supported": false,
  "hidden_support_target_control_passed": true,
  "identity_acceptance_relabel_blocked": true,
  "native_support_relabel_blocked": true,
  "post_hoc_support_label_control_passed": true,
  "self_maintenance_candidate_supported": false,
  "semantic_goal_ownership_relabel_blocked": true,
  "stress_matrix_pending_iteration6": true,
  "support_disrupted_pre_stress_control_passed": true
}
```

## Pending After Iteration 5

```json
[
  "support_disruption_restoration_stress_not_run_until_iteration_6",
  "claim_boundary_record_not_frozen_until_iteration_7"
]
```

## Checks

```json
{
  "all_controls_fail_closed": true,
  "all_required_controls_present": true,
  "budget_ambiguous_correction_control_passed": true,
  "candidate_ap3_not_final_support": true,
  "claim_boundary_controls_false": true,
  "claim_flags_all_false": true,
  "claim_relabel_controls_passed": true,
  "external_proxy_only_control_passed": true,
  "hidden_support_target_control_passed": true,
  "interpretation_preserves_final_ap3_false": true,
  "interpretation_record_present": true,
  "interpretation_records_remaining_work": true,
  "inventory_source_passed": true,
  "native_support_not_opened": true,
  "phase8_not_opened": true,
  "post_hoc_support_label_control_passed": true,
  "regulation_source_passed": true,
  "schema_source_passed": true,
  "self_maintenance_not_supported_yet": true,
  "src_diff_empty": true,
  "stale_source_replay_control_passed": true,
  "stress_and_claim_boundary_pending": true,
  "support_disrupted_regulation_control_passed": true,
  "target_source_passed": true
}
```

## Claim Boundary

```text
support-seeking regulation candidate != agency
support survival != identity acceptance
support error != semantic goal ownership
bounded response != intention
candidate AP3 != final supported AP3
artifact-level support regulation != native support
```

## Output Digest

```text
4894859811d54d1ebd80411847de5bd4670bfe8e282f3bffea3c0d0712ce7d16
```
