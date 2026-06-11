# N08 Iteration 9 Native Geometry Trail Baseline

Status: `passed`.

Iteration 9 starts Hypothesis B and freezes the native geometry-mediated trail
question before any native trail probe. It inventories available native
LGRC geometry/topology/support mechanisms and records blockers without using
`memory_strength`, memory-shaped scoring, hidden route preference, or claim
promotion.

## Baseline Decision

- Hypothesis A remains closed at:
  `artifact_only_route_memory_or_trail_affordance_candidate`
- Hypothesis B status:
  `open_not_claimed`
- Hypothesis B current blocker:
  `native_geometry_mediated_trail_not_tested_before_iteration_9`
- Preferred Iteration 10 probe:
  `edge_split_or_inserted_node_topology_trace`
- Iteration 10 entry allowed:
  `True`

## Mechanism Inventory

| Mechanism | Availability | Usable I10 | Usable I11 | Blocker | Notes |
|---|---|---:|---:|---|---|
| `committed_topology_event` | `available_as_runtime_support` | `True` | `None` | `None` | Topology events can exist as declared runtime events, but a native trail still requires proving route-use-created geometry/topology trace formation. |
| `edge_split_or_inserted_node` | `candidate_design_available_over_topology_events` | `True` | `None` | `None` | This is the preferred first Hypothesis B probe because it can avoid an independent memory scalar and use declared topology. |
| `surface_lineage_transport` | `available_as_runtime_support` | `True` | `None` | `None` | Surface lineage is support infrastructure only. It does not itself create route memory. |
| `topology_state_reabsorption` | `available_as_runtime_support` | `True` | `None` | `None` | Required if the geometry trail changes topology and later packet work crosses the changed substrate. |
| `time_scoped_lineage_replay` | `available_as_artifact_replay_support` | `True` | `None` | `None` | Useful for artifact replay if multiple route-use or topology events are later chained. |
| `native_route_arbitration` | `available_as_runtime_support` | `None` | `True` | `None` | May be used to observe future routing response, but Iteration 11 must reject score-only memory inputs. |
| `declared_node_or_edge_geometry_parameter_change` | `not_confirmed_in_current_n08_sources` | `False` | `None` | `declared_geometry_parameter_update_not_inventory_confirmed` | Do not assume custom conductance or geometry parameters are available as serialized native policy fields. |
| `support_shape_or_local_coupling_geometry_change` | `not_confirmed_in_current_n08_sources` | `False` | `None` | `support_shape_update_policy_not_inventory_confirmed` | This remains attractive for a pure RC trail, but Iteration 9 does not find a source-backed native support-shape update contract. |
| `packet_or_loop_residue_visible_in_existing_state` | `not_yet_demonstrated_as_route_memory` | `False` | `None` | `packet_loop_residue_route_memory_not_demonstrated` | Existing packet/loop machinery exists, but N08 has not shown a residue that changes routing without score memory. |
| `route_conductance_memory_metric` | `blocked` | `False` | `None` | `native_route_conductance_memory_policy_missing` | Do not smuggle Hypothesis A memory_strength into native geometry by renaming it conductance. |

## Iteration 10 Guardrails

Must not use:

```json
[
  "memory_strength",
  "memory_shaped_candidate_score",
  "hidden_route_preference",
  "report_side_route_history",
  "unserialized_geometry_state"
]
```

Required controls:

```json
[
  "missing_route_use_event",
  "missing_geometry_or_topology_event",
  "hidden_scalar_memory",
  "stale_geometry_read",
  "budget_drift",
  "unsupported_topology_mutation",
  "claim_promotion"
]
```

## Claim Boundary

All Iteration 9 claim flags remain false. The narrow Hypothesis A
`memory_or_trail_claim_allowed` does not transfer to Hypothesis B.

```json
{
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
  "native_geometry_mediated_trail_claim_allowed": false,
  "personhood_claim_allowed": false,
  "pure_coherence_flux_trail_claim_allowed": false,
  "rc_identity_collapse_claim_allowed": false,
  "runtime_identity_acceptance_claim_allowed": false,
  "semantic_choice_claim_allowed": false,
  "unrestricted_identity_claim_allowed": false,
  "unrestricted_movement_claim_allowed": false
}
```

## Checks

| Check | Passed |
|---|---|
| `all_claim_flags_false` | `True` |
| `committed_topology_event_available` | `True` |
| `edge_split_inserted_node_candidate_available` | `True` |
| `geometry_parameter_update_not_confirmed` | `True` |
| `hypothesis_a_closeout_passed` | `True` |
| `hypothesis_b_separate_from_iterations_1_8` | `True` |
| `iteration_10_entry_gate_defined` | `True` |
| `no_memory_shaped_scoring_in_iteration_9` | `True` |
| `no_memory_strength_in_native_entry_gate` | `True` |
| `no_new_probe_run` | `True` |
| `route_conductance_memory_policy_blocked` | `True` |
| `src_clean` | `True` |
| `support_shape_update_not_confirmed` | `True` |
| `surface_lineage_available` | `True` |
| `topology_state_reabsorption_available` | `True` |

## Acceptance

Iteration 9 passes if the native geometry-mediated trail question is frozen
with a source-backed inventory of available LGRC geometry/topology/support
mechanisms and explicit blockers, without using `memory_strength`, hidden route
preference, memory-shaped scoring, or claim promotion.

Achieved: `True`.

Output digest: `ac57b1dd11a603ded02fe12446cb3826862d93b252a60358729da1c65346fd95`.
