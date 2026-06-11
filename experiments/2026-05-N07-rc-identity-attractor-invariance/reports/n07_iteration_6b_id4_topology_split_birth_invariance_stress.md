# N07 Iteration 6-B: ID4 Split/Birth Topology Stress

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_6b_id4_topology_split_birth_invariance_stress.py
```

Iteration 6-B consumes the minimum Iteration 6 ID4 candidate and stresses the
same identity ceiling across a longer lineage-proper-time sequence. The stress
sequence includes a committed support split and a lineage-authorized support
birth, then continues through post-birth cycles while preserving support
overlap, lineage-current overlap, exact node-plus-packet budget, and
nonnegative state.

The birth event is a topology-lineage event only. It does not emit identity
acceptance, RC identity collapse, agency, reproduction, or native LGRC identity
support. Native identity-invariance policy remains unavailable.

## Topology Stress Sequence

```json
{
  "all_lineage_maps_complete": true,
  "all_state_reabsorption_records_present": true,
  "all_topology_events_committed": true,
  "birth_event_present": true,
  "birth_is_identity_acceptance": false,
  "birth_support_area": {
    "birth_is_identity_acceptance": false,
    "born_node_ids": [
      32
    ],
    "born_node_parent_map": {
      "32": 30
    },
    "candidate_identity_carrier_type": "coherence_basin",
    "identity_label_is_evidence": false,
    "lineage_action": "birth",
    "source_support_area_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
    "support_area_id": "n07_support_area_A_split_birth_lineage_current_v1",
    "support_node_ids": [
      30,
      31,
      32
    ]
  },
  "birth_support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
  "identity_inherited_from_infrastructure": false,
  "sequence_id": "n07_i6b_topology_split_birth_sequence_v1",
  "sequence_kind": "lineage_current_split_and_birth_topology_stress",
  "source_minimum_id4_candidate_row_digest": "f88dd0e1385dbdbea8f6411782e39becce26b0fe3fe1302855fda11261f64710",
  "source_support_area_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac",
  "split_event_present": true,
  "split_support_area": {
    "candidate_identity_carrier_type": "coherence_basin",
    "identity_label_is_evidence": false,
    "lineage_action": "split",
    "source_support_area_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac",
    "support_area_id": "n07_support_area_A_split_lineage_current_v1",
    "support_node_ids": [
      30,
      31
    ]
  },
  "split_support_area_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
  "topology_event_count": 2,
  "topology_events": [
    {
      "lineage_map": {
        "action": "split",
        "born_node_ids": [],
        "born_node_parent_map": {},
        "complete": true,
        "node_map": {
          "20": [
            30,
            31
          ]
        },
        "retired_node_ids": [
          20
        ],
        "scrambled": false,
        "source_support_nodes": [
          20
        ],
        "target_support_nodes": [
          30,
          31
        ]
      },
      "lineage_transfer_map_digest": "5265b071b0bac39ca322d69744d8e4e706c9f91778f24c7ae77975ad750a9cfe",
      "surface_lineage_record": {
        "born_node_ids": [],
        "identity_inherited_from_infrastructure": false,
        "lineage_action": "split",
        "lineage_current": true,
        "lineage_transfer_map_digest": "5265b071b0bac39ca322d69744d8e4e706c9f91778f24c7ae77975ad750a9cfe",
        "record_id": "n07_i6b_topology_split_support_A_0001_surface_lineage_record",
        "record_kind": "surface_lineage_transport_context_record",
        "retired_node_ids": [
          20
        ],
        "source_support_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac",
        "source_surface_nodes": [
          20
        ],
        "target_surface_nodes": [
          30,
          31
        ],
        "topology_event_digest": "287d8794e73e74b8975b54286d6b9a5dc0f2bbd91437209d08884df8ea852736",
        "transported_support_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8"
      },
      "surface_lineage_record_digest": "507e8c4f0888ab8da7608f0d7a0ae37012e2b55642e7afed322e351b3adf940d",
      "topology_event": {
        "birth_is_identity_acceptance": false,
        "born_node_ids": [],
        "event_kind": "committed_lgrc3_topology_split",
        "event_time_key": "n07_i6b_topology_split_support_A_0001_proper_time",
        "identity_inherited_from_topology": false,
        "lineage_transfer_map_digest": "5265b071b0bac39ca322d69744d8e4e706c9f91778f24c7ae77975ad750a9cfe",
        "retired_node_ids": [
          20
        ],
        "scheduler_event_index": 12,
        "source_support_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac",
        "source_support_nodes": [
          20
        ],
        "target_support_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
        "target_support_nodes": [
          30,
          31
        ],
        "topology_action": "split",
        "topology_event_committed": true,
        "topology_event_id": "n07_i6b_topology_split_support_A_0001",
        "topology_mutation_occurs": true
      },
      "topology_event_digest": "287d8794e73e74b8975b54286d6b9a5dc0f2bbd91437209d08884df8ea852736",
      "topology_state_reabsorption_record": {
        "active_state_node_total_after": 6.0,
        "born_node_ids": [],
        "identity_inherited_from_infrastructure": false,
        "lineage_transfer_map_digest": "5265b071b0bac39ca322d69744d8e4e706c9f91778f24c7ae77975ad750a9cfe",
        "node_plus_packet_budget_after": 6.0,
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_error": 0.0,
        "nonnegative_state_passed": true,
        "packet_ledger_node_total_after": 6.0,
        "record_id": "n07_i6b_topology_split_support_A_0001_topology_state_reabsorption_record",
        "record_kind": "topology_state_reabsorption_context_record",
        "retired_node_ids": [
          20
        ],
        "source_active_state_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac",
        "source_support_nodes": [
          20
        ],
        "target_active_state_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
        "target_support_nodes": [
          30,
          31
        ],
        "topology_event_digest": "287d8794e73e74b8975b54286d6b9a5dc0f2bbd91437209d08884df8ea852736"
      },
      "topology_state_reabsorption_record_digest": "408d892fdbf624c9c99b7849de6caedaf7b6bda9797545becda95e08fd24b6e4"
    },
    {
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
      "surface_lineage_record": {
        "born_node_ids": [
          32
        ],
        "identity_inherited_from_infrastructure": false,
        "lineage_action": "birth",
        "lineage_current": true,
        "lineage_transfer_map_digest": "70037da10c07fc329def298c94aaf75f5d48e6071d69cd85fc9f938fef5a84a1",
        "record_id": "n07_i6b_topology_birth_support_A_0002_surface_lineage_record",
        "record_kind": "surface_lineage_transport_context_record",
        "retired_node_ids": [],
        "source_support_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
        "source_surface_nodes": [
          30,
          31
        ],
        "target_surface_nodes": [
          30,
          31,
          32
        ],
        "topology_event_digest": "d0b636dfa696a17d75740803074dd2c11b46dcf585450f11ac1de66c0b5888ca",
        "transported_support_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075"
      },
      "surface_lineage_record_digest": "9ca3eabfdaa9611fc127fe602c260cb576730ed0a84fbef3d8a2cffa53f446b9",
      "topology_event": {
        "birth_is_identity_acceptance": false,
        "born_node_ids": [
          32
        ],
        "event_kind": "committed_lgrc3_topology_birth",
        "event_time_key": "n07_i6b_topology_birth_support_A_0002_proper_time",
        "identity_inherited_from_topology": false,
        "lineage_transfer_map_digest": "70037da10c07fc329def298c94aaf75f5d48e6071d69cd85fc9f938fef5a84a1",
        "retired_node_ids": [],
        "scheduler_event_index": 15,
        "source_support_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
        "source_support_nodes": [
          30,
          31
        ],
        "target_support_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
        "target_support_nodes": [
          30,
          31,
          32
        ],
        "topology_action": "birth",
        "topology_event_committed": true,
        "topology_event_id": "n07_i6b_topology_birth_support_A_0002",
        "topology_mutation_occurs": true
      },
      "topology_event_digest": "d0b636dfa696a17d75740803074dd2c11b46dcf585450f11ac1de66c0b5888ca",
      "topology_state_reabsorption_record": {
        "active_state_node_total_after": 6.0,
        "born_node_ids": [
          32
        ],
        "identity_inherited_from_infrastructure": false,
        "lineage_transfer_map_digest": "70037da10c07fc329def298c94aaf75f5d48e6071d69cd85fc9f938fef5a84a1",
        "node_plus_packet_budget_after": 6.0,
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_error": 0.0,
        "nonnegative_state_passed": true,
        "packet_ledger_node_total_after": 6.0,
        "record_id": "n07_i6b_topology_birth_support_A_0002_topology_state_reabsorption_record",
        "record_kind": "topology_state_reabsorption_context_record",
        "retired_node_ids": [],
        "source_active_state_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
        "source_support_nodes": [
          30,
          31
        ],
        "target_active_state_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
        "target_support_nodes": [
          30,
          31,
          32
        ],
        "topology_event_digest": "d0b636dfa696a17d75740803074dd2c11b46dcf585450f11ac1de66c0b5888ca"
      },
      "topology_state_reabsorption_record_digest": "e5bc4a6f79e5a33ef9c4710c4863dee20ee00574c8f3f88a91e9d326d77e759d"
    }
  ]
}
```

## Stress Event

```json
{
  "birth_event_present": true,
  "birth_is_identity_acceptance": false,
  "budget_error_max": 0.0,
  "budget_surface": "node_plus_packet",
  "cycles": [
    {
      "attractivity_gate": "pass",
      "birth_is_identity_acceptance": false,
      "born_node_ids": [],
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6b_cycle_0",
      "event_time_key": "n07_i6b_t5_cycle_0",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 1.0,
      "literal_node_set_overlap_with_previous": null,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "proper_time_index": 0,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 10,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.45,
      "support_area_mass_before": 1.45,
      "support_gate": "pass",
      "support_node_ids": [
        20
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 1.0,
      "topology_action": null
    },
    {
      "attractivity_gate": "pass",
      "birth_is_identity_acceptance": false,
      "born_node_ids": [],
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6b_cycle_1",
      "event_time_key": "n07_i6b_t5_cycle_1",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.985,
      "literal_node_set_overlap_with_previous": 1.0,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "proper_time_index": 1,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 11,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.44,
      "support_area_mass_before": 1.45,
      "support_gate": "pass",
      "support_node_ids": [
        20
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.985,
      "topology_action": null
    },
    {
      "attractivity_gate": "pass",
      "birth_is_identity_acceptance": false,
      "born_node_ids": [],
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6b_cycle_2",
      "event_time_key": "n07_i6b_t5_cycle_2",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.975,
      "literal_node_set_overlap_with_previous": 0.0,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "proper_time_index": 2,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 13,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.438,
      "support_area_mass_before": 1.44,
      "support_gate": "pass",
      "support_node_ids": [
        30,
        31
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.97,
      "topology_action": "split"
    },
    {
      "attractivity_gate": "pass",
      "birth_is_identity_acceptance": false,
      "born_node_ids": [],
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6b_cycle_3",
      "event_time_key": "n07_i6b_t5_cycle_3",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.97,
      "literal_node_set_overlap_with_previous": 1.0,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "proper_time_index": 3,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 14,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.442,
      "support_area_mass_before": 1.438,
      "support_gate": "pass",
      "support_node_ids": [
        30,
        31
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.965,
      "topology_action": null
    },
    {
      "attractivity_gate": "pass",
      "birth_is_identity_acceptance": false,
      "born_node_ids": [
        32
      ],
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6b_cycle_4",
      "event_time_key": "n07_i6b_t5_cycle_4",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.96,
      "literal_node_set_overlap_with_previous": 0.6666666666666666,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "proper_time_index": 4,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 16,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.44,
      "support_area_mass_before": 1.442,
      "support_gate": "pass",
      "support_node_ids": [
        30,
        31,
        32
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.955,
      "topology_action": "birth"
    },
    {
      "attractivity_gate": "pass",
      "birth_is_identity_acceptance": false,
      "born_node_ids": [
        32
      ],
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6b_cycle_5",
      "event_time_key": "n07_i6b_t5_cycle_5",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.962,
      "literal_node_set_overlap_with_previous": 1.0,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "proper_time_index": 5,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 17,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.446,
      "support_area_mass_before": 1.44,
      "support_gate": "pass",
      "support_node_ids": [
        30,
        31,
        32
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.96,
      "topology_action": null
    },
    {
      "attractivity_gate": "pass",
      "birth_is_identity_acceptance": false,
      "born_node_ids": [
        32
      ],
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6b_cycle_6",
      "event_time_key": "n07_i6b_t5_cycle_6",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.961,
      "literal_node_set_overlap_with_previous": 1.0,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "proper_time_index": 6,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 18,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.448,
      "support_area_mass_before": 1.446,
      "support_gate": "pass",
      "support_node_ids": [
        30,
        31,
        32
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.958,
      "topology_action": null
    }
  ],
  "cycles_digest": "db63479d3d636c3038e30c5ff6d59c3021b1a599b81dc64c15141d943f0c7893",
  "event_id": "n07_i6b_split_birth_invariance_stress_event_0001",
  "event_kind": "experiment_local_lineage_current_split_birth_invariance_stress",
  "event_time_key": "n07_i6b_t5_split_birth_stress",
  "lineage_current_overlap_method": "fraction_of_lineage_mapped_support_nodes_retaining_current_support_membership",
  "lineage_current_overlap_passed": true,
  "lineage_current_overlap_threshold": 0.95,
  "literal_node_set_overlap_serialized": true,
  "metric_id": "n07_invariance_support_overlap_lineage_v1",
  "min_lineage_current_overlap": 0.96,
  "min_support_overlap": 0.955,
  "nonnegative_state_passed": true,
  "overlap_computation_method": "lineage_weighted_jaccard_over_declared_lineage_transfer_map",
  "proper_time_persistence_threshold": 3,
  "proper_time_window_count": 7,
  "report_side_only": false,
  "runtime_visible": true,
  "scheduler_event_index": 10,
  "source_backed": true,
  "source_id4_candidate_row_digest": "f88dd0e1385dbdbea8f6411782e39becce26b0fe3fe1302855fda11261f64710",
  "source_invariance_record_digest": "67c346f1558b74ed19baa15947c053561db8ab665ecbcc1a6c5f1e6b353ed85e",
  "source_iteration_6_output_path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json",
  "source_iteration_6_output_sha256": "7134db432a859e9e94e191c525ba92f5f84e94e787246bc11b668f9343f92fcc",
  "split_event_present": true,
  "support_overlap_kind": "lineage_weighted",
  "support_overlap_passed": true,
  "support_overlap_threshold": 0.95,
  "topology_event_count": 2,
  "topology_sequence_digest": "8bef72a6dfb3a82e47053b7c8a06b06dde9909813f75ce2ba17abb10273b3781",
  "topology_sequence_length_above_minimum": true
}
```

## Stress Record

```json
{
  "all_lineage_maps_complete": true,
  "all_state_reabsorption_records_present": true,
  "all_topology_events_committed": true,
  "birth_event_present": true,
  "birth_is_identity_acceptance": false,
  "budget_error_max": 0.0,
  "budget_surface": "node_plus_packet",
  "identity_inherited_from_infrastructure": false,
  "invariance_gate": "pass",
  "lineage_current_overlap_method": "fraction_of_lineage_mapped_support_nodes_retaining_current_support_membership",
  "lineage_current_overlap_min": 0.96,
  "lineage_current_overlap_passed": true,
  "lineage_current_overlap_threshold": 0.95,
  "literal_node_set_overlap_serialized": true,
  "metric_id": "n07_invariance_support_overlap_lineage_v1",
  "native_policy_available": false,
  "native_policy_blocker": "native_identity_invariance_policy_missing",
  "nonnegative_state_passed": true,
  "overlap_computation_method": "lineage_weighted_jaccard_over_declared_lineage_transfer_map",
  "proper_time_sequence_extended_beyond_minimum": true,
  "proper_time_window_count": 7,
  "record_id": "n07_i6b_split_birth_invariance_stress_record_v1",
  "record_kind": "experiment_local_split_birth_invariance_stress_record",
  "report_side_only": false,
  "runtime_visible": true,
  "source_backed": true,
  "source_event_digest": "cbfa440ba79687d2afa7649d538ceddc1152f273d5f2bd432e31fa9f35743574",
  "source_event_id": "n07_i6b_split_birth_invariance_stress_event_0001",
  "source_id4_candidate_row_digest": "f88dd0e1385dbdbea8f6411782e39becce26b0fe3fe1302855fda11261f64710",
  "source_invariance_record_digest": "67c346f1558b74ed19baa15947c053561db8ab665ecbcc1a6c5f1e6b353ed85e",
  "split_event_present": true,
  "stress_record_digest": "5d2d4c1aba4a2eba4eb3e967bdbc6e800f15ed193c07f6ee826ca595647a8866",
  "stress_record_digest_input": {
    "birth_support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "cycles_digest": "db63479d3d636c3038e30c5ff6d59c3021b1a599b81dc64c15141d943f0c7893",
    "lineage_current_overlap_threshold": 0.95,
    "metric_id": "n07_invariance_support_overlap_lineage_v1",
    "source_id4_candidate_row_digest": "f88dd0e1385dbdbea8f6411782e39becce26b0fe3fe1302855fda11261f64710",
    "source_invariance_record_digest": "67c346f1558b74ed19baa15947c053561db8ab665ecbcc1a6c5f1e6b353ed85e",
    "support_overlap_threshold": 0.95,
    "topology_event_count": 2,
    "topology_sequence_digest": "8bef72a6dfb3a82e47053b7c8a06b06dde9909813f75ce2ba17abb10273b3781"
  },
  "stress_record_idempotency_key": {
    "cycles_digest": "db63479d3d636c3038e30c5ff6d59c3021b1a599b81dc64c15141d943f0c7893",
    "metric_id": "n07_invariance_support_overlap_lineage_v1",
    "source_id4_candidate_row_digest": "f88dd0e1385dbdbea8f6411782e39becce26b0fe3fe1302855fda11261f64710",
    "topology_sequence_digest": "8bef72a6dfb3a82e47053b7c8a06b06dde9909813f75ce2ba17abb10273b3781"
  },
  "stress_record_idempotency_key_digest": "58b7a4922ba9c4cb049748f02029a38e0b1b8deefc1e26dd21986c7c03736f23",
  "support_overlap_kind": "lineage_weighted",
  "support_overlap_min": 0.955,
  "support_overlap_passed": true,
  "support_overlap_threshold": 0.95,
  "topology_event_count": 2,
  "topology_sequence_digest": "8bef72a6dfb3a82e47053b7c8a06b06dde9909813f75ce2ba17abb10273b3781"
}
```

## Candidate Row

```json
{
  "activity_history_digest": "972f9e618574731dd49fa4338c9ed02dda9fcdef21ff83d025572f81729f12dd",
  "agency_claim_allowed": false,
  "becoming_class_status": "observation_tag",
  "birth_is_identity_acceptance_claim": false,
  "birth_support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
  "boundary_rung": "recurrence_or_continuation",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "invariant_basin_candidate_topology_stress_validated",
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
  "composite_topology_id": null,
  "derived_id_ceiling": "ID4",
  "experiment_local_observables_used": [
    "n07_i6b_split_birth_invariance_stress_event_0001",
    "n07_i6b_split_birth_invariance_stress_record_v1",
    "lineage_current_split_surface_digest",
    "lineage_authorized_birth_surface_digest"
  ],
  "gate_vector": {
    "artifact_replay": "not_measured",
    "attractivity": "pass",
    "compatibility": "not_measured",
    "invariance": "pass",
    "lineage_current": "pass",
    "reflexive_closure": "not_measured",
    "stability": "pass",
    "support": "pass"
  },
  "id4_is_not_id5": true,
  "id_level": "ID4",
  "identity_acceptance_claim_allowed": false,
  "identity_carrier_surface": "runtime_coherence_basin",
  "identity_inherited_from_infrastructure": false,
  "implementation_surface": "experiment_local_identity_gate_record",
  "invariance_is_identity_acceptance_claim": false,
  "native_observables_used": [
    "surface_lineage_transport_context",
    "topology_state_reabsorption_context",
    "node_plus_packet_budget_accounting"
  ],
  "native_policy_blockers": [
    "native_identity_invariance_policy_missing"
  ],
  "native_support_status": "mixed_native_experiment_local",
  "naturalization_rung": "Nat0_probe_dependent_expression",
  "primary_blocker": null,
  "probe_role": "diagnostic_probe",
  "row_id": "n07_i6b_id4_split_birth_invariance_stress_candidate_row_v1",
  "runtime_family": "LGRC9V3",
  "source_artifact_sha256": {
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json": "7134db432a859e9e94e191c525ba92f5f84e94e787246bc11b668f9343f92fcc"
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
      "id4_candidate_row_digest": "f88dd0e1385dbdbea8f6411782e39becce26b0fe3fe1302855fda11261f64710",
      "invariance_record_digest": "67c346f1558b74ed19baa15947c053561db8ab665ecbcc1a6c5f1e6b353ed85e",
      "name": "n07_iteration_6_id4_invariance_candidate",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json",
      "sha256": "7134db432a859e9e94e191c525ba92f5f84e94e787246bc11b668f9343f92fcc",
      "status": "passed"
    }
  ],
  "source_id4_candidate_row_digest": "f88dd0e1385dbdbea8f6411782e39becce26b0fe3fe1302855fda11261f64710",
  "source_id4_candidate_row_id": "n07_i6_id4_invariance_candidate_row_v1",
  "source_invariance_record_digest": "67c346f1558b74ed19baa15947c053561db8ab665ecbcc1a6c5f1e6b353ed85e",
  "source_reports": [
    {
      "name": "n07_iteration_6_id4_invariance_candidate_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_6_id4_invariance_candidate.md",
      "sha256": "ce74a24f9bac7f3c05a98063ecb9864f26716779de04442bc355548d412f9ea0"
    }
  ],
  "split_support_area_digest": "d01153c4736b64002f758f704ea1e29f5998c755c3714d0213ebfd7a5e86b4b8",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_dependency_status": "probe_dependent",
  "topology_family_id": "n07_T5_lineage_current_invariance",
  "topology_stress_record_digest": "5d2d4c1aba4a2eba4eb3e967bdbc6e800f15ed193c07f6ee826ca595647a8866",
  "topology_stress_record_id": "n07_i6b_split_birth_invariance_stress_record_v1",
  "unrestricted_identity_claim_allowed": false,
  "visual_is_evidence_source": false,
  "visual_reference": null,
  "withdrawal_test_status": "not_tested"
}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
| `stale_node_id_replay` | `blocked` | `stale_node_id_replay` | `ID3` |
| `lineage_map_scrambled` | `blocked` | `lineage_map_scrambled` | `ID3` |
| `missing_topology_state_reabsorption` | `blocked` | `missing_topology_state_reabsorption` | `ID3` |
| `ambiguous_overlap` | `blocked` | `ambiguous_overlap` | `ID3` |
| `support_drift_beyond_threshold` | `blocked` | `support_drift_beyond_threshold` | `ID3` |
| `direct_state_or_topology_rewrite` | `blocked` | `direct_state_or_topology_rewrite` | `ID3` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID3` |
| `identity_claim_promotion` | `blocked` | `identity_claim_promotion` | `ID3` |

## Checks

| Check | Passed |
|---|---:|
| `all_topology_events_committed` | `True` |
| `becoming_method_values_allowed` | `True` |
| `birth_event_present` | `True` |
| `birth_not_identity_acceptance` | `True` |
| `budget_exact` | `True` |
| `candidate_carrier_is_coherence_basin` | `True` |
| `candidate_gate_matches_manifest` | `True` |
| `candidate_target_id_matches_manifest` | `True` |
| `candidate_topology_family_matches_manifest` | `True` |
| `claim_ceiling_scoped` | `True` |
| `claim_flag_keys_match_manifest` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_canonical` | `True` |
| `control_blockers_distinct` | `True` |
| `control_ceilings_id3` | `True` |
| `controls_blocked` | `True` |
| `derived_ceiling_id4` | `True` |
| `evidence_only_surfaces_not_promoted` | `True` |
| `gate_vector_schema_matches_manifest` | `True` |
| `identity_acceptance_blocked` | `True` |
| `infrastructure_identity_not_inherited` | `True` |
| `lineage_current_overlap_threshold_passed` | `True` |
| `lineage_maps_complete` | `True` |
| `lineage_weighted_overlap_literal_overlap_disambiguated` | `True` |
| `metric_policy_matches_manifest` | `True` |
| `native_support_not_overstated` | `True` |
| `no_src_changes_required` | `True` |
| `nonnegative_state_passed` | `True` |
| `overlap_method_matches_manifest` | `True` |
| `post_birth_cycles_present` | `True` |
| `post_birth_support_includes_born_nodes` | `True` |
| `proper_time_cycles_ordered` | `True` |
| `proper_time_sequence_extended` | `True` |
| `required_controls_present` | `True` |
| `source_id4_minimum_candidate_passed` | `True` |
| `source_iteration_6_points_to_6b` | `True` |
| `source_iteration_6_status_passed` | `True` |
| `split_birth_node_id_disjointness` | `True` |
| `split_event_present` | `True` |
| `state_reabsorption_present` | `True` |
| `status_passed` | `True` |
| `stress_record_digest_recomputed` | `True` |
| `support_overlap_threshold_passed` | `True` |
| `topology_event_count_passed` | `True` |
| `topology_state_reabsorption_budget_matches_cycles` | `True` |
| `transported_node_ids_do_not_collide_with_fixture` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "86c6f667991daf3e2aef1e3fb0949da371f9fa83b760e8dd9fb7a1ccf187e326",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "810cef61a746eda973131eba329ab4c8c7c0c901e795d50f3af9b203cf826073",
  "id4_stress_candidate_row_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
  "source_iteration_6_output_digest": "dabf677ba72103e37eec6657a9eb11b7ea67f7b8bdc2284975f598037477bff3",
  "topology_stress_event_digest": "cbfa440ba79687d2afa7649d538ceddc1152f273d5f2bd432e31fa9f35743574",
  "topology_stress_record_digest": "9c4ed80df8f1c0eadac9a5ab0f2034f2d792785213d21be29aa98fcc06b4b70c",
  "topology_stress_sequence_digest": "8bef72a6dfb3a82e47053b7c8a06b06dde9909813f75ce2ba17abb10273b3781"
}
```

## Acceptance

Iteration 6-B passes because the candidate coherence basin remains
lineage-current and support-continuous across a split, a lineage-authorized
birth, and post-birth cycles. It strengthens the ID4 invariant-basin candidate
but does not promote to ID5, identity acceptance, agency, RC identity collapse,
or native identity support.
