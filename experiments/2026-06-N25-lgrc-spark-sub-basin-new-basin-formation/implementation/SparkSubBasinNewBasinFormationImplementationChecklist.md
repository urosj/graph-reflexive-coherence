# N25 Implementation Checklist - Spark / Sub-Basin / New-Basin Formation

## Global Guards

- [x] Consume N20 contract row `n20_i4_row_06_spark_sub_basin_new_basin_formation`.
- [x] Consume N20 same-basin row `n20_i5_row_06_spark_sub_basin_new_basin_formation`.
- [x] Consume N24 native lane as AB5 / N24-C5 context only.
- [x] Consume N24 I7-C producer-assisted lane separately.
- [x] Preserve native N24 flux/leakage debt row-locally.
- [x] Prevent producer-assisted success from upgrading native N24-C6.
- [x] Prevent producer-assisted success from upgrading native BF.
- [x] Require row-level lane ceilings for every row.
- [x] Prevent N24 optionality from being relabeled as N25 basin formation.
- [x] Record that existing LGRC/LGRC9V3 spark mechanisms are expected and must be checked first.
- [x] Prevent new producer code from being introduced before native spark/example paths are considered.
- [x] Keep AP4/AP5 gap handling row-local.
- [x] Keep agency, semantic choice, native support, sentience, Phase 8, and ant ecology blocked.
- [x] Avoid absolute paths in records.

Global guard freeze note:

```text
Iterations 1 and 2 freeze source consumption, lane separation, row-level lane
ceilings, native flux-debt handling, producer-assisted non-upgrade policy,
formation classifications, artifact roles, AP4/AP5 discipline, and unsafe
claim blockers.
They also freeze the native-spark-first policy: N25 must inspect and reuse
existing LGRC/LGRC9V3 spark mechanisms/examples before adding producer code.

Positive runtime-row obligations remain unchecked until candidate rows exist.
They must be satisfied by I4+ before BF support can be admitted.
```

## Iteration 1. Source And Handoff Inventory

- [x] Read N20 native-function/proxy contract.
- [x] Read N20 same-basin/continuation contract.
- [x] Read N24 closeout and N25 handoff.
- [x] Read N24 I7-C producer flux-conditioning artifact.
- [x] Read `examples/lgrc9v3` spark-related example context.
- [x] Verify N20 spark/sub-basin/new-basin rows exist.
- [x] Verify existing LGRC9V3 spark-ish examples are available.
- [x] Verify N24 native lane is AB5 / N24-C5.
- [x] Verify native N24-C6 is blocked.
- [x] Verify producer-assisted N24 lane is available only as separate scaffold.
- [x] Record source digests and roles.
- [x] Assign no BF rung.
- [x] Open no positive N25 evidence.

Expected artifacts:

```text
outputs/n25_source_handoff_inventory.json
reports/n25_source_handoff_inventory.md
scripts/build_n25_source_handoff_inventory.py
```

Iteration 1 result:

```text
status = passed
acceptance_state = accepted_source_handoff_inventory_no_basin_formation_evidence
failed_checks = []
output_digest = f266f8719937c4d2b84be5c87a1be460bc384d698300dc79ad443c839787bce2
source_contract_row = n20_i4_row_06_spark_sub_basin_new_basin_formation
source_consumable_contract_row = n20_i5_row_06_spark_sub_basin_new_basin_formation
n24_native_lane = AB5_N24-C5_surplus_supported_optionality
n24_native_c6_supported = false
n24_native_flux_debt = flux_envelope_not_widened_above_1e-9
n24_producer_assisted_lane = producer_mediated_flux_conditioning_scaffold
existing_lgrc9v3_spark_examples_available = true
bf_ladder_rung_assigned = false
n25_closeout_ladder_rung = N25-C0_inventory_only
ready_for_iteration_2_schema_freeze = true
```

Iteration 1 interpretation:

```text
I1 is a source handoff inventory only. It validates N20's N25 primitive rows,
consumes N24 native AB5/N24-C5 as prerequisite optionality context, records
N24 native C6 as blocked by the 1e-9 flux/leakage debt, and records I7-C as a
separate producer-assisted flux scaffold. It does not support BF evidence,
new-basin formation, semantic learning, choice, agency, native support,
sentience, Phase 8, or ant ecology.
It also records that native LGRC/LGRC9V3 spark behavior already exists and
must be considered before producer extensions.

Review follow-up:

```text
unsafe_claim_flags now include semantic_learning, reward_maximization, and
ant_ecology_specification in addition to the previous blocked claim set.
```

## Iteration 2. Basin-Formation Schema And Controls

- [x] Freeze positive candidate row schema.
- [x] Freeze lane enum: `native`, `producer_assisted`.
- [x] Freeze row-level lane ceilings.
- [x] Freeze cross-field lane invariants.
- [x] Freeze native-row `n24_producer_lane_status = not_used_in_native_row`.
- [x] Freeze `producer_assisted_result_class` enum.
- [x] Freeze sub-basin versus new-basin definitions.
- [x] Freeze `formation_class` enum.
- [x] Freeze `bifurcation_partial` formation class for BF2 rows.
- [x] Freeze `formation_source` enum.
- [x] Freeze required source-current fields.
- [x] Freeze row-level digest/provenance fields.
- [x] Freeze native spark source policy.
- [x] Freeze temporal/window fields.
- [x] Freeze old-basin/candidate-basin signature digest fields.
- [x] Freeze distinguishability metrics.
- [x] Freeze explicit artifact roles.
- [x] Freeze BF0...BF6 ladder.
- [x] Freeze N25-C0...N25-C6 closeout ladder.
- [x] Freeze native flux debt handling.
- [x] Freeze producer-assisted flux bounds from I1.
- [x] Freeze producer-residue and naturalization-debt classifications.
- [x] Freeze replay requirements.
- [x] Freeze AP4/AP5 dependency statuses.
- [x] Freeze row decision policy.
- [x] Freeze active-null versus positive-row control status semantics.
- [x] Freeze I1-to-I2 control alias map.
- [x] Freeze fail-closed controls.
- [x] Confirm no positive N25 evidence is opened.

Expected artifacts:

```text
outputs/n25_basin_formation_schema_and_controls.json
reports/n25_basin_formation_schema_and_controls.md
scripts/build_n25_basin_formation_schema_and_controls.py
```

Iteration 2 result:

```text
status = passed
acceptance_state = accepted_basin_formation_schema_controls_frozen_no_positive_evidence
failed_checks = []
output_digest = 17511cc4a21aee172d0f80600c55636701e97af4c1c46f6578411b4e97c7192f
bf_ladder_rung_assigned = false
n25_closeout_ladder_rung = N25-C0_schema_only
basin_formation_evidence_opened = false
ready_for_iteration_3_active_nulls = true
```

Iteration 2 interpretation:

```text
I2 freezes the admissibility contract for later N25 rows. Positive candidate
rows must carry explicit native or producer-assisted lane ceilings, formation
class/source enums, distinguishability margins, native flux-debt status,
producer-residue/naturalization-debt records, AP4/AP5 statuses, artifact roles,
and fail-closed controls. It opens no positive basin-formation evidence.

Review follow-up:

```text
I2 now freezes active-null versus positive-row control status semantics:
  active-null false positives expect failed_closed
  positive candidate rows expect blocker absence as passed
  failed_open blocks row and closeout upgrade
  not_run blocks dependent rung
  not_applicable requires scope reason

I2 also freezes I1-to-I2 control aliases, source/provenance digest fields,
artifact path/SHA equality fields, temporal formation windows, old/candidate
basin signature digests, lane cross-field invariants, producer-assisted flux
bounds, and expanded artifact roles.
It additionally freezes that existing LGRC/LGRC9V3 spark examples must be
considered before new producer code is introduced.
Positive rows must use full `control_results`; active-null sentinel values are
allowed only when `schema_instantiation_only = true` and
`positive_evidence_admissible = false`.
```

## Iteration 3. Active Nulls And Failure Baselines

- [x] Instantiate label-only new-basin null.
- [x] Instantiate single-basin thickening relabel null.
- [x] Instantiate reshaped-old-boundary-only null.
- [x] Instantiate merge/leakage-as-basin null.
- [x] Instantiate non-replayable transient null.
- [x] Instantiate hidden producer insertion null.
- [x] Instantiate N24 optionality relabel null.
- [x] Instantiate producer-assisted native-upgrade relabel null.
- [x] Instantiate native flux debt omitted null.
- [x] Instantiate AP gap prose-only null.
- [x] Instantiate unsafe semantic/agency/native-support/Phase-8 relabel nulls.
- [x] Instantiate existing-LGRC9V3-spark-examples-skipped null.
- [x] Instantiate producer-before-native-spark-path null.
- [x] Confirm all fail closed.
- [x] Assign no BF rung above active-null scope.

Expected artifacts:

```text
outputs/n25_active_nulls_and_failure_baselines.json
reports/n25_active_nulls_and_failure_baselines.md
scripts/build_n25_active_nulls_and_failure_baselines.py
```

Iteration 3 result:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_basin_formation_evidence
failed_checks = []
output_digest = 857e88aa4efbbe55458e538a29803e4f7b4731c5bf1872a56c303073797441c9
active_null_count = 14
failed_open_rows = []
bf_ceiling = BF0_active_null_control_scope
n25_closeout_ceiling = N25-C1_active_nulls_fail_closed
n25_closeout_ladder_rung_assigned = false
basin_formation_evidence_opened = false
ready_for_iteration_4_native_bifurcation_probe = true
```

Iteration 3 interpretation:

```text
I3 is a pre-positive false-positive rejection artifact. It rejects label-only
new-basin claims, old-basin thickening, reshaped old boundary, merge/leakage,
non-replayable transient sparks, hidden producer insertion, N24 optionality
relabels, producer-assisted native upgrades, omitted native flux debt, prose-only
AP handling, unsafe semantic/native-support claims, and bypassing existing
LGRC9V3 spark examples. It does not provide BF evidence or source-current
basin-formation support.
It also records full `control_results` per null row and clarifies that
`native_flux_debt_omitted` is blocked because the flux-debt record is omitted,
not widened.
The plan I3 list now enumerates all 14 active null rows, including the split
unsafe-claim rows and the two native-spark-first guard rows. I3 rows now also
carry `n20_source_contract_row`, `n20_consumable_contract_row`, `row_digest`,
and a row-level `output_digest` alias for schema-name consistency.
```

## Iteration 4. Native Optional-Branch Bifurcation Probe

- [x] Build source-current native bifurcation probe under N24 native lane.
- [x] Preserve inherited `1e-9` flux/leakage bound.
- [x] Record `native_flux_debt_bound = 1e-9`.
- [x] Record `native_flux_debt_widened = false`.
- [x] Record `native_flux_debt_status`.
- [x] Record bifurcation trace.
- [x] Record new boundary candidate trace.
- [x] Record support/coherence floor traces for candidate region.
- [x] Record old-basin relation trace.
- [x] Record formation class and formation source.
- [x] Record distinguishability margins.
- [x] Reject label-only and old-basin thickening interpretations.
- [x] Keep producer-assisted lane out of native row.

Expected artifacts:

```text
outputs/n25_native_bifurcation_probe.json
reports/n25_native_bifurcation_probe.md
scripts/build_n25_native_bifurcation_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_native_source_current_bf2_bifurcation_partial_pending_i5_controls
output_digest = 9df1111ec04d785b7f037b208062d1b660faf85a18bbe09a01d24469b4bdd652

bf_ceiling = BF2_native_source_current_bifurcation_partial
formation_class = bifurcation_partial
provisional_formation_class_target = sub_basin_candidate
bf_ladder_rung_assigned = false
provisional_bf3_candidate_pending_i5 = true
n25_closeout_ceiling = N25-C2_spark_bifurcation_partial
n25_closeout_ladder_rung_assigned = false
basin_formation_claim_allowed = false

native_flux_debt_bound = 1e-9
native_flux_debt_widened = false
native_flux_debt_status = preserved
producer_assisted_lane_opened = false
```

Review follow-up:

```text
n20_source_contract_row = n20_i4_row_06_spark_sub_basin_new_basin_formation
n20_consumable_contract_row = n20_i5_row_06_spark_sub_basin_new_basin_formation
n24_optionality_relabel_as_formation_rejected = passed
runtime_trace_artifact_role_present = true
source_current_inputs_exclude_generated_i4_outputs = true
source_commit_or_source_digest_uses_file_sha256_map = true
bifurcation_window_has_start_end_step_fields = true
boundary_candidate_window_has_start_end_step_fields = true
boundary_distinguishability_margin_formula_recorded = true
old_basin_separation_margin_kind = binary_indicator
producer_intervention_ledger_artifact_role_present = true
all_plan_controls_scoped_in_i4 = true
refinement_packet_transport_amount_total = 0.0
transport_amount_total_interpretation = structural transport event present; no measurable residual carried flux
```

Geometric interpretation:

```text
I4 reuses the existing LGRC9V3 Lane-B causal spark and active topology
integration path. A packet bounded at the inherited native flux-debt value
1e-9 reaches the saturated root sink. The Lane-B column-H spark fires at the
arrival/local-update boundary, and the active topology path emits a mechanical
expansion. Geometrically, the old root center is replaced by a module with new
module nodes and internal edges, so the result is not a label-only basin and
not merely old-basin thickening.

The result remains BF2 because the new-region support/coherence floor trace is
zero-margin and replay, transient rejection, and merge/leakage controls are not
yet run. I4 therefore records a source-current native bifurcation and a
provisional BF3 target for I5, not stable sub-basin or new-basin formation.
The refinement packet transport event is structurally present with
`amount_total = 0.0`; I4 therefore reads conservation from the expansion budget
trace (`budget_error = 0.0`) rather than treating transport as measurable
residual carried flux.
```

## Iteration 5. Native Replay And Control Matrix

- [x] Replay any native candidate.
- [x] Run label-only control.
- [x] Run thickened-old-basin control.
- [x] Run merge/leakage control.
- [x] Run transient control.
- [x] Run hidden producer control.
- [x] Confirm old-basin thickening, reshaped-boundary, merge/leakage, transient, and label-only blockers are explicit.
- [x] Determine native BF ceiling.

Expected artifacts:

```text
outputs/n25_native_replay_and_control_matrix.json
reports/n25_native_replay_and_control_matrix.md
scripts/build_n25_native_replay_and_control_matrix.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_native_bf4_replay_control_backed_sub_basin_candidate_zero_margin
output_digest = b922ab52e616e94231905e626087c07258aeb2d9adfcee349ab270a386a300db

bf_ceiling = BF4_native_replay_control_backed_sub_basin_differentiation_candidate
native_bf4_candidate_supported = true
native_bf5_supported = false
native_bf6_supported = false
n25_closeout_ceiling = N25-C4_replay_control_backed_sub_basin_differentiation_candidate
n25_closeout_ladder_rung_assigned = false
basin_formation_claim_allowed = false

runtime_replay_stable = true
artifact_reconstruction_stable = true
replay_distinction_persistence_ratio = 1.0
zero_margin_native_support_coherence_debt = true
producer_assisted_lane_opened = false
```

Review follow-up:

```text
n20_source_contract_row = n20_i4_row_06_spark_sub_basin_new_basin_formation
n20_consumable_contract_row = n20_i5_row_06_spark_sub_basin_new_basin_formation
n24_optionality_relabel_as_formation_rejected = passed
source_current_inputs_exclude_generated_i5_outputs = true
native_row_n24_producer_lane_status = not_used_in_native_row
i5_row_control_results_count = 25
i5_control_matrix_trace_count = 25
artifact_reconstruction_source_i4_output_digest_matches_current_i4 = true
merge_leakage_trace_reference_unmodified = true
merge_leakage_i5_control_status = passed
```

Geometric interpretation:

```text
I5 reruns and reconstructs the I4 native LGRC9V3 spark-to-expansion geometry.
The same event sequence, module boundary, old-center replacement,
budget-preserved expansion, native 1e-9 packet bound, and source-current
boundary digest replay deterministically. That rejects the I3 false-positive
families for label-only formation, old-basin thickening, reshaped old boundary,
transient spark, merge/leakage-as-basin, hidden producer insertion, and omitted
native flux debt.

The native ceiling therefore rises from I4 BF2 partial to a BF4
replay/control-backed sub-basin differentiation candidate. It still does not
support BF5 or BF6 because the candidate's support/coherence floors remain
zero-margin and no stress/threshold matrix has been run.
```

## Iteration 6. Producer-Assisted Flux-Conditioned Formation Probe

- [x] Consume N24 I7-C producer contract.
- [x] Keep thresholds and floors unchanged.
- [x] Record producer intervention ledger.
- [x] Record producer flux window bound.
- [x] Confirm producer flux window was declared before use.
- [x] Test producer-assisted bifurcation/sub-basin candidate.
- [x] Record producer residue and naturalization debt.
- [x] Run producer schedule post-hoc control.
- [x] Run producer hidden-support control.
- [x] Run producer threshold-relaxation control.
- [x] Run producer basin-insertion-without-trace control.
- [x] Run producer-success-as-native relabel control.
- [x] Confirm producer-assisted success does not overwrite native failure.

Expected artifacts:

```text
outputs/n25_producer_assisted_formation_probe.json
reports/n25_producer_assisted_formation_probe.md
scripts/build_n25_producer_assisted_formation_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_producer_assisted_flux_conditioned_bf4_scaffold_candidate_native_bf_unchanged
output_digest = 84dec8a317b7cf6abeb328b28c4ef1d58f9d52d5b8ae69caf0b0944b33959780

producer_assisted_lane_opened = true
producer_assisted_bf4_candidate_supported = true
producer_assisted_bf5_supported = false
producer_assisted_bf6_supported = false
native_bf_ceiling_preserved = BF4_native_replay_control_backed_sub_basin_differentiation_candidate
native_bf5_supported = false
native_bf6_supported = false
native_lane_failure_overwritten = false
producer_assisted_success_does_not_overwrite_native_failure = true
missing_native_mechanism_probe_supported = true
basin_formation_claim_allowed = false
ready_for_iteration_7_comparative_stress_boundary_matrix = true
```

Geometric interpretation:

```text
I6 keeps the I5 spark-to-expansion sub-basin trace as the native object. The
module boundary, old-center replacement, replay-stable distinction trace, and
zero-margin support/coherence surface are unchanged. The added producer is not
a basin generator and does not add support or coherence. It is a declared flux
windowing surface, consumed from N24 I7-C, that splits larger attempted flux
into source-visible windows capped at the inherited native 1e-9 per-window
bound.

The producer-assisted lane therefore supports only a BF4 producer-mediated
scaffold candidate and a missing-native-mechanism probe. It identifies
`native_flux_routing_or_rate_limiting_surface` as naturalization debt. It does
not upgrade native BF, native N24-C6, native support, semantic learning, choice,
agency, Phase 8, or ant ecology.
```

## Iteration 7. Comparative Stress And Formation Boundary Matrix

- [x] Compare native and producer-assisted candidates.
- [x] Preserve native and producer-assisted row ceilings.
- [x] Stress boundary distinguishability.
- [x] Stress support/coherence floors.
- [x] Stress merge/leakage controls.
- [x] Identify whether producer scaffold points to native naturalization target.
- [x] Keep unsafe claims false.

Expected artifacts:

```text
outputs/n25_comparative_stress_boundary_matrix.json
reports/n25_comparative_stress_boundary_matrix.md
scripts/build_n25_comparative_stress_boundary_matrix.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_comparative_bf4_boundary_matrix_bf5_blocked_n26_ready
output_digest = 0cf5c7d42e775a2e34a9cbb6bc6e31a89b2aae09e1e0785b590efd24b18e8c79

native_bf4_candidate_supported = true
native_bf5_supported = false
native_bf6_supported = false
producer_assisted_bf4_candidate_supported = true
producer_assisted_bf5_supported = false
producer_assisted_bf6_supported = false
bf5_or_stronger_supported = false
bf6_supported = false
bf_ceiling = BF4_comparative_native_and_producer_scaffold_boundary
n25_closeout_ceiling = N25-C4_comparative_bf4_with_producer_scaffold_debt
n25_closeout_ladder_rung_assigned = false
ready_for_iteration_8_closeout_and_n26_handoff = true
```

Stress-axis interpretation:

```text
I7 separates the axes rather than merging the native and producer-assisted
results into one stronger claim.

Boundary distinguishability has margin and merge/leakage controls remain clean.
The producer-assisted lane improves only the flux-scheduling axis by windowing
larger attempted flux into native-bound packets. The native flux envelope is
still not widened above 1e-9.

The support/coherence axis blocks BF5/BF6. Both the native I5 row and the
producer-assisted I6 row remain exactly at the support/coherence floor, so any
positive floor-buffer stress fails. The producer does not create a
substrate-carried new basin and does not solve support/coherence margin.

I7 therefore strengthens the diagnosis rather than upgrading the claim. N25 has
a replay/control-backed BF4 native sub-basin differentiation candidate plus a
producer-assisted flux scaffold. BF5/BF6 remain blocked by:

  zero_margin_support_coherence_floor
  producer_flux_help_not_native
  new_basin_candidate_not_established

The naturalization targets carried to closeout are:

  native_flux_routing_or_rate_limiting_surface
  positive_support_coherence_margin_for_formed_region
  new_basin_independence_beyond_sub_basin_differentiation
```

## Iteration 7-A. Native High-Margin Formation Probe

- [x] Consume the I4/I5 native source-current emitted module.
- [x] Preserve the full-module zero-margin support/coherence record.
- [x] Declare the core/shell partition rule before use.
- [x] Select positive-coherence core nodes only as support carriers.
- [x] Retain zero-coherence emitted module nodes as boundary shell.
- [x] Confirm support/coherence margins are positive for the core axis.
- [x] Confirm no producer-assisted lane contributes.
- [x] Preserve native `1e-9` flux debt.
- [x] Block positive-core relabel as full-module BF5.
- [x] Block core/shell relabel as independent new basin.
- [x] Keep unsafe claims false.

Expected artifacts:

```text
outputs/n25_native_high_margin_formation_probe_i7a.json
reports/n25_native_high_margin_formation_probe_i7a.md
scripts/build_n25_native_high_margin_formation_probe_i7a.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_native_high_margin_core_candidate_bf5_pending_replay_stress
output_digest = f3137900d167f264fa30001be5e4f5d3f8991c6af30dc49e4b0aafa3b886bec3

native_high_margin_core_candidate_supported = true
positive_core_node_count = 3
boundary_shell_node_count = 2
support_floor_margin_new_region = 10.000000001
coherence_floor_margin_new_region = 3.3333333336666664
full_module_zero_margin_preserved = true
native_bf5_supported = false
bf5_or_stronger_supported = false
bf_ceiling = BF4_native_high_margin_core_sub_basin_candidate_pending_replay_stress
n25_closeout_ceiling = N25-C4_native_high_margin_core_candidate_pending_replay_stress
ready_for_iteration_7b_high_margin_replay_controls = true
```

Geometric interpretation:

```text
I7-A does not change the LGRC9V3 run. It re-examines the native source-current
module emitted by the I4/I5 spark-to-expansion path and partitions it into a
positive-coherence core plus zero-coherence boundary shell.

This removes the zero-margin support/coherence blocker only for the
positive-core axis. The full emitted module remains zero-margin, and the core
remains attached to the boundary shell and old-basin refinement relation. I7-A
therefore supports a native high-margin core sub-basin candidate, not BF5,
independent new-basin formation, native support, semantic learning, choice,
agency, Phase 8, or ant ecology.

Remaining blockers:

  full_module_zero_margin_preserved
  positive_core_replay_control_pending
  new_basin_candidate_not_established
  native_flux_routing_or_rate_limiting_surface_not_naturalized
```

## Iteration 7-B. High-Margin Core Replay And Controls

- [x] Consume I7-A native high-margin core row.
- [x] Replay the core/shell partition.
- [x] Validate I7-A artifact reconstruction.
- [x] Confirm core replay stability.
- [x] Run positive-core post-hoc relabel control.
- [x] Run boundary-shell-as-support relabel control.
- [x] Run independent-new-basin relabel control.
- [x] Run transient control.
- [x] Preserve native flux debt.
- [x] Keep producer lane out of native core support.
- [x] Keep unsafe claims false.

Expected artifacts:

```text
outputs/n25_high_margin_core_replay_controls_i7b.json
reports/n25_high_margin_core_replay_controls_i7b.md
scripts/build_n25_high_margin_core_replay_controls_i7b.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_high_margin_core_replay_control_backed_bf5_stress_ready
output_digest = dc33c7d5ee0d59152027753c8f287fab381b283bf4ee6910039074155c1cf5ce

native_high_margin_core_replay_control_supported = true
core_replay_stable = true
artifact_reconstruction_stable = true
support_floor_margin_new_region = 10.000000001
coherence_floor_margin_new_region = 3.3333333336666664
native_bf5_supported = false
bf5_or_stronger_supported = false
bf_ceiling = BF4_native_high_margin_core_replay_control_backed_candidate
n25_closeout_ceiling = N25-C4_native_high_margin_core_replay_control_candidate_pending_stress
ready_for_iteration_7c_bf5_stress_gate = true
```

Geometric interpretation:

```text
I7-B replays and reconstructs the I7-A positive-core partition. The same three
coherence-positive core nodes, two zero-coherence shell nodes, and core/shell
boundary relation are recovered. This removes the core replay/control blocker,
but does not by itself run the BF5 stress gate.
```

## Iteration 7-C. BF5 Core Stress Gate

- [x] Consume I7-A and I7-B.
- [x] Stress positive-core support/coherence margins.
- [x] Stress boundary distinguishability.
- [x] Stress native flux/merge-leakage within inherited `1e-9` envelope.
- [x] Confirm native flux above `1e-9` fails closed.
- [x] Scope BF5 to high-margin core/sub-basin formation.
- [x] Block independent-new-basin relabel.
- [x] Keep BF6 false.
- [x] Keep producer-assisted lane out of native BF5.
- [x] Keep unsafe claims false.

Expected artifacts:

```text
outputs/n25_bf5_core_stress_gate_i7c.json
reports/n25_bf5_core_stress_gate_i7c.md
scripts/build_n25_bf5_core_stress_gate_i7c.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_scoped_native_bf5_high_margin_core_sub_basin_stress_candidate
output_digest = 2af0f3eb0cb463df1565ce73458353f96259bc103e9d9c6198aeef9695595858

native_bf5_supported = true
native_bf6_supported = false
bf5_or_stronger_supported = true
bf_ceiling = BF5_native_high_margin_core_sub_basin_stress_candidate
n25_closeout_ceiling = N25-C5_native_high_margin_core_sub_basin_stress_candidate
independent_new_basin_supported = false
ready_for_iteration_8_closeout_and_n26_handoff = true

bf5_scope = bounded_high_margin_core_sub_basin_within_native_1e-9_flux_envelope
support_floor_margin_new_region = 10.000000001
coherence_floor_margin_new_region = 3.3333333336666664
native_flux_stress_above_bound_supported = false
```

Geometric interpretation:

```text
I7-C upgrades N25 to a scoped BF5: stress/threshold-backed native high-margin
core sub-basin formation inside the inherited 1e-9 flux envelope. The core
survives nonzero support/coherence buffer stress, boundary distinguishability
stress, and merge/leakage checks at the native flux bound.

The result remains scoped. It does not support independent new-basin formation,
native flux routing above 1e-9, BF6, native support, semantic learning, choice,
agency, Phase 8, or ant ecology.

Remaining limitations:

  independent_new_basin_not_supported
  native_flux_routing_above_1e-9_not_naturalized
  full_module_zero_margin_preserved
```

## Iteration 7-D. N26 Readiness And Bounded Formation Evidence Gate

- [x] Consume I6, I7, I7-A, I7-B, and I7-C lineage.
- [x] Treat I7-C scoped BF5 as the final BF evidence ceiling.
- [x] Support N25-C6 as a handoff/readiness ceiling, not a BF6 upgrade.
- [x] Record N26 handoff constraints.
- [x] Preserve native flux debt at `1e-9`.
- [x] Carry independent-new-basin, full-module zero-margin, and producer-scaffold debts forward.
- [x] Confirm producer-assisted success does not overwrite native evidence.
- [x] Keep AP4/AP5 ledger carry-forward visible.
- [x] Keep independent-new-basin, BF6, native support, semantic learning, choice, agency, Phase 8, and ant ecology blocked.
- [x] Keep final closeout claim pending Iteration 8.

Expected artifacts:

```text
outputs/n25_n26_readiness_bounded_formation_gate_i7d.json
reports/n25_n26_readiness_bounded_formation_gate_i7d.md
scripts/build_n25_n26_readiness_bounded_formation_gate_i7d.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_n26_ready_bounded_formation_evidence_c6_bf5_scoped
output_digest = 616d948629d7c27a23b8668bb5560dca2fff7e190748951e414b7ba608b76404

n25_c6_supported = true
final_supported_bf_level = BF5_scoped_native_high_margin_core_sub_basin
native_bf5_supported = true
native_bf6_supported = false
independent_new_basin_supported = false
n25_closeout_ceiling = N25-C6_n26_ready_bounded_basin_formation_evidence
ready_for_iteration_8_closeout_and_n26_handoff = true

bf5_scope = bounded_high_margin_core_sub_basin_within_native_1e-9_flux_envelope
bounded_formation_handoff_allowed = true
basin_formation_claim_allowed = false
```

Geometric interpretation:

```text
I7-D does not change the geometry discovered by I7-C. It packages the
high-margin core/shell sub-basin as bounded formation substrate that N26 may
consume for proxy-divergence work.

The source geometry remains scoped BF5: a high-margin core inside the inherited
native 1e-9 flux envelope. C6 means the evidence is complete enough for handoff,
not that BF6 or independent new-basin formation has been shown.

The carried-forward limitations are:

  independent_new_basin_not_supported
  native_flux_routing_above_1e-9_not_naturalized
  full_module_zero_margin_preserved
  producer_flux_scaffold_not_native
  BF5_scope_not_BF6
```

## Iteration 7-E. Producer-Assisted High-Margin Scaffold Probe

- [x] Consume I6 producer-assisted flux-windowing contract.
- [x] Consume I7-C native high-margin core geometry.
- [x] Confirm I7-D C6 readiness remains preserved and not replaced.
- [x] Test larger attempted flux through producer-mediated windowing.
- [x] Keep conditioned flux per window inside native `1e-9` bound.
- [x] Confirm producer adds no hidden support or coherence.
- [x] Confirm support/coherence margin comes from I7-C source geometry.
- [x] Support only producer-assisted BF5 scaffold candidate.
- [x] Record missing native mechanism / naturalization targets.
- [x] Block producer-assisted result as native BF upgrade.
- [x] Block producer-assisted BF6 and independent new-basin relabels.
- [x] Keep unsafe claims false.

Expected artifacts:

```text
outputs/n25_producer_assisted_high_margin_scaffold_i7e.json
reports/n25_producer_assisted_high_margin_scaffold_i7e.md
scripts/build_n25_producer_assisted_high_margin_scaffold_i7e.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_producer_assisted_high_margin_bf5_scaffold_candidate_native_unchanged
output_digest = c1de0efc13c8ad1a6bb12c1296bc58d34a89552d7ef6bd51ba2e44c45139844e

producer_assisted_bf5_scaffold_supported = true
producer_assisted_bf5_supported = true
producer_assisted_bf6_supported = false
native_bf_upgraded_by_producer = false
independent_new_basin_supported = false
n25_closeout_ceiling = N25-C6_n26_ready_bounded_basin_formation_evidence
```

Geometric interpretation:

```text
I7-E combines I6 producer flux windowing with the I7-C high-margin core. The
producer does not create the core and does not add support/coherence. It exposes
larger attempted flux as declared source-visible windows that each remain within
the inherited native 1e-9 bound.

This supports a producer-assisted BF5 scaffold candidate and identifies the
missing native mechanism: LGRC would need a native flux routing / rate-limiting
surface that can preserve a high-margin core under larger attempted flux without
producer mediation.

The result does not upgrade native BF, does not replace I7-D, does not support
BF6, and does not support independent new-basin formation.
```

## Iteration 8. Closeout And N26 Handoff

- [x] Classify final BF ladder rung.
- [x] Classify final N25-C closeout rung.
- [x] Preserve AP4/AP5 ledger.
- [x] Preserve N24 native and producer-assisted lane separation.
- [x] Confirm producer-assisted success does not overwrite native BF or native N24-C6.
- [x] Confirm final formation classes and sources are recorded.
- [x] Confirm semantic learning, choice, agency, native support, sentience, Phase 8, and ant ecology remain blocked.
- [x] Confirm `src_diff_empty`.
- [x] Record N26 proxy divergence / proxy collapse handoff.

Expected artifacts:

```text
outputs/n25_closeout_and_n26_handoff.json
reports/n25_closeout_and_n26_handoff.md
scripts/build_n25_closeout_and_n26_handoff.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_n25_c6_scoped_bf5_closeout_with_producer_scaffold_context
output_digest = 2a1f19a2ce760275a223989b886c6a006ab1ccea33961b7bcf834c6cb22a565f

final_bf_level = BF5_scoped_native_high_margin_core_sub_basin
final_n25_closeout_rung = N25-C6_n26_ready_bounded_basin_formation_evidence
native_bf5_supported = true
native_bf6_supported = false
independent_new_basin_supported = false
producer_assisted_bf5_scaffold_supported = true
lgrc9v3_multi_basin_native_formation_supported = false
phase8_extension_required_for_multi_basin_formation = true
n25_1_requirements_bridge_needed = true
ready_for_n26_with_scope_constraints = true
```

Closeout interpretation:

```text
N25 closes as scoped native BF5 and N25-C6 readiness. It supports bounded
sub-basin / high-margin core formation, not independent new-basin formation,
BF6, or native LGRC9V3 multi-basin formation.

I7-E remains producer-assisted missing-mechanism evidence. It identifies the
native mechanism that would be needed later: LGRC9V3 flux routing /
rate-limiting able to preserve high-margin core formation under larger
attempted flux without producer mediation.

N26 may consume N25 only as scoped sub-basin / high-margin core substrate and
producer-assisted naturalization-target context. If N26 needs independent
multi-basin substrate evidence, a Phase 8 LGRC9V3 multi-basin formation
extension is required first.
```
