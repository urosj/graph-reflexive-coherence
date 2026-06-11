# N07 Iteration 7: ID5 Reflexive Closure And Persistence

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_7_id5_reflexive_closure_persistence.py
```

Iteration 7 consumes the Iteration 6-B ID4 topology stress candidate and adds
the reflexive closure gate: re-entry into the lineage-current support basin,
strengthened artifact-visible experiment-local basin evidence after re-entry,
and later-cycle consumption of the updated basin evidence digest.

This may support an ID5 reflexively self-maintaining identity candidate. It
does not emit identity acceptance, RC identity collapse, agency, semantic
choice, or native LGRC identity support. Native reflexive-closure policy
remains unavailable. The re-entry node lineage is sourced from the Iteration
6-B birth topology event; the reflexive-closure measurements themselves remain
experiment-local probe evidence, not native runtime observations.

## Reflexive Reentry Event

```json
{
  "artifact_visible": true,
  "authored_measurement_values_present": true,
  "basin_evidence_after_reentry": {
    "artifact_visible": true,
    "authored_measurement_value": true,
    "basin_attribute_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
    "budget_after": 6.0,
    "budget_before": 6.0,
    "budget_error": 0.0,
    "budget_surface": "node_plus_packet",
    "consumed_basin_evidence_digest": "6ff242751a0a21825ed4b34ac1220edc1315e0b4f235f85efba529f5bf0795ed",
    "derived_from_source_artifact_digest": "b25b802b55217bb687defbe3add64a5f24133005ed0aff0e1969e0876369831d",
    "evidence_id": "n07_i7_basin_evidence_after_reentry_v1",
    "measurement_origin": "experiment_local_declared_reentry_probe",
    "native_runtime_observed": false,
    "nonnegative_state_passed": true,
    "proper_time_index": 8,
    "proper_time_persistence_score": 0.965,
    "report_side_only": false,
    "retention_score": 0.962,
    "runtime_visible": false,
    "scheduler_event_index": 22,
    "source_backed": true,
    "source_backing_kind": "iteration_7_artifact_generated_probe_record",
    "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "support_area_mass": 1.456
  },
  "basin_evidence_after_reentry_strengthened": true,
  "basin_evidence_before_reentry": {
    "artifact_visible": true,
    "authored_measurement_value": false,
    "basin_attribute_digest": "6ff242751a0a21825ed4b34ac1220edc1315e0b4f235f85efba529f5bf0795ed",
    "budget_after": 6.0,
    "budget_before": 6.0,
    "budget_error": 0.0,
    "budget_surface": "node_plus_packet",
    "consumed_basin_evidence_digest": null,
    "derived_from_source_artifact_digest": "cbfa440ba79687d2afa7649d538ceddc1152f273d5f2bd432e31fa9f35743574",
    "evidence_id": "n07_i7_basin_evidence_before_reentry_v1",
    "measurement_origin": "source_iteration_6b_lineage_current_cycle",
    "native_runtime_observed": false,
    "nonnegative_state_passed": true,
    "proper_time_index": 7,
    "proper_time_persistence_score": 0.96,
    "report_side_only": false,
    "retention_score": 0.955,
    "runtime_visible": false,
    "scheduler_event_index": 19,
    "source_backed": true,
    "source_backing_kind": "source_iteration_6b_artifact",
    "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "support_area_mass": 1.448
  },
  "basin_evidence_bundle": [
    "support_area_mass",
    "retention_score",
    "proper_time_persistence_score",
    "basin_evidence_digest"
  ],
  "basin_evidence_chain": [
    {
      "artifact_visible": true,
      "authored_measurement_value": false,
      "basin_attribute_digest": "6ff242751a0a21825ed4b34ac1220edc1315e0b4f235f85efba529f5bf0795ed",
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "consumed_basin_evidence_digest": null,
      "derived_from_source_artifact_digest": "cbfa440ba79687d2afa7649d538ceddc1152f273d5f2bd432e31fa9f35743574",
      "evidence_id": "n07_i7_basin_evidence_before_reentry_v1",
      "measurement_origin": "source_iteration_6b_lineage_current_cycle",
      "native_runtime_observed": false,
      "nonnegative_state_passed": true,
      "proper_time_index": 7,
      "proper_time_persistence_score": 0.96,
      "report_side_only": false,
      "retention_score": 0.955,
      "runtime_visible": false,
      "scheduler_event_index": 19,
      "source_backed": true,
      "source_backing_kind": "source_iteration_6b_artifact",
      "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
      "support_area_mass": 1.448
    },
    {
      "artifact_visible": true,
      "authored_measurement_value": true,
      "basin_attribute_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "consumed_basin_evidence_digest": "6ff242751a0a21825ed4b34ac1220edc1315e0b4f235f85efba529f5bf0795ed",
      "derived_from_source_artifact_digest": "b25b802b55217bb687defbe3add64a5f24133005ed0aff0e1969e0876369831d",
      "evidence_id": "n07_i7_basin_evidence_after_reentry_v1",
      "measurement_origin": "experiment_local_declared_reentry_probe",
      "native_runtime_observed": false,
      "nonnegative_state_passed": true,
      "proper_time_index": 8,
      "proper_time_persistence_score": 0.965,
      "report_side_only": false,
      "retention_score": 0.962,
      "runtime_visible": false,
      "scheduler_event_index": 22,
      "source_backed": true,
      "source_backing_kind": "iteration_7_artifact_generated_probe_record",
      "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
      "support_area_mass": 1.456
    },
    {
      "artifact_visible": true,
      "authored_measurement_value": true,
      "basin_attribute_digest": "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "consumed_basin_evidence_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
      "derived_from_source_artifact_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
      "evidence_id": "n07_i7_later_cycle_consumed_reentry_evidence_v1",
      "measurement_origin": "experiment_local_declared_later_cycle_probe",
      "native_runtime_observed": false,
      "nonnegative_state_passed": true,
      "proper_time_index": 9,
      "proper_time_persistence_score": 0.969,
      "report_side_only": false,
      "retention_score": 0.966,
      "runtime_visible": false,
      "scheduler_event_index": 23,
      "source_backed": true,
      "source_backing_kind": "iteration_7_artifact_generated_probe_record",
      "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
      "support_area_mass": 1.4609999999999999
    },
    {
      "artifact_visible": true,
      "authored_measurement_value": true,
      "basin_attribute_digest": "635560ceabc27cc6da817843ba51c4dbbac366a4320460bf3f149ee2ba6e92d7",
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "consumed_basin_evidence_digest": "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
      "derived_from_source_artifact_digest": "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
      "evidence_id": "n07_i7_final_persistence_cycle_evidence_v1",
      "measurement_origin": "experiment_local_declared_final_persistence_probe",
      "native_runtime_observed": false,
      "nonnegative_state_passed": true,
      "proper_time_index": 10,
      "proper_time_persistence_score": 0.971,
      "report_side_only": false,
      "retention_score": 0.967,
      "runtime_visible": false,
      "scheduler_event_index": 24,
      "source_backed": true,
      "source_backing_kind": "iteration_7_artifact_generated_probe_record",
      "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
      "support_area_mass": 1.4629999999999999
    }
  ],
  "basin_evidence_chain_digest": "12520b48b2d9e62376ff55546ec853f5bd1dd2d866aff3ef93b306f9ccec1724",
  "budget_error_max": 0.0,
  "budget_surface": "node_plus_packet",
  "candidate_identity_carrier_type": "coherence_basin",
  "event_id": "n07_i7_reflexive_reentry_event_0001",
  "event_kind": "experiment_local_reflexive_reentry_and_later_consumption",
  "event_time_key": "n07_i7_t6_reflexive_reentry_event",
  "evidence_generation_mode": "experiment_local_declared_probe",
  "final_persistence_basin_evidence": {
    "artifact_visible": true,
    "authored_measurement_value": true,
    "basin_attribute_digest": "635560ceabc27cc6da817843ba51c4dbbac366a4320460bf3f149ee2ba6e92d7",
    "budget_after": 6.0,
    "budget_before": 6.0,
    "budget_error": 0.0,
    "budget_surface": "node_plus_packet",
    "consumed_basin_evidence_digest": "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
    "derived_from_source_artifact_digest": "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
    "evidence_id": "n07_i7_final_persistence_cycle_evidence_v1",
    "measurement_origin": "experiment_local_declared_final_persistence_probe",
    "native_runtime_observed": false,
    "nonnegative_state_passed": true,
    "proper_time_index": 10,
    "proper_time_persistence_score": 0.971,
    "report_side_only": false,
    "retention_score": 0.967,
    "runtime_visible": false,
    "scheduler_event_index": 24,
    "source_backed": true,
    "source_backing_kind": "iteration_7_artifact_generated_probe_record",
    "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "support_area_mass": 1.4629999999999999
  },
  "later_cycle_basin_evidence": {
    "artifact_visible": true,
    "authored_measurement_value": true,
    "basin_attribute_digest": "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
    "budget_after": 6.0,
    "budget_before": 6.0,
    "budget_error": 0.0,
    "budget_surface": "node_plus_packet",
    "consumed_basin_evidence_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
    "derived_from_source_artifact_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
    "evidence_id": "n07_i7_later_cycle_consumed_reentry_evidence_v1",
    "measurement_origin": "experiment_local_declared_later_cycle_probe",
    "native_runtime_observed": false,
    "nonnegative_state_passed": true,
    "proper_time_index": 9,
    "proper_time_persistence_score": 0.969,
    "report_side_only": false,
    "retention_score": 0.966,
    "runtime_visible": false,
    "scheduler_event_index": 23,
    "source_backed": true,
    "source_backing_kind": "iteration_7_artifact_generated_probe_record",
    "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "support_area_mass": 1.4609999999999999
  },
  "later_cycle_consumed_updated_basin_evidence": true,
  "later_cycle_consumption_record": {
    "artifact_visible": true,
    "consumed_basin_evidence_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
    "consumed_updated_digest": true,
    "consuming_cycle_id": "n07_i7_later_cycle_consumed_reentry_evidence_v1",
    "expected_updated_basin_evidence_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
    "native_runtime_observed": false,
    "pre_reentry_basin_evidence_digest": "6ff242751a0a21825ed4b34ac1220edc1315e0b4f235f85efba529f5bf0795ed",
    "record_id": "n07_i7_later_cycle_consumption_record_v1",
    "record_kind": "experiment_local_digest_consumption_record",
    "source_backing_kind": "iteration_7_artifact_generated_probe_record",
    "stale_pre_reentry_digest_used": false
  },
  "later_cycle_consumption_record_digest": "f2bb4aa163771ce41bf5ebf99b003337720be031df6a830a4e5d10ba2c9ed632",
  "metric_id": "n07_reflexive_closure_reentry_v1",
  "native_runtime_observed": false,
  "nonnegative_state_passed": true,
  "processed_packet_event": {
    "artifact_visible": true,
    "budget_after": 6.0,
    "budget_before": 6.0,
    "budget_error": 0.0,
    "native_runtime_observed": false,
    "processed_packet_id": "n07_i7_processed_reentry_packet_0001",
    "producer_mutated_state": false,
    "scheduled_packet_id": "n07_i7_scheduled_reentry_packet_0001",
    "scheduler_event_index": 21,
    "step_mutated_state": true,
    "step_processed": true
  },
  "processed_packet_event_digest": "ce104d660d36eaf29066b97875f8c587787bcbff701fcb610ef72cbd4256f459",
  "producer_record": {
    "artifact_visible": true,
    "causal_surface_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "native_runtime_observed": false,
    "producer_changed_topology": false,
    "producer_emitted_claim_label": false,
    "producer_mutated_coherence": false,
    "producer_record_id": "n07_i7_reentry_producer_record_0001",
    "producer_wrote_centroid": false,
    "producer_wrote_support_mask": false,
    "reason_code": "n07_reflexive_reentry_packet_scheduled",
    "record_kind": "experiment_local_reentry_scheduling_record",
    "scheduled_packet_id": "n07_i7_scheduled_reentry_packet_0001",
    "scheduler_event_index": 20
  },
  "producer_record_digest": "d6a2d186ecb99f9c44372d16ca09cd44565b68cd4e10a2e03208ac66210313af",
  "reentry_coherence_into_support": 0.08,
  "reentry_node_lineage": {
    "birth_is_identity_acceptance": false,
    "born_node_id": 32,
    "lineage_action": "birth",
    "lineage_map": {
      "action": "birth",
      "born_node_ids": [
        32
      ],
      "born_node_parent_map": {
        "32": 30
      },
      "complete": true,
      "node_map": {
        "30": [
          30,
          32
        ],
        "31": [
          31
        ]
      },
      "retired_node_ids": [],
      "scrambled": false,
      "source_support_nodes": [
        30,
        31
      ],
      "target_support_nodes": [
        30,
        31,
        32
      ]
    },
    "lineage_transfer_map_digest": "70037da10c07fc329def298c94aaf75f5d48e6071d69cd85fc9f938fef5a84a1",
    "node_lineage_source_backed": true,
    "parent_node_id": 30,
    "source_iteration": "6B",
    "source_support_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
    "surface_lineage_record_digest": "9ca3eabfdaa9611fc127fe602c260cb576730ed0a84fbef3d8a2cffa53f446b9",
    "topology_event_digest": "d0b636dfa696a17d75740803074dd2c11b46dcf585450f11ac1de66c0b5888ca",
    "topology_event_id": "n07_i6b_topology_birth_support_A_0002",
    "topology_state_reabsorption_record_digest": "e5bc4a6f79e5a33ef9c4710c4863dee20ee00574c8f3f88a91e9d326d77e759d",
    "transported_support_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075"
  },
  "reentry_packet_event": {
    "amount": 0.08,
    "artifact_visible": true,
    "causal_surface_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "event_generation_mode": "experiment_local_declared_probe",
    "native_runtime_observed": false,
    "node_lineage_context": {
      "birth_is_identity_acceptance": false,
      "born_node_id": 32,
      "lineage_action": "birth",
      "lineage_map": {
        "action": "birth",
        "born_node_ids": [
          32
        ],
        "born_node_parent_map": {
          "32": 30
        },
        "complete": true,
        "node_map": {
          "30": [
            30,
            32
          ],
          "31": [
            31
          ]
        },
        "retired_node_ids": [],
        "scrambled": false,
        "source_support_nodes": [
          30,
          31
        ],
        "target_support_nodes": [
          30,
          31,
          32
        ]
      },
      "lineage_transfer_map_digest": "70037da10c07fc329def298c94aaf75f5d48e6071d69cd85fc9f938fef5a84a1",
      "node_lineage_source_backed": true,
      "parent_node_id": 30,
      "source_iteration": "6B",
      "source_support_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
      "surface_lineage_record_digest": "9ca3eabfdaa9611fc127fe602c260cb576730ed0a84fbef3d8a2cffa53f446b9",
      "topology_event_digest": "d0b636dfa696a17d75740803074dd2c11b46dcf585450f11ac1de66c0b5888ca",
      "topology_event_id": "n07_i6b_topology_birth_support_A_0002",
      "topology_state_reabsorption_record_digest": "e5bc4a6f79e5a33ef9c4710c4863dee20ee00574c8f3f88a91e9d326d77e759d",
      "transported_support_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075"
    },
    "packet_event_id": "n07_i7_reentry_packet_0001",
    "polarity": "reentry_into_support",
    "producer_record_id": "n07_i7_reentry_producer_record_0001",
    "route_node_ids": [
      32,
      30
    ],
    "runtime_visible": false,
    "scheduled_packet_id": "n07_i7_scheduled_reentry_packet_0001",
    "source_node_id": 32,
    "target_node_id": 30
  },
  "reentry_packet_event_digest": "b25b802b55217bb687defbe3add64a5f24133005ed0aff0e1969e0876369831d",
  "report_side_only": false,
  "runtime_visible": false,
  "scheduler_event_index": 19,
  "source_backed": true,
  "source_backing_kind": "source_iteration_6b_plus_iteration_7_probe_artifact",
  "source_id4_stress_candidate_row_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
  "source_iteration_6b_output_path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json",
  "source_iteration_6b_output_sha256": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
  "source_topology_stress_record_digest": "9c4ed80df8f1c0eadac9a5ab0f2034f2d792785213d21be29aa98fcc06b4b70c",
  "stale_digest_consumed": false,
  "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075"
}
```

## Proper-Time Persistence Evaluation

```json
{
  "artifact_visible": true,
  "basin_evidence_digests": [
    "6ff242751a0a21825ed4b34ac1220edc1315e0b4f235f85efba529f5bf0795ed",
    "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
    "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
    "635560ceabc27cc6da817843ba51c4dbbac366a4320460bf3f149ee2ba6e92d7"
  ],
  "evaluator_digest": "348d3dd07b04d08dcbaaa50975225367bb75b6ee32a39a53e584989e7a859016",
  "evaluator_digest_input": {
    "evaluator_id": "n07_i7_proper_time_identity_persistence_evaluator_v1",
    "evidence_digests": [
      "6ff242751a0a21825ed4b34ac1220edc1315e0b4f235f85efba529f5bf0795ed",
      "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
      "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
      "635560ceabc27cc6da817843ba51c4dbbac366a4320460bf3f149ee2ba6e92d7"
    ],
    "metric_id": "n07_reflexive_closure_reentry_v1",
    "proper_time_indices": [
      7,
      8,
      9,
      10
    ],
    "threshold": 3
  },
  "evaluator_id": "n07_i7_proper_time_identity_persistence_evaluator_v1",
  "evidence_generation_mode": "experiment_local_proper_time_probe",
  "metric_id": "n07_reflexive_closure_reentry_v1",
  "native_runtime_observed": false,
  "native_support_status": "experiment_local",
  "persistence_passed": true,
  "persistence_score_min": 0.96,
  "proper_time_indices": [
    7,
    8,
    9,
    10
  ],
  "proper_time_only": true,
  "proper_time_persistence_threshold": 3,
  "proper_time_window_count": 4,
  "raw_scheduler_window_used": false,
  "record_kind": "experiment_local_proper_time_identity_persistence_evaluation",
  "report_side_only": false,
  "runtime_visible": false,
  "source_backed": true,
  "source_backing_kind": "iteration_7_artifact_generated_probe_record",
  "source_event_digest": "7014cc83a38bfb897de72455316e5598a59a5df9102322a0e32563ecb826329d",
  "source_event_id": "n07_i7_reflexive_reentry_event_0001",
  "updated_evidence_consumed_by_later_cycle": true
}
```

## Reflexive Closure Record

```json
{
  "artifact_visible": true,
  "authored_measurement_values_present": true,
  "basin_evidence_after_reentry": 1.456,
  "basin_evidence_after_reentry_digest": "0cc6feb690fcbd46a5facfc38ede8579dea22e173d5b31b8debfd62a2404eca9",
  "basin_evidence_after_reentry_strengthened": true,
  "basin_evidence_before_reentry": 1.448,
  "basin_evidence_before_reentry_digest": "6ff242751a0a21825ed4b34ac1220edc1315e0b4f235f85efba529f5bf0795ed",
  "budget_error_max": 0.0,
  "budget_surface": "node_plus_packet",
  "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
  "conditions": [
    "reentry_coherence_into_support > 0",
    "basin_evidence_after_reentry >= basin_evidence_before_reentry",
    "later_cycle_consumed_updated_basin_evidence = true",
    "budget_error == 0"
  ],
  "evidence_generation_mode": "experiment_local_declared_probe",
  "identity_acceptance_blocker": "unauthorized_identity_acceptance_event",
  "identity_acceptance_contract_available": false,
  "identity_acceptance_event_emitted": false,
  "later_cycle_basin_evidence_digest": "c3cce5e44ce3dc9cd43914a09b73e7e8e243099af6ba4a705212c0321371f185",
  "later_cycle_consumed_updated_basin_evidence": true,
  "later_cycle_consumption_record_digest": "f2bb4aa163771ce41bf5ebf99b003337720be031df6a830a4e5d10ba2c9ed632",
  "metric_id": "n07_reflexive_closure_reentry_v1",
  "native_policy_available": false,
  "native_policy_blocker": "native_reflexive_closure_policy_missing",
  "native_runtime_observed": false,
  "nonnegative_state_passed": true,
  "producer_changed_topology": false,
  "producer_mutated_coherence": false,
  "producer_mutated_state": false,
  "proper_time_persistence_evaluator_digest": "348d3dd07b04d08dcbaaa50975225367bb75b6ee32a39a53e584989e7a859016",
  "proper_time_persistence_evaluator_id": "n07_i7_proper_time_identity_persistence_evaluator_v1",
  "proper_time_persistence_passed": true,
  "record_id": "n07_i7_reflexive_closure_record_v1",
  "record_kind": "experiment_local_reflexive_closure_record",
  "reentry_coherence_into_support": 0.08,
  "reflexive_closure_component_native_support_status": "experiment_local",
  "reflexive_closure_gate": "pass",
  "reflexive_closure_record_digest": "2d4afdd8964b0192c160af1eca65b853636aee16f5b57c8286f76614b9ebf392",
  "reflexive_closure_record_digest_input": {
    "basin_evidence_chain_digest": "12520b48b2d9e62376ff55546ec853f5bd1dd2d866aff3ef93b306f9ccec1724",
    "conditions": [
      "reentry_coherence_into_support > 0",
      "basin_evidence_after_reentry >= basin_evidence_before_reentry",
      "later_cycle_consumed_updated_basin_evidence = true",
      "budget_error == 0"
    ],
    "metric_id": "n07_reflexive_closure_reentry_v1",
    "processed_packet_event_digest": "ce104d660d36eaf29066b97875f8c587787bcbff701fcb610ef72cbd4256f459",
    "producer_record_digest": "d6a2d186ecb99f9c44372d16ca09cd44565b68cd4e10a2e03208ac66210313af",
    "proper_time_persistence_evaluator_digest": "348d3dd07b04d08dcbaaa50975225367bb75b6ee32a39a53e584989e7a859016",
    "reentry_packet_event_digest": "b25b802b55217bb687defbe3add64a5f24133005ed0aff0e1969e0876369831d",
    "source_id4_stress_candidate_row_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
    "source_topology_stress_record_digest": "9c4ed80df8f1c0eadac9a5ab0f2034f2d792785213d21be29aa98fcc06b4b70c"
  },
  "reflexive_closure_record_idempotency_key": {
    "basin_evidence_chain_digest": "12520b48b2d9e62376ff55546ec853f5bd1dd2d866aff3ef93b306f9ccec1724",
    "metric_id": "n07_reflexive_closure_reentry_v1",
    "reentry_packet_event_digest": "b25b802b55217bb687defbe3add64a5f24133005ed0aff0e1969e0876369831d",
    "source_id4_stress_candidate_row_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba"
  },
  "reflexive_closure_record_idempotency_key_digest": "67e7c0a7f04a01e966e564726e84292b9d777fbc581cddd529c762157d7ed2dd",
  "report_side_only": false,
  "runtime_visible": false,
  "source_backed": true,
  "source_backing_kind": "iteration_7_artifact_generated_probe_record",
  "source_context_composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
  "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
  "source_event_digest": "7014cc83a38bfb897de72455316e5598a59a5df9102322a0e32563ecb826329d",
  "source_event_id": "n07_i7_reflexive_reentry_event_0001",
  "source_id4_stress_candidate_row_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
  "source_topology_stress_record_digest": "9c4ed80df8f1c0eadac9a5ab0f2034f2d792785213d21be29aa98fcc06b4b70c",
  "stale_digest_consumed": false,
  "step_processed_reentry_packet": true,
  "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
  "topology_family_id": "n07_T6_reflexive_closure"
}
```

## Candidate Row

```json
{
  "activity_history_digest": "9261be23e79b6bfacf05fb2f784bb5d47612886e9e1f457cebe2adf7191d4eac",
  "agency_claim_allowed": false,
  "becoming_class_status": "reusable_class",
  "birth_support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
  "boundary_rung": "recurrence_or_continuation",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "reflexively_self_maintaining_identity_candidate",
  "claim_flags": {
    "agency_claim_allowed": false,
    "agentic_like_claim_allowed": false,
    "ant_colony_claim_allowed": false,
    "biological_claim_allowed": false,
    "goal_proxy_regulation_claim_allowed": false,
    "identity_acceptance_claim_allowed": false,
    "intention_claim_allowed": false,
    "locomotion_like_claim_allowed": false,
    "memory_or_trail_claim_allowed": false,
    "movement_claim_allowed": false,
    "personhood_claim_allowed": false,
    "rc_identity_collapse_claim_allowed": false,
    "semantic_choice_claim_allowed": false,
    "unrestricted_identity_claim_allowed": false,
    "unrestricted_movement_claim_allowed": false
  },
  "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
  "derived_id_ceiling": "ID5",
  "experiment_local_observables_used": [
    "n07_i7_reflexive_reentry_event_0001",
    "n07_i7_reflexive_closure_record_v1",
    "n07_i7_proper_time_identity_persistence_evaluator_v1",
    "reentry_packet_event",
    "later_cycle_consumed_updated_basin_evidence"
  ],
  "gate_vector": {
    "artifact_replay": "not_measured",
    "attractivity": "pass",
    "compatibility": "not_measured",
    "invariance": "pass",
    "lineage_current": "pass",
    "reflexive_closure": "pass",
    "stability": "pass",
    "support": "pass"
  },
  "id5_is_not_id6": true,
  "id_level": "ID5",
  "identity_acceptance_claim_allowed": false,
  "identity_acceptance_event_emitted": false,
  "identity_carrier_surface": "runtime_coherence_basin",
  "implementation_surface": "experiment_local_identity_gate_record",
  "later_cycle_consumption_record_digest": "f2bb4aa163771ce41bf5ebf99b003337720be031df6a830a4e5d10ba2c9ed632",
  "native_observables_used": [
    "surface_lineage_transport_context",
    "topology_state_reabsorption_context",
    "node_plus_packet_budget_accounting"
  ],
  "native_policy_blockers": [
    "native_reflexive_closure_policy_missing"
  ],
  "native_runtime_reflexive_closure_observed": false,
  "native_support_status": "mixed_native_experiment_local",
  "naturalization_rung": "Nat0_probe_dependent_expression",
  "primary_blocker": null,
  "probe_role": "diagnostic_probe",
  "proper_time_persistence_evaluator_digest": "348d3dd07b04d08dcbaaa50975225367bb75b6ee32a39a53e584989e7a859016",
  "proper_time_persistence_evaluator_id": "n07_i7_proper_time_identity_persistence_evaluator_v1",
  "rc_identity_collapse_claim_allowed": false,
  "reentry_node_lineage": {
    "birth_is_identity_acceptance": false,
    "born_node_id": 32,
    "lineage_action": "birth",
    "lineage_map": {
      "action": "birth",
      "born_node_ids": [
        32
      ],
      "born_node_parent_map": {
        "32": 30
      },
      "complete": true,
      "node_map": {
        "30": [
          30,
          32
        ],
        "31": [
          31
        ]
      },
      "retired_node_ids": [],
      "scrambled": false,
      "source_support_nodes": [
        30,
        31
      ],
      "target_support_nodes": [
        30,
        31,
        32
      ]
    },
    "lineage_transfer_map_digest": "70037da10c07fc329def298c94aaf75f5d48e6071d69cd85fc9f938fef5a84a1",
    "node_lineage_source_backed": true,
    "parent_node_id": 30,
    "source_iteration": "6B",
    "source_support_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
    "surface_lineage_record_digest": "9ca3eabfdaa9611fc127fe602c260cb576730ed0a84fbef3d8a2cffa53f446b9",
    "topology_event_digest": "d0b636dfa696a17d75740803074dd2c11b46dcf585450f11ac1de66c0b5888ca",
    "topology_event_id": "n07_i6b_topology_birth_support_A_0002",
    "topology_state_reabsorption_record_digest": "e5bc4a6f79e5a33ef9c4710c4863dee20ee00574c8f3f88a91e9d326d77e759d",
    "transported_support_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075"
  },
  "reflexive_closure_is_agency_claim": false,
  "reflexive_closure_native_support_status": "experiment_local",
  "reflexive_closure_record_digest": "2d4afdd8964b0192c160af1eca65b853636aee16f5b57c8286f76614b9ebf392",
  "reflexive_closure_record_id": "n07_i7_reflexive_closure_record_v1",
  "row_id": "n07_i7_id5_reflexive_closure_candidate_row_v1",
  "runtime_family": "LGRC9V3",
  "source_artifact_sha256": {
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77"
  },
  "source_artifacts": [
    {
      "name": "n07_fixture_manifest_v1",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json",
      "sha256": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603"
    },
    {
      "name": "n07_iteration_2_fixture_manifest_validation",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json",
      "sha256": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26"
    },
    {
      "id4_stress_candidate_row_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
      "name": "n07_iteration_6b_id4_topology_split_birth_invariance_stress",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json",
      "sha256": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
      "status": "passed",
      "topology_stress_record_digest": "9c4ed80df8f1c0eadac9a5ab0f2034f2d792785213d21be29aa98fcc06b4b70c"
    }
  ],
  "source_context_composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
  "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
  "source_id4_stress_candidate_row_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
  "source_id4_stress_candidate_row_id": "n07_i6b_id4_split_birth_invariance_stress_candidate_row_v1",
  "source_reports": [
    {
      "name": "n07_iteration_6b_id4_topology_split_birth_invariance_stress_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md",
      "sha256": "5ef2dda323b44c4e6c2cd026773a90e0dbe2d41e8b7c28671e8dc372a8a1a8c8"
    }
  ],
  "source_topology_stress_record_digest": "9c4ed80df8f1c0eadac9a5ab0f2034f2d792785213d21be29aa98fcc06b4b70c",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_dependency_status": "probe_dependent",
  "t4_deferral_rationale": "Iteration 7 tests reflexive closure on the lineage-current 6-B source context; topology-free recurrence remains a deferred T4 baseline.",
  "t4_no_mutation_recurrence_baseline_status": "deferred",
  "topology_family_id": "n07_T6_reflexive_closure",
  "unrestricted_identity_claim_allowed": false,
  "visual_is_evidence_source": false,
  "visual_reference": null,
  "withdrawal_test_status": "not_tested"
}
```

## Scope Limitations

```json
{
  "agency": "blocked",
  "composite_topology_under_test": "n07_C1_recurrent_single_basin_identity_candidate",
  "id6_artifact_only_replay": "pending_iteration_7B_source_backed_t6_then_iteration_8",
  "identity_acceptance": "blocked",
  "native_reflexive_closure_policy_available": false,
  "native_runtime_reflexive_closure_observed": false,
  "reflexive_closure_measurements": "experiment_local_declared_probe_values",
  "source_context": "iteration_6b_lineage_current_topology_stress_candidate",
  "source_context_composite": "n07_C2_lineage_current_topology_mutating_identity_candidate",
  "source_context_topology": "n07_T5_lineage_current_invariance",
  "t4_no_mutation_recurrence_baseline": "deferred",
  "topology_family_under_test": "n07_T6_reflexive_closure"
}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
| `no_reentry` | `blocked` | `no_reentry` | `ID4` |
| `closure_not_consumed_by_later_cycle` | `blocked` | `closure_not_consumed_by_later_cycle` | `ID4` |
| `improper_proper_time_threshold` | `blocked` | `improper_proper_time_threshold` | `ID4` |
| `failed_persistence` | `blocked` | `failed_persistence` | `ID4` |
| `unauthorized_identity_acceptance_event` | `blocked` | `unauthorized_identity_acceptance_event` | `ID4` |
| `producer_mutation_boundary_violation` | `blocked` | `producer_mutation_boundary_violation` | `ID4` |
| `agency_claim_promotion` | `blocked` | `agency_claim_promotion` | `ID4` |

## Checks

| Check | Passed |
|---|---:|
| `agency_and_identity_acceptance_blocked` | `True` |
| `basin_evidence_after_reentry_strengthened` | `True` |
| `basin_evidence_chain_ordered` | `True` |
| `becoming_method_values_allowed` | `True` |
| `budget_exact` | `True` |
| `candidate_carrier_is_coherence_basin` | `True` |
| `candidate_composite_matches_manifest` | `True` |
| `claim_ceiling_scoped` | `True` |
| `claim_flag_keys_match_manifest` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_canonical` | `True` |
| `control_blockers_distinct` | `True` |
| `control_ceilings_id4` | `True` |
| `controls_blocked` | `True` |
| `derived_ceiling_id5` | `True` |
| `evidence_only_surfaces_not_promoted` | `True` |
| `experiment_local_provenance_disclosed` | `True` |
| `gate_vector_schema_matches_manifest` | `True` |
| `identity_acceptance_event_not_emitted` | `True` |
| `later_cycle_consumed_updated_digest` | `True` |
| `later_cycle_consumption_record_matches_digest` | `True` |
| `metric_conditions_passed` | `True` |
| `metric_policy_matches_manifest` | `True` |
| `native_support_not_overstated` | `True` |
| `no_src_changes_required` | `True` |
| `nonnegative_state_passed` | `True` |
| `processed_packet_links_to_scheduled_packet` | `True` |
| `producer_boundary_preserved` | `True` |
| `proper_time_evaluator_digest_recomputed` | `True` |
| `proper_time_evaluator_scope_disclosed` | `True` |
| `proper_time_persistence_evaluation_passed` | `True` |
| `reentry_node_lineage_source_backed` | `True` |
| `reflexive_closure_record_digest_recomputed` | `True` |
| `required_controls_present` | `True` |
| `source_context_preserved_as_t5_c2` | `True` |
| `source_id4_stress_candidate_passed` | `True` |
| `source_iteration_6b_points_to_iteration_7` | `True` |
| `source_iteration_6b_status_passed` | `True` |
| `stale_digest_not_consumed` | `True` |
| `status_passed` | `True` |
| `t4_deferral_recorded` | `True` |
| `t6_topology_family_declared` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "964ba7adf04b75da8889590e2eb6f05656fce8bb75f8328f439f008cb372a137",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "b8f0d288826268cd4bb2ad55274aa12e92fdc0e9efe2111b1e2e8020b981fce1",
  "id5_candidate_row_digest": "1d9a5bca48662fbb927e66abfd3ee346a0adb512da5fbc0a9ae59f39417a6e2a",
  "proper_time_persistence_evaluation_digest": "045c6dcb159f5205413aaac393981bfd23ad5170f87b626e95474751f18a4b2d",
  "reentry_event_digest": "7014cc83a38bfb897de72455316e5598a59a5df9102322a0e32563ecb826329d",
  "reflexive_closure_record_digest": "1e7e20292a217c1a8549f08e7fea8cf45000f8a192acd16539400c6ace0d90f1",
  "source_iteration_6b_output_digest": "4afe80c667d17079a9cf6b1d7a70be3a37bd366e1b421706bd121c78db34a988"
}
```

## Acceptance

Iteration 7 passes because re-entry into the candidate coherence basin
maintains/strengthens serialized experiment-local basin evidence and a later
proper-time cycle consumes the updated evidence digest. The result reaches ID5
only; it does not support agency, identity acceptance, or native LGRC identity
support.
