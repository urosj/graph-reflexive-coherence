# LGRC9V3 Causal-History Reference Guide

This guide describes the current LGRC-9 implementation slice in PyGRC.

The implemented target is `LGRC9V3`: causal-history evidence and a narrow
executable causal event queue over the existing `GRC9V3` state substrate.
There is not a general LGRC runtime.

The active runtime shape is composed:

```text
LGRC9V3RuntimeState =
    GRC9V3State
    + LGRC9V3PacketLedger
    + deterministic packet event queue
    + scheduled boundary-birth trial queue
    + local-update, causal-spark, topology, and replay ledgers
    + causal timing/checkpoint fields
```

`LGRC9V3.step()` currently means:

```text
process one queued packet departure/arrival or scheduled causal boundary-birth
trial;
on arrival, advance the target local clock and run the explicit packetized
local-update route surface;
after the local-update boundary, evaluate causally scheduled Lane A/Lane B
spark diagnostics and emit candidate evidence when the predicate fires.
```

Autonomous execution is layered above `step()`:

```text
produce_events(...)
    schedules eligible packet departures or boundary-birth trials;
    does not consume queued work.

run_autonomous(...)
    bounded loop:
        produce when queues are empty;
        consume through LGRC9V3.step().
```

Use this guide when you want to:

- compute LGRC-0 causal-history annotations over `GRC9V3State`;
- compute LGRC-1 fixed-topology semi-causal eligibility evidence;
- process LGRC-2 fixed-topology packet departures and arrivals;
- derive LGRC-2 compact pending-flux ledgers from in-flight packets;
- transport LGRC-2 packet evidence through one GRC9V3 refinement event;
- serialize or restore LGRC causal-history artifact blocks;
- understand which active LGRC-3 and executable LGRC9V3 runtime surfaces are
  implemented and which claims remain out of scope.

## Synchronous GRC And LGRC Execution Roles

Synchronous GRC-family runtimes and native LGRC execution serve different
purposes.

Use `GRC9V3` / `GRCV3` when the question is:

```text
What structure does the coherence field relax into?
```

Typical synchronous-GRC surfaces include basin formation, coherence
redistribution, structural attractors, spark-candidate diagnostics, topology
growth/pruning decisions, and collapse/reabsorption decisions.

Use `LGRC9V3` when the question is:

```text
What causal packet history can propagate through that structure?
```

Typical LGRC surfaces include packet departure/arrival, in-flight packet
coherence, local event ordering, proper-time/event-time evidence, and
self-rearming packetized pulse transport.

The recommended pipeline is:

```text
GRC builds or diagnoses substrate structure.
LGRC runs causal packet transport through that substrate.
Movement experiments test whether packet pulses couple to boundaries.
```

The N03 packet-loop result follows this split: native fixed-topology `GRC9V3`
proposal flux did not produce polarized loops on the tested fixtures, while
native `LGRC9V3` packetized causal execution reproduced the self-rearming
packet loop under controls.

## Current Status

Implemented:

| Level | Meaning | Current Surface |
|---|---|---|
| LGRC-0 | Derived annotation over synchronous `GRC9V3` evidence. | `annotate_lgrc9v3_causal_history(...)` |
| LGRC-1 | Opt-in fixed-topology semi-causal eligibility. | `compute_lgrc9v3_fixed_topology_eligibility(...)` |
| LGRC-2 contract | Packetized fixed-topology causal-flux schema. | `build_lgrc9v3_packet_contract_artifact(...)` |
| LGRC-2 ledger | Passive packet and ledger artifacts. | `build_lgrc9v3_packet_ledger(...)` |
| LGRC-2 processing | Fixed-topology departure/arrival transitions. | `process_lgrc9v3_packet_departure(...)`, `process_lgrc9v3_packet_arrival(...)` |
| LGRC9V3 runtime | Executable queue processing, packetized local-update route scheduling, boundary-birth trial routing, and opt-in topology integration. | `LGRC9V3.step(...)`, `LGRC9V3.set_causal_flux_routes(...)` |
| LGRC9V3 autonomous production | Producer/executor split for packet departures and boundary-birth trials. | `LGRC9V3.produce_events(...)`, `LGRC9V3.run_autonomous(...)` |
| LGRC9V3 causal sparks | Causally scheduled Lane A/Lane B candidate diagnostics at arrival/local-update boundaries. | `LGRC9V3.step(...)`, `LGRC9V3.evaluate_causal_spark_diagnostics(...)` |
| LGRC-2 compaction | Compact pending-flux view over in-flight packets. | `compact_lgrc9v3_packet_ledger(...)` |
| LGRC-3 contract | Topology-changing causal-history field and event-kind contract. | `build_lgrc9v3_topology_contract_artifact(...)` |
| LGRC-3 packet transport | Packet endpoint/lineage transport through one mechanical expansion. | `transport_lgrc9v3_packets_through_refinement(...)` |
| LGRC-3 policy contract | Default-disabled collapse/reabsorption and proper-time identity payload policy. | `build_lgrc9v3_lgrc3_policy_contract_artifact(...)` |
| LGRC-3 proper-time inheritance | Uniform parent proper-time inheritance evidence after mechanical expansion. | `process_lgrc9v3_proper_time_inheritance(...)` |
| LGRC-3 collapse/reabsorption | Budget-conserving collapse/reabsorption lineage evidence. | `process_lgrc9v3_collapse_reabsorption(...)` |
| LGRC-3 collapse packet transport | Packet and pending-flux redirection/settlement through collapse/reabsorption. | `transport_lgrc9v3_packets_through_collapse_reabsorption(...)` |
| LGRC-3 identity evaluator | Sink-local proper-time identity persistence pass/fail evidence. | `evaluate_lgrc9v3_proper_time_identity_persistence(...)` |
| LGRC-3 identity acceptance | Explicit identity-acceptance event emission after passing evaluator and enabled policy. | `emit_lgrc9v3_proper_time_identity_acceptance(...)` |
| LGRC-3 replay validation | Audit ordering, lineage, and budget continuity across LGRC-3 evidence. | `validate_lgrc9v3_topology_event_replay(...)` |

Not implemented:

- full event-driven LGRC propagation;
- delayed-evaluation continuity as an active runtime path;
- default automatic mechanical expansion from causal spark candidates;
- broad autonomous discovery for collapse/reabsorption and identity
  acceptance;
- general LGRC, LGRC-V3, executable `LGRC9`, or executable `LGRCV3`.

Current examples:

| Script | Slice |
|---|---|
| `examples/lgrc9v3/executable_runtime.py` | Construct executable `LGRC9V3`, schedule one packet, and process the queue with `LGRC9V3.step()`. |
| `examples/lgrc9v3/landscape_seed_runtime.py` | Build executable `LGRC9V3` directly from a GRCL9V3 landscape seed through the library-owned lowering facade. |
| `examples/lgrc9v3/autonomous_produce_then_step.py` | Call `produce_events(...)`, inspect the scheduled packet evidence, then consume it with `step()`. |
| `examples/lgrc9v3/autonomous_run.py` | Compare manual packet queue seeding with `run_autonomous(...)` over the same route. |
| `examples/lgrc9v3/executable_packet_queue.py` | Configure packetized local-update routes and process routed LGRC9V3 queue events. |
| `examples/lgrc9v3/causal_spark_diagnostics.py` | Trigger Lane B candidate evidence at a causal arrival/local-update boundary. |
| `examples/lgrc9v3/telemetry_visual_bundle.py` | Save LGRC9V3 telemetry/checkpoints and render graph visual artifacts. |
| `examples/lgrc9v3/corrected_cascade_comparison.py` | Reproduce the corrected front-capacity GRC9V3/LGRC9V3 comparison run. |
| `examples/lgrc9v3/causal_history_surfaces.py` | LGRC-0/LGRC-1 annotation and eligibility. |
| `examples/lgrc9v3/packetized_causal_flux.py` | LGRC-2 fixed-topology packet processing. |
| `examples/lgrc9v3/refinement_packet_transport.py` | LGRC-3 refinement packet transport smoke path. |
| `examples/lgrc9v3/active_lgrc3_causal_history.py` | Active LGRC-3 helper chain through refinement transport, proper-time inheritance, collapse/reabsorption, identity evidence, and replay validation. |

The controlled GRC9V3/LGRC9V3 comparison fixtures and Iteration 31-A stress
sweep live in `tests/models/test_lgrc_9_v3_runtime.py`.

## Reproducible Corrected Cascade Comparison

The large comparison artifacts are intentionally generated under `outputs/`
and are not tracked. The tracked reproduction entry point is:

```bash
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
```

The script regenerates the corrected synchronous baseline if absent:

```text
session id:
    S_LGRC_COMPARE_CORRECTED

fixture:
    appendix_e_cell_division_corrected_full_capacity_cascade

baseline command:
    python -m pygrc.telemetry.grcl9v3_replay
        --session-id S_LGRC_COMPARE_CORRECTED
        --steps 20
        --source-mode landscape_seed_examples
        --fixture appendix_e_cell_division_corrected_full_capacity_cascade
```

Then it runs native `LGRC9V3` queue execution for 100 events from the corrected
initial state. The LGRC run does not call synchronous `GRC9V3.step()`. It
refreshes the substrate's non-topological diagnostic/transport/identity labels
and then uses:

```text
causal_layer_mode = topology_changing_causal_history
lgrc_runtime_level = lgrc3
lapse_policy = unit
edge_delay_policy = constant_delay
proper_time_accumulation_policy = local_event_frontier
causal_boundary_birth_allowed = true
causal_boundary_birth_policy = grc9v3_outward_flux_probability
causal_topology_integration_allowed = true
causal_spark_expansion_allowed = true
causal_refinement_packet_transport_allowed = true
causal_proper_time_inheritance_allowed = true
```

Expected topological result:

```text
GRC9V3 corrected baseline:
    20 synchronous steps
    31 event rows
    final topology = 29 nodes / 28 edges

LGRC9V3 corrected queue run:
    100 native queue events
    final topology = 29 nodes / 28 edges
    max packet budget error ~= 2.84e-14
```

Expected activity result:

```text
GRC9V3 touched nodes in event evidence:
    18

LGRC9V3 touched nodes in event evidence:
    30
```

Generated records:

```text
outputs/examples/lgrc9v3_corrected_comparison/comparison_summary.md
outputs/examples/lgrc9v3_corrected_comparison/comparison_report.json
outputs/examples/lgrc9v3_corrected_comparison/visuals/.../graph_sequence.png
outputs/examples/lgrc9v3_corrected_comparison/visuals/comparison/.../graph_comparison.png
```

Interpretation:

```text
The corrected cascade reaches the same final topological surface under
synchronous GRC9V3 and native LGRC9V3 queue execution, while the code paths and
clock semantics are different.
```

Boundary:

```text
This is not a proof that one LGRC queue event equals one GRC9V3 step.
It is a corrected source/frontier comparison with equal final topology and
different runtime evidence.
```

Known visualization caveat:

```text
The LGRC graph sequence and graph comparison render. The current final
interactive HTML/animation path may report:

    AssertionError: non existent node '0'

because the graph HTML renderer tries to draw lineage from a removed expanded
node. That is a visualization-layer limitation, not a runtime or telemetry
failure.
```

## Stable Imports

Current examples import LGRC9V3 helpers and the executable runtime from
`pygrc.models`. The stable import surface now includes:

```python
from pygrc.models import (
    LGRC9V3,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
    LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1,
    LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND,
    LGRC9V3_LOCAL_UPDATE_EVENT_KIND,
    LGRC9V3RuntimeState,
    build_lgrc9v3_from_landscape_seed,
    build_lgrc9v3_packet_ledger,
    compact_lgrc9v3_packet_ledger,
    emit_lgrc9v3_proper_time_identity_acceptance,
    evaluate_lgrc9v3_proper_time_identity_persistence,
    prepare_lgrc9v3_landscape_runtime,
    prime_lgrc9v3_broad_seed_packets,
    prime_lgrc9v3_corrected_cascade_broad_seed,
    prime_lgrc9v3_corrected_cascade_queues,
    prime_lgrc9v3_packet_departures,
    process_lgrc9v3_collapse_reabsorption,
    process_lgrc9v3_packet_departure,
    process_lgrc9v3_proper_time_inheritance,
    transport_lgrc9v3_packets_through_collapse_reabsorption,
    transport_lgrc9v3_packets_through_refinement,
    validate_lgrc9v3_topology_event_replay,
)
```

Telemetry and visualization entry points used by the executable examples are:

```python
from pygrc.telemetry import (
    build_lgrc9v3_graph_checkpoint,
    lgrc9v3_event_family_extensions_for_events,
    lgrc9v3_step_family_extensions,
)
from pygrc.visualization import (
    build_graph_run_visualization_layout,
    render_graph_run_visual_bundle,
)
```

The helper functions remain stable evidence surfaces. They operate on
`GRC9V3State`, packet ledgers, explicit topology/lineage ids, and existing
`GRCEvent` topology evidence. `LGRC9V3` is the first model-class API. Its
`step()` loop owns deterministic queued packet departure/arrival processing,
scheduled causal boundary-birth trials, causal local-update/spark evidence,
and opt-in topology integration gates.

## Runtime Class Decision

Iteration 24 accepts a concrete executable `LGRC9V3` model class as the target
for Iterations 25+. Iteration 25 implements the first event-queue shell.

Current runtime boundary:

```text
LGRC9V3 implements/shares the GRCModel interface.
LGRC9V3 uses composition over GRC9V3State.
LGRC9V3 does not subclass GRC9V3 or inherit synchronous GRC9V3.step()
semantics.
```

The runtime state owns:

```text
base GRC9V3State
causal timing fields
packet ledger
event queue
topology-event/replay ledger
causal-history modes and policies
diagnostic history needed by causal spark evaluation
```

Current helper APIs remain stable. `LGRC9V3.from_state(...)` explicitly
initializes causal clocks, packet ledgers, queue state, topology history, and
policies from a `GRC9V3State` substrate. Old `GRC9V3` snapshots remain
synchronous snapshots
unless an explicit LGRC adapter or synchronous-limit policy is used.

`LGRC9V3.snapshot()`, `LGRC9V3.save(...)`, and `LGRC9V3.load(...)` now support
native LGRC9V3 runtime snapshots. `LGRC9V3.load(...)` restores snapshots whose
metadata declares `model_family = "LGRC9V3"`. Legacy `GRC9V3` snapshots should
still be loaded as synchronous `GRC9V3` unless an explicit adapter is used.

## Landscape Construction

LGRC9V3 can be constructed directly from GRCL9V3 landscape seeds through the
library-owned construction facade:

```python
from pygrc.models import LGRC9V3, build_lgrc9v3_from_landscape_seed

model = LGRC9V3.from_landscape_seed(seed)

same_model = build_lgrc9v3_from_landscape_seed(seed)
```

The facade still lowers the seed through the proven GRC9V3 landscape compiler
into a `GRC9V3State` substrate, then wraps that substrate in native
`LGRC9V3RuntimeState`. This is the intended construction path for examples
that need landscape-defined initial conditions without hand-building runtime
state dictionaries.

## Timing Vocabulary

LGRC9V3 keeps these fields distinct.

| Field | Alias | Meaning |
|---|---|---|
| `scheduler_event_index` | `kappa` | Event-processing order. |
| `checkpoint_index` | `k` | Snapshot/replay order. |
| `event_time_key` | `T_e` | Scheduler/event-queue ordering key. |
| `node_proper_time` | `tau_i` | Local accumulated proper time. |
| `edge_causal_delay` | `tau_ij` | Edge causal delay. |

Synchronous `GRC9V3.step_index` is not automatically any of these. Current
LGRC-0/LGRC-1 helpers may map `step_index` into `event_time_key` only through
an explicit policy such as:

```text
event_time_policy = "synchronous_limit"
event_time_scale = ...
```

## LGRC-0 Annotation

LGRC-0 computes derived evidence over an existing `GRC9V3State`.

```python
from pygrc.models import (
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LAPSE_POLICY_UNIT,
    annotate_lgrc9v3_causal_history,
)

annotation = annotate_lgrc9v3_causal_history(
    model.get_state(),
    causal_modes={
        "lapse_policy": LAPSE_POLICY_UNIT,
        "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
        "event_time_policy": "synchronous_limit",
    },
    event_time_scale=0.1,
    edge_delay_kwargs={"tau_0": 0.1},
)
```

The result includes:

- `node_proper_time`;
- `edge_causal_delay`;
- event-time records for supplied events;
- geometric, causal/proper-time, and functional/coupling distance surfaces;
- causal cone overlays;
- derived causal basin-core evidence.

LGRC-0 is labelled:

```text
annotation_only = true
evidence_class = "derived_annotation"
causal_layer_mode = "annotation"
lgrc_runtime_level = "lgrc0"
```

It does not mutate topology, events, budgets, observables, spark decisions, or
identity state.

## LGRC-1 Fixed-Topology Eligibility

LGRC-1 makes proper-time eligibility operational on fixed topology, but remains
semi-causal unless causal availability buffers exist.

```python
from pygrc.models import compute_lgrc9v3_fixed_topology_eligibility

eligibility = compute_lgrc9v3_fixed_topology_eligibility(
    model.get_state(),
    causal_modes={
        "causal_layer_mode": "fixed_topology_semicausal",
        "lgrc_runtime_level": "lgrc1",
        "proper_time_accumulation_policy": "global_scheduler",
        "lapse_policy": "unit",
        "edge_delay_policy": "constant_delay",
        "require_fixed_topology_for_lgrc1": True,
    },
    min_delta_tau=1.0,
)
```

The result includes:

- `node_proper_time`;
- `node_last_update_proper_time`;
- `node_elapsed_proper_time`, where `delta_tau_i = tau_i - tau_i_last_update`;
- eligible and ineligible node ids;
- next last-update proper-time values for processed nodes;
- fixed topology signature;
- budget before/after/error evidence.

The artifact explicitly records:

```text
semi_causal = true
causal_availability_buffers = false
packetized_flux = false
topology_change_allowed = false
mechanical_expansion_allowed = false
collapse_allowed = false
identity_acceptance_allowed = false
```

Requesting mechanical expansion, collapse, identity acceptance, or packetized
flux through the LGRC-1 helper is rejected in the current slice.

## Artifact Blocks

LGRC-0 annotation artifacts use the optional key:

```text
causal_history
```

Helpers:

| Helper | Purpose |
|---|---|
| `build_lgrc9v3_causal_history_artifact(annotation)` | Build a standalone causal-history artifact envelope. |
| `attach_lgrc9v3_causal_history_artifact(artifact, annotation)` | Attach a `causal_history` block to a top-level artifact copy. |
| `extract_lgrc9v3_causal_history_artifact(artifact)` | Return the causal-history block, or `None` for non-LGRC evidence. |
| `restore_lgrc9v3_causal_annotation_artifact(artifact)` | Restore an annotation object, or `None` for old non-LGRC artifacts. |

Missing `causal_history` means non-LGRC evidence. Readers must not invent LGRC
semantics for old `GRC9` or `GRC9V3` snapshots.

## Synchronous Limit

The tested compatibility surface uses:

```text
lapse_policy = "unit"
edge_delay_policy = "constant_delay"
event_time_policy = "synchronous_limit"
```

This proves compatibility and no-regression only:

```text
LGRC-0/LGRC-1 evidence can be computed over GRC9V3 without corrupting the
synchronous runtime.
```

It does not prove full LGRC dynamics.

## LGRC-2 And LGRC-3 Runtime Surfaces

LGRC-2 now has a packet/event-queue contract. It defines:

- event queue keys and ordering;
- packet departure/arrival events;
- in-flight coherence budget invariant;
- packet ledger representation;
- replay and artifact schema for packet lifecycle;
- relation between packet arrival and spark/diagnostic eligibility;
- scheduled packet departure processing;
- compact pending-flux ledger derivation;
- fixed-topology/no-identity boundaries.

The current LGRC-2 surface can build passive packet records, queue-event
records, deterministic packet/event ids, fixed-topology ledger artifacts, and
active fixed-topology departure/arrival processing.

Scheduled packet state is operational. Use
`schedule_lgrc9v3_packet_departure(...)` to add a scheduled packet and queued
departure event without debiting source coherence. Processing that queued
departure transitions the packet to `in_flight`, debits the source, and queues
the arrival.

The normal LGRC-2 path derives packet arrival `T_e` from the edge-delay surface
captured for the scheduling/departure decision:

```text
arrival_event_time_key =
    departure_event_time_key + edge_causal_delay[edge_id]
```

Use `derive_lgrc9v3_packet_arrival_event_time_key(...)` for this. The result is
an event-queue ordering key, not `tau_i` for the source and not `tau_j` for the
target. Explicit `arrival_event_time_key` values remain allowed for fixtures
and replay, but they should be read as explicit event-time keys rather than
local proper-time evidence.

Departure processing subtracts coherence from the source node and adds the
same amount to the in-flight packet total. Arrival processing removes that
amount from in-flight packets and credits the target node. The processing
result records `kappa`, `T_e`, source/target node ids, edge id, amount, and
budget evidence for the transition:

```text
B = sum_i C_i + sum_p C_p
```

Arrival can expose positive eligibility evidence through
`derive_lgrc9v3_packet_arrival_eligibility(...)`. That artifact says the
arrival target can be considered for a local update or spark diagnostic. It
does not itself run the spark predicate. In executable `LGRC9V3.step()`, the
arrival/local-update boundary may then evaluate Lane A/Lane B spark diagnostics
and emit `lgrc9v3_causal_spark_candidate` evidence. A candidate is still not a
refinement, collapse, or identity event.
LGRC-2 should not be folded silently into the current LGRC-0/LGRC-1 helper
surfaces or into later topology-changing LGRC-3 semantics.

The important implementation boundary is that LGRC-2 helper processing mutates
the passed `GRC9V3State` node coherences, while executable `LGRC9V3` owns a
composed runtime state with packet ledger, event queue, local-update log, and
causal spark diagnostic log.

The pending-flux ledger compaction gate is now defined. Canonical LGRC-2 packet
ledgers stay per-packet. `compact_lgrc9v3_packet_ledger(...)` derives a compact
pending-flux ledger over in-flight packets. It aggregates only by exact:

```text
source node
target node
edge id
arrival event-time key
source lineage id
target lineage id
```

and preserves packet ids, departure keys, total amount, and lineage fields for
later refinement transport audits. The compact ledger is budget-equivalent to
the expanded packet ledger:

```text
pending_flux_total == in_flight_packet_total
conserved_budget_total == node_coherence_total + pending_flux_total
```

It is not packet transport through topology change. That remains LGRC-3.

The LGRC-3 contract artifact is now defined by
`build_lgrc9v3_topology_contract_artifact(...)`. It records that LGRC-3 builds
on LGRC-2 packet accounting and pending-flux compaction. Its original
topology-changing refinement surface named these event kinds:

```text
lgrc9v3_refinement_topology_event
lgrc9v3_refinement_packet_transport
lgrc9v3_proper_time_inheritance
```

The active LGRC-3 helper chain now also includes explicit, policy-gated
collapse/reabsorption and proper-time identity evidence:

```text
lgrc9v3_causal_collapse
lgrc9v3_causal_reabsorption
lgrc9v3_proper_time_identity_acceptance
```

Those surfaces are available through explicit processors/evaluators. They are
not broad autonomous discovery mechanisms and they are not emitted by default
merely because a mechanical expansion occurred.

Iteration 14 adds `transport_lgrc9v3_packets_through_refinement(...)`. It
consumes a pre-expansion packet ledger, a GRC9V3
`hybrid_mechanical_expansion` event, a post-expansion topology signature, and
optionally the compact pending-flux ledger.

The helper emits `lgrc9v3_refinement_packet_transport_result` evidence. It
updates in-flight packet endpoint/lineage evidence through the expansion
`reassignment_map`, preserves packet ids and amounts, updates queued future
arrival records, and records old/new boundary port-column evidence when a
packet endpoint is transported.

It preserves:

```text
B = sum_i C_i + sum_p C_p
```

and keeps:

```text
identity_acceptance_emitted = false
packet_transport_identity_transfer = false
```

Iteration 17 adds `process_lgrc9v3_proper_time_inheritance(...)`. It consumes
a GRC9V3 `hybrid_mechanical_expansion` event, the parent `node_proper_time`
surface captured at the refinement event, and the expansion's replacement
node/internal edge ids.

The helper emits `lgrc9v3_proper_time_inheritance_result` evidence with
topology event kind:

```text
lgrc9v3_proper_time_inheritance
```

under:

```text
proper_time_inheritance_policy = "uniform_parent_proper_time"
internal_edge_delay_policy = "explicit_or_default_tau0"
```

Uniform inheritance means each newly created node receives the expanded
parent's proper-time value at the refinement event. Internal edge delays are
recorded from explicit input when supplied, or from configured `tau_0`
otherwise.

The inheritance evidence keeps scheduler event index, checkpoint index, and
event-time key as separate serialized fields, and keeps:

```text
identity_acceptance_emitted = false
refinement_lineage_identity_persistence = false
```

Iteration 18 adds `process_lgrc9v3_collapse_reabsorption(...)`. It consumes
explicit sink-selection/collapse evidence parameters: competing/selected/losing
sinks, transferred nodes, explicit lineage transfer maps, proper-time surfaces,
and packet/pending-flux ledgers when available.

The current helper does not take a single basin/collapse artifact object. A
future replay/runtime adapter may collect those explicit fields from a richer
basin-collapse artifact and call the same processor.

The helper emits `lgrc9v3_collapse_reabsorption_result` evidence whose
topology event kind is one of:

```text
lgrc9v3_causal_collapse
lgrc9v3_causal_reabsorption
```

under:

```text
budget_transfer_policy = "budget_conserving_transfer"
lineage_transfer_policy = "explicit_lineage_transfer_map"
proper_time_transfer_policy = "selected_sink_clock_continuity"
```

The processor must be explicitly enabled by the caller. This keeps the default
policy contract conservative while allowing active evidence when the project
opens the surface:

```text
collapse_reabsorption_allowed = true
collapse_reabsorption_processing_implemented = true
```

The helper records affected packet and pending-flux ids from supplied ledgers.
Iteration 19 adds `transport_lgrc9v3_packets_through_collapse_reabsorption(...)`
to carry those ledgers through the collapse lineage map.

The transport helper consumes the pre-collapse packet ledger, the
collapse/reabsorption result, and optionally the compact pending-flux ledger.
Affected in-flight packet endpoints are redirected to the selected sink through
the explicit lineage map. Packet ids are preserved while packets remain in
flight. If a packet becomes a selected-sink self-loop, it is settled into the
returned ledger's node-coherence total and removed from the future queue.

The helper emits `lgrc9v3_collapse_reabsorption_packet_transport_result`
evidence under:

```text
transport_policy = "redirect_to_selected_sink_or_settle_self_loop"
```

It preserves source pending-flux entry links, rewrites pending-flux endpoints
through the same lineage map, and keeps historical packet event records
unchanged.

It keeps:

```text
identity_acceptance_emitted = false
packet_transport_identity_transfer = false
```

Iteration 15 adds `build_lgrc9v3_lgrc3_policy_contract_artifact(...)`. It
defines the default-disabled policy-gated payload shape for
collapse/reabsorption and proper-time identity acceptance.

The policy contract records these first-round choices:

```text
budget_transfer_policy = "budget_conserving_transfer"
lineage_transfer_policy = "explicit_lineage_transfer_map"
proper_time_transfer_policy = "selected_sink_clock_continuity"
identity_clock_policy = "sink_local_proper_time"
threshold_calibration_policy = "local_median_delay_multiplier"
threshold_multiplier = 4.0
```

and keeps:

```text
collapse_reabsorption_allowed = false
identity_acceptance_allowed = false
collapse_reabsorption_processing_implemented = false
proper_time_identity_processing_implemented = false
mechanical_expansion_is_identity_acceptance = false
refinement_packet_transport_is_identity_transfer = false
```

The policy contract remains conservative by default. Packet transport,
proper-time inheritance, collapse/reabsorption evidence, and identity
acceptance are narrow LGRC-3 processing surfaces unless a runtime path or
caller explicitly enables the corresponding policy.

The active LGRC-3 helper/evidence iterations after this contract are now
implemented:

- Iteration 19: packet and pending-flux transport through
  collapse/reabsorption;
- Iteration 20: sink-local proper-time identity persistence evaluation;
- Iteration 21: identity acceptance event emission after explicit policy
  enablement;
- Iteration 22: topology event replay validation for budget, lineage, and
  event-time order;
- Iteration 23: active LGRC-3 examples and handoff.

These are direct LGRC-3 continuations, not general LGRC or LGRC-V3 work.

Those helper/evidence iterations did not by themselves make LGRC9V3 a
standalone executable runtime. The later executable runtime-parity arc is now:

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
- Iteration 32: executable examples and handoff (complete);
- Iterations 33-37: implementation-state recording, module split,
  construction facade, native snapshot restore, and readable examples
  (complete);
- Iterations 38-42: autonomous producer contract, packet-departure producer,
  boundary-birth producer, bounded autonomous run loop, and autonomy examples
  (complete).

Iteration 27 closes the first spark parity gap. LGRC9V3 now emits
`lgrc9v3_causal_spark_candidate` events when the existing Lane A or opt-in
Lane B predicate fires at a causal diagnostic boundary. These events remain
candidate evidence only by default. Mechanical expansion and topology
integration require explicit LGRC9V3 topology-integration gates.

LGRC-3 should not reinterpret LGRC-0 annotation, LGRC-1 semi-causal
eligibility, or fixed-topology LGRC-2 packet evidence.

## Proper-Time Identity Persistence Evaluation

Iteration 20 adds the active evaluator:

```python
evaluate_lgrc9v3_proper_time_identity_persistence(...)
```

The evaluator consumes topology/lineage ids, basin membership or basin-core
evidence, node proper-time surfaces, and a local edge-delay calibration. It
uses:

```text
identity_clock_policy = "sink_local_proper_time"
threshold_calibration_policy = "local_median_delay_multiplier"
```

and computes:

```text
proper_time_persistence_threshold =
    threshold_multiplier * local_median_edge_delay

observed_persistence_duration =
    window_end_sink_proper_time - window_start_sink_proper_time
```

The output artifact is:

```text
artifact_kind =
    "lgrc9v3_proper_time_identity_persistence_evaluation"
```

This artifact is pass/fail evidence only. It records:

```text
identity_acceptance_allowed = false
identity_acceptance_emitted = false
state_mutated = false
topology_mutated = false
```

Identity acceptance remains a separate event-emission step.

The evaluator intentionally consumes string ids for topology, lineage, and
basin-core evidence rather than full event objects. This keeps the current
helper-only architecture explicit: replay/runtime adapters may resolve richer
objects into those ids later, but the evaluator itself remains a narrow,
serializable evidence function.

## Proper-Time Identity Acceptance

Iteration 21 adds:

```python
emit_lgrc9v3_proper_time_identity_acceptance(...)
```

The emitter consumes a passing
`LGRC9V3ProperTimeIdentityPersistenceEvaluation` and requires:

```text
identity_acceptance_allowed = true
```

It emits exactly one `GRCEvent`:

```text
kind = "lgrc9v3_proper_time_identity_acceptance"
event_schema_version = "lgrc9v3_proper_time_identity_acceptance_event_v1"
evidence_class = "proper_time_identity_acceptance"
```

The payload links to:

```text
source_identity_evaluation_id
source_topology_event_ids
source_basin_evidence_id
lineage_id
```

and keeps identity distinct from mechanical expansion and packet transport:

```text
mechanical_expansion_emitted = false
packet_transport_emitted = false
mechanical_expansion_is_identity_acceptance = false
refinement_packet_transport_is_identity_transfer = false
state_mutated = false
topology_mutated = false
```

This event is active identity evidence, but it is not by itself a full
LGRC9V3 event-driven runtime loop.

## Topology Replay Validation

Iteration 22 adds:

```python
validate_lgrc9v3_topology_event_replay(...)
```

The validator consumes an ordered replay sequence containing LGRC-3
artifacts/events such as:

```text
lgrc9v3_refinement_packet_transport_result
lgrc9v3_proper_time_inheritance_result
lgrc9v3_collapse_reabsorption_result
lgrc9v3_collapse_reabsorption_packet_transport_result
lgrc9v3_proper_time_identity_persistence_evaluation
lgrc9v3_proper_time_identity_acceptance
```

It emits:

```text
artifact_kind = "lgrc9v3_topology_event_replay_validation"
artifact_schema_version = "lgrc9v3_topology_event_replay_validation_v1"
evidence_class = "topology_event_replay_validation"
```

The validator checks that event-time keys are nondecreasing, source topology
ids and identity-evaluation references point backward to prior replay evidence,
lineage ids are present where semantic lineage is required, and budget-bearing
records conserve budget across the sequence.

This is an audit/replay surface. It does not schedule events, run an event
queue, mutate state, or provide a standalone `LGRC9V3.step()` loop.

## Native Packet-Loop Route Aspects

Phase 8 Iterations 44-48 add a native packet-loop surface for the bounded
D2.3 mechanism discovered in the N03 polarized-basin-loop experiment.

The surface is composed of three parts:

```text
LGRC9V3RouteAspect
LGRC9V3.set_route_aspect_surplus_trigger(...)
validate_lgrc9v3_self_rearm_evidence_artifacts(...)
```

`LGRC9V3RouteAspect` records pole masks, channel order, expected next-channel
semantics, direction, and stable digests:

```text
route_aspect_digest
pole_region_digest
channel_sequence_digest
```

The surplus-trigger producer is explicit and policy-gated:

```text
produce_events(policy="packet_departure_from_route_surplus")
```

It inspects runtime node coherence, records observed pole mass and surplus,
and schedules a packet departure when the configured threshold is crossed. The
producer does not debit coherence. Packet budget mutation still starts only
when `LGRC9V3.step()` processes the queued packet departure.

Native self-rearm evidence is emitted only for the auditable chain:

```text
parent packet arrival processed by step()
-> producer observes post-arrival source-pole surplus
-> producer schedules child packet departure
-> step() processes the child departure
```

The event kind is:

```text
lgrc9v3_self_rearm_evidence
```

Completed self-rearm evidence links:

```text
parent_packet_id
parent_arrival_event_id
producer_record_id
child_packet_id
child_departure_event_id
route_aspect_digest
parent_arrival_channel_id
trigger_channel_id
expected_next_channel_id
```

and records event-time, scheduler-index, proper-time, and per-transition
budget evidence.

Snapshots preserve the route-aspect trigger configuration, autonomous
production log, and self-rearm log through
`dynamics.lgrc9v3_runtime.cached_quantities`. The persisted producer log lets
the artifact-only self-rearm validator replay chains after save/load without
retaining the return value from `produce_events(...)`. LGRC9V3 telemetry exposes
self-rearm events under the `self_rearm` event domain and includes a
`packet_loop` step/checkpoint surface with route-aspect digest, producer-policy
evidence, and completed self-rearm counts.

The supported claim is deliberately narrow:

```text
native LGRC9V3 supports artifact-validated surplus-triggered packet loops
```

The following claims remain blocked by this surface:

```text
native GRC9V3 proposal-flux loop evidence
movement or locomotion
agency, intention, or biological behavior
identity acceptance
```

Run the minimal example with:

```bash
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/native_packet_loop.py
```
