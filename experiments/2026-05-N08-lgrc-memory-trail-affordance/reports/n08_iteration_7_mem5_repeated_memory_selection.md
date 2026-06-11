# N08 Iteration 7 MEM5 Repeated Memory-Shaped Selection

Status: `passed`.

Iteration 7 repeats the Hypothesis A memory policy loop. It does not claim
native geometry-mediated trail memory, pure coherence/flux trail memory, ACO,
agency, or biological pheromone behavior.

## Branch Question

What regime appears when memory-shaped arbitration, route use, and memory update repeat across cycles?

## Branch Answer

Repeated memory-shaped arbitration converges to route B. Route B reaches the
serialized memory ceiling while route A decays under non-selection:

```json
{
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
```

## Arc-of-Becoming Interpretation

This report treats pass/fail as a gate, not as the whole result.

- expressed property:
  `repeated_memory_shaped_selection_candidate`
- naturalization rung:
  `Nat4_repeated_policy_memory_loop`

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
| `same_route_reinforces_and_saturates` | `route_b_strength_after_each_cycle` | `[0.88, 1.0, 1.0, 1.0]` | Route B is repeatedly selected and reaches the serialized memory ceiling. |
| `unselected_route_decays` | `route_a_strength_after_each_cycle` | `[0.5895, 0.53055, 0.477495, 0.4297455]` | Route A remains present as a memory surface but decays while it is not selected. |
| `competing_memory_regime_classified` | `competing_memory_behavior` | `route_b_converges_to_saturation_while_route_a_decays_without_reinforcement` | The observed regime is convergence to the reinforced route, not oscillation or unresolved tie. |
| `policy_memory_not_native_flux` | `hypothesis` | `A_serialized_producer_policy_memory` | The loop is useful producer/policy memory evidence; it does not prove native geometry-mediated trail memory. |

Cultivation next question:

Can route use, memory updates, memory-shaped candidate scores, route arbitration, and controls replay from artifacts only?

## Repeated Cycles

| Cycle | Selected Route | Candidate Scores | Route A After | Route B After |
|---|---|---|---:|---:|
| `cycle_0` | `route_b` | `{"route_a": 0.86395, "route_b": 0.963}` | `0.5895` | `0.88` |
| `cycle_1` | `route_b` | `{"route_a": 0.775888333333, "route_b": 1.1592}` | `0.53055` | `1.0` |
| `cycle_2` | `route_b` | `{"route_a": 0.7032995, "route_b": 1.29}` | `0.477495` | `1.0` |
| `cycle_3` | `route_b` | `{"route_a": 0.64046955, "route_b": 1.29}` | `0.4297455` | `1.0` |

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
  "serialized_memory_policy_loop": true
}
```

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
| `repeated_hidden_route_preference` | `blocked` | `candidate_score_hidden_memory_input` | `True` | Reject repeated selection driven by hidden route preference. |
| `stale_memory_surface_read` | `blocked` | `stale_memory_surface_read` | `True` | Reject a cycle that scores candidates from stale memory rows. |
| `duplicate_memory_update` | `blocked` | `duplicate_memory_update` | `True` | Reject duplicate update rows for the same route/cycle. |
| `cross_cycle_memory_leak` | `blocked` | `cross_cycle_memory_leak` | `True` | Reject memory state leaking across unrelated route keys. |
| `memory_budget_discontinuity` | `blocked` | `memory_budget_discontinuity` | `True` | Reject memory update budget drift. |
| `node_plus_packet_budget_discontinuity` | `blocked` | `node_plus_packet_budget_discontinuity` | `True` | Reject physical budget drift hidden by memory scoring. |
| `claim_promotion` | `blocked` | `claim_promotion` | `True` | Reject MEM5 promotion to memory claim, ACO, agency, or movement. |

## Checks

| Check | Passed |
|---|---|
| `arc_interpretation_present` | `True` |
| `candidate_route_digests_recompute` | `True` |
| `candidate_scores_equal_component_sums` | `True` |
| `claim_flags_all_false` | `True` |
| `competing_memory_behavior_recorded` | `True` |
| `control_blockers_distinct` | `True` |
| `controls_passed` | `True` |
| `controls_present` | `True` |
| `duplicate_updates_suppressed` | `True` |
| `extinction_trend_observed_not_floor_reached` | `True` |
| `hypothesis_a_only_no_native_geometry_claim` | `True` |
| `memory_budget_equations_hold` | `True` |
| `memory_claim_still_closed` | `True` |
| `memory_surface_digests_recompute` | `True` |
| `memory_update_after_route_use` | `True` |
| `minimum_cycle_count_met` | `True` |
| `node_plus_packet_budget_exact` | `True` |
| `oscillation_and_tie_recorded` | `True` |
| `producer_step_boundary_preserved` | `True` |
| `route_arbitration_digests_recompute` | `True` |
| `route_b_repeated_selection_observed` | `True` |
| `route_use_after_arbitration` | `True` |
| `route_use_digests_recompute` | `True` |
| `saturation_observed` | `True` |
| `selected_route_reinforced_only` | `True` |
| `source_manifest_passed` | `True` |
| `source_mem4_passed` | `True` |
| `src_clean` | `True` |

## Artifact Digests

```json
{
  "arc_interpretation_digest": "5adba781e165fda4494cd15e741c2a8524bfc68a6f730d9e08156c258d708592",
  "checks_digest": "592780e2284960a6c605c48a8259af918ae6d3677969d230036ea4101c2c0032",
  "controls_digest": "cd8e2d0fb8542c4a8110bd1be91ea143456dead4eae250362e5fe9871fcd002e",
  "cycles_digest": "60588fbf5fcd37c2f3eb5c16a5f88fe9915a2709413ae01ed7889715129d5d32",
  "trend_summary_digest": "ade130e57217d79ec7869dd33aeae5ff4965e678a149397fc012a94b2819ff76"
}
```

## Acceptance

Iteration 7 passes if repeated route-use cycles produce memory-shaped route
selection without hidden steering and without budget drift.

Achieved: `True`.

Output digest: `a5b8673f705a67394f284808a780a5ec4e30af00eac003b7f411ec14ce2b135a`.
