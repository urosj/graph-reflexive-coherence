# N04 Iteration 18-E S3 Grid Composed 1D Fork Competition

Status: **passed**

Claim ceiling: `s3_grid_composed_1d_fork_competition_candidate`

Iteration 18-E tests whether two native 1D LGRC branch elements can compose a 2D fork without external geometry scoring.

## Reasoning

Iteration 18-D demonstrated a useful geometry/flux relation, but its selection scorer lived outside LGRC. Iteration 18-E removes that scorer. The probe evaluates native feedback eligibility on two declared 1D branch elements sharing a fork. A unique branch may be selected only when branch state makes one branch eligible and the other subthreshold; when both branches are eligible, current LGRC records a no-arbitration tie.

## Summary

- achieved level: `M6`
- persistence level: `T6_candidate`
- recovery status: `recovers_0_15_on_unique_native_eligible_branch`
- entry ceiling: `s3_grid_geometry_scored_selection_design_prototype`
- selected branches: `{'north_branch_capacity_dominant': 'north_branch', 'east_branch_capacity_dominant': 'east_branch'}`
- remaining blocker: `A symmetric eligible fork produces no native arbitration; selection is supported only when geometry/capacity makes one branch eligible and the other subthreshold.`

## Native Boundary

- `native_lgrc_packet_work_used`: `True`
- `native_causal_pulse_substrate_surface_used`: `True`
- `native_feedback_eligibility_surface_used`: `True`
- `native_feedback_producer_used`: `True`
- `native_artifact_validator_used`: `True`
- `external_geometry_scorer_used`: `False`
- `external_argmax_used`: `False`
- `native_branch_competition_supported`: `True`
- `native_branch_arbitration_supported`: `False`
- `selection_mechanism`: `branch_eligibility_differentiation_from_composed_1d_elements`
- `arbitration_blocker`: `When both branches are eligible, current LGRC producer semantics expose a tie/no-arbitration state rather than choosing one branch.`

## Controls

- `symmetric_tie_no_arbitration`: passed=`True`, blocker=`both_branches_eligible_no_native_arbitration`, outcome=`tie_no_native_arbitration`
- `single_branch_disabled`: passed=`True`, blocker=`east_branch_producer_disabled`, outcome=`unique_branch_by_native_eligibility`
- `budget_limited_subthreshold`: passed=`True`, blocker=`branch_polarity_below_feedback_threshold`, outcome=`no_branch_eligible`
- `wrong_polarity`: passed=`True`, blocker=`feedback_wrong_polarity`, outcome=`no_branch_eligible`

## Checks

- `iteration_18d_available`: `True`
- `two_1d_branch_elements_declared`: `True`
- `shared_fork_source_declared`: `True`
- `native_surface_and_feedback_used_on_both_branches`: `True`
- `external_geometry_scorer_absent`: `True`
- `external_argmax_absent`: `True`
- `direct_branch_suppression_absent`: `True`
- `preauthored_input_to_output_lookup_absent`: `True`
- `north_and_east_dominant_lanes_select_distinct_branches`: `True`
- `branch_selection_by_native_eligibility`: `True`
- `native_arbitration_not_supported`: `True`
- `symmetric_tie_exposes_no_arbitration`: `True`
- `controls_fail_for_distinct_blockers`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `m6_composed_fork_candidate_passed`: `True`
- `all_recovery_pulses_feedback_authorized`: `True`
- `no_direct_writes`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_19_allowed`: `True`
- `port_graph_ceiling_to_test`: `s3_grid_composed_1d_fork_competition_candidate`
- `guidance`: `Iteration 19 may test whether branch-eligibility competition transfers to port graph mechanics. Native arbitration/choice for symmetric competing branches remains blocked.`

## Claim Boundary

This is a composed 1D fork competition candidate. It supports branch differentiation by native eligibility when one branch is subthreshold, but it does not support native branch arbitration, native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, identity-acceptance, inherited-N03, or unrestricted movement evidence.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18e_grid_composed_1d_fork_competition.py
```
