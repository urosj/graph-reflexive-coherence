# N25.2 - LGRC9V3 MB6 Validation Bridge

N25.2 is the validation bridge after N25, N25.1, and the Phase 8 LGRC9V3
multi-basin formation implementation tranche.

N25 closed scoped BF5 high-margin core / sub-basin formation. N25.1 defined
the missing LGRC9V3 multi-basin formation extension contract. The Phase 8
implementation tranche then added default-off LGRC9V3 multi-basin runtime
surfaces and closed at:

```text
MB5 = control-backed native multi-basin formation candidate
```

N25.2 asks whether that Phase 8 MB5 evidence is enough to support the next
handoff rung:

```text
MB6 = N26-ready multi-basin substrate evidence
```

This is a validation/classification experiment, not a new runtime
implementation tranche. It should run the closed Phase 8 LGRC9V3 runtime
implementation as evidence, but it must not modify `src`, `specs`, `tests`,
examples, or implementation sources. If validation finds a defect, N25.2 records
the defect as a blocker or repair target. Runtime fixes require a separate
implementation branch/tranche outside this experiment.

## Core Question

```text
Does the Phase 8 LGRC9V3 multi-basin formation tranche provide source-backed,
replay-clean, control-clean, claim-clean evidence that N26 may consume as
N26-ready multi-basin substrate evidence?
```

Allowed outcomes:

```text
MB6 bridge supported:
  N26 may consume explicitly scoped multi-basin substrate evidence.

MB6 bridge blocked:
  N26 remains blocked from unscoped multi-basin substrate consumption, and
  N25.2 records the exact missing conditions.

MB5 demoted:
  N25.2 finds a flaw in the Phase 8 MB5 evidence and records the repair target.
```

## Source Boundary

Primary sources:

```text
experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json
experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/reports/n25_closeout_and_n26_handoff.md
experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/outputs/n25_1_closeout_and_phase8_extension_handoff.json
experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/reports/n25_1_closeout_and_phase8_extension_handoff.md
implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.json
implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.md
implementation/Phase-8-LGRC9-MultiBasinFormationPlan.md
implementation/Phase-8-LGRC9-MultiBasinFormationChecklist.md
implementation/Phase-8-LGRC9-MultiBasinFormationContractSchema.json
implementation/Phase-8-LGRC9-MultiBasinFormationContractSchema.md
implementation/Phase-8-LGRC9-Handoff.md
specs/lgrc-9-v3-spec.md
examples/lgrc9v3/README.md
```

Runtime implementation sources may be audited only to verify that recorded
Phase 8 evidence matches the claimed producer/runtime discipline:

```text
src/pygrc/models/lgrc_9_v3_contract.py
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
src/pygrc/telemetry/lgrc9v3_contract.py
tests/models/test_lgrc_9_v3_contract.py
tests/models/test_lgrc_9_v3_runtime.py
tests/models/test_lgrc_9_v3_autonomy_contract.py
tests/telemetry/test_lgrc9v3_contract.py
tests/visualization/test_visualization.py
```

N25.2 may execute existing LGRC9V3 runtime paths and consume the resulting
experiment artifacts as validation evidence. It may not patch implementation
sources, patch tests, relax specs, add examples, or use runtime execution to
claim semantic learning, choice, agency, native support, sentience, ant ecology,
organism/life, Phase 8 completion, or unrestricted autonomy.

Initial scaffold source inventory:

```text
source_inventory.md
```

## Local MB Ladder

N25.2 consumes the N25.1 / Phase 8 MB ladder:

```text
MB0 = no LGRC9V3 multi-basin evidence
MB1 = causal spark / boundary-birth candidate recorded
MB2 = topology integration / mechanical refinement recorded
MB3 = post-refinement child-basin cores detected
MB4 = replay-backed child-basin persistence candidate
MB5 = control-backed native multi-basin formation candidate
MB6 = N26-ready multi-basin substrate evidence
```

N25.2 starts from Phase 8 closeout state:

```text
phase8_closeout_mb_ceiling = MB5
mb5_control_backed_candidate_allowed = true
mb6_or_stronger_supported = false
n26_unscoped_consumption_allowed = false
```

## N25.2 Closeout Ladder

```text
N25.2-C0 = initialized validation bridge only
N25.2-C1 = source inventory and admissibility audit passed
N25.2-C2 = Phase 8 MB5 evidence chain validated or demotion recorded
N25.2-C3 = MB6 gate schema and active blockers frozen
N25.2-C4 = MB6 support/blocker matrix complete
N25.2-C5 = N26 consumption classification complete
N25.2-C6 = closeout and N26 handoff complete
```

`N25.2-C6` is a bridge closeout rung. It does not imply `MB6` support unless
the MB6 support matrix independently passes.

## Initial Status

```text
status = initialized
experiment_kind = validation_bridge
phase8_implementation_already_closed = true
starting_phase8_mb_ceiling = MB5_control_backed_native_multi_basin_formation_candidate
starting_mb6_status = blocked
runtime_implementation_opened = false
existing_lgrc9v3_runtime_execution_allowed = true
implementation_modification_allowed = false
defects_recorded_as_blockers_or_repair_targets = true
source_inventory_opened = false
mb6_validation_opened = false
n26_unscoped_consumption_allowed = false
```

## Expected Artifacts

```text
outputs/n25_2_source_inventory_and_admissibility_audit.json
reports/n25_2_source_inventory_and_admissibility_audit.md

outputs/n25_2_mb6_gate_schema_and_controls.json
reports/n25_2_mb6_gate_schema_and_controls.md

outputs/n25_2_phase8_mb5_evidence_chain_audit.json
reports/n25_2_phase8_mb5_evidence_chain_audit.md

outputs/n25_2_native_runtime_positive_probe.json
reports/n25_2_native_runtime_positive_probe.md

outputs/n25_2_native_runtime_variant_probe.json
reports/n25_2_native_runtime_variant_probe.md

outputs/n25_2_replay_persistence_matrix.json
reports/n25_2_replay_persistence_matrix.md

outputs/n25_2_fail_closed_control_matrix.json
reports/n25_2_fail_closed_control_matrix.md

outputs/n25_2_stress_variant_matrix.json
reports/n25_2_stress_variant_matrix.md

outputs/n25_2_mb6_support_blocker_matrix.json
reports/n25_2_mb6_support_blocker_matrix.md

outputs/n25_2_closeout_and_n26_handoff.json
reports/n25_2_closeout_and_n26_handoff.md
```

## Claim Boundary

N25.2 must keep the following false unless a later, explicit experiment opens
them:

```text
semantic_learning_claim_allowed = false
semantic_choice_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
native_support_claim_allowed = false
sentience_claim_allowed = false
organism_life_claim_allowed = false
ant_ecology_claim_allowed = false
phase8_completion_claim_allowed = false
unrestricted_autonomy_claim_allowed = false
```
