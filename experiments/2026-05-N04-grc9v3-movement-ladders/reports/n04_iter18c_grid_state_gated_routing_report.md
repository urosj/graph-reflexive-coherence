# N04 Iteration 18-C S3 Grid State-Gated Routing

Status: **passed**

Claim ceiling: `s3_grid_state_gated_two_input_two_output_routing_candidate`

Iteration 18-C tests a fixed-topology two-input/two-output grid junction.

## Reasoning

Iteration 18-B proved a declared two-axis turn route. Iteration 18-C asks whether the same junction can select different output gates from different committed pulse-contact histories under one serialized gate policy. This is a design prototype over native LGRC primitives: packet work, surface rows, feedback eligibility, feedback scheduling, and artifact validation are native, but gate selection itself is still experiment-level policy. The native direction is to make selection geometry-driven through committed surface evidence rather than external decision logic.

## Summary

- achieved level: `M6`
- persistence level: `T6_candidate`
- recovery status: `recovers_0_15_state_gated_output_routes`
- entry ceiling: `s3_grid_two_axis_turn_m6_transfer_candidate`
- selected outputs: `{'west_input_selects_north': 7, 'south_input_selects_east': 13}`
- route progress: `{'west_input_selects_north': 0.011785113019775906, 'south_input_selects_east': 0.011785113019775906}`

The same fixed S3 grid junction exposes two input gates and two output gates. Different committed ingress histories select different outputs under one serialized gate policy, and each selected output route recovers after perturbation through native feedback scheduling. This is a design prototype over native LGRC primitives: gate selection itself is experiment-level policy, not yet a native geometry-driven LGRC producer. It remains fixed-topology routing, not adaptive topology.

## Controls

- `gate_policy_disabled`: passed=`True`, blocker=`gate_policy_disabled`
- `wrong_history_gate`: passed=`True`, blocker=`gate_selection_rejected_by_committed_ingress_history`
- `wrong_polarity`: passed=`True`, blocker=`feedback_wrong_polarity`
- `diagonal_shortcut`: passed=`True`, blocker=`diagonal_route_shortcuts_disabled_by_fixture_policy`
- `scrambled_order`: passed=`True`, blocker=`gate_selection_requires_committed_ingress_history`

## Checks

- `iteration_18b_available`: `True`
- `state_gated_reasoning_recorded`: `True`
- `two_input_two_output_policy_declared_before_run`: `True`
- `same_fixed_grid_topology_used`: `True`
- `different_histories_select_different_outputs`: `True`
- `gate_selection_uses_committed_ingress_history`: `True`
- `local_unit_route_edges_only`: `True`
- `diagonal_route_shortcuts_disabled`: `True`
- `route_turns_axis`: `True`
- `two_axis_centroid_components_observed`: `True`
- `m4_boundary_response_passed`: `True`
- `m5_direction_control_passed`: `True`
- `m6_state_gated_routing_candidate_passed`: `True`
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
- `port_graph_ceiling_to_test`: `s3_grid_state_gated_two_input_two_output_routing_candidate`
- `guidance`: `Iteration 19 may now test whether state-gated fixed-topology routing transfers to S7 port-graph mechanics. Adaptive topology remains blocked until topology-specific controls pass.`

## Claim Boundary

This is a fixed-topology state-gated grid routing design prototype over native LGRC primitives. It is not yet native geometry-driven gate selection, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement evidence.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18c_grid_state_gated_routing.py
```
