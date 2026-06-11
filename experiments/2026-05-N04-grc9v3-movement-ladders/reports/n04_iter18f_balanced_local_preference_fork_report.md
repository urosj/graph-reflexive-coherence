# N04 Iteration 18-F Balanced Local Preference Fork

Status: **passed**

Claim ceiling: `s3_grid_balanced_local_preference_fork_competition_candidate`

Iteration 18-F tests whether tiny balanced local preferences can remove the 18-E tie/no-arbitration blocker without adding a global selector.

## Reasoning

Iteration 18-E showed that composed 1D branches can differentiate by native eligibility, but a symmetric eligible fork has no native arbitration. Iteration 18-F adds paired local epsilon preferences with zero global branch-preference sum. The epsilon is allowed to break near-threshold local ties, but it must not become a global argmax or override stronger branch evidence.

## Summary

- achieved level: `M6`
- entry ceiling: `s3_grid_composed_1d_fork_competition_candidate`
- selected branches: `{'north_local_preference_tie_break': 'north_branch', 'east_local_preference_tie_break': 'east_branch', 'east_dominant_overrides_north_preference': 'east_branch'}`
- remaining blocker: `This is local symmetry breaking by declared epsilon, not native LGRC choice selection, RC identity collapse, or agency.`

## Preference Policy

- epsilon: `0.03`
- global preference sum: `{'north_branch': 0.0, 'east_branch': 0.0}`
- global directional preference: `none`

## Controls

- `no_preference_remains_no_arbitration`: passed=`True`, reason=`both_branches_eligible_no_native_arbitration`, outcome=`tie_no_native_arbitration`
- `north_local_preference_resolves_tie`: passed=`True`, reason=`east_branch_damped_below_threshold_by_local_epsilon`, outcome=`unique_branch_by_native_eligibility`
- `east_local_preference_resolves_tie`: passed=`True`, reason=`north_branch_damped_below_threshold_by_local_epsilon`, outcome=`unique_branch_by_native_eligibility`
- `epsilon_not_global_override`: passed=`True`, reason=`both_strong_branches_remain_eligible_epsilon_does_not_force_choice`, outcome=`tie_no_native_arbitration`

## Checks

- `iteration_18e_available`: `True`
- `balanced_local_preference_policy_declared`: `True`
- `epsilon_declared_before_run`: `True`
- `global_preference_sum_zero`: `True`
- `external_scorer_absent`: `True`
- `external_argmax_absent`: `True`
- `north_and_east_preferences_resolve_local_ties`: `True`
- `unbiased_tie_still_exposes_18e_blocker`: `True`
- `epsilon_does_not_force_global_choice`: `True`
- `dominant_signal_overrides_local_preference`: `True`
- `m6_balanced_preference_candidate_passed`: `True`
- `all_recovery_pulses_feedback_authorized`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `broader_claims_blocked`: `True`

## Claim Boundary

This supports balanced local preference as a near-tie symmetry breaker for composed LGRC branch competition. It is not native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, identity-acceptance, inherited-N03, or unrestricted movement evidence.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter18f_balanced_local_preference_fork.py
```
