# N14 Route Consequence Records

Status: `passed`.

## Acceptance State

```text
accepted_route_consequence_records_no_selection
```

## Interpretation

```json
{
  "acceptance_state": "accepted_route_consequence_records_no_selection",
  "next_required_step": "Apply a deterministic selection rule in Iteration 4 and test whether the recorded consequence vector, not immediate affordance alone, determines the selected route.",
  "plain_language_interpretation": "Iteration 3 builds the consequence records that Iteration 4 can use for route selection. N06 immediate affordance favors route_a, while a serialized, memory-dominant consequence score derived from N08 memory deltas ranks route_b higher. N09/N13 support and regulation evidence is source-compatible but not route-specific in this iteration. The conflict is recorded, but it is not resolved by a selection rule yet.",
  "record_id": "n14_i3_interpretation_route_consequence_records_v1",
  "supported_interpretation": "N14 now has source-backed, pre-selection consequence records for the route_a/route_b candidate set, including an explicit affordance-versus-consequence conflict.",
  "unsupported_interpretations": [
    "selected route by consequence",
    "AP4 consequence-sensitive selection support",
    "intention",
    "agency",
    "semantic choice",
    "semantic goal ownership",
    "identity acceptance",
    "native support",
    "fully native integration"
  ]
}
```

## Candidate Set

```json
{
  "affordance_consequence_conflict_present": true,
  "affordance_consequence_conflict_resolved": false,
  "candidate_set_digest": "cc28d581e856d3782a840c63157f7b1d4d565387e8c00ed28b8365cba7b5f4a9",
  "consequence_score_policy": {
    "claim_boundary": "artifact-local consequence ordering only; not utility, intention, semantic choice, goal ownership, agency, or native support",
    "components": {
      "budget_penalty_component": "0.0 when pinned budget surfaces are present; budget-invalid variants are deferred to Iteration 5 controls",
      "memory_delta_component": "N08 memory_strength_end - memory_strength_start from the pinned MEM6 replay window",
      "route_specific_regulation_component": "0.0 unless a route-specific regulation effect is source-backed; Iteration 3 has source-compatible regulation evidence but no route-specific regulation consequence",
      "route_specific_support_component": "0.0 unless a route-specific support effect is source-backed; Iteration 3 has source-compatible support evidence but no route-specific support consequence"
    },
    "policy_id": "n14_i3_memory_dominant_consequence_score_v1",
    "score_direction": "higher_is_better"
  },
  "consequence_signal_scope": "memory_dominant_provisional_candidate; support and regulation sources are compatible but not route-specific in Iteration 3",
  "consequence_top_route": "route_b",
  "eligible_candidate_set_id": "native-route-candidate-set:2eb3d1248ced33eb4f89aa22ad208b39",
  "eligible_routes": [
    "route_a",
    "route_b"
  ],
  "immediate_affordance_top_route": "route_a",
  "missing_consequence_records": [],
  "records_present_for_all_eligible_routes": true,
  "selection_deferred_to_iteration_4": true
}
```

## Consequence Score Policy

```json
{
  "claim_boundary": "artifact-local consequence ordering only; not utility, intention, semantic choice, goal ownership, agency, or native support",
  "components": {
    "budget_penalty_component": "0.0 when pinned budget surfaces are present; budget-invalid variants are deferred to Iteration 5 controls",
    "memory_delta_component": "N08 memory_strength_end - memory_strength_start from the pinned MEM6 replay window",
    "route_specific_regulation_component": "0.0 unless a route-specific regulation effect is source-backed; Iteration 3 has source-compatible regulation evidence but no route-specific regulation consequence",
    "route_specific_support_component": "0.0 unless a route-specific support effect is source-backed; Iteration 3 has source-compatible support evidence but no route-specific support consequence"
  },
  "policy_id": "n14_i3_memory_dominant_consequence_score_v1",
  "score_direction": "higher_is_better"
}
```

## Route Records

| Route | Immediate rank | Consequence score | Consequence rank | Selected rank | Conflict resolved |
| --- | ---: | ---: | ---: | --- | --- |
| `route_a` | 1 | -0.1597545 | 2 | `not_selected_until_iteration_4` | `false` |
| `route_b` | 2 | 0.12 | 1 | `not_selected_until_iteration_4` | `false` |

Iteration 3 records candidate consequences before N14 selection.
The rank is derived from serialized memory-dominant score
components. Support and regulation sources are compatible inputs
but are not route-specific consequence evidence in this iteration.
Iteration 3 does not assign a selected route, does not resolve the
affordance/consequence conflict, and does not support final `AP4`.

## Checks

```json
{
  "affordance_consequence_conflict_not_resolved_yet": true,
  "affordance_consequence_conflict_present": true,
  "bounded_consequence_horizon_present": true,
  "budget_cost_surface_present": true,
  "candidate_set_complete": true,
  "claim_flags_forced_false": true,
  "consequence_rank_derived_from_score_components": true,
  "consequence_rank_recorded": true,
  "consequence_score_components_serialized": true,
  "derivation_policy_declared": true,
  "hidden_outcome_table_not_used": true,
  "immediate_affordance_rank_recorded": true,
  "inventory_source_passed": true,
  "memory_dominant_scope_recorded": true,
  "native_supported_flags_false": true,
  "no_final_ap4_supported": true,
  "no_selected_route_claim": true,
  "observed_downstream_effect_present": true,
  "phase8_opened_false": true,
  "post_hoc_scoring_not_used": true,
  "prediction_basis_declared": true,
  "prediction_match_status_present": true,
  "records_pre_selection": true,
  "records_satisfy_schema": true,
  "route_consequence_record_count": true,
  "runtime_state_used_false": true,
  "schema_source_passed": true,
  "source_references_pinned": true,
  "source_window_declared": true,
  "src_diff_empty": true,
  "support_memory_regulation_descriptors_present": true
}
```

## Claim Boundary

```text
route consequence record != selected route
affordance/consequence conflict present != conflict resolved
pre-selection consequence records != intention
source-backed support effect != semantic goal ownership
N14 Iteration 3 != AP4 closeout
artifact-level route consequence record != native support
```

## Output Digest

```text
9eef9c0bbcfd64004915259964ddcbb39efb32563fec5975a6bb30684d83d253
```
