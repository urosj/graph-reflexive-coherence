# Implementation Trace

This directory records what was done for the
`2026-05-N04-grc9v3-movement-ladders` experiment family and why.

Primary local planning documents:

- [`MovementLaddersImplementationPlan.md`](./MovementLaddersImplementationPlan.md)
- [`MovementLaddersImplementationChecklist.md`](./MovementLaddersImplementationChecklist.md)
- [`MovementLaddersHandoff.md`](./MovementLaddersHandoff.md)

Use this area for experiment-local notes such as:

- run plans,
- movement ladder fixture and seed design notes,
- pulse/boundary-coupling conventions,
- observed failures,
- interpretation changes,
- report closeouts,
- and links to generated artifacts.

This is not the global `implementation/` directory. It should not describe
project-wide runtime contracts unless an experiment result is being promoted
into a separate implementation task.

## Handoff Boundary

N04 starts after N03/E3 established a native LGRC9V3 self-rearming packetized
pulse substrate. That result does not by itself establish movement.

N04 must independently test:

```text
pulse -> boundary/front-rear coupling -> identity-preserving displacement
```

and must keep movement, locomotion-like, adaptive topology, agency, and
biological claims gated by the movement-ladder report rather than inherited
from N03.

Current resume point:

```text
MovementLaddersHandoff.md
```

As of the latest handoff, N04 has closed the Iterations 19-23 S7
port-graph/topology-mutating tranche and completed Iteration 20 repeatability
and stress, Iteration 21 choice-boundary probing, Iteration 21-B native route
arbitration rerun, Iteration 22 identity-through-topology probing, and
Iteration 22-B identity-through-native-route-arbitrated-topology probing.
Iteration 23 freezes the current ceiling as
`topology_mutating_movement_candidate`. Iteration 21-B resolves the old
route-selection exposure blocker as runtime route arbitration: candidate route
sets are emitted from runtime-visible evidence, native route-arbitration
selects one route, and the selected topology event is artifact-replayed through
lineage, reabsorption, producer scheduling, and `step()` processing. Iteration
22-B confirms that this native route-arbitrated continuity still does not
serialize a stable RC coherence-basin identity or validate attractor-basin
invariance through topology mutation. Semantic choice, agency, RC identity
collapse, identity acceptance, locomotion-like behavior, biological behavior,
inherited-N03 movement, and unrestricted movement remain blocked.

Current resume point:

```text
Choose the next post-topology-mutating tranche.
```

Current visual reference:

```text
../outputs/m_taxonomy_visual_reference/index.html
```

The visual pack covers the best current M0-M6 candidates. M5 and M6 include
native LGRC9V3 telemetry packs rendered through standard `pygrc.visualization`
outputs. M2 now has an experiment-local runtime timeseries reference from
Iteration 11-B; native LGRC telemetry packs remain available only for M5 and
M6.
