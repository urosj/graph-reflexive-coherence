# N04 Iteration 18 S3 Grid Transfer

Status: **passed**

Claim ceiling: `s3_grid_route_defined_m6_transfer_candidate`

Iteration 18 tests route-defined front/rear transfer on a 5x5 grid.

## Summary

- achieved level: `M6`
- persistence level: `T6_candidate`
- recovery status: `recovers_0_15_grid_route_defined_front_rear`
- entry ceiling: `s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness`
- forward final x delta: `0.03571428571428581`
- reversed final x delta: `-0.03571428571428559`
- max |y drift|: `0.0`

The ring-series ceiling transfers to a route-defined S3 grid candidate under local east/west unit edges. The 2D grid does not use diagonal shortcuts, direct displacement writes, or post-hoc front/rear masks.

## Controls

- `wrong_direction`: passed=`True`, blocker=`feedback_wrong_polarity`
- `diagonal_shortcut`: passed=`True`, blocker=`diagonal_route_shortcuts_disabled_by_fixture_policy`

## Checks

- `iteration_17c_available`: `True`
- `route_based_direction_declared`: `True`
- `front_rear_masks_declared_before_run`: `True`
- `grid_fixture_declared_before_run`: `True`
- `local_unit_route_edges_only`: `True`
- `diagonal_route_shortcuts_disabled`: `True`
- `m4_boundary_response_passed`: `True`
- `m5_direction_control_passed`: `True`
- `m6_grid_transfer_candidate_passed`: `True`
- `grid_direction_parity_passed`: `True`
- `no_y_axis_drift`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `feedback_authorized_not_schedule_copied`: `True`
- `controls_fail_for_distinct_blockers`: `True`
- `native_surface_semantics_unchanged`: `True`
- `native_feedback_producer_semantics_unchanged`: `True`
- `no_direct_writes`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_19_allowed`: `True`
- `port_graph_ceiling_to_test`: `s3_grid_route_defined_m6_transfer_candidate`
- `guidance`: `Iteration 19 may test port-graph and adaptive-topology gates. Grid evidence does not automatically promote topology-mutating or adaptive-topology claims.`

## Claim Boundary

This is a route-defined grid transfer candidate. It is not port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement evidence.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18_grid_transfer.py
```
