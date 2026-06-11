# Phase 8 LGRC9 Topology-State Reabsorption Plan

## Purpose

This document defines the Phase 8 continuation opened by N04 Iteration 19-D.

The previous continuation closed native causal pulse-substrate surface lineage
transport:

```text
committed topology event
-> superseded or transported surface row
-> producer stale-read prevention
-> artifact-only lineage replay
```

N04 Iteration 19-D showed that this lineage layer works, but that actual
topology-mutating movement remains blocked by a deeper runtime boundary:

```text
primary_blocker =
packet_ledger_state_reabsorption_mismatch_after_topology_event
```

The concrete 19-D failure was:

```text
ledger node total = 6.0
active state node total = 5.9
delta = 0.1
```

This continuation adds the missing operational layer:

```text
native topology-state reabsorption
```

Surface lineage records what old evidence maps to. Topology-state
reabsorption applies a committed topology lineage event to the live runtime
substrate so active node/edge state and packet ledger accounting are rebased
together.

Companion checklist:

- [`Phase-8-LGRC9-TopologyStateReabsorptionChecklist.md`](./Phase-8-LGRC9-TopologyStateReabsorptionChecklist.md)

## Inputs

Theory and implementation context:

- [`../papers/2026-05-LGRC-9.md`](../papers/2026-05-LGRC-9.md)
- [`../papers/2026-05-LGRC9V3-Native-Packet-Loops.md`](../papers/2026-05-LGRC9V3-Native-Packet-Loops.md)
- [`../papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md`](../papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md)

N04 boundary evidence:

- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.md)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19d_topology_mutating_movement_probe.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19d_topology_mutating_movement_probe.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19d_topology_mutating_movement_probe.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19d_topology_mutating_movement_probe.md)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_continuation_closeout.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_continuation_closeout.md)

## Current Boundary

Supported today:

- LGRC-3 committed topology events and topology event digests;
- packet transport through topology lineage records;
- causal pulse-substrate surface supersession and transport;
- producer stale-read prevention;
- artifact-only surface lineage replay;
- N04 adaptive topology entry candidate.

Blocked today:

- applying topology lineage to the active runtime substrate;
- reconciling active `GRC9V3State.nodes` with packet-ledger node totals after
  topology events;
- post-topology producer-scheduled packet work;
- topology-mutating movement evidence.

The current N04 ceiling remains:

```text
adaptive_topology_entry_candidate
```

## Scope

In scope:

- default-off topology-state reabsorption policy;
- serializable topology-state reabsorption records;
- active node-state rebase/merge/retirement through committed topology lineage
  maps;
- packet-ledger node totals and in-flight packet totals rebased with the same
  lineage map;
- lineage-aware packet ledger/state alignment for LGRC-3 after topology
  events;
- producer scheduling after topology events only from reabsorbed,
  lineage-current state;
- snapshot, telemetry, and artifact-only replay for topology-state
  reabsorption evidence;
- controls for missing topology event, missing lineage map, partial lineage
  map, budget discontinuity, stale topology state, direct state rewrite, and
  topology-only claim promotion.

Out of scope:

- movement, adaptive-topology movement, topology-mutating movement, choice,
  agency, locomotion-like, biological, or identity-acceptance claims;
- native RC identity collapse or semantic branch choice;
- producers directly mutating coherence or topology;
- weakening fixed-topology LGRC-2 packet invariants;
- replacing existing surface-lineage transport contracts.

## Mechanism

This is not just a boolean flag. The flag only enables a default-off policy.

Required mechanism:

```text
active state before topology event
    + committed topology event
    + explicit lineage transfer map
    + packet transport/reabsorption result
    -> active state after topology event
    -> packet ledger after topology event
    -> topology-state reabsorption record
```

The resulting invariant is:

```text
sum(active node coherence after)
==
packet_ledger.node_coherence_total after
```

and:

```text
sum(active node coherence after)
+ packet_ledger.in_flight_packet_total after
==
packet_ledger.conserved_budget_total
```

For LGRC-3, packet ledger alignment must be lineage-aware. Fixed-topology
LGRC-2 validation remains unchanged; LGRC-3 post-topology packet work must not
reuse a stale fixed-topology signature as if no topology event occurred.

Minimum topology-state reabsorption record fields:

```text
topology_state_reabsorption_record_id
schema_version
topology_event_id
topology_event_kind
topology_event_digest
event_time_key
scheduler_event_index
checkpoint_index
lineage_transfer_map
source_node_ids
target_node_ids
retired_node_ids
source_edge_ids
target_edge_ids
retired_edge_ids
node_state_before
node_state_after
edge_state_before
edge_state_after
packet_ledger_digest_before
packet_ledger_digest_after
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
active_state_digest_before
active_state_digest_after
state_reabsorption_action = rebased | merged | superseded | rejected
claim_flags
topology_state_reabsorption_digest
```

The record is evidence. It is not a movement claim.

The topology-state reabsorption idempotency key is the SHA-256 digest of:

```text
topology_event_digest
lineage_transfer_map_digest
topology_state_reabsorption_policy_id
state_reabsorption_action
packet_ledger_digest_before
active_state_digest_before
```

This suppresses duplicate reabsorption records for the same committed
topology/state/ledger transition while still allowing explicit policy or
lineage-map variants to be rejected or compared by validators. A weaker key
such as `topology_event_id` alone is not sufficient.

Reabsorption must account for transferred coherence through the lineage map.
It must not silently renormalize active node totals to match the packet ledger.
If a correction is needed but cannot be traced to committed packet/topology
lineage evidence, the lane fails closed and no support flag may be promoted.

## Policy Flags

Default baseline:

```text
causal_topology_state_reabsorption_enabled = false
causal_topology_state_reabsorption_policy = disabled
causal_topology_state_reabsorption_validated = false
causal_topology_state_reabsorption_supported = false
```

Validated/supported may become true only after schema, runtime, snapshot,
telemetry, artifact-only replay, and negative controls pass.

Enabled does not imply supported.

## Iteration Plan

### Iteration 66. Baseline Freeze

Freeze the 19-D boundary and current runtime behavior.

Acceptance:

- record 19-D primary blocker;
- confirm surface lineage support remains closed and green;
- confirm topology-state reabsorption flags are absent or false;
- confirm current focused LGRC9V3, packet-loop, topology, surface-lineage,
  snapshot, telemetry, and diff checks;
- record that N04 ceiling remains `adaptive_topology_entry_candidate`.

### Iteration 67. Contract And Policy Schema

Add default-off topology-state reabsorption schema and policy flags.

Acceptance:

- add policy flags;
- add topology-state reabsorption record schema;
- add digest helpers and the exact topology-state reabsorption idempotency key
  over topology event digest, lineage-map digest, policy id, action, packet
  ledger digest before, and active state digest before;
- reject below-LGRC-3 construction when enabled;
- reject records without committed topology event and lineage map;
- reject claim fields and producer-owned mutation fields;
- preserve old fixed-topology behavior.

### Iteration 68. Active State Reabsorption

Apply committed topology events to active node/edge state under explicit
lineage maps.

Acceptance:

- active node totals update with settled/reabsorbed packet amounts;
- retired/superseded nodes and edges are explicit;
- active graph state digest changes only through committed topology event;
- reabsorption accounts for coherence through lineage evidence and does not
  silently normalize active node totals to match the packet ledger;
- missing/partial lineage maps fail closed;
- no producer or claim flag writes occur.

### Iteration 69. Packet Ledger And State Rebase

Make packet ledger and active state agree after topology events.

Acceptance:

- LGRC-3 lineage-aware state/ledger alignment passes after topology event;
- fixed-topology LGRC-2 validation remains unchanged;
- in-flight and settled packets are transported/reabsorbed consistently;
- post-topology scheduling no longer fails with
  `packet_ledger_state_reabsorption_mismatch_after_topology_event`;
- budget conservation remains exact.

### Iteration 70. Producers After Reabsorption

Allow producers to schedule from lineage-current, reabsorbed state only.

Acceptance:

- producer reads transported surface digest and reabsorbed active state;
- stale pre-reabsorption state reads fail closed;
- scheduled post-topology packet work is consumed only by `step()`;
- producers do not mutate state or emit claims;
- N04-style 19-D fixture can schedule and process post-topology packet work,
  but movement claims remain blocked until N04 validators rerun.

### Iteration 71. Snapshot, Telemetry, Artifact Replay, Controls

Persist and validate topology-state reabsorption evidence.

Acceptance:

- snapshot save/load preserves reabsorbed state, packet ledger, topology event
  log, surface lineage log, and state reabsorption records;
- telemetry emits topology-state reabsorption evidence only when enabled;
- artifact-only validator reconstructs:

```text
packet event
-> source surface row
-> topology event
-> topology-state reabsorption record
-> transported/superseded surface row
-> producer record
-> scheduled/processed post-topology packet
```

- missing topology event, missing lineage map, budget discontinuity, duplicate
  reabsorption, stale state read, direct rewrite, and topology-only claim
  promotion controls fail with distinct blockers;
- old behavior remains compatible.

### Iteration 72. Closeout And N04 Return

Close this continuation only if topology-state reabsorption is artifact
validatable and old behavior remains compatible.

Acceptance:

- closeout JSON and markdown produced;
- enabled/validated/supported flags separated;
- claim flags remain blocked;
- N04 handoff points to a follow-up probe, likely `19-E`, to rerun strict
  topology-mutating movement after runtime support exists.

## Claim Boundary

This continuation may support:

```text
native_topology_state_reabsorption_supported
```

It may not support by itself:

```text
movement_claim_allowed
adaptive_topology_movement_claim_allowed
topology_mutating_movement_claim_allowed
native_lgrc_choice_selection_claim_allowed
rc_identity_collapse_claim_allowed
agency_claim_allowed
locomotion_like_claim_allowed
identity_acceptance_claim_allowed
```

N04 must rerun the movement ladder after closeout.

Topology-state reabsorption makes post-topology packet work runtime-valid. It
does not by itself make topology-mutating movement valid.
