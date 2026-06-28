# Phase 8 LGRC9 Multi-Basin Formation Checklist

This checklist tracks the Phase 8 continuation for:

- [`Phase-8-LGRC9-MultiBasinFormationPlan.md`](./Phase-8-LGRC9-MultiBasinFormationPlan.md)

The task is to add a default-off LGRC9V3 runtime extension for multi-basin
formation from causal refinement. This is not a semantic learning, semantic
choice, agency, identity, native support, sentience, organism/life, ant-ecology,
or Phase 8 completion claim.

## Ground Rules

- Consume N25 and N25.1 as boundary and requirements sources, not as runtime
  success upgrades.
- Preserve the N25.1 distinction:

```text
causal_spark_candidate != mechanical_expansion
mechanical_expansion != child_basin_persistence
refinement_lineage != identity_transfer
sub_basin_refinement != independent_multi_basin_formation
producer_scaffold != native_support
requirements_contract != runtime_evidence
```

- Existing GRC9V3 spark and child-stabilization code is source context.
- Dedicated LGRC9V3 multi-basin runtime records must be newly exposed before
  MB3+ can be claimed.
- Preserve default-off behavior.
- Preserve packet, topology-event, surface-lineage, topology-state
  reabsorption, native route-arbitration, and node-plus-packet budget
  invariants.
- Producers may observe, record, and schedule only through declared producer
  surfaces. Mutation remains owned by LGRC9V3 runtime transitions.
- Producer-assisted success cannot upgrade native rows.
- N26 unscoped multi-basin consumption remains blocked unless MB6 passes.
- Unsafe claim flags must stay false in every artifact.
- Baseline freeze means no `src`, `specs`, `tests`, or `examples` behavior
  changes before the source-change envelope is opened and recorded.
- Future source changes must stay inside the multi-basin formation envelope or
  record an explicit dependency justification before the edit.

## Iteration 83. Baseline Freeze

Status: passed.

### Goal

Freeze current behavior before multi-basin formation source changes.

### Checks

- [x] Consume N25.1 as the immediate Phase 8 requirements handoff.
- [x] Confirm N25.1 closed at:

```text
final_mb_ladder_ceiling = MB0_requirements_bridge_only_no_runtime_evidence
phase8_extension_ready_to_implement = true
runtime_implementation_opened = false
native_multi_basin_formation_supported = false
BF6_supported = false
```

- [x] Confirm existing GRC9V3 child-stabilization behavior is present:

```text
evaluate_child_basin_stabilization(...)
register_completed_hybrid_spark(...)
hybrid_spark_completed
last_child_basin_stabilization
```

- [x] Confirm existing LGRC9V3 topology integration and causal spark runtime
  tests pass.
- [x] Confirm dedicated LGRC9V3 multi-basin runtime surfaces are absent:

```text
post_refinement_flow_window_log
child_basin_state_record_log
multi_basin_replay_validation_log
merge_leakage_control_matrix_log
native_lgrc_multi_basin_formation_supported
```

- [x] Confirm MB evidence remains closed:

```text
runtime_multi_basin_evidence_opened = false
native_multi_basin_formation_supported = false
BF6_supported = false
```

- [x] Confirm no source/spec/test/example changes are present in the baseline
  freeze:

```text
git diff --name-only -- src specs tests examples
    no output
```

- [x] Record intended source-change envelope for Iterations 84-89.
- [x] Run focused existing GRC9V3 and LGRC9V3 runtime tests.
- [x] Run `git diff --check`.

### Artifacts

- [`Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.json`](./Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.json)
- [`Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.md`](./Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.md)

### Verification

```text
.venv/bin/python -m pytest tests/models/test_grc_9_v3_sparks.py tests/models/test_lgrc_9_v3_runtime.py -q -k "child_basin or active_topology_integration_expands_causal_lane_b_candidate or stress_mixed_packet_birth_and_lane_b_expansion_preserves_runtime_refs or snapshot_round_trip"
    7 passed, 151 deselected

git diff --check
    passed
```

## Iteration 84. Contract And Policy Schema

Status: passed.

### Goal

Add default-off multi-basin formation schema and policy support without emitting
runtime evidence.

### Checks

- [x] Add default-off policy fields for native multi-basin formation.
- [x] Add serializable post-refinement flow-window records.
- [x] Add serializable child-basin state records.
- [x] Add serializable replay/persistence validation records.
- [x] Add serializable merge/leakage control records or matrix artifacts.
- [x] Add canonical digest and restore helpers for all record types.
- [x] Reject enabled policy below the required LGRC-3 topology integration
      surface.
- [x] Reject missing source topology event, missing lineage map, missing flow
      window, malformed child membership, and malformed support/coherence /
      boundary / flux records.
- [x] Reject producer-assisted success as native upgrade.
- [x] Reject all unsafe claim flags.
- [x] Add JSON round-trip, digest stability, and default-off compatibility tests.

### Artifacts

- [`Phase-8-LGRC9-MultiBasinFormationContractSchema.json`](./Phase-8-LGRC9-MultiBasinFormationContractSchema.json)
- [`Phase-8-LGRC9-MultiBasinFormationContractSchema.md`](./Phase-8-LGRC9-MultiBasinFormationContractSchema.md)

### Implementation Notes

- Added default-off causal mode flags:

```text
native_lgrc_multi_basin_formation_enabled = false
native_lgrc_multi_basin_formation_policy = disabled
native_lgrc_multi_basin_formation_validated = false
native_lgrc_multi_basin_formation_supported = false
```

- Added the active v1 policy:

```text
post_refinement_child_basin_replay
```

- Added serializable contract records:

```text
LGRC9V3MultiBasinFlowWindowRecord
LGRC9V3ChildBasinStateRecord
LGRC9V3MultiBasinReplayValidationRecord
LGRC9V3MultiBasinControlRecord
```

- Added canonical digest helpers and artifact restore helpers for all four
  record types.
- Updated `specs/lgrc-9-v3-spec.md` with the default-off multi-basin formation
  contract.
- Added `src/pygrc/models/__init__.py` facade exports for the new multi-basin
  contract surface. The same edit also exported pre-existing native-route
  contract names already imported by the facade; this is recorded as a
  dependency cleanup required for the touched facade file to pass `ruff` while
  adding the multi-basin exports.
- Removed two unused native-route validation temporary assignments in
  `LGRC9V3NativeRouteCandidateRecord`. This is a dependency cleanup required
  for the touched contract file to pass `ruff`; it preserves validation calls
  and does not change native-route semantics.
- The schema layer does not emit flow-window records, child-basin state,
  replay records, controls, topology events, or packet work.
- Multi-basin runtime evidence, MB4/MB5/MB6, BF6, independent new-basin
  formation, native support, semantic learning, semantic choice, agency,
  sentience, ant ecology, and Phase 8 completion remain blocked.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
133 passed, 81 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin or native_route or child_basin or active_topology_integration_expands_causal_lane_b_candidate or stress_mixed_packet_birth_and_lane_b_expansion_preserves_runtime_refs or snapshot_round_trip"
64 passed, 220 deselected, 42 subtests passed

git diff --check
passed
```

## Iteration 85. Flow Window And Child-Basin Emission

Status: complete.

### Goal

Emit source-current post-refinement flow-window and child-basin state records
from committed topology integration evidence.

### Checks

- [x] Emission is default-off.
- [x] Flow-window records cite committed topology integration and refinement
      lineage evidence.
- [x] Child-basin state records cite flow-window digests.
- [x] Child-basin membership is source-current and digest-backed.
- [x] Support, coherence, boundary, and flux records are serialized.
- [x] Candidate emission alone cannot support MB4+.
- [x] No semantic or identity claim is opened.

### Implementation Record

- Added default-off runtime logs to `LGRC9V3RuntimeState`:

```text
post_refinement_flow_window_log
child_basin_state_log
```

- Old snapshots remain compatible because missing logs restore as empty lists.
- Added a passive runtime emitter on committed native route arbitration topology
  events. The emitter runs only when:

```text
native_lgrc_multi_basin_formation_enabled = true
native_lgrc_multi_basin_formation_policy = post_refinement_child_basin_replay
```

- Default route-arbitration commits still emit no multi-basin records.
- Enabled commits emit:

```text
LGRC9V3MultiBasinFlowWindowRecord
LGRC9V3ChildBasinStateRecord
```

- Flow-window records cite the committed topology event digest, selected route
  candidate, topology-state reabsorption digest context, lineage transfer map,
  active node/edge state, packet ledger, and node-plus-packet budget trace.
- Child-basin state records cite the flow-window digest, source-current child
  core ids, digest-backed membership, support/coherence records, boundary
  records, flux records, old-basin relation trace, and merge/leakage trace.
- Digest-based idempotency keys suppress duplicate flow-window and child-state
  appends.

### Interpretation

Iteration 85 changes the runtime from "schema exists only" to "candidate
multi-basin surfaces can be emitted from committed topology integration
evidence." The emitted child-basin record is still a candidate extraction
surface:

```text
candidate_ceiling = MB3_candidate_emission_only
mb4_or_stronger_supported = false
```

It does not provide replay validation, persistence ratios, merge/leakage
controls, MB4, MB5, MB6, BF6, independent new-basin formation, native support,
semantic learning, semantic choice, agency, identity acceptance, sentience, ant
ecology, or Phase 8 completion.

Geometrically, the flow window serializes the post-refinement live substrate:
the committed topology event, lineage map, active node support/coherence
values, edge fluxes, packet flux summary, and conserved node-plus-packet budget.
The child-basin state then extracts a source-current local candidate around the
selected target core and records its membership, incident boundary conductance,
and incident flux. This is a runtime-visible geometric surface for later replay
and controls, not a final multi-basin proof.

Current LGRC9V3 node state exposes coherence as the source-current scalar used
for support accounting in this surface. Therefore `node_support_trace` and
`node_coherence_trace`, and the child-basin support/coherence floor records, are
coherence-derived in Iteration 85. This is a substrate-limited representation,
not evidence for an independent native support channel. If a later Phase 8
implementation adds a distinct source-current support field, these records
should separate the two traces without changing the I85 claim ceiling.

`old_basin_relation_trace` is a string-valued trace map, so the MB4 blocker is
serialized as:

```text
mb4_or_stronger_supported = "false"
```

Downstream consumers should treat this as a trace value, not as a support flag.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin or native_route_arbitration_commit"
10 passed, 146 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
156 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin or native_route or child_basin or active_topology_integration_expands_causal_lane_b_candidate or stress_mixed_packet_birth_and_lane_b_expansion_preserves_runtime_refs or snapshot_round_trip"
69 passed, 220 deselected, 42 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
133 passed, 81 subtests passed

.venv/bin/python -m ruff check src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/lgrc_9_v3_runtime_state.py tests/models/test_lgrc_9_v3_runtime.py
All checks passed

git diff --check
passed
```

## Iteration 86. Replay And Persistence Validator

Status: pending.

### Goal

Validate child-basin state persistence through artifact-only and snapshot/load
replay.

### Checks

- [ ] Artifact-only replay reconstructs the refinement -> flow-window ->
      child-basin-state chain.
- [ ] Snapshot/load replay preserves multi-basin records and idempotency keys.
- [ ] Duplicate replay is stable.
- [ ] Order inversion fails closed.
- [ ] Missing replay blocks MB4+.
- [ ] Persistence ratios are computed from serialized state, not report labels.

## Iteration 87. Merge/Leakage Controls

Status: pending.

### Goal

Reject false-positive multi-basin formation paths.

### Checks

- [ ] Label-only child-basin relabel fails closed.
- [ ] Old-basin thickening as child-basin formation fails closed.
- [ ] Transient flow sink as child-basin formation fails closed.
- [ ] Merge/leakage as multi-basin success fails closed.
- [ ] Hidden producer basin insertion fails closed.
- [ ] Producer-assisted success as native upgrade fails closed.
- [ ] Post-hoc threshold or membership selection fails closed.
- [ ] Semantic learning, choice, agency, native support, identity, sentience,
      organism/life, ant ecology, and Phase 8 completion relabels fail closed.

## Iteration 88. Snapshot, Telemetry, Examples

Status: pending.

### Goal

Persist, export, and demonstrate the multi-basin formation surfaces without
changing default runtime behavior.

### Checks

- [ ] Default-off snapshots and telemetry remain backward-compatible.
- [ ] Enabled snapshots preserve flow-window, child-basin, replay, and control
      records.
- [ ] Enabled telemetry exports summaries only when policy/logs are active.
- [ ] Add a focused example under `examples/lgrc9v3/`.
- [ ] The example states what the extension does and what it is not.

## Iteration 89. Closeout And N26 Gate

Status: pending.

### Goal

Close or block native multi-basin formation support and record N26 consumption
rules.

### Checks

- [ ] Focused runtime, contract, telemetry, and example tests pass.
- [ ] `git diff --check` passes.
- [ ] Support flags are true only if positive replay and negative controls pass.
- [ ] MB ladder ceiling is recorded.
- [ ] N26 handoff is scoped:

```text
MB6 supported -> N26 may consume multi-basin substrate evidence.
MB6 not supported -> N26 remains scoped to N25 BF5 / N25.1 requirements context.
```

- [ ] Unsafe claims remain false.
