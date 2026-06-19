# N19 Native Naturalization Review AP3-AP8 Implementation Checklist

## Initialization

- [x] Create `experiment-N19` branch.
- [x] Create N19 experiment directory.
- [x] Add top-level N19 `README.md`.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add `configs/`, `hypotheses/`, `outputs/`, `reports/`, and `scripts/`
      scaffolds.
- [x] Add hypothesis records.
- [x] Keep N19 scoped as review/classification only.
- [x] Confirm N19 does not open AP9, Phase 8, or native support.

## Global Rules

- [x] Preserve N12 NAT ladder definitions exactly.
- [x] Treat `phase8_ready` as derived from `nat_level = NAT4`.
- [x] Keep `NAT5` and `NAT6` out of scope.
- [x] Require exactly one `primary_disposition` per candidate row.
- [ ] Force unsafe claim flags false in every row.
- [x] Require source digests for all consumed artifacts.
- [x] Use relative paths only.
- [x] Confirm generated records contain no local absolute paths.
- [ ] Confirm `src_diff_empty = true` before closeout.
- [x] Reject native-support claims unless a separate Phase 8 implementation
      exists and validates them.

## Iteration 1. Source Inventory And N12 Ladder Replay

- [x] Build N12-N18 source inventory.
- [x] Confirm all N13-N18 closeout reports and JSON closeouts are present.
- [x] Record source SHA-256 digests and output digests.
- [x] Record each source final supported AP level.
- [x] Record each source final claim ceiling.
- [x] Replay N12 NAT ladder definitions into N19.
- [x] Record N12 `NAT4` readiness gates.
- [x] Confirm direct native support evidence is absent unless source-backed.
- [x] Confirm Phase 8 remains unopened.
- [x] Confirm native support remains false.

Expected artifacts:

```text
outputs/n19_ap3_ap8_source_inventory.json
reports/n19_ap3_ap8_source_inventory.md
scripts/build_n19_ap3_ap8_source_inventory.py
```

Implementation record:

```text
status = passed
artifact = outputs/n19_ap3_ap8_source_inventory.json
report = reports/n19_ap3_ap8_source_inventory.md
script = scripts/build_n19_ap3_ap8_source_inventory.py
command = .venv/bin/python experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/scripts/build_n19_ap3_ap8_source_inventory.py
row_count = 8
output_digest = d8238db4f551ddf43bde51511ab1f2d061f1fda5874875b96c7b68a40c22f19a
artifact_sha256 = 29844f5f77fd06a4d2cd11bb6ae973ff2154760328b010803dd3018a214a477a
report_sha256 = 977b336a159019f6c0dad995f375d8ce728382ed11f9c47738126a4c0b1211ef
script_sha256 = d47de9279ab859fddd5efb2b25c58a23fe7c6d93db6c237e1c8969e474fee6ef
failed_checks = []
phase8_opened = false
native_support_opened = false
ap9_opened = false
```

Iteration 1 records N12 as the method source and NAT ladder source, then
records N13-N18 as AP3-AP8 artifact-level prerequisite sources. The inventory
preserves all source claim ceilings and confirms no direct native support
evidence is opened by the sources.

## Iteration 2. Schema And Control Freeze

- [x] Freeze candidate row schema.
- [x] Freeze `primary_disposition` enum.
- [x] Freeze `nat_level` enum.
- [x] Freeze `phase8_ready` derivation.
- [x] Freeze NAT4 readiness gates.
- [x] Freeze required claim flags.
- [x] Freeze non-RC quantity audit fields.
- [x] Freeze `minimal_producer_code_needed` field.
- [x] Freeze unsafe relabel controls.
- [x] Confirm no candidate row is classified before schema freeze.

Expected artifacts:

```text
outputs/n19_naturalization_schema_v1.json
reports/n19_naturalization_schema_v1.md
scripts/build_n19_naturalization_schema_v1.py
```

Implementation record:

```text
status = passed
artifact = outputs/n19_naturalization_schema_v1.json
report = reports/n19_naturalization_schema_v1.md
script = scripts/build_n19_naturalization_schema_v1.py
command = .venv/bin/python experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/scripts/build_n19_naturalization_schema_v1.py
candidate_rows_classified = false
output_digest = b8e33e97c51603dc73455409b41f858af71d7d7ded8099df2a52e3ce07640935
artifact_sha256 = a5b3afa89b0075cf3805557019788d6bc02d7c3fd3bcb63fe6bdcc244d0d8ccb
report_sha256 = 9e902a79e60b6bd776d127b3ad1c148134ba60d1bea7b5854eeea18cdb3ed3a1
script_sha256 = 94a705bf94479564305da80458f2323bae1be34ba7c28de4b611b5338a452d0e
source_inventory_sha256 = 29844f5f77fd06a4d2cd11bb6ae973ff2154760328b010803dd3018a214a477a
source_inventory_output_digest = d8238db4f551ddf43bde51511ab1f2d061f1fda5874875b96c7b68a40c22f19a
failed_checks = []
phase8_opened = false
native_support_opened = false
ap9_opened = false
```

Iteration 2 freezes schema and controls only. It deliberately leaves candidate
classification for later iterations, so no N13-N18 component is assigned a NAT
level beyond the source inventory yet.

Post-review tightening adds the plan-level `row_decision` enum, replaces two
documentation-style checks with structural assertions over
`phase8_ready_derivation` and `candidate_rows`, and records an explicit
claim-flag-to-blocked-claim mapping so `phase8_opened` is distinguished from
the separate `phase8_implementation` relabel control.

## Iteration 3. AP3-AP5 Lower-Stack Candidate Classification

- [ ] Classify N13 AP3 support/regulation candidates.
- [ ] Classify N14 AP4 consequence/selection candidates.
- [ ] Classify N15 AP5 proxy/target candidates.
- [ ] Distinguish native contract candidates from implementation blockers.
- [ ] Prevent support-seeking from becoming semantic goal ownership.
- [ ] Prevent route selection from becoming semantic choice or intention.
- [ ] Prevent proxy/target formation from becoming semantic goal ownership.
- [ ] Preserve N12 readiness-only context as readiness-only.
- [ ] Record minimal producer code needed for each implementation-gap row.

## Iteration 4. AP6 Boundary Native-Readiness Classification

- [ ] Classify N16 boundary side-state candidates.
- [ ] Classify N16 leakage/separability telemetry candidates.
- [ ] Classify B4/C5 shared-medium geometry and telemetry candidates.
- [ ] Preserve original B4/C5 one-sidedness where source-backed.
- [ ] Prevent boundary evidence from becoming selfhood.
- [ ] Prevent shared-medium evidence from becoming native multi-basin selfhood.
- [ ] Record native boundary telemetry requirements.
- [ ] Record controls for hidden external-state or boundary-label relabels.

## Iteration 5. AP7 Loop Native-Readiness Classification

- [ ] Classify N17 ordered loop trace-leg candidates.
- [ ] Classify loop replay/control telemetry contracts.
- [ ] Classify perturbation-response-recovery loop candidates.
- [ ] Classify resource/support loop candidates.
- [ ] Classify shared-medium loop candidates.
- [ ] Prevent loop evidence from becoming agency.
- [ ] Prevent response from becoming semantic action.
- [ ] Prevent feedback from becoming semantic perception.
- [ ] Keep one-way crossing relabel rejected.
- [ ] Record native loop telemetry requirements.

## Iteration 6. AP8 Horizon And Budget Native-Readiness Classification

- [ ] Classify N18 h4/L5 horizon evidence.
- [ ] Classify N18 budget and replay contracts.
- [ ] Classify N18 cross-axis continuity constraints.
- [ ] Preserve `boundary_to_loop_feedback` as the named bottleneck.
- [ ] Preserve `max_supported_horizon = h4`.
- [ ] Keep h8/h16 extrapolation blocked.
- [ ] Prevent artifact replay from becoming native support.
- [ ] Prevent limited AP8 from becoming general AP8.
- [ ] Record native horizon/budget validation requirements.

## Iteration 7. Phase 8 Readiness Matrix

- [ ] Generate candidate classification matrix.
- [ ] Generate Phase 8 readiness matrix.
- [ ] Require all NAT4 rows to satisfy all NAT4 gates.
- [ ] Keep NAT3 rows below `phase8_ready`.
- [ ] Record blocked rows with distinct blockers.
- [ ] Record implementation-gap rows with minimal producer code needed.
- [ ] Confirm no native implementation claim is made.
- [ ] Confirm all unsafe claim flags remain false.

Expected artifacts:

```text
outputs/n19_candidate_classification_matrix.json
outputs/n19_phase8_readiness_matrix.json
reports/n19_candidate_classification_matrix.md
reports/n19_phase8_readiness_matrix.md
scripts/build_n19_candidate_classification_matrix.py
scripts/build_n19_phase8_readiness_matrix.py
```

## Iteration 8. Closeout And Handoff

- [ ] Close N19 as native-readiness review only.
- [ ] Record final candidate partition.
- [ ] Record Phase 8-ready candidates, if any.
- [ ] Record scaffolds and blockers.
- [ ] Record future Phase 8 implementation tasks without implementing them.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `native_support_opened = false`.
- [ ] Confirm `ap9_opened = false`.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Confirm no absolute paths in generated records.
- [ ] Confirm final claim ceiling is
      `artifact_level_phase8_readiness_review_for_ap3_ap8`.

Expected artifacts:

```text
outputs/n19_closeout_and_handoff.json
reports/n19_closeout_and_handoff.md
scripts/build_n19_closeout_and_handoff.py
```

## Final Blocked Claims

These must remain blocked through closeout:

```text
agency
intention
choice
semantic action
semantic perception
semantic goal ownership
selfhood
identity acceptance
native support
Phase 8 opened
Phase 8 implementation
organism/life behavior
fully native agentic-like integration
unrestricted autonomy
AP9
```
