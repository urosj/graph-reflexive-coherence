# LGRC9V3 Causal Time Design Observations

Date: 2026-05-07
Updated: 2026-05-16

Status: observed design implication from the corrected LGRC9V3 cascade run;
not an implementation change request.

2026-05-16 note: Phase 8 now also includes native packet-loop and native
causal pulse-substrate continuations. These continuations keep the same
event-ordering discipline described here: producers schedule through LGRC
queues, `step()` remains the mutation boundary, and surface rows are emitted
only from committed packet events. N04 Lane H uses those surfaces to support a
bounded `native_m6_same_fixture_self_renewal_candidate`; this does not change
the causal-time semantics below and does not promote locomotion-like,
adaptive-topology, agency, biological, identity-acceptance, or unrestricted
movement claims.

## Purpose

This note records what the corrected LGRC9V3 comparison run revealed about
local proper time, the current global event-time scaffold, and possible future
local-queue variants.

The tracked reproduction entry point for the run is:

```bash
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
```

Generated outputs live under `outputs/` and are intentionally not tracked.

## Current Clock Semantics

The current executable `LGRC9V3` runtime uses four distinct ordering/timing
surfaces:

```text
kappa:
    scheduler event ordinal

k:
    checkpoint index

T_e:
    event-time key used by the deterministic event queue

tau_i:
    node-local proper time
```

The global queue is ordered by `T_e`. This means the implementation has a
global event-time coordinate for deterministic processing and replay.

That does not mean `T_e` is node proper time. `T_e` is a scheduler/event-time
surface. Each node still has its own local clock `tau_i`.

## Proper-Time Advancement

When a node is touched by a local causal event, such as a packet departure,
packet arrival, or local update boundary, the runtime advances that node's
proper time from its previous event surface to the current event surface:

```text
delta_T = T_e - last_event_time_key[i]
delta_tau_i = N_i * delta_T
tau_i += delta_tau_i
last_event_time_key[i] = T_e
```

Here `N_i` is the node lapse value selected by `lapse_policy`.

This advancement is not "add one unit of time per packet." It is a lazy local
clock catch-up to the current causal event surface. If a node was last touched
at `T_e = 0.1` and is next touched at `T_e = 2.0`, then with unit lapse it
advances by:

```text
delta_tau_i = 1.0 * (2.0 - 0.1) = 1.9
```

Packet departure advances the source node's local clock. Packet arrival
advances the target node's local clock.

## Corrected Cascade Observation

In the corrected 100-event cascade run, the selected policy was:

```text
lapse_policy = unit
```

Therefore:

```text
N_i = 1
```

for every live node.

The observed local proper-time spread at the final checkpoint was therefore not
lapse-driven time dilation. It was caused by different nodes being touched at
different event-time surfaces.

Final live-node proper-time summary from the run:

```text
live nodes with tau_i:
    29

min tau_i:
    0.1

max tau_i:
    2.024

range:
    1.924

mean:
    1.2868275862068965

median:
    1.068
```

Interpretation:

```text
Nodes touched late by packet departures or arrivals advanced toward
T_e ~= 2.0.

Nodes born or inherited at the initial refinement surface and not touched again
remained near tau_i = 0.1.
```

This is still meaningful LGRC evidence: the runtime keeps local clocks, and
the final checkpoint exposes their divergence. But the divergence in this run
comes from event participation, not from different lapse rates.

## Lapse-Driven Time Dilation

In LGRC terminology, lapse-driven time dilation means two nodes can accumulate
different proper-time increments over the same event-time interval because
their lapse values differ.

Example:

```text
delta_T = 1.5

node A:
    N_A = 1.0
    delta_tau_A = 1.5

node B:
    N_B = 0.4
    delta_tau_B = 0.6
```

The current implemented lapse policies are:

```text
unit:
    N_i = 1 for every live node.

bounded_density_tension:
    N_i is derived from node coherence and gradient norm, bounded by
    configured minimum and maximum values.
```

The `bounded_density_tension` policy is a first-round LGRC policy surface. It
should be interpreted as a local reflexive activity-rate policy, not as a
literal general-relativistic gravitational lapse.

## What T_e Buys The Current Runtime

The current `T_e` scaffold gives the implementation:

```text
deterministic event ordering;
simple packet-arrival scheduling;
straightforward replay;
clear checkpoint ordering;
clean comparison against synchronous GRC9V3;
simple local-clock catch-up semantics.
```

This is why it is useful for the current executable `LGRC9V3` runtime.

The current design should be read as:

```text
global queue time:
    yes, T_e

local proper time:
    yes, tau_i

physical universal time claim:
    no
```

## Possible Future Local-Queue Variant

A more relational LGRC design could remove `T_e` as a causal semantic object
and use node-local queues instead.

Such a runtime would still need a computational processing order:

```text
kappa:
    scheduler event ordinal / deterministic execution order
```

But it would not need to interpret a scalar `T_e` as the event-time key that
all arrivals share.

Possible replacement mechanisms:

```text
edge transit clock:
    packets accumulate their own transit progress and arrive when progress
    reaches edge delay.

clock transport map:
    source-local departure time plus edge delay is mapped into target-local
    eligibility.

causal dependency graph:
    events become ready when predecessor events and delay constraints are
    satisfied, without a scalar universal event-time coordinate.
```

In such a design, local proper times would likely drift more strongly because
nodes would not be periodically projected onto a shared `T_e` surface. Drift
would become a primary semantic object rather than a side effect of which nodes
were touched late.

This is conceptually attractive, but it would require new rules for:

```text
packet transit progress;
source-clock to target-clock transport;
arrival eligibility;
fairness and non-starvation;
checkpoint/frontier comparison;
replay determinism;
visualization of non-scalar causal fronts.
```

## Possible Future Hierarchical-Queue Variant

The flat local-queue idea has a stronger fractal version: replace one global
event-time queue with nested queues attached to identities, basins, modules, or
scale levels.

This is closer to the Fractal Reflexive Coherence paper, where coherence
propagates not only spatially but across a generation/scale coordinate.

Current executable `LGRC9V3`:

```text
one global deterministic queue
    ordered by T_e
```

Possible hierarchical LGRC:

```text
root identity queue
    basin/module queue A
        node/module queue A1
        node/module queue A2
    basin/module queue B
        node/module queue B1
        node/module queue B2
```

The runtime would still need an operational processing order:

```text
kappa:
    deterministic execution ordinal
```

But causal synchronization would be distributed through parent/child frontier
contracts rather than imposed by one global event-time key.

Each hierarchy scope could own a local frontier:

```text
Q_H:
    local queue for hierarchy scope H

tau_H or frontier_H:
    scope-local proper-time / causal frontier

tau_i:
    node-local proper time
```

Cross-scope influence would be mediated by boundary events:

```text
child -> parent:
    outgoing packet / scale-flux / boundary signal

parent -> child:
    synchronization grant / inherited influence / routed packet

parent -> sibling via parent:
    boundary-mediated transfer
```

This maps naturally to the fractal RC distinction:

```text
J^i:
    spatial flux within a scale or scope

J^sigma:
    scale-flux between hierarchy levels

multiscale identity basin:
    stable queue/frontier structure spanning parent and children
```

The conceptual shift is:

```text
global queue:
    synchronizes by one scalar event-time key

hierarchical queues:
    synchronize by parent/child frontier contracts
```

Local proper-time drift would become stronger and more semantically central.
A child identity could process many internal events while another child remains
quiet, until parent-level boundary exchange makes the scopes interact.

The key invariant would not be "all scopes share time." It would be:

```text
No boundary transfer is applied unless the parent/child frontier contract says
the receiving scope is causally eligible.
```

Budget conservation would also become hierarchical:

```text
coherence inside scope H
+ coherence inside children of H
+ in-flight packets crossing H boundaries
= conserved for H,
  except for explicitly recorded parent-mediated exchange
```

This would preserve the mechanism discipline of LGRC while replacing the
single global lock with distributed synchronization.

Required future design work:

```text
hierarchical frontier advancement;
cross-queue packet routing;
parent/child budget ledgers;
scale-flux event representation;
fairness between queues;
deadlock/starvation prevention;
checkpoint surfaces across unsynchronized queues;
replay determinism;
visualizing nested causal fronts.
```

This is not a current implementation target. It is recorded as a future LGRC
or fractal-LGRC design surface if the global `T_e` scaffold becomes limiting.

## Current Decision

Do not change the current executable `LGRC9V3` design now.

Record the local-queue/no-`T_e` and hierarchical-queue designs as future LGRC
surfaces if the current event-time scaffold creates conceptual or experimental
tension.

The current design remains valid as a disciplined executable bridge:

```text
T_e orders events for deterministic packet scheduling and replay.
tau_i records node-local proper time.
lapse_policy determines how much proper time a node accumulates when touched.
```
