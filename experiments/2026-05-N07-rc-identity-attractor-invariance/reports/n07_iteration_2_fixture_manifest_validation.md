# N07 Iteration 2: Fixture Manifest And Discrete RC Observable Mapping

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/validate_n07_fixture_manifest.py
```

Manifest: `experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json`

Manifest SHA-256: `e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603`

No identity probes were run. No support rows or ID evidence rows were emitted.

## Topology Families

| Family | Target | Gate | Expected ceiling | Negative blocker |
|---|---|---|---|---|
| `n07_T1_support_area_minimal` | `ID1` | `support` | `ID1` | `missing_support_area` |
| `n07_T2_stable_well_basin` | `ID2` | `stability` | `ID2` | `unstable_basin_no_local_well` |
| `n07_T3_attractor_neighborhood` | `ID3` | `attractivity` | `ID3` | `non_attractive_flux` |
| `n07_T5_lineage_current_invariance` | `ID4` | `lineage_current` | `ID4` | `stale_node_id_replay` |
| `n07_T6_reflexive_closure` | `ID5` | `reflexive_closure` | `ID5` | `no_reentry` |

T4 no-mutation invariance is explicitly deferred as a recurrence baseline, not
omitted from the topology ladder.

## Support Area

```json
{
  "authored_central_node_is_identity_evidence": false,
  "budget_after": 6.0,
  "budget_before": 6.0,
  "budget_error": 0.0,
  "budget_surface": "node_plus_packet",
  "candidate_identity_carrier_type": "coherence_basin",
  "duplicate_support_row_primary_blocker": "duplicate_support_row",
  "event_time_key": "manifest_declared_no_runtime_event",
  "idempotency_key_fields": [
    "support_area_id",
    "support_area_digest",
    "event_time_key",
    "scheduler_event_index",
    "lineage_status"
  ],
  "identity_label_is_evidence": false,
  "lineage_map_digest": null,
  "lineage_status": "fixed_topology",
  "scheduler_event_index": null,
  "support_area_digest": "0942731278e985c654cb39323ee9ac78550e293d6183c927b386de93ac02c887",
  "support_area_id": "n07_support_area_A_v1",
  "support_edge_ids": [
    1,
    2,
    3,
    5
  ],
  "support_node_ids": [
    2
  ],
  "support_port_ids": [
    "support_front",
    "support_rear",
    "support_reentry"
  ],
  "support_surface_digest": "manifest_symbolic_support_surface_digest_pending_iteration_3"
}
```

## Metric Definitions

```json
{
  "coherence_compatibility": {
    "compatibility_controls_deferred_until": "T7_or_C3",
    "conditions": [
      "budget_error == 0",
      "min_active_node_coherence >= 0",
      "candidate_support_overlap_with_competitor <= declared_overlap_threshold",
      "lineage_conflict_detected = false",
      "hidden_support_source_detected = false",
      "destructive_interference_score <= declared_interference_threshold"
    ],
    "metric_id": "n07_coherence_compatibility_v1"
  },
  "flux_convergence": {
    "controls": [
      "non_attractive_flux",
      "wrong_polarity",
      "subthreshold_flux",
      "wrong_basin"
    ],
    "formula": "net_flux_into_support_from_U > net_flux_out_of_support",
    "metric_id": "n07_flux_convergence_to_support_v1",
    "native_policy_available": false,
    "native_policy_blocker": "native_attractor_neighborhood_policy_missing",
    "positive_threshold": 0.0,
    "runtime_visible_inputs": [
      "neighborhood_U",
      "packet_work_events",
      "surface_rows",
      "budget_surface"
    ]
  },
  "invariance": {
    "controls": [
      "stale_node_id_replay",
      "missing_topology_state_reabsorption",
      "lineage_map_scrambled",
      "support_drift_beyond_threshold",
      "budget_discontinuity",
      "identity_claim_promotion"
    ],
    "destructive_perturbation_blocker": "support_drift_beyond_threshold",
    "lineage_current_overlap_method": "fraction_of_lineage_mapped_support_nodes_retaining_current_support_membership",
    "lineage_current_overlap_threshold": 0.95,
    "literal_node_set_overlap_serialized": true,
    "metric_id": "n07_invariance_support_overlap_lineage_v1",
    "missing_threshold_blocker": "identity_threshold_missing",
    "native_policy_available": false,
    "native_policy_blocker": "native_identity_invariance_policy_missing",
    "overlap_computation_method": "lineage_weighted_jaccard_over_declared_lineage_transfer_map",
    "perturbation_magnitude": 0.1,
    "perturbation_window": "one_proper_time_window",
    "proper_time_only": true,
    "proper_time_persistence_threshold": 3,
    "runtime_visible_inputs": [
      "proper_time_cycle_events",
      "support_area_digest",
      "transported_support_area_digest",
      "topology_event_digest",
      "surface_lineage_record_digest",
      "topology_state_reabsorption_record_digest",
      "node_plus_packet_budget_surface"
    ],
    "support_overlap_kind": "lineage_weighted",
    "support_overlap_threshold": 0.95
  },
  "reflexive_closure": {
    "basin_evidence_bundle": [
      "support_area_mass",
      "retention_score",
      "proper_time_persistence_score",
      "basin_evidence_digest"
    ],
    "conditions": [
      "reentry_coherence_into_support > 0",
      "basin_evidence_after_reentry >= basin_evidence_before_reentry",
      "later_cycle_consumed_updated_basin_evidence = true",
      "budget_error == 0"
    ],
    "controls": [
      "no_reentry",
      "closure_not_consumed_by_later_cycle",
      "improper_proper_time_threshold",
      "failed_persistence",
      "unauthorized_identity_acceptance_event",
      "producer_mutation_boundary_violation",
      "agency_claim_promotion"
    ],
    "identity_acceptance_blocker": "unauthorized_identity_acceptance_event",
    "identity_acceptance_contract_available": false,
    "metric_id": "n07_reflexive_closure_reentry_v1",
    "native_policy_available": false,
    "native_policy_blocker": "native_reflexive_closure_policy_missing",
    "proper_time_persistence_threshold": 3,
    "runtime_visible_inputs": [
      "reentry_packet_event",
      "producer_record",
      "processed_packet_event",
      "basin_evidence_before_reentry",
      "basin_evidence_after_reentry",
      "later_cycle_consumed_basin_evidence_digest",
      "proper_time_identity_persistence_evaluation",
      "node_plus_packet_budget_surface"
    ],
    "stale_digest_blocker": "closure_not_consumed_by_later_cycle"
  },
  "stability_well_proxy": {
    "digest_scope": [
      "proxy_formula",
      "threshold",
      "input_fields",
      "support_area_digest"
    ],
    "hidden_report_side_score_allowed": false,
    "input_fields": [
      "support_area_mass_before",
      "support_area_mass_after",
      "incoming_flux_to_support",
      "outgoing_flux_from_support"
    ],
    "native_policy_available": false,
    "native_policy_blocker": "native_basin_potential_policy_missing",
    "proxy_formula": "0.5 * support_area_mass_retention + 0.5 * local_inflow_dominance_score",
    "selected_proxy": "experiment_local_declared_second_difference_retention_proxy",
    "threshold": 0.75
  },
  "support_area_digest": {
    "excludes_fields": [
      "support_area_digest"
    ],
    "method": "sha256_canonical_json_sorted_keys",
    "required_input_fields": [
      "support_area_id",
      "candidate_identity_carrier_type",
      "support_node_ids",
      "support_edge_ids",
      "support_port_ids",
      "lineage_status",
      "lineage_map_digest",
      "support_surface_digest",
      "event_time_key",
      "scheduler_event_index",
      "budget_surface",
      "budget_before",
      "budget_after",
      "budget_error"
    ]
  }
}
```

## Composite Topologies

| Composite | Primitive blocks | Expected ceiling | Current blocker |
|---|---|---|---|
| `n07_C1_recurrent_single_basin_identity_candidate` | `n07_T1_support_area_minimal, n07_T2_stable_well_basin, n07_T3_attractor_neighborhood, n07_T6_reflexive_closure` | `ID5_after_reflexive_closure_probe` | `not_run_iteration_2_manifest_only` |
| `n07_C2_lineage_current_topology_mutating_identity_candidate` | `n07_T1_support_area_minimal, n07_T5_lineage_current_invariance` | `ID4_until_reflexive_closure_passes` | `not_run_iteration_2_manifest_only` |
| `n07_C3_competing_basin_compatibility_candidate` | `n07_T2_stable_well_basin, n07_T3_attractor_neighborhood` | `ID5_or_ID6_only_after_T7_compatibility_and_replay` | `not_run_iteration_2_manifest_only` |
| `n07_C4_route_fed_route_independent_identity_candidate` | `n07_T1_support_area_minimal, n07_T3_attractor_neighborhood` | `ID3_until_identity_gates_pass_independently` | `not_run_iteration_2_manifest_only` |
| `n07_C5_movement_carried_movement_independent_identity_candidate` | `n07_T1_support_area_minimal, n07_T5_lineage_current_invariance` | `ID4_until_movement_independence_passes` | `not_run_iteration_2_manifest_only` |
| `n07_C6_parent_child_refinement_identity_boundary_candidate` | `n07_T1_support_area_minimal, n07_T5_lineage_current_invariance` | `ID4_until_parent_child_compatibility_passes` | `not_run_iteration_2_manifest_only` |

## Controls

| Control | Primary blocker |
|---|---|
| `label_only_null_topology` | `label_only_null_topology` |
| `missing_support_area` | `missing_support_area` |
| `external_label_only` | `external_label_only` |
| `duplicate_support_row` | `duplicate_support_row` |
| `budget_discontinuity` | `budget_discontinuity` |
| `stale_node_id_replay` | `stale_node_id_replay` |
| `missing_topology_state_reabsorption` | `missing_topology_state_reabsorption` |
| `lineage_map_scrambled` | `lineage_map_scrambled` |
| `support_drift_beyond_threshold` | `support_drift_beyond_threshold` |
| `unstable_basin_no_local_well` | `unstable_basin_no_local_well` |
| `hidden_potential_or_report_side_well_score` | `hidden_potential_or_report_side_well_score` |
| `posthoc_threshold_change` | `posthoc_threshold_change` |
| `identity_threshold_missing` | `identity_threshold_missing` |
| `wrong_support_area` | `wrong_support_area` |
| `no_reentry` | `no_reentry` |
| `closure_not_consumed_by_later_cycle` | `closure_not_consumed_by_later_cycle` |
| `improper_proper_time_threshold` | `improper_proper_time_threshold` |
| `failed_persistence` | `failed_persistence` |
| `non_attractive_flux` | `non_attractive_flux` |
| `wrong_basin` | `wrong_basin` |
| `wrong_polarity` | `wrong_polarity` |
| `subthreshold_flux` | `subthreshold_flux` |
| `hidden_route_context_steering` | `hidden_route_context_steering` |
| `destructive_interference` | `destructive_interference` |
| `ambiguous_overlap` | `ambiguous_overlap` |
| `hidden_support_field` | `hidden_support_field` |
| `producer_mutation_boundary_violation` | `producer_mutation_boundary_violation` |
| `direct_state_or_topology_rewrite` | `direct_state_or_topology_rewrite` |
| `unauthorized_identity_acceptance_event` | `unauthorized_identity_acceptance_event` |
| `identity_claim_promotion` | `identity_claim_promotion` |
| `agency_claim_promotion` | `agency_claim_promotion` |

## Checks

| Check | Passed |
|---|---:|
| `all_baseline_controls_declared` | `True` |
| `baseline_schema_matches_iteration_1` | `True` |
| `becoming_enum_values_declared` | `True` |
| `becoming_fields_declared` | `True` |
| `claim_flags_all_false` | `True` |
| `claim_flags_complete` | `True` |
| `compatibility_metric_declared` | `True` |
| `composite_primitive_refs_resolve` | `True` |
| `composite_rows_complete` | `True` |
| `composite_topologies_complete` | `True` |
| `composite_topology_policy_complete` | `True` |
| `control_blockers_are_distinct` | `True` |
| `derived_id_algorithm_declared` | `True` |
| `fixture_edge_endpoints_exist` | `True` |
| `fixture_edge_ids_unique` | `True` |
| `fixture_node_edge_counts_match` | `True` |
| `fixture_node_ids_unique` | `True` |
| `fixture_ports_resolve` | `True` |
| `flux_metric_declared` | `True` |
| `gate_vector_allowed_values_complete` | `True` |
| `gate_vector_fields_complete` | `True` |
| `hidden_identity_labels_blocked` | `True` |
| `id_levels_are_not_claim_flags` | `True` |
| `identity_threshold_missing_control_declared` | `True` |
| `identity_threshold_missing_declared` | `True` |
| `invariance_policy_declared` | `True` |
| `invariance_thresholds_declared` | `True` |
| `no_identity_acceptance_or_agency_claims` | `True` |
| `no_identity_probe_run` | `True` |
| `no_positive_identity_evidence_generated` | `True` |
| `no_src_changes_required` | `True` |
| `no_support_rows_emitted` | `True` |
| `reflexive_closure_metric_declared` | `True` |
| `reflexive_closure_policy_declared` | `True` |
| `schema_matches` | `True` |
| `stability_proxy_declared` | `True` |
| `support_area_digest_matches` | `True` |
| `support_area_idempotency_key_declared` | `True` |
| `support_area_not_label_identity` | `True` |
| `t4_deferred_with_rationale` | `True` |
| `t5_lineage_required` | `True` |
| `topology_design_policy_complete` | `True` |
| `topology_families_complete` | `True` |
| `topology_family_gates_valid` | `True` |
| `topology_family_metrics_resolve` | `True` |
| `topology_family_rows_complete` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "c71087b29078131e270c2d9508d6f3474762a88cc66d7838e6f6342a4a68e8ae",
  "claim_boundary_digest": "462a721dd54e1b29c82d73cd4385d84b0021f96e51825c4c4aaea3214044ea7b",
  "composite_topologies_digest": "836e37869b5740a8770c8707d160c1ca8e0abde89742de76b96698ee1bbb624f",
  "controls_digest": "4cd7e48045aaabb0dc80b30878b7b680fa10254617cd4310803dfd85e9ddfca5",
  "manifest_digest": "89d46bf941cb40f359b99381f0c7d1b391f67ae3eb07955ec850a8c03a242e5e",
  "metric_definitions_digest": "4f41926bce131f4022aa472cbf83c6ef64f461275ddb5550d4f17dae2c562a1f",
  "topology_families_digest": "5cefd2b9f0a7e66a3d0d26b21ab7111c0111d5a82bff81849f7a3a0df808a949"
}
```

## Acceptance

Iteration 2 passes because N07 fixture topology families, support-area digest
rules, discrete RC observable mappings, gate-vector semantics, composite
topology policies, controls, and claim boundaries are declared before identity
probes. The manifest blocks hidden identity labels, authored-center identity
shortcuts, hidden report-side well scores, budget ambiguity, stale lineage,
producer mutation, and claim promotion.
