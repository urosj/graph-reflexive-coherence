# N25.1 Implementation Plan - LGRC9V3 Multi-Basin Formation Extension Requirements

## Scope

N25.1 defines the contract for a future Phase 8 LGRC9V3 extension that can test
native multi-basin formation from causal refinement.

It does not implement that extension.

## Core Question

```text
What exact LGRC9V3 runtime surface is missing between:

causal spark / topology refinement exists

and:

multiple stable child basins form and persist replayably?
```

## Required Distinctions

```text
causal_spark_candidate != mechanical_expansion
mechanical_expansion != child_basin_persistence
refinement_lineage != identity_transfer
sub_basin_refinement != independent_multi_basin_formation
producer_scaffold != native_support
requirements_contract != runtime_evidence
```

## Required Evidence Fields For Future Extension

Future Phase 8 rows must record:

```text
source_current_inputs
runtime_config_digest
source_commit_or_source_digest
causal_spark_or_boundary_birth_event_id
topology_integration_event_id
refinement_lineage_map
pre_refinement_topology_signature
post_refinement_topology_signature
post_refinement_flow_window
child_basin_core_ids
child_basin_support_floor_records
child_basin_coherence_floor_records
child_basin_boundary_records
child_basin_flux_records
child_basin_membership_digest
merge_leakage_trace
replay_window
artifact_manifest
unsafe_claim_flags
```

## MB Ladder

```text
MB0 = no LGRC9V3 multi-basin evidence
MB1 = causal spark / boundary-birth candidate recorded
MB2 = topology integration / mechanical refinement recorded
MB3 = post-refinement child-basin cores detected
MB4 = replay-backed child-basin persistence candidate
MB5 = control-backed native multi-basin formation candidate
MB6 = N26-ready multi-basin substrate evidence
```

## Iterations

### Iteration 1. Source Crosswalk And Gap Inventory

Read GRCV3, GRC-9, GRC9V3, LGRC9V3, Phase 7, Phase 8, and N25 closeout sources.
Classify each source as theory, spec, historical evidence, current evidence, or
blocked relabel.

### Iteration 2. Multi-Basin Extension Schema Freeze

Freeze the MB ladder, required fields, child-basin extraction schema,
merge/leakage controls, replay requirements, producer-residue blockers, and
N26 consumption constraints.

### Iteration 3. Phase 8 Extension Requirement Matrix

Define the exact Phase 8 implementation surfaces needed: causal refinement
event, post-refinement flow evolution, child-basin extraction, replay, and
control hooks.

### Iteration 4. Closeout And Phase 8 Handoff

Close N25.1 as a requirements bridge. Record whether a Phase 8 extension is
ready to implement and whether N26 must remain scoped to N25 sub-basin evidence.
