# N13 Support-Derived Target Candidate

## Status

Status: `passed`.

```text
support_derived_target_candidate = true
provisional_ap_level = AP2
final_ap3_supported = false
self_maintenance_candidate_supported = false
phase8_opened = false
native_support_opened = false
```

Iteration 3 isolates a source-current support-state target rule. It
does not assign final AP3 support; support-seeking regulation and
controls remain pending for Iterations 4-7.

## Target Rule

```json
{
  "expression": "final_A_support_retention >= support_survival_threshold",
  "input_fields": [
    "final_A_support_retention",
    "support_survival_threshold"
  ],
  "runtime_visible_inputs": [
    "final_A_support_retention",
    "support_survival_threshold",
    "withdrawal_depth",
    "restoration_fraction"
  ],
  "support_area_digest": "c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb",
  "support_area_id": "n07_support_area_A_v1",
  "threshold_source": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_13_identity_support_withdrawal_baseline.json"
}
```

## Lane Records

| Lane | Final support | Threshold | Target state | Rule matches source |
| --- | ---: | ---: | --- | --- |
| `support_intact_reference` | 0.9731535762447039 | 0.85 | `support_valid` | `true` |
| `mild_support_weakening` | 0.8758382186202335 | 0.85 | `support_valid` | `true` |
| `n09_matched_partial_support_withdrawal` | 0.7298651821835279 | 0.85 | `support_disrupted` | `true` |
| `restored_after_n09_partial_withdrawal` | 0.9244958974324687 | 0.85 | `support_valid` | `true` |

## External Proxy Separation

```json
{
  "external_proxy_fields_available_but_excluded": [
    "error_policy_digest",
    "proxy_surface_digest",
    "regulation_policy_digest",
    "regulation_response_digest"
  ],
  "n09_proxy_row_role": "external_proxy_regulation_baseline_only",
  "n09_withdrawal_digest_is_lane_link_only": true,
  "target_uses_external_proxy_fields": false
}
```

## Post-Hoc And Hidden-Target Audits

```json
{
  "hidden_target_audit": {
    "full_hidden_target_control_pending_iteration_5": true,
    "hidden_support_target_required": false,
    "target_fields_declared": true
  },
  "post_hoc_label_audit": {
    "full_post_hoc_label_control_pending_iteration_5": true,
    "lane_digests_preexist_n13": true,
    "n13_did_not_choose_threshold": true,
    "target_rule_matches_all_source_lanes": true,
    "threshold_preexists_n13": true
  }
}
```

## Pending Gates

```json
[
  "support_error_signal_not_evaluated_until_iteration_4",
  "bounded_response_magnitude_not_evaluated_until_iteration_4",
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
  "claim_flags_all_false": true,
  "explicit_restoration_case_present": true,
  "final_ap3_not_assigned": true,
  "inventory_source_passed": true,
  "n07_support_row_present": true,
  "n09_external_proxy_row_present": true,
  "n10_disrupted_support_blocks": true,
  "n10_explicit_restoration_resumes": true,
  "n10_support_matrix_row_present": true,
  "provisional_ap_level_ap2": true,
  "schema_source_passed": true,
  "self_maintenance_not_supported_yet": true,
  "source_current_lane_digests_present": true,
  "src_diff_empty": true,
  "support_valid_and_disrupted_cases_present": true,
  "target_derivation_not_external_proxy_label": true,
  "target_derivation_not_post_hoc_label": true,
  "target_rule_matches_all_lanes": true
}
```

## Claim Boundary

```text
support-derived target candidate != support-seeking regulation
support-derived target != semantic goal ownership
support survival != identity acceptance
provisional AP2 target candidate != final AP3 support
self-maintenance candidate != selfhood
artifact-level target derivation != native support
```

## Output Digest

```text
917e65721362fcda37ea4777489a5e3289a35ef550a16b3774884c803584ac3e
```
