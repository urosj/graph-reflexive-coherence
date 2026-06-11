# Boundary-Coupled Pulse Fixture

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_boundary_coupled_pulse_fixture.py
```

Status: `passed`

## Summary

- Mapping: `e3_four_pole_to_s0_chain_boundary_v1`
- Target fixture: `S0_chain_v1`
- Claim ceiling: `boundary_coupled_pulse_fixture_validation`
- Primary blocked reason: `movement_classification_deferred_to_iteration_9`
- Movement claim allowed: `False`
- Symmetric null dX: `-1.7763568394002505e-15`
- Forward dX: `0.08333333333333215`
- Reversed dX: `-0.08333333333333393`
- Forward boundary coupling score: `0.25`
- Reversed boundary coupling score: `0.25`
- Forward configured coupling mass: `0.25`
- Reversed configured coupling mass: `0.25`
- Iteration 5 displacement threshold: `0.05`
- Max Iteration 8 |dX|: `0.08333333333333393`
- Mapping consistency passed: `True`
- Centroid replay passed: `True`
- Timeseries digests verified: `True`

## Mapping

- Mapping type: `region_based`
- Node-id preserving: `False`
- Positive direction: `increasing_chain_index`
- Direction source: `mapped_e3_route`
- Direction frozen before run: `True`

## Checks

| Check | Passed |
|---|---:|
| `iteration_7b_dependency_passed` | `True` |
| `route_to_substrate_mapping_defined` | `True` |
| `s0_chain_mapping_active` | `True` |
| `symmetric_null_no_net_movement_claim` | `True` |
| `asymmetric_coupling_measurable` | `True` |
| `reversed_coupling_measurable` | `True` |
| `reversal_changes_centroid_sign` | `True` |
| `all_budget_gates_pass` | `True` |
| `all_nonnegative_gates_pass` | `True` |
| `no_direct_state_writes` | `True` |
| `movement_claims_blocked` | `True` |
| `mapping_consistency_passed` | `True` |
| `centroid_replay_passed` | `True` |
| `forward_reversal_magnitude_symmetry_passed` | `True` |
| `boundary_score_symmetry_passed` | `True` |
| `iteration_5_threshold_comparison_recorded` | `True` |
| `all_timeseries_digests_verified` | `True` |

## Lanes

| Lane | Mode | dX | Dir Gain | Dir Release | Fwd Score | Rev Score | Timeseries | Movement Claim |
|---|---|---:|---:|---:|---:|---:|---|---:|
| `P0_pulse_disabled_control` | `disabled` | `0.000000000` | `0.000000000` | `0.000000000` | `0.000000000` | `0.000000000` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_timeseries/P0_pulse_disabled_control.jsonl` | `False` |
| `P1_symmetric_boundary_coupling_null` | `symmetric_null` | `-0.000000000` | `0.000000000` | `0.000000000` | `0.000000000` | `0.000000000` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_timeseries/P1_symmetric_boundary_coupling_null.jsonl` | `False` |
| `P2_asymmetric_boundary_coupling_forward` | `asymmetric_forward` | `0.083333333` | `0.250000000` | `0.250000000` | `0.250000000` | `0.000000000` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_timeseries/P2_asymmetric_boundary_coupling_forward.jsonl` | `False` |
| `P2_asymmetric_boundary_coupling_reversed` | `asymmetric_reversed` | `-0.083333333` | `0.250000000` | `0.250000000` | `0.000000000` | `0.250000000` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_timeseries/P2_asymmetric_boundary_coupling_reversed.jsonl` | `False` |

## Interpretation

Iteration 8 defines a state-mediated route-to-substrate coupling fixture and verifies measurable boundary coherence effects, while leaving movement claims blocked for Iteration 9 classification.

## Notes

- Coupling is state-mediated through mapped E3 pole coherence signal.
- The reversed Iteration 8 lane reverses coupling direction only; a true reversed-E3-pulse telemetry lane is deferred to Iteration 9.
- The frozen Iteration 5 effective displacement threshold is read from `fixed_substrate_tranche_a_report.json`; Iteration 8 records the comparison but does not classify movement.
- `net_boundary_mass_accumulation` records mass accumulated in front+rear boundary masks relative to the initial state; it is not a conservation error.
- `coupling_strength = 0.5` was chosen as a first fixture-validation value that produces measurable bounded coupling; sensitivity analysis is deferred.
- K2 and S2 are mapped for route completeness but are not used by `coupling_signal_v1`.
- The fixture changes movement node coherence, not support masks, centroids, displacement, or topology directly.
- Iteration 8 measures boundary coupling only; M4/M5 movement classification remains Iteration 9 work.
- `S1_ring_v1` mapping is deferred because ring boundary coupling needs a separate unwrap/front-rear policy.
