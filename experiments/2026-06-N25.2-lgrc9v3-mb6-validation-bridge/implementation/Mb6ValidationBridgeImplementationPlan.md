# N25.2 Implementation Plan - LGRC9V3 MB6 Validation Bridge

## Scope

N25.2 validates the Phase 8 LGRC9V3 multi-basin formation implementation
tranche against the MB6 / N26 handoff gate.

It does not add new runtime behavior. It may run the closed Phase 8 LGRC9V3
runtime implementation and generate experiment artifacts from that execution.
It must not modify `src`, `specs`, `tests`, examples, or implementation sources.
If validation finds a defect, record it as a blocker or repair target; do not
patch it inside N25.2.

## Core Question

```text
Can the Phase 8 MB5 multi-basin formation candidate evidence be classified as
MB6 / N26-ready multi-basin substrate evidence?
```

If not, N25.2 must record the exact blockers and keep N26 unscoped
multi-basin consumption closed.

## Required Distinctions

```text
N25 BF5 scoped sub-basin evidence != MB6
N25.1 requirements contract != runtime evidence
Phase 8 MB5 candidate != MB6
visual topology growth != multi-basin substrate persistence
collapse/reabsorption telemetry != independent new-basin formation
producer scheduling != native support
front-capacity companion != blanket MB6 upgrade
N25.2-C6 closeout != MB6 support
```

## Source Rules

N25.2 may consume:

```text
N25 closeout as scoped BF5 / N25-C6 context
N25.1 closeout as MB ladder and Phase 8 requirements context
Phase 8 multi-basin closeout as MB5 implementation evidence
Phase 8 plan/checklist/schema as implementation evidence context
LGRC9V3 spec and tests as admissibility evidence
examples as telemetry/visual corroboration only
native LGRC9V3 runtime execution artifacts generated during N25.2 as validation
  evidence only
```

N25.2 must not consume:

```text
N25 BF5 as independent multi-basin formation
N25.1 requirements as runtime evidence
Phase 8 MB5 as automatic MB6
producer-assisted evidence as native support
visual graph growth as standalone proof
runtime implementation changes made inside N25.2
test or spec edits made to make evidence pass
```

## Required Evidence Fields

Every N25.2 candidate row should record:

```text
row_id
source_artifact_path
source_artifact_digest
source_role
may_consume_as
must_not_consume_as
mb_ladder_input
mb_ladder_candidate
n25_2_closeout_candidate
source_current_inputs
runtime_surface_evidence
native_runtime_execution_evidence
child_basin_state_records
multi_basin_substrate_persistence
replay_evidence
control_evidence
producer_audit_evidence
telemetry_example_evidence
mb6_gate_status
mb6_blockers
n26_consumption_effect
unsafe_claim_flags
row_decision
claim_ceiling
```

## Iterations

### Iteration 1. Source Inventory And Admissibility Audit

Read N25, N25.1, Phase 8 multi-basin closeout, implementation/spec, tests, and
example sources. Classify every source by role and admissible consumption.
Confirm that Phase 8 closeout starts at MB5 and that MB6 remains false.

### Iteration 2. MB6 Gate Schema And Controls

Freeze the MB6 gate schema, N26 consumption rules, source-admissibility rules,
producer/native discipline, replay/control requirements, and fail-closed
blockers.

### Iteration 3. Phase 8 MB5 Evidence Chain Audit

Audit the closed Phase 8 MB5 evidence chain before new N25.2 runtime probes:

```text
runtime surfaces
child-basin state records
replay validation
merge/leakage controls
producer compatibility audit
telemetry and examples
```

Record whether MB5 remains valid, is demoted, or requires repair.

### Iteration 4. Native LGRC9V3 Runtime Positive Probe

Run existing LGRC9V3 with the native multi-basin policy enabled. Emit
source-current runtime artifacts for the reference positive multi-basin case:

```text
runtime execution trace
flow-window records
child-basin state records
topology/refinement provenance
producer/native mutation ownership ledger
claim-boundary flags
```

Iteration 4 may support only a positive runtime candidate. Replay, controls,
stress, MB6, and N26 consumption remain pending.

### Iteration 4-A. Native Runtime Variant / Companion Probe

Run at least one alternative native runtime probe, such as a front-capacity
boundary-birth companion, seed/topology variant, or topology-growth companion
that remains inside the closed Phase 8 implementation.

This iteration tests whether the positive runtime evidence is not confined to a
single fixture. It must not retune the runtime or add implementation code.

### Iteration 5. Replay And Persistence Matrix

Replay the I4/I4-A runtime artifacts:

```text
artifact replay
snapshot/load replay
duplicate replay
multi-window child-basin persistence replay
```

Reconstruction is admissibility evidence only. It validates runtime-emitted
records; it does not replace runtime execution.

### Iteration 6. Fail-Closed Control Matrix

Run fail-closed controls against the runtime-emitted candidates:

```text
label-only basin formation
old-basin thickening relabel
transient flow sink relabel
collapse/reabsorption relabel
graph-visual-only success
hidden producer basin insertion
producer success as native support
front-capacity backfill
MB5-as-MB6 relabel
unsafe semantic / agency / native-support relabels
```

### Iteration 7. Stress / Threshold / Variant Matrix

Stress the strongest replay/control-backed native candidate without modifying
the implementation:

```text
flow-window threshold variation
merge/leakage pressure
child-basin persistence window variation
front-capacity / boundary-birth provenance variation
seed or topology fixture variation, where source-backed
```

Record whether evidence remains MB5 only, strengthens toward MB6, or exposes a
repair target.

### Iteration 8. MB6 Support / Blocker Matrix

Apply the MB6 gate. Classify whether evidence supports MB6 or whether MB6 is
blocked. If blocked, record exact blockers and their effect on N26.

### Iteration 9. Closeout And N26 Handoff

Close N25.2. Record final MB status, N25.2-C rung, N26 consumption permission,
claim boundary, and next handoff.

## Expected Closeout

Allowed:

```text
MB5 evidence validated
MB6 bridge supported with explicit N26 scope
MB6 blocked with exact blocker list
MB5 demoted with repair target
N25.2-C6 closeout and N26 handoff
```

Blocked:

```text
automatic MB6 from MB5
unscoped N26 consumption without MB6
native support
semantic learning
semantic choice
agency
sentience
ant ecology
organism/life
Phase 8 completion
unrestricted autonomy
```
