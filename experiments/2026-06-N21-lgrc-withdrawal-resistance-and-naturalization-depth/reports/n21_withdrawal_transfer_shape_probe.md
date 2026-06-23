# N21 Iteration 4-B - Withdrawal Transfer And Schedule-Shape Probe

## Summary

Status: `passed`

Acceptance state: `accepted_withdrawal_transfer_shape_wr4_candidate_pending_i6`

Output digest: `8179871ea16bd6243c46e28249c1f1e8f12246158d873763fa9ee5909cc64a1f`

Iteration 4-B keeps the I4/I4-A thresholds fixed and tests whether
the bounded withdrawal pattern transfers to a second support route
and to delayed, split, and mixed route schedule shapes.

## Transfer Result

```text
supported_variant_ids = ['reference_single_route', 'alternate_single_route', 'delayed_single_route', 'split_same_route', 'mixed_route_split']
route_transfer_supported = true
schedule_shape_transfer_supported = true
mixed_route_split_supported = true
wr5_supported = false
wr6_supported = false
final_withdrawal_resistance_supported = false
```

## Variant Rows

| Variant | Role | Decision | Packets | Support Margin | Coherence Margin |
| --- | --- | --- | --- | --- | --- |
| `reference_single_route` | `i4_reference_reproduction` | `supported` | `1` | `0.01` | `0.02` |
| `alternate_single_route` | `route_transfer_candidate` | `supported` | `1` | `0.01` | `0.02` |
| `delayed_single_route` | `schedule_delay_candidate` | `supported` | `1` | `0.01` | `0.02` |
| `split_same_route` | `schedule_split_candidate` | `supported` | `2` | `0.01` | `0.02` |
| `mixed_route_split` | `route_and_schedule_split_candidate` | `supported` | `2` | `0.01` | `0.02` |

## Controls

| Control | Status |
| --- | --- |
| `route_transfer_source_current_control` | `passed` |
| `schedule_shape_source_current_control` | `passed` |
| `mixed_route_split_control` | `passed` |
| `threshold_retune_control` | `passed` |

## Claim Boundary

```text
bounded transfer/schedule-shape WR4 candidate = true
WR5 = false
WR6 = false
robust withdrawal resistance = false
support removal resistance = false
final withdrawal resistance = false
native support = false
agency = false
sentience = false
phase8_implementation = false
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_i1_i2_i3_i4_i4a_passed` | `true` | {"i1": "accepted_source_contract_inventory_no_primitive_evidence", "i2": "accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence", "i3": "accepted_active_nulls_fail_closed_no_primitive_evidence", "i4": "accepted_provisional_wr4_withdrawal_candidate_pending_i6", "i4a": "accepted_withdrawal_severity_boundary_mapped_no_removal_overclaim"} |
| `artifact_paths_exist_and_hash` | `true` | {"artifact_count": 62} |
| `i4_reference_reproduced` | `true` | {"reference_row": "reference_single_route", "source_i4_output_digest": "6d80c4dd915c0c5d2b1f67c2af69881d88ab3d632acf828013389f90c53cfb36", "support_margin": 0.01} |
| `route_transfer_variant_distinct_and_supported` | `true` | {"all_controls_passed": true, "bounded_transfer_shape_wr4_candidate_supported": true, "final_withdrawal_resistance_supported": false, "mixed_route_split_supported": true, "rejected_variant_ids": [], "robust_withdrawal_resistance_supported": false, "route_transfer_supported": true, "schedule_shape_transfer_supported": true, "summary_digest": "a1621a953409b6246e972ea5eea98d1c6aeea071ad5a6262c421aa7d278c6cd1", "support_removal_resistance_supported": false, "supported_variant_ids": ["reference_single_route", "alternate_single_route", "delayed_single_route", "split_same_route", "mixed_route_split"], "variant_count": 5, "wr5_supported": false, "wr6_supported": false} |
| `schedule_shape_variants_supported` | `true` | {"all_controls_passed": true, "bounded_transfer_shape_wr4_candidate_supported": true, "final_withdrawal_resistance_supported": false, "mixed_route_split_supported": true, "rejected_variant_ids": [], "robust_withdrawal_resistance_supported": false, "route_transfer_supported": true, "schedule_shape_transfer_supported": true, "summary_digest": "a1621a953409b6246e972ea5eea98d1c6aeea071ad5a6262c421aa7d278c6cd1", "support_removal_resistance_supported": false, "supported_variant_ids": ["reference_single_route", "alternate_single_route", "delayed_single_route", "split_same_route", "mixed_route_split"], "variant_count": 5, "wr5_supported": false, "wr6_supported": false} |
| `mixed_route_split_supported_without_merge_overclaim` | `true` | {"all_controls_passed": true, "bounded_transfer_shape_wr4_candidate_supported": true, "final_withdrawal_resistance_supported": false, "mixed_route_split_supported": true, "rejected_variant_ids": [], "robust_withdrawal_resistance_supported": false, "route_transfer_supported": true, "schedule_shape_transfer_supported": true, "summary_digest": "a1621a953409b6246e972ea5eea98d1c6aeea071ad5a6262c421aa7d278c6cd1", "support_removal_resistance_supported": false, "supported_variant_ids": ["reference_single_route", "alternate_single_route", "delayed_single_route", "split_same_route", "mixed_route_split"], "variant_count": 5, "wr5_supported": false, "wr6_supported": false} |
| `all_variant_replays_stable` | `true` | {"alternate_single_route": true, "delayed_single_route": true, "mixed_route_split": true, "reference_single_route": true, "split_same_route": true} |
| `controls_passed_without_failed_open` | `true` | [{"actual_result": {"route_signature": [{"amount": 0.07, "departure_event_time_key": 1.0, "edge_id": 8, "scheduler_event_index": 1, "source_node_id": 9, "target_node_id": 0}], "row_decision": "supported", "variant_id": "alternate_single_route"}, "blocked_condition": "alternate route is only a label swap without source-current packet evidence", "claim_allowed_when_control_triggers": false, "control_id": "route_transfer_source_current_control", "control_status": "passed", "expected_result": "alternate route has distinct source node/edge and replay-backed run artifacts", "rung_effect": "blocks route-transfer wording if triggered"}, {"actual_result": {"delayed_departure_time": 2.0, "delayed_row_decision": "supported", "split_packet_count": 2, "split_row_decision": "supported"}, "blocked_condition": "schedule-shape transfer is only a prose relabel", "claim_allowed_when_control_triggers": false, "control_id": "schedule_shape_source_current_control", "control_status": "passed", "expected_result": "delayed and split schedules have source-current packet traces and replay", "rung_effect": "blocks schedule-shape transfer wording if triggered"}, {"actual_result": {"gate_statuses": {"boundary_integrity_result": "preserved", "coherence_floor_result": "preserved", "flux_or_leakage_result": "preserved", "support_floor_result": "preserved"}, "row_decision": "supported", "same_basin_preserved": true}, "blocked_condition": "mixed route distribution masks leakage or merge pressure", "claim_allowed_when_control_triggers": false, "control_id": "mixed_route_split_control", "control_status": "passed", "expected_result": "mixed route preserves support/coherence/boundary/flux gates", "rung_effect": "blocks mixed-route wording if triggered"}, {"actual_result": {"boundary_active_degree_floor": 9, "coherence_floor": 10.05, "max_budget_error": 1e-09, "support_floor": 0.06}, "blocked_condition": "I4-B changes thresholds to make variants pass", "claim_allowed_when_control_triggers": false, "control_id": "threshold_retune_control", "control_status": "passed", "expected_result": "I4 support, coherence, boundary, and budget thresholds unchanged", "rung_effect": "blocks transfer evidence if triggered"}] |
| `no_wr5_wr6_or_final_overclaim` | `true` | {"all_controls_passed": true, "bounded_transfer_shape_wr4_candidate_supported": true, "final_withdrawal_resistance_supported": false, "mixed_route_split_supported": true, "rejected_variant_ids": [], "robust_withdrawal_resistance_supported": false, "route_transfer_supported": true, "schedule_shape_transfer_supported": true, "summary_digest": "a1621a953409b6246e972ea5eea98d1c6aeea071ad5a6262c421aa7d278c6cd1", "support_removal_resistance_supported": false, "supported_variant_ids": ["reference_single_route", "alternate_single_route", "delayed_single_route", "split_same_route", "mixed_route_split"], "variant_count": 5, "wr5_supported": false, "wr6_supported": false} |
| `unsafe_claim_flags_false` | `true` | all I4-B rows keep unsafe claim flags false |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

I4-B strengthens the future I6 evidence base by showing that the
bounded `0.10 -> 0.07` withdrawal pattern is not confined to the
single I4 route and schedule shape. A second support route, a delayed
schedule, a split schedule, and a mixed-route split all preserve the
same center basin, support floor, coherence floor, boundary degree,
flux/budget bounds, and replay.

The claim remains deliberately bounded. I4-B supports only a
provisional WR4 transfer/schedule-shape candidate pending I6. It
does not support WR5, WR6, support-removal resistance, robust
withdrawal resistance, native support, agency, sentience, or Phase 8.
