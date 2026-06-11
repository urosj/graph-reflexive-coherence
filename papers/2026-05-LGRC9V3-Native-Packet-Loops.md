# Native Packet-Loop Semantics in LGRC9V3

## From N03 Polarized Basin Loops to D2.3-Equivalent Runtime Semantics

Copyright © 2026 Uroš Jovanovič, CC BY-SA 4.0.

## Abstract

This paper records a validated implementation specialization of Lorentzian
Graph Reflexive Coherence: native self-rearming packet loops in LGRC9V3.

The result was reached through the N03 polarized-basin-loop experiment. The
first tested surface, native fixed-topology GRC9V3 proposal flux, did not
produce polarized loops on the tested fixtures. A packetized causal-history
mechanism then produced a positive result as an experiment-local prototype:
scheduled packet loops, measured state-triggered packet departure, and
self-rearming packetized pulse cycles. E1 showed that this mechanism was
LGRC-compatible as a causal event ledger. E2 showed that existing LGRC9V3
could execute packet routes, but still required an adapter for D2.3-style
surplus triggers and self-rearm evidence. The Phase 8 native packet-loop
continuation then promoted the missing pieces into LGRC9V3 runtime surfaces.
E3 reproduced the D2.3 mechanism using native LGRC9V3 only.

The resulting classification is:

```text
native_d2_3_equivalent_packet_loop_supported
adapter_required_for_d2_3_semantics = false
native_static_route_only = false
```

The supported claim is narrow: native LGRC9V3 packetized causal execution
reproduces a conserved self-rearming polarized packet loop under controls. It
is not a native GRC9V3 proposal-flux loop claim, not a movement claim, not an
agency claim, and not a biological claim.

## 1. Scope

This paper is not the foundational LGRC definition. The base LGRC paper
defines causal histories, local proper time, edge delay, event queues, and the
packet conservation invariant:

$$
B
=
\sum_i C_i
+
\sum_{p\in P_{\mathrm{flight}}} C_p .
$$

This paper describes one concrete LGRC9V3 realization of that packetized
causal flux surface. It adds runtime semantics for:

```text
route-aspects
pole masks
ordered channel routes
measured surplus triggers
self-rearm evidence
artifact-only validation
```

These are implementation-level specialization mechanisms. They are not minimal
axioms of LGRC, and they should not be read as saying that every LGRC runtime
must contain four-pole routes or surplus-triggered self-rearming loops.

This paper is therefore an implementation-specialization paper. The LGRC paper
defines the causal-history substrate; this paper records one validated native
LGRC9V3 mechanism built on that substrate. The mechanism remains RC-compatible
because coherence is never created or destroyed: packet coherence is counted
either on nodes or in flight, and every departure/arrival is budget-audited.

## 2. Background

The N03 polarized-basin-loop experiment asks whether an internal source/sink
polarity can sustain a conserved recurrent loop:

```text
source-aspect exports coherence
-> channel carries coherence
-> sink-aspect imports coherence
-> return channel refills the source-aspect
-> source-aspect exports again
```

The desired loop is closed. It does not introduce external source or sink
terms. Its budget must be reconstructed from tracked coherence surfaces.

The initial synchronous test surface was native fixed-topology GRC9V3 proposal
flux. This was the correct first test because it asks whether existing GRC9V3
continuity dynamics already generate the loop without new causal packet
machinery.

## 3. Negative Synchronous Result

The tested native fixed-topology GRC9V3 proposal-flux surfaces did not produce
polarized basin loops.

The negative chain includes:

```text
plain two-aspect rings
amplitude sweeps
mask-width sweeps
ring-size sweeps
source/sink spacing sweeps
transport-rebuild audits
conductance-corridor diagnostics
delayed accumulator fixtures
leak / threshold / hysteresis / refractory release policies
three-pole accumulator fixtures
circulation and residual-curl audits
rotation fixtures
initial-flux retention tests
alternating source/sink pole rings
```

The best interpretation is:

```text
Native fixed-topology GRC9V3 proposal flux behaves primarily as a conservative
relaxation surface on these fixtures, not as an endogenous phase-organizing
loop generator.
```

The negative synchronous result is not a failure of conservation. It shows
that recomputed proposal flux is not the same as persistent in-flight
coherence. LGRC packet transport supplies the missing causal-handoff state.

This is a negative result about a named execution surface, not a falsification
of the packet-loop mechanism.

## 4. D2.3 Packetized Prototype

The experiment then isolated the missing mechanism: causal handoff.

The packetized prototype represents coherence in flight explicitly:

```text
node coherence -> packet departure -> in-flight coherence -> packet arrival
```

with the conserved budget:

$$
B
=
\sum_i C_i
+
\sum_p C_p .
$$

The D2 branch established three steps:

| Branch | Result |
|---|---|
| D2 | Scheduled conserved packet loops pass controls. |
| D2.1 | Robustness and conservation audits pass. |
| D2.2 | Measured state-triggered packet departure passes controls. |
| D2.3 | Returned packet coherence re-creates source surplus and triggers later departures. |

D2.3 is the key mechanism:

```text
packet returns to source pole
-> source-pole surplus crosses threshold
-> next packet departure is scheduled
-> loop re-arms without a hand-authored seed schedule
```

At this stage the result was still experiment-local packetized prototype
evidence, not native LGRC9V3 evidence.

## 5. E1/E2 Alignment

E1 translated D2.3 into an LGRC-style event ledger. The result was:

```text
lgrc_style_event_ledger = validated_from_ledger_only
lgrc9v3_compatibility = adapter_compatible
native_lgrc9v3_execution = false
```

E2 then ran the mechanism closer to LGRC9V3:

```text
native_packet_execution_compatible
adapter_triggered_runtime_compatible
native_static_route_autonomy_available
missing_native_surplus_trigger_primitive
```

E2 showed that native LGRC9V3 already had packet execution and static route
autonomy, but did not yet have the D2.3-specific semantics:

```text
pole/channel route semantics
measured source-pole surplus trigger
self_rearm evidence label
```

Static route autonomy can move packets around a declared closed route, but it
does not by itself prove state-triggered self-rearm. D2.3 equivalence requires
the returned packet to alter runtime pole mass, the producer to observe the
post-arrival surplus, and the child departure to be scheduled from that
evidence.

Those missing pieces became the Phase 8 native packet-loop implementation
target.

## 6. Native LGRC9V3 Mechanism

The native LGRC9V3 packet-loop mechanism has three runtime surfaces.

The native invariant is the same node-plus-packet budget:

$$
B(t)
=
\sum_i C_i(t)
+
\sum_{p\in P_{\mathrm{flight}}(t)} C_p(t) .
$$

Producer records do not change this quantity; only packet departure and
arrival events do.

### 6.1 Route-Aspects

A route-aspect serializes the semantic route that a packet loop claims to
follow:

```text
route_aspect_id
direction
pole_regions
channel_sequence
channels
route_hops
expected_next_channel
route_aspect_digest
pole_region_digest
channel_sequence_digest
```

Pole regions are node masks. Channels are ordered node/edge routes between
poles. The digest fields make replay identity explicit: changing pole masks,
channel order, route direction, or route hops changes the replay identity.

### 6.2 Surplus Trigger Producer

The surplus trigger is a policy-gated producer and is disabled by default.
Enabling native packet-loop behavior is therefore an explicit runtime choice,
not a change to all LGRC9V3 execution. When enabled, it observes runtime node
coherence and schedules a packet departure when:

$$
\mathrm{pole\_mass}(R_m)
-
\mathrm{reference\_mass}(R_m)
\ge
\theta_{\mathrm{trigger}} .
$$

The producer records:

```text
producer_policy
route_aspect_digest
source_pole_id
eligible_channel_id
observed_mass
reference_mass
surplus
trigger_threshold
scheduled_packet_id
reason_code
event_time_key
```

The producer does not debit coherence. It only schedules work. Packet budget
mutation still begins when `LGRC9V3.step()` processes the queued packet
departure.

### 6.3 Self-Rearm Evidence

Native self-rearm evidence is emitted only for the auditable chain:

```text
step() processes parent packet arrival
-> arrival mutates target/source pole coherence
-> producer runs after that committed arrival
-> producer observes surplus above threshold
-> producer schedules child packet departure
-> step() processes child departure
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
event_time_key
scheduler_event_index
node_proper_time evidence
per-transition budget evidence
```

Pre-arrival triggers, wrong-route children, scheduled-but-unprocessed children,
missing parent arrivals, and route digest mismatches do not support completed
self-rearm evidence.

## 7. Producer/Step Boundary

The implementation preserves the LGRC runtime boundary:

```text
produce_events(...):
    inspect runtime state and enqueue eligible causal work

step():
    consume exactly one queued event and mutate runtime state

run_autonomous(...):
    bounded producer + step loop
```

This boundary prevents a producer from becoming a hidden mutator. It also makes
event ordering reviewable: every positive chain must pass through serialized
packet departure and arrival events.

Duplicate trigger suppression is deterministic. Repeated producer calls in the
same eligibility window do not schedule duplicate children.
This prevents a single surplus crossing from emitting multiple child packets
during the same eligibility window. It is replay hygiene, not a biological
refractory claim.

## 8. Controls

The native D2.3-equivalent control matrix preserves the original packet-loop
claim discipline.

| Control | Expected blocker |
|---|---|
| `no_surplus` | no surplus gate crossing |
| `subthreshold` | threshold gate failed |
| `threshold_too_high` | threshold gate failed |
| `wrong_direction` | route direction gate failed |
| `forward_only` | return chain missing |
| `broken_return` | closed-loop route validation failed |
| `scrambled_order` | route order / pole-contiguity validation failed |

Packet activity alone is not enough. A control may schedule or process packets
and still remain negative if it cannot complete the required route-ordered
self-rearm chain.

## 9. Native E3 Result

In this paper, E3 denotes the Phase 8 native LGRC9V3 reproduction of the D2.3
mechanism: the first run in which route-aspect semantics, surplus-trigger
production, and self-rearm evidence are all native runtime surfaces rather
than experiment-local adapters.

The N03 E3 reproduction uses native LGRC9V3 packet-loop surfaces only. The old
D2/D2.3 prototype runner and the E2 adapter trigger are not execution engines.

The positive routes are:

```text
clockwise:         S1 -> K2 -> S2 -> K1 -> S1
counter-clockwise: S1 -> K1 -> S2 -> K2 -> S1
```

The symbols `S` and `K` in the four-pole route are route-aspect role labels.
They do not denote external sources or sinks, and they do not by themselves
prove measured source/sink behavior. The runtime claim depends on
surplus-trigger evidence, packet events, self-rearm links, and budget audit.

The native result is:

```text
classification = n03_native_lgrc9v3_packet_loop_reproduced
scope_closed = d2_3_native_lgrc_packet_loop_branch
entire_n03_experiment_closed = false
```

Positive rows:

```text
clockwise cycles = 3
counter-clockwise cycles = 3
clockwise completed self-rearms = 12
counter-clockwise completed self-rearms = 12
clockwise trigger count = 12
counter-clockwise trigger count = 12
max event budget error = 0.0
topology changed = false
direction symmetry = passed
```

Claim flags:

```text
native_lgrc9v3_execution = true
native_packet_execution = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = true
adapter_required_for_d2_3_semantics = false
native_static_route_only = false
snapshot_telemetry_replayable = true
```

The classification is accepted because a ledger/artifact-only validator can
reconstruct the positive and negative classifications from native runtime
artifacts.

## 10. Snapshot, Telemetry, And Replay

Native packet-loop evidence survives snapshot and telemetry export.

Snapshots preserve:

```text
route-aspect trigger config
autonomous producer records
self-rearm evidence records
packet departure/arrival records
route-aspect digests
event-time keys
node proper-time evidence
```

Loading a snapshot does not duplicate evidence. Continue-after-load preserves
route order and duplicate-trigger suppression.

Telemetry exports a packet-loop surface with producer policy, route-aspect
digest, completed self-rearm counts, claim flags, and cached producer records.
The artifact-only validator can reproduce self-rearm classifications from
exported runtime artifacts.

## 11. Claim Discipline

Supported:

```text
native LGRC9V3 causal packet-loop support
D2.3-equivalent surplus-triggered self-rearming packet loop
conserved node-plus-packet budget
artifact-validated causal self-rearm evidence
```

Blocked:

```text
native GRC9V3 proposal-flux loop evidence
movement or locomotion
agency, intention, or biological behavior
identity acceptance
broader multi-pole generalization beyond the tested four-pole route
```

The native packet-loop result gives a pulse substrate. It does not by itself
show boundary-coupled movement. Movement remains a separate experiment with a
separate claim ladder.

## 12. Relation To The LGRC Paper

The base LGRC paper should define packetized causal flux generally:

```text
packet departure
packet arrival
event queue
node-plus-packet budget
proper-time/event-time distinction
```

This paper records one successful LGRC9V3 specialization:

```text
route-aspects
surplus triggers
self-rearm evidence
D2.3-equivalent controls
native N03 reproduction
```

This separation preserves the theory/implementation boundary. LGRC supports
causal packet histories. Native packet-loop semantics are one validated
runtime mechanism built on that support.

## 13. Remaining Work

This paper closes the D2.3/native-LGRC packet-loop branch. It does not close
the entire N03 experiment family.

Remaining N03 or downstream branches include:

```text
movement-ladder handoff
boundary-coupled pulse experiments
multi-pole basin loops
larger fixture families
output bundling and artifact cleanup
paper polish against the full implementation record
```

Each should open with its own controls and claim boundary.
