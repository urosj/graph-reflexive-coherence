# Phase 8 LGRC9 Topology-State Reabsorption Checklist

This checklist tracks the Phase 8 continuation for:

- [`Phase-8-LGRC9-TopologyStateReabsorptionPlan.md`](./Phase-8-LGRC9-TopologyStateReabsorptionPlan.md)

The task is to make committed LGRC-3 topology events operational for the live
runtime substrate: active node/edge state and packet-ledger accounting must be
rebased together before post-topology packet work can be valid.

## Ground Rules

- This is an LGRC9V3 implementation continuation using LGRC-3 semantics.
- It consumes, but does not replace, native surface-lineage transport.
- Preserve default-off behavior.
- Preserve fixed-topology LGRC-2 packet validation.
- Add lineage-aware LGRC-3 packet/state alignment only under explicit topology
  state reabsorption policy.
- Topology-state reabsorption may mutate active state only as a committed
  topology event consequence.
- Producers still observe, record, and schedule; `step()` or topology-state
  transition machinery owns mutation.
- Producers must not write coherence, support masks, centroid, displacement,
  topology, or claim flags.
- Reabsorbed active state and packet ledger must conserve node-plus-packet
  budget exactly.
- Surface lineage evidence and topology-state reabsorption evidence remain
  separate artifacts.
- Movement, adaptive-topology movement, topology-mutating movement, choice,
  agency, locomotion-like, biological, and identity-acceptance claims remain
  blocked until N04 validators rerun.
- Existing fixed-topology packet loops, causal pulse-substrate surfaces,
  surface-lineage transport, snapshot, telemetry, and GRC9V3 behavior must
  remain compatible.

## Iteration 66. Baseline Freeze

Status: complete.

### Goal

Freeze current behavior before topology-state reabsorption source changes.

### Checks

- [x] Record git commit and dirty working-tree state.
- [x] Record N04 Iteration 19-D boundary:

```text
primary_blocker =
packet_ledger_state_reabsorption_mismatch_after_topology_event
```

- [x] Confirm N04 current ceiling remains:

```text
adaptive_topology_entry_candidate
```

- [x] Confirm surface-lineage transport closeout remains supported.
- [x] Confirm topology-state reabsorption flags are absent or false:

```text
causal_topology_state_reabsorption_enabled = false
causal_topology_state_reabsorption_validated = false
causal_topology_state_reabsorption_supported = false
```

- [x] Confirm post-topology packet work still fails closed in the 19-D fixture.
- [x] Record current snapshot and telemetry schema baselines.
- [x] Run focused LGRC9V3 runtime, contract, packet-loop, surface-lineage,
  topology, telemetry, and diff checks.

Artifacts:

- [`Phase-8-LGRC9-TopologyStateReabsorptionBaselineFreeze.json`](./Phase-8-LGRC9-TopologyStateReabsorptionBaselineFreeze.json)
- [`Phase-8-LGRC9-TopologyStateReabsorptionBaselineFreeze.md`](./Phase-8-LGRC9-TopologyStateReabsorptionBaselineFreeze.md)

### Verification

```bash
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q
# 200 passed, 24 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py -q
# 42 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
# 7 passed

git diff -- src tests/models tests/telemetry
# empty
```

## Iteration 67. Contract And Policy Schema

Status: complete.

### Goal

Add default-off topology-state reabsorption schema and policy support.

### Checks

- [x] Add default-off policy flags:

```text
causal_topology_state_reabsorption_enabled
causal_topology_state_reabsorption_policy
causal_topology_state_reabsorption_validated
causal_topology_state_reabsorption_supported
```

- [x] Add a serializable topology-state reabsorption record with:
  - [x] topology event id/kind/digest;
  - [x] committed topology event flag;
  - [x] lineage transfer map;
  - [x] source/target/retired node ids;
  - [x] source/target/retired edge ids;
  - [x] node state before/after;
  - [x] edge state before/after;
  - [x] packet ledger digest before/after;
  - [x] active state digest before/after;
  - [x] active node-state totals;
  - [x] packet-ledger node, in-flight, and conserved-budget totals;
  - [x] node-plus-packet budget before/after/error;
  - [x] action = `rebased | merged | superseded | rejected`;
  - [x] claim flags;
  - [x] canonical digest.
- [x] Add idempotency key for the same topology event, lineage map, and
  reabsorption policy.
- [x] Freeze exact idempotency digest scope:

```text
topology_event_digest
lineage_transfer_map_digest
topology_state_reabsorption_policy_id
state_reabsorption_action
packet_ledger_digest_before
active_state_digest_before
```

- [x] Reject construction below LGRC-3 when enabled.
- [x] Reject records without committed topology event evidence.
- [x] Reject missing or partial lineage maps.
- [x] Reject merged or ambiguous budget surfaces.
- [x] Reject claim-promotion fields in runtime records.
- [x] Add JSON round-trip and digest stability tests.
- [x] Confirm fixed-topology behavior remains compatible.

### Implementation Notes

- Added default-off topology-state reabsorption causal mode flags in
  `src/pygrc/models/lgrc_9_v3_contract.py`.
- Added `LGRC9V3TopologyStateReabsorptionRecord` and stable field names.
- Added canonical record digest and idempotency key helpers.
- Exported the contract from `pygrc.models`.
- Added schema-level tests for default-off behavior, LGRC-3 gating, flag
  consistency, JSON round-trip, digest stability, missing lineage maps, budget
  mismatch, and claim-promotion rejection.
- Reabsorption records require committed topology-event evidence, complete
  source-node lineage coverage, and explicit active/packet-ledger budget
  totals. The schema rejects records where active node totals, packet-ledger
  node totals, in-flight totals, conserved totals, and node-plus-packet budget
  are merged or inconsistent.
- Action semantics are frozen as:
  `rebased` = active state moved through a declared lineage target;
  `merged` = multiple sources combine into a declared target;
  `superseded` = source state is retired without current active successor;
  `rejected` = topology event could not be safely applied.
- No active state mutation, packet-ledger rebase, runtime scheduling,
  snapshot persistence, or telemetry emission is implemented in Iteration 67.

### Verification

```bash
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
# 113 passed, 39 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
# 107 passed

uv run ruff check src/pygrc/models/lgrc_9_v3_contract.py src/pygrc/models/__init__.py tests/models/test_lgrc_9_v3_contract.py
# All checks passed

git diff --check
# passed

.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter19d_topology_mutating_movement_probe.py
# passed fail-closed with primary_blocker=packet_ledger_state_reabsorption_mismatch_after_topology_event
```

## Iteration 68. Active State Reabsorption

Status: complete.

### Goal

Apply committed topology events to active node/edge state under explicit
lineage maps.

### Checks

- [x] Reabsorption occurs only after a committed topology event.
- [x] Active state mutation is attributed to the topology event, not producer
  execution.
- [x] Selected/target nodes absorb transferred coherence according to the
  lineage map and declared policy.
- [x] Reabsorption accounts for transferred coherence through committed
  packet/topology lineage evidence.
- [x] Silent active-state renormalization is rejected; if a correction cannot
  be lineage-accounted, the lane fails closed.
- [x] Retired or superseded nodes remain auditable.
- [x] Edge rebasing, retirement, or supersession is explicit.
- [x] Active state digest changes only through the committed topology event.
- [x] Node-plus-packet budget remains conserved.
- [x] Missing topology event control fails closed.
- [x] Missing lineage map control fails closed.
- [x] Partial lineage map control fails closed.
- [x] Direct state rewrite control fails closed.
- [x] No movement or topology-mutating movement claim is emitted.

### Result

Iteration 68 adds a default-off runtime topology-state reabsorption path for
collapse/reabsorption packet transport. When explicitly enabled, committed
collapse topology events can settle transported in-flight packet mass into the
selected live target node and emit a
`lgrc9v3_topology_state_reabsorption_record` with active-state before/after
digests, packet-ledger before/after digests, source/target/retired node and
edge ids, lineage map, idempotency key, and false claim flags.

The default-off path still preserves the prior mismatch: after the same
collapse packet-transport lane, the ledger can report node total `6.0` while
active state remains `5.9`, and no topology-state reabsorption record is
emitted. The enabled path rebases active state to the packet ledger through the
committed topology event and records `node_plus_packet_budget_error = 0.0`.

Recorded Iteration 68 boundary details:

```json
{
  "active_state_change_owner": "committed_topology_event",
  "producer_mutated_active_state": false,
  "direct_state_rewrite": false,
  "ledger_node_total_before_reabsorption": 6.0,
  "active_state_node_total_before_reabsorption": 5.9,
  "lineage_accounted_reabsorbed_packet_amount": 0.1,
  "ledger_node_total_after_reabsorption": 6.0,
  "active_state_node_total_after_reabsorption": 6.0,
  "node_plus_packet_budget_error": 0.0,
  "state_reabsorption_action": "merged",
  "source_node_ids": [1, 2],
  "target_node_ids": [0],
  "retired_node_ids": [1],
  "edge_reabsorption_status": "incident_edges_audited_no_edge_topology_rewrite_in_iteration_68_fixture",
  "fixed_topology_signature_reuse_after_topology_event": "pending_iteration_69"
}
```

This is active-state support only. Packet processing after reabsorption,
producer post-topology scheduling, and the full 19-D promotion blocker are
still left for Iteration 69/70.

### Verification

```bash
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
# 100 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
# 226 passed, 39 subtests passed

uv run ruff check src/pygrc/models/lgrc_9_v3_packets.py src/pygrc/models/lgrc_9_v3_topology.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/lgrc_9_v3_runtime_state.py tests/models/test_lgrc_9_v3_runtime.py --extend-ignore F401,F403,F405
# passed
```

## Iteration 69. Packet Ledger And State Rebase

Status: complete.

### Goal

Make packet ledger and active state agree after topology events.

### Checks

- [x] Add lineage-aware LGRC-3 packet/state alignment path.
- [x] Preserve existing fixed-topology LGRC-2 packet alignment unchanged.
- [x] Settled in-flight packet amounts update active state and packet ledger
  together.
- [x] Transported in-flight packet endpoints rebase through the lineage map.
- [x] Packet ledger fixed-topology signature is not reused incorrectly after
  topology-state reabsorption.
- [x] Post-topology scheduling no longer fails with:

```text
packet_ledger_state_reabsorption_mismatch_after_topology_event
```

- [x] Budget error remains zero.
- [x] Nonnegative state checks pass.
- [x] Duplicate reabsorption attempts are suppressed.
- [x] Duplicate suppression uses the exact topology event, lineage-map,
  policy, action, packet-ledger-before, and active-state-before digest key.
- [x] Budget discontinuity control fails closed.

### Result

Iteration 69 adds lineage-aware LGRC-3 packet/state alignment for ledgers that
have passed collapse/reabsorption packet transport. Transported ledgers now
carry explicit non-fixed LGRC-3 metadata:

```json
{
  "causal_layer_mode": "topology_changing_causal_history",
  "lgrc_runtime_level": "lgrc3",
  "fixed_topology": false,
  "topology_change_allowed": true,
  "packet_transport_through_topology_change": true,
  "evidence_class": "collapse_reabsorption_packet_transport"
}
```

The packet validator still enforces strict fixed-topology signatures for normal
LGRC-2 ledgers. It only skips fixed-signature equality when the ledger is
explicitly marked as lineage-transported LGRC-3 packet evidence, and it still
requires `sum(active node coherence) == packet_ledger.node_coherence_total`.

The Iteration 69 runtime fixture confirms:

```json
{
  "old_primary_blocker": "packet_ledger_state_reabsorption_mismatch_after_topology_event",
  "old_blocker_resolved": true,
  "same_topology_event_lineage_used_for_state_and_ledger": true,
  "after_state_reabsorption": {
    "active_node_total": 6.0,
    "packet_ledger_node_total": 6.0,
    "packet_ledger_in_flight_total": 0.0,
    "lineage_accounted_reabsorbed_packet_amount": 0.1,
    "lineage_transfer_map": {"1": "0", "2": "0"}
  },
  "in_flight_endpoint_transport_fixture": {
    "lineage_transfer_map": {"1": "0"},
    "source_node_before": 1,
    "source_node_after": 0,
    "target_node_before": 2,
    "target_node_after": 2,
    "retired_node_endpoint_referenced_after_transport": false
  },
  "post_topology_departure_processed_by_step": true,
  "after_post_topology_departure": {
    "active_node_total": 5.9,
    "packet_ledger_node_total": 5.9,
    "packet_ledger_in_flight_total": 0.1
  },
  "post_topology_arrival_processed_by_step": true,
  "after_post_topology_arrival": {
    "active_node_total": 6.0,
    "packet_ledger_node_total": 6.0,
    "packet_ledger_in_flight_total": 0.0
  },
  "fixed_topology_signature_reused_after_topology_event": false,
  "duplicate_reabsorption_suppressed": true,
  "budget_after_duplicate_attempt_unchanged": true,
  "node_plus_packet_budget_error": 0.0
}
```

Snapshot restore now preserves the LGRC-3 packet-ledger metadata while still
accepting old fixed-topology LGRC-2 ledgers. Producer gating and N04 19-D
integration remain for Iteration 70.

Iteration 69 does not add a separate `packet_ledger_rebase_record_digest`; the
packet-ledger rebase evidence is the collapse packet-transport artifact plus
the topology-state reabsorption record. Both carry the committed topology event
and the same serialized lineage map. A separate packet-ledger rebase record can
be added later if artifact replay needs an additional digest surface.

### Verification

```bash
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
# 102 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
# 228 passed, 39 subtests passed

uv run ruff check src/pygrc/models/lgrc_9_v3_packets.py src/pygrc/models/lgrc_9_v3_topology.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/lgrc_9_v3_runtime_state.py tests/models/test_lgrc_9_v3_runtime.py --extend-ignore F401,F403,F405
# passed
```

## Iteration 70. Producers After Reabsorption

Status: Complete.

### Goal

Allow producers to schedule only from lineage-current, reabsorbed state after
topology events.

### Checks

- [x] Producer reads transported surface digest after topology event.
- [x] Producer verifies active state has been reabsorbed before scheduling.
- [x] Producer blocks stale pre-reabsorption state reads.
- [x] Producer schedules post-topology packet work only through LGRC scheduling.
- [x] `step()` processes scheduled post-topology packet work.
- [x] Producer records cite:
  - [x] transported surface digest;
  - [x] topology event digest;
  - [x] topology-state reabsorption record digest;
  - [x] scheduled packet id, if any.
- [x] Producer does not mutate coherence or topology directly.
- [x] Producer does not emit claims.
- [x] N04 19-D fixture can schedule and process post-topology packet work, but
  movement claims remain blocked in Phase 8.

### Implementation Notes

- Added producer-side topology-state reabsorption gating for transported
  surface rows. Coupling and feedback producers may evaluate transported
  surface rows, but schedule post-topology packet work only when a matching
  topology-state reabsorption record exists for the same topology event digest
  and lineage transfer map.
- Added producer reason code
  `topology_state_reabsorption_required_before_producer_scheduling` for
  transported-surface scheduling attempts before active state reabsorption.
- Producer evidence now records transported surface linkage, topology event
  digest, topology-state reabsorption record digest, and keeps all mutation and
  claim flags false.
- Fixed-topology producer reads remain unchanged. Transported-row subthreshold
  or non-trigger evaluations may still record evidence; scheduling requires the
  reabsorbed active state gate.

### Verification

```bash
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
# 105 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
# 231 passed, 39 subtests passed

uv run ruff check src/pygrc/models/lgrc_9_v3_contract.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/__init__.py tests/models/test_lgrc_9_v3_runtime.py --extend-ignore F401,F403,F405
# passed

git diff --check
# passed
```

## Iteration 71. Snapshot, Telemetry, Artifact Replay, Controls

Status: Complete.

### Goal

Validate topology-state reabsorption through persistence, export, and
artifact-only replay.

### Checks

- [x] Snapshot save/load preserves topology-state reabsorption records.
- [x] Snapshot save/load preserves reabsorbed active state and packet ledger.
- [x] Continue-after-load does not duplicate reabsorption records.
- [x] Telemetry exports topology-state reabsorption only when policy is enabled.
- [x] Default-off telemetry remains backward-compatible.
- [x] Artifact-only validator reconstructs:

```text
packet event
-> source surface row
-> topology event
-> topology-state reabsorption record
-> transported/superseded surface row
-> producer record
-> scheduled/processed post-topology packet
```

- [x] Validator rejects:
  - [x] missing topology event;
  - [x] missing lineage map;
  - [x] partial lineage map;
  - [x] budget discontinuity;
  - [x] duplicate reabsorption record;
  - [x] stale state read after topology event;
  - [x] direct rewrite;
  - [x] topology-only claim promotion.
- [x] Existing packet-loop, causal pulse-substrate, surface-lineage,
  topology, snapshot, telemetry, and focused runtime tests remain green.

### Implementation Notes

- Extended the artifact-only surface-lineage validator with optional
  `topology_state_reabsorption_records`. When producer records schedule from a
  transported surface digest, the validator now requires a linked
  topology-state reabsorption record digest and verifies topology-event digest,
  lineage-map, budget, duplicate, and claim-boundary evidence from artifacts
  only.
- Validator result records `artifact_only = true` and `runtime_state_used =
  false`. Under the current artifact contract, topology-state reabsorption
  records carry active-state and packet-ledger digests; those digest fields are
  made load-bearing by canonical record-digest validation and producer linkage.
  Independent packet-ledger-by-digest replay remains a possible future
  hardening surface if a separate packet-ledger digest artifact index is added.
- Producer-scheduled packet work is now stamped after producer evidence so the
  replay chain is strictly ordered:

```text
transported surface
-> producer evidence
-> scheduled/processed packet event
```

- Added telemetry namespace support in `src/pygrc/telemetry/lgrc9v3_contract.py`:
  step summaries, run summaries, and graph checkpoints export
  `topology_state_reabsorption` only when the policy/log is active. Default-off
  telemetry remains unchanged.
- Snapshot/load preserves topology-state reabsorption records and idempotency
  keys; continue-after-load producer scheduling does not duplicate reabsorption
  records.

### Result

```json
{
  "iteration": 71,
  "status": "passed",
  "snapshot_roundtrip_preserves_topology_state_reabsorption": true,
  "continue_after_load_duplicate_reabsorption": false,
  "telemetry_default_off_backward_compatible": true,
  "telemetry_exports_topology_state_reabsorption_when_enabled": true,
  "artifact_only_validator_reconstructs_reabsorption_chain": true,
  "artifact_only_validator_rejects_missing_reabsorption_record": true,
  "artifact_only_validator_rejects_duplicate_reabsorption_record": true,
  "artifact_only_validator_rejects_budget_discontinuity": true,
  "artifact_only_validator_rejects_topology_only_claim_promotion": true,
  "movement_claim_allowed": false,
  "adaptive_topology_movement_claim_allowed": false,
  "topology_mutating_movement_claim_allowed": false
}
```

### Verification

```bash
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py tests/telemetry/test_lgrc9v3_contract.py -q
# 117 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
# 238 passed, 39 subtests passed

.venv/bin/python -m pytest tests/telemetry -q
# 231 passed, 9 subtests passed

uv run ruff check src/pygrc/models/lgrc_9_v3_contract.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/lgrc_9_v3_runtime_state.py src/pygrc/models/__init__.py src/pygrc/telemetry/lgrc9v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/telemetry/test_lgrc9v3_contract.py --extend-ignore F401,F403,F405
# passed

git diff --check
# passed
```

## Iteration 72. Closeout And N04 Return

Status: Complete.

### Goal

Close this Phase 8 continuation only if topology-state reabsorption is
artifact-validatable and old behavior remains compatible.

### Checks

- [x] Closeout report produced:
  `implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`.
- [x] Closeout JSON produced:
  `implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json`.
- [x] Commands and environment recorded.
- [x] Worktree state recorded.
- [x] Schema and digest policy recorded.
- [x] State/ledger reabsorption boundary audited.
- [x] Snapshot/telemetry round-trip audited.
- [x] Artifact-only validator passed.
- [x] Controls passed with distinct primary blockers.
- [x] Claim flags recorded.
- [x] N04 handoff updated to resume with a follow-up strict topology-mutating
  movement probe, likely `19-E`.
- [x] No movement, adaptive-topology movement, topology-mutating movement,
  choice, agency, locomotion-like, biological, or identity-acceptance claims
  emitted by runtime producers.

### Artifacts

- [`Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`](./Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md)
- [`Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json`](./Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json)

### Result

```json
{
  "iteration": 72,
  "status": "passed",
  "native_topology_state_reabsorption_supported": true,
  "native_topology_state_reabsorption_validated": true,
  "default_policy_enabled": false,
  "artifact_only_validator_passed": true,
  "runtime_state_used_by_validator": false,
  "producer_record_digest_available": false,
  "producer_linkage_validation_used": true,
  "n04_return_iteration": "19-E",
  "n04_current_ceiling": "adaptive_topology_entry_candidate",
  "movement_claim_allowed": false,
  "adaptive_topology_movement_claim_allowed": false,
  "topology_mutating_movement_claim_allowed": false
}
```

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py tests/telemetry/test_lgrc9v3_contract.py -q
# 117 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
# 238 passed, 39 subtests passed

uv run ruff check src/pygrc/models/lgrc_9_v3_contract.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/lgrc_9_v3_runtime_state.py src/pygrc/models/__init__.py src/pygrc/telemetry/lgrc9v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/telemetry/test_lgrc9v3_contract.py --extend-ignore F401,F403,F405
# passed

git diff --check
# passed
```

### Minimal Closeout Statement

```text
LGRC9V3 supports default-off native topology-state reabsorption. Committed
topology events can rebase active node/edge state and packet-ledger accounting
through explicit lineage maps, preserving node-plus-packet conservation and
allowing post-topology packet work to be scheduled from lineage-current,
reabsorbed state. This is runtime support only. Movement, adaptive-topology
movement, topology-mutating movement, native LGRC choice selection, RC identity
collapse, agency, locomotion-like behavior, biological behavior, and identity
acceptance remain blocked unless N04 reruns and passes the movement ladder.
```

Topology-state reabsorption makes post-topology packet work runtime-valid. It
does not by itself make topology-mutating movement valid.
