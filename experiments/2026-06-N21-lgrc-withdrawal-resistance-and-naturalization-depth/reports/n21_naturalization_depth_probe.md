# N21 Iteration 5 - Naturalization Depth Probe

## Summary

Status: `passed`

Acceptance state: `accepted_provisional_nd3_naturalization_candidate_pending_i6`

Output digest: `076461e9779b024e0633810be35e78359b8e36cd88bbb9ea655aa8b5c9bf7df2`

Iteration 5 runs the first source-current naturalization-depth
candidate. It contrasts a probe-present LGRC9V3 baseline with a
probe-absent multi-window replay of the same substrate geometry.

## Candidate Row

```text
row_id = n21_i5_row_01_naturalization_depth_lgrc9v3_probe_absence
row_decision = supported
nd_ladder_rung = ND3
nd_ladder_rung_status = provisional_pending_iteration6_control_matrix
primitive_claim_allowed = true
derived_report_only = false
```

## Source-Current Artifacts

```text
probe_present_baseline_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_present_baseline_run.json
probe_absent_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_run.json
event_log_or_trace_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/naturalization_trace.json
snapshot_or_replay_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/multi_window_replay.json
```

## Probe Absence

```text
probe_absent_runtime_input = true
probe_residue_digest_absent = true
support_annotation_not_used_as_evidence = true
producer_probe_schedule_disabled = true
```

## Post-Probe Geometry

```text
baseline_original_probe_packet_amount = 0.04
post_probe_replay_windows = 3
post_probe_same_basin_continuation_status = preserved
post_probe_support_score = 10.0
post_probe_support_floor = 9.95
post_probe_support_margin = 0.05000000000000071
post_probe_center_coherence = 10.0
post_probe_coherence_floor = 9.95
post_probe_coherence_margin = 0.05000000000000071
post_probe_active_degree = 9
post_probe_budget_error = 0.0
original_probe_packet_record_count = 0
```

## State Derivation

```text
probe_absent_initial_state_source = initial_fixture_state
probe_removed_from_existing_state = false
post_probe_state_carried_into_probe_absent_run = false
baseline_probe_effect_observed = true
center_coherence_delta = 0.03999999999999915
source_coherence_delta = -0.03999999999999915
packet_count_delta = 1
replay_kind = static_snapshot_replay
eventful_post_probe_continuation = false
```

## Replay

```text
replay_result_status = passed
all_replay_modes_passed = true
declared_multi_window_replay_without_original_probe_scaffold = passed
```

## Boundary

```text
final_naturalization_depth_supported = false
post_probe_aftereffect_evidence_supported = false
iteration6_replay_control_matrix_required = true
agency = false
native_support = false
sentience = false
phase8_implementation = false
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_i1_i2_i3_i4_passed` | `true` | {"i1": "accepted_source_contract_inventory_no_primitive_evidence", "i2": "accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence", "i3": "accepted_active_nulls_fail_closed_no_primitive_evidence", "i4": "accepted_provisional_wr4_withdrawal_candidate_pending_i6"} |
| `candidate_evidence_fields_present` | `true` | {"required_field_count": 33} |
| `artifact_paths_exist_and_hash` | `true` | [{"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/multi_window_replay.json", "sha256": "d0d270ee1f372f4e4de0cbbacd013e30f30bd1fa021eee81ab5ac93b201605a7"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/naturalization_trace.json", "sha256": "eb34259c4411cf248dfee6996dc52f5f5bcbdc4a0224d958c3560cd36ac6c9eb"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent-checkpoint-00000000.json", "sha256": "ce8d8b1fc6ea6727d29681ddf5b779b83e2ba6bcc12e26fd6a91d4c272591c60"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent-checkpoint-00000001.json", "sha256": "cd6b42454a79d12b1c86369b0b901b3870d4cce7b19c7ef11901bb421243d0e4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_duplicate_replay-checkpoint-00000000.json", "sha256": "720a7b2f1866a68c30cf1b14689e1294d8e00ae9e98f7337c895dc1d4cf8d862"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_duplicate_replay-checkpoint-00000001.json", "sha256": "30d73c9f1535f8658f9872d1b2f0f18ec5382c30cd6b31836568a707c4ec4b2d"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_duplicate_replay_events.jsonl", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_duplicate_replay_final_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_duplicate_replay_initial_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_duplicate_replay_run.json", "sha256": "dcc5bbe195a0cbc953c6a650e0054e133d2acf506cce9d08df9fda5e949fb356"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_events.jsonl", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_final_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_initial_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_multi_window_replay-checkpoint-00000000.json", "sha256": "9237ea046bde157a976bef2f41d3b7fe0355100b81bc7468700f5d9580bf9cef"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_multi_window_replay-checkpoint-00000001.json", "sha256": "ab75b0a038d323d16e629dbae9b4de45ffe6cb4abfd1db07d5af2fb64ab43fb3"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_multi_window_replay_events.jsonl", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_multi_window_replay_final_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_multi_window_replay_initial_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_multi_window_replay_run.json", "sha256": "ee9279ed88c350b53f0022786a8f36f0e690f20ea14f37522300e5da59a26d0c"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_run.json", "sha256": "c8125e094c3a009717eeb63191e2f2a10aaa371b5869f67f60658f68111e024d"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_present_baseline-checkpoint-00000000.json", "sha256": "ff772e084ad4e4ba6edce7332b5e1725b86aa0412e271dbe58ce9a6215368c13"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_present_baseline-checkpoint-00000001.json", "sha256": "350ec038e1ac56c62deaad5eb20e705d0c7b5a5e5ae8432e3e29984d16b32ca6"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_present_baseline_events.jsonl", "sha256": "122c24887a5ab926cdd7df9e3123b6f0e4f4953e36d6f37ddbaf81a9d7e1cdd1"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_present_baseline_final_snapshot.json", "sha256": "9322b86dae10942ea2dea0b372993f9b75009db60a33144abd1bdec7a25f9d2a"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_present_baseline_initial_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_present_baseline_run.json", "sha256": "ef099ed7aebde0353187c66495f2856d3dc618bf268966cd25c64ccf3651d641"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/runtime_config.json", "sha256": "080bcf04d23ddbef7a2f8cb2234aa69efd7e76fa9debfcbf178cb590dc40ce09"}] |
| `derived_report_only_false` | `true` | false |
| `probe_absence_schema_values_present` | `true` | {"probe_absent_runtime_input": true, "probe_residue_digest_absent": true, "producer_probe_schedule_disabled": true, "support_annotation_not_used_as_evidence": true} |
| `probe_present_vs_probe_absent_declared` | `true` | {"active_degree_same": true, "baseline_original_probe_packet_record_count": 1, "center_basin_id_same": true, "center_node_id_same": true, "probe_absent_event_count": 0, "probe_absent_original_probe_packet_record_count": 0, "topology_signature_same": true} |
| `probe_state_derivation_clarified` | `true` | {"post_probe_state_carried_into_probe_absent_run": false, "probe_absent_initial_state_digest": "ac27c6bfae255bf87440b1329637d79e0b698279cc192e37601725d2b838e868", "probe_absent_initial_state_source": "initial_fixture_state", "probe_present_final_state_digest": "35fa77d993587cd6ab957d6cabe3bf89d436acfa98b55e605ef3860c1c6e6495", "probe_present_initial_state_digest": "c9693a253471f19ca8ed47cc80f6a210c29013eb6157ad3bdb2318416802851b", "probe_removed_from_existing_state": false, "state_derivation_digest": "3c20abdbb2725d04edee33b80de74c4652262025e211286b0685cf16019e2423", "state_derivation_interpretation": "I5 tests probe-omitted source-current persistence from the declared initial fixture, not a carried post-probe aftereffect state."} |
| `baseline_probe_effect_observed` | `true` | {"baseline_event_count": 5, "baseline_original_probe_packet_record_count": 1, "baseline_probe_effect_observed": true, "center_coherence_delta": 0.03999999999999915, "packet_count_delta": 1, "probe_effect_digest": "6de5940b36f4f2a7073e8200b3fa5e94c2ebb6bcb25162160484a2e51f01b71f", "source_coherence_delta": -0.03999999999999915} |
| `static_replay_classified` | `true` | {"eventful_post_probe_continuation": false, "replay_kind": "static_snapshot_replay"} |
| `post_probe_same_basin_preserved` | `true` | {"active_degree_same": true, "basin_member_count_same": true, "center_basin_id_same": true, "center_node_id_same": true, "topology_signature_same": true} |
| `support_coherence_boundary_flux_gates_preserved` | `true` | {"boundary_integrity_result": "preserved", "coherence_floor_result": "preserved", "flux_or_leakage_result": "preserved", "support_floor_result": "preserved"} |
| `multi_window_replay_passed` | `true` | {"all_replay_modes_passed": true, "artifact_id": "n21_i5_naturalization_depth_multi_window_replay", "artifact_replay": {"artifact_path_exists": true, "source_run_artifact_digest": "c8125e094c3a009717eeb63191e2f2a10aaa371b5869f67f60658f68111e024d", "status": "passed"}, "declared_multi_window_replay_without_original_probe_scaffold": {"original_probe_packet_record_count": 0, "status": "passed", "window_count": 3}, "duplicate_replay": {"duplicate_geometry_digest": "ac27c6bfae255bf87440b1329637d79e0b698279cc192e37601725d2b838e868", "original_geometry_digest": "ac27c6bfae255bf87440b1329637d79e0b698279cc192e37601725d2b838e868", "status": "passed"}, "duplicate_run_artifact_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_duplicate_replay_run.json", "replay_digest": "90d2109e4d6f9287f00f4589925a4c2491eb990b37b107bd9e914b383a649794", "snapshot_load_replay": {"loaded_snapshot_geometry_digest": "ac27c6bfae255bf87440b1329637d79e0b698279cc192e37601725d2b838e868", "original_geometry_digest": "ac27c6bfae255bf87440b1329637d79e0b698279cc192e37601725d2b838e868", "status": "passed"}, "source_final_snapshot_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_final_snapshot.json", "source_run_artifact_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_run.json"} |
| `row_controls_passed_without_failed_open` | `true` | [{"actual_result": "probe_absent_runtime_input=true", "blocked_condition": "row only shows probe-present baseline", "claim_allowed_when_control_triggers": false, "control_id": "probe_present_only_control", "control_status": "passed", "expected_result": "evaluated run disables original probe schedule", "rung_effect": "blocks ND1 and stronger if triggered"}, {"actual_result": 0, "blocked_condition": "original probe packet residue remains in evaluated run", "claim_allowed_when_control_triggers": false, "control_id": "probe_residue_control", "control_status": "passed", "expected_result": "original probe packet record count is zero", "rung_effect": "blocks ND4 and stronger if triggered"}, {"actual_result": "support_annotation_not_used_as_evidence=true", "blocked_condition": "support annotation is used as source-current support", "claim_allowed_when_control_triggers": false, "control_id": "support_source_annotation_relabel_control", "control_status": "passed", "expected_result": "support annotation not used as evidence", "rung_effect": "blocks ND4 and stronger if triggered"}, {"actual_result": "producer_probe_schedule_disabled=true and no packet residue", "blocked_condition": "undeclared producer support preserves post-probe basin", "claim_allowed_when_control_triggers": false, "control_id": "hidden_producer_support_control", "control_status": "passed", "expected_result": "no queued extra support in evaluated run", "rung_effect": "blocks ND4 and stronger if triggered"}, {"actual_result": "preserved", "blocked_condition": "depth proxy improves while same-basin gates fail", "claim_allowed_when_control_triggers": false, "control_id": "proxy_only_success_control", "control_status": "passed", "expected_result": "post-probe support/coherence/boundary/flux gates preserved", "rung_effect": "blocks ND2 and stronger if triggered"}, {"actual_result": "post-probe basin signature and topology traces present", "blocked_condition": "post-probe continuation is label-only", "claim_allowed_when_control_triggers": false, "control_id": "label_only_success_control", "control_status": "passed", "expected_result": "source-current basin signature fields present", "rung_effect": "blocks ND2 and stronger if triggered"}, {"actual_result": "LGRC9V3 snapshots and multi-window replay generated", "blocked_condition": "post-probe trace assembled without runtime artifacts", "claim_allowed_when_control_triggers": false, "control_id": "post_hoc_trace_construction_control", "control_status": "passed", "expected_result": "event logs, snapshots, and replay artifacts exist", "rung_effect": "blocks ND2 and stronger if triggered"}, {"actual_result": "passed", "blocked_condition": "multi-window no-probe replay diverges", "claim_allowed_when_control_triggers": false, "control_id": "multi_window_replay_control", "control_status": "passed", "expected_result": "replay geometry digest matches probe-absent run", "rung_effect": "blocks ND3 and stronger if triggered"}] |
| `provisional_nd3_no_final_closeout` | `true` | {"nd_ladder_rung": "ND3", "nd_ladder_rung_status": "provisional_pending_iteration6_control_matrix"} |
| `unsafe_claim_flags_false` | `true` | {"agency": false, "consciousness": false, "fully_native_integration": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false} |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

Geometrically, I5 removes the original packetized probe scaffold
from the evaluated run by omitting the probe from the initial
fixture. It asks whether the center basin remains the same basin
across source-current no-probe replay windows. The no-probe run
preserves basin identity, topology signature, active
boundary degree, residual support floor, coherence floor, and packet
budget while recording zero original-probe packet residue. This
supports only a provisional local ND3 probe-absent same-basin
replay candidate because the declared no-probe multi-window replay
passes. It does not show carried post-probe aftereffect persistence:
the probe-absent run starts from the initial fixture state, not from
the probe-present final snapshot. Final ND support remains pending
the I6 replay/control matrix and N21 closeout.
