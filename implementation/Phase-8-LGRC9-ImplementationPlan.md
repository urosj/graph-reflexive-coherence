# Phase 8 LGRC-9 Implementation Plan

This document is the execution plan for **Phase 8: `LGRC-9`
Causal-History Substrate**.

It turns the Phase 8 summary in
[`ImplementationPhases.md`](./ImplementationPhases.md) and the LGRC-9 paper in
[`../papers/2026-05-LGRC-9.md`](../papers/2026-05-LGRC-9.md) into an explicit
implementation track.

Required companion document:

- [`Phase-8-LGRC9-ImplementationChecklist.md`](./Phase-8-LGRC9-ImplementationChecklist.md)

Focused continuation document:

- [`Phase-8-LGRC9-NativePacketLoopPlan.md`](./Phase-8-LGRC9-NativePacketLoopPlan.md)

## Purpose

Phase 8 defines the first implementation path for the **LGRC-9** family:
Lorentzian/event-driven nine-port GRC.

The purpose is not to create a general LGRC family framework. The purpose is to
make the minimum causal-history substrate needed by the nine-port family
auditable, reducible to synchronous GRC, and safe to extend.

The first executable implementation target is **LGRC9V3** annotation/timing
evidence, because `GRC9V3` is the current complete nine-port runtime with
basin, spark, Lane A, and Lane B evidence. Pure `LGRC9` remains the substrate
interpretation. It is not the first standalone runtime target.

After the completed LGRC-0/LGRC-1 slice, Phase 8 continues with two explicit
runtime scopes:

```text
LGRC-2:
    packetized causal flux on fixed topology

LGRC-3:
    topology-changing causal history
```

These later scopes are part of Phase 8, but they must be opened through their
own decision records, contracts, tests, and handoffs. They do not retroactively
change the meaning of the completed LGRC-0/LGRC-1 evidence.

Iteration 13 opened LGRC-3 with a contract artifact only. Iterations 14-23
then added the active helper/evidence slice for refinement packet transport,
proper-time inheritance, collapse/reabsorption evidence, collapse packet
transport, proper-time identity evaluation, explicit identity acceptance, replay
validation, and examples. Iteration 24 accepted the runtime-class boundary, and
Iteration 25 introduces the first concrete `LGRC9V3` event-queue shell.
Iteration 26 adds packetized local updates driven by packet-arrival
eligibility. The shell still does not run delayed-evaluation continuity,
causal spark predicates, topology integration, or identity acceptance.

Phase 8 starts from the completed synchronous family stack:

- `GRC9` supplies the ordered nine-port substrate.
- `GRC9V3` supplies the current hybrid nine-port runtime and spark evidence.
- `LGRC-9` adds causal-history interpretation: scheduler events, local proper
  time, edge delays, causal reachability, and event-time ordering.

## Iterations 1-4 Record

The first completed implementation slice is **LGRC-0 derived annotation over
synchronous `GRC9V3`**.

This slice proves compatibility and evidence hygiene:

- the LGRC9V3 timing vocabulary can be serialized without ambiguity;
- causal-history policy names can be validated;
- lapse, edge-delay, and geometric/causal/functional distance helpers can be
  computed from `GRC9V3State`;
- derived proper-time, edge-delay, event-time, cone, and causal basin-core
  evidence can be emitted under an optional `causal_history` artifact block;
- old non-LGRC artifacts remain valid and are read as non-LGRC evidence;
- `GRC9V3` default stepping, `dt`, event counts, topology, budgets,
  observables, and Lane A/Lane B spark semantics are unchanged.

This slice does **not** prove operational LGRC dynamics. It does not replace
`dt`, implement event-queue flux, preserve in-flight packet budget, causally
schedule sparks, or implement proper-time identity persistence.

Safe wording:

```text
LGRC-0 timing and causal-history vocabulary can be attached to synchronous
GRC9V3 artifacts as derived annotation evidence without corrupting the
synchronous runtime.
```

Do not summarize Iterations 1-4 as:

```text
LGRC is operationally validated.
```

## Iteration 5 Record

Iteration 5 adds the first **LGRC-1 fixed-topology semi-causal eligibility**
surface.

This proves only that:

- proper time can be advanced as an opt-in fixed-topology eligibility surface;
- `delta_tau_i = tau_i - tau_i_last_update` can be computed and serialized;
- nodes can be marked eligible/ineligible under `min_delta_tau`;
- nodes without a processed event can still receive virtual proper-time
  advancement at the current event-time frontier;
- the surface rejects topology drift against a prior fixed-topology signature;
- budget evidence remains unchanged because the surface does not move
  coherence;
- artifacts can label the run as semi-causal with no causal availability
  buffers and no packetized flux.

This still does **not** prove full operational LGRC dynamics. Iteration 5 does
not replace `dt`, does not run packet/event-queue flux, does not causally
schedule GRC9V3 sparks, and does not implement topology-changing causal
history.

## Iteration 6 Record

Iteration 6 verifies the documented synchronous-limit and no-regression
boundary.

The synchronous-limit fixture uses:

```text
lapse_policy = "unit"
edge_delay_policy = "constant_delay"
event_time_policy = "synchronous_limit"
```

with an explicit `event_time_scale` mapping from synchronous `step_index` to
compatibility event-time evidence.

This proves:

- LGRC-0 annotation can expose unit proper-time labels and constant edge-delay
  labels without mutating the synchronous state;
- LGRC-1 fixed-topology eligibility can mark nodes eligible under
  `delta_tau_i` in the synchronous-limit surface;
- no in-flight packets or pending-flux ledger are retained or claimed;
- default `GRC9` and `GRC9V3` do not claim the causal layer;
- Lane A/Lane B `GRC9V3` spark evidence remains unchanged when LGRC helpers are
  external and causal modes are disabled.

This remains a compatibility/no-regression proof, not proof of operational
event-driven LGRC dynamics.

## Inputs

Authoritative semantic input:

- [`../papers/2026-05-LGRC-9.md`](../papers/2026-05-LGRC-9.md)

Reference family inputs:

- [`../papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md)
- [`../papers/2026-02-GRC-V3.md`](../papers/2026-02-GRC-V3.md)
- [`../specs/lgrc-9-v3-spec.md`](../specs/lgrc-9-v3-spec.md)
- [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)
- [`../specs/grc-9-v3-spec.md`](../specs/grc-9-v3-spec.md)
- [`Phase-6-ImplementationPlan.md`](./Phase-6-ImplementationPlan.md)
- [`Phase-6-Closeout.md`](./Phase-6-Closeout.md)
- [`Phase-7-ImplementationPlan.md`](./Phase-7-ImplementationPlan.md)
- [`Phase-7-Closeout.md`](./Phase-7-Closeout.md)
- [`GRC9V3-CanonicalColumnH-ImplementationPlan.md`](./GRC9V3-CanonicalColumnH-ImplementationPlan.md)

## Scope Boundary

Phase 8 is the **LGRC-9 family phase**.

Naming convention:

```text
LGRC-9:
    paper / family phase label

LGRC9:
    executable/runtime family name for the pure nine-port Lorentzian target

LGRC-V3:
    paper / family phase label for a possible V3 Lorentzian target

LGRCV3:
    executable/runtime family name for that possible target

LGRC9V3:
    executable/runtime family name for the hybrid nine-port V3 target
```

Its first executable target is `LGRC9V3`: causal-history annotation and timing
surfaces over the existing `GRC9V3` runtime. Pure `LGRC9` remains the substrate
interpretation used to keep the nine-port mechanics honest.

Phase 8 does not implement a separate general `LGRC` family, a separate
`LGRC-V3` family phase / executable `LGRCV3` runtime, or a broad multi-family
Lorentzian architecture. Those families may be derived later if there is enough
implementation tension to justify them.

Phase 8 also does not rename or reorganize `GRCL`/`LGRC` terminology. The names
are close, but the current task is causal-history implementation planning, not
vocabulary cleanup.

## In Scope

- Timing schema for:
  - scheduler event index `kappa`,
  - checkpoint/snapshot index `k`,
  - event-time key `T_e`,
  - node-local proper time `tau_i`,
  - edge causal delay `tau_ij`.
- Initial bounded lapse policy.
- Initial edge-delay policy.
- Preservation of the three distance notions:
  - geometric distance,
  - causal/proper-time distance,
  - functional/coupling distance.
- LGRC-0 causal annotation surfaces over existing `GRC9V3` runtime evidence.
- Pure `GRC9` substrate terms where they are needed to interpret LGRC-9 timing
  and port geometry.
- LGRC-1 fixed-topology local proper-time eligibility.
- LGRC-2 packetized causal flux on fixed topology.
- LGRC-3 topology-changing causal history.
- Reduction/no-regression tests against synchronous GRC behavior.
- Clear artifact wording that distinguishes annotation, semi-causal behavior,
  packetized causal propagation, and topology-changing causal history.

## Out Of Scope For Completed LGRC-0/LGRC-1 Slice

- default behavior changes for `GRC9` or `GRC9V3`;
- general LGRC runtime families;
- `LGRC-V3` family phase or executable `LGRCV3` runtime;
- algebraic Lorentzian metric tensor or signed interval form;
- in-flight packet redirection through mechanical expansion;
- causal collapse/reabsorption implementation;
- identity acceptance changes;
- broad landscape-general LGRC validation;
- application/IDE host integration work.

The packetized and topology-changing items are no longer outside Phase 8 as a
whole. They remain outside the completed LGRC-0/LGRC-1 slice until opened by
the LGRC-2 and LGRC-3 continuation records below.

## Phase 8 Continuation And Gate Map

The following surfaces record planned continuations, closed gates, and future
surfaces outside the first `LGRC9V3` annotation slice. Completed gates should
not be reopened silently; later work should consume their contracts or open an
explicit revision.

| Surface | Status Or Continue From | First Question To Resolve |
|---|---|---|
| Standalone `LGRC9` runtime | LGRC-0 annotation fields over pure `GRC9` substrate evidence | Does pure nine-port causal history need behavior beyond `GRC9V3`-backed annotation? |
| `LGRC-V3` / executable `LGRCV3` | `GRCV3` basin semantics plus the timing schema in this plan | Does non-nine-port V3 need its own causal-history substrate, or can it inherit a later common LGRC layer? |
| General LGRC family layer | stable `LGRC9V3` and at least one other executable Lorentzian family | Is there enough repeated structure to justify a shared base abstraction? |
| LGRC-2 packetized causal flux | `LGRC9V3` timing fields, edge delay policy, and budget audit hooks | What packet/ledger representation preserves `B = sum_i C_i + sum_p C_p` exactly? |
| Pending-flux ledger compaction | Complete in Iteration 12 | Canonical packets stay per-packet; compact pending-flux entries are derived from in-flight packets by directed channel, arrival key, and source/target lineage. |
| Native causal pulse-substrate surface | Closed in [`Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md) | LGRC9V3 now supports a default-off native surface over committed packet events plus policy-gated coupling/feedback producers. Movement, native M6, identity, agency, and topology-lineage claims remain blocked unless separately validated. |
| Native causal pulse-substrate surface lineage transport | Closed in [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md) | LGRC9V3 now supports default-off LGRC-3 surface-row supersession/transport through committed topology events, artifact-only lineage replay, and producer stale-read prevention. Adaptive-topology movement and choice/agency claims remain blocked until N04 Iteration 19-C or later validators pass. |
| Native topology-state reabsorption | Closed in [`Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`](./Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md) | LGRC9V3 now supports default-off LGRC-3 topology-state reabsorption: committed topology events can rebase active node/edge state and packet-ledger accounting together through explicit lineage maps. This makes post-topology packet work runtime-valid, but movement, topology-mutating movement, choice, agency, and identity claims remain blocked until N04 reruns and passes the movement ladder. |
| Time-scoped lineage replay | Closed in [`Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md`](./Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md) | Artifact-only surface-lineage replay now validates producer stale-read status at producer scheduler time. Later topology transports no longer invalidate historically valid earlier producer reads; stale reads at/after transport remain blocked. |
| Native route arbitration | Closed in [`Phase-8-LGRC9-NativeRouteArbitrationCloseout.md`](./Phase-8-LGRC9-NativeRouteArbitrationCloseout.md) | LGRC9V3 now supports default-off LGRC-3 native route arbitration: runtime-visible evidence emits candidate route sets, serialized policy selects one route, the selected topology event references the arbitration record, and artifact-only replay reconstructs the selected-route chain through surface lineage, topology-state reabsorption, producer scheduling, and step processing. Native choice, semantic choice, agency, RC identity collapse, identity acceptance, locomotion-like behavior, biological behavior, and unrestricted movement claims remain blocked until N04 reruns and separately validates them. |
| LGRC-3 topology-changing causal history | existing GRC9V3 mechanical expansion events plus LGRC-2 packets | How are in-flight packets transported through refinement lineage maps? |
| Proper-time identity acceptance | GRC9V3 identity/basin persistence evidence plus LGRC causal clocks | Which clock defines the identity window: sink-local, lineage, basin aggregate, or causal frontier? |
| Causal collapse/reabsorption | GRCV3/GRC9V3 collapse events plus LGRC causal lineage | How are budget, lineage, and proper-time transfer recorded at collapse? |
| Post-32 LGRC9V3 baseline freeze | Iterations 24-32 plus Iteration 31-A stress sweep and corrected cascade comparison | Which exact behavior, imports, examples, event counts, and assumptions must remain stable before design cleanup? |
| LGRC9V3 design cleanup | frozen post-32 baseline and observed design tension in `docs/status/LGRC9V3-Implementation-State-And-Design-Tension.md` | How can module ownership improve without changing semantics or breaking legacy imports? |
| LGRC9V3 runtime facades | frozen post-32 baseline plus landscape-loading friction | Which library-owned helpers should replace example-owned queue seeding and source-to-runtime wiring? |
| LGRC9V3 native snapshot restore | existing `snapshot()` output and deferred `load()` | What runtime-state fields must round-trip before ignored artifacts stop requiring reconstruction paths? |
| LGRC9V3 autonomous event production | post-37 deterministic executor plus construction-time queue seeding helpers | Which state-derived producer policies can schedule causal work without making `step()` opaque? |
| Directed delay | symmetric edge-delay baseline and flux orientation convention | What sign convention and clipping policy make directionality stable? |
| Algebraic Lorentzian metric | operational causal-distance surfaces | Is a signed interval/tensor useful, or does it create geometry without runtime tension? |
| Landscape-general validation | LGRC0/LGRC1 fixtures and clean Lane A/B contrasts | Which held-out landscapes show stable causal-history behavior? |

None of these continuation surfaces should alter the meaning of completed
Phase 8 results. They should be opened as explicit implementation tasks,
separate lanes, or later phase revisions.

## Implementation Levels

### LGRC-0. Causal Annotation

LGRC-0 is the first implementation level. Its first concrete target is
`LGRC9V3` annotation/timing evidence.

It computes causal-history annotations from existing synchronous runtime state
and event evidence. It must not change model behavior, event counts, topology,
budget evolution, or existing snapshot semantics.

LGRC-0 may expose:

- `kappa`/`T_e` annotations for observed events;
- derived `tau_i` values under a documented lapse policy;
- derived `tau_ij` values under a documented edge-delay policy;
- causal/proper-time path distances;
- causal cone overlays;
- causal basin-core diagnostics as derived evidence only.

### LGRC-1. Fixed-Topology Semi-Causal Eligibility

LGRC-1 is the first possible behavior-changing target.

It may allow local updates or diagnostics to be scheduled by node-local
proper-time eligibility on a fixed topology. Unless causal availability buffers
exist, LGRC-1 must be labeled **semi-causal**.

LGRC-1 must not claim packetized conservation, topology-changing causal
lineage, or causal identity persistence unless those mechanisms are implemented
explicitly.

### LGRC-2. Packetized Causal Flux

LGRC-2 introduces event queues and packetized in-flight coherence accounting on
fixed topology.

It is the first level allowed to claim packetized causal propagation. The
conserved budget must include in-flight packets:

```text
B = sum_i C_i + sum_p C_p
```

LGRC-2 must define:

- deterministic event queue keys and tie-breaking;
- packet departure and arrival event payloads;
- packet ledger or pending-flux representation;
- packet budget before/after/error fields;
- replay and JSON round-trip semantics;
- how packet arrivals expose local update or spark-diagnostic eligibility;
- synchronous-limit behavior with no in-flight retention.

Iteration 8 fixes the initial contract names:

```text
causal_layer_mode = "packetized_fixed_topology"
lgrc_runtime_level = "lgrc2"
artifact_kind = "lgrc9v3_packet_contract"
artifact_schema_version = "lgrc9v3_packet_contract_v1"
mode_version = "lgrc2_packetized_fixed_topology_v1"
event_queue_tie_break_policy =
    "event_time_key_then_scheduler_event_index_then_event_id"
```

Packet events are named:

```text
lgrc9v3_packet_departure
lgrc9v3_packet_arrival
```

Iteration 9 adds passive packet, queue-event, and ledger artifacts:

```text
LGRC9V3PacketRecord
LGRC9V3PacketQueueEventRecord
LGRC9V3PacketLedger
artifact_kind = "lgrc9v3_packet_ledger"
artifact_schema_version = "lgrc9v3_packet_ledger_v1"
```

These artifacts serialize packet state and queue ordering without mutating
`GRC9V3State` or processing departure/arrival transitions.

Iteration 10 adds active fixed-topology packet processing:

```text
derive_lgrc9v3_packet_arrival_event_time_key(...)
process_lgrc9v3_packet_departure(...)
process_lgrc9v3_packet_arrival(...)
process_lgrc9v3_next_packet_event(...)
schedule_lgrc9v3_packet_departure(...)
derive_lgrc9v3_packet_arrival_eligibility(...)
artifact_kind = "lgrc9v3_packet_processing_result"
artifact_schema_version = "lgrc9v3_packet_processing_result_v1"
```

Departure debits the source node and adds the same amount to in-flight packet
evidence. Arrival removes that in-flight amount and credits the target node.
Both transitions audit:

```text
budget_before
budget_after
budget_error
```

under:

```text
B = sum_i C_i + sum_p C_p
```

Packet processing mutates node coherence and packet lifecycle evidence only.
It does not mutate topology, causally schedule sparks, apply mechanical
expansion, accept identity, collapse basins, or transport packets through
topology changes.

The `scheduled` packet state is implemented by queuing a departure event before
source coherence is debited. Processing the queued departure transitions the
packet to `in_flight` and queues the matching arrival.

The normal LGRC-2 packet path derives arrival event-time keys from the captured
edge-delay surface:

```text
arrival_event_time_key =
    departure_event_time_key + edge_causal_delay[edge_id]
```

This is a `T_e` queue-ordering key, not the source or target node's local
proper time. Explicit caller-provided arrival keys remain valid for replay and
fixture construction, but the delay-derived helper is the normal causal path.

Packet arrival can produce local-update / spark-diagnostic eligibility
evidence, but that evidence is not itself a spark event. It only identifies the
arrival target as eligible for a later local update or diagnostic predicate.

LGRC-2 remains fixed-topology unless LGRC-3 is explicitly enabled. It must not
redirect packets through refinement, claim proper-time identity acceptance, or
represent collapse/reabsorption.

### LGRC-2 Ledger Compaction Gate

Iteration 12 closes the LGRC-2 ledger compaction gate.

The decision is:

```text
canonical LGRC-2 packet ledger:
    remains per-packet

compact pending-flux ledger:
    derived budget-equivalent artifact over in-flight packets
```

Compact entries aggregate only by exact:

```text
source_node_id
target_node_id
edge_id
arrival_event_time_key
source_lineage_id
target_lineage_id
```

Each compact entry preserves:

- packet ids;
- departure event-time keys;
- total pending amount;
- source and target lineage ids;
- the exact compaction policy.

The compact ledger must prove:

```text
pending_flux_total == in_flight_packet_total
conserved_budget_total == node_coherence_total + pending_flux_total
```

It is marked as ready for later refinement-transport audit because it retains
the required lineage fields. It does not itself transport packets through
topology changes.

This is a correctness boundary, not just an optimization. LGRC-3 cannot safely
redirect in-flight coherence through topology changes if the packet ledger has
already discarded the lineage needed for audit.

### LGRC-3. Topology-Changing Causal History

Iteration 13 defines the LGRC-3 topology contract. Later LGRC-3 iterations
extend LGRC-2 packetized causal flux across topology-changing events.

The Iteration 13 contract covers:

- mechanical expansion / refinement lineage fields;
- packet redirection field requirements for refinement maps;
- proper-time inheritance fields for newly created nodes and internal edges;
- first-round uniform parent proper-time inheritance policy;
- explicit out-of-scope status for causal collapse/reabsorption;
- explicit out-of-scope status for proper-time identity persistence.

The contract artifact is:

```text
artifact_kind = "lgrc9v3_topology_contract"
artifact_schema_version = "lgrc9v3_topology_contract_v1"
mode_version = "lgrc3_topology_contract_v1"
evidence_class = "topology_contract"
contract_only = true
topology_change_processing_implemented = false
packet_transport_through_topology_change_implemented = false
```

In-scope topology event kinds:

```text
lgrc9v3_refinement_topology_event
lgrc9v3_refinement_packet_transport
lgrc9v3_proper_time_inheritance
lgrc9v3_causal_boundary_birth
```

Out-of-scope event kinds for this slice:

```text
lgrc9v3_causal_collapse
lgrc9v3_causal_reabsorption
lgrc9v3_proper_time_identity_acceptance
```

Iteration 14 implements the first LGRC-3 transport helper:

```text
transport_lgrc9v3_packets_through_refinement(...)
artifact_kind = "lgrc9v3_refinement_packet_transport_result"
artifact_schema_version = "lgrc9v3_refinement_packet_transport_result_v1"
evidence_class = "refinement_packet_transport"
```

The helper consumes:

```text
pre-expansion LGRC-2 packet ledger
GRC9V3 hybrid_mechanical_expansion event
post-expansion topology signature
optional compact pending-flux ledger
```

For every in-flight packet, it emits a packet transport record. Packets whose
source or target was the expanded node are mapped through the expansion
`reassignment_map`; unaffected packets remain unchanged but are still included
in deterministic transport evidence. Boundary rows preserve:

```text
old_parent_port
new_endpoint_port
old_parent_column
new_endpoint_column
```

Packet ids and amounts are preserved. Future queued arrival events are updated
to point at the transported packet endpoint. Past packet event records remain
historical evidence.

Transport preserves:

```text
B = sum_i C_i + sum_p C_p
```

and records:

```text
identity_acceptance_emitted = false
packet_transport_identity_transfer = false
```

LGRC-3 must keep these distinctions explicit:

```text
candidate event != mechanical expansion != identity acceptance
packet transport != semantic identity transfer
refinement lineage != proof of persistent child identity
```

Iteration 15 adds a default-disabled LGRC-3 policy contract for future
collapse/reabsorption and proper-time identity work:

```text
build_lgrc9v3_lgrc3_policy_contract_artifact(...)
artifact_kind = "lgrc9v3_collapse_identity_policy_contract"
artifact_schema_version = "lgrc9v3_collapse_identity_policy_contract_v1"
evidence_class = "collapse_identity_policy_contract"
contract_only = true
```

This policy contract defines future payload fields and first-round policy
choices. It does not execute collapse, reabsorption, or identity acceptance.

Collapse/reabsorption payloads must preserve:

```text
causal timing fields
competing/selected/losing sink ids
lineage_transfer_map
transferred node / packet / pending-flux ids
coherence_transfer_amount
budget_before / budget_after / budget_error
budget_transfer_policy
lineage_transfer_policy
proper_time_transfer_policy
identity_acceptance_emitted
```

The first-round transfer policies are:

```text
budget_transfer_policy = "budget_conserving_transfer"
lineage_transfer_policy = "explicit_lineage_transfer_map"
proper_time_transfer_policy = "selected_sink_clock_continuity"
```

Proper-time identity payloads must preserve:

```text
source_topology_event_ids
sink_node_id
lineage_id
basin_node_ids
identity_clock_policy
threshold_calibration_policy
proper_time_persistence_threshold
threshold_multiplier
window_start_event_time_key
window_end_event_time_key
observed_persistence_duration
budget_before / budget_after / budget_error
identity_acceptance_allowed
identity_acceptance_emitted
```

The first-round identity policy is:

```text
identity_clock_policy = "sink_local_proper_time"
threshold_calibration_policy = "local_median_delay_multiplier"
threshold_multiplier = 4.0
```

The default contract keeps:

```text
collapse_reabsorption_allowed = false
identity_acceptance_allowed = false
collapse_reabsorption_processing_implemented = false
proper_time_identity_processing_implemented = false
mechanical_expansion_is_identity_acceptance = false
refinement_packet_transport_is_identity_transfer = false
```

Topology-changing causal history must preserve both budget accounting and
lineage evidence. No LGRC-3 result may reinterpret completed LGRC-0/LGRC-1 or
fixed-topology LGRC-2 results.

### Active LGRC-3 Helper/Evidence Iterations

Iteration 15 closed the policy contract, not the runtime implementation. The
following surfaces are now completed active LGRC-3 helper/evidence iterations:

```text
Iteration 17: proper_time_inheritance_processor
Iteration 18: collapse_reabsorption_processor
Iteration 19: collapse_reabsorption_packet_transport
Iteration 20: proper_time_identity_persistence_evaluator
Iteration 21: identity_acceptance_event_emitter
Iteration 22: lgrc3_topology_event_replay_validator
Iteration 23: active_lgrc3_examples_and_handoff
```

The proper-time inheritance processor should consume a mechanical expansion
event and the parent proper-time surface, then emit
`lgrc9v3_proper_time_inheritance` evidence under:

```text
proper_time_inheritance_policy = "uniform_parent_proper_time"
internal_edge_delay_policy = "explicit_or_default_tau0"
```

The active Iteration 17 helper is
`process_lgrc9v3_proper_time_inheritance(...)`. It returns typed evidence and
does not own a full LGRC9V3 event loop.

The collapse/reabsorption processor should consume explicit
sink-selection/collapse evidence parameters plus packet and pending-flux
ledgers, then emit `lgrc9v3_causal_collapse` or
`lgrc9v3_causal_reabsorption` events with:

```text
budget_transfer_policy = "budget_conserving_transfer"
lineage_transfer_policy = "explicit_lineage_transfer_map"
proper_time_transfer_policy = "selected_sink_clock_continuity"
```

The active Iteration 18 helper is
`process_lgrc9v3_collapse_reabsorption(...)`. It requires explicit
`collapse_reabsorption_allowed=True`, records impacted packet/pending-flux ids,
and leaves packet transport through the collapse lineage map to Iteration 19.
It does not yet require callers to wrap causal basin/collapse evidence in a
single artifact object. A replay/runtime adapter can later assemble the helper
parameters from a richer basin-collapse artifact.

The active Iteration 19 helper is
`transport_lgrc9v3_packets_through_collapse_reabsorption(...)`. It redirects
affected in-flight packet endpoints through the explicit lineage map, preserves
packet ids for packets that remain in flight, settles selected-sink self-loop
packets into the returned packet ledger, and preserves historical packet event
records.

The proper-time identity evaluator should consume topology/lineage events,
basin membership evidence, and proper-time surfaces, then evaluate:

```text
identity_clock_policy = "sink_local_proper_time"
threshold_calibration_policy = "local_median_delay_multiplier"
```

The active Iteration 20 helper is
`evaluate_lgrc9v3_proper_time_identity_persistence(...)`. It computes:

```text
proper_time_persistence_threshold =
    threshold_multiplier * local_median_edge_delay

observed_persistence_duration =
    window_end_sink_proper_time - window_start_sink_proper_time
```

It returns typed pass/fail evidence under
`LGRC9V3ProperTimeIdentityPersistenceEvaluation`. It does not emit identity
acceptance, does not mutate state, and does not mutate topology.

The identity event emitter must remain separate from the evaluator and may
emit `lgrc9v3_proper_time_identity_acceptance` only after the evaluator passes
and the policy explicitly enables identity acceptance.

The active Iteration 21 helper is
`emit_lgrc9v3_proper_time_identity_acceptance(...)`. It returns exactly one
`GRCEvent` after a passing evaluator result and explicit
`identity_acceptance_allowed=True`. The event payload links to the evaluator,
source topology ids, basin evidence id, and lineage id, records budget
before/after/error, and keeps mechanical expansion and packet transport
separate from identity acceptance.

The active Iteration 22 helper is
`validate_lgrc9v3_topology_event_replay(...)`. It consumes an ordered replay
sequence of LGRC-3 artifacts/events, normalizes them into
`LGRC9V3TopologyReplayRecord` rows, and returns
`LGRC9V3TopologyReplayValidationResult` evidence. It validates event-time
ordering, source-topology and identity-evaluation references, required lineage
ids, and cross-record budget continuity. It is an audit/replay validator, not
an event scheduler or standalone `LGRC9V3.step()` loop.

Iteration 23 adds `examples/lgrc9v3/active_lgrc3_causal_history.py` and updates
the handoff/reference docs. The example composes the current active LGRC-3
helper chain around a known GRC9V3 Lane B mechanical expansion while preserving
the boundary that, at that stage, spark scheduling and the model loop remained
future runtime parity work.

### Executable LGRC9V3 Runtime Parity Iterations

Iterations 17-23 complete more of the LGRC-3 causal-history evidence layer.
They do not, by themselves, make LGRC9V3 an executable event-driven runtime on
par with synchronous `GRC9V3`. The accepted runtime-parity path is:

```text
Iteration 24: lgrc9v3_runtime_class_decision
Iteration 25: event_queue_orchestration_loop
    status: complete
    adds concrete LGRC9V3 queue shell over composed runtime state
Iteration 26: causal_flux_and_local_update_loop
    status: complete
    consumes arrival eligibility, advances local proper time, and schedules
    explicit packetized causal-flux routes without delayed-evaluation updates
Iteration 27: causally_scheduled_lane_a_lane_b_spark_diagnostics
    status: complete
    evaluates existing GRC9V3 Lane A/Lane B predicates at arrival/local-update
    boundaries and emits lgrc9v3_causal_spark_candidate evidence without
    mechanical expansion
Iteration 28-A: causal_frontier_boundary_birth
    status: complete
    adds opt-in lgrc9v3_causal_boundary_birth events using the GRC9V3
    outward-flux probability law, parent-debit coherence transfer,
    parent proper-time inheritance, and explicit/tau_0 edge-delay assignment
Iteration 28: active_topology_integration
    status: complete
    routes scheduled boundary-birth trials through step(), and routes causal
    spark candidates to mechanical expansion, refinement packet transport,
    and proper-time inheritance when LGRC-3 integration gates are enabled
Iteration 29: lgrc9v3_telemetry_and_checkpoint_parity
    status: complete
    adds LGRC9V3 telemetry family extensions and graph-checkpoint overlays for
    causal clocks, packet ledgers, causal spark diagnostics, topology history,
    collapse/identity events, and old GRC9V3 artifact compatibility
Iteration 30: lgrc9v3_visualization_parity
    status: complete
    renders LGRC9V3 causal event-time/proper-time observables, packet state,
    topology lineage, identity windows, and Lane A/Lane B spark attribution
    from LGRC9V3 telemetry/checkpoint overlays without collapsing distance
    surfaces
Iteration 31: grc9v3_vs_lgrc9v3_comparison_fixtures
    status: complete
    adds controlled comparison fixtures for synchronous-limit timing,
    delay-sensitive packet routing, Lane B refinement/topology integration,
    and proper-time identity persistence; reports align by proper-time
    surfaces and event classes, not raw step counts
Iteration 31-A: runtime_stress_and_determinism_sweep
    status: complete
    adds bounded stress coverage for deterministic packet queue tie-order,
    multi-event budget preservation, mixed packet/boundary-birth/Lane B
    expansion processing, causal-clock monotonicity, runtime snapshot
    round-trip, and default GRC9V3 isolation
Iteration 32: executable_lgrc9v3_examples_and_handoff
    status: complete
    adds runnable executable LGRC9V3 examples, telemetry/visual artifact
    example, reference-guide import updates, and handoff closeout wording
```

### Post-32 Baseline Freeze And Code Design Catch-Up

Iterations 24-32 produced a behaviorally strong executable `LGRC9V3`, but they
also exposed code-design tension:

```text
lgrc_9_v3.py:
    large mixed contract/helper/processor/restore module

LGRC9V3.step():
    deterministic event consumer

missing first-class surfaces:
    deterministic event production / queue priming;
    landscape seed -> LGRC9V3 runtime construction;
    native LGRC9V3.load restore parity;
    library-owned corrected-cascade-style run policy.
```

The next Phase 8 work should therefore be a **baseline-preserving design
catch-up track**, not a semantic rewrite.

Governing rule:

```text
Freeze current behavior before changing code geometry.
```

The current implementation becomes the baseline for the design catch-up track:

```text
LGRC9V3.step() semantics;
packet queue ordering;
boundary-birth trial behavior;
Lane A/Lane B causal spark wrapping;
active topology integration gates;
packet transport and proper-time inheritance evidence;
telemetry/checkpoint family extensions;
visualization interpretation;
corrected cascade reproduction result;
old GRC9/GRC9V3 no-regression behavior;
legacy import path through pygrc.models.lgrc_9_v3.
```

Any refactor iteration must prove that these assumptions remain true.

Accepted post-32 continuation path:

```text
Iteration 33: lgrc9v3_baseline_freeze_and_assumption_audit
    status: complete
    record the exact behavior, imports, examples, fixtures, and comparison
    outputs that define the post-32 baseline before refactor work begins

Iteration 34: deterministic_queue_ownership_patch
    status: complete
    align run_event_queue(max_events=...) with step() so birth-only queues do
    not stop early; add tests and no-regression checks

Iteration 35: behavior_preserving_module_ownership_split
    status: complete
    split lgrc_9_v3.py into contract/timing/packets/topology/identity modules
    under a DAG import rule while keeping lgrc_9_v3.py as a compatibility
    facade

Iteration 36: runtime_construction_and_landscape_facades
    status: complete
    add tested source-to-runtime and queue-priming helpers so examples stop
    owning core orchestration policy

Iteration 37: native_runtime_snapshot_restore_parity
    status: complete
    implement LGRC9V3.load(...) for snapshots emitted by LGRC9V3.snapshot()
```

These iterations are code-design correctness work. They should not introduce
new LGRC semantics. If an iteration discovers that a semantic change is needed,
that semantic change must be split into a separate decision record before code
movement continues.

### Post-37 Autonomy Track

After Iteration 37, `LGRC9V3.step()` is a stable deterministic executor. The
remaining design tension is that event production is still mostly explicit:
examples or construction helpers seed packet departures, route tables, and
boundary-birth trials before the executor has work to consume.

Do not solve this by making `step()` opaque.

Boundary:

```text
step()
    consumes exactly one queued causal work item

produce_events(...)
    inspects current state and schedules eligible causal work

run_autonomous(...)
    bounded loop that calls produce_events(...) when queues need work, then
    calls step()
```

Accepted post-37 autonomy continuation path:

```text
Iteration 38: autonomous_event_production_contract
    status: complete
    define producer policy ids, reason-code schema, generated-event evidence,
    idempotency rules, and the invariant that producers schedule work but do
    not consume queued work

Iteration 39: packet_departure_producer_from_flux_route_policy
    status: complete
    schedule packet departures from explicit causal flux/route policy using
    auditable thresholds and reason codes

Iteration 40: boundary_birth_trial_producer
    status: complete
    schedule causal boundary-birth trials when the existing policy is enabled,
    without changing acceptance/rejection semantics

Iteration 41: bounded_autonomous_run_loop
    status: complete
    add run_autonomous(max_events=..., policy=...) as a bounded producer +
    executor loop over the existing step() contract

Iteration 42: autonomy_examples_and_handoff
    status: complete
    add runnable examples and handoff text showing manual queue execution
    versus autonomous producer-driven execution
```

Autonomy v1 should remain narrow:

```text
packet departure producer:
    allowed

boundary-birth trial producer:
    allowed when policy-enabled

causal spark diagnostics:
    remain tied to arrivals/local updates

collapse/reabsorption and identity acceptance:
    explicit or separately gated

all generated work:
    serializes producer policy, producer version, reason code, thresholds, and
    observed evidence
```

The historical boundary decision for Iteration 24 remains important. Before
Iteration 25, LGRC9V3 was a causal-history/event-evidence layer over
`GRC9V3State`, not a standalone model class with its own `step()` loop.

### Iteration 24 Runtime Class Decision

Iteration 24 accepts the executable-runtime boundary, but it does not implement
the class yet.

Decision:

```text
Introduce a concrete executable `LGRC9V3` model class for Iterations 25+.
```

The class should implement/share the `GRCModel` interface rather than subclass
`GRC9V3`. It should use composition over a `GRC9V3State` substrate so the
event-driven runtime cannot be confused with synchronous `GRC9V3.step()`
semantics.

Planned files:

```text
src/pygrc/models/lgrc_9_v3_runtime.py
    concrete `LGRC9V3` model class

src/pygrc/models/lgrc_9_v3_runtime_state.py
    composed runtime-state bundle, if a separate dataclass is needed

tests/models/test_lgrc_9_v3_runtime.py
    executable-runtime tests for Iterations 25+
```

Existing file roles stay stable:

```text
src/pygrc/models/lgrc_9_v3.py
    helper/evidence contracts, pure functions, packet ledgers, replay records
```

State ownership:

```text
LGRC9V3 runtime state =
    base GRC9V3State
    + causal timing fields
    + packet ledger
    + event queue
    + topology-event/replay ledger
    + causal-history modes/policies
    + diagnostic history needed by causal spark evaluation
```

Migration path:

```text
GRC9V3State -> explicit LGRC9V3.from_state(...) adapter
```

The adapter must initialize causal clocks, packet ledgers, queue state, topology
history, and policy values explicitly. Existing helper APIs remain valid and
must not be silently reinterpreted as model-owned state.

Compatibility expectation:

```text
Old GRC9V3 snapshots remain GRC9V3 snapshots.
LGRC9V3 loading requires an explicit LGRC causal-state block or an explicit
synchronous-limit adapter policy.
```

Iteration 27 is a significant parity gap, not a telemetry port. GRC9V3 already
implements:

```text
Lane A: current_hybrid_signed_hessian
Lane B: grc9v3_column_h_assisted
```

Iteration 27 now evaluates the Lane A/Lane B predicates at arrival/local-update
boundaries and through an explicit diagnostic API. It records the causal
snapshot, resolves previous Column-H values through a causal evaluation index,
and wraps the single captured GRC9V3 candidate payload as
`lgrc9v3_causal_spark_candidate` evidence. Candidate production remains
separate from mechanical expansion and topology integration.

Iteration 28-A covers LGRC9V3's active analogue of GRC9V3 boundary birth. It is
implemented as an explicit API and remains default-off/overridable:

```text
causal_boundary_birth_allowed = false
```

When enabled, the active causal frontier birth policy must map to the
corresponding GRC9V3 boundary-birth probability semantics under
synchronous-limit conditions. LGRC adds causal fields around that behavior:
event-time owner `T_e`, parent/frontier proper-time inheritance, coherence
source, edge-delay assignment, packet visibility after the birth event, budget
evidence, lineage evidence, and topology signatures.

Iteration 28 routes scheduled boundary-birth trials through `LGRC9V3.step()`.
It also keeps candidate-only behavior as the default and requires explicit
LGRC-3 topology-integration gates before causal spark candidates can trigger
mechanical expansion, packet transport, and proper-time inheritance.

Iteration 29 exposes the active LGRC9V3 runtime through telemetry and graph
checkpoints without changing runtime behavior. Event rows use
`family_extensions["lgrc9v3"]` to classify packet, local-update, spark,
topology, collapse, and identity events. Graph checkpoints add causal-clock
overlays, node proper-time surfaces, edge causal delays, packet-ledger state,
causal spark diagnostics, topology history, and a runtime-state artifact.
Existing GRC9V3 telemetry artifacts remain loadable because LGRC9V3 fields are
family extensions, not required shared-schema fields.

Iteration 32 closes the executable runtime-parity arc. It adds no new runtime
semantics. It makes the accepted Iterations 24-31-A runnable and auditable
through examples, reference-guide import paths, and a handoff that states
supported and unsupported claims. This mirrors Iteration 23 for the active
LGRC-3 helper/evidence slice.

Iterations 33-42 then closed the immediate design-correctness and autonomy
surface work: baseline freeze, queue ownership, module ownership split,
runtime construction facades, native snapshot restore, producer contracts,
packet-route producers, boundary-birth producers, bounded autonomous run, and
autonomy examples.

The next Phase 8 continuation is not another broad LGRC runtime rewrite. It is
the N03-driven native packet-loop surface recorded in:

```text
Phase-8-LGRC9-NativePacketLoopPlan.md
Phase-8-LGRC9-NativePacketLoopChecklist.md
```

That continuation targets route-aspect semantics, source-pole surplus trigger
production, and native self-rearm causality evidence for `LGRC9V3`.

A later RCAE P2-I1-driven bounded restoration-contract continuation is now
defined in:

```text
Phase-8-LGRC9-RestorationIdentityPlan.md
Phase-8-LGRC9-RestorationIdentityChecklist.md
```

That continuation adds no causal or dynamical mechanism. It defines a
versioned library-owned distinction between raw snapshot representation and
LGRC9V3 restoration identity, including a read-only embedded-GRC9V3 state
component, so downstream branch/replay experiments do not need to invent
native-state projections.

### Later Levels

Later levels, if any, should be added only after LGRC-2 and LGRC-3 expose
repeated structure or unresolved tension.

## Design Constraints

### 1. Scheduler Order Is Not Proper Time

The scheduler index orders computation. Node-local proper time orders local
causal accumulation. Checkpoint order records observer/replay surfaces.

The runtime must keep these separate:

```text
kappa != k != tau_i != T_e
```

Any artifact that serializes one of these values must name it precisely.

### 2. Operational Lorentzian Scope

Phase 8 uses "Lorentzian" in the operational causal-structure sense:

- local proper time,
- lapse,
- edge causal delay,
- event-time ordering,
- causal cones,
- causal availability.

It does not claim a full algebraic Lorentzian metric tensor.

### 3. No Budget Claim Without Accounting

LGRC-0 annotations do not change budget.

LGRC-1 fixed-topology eligibility may change update order only if budget
preservation remains audited under the selected mode.

Packetized conservation claims belong to LGRC-2, where in-flight coherence is
part of the conserved budget:

```text
B = sum_i C_i + sum_p C_p
```

### 4. Three Distances Must Stay Separate

Phase 8 must preserve the GRC family distinction between:

- geometric proximity,
- causal/proper-time reachability,
- functional/coupling influence.

No path helper or visualization surface should collapse these into one
ambiguous distance.

### 5. Reduction To Synchronous GRC Must Be Testable

Under uniform lapse, constant delay, synchronous eligibility, and no in-flight
retention, the LGRC-9 surfaces must reduce to the existing synchronous GRC
interpretation.

At minimum, Phase 8 must prove that LGRC-0 does not perturb existing
`GRC9`/`GRC9V3` outputs. Any LGRC-1 behavior must include a named synchronous
limit test.

### 6. No Geometry Change Without Tension

Phase 8 follows the same discipline as the GRC theory itself: do not introduce
new runtime geometry or broad restructuring unless an observed implementation
tension requires it.

The first executable target is annotation. Behavior changes come later.

## Workstreams

### Workstream A. Decision Record And Naming

Record that Phase 8 is an LGRC-9 family track whose first executable target is
LGRC9V3 annotation/timing evidence, not a general LGRC program. Preserve the
distinction between LGRC and GRCL without renaming either system in this phase.

### Workstream B. Timing Schema

Define the serialized timing vocabulary:

| Field | Meaning |
|---|---|
| `scheduler_event_index` / `kappa` | event-processing order |
| `checkpoint_index` / `k` | snapshot/replay order |
| `event_time_key` / `T_e` | event-queue ordering key |
| `node_proper_time` / `tau_i` | local accumulated proper time |
| `edge_causal_delay` / `tau_ij` | delay on an edge or directed edge |
| `lapse_policy` | policy used to update proper time |
| `edge_delay_policy` | policy used to compute causal delay |

For model parameters, the causal-history policy values live under:

```text
constitutive_semantic_modes["causal_history"]
```

Artifacts and checkpoints should copy the resolved values into a same-named
`causal_history` evidence block. This keeps the model semantics in core params
while preserving replay evidence without using excluded `runtime`, `observer`,
or `tooling` parameter domains.

### Workstream C. Policy Helpers

Implement or stage pure helpers for:

- bounded density/tension lapse;
- geometry-only edge delay baseline;
- GRC-V3-style flux-dependent edge delay candidate;
- symmetric delay as the default;
- directed delay only as an explicit future option.

Helpers should be deterministic and independently testable.

### Workstream D. LGRC-0 Annotation

Add annotation surfaces that can be computed from existing runtime state or
artifacts without mutating the model.

Outputs should be explicit about being derived/annotation-only.

### Workstream E. LGRC-1 Eligibility

If promoted, add opt-in fixed-topology local proper-time eligibility.

The mode must:

- be disabled by default;
- reject topology-changing claims;
- preserve budget checks;
- serialize that the run is semi-causal unless causal availability buffers
  exist.

### Workstream F. LGRC-2 Packetized Causal Flux

Define and implement fixed-topology packetized causal flux.

The workstream must introduce packet/event-queue semantics before claiming
causal propagation. It must not introduce topology-changing behavior.

Required contracts:

- event queue key and deterministic ordering;
- packet schema and packet lifecycle states;
- departure/arrival event payloads;
- in-flight budget invariant and audit fields;
- packet ledger JSON round-trip;
- relation between arrival events, local eligibility, and spark diagnostics.

### Workstream G. Pending-Flux Ledger Compaction

Define compact pending-flux ledger semantics after basic LGRC-2 packet
accounting is proven and before LGRC-3 topology-changing history begins.
This workstream is complete for the fixed-topology LGRC-2 contract as of
Iteration 12.

Required contracts:

- aggregation keys;
- lineage-retention rules;
- compact ledger JSON schema;
- budget audit equivalence between expanded packets and compact entries;
- expansion/transport readiness for LGRC-3.

### Workstream H. LGRC-3 Topology-Changing Causal History

Define and implement topology-changing causal history after LGRC-2 packet
accounting and pending-flux ledger compaction are stable.

Required contracts:

- refinement lineage map for causal history;
- packet transport through mechanical expansion;
- proper-time inheritance policy;
- collapse/reabsorption event payloads, if enabled;
- proper-time identity window policy, if enabled;
- budget and lineage audit after every topology-changing event.

### Workstream I. Evidence, Replay, And Docs

Update evidence surfaces only enough to make timing annotations auditable.
Downstream telemetry and visualization expansion can happen in later phase
tracks after the core semantics are stable.

## Acceptance Criteria

Phase 8 planning is accepted when:

- this plan and its checklist exist;
- Phase 8 scope is locked to the LGRC-9 family;
- the first executable target is recorded as LGRC9V3 annotation/timing
  evidence;
- LGRC-0, LGRC-1, LGRC-2, and LGRC-3 meanings are distinct;
- LGRC-2/LGRC-3 are explicitly gated as later Phase 8 continuation scopes;
- timing vocabulary is named and serializable;
- default `GRC9`/`GRC9V3` behavior remains unchanged;
- any behavior-changing mode is opt-in and labelled;
- synchronous-limit/no-regression tests are specified before code changes.
