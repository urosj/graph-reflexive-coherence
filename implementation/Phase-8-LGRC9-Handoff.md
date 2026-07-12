# Phase 8 LGRC-9 Handoff

This handoff records the current Phase 8 implementation state after Iteration
34, the deterministic queue ownership patch.

The implemented target is `LGRC9V3`: causal-history evidence and a narrow
packet event-queue shell over the existing `GRC9V3` state substrate. This is
not executable `LGRC9`, and not executable `LGRCV3`.

The current executable LGRC9V3 shape is composed:

```text
LGRC9V3RuntimeState =
    GRC9V3State
    + LGRC9V3PacketLedger
    + deterministic packet event queue
    + causal timing/checkpoint fields
```

`LGRC9V3.step()` now processes one queued packet departure or arrival. On
arrival it also advances the target's local proper-time surface and applies
explicit packetized local-update routes. It can also process scheduled causal
boundary-birth trials and, when explicit LGRC-3 topology-integration gates are
enabled, route causal spark candidates to mechanical expansion, refinement
packet transport, and proper-time inheritance. It does not call synchronous
`GRC9V3.step()` and does not run delayed-evaluation continuity.
Lane A/Lane B spark candidates are causally evaluated at arrival/local-update
boundaries. They remain candidate-only unless active topology integration is
explicitly enabled.
An explicit `apply_causal_boundary_birth_trial(...)` API now supports
default-off LGRC-3 causal frontier boundary birth; scheduled trials are routed
by `step()` and drained by `run_event_queue(...)`.

The current executable tests do not prove full equivalence with synchronous
`GRC9V3.step()`. They prove the narrower LGRC9V3 packet and causal-diagnostic
surface: deterministic queue order, no starvation in bounded interleaved
fixtures, packet budget preservation across many events, the unit-lapse /
constant-delay timing surface, and Lane A/Lane B candidate attribution at
causal diagnostic boundaries. Iteration 31 adds controlled GRC9V3/LGRC9V3
comparison fixtures for timing, delay sensitivity, refinement/topology
integration, and identity persistence. These fixtures align by proper-time
surfaces and event classes, not raw step counts.
Iteration 31-A adds bounded stress coverage for deterministic packet queue
tie-order, repeated packet budget preservation, mixed packet, boundary-birth,
and Lane B expansion processing, causal-clock monotonicity, runtime snapshot
round-trip, and default GRC9V3 isolation.

Post-closeout corrected comparison record:

```text
script:
    examples/lgrc9v3/corrected_cascade_comparison.py

command:
    PYTHONPATH=src ./.venv/bin/python \
        examples/lgrc9v3/corrected_cascade_comparison.py

fixture:
    appendix_e_cell_division_corrected_full_capacity_cascade

baseline session:
    S_LGRC_COMPARE_CORRECTED
```

This script is the tracked reproduction path for the ignored
`outputs/examples/lgrc9v3_corrected_comparison/` artifacts. It regenerates the
corrected 20-step synchronous GRC9V3 baseline when absent, then runs 100 native
LGRC9V3 queue events from the same corrected initial state.

Observed result:

```text
GRC9V3:
    20 synchronous steps
    31 event rows
    final topology = 29 nodes / 28 edges

LGRC9V3:
    100 native queue events
    132 runtime event rows
    final topology = 29 nodes / 28 edges
    max packet budget error ~= 2.84e-14

activity evidence:
    GRC9V3 touched nodes = 18
    LGRC9V3 touched nodes = 30
```

Interpretation:

```text
The corrected cascade reaches the same final topological surface under two
different runtime code paths:

    synchronous GRC9V3.step() replay
    native LGRC9V3 event queue

This supports LGRC9V3 as the most advanced executable RC-family runtime in the
repo, but it is not a claim that one LGRC queue event equals one GRC9V3 step.
```

Generated records:

```text
outputs/examples/lgrc9v3_corrected_comparison/comparison_summary.md
outputs/examples/lgrc9v3_corrected_comparison/comparison_report.json
outputs/examples/lgrc9v3_corrected_comparison/visuals/.../graph_sequence.png
outputs/examples/lgrc9v3_corrected_comparison/visuals/comparison/.../graph_comparison.png
```

## Iteration 33 Baseline Freeze

Iteration 33 freezes the accepted post-32 implementation as the behavioral
baseline for future code-design cleanup.

Frozen runtime assumptions:

```text
LGRC9V3.step():
    processes one deterministic queued event:
        packet departure;
        packet arrival;
        scheduled causal boundary-birth trial.

LGRC9V3.run_event_queue(max_events=...):
    drains both packet event_queue_records and boundary_birth_trial_queue.
    This was aligned with LGRC9V3.step() in Iteration 34.

LGRC9V3 queue execution:
    reuses GRC9V3State as substrate;
    does not call synchronous GRC9V3.step();
    advances LGRC causal clocks and packet state through native LGRC9V3
    queue processing.
```

Frozen event/evidence surfaces:

```text
packet:
    lgrc9v3_packet_departure
    lgrc9v3_packet_arrival
    lgrc9v3_packet_arrival_eligibility

local update:
    lgrc9v3_local_update

spark:
    lgrc9v3_causal_spark_candidate

topology:
    lgrc9v3_causal_boundary_birth
    hybrid_mechanical_expansion
    lgrc9v3_refinement_packet_transport
    lgrc9v3_proper_time_inheritance
    lgrc9v3_causal_collapse
    lgrc9v3_causal_reabsorption

identity:
    lgrc9v3_proper_time_identity_persistence_evaluation
    lgrc9v3_proper_time_identity_acceptance
```

Frozen construction and loading assumptions:

```text
Landscape-backed LGRC9V3 path:
    LandscapeSeed
      -> GRCL9V3 source
      -> GRC9V3State
      -> LGRC9V3.from_state(...)

Native snapshots:
    LGRC9V3.snapshot() exists.
    LGRC9V3.load(...) restores native LGRC9V3 snapshots emitted by
    LGRC9V3.snapshot().
    Plain GRC9V3 snapshots remain GRC9V3 snapshots and are not silently
    loaded as native LGRC9V3.

Stable imports:
    pygrc.models.LGRC9V3
    pygrc.models.lgrc_9_v3 legacy helper/constant imports
```

Baseline verification on 2026-05-07:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime
    31 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_lgrc9v3_contract
    3 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization
    68 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest \
    tests.models.test_grc_9_step \
    tests.models.test_grc_9_runtime \
    tests.models.test_grc_9_v3_step \
    tests.models.test_grc_9_v3_sparks \
    tests.models.test_grc_9_v3_column_h_assisted
    69 tests passed
```

Executable example verification on 2026-05-07:

```text
examples/lgrc9v3/executable_runtime.py
examples/lgrc9v3/executable_packet_queue.py
examples/lgrc9v3/causal_spark_diagnostics.py
examples/lgrc9v3/telemetry_visual_bundle.py
examples/lgrc9v3/causal_history_surfaces.py
examples/lgrc9v3/packetized_causal_flux.py
examples/lgrc9v3/refinement_packet_transport.py
examples/lgrc9v3/active_lgrc3_causal_history.py
```

Corrected cascade reproduction was run again on 2026-05-07 and refreshed
ignored outputs. The accepted high-level result remained:

```text
GRC9V3:
    final topology = 29 nodes / 28 edges

LGRC9V3:
    final topology = 29 nodes / 28 edges
    max packet budget error = 2.842170943040401e-14
```

Known visualization boundary:

```text
LGRC graph sequence and graph comparison artifacts render.
The LGRC final graph HTML path can still report:
    AssertionError: non existent node '0'

This remains a visualization-layer lineage rendering limitation, not a runtime
or telemetry failure.
```

Future code-design work must preserve this baseline unless it opens an
explicit semantic revision.

## Iteration 34 Queue Ownership Patch

Iteration 34 closed the post-33 queue ownership gap.

Behavior now recorded as baseline:

```text
LGRC9V3.run_event_queue(max_events=...):
    processes packet departure events;
    processes packet arrival events;
    processes scheduled causal boundary-birth trials;
    stops only when both model-owned queues are empty or max_events is reached.
```

Regression coverage added:

```text
birth-only boundary trial queue drains through run_event_queue(...);
mixed packet/birth queues drain in step() deterministic order;
run_event_queue(max_events=0) remains a no-op;
empty queues still stop cleanly.
```

Verification on 2026-05-07:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime
    33 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest \
    tests.models.test_grc_9_step \
    tests.models.test_grc_9_runtime \
    tests.models.test_grc_9_v3_step \
    tests.models.test_grc_9_v3_sparks \
    tests.models.test_grc_9_v3_column_h_assisted
    69 tests passed

PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
    GRC9V3 final topology = 29 nodes / 28 edges
    LGRC9V3 final topology = 29 nodes / 28 edges
    max packet budget error = 2.842170943040401e-14
```

## Iteration 35 Module Ownership Split

Iteration 35 split the large LGRC9V3 helper/contract module by ownership while
preserving behavior and legacy import compatibility.

New ownership modules:

```text
src/pygrc/models/lgrc_9_v3_contract.py
src/pygrc/models/lgrc_9_v3_timing.py
src/pygrc/models/lgrc_9_v3_packets.py
src/pygrc/models/lgrc_9_v3_topology.py
src/pygrc/models/lgrc_9_v3_identity.py
```

Compatibility surface:

```text
src/pygrc/models/lgrc_9_v3.py
    remains the legacy re-export facade;
    preserves old `pygrc.models.lgrc_9_v3` imports;
    re-exports `LGRC9V3` from `lgrc_9_v3_runtime.py`.
```

Dependency rule now recorded as baseline:

```text
contract imports no split modules;
timing/packets/topology/identity may import contract;
runtime imports split modules directly;
split modules do not import runtime.
```

No runtime semantics were changed in this iteration.

Verification on 2026-05-07:

```text
PYTHONPATH=src ./.venv/bin/python -m py_compile \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_packets.py \
    src/pygrc/models/lgrc_9_v3_topology.py \
    src/pygrc/models/lgrc_9_v3_identity.py \
    src/pygrc/models/lgrc_9_v3_timing.py \
    src/pygrc/models/lgrc_9_v3.py \
    src/pygrc/models/lgrc_9_v3_runtime.py

PYTHONPATH=src ./.venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_module_split \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_runtime
    118 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest discover tests -p 'test_lgrc*.py'
    118 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest \
    tests.telemetry.test_lgrc9v3_contract \
    tests.visualization.test_visualization
    71 tests passed

PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
    GRC9V3 final topology = 29 nodes / 28 edges
    LGRC9V3 final topology = 29 nodes / 28 edges
    max packet budget error = 2.842170943040401e-14
```

## Iteration 36 Runtime Construction And Landscape Facades

Iteration 36 moved source-to-runtime wiring and accepted queue-priming policy
out of examples and into tested library-owned facades.

New construction module:

```text
src/pygrc/models/lgrc_9_v3_construction.py
```

Library-owned construction surfaces:

```text
prepare_lgrc9v3_landscape_runtime(...)
build_lgrc9v3_from_landscape_seed(...)
LGRC9V3.from_landscape_seed(...)
```

The preserved lowering sequence is:

```text
LandscapeSeed
  -> GRCL9V3 source
  -> GRC9V3State
  -> LGRC9V3RuntimeState
```

Library-owned queue-priming surfaces:

```text
lgrc9v3_graph_routes_for_current_topology(...)
prime_lgrc9v3_packet_departures(...)
prime_lgrc9v3_broad_seed_packets(...)
```

Corrected-cascade scenario policy:

```text
LGRC9V3CorrectedCascadeScenarioPolicy
build_lgrc9v3_corrected_cascade_runtime(...)
prime_lgrc9v3_corrected_cascade_queues(...)
prime_lgrc9v3_corrected_cascade_broad_seed(...)
```

Updated examples:

```text
examples/lgrc9v3/landscape_seed_runtime.py
examples/lgrc9v3/corrected_cascade_comparison.py
```

The corrected comparison no longer owns the causal mode dictionary, initial
packet priming, causal boundary-birth trial priming, topology route generation,
or broad seed packet scheduling. It consumes the new construction helpers.

Verification on 2026-05-07:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_module_split \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_runtime
    122 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest discover tests -p 'test_lgrc*.py'
    122 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest \
    tests.telemetry.test_lgrc9v3_contract \
    tests.visualization.test_visualization
    71 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest \
    tests.models.test_grc_9_step \
    tests.models.test_grc_9_runtime \
    tests.models.test_grc_9_v3_step \
    tests.models.test_grc_9_v3_sparks \
    tests.models.test_grc_9_v3_column_h_assisted
    69 tests passed

PYTHONPATH=src ./.venv/bin/python examples/landscapes/run_seed_grc9v3.py
    existing GRC9V3 landscape example passed

PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/landscape_seed_runtime.py
    new landscape-backed LGRC9V3 example passed

PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
    GRC9V3 final topology = 29 nodes / 28 edges
    LGRC9V3 final topology = 29 nodes / 28 edges
    max packet budget error = 2.842170943040401e-14
```

## Iteration 37 Native Runtime Snapshot Restore Parity

Iteration 37 implemented native `LGRC9V3.load(...)` for snapshots emitted by
`LGRC9V3.snapshot()`.

The native restore path now:

```text
requires metadata.model_family == "LGRC9V3";
restores caches.base_grc9v3_snapshot into the base GRC9V3State;
restores dynamics.lgrc9v3_runtime into LGRC9V3RuntimeState;
restores causal modes, packet ledger, event queue, boundary-birth trial queue,
    causal flux routes, proper-time maps, last-update event-time maps,
    packet-processing logs, local-update logs, causal-spark logs, and topology
    logs;
checks observables against compute_observables();
rejects partial native snapshots clearly;
rejects plain GRC9V3 snapshots.
```

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    125 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    920 tests passed

.venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_runtime_state.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/grc_9_v3.py \
    tests/models/test_lgrc_9_v3_runtime.py
    passed
```

## Post-37 Next Surface: Autonomous Event Production

After Iteration 37, `LGRC9V3.step()` is the accepted deterministic executor.
The next design tension is event production, not event consumption.

Boundary for future work:

```text
LGRC9V3.step()
    consumes one queued causal work item

producer helpers / produce_events(...)
    inspect state and schedule eligible work

run_autonomous(...)
    bounded producer + step() loop
```

Autonomy v1 should stay narrow:

```text
packet departures from explicit flux/route policy;
boundary-birth trial scheduling when enabled;
causal spark diagnostics remain tied to arrivals/local updates;
collapse/reabsorption and identity acceptance remain explicit or separately
    gated;
all generated work records producer policy, reason code, thresholds, and
    observed evidence.
```

## Iteration 38 Autonomous Event Production Contract

Iteration 38 added the autonomy contract without turning on active producer
behavior.

Implemented now:

```text
LGRC9V3.produce_events(policy="disabled")
    returns auditable no-op producer result;
    schedules no work;
    consumes no queued work;
    mutates no topology;
    is idempotent on the same causal surface.
```

New artifact surfaces:

```text
lgrc9v3_autonomous_event_production_result
LGRC9V3AutonomousProductionRecord
LGRC9V3AutonomousProductionResult
```

Queue ownership rule:

```text
producer:
    may schedule work in future iterations

step():
    remains the only default queue consumer
```

Implemented after Iteration 38:

```text
packet_departure_from_flux_route_policy
```

Still planned:

```text
run_autonomous(...)
```

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    129 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    924 tests passed
```

## Iteration 39 Packet Departure Producer

Iteration 39 added the first active autonomous producer:

```text
LGRC9V3.produce_events(
    policy="packet_departure_from_flux_route_policy"
)
```

Implemented behavior:

```text
inspect causal_flux_routes
validate source node, target node, edge, and edge causal delay
resolve fixed amount or source-coherence amount_fraction
reject source overdraw before queueing
schedule packet departure events
emit producer evidence for each scheduled packet
enforce route-surface idempotency
leave packet processing to step()
```

The producer records `packet_departure_scheduled` for scheduled departures and
`idempotent_causal_surface_already_produced` for repeated calls on the same
causal route surface. It does not debit coherence, process arrivals, mutate
topology, emit collapse/reabsorption, or accept identity. Those remain owned by
the existing queue consumer and policy-gated topology/identity surfaces.

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    9 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_construction -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    929 tests passed
```

## Iteration 40 Boundary-Birth Trial Producer

Iteration 40 added the second active autonomous producer:

```text
LGRC9V3.produce_events(
    policy="boundary_birth_trial_policy"
)
```

Implemented behavior:

```text
inspect live nodes for inactive boundary ports
compute outward_flux_pressure through the accepted GRC9V3-compatible surface
compute birth_probability = 1 - exp(-lambda_birth * outward_flux_pressure)
schedule causal boundary-birth trial records
record explicit rng_sample values in queued trials
emit producer evidence for each scheduled trial
enforce causal-surface idempotency
leave acceptance/rejection and topology mutation to step()
```

The producer records `boundary_birth_trial_scheduled` for scheduled trials and
`idempotent_causal_surface_already_produced` for repeated calls on the same
causal surface. Disabled boundary-birth policy, zero `lambda_birth`, no open
ports, or zero outward pressure emit `no_eligible_work`.

This does not change the boundary-birth probability law. The scheduled trial
routes through the existing `step()` path, which still performs acceptance or
rejection and is the only path that mutates topology.

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    13 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_construction -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    138 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    933 tests passed
```

## Iteration 41 Bounded Autonomous Run Loop

Iteration 41 added a bounded producer-plus-executor loop:

```text
LGRC9V3.run_autonomous(
    max_events=...,
    policy="bounded_lgrc9v3_v1",
    producer_policies=(...)
)
```

Implemented behavior:

```text
run active producers only when model-owned queues are empty
consume scheduled work only through LGRC9V3.step()
respect max_events
stop when no producer can schedule work and queues remain empty
record producer and consumer counts
preserve manual step() and run_event_queue(...) behavior
```

The run summary is stored in:

```text
StepResult.bookkeeping["autonomous_run"]
state.cached_quantities["last_lgrc9v3_autonomous_run"]
```

It records producer invocations, scheduled event count, idempotent skips,
no-eligible-work count, consumed step/event count, stop condition, queue status,
and serialized production results.

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    18 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_construction -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    143 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    938 tests passed
```

## Iteration 42 Autonomy Examples And Handoff

Iteration 42 added runnable autonomy examples and closed the Phase 8 autonomy
handoff.

New examples:

```text
examples/lgrc9v3/autonomous_produce_then_step.py
examples/lgrc9v3/autonomous_run.py
```

Accepted autonomy v1 claim:

```text
LGRC9V3 can now run a bounded autonomous producer/executor loop.
Producers enqueue packet departures or boundary-birth trials.
LGRC9V3.step() remains the only default queue consumer.
run_autonomous(...) is a bounded loop over those two responsibilities.
```

Non-claims:

```text
run_autonomous(...) is not a general LGRC abstraction;
it is not synchronous GRC9V3.step();
it does not auto-discover every possible causal mechanism;
collapse/reabsorption and identity acceptance remain explicit or separately gated.
```

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/autonomous_produce_then_step.py
    passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/autonomous_run.py
    passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/executable_runtime.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/executable_packet_queue.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/causal_spark_diagnostics.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/landscape_seed_runtime.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/causal_history_surfaces.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/packetized_causal_flux.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/refinement_packet_transport.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/active_lgrc3_causal_history.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/telemetry_visual_bundle.py
    passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
    passed
    GRC final nodes/edges: 29 / 28
    LGRC final nodes/edges: 29 / 28
    max_abs_packet_budget_error: 2.842170943040401e-14

PYTHONPATH=src .venv/bin/python examples/landscapes/run_seed_grc9v3.py
    passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    18 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_construction -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    143 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    938 tests passed

PYTHONPATH=src .venv/bin/python -m ruff check ...
    passed

git diff --check
    passed
```

## Completed Scope

Implemented surfaces:

- `LGRC-0` derived causal-history annotation over `GRC9V3State`;
- `LGRC-1` fixed-topology semi-causal eligibility;
- `LGRC-2` fixed-topology packet contract, passive ledger, and
  departure/arrival processing;
- `LGRC-2` compact pending-flux ledger derivation over in-flight packet
  records;
- `LGRC-3` topology contract artifact for refinement lineage, packet
  transport, and proper-time inheritance field requirements;
- `LGRC-3` refinement packet transport through one GRC9V3 mechanical
  expansion, preserving packet ids, packet amounts, endpoint lineage, queued
  arrival targets, pending-flux entry links, and budget evidence;
- `LGRC-3` default-disabled collapse/identity policy contract with
  collapse/reabsorption payload fields, budget/lineage transfer fields,
  sink-local identity clock policy, and local-delay threshold calibration;
- `LGRC-3` proper-time inheritance processing after GRC9V3 mechanical
  expansion, using uniform parent proper-time inheritance;
- `LGRC-3` active collapse/reabsorption evidence with explicit sink selection,
  explicit lineage transfer maps, proper-time transfer policy, and budget
  continuity;
- `LGRC-3` packet and pending-flux transport through collapse/reabsorption,
  redirecting endpoints to the selected sink or settling selected-sink
  self-loop packets;
- `LGRC-3` sink-local proper-time identity persistence evaluation;
- `LGRC-3` explicit identity-acceptance event emission after a passing
  evaluator and opt-in policy enablement;
- `LGRC-3` replay validation for event-time order, source topology references,
  identity-evaluation references, lineage continuity, and budget continuity;
- executable `LGRC9V3` event-queue shell for deterministic packet
  departure/arrival processing and arrival-eligibility evidence;
- packetized local-update route scheduling after packet arrival, with
  delayed-evaluation continuity disabled;
- causally scheduled Lane A/Lane B spark candidate diagnostics after
  arrival/local-update boundaries, emitted as
  `lgrc9v3_causal_spark_candidate`;
- opt-in causal frontier boundary birth through
  `apply_causal_boundary_birth_trial(...)`, emitted as
  `lgrc9v3_causal_boundary_birth`, using the GRC9V3 outward-flux probability
  law, parent-debit coherence transfer, parent proper-time inheritance, and
  explicit/`tau_0` edge-delay assignment;
- scheduled boundary-birth trial routing through `LGRC9V3.step()`;
- opt-in active topology integration from causal spark candidates to
  mechanical expansion, refinement packet transport, and proper-time
  inheritance;
- runtime wrappers for policy-gated collapse/reabsorption and identity
  acceptance evidence;
- LGRC9V3 telemetry family extensions for packet, local-update, spark,
  topology, collapse, and identity event rows;
- LGRC9V3 graph checkpoint overlays for causal clocks, node proper-time
  surfaces, edge causal delays, packet ledger state, local-update logs,
  causal spark diagnostics, topology history, and runtime-state artifacts;
- LGRC9V3 visualization surfaces for event-time/proper-time observables,
  packet in-flight overlays, topology lineage overlays, proper-time identity
  windows, and LGRC Lane A/Lane B spark attribution;
- controlled GRC9V3/LGRC9V3 comparison fixtures for synchronous-limit timing,
  delay-sensitive packet routing, Lane B refinement/topology integration, and
  proper-time identity persistence, with explicit supported/open claims;
- bounded runtime stress tests for packet queue tie-order, repeated packet
  budget preservation, mixed packet/boundary-birth/Lane B expansion,
  causal-clock monotonicity, runtime snapshot round-trip, and default GRC9V3
  isolation;
- executable LGRC9V3 examples for construction/step processing, routed packet
  queues, causal Lane B spark diagnostics, and telemetry/graph visualization;
- behavior-preserving LGRC9V3 module split into contract, timing, packet,
  topology, and identity ownership modules with a legacy compatibility facade;
- library-owned LGRC9V3 landscape construction and queue-priming facades for
  seed-backed runtime creation, topology route generation, broad seed packets,
  and corrected-cascade reproduction policy;
- timing vocabulary for `kappa`, `k`, `T_e`, `tau_i`, and `tau_ij`;
- derived geometric, causal/proper-time, and functional distance surfaces;
- causal cone and causal basin-core overlays as derived evidence;
- core causal-history artifact attach/extract/restore helpers;
- no-regression tests showing default `GRC9V3` does not claim the causal
  layer and Lane A/Lane B spark evidence remains unchanged when LGRC helpers
  are external;
- executable `LGRC9V3` unit-lapse / constant-delay packet timing-surface tests,
  bounded interleaved queue-drain tests, and many-event packet budget audits.

Primary files:

- [src/pygrc/models/lgrc_9_v3.py](../src/pygrc/models/lgrc_9_v3.py)
- [src/pygrc/models/lgrc_9_v3_runtime.py](../src/pygrc/models/lgrc_9_v3_runtime.py)
- [src/pygrc/models/lgrc_9_v3_runtime_state.py](../src/pygrc/models/lgrc_9_v3_runtime_state.py)
- [src/pygrc/telemetry/lgrc9v3_contract.py](../src/pygrc/telemetry/lgrc9v3_contract.py)
- [src/pygrc/visualization/render.py](../src/pygrc/visualization/render.py)
- [src/pygrc/visualization/graph_render.py](../src/pygrc/visualization/graph_render.py)
- [tests/models/test_lgrc_9_v3_contract.py](../tests/models/test_lgrc_9_v3_contract.py)
- [tests/models/test_lgrc_9_v3_runtime.py](../tests/models/test_lgrc_9_v3_runtime.py)
- [tests/telemetry/test_lgrc9v3_contract.py](../tests/telemetry/test_lgrc9v3_contract.py)
- [tests/visualization/test_visualization.py](../tests/visualization/test_visualization.py)
- [specs/lgrc-9-v3-spec.md](../specs/lgrc-9-v3-spec.md)
- [docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md](../docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md)
- [examples/lgrc9v3/executable_runtime.py](../examples/lgrc9v3/executable_runtime.py)
- [examples/lgrc9v3/executable_packet_queue.py](../examples/lgrc9v3/executable_packet_queue.py)
- [examples/lgrc9v3/causal_spark_diagnostics.py](../examples/lgrc9v3/causal_spark_diagnostics.py)
- [examples/lgrc9v3/telemetry_visual_bundle.py](../examples/lgrc9v3/telemetry_visual_bundle.py)
- [examples/lgrc9v3/corrected_cascade_comparison.py](../examples/lgrc9v3/corrected_cascade_comparison.py)
- [examples/lgrc9v3/causal_history_surfaces.py](../examples/lgrc9v3/causal_history_surfaces.py)
- [examples/lgrc9v3/packetized_causal_flux.py](../examples/lgrc9v3/packetized_causal_flux.py)
- [examples/lgrc9v3/refinement_packet_transport.py](../examples/lgrc9v3/refinement_packet_transport.py)
- [examples/lgrc9v3/active_lgrc3_causal_history.py](../examples/lgrc9v3/active_lgrc3_causal_history.py)

## Safe Claims

A current `LGRC9V3` run may claim:

```text
LGRC-0 causal-history annotation can be computed over synchronous GRC9V3 state.
LGRC-1 fixed-topology proper-time eligibility can be computed as semi-causal
evidence.
Fixed-topology LGRC-2 packet departures/arrivals preserve
sum_i C_i + sum_p C_p with explicit budget evidence.
Scheduled packets can be queued before departure and then processed into
in-flight packets.
LGRC9V3.step() processes one deterministic queued packet departure or arrival
and emits packet-processing event evidence.
Packet arrivals can feed `lgrc9v3_local_update` evidence, advance local proper
time under the serialized lapse/proper-time policy, and schedule explicit
outbound packet routes.
Arrival/local-update boundaries can evaluate the existing GRC9V3 Lane A/Lane B
spark predicates and emit `lgrc9v3_causal_spark_candidate` events with
event-time, proper-time, trigger, topology-signature, and branch-attribution
evidence.
Packet arrival event-time keys can be derived from captured edge-delay
surfaces as `T_arrive = T_depart + tau_ij`, while remaining distinct from
source/target node proper time.
Compact pending-flux ledger artifacts can be derived from in-flight packet
records without replacing the canonical per-packet ledger.
LGRC-3 topology-contract evidence can name refinement lineage and packet
transport fields without claiming topology-changing processing.
LGRC-3 refinement packet transport can map in-flight packet endpoint and
lineage evidence through one GRC9V3 mechanical expansion using the expansion
reassignment map.
Refinement packet transport preserves packet ids, packet amounts, queued
arrival linkage, compact pending-flux links, and
sum_i C_i + sum_p C_p budget evidence.
The LGRC-3 collapse/identity policy contract defines future
collapse/reabsorption and proper-time identity payload fields while keeping
both mechanisms disabled by default.
Active LGRC-3 collapse/reabsorption evidence can be emitted when the caller
explicitly enables the processor and supplies sink, lineage, proper-time, and
budget evidence.
Active LGRC-3 packet transport can redirect or settle in-flight packet evidence
through collapse/reabsorption while preserving packet ids and the packet budget
invariant.
Active LGRC-3 proper-time identity persistence can be evaluated over a
sink-local proper-time window using a local-delay threshold calibration.
Active LGRC-3 identity acceptance can be emitted only after a passing evaluator
and explicit identity-acceptance policy enablement.
LGRC-3 replay validation can audit the current topology-changing evidence chain
for event-time order, lineage references, and budget continuity.
LGRC9V3 telemetry can classify active runtime events by causal domain and
serialize graph checkpoints with causal-clock, packet-ledger, spark-diagnostic,
and topology-history overlays.
LGRC9V3 visual bundles can render those telemetry/checkpoint overlays as
causal event-time/proper-time series, packet in-flight state, topology lineage,
proper-time identity windows, and LGRC Lane A/Lane B spark labels.
Controlled GRC9V3/LGRC9V3 comparison fixtures can show where the executable
LGRC9V3 runtime matches a synchronous-limit timing/topology surface and where
causal delay, packet transport, or proper-time identity evidence creates a
bounded fixture-local delta.
Bounded stress fixtures can show deterministic queue ordering, stable packet
budget accounting, mixed event processing, causal-clock monotonicity, snapshot
round-trip, and default GRC9V3 isolation in selected small fixtures.
Packet arrivals can emit eligibility evidence for later local update or
spark-diagnostic evaluation without emitting a spark.
The synchronous GRC9V3 runtime remains unchanged when LGRC modes are disabled.
```

A current `LGRC9V3` run must not claim:

```text
Full event-driven LGRC propagation beyond packet departure/arrival and explicit
packetized local-update routing is implemented.
LGRC9V3.step() runs synchronous GRC9V3.step().
Spark candidates automatically trigger mechanical expansion.
Delayed-evaluation continuity updates are applied from arrival eligibility.
Full topology-changing causal-history step-loop processing is implemented.
Mechanical expansion is proper-time identity acceptance.
Collapse/reabsorption or identity acceptance is enabled by default.
Proper-time identity evaluation alone is identity acceptance.
General LGRC, executable LGRC9, or executable LGRCV3 exists.
Visual packet/topology/identity overlays are proof of recorded LGRC9V3 evidence,
not proof of general landscape validity.
Iteration 31 comparison fixtures are full GRC9V3/LGRC9V3 equivalence proofs or
landscape-general parity evidence.
Iteration 31-A stress fixtures are landscape-general robustness evidence or a
proof of exhaustive scheduler fairness.
```

## Verification

Focused verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.models.test_lgrc_9_v3_contract \
  tests.models.test_lgrc_9_v3_runtime \
  tests.telemetry.test_lgrc9v3_contract
```

Executable example verification:

```bash
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/executable_runtime.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/executable_packet_queue.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/causal_spark_diagnostics.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/telemetry_visual_bundle.py
```

Visualization verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization
```

Regression verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract tests.models.test_grc_9_state tests.models.test_grc_9_step tests.models.test_grc_9_runtime tests.models.test_grc_9_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_column_h_assisted tests.models.test_grc_9_v3_hessian_readiness tests.core.test_module_imports tests.core.test_serialization_contract
```

Example verification:

```bash
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/causal_history_surfaces.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/packetized_causal_flux.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/refinement_packet_transport.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/active_lgrc3_causal_history.py
```

## Phase 8 Continuation Scope

The pending-flux ledger compaction gate is closed. The LGRC-2 packet/event
queue contract, passive packet ledger surface, fixed-topology
departure/arrival processing, scheduled departure processing, arrival
eligibility evidence, and compact pending-flux representation now exist.

The `LGRC-3` decision record, topology-changing causal-history contract,
refinement packet transport helper, collapse/identity policy contract, active
proper-time inheritance processor, active collapse/reabsorption processor,
collapse packet-transport processor, proper-time identity evaluator, identity
acceptance emitter, replay validator, and active example are now defined. The
next planned implementation step is Iteration 24, the `LGRC9V3` runtime class
decision, unless the project explicitly keeps the helper/evidence architecture
for longer.

The LGRC-2 contract defines:

- event queue keys and deterministic ordering;
- packet departure and arrival events;
- scheduled packet departure processing;
- delay-derived packet arrival event-time keys, with explicit arrival keys
  reserved for replay/fixture construction;
- in-flight coherence budget invariant:

```text
B = sum_i C_i + sum_p C_p
```

- canonical per-packet ledger representation;
- compact pending-flux ledger representation derived from in-flight packets;
- replay and artifact schema for packet lifecycle;
- the relation between packet arrival, local update eligibility, and spark
  diagnostics, via explicit eligibility evidence;
- tests proving packetized conservation across fixed-topology departure/arrival
  processing before any topology-changing LGRC-3 behavior is introduced.

LGRC-2 should not silently redefine the completed `LGRC-0`/`LGRC-1` surfaces.

The compaction decision is:

```text
canonical LGRC-2 packet ledger:
    remains per-packet

compact pending-flux ledger:
    derived budget-equivalent artifact over in-flight packets
```

Compact entries aggregate only by exact directed channel, arrival key, and
source/target lineage. They preserve packet ids, departure keys, amounts, and
lineage fields for refinement-transport audit. They do not themselves
transport packets through topology changes;
`transport_lgrc9v3_packets_through_refinement(...)` consumes them as optional
supporting evidence.

The LGRC-3 contract and active helper slice now define:

- topology-changing causal-history event kinds;
- refinement lineage maps for causal history;
- packet transport through mechanical expansion;
- proper-time inheritance across new nodes and internal edges;
- active collapse/reabsorption processing behind explicit policy enablement;
- active sink-local proper-time identity persistence evaluation;
- active identity-acceptance event emission behind explicit policy enablement;
- budget and lineage audits after topology-changing events.

LGRC-3 implementation should not start by changing the completed LGRC-2 budget
or compaction semantics. It should consume the preserved packet and
compact-entry lineage named by the topology contract.

Iteration 14 implements that first consumption path for refinement only:

```text
pre-expansion packet ledger
+ GRC9V3 hybrid_mechanical_expansion event
+ post-expansion topology signature
+ optional compact pending-flux ledger
-> lgrc9v3_refinement_packet_transport_result
```

The transport result is not identity evidence. It records:

```text
identity_acceptance_emitted = false
packet_transport_identity_transfer = false
```

Iteration 15 defines the future policy surface for collapse/reabsorption and
proper-time identity:

```text
artifact_kind = "lgrc9v3_collapse_identity_policy_contract"
artifact_schema_version = "lgrc9v3_collapse_identity_policy_contract_v1"
contract_only = true
collapse_reabsorption_allowed = false
identity_acceptance_allowed = false
```

The selected first-round identity clock is:

```text
identity_clock_policy = "sink_local_proper_time"
threshold_calibration_policy = "local_median_delay_multiplier"
threshold_multiplier = 4.0
```

## Completed Active LGRC-3 Helper/Evidence Iterations

The current Phase 8 code defines contracts plus active LGRC-3 helper/evidence
processors. The completed active LGRC-3 iterations are:

- Iteration 17: proper-time inheritance processor for
  `lgrc9v3_proper_time_inheritance`;
- Iteration 18: collapse/reabsorption processor for
  `lgrc9v3_causal_collapse` and `lgrc9v3_causal_reabsorption`;
- Iteration 19: packet and pending-flux transport through
  collapse/reabsorption;
- Iteration 20: sink-local proper-time identity persistence evaluator;
- Iteration 21: identity acceptance event emitter for
  `lgrc9v3_proper_time_identity_acceptance`;
- Iteration 22: LGRC-3 topology event replay validator for budget, lineage,
  and event-time ordering;
- Iteration 23: active LGRC-3 examples and handoff.

These are not long-range general-family abstractions. They are the direct
helper/evidence continuation of the LGRC-3 contracts. They still do not create
a concrete `LGRC9V3` model class.

Iteration 20's identity evaluator consumes topology, lineage, and basin-core
evidence as string ids rather than full event objects. That is intentional for
the helper-only architecture: future replay/runtime adapters may resolve richer
objects into those ids without changing the narrow evaluator contract.

## Completed Executable LGRC9V3 Runtime Parity Iterations

Iterations 17-23 completed the active LGRC-3 causal-history helper/evidence
layer. They did not, by themselves, make LGRC9V3 an executable runtime on par
with synchronous `GRC9V3`. The accepted parity path is:

- Iteration 24: LGRC9V3 runtime class decision;
- Iteration 25: event queue orchestration loop (complete);
- Iteration 26: causal flux and local update loop (complete);
- Iteration 27: causally scheduled Lane A/Lane B spark diagnostics (complete);
- Iteration 28-A: causal frontier boundary birth, default-off/overridable and
  probability-compatible with GRC9V3 boundary birth when enabled (complete);
- Iteration 28: active topology integration (complete);
- Iteration 29: LGRC9V3 telemetry and checkpoint parity (complete);
- Iteration 30: LGRC9V3 visualization parity (complete);
- Iteration 31: GRC9V3 vs LGRC9V3 comparison fixtures (complete);
- Iteration 31-A: runtime stress and determinism sweep (complete);
- Iteration 32: executable LGRC9V3 examples and handoff (complete).

Iteration 32 is the closeout gate for the executable runtime-parity arc. It
introduced no new runtime semantics. It added runnable examples, reference-guide
imports, and this handoff closeout for what `LGRC9V3.step()` and equivalent
runtime surfaces support after Iterations 24-31-A, and which claims remain
unsupported.

Iteration 24 accepts a concrete executable `LGRC9V3` model class as the target
for Iterations 25+. The class is not implemented in Iteration 24.

Runtime-class decision:

```text
LGRC9V3 should implement/share the GRCModel interface.
LGRC9V3 should use composition over GRC9V3State, not subclass GRC9V3.
LGRC9V3 runtime state should own packet ledger, event queue, topology-event
ledger, causal clocks, policies, and diagnostic history.
Current helper/evidence APIs remain valid and are not reinterpreted as
model-owned state.
```

Planned files:

```text
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
tests/models/test_lgrc_9_v3_runtime.py
```

Old `GRC9V3` snapshots remain `GRC9V3` snapshots. Loading them into executable
`LGRC9V3` must use an explicit adapter or synchronous-limit policy.

Iteration 27 closes the first spark parity gap. LGRC9V3 may now claim
causally scheduled Lane A/Lane B candidate diagnostics at arrival/local-update
boundaries. It still may not claim that those candidates automatically run
mechanical expansion or topology integration; those are Iteration 28 surfaces.

## Post-Closeout Continuation Addendum

Later Phase 8 LGRC9 continuations extend the executable `LGRC9V3` runtime with
default-off support surfaces used by N03/N04. These closeouts supersede this
handoff as the current Phase 8 continuation index:

- [`Phase-8-LGRC9-NativePacketLoopChecklist.md`](./Phase-8-LGRC9-NativePacketLoopChecklist.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md)
- [`Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`](./Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md)
- [`Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md`](./Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md)
- [`Phase-8-LGRC9-NativeRouteArbitrationCloseout.md`](./Phase-8-LGRC9-NativeRouteArbitrationCloseout.md)
- [`Phase-8-LGRC9-MultiBasinFormationPlan.md`](./Phase-8-LGRC9-MultiBasinFormationPlan.md)
- [`Phase-8-LGRC9-MultiBasinFormationChecklist.md`](./Phase-8-LGRC9-MultiBasinFormationChecklist.md)
- [`Phase-8-LGRC9-MultiBasinFormationCloseout.md`](./Phase-8-LGRC9-MultiBasinFormationCloseout.md)
- [`Phase-8-LGRC9-RestorationIdentityPlan.md`](./Phase-8-LGRC9-RestorationIdentityPlan.md)
- [`Phase-8-LGRC9-RestorationIdentityChecklist.md`](./Phase-8-LGRC9-RestorationIdentityChecklist.md)
- [`Phase-8-LGRC9-RestorationIdentityCloseout.md`](./Phase-8-LGRC9-RestorationIdentityCloseout.md)
- [`Phase-8-LGRC9-RestorationIdentityCloseout.json`](./Phase-8-LGRC9-RestorationIdentityCloseout.json)

Current N04 return target after the route-arbitration closeout:

```text
N04 Iteration 21-B: native LGRC route-arbitration rerun
```

These continuations remain runtime-support closeouts. They do not promote
semantic choice, agency, RC identity collapse, identity acceptance,
locomotion-like behavior, biological behavior, unrestricted movement, or
claim-promotion flags.

The restoration-identity continuation is closed as a bounded additive contract
for explicit RCAE P2-I2 adoption. It provides:

```text
LGRC9V3-owned read-only embedded-GRC9V3 state projection
+ exact LGRC9V3 runtime artifact
+ events and observables
-> lgrc9v3_restoration_identity_v1
```

It preserves raw snapshot digests as observations and leaves snapshot schema,
load behavior, runtime dynamics, and the GRC9V3 substrate unchanged.
RCAE-owned medium or pool state remains outside the native PyGRC identity and
must be composed separately by the consuming project.

The supported scope is LGRC9V3 `pygrc.snapshot` version 1 model/snapshot
inputs, including older supported representations that omit deterministic
empty LGRC runtime logs. The identity reaches a fixed point across repeated
native load even when the raw representation cycles. Bounded equal-input
continuation passed for the retained RCAE fixture and a local queued-arrival
twin; unrestricted continuation equivalence remains blocked.

P2-I1 remains unchanged. P2-I2 may replace its RCAE C02 projection only by
declaring a realization-profile transition to
`pygrc.models.lgrc9v3_restoration_identity_v1`. Silent upgrade is forbidden.
The C02 projection remains an explicit non-native fallback for older graph
revisions or environments without the helper.

The N25.1-driven multi-basin formation implementation tranche is closed at
Iteration 89. Iteration 83 freezes the baseline in:

```text
Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.md
Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.json
```

The closeout supports an MB5 control-backed native multi-basin formation
candidate through default-off runtime surfaces, replay validation,
merge/leakage controls, telemetry, visual examples, and a front-capacity-gated
boundary-birth companion. It does not by itself support MB6, N26-ready
unscoped multi-basin substrate evidence, BF6, independent new-basin formation
as a general native capacity, native support, agency, semantic learning,
semantic choice, sentience, ant ecology, or Phase 8 completion.

The scoped N25.2 validation bridge is now closed. N25.2 consumes N25 BF5,
N25.1 requirements, Phase 8 MB5/I88-A evidence, replay/control/stress evidence,
and the MB6 gate matrix, then closes at:

```text
final_mb_ladder_rung = MB6_N26_ready_multi_basin_substrate_evidence
final_n25_2_closeout_rung = N25.2-C6_closeout_and_N26_handoff_complete
n26_consumption_effect = scoped_mb6_substrate_consumption_allowed
n26_unscoped_multi_basin_consumption_allowed = false
```

The current experiment handoff is therefore N26, with scoped multi-basin
substrate evidence allowed and unscoped multi-basin, native support, agency,
sentience, ant ecology, and Phase 8 completion claims still blocked.
