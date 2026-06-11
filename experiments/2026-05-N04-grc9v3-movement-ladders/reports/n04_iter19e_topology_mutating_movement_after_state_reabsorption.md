# N04 Iteration 19-E Topology-Mutating Movement After State Reabsorption

Status: **passed**

Claim ceiling: `topology_mutating_movement_candidate`

Attempted promotion: `topology_mutating_movement_candidate`

Promotion result: `supported_candidate`

19-E reruns the strict 19-D topology-mutating movement gate after Phase 8 topology-state reabsorption support.

## Attempt

- topology event logged: `True`
- transported surface row emitted: `True`
- topology-state reabsorption emitted: `True`
- reabsorption action: `merged`
- post-topology packet scheduled: `True`
- post-topology packet processed by step: `True`
- producer reads transported digest: `True`
- producer uses reabsorption record: `True`
- budget exact after reabsorption: `True`
- budget exact after post-topology packet: `True`
- artifact-only replay passed: `True`

## Ledger State

- after initial packet: `{'packet_ledger_present': True, 'base_node_coherence_total': 5.9, 'ledger_node_coherence_total': 5.9, 'ledger_in_flight_packet_total': 0.1, 'ledger_conserved_budget_total': 6.0, 'node_plus_packet_total': 6.0, 'node_total_delta_ledger_minus_state': 0.0, 'fixed_topology': True, 'topology_change_allowed': False, 'packet_transport_through_topology_change': False}`
- after reabsorption: `{'packet_ledger_present': True, 'base_node_coherence_total': 6.0, 'ledger_node_coherence_total': 6.0, 'ledger_in_flight_packet_total': 0.0, 'ledger_conserved_budget_total': 6.0, 'node_plus_packet_total': 6.0, 'node_total_delta_ledger_minus_state': 0.0, 'fixed_topology': False, 'topology_change_allowed': True, 'packet_transport_through_topology_change': True}`
- after post-topology departure: `{'packet_ledger_present': True, 'base_node_coherence_total': 5.9, 'ledger_node_coherence_total': 5.9, 'ledger_in_flight_packet_total': 0.1, 'ledger_conserved_budget_total': 6.0, 'node_plus_packet_total': 6.0, 'node_total_delta_ledger_minus_state': 0.0, 'fixed_topology': False, 'topology_change_allowed': True, 'packet_transport_through_topology_change': True}`
- after post-topology arrival: `{'packet_ledger_present': True, 'base_node_coherence_total': 6.0, 'ledger_node_coherence_total': 6.0, 'ledger_in_flight_packet_total': 0.0, 'ledger_conserved_budget_total': 6.0, 'node_plus_packet_total': 6.0, 'node_total_delta_ledger_minus_state': 0.0, 'fixed_topology': False, 'topology_change_allowed': True, 'packet_transport_through_topology_change': True}`

## Controls

- `state_reabsorption_disabled_control`: passed=`True`, reason=`topology_state_reabsorption_required_before_producer_scheduling`
- `superseded_source_stale_read_control`: passed=`True`, reason=`producer_stale_surface_read_blocked`
- `topology_only_claim_promotion_control`: passed=`True`, reason=`runtime_topology_state_reabsorption_support_is_not_by_itself_choice_agency_or_identity_collapse`

## Checks

- `iteration_19c_adaptive_entry_passed`: `True`
- `iteration_19d_failed_for_expected_runtime_gap`: `True`
- `phase8_topology_state_reabsorption_supported`: `True`
- `committed_topology_event_logged`: `True`
- `transported_surface_row_emitted`: `True`
- `topology_state_reabsorption_record_emitted`: `True`
- `ledger_state_reabsorption_gap_resolved`: `True`
- `producer_reads_reabsorbed_transport`: `True`
- `post_topology_packet_work_scheduled`: `True`
- `post_topology_packet_work_processed_by_step`: `True`
- `post_topology_packet_budget_exact`: `True`
- `artifact_only_replay_passed`: `True`
- `disabled_reabsorption_control_blocks_scheduling`: `True`
- `superseded_source_read_control_still_passes`: `True`
- `topology_only_claim_control_passes`: `True`
- `claim_boundary_preserved`: `True`

## Boundary

19-E supports a topology-mutating movement candidate because post-topology packet work schedules and processes from lineage-current, reabsorbed native state. It does not support native LGRC choice selection, RC identity collapse, agency, locomotion-like behavior, biological behavior, identity acceptance, inherited-N03 movement, or unrestricted movement.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter19e_topology_mutating_movement_after_state_reabsorption.py
```
