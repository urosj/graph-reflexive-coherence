# Phase 8 LGRC9 Causal Pulse-Substrate Surface Lineage Plan

## Purpose

This document defines the Phase 8 continuation opened by N04 Iteration 19-B.

LGRC9V3 already has both prerequisite halves:

```text
LGRC-3 topology/lineage machinery:
    topology events, lineage maps, budget-conserving collapse/reabsorption,
    packet transport through topology lineage, proper-time inheritance, and
    replay validation.

Phase 8 causal pulse-substrate surface:
    native packet-contact surface rows, coupling producer, feedback producer,
    artifact-only packet/surface/producer validation, and fixed-topology
    surface evidence.
```

The missing bridge is:

```text
native causal pulse-substrate surface lineage transport
```

N04 Iteration 19-B found the exact blocker:

```text
causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status
```

This continuation adds a conservative mechanism for transporting or
superseding causal pulse-substrate surface evidence across committed LGRC-3
topology events. It does not add topology change from scratch and does not add
packet scheduling from scratch.

Companion checklist:

- [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md)

## Inputs

Theory and implementation context:

- [`../papers/2026-05-LGRC-9.md`](../papers/2026-05-LGRC-9.md)
- [`../papers/2026-05-LGRC9V3-Native-Packet-Loops.md`](../papers/2026-05-LGRC9V3-Native-Packet-Loops.md)
- [`../papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md`](../papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md)
- [`Phase-8-LGRC9-CausalPulseSubstratePlan.md`](./Phase-8-LGRC9-CausalPulseSubstratePlan.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateChecklist.md`](./Phase-8-LGRC9-CausalPulseSubstrateChecklist.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md)

N04 boundary evidence:

- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19b_topology_lineage_adaptive_gate_report.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19b_topology_lineage_adaptive_gate_report.md)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_continuation_closeout.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_continuation_closeout.md)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/implementation/MovementLaddersHandoff.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/implementation/MovementLaddersHandoff.md)

## Current Boundary

Supported today:

- LGRC-3 topology event replay with lineage continuity and budget
  conservation;
- fixed-topology causal pulse-substrate surface rows;
- fixed-topology coupling and feedback producers;
- artifact-only validation of packet event -> surface row -> producer record
  -> scheduled packet -> processed packet chains.

Blocked today:

- causal pulse-substrate surface rows with non-fixed lineage status;
- transported or superseded surface evidence after topology events;
- producer stale-read prevention after topology changes;
- adaptive topology entry in N04.

The current N04 ceiling remains:

```text
s7_fixed_port_composed_gate_candidate
```

## Scope

In scope:

- new surface lineage statuses or companion records for:
  - fixed-topology current rows;
  - rows superseded by committed topology events;
  - rows transported/rebased through topology lineage;
- surface lineage transport/supersession records linked to committed topology
  events;
- artifact-only validation of:

```text
packet event
-> original surface row
-> topology event
-> surface lineage transport or supersession record
-> transported surface row or blocked stale row
-> producer record, if eligible
```

- producer rules that reject stale pre-topology rows;
- snapshot and telemetry persistence for lineage transport evidence;
- duplicate suppression for transported/superseded rows;
- negative controls for missing topology event, missing lineage map, budget
  mismatch, direct rewrite, stale producer read, and topology-only claim
  promotion.

Out of scope:

- adding LGRC-3 topology change from scratch;
- adding packet scheduling, coupling producer, or feedback producer from
  scratch;
- movement, adaptive topology movement, locomotion-like behavior, choice,
  agency, biological, or identity-acceptance claims;
- native RC identity collapse or semantic branch choice;
- allowing producers to mutate coherence, support masks, centroid,
  displacement, topology, or claim flags.

## Mechanism

The core mechanism is not a boolean flag. The flag is only a default-off policy
gate.

Required mechanism:

```text
old surface row
    + committed LGRC-3 topology event
    + lineage transfer map
    -> transported surface row
```

or:

```text
old surface row
    + committed LGRC-3 topology event
    + lineage transfer map
    -> supersession record
```

Transported means the old evidence has a valid successor surface after the
topology event.

Superseded means the old evidence is no longer current and producers must not
read it for scheduling eligibility.

Minimum transport/supersession artifact fields:

```text
surface_lineage_record_id
schema_version
source_surface_id
source_surface_digest
topology_event_id
topology_event_kind
topology_event_digest
event_time_key
scheduler_event_index
checkpoint_index
lineage_transfer_map
source_surface_nodes
target_surface_nodes
source_surface_ports
target_surface_ports
lineage_action = transported | superseded
surface_budget_surface
surface_budget_before
surface_budget_after
surface_budget_error
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
transported_surface_id
transported_surface_digest
superseded_surface_id
producer_stale_read_blocker
claim_flags
lineage_record_digest
```

Lineage records use a separate idempotency surface from ordinary surface rows.
The canonical lineage idempotency key is the SHA-256 digest of:

```text
source_surface_digest
topology_event_digest
surface_lineage_policy_id
lineage_action
lineage_transfer_map_digest
```

This suppresses duplicate transport/supersession records for the same committed
surface/topology/policy action while still allowing explicitly different
declared lineage maps or policies to be rejected or compared by validators. A
weaker key such as `source_surface_id` alone is not sufficient.

`topology_event_digest` is a canonical derived digest when the source topology
event artifact does not already serialize a digest field. It is computed as
SHA-256 over JSON-canonicalized topology event artifact content, excluding any
digest field being computed. Iteration 59 must add the helper and artifact
field without changing existing topology event semantics.

`source_surface_ports` and `target_surface_ports` are optional, kind-specific
fields. They are required only for surface kinds that declare port-local state
or port-graph/nine-port inputs. Non-port surface kinds must serialize these as
empty arrays or `null` under the v1 schema and may not infer hidden ports.

Lineage status vocabulary is frozen as:

```text
fixed_topology
topology_lineage_deferred
transported_topology_lineage
superseded_by_topology_event
```

The lineage action enum remains:

```text
transported
superseded
```

Existing fixed-topology v1 rows remain valid only with `fixed_topology`; new
transported or superseded evidence must be emitted as lineage-aware companion
records or v2 transported rows, not by weakening v1 validation.

Lineage transport is LGRC-3-only. Enabling surface lineage transport requires:

```text
lgrc_runtime_level == lgrc3
causal_layer_mode == topology_changing_causal_history
```

Construction or execution below LGRC-3 must fail closed with a distinct
`surface_lineage_transport_requires_lgrc3` blocker.

## Producer Rule

Current producer rule:

```text
read committed surface row
```

New producer rule:

```text
read committed surface row only if:
    no later committed topology event supersedes it
    or a transported successor row exists after that topology event
```

This prevents producers from scheduling work from stale pre-topology evidence.

## Budget Rule

The continuation must keep three accounting surfaces distinct:

```text
LGRC node-plus-packet budget:
    runtime conservation surface.

Derived surface accounting:
    declared pulse-substrate surface values before/after lineage transport.

Claim/economy accounting:
    experiment-level movement taxonomy cost interpretation.
```

Conservation of one surface does not imply claim validity on another. A
budget-ambiguous lineage record must fail closed.

## Claim Boundary

This continuation may support:

```text
native_causal_pulse_substrate_surface_lineage_transport_supported
```

It may not support by itself:

```text
movement
adaptive topology movement
topology-mutating movement
native LGRC choice selection
RC identity collapse
semantic choice
agency
locomotion-like behavior
biological behavior
identity acceptance
unrestricted movement
```

Those claims remain N04 validator responsibilities after Phase 8 closeout.

## Iteration Plan

Iteration 58: baseline freeze for surface-lineage continuation.

Iteration 59: schema and policy extension for surface lineage transport and
supersession records.

Iteration 60: emit supersession records after committed topology events.

Iteration 61: emit transported surface rows through explicit lineage maps.

Iteration 62: artifact-only lineage replay validator.

Iteration 63: producer stale-read prevention and transported-row eligibility.

Iteration 64: snapshot, telemetry, controls, and compatibility sweep.

Iteration 65: closeout and N04 Iteration 19-C handoff.

## Acceptance Criteria

This continuation is accepted when:

- default-off behavior preserves all existing LGRC9V3 tests;
- old fixed-topology causal pulse-substrate surface behavior remains unchanged;
- committed topology events can supersede surface rows;
- committed topology events can transport/rebase surface rows through explicit
  lineage maps when policy allows;
- producers cannot read stale pre-topology surface rows;
- artifact-only validators reconstruct the full packet/surface/topology/
  transported-surface/producer chain;
- snapshot and telemetry round-trip lineage transport evidence;
- controls fail closed with distinct blockers;
- runtime producers still emit evidence and schedule work only;
- movement, adaptive topology, choice, agency, and identity claims remain
  blocked by Phase 8 closeout;
- N04 handoff points back to Iteration 19-C.
