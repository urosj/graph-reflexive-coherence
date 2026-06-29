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

- [ ] Consume N20 I3 generative/extractive producer-residue and naturalization-debt ledger.
- [ ] Consume N20 I4 native-function / proxy descriptor for generative/extractive persistence.
- [ ] Consume N20 I5 same-basin continuation contract as the normative downstream contract.
- [ ] Consume N27 closeout as bounded CT6 transfer and N28 precursor context only.
- [ ] Record N27 side-effect precursor metrics without promoting them to N28 evidence.
- [ ] Record N27 `n28_generative_persistence_supported = false`.
- [ ] Record source roles, source digests, and source consumption boundaries.
- [ ] Record medium-debt fields deferred to N28/N29.
- [ ] Confirm no positive generative/extractive evidence opens.
- [ ] Confirm no semantic cooperation, native support, agency, sentience, Phase 8, or ant ecology claim opens.

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

## Iteration 2 - Generative / Extractive Schema And Control Freeze

- [ ] Freeze GE0...GE6 ladder.
- [ ] Freeze N28-C0...N28-C6 closeout ladder.
- [ ] Freeze paired-regime evidence requirement: primary and alternative rows for generative, extractive, and competitive/neutral regimes.
- [ ] Freeze N20 I5 same-basin continuation contract as normative.
- [ ] Freeze N20 I4 native-function / proxy descriptor as descriptor context.
- [ ] Freeze N20 I3 producer-residue ledger as residue / debt context.
- [ ] Freeze N27 closeout and side-effect rows as context-only.
- [ ] Freeze required evidence fields.
- [ ] Freeze reusable `generative_extractive_core` object.
- [ ] Freeze `generative_extractive_core_digest` canonicalization policy.
- [ ] Freeze focal stability and neighbor capacity formulas.
- [ ] Freeze extraction, flattening, merge/leakage formulas.
- [ ] Freeze regime labels and evidence roles.
- [ ] Freeze regime-boundary trace requirements.
- [ ] Freeze `shared_regime_policy_status` enum.
- [ ] Freeze policy-divergence record fields.
- [ ] Freeze policy-retuning / label-specific-threshold / post-hoc-boundary controls.
- [ ] Freeze medium-debt and producer-residue record fields.
- [ ] Freeze rung-specific artifact role requirements.
- [ ] Freeze replay requirements.
- [ ] Freeze AP4/AP5 dependency statuses.
- [ ] Require row-local reason when AP4/AP5 status is `not_applicable`.
- [ ] Freeze active-null/control families.
- [ ] Freeze claim boundary and unsafe claim flags.
- [ ] Confirm no positive N28 evidence opens.

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

## Iteration 3 - Active Nulls And Failure Baselines

- [ ] Run focal-survival-only-as-generative control.
- [ ] Run neighbor-label-only-as-capacity control.
- [ ] Run neighbor-count-only-as-capacity control.
- [ ] Run merge/leakage-as-support control.
- [ ] Run extractive-flattening-masked control.
- [ ] Run competitive-persistence-as-generative control.
- [ ] Run transfer-success-as-N28-success control.
- [ ] Run hidden-capacity-attribution-policy control.
- [ ] Run producer-generativity-label control.
- [ ] Run medium-segmentation-policy-hidden control.
- [ ] Run environment-capacity-budget-mismatch control.
- [ ] Run neighbor-support-floor-missing control.
- [ ] Run neighbor-boundary-integrity-missing control.
- [ ] Run replay-failure control.
- [ ] Run stress-variant-failure control.
- [ ] Run semantic-cooperation relabel control.
- [ ] Run native-support relabel control.
- [ ] Run ant-ecology relabel control.
- [ ] Run Phase 8 completion relabel control.
- [ ] Run native-AP5 / AP5-NAT4-gap relabel controls.
- [ ] Confirm failed-open control count is zero.
- [ ] Confirm no positive GE rung is assigned.

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

## Iteration 4 - Primary Generative Candidate Probe

- [ ] Produce a generative candidate row, not only a focal-survival row.
- [ ] Declare classification policy before use.
- [ ] Record focal basin signature and stability.
- [ ] Record focal support/coherence floor.
- [ ] Record neighbor or sub-basin scope.
- [ ] Record neighbor distinguishability, support, and boundary traces.
- [ ] Record environment basin-forming capacity trace.
- [ ] Record extraction, flattening, merge/leakage traces.
- [ ] Confirm neighbor capacity improves above declared threshold.
- [ ] Confirm extraction, flattening, merge, and leakage remain below ceilings.
- [ ] Set `regime_label = generative`.
- [ ] Set `regime_evidence_role = positive_candidate`.
- [ ] Record artifact manifest and hashes.
- [ ] Keep result provisional pending replay/control validation.

## Iteration 4-A - Alternative Generative Candidate Probe

- [ ] Produce a second generative candidate row under a distinct setup.
- [ ] Test whether the alternative can use the same frozen policy family.
- [ ] If the same policy family fails, record policy divergence instead of retuning.
- [ ] Confirm thresholds are not widened relative to the primary generative row unless a split-policy blocker is explicitly recorded.
- [ ] Confirm the row does not import or relabel the primary I4 outcome.
- [ ] Record focal basin stability and neighborhood capacity improvement.
- [ ] Confirm extraction, flattening, merge, and leakage remain below ceilings.
- [ ] Set `regime_label = generative`.
- [ ] Set `regime_evidence_role = positive_candidate_alternative`.
- [ ] Keep result provisional pending replay/control validation.

## Iteration 4-B - Primary Extractive Persistence Contrast Probe

- [ ] Produce an extractive persistence contrast row.
- [ ] Preserve focal basin stability.
- [ ] Record neighbor capacity degradation or boundary weakening.
- [ ] Record extraction, flattening, merge, or leakage as the degrading mechanism.
- [ ] Set `regime_label = extractive`.
- [ ] Set `regime_evidence_role = measured_contrast`.
- [ ] Confirm the row is not promoted to generative evidence.
- [ ] Preserve N20/N27 source boundaries.
- [ ] Confirm thresholds are not retuned to force extractive classification.

## Iteration 4-C - Alternative Extractive Persistence Contrast Probe

- [ ] Produce a second extractive contrast row under a distinct degradation mechanism or neighborhood variant.
- [ ] Preserve focal basin stability.
- [ ] Record neighbor capacity degradation or boundary weakening.
- [ ] Record extraction, flattening, merge, or leakage as the degrading mechanism.
- [ ] Confirm the row is not a relabeled copy of I4-B.
- [ ] Set `regime_label = extractive`.
- [ ] Set `regime_evidence_role = measured_contrast_alternative`.
- [ ] Confirm the row is not promoted to generative evidence.
- [ ] Preserve N20/N27 source boundaries.
- [ ] Confirm thresholds are not retuned to force extractive classification.

## Iteration 4-D - Primary Competitive / Neutral Persistence Contrast Probe

- [ ] Produce a competitive or neutral persistence contrast row.
- [ ] Preserve focal basin stability.
- [ ] Record neighborhood capacity as unchanged, mixed, or competitively redistributed.
- [ ] Set `regime_label = competitive` or `neutral`.
- [ ] Set `regime_evidence_role = measured_contrast`.
- [ ] Confirm the row is not promoted to generative evidence.
- [ ] Preserve N20/N27 source boundaries.
- [ ] Confirm variant is not threshold retuning.
- [ ] Record whether result sharpens the paired generative/extractive/competitive regime boundary.

## Iteration 4-E - Alternative Competitive / Neutral Persistence Contrast Probe

- [ ] Produce a second competitive or neutral persistence contrast under a distinct setup.
- [ ] Preserve focal basin stability.
- [ ] Record neighborhood capacity as unchanged, mixed, or competitively redistributed.
- [ ] Confirm the row is not a relabeled copy of I4-D.
- [ ] Set `regime_label = competitive` or `neutral`.
- [ ] Set `regime_evidence_role = measured_contrast_alternative`.
- [ ] Confirm the row is not promoted to generative evidence.
- [ ] Preserve N20/N27 source boundaries.
- [ ] Confirm variant is not threshold retuning.
- [ ] Record whether result sharpens the paired-regime boundary.

## Iteration 5 - Replay And Capacity Attribution Matrix

- [ ] Run artifact replay.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay.
- [ ] Run capacity-attribution controls.
- [ ] Run merge/leakage controls.
- [ ] Run focal-survival-only controls.
- [ ] Replay I4 through I4-E paired-regime rows.
- [ ] Test whether replayed rows can still use one shared policy family.
- [ ] Record `shared_regime_policy_status` or a provisional policy-divergence blocker.
- [ ] Confirm both generative candidates remain generative or are demoted explicitly.
- [ ] Confirm both extractive contrasts remain extractive or are demoted explicitly.
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
- [ ] Stress I4 through I4-E paired-regime rows under the same policy family first.
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
- [ ] Confirm primary and alternative generative candidates are represented, or record blocker.
- [ ] Confirm primary and alternative extractive contrasts are represented, or record blocker.
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
