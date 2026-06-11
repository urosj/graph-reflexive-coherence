# N04 Iteration 16-B S4 Corridor Perturbation Probe

Status: **passed**

Claim ceiling: `s4_corridor_perturbation_envelope_profile`

Iteration 16-B sweeps budget-neutral front/rear perturbations on the S4 corridor transfer fixture.

## T-Axis Summary

- persistence level: `T6_candidate`
- persistence basis: `s4_corridor_perturbation_envelope`
- largest T6-candidate recoverable perturbation: `0.15`
- smallest T6-candidate failed perturbation: `0.175`
- full T6 claim allowed: `False`
- full T6 blocker: `single_corridor_fixture_envelope_without_ring_grid_or_port_graph_transfer`

The S4 corridor fixture recovers T6-candidate centroid restoration through perturbation 0.15 in both directions. Above that boundary, direction-controlled feedback response continues below the full M6/T6-candidate ceiling: M5-style recovery is retained through 0.25 and M4-style boundary response through 0.35. This strengthens the scoped T6-candidate persistence evidence for the corridor fixture, but full T6 and broad geometry-transfer claims remain blocked.

## Sweep Points

| transfer | outcome | M4 | M5 | M6 | blocker | scheduled recovery cycles |
|---:|---|---|---|---|---|---|
| 0.0 | neutral_control | False | True | False | no_perturbation_applied | 3/3 |
| 0.02 | recovered | True | True | True | None | 3/3 |
| 0.05 | recovered | True | True | True | None | 3/3 |
| 0.075 | recovered | True | True | True | None | 3/3 |
| 0.1 | recovered | True | True | True | None | 3/3 |
| 0.125 | recovered | True | True | True | None | 3/3 |
| 0.15 | recovered | True | True | True | None | 3/3 |
| 0.175 | partially_recovered | True | True | False | centroid_not_restored | 3/3 |
| 0.2 | partially_recovered | True | True | False | centroid_not_restored | 3/3 |
| 0.25 | partially_recovered | True | True | False | centroid_not_restored | 3/3 |
| 0.3 | partially_recovered | True | False | False | centroid_not_restored | 0/0 |
| 0.35 | partially_recovered | True | False | False | centroid_not_restored | 0/0 |

## Checks

- `iteration_16_available`: `True`
- `sweep_values_declared_before_run`: `True`
- `same_s4_corridor_policy_reused`: `True`
- `same_recovery_window_reused`: `True`
- `every_point_classified`: `True`
- `primary_blockers_recorded_for_failed_points`: `True`
- `budget_neutral_all_points`: `True`
- `topology_fixed_all_points`: `True`
- `no_forbidden_direct_writes`: `True`
- `artifact_validators_passed`: `True`
- `nonnegative_and_shape_gates_passed`: `True`
- `corridor_tolerance_boundaries_recorded`: `True`
- `no_full_t6_claim_promotion`: `True`

## Go/No-Go

- `iteration_17_allowed`: `True`
- `ring_transfer_ceiling_to_test`: `s4_corridor_m6_transfer_candidate`
- `ring_transfer_guidance`: `ring transfer may proceed under explicit unwrap policy; do not inherit full T6`

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter16b_corridor_perturbation_probe.py
```
