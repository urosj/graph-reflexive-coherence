# N13 Support Disruption And Restoration Stress Matrix

## Status

Status: `passed`.

```text
support_disruption_restoration_stress_matrix_passed = true
support_seeking_regulation_survives_controls = true
candidate_ap_level = AP3
provisional_ap_level = AP3_candidate_stress_clean_pending_claim_boundary
final_ap3_supported = false
self_maintenance_candidate_supported = false
phase8_opened = false
native_support_opened = false
```

Iteration 6 stress-tests the support-seeking regulation candidate
across support-present, support-disrupted, explicit-restoration,
neutral/non-disruptive, and no-support-target regimes. It does not
freeze final AP3 support; the claim-boundary record remains pending
for Iteration 7.

## Stress Summary

```json
{
  "all_stress_records_passed": true,
  "failed_stress_records": [],
  "no_support_target_blocks_response": true,
  "response_only_when_support_error_positive": true,
  "stress_record_count": 5,
  "support_seeking_regulation_survives_controls": true
}
```

## Stress Records

| Regime | Source lane | Support error | Scheduled response | Passed |
| --- | --- | ---: | ---: | --- |
| `support_present_baseline` | `support_intact_reference` | 0.0 | 0 | `true` |
| `support_disrupted_regime` | `n09_matched_partial_support_withdrawal` | 0.120134817816 | 0.120134817816 | `true` |
| `explicit_restoration_regime` | `restored_after_n09_partial_withdrawal` | 0.0 | 0 | `true` |
| `neutral_or_non_disruptive_perturbation_regime` | `mild_support_weakening` | 0.0 | 0 | `true` |
| `no_support_control_regime` | `none` | null | 0 | `true` |

## Source-Current Replay Requirements

```json
{
  "control_output_digest_required": "4894859811d54d1ebd80411847de5bd4670bfe8e282f3bffea3c0d0712ce7d16",
  "lane_digests_required": true,
  "no_support_target_blocks_response": true,
  "regulation_output_digest_required": "a6c367246eaeba14953b87c4a89862238b5bde4568308f1ee4c7ef1d9c85116b",
  "source_artifacts_pinned": true,
  "stale_source_replay_blocked": true,
  "support_area_digest_required": true,
  "target_output_digest_required": "917e65721362fcda37ea4777489a5e3289a35ef550a16b3774884c803584ac3e"
}
```

## Budget And Response Surfaces

```json
{
  "budget_debit_surface": {
    "all_scheduled_responses_have_budget_debit": true,
    "budget_surfaces": [
      "support_response_packet_budget_debit",
      "response_packet_budget_surface",
      "node_plus_packet_budget_error",
      "final_budget_error"
    ],
    "debit_rule": "scheduled bounded response amount must debit node-plus-packet or explicit response packet budget before commit",
    "mutation_boundary": {
      "phase8_implementation_opened": false,
      "producer_direct_mutation_allowed": false,
      "producer_or_policy_may_schedule_only": true,
      "step_or_topology_event_owns_state_mutation": true
    }
  },
  "response_magnitude_surface": {
    "bounded_window_count": 4,
    "max_correction_per_window": 0.07,
    "native_policy_enabled": false,
    "native_policy_name": "native_response_magnitude_policy",
    "native_policy_supported": false,
    "out_of_envelope_blocker": "unbounded_perturbation_envelope_blocked",
    "phase8_ready_input_only": true,
    "response_gain_source": "serialized response gain and max correction per window",
    "source": "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/outputs/n12_response_magnitude_candidate.json",
    "total_bounded_correction_capacity": 0.28
  },
  "trend_stability_fields": {
    "out_of_envelope_blocker": "unbounded_perturbation_envelope_blocked",
    "overcorrection_status": [
      "capped_at_support_threshold",
      "not_applicable_no_response"
    ],
    "saturation_status": [
      "not_applicable_no_response",
      "not_saturated_within_bounded_window"
    ],
    "support_trend": [
      "bounded_correction_needed",
      "mild_support_above_threshold_no_response",
      "source_restored_above_threshold_no_new_response",
      "stable_above_threshold_no_response"
    ]
  }
}
```

## Interpretation Record

```json
{
  "ap_state_after_stress_matrix": {
    "candidate_ap_level": "AP3",
    "claim_boundary_record_pending_iteration7": true,
    "external_proxy_controls_passed": true,
    "final_ap3_supported": false,
    "hidden_target_controls_passed": true,
    "native_support_opened": false,
    "phase8_opened": false,
    "post_hoc_label_controls_passed": true,
    "provisional_ap_level": "AP3_candidate_stress_clean_pending_claim_boundary",
    "self_maintenance_candidate_supported": false,
    "stress_matrix_passed": true
  },
  "plain_language_meaning": "Iteration 6 shows the candidate behaves differently across support-present, support-disrupted, restored, neutral, and no-support-target regimes: it schedules a bounded budgeted response only for the source-current support deficit, avoids false-positive responses when support remains valid, and blocks when no support target is available.",
  "record_id": "n13_i6_interpretation_stress_matrix_v1",
  "record_type": "n13_iteration_6_interpretation_record",
  "remaining_required_work": [
    "identity_goal_ownership_agency_boundary_record_iteration_7",
    "n13_closeout_handoff_iteration_8"
  ],
  "supported_interpretation": "The candidate may be carried forward as an artifact-level AP3 stress-clean support-seeking regulation candidate pending the Iteration 7 claim-boundary record.",
  "unsupported_interpretations": [
    "stress-clean candidate is final supported AP3",
    "support-seeking regulation is agency",
    "support survival is identity acceptance",
    "bounded response is intention",
    "stress behavior proves selfhood or self-maintenance as final support",
    "artifact-level stress behavior is native support"
  ]
}
```

## AP State After Stress Matrix

```json
{
  "candidate_ap_level": "AP3",
  "claim_boundary_record_pending_iteration7": true,
  "external_proxy_controls_passed": true,
  "final_ap3_supported": false,
  "hidden_target_controls_passed": true,
  "native_support_opened": false,
  "phase8_opened": false,
  "post_hoc_label_controls_passed": true,
  "provisional_ap_level": "AP3_candidate_stress_clean_pending_claim_boundary",
  "self_maintenance_candidate_supported": false,
  "stress_matrix_passed": true
}
```

## Checks

```json
{
  "all_required_regimes_present": true,
  "ap_ceiling_after_stress_matrix_recorded": true,
  "budget_and_response_surfaces_recorded": true,
  "claim_boundary_controls_false": true,
  "claim_flags_all_false": true,
  "control_source_passed": true,
  "explicit_restoration_regime_passed": true,
  "final_ap3_not_supported_until_iteration7": true,
  "interpretation_record_present": true,
  "inventory_source_passed": true,
  "native_support_not_opened": true,
  "neutral_perturbation_regime_passed": true,
  "no_support_control_regime_passed": true,
  "phase8_not_opened": true,
  "regulation_source_passed": true,
  "schema_source_passed": true,
  "self_maintenance_not_supported_yet": true,
  "source_current_replay_requirements_recorded": true,
  "src_diff_empty": true,
  "support_disrupted_regime_passed": true,
  "support_present_baseline_passed": true,
  "support_seeking_regulation_survives_controls": true,
  "target_source_passed": true
}
```

## Claim Boundary

```text
stress-clean candidate != final supported AP3
support-seeking regulation != agency
support survival != identity acceptance
bounded response != intention
artifact-level stress matrix != native support
```

## Output Digest

```text
f515ff673d38adba5d401088762040899add0e0f91d29f1f9d37de9100db7100
```
