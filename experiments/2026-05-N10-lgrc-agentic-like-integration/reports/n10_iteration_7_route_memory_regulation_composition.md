# N10 Iteration 7 Route-Memory-Regulation Composition

Status: `passed`.

## Result

Iteration 7 composed N06 route-choice evidence, N08 memory/trail
affordance evidence, N07 support-intact evidence, and N09 goal-proxy
regulation evidence into one source-backed artifact-only row.

This is the first ALI4 row. It does not close A6/ALI6 because bounded
repetition and final artifact-only closeout remain assigned to
Iterations 8 and 9.

```text
integration_level = A4
attempted_integration_level = A6
accepted_integration_level = A4
n10_category_level = ALI4
integration_outcome_tag = route_memory_regulation_composition_candidate
route_context_tag = route_context_selection_only
memory_scope_tag = artifact_only_serialized_producer_policy_route_memory_or_trail
support_state_tag = support_intact_survives
artifact_only = true
runtime_state_used = false
```

## Route Evidence

```json
{
  "artifact_only_replay_passed": true,
  "budget_conservation_passed": true,
  "candidate_sets_replayed": true,
  "claim_flags_false": true,
  "context_relations_replayed": true,
  "controls_passed": true,
  "native_arbitration_records_replayed": true,
  "native_selection_replayable_under_selection_only_scope": true,
  "scheduled_processed_packet_evidence_applicability": "not_applicable_pre_topology_selection_only_scope",
  "selected_route_count": 4,
  "selected_routes": [
    "route_a",
    "route_b",
    "route_a",
    "route_b"
  ],
  "selection_causality_basis": "serialized_context_relation_replay_and_native_selection_replay",
  "selection_scope": "selection_only_pre_topology_commit",
  "source_claim_ceiling": "artifact_only_semantic_route_choice_candidate",
  "source_sc_level": "SC6"
}
```

## Memory Evidence

```json
{
  "artifact_only_chain_reconstructed": true,
  "artifact_only_replay_passed": true,
  "claim_flags_scope": "source_memory_or_trail_claim_only_not_n10_agency_claim",
  "corrupted_controls_passed": true,
  "hidden_route_preference_control_passed": true,
  "memory_budget_discontinuity_control_passed": true,
  "memory_or_trail_claim_scope": "artifact_only_serialized_producer_policy_route_memory_or_trail",
  "memory_strength_used_as_physical_flux": false,
  "memory_strength_used_as_score_evidence": true,
  "native_support_status": "experiment_local_artifact_replay",
  "route_a_strength_after_each_cycle": [
    0.5895,
    0.53055,
    0.477495,
    0.4297455
  ],
  "route_b_strength_after_each_cycle": [
    0.88,
    1.0,
    1.0,
    1.0
  ],
  "selected_routes": [
    "route_b",
    "route_b",
    "route_b",
    "route_b"
  ],
  "source_claim_ceiling": "artifact_only_route_memory_or_trail_affordance_candidate",
  "source_controls_replayed": true,
  "source_mem_level": "MEM6",
  "stale_memory_surface_control_passed": true
}
```

## Support Evidence

```json
{
  "final_A_support_retention": 0.9731535762447039,
  "final_basin_separability": 0.9731535762447039,
  "final_budget_error": 0.0,
  "identity_support_outcome_tag": "support_intact_bounded_exchange_reference",
  "lane_digest": "359d248493fc4ce8ee57f5f682d043cc745762671ab1a67fb8c779e38ed67bdb",
  "reference_A_support_retention": 0.9731535762447039,
  "restoration_fraction": 0.0,
  "source_lane_id": "support_intact_reference",
  "support_survival_passed": true,
  "support_survival_threshold": 0.85,
  "withdrawal_depth": 0.0
}
```

## Regulation Evidence

```json
{
  "source_artifact_only_runtime_fallback_blocked": true,
  "source_budget_control_passed": true,
  "source_claim_ceiling": "artifact_only_goal_proxy_regulation_candidate",
  "source_gpr_level": "GPR6",
  "source_hypothesis_a_status": "closed"
}
```

## Boundary

N06 is consumed under `route_context_selection_only`; selected topology
events and scheduled/processed packet evidence are outside the N06
source scope. N08 is consumed as artifact-only serialized
producer-policy memory/trail evidence, not as pure native geometry
memory, ACO behavior, or agency.

```text
budget_mode = source_artifact_budget_compatibility_not_single_runtime_continuity
node_plus_packet_budget_error = 0.0
a6_relevance = route_memory_regulation_composition_component_not_a6_closeout
```

## Controls

```json
{
  "artifact_only_replay_missing_link": {
    "control_passed": true,
    "primary_blocker": "artifact_only_replay_missing_link",
    "reason": "all four source links are present and replay remains artifact-only"
  },
  "budget_surface_ambiguity": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "reason": "Iteration 7 claims source-artifact budget compatibility only, while route, memory, support, and proxy budget surfaces remain separate"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "ALI4 composition cannot emit ACO, agency, A6, identity acceptance, or goal-ownership claims"
  },
  "hidden_experiment_side_steering": {
    "control_passed": true,
    "primary_blocker": "hidden_experiment_side_steering",
    "reason": "route selection and memory-shaped scoring are source-backed replay evidence, not N10 report-side if/else steering"
  },
  "missing_goal_proxy_regulation_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_goal_proxy_regulation_artifact",
    "reason": "ALI4 composition requires N09 GPR closeout evidence"
  },
  "missing_identity_support_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_identity_support_artifact",
    "reason": "ALI4 composition requires N07 support baseline evidence"
  },
  "missing_memory_affordance_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_memory_affordance_artifact",
    "reason": "ALI4 composition requires the N08 Hypothesis A MEM6 closeout"
  },
  "missing_route_choice_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_route_choice_artifact",
    "reason": "ALI4 composition requires the N06 route-choice closeout"
  },
  "source_artifact_digest_mismatch": {
    "control_passed": true,
    "primary_blocker": "source_artifact_digest_mismatch",
    "reason": "N06/N07/N08/N09 source artifact digests are rechecked against Iteration 1"
  },
  "stale_identity_support_baseline": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "support state is read from the current N07 support-intact lane and matched against the N10 manifest summary"
  },
  "stale_memory_surface": {
    "control_passed": true,
    "primary_blocker": "stale_memory_surface",
    "reason": "N08 memory surface is consumed only as serialized artifact-only producer-policy memory evidence"
  },
  "stale_route_context": {
    "control_passed": true,
    "primary_blocker": "stale_route_context",
    "reason": "N06 route evidence is consumed only under its declared selection-only pre-topology scope"
  }
}
```

## Checks

```json
{
  "a6_not_supported_by_iteration_7": true,
  "ali3_support_sensitive_precondition_available": true,
  "all_four_source_links_present": true,
  "artifact_only_replay": true,
  "attempted_a6_not_accepted": true,
  "claim_flags_all_false": true,
  "controls_passed": true,
  "fixture_required_route_context_tag_matched": true,
  "fixture_required_support_state_tag_matched": true,
  "integration_allowed_true": true,
  "integration_level_is_a4_not_a6": true,
  "integration_row_digest_valid": true,
  "integration_row_required_fields_present": true,
  "memory_artifact_only_chain_reconstructed": true,
  "memory_mem6_available": true,
  "memory_not_physical_flux": true,
  "memory_scope_preserved": true,
  "memory_scope_tag_is_artifact_only_policy": true,
  "n09_goal_proxy_candidate_available": true,
  "n09_gpr6_available": true,
  "n10_category_level_is_ali4": true,
  "positive_integration_row_emitted": true,
  "route_context_tag_is_selection_only": true,
  "route_native_selection_replayable": true,
  "route_sc6_available": true,
  "route_selection_scope_preserved": true,
  "source_artifact_digests_match_baseline": true,
  "src_clean_for_iteration_7": true,
  "support_intact_lane_survives": true,
  "support_lane_budget_error_zero": true,
  "support_state_tag_is_support_intact": true
}
```

## Acceptance

Iteration 7 passes if N10 can compose route choice, memory/trail affordance, identity/support evidence, and goal-proxy regulation into one replayable source-backed row while rejecting hidden route labels, hidden memory surfaces, stale context, budget ambiguity, and claim promotion.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_7_route_memory_regulation_composition.py
```

Output digest:

```text
a00715cbf8f004340a9223f011cbdc6c89345a6a134cdb0d87da58b32e5aa020
```
