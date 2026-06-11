# Phase 8 LGRC9 Native Packet-Loop Continuation Plan

## Purpose

This document promotes the N03 polarized-basin-loop experiment findings into a
Phase 8 core implementation continuation.

The N03 result is intentionally two-part:

```text
native fixed-topology GRC9V3 proposal flux:
    negative for polarized loop formation under tested fixtures

experiment-local conserved packet layer:
    positive for scheduled packet loops,
    positive for state-triggered packet departure,
    positive for self-rearming packetized pulse cycles
```

E2 then showed that existing `LGRC9V3` can execute packet routes natively, but
does not yet provide the full D2.3 semantics as native runtime primitives.

This plan defines the next Phase 8 work:

```text
Make the D2.3 state-triggered, self-rearming packet-loop mechanism a native
LGRC9V3 runtime surface, without changing the deterministic step boundary.
```

Companion checklist:

- [`Phase-8-LGRC9-NativePacketLoopChecklist.md`](./Phase-8-LGRC9-NativePacketLoopChecklist.md)

## Inputs

Primary implementation context:

- [`Phase-8-LGRC9-ImplementationPlan.md`](./Phase-8-LGRC9-ImplementationPlan.md)
- [`Phase-8-LGRC9-ImplementationChecklist.md`](./Phase-8-LGRC9-ImplementationChecklist.md)
- [`../specs/lgrc-9-v3-spec.md`](../specs/lgrc-9-v3-spec.md)
- [`../docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md`](../docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md)

Experiment evidence:

- [`../experiments/2026-05-N03-grc9v3-polarized-basin-loops/implementation/E1-LGRC9V3-AlignmentPlan.md`](../experiments/2026-05-N03-grc9v3-polarized-basin-loops/implementation/E1-LGRC9V3-AlignmentPlan.md)
- [`../experiments/2026-05-N03-grc9v3-polarized-basin-loops/implementation/E2-LGRC9V3-NativeRuntimePlan.md`](../experiments/2026-05-N03-grc9v3-polarized-basin-loops/implementation/E2-LGRC9V3-NativeRuntimePlan.md)
- [`../experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e2_lgrc9v3_runtime_closeout.md`](../experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e2_lgrc9v3_runtime_closeout.md)
- [`../experiments/2026-05-N03-grc9v3-polarized-basin-loops/implementation/E3-LGRC9V3-NativePacketLoopReproductionPlan.md`](../experiments/2026-05-N03-grc9v3-polarized-basin-loops/implementation/E3-LGRC9V3-NativePacketLoopReproductionPlan.md)
- [`../experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e3_native_lgrc9v3_packet_loop_closeout.md`](../experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e3_native_lgrc9v3_packet_loop_closeout.md)

## E2 Closeout Boundary

E2 selected these classifications:

```text
native_packet_execution_compatible
adapter_triggered_runtime_compatible
native_static_route_autonomy_available
missing_native_surplus_trigger_primitive
```

Existing native `LGRC9V3` already supports:

- scheduled packet departure and arrival processing;
- route-based packet forwarding through existing causal flux routes;
- static-route autonomous production;
- deterministic `step()` consumption;
- bounded `run_autonomous(...)`;
- node-plus-packet budget auditing.

Existing native `LGRC9V3` does not yet provide:

- pole-mask route semantics as a first-class runtime concept;
- a source-pole surplus threshold trigger producer;
- native self-rearm evidence labels for:

```text
returned packet arrival
-> measured source surplus crosses threshold
-> child packet departure is scheduled
```

These missing surfaces are the implementation target.

## Scope

In scope:

- native LGRC9V3 packet-loop route descriptors;
- pole/aspect region definitions over nodes;
- channel route definitions over existing node/edge routes;
- source-pole surplus threshold trigger policy;
- state-triggered packet departure producer;
- native self-rearm causality evidence;
- replayable event-ledger extraction from native runtime evidence;
- controls equivalent to N03 D2.3/E2:
  no-surplus,
  subthreshold,
  wrong-direction,
  forward-only,
  broken-return,
  scrambled-order;
- budget, event ordering, proper-time, and topology audits;
- examples that show producer-generated packet loops through `step()` or
  `run_autonomous(...)`.

Out of scope:

- movement or locomotion claims;
- agency, intention, or biological claims;
- native GRC9V3 proposal-flux loop claims;
- threshold tuning to force a positive result;
- replacing `LGRC9V3.step()` with an opaque all-in-one loop;
- general LGRC, `LGRC9`, or `LGRCV3` runtimes;
- N03 generated-output cleanup.

## Runtime Boundary

The existing Phase 8 autonomy boundary remains in force:

```text
produce_events(...):
    inspect runtime state and enqueue eligible causal work

step():
    consume exactly one queued event and mutate runtime state

run_autonomous(...):
    bounded producer + step loop
```

This continuation must not make `step()` discover all work implicitly. New
autonomy belongs in explicit, policy-gated producers whose evidence is
serialized.

## Design Requirements

### 1. Native Route-Aspects

Add a native route-aspect description that can express the N03 pole/channel
surface without depending on experiment-local arrays.

Minimum fields:

```text
route_id
direction
pole_regions
channel_sequence
source_pole
target_pole
node_route
edge_route
expected_next_channel
```

The route-aspect surface may compile to existing node/edge causal flux routes,
but the original pole/channel intent must remain serializable.

### 2. Surplus Trigger Producer

Add a producer policy that can schedule packet departure when a measured pole
surplus crosses a threshold:

```text
pole_mass - reference_mass >= trigger_threshold
```

The producer must record:

```text
producer_policy
route_id
pole_id
reference_mass
observed_mass
surplus
trigger_threshold
eligible_channel
scheduled_packet_id
event_time_key
reason_code
```

The producer schedules work only. `step()` still owns mutation.

### 3. Native Self-Rearm Evidence

Self-rearm evidence is native only when the runtime can reconstruct this chain:

```text
parent packet arrives
arrival updates node/pole coherence
measured surplus crosses threshold
producer schedules child departure
child departure is processed
```

The evidence must preserve:

```text
parent_packet_id
child_packet_id
arrival_event_id
trigger_event_id or producer_record_id
departure_event_id
route_id
channel_order
event_time ordering
node proper-time updates
```

### 4. Conservation And Replay

Every positive result must be reconstructable from runtime artifacts:

```text
sum node coherence + sum in-flight packet coherence = B
```

Budget must be audited at each packet transition, not only at final state.

### 5. Post-Arrival Trigger Ordering

Native self-rearm evidence is valid only if producer evaluation happens after
the parent arrival mutation has been committed by `step()`.

The required order is:

```text
step() processes parent packet arrival
arrival credits target/source pole coherence
producer observes the post-arrival runtime state
producer records threshold crossing
producer schedules child packet departure
step() later processes child departure
```

Pre-arrival observations cannot support self-rearm evidence.

### 6. Route-Aspect Replay Identity

D2.3-style claims depend on declared route semantics. Route-aspect config must
therefore be part of replay identity.

Minimum identity fields:

```text
route_aspect_id
route_aspect_digest
pole_region_digest
channel_sequence_digest
```

The digest input should be canonicalized so replay validators can detect
changed pole masks, changed route order, changed channel definitions, or
changed direction conventions.

### 7. Duplicate Trigger Suppression

The native producer must not schedule duplicate child packets from the same
surplus crossing in the same eligibility window.

Acceptable policies include:

```text
producer_epoch_id
last_triggered_route_step
trigger_consumed_until_arrival
refractory_event_count
```

This is deterministic producer hygiene, not a biological refractory claim.

### 8. Claim Labels

Native runtime reports must state:

```text
native_lgrc9v3_execution = true
native_packet_execution = true
native_surplus_trigger = true|false
native_self_rearm_evidence = true|false
native_d2_3_equivalent = true|false
adapter_required_for_d2_3_semantics = true|false
native_static_route_only = true|false
native_grc9v3_loop_evidence = false
movement_claim_allowed = false
```

`native_static_route_only` distinguishes existing native route autonomy from
the stronger D2.3-equivalent surplus-triggered self-rearming route.

## Proposed Iterations

### Iteration 43. Baseline Freeze And E2 Fixture Import

Freeze the current Phase 8/E2 baseline before source changes. Import the E2
route manifest and runtime closeout expectations into tests without changing
runtime behavior.

### Iteration 44. Native Route-Aspect Contract

Add the serializable pole/channel route-aspect contract and compile it to the
existing route surfaces where possible.

### Iteration 45. Surplus Trigger Producer

Add a policy-gated producer that schedules packet departures from measured
pole surplus. It must be disabled by default.

### Iteration 46. Self-Rearm Causality Evidence

Record native self-rearm chains from parent arrival through trigger to child
departure. Keep this as evidence; do not make it a movement or identity claim.

### Iteration 47. D2.3 Native Control Parity

Run N03-equivalent controls through native runtime surfaces:

```text
no-surplus
subthreshold
wrong-direction
forward-only
broken-return
scrambled-order
clockwise/counter-clockwise symmetry
```

### Iteration 48. Snapshot, Telemetry, And Reference Surfaces

Expose route-aspect, trigger, and self-rearm evidence in snapshots, telemetry,
and reference docs as family extensions.

### Iteration 49. Native Packet-Loop Closeout

Produce a closeout that states whether native `LGRC9V3` now supports the D2.3
semantics without an experiment-local adapter.

Closeout result:

```text
native_d2_3_equivalent_packet_loop_supported
adapter_required_for_d2_3_semantics = false for validated native rows
```

The N03 E3 reproduction branch verifies that the D2.3 packet-loop result can be
reproduced using native LGRC9V3 route-aspects, surplus-trigger producers,
`step()` packet processing, self-rearm evidence, snapshots, telemetry, and
artifact-only validation. E3 is an experiment-local reproduction, not an
additional core implementation dependency.

## Acceptance Criteria

This continuation is accepted only if:

- the pre-change E2 baseline is frozen;
- route-aspect definitions serialize and round-trip;
- route-aspect digests are recorded and validated;
- the surplus-trigger producer is policy-gated and disabled by default;
- packet departure still mutates state only through `step()`;
- producer evidence remains eligibility/scheduling evidence only;
- every positive packet loop preserves node-plus-packet budget;
- trigger evaluation for self-rearm happens after parent arrival mutation;
- duplicate trigger suppression is deterministic and audited;
- self-rearm evidence is reconstructable from runtime event records;
- D2.3-equivalent negative controls remain negative;
- ledger-only validation from native artifacts reproduces positive and
  negative classifications;
- clockwise and counter-clockwise directions are symmetric within declared
  tolerances;
- snapshots and telemetry preserve the new evidence without breaking old
  artifacts;
- no movement, locomotion, agency, biological, or native GRC9V3 loop claim is
  emitted.
