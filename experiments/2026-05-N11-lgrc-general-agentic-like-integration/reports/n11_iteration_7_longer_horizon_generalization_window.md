# N11 Iteration 7 Longer-Horizon Generalization Window

Status: `passed`.

## Result

Iteration 7 extended the accepted Iteration 6 matrix rows across an
8-window artifact replay horizon. It recorded source-current status,
node-plus-packet budget error, proxy trend, support trend, transfer
stability, and degradation/recovery pattern for every row.

Current ceiling:

```text
strongest_supported_gali_level = GALI6
strongest_contiguous_gali_level = GALI6
strongest_claim_ceiling = longer_horizon_generalization_candidate
semantic_goal_ownership_claim_allowed = false
intention_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
A7/GALI7 supported = false
```

## Longer-Horizon Summary

```json
{
  "accepted_gali6_examples": [
    {
      "context_tag": "context_same_as_n10",
      "proxy_condition_tag": "proxy_target_band_variant",
      "source_matrix_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__mild_withdrawal_survives_row_v1",
      "source_variant_axis_count": 2,
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_row_id": "n11_i7_n11_i6_context_same_as_n10__proxy_target_band_variant__mild_withdrawal_survives_row_v1_longer_window_v1",
      "trend_digest": "c0fd2509168c29f5aceb804dc055ce81275831ad40d27d2330d363ae52efb0e9"
    },
    {
      "context_tag": "context_same_as_n10",
      "proxy_condition_tag": "proxy_target_band_variant",
      "source_matrix_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1",
      "source_variant_axis_count": 2,
      "support_state_tag": "explicit_restoration_recovers_support",
      "transfer_row_id": "n11_i7_n11_i6_context_same_as_n10__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1_longer_window_v1",
      "trend_digest": "b6c5b7f087786647c8866f0c30b892a2e5522124c35bbeb9af3e3c797378ae5a"
    },
    {
      "context_tag": "context_route_variant",
      "proxy_condition_tag": "proxy_same_as_n10",
      "source_matrix_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__mild_withdrawal_survives_row_v1",
      "source_variant_axis_count": 2,
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_same_as_n10__mild_withdrawal_survives_row_v1_longer_window_v1",
      "trend_digest": "8c46a142bcfb1842d0a036e72611fb2b91e5753aa376563747169a9495529bd4"
    },
    {
      "context_tag": "context_route_variant",
      "proxy_condition_tag": "proxy_same_as_n10",
      "source_matrix_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1",
      "source_variant_axis_count": 2,
      "support_state_tag": "explicit_restoration_recovers_support",
      "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1_longer_window_v1",
      "trend_digest": "927db49b26cb796506819e1443133728059567d220722d4e1e8dc1623ad9dcf1"
    },
    {
      "context_tag": "context_route_variant",
      "proxy_condition_tag": "proxy_target_band_variant",
      "source_matrix_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__support_intact_survives_row_v1",
      "source_variant_axis_count": 2,
      "support_state_tag": "support_intact_survives",
      "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_target_band_variant__support_intact_survives_row_v1_longer_window_v1",
      "trend_digest": "e5ac4fbbad7ad163c133ea9baecf708766111e73f95a4284ceb79ccf6a08959d"
    }
  ],
  "accepted_gali6_row_count": 7,
  "accepted_row_count": 12,
  "blocked_row_count": 0,
  "context_tag_counts": {
    "context_route_variant": 6,
    "context_same_as_n10": 6
  },
  "degradation_or_recovery_pattern_counts": {
    "bounded_low_margin_no_threshold_crossing": 4,
    "restoration_gated_recovery_preserved": 4,
    "stable_no_degradation_detected": 4
  },
  "longer_horizon_row_count": 12,
  "min_support_margin": 0.02583821862,
  "node_plus_packet_budget_error_max": 0.0,
  "proxy_condition_tag_counts": {
    "proxy_same_as_n10": 6,
    "proxy_target_band_variant": 6
  },
  "source_iteration_6_accepted_row_count": 12,
  "source_variant_axis_count_counts": {
    "0": 1,
    "1": 4,
    "2": 5,
    "3": 2
  },
  "support_state_tag_counts": {
    "explicit_restoration_recovers_support": 4,
    "mild_withdrawal_survives": 4,
    "support_intact_survives": 4
  },
  "support_trend_counts": {
    "bounded_low_margin_stable_replay": 4,
    "restoration_gated_stable_after_disruption_history": 4,
    "stable_support_reference_replay": 4
  },
  "unstable_window_count": 0
}
```

## Transfer Rows

```json
[
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_same_as_n10",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI1",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "longer_horizon_reference_or_single_axis_stability",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
    "source_matrix_gali_level": "GALI1",
    "source_matrix_row_id": "n11_i6_context_same_as_n10__proxy_same_as_n10__support_intact_survives_row_v1",
    "source_matrix_transfer_row_digest": "5d1505d633de98a6d26f602e38d69e0671865d62addbd3061c90dd1c21b92ece",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 0,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "795efe07728564d739e533bca7fd8ac1ea595ba6fc8bc36e09279522581f344e",
    "transfer_row_id": "n11_i7_n11_i6_context_same_as_n10__proxy_same_as_n10__support_intact_survives_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "61b9a5706a74e62c8e76f194a9c72a6776db8ec3095067fd45d666988444a1ed",
    "trend_fields": {
      "degradation_or_recovery_pattern": "stable_no_degradation_detected",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55
        ],
        "pre_measurements_by_window": [
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n09_same_band_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 1
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 2
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 3
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 4
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 5
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 6
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 7
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": false,
        "support_margin_min": 0.123153576245,
        "support_retention_by_window": [
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "stable_support_reference_replay"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_same_as_n10",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI4",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "longer_horizon_reference_or_single_axis_stability",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
    "source_matrix_gali_level": "GALI4",
    "source_matrix_row_id": "n11_i6_context_same_as_n10__proxy_same_as_n10__mild_withdrawal_survives_row_v1",
    "source_matrix_transfer_row_digest": "b3de0fed103faab8e3aecffd2ba815d3b963016fad6b3a3b9b5c010426e0d7f3",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 1,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "7dc3f5af5b657221a98831616bf73b84378ece24603040d908cc20bc533a32ab",
    "transfer_row_id": "n11_i7_n11_i6_context_same_as_n10__proxy_same_as_n10__mild_withdrawal_survives_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "12ab5d119e5943c372832e220725ff3b8900dd0d2ae590469f79db5527d8c28f",
    "trend_fields": {
      "degradation_or_recovery_pattern": "bounded_low_margin_no_threshold_crossing",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55
        ],
        "pre_measurements_by_window": [
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n09_same_band_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 1
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 2
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 3
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 4
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 5
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 6
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 7
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": false,
        "support_margin_min": 0.02583821862,
        "support_retention_by_window": [
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "bounded_low_margin_stable_replay"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_same_as_n10",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI4",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "longer_horizon_reference_or_single_axis_stability",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
    "source_matrix_gali_level": "GALI4",
    "source_matrix_row_id": "n11_i6_context_same_as_n10__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1",
    "source_matrix_transfer_row_digest": "7c0ac3491b59e499ab1ef53f38f3560108ddaea258e0cdcc643851814de31428",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 1,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "5ed0c15dfcab9bf4bab787159ad6b11777aec8410a5d423d0d00d945a89b215e",
    "transfer_row_id": "n11_i7_n11_i6_context_same_as_n10__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "61fb6c5cffcf231d10f956c1b6cb04bab0fda21490356fef1de4817582a93e81",
    "trend_fields": {
      "degradation_or_recovery_pattern": "restoration_gated_recovery_preserved",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55
        ],
        "pre_measurements_by_window": [
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n09_same_band_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 1
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 2
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 3
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 4
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 5
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 6
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 7
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": true,
        "support_margin_min": 0.074495897432,
        "support_retention_by_window": [
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "restoration_gated_stable_after_disruption_history"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_same_as_n10",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI4",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "longer_horizon_reference_or_single_axis_stability",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
    "source_matrix_gali_level": "GALI4",
    "source_matrix_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__support_intact_survives_row_v1",
    "source_matrix_transfer_row_digest": "7e3f40df635cc98613a95dd46145c22da4e262373d0b2d7bbf7c84e7fdb219ae",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 1,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "6debaca1f6a2ab84a8ffdb5f1e34291b554cab6bce5369e0482729d722c03378",
    "transfer_row_id": "n11_i7_n11_i6_context_same_as_n10__proxy_target_band_variant__support_intact_survives_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "0ee51dca53de83e9019fc425cf6a3aa4bbac49abaa2223ebaaf72cef69cc8a2e",
    "trend_fields": {
      "degradation_or_recovery_pattern": "stable_no_degradation_detected",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6
        ],
        "pre_measurements_by_window": [
          0.62,
          0.67,
          0.67,
          0.67,
          0.62,
          0.67,
          0.67,
          0.67
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n11_i4b_variant_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 1
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 2
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 3
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 4
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 5
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 6
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 7
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": false,
        "support_margin_min": 0.123153576245,
        "support_retention_by_window": [
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "stable_support_reference_replay"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_same_as_n10",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI6",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "gali6_multi_axis_candidate",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
    "source_matrix_gali_level": "GALI5",
    "source_matrix_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__mild_withdrawal_survives_row_v1",
    "source_matrix_transfer_row_digest": "22faa60ac06b9691d42db18023eb5a666049a39736e5797f46a35d8ae9a6eb3b",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 2,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "d9d43ecaa8962a9c01f6a3deb75600608a4fea8cf37b2c70a3682ab58904ce63",
    "transfer_row_id": "n11_i7_n11_i6_context_same_as_n10__proxy_target_band_variant__mild_withdrawal_survives_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "c0fd2509168c29f5aceb804dc055ce81275831ad40d27d2330d363ae52efb0e9",
    "trend_fields": {
      "degradation_or_recovery_pattern": "bounded_low_margin_no_threshold_crossing",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6
        ],
        "pre_measurements_by_window": [
          0.62,
          0.67,
          0.67,
          0.67,
          0.62,
          0.67,
          0.67,
          0.67
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n11_i4b_variant_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 1
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 2
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 3
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 4
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 5
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 6
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 7
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": false,
        "support_margin_min": 0.02583821862,
        "support_retention_by_window": [
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "bounded_low_margin_stable_replay"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_same_as_n10",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI6",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "gali6_multi_axis_candidate",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
    "source_matrix_gali_level": "GALI5",
    "source_matrix_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1",
    "source_matrix_transfer_row_digest": "fefcbd6356157bab46b68824c4466264619369ab96910331dbc2d70e5ad01788",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 2,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "3a8fec48d28fad2fc7fc593a266e9451f9a5873a9f794462fb4654e75a6574e4",
    "transfer_row_id": "n11_i7_n11_i6_context_same_as_n10__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "b6c5b7f087786647c8866f0c30b892a2e5522124c35bbeb9af3e3c797378ae5a",
    "trend_fields": {
      "degradation_or_recovery_pattern": "restoration_gated_recovery_preserved",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6
        ],
        "pre_measurements_by_window": [
          0.62,
          0.67,
          0.67,
          0.67,
          0.62,
          0.67,
          0.67,
          0.67
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n11_i4b_variant_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 1
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 2
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 3
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 4
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 5
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 6
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 7
        },
        {
          "context_source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
          "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": true,
        "support_margin_min": 0.074495897432,
        "support_retention_by_window": [
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "restoration_gated_stable_after_disruption_history"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_route_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI4",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "longer_horizon_reference_or_single_axis_stability",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
    "source_matrix_gali_level": "GALI4",
    "source_matrix_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__support_intact_survives_row_v1",
    "source_matrix_transfer_row_digest": "1a7bb9f87eee52a043c1d4f837a69feb1c4e3f935dcdccc3d34b415f370aeeb1",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 1,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "6d11465c37954ea3013fed4a9a25d277130376a932b83faf2d944d16fcca1cfe",
    "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_same_as_n10__support_intact_survives_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "51d58153e6895ddc72194dffd0993e8a1d94f7820fef5e46b7af7f607dfb8402",
    "trend_fields": {
      "degradation_or_recovery_pattern": "stable_no_degradation_detected",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55
        ],
        "pre_measurements_by_window": [
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n09_same_band_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 1
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 2
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 3
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 4
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 5
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 6
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 7
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": false,
        "support_margin_min": 0.123153576245,
        "support_retention_by_window": [
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "stable_support_reference_replay"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_route_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI6",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "gali6_multi_axis_candidate",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
    "source_matrix_gali_level": "GALI5",
    "source_matrix_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__mild_withdrawal_survives_row_v1",
    "source_matrix_transfer_row_digest": "d047d8636dac80485b87f4587258a6de9e7452cdabc5710ece286b84b3756519",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 2,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "20f6e7aeb3bd31d3b0cad354d9b56d9666089a8f8d83fe92dbc650b63f66446b",
    "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_same_as_n10__mild_withdrawal_survives_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "8c46a142bcfb1842d0a036e72611fb2b91e5753aa376563747169a9495529bd4",
    "trend_fields": {
      "degradation_or_recovery_pattern": "bounded_low_margin_no_threshold_crossing",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55
        ],
        "pre_measurements_by_window": [
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n09_same_band_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 1
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 2
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 3
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 4
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 5
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 6
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 7
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": false,
        "support_margin_min": 0.02583821862,
        "support_retention_by_window": [
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "bounded_low_margin_stable_replay"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_route_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI6",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "gali6_multi_axis_candidate",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
    "source_matrix_gali_level": "GALI5",
    "source_matrix_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1",
    "source_matrix_transfer_row_digest": "1d255b7fcb52da813e9ebb78affeb4c7f7ec963f53f88d59b90d468b7c276d0a",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 2,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "e38c7fd10a4ff0df59b08f7032f3c68479c5c8c8249cb59ec7be91bb370ac2d0",
    "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "927db49b26cb796506819e1443133728059567d220722d4e1e8dc1623ad9dcf1",
    "trend_fields": {
      "degradation_or_recovery_pattern": "restoration_gated_recovery_preserved",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55,
          0.55
        ],
        "pre_measurements_by_window": [
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62,
          0.62
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n09_same_band_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 1
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 2
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 3
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 4
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 5
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 6
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 7
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
          "proxy_source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": true,
        "support_margin_min": 0.074495897432,
        "support_retention_by_window": [
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "restoration_gated_stable_after_disruption_history"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.55,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_route_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI6",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "gali6_multi_axis_candidate",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
    "source_matrix_gali_level": "GALI5",
    "source_matrix_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__support_intact_survives_row_v1",
    "source_matrix_transfer_row_digest": "68ec2334e8acabcedb0c35138ae456a5bd7debe23a2be9327baa51563451ae0d",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 2,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "aaa3fc6bc0b360d9395a9f48a956197b3892178d20055256992454f6fdb349ea",
    "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_target_band_variant__support_intact_survives_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "e5ac4fbbad7ad163c133ea9baecf708766111e73f95a4284ceb79ccf6a08959d",
    "trend_fields": {
      "degradation_or_recovery_pattern": "stable_no_degradation_detected",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6
        ],
        "pre_measurements_by_window": [
          0.62,
          0.67,
          0.67,
          0.67,
          0.62,
          0.67,
          0.67,
          0.67
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n11_i4b_variant_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 1
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 2
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 3
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 4
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 5
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 6
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 7
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": false,
        "support_margin_min": 0.123153576245,
        "support_retention_by_window": [
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245,
          0.973153576245
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "stable_support_reference_replay"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.973153576245,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_route_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI6",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "gali6_multi_axis_candidate",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
    "source_matrix_gali_level": "GALI5",
    "source_matrix_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__mild_withdrawal_survives_row_v1",
    "source_matrix_transfer_row_digest": "24cd5d81bab470b951796ddf0b33a043bf2bcf2fea0850e8c91edf94770c80a9",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 3,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "3144ac324efaa9e63699368682bb480e02bf60765d576f24b46ff2270e1165e8",
    "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_target_band_variant__mild_withdrawal_survives_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "bcfc95e9aeb5f41e8694fd2b256c67855235db4108976f9793b500c56a11b0b2",
    "trend_fields": {
      "degradation_or_recovery_pattern": "bounded_low_margin_no_threshold_crossing",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6
        ],
        "pre_measurements_by_window": [
          0.62,
          0.67,
          0.67,
          0.67,
          0.62,
          0.67,
          0.67,
          0.67
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n11_i4b_variant_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 1
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 2
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 3
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 4
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 5
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 6
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 7
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": false,
        "support_margin_min": 0.02583821862,
        "support_retention_by_window": [
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862,
          0.87583821862
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "bounded_low_margin_stable_replay"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.87583821862,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 8
      }
    ]
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI6",
    "blocked_claims": [
      "agency",
      "intention",
      "semantic_goal_ownership",
      "semantic_goal_understanding",
      "identity_acceptance",
      "runtime_identity_acceptance",
      "rc_identity_collapse",
      "aco_like_behavior",
      "ant_colony_behavior",
      "locomotion_like_behavior",
      "biological_behavior",
      "personhood",
      "unrestricted_identity",
      "unrestricted_movement",
      "unrestricted_agency",
      "fully_native_agentic_like_integration",
      "A7_generalization_by_inheritance",
      "GALI7_by_inheritance"
    ],
    "claim_flags": {
      "a7_claim_allowed": false,
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "gali7_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "context_tag": "context_route_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "longer_horizon_generalization_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "longer_horizon_generalization_window",
      "planned_iteration": 7,
      "proxy_condition_tag": "proxy_perturbation_envelope_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_axis": "longer_horizon",
      "transfer_window_tag": "longer_horizon_window",
      "window_spec": {
        "boundedness_required": "node_plus_packet_budget_error remains zero or the row is blocked; source-current status must remain true; support, proxy, and transfer trends must remain bounded or be explicitly downgraded",
        "minimum_extended_window_count": 8,
        "reference_n10_bounded_window_count": 4,
        "trend_fields_required": [
          "source_current_status_by_window",
          "node_plus_packet_budget_error_by_window",
          "support_trend",
          "proxy_trend",
          "transfer_stability_trend",
          "degradation_or_recovery_pattern"
        ]
      }
    },
    "gali_level": "GALI6",
    "hidden_steering_used": false,
    "interpretation": "The source matrix row remains source-current, budget-clean, proxy-in-band, support-surviving, and claim-clean across the bounded 8-window artifact replay extension.",
    "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
    "longer_horizon_role": "gali6_multi_axis_candidate",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "reference_n10_bounded_window_count": 4,
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_6_multi_axis_transfer_matrix": "9dff6b26c3df467f17cd9607ebe32a1499db3cf4e8f7de1a86d13687ba8e754e"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_6_multi_axis_transfer_matrix.json"
    },
    "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
    "source_matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
    "source_matrix_gali_level": "GALI5",
    "source_matrix_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1",
    "source_matrix_transfer_row_digest": "3bf7ab61dc1599be5410cab7cffd50025fe675544886fd518b9d05eae7a05751",
    "source_reports": {
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_6_multi_axis_transfer_matrix": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_6_multi_axis_transfer_matrix.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_variant_axis_count": 3,
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": true,
    "transfer_axis": "longer_horizon",
    "transfer_outcome_tag": "longer_horizon_generalization_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "3d1dee882c250702ad64a0348b218d42321c065612e1f99ee6c9ddca4cac6f3a",
    "transfer_row_id": "n11_i7_n11_i6_context_route_variant__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1_longer_window_v1",
    "transfer_window_tag": "longer_horizon_window",
    "trend_digest": "a611fd2c8f82f6b9e394c84bd4870cb7cbb3dbd7fe4f4ad38a09f50cdda49837",
    "trend_fields": {
      "degradation_or_recovery_pattern": "restoration_gated_recovery_preserved",
      "node_plus_packet_budget_error_by_window": [
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 1
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 2
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 3
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 4
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 5
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 6
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 7
        },
        {
          "node_plus_packet_budget_error": 0.0,
          "window_index": 8
        }
      ],
      "proxy_trend": {
        "post_measurements_by_window": [
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6,
          0.6
        ],
        "pre_measurements_by_window": [
          0.62,
          0.67,
          0.67,
          0.67,
          0.62,
          0.67,
          0.67,
          0.67
        ],
        "proxy_error_after_max": 0.0,
        "proxy_in_band_after_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "proxy_pattern_kind": "n11_i4b_variant_four_cycle_replay_repeated",
        "proxy_trend": "bounded_repeated_source_pattern",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "source_current_status_by_window": [
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 1
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 2
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 3
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 4
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 5
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 6
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 7
        },
        {
          "context_source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
          "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
          "proxy_source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
          "source_current": true,
          "source_current_status": "source_current_from_iteration_6_matrix_cell",
          "support_source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
          "window_index": 8
        }
      ],
      "support_trend": {
        "explicit_restoration_present": true,
        "support_margin_min": 0.074495897432,
        "support_retention_by_window": [
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432,
          0.924495897432
        ],
        "support_survival_passed_all_windows": true,
        "support_survival_threshold": 0.85,
        "support_trend": "restoration_gated_stable_after_disruption_history"
      },
      "transfer_stability_trend": {
        "stable_by_window": [
          true,
          true,
          true,
          true,
          true,
          true,
          true,
          true
        ],
        "stable_window_count": 8,
        "transfer_stability_trend": "stable_all_windows",
        "unstable_window_count": 0
      }
    },
    "window_count": 8,
    "window_records": [
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 1
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 2
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 3
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 4
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.62,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 5
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 6
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 7
      },
      {
        "claim_flags_false": true,
        "node_plus_packet_budget_error": 0.0,
        "proxy_in_band_after": true,
        "proxy_measurement_after": 0.6,
        "proxy_measurement_before": 0.67,
        "source_current": true,
        "support_retention": 0.924495897432,
        "support_survival_passed": true,
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
        "window_index": 8
      }
    ]
  }
]
```

## Controls

```json
{
  "a7_gali7_by_inheritance": {
    "control_passed": true,
    "primary_blocker": "gali7_by_inheritance_blocked",
    "reason": "GALI6 longer-horizon evidence does not promote GALI7/A7."
  },
  "budget_drift": {
    "control_passed": true,
    "primary_blocker": "node_plus_packet_budget_discontinuity",
    "reason": "Node-plus-packet budget error remains 0.0 in every replay window."
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "All claim flags remain false on every longer-horizon row."
  },
  "hidden_repair_or_steering": {
    "control_passed": true,
    "primary_blocker": "hidden_experiment_side_steering",
    "reason": "Window traces repeat source-backed proxy/support patterns and cannot add hidden repair fields."
  },
  "stale_proxy_state": {
    "control_passed": true,
    "primary_blocker": "stale_proxy_state_blocked",
    "reason": "Proxy traces use only Iteration 4 same-band or Iteration 4-B variant-band source digests."
  },
  "stale_source_row": {
    "control_passed": true,
    "primary_blocker": "stale_context_blocked",
    "reason": "Every longer-horizon row links back to a source-current Iteration 6 matrix-cell digest in every window."
  },
  "stale_support_state": {
    "control_passed": true,
    "primary_blocker": "stale_support_state_blocked",
    "reason": "Support trends are inherited from source-current Iteration 6 support digests."
  }
}
```

## Checks

```json
{
  "a7_not_supported": true,
  "accepted_gali6_rows_present": true,
  "all_claim_flags_false": true,
  "all_controls_passed": true,
  "all_required_fields_present": true,
  "all_rows_have_required_window_count": true,
  "all_transfer_row_digests_valid": true,
  "all_trend_digests_valid": true,
  "baseline_passed": true,
  "budget_errors_zero_all_windows": true,
  "gali6_multi_axis_rows_present": true,
  "gali7_not_supported": true,
  "iteration_4_available": true,
  "iteration_4b_available": true,
  "iteration_6_matrix_passed": true,
  "longer_horizon_lane_present": true,
  "manifest_passed": true,
  "only_accepted_iteration_6_rows_selected": true,
  "proxy_in_band_all_windows": true,
  "source_current_all_windows": true,
  "src_clean_for_iteration_7": true,
  "support_survives_all_windows": true,
  "transfer_stable_all_windows": true,
  "trend_fields_present": true,
  "window_count_matches_manifest": true
}
```

## Interpretation

This is an artifact replay extension, not a new native runtime stress
test. Its value is the trend record: accepted source rows remain
source-current, budget-clean, proxy-in-band, support-surviving, and
claim-clean over the declared longer horizon. Mild withdrawal is kept as
a bounded low-margin trend, and explicit restoration is recorded as
restoration-gated recovery. The result supports GALI6 as a bounded
longer-horizon candidate only; it does not support A7, GALI7, agency,
intention, semantic goal ownership, or identity acceptance.

## Acceptance

Iteration 7 passes if accepted transfer rows remain source-current, budget-clean, and claim-clean across a bounded longer window, or else record their degradation with distinct blockers. Trend and envelope evidence must be recorded; a bare true/false result is not sufficient.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/run_n11_iteration_7_longer_horizon_generalization_window.py
```

Output digest:

```text
dd1409f5f777a46958467ca1f161b83e8173258a003423575b44e86a7b2e552f
```
