# N25 Implementation Plan - Spark / Sub-Basin / New-Basin Formation

## Aim

N25 tests whether becoming pressure can produce a distinguishable sub-basin or
new-basin candidate rather than only reinforcing, thickening, or relabeling an
existing basin.

The experiment must preserve two N24 handoff lanes:

```text
native lane:
  AB5 / N24-C5 surplus-supported optionality
  native flux/leakage debt remains at 1e-9

producer-assisted lane:
  I7-C producer-mediated flux-conditioning scaffold
  naturalization target = native_flux_routing_or_rate_limiting_surface
```

Producer-assisted success is useful as a missing-mechanism probe, but it cannot
retroactively upgrade native N24-C6 or native N25 formation evidence.

N25 must not invent spark machinery unless needed. LGRC is already expected to
emit spark-like evidence, and `examples/lgrc9v3` already contains native
spark-ish cases:

```text
examples/lgrc9v3/README.md
examples/lgrc9v3/causal_spark_diagnostics.py
examples/lgrc9v3/refinement_packet_transport.py
```

The native lane should start by reusing existing LGRC/LGRC9V3 spark mechanisms
or examples. New producer code is allowed only as a declared extension when the
native/example path is insufficient, and must record the missing native
mechanism as naturalization debt.

## Source Rules

N25 may consume:

```text
N20 native-function/proxy contract:
  n20_i4_row_06_spark_sub_basin_new_basin_formation

N20 same-basin/control contract:
  n20_i5_row_06_spark_sub_basin_new_basin_formation

N24 closeout:
  AB5 / N24-C5 native surplus-supported optionality
  producer-assisted I7-C flux scaffold
```

N25 must not consume N24 as:

```text
native_n24_c6
general_abundance_robustness
new_basin_formation_evidence
semantic_choice
reward_maximization
agency
native_support
sentience
phase8_implementation
ant_ecology_specification
```

## Required Evidence Fields

Every positive candidate row must record:

```text
row_id
source_iteration
source_contract_row_digest
source_consumable_contract_row_digest
source_output_digest
run_artifact_id
runtime_config_digest
source_commit_or_source_digest
source_current_inputs
artifact_manifest
artifact_paths
artifact_sha256
artifact_paths_equal_manifest_paths
artifact_sha256_equal_manifest_sha256
all_artifact_sha256_match_file_contents
row_digest
output_digest
row_specific_thresholds_declared_before_use
existing_lgrc_spark_sources_considered
native_spark_mechanism_reuse_status
new_producer_code_justification
lane = native | producer_assisted
lane_success_can_upgrade_native
native_lane_failure_overwritten
producer_assisted_result_class
n20_source_contract_row
n20_consumable_contract_row
n24_native_lane_status
n24_producer_lane_status
formation_class
formation_source
bifurcation_trace
new_boundary_candidate_trace
new_basin_support_coherence_trace
replayable_distinction_trace
old_basin_relation_trace
merge_leakage_trace
formation_window
bifurcation_window
boundary_candidate_window
replay_window
old_basin_reference_window
bifurcation_window_order_valid
thresholds_declared_before_bifurcation_window
old_basin_signature_digest
candidate_basin_signature_digest
candidate_boundary_signature_digest
old_to_candidate_separation_digest
boundary_distinguishability_margin
support_floor_margin_new_region
coherence_floor_margin_new_region
old_basin_separation_margin
merge_leakage_margin
replay_distinction_persistence_ratio
old_basin_thickening_rejected
reshaped_old_boundary_rejected
merge_leakage_rejected
transient_rejected
label_only_rejected
native_flux_debt_bound
native_flux_debt_widened
native_flux_debt_status
producer_flux_window_bound
producer_flux_window_declared_before_use
native_flux_debt_not_overwritten
support_floor_result
coherence_floor_result
boundary_integrity_result
flux_or_leakage_result
producer_residue_classification
naturalization_debt
ap4_dependency_status
ap5_dependency_status
bf_ladder_rung
row_decision
basin_formation_claim_allowed
claim_ceiling
unsafe_claim_flags
n25_closeout_ceiling
n25_closeout_ladder_rung_assigned
```

## Formation Classification

Iteration 2 must freeze these distinctions before positive rows:

```text
sub_basin_candidate =
  boundary-distinguishable region inside or attached to old basin
  old-basin relation remains auditable
  support/coherence floor is distinct from local old-basin thickening

new_basin_candidate =
  boundary-distinguishable region with replayable support/coherence floor
  not reducible to old-basin thickening
  merge/leakage controls clean
  persists under stress/threshold matrix
```

Every candidate row must classify the observed formation:

```text
formation_class =
  reinforced_old_basin |
  reshaped_old_boundary |
  sub_basin_candidate |
  new_basin_candidate |
  transient_fluctuation |
  merge_leakage_artifact |
  producer_assisted_scaffold

formation_source =
  native_source_current_bifurcation |
  native_old_basin_thickening |
  native_merge_leakage |
  producer_flux_conditioned |
  hidden_producer_insertion |
  label_only |
  report_derived
```

Native `BF3+` requires `formation_source =
native_source_current_bifurcation`. Producer-assisted `BF3+` requires
`formation_source = producer_flux_conditioned`.

## Lane Ceilings

Every row must record:

```text
lane = native | producer_assisted
lane_success_can_upgrade_native = false
native_lane_failure_overwritten = false
producer_assisted_result_class =
  not_applicable |
  producer_mediated_scaffold_candidate |
  missing_native_mechanism_probe
```

Native lane ceiling:

```text
may support native BF rungs if all native gates pass
cannot omit or widen the inherited N24 native flux debt
```

Producer-assisted lane ceiling:

```text
may support producer-assisted BF candidate
may identify naturalization target
cannot upgrade native BF
cannot upgrade N24 native lane
cannot support native support or Phase 8
```

## Native Flux Debt

Native rows must include:

```text
native_flux_debt_bound = 1e-9
native_flux_debt_widened = false
native_flux_debt_status =
  preserved |
  violated_blocks_native_row |
  not_applicable_producer_lane
```

Producer-assisted rows must include:

```text
producer_flux_window_bound
producer_flux_window_declared_before_use = true
native_flux_debt_not_overwritten = true
producer_conditioned_flux_bound_max = 1e-8
max_conditioning_windows = 10
producer_threshold_relaxation_rejected = true
```

Native spark source policy:

```text
existing_lgrc_spark_behavior_expected = true
existing_examples_must_be_considered_before_new_producer_code = true
new_producer_code_allowed_only_if_needed = true
producer_extension_must_signal_missing_native_mechanism = true
```

Lane cross-field invariants:

```text
if lane = native:
  formation_source = native_source_current_bifurcation
  producer_assisted_result_class = not_applicable
  lane_success_can_upgrade_native = false
  native_lane_failure_overwritten = false
  native_flux_debt_bound = 1e-9
  native_flux_debt_widened = false
  native_flux_debt_status = preserved

if lane = producer_assisted:
  formation_source = producer_flux_conditioned
  producer_assisted_result_class =
    producer_mediated_scaffold_candidate | missing_native_mechanism_probe
  lane_success_can_upgrade_native = false
  native_lane_failure_overwritten = false
  native_flux_debt_not_overwritten = true
```

Temporal order must be recorded:

```text
bifurcation_window.end_step <= boundary_candidate_window.start_step
thresholds_declared_before_bifurcation_window = true
```

## Artifact Roles

Artifact manifests must use explicit roles:

```text
bifurcation_trace
new_boundary_candidate_trace
new_basin_support_coherence_trace
replayable_distinction_trace
old_basin_relation_trace
merge_leakage_trace
native_flux_debt_trace
producer_intervention_ledger
formation_replay_trace
stress_boundary_trace
negative_control_trace
runtime_trace
threshold_record
active_null_trace
closeout
source_handoff
schema_control_freeze
```

## Local Ladders

```text
BF0 = no source-current basin-formation evidence
BF1 = run artifact with becoming-pressure / N24 optionality context
BF2 = bifurcation or spark trace observed, but distinguishable basin not yet stable
BF3 = source-current distinguishable sub-basin boundary/support candidate
BF4 = replay/control-backed sub-basin differentiation candidate
BF5 = stress/threshold-backed new-basin formation candidate with merge/leakage controls clean
BF6 = N26-ready bounded basin-formation evidence
```

```text
N25-C0 = contract-only closeout
N25-C1 = active-null/control discipline established
N25-C2 = spark/bifurcation partial
N25-C3 = source-current sub-basin candidate
N25-C4 = replay/control-backed sub-basin differentiation candidate
N25-C5 = stress/threshold-backed basin-formation candidate
N25-C6 = N26-ready bounded basin-formation evidence
```

## Controls

Required controls:

```text
label_only_new_basin_rejected
single_basin_thickening_relabel_rejected
reshaped_old_boundary_relabel_rejected
merge_leakage_masquerading_as_new_basin_rejected
non_replayable_transient_rejected
hidden_producer_insertion_rejected
n24_optionality_relabel_as_formation_rejected
producer_assisted_success_does_not_overwrite_native_failure
native_flux_debt_remains_row_local
producer_schedule_post_hoc_control
producer_hidden_support_control
producer_threshold_relaxation_control
producer_basin_insertion_without_trace_control
producer_success_as_native_relabel_control
producer_success_overwrites_native_failure_control
native_spark_source_policy_rejected
producer_before_native_spark_path_rejected
ap4_gap_prose_only_rejected
ap5_proxy_target_omission_rejected_when_applicable
semantic_learning_relabel_rejected
semantic_choice_relabel_rejected
agency_relabel_rejected
native_support_relabel_rejected
phase8_relabel_rejected
ant_ecology_relabel_rejected
```

Control status semantics:

```text
active-null rows:
  expected_status = failed_closed

positive candidate rows:
  blocker_absent_status = passed
  failed_closed may satisfy a negative-control row, not automatically a
  positive row
  failed_open blocks row and closeout upgrade
  not_run blocks dependent rung
  not_applicable requires scope reason
```

Positive-row control result schema:

```text
control_results = [
  {
    control_id
    control_status
    blocked_condition
    expected_result
    actual_result
    claim_allowed_when_control_triggers
    rung_effect
  }
]
```

Active-null sentinel values such as `not_applicable_active_null_fixture` are
allowed only when:

```text
schema_instantiation_only = true
positive_evidence_admissible = false
```

Positive rows must use strict boolean values for artifact path/SHA validation.

I1 control-name aliases:

```text
label_only_new_basin_control -> label_only_new_basin_rejected
hidden_producer_insertion_control -> hidden_producer_insertion_rejected
hidden_producer_support_control -> producer_hidden_support_control
semantic_relabel_control -> semantic_choice_relabel_rejected / semantic_learning_relabel_rejected
native_support_relabel_control -> native_support_relabel_rejected
phase8_relabel_control -> phase8_relabel_rejected
```

## Iterations

### Iteration 1. Source And Handoff Inventory

Build a source inventory for N20 and N24, including native and
producer-assisted N24 lanes. No BF rung is assigned and no positive N25
evidence is opened.

### Iteration 2. Basin-Formation Schema And Controls

Freeze row schema, lane enums, BF/N25-C ladders, source-current field
requirements, producer-residue accounting, naturalization debt, replay rules,
native flux debt invariants, artifact roles, distinguishability metrics,
formation classification, lane ceilings, and fail-closed controls.

### Iteration 3. Active Nulls And Failure Baselines

Instantiate false-positive rows before positive probes:

```text
label_only_new_basin
single_basin_thickening
reshaped_old_boundary_only
merge_leakage_as_basin
non_replayable_transient
hidden_producer_insertion
n24_optionality_relabel
producer_assisted_native_upgrade_relabel
native_flux_debt_omitted
ap_gap_prose_only
unsafe_semantic_learning_relabel
unsafe_choice_agency_native_support_phase8_relabels
existing_lgrc9v3_spark_examples_skipped
producer_before_native_spark_path
```

The unsafe-claim umbrella is deliberately split into semantic-learning and
choice/agency/native-support/Phase-8 relabel rows so I3 can show each blocker
family failing closed. The final two rows come from the native-spark-first
global guard: N25 must not bypass existing LGRC9V3 spark examples or introduce
producer spark scaffolds before the native spark path is evaluated.

All must fail closed.

### Iteration 4. Native Optional-Branch Bifurcation Probe

Attempt a native source-current bifurcation/sub-basin probe using N24 native
AB5 optionality while preserving the inherited `1e-9` flux/leakage bound.

### Iteration 5. Native Replay And Control Matrix

Replay any native BF candidate and run controls for label-only, thickening,
merge/leakage, transient, and hidden producer paths.

### Iteration 6. Producer-Assisted Flux-Conditioned Formation Probe

Use the N24 I7-C producer-mediated flux scaffold as a separate lane. Test
whether producer-conditioned flux enables a stronger formation candidate while
recording producer residue and naturalization debt.

### Iteration 7. Comparative Stress And Formation Boundary Matrix

Compare native and producer-assisted candidates under stress. Determine whether
the producer-assisted lane identifies a minimal missing native mechanism.

### Iteration 8. Closeout And N26 Handoff

Classify final BF and N25-C rungs, preserve claim boundaries, record N26 proxy
divergence / proxy collapse handoff, and keep agency/native support/Phase 8
blocked.
