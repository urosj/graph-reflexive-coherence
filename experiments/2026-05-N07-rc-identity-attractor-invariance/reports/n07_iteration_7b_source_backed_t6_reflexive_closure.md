# N07 Iteration 7-B: Source-Backed T6 Reflexive Closure

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_7b_source_backed_t6_reflexive_closure.py
```

Iteration 7-B consumes the Iteration 6-B T5 lineage-current source context and
the Iteration 7 T6 design probe. It then emits a stricter T6 chain from
serialized state rows, experiment-local packet application records, and a
later producer-linkage record that consumes the updated basin evidence digest.

The result is source-backed and artifact-derived, but it is still not native
LGRC reflexive-closure support. Native reflexive-closure policy remains
unavailable. Packet and producer records are digest-chain source-backed but
experiment-local constructions; they do not claim actual LGRC `step()`
execution.

## Source-Backed T6 Chain

```json
{
  "all_measurements_derived_from_source_rows": true,
  "allocation_policy": {
    "core_membership_policy_id": "n07_i7b_core_membership_design_policy_v1",
    "node_weight_fraction": {
      "30": 0.35,
      "31": 0.33,
      "32": 0.32
    },
    "policy_id": "n07_i7b_pre_state_allocation_from_6b_final_mass_v1",
    "policy_is_serialized": true,
    "policy_origin": "experiment_local_design_probe",
    "source": "iteration_6b_final_cycle_support_area_mass_after",
    "weights_derivation_kind": "serialized_experiment_local_design_policy",
    "weights_source_backed": false
  },
  "artifact_visible": true,
  "basin_evidence_digests": [
    "95b8a15748aa01d16a29ae2b81b4b8a8a6295c99660e48e157d1c8d582de2f16",
    "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
    "12720b3d71c062d4c62c283fd8310c66100b1c733d9161d42702f5e38fb0e84e"
  ],
  "basin_evidence_score_strengthened_after_reentry": true,
  "birth_lineage_context": {
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
  "budget_error_max": 0.0,
  "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
  "core_membership_policy": {
    "born_node_id": 32,
    "core_membership_derivation_kind": "experiment_local_design_policy_over_source_backed_support_nodes",
    "core_membership_source_backed": false,
    "core_node_ids": [
      30,
      31
    ],
    "parent_node_id": 30,
    "peer_core_node_id": 31,
    "peripheral_node_ids": [
      32
    ],
    "policy_id": "n07_i7b_core_membership_design_policy_v1",
    "policy_origin": "experiment_local_design_probe",
    "rule": "parent_node_and_existing_peer_support_node_are_core; born_node_is_peripheral_reentry_source",
    "source_support_node_ids": [
      30,
      31,
      32
    ],
    "support_membership_source_backed": true,
    "support_membership_source_field": "iteration_6b_final_cycle.support_node_ids"
  },
  "event_id": "n07_i7b_source_backed_t6_reflexive_closure_event_0001",
  "event_kind": "source_backed_artifact_derived_t6_reflexive_closure",
  "later_cycle_consumed_updated_basin_evidence": true,
  "later_cycle_consumption_constructed_by_artifact_chain": true,
  "later_cycle_consumption_independently_observed": false,
  "later_cycle_consumption_validation_scope": "artifact_chain_digest_linkage_not_independent_runtime_observation",
  "later_cycle_producer_record": {
    "artifact_visible": true,
    "causal_basin_evidence_digest": "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
    "digest_chain_source_backed": true,
    "experiment_local_constructed": true,
    "independently_observed_runtime_producer_record": false,
    "native_runtime_observed": false,
    "producer_changed_topology": false,
    "producer_emitted_claim_label": false,
    "producer_mutated_coherence": false,
    "producer_record_digest": "e7eaab4b6099c147c01f2d1771262dd77adc3a8ed680800e1cd835f290f8f42b",
    "producer_record_id": "n07_i7b_later_cycle_producer_record_0001",
    "reason_code": "source_backed_t6_later_cycle_consumed_updated_basin_evidence",
    "record_kind": "artifact_derived_later_cycle_producer_record",
    "references_source_backed_state": true,
    "scheduled_packet_id": "n07_i7b_scheduled_later_reentry_packet_0002",
    "scheduler_event_index": 23,
    "source_backed": false,
    "source_backing_scope": "references_post_reentry_basin_evidence_digest_only",
    "source_state_digest": "9ea80b8a4c9d26f099ef0ff067f8629269da808c08e782c5d4ad58b58ccf8d38"
  },
  "later_cycle_state_row": {
    "artifact_visible": true,
    "authored_measurement_value": false,
    "basin_evidence_digest": "12720b3d71c062d4c62c283fd8310c66100b1c733d9161d42702f5e38fb0e84e",
    "basin_evidence_digest_input": {
      "basin_evidence_score": 1.26632,
      "consumed_basin_evidence_digest": "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
      "proper_time_persistence_score": 0.937265,
      "retention_score": 0.87453,
      "state_digest": "ac273d194207e577eba900fec8ec816e40508eb0fc71fc8f399989a274cdb08e",
      "support_area_mass": 1.448
    },
    "basin_evidence_score": 1.26632,
    "budget_after": 6.0,
    "budget_before": 6.0,
    "budget_error": 0.0,
    "budget_surface": "node_plus_packet",
    "consumed_basin_evidence_digest": "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
    "core_mass": 1.08464,
    "core_membership_policy": {
      "born_node_id": 32,
      "core_membership_derivation_kind": "experiment_local_design_policy_over_source_backed_support_nodes",
      "core_membership_source_backed": false,
      "core_node_ids": [
        30,
        31
      ],
      "parent_node_id": 30,
      "peer_core_node_id": 31,
      "peripheral_node_ids": [
        32
      ],
      "policy_id": "n07_i7b_core_membership_design_policy_v1",
      "policy_origin": "experiment_local_design_probe",
      "rule": "parent_node_and_existing_peer_support_node_are_core; born_node_is_peripheral_reentry_source",
      "source_support_node_ids": [
        30,
        31,
        32
      ],
      "support_membership_source_backed": true,
      "support_membership_source_field": "iteration_6b_final_cycle.support_node_ids"
    },
    "core_membership_source_backed": false,
    "core_node_ids": [
      30,
      31
    ],
    "derivation_kind": "derived_by_later_cycle_consuming_updated_basin_evidence",
    "native_runtime_observed": false,
    "node_coherence": {
      "30": 0.6068,
      "31": 0.47784,
      "32": 0.36336
    },
    "nonnegative_state_passed": true,
    "peripheral_mass": 0.36336,
    "policy_derived_measurement_values": true,
    "proper_time_index": 9,
    "proper_time_persistence_score": 0.937265,
    "retention_score": 0.87453,
    "row_id": "n07_i7b_later_cycle_state_row_v1",
    "row_kind": "artifact_derived_basin_state_row",
    "scheduler_event_index": 26,
    "source_backed": true,
    "source_record_digest": "531e86dfe206e6a26989aed4c81b7f0b51d2332dd808c3f02debb954ad7587d8",
    "state_digest": "ac273d194207e577eba900fec8ec816e40508eb0fc71fc8f399989a274cdb08e",
    "state_digest_input": {
      "consumed_basin_evidence_digest": "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
      "core_node_ids": [
        30,
        31
      ],
      "metrics": {
        "basin_evidence_score": 1.26632,
        "core_mass": 1.08464,
        "peripheral_mass": 0.36336,
        "proper_time_persistence_score": 0.937265,
        "retention_score": 0.87453,
        "support_area_mass": 1.448
      },
      "node_coherence": {
        "30": 0.6068,
        "31": 0.47784,
        "32": 0.36336
      },
      "proper_time_index": 9,
      "row_id": "n07_i7b_later_cycle_state_row_v1",
      "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
      "support_node_ids": [
        30,
        31,
        32
      ]
    },
    "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "support_area_mass": 1.448,
    "support_membership_source_backed": true,
    "support_node_ids": [
      30,
      31,
      32
    ]
  },
  "later_cycle_used_stale_pre_reentry_digest": false,
  "metric_id": "n07_reflexive_closure_reentry_v1",
  "native_reflexive_closure_policy_available": false,
  "native_reflexive_closure_policy_blocker": "native_reflexive_closure_policy_missing",
  "native_runtime_observed": false,
  "nonnegative_state_passed": true,
  "packet_application_scope": "experiment_local_step_semantics_simulation",
  "post_reentry_state_row": {
    "artifact_visible": true,
    "authored_measurement_value": false,
    "basin_evidence_digest": "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
    "basin_evidence_digest_input": {
      "basin_evidence_score": 1.25632,
      "consumed_basin_evidence_digest": "95b8a15748aa01d16a29ae2b81b4b8a8a6295c99660e48e157d1c8d582de2f16",
      "proper_time_persistence_score": 0.933812,
      "retention_score": 0.867624,
      "state_digest": "9ea80b8a4c9d26f099ef0ff067f8629269da808c08e782c5d4ad58b58ccf8d38",
      "support_area_mass": 1.448
    },
    "basin_evidence_score": 1.25632,
    "budget_after": 6.0,
    "budget_before": 6.0,
    "budget_error": 0.0,
    "budget_surface": "node_plus_packet",
    "consumed_basin_evidence_digest": "95b8a15748aa01d16a29ae2b81b4b8a8a6295c99660e48e157d1c8d582de2f16",
    "core_mass": 1.06464,
    "core_membership_policy": {
      "born_node_id": 32,
      "core_membership_derivation_kind": "experiment_local_design_policy_over_source_backed_support_nodes",
      "core_membership_source_backed": false,
      "core_node_ids": [
        30,
        31
      ],
      "parent_node_id": 30,
      "peer_core_node_id": 31,
      "peripheral_node_ids": [
        32
      ],
      "policy_id": "n07_i7b_core_membership_design_policy_v1",
      "policy_origin": "experiment_local_design_probe",
      "rule": "parent_node_and_existing_peer_support_node_are_core; born_node_is_peripheral_reentry_source",
      "source_support_node_ids": [
        30,
        31,
        32
      ],
      "support_membership_source_backed": true,
      "support_membership_source_field": "iteration_6b_final_cycle.support_node_ids"
    },
    "core_membership_source_backed": false,
    "core_node_ids": [
      30,
      31
    ],
    "derivation_kind": "derived_by_applying_processed_reentry_packet_to_pre_state",
    "native_runtime_observed": false,
    "node_coherence": {
      "30": 0.5868,
      "31": 0.47784,
      "32": 0.38336
    },
    "nonnegative_state_passed": true,
    "peripheral_mass": 0.38336,
    "policy_derived_measurement_values": true,
    "proper_time_index": 8,
    "proper_time_persistence_score": 0.933812,
    "retention_score": 0.867624,
    "row_id": "n07_i7b_post_reentry_state_row_v1",
    "row_kind": "artifact_derived_basin_state_row",
    "scheduler_event_index": 22,
    "source_backed": true,
    "source_record_digest": "c7bdc052c0f385b5a90ed1c18e85f00ba2a377a18ee96b556b48ce30c6d1ecf5",
    "state_digest": "9ea80b8a4c9d26f099ef0ff067f8629269da808c08e782c5d4ad58b58ccf8d38",
    "state_digest_input": {
      "consumed_basin_evidence_digest": "95b8a15748aa01d16a29ae2b81b4b8a8a6295c99660e48e157d1c8d582de2f16",
      "core_node_ids": [
        30,
        31
      ],
      "metrics": {
        "basin_evidence_score": 1.25632,
        "core_mass": 1.06464,
        "peripheral_mass": 0.38336,
        "proper_time_persistence_score": 0.933812,
        "retention_score": 0.867624,
        "support_area_mass": 1.448
      },
      "node_coherence": {
        "30": 0.5868,
        "31": 0.47784,
        "32": 0.38336
      },
      "proper_time_index": 8,
      "row_id": "n07_i7b_post_reentry_state_row_v1",
      "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
      "support_node_ids": [
        30,
        31,
        32
      ]
    },
    "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "support_area_mass": 1.448,
    "support_membership_source_backed": true,
    "support_node_ids": [
      30,
      31,
      32
    ]
  },
  "pre_reentry_state_row": {
    "artifact_visible": true,
    "authored_measurement_value": false,
    "basin_evidence_digest": "95b8a15748aa01d16a29ae2b81b4b8a8a6295c99660e48e157d1c8d582de2f16",
    "basin_evidence_digest_input": {
      "basin_evidence_score": 1.21632,
      "consumed_basin_evidence_digest": null,
      "proper_time_persistence_score": 0.92,
      "retention_score": 0.84,
      "state_digest": "b576cce8f30cc10c5212db2a041a77ea253ea684058352f56df6144a861c6989",
      "support_area_mass": 1.448
    },
    "basin_evidence_score": 1.21632,
    "budget_after": 6.0,
    "budget_before": 6.0,
    "budget_error": 0.0,
    "budget_surface": "node_plus_packet",
    "consumed_basin_evidence_digest": null,
    "core_mass": 0.98464,
    "core_membership_policy": {
      "born_node_id": 32,
      "core_membership_derivation_kind": "experiment_local_design_policy_over_source_backed_support_nodes",
      "core_membership_source_backed": false,
      "core_node_ids": [
        30,
        31
      ],
      "parent_node_id": 30,
      "peer_core_node_id": 31,
      "peripheral_node_ids": [
        32
      ],
      "policy_id": "n07_i7b_core_membership_design_policy_v1",
      "policy_origin": "experiment_local_design_probe",
      "rule": "parent_node_and_existing_peer_support_node_are_core; born_node_is_peripheral_reentry_source",
      "source_support_node_ids": [
        30,
        31,
        32
      ],
      "support_membership_source_backed": true,
      "support_membership_source_field": "iteration_6b_final_cycle.support_node_ids"
    },
    "core_membership_source_backed": false,
    "core_node_ids": [
      30,
      31
    ],
    "derivation_kind": "derived_from_6b_final_cycle_mass_and_serialized_allocation_policy",
    "native_runtime_observed": false,
    "node_coherence": {
      "30": 0.5068,
      "31": 0.47784,
      "32": 0.46336
    },
    "nonnegative_state_passed": true,
    "peripheral_mass": 0.46336,
    "policy_derived_measurement_values": true,
    "proper_time_index": 7,
    "proper_time_persistence_score": 0.92,
    "retention_score": 0.84,
    "row_id": "n07_i7b_pre_reentry_state_row_v1",
    "row_kind": "artifact_derived_basin_state_row",
    "scheduler_event_index": 19,
    "source_backed": true,
    "source_record_digest": "cbfa440ba79687d2afa7649d538ceddc1152f273d5f2bd432e31fa9f35743574",
    "state_digest": "b576cce8f30cc10c5212db2a041a77ea253ea684058352f56df6144a861c6989",
    "state_digest_input": {
      "consumed_basin_evidence_digest": null,
      "core_node_ids": [
        30,
        31
      ],
      "metrics": {
        "basin_evidence_score": 1.21632,
        "core_mass": 0.98464,
        "peripheral_mass": 0.46336,
        "proper_time_persistence_score": 0.92,
        "retention_score": 0.84,
        "support_area_mass": 1.448
      },
      "node_coherence": {
        "30": 0.5068,
        "31": 0.47784,
        "32": 0.46336
      },
      "proper_time_index": 7,
      "row_id": "n07_i7b_pre_reentry_state_row_v1",
      "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
      "support_node_ids": [
        30,
        31,
        32
      ]
    },
    "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "support_area_mass": 1.448,
    "support_membership_source_backed": true,
    "support_node_ids": [
      30,
      31,
      32
    ]
  },
  "processed_packet_digests": [
    "53d8720713ec683aa3cbdccb61475c97ea10a8819bb9368bf36563789353c11d",
    "104ed468da9249a0edfde1795e753c2ce0aa7eff7a9d816617ff1141e74cd745"
  ],
  "processed_packet_records": [
    {
      "artifact_visible": true,
      "basin_evidence_score_after": 1.25632,
      "basin_evidence_score_before": 1.21632,
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "digest_chain_source_backed": true,
      "experiment_local_constructed": true,
      "experiment_local_mutation_simulated": true,
      "experiment_local_packet_applied": true,
      "native_runtime_observed": false,
      "post_state_digest": "9ea80b8a4c9d26f099ef0ff067f8629269da808c08e782c5d4ad58b58ccf8d38",
      "pre_state_digest": "b576cce8f30cc10c5212db2a041a77ea253ea684058352f56df6144a861c6989",
      "processed_by_actual_lgrc_step": false,
      "processed_packet_digest": "53d8720713ec683aa3cbdccb61475c97ea10a8819bb9368bf36563789353c11d",
      "processed_packet_id": "n07_i7b_processed_reentry_packet_0001",
      "producer_changed_topology": false,
      "producer_mutated_state": false,
      "references_source_backed_state": true,
      "runtime_step_contract_claimed": false,
      "scheduled_packet_digest": "c7bdc052c0f385b5a90ed1c18e85f00ba2a377a18ee96b556b48ce30c6d1ecf5",
      "scheduled_packet_id": "n07_i7b_scheduled_reentry_packet_0001",
      "scheduler_event_index": 21,
      "source_backed": false,
      "source_backing_scope": "pre_state_and_post_state_digests_are_source_backed",
      "step_owned_mutation": false,
      "step_processed": false,
      "step_semantics_simulated": true,
      "support_area_mass_after": 1.448,
      "support_area_mass_before": 1.448
    },
    {
      "artifact_visible": true,
      "basin_evidence_score_after": 1.26632,
      "basin_evidence_score_before": 1.25632,
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "digest_chain_source_backed": true,
      "experiment_local_constructed": true,
      "experiment_local_mutation_simulated": true,
      "experiment_local_packet_applied": true,
      "native_runtime_observed": false,
      "post_state_digest": "ac273d194207e577eba900fec8ec816e40508eb0fc71fc8f399989a274cdb08e",
      "pre_state_digest": "9ea80b8a4c9d26f099ef0ff067f8629269da808c08e782c5d4ad58b58ccf8d38",
      "processed_by_actual_lgrc_step": false,
      "processed_packet_digest": "104ed468da9249a0edfde1795e753c2ce0aa7eff7a9d816617ff1141e74cd745",
      "processed_packet_id": "n07_i7b_processed_later_reentry_packet_0002",
      "producer_changed_topology": false,
      "producer_mutated_state": false,
      "references_source_backed_state": true,
      "runtime_step_contract_claimed": false,
      "scheduled_packet_digest": "531e86dfe206e6a26989aed4c81b7f0b51d2332dd808c3f02debb954ad7587d8",
      "scheduled_packet_id": "n07_i7b_scheduled_later_reentry_packet_0002",
      "scheduler_event_index": 25,
      "source_backed": false,
      "source_backing_scope": "pre_state_and_post_state_digests_are_source_backed",
      "step_owned_mutation": false,
      "step_processed": false,
      "step_semantics_simulated": true,
      "support_area_mass_after": 1.448,
      "support_area_mass_before": 1.448
    }
  ],
  "reentry_coherence_into_support": 0.08,
  "scheduled_packet_digests": [
    "c7bdc052c0f385b5a90ed1c18e85f00ba2a377a18ee96b556b48ce30c6d1ecf5",
    "531e86dfe206e6a26989aed4c81b7f0b51d2332dd808c3f02debb954ad7587d8"
  ],
  "scheduled_packet_records": [
    {
      "amount": 0.08,
      "artifact_visible": true,
      "causal_basin_evidence_digest": "95b8a15748aa01d16a29ae2b81b4b8a8a6295c99660e48e157d1c8d582de2f16",
      "digest_chain_source_backed": true,
      "experiment_local_constructed": true,
      "native_runtime_observed": false,
      "packet_digest": "c7bdc052c0f385b5a90ed1c18e85f00ba2a377a18ee96b556b48ce30c6d1ecf5",
      "packet_id": "n07_i7b_scheduled_reentry_packet_0001",
      "polarity": "reentry_into_support",
      "reason_code": "source_backed_t6_reentry_packet_scheduled",
      "record_kind": "artifact_derived_scheduled_reentry_packet",
      "references_source_backed_state": true,
      "route_node_ids": [
        32,
        30
      ],
      "scheduler_event_index": 20,
      "source_backed": false,
      "source_backing_scope": "references_source_backed_basin_evidence_digest_only",
      "source_node_id": 32,
      "target_node_id": 30
    },
    {
      "amount": 0.02,
      "artifact_visible": true,
      "causal_basin_evidence_digest": "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
      "digest_chain_source_backed": true,
      "experiment_local_constructed": true,
      "native_runtime_observed": false,
      "packet_digest": "531e86dfe206e6a26989aed4c81b7f0b51d2332dd808c3f02debb954ad7587d8",
      "packet_id": "n07_i7b_scheduled_later_reentry_packet_0002",
      "polarity": "reentry_into_support",
      "reason_code": "source_backed_t6_later_reentry_packet_scheduled",
      "record_kind": "artifact_derived_scheduled_reentry_packet",
      "references_source_backed_state": true,
      "route_node_ids": [
        32,
        30
      ],
      "scheduler_event_index": 24,
      "source_backed": false,
      "source_backing_scope": "references_source_backed_basin_evidence_digest_only",
      "source_node_id": 32,
      "target_node_id": 30
    }
  ],
  "source_backed": true,
  "source_backing_scope": "state_rows_and_digest_chain_source_backed; packet_and_producer_records are experiment_local_constructed",
  "source_context_composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
  "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
  "source_iteration_6b_output_path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json",
  "source_iteration_6b_output_sha256": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
  "source_iteration_7_design_probe_digest": "1d9a5bca48662fbb927e66abfd3ee346a0adb512da5fbc0a9ae59f39417a6e2a",
  "source_iteration_7_design_probe_path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json",
  "source_iteration_7_design_probe_sha256": "59b6a2dd5f0b88abe453997e74263ef4cf01ce629f975b0fb6f1712e98dde15e",
  "state_row_digests": [
    "b576cce8f30cc10c5212db2a041a77ea253ea684058352f56df6144a861c6989",
    "9ea80b8a4c9d26f099ef0ff067f8629269da808c08e782c5d4ad58b58ccf8d38",
    "ac273d194207e577eba900fec8ec816e40508eb0fc71fc8f399989a274cdb08e"
  ],
  "support_area_mass_maintained_after_reentry": true,
  "topology_family_id": "n07_T6_reflexive_closure"
}
```

## T6 Record

```json
{
  "actual_lgrc_step_processed_packet": false,
  "all_measurements_derived_from_source_rows": true,
  "allocation_policy_origin": "experiment_local_design_probe",
  "allocation_weights_source_backed": false,
  "artifact_visible": true,
  "authored_measurement_values_present": false,
  "basin_evidence_score_after_reentry": 1.25632,
  "basin_evidence_score_before_reentry": 1.21632,
  "basin_evidence_score_strengthened_after_reentry": true,
  "budget_error_max": 0.0,
  "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
  "core_membership_derivation_kind": "experiment_local_design_policy_over_source_backed_support_nodes",
  "core_membership_policy_id": "n07_i7b_core_membership_design_policy_v1",
  "core_membership_source_backed": false,
  "experiment_local_packet_application": true,
  "identity_acceptance_blocker": "unauthorized_identity_acceptance_event",
  "identity_acceptance_event_emitted": false,
  "later_cycle_basin_evidence_digest": "12720b3d71c062d4c62c283fd8310c66100b1c733d9161d42702f5e38fb0e84e",
  "later_cycle_consumed_updated_basin_evidence": true,
  "later_cycle_consumption_constructed_by_artifact_chain": true,
  "later_cycle_consumption_independently_observed": false,
  "later_cycle_consumption_validation_scope": "artifact_chain_digest_linkage_not_independent_runtime_observation",
  "later_cycle_state_digest": "ac273d194207e577eba900fec8ec816e40508eb0fc71fc8f399989a274cdb08e",
  "later_cycle_used_stale_pre_reentry_digest": false,
  "metric_id": "n07_reflexive_closure_reentry_v1",
  "native_reflexive_closure_policy_available": false,
  "native_reflexive_closure_policy_blocker": "native_reflexive_closure_policy_missing",
  "native_runtime_observed": false,
  "nonnegative_state_passed": true,
  "packet_application_scope": "experiment_local_step_semantics_simulation",
  "post_reentry_basin_evidence_digest": "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
  "post_reentry_state_digest": "9ea80b8a4c9d26f099ef0ff067f8629269da808c08e782c5d4ad58b58ccf8d38",
  "pre_reentry_basin_evidence_digest": "95b8a15748aa01d16a29ae2b81b4b8a8a6295c99660e48e157d1c8d582de2f16",
  "pre_reentry_state_digest": "b576cce8f30cc10c5212db2a041a77ea253ea684058352f56df6144a861c6989",
  "producer_changed_topology": false,
  "producer_emitted_claim_label": false,
  "producer_mutated_state": false,
  "proper_time_persistence_evaluator_digest": "2a88ae2d8ae01c12c27eb6ba514a06a9b87eef8667e1e9a852fefc2a38965753",
  "proper_time_persistence_evaluator_id": "n07_i7b_proper_time_identity_persistence_evaluator_v1",
  "proper_time_persistence_passed": true,
  "record_id": "n07_i7b_source_backed_t6_reflexive_closure_record_v1",
  "record_kind": "source_backed_artifact_derived_t6_reflexive_closure_record",
  "reentry_coherence_into_support": 0.08,
  "source_backed": true,
  "source_backing_scope": "state_rows_and_digest_chain_source_backed; packet_and_producer_records are experiment_local_constructed",
  "source_context_composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
  "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
  "source_event_digest": "96cc04a82aeaed185ba540c1201911113b8af1c074bb24a79bc41fdffd0b381f",
  "source_event_id": "n07_i7b_source_backed_t6_reflexive_closure_event_0001",
  "support_area_mass_after_reentry": 1.448,
  "support_area_mass_before_reentry": 1.448,
  "support_area_mass_maintained_after_reentry": true,
  "t4_deferral_rationale": "T4 is the recurrence/no-mutation baseline and must be run before interpreting topology-free recurrence as stronger than ID4.",
  "t4_no_mutation_baseline_deferred": true,
  "t6_record_digest": "f8852c2e90beae00489abd6ec2d93c2b5bba6a268826c6baeb61d8fad809f0f0",
  "t6_record_digest_input": {
    "basin_evidence_digests": [
      "95b8a15748aa01d16a29ae2b81b4b8a8a6295c99660e48e157d1c8d582de2f16",
      "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
      "12720b3d71c062d4c62c283fd8310c66100b1c733d9161d42702f5e38fb0e84e"
    ],
    "metric_id": "n07_reflexive_closure_reentry_v1",
    "processed_packet_digests": [
      "53d8720713ec683aa3cbdccb61475c97ea10a8819bb9368bf36563789353c11d",
      "104ed468da9249a0edfde1795e753c2ce0aa7eff7a9d816617ff1141e74cd745"
    ],
    "proper_time_persistence_evaluator_digest": "2a88ae2d8ae01c12c27eb6ba514a06a9b87eef8667e1e9a852fefc2a38965753",
    "record_id": "n07_i7b_source_backed_t6_reflexive_closure_record_v1",
    "scheduled_packet_digests": [
      "c7bdc052c0f385b5a90ed1c18e85f00ba2a377a18ee96b556b48ce30c6d1ecf5",
      "531e86dfe206e6a26989aed4c81b7f0b51d2332dd808c3f02debb954ad7587d8"
    ],
    "source_event_digest": "96cc04a82aeaed185ba540c1201911113b8af1c074bb24a79bc41fdffd0b381f",
    "state_row_digests": [
      "b576cce8f30cc10c5212db2a041a77ea253ea684058352f56df6144a861c6989",
      "9ea80b8a4c9d26f099ef0ff067f8629269da808c08e782c5d4ad58b58ccf8d38",
      "ac273d194207e577eba900fec8ec816e40508eb0fc71fc8f399989a274cdb08e"
    ]
  },
  "t6_record_idempotency_key": {
    "later_cycle_basin_evidence_digest": "12720b3d71c062d4c62c283fd8310c66100b1c733d9161d42702f5e38fb0e84e",
    "metric_id": "n07_reflexive_closure_reentry_v1",
    "post_reentry_basin_evidence_digest": "b64ecbe220b6004b4d036bac00db64e3022abb01c862587b1f4ec1e1fe7f0c59",
    "source_event_digest": "96cc04a82aeaed185ba540c1201911113b8af1c074bb24a79bc41fdffd0b381f"
  },
  "topology_family_id": "n07_T6_reflexive_closure"
}
```

## Candidate Row

```json
{
  "activity_history_digest": "43f7a966cc303e56d20bc4fe558bdf697ef0c0e74a054472828359fcc9c7cfbd",
  "actual_lgrc_step_processed_packet": false,
  "agency_claim_allowed": false,
  "allocation_policy_origin": "experiment_local_design_probe",
  "allocation_weights_source_backed": false,
  "becoming_class_status": "reusable_class",
  "boundary_rung": "recurrence_or_continuation",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "source_backed_reflexively_self_maintaining_identity_candidate",
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
  "core_membership_derivation_kind": "experiment_local_design_policy_over_source_backed_support_nodes",
  "core_membership_policy_id": "n07_i7b_core_membership_design_policy_v1",
  "core_membership_source_backed": false,
  "derived_id_ceiling": "ID5",
  "experiment_local_observables_used": [
    "n07_i7b_source_backed_t6_reflexive_closure_event_0001",
    "n07_i7b_source_backed_t6_reflexive_closure_record_v1",
    "n07_i7b_proper_time_identity_persistence_evaluator_v1",
    "artifact_derived_state_rows",
    "artifact_derived_processed_packet_rows",
    "later_cycle_producer_record_consumes_updated_digest"
  ],
  "experiment_local_packet_application": true,
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
  "later_cycle_consumption_constructed_by_artifact_chain": true,
  "later_cycle_consumption_independently_observed": false,
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
  "packet_application_scope": "experiment_local_step_semantics_simulation",
  "primary_blocker": null,
  "probe_role": "diagnostic_probe",
  "proper_time_persistence_evaluator_digest": "2a88ae2d8ae01c12c27eb6ba514a06a9b87eef8667e1e9a852fefc2a38965753",
  "proper_time_persistence_evaluator_id": "n07_i7b_proper_time_identity_persistence_evaluator_v1",
  "rc_identity_collapse_claim_allowed": false,
  "row_id": "n07_i7b_id5_source_backed_t6_candidate_row_v1",
  "runtime_family": "LGRC9V3",
  "source_artifact_sha256": {
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json": "59b6a2dd5f0b88abe453997e74263ef4cf01ce629f975b0fb6f1712e98dde15e"
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
      "name": "n07_iteration_6b_topology_stress_source",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json",
      "sha256": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
      "status": "passed",
      "topology_stress_record_digest": "9c4ed80df8f1c0eadac9a5ab0f2034f2d792785213d21be29aa98fcc06b4b70c"
    },
    {
      "id5_candidate_row_digest": "1d9a5bca48662fbb927e66abfd3ee346a0adb512da5fbc0a9ae59f39417a6e2a",
      "name": "n07_iteration_7_reflexive_closure_design_probe",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json",
      "scope": "design_context_not_positive_t6_source",
      "sha256": "59b6a2dd5f0b88abe453997e74263ef4cf01ce629f975b0fb6f1712e98dde15e",
      "status": "passed"
    }
  ],
  "source_context_composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
  "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
  "source_id4_stress_candidate_row_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
  "source_id4_stress_candidate_row_id": "n07_i6b_id4_split_birth_invariance_stress_candidate_row_v1",
  "source_iteration_7_design_probe_digest": "1d9a5bca48662fbb927e66abfd3ee346a0adb512da5fbc0a9ae59f39417a6e2a",
  "source_reports": [
    {
      "name": "n07_iteration_6b_topology_stress_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md",
      "sha256": "5ef2dda323b44c4e6c2cd026773a90e0dbe2d41e8b7c28671e8dc372a8a1a8c8"
    },
    {
      "name": "n07_iteration_7_reflexive_closure_design_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_7_id5_reflexive_closure_persistence.md",
      "sha256": "a43304bbfafa5f7d5a1645f870716be3d1c93602c6f4916abe7a29a5c24d231b"
    }
  ],
  "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
  "support_area_id": "n07_support_area_A_v1",
  "support_dependency_status": "probe_dependent",
  "t4_deferral_rationale": "T4 is the recurrence/no-mutation baseline and must be run before interpreting topology-free recurrence as stronger than ID4.",
  "t4_no_mutation_baseline_deferred": true,
  "t6_evidence_native_support_status": "experiment_local_artifact_derived",
  "t6_record_digest": "f8852c2e90beae00489abd6ec2d93c2b5bba6a268826c6baeb61d8fad809f0f0",
  "t6_record_id": "n07_i7b_source_backed_t6_reflexive_closure_record_v1",
  "topology_family_id": "n07_T6_reflexive_closure",
  "unrestricted_identity_claim_allowed": false,
  "visual_is_evidence_source": false,
  "visual_reference": null,
  "withdrawal_test_status": "not_tested"
}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
| `no_reentry` | `blocked` | `no_reentry` | `ID4` |
| `closure_not_consumed_by_later_cycle` | `blocked` | `closure_not_consumed_by_later_cycle` | `ID4` |
| `hidden_support_field` | `blocked` | `hidden_support_field` | `ID4` |
| `improper_proper_time_threshold` | `blocked` | `improper_proper_time_threshold` | `ID4` |
| `failed_persistence` | `blocked` | `failed_persistence` | `ID4` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID4` |
| `unauthorized_identity_acceptance_event` | `blocked` | `unauthorized_identity_acceptance_event` | `ID4` |
| `producer_mutation_boundary_violation` | `blocked` | `producer_mutation_boundary_violation` | `ID4` |
| `agency_claim_promotion` | `blocked` | `agency_claim_promotion` | `ID4` |

## Checks

| Check | Passed |
|---|---:|
| `agency_and_identity_acceptance_blocked` | `True` |
| `allocation_policy_origin_recorded` | `True` |
| `birth_lineage_source_backed` | `True` |
| `budget_exact` | `True` |
| `c1_composite_selected` | `True` |
| `candidate_digest_source_links_present` | `True` |
| `claim_flag_keys_match_manifest` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_canonical` | `True` |
| `control_blockers_distinct` | `True` |
| `control_ceilings_id4` | `True` |
| `control_set_present` | `True` |
| `controls_blocked` | `True` |
| `core_membership_scope_recorded` | `True` |
| `derived_ceiling_id5_not_id6` | `True` |
| `gate_vector_valid` | `True` |
| `identity_acceptance_not_emitted` | `True` |
| `later_cycle_consumes_updated_digest` | `True` |
| `later_cycle_independence_limitation_recorded` | `True` |
| `measurements_derived_not_authored` | `True` |
| `native_support_not_overstated` | `True` |
| `no_src_changes_required` | `True` |
| `nonnegative_state_passed` | `True` |
| `packet_records_scope_precise` | `True` |
| `proper_time_persistence_passed` | `True` |
| `reentry_strengthens_basin_evidence` | `True` |
| `source_context_preserved` | `True` |
| `source_iteration_6b_passed` | `True` |
| `source_iteration_7_passed` | `True` |
| `source_iteration_7_routes_to_7b` | `True` |
| `state_rows_source_backed` | `True` |
| `status_passed` | `True` |
| `t4_deferral_limitation_recorded` | `True` |
| `t6_family_declared` | `True` |
| `t6_record_digest_recomputed` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "a456a32d333bd4be18280ee6a5eff590d1f2aaea7b05772e7d31f009df5eee4c",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "821a20660669e83b4ac6a8ae4a17f55a76abb0be9b0a8827b4d5daef6df3b9f9",
  "id5_candidate_row_digest": "88f284dd115bcabc77db0e5cea038f1c7c043abfbd720afcf94145839e2c0e56",
  "proper_time_persistence_evaluation_digest": "a8839b20c2bebff8baae6db5639bcd03ce6bb8822b6c446f83898c40276a050d",
  "source_backed_t6_chain_digest": "96cc04a82aeaed185ba540c1201911113b8af1c074bb24a79bc41fdffd0b381f",
  "source_backed_t6_record_digest": "7ac28f40a645fbb013d64816e4c88e6ee89f1124ac1cefcce9eacd40349e393d"
}
```

## Acceptance

Iteration 7-B passes because re-entry is represented by serialized packet and
state rows, basin evidence is computed from those rows, and the later
proper-time cycle consumes the updated basin evidence digest. The result
reaches ID5/T6 only; it does not support ID6, native LGRC identity support,
identity acceptance, RC identity collapse, agency, or personhood.
