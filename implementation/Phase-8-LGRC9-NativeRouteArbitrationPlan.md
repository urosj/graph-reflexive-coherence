# Phase 8 LGRC9 Native Route Arbitration Plan

Status: Closed.

This continuation is opened by N04 Iteration 21. Iteration 21 showed that
multiple topology-mutating continuations can each execute and artifact-replay
when supplied, but LGRC9V3 does not yet expose a native mechanism that forms a
competing route set and arbitrates one route from runtime-visible evidence.

The recorded N04 blocker is:

```text
native_lgrc_topology_route_selection_not_exposed
```

Companion checklist:

- [`Phase-8-LGRC9-NativeRouteArbitrationChecklist.md`](./Phase-8-LGRC9-NativeRouteArbitrationChecklist.md)

## Goal

Add default-off native route arbitration for LGRC-3 topology-mutating work:

```text
committed runtime evidence
-> candidate topology-route set
-> native route-arbitration record
-> selected topology event
-> surface lineage transport/supersession
-> topology-state reabsorption
-> producer scheduling from lineage-current reabsorbed state
```

The mechanism should let N04 rerun Iteration 21 as a native route-arbitration
probe without experiment-side `if/else` route selection or preselected
`selected_sink_id` being the causal source of the route.

## Non-Goals

- Do not claim semantic choice.
- Do not claim agency.
- Do not claim RC identity collapse or identity acceptance.
- Do not claim locomotion-like or biological behavior.
- Do not promote general movement or unrestricted movement claims.
- Do not let producers directly mutate coherence, packet ledger, topology, or
  claim flags.
- Do not weaken surface-lineage, topology-state reabsorption, or
  node-plus-packet budget invariants.

This continuation may support a runtime capability named:

```text
native_lgrc_route_arbitration_supported
```

but that means native route arbitration support only. It does not mean native
choice, semantic choice, agency, or RC identity collapse.

## Inputs

Phase 8 inputs:

- [`Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md)
- [`Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`](./Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md)
- [`Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md`](./Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md)

N04 boundary evidence:

- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter21_native_lgrc_choice_selection_boundary.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter21_native_lgrc_choice_selection_boundary.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter21_native_lgrc_choice_selection_boundary.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter21_native_lgrc_choice_selection_boundary.md)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22_identity_through_topology_mutation_boundary.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22_identity_through_topology_mutation_boundary.json)
- [`../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter22_identity_through_topology_mutation_boundary.md`](../experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter22_identity_through_topology_mutation_boundary.md)

## Current Boundary

Supported today:

- native causal pulse-substrate surface rows from committed packet events;
- coupling and feedback producers over committed surface evidence;
- LGRC-3 surface lineage transport/supersession;
- topology-state reabsorption of active state and packet ledger;
- time-scoped artifact replay for multiple topology events;
- N04 `topology_mutating_movement_candidate`.

Blocked today:

- native construction of a competing route set;
- native route arbitration among multiple valid topology-mutating candidates;
- selected topology-event provenance from a native route-arbitration record;
- artifact-only replay of:

```text
candidate route set
-> route-arbitration record
-> selected topology event
-> lineage/reabsorption
-> producer/scheduled packet chain
```

The N04 ceiling before and after this continuation remains:

```text
topology_mutating_movement_candidate
```

## Closeout

Closeout artifacts:

- [`Phase-8-LGRC9-NativeRouteArbitrationCloseout.md`](./Phase-8-LGRC9-NativeRouteArbitrationCloseout.md)
- [`Phase-8-LGRC9-NativeRouteArbitrationCloseout.json`](./Phase-8-LGRC9-NativeRouteArbitrationCloseout.json)

Closed support capability:

```text
native_lgrc_route_arbitration_supported = true
```

This is runtime route-arbitration support only. Native choice, semantic choice,
agency, RC identity collapse, identity acceptance, locomotion-like behavior,
biological behavior, unrestricted movement, and claim-promotion flags remain
blocked until N04 reruns and separately validates them.

Return target:

```text
N04 Iteration 21-B: native LGRC route-arbitration rerun
```

## Mechanism

The new mechanism is a default-off LGRC-3 route-arbitration surface.

It has three core artifacts.

### Candidate Route Record

A candidate route record serializes one possible topology-mutating
continuation before arbitration. Minimum fields:

```text
candidate_route_id
schema_version
native_route_arbitration_policy_id
candidate_set_id
candidate_source_surface_digest
candidate_source_producer_record_id, if any
candidate_source_topology_state_reabsorption_digest, if any
route_intent = collapse | reabsorb | split | merge | redirect
candidate_topology_event_kind
candidate_competing_sink_ids
candidate_losing_sink_ids
candidate_selected_sink_id
candidate_transferred_node_ids
candidate_lineage_transfer_map
candidate_source_node_ids
candidate_target_node_ids
candidate_retired_node_ids
candidate_source_edge_ids
candidate_target_edge_ids
candidate_retired_edge_ids
candidate_route_score
candidate_score_components
candidate_budget_prediction
candidate_order_key
candidate_runtime_visible_inputs
claim_flags
candidate_route_digest
```

`candidate_selected_sink_id` is a candidate field, not the selected route for
the run. The selected route is determined only by the route-arbitration record.

Candidate scores must be computed from serialized policy parameters and
runtime-visible evidence. Hidden fixture arrays, report code, or experiment
`if/else` logic may not be the source of route selection.

### Candidate Set Record

A candidate set record groups competing candidate routes observed in the same
arbitration window. Minimum fields:

```text
candidate_set_id
schema_version
native_route_arbitration_policy_id
arbitration_window_id
event_time_key
scheduler_event_index
candidate_route_digests
candidate_set_digest
candidate_set_order_key
unresolved_tie_policy
claim_flags
```

The candidate set idempotency key is the SHA-256 digest over:

```text
native_route_arbitration_policy_id
arbitration_window_id
event_time_key
candidate_route_digests
candidate_set_order_key
```

### Native Route-Arbitration Record

A route-arbitration record is the only artifact that can authorize committing one
candidate route as the selected topology event. Minimum fields:

```text
native_route_arbitration_record_id
schema_version
native_route_arbitration_policy_id
candidate_set_id
candidate_set_digest
selected_candidate_route_id
selected_candidate_route_digest
rejected_candidate_route_digests
arbitration_reason_code
arbitration_score
arbitration_rule
arbitration_runtime_visible_inputs
selected_topology_event_id
selected_topology_event_digest, if committed
event_time_key
scheduler_event_index
claim_flags
native_route_arbitration_digest
```

Valid reason codes:

```text
native_route_arbitration_selected_highest_score
native_route_arbitration_selected_declared_local_preference
native_route_arbitration_no_candidates
native_route_arbitration_unresolved_tie
native_route_arbitration_policy_disabled
native_route_arbitration_budget_invalid
native_route_arbitration_order_invalid
native_route_arbitration_hidden_input_rejected
```

Unresolved ties fail closed unless the serialized policy declares a
deterministic tie-breaker from runtime-visible candidate fields. A deterministic
tie-breaker is route arbitration, not semantic choice or agency.

## Policy Flags

Default baseline:

```text
native_lgrc_route_arbitration_enabled = false
native_lgrc_route_arbitration_policy = disabled
native_lgrc_route_arbitration_validated = false
native_lgrc_route_arbitration_supported = false
```

Claim flags remain false unless N04 validators separately prove them:

```text
semantic_choice_claim_allowed = false
agency_claim_allowed = false
rc_identity_collapse_claim_allowed = false
identity_acceptance_claim_allowed = false
locomotion_like_claim_allowed = false
biological_claim_allowed = false
unrestricted_movement_claim_allowed = false
```

Enabled does not imply validated. Validated does not imply semantic choice or
agency.

## Iteration Plan

### Iteration 76. Baseline Freeze

Freeze the N04 Iteration 21 blocker and current runtime behavior.

Acceptance:

- record `native_lgrc_topology_route_selection_not_exposed`;
- confirm Iteration 20 and 21 artifacts still pass;
- confirm Iteration 22 identity boundary remains blocked;
- confirm native route-arbitration flags are absent or false;
- confirm current focused LGRC9V3, topology-state reabsorption,
  surface-lineage, telemetry, and diff checks.

### Iteration 77. Contract And Policy Schema

Add default-off native route-arbitration schema and policy support.

Acceptance:

- add policy flags;
- add candidate route, candidate set, and route-arbitration record schemas;
- add canonical digest helpers and idempotency keys;
- reject construction below LGRC-3 when enabled;
- reject hidden-input, claim-promotion, missing-budget, and malformed route
  records;
- confirm JSON round-trip and digest stability.

### Iteration 78. Candidate Route Set Emission

Emit candidate route records and candidate set records from runtime-visible
evidence.

Acceptance:

- candidate set emission is default-off;
- candidate sources cite committed surface/producers/reabsorption evidence;
- route scores and score components are serialized;
- duplicate candidate records are suppressed;
- candidate set ordering is deterministic;
- hidden fixture route selection is rejected.

### Iteration 79. Native Route Arbitration

Select one candidate route through serialized policy.

Acceptance:

- selected route comes from a route-arbitration record, not experiment-side `if/else`;
- unresolved tie fails closed unless declared policy provides deterministic
  runtime-visible tie-breaker;
- rejected candidates remain auditable;
- route-arbitration record authorizes exactly one selected topology event;
- budget/order-invalid candidates fail with distinct blockers.

### Iteration 80. Commit Selected Topology Event And Producers

Integrate selection with existing topology event, surface lineage,
topology-state reabsorption, and producer scheduling.

Acceptance:

- selected topology event references the route-arbitration record;
- surface lineage and topology-state reabsorption consume the selected event;
- producers schedule only from lineage-current, reabsorbed state;
- no producer mutates coherence, packet ledger, topology, or claims;
- node-plus-packet budget remains exact.

### Iteration 81. Snapshot, Telemetry, Artifact Replay, Controls

Persist and validate native route-arbitration artifacts.

Acceptance:

- snapshot/load preserves candidate sets, route-arbitration records, and idempotency
  keys;
- telemetry exports route-arbitration artifacts only when policy is enabled;
- artifact-only validator reconstructs:

```text
candidate set
-> route-arbitration record
-> selected topology event
-> surface lineage
-> topology-state reabsorption
-> producer record
-> scheduled/processed packet
```

- negative controls fail with distinct blockers:
  disabled policy, no candidates, unresolved tie, hidden input, budget
  mismatch, order inversion, duplicate arbitration, stale state, direct rewrite,
  and claim promotion.

### Iteration 82. Closeout And N04 Return

Close the continuation and return to N04.

Acceptance:

- focused runtime, topology, packet-loop, surface-lineage, topology-state
  reabsorption, snapshot, telemetry, and artifact-replay tests pass;
- support flag may become true only if positive and negative validators pass;
- semantic choice, agency, RC identity collapse, identity acceptance,
  locomotion-like, biological, and unrestricted movement claims remain false;
- N04 reruns Iteration 21 as the next evidence step.

Return target:

```text
N04 Iteration 21-B: native LGRC route-arbitration rerun
```
