# N21 Iteration 5-A - Post-Probe Derivation Persistence Probe

## Summary

Status: `passed`

Acceptance state: `accepted_provisional_post_probe_derived_nd3_candidate_pending_i6`

Output digest: `311440952d246a6fa1748f3a215ae8d8513c4bd8c29eb0fcce346ecf76060dc2`

Iteration 5-A tests the stronger post-probe derivation question:
probe-present state, derived post-probe checkpoint, active probe removed,
then no-probe replay from that derived state.

## Candidate Row

```text
row_id = n21_i5a_row_01_post_probe_derived_state_persistence
row_decision = supported
nd_ladder_rung = ND3
nd_evidence_variant = post_probe_derived_state
nd_ladder_rung_status = provisional_pending_iteration6_control_matrix
primitive_claim_allowed = true
```

## Derivation

```text
post_probe_state_derivation_source = probe_present_final_snapshot
probe_absent_initial_state_matches_derived_post_probe_state = true
post_probe_state_carried_into_probe_absent_run = true
probe_effect_detected = true
center_coherence_delta = 0.03999999999999915
source_coherence_delta = -0.03999999999999915
packet_count_delta = 1
```

## Active Probe State

```text
historical_probe_provenance_present = true
active_probe_schedule_disabled = true
active_probe_queue_empty = true
in_flight_probe_budget = 0.0
active_probe_packet_records_in_replay = 0
```

## Post-Probe Geometry

```text
post_probe_same_basin_continuation_status = preserved
post_probe_support_score = 10.0
post_probe_support_floor = 9.95
post_probe_center_coherence = 10.04
post_probe_coherence_floor = 9.95
post_probe_active_degree = 9
post_probe_budget_error = 1.4210854715202004e-14
replay_kind = static_post_probe_snapshot_replay
eventful_post_probe_continuation = false
```

## Boundary

```text
post_probe_aftereffect_evidence_supported = true
final_naturalization_depth_supported = false
ND4_or_ND5_supported = false
agency = false
native_support = false
sentience = false
phase8_implementation = false
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_i1_to_i5_passed` | `true` | {"i1": "accepted_source_contract_inventory_no_primitive_evidence", "i2": "accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence", "i3": "accepted_active_nulls_fail_closed_no_primitive_evidence", "i4": "accepted_provisional_wr4_withdrawal_candidate_pending_i6", "i5": "accepted_provisional_nd3_naturalization_candidate_pending_i6"} |
| `candidate_evidence_fields_present` | `true` | {"required_field_count": 33} |
| `artifact_paths_exist_and_hash` | `true` | [{"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derivation_replay.json", "sha256": "06c823abad668a5f85e019eabc9c4458bf323fdf6d3df716fb4b1ba3b24fef98"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derivation_trace.json", "sha256": "8ce7245725d5de2b77a40147687679eb3ef532fa7fc68a20f44c36fe59186dfe"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived-checkpoint-00000000.json", "sha256": "0ecd4c85a9b86ae20e7c371764afc5f1b87fe89a2ae625e2c21e08e47d494053"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived-checkpoint-00000001.json", "sha256": "e2524df98ee5cae46676258c56b8a93bb8c0a1b7a9beee8a75067960bdc6aaf3"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived_events.jsonl", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived_final_snapshot.json", "sha256": "8603a99a60aac29595ef4c8b36485850d5f916446d5abfda6be8d7f97e47b1b9"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived_initial_snapshot.json", "sha256": "8603a99a60aac29595ef4c8b36485850d5f916446d5abfda6be8d7f97e47b1b9"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived_run.json", "sha256": "d79ea323b3af96918df87b6c53335f0285c176749fc5c6ddd93a442409a7923e"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline-checkpoint-00000000.json", "sha256": "64dbbaec093718f083cfc524a4ad88543cd301d597e96b9a6192182ffb019474"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline-checkpoint-00000001.json", "sha256": "d6874d8f091b086bb19b36c1f0dc11025c76bed235c3ef82acd5b63f21f821e4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline_events.jsonl", "sha256": "122c24887a5ab926cdd7df9e3123b6f0e4f4953e36d6f37ddbaf81a9d7e1cdd1"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline_final_snapshot.json", "sha256": "9322b86dae10942ea2dea0b372993f9b75009db60a33144abd1bdec7a25f9d2a"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline_initial_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline_run.json", "sha256": "21d86bcd811a24efc93f0d2c4390b4a627f5ec916661e74c0c89a1a74eb39540"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/runtime_config.json", "sha256": "c6f7b67b64940d7765dc71b9cdfe0a8b3b68a2230300188a0743d6024f364a4e"}] |
| `derived_report_only_false` | `true` | false |
| `probe_effect_detected` | `true` | {"center_coherence_delta": 0.03999999999999915, "packet_count_delta": 1, "pre_probe_state_digest": "aa560ca1ae707821257ce9f3d3388871efabbf6dbb2ccca1a20b8c612094054e", "probe_effect_delta_digest": "8f3ed3b6152d315772fbe0e1dab9c09ccb354cfbd09498ce2c99701d3c77ff3a", "probe_effect_detected": true, "probe_effect_fields": ["center_node_coherence", "source_node_coherence", "packet_records", "local_update_count", "causal_spark_diagnostic_count"], "probe_event_count": 5, "probe_present_final_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "source_coherence_delta": -0.03999999999999915} |
| `post_probe_state_derivation_source_valid` | `true` | {"post_probe_state_carried_into_probe_absent_run": true, "post_probe_state_derivation_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "post_probe_state_derivation_source": "probe_present_final_snapshot", "probe_absent_initial_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "probe_absent_initial_state_matches_derived_post_probe_state": true, "source_snapshot_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline_final_snapshot.json", "state_derivation_digest": "1440a81727bea11cc9132322360f421184b115273b6c57ce43f05d7937d948ac"} |
| `active_probe_removed_historical_provenance_preserved` | `true` | {"active_probe_packet_records_in_replay": 0, "active_probe_queue_empty": true, "active_probe_schedule_disabled": true, "historical_probe_provenance_allowed": true, "historical_probe_provenance_present": true, "in_flight_probe_budget": 0.0, "probe_absent_runtime_input": true, "probe_residue_digest_absent": false, "probe_support_not_used_as_evidence": true} |
| `reset_to_initial_no_probe_control_distinguishes_derived_state` | `true` | {"control_interpretation": "I5 already supports initial no-probe replay, but 5-A starts from the probe-present final state and preserves a different derived state signature.", "derived_state_differs_from_initial_no_probe_state": true, "initial_no_probe_candidate_supported": true, "initial_no_probe_state_digest": "ac27c6bfae255bf87440b1329637d79e0b698279cc192e37601725d2b838e868", "post_probe_derived_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "source_i5_output": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe.json"} |
| `post_probe_same_basin_preserved` | `true` | {"active_degree_same": true, "basin_member_count_same": true, "center_basin_id_same": true, "center_node_id_same": true, "topology_signature_same": true} |
| `support_coherence_boundary_flux_gates_preserved` | `true` | {"boundary_integrity_result": "preserved", "coherence_floor_result": "preserved", "flux_or_leakage_result": "preserved", "support_floor_result": "preserved"} |
| `multi_window_replay_passed` | `true` | {"all_replay_modes_passed": true, "artifact_id": "n21_i5a_post_probe_derivation_replay", "artifact_replay": {"artifact_path_exists": true, "source_run_artifact_digest": "d79ea323b3af96918df87b6c53335f0285c176749fc5c6ddd93a442409a7923e", "status": "passed"}, "declared_multi_window_replay_without_active_probe_scaffold": {"active_probe_packet_records_in_replay": 0, "historical_probe_packet_record_count": 1, "status": "passed", "window_count": 3}, "replay_digest": "ed6a607f4fba199dfaee8e0ea223d97a1a0b79a29b8e644ff7d30d5026be2fa4", "snapshot_load_replay": {"loaded_snapshot_geometry_digest": "df2b9c25191a4c61f7a4b045785657ba6bc916eecebc39cfd5d1ccac0c0da04f", "original_geometry_digest": "df2b9c25191a4c61f7a4b045785657ba6bc916eecebc39cfd5d1ccac0c0da04f", "status": "passed"}, "source_final_snapshot_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived_final_snapshot.json", "source_run_artifact_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived_run.json"} |
| `row_controls_passed_without_failed_open` | `true` | [{"actual_result": {"center_coherence_delta": 0.03999999999999915, "packet_count_delta": 1, "pre_probe_state_digest": "aa560ca1ae707821257ce9f3d3388871efabbf6dbb2ccca1a20b8c612094054e", "probe_effect_delta_digest": "8f3ed3b6152d315772fbe0e1dab9c09ccb354cfbd09498ce2c99701d3c77ff3a", "probe_effect_detected": true, "probe_effect_fields": ["center_node_coherence", "source_node_coherence", "packet_records", "local_update_count", "causal_spark_diagnostic_count"], "probe_event_count": 5, "probe_present_final_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "source_coherence_delta": -0.03999999999999915}, "blocked_condition": "probe-present run has no measurable effect", "claim_allowed_when_control_triggers": false, "control_id": "probe_effect_absent_control", "control_status": "passed", "expected_result": "probe changes source-current geometry", "rung_effect": "blocks post-probe-derived variant if triggered"}, {"actual_result": {"post_probe_state_carried_into_probe_absent_run": true, "post_probe_state_derivation_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "post_probe_state_derivation_source": "probe_present_final_snapshot", "probe_absent_initial_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "probe_absent_initial_state_matches_derived_post_probe_state": true, "source_snapshot_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline_final_snapshot.json", "state_derivation_digest": "1440a81727bea11cc9132322360f421184b115273b6c57ce43f05d7937d948ac"}, "blocked_condition": "no-probe replay did not start from post-probe state", "claim_allowed_when_control_triggers": false, "control_id": "post_probe_state_derivation_control", "control_status": "passed", "expected_result": "post-probe replay initial state matches derived checkpoint", "rung_effect": "blocks post-probe-derived variant if triggered"}, {"actual_result": {"active_probe_packet_records_in_replay": 0, "active_probe_queue_empty": true, "active_probe_schedule_disabled": true, "historical_probe_provenance_allowed": true, "historical_probe_provenance_present": true, "in_flight_probe_budget": 0.0, "probe_support_not_used_as_evidence": true}, "blocked_condition": "active probe queue or in-flight budget remains", "claim_allowed_when_control_triggers": false, "control_id": "active_probe_residue_control", "control_status": "passed", "expected_result": "historical provenance allowed, active support absent", "rung_effect": "blocks ND4 and stronger if triggered"}, {"actual_result": {"control_interpretation": "I5 already supports initial no-probe replay, but 5-A starts from the probe-present final state and preserves a different derived state signature.", "derived_state_differs_from_initial_no_probe_state": true, "initial_no_probe_candidate_supported": true, "initial_no_probe_state_digest": "ac27c6bfae255bf87440b1329637d79e0b698279cc192e37601725d2b838e868", "post_probe_derived_state_digest": "5f98c9ebb4110dab0762fd13fc7aacb6d86c449d89179dd6fea4edacbbbf96c9", "source_i5_output": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe.json"}, "blocked_condition": "post-probe replay is not derivation-specific", "claim_allowed_when_control_triggers": false, "control_id": "reset_to_initial_no_probe_control", "control_status": "passed", "expected_result": "derived state differs from initial no-probe state", "rung_effect": "demotes derivation-specific language if triggered"}, {"actual_result": "probe_support_not_used_as_evidence=true", "blocked_condition": "support annotation replaces source-current support", "claim_allowed_when_control_triggers": false, "control_id": "support_annotation_relabel_control", "control_status": "passed", "expected_result": "probe support is not used as evidence", "rung_effect": "blocks ND4 and stronger if triggered"}, {"actual_result": "active_probe_schedule_disabled=true", "blocked_condition": "hidden producer scaffold preserves post-probe state", "claim_allowed_when_control_triggers": false, "control_id": "hidden_producer_support_control", "control_status": "passed", "expected_result": "no new probe schedule or queue work", "rung_effect": "blocks ND4 and stronger if triggered"}, {"actual_result": "probe_present_final_snapshot -> post_probe_derived_initial", "blocked_condition": "derivation trace assembled after outcome inspection", "claim_allowed_when_control_triggers": false, "control_id": "post_hoc_trace_construction_control", "control_status": "passed", "expected_result": "state derivation path recorded from source snapshots", "rung_effect": "blocks ND2 and stronger if triggered"}, {"actual_result": "passed", "blocked_condition": "post-probe no-active-probe replay diverges", "claim_allowed_when_control_triggers": false, "control_id": "multi_window_replay_control", "control_status": "passed", "expected_result": "replay geometry digest matches source run", "rung_effect": "blocks ND3 and stronger if triggered"}] |
| `provisional_nd3_variant_no_final_closeout` | `true` | {"nd_evidence_variant": "post_probe_derived_state", "nd_ladder_rung": "ND3", "nd_ladder_rung_status": "provisional_pending_iteration6_control_matrix"} |
| `unsafe_claim_flags_false` | `true` | {"agency": false, "consciousness": false, "fully_native_integration": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false} |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

5-A is stronger than I5 because the no-probe replay starts from the
probe-present final snapshot rather than from the initial fixture.
The historical probe packet remains as provenance, but active probe
support is disabled: the queue is empty, in-flight budget is zero,
and no active probe packet is replayed. The derived post-probe state
persists across no-probe windows with the same basin signature and
above-floor support/coherence. This supports a provisional
post-probe-derived ND3 candidate only. ND4/ND5 and final
naturalization-depth closeout remain pending I6/I7.
