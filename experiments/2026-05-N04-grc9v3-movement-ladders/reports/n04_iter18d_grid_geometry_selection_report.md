# N04 Iteration 18-D S3 Grid Geometry-Scored Selection

Status: **passed**

Claim ceiling: `s3_grid_geometry_scored_selection_design_prototype`

Iteration 18-D tests a geometry-scored competing-output-basin selection prototype.

## Reasoning

Iteration 18-C selected output gates from an experiment-level ingress-to-output policy. Iteration 18-D moves the design closer to geometry itself: both output basins are available, the input pulse carries a flux-shape signature, and the selected basin is the one with the stronger geometry/flux compatibility score. This is a selection/collapse analogue only, not RC identity collapse, agency, or native LGRC selection. Unlike the earlier native policy extensions, 18-D adds an external experiment scorer that evaluates competing outputs; it does not let composed LGRC branch dynamics make the selection.

## Summary

- achieved level: `M6`
- persistence level: `T6_candidate`
- recovery status: `recovers_0_15_geometry_selected_output_routes`
- entry ceiling: `s3_grid_state_gated_two_input_two_output_routing_candidate`
- selected basins: `{'north_curved_flux': 'north_output_basin', 'east_curved_flux': 'east_output_basin'}`
- selected outputs: `{'north_curved_flux': 7, 'east_curved_flux': 13}`
- route progress: `{'north_curved_flux': 0.004761904761904967, 'east_curved_flux': 0.004761904761904745}`

Two output basins compete under one fixed grid geometry. Different input flux shapes resolve to different selected basins by geometry/flux compatibility score, then native feedback scheduling carries the selected pulse work. This is a selection/collapse analogue and design prototype, not RC identity collapse, agency, or native LGRC selection. The selection scorer is external experiment logic, not merely a native LGRC scheduling policy.

## Native Boundary

- `native_lgrc_packet_work_used`: `True`
- `native_causal_pulse_substrate_surface_used`: `True`
- `native_feedback_eligibility_surface_used`: `True`
- `native_feedback_producer_used`: `True`
- `native_artifact_validator_used`: `True`
- `selection_native_lgrc_producer`: `False`
- `selection_source`: `experiment_level_geometry_competition_score`
- `selection_logic_kind`: `external_experiment_scoring_logic`
- `different_from_prior_lgrc_policy_extensions`: `True`
- `prior_policy_extension_distinction`: `Earlier native policy extensions ordered or scheduled already declared packet work from committed evidence. Iteration 18-D adds an experiment-level compatibility scorer that evaluates competing futures and suppresses the non-selected basin.`
- `geometry_driven_selection_supported`: `False`
- `native_selection_blocker`: `compatibility scoring is performed by experiment script logic; a native geometry-driven selection/collapse producer or equivalent surface mechanism is not implemented yet`
- `compositional_lgrc_fork_direction`: `Compose two native one-dimensional LGRC route elements into a shared fork and measure whether branch eligibility, budget, and feedback dynamics select a branch without external argmax or compatibility scoring.`

## Controls

- `competition_disabled`: passed=`True`, blocker=`competition_selection_disabled`
- `ambiguous_tie_flux`: passed=`True`, blocker=`ambiguous_competing_basin_scores`
- `wrong_output_basin`: passed=`True`, blocker=`geometry_score_rejects_wrong_output_basin`
- `diagonal_shortcut`: passed=`True`, blocker=`diagonal_route_shortcuts_disabled_by_fixture_policy`

## Checks

- `iteration_18c_available`: `True`
- `selection_collapse_reasoning_recorded`: `True`
- `competing_output_basins_declared_before_run`: `True`
- `compatibility_scoring_rule_declared_before_run`: `True`
- `selection_derived_from_flux_shape_and_geometry`: `True`
- `distinct_flux_shapes_select_distinct_basins`: `True`
- `m4_boundary_response_passed`: `True`
- `m5_direction_control_passed`: `True`
- `m6_geometry_selection_candidate_passed`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `feedback_authorized_not_schedule_copied`: `True`
- `controls_fail_for_distinct_blockers`: `True`
- `native_surface_semantics_unchanged`: `True`
- `native_feedback_producer_semantics_unchanged`: `True`
- `no_direct_writes`: `True`
- `selection_not_identity_collapse_or_agency`: `True`
- `native_geometry_selection_not_yet_supported`: `True`
- `external_selection_logic_blocker_recorded`: `True`
- `compositional_lgrc_fork_direction_recorded`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_19_allowed`: `True`
- `port_graph_ceiling_to_test`: `s3_grid_geometry_scored_selection_design_prototype`
- `guidance`: `Iteration 19 may test whether this geometry-scored selection direction can be represented by S7 port mechanics. Native selection/collapse remains blocked until implemented in LGRC.`

## Claim Boundary

This is a geometry-scored selection design prototype over native LGRC primitives. It is not native geometry-driven selection, selection without external logic, native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, identity-acceptance, inherited-N03, or unrestricted movement evidence.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18d_grid_geometry_selection.py
```
