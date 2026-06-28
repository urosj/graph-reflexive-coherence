# N26 Proxy Divergence / Proxy Collapse Implementation Plan

## Purpose

N26 tests whether source-current proxy improvement can separate from basin
deepening on scoped multi-basin LGRC substrate.

The experiment consumes N25.2 only as scoped MB6 substrate evidence and keeps
all semantic, agency, native-support, sentience, Phase 8, and ant-ecology
claims blocked.

## Source Rules

N26 may consume:

```text
N20 = proxy contract / same-basin rule source, not primitive evidence
N15 = historical artifact-level AP5/proxy context, not native AP5
N19 = AP5/NAT3 gap boundary, not proxy evidence
N25 = scoped BF5 context, not independent new-basin or native multi-basin evidence
N25.1 = requirements / ladder context, not runtime evidence
N25.2 = scoped MB6 substrate evidence, not native support or agency
roadmap/handoff = context only
```

N26 must not consume sources as:

```text
semantic goal or target ownership
agency
native support
sentience
ant ecology implementation
unscoped multi-basin substrate
Phase 8 completion
```

The I1 source-role split is immutable for later rows unless a later artifact
explicitly records a blocker/repair. Inventory/context records cannot be
promoted into proxy evidence by relabeling.

Future candidate rows must preserve scoped N25.2 consumption with:

```text
scoped_mb6_substrate_consumption_record
multi_basin_scope_id
basin_ids_or_child_basin_ids
n25_2_unscoped_consumption_allowed = false
n25_2_unscoped_multi_basin_consumption_allowed = false
front_capacity_companion_backfill_used = false
```

AP5 remains a gap ledger until N26 produces row-local evidence:

```text
ap5_dependency_status = required_recorded | missing_blocks_row | not_applicable
ap5_condition_reason
AP5_gap_prose_only_control = passed_or_failed_closed
```

For positive proxy rows (`PD2...PD6`), `ap5_dependency_status` must not be
`not_applicable`; the row must explain proxy/target participation in
`ap5_condition_reason`. `not_applicable` is allowed only for inventory rows,
schema rows, or active-null rows where no proxy/target formation is claimed.
N15/N19 context must not be counted as native AP5 evidence.

## Proxy Definitions

Proxy divergence is narrower than proxy improvement:

```text
proxy metric improves
AND basin persistence/deepening stalls or degrades
AND both are measured independently
AND thresholds/target are declared before outcome inspection
```

Proxy collapse requires a shared perturbation contrast:

```text
proxy-optimized path fails under declared perturbation
basin-deepened path survives the same perturbation envelope
perturbation envelope digest is identical across both rows
```

If the survivor contrast is missing, the envelope differs, or the basin trace is
not independent of the proxy score, PD4/PD5 must be blocked.

## Ladder

```text
PD0 = no source-current proxy evidence
PD1 = proxy metric present, but not source-current or not lower-stack linked
PD2 = source-current proxy derivation candidate with target digest declared before use
PD3 = replay-backed proxy / basin contrast candidate
PD4 = controlled proxy divergence candidate
PD5 = controlled proxy collapse candidate
PD6 = N27-ready bounded proxy divergence / collapse evidence with scoped AP5 bridge candidate
```

Closeout ladder:

```text
N26-C0 = initialized contract only
N26-C1 = source inventory and scoped-substrate admission passed
N26-C2 = proxy divergence / collapse schema frozen
N26-C3 = active nulls fail closed
N26-C4 = source-current proxy derivation and replay-backed contrast supported
N26-C5 = controlled proxy divergence / collapse candidate supported
N26-C6 = N27-ready bounded proxy divergence / collapse closeout
```

## Required Candidate Row Fields

Every positive candidate row must record:

```text
row_id
row_decision
candidate_pd_ladder_rung
source_current_inputs
source_contract_row_digest
source_consumable_contract_row_digest
source_output_digest
artifact_manifest
all_artifact_sha256_match_file_contents
row_specific_thresholds_declared_before_use
scoped_mb6_substrate_consumption_record
multi_basin_scope_id
basin_ids_or_child_basin_ids
n25_2_unscoped_consumption_allowed
n25_2_unscoped_multi_basin_consumption_allowed
front_capacity_companion_backfill_used
proxy_metric_definition_digest
proxy_derivation_policy_digest
proxy_target_digest_declared_before_use
proxy_policy_owner
producer_mediated_target_derivation_counted_as_substrate
lower_stack_input_trace
proxy_metric_trace
basin_persistence_capacity_trace
support_coherence_floor_trace
basin_deepening_comparison_trace
proxy_vs_basin_delta_trace
proxy_optimized_path_trace
basin_deepened_path_trace
perturbation_challenge_trace
proxy_collapse_result_trace
peer_or_control_basin_trace
replay_result
control_results
ap5_dependency_status
ap5_condition_reason
claim_ceiling
unsafe_claim_flags
```

The frozen I1 source digests to consume in I2+ are:

```text
source_contract_row_digest = 5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61
source_consumable_contract_row_digest = 99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec
source_output_digest = b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a
```

Positive rows must use an artifact manifest with explicit roles. Role
requirements are rung-specific so early derivation rows are not blocked by
collapse/closeout artifacts that only belong to later rows:

```text
PD2 = runtime_trace, lower_stack_input_trace, proxy_metric_trace,
      basin_persistence_capacity_trace, support_coherence_floor_trace, report

PD3 = PD2 roles + basin_deepening_comparison_trace,
      proxy_vs_basin_delta_trace, replay_trace

PD4 = PD3 roles + peer_or_control_basin_trace, control_trace

PD5 = PD4 roles + proxy_optimized_path_trace, basin_deepened_path_trace,
      perturbation_challenge_trace, proxy_collapse_result_trace

PD6 = all relevant positive-row roles + closeout
```

Positive support is blocked if an artifact is missing, a SHA-256 digest does not
match, an artifact role is missing, `derived_report_only = true`, or any local
absolute path appears.

The proxy policy owner enum is:

```text
source_current_runtime
declared_analysis_policy
producer_mediated_blocks_substrate_claim
hidden_policy_blocks_row
```

`producer_mediated_target_derivation_counted_as_substrate` must remain `false`.

## Controls

Required false-positive controls:

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

Every positive row `control_results` item must include
`control_satisfied_for_positive_row`, so the record distinguishes a declared
control from a control that actually cleared the candidate row.

For PD3+:

```text
artifact_replay = passed
snapshot_load_replay = passed
duplicate_replay = passed
order_control = passed
```

For PD4/PD5:

```text
negative_controls_fail_closed = true
failed_open_controls = 0
not_run_required_controls = 0
```

## Iterations

### Iteration 1. Source Inventory And Scoped Substrate Admission

Inventory N20, N15, N25, N25.1, N25.2, roadmap, and handoff sources. Confirm
N25.2 may be consumed only as scoped MB6 substrate evidence. Assign no PD rung.

### Iteration 2. Proxy Divergence / Collapse Schema Freeze

Freeze candidate row schema, PD ladder, N26-C ladder, AP5 status enum, scoped
substrate consumption rules, replay requirements, and fail-closed controls.
Open no positive proxy evidence.

Required acceptance state:

```text
accepted_proxy_divergence_collapse_schema_frozen_no_proxy_evidence
```

Required ceiling:

```text
candidate_pd_ladder_rung = not_assigned_schema_only
n26_closeout_ceiling = N26-C2_proxy_divergence_collapse_schema_frozen
positive_proxy_evidence_opened = false
proxy_derivation_opened = false
proxy_divergence_opened = false
proxy_collapse_opened = false
ap5_bridge_status = not_supported_schema_only
```

### Iteration 3. Active Nulls And Failure Baselines

Instantiate controls before positive probes. Required nulls include source
digest mismatch, missing lower-stack/proxy/basin/floor traces, label-only
proxy, post-hoc target, hidden proxy policy, proxy-only improvement, proxy
improvement without divergence, basin degradation hidden by proxy score,
unscoped MB6 relabel, front-capacity backfill, peer-basin missing,
perturbation mismatch or missing digest, missing basin-deepened survivor,
missing collapse result trace, AP5 prose-only handling, N15/N19 native-AP5
relabels, and unsafe semantic/agency/native-support relabels.

Required acceptance state:

```text
accepted_active_nulls_fail_closed_no_positive_proxy_evidence
```

### Iteration 4. Source-Current Proxy Derivation Probe

Build the first source-current proxy derivation candidate on scoped MB6
substrate. This can reach PD2/PD3 only if lower-stack inputs, target digest,
proxy trace, basin persistence trace, and replay are present.

### Iteration 5. Proxy Divergence Contrast Matrix

Compare proxy metric improvement against basin persistence/deepening. A PD4
candidate requires proxy improvement while basin persistence capacity stalls or
degrades under declared controls.

### Iteration 6. Proxy Collapse Perturbation Matrix

Test whether proxy-optimized success fails under a perturbation that a
basin-deepened contrast survives. A PD5 candidate requires a shared challenge
envelope and a survivor contrast.

### Iteration 7. Replay, Controls, And AP5 Classification Gate

Replay and control all positive rows. Classify scoped AP5 bridge candidate
status only if target derivation, proxy metrics, lower-stack inputs, controls,
and claim boundaries are clean.

### Iteration 8. Closeout And N27 Handoff

Freeze final PD/N26-C rung, claim ceiling, AP5 bridge status, source roles,
blocked claims, `src_diff_empty`, and N27 configuration/substrate transfer
handoff.
