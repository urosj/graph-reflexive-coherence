# E2.1 Scheduled Packet Route Replay

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e2_1_scheduled_packet_route_replay.py
```

Status: `passed`

Boundary:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = true
adapter_only = false
movement_claim_allowed = false
```

Claim ceiling:

```text
native_packet_execution = true
native_autonomous_trigger = false
native_self_rearm = false
scheduled_route_replay = true
loop_claim_allowed = false
```

## Audit

- `route_id`: `d2_3_cw_closed_loop`
- `scheduled_packet_count`: `8`
- `runtime_step_count`: `16`
- `departure_count`: `8`
- `arrival_count`: `8`
- `expected_hop_count`: `8`
- `expected_route_steps`: `[0, 1, 2, 3, 4, 5, 6, 7]`
- `departure_route_steps`: `[0, 1, 2, 3, 4, 5, 6, 7]`
- `arrival_route_steps`: `[0, 1, 2, 3, 4, 5, 6, 7]`
- `departure_sequence_matches_route`: `True`
- `arrival_sequence_matches_route`: `True`
- `departure_route_steps_match`: `True`
- `arrival_route_steps_match`: `True`
- `each_departure_has_exactly_one_matching_arrival`: `True`
- `matched_packet_count`: `8`
- `unmatched_departure_packet_ids`: `[]`
- `unmatched_arrival_packet_ids`: `[]`
- `mismatch_packet_ids`: `[]`
- `packet_ids_unique`: `True`
- `processed_only_packet_events`: `True`
- `all_packet_events_mapped_to_route`: `True`
- `all_packet_events_have_budget_error`: `True`
- `max_packet_event_budget_error`: `0.0`
- `event_time_keys`: `[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0]`
- `event_time_keys_monotonic`: `True`
- `proper_time_nodes_recorded_in_packet_events`: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]`
- `touched_route_nodes`: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]`
- `all_touched_route_nodes_have_proper_time`: `True`
- `packet_topology_mutation_count`: `0`
- `node_plus_packet_budget`: `1.0`
- `budget_error`: `0.0`
- `in_flight_packet_total`: `0.0`
- `topology_unchanged`: `True`
- `queue_empty`: `True`
- `native_trigger_claim_made`: `False`
- `native_self_rearm_claim_made`: `False`
- `single_packet_continuity_claim_made`: `False`
- `loop_claim_made`: `False`

## Expected Route

```text
S1_to_K2 -> K2_to_S2 -> S2_to_K1 -> K1_to_S1
```

## Runtime Route Records

| kind | T_e | scheduler | channel | hop | edge | source | target |
|---|---:|---:|---|---:|---:|---:|---:|
| lgrc9v3_packet_departure | 0.0 | 1 | S1_to_K2 | 0 | 1 | 1 | 2 |
| lgrc9v3_packet_arrival | 1.0 | 2 | S1_to_K2 | 0 | 1 | 1 | 2 |
| lgrc9v3_packet_departure | 2.0 | 3 | S1_to_K2 | 1 | 2 | 2 | 3 |
| lgrc9v3_packet_arrival | 3.0 | 4 | S1_to_K2 | 1 | 2 | 2 | 3 |
| lgrc9v3_packet_departure | 4.0 | 5 | K2_to_S2 | 0 | 4 | 4 | 5 |
| lgrc9v3_packet_arrival | 5.0 | 6 | K2_to_S2 | 0 | 4 | 4 | 5 |
| lgrc9v3_packet_departure | 6.0 | 7 | K2_to_S2 | 1 | 5 | 5 | 6 |
| lgrc9v3_packet_arrival | 7.0 | 8 | K2_to_S2 | 1 | 5 | 5 | 6 |
| lgrc9v3_packet_departure | 8.0 | 9 | S2_to_K1 | 0 | 7 | 7 | 8 |
| lgrc9v3_packet_arrival | 9.0 | 10 | S2_to_K1 | 0 | 7 | 7 | 8 |
| lgrc9v3_packet_departure | 10.0 | 11 | S2_to_K1 | 1 | 8 | 8 | 9 |
| lgrc9v3_packet_arrival | 11.0 | 12 | S2_to_K1 | 1 | 8 | 8 | 9 |
| lgrc9v3_packet_departure | 12.0 | 13 | K1_to_S1 | 0 | 10 | 10 | 11 |
| lgrc9v3_packet_arrival | 13.0 | 14 | K1_to_S1 | 0 | 10 | 10 | 11 |
| lgrc9v3_packet_departure | 14.0 | 15 | K1_to_S1 | 1 | 11 | 11 | 0 |
| lgrc9v3_packet_arrival | 15.0 | 16 | K1_to_S1 | 1 | 11 | 11 | 0 |

## Interpretation

Existing LGRC9V3 runtime methods can replay the declared D2.3 clockwise route as a scheduled sequence of packet departure and arrival events with conserved node-plus-packet budget and unchanged topology. This establishes native scheduled route-level packet execution only; native trigger production and self-rearm semantics remain unclaimed.
