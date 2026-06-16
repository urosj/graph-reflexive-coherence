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
accepted_route_consequence_records_no_selection
```

- [x] Build route consequence records before selection.
- [x] Record source artifact and report digests for each record.
- [x] Record prediction basis.
- [x] Record derivation policy.
- [x] Record source window.
- [x] Record support effect descriptor.
- [x] Record memory effect descriptor.
- [x] Record regulation effect descriptor.
- [x] Record observed downstream effect when the bounded horizon is evaluated.
- [x] Record prediction match status.
- [x] Record bounded consequence horizon.
- [x] Record budget cost surface.
- [x] Serialize consequence score components.
- [x] Derive consequence rank from serialized score components.
- [x] Record memory-dominant scope and support/regulation route-specific limits.
- [x] Confirm no hidden outcome table is used.
- [x] Confirm no post-hoc consequence scoring is used.
- [x] Keep AP level provisional.

Expected artifacts:

- [x] `outputs/n14_route_consequence_records.json`
- [x] `reports/n14_route_consequence_records.md`
- [x] `scripts/build_n14_route_consequence_records.py`

Output digest:

```text
9eef9c0bbcfd64004915259964ddcbb39efb32563fec5975a6bb30684d83d253
```

Artifact SHA-256:

```text
outputs/n14_route_consequence_records.json 59efc5980f1dce63438f1c5f054ce8feab9cf818fb63ee718b07b7934933470d
reports/n14_route_consequence_records.md 82a7ed080b89b1228eb42fe93e6289c48d49a5f426dad46caea9fe7f03847bca
scripts/build_n14_route_consequence_records.py 74f0ddfb9a852f48bd1d8b1e7e112b6c3e210409d1c0b3e5db1da9b342d7b81d
```

Interpretation:

```text
N14 has pre-selection consequence records and an explicit
affordance/consequence conflict. Consequence ranks are derived from serialized
memory-dominant score components. Support and regulation sources are compatible
but not route-specific in this iteration. It does not yet have a selected route
or AP4 support.
```

## Iteration 4. Consequence-Sensitive Selection Candidate

Acceptance state:

```text
accepted_consequence_sensitive_selection_candidate_pending_controls
```

- [x] Apply deterministic selection rule.
- [x] Record candidate routes.
- [x] Record all eligible candidates in the bounded selection window.
- [x] Record rejected candidate records.
- [x] Reject missing consequence records.
- [x] Record selected route.
- [x] Record selection rationale surface.
- [x] Record immediate affordance rank.
- [x] Record consequence rank.
- [x] Confirm consequence rank is derived from serialized score components.
- [x] Record selected rank.
- [x] Record explicit `selection_status_record`.
- [x] Include a case where immediate affordance is equal or favors a rejected
      route while the consequence vector selects another route.
- [x] Confirm
      `affordance_consequence_conflict_resolved_by_consequence = true`.
- [x] Apply explicit tie policy.
- [x] Record budget validity.
- [x] Show whether selection depends on downstream consequence vector.
- [x] Record that missing/stale/budget controls are policy-only until
      Iteration 5 adversarial controls.
- [x] Assign only `provisional_ap_level = AP4_candidate`.
- [x] Do not freeze final AP4 before controls pass.

Expected artifacts:

- [x] `outputs/n14_consequence_sensitive_selection_candidate.json`
- [x] `reports/n14_consequence_sensitive_selection_candidate.md`
- [x] `scripts/build_n14_consequence_sensitive_selection_candidate.py`

Result:

```text
Status: passed.
Output digest: d867b665e3ca96df4a78576b89fb2b89a19ff2761f0099e48d057f00c6b8cfdd
Selected route: route_b
Rejected route: route_a
Provisional AP level: AP4_candidate
Final AP4 supported: false
```

Artifact SHA-256:

```text
outputs/n14_consequence_sensitive_selection_candidate.json da0d2e070fa34098d14673714f2d23ea3f3041821c2a203798c206786e07cde3
reports/n14_consequence_sensitive_selection_candidate.md 45d32f1ca30cbe95b262e650ca9c627e9c6dc858b2f06e202d60490036070cca
scripts/build_n14_consequence_sensitive_selection_candidate.py 8421a376d2f46f7a897a81aa13aa75cb63afa82304458420900dc23c9d94399f
```

Interpretation:

```text
N14 now has a provisional consequence-sensitive selection candidate: the
deterministic artifact-only rule selects route_b by derived, memory-dominant
consequence rank while immediate affordance favors the rejected route_a. This
closes only the selection-candidate layer. Missing/stale/budget controls are
recorded as policies only until Iteration 5 adversarial controls. Final AP4
remains pending until controls, replay/snapshot checks, and claim-boundary
classification pass.
```

## Iteration 5. Hidden Outcome, Post-Hoc, Stale, And Budget Controls

Acceptance state:

```text
accepted_adversarial_control_matrix_pending_replay
```

- [x] Hidden outcome table control fails closed.
- [x] Post-hoc consequence scoring control fails closed.
- [x] Fabricated consequence rank source control fails closed.
- [x] Stale consequence record control fails closed.
- [x] Budget-invalid route control fails closed.
- [x] Missing consequence record control fails closed.
- [x] Candidate-set cherry-picking control fails closed.
- [x] Tie-policy ambiguity control fails closed.
- [x] Immediate-affordance-only relabel control fails closed.
- [x] Matched-affordance conflict control is resolved by consequence evidence.
- [x] Fixture-label preference control fails closed.
- [x] Semantic intention relabel control fails closed.
- [x] Agency relabel control fails closed.
- [x] Native support relabel control fails closed.
- [x] Identity acceptance relabel control fails closed.
- [x] Selfhood relabel control fails closed.
- [x] Personhood relabel control fails closed.
- [x] Biological behavior relabel control fails closed.
- [x] Semantic choice relabel control fails closed.
- [x] Semantic goal ownership relabel control fails closed.
- [x] Unrestricted agency relabel control fails closed.
- [x] Budget validity is checked before ranking.
- [x] Consequence-rank source is validated before ranking.
- [x] Tie-policy removal requires explicit metadata.

Expected artifacts:

- [x] `outputs/n14_consequence_control_matrix.json`
- [x] `reports/n14_consequence_control_matrix.md`
- [x] `scripts/build_n14_consequence_control_matrix.py`

Result:

```text
Status: passed.
Output digest: d9ff2a2ff515eec26226048b25a990faa9f7c7ba94cea14ef833a89f8d9292e7
Control records: 21
Negative controls blocked: 20
Matched conflict selected route: route_b
Final AP4 supported: false
```

Artifact SHA-256:

```text
outputs/n14_consequence_control_matrix.json 9d7153c031665f8325502ee9241048f8a2ac43cecf1b47ecefa67d715d1d59c0
reports/n14_consequence_control_matrix.md 0797b2731145e88db360e9cd8cbcc817e0bf89fc6795be14848658a68e285a18
scripts/build_n14_consequence_control_matrix.py a4631658fec1e91854d284f0c26f6e16b1004115b4b96d0c885a0090b603e7fd
```

Interpretation:

```text
Iteration 5 executes adversarial controls for the provisional memory-dominant
AP4 candidate. The negative controls fail closed with distinct blockers,
including fabricated consequence-rank source rejection. The clean
matched-conflict case still selects route_b by consequence evidence. The
selection contract now checks budget validity before ranking, validates
`consequence_rank_source` before ranking, and requires explicit tie-policy
removal metadata. This closes the control-matrix layer only. Final AP4 remains
pending until Iteration 6 replay/perturbation and Iteration 7 claim-boundary
classification.
```

## Iteration 6. Consequence Perturbation And Replay Matrix

Acceptance state:

```text
accepted_perturbation_replay_matrix_pending_claim_classification
```

- [x] Support-risk variant changes route ranking only through source-backed
      support consequence input.
- [x] Memory-effect variant changes route ranking only through source-backed
      memory consequence input.
- [x] Regulation-deficit variant changes route ranking only through
      source-backed regulation consequence input.
- [x] Budget-invalid high-consequence route is rejected.
- [x] Stale consequence record is rejected.
- [x] Duplicate replay is stable.
- [x] Artifact-only replay is stable.
- [x] Artifact-only replay uses filesystem JSON roundtrip.
- [x] Snapshot/load replay is stable.
- [x] Snapshot/load replay uses filesystem JSON roundtrip.
- [x] Order inversion replay is stable.
- [x] Budget validity is checked before ranking.
- [x] Consequence-rank source is validated before ranking.
- [x] `runtime_state_used = false`.
- [x] No producer direct mutation is recorded.

Expected artifacts:

- [x] `outputs/n14_consequence_perturbation_matrix.json`
- [x] `reports/n14_consequence_perturbation_matrix.md`
- [x] `scripts/build_n14_consequence_perturbation_matrix.py`

Result:

```text
Status: passed.
Output digest: 3d207f963e6d3ed049c01bfcf75235c2cb8780d79e0cbe14d8ab349d7b6674e9
Baseline selected route: route_b
Support-risk selected route: route_a
Memory-effect selected route: route_a
Regulation-deficit selected route: route_a
Budget-invalid blocker: budget_invalid_route_blocked
Stale-record blocker: stale_consequence_record_blocked
Replay stable: true
Artifact-only filesystem replay: true
Snapshot/load filesystem replay: true
Final AP4 supported: false
```

Artifact SHA-256:

```text
outputs/n14_consequence_perturbation_matrix.json 0405d0da3ca05889b3adbc12b8c6055b224155de8dd04f7bf9c48a7f18f6adcf
reports/n14_consequence_perturbation_matrix.md 3520680e9eb00d0d18510b1db6a49c527dd22047141bdcb05a79af8713b5687e
scripts/build_n14_consequence_perturbation_matrix.py 2a69e04bfd3ab7d6f076f75cb48e536c56a564d74a00b21ee97f7f1580679b5a
```

Interpretation:

```text
Iteration 6 handles the Iteration 5 control-clean candidate by testing
source-sensitive perturbations and replay stability. Route selection changes
only when serialized source-backed support, memory, or regulation consequence
inputs change. Unchanged inputs replay stably across duplicate, artifact-only,
snapshot/load, and order-inverted runs. Artifact-only and snapshot/load replay
roundtrip through filesystem JSON artifacts. Final AP4 remains pending until
Iteration 7 claim-boundary classification.
```

## Iteration 6-A. Observed Route-Specific Consequence Probe

Acceptance state:

```text
accepted_observed_route_specific_memory_probe_support_regulation_generic
```

- [x] Record `route_a` observed downstream memory consequence record.
- [x] Record `route_b` observed downstream memory consequence record.
- [x] Record that Iteration 6-A uses N08 MEM3 rather than MEM6 because MEM3
      contains the memory-surface key snapshot needed for observed
      route-specific memory rows.
- [x] Use the same source-window policy.
- [x] Use the same budget accounting.
- [x] Use the same bounded horizon.
- [x] Use the same selection rule.
- [x] Derive route-specific consequence components from observed
      route-contingent records.
- [x] Do not assign post-hoc score or rank.
- [x] Block route-label swap against the memory-surface digest mapping.
- [x] Block generic support/regulation reuse.
- [x] Block missing route observation.
- [x] Block stale route-specific consequence.
- [x] Block budget-invalid observed route.
- [x] Block post-hoc score/rank.
- [x] Record observed route-specific support as unsupported/generic.
- [x] Record observed route-specific regulation as unsupported/generic.

Expected artifacts:

- [x] `outputs/n14_observed_route_specific_consequence_probe.json`
- [x] `reports/n14_observed_route_specific_consequence_probe.md`
- [x] `scripts/build_n14_observed_route_specific_consequence_probe.py`

Result:

```text
Status: passed.
Output digest: 7f75ab3c2601a483938ba333676ef0435412ea7d5681910edcdc31c39c5a5a70
Observed memory top route: route_b
Observed route-specific memory supported: true
Observed route-specific support supported: false
Observed route-specific regulation supported: false
Supported closeout scope: artifact_level_ap4_memory_dominant_consequence_sensitive_route_selection_candidate
Final AP4 supported: false
```

Artifact SHA-256:

```text
outputs/n14_observed_route_specific_consequence_probe.json 00fd138e88c0bc19341c605601c9dd070796a63903fb0dc8ef3036f9a363a7f0
reports/n14_observed_route_specific_consequence_probe.md d1eb76781f891d9d5c270642ee1f2ed42dcc389c3efabe0826435912abef8181
scripts/build_n14_observed_route_specific_consequence_probe.py 512b55917937a6f634b8ccefe08677e4c9e5db698936bb9dd7582d8c14645786
```

Interpretation:

```text
Iteration 6-A supports observed route-specific memory consequence evidence
under the same N08 MEM3 update-window policy. It does not support observed
route-specific support or regulation consequence evidence because the available
N09/N13 sources are generic lanes, not route-contingent route observations.
This source-window switch is intentional: N08 MEM3 supplies the observed
memory-surface key snapshot, while MEM6 remains the Iteration 3-6 replay source.
Iteration 7 should classify AP4 with a memory-dominant claim ceiling unless new
route-specific support/regulation sources are added.
```

## Iteration 6-B. Route-Conditioned Support And Regulation Consequence Probe

Acceptance state:

```text
accepted_route_conditioned_support_regulation_probe_no_route_specific_support_regulation
```

- [x] Require `route_a` observed support consequence row.
- [x] Require `route_b` observed support consequence row.
- [x] Require `route_a` observed regulation consequence row.
- [x] Require `route_b` observed regulation consequence row.
- [x] Require route IDs in observed support/regulation rows.
- [x] Require same source-window policy.
- [x] Require same budget accounting.
- [x] Require same selection rule.
- [x] Record generic N13 support lanes as available but not route-conditioned.
- [x] Record generic N09 regulation summary as available but not
      route-conditioned.
- [x] Block route-label swap.
- [x] Block generic source reuse.
- [x] Block missing route observation.
- [x] Block stale route observation.
- [x] Block budget-invalid consequence.
- [x] Block post-hoc route conditioning.
- [x] Execute 6-B controls through adversarial variants and a validator rather
      than declaring blockers directly.
- [x] Preserve memory-dominant closeout ceiling.

Expected artifacts:

- [x] `outputs/n14_route_conditioned_support_regulation_probe.json`
- [x] `reports/n14_route_conditioned_support_regulation_probe.md`
- [x] `scripts/build_n14_route_conditioned_support_regulation_probe.py`

Result:

```text
Status: passed.
Output digest: e309f40822f782d5d5dba684656c4a4dd133b649ce815f72b253c38957565f6e
Observed route-conditioned support supported: false
Observed route-conditioned regulation supported: false
Stronger support/regulation closeout available: false
Supported closeout scope: artifact_level_ap4_memory_dominant_consequence_sensitive_route_selection_candidate
Final AP4 supported: false
```

Artifact SHA-256:

```text
outputs/n14_route_conditioned_support_regulation_probe.json 2f5c6176e09a02eb2afb83dc9d83a98de743587609f9cf6c010cf3e8ef91ffc2
reports/n14_route_conditioned_support_regulation_probe.md 9ab0be6d6fa90e179aebffd8f185249c0d50ab7c805f50f702e89da98f3ec4cf
scripts/build_n14_route_conditioned_support_regulation_probe.py 85c5f0bfc23d53178af074be0bf56c97a989d35117b968ad56170edab7ad1921
```

Interpretation:

```text
Iteration 6-B directly tests the remaining support/regulation ambiguity. It
does not find observed route-conditioned support or regulation consequence
records in the current N09/N13 sources. Generic source compatibility remains
useful context but is blocked from route-conditioned AP4 evidence by executed
adversarial controls. N14 should therefore close, if Iteration 7 supports AP4,
as a memory-dominant consequence-sensitive route selection candidate unless new
route-conditioned support/regulation artifacts are created.
```

## Iteration 6-C. Route-Conditioned Followout Probe

Acceptance state:

```text
accepted_constructed_route_conditioned_support_regulation_followout
```

- [x] Serialize route IDs before support/regulation axis scoring.
- [x] Apply one route-conditioned followout policy to `route_a` and `route_b`.
- [x] Record constructed route-conditioned support followout rows.
- [x] Record constructed route-conditioned regulation followout rows.
- [x] Derive support components from serialized N13-calibrated followout rows.
- [x] Derive regulation components from serialized N09-calibrated followout
      rows.
- [x] Confirm support components differ by route.
- [x] Confirm regulation components differ by route.
- [x] Derive followout rank from serialized components.
- [x] Block route-label swap.
- [x] Block generic source reuse.
- [x] Block missing route followout.
- [x] Block stale source window.
- [x] Block budget-invalid followout.
- [x] Block post-hoc route conditioning.
- [x] Block fixture-label assignment.
- [x] Block equal-effect null followout.
- [x] Block support-only equal-effect null followout.
- [x] Block regulation-only equal-effect null followout.
- [x] Equal-effect null blocks either an undifferentiated support axis or an
      undifferentiated regulation axis.
- [x] Preserve the Iteration 6-B upstream-source boundary.
- [x] Confirm the positive is constructed artifact-level followout evidence,
      not upstream observed N09/N13 route-conditioned evidence.

Expected artifacts:

- [x] `outputs/n14_route_conditioned_followout_probe.json`
- [x] `reports/n14_route_conditioned_followout_probe.md`
- [x] `scripts/build_n14_route_conditioned_followout_probe.py`

Result:

```text
Status: passed.
Output digest: 387faa187068737884b67723e21c2c8068e38c337b486d8146cbd3261e73cb29
Constructed route-conditioned support followout supported: true
Constructed route-conditioned regulation followout supported: true
Observed upstream route-conditioned support/regulation supported: false
Top followout route: route_b
Supported closeout scope: artifact_level_ap4_support_memory_regulation_consequence_sensitive_route_selection_candidate
Final AP4 supported: false
```

Artifact SHA-256:

```text
outputs/n14_route_conditioned_followout_probe.json 450dd43f4f35a7ba375fa0b197c34c11a0ddac324b2d26660d75c98b201ccaa4
reports/n14_route_conditioned_followout_probe.md 6b25d12a8f8cf9412d317ebb398972be68b19f9ae8cc8f683b59fbf69316533f
scripts/build_n14_route_conditioned_followout_probe.py 8c3822fe5108d5b7207bacb8c556f02c6a54a40f057eb7290bf36dd85b383b7b
```

Interpretation:

```text
Iteration 6-C gets the guarded positive that Iteration 6-B could not: N14 can
construct route-conditioned support and regulation followout rows with route IDs
present before scoring, and those components differ by route. This gives
Iteration 7 a basis for a broader support/memory/regulation AP4 candidate, but
only with a clear caveat: the support/regulation evidence is constructed N14
followout evidence, not upstream observed route-conditioned N09/N13 evidence,
and it is not native support, intention, semantic choice, or agency. The
support-only, regulation-only, and combined equal-effect null controls now block
if either support or regulation is undifferentiated, and mutated scores/ranks
are recomputed before validation.
```

## Iteration 7. Claim Boundary And AP4 Classification

Acceptance state:

```text
accepted_ap4_classification_claim_boundary_clean_pending_closeout
```

- [x] Close Hypothesis A.
- [x] Close Hypothesis B.
- [x] Close Hypothesis C.
- [x] Determine supported AP level.
- [x] Confirm `agency_claim_opened = false`.
- [x] Confirm `intention_claim_opened = false`.
- [x] Confirm `semantic_goal_ownership_opened = false`.
- [x] Confirm `identity_acceptance_opened = false`.
- [x] Confirm `semantic_choice_opened = false`.
- [x] Confirm `selfhood_opened = false`.
- [x] Confirm `personhood_or_biological_behavior_opened = false`.
- [x] Confirm `unrestricted_agency_opened = false`.
- [x] Confirm `native_support_opened = false`.
- [x] Confirm `fully_native_integration_opened = false`.
- [x] Confirm `phase8_opened = false`.
- [x] Confirm `src_diff_empty = true`.
- [x] Confirm boundary evidence references are typed.
- [x] Confirm boundary control references use canonical control IDs.
- [x] Confirm legacy mixed `source_controls` field is absent.

Expected artifacts:

- [x] `outputs/n14_claim_boundary_record.json`
- [x] `reports/n14_claim_boundary_record.md`
- [x] `scripts/build_n14_claim_boundary_record.py`

Result:

```text
Status: passed.
Output digest: 828a553f428245c7fff758c519014fe22c4a1fe924b441f0c066dcf09747b2ea
Classified AP level: AP4
AP4 classification supported: true
Provisional AP level: AP4_candidate_boundary_clean_pending_closeout
Final AP4 supported: false
Final AP freeze pending Iteration 8: true
Hypothesis A acceptance state: supported
Hypothesis B acceptance state: supported
Hypothesis C acceptance state: supported
Phase 8 opened: false
Native support opened: false
```

Artifact SHA-256:

```text
outputs/n14_claim_boundary_record.json 156e76ffd0186dbf613f6754eb84d4b06dc7cc7f6512075989502d70194e8371
reports/n14_claim_boundary_record.md f17e03d0563c8881a29065a31c3a1ddcde57fb1ea15cb8dcf8bd104390c79767
scripts/build_n14_claim_boundary_record.py 31ad2b7480f808630967f483bdbefac611f4171f4178287f51da91bc7825416b
```

Interpretation:

```text
Iteration 7 supports all three hypotheses and classifies N14 as
boundary-clean artifact-level AP4, pending Iteration 8 final freeze. The AP4
scope is observed route-specific memory plus constructed route-conditioned
support/regulation followout. The upstream N09/N13 route-conditioned
support/regulation gap remains explicit, and all intention, semantic choice,
semantic goal ownership, identity acceptance, selfhood, personhood, biological
behavior, agency, unrestricted agency, native support, fully native
integration, and Phase 8 claims remain blocked.
```

## Iteration 8. N14 Closeout And N15 Handoff

Acceptance state:

```text
closed_claim_clean_ap4_artifact_level_consequence_sensitive_route_selection
```

- [x] Freeze final supported AP level.
- [x] Record final claim ceiling.
- [x] Record final controls.
- [x] Record final blockers.
- [x] Record final N15 handoff.
- [x] Record whether targeted Phase 8 is optional, required, or deferred.
- [x] Confirm `src_diff_empty = true`.
- [x] Confirm `native_supported_flags = false`.
- [x] Confirm `phase8_opened = false`.
- [x] Confirm `fully_native_integration_opened = false`.
- [x] Confirm all source rows receive specific final roles.

Expected artifacts:

- [x] `outputs/n14_closeout_and_handoff.json`
- [x] `reports/n14_closeout_and_handoff.md`
- [x] `scripts/build_n14_closeout_and_handoff.py`

Result:

```text
Status: passed.
Output digest: 494da082bfe804cac1b683469d2b8e2f4e7c5f8574fc77ded7ce945c83a1422a
Final supported AP level: AP4
Final AP4 supported: true
Final claim ceiling: artifact_level_ap4_consequence_sensitive_route_selection_candidate_with_constructed_route_conditioned_support_regulation_followout
Final scope: observed route-specific memory plus constructed route-conditioned support/regulation followout
Upstream observed route-conditioned support/regulation supported: false
Targeted Phase 8 required before N15: false
Native support opened: false
Phase 8 opened: false
Fully native integration opened: false
Generic source row classifications: false
```

Artifact SHA-256:

```text
outputs/n14_closeout_and_handoff.json 47d794a5fd53e96e9017d5cbdcf8959d5372d6dfa52467661a0dc14661eadbc1
reports/n14_closeout_and_handoff.md 5f058dd6802065954e2c4e0f8d663d93fb8d55b2520a43edafbf79b3a14e1c7a
scripts/build_n14_closeout_and_handoff.py 6e7258e00e6ff762c53bfd41ddeb4c8161fa7a3df7860ffb1baf3a114939840d
```

Interpretation:

```text
Iteration 8 closes N14 as a claim-clean artifact-level AP4 consequence-
sensitive route selection experiment. It freezes the final supported AP level
at AP4, records all three hypotheses as supported, preserves the constructed
followout versus upstream observed support/regulation distinction, and hands
off to N15 endogenous proxy formation. Targeted Phase 8 remains optional and
deferred, not required before N15. It carries forward
`fully_native_integration_opened = false` and assigns a specific final role to
every Iteration 1 source row.
```

## Setup Verification

- [x] `git diff --check`
- [x] `git diff -- src`
