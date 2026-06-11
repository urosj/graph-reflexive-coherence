# Fixed-Substrate Tranche A Report

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_fixed_substrate_tranche_a.py
```

Status: `passed`

## Summary

- Execution surface: `surface_a_fixed_substrate_metrics`
- Runner: `experiment_local_fixed_topology_diffusive_response_runner_v1`
- Fixed-substrate tranche A result: `no_movement_response_candidates`
- Movement response candidates: `[]`
- Subthreshold directional bias runs: `['S0_chain_v1_B1', 'S0_chain_v1_B1_reversed', 'S1_ring_v1_B1', 'S1_ring_v1_B1_reversed']`
- Below-threshold substrate-bias-possible reversal pairs: `['S1_ring_v1_K1']`
- Max absolute response displacement: `0.001635474`
- Effective displacement threshold: `0.050000000`
- Interpretation: Fixed-substrate tranche A validated null/control execution, but produced no movement-response candidates under the frozen effective displacement gate.

## Checks

| Check | Passed |
|---|---:|
| `all_lane_budgets_passed` | `True` |
| `all_topology_gates_passed` | `True` |
| `all_nonnegative_gates_passed` | `True` |
| `u0_b0_reject_directed_movement` | `True` |
| `response_lanes_do_not_claim_loop_or_locomotion` | `True` |
| `reversal_controls_are_coherent` | `True` |
| `timeseries_evidence_emitted` | `True` |
| `no_movement_claims_emitted` | `True` |

## Threshold Policy

- Configured minimum: `0.050000000`
- Empirical null threshold: `0.000063063`
- Effective minimum: `0.050000000`
- Threshold source: `configured_min`
- Null max source: `S1_ring_v1_B0` (`ring_antipodal_unwrap_convention_artifact`)

## Lanes

| Run | Budget | Move | Identity | Shape | dX final | dX max | Bias | Width d | Profile | Claim Ceiling |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| `S0_chain_v1_U0` | `True` | `False` | `True` | `True` | `0.000000000` | `0.000000000` | `null_lane` | `0.000000` | `1.000000` | `no_directed_movement` |
| `S0_chain_v1_B0` | `True` | `False` | `True` | `True` | `0.000000000` | `0.000000000` | `null_lane` | `0.002274` | `0.992685` | `no_directed_movement` |
| `S0_chain_v1_B1` | `True` | `False` | `True` | `True` | `-0.000095061` | `0.000095061` | `subthreshold_directional_bias_observed` | `0.002275` | `0.992745` | `no_movement_response_observed` |
| `S0_chain_v1_B1_reversed` | `True` | `False` | `True` | `True` | `0.000095061` | `0.000095061` | `subthreshold_directional_bias_observed` | `0.002275` | `0.992745` | `no_movement_response_observed` |
| `S0_chain_v1_K1` | `True` | `False` | `True` | `True` | `-0.000000000` | `0.000000000` | `no_threshold_level_response` | `0.002274` | `0.992103` | `no_movement_response_observed` |
| `S0_chain_v1_K1_reversed` | `True` | `False` | `True` | `True` | `0.000000000` | `0.000000000` | `no_threshold_level_response` | `0.002274` | `0.992103` | `no_movement_response_observed` |
| `S1_ring_v1_U0` | `True` | `False` | `True` | `True` | `0.000000000` | `0.000000000` | `null_lane` | `0.000000` | `1.000000` | `no_directed_movement` |
| `S1_ring_v1_B0` | `True` | `False` | `True` | `True` | `-0.000040711` | `0.000040711` | `null_lane` | `0.001914` | `0.996584` | `no_directed_movement` |
| `S1_ring_v1_B1` | `True` | `False` | `True` | `True` | `-0.001635474` | `0.001635474` | `subthreshold_directional_bias_observed` | `0.001905` | `0.996610` | `no_movement_response_observed` |
| `S1_ring_v1_B1_reversed` | `True` | `False` | `True` | `True` | `0.001554052` | `0.001554052` | `subthreshold_directional_bias_observed` | `0.001931` | `0.996610` | `no_movement_response_observed` |
| `S1_ring_v1_K1` | `True` | `False` | `True` | `True` | `-0.000040711` | `0.000040711` | `no_threshold_level_response` | `0.001914` | `0.996081` | `no_movement_response_observed` |
| `S1_ring_v1_K1_reversed` | `True` | `False` | `True` | `True` | `-0.000040711` | `0.000040711` | `no_threshold_level_response` | `0.001914` | `0.996081` | `no_movement_response_observed` |

## Diagnostic Notes

- `S0_chain_v1_B1`: asymmetric initial condition under symmetric diffusion relaxed opposite the initial mass bias; this is subthreshold relaxation, not directed movement
- `S0_chain_v1_B1_reversed`: asymmetric initial condition under symmetric diffusion relaxed opposite the initial mass bias; this is subthreshold relaxation, not directed movement
- `S1_ring_v1_B1`: asymmetric initial condition under symmetric diffusion relaxed opposite the initial mass bias; this is subthreshold relaxation, not directed movement
- `S1_ring_v1_B1_reversed`: asymmetric initial condition under symmetric diffusion relaxed opposite the initial mass bias; this is subthreshold relaxation, not directed movement
- `S1_ring_v1_K1`: displacement matches S1 B0 ring antipodal unwrap baseline; kick signal is swamped by the ring convention floor
- `S1_ring_v1_K1_reversed`: displacement matches S1 B0 ring antipodal unwrap baseline; kick signal is swamped by the ring convention floor

## Environment

- Python executable: `.venv/bin/python`
- Python version: `3.12.3 (main, Mar 23 2026, 19:04:32) [GCC 13.3.0]`
- Platform: `Linux-5.15.167-0515167-generic-x86_64-with-glibc2.39`
- `git diff --check` return code: `0`
- `git status --short src experiments/.../N04`: `M experiments/2026-05-N04-grc9v3-movement-ladders/implementation/MovementLaddersImplementationChecklist.md
 M experiments/2026-05-N04-grc9v3-movement-ladders/implementation/MovementLaddersImplementationPlan.md
?? experiments/2026-05-N04-grc9v3-movement-ladders/configs/movement_fixture_manifest_v1.json
?? experiments/2026-05-N04-grc9v3-movement-ladders/hypotheses/movement_ladders_hypothesis_v1.md
?? experiments/2026-05-N04-grc9v3-movement-ladders/outputs/fixed_substrate_tranche_a_report.json
?? experiments/2026-05-N04-grc9v3-movement-ladders/outputs/fixed_substrate_tranche_a_timeseries/
?? experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_fixture_manifest_validation.json
?? experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_initializer_validation.json
?? experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_observables_timeseries/
?? experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_observables_validation.json
?? experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_baseline_inventory.json
?? experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iteration_1_3_lock_summary.json
?? experiments/2026-05-N04-grc9v3-movement-ladders/reports/fixed_substrate_tranche_a_report.md
?? experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_fixture_manifest_validation.md
?? experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_initializer_validation.md
?? experiments/2026-05-N04-grc9v3-movement-ladders/reports/movement_observables_validation.md
?? experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_baseline_inventory.md
?? experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iteration_1_3_lock_summary.md
?? experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_baseline_inventory.py
?? experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_iteration_1_3_lock_summary.py
?? experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_fixed_substrate_tranche_a.py
?? experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_fixture_manifest.py
?? experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_initializers.py
?? experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_observables.py`

## Notes

- This is an experiment-local fixed-substrate response runner, not a native GRC9V3 or LGRC9V3 movement run.
- U0/B0 reject directed movement.
- B1/B1 reversed preserve subthreshold directional sign evidence where present, but do not promote movement.
- K1/K1 reversed kick audits are serialized so a negative response is not confused with a missing stimulus.
- The null envelope is informational in this tranche because the configured displacement minimum dominates it.
- The maximum null displacement comes from the S1 ring antipodal unwrap convention, not stochastic jitter.
- No loop-driven movement, locomotion-like movement, adaptive-topology movement, or inherited N03 movement claim is emitted.
