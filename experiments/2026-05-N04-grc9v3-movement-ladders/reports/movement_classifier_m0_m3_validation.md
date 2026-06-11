# Movement Classifier M0-M3 Validation

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_classifier.py
```

Status: `passed`
Classifier: `movement_m0_m3_classifier_v1`

## Checks

| Check | Passed |
|---|---:|
| `deterministic_classification` | `True` |
| `m0_m3_levels_emitted` | `True` |
| `budget_failure_blocks_promotion` | `True` |
| `topology_failure_blocks_promotion` | `True` |
| `identity_failure_blocks_m2_m3` | `True` |
| `shape_failure_blocks_m3` | `True` |
| `m2_shape_failure_gate_exercised` | `True` |
| `nonnegative_failure_blocks_promotion` | `True` |
| `synthetic_positive_reaches_m3` | `True` |
| `iteration_5_tranche_a_remains_m0` | `True` |
| `iteration_5_subthreshold_bias_preserved` | `True` |
| `boundary_churn_not_m2` | `True` |
| `paired_control_results_emitted` | `True` |
| `schema_v1_required_fields_present` | `True` |
| `all_reports_keep_claims_false` | `True` |
| `secondary_gate_failures_visible` | `True` |

## Distribution

| Level | Count |
|---|---:|
| `M0_blocked` | `5` |
| `M0_no_threshold_displacement` | `17` |
| `M1_apparent_centroid_displacement` | `4` |
| `M2_identity_preserving_displacement` | `1` |
| `M3_shape_preserving_identity_displacement` | `8` |

## Diagnostic Subtypes

| Subtype | Count |
|---|---:|
| `M0_budget_failure` | `2` |
| `M0_no_kick_response` | `4` |
| `M0_no_threshold_response` | `1` |
| `M0_nonnegative_failure` | `1` |
| `M0_null_symmetric` | `8` |
| `M0_subthreshold_directional_bias` | `4` |
| `M0_topology_failure` | `2` |
| `M1_centroid_without_directed_boundary_reassignment` | `2` |
| `M1_identity_replacement_or_untracked_basin` | `2` |
| `M2_boundary_reassignment_shape_blocked` | `1` |
| `M3_boundary_and_shape_preserved` | `8` |

## Iteration 5 Classifications

| Run | Level | Subtype | Primary Blocker | dX |
|---|---|---|---|---:|
| `S0_chain_v1_B0` | `M0_no_threshold_displacement` | `M0_null_symmetric` | `displacement_below_threshold` | `0.000000000` |
| `S0_chain_v1_B1` | `M0_no_threshold_displacement` | `M0_subthreshold_directional_bias` | `displacement_below_threshold` | `-0.000095061` |
| `S0_chain_v1_B1_reversed` | `M0_no_threshold_displacement` | `M0_subthreshold_directional_bias` | `displacement_below_threshold` | `0.000095061` |
| `S0_chain_v1_K1` | `M0_no_threshold_displacement` | `M0_no_kick_response` | `displacement_below_threshold` | `-0.000000000` |
| `S0_chain_v1_K1_reversed` | `M0_no_threshold_displacement` | `M0_no_kick_response` | `displacement_below_threshold` | `0.000000000` |
| `S0_chain_v1_U0` | `M0_no_threshold_displacement` | `M0_null_symmetric` | `displacement_below_threshold` | `0.000000000` |
| `S1_ring_v1_B0` | `M0_no_threshold_displacement` | `M0_null_symmetric` | `displacement_below_threshold` | `-0.000040711` |
| `S1_ring_v1_B1` | `M0_no_threshold_displacement` | `M0_subthreshold_directional_bias` | `displacement_below_threshold` | `-0.001635474` |
| `S1_ring_v1_B1_reversed` | `M0_no_threshold_displacement` | `M0_subthreshold_directional_bias` | `displacement_below_threshold` | `0.001554052` |
| `S1_ring_v1_K1` | `M0_no_threshold_displacement` | `M0_no_kick_response` | `displacement_below_threshold` | `-0.000040711` |
| `S1_ring_v1_K1_reversed` | `M0_no_threshold_displacement` | `M0_no_kick_response` | `displacement_below_threshold` | `-0.000040711` |
| `S1_ring_v1_U0` | `M0_no_threshold_displacement` | `M0_null_symmetric` | `displacement_below_threshold` | `0.000000000` |

## Paired Controls

| Pair | Result | Forward dX | Reverse dX |
|---|---|---:|---:|
| `S0_chain_v1_B1` | `subthreshold_opposite_sign_bias` | `-0.000095061` | `0.000095061` |
| `S0_chain_v1_K1` | `no_threshold_response` | `-0.000000000` | `0.000000000` |
| `S1_ring_v1_B1` | `subthreshold_opposite_sign_bias` | `-0.001635474` | `0.001554052` |
| `S1_ring_v1_K1` | `possible_substrate_bias` | `-0.000040711` | `-0.000040711` |

## Blocker Audits

- Budget-blocked runs: `['S0_chain_v1_budget_drift', 'S1_ring_v1_budget_drift']`
- Topology-blocked runs: `['S0_chain_v1_topology_changed_apparent_displacement', 'S1_ring_v1_topology_changed_apparent_displacement']`
- Identity-blocked runs: `['S0_chain_v1_basin_replacement', 'S1_ring_v1_basin_replacement']`
- Shape-blocked runs: `['S0_chain_v1_smeared_shift', 'S1_ring_v1_smeared_shift']`
- M2 shape-blocked runs: `['iteration_6_adversarial_m2_shape_failure']`
- Nonnegative-blocked runs: `['iteration_6_adversarial_nonnegative_failure']`

## Notes

- M0-M3 labels classify evidence only; movement claim flags remain false in this validation.
- Budget, topology, and nonnegative coherence failures are hard blockers.
- Identity failure caps evidence at M1.
- Directed boundary reassignment is required before M2.
- Shape/profile failure caps evidence below M3.
- Boundary churn without coherent front/rear handoff is not M2, even when displacement and identity gates pass.
- Iteration 5 B1/B1_reversed are preserved as M0 subthreshold directional bias.
- Iteration 5 fixed-substrate tranche A remains M0 because no lane reaches threshold displacement.
- Iteration 7 E3 pulse import is not a movement run and is validated separately.
