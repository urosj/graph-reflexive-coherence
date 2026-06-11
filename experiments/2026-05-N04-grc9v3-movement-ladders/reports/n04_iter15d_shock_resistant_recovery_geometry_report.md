# N04 Iteration 15-D Shock-Resistant Recovery Geometry

Status: **passed**

Claim ceiling: `shock_resistant_same_family_geometry_recovery_candidate`

Iteration 15-D tests whether a same-family source-reservoir geometry improves the S0 source-budget exhaustion failure mode.

## Resilience Summary

- challenge perturbation: `0.02`
- stress perturbation: `0.15`
- challenge recovered: `True`
- stress recovered: `False`
- target failure mode: `source_budget_exhausted`
- source-budget exhaustion avoided at challenge: `True`
- source-budget exhaustion avoided at stress: `True`

A symmetric source-reservoir buffer removes the S0 source-budget exhaustion failure at the first positive S0 T6-failing perturbation. At the stronger 0.15 stress point it also schedules the full recovery window and avoids source exhaustion, but it does not satisfy the T6 centroid-restoration criterion. Native surface and feedback producer semantics are unchanged.

## Checks

- `iteration_15c_available`: `True`
- `candidate_geometry_declared_before_run`: `True`
- `challenge_inherited_from_15c`: `True`
- `same_native_surface_and_feedback_producer_reused`: `True`
- `policy_differences_declared`: `True`
- `budget_neutral_geometry_init`: `True`
- `topology_fixed`: `True`
- `no_forbidden_direct_writes`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `challenge_recovery_improved_over_s0`: `True`
- `source_budget_exhaustion_improved`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_16_allowed`: `True`
- `entry_ceiling_for_geometry_transfer`: `shock_resistant_same_family_geometry_recovery_candidate`
- `iteration_16_fixture_guidance`: `test resilience-informed corridor/widened-chain geometry`

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15d_shock_resistant_geometry.py
```
