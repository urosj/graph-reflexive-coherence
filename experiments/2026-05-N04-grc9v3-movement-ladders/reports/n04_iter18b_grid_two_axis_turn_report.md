# N04 Iteration 18-B S3 Grid Two-Axis Turn

Status: **passed**

Claim ceiling: `s3_grid_two_axis_turn_m6_transfer_candidate`

Iteration 18-B tests whether the grid candidate can turn across axes.

## Reasoning

Iteration 18 showed that a one-axis route can survive inside a 2D grid. That is useful, but still close to chain/ring behavior. Iteration 18-B requires an L-shaped route episode: committed ingress reaches the center on one axis, then feedback eligibility authorizes egress on the orthogonal axis.

## Summary

- achieved level: `M6`
- persistence level: `T6_candidate`
- recovery status: `recovers_0_15_two_axis_turn_route`
- entry ceiling: `s3_grid_route_defined_m6_transfer_candidate`
- forward final delta: `{'x': 0.011904761904762085, 'y': -0.004761904761904967}`
- reversed final delta: `{'x': -0.004761904761904745, 'y': 0.011904761904761862}`
- forward route progress: `0.011785113019776063`
- reversed route progress: `0.011785113019775749`

The grid result is stronger than Iteration 18 because the route episode crosses axes: a committed ingress pulse reaches the center on one axis, then native feedback eligibility authorizes egress on the orthogonal axis. This remains a declared route candidate, not adaptive gate selection.

## Controls

- `wrong_polarity`: passed=`True`, blocker=`feedback_wrong_polarity`
- `diagonal_shortcut`: passed=`True`, blocker=`diagonal_route_shortcuts_disabled_by_fixture_policy`

## Checks

- `iteration_18_available`: `True`
- `two_axis_turn_reasoning_recorded`: `True`
- `l_route_declared_before_run`: `True`
- `ingress_egress_gates_declared_before_run`: `True`
- `grid_fixture_declared_before_run`: `True`
- `local_unit_route_edges_only`: `True`
- `diagonal_route_shortcuts_disabled`: `True`
- `route_turns_axis`: `True`
- `two_axis_centroid_components_observed`: `True`
- `m4_boundary_response_passed`: `True`
- `m5_direction_control_passed`: `True`
- `m6_two_axis_turn_candidate_passed`: `True`
- `paired_turn_parity_passed`: `True`
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

- `iteration_18c_allowed`: `True`
- `state_gated_routing_ceiling_to_test`: `s3_grid_two_axis_turn_m6_transfer_candidate`
- `guidance`: `Iteration 18-C may test whether the same fixed grid junction can select between two output gates from committed pulse-contact history. Iteration 18-B alone does not prove state-gated routing.`

## Claim Boundary

This is a declared two-axis turn-route candidate. It is not state-gated 2D routing, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement evidence.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18b_grid_two_axis_turn.py
```
