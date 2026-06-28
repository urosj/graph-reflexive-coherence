# LGRC9V3 Examples

These examples show the current LGRC-9 implementation slice.

Important boundary:

```text
Current LGRC9V3 examples include a narrow executable model class:
    LGRC9V3

LGRC9V3 is not synchronous GRC9V3.step().
LGRC9V3 is not general LGRC, executable LGRC9, or executable LGRCV3.
```

Use these examples when you want to see:

- how to build a `GRC9V3` state first;
- how to construct executable `LGRC9V3`;
- how `LGRC9V3.step()` processes causal queue events;
- how LGRC-0 annotation adds derived proper-time and delay evidence;
- how LGRC-1 computes `delta_tau_i` eligibility on fixed topology;
- how LGRC-2 packet departure/arrival preserves
  `sum_i C_i + sum_p C_p`;
- how executable packet arrivals advance local proper time and schedule
  packetized local-update routes;
- how `produce_events(...)` schedules causal work without consuming it;
- how `run_autonomous(...)` runs a bounded producer-plus-executor loop;
- how route-aspect surplus triggers can produce native, artifact-validated
  self-rearming packet loops;
- how causally scheduled Lane A/Lane B spark diagnostics are emitted as
  `lgrc9v3_causal_spark_candidate` events;
- how packet arrival `T_e` is derived from a captured edge-delay surface;
- how LGRC-2 derives a compact pending-flux ledger from in-flight packet
  records without replacing the canonical packet ledger;
- how LGRC-3 consumes a GRC9V3 mechanical expansion event and transports
  in-flight packet endpoint/lineage evidence through refinement;
- how active LGRC-3 processors compose proper-time inheritance,
  collapse/reabsorption evidence, collapse packet transport, proper-time
  identity evaluation, identity acceptance, and replay validation;
- how to distinguish a multi-basin telemetry/control surface over an unchanged
  graph from a visible topology birth/refinement checkpoint sequence;
- what artifact labels prevent overclaiming full LGRC dynamics.

## LGRC-2 Versus Active LGRC-3

LGRC-2 is fixed-topology packetized causal flux:

```text
GRC9V3State + LGRC9V3PacketLedger -> departure/arrival processing
```

It moves coherence through packet departure and arrival events while preserving:

```text
sum_i C_i + sum_p C_p
```

Active LGRC-3 starts when topology-changing causal-history evidence is
processed:

```text
GRC9V3 topology event + LGRC packet/proper-time evidence
    -> refinement/collapse/identity/replay artifacts
```

The current LGRC-3 scripts consume proven `GRC9V3` topology events and run
LGRC-owned helper processors around them.

Executable `LGRC9V3` now owns a composed runtime state:

```text
LGRC9V3RuntimeState =
    GRC9V3State
    + LGRC9V3PacketLedger
    + event queue
    + causal clocks
    + topology/spark diagnostic logs
```

`LGRC9V3.step()` processes one queued packet event or scheduled causal
boundary-birth trial. Packet arrivals can emit local-update evidence and
causally scheduled Lane A/Lane B spark candidates. Mechanical expansion still
requires explicit active topology-integration gates.

## Producer / Executor Boundary

Autonomous LGRC9V3 does not make `step()` opaque.

```text
produce_events(...)
    inspects current runtime state;
    schedules eligible packet departures or boundary-birth trials;
    emits producer evidence;
    does not consume queued work.

step()
    consumes exactly one queued event;
    performs packet debit/arrival, boundary-birth acceptance/rejection, or
    topology mutation when the queued event requires it.

run_autonomous(...)
    bounded loop:
        produce when queues are empty;
        consume through step();
        stop at max_events or when no producer can schedule work.
```

The smallest autonomy examples are:

```bash
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/autonomous_produce_then_step.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/autonomous_run.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/native_packet_loop.py
```

## Scripts

| Script | Purpose |
|---|---|
| `executable_runtime.py` | Construct executable `LGRC9V3`, schedule one packet, run `LGRC9V3.step()`, and inspect scheduler/event-time/proper-time fields. |
| `landscape_seed_runtime.py` | Build executable `LGRC9V3` directly from a GRCL9V3 landscape seed using the library-owned lowering facade, prime broad packet traffic, and run a short queue. |
| `autonomous_produce_then_step.py` | Configure one explicit causal flux route, call `produce_events(...)`, inspect the scheduled packet evidence, then consume it with `step()`. |
| `autonomous_run.py` | Compare manual packet queue seeding against `run_autonomous(...)` over the same route, showing equal packet lifecycle and selected coherence results. |
| `native_packet_loop.py` | Run a small route-aspect surplus-triggered packet loop and validate completed self-rearm chains from native artifacts. |
| `executable_packet_queue.py` | Configure packetized local-update routes and process a routed executable event queue. |
| `causal_spark_diagnostics.py` | Trigger opt-in Lane B candidate evidence at a causal arrival/local-update boundary. |
| `telemetry_visual_bundle.py` | Capture LGRC9V3 telemetry/checkpoint artifacts and render graph visuals under `outputs/examples/lgrc9v3/`. |
| `multi_basin_formation_bundle.py` | Run the opt-in multi-basin formation chain through flow-window, child-basin, replay, and fail-closed controls, then save telemetry/checkpoints and render graph visuals. This is a collapse/reabsorption telemetry/control example over an unchanged three-node graph, not visible node birth. |
| `topology_birth_refinement_visual_bundle.py` | Run the existing saturated-sink boundary-birth/refinement path and save checkpoints that visibly change node/edge structure. This is a topology-growth visualization companion, not an MB5/MB6 closeout claim. |
| `front_capacity_topology_birth_visual_bundle.py` | Run a GRCL9V3-source-backed front-capacity boundary-birth path and save checkpoints that visibly change node/edge structure. This is the corrected front-capacity visual companion to the diagnostic topology-growth fixture. |
| `corrected_cascade_comparison.py` | Reproduce the corrected front-capacity GRC9V3/LGRC9V3 comparison: 20 synchronous GRC9V3 steps versus 100 native LGRC9V3 queue events, with matching final topology and different runtime code paths. |
| `causal_history_surfaces.py` | Build a small GRC9V3 fixture, compute LGRC-0 and LGRC-1 evidence, and print the safe interpretation. |
| `packetized_causal_flux.py` | Use the lower-level helper API to process one fixed-topology LGRC-2 packet departure/arrival cycle, derive compact pending-flux evidence, and print the budget audit. |
| `refinement_packet_transport.py` | Create one in-flight LGRC-2 packet, trigger a GRC9V3 Lane B mechanical expansion, transport the packet evidence through refinement, and print the LGRC-3 budget/lineage audit. |
| `active_lgrc3_causal_history.py` | Compose the active LGRC-3 helper chain: refinement packet transport, proper-time inheritance, collapse/reabsorption, collapse packet transport, identity evaluation/acceptance, and replay validation. |

## Multi-Basin Versus Visible Topology Growth

`multi_basin_formation_bundle.py` demonstrates the Phase 8 multi-basin
telemetry/control surface. The generated graph checkpoints remain three nodes
and three edges:

```text
initial_node_count = 3
final_node_count = 3
initial_edge_count = 3
final_edge_count = 3
```

The topology-history records in that example are both
`lgrc9v3_causal_collapse` records: one collapse/reabsorption result and one
associated packet-transport result. Both report `topology_mutated = false`.
The child-basin state is intentionally narrow:

```text
child_basin_core_ids = [0]
child_basin_membership_by_core = {"0": [0, 1, 2]}
```

That example is useful for inspecting MB5 telemetry/replay/control artifacts,
but it is not a visible new-node or independent new-basin birth example.

Use `topology_birth_refinement_visual_bundle.py` when the goal is to inspect a
checkpoint sequence where topology visibly changes through the existing
saturated-sink boundary-birth/refinement fixture. This fixture is intentionally
kept as a diagnostic visual companion because it exercises an explicit,
aggressive topology-growth path rather than the corrected front-capacity
eligibility surface:

```text
checkpoint_node_counts = [10, 10, 11, 15]
checkpoint_edge_counts = [9, 9, 10, 14]
topology_event_kinds = [
    "lgrc9v3_causal_boundary_birth",
    "hybrid_mechanical_expansion",
    "lgrc9v3_refinement_packet_transport",
    "lgrc9v3_proper_time_inheritance",
]
```

The topology-growth bundle is a visualization and telemetry example. It does
not upgrade MB5/MB6, native support, semantic learning, agency, or Phase 8
completion claims.

Use `front_capacity_topology_birth_visual_bundle.py` when the goal is to inspect
visible topology growth through the corrected front-capacity boundary-birth
surface. It lowers a GRCL9V3 front-growth source, consumes
`grcl9v3_front_growth_eligible_ports` and
`grcl9v3_growth_parent_capacity_sources`, schedules a boundary-birth trial only
through that front-capacity metadata, and records a visible node/edge increase:

```text
causal_boundary_birth_parent_eligibility = grcl9v3_front_capacity
front_capacity_source = spark_expansion_front
visible_topology_growth = true
```

This corrected-front-capacity visual remains a topology-birth example, not an
MB5/MB6 closeout, native support, semantic learning, agency, or Phase 8
completion claim.

## Corrected Cascade Comparison

Use this command to regenerate the corrected comparison artifacts that are not
tracked because `outputs/` is gitignored:

```bash
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
```

The script first ensures the corrected synchronous baseline exists:

```text
fixture = appendix_e_cell_division_corrected_full_capacity_cascade
session = S_LGRC_COMPARE_CORRECTED
GRC9V3 steps = 20
```

Then it runs:

```text
LGRC9V3 native queue events = 100
causal_layer_mode = topology_changing_causal_history
lgrc_runtime_level = lgrc3
boundary birth = opt-in, GRC9V3 outward-flux probability
topology integration = opt-in spark expansion + packet transport + proper-time inheritance
```

Expected high-level result:

```text
GRC9V3 final topology:
    29 nodes / 28 edges

LGRC9V3 final topology:
    29 nodes / 28 edges

Interpretation:
    same corrected topological surface,
    different runtime code path and clock semantics.
```

The generated record is written to:

```text
outputs/examples/lgrc9v3_corrected_comparison/comparison_summary.md
outputs/examples/lgrc9v3_corrected_comparison/comparison_report.json
```

The comparison is not a step/event equivalence proof. It is a reproducible
source/frontier comparison showing that the corrected cascade can reach the
same final topology under synchronous GRC9V3 and native LGRC9V3 queue
execution, while LGRC also records causal packets, proper-time surfaces,
causal spark wrapping, refinement packet transport, and proper-time
inheritance.

The Iteration 31 GRC9V3/LGRC9V3 comparison fixtures live in
`tests/models/test_lgrc_9_v3_runtime.py`. They are test fixtures rather than
example scripts because their purpose is controlled parity evidence, not user
onboarding.

Iteration 31-A stress coverage also lives in
`tests/models/test_lgrc_9_v3_runtime.py`.

## References

- [LGRC9V3 Causal-History Reference Guide](../../docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md)
- [GRC Runtime Reference Guide](../../docs/reference/GRC-Runtime-ReferenceGuide.md)
- [GRC9V3 Examples](../grc9v3/README.md)
