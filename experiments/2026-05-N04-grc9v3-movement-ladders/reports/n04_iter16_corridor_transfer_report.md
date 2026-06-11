# N04 Iteration 16 S4 Corridor Transfer

Status: **passed**

Claim ceiling: `s4_corridor_m6_transfer_candidate`

Iteration 16 transfers the strongest absorber-informed same-family result to a fixed S4 widened-chain corridor fixture.

## Transfer Summary

- entry ceiling: `large_shock_absorber_same_family_recovery_candidate`
- achieved level: `M6`
- persistence level: `T6_candidate`
- persistence basis: `s4_corridor_transfer_recovers_0_15`
- recovery status: `recovers_0_15_corridor_transfer`
- challenge perturbation: `0.15`
- directions recovered: `['forward', 'reversed']`
- front/rear direction: `positive=increasing_chain_index`
- cost metric: `total_redistribution_load_per_cycle`
- cost per feedback cycle: `0.1`

The absorber-informed S4 widened-chain corridor transfers the same native causal pulse-substrate surface and feedback producer semantics to a non-identical fixed fixture. The candidate preserves direction parity and same-window feedback recovery in both directions, while broad geometry-transfer, locomotion-like, and adaptive-topology claims remain blocked.

Topology note: corridor rails are fixture-defined before execution. Runtime topology remains fixed; no topology mutation occurs during the run.

Centroid note: raw centroid deltas use increasing chain index. Signed centroid deltas are direction-normalized, so positive means recovery in the lane's declared direction.

## Checks

- `iteration_15e_available`: `True`
- `corridor_fixture_declared_before_run`: `True`
- `front_rear_direction_frozen_before_run`: `True`
- `geometry_scope_is_transferred_geometry`: `True`
- `native_surface_semantics_unchanged`: `True`
- `native_feedback_producer_semantics_unchanged`: `True`
- `fixture_topology_changed_before_run`: `True`
- `topology_fixed_during_run`: `True`
- `no_runtime_topology_mutation_observed`: `True`
- `corridor_initialization_budget_neutral`: `True`
- `no_forbidden_direct_writes`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `direction_parity_passed`: `True`
- `m4_boundary_response_passed`: `True`
- `m5_direction_control_passed`: `True`
- `m6_transfer_candidate_passed`: `True`
- `feedback_authorized_not_schedule_copied`: `True`
- `cost_scaling_inherited_from_iteration_15`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_17_allowed`: `True`
- `ring_transfer_ceiling_to_test`: `s4_corridor_m6_transfer_candidate`
- `ring_transfer_guidance`: `ring transfer may test M5/M6 only under explicit unwrap policy`

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter16_corridor_transfer.py
```
