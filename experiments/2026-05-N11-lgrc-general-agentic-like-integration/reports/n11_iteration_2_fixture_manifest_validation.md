# N11 Iteration 2 Generalization Schema And Fixture Manifest

Status: `passed`.

## Result

Iteration 2 froze the N11 transfer schema and fixture manifest before
any positive generalization probe. The manifest is contract-only; it
does not support A7 or GALI7 by itself.

```text
positive generalization probe run = false
A7 supported by Iteration 2 = false
GALI7 supported by Iteration 2 = false
runtime state used = false
claim promotion allowed = false
```

## Manifest

- path: `experiments/2026-05-N11-lgrc-general-agentic-like-integration/configs/n11_generalization_fixture_manifest_v1.json`
- manifest digest: `1ca7ab5eb6946a0e3eb00fc7dea974d8fcbc89439211b356282a0e02da303459`
- manifest SHA-256: `967faefd00559334e506d44976b2327594a165e8adbca796a0332f89609d3e99`

## Frozen GALI Ladder

```json
{
  "GALI0": "no_generalization",
  "GALI1": "source_backed_transfer_inventory",
  "GALI2": "single_axis_context_transfer",
  "GALI3": "proxy_condition_transfer",
  "GALI4": "support_state_transfer",
  "GALI5": "multi_axis_bounded_transfer",
  "GALI6": "longer_horizon_generalization_candidate",
  "GALI7": "broader_general_artifact_only_agentic_like_integration_candidate"
}
```

## Frozen Tags

```json
{
  "arc_of_becoming_classification": [
    "local_observation_tag",
    "reusable_becoming_class",
    "probe_supported_capacity",
    "support_dependent_expression",
    "endogenous_precondition_candidate",
    "native_regime_expression",
    "not_applicable"
  ],
  "context_tag": [
    "context_same_as_n10",
    "context_route_variant",
    "context_arbitration_policy_variant",
    "context_source_scope_variant",
    "context_out_of_scope",
    "context_stale",
    "context_hidden",
    "context_not_applicable"
  ],
  "gali_level": [
    "GALI0",
    "GALI1",
    "GALI2",
    "GALI3",
    "GALI4",
    "GALI5",
    "GALI6",
    "GALI7"
  ],
  "producer_mediation_classification": [
    "producer_mediated",
    "threshold_authorized",
    "native_route_arbitrated",
    "constitutive_native",
    "native_policy_gap",
    "not_applicable"
  ],
  "proxy_condition_tag": [
    "proxy_same_as_n10",
    "proxy_target_band_variant",
    "proxy_perturbation_envelope_variant",
    "proxy_measurement_surface_variant",
    "proxy_out_of_envelope",
    "proxy_stale",
    "proxy_hidden",
    "proxy_not_applicable"
  ],
  "source_scope_tag": [
    "n10_bounded_artifact_only_source",
    "n10_support_sensitive_source",
    "n10_native_contract_handoff_source",
    "source_scope_out_of_bounds",
    "source_scope_stale"
  ],
  "support_state_tag": [
    "support_intact_survives",
    "mild_withdrawal_survives",
    "n09_matched_withdrawal_disrupts_support",
    "explicit_restoration_recovers_support",
    "support_variant_new",
    "support_state_stale",
    "support_state_out_of_scope",
    "support_state_not_applicable"
  ],
  "transfer_axis": [
    "inventory",
    "context",
    "proxy",
    "support",
    "multi_axis",
    "longer_horizon",
    "controls",
    "artifact_validator",
    "native_gap"
  ],
  "transfer_outcome_tag": [
    "no_transfer",
    "bookkeeping_only_transfer",
    "single_axis_context_transfer_candidate",
    "proxy_condition_transfer_candidate",
    "support_state_transfer_candidate",
    "multi_axis_bounded_transfer_candidate",
    "longer_horizon_generalization_candidate",
    "broader_general_artifact_only_agentic_like_integration_candidate",
    "transfer_blocked"
  ],
  "transfer_window_tag": [
    "inventory_only",
    "single_replay_window",
    "bounded_repeated_window",
    "longer_horizon_window",
    "out_of_window",
    "not_applicable"
  ]
}
```

## Fixture Lanes

```json
[
  {
    "context_tag": "context_same_as_n10",
    "expected_role": "reference_replay_before_context_variation",
    "hypothesis": "A_artifact_only_generalization",
    "lane_id": "context_same_as_n10_reference",
    "planned_iteration": 3,
    "proxy_condition_tag": "proxy_same_as_n10",
    "support_state_tag": "support_intact_survives",
    "transfer_axis": "context"
  },
  {
    "context_tag": "context_route_variant",
    "expected_role": "single_axis_context_transfer_candidate_or_blocked",
    "hypothesis": "A_artifact_only_generalization",
    "lane_id": "context_route_variant_replay",
    "planned_iteration": 3,
    "proxy_condition_tag": "proxy_same_as_n10",
    "support_state_tag": "support_intact_survives",
    "transfer_axis": "context"
  },
  {
    "context_tag": "context_arbitration_policy_variant",
    "expected_role": "arbitration_policy_context_transfer_candidate_or_blocked",
    "hypothesis": "A_artifact_only_generalization",
    "lane_id": "context_arbitration_policy_variant_replay",
    "planned_iteration": 3,
    "proxy_condition_tag": "proxy_same_as_n10",
    "support_state_tag": "support_intact_survives",
    "transfer_axis": "context"
  },
  {
    "context_tag": "context_same_as_n10",
    "expected_role": "proxy_condition_transfer_candidate_or_blocked",
    "hypothesis": "A_artifact_only_generalization",
    "lane_id": "proxy_target_band_variant_replay",
    "planned_iteration": 4,
    "proxy_condition_tag": "proxy_target_band_variant",
    "support_state_tag": "support_intact_survives",
    "transfer_axis": "proxy"
  },
  {
    "context_tag": "context_same_as_n10",
    "expected_role": "support_state_transfer_candidate_or_blocked",
    "hypothesis": "B_generalization_envelope",
    "lane_id": "support_state_transfer_matrix",
    "matrix_states": [
      "support_intact_survives",
      "mild_withdrawal_survives",
      "n09_matched_withdrawal_disrupts_support",
      "explicit_restoration_recovers_support"
    ],
    "planned_iteration": 5,
    "proxy_condition_tag": "proxy_same_as_n10",
    "support_state_tag": "support_variant_new",
    "transfer_axis": "support"
  },
  {
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
  {
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
  {
    "context_tag": "context_hidden",
    "expected_role": "distinct_fail_closed_controls",
    "hypothesis": "A_B_claim_boundary",
    "is_control_lane": true,
    "lane_id": "hidden_stale_out_of_envelope_claim_controls",
    "planned_iteration": 8,
    "proxy_condition_tag": "proxy_out_of_envelope",
    "support_state_tag": "support_state_stale",
    "transfer_axis": "controls"
  },
  {
    "context_tag": "context_not_applicable",
    "expected_role": "artifact_only_replay_validator",
    "hypothesis": "A_B_replay_validator",
    "lane_id": "artifact_only_generalization_validator",
    "planned_iteration": 9,
    "proxy_condition_tag": "proxy_not_applicable",
    "support_state_tag": "support_state_not_applicable",
    "transfer_axis": "artifact_validator"
  }
]
```

## Matrix And Window Specs

Support-state matrix:

```json
{
  "coverage_required_in_iteration_5": true,
  "disrupted_support_must_block_without_restoration": true,
  "explicit_restoration_must_preserve_disruption_history": true,
  "matrix_states": [
    "support_intact_survives",
    "mild_withdrawal_survives",
    "n09_matched_withdrawal_disrupts_support",
    "explicit_restoration_recovers_support"
  ]
}
```

Multi-axis matrix:

```json
{
  "context_variants": [
    "context_same_as_n10",
    "context_route_variant",
    "context_arbitration_policy_variant"
  ],
  "expected_minimum_row_count": 24,
  "matrix_expansion_required_in_iteration_6": true,
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
}
```

Longer-horizon window:

```json
{
  "minimum_extended_window_count": 8,
  "pass_fail_alone_sufficient": false,
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
```

Artifact-validator architecture:

```json
{
  "required_passes": [
    "source_artifact_digest_pass",
    "transfer_row_schema_pass",
    "context_proxy_support_matrix_pass",
    "longer_horizon_window_pass",
    "negative_control_pass",
    "budget_surface_pass",
    "claim_boundary_pass"
  ],
  "runtime_state_used": false,
  "validator_shape": "single_script_with_separate_validation_passes"
}
```

## Negative Control Contract

```json
{
  "a7_by_inheritance": "a7_by_inheritance_blocked",
  "budget_surface_ambiguity": "budget_surface_ambiguity",
  "claim_promotion_fields": "claim_promotion_blocked",
  "gali7_by_inheritance": "gali7_by_inheritance_blocked",
  "hidden_context_substitution": "hidden_context_substitution_blocked",
  "hidden_experiment_side_steering": "hidden_experiment_side_steering",
  "missing_n10_closeout_artifact": "missing_n10_closeout_artifact",
  "native_relabel_without_phase8": "native_relabel_without_phase8_blocked",
  "node_plus_packet_budget_discontinuity": "node_plus_packet_budget_discontinuity",
  "out_of_envelope_proxy": "out_of_envelope_proxy_blocked",
  "restoration_required_but_missing": "restoration_required_but_missing",
  "source_artifact_digest_mismatch": "source_artifact_digest_mismatch",
  "stale_context": "stale_context_blocked",
  "stale_proxy_state": "stale_proxy_state_blocked",
  "stale_support_state": "stale_support_state_blocked",
  "support_disrupted_but_generalization_allowed": "support_disrupted_but_generalization_allowed"
}
```

## Schema Validation

```json
{
  "exemplar_row_is_evidence": false,
  "exemplar_row_valid": true,
  "lane_tag_checks": [
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    true
  ],
  "missing_required_fields": []
}
```

## Checks

```json
{
  "a7_by_inheritance_rejected": true,
  "a7_not_supported_by_iteration_2": true,
  "arc_of_becoming_classifications_frozen": true,
  "artifact_validator_architecture_declared": true,
  "artifact_validator_lane_declared": true,
  "baseline_inventory_digest_pinned": true,
  "claim_flags_all_false": true,
  "claim_promotion_fields_rejected": true,
  "context_arbitration_policy_variant_lane_declared": true,
  "context_tags_frozen": true,
  "context_transfer_lane_declared": true,
  "control_blockers_frozen": true,
  "control_lane_declared": true,
  "exemplar_is_not_evidence": true,
  "fixture_lane_tags_valid": true,
  "fixture_lanes_cover_iterations_3_to_9": true,
  "gali7_by_inheritance_rejected": true,
  "gali7_not_supported_by_iteration_2": true,
  "gali_ladder_frozen": true,
  "longer_horizon_lane_declared": true,
  "longer_horizon_window_spec_declared": true,
  "manifest_digest_present": true,
  "missing_n10_closeout_rejected": true,
  "multi_axis_lane_declared": true,
  "multi_axis_matrix_spec_declared": true,
  "negative_control_contract_covers_required_controls": true,
  "no_positive_probe_run": true,
  "producer_mediation_classifications_frozen": true,
  "proxy_condition_tags_frozen": true,
  "proxy_transfer_lane_declared": true,
  "source_artifact_digests_validate": true,
  "source_scope_tags_frozen": true,
  "src_clean_for_iteration_2": true,
  "support_state_tags_frozen": true,
  "support_transfer_lane_declared": true,
  "support_transfer_matrix_states_declared": true,
  "transfer_outcome_tags_frozen": true,
  "transfer_row_required_fields_complete": true,
  "transfer_window_tags_frozen": true
}
```

## Acceptance

Iteration 2 passes if the N11 generalization schema and fixture manifest are frozen before any transfer probe, and the manifest validates source artifacts, tags, controls, and claim boundaries without producing positive evidence.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/build_n11_iteration_2_fixture_manifest.py
```

Validation digest:

```text
0b5db686ece0f0aa4a22f17470de32acc5c183afe8f15dbfdebb116a608b1018
```
