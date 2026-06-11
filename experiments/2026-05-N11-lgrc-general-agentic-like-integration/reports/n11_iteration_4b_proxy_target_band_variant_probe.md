# N11 Iteration 4-B Proxy Target-Band Variant Probe

Status: `passed`.

## Result

Iteration 4-B keeps Iteration 4's negative source audit intact, then
adds a new declared proxy target-band variant. The variant shifts the
N09 source band by +0.05 while preserving the same regulated variable,
same proxy measurement surface, and same band width. The N09-style
producer-mediated correction returned the proxy into the variant band
across four bounded windows.

Current proxy-axis state:

```text
GALI3 proxy-condition transfer = supported
strongest_claim_ceiling = proxy_condition_transfer_candidate
semantic_goal_ownership_claim_allowed = false
intention_claim_allowed = false
agency_claim_allowed = false
A7/GALI7 supported = false
```

## Target Bands

```json
{
  "baseline_target_band": {
    "event_time_key": 0.0,
    "lower_bound": 0.45,
    "regulated_variable_id": "source_reservoir_node_coherence",
    "regulated_variable_surface": "active_node_state",
    "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
    "target_band_id": "n09_i3_source_reservoir_target_band_v1",
    "target_band_policy_digest": "f8bedb4cd5680a9b2bc482f4260473fa0795ecc466409b82c4c8595eef4ce53a",
    "target_band_policy_id": "n09_static_declared_band_policy_v1",
    "target_kind": "closed_interval",
    "target_value": 0.5,
    "tolerance": 1e-09,
    "unit": "coherence",
    "upper_bound": 0.55
  },
  "variant_target_band": {
    "baseline_target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
    "event_time_key": 0.0,
    "lower_bound": 0.5,
    "regulated_variable_id": "source_reservoir_node_coherence",
    "regulated_variable_surface": "active_node_state",
    "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
    "target_band_id": "n11_i4b_source_reservoir_target_band_variant_v1",
    "target_band_policy_digest": "5c7a9dbe8a26e5a4bae1ccc38afc4cbbf02acf9a662848916d8eefe7ae2855ea",
    "target_band_policy_id": "n11_i4b_declared_shifted_band_policy_v1",
    "target_kind": "closed_interval",
    "target_value": 0.55,
    "tolerance": 1e-09,
    "unit": "coherence",
    "upper_bound": 0.6,
    "variant_declared_before_execution": true,
    "variant_envelope": {
      "declared_before_execution": true,
      "max_abs_target_shift": 0.05,
      "same_band_width_required": true,
      "same_proxy_measurement_surface_required": true,
      "same_regulated_variable_required": true
    }
  }
}
```

## Probe Summary

```json
{
  "all_corrections_step_processed": true,
  "all_cycles_returned_to_variant_band": true,
  "all_cycles_started_out_of_variant_band": true,
  "correction_amounts": [
    0.02,
    0.07,
    0.07,
    0.07
  ],
  "cycle_count": 4,
  "node_plus_packet_budget_error_max": 0.0,
  "post_measurements": [
    0.6,
    0.6,
    0.6,
    0.6
  ],
  "pre_measurements": [
    0.62,
    0.67,
    0.67,
    0.67
  ],
  "producer_direct_mutation_used": false,
  "window_input_amount": 0.07
}
```

## Transfer Row

```json
[
  {
    "arc_of_becoming_classification": "probe_supported_capacity",
    "artifact_only": true,
    "attempted_gali_level": "GALI3",
    "baseline_target_band": {
      "event_time_key": 0.0,
      "lower_bound": 0.45,
      "regulated_variable_id": "source_reservoir_node_coherence",
      "regulated_variable_surface": "active_node_state",
      "target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
      "target_band_id": "n09_i3_source_reservoir_target_band_v1",
      "target_band_policy_digest": "f8bedb4cd5680a9b2bc482f4260473fa0795ecc466409b82c4c8595eef4ce53a",
      "target_band_policy_id": "n09_static_declared_band_policy_v1",
      "target_kind": "closed_interval",
      "target_value": 0.5,
      "tolerance": 1e-09,
      "unit": "coherence",
      "upper_bound": 0.55
    },
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
      "context_tag": "context_same_as_n10",
      "expected_role": "proxy_condition_transfer_candidate_or_blocked",
      "hypothesis": "A_artifact_only_generalization",
      "lane_id": "proxy_target_band_variant_replay",
      "planned_iteration": 4,
      "proxy_condition_tag": "proxy_target_band_variant",
      "support_state_tag": "support_intact_survives",
      "transfer_axis": "proxy"
    },
    "gali_level": "GALI3",
    "goal_proxy_not_goal_ownership": true,
    "hidden_steering_used": false,
    "interpretation": "A shifted proxy target band was declared before execution and given its own digest. The N09-style producer-mediated packet correction returned the proxy to the variant band across four windows with exact node-plus-packet budget conservation. This supports scoped GALI3 proxy-condition transfer without goal ownership, intention, agency, A7, or GALI7 claims.",
    "memory_budget_surface": "n10_source_memory_budget_compatibility",
    "native_policy_gap": [
      "native_agentic_like_integration_policy_missing",
      "native_goal_proxy_regulation_policy_missing",
      "native_identity_acceptance_validator_missing",
      "native_response_magnitude_policy_missing_for_unbounded_perturbations",
      "native_route_conductance_memory_policy_missing"
    ],
    "node_plus_packet_budget_after": 1.5,
    "node_plus_packet_budget_before": 1.5,
    "node_plus_packet_budget_error": 0.0,
    "primary_blocker": null,
    "producer_mediation_classification": "producer_mediated",
    "producer_scaffold_used": true,
    "proxy_budget_surface": "active_node_coherence_band",
    "proxy_condition_tag": "proxy_target_band_variant",
    "runtime_state_used": false,
    "source_artifact_digests": {
      "n09_fixture_manifest": "e8ac646605f8524e344f378ae060bb6c25420c6701024f8802a7972e77d59c45",
      "n09_gpr1_proxy_measurement": "29a3ea964ef38f1eae1be1b5d420453a5119c02dde6e5174328341ddd2c7df15",
      "n09_gpr3_proxy_conditioned_eligibility": "7d31f6d593cc43ec15223292cb70e8981a503b17276a1f0f9a2823a1850b5242",
      "n09_gpr5_repeated_bounded_regulation": "0aa631930ff59776764fd3147285669eb006942ee656e27b1b748dbe3e2bf483",
      "n09_gpr6_closeout": "f2023e4b3aa456ac7aa301494b25e4a190226260fb90adc1c292182dccee3b68",
      "n10_route_memory_regulation_composition": "11027db3a40f9a13358fde937579890a888f255fa6a4375f04169d63fe219ea2",
      "n11_baseline_inventory": "e736ae2b0c8a4475be7b053e5d278d14c4ddb8ab74aa14fd480d223b667b2b70",
      "n11_fixture_manifest": "967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99",
      "n11_iteration_3_route_context_transfer_replay": "badddb1b9c08c92bf6efa64a31c2a50c0019bceac008d40fcdb471ebc8c5817d",
      "n11_iteration_4_proxy_condition_transfer_replay": "6ebc8d832cf58fd071ab7587a6abf4585075d0eee6842b98a90dfa32cf9fb70a"
    },
    "source_artifacts": {
      "n09_fixture_manifest": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/configs/n09_fixture_manifest_v1.json",
      "n09_gpr1_proxy_measurement": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_3_gpr1_proxy_measurement.json",
      "n09_gpr3_proxy_conditioned_eligibility": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_5_gpr3_proxy_conditioned_eligibility.json",
      "n09_gpr5_repeated_bounded_regulation": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_7_gpr5_repeated_bounded_regulation.json",
      "n09_gpr6_closeout": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_9_gpr6_closeout.json",
      "n10_route_memory_regulation_composition": "experiments/2026-05-N10-lgrc-agentic-like-integration/outputs/n10_iteration_7_route_memory_regulation_composition.json",
      "n11_baseline_inventory": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_1_baseline_inventory.json",
      "n11_fixture_manifest": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json",
      "n11_iteration_3_route_context_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_3_route_context_transfer_replay.json",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_4_proxy_condition_transfer_replay.json"
    },
    "source_boundary": "N10_iteration_15_closeout",
    "source_reports": {
      "n09_gpr1_proxy_measurement": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/n09_iteration_3_gpr1_proxy_measurement.md",
      "n09_gpr3_proxy_conditioned_eligibility": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/n09_iteration_5_gpr3_proxy_conditioned_eligibility.md",
      "n09_gpr5_repeated_bounded_regulation": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/n09_iteration_7_gpr5_repeated_bounded_regulation.md",
      "n09_gpr6_closeout": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/n09_iteration_9_gpr6_closeout.md",
      "n10_route_memory_regulation_composition": "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/n10_iteration_7_route_memory_regulation_composition.md",
      "n11_iteration_4_proxy_condition_transfer_replay": "experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_4_proxy_condition_transfer_replay.md"
    },
    "source_scope_tag": "n10_bounded_artifact_only_source",
    "support_budget_surface": "n10_source_support_budget_compatibility",
    "support_state_tag": "support_intact_survives",
    "transfer_accepted": true,
    "transfer_axis": "proxy",
    "transfer_outcome_tag": "proxy_condition_transfer_candidate",
    "transfer_policy_digest": "cba8d2b5af612e8263d6b2d6fd3cc81a148afdd538a61c4424621248c82155bd",
    "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
    "transfer_row_digest": "6fc4b8aab4c950b65fe1ef2a515df6c7fd81195963b51e1f1689454c4a6a9a8b",
    "transfer_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
    "transfer_window_tag": "bounded_four_cycle_variant_probe",
    "variant_probe_runtime_used_to_generate_artifacts": true,
    "variant_probe_summary": {
      "all_corrections_step_processed": true,
      "all_cycles_returned_to_variant_band": true,
      "all_cycles_started_out_of_variant_band": true,
      "correction_amounts": [
        0.02,
        0.07,
        0.07,
        0.07
      ],
      "cycle_count": 4,
      "node_plus_packet_budget_error_max": 0.0,
      "post_measurements": [
        0.6,
        0.6,
        0.6,
        0.6
      ],
      "pre_measurements": [
        0.62,
        0.67,
        0.67,
        0.67
      ],
      "producer_direct_mutation_used": false,
      "window_input_amount": 0.07
    },
    "variant_target_band": {
      "baseline_target_band_digest": "72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b",
      "event_time_key": 0.0,
      "lower_bound": 0.5,
      "regulated_variable_id": "source_reservoir_node_coherence",
      "regulated_variable_surface": "active_node_state",
      "target_band_digest": "b75b2e4b1f069bc0fb9f0e798529542e8b9fa1138821a2d62e35fbca9e3a21ab",
      "target_band_id": "n11_i4b_source_reservoir_target_band_variant_v1",
      "target_band_policy_digest": "5c7a9dbe8a26e5a4bae1ccc38afc4cbbf02acf9a662848916d8eefe7ae2855ea",
      "target_band_policy_id": "n11_i4b_declared_shifted_band_policy_v1",
      "target_kind": "closed_interval",
      "target_value": 0.55,
      "tolerance": 1e-09,
      "unit": "coherence",
      "upper_bound": 0.6,
      "variant_declared_before_execution": true,
      "variant_envelope": {
        "declared_before_execution": true,
        "max_abs_target_shift": 0.05,
        "same_band_width_required": true,
        "same_proxy_measurement_surface_required": true,
        "same_regulated_variable_required": true
      }
    }
  }
]
```

## Controls

```json
{
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "All claim flags remain false."
  },
  "hidden_proxy_target_substitution": {
    "control_passed": true,
    "primary_blocker": "hidden_proxy_target_substitution_blocked",
    "reason": "The variant target band is serialized and digested before cycles run."
  },
  "iteration_4_negative_boundary_preserved": {
    "control_passed": true,
    "primary_blocker": "proxy_target_band_variant_missing_source",
    "reason": "Iteration 4 remains the source-audit negative result; 4-B adds new variant evidence instead of rewriting it."
  },
  "out_of_envelope_proxy_target": {
    "control_passed": true,
    "primary_blocker": "out_of_envelope_proxy_blocked",
    "reason": "The variant preserves the same width and shifts bounds by +0.05."
  },
  "semantic_goal_ownership_relabeling": {
    "control_passed": true,
    "primary_blocker": "goal_proxy_relabelled_as_goal_ownership",
    "reason": "The result remains goal-proxy regulation only."
  },
  "stale_proxy_state": {
    "control_passed": true,
    "primary_blocker": "stale_proxy_state_blocked",
    "reason": "Every cycle links proxy surface digests to current packet ledger digests."
  }
}
```

## Checks

```json
{
  "a7_not_supported": true,
  "all_claim_flags_false": true,
  "all_controls_passed": true,
  "all_corrections_step_processed": true,
  "all_cycles_returned_to_variant_band": true,
  "all_cycles_started_out_of_variant_band": true,
  "all_required_fields_present": true,
  "all_transfer_row_digests_valid": true,
  "baseline_passed": true,
  "gali7_not_supported": true,
  "iteration_3_passed": true,
  "iteration_4_negative_boundary_preserved": true,
  "manifest_passed": true,
  "n09_gpr6_available": true,
  "n10_regulation_source_gpr6_available": true,
  "node_plus_packet_budget_error_zero": true,
  "producer_direct_mutation_not_used": true,
  "proxy_fixture_lane_reused": true,
  "same_proxy_measurement_surface": true,
  "src_clean_for_iteration_4b": true,
  "target_band_declared_before_execution": true,
  "target_band_digest_changed": true,
  "target_band_shift_within_envelope": true,
  "target_band_width_preserved": true,
  "transfer_row_accepted_as_gali3": true
}
```

## Interpretation

This is a proxy-condition transfer result, not a semantic-goal result.
The system is still using a producer-mediated regulation scaffold, and
the target band is an explicit artifact policy. What changed is source
coverage: unlike Iteration 4, 4-B now has a committed target-band
variant digest and packet-processed response evidence. That supports
scoped GALI3 without native goal ownership, intention, agency, A7, or
GALI7 claims.

## Acceptance

Iteration 4-B passes if a proxy target-band variant is declared before execution, receives a distinct target-band digest, stays within the declared proxy envelope, returns to band across bounded producer-mediated packet cycles, preserves separated budgets, and does not promote goal ownership, intention, agency, A7, or GALI7.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/run_n11_iteration_4b_proxy_target_band_variant_probe.py
```

Output digest:

```text
08925d575181c5206eacc2541712d953ce2d2c2d4e303770f5c23d96319c7a05
```
