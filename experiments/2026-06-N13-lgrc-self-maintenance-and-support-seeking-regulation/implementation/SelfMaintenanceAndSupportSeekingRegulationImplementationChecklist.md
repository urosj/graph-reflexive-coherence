# N13 Self-Maintenance And Support-Seeking Regulation Implementation Checklist

This checklist tracks implementation of
`2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation`.

Status keys:

```text
Pending     not started
In Progress work has begun
Complete    implemented, run, and recorded
Blocked     cannot proceed without a decision or upstream result
Deferred    intentionally postponed
```

## Global Constraints

- [ ] Keep N13 as an agency-prerequisite experiment, not an agency claim
      experiment.
- [ ] Keep N13 experiment-local unless a separate Phase 8/core task is opened.
- [ ] Stop before changing `src/*`.
- [ ] If Phase 8 is opened later, inspect `src/pygrc/telemetry` as a
      first-class native surface namespace.
- [ ] Treat N11 GALI7 as artifact-only source evidence, not native support.
- [ ] Treat N12 NAT4 rows as Phase 8-ready contracts, not native support.
- [ ] Treat N12 identity acceptance and integration meta-policy rows as
      theory-sensitive blockers.
- [ ] Start from support-seeking regulation, not identity-seeking regulation.
- [ ] Do not consume identity acceptance, runtime identity acceptance, semantic
      goal ownership, agency, or fully native integration as supported inputs.
- [ ] Preserve compatibility with RC causality, coherence, LGRC geometry,
      packet scheduling, topology lineage, and budget conservation.
- [ ] Preserve separated support, proxy, response, route, artifact replay, and
      node-plus-packet budget surfaces.
- [ ] Split support-state fields from external proxy fields for every candidate
      row.
- [ ] Split essential producer decisions from bookkeeping fields for every
      candidate row.
- [ ] Require artifact-only replay or source-current reconstruction gates where
      applicable.
- [ ] Block external-proxy relabeling.
- [ ] Block hidden support target use.
- [ ] Block post-hoc support labeling.
- [ ] Block support-disrupted regulation evidence from counting as
      self-maintenance.
- [ ] Block budget ambiguity.
- [ ] Keep support survival distinct from identity acceptance.
- [ ] Keep support-derived target distinct from semantic goal ownership.
- [ ] Keep bounded response distinct from intention.
- [ ] Keep self-maintenance candidate distinct from selfhood, personhood,
      biological behavior, and agency.
- [ ] Keep native support flags false unless separate Phase 8 source exists.
- [ ] Record exact replay commands for every generated artifact.
- [ ] Before closing any file-editing turn, run `git diff --check`.
- [ ] Before closing any file-editing turn, run `git diff -- src`.

## Iteration 0. Planning And Stubs

Status: Complete.

- [x] Create N13 experiment root.
- [x] Create N13 root README.
- [x] Create implementation README.
- [x] Create implementation plan.
- [x] Create implementation checklist.
- [x] Create `configs/`, `outputs/`, `reports/`, `scripts/`, and
      `hypotheses/` stubs.
- [x] Record N13 as an agency-prerequisite experiment, not an agency claim.
- [x] Record N13 as artifact-level unless Phase 8 is separately opened.
- [x] Record N13's target as `AP3`, not agency.
- [x] Record N12 closeout as the direct source boundary.
- [x] Record Hypothesis A/B/C split.
- [x] Record support-seeking vs identity-seeking boundary.
- [x] Record external proxy, hidden target, support disruption, budget, and
      claim-promotion controls.
- [x] Record claim boundaries and native support blockers.

Acceptance statement:

```text
N13 starts from N12's claim-clean bridge closeout and opens only a
source-backed support-condition inventory, support-derived target track,
support-seeking regulation track, and control matrix. A valid N13 positive
result requires source-current support-state fields, explicit target
derivation, bounded response surfaces, budget/replay gates, external-proxy and
hidden-target controls, and no agency, intention, semantic goal ownership,
identity acceptance, selfhood, personhood, biological, unrestricted-agency, or
fully native integration claim promotion.
```

Acceptance status:

```text
Achieved. The N13 experiment skeleton, README, implementation plan,
implementation checklist, hypotheses records, and artifact stubs were created.
No N13 inventory builders, probes, validators, or Phase 8 implementation have
been run. No `src/*` changes are required for Iteration 0.
```

Implementation record:

- Added `experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/README.md`.
- Added `implementation/README.md`.
- Added `implementation/SelfMaintenanceAndSupportSeekingRegulationImplementationPlan.md`.
- Added `implementation/SelfMaintenanceAndSupportSeekingRegulationImplementationChecklist.md`.
- Added `hypotheses/README.md`.
- Added `hypotheses/hypothesis_a_support_condition_inventory.md`.
- Added `hypotheses/hypothesis_b_support_seeking_regulation.md`.
- Added `hypotheses/hypothesis_c_claim_boundary_blockers.md`.
- Added stub README files for `configs/`, `outputs/`, `reports/`, and
  `scripts/`.
- Created the N13 experiment directory layout.
- No implementation scripts or probes have been run yet.

## Iteration 1. Baseline Source And Support-Condition Inventory

Status: Complete.

- [x] Inventory N12 closeout and N13 handoff records.
- [x] Inventory N12 Phase 8 readiness matrix rows relevant to route memory and
      response magnitude.
- [x] Inventory N07 support survival/disruption/restoration evidence.
- [x] Inventory N09 bounded proxy regulation evidence.
- [x] Inventory N10 support-sensitive integration evidence.
- [x] Inventory N11 GALI7 artifact-only generalization evidence.
- [x] Record source artifact paths, report paths, and SHA-256 digests.
- [x] Record support-state fields.
- [x] Record external proxy fields.
- [x] Record producer-mediated fields.
- [x] Record bookkeeping-only fields.
- [x] Record runtime-visible surfaces.
- [x] Record budget surfaces.
- [x] Record response surfaces.
- [x] Record provisional AP levels.
- [x] Record claim ceilings and blocked claims.
- [x] Confirm no identity acceptance evidence is consumed as supported input.
- [x] Confirm no native support opens.
- [x] Confirm `src/*` remains clean for Iteration 1.

Expected artifacts:

- [x] `outputs/n13_support_condition_inventory.json`
- [x] `reports/n13_support_condition_inventory.md`
- [x] `scripts/build_n13_support_condition_inventory.py`

Acceptance statement:

```text
Iteration 1 passes if every support-condition row is source-backed and N13
records support-state, external-proxy, producer-decision, budget, replay, and
claim-boundary fields without promoting support survival into identity
acceptance or native support.
```

Acceptance state:

```text
Achieved. Iteration 1 builds a seven-row source-backed inventory from N07,
N09, N10, N11, and N12. It records two AP0 boundary/envelope rows, two AP1
bounded response/readiness rows, three AP2 support-condition or
support-sensitive rows, and zero AP3 self-maintenance rows. Support-state,
external-proxy, producer-decision, bookkeeping, runtime-visible, budget,
response, claim, source, and report digest fields are recorded. The summary
separates actual support-condition rows from N11/N12 boundary rows. Identity
acceptance, native support, Phase 8 implementation, and agency remain unopened.
```

Implementation record:

- Added and ran `scripts/build_n13_support_condition_inventory.py`.
- Generated `outputs/n13_support_condition_inventory.json`.
- Generated `reports/n13_support_condition_inventory.md`.
- Command:

```text
.venv/bin/python experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/scripts/build_n13_support_condition_inventory.py
```

- Status: `passed`.
- Output digest:

```text
4c8cd0a1ea074d27ff1a7cd5cdd176b789ef57da808223c1fa08750355732e23
```

- Artifact SHA-256:

```text
outputs/n13_support_condition_inventory.json d5aa30e8257769729ada1ecd4c7adf59342ae41b2d2b68b3ff06ce83105849d2
reports/n13_support_condition_inventory.md 575c7e518f1af9c8b485f63ecbf9b962072ff49ebe54d6c17780ec90fd130435
scripts/build_n13_support_condition_inventory.py 3632f4835e1cca46194a9c605f8b2ec9f0745d063416ca18c758959e1552bc43
```

## Iteration 2. Support-Condition Schema And AP Mapping

Status: Complete.

- [x] Freeze candidate row schema.
- [x] Freeze AP0-AP8 mapping for N13.
- [x] Freeze AP2 vs AP3 criteria.
- [x] Freeze support-condition tags.
- [x] Freeze support-derived target fields.
- [x] Freeze external proxy separation fields.
- [x] Freeze claim flags.
- [x] Freeze control flags.
- [x] Freeze budget/replay fields.
- [x] Freeze telemetry requirements if needed.
- [x] Freeze fail-closed blocker tags.
- [x] Reject identity acceptance relabeling.
- [x] Reject semantic goal ownership relabeling.
- [x] Reject agency relabeling.
- [x] Reject hidden support target use.
- [x] Reject budget ambiguity.
- [x] Declare no-native-implementation boundary.

Expected artifacts:

- [x] `outputs/n13_support_schema_v1.json`
- [x] `reports/n13_support_schema_v1.md`
- [x] `scripts/build_n13_support_schema_v1.py`

Acceptance statement:

```text
Iteration 2 passes if the schema distinguishes AP2 support-sensitive
regulation from AP3 self-maintenance candidates and rejects identity
acceptance, semantic goal ownership, agency, stale source use, hidden target
use, and budget ambiguity.
```

Acceptance state:

```text
Achieved. Iteration 2 freezes the AP0-AP8 mapping for N13, support-condition
row schema, AP2/AP3 criteria, primary dispositions, control flags,
fail-closed blockers, forced-false claim flags, and validation scope. AP3
requires source-current support-state target derivation, external-proxy
separation, support-disrupted controls, bounded response and budget surfaces,
and claim relabel blockers. Row validation against AP3 starts in Iterations
3-7.
```

Implementation record:

- Added and ran `scripts/build_n13_support_schema_v1.py`.
- Generated `outputs/n13_support_schema_v1.json`.
- Generated `reports/n13_support_schema_v1.md`.
- Command:

```text
.venv/bin/python experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/scripts/build_n13_support_schema_v1.py
```

- Status: `passed`.
- Output digest:

```text
7691834eb654dc15ee8aabf8ce732a10a72c375d95f3fa97290a8b6cf6984a4f
```

- Artifact SHA-256:

```text
outputs/n13_support_schema_v1.json 55d9105ca829d5ca23467906390ddeebdd35b72a09dfa688ae01ff1804bd8e6f
reports/n13_support_schema_v1.md 123d58e36e57a4e760ad5b13d59682ba237b3cf18ba74e15a4e4984535e26a73
scripts/build_n13_support_schema_v1.py 36b85fc1f6021501f0b92a4afc10a8c1b199d847f9b1419ec00576fd0b843fb2
```

## Iteration 3. Support-State Derived Target Candidate

Status: Complete.

- [x] Evaluate source-current support-state fields.
- [x] Define candidate support condition.
- [x] Define target derivation rule.
- [x] Confirm target derivation is not an external fixture label.
- [x] Confirm target derivation is not post-hoc support labeling.
- [x] Record runtime-visible surfaces.
- [x] Record source-current replay requirement.
- [x] Record producer decision vs bookkeeping split.
- [x] Record identity acceptance relabel blocker.
- [x] Record semantic goal ownership relabel blocker.
- [x] Assign provisional AP level for the derived target row.

Expected artifacts:

- [x] `outputs/n13_support_derived_target_candidate.json`
- [x] `reports/n13_support_derived_target_candidate.md`
- [x] `scripts/build_n13_support_derived_target_candidate.py`

Acceptance statement:

```text
Iteration 3 passes if N13 isolates a source-current support-derived target
candidate with explicit input fields, target derivation, replay/source
requirements, producer/bookkeeping split, external-proxy separation,
post-hoc-label and hidden-target audits, and no final AP3, identity
acceptance, semantic goal ownership, agency, native support, or Phase 8 claim.
```

Acceptance state:

```text
Achieved. Iteration 3 isolates
support_retention_above_threshold_source_current as a source-current
support-derived target candidate. The derivation rule is
final_A_support_retention >= support_survival_threshold, sourced from N07
support lane fields. The target excludes N09 external proxy fields, matches
all N07 source lane classifications, cross-checks against the N10 support
matrix, and records post-hoc-label and hidden-target audits. It assigns only
provisional AP2 target-candidate status. Final AP3, self-maintenance support,
support-seeking regulation, native support, Phase 8 implementation, identity
acceptance, semantic goal ownership, and agency remain unopened.
```

Implementation record:

- Added and ran `scripts/build_n13_support_derived_target_candidate.py`.
- Generated `outputs/n13_support_derived_target_candidate.json`.
- Generated `reports/n13_support_derived_target_candidate.md`.
- Command:

```text
.venv/bin/python experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/scripts/build_n13_support_derived_target_candidate.py
```

- Status: `passed`.
- Output digest:

```text
917e65721362fcda37ea4777489a5e3289a35ef550a16b3774884c803584ac3e
```

- Artifact SHA-256:

```text
outputs/n13_support_derived_target_candidate.json 59db9662a29dad513bc0d861b31ef8c46ae1d421be3befe97b383752855c7bdb
reports/n13_support_derived_target_candidate.md ff494f48a5d29cc6ef4a72acace91108c02e976cee31c186dff604009767ccbd
scripts/build_n13_support_derived_target_candidate.py 6927fe7a0392755c33f79887ac0c2a733a5e4de5b8a2a9c5a17608f0059e0187
```

## Iteration 4. Support-Seeking Regulation Candidate

Status: Complete.

- [x] Evaluate bounded regulation responses against the derived support target.
- [x] Record support error signal.
- [x] Record response magnitude surface.
- [x] Record bounded window.
- [x] Record budget debit surface.
- [x] Record support trend.
- [x] Record saturation status.
- [x] Record overcorrection status.
- [x] Record out-of-envelope blocker.
- [x] Record response packet scheduling boundary.
- [x] Record support-disrupted negative control.
- [x] Assign candidate/provisional AP level for support-seeking regulation.
- [x] Defer final AP3 support until Iterations 5-7 controls pass.

Expected artifacts:

- [x] `outputs/n13_support_seeking_regulation_candidate.json`
- [x] `reports/n13_support_seeking_regulation_candidate.md`
- [x] `scripts/build_n13_support_seeking_regulation_candidate.py`

- Output digest:

```text
a6c367246eaeba14953b87c4a89862238b5bde4568308f1ee4c7ef1d9c85116b
```

- Artifact SHA-256:

```text
outputs/n13_support_seeking_regulation_candidate.json 890611bf58898034d728af897b1a5d799aee999faaf5ec6446691121b9d8c9ea
reports/n13_support_seeking_regulation_candidate.md 912a1340d9ff47381951c52f3e5093e0d7b320385a7c21b52f37968a30b8e449
scripts/build_n13_support_seeking_regulation_candidate.py d3638305010e349c9c704f1915b82c7c1d3ea255d2b20701979c274849864c76
```

- Acceptance state:

```text
candidate_ap_level = AP3
provisional_ap_level = AP3_candidate_pending_controls
final_ap3_supported = false
self_maintenance_candidate_supported = false
native_support_opened = false
phase8_opened = false
```

## Iteration 5. External Proxy And Hidden Target Controls

Status: Complete.

- [x] Build external-proxy-only control.
- [x] Build hidden-support-target control.
- [x] Build post-hoc support label control.
- [x] Build support-disrupted regulation control.
- [x] Build stale-source replay control.
- [x] Build budget-ambiguous correction control.
- [x] Build identity-acceptance relabel control.
- [x] Build semantic-goal-ownership relabel control.
- [x] Build agency relabel control.
- [x] Build native-support-without-Phase-8 relabel control.
- [x] Confirm controls fail closed.
- [x] Record Iteration 5 interpretation.

Expected artifacts:

- [x] `outputs/n13_external_proxy_control_matrix.json`
- [x] `reports/n13_external_proxy_control_matrix.md`
- [x] `scripts/build_n13_external_proxy_control_matrix.py`

- Output digest:

```text
4894859811d54d1ebd80411847de5bd4670bfe8e282f3bffea3c0d0712ce7d16
```

- Artifact SHA-256:

```text
outputs/n13_external_proxy_control_matrix.json 40b50b7df537c908af28d0dbb352bf154dea3e023979928aa89fe8f3444a028d
reports/n13_external_proxy_control_matrix.md d3d97e379004ed49de812c6d516e20ed99bcfa2c0203ce896017e899faaf382a
scripts/build_n13_external_proxy_control_matrix.py cce2592dd8236f3e4e0b357a86887019d6b989da4e3a4973413264716bdd22d8
```

- Acceptance state:

```text
external_proxy_controls_passed = true
hidden_target_controls_passed = true
post_hoc_label_controls_passed = true
support_disrupted_pre_stress_control_passed = true
budget_control_passed = true
claim_relabel_controls_passed = true
interpretation_record = n13_i5_interpretation_external_proxy_controls_v1
provisional_ap_level = AP3_candidate_control_clean_pending_stress_and_boundary
final_ap3_supported = false
self_maintenance_candidate_supported = false
native_support_opened = false
phase8_opened = false
```

## Iteration 6. Support Disruption And Restoration Stress Matrix

Status: Complete.

- [x] Evaluate support-present baseline.
- [x] Evaluate support-disrupted regime.
- [x] Evaluate explicit restoration regime.
- [x] Evaluate neutral perturbation regime.
- [x] Evaluate no-support-control regime.
- [x] Record source-current replay requirements.
- [x] Record budget and response surfaces.
- [x] Record whether support-seeking regulation survives controls.
- [x] Record AP ceiling after stress matrix.
- [x] Record Iteration 6 interpretation.

Expected artifacts:

- [x] `outputs/n13_support_disruption_restoration_matrix.json`
- [x] `reports/n13_support_disruption_restoration_matrix.md`
- [x] `scripts/build_n13_support_disruption_restoration_matrix.py`

- Output digest:

```text
f515ff673d38adba5d401088762040899add0e0f91d29f1f9d37de9100db7100
```

- Artifact SHA-256:

```text
outputs/n13_support_disruption_restoration_matrix.json 35270298acde53f910eb9b88582d7c326d89ca601f30bef44aaaf68b657c9363
reports/n13_support_disruption_restoration_matrix.md 3bbf1027e535b3c6136223ca1559f6bdd4e29c6a736fe1f19dbc559f0870685b
scripts/build_n13_support_disruption_restoration_matrix.py 4288116fe4f547fc5115b26fb827b7100da8f01332a6ad4ac9c70439697b0731
```

- Acceptance state:

```text
support_disruption_restoration_stress_matrix_passed = true
support_seeking_regulation_survives_controls = true
interpretation_record = n13_i6_interpretation_stress_matrix_v1
provisional_ap_level = AP3_candidate_stress_clean_pending_claim_boundary
final_ap3_supported = false
self_maintenance_candidate_supported = false
native_support_opened = false
phase8_opened = false
```

- Interpretation:

```text
The system has an artifact-level AP3 stress-clean support-seeking regulation
candidate: it derives a support error from source-current support state,
schedules a bounded budgeted response only when that support error is positive,
avoids false-positive response when support remains valid, and blocks response
when no support target exists.

support present -> no response needed
mild/non-disruptive support weakening -> no false-positive response
support disrupted -> bounded response scheduled
explicit restoration -> no extra response needed
no support target -> response blocked

stress-clean candidate != final supported AP3
support-seeking regulation != agency
support survival != identity acceptance
bounded response != intention
artifact-level stress behavior != native support
```

## Iteration 7. Identity, Goal-Ownership, And Agency Boundary Record

Status: Complete.

- [x] Record why support survival is not identity acceptance.
- [x] Record why support-derived target is not semantic goal ownership.
- [x] Record why bounded response is not intention.
- [x] Record why self-maintenance candidate is not selfhood.
- [x] Record why N13 is not agency.
- [x] Record why N13 is not native support unless Phase 8 exists.
- [x] Record why N13 is not fully native integration.
- [x] Record why N13 is not personhood or biological behavior.
- [x] Record remaining theory-sensitive blockers.
- [x] Confirm all unsafe claim flags remain false.
- [x] Record Iteration 7 interpretation.

Expected artifacts:

- [x] `outputs/n13_claim_boundary_record.json`
- [x] `reports/n13_claim_boundary_record.md`
- [x] `scripts/build_n13_claim_boundary_record.py`

- Output digest:

```text
5a4aae36a54f566533270028ae62943490f75ef0fd210d821ab234193a8983db
```

- Artifact SHA-256:

```text
outputs/n13_claim_boundary_record.json c50564556c1ea6f71547826f13214ee1cfb6154f51f1b2affb21ea075485327b
reports/n13_claim_boundary_record.md f23186194c8a8a5372bb4f693830a00ad623d1b85deda3802b8a7daf92063edc
scripts/build_n13_claim_boundary_record.py 20707e041e7c9cc9c4baf54e7a2ae591a7bc68dfa968f266bd97dc4aba5e5e70
```

- Acceptance state:

```text
claim_boundary_record_passed = true
interpretation_record = n13_i7_interpretation_claim_boundary_v1
candidate_ap_level = AP3
provisional_ap_level = AP3_candidate_boundary_clean_pending_closeout
final_ap3_supported = false
final_ap_freeze_pending_iteration8 = true
self_maintenance_candidate_supported = false
native_support_opened = false
phase8_opened = false
```

- Interpretation:

```text
The N13 stress-clean AP3 candidate is claim-clean: the positive result may be
interpreted as artifact-level support-seeking regulation, but not as identity
acceptance, semantic goal ownership, intention, agency, selfhood, personhood,
biological behavior, native support, or fully native integration.
```

## Iteration 8. N13 Closeout And Handoff

Status: Complete.

- [x] Close Hypothesis A.
- [x] Close Hypothesis B.
- [x] Close Hypothesis C.
- [x] Freeze supported AP level.
- [x] Confirm every seed row is classified.
- [x] Record final support-condition candidates.
- [x] Record final support-seeking regulation result.
- [x] Record external proxy and hidden target controls.
- [x] Record final blockers.
- [x] Record whole-experiment interpretation.
- [x] Record final native support flags as false unless separate Phase 8 source
      exists.
- [x] Record final claim flags as false for unsafe claims.
- [x] Update handoff if needed.
- [x] Decide whether next work is N14 or targeted Phase 8.
- [x] Confirm `src_diff_empty = true`.
- [x] Confirm `native_supported_flags = false`.
- [x] Confirm `phase8_opened = false`.
- [x] Confirm `src/*` remains clean for N13.

Expected artifacts:

- [x] `outputs/n13_closeout_and_handoff.json`
- [x] `reports/n13_closeout_and_handoff.md`
- [x] `scripts/build_n13_closeout_and_handoff.py`

- Output digest:

```text
e4a1df87ca55d5e3710ccc77739f71589a8f4767fc517e9030662b5f6d06380b
```

- Artifact SHA-256:

```text
outputs/n13_closeout_and_handoff.json 4a6aefc94f50d90795c64199e7cf84b430a197aa5f0e07c9215e6fa66b362806
reports/n13_closeout_and_handoff.md e2b46f6790e95488c0b3eef70469fcfd618b31ff6b2b9aa13ead1c8ed9ae3b45
scripts/build_n13_closeout_and_handoff.py 3aa8b874e4eeaa01b3efee2b4824d24c99a83a3b2cc6576302cdbb9b36d9e89f
```

- Hypothesis acceptance states:

```text
Hypothesis A = supported
Hypothesis B = supported
Hypothesis C = supported
```

- Whole-experiment interpretation:

```text
N13 supports artifact-level AP3 self-maintenance candidate /
support-seeking regulation candidate evidence only. It does not support
agency, identity acceptance, semantic goal ownership, selfhood, native support,
or fully native integration.
```

- Closeout state:

```text
final_supported_ap_level = AP3
final_ap3_supported = true
self_maintenance_candidate_supported = true
final_claim_ceiling = artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation
artifact_only = true
fully_native = false
native_supported_flags = false
native_support_opened = false
phase8_opened = false
agency_claim_opened = false
identity_acceptance_opened = false
semantic_goal_ownership_opened = false
```

- Handoff state:

```text
recommended_next = N14_consequence_sensitive_route_selection
recommended_branch = continue_artifact_roadmap_no_src
targeted_phase8_required_before_n14 = false
targeted_phase8_optional_parallel_branch = true
```

Acceptance statement:

```text
Iteration 8 passes if N13 closes with source-backed support-seeking regulation
evidence at its supported AP level and a claim-clean handoff, without
implementing Phase 8 or promoting support survival into identity acceptance,
semantic goal ownership, or agency.
```
