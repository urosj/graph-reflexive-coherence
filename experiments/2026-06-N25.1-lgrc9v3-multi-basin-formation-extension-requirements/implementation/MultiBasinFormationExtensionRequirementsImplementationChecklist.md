# N25.1 Implementation Checklist - LGRC9V3 Multi-Basin Formation Extension Requirements

## Global Guardrails

- [x] Create N25.1 requirements/spec bridge package.
- [x] Keep runtime implementation closed.
- [x] Keep multi-basin evidence closed.
- [x] Keep Phase 8 extension unimplemented.
- [x] Keep unsafe claims blocked.
- [x] Use repo-relative paths only.

Current closeout state:

```text
status = passed
experiment_kind = requirements_spec_bridge
acceptance_state = closed_n25_1_c4_requirements_bridge_phase8_handoff_ready_no_runtime_evidence
final_n25_1_closeout_rung = N25.1-C4_closeout_and_phase8_handoff_complete
final_mb_ladder_ceiling = MB0_requirements_bridge_only_no_runtime_evidence
requirements_bridge_closed = true
phase8_extension_ready_to_implement = true
runtime_implementation_opened = false
phase8_extension_implemented = false
multi_basin_evidence_opened = false
native_support_supported = false
agency_supported = false
sentience_supported = false
ant_ecology_opened = false
```

## Iteration 1. Source Crosswalk And Gap Inventory

- [x] Read GRCV3 spark completion sources.
- [x] Read GRC-9 mechanical refinement sources.
- [x] Read GRC9V3 child-basin stabilization sources.
- [x] Read LGRC9V3 causal spark / topology integration sources.
- [x] Read Phase 8 LGRC9 implementation plan boundary.
- [x] Read N25 closeout and producer-assisted scaffold sources.
- [x] Classify source roles.
- [x] Record missing LGRC9V3 multi-basin runtime surface.

Expected artifacts:

```text
outputs/n25_1_source_crosswalk_and_gap_inventory.json
reports/n25_1_source_crosswalk_and_gap_inventory.md
```

Result:

```text
status = passed
acceptance_state = accepted_source_crosswalk_gap_inventory_no_runtime_implementation
output_digest = 125a487cb0514535616ee5c7385f6ea566eca6fedac4c1657a77a75693bd845c
source_row_count = 11
source_record_count = 13
missing_runtime_surface_count = 3
runtime_implementation_opened = false
phase8_extension_implemented = false
multi_basin_evidence_opened = false
```

Interpretation:

N25.1 I1 is a source/spec inventory only. It does not invent a mechanism to
satisfy the N25.1 goal. The crosswalk records that spark/refinement machinery
already exists in the RC/GRC lineage:

```text
GRC-9 mechanical sparks and deterministic expansion are theory/spec-backed.
GRC9V3 hybrid sparks and child-basin stabilization are spec-backed.
Phase 7 records representative synchronous GRC9V3 spark/daughter-sink evidence.
LGRC9V3 examples/specs already expose causal spark candidates and refinement
packet transport surfaces.
```

So the N25.1 gap is not:

```text
sparks are absent
```

The gap is:

```text
native LGRC9V3 causal refinement
-> topology integration
-> post-refinement flow window
-> replayable child-basin extraction and persistence
-> merge/leakage and relabel controls
-> N26-ready multi-basin substrate evidence
```

I1 records three missing runtime surfaces:

```text
causal_refinement_event_to_topology_integration
post_refinement_child_basin_extraction
merge_leakage_and_relabel_controls
```

These are requirements targets only. They do not support BF6, native
multi-basin formation, independent new-basin formation, native support,
semantic learning, semantic choice, agency, sentience, Phase 8 implementation
completion, or ant ecology.

Traceability note:

```text
source_row_count = 11 crosswalk rows
source_record_count = 13 source files
```

The two extra source records are supporting LGRC9V3 example files consumed by
the examples/context row rather than independent crosswalk rows.

## Iteration 2. Multi-Basin Extension Schema Freeze

- [x] Freeze MB0...MB6 ladder.
- [x] Freeze required source-current fields.
- [x] Freeze child-basin extraction schema.
- [x] Freeze merge/leakage controls.
- [x] Freeze replay requirements.
- [x] Freeze producer-residue blockers.
- [x] Freeze N26 consumption constraints.

Expected artifacts:

```text
outputs/n25_1_multi_basin_extension_schema.json
reports/n25_1_multi_basin_extension_schema.md
```

Result:

```text
status = passed
acceptance_state = accepted_multi_basin_extension_schema_frozen_no_runtime_evidence
output_digest = a8a9f42ed03ff9ff54830a15f9c49a1016ffdd7c22864fcf225758fd539e028b
mb_ladder_ceiling = MB0_schema_freeze_only
n25_1_closeout_ceiling = N25.1-C2_multi_basin_extension_schema_frozen
runtime_implementation_opened = false
phase8_extension_implemented = false
multi_basin_evidence_opened = false
```

Frozen ladder:

```text
MB0 = no LGRC9V3 multi-basin evidence
MB1 = causal spark / boundary-birth candidate recorded
MB2 = topology integration / mechanical refinement recorded
MB3 = post-refinement child-basin cores detected
MB4 = replay-backed child-basin persistence candidate
MB5 = control-backed native multi-basin formation candidate
MB6 = N26-ready multi-basin substrate evidence
```

N25.1 closeout ladder:

```text
N25.1-C0 = initialized requirements bridge only
N25.1-C1 = source crosswalk and gap inventory passed
N25.1-C2 = multi-basin extension schema frozen
N25.1-C3 = Phase 8 extension requirement matrix ready
N25.1-C4 = closeout and Phase 8 handoff complete
```

Schema interpretation:

I2 freezes the future extension contract; it does not satisfy it. Paper/spec
vocabulary can define required fields, ordering rules, replay modes, controls,
and N26 consumption constraints, but it cannot count as runtime evidence.

The future candidate row schema now requires, among other fields:

```text
causal_spark_or_boundary_birth_event_id
topology_integration_event_id
mechanical_refinement_event_id
refinement_lineage_map
post_refinement_flow_window
child_basin_core_ids
child_basin_support_floor_records
child_basin_coherence_floor_records
child_basin_boundary_records
child_basin_flux_records
child_basin_membership_digest
merge_leakage_trace
replay_results
control_results
producer_residue_classification
unsafe_claim_flags
```

The schema blocks common false positives:

```text
old synchronous expansion relabeled as causal extension
causal spark label without topology integration
module-node creation relabeled as child basin
transient sink relabeled as persistent child basin
old-basin thickening relabeled as independent multi-basin formation
merge/leakage relabeled as separation
producer-assisted success upgraded into native success
producer scaffold overwriting native failure
producer threshold relaxation
post-hoc child-basin stitching
event-order inversion
topology integration event missing
support/coherence/boundary/flux child-record omission
child membership digest omission
BF5 scoped sub-basin relabeled as BF6
```

Replay result field convention:

```text
container_field = replay_results
allowed_granular_fields =
  artifact_replay_result
  snapshot_load_replay_result
  duplicate_replay_result
  handoff_reconstruction_replay_result
granular_fields_may_be_nested_under_replay_results = true
```

N26 constraint:

```text
N26 may consume N25 scoped BF5 context and the N25.1 requirements schema.
N26 may not consume unscoped multi-basin substrate, independent new-basin
substrate, native LGRC9V3 multi-basin claims, or BF6 until MB6 exists.
```

Claim boundary:

```text
requirements_contract_allowed = true
runtime_evidence_allowed = false
native_multi_basin_formation_supported = false
BF6_supported = false
phase8_extension_ready_to_implement = false
```

## Iteration 3. Phase 8 Extension Requirement Matrix

- [x] Define Phase 8 runtime surfaces needed for native multi-basin formation.
- [x] Define causal refinement event requirements.
- [x] Define post-refinement flow-window requirements.
- [x] Define child-basin persistence/replay requirements.
- [x] Define implementation blockers and controls.

Expected artifacts:

```text
outputs/n25_1_phase8_extension_requirements_matrix.json
reports/n25_1_phase8_extension_requirements_matrix.md
```

Result:

```text
status = passed
acceptance_state = accepted_phase8_extension_requirements_matrix_no_runtime_implementation
output_digest = 7dacf161f9374a9807cc5a67c9885ebede7cf4e3cd7a68031ac749f31742d4fb
requirement_row_count = 7
mb_ladder_ceiling = MB0_requirement_matrix_only
n25_1_closeout_ceiling = N25.1-C3_phase8_extension_requirement_matrix_ready
phase8_extension_ready_to_implement = true
runtime_implementation_opened = false
phase8_extension_implemented = false
multi_basin_evidence_opened = false
```

Requirement matrix:

```text
causal_refinement_event_surface
  status = required_specifiable
  role = reuse_existing_surface
  enables = MB1

topology_integration_processor
  status = required_missing
  role = new_default_off_processor
  enables = MB2

post_refinement_flow_window
  status = required_missing
  role = new_default_off_surface
  enables = MB3

child_basin_state_record_surface
  status = required_missing
  role = new_default_off_surface
  enables = MB3, MB4

replay_and_persistence_validator
  status = required_missing
  role = new_validator
  enables = MB4, MB6

merge_leakage_control_matrix
  status = required_missing
  role = new_control_matrix
  enables = MB5, MB6

n26_handoff_gate
  status = required_specifiable
  role = handoff_constraint
  enables = MB6
```

Implementation sequence recommendation:

```text
reuse_or_expose_causal_refinement_event_surface
implement_default_off_topology_integration_processor
emit_post_refinement_flow_window_records
emit_child_basin_state_records
add_replay_and_persistence_validator
add_merge_leakage_control_matrix
gate_N26_unscoped_consumption_on_MB6
```

I2/I3 control alignment:

```text
i2_required_control_count = 30
i2_controls_missing_from_i3_rows = []
i3_controls_not_in_i2_required_control_ids = []
```

Replay result field convention:

```text
container_field = replay_results
allowed_granular_fields =
  artifact_replay_result
  snapshot_load_replay_result
  duplicate_replay_result
  handoff_reconstruction_replay_result
granular_fields_may_be_nested_under_replay_results = true
```

Interpretation:

I3 means the future Phase 8 extension is now specified enough to implement as
a separate tranche. It does not mean the extension has been implemented, and it
does not support MB runtime evidence. The phrase `ready_to_implement` is a
requirements status only:

```text
ready_to_implement = requirements are sufficiently specified
implemented = false
runtime evidence opened = false
native multi-basin formation supported = false
BF6 supported = false
```

N26 remains scoped:

```text
scoped_N25_BF5_consumption_allowed = true
N25_1_requirements_schema_consumption_allowed = true
unscoped_multi_basin_consumption_allowed = false
independent_new_basin_consumption_allowed = false
BF6_consumption_allowed = false
native_LGRC9V3_multi_basin_consumption_allowed = false
```

## Iteration 4. Closeout And Phase 8 Handoff

- [x] Classify final N25.1 requirements status.
- [x] Record whether Phase 8 extension is ready to implement.
- [x] Record N26 consumption constraints.
- [x] Keep runtime evidence closed.
- [x] Keep unsafe claims blocked.

Expected artifacts:

```text
outputs/n25_1_closeout_and_phase8_extension_handoff.json
reports/n25_1_closeout_and_phase8_extension_handoff.md
```

Result:

```text
status = passed
acceptance_state = closed_n25_1_c4_requirements_bridge_phase8_handoff_ready_no_runtime_evidence
output_digest = 396692475de004ddc8a586a501e1518b8316eebbf8f651304a76abeae25ae09e
final_n25_1_closeout_rung = N25.1-C4_closeout_and_phase8_handoff_complete
final_mb_ladder_ceiling = MB0_requirements_bridge_only_no_runtime_evidence
phase8_extension_ready_to_implement = true
runtime_implementation_opened = false
phase8_extension_implemented = false
multi_basin_evidence_opened = false
native_multi_basin_formation_supported = false
BF6_supported = false
```

Closeout interpretation:

N25.1 closes as a requirements/spec bridge. It hands a future Phase 8
implementation tranche a concrete, source-backed extension matrix, but it does
not implement the extension and does not provide MB runtime evidence.

Phase 8 handoff surfaces:

```text
causal_refinement_event_surface
topology_integration_processor
post_refinement_flow_window
child_basin_state_record_surface
replay_and_persistence_validator
merge_leakage_control_matrix
n26_handoff_gate
```

N26 handoff:

```text
N26 may consume scoped N25 BF5 context and N25.1 requirements context.
N26 may not consume unscoped multi-basin substrate, independent new-basin
substrate, native LGRC9V3 multi-basin formation, or BF6 unless a future
Phase 8 extension supplies MB6 runtime evidence.
```
