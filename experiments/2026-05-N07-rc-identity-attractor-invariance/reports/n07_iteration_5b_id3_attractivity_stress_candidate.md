# N07 Iteration 5-B: ID3 Attractivity Stress

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_5b_id3_attractivity_stress_candidate.py
```

Iteration 5-B treats Iteration 5 as a first-pass ID3 attractivity candidate and
adds a stronger stress record: two source nodes from the manifest-declared
neighborhood U, three proper-time windows, serialized distance/potential
approach traces, retained support mass after inflow, exact node-plus-packet
budget, and distinct negative controls.

This strengthens the ID3 attractor candidate but does not promote to ID4,
native identity support, agency, identity acceptance, movement, or semantic
choice. Native attractor-neighborhood policy support remains unavailable, so
the implementation surface is still experiment-local.

## Multi-Window Event

```json
{
  "all_windows_positive_margin": true,
  "approach_metric_id": "n07_multi_window_distance_potential_approach_v1",
  "approach_metric_kind": "distance_to_support_nonincreasing_and_potential_decrease",
  "approach_traces_digest": "d1227282aa47172f4d695f378d8574957a1208eb51dd4ac913c45b37b7c3fcab",
  "budget_error_max": 0.0,
  "budget_surface": "node_plus_packet",
  "candidate_basin_id": "n07_basin_A_candidate_v1",
  "candidate_identity_carrier_type": "coherence_basin",
  "distance_nonincreasing_all_sources": true,
  "distinct_source_count": 2,
  "event_id": "n07_i5b_attractivity_stress_event_0001",
  "event_kind": "experiment_local_runtime_visible_multi_window_attractivity_stress",
  "event_time_key": "n07_i5b_t3_multi_window_attractivity_stress",
  "final_support_area_mass": 1.455,
  "flux_metric_id": "n07_flux_convergence_to_support_v1",
  "hidden_route_context_steering_used": false,
  "neighborhood_U": {
    "excluded_wrong_basin_node_ids": [
      5
    ],
    "flux_source_node_ids": [
      0,
      4
    ],
    "neighborhood_id": "n07_U_support_A_v1",
    "node_ids": [
      0,
      1,
      3,
      4
    ],
    "target_support_area_id": "n07_support_area_A_v1"
  },
  "neighborhood_U_digest": "c9a63c87b120554882f09fb3f3f8c010425735395909b3a65e336ee5e9578a05",
  "nonnegative_state_passed": true,
  "not_throughput_only": true,
  "potential_decreases_all_sources": true,
  "preselected_by_fixture_label": false,
  "report_side_only": false,
  "runtime_visible": true,
  "scheduler_event_index": 3,
  "source_backed": true,
  "source_flux_convergence_record_digest": "3c65623498c011abe71ce795308152a258f5944229944750a335b5c02497f526",
  "source_id3_candidate_row_digest": "ccc285afc59abcad2c07fb1f75009a42400f5ce2357a4adb7d796536fd677177",
  "source_id3_candidate_row_id": "n07_i5_id3_attractivity_candidate_row_v1",
  "source_iteration_5_output_path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json",
  "source_iteration_5_output_sha256": "7da0bfbc044eb8589d0d4749d59fe21b72dc095299546807b1d46058c07c2ebc",
  "source_node_ids": [
    0,
    4
  ],
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_retention_after_inflow_passed": true,
  "topology_family_id": "n07_T3_attractor_neighborhood",
  "window_count": 3,
  "windows": [
    {
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "event_time_key": "n07_i5b_t3_window_0",
      "hidden_route_context_steering_used": false,
      "min_active_node_coherence": 0.0,
      "min_packet_amount": 0.04,
      "net_flux_convergence_margin": 0.18,
      "net_flux_into_support_from_U": 0.22,
      "net_flux_out_of_support": 0.04,
      "nonnegative_state_passed": true,
      "packet_work_events": [
        {
          "amount": 0.12,
          "packet_event_id": "n07_i5b_w0_packet_0001",
          "polarity": "toward_support",
          "route_node_ids": [
            0,
            1,
            2
          ],
          "runtime_visible": true,
          "source_node_id": 0,
          "target_node_id": 2
        },
        {
          "amount": 0.1,
          "packet_event_id": "n07_i5b_w0_packet_0002",
          "polarity": "toward_support",
          "route_node_ids": [
            4,
            2
          ],
          "runtime_visible": true,
          "source_node_id": 4,
          "target_node_id": 2
        },
        {
          "amount": 0.04,
          "packet_event_id": "n07_i5b_w0_packet_0003",
          "polarity": "away_from_support",
          "route_node_ids": [
            2,
            3
          ],
          "runtime_visible": true,
          "source_node_id": 2,
          "target_node_id": 3
        }
      ],
      "packet_work_events_digest": "a1fb58ca7831eb346be93312f38d0f8db76c697bc94494cfea96c986d174a3de",
      "preselected_by_fixture_label": false,
      "proper_time_index": 0,
      "report_side_only": false,
      "retained_inflow_fraction": 0.8181818181818181,
      "retention_passed": true,
      "retention_threshold": 0.7,
      "runtime_visible": true,
      "scheduler_event_index": 3,
      "source_approach_traces": [
        {
          "distance_nonincreasing": true,
          "distance_to_support_after": 1.0,
          "distance_to_support_before": 2.0,
          "potential_decreased": true,
          "potential_score_after": 0.55,
          "potential_score_before": 1.0,
          "runtime_visible": true,
          "source_node_id": 0
        },
        {
          "distance_nonincreasing": true,
          "distance_to_support_after": 0.55,
          "distance_to_support_before": 1.0,
          "potential_decreased": true,
          "potential_score_after": 0.42,
          "potential_score_before": 0.75,
          "runtime_visible": true,
          "source_node_id": 4
        }
      ],
      "source_approach_traces_digest": "ec377fa5acb89f5dc99201ccefb23f8d7bfefc15fce78d330dbbd46d2be6306a",
      "source_backed": true,
      "support_area_mass_after_inflow": 1.22,
      "support_area_mass_after_settle": 1.18,
      "support_area_mass_before": 1.0,
      "through_loss_fraction": 0.18181818181818182,
      "throughput_only": false,
      "window_id": "n07_i5b_window_0",
      "wrong_basin_node_ids_observed": []
    },
    {
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "event_time_key": "n07_i5b_t3_window_1",
      "hidden_route_context_steering_used": false,
      "min_active_node_coherence": 0.0,
      "min_packet_amount": 0.035,
      "net_flux_convergence_margin": 0.155,
      "net_flux_into_support_from_U": 0.19,
      "net_flux_out_of_support": 0.035,
      "nonnegative_state_passed": true,
      "packet_work_events": [
        {
          "amount": 0.1,
          "packet_event_id": "n07_i5b_w1_packet_0001",
          "polarity": "toward_support",
          "route_node_ids": [
            0,
            1,
            2
          ],
          "runtime_visible": true,
          "source_node_id": 0,
          "target_node_id": 2
        },
        {
          "amount": 0.09,
          "packet_event_id": "n07_i5b_w1_packet_0002",
          "polarity": "toward_support",
          "route_node_ids": [
            4,
            2
          ],
          "runtime_visible": true,
          "source_node_id": 4,
          "target_node_id": 2
        },
        {
          "amount": 0.035,
          "packet_event_id": "n07_i5b_w1_packet_0003",
          "polarity": "away_from_support",
          "route_node_ids": [
            2,
            3
          ],
          "runtime_visible": true,
          "source_node_id": 2,
          "target_node_id": 3
        }
      ],
      "packet_work_events_digest": "add193e012d00c45dc17c940bb9f66fc801891f5ef4f964c163c5004d50a130e",
      "preselected_by_fixture_label": false,
      "proper_time_index": 1,
      "report_side_only": false,
      "retained_inflow_fraction": 0.8157894736842105,
      "retention_passed": true,
      "retention_threshold": 0.7,
      "runtime_visible": true,
      "scheduler_event_index": 4,
      "source_approach_traces": [
        {
          "distance_nonincreasing": true,
          "distance_to_support_after": 0.4,
          "distance_to_support_before": 1.0,
          "potential_decreased": true,
          "potential_score_after": 0.25,
          "potential_score_before": 0.55,
          "runtime_visible": true,
          "source_node_id": 0
        },
        {
          "distance_nonincreasing": true,
          "distance_to_support_after": 0.2,
          "distance_to_support_before": 0.55,
          "potential_decreased": true,
          "potential_score_after": 0.18,
          "potential_score_before": 0.42,
          "runtime_visible": true,
          "source_node_id": 4
        }
      ],
      "source_approach_traces_digest": "b40f2600f30a1f2c599496e16d8a0dbf84252a0f9f733248e2ac7817849aec6b",
      "source_backed": true,
      "support_area_mass_after_inflow": 1.3699999999999999,
      "support_area_mass_after_settle": 1.335,
      "support_area_mass_before": 1.18,
      "through_loss_fraction": 0.1842105263157895,
      "throughput_only": false,
      "window_id": "n07_i5b_window_1",
      "wrong_basin_node_ids_observed": []
    },
    {
      "budget_after": 6.0,
      "budget_before": 6.0,
      "budget_error": 0.0,
      "budget_surface": "node_plus_packet",
      "event_time_key": "n07_i5b_t3_window_2",
      "hidden_route_context_steering_used": false,
      "min_active_node_coherence": 0.0,
      "min_packet_amount": 0.03,
      "net_flux_convergence_margin": 0.12000000000000002,
      "net_flux_into_support_from_U": 0.15000000000000002,
      "net_flux_out_of_support": 0.03,
      "nonnegative_state_passed": true,
      "packet_work_events": [
        {
          "amount": 0.08,
          "packet_event_id": "n07_i5b_w2_packet_0001",
          "polarity": "toward_support",
          "route_node_ids": [
            0,
            1,
            2
          ],
          "runtime_visible": true,
          "source_node_id": 0,
          "target_node_id": 2
        },
        {
          "amount": 0.07,
          "packet_event_id": "n07_i5b_w2_packet_0002",
          "polarity": "toward_support",
          "route_node_ids": [
            4,
            2
          ],
          "runtime_visible": true,
          "source_node_id": 4,
          "target_node_id": 2
        },
        {
          "amount": 0.03,
          "packet_event_id": "n07_i5b_w2_packet_0003",
          "polarity": "away_from_support",
          "route_node_ids": [
            2,
            3
          ],
          "runtime_visible": true,
          "source_node_id": 2,
          "target_node_id": 3
        }
      ],
      "packet_work_events_digest": "ad4f8f6c682e3ef513b3811fb2d2b4e5945d50e6de41b395d02b27734d71df4c",
      "preselected_by_fixture_label": false,
      "proper_time_index": 2,
      "report_side_only": false,
      "retained_inflow_fraction": 0.8,
      "retention_passed": true,
      "retention_threshold": 0.7,
      "runtime_visible": true,
      "scheduler_event_index": 5,
      "source_approach_traces": [
        {
          "distance_nonincreasing": true,
          "distance_to_support_after": 0.0,
          "distance_to_support_before": 0.4,
          "potential_decreased": true,
          "potential_score_after": 0.0,
          "potential_score_before": 0.25,
          "runtime_visible": true,
          "source_node_id": 0
        },
        {
          "distance_nonincreasing": true,
          "distance_to_support_after": 0.0,
          "distance_to_support_before": 0.2,
          "potential_decreased": true,
          "potential_score_after": 0.0,
          "potential_score_before": 0.18,
          "runtime_visible": true,
          "source_node_id": 4
        }
      ],
      "source_approach_traces_digest": "907a214ac27446e8646d972392b55e22b4cf50e33e4fed9210ddddb82b1c0592",
      "source_backed": true,
      "support_area_mass_after_inflow": 1.4849999999999999,
      "support_area_mass_after_settle": 1.455,
      "support_area_mass_before": 1.335,
      "through_loss_fraction": 0.19999999999999996,
      "throughput_only": false,
      "window_id": "n07_i5b_window_2",
      "wrong_basin_node_ids_observed": []
    }
  ],
  "windows_digest": "52da914b6e823c887ebaad4b0262560c413fa4b2f2ef7a435345aec83cd93b9b"
}
```

## Attractivity Stress Record

```json
{
  "all_sources_approach_support": true,
  "all_windows_positive_margin": true,
  "approach_metric_id": "n07_multi_window_distance_potential_approach_v1",
  "approach_metric_kind": "distance_to_support_nonincreasing_and_potential_decrease",
  "approach_metric_passed": true,
  "attractivity_gate": "pass",
  "budget_error_max": 0.0,
  "budget_surface": "node_plus_packet",
  "distinct_source_count": 2,
  "final_support_area_mass": 1.455,
  "flux_metric_id": "n07_flux_convergence_to_support_v1",
  "hidden_route_context_steering_used": false,
  "native_policy_available": false,
  "native_policy_blocker": "native_attractor_neighborhood_policy_missing",
  "neighborhood_U_digest": "c9a63c87b120554882f09fb3f3f8c010425735395909b3a65e336ee5e9578a05",
  "nonnegative_state_passed": true,
  "not_throughput_only": true,
  "positive_threshold": 0.0,
  "preselected_by_fixture_label": false,
  "record_id": "n07_i5b_attractivity_stress_record_v1",
  "record_kind": "experiment_local_multi_window_attractivity_stress_record",
  "report_side_only": false,
  "retention_threshold": 0.7,
  "runtime_visible": true,
  "source_backed": true,
  "source_event_digest": "cbb007f76fd7b4ceac4c9826ecff0f6f45b7be6a4734e1e1e42ad11fda190532",
  "source_event_id": "n07_i5b_attractivity_stress_event_0001",
  "source_flux_convergence_record_digest": "3c65623498c011abe71ce795308152a258f5944229944750a335b5c02497f526",
  "source_id3_candidate_row_digest": "ccc285afc59abcad2c07fb1f75009a42400f5ce2357a4adb7d796536fd677177",
  "source_node_ids": [
    0,
    4
  ],
  "stress_metric_id": "n07_multi_source_multi_window_attractivity_stress_v1",
  "stress_record_digest": "64f9c5e33d7dcb1f6c727d8099fe6b419e022350277ee47fdaee84842dc4ff59",
  "stress_record_digest_input": {
    "approach_metric_id": "n07_multi_window_distance_potential_approach_v1",
    "approach_traces_digest": "d1227282aa47172f4d695f378d8574957a1208eb51dd4ac913c45b37b7c3fcab",
    "event_time_key": "n07_i5b_t3_multi_window_attractivity_stress",
    "metric_id": "n07_flux_convergence_to_support_v1",
    "neighborhood_U_digest": "c9a63c87b120554882f09fb3f3f8c010425735395909b3a65e336ee5e9578a05",
    "retention_threshold": 0.7,
    "scheduler_event_index": 3,
    "source_flux_convergence_record_digest": "3c65623498c011abe71ce795308152a258f5944229944750a335b5c02497f526",
    "source_id3_candidate_row_digest": "ccc285afc59abcad2c07fb1f75009a42400f5ce2357a4adb7d796536fd677177",
    "source_node_ids": [
      0,
      4
    ],
    "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "window_count": 3,
    "windows_digest": "52da914b6e823c887ebaad4b0262560c413fa4b2f2ef7a435345aec83cd93b9b"
  },
  "stress_record_idempotency_key": {
    "event_time_key": "n07_i5b_t3_multi_window_attractivity_stress",
    "neighborhood_U_digest": "c9a63c87b120554882f09fb3f3f8c010425735395909b3a65e336ee5e9578a05",
    "source_id3_candidate_row_digest": "ccc285afc59abcad2c07fb1f75009a42400f5ce2357a4adb7d796536fd677177",
    "stress_metric_id": "n07_multi_source_multi_window_attractivity_stress_v1",
    "windows_digest": "52da914b6e823c887ebaad4b0262560c413fa4b2f2ef7a435345aec83cd93b9b"
  },
  "stress_record_idempotency_key_digest": "5c309ca3762e59b207f96a446e2de77c0681be545060a0b95195805c11bc22b6",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_retention_after_inflow_passed": true,
  "window_count": 3
}
```

## Candidate Row

```json
{
  "activity_history_digest": "46e26f7308e7e39e39259d06473ae145fa9531e0f7d5e47f7efcf1539c862d18",
  "agency_claim_allowed": false,
  "attractivity_is_agency_claim": false,
  "attractivity_stress_record_digest": "64f9c5e33d7dcb1f6c727d8099fe6b419e022350277ee47fdaee84842dc4ff59",
  "attractivity_stress_record_id": "n07_i5b_attractivity_stress_record_v1",
  "becoming_class_status": "observation_tag",
  "boundary_rung": "structured_consequence",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "attractor_candidate_stress_validated",
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
  "derived_id_ceiling": "ID3",
  "experiment_local_observables_used": [
    "n07_i5b_attractivity_stress_event_0001",
    "n07_i5b_attractivity_stress_record_v1"
  ],
  "gate_vector": {
    "artifact_replay": "not_measured",
    "attractivity": "pass",
    "compatibility": "not_measured",
    "invariance": "not_measured",
    "lineage_current": "not_applicable",
    "reflexive_closure": "not_measured",
    "stability": "pass",
    "support": "pass"
  },
  "id3_is_not_id4": true,
  "id_level": "ID3",
  "identity_acceptance_claim_allowed": false,
  "identity_carrier_surface": "runtime_coherence_basin",
  "implementation_surface": "experiment_local_identity_gate_record",
  "native_observables_used": [
    "manifest_declared_lgrc_node_ids",
    "manifest_declared_lgrc_edge_ids",
    "node_plus_packet_budget_accounting"
  ],
  "native_policy_blockers": [
    "native_attractor_neighborhood_policy_missing"
  ],
  "native_support_status": "experiment_local",
  "naturalization_rung": "Nat0_probe_dependent_expression",
  "primary_blocker": null,
  "probe_role": "diagnostic_probe",
  "row_id": "n07_i5b_id3_attractivity_stress_candidate_row_v1",
  "runtime_family": "LGRC9V3",
  "source_artifact_sha256": {
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json": "7da0bfbc044eb8589d0d4749d59fe21b72dc095299546807b1d46058c07c2ebc"
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
      "flux_convergence_record_digest": "3c65623498c011abe71ce795308152a258f5944229944750a335b5c02497f526",
      "id3_candidate_row_digest": "ccc285afc59abcad2c07fb1f75009a42400f5ce2357a4adb7d796536fd677177",
      "name": "n07_iteration_5_id3_attractivity_candidate",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json",
      "sha256": "7da0bfbc044eb8589d0d4749d59fe21b72dc095299546807b1d46058c07c2ebc",
      "status": "passed"
    }
  ],
  "source_flux_convergence_record_digest": "3c65623498c011abe71ce795308152a258f5944229944750a335b5c02497f526",
  "source_id3_candidate_row_digest": "ccc285afc59abcad2c07fb1f75009a42400f5ce2357a4adb7d796536fd677177",
  "source_id3_candidate_row_id": "n07_i5_id3_attractivity_candidate_row_v1",
  "source_reports": [
    {
      "name": "n07_iteration_5_id3_attractivity_candidate_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_5_id3_attractivity_candidate.md",
      "sha256": "5c0b0678b26056ac4a8ffd7fced456160e40c700624cc9ca857c8a516b2afcf6"
    }
  ],
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_dependency_status": "probe_dependent",
  "topology_family_id": "n07_T3_attractor_neighborhood",
  "visual_is_evidence_source": false,
  "visual_reference": null,
  "withdrawal_test_status": "not_tested"
}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
| `non_attractive_flux` | `blocked` | `non_attractive_flux` | `ID2` |
| `wrong_basin` | `blocked` | `wrong_basin` | `ID2` |
| `wrong_polarity` | `blocked` | `wrong_polarity` | `ID2` |
| `subthreshold_flux` | `blocked` | `subthreshold_flux` | `ID2` |
| `hidden_route_context_steering` | `blocked` | `hidden_route_context_steering` | `ID2` |
| `failed_persistence` | `blocked` | `failed_persistence` | `ID2` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID2` |

## Checks

| Check | Passed |
|---|---:|
| `all_windows_positive_margin` | `True` |
| `all_windows_runtime_visible` | `True` |
| `approach_metric_serialized` | `True` |
| `attractivity_not_agency_claim` | `True` |
| `becoming_method_values_allowed` | `True` |
| `budget_exact` | `True` |
| `candidate_carrier_is_coherence_basin` | `True` |
| `candidate_gate_matches_manifest` | `True` |
| `candidate_target_id_matches_manifest` | `True` |
| `candidate_topology_family_matches_manifest` | `True` |
| `claim_flag_keys_match_manifest` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_distinct` | `True` |
| `control_ceilings_id2` | `True` |
| `controls_blocked` | `True` |
| `derived_ceiling_id3` | `True` |
| `distance_nonincreasing_all_sources` | `True` |
| `evidence_only_surfaces_not_promoted` | `True` |
| `gate_vector_schema_matches_manifest` | `True` |
| `identity_acceptance_blocked` | `True` |
| `multi_source_count_passed` | `True` |
| `multi_window_count_passed` | `True` |
| `native_support_not_overstated` | `True` |
| `neighborhood_u_matches_manifest` | `True` |
| `no_hidden_route_context_steering` | `True` |
| `no_src_changes_required` | `True` |
| `nonnegative_state_passed` | `True` |
| `not_preselected_by_fixture_labels` | `True` |
| `not_throughput_only` | `True` |
| `potential_decreases_all_sources` | `True` |
| `required_controls_present` | `True` |
| `source_id3_gate_vector_passed` | `True` |
| `source_iteration_5_is_first_pass_candidate` | `True` |
| `source_iteration_5_status_passed` | `True` |
| `status_passed` | `True` |
| `stress_record_passed` | `True` |
| `support_retention_after_inflow_passed` | `True` |
| `window_margins_recomputed` | `True` |
| `window_support_masses_recomputed` | `True` |

## Artifact Digests

```json
{
  "attractivity_stress_record_digest": "6c8026422a0ec495acb070812e9b5b60fb9405f6d0d7e8be9d7cbc390b872172",
  "checks_digest": "8703ac5bf2585b6005224e967ec2712c19798106bd81b45c54482053e040f9a8",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "bbf1cbe0b404d4047e0e295cd15b287a456ba2565479b8d3329e7c7efba202f3",
  "id3_stress_candidate_row_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
  "multi_window_event_digest": "cbb007f76fd7b4ceac4c9826ecff0f6f45b7be6a4734e1e1e42ad11fda190532",
  "source_iteration_5_output_digest": "406079cbc1d927204815d26cb4a25220129b68ccc9c4a5f276ce2c3ce573449f"
}
```

## Acceptance

Iteration 5-B passes because attractivity remains positive across multiple
runtime-visible source points and multiple windows from the declared
neighborhood U, with a serialized approach metric, exact budget accounting,
stable post-inflow support evidence, and distinct controls. It strengthens the
ID3 attractor candidate but does not promote to ID4, agency, identity
acceptance, or native identity support.
