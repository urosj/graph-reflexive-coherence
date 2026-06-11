# LGRC9V3 Implementation State And Design Tension

Date: 2026-05-07
Updated: 2026-05-16

Status: current state recorded; future Phase 8 plan/checklist items should be
derived from this record before further LGRC9V3 design work.

## Purpose

This note records the state of the LGRC9V3 implementation after the Phase 8
runtime, telemetry, visualization, examples, stress checks, and corrected
cascade comparison.

It is not an implementation checklist. It is a design-state record: what is
solid, where code shape is now creating pressure, and which follow-up items
should be considered for the Phase 8 plan/checklist.

## Current Runtime State

LGRC9V3 now has a concrete executable model class:

```text
pygrc.models.LGRC9V3
```

The active runtime shape is composed:

```text
LGRC9V3RuntimeState =
    GRC9V3State
    + LGRC9V3PacketLedger
    + deterministic packet event queue
    + causal timing/checkpoint fields
```

The runtime does not call synchronous `GRC9V3.step()`. It owns native LGRC
queue processing through:

```text
LGRC9V3.step()
LGRC9V3.run_event_queue(max_events=...)
```

Current `LGRC9V3.step()` processes one deterministic queued event:

```text
packet departure;
packet arrival;
scheduled causal boundary-birth trial.
```

On packet arrival, it can:

```text
advance target-local proper time;
emit packet-arrival eligibility;
apply explicit packetized local-update routes;
evaluate causally scheduled Lane A/Lane B spark diagnostics;
route allowed causal topology integration;
transport packets through refinement;
inherit proper time across refinement.
```

The runtime also exposes explicit helper-owned surfaces for:

```text
collapse/reabsorption evidence;
collapse packet transport;
proper-time identity evaluation;
identity acceptance;
topology replay validation.
```

## What Is Solid

The implementation has strong behavioral correctness evidence:

- packetized budget accounting is audited;
- proper-time surfaces are serialized in checkpoints;
- event queue ordering is deterministic;
- Lane A/Lane B GRC9V3 spark predicates can be evaluated at LGRC causal
  boundaries;
- mechanical expansion remains distinct from identity acceptance;
- packet transport through refinement is explicit;
- boundary birth is represented as a causal event and can be enabled/disabled;
- telemetry and graph checkpoint surfaces expose LGRC9V3 causal evidence;
- stress tests pass;
- the corrected front-capacity cascade comparison reaches the same final
  topological surface under synchronous `GRC9V3` and native `LGRC9V3` queue
  execution.

The corrected comparison is reproducible through:

```bash
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
```

Expected corrected comparison boundary:

```text
GRC9V3:
    20 synchronous steps
    final topology = 29 nodes / 28 edges

LGRC9V3:
    100 native queue events
    final topology = 29 nodes / 28 edges
    max packet budget error ~= 2.84e-14
```

This is runtime evidence, not a claim that one LGRC event equals one GRC step.

## Synchronous GRC Versus LGRC Execution Roles

The N03 polarized-basin-loop experiment clarified a useful architectural
division between synchronous GRC-family runtimes and native LGRC execution.

Synchronous `GRC9V3` and `GRCV3` remain valuable as global relaxation,
redistribution, and structure-formation surfaces:

```text
given current coherence + geometry + couplings
-> recompute proposal flux
-> redistribute coherence
-> update diagnostics, topology, and identity surfaces
```

They are well suited for:

```text
basin formation and refinement;
coherence settling;
gradient-like redistribution;
instability and spark-candidate detection;
topology growth/pruning decisions;
collapse/reabsorption decisions;
landscape generation;
structural attractor comparison.
```

They are not the best native surface for persistent in-flight transport,
delayed causal handoff, self-rearming pulse loops, or local event-time
propagation. N03 tested that boundary directly: native fixed-topology
`GRC9V3` proposal flux behaved as a conservative relaxation surface on the
tested fixtures and did not generate the polarized packet loop.

Native `LGRC9V3` is the complementary causal-history execution layer:

```text
LGRC9V3:
    packet departure;
    in-flight packet coherence;
    packet arrival;
    post-arrival local state;
    event producer;
    next queued causal event.
```

The E3 native packet-loop reproduction shows that this layer can support an
internal self-rearming packetized pulse under conservation. Informally, this is
a "heartbeat"; precisely, it is a native `LGRC9V3` self-rearming packetized
causal pulse. It is not a perpetual-motion claim and not native `GRC9V3`
proposal-flux loop evidence.

## 2026-05-16 Extension Status

Phase 8 has since added two native LGRC9V3 continuation surfaces:

```text
native_d2_3_equivalent_packet_loop_supported
native_lgrc_pulse_substrate_surface_supported
```

The native packet-loop continuation promotes the N03/E3 packet-loop result
into native `LGRC9V3` route-aspect and surplus-trigger producer evidence.

The causal pulse-substrate continuation adds a default-off native surface over
committed packet events, plus policy-gated coupling and feedback producers.
The producer/step boundary remains intact:

```text
producer:
    reads committed surface evidence
    emits producer evidence
    schedules packet work through LGRC scheduling

step():
    consumes queued packet work
    mutates coherence and packet budget
```

N04 then used the extension to open a bounded native M6 candidate:

```text
claim_ceiling = native_m6_same_fixture_self_renewal_candidate
native_m6_candidate_gate_passed = true
native_m6 = true
movement_claim_allowed = false
```

This is a same-fixture self-renewal candidate on `S0_chain_v1`: after one
seeded packet contact, native feedback eligibility rows authorize regenerated
packet work through the native feedback producer for both forward and reversed
boundary polarity. It is not a locomotion-like, adaptive-topology, biological,
agency, identity-acceptance, inherited-N03 movement, or unrestricted movement
claim.

Current evidence pointers:

```text
implementation/Phase-8-LGRC9-Closeout.md
implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.md
experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_m6_same_fixture_validator.json
experiments/2026-05-N04-grc9v3-movement-ladders/reports/native_m6_same_fixture_validator.md
```

The recommended architecture is therefore:

```text
GRC/GRC9V3/GRCV3:
    build or diagnose coherence structures, basins, corridors, boundaries,
    and instability surfaces.

LGRC9V3:
    run causal packet histories and recurrent packet-pulse transport through
    those structures.

Movement experiments:
    test whether causal pulses couple to boundaries under a separate movement
    ladder and explicit claim discipline.
```

This split should guide future work. Adding the packet heartbeat directly to
synchronous `GRC9V3` or `GRCV3` as default behavior would blur the negative
GRC9V3 result and the positive LGRC9V3 result. If synchronous runtimes need to
interact with packet loops, they should diagnose, export, or approximate them
through explicitly named modes rather than silently inheriting LGRC semantics.

## Current Code Shape

The implementation grew through correctness-first iterations. That was the
right development path, but the resulting code shape is now visibly under
pressure.

Current module sizes:

```text
src/pygrc/models/lgrc_9_v3.py                8413 lines
src/pygrc/models/lgrc_9_v3_runtime.py        1801 lines
src/pygrc/models/lgrc_9_v3_runtime_state.py   189 lines
```

The large `lgrc_9_v3.py` module currently owns too many distinct concerns:

```text
policy constants;
field-name contracts;
schema versions;
annotation artifacts;
lapse/delay/distance helpers;
packet records and ledgers;
packet scheduling and processing;
pending-flux compaction;
refinement packet transport;
collapse/reabsorption evidence;
collapse packet transport;
proper-time inheritance;
proper-time identity evaluation;
identity acceptance;
topology replay validation;
artifact restore functions.
```

This is coherent historically, but it is not a clean long-term module boundary.

## GRC9V3 Substrate Dependency

LGRC9V3 currently reuses the proven `GRC9V3State` substrate and selected
`GRC9V3` mechanics.

This is intentional and still valid:

```text
GRC9V3State:
    topology, node state, port graph, basin/sink surfaces, conductance,
    flux, Hessian/spark diagnostic substrate

LGRC9V3RuntimeState:
    causal queue, packet ledger, event-time key, local proper time,
    causal modes, LGRC logs
```

The distinction is important:

```text
The state substrate is reused.
The synchronous GRC9V3.step() loop is not the LGRC event loop.
```

However, the reuse now creates design friction:

```text
landscape seed -> GRC9V3 lowering -> wrap into LGRC9V3
```

instead of a first-class path:

```text
landscape seed -> LGRC9V3 runtime
```

## Deterministic Step Boundary

There is a deterministic LGRC9V3 `step()` method today. The missing piece is
not deterministic event consumption. The missing piece is first-class,
deterministic event production and scenario initialization.

Current distinction:

```text
LGRC9V3.step():
    deterministic event consumer

examples/lgrc9v3/corrected_cascade_comparison.py:
    schedules initial packet;
    schedules causal boundary-birth trial;
    injects broad seed packets after early events;
    configures graph routes from current topology;
    then calls LGRC9V3.step().
```

That orchestration is meaningful, but it lives in an example script. This makes
larger LGRC9V3 runs more error-prone than they should be.

The intended future boundary should be closer to:

```text
LGRC9V3.from_landscape_seed(...)
LGRC9V3.prime_event_queue(...)
LGRC9V3.configure_routes_from_topology(...)
LGRC9V3.run_event_queue(max_events=...)
```

or equivalent helper/facade names.

## Concrete Loop Gap

This issue was moved into the Phase 8 checklist and closed in Iteration 34.

Original gap:

```text
LGRC9V3.step()
    can process packet events or scheduled boundary-birth trials.

LGRC9V3.run_event_queue(max_events=...)
    checked only packet event_queue_records before deciding to stop.
```

Current contract:

```text
packet event queue empty
AND boundary birth trial queue empty
```

`run_event_queue(...)` now uses this queue-exhaustion condition.

## Landscape Loading State

LGRC9V3 can run from a landscape-derived state today through the substrate
route:

```text
LandscapeSeed
  -> extract GRCL9V3 extension
  -> compile GRCL9V3 source
  -> lower to GRC9V3State
  -> LGRC9V3.from_state(...)
  -> run LGRC9V3 event queue
```

That is semantically valid because `LGRC9V3` composes a `GRC9V3State`.

What is missing is a first-class LGRC9V3 landscape-loading facade:

```text
build_lgrc9v3_from_landscape_seed(...)
run_lgrc9v3_landscape_seed(...)
LGRC9V3.from_landscape_seed(...)
```

The current path is too easy to get wrong because users must know where source
loading ends, where GRC9V3 lowering begins, and where LGRC event-queue priming
begins.

## Snapshot/Restore State

`LGRC9V3.snapshot()` exists and records the composed runtime state.

Native `LGRC9V3.load(...)` is now implemented as of Phase 8 Iteration 37.

```text
LGRC9V3.save(...) / LGRC9V3.load(...) restore native LGRC9V3 runtime snapshots.
```

The restore path preserves:

```text
base GRC9V3 state;
causal modes;
packet ledger;
event queue;
boundary birth queue;
proper-time surfaces;
last-update event-time surfaces;
local-update logs;
packet-processing logs;
causal spark logs;
topology event logs.
```

Plain `GRC9V3` snapshots remain `GRC9V3` snapshots and are not silently loaded
as native `LGRC9V3`.

## Post-37 Runtime State

Phase 8 Iterations 33-37 closed the immediate design-correctness pressure
without changing LGRC9V3 semantics.

Current state:

```text
LGRC9V3.step()
    solid deterministic queue executor

LGRC9V3.run_event_queue(max_events=...)
    bounded loop over step(), draining packet events and boundary-birth trials

LGRC9V3.from_landscape_seed(...)
    first-class landscape-backed construction facade

LGRC9V3.save(...) / LGRC9V3.load(...)
    native runtime snapshot round-trip

LGRC9V3.produce_events(policy="disabled")
    Iteration 38 no-op autonomous producer contract

lgrc_9_v3.py
    compatibility facade over ownership-specific modules
```

The important boundary is:

```text
LGRC9V3.step() consumes scheduled causal work.
It should remain deterministic and auditable.
```

The remaining runtime-design tension is not the executor. It is **event
production**.

## Autonomy Tension

LGRC9V3 can now execute causal events correctly, but the runtime still relies
on construction helpers or explicit API calls to schedule much of the work.

Current examples and facades can seed:

```text
packet departures;
route tables;
boundary-birth trials;
corrected-cascade-style initial queues.
```

That is reproducible, but not yet very autonomous. A user still has to know
which producer helper to call before `step()` has work to consume.

The next useful design move is not to make `step()` opaque. The correct split
is:

```text
LGRC9V3.step()
    deterministic executor

LGRC9V3.produce_events(...)
    policy-gated scheduler/producer that inspects the current state and
    enqueues eligible causal work

LGRC9V3.run_autonomous(...)
    bounded loop that calls produce_events(...) when queues need work, then
    calls step()
```

First autonomous producer scope should be intentionally narrow:

```text
packet departures from explicit flux/route policy;
boundary-birth trial scheduling when the policy is enabled;
causal spark diagnostics remain tied to arrivals/local updates;
collapse/reabsorption and identity acceptance remain explicit or separately
    gated;
every generated event carries producer policy, reason code, thresholds, and
    observed evidence.
```

Autonomy should schedule work. `step()` should still be the only default path
that consumes scheduled work and mutates runtime state.

Iteration 38 implemented the disabled/no-op producer contract. Iteration 39
implemented the first active producer:

```text
packet_departure_from_flux_route_policy
```

This producer inspects explicit `causal_flux_routes`, schedules packet
departures with auditable producer evidence, and leaves queue consumption and
budget mutation to `step()`.

Iteration 40 implemented the second active producer:

```text
boundary_birth_trial_policy
```

This producer inspects open boundary ports, computes outward flux pressure,
records explicit birth probability and RNG sample evidence, and schedules
causal boundary-birth trials. Acceptance/rejection and topology mutation remain
owned by `step()`.

Iteration 41 implemented the bounded autonomous run loop:

```text
LGRC9V3.run_autonomous(...)
```

The loop runs producers when model-owned queues are empty, consumes work only
through `step()`, respects `max_events`, and records producer/consumer summary
evidence in step bookkeeping and runtime cached quantities.

Iteration 42 added the user-facing autonomy examples:

```text
examples/lgrc9v3/autonomous_produce_then_step.py
examples/lgrc9v3/autonomous_run.py
```

These examples make the accepted boundary visible:

```text
produce_events(...):
    enqueue causal work

step():
    consume one queued event

run_autonomous(...):
    bounded producer + step loop
```

## Refactor Pressure

This is now real refactor pressure under the project policy:

```text
Do not create code geometry changes unless there is tension.
```

The tension is not abstract line-count discomfort. It appears in usage:

- before Iteration 34, model-owned `run_event_queue(...)` was narrower than
  `step()`'s actual work surface;
- before Iteration 35, `lgrc_9_v3.py` had become a mixed
  contract/helper/processor/restore module;
- before Iteration 36, landscape-backed LGRC9V3 construction required manual
  multi-stage wiring;
- before Iteration 36, corrected cascade orchestration lived in an example
  rather than a tested scenario/runtime policy;
- before Iteration 37, native LGRC snapshot restore was missing;
- after Iteration 37, the remaining pressure is autonomous event production.

## Candidate Phase 8 Plan Items

The following items record the post-32 design pressure. Iterations 33-37 have
now promoted and completed the baseline-freeze, queue-ownership, module-split,
runtime-facade, and snapshot-restore items. The remaining active candidate
surface is autonomous event production.

### Design Cleanup Without Semantic Change

Split `lgrc_9_v3.py` by ownership while preserving imports and behavior:

```text
lgrc_9_v3_contract.py:
    constants, field names, schema versions, allowed policy values

lgrc_9_v3_timing.py:
    lapse, delay, distance, causal annotation, LGRC-0/LGRC-1 surfaces

lgrc_9_v3_packets.py:
    packet records, packet ledgers, scheduling, processing, compaction

lgrc_9_v3_topology.py:
    refinement packet transport, boundary birth, collapse/reabsorption,
    collapse packet transport, topology replay validation

lgrc_9_v3_identity.py:
    proper-time inheritance, proper-time identity evaluation,
    identity acceptance

lgrc_9_v3_runtime.py:
    model-owned orchestration only
```

Keep compatibility exports from `pygrc.models` during the split.

### Refactor Constraints

The split should be a strict behavior-preserving refactor. Do not mix semantic
changes with file movement.

The intended module dependency shape is a DAG:

```text
lgrc_9_v3_contract.py
    imports:
        core typing/dataclasses/constants only

lgrc_9_v3_timing.py
    imports:
        contract
        GRC9V3State

lgrc_9_v3_packets.py
    imports:
        contract
        GRC9V3State

lgrc_9_v3_topology.py
    imports:
        contract
        packets
        GRC9V3State / GRCEvent

lgrc_9_v3_identity.py
    imports:
        contract
        topology artifacts as needed

lgrc_9_v3_runtime.py
    imports:
        timing
        packets
        topology
        identity

lgrc_9_v3.py
    compatibility re-export facade
```

Hard rules:

```text
contract imports no split modules;
runtime may import split modules;
split modules do not import runtime;
tests migrate to specific modules gradually;
old pygrc.models.lgrc_9_v3 imports keep working during transition.
```

Each split module should define an explicit `__all__`.

The legacy module should remain as a thin facade during the transition:

```python
from .lgrc_9_v3_contract import *
from .lgrc_9_v3_packets import *
from .lgrc_9_v3_topology import *
from .lgrc_9_v3_identity import *
from .lgrc_9_v3_timing import *
from .lgrc_9_v3_runtime import LGRC9V3
```

Verification for the split should include:

```text
compile all model modules;
run targeted LGRC9V3 tests;
smoke-test old import path;
smoke-test specific split-module imports;
confirm no circular import through runtime.
```

### Runtime Facades

Add tested runtime-level helpers for common usage:

```text
from_landscape_seed / build_lgrc9v3_from_landscape_seed;
queue priming from current topology;
route configuration from topology;
scenario/run policy for corrected cascade style runs;
native LGRC9V3 save/load parity.
```

### Deterministic Queue Ownership

Move example-owned orchestration into tested runtime or helper policy:

```text
initial packet seeding;
boundary-birth trial scheduling;
broad packet seeding;
route generation from current topology;
empty-queue handling across packet and boundary queues.
```

### Documentation And Examples

Update examples after the runtime facade exists:

```text
examples/landscapes/run_seed_lgrc9v3.py
examples/lgrc9v3/corrected_cascade_comparison.py
```

The examples should become thin demonstrations of library-owned behavior, not
the owners of core scheduling policy.

### Autonomous Producer Layer

Add a policy-gated event producer without changing `step()` into an opaque
all-in-one loop:

```text
produce_events(...)
    inspect current runtime state
    enqueue eligible packet departures or boundary-birth trials
    serialize producer evidence
    do not consume queued events

run_autonomous(...)
    bounded producer + step() loop
```

Completed and remaining producer surfaces:

```text
packet departure producer from explicit flux/route policy: complete;
boundary-birth trial producer when birth policy is enabled: complete;
autonomous run loop: complete;
examples and handoff: complete.
```

## Current Decision

Do not redesign LGRC semantics now.

Do not treat the current design tension as a reason to discard the working
runtime.

Do record autonomous event production as a legitimate next engineering phase:

```text
Behavior first succeeded.
Code ownership and usage entry points caught up in Iterations 33-37.
Now producer autonomy can be added above the deterministic executor.
```
