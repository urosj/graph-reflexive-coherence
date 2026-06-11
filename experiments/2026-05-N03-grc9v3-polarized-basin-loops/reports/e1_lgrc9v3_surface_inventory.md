# E1.0 LGRC9V3 Surface Inventory

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e1_0_lgrc9v3_surface_inventory.py
```

Status: `complete`

Classification: `adapter_compatible`

Boundary:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = false
adapter_only = true
movement_claim_allowed = false
```

## Summary

Existing LGRC9V3 surfaces are sufficient for packet records, event queue ordering, in-flight packet budgets, causal clocks, runtime state snapshots, telemetry/checkpoint overlays, and queued packet execution. D2.3 still needs an experiment-local adapter for pole/channel route semantics and measured pole-surplus state triggers.

## Required Questions

### Does LGRC9V3 already expose packet departure / arrival records?

Answer: `yes`

Evidence:

- LGRC9V3PacketQueueEventRecord
- LGRC9V3_PACKET_EVENT_KIND_DEPARTURE
- LGRC9V3_PACKET_EVENT_KIND_ARRIVAL
- schedule_lgrc9v3_packet_departure
- process_lgrc9v3_packet_arrival

### Does LGRC9V3 already expose a packet ledger with in-flight amount?

Answer: `yes`

Evidence:

- LGRC9V3PacketLedger.in_flight_packet_total
- LGRC9V3PacketLedger.packet_records
- LGRC9V3PacketLedger.event_queue_records

### Does LGRC9V3 serialize event-time key, proper time, and node update timing?

Answer: `yes`

Evidence:

- LGRC9V3RuntimeState.event_time_key
- LGRC9V3RuntimeState.node_proper_time
- LGRC9V3RuntimeState.node_last_update_proper_time
- LGRC9V3RuntimeState.node_last_update_event_time_key
- classify_lgrc9v3_step_extension
- build_lgrc9v3_graph_checkpoint

### Does LGRC9V3 distinguish event-time key from node proper time?

Answer: `yes`

Evidence:

- LGRC9V3RuntimeState.event_time_key
- LGRC9V3RuntimeState.node_proper_time
- LGRC9V3.step advances a local node proper-time surface from processed packet events

### Does LGRC9V3 expose enough state to reconstruct budget: sum(C_i) + sum(packet_amount)?

Answer: `yes`

Evidence:

- LGRC9V3PacketLedger.node_coherence_total
- LGRC9V3PacketLedger.in_flight_packet_total
- LGRC9V3PacketLedger.conserved_budget_total
- LGRC9V3PacketLedger.budget_error

### Does LGRC9V3 have a route/causal channel abstraction, or must E1 define an experiment-local route manifest?

Answer: `partial`

Evidence:

- LGRC9V3RuntimeState.causal_flux_routes
- LGRC9V3.set_causal_flux_routes
- LGRC9V3.produce_events can schedule packet departures from flux routes

Gap:

D2.3 pole/channel cycle semantics are not a native LGRC9V3 route manifest. E1 still needs an experiment-local route mapping from D2.3 poles/channels to LGRC9V3 node/edge packet routes.

### Does LGRC9V3 have a native state-trigger surface, or is D2.3's trigger an experiment-local policy?

Answer: `experiment-local policy`

Evidence:

- LGRC9V3 has autonomous packet production from configured flux routes
- No native source-pole-mass-minus-reference threshold trigger was found

Gap:

D2.3's measured pole-surplus threshold trigger should be represented as an experiment-local policy in E1. A native trigger primitive would require a separate core task.

## Sufficient Existing Surfaces

- `LGRC9V3PacketRecord`
- `LGRC9V3PacketQueueEventRecord`
- `LGRC9V3PacketLedger`
- `LGRC9V3RuntimeState`
- `schedule_lgrc9v3_packet_departure`
- `process_lgrc9v3_packet_departure`
- `process_lgrc9v3_packet_arrival`
- `process_lgrc9v3_next_packet_event`
- `LGRC9V3.schedule_packet_departure`
- `LGRC9V3.step`
- `LGRC9V3.run_event_queue`
- `LGRC9V3.set_causal_flux_routes`
- `classify_lgrc9v3_step_extension`
- `build_lgrc9v3_graph_checkpoint`

## Missing Or Adapter-Only Surfaces

- `d2_3_pole_channel_route_manifest`: `experiment_local_adapter_required`
  LGRC9V3 supports node/edge causal flux routes, but D2.3 defines poles and ordered channels at experiment level.
- `source_pole_surplus_trigger_policy`: `experiment_local_adapter_required`
  LGRC9V3 does not expose a native trigger of the form source_pole_mass - reference_pole_mass >= threshold.
- `d2_3_self_rearm_event_kind`: `experiment_local_adapter_required`
  LGRC9V3 can represent the packet arrival and next departure, but D2.3's semantic self_rearm label is experiment-level evidence.

## Source References

### classes

- `LGRC9V3PacketRecord` -> `src/pygrc/models/lgrc_9_v3_packets.py:37`
- `LGRC9V3PacketQueueEventRecord` -> `src/pygrc/models/lgrc_9_v3_packets.py:113`
- `LGRC9V3PacketLedger` -> `src/pygrc/models/lgrc_9_v3_packets.py:311`
- `LGRC9V3RuntimeState` -> `src/pygrc/models/lgrc_9_v3_runtime_state.py:482`
- `LGRC9V3` -> `src/pygrc/models/lgrc_9_v3_runtime.py:173`

### functions

- `build_lgrc9v3_packet_ledger` -> `src/pygrc/models/lgrc_9_v3_packets.py:950`
- `schedule_lgrc9v3_packet_departure` -> `src/pygrc/models/lgrc_9_v3_packets.py:1238`
- `process_lgrc9v3_packet_departure` -> `src/pygrc/models/lgrc_9_v3_packets.py:1353`
- `process_lgrc9v3_packet_arrival` -> `src/pygrc/models/lgrc_9_v3_packets.py:1624`
- `process_lgrc9v3_next_packet_event` -> `src/pygrc/models/lgrc_9_v3_packets.py:1759`
- `derive_lgrc9v3_packet_arrival_event_time_key` -> `src/pygrc/models/lgrc_9_v3_packets.py:785`
- `ordered_lgrc9v3_event_queue` -> `src/pygrc/models/lgrc_9_v3_runtime_state.py:42`
- `restore_lgrc9v3_runtime_state_artifact` -> `src/pygrc/models/lgrc_9_v3_runtime_state.py:339`
- `classify_lgrc9v3_step_extension` -> `src/pygrc/telemetry/lgrc9v3_contract.py:291`
- `build_lgrc9v3_graph_checkpoint` -> `src/pygrc/telemetry/lgrc9v3_contract.py:442`

### runtime_methods

- `LGRC9V3.schedule_packet_departure` -> `src/pygrc/models/lgrc_9_v3_runtime.py:1163`
- `LGRC9V3.step` -> `src/pygrc/models/lgrc_9_v3_runtime.py:2245`
- `LGRC9V3.run_event_queue` -> `src/pygrc/models/lgrc_9_v3_runtime.py:2484`
- `LGRC9V3.set_causal_flux_routes` -> `src/pygrc/models/lgrc_9_v3_runtime.py:1048`
- `LGRC9V3.produce_events` -> `src/pygrc/models/lgrc_9_v3_runtime.py:1008`
- `LGRC9V3.run_autonomous` -> `src/pygrc/models/lgrc_9_v3_runtime.py:2557`

