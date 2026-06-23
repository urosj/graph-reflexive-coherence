# N21 Iteration 5-B - Eventful Post-Probe Continuation Probe

## Summary

Status: `passed`

Acceptance state: `accepted_provisional_eventful_post_probe_derived_nd3_candidate_pending_i6`

Output digest: `5cdb24a076ae5a4e814a523663ad460754937f3650f3359da86d3c9f5147cec6`

Iteration 5-B starts from a probe-present final snapshot, disables the
original probe support, and then runs a distinct non-original post-probe
challenge packet so the post-probe continuation is eventful rather than
static snapshot-only replay.

## Candidate Row

```text
row_id = n21_i5b_row_01_eventful_post_probe_continuation
row_decision = supported
nd_ladder_rung = ND3
nd_evidence_variant = eventful_post_probe_derived_state
nd_ladder_rung_status = provisional_pending_iteration6_control_matrix
final_naturalization_depth_supported = false
ND4 = false
ND5 = false
```

## Eventful Post-Probe Geometry

```text
challenge_packet = {'source_node_id': 0, 'target_node_id': 2, 'edge_id': 1, 'amount': 0.01, 'departure_event_time_key': 2.0, 'scheduler_event_index': 2, 'packet_index': 0}
eventful_post_probe_event_count = 5
center_coherence_delta_after_challenge = -0.009999999999999787
support_floor_result = preserved
coherence_floor_result = preserved
boundary_integrity_result = preserved
flux_or_leakage_result = preserved
active_original_probe_packet_records_in_eventful_window = 0
```

## Controls

| Control | Status |
| --- | --- |
| `probe_effect_absent_control` | `passed` |
| `post_probe_state_derivation_control` | `passed` |
| `eventful_continuation_control` | `passed` |
| `original_probe_reintroduction_control` | `passed` |
| `hidden_producer_support_control` | `passed` |
| `support_annotation_relabel_control` | `passed` |
| `post_hoc_trace_construction_control` | `passed` |
| `eventful_replay_control` | `passed` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_i1_to_i5a_passed` | `true` | {"i1": "accepted_source_contract_inventory_no_primitive_evidence", "i2": "accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence", "i3": "accepted_active_nulls_fail_closed_no_primitive_evidence", "i4": "accepted_provisional_wr4_withdrawal_candidate_pending_i6", "i5": "accepted_provisional_nd3_naturalization_candidate_pending_i6", "i5a": "accepted_provisional_post_probe_derived_nd3_candidate_pending_i6"} |
| `candidate_evidence_fields_present` | `true` | {"required_field_count": 33} |
| `artifact_paths_exist_and_hash` | `true` | {"artifact_count": 21} |
| `derived_report_only_false` | `true` | false |
| `probe_effect_detected` | `true` | {"center_coherence_delta": 0.03999999999999915, "packet_count_delta": 1, "pre_probe_state_digest": "aa560ca1ae707821257ce9f3d3388871efabbf6dbb2ccca1a20b8c612094054e", "probe_effect_delta_digest": "8f3ed3b6152d315772fbe0e1dab9c09ccb354cfbd09498ce2c99701d3c77ff3a", "probe_effect_detected": true, "probe_effect_fields": ["center_node_coherence", "source_node_coherence", "packet_records", "local_update_count", "causal_spark_diagnostic_count"], "probe_event_count": 5, "probe_present_final_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "source_coherence_delta": -0.03999999999999915} |
| `post_probe_state_derivation_source_valid` | `true` | {"post_probe_state_carried_into_probe_absent_run": true, "post_probe_state_derivation_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "post_probe_state_derivation_source": "probe_present_final_snapshot", "probe_absent_initial_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "probe_absent_initial_state_matches_derived_post_probe_state": true, "source_snapshot_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_eventful_post_probe_artifacts/probe_present_baseline_final_snapshot.json", "state_derivation_digest": "d13556c8089437df94c8010b611615a6d3a0568287a9435b62c6158afaec4dd3"} |
| `eventful_post_probe_continuation_present` | `true` | {"center_coherence_delta_after_challenge": -0.009999999999999787, "challenge_is_center_outward": true, "challenge_packet": {"amount": 0.01, "departure_event_time_key": 2.0, "edge_id": 1, "packet_index": 0, "scheduler_event_index": 2, "source_node_id": 0, "target_node_id": 2}, "event_counts_by_kind": {"lgrc9v3_causal_spark_candidate": 1, "lgrc9v3_local_update": 1, "lgrc9v3_packet_arrival": 1, "lgrc9v3_packet_arrival_eligibility": 1, "lgrc9v3_packet_departure": 1}, "eventful_post_probe_event_count": 5, "original_probe_route_reused": false, "target_node_2_coherence_delta_after_challenge": 0.04} |
| `original_probe_not_reintroduced` | `true` | {"active_original_probe_packet_records_in_eventful_window": 0, "active_original_probe_schedule_disabled": true, "active_probe_queue_empty": true, "historical_probe_provenance_allowed": true, "historical_probe_provenance_present": true, "in_flight_probe_budget": 0.0, "probe_absent_runtime_input": true, "probe_residue_digest_absent": false, "probe_support_not_used_as_evidence": true} |
| `post_probe_same_basin_preserved` | `true` | {"active_degree_same": true, "basin_member_count_same": true, "center_basin_id_same": true, "center_node_id_same": true, "topology_signature_same": true} |
| `support_coherence_boundary_flux_gates_preserved` | `true` | {"boundary_integrity_result": "preserved", "coherence_floor_result": "preserved", "flux_or_leakage_result": "preserved", "support_floor_result": "preserved"} |
| `eventful_replay_passed` | `true` | {"all_replay_modes_passed": true, "artifact_id": "n21_i5b_eventful_post_probe_replay", "artifact_replay": {"artifact_path_exists": true, "source_run_artifact_digest": "5f2907610ed8cfd6723590bd8ec22b52f0e4f0b2dad32b0416b75bf3d5bc3a21", "status": "passed"}, "duplicate_eventful_replay": {"duplicate_geometry_digest": "cef5db3b1b9e068aec1c632f6ea15120b9e1081071c161a5b2cd89069dfc61aa", "original_geometry_digest": "cef5db3b1b9e068aec1c632f6ea15120b9e1081071c161a5b2cd89069dfc61aa", "status": "passed"}, "duplicate_run_artifact_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_eventful_post_probe_artifacts/eventful_post_probe_duplicate_run.json", "eventful_post_probe_replay": {"active_original_probe_packet_records_in_eventful_window": 0, "event_count": 5, "status": "passed", "window_count": 3}, "replay_digest": "f51d39859b0d3870aed371e785b183d10e6beee37586774eac312f12d1d9b2e5", "snapshot_load_replay": {"loaded_snapshot_geometry_digest": "cef5db3b1b9e068aec1c632f6ea15120b9e1081071c161a5b2cd89069dfc61aa", "original_geometry_digest": "cef5db3b1b9e068aec1c632f6ea15120b9e1081071c161a5b2cd89069dfc61aa", "status": "passed"}, "source_final_snapshot_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_eventful_post_probe_artifacts/eventful_post_probe_final_snapshot.json", "source_run_artifact_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_eventful_post_probe_artifacts/eventful_post_probe_run.json"} |
| `row_controls_passed_without_failed_open` | `true` | [{"actual_result": {"center_coherence_delta": 0.03999999999999915, "packet_count_delta": 1, "pre_probe_state_digest": "aa560ca1ae707821257ce9f3d3388871efabbf6dbb2ccca1a20b8c612094054e", "probe_effect_delta_digest": "8f3ed3b6152d315772fbe0e1dab9c09ccb354cfbd09498ce2c99701d3c77ff3a", "probe_effect_detected": true, "probe_effect_fields": ["center_node_coherence", "source_node_coherence", "packet_records", "local_update_count", "causal_spark_diagnostic_count"], "probe_event_count": 5, "probe_present_final_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "source_coherence_delta": -0.03999999999999915}, "blocked_condition": "probe-present run has no measurable effect", "claim_allowed_when_control_triggers": false, "control_id": "probe_effect_absent_control", "control_status": "passed", "expected_result": "probe changes source-current geometry", "rung_effect": "blocks eventful post-probe variant if triggered"}, {"actual_result": {"post_probe_state_carried_into_probe_absent_run": true, "post_probe_state_derivation_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "post_probe_state_derivation_source": "probe_present_final_snapshot", "probe_absent_initial_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "probe_absent_initial_state_matches_derived_post_probe_state": true, "source_snapshot_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_eventful_post_probe_artifacts/probe_present_baseline_final_snapshot.json", "state_derivation_digest": "d13556c8089437df94c8010b611615a6d3a0568287a9435b62c6158afaec4dd3"}, "blocked_condition": "eventful replay did not start from post-probe state", "claim_allowed_when_control_triggers": false, "control_id": "post_probe_state_derivation_control", "control_status": "passed", "expected_result": "eventful replay initial state matches derived checkpoint", "rung_effect": "blocks eventful post-probe variant if triggered"}, {"actual_result": {"center_coherence_delta_after_challenge": -0.009999999999999787, "challenge_is_center_outward": true, "challenge_packet": {"amount": 0.01, "departure_event_time_key": 2.0, "edge_id": 1, "packet_index": 0, "scheduler_event_index": 2, "source_node_id": 0, "target_node_id": 2}, "event_counts_by_kind": {"lgrc9v3_causal_spark_candidate": 1, "lgrc9v3_local_update": 1, "lgrc9v3_packet_arrival": 1, "lgrc9v3_packet_arrival_eligibility": 1, "lgrc9v3_packet_departure": 1}, "eventful_post_probe_event_count": 5, "original_probe_route_reused": false, "target_node_2_coherence_delta_after_challenge": 0.04}, "blocked_condition": "post-probe continuation is static only", "claim_allowed_when_control_triggers": false, "control_id": "eventful_continuation_control", "control_status": "passed", "expected_result": "non-original post-probe runtime events occur", "rung_effect": "blocks eventful wording if triggered"}, {"actual_result": {"active_original_probe_packet_records_in_eventful_window": 0, "active_original_probe_schedule_disabled": true, "active_probe_queue_empty": true, "historical_probe_provenance_allowed": true, "historical_probe_provenance_present": true, "in_flight_probe_budget": 0.0, "probe_support_not_used_as_evidence": true}, "blocked_condition": "original probe route is reintroduced during eventful replay", "claim_allowed_when_control_triggers": false, "control_id": "original_probe_reintroduction_control", "control_status": "passed", "expected_result": "historical provenance allowed, active original probe absent", "rung_effect": "blocks ND3 and stronger if triggered"}, {"actual_result": "active_original_probe_schedule_disabled=true", "blocked_condition": "hidden producer scaffold preserves post-probe state", "claim_allowed_when_control_triggers": false, "control_id": "hidden_producer_support_control", "control_status": "passed", "expected_result": "only declared non-original challenge packet is scheduled", "rung_effect": "blocks ND4 and stronger if triggered"}, {"actual_result": "probe_support_not_used_as_evidence=true", "blocked_condition": "support annotation replaces source-current support", "claim_allowed_when_control_triggers": false, "control_id": "support_annotation_relabel_control", "control_status": "passed", "expected_result": "source-current support/coherence gates are used", "rung_effect": "blocks ND4 and stronger if triggered"}, {"actual_result": "probe_present_final_snapshot -> eventful_post_probe_initial -> eventful_runtime_trace", "blocked_condition": "eventful trace assembled after outcome inspection", "claim_allowed_when_control_triggers": false, "control_id": "post_hoc_trace_construction_control", "control_status": "passed", "expected_result": "state derivation and event trace recorded from source artifacts", "rung_effect": "blocks ND2 and stronger if triggered"}, {"actual_result": "passed", "blocked_condition": "eventful post-probe replay diverges", "claim_allowed_when_control_triggers": false, "control_id": "eventful_replay_control", "control_status": "passed", "expected_result": "snapshot and duplicate eventful replay geometry match source run", "rung_effect": "blocks ND3 and stronger if triggered"}] |
| `provisional_eventful_nd3_no_final_closeout` | `true` | {"nd_evidence_variant": "eventful_post_probe_derived_state", "nd_ladder_rung": "ND3", "nd_ladder_rung_status": "provisional_pending_iteration6_control_matrix"} |
| `unsafe_claim_flags_false` | `true` | {"agency": false, "consciousness": false, "fully_native_integration": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false} |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

5-B strengthens 5-A by replacing static post-probe snapshot replay with
an eventful post-probe continuation window. The original probe changed
the state, the eventful run starts from that derived post-probe state,
and the original probe route is not reintroduced. The eventful packet
runs from the center basin outward to a neighbor, so it is a small
post-probe challenge rather than renewed support.

The same basin remains within support, coherence, boundary, and
flux/budget gates, and duplicate eventful replay is stable. The claim
remains a provisional eventful post-probe-derived ND3 candidate
pending I6; it does not support ND4, ND5, general naturalization
depth, native support, agency, sentience, Phase 8, or ant ecology.
