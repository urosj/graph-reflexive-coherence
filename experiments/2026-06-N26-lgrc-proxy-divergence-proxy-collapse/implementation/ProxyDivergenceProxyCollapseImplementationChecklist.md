# N26 Proxy Divergence / Proxy Collapse Implementation Checklist

## Initial Scaffold

- [x] Create N26 experiment branch.
- [x] Create experiment directory structure.
- [x] Add README with source boundary, local ladder, closeout ladder, and claim boundary.
- [x] Add hypotheses.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Keep N25.2 consumption scoped.
- [x] Keep unscoped multi-basin, native support, agency, sentience, Phase 8, and ant ecology blocked.

## Iteration 1 - Source Inventory And Scoped Substrate Admission

- [x] Read N20 proxy contract rows.
- [x] Read N15 AP5 historical gap records.
- [x] Read N25 closeout and N26 handoff.
- [x] Read N25.1 extension requirements bridge.
- [x] Read N25.2 MB6 closeout and N26 handoff.
- [x] Classify every source as evidence, context, boundary, or blocked relabel.
- [x] Confirm N25.2 scoped MB6 consumption is allowed.
- [x] Confirm unscoped MB6 consumption is blocked.
- [x] Assign no PD rung.

### Iteration 1 Result

```text
status = passed
acceptance_state = accepted_source_inventory_scoped_substrate_admission_no_proxy_evidence
source_record_count = 13
source_contract_row_digest = 5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61
source_consumable_contract_row_digest = 99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec
candidate_pd_ladder_rung = not_assigned_inventory_only
n26_closeout_ceiling = N26-C1_source_inventory_and_scoped_substrate_admission_passed
n26_closeout_ladder_rung_assigned = false
positive_proxy_evidence_opened = false
proxy_derivation_opened = false
proxy_divergence_opened = false
proxy_collapse_opened = false
ap5_bridge_status = not_supported_inventory_only
n25_2_scoped_context_consumption_allowed = true
n25_2_unscoped_consumption_allowed = false
n25_2_unscoped_multi_basin_consumption_allowed = false
failed_checks = []
output_digest = b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a
```

Interpretation: I1 admits the N25.2 result only as scoped MB6 multi-basin
substrate context for future N26 rows. It does not open proxy derivation,
proxy divergence, proxy collapse, AP5 bridge support, semantic goal evidence,
agency, native support, sentience, Phase 8 completion, ant ecology, or
unscoped multi-basin substrate claims.

Artifacts:

```text
outputs/n26_source_inventory_and_scoped_substrate_admission.json
reports/n26_source_inventory_and_scoped_substrate_admission.md
scripts/build_n26_source_inventory_and_scoped_substrate_admission.py
```

## Iteration 2 - Proxy Divergence / Collapse Schema Freeze

- [x] Freeze PD0...PD6 ladder.
- [x] Freeze N26-C0...N26-C6 closeout ladder.
- [x] Freeze candidate row schema.
- [x] Freeze I1 source digest requirements.
- [x] Freeze AP5 dependency status enum.
- [x] Freeze scoped MB6 consumption rules.
- [x] Freeze proxy metric / target digest declaration rules.
- [x] Freeze proxy policy owner enum.
- [x] Freeze artifact roles and manifest validation rules.
- [x] Freeze replay requirements.
- [x] Freeze fail-closed controls.
- [x] Confirm no positive proxy evidence opened.

Required I2 result:

```text
acceptance_state = accepted_proxy_divergence_collapse_schema_frozen_no_proxy_evidence
candidate_pd_ladder_rung = not_assigned_schema_only
n26_closeout_ceiling = N26-C2_proxy_divergence_collapse_schema_frozen
positive_proxy_evidence_opened = false
proxy_derivation_opened = false
proxy_divergence_opened = false
proxy_collapse_opened = false
ap5_bridge_status = not_supported_schema_only
```

I2 must freeze these source digests for future candidate rows:

```text
source_contract_row_digest = 5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61
source_consumable_contract_row_digest = 99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec
source_output_digest = b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a
```

Candidate rows must include scoped substrate fields:

```text
scoped_mb6_substrate_consumption_record
multi_basin_scope_id
basin_ids_or_child_basin_ids
n25_2_unscoped_consumption_allowed = false
n25_2_unscoped_multi_basin_consumption_allowed = false
front_capacity_companion_backfill_used = false
```

Positive support must be blocked if:

```text
artifact missing
sha256 mismatch
artifact role missing
derived_report_only = true
absolute path appears
AP5 handled only in prose
producer-mediated target derivation is counted as substrate
```

Artifact roles are rung-specific:

```text
PD2 = runtime/lower-stack/proxy/basin-capacity/support-coherence/report
PD3 = PD2 + basin-deepening/proxy-vs-basin/replay
PD4 = PD3 + peer-or-control-basin/control
PD5 = PD4 + proxy-optimized/basin-deepened/perturbation/collapse-result
PD6 = relevant positive-row roles + closeout
```

AP5 `not_applicable` is blocked for positive proxy rows:

```text
PD2...PD6 require ap5_dependency_status = required_recorded | missing_blocks_row
not_applicable is allowed only for inventory/schema/null rows with no proxy or target formation claim
```

Every positive row control result must include:

```text
control_satisfied_for_positive_row
```

### Iteration 2 Result

```text
status = passed
acceptance_state = accepted_proxy_divergence_collapse_schema_frozen_no_proxy_evidence
candidate_pd_ladder_rung = not_assigned_schema_only
n26_closeout_ceiling = N26-C2_proxy_divergence_collapse_schema_frozen
n26_closeout_ladder_rung_assigned = false
positive_proxy_evidence_opened = false
proxy_derivation_opened = false
proxy_divergence_opened = false
proxy_collapse_opened = false
ap5_bridge_status = not_supported_schema_only
candidate_required_field_count = 38
required_control_count = 37
failed_checks = []
output_digest = bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070
```

Interpretation: I2 freezes the proxy divergence / proxy collapse schema,
source digest requirements, scoped MB6 consumption rules, AP5 dependency enum,
proxy-policy owner enum, artifact manifest roles, replay requirements, and
fail-closed controls. It does not produce proxy derivation, proxy divergence,
proxy collapse, AP5 bridge, semantic goal, agency, native support, sentience,
Phase 8, ant ecology, or unscoped multi-basin substrate evidence.

Artifacts:

```text
outputs/n26_proxy_divergence_collapse_schema_and_controls.json
reports/n26_proxy_divergence_collapse_schema_and_controls.md
scripts/build_n26_proxy_divergence_collapse_schema_and_controls.py
```

## Iteration 3 - Active Nulls And Failure Baselines

- [x] Reject source digest mismatch rows.
- [x] Reject missing lower-stack input rows.
- [x] Reject missing proxy metric trace rows.
- [x] Reject non-replayable proxy metric rows.
- [x] Reject missing basin persistence capacity trace rows.
- [x] Reject missing support/coherence floor rows.
- [x] Reject non-independent proxy/basin measurement rows.
- [x] Reject missing scoped MB6 scope ID rows.
- [x] Reject derived-report-only positive rows.
- [x] Reject artifact manifest failure rows.
- [x] Reject proxy label-only rows.
- [x] Reject post-hoc target digest rows.
- [x] Reject hidden proxy policy rows.
- [x] Reject proxy-only improvement rows.
- [x] Reject proxy improvement when basin persistence also improves.
- [x] Reject proxy improvement when basin persistence is unmeasured.
- [x] Reject basin degradation hidden by proxy score.
- [x] Reject unscoped MB6 relabel.
- [x] Reject front-capacity companion backfill.
- [x] Reject peer-basin missing rows.
- [x] Reject perturbation mismatch rows.
- [x] Reject missing perturbation digest rows.
- [x] Reject missing basin-deepened survivor rows.
- [x] Reject missing proxy collapse result trace rows.
- [x] Reject AP5 prose-only handling.
- [x] Reject missing AP5 dependency status rows.
- [x] Reject N15 context as native AP5 rows.
- [x] Reject N19 NAT3 as AP5 closeout rows.
- [x] Reject N25.2 MB6 as native support rows.
- [x] Reject N25.2 MB6 as agency/sentience/ant-ecology rows.
- [x] Reject unsafe semantic, agency, native-support, sentience, Phase 8, and ant-ecology relabels.

Required active-null control IDs:

```text
source_digest_mismatch_control
lower_stack_input_missing_control
proxy_metric_trace_missing_control
proxy_metric_not_replayable_control
basin_persistence_capacity_trace_missing_control
support_coherence_floor_missing_control
proxy_basin_measurement_not_independent_control
scoped_mb6_scope_id_missing_control
derived_report_only_positive_row_control
artifact_manifest_failure_control
proxy_label_only_control
post_hoc_target_digest_control
hidden_proxy_policy_control
proxy_only_improvement_control
proxy_improves_basin_also_improves_control
proxy_improves_basin_unmeasured_control
basin_degradation_hidden_by_proxy_control
unscoped_mb6_consumption_control
front_capacity_backfill_control
peer_basin_missing_control
perturbation_mismatch_control
perturbation_digest_missing_control
basin_deepened_survivor_missing_control
proxy_collapse_result_trace_missing_control
AP5_gap_prose_only_control
missing_ap5_dependency_status_control
n15_context_as_native_ap5_control
n19_nat3_as_ap5_closeout_control
semantic_goal_relabel_control
semantic_choice_relabel_control
agency_relabel_control
native_support_relabel_control
n25_2_mb6_as_native_support_control
n25_2_mb6_as_agency_sentience_ant_ecology_control
sentience_relabel_control
phase8_completion_relabel_control
ant_ecology_relabel_control
```

Required I3 result:

```text
acceptance_state = accepted_active_nulls_fail_closed_no_positive_proxy_evidence
positive_proxy_evidence_opened = false
failed_open_controls = 0
candidate_pd_ladder_rung = not_assigned_active_null_control_only
```

### Iteration 3 Result

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_proxy_evidence
source_schema_output_digest = bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070
candidate_pd_ladder_rung = not_assigned_active_null_control_only
n26_closeout_ceiling = N26-C3_active_nulls_fail_closed
n26_closeout_ladder_rung_assigned = false
positive_proxy_evidence_opened = false
proxy_derivation_opened = false
proxy_divergence_opened = false
proxy_collapse_opened = false
ap5_bridge_status = not_supported_active_null_only
required_control_count = 37
active_null_row_count = 37
failed_open_controls = 0
failed_checks = []
output_digest = 90b3adf46add9fd0b98b3022733ce9f9fabbbd1b3695908aefbfb58f7199c2fd
```

Interpretation: I3 proves that the N26 false-positive paths fail closed before
positive proxy probes run. The rows are active-null fixtures only:
`derived_report_only = true`, `trace_admissibility =
active_null_fixture_only_not_positive_evidence`, and
`positive_support_admissible = false`. They can block proxy overclaims but
cannot support PD2, proxy derivation, proxy divergence, proxy collapse, AP5
bridge status, semantic goal, agency, native support, sentience, Phase 8, ant
ecology, or unscoped multi-basin substrate claims.

Artifacts:

```text
outputs/n26_active_nulls_and_failure_baselines.json
reports/n26_active_nulls_and_failure_baselines.md
scripts/build_n26_active_nulls_and_failure_baselines.py
```

## Iteration 4 - Source-Current Proxy Derivation Probe

- [ ] Produce or consume source-current lower-stack input trace.
- [ ] Record proxy metric definition digest.
- [ ] Record proxy derivation policy digest.
- [ ] Declare proxy target digest before use.
- [ ] Record proxy metric trace.
- [ ] Record basin persistence capacity trace.
- [ ] Record support/coherence floor trace.
- [ ] Keep PD ceiling at PD2/PD3 pending divergence/collapse controls.

## Iteration 5 - Proxy Divergence Contrast Matrix

- [ ] Compare proxy metric delta with basin persistence/deepening delta.
- [ ] Require peer or control basin where applicable.
- [ ] Require proxy improvement and basin persistence stall/degradation for PD4.
- [ ] Reject proxy-only success.
- [ ] Preserve AP5 gap discipline.

## Iteration 6 - Proxy Collapse Perturbation Matrix

- [ ] Define shared perturbation challenge before use.
- [ ] Run proxy-optimized path.
- [ ] Run basin-deepened contrast path.
- [ ] Confirm proxy-optimized success fails under perturbation.
- [ ] Confirm basin-deepened contrast survives under the same envelope.
- [ ] Keep semantic goal/choice/agency claims blocked.

## Iteration 7 - Replay, Controls, And AP5 Classification Gate

- [ ] Replay all positive rows.
- [ ] Run negative control matrix.
- [ ] Confirm target derivation is not post-hoc.
- [ ] Confirm hidden proxy policy is absent or fails closed.
- [ ] Classify scoped AP5 bridge status.
- [ ] Keep final N26 closeout pending I8.

## Iteration 8 - Closeout And N27 Handoff

- [ ] Freeze final PD rung.
- [ ] Freeze final N26-C rung.
- [ ] Record AP5 bridge status.
- [ ] Record claim ceiling.
- [ ] Record all blocked claims.
- [ ] Confirm `src_diff_empty`.
- [ ] Record N27 handoff.

## Claim Boundary

N26 must not support:

```text
semantic goal
semantic choice
semantic learning
agency
native support
selfhood
identity acceptance
sentience
organism/life
ant ecology implementation
Phase 8 completion
unscoped multi-basin substrate
```
