# N21 Iteration 4-A - Withdrawal Severity And Removal Boundary Probe

## Summary

Status: `passed`

Acceptance state: `accepted_withdrawal_severity_boundary_mapped_no_removal_overclaim`

Output digest: `611de6672537df3a27c5a259fe53c09f302771eaceb1d40fac4284cea08558e8`

Iteration 4-A keeps the I4 producer family fixed and sweeps the
declared packetized support surface across mild weakening, floor,
below-floor, strong-withdrawal, and full-removal rows.

## Boundary Result

```text
supported_positive_margin_amounts = [0.09, 0.07]
floor_boundary_amounts = [0.06]
fail_closed_amounts = [0.05, 0.03, 0.0]
max_positive_margin_supported_withdrawal_amount = 0.03
failure_boundary_interval = [0.06, 0.05]
full_removal_status = rejected
support_removal_resistance_supported = false
robust_withdrawal_resistance_supported = false
```

## Severity Rows

| Packet Amount | Withdrawal | Decision | Role | Failure Modes |
| --- | --- | --- | --- | --- |
| `0.09` | `0.01` | `supported` | `positive_margin_withdrawal_candidate` | `none` |
| `0.07` | `0.03` | `supported` | `positive_margin_withdrawal_candidate` | `none` |
| `0.06` | `0.04` | `partial` | `floor_boundary_zero_margin` | `none` |
| `0.05` | `0.05` | `rejected` | `fail_closed_boundary_row` | `support_floor_crossed` |
| `0.03` | `0.07` | `rejected` | `fail_closed_boundary_row` | `support_floor_crossed, coherence_floor_crossed` |
| `0.0` | `0.1` | `rejected` | `fail_closed_boundary_row` | `support_floor_crossed, coherence_floor_crossed` |

## Support Relevance Control

```text
control_status = passed
center_coherence_delta = 0.1
source_coherence_delta = 0.1
packet_count_delta = 1
event_count_delta = 5
```

## Claim Boundary

```text
bounded support-weakening scope = supported
support removal resistance = false
robust withdrawal resistance = false
final withdrawal resistance = false
native support = false
agency = false
sentience = false
phase8_implementation = false
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_i1_i2_i3_i4_passed` | `true` | {"i1": "accepted_source_contract_inventory_no_primitive_evidence", "i2": "accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence", "i3": "accepted_active_nulls_fail_closed_no_primitive_evidence", "i4": "accepted_provisional_wr4_withdrawal_candidate_pending_i6"} |
| `severity_amounts_match_plan` | `true` | {"actual": [0.09, 0.07, 0.06, 0.05, 0.03, 0.0], "expected": [0.09, 0.07, 0.06, 0.05, 0.03, 0.0]} |
| `artifact_paths_exist_and_hash` | `true` | {"artifact_count": 54} |
| `i4_row_reproduced` | `true` | {"row_decision": "supported", "source_i4_output_digest": "6d80c4dd915c0c5d2b1f67c2af69881d88ab3d632acf828013389f90c53cfb36", "support_margin": 0.01, "support_packet_amount": 0.07} |
| `support_relevance_control_passed` | `true` | {"actual_result": {"baseline_packet_amount": 0.1, "center_coherence_delta": 0.1, "event_count_delta": 5, "packet_count_delta": 1, "removal_packet_amount": 0.0, "source_coherence_delta": 0.1}, "blocked_condition": "support surface can be changed or removed with no measurable source-current geometric effect", "claim_allowed_when_control_triggers": false, "control_id": "support_necessity_or_relevance_control", "control_status": "passed", "expected_result": "support removal changes coherence, packet records, and event trace", "rung_effect": "demotes positive rows to same-basin invariance under irrelevant support perturbation if triggered"} |
| `positive_boundary_and_fail_closed_rows_present` | `true` | {"boundary_summary_digest": "d8a2d786434e4f1f33c701bede82f84a90ae2e19e32a41faef570ab021356c28", "bounded_support_weakening_scope_supported": true, "fail_closed_amounts": [0.05, 0.03, 0.0], "failure_boundary_interval": [0.06, 0.05], "floor_boundary_amounts": [0.06], "floor_boundary_packet_amount": 0.06, "full_removal_failure_modes": ["support_floor_crossed", "coherence_floor_crossed"], "full_removal_status": "rejected", "max_positive_margin_supported_withdrawal_amount": 0.03, "min_positive_margin_supported_packet_amount": 0.07, "robust_withdrawal_resistance_supported": false, "severity_boundary_interpretation": "I4 survives one mild weakening. I4-A maps the local boundary: positive-margin rows above the 0.06 floor support bounded weakening, the exact floor row is zero-margin partial, and rows below the floor fail closed. Full removal is rejected.", "support_removal_resistance_supported": false, "supported_positive_margin_amounts": [0.09, 0.07]} |
| `full_removal_rejected_no_removal_overclaim` | `true` | {"boundary_summary_digest": "d8a2d786434e4f1f33c701bede82f84a90ae2e19e32a41faef570ab021356c28", "bounded_support_weakening_scope_supported": true, "fail_closed_amounts": [0.05, 0.03, 0.0], "failure_boundary_interval": [0.06, 0.05], "floor_boundary_amounts": [0.06], "floor_boundary_packet_amount": 0.06, "full_removal_failure_modes": ["support_floor_crossed", "coherence_floor_crossed"], "full_removal_status": "rejected", "max_positive_margin_supported_withdrawal_amount": 0.03, "min_positive_margin_supported_packet_amount": 0.07, "robust_withdrawal_resistance_supported": false, "severity_boundary_interpretation": "I4 survives one mild weakening. I4-A maps the local boundary: positive-margin rows above the 0.06 floor support bounded weakening, the exact floor row is zero-margin partial, and rows below the floor fail closed. Full removal is rejected.", "support_removal_resistance_supported": false, "supported_positive_margin_amounts": [0.09, 0.07]} |
| `all_replays_stable` | `true` | {"n21_i4a_row_amount_0_00": true, "n21_i4a_row_amount_0_03": true, "n21_i4a_row_amount_0_05": true, "n21_i4a_row_amount_0_06": true, "n21_i4a_row_amount_0_07": true, "n21_i4a_row_amount_0_09": true} |
| `unsafe_claim_flags_false` | `true` | all severity rows keep unsafe claim flags false |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

I4-A does not invalidate I4. It sharpens its scope. Geometrically,
the same center basin survives positive-margin weakening at `0.09`
and `0.07`, reaches a zero-margin floor boundary at `0.06`, and
fails closed below the declared support floor at `0.05`, `0.03`,
and `0.00`. The full-removal row is rejected, so the supported
claim remains bounded support weakening, not support-removal
resistance or broad withdrawal resistance.

The support-relevance control also passes: removing the support
surface changes source-current coherence, packet records, and event
trace. That prevents the positive rows from being dismissed as
same-basin invariance under an irrelevant support perturbation.
