# N28 Generative Vs Extractive Persistence Implementation Checklist

## Initialization

- [x] Create N28 experiment branch.
- [x] Create experiment directory structure.
- [x] Add README.
- [x] Add hypotheses.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add configs/outputs/reports/scripts indexes.

Initial state:

```text
status = initialized
positive_generative_evidence_opened = false
ge_ladder_rung_assigned = false
n28_closeout_ladder_rung_assigned = false
n27_generative_persistence_supported = false
native_support_opened = false
phase8_completion_opened = false
ant_ecology_opened = false
ready_for_iteration_1 = true
```

## Iteration 1 - Source Inventory And Generative / Extractive Contract Admission

- [x] Consume N20 I3 generative/extractive producer-residue and naturalization-debt ledger.
- [x] Consume N20 I4 native-function / proxy descriptor for generative/extractive persistence.
- [x] Consume N20 I5 same-basin continuation contract as the normative downstream contract.
- [x] Consume N27 closeout as bounded CT6 transfer and N28 precursor context only.
- [x] Record N27 side-effect precursor metrics without promoting them to N28 evidence.
- [x] Record N27 `n28_generative_persistence_supported = false`.
- [x] Record source roles, source digests, and source consumption boundaries.
- [x] Record medium-debt fields deferred to N28/N29.
- [x] Confirm no positive generative/extractive evidence opens.
- [x] Confirm no semantic cooperation, native support, agency, sentience, Phase 8, or ant ecology claim opens.

Expected result:

```text
status = passed
acceptance_state = accepted_source_inventory_generative_extractive_contract_admission_no_positive_evidence
positive_generative_evidence_opened = false
candidate_rows_classified = false
ge_ladder_rung_assigned = false
n28_closeout_ladder_rung_assigned = false
n27_consumed_as_n28_evidence = false
n27_transfer_success_as_n28_success_allowed = false
native_support_opened = false
phase8_completion_opened = false
ant_ecology_opened = false
ready_for_iteration_2 = true
```

Artifacts:

```text
outputs/n28_source_inventory_and_contract_admission.json
reports/n28_source_inventory_and_contract_admission.md
scripts/build_n28_source_inventory_and_contract_admission.py
```

Result:

```text
status = passed
acceptance_state = accepted_source_inventory_generative_extractive_contract_admission_no_positive_evidence
output_digest = f30af50b1e1209039b82454b510f4765de7ee8befe214d96218dec3207db5985
source_record_count = 8
failed_checks = []
positive_generative_evidence_opened = false
positive_extractive_evidence_opened = false
candidate_rows_classified = false
ge_ladder_rung_assigned = false
n28_closeout_ladder_rung_assigned = false
n27_consumed_as_n28_evidence = false
n27_transfer_success_as_n28_success_allowed = false
n27_precursor_metrics_context_only = true
n27_generative_persistence_supported = false
medium_debt_recorded = true
native_support_opened = false
phase8_completion_opened = false
ant_ecology_opened = false
ready_for_iteration_2 = true
```

Interpretation:

```text
I1 admits the N20 generative/extractive contract stack and the N27
side-effect precursor as context only. N27 supplies useful starting metrics
for focal stability, neighbor capacity, extraction cost, and merge/leakage,
but N27 explicitly keeps N28 generative persistence unsupported. The medium
debt fields are carried forward for schema/control work; they are not
success evidence.
```

## Iteration 2 - Generative / Extractive Schema And Control Freeze

- [x] Freeze GE0...GE6 ladder.
- [x] Freeze N28-C0...N28-C6 closeout ladder.
- [x] Freeze paired-regime evidence requirement: primary and alternative rows for generative, extractive, and competitive/neutral regimes.
- [x] Freeze the three-axis classifier: focal persistence, neighborhood capacity, and extraction/leakage.
- [x] Freeze source precedence as immutable from I1 onward.
- [x] Pin I1 output digest and consumed N20/N27 row/output digests for later rows.
- [x] Freeze N20 I5 same-basin continuation contract as normative.
- [x] Freeze N20 I4 native-function / proxy descriptor as descriptor context.
- [x] Freeze N20 I3 producer-residue ledger as residue / debt context.
- [x] Freeze N27 closeout and side-effect rows as context-only.
- [x] Freeze required evidence fields.
- [x] Freeze reusable `generative_extractive_core` object.
- [x] Freeze `generative_extractive_core_digest` canonicalization policy.
- [x] Freeze focal stability and neighbor capacity formulas.
- [x] Freeze extraction, flattening, merge/leakage formulas.
- [x] Freeze regime labels and evidence roles.
- [x] Freeze regime-boundary trace requirements.
- [x] Freeze `shared_regime_policy_status` enum.
- [x] Freeze policy-divergence record fields.
- [x] Freeze policy-retuning / label-specific-threshold / post-hoc-boundary controls.
- [x] Freeze medium-debt and producer-residue record fields.
- [x] Require `medium_debt_record`, `producer_residue_record`, `capacity_attribution_trace`, `shared_regime_policy_id`, `shared_regime_policy_status`, and `policy_divergence_record` in positive rows.
- [x] Freeze `medium_debt_as_success_allowed = false`.
- [x] Freeze rung-specific artifact role requirements.
- [x] Freeze replay requirements.
- [x] Freeze AP4/AP5 dependency statuses.
- [x] Require row-local reason when AP4/AP5 status is `not_applicable`.
- [x] Freeze active-null/control families.
- [x] Freeze claim boundary and unsafe claim flags.
- [x] Confirm no positive N28 evidence opens.

Expected result:

```text
status = passed
acceptance_state = accepted_generative_extractive_schema_and_controls_frozen_no_positive_evidence
n28_closeout_ceiling = N28-C2_schema_controls_and_classification_policy_frozen
positive_generative_evidence_opened = false
candidate_rows_classified = false
ge_ladder_rung_assigned = false
n28_closeout_ladder_rung_assigned = false
ready_for_iteration_3 = true
```

Artifacts:

```text
outputs/n28_generative_extractive_schema_and_controls.json
reports/n28_generative_extractive_schema_and_controls.md
scripts/build_n28_generative_extractive_schema_and_controls.py
```

Result:

```text
status = passed
acceptance_state = accepted_generative_extractive_schema_and_controls_frozen_no_positive_evidence
n28_closeout_ceiling = N28-C2_schema_controls_and_classification_policy_frozen
output_digest = e118496c025e1a36aac7e4337adcacd869715a5ce5ec6aaaf1558ef0d6576c18
source_inventory_output_digest = f30af50b1e1209039b82454b510f4765de7ee8befe214d96218dec3207db5985
required_evidence_field_count = 66
failed_checks = []
positive_generative_evidence_opened = false
positive_extractive_evidence_opened = false
candidate_rows_classified = false
ge_ladder_rung_assigned = false
n28_closeout_ladder_rung_assigned = false
native_support_opened = false
phase8_completion_opened = false
ant_ecology_opened = false
ready_for_iteration_3 = true
```

Interpretation:

```text
I2 freezes the N28 regime classifier as a three-axis source-current policy:
focal persistence, neighborhood capacity, and extraction/leakage. It also
freezes the reusable generative_extractive_core and core digest policy so
later replay, controls, and stress rows can reference a canonical object
instead of reconstructing claims in prose. Medium debt, producer residue,
N27 transfer success, and N27 side-effect metrics remain context only.
```

## Iteration 3 - Active Nulls And Failure Baselines

- [x] Run focal-survival-only-as-generative control.
- [x] Run neighbor-label-only-as-capacity control.
- [x] Run neighbor-count-only-as-capacity control.
- [x] Run merge/leakage-as-support control.
- [x] Run extractive-flattening-masked control.
- [x] Run competitive-persistence-as-generative control.
- [x] Run transfer-success-as-N28-success control.
- [x] Run hidden-capacity-attribution-policy control.
- [x] Run producer-generativity-label control.
- [x] Run medium-segmentation-policy-hidden control.
- [x] Run environment-capacity-budget-mismatch control.
- [x] Run neighbor-support-floor-missing control.
- [x] Run neighbor-boundary-integrity-missing control.
- [x] Run replay-failure control.
- [x] Run stress-variant-failure control.
- [x] Run semantic-cooperation relabel control.
- [x] Run native-support relabel control.
- [x] Run ant-ecology relabel control.
- [x] Run Phase 8 completion relabel control.
- [x] Run native-AP5 / AP5-NAT4-gap relabel controls.
- [x] Confirm failed-open control count is zero.
- [x] Confirm no positive GE rung is assigned.

Expected result:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_generative_evidence
n28_closeout_ceiling = N28-C3_active_nulls_fail_closed
positive_generative_evidence_opened = false
failed_open_control_count = 0
ready_for_iteration_4_minimal_generativity_probe = true
```

Artifacts:

```text
outputs/n28_active_nulls_and_failure_baselines.json
reports/n28_active_nulls_and_failure_baselines.md
scripts/build_n28_active_nulls_and_failure_baselines.py
```

Result:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_generative_evidence
n28_closeout_ceiling = N28-C3_active_nulls_fail_closed
output_digest = ddd8234d8f3b5fb424c8160d65e90adbe755916c6e4e1b26bd8574a48dc6e8a4
source_schema_output_digest = e118496c025e1a36aac7e4337adcacd869715a5ce5ec6aaaf1558ef0d6576c18
active_null_row_count = 35
failed_closed_control_count = 35
failed_open_control_count = 0
failed_checks = []
positive_generative_evidence_opened = false
positive_extractive_evidence_opened = false
candidate_rows_classified = false
ge_ladder_rung_assigned = false
n28_closeout_ladder_rung_assigned = false
native_support_opened = false
phase8_completion_opened = false
ant_ecology_opened = false
ready_for_iteration_4_minimal_generativity_probe = true
```

Interpretation:

```text
I3 instantiates every I2 control family as an active null. The nulls show
that source/artifact hygiene failures, malformed or missing canonical core
digests, focal survival alone, neighbor labels/counts, merge/leakage,
extraction masking, transfer success, hidden attribution, producer labels,
medium segmentation, missing floors/boundaries, replay/stress failures, AP5
relabels, semantic relabels, native support, Phase 8, and ant ecology all fail
closed. The rows are control fixtures only; they do not provide source-current
N28 positive evidence and do not assign a GE rung.
```

## Iteration 4 - Primary Generative Candidate Probe

- [x] Produce a generative candidate row, not only a focal-survival row.
- [x] Declare classification policy before use.
- [x] Record focal basin signature and stability.
- [x] Record focal support/coherence floor.
- [x] Record neighbor or sub-basin scope.
- [x] Record neighbor distinguishability, support, and boundary traces.
- [x] Record environment basin-forming capacity trace.
- [x] Record extraction, flattening, merge/leakage traces.
- [x] Confirm neighbor capacity improves above declared threshold.
- [x] Confirm extraction, flattening, merge, and leakage remain below ceilings.
- [x] Set `regime_label = generative`.
- [x] Set `regime_evidence_role = positive_candidate`.
- [x] Record artifact manifest and hashes.
- [x] Keep result provisional pending replay/control validation.

Result:

```text
status = passed
acceptance_state = accepted_primary_source_current_ge3_generative_candidate_pending_replay_controls
output_digest = daa25e4694929b11af38d7b044f4b4f5a4e70f6c2fbcae954db6a84854c08e5d
provisional_ge_ladder_rung = GE3
n28_closeout_ceiling = N28-C4_source_current_regime_candidate_supported
shared_regime_policy_status = partially_supported
shared_regime_policy_status_scope = provisionally_primary_only_pending_alternative_and_contrast_rows
ge4_or_stronger_supported = false
ge5_or_stronger_supported = false
ge6_or_stronger_supported = false
final_generative_persistence_supported = false
final_n28_supported = false
ready_for_iteration_4a_alternative_generative_candidate = true
ready_for_iteration_4a_strengthening_generative_candidate = true
```

Artifacts:

```text
outputs/n28_primary_generative_candidate_probe.json
reports/n28_primary_generative_candidate_probe.md
scripts/build_n28_primary_generative_candidate_probe.py
outputs/n28_primary_generative_candidate_probe_artifacts/threshold_policy_trace.json
outputs/n28_primary_generative_candidate_probe_artifacts/source_current_runtime_trace.json
outputs/n28_primary_generative_candidate_probe_artifacts/focal_basin_stability_trace.json
outputs/n28_primary_generative_candidate_probe_artifacts/neighbor_capacity_trace.json
outputs/n28_primary_generative_candidate_probe_artifacts/extraction_leakage_trace.json
outputs/n28_primary_generative_candidate_probe_artifacts/capacity_attribution_trace.json
outputs/n28_primary_generative_candidate_probe_artifacts/classification_trace.json
outputs/n28_primary_generative_candidate_probe_artifacts/generative_extractive_core.json
```

Key metric record:

```text
focal_stability_preserved = true
focal_support_floor_preserved = true
focal_coherence_floor_preserved = true
neighbor_distinguishability_delta = 0.133
neighbor_support_delta = 0.082
neighbor_boundary_delta = 0.126
environment_capacity_delta = 0.123
focal_extraction_cost = 0.018
focal_extraction_cost_ceiling = 0.035
extractive_flattening_score = 0.014
extractive_flattening_ceiling = 0.03
merge_leakage_score = 0.012
merge_leakage_ceiling = 0.025
```

Interpretation:

```text
I4 is the first positive N28 row. It is generative because the focal basin
remains above support/coherence/stability floors while the neighboring capacity
shell becomes more distinguishable, better supported, and better bounded, and
the environment basin-forming capacity increases. It is not merely focal
survival.

In geometric dynamics terms, the focal basin keeps its shape and viability
while the surrounding geometry becomes more basin-capable. The original basin
does not survive by draining or flattening its neighborhood. Its support,
coherence, and stability remain above floor, so the focal basin remains a valid
basin. At the same time, the adjacent shell becomes more structured: it
separates more clearly from the focal basin, gains support, gains boundary
integrity, and has higher capacity to hold basin-like organization.

The dynamics are therefore not one basin persisting by absorbing the
surrounding field, nor focal survival while nearby geometry becomes less
organized. They are persistence with neighboring capacity increase: a stable
basin preserves itself while nearby geometry becomes more capable of holding
distinct organized structure.

The `shared_regime_policy_status = partially_supported` field is intentionally
scoped to this primary generative row only. It does not mean the shared
generative/extractive/competitive policy family is settled. That remains
blocked until the generative strengthening row, extractive contrasts, and
competitive/neutral contrasts exist.

The artifact manifest uses bundled trace roles, with an explicit alias map:
`neighbor_capacity_trace` covers neighbor distinguishability, neighbor support
floor, neighbor boundary integrity, environment basin-forming capacity, and
neighborhood capacity delta traces; `extraction_leakage_trace` covers focal
extraction cost, extractive flattening, and merge/leakage traces.

I4 inherits the I3 active-null matrix as a fail-closed false-positive boundary:

active_null_matrix_output_digest = ddd8234d8f3b5fb424c8160d65e90adbe755916c6e4e1b26bd8574a48dc6e8a4
row_local_controls_scope = primary_GE3_applicable_controls
full_controls_pending_for_ge4_plus = true

The row remains provisional GE3 because replay, full control validation,
strengthening generative evidence, extractive/competitive/neutral contrasts,
stress testing, and final closeout have not run. N27 transfer evidence is
carried only as context and is not consumed as N28 success evidence.
```

## Iteration 4-A - Generative Strengthening Candidate Probe

- [x] Produce a second generative candidate row under a distinct setup whose purpose is to strengthen I4.
- [x] Test whether the strengthening row can use the same frozen policy family.
- [x] Compare I4-A margins directly against I4 on focal stability, neighbor distinguishability, neighbor support, neighbor boundary integrity, environment capacity, extraction cost, flattening, and merge/leakage.
- [x] Classify the row as corroborating I4 only if it preserves comparable or stronger load-bearing margins without weakening thresholds.
- [x] If the same policy family fails, record policy divergence instead of retuning.
- [x] Confirm thresholds are not widened relative to the primary generative row unless a split-policy blocker is explicitly recorded.
- [x] Confirm the row strengthens I4 but does not replace I4.
- [x] Confirm the row does not import or relabel the primary I4 outcome.
- [x] Record focal basin stability and neighborhood capacity improvement.
- [x] Confirm extraction, flattening, merge, and leakage remain below ceilings.
- [x] Set `regime_label = generative`.
- [x] Set `regime_evidence_role = positive_candidate_alternative`.
- [x] Keep result provisional pending replay/control validation.

Result:

```text
status = passed
acceptance_state = accepted_generative_strengthening_ge3_candidate_pending_replay_controls
output_digest = 07f15756b0584cbc91e4b765e4e96a07de0e62a772e0b0a49f1723f83d68b85c
source_i4_primary_output_digest = daa25e4694929b11af38d7b044f4b4f5a4e70f6c2fbcae954db6a84854c08e5d
provisional_ge_ladder_rung = GE3
n28_closeout_ceiling = N28-C4_source_current_generative_candidate_supported
shared_regime_policy_status = partially_supported
shared_regime_policy_status_scope = strengthened_by_primary_and_i4a_pending_extractives_and_neutral_contrasts
i4_strengthened_not_replaced = true
ge4_or_stronger_supported = false
ge5_or_stronger_supported = false
ge6_or_stronger_supported = false
final_generative_persistence_supported = false
final_n28_supported = false
ready_for_iteration_4b_primary_extractive_contrast = true
```

Artifacts:

```text
outputs/n28_generative_strengthening_candidate_probe.json
reports/n28_generative_strengthening_candidate_probe.md
scripts/build_n28_generative_strengthening_candidate_probe.py
outputs/n28_generative_strengthening_candidate_probe_artifacts/threshold_policy_trace.json
outputs/n28_generative_strengthening_candidate_probe_artifacts/source_current_runtime_trace.json
outputs/n28_generative_strengthening_candidate_probe_artifacts/focal_basin_stability_trace.json
outputs/n28_generative_strengthening_candidate_probe_artifacts/neighbor_capacity_trace.json
outputs/n28_generative_strengthening_candidate_probe_artifacts/extraction_leakage_trace.json
outputs/n28_generative_strengthening_candidate_probe_artifacts/capacity_attribution_trace.json
outputs/n28_generative_strengthening_candidate_probe_artifacts/classification_trace.json
outputs/n28_generative_strengthening_candidate_probe_artifacts/generative_extractive_core.json
```

I4 comparison:

```text
focal_stability: I4 = 0.878, I4-A = 0.889
neighbor_distinguishability_delta: I4 = 0.133, I4-A = 0.154
neighbor_support_delta: I4 = 0.082, I4-A = 0.087
neighbor_boundary_delta: I4 = 0.126, I4-A = 0.145
environment_capacity_delta: I4 = 0.123, I4-A = 0.134
focal_extraction_cost: I4 = 0.018, I4-A = 0.016
extractive_flattening: I4 = 0.014, I4-A = 0.013
merge_leakage: I4 = 0.012, I4-A = 0.011
thresholds_widened_relative_to_i4 = false
i4_imported_as_evidence = false
i4_replaced = false
```

Interpretation:

```text
I4-A strengthens I4 by showing the same generative geometric pattern in a
distinct local setup under the same frozen policy family. The focal basin
remains viable, the adjacent shell gains distinguishability/support/boundary
integrity/environment capacity, and extraction/flattening/merge-leakage are
lower than or equal to I4. This corroborates the I4 generative pattern without
replacing I4 or upgrading to GE4.

Geometrically, I4 is the primary alpha case: focal basin alpha remains stable
while neighbor capacity shell alpha becomes more basin-capable and
extraction/flattening/merge-leakage stay low. I4-A repeats the same kind of
event in a distinct beta setup: focal basin beta remains stable while neighbor
capacity shell beta becomes more basin-capable, again without absorption,
drainage, or merge/leakage masquerading as support.

The topology difference is not new basin birth and not a replay-backed topology
transition. It is a different local basin/shell configuration: different focal
basin id, different neighbor shell id, different runtime fixture digest, and a
stronger capacity margin profile. I4-A therefore strengthens I4 by showing that
the generative geometry is not confined to the alpha setup, while still
remaining GE3 pending replay/control/stress and extractive/neutral contrasts.
```

## Iteration 4-A2 - Generative Mechanism-Diversity Probe

- [x] Produce a generative candidate through a different geometric mechanism, not a margin-optimized copy of I4 or I4-A.
- [x] Preserve focal basin stability.
- [x] Record neighbor capacity gain through split-shell capacity growth and delayed boundary thickening.
- [x] Confirm the mechanism differs from the I4 single-shell and I4-A local-shell margin-strengthening cases.
- [x] Confirm the same frozen policy family is preserved.
- [x] Confirm source-current traces support focal persistence and neighbor capacity gain.
- [x] Confirm extraction, flattening, merge, and leakage remain below ceilings.
- [x] Confirm thresholds are not retuned.
- [x] Confirm mechanism diversity is not inferred from labels alone.
- [x] Keep result provisional pending replay/control validation.

Result:

```text
status = passed
acceptance_state = accepted_generative_mechanism_diversity_ge3_candidate_pending_replay_controls
output_digest = f2785e97307704bff58e413eb071aff10311f0a3d6bd753ebccfb4c1975b6c20
row_digest = 6d7c791cb4a937ab27ccb33c8bc2eae7908be25c60e2a88b45f024e6950af8cf
source_i4_primary_output_digest = daa25e4694929b11af38d7b044f4b4f5a4e70f6c2fbcae954db6a84854c08e5d
source_i4a_strengthening_output_digest = 07f15756b0584cbc91e4b765e4e96a07de0e62a772e0b0a49f1723f83d68b85c
provisional_ge_ladder_rung = GE3
regime_label = generative
regime_evidence_role = positive_candidate_alternative
mechanism_class = split_shell_capacity_growth_with_delayed_boundary_thickening
i4a2_mechanism_diversity_supported = true
ge4_or_stronger_supported = false
failed_checks = []
```

Artifacts:

```text
outputs/n28_generative_mechanism_diversity_probe.json
reports/n28_generative_mechanism_diversity_probe.md
scripts/build_n28_generative_mechanism_diversity_probe.py
outputs/n28_generative_mechanism_diversity_probe_artifacts/threshold_policy_trace.json
outputs/n28_generative_mechanism_diversity_probe_artifacts/source_current_runtime_trace.json
outputs/n28_generative_mechanism_diversity_probe_artifacts/focal_basin_stability_trace.json
outputs/n28_generative_mechanism_diversity_probe_artifacts/neighbor_capacity_trace.json
outputs/n28_generative_mechanism_diversity_probe_artifacts/extraction_leakage_trace.json
outputs/n28_generative_mechanism_diversity_probe_artifacts/capacity_attribution_trace.json
outputs/n28_generative_mechanism_diversity_probe_artifacts/classification_trace.json
outputs/n28_generative_mechanism_diversity_probe_artifacts/generative_extractive_core.json
```

Interpretation:

```text
I4-A2 strengthens the generative side by mechanism diversity rather than margin
optimization. I4 is the alpha single-shell capacity-growth case and I4-A is
the beta local-shell margin-strengthening case. I4-A2 is the epsilon
split-shell case: focal persistence remains viable while two neighboring shell
lobes thicken and gain distinguishability, support, boundary integrity, and
basin-forming capacity.

The important point is not that every value is the largest so far. The point is
that the same frozen classifier accepts a different source-current geometric
mechanism: split-shell capacity growth with delayed boundary thickening.
Extraction, flattening, and merge/leakage stay below ceiling, so the row
remains generative rather than extractive.

The claim remains GE3 only. GE4+, GE5+, GE6, final N28, agency, native support,
Phase 8 completion, and ant ecology remain blocked pending replay, controls,
stress, and closeout.
```

## Iteration 4-B - Primary Extractive Persistence Contrast Probe

- [x] Produce an extractive persistence contrast row.
- [x] Preserve focal basin stability.
- [x] Record neighbor capacity degradation or boundary weakening.
- [x] Record extraction, flattening, merge, or leakage as the degrading mechanism.
- [x] Set `regime_label = extractive`.
- [x] Set `regime_evidence_role = measured_contrast`.
- [x] Confirm the row is not promoted to generative evidence.
- [x] Preserve N20/N27 source boundaries.
- [x] Confirm thresholds are not retuned to force extractive classification.

Result:

```text
status = passed
acceptance_state = accepted_primary_extractive_ge3_measured_contrast_pending_replay_controls
output_digest = 15bd062bd8e6f1b637477c4412ca5f8913506353cf8404729ad0050167b60882
source_i4_primary_output_digest = daa25e4694929b11af38d7b044f4b4f5a4e70f6c2fbcae954db6a84854c08e5d
source_i4a_strengthening_output_digest = 07f15756b0584cbc91e4b765e4e96a07de0e62a772e0b0a49f1723f83d68b85c
provisional_ge_ladder_rung = GE3
n28_closeout_ceiling = N28-C4_source_current_generative_candidate_supported
shared_regime_policy_status = partially_supported
shared_regime_policy_status_scope = generative_primary_and_strengthening_plus_primary_extractive_contrast_pending_alternative_extractive_and_neutral_contrasts
primary_extractive_contrast_supported = true
positive_extractive_evidence_opened = true
extractive_contrast_promoted_to_generative = false
ge4_or_stronger_supported = false
ge5_or_stronger_supported = false
ge6_or_stronger_supported = false
final_generative_persistence_supported = false
final_n28_supported = false
ready_for_iteration_4c_alternative_extractive_contrast = true
```

Artifacts:

```text
outputs/n28_primary_extractive_contrast_probe.json
reports/n28_primary_extractive_contrast_probe.md
scripts/build_n28_primary_extractive_contrast_probe.py
outputs/n28_primary_extractive_contrast_probe_artifacts/threshold_policy_trace.json
outputs/n28_primary_extractive_contrast_probe_artifacts/source_current_runtime_trace.json
outputs/n28_primary_extractive_contrast_probe_artifacts/focal_basin_stability_trace.json
outputs/n28_primary_extractive_contrast_probe_artifacts/neighbor_capacity_trace.json
outputs/n28_primary_extractive_contrast_probe_artifacts/extraction_leakage_trace.json
outputs/n28_primary_extractive_contrast_probe_artifacts/capacity_attribution_trace.json
outputs/n28_primary_extractive_contrast_probe_artifacts/classification_trace.json
outputs/n28_primary_extractive_contrast_probe_artifacts/generative_extractive_core.json
```

Key metric record:

```text
focal_stability_preserved = true
neighbor_distinguishability_delta = -0.077
neighbor_support_delta = -0.063
neighbor_boundary_delta = -0.081
environment_capacity_delta = -0.069
focal_extraction_cost = 0.046
focal_extraction_cost_ceiling = 0.035
extractive_flattening_score = 0.041
extractive_flattening_ceiling = 0.03
merge_leakage_score = 0.033
merge_leakage_ceiling = 0.025
```

Interpretation:

```text
I4-B is the first measured extractive contrast against the I4/I4-A generative
pattern. The focal gamma basin remains above support/coherence/stability
floors, but the adjacent gamma shell loses distinguishability, support,
boundary integrity, and basin-forming capacity. The focal basin persists by
drawing down or flattening neighboring geometry rather than co-preserving it.

The geometric difference is the direction of capacity change around a stable
focal basin. In the generative cases, I4 and I4-A, the focal basin stays stable
while the neighbor shell becomes more basin-capable and
extraction/flattening/merge-leakage stay low. Nearby geometry gains
distinguishability, support, boundary integrity, and basin-forming capacity.
In the extractive case, I4-B, the focal basin also stays stable, but the
neighbor shell becomes less basin-capable while extraction, flattening, and
merge/leakage rise above generative ceilings. The focal basin's persistence is
therefore coupled to neighbor capacity loss.

Compactly:

Generative = focal persistence with neighbor capacity gain.
Extractive = focal persistence with neighbor capacity loss.

Topology-wise, this is not a failed I4-A and not a new-basin birth row. It is a
third local basin/shell configuration where focal continuation is coupled to
neighbor capacity degradation. The row is valid contrast evidence only because
it is classified as extractive and not promoted to generative support.

The row keeps I2-required `generative_classification_*` fields for schema
compatibility, but also records `regime_classification_*` aliases because I4-B
is an extractive measured contrast, not a generative candidate.
```

## Iteration 4-C - Extractive Strengthening Contrast Probe

- [x] Produce a second extractive contrast row under a distinct degradation mechanism or neighborhood variant whose purpose is to strengthen I4-B.
- [x] Preserve focal basin stability.
- [x] Record neighbor capacity degradation or boundary weakening.
- [x] Record extraction, flattening, merge, or leakage as the degrading mechanism.
- [x] Compare I4-C margins directly against I4-B on focal stability, neighbor distinguishability loss, neighbor support loss, neighbor boundary loss, environment capacity loss, extraction cost, flattening, and merge/leakage.
- [x] Classify the row as corroborating I4-B only if it preserves comparable or stronger extractive margins without weakening thresholds.
- [x] Confirm the row is not a relabeled copy of I4-B.
- [x] Confirm the row strengthens I4-B but does not replace I4-B.
- [x] Confirm the row does not import or relabel the primary I4-B outcome.
- [x] Set `regime_label = extractive`.
- [x] Set `regime_evidence_role = measured_contrast_alternative`.
- [x] Confirm the row is not promoted to generative evidence.
- [x] Preserve N20/N27 source boundaries.
- [x] Confirm thresholds are not retuned to force extractive classification.

Result:

```text
status = passed
acceptance_state = accepted_extractive_strengthening_ge3_measured_contrast_pending_replay_controls
output_digest = 013286de4bfa88838412d757a47c76b09f6f98381f71bddfa21cd1f5f70ba9d6
row_digest = 756d226e16cbf51696ef67a615a312fdb548102acefd7672f3905ae8f7d2fc8d
source_i4b_output_digest = 5015b7f5a148db75c7513b8fa8f249d1ac1fb0fc5fe4c6150d28d4ae644f84d3
provisional_ge_ladder_rung = GE3
regime_label = extractive
regime_evidence_role = measured_contrast_alternative
extractive_strengthening_contrast_supported = true
i4b_strengthened_not_replaced = true
extractive_contrast_promoted_to_generative = false
ge4_or_stronger_supported = false
ready_for_iteration_4d_primary_competitive_neutral_contrast = true
failed_checks = []
```

Artifacts:

```text
outputs/n28_extractive_strengthening_contrast_probe.json
reports/n28_extractive_strengthening_contrast_probe.md
scripts/build_n28_extractive_strengthening_contrast_probe.py
outputs/n28_extractive_strengthening_contrast_probe_artifacts/threshold_policy_trace.json
outputs/n28_extractive_strengthening_contrast_probe_artifacts/source_current_runtime_trace.json
outputs/n28_extractive_strengthening_contrast_probe_artifacts/focal_basin_stability_trace.json
outputs/n28_extractive_strengthening_contrast_probe_artifacts/neighbor_capacity_trace.json
outputs/n28_extractive_strengthening_contrast_probe_artifacts/extraction_leakage_trace.json
outputs/n28_extractive_strengthening_contrast_probe_artifacts/capacity_attribution_trace.json
outputs/n28_extractive_strengthening_contrast_probe_artifacts/classification_trace.json
outputs/n28_extractive_strengthening_contrast_probe_artifacts/generative_extractive_core.json
```

I4-B comparison:

```text
all_load_bearing_extractive_margins_comparable_or_stronger = true
thresholds_widened_relative_to_i4b = false
i4b_imported_as_evidence = false
i4b_replaced = false

focal_stability: I4-B 0.873 -> I4-C 0.878
neighbor_distinguishability_loss: I4-B -0.077 -> I4-C -0.086
neighbor_support_loss: I4-B -0.063 -> I4-C -0.070
neighbor_boundary_loss: I4-B -0.081 -> I4-C -0.090
environment_capacity_loss: I4-B -0.069 -> I4-C -0.078
focal_extraction_cost: I4-B 0.046 -> I4-C 0.049
extractive_flattening: I4-B 0.041 -> I4-C 0.044
merge_leakage: I4-B 0.033 -> I4-C 0.036
```

Interpretation:

```text
I4-C strengthens I4-B by repeating the extractive predicate in a distinct
delta focal/shell configuration. The focal basin remains above support,
coherence, and stability floors, while the neighboring shell loses
distinguishability, support, boundary integrity, and basin-forming capacity
with comparable or stronger extractive margins than I4-B.

Geometrically, I4-B used a gamma local shell drain. I4-C uses a delta
cross-shell drain. In both cases the focal basin persists, but persistence is
coupled to neighbor capacity loss rather than neighbor capacity gain. I4-C
therefore corroborates I4-B as extractive regime evidence; it does not replace
I4-B, import I4-B as evidence, widen thresholds, or promote extractive behavior
to generative support.

The claim remains GE3 only. GE4+, GE5+, GE6, final N28, agency, native support,
Phase 8 completion, and ant ecology remain blocked pending replay, controls,
stress, and closeout.
```

## Iteration 4-C2 - Extractive Mechanism-Diversity Probe

- [x] Produce an extractive contrast through a different degradation mechanism, not a margin-optimized copy of I4-B or I4-C.
- [x] Preserve focal basin stability.
- [x] Record neighbor capacity loss through merge/leakage-dominant boundary flattening.
- [x] Confirm the mechanism differs from the I4-B local shell drain and I4-C cross-shell directional drain.
- [x] Confirm the same frozen policy family is preserved.
- [x] Confirm source-current traces support focal persistence and neighbor capacity loss.
- [x] Confirm extraction, flattening, merge, and leakage expose the degrading mechanism.
- [x] Confirm thresholds are not retuned.
- [x] Confirm mechanism diversity is not inferred from labels alone.
- [x] Keep result provisional pending replay/control validation.

Result:

```text
status = passed
acceptance_state = accepted_extractive_mechanism_diversity_ge3_measured_contrast_pending_replay_controls
output_digest = cd099229fa37dcdf1c497555fd6ace7d4435035c87e58c1eec9bac6acb7e7067
row_digest = 653698de931037e832c2964766eef7644a78505f2775f15ddbe79e6adbf95204
source_i4b_primary_extractive_output_digest = 5015b7f5a148db75c7513b8fa8f249d1ac1fb0fc5fe4c6150d28d4ae644f84d3
source_i4c_strengthening_extractive_output_digest = 013286de4bfa88838412d757a47c76b09f6f98381f71bddfa21cd1f5f70ba9d6
provisional_ge_ladder_rung = GE3
regime_label = extractive
regime_evidence_role = measured_contrast_alternative
mechanism_class = merge_leakage_dominant_boundary_flattening
extractive_mechanism_diversity_supported = true
ge4_or_stronger_supported = false
failed_checks = []
```

Artifacts:

```text
outputs/n28_extractive_mechanism_diversity_probe.json
reports/n28_extractive_mechanism_diversity_probe.md
scripts/build_n28_extractive_mechanism_diversity_probe.py
outputs/n28_extractive_mechanism_diversity_probe_artifacts/threshold_policy_trace.json
outputs/n28_extractive_mechanism_diversity_probe_artifacts/source_current_runtime_trace.json
outputs/n28_extractive_mechanism_diversity_probe_artifacts/focal_basin_stability_trace.json
outputs/n28_extractive_mechanism_diversity_probe_artifacts/neighbor_capacity_trace.json
outputs/n28_extractive_mechanism_diversity_probe_artifacts/extraction_leakage_trace.json
outputs/n28_extractive_mechanism_diversity_probe_artifacts/capacity_attribution_trace.json
outputs/n28_extractive_mechanism_diversity_probe_artifacts/classification_trace.json
outputs/n28_extractive_mechanism_diversity_probe_artifacts/generative_extractive_core.json
```

Interpretation:

```text
I4-C2 strengthens the extractive side by mechanism diversity rather than margin
optimization. I4-B is the gamma local-shell drain and I4-C is the delta
cross-shell directional drain. I4-C2 is the zeta boundary-flattening case:
focal persistence remains viable while neighboring distinguishability, support,
boundary integrity, and basin-forming capacity degrade as merge/leakage and
flattening rise above generative ceilings.

The important point is not that every extractive value is larger than I4-B or
I4-C. The point is that the same frozen classifier accepts a different
source-current degradation mechanism: merge/leakage-dominant boundary
flattening. The row is extractive because focal persistence is coupled to
neighbor capacity loss, not because of a relabeled or imported prior result.

The claim remains GE3 only. GE4+, GE5+, GE6, final N28, agency, native support,
Phase 8 completion, and ant ecology remain blocked pending replay, controls,
stress, and closeout.
```

## Iteration 4-D - Primary Competitive / Neutral Persistence Contrast Probe

- [x] Produce a competitive or neutral persistence contrast row.
- [x] Preserve focal basin stability.
- [x] Record neighborhood capacity as unchanged, mixed, or competitively redistributed.
- [x] Set `regime_label = competitive` or `neutral`.
- [x] Set `regime_evidence_role = measured_contrast`.
- [x] Confirm the row is not promoted to generative evidence.
- [x] Preserve N20/N27 source boundaries.
- [x] Confirm variant is not threshold retuning.
- [x] Record whether result sharpens the paired generative/extractive/competitive regime boundary.

Result:

```text
status = passed
acceptance_state = accepted_primary_competitive_neutral_ge3_measured_contrast_pending_replay_controls
output_digest = f124a1afe8aff1a54a44157290e053d748e5545e1a9afcff1d1accbebef6c173
row_digest = a3f9a912682c099a7be25d69041a22a59494dba15ae1dc4f993bd19a780e2ffa
provisional_ge_ladder_rung = GE3
regime_label = competitive
regime_evidence_role = measured_contrast
primary_competitive_neutral_contrast_supported = true
competitive_neutral_promoted_to_generative = false
competitive_neutral_promoted_to_extractive = false
ge4_or_stronger_supported = false
ready_for_iteration_4e_alternative_competitive_neutral_contrast = true
failed_checks = []
```

Artifacts:

```text
outputs/n28_primary_competitive_neutral_contrast_probe.json
reports/n28_primary_competitive_neutral_contrast_probe.md
scripts/build_n28_primary_competitive_neutral_contrast_probe.py
outputs/n28_primary_competitive_neutral_contrast_probe_artifacts/threshold_policy_trace.json
outputs/n28_primary_competitive_neutral_contrast_probe_artifacts/source_current_runtime_trace.json
outputs/n28_primary_competitive_neutral_contrast_probe_artifacts/focal_basin_stability_trace.json
outputs/n28_primary_competitive_neutral_contrast_probe_artifacts/neighbor_capacity_trace.json
outputs/n28_primary_competitive_neutral_contrast_probe_artifacts/extraction_leakage_trace.json
outputs/n28_primary_competitive_neutral_contrast_probe_artifacts/capacity_attribution_trace.json
outputs/n28_primary_competitive_neutral_contrast_probe_artifacts/classification_trace.json
outputs/n28_primary_competitive_neutral_contrast_probe_artifacts/generative_extractive_core.json
```

Competitive / neutral boundary:

```text
neighbor_distinguishability_delta = 0.018
neighbor_support_delta = 0.006
neighbor_boundary_delta = -0.012
environment_capacity_delta = 0.004
route_lobe_a_capacity_delta = 0.055
route_lobe_b_capacity_delta = -0.050
focal_extraction_cost = 0.028
extractive_flattening = 0.024
merge_leakage = 0.019

aggregate_neighbor_capacity_not_materially_generative = true
aggregate_neighbor_capacity_not_materially_extractive = true
competitive_redistribution_detected = true
```

Interpretation:

```text
I4-D adds the first competitive/neutral source-current contrast. The focal eta
basin remains above support, coherence, and stability floors, but the
neighboring field is not broadly enriched and not broadly depleted. Capacity is
redistributed: one neighbor lobe gains while another loses, and aggregate
neighbor capacity remains below the material generative and extractive
thresholds.

Geometrically, this fills the middle regime between I4/I4-A/I4-A2 enrichment
and I4-B/I4-C/I4-C2 depletion. It is focal persistence with mixed
environmental exchange. Extraction, flattening, and merge/leakage stay below
extractive ceilings, so the row is not extractive. Aggregate neighbor capacity
does not reach the generative gain thresholds, so the row is not generative.

In that sense I4-D can be read as a bounded processing or changing regime. The
focal basin does not simply enrich its surroundings or deplete them. It
reshapes the local capacity field: one adjacent region is thinned, reduced, or
competitively drained while another adjacent region is strengthened. The result
is environmental redistribution around a persisting basin, not net
basin-forming enrichment and not broad extractive collapse.

The claim remains GE3 only. GE4+, GE5+, GE6, final N28, agency, native support,
Phase 8 completion, and ant ecology remain blocked pending replay, controls,
stress, and closeout.
```

## Iteration 4-E - Competitive / Neutral Mechanism-Diversity Probe

- [x] Produce a second competitive or neutral persistence contrast under a distinct setup.
- [x] Preserve focal basin stability.
- [x] Record neighborhood capacity as unchanged, mixed, or competitively redistributed.
- [x] Confirm the row is not a relabeled copy of I4-D.
- [x] Confirm the row is a mechanism-diversity row rather than a margin-optimized copy of I4-D.
- [x] Set `regime_label = competitive` or `neutral`.
- [x] Set `regime_evidence_role = measured_contrast_alternative`.
- [x] Confirm the row is not promoted to generative evidence.
- [x] Preserve N20/N27 source boundaries.
- [x] Confirm variant is not threshold retuning.
- [x] Record whether result sharpens the paired-regime boundary.

Result:

```text
status = passed
acceptance_state = accepted_competitive_neutral_mechanism_diversity_ge3_measured_contrast_pending_replay_controls
output_digest = d760e55481c2d84e554c5089863c725c3b57ee7da1dedbf5b919f201c3c754cd
row_digest = 1d59626e0765e15b3e29f39e089b848c21ee15e5fa7a442b49413c01389ecfdc
provisional_ge_ladder_rung = GE3
regime_label = neutral
regime_evidence_role = measured_contrast_alternative
mechanism_class = three_lobe_circulatory_capacity_exchange
competitive_neutral_mechanism_diversity_supported = true
i4e_mechanism_diversity_supported = true
competitive_neutral_promoted_to_generative = false
competitive_neutral_promoted_to_extractive = false
ge4_or_stronger_supported = false
ready_for_iteration_5_replay_and_capacity_attribution_matrix = true
failed_checks = []
```

Artifacts:

```text
outputs/n28_competitive_neutral_mechanism_diversity_probe.json
reports/n28_competitive_neutral_mechanism_diversity_probe.md
scripts/build_n28_competitive_neutral_mechanism_diversity_probe.py
outputs/n28_competitive_neutral_mechanism_diversity_probe_artifacts/threshold_policy_trace.json
outputs/n28_competitive_neutral_mechanism_diversity_probe_artifacts/source_current_runtime_trace.json
outputs/n28_competitive_neutral_mechanism_diversity_probe_artifacts/focal_basin_stability_trace.json
outputs/n28_competitive_neutral_mechanism_diversity_probe_artifacts/neighbor_capacity_trace.json
outputs/n28_competitive_neutral_mechanism_diversity_probe_artifacts/extraction_leakage_trace.json
outputs/n28_competitive_neutral_mechanism_diversity_probe_artifacts/capacity_attribution_trace.json
outputs/n28_competitive_neutral_mechanism_diversity_probe_artifacts/classification_trace.json
outputs/n28_competitive_neutral_mechanism_diversity_probe_artifacts/generative_extractive_core.json
```

Neutral circulation boundary:

```text
neighbor_distinguishability_delta = 0.008
neighbor_support_delta = -0.006
neighbor_boundary_delta = 0.007
environment_capacity_delta = -0.002
inflow_lobe_capacity_delta = 0.047
outflow_lobe_capacity_delta = -0.045
buffer_lobe_capacity_delta = 0.002
focal_extraction_cost = 0.027
extractive_flattening = 0.023
merge_leakage = 0.020

aggregate_neighbor_capacity_not_materially_generative = true
aggregate_neighbor_capacity_not_materially_extractive = true
neutral_circulation_detected = true
direct_two_lobe_competitive_pair_used = false
```

Interpretation:

```text
I4-E strengthens the competitive/neutral side by mechanism diversity rather
than by tuning I4-D. I4-D showed direct two-lobe competitive redistribution:
one lobe gained while another lobe lost. I4-E instead shows neutral
three-lobe circulation: an inflow lobe gains, an outflow lobe loses, and a
buffer lobe remains near stable while aggregate neighbor capacity remains
near-neutral.

Geometrically, the focal theta basin remains above support, coherence, and
stability floors. The surrounding theta shell is not broadly enriched and not
broadly depleted. Instead, the local capacity field is processed through a
circulatory exchange. One adjacent region is strengthened, one is reduced, and
one buffers the exchange.

This is a middle-regime processing row, not generative enrichment and not
extractive collapse. It consumes I4/I4-A/I4-A2, I4-B/I4-C/I4-C2, and I4-D only
as regime-boundary context. It does not import those outcomes as evidence,
replace them, widen thresholds, or promote neutral circulation to generative
support.

The claim remains GE3 only. GE4+, GE5+, GE6, final N28, agency, native support,
Phase 8 completion, and ant ecology remain blocked pending replay, controls,
stress, and closeout.
```

## Iteration 5 - Replay And Capacity Attribution Matrix

- [ ] Run artifact replay.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay.
- [ ] Run capacity-attribution controls.
- [ ] Run merge/leakage controls.
- [ ] Run focal-survival-only controls.
- [ ] Replay I4 through I4-E paired-regime rows, including I4-A2 and I4-C2.
- [ ] Test whether replayed rows can still use one shared policy family.
- [ ] Record `shared_regime_policy_status` or a provisional policy-divergence blocker.
- [ ] Confirm all generative candidates, including mechanism-diverse rows, remain generative or are demoted explicitly.
- [ ] Confirm all extractive contrasts, including mechanism-diverse rows, remain extractive or are demoted explicitly.
- [ ] Confirm both competitive/neutral contrasts remain non-generative or are demoted explicitly.
- [ ] Confirm regime labels remain stable under replay or are demoted explicitly.
- [ ] Confirm extractive/competitive rows remain valid contrasts, not failed rows, unless promoted incorrectly.
- [ ] Record per-row demotions or blockers.

## Iteration 5-A - Artifact-Only Reconstruction Replay Probe

- [ ] Test whether N28 classification can be reconstructed from reports alone.
- [ ] Test whether N27 transfer success alone can recreate the N28 claim.
- [ ] Require source-current N28 traces for positive support.

## Iteration 6 - Stress / Regime-Separation Matrix

- [ ] Stress focal stability.
- [ ] Stress neighbor capacity.
- [ ] Stress extraction cost.
- [ ] Stress merge/leakage.
- [ ] Stress boundary integrity.
- [ ] Stress I4 through I4-E paired-regime rows, including I4-A2 and I4-C2, under the same policy family first.
- [ ] If the same policy family fails, record split-policy evidence rather than retuning thresholds.
- [ ] Confirm generative rows do not collapse into focal-survival-only rows.
- [ ] Confirm extractive rows are not hidden by focal stability.
- [ ] Preserve thresholds and policy declared before use.

## Iteration 6-A - Regime Boundary / Transition Matrix

- [ ] Vary stress or capacity envelope across declared settings.
- [ ] Record where rows remain generative.
- [ ] Record where rows become competitive or neutral.
- [ ] Record where rows become extractive.
- [ ] Confirm transition points are source-current and not post-hoc threshold choices.
- [ ] Decide provisional `shared_regime_policy_status`.
- [ ] Confirm any policy divergence is declared, source-current, and replay/control clean.
- [ ] Confirm regime boundary remains replay/control clean when shared policy is supported.

## Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification

- [ ] Classify all positive, partial, rejected, blocked, and contrast rows.
- [ ] Confirm primary and strengthening generative candidates are represented, or record blocker.
- [ ] Confirm primary and strengthening extractive contrasts are represented, or record blocker.
- [ ] Confirm primary and alternative competitive/neutral contrasts are represented, or record blocker.
- [ ] Classify `shared_regime_policy_status`.
- [ ] Confirm label-specific thresholds are either absent or recorded as split-policy blockers.
- [ ] Confirm competitive/neutral rows are not promoted to generative evidence.
- [ ] Confirm AP4/AP5 dependencies are row-local.
- [ ] Confirm N27 context is not promoted to N28 evidence.
- [ ] Confirm unsafe claim flags remain false.
- [ ] Confirm no ant ecology implementation opens.

## Iteration 8 - Closeout And N29 Handoff

- [ ] Freeze final GE rung if warranted.
- [ ] Freeze final N28-C rung if warranted.
- [ ] Confirm closeout does not rely on a single generative-looking row.
- [ ] Confirm GE5/N28-C5 require paired generative, extractive, and competitive/neutral regime separation unless explicit blockers are recorded.
- [ ] Record whether same-rule classification is supported, partially supported, split-policy-required, or blocked.
- [ ] Record final claim ceiling.
- [ ] Record final controls and blockers.
- [ ] Confirm source digests and artifact hashes.
- [ ] Confirm no absolute paths.
- [ ] Confirm `src_diff_empty` unless an explicit implementation defect is only recorded, not fixed.
- [ ] Record N29 handoff.

Expected closeout ceiling:

```text
bounded artifact-level generative/extractive persistence candidate
```

Blocked at closeout unless separately supported:

```text
semantic cooperation
semantic choice
agency
native support
sentience
organism/life
ant ecology implementation
native ant agency
native colony agency
Phase 8 completion
native AP5
AP5 NAT4 gap resolution
```
