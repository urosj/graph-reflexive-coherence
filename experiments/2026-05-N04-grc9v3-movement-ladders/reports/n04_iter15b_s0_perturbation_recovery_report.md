# N04 Iteration 15-B S0 Perturbation Recovery

Status: **passed**

Claim ceiling: `native_m6_same_fixture_self_renewal_candidate_stress_passed`

Iteration 15-B tests threshold-preserving perturbation recovery on the native S0 same-fixture candidate.

## Checks

- `iteration_15_baseline_available`: `True`
- `pre_perturbation_baseline_has_five_cycles`: `True`
- `perturbation_policy_declared_before_run`: `True`
- `perturbation_budget_neutral`: `True`
- `topology_fixed`: `True`
- `no_forbidden_direct_writes`: `True`
- `finite_recovery_window_declared`: `True`
- `recovery_outcome_recorded`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `artifact_validators_passed`: `True`
- `out_of_envelope_controls_negative`: `True`
- `broader_claims_blocked`: `True`

## Recovery Result

- forward pre-perturbation cycles: `5`
- reversed pre-perturbation cycles: `5`
- forward recovery cycles: `2`
- reversed recovery cycles: `2`
- persistence level: `tested_negative`
- R level: `tested_negative`
- out-of-envelope recovery: `tested_negative`

## Go/No-Go

- `iteration_16_allowed`: `True`
- `entry_ceiling_for_geometry_transfer`: `native_m6_same_fixture_self_renewal_candidate_stress_passed`
- `recovery_result_used_for_transfer`: `False`
- `out_of_envelope_recovery_claim_allowed`: `False`

## Claim Flags

```json
{
  "adaptive_topology_entry_allowed": false,
  "agency_claim_allowed": false,
  "biological_claim_allowed": false,
  "identity_acceptance_claim_allowed": false,
  "locomotion_like_claim_allowed": false,
  "loop_driven_movement_claim_allowed": false,
  "movement_claim_allowed": false,
  "movement_claim_inherited_from_n03": false,
  "native_m6": true,
  "native_m6_candidate_gate_passed": true,
  "unrestricted_movement_claim_allowed": false
}
```

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15b_s0_perturbation_recovery.py
```
