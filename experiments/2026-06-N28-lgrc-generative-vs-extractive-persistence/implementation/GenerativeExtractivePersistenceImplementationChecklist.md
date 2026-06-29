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

- [x] Run artifact replay.
- [x] Run snapshot/load replay.
- [x] Run duplicate replay.
- [x] Run capacity-attribution controls.
- [x] Run merge/leakage controls.
- [x] Run focal-survival-only controls.
- [x] Replay I4 through I4-E paired-regime rows, including I4-A2 and I4-C2.
- [x] Test whether replayed rows can still use one shared policy family.
- [x] Record `shared_regime_policy_status` or a provisional policy-divergence blocker.
- [x] Confirm all generative candidates, including mechanism-diverse rows, remain generative or are demoted explicitly.
- [x] Confirm all extractive contrasts, including mechanism-diverse rows, remain extractive or are demoted explicitly.
- [x] Confirm both competitive/neutral contrasts remain non-generative or are demoted explicitly.
- [x] Confirm regime labels remain stable under replay or are demoted explicitly.
- [x] Confirm extractive/competitive rows remain valid contrasts, not failed rows, unless promoted incorrectly.
- [x] Record per-row demotions or blockers.

Result:

```text
status = passed
acceptance_state = accepted_replay_control_backed_ge4_regime_separation_candidate_pending_stress
output_digest = 3fd8875fa01e4cbb91933bc89cf2db32a1a2d8396a6ebc16451c33a008af6caa
provisional_ge_ladder_rung = GE4
ge4_or_stronger_supported = true
ge5_or_stronger_supported = false
ge6_or_stronger_supported = false
shared_regime_policy_status = replay_control_backed_pending_stress
source_row_count = 8
rows_demoted = []
failed_checks = []
```

Artifacts:

```text
outputs/n28_replay_capacity_attribution_matrix.json
reports/n28_replay_capacity_attribution_matrix.md
scripts/build_n28_replay_capacity_attribution_matrix.py
outputs/n28_replay_capacity_attribution_matrix_artifacts/matrix_summary_trace.json
outputs/n28_replay_capacity_attribution_matrix_artifacts/n28_i5_replay_n28_i4_row_primary_generative_candidate_trace.json
outputs/n28_replay_capacity_attribution_matrix_artifacts/n28_i5_replay_n28_i4a_row_generative_strengthening_candidate_trace.json
outputs/n28_replay_capacity_attribution_matrix_artifacts/n28_i5_replay_n28_i4a2_row_generative_mechanism_diversity_candidate_trace.json
outputs/n28_replay_capacity_attribution_matrix_artifacts/n28_i5_replay_n28_i4b_row_primary_extractive_contrast_trace.json
outputs/n28_replay_capacity_attribution_matrix_artifacts/n28_i5_replay_n28_i4c_row_extractive_strengthening_contrast_trace.json
outputs/n28_replay_capacity_attribution_matrix_artifacts/n28_i5_replay_n28_i4c2_row_extractive_mechanism_diversity_contrast_trace.json
outputs/n28_replay_capacity_attribution_matrix_artifacts/n28_i5_replay_n28_i4d_row_primary_competitive_neutral_contrast_trace.json
outputs/n28_replay_capacity_attribution_matrix_artifacts/n28_i5_replay_n28_i4e_row_competitive_neutral_mechanism_diversity_contrast_trace.json
```

Replay matrix:

```text
I4   generative  -> generative  artifact/snapshot/duplicate = passed/passed/passed  final = GE4
I4-A generative  -> generative  artifact/snapshot/duplicate = passed/passed/passed  final = GE4
I4-A2 generative -> generative  artifact/snapshot/duplicate = passed/passed/passed  final = GE4
I4-B extractive  -> extractive  artifact/snapshot/duplicate = passed/passed/passed  final = GE4
I4-C extractive  -> extractive  artifact/snapshot/duplicate = passed/passed/passed  final = GE4
I4-C2 extractive -> extractive  artifact/snapshot/duplicate = passed/passed/passed  final = GE4
I4-D competitive -> competitive artifact/snapshot/duplicate = passed/passed/passed  final = GE4
I4-E neutral     -> neutral     artifact/snapshot/duplicate = passed/passed/passed  final = GE4
```

Interpretation:

```text
I5 upgrades the I4-family evidence from provisional GE3 source-current regime
rows to a replay/control-backed GE4 regime-separation candidate. The upgrade
is matrix-level: all three generative rows, all three extractive rows, and both
competitive/neutral rows replay with stable regime labels and pass
capacity-attribution, merge/leakage, and focal-survival-only controls.

The shared policy family survives replay/control validation:

shared_policy_ids = [n28_shared_regime_policy_v1]
single_shared_policy_family_preserved = true

This is still not GE5 or GE6. I6 must stress the same regime boundaries before
N28 can claim stress/variant-backed paired-regime separation. I7 and I8 still
need AP/claim classification and closeout.

Duplicate replay uses the standard convention from earlier experiments:
first_emitted = true and second_emitted = false means the second replay
suppressed a duplicate while preserving the same digest. This is a pass, not a
failed second replay.
```

## Iteration 5-A - Artifact-Only Reconstruction Replay Probe

- [x] Test whether N28 classification can be reconstructed from reports alone.
- [x] Test whether N27 transfer success alone can recreate the N28 claim.
- [x] Require source-current N28 traces for positive support.

Result:

```text
status = passed
acceptance_state = accepted_artifact_only_reconstruction_controls_fail_closed_no_new_ge_support
output_digest = c88d2605b60f272ab4fd50bc062c09ab5059f26bf236e7339309196f47863646
provisional_ge_ladder_rung = GE4
i5_ge4_result_preserved = true
i5a_new_ge_support_opened = false
ge5_or_stronger_supported = false
control_row_count = 5
failed_closed_row_count = 5
failed_open_row_count = 0
positive_support_allowed_rows = []
failed_checks = []
```

Artifacts:

```text
outputs/n28_artifact_only_reconstruction_replay_probe.json
reports/n28_artifact_only_reconstruction_replay_probe.md
scripts/build_n28_artifact_only_reconstruction_replay_probe.py
outputs/n28_artifact_only_reconstruction_replay_probe_artifacts/artifact_only_reconstruction_summary.json
outputs/n28_artifact_only_reconstruction_replay_probe_artifacts/n28_i5a_report_only_reconstruction_control_reconstruction_trace.json
outputs/n28_artifact_only_reconstruction_replay_probe_artifacts/n28_i5a_label_only_regime_reconstruction_control_reconstruction_trace.json
outputs/n28_artifact_only_reconstruction_replay_probe_artifacts/n28_i5a_n27_transfer_only_reconstruction_control_reconstruction_trace.json
outputs/n28_artifact_only_reconstruction_replay_probe_artifacts/n28_i5a_digest_only_reconstruction_control_reconstruction_trace.json
outputs/n28_artifact_only_reconstruction_replay_probe_artifacts/n28_i5a_matrix_summary_only_reconstruction_control_reconstruction_trace.json
```

Control rows:

```text
report_only_summary -> rejected / failed_closed
regime_labels_and_counts_only -> rejected / failed_closed
n27_transfer_context_only -> rejected / failed_closed
digest_and_hashes_only -> rejected / failed_closed
i5_matrix_summary_only -> rejected / failed_closed
```

Interpretation:

```text
I5-A does not add positive GE support. It protects the I5 result by showing
that reports, labels, N27 transfer context, digests/hashes, and I5 matrix
summaries cannot replace source-current N28 traces and per-row replay controls.

It does this by turning each possible shortcut into an explicit negative
control row. Each row is allowed to carry the shortcut surface it is testing,
but it is forced to record:

source_current_inputs = []
source_current_n28_trace_required = true
source_current_n28_trace_available = false
regime_metrics_reconstructable = false
ge_ladder_rung = GE0
ge4_support_allowed = false
row_decision = rejected
control_status = failed_closed

The report-only row has report text but lacks source-current runtime traces,
neighbor-capacity traces, extraction/leakage traces, classification traces,
and the generative/extractive core. The label/count row has regime labels and
counts but lacks focal stability, neighbor capacity delta, merge/leakage, and
capacity-attribution traces. The N27-only row has transfer-context digests but
lacks N28 regime rows, N28 replay rows, and N28 capacity-attribution traces.
The digest-only row has provenance hashes but lacks loaded trace payloads,
metric sign checks, and regime-specific attribution controls. The I5-summary
row has the matrix summary but lacks per-row source-current traces, per-row
replay traces, and per-row control results.

All five rows therefore fail closed:

control_row_count = 5
failed_closed_row_count = 5
failed_open_row_count = 0
positive_support_allowed_rows = []
source_current_n28_trace_missing_blocks_support = true

The GE4 candidate remains sourced to I5. I5-A only confirms that insufficient
reconstruction surfaces fail closed. GE5, GE6, final N28, semantic
cooperation, agency, native support, Phase 8 completion, and ant ecology remain
blocked pending stress, claim classification, and closeout.
```

## Iteration 6 - Stress / Regime-Separation Matrix

- [x] Stress focal stability.
- [x] Stress neighbor capacity.
- [x] Stress extraction cost.
- [x] Stress merge/leakage.
- [x] Stress boundary integrity.
- [x] Stress I4 through I4-E paired-regime rows, including I4-A2 and I4-C2, under the same policy family first.
- [x] If the same policy family fails, record split-policy evidence rather than retuning thresholds.
- [x] Confirm generative rows do not collapse into focal-survival-only rows.
- [x] Confirm extractive rows are not hidden by focal stability.
- [x] Preserve thresholds and policy declared before use.

Result:

```text
status = passed
acceptance_state = accepted_stress_variant_backed_ge5_regime_separation_candidate_pending_claim_classification
output_digest = fe051d860391bdbceddc2892abd49dc117b8a5797b3802d77609b1578e1ad756
provisional_ge_ladder_rung = GE5
ge4_or_stronger_supported = true
ge5_or_stronger_supported = true
ge6_or_stronger_supported = false
shared_regime_policy_status = supported
stress_variant_count = 5
stress_row_count = 40
stress_passed_row_count = 40
stress_failed_row_count = 0
rows_demoted = []
failed_checks = []
ready_for_iteration_7_claim_classification = true
```

Artifacts:

```text
outputs/n28_stress_regime_separation_matrix.json
reports/n28_stress_regime_separation_matrix.md
scripts/build_n28_stress_regime_separation_matrix.py
outputs/n28_stress_regime_separation_matrix_artifacts/stress_regime_separation_summary.json
outputs/n28_stress_regime_separation_matrix_artifacts/n28_i6_*_trace.json
```

Stress axes:

```text
focal_stability_softening -> 8 / 8 passed, minimum margin = 0.003
neighbor_capacity_compression -> 8 / 8 passed, minimum margin = 0.003
extraction_cost_pressure -> 8 / 8 passed, minimum margin = 0.002
merge_leakage_pressure -> 8 / 8 passed, minimum margin = 0.002
boundary_integrity_compression -> 8 / 8 passed, minimum margin = 0.001
```

Regime coverage:

```text
generative = 15 / 15 stress rows passed, minimum margin = 0.010
extractive = 15 / 15 stress rows passed, minimum margin = 0.003
competitive = 5 / 5 stress rows passed, minimum margin = 0.002
neutral = 5 / 5 stress rows passed, minimum margin = 0.001
```

Interpretation:

```text
I6 upgrades I5 from replay/control-backed GE4 to a provisional GE5 candidate.
It does so by applying five declared stress overlays to every I4-family row
already admitted by I5: focal stability softening, neighbor-capacity
compression, extraction-cost pressure, merge/leakage pressure, and boundary
integrity compression.

The stress overlays do not retune thresholds, do not mutate source rows, and
preserve the same shared policy family:

shared_policy_ids = [n28_shared_regime_policy_v1]
thresholds_retuned_for_stress = false
source_rows_mutated = false

Geometrically, I6 compresses each regime's load-bearing axes while keeping the
same classification rules. Generative rows keep focal persistence while their
neighboring capacity shell remains enriched. Extractive rows keep focal
persistence while the neighborhood remains depleted/flattened and extraction
remains present. Competitive/neutral rows keep redistribution or circulation
without becoming aggregate enrichment or depletion.

The result is strong enough for GE5 because all paired regime families survive
bounded stress without demotion:

generative source rows = 3
extractive source rows = 3
competitive/neutral source rows = 2
stress rows passed = 40
stress rows failed = 0

The result is still not GE6 or final N28. Margins remain narrow in the weakest
neutral/boundary cases, with minimum stress margin 0.001. I7 must still classify
AP4/AP5 dependencies and unsafe claim boundaries, and I8 must still freeze
closeout and the N29 handoff.
```

## Iteration 6-A - Regime Boundary / Transition Matrix

- [x] Vary stress or capacity envelope across declared settings.
- [x] Record where rows remain generative.
- [x] Record where rows become competitive or neutral.
- [x] Record where rows become extractive.
- [x] Confirm transition points are source-current and not post-hoc threshold choices.
- [x] Decide provisional `shared_regime_policy_status`.
- [x] Confirm any policy divergence is declared, source-current, and replay/control clean.
- [x] Confirm regime boundary remains replay/control clean when shared policy is supported.

Result:

```text
status = passed
acceptance_state = accepted_regime_boundary_transition_matrix_same_policy_supported_no_new_ge_support
output_digest = e6b0afbf81873e519db458e611cc01a1c11b2e9b5c2dead899946b270077700d
i6_ge5_result_preserved = true
i6a_new_ge_support_opened = false
ge5_or_stronger_supported = true
ge6_or_stronger_supported = false
shared_regime_policy_status = supported
transition_row_count = 34
label_match_count = 34
label_mismatch_count = 0
ge5_boundary_preservation_row_count = 16
failed_checks = []
ready_for_iteration_7_claim_classification = true
```

Artifacts:

```text
outputs/n28_regime_boundary_transition_matrix.json
reports/n28_regime_boundary_transition_matrix.md
scripts/build_n28_regime_boundary_transition_matrix.py
outputs/n28_regime_boundary_transition_matrix_artifacts/regime_boundary_transition_summary.json
outputs/n28_regime_boundary_transition_matrix_artifacts/n28_i6a_*_trace.json
```

Transition roles:

```text
source_current_anchor = 8 / 8 matched
same_regime_boundary_edge = 8 / 8 matched
unclassified_gap_expected = 8 / 8 matched
opposite_regime_cross_check = 6 / 6 matched
aggregate_enrichment_cross_check = 2 / 2 matched
aggregate_depletion_cross_check = 2 / 2 matched
```

Observed label transitions:

```text
generative -> generative = 6
generative -> unclassified = 3
generative -> extractive = 3
extractive -> extractive = 6
extractive -> unclassified = 3
extractive -> generative = 3
competitive -> competitive = 2
competitive -> unclassified = 1
competitive -> generative = 1
competitive -> extractive = 1
neutral -> neutral = 2
neutral -> unclassified = 1
neutral -> generative = 1
neutral -> extractive = 1
```

Interpretation:

```text
I6-A preserves the I6 GE5 result and supports the same shared regime policy as
a boundary classifier. It does not add new source-current GE support. Instead,
it varies declared transition envelopes around the I4-family source anchors and
checks whether the same frozen policy classifies each transition surface as
expected.

Source anchors and same-regime boundary-edge rows preserve the GE5 policy
surface. Boundary-gap and cross-regime rows are controls. The key result is
that near-zero aggregate deltas alone do not become competitive or neutral:
when mixed-lobe or circulation evidence is removed, the row becomes
unclassified. When aggregate enrichment or depletion crosses the declared
thresholds, the same policy classifies it as generative or extractive.

This means the N28 classifier is not merely memorizing labels. It has a
traceable transition surface:

generative / extractive regimes require signed neighborhood-capacity and
extraction/leakage evidence;
competitive / neutral regimes require mixed-lobe or circulation evidence;
boundary gaps fail closed as unclassified.

GE6 and final N28 remain blocked pending I7 claim classification and I8
closeout. I6-A makes additional I5/I6 replay/stress rows optional rather than
required unless we want broader margins or more source-current variety.
```

## Iteration 6-B - Margin Envelope Sweep

- [x] Sweep I6 stress multipliers across all I4-family source rows.
- [x] Preserve the current I6 multiplier as an explicit checkpoint.
- [x] Record max passed multiplier and first failed multiplier per row/axis.
- [x] Identify critical current-margin bottlenecks.
- [x] Decide whether generic extra I5/I6 runs or targeted higher-margin rows are useful.
- [x] Confirm thresholds are not retuned and source rows are not mutated.
- [x] Confirm I6-B does not open new source-current GE support or GE6.

Result:

```text
status = passed
acceptance_state = accepted_margin_envelope_sweep_ge5_preserved_bottlenecks_identified
output_digest = f91f4cb675b39e0fa87f5ebfbbb842e52129d42c2fbe7d4586bbe2bcd54c5fab
i6_ge5_result_preserved = true
i6b_new_ge_support_opened = false
ge5_or_stronger_supported = true
ge6_or_stronger_supported = false
envelope_row_count = 40
current_i6_rows_preserved = 40
critical_current_margin_count = 3
narrow_current_margin_count = 9
failed_within_sweep_count = 7
failed_checks = []
ready_for_iteration_7_claim_classification = true
```

Artifacts:

```text
outputs/n28_margin_envelope_sweep.json
reports/n28_margin_envelope_sweep.md
scripts/build_n28_margin_envelope_sweep.py
outputs/n28_margin_envelope_sweep_artifacts/margin_envelope_sweep_summary.json
outputs/n28_margin_envelope_sweep_artifacts/n28_i6b_*_envelope.json
```

Critical bottlenecks:

```text
competitive / extraction_cost_pressure:
  limiting field = flattening_margin
  current margin = 0.002
  max passed multiplier = 1.5
  first failed multiplier = 2.0

neutral / merge_leakage_pressure:
  limiting field = merge_leakage_margin
  current margin = 0.002
  max passed multiplier = 1.5
  first failed multiplier = 2.0

neutral / boundary_integrity_compression:
  limiting field = outflow_lobe_margin
  current margin = 0.001
  max passed multiplier = 1.25
  first failed multiplier = 1.5
```

Recommendation:

```text
generic_more_i5_i6_runs_recommended = false
higher_margin_neutral_circulation_variant_recommended = true
higher_margin_competitive_redistribution_variant_recommended = true
higher_margin_generative_variant_recommended = false
higher_margin_extractive_variant_recommended = false
```

Interpretation:

```text
I6-B preserves the I6 GE5 result at the current stress multiplier and maps the
failure envelope around it. The current weak margins are not spread across the
whole paired-regime matrix. They are localized to competitive/neutral rows,
especially the neutral circulation row under boundary compression.

This means a generic extra replay/stress pass would mostly add volume, not new
agency-relevant structure. If N28 is strengthened further before I7, the useful
work is focused: add a higher-margin neutral circulation variant and, second,
a higher-margin competitive redistribution variant, then replay/stress those
specific rows. More generative or extractive variants are not indicated by the
current bottleneck map.

I6-B remains GE5 envelope characterization only. It does not add new
source-current GE support, does not solve GE6, and does not open final N28,
semantic cooperation, agency, native support, Phase 8 completion, or ant
ecology.
```

## Iteration 4-F - Higher-Margin Neutral Circulation Variant

- [x] Add the focused higher-margin neutral circulation row recommended by I6-B.
- [x] Preserve the same shared regime policy family and claim boundary.
- [x] Confirm I4-F does not replace I4-E.
- [x] Confirm the row remains neutral circulation, not generative or extractive.
- [x] Record improvement against the I6-B neutral circulation bottlenecks.
- [x] Keep GE4+ pending focused replay/control.

Result:

```text
status = passed
acceptance_state = accepted_higher_margin_neutral_circulation_ge3_candidate_pending_replay_stress
output_digest = 1848a9ffe8c4c0242ef2b670527b65bedbcd9ea5ae0c57a15a8208acf1ab0921
provisional_ge_ladder_rung = GE3
regime_label = neutral
regime_evidence_role = measured_contrast_margin_strengthening
higher_margin_neutral_circulation_supported = true
i4e_replaced = false
i6b_bottleneck_targeted = true
ge4_or_stronger_supported = false
ready_for_i5b_focused_replay = true
failed_checks = []
```

Artifacts:

```text
outputs/n28_higher_margin_neutral_circulation_probe.json
reports/n28_higher_margin_neutral_circulation_probe.md
scripts/build_n28_higher_margin_neutral_circulation_probe.py
outputs/n28_higher_margin_neutral_circulation_probe_artifacts/*.json
```

Focused margin comparison:

```text
i4e_outflow_margin = 0.005
i4f_outflow_margin = 0.020
i4e_merge_leakage_margin = 0.005
i4f_merge_leakage_margin = 0.010
i4f_inflow_margin = 0.022
i4f_flattening_margin = 0.010
```

Interpretation:

```text
I4-F is a focused answer to I6-B's neutral circulation bottleneck. It keeps
the same neutral/circulatory geometry as I4-E: the focal basin remains stable,
aggregate neighbor capacity remains near-neutral, and the surrounding field is
processed through inflow, outflow, and buffer lobes rather than broad
enrichment or depletion.

The strengthening is geometric margin, not a new label. The inflow/outflow
circulation pair has more room above the mixed-lobe floor, and merge/leakage is
further below ceiling. This targets the I6-B outflow-lobe and merge/leakage
bottlenecks while keeping the claim at GE3 pending focused replay and stress.
```

## Iteration 4-G - Higher-Margin Competitive Redistribution Variant

- [x] Add the focused higher-margin competitive redistribution row recommended by I6-B.
- [x] Preserve the same shared regime policy family and claim boundary.
- [x] Confirm I4-G does not replace I4-D.
- [x] Confirm the row remains competitive redistribution, not generative or extractive.
- [x] Record improvement against the I6-B competitive flattening bottleneck.
- [x] Keep GE4+ pending focused replay/control.

Result:

```text
status = passed
acceptance_state = accepted_higher_margin_competitive_redistribution_ge3_candidate_pending_replay_stress
output_digest = 8bc907a97b07c09c72fd7ceda63811555c335c0d45d6dbef6cfb29489f463e72
provisional_ge_ladder_rung = GE3
regime_label = competitive
regime_evidence_role = measured_contrast_margin_strengthening
higher_margin_competitive_redistribution_supported = true
i4d_replaced = false
i6b_bottleneck_targeted = true
ge4_or_stronger_supported = false
ready_for_i5b_focused_replay = true
failed_checks = []
```

Artifacts:

```text
outputs/n28_higher_margin_competitive_redistribution_probe.json
reports/n28_higher_margin_competitive_redistribution_probe.md
scripts/build_n28_higher_margin_competitive_redistribution_probe.py
outputs/n28_higher_margin_competitive_redistribution_probe_artifacts/*.json
```

Focused margin comparison:

```text
i4d_route_lobe_a_margin = 0.015
i4g_route_lobe_a_margin = 0.030
i4d_route_lobe_b_margin = 0.010
i4g_route_lobe_b_margin = 0.028
i4d_flattening_margin = 0.006
i4g_flattening_margin = 0.011
i4g_extraction_cost_margin = 0.013
```

Interpretation:

```text
I4-G is a focused answer to I6-B's competitive redistribution bottleneck. The
geometry remains competitive: one route lobe gains capacity while the opposed
lobe loses capacity, focal support remains stable, and aggregate neighbor
capacity remains near-neutral rather than becoming generative or extractive.

The improvement is that the two route lobes are farther from the mixed-lobe
floor and flattening/extraction costs are farther below ceiling. It therefore
strengthens the competitive transition surface without retuning policy or
replacing I4-D. GE4+ remains pending focused replay and stress.
```

## Iteration 5-B - Focused Margin Variant Replay Matrix

- [x] Replay I4-F and I4-G as focused variants.
- [x] Run artifact replay.
- [x] Run snapshot/load replay.
- [x] Run duplicate replay.
- [x] Confirm regime labels remain stable.
- [x] Confirm capacity-attribution, merge/leakage, and focal-survival-only controls pass.
- [x] Confirm GE5 remains pending I6-C.

Result:

```text
status = passed
acceptance_state = accepted_focused_margin_variants_ge4_replay_control_backed_pending_stress
output_digest = 0ce6c4dcb35f4c7bef0f2e17c8ab2ff87bde958706c390fd05e016b5092fb08e
provisional_ge_ladder_rung = GE4
focused_variant_ge4_supported = true
ge4_or_stronger_supported = true
ge5_or_stronger_supported = false
source_row_count = 2
rows_demoted = []
failed_checks = []
ready_for_i6c_focused_stress = true
```

Artifacts:

```text
outputs/n28_focused_margin_variant_replay_matrix.json
reports/n28_focused_margin_variant_replay_matrix.md
scripts/build_n28_focused_margin_variant_replay_matrix.py
outputs/n28_focused_margin_variant_replay_matrix_artifacts/*.json
```

Replay rows:

```text
I4-F neutral     -> neutral     artifact/snapshot/duplicate = passed/passed/passed  final = GE4
I4-G competitive -> competitive artifact/snapshot/duplicate = passed/passed/passed  final = GE4
```

Interpretation:

```text
I5-B upgrades the focused variants from GE3 to GE4 only. It shows that the
higher-margin neutral circulation and competitive redistribution rows are
replay/control consumable under the same shared policy family. It does not
replace I5 and does not claim stress-backed GE5 until I6-C.
```

## Iteration 6-C - Focused Margin Variant Stress Envelope

- [x] Stress I5-B focused variants using the same I6 stress family.
- [x] Sweep the same multiplier envelope used by I6-B.
- [x] Confirm all current focused stress rows preserve classification.
- [x] Confirm targeted I6-B bottleneck margins improve.
- [x] Confirm no critical or narrow current margins remain.
- [x] Confirm thresholds are not retuned and source rows are not mutated.
- [x] Keep GE6 and final N28 blocked pending claim classification.

Result:

```text
status = passed
acceptance_state = accepted_focused_margin_variants_ge5_stress_envelope_supported_pending_claim_classification
output_digest = 0dc3cc97695338d5f54719e993a4dd2912d5983eb03f066c3de04e027f3c06b3
provisional_ge_ladder_rung = GE5
focused_variant_ge5_supported = true
ge5_or_stronger_supported = true
ge6_or_stronger_supported = false
stress_row_count = 10
current_stress_rows_preserved = 10
targeted_bottleneck_improvement_count = 3
critical_current_margin_count = 0
narrow_current_margin_count = 0
minimum_current_margin = 0.005
broad_margin_robustness_supported = false
order_of_magnitude_robustness_supported = false
margin_interpretation = targeted_current_multiplier_margin_improvement_not_broad_robustness
failed_checks = []
ready_for_iteration_7_claim_classification = true
```

Artifacts:

```text
outputs/n28_focused_margin_variant_stress_envelope.json
reports/n28_focused_margin_variant_stress_envelope.md
scripts/build_n28_focused_margin_variant_stress_envelope.py
outputs/n28_focused_margin_variant_stress_envelope_artifacts/*.json
```

Targeted improvements:

```text
neutral / merge_leakage_pressure:
  I6-B critical margin = 0.002
  I6-C focused margin = 0.007

neutral / boundary_integrity_compression:
  I6-B critical margin = 0.001
  I6-C focused margin = 0.010

competitive / extraction_cost_pressure:
  I6-B critical margin = 0.002
  I6-C focused margin = 0.007
```

Interpretation:

```text
I6-C shows that the focused neutral circulation and competitive redistribution
variants improve the specific current-multiplier bottleneck margins identified
by I6-B. This is focused optimization of the weak competitive/neutral
transition rows, not broad margin robustness. The geometric change is not a new
regime label. I4-F remains neutral circulation and I4-G remains competitive
redistribution.

The stronger evidence is narrow: their circulation, leakage, route-lobe, and
flattening margins no longer sit on the I6-B critical edge under the current
stress multiplier. The absolute normalized margins remain small, with minimum
current margin 0.005, so this is not order-of-magnitude robustness and not GE6.

This supports focused GE5 evidence for the competitive/neutral transition
region only. It does not upgrade GE6, final N28, semantic cooperation, agency,
native support, Phase 8 completion, or ant ecology.
```

## Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification

- [x] Classify all positive, partial, rejected, blocked, and contrast rows.
- [x] Confirm primary and strengthening generative candidates are represented, or record blocker.
- [x] Confirm primary and strengthening extractive contrasts are represented, or record blocker.
- [x] Confirm primary and alternative competitive/neutral contrasts are represented, or record blocker.
- [x] Classify `shared_regime_policy_status`.
- [x] Confirm label-specific thresholds are either absent or recorded as split-policy blockers.
- [x] Confirm competitive/neutral rows are not promoted to generative evidence.
- [x] Confirm AP4/AP5 dependencies are row-local.
- [x] Confirm N27 context is not promoted to N28 evidence.
- [x] Confirm unsafe claim flags remain false.
- [x] Confirm no ant ecology implementation opens.

Result:

```text
status = passed
acceptance_state = accepted_ge5_controls_ap_claim_classification_pending_i8_closeout
output_digest = 13271b6c1e5e67f89fdabf77722aba648654094250cd1bf8c60d361c95560e35
provisional_ge_ladder_rung = GE5
n28_closeout_ceiling = N28-C5_replay_control_stress_backed_generative_extractive_candidate_supported
classification_row_count = 10
generative_row_count = 3
extractive_contrast_row_count = 3
competitive_neutral_contrast_row_count = 4
focused_margin_row_count = 2
shared_regime_policy_status = supported
ge5_or_stronger_supported = true
ge6_or_stronger_supported = false
final_n28_supported = false
broad_margin_robustness_supported = false
order_of_magnitude_robustness_supported = false
ap4_nat4_gap_resolved = false
ap5_nat4_gap_resolved = false
failed_checks = []
ready_for_iteration_8_closeout_and_n29_handoff = true
```

Artifacts:

```text
outputs/n28_controls_ap_dependency_claim_classification.json
reports/n28_controls_ap_dependency_claim_classification.md
scripts/build_n28_controls_ap_dependency_claim_classification.py
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i7_classification_summary.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4_row_primary_generative_candidate_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4a_row_generative_strengthening_candidate_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4a2_row_generative_mechanism_diversity_candidate_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4b_row_primary_extractive_contrast_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4c_row_extractive_strengthening_contrast_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4c2_row_extractive_mechanism_diversity_contrast_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4d_row_primary_competitive_neutral_contrast_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4e_row_competitive_neutral_mechanism_diversity_contrast_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4f_row_higher_margin_neutral_circulation_contrast_claim_classification_trace.json
outputs/n28_controls_ap_dependency_claim_classification_artifacts/n28_i4g_row_higher_margin_competitive_redistribution_contrast_claim_classification_trace.json
```

Interpretation:

```text
I7 classifies the N28 evidence stack as a bounded GE5 candidate pending I8
closeout. It does not close GE6 or final N28.

The strongest support is the broad I6 paired regime matrix: generative,
extractive, and competitive/neutral rows remain separable under one shared
policy, with replay/control backing from I5 and artifact-only blockers from
I5-A.

I6-A contributes the same-policy transition surface. It shows that the
classification boundary can hold across declared transition envelopes, but it
does not add new source-current GE evidence by itself.

I6-B remains a margin diagnostic. It identifies bottlenecks and motivates
focused variants, but it does not support broad robustness or GE6.

I6-C contributes focused current-multiplier margin evidence for I4-F and I4-G.
It removes the critical current-margin blockers for the focused
competitive/neutral region only. It does not widen the full I4-family envelope
and does not support order-of-magnitude robustness.

AP4 and AP5 NAT4 gaps remain unresolved and row-local. N27 transfer context is
not promoted to N28 evidence. Extractive and competitive/neutral rows remain
contrast evidence, not generative evidence. Semantic cooperation, semantic
choice, agency, native support, sentience, Phase 8 completion, and ant ecology
remain blocked.
```

## Iteration 8 - Closeout And N29 Handoff

- [x] Freeze final GE rung if warranted.
- [x] Freeze final N28-C rung if warranted.
- [x] Confirm closeout does not rely on a single generative-looking row.
- [x] Confirm GE5/N28-C5 require paired generative, extractive, and competitive/neutral regime separation unless explicit blockers are recorded.
- [x] Record whether same-rule classification is supported, partially supported, split-policy-required, or blocked.
- [x] Record final claim ceiling.
- [x] Record final controls and blockers.
- [x] Confirm source digests and artifact hashes.
- [x] Confirm no absolute paths.
- [x] Confirm `src_diff_empty` unless an explicit implementation defect is only recorded, not fixed.
- [x] Record N29 handoff.

Result:

```text
status = passed
acceptance_state = accepted_n28_c6_closeout_n29_handoff_ready
output_digest = 80ca5f1fcd75372fbd0f05065e67e077d140f4e9ff5931574f4d1beefee2ec4f
final_ge_ladder_rung = GE6_N29_ready_bounded_generative_extractive_persistence_evidence
final_n28_closeout_rung = N28-C6_N29_ready_bounded_generative_extractive_closeout
final_n28_supported = true
ready_for_n29 = true
same_rule_classification_status = supported
broad_margin_robustness_supported = false
order_of_magnitude_robustness_supported = false
ap4_nat4_gap_resolved = false
ap5_nat4_gap_resolved = false
native_ap5_supported = false
native_support_supported = false
phase8_completion_supported = false
ant_ecology_implementation_supported = false
src_diff_empty = true
failed_checks = []
```

Artifacts:

```text
outputs/n28_closeout_and_n29_handoff.json
reports/n28_closeout_and_n29_handoff.md
scripts/build_n28_closeout_and_n29_handoff.py
outputs/n28_closeout_and_n29_handoff_artifacts/source_lineage_trace.json
outputs/n28_closeout_and_n29_handoff_artifacts/claim_boundary_trace.json
outputs/n28_closeout_and_n29_handoff_artifacts/closeout_trace.json
outputs/n28_closeout_and_n29_handoff_artifacts/n29_handoff_record.json
```

Interpretation:

```text
N28 closes at GE6 / N28-C6 because I8 records a claim-clean handoff to N29
over the I7-classified GE5 evidence stack. GE6 is the N29-ready closeout rung;
it is not a new dynamics probe and not a broad robustness claim.

The final support remains bounded: paired generative, extractive, and
competitive/neutral regime separation survived replay/control/stress under one
shared policy. I6-A contributes same-policy transition context; I6-B remains a
margin diagnostic; I6-C contributes focused current-multiplier margin support
only.

N29 may consume N28 as bounded artifact-level generative/extractive persistence
evidence and claim-clean environment-exchange context. N29 must not consume it
as semantic cooperation, semantic choice, agency, native support, native AP5,
AP5 NAT4-gap resolution, Phase 8 completion, ant ecology implementation, broad
margin robustness, order-of-magnitude robustness, or unscoped multi-basin
substrate evidence.
```

Final closeout ceiling:

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
