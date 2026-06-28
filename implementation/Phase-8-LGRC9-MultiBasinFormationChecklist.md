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
- N26 unscoped multi-basin consumption remains blocked unless MB6 passes and a
  follow-up N25.2 bridge records what N25/N25.1 and this Phase 8 tranche still
  leave unresolved.
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

Status: complete.

### Goal

Validate child-basin state persistence through artifact-only and snapshot/load
replay.

### Checks

- [x] Artifact-only replay reconstructs the refinement -> flow-window ->
      child-basin-state chain.
- [x] Snapshot/load replay preserves multi-basin records and idempotency keys.
- [x] Duplicate replay is stable.
- [x] Order inversion fails closed.
- [x] Missing replay blocks MB4+.
- [x] Persistence ratios are computed from serialized state, not report labels.

### Implementation Record

- Added `multi_basin_replay_validation_log` to `LGRC9V3RuntimeState`.
- Old snapshots remain compatible because missing replay logs restore as empty
  lists.
- Added `validate_multi_basin_child_basin_replay(...)` to validate one emitted
  child-basin state record by digest.
- Artifact-only replay checks the serialized chain:

```text
committed topology event
-> post_refinement_flow_window_log record
-> child_basin_state_log record
```

- Snapshot/load replay consumes an actual loaded snapshot artifact and verifies
  the same flow-window and child-basin records survive serialization.
- Duplicate replay is digest-idempotent: the same replay validation does not
  append a second record.
- Time-order inversion is represented as an explicit fail-closed replay control.
- Missing snapshot replay records `snapshot_load_replay_result = not_run` and
  blocks MB4 replay admission.
- Tampered serialized child-basin state records fail closed when persistence
  ratios drop below `1.0`.

### Interpretation

Iteration 86 validates replay persistence for the runtime surfaces opened in
Iteration 85. A clean replay record can support:

```text
MB4 replay-backed child-basin candidate
```

only when artifact replay, snapshot/load replay, duplicate replay, time-order
replay, and serialized persistence ratios all pass. It still does not support:

```text
MB5
MB6
native multi-basin formation support
BF6
independent new-basin formation
native support
agency
semantic learning
semantic choice
identity acceptance
sentience
ant ecology
Phase 8 completion
```

The persistence ratios are computed from serialized child-basin records:
membership, support, coherence, boundary, and flux maps are compared against the
loaded snapshot artifact. They are not report labels. As in Iteration 85,
support persistence remains coherence-derived because current LGRC9V3 node
state does not expose an independent support scalar.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin or native_route_arbitration_commit"
15 passed, 146 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
161 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin or native_route or child_basin or active_topology_integration_expands_causal_lane_b_candidate or stress_mixed_packet_birth_and_lane_b_expansion_preserves_runtime_refs or snapshot_round_trip"
74 passed, 220 deselected, 42 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
133 passed, 81 subtests passed

.venv/bin/python -m ruff check src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/lgrc_9_v3_runtime_state.py tests/models/test_lgrc_9_v3_runtime.py
All checks passed

git diff --check
passed
```

## Iteration 87. Merge/Leakage Controls

Status: complete.

### Goal

Reject false-positive multi-basin formation paths.

### Checks

- [x] Label-only child-basin relabel fails closed.
- [x] Old-basin thickening as child-basin formation fails closed.
- [x] Transient flow sink as child-basin formation fails closed.
- [x] Merge/leakage as multi-basin success fails closed.
- [x] Hidden producer basin insertion fails closed.
- [x] Producer-assisted success as native upgrade fails closed.
- [x] Post-hoc threshold or membership selection fails closed.
- [x] Semantic learning, choice, agency, native support, identity, sentience,
      organism/life, ant ecology, and Phase 8 completion relabels fail closed.

### Implementation Record

- Added `merge_leakage_control_matrix_log` to `LGRC9V3RuntimeState`.
- Old snapshots remain compatible because missing control logs restore as empty
  lists.
- Added `validate_multi_basin_merge_leakage_controls(...)` to record one
  digest-idempotent fail-closed control row per required false-positive path.
- The complete I87 matrix covers:

```text
label_only_child_basin
old_basin_thickening_as_child_basin
transient_flow_sink_as_child_basin
merge_leakage_as_multi_basin_success
missing_flow_window
missing_child_basin_state
missing_replay
hidden_producer_basin_insertion
producer_assisted_success_as_native_upgrade
post_hoc_threshold_or_membership_selection
semantic_learning_choice_agency_relabel
native_support_relabel
identity_acceptance_relabel
sentience_relabel
organism_life_relabel
ant_ecology_relabel
phase8_completion_relabel
```

- A complete fail-closed matrix requires a clean replay record before it can
  admit an MB5 candidate.
- Complete controls set
  `native_lgrc_multi_basin_formation_validated = true`, but preserve
  `native_lgrc_multi_basin_formation_supported = false` pending I89 closeout.
- Incomplete control matrices, missing replay, and claim-passing control rows
  fail closed.
- Failed-open control records remain blockers for that source child-basin state
  and cannot be bypassed by rerunning the default matrix.
- Duplicate control validation is digest-idempotent.
- Snapshot/load preserves the control matrix log.

### Interpretation

Iteration 87 closes the core merge/leakage control gate for the runtime surfaces
opened in I85 and replay-validated in I86. The strongest supported ceiling is:

```text
MB5 control-backed native multi-basin formation candidate
```

This means the child-basin candidate is now replay-backed and protected against
the required false-positive paths. It still does not support:

```text
MB6
N26-ready unscoped multi-basin substrate evidence
BF6
independent new-basin formation
native support
agency
semantic learning
semantic choice
identity acceptance
sentience
organism/life
ant ecology
Phase 8 completion
```

The control rows are negative controls. Their success means blocker paths are
rejected, not that those blocker paths are positive evidence.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin or stress_mixed_packet_birth_and_lane_b_expansion_preserves_runtime_refs"
18 passed, 150 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
168 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin or native_route or child_basin or active_topology_integration_expands_causal_lane_b_candidate or stress_mixed_packet_birth_and_lane_b_expansion_preserves_runtime_refs or snapshot_round_trip"
81 passed, 220 deselected, 42 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
133 passed, 81 subtests passed

.venv/bin/python -m ruff check src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/lgrc_9_v3_runtime_state.py tests/models/test_lgrc_9_v3_runtime.py
All checks passed

git diff --check
passed
```

## Iteration 88. Snapshot, Telemetry, Examples

Status: complete.

### Goal

Persist, export, and demonstrate the multi-basin formation surfaces without
changing default runtime behavior.

### Checks

- [x] Default-off snapshots and telemetry remain backward-compatible.
- [x] Enabled snapshots preserve flow-window, child-basin, replay, and control
      records.
- [x] Enabled telemetry exports summaries only when policy/logs are active.
- [x] Add a focused example under `examples/lgrc9v3/`.
- [x] The example states what the extension does and what it is not.

### Implementation Record

- Added an optional `multi_basin_formation` LGRC9V3 telemetry family-extension
  summary in `src/pygrc/telemetry/lgrc9v3_contract.py`.
- Default-off telemetry remains backward-compatible: the summary and raw
  multi-basin logs are absent when the policy is disabled and no logs exist.
- Enabled telemetry emits compact counts, latest digests, replay/control
  status counts, MB5 candidate admission, and explicit false stronger-claim
  flags.
- Graph checkpoints now carry the compact `multi_basin_formation` summary plus
  the raw `post_refinement_flow_window_log`, `child_basin_state_log`,
  `multi_basin_replay_validation_log`, and
  `merge_leakage_control_matrix_log` only when the policy/logs are active.
- Added LGRC9V3 default visual observable paths for child-basin count, clean
  replay count, failed-closed control count, and failed-open control count.
- Added
  `examples/lgrc9v3/multi_basin_formation_bundle.py`, which runs the opt-in
  route-arbitration -> flow-window -> child-basin -> replay -> control chain,
  saves telemetry/checkpoint artifacts, and renders graph visuals from saved
  checkpoints.
- Added an explicit geometry note to the multi-basin bundle: this fixture is a
  collapse/reabsorption telemetry/control example over an unchanged three-node
  graph. Its two topology-history records are `lgrc9v3_causal_collapse`
  collapse/reabsorption and packet-transport records with
  `topology_mutated = false`; its child-basin state has
  `child_basin_core_ids = [0]` and
  `child_basin_membership_by_core = {"0": [0, 1, 2]}`.
- Added
  `examples/lgrc9v3/topology_birth_refinement_visual_bundle.py`, which uses
  the existing saturated-sink boundary-birth/refinement path to save
  initial/after-each-event checkpoints where topology visibly changes.
- Updated `examples/lgrc9v3/README.md` to list the focused multi-basin bundle.
  The README now distinguishes the MB telemetry/control bundle from the
  topology-growth visualization bundle.

Generated example artifacts are under:

```text
outputs/examples/lgrc9v3/lgrc9v3-multi-basin-formation-bundle/
outputs/examples/lgrc9v3/lgrc9v3-topology-birth-refinement-visual-bundle/
```

### Interpretation

Iteration 88 closes the snapshot/telemetry/example surface for the I85-I87
multi-basin runtime records. The Phase-T-style telemetry extension exports the
new surface only as an LGRC9V3 family-extension payload; the Phase-V-style
visual bundle renders saved graph-checkpoint artifacts and does not inspect
live runtime internals.

The example summary records:

```text
flow_window_record_count = 1
child_basin_state_record_count = 1
replay_validation_record_count = 1
control_record_count = 17
failed_closed_control_count = 17
failed_open_control_count = 0
clean_replay_record_count = 1
mb5_control_backed_candidate_allowed = true
mb6_or_stronger_supported = false
native_lgrc_multi_basin_formation_supported = false
```

The MB telemetry/control example is intentionally not a visible node-birth
fixture:

```text
initial_node_count = 3
final_node_count = 3
initial_edge_count = 3
final_edge_count = 3
topology_history = [
  lgrc9v3_causal_collapse / collapse_reabsorption / topology_mutated=false,
  lgrc9v3_causal_collapse / packet_transport / topology_mutated=false,
]
child_basin_core_ids = [0]
child_basin_membership_by_core = {"0": [0, 1, 2]}
```

The separate topology-growth visualization example records visible topology
expansion through the existing boundary-birth/refinement path:

```text
checkpoint_node_counts = [10, 10, 11, 15]
checkpoint_edge_counts = [9, 9, 10, 14]
topology_event_kinds = [
  "lgrc9v3_causal_boundary_birth",
  "hybrid_mechanical_expansion",
  "lgrc9v3_refinement_packet_transport",
  "lgrc9v3_proper_time_inheritance",
]
```

The I88 result supports telemetry and visualization readiness for:

```text
MB5 control-backed native multi-basin formation candidate
```

It still does not support:

```text
MB6
N26-ready unscoped multi-basin substrate evidence
BF6
independent new-basin formation
native support
semantic learning
agency
identity acceptance
sentience
organism/life
ant ecology
Phase 8 completion
```

### Verification

```text
.venv/bin/python -m pytest tests/telemetry/test_lgrc9v3_contract.py -q
8 passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/multi_basin_formation_bundle.py
passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/topology_birth_refinement_visual_bundle.py
passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin"
17 passed, 151 deselected

.venv/bin/python -m pytest tests/visualization/test_visualization.py -q -k "lgrc9v3"
5 passed, 63 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/telemetry/test_lgrc9v3_contract.py -q
309 passed, 81 subtests passed

.venv/bin/python -m ruff check src/pygrc/telemetry/lgrc9v3_contract.py src/pygrc/visualization/render.py src/pygrc/visualization/graph_render.py tests/telemetry/test_lgrc9v3_contract.py tests/visualization/test_visualization.py examples/lgrc9v3/multi_basin_formation_bundle.py examples/lgrc9v3/topology_birth_refinement_visual_bundle.py
All checks passed

git diff --check
passed
```

## Iteration 88-A. Front-Capacity-Gated Boundary Birth Companion

Status: complete.

### Goal

Add a corrected LGRC9V3 boundary-birth path that can require GRCL9V3/GRC9V3
front-capacity eligibility, then add a visual topology-growth example that uses
that corrected path rather than the diagnostic saturated-sink fixture.

### Checks

- [x] Keep legacy inactive-port boundary birth as the default for backward
      compatibility.
- [x] Add explicit
      `causal_boundary_birth_parent_eligibility =
      legacy_any_inactive_port | grcl9v3_front_capacity`.
- [x] Require `grcl9v3_front_capacity` mode to consume
      `grcl9v3_front_growth_eligible_ports` and
      `grcl9v3_growth_parent_capacity_sources`.
- [x] Make missing front-capacity metadata fail closed.
- [x] Reject explicit parent ports that are inactive but not front-capacity
      eligible.
- [x] Record front-capacity provenance in producer records and boundary-birth
      event payloads.
- [x] Add a corrected front-capacity topology-growth visual example.
- [x] Preserve the diagnostic topology-growth fixture as diagnostic, not as the
      corrected front-capacity result.
- [x] Preserve MB6, native support, agency, semantic learning, sentience, ant
      ecology, and Phase 8 completion blockers.

### Implementation Record

- Added LGRC9V3 causal-mode constants:

```text
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_LEGACY_ANY_INACTIVE_PORT
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_GRCL9V3_FRONT_CAPACITY
```

- Added default causal mode:

```text
causal_boundary_birth_parent_eligibility = legacy_any_inactive_port
```

- Updated LGRC9V3 causal-mode validation so active
  `grcl9v3_front_capacity` parent eligibility requires
  `causal_boundary_birth_allowed = true`.
- Updated the LGRC9V3 boundary-birth producer so
  `grcl9v3_front_capacity` mode filters inactive ports through the lowered
  front-capacity cache:

```text
grcl9v3_front_growth_eligible_ports
grcl9v3_growth_parent_capacity_sources
```

- Updated explicit boundary-birth execution so missing front-capacity metadata
  returns:

```text
last_causal_boundary_birth_status = no_front_capacity_eligible_port
```

  and an explicitly supplied inactive but non-front-capacity port raises a
  fail-closed state-transition error.
- Tightened the front-capacity cache reader so an eligible-port entry without a
  matching `grcl9v3_growth_parent_capacity_sources` record is treated as
  incomplete metadata and fails closed rather than scheduling a birth.
- Added front-capacity provenance to scheduled producer records and accepted
  boundary-birth event payloads:

```text
parent_eligibility_mode = grcl9v3_front_capacity
growth_parent_eligibility_mode = grcl9v3_front_capacity
front_capacity_source = spark_expansion_front
growth_parent_capacity_source = spark_expansion_front
```

- Added
  `examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py`, which
  lowers a GRCL9V3 front-growth source, consumes the lowered front-capacity
  metadata, schedules one boundary-birth trial through the producer, executes
  the trial, saves telemetry/checkpoint artifacts, and renders graph visuals.
- Updated `examples/lgrc9v3/README.md` to distinguish:

```text
multi_basin_formation_bundle.py
  collapse/reabsorption telemetry/control surface over unchanged graph

topology_birth_refinement_visual_bundle.py
  diagnostic visible topology-growth fixture using explicit/aggressive path

front_capacity_topology_birth_visual_bundle.py
  corrected front-capacity-gated visible topology-growth companion
```

Generated example artifacts are under:

```text
outputs/examples/lgrc9v3/lgrc9v3-front-capacity-topology-birth-visual-bundle/
```

### Interpretation

Iteration 88-A resolves the immediate I88 visual ambiguity without relabeling
the diagnostic fixture. LGRC9V3 still does not inherit GRC9V3 front capacity
implicitly; it now has an explicit, opt-in boundary-birth parent-eligibility
mode that consumes the GRCL9V3/GRC9V3 lowered front-capacity cache.

The corrected visual companion records:

```text
causal_boundary_birth_parent_eligibility = grcl9v3_front_capacity
front_capacity_source = spark_expansion_front
scheduled_event_count = 1
event_counts_by_kind = {"lgrc9v3_causal_boundary_birth": 1}
checkpoint_node_counts = [13, 14]
checkpoint_edge_counts = [12, 13]
visible_topology_growth = true
```

This supports:

```text
front-capacity-gated LGRC9V3 boundary-birth producer/executor evidence
corrected visible topology-growth visual companion
```

It does not support:

```text
MB6
N26-ready unscoped multi-basin substrate evidence
BF6
independent new-basin formation
native support
semantic learning
agency
identity acceptance
sentience
organism/life
ant ecology
Phase 8 completion
```

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q -k "causal_modes or boundary_birth"
9 passed, 125 deselected, 12 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "causal_boundary_birth"
7 passed, 163 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_autonomy_contract.py -q -k "boundary_birth"
8 passed, 13 deselected

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py
passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/topology_birth_refinement_visual_bundle.py
passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/multi_basin_formation_bundle.py
passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_autonomy_contract.py tests/telemetry/test_lgrc9v3_contract.py -q
333 passed, 81 subtests passed

.venv/bin/python -m pytest tests/visualization/test_visualization.py -q -k "lgrc9v3"
5 passed, 63 deselected

.venv/bin/python -m ruff check src/pygrc/models/lgrc_9_v3_contract.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/__init__.py tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_autonomy_contract.py examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py examples/lgrc9v3/topology_birth_refinement_visual_bundle.py examples/lgrc9v3/multi_basin_formation_bundle.py
All checks passed

git diff --check
passed
```

## Iteration 89. Closeout And N25.2 Transition Gate

Status: complete.

### Goal

First validate that producers added or exercised in this branch remain
compatible with existing LGRC9V3 producer discipline and RC theory. Then close
or block native multi-basin formation support and record a scoped N25.2
transition before any N26 handoff.

### Checks

- [x] Producer compatibility audit passes before closeout classification.
- [x] Every producer touched by this tranche declares observed runtime-visible
      inputs, scheduled event kind, mutation owner, and forbidden direct
      mutations.
- [x] Producers observe, record, and schedule only through declared LGRC/RC
      surfaces.
- [x] Producers do not inject semantic content, basin content, hidden support,
      or success criteria from outside the reflexive loop.
- [x] Producers do not act as third-party observers that manage formation
      content above the RC reflexive mechanics.
- [x] Native LGRC capacity claims are not upgraded from producer-mediated
      scheduling alone.
- [x] Focused runtime, contract, telemetry, and example tests pass.
- [x] `git diff --check` passes.
- [x] Support flags are true only if positive replay and negative controls pass.
- [x] MB ladder ceiling is recorded.
- [x] N25.2 transition is scoped:

```text
MB6 supported ->
  N25.2 records how this tranche supplies the missing multi-basin mechanism
  before N26 consumes unscoped multi-basin substrate evidence.

MB6 not supported ->
  N25.2 consumes N25 BF5, N25.1 requirements, Phase 8 MB5/I88-A evidence,
  and remaining MB6 blockers to show what is still missing before N26.
```

- [x] Unsafe claims remain false.

### Artifacts

- [`Phase-8-LGRC9-MultiBasinFormationCloseout.md`](./Phase-8-LGRC9-MultiBasinFormationCloseout.md)
- [`Phase-8-LGRC9-MultiBasinFormationCloseout.json`](./Phase-8-LGRC9-MultiBasinFormationCloseout.json)

### Producer Compatibility Audit

The I89 audit validates the same producer/executor split used by prior
LGRC9V3 Phase 8 work:

```text
producers observe declared runtime-visible LGRC/RC surfaces
producers record declared evidence
producers schedule declared work
LGRC9V3 runtime transitions own mutation
```

Audited producers:

```text
packet_departure_from_flux_route
packet_departure_from_route_surplus
packet_departure_from_pulse_substrate_coupling
packet_departure_from_feedback_eligibility
boundary_birth_trial
```

The packet producers schedule packet-departure events from declared route,
surface-lineage, feedback, or route-surplus evidence. Packet coherence mutation
remains owned by packet event processing in `step()`.

The boundary-birth producer schedules
`lgrc9v3_causal_boundary_birth_trial` records. Topology mutation remains owned
by `apply_causal_boundary_birth_trial(...)` when the runtime consumes the
queued trial. In front-capacity mode the producer consumes:

```text
grcl9v3_front_growth_eligible_ports
grcl9v3_growth_parent_capacity_sources
```

Partial or mismatched front-capacity metadata fails closed. No producer is
allowed to inject semantic content, basin content, hidden support, or success
criteria above the LGRC/RC runtime loop.

### Closeout Result

Supported ceiling:

```text
mb_ladder_ceiling = MB5_control_backed_native_multi_basin_formation_candidate
mb5_control_backed_candidate_allowed = true
```

Blocked:

```text
MB6
N26-ready unscoped multi-basin substrate evidence
BF6
independent new-basin formation as a general native capacity
native support
semantic learning
semantic choice
agency
identity acceptance
sentience
organism/life
ant ecology
Phase 8 completion
```

N25.2 is the next scoped bridge before N26. Because MB6 is not supported,
N25.2 should consume N25 BF5, N25.1 requirements, Phase 8 MB5/I88-A evidence,
and the remaining MB6 blockers to state exactly what is still missing.

### Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_autonomy_contract.py tests/telemetry/test_lgrc9v3_contract.py -q
333 passed, 81 subtests passed

.venv/bin/python -m pytest tests/visualization/test_visualization.py -q -k "lgrc9v3"
5 passed, 63 deselected

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/multi_basin_formation_bundle.py
passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/topology_birth_refinement_visual_bundle.py
passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py
passed

.venv/bin/python -m ruff check src/pygrc/models/lgrc_9_v3_contract.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/__init__.py src/pygrc/telemetry/lgrc9v3_contract.py src/pygrc/visualization/render.py src/pygrc/visualization/graph_render.py tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_autonomy_contract.py tests/telemetry/test_lgrc9v3_contract.py tests/visualization/test_visualization.py examples/lgrc9v3/multi_basin_formation_bundle.py examples/lgrc9v3/topology_birth_refinement_visual_bundle.py examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py
All checks passed

git diff --check
passed
```
