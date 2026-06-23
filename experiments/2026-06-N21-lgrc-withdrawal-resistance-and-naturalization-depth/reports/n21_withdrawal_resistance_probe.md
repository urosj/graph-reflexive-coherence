# N21 Iteration 4 - Withdrawal Resistance Probe

## Summary

Status: `passed`

Acceptance state: `accepted_provisional_wr4_withdrawal_candidate_pending_i6`

Output digest: `6d80c4dd915c0c5d2b1f67c2af69881d88ab3d632acf828013389f90c53cfb36`

Iteration 4 runs the first source-current withdrawal-resistance
candidate. It weakens a declared LGRC9V3 packetized support surface
and compares baseline vs withdrawn geometry.

## Candidate Row

```text
row_id = n21_i4_row_01_withdrawal_resistance_lgrc9v3_support_weakening
row_decision = supported
wr_ladder_rung = WR4
wr_ladder_rung_status = provisional_pending_iteration6_control_matrix
row_decision_scope = supported_for_replay_backed_WR4_candidate_only; I2-required control-backed WR5/WR6 gates remain deferred to I6
primitive_claim_allowed = true
derived_report_only = false
```

## Source-Current Artifacts

```text
baseline_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/baseline_run.json
withdrawn_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_run.json
event_log_or_trace_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawal_trace.json
snapshot_or_replay_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/snapshot_replay.json
```

## Withdrawal Geometry

```text
baseline_packet_amount = 0.1
withdrawn_packet_amount = 0.07
withdrawal_amount = 0.03
support_retention_ratio = 0.7000000000000001
same_basin_continuation_status = preserved
support_floor_result = preserved
coherence_floor_result = preserved
boundary_integrity_result = preserved
flux_or_leakage_result = preserved
```

## Replay

```text
replay_result_status = passed
all_replay_modes_passed = true
```

## Controls

```text
executed_control_ids = hidden_producer_support_control, proxy_only_success_control, label_only_success_control, post_hoc_trace_construction_control, support_floor_crossing_control, snapshot_replay_control
deferred_controls_to_i6 = semantic_relabel_control, native_support_relabel_control, phase8_relabel_control, withdrawal_schedule_removed_control, hidden_support_margin_control
control_result_statuses = not_run, passed
```

## Boundary

```text
final_withdrawal_resistance_supported = false
iteration6_replay_control_matrix_required = true
agency = false
native_support = false
sentience = false
phase8_implementation = false
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_i1_i2_i3_passed` | `true` | {"i1": "accepted_source_contract_inventory_no_primitive_evidence", "i2": "accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence", "i3": "accepted_active_nulls_fail_closed_no_primitive_evidence"} |
| `candidate_evidence_fields_present` | `true` | {"required_field_count": 33} |
| `artifact_paths_exist_and_hash` | `true` | [{"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/baseline-checkpoint-00000000.json", "sha256": "a21471d4192f9f35f18fd5c4864c008621e51773720f1798de80aee086924ebc"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/baseline-checkpoint-00000001.json", "sha256": "2643ca082621223c038ae6057b53e3bf43d4fe8278fb2089918a8b36d290b41b"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/baseline_events.jsonl", "sha256": "740b53cbbded1ff6960557a2ca1ad79d3e68c694ccdf47d8bb44c8a782e74081"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/baseline_final_snapshot.json", "sha256": "feb529a97ad99af44e7760d3819446041db63f92086deb794f9056cd51241442"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/baseline_initial_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/baseline_run.json", "sha256": "35d96567c8d76da6a3b382125fefb3314b461132458dd409d42165f054fb9854"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/runtime_config.json", "sha256": "7c1045c3424faa29c5950987ec126e2bea00feb14fb4ab21746aba0751f14805"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/snapshot_replay.json", "sha256": "1ebfc7bea0a2b3e9147230459181e8fc2ea5184d8f0511fd811f46b59934d0ab"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawal_trace.json", "sha256": "6702428ec0d042bed580f366511464904000b617522029be65f27c028bb676f3"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn-checkpoint-00000000.json", "sha256": "0eb44dea8a304b1a824f11bef1a5c8c1d4201b8f1ac32e07017d5d3da30459d2"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn-checkpoint-00000001.json", "sha256": "ad4f242ded717532bba4b7e337c0c32870a802bfb936a30c9594b26d0cea8155"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_duplicate_replay-checkpoint-00000000.json", "sha256": "4941b87f575aaa377db188aaa3a01770d8269571014f2d97c85b210c57484d32"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_duplicate_replay-checkpoint-00000001.json", "sha256": "b743d574cd020d2808ae7c0d2c35a36ef1e6431081cd30adcfa982104d33e415"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_duplicate_replay_events.jsonl", "sha256": "9036a6cd1a851171bc1646645eecff85f5e7a9fa4dead900374495455bf0ccf3"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_duplicate_replay_final_snapshot.json", "sha256": "3d24ddca3b50d1b4ea6740d4269a1ede4eb78bd2f66ca56b8d9c41e85a2416cc"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_duplicate_replay_initial_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_duplicate_replay_run.json", "sha256": "46e7987163213839d11df1f798015c262903b69ad3b70a25c2e02b9684d13d58"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_events.jsonl", "sha256": "676ecfad3d7cfc040e6fafc87f76d39bc69714309968d5c1bc24ef114ba4044e"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_final_snapshot.json", "sha256": "3d24ddca3b50d1b4ea6740d4269a1ede4eb78bd2f66ca56b8d9c41e85a2416cc"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_initial_snapshot.json", "sha256": "9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4"}, {"path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_run.json", "sha256": "2c8d218462956db9c675e57735a491030a5bac2284b8c501874a7b329a9c6133"}] |
| `derived_report_only_false` | `true` | false |
| `withdrawal_schedule_declared_and_weakened` | `true` | {"baseline_packet_amount": 0.1, "edge_id": 0, "floor_crossing_policy": "crossing_blocks_WR3_and_stronger", "kind": "packetized_causal_flux_support_surface", "recovery_window": [1.0, 2.0], "source_node_id": 1, "target_node_id": 0, "withdrawal_amount": 0.03, "withdrawal_end": 2.0, "withdrawal_mode": "weaken", "withdrawal_start": 1.0, "withdrawal_target": "support", "withdrawn_packet_amount": 0.07} |
| `source_current_same_basin_preserved` | `true` | {"active_degree_same": true, "basin_member_count_same": true, "center_basin_id_same": true, "center_node_id_same": true, "topology_signature_same": true} |
| `support_coherence_boundary_flux_gates_preserved` | `true` | {"boundary_integrity_result": "preserved", "coherence_floor_result": "preserved", "flux_or_leakage_result": "preserved", "support_floor_result": "preserved"} |
| `replay_modes_passed` | `true` | {"all_replay_modes_passed": true, "artifact_id": "n21_i4_withdrawal_resistance_snapshot_replay", "artifact_replay": {"artifact_path_exists": true, "source_run_artifact_digest": "2c8d218462956db9c675e57735a491030a5bac2284b8c501874a7b329a9c6133", "status": "passed"}, "duplicate_replay": {"duplicate_geometry_digest": "c0f61e7929d4a4491f4dbc74fa79633b4687bc610e3aa96ea19c6981cebd7633", "original_geometry_digest": "c0f61e7929d4a4491f4dbc74fa79633b4687bc610e3aa96ea19c6981cebd7633", "status": "passed"}, "duplicate_run_artifact_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_duplicate_replay_run.json", "replay_digest": "f59376df335ce1d9e2fd1e81fa38a5bb13f08dcd3c368fee08ef22116cb006f9", "snapshot_load_replay": {"loaded_snapshot_geometry_digest": "c0f61e7929d4a4491f4dbc74fa79633b4687bc610e3aa96ea19c6981cebd7633", "original_geometry_digest": "c0f61e7929d4a4491f4dbc74fa79633b4687bc610e3aa96ea19c6981cebd7633", "status": "passed"}, "source_final_snapshot_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_final_snapshot.json", "source_run_artifact_path": "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_run.json"} |
| `required_controls_recorded_with_i6_deferrals` | `true` | {"control_result_statuses": ["not_run", "passed"], "deferred_controls_to_i6": ["semantic_relabel_control", "native_support_relabel_control", "phase8_relabel_control", "withdrawal_schedule_removed_control", "hidden_support_margin_control"], "recorded_control_ids": ["hidden_producer_support_control", "hidden_support_margin_control", "label_only_success_control", "native_support_relabel_control", "phase8_relabel_control", "post_hoc_trace_construction_control", "proxy_only_success_control", "semantic_relabel_control", "snapshot_replay_control", "support_floor_crossing_control", "withdrawal_schedule_removed_control"], "required_control_ids": ["hidden_producer_support_control", "hidden_support_margin_control", "label_only_success_control", "native_support_relabel_control", "phase8_relabel_control", "post_hoc_trace_construction_control", "proxy_only_success_control", "semantic_relabel_control", "support_floor_crossing_control", "withdrawal_schedule_removed_control"]} |
| `provisional_wr4_no_final_closeout` | `true` | {"wr_ladder_rung": "WR4", "wr_ladder_rung_status": "provisional_pending_iteration6_control_matrix"} |
| `unsafe_claim_flags_false` | `true` | {"agency": false, "consciousness": false, "fully_native_integration": false, "identity_acceptance": false, "native_ant_agency": false, "native_colony_agency": false, "native_support": false, "organism_life": false, "phase8_implementation": false, "selfhood": false, "semantic_action": false, "semantic_choice": false, "semantic_goal_ownership": false, "semantic_intention": false, "semantic_perception": false, "sentience": false, "unrestricted_autonomy": false} |
| `no_local_absolute_paths` | `true` | payload uses repository-relative paths and source IDs only |

## Interpretation

Geometrically, I4 weakens a packetized support surface feeding the
center basin node. The withdrawn run still preserves the center basin
identity, fixed topology signature, active boundary degree, support
floor, coherence floor, and packet budget. This supports a
provisional WR4 withdrawal-resistance candidate because replay
passes, but final WR support remains pending the I6 replay/control
matrix and N21 closeout. I2-required control IDs that are not part
of the I4 replay-backed WR4 gate are recorded as `not_run` and
explicitly deferred to I6; they are not treated as passed in I4.
