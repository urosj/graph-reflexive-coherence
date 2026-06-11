# Phase 8 LGRC9 Causal Pulse-Substrate Surface Plan

## Purpose

This document promotes the N04 movement-ladders Lane E result into a Phase 8
native implementation plan.

N03/E3 established native LGRC9V3 self-rearming packet loops. N04 then showed
that existing native LGRC9V3 E3 pulse-contact telemetry can drive an
experiment-local causal pulse-substrate surface that covers:

```text
Lane D-style pulse-substrate deformation
Lane C-style feedback regeneration
```

Lane E passed as a hybrid proof of contract:

```text
hybrid_lgrc_causal_pulse_substrate_surface_contract_supported
native_lgrc_pulse_substrate_supported = false
movement_claim_allowed = false
```

This plan defines the next Phase 8 work:

```text
Add a default-off native causal pulse-substrate surface to LGRC9V3, with
policy-gated producer specializations for pulse-substrate coupling and
feedback-coupled pulse scheduling, while preserving the existing LGRC
producer/step mutation boundary.
```

Companion checklist:

- [`Phase-8-LGRC9-CausalPulseSubstrateChecklist.md`](./Phase-8-LGRC9-CausalPulseSubstrateChecklist.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md)

## Inputs

Primary theory and implementation context:

- [`../papers/2026-05-LGRC-9.md`](../papers/2026-05-LGRC-9.md)
- [`../papers/2026-05-LGRC9V3-Native-Packet-Loops.md`](../papers/2026-05-LGRC9V3-Native-Packet-Loops.md)
- [`../papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md`](../papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md)
- [`../papers/2025-11-RC-IdentityChoiceAbundance.md`](../papers/2025-11-RC-IdentityChoiceAbundance.md)
- [`Phase-8-LGRC9-ImplementationPlan.md`](./Phase-8-LGRC9-ImplementationPlan.md)
- [`Phase-8-LGRC9-ImplementationChecklist.md`](./Phase-8-LGRC9-ImplementationChecklist.md)
- [`Phase-8-LGRC9-NativePacketLoopPlan.md`](./Phase-8-LGRC9-NativePacketLoopPlan.md)
- [`Phase-8-LGRC9-NativePacketLoopChecklist.md`](./Phase-8-LGRC9-NativePacketLoopChecklist.md)

N04 evidence:

- [`../experiments/2026-05-N04-grc9v3-movement-ladders/implementation/MovementLaddersImplementationPlan.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/implementation/MovementLaddersImplementationPlan.md)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/implementation/MovementLaddersImplementationChecklist.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/implementation/MovementLaddersImplementationChecklist.md)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/hybrid_lgrc_pulse_substrate_surface_probe.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/hybrid_lgrc_pulse_substrate_surface_probe.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/hybrid_lgrc_lane_c_feedback_surface_compatibility.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/hybrid_lgrc_lane_c_feedback_surface_compatibility.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/pulse_substrate_movement_reclassification.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/pulse_substrate_movement_reclassification.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/reopened_m6_feedback_gate_report.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/reopened_m6_feedback_gate_report.json)

## Current Boundary

Existing native LGRC9V3 supports:

- packet departure and arrival events;
- route-aspects and D2.3-equivalent native packet loops;
- native surplus-trigger producers;
- native self-rearm evidence;
- node-plus-packet budget audit;
- snapshot/telemetry persistence for packet-loop evidence.

As of Iteration 57, native LGRC9V3 also supports:

- native causal pulse-substrate surface rows;
- native pulse/substrate contact ledger;
- native surface-derived feedback eligibility;
- native pulse-substrate coupling producer;
- native feedback-coupled pulse producer.

Existing native LGRC9V3 does not yet support:

- native M6/self-renewing movement evidence.

This continuation did not add movement. It added an auditable surface that can
later support movement-ladder experiments without bypassing LGRC conservation
or RC identity discipline.

## Scope

In scope:

- native causal pulse-substrate surface contract;
- enabled/validated/supported claim flag separation;
- default-off surface emission policy;
- surface rows linked to committed packet events;
- runtime-visible input declarations for each surface kind;
- explicit separation of:
  - LGRC node-plus-packet conservation budget,
  - derived surface accounting,
  - claim/economy accounting;
- fixed-topology v1 execution, with topology-changing surface rows rejected
  or marked unsupported by an explicit `topology_lineage_deferred` blocker;
- snapshot, telemetry, and replay support;
- artifact-only validators;
- policy-gated pulse-substrate coupling producer;
- policy-gated feedback-coupled pulse producer;
- controls for disabled policy, missing event, pre-event producer,
  subthreshold, wrong polarity, scrambled order, direct-write attempt, and
  budget ambiguity.

Out of scope:

- movement, locomotion-like, biological, agency, or identity acceptance
  claims;
- native M6 support until Lane F controls pass;
- changing synchronous GRC or GRC9V3 proposal-flux semantics;
- adding hidden environment or affordance fields;
- direct support, centroid, displacement, topology, or claim writes by
  producers;
- treating deformation tokens as RC identities;
- making LGRC-0 or LGRC-1 expose this surface;
- implementing LGRC-3 topology-lineage transport for this surface.

## Required LGRC Level

The causal pulse-substrate surface requires LGRC-2 or higher:

```text
packetized causal flux
committed packet departure/arrival events
event queue ordering
node-plus-packet budget invariant
```

The surface schema and policy metadata are defined at all LGRC levels. Surface
row emission and producer evaluation require LGRC-2 or higher and are inert at
LGRC-0/LGRC-1.

In the synchronous GRC reduction limit, the surface is inert: no retained
in-flight packets means no committed packet-contact events and therefore no
surface rows or producer scheduling.

## Runtime Boundary

The existing boundary remains in force:

```text
producer:
    observe committed runtime/surface evidence
    emit evidence records
    optionally schedule work through LGRC scheduling

step():
    consume queued events and mutate coherence/packet budget
```

Producers must never:

```text
debit or credit coherence
write support masks
write centroid or displacement
change topology
mark a packet departure as processed
emit claim labels or claim promotion decisions
```

Claims belong to validators and reports, not runtime producers.

## Native Surface Contract

Minimum native row fields:

```text
surface_id
schema_version
lgrc_runtime_level
surface_policy_id
surface_policy_enabled
route_aspect_id
route_aspect_digest
pulse_event_id
pulse_packet_id
pulse_event_kind
pulse_channel_id
pulse_route_step
event_time_key
scheduler_event_index
node_proper_time
source_node_id
target_node_id
contact_amount
surface_state_id
surface_state_digest
surface_kind
surface_nodes
surface_values_before
surface_values_after
surface_update_policy
surface_budget_surface
surface_budget_before
surface_budget_after
surface_budget_error
lineage_status
producer_records
claim_flags
surface_digest
```

Native surface v1 rows require `lgrc_runtime_level = lgrc2|lgrc3`;
construction below LGRC-2 is invalid because committed packet events do not
exist there.

The surface policy is the serialized activation gate controlling whether
surface rows are emitted and whether producer specializations evaluate
eligibility. When policy is disabled, the surface is inert: no rows are
emitted and no producers run. When policy is enabled, surface rows are emitted
from committed packet events and producers may evaluate eligibility according
to their own producer policies. Policy state is serialized as:

```text
surface_policy_id
surface_policy_enabled
```

The row-level `surface_update_policy` is a serialized policy object with:

```text
policy_id
version
activation_gate
allowed_surface_kinds
```

The policy must allow the row's `surface_kind`; malformed policies fail schema
validation.

Surface row emission must be idempotent. A committed packet event may generate
at most one surface row per surface policy and surface kind unless the policy
explicitly declares a multi-row decomposition. Implementations should use a
stable idempotency key, for example:

```text
(source_event_id, surface_policy_id, surface_kind, route_aspect_digest)
```

Each `surface_kind` must declare runtime-visible inputs:

| Surface kind | Inputs |
|---|---|
| `local_support_mass` | Sum of $C_i$ over declared support mask. |
| `boundary_polarity_score` | Front/rear mass aggregates over declared masks. |
| `proper_time_phase` | Node proper time $\tau_i$ at contact nodes or masks. |
| `surface_deformation` | Declared function of serialized runtime fields. |
| `route_local_pulse_contact` | Packet contact amount and route/channel fields. |
| `feedback_eligibility` | Declared surface values, references, thresholds, polarity policy. |

Hidden fixture arrays, preauthored itineraries, and post-hoc movement labels
are not valid runtime inputs.

Budget accounting is split at schema level. A surface row may record the LGRC
node-plus-packet budget context and a derived `surface_budget_surface`, but it
must not merge those accounting surfaces into one ambiguous budget field.

Producer-writable fields are limited to producer evidence and scheduling
eligibility records. System-only fields include runtime level, schema/policy
ids, event references, surface values, budget fields, lineage status, claim
flags, and digests. Producers may not write system-only fields or promote
claims.

The canonical `surface_digest` is SHA-256 over JSON-canonicalized row content
excluding `surface_digest` itself.

## Claim Flags

Use separate enabled, validated, and supported flags:

```text
native_causal_pulse_substrate_surface_enabled
native_causal_pulse_substrate_surface_validated
native_pulse_substrate_coupling_producer_enabled
native_pulse_substrate_coupling_producer_validated
native_feedback_coupled_pulse_producer_enabled
native_feedback_coupled_pulse_producer_validated
native_lgrc_pulse_substrate_supported
native_m6
movement_claim_allowed
loop_driven_movement_claim_allowed
locomotion_like_claim_allowed
adaptive_topology_entry_allowed
biological_claim_allowed
agency_claim_allowed
identity_acceptance_claim_allowed
```

Enabling the surface does not imply support. Support requires schema,
ordering, budget, snapshot/replay, and negative-control validators.

## Iteration Map

### Iteration 50. Baseline Freeze

Freeze post-native-packet-loop LGRC9V3 behavior and N04 Lane E evidence before
adding native surface code.

### Iteration 51. Native Surface Contract

Add serializable native surface schema, policy, digests, enabled/validated
flags, runtime-visible input declarations, and default-off behavior.

### Iteration 52. Surface Emission From Committed Packet Events

Emit surface rows only after committed packet events. Verify ordering,
proper-time/event-time evidence, budget-surface separation, and no producer
mutation.

### Iteration 53. Snapshot, Telemetry, And Replay

Persist and reload surface rows without duplication. Add artifact-only
validators.

### Iteration 54. Pulse-Substrate Coupling Producer

Add default-off coupling producer specialization. It may observe surface rows
and schedule work through LGRC scheduling, but may not mutate coherence or
emit claims.

### Iteration 55. Feedback-Coupled Pulse Producer

Add default-off feedback producer specialization for Lane C-style feedback
eligibility. It must read committed surface rows and schedule only through
LGRC scheduling.

### Iteration 56. Controls And N04 Lane F Bridge

Run controls, prove old behavior unchanged, verify fixed-topology behavior,
and generate N04 Lane F native surface evidence without movement/agency claim
promotion. Topology-changing surface execution is deferred in v1 and must fail
closed with `topology_lineage_deferred`.

### Iteration 57. Closeout

Close the native pulse-substrate surface continuation only if artifact-only
validators reproduce the classifications and all claim boundaries are clean.

Note: the main Phase 8 continuation gate map should be kept in sync with this
continuation surface. It records the native causal pulse-substrate surface as
the post-native-packet-loop LGRC-2 specialization and should be updated at
Iteration 57 closeout if the support status changes.

## Acceptance Statement

This continuation is complete only if:

```text
LGRC9V3 exposes a default-off native causal pulse-substrate surface whose rows
are emitted only from committed packet events, preserve event/proper-time
ordering, declare runtime-visible inputs, separate physical packet conservation
from derived accounting surfaces, survive snapshot/telemetry round-trip, and
can be validated from artifacts alone. Coupling and feedback producers are
policy-gated scheduling specializations that emit evidence and schedule work
only through LGRC surfaces; they never mutate coherence or emit claims. Existing
packet-loop, static-route, snapshot, telemetry, topology, spark, and GRC9V3
behavior remains compatible. Native movement, M6, locomotion-like, agency,
biology, and identity-acceptance claims remain blocked unless later experiment
validators independently open them.
```
