# N04 Iteration 21-B Native LGRC Route-Arbitration Rerun

Status: **passed**

Claim ceiling: `topology_mutating_movement_candidate`

Attempted promotion: `native_lgrc_route_arbitration_selection_candidate`

Promotion result: `runtime_route_arbitration_supported_choice_claim_blocked`

Previous blocker: `native_lgrc_topology_route_selection_not_exposed`

Primary blocker: `null`

Iteration 21-B reruns the route-selection boundary after Phase 8 native route arbitration.

## Positive Lane

- candidate route count: `2`
- arbitration reason: `native_route_arbitration_selected_highest_score`
- selected candidate: `route_a_collapse_to_sink_0`
- selected topology event references arbitration: `True`
- producer reads transported digest: `True`
- producer uses reabsorption record: `True`
- scheduled packet processed by step: `True`
- artifact replay valid: `True`

## Controls

- `unresolved_tie_control`: passed=`True`, reason=`native_route_arbitration_unresolved_tie`
- `hidden_input_control`: passed=`True`, reason=`native_route_arbitration_hidden_input_rejected`
- `claim_promotion_control`: passed=`True`, reason=`route_arbitration_is_not_semantic_choice_or_agency`

## Checks

- `iteration_20_baseline_passed`: `True`
- `phase8_native_route_arbitration_closed`: `True`
- `candidate_route_set_emitted`: `True`
- `native_route_arbitration_record_emitted`: `True`
- `selected_topology_event_from_arbitration_record`: `True`
- `selected_route_not_experiment_if_else`: `True`
- `surface_lineage_and_reabsorption_consumed_selected_event`: `True`
- `producer_scheduled_from_reabsorbed_transport`: `True`
- `scheduled_packet_processed_by_step`: `True`
- `artifact_only_route_arbitration_replay_passed`: `True`
- `old_primary_blocker_resolved`: `True`
- `unresolved_tie_control_blocks_selection`: `True`
- `hidden_input_control_blocks_selection`: `True`
- `claim_boundary_preserved`: `True`

## Boundary

Iteration 21-B resolves the old route-selection exposure blocker as runtime route arbitration: candidate routes are formed from committed runtime-visible evidence, serialized policy selects one route, the selected topology event cites the arbitration record, and artifact-only replay reconstructs the downstream lineage/reabsorption/producer/step chain. This is not semantic choice, agency, or RC identity collapse.

Native route arbitration support remains distinct from semantic choice, agency, RC identity collapse, identity acceptance, locomotion-like behavior, biological behavior, inherited-N03 movement, and unrestricted movement.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter21b_native_lgrc_route_arbitration_rerun.py
```
