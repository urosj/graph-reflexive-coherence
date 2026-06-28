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

- [x] Produce or consume source-current lower-stack input trace.
- [x] Record proxy metric definition digest.
- [x] Record proxy derivation policy digest.
- [x] Declare proxy target digest before use.
- [x] Record proxy metric trace.
- [x] Record basin persistence capacity trace.
- [x] Record support/coherence floor trace.
- [x] Keep PD ceiling at PD2 pending divergence/collapse controls.

### Iteration 4 Result

```text
status = passed
acceptance_state = accepted_source_current_pd2_proxy_derivation_candidate_pending_contrast_controls
source_schema_output_digest = bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070
source_active_null_output_digest = 90b3adf46add9fd0b98b3022733ce9f9fabbbd1b3695908aefbfb58f7199c2fd
source_n25_2_closeout_output_digest = b92401da545899c7721ab42692827beb5b357bbd246d8991d7ad56649a6bbf03
candidate_pd_ladder_rung = PD2
n26_closeout_ceiling = N26-C3_active_nulls_fail_closed_with_PD2_derivation_candidate
n26_closeout_ladder_rung_assigned = false
positive_proxy_evidence_opened = true
proxy_derivation_opened = true
proxy_divergence_opened = false
proxy_collapse_opened = false
pd3_or_stronger_supported = false
ap5_bridge_status = not_supported_i4_row_local_dependency_recorded
candidate_row_count = 2
failed_checks = []
output_digest = b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680
```

Candidate rows:

```text
n26_i4_i4_reference_child_basin_core_0:
  source = N25.2 I4 reference child-basin core 0
  proxy_basin_coupling_gap = 0.0
  basin_persistence_capacity_score = 1.0
  rung = PD2

n26_i4_i4a_route_variant_child_basin_core_2:
  source = N25.2 I4-A route-variant child-basin core 2
  proxy_basin_coupling_gap = 0.0
  basin_persistence_capacity_score = 1.0
  rung = PD2
```

Interpretation: I4 derives a local proxy metric from scoped, source-current
N25.2 MB6 child-basin replay traces. The proxy is the coupling gap between
perfect scoped child-basin persistence and the weakest observed support,
coherence, boundary, flux, or membership replay ratio. Both source rows have
all ratios at `1.0`, so the derived gap is `0.0`.

This supports only a source-current PD2 proxy derivation candidate. It does not
yet support replay-backed proxy/basin contrast, controlled proxy divergence,
proxy collapse, an AP5 bridge closeout, semantic goal or choice, agency, native
support, sentience, Phase 8 completion, ant ecology, or unscoped multi-basin
substrate. The AP5 dependency is recorded row-locally because proxy target
derivation participates, but N15/N19 remain gap context and are not consumed as
native AP5 evidence.

Artifacts:

```text
outputs/n26_source_current_proxy_derivation_probe.json
outputs/n26_source_current_proxy_derivation_probe_artifacts/
reports/n26_source_current_proxy_derivation_probe.md
scripts/build_n26_source_current_proxy_derivation_probe.py
```

## Iteration 4-A - Proxy Derivation Sensitivity Probe

- [x] Consume existing N25.2 stress matrix rows without new runtime behavior.
- [x] Keep the I4 proxy derivation record unchanged.
- [x] Apply the same coupling-gap proxy family to stress-normalized source-current rows.
- [x] Confirm source-passing stress rows keep proxy gap at `0.0`.
- [x] Confirm tightened-threshold and injected-leakage rows produce nonzero gaps.
- [x] Reject all nonzero-gap failed-closed rows as positive proxy support.
- [x] Keep PD ceiling at PD2 and leave PD3+ pending I5/I6.

### Iteration 4-A Result

```text
status = passed
acceptance_state = accepted_pd2_proxy_derivation_sensitivity_probe_no_pd3_no_divergence
source_i4_output_digest = b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680
source_n25_2_stress_output_digest = 1759dbb4d8c85c27bc056108f04fea3cfcc1c59b5ee9518ebb7f641e60949627
candidate_pd_ladder_rung = PD2
n26_closeout_ceiling = N26-C3_active_nulls_fail_closed_with_PD2_sensitivity_checked_derivation_candidate
n26_closeout_ladder_rung_assigned = false
positive_proxy_evidence_opened = true
proxy_derivation_opened = true
proxy_derivation_sensitivity_opened = true
proxy_divergence_opened = false
proxy_collapse_opened = false
pd3_or_stronger_supported = false
ap5_bridge_status = not_supported_i4a_sensitivity_only
i4_replaced = false
sensitivity_row_count = 16
bounded_degraded_positive_row_supported = false
failed_checks = []
output_digest = 5dbe325f6ce1ff95434b978e69cf659fdf609e2890960198aca66e2c5c85e414
```

Interpretation: I4-A checks that the I4 proxy is not just a success label. It
reuses the same coupling-gap proxy family over source-current N25.2 stress rows:

```text
stress_normalized_proxy_basin_coupling_gap =
  max(0.0, 1.0 - weakest_stress_normalized_capacity_ratio)
```

Passing source/relaxed threshold, source merge/leakage ceiling, and persistence
window rows keep the gap at `0.0`. Tightened-threshold rows produce nonzero
gaps (`0.083333...` for the reference row and `0.03125` for the route variant),
and injected merge/leakage rows produce gap `1.0`. Those nonzero rows fail
closed and are not counted as positive proxy support.

This strengthens PD2 by showing source-current sensitivity: the derived proxy
responds to lower-stack stress conditions. It does not provide a passing
bounded-degradation positive row in the consumed N25.2 sources, and it does not
support replay-backed proxy/basin contrast, proxy divergence, proxy collapse,
AP5 bridge closeout, semantic goal or choice, agency, native support, sentience,
Phase 8 completion, ant ecology, or unscoped multi-basin substrate.

Artifacts:

```text
outputs/n26_proxy_derivation_sensitivity_probe.json
outputs/n26_proxy_derivation_sensitivity_probe_artifacts/
reports/n26_proxy_derivation_sensitivity_probe.md
scripts/build_n26_proxy_derivation_sensitivity_probe.py
```

## Iteration 5 - Proxy Divergence Contrast Matrix

- [x] Compare proxy metric delta with basin persistence/deepening delta.
- [x] Require peer or control basin where applicable.
- [x] Require proxy improvement and basin persistence stall/degradation for PD4.
- [x] Reject proxy-only success.
- [x] Preserve AP5 gap discipline.

### Iteration 5 Result

```text
status = passed
acceptance_state = accepted_replay_backed_pd3_proxy_basin_contrast_no_controlled_divergence
source_i4_output_digest = b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680
source_i4a_output_digest = 5dbe325f6ce1ff95434b978e69cf659fdf609e2890960198aca66e2c5c85e414
candidate_pd_ladder_rung = PD3
n26_closeout_ceiling = N26-C4_source_current_proxy_derivation_and_replay_backed_contrast_supported
n26_closeout_ladder_rung_assigned = false
positive_proxy_evidence_opened = true
proxy_derivation_opened = true
proxy_derivation_sensitivity_opened = true
proxy_divergence_contrast_opened = true
proxy_divergence_opened = true
proxy_divergence_supported = false
controlled_proxy_divergence_candidate_supported = false
pd4_or_stronger_supported = false
proxy_collapse_opened = false
proxy_collapse_supported = false
ap5_bridge_status = not_supported_i5_contrast_only
contrast_row_count = 8
failed_checks = []
output_digest = 52e7cba79816e840947472d35ee8906f357db1bcf896b59f59bbac243d9ee4a5
```

Interpretation: I5 pairs the two scoped N25.2 child-basin candidates across
the I4-A stress axes and supports a replay-backed proxy/basin contrast matrix
at PD3. The matrix does not support controlled proxy divergence. Passing stress
rows keep both proxy gaps at `0.0`; tightened-threshold and injected-leakage
rows produce nonzero gaps only where the source stress row already fails
closed. No row shows proxy improvement while basin persistence/deepening stalls
or degrades under independent measurement.

PD4 remains blocked by:

```text
no_proxy_improvement_observed
proxy_and_basin_measurement_not_independent_enough_for_PD4
nonzero_proxy_gap_rows_are_fail_closed_blockers_not_positive_support
basin_deepening_not_observed
```

This supports contrast, not divergence or collapse. It does not support AP5
bridge closeout, semantic goal or choice, agency, native support, sentience,
Phase 8 completion, ant ecology, or unscoped multi-basin substrate.

Artifacts:

```text
outputs/n26_proxy_divergence_contrast_matrix.json
outputs/n26_proxy_divergence_contrast_matrix_artifacts/
reports/n26_proxy_divergence_contrast_matrix.md
scripts/build_n26_proxy_divergence_contrast_matrix.py
```

## Iteration 5-A - Alternative Proxy Surface Divergence Probe

- [x] Declare alternative proxy surfaces before use.
- [x] Compare alternative proxy delta with basin-state delta.
- [x] Test threshold-margin proxy surface.
- [x] Test replay-window-surplus proxy surface.
- [x] Confirm divergence-shaped signals are observed.
- [x] Reject threshold-policy-mediated proxy improvement as PD4 evidence.
- [x] Reject evaluation-window-mediated proxy improvement as PD4 evidence.
- [x] Preserve the I5 PD3 contrast result without upgrade.

### Iteration 5-A Result

```text
status = passed
acceptance_state = accepted_alternative_proxy_surface_divergence_shape_detected_pd4_blocked
source_i5_output_digest = 52e7cba79816e840947472d35ee8906f357db1bcf896b59f59bbac243d9ee4a5
candidate_pd_ladder_rung = PD3
n26_closeout_ceiling = N26-C4_source_current_proxy_derivation_and_replay_backed_contrast_supported
n26_closeout_ladder_rung_assigned = false
alternative_proxy_surface_probe_opened = true
divergence_shaped_signal_observed = true
controlled_proxy_divergence_candidate_supported = false
pd4_or_stronger_supported = false
proxy_collapse_opened = false
proxy_collapse_supported = false
ap5_bridge_status = not_supported_i5a_alternative_surface_blocked
row_count = 4
failed_checks = []
output_digest = 108849bf8b5249b97611461a4423d4986030c6d84d83b6580ba03cfc561e8eda
```

Interpretation: I5-A tries two alternative proxy surfaces over the same scoped
N25.2 substrate:

```text
threshold_margin = min(observed support, observed coherence) - declared threshold
window_surplus = observed replay window count - required replay window count
```

Both surfaces can produce divergence-shaped signals:

```text
threshold_margin proxy_delta = 0.1 with basin_delta = 0.0
window_surplus proxy_delta = 1.0 with basin_delta = 0.0
```

These signals fail closed for PD4. The threshold-margin improvement is mediated
by relaxed threshold policy, and the window-surplus improvement is mediated by a
changed evaluation-window requirement. They are useful false-positive evidence:
N26 can induce proxy-looking separation, but controlled proxy divergence still
requires a source-backed basin/proxy separation that is not created by changing
the proxy or evaluation surface.

This does not overwrite I5. It preserves:

```text
PD3 replay-backed contrast supported
PD4 controlled proxy divergence blocked
proxy collapse not opened
AP5 bridge closeout not supported
```

Artifacts:

```text
outputs/n26_alternative_proxy_surface_divergence_probe.json
outputs/n26_alternative_proxy_surface_divergence_probe_artifacts/
reports/n26_alternative_proxy_surface_divergence_probe.md
scripts/build_n26_alternative_proxy_surface_divergence_probe.py
```

## Iteration 5-B - Fixed-Surface Divergence Search

- [x] Hold the proxy surface fixed as native route arbitration score.
- [x] Hold basin comparison requirements fixed before searching.
- [x] Check selected-vs-rejected route pairs for paired basin-state traces.
- [x] Check cross-route selected pairs for same child scope and threshold surface.
- [x] Reject missing rejected-route basin traces as PD4 evidence.
- [x] Reject cross-route scope/threshold mismatches as PD4 evidence.
- [x] Preserve the I5/I5-A PD3 ceiling without upgrade.

### Iteration 5-B Result

```text
status = passed
acceptance_state = accepted_fixed_surface_divergence_search_no_admissible_pd4_pair
source_i5_output_digest = 52e7cba79816e840947472d35ee8906f357db1bcf896b59f59bbac243d9ee4a5
source_i5a_output_digest = 108849bf8b5249b97611461a4423d4986030c6d84d83b6580ba03cfc561e8eda
candidate_pd_ladder_rung = PD3
n26_closeout_ceiling = N26-C4_source_current_proxy_derivation_and_replay_backed_contrast_supported
n26_closeout_ladder_rung_assigned = false
fixed_surface_divergence_search_opened = true
eligible_fixed_surface_pair_count = 0
controlled_proxy_divergence_candidate_supported = false
pd4_or_stronger_supported = false
proxy_collapse_opened = false
proxy_collapse_supported = false
ap5_bridge_status = not_supported_i5b_no_admissible_fixed_surface_pd4_pair
row_count = 4
failed_checks = []
output_digest = cab31a49994ae2ddf1c031e0e3f30c6c17c9dd169bbb3a9d2ccdc80b1da59c73
```

Interpretation: I5-B asks the stricter PD4 question that I5-A could not
answer: can existing native N25.2 route/runtime sources show proxy improvement
while the basin metric stalls or degrades without changing the proxy surface,
basin metric, threshold policy, or control envelope?

The answer is no for the current sources. The selected-vs-rejected native route
pairs show route-score proxy contrast:

```text
selected route score = 0.75
rejected route score = 0.25
proxy_delta = 0.5
```

but the rejected routes do not emit child-basin state traces. That means there
is no paired source-current basin persistence surface for the rejected route,
so the row cannot support controlled proxy/basin divergence.

The cross-route selected pairs both emit child-basin state, but they do not
share the same basin surface:

```text
core 0 source threshold = 1.1
core 2 source threshold = 3.1
route-score proxy delta = 0.0
basin support/coherence delta = 2.0
```

This is a scoped substrate difference, not same-surface proxy divergence. The
child scope and threshold surfaces differ, and no route-score proxy improvement
appears between the two selected routes.

I5-B therefore strengthens the negative result. I5-A showed that
proxy-looking divergence can be induced by changing proxy/evaluation surfaces.
I5-B holds the surface fixed and shows that the current native sources still do
not contain an admissible PD4 pair.

The correct ceiling remains:

```text
PD3 replay-backed proxy/basin contrast supported
PD4 controlled proxy divergence blocked
proxy collapse not opened
AP5 bridge closeout not supported
```

Artifacts:

```text
outputs/n26_fixed_surface_divergence_search.json
outputs/n26_fixed_surface_divergence_search_artifacts/
reports/n26_fixed_surface_divergence_search.md
scripts/build_n26_fixed_surface_divergence_search.py
```

## Iteration 5-C - Same-Route Score-Dose Divergence Probe

- [x] Run paired same-route source-current LGRC9V3 score-dose rows.
- [x] Keep selected sink, fixture, packet schedule, basin metric, and threshold/control envelope fixed.
- [x] Vary route-score proxy dose under the same proxy surface.
- [x] Confirm proxy score improves while basin geometry stalls.
- [x] Confirm child-basin membership, support, coherence, boundary, and flux remain fixed.
- [x] Replay both score-dose rows.
- [x] Mark the PD4 result provisional pending I7 replay/control classification.
- [x] Preserve producer-mediated route-score boundary and keep native AP5 blocked.

### Iteration 5-C Result

```text
status = passed
acceptance_state = accepted_provisional_pd4_same_route_score_dose_divergence_candidate_pending_i7
source_i5b_output_digest = cab31a49994ae2ddf1c031e0e3f30c6c17c9dd169bbb3a9d2ccdc80b1da59c73
candidate_pd_ladder_rung = PD4_candidate_pending_I7
n26_closeout_ceiling = N26-C5_provisional_controlled_proxy_divergence_candidate_pending_controls
n26_closeout_ladder_rung_assigned = false
same_route_score_dose_probe_opened = true
provisional_pd4_candidate_supported = true
controlled_proxy_divergence_candidate_supported = true
controlled_proxy_divergence_status = provisional_pending_I7_replay_controls_and_AP5_gate
pd4_or_stronger_supported = false
final_pd4_supported = false
pd4_support_scope = producer_mediated_route_score_surface_only
proxy_collapse_opened = false
proxy_collapse_supported = false
native_ap5_bridge_supported = false
ap5_bridge_status = not_supported_i5c_producer_mediated_score_surface
row_count = 2
failed_checks = []
output_digest = 5f4c9355645ba39840f860d4544b71195fbfde277ab9ce7b6fd22291c34099ab
```

Interpretation: I5-C addresses the I5-B blocker by producing paired basin
traces directly. It runs two mirrored same-route score-dose families:

```text
sink0 fixed route:
  low score = 0.55
  high score = 0.95
  proxy_delta = 0.4
  basin_delta = 0.0

sink2 fixed route:
  low score = 0.55
  high score = 0.95
  proxy_delta = 0.4
  basin_delta = 0.0
```

Geometrically, the selected route family, packet schedule, child-basin
membership, support floor, coherence floor, boundary value, and flux value stay
fixed. The route-score proxy improves; the basin does not deepen. This is the
first positive controlled proxy-divergence shape in N26.

The claim is deliberately bounded:

```text
supports: provisional producer-mediated PD4 proxy-divergence candidate
pending: I7 replay/control/AP5 classification
blocked: proxy collapse, native AP5, native support, agency, semantic goal,
         sentience, Phase 8 completion, ant ecology
```

The route-score proxy is runtime-visible and source-current, but it is still a
producer-mediated route-candidate score. I5-C therefore does not convert the
score into native AP5 target formation or native support evidence.

Artifacts:

```text
outputs/n26_same_route_score_dose_divergence_probe.json
outputs/n26_same_route_score_dose_divergence_probe_artifacts/
reports/n26_same_route_score_dose_divergence_probe.md
scripts/build_n26_same_route_score_dose_divergence_probe.py
```

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
