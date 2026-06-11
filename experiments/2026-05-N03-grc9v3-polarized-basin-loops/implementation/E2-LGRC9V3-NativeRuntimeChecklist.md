# E2 LGRC9V3 Native Runtime Checklist

This checklist tracks the experiment-local E2 branch.

Primary plan:

- [`E2-LGRC9V3-NativeRuntimePlan.md`](./E2-LGRC9V3-NativeRuntimePlan.md)

## Ground Rules

- Keep E2 under
  `experiments/2026-05-N03-grc9v3-polarized-basin-loops/`.
- Do not modify `src/*`.
- Treat any required `src/*` change as a stop condition.
- E2 is not a global implementation branch unless separately promoted.
- E2 starts from E1's closeout:
  `native_grc9v3_negative`, `packet_positive`,
  `lgrc_adapter_compatible`, `native_lgrc9v3_execution = false`.
- Do not claim movement, locomotion, agency, intention, biological behavior, or
  multi-pole native behavior.
- Distinguish scheduled packet execution, adapter-triggered execution, and
  native autonomous execution in every report.
- Generated E2 reports must state:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = true|false
adapter_only = true|false
movement_claim_allowed = false
```

## E2.0. Runtime Feasibility And Fixture Bridge

Status: complete.

### Goal

Prove that the N03 fixture can be instantiated as an LGRC9V3 runtime target and
that one scheduled packet can be executed through `run_event_queue`.

### Checks

- [x] Construct the relevant fixed-topology runtime fixture.
- [x] Declare pole/channel-to-node/edge route manifest.
- [x] Schedule one packet with `LGRC9V3.schedule_packet_departure`.
- [x] Run `LGRC9V3.run_event_queue`.
- [x] Extract packet departure evidence.
- [x] Extract packet arrival evidence.
- [x] Verify event-time key advances through runtime event processing.
- [x] Verify local node proper-time update is recorded.
- [x] Verify node-plus-packet budget is reconstructable.
- [x] Verify topology remains unchanged.
- [x] Record any non-native fixture bridge assumptions.

### Outputs

- [x] `configs/e2_lgrc9v3_route_manifest.json`
- [x] `outputs/e2_0_runtime_feasibility.json`
- [x] `reports/e2_0_runtime_feasibility.md`

### Verification

- [x] Command recorded.
- [x] One scheduled packet executes through existing runtime methods.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e2_0_runtime_feasibility.py
```

Result:

```json
{"arrival_seen": true, "budget_error": 0.0, "departure_seen": true, "runtime_step_count": 2, "status": "passed", "topology_unchanged": true}
```

Summary:

- E2.0 instantiated a 12-node / 12-edge LGRC9V3 ported-ring fixture.
- This was the E2 bridge fixture inherited from the original N03 12-node
  ported-ring exploration. It was used to prove native packet execution,
  route replay, ledger extraction, and adapter-trigger compatibility on the
  earlier ring substrate. It is not the compact E3 native reproduction fixture.
- It wrote the route manifest at `configs/e2_lgrc9v3_route_manifest.json`.
- It scheduled one packet on the first `S1_to_K2` route hop using
  `LGRC9V3.schedule_packet_departure`.
- It processed the queue with `LGRC9V3.run_event_queue`.
- The runtime emitted one packet departure and one packet arrival.
- Event-time advanced from `0.0` to `1.0`.
- Source and target node proper-time surfaces were recorded.
- Node-plus-packet budget reconstructed exactly with `budget_error = 0.0`.
- Topology remained unchanged.
- Claim ceiling:
  `native_packet_execution = true`,
  `native_autonomous_trigger = false`,
  `native_self_rearm = false`,
  `loop_claim_allowed = false`.
- Boundary:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = true`,
  `adapter_only = false`,
  `movement_claim_allowed = false`.

## E2.1. Scheduled Packet Route Replay

Status: complete.

### Goal

Replay one declared D2.3 route direction through native LGRC9V3 scheduled
packet execution.

### Checks

- [x] Use the E2 route manifest.
- [x] Schedule a bounded sequence of packets matching a D2.3 route.
- [x] Process the queue with `run_event_queue`.
- [x] Extract packet departures.
- [x] Extract packet arrivals.
- [x] Compare event order to the E1 canonical route.
- [x] Verify node-plus-packet budget.
- [x] Verify topology audit.
- [x] Verify no native trigger claim is made.
- [x] Verify no native `self_rearm` claim is made.

### Outputs

- [x] `outputs/e2_1_scheduled_packet_route_replay.json`
- [x] `reports/e2_1_scheduled_packet_route_replay.md`

### Verification

- [x] Command recorded.
- [x] Runtime event order matches the declared route.
- [x] Claim ceiling states `native_packet_execution = true` and
      `native_autonomous_trigger = false`.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e2_1_scheduled_packet_route_replay.py
```

Result:

```json
{"arrival_sequence_matches_route": true, "budget_error": 0.0, "departure_sequence_matches_route": true, "runtime_step_count": 16, "scheduled_packet_count": 8, "status": "passed", "topology_unchanged": true}
```

Summary:

- E2.1 reused the E2 route manifest and replayed
  `d2_3_cw_closed_loop`.
- It scheduled 8 bounded packet departures across the declared route hops:
  `S1_to_K2`, `K2_to_S2`, `S2_to_K1`, and `K1_to_S1`.
- It processed the queue with existing `LGRC9V3.run_event_queue`.
- The runtime emitted 8 packet departures and 8 packet arrivals.
- Both departure and arrival sequences matched the declared route order.
- Route-step sequences were independently verified as `[0,1,2,3,4,5,6,7]`
  for both departures and arrivals.
- Each departure had exactly one matching arrival with the same packet id,
  amount, channel, route step, hop, edge, source, and target.
- Each packet event carried a per-event budget audit with
  `max_packet_event_budget_error = 0.0`.
- Event-time keys were monotonic across the replay.
- All route-touched source/target nodes had proper-time surfaces recorded.
- Packet event topology mutation count was `0`.
- Node-plus-packet budget reconstructed exactly with `budget_error = 0.0`.
- Topology remained unchanged and the packet queue drained.
- Claim ceiling:
  `native_packet_execution = true`,
  `native_autonomous_trigger = false`,
  `native_self_rearm = false`,
  `scheduled_route_replay = true`,
  `loop_claim_allowed = false`.
- Boundary:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = true`,
  `adapter_only = false`,
  `movement_claim_allowed = false`.
- E2.1 makes no native trigger, native self-rearm, single-packet continuity, or
  loop claim.

## E2.2. Runtime Ledger Extractor

Status: complete.

### Goal

Convert LGRC9V3 runtime packet logs and `StepResult`s into the E1 event-ledger
schema.

### Checks

- [x] Read runtime packet ledger.
- [x] Read packet processing logs.
- [x] Read `StepResult` events/bookkeeping.
- [x] Emit E1-compatible `packet_departure` records.
- [x] Emit E1-compatible `packet_arrival` records.
- [x] Preserve native event ids where available.
- [x] Preserve native scheduler event indices.
- [x] Preserve native event-time keys.
- [x] Preserve native node proper-time updates where available.
- [x] Mark experiment-inferred route fields.
- [x] Mark experiment-inferred trigger fields.
- [x] Mark experiment-inferred `self_rearm` fields.
- [x] Validate extracted ledgers with the E1.3 ledger-only validator or its E2
      equivalent.

### Outputs

- [x] `outputs/e2_runtime_extracted_ledgers/*.jsonl`
- [x] `outputs/e2_2_runtime_ledger_extraction.json`
- [x] `reports/e2_2_runtime_ledger_extraction.md`

### Verification

- [x] Command recorded.
- [x] Extracted ledger validates against schema.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/extract_e2_2_runtime_ledgers.py
```

Result:

```json
{"errors": [], "event_kind_counts": {"control_blocked": 6, "cycle_complete": 20, "packet_arrival": 250, "packet_departure": 250, "self_rearm": 18, "state_trigger": 125}, "ledger_count": 8, "status": "passed"}
```

Summary:

- E2.2 extracted 8 per-lane JSONL ledgers from the E2.3 runtime artifact.
- Packet departure and arrival records preserve native event ids, native
  scheduler event indices, native event-time keys, and native proper-time
  updates where present.
- Route, pole, trigger, self-rearm, cycle-complete, and control-blocked fields
  are explicitly marked as experiment-inferred or adapter-derived evidence.
- Ledger-only validation reproduces the E2.3 positive and negative lane
  classifications.
- Terminal adapter triggers whose child departure was not processed inside the
  bounded event window are excluded from ledger evidence.
- Event kind counts:
  `packet_departure = 250`,
  `packet_arrival = 250`,
  `state_trigger = 125`,
  `self_rearm = 18`,
  `cycle_complete = 20`,
  `control_blocked = 6`.

## E2.3. Adapter-Triggered Runtime Loop

Status: complete.

### Goal

Use existing LGRC9V3 packet execution while an experiment-local trigger policy
observes runtime state and schedules the next packet.

### Checks

- [x] Implement trigger policy outside `src/*`.
- [x] Trigger only from measured runtime state.
- [x] Schedule packets using existing `LGRC9V3.schedule_packet_departure`.
- [x] Process events using existing `LGRC9V3.step` or `run_event_queue`.
- [x] Extract the resulting runtime ledger.
- [x] Verify returned-packet arrival precedes trigger-authorized departure.
- [x] Verify self-rearm evidence is adapter-derived, not native.
- [x] Run no-surplus control.
- [x] Run subthreshold control.
- [x] Run wrong-direction control.
- [x] Run forward-only control.
- [x] Run broken-return control.
- [x] Run scrambled-order control.
- [x] Compare positive/control lanes against E1.3 expectations.

### Outputs

- [x] `outputs/e2_3_adapter_triggered_runtime_loop.json`
- [x] `reports/e2_3_adapter_triggered_runtime_loop.md`

### Verification

- [x] Command recorded.
- [x] Controls remain negative.
- [x] Positive lanes, if any, are classified as adapter-driven runtime
      execution, not native autonomous execution.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e2_3_adapter_triggered_runtime_loop.py
```

Result:

```json
{"classification": "adapter_triggered_runtime_loop_with_controls", "errors": [], "positive_rows": ["E2.3-P-adapter-triggered-cw", "E2.3-R-adapter-triggered-ccw"], "status": "passed", "symmetry_passed": true}
```

Summary:

- E2.3 used an experiment-local surplus trigger adapter while keeping packet
  departure and arrival processing inside existing `LGRC9V3.run_event_queue`.
- Positive rows:
  `E2.3-P-adapter-triggered-cw`,
  `E2.3-R-adapter-triggered-ccw`.
- Negative controls remained negative:
  no-surplus, subthreshold, wrong-direction, forward-only, broken-return, and
  scrambled-order.
- Direction reversal symmetry passed.
- Positive rows reached 10 completed cycles and 9 adapter-derived self-rearm
  events whose child departure was processed inside the bounded runtime event
  window.
- Node-plus-packet budget remained conserved with `max budget error = 0.0` and
  `max event budget error = 2.22045e-16`.
- Topology remained unchanged in all lanes.
- Claim ceiling:
  `native_packet_execution = true`,
  `adapter_driven_runtime_execution = true`,
  `native_autonomous_runtime_execution = false`,
  `native_autonomous_trigger = false`,
  `native_self_rearm = false`,
  `adapter_triggered_self_rearm = true`,
  `loop_claim_allowed = false`.
- Boundary:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = true`,
  `adapter_only = false`,
  `movement_claim_allowed = false`.
- Trigger authorization, route semantics, and self-rearm labels remain
  experiment-local adapter evidence, not native LGRC9V3 producer/autonomy
  evidence.

## E2.3-A. Adapter-Triggered Runtime Loop Hardening

Status: complete.

### Goal

Validate E2.3 from its artifact-level evidence before E2.5 closeout.

### Checks

- [x] Confirm adapter trigger reads only runtime-exposed state fields recorded
      in the artifact.
- [x] Verify each counted self-rearm follows:
      returned packet arrival,
      measured surplus above threshold,
      adapter-authorized child departure.
- [x] Reproduce positive and negative classifications from event records
      without runner internals.
- [x] Compare clockwise/counter-clockwise symmetry across cycle count, trigger
      count, continuation count, rearm count, runtime event count, departure
      count, arrival count, budget error, event budget error, and
      trigger-to-departure timing.
- [x] Preserve and validate per-event budget audits.

### Outputs

- [x] `outputs/e2_3a_adapter_triggered_runtime_loop_hardening.json`
- [x] `reports/e2_3a_adapter_triggered_runtime_loop_hardening.md`

### Verification

- [x] Command recorded.
- [x] Artifact-only validation passes.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e2_3_adapter_triggered_runtime_loop.py
```

Result:

```json
{"adapter_state_visibility_passed": true, "direction_symmetry_passed": true, "errors": [], "ledger_only_validation_passed": true, "per_event_budget_preserved": true, "self_rearm_causality_passed": true, "status": "passed"}
```

Summary:

- E2.3-A reads only `outputs/e2_3_adapter_triggered_runtime_loop.json`.
- Adapter trigger records contain measured surplus, threshold, event time,
  packet id, parent packet id, source pole, and triggered channel; no hidden
  D2.3 arrays are needed for validation.
- Counted self-rearm evidence requires a returned packet arrival, threshold
  crossing, and processed child departure.
- Ledger-only validation reproduces the two positive rows and all negative
  controls.
- Direction symmetry holds across event counts, rearm counts, budget errors,
  and trigger-to-departure timing.
- Per-event budget audits remain within tolerance with max event budget error
  `2.22045e-16`.

## E2.4. Native Autonomy Feasibility Audit

Status: complete.

### Goal

Determine whether existing LGRC9V3 producer/autonomy surfaces can natively
produce the D2.3 state-triggered route without the experiment-local trigger
adapter.

### Checks

- [x] Inspect existing `set_causal_flux_routes` surface.
- [x] Inspect existing `produce_events` surface.
- [x] Inspect existing `run_autonomous` surface.
- [x] Attempt bounded native producer configuration if expressible.
- [x] Verify whether native trigger is route/state equivalent to D2.3.
- [x] Record gaps if native surplus-trigger semantics are absent.
- [x] Avoid adding new primitives.
- [x] Decide between `native_autonomy_feasible`, `adapter_required`,
      `missing_trigger_primitive`, and `not_runtime_aligned`.

### Outputs

- [x] `outputs/e2_4_native_autonomy_feasibility.json`
- [x] `reports/e2_4_native_autonomy_feasibility.md`

### Verification

- [x] Command recorded.
- [x] Feasibility classification is explicit.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e2_4_native_autonomy_feasibility.py
```

Result:

```json
{"adapter_required_for_d2_3_semantics": true, "classification": "native_static_route_autonomy_feasible_d2_3_surplus_trigger_missing", "native_d2_3_equivalent": false, "native_static_route_probe": "passed", "status": "passed"}
```

Summary:

- E2.4 inspected the native `set_causal_flux_routes`, `produce_events`, and
  `run_autonomous` surfaces.
- Existing LGRC9V3 can run a bounded native static closed-route packet autonomy
  probe using `packet_departure_from_flux_route_policy`.
- The native probe produced 40 packet departures, 40 packet arrivals, and 40
  local updates in 80 runtime steps.
- Node-plus-packet budget reconstructed exactly with `budget_error = 0.0`.
- Topology remained unchanged.
- This native surface is stronger than E1's adapter-only classification:
  LGRC9V3 can natively produce static route packet work and arrival-triggered
  route forwarding.
- It is not D2.3-equivalent:
  native routes are node/edge keyed, not pole-mask keyed;
  there is no native source-pole surplus threshold trigger;
  there is no native D2.3 self-rearm semantic label.
- Classification:
  `native_static_route_autonomy_feasible_d2_3_surplus_trigger_missing`.
- E2.3 remains the correct D2.3-aligned runtime result, while E2.4 records the
  existing native static-route autonomy surface and the missing native
  surplus-trigger primitive.
- No core task was requested.

## E2.4-A. Native Autonomy Boundary Hardening

Status: complete.

### Goal

Preserve E2.4's claim boundary before E2.5 closeout.

### Checks

- [x] Confirm native static-route autonomy exists.
- [x] Confirm native packet route production exists.
- [x] Confirm native arrival-triggered route forwarding exists.
- [x] Confirm native pole-mask route semantics are absent.
- [x] Confirm native source-pole surplus threshold trigger is absent.
- [x] Confirm native D2.3 self-rearm semantic label is absent.
- [x] Confirm D2.3-equivalent native autonomy is not claimed.
- [x] Confirm the adapter remains required for D2.3 semantics.
- [x] Confirm no core task is requested by this experiment closeout.

### Outputs

- [x] `outputs/e2_4a_native_autonomy_boundary.json`
- [x] `reports/e2_4a_native_autonomy_boundary.md`

### Verification

- [x] Command recorded.
- [x] Boundary validation passes.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e2_4_native_autonomy_boundary.py
```

Result:

```json
{"adapter_required_for_d2_3_semantics": true, "errors": [], "native_d2_3_equivalent": false, "native_static_route_autonomy_exists": true, "status": "passed"}
```

Summary:

- E2.4-A confirms that native static-route autonomy exists.
- It also confirms that D2.3-equivalent autonomy is not currently native:
  pole-mask route semantics, source-pole surplus threshold trigger, and the
  D2.3 self-rearm semantic label remain absent as native primitives.
- The adapter remains required for D2.3 semantics.
- No core task is requested by this experiment closeout.

## E2.5. Runtime Compatibility Closeout

Status: complete.

### Goal

Close E2 with a precise runtime classification and next-branch decision.

### Possible Classifications

- [x] `native_packet_execution_compatible`
- [x] `adapter_triggered_runtime_compatible`
- [x] `missing_native_trigger_primitive`

Non-selected E2 closeout classifications:

```text
native_autonomous_runtime_compatible
not_lgrc9v3_runtime_compatible
```

These are not pending tasks. E2 captured the pre-core state where native packet
execution and static-route autonomy existed, but D2.3-equivalent pole-surplus
trigger and self-rearm semantics were still missing.

### Outputs

- [x] `outputs/e2_lgrc9v3_runtime_closeout.json`
- [x] `reports/e2_lgrc9v3_runtime_closeout.md`

### Verification

- [x] Closeout records all commands and artifacts.
- [x] Closeout preserves native-negative / packet-positive / adapter-compatible
      distinctions.
- [x] Closeout states whether a core task is requested.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/build_e2_5_runtime_closeout.py
```

Result:

```json
{"core_task_requested": false, "errors": [], "native_d2_3_equivalent_autonomy": false, "selected_classifications": ["native_packet_execution_compatible", "adapter_triggered_runtime_compatible", "native_static_route_autonomy_available", "missing_native_surplus_trigger_primitive"], "status": "passed"}
```

Summary:

- E2 is closed.
- Selected classifications:
  `native_packet_execution_compatible`,
  `adapter_triggered_runtime_compatible`,
  `native_static_route_autonomy_available`,
  `missing_native_surplus_trigger_primitive`.
- Existing LGRC9V3 can execute scheduled packet departure/arrival events.
- Existing LGRC9V3 can replay the declared D2.3 packet route when packets are
  scheduled.
- Existing LGRC9V3 can run native static route autonomy through causal flux
  routes and autonomous producers.
- E2.3 demonstrates a D2.3-aligned adapter-triggered runtime loop with controls
  preserved.
- E2.2 extracts replayable E1-compatible ledgers from E2.3 runtime evidence.
- Existing native autonomy is not D2.3-equivalent because pole-mask route
  semantics, source-pole surplus threshold trigger, and D2.3 self-rearm labels
  remain adapter-derived.
- No movement, locomotion, agency, biological, or native GRC9V3 loop claim is
  made.
- No `src/*` change or core task is requested by this experiment closeout.

Postscript after Phase 8/E3:

```text
E2 remains historically correct as the pre-core native-runtime compatibility
branch.
The missing native trigger primitive was later implemented in the separate
Phase 8 native packet-loop continuation.
E3 later reproduced D2.3 using native LGRC9V3 packet-loop surfaces only.
```
