# N13 Support-Seeking Regulation Candidate

## Status

Status: `passed`.

```text
support_seeking_regulation_candidate = true
candidate_ap_level = AP3
provisional_ap_level = AP3_candidate_pending_controls
final_ap3_supported = false
self_maintenance_candidate_supported = false
phase8_opened = false
native_support_opened = false
```

Iteration 4 records a bounded support-error response candidate against
the Iteration 3 source-current support target. It does not freeze final
AP3 support; external-proxy, hidden-target, post-hoc-label, disruption,
restoration, and claim-boundary controls remain pending for Iterations
5-7.

## Support Error Signal

```json
{
  "error_expression": "max(0, support_survival_threshold - final_A_support_retention)",
  "error_is_external_proxy": false,
  "error_is_source_current_support_state_derived": true,
  "error_name": "support_retention_threshold_deficit",
  "runtime_visible_inputs": [
    "final_A_support_retention",
    "support_survival_threshold",
    "lane_digest",
    "support_area_digest"
  ]
}
```

## Response Magnitude Surface

```json
{
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
}
```

## Lane Responses

| Lane | Target before response | Support error | Scheduled response | Windows | Out of envelope | Post-response estimate | Trend |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- |
| `support_intact_reference` | `support_valid` | 0.0 | 0 | 0 | `false` | 0.973153576245 | `stable_above_threshold_no_response` |
| `mild_support_weakening` | `support_valid` | 0.0 | 0 | 0 | `false` | 0.87583821862 | `mild_support_above_threshold_no_response` |
| `n09_matched_partial_support_withdrawal` | `support_disrupted` | 0.120134817816 | 0.120134817816 | 2 | `false` | 0.85 | `bounded_correction_needed` |
| `restored_after_n09_partial_withdrawal` | `support_valid` | 0.0 | 0 | 0 | `false` | 0.924495897432 | `source_restored_above_threshold_no_new_response` |

## Budget And Mutation Boundary

```json
{
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
}
```

## Stability Fields

```json
{
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
```

## Support-Disrupted Negative Control Record

```json
{
  "bounded_response_is_schedule_candidate_not_raw_support_pass": true,
  "full_stress_control_pending_iteration_6": true,
  "raw_disrupted_lane_count": 1,
  "raw_disrupted_lanes": [
    "n09_matched_partial_support_withdrawal"
  ],
  "raw_disrupted_lanes_not_counted_as_supported_before_response": true
}
```

## Pending Controls

```json
[
  "external_proxy_controls_not_run_until_iteration_5",
  "hidden_target_controls_not_run_until_iteration_5",
  "post_hoc_label_controls_not_run_until_iteration_5",
  "support_disruption_restoration_stress_not_run_until_iteration_6",
  "claim_boundary_record_not_frozen_until_iteration_7"
]
```

## Checks

```json
{
  "all_source_lanes_within_bounded_window": true,
  "bounded_window_recorded": true,
  "budget_debit_surface_recorded": true,
  "candidate_ap3_recorded_without_final_support": true,
  "claim_boundary_controls_false": true,
  "claim_flags_all_false": true,
  "external_proxy_fields_excluded_from_support_error": true,
  "inventory_source_passed": true,
  "n12_phase8_source_passed": true,
  "n12_response_source_passed": true,
  "native_support_not_opened": true,
  "out_of_envelope_blocker_recorded": true,
  "overcorrection_status_recorded": true,
  "pending_controls_recorded": true,
  "phase8_not_opened": true,
  "response_magnitude_surface_recorded": true,
  "response_needed_case_present": true,
  "response_packet_scheduling_boundary_recorded": true,
  "saturation_status_recorded": true,
  "scheduled_response_does_not_overcorrect": true,
  "schema_source_passed": true,
  "self_maintenance_not_supported_yet": true,
  "src_diff_empty": true,
  "support_disrupted_negative_control_recorded": true,
  "support_error_signal_recorded": true,
  "support_trend_recorded": true,
  "target_source_passed": true
}
```

## Claim Boundary

```text
support-seeking regulation candidate != agency
bounded response != intention
support error != semantic goal ownership
candidate AP3 != final supported AP3
self-maintenance candidate != selfhood
artifact-level response scheduling != native support
N12 response magnitude readiness != Phase 8 implementation
```

## Output Digest

```text
a6c367246eaeba14953b87c4a89862238b5bde4568308f1ee4c7ef1d9c85116b
```
