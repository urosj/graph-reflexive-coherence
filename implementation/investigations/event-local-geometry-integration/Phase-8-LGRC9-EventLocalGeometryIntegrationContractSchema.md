# Phase 8 LGRC9 Event-Local Geometry Integration Contract Schema

**Schema family:** `lgrc9v3_event_local_geometry_integration_v0`
**Status:** Retained prospective schema; not installed or frozen as runtime authority
**Source-change gate:** Closed without runtime change at Iteration 96

## Purpose

Define the minimum default-off policy and record contracts required before
runtime event-local geometry integration may be implemented.

This schema deliberately separates:

```text
causal availability
geometry/current proposal
current realization
packet work
runtime claim status
```

No one record may silently own all five functions.

## Default Flags

```text
event_local_geometry_integration_enabled = false
event_local_geometry_integration_policy = disabled
event_local_geometry_integration_validated = false
event_local_geometry_integration_supported = false
```

Enabled, validated, and supported are distinct.

## Candidate Policies

```text
disabled

event_arrival_dependency_closed_geometry_v1
```

The active policy name may be changed before source modification, but the
following requirements are fixed:

- committed-event trigger;
- causal-availability declaration;
- read/action scope separation;
- pure proposal;
- exactly-once current realization;
- direct-funding preflight;
- generic flux-to-packet mapping;
- event-queue-owned recurrence;
- default-off no-regression.

## Record 1 — Causal Availability

Candidate artifact:

```text
artifact_kind = lgrc9v3_event_local_causal_availability_record
artifact_schema_version = lgrc9v3_event_local_causal_availability_record_v1
```

Minimum fields:

```text
causal_availability_record_id
schema_version
policy_id
trigger_event_id
trigger_packet_id
trigger_node_id
scheduler_event_index
checkpoint_index
event_time_key
trigger_node_proper_time
source_state_digest
available_node_ids
available_edge_ids
available_state_fields
retained_state_sources
causal_path_evidence
excluded_future_event_ids
same_frontier_policy
read_scope_node_ids
read_scope_edge_ids
action_scope_node_ids
action_scope_edge_ids
claim_flags
causal_availability_digest
```

Guards:

- future outcomes cannot be included;
- action scope must be a subset of the permitted scope;
- trigger node must belong to action scope;
- hidden fixture arrays and semantic target labels are rejected;
- record construction mutates no runtime state.

## Record 2 — Geometry/Current Proposal

Candidate artifact:

```text
artifact_kind = lgrc9v3_event_local_geometry_proposal_record
artifact_schema_version = lgrc9v3_event_local_geometry_proposal_record_v1
```

Minimum fields:

```text
proposal_id
schema_version
policy_id
causal_availability_record_id
causal_availability_digest
trigger_event_id
trigger_packet_id
trigger_node_id
source_state_digest
grc_parameter_digest
reconstruction_policy_id
reconstruction_count
proposal_gradient_state
proposal_conductance_state
proposal_potential_state
proposal_flux_state
proposal_choice_annotation
proposal_current_digest
read_scope_node_ids
read_scope_edge_ids
action_scope_node_ids
action_scope_edge_ids
same_frontier_policy
runtime_visible_inputs
claim_flags
proposal_digest
```

Guards:

- proposal construction is pure;
- choice annotation does not authorize packet work;
- proposal flux is derived from declared state and generic rules;
- no fixture-authored winner or route score is accepted;
- digest excludes its own field and is JSON-canonicalized;
- duplicate trigger/policy/source state yields the same idempotency key.

## Record 3 — Current Realization

Candidate artifact:

```text
artifact_kind = lgrc9v3_event_local_current_realization_record
artifact_schema_version = lgrc9v3_event_local_current_realization_record_v1
```

Minimum fields:

```text
current_realization_id
schema_version
policy_id
proposal_id
proposal_digest
source_state_digest
proposal_current_digest
trigger_node_id
action_scope_node_ids
action_scope_edge_ids
integration_policy_id
integration_interval_id
integration_start
integration_end
integration_amount
same_frontier_policy
funding_policy_id
direct_funding_required
direct_funding_available
direct_funding_required_total
funding_disposition
packetization_policy_id
packet_work_ids
status
reason_code
supersedes_current_realization_id
consumed_by_event_ids
claim_flags
current_realization_digest
```

Allowed statuses:

```text
proposed
rejected
eligible
committed
packetized
consumed
superseded
invalidated
```

Required reason-code families:

```text
policy_disabled
causal_scope_invalid
future_input_rejected
source_state_stale
same_frontier_unresolved
integration_interval_invalid
interval_overlap_rejected
duplicate_realization_rejected
direct_funding_passed
direct_funding_failed
packetization_mapping_invalid
action_scope_leak_rejected
committed
packetized
consumed
superseded_by_new_state
invalidated_by_restore_or_policy_change
```

Guards:

- one proposal/interval cannot be packetized twice;
- overlapping intervals for one node/policy fail closed;
- stale proposals cannot commit;
- failed funding schedules no packet;
- packet work remains inside action scope;
- current commitment does not itself mutate coherence;
- only packet departure/arrival mutates the budget.

## Packet Linkage

Every geometry-derived packet record must cite:

```text
source_proposal_id
source_current_realization_id
source_current_realization_digest
integration_interval_id
packetization_policy_id
```

The implementation may extend the existing packet schema or use an associated
producer/authorization record, but replay must reconstruct the relation.

## Idempotency

Minimum keys:

```text
causal availability:
  (policy_id, trigger_event_id, trigger_node_id, source_state_digest)

proposal:
  (policy_id, causal_availability_digest, reconstruction_policy_id)

current realization:
  (policy_id, proposal_digest, integration_interval_id, trigger_node_id)
```

## Snapshot and Restoration

All enabled-mode state that affects later execution must be serialized. The
contract must not depend on untracked in-memory caches.

## Schema Guards

The implementation must reject:

- enabled with disabled policy;
- validated without enabled;
- supported without validated;
- wrong runtime family or level;
- missing trigger/event identity;
- malformed read/action scope;
- future-event input;
- hidden fixture target or score;
- missing source-state digest;
- overlapping current interval;
- stale proposal commitment;
- underfunded partial scheduling;
- claim-promotion fields supplied by producer code;
- packet work without a valid current realization.

## Claim Flags

Default false:

```text
native_event_local_geometry_claim_allowed
native_event_to_current_closure_claim_allowed
native_current_to_packet_claim_allowed
n32_claim_allowed
full_rc_readback_claim_allowed
learning_claim_allowed
semantic_choice_claim_allowed
agency_claim_allowed
ecology_claim_allowed
formative_plurality_claim_allowed
```

## Current Status

This document defines a prospective schema envelope only. Iteration 96 closed
at `C1-SCOPE`, so Iteration 97 did not open, no candidate policy was selected,
and no schema or runtime behavior was installed.
