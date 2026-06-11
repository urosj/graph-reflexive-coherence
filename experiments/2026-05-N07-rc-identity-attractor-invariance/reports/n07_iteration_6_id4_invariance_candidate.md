# N07 Iteration 6: ID4 Invariance Candidate

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_6_id4_invariance_candidate.py
```

Iteration 6 consumes the Iteration 5-B ID3 attractivity stress candidate and
adds repeated proper-time cycles, a manifest-declared mild perturbation, and a
lineage-current topology context. The support overlap and lineage-current
overlap remain above the manifest thresholds after transport through the
declared lineage map.

The native topology lineage and topology-state reabsorption context is used
only as runtime infrastructure evidence. N07 identity is not inherited from
N04, and native identity-invariance policy remains unavailable, so this is an
ID4 invariant-basin candidate rather than identity acceptance, agency, or
unrestricted identity.

## Topology Lineage Context

```json
{
  "context_id": "n07_i6_lineage_current_context_v1",
  "context_kind": "declared_lgrc3_topology_lineage_and_state_reabsorption_context",
  "identity_inherited_from_infrastructure": false,
  "lineage_current_status": "transported_topology_lineage",
  "lineage_map_complete": true,
  "lineage_transfer_map": {
    "complete": true,
    "edge_map": {
      "1": 101,
      "2": 102,
      "3": 103,
      "5": 105
    },
    "node_map": {
      "2": 20
    },
    "port_map": {
      "support_front": "transported_support_front",
      "support_rear": "transported_support_rear",
      "support_reentry": "transported_support_reentry"
    },
    "retired_edge_ids": [
      1,
      2,
      3,
      5
    ],
    "retired_node_ids": [
      2
    ],
    "scrambled": false,
    "target_edge_ids": [
      101,
      102,
      103,
      105
    ],
    "target_node_ids": [
      20
    ]
  },
  "lineage_transfer_map_digest": "b625d07691f57acbc9332c08e88ddf3b266777f368ed2a77b15600a9e175b85f",
  "source_support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "source_support_area_id": "n07_support_area_A_v1",
  "stale_source_support_row_current_after_topology": false,
  "support_lineage_current": true,
  "surface_lineage_record": {
    "identity_inherited_from_infrastructure": false,
    "lineage_action": "transported",
    "lineage_current": true,
    "lineage_transfer_map_digest": "b625d07691f57acbc9332c08e88ddf3b266777f368ed2a77b15600a9e175b85f",
    "record_id": "n07_i6_surface_lineage_transport_record_v1",
    "record_kind": "surface_lineage_transport_context_record",
    "source_surface_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "source_surface_nodes": [
      2
    ],
    "source_surface_ports": [
      "support_front",
      "support_rear",
      "support_reentry"
    ],
    "target_surface_nodes": [
      20
    ],
    "target_surface_ports": [
      "transported_support_front",
      "transported_support_rear",
      "transported_support_reentry"
    ],
    "topology_event_digest": "20263b4683c8419d46196e286e508e1f44c11d5f2957f4fe512d57dbc0571c81",
    "transported_surface_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac"
  },
  "surface_lineage_record_digest": "2da79ac517f7beadce9f1e859897d1a35d602426086788e2f047e2cec1ccef0a",
  "topology_event": {
    "event_kind": "committed_lgrc3_topology_lineage_context",
    "event_time_key": "n07_i6_t5_topology_event_0001",
    "lineage_transfer_map_digest": "b625d07691f57acbc9332c08e88ddf3b266777f368ed2a77b15600a9e175b85f",
    "retired_edge_ids": [
      1,
      2,
      3,
      5
    ],
    "retired_node_ids": [
      2
    ],
    "scheduler_event_index": 7,
    "source_edge_ids": [
      1,
      2,
      3,
      5
    ],
    "source_node_ids": [
      2
    ],
    "source_surface_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "target_edge_ids": [
      101,
      102,
      103,
      105
    ],
    "target_node_ids": [
      20
    ],
    "topology_event_committed": true,
    "topology_event_id": "n07_i6_topology_event_transport_support_A_0001",
    "topology_mutation_occurs": true
  },
  "topology_event_committed": true,
  "topology_event_digest": "20263b4683c8419d46196e286e508e1f44c11d5f2957f4fe512d57dbc0571c81",
  "topology_mutation_occurs": true,
  "topology_state_reabsorption_record": {
    "active_state_node_total_after": 6.0,
    "identity_inherited_from_infrastructure": false,
    "lineage_transfer_map_digest": "b625d07691f57acbc9332c08e88ddf3b266777f368ed2a77b15600a9e175b85f",
    "node_plus_packet_budget_after": 6.0,
    "node_plus_packet_budget_before": 6.0,
    "node_plus_packet_budget_error": 0.0,
    "nonnegative_state_passed": true,
    "packet_ledger_node_total_after": 6.0,
    "record_id": "n07_i6_topology_state_reabsorption_record_v1",
    "record_kind": "topology_state_reabsorption_context_record",
    "retired_node_state_before": {
      "2": 1.455
    },
    "source_active_state_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "source_edge_state_before": {
      "1": "active",
      "2": "active",
      "3": "active",
      "5": "active"
    },
    "source_node_state_before": {
      "2": 1.455
    },
    "target_active_state_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac",
    "target_edge_state_after": {
      "101": "transported",
      "102": "transported",
      "103": "transported",
      "105": "transported"
    },
    "target_node_state_after": {
      "20": 1.445
    },
    "topology_event_digest": "20263b4683c8419d46196e286e508e1f44c11d5f2957f4fe512d57dbc0571c81"
  },
  "topology_state_reabsorption_record_digest": "3274c1d68d26301df42e3f3343a1cb5b150dc78a61315a1e2539f2a9157d1c6b",
  "transported_support_area": {
    "candidate_identity_carrier_type": "coherence_basin",
    "identity_label_is_evidence": false,
    "lineage_map_digest": "b625d07691f57acbc9332c08e88ddf3b266777f368ed2a77b15600a9e175b85f",
    "lineage_status": "transported_topology_lineage",
    "source_support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "source_support_area_id": "n07_support_area_A_v1",
    "support_area_id": "n07_support_area_A_lineage_current_v1",
    "support_edge_ids": [
      101,
      102,
      103,
      105
    ],
    "support_node_ids": [
      20
    ],
    "support_port_ids": [
      "transported_support_front",
      "transported_support_rear",
      "transported_support_reentry"
    ]
  },
  "transported_support_area_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac"
}
```

## Invariance Cycle Event

```json
{
  "budget_error_max": 0.0,
  "budget_surface": "node_plus_packet",
  "candidate_basin_id": "n07_basin_A_candidate_v1",
  "candidate_identity_carrier_type": "coherence_basin",
  "cycles": [
    {
      "attractivity_gate": "pass",
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6_cycle_0",
      "event_time_key": "n07_i6_t5_cycle_0",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 1.0,
      "lineage_status": "fixed_topology",
      "literal_node_set_overlap_with_previous": null,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "perturbation_applied": false,
      "proper_time_index": 0,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 4,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.455,
      "support_area_mass_before": 1.455,
      "support_gate": "pass",
      "support_node_ids": [
        2
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 1.0,
      "topology_event_applied": false
    },
    {
      "attractivity_gate": "pass",
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6_cycle_1",
      "event_time_key": "n07_i6_t5_cycle_1",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.98,
      "lineage_status": "fixed_topology",
      "literal_node_set_overlap_with_previous": 1.0,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "perturbation_applied": true,
      "proper_time_index": 1,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 5,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.435,
      "support_area_mass_before": 1.455,
      "support_gate": "pass",
      "support_node_ids": [
        2
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.98,
      "topology_event_applied": false
    },
    {
      "attractivity_gate": "pass",
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6_cycle_2",
      "event_time_key": "n07_i6_t5_cycle_2",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.98,
      "lineage_status": "transported_topology_lineage",
      "literal_node_set_overlap_with_previous": 0.0,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "perturbation_applied": false,
      "proper_time_index": 2,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 8,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.445,
      "support_area_mass_before": 1.435,
      "support_gate": "pass",
      "support_node_ids": [
        20
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.97,
      "topology_event_applied": true
    },
    {
      "attractivity_gate": "pass",
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "cycle_id": "n07_i6_cycle_3",
      "event_time_key": "n07_i6_t5_cycle_3",
      "invariance_gate": "pass",
      "lineage_current": true,
      "lineage_current_overlap": 0.97,
      "lineage_status": "transported_topology_lineage",
      "literal_node_set_overlap_with_previous": 1.0,
      "min_active_node_coherence": 0.0,
      "nonnegative_state_passed": true,
      "perturbation_applied": false,
      "proper_time_index": 3,
      "report_side_only": false,
      "runtime_visible": true,
      "scheduler_event_index": 9,
      "source_backed": true,
      "stability_gate": "pass",
      "support_area_mass_after": 1.45,
      "support_area_mass_before": 1.445,
      "support_gate": "pass",
      "support_node_ids": [
        20
      ],
      "support_overlap_kind": "lineage_weighted",
      "support_overlap_with_previous": 0.96,
      "topology_event_applied": false
    }
  ],
  "cycles_digest": "351ff00f48b253bdf3f5e5ffa9ba940072912a2cd016252af37f9bd411e3324a",
  "event_id": "n07_i6_invariance_cycle_event_0001",
  "event_kind": "experiment_local_runtime_visible_invariance_windows_with_lineage_context",
  "event_time_key": "n07_i6_t5_invariance_cycle_event",
  "lineage_current_overlap_method": "fraction_of_lineage_mapped_support_nodes_retaining_current_support_membership",
  "lineage_current_overlap_passed": true,
  "lineage_current_overlap_threshold": 0.95,
  "lineage_current_passed": true,
  "lineage_current_required": true,
  "literal_node_set_overlap_serialized": true,
  "metric_id": "n07_invariance_support_overlap_lineage_v1",
  "min_lineage_current_overlap": 0.97,
  "min_support_overlap": 0.96,
  "nonnegative_state_passed": true,
  "overlap_computation_method": "lineage_weighted_jaccard_over_declared_lineage_transfer_map",
  "perturbation_applied": true,
  "perturbation_magnitude": 0.1,
  "perturbation_recovery_passed": true,
  "perturbation_window": "one_proper_time_window",
  "proper_time_only": true,
  "proper_time_persistence_threshold": 3,
  "proper_time_window_count": 4,
  "report_side_only": false,
  "runtime_visible": true,
  "scheduler_event_index": 4,
  "source_attractivity_stress_record_digest": "6c8026422a0ec495acb070812e9b5b60fb9405f6d0d7e8be9d7cbc390b872172",
  "source_backed": true,
  "source_id3_stress_candidate_row_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
  "source_id3_stress_candidate_row_id": "n07_i5b_id3_attractivity_stress_candidate_row_v1",
  "source_iteration_5b_output_path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json",
  "source_iteration_5b_output_sha256": "418334600c32cc2bda5ff4343ae08fcf6b49ee3cf248fca9249846d15f7da6f0",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_overlap_kind": "lineage_weighted",
  "support_overlap_passed": true,
  "support_overlap_threshold": 0.95,
  "surface_lineage_record_digest": "2da79ac517f7beadce9f1e859897d1a35d602426086788e2f047e2cec1ccef0a",
  "topology_event_digest": "20263b4683c8419d46196e286e508e1f44c11d5f2957f4fe512d57dbc0571c81",
  "topology_family_id": "n07_T5_lineage_current_invariance",
  "topology_mutation_occurs": true,
  "topology_state_reabsorption_record_digest": "3274c1d68d26301df42e3f3343a1cb5b150dc78a61315a1e2539f2a9157d1c6b",
  "transported_support_area_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac",
  "transported_support_area_id": "n07_support_area_A_lineage_current_v1"
}
```

## Invariance Record

```json
{
  "budget_error_max": 0.0,
  "budget_surface": "node_plus_packet",
  "invariance_gate": "pass",
  "invariance_record_digest": "e63900185c730d0073406796681dbc72bac70ee5983392fe0422d0cff73a6d48",
  "invariance_record_digest_input": {
    "cycles_digest": "351ff00f48b253bdf3f5e5ffa9ba940072912a2cd016252af37f9bd411e3324a",
    "lineage_current_overlap_threshold": 0.95,
    "lineage_transfer_map_digest": "b625d07691f57acbc9332c08e88ddf3b266777f368ed2a77b15600a9e175b85f",
    "metric_id": "n07_invariance_support_overlap_lineage_v1",
    "perturbation_magnitude": 0.1,
    "perturbation_window": "one_proper_time_window",
    "proper_time_persistence_threshold": 3,
    "source_attractivity_stress_record_digest": "6c8026422a0ec495acb070812e9b5b60fb9405f6d0d7e8be9d7cbc390b872172",
    "source_id3_stress_candidate_row_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
    "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "support_overlap_threshold": 0.95,
    "surface_lineage_record_digest": "2da79ac517f7beadce9f1e859897d1a35d602426086788e2f047e2cec1ccef0a",
    "topology_event_digest": "20263b4683c8419d46196e286e508e1f44c11d5f2957f4fe512d57dbc0571c81",
    "topology_state_reabsorption_record_digest": "3274c1d68d26301df42e3f3343a1cb5b150dc78a61315a1e2539f2a9157d1c6b",
    "transported_support_area_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac"
  },
  "invariance_record_idempotency_key": {
    "cycles_digest": "351ff00f48b253bdf3f5e5ffa9ba940072912a2cd016252af37f9bd411e3324a",
    "metric_id": "n07_invariance_support_overlap_lineage_v1",
    "source_id3_stress_candidate_row_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
    "topology_event_digest": "20263b4683c8419d46196e286e508e1f44c11d5f2957f4fe512d57dbc0571c81",
    "topology_state_reabsorption_record_digest": "3274c1d68d26301df42e3f3343a1cb5b150dc78a61315a1e2539f2a9157d1c6b"
  },
  "invariance_record_idempotency_key_digest": "e74e8ac7808bced1f952c8898aab2a632bf825116897e2450068dc5fb04a6dca",
  "lineage_current_overlap_method": "fraction_of_lineage_mapped_support_nodes_retaining_current_support_membership",
  "lineage_current_overlap_min": 0.97,
  "lineage_current_overlap_passed": true,
  "lineage_current_overlap_threshold": 0.95,
  "lineage_current_passed": true,
  "lineage_map_complete": true,
  "lineage_transfer_map_digest": "b625d07691f57acbc9332c08e88ddf3b266777f368ed2a77b15600a9e175b85f",
  "literal_node_set_overlap_serialized": true,
  "metric_id": "n07_invariance_support_overlap_lineage_v1",
  "native_policy_available": false,
  "native_policy_blocker": "native_identity_invariance_policy_missing",
  "nonnegative_state_passed": true,
  "overlap_computation_method": "lineage_weighted_jaccard_over_declared_lineage_transfer_map",
  "perturbation_magnitude": 0.1,
  "perturbation_recovery_passed": true,
  "perturbation_window": "one_proper_time_window",
  "proper_time_persistence_passed": true,
  "proper_time_persistence_threshold": 3,
  "proper_time_window_count": 4,
  "record_id": "n07_i6_invariance_record_v1",
  "record_kind": "experiment_local_lineage_current_invariance_record",
  "report_side_only": false,
  "runtime_visible": true,
  "source_attractivity_stress_record_digest": "6c8026422a0ec495acb070812e9b5b60fb9405f6d0d7e8be9d7cbc390b872172",
  "source_backed": true,
  "source_event_digest": "dada737ec0243b98d60821700f3ec5c319f7c455df34175624a468d906ae70f1",
  "source_event_id": "n07_i6_invariance_cycle_event_0001",
  "source_id3_stress_candidate_row_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_drift_max": 0.040000000000000036,
  "support_drift_within_threshold": true,
  "support_overlap_kind": "lineage_weighted",
  "support_overlap_min": 0.96,
  "support_overlap_passed": true,
  "support_overlap_threshold": 0.95,
  "surface_lineage_record_digest": "2da79ac517f7beadce9f1e859897d1a35d602426086788e2f047e2cec1ccef0a",
  "topology_event_committed": true,
  "topology_event_digest": "20263b4683c8419d46196e286e508e1f44c11d5f2957f4fe512d57dbc0571c81",
  "topology_lineage_context_digest": "7fb61fee01f595296c6958cc2ada97279b9bb002a2c1752519dbd6043a1e1427",
  "topology_state_reabsorption_record_digest": "3274c1d68d26301df42e3f3343a1cb5b150dc78a61315a1e2539f2a9157d1c6b",
  "topology_state_reabsorption_record_present": true,
  "transported_support_area_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac"
}
```

## Candidate Row

```json
{
  "activity_history_digest": "c74b7765ab5b8c7a81d8f78652c497b67fc33879ad82277322f2363a56887c13",
  "agency_claim_allowed": false,
  "becoming_class_status": "observation_tag",
  "boundary_rung": "recurrence_or_continuation",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "invariant_basin_candidate",
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
    "n07_i6_invariance_cycle_event_0001",
    "n07_i6_invariance_record_v1",
    "lineage_current_surface_digest"
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
  "invariance_record_digest": "e63900185c730d0073406796681dbc72bac70ee5983392fe0422d0cff73a6d48",
  "invariance_record_id": "n07_i6_invariance_record_v1",
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
  "row_id": "n07_i6_id4_invariance_candidate_row_v1",
  "runtime_family": "LGRC9V3",
  "source_artifact_sha256": {
    "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json": "a293e7efa74e92369d6fd59f0c73f25669ee385b224e0f3fb32d06a5204e8910",
    "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json": "65477fda0529097244fa7191df540721f8f148526619193007e639e7d4dc6714",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json": "418334600c32cc2bda5ff4343ae08fcf6b49ee3cf248fca9249846d15f7da6f0"
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
      "attractivity_stress_record_digest": "6c8026422a0ec495acb070812e9b5b60fb9405f6d0d7e8be9d7cbc390b872172",
      "id3_stress_candidate_row_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
      "name": "n07_iteration_5b_id3_attractivity_stress_candidate",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json",
      "sha256": "418334600c32cc2bda5ff4343ae08fcf6b49ee3cf248fca9249846d15f7da6f0",
      "status": "passed"
    },
    {
      "identity_inherited": false,
      "name": "n04_19e_topology_state_reabsorption_infrastructure_context",
      "path": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json",
      "sha256": "a293e7efa74e92369d6fd59f0c73f25669ee385b224e0f3fb32d06a5204e8910"
    },
    {
      "identity_inherited": false,
      "name": "n04_22b_route_arbitrated_topology_identity_boundary_context",
      "path": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json",
      "sha256": "65477fda0529097244fa7191df540721f8f148526619193007e639e7d4dc6714"
    }
  ],
  "source_attractivity_stress_record_digest": "6c8026422a0ec495acb070812e9b5b60fb9405f6d0d7e8be9d7cbc390b872172",
  "source_id3_stress_candidate_row_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
  "source_id3_stress_candidate_row_id": "n07_i5b_id3_attractivity_stress_candidate_row_v1",
  "source_reports": [
    {
      "name": "n07_iteration_5b_id3_attractivity_stress_candidate_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_5b_id3_attractivity_stress_candidate.md",
      "sha256": "df11920ef76e1aa7a71811378131123eb95e9f351b1e498e7045dbe187804fb7"
    },
    {
      "identity_inherited": false,
      "name": "n04_19e_topology_state_reabsorption_report_context",
      "path": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md",
      "sha256": "94585dbbd9dec56290647c14b3a8eb6b846db318329d151c7c659e5e78d369ff"
    },
    {
      "identity_inherited": false,
      "name": "n04_22b_identity_boundary_report_context",
      "path": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md",
      "sha256": "43a405c11ea9fa9984b11748bff76489fad206ff5ae1d8899a2c409e62e66ef9"
    }
  ],
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_dependency_status": "probe_dependent",
  "surface_lineage_record_digest": "2da79ac517f7beadce9f1e859897d1a35d602426086788e2f047e2cec1ccef0a",
  "topology_event_digest": "20263b4683c8419d46196e286e508e1f44c11d5f2957f4fe512d57dbc0571c81",
  "topology_family_id": "n07_T5_lineage_current_invariance",
  "topology_state_reabsorption_record_digest": "3274c1d68d26301df42e3f3343a1cb5b150dc78a61315a1e2539f2a9157d1c6b",
  "transported_support_area_digest": "776912eeb0fef347bb9ae062d264ef0b8ac2f570a46d87fb17a7dbf59e9ae6ac",
  "transported_support_area_id": "n07_support_area_A_lineage_current_v1",
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
| `missing_topology_state_reabsorption` | `blocked` | `missing_topology_state_reabsorption` | `ID3` |
| `lineage_map_scrambled` | `blocked` | `lineage_map_scrambled` | `ID3` |
| `support_drift_beyond_threshold` | `blocked` | `support_drift_beyond_threshold` | `ID3` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID3` |
| `identity_claim_promotion` | `blocked` | `identity_claim_promotion` | `ID3` |

## Checks

| Check | Passed |
|---|---:|
| `becoming_method_values_allowed` | `True` |
| `budget_exact` | `True` |
| `candidate_carrier_is_coherence_basin` | `True` |
| `candidate_gate_matches_manifest` | `True` |
| `candidate_target_id_matches_manifest` | `True` |
| `candidate_topology_family_matches_manifest` | `True` |
| `claim_ceiling_scoped` | `True` |
| `claim_flag_keys_match_manifest` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_distinct` | `True` |
| `control_ceilings_id3` | `True` |
| `controls_blocked` | `True` |
| `derived_ceiling_id4` | `True` |
| `evidence_only_surfaces_not_promoted` | `True` |
| `gate_vector_schema_matches_manifest` | `True` |
| `identity_acceptance_blocked` | `True` |
| `infrastructure_identity_not_inherited` | `True` |
| `invariance_record_digest_recomputed` | `True` |
| `lineage_current_overlap_threshold_passed` | `True` |
| `lineage_weighted_overlap_literal_overlap_disambiguated` | `True` |
| `metric_policy_matches_manifest` | `True` |
| `native_support_not_overstated` | `True` |
| `no_src_changes_required` | `True` |
| `nonnegative_state_passed` | `True` |
| `overlap_method_matches_manifest` | `True` |
| `perturbation_matches_manifest` | `True` |
| `perturbation_recovery_passed` | `True` |
| `proper_time_cycles_ordered` | `True` |
| `proper_time_persistence_passed` | `True` |
| `required_controls_present` | `True` |
| `same_lineage_map_used` | `True` |
| `source_gates_support_stability_attractivity_passed` | `True` |
| `source_iteration_5b_points_to_iteration_6` | `True` |
| `source_iteration_5b_status_passed` | `True` |
| `status_passed` | `True` |
| `support_lineage_current_after_topology` | `True` |
| `support_overlap_threshold_passed` | `True` |
| `topology_event_committed` | `True` |
| `topology_lineage_context_complete` | `True` |
| `topology_state_reabsorption_budget_matches_cycles` | `True` |
| `topology_state_reabsorption_present` | `True` |
| `transported_node_ids_do_not_collide_with_fixture` | `True` |
| `transported_support_digest_matches_context` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "d1cd83cbf6d45ef62751bb267c76e036c9c58d70d0e4d7a6c30e9901ec632ca2",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "30400e77b2396f4fe19e3a9a0ea3b8f1c65124bed1e84884800eaca8b41abf64",
  "id4_candidate_row_digest": "f88dd0e1385dbdbea8f6411782e39becce26b0fe3fe1302855fda11261f64710",
  "invariance_cycle_event_digest": "dada737ec0243b98d60821700f3ec5c319f7c455df34175624a468d906ae70f1",
  "invariance_record_digest": "67c346f1558b74ed19baa15947c053561db8ab665ecbcc1a6c5f1e6b353ed85e",
  "source_iteration_5b_output_digest": "825953b50a4ec8e2b267e8f507e085959585cc0a41ad8a376d29e78f8af3b109",
  "topology_lineage_context_digest": "7fb61fee01f595296c6958cc2ada97279b9bb002a2c1752519dbd6043a1e1427"
}
```

## Acceptance

Iteration 6 passes because the candidate coherence basin remains
lineage-current and identity-continuous across repeated cycles, the declared
mild perturbation, and topology-lineage context. It promotes the evidence
classification only to ID4 invariant-basin candidate; it does not support ID5,
identity acceptance, RC identity collapse, semantic choice, agency, or native
identity support.
