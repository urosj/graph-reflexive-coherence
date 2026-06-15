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

Status: Pending.

- [ ] Evaluate source-current support-state fields.
- [ ] Define candidate support condition.
- [ ] Define target derivation rule.
- [ ] Confirm target derivation is not an external fixture label.
- [ ] Confirm target derivation is not post-hoc support labeling.
- [ ] Record runtime-visible surfaces.
- [ ] Record source-current replay requirement.
- [ ] Record producer decision vs bookkeeping split.
- [ ] Record identity acceptance relabel blocker.
- [ ] Record semantic goal ownership relabel blocker.
- [ ] Assign provisional AP level for the derived target row.

Expected artifacts:

- [ ] `outputs/n13_support_derived_target_candidate.json`
- [ ] `reports/n13_support_derived_target_candidate.md`
- [ ] `scripts/build_n13_support_derived_target_candidate.py`

## Iteration 4. Support-Seeking Regulation Candidate

Status: Pending.

- [ ] Evaluate bounded regulation responses against the derived support target.
- [ ] Record support error signal.
- [ ] Record response magnitude surface.
- [ ] Record bounded window.
- [ ] Record budget debit surface.
- [ ] Record support trend.
- [ ] Record saturation status.
- [ ] Record overcorrection status.
- [ ] Record out-of-envelope blocker.
- [ ] Record response packet scheduling boundary.
- [ ] Record support-disrupted negative control.
- [ ] Assign candidate/provisional AP level for support-seeking regulation.
- [ ] Defer final AP3 support until Iterations 5-7 controls pass.

Expected artifacts:

- [ ] `outputs/n13_support_seeking_regulation_candidate.json`
- [ ] `reports/n13_support_seeking_regulation_candidate.md`
- [ ] `scripts/build_n13_support_seeking_regulation_candidate.py`

## Iteration 5. External Proxy And Hidden Target Controls

Status: Pending.

- [ ] Build external-proxy-only control.
- [ ] Build hidden-support-target control.
- [ ] Build post-hoc support label control.
- [ ] Build support-disrupted regulation control.
- [ ] Build stale-source replay control.
- [ ] Build budget-ambiguous correction control.
- [ ] Build identity-acceptance relabel control.
- [ ] Build semantic-goal-ownership relabel control.
- [ ] Build agency relabel control.
- [ ] Confirm controls fail closed.

Expected artifacts:

- [ ] `outputs/n13_external_proxy_control_matrix.json`
- [ ] `reports/n13_external_proxy_control_matrix.md`
- [ ] `scripts/build_n13_external_proxy_control_matrix.py`

## Iteration 6. Support Disruption And Restoration Stress Matrix

Status: Pending.

- [ ] Evaluate support-present baseline.
- [ ] Evaluate support-disrupted regime.
- [ ] Evaluate explicit restoration regime.
- [ ] Evaluate neutral perturbation regime.
- [ ] Evaluate no-support-control regime.
- [ ] Record source-current replay requirements.
- [ ] Record budget and response surfaces.
- [ ] Record whether support-seeking regulation survives controls.
- [ ] Record AP ceiling after stress matrix.

Expected artifacts:

- [ ] `outputs/n13_support_disruption_restoration_matrix.json`
- [ ] `reports/n13_support_disruption_restoration_matrix.md`
- [ ] `scripts/build_n13_support_disruption_restoration_matrix.py`

## Iteration 7. Identity, Goal-Ownership, And Agency Boundary Record

Status: Pending.

- [ ] Record why support survival is not identity acceptance.
- [ ] Record why support-derived target is not semantic goal ownership.
- [ ] Record why bounded response is not intention.
- [ ] Record why self-maintenance candidate is not selfhood.
- [ ] Record why N13 is not agency.
- [ ] Record why N13 is not native support unless Phase 8 exists.
- [ ] Record remaining theory-sensitive blockers.
- [ ] Confirm all unsafe claim flags remain false.

Expected artifacts:

- [ ] `outputs/n13_claim_boundary_record.json`
- [ ] `reports/n13_claim_boundary_record.md`
- [ ] `scripts/build_n13_claim_boundary_record.py`

## Iteration 8. N13 Closeout And Handoff

Status: Pending.

- [ ] Close Hypothesis A.
- [ ] Close Hypothesis B.
- [ ] Close Hypothesis C.
- [ ] Freeze supported AP level.
- [ ] Confirm every seed row is classified.
- [ ] Record final support-condition candidates.
- [ ] Record final support-seeking regulation result.
- [ ] Record external proxy and hidden target controls.
- [ ] Record final blockers.
- [ ] Record final native support flags as false unless separate Phase 8 source
      exists.
- [ ] Record final claim flags as false for unsafe claims.
- [ ] Update handoff if needed.
- [ ] Decide whether next work is N14 or targeted Phase 8.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `src/*` remains clean for N13.

Expected artifacts:

- [ ] `outputs/n13_closeout_and_handoff.json`
- [ ] `reports/n13_closeout_and_handoff.md`
- [ ] `scripts/build_n13_closeout_and_handoff.py`

Acceptance statement:

```text
Iteration 8 passes if N13 closes with source-backed support-seeking regulation
evidence at its supported AP level and a claim-clean handoff, without
implementing Phase 8 or promoting support survival into identity acceptance,
semantic goal ownership, or agency.
```
