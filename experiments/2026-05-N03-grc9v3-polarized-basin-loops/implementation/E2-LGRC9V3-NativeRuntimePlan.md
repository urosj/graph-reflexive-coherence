# E2 LGRC9V3 Native Runtime Plan

## Purpose

E2 follows the closed E1 alignment branch.

E1 established:

```text
D2.3 mechanism -> LGRC-style event ledger
classification: adapter_compatible
native_lgrc9v3_execution: false
core_task_requested: false
```

E2 asks the next, stronger question:

```text
Can native LGRC9V3.step or LGRC9V3.run_event_queue produce the D2.3 packet
ledger through declared runtime primitives?
```

E2 remains experiment-local unless a later result explicitly requests a
separate core LGRC9V3 task.

## Claim Boundary

Supported if successful:

- LGRC9V3 can execute packet departure and arrival events corresponding to the
  D2.3 route.
- Runtime packet ledgers can be extracted into the E1 schema.
- Native packet event ordering, event-time keys, node proper-time updates, and
  node-plus-packet budgets can reproduce the E1 ledger contract.

Not automatically supported:

- native autonomous surplus-trigger generation;
- native `self_rearm` semantic evidence;
- native GRC9V3 loop formation;
- movement or locomotion;
- agency, intention, biological behavior;
- core `src/*` change.

## Core-Library Stop Rule

E2 may:

- instantiate existing `LGRC9V3`;
- use existing public runtime methods;
- write experiment-local route manifests, adapters, validators, and reports;
- compare runtime output to E1 ledgers.

E2 must not modify `src/*`.

If E2 requires a new runtime primitive, stop and record:

```text
missing primitive
why experiment-local adapter is insufficient
expected public surface
required tests
claim affected
```

## Execution Surfaces

E2 must keep these surfaces distinct.

| Surface | Meaning | Claim ceiling |
|---|---|---|
| `scheduled_packet_runtime` | Experiment schedules packets into existing LGRC9V3 queue. | Native packet execution, not autonomous loop. |
| `adapter_triggered_runtime` | Experiment-local trigger policy observes runtime state and schedules next packet. | Adapter-driven runtime loop. |
| `native_autonomous_runtime` | LGRC9V3's own producer/runtime surfaces create the needed packet sequence. | Native LGRC9V3 execution, if controls pass. |

The first useful target is `scheduled_packet_runtime`, because it tests the
runtime packet machinery without confusing it with trigger autonomy.

## Required Runtime Evidence

Every positive E2 result must record:

- runtime construction command;
- route manifest used;
- scheduled packets or producer policy used;
- `LGRC9V3.step` or `LGRC9V3.run_event_queue` invocation;
- runtime packet event records;
- extracted E1-compatible ledger;
- node-plus-packet budget audit;
- event-time and proper-time audit;
- topology-change audit;
- control lane behavior;
- comparison against E1 ledger expectations.

Every E2 report must state:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = true|false
adapter_only = true|false
movement_claim_allowed = false
```

## Non-Goals

E2 does not:

- tune D2.3 thresholds;
- rewrite D2.3 mechanics;
- change `src/*`;
- claim movement;
- claim native autonomous trigger production unless produced by existing native
  LGRC9V3 surfaces;
- erase the E1 conclusion.

## Iteration E2.0. Runtime Feasibility And Fixture Bridge

Goal:

```text
Prove that the N03 fixture can be instantiated as an LGRC9V3 runtime target
and that one scheduled packet can be executed through run_event_queue.
```

Checks:

- construct the relevant fixed-topology runtime fixture;
- declare a minimal pole/channel-to-node/edge route manifest;
- schedule one packet with `LGRC9V3.schedule_packet_departure`;
- run `LGRC9V3.run_event_queue`;
- extract packet departure and arrival evidence;
- verify event-time key advances through runtime event processing;
- verify local node proper-time update is recorded on arrival/departure;
- verify node-plus-packet budget is reconstructable;
- verify topology remains unchanged;
- record whether the fixture bridge requires any non-native assumptions.

Outputs:

- `configs/e2_lgrc9v3_route_manifest.json`
- `outputs/e2_0_runtime_feasibility.json`
- `reports/e2_0_runtime_feasibility.md`

Stop condition:

```text
If one scheduled packet cannot be executed and audited through existing
LGRC9V3 runtime methods, stop E2 and record a missing runtime primitive.
```

## Iteration E2.1. Scheduled Packet Route Replay

Goal:

```text
Replay one declared D2.3 route direction through native LGRC9V3 scheduled
packet execution.
```

Checks:

- use the E2 route manifest;
- schedule a bounded sequence of packets matching a D2.3 route;
- process the queue with `run_event_queue`;
- extract packet departures and arrivals;
- compare event order to the E1 canonical route;
- verify budget and topology audits;
- verify no native trigger or self-rearm claim is made.

Outputs:

- `outputs/e2_1_scheduled_packet_route_replay.json`
- `reports/e2_1_scheduled_packet_route_replay.md`

Claim ceiling:

```text
native_packet_execution = true
native_autonomous_trigger = false
```

## Iteration E2.2. Runtime Ledger Extractor

Goal:

```text
Convert LGRC9V3 runtime packet logs and StepResults into the E1 event-ledger
schema.
```

Checks:

- read runtime packet ledger and packet processing logs;
- emit E1-compatible `packet_departure` and `packet_arrival` records;
- mark experiment-inferred route, trigger, and self-rearm fields explicitly;
- preserve native event ids, scheduler indices, event-time keys, and proper-time
  updates where available;
- validate extracted ledgers with the E1.3 ledger-only validator.

Outputs:

- `outputs/e2_runtime_extracted_ledgers/*.jsonl`
- `outputs/e2_2_runtime_ledger_extraction.json`
- `reports/e2_2_runtime_ledger_extraction.md`

## Iteration E2.3. Adapter-Triggered Runtime Loop

Goal:

```text
Use existing LGRC9V3 packet execution while an experiment-local trigger policy
observes runtime state and schedules the next packet.
```

Checks:

- implement trigger policy outside `src/*`;
- trigger only from measured runtime state;
- schedule packets using existing `LGRC9V3.schedule_packet_departure`;
- process events using existing `LGRC9V3.step` or `run_event_queue`;
- extract the resulting runtime ledger;
- verify self-rearm evidence through returned-packet arrival followed by
  trigger-authorized departure;
- run controls: no-surplus, subthreshold, wrong-direction, forward-only,
  broken-return, scrambled-order;
- compare positive/control lanes against E1.3 expectations.

Outputs:

- `outputs/e2_3_adapter_triggered_runtime_loop.json`
- `reports/e2_3_adapter_triggered_runtime_loop.md`

Claim ceiling:

```text
adapter_driven_runtime_execution = true
native_autonomous_runtime_execution = false
```

## Iteration E2.4. Native Autonomy Feasibility Audit

Goal:

```text
Determine whether existing LGRC9V3 producer/autonomy surfaces can natively
produce the D2.3 state-triggered route without the experiment-local trigger
adapter.
```

Checks:

- inspect existing `set_causal_flux_routes`, `produce_events`, and
  `run_autonomous` surfaces;
- attempt a bounded native producer configuration if one is expressible;
- verify whether the trigger is route/state equivalent to D2.3;
- record gaps if native surplus-trigger semantics are absent;
- avoid adding new primitives.

Outputs:

- `outputs/e2_4_native_autonomy_feasibility.json`
- `reports/e2_4_native_autonomy_feasibility.md`

Allowed outcomes:

| Outcome | Meaning |
|---|---|
| `native_autonomy_feasible` | Existing runtime can natively produce the ledger surface. |
| `adapter_required` | Native packet execution works, but trigger semantics remain experiment-local. |
| `missing_trigger_primitive` | A core trigger/route primitive is needed for native autonomy. |
| `not_runtime_aligned` | Runtime output cannot express the D2.3 packet mechanism. |

## Iteration E2.5. Runtime Compatibility Closeout

Goal:

```text
Close E2 with a precise runtime classification and next-branch decision.
```

Possible classifications:

| Classification | Meaning |
|---|---|
| `native_packet_execution_compatible` | Existing LGRC9V3 can execute scheduled D2.3 packet routes. |
| `adapter_triggered_runtime_compatible` | Runtime can execute the loop with experiment-local trigger adapter. |
| `native_autonomous_runtime_compatible` | Existing LGRC9V3 autonomously produces the D2.3 ledger. |
| `missing_native_trigger_primitive` | Native autonomy requires a separate core task. |
| `not_lgrc9v3_runtime_compatible` | Runtime cannot reproduce the packet mechanism. |

Outputs:

- `outputs/e2_lgrc9v3_runtime_closeout.json`
- `reports/e2_lgrc9v3_runtime_closeout.md`

## Success Criteria

Minimum E2 success:

```text
LGRC9V3 can execute scheduled packet departure/arrival events for the D2.3
route, and the runtime output can be extracted into an E1-compatible ledger.
```

Stronger E2 success:

```text
LGRC9V3 can execute the self-rearming packet loop under an experiment-local
state-trigger adapter, with controls preserved.
```

Strongest E2 success:

```text
Existing native LGRC9V3 autonomous producer/runtime surfaces can produce the
D2.3 ledger without an experiment-local trigger adapter.
```

