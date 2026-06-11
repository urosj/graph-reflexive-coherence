# N08 Iteration 6 MEM4 Memory-Shaped Route Arbitration

Status: `passed`.

Iteration 6 tests Hypothesis A only: serialized producer/policy memory becomes
candidate-score evidence. It does not claim pure coherence/flux memory, native
geometry-mediated trail memory, ACO, agency, or biological pheromone behavior.

## Branch Question

Can serialized MEM3 trail state become route-arbitration evidence without hidden memory inputs?

## Branch Answer

Without memory components, route candidates tie and deterministic ordering
selects `route_a`. With serialized MEM3
memory components, route arbitration selects `route_b`.

```json
{
  "changed": true,
  "with_memory": "route_b",
  "without_memory": "route_a"
}
```

The memory score delta is `0.0995`.

## Arc-of-Becoming Interpretation

This report treats pass/fail as a gate, not as the whole result.

- expressed property:
  `memory_shaped_route_selection_candidate`
- naturalization rung:
  `Nat3_score_operational_artifact_surface`
- affordance status:
  `operational_as_score_evidence_only`

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
| `counterfactual_tie_selects_order_key` | `counterfactual_selected_route` | `route_a` | Without memory components, both candidates have equal score and deterministic order selects route_a. |
| `memory_components_select_stronger_trace` | `memory_shaped_selected_route` | `route_b` | With serialized memory components, route_b wins because its MEM3 strength and recency score are higher. |
| `selected_route_delta_observed` | `selected_route_delta` | `{'without_memory': 'route_a', 'with_memory': 'route_b'}` | The selected route changes only when memory-derived score components are included. |
| `memory_score_delta_serialized` | `route_b_minus_route_a_memory_score_delta` | `0.0995` | The score delta is replayable from serialized MEM3 surface fields, not fixture-side route preference. |

Cultivation next question:

Can repeated route-use, memory update, and memory-shaped arbitration cycles remain replayable without hidden steering or budget drift?

## Candidate Scores

| Lane | Route | Score | Candidate Digest | Components |
|---|---|---:|---|---|
| `n08_mem4_counterfactual_without_memory_component` | `route_a` | `0` | `bec628c9779ac5817dafbf89d98369a13eb778fe199840c9efa5a1cc8b9c3472` | `{}` |
| `n08_mem4_counterfactual_without_memory_component` | `route_b` | `0` | `6f80bea69e673bc39d40953e9257f8e7aa5871c0c12fecd10785c733524ddd0c` | `{}` |
| `n08_mem4_memory_shaped_arbitration` | `route_a` | `0.8455` | `af55b2f9ed867ed75a3c828934c684853733853805adeecf2d22d9a0ed9b14df` | `{"memory_decay_adjusted_strength": 0.0405, "memory_recency_weight": 0.05, "memory_surface_digest_match": 0.1, "memory_trail_strength": 0.655}` |
| `n08_mem4_memory_shaped_arbitration` | `route_b` | `0.945` | `e856d8fb1fe78aa972d784f9e4041ee6617b10db1d24b19aac0930d977b2bdd7` | `{"memory_decay_adjusted_strength": 0.045, "memory_recency_weight": 0.1, "memory_surface_digest_match": 0.1, "memory_trail_strength": 0.7}` |

## Counterfactual Lane

```json
{
  "arbitration_reason_code": "native_route_arbitration_selected_declared_order_tiebreak",
  "arbitration_rule": "highest_score_then_candidate_order_key",
  "arbitration_runtime_visible_inputs": [
    "candidate_route_score",
    "candidate_order_key",
    "candidate_set_order_key",
    "candidate_score_components",
    "counterfactual_without_memory_component"
  ],
  "arbitration_score": 0,
  "artifact_kind": "lgrc9v3_native_route_arbitration_record",
  "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
  "candidate_set_digest": "6960657b8233d70f972bb3eca04e0f32e02bd280df4e16fe4aee1eb8534e16c6",
  "candidate_set_id": "n08-native-route-candidate-set:n08_mem4_counterfactual_without_memory_component",
  "causal_layer_mode": "topology_changing_causal_history",
  "claim_ceiling": "mem4_memory_shaped_route_selection_candidate",
  "claim_flags": {
    "aco_like_claim_allowed": false,
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
    "runtime_identity_acceptance_claim_allowed": false,
    "semantic_choice_claim_allowed": false,
    "unrestricted_identity_claim_allowed": false,
    "unrestricted_movement_claim_allowed": false
  },
  "event_time_key": 6.1,
  "evidence_class": "memory_shaped_route_arbitration",
  "experiment": "N08",
  "hypothesis": "A_serialized_producer_policy_memory",
  "idempotency_key": "c046974f3d4d0277b5a3b96a2df45bf44e50b0a724bf1711f99d69f8224070c1",
  "lane_id": "n08_mem4_counterfactual_without_memory_component",
  "lane_kind": "counterfactual_without_memory_component",
  "lgrc_runtime_level": "lgrc3",
  "mem_level": "MEM4",
  "mem_level_is_evidence_classification": true,
  "native_route_arbitration_digest": "fc86e61b4e81e4d311832a495eb086ce9139cd4a66f66976dec090d4c37caac8",
  "native_route_arbitration_enabled": true,
  "native_route_arbitration_policy_id": "score_ordered_topology_route_candidates",
  "native_route_arbitration_record_id": "n08-native-route-arbitration:n08_mem4_counterfactual_without_memory_component:route_a",
  "packet_scheduled": false,
  "rejected_candidate_route_digests": [
    "6f80bea69e673bc39d40953e9257f8e7aa5871c0c12fecd10785c733524ddd0c"
  ],
  "runtime_family": "LGRC9V3",
  "scheduler_event_index": 45,
  "schema_version": "lgrc9v3_native_route_arbitration_record_v1",
  "selected_candidate_route_digest": "bec628c9779ac5817dafbf89d98369a13eb778fe199840c9efa5a1cc8b9c3472",
  "selected_candidate_route_id": "route_a",
  "selected_topology_event_digest": null,
  "selected_topology_event_id": null,
  "state_mutated": false,
  "topology_event_committed": false
}
```

## Memory-Shaped Lane

```json
{
  "arbitration_reason_code": "native_route_arbitration_selected_highest_score",
  "arbitration_rule": "highest_score_then_candidate_order_key",
  "arbitration_runtime_visible_inputs": [
    "candidate_route_score",
    "candidate_order_key",
    "candidate_set_order_key",
    "candidate_score_components",
    "memory_surface_digest:b21c093d70245fab02088b8ebed42ac931629c41f6e45d618f5b5a67d9bea627",
    "memory_surface_state_snapshot_digest:284cf90a485db74c28e0d5e8c90cc3aceb4aac1f6073f4d9c1a0fade35623209"
  ],
  "arbitration_score": 0.945,
  "artifact_kind": "lgrc9v3_native_route_arbitration_record",
  "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
  "candidate_set_digest": "4fcb1a43c3849912ed121caec4bd68ec57484e35dd6c6f93da9cb3153700b896",
  "candidate_set_id": "n08-native-route-candidate-set:n08_mem4_memory_shaped_arbitration",
  "causal_layer_mode": "topology_changing_causal_history",
  "claim_ceiling": "mem4_memory_shaped_route_selection_candidate",
  "claim_flags": {
    "aco_like_claim_allowed": false,
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
    "runtime_identity_acceptance_claim_allowed": false,
    "semantic_choice_claim_allowed": false,
    "unrestricted_identity_claim_allowed": false,
    "unrestricted_movement_claim_allowed": false
  },
  "event_time_key": 6.3,
  "evidence_class": "memory_shaped_route_arbitration",
  "experiment": "N08",
  "hypothesis": "A_serialized_producer_policy_memory",
  "idempotency_key": "e57e4852b8c733cc2927f80663a9e2979c3186803c97dd1288f6ca3869b121d5",
  "lane_id": "n08_mem4_memory_shaped_arbitration",
  "lane_kind": "memory_shaped_arbitration",
  "lgrc_runtime_level": "lgrc3",
  "mem_level": "MEM4",
  "mem_level_is_evidence_classification": true,
  "native_route_arbitration_digest": "de7100ef762ab666835dac8bd6d64c14f3f7733d00c656743bc3d0a53b14f9bf",
  "native_route_arbitration_enabled": true,
  "native_route_arbitration_policy_id": "score_ordered_topology_route_candidates",
  "native_route_arbitration_record_id": "n08-native-route-arbitration:n08_mem4_memory_shaped_arbitration:route_b",
  "packet_scheduled": false,
  "rejected_candidate_route_digests": [
    "af55b2f9ed867ed75a3c828934c684853733853805adeecf2d22d9a0ed9b14df"
  ],
  "runtime_family": "LGRC9V3",
  "scheduler_event_index": 55,
  "schema_version": "lgrc9v3_native_route_arbitration_record_v1",
  "selected_candidate_route_digest": "e856d8fb1fe78aa972d784f9e4041ee6617b10db1d24b19aac0930d977b2bdd7",
  "selected_candidate_route_id": "route_b",
  "selected_topology_event_digest": null,
  "selected_topology_event_id": null,
  "state_mutated": false,
  "topology_event_committed": false
}
```

## Hypothesis Boundary

```json
{
  "hypothesis": "A_serialized_producer_policy_memory",
  "hypothesis_b_remains_open": true,
  "independent_memory_strength_used_as_physical_flux": false,
  "independent_memory_strength_used_as_score_evidence": true,
  "native_geometry_mediated_trail_path": false,
  "native_geometry_trail_claimed": false,
  "pure_coherence_flux_trail_claimed": false,
  "serialized_memory_policy_path": true
}
```

## Producer / Step Boundary

```json
{
  "primary_blocker": "producer_mutation_boundary_violation",
  "producer_may_mutate_memory_surface": false,
  "producer_may_mutate_node_coherence": false,
  "producer_may_mutate_packet_ledger": false,
  "producer_scheduling_allowed": true,
  "step_remains_packet_mutation_boundary": true
}
```

## Inherited Native Policy Blockers

```json
[
  "native_route_conductance_memory_policy_missing",
  "native_trail_memory_surface_missing",
  "native_memory_surface_serialization_policy_missing",
  "native_memory_surface_keying_policy_missing",
  "native_memory_budget_accounting_policy_missing",
  "native_memory_cross_cycle_persistence_policy_missing",
  "native_memory_decay_policy_missing",
  "native_memory_reinforcement_policy_missing",
  "native_memory_candidate_score_component_semantics_missing",
  "native_memory_artifact_replay_validator_missing"
]
```

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
| `candidate_score_memory_digest_missing` | `blocked` | `candidate_score_memory_digest_missing` | `True` | Reject memory score components without a memory surface digest. |
| `candidate_score_hidden_memory_input` | `blocked` | `candidate_score_hidden_memory_input` | `True` | Reject memory score inputs not serialized as runtime-visible fields. |
| `stale_memory_surface_read` | `blocked` | `stale_memory_surface_read` | `True` | Reject candidate scoring against a stale MEM2 surface digest. |
| `arbitration_memory_order_invalid` | `blocked` | `arbitration_memory_order_invalid` | `True` | Reject candidate scoring before the MEM3 memory update row. |
| `memory_budget_discontinuity` | `blocked` | `memory_budget_discontinuity` | `True` | Reject memory-shaped scoring from invalid memory budget rows. |
| `node_plus_packet_budget_discontinuity` | `blocked` | `node_plus_packet_budget_discontinuity` | `True` | Reject memory-shaped scoring that hides physical budget drift. |
| `no_memory_surface_read_by_arbitration` | `blocked` | `no_memory_surface_read_by_arbitration` | `True` | Reject MEM4 claim if arbitration does not read memory evidence. |
| `claim_promotion` | `blocked` | `claim_promotion` | `True` | Reject MEM4 promotion to memory claim, ACO, agency, or movement. |

## Checks

| Check | Passed |
|---|---|
| `arc_interpretation_present` | `True` |
| `arc_not_endpoint_only` | `True` |
| `candidate_budget_predictions_exact` | `True` |
| `candidate_route_digests_recompute` | `True` |
| `candidate_scores_equal_component_sums` | `True` |
| `candidate_set_digests_recompute` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_distinct` | `True` |
| `controls_passed` | `True` |
| `controls_present` | `True` |
| `counterfactual_has_no_memory_components` | `True` |
| `counterfactual_selected_route_a` | `True` |
| `hypothesis_a_only_no_native_geometry_claim` | `True` |
| `memory_candidate_components_allowed` | `True` |
| `memory_candidate_order_after_mem3` | `True` |
| `memory_claim_still_closed` | `True` |
| `memory_runtime_inputs_cite_source_mem3_digest` | `True` |
| `memory_runtime_inputs_include_required_fields` | `True` |
| `memory_score_delta_positive` | `True` |
| `memory_shaped_selected_route_b` | `True` |
| `memory_surface_read_by_arbitration` | `True` |
| `native_memory_still_experiment_local` | `True` |
| `no_topology_or_packet_side_effects` | `True` |
| `producer_step_boundary_preserved` | `True` |
| `route_arbitration_digests_recompute` | `True` |
| `selected_route_delta_recorded` | `True` |
| `source_manifest_passed` | `True` |
| `source_mem3_passed` | `True` |
| `src_clean` | `True` |

## Artifact Digests

```json
{
  "arc_interpretation_digest": "4cbf9ef6faf9383f948b18101a0bf129cf3e00e5a43eae4f20916e3065525ee7",
  "checks_digest": "3e1631b965951352a5f238e5399ef2caf5d88f891c915f608e57ec238c095c84",
  "controls_digest": "f6f7301589c2e3e2a8d06fdeaaa904001c85bc73c51ba9545ccdd46670c06dfc",
  "counterfactual_lane_digest": "6402c1f4c73c0fdc569455d463fb255624b03e6844f01b3680df2c1f5efa994c",
  "memory_shaped_lane_digest": "0ef2545b508d9cbc2551dd538468a747489de31fffa511821613516f8c0f7116"
}
```

## Acceptance

Iteration 6 passes if memory surface state changes candidate-route evidence and
native route arbitration selects according to serialized memory-derived score
components.

Achieved: `True`.

Output digest: `f154865ec31bcd2187b777682cb58269d2845c92d981e1196507cb53a08d6cc5`.
