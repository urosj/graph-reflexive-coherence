# LGRC9V3 Specification

Source papers:

- `papers/2026-05-LGRC-9.md`
- `papers/2026-04-GRC-9.md`
- `papers/2026-02-GRC-V3.md`

Source implementation specs:

- `specs/grc-9-v3-spec.md`
- `specs/grc-9-spec.md`
- `specs/grc-v3-spec.md`

## Current Implemented Slices

The current implemented slices are:

```text
LGRC-0:
    derived annotation over synchronous GRC9V3

LGRC-1:
    opt-in fixed-topology semi-causal eligibility evidence

LGRC-2 contract:
    packetized causal-flux schema names and boundary artifact

LGRC-2 ledger surface:
    passive packet records, queue-event records, and fixed-topology ledger
    artifacts

LGRC-2 processing surface:
    fixed-topology packet departure and arrival processing

LGRC-2 pending-flux compaction:
    compact budget-equivalent pending-flux entries derived from in-flight
    packet records

LGRC-3 topology contract:
    topology-changing causal-history event kinds, lineage fields, and boundary
    decisions, without topology-changing processing

LGRC-3 refinement packet transport:
    packet endpoint/lineage transport through one mechanical expansion using
    GRC9V3 reassignment evidence

LGRC-3 collapse/identity policy contract:
    default-disabled payload and policy fields for future collapse,
    reabsorption, and proper-time identity work
```

They support:

- timing field names and causal-history policy validation;
- derived lapse, edge-delay, and three-distance helpers;
- annotation-only proper-time, edge-delay, event-time, cone, and causal
  basin-core evidence;
- optional `causal_history` artifact/replay blocks;
- opt-in fixed-topology proper-time eligibility with `delta_tau_i`;
- stable LGRC-2 packet/event/ledger field names;
- a JSON-round-trippable LGRC-2 packet contract artifact;
- deterministic packet and packet-event ids;
- JSON-round-trippable packet records, queue-event records, and passive ledger
  artifacts;
- fixed-topology packet departure/arrival processing that mutates source/target
  node coherence and packet lifecycle state while preserving
  `sum_i C_i + sum_p C_p`;
- compact pending-flux ledger artifacts that preserve packet totals, directed
  channel, arrival key, source/target lineage, and source packet ids;
- a JSON-round-trippable LGRC-3 topology contract artifact that records
  refinement lineage, packet-transport, and proper-time inheritance fields;
- LGRC-3 refinement packet transport artifacts that preserve packet amount,
  pending-flux lineage, budget evidence, and old/new boundary column evidence;
- a JSON-round-trippable LGRC-3 collapse/identity policy contract that records
  collapse/reabsorption payload fields, budget/lineage transfer fields,
  sink-local identity clock policy, and local-delay threshold calibration;
- virtual proper-time advancement for all live nodes at an event-time frontier;
- a tested synchronous-limit surface using unit lapse, constant delay, and an
  explicit `step_index` to event-time compatibility scale;
- backward-compatible non-LGRC snapshot reads.

They do not implement:

- event-driven LGRC propagation;
- replacement of `dt` as the operational update driver;
- full event-queue-driven LGRC step loop beyond the current packet/local-update
  and causal spark-candidate shell;
- automatic mechanical expansion from causal spark candidates;
- full topology-changing causal-history step loop.

Artifacts produced by the current slices must be read as derived annotation,
fixed-topology semi-causal eligibility, fixed-topology packet-processing
evidence, compact pending-flux evidence, topology-contract evidence, or
single-refinement packet-transport evidence, plus active proper-time
inheritance, collapse/reabsorption, collapse packet-transport, and
proper-time identity persistence-evaluation and acceptance-event evidence.
They are not proof that full LGRC dynamics or a complete topology-changing
causal-history step loop is operational.

Iteration 24 adds a runtime-class decision only: future executable `LGRC9V3`
should be a `GRCModel`-compatible class built by composition over `GRC9V3State`.
It does not yet implement the class.

## Naming

This spec uses the repo naming convention established by the Phase 8 plan:

| Name | Meaning |
|---|---|
| `LGRC-9` | paper / family phase label |
| `LGRC9` | executable/runtime name for a pure nine-port Lorentzian target |
| `LGRC-V3` | paper / family phase label for a possible V3 Lorentzian target |
| `LGRCV3` | executable/runtime name for that possible target |
| `LGRC9V3` | executable/runtime name for the hybrid nine-port V3 Lorentzian target |

This file specifies `LGRC9V3`.

## Purpose

`LGRC9V3` is the Lorentzian/event-driven causal-history interpretation of the
completed `GRC9V3` runtime.

It preserves:

- the `GRC9` nine-port substrate,
- the `GRC9V3` basin / hierarchy / signed-Hessian and Lane B spark semantics,
- mechanical expansion as a separate operation from identity acceptance,
- quadrature-style budget interpretation,

while adding:

- scheduler event order,
- checkpoint / observer-surface order,
- event-time keys,
- node-local proper time,
- edge causal delay,
- causal/proper-time distance,
- causal cone / causal basin-core annotations,
- optional fixed-topology local proper-time eligibility.

`LGRC9V3` is not a general LGRC runtime and not an executable `LGRCV3`
runtime. Those may be derived later if implementation tension requires them.

## Class

Iteration 24 accepts a concrete executable runtime surface, and Iteration 25
implements its first packet event-queue shell:

```python
class LGRC9V3(GRCModel):
    ...
```

The class should implement/share the `GRCModel` interface. It should not
subclass `GRC9V3`, because the synchronous `GRC9V3.step()` loop and the
event-driven LGRC queue loop have different timing semantics. The implementation
should use composition over a `GRC9V3State` substrate.

Planned implementation files:

```text
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
tests/models/test_lgrc_9_v3_runtime.py
```

Annotation-only artifacts remain derived evidence and must not be reported as
behavior-changing runtime evidence.

Iteration 25 `LGRC9V3.step()` guarantees packet event-queue processing:

```text
process the next deterministic packet departure or packet arrival event
```

Iteration 26 adds packetized local updates after packet arrival. On arrival the
runtime may consume arrival eligibility, advance the target node's local
proper-time surface, emit `lgrc9v3_local_update` evidence, and schedule
explicit outbound packet routes.

Iteration 27 adds causally scheduled Lane A/Lane B spark diagnostics at
arrival/local-update boundaries. These diagnostics reuse the existing GRC9V3
predicate core and wrap candidate evidence as:

```text
lgrc9v3_causal_spark_candidate
```

The causal candidate event records trigger kind/id/source, event-time key,
node proper-time evidence, pre-expansion topology signature, spark lane, and
branch attribution. Candidate production remains separate from mechanical
expansion and topology integration.

It does not call synchronous `GRC9V3.step()`, apply the delayed-evaluation
continuity formula, integrate topology changes, or emit identity acceptance.

The executable Iteration 25/26 verification surface is correspondingly narrow:
bounded interleaved packet fixtures must drain without starvation, many-event
packet runs must preserve `sum_i C_i + sum_p C_p` after every processed event,
and unit-lapse / constant-delay runs must produce the documented packet timing
surface. Full comparison against synchronous `GRC9V3.step()` is a later
comparison task, not an Iteration 26 claim.

LGRC-2 still exposes helper functions for direct packet processing:

```text
GRC9V3State + LGRC9V3PacketLedger + processing helpers
```

The helpers may mutate node coherence on the supplied `GRC9V3State`, but the
packet ledger and event queue remain explicit evidence objects. Iteration 25
adds a concrete `LGRC9V3.step()` shell that composes those helpers into
deterministic packet departure/arrival queue processing without
reinterpreting the helpers as synchronous `GRC9V3.step()` behavior.

## Capabilities

`LGRC9V3.list_capabilities()` must include all required `GRC9V3` capabilities:

- `port_graph`
- `mechanical_refinement`
- `column_coarse_graining`
- `basin_attributes`
- `hierarchy_tracking`
- `multi_metric_edges`
- `choice_collapse_semantics`
- `quadrature_budget`
- `intrinsic_frame`

It must also include:

- `causal_layer`

if and only if the executable `LGRC9V3` runtime or artifact surface serializes
the causal-state fields required by this spec.

Annotation-only LGRC-0 evidence may expose causal fields before a concrete
model class exists, but it must mark them as:

```text
causal_layer_mode = "annotation"
```

and must not imply behavior-changing causal propagation.

## Runtime Levels

### LGRC-0: Causal Annotation

LGRC-0 is annotation-only.

It may compute timing and causal overlays from existing `GRC9V3` runtime
evidence. It must not change:

- step order,
- event counts,
- spark decisions,
- topology,
- budget evolution,
- identity acceptance,
- snapshots produced by the underlying synchronous model.

### LGRC-1: Fixed-Topology Semi-Causal Eligibility

LGRC-1 may make local proper time operational for update or diagnostic
eligibility on fixed topology.

It must be opt-in and must serialize:

```text
causal_layer_mode = "fixed_topology_semicausal"
```

unless causal availability buffers exist. Without such buffers, it must not
claim full causal propagation.

LGRC-1 must reject or disable:

- mechanical expansion,
- collapse/reabsorption,
- topology-changing identity claims,
- in-flight packet conservation claims.

The first LGRC-1 implementation is an eligibility surface, not a full
replacement step loop. It computes:

```text
delta_tau_i = tau_i - tau_i_last_update
```

and marks nodes eligible when `delta_tau_i >= min_delta_tau` under the selected
policy. Proper time may advance virtually for all live nodes at the current
event-time frontier, while `node_last_update_proper_time` advances only for
explicitly processed nodes.

LGRC-1 evidence must serialize:

```text
artifact_kind = "lgrc9v3_fixed_topology_eligibility"
artifact_schema_version = "lgrc9v3_fixed_topology_eligibility_v1"
mode_version = "lgrc1_fixed_topology_semicausal_v1"
evidence_class = "fixed_topology_semicausal"
semi_causal = true
causal_availability_buffers = false
packetized_flux = false
topology_change_allowed = false
mechanical_expansion_allowed = false
collapse_allowed = false
identity_acceptance_allowed = false
```

unless a later version explicitly introduces causal availability buffers or a
packetized runtime.

### Continuation Levels

LGRC-2 is packetized causal flux on fixed topology. The current code exports
the packet/event/ledger contract, passive packet ledger artifacts, and active
departure/arrival processors for fixed-topology packet records.

The pending-flux compaction gate is complete for fixed-topology LGRC-2.
Canonical packet ledgers remain per-packet. Compact pending-flux ledgers are
derived, budget-equivalent artifacts over in-flight packets. They aggregate by
directed channel, arrival key, and source/target lineage while retaining packet
ids and departure keys for later LGRC-3 refinement transport audits.

LGRC-3 now has a contract artifact for topology-changing causal history. The
first LGRC-3 scope is refinement lineage, packet transport through refinement,
and uniform proper-time inheritance. Collapse/reabsorption and proper-time
identity persistence remain out of scope until explicitly promoted.

Neither level is part of the completed LGRC-0/LGRC-1 behavior slice.

### LGRC-2: Packetized Causal-Flux Contract

LGRC-2 uses:

```text
causal_layer_mode = "packetized_fixed_topology"
lgrc_runtime_level = "lgrc2"
mode_version = "lgrc2_packetized_fixed_topology_v1"
evidence_class = "packetized_causal_flux"
```

The packet contract artifact uses:

```text
artifact_kind = "lgrc9v3_packet_contract"
artifact_schema_version = "lgrc9v3_packet_contract_v1"
```

Event queue ordering is deterministic:

```text
event_queue_tie_break_policy =
    "event_time_key_then_scheduler_event_index_then_event_id"
```

Packet event kinds are:

```text
lgrc9v3_packet_departure
lgrc9v3_packet_arrival
```

Packet lifecycle states are:

```text
scheduled
in_flight
arrived
cancelled
```

Packet records must include at least:

```text
packet_id
packet_state
source_node_id
target_node_id
edge_id
amount
departure_event_time_key
arrival_event_time_key
```

The normal LGRC-2 packet path derives the arrival event-time key from the
captured edge-delay surface:

```text
arrival_event_time_key = departure_event_time_key + edge_causal_delay[edge_id]
```

This key is `T_e`, the event-queue ordering key. It is not the source node's
or target node's local proper time. Explicit caller-provided
`arrival_event_time_key` values remain allowed for replay fixtures and
compatibility tests, but they must be treated as explicit event-time policy,
not as node-local clock evidence.

Packet records may also carry:

```text
departure_event_id
arrival_event_id
departure_scheduler_event_index
arrival_scheduler_event_index
source_lineage_id
target_lineage_id
```

Ledger artifacts must name:

```text
packet_records
packet_event_records
event_queue_records
event_queue_tie_break_policy
packet_budget_invariant
node_coherence_total
in_flight_packet_total
conserved_budget_total
budget_before
budget_after
budget_error
fixed_topology_signature
```

Passive ledger artifacts use:

```text
artifact_kind = "lgrc9v3_packet_ledger"
artifact_schema_version = "lgrc9v3_packet_ledger_v1"
```

The packet/ledger surface provides:

```text
LGRC9V3PacketRecord
LGRC9V3PacketQueueEventRecord
LGRC9V3PacketLedger
build_lgrc9v3_packet_id(...)
build_lgrc9v3_packet_event_id(...)
derive_lgrc9v3_packet_arrival_event_time_key(...)
create_lgrc9v3_packet_record(...)
create_lgrc9v3_packet_queue_event_record(...)
build_lgrc9v3_packet_ledger(...)
restore_lgrc9v3_packet_ledger_artifact(...)
schedule_lgrc9v3_packet_departure(...)
process_lgrc9v3_packet_departure(...)
process_lgrc9v3_packet_arrival(...)
process_lgrc9v3_next_packet_event(...)
derive_lgrc9v3_packet_arrival_eligibility(...)
build_lgrc9v3_pending_flux_entry_id(...)
compact_lgrc9v3_packet_ledger(...)
restore_lgrc9v3_pending_flux_ledger_artifact(...)
```

The record and ledger creation helpers are passive data surfaces. The
processing helpers are active fixed-topology transitions:

```text
departure:
    subtract amount from source node coherence
    add amount to in-flight packet total

arrival:
    remove amount from in-flight packet total
    add amount to target node coherence
```

Processing helpers mutate node coherence and packet lifecycle evidence only.
They do not mutate topology, schedule sparks, apply mechanical expansion,
accept identity, collapse basins, or transport packets through topology
changes.

The `scheduled` packet state is operational. A scheduled packet is created by
`schedule_lgrc9v3_packet_departure(...)`, is queued as a deterministic
departure event, and does not count as in-flight coherence until that queued
departure is processed. Processing the queued departure transitions the packet
to `in_flight`, debits source coherence, and queues the arrival event.

Packet arrival can expose a positive local-update / spark-diagnostic
eligibility surface through:

```text
derive_lgrc9v3_packet_arrival_eligibility(...)
```

That artifact uses:

```text
artifact_kind = "lgrc9v3_packet_arrival_eligibility"
artifact_schema_version = "lgrc9v3_packet_arrival_eligibility_v1"
evidence_class = "packet_arrival_eligibility"
```

It records that the target node may be considered for local update or
spark-diagnostic evaluation after an arrival. It does not run the local update,
does not run a spark predicate, and does not emit expansion or identity
acceptance.

Compact pending-flux ledgers use:

```text
artifact_kind = "lgrc9v3_pending_flux_ledger"
artifact_schema_version = "lgrc9v3_pending_flux_ledger_v1"
evidence_class = "compact_pending_flux"
compaction_policy = "exact_directed_channel_arrival_lineage"
```

The canonical LGRC-2 packet ledger remains per-packet. The compact ledger is a
derived representation over in-flight packets. It aggregates packets only when
these fields match:

```text
source_node_id
target_node_id
edge_id
arrival_event_time_key
source_lineage_id
target_lineage_id
```

Each compact entry preserves:

```text
entry_id
source_node_id
target_node_id
edge_id
arrival_event_time_key
source_lineage_id
target_lineage_id
amount_total
packet_count
packet_ids
departure_event_time_keys
transport_ready_for_refinement = true
```

The compact ledger must preserve budget equivalence:

```text
pending_flux_total == in_flight_packet_total
conserved_budget_total == node_coherence_total + pending_flux_total
```

It also serializes:

```text
canonical_packet_ledger_retained = true
lineage_preserved = true
topology_change_allowed = false
packet_transport_through_topology_change = false
```

LGRC-3 may later transport compact entries by applying refinement lineage maps
to the preserved source node, target node, edge id, source lineage, target
lineage, and packet ids. Iteration 12 does not perform that transport.

The LGRC-2 budget invariant is:

```text
packet_budget_invariant = "sum_node_coherence_plus_packets"
B = sum_i C_i + sum_p C_p
```

LGRC-2 is fixed-topology. It must serialize:

```text
packetized_flux = true
fixed_topology = true
topology_change_allowed = false
packet_transport_through_topology_change = false
identity_acceptance_allowed = false
collapse_allowed = false
```

Packet arrival may expose local update or spark-diagnostic eligibility, but
arrival alone is not a spark, refinement, collapse, or identity event.

### LGRC-3: Topology Contract

Iteration 13 defines the LGRC-3 topology-changing causal-history contract. It
does not process topology changes.

The contract artifact uses:

```text
artifact_kind = "lgrc9v3_topology_contract"
artifact_schema_version = "lgrc9v3_topology_contract_v1"
mode_version = "lgrc3_topology_contract_v1"
evidence_class = "topology_contract"
causal_layer_mode = "topology_changing_causal_history"
lgrc_runtime_level = "lgrc3"
contract_only = true
topology_change_processing_implemented = false
packet_transport_through_topology_change_implemented = false
collapse_reabsorption_in_scope = false
proper_time_identity_in_scope = false
```

The topology event kinds in scope for the first LGRC-3 contract are:

```text
lgrc9v3_refinement_topology_event
lgrc9v3_refinement_packet_transport
lgrc9v3_proper_time_inheritance
```

The topology event kinds explicitly out of scope for this slice are:

```text
lgrc9v3_causal_collapse
lgrc9v3_causal_reabsorption
lgrc9v3_proper_time_identity_acceptance
```

Refinement lineage records must preserve enough evidence to link the
pre-topology and post-topology state:

```text
topology_event_id
topology_event_kind
source_expansion_event_id
pre_topology_signature
post_topology_signature
refinement_lineage_map
expanded_node_id
replacement_node_ids
parent_to_child_node_lineage
boundary_reassignment_map
budget_before
budget_after
budget_error
```

Packet transport records must preserve packet and pending-flux lineage:

```text
topology_event_id
source_packet_ids
source_pending_flux_entry_ids
transported_packet_ids
amount_total
budget_before
budget_after
budget_error
identity_acceptance_emitted
```

Iteration 14 implements refinement packet transport evidence:

```text
artifact_kind = "lgrc9v3_refinement_packet_transport_result"
artifact_schema_version = "lgrc9v3_refinement_packet_transport_result_v1"
evidence_class = "refinement_packet_transport"
topology_event_kind = "lgrc9v3_refinement_packet_transport"
```

The transport helper consumes:

```text
pre-expansion LGRC-2 packet ledger
GRC9V3 hybrid_mechanical_expansion event
post-expansion topology signature
optional compact pending-flux ledger
```

and produces:

```text
transported_ledger
packet_transport_records
source_packet_ids
transported_packet_ids
source_pending_flux_entry_ids
budget_before
budget_after
budget_error
```

For packets whose source or target is the expanded node, transport uses the
GRC9V3 expansion `reassignment_map` to replace the expanded endpoint with the
column-preserving replacement endpoint. Boundary evidence must record:

```text
old_parent_port
new_endpoint_port
old_parent_column
new_endpoint_column
```

The packet id is preserved. Lineage fields record the endpoint transport, for
example:

```text
source_lineage_id_after = source_lineage_id_before + "|node:old->node:new"
```

Transport preserves:

```text
sum_i C_i + sum_p C_p
```

and must keep:

```text
identity_acceptance_emitted = false
packet_transport_identity_transfer = false
```

Proper-time inheritance uses the first-round policy:

```text
proper_time_inheritance_policy = "uniform_parent_proper_time"
internal_edge_delay_policy = "explicit_or_default_tau0"
```

Uniform inheritance means newly created child nodes inherit the parent's
proper-time value at the refinement event. Internal edge delays must be
explicitly recorded or assigned the configured default `tau_0`.

The first active processor for this contract is:

```text
process_lgrc9v3_proper_time_inheritance(...)
```

It consumes a GRC9V3 `hybrid_mechanical_expansion` event and the parent
proper-time surface captured at the refinement event, then emits
`lgrc9v3_proper_time_inheritance` evidence. It must serialize
`scheduler_event_index`, `checkpoint_index`, and `event_time_key` separately,
and it must keep `identity_acceptance_emitted = false`.

The contract preserves these distinctions:

```text
candidate_event != mechanical_expansion != identity_acceptance
packet_transport != semantic_identity_transfer
refinement_lineage != proof_of_persistent_child_identity
```

Iteration 15 defines the default-disabled collapse/identity policy contract:

```text
artifact_kind = "lgrc9v3_collapse_identity_policy_contract"
artifact_schema_version = "lgrc9v3_collapse_identity_policy_contract_v1"
evidence_class = "collapse_identity_policy_contract"
contract_only = true
collapse_reabsorption_processing_implemented = false
proper_time_identity_processing_implemented = false
```

Collapse/reabsorption payloads must preserve causal timing, sink selection,
budget transfer, and lineage transfer evidence:

```text
topology_event_id
topology_event_kind
scheduler_event_index
checkpoint_index
event_time_key
node_proper_time
competing_sink_ids
selected_sink_id
losing_sink_ids
lineage_transfer_map
source_lineage_ids
target_lineage_id
transferred_node_ids
transferred_packet_ids
transferred_pending_flux_entry_ids
coherence_transfer_amount
budget_before
budget_after
budget_error
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

The first active processor for this contract is:

```text
process_lgrc9v3_collapse_reabsorption(...)
```

It consumes explicit sink-selection/collapse evidence, node proper-time
surfaces, explicit lineage transfer maps, and packet/pending-flux ledgers when
available. It emits `lgrc9v3_causal_collapse` or
`lgrc9v3_causal_reabsorption` evidence only when
`collapse_reabsorption_allowed = true`.

The v1 helper consumes these as explicit parameters rather than a single
basin/collapse artifact object. A future replay/runtime adapter may assemble
the same parameters from a richer causal basin-collapse artifact.

The processor records affected packet and pending-flux ids, but does not
transport those packets through the collapse/reabsorption lineage map. That is
owned by the packet-transport extension.

The active packet-transport extension is:

```text
transport_lgrc9v3_packets_through_collapse_reabsorption(...)
```

It consumes the pre-collapse packet ledger, the collapse/reabsorption result,
and the compact pending-flux ledger when available. Affected in-flight packet
endpoints are redirected through the lineage map to the selected sink. Packet
ids remain stable for packets that remain in flight. Packets that become
selected-sink self-loops are settled into node coherence in the returned
packet ledger and removed from the future event queue.

The transport policy is:

```text
redirect_to_selected_sink_or_settle_self_loop
```

Proper-time identity payloads must keep identity acceptance explicit:

```text
topology_event_id
topology_event_kind
source_topology_event_ids
event_time_key
sink_node_id
lineage_id
basin_node_ids
identity_clock_policy
threshold_calibration_policy
proper_time_persistence_threshold
threshold_multiplier
local_median_edge_delay
window_start_event_time_key
window_end_event_time_key
observed_persistence_duration
budget_before
budget_after
budget_error
identity_acceptance_allowed
identity_acceptance_emitted
```

The first-round identity clock policy is:

```text
identity_clock_policy = "sink_local_proper_time"
threshold_calibration_policy = "local_median_delay_multiplier"
threshold_multiplier = 4.0
```

The active persistence evaluator is:

```text
evaluate_lgrc9v3_proper_time_identity_persistence(...)
```

It evaluates, but does not accept, identity. The evaluator consumes:

```text
source_topology_event_ids
basin_node_ids
node_proper_time
local_edge_delay or local_median_edge_delay
```

The evaluator computes:

```text
proper_time_persistence_threshold =
    threshold_multiplier * local_median_edge_delay

observed_persistence_duration =
    window_end_sink_proper_time - window_start_sink_proper_time
```

and serializes:

```text
artifact_kind = "lgrc9v3_proper_time_identity_persistence_evaluation"
evidence_class = "proper_time_identity_persistence_evaluation"
identity_acceptance_allowed = false
identity_acceptance_emitted = false
```

The active identity-acceptance event emitter remains separate:

```text
emit_lgrc9v3_proper_time_identity_acceptance(...)
```

It requires a passing evaluator result and explicit:

```text
identity_acceptance_allowed = true
```

and emits exactly one event:

```text
kind = "lgrc9v3_proper_time_identity_acceptance"
event_schema_version = "lgrc9v3_proper_time_identity_acceptance_event_v1"
evidence_class = "proper_time_identity_acceptance"
```

The identity event is semantic acceptance evidence. It must record
`mechanical_expansion_emitted = false`,
`packet_transport_emitted = false`,
`mechanical_expansion_is_identity_acceptance = false`, and
`refinement_packet_transport_is_identity_transfer = false`.

The active topology-event replay validator is:

```text
validate_lgrc9v3_topology_event_replay(...)
```

It consumes an ordered replay sequence of LGRC-3 artifacts/events:

```text
lgrc9v3_refinement_packet_transport_result
lgrc9v3_proper_time_inheritance_result
lgrc9v3_collapse_reabsorption_result
lgrc9v3_collapse_reabsorption_packet_transport_result
lgrc9v3_proper_time_identity_persistence_evaluation
lgrc9v3_proper_time_identity_acceptance
```

and emits validation evidence:

```text
artifact_kind = "lgrc9v3_topology_event_replay_validation"
artifact_schema_version = "lgrc9v3_topology_event_replay_validation_v1"
evidence_class = "topology_event_replay_validation"
```

The validator checks:

```text
event_time_key is nondecreasing in replay order
source topology ids have already appeared in replay
identity acceptance references a prior identity evaluation
lineage ids are present where required
budget continuity holds across budget-bearing records
```

It does not schedule or process the events; it only audits serialized replay
evidence.

The contract remains disabled by default:

```text
collapse_reabsorption_allowed = false
identity_acceptance_allowed = false
mechanical_expansion_is_identity_acceptance = false
refinement_packet_transport_is_identity_transfer = false
```

### LGRC-3: Default-Off Multi-Basin Formation Contract

The N25.1-driven Phase 8 continuation defines a default-off contract surface for
multi-basin formation from causal refinement. The contract does not emit runtime
evidence by itself. It freezes the artifact names, policy flags, digest fields,
and fail-closed guards required before LGRC9V3 can expose replayable
multi-basin formation evidence.

Default flags:

```text
native_lgrc_multi_basin_formation_enabled = false
native_lgrc_multi_basin_formation_policy = "disabled"
native_lgrc_multi_basin_formation_validated = false
native_lgrc_multi_basin_formation_supported = false
```

The active v1 policy name is:

```text
post_refinement_child_basin_replay
```

When enabled, the policy requires:

```text
lgrc_runtime_level = "lgrc3"
causal_layer_mode = "topology_changing_causal_history"
causal_topology_integration_allowed = true
```

The v1 contract defines four passive artifact types:

```text
lgrc9v3_multi_basin_post_refinement_flow_window_record
lgrc9v3_child_basin_state_record
lgrc9v3_multi_basin_replay_validation_record
lgrc9v3_multi_basin_merge_leakage_control_record
```

The post-refinement flow-window record cites a committed topology/refinement
source and serializes:

```text
source_topology_event_id
source_topology_event_digest
source_expansion_id
pre_refinement_topology_signature
post_refinement_topology_signature
refinement_lineage_map
refinement_lineage_map_digest
window_start_event_time_key
window_end_event_time_key
window_scheduler_indices
node_support_trace
node_coherence_trace
edge_flux_trace
packet_flux_trace
node_plus_packet_budget_trace
runtime_visible_inputs
claim_flags
post_refinement_flow_window_digest
```

The child-basin state record cites the flow-window digest and serializes:

```text
child_basin_core_ids
child_basin_membership_by_core
child_basin_membership_digest
child_basin_support_floor_records
child_basin_coherence_floor_records
child_basin_boundary_records
child_basin_flux_records
old_basin_relation_trace
merge_leakage_trace
producer_residue_classification
runtime_visible_inputs
claim_flags
child_basin_state_digest
```

The runtime stores emitted candidate records under:

```text
post_refinement_flow_window_log
child_basin_state_log
multi_basin_replay_validation_log
```

All three logs are empty when the policy is disabled. Missing log fields in older
snapshots restore as empty lists. When the policy is enabled, committed native
route arbitration topology events may emit one post-refinement flow-window
record and one child-basin state record from the committed topology event,
lineage transfer map, topology-state reabsorption state signatures, active
node/edge state, and packet ledger. For route-arbitration collapse/reabsorption
sources, `source_expansion_id` is namespaced as a native-route candidate source;
it is not relabeled as a GRC spark expansion event. This emission is a
candidate surface only:
it does not set `native_lgrc_multi_basin_formation_validated`, does not set
`native_lgrc_multi_basin_formation_supported`, and cannot support MB4+ without
later replay and merge/leakage controls.

In the current LGRC9V3 substrate, node state exposes coherence as the
source-current scalar available for local support accounting. I85 therefore
populates support traces and coherence traces from the same source-current
coherence value. This preserves the contract fields while keeping the claim
bounded: I85 does not establish an independent native support channel.

The replay validation record cites the child-basin state digest and serializes
artifact replay, snapshot/load replay, duplicate replay, time-order replay,
persistence ratios, replay window, and replay failure modes. Replay result
statuses are `passed`, `failed_closed`, `failed_open`, and `not_run`.
Runtime replay validation reconstructs the serialized topology-event ->
flow-window -> child-basin-state chain, compares child-basin membership,
support, coherence, boundary, and flux maps against a loaded snapshot artifact,
and appends a digest-idempotent replay record. Missing snapshot replay records
`not_run` and blocks MB4 admission. Clean replay can support an MB4
replay-backed child-basin candidate, but does not support MB5/MB6 without
merge/leakage controls and N26 handoff gates.

The merge/leakage control record cites the child-basin state digest and
serializes one fail-closed control result, including blocked condition,
expected/actual result, rung effect, and merge/leakage metrics.

These records must reject hidden fixture inputs, label-only child basins,
old-basin thickening, transient flow sinks, merge/leakage-as-success,
hidden producer basin insertion, producer-assisted success as native upgrade,
post-hoc membership selection, and claim promotion. The implementation also
rejects existing native-route hidden-input aliases and legacy claim-promotion
keys as a defensive superset, but those aliases do not broaden the positive
multi-basin claim. These records do not mutate runtime state, schedule packets,
commit topology events, or open BF6 / native support / agency / semantic
learning / semantic choice / sentience / ant-ecology claims.

## State Specification

Iteration 24 chooses a composed runtime-state bundle rather than subclassing
`GRC9V3State`.

```python
@dataclass
class LGRC9V3RuntimeState:
    base_state: GRC9V3State
    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    node_proper_time: dict[NodeId, float]
    node_last_update_proper_time: dict[NodeId, float]
    node_last_update_event_time_key: dict[NodeId, float]
    edge_causal_delay: dict[EdgeId, float]
    lapse: dict[NodeId, float]
    packet_ledger: LGRC9V3PacketLedger
    event_queue: tuple[LGRC9V3PacketQueueEventRecord, ...]
    causal_flux_routes: dict[NodeId, list[dict[str, object]]]
    local_update_log: tuple[dict[str, object], ...]
    topology_event_log: tuple[GRCEvent | dict[str, object], ...]
    causal_layer_mode: str
    lapse_policy: str
    edge_delay_policy: str
    proper_time_accumulation_policy: str
```

The runtime may choose equivalent nested names, but snapshot serialization must
expose equivalent fields with stable names. Existing `GRC9V3State` snapshots do
not become `LGRC9V3RuntimeState` snapshots automatically; loading them into
`LGRC9V3` requires an explicit adapter or synchronous-limit policy.

## Timing Semantics

`LGRC9V3` must keep these quantities distinct:

| Field | Meaning |
|---|---|
| `scheduler_event_index` / `kappa` | event-processing order |
| `checkpoint_index` / `k` | snapshot/replay order |
| `event_time_key` / `T_e` | scheduler/event-queue ordering key |
| `node_proper_time` / `tau_i` | local accumulated proper time |
| `edge_causal_delay` / `tau_ij` | edge or directed-edge causal delay |

`step_index` from synchronous `GRC9V3` is not automatically any of these
quantities. Compatibility adapters may map synchronous `step_index` to one or
more causal fields only under an explicitly serialized synchronous-limit
policy.

Arrival timing must use the event-time key form:

```text
T_arrive(i -> j) = T_depart(i) + tau_ij
```

not a silent assumption that all nodes share the same local proper-time clock.

## Parameters

`LGRC9V3` includes all `GRC9V3` parameters plus:

- `causal_layer_mode`
- `lgrc_runtime_level`
- `lapse_policy`
- `edge_delay_policy`
- `event_time_policy`
- `proper_time_accumulation_policy`
- `causal_distance_policy`
- `causal_cone_policy`
- `causal_basin_core_policy`
- `require_fixed_topology_for_lgrc1`
- `require_fixed_topology_for_lgrc2`

These fields live in:

```text
constitutive_semantic_modes["causal_history"]
```

for model parameters. Runtime artifacts and checkpoints must copy the resolved
values into a same-named evidence block:

```text
causal_history
```

This keeps causal-history semantics inside core model params while preserving
artifact-level replay evidence. It must not use top-level `runtime`,
`observer`, or `tooling` parameter domains, because the core parameter contract
excludes those domains.

Required defaults:

```text
causal_layer_mode = "annotation"
lgrc_runtime_level = "lgrc0"
lapse_policy = "bounded_density_tension"
edge_delay_policy = "geometry_baseline"
event_time_policy = "derived_from_synchronous_step"
proper_time_accumulation_policy = "annotation"
require_fixed_topology_for_lgrc1 = true
require_fixed_topology_for_lgrc2 = true
```

Changing `causal_layer_mode` from `"annotation"` to a behavior-changing mode
is a runtime semantic change and must be opt-in.

## Lapse And Edge Delay

The first lapse policy should be bounded and reflexive:

```text
N_i = clip(
    1
    + lambda_N * (C_i - C_ref) / (C_ref + eps_C)
    + mu_N * ||g_i|| / (g_ref + eps_g),
    N_min,
    N_max
)
```

where reference scales may initially be global or fixture-level medians, but
the selected calibration source must be serialized.

The first edge-delay policy may use a geometry-only baseline:

```text
tau_ij = tau_0 * h_ij
```

or the GRC-V3 temporal-delay label as an operational candidate:

```text
tau_ij = max(tau_min, ell_ij / (v_0 + rho * |J_ij| + eps_tau))
```

The implementation must serialize which policy was used.

## Three Distance Surfaces

`LGRC9V3` must preserve the three-distance distinction:

| Distance | Meaning | Example source |
|---|---|---|
| geometric distance | spatial/chart separation | `geometric_length`, port geometry |
| causal/proper-time distance | minimum arrival-time cost | `edge_causal_delay` |
| functional/coupling distance | influence / transport relation | `base_conductance`, `flux_coupling`, flux |

No API or artifact field should collapse these into an ambiguous generic
`distance` without a mode tag.

LGRC-0 annotation may expose the functional distance surface using one of:

- `inverse_base_conductance`
- `inverse_flux_coupling`
- `inverse_combined_coupling`

The selected `functional_distance_policy` must be serialized when the
functional distance surface is emitted. These policies describe a derived
annotation surface; they are not packet transport or operational causal
propagation semantics.

The v1 shortest-path helpers are undirected because LGRC-0 uses symmetric
edge-delay annotations. Directed future/past cone computation requires a
directed adjacency surface and belongs to later LGRC packet/causal runtime
work.

## Spark Semantics

`LGRC9V3` inherits `GRC9V3` spark lanes:

| Lane | Meaning |
|---|---|
| `current_hybrid_signed_hessian` | default Lane A signed-Hessian hybrid gate |
| `grc9v3_column_h_assisted` | opt-in Lane B direct runtime-computed column-H proxy branch inside the GRC9V3 saturation / gradient envelope |

LGRC-0 must not change either lane.

LGRC-1 may change when diagnostics are eligible to be evaluated, but it must
not silently change the predicate itself. Any causal eligibility field must be
serialized separately from the spark-lane field.

If previous diagnostics are needed after refinement or lineage transport, the
runtime must resolve them through explicit lineage/chart transport. If no valid
predecessor chart exists, the previous diagnostic is unavailable rather than
guessed.

Iteration 27 implements the first active causal spark diagnostic surface:

```text
event kind:
    lgrc9v3_causal_spark_candidate

schema:
    lgrc9v3_causal_spark_candidate_event_v1
```

The runtime evaluates the existing GRC9V3 Lane A/Lane B predicate at
arrival/local-update boundaries and through an explicit diagnostic API. It
temporarily keys GRC9V3 diagnostic history by
`causal_spark_evaluation_index`, then wraps the captured candidate payload
without recomputing Column-H after the diagnostic snapshot. The wrapped event
must record:

```text
causal_spark_evaluation_index
causal_spark_trigger_kind
causal_spark_trigger_event_id
causal_spark_trigger_source
scheduler_event_index
checkpoint_index
event_time_key
candidate_node_proper_time
node_proper_time_surface
pre_expansion_topology_signature
diagnostic_source
```

The candidate event must also preserve branch attribution fields from GRC9V3,
including `signed_hessian_hit`, `column_h_threshold_hit`,
`column_h_sign_crossing_hit`, `column_h_branch_hit`, `lane_b_candidate_hit`
when Lane B is selected, and `gate_reasons`.

The event must not imply expansion or identity:

```text
topology_mutated = false
mechanical_expansion_emitted = false
identity_acceptance_emitted = false
packet_transport_emitted = false
```

## Budget Semantics

LGRC-0 does not change the `GRC9V3` budget invariant:

```text
B = sum_i mu_i C_i
```

LGRC-1 must preserve the same budget under its selected fixed-topology update
order.

The packetized LGRC invariant:

```text
B = sum_i C_i + sum_p C_p
```

belongs to LGRC-2. It may be claimed only by packet ledger or processing
artifacts that explicitly represent in-flight coherence and audit
`budget_before`, `budget_after`, and `budget_error`. LGRC-0/LGRC-1 artifacts
must not claim this invariant.

## Serialization

An `LGRC9V3` snapshot or annotation artifact must serialize:

- all required `GRC9V3` snapshot fields,
- `causal_layer_mode`,
- `lgrc_runtime_level`,
- `scheduler_event_index`,
- `checkpoint_index`,
- `event_time_key`,
- `node_proper_time`,
- `node_last_update_proper_time`,
- `node_last_update_event_time_key`,
- `edge_causal_delay`,
- `lapse`,
- `causal_flux_routes`,
- `local_update_log`,
- `causal_spark_evaluation_index`,
- `causal_spark_diagnostic_log`,
- `lapse_policy`,
- `edge_delay_policy`,
- `event_time_policy`,
- `proper_time_accumulation_policy`,
- causal distance/cone policy metadata when those surfaces are emitted.

LGRC-0 annotation evidence is serialized under the optional artifact key:

```text
causal_history
```

The v1 block must record:

```text
artifact_kind = "lgrc9v3_causal_annotation"
artifact_schema_version = "lgrc9v3_causal_annotation_v1"
annotation_mode_version = "lgrc0_annotation_v1"
runtime_family = "LGRC9V3"
evidence_class = "derived_annotation"
annotation_only = true
```

Event timing fields, node proper-time fields, and edge delay fields are present
only inside this optional block for LGRC-0. Existing non-LGRC snapshots must
remain valid without the block.

If a field is absent because the artifact predates LGRC support or because the
mode is disabled, readers must treat the artifact as non-LGRC evidence rather
than inventing default causal semantics.

## Out Of Scope

The current executable `LGRC9V3` queue shell must not claim:

- general LGRC runtime implementation;
- executable `LGRC9` standalone runtime;
- executable `LGRCV3` runtime;
- algebraic Lorentzian metric tensor;
- active topology-changing causal-history processing inside `LGRC9V3.step()`;
- in-loop in-flight packet redirection through expansion;
- in-loop causal collapse/reabsorption;
- default proper-time identity acceptance;
- delayed-evaluation continuity as an active runtime path;
- landscape-general LGRC validation.

## Future Continuation Points

The following are named continuation points, not part of the first
`LGRC9V3` contract.

| Surface | Future Contract Needed |
|---|---|
| standalone `LGRC9` | executable pure nine-port Lorentzian runtime contract |
| executable `LGRCV3` | non-nine-port V3 Lorentzian runtime contract |
| shared LGRC base | common abstraction after multiple executable LGRC families exist |
| LGRC-3 topology processing | implementation of the Iteration 13 topology contract |
| proper-time identity | identity clock policy and persistence-window semantics |
| causal collapse/reabsorption | collapse event schema with budget and lineage transfer |
| directed delay | orientation, normalization, clipping, and default policy |
| algebraic Lorentzian metric | signed interval/tensor semantics, if ever justified |
| landscape-general validation | held-out validation suite and reporting protocol |

Future work must extend this spec or create a new spec before claiming any of
these surfaces as implemented.

## Acceptance Criteria

The `LGRC9V3` implementation is acceptable only when:

- LGRC-0 annotation can be produced without changing `GRC9V3` outputs;
- timing fields are serialized with unambiguous names;
- the selected lapse and edge-delay policies are serialized;
- three-distance surfaces remain distinct;
- Lane A and Lane B spark predicates remain unchanged when causal modes are
  annotation-only;
- LGRC-1, if implemented, is opt-in and labelled semi-causal unless causal
  availability buffers exist;
- LGRC-2 packet processing preserves
  `sum_i C_i + sum_p C_p` on fixed topology;
- LGRC-2 compact pending-flux artifacts are budget-equivalent derived views of
  in-flight packet records and preserve packet/lineage audit fields;
- old `GRC9V3` snapshots and artifacts remain loadable.
