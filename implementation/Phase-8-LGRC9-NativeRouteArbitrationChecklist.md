# Phase 8 LGRC9 Native Route Arbitration Checklist

This checklist tracks the Phase 8 continuation for:

- [`Phase-8-LGRC9-NativeRouteArbitrationPlan.md`](./Phase-8-LGRC9-NativeRouteArbitrationPlan.md)

The task is to add default-off native route arbitration for LGRC-3
topology-mutating candidate routes. This is runtime route selection from
serialized, runtime-visible candidate evidence. It is not semantic choice,
agency, RC identity collapse, or identity acceptance.

## Ground Rules

- This is an LGRC9V3 implementation continuation using LGRC-3 semantics.
- It consumes native causal pulse-substrate surfaces, surface lineage
  transport, topology-state reabsorption, and time-scoped lineage replay.
- Preserve default-off behavior.
- Preserve fixed-topology LGRC-2 packet validation.
- Preserve existing topology-state reabsorption and surface-lineage invariants.
- Route arbitration may authorize exactly one selected topology event from a
  declared candidate set.
- Candidate scores and tie-breakers must be computed only from serialized
  policy fields and runtime-visible evidence.
- Hidden fixture arrays, experiment-level `if/else` route choice, report code,
  and post-hoc threshold changes must be rejected as native route-arbitration
  evidence.
- Producers still observe, record, and schedule; `step()` or topology
  transition machinery owns mutation.
- Producers must not write coherence, packet ledger, support masks, centroid,
  displacement, topology, route-arbitration records, or claim flags.
- Node-plus-packet budget must remain exact.
- Movement, semantic choice, agency, RC identity collapse, identity acceptance,
  locomotion-like, biological, and unrestricted movement claims remain blocked
  until N04 validators separately rerun and pass.

## Iteration 76. Baseline Freeze

Status: passed.

### Goal

Freeze current behavior before native route-arbitration source changes.

### Checks

- [x] Record N04 Iteration 21 boundary:

```text
primary_blocker = native_lgrc_topology_route_selection_not_exposed
```

- [x] Confirm N04 current ceiling remains:

```text
topology_mutating_movement_candidate
```

- [x] Confirm Iteration 20 repeatability/stress artifacts still pass.
- [x] Confirm Iteration 21 route candidates are executable only when supplied.
- [x] Confirm Iteration 22 identity-through-topology remains blocked at:

```text
rc_identity_basin_invariance_not_validated_across_topology_mutation
```

- [x] Confirm native route-arbitration flags are absent or false:

```text
native_lgrc_route_arbitration_enabled = false
native_lgrc_route_arbitration_validated = false
native_lgrc_route_arbitration_supported = false
```

- [x] Run focused LGRC9V3 runtime, surface-lineage, topology-state
  reabsorption, snapshot, telemetry, and diff checks.

### Artifacts

- [`Phase-8-LGRC9-NativeRouteArbitrationBaselineFreeze.json`](./Phase-8-LGRC9-NativeRouteArbitrationBaselineFreeze.json)
- [`Phase-8-LGRC9-NativeRouteArbitrationBaselineFreeze.md`](./Phase-8-LGRC9-NativeRouteArbitrationBaselineFreeze.md)

### Verification

```text
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter20_topology_mutating_repeatability_stress.py
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter21_native_lgrc_choice_selection_boundary.py
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter22_identity_through_topology_mutation_boundary.py
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
git diff --check
```

Result:

```text
N04 scripts passed
3 passed, 109 deselected
git diff --check passed
```

## Iteration 77. Contract And Policy Schema

Status: passed.

### Goal

Add default-off native route-arbitration schema and policy support.

### Checks

- [x] Add default-off policy flags:

```text
native_lgrc_route_arbitration_enabled
native_lgrc_route_arbitration_policy
native_lgrc_route_arbitration_validated
native_lgrc_route_arbitration_supported
```

- [x] Add serializable candidate route records.
- [x] Add serializable candidate set records.
- [x] Add serializable native route-arbitration records.
- [x] Add canonical digest helpers for all three artifact types.
- [x] Add idempotency keys for candidate sets and arbitration records.
- [x] Reject construction below LGRC-3 when enabled.
- [x] Reject hidden-input candidate scores or undeclared score components.
- [x] Reject missing budget predictions, malformed lineage maps, and malformed
  route topology fields.
- [x] Reject claim-promotion fields in all route-arbitration artifacts.
- [x] Add JSON round-trip and digest stability tests.
- [x] Confirm fixed-topology and default-off behavior remains compatible.

### Artifacts

- [`Phase-8-LGRC9-NativeRouteArbitrationContractSchema.json`](./Phase-8-LGRC9-NativeRouteArbitrationContractSchema.json)
- [`Phase-8-LGRC9-NativeRouteArbitrationContractSchema.md`](./Phase-8-LGRC9-NativeRouteArbitrationContractSchema.md)

### Implementation Notes

- Added default-off causal mode flags:

```text
native_lgrc_route_arbitration_enabled = false
native_lgrc_route_arbitration_policy = disabled
native_lgrc_route_arbitration_validated = false
native_lgrc_route_arbitration_supported = false
```

- Added `LGRC9V3NativeRouteCandidateRecord`,
  `LGRC9V3NativeRouteCandidateSetRecord`, and
  `LGRC9V3NativeRouteArbitrationRecord`.
- Added canonical digest helpers and restore helpers for all three artifact
  types.
- Candidate sets and arbitration records carry canonical idempotency keys.
- Candidate-set route digests are ordered by a declared order key
  (`score_desc_then_candidate_id` or `digest_ascending`); `digest_ascending`
  records must serialize sorted digests.
- Unresolved tie policy is explicit (`fail_closed` or
  `declared_runtime_visible_tiebreaker`); accidental list-order selection is
  not valid native route arbitration.
- Contract construction rejects sub-LGRC-3 enabled contexts, hidden inputs,
  malformed lineage maps, missing/ambiguous budget prediction, duplicate
  candidate-set digests, malformed selected-route records, and claim
  promotion.
- The schema layer does not emit candidate sets, select routes, commit topology
  events, schedule packets, or mutate state.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
123 passed, 59 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
13 passed, 222 deselected, 20 subtests passed

git diff --check
passed
```

## Iteration 78. Candidate Route Set Emission

Status: passed.

### Goal

Emit candidate route and candidate set records from runtime-visible evidence.

### Checks

- [x] Candidate emission is default-off.
- [x] Candidate routes cite committed source evidence:
  - [x] source surface digest;
  - [x] source producer record id or linkage fields, if any;
  - [x] topology-state reabsorption digest, if any;
  - [x] runtime-visible policy id.
- [x] Candidate route scores and score components are serialized.
- [x] Candidate set includes every candidate in the arbitration window.
- [x] Candidate set ordering is deterministic.
- [x] Duplicate candidate route records are suppressed.
- [x] Hidden fixture route selection is rejected with a distinct blocker.
- [x] No topology event is committed by candidate emission alone.

### Artifacts

- `Phase-8-LGRC9-NativeRouteArbitrationCandidateEmission.json`
- `Phase-8-LGRC9-NativeRouteArbitrationCandidateEmission.md`

### Implementation Notes

- Added `LGRC9V3.emit_native_route_candidate_set(...)`.
- Candidate emission is gated by
  `native_lgrc_route_arbitration_enabled=true` and
  `native_lgrc_route_arbitration_policy=score_ordered_topology_route_candidates`.
- Runtime state now serializes `native_route_candidate_log` and
  `native_route_candidate_set_log`.
- Candidate records require committed source surface evidence and serialize
  score components, budget prediction, lineage map, runtime-visible inputs,
  and the route-arbitration policy id.
- Candidate budget prediction is explicit and mandatory; missing budget
  prediction fails with `native_route_arbitration_budget_invalid`.
- Partial lineage maps, experiment `if/else` provenance, and preselected-sink
  provenance fail closed before candidate logs are emitted.
- Candidate sets serialize ordered route digests under a declared deterministic
  order key.
- Duplicate candidate route records and candidate sets are suppressed by
  digest/idempotency caches.
- Hidden fixture/report/if-else inputs fail with
  `native_route_arbitration_hidden_input_rejected`.
- The emitter does not arbitrate, commit topology events, schedule packets, or
  mutate coherence/packet/topology state.
- `candidate_selected_sink_id` is candidate-local proposed topology payload
  only. Run selection requires a native route-arbitration record in Iteration
  79.
- Producer linkage is serialized when supplied; current producer records do not
  include a canonical `producer_record_digest`, so Iteration 78 does not claim
  producer-record digest validation.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_candidate"
12 passed, 112 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
25 passed, 222 deselected, 20 subtests passed

git diff --check
passed
```

## Iteration 79. Native Route Arbitration

Status: passed.

### Goal

Select one candidate route through serialized runtime policy.

### Checks

- [x] Route arbitration is default-off.
- [x] Selected route comes from a native route-arbitration record.
- [x] Experiment-side `if/else` route selection cannot satisfy the native
  route-arbitration gate.
- [x] Rejected candidates remain auditable.
- [x] Selection is replayable from serialized score, rule, rejected digests,
  and runtime-visible inputs.
- [x] No-candidate arbitration fails closed with
  `native_route_arbitration_no_candidates`.
- [x] Unresolved tie fails closed unless the serialized policy declares a
  deterministic runtime-visible tie-breaker.
- [x] Budget-invalid candidates fail with
  `native_route_arbitration_budget_invalid`.
- [x] Order-invalid candidates fail with
  `native_route_arbitration_order_invalid`.
- [x] Hidden-input candidates fail with
  `native_route_arbitration_hidden_input_rejected`.
- [x] The route-arbitration record authorizes exactly one selected topology
  event.
- [x] Duplicate arbitration over the same candidate set is idempotent and does
  not duplicate route-arbitration log records.
- [x] Semantic choice, agency, and identity claims remain false.

### Artifacts

- `Phase-8-LGRC9-NativeRouteArbitrationSelection.json`
- `Phase-8-LGRC9-NativeRouteArbitrationSelection.md`

### Implementation Notes

- Added `LGRC9V3.arbitrate_native_route_candidate_set(...)`.
- Arbitration is gated by
  `native_lgrc_route_arbitration_enabled=true` and
  `native_lgrc_route_arbitration_policy=score_ordered_topology_route_candidates`.
- Runtime state now serializes `native_route_arbitration_log`.
- Arbitration requires a committed candidate set and committed candidate route
  records.
- Highest-score selection emits
  `native_route_arbitration_selected_highest_score`.
- Selection records are replayable from the committed candidate-set digest,
  selected digest, rejected digests, score, rule, and runtime-visible inputs.
- Rejected candidate route digests remain serialized and auditable.
- Empty candidate sets fail closed with
  `native_route_arbitration_no_candidates`.
- Unresolved ties fail closed with `native_route_arbitration_unresolved_tie`
  unless the candidate set declares a deterministic runtime-visible
  tie-breaker.
- Declared tie-breaker selection emits
  `native_route_arbitration_selected_declared_local_preference`.
- Hidden arbitration provenance, budget-invalid candidate records, and
  order-invalid candidate sets fail closed with distinct reason codes.
- Selected records serialize exactly one selected topology event id and digest.
  The selected topology event is authorized, not committed. Commit is deferred
  to Iteration 80.
- Replaying the same candidate-set arbitration hits the canonical idempotency
  key and does not append a duplicate route-arbitration log record.
- The arbitration method does not emit candidate sets, commit topology events,
  schedule packets, mutate coherence/packet/topology state, or promote claims.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_arbitration"
10 passed, 124 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
35 passed, 222 deselected, 20 subtests passed

git diff --check
passed
```

## Iteration 80. Commit Selected Topology Event And Producers

Status: passed.

### Goal

Integrate route arbitration with committed topology events, surface lineage,
topology-state reabsorption, and producer scheduling.

### Checks

- [x] Selected topology event references the route-arbitration record.
- [x] Selected topology event references the route-arbitration digest,
  selected candidate id, selected candidate digest, and candidate-set digest.
- [x] Exactly one selected topology event is committed for the arbitration
  record; rejected candidates do not commit selected topology events.
- [x] Surface lineage consumes the selected topology event.
- [x] Topology-state reabsorption consumes the selected topology event.
- [x] Candidate lineage map matches the selected topology event, surface
  lineage record, and topology-state reabsorption record.
- [x] Producers schedule only from lineage-current, reabsorbed state.
- [x] Producers do not mutate coherence, packet ledger, topology, or claims.
- [x] `step()` processes scheduled post-arbitration packet work.
- [x] Node-plus-packet budget remains exact.
- [x] Stale candidate set, missing selected candidate, candidate digest drift,
  wrong arbitration provenance, and duplicate arbitration commit controls fail
  closed.
- [x] Stale surface, stale state, and direct-write boundaries remain covered by
  the surface-lineage and topology-state reabsorption producer gates.

### Artifacts

- `Phase-8-LGRC9-NativeRouteArbitrationCommit.json`
- `Phase-8-LGRC9-NativeRouteArbitrationCommit.md`

### Implementation Notes

- Added `LGRC9V3.commit_native_route_arbitration_selection(...)`.
- The commit method consumes an existing route-arbitration record; it does not
  select routes itself.
- The committed selected topology event serializes
  `native_route_arbitration_record_id`,
  `native_route_arbitration_digest`,
  `native_route_selected_candidate_route_id`,
  `native_route_selected_candidate_route_digest`, and
  `native_route_candidate_set_digest`.
- The committed topology-event digest matches the digest authorized by the
  route-arbitration record. The arbitration digest is a backreference and is
  excluded from topology-event identity to avoid circular digest dependency.
- The selected candidate's lineage map is preserved through candidate route,
  selected topology event, surface lineage, and topology-state reabsorption
  records.
- Source, target, and retired node sets on topology-state reabsorption match
  the selected candidate route record.
- Surface-lineage transport and topology-state reabsorption consume the
  selected topology-event digest.
- Coupling producer evidence after commit cites the transported surface digest
  and topology-state reabsorption record digest before scheduling.
- Duplicate commit attempts return an idempotent skip and do not append
  duplicate topology, surface-lineage, or topology-state reabsorption records.
- A stale candidate set that no longer contains the selected candidate is
  rejected before topology commit.
- Missing selected candidate records, post-arbitration candidate digest drift,
  and wrong route-arbitration topology provenance are rejected before topology
  commit.
- Budget remains exact at the selected topology event, surface lineage,
  topology-state reabsorption, producer scheduling, and `step()` packet
  processing boundaries.
- Producers still schedule through LGRC scheduling only. `step()` remains the
  packet/coherence mutation boundary.
- Semantic choice, agency, RC identity collapse, identity acceptance,
  locomotion-like, biological, unrestricted movement, and movement claims remain
  blocked.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_arbitration"
15 passed, 125 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
41 passed, 222 deselected, 20 subtests passed

git diff --check
passed
```

## Iteration 81. Snapshot, Telemetry, Artifact Replay, Controls

Status: passed.

### Goal

Persist, export, reload, and artifact-validate native route-arbitration
evidence.

### Checks

- [x] Snapshot/load preserves candidate routes, candidate sets,
  route-arbitration records, selected topology events, and idempotency keys.
- [x] Continue-after-load does not duplicate candidate sets, arbitration
  records, topology events, reabsorption, or producer scheduling.
- [x] Telemetry exports route-arbitration artifacts only when policy is enabled.
- [x] Default-off telemetry remains backward-compatible.
- [x] Artifact-only validator reconstructs:

```text
candidate route set
-> route-arbitration record
-> selected topology event
-> surface lineage record
-> topology-state reabsorption record
-> producer record
-> scheduled/processed packet
```

- [x] Negative controls fail with distinct blockers:
  - [x] disabled policy;
  - [x] no candidates;
  - [x] unresolved tie;
  - [x] hidden input;
  - [x] budget mismatch;
  - [x] order inversion;
  - [x] duplicate arbitration;
  - [x] stale state;
  - [x] direct rewrite;
  - [x] claim promotion.

### Artifacts

- `Phase-8-LGRC9-NativeRouteArbitrationReplay.json`
- `Phase-8-LGRC9-NativeRouteArbitrationReplay.md`

### Implementation Notes

- Added `validate_lgrc9v3_native_route_arbitration_artifacts(...)`.
- The route-arbitration validator is artifact-only and records
  `runtime_state_used = false`.
- The validator reconstructs candidate route records, candidate set records,
  route-arbitration records, selected topology events, surface lineage,
  topology-state reabsorption, producer records, and scheduled/processed packet
  evidence.
- Candidate, candidate-set, and arbitration records are restored through
  canonical digest helpers.
- The selected topology event must reference the route-arbitration record,
  route-arbitration digest, selected candidate digest, and candidate-set digest.
  Rejected candidates must not commit topology events.
- Artifact-level hidden input, order inversion, budget mismatch, duplicate
  arbitration, topology drift, and claim-promotion controls are covered by
  validator tests with route-arbitration-specific blockers.
- Surface-lineage and topology-state reabsorption replay is delegated to the
  existing artifact-only lineage validator.
- Identical topology-event artifacts exported both as event rows and topology
  logs are deduplicated by event id and digest. Conflicting duplicates fail.
- Snapshot/load preserves native route candidate logs, candidate-set logs,
  route-arbitration logs, selected topology events, surface-lineage records,
  topology-state reabsorption records, and idempotency caches.
- Continue-after-load idempotency prevents duplicate arbitration records,
  selected topology events, lineage/reabsorption records, and producer
  scheduling from the same pending transported surface.
- Updated `src/pygrc/telemetry/lgrc9v3_contract.py` so telemetry exports a
  route-arbitration summary only when route-arbitration policy/logs are active.
- Default-off telemetry omits `native_route_arbitration`, preserving old
  telemetry shape.
- Enabled telemetry exports route-arbitration summaries in step and run-summary
  extensions, and graph checkpoints export candidate route, candidate-set, and
  route-arbitration logs.
- Event telemetry extensions expose native route-arbitration topology-event
  backreferences when present.
- Semantic choice, agency, RC identity collapse, identity acceptance,
  locomotion-like, biological, unrestricted movement, and claim promotion
  remain blocked.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_arbitration"
26 passed, 125 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
151 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
48 passed, 222 deselected, 20 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
123 passed, 59 subtests passed

.venv/bin/python -m pytest tests/telemetry/test_lgrc9v3_contract.py -q
7 passed

git diff --check
passed
```

## Iteration 82. Closeout And N04 Return

Status: passed.

### Goal

Close native route arbitration as runtime support and return to N04.

### Checks

- [x] Focused runtime tests pass.
- [x] Surface-lineage tests pass.
- [x] Topology-state reabsorption tests pass.
- [x] Packet-loop tests pass.
- [x] Snapshot and telemetry tests pass.
- [x] Artifact-only route-arbitration replay tests pass.
- [x] Support flag is true only if positive and negative validators pass:

```text
native_lgrc_route_arbitration_supported = true
```

- [x] Semantic choice, agency, RC identity collapse, identity acceptance,
  locomotion-like, biological, and unrestricted movement claims remain false.
- [x] N04 return target is recorded:

```text
N04 Iteration 21-B: native LGRC route-arbitration rerun
```

### Artifacts

- `Phase-8-LGRC9-NativeRouteArbitrationCloseout.md`
- `Phase-8-LGRC9-NativeRouteArbitrationCloseout.json`

### Implementation Notes

- Native route arbitration is closed as runtime support only.
- The supported capability is `native_lgrc_route_arbitration_supported = true`
  after positive replay and negative controls pass.
- Native route arbitration remains separate from semantic choice, agency,
  RC identity collapse, identity acceptance, locomotion-like behavior,
  biological behavior, unrestricted movement, and movement-claim promotion.
- N04 should return at Iteration 21-B and rerun the route-selection boundary
  with native route-arbitration records as the causal selection source.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_contract.py tests/telemetry/test_lgrc9v3_contract.py -q
281 passed, 59 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_arbitration"
26 passed, 125 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
151 passed

.venv/bin/python -m pytest tests/telemetry/test_lgrc9v3_contract.py -q
7 passed

git diff --check
passed
```
