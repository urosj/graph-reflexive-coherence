# Implementation Trace

This directory records what was done for the
`2026-05-N03-grc9v3-polarized-basin-loops` experiment family and why.

Primary local planning documents:

- [`PolarizedBasinLoopsImplementationPlan.md`](./PolarizedBasinLoopsImplementationPlan.md)
- [`PolarizedBasinLoopsImplementationChecklist.md`](./PolarizedBasinLoopsImplementationChecklist.md)
- [`E1-LGRC9V3-AlignmentPlan.md`](./E1-LGRC9V3-AlignmentPlan.md)
- [`E1-LGRC9V3-AlignmentChecklist.md`](./E1-LGRC9V3-AlignmentChecklist.md)
- [`E2-LGRC9V3-NativeRuntimePlan.md`](./E2-LGRC9V3-NativeRuntimePlan.md)
- [`E2-LGRC9V3-NativeRuntimeChecklist.md`](./E2-LGRC9V3-NativeRuntimeChecklist.md)
- [`E3-LGRC9V3-NativePacketLoopReproductionPlan.md`](./E3-LGRC9V3-NativePacketLoopReproductionPlan.md)
- [`E3-LGRC9V3-NativePacketLoopReproductionChecklist.md`](./E3-LGRC9V3-NativePacketLoopReproductionChecklist.md)

Use this area for experiment-local notes such as:

- run plans,
- loop fixture and seed design notes,
- source/sink-aspect conventions,
- observed failures,
- interpretation changes,
- report closeouts,
- and links to generated artifacts.

This is not the global `implementation/` directory. It should not describe
project-wide runtime contracts unless an experiment result is being promoted
into a separate implementation task.

The E1 LGRC9V3 alignment docs are still experiment-local. They translate and
validate N03 D2.3 packet artifacts against LGRC-style event/packet concepts
without changing `src/*`.

The E2 LGRC9V3 native-runtime docs are also experiment-local. They ask the
stronger runtime question:

```text
Can native LGRC9V3.step or LGRC9V3.run_event_queue produce the D2.3 event
ledger through declared runtime primitives?
```

E2 must still avoid `src/*` changes. Any required core change is a stop point
and requires a separate implementation task.

The E3 LGRC9V3 native packet-loop reproduction docs are experiment-local
follow-up after the separate Phase 8 native packet-loop implementation. E3 does
not define new core behavior. It asks whether N03 can now be reproduced using
only native LGRC9V3 runtime surfaces, without the old experiment-local packet
prototype or adapter trigger as the execution engine.

## Document Roles

Use the original N03 plan/checklist for the experiment exploration record:

```text
What did we try?
What failed?
What passed?
Why did we branch?
What evidence was produced?
What claim boundary applies?
```

Use the E1 plan/checklist for the alignment and implementation-readiness
track:

```text
Can the packet-positive mechanism be expressed in LGRC9V3 terms?
What schemas, adapters, or validators are needed?
What existing LGRC9V3 surfaces are sufficient?
What is missing?
Does this stay experiment-local or need a future core task?
```

Use the E2 plan/checklist for the native-runtime execution track:

```text
Can existing LGRC9V3 execute the packet route?
Can runtime packet logs be extracted into the E1 ledger schema?
Can an adapter-triggered runtime loop preserve D2.3 controls?
Can native autonomy produce the same ledger without the adapter?
Is a core LGRC9V3 task actually required?
```

Use the E3 plan/checklist for the post-core reproduction track:

```text
Can the N03 D2.3 result be reproduced with native LGRC9V3 only?
Do positive clockwise/counter-clockwise rows pass through native route-aspects,
surplus triggers, step processing, and self-rearm evidence?
Do D2.3 negative controls remain negative without experiment-local execution
adapters?
Do snapshot/telemetry artifacts validate without private runtime state?
```

Relationship:

```text
N03 plan/checklist = discovery and evidence history
E1 plan/checklist = translate the discovered packet mechanism toward LGRC9V3
E2 plan/checklist = test existing LGRC9V3 runtime execution against E1 ledger
E3 plan/checklist = reproduce N03 after native LGRC9V3 packet-loop support exists
```

This keeps N03 open for exploration, keeps E1 grounded in evidence from the
packet-positive branch rather than theory alone, keeps E2 from being confused
with a core implementation branch, and keeps E3 as the native post-core
reproduction record.

## Current Status Before Movement Handoff

Current N03 status:

```text
native fixed-topology GRC9V3 proposal flux:
    negative for polarized loop formation on tested fixtures

experiment-local D2.3 packet prototype:
    positive for self-rearming packetized pulse behavior under controls

E1/E2 alignment:
    adapter-compatible and runtime-compatible, but E2 alone was not
    D2.3-equivalent native execution

E3 native LGRC9V3 packet loop:
    positive native D2.3-equivalent reproduction under controls

L5:
    resolved for native LGRC9V3 packetized execution

L6 / movement:
    unopened; belongs to a separate movement-ladder experiment
```

Fixture lineage note:

```text
N03 / E2 bridge fixture:
    12-node / 12-edge ported ring inherited from the original fixed-topology
    GRC9V3 exploration

E3 native reproduction fixture:
    compact 4-node / 4-edge four-pole route
    S1 -> K2 -> S2 -> K1 -> S1
```

The E3 fixture is smaller by design. E2 asked whether native LGRC9V3 could
execute packet routes against the earlier ring substrate and export a compatible
ledger. E3 asked a different question: whether the native route-aspect,
surplus-trigger, and self-rearm surfaces can reproduce the D2.3 packet-loop
mechanism directly. For that reproduction, each pole is represented by one
runtime node and each channel by one route hop.

Supported E3 claim:

```text
Native LGRC9V3 supports a D2.3-equivalent surplus-triggered,
self-rearming packet-loop runtime surface under fixed topology, with exact
node-plus-packet budget conservation and D2.3 controls preserved.
```

Still blocked:

```text
native GRC9V3 proposal-flux loop evidence
movement / locomotion
agency / intention
biological claims
general multi-pole basin-loop theory beyond the tested route
```

## E3 Visualization And Animation

Static E3 route visualization:

- [`e3_native_lgrc9v3_packet_loop_visualization.svg`](../reports/e3_native_lgrc9v3_packet_loop_visualization.svg)
- [`e3_native_lgrc9v3_packet_loop_visualization.md`](../reports/e3_native_lgrc9v3_packet_loop_visualization.md)
- [`e3_native_lgrc9v3_packet_loop_visualization.json`](../outputs/e3_native_lgrc9v3_packet_loop_visualization.json)

Standard LGRC/PyGRC E3 animation artifacts:

- [`graph_animation.gif`](../outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_animation.gif)
- [`graph_sequence.png`](../outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_sequence.png)
- [`final_graph.html`](../outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_html/final_graph.html)
- [`e3_native_lgrc9v3_packet_loop_animation.md`](../reports/e3_native_lgrc9v3_packet_loop_animation.md)
- [`e3_native_lgrc9v3_packet_loop_animation.json`](../outputs/e3_native_lgrc9v3_packet_loop_animation.json)

Replay command from the repository root:

```bash
PYTHONPATH=src .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/animate_e3_native_lgrc9v3_packet_loop.py
```

## Output Cleanup Status

Output cleanup is intentionally deferred. The large number of files under
`experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/` is not itself
a correctness problem while the branch history is still being reviewed.

The current priority is trace completeness: Branch B through E3 outputs remain
available so reviewers can replay how the result moved from negative native
GRC9V3 proposal flux, to experiment-local packet positivity, to native LGRC9V3
D2.3-equivalent reproduction. A later cleanup pass may consolidate or archive
outputs after the movement handoff is safely recorded.

## Movement Handoff Boundary

The E3 result may serve as a pulse substrate for the movement-ladders
experiment, but movement is not claimed here.

For movement work, the correct handoff statement is:

```text
N03 provides a native LGRC9V3 self-rearming packetized causal pulse.
Movement-ladder experiments must separately test whether that pulse couples to
boundary change, displacement, shape preservation, and fixed/adaptive topology
movement gates.
```

Movement experiments must not inherit an L6 or locomotion claim from E3. They
must define their own fixtures, controls, telemetry, nulls, and claim ceilings.
