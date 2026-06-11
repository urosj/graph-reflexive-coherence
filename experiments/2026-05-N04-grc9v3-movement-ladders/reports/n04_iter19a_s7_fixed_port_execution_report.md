# N04 Iteration 19-A S7 Fixed-Port Execution

Status: **passed**

Claim ceiling: `s7_fixed_port_composed_gate_candidate`

Iteration 19-A executes the Iteration 19 role-based S7 fixed-port mapping with topology mutation disabled.

## Port Lanes

- `west_in_to_north_out`: input=`west_in`, output=`north_out`, selected=`north_branch`, passed=`True`
- `south_in_to_east_out`: input=`south_in`, output=`east_out`, selected=`east_branch`, passed=`True`

## Controls

- `no_preference_reproduces_18e_no_arbitration`: passed=`True`, reason=`both_branches_eligible_no_native_arbitration`, outcome=`tie_no_native_arbitration`
- `dominant_branch_overrides_local_preference`: passed=`True`, reason=`dominant_east_branch_remains_eligible_despite_north_local_preference`, outcome=`unique_branch_by_native_eligibility`
- `epsilon_does_not_force_strong_two_branch_choice`: passed=`True`, reason=`both_strong_branches_remain_eligible`, outcome=`tie_no_native_arbitration`
- `global_preference_sum_zero`: passed=`True`, reason=`paired_local_preferences_cancel_globally`, outcome=`global_unbiased`
- `topology_mutation_disabled_control`: passed=`True`, reason=`runtime_topology_mutation_disabled_for_19a`, outcome=`no_topology_events_emitted`
- `port_rewiring_disabled_control`: passed=`True`, reason=`fixed_port_graph_rewiring_disabled`, outcome=`no_port_rewiring_emitted`

## Checks

- `iteration_19_contract_passed`: `True`
- `mapping_id_matches_contract`: `True`
- `fixed_port_graph_used`: `True`
- `topology_mutation_disabled`: `True`
- `port_rewiring_disabled`: `True`
- `west_port_selects_north_output`: `True`
- `south_port_selects_east_output`: `True`
- `native_branch_eligibility_selects_outputs`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `all_recovery_pulses_feedback_authorized`: `True`
- `s7_fixed_port_execution_passed`: `True`
- `no_topology_events`: `True`
- `no_port_rewiring`: `True`
- `no_preference_still_blocks_native_arbitration`: `True`
- `dominant_branch_overrides_local_preference`: `True`
- `epsilon_does_not_force_strong_two_branch_choice`: `True`
- `broader_claims_blocked`: `True`

## Boundary

The target fixture is `S7_port_graph_fixed_composed_gate_v1`. This is fixed-port S7 transfer evidence only: topology mutation, port rewiring, adaptive topology, native LGRC choice selection, RC identity collapse, locomotion-like behavior, agency, and unrestricted movement remain blocked.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter19a_s7_fixed_port_execution.py
```
