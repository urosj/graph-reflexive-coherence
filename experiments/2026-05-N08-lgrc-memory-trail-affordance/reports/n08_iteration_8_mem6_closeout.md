# N08 Iteration 8 MEM6 Artifact-Only Replay And Closeout

Status: `passed`.

Iteration 8 replays the Iteration 7 route-use, memory update, candidate-score,
candidate-set, and route-arbitration chain from exported artifacts only. It
does not run a new behavioral probe and does not use private runtime state.

## Closeout

- strongest supported MEM level: `MEM6`
- strongest claim ceiling: `artifact_only_route_memory_or_trail_affordance_candidate`
- narrow memory/trail claim allowed:
  `True`
- claim scope: `artifact_only_serialized_producer_policy_route_memory_or_trail`
- Hypothesis B status: `open_not_claimed`
- Hypothesis B blocker: `native_geometry_mediated_trail_not_tested_in_iterations_1_8`

The supported claim is only an artifact-only serialized producer/policy
route-memory or trail-affordance candidate. It is not native geometry-mediated
trail memory, pure coherence/flux memory, ACO, agency, intention,
goal-proxy regulation, locomotion, biological behavior, personhood, semantic
choice, identity collapse, or identity acceptance.

## Artifact-Only Replay

```json
{
  "artifact_only": true,
  "candidate_route_records_replayed": 8,
  "candidate_set_records_replayed": 4,
  "chain_reconstructed": true,
  "memory_surface_update_rows_replayed": 8,
  "processed_packet_records_applicable": false,
  "processed_packet_records_replayed": 0,
  "replay_summary_digest": "de7d2d550abb384221a1d4e4f14721cb3d0303f4484bfd04c65aff3d12bd76e9",
  "replayed_mem_level": "MEM6",
  "route_a_strength_after_each_cycle": [
    0.5895,
    0.53055,
    0.477495,
    0.4297455
  ],
  "route_arbitration_records_replayed": 4,
  "route_b_strength_after_each_cycle": [
    0.88,
    1.0,
    1.0,
    1.0
  ],
  "route_use_events_replayed": 4,
  "runtime_state_used": false,
  "scheduled_packet_records_applicable": false,
  "scheduled_packet_records_replayed": 0,
  "selected_routes": [
    "route_b",
    "route_b",
    "route_b",
    "route_b"
  ],
  "serialized_state_replay_scope": "route-use events, memory surface rows, candidate records, candidate set records, native route-arbitration records, controls",
  "source_iteration": 7,
  "source_mem_level": "MEM5",
  "trend_summary_replayed": {
    "competing_memory_behavior": "route_b_converges_to_saturation_while_route_a_decays_without_reinforcement",
    "oscillation_observed": false,
    "route_a_extinction_trend_observed": true,
    "route_a_floor_reached": false,
    "route_a_strength_after_each_cycle": [
      0.5895,
      0.53055,
      0.477495,
      0.4297455
    ],
    "route_b_saturation_observed": true,
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
    "tie_observed": false
  }
}
```

## Source Control Replay

| Control | Expected Blocker | Observed Blocker | Passed |
|---|---|---|---|
| `repeated_hidden_route_preference` | `candidate_score_hidden_memory_input` | `candidate_score_hidden_memory_input` | `True` |
| `stale_memory_surface_read` | `stale_memory_surface_read` | `stale_memory_surface_read` | `True` |
| `duplicate_memory_update` | `duplicate_memory_update` | `duplicate_memory_update` | `True` |
| `cross_cycle_memory_leak` | `cross_cycle_memory_leak` | `cross_cycle_memory_leak` | `True` |
| `memory_budget_discontinuity` | `memory_budget_discontinuity` | `memory_budget_discontinuity` | `True` |
| `node_plus_packet_budget_discontinuity` | `node_plus_packet_budget_discontinuity` | `node_plus_packet_budget_discontinuity` | `True` |
| `claim_promotion` | `claim_promotion` | `claim_promotion` | `True` |

## Corrupted Artifact Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
| `missing_route_use_event` | `blocked` | `missing_route_use_event` | `True` | Remove the committed route-use event from cycle 0. |
| `memory_surface_digest_mismatch` | `blocked` | `memory_surface_digest_mismatch` | `True` | Change a memory row strength without updating its digest. |
| `memory_state_reconstruction_mismatch` | `blocked` | `memory_state_reconstruction_mismatch` | `True` | Corrupt reconstructed memory_state_after for route A. |
| `score_component_mismatch` | `blocked` | `score_component_mismatch` | `True` | Alter a candidate route score away from its component sum. |
| `event_order_inversion` | `blocked` | `event_order_inversion` | `True` | Move a route-use event before arbitration in scheduler order. |
| `stale_memory_read` | `blocked` | `stale_memory_read` | `True` | Make cycle 1 read route A memory from the pre-cycle-0 surface. |
| `duplicate_update` | `blocked` | `duplicate_update` | `True` | Duplicate a memory update row in cycle 0. |
| `memory_budget_discontinuity` | `blocked` | `memory_budget_discontinuity` | `True` | Change a memory budget after value without matching the equation. |
| `claim_promotion` | `blocked` | `claim_promotion` | `True` | Inject an agency claim into a candidate row. |

## Checks

| Check | Passed |
|---|---|
| `arbitration_records_replayed` | `True` |
| `artifact_only_runtime_state_not_used` | `True` |
| `broader_claims_remain_blocked` | `True` |
| `candidate_scores_replayed` | `True` |
| `candidate_sets_replayed` | `True` |
| `corrupted_control_blockers_distinct` | `True` |
| `corrupted_controls_passed` | `True` |
| `hypothesis_a_ceiling_frozen` | `True` |
| `hypothesis_b_deferred_with_blocker` | `True` |
| `manifest_validation_passed` | `True` |
| `memory_claim_opened_only_at_closeout` | `True` |
| `memory_strength_not_physical_flux` | `True` |
| `memory_surface_updates_replayed` | `True` |
| `positive_replay_has_no_blockers` | `True` |
| `route_use_events_replayed` | `True` |
| `scheduled_packets_not_applicable_recorded` | `True` |
| `source_controls_replayed` | `True` |
| `source_mem5_passed` | `True` |
| `source_output_digest_recomputed` | `True` |
| `source_rows_claim_flags_false` | `True` |
| `src_clean` | `True` |

## Artifact Digests

```json
{
  "artifact_only_replay_digest": "de7d2d550abb384221a1d4e4f14721cb3d0303f4484bfd04c65aff3d12bd76e9",
  "checks_digest": "425bde4579d431333d4f0d14ac85ebc90112d716b5ea5ae6df70c22927f130d6",
  "closeout_digest": "2ef35b7ec6909ba6a1178a77d0741560df16a10126832fd88d8fb66a6a0e2472",
  "corrupted_controls_digest": "6472f47b68ef1fe8354693319c35d0ee85d3baa2a644cc0e442f7121570ae5c4",
  "source_control_replay_digest": "e2fcbe004b22a6189786412e6817b2d52d9628e1852e345810d57294f4d3aeda"
}
```

## Acceptance

Iteration 8 passes if the route-use -> memory surface -> decay/reinforcement
-> memory-shaped route arbitration chain can be reconstructed from artifacts
only, controls fail with distinct blockers, budgets remain exact, and the
strongest N08 Hypothesis A memory/trail evidence ceiling is frozen without ACO,
agency, intention, goal-regulation, identity-acceptance, locomotion,
biological, or unrestricted claims.

Achieved: `True`.

Output digest: `202cd1a6d447aedf6c2914b0768819fff6f15c918f509cb26b88eba2d88e7a5c`.
