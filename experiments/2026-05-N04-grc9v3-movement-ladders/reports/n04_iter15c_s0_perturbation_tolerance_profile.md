# N04 Iteration 15-C S0 Perturbation Tolerance Profile

Status: **passed**

Claim ceiling: `s0_same_fixture_perturbation_tolerance_profile`

Iteration 15-C sweeps budget-neutral front/rear polarity perturbations on the native S0 same-fixture mechanism.

## Tolerance Summary

- largest T6-recoverable perturbation: `None`
- smallest T6-failed perturbation: `0.0`
- smallest positive T6-failed perturbation: `0.02`
- largest R6-recoverable perturbation: `0.1`
- smallest R6-failed perturbation: `0.0`
- smallest positive R6-failed perturbation: `0.125`
- dominant T6 blocker: `source_budget_exhausted`

Current S0 does not complete the three-cycle T6 recovery window at any tested perturbation amount, including the zero-perturbation reservoir control. Smaller perturbations can restore R6 polarity, but T6 remains source-reservoir limited after the five-cycle pre-perturbation baseline.

## Sweep Points

| transfer | outcome | R6 | T6 | blocker | scheduled recovery cycles |
|---:|---|---|---|---|---|
| 0.0 | partially_recovered | False | False | source_budget_exhausted | 2/2 |
| 0.02 | partially_recovered | True | False | source_budget_exhausted | 2/2 |
| 0.05 | partially_recovered | True | False | source_budget_exhausted | 2/2 |
| 0.075 | partially_recovered | True | False | source_budget_exhausted | 2/2 |
| 0.1 | partially_recovered | True | False | source_budget_exhausted | 2/2 |
| 0.125 | partially_recovered | False | False | source_budget_exhausted | 2/2 |
| 0.15 | partially_recovered | False | False | source_budget_exhausted | 2/2 |
| 0.175 | partially_recovered | False | False | source_budget_exhausted | 2/2 |
| 0.2 | partially_recovered | False | False | source_budget_exhausted | 2/2 |
| 0.25 | partially_recovered | False | False | source_budget_exhausted | 2/2 |
| 0.3 | failed_closed | False | False | subthreshold | 0/0 |
| 0.35 | failed_closed | False | False | subthreshold | 0/0 |

## Checks

- `iteration_15b_available`: `True`
- `sweep_values_declared_before_run`: `True`
- `same_native_s0_policy_reused`: `True`
- `same_recovery_window_reused`: `True`
- `every_point_classified`: `True`
- `primary_blockers_recorded_for_failed_points`: `True`
- `budget_neutral_all_points`: `True`
- `topology_fixed_all_points`: `True`
- `no_forbidden_direct_writes`: `True`
- `artifact_validators_passed`: `True`
- `nonnegative_and_shape_gates_passed`: `True`
- `tolerance_boundaries_recorded`: `True`
- `no_t6_r6_claim_promotion`: `True`

## Go/No-Go

- `iteration_15d_allowed`: `True`
- `challenge_perturbation`: `0.02`
- `challenge_reason`: `smallest_positive_t6_failure_under_current_s0`
- `target_failure_mode_to_improve`: `source_budget_exhausted`
- `s0_reference_claim_ceiling`: `s0_same_fixture_perturbation_tolerance_profile`

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15c_s0_perturbation_tolerance.py
```
