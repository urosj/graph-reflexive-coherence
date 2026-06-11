# N11 Iteration 6 Multi-Axis Transfer Matrix

Status: `passed`.

## Result

Iteration 6 expanded the source-backed context, proxy, and support
axes into a deterministic 24-row matrix. It did not ask for universal
success. It recorded a generalization envelope: rows with available
context/proxy/support sources pass, rows requiring the missing alternate
arbitration policy block, and rows using disrupted support block unless
explicit restoration is the selected support state.

Current ceiling:

```text
strongest_supported_gali_level = GALI5
strongest_contiguous_gali_level = GALI5
strongest_claim_ceiling = multi_axis_bounded_transfer_candidate
semantic_goal_ownership_claim_allowed = false
intention_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
A7/GALI7 supported = false
```

## Matrix Summary

```json
{
  "accepted_gali5_examples": [
    {
      "context_tag": "context_same_as_n10",
      "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__mild_withdrawal_survives_row_v1",
      "variant_axis_count": 2
    },
    {
      "context_tag": "context_same_as_n10",
      "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "explicit_restoration_recovers_support",
      "transfer_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1",
      "variant_axis_count": 2
    },
    {
      "context_tag": "context_route_variant",
      "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
      "proxy_condition_tag": "proxy_same_as_n10",
      "support_state_tag": "mild_withdrawal_survives",
      "transfer_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__mild_withdrawal_survives_row_v1",
      "variant_axis_count": 2
    },
    {
      "context_tag": "context_route_variant",
      "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
      "proxy_condition_tag": "proxy_same_as_n10",
      "support_state_tag": "explicit_restoration_recovers_support",
      "transfer_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1",
      "variant_axis_count": 2
    },
    {
      "context_tag": "context_route_variant",
      "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_intact_survives",
      "transfer_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__support_intact_survives_row_v1",
      "variant_axis_count": 2
    }
  ],
  "accepted_gali5_row_count": 7,
  "accepted_row_count": 12,
  "actual_row_count": 24,
  "blocked_row_count": 12,
  "blocker_chain_counts": {
    "context_arbitration_policy_variant_missing_source": 8,
    "support_disrupted_but_integration_allowed": 6
  },
  "context_tag_counts": {
    "context_arbitration_policy_variant": 8,
    "context_route_variant": 8,
    "context_same_as_n10": 8
  },
  "expected_minimum_row_count": 24,
  "primary_blocker_counts": {
    "context_arbitration_policy_variant_missing_source": 8,
    "null": 12,
    "support_disrupted_but_integration_allowed": 4
  },
  "proxy_condition_tag_counts": {
    "proxy_same_as_n10": 12,
    "proxy_target_band_variant": 12
  },
  "support_state_tag_counts": {
    "explicit_restoration_recovers_support": 6,
    "mild_withdrawal_survives": 6,
    "n09_matched_withdrawal_disrupts_support": 6,
    "support_intact_survives": 6
  },
  "variant_axis_count_counts": {
    "0": 1,
    "1": 6,
    "2": 11,
    "3": 6
  }
}
```

## Transfer Rows

```json
[
  {
    "arc_of_becoming_classification": "local_observation_tag",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI1",
    "hidden_steering_used": false,
    "matrix_cell_digest": "489a7559bfa6be2b39181c063a5e9117d61f7aab76942ba6cb4b996db377dce2",
    "matrix_interpretation": "Accepted source-backed matrix reference or single-axis row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_same_as_n10_reference_row_v1",
        "source_scope": "reference_context"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_support_intact_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9731535762447039
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "5d1505d633de98a6d26f602e38d69e0671865d62addbd3061c90dd1c21b92ece",
    "transfer_row_id": "n11_i6_context_same_as_n10__proxy_same_as_n10__support_intact_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 0
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI4",
    "hidden_steering_used": false,
    "matrix_cell_digest": "ccdc552dc581ebba0e8c1e048a2cb211ddbe020d1bcdda02e2b604ec47e009cc",
    "matrix_interpretation": "Accepted source-backed matrix reference or single-axis row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_same_as_n10_reference_row_v1",
        "source_scope": "reference_context"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_mild_withdrawal_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.8758382186202335
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "b3de0fed103faab8e3aecffd2ba815d3b963016fad6b3a3b9b5c010426e0d7f3",
    "transfer_row_id": "n11_i6_context_same_as_n10__proxy_same_as_n10__mild_withdrawal_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 1
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "support_disrupted_but_integration_allowed"
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "e51048bb3f1789a5c40e8b6c02d07143cb6c6084246429d14d9263a951b99a13",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_same_as_n10_reference_row_v1",
        "source_scope": "reference_context"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": false,
        "explicit_restoration_present": false,
        "source_digest": "c1009fd4f7f04a1e42127de5c16fffc3b538d15d64306008edae7fa10e6e929c",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": "support_disrupted_but_integration_allowed",
        "source_row_id": "n11_i5_n09_matched_withdrawal_disrupts_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.7298651821835279
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "n09_matched_withdrawal_disrupts_support",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "0ef3a11ae5207332a4e1fb62305053b1e30c68bcc062f50a4d90771b1bee945d",
    "transfer_row_id": "n11_i6_context_same_as_n10__proxy_same_as_n10__n09_matched_withdrawal_disrupts_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 1
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI4",
    "hidden_steering_used": false,
    "matrix_cell_digest": "942f0aa1d8181d558248bbd1e922d013ec84158295cd1df1487f774e205bd7bf",
    "matrix_interpretation": "Accepted source-backed matrix reference or single-axis row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_same_as_n10_reference_row_v1",
        "source_scope": "reference_context"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": true,
        "source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_explicit_restoration_recovers_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9244958974324687
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "7c0ac3491b59e499ab1ef53f38f3560108ddaea258e0cdcc643851814de31428",
    "transfer_row_id": "n11_i6_context_same_as_n10__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 1
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI4",
    "hidden_steering_used": false,
    "matrix_cell_digest": "2942df74624471b87fadd2b66c0a2ceb991976233b5cca95cc2bb355dca7713e",
    "matrix_interpretation": "Accepted source-backed matrix reference or single-axis row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_same_as_n10_reference_row_v1",
        "source_scope": "reference_context"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_support_intact_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9731535762447039
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "7e3f40df635cc98613a95dd46145c22da4e262373d0b2d7bbf7c84e7fdb219ae",
    "transfer_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__support_intact_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 1
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "ec2565b2dd172374ec6692e374a848ce4250bc619e2e552f88b3c943e6f71924",
    "matrix_interpretation": "Accepted bounded multi-axis transfer row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_same_as_n10_reference_row_v1",
        "source_scope": "reference_context"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_mild_withdrawal_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.8758382186202335
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "22faa60ac06b9691d42db18023eb5a666049a39736e5797f46a35d8ae9a6eb3b",
    "transfer_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__mild_withdrawal_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "support_disrupted_but_integration_allowed"
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "6a5325207455ac6851930acc7bfaefaebced469a58e6722c5e05174bd2e46615",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_same_as_n10_reference_row_v1",
        "source_scope": "reference_context"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": false,
        "explicit_restoration_present": false,
        "source_digest": "c1009fd4f7f04a1e42127de5c16fffc3b538d15d64306008edae7fa10e6e929c",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": "support_disrupted_but_integration_allowed",
        "source_row_id": "n11_i5_n09_matched_withdrawal_disrupts_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.7298651821835279
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "n09_matched_withdrawal_disrupts_support",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "c03ff09f8a59e51b438a537217c37f1cdcbaa7a6e3867df3fcceee79ffb2d05d",
    "transfer_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__n09_matched_withdrawal_disrupts_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "e23e190ef71dfd608b41afdf825d74bdadc996609f92a2ee017095547d34e603",
    "matrix_interpretation": "Accepted bounded multi-axis transfer row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "6cf0494587aca7db1011f604466298ef3f1709de916638079575d25031fdd579",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_same_as_n10_reference_row_v1",
        "source_scope": "reference_context"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": true,
        "source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_explicit_restoration_recovers_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9244958974324687
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "fefcbd6356157bab46b68824c4466264619369ab96910331dbc2d70e5ad01788",
    "transfer_row_id": "n11_i6_context_same_as_n10__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI4",
    "hidden_steering_used": false,
    "matrix_cell_digest": "ed62e5561548c3e03ab297cc8bbaf2fa22eb26ece11c90975af55dd343d16904",
    "matrix_interpretation": "Accepted source-backed matrix reference or single-axis row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
        "source_level": "GALI2",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_route_variant_replay_row_v1",
        "source_scope": "accepted_route_context_variant"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_support_intact_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9731535762447039
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "1a7bb9f87eee52a043c1d4f837a69feb1c4e3f935dcdccc3d34b415f370aeeb1",
    "transfer_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__support_intact_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 1
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "439ad581620a8ac5a30e1d709382b2c2fe6a75aef235f531b1a7bd1725409ac1",
    "matrix_interpretation": "Accepted bounded multi-axis transfer row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
        "source_level": "GALI2",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_route_variant_replay_row_v1",
        "source_scope": "accepted_route_context_variant"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_mild_withdrawal_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.8758382186202335
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "d047d8636dac80485b87f4587258a6de9e7452cdabc5710ece286b84b3756519",
    "transfer_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__mild_withdrawal_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "support_disrupted_but_integration_allowed"
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "126cb802c5e75af809bf3806550b177ca1516ec22c5a7e41e1a8a013f5ceb024",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
        "source_level": "GALI2",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_route_variant_replay_row_v1",
        "source_scope": "accepted_route_context_variant"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": false,
        "explicit_restoration_present": false,
        "source_digest": "c1009fd4f7f04a1e42127de5c16fffc3b538d15d64306008edae7fa10e6e929c",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": "support_disrupted_but_integration_allowed",
        "source_row_id": "n11_i5_n09_matched_withdrawal_disrupts_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.7298651821835279
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "n09_matched_withdrawal_disrupts_support",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "b9ec3e5fc3404db2189a265b1aab8d83d8692696d58c52a435b55de44bbb84de",
    "transfer_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__n09_matched_withdrawal_disrupts_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "ab2699919eab53f491c91c98700c3562fe0f22684f977f2864410309486ba31e",
    "matrix_interpretation": "Accepted bounded multi-axis transfer row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
        "source_level": "GALI2",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_route_variant_replay_row_v1",
        "source_scope": "accepted_route_context_variant"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": true,
        "source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_explicit_restoration_recovers_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9244958974324687
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "1d255b7fcb52da813e9ebb78affeb4c7f7ec963f53f88d59b90d468b7c276d0a",
    "transfer_row_id": "n11_i6_context_route_variant__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "1462bca34371ca7bdc3fcfa772c7eb63e5e990f01599eff553a08c3ce5c8f779",
    "matrix_interpretation": "Accepted bounded multi-axis transfer row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
        "source_level": "GALI2",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_route_variant_replay_row_v1",
        "source_scope": "accepted_route_context_variant"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_support_intact_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9731535762447039
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "68ec2334e8acabcedb0c35138ae456a5bd7debe23a2be9327baa51563451ae0d",
    "transfer_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__support_intact_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "162d9726dff33a31c36f8488d5b757071f8d600476756ac2af4e8aacafa9e4a2",
    "matrix_interpretation": "Accepted bounded multi-axis transfer row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
        "source_level": "GALI2",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_route_variant_replay_row_v1",
        "source_scope": "accepted_route_context_variant"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_mild_withdrawal_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.8758382186202335
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "24cd5d81bab470b951796ddf0b33a043bf2bcf2fea0850e8c91edf94770c80a9",
    "transfer_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__mild_withdrawal_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 3
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "support_disrupted_but_integration_allowed"
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "773028e786051010c340b79d3716309c4db1a3f091d4b930c28649b52aead34e",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
        "source_level": "GALI2",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_route_variant_replay_row_v1",
        "source_scope": "accepted_route_context_variant"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": false,
        "explicit_restoration_present": false,
        "source_digest": "c1009fd4f7f04a1e42127de5c16fffc3b538d15d64306008edae7fa10e6e929c",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": "support_disrupted_but_integration_allowed",
        "source_row_id": "n11_i5_n09_matched_withdrawal_disrupts_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.7298651821835279
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "n09_matched_withdrawal_disrupts_support",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "55523aedc469d822042d1cbf00fabeb07e6dec3c80abd040399e187b0f2a34e2",
    "transfer_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__n09_matched_withdrawal_disrupts_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 3
  },
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [],
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
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "79ec92813dba3defcf5cfd348b4d3a5e88f58884e1d21b842a520ad58c18ac55",
    "matrix_interpretation": "Accepted bounded multi-axis transfer row.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": true,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": true,
        "source_digest": "790437f815a58e834770a68dc125785ef0c8293a6369dde23ce7456959c773d3",
        "source_level": "GALI2",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": null,
        "source_row_id": "n11_i3_context_route_variant_replay_row_v1",
        "source_scope": "accepted_route_context_variant"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": true,
        "source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_explicit_restoration_recovers_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9244958974324687
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": true,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "multi_axis_bounded_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "3bf7ab61dc1599be5410cab7cffd50025fe675544886fd518b9d05eae7a05751",
    "transfer_row_id": "n11_i6_context_route_variant__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 3
  },
  {
    "arc_of_becoming_classification": "local_observation_tag",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "context_arbitration_policy_variant_missing_source"
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
    "context_tag": "context_arbitration_policy_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "418809be5302234cd00822e412fce8e304c85fa1335a62a72b577dc5623e8c87",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": false,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "context_arbitration_policy_variant_missing_source",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": false,
        "source_digest": "72c944986d7bda4618341529e62050cf098e3eb9a6f097a793a52578e8e3a6fb",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": "context_arbitration_policy_variant_missing_source",
        "source_row_id": "n11_i3_context_arbitration_policy_variant_replay_row_v1",
        "source_scope": "blocked_arbitration_policy_variant"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_support_intact_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9731535762447039
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "ecabadfeb0c8a5b97d2e6b39be35c90f47581d0a89081a3488fed8eea803e22d",
    "transfer_row_id": "n11_i6_context_arbitration_policy_variant__proxy_same_as_n10__support_intact_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 1
  },
  {
    "arc_of_becoming_classification": "local_observation_tag",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "context_arbitration_policy_variant_missing_source"
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
    "context_tag": "context_arbitration_policy_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "8d02b703148a4cd20a73345fb2e45d697efba8e2fbc00cbfa98fd759752ff05e",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": false,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "context_arbitration_policy_variant_missing_source",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": false,
        "source_digest": "72c944986d7bda4618341529e62050cf098e3eb9a6f097a793a52578e8e3a6fb",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": "context_arbitration_policy_variant_missing_source",
        "source_row_id": "n11_i3_context_arbitration_policy_variant_replay_row_v1",
        "source_scope": "blocked_arbitration_policy_variant"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_mild_withdrawal_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.8758382186202335
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "2ea9acde4c10096942975eb88682a4a3628de1aa2d471759847720cf37b755cb",
    "transfer_row_id": "n11_i6_context_arbitration_policy_variant__proxy_same_as_n10__mild_withdrawal_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "context_arbitration_policy_variant_missing_source",
      "support_disrupted_but_integration_allowed"
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
    "context_tag": "context_arbitration_policy_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "15e9755b6c177bd7327a10dd620d2ab9c3948c53b4db10137b53e855a80a6b25",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": false,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "context_arbitration_policy_variant_missing_source",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": false,
        "source_digest": "72c944986d7bda4618341529e62050cf098e3eb9a6f097a793a52578e8e3a6fb",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": "context_arbitration_policy_variant_missing_source",
        "source_row_id": "n11_i3_context_arbitration_policy_variant_replay_row_v1",
        "source_scope": "blocked_arbitration_policy_variant"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": false,
        "explicit_restoration_present": false,
        "source_digest": "c1009fd4f7f04a1e42127de5c16fffc3b538d15d64306008edae7fa10e6e929c",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": "support_disrupted_but_integration_allowed",
        "source_row_id": "n11_i5_n09_matched_withdrawal_disrupts_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.7298651821835279
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "n09_matched_withdrawal_disrupts_support",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "b55ef5d19b0c58b9da9fde4c7d50ef85ed384f8c9404505a5af574ec4eeed389",
    "transfer_row_id": "n11_i6_context_arbitration_policy_variant__proxy_same_as_n10__n09_matched_withdrawal_disrupts_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "local_observation_tag",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "context_arbitration_policy_variant_missing_source"
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
    "context_tag": "context_arbitration_policy_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "96b0f8dbd2e26bfd5ea5d590143b6f1d6cc36ad3d775d9fdd5549812200f1cc1",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": false,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "context_arbitration_policy_variant_missing_source",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_same_as_n10",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": false,
        "source_digest": "72c944986d7bda4618341529e62050cf098e3eb9a6f097a793a52578e8e3a6fb",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": "context_arbitration_policy_variant_missing_source",
        "source_row_id": "n11_i3_context_arbitration_policy_variant_replay_row_v1",
        "source_scope": "blocked_arbitration_policy_variant"
      },
      "proxy": {
        "accepted": true,
        "source_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
        "source_level": "GALI1",
        "source_output_digest": "df32344a5dccb1eb58520977052db86f1b40bc37188af8843790cd7715281ac2",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4_same_band_proxy_reference_v1",
        "source_scope": "same_band_reference_proxy_condition",
        "target_band": {
          "lower_bound": 0.45,
          "target_value": 0.5,
          "upper_bound": 0.55
        },
        "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": true,
        "source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_explicit_restoration_recovers_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9244958974324687
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "16d4cdac6e5e4314c7e47bc57fb6e38f78c361d6e7d79ba58e8d7fbdc072c4b5",
    "transfer_row_id": "n11_i6_context_arbitration_policy_variant__proxy_same_as_n10__explicit_restoration_recovers_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "local_observation_tag",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "context_arbitration_policy_variant_missing_source"
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
    "context_tag": "context_arbitration_policy_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "11df608589e2f7d082d90995ef4caa09e8e2952813ab93e97522af9ca50680a4",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": false,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "context_arbitration_policy_variant_missing_source",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": false,
        "source_digest": "72c944986d7bda4618341529e62050cf098e3eb9a6f097a793a52578e8e3a6fb",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": "context_arbitration_policy_variant_missing_source",
        "source_row_id": "n11_i3_context_arbitration_policy_variant_replay_row_v1",
        "source_scope": "blocked_arbitration_policy_variant"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "77894c2a10baa4ab12b0ffafac7dd774f0ffd26a7dcfbfe390e471df07c5ebca",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_support_intact_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9731535762447039
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "c3aeb926f1ca835e28fd7a64f32002d125dc71064b1cab2a5aec80c534e3a99e",
    "transfer_row_id": "n11_i6_context_arbitration_policy_variant__proxy_target_band_variant__support_intact_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 2
  },
  {
    "arc_of_becoming_classification": "local_observation_tag",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "context_arbitration_policy_variant_missing_source"
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
    "context_tag": "context_arbitration_policy_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "56f8b3184ab2b22c0d8fdcb7409b0aff58f85e51267ab3d519ced9d5910d5266",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": false,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "context_arbitration_policy_variant_missing_source",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": false,
        "source_digest": "72c944986d7bda4618341529e62050cf098e3eb9a6f097a793a52578e8e3a6fb",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": "context_arbitration_policy_variant_missing_source",
        "source_row_id": "n11_i3_context_arbitration_policy_variant_replay_row_v1",
        "source_scope": "blocked_arbitration_policy_variant"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": false,
        "source_digest": "59d3b52cc766207775449b5aa8ca3d58aa51d3d77f1fe001905ae1690d1d6ec8",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_mild_withdrawal_survives_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.8758382186202335
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "mild_withdrawal_survives",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "c68854e484b3a2724dd5a3988774d08e0f2a249d8c6650c0f7ff7007c6948eef",
    "transfer_row_id": "n11_i6_context_arbitration_policy_variant__proxy_target_band_variant__mild_withdrawal_survives_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 3
  },
  {
    "arc_of_becoming_classification": "support_dependent_expression",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "context_arbitration_policy_variant_missing_source",
      "support_disrupted_but_integration_allowed"
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
    "context_tag": "context_arbitration_policy_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "ea97e81f038fe178c1aaa2433110b04efb347b78900621ee8ebbaf26aa973162",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": false,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "context_arbitration_policy_variant_missing_source",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": false,
        "source_digest": "72c944986d7bda4618341529e62050cf098e3eb9a6f097a793a52578e8e3a6fb",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": "context_arbitration_policy_variant_missing_source",
        "source_row_id": "n11_i3_context_arbitration_policy_variant_replay_row_v1",
        "source_scope": "blocked_arbitration_policy_variant"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": false,
        "explicit_restoration_present": false,
        "source_digest": "c1009fd4f7f04a1e42127de5c16fffc3b538d15d64306008edae7fa10e6e929c",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": "support_disrupted_but_integration_allowed",
        "source_row_id": "n11_i5_n09_matched_withdrawal_disrupts_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.7298651821835279
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "n09_matched_withdrawal_disrupts_support",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "6d3eb8f37395ccdc59dbacf7f8fdcfad82e8f4f86644b128c85bfda477e8cdbb",
    "transfer_row_id": "n11_i6_context_arbitration_policy_variant__proxy_target_band_variant__n09_matched_withdrawal_disrupts_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 3
  },
  {
    "arc_of_becoming_classification": "local_observation_tag",
    "artifact_only": true,
    "attempted_gali_level": "GALI5",
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
    "blocker_chain": [
      "context_arbitration_policy_variant_missing_source"
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
    "context_tag": "context_arbitration_policy_variant",
    "fixture_lane": {
      "context_tag": "context_route_variant",
      "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
      "hypothesis": "B_generalization_envelope",
      "lane_id": "multi_axis_context_proxy_support_matrix",
      "matrix_spec": {
        "context_variants": [
          "context_same_as_n10",
          "context_route_variant",
          "context_arbitration_policy_variant"
        ],
        "expected_minimum_row_count": 24,
        "matrix_expansion_required": true,
        "proxy_condition_variants": [
          "proxy_same_as_n10",
          "proxy_target_band_variant"
        ],
        "support_state_variants": [
          "support_intact_survives",
          "mild_withdrawal_survives",
          "n09_matched_withdrawal_disrupts_support",
          "explicit_restoration_recovers_support"
        ]
      },
      "planned_iteration": 6,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_variant_new",
      "transfer_axis": "multi_axis"
    },
    "gali_level": "GALI5",
    "hidden_steering_used": false,
    "matrix_cell_digest": "b8460ee7224ffd8136b9b657e924df3bb1f84058e162b6cab8f643dd59352d12",
    "matrix_interpretation": "Blocked matrix row; blocker is inherited from source axis status.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "native_route_arbitration_component_used": false,
    "node_plus_packet_budget_after": null,
    "node_plus_packet_budget_before": null,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": "context_arbitration_policy_variant_missing_source",
    "producer_mediation_classification": "native_policy_gap",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_2_fixture_manifest_validation": "70fc8c4036735e68ab4667c99466614ef44fcf6076f48e4223dccaf9d82026df",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a",
      "n11_iteration_4b_proxy_target_band_variant_probe": "7db81ae8b964883285b471778679639fec24b80eb635332a8e63f50fb65e26f5",
      "n11_iteration_5_support_state_transfer_replay": "f71fcf27f944854b4991d1343ae89175a5782917bdd7e2ad4dee42016025312d"
    },
    "source_artifacts": {
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_2_fixture_manifest_validation": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_2_fixture_manifest_validation.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4b_proxy_target_band_variant_probe.json",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_5_support_state_transfer_replay.json"
    },
    "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
    "source_reports": {
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_3_route_context_transfer_replay.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md",
      "n11_iteration_4b_proxy_target_band_variant_probe": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4b_proxy_target_band_variant_probe.md",
      "n11_iteration_5_support_state_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_5_support_state_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "source_status": {
      "context": {
        "accepted": false,
        "source_digest": "72c944986d7bda4618341529e62050cf098e3eb9a6f097a793a52578e8e3a6fb",
        "source_level": "GALI1",
        "source_output_digest": "301d045090005aac333786d8bad83eae5aba0519522de2f33d89699f5432bfc9",
        "source_primary_blocker": "context_arbitration_policy_variant_missing_source",
        "source_row_id": "n11_i3_context_arbitration_policy_variant_replay_row_v1",
        "source_scope": "blocked_arbitration_policy_variant"
      },
      "proxy": {
        "accepted": true,
        "iteration_4_negative_audit_preserved": true,
        "iteration_4_primary_blocker": "proxy_target_band_variant_missing_source",
        "source_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
        "source_level": "GALI3",
        "source_output_digest": "08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05",
        "source_primary_blocker": null,
        "source_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "source_scope": "accepted_proxy_target_band_variant",
        "target_band": {
          "lower_bound": 0.5,
          "target_value": 0.55,
          "upper_bound": 0.6
        },
        "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab"
      },
      "support": {
        "accepted": true,
        "explicit_restoration_present": true,
        "source_digest": "10f2fb8391f79162caa855a839f09f9fcb879f59ddd33b8c266d0ced0db77b21",
        "source_level": "GALI4",
        "source_output_digest": "14d1fe3decea295a4a9bb5c94b558e49bc7e8a3bdc71b23ad3681572803896d4",
        "source_primary_blocker": null,
        "source_row_id": "n11_i5_explicit_restoration_recovers_support_row_v1",
        "source_scope": "source_current_from_n10_hypothesis_b_matrix",
        "support_retention": 0.9244958974324687
      }
    },
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "explicit_restoration_recovers_support",
    "transfer_accepted": false,
    "transfer_axis": "multi_axis",
    "transfer_outcome_tag": "transfer_blocked",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "de27929e8536c1b34d14d56eb266d446f7be40455dd71e7ea7c4ff01961a1104",
    "transfer_row_id": "n11_i6_context_arbitration_policy_variant__proxy_target_band_variant__explicit_restoration_recovers_support_row_v1",
    "transfer_window_tag": "bounded_repeated_window",
    "variant_axis_count": 3
  }
]
```

## Controls

```json
{
  "budget_surface_ambiguity": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "reason": "Memory, proxy, support, and node-plus-packet budget surfaces remain separate on every row."
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "All matrix rows keep all N11 claim flags false."
  },
  "hidden_experiment_side_steering": {
    "control_passed": true,
    "primary_blocker": "hidden_experiment_side_steering",
    "reason": "Matrix rows are a deterministic cartesian expansion of manifest tags and prior source row status; no report-side route, proxy, or support selection can make a row pass."
  },
  "out_of_envelope_proxy": {
    "control_passed": true,
    "primary_blocker": "out_of_envelope_proxy_blocked",
    "reason": "The only proxy variant admitted is the 4-B declared envelope."
  },
  "stale_context": {
    "control_passed": true,
    "primary_blocker": "stale_context_blocked",
    "reason": "Context status is inherited from Iteration 3 row digests."
  },
  "stale_proxy_state": {
    "control_passed": true,
    "primary_blocker": "stale_proxy_state_blocked",
    "reason": "Proxy status is inherited from Iteration 4 audit and 4-B row digests."
  },
  "stale_support_state": {
    "control_passed": true,
    "primary_blocker": "stale_support_state_blocked",
    "reason": "Support status is inherited from Iteration 5 row digests."
  },
  "support_disrupted_without_restoration": {
    "control_passed": true,
    "primary_blocker": "support_disrupted_but_generalization_allowed",
    "reason": "Rows using disrupted support remain blocked unless explicit restoration is the source support state."
  }
}
```

## Checks

```json
{
  "a7_not_supported": true,
  "accepted_and_blocked_rows_recorded": true,
  "accepted_gali5_rows_present": true,
  "all_claim_flags_false": true,
  "all_controls_passed": true,
  "all_matrix_cell_digests_valid": true,
  "all_required_fields_present": true,
  "all_transfer_row_digests_valid": true,
  "baseline_passed": true,
  "budget_surfaces_separate": true,
  "context_policy_variant_blocked": true,
  "disrupted_support_blocked_for_available_contexts": true,
  "gali7_not_supported": true,
  "iteration_3_passed": true,
  "iteration_4_negative_audit_available": true,
  "iteration_4b_proxy_variant_supported": true,
  "iteration_5_support_matrix_passed": true,
  "manifest_passed": true,
  "matrix_expands_all_context_tags": true,
  "matrix_expands_all_proxy_tags": true,
  "matrix_expands_all_support_tags": true,
  "matrix_lane_present": true,
  "matrix_row_count_matches_expected": true,
  "node_plus_packet_budget_errors_zero": true,
  "source_artifact_digests_present": true,
  "source_status_digest_links_present": true,
  "src_clean_for_iteration_6": true
}
```

## Interpretation

The useful result is the envelope, not a bare true/false. N11 now has
source-backed evidence that route context, proxy target-band variation,
and support-state variation can be composed in accepted bounded rows.
The same matrix also preserves the boundaries that matter: no alternate
arbitration policy exists yet, disrupted support blocks the composition
without restoration, and no row promotes semantic goal ownership,
intention, agency, identity acceptance, A7, or GALI7.

## Acceptance

Iteration 6 passes if the context/proxy/support transfer matrix is source-backed, budget-clean, and claim-clean, with a legible envelope of accepted, downgraded, and blocked rows. The goal is not universal transfer; the goal is a replayable generalization envelope with distinct blockers.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/run_n11_iteration_6_multi_axis_transfer_matrix.py
```

Output digest:

```text
a906f1190f94fea78c10754834f6b3312797280df40c933bd5497a6b0868fd9c
```
