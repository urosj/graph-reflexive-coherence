# N04 Iteration 16-C High-Shock Corridor Resilience

Status: **passed**

Claim ceiling: `s4_corridor_high_shock_capacity_requirement_probe`

Iteration 16-C probes whether the S4 corridor high-shock boundary is geometry-limited or capacity-limited.

## T-Axis Summary

- persistence level: `T6_candidate`
- persistence basis: `s4_corridor_high_shock_capacity_requirement`
- three-cycle reference largest T6-candidate perturbation from 16-B: `0.15`
- three-cycle above-boundary probe largest T6-candidate perturbation: `None`
- four-cycle largest T6-candidate perturbation: `0.2`
- five-cycle largest T6-candidate perturbation: `0.25`
- full T6 claim allowed: `False`
- full T6 blocker: `capacity_variants_change_recovery_window_and_are_single_corridor_fixture_only`

Iteration 16-C shows the 16-B high-shock boundary is a feedback capacity boundary under the declared three-cycle, 0.1-packet native feedback window. Geometry-only corridor changes do not lift the 0.15 T6-candidate limit. Extending serialized recovery capacity to four cycles recovers 0.20, and five cycles recovers 0.25. This is capacity-requirement evidence for Iteration 17, not a full T6 or broad geometry-transfer claim.

## Discovery Note

- finding: `corridor_high_shock_recovery_is_capacity_limited`
- rule: `required_boundary_recovery_load = 2 * perturbation_amount`
- available capacity: `recovery_window_cycles * native_feedback_packet_amount`
- default capacity: `3 * 0.1 = 0.30000000000000004`
- first above-boundary failure: `0.175`

The 0.175 failure is expected because it requires 0.35 boundary recovery load while the default three-cycle window supplies only 0.30. Larger shocks require declared capacity extension, not only different fixed corridor geometry.

## Variant Summary

| recovery cycles | largest M6/T6-candidate | largest M5 | largest M4 | first M6 failure |
|---:|---:|---:|---:|---:|
| 3 | None | 0.25 | 0.35 | 0.175 |
| 4 | 0.2 | 0.25 | 0.35 | 0.25 |
| 5 | 0.25 | 0.25 | 0.35 | 0.3 |

## Checks

- `iteration_16b_available`: `True`
- `capacity_boundary_from_16b_confirmed`: `True`
- `window_variants_declared_before_run`: `True`
- `three_cycle_geometry_only_boundary_preserved`: `True`
- `four_cycle_capacity_recovers_0_20`: `True`
- `five_cycle_capacity_recovers_0_25`: `True`
- `all_budget_and_shape_gates_pass`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_17_allowed`: `True`
- `ring_transfer_guidance`: `ring transfer should declare whether it keeps the three-cycle capacity from 16-B or explicitly tests capacity-extended variants from 16-C`

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter16c_high_shock_corridor_resilience.py
```
