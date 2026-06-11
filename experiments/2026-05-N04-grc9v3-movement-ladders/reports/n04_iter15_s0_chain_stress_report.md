# N04 Iteration 15 S0 Chain Stress

Status: **passed**

Claim ceiling: `native_m6_same_fixture_self_renewal_candidate_stress_passed`

Iteration 15 stresses the same-fixture S0 M5/M6 candidates without transferring geometry.

## Checks

- `tag_schema_passed`: `True`
- `m5_replay_passed`: `True`
- `baseline_m6_available`: `True`
- `forward_five_feedback_cycles`: `True`
- `reversed_five_feedback_cycles`: `True`
- `seeded_vs_feedback_cycles_separated`: `True`
- `direction_parity_preserved`: `True`
- `budget_error_bounded`: `True`
- `nonnegative_gate_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `artifact_validators_passed`: `True`
- `cost_scaling_bounded`: `True`
- `cycle3_to_cycle5_cost_not_doubled`: `True`
- `recovery_status_recorded`: `True`
- `broader_claims_blocked`: `True`

## Stress Result

- forward self-renewed cycles: `5`
- reversed self-renewed cycles: `5`
- forward dX: `0.035714285714286476`
- reversed dX: `-0.035714285714286476`
- cost scaling status: `bounded`
- recovery status: `not_tested_blocked_until_perturbation_recovery_probe`

## Go/No-Go

- `m6_sustained_five_feedback_cycles`: `True`
- `bounded_cost`: `True`
- `entry_ceiling_for_geometry_transfer`: `native_m6_same_fixture_self_renewal_candidate_stress_passed`
- `iteration_16_allowed`: `True`

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
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15_s0_chain_stress.py
```
