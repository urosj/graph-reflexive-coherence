# Phase 8 LGRC9 Multi-Basin Formation Plan

Status: Open.

This continuation is opened by N25.1. N25 closed scoped native BF5
core/sub-basin formation evidence and producer-assisted BF5 scaffold context,
but native LGRC9V3 multi-basin formation, independent new-basin formation,
BF6, and unscoped multi-basin substrate evidence remained blocked. N25.1 then
closed as a requirements bridge for a future Phase 8 implementation tranche.

The N25.1 closeout state is:

```text
final_mb_ladder_ceiling = MB0_requirements_bridge_only_no_runtime_evidence
phase8_extension_ready_to_implement = true
runtime_implementation_opened = false
native_multi_basin_formation_supported = false
BF6_supported = false
```

Companion checklist:

- [`Phase-8-LGRC9-MultiBasinFormationChecklist.md`](./Phase-8-LGRC9-MultiBasinFormationChecklist.md)

## Goal

Add a default-off LGRC9V3 runtime extension that turns existing causal
refinement / spark / topology-integration machinery into replayable,
source-current multi-basin formation evidence:

```text
causal spark or boundary-birth event
-> topology integration / mechanical refinement event
-> post-refinement flow window
-> child-basin state records
-> replay-backed persistence validator
-> merge/leakage control matrix
-> N26 handoff gate
```

The extension should answer the N25.1 implementation question:

```text
What exact LGRC9V3 runtime surface is missing between:
  causal spark / topology refinement exists
and:
  multiple stable child basins form and persist replayably?
```

## Non-Goals

- Do not invent a new basin-formation mechanism beyond GRC-9/GRC9V3/LGRC9V3
  causal refinement mechanics.
- Do not relabel existing spark completion as replayable multi-basin
  persistence.
- Do not claim independent new-basin formation unless the replay/control matrix
  proves the new basin is not old-basin thickening, transient fluctuation,
  merge/leakage, or label-only reassignment.
- Do not claim semantic learning, semantic choice, agency, native support,
  sentience, organism/life, ant ecology, or Phase 8 completion.
- Do not let producer-assisted rows upgrade native multi-basin support.
- Do not let producers directly mutate coherence, packet ledger, topology,
  child-basin records, replay records, merge/leakage controls, or claim flags.
- Do not weaken existing packet, topology-event, surface-lineage,
  topology-state reabsorption, route-arbitration, or node-plus-packet budget
  invariants.

This continuation may eventually support a runtime capability named:

```text
native_lgrc_multi_basin_formation_supported
```

but only after source-current runtime evidence, replay, controls, and claim
boundaries pass. It does not mean native support, agency, identity acceptance,
or unrestricted basin generation.

## Inputs

N25 / N25.1 inputs:

- [`../experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json`](../experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json)
- [`../experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/reports/n25_closeout_and_n26_handoff.md`](../experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/reports/n25_closeout_and_n26_handoff.md)
- [`../experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/outputs/n25_1_phase8_extension_requirements_matrix.json`](../experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/outputs/n25_1_phase8_extension_requirements_matrix.json)
- [`../experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/outputs/n25_1_closeout_and_phase8_extension_handoff.json`](../experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/outputs/n25_1_closeout_and_phase8_extension_handoff.json)

Phase 8 inputs:

- [`Phase-8-LGRC9-ImplementationPlan.md`](./Phase-8-LGRC9-ImplementationPlan.md)
- [`Phase-8-LGRC9-Handoff.md`](./Phase-8-LGRC9-Handoff.md)
- [`Phase-8-LGRC9-NativePacketLoopChecklist.md`](./Phase-8-LGRC9-NativePacketLoopChecklist.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md)
- [`Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`](./Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md)
- [`Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md`](./Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md)
- [`Phase-8-LGRC9-NativeRouteArbitrationCloseout.md`](./Phase-8-LGRC9-NativeRouteArbitrationCloseout.md)

Telemetry and visualization inputs:

- [`Phase-T-GRC9V3-TelemetryContract.md`](./Phase-T-GRC9V3-TelemetryContract.md)
- [`Phase-V-GRC9V3-ImplementationPlan.md`](./Phase-V-GRC9V3-ImplementationPlan.md)
- [`Phase-V-GraphEvolutionContract.md`](./Phase-V-GraphEvolutionContract.md)

Source-code context:

- `src/pygrc/models/grc_9_v3_sparks.py`
- `src/pygrc/models/grc_9_v3.py`
- `src/pygrc/models/lgrc_9_v3_runtime.py`
- `src/pygrc/models/lgrc_9_v3_runtime_state.py`
- `src/pygrc/models/lgrc_9_v3_contract.py`
- `src/pygrc/models/lgrc_9_v3_topology.py`

## Current Boundary

Supported today:

- GRC9V3 can detect hybrid spark candidates and apply mechanical expansion.
- GRC9V3 can evaluate child-basin stabilization and register completed hybrid
  sparks when child nodes stabilize.
- LGRC9V3 can run causally scheduled spark diagnostics.
- LGRC9V3 can integrate topology-changing causal history under explicit modes.
- LGRC9V3 can preserve packet transport, proper-time inheritance,
  surface-lineage, topology-state reabsorption, time-scoped replay, and native
  route-arbitration invariants.

Blocked today:

- dedicated LGRC9V3 post-refinement flow-window records;
- dedicated LGRC9V3 child-basin state records;
- replay-backed child-basin persistence validation;
- merge/leakage controls for multi-basin formation;
- N26 unscoped multi-basin substrate consumption;
- BF6 or native multi-basin formation support.

The current gap is not spark absence. The gap is missing runtime evidence that
connects existing causal refinement to replayable, controlled multi-basin
formation.

## Freeze Semantics And Change Boundary

Iteration 83 is a baseline freeze in the same sense as prior Phase 8
continuations:

```text
record current behavior
prove focused old behavior still passes
record absent target surfaces
record the exact intended source-change envelope
block unrelated behavior changes
```

At Iteration 83, source changes are not opened. The only repository changes in
scope for the freeze are implementation records:

```text
implementation/Phase-8-LGRC9-MultiBasinFormationPlan.md
implementation/Phase-8-LGRC9-MultiBasinFormationChecklist.md
implementation/Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.md
implementation/Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.json
implementation/Phase-8-LGRC9-Handoff.md
implementation/Phase-8-LGRC9-ImplementationChecklist.md
```

The first source-changing iteration is Iteration 84. Its intended change
envelope is limited to multi-basin contract/schema support and matching tests.
Later iterations may touch only the surfaces needed by this tranche:

```text
src/pygrc/models/lgrc_9_v3_contract.py
src/pygrc/models/__init__.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_topology.py, if topology helpers are needed
src/pygrc/telemetry/lgrc9v3_contract.py, if telemetry is opened
specs/lgrc-9-v3-spec.md
tests/models/test_lgrc_9_v3_contract.py
tests/models/test_lgrc_9_v3_runtime.py
tests/telemetry/test_lgrc9v3_contract.py, if telemetry is opened
examples/lgrc9v3/, if examples are opened
```

Any change outside that envelope must be justified as a required dependency and
recorded in the checklist before it is made. Existing GRC9V3 spark behavior,
LGRC9V3 packet processing, topology integration, surface lineage,
topology-state reabsorption, native route arbitration, and default-off behavior
are protected invariants.

## MB Ladder

This continuation consumes the N25.1 MB ladder:

```text
MB0 = no LGRC9V3 multi-basin evidence
MB1 = causal spark / boundary-birth candidate recorded
MB2 = topology integration / mechanical refinement recorded
MB3 = post-refinement child-basin cores detected
MB4 = replay-backed child-basin persistence candidate
MB5 = control-backed native multi-basin formation candidate
MB6 = N26-ready multi-basin substrate evidence
```

Rows below MB4 cannot support persistence. Rows below MB5 cannot support
control-backed native multi-basin formation. MB6 is a handoff rung, not an
agency, identity, native support, or ant-ecology claim.

## Mechanism

The extension should add a default-off multi-basin formation policy surface.
The tentative policy fields are:

```text
native_lgrc_multi_basin_formation_enabled
native_lgrc_multi_basin_formation_policy
native_lgrc_multi_basin_formation_validated
native_lgrc_multi_basin_formation_supported
```

Exact field names are frozen in the contract-schema iteration, not in this
opening plan.

### Causal Refinement Source

The source record is reused from existing LGRC9V3 topology integration and
GRC9V3 spark machinery. It must cite:

```text
causal_spark_or_boundary_birth_event_id
topology_integration_event_id
mechanical_refinement_event_id
pre_refinement_topology_signature
post_refinement_topology_signature
refinement_lineage_map
source_runtime_config_digest
```

This source can support MB1/MB2 only. It cannot by itself support MB3+.

### Post-Refinement Flow Window Record

The flow-window record is the first new runtime surface. Minimum fields:

```text
post_refinement_flow_window_id
schema_version
native_multi_basin_policy_id
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

This surface records what happened after refinement. It does not classify child
basins by itself.

### Child-Basin State Record

The child-basin record extracts candidate child-basin state from the
post-refinement flow window. Minimum fields:

```text
child_basin_state_record_id
schema_version
native_multi_basin_policy_id
source_flow_window_digest
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

This surface may support MB3 only if the child-basin core is source-current and
not a label-only reassignment, old-basin thickening, transient fluctuation, or
merge/leakage artifact.

### Replay And Persistence Validation

The replay validator must reconstruct:

```text
causal refinement source
-> post-refinement flow window
-> child-basin state record
-> replay window
-> persisted child-basin state
```

Minimum result fields:

```text
replay_validation_id
schema_version
source_child_basin_state_digest
artifact_replay_result
snapshot_load_replay_result
duplicate_replay_result
time_order_replay_result
membership_persistence_ratio
support_persistence_ratio
coherence_persistence_ratio
boundary_persistence_ratio
flux_persistence_ratio
replay_window
replay_failure_modes
claim_flags
replay_validation_digest
```

Replay result status values are:

```text
passed
failed_closed
failed_open
not_run
```

Replay support can raise the ceiling to MB4 only if all required replay modes
pass and persistence ratios stay within frozen thresholds.

### Merge/Leakage Control Matrix

The control matrix must reject at least:

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
```

Clean replay plus fail-closed controls may support MB5. MB6 additionally
requires N26 handoff constraints to remain satisfied.

## Iterations

### Iteration 83. Baseline Freeze

Freeze the current boundary before multi-basin source changes. Confirm existing
spark/child-stabilization behavior exists, but dedicated LGRC9V3 multi-basin
runtime surfaces are absent.

### Iteration 84. Contract And Policy Schema

Add default-off policy flags, artifact dataclasses, digest helpers, restore
helpers, and validators for flow-window, child-basin state, replay, and control
records.

### Iteration 85. Flow Window And Child-Basin Emission

Emit post-refinement flow-window and child-basin state records from
runtime-visible topology integration evidence. Candidate emission alone must
not support MB4+.

### Iteration 86. Replay And Persistence Validator

Add artifact-only replay and persistence validation for child-basin state
records across declared replay windows.

### Iteration 87. Merge/Leakage Controls

Add negative controls for label-only, old-basin thickening, transient flow sink,
merge/leakage, hidden producer insertion, post-hoc thresholds, and unsafe
claim relabels.

### Iteration 88. Snapshot, Telemetry, Examples

Persist and export the new surfaces only when the policy is enabled. Add a
minimal example that states what the extension does and what it does not claim.
When visual inspection would otherwise confuse collapse/reabsorption telemetry
with visible node birth, add a separate topology-growth companion example
using the existing boundary-birth/refinement path.
Telemetry must remain under the LGRC9V3 family extension pattern established by
Phase T, and visualization must consume saved telemetry/checkpoint artifacts in
the Phase V style rather than reading live runtime internals.

### Iteration 88-A. Front-Capacity-Gated Boundary Birth Companion

Add LGRC9V3 front-capacity parent eligibility for causal boundary birth so the
LGRC producer/executor path can consume the corrected GRCL9V3/GRC9V3
front-growth surface instead of scanning any inactive port. Keep the legacy
inactive-port behavior as the default for backward compatibility, and require
`grcl9v3_front_capacity` to fail closed when front-capacity metadata is missing
or when an explicit parent port is not eligible.

Add a corrected topology-growth visual companion that lowers a GRCL9V3
front-growth source, schedules boundary birth only through
`grcl9v3_front_growth_eligible_ports` and
`grcl9v3_growth_parent_capacity_sources`, and saves saved-checkpoint visuals.
This companion must be recorded beside, not instead of, the diagnostic
saturated-sink topology-growth fixture from Iteration 88.

### Iteration 89. Closeout And N26 Gate

Close the extension only if runtime evidence, replay, controls, snapshot/load,
telemetry, and claim boundaries pass. Record whether N26 may consume MB6 or
must remain scoped to N25 BF5 / N25.1 requirements context.

## Initial Baseline

Baseline artifacts:

- [`Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.md`](./Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.md)
- [`Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.json`](./Phase-8-LGRC9-MultiBasinFormationBaselineFreeze.json)

The baseline result is MB0:

```text
native_multi_basin_formation_supported = false
BF6_supported = false
runtime_multi_basin_evidence_opened = false
```
