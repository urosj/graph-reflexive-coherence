# N04 Iteration 18-G Integrated 2D Composed Gate

Status: **passed**

Claim ceiling: `s3_grid_integrated_2d_composed_gate_candidate`

Iteration 18-G integrates the 18-C two-input/two-output gate shape with 18-E composed 1D branch competition and 18-F balanced local preference tie-breaking.

## Summary

- achieved level: `M6`
- entry ceiling: `s3_grid_balanced_local_preference_fork_competition_candidate`
- selected branches: `{'west_input': 'north_branch', 'south_input': 'east_branch'}`
- remaining blocker: `The result is fixed-topology 2D composed-gate evidence, not native LGRC choice selection, RC collapse, port-graph, or adaptive topology.`

## Controls

- `no_preference_reproduces_18e_no_arbitration`: passed=`True`, reason=`both_branches_eligible_no_native_arbitration`, outcome=`tie_no_native_arbitration`
- `dominant_branch_overrides_local_preference`: passed=`True`, reason=`dominant_east_branch_remains_eligible_despite_north_local_preference`, outcome=`unique_branch_by_native_eligibility`
- `epsilon_does_not_force_strong_two_branch_choice`: passed=`True`, reason=`both_strong_branches_remain_eligible`, outcome=`tie_no_native_arbitration`
- `global_preference_sum_zero`: passed=`True`, reason=`paired_local_preferences_cancel_globally`, outcome=`global_unbiased`

## Checks

- `iteration_18f_available`: `True`
- `two_input_gates_declared`: `True`
- `two_output_branches_declared`: `True`
- `composed_1d_branches_used`: `True`
- `balanced_local_preferences_used`: `True`
- `global_preference_sum_zero`: `True`
- `external_scorer_absent`: `True`
- `external_argmax_absent`: `True`
- `west_and_south_inputs_select_distinct_outputs`: `True`
- `native_branch_eligibility_selects_outputs`: `True`
- `no_preference_reproduces_18e_no_arbitration`: `True`
- `dominant_branch_overrides_local_preference`: `True`
- `epsilon_does_not_force_strong_two_branch_choice`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `m6_integrated_2d_gate_candidate_passed`: `True`
- `all_recovery_pulses_feedback_authorized`: `True`
- `broader_claims_blocked`: `True`

## Claim Boundary

This supports a fixed-topology 2D composed-gate candidate. It does not support native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph transfer, topology-mutating movement, adaptive topology, broad geometry-transfer, locomotion-like behavior, biological behavior, identity acceptance, inherited-N03 movement, or unrestricted movement.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18g_integrated_2d_composed_gate.py
```
