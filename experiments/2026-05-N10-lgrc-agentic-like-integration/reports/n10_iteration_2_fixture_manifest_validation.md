# N10 Iteration 2 Integration Schema And Fixture Manifest

Status: `passed`.

## Result

Iteration 2 froze the N10 integration contract before any positive
integration probe. The manifest is contract-only and does not support
A6 by itself.

```text
positive integration probe run = false
A6 supported by Iteration 2 = false
runtime state used = false
claim promotion allowed = false
```

## Manifest

- path: `experiments/2026-05-N10-lgrc-agentic-like-integration/configs/n10_integration_fixture_manifest_v1.json`
- manifest digest: `8fbcba8838098bee67585f42554452d782e3b8d5f50bf184bc8bd35db91cd638`
- manifest SHA-256: `55536ce1c244a966a5f927f55c2f41f7e787a18728ee76b543f86e36a7bececd`

## Frozen Tags

N10 category ladder:

```json
{
  "ALI0": "no_integration_inventory_schema_or_external_juxtaposition_only",
  "ALI1": "source_backed_bookkeeping_composition_schema_valid_no_causal_replay",
  "ALI2": "support_aware_regulation_replay",
  "ALI3": "support_sensitive_regulation_with_disruption_and_restoration_controls",
  "ALI4": "route_memory_regulation_composition",
  "ALI5": "bounded_repeated_integration",
  "ALI6": "bounded_artifact_only_agentic_like_integration_candidate"
}
```

Support-state tags:

```json
[
  "support_intact_survives",
  "mild_withdrawal_survives",
  "n09_matched_withdrawal_disrupts_support",
  "explicit_restoration_recovers_support",
  "support_state_not_applicable"
]
```

Integration outcome tags:

```json
[
  "bookkeeping_only",
  "support_aware_regulation_candidate",
  "memory_shaped_support_aware_regulation_candidate",
  "route_memory_regulation_composition_candidate",
  "support_disruption_blocked_integration",
  "restoration_gated_integration_candidate",
  "bounded_artifact_only_agentic_like_integration_candidate",
  "native_policy_gap"
]
```

## Fixture Lanes

```json
[
  {
    "expected_role": "support_aware_regulation_candidate",
    "hypothesis": "A_with_B_support_gate",
    "lane_id": "support_intact_regulation_replay",
    "planned_iteration": 3,
    "required_support_state_tag": "support_intact_survives",
    "source_support_lane_id": "support_intact_reference"
  },
  {
    "expected_role": "support_aware_regulation_candidate_or_downgrade",
    "hypothesis": "B_support_sensitivity",
    "lane_id": "mild_withdrawal_survival_replay",
    "planned_iteration": 4,
    "required_support_state_tag": "mild_withdrawal_survives",
    "source_support_lane_id": "mild_support_weakening"
  },
  {
    "expected_role": "support_disruption_blocked_integration",
    "hypothesis": "B_support_sensitivity",
    "lane_id": "disrupted_support_control",
    "planned_iteration": 5,
    "required_support_state_tag": "n09_matched_withdrawal_disrupts_support",
    "source_support_lane_id": "n09_matched_partial_support_withdrawal"
  },
  {
    "expected_role": "restoration_gated_integration_candidate",
    "hypothesis": "B_support_sensitivity",
    "lane_id": "explicit_restoration_replay",
    "planned_iteration": 6,
    "required_support_state_tag": "explicit_restoration_recovers_support",
    "source_support_lane_id": "restored_after_n09_partial_withdrawal"
  },
  {
    "expected_role": "route_memory_regulation_composition_candidate",
    "hypothesis": "A_bounded_artifact_only_integration",
    "lane_id": "route_memory_regulation_composition",
    "planned_iteration": 7,
    "required_route_context_tag": "route_context_selection_only",
    "required_support_state_tag": "support_intact_survives",
    "route_context_constraint": "N06_SC6_is_selection_only_pre_topology_scope",
    "source_support_lane_id": "support_intact_reference"
  },
  {
    "expected_role": "bounded_artifact_only_agentic_like_integration_candidate",
    "hypothesis": "A_bounded_artifact_only_integration",
    "lane_id": "bounded_repeated_integration",
    "planned_iteration": 8,
    "required_route_context_tag": "route_context_selection_only",
    "required_support_state_tag": "support_intact_survives",
    "route_context_constraint": "N06_SC6_is_selection_only_pre_topology_scope",
    "source_support_lane_id": "support_intact_reference"
  },
  {
    "expected_role": "bounded_repeated_integration_a5_relevant_companion_or_downgrade",
    "hypothesis": "A_with_B_support_gate_a5_companion",
    "lane_id": "bounded_repeated_integration_mild_withdrawal_companion",
    "planned_iteration": 8,
    "required_route_context_tag": "route_context_selection_only",
    "required_support_state_tag": "mild_withdrawal_survives",
    "route_context_constraint": "N06_SC6_is_selection_only_pre_topology_scope",
    "source_support_lane_id": "mild_support_weakening"
  }
]
```

## Control Blockers

```json
{
  "agency_overclaim": "agency_overclaim_blocked",
  "artifact_only_replay_missing_link": "artifact_only_replay_missing_link",
  "budget_surface_ambiguity": "budget_surface_ambiguity",
  "claim_promotion": "claim_promotion_blocked",
  "hidden_experiment_side_steering": "hidden_experiment_side_steering",
  "missing_goal_proxy_regulation_artifact": "missing_goal_proxy_regulation_artifact",
  "missing_identity_support_artifact": "missing_identity_support_artifact",
  "missing_memory_affordance_artifact": "missing_memory_affordance_artifact",
  "missing_route_choice_artifact": "missing_route_choice_artifact",
  "node_plus_packet_budget_discontinuity": "node_plus_packet_budget_discontinuity",
  "producer_direct_mutation": "producer_direct_mutation_blocked",
  "restoration_required_but_missing": "restoration_required_but_missing",
  "source_artifact_digest_mismatch": "source_artifact_digest_mismatch",
  "stale_identity_support_baseline": "stale_identity_support_baseline",
  "stale_memory_surface": "stale_memory_surface",
  "stale_route_context": "stale_route_context",
  "support_disrupted_but_integration_allowed": "support_disrupted_but_integration_allowed"
}
```

## Schema Validation

```json
{
  "exemplar_row_is_evidence": false,
  "exemplar_row_valid": true,
  "invalid_controls": {
    "budget_surface_ambiguity": "budget_surface_ambiguity",
    "claim_promotion": "claim_promotion_blocked",
    "hidden_experiment_side_steering": "hidden_experiment_side_steering",
    "missing_goal_proxy_regulation_artifact": "missing_goal_proxy_regulation_artifact",
    "missing_identity_support_artifact": "missing_identity_support_artifact",
    "missing_memory_affordance_artifact": "missing_memory_affordance_artifact",
    "missing_route_choice_artifact": "missing_route_choice_artifact",
    "restoration_required_but_missing": "restoration_required_but_missing",
    "source_artifact_digest_mismatch": "source_artifact_digest_mismatch",
    "support_disrupted_but_integration_allowed": "support_disrupted_but_integration_allowed"
  },
  "missing_required_fields": []
}
```

## Checks

```json
{
  "a5_mild_withdrawal_companion_lane_declared": true,
  "a6_not_supported_by_iteration_2": true,
  "all_required_controls_declared": true,
  "baseline_inventory_digest_pinned": true,
  "budget_extraction_spec_declared": true,
  "claim_flags_all_false": true,
  "control_blockers_frozen": true,
  "cross_artifact_budget_continuity_not_claimed": true,
  "exemplar_is_not_evidence": true,
  "explicit_restoration_lane_declared": true,
  "fixture_lanes_cover_iterations_3_to_8": true,
  "integration_outcome_tags_frozen": true,
  "integration_row_required_fields_complete": true,
  "manifest_digest_present": true,
  "memory_scope_tags_frozen": true,
  "n06_selection_only_constraint_declared_for_full_composition": true,
  "n10_category_ladder_frozen": true,
  "no_positive_probe_run": true,
  "regulation_scope_tags_frozen": true,
  "route_context_tags_frozen": true,
  "source_artifact_digests_validate": true,
  "src_clean_for_iteration_2": true,
  "support_disruption_lane_declared": true,
  "support_state_tags_frozen": true
}
```

## Acceptance

Iteration 2 passes if the N10 integration schema and fixture manifest are frozen before positive integration runs. The schema must keep evidence levels, support tags, budget surfaces, source provenance, and claim flags separate, and must reject missing source artifacts or claim-promotion fields.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/build_n10_iteration_2_fixture_manifest.py
```

Validation digest:

```text
bd0bba250e6f46eb522668eef039dae327e03801772aac89c479e0a1d78f0375
```
