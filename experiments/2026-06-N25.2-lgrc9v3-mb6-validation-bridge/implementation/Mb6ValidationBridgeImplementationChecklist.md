# N25.2 Implementation Checklist - LGRC9V3 MB6 Validation Bridge

## Ground Rules

- N25.2 validates, classifies, and hands off. It does not add new runtime code
  by default.
- Consume N25 as scoped BF5 / N25-C6 context, not as independent multi-basin
  evidence.
- Consume N25.1 as MB ladder and requirements context, not as runtime evidence.
- Consume Phase 8 multi-basin closeout as MB5 evidence, not automatic MB6.
- Run existing closed LGRC9V3 runtime implementation as primary N25.2 evidence.
- Do not modify `src`, `specs`, `tests`, examples, or implementation sources
  inside N25.2. Defects become blockers or repair targets.
- Treat examples and visual artifacts as corroboration only.
- Preserve producer/native mutation discipline.
- N26 unscoped multi-basin substrate consumption remains blocked unless MB6
  passes.
- Unsafe claim flags remain false in every artifact.
- No absolute paths in records.

## Iteration 1. Source Inventory And Admissibility Audit

Status: passed.

### Goal

Build the source inventory and admissibility map for N25.2.

### Checks

- [x] Read N25 closeout and N26 handoff.
- [x] Read N25.1 closeout and Phase 8 extension requirements.
- [x] Read Phase 8 multi-basin formation closeout.
- [x] Read Phase 8 multi-basin plan, checklist, and contract schema.
- [x] Read LGRC9V3 spec multi-basin section.
- [x] Read examples README and relevant example interpretations.
- [x] Classify every source by role.
- [x] Freeze `may_consume_as` and `must_not_consume_as`.
- [x] Confirm starting Phase 8 ceiling is MB5.
- [x] Confirm starting MB6 status is false/blocked.
- [x] Confirm N26 unscoped consumption remains false.
- [x] Confirm unsafe claims remain false.
- [x] Confirm no absolute paths in records.

Expected artifacts:

```text
outputs/n25_2_source_inventory_and_admissibility_audit.json
reports/n25_2_source_inventory_and_admissibility_audit.md
```

### Result

```text
status = passed
acceptance_state = accepted_source_inventory_admissibility_audit_ready_for_i2_no_mb6
source_row_count = 23
failed_checks = []
starting_phase8_mb_ceiling = MB5_control_backed_native_multi_basin_formation_candidate
starting_mb6_status = blocked
mb5_evidence_admissible_for_validation = true
mb6_supported = false
mb6_gate_applied = false
mb6_gate_schema_frozen = false
n26_unscoped_consumption_allowed = false
n26_consumption_effect = blocked_pending_mb6_gate
runtime_implementation_opened = false
existing_lgrc9v3_runtime_execution_allowed_in_later_iterations = true
src_diff_expected = false
ready_for_iteration_2_mb6_gate_schema = true
implementation_modification_allowed = false
implementation_defect_fix_allowed_in_n25_2 = false
implementation_defect_disposition = record_as_blocker_or_repair_target_only
n25_2_closeout_ceiling = N25.2-C1_source_inventory_and_admissibility_audit_passed
n25_2_closeout_ladder_rung_assigned = false
output_digest = 3134b384b529b8c04bb6d78aff18f287884ef1cba536ed39637727157f25dd26
artifact_sha256 = 585accaf91af0dc4d569912bb3e5b0d436fe9f54642578436e1e694b9b583d70
report_sha256 = 620f6ecd0fd5b2e369d40d7d155501a71cdc262b2486be756466e09ee6870ab8
```

### Interpretation

Iteration 1 validates the N25.2 source map only. It makes Phase 8 MB5 evidence
admissible for the next schema step, but it does not support MB6, does not open
N26 unscoped multi-basin substrate consumption, and does not modify runtime
implementation.

The source-role split is load-bearing:

```text
N25 = scoped BF5 / N25-C6 context, not independent multi-basin evidence
N25.1 = MB ladder and requirements context, not runtime evidence
Phase 8 closeout = MB5 implementation evidence, not automatic MB6
examples = telemetry/visual corroboration only, not proof by visualization
tests/code = admissibility and implementation-boundary evidence, not claim
             support without artifacts
```

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_source_inventory_and_admissibility_audit.py
passed
```

## Iteration 2. MB6 Gate Schema And Controls

Status: passed.

### Goal

Freeze the schema that decides whether MB6 can be supported.

### Checks

- [x] Freeze MB6 support gate fields.
- [x] Freeze N26 consumption effects.
- [x] Freeze source artifact admissibility rules.
- [x] Freeze replay/control requirements.
- [x] Freeze producer/native discipline.
- [x] Freeze visual-evidence limitations.
- [x] Freeze active blockers for label-only, old-basin thickening, transient
      flow sink, collapse/reabsorption relabel, graph-visual-only success,
      hidden producer insertion, producer success as native support, and
      MB5-as-MB6 relabel.
- [x] Freeze unsafe claim flags.
- [x] Confirm no MB6 claim is made in Iteration 2.

Expected artifacts:

```text
outputs/n25_2_mb6_gate_schema_and_controls.json
reports/n25_2_mb6_gate_schema_and_controls.md
```

### Result

```text
status = passed
acceptance_state = accepted_mb6_gate_schema_and_controls_frozen_no_mb6_evidence
i1_output_digest = 3134b384b529b8c04bb6d78aff18f287884ef1cba536ed39637727157f25dd26
failed_checks = []
mb6_gate_schema_frozen = true
mb6_gate_applied = false
mb6_gate_status = not_applied
mb6_supported = false
phase8_mb5_evidence_chain_audited = false
mb5_demoted = false
n26_unscoped_consumption_allowed = false
n26_consumption_effect = unscoped_consumption_blocked
n26_consumption_blocker = blocked_pending_mb6_gate
runtime_implementation_opened = false
existing_lgrc9v3_runtime_execution_allowed = true
runtime_execution_is_primary_positive_evidence = true
implementation_source_modification_allowed = false
defect_disposition = record_as_blocker_or_repair_target_only
src_diff_expected = false
n25_2_closeout_ceiling = N25.2-C3_MB6_gate_schema_and_active_blockers_frozen
n25_2_closeout_ladder_rung_assigned = false
ready_for_iteration_3_phase8_mb5_evidence_chain_audit = true
output_digest = fe84d14ccf3f71f96453cc67653d080e3b3d172776ccc7ffaa061a6c4716485f
artifact_sha256 = ad3a04cc84cd230f8cb30ed0828133e62c45577c41a4aaa20fbb1fb91d7fdaae
report_sha256 = e2c04a0036d4b522073548730454931b16188534caf12bd0429267bb25e17a07
```

### Interpretation

Iteration 2 freezes the MB6 gate and fail-closed control schema only. It does
not audit the Phase 8 MB5 evidence chain, does not apply the MB6 support
matrix, does not claim MB6, and does not open N26 unscoped multi-basin
substrate consumption.

The frozen evidence policy makes existing LGRC9V3 runtime execution the primary
positive-evidence source. Artifact reconstruction and replay validate
runtime-emitted records; they do not replace runtime execution.

I4+ runtime artifacts must record source-tree and implementation digests,
runtime artifact roles, child-basin state record fields, and no-modification
proof:

```text
implementation_source_modification_observed = false
src_diff_observed = false
spec_diff_observed = false
test_diff_observed = false
example_diff_observed = false
runtime_execution_from_closed_implementation = true
defect_fix_attempted = false
defect_disposition = record_as_blocker_or_repair_target_only
```

The frozen gate requires source-backed runtime surfaces, child-basin state
records, replay-backed child-basin persistence, artifact/snapshot/duplicate
replay, merge/leakage controls, clean producer/native mutation ownership,
front-capacity or boundary-birth provenance when used, hidden-producer and
label-only controls, visual-evidence limits, explicit N26 scope, and unsafe
claim flags false.

N26 remains blocked from unscoped multi-basin consumption. If MB6 is later
supported, the only allowed handoff effect is scoped MB6 substrate consumption,
not vague unscoped consumption. If MB5 is demoted, N26 substrate consumption is
blocked.

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_mb6_gate_schema_and_controls.py
passed
```

## Iteration 3. Phase 8 MB5 Evidence Chain Audit

Status: passed.

### Goal

Validate whether the closed Phase 8 MB5 evidence chain remains admissible
before new N25.2 runtime probes.

### Checks

- [x] Validate runtime surfaces.
- [x] Validate child-basin state records.
- [x] Validate replay evidence.
- [x] Validate merge/leakage control evidence.
- [x] Validate producer compatibility audit.
- [x] Validate telemetry/example interpretations.
- [x] Classify MB5 chain status as one of:
      `mb5_chain_validated_for_runtime_probe`,
      `mb5_chain_validated_with_blockers`,
      `mb5_demoted_repair_required`, or
      `mb5_chain_unreadable_blocks_runtime_probe`.
- [x] Confirm MB5 remains supported, remains usable only with blockers, or is
      demoted with repair target.
- [x] Confirm I4 runtime probes cannot retroactively fix an I3 MB5-chain flaw.
- [x] Confirm MB6 remains unassigned until the MB6 matrix.
- [x] Confirm no implementation source is modified.

Expected artifacts:

```text
outputs/n25_2_phase8_mb5_evidence_chain_audit.json
reports/n25_2_phase8_mb5_evidence_chain_audit.md
```

### Result

```text
status = passed
acceptance_state = accepted_phase8_mb5_evidence_chain_validated_ready_for_i4_no_mb6
i1_output_digest = 3134b384b529b8c04bb6d78aff18f287884ef1cba536ed39637727157f25dd26
i2_output_digest = fe84d14ccf3f71f96453cc67653d080e3b3d172776ccc7ffaa061a6c4716485f
failed_checks = []
i3_mb5_chain_status = mb5_chain_validated_for_runtime_probe
phase8_mb5_evidence_chain_status = mb5_validated_for_runtime_probe
phase8_mb5_evidence_chain_audited = true
phase8_mb5_chain_safe_for_i4_runtime_probe = true
mb5_remains_supported = true
mb5_repair_targets = []
mb5_demoted = false
mb5_repair_required = false
mb6_gate_applied = false
mb6_gate_status = not_applied
mb6_supported = false
mb6_claim_allowed = false
mb6_blockers = [not_applied_until_iteration_8]
n26_unscoped_consumption_allowed = false
n26_consumption_effect = unscoped_consumption_blocked
n26_consumption_blocker = blocked_pending_mb6_gate
runtime_execution_performed = false
runtime_execution_deferred_to_iteration_4 = true
runtime_implementation_opened = false
native_runtime_positive_probe_opened = false
implementation_source_modification_allowed = false
implementation_source_modification_observed = false
src_diff_observed = false
spec_diff_observed = false
test_diff_observed = false
example_diff_observed = false
defect_fix_attempted = false
defect_disposition = blocker_or_repair_target_only
i4_runtime_probe_cannot_retroactively_fix_i3_chain_flaw = true
n25_2_closeout_ceiling = N25.2-C3_MB6_gate_schema_and_active_blockers_frozen_with_Phase_8_MB5_chain_validated
n25_2_closeout_ladder_rung_assigned = false
ready_for_iteration_4_native_runtime_positive_probe = true
output_digest = 7ef81dc80600d0fee487804efc3b022a2547b71b7a63bacdd761a41691f0dc6d
artifact_sha256 = e45535c28076553b64862469922f41d0c6f692a68d8f043528a03f93b001da29
report_sha256 = 35a5d6cc2f8181d49c04fec0519da228e1612b14429bd2b45e87755422b4d559
```

### Interpretation

Iteration 3 validates the closed Phase 8 MB5 chain as admissible input for the
next N25.2 runtime probe. It confirms the Phase 8 closeout remains MB5-only,
with runtime surfaces exposed, child-basin state schema present, replay and
merge/leakage control schemas present, producer compatibility audit passed,
verification results recorded, visual/example artifacts limited to
corroboration, and unsafe claims blocked.

It also records directive-level source-chain integrity, default-off runtime
surface checks, child-basin field mapping, replay/control non-prose checks,
producer/native mutation ownership, tests-as-admissibility-only limits, and
structured repair-target schema. No repair targets were emitted.

This is not a positive N25.2 runtime probe. It does not run the runtime, does
not apply the MB6 gate, does not support MB6, and does not open N26 unscoped
multi-basin substrate consumption. If a Phase 8 chain defect had been found in
I3, later runtime probes could only identify a repair target; they could not
retroactively make the I3 chain clean.

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_phase8_mb5_evidence_chain_audit.py
passed
```

## Iteration 4. Native LGRC9V3 Runtime Positive Probe

Status: passed.

### Goal

Run existing LGRC9V3 runtime with native multi-basin policy enabled and emit a
source-current positive runtime candidate.

### Checks

- [x] Run existing runtime only; no implementation edits.
- [x] Emit runtime execution trace.
- [x] Emit flow-window records.
- [x] Emit child-basin state records.
- [x] Emit topology/refinement provenance.
- [x] Emit producer/native mutation ownership ledger.
- [x] Record implementation source digests and runtime config digest.
- [x] Record child-basin fields: id, birth/detection step,
      parent/source basin, provenance, support/coherence core nodes, basin
      signature digest, topology before/after, flow-window id, merge/leakage
      status, persistence-window status, mutation owner, trace origin, and
      trace digest.
- [x] Record no-modification proof for `src`, `specs`, `tests`, examples, and
      implementation sources.
- [x] Record source-current inputs and artifact digests.
- [x] Confirm replay, controls, stress, MB6, and N26 remain pending.
- [x] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_native_runtime_positive_probe.json
reports/n25_2_native_runtime_positive_probe.md
```

### Result

```text
status = passed
acceptance_state = accepted_native_runtime_positive_mb3_candidate_pending_replay_controls_no_mb6
i3_output_digest = 7ef81dc80600d0fee487804efc3b022a2547b71b7a63bacdd761a41691f0dc6d
failed_checks = []
runtime_execution_performed = true
native_runtime_positive_probe_opened = true
runtime_execution_from_closed_implementation = true
flow_window_record_count = 1
child_basin_state_record_count = 1
replay_validation_record_count = 0
merge_leakage_control_record_count = 0
artifact_manifest_scope = embedded_payloads_only
embedded_artifact_manifest_count = 5
topology_provenance_shape = collapse_reabsorption_shaped_existing_graph
producer_residue_status = not_load_bearing_for_claim
source_current_status = native_runtime_emitted
mb_ladder_candidate = MB3_source_current_child_basin_candidate_emission
row_decision = supported
claim_ceiling = source-current MB3 child-basin candidate pending replay/control/stress; not MB5, not MB6
mb6_gate_status = not_applied
mb6_supported = false
mb6_claim_allowed = false
mb6_blockers = [replay_matrix_pending_iteration_5, control_matrix_pending_iteration_6, stress_matrix_pending_iteration_7, mb6_gate_pending_iteration_8]
n26_unscoped_consumption_allowed = false
n26_consumption_effect = unscoped_consumption_blocked
implementation_source_modification_allowed = false
implementation_source_modification_observed = false
src_diff_observed = false
spec_diff_observed = false
test_diff_observed = false
example_diff_observed = false
defect_fix_attempted = false
defect_disposition = record_as_blocker_or_repair_target_only
ready_for_iteration_5_replay_persistence_matrix = true
ready_for_iteration_4a_variant_probe = true
output_digest = 1a38c59b8e3149a4cdde1861237e45a0e9f2da8ecca6f548bf462313149527f1
artifact_sha256 = 19de5ce2be01e3cac2625ea5e01ee2fa0a302fa98c713e5a2bcd06769c6bd304
report_sha256 = 72d87074fdaf1bd00a7163d29d2adebc2c80b2ad95c032e6656555b89c6e5203
```

### Interpretation

Iteration 4 is the first N25.2 source-current runtime probe. It runs the closed
LGRC9V3 implementation with native multi-basin policy enabled and emits one
post-refinement flow-window record plus one child-basin state record. The
runtime evidence is embedded in this JSON artifact, so I4 records an embedded
payload manifest with JSON-pointer fragments and canonical digests rather than
repo-relative external trace paths. The child-basin record includes
support/coherence/boundary/flux fields, old-basin relation provenance,
merge/leakage trace, runtime-visible inputs, non-load-bearing producer-residue
status, native runtime-emitted source-current status, and a trace digest.

The topology/refinement provenance is explicitly
`collapse_reabsorption_shaped_existing_graph`: it is admissible for MB3
candidate emission, but it is not yet independent new-basin formation or
multi-basin substrate persistence. I6 must fail-close the
collapse/reabsorption relabel, old-basin thickening relabel,
transient-flow-sink relabel, and label-only basin formation controls before I4
can contribute to any stronger claim.

The result is a positive source-current candidate only:

```text
MB3 source-current child-basin candidate emission
```

It is not replay-backed MB4, not control-backed MB5, and not MB6. Replay,
controls, stress, and MB6 gate application remain pending for later iterations.

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_native_runtime_positive_probe.py
passed
```

## Iteration 4-A. Native Runtime Variant / Companion Probe

Status: passed.

### Goal

Run at least one alternative native runtime probe without changing the
implementation.

### Checks

- [x] Run a source-backed variant or companion fixture.
- [x] Prefer front-capacity boundary-birth companion and/or topology/seed
      variation already supported by the closed runtime.
- [x] Confirm the variant is not a retuned copy of I4.
- [x] Record declared variant axis and comparability digest.
- [x] Confirm variant evidence cannot backfill unrelated MB5 rows.
- [x] Emit comparable flow-window and child-basin records.
- [x] Preserve producer/native mutation discipline.
- [x] Confirm no implementation source is modified.
- [x] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_native_runtime_variant_probe.json
reports/n25_2_native_runtime_variant_probe.md
```

### Result

```text
status = passed
acceptance_state = accepted_native_runtime_variant_and_front_capacity_companion_mb3_scope_no_mb6
i4_output_digest = 1a38c59b8e3149a4cdde1861237e45a0e9f2da8ecca6f548bf462313149527f1
failed_checks = []
runtime_execution_performed = true
runtime_execution_from_closed_implementation = true
native_runtime_variant_probe_opened = true
variant_probe_role = additional_runtime_variety_evidence_not_replacement
i4_replaced = false
i4_mb5_or_mb6_backfilled = false
route_variant_candidate = MB3_source_current_child_basin_candidate_emission_variant
route_variant_child_basin_core_ids = [2]
route_variant_topology_provenance_shape = collapse_reabsorption_shaped_existing_graph
front_capacity_companion_candidate = not_assigned_topology_birth_companion_only
front_capacity_initial_node_count = 13
front_capacity_final_node_count = 14
front_capacity_initial_edge_count = 12
front_capacity_final_edge_count = 13
front_capacity_visible_topology_growth = true
front_capacity_parent_eligibility_mode = grcl9v3_front_capacity
front_capacity_backfill_allowed = false
variant_evidence_cannot_backfill_unrelated_mb5_rows = true
artifact_manifest_scope = embedded_payloads_only
embedded_artifact_manifest_count = 3
mb6_gate_status = not_applied
mb6_supported = false
mb6_claim_allowed = false
n26_unscoped_consumption_allowed = false
n26_consumption_effect = unscoped_consumption_blocked
output_digest = f2a49eab162893564433286d8e12bad8c3f4b3891f2f0007857ec23ae2d83d07
artifact_sha256 = 1ed05789f0d062e3058a891d55af2da3be7d26a6bd19eb1825bda3af536246f7
report_sha256 = 962739cca4eaecedaa21aaf8e2bf8c54ed714a4ec252f6cedfaf5966ba589a69
```

### Interpretation

Iteration 4-A adds runtime variety without replacing I4. It records two
source-current companion probes from the closed runtime:

```text
route_child_basin_variant:
  same compact multi-basin fixture family
  different selected native route sink
  comparable flow-window and child-basin state records
  child-basin core changes from I4 [0] to I4-A [2]

front_capacity_boundary_birth_companion:
  corrected front-capacity parent eligibility
  visible topology growth from 13 to 14 nodes and 12 to 13 edges
  companion context only, not a child-basin persistence row
```

The route variant strengthens MB3 source-current child-basin candidate emission
by showing the record family is not confined to the I4 selected sink. The
front-capacity companion strengthens the provenance story by showing the closed
runtime can also express source-current topology growth through corrected
front-capacity boundary birth. It does not backfill the I4/I4-A child-basin
record, does not upgrade MB5, and does not support MB6.

I4-A remains below replay-backed MB4, control-backed MB5, MB6, and N26
unscoped consumption. I5 must replay runtime-emitted child-basin records, and
I6 must still run fail-closed controls.

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_native_runtime_variant_probe.py
passed
```

## Iteration 5. Replay And Persistence Matrix

Status: passed.

### Goal

Replay I4/I4-A runtime-emitted artifacts and validate child-basin persistence.

### Checks

- [x] Run artifact replay.
- [x] Run snapshot/load replay.
- [x] Run duplicate replay.
- [x] Run multi-window child-basin persistence replay.
- [x] Confirm reconstruction validates runtime-emitted records only.
- [x] Confirm missing or failed replay blocks MB6.
- [x] Confirm no implementation source is modified.
- [x] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_replay_persistence_matrix.json
reports/n25_2_replay_persistence_matrix.md
```

### Result

```text
status = passed
acceptance_state = accepted_replay_persistence_matrix_mb4_candidates_no_mb5_no_mb6
i4_output_digest = 1a38c59b8e3149a4cdde1861237e45a0e9f2da8ecca6f548bf462313149527f1
i4a_output_digest = f2a49eab162893564433286d8e12bad8c3f4b3891f2f0007857ec23ae2d83d07
failed_checks = []
candidate_row_count = 2
mb4_replay_candidate_count = 2
multi_window_child_basin_persistence_replay_status = passed
persistence_claim_kind = replay_persistence_of_emitted_child_basin_records
long_horizon_persistence_supported = false
extended_multi_window_survival_under_stress_supported = false
matrix_window_count = 2
runtime_record_window_count_per_row = [1.0, 1.0]
replay_rows = [i4_reference_child_basin_core_0, i4a_route_variant_child_basin_core_2]
i4_reference_child_basin_core_0_replay_modes = passed/passed/passed/passed
i4_reference_child_basin_core_0_duplicate_first_second_emitted = true/false
i4_reference_child_basin_core_0_ratios = 1.0/1.0/1.0/1.0/1.0
i4a_route_variant_child_basin_core_2_replay_modes = passed/passed/passed/passed
i4a_route_variant_child_basin_core_2_duplicate_first_second_emitted = true/false
i4a_route_variant_child_basin_core_2_ratios = 1.0/1.0/1.0/1.0/1.0
front_capacity_companion_replay_scope = not_applicable
front_capacity_companion_child_basin_replay_consumption_allowed = false
front_capacity_companion_carry_forward_to_i6_i7_as = provenance_context_only
mb_ladder_candidate = MB4_replay_backed_child_basin_persistence_candidate
mb5_or_stronger_supported = false
required_iteration_6_control_count = 10
mb6_gate_status = not_applied
mb6_supported = false
mb6_claim_allowed = false
n26_unscoped_consumption_allowed = false
n26_consumption_effect = unscoped_consumption_blocked
ready_for_iteration_6_fail_closed_control_matrix = true
output_digest = 8d9163901e664ba8217ebe72389f99c34141dfbff76c81ee5f57f6e4e4484699
artifact_sha256 = 58146a72e5e67b840505041fe8a3f33f987fba8bf3987d5130792a1d50d33de7
report_sha256 = bba38d472012481ec603aa38870a526f14744c6cb410aad81e63d5e01e84943a
```

### Interpretation

Iteration 5 validates replay-backed persistence for the two runtime-emitted
child-basin candidates:

```text
I4 reference child-basin core [0]
I4-A route-variant child-basin core [2]
```

Both rows pass the native replay validator with artifact replay,
snapshot/load replay, duplicate replay, and time-order replay all `passed`.
Their membership, support, coherence, boundary, and flux persistence ratios
are all exactly `1.0`.

The matrix-level multi-window result means I5 covers two source-current
child-basin candidate windows. Each runtime replay validation record remains a
one-window native replay row, which is the current runtime contract. I5
therefore supports replay persistence of emitted child-basin records, not
extended multi-window survival under stress or long-horizon child-basin
persistence. I7 must test stress and window variation.

For duplicate replay, `first_emitted = true` and `second_emitted = false`
means idempotency worked: the first replay emitted the validation record, while
the second replay suppressed a duplicate and returned the same digest.

The I4-A front-capacity boundary-birth companion is intentionally not replayed
as a child-basin row. It remains topology-growth companion evidence only and
cannot backfill child-basin persistence, MB5, or MB6. I6/I7 should carry it
forward only as provenance context.

I5 supports only:

```text
MB4 replay-backed child-basin persistence candidate
```

It does not run fail-closed controls, does not support MB5, does not apply the
MB6 gate, and does not open N26 unscoped consumption. I6 must still fail-close
label-only basin formation, old-basin thickening, transient sink,
collapse/reabsorption relabel, visual-only success, hidden producer insertion,
producer-as-native, front-capacity backfill, MB5-as-MB6, and unsafe relabel
controls.

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_replay_persistence_matrix.py
passed
```

## Iteration 5-A. Multi-Window Persistence Replay

Status: passed.

### Goal

Obtain explicit multi-window child-basin persistence replay evidence from the
closed LGRC9V3 runtime before the I6 control matrix and I7 stress matrix consume
the candidates.

### Checks

- [x] Load closed I4/I4-A runtime snapshots.
- [x] Replay each emitted child-basin candidate across three runtime snapshot
      windows.
- [x] Confirm child-basin state records remain present in every replay window.
- [x] Confirm replay modes pass in every replay window.
- [x] Confirm persistence ratios remain exact in every replay window.
- [x] Confirm duplicate replay suppression remains stable.
- [x] Confirm the aggregate trace is replay evidence, not a runtime
      implementation change.
- [x] Confirm no implementation source is modified.
- [x] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_multi_window_persistence_replay.json
reports/n25_2_multi_window_persistence_replay.md
```

### Result

```text
status = passed
acceptance_state = accepted_multi_window_persistence_replay_mb4_extension_no_mb6
i5_output_digest = 8d9163901e664ba8217ebe72389f99c34141dfbff76c81ee5f57f6e4e4484699
failed_checks = []
candidate_count = 2
declared_replay_window_count = 3
runtime_snapshot_window_count_per_candidate = [3, 3]
multi_window_passed_candidate_count = 2
all_window_child_basin_records_present = true
all_window_replay_results_passed = true
all_window_replay_ratios_exact = true
duplicate_replay_suppression_observed = true
eventful_stress_window_supported = false

mb_ladder_candidate = MB4_multi_window_replay_backed_child_basin_persistence_candidate
mb5_or_stronger_supported = false
mb6_supported = false
n26_unscoped_consumption_allowed = false
ready_for_iteration_6_fail_closed_control_matrix = true
ready_for_iteration_7_stress_variant_matrix = true
output_digest = c297e0ef20296c37d54717df4d4d0adc3c44944e5fc2f828fd22ff789e67ec0a
artifact_sha256 = 018cadd02b547421441f254f2b2f632548bd4bfe97e71c55604d987073efbfd7
report_sha256 = f09e3886713a43fefca295118668ef8d5845e350556ba96c700faf7e7b3f0455
```

### Interpretation

Iteration 5-A supplies the missing multi-window replay evidence for the two
runtime-emitted child-basin candidates. Each candidate is replayed across three
closed-runtime snapshot windows; in every window, the child-basin state record
remains present and replay ratios remain exactly `1.0`.

This corrects the earlier I7 limitation. The native replay validator still
emits one-window validation records, but I5-A provides an aggregate
source-current multi-window replay trace built from repeated closed-runtime
snapshots. It can be consumed by I8 as multi-window persistence replay evidence.

The claim remains bounded:

```text
multi-window replay-backed child-basin persistence candidate
```

It is not eventful stress persistence, MB5 by itself, MB6 by itself, native
support, agency, or Phase 8 completion.

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_multi_window_persistence_replay.py
passed
```

## Iteration 6. Fail-Closed Control Matrix

Status: passed.

### Goal

Run fail-closed controls against runtime-emitted candidates.

### Checks

- [x] Run label-only basin formation control.
- [x] Run old-basin thickening relabel control.
- [x] Run transient flow sink relabel control.
- [x] Run collapse/reabsorption relabel control.
- [x] Run graph-visual-only success control.
- [x] Run hidden producer basin insertion control.
- [x] Run producer success as native support control.
- [x] Run front-capacity backfill control.
- [x] Run MB5-as-MB6 relabel control.
- [x] Run unsafe semantic / agency / native-support relabel controls.
- [x] Confirm controls fail closed.
- [x] Confirm failed-open controls block MB6.
- [x] Confirm no implementation source is modified.
- [x] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_fail_closed_control_matrix.json
reports/n25_2_fail_closed_control_matrix.md
```

### Result

```text
status = passed
acceptance_state = accepted_fail_closed_controls_mb5_candidates_no_mb6
i5_output_digest = 8d9163901e664ba8217ebe72389f99c34141dfbff76c81ee5f57f6e4e4484699
i5a_output_digest = c297e0ef20296c37d54717df4d4d0adc3c44944e5fc2f828fd22ff789e67ec0a
failed_checks = []
control_candidate_count = 2
mb5_control_backed_candidate_count = 2
runtime_required_control_count = 17
supplemental_experiment_control_count = 4
multi_window_replay_passed_candidate_count = 2
multi_window_replay_window_count_per_candidate = [3, 3]
control_record_count_per_candidate = [21, 21]
failed_open_control_count = 0
all_controls_failed_closed = true
i4_reference_child_basin_core_0_control_record_count = 21
i4_reference_child_basin_core_0_clean_replay_present = true
i4_reference_child_basin_core_0_mb5_control_backed_candidate_allowed = true
i4a_route_variant_child_basin_core_2_control_record_count = 21
i4a_route_variant_child_basin_core_2_clean_replay_present = true
i4a_route_variant_child_basin_core_2_mb5_control_backed_candidate_allowed = true
front_capacity_control_scope = provenance_context_only
front_capacity_backfill_control_status = failed_closed
front_capacity_mb5_or_mb6_backfill_allowed = false
mb_ladder_candidate = MB5_control_backed_native_multi_basin_candidate
mb6_gate_status = not_applied
mb6_supported = false
mb6_claim_allowed = false
n26_unscoped_consumption_allowed = false
n26_consumption_effect = unscoped_consumption_blocked
ready_for_iteration_7_stress_variant_matrix = true
output_digest = 62d1213a2a31b2704a064cb53a23cf1838e08850b92508a5cf6b592cfeee4011
artifact_sha256 = 09c92e5f7c52bb0edfb89a3012e0544a6ad9d905ea1416c764b3c7d8e88e27ea
report_sha256 = c177c83496cc433458b946f6e843020b64f035b0c1c72981853fdab781c18e4f
```

### Interpretation

Iteration 6 consumes the I5 replay-backed child-basin candidates and runs the
fail-closed control matrix against both:

```text
I4 reference child-basin core [0]
I4-A route-variant child-basin core [2]
```

For each candidate, the matrix records the 17 runtime-required controls plus 4
N25.2 supplemental controls:

```text
collapse/reabsorption relabel control
graph-visual-only success control
front-capacity backfill control
MB5-as-MB6 relabel control
```

All controls fail closed, no failed-open controls appear, clean I5 replay and
I5-A multi-window replay are present for each candidate, and control idempotency
is stable. This is the first N25.2 point that supports:

```text
MB5 control-backed native multi-basin candidate
```

The result remains bounded. It is not MB6, not N26 substrate consumption, not
native support, not agency, and not Phase 8 completion. I7 must still test
stress/window variation, and I8 must still apply the MB6 gate.

The I4-A front-capacity topology-birth companion remains provenance context
only. Its backfill control fails closed, so it cannot be used as child-basin
control evidence or as an MB5/MB6 upgrade.

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_fail_closed_control_matrix.py
passed
```

## Iteration 7. Stress / Threshold / Variant Matrix

Status: passed.

### Goal

Stress the strongest replay/control-backed native multi-basin candidate without
modifying runtime implementation.

### Checks

- [x] Stress flow-window thresholds.
- [x] Stress merge/leakage pressure.
- [x] Stress child-basin persistence window.
- [x] Stress front-capacity / boundary-birth provenance where applicable.
- [x] Stress seed or topology fixture variation where source-backed.
- [x] Record whether evidence remains MB5, strengthens toward MB6, or exposes
      repair target.
- [x] Confirm no implementation source is modified.
- [x] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_stress_variant_matrix.json
reports/n25_2_stress_variant_matrix.md
```

Result:

```text
status = passed
acceptance_state = accepted_stress_variant_matrix_mb5_retained_multi_window_ready_pending_gate
output_digest = 1759dbb4d8c85c27bc056108f04fea3cfcc1c59b5ee9518ebb7f641e60949627
artifact_sha256 = ad303bb671707d877d80f4a2baa05b99f4d28d658f99f65a28c266fab96462b5
report_sha256 = ca1d8ee65578789a5ab96d7cc3c3ee4bd9b11d9cabeae91549f854c97794d8de

stress_candidate_count = 2
mb5_retained_candidate_count = 2
source_threshold_pass_count = 2
tightened_threshold_fail_closed_count = 2
source_merge_leakage_pass_count = 2
injected_pressure_fail_closed_count = 2
source_one_window_replay_pass_count = 2
extended_multi_window_pass_count = 4
extended_multi_window_blocker_count = 0
unexpected_failed_open_stress_count = 0
variant_axis_supported = true
front_capacity_boundary_scope_preserved = true

mb_ladder_candidate = MB5_stress_bounded_native_multi_basin_candidate
mb5_retained_after_i7 = true
mb5_demoted = false
mb6_supported = false
mb6_blockers = [
  mb6_gate_pending_iteration_8
]
n26_unscoped_consumption_allowed = false
ready_for_iteration_8_mb6_support_blocker_matrix = true
```

Interpretation:

Iteration 7 keeps both I6 MB5 candidates alive under stress. The reference
I4 child-basin core `[0]` and I4-A route-variant child-basin core `[2]` both
preserve their source-threshold replay, source merge/leakage ceiling, one-window
replay, and fail-closed behavior under tightened-threshold and injected-pressure
stress.

This strengthens the MB5 record, but it does not support MB6 by itself because
I8 still has to apply the MB6 gate. I7 now consumes I5-A multi-window replay
evidence: each candidate has a three-window closed-runtime persistence trace
with exact replay ratios. The previous missing multi-window replay blocker is
therefore removed from I7 and replaced by the narrower pending-I8 gate blocker.

The front-capacity / boundary-birth companion remains provenance context only.
It cannot backfill child-basin stress, MB5, MB6, or N26 substrate consumption.

Allowed claim:

```text
stress-bounded MB5 native multi-basin candidate
```

Blocked claims:

```text
MB6 support
N26 unscoped substrate consumption
native support
agency
semantic learning or choice
sentience
Phase 8 completion
ant ecology implementation
```

## Iteration 8. MB6 Support / Blocker Matrix

Status: passed.

### Goal

Apply the MB6 gate and classify N26 consumption.

### Checks

- [x] Apply all MB6 gates to I3-I7 evidence.
- [x] Record support/blocker status per gate.
- [x] Record whether MB6 is supported.
- [x] Record exact blocker list if MB6 is blocked.
- [x] Record N26 consumption effect.
- [x] Confirm N25.2-C closeout rung remains separate from MB ladder support.
- [x] Confirm no implementation source is modified.
- [x] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_mb6_support_blocker_matrix.json
reports/n25_2_mb6_support_blocker_matrix.md
```

Result:

```text
status = passed
acceptance_state = accepted_mb6_supported_scoped_n26_consumption
output_digest = 06439fce5f6fa7baee0047e259f66ad12e5fb77d32f7f20750a2d4f23318c728
artifact_sha256 = c05826b383c2df29b565eee22138ee2cc8587bcdd4452f38cde16db65467e199
report_sha256 = 7d1bf3be29a4dfaa433b9a4b817f2ef982b8b5dfc6c4166a2e0ef49ba669ed46

gate_count = 17
passed_gate_count = 17
blocked_gate_count = 0
blocked_gate_ids = []
mb5_demoted = false
mb6_supported = true
mb6_gate_status = supported
n26_consumption_effect = scoped_mb6_substrate_consumption_allowed
n26_scoped_context_consumption_allowed = true
n26_unscoped_multi_basin_consumption_allowed = false
n25_2_closeout_ceiling = N25.2-C5_N26_consumption_classification_complete_pending_closeout
n25_2_c6_closeout_pending_iteration_9 = true
ready_for_iteration_9_closeout_and_n26_handoff = true
```

Interpretation:

Iteration 8 applies the I2 MB6 gate to the full I3-I7 evidence chain. All
17 required MB6 gates pass:

```text
source inventory admissible
Phase 8 MB5 chain validated
source-backed multi-basin runtime surfaces
source-backed child-basin state records
multi-window child-basin persistence replay
artifact/snapshot/duplicate replay clean
merge/leakage controls fail closed
producer/native mutation ownership clean
front-capacity provenance bounded when used
hidden producer insertion rejected
label-only basin formation rejected
old-basin thickening relabel rejected
transient flow-sink relabel rejected
graph-visual-only success rejected
visual evidence remains corroboration-only
N26 consumption rule explicit
unsafe claim flags false
```

Allowed claim:

```text
MB6 N26-ready multi-basin substrate evidence
```

N26 consumption is explicitly scoped:

```text
scoped multi-basin substrate evidence only
```

Blocked claims remain:

```text
unscoped N26 consumption
native support
semantic learning or choice
agency
identity acceptance
sentience
organism/life
ant ecology implementation
Phase 8 completion
unrestricted autonomy
```

N25.2-C6 remains pending for Iteration 9 closeout. The N25.2 closeout rung is
not the same thing as MB6 support.

## Iteration 9. Closeout And N26 Handoff

Status: passed.

### Goal

Close N25.2 and hand off to N26 with explicit MB status.

### Checks

- [x] Record final MB status.
- [x] Record final N25.2-C rung.
- [x] Record final N26 consumption permission.
- [x] Record whether MB6 is supported or blocked.
- [x] Record whether MB5 remains valid or was demoted.
- [x] Record all remaining blockers.
- [x] Confirm source artifacts are repo-relative.
- [x] Confirm unsafe claims remain false.
- [x] Confirm no implementation source was modified.
- [x] Record any implementation defect as blocker or repair target only.

Expected artifacts:

```text
outputs/n25_2_closeout_and_n26_handoff.json
reports/n25_2_closeout_and_n26_handoff.md
```

Result:

```text
status = passed
acceptance_state = accepted_n25_2_c6_closeout_scoped_n26_handoff
output_digest = b92401da545899c7721ab42692827beb5b357bbd246d8991d7ad56649a6bbf03
artifact_sha256 = 7cb419ae2ed31b297f65f50654c650cc755f9edc0feaef2acfb2c85225b6e328
report_sha256 = e3682bfb8b40f91a4647f5acbb5961932642ebbb58dcebf282e711314320f35d

final_mb_ladder_rung = MB6_N26_ready_multi_basin_substrate_evidence
mb6_supported = true
mb5_remains_valid = true
mb5_demoted = false
mb6_blockers = []
final_n25_2_closeout_rung = N25.2-C6_closeout_and_N26_handoff_complete
n26_consumption_effect = scoped_mb6_substrate_consumption_allowed
n26_scoped_context_consumption_allowed = true
n26_unscoped_multi_basin_consumption_allowed = false
```

Interpretation:

Iteration 9 closes N25.2. The final MB ladder status is `MB6`, because I8
passed all MB6 gates. The final N25.2 closeout rung is `N25.2-C6`, because
the MB6 result and the scoped N26 handoff are now recorded.

The handoff to N26 is intentionally scoped:

```text
N26 may consume N25.2 as scoped multi-basin substrate evidence.
N26 may not consume N25.2 as unscoped multi-basin substrate, native support,
agency, sentience, ant ecology implementation, or Phase 8 completion.
```

The Phase 8 MB5 evidence remains valid and is not demoted. No implementation
defect was found or repaired inside N25.2.
