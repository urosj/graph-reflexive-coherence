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

- [x] Classify N13 AP3 support/regulation candidates.
- [x] Classify N14 AP4 consequence/selection candidates.
- [x] Classify N15 AP5 proxy/target candidates.
- [x] Distinguish native contract candidates from implementation blockers.
- [x] Prevent support-seeking from becoming semantic goal ownership.
- [x] Prevent route selection from becoming semantic choice or intention.
- [x] Prevent proxy/target formation from becoming semantic goal ownership.
- [x] Preserve N12 readiness-only context as readiness-only.
- [x] Record minimal producer code needed for each implementation-gap row.

Expected artifacts:

```text
outputs/n19_lower_stack_candidate_classification.json
reports/n19_lower_stack_candidate_classification.md
scripts/build_n19_lower_stack_candidate_classification.py
```

Implementation record:

```text
status = passed
artifact = outputs/n19_lower_stack_candidate_classification.json
report = reports/n19_lower_stack_candidate_classification.md
script = scripts/build_n19_lower_stack_candidate_classification.py
command = .venv/bin/python experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/scripts/build_n19_lower_stack_candidate_classification.py
row_count = 6
output_digest = b0c2a1ec62143b1108034be99174176fa87f782baa51a18811dd5ea28aa76836
artifact_sha256 = 61c783065cf8fa7828944fd99b71c717a5ebc46cadbb95dc85c198beadac3c1a
report_sha256 = a3d9fa4829c57ab6d7253cf83652e312b63140070bde8a9dd3d2f728f711c189
script_sha256 = 59dfde4b21400ee130cbf9a8a47fd1ce37d1d2b3cbf8b3f9fde5e34797f3c366
failed_checks = []
phase8_opened = false
native_support_opened = false
ap9_opened = false
```

Iteration 3 classifies the AP3-AP5 lower stack without opening Phase 8 or
native support. The conservative partition is:

```text
N13 support-margin / response-magnitude policy = NAT4, phase8_ready
N14 route consequence selection telemetry = NAT3, native contract candidate
N14 constructed followout as observed/native support = blocked
N15 proxy derivation policy = NAT3, native contract candidate
N13/N15 semantic-goal, choice, agency, selfhood, and native-support relabels = rejected
```

N13 reaches `NAT4` because the source-current support margin, threshold
deficit, bounded response schedule, budget debit surface, default-off policy
separation, replay requirements, and claim controls are all explicit. This is
only Phase 8 readiness; it is not native support and it does not implement the
policy.

N14 remains `NAT3` because the route consequence-selection contract is clear,
but the stronger support/regulation route-conditioned input is blocked: current
sources have constructed followout and generic support/regulation compatibility,
not upstream observed route-conditioned support/regulation rows.

N15 remains `NAT3` because runtime-derived proxy/target formation is
source-backed and control-clean at artifact level, but its lower-stack inputs
are still artifact surfaces. N12 readiness remains readiness-only, with the N15
readiness-context weight fixed at `0.0`, so it is not relabeled as native
support.

## Iteration 4. AP6 Boundary Native-Readiness Classification

- [x] Classify N16 boundary side-state candidates.
- [x] Classify N16 leakage/separability telemetry candidates.
- [x] Classify B4/C5 shared-medium geometry and telemetry candidates.
- [x] Preserve original B4/C5 one-sidedness where source-backed.
- [x] Prevent boundary evidence from becoming selfhood.
- [x] Prevent shared-medium evidence from becoming native multi-basin selfhood.
- [x] Record native boundary telemetry requirements.
- [x] Record controls for hidden external-state or boundary-label relabels.

Expected artifacts:

```text
outputs/n19_ap6_boundary_native_readiness_classification.json
reports/n19_ap6_boundary_native_readiness_classification.md
scripts/build_n19_ap6_boundary_native_readiness_classification.py
```

Implementation record:

```text
status = passed
artifact = outputs/n19_ap6_boundary_native_readiness_classification.json
report = reports/n19_ap6_boundary_native_readiness_classification.md
script = scripts/build_n19_ap6_boundary_native_readiness_classification.py
command = .venv/bin/python experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/scripts/build_n19_ap6_boundary_native_readiness_classification.py
row_count = 6
output_digest = 74bf51bfa5b4e581baa777b3133d2e7de1706d9fb2229995a81a2432ccb46e0f
artifact_sha256 = ad4ad341a71ee94d5710249d26a60479379929f16b766b126f2ad3816b17e449
report_sha256 = 314cdd05fca615626e34037cea1078e834321f82a0642126a277aa56d97f02b9
script_sha256 = 9be6dfc3767c8c986ce61af58ce5392fb31e87c9b3998c20e98fee7b05716b49
failed_checks = []
phase8_opened = false
native_support_opened = false
ap9_opened = false
```

Iteration 4 classifies the AP6 boundary stack without opening Phase 8,
native support, selfhood, identity acceptance, agency, or organism/life
claims. The conservative partition is:

```text
N16 boundary side-state and edge telemetry = NAT4, phase8_ready
N16 leakage / support / coherence / separability requirement telemetry = NAT4, phase8_ready
N16 B3_C4 breach/reclosure boundary telemetry = NAT4, phase8_ready
Original N16 B4_C5 shared-medium paired-separability contract gap = NAT3
Original N16 B4_C5 reverse-perspective backfill = blocked
Boundary/selfhood/native-support/native-multi-basin-selfhood relabels = rejected
```

The NAT4 rows are telemetry readiness only. They name default-off boundary
side-state, edge, leakage/separability, and breach/reclosure telemetry
surfaces. They do not implement native boundary state, native support, selfhood,
or autonomous repair.

The original `B4_C5` row is preserved as source-backed one-sided shared-medium
geometry: basin A is internal, neighbor basin and shared medium are external,
basin separation is `0.74`, boundary exclusivity is `0.73`, shared-medium
leakage is `0.108`, and merge pressure is `0.14`. Because original N16 lacks
reverse-side internal nodes, reverse support/coherence metrics, and reverse
boundary edges, it remains `NAT3` for paired/native shared-medium separability.
Later derived paired evidence must not be backfilled into original N16
provenance.

The B4/C5 NAT3 row names a future paired-separability telemetry contract gap,
not existing paired evidence. Minimal producer work must add reverse-side
state, reverse support/coherence metrics, reverse boundary edges, reverse
later-feedback traces, and two-sided separability/leakage/merge controls.

## Iteration 5. AP7 Loop Native-Readiness Classification

- [x] Classify N17 ordered loop trace-leg candidates.
- [x] Classify loop replay/control telemetry contracts.
- [x] Classify perturbation-response-recovery loop candidates.
- [x] Classify resource/support loop candidates.
- [x] Classify shared-medium loop candidates.
- [x] Prevent loop evidence from becoming agency.
- [x] Prevent response from becoming semantic action.
- [x] Prevent feedback from becoming semantic perception.
- [x] Keep one-way crossing relabel rejected.
- [x] Record native loop telemetry requirements.

Expected artifacts:

```text
outputs/n19_ap7_loop_native_readiness_classification.json
reports/n19_ap7_loop_native_readiness_classification.md
scripts/build_n19_ap7_loop_native_readiness_classification.py
```

Implementation record:

```text
status = passed
artifact = outputs/n19_ap7_loop_native_readiness_classification.json
report = reports/n19_ap7_loop_native_readiness_classification.md
script = scripts/build_n19_ap7_loop_native_readiness_classification.py
command = .venv/bin/python experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/scripts/build_n19_ap7_loop_native_readiness_classification.py
row_count = 7
output_digest = 5da747e86b49ec88921ed204a4af3dc369acf31c4696fce403f18c53c870845c
artifact_sha256 = 8144c3b8c3d94f553b8ce9c85a2bf97222eee6cded317613c1200283c0b7c9fa
report_sha256 = d117bd94b6b938b168d1e9760ff7bb0b8af145ebf30e4d8b32541c32b7d2e0b9
script_sha256 = 84cdbc7f69972b46489efd327382ffdcb2201ae06b342c18b69fc2602cf621d7
failed_checks = []
phase8_opened = false
native_support_opened = false
ap9_opened = false
```

Iteration 5 classifies N17 AP7 evidence into loop-native-readiness surfaces
without opening Phase 8 or native support. The partition is:

```text
N17 ordered trace-leg telemetry = NAT4, phase8_ready
N17 replay/order/control telemetry = NAT4, phase8_ready
N17 perturbation-response-recovery loop telemetry = NAT4, phase8_ready
N17 resource/support modulation loop telemetry = NAT4, phase8_ready
N17 scoped shared-medium loop telemetry = NAT4, phase8_ready
Original B4_C5/general shared-medium reverse replay = blocked
Agency/action/perception/native-support relabels = rejected
```

The shared-medium row is deliberately scoped. It records local one-sided,
local paired-perspective, and B4_C5-derived two-cycle candidates as source
backed, but preserves that original B4_C5 reverse-perspective replay and
general symmetric shared-medium G6 remain blocked. Later paired or derived
evidence cannot rewrite original B4_C5 provenance.

The AP7 rows support telemetry-readiness only: ordered trace legs, replay and
control records, loop-family envelopes, and claim-boundary checks. They do not
turn response into semantic action, feedback into semantic perception, loop
closure into agency, or resource/support modulation into native support.

The I5 B4/C5/general shared-medium row is `NAT2` because the blocker evidence
is replayable and source-backed. It is not readiness: `row_decision = blocked`
and `phase8_ready = false`. The one-way crossing guard is explicit:
`one_way_crossing_trace != closed_boundary_engagement_loop`.

## Iteration 6. AP8 Horizon And Budget Native-Readiness Classification

- [x] Classify N18 h4/L5 horizon evidence.
- [x] Classify N18 budget and replay contracts.
- [x] Classify N18 cross-axis continuity constraints.
- [x] Preserve `boundary_to_loop_feedback` as the named bottleneck.
- [x] Preserve `max_supported_horizon = h4`.
- [x] Keep h8/h16 extrapolation blocked.
- [x] Prevent artifact replay from becoming native support.
- [x] Prevent limited AP8 from becoming general AP8.
- [x] Record native horizon/budget validation requirements.

Expected artifacts:

```text
outputs/n19_ap8_horizon_budget_native_readiness_classification.json
reports/n19_ap8_horizon_budget_native_readiness_classification.md
scripts/build_n19_ap8_horizon_budget_native_readiness_classification.py
```

Implementation record:

```text
status = passed
artifact = outputs/n19_ap8_horizon_budget_native_readiness_classification.json
report = reports/n19_ap8_horizon_budget_native_readiness_classification.md
script = scripts/build_n19_ap8_horizon_budget_native_readiness_classification.py
command = .venv/bin/python experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/scripts/build_n19_ap8_horizon_budget_native_readiness_classification.py
row_count = 5
output_digest = 5423c24806dba6df1344c667646fa72d329ce939857b9577b369fc9fe4c558b3
artifact_sha256 = be1b9e3288e2d3a5c4999a827b8024b2ac14ab5b6bc37ea504caff5709920c68
report_sha256 = 295dda108232f85d03fb12aeac9bd3b1c699c4a4319054db95d04f8d2a90d9df
script_sha256 = 14b8caf45125ed0a15f17aaa9b7fc2cef5d28418c537e5407bfa1084a02e6952
failed_checks = []
phase8_opened = false
native_support_opened = false
ap9_opened = false
```

Iteration 6 classifies N18 AP8 evidence into horizon/budget native-readiness
surfaces without opening Phase 8 or native support. The partition is:

```text
N18 limited h4 horizon-envelope telemetry = NAT4, phase8_ready
N18 long-horizon budget/replay/control telemetry = NAT4, phase8_ready
N18 cross-axis continuity and boundary_to_loop_feedback bottleneck telemetry = NAT4, phase8_ready
N18 h8/h16/general AP8 extrapolation = blocked
N18 native-support/agency/semantic-action/semantic-perception relabels = rejected
```

The AP8 rows are validation-readiness only. They preserve
`final_supported_ap_level = AP8_limited_artifact_candidate`,
`max_supported_horizon = h4`, `highest_positive_stress_ladder_rung = L5`,
and `principal_bottleneck_link = boundary_to_loop_feedback` with score `0.8`.
The h8 partial row, h16 rejected row, and general AP8 extrapolation remain
blocked. Artifact replay is explicitly not native support.

Post-audit tightening records `boundary_to_loop_feedback` as a tracked
Phase 8 validation requirement, not as a solved bottleneck.

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
