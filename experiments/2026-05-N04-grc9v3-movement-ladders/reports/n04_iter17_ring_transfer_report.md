# N04 Iteration 17 S1 Ring Transfer

Status: **passed**

Claim ceiling: `s1_ring_m6_transfer_candidate_under_declared_unwrap`

Iteration 17 transfers the corridor candidate to an S1 ring under an explicit unwrap policy.

## Transfer Summary

- achieved level: `M6`
- persistence level: `T6_candidate`
- persistence basis: `s1_ring_declared_unwrap_recovers_0_15`
- recovery status: `recovers_0_15_ring_declared_unwrap`
- challenge perturbation: `0.15`
- directions recovered: `['forward', 'reversed']`
- unwrap policy: `s1_ring_unwrap_policy_v1`
- cost metric: `total_redistribution_load_per_cycle`
- cost per feedback cycle: `0.1`

The S1 ring transfer preserves the corridor M6 candidate under a declared unwrap policy whose active route does not cross the seam. This is ring-under-policy evidence, not circular locomotion, wrap-crossing, broad geometry-transfer, or adaptive-topology evidence.

Unwrap note: the seam is fixed at `[20, 0]`, the active route does not cross it, and wrap-jump promotion is blocked.

## Checks

- `iteration_16c_available`: `True`
- `unwrap_policy_available`: `True`
- `ring_fixture_declared_before_run`: `True`
- `front_rear_direction_frozen_before_run`: `True`
- `route_does_not_cross_unwrap_seam`: `True`
- `antipodal_tie_cannot_promote`: `True`
- `wrap_jump_promotion_blocked`: `True`
- `native_surface_semantics_unchanged`: `True`
- `native_feedback_producer_semantics_unchanged`: `True`
- `fixture_topology_changed_before_run`: `True`
- `topology_fixed_during_run`: `True`
- `no_runtime_topology_mutation_observed`: `True`
- `ring_initialization_budget_neutral`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `direction_parity_passed`: `True`
- `m4_boundary_response_passed`: `True`
- `m5_direction_control_passed`: `True`
- `m6_ring_transfer_candidate_passed`: `True`
- `feedback_authorized_not_schedule_copied`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_18_allowed`: `True`
- `grid_transfer_ceiling_to_test`: `s1_ring_m6_transfer_candidate_under_declared_unwrap`
- `grid_transfer_guidance`: `grid transfer may test M5/M6 under route-defined front/rear masks`

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter17_ring_transfer.py
```
