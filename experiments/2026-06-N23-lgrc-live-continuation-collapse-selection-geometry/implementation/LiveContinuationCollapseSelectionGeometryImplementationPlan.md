# N23 Live-Continuation Collapse And Selection Geometry Implementation Plan

## Goal

N23 tests whether multiple live continuation branches can resolve into one
source-current continuation while preserving auditable counterfactual
alternatives and claim boundaries.

The experiment should support only:

```text
bounded artifact-level live-continuation collapse / selection-geometry
candidate
```

It must not support:

```text
semantic choice
semantic intention
agency
free will
selfhood
identity acceptance
native support
sentience
Phase 8 implementation
ant ecology implementation
```

## Source Rules

N23 must consume the N20 contract row:

```text
source_contract_row = n20_i4_row_04_live_continuation_collapse
```

N23 must consume N22 closeout only as prerequisite context:

```text
N22 final_supported_su_ladder_rung =
  SU5_producer_mediated_bounded_susceptibility_update_candidate
N22 n22_closeout_ladder_rung = N22-C6
N22 ready_for_n23 = true
```

N22 cannot supply live-continuation collapse evidence. N23 must produce new
source-backed branch-set, collapse, and counterfactual-retention evidence.

N19 may be consumed only as AP-gap boundary context:

```text
n19_native_readiness_boundary_consumption =
  ap_gap_boundary_only
```

N19 must not be consumed as live-continuation evidence, selection evidence, or
an LC ladder assignment source.

When N23 mirrors N20 or N22 source statuses, inherited fields must be prefixed:

```text
n20_source_downstream_consumption_status
n22_source_closeout_status
```

## AP4 Gap Rule

N23 is the first N20-N29 primitive intended to directly test the missing AP4
condition: source-current route or branch selection. N23 may support an AP4
bridge record only if live branch alternatives, collapse, counterfactual
retention, replay, and controls are all source-backed.

N23 closeout must record:

```text
ap4_bridge_status =
  not_supported |
  bridge_candidate_supported |
  blocked_by_live_branch_set |
  blocked_by_single_live_branch |
  blocked_by_counterfactual_retention |
  blocked_by_same_basin_floor |
  blocked_by_report_only_evidence |
  blocked_by_artifact_manifest |
  blocked_by_not_route_or_branch_conditioned |
  blocked_by_replay |
  blocked_by_controls |
  blocked_by_producer_preference |
  blocked_by_ap_gap
```

The bridge status is not semantic choice and cannot retroactively upgrade N14
unless a later review explicitly reclassifies AP4 NAT4 evidence.

## Required Evidence Fields

Every candidate evidence row must record:

```text
row_id
source_contract_row
source_contract_row_digest
source_output_digest
run_artifact_id
source_commit_or_source_digest
runtime_config_digest
source_current_inputs
row_specific_thresholds_declared_before_use
n19_native_readiness_boundary_consumption
n20_source_downstream_consumption_status
n22_source_closeout_status
branch_window
collapse_window
pre_collapse_geometry_trace
live_branch_set_trace
branch_support_coherence_traces
branch_boundary_flux_traces
branch_counterfactual_records
collapsed_continuation_trace
counterfactual_branch_retention_trace
selected_branch_source_current_reason
producer_selected_branch_label_absent
producer_preference_injection_absent
random_tie_status
same_basin_continuation_rule
same_basin_invariant_fields
out_of_scope_drift_blocks_row
selection_not_label_reassignment
route_or_branch_conditioned
peer_or_counterfactual_comparison
peer_or_counterfactual_scope_reason
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
collapse_trace_digest
replay_collapse_digest
counterfactual_retention_digest
collapse_persistence_ratio
collapse_threshold_or_rule
fake_alternatives_rejected
single_branch_relabel_rejected
post_hoc_selection_rejected
producer_preference_rejected
random_tie_as_collapse_rejected
producer_residue_fields
naturalization_debt_fields
blocked_relabel_fields
claim_ceiling
unsafe_claim_flags
row_decision
live_continuation_collapse_claim_allowed
semantic_choice_claim_allowed
derived_report_only
artifact_manifest
artifact_paths
artifact_sha256
all_artifact_sha256_match_file_contents
output_digest
```

## Local Ladder

```text
LC0 = no source-current live-continuation evidence
LC1 = run artifact with possible branch/collapse context
LC2 = source-current live branch set with at least two real alternatives
LC3 = source-current collapse trace from live branch set to one continuation
LC4 = replay/control-backed live-continuation collapse candidate
LC5 = AP4-relevant route/branch selection-geometry candidate
LC6 = N24-ready bounded live-continuation collapse evidence
```

Rows below `LC3` cannot support collapse. Rows below `LC4` cannot support
replay/control-backed selection geometry. `LC6` is a handoff rung, not agency
or semantic choice.

## Closeout Ladder

N23 must also use a tranche-level closeout ladder:

```text
N23-C0 = contract-only closeout
  N20/N22 handoff consumed, but no N23 collapse evidence opened.

N23-C1 = active-null/control discipline established
  Active nulls and failure baselines fail closed, but no positive LC row.

N23-C2 = live-branch partial
  Live branch evidence appears, but collapse, replay, controls, or AP gaps
  block stronger support.

N23-C3 = source-current collapse candidate
  LC3 reached on at least one source-backed row.

N23-C4 = replay/control-backed collapse candidate
  LC4 reached after replay and fail-closed controls.

N23-C5 = AP4-relevant selection-geometry candidate
  LC5 reached with route/branch-conditioned source-current collapse evidence.

N23-C6 = N24-ready bounded live-continuation collapse evidence
  LC5/LC6 evidence plus producer residue, naturalization debt, AP4/AP5
  discipline, unsafe-claim blockers, src_diff_empty, and N24 handoff.
```

The closeout ladder classifies the whole N23 tranche. It must not convert an
LC row into semantic choice, intention, agency, native support, sentience, or a
Phase 8 claim.

## Schema Policies To Freeze

Iteration 2 must freeze how branch alternatives may be counted:

```text
live_branch_set_trace = source-current branch records before collapse
branch_counterfactual_records = auditable non-selected pre-collapse records
collapsed_continuation_trace = source-current continuation after collapse
selection_not_label_reassignment = true
out_of_scope_drift_blocks_row = true
```

Operational live-branch acceptance must be:

```text
same_source_current_run = true
same_declared_branch_window = true
branch_window.end_step <= collapse_window.start_step
pre_collapse_live_branch_set_trace.step_range subset branch_window
collapsed_continuation_trace.step_range subset collapse_window
branch_specific_support_coherence_traces_present = true
branch_specific_boundary_flux_traces_present = true
```

Branches assembled across independent runs, replay forks, report-side
construction, or post-hoc alternative labels do not count as original
live-branch-set evidence. Replay forks may audit counterfactuals, but they
cannot create the original live-branch-set evidence.

Counterfactual retention must mean:

```text
counterfactual_branch_retention_trace = immutable audit record proving that
the non-selected branches existed source-current before collapse.
```

It is not sufficient if it contains only branch labels, producer alternatives,
replay-created branches, or report-side reconstruction. Counterfactual
retention is not a requirement that non-selected branches remain dynamically
active after collapse.

The selected branch reason must be a closed enum:

```text
selected_branch_source_current_reason =
  support_gradient_dominance |
  coherence_floor_dominance |
  boundary_integrity_dominance |
  flux_leakage_minimization |
  susceptibility_delta_conditioned |
  route_cost_or_conductance_dominance |
  multi_channel_geometry_dominance |
  not_supported
```

Blocked selected-branch reason values:

```text
producer_label
producer_preference
random_tie
post_hoc_report_selection
single_branch_relabel
semantic_choice_label
```

Artifact roles must be frozen:

```text
artifact_role =
  source_contract |
  inherited_context |
  runtime_trace |
  branch_set_trace |
  collapse_trace |
  counterfactual_retention_trace |
  replay_trace |
  snapshot_load_replay_trace |
  duplicate_replay_trace |
  negative_control_trace |
  active_null_trace |
  report |
  closeout
```

Positive LC evidence may not be supported by artifacts whose only roles are
`report`, `inherited_context`, `source_contract`, or `closeout`.

Rows with fake alternatives, single-branch relabels, producer preferences,
random ties, hidden labels, or post-hoc selected-branch construction must be
blocked rather than interpreted as successful selection geometry.

## Iteration Plan

### Iteration 1. Source Handoff Inventory

Inventory N20 live-continuation contract, N22 closeout, N19 AP4/AP5 gap
boundary, and source rules. No positive N23 evidence may open.

Expected artifacts:

```text
outputs/n23_source_handoff_inventory.json
reports/n23_source_handoff_inventory.md
scripts/build_n23_source_handoff_inventory.py
```

### Iteration 2. Schema, Ladder, And Control Freeze

Freeze candidate row schema, LC ladder, N23-C ladder, branch/collapse fields,
AP4/AP5 enums, replay requirements, row decisions, active-null expectations,
and claim boundary. No positive N23 evidence may open.

Expected artifacts:

```text
outputs/n23_live_continuation_schema_and_controls.json
reports/n23_live_continuation_schema_and_controls.md
scripts/build_n23_live_continuation_schema_and_controls.py
```

### Iteration 3. Active Nulls And Failure Baselines

Instantiate active nulls before positive probes:

```text
fake_alternative_control
single_branch_relabel_control
post_hoc_selected_branch_control
producer_preference_injection_control
random_tie_as_collapse_control
missing_counterfactual_retention_control
N22_susceptibility_as_choice_relabel_control
route_conditioned_row_missing_AP4
proxy_conditioned_row_missing_AP5
AP_gap_prose_only
semantic_choice_relabel
agency_relabel
native_support_relabel
phase8_relabel
```

Expected artifacts:

```text
outputs/n23_active_nulls_and_failure_baselines.json
reports/n23_active_nulls_and_failure_baselines.md
scripts/build_n23_active_nulls_and_failure_baselines.py
```

### Iteration 4. Minimal Live-Branch Collapse Probe

Produce the first source-current live branch set and collapse candidate. Keep
it provisional pending replay/control validation.

Expected artifacts:

```text
outputs/n23_minimal_live_branch_collapse_probe.json
reports/n23_minimal_live_branch_collapse_probe.md
scripts/build_n23_minimal_live_branch_collapse_probe.py
```

### Iteration 4-A. Multi-Branch Live-Set Collapse Probe

Add breadth without replacing Iteration 4 by producing a source-current
live-branch set with three or more branch alternatives in the same basin.
Keep the result provisional pending its own replay/control validation.

Expected artifacts:

```text
outputs/n23_multibranch_live_set_collapse_probe.json
reports/n23_multibranch_live_set_collapse_probe.md
scripts/build_n23_multibranch_live_set_collapse_probe.py
```

### Iteration 5. Collapse Replay And Counterfactual Controls

Replay the minimal collapse row, run order/post-hoc/producer-preference
controls, and decide whether LC4 is supported.

Iteration 5 replay rows are replay/control records, not new 80-field candidate
evidence rows. They must consume the full Iteration 4 candidate row by
reference, record that schema role explicitly, and defer full candidate-schema
revalidation to the Iteration 7 matrix.

The local I5 control suite is intentionally narrower than the full I7 matrix,
but it must include constructed negative-control evaluations for order
inversion, post-hoc stitching, fake alternatives, single-branch relabeling,
missing counterfactual retention, producer preference injection, and
random-tie-as-collapse. Unsafe claim relabels remain false in the replay row
and are revalidated in the full I7 matrix.

Expected artifacts:

```text
outputs/n23_collapse_replay_and_counterfactual_controls.json
reports/n23_collapse_replay_and_counterfactual_controls.md
scripts/build_n23_collapse_replay_and_counterfactual_controls.py
```

### Iteration 5-A. Multi-Branch Collapse Replay And Controls

Replay the Iteration 4-A multi-branch collapse row without changing the
minimal Iteration 5 result. This is additive breadth evidence: it can support
a multi-branch provisional LC4 candidate, but it must not close AP4, LC5, LC6,
semantic choice, agency, or native support.

Iteration 5-A follows the same replay-row schema policy as Iteration 5:
replay rows are replay/control records, not new 80-field candidate evidence
rows. The full Iteration 4-A candidate row remains the referenced evidence
row, and Iteration 7 performs the full matrix-level revalidation.

Expected artifacts:

```text
outputs/n23_multibranch_collapse_replay_and_controls.json
reports/n23_multibranch_collapse_replay_and_controls.md
scripts/build_n23_multibranch_collapse_replay_and_controls.py
```

### Iteration 6. AP4-Relevant Selection Geometry Probe

Test whether route/branch selection is source-current and geometry-conditioned
enough to support an AP4 bridge candidate without semantic choice promotion.

Iteration 6 consumes the replay/control-backed Iteration 5 and 5-A rows by
reference. It does not create a fresh live-branch run. Its bridge rows must
show that LC4-backed branch collapse was selected by source-current branch
geometry, with AP4 dependency recorded row-locally, AP5 not applicable unless
proxy/target formation is used, and producer/semantic relabels failing closed.
I6 may support provisional LC5 / N23-C5 candidate status, but LC6, final AP4,
semantic choice, agency, native support, Phase 8, and ant-ecology claims remain
blocked pending I7/I8.

I6 bridge-by-reference records may use `row_schema_role` as an explicitly
declared I6 extension field. I6 artifacts must still use the Iteration 2 frozen
artifact-role enum, with `artifact_subrole` for AP4-specific trace names.

Expected artifacts:

```text
outputs/n23_ap4_selection_geometry_probe.json
reports/n23_ap4_selection_geometry_probe.md
scripts/build_n23_ap4_selection_geometry_probe.py
```

### Iteration 6-A. AP4 Selection-Geometry Robustness Probe

Stress-test the Iteration 6 AP4 bridge candidate before the full matrix. This
iteration must not replace I6 or claim general AP4 robustness. It should vary
bounded source-current branch geometry and classify whether selection follows
geometry under margin erosion and alternate-winner conditions while failing
closed under below-margin or tie conditions.

I6-A robustness rows may use `row_schema_role` and `stress_case_role` as
explicitly declared I6-A extension fields. I6-A artifacts must use the Iteration
2 frozen artifact-role enum, with `artifact_subrole` for stress-specific
snapshots, event logs, branch traces, collapse traces, duplicate replays, and
negative controls.

Expected artifacts:

```text
outputs/n23_ap4_selection_geometry_robustness_probe.json
reports/n23_ap4_selection_geometry_robustness_probe.md
scripts/build_n23_ap4_selection_geometry_robustness_probe.py
```

### Iteration 7. Replay And Control Matrix

Consume all provisional rows, run the full replay/control matrix, preserve
claim ceilings, and prepare closeout.

Expected artifacts:

```text
outputs/n23_replay_and_control_matrix.json
reports/n23_replay_and_control_matrix.md
scripts/build_n23_replay_and_control_matrix.py
```

### Iteration 8. Closeout And N24 Handoff

Classify final N23 support, AP4 bridge status, producer residue,
naturalization debt, AP4/AP5 dependency status, unsafe blockers, and N24
handoff.

Expected artifacts:

```text
outputs/n23_closeout_and_n24_handoff.json
reports/n23_closeout_and_n24_handoff.md
scripts/build_n23_closeout_and_n24_handoff.py
```

## Closeout Requirement

N23 closeout must answer:

```text
Did N23 produce source-backed live branch set evidence?
Did a source-current collapse trace resolve those branches into one continuation?
Were non-selected branches retained as auditable counterfactual alternatives?
Did replay and controls reject fake alternatives, single-branch relabels,
post-hoc selection, producer preference, random tie, and semantic choice relabels?
Did N23 produce an AP4-relevant bridge candidate, or did AP4 remain blocked?
Which producer-mediated fields remain residue?
Which naturalization-debt fields remain unresolved?
Were AP4/AP5 dependencies carried row-locally?
Did unsafe relabels stay blocked?
Is N24 ready, and with what claim ceiling?
```
