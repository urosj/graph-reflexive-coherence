# N13 Support-Condition Inventory

## Status

Status: `passed`.

```text
target_ap_ceiling = AP3
iteration_ceiling = AP2_inventory_only
phase8_opened = false
native_support_opened = false
identity_acceptance_opened = false
agency_claim_opened = false
```

Iteration 1 is an inventory only. It records support-state, external
proxy, producer-decision, budget, replay, and claim-boundary fields
without assigning AP3 self-maintenance support.

## Inventory Rows

| Row | Mechanism | Role | AP | Self-maintenance candidate | Source |
| --- | --- | --- | --- | --- | --- |
| `n13_i1_row_01_n07_support_withdrawal_baseline` | `n07_support_survival_disruption_restoration_baseline` | `support_state_baseline` | `AP2` | `false` | `experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_13_identity_support_withdrawal_baseline.json` |
| `n13_i1_row_02_n09_bounded_external_proxy_regulation` | `n09_bounded_goal_proxy_regulation` | `external_proxy_regulation_baseline` | `AP1` | `false` | `experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_9_gpr6_closeout.json` |
| `n13_i1_row_03_n10_support_sensitive_matrix` | `n10_support_sensitive_full_composition_matrix` | `support_sensitive_integration_baseline` | `AP2` | `false` | `experiments/2026-05-N10-lgrc-agentic-like-integration/outputs/n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json` |
| `n13_i1_row_04_n10_final_handoff` | `n10_bounded_artifact_only_support_sensitive_handoff` | `bounded_artifact_only_integration_handoff` | `AP2` | `false` | `experiments/2026-05-N10-lgrc-agentic-like-integration/outputs/n10_iteration_15_hypothesis_c_closeout_and_handoff.json` |
| `n13_i1_row_05_n11_gali7_artifact_envelope` | `n11_gali7_artifact_only_generalization_envelope` | `generalization_envelope` | `AP0` | `false` | `experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_12_final_closeout_and_handoff.json` |
| `n13_i1_row_06_n12_phase8_readiness_inputs` | `n12_route_memory_and_response_magnitude_readiness_inputs` | `phase8_ready_input_records` | `AP1` | `false` | `experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/outputs/n12_phase8_readiness_matrix.json` |
| `n13_i1_row_07_n12_closeout_boundary` | `n12_closeout_n13_boundary` | `handoff_and_claim_boundary` | `AP0` | `false` | `experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/outputs/n12_closeout_and_handoff.json` |

## Summary

```json
{
  "boundary_rows": [
    "n13_i1_row_05_n11_gali7_artifact_envelope",
    "n13_i1_row_07_n12_closeout_boundary"
  ],
  "external_proxy_rows": [
    "n13_i1_row_02_n09_bounded_external_proxy_regulation"
  ],
  "phase8_ready_contract_inputs": [
    "native_route_conductance_memory_policy",
    "native_response_magnitude_policy"
  ],
  "provisional_ap_counts": {
    "AP0": 2,
    "AP1": 2,
    "AP2": 3,
    "AP3": 0
  },
  "row_count": 7,
  "support_condition_rows": [
    "n13_i1_row_01_n07_support_withdrawal_baseline",
    "n13_i1_row_03_n10_support_sensitive_matrix",
    "n13_i1_row_04_n10_final_handoff"
  ],
  "theory_sensitive_blockers": [
    "native_identity_acceptance_validator",
    "native_agentic_like_integration_policy"
  ]
}
```

## Blocked Inputs

```json
[
  "identity acceptance",
  "runtime identity acceptance",
  "semantic goal ownership",
  "agency",
  "fully native agentic-like integration"
]
```

## Checks

```json
{
  "boundary_rows_present": true,
  "claim_flags_all_false": true,
  "every_row_has_source_report_sha256": true,
  "every_row_has_source_sha256": true,
  "every_row_has_support_state_fields": true,
  "external_proxy_rows_present": true,
  "identity_acceptance_not_consumed": true,
  "n10_support_matrix_present": true,
  "n12_handoff_boundary_present": true,
  "native_support_not_opened": true,
  "no_ap3_claimed_in_iteration_1": true,
  "phase8_not_opened": true,
  "source_artifacts_all_present": true,
  "source_reports_all_present": true,
  "src_diff_empty": true,
  "support_condition_rows_present": true
}
```

## Claim Boundary

```text
support-seeking regulation != agency
self-maintenance candidate != selfhood
support survival != identity acceptance
support-derived target != semantic goal ownership
bounded response != intention
artifact replay != native support
N12 NAT4 readiness != Phase 8 implementation
```

## Output Digest

```text
4c8cd0a1ea074d27ff1a7cd5cdd176b789ef57da808223c1fa08750355732e23
```
