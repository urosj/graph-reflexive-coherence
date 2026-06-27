# N24 Abundance Surplus-Supported Optionality Implementation Plan

## Goal

N24 tests whether surplus support/coherence above maintenance floors can open
source-current optional continuation space while preserving basin integrity.

The experiment should support only:

```text
bounded artifact-level surplus-supported optionality / abundance candidate
```

It must not support:

```text
reward maximization
semantic choice
semantic goal
semantic intention
agency
free will
selfhood
identity acceptance
native support
sentience
Phase 8 implementation
ant ecology implementation
native ant agency
native colony agency
unrestricted autonomy
```

## Source Rules

N24 must consume the N20 contract rows:

```text
source_contract_row = n20_i4_row_05_surplus_supported_optionality
source_consumable_contract_row = n20_i5_row_05_surplus_supported_optionality
```

N24 must consume N23 closeout only as bounded context:

```text
N23 final_supported_lc_ladder_rung = LC6
N23 final_n23_closeout_ladder_rung = N23-C6
N23 ap4_bridge_status = bridge_candidate_supported
N23 ready_for_n24 = true
```

N23 consumption is conditional, not assumed:

```text
n23_closeout_required = true
n23_closeout_artifact_required =
  experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_closeout_and_n24_handoff.json

if n23_closeout_missing:
  n24_source_inventory_status = blocked_by_missing_n23_closeout
  n23_context_consumption = not_available
  max_ab_rung = AB0

if n23_final_lc_ladder_rung < LC6 or n23_closeout_ladder_rung < N23-C6:
  n23_context_consumption = bounded_lower_rung_context_only
  n23_ap4_bridge_status = not_consumable_as_bridge_candidate
  n24_claim_ceiling = contract_only_or_downgraded_context
```

N23 cannot supply N24 abundance evidence. N24 must produce new source-backed
surplus, maintenance-floor, optional-continuation, and hidden-budget-control
evidence.

N19/N20/N23 AP gap context must be preserved:

```text
N23 AP4 bridge candidate context may be consumed.
Final global AP4 reclassification is not made here.
Conditional AP5 dependency is required when proxy/reward/target formation
participates.
```

Inherited fields must be prefixed:

```text
n20_source_downstream_consumption_status
n23_source_closeout_status
n23_ap4_bridge_status
```

## Required Evidence Fields

Every candidate evidence row must record:

```text
row_id
source_contract_row
source_consumable_contract_row
source_contract_row_digest
source_consumable_contract_row_digest
source_output_digest
run_artifact_id
source_commit_or_source_digest
runtime_config_digest
source_current_inputs
source_current_required_fields
row_specific_thresholds_declared_before_use
n20_source_downstream_consumption_status
n23_source_closeout_status
n23_closeout_required
n23_context_consumption
n23_ap4_bridge_status
ap4_context_status
maintenance_floor_policy
maintenance_basin_id
maintenance_basin_signature_digest
support_measurement_scope
support_aggregation_method
surplus_channel_policy
support_floor_value
coherence_floor_value
boundary_integrity_floor_value
flux_or_leakage_bound
optionality_window
pre_surplus_geometry_trace
support_surplus_margin_trace
coherence_surplus_margin_trace
residual_support_margin_under_optionality
residual_coherence_margin_under_optionality
optional_flux_drain_margin
maintenance_floor_trace
optional_continuation_set_trace
optional_continuation_count
optional_continuation_availability_count
jointly_admissible_optional_continuation_count
optional_branch_records
optional_branch_evidence_mode
optional_branch_support_coherence_traces
optional_branch_boundary_flux_traces
boundary_integrity_under_optionality_trace
optional_flux_does_not_drain_maintenance_support
surplus_budget_owner
hidden_budget_relief_absent
reward_or_proxy_label_absent_or_blocked
same_basin_continuation_rule
same_basin_invariant_fields
out_of_scope_drift_blocks_row
optionality_not_label_reassignment
support_floor_result
coherence_floor_result
boundary_integrity_result
flux_or_leakage_result
replay_result
control_results
ap4_dependency_status
ap5_dependency_status
ap4_condition_reason
ap5_condition_reason
surplus_trace_digest
optional_continuation_trace_digest
maintenance_floor_trace_digest
replay_surplus_digest
replay_optionality_digest
surplus_persistence_ratio
optional_branch_persistence_ratio
surplus_threshold_or_rule
optionality_threshold_or_rule
hidden_budget_relief_rejected
floor_crossing_rejected
surplus_without_optional_continuation_rejected_or_demoted
optionality_without_surplus_rejected
proxy_only_success_rejected
optional_branch_label_only_rejected
independent_run_optional_assembly_rejected
maintenance_basin_shift_rejected
floor_renormalization_rejected
post_hoc_surplus_rejected
n23_context_relabel_rejected
producer_residue_fields
naturalization_debt_fields
blocked_relabel_fields
claim_ceiling
unsafe_claim_flags
row_decision
surplus_supported_optionality_claim_allowed
semantic_choice_claim_allowed
reward_maximization_claim_allowed
agency_claim_allowed
native_support_claim_allowed
final_global_ap4_reclassification_supported
derived_report_only
artifact_manifest
artifact_paths
artifact_sha256
all_artifact_sha256_match_file_contents
output_digest
```

## Local Ladder

```text
AB0 = no source-current surplus optionality evidence
AB1 = run artifact with possible surplus or optionality context
AB2 = source-current surplus above declared maintenance floor
AB3 = surplus opens source-current optional continuation set while floors hold
AB4 = replay/control-backed surplus-supported optionality candidate
AB5 = stress/threshold-backed abundance candidate with hidden-budget, proxy,
      and floor-crossing controls clean
AB6 = N25-ready bounded surplus-supported optionality evidence
```

Rows below `AB3` cannot support optionality. Rows below `AB4` cannot support
replay/control-backed abundance evidence. `AB6` is an N25 handoff rung, not
agency, semantic choice, or native support.

## Closeout Ladder

N24 must also use a tranche-level closeout ladder:

```text
N24-C0 = contract-only closeout
  N20/N23 handoff consumed, but no N24 abundance evidence opened.

N24-C1 = active-null/control discipline established
  Active nulls and failure baselines fail closed, but no positive AB row.

N24-C2 = surplus partial
  Surplus appears, but optionality, replay, controls, or AP gaps block stronger
  support.

N24-C3 = source-current optional continuation candidate
  AB3 reached on at least one source-backed row.

N24-C4 = replay/control-backed surplus optionality candidate
  AB4 reached after replay and fail-closed controls.

N24-C5 = stress/threshold-backed abundance candidate
  AB5 reached with hidden-budget, proxy-only, floor-crossing, and optional-label
  controls clean.

N24-C6 = N25-ready bounded surplus-supported optionality evidence
  AB5/AB6 evidence plus producer residue, naturalization debt, AP4/AP5
  discipline, unsafe-claim blockers, src_diff_empty, and N25 handoff.
```

The closeout ladder classifies the whole N24 tranche. It must not convert an
AB row into semantic choice, agency, native support, sentience, Phase 8, or ant
ecology.

## Schema Policies To Freeze

Iteration 2 must freeze how optional continuation space may be counted:

```text
support_surplus_margin_trace = source-current surplus above maintenance floor
maintenance_floor_trace = declared support/coherence floor record
optional_continuation_set_trace = source-current optional branch records
boundary_integrity_under_optionality_trace = boundary remains above floor while
optional branches are open
optional_continuation_availability_count = source-current alternatives
available in the same optionality window
jointly_admissible_optional_continuation_count = alternatives jointly
admissible under the same maintenance surplus and budget envelope
optionality_not_label_reassignment = true
out_of_scope_drift_blocks_row = true
```

Operational optionality acceptance must be:

```text
original_optional_continuation_set_trace.same_source_current_run = true
declared_replay_family_may_validate_but_not_create_original_set = true
same_declared_optionality_window = true
maintenance_floor_declared_before_window = true
surplus_margin_trace.step_range intersects optionality_window
optional_continuation_set_trace.step_range subset optionality_window
branch_specific_support_coherence_traces_present = true
branch_specific_boundary_flux_traces_present = true
optional_flux_does_not_drain_maintenance_support = true
AB3 requires optional_continuation_availability_count >= 2
AB5 requires jointly_admissible_optional_continuation_count >= 2 under stress
```

Optional branches assembled across independent runs, labels, reward/proxy
scores, report-side construction, or hidden producer budget relief do not
count as original optional-continuation evidence.

Iteration 2 must also freeze surplus formulas before probes:

```text
support_surplus_margin =
  observed_support - support_floor_value

coherence_surplus_margin =
  observed_coherence - coherence_floor_value

residual_support_margin_under_optionality =
  min_support_during_optionality_window - support_floor_value

residual_coherence_margin_under_optionality =
  min_coherence_during_optionality_window - coherence_floor_value

optional_flux_drain_margin =
  flux_or_leakage_bound - observed_optional_flux_drain
```

AB2 requires positive surplus margin. AB3 requires residual support and
coherence margins to remain positive while optional branches are open.

Each optional branch record must follow this schema:

```text
optional_branch_record = {
  branch_id,
  source_node_id,
  target_node_id,
  edge_id_or_route_id,
  trace_origin,
  trace_status,
  optionality_window_step_range,
  support_before,
  support_after_or_projected_after,
  coherence_before,
  coherence_after_or_projected_after,
  support_surplus_margin_before,
  support_surplus_margin_after,
  coherence_surplus_margin_before,
  coherence_surplus_margin_after,
  boundary_integrity_result,
  flux_or_leakage_result,
  optional_flux_cost,
  maintenance_floor_preserved,
  reward_or_proxy_label_used,
  producer_enumeration_used,
  admissibility_status
}
```

The surplus budget owner must be a closed enum:

```text
source_current_geometry
declared_producer_surface
mixed_declared
hidden_budget_relief_blocks_row
not_recorded_blocks_row
```

If the owner is `declared_producer_surface` or `mixed_declared`, the row may
remain producer-mediated candidate evidence but cannot support native support
or Phase 8.

The surplus budget owner also sets a rung ceiling:

```text
source_current_geometry:
  may support AB2..AB6 if all other gates pass

declared_producer_surface:
  may support producer-mediated AB2/AB3/AB4 candidate evidence only
  cannot support native support, Phase 8, or naturalized abundance

mixed_declared:
  must record producer residue and naturalization debt
  cannot exceed bounded producer-mediated candidate unless source-backed
  naturalization evidence is produced

hidden_budget_relief_blocks_row:
  blocks positive support
```

AP4 context must remain distinct from final AP4 reclassification:

```text
ap4_context_status =
  n23_bridge_candidate_consumed |
  lower_n23_context_consumed |
  not_applicable |
  missing_blocks_row

final_global_ap4_reclassification_supported = false

if route_or_branch_conditioned_optionality = true:
  ap4_dependency_status = required_recorded
  ap4_context_status must be recorded
```

## Control Matrix

N24 controls must include:

```text
hidden_budget_relief_control
floor_crossing_as_abundance_control
surplus_without_optional_continuation_control
optionality_without_surplus_control
proxy_only_optional_branch_gain_control
optional_branch_label_only_control
single_optional_branch_relabel_control
independent_run_optional_assembly_control
maintenance_basin_shift_control
floor_renormalization_as_surplus_control
post_hoc_surplus_construction_control
n23_selection_context_relabel_as_abundance_control
reward_maximization_relabel_control
semantic_choice_relabel_control
agency_relabel_control
native_support_relabel_control
phase8_relabel_control
ap4_final_reclassification_relabel_control
ap5_proxy_gap_omission_control
```

Controls must fail closed:

```text
failed_closed = blocker triggered and claim was correctly rejected
failed_open = blocker triggered but claim still passed
not_run = blocks dependent rung
```

## Iteration Plan

### Iteration 1. Source Handoff Inventory

Build a source inventory. Consume N20 I4/I5 surplus contract rows and N23
closeout/handoff only if the closeout artifact exists and validates LC6/N23-C6
with `ready_for_n24 = true`. Record source roles, AP gap status, producer
residue, naturalization debt, blocked relabels, required N24 source-current
fields, and expected controls. Assign no AB rung above inventory scope.

Expected artifacts:

```text
outputs/n24_source_handoff_inventory.json
reports/n24_source_handoff_inventory.md
scripts/build_n24_source_handoff_inventory.py
```

### Iteration 2. Schema, Ladder, And Control Freeze

Freeze candidate row schema, local `AB0...AB6` ladder, `N24-C0...N24-C6`
closeout ladder, maintenance-floor policy, surplus budget owner enum,
surplus formulas, optional branch record schema, optionality acceptance rule,
AP4/AP5 enums, AP4 context status, and control matrix. Open no positive N24
evidence.

Expected artifacts:

```text
outputs/n24_abundance_schema_and_controls.json
reports/n24_abundance_schema_and_controls.md
scripts/build_n24_abundance_schema_and_controls.py
```

### Iteration 3. Active Nulls And Failure Baselines

Instantiate active nulls before positive probes. Required false-positive rows:

```text
hidden_budget_relief_as_surplus
floor_crossing_as_abundance
surplus_without_optional_continuation
optionality_without_surplus
proxy_only_optional_branch_gain
optional_branch_label_only
single_branch_relabel_as_optionality
independent_run_optional_assembly
maintenance_basin_shift_as_surplus
floor_renormalization_as_surplus
post_hoc_surplus_construction
n23_selection_context_relabel_as_abundance
reward_maximization_relabel
missing_maintenance_floor
missing_boundary_integrity_trace
optional_flux_drains_maintenance_support
ap4_final_reclassification_relabel
ap5_proxy_gap_omission
semantic_choice_agency_native_support_phase8_relabels
```

All must fail closed and assign no AB rung above null/control scope.

Expected artifacts:

```text
outputs/n24_active_nulls_and_failure_baselines.json
reports/n24_active_nulls_and_failure_baselines.md
scripts/build_n24_active_nulls_and_failure_baselines.py
```

### Iteration 4. Minimal Source-Current Surplus Probe

Run the first positive surplus probe. Show source-current support/coherence
surplus above declared maintenance floors with maintenance basin preserved.
Keep result bounded as `AB2` or provisional `AB3` pending optionality, replay,
and controls.

Expected artifacts:

```text
outputs/n24_minimal_surplus_probe.json
reports/n24_minimal_surplus_probe.md
scripts/build_n24_minimal_surplus_probe.py
```

### Iteration 5. Optional Continuation Set Probe

Test whether surplus opens multiple source-current optional continuations while
support, coherence, boundary, and flux floors remain preserved. Keep reward,
semantic choice, and agency labels blocked.

Expected artifacts:

```text
outputs/n24_optional_continuation_set_probe.json
reports/n24_optional_continuation_set_probe.md
scripts/build_n24_optional_continuation_set_probe.py
```

### Iteration 6. Replay And Control Matrix

Replay positive candidate rows and run hidden-budget, floor-crossing,
proxy-only, optional-label-only, post-hoc, N23-relabel, reward, AP-gap, and
unsafe-claim controls. Demote rows whose controls fail open or whose replay
does not preserve surplus/optionality.

Expected artifacts:

```text
outputs/n24_replay_and_control_matrix.json
reports/n24_replay_and_control_matrix.md
scripts/build_n24_replay_and_control_matrix.py
```

### Iteration 7. Stress And Threshold Matrix

Map surplus margin, optional branch capacity, maintenance floor, and flux
stress boundaries. Determine whether the result is only a narrow edge case or
stress/threshold-backed `AB5` candidate evidence.

Expected artifacts:

```text
outputs/n24_stress_threshold_matrix.json
reports/n24_stress_threshold_matrix.md
scripts/build_n24_stress_threshold_matrix.py
```

### Iteration 8. Closeout And N25 Handoff

Classify final AB and N24-C rungs, record claim ceiling, preserve AP4/AP5
ledger, confirm unsafe claims remain false, confirm `src_diff_empty`, and hand
off only bounded surplus-supported optionality context to N25.

Expected artifacts:

```text
outputs/n24_closeout_and_n25_handoff.json
reports/n24_closeout_and_n25_handoff.md
scripts/build_n24_closeout_and_n25_handoff.py
```

## Closeout Requirements

N24 closeout must record:

```text
final_supported_ab_ladder_rung
final_n24_closeout_ladder_rung
n24_closeout_supported
source_backed_surplus_evidence
source_backed_optional_continuation_evidence
maintenance_floor_preserved
hidden_budget_relief_rejected
proxy_only_success_rejected
floor_crossing_rejected
n23_context_relabel_rejected
ap4_context_preserved
final_global_ap4_reclassification_supported = false
ap5_dependency_status
reward_maximization_supported = false
semantic_choice_supported = false
agency_supported = false
native_support_supported = false
sentience_supported = false
phase8_opened = false
ant_ecology_opened = false
ready_for_n25
```
