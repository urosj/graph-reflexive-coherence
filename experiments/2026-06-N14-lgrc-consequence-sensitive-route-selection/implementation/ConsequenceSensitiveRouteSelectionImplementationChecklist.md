# N14 Consequence-Sensitive Route Selection Implementation Checklist

## Global Rules

- [ ] Preserve the N14 claim boundary.
- [ ] Do not edit `src/*`.
- [ ] Use `.venv/bin/python` for local script/test runs.
- [ ] Use source-backed artifacts and SHA-256 digests.
- [ ] Do not promote N12 NAT4 readiness records into native support.
- [ ] Do not promote N13 AP3 support-seeking regulation into selfhood,
      identity acceptance, intention, or agency.
- [ ] Keep `phase8_opened = false` unless a separate Phase 8 task is explicitly
      opened.
- [ ] Before closing any turn that edits files, run `git diff --check`.
- [ ] Before closing any turn that edits files, run `git diff -- src`.

## Setup

- [x] Create N14 experiment root.
- [x] Create `README.md`.
- [x] Create `configs/`, `hypotheses/`, `implementation/`, `outputs/`,
      `reports/`, and `scripts/` directories.
- [x] Create N14-specific hypotheses.
- [x] Create implementation plan.
- [x] Create implementation checklist.

## Hypotheses

- [ ] Hypothesis A: pre-selection consequence records.
- [ ] Hypothesis B: rank-sensitive route selection.
- [ ] Hypothesis C: intention and agency boundary.

## Iteration 1. Baseline And Consequence Source Inventory

- [x] Pin N06 route arbitration source artifacts.
- [x] Pin N08 route memory / affordance source artifacts.
- [x] Pin N09 bounded response regulation source artifacts.
- [x] Pin N12 NAT4 readiness source artifacts.
- [x] Pin N13 AP3 support-seeking regulation source artifacts.
- [x] Classify source rows by route, memory, regulation, support, or boundary
      role.
- [x] Record provisional AP levels only.
- [x] Confirm no final AP4 claim is made.

Expected artifacts:

- [x] `outputs/n14_consequence_source_inventory.json`
- [x] `reports/n14_consequence_source_inventory.md`
- [x] `scripts/build_n14_consequence_source_inventory.py`

Output digest:

```text
7e8013464efdb35805bc9aa9b765a5c81afaa2a1f0d7210706d43ddd06a41513
```

Artifact SHA-256:

```text
outputs/n14_consequence_source_inventory.json b0cc190a75ac571614966778557b5af3f02f844a79da43602c26e59256f3d8f8
reports/n14_consequence_source_inventory.md 49d9ee46ad6be542da973b75d573fd0af51b117388912c5d4ca005114fd97d28
scripts/build_n14_consequence_source_inventory.py cfdbd7259508d63c26258e7157998a077e0120db865af2665f78c1b27ed71800
```

Acceptance state:

```text
accepted_source_inventory_only_no_ap4
```

Interpretation:

```text
N14 has sufficient pinned source coverage to proceed, but no route consequence
records or AP4 selection candidate exist yet.
```

## Iteration 2. Consequence Selection Schema And AP4 Gate

- [x] Freeze consequence record schema.
- [x] Freeze route candidate schema.
- [x] Freeze eligible candidate completeness fields.
- [x] Freeze rejected candidate record fields.
- [x] Freeze deterministic selection rule fields.
- [x] Freeze tie-policy fields.
- [x] Freeze immediate affordance rank, consequence rank, and selected rank
      fields.
- [x] Freeze matched/conflicting affordance case fields.
- [x] Freeze prediction basis, derivation policy, source window, observed
      downstream effect, and prediction match status fields.
- [x] Freeze budget validity fields.
- [x] Freeze missing consequence record rejection policy.
- [x] Freeze stale-record policy.
- [x] Freeze artifact-only replay, snapshot/load, order inversion, and
      `runtime_state_used = false` requirements.
- [x] Freeze AP4 gates.
- [x] Freeze negative controls.
- [x] Freeze claim flags forced false.
- [x] State that final AP4 requires Iterations 5-7 controls.

Expected artifacts:

- [x] `outputs/n14_consequence_selection_schema_v1.json`
- [x] `reports/n14_consequence_selection_schema_v1.md`
- [x] `scripts/build_n14_consequence_selection_schema_v1.py`

Output digest:

```text
56a2080a76f941e77e7a822874fa62e292f34452c06f02cbb8e971bccc540217
```

Artifact SHA-256:

```text
outputs/n14_consequence_selection_schema_v1.json 543533cfc4a8c505828393896f32edc76226c0ad9c2983c0bba1246574086dc4
reports/n14_consequence_selection_schema_v1.md 07b83caf31195ac7924fe66066b6d7b784ce940717f5540672d6f02f9e6e7430
scripts/build_n14_consequence_selection_schema_v1.py 3b6638b42d33353e7685f944f4f15b5fc2b49c66fc7bc0e6999231dd4c57711c
```

Acceptance state:

```text
accepted_schema_freeze_no_row_validation
```

Interpretation:

```text
N14 has a frozen AP4 validation contract, but row validation and AP4 support
start only in Iterations 3-7.
```

## Iteration 3. Route Consequence Record Candidate

Acceptance state:

```text
pending_not_run
```

- [ ] Build route consequence records before selection.
- [ ] Record source artifact and report digests for each record.
- [ ] Record prediction basis.
- [ ] Record derivation policy.
- [ ] Record source window.
- [ ] Record support effect descriptor.
- [ ] Record memory effect descriptor.
- [ ] Record regulation effect descriptor.
- [ ] Record observed downstream effect when the bounded horizon is evaluated.
- [ ] Record prediction match status.
- [ ] Record bounded consequence horizon.
- [ ] Record budget cost surface.
- [ ] Confirm no hidden outcome table is used.
- [ ] Confirm no post-hoc consequence scoring is used.
- [ ] Keep AP level provisional.

Expected artifacts:

- [ ] `outputs/n14_route_consequence_records.json`
- [ ] `reports/n14_route_consequence_records.md`
- [ ] `scripts/build_n14_route_consequence_records.py`

## Iteration 4. Consequence-Sensitive Selection Candidate

Acceptance state:

```text
pending_not_run
```

- [ ] Apply deterministic selection rule.
- [ ] Record candidate routes.
- [ ] Record all eligible candidates in the bounded selection window.
- [ ] Record rejected candidate records.
- [ ] Reject missing consequence records.
- [ ] Record selected route.
- [ ] Record selection rationale surface.
- [ ] Record immediate affordance rank.
- [ ] Record consequence rank.
- [ ] Record selected rank.
- [ ] Include a case where immediate affordance is equal or favors a rejected
      route while the consequence vector selects another route.
- [ ] Confirm
      `affordance_consequence_conflict_resolved_by_consequence = true`.
- [ ] Apply explicit tie policy.
- [ ] Record budget validity.
- [ ] Show whether selection depends on downstream consequence vector.
- [ ] Assign only `provisional_ap_level = AP4_candidate`.
- [ ] Do not freeze final AP4 before controls pass.

Expected artifacts:

- [ ] `outputs/n14_consequence_sensitive_selection_candidate.json`
- [ ] `reports/n14_consequence_sensitive_selection_candidate.md`
- [ ] `scripts/build_n14_consequence_sensitive_selection_candidate.py`

## Iteration 5. Hidden Outcome, Post-Hoc, Stale, And Budget Controls

Acceptance state:

```text
pending_not_run
```

- [ ] Hidden outcome table control fails closed.
- [ ] Post-hoc consequence scoring control fails closed.
- [ ] Stale consequence record control fails closed.
- [ ] Budget-invalid route control fails closed.
- [ ] Missing consequence record control fails closed.
- [ ] Candidate-set cherry-picking control fails closed.
- [ ] Tie-policy ambiguity control fails closed.
- [ ] Immediate-affordance-only relabel control fails closed.
- [ ] Matched-affordance conflict control is resolved by consequence evidence.
- [ ] Fixture-label preference control fails closed.
- [ ] Semantic intention relabel control fails closed.
- [ ] Agency relabel control fails closed.
- [ ] Native support relabel control fails closed.
- [ ] Identity acceptance relabel control fails closed.
- [ ] Selfhood relabel control fails closed.
- [ ] Personhood relabel control fails closed.
- [ ] Biological behavior relabel control fails closed.
- [ ] Semantic choice relabel control fails closed.
- [ ] Unrestricted agency relabel control fails closed.

Expected artifacts:

- [ ] `outputs/n14_consequence_control_matrix.json`
- [ ] `reports/n14_consequence_control_matrix.md`
- [ ] `scripts/build_n14_consequence_control_matrix.py`

## Iteration 6. Consequence Perturbation And Replay Matrix

Acceptance state:

```text
pending_not_run
```

- [ ] Support-risk variant changes route ranking only through source-backed
      support consequence input.
- [ ] Memory-effect variant changes route ranking only through source-backed
      memory consequence input.
- [ ] Regulation-deficit variant changes route ranking only through
      source-backed regulation consequence input.
- [ ] Budget-invalid high-consequence route is rejected.
- [ ] Stale consequence record is rejected.
- [ ] Duplicate replay is stable.
- [ ] Artifact-only replay is stable.
- [ ] Snapshot/load replay is stable.
- [ ] Order inversion replay is stable.
- [ ] `runtime_state_used = false`.
- [ ] No producer direct mutation is recorded.

Expected artifacts:

- [ ] `outputs/n14_consequence_perturbation_matrix.json`
- [ ] `reports/n14_consequence_perturbation_matrix.md`
- [ ] `scripts/build_n14_consequence_perturbation_matrix.py`

## Iteration 7. Claim Boundary And AP4 Classification

Acceptance state:

```text
pending_not_run
```

- [ ] Close Hypothesis A.
- [ ] Close Hypothesis B.
- [ ] Close Hypothesis C.
- [ ] Determine supported AP level.
- [ ] Confirm `agency_claim_opened = false`.
- [ ] Confirm `intention_claim_opened = false`.
- [ ] Confirm `semantic_goal_ownership_opened = false`.
- [ ] Confirm `identity_acceptance_opened = false`.
- [ ] Confirm `semantic_choice_opened = false`.
- [ ] Confirm `selfhood_opened = false`.
- [ ] Confirm `personhood_or_biological_behavior_opened = false`.
- [ ] Confirm `unrestricted_agency_opened = false`.
- [ ] Confirm `native_support_opened = false`.
- [ ] Confirm `fully_native_integration_opened = false`.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `src_diff_empty = true`.

Expected artifacts:

- [ ] `outputs/n14_claim_boundary_record.json`
- [ ] `reports/n14_claim_boundary_record.md`
- [ ] `scripts/build_n14_claim_boundary_record.py`

## Iteration 8. N14 Closeout And N15 Handoff

Acceptance state:

```text
pending_not_run
```

- [ ] Freeze final supported AP level.
- [ ] Record final claim ceiling.
- [ ] Record final controls.
- [ ] Record final blockers.
- [ ] Record final N15 handoff.
- [ ] Record whether targeted Phase 8 is optional, required, or deferred.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.

Expected artifacts:

- [ ] `outputs/n14_closeout_and_handoff.json`
- [ ] `reports/n14_closeout_and_handoff.md`
- [ ] `scripts/build_n14_closeout_and_handoff.py`

## Setup Verification

- [x] `git diff --check`
- [x] `git diff -- src`
