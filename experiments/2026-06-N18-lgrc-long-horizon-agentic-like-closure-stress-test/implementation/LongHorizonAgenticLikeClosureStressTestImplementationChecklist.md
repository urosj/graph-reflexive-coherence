# N18 Long-Horizon Agentic-Like Closure Stress Test Implementation Checklist

## Global Rules

- [ ] Preserve the N18 claim boundary.
- [ ] Do not edit `src/*` unless a separate Phase 8 task explicitly opens.
- [ ] Use `.venv/bin/python` for local script/test runs.
- [ ] Use source-backed artifacts and SHA-256 digests.
- [ ] Record all paths as portable relative paths.
- [ ] Do not promote N17 AP7 closed loop evidence into agency, semantic
      action, semantic perception, native support, or unrestricted autonomy.
- [ ] Do not promote N16 AP6 boundary evidence into selfhood, identity
      acceptance, agency, native support, or closed-loop support by relabel.
- [ ] Do not promote N15 AP5 proxy evidence into semantic goal ownership,
      intention, identity acceptance, agency, or native support.
- [ ] Do not promote N14 AP4 route selection into intention, semantic choice,
      agency, or goal ownership.
- [ ] Do not promote N13 AP3 support regulation into selfhood, agency, or
      native support.
- [ ] Do not promote N12 NAT4 readiness records into native support.
- [ ] Use direct historic AP8-style evidence when it exists and is
      source-backed, source-current, claim-clean, replay-clean, budget-clean,
      and control-clean.
- [ ] Treat AP8 as an agency-prerequisite long-horizon closure candidate, not
      as agency.
- [ ] Keep `phase8_opened = false` unless a separate Phase 8 task is explicitly
      opened.
- [ ] Block stale state replay, hidden native support, semantic agency relabel,
      goal ownership relabel, identity acceptance relabel, Phase 8 relabel,
      long-horizon drift outside source-backed envelope, and
      resource/shared-medium merge relabels.
- [ ] Treat short-horizon AP7 replay as the AP8 active null.
- [ ] Record max supported horizon as an explicit envelope.
- [ ] Require linked trace continuity, not merely trace presence.
- [ ] Run single-axis stale-state controls.
- [ ] Block drift-as-autonomy relabels.
- [ ] Mark every generated artifact with `evidence_branch = artifact_only`.
- [ ] Define full, limited, and blocked AP8 closeout outcomes.
- [ ] Before closing any turn that edits files, run `git diff --check`.
- [ ] Before closing any turn that edits files, run `git diff -- src`.

## Setup

- [x] Create N18 experiment root.
- [x] Create `README.md`.
- [x] Create `configs/`, `hypotheses/`, `implementation/`, `outputs/`,
      `reports/`, and `scripts/` directories.
- [x] Create N18-specific hypotheses.
- [x] Create implementation plan.
- [x] Create implementation checklist.

## Hypotheses

- [ ] Hypothesis A: long-horizon source-current closure can be shown.
- [ ] Hypothesis B: stress replay and budget controls remain clean.
- [ ] Hypothesis C: claim boundary and Phase 8/native blockers remain clean.

## Iteration 1. Source Inventory And AP8 Contract

- [x] Pin N17 AP7 closeout, requirements, control, and claim-boundary artifacts.
- [x] Pin N16 AP6 boundary closeout and claim-boundary artifacts.
- [x] Pin N15 AP5 proxy closeout and claim-boundary artifacts.
- [x] Pin N14 AP4 consequence-sensitive selection closeout artifacts.
- [x] Pin N13 AP3 support regulation closeout artifacts.
- [x] Pin N12 NAT4 readiness and closeout artifacts if used.
- [x] Pin N08/N09 memory and bounded-regulation context if used.
- [x] Record whether direct historic AP8 long-horizon closure evidence exists.
- [x] Confirm N17 I10 closeout exists.
- [x] Classify source rows by long-horizon contribution.
- [x] Record old-best construction inputs.
- [x] Record source claim ceilings and non-promotions.
- [x] Confirm no final AP8 claim is made.

Expected artifacts:

- [x] `outputs/n18_long_horizon_source_inventory.json`
- [x] `reports/n18_long_horizon_source_inventory.md`
- [x] `scripts/build_n18_long_horizon_source_inventory.py`

Result:

```text
status = passed
acceptance_state = accepted_long_horizon_source_inventory_only_no_ap8
output_digest = b9e45e7fb4e2c90fac206e1b2c666b425eec18b02bee6cd48685fc705000a2bf
artifact_sha256 = 743a7d91cc63c9fbd49fa33c1f01404727eecb4225bc39f361817fce7d0c3546
source_rows = 12
direct_historic_ap8_evidence_exists = false
evidence_branch = artifact_only
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
ready_for_iteration_2_schema = true
failed_checks = []
```

Iteration 1 interpretation:

```text
N17 provides the strongest old-best input, but only at artifact-level AP7.
N16-N13 provide AP6/AP5/AP4/AP3 prerequisites, N12 provides readiness-only
context, and N08/N09 provide memory/regulation context. None is direct AP8
long-horizon evidence by itself, so Iteration 2 must freeze the AP8 schema and
fail-closed gate before any stress rows are interpreted.
```

## Iteration 2. Long-Horizon Schema And AP8 Gate

- [x] Freeze AP8 row schema.
- [x] Freeze local stress ladder values L0-L7.
- [x] Freeze horizon window policy.
- [x] Freeze horizon envelope policy.
- [x] Freeze stress dimensions and allowed values.
- [x] Freeze budget validity fields.
- [x] Freeze replay digest scope and algorithm.
- [x] Freeze artifact-only reconstruction requirements.
- [x] Freeze source-current continuity fields.
- [x] Freeze linked trace continuity fields.
- [x] Freeze cross-axis continuity evidence policy.
- [x] Freeze negative controls.
- [x] Freeze single-axis stale-state controls.
- [x] Freeze order-inversion control.
- [x] Freeze drift-as-autonomy relabel control.
- [x] Freeze B4/C5 and symmetric/native multi-basin relabel controls.
- [x] Freeze artifact-only evidence branch fields.
- [x] Freeze full, limited, and blocked AP8 outcome taxonomy.
- [x] Align claim-boundary blocked names with control blocked names.
- [x] Check embedded policy/config consistency.
- [x] Freeze claim-boundary flags.
- [x] Materialize `configs/n18_source_registry.json`.
- [x] Materialize `configs/n18_horizon_policy_v1.json`.
- [x] Materialize `configs/n18_stress_policy_v1.json`.
- [x] Materialize `configs/n18_budget_limits_v1.json`.
- [x] Materialize `configs/n18_control_variants_v1.json`.
- [x] Materialize `configs/n18_replay_policy_v1.json`.
- [x] Confirm no final AP8 claim is made.

Expected artifacts:

- [x] `outputs/n18_long_horizon_schema_v1.json`
- [x] `reports/n18_long_horizon_schema_v1.md`
- [x] `scripts/build_n18_long_horizon_schema_v1.py`
- [x] `scripts/validate_n18_stress_row.py`

Result:

```text
status = passed
acceptance_state = accepted_long_horizon_schema_v1_no_ap8_evidence
output_digest = 53918702f07a4ccb613149f839855a855db912646ef7c53e45679d3383bcf760
artifact_sha256 = fba0c288b9aa18bc4963715185dc81dc62ee3ae1e9a0ba06db7a9c2f0a0a2252
rows = 0
ap8_gate_count = 22
schema_check_count = 18
evidence_branch = artifact_only
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
validator_self_test = passed
validator_self_test_without_artifact_argument = passed
failed_checks = []
```

Iteration 2 interpretation:

```text
The AP8 gate is frozen before positive evidence. A row cannot allow AP8 unless
source rows are pinned, claim ceilings are preserved, artifact-only branch is
declared, the horizon envelope is explicit, horizon policy passes, all trace
axes are source-backed, linked trace continuity is present, long-horizon
continuity is present, budget is valid, replay/reconstruction and single-axis
stale controls pass, drift-as-autonomy relabel fails closed, unsafe claim
flags remain false, and Phase 8/native support remain unopened. Baseline AP7
replay alone is explicitly blocked from supporting AP8.
```

## Iteration 3. Short-Horizon AP7 Replay Baseline

- [x] Replay the N17 AP7 closeout at the declared baseline horizon.
- [x] Treat AP7 replay as an AP8 active null.
- [x] Confirm source-current loop traces remain present.
- [x] Confirm boundary separation remains present.
- [x] Confirm AP8 is not claimed from baseline replay alone.
- [x] Run stale-state and hidden-native-support controls.

Expected artifacts:

- [x] `outputs/n18_short_horizon_ap7_replay_baseline.json`
- [x] `reports/n18_short_horizon_ap7_replay_baseline.md`
- [x] `scripts/build_n18_short_horizon_ap7_replay_baseline.py`

Result:

```text
status = passed
acceptance_state = accepted_short_horizon_ap7_replay_baseline_no_ap8
output_digest = 9a7a01ed47991bd8ca631d36fa427c8365dc9ae7324c6984c8fc41b5e37aa7fe
artifact_sha256 = 23418170ff6e46de96b8e40730197c1997f7803d04597a9c814b2b3c9aa11671
row_count = 10
highest_positive_stress_ladder_rung = L1
control_rungs_exercised = [L6]
baseline_ap7_replay_supported = true
long_horizon_continuity_tested = false
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
validator_error_count = 0
ready_for_iteration_4_horizon_window_sweep = true
failed_checks = []
```

Iteration 3 interpretation:

```text
The N17 AP7 closeout stack replays at the short baseline horizon with support,
memory, regulation, selection, proxy, boundary, and closed-loop feedback traces
present and source-current. This is only the AP8 active null: the positive row
is L1 baseline replay, while L6 stale-state rows are controls rather than
positive evidence. Baseline AP7 replay, stale whole-state replay, stale
single-axis replay, and hidden-native-support relabels all keep
ap8_candidate_allowed = false.
```

Iteration 3 review follow-up:

```text
The post-review cleanup keeps ap8_outcome_classification inside the frozen
Iteration 2 taxonomy by using AP8_blocked for AP8 outcome classification, with
row-specific diagnostics moved to ap8_outcome_detail. Row 02 no longer adds an
ad-hoc control key outside the schema control set. Stale single-axis rows now
mark only links touching the stale trace as non-source-current. N12 remains
excluded from I3 trace sources by design because it is readiness-only context,
not AP7 baseline trace evidence.
```

## Iteration 4. Horizon Window Sweep

- [x] Run longer horizon windows without added perturbation.
- [x] Track support, memory, regulation, selection, proxy, boundary, and loop
      continuity per window.
- [x] Record drift and budget surface.
- [x] Reject windows outside source-backed envelope.
- [x] Confirm AP8 remains provisional pending stress controls.

Expected artifacts:

- [x] `outputs/n18_horizon_window_sweep.json`
- [x] `reports/n18_horizon_window_sweep.md`
- [x] `scripts/build_n18_horizon_window_sweep.py`

Result:

```text
status = passed
acceptance_state = accepted_horizon_window_sweep_l2_max_h4_no_ap8
output_digest = 0b65b390dabc30ee34b3003796cfb85cb1ca8f2c1bfe44f91bac160aa9c7c21e
artifact_sha256 = 1d5b554dc6c6a5f08b2b559cc40f6afca71622024b7c5ff50b57d8150a209971
row_count = 4
highest_positive_stress_ladder_rung = L2
supported_windows = [h2, h4]
partial_windows = [h8]
blocked_windows = [h16]
max_supported_horizon = h4
long_horizon_continuity_tested = true
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
validator_error_count = 0
ready_for_iteration_5_support_proxy_stress = true
failed_checks = []
```

Iteration 4 interpretation:

```text
Iteration 4 is stronger than the I3 active null because it tests longer
no-perturbation windows. The h2 and h4 rows remain source-current across the
support, memory, regulation, selection, proxy, boundary, loop feedback, and
linked-continuity axes, establishing max_supported_horizon = h4 for the L2
replay envelope. The h8 row is partial because linked continuity drops below
floor and drift exceeds the quiet ceiling. The h16 row is rejected because it is
outside the source-backed envelope and exceeds the budget surface. AP8 remains
blocked pending stress families, replay controls, stale-state controls, and
classification.
```

Iteration 4 review follow-up:

```text
h4 is explicitly recorded as the primary Iteration 5 stress anchor, with h2 as
fallback/control. h8 remains partial horizon-limit evidence, not almost
supported AP8, and h16 remains rejected out-of-envelope evidence. The h4
limiting axis is loop_feedback and the limiting linked edge is
boundary_to_loop_feedback; support/proxy stress in I5 must preserve those links
rather than retune the horizon. N12 is explicitly not consumed in I4 trace rows
because it remains readiness-only context. The L2 numeric floors and ceilings
are recorded in threshold_policy: Iteration 2 froze the required fields and
fail-closed gates, while Iteration 4 freezes the L2 numeric thresholds before
row evaluation.
```

## Iteration 5. Support Withdrawal And Proxy Perturbation

- [x] Apply support withdrawal and restoration stress.
- [x] Apply proxy/target perturbation stress.
- [x] Confirm bounded regulation and proxy formation remain source-current.
- [x] Reject hidden goal-ownership or native-support relabels.
- [x] Record whether the AP7 loop remains closed under stress.

Expected artifacts:

- [x] `outputs/n18_support_proxy_stress_matrix.json`
- [x] `reports/n18_support_proxy_stress_matrix.md`
- [x] `scripts/build_n18_support_proxy_stress_matrix.py`

Result:

```text
status = passed
acceptance_state = accepted_support_proxy_stress_matrix_h4_l3_no_ap8
output_digest = ecaa439bdfc20cd416d3b9405c9ed9b04b1aa0871dfce82f27ad966fba13b352
artifact_sha256 = f40c2d3d3390c69b99741e3beff5cbd8773551d9534fcdcb1e0f70fc0db3a715
row_count = 7
highest_positive_stress_ladder_rung = L3
primary_stress_anchor = h4
max_supported_horizon = h4
support_withdrawal_restoration_supported = true
proxy_perturbation_supported = true
h2_fallback_supported = true
current_bottleneck_axis = loop_feedback
current_bottleneck_link = boundary_to_loop_feedback
minimum_loop_feedback_score_supported_h4_rows = 0.808
minimum_budget_headroom_supported_h4_rows = 0.24
support_overdraw = partial
proxy_target_band_crossing = rejected
hidden_native_support_relabel_blocked = true
semantic_goal_ownership_relabel_blocked = true
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
validator_error_count = 0
ready_for_iteration_6_route_memory_stress = true
failed_checks = []
```

Iteration 5 interpretation:

```text
Iteration 5 stresses the I4 h4 anchor without retuning the horizon or trying to
recover h8. The bounded support withdrawal/restoration row and bounded
proxy-perturbation row are both supported at L3, but both are narrow and remain
pending replay/control validation. Support overdraw is partial because support
and loop-feedback floors are not preserved. Proxy target-band crossing is
rejected because proxy continuity and loop feedback fail closed when target
deviation exceeds the declared ceiling. The h2 row is only fallback/control; it
does not widen or replace the h4 envelope. Hidden native support and semantic
goal ownership relabels are rejected, so bounded restoration is not native
support and bounded proxy perturbation is not semantic goal ownership.
```

Iteration 5 review follow-up:

```text
The supported h4 stress rows preserve linked continuity across the full AP8
stack, not only local support/proxy fields: all trace axes and all trace links
remain source-current in the two supported h4 rows. The current bottleneck is
loop_feedback, specifically boundary_to_loop_feedback, with minimum supported
h4 loop-feedback score 0.808. I6 must use the h4/L3 support-proxy envelope
as-is, must not replace it with h2 fallback success, must not recover h8, and
must not change the budget policy. Route/context reversal and memory relaxation
should be interpreted against the existing loop-feedback bottleneck and the
minimum supported h4 budget headroom of 0.24.
```

## Iteration 6. Route/Context Reversal And Memory Relaxation

- [x] Apply route/context reversal variants.
- [x] Apply memory relaxation stress.
- [x] Confirm consequence-sensitive selection remains bounded and
      claim-clean.
- [x] Confirm memory effects remain source-backed and do not become native
      identity acceptance.
- [x] Record whether loop closure survives the reversal/relaxation matrix.

Expected artifacts:

- [x] `outputs/n18_route_memory_stress_matrix.json`
- [x] `reports/n18_route_memory_stress_matrix.md`
- [x] `scripts/build_n18_route_memory_stress_matrix.py`

Result:

```text
status = passed
acceptance_state = accepted_route_memory_stress_matrix_h4_l4_no_ap8
output_digest = a2a9d0f41b389a9769605329a282674fa17e12ec861897ed81a5f31b83a9a114
artifact_sha256 = 082b0ad9fe639135e3c8b6fff6409d6739030435ab100372dc2f7c1ac0564ec7
row_count = 7
highest_positive_stress_ladder_rung = L4
primary_stress_anchor = h4
max_supported_horizon = h4
route_context_reversal_supported = true
memory_relaxation_supported = true
route_context_break = partial
memory_decay = partial
compound_route_memory = rejected
semantic_choice_intention_relabel_blocked = true
identity_acceptance_relabel_blocked = true
current_bottleneck_axis = loop_feedback
current_bottleneck_link = boundary_to_loop_feedback
minimum_loop_feedback_score_supported_h4_rows = 0.801
minimum_budget_headroom_supported_h4_rows = 0.09
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
validator_error_count = 0
ready_for_iteration_7_environment_resource_stress = true
failed_checks = []
```

Iteration 6 interpretation:

```text
Iteration 6 stresses the h4/L3 support-proxy envelope without changing horizon
or budget policy. Bounded route/context reversal and bounded memory relaxation
are supported at L4, with linked stack continuity preserved. Route/context
break and memory decay are partial boundary rows; compound route/memory stress
is rejected because linked continuity and budget fall outside the envelope.
Route reversal is not semantic choice/intention, and memory relaxation is not
identity acceptance. AP8 remains blocked pending later
stress/replay/control/classification.
```

Iteration 6 review follow-up:

```text
I6 supports bounded L4 route/context and memory stress at h4, but the active
bottleneck is now loop_feedback, specifically boundary_to_loop_feedback. I7
must treat boundary_to_loop_feedback as the main risk, preserve h4 as the only
positive horizon anchor, avoid recovering h8, and keep the budget policy
unchanged. Supported h4 rows have narrow remaining budget headroom, with
minimum supported h4 budget headroom 0.09, so I7 must distinguish real
environment/resource failure from budget exhaustion.

The compound route/memory row remains a real blocker and must not become the
positive I7 starting point. I7 positive rows should start from the supported
h4/L4 envelope, not from the rejected compound route-memory row. The partial
route/context break and memory-decay rows remain envelope limits for
selection/memory continuity and must be carried forward to I9.

I7 must verify linked continuity link-by-link, not only in aggregate. The links
to keep visible are memory_context_to_selection, regulation_to_selection,
selection_to_proxy, and boundary_to_loop_feedback. Consequence-sensitive route
context remains not semantic choice or intention, and memory relaxation remains
not identity acceptance. L4 is still not AP8; AP8 remains blocked pending
environment/resource stress, shared-medium stress, replay/reconstruction,
stale-state controls, and claim classification.
```

Iteration 6 validation follow-up:

```text
The I6 budget-valid gate is now conditioned on the same budget ceiling used by
row-level budget_valid and budget_surface.valid. The compound route-memory
limit row therefore records budget_valid = false, ap8_gates.budget_valid =
false, and within_supported_envelope = false. The same gate helper was updated
in I5 to remove the latent mismatch before I7 consumes the stress chain.

within_supported_envelope now reflects threshold/budget membership, not mere
presence in the h4 horizon. Partial limit rows remain outside the supported
envelope; relabel controls can remain numerically inside the envelope while
their unsafe claim remains rejected.
```

## Iteration 7. Environment/Resource Perturbation

- [x] Apply environment/resource perturbation stress.
- [x] Confirm boundary separation remains preserved.
- [x] Treat `boundary_to_loop_feedback` as the primary expected bottleneck.
- [x] Use the supported `h4/L4` envelope without recovering `h8` or changing
      budget policy.
- [x] Start positive rows from supported I6 h4 rows, not from the rejected
      compound route-memory row.
- [x] Check budget exhaustion separately from environment/resource failure.
- [x] Preserve route/context and memory partial rows as envelope limits.
- [x] Verify `memory_context_to_selection`, `regulation_to_selection`,
      `selection_to_proxy`, and `boundary_to_loop_feedback` link-by-link.
- [x] Confirm resource/support closure does not become goal ownership.
- [x] Reject resource-as-self relabels.
- [x] Record long-horizon budget and replay status.

Expected artifacts:

- [x] `outputs/n18_environment_resource_stress_matrix.json`
- [x] `reports/n18_environment_resource_stress_matrix.md`
- [x] `scripts/build_n18_environment_resource_stress_matrix.py`

Result:

```text
status = passed
acceptance_state = accepted_environment_resource_stress_matrix_h4_l5_no_ap8
output_digest = f1e9b88b5ab0f3157f46f62787092477f232f5045d31e35284a3abefabb7ee48
artifact_sha256 = 102d2fd4758e08bb0d29060fda95944363afa18a55891ca0c20069f20eb3490f
row_count = 7
highest_positive_stress_ladder_rung = L5
primary_stress_anchor = h4
max_supported_horizon = h4
environment_boundary_pressure_supported = true
resource_access_perturbation_supported = true
environment_boundary_pressure = partial
resource_access_budget = rejected
compound_environment_resource = rejected
resource_goal_ownership_relabel_blocked = true
resource_as_self_relabel_blocked = true
current_bottleneck_axis = loop_feedback
current_bottleneck_link = boundary_to_loop_feedback
minimum_boundary_score_supported_h4_rows = 0.806
minimum_loop_feedback_score_supported_h4_rows = 0.800
minimum_budget_headroom_supported_h4_rows = 0.03
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
validator_error_count = 0
ready_for_iteration_8_shared_medium_stress = true
failed_checks = []
```

Iteration 7 interpretation:

```text
Iteration 7 stresses the h4/L4 route-memory envelope without changing horizon
or budget policy. Bounded environment boundary pressure and bounded resource
access perturbation are supported at L5 for the environment/resource family,
with linked stack continuity preserved. The result is narrow: the minimum
supported h4 budget headroom is 0.03 and the active bottleneck remains
loop_feedback, specifically boundary_to_loop_feedback.

The environment pressure limit is partial because boundary-to-loop feedback
falls below floor before budget is exhausted. The resource-access budget row is
rejected because budget fails while trace continuity is still source-current,
separating budget exhaustion from environment/resource trace failure. The
compound environment/resource row is rejected because both linked continuity
and budget leave the envelope.

Resource access is not semantic goal ownership, native support, selfhood, or
resource-as-self evidence. AP8 remains blocked pending shared-medium stress,
replay/reconstruction, stale-state controls, and claim classification.
```

Iteration 7 review follow-up:

```text
I7 is the narrowest positive stress result so far. It supports L5
environment/resource stress at h4, but only with minimum supported h4 budget
headroom 0.03 and boundary_to_loop_feedback still the active bottleneck. I8
must treat 0.03 budget headroom as a hard constraint, must not change the
budget policy, and must not recover h8.

The resource-access budget-limit row is a real blocker: source-current trace
continuity alone is not enough because budget validity is a hard AP8 gate. The
environment pressure limit is a different blocker because boundary-to-loop
feedback fails before budget is exhausted. The compound environment/resource
row is rejected because both linked continuity and budget leave the envelope.
I8 must preserve these three failure modes rather than smoothing them together.

I8 should therefore be a minimal bounded shared-medium separability test, not a
general shared-medium robustness sweep. It should start from supported h4/L5
rows only, keep resource-as-goal and resource-as-self relabels blocked, and
keep AP8 blocked until I9 replay/control/classification.
```

## Iteration 8. Shared-Medium Perturbation And Merge Controls

- [x] Apply shared-medium perturbation stress.
- [x] Confirm basin separability and no-merge controls.
- [x] Treat `minimum_budget_headroom_supported_h4_rows = 0.03` as a hard
      budget constraint.
- [x] Keep `boundary_to_loop_feedback` as the primary expected bottleneck.
- [x] Use the supported `h4/L5` environment-resource envelope without
      recovering `h8` or changing budget policy.
- [x] Do not treat the rejected compound environment/resource row as a
      positive shared-medium starting point.
- [x] Run a minimal bounded shared-medium separability probe, not a general
      robustness sweep.
- [x] Preserve environment continuity failure, resource budget failure, and
      compound failure as distinct blockers.
- [x] Preserve N17 caveat that original B4/C5 reverse replay remains blocked.
- [x] Distinguish derived paired-perspective evidence from original B4/C5
      relabeling.
- [x] Reject resource/shared-medium merge relabels.
- [x] Keep AP8 blocked until Iteration 9 replay/control/classification.

Expected artifacts:

- [x] `outputs/n18_shared_medium_stress_matrix.json`
- [x] `reports/n18_shared_medium_stress_matrix.md`
- [x] `scripts/build_n18_shared_medium_stress_matrix.py`

Result:

```text
status = passed
acceptance_state = accepted_minimal_shared_medium_stress_matrix_h4_l5_no_ap8
output_digest = f2e0d7f8b8c88bb85f7bf5d588819e83043d3ff17c4bdfad306955fd8fcd9b60
artifact_sha256 = f3e9f4c7c6fd57100e47c03f73110fbf3a0293deaa2d370df4f54533534a605c
row_count = 7
highest_positive_stress_ladder_rung = L5
primary_stress_anchor = h4
max_supported_horizon = h4
minimal_shared_medium_separability_supported = true
shared_medium_merge_pressure = partial
shared_medium_budget = rejected
compound_shared_medium = rejected
b4c5_original_reverse_replay_relabel_blocked = true
derived_paired_as_original_b4c5_relabel_blocked = true
resource_shared_medium_merge_relabel_blocked = true
current_bottleneck_axis = loop_feedback
current_bottleneck_link = boundary_to_loop_feedback
maximum_merge_pressure_supported_h4_rows = 0.12
maximum_neighbor_leakage_supported_h4_rows = 0.012
minimum_boundary_score_supported_h4_rows = 0.802
minimum_loop_feedback_score_supported_h4_rows = 0.800
minimum_budget_headroom_supported_h4_rows = 0.01
minimum_continuity_margin_supported_h4_rows = 0.0
floor_sensitivity_recorded_for_i9 = true
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
validator_error_count = 0
ready_for_iteration_9_replay_control_classification = true
failed_checks = []
```

Interpretation:

```text
Iteration 8 stresses the h4/L5 environment-resource envelope without changing
horizon or budget policy. Only a minimal bounded shared-medium separability row
is supported at L5, with linked stack continuity preserved and minimum budget
headroom 0.01.

The positive row is exactly at the inclusive `0.800` continuity floor for
`closed_loop_feedback_trace`, `boundary_to_loop_feedback`, and cross-axis
continuity. The builder comparison policy is floor-inclusive (`score >= floor`)
and ceiling-inclusive (`cost/drift <= ceiling`), and the JSON records numeric
values before report formatting. I9 must preserve this equality-at-floor
semantics during replay/classification.

The merge-pressure row is partial because boundary-to-loop feedback fails
before budget is exhausted. The budget row is rejected while traces remain
source-current. The compound row is rejected because both separability and
budget leave the envelope.

Original B4/C5 reverse replay remains blocked, derived paired-perspective
evidence cannot backfill the original B4/C5 source, and bounded shared-medium
separability is not a resource/shared-medium merge. AP8 remains blocked
pending I9 replay/control/classification.
```

Iteration 8 review follow-up:

```text
I8 is a good pass but the positive envelope is now very tight. It supports only
bounded artifact-level L5 minimal shared-medium stress under h4, not AP8,
general shared-medium robustness, original B4/C5 reverse replay, agency,
native support, Phase 8, or unrestricted autonomy.

The I8 positive row has zero continuity margin at the active floor:
closed_loop_feedback_trace = 0.800, boundary_to_loop_feedback = 0.800, and
cross_axis_score = 0.800. This is valid because the frozen comparison policy is
inclusive, but I9 must reproduce it from canonical numeric artifact values and
must not let formatted report rounding, hidden state, order effects, or budget
policy changes flip the row.

The final I8 bottleneck remains boundary_to_loop_feedback. Budget validity is
a hard gate: the budget-limit row remains rejected even while trace continuity
is source-current. Merge pressure is a distinct partial continuity boundary,
and compound shared-medium stress is a distinct rejected separability-plus-
budget boundary. I9 must preserve all three failure modes and must not start a
positive AP8 path from rejected compound stress.

I7 and I8 together complete the L5 stress stack enough for I9 control and
classification, but AP8 remains false until I9/I10.
```

Iteration 8 visualization addendum:

```text
status = passed
artifact = outputs/n18_iteration8_shared_medium_visualization.json
report = reports/n18_iteration8_shared_medium_visualization.md
script = scripts/render_n18_iteration8_shared_medium_visualization.py
static_graph = outputs/n18_iteration8_shared_medium_visualization/n18_i8_shared_medium_graph.png
sequence_panel = outputs/n18_iteration8_shared_medium_visualization/n18_i8_shared_medium_sequence.png
animation = outputs/n18_iteration8_shared_medium_visualization/n18_i8_shared_medium_animation.gif
geometry_graph = outputs/n18_iteration8_shared_medium_visualization/n18_i8_b4c5_source_geometry_graph.png
geometry_sequence_panel = outputs/n18_iteration8_shared_medium_visualization/n18_i8_b4c5_source_geometry_sequence.png
geometry_animation = outputs/n18_iteration8_shared_medium_visualization/n18_i8_b4c5_source_geometry_animation.gif
output_digest = 2683140c773fa54ef7e2f2c0a63c3d665653c0bf8f580f410618159d781951e5
manifest_sha256 = 524fc111d82f51a8fc20138d3ca4f5c5b0ba13578745d5d023cee286d78e87ba
report_sha256 = 64489c388cba1cbebe611b5cc96b06a7d51819da79f95f064ffbde9242b60cb8
script_sha256 = 913ca0165bb2aafa7e8fe08b0c4fa8c0f1b425dfa29b91dfa503040b6aaccffe
static_graph_sha256 = 6b03c5fe62e34b5a32945222a6b1ba696b4eca4142ccf4339cc689a854e82fc6
sequence_panel_sha256 = a6474d3643a9b7b6a3b9a5b161b040844abe17773bab31979e99ce17c6af8af1
animation_sha256 = 0b91d37a4975e6d97dd0ef115334cf221e68635c9d2ad0d73d3e5e54539d8fa3
geometry_graph_sha256 = 3f35d7f7fabb934de12b263c40d03f0ecfc23df84c8cc97fa7d0be806951748c
geometry_sequence_panel_sha256 = 134c483c7709b1d95ea2600a5db9caf1a2d1886b47a296182f9ffa64360dc825
geometry_animation_sha256 = 75a5b2e0c63d38fb9cd096b0e964704d4d51c6b4ad1f2029eb26c3be9246d60c
renderer_boundary = supporting artifact-level visualization only
direct_pygrc_graph_checkpoint_renderer_used = false
reused_libraries = matplotlib, networkx, PIL
```

The visualization renders I8's source-row graph, phase progression, and
source-backed B4/C5 geometry graph. It
reuses the same visualization dependency stack used by the LGRC visual tools,
but it does not call the checkpoint-backed `render_graph_run_visual_bundle`
path because I8 is an artifact-level stress matrix and does not contain native
LGRC telemetry graph checkpoints.

The animations are therefore source-row/phase and source-backed geometry
animations, not native runtime execution. They do not add evidence, open AP8,
open Phase 8, support agency, or support native LGRC dynamics.

## Iteration 8-A. Shared-Medium Margin Robustness Probe

- [x] Add an alternative shared-medium margin probe without retuning or
      replacing I8.
- [x] Keep `h4`, `L5`, threshold policy, budget ceiling, and claim boundary
      fixed.
- [x] Preserve I8 as the primary minimal edge-case support row.
- [x] Require the alternative positive row to have budget headroom at least
      `0.05` and continuity margin above the `0.800` floor.
- [x] Preserve `boundary_to_loop_feedback` as the limiting link.
- [x] Reject hidden budget relief, threshold relaxation, horizon shortening,
      dropped bottleneck-link, merge-as-success, and original B4/C5 backfill
      controls.
- [x] Keep AP8 blocked until Iteration 9 replay/control/classification.

Expected artifacts:

- [x] `outputs/n18_shared_medium_margin_probe.json`
- [x] `reports/n18_shared_medium_margin_probe.md`
- [x] `scripts/build_n18_shared_medium_margin_probe.py`

Result:

```text
status = passed
acceptance_state = accepted_shared_medium_margin_probe_h4_l5_no_ap8
output_digest = 997bbcfa45c10cfd3a51fa61553a7df56337aa60b969c231a90848cca7723c0b
artifact_sha256 = 765ea51640d7533727d9a946a9b38db4696e71bc7c43b9a109c232eac3bae318
row_count = 8
highest_positive_stress_ladder_rung = L5
primary_stress_anchor = h4
max_supported_horizon = h4
margin_candidate_supported = true
minimum_boundary_score_supported_h4_rows = 0.826
minimum_loop_feedback_score_supported_h4_rows = 0.822
minimum_budget_headroom_supported_h4_rows = 0.06
minimum_continuity_margin_supported_h4_rows = 0.022
current_bottleneck_axis = loop_feedback
current_bottleneck_link = boundary_to_loop_feedback
hidden_budget_relief_rejected = true
threshold_relaxation_rejected = true
horizon_shortening_rejected = true
dropped_boundary_to_loop_feedback_rejected = true
merge_as_success_rejected = true
b4c5_original_reverse_replay_relabel_blocked = true
i8a_replaces_i8_minimal_row = false
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
validator_error_count = 0
ready_for_iteration_9_replay_control_classification = true
failed_checks = []
```

Interpretation:

```text
Iteration 8-A adds a higher-margin shared-medium variant without changing the
horizon, stress ladder, thresholds, budget ceiling, or claim boundary. It
preserves the same shared-medium perturbation size as I8 while raising the
minimum continuity margin from 0.0 to 0.022 and budget headroom from 0.01 to
0.06.

This is additional robustness evidence, not a replacement for I8. I8 remains
the honest minimal edge-case support row. I8-A says the shared-medium story is
not only a knife-edge equality-at-floor pass, but the result is still local,
source-backed, h4/L5, and AP8-false.

The active bottleneck remains boundary_to_loop_feedback. Hidden budget relief,
threshold relaxation, horizon shortening, dropped boundary-to-loop feedback,
merge-as-success, and original B4/C5 backfill all fail closed.
```

Geometric and flux difference from Iteration 8:

```text
Iteration 8 is the minimal shared-medium crossing case. Geometrically, the
boundary and loop surfaces remain connected, but the connection is tangent to
the admissible floor: closed_loop_feedback_trace = 0.800,
boundary_to_loop_feedback = 0.800, and cross_axis_score = 0.800. In flux terms,
shared-medium pressure is transmitted through the boundary-to-loop channel
without breaking it, but the retained loop-feedback flow has no continuity
slack. The pass is valid only because the frozen policy accepts equality at
the floor.

Iteration 8-A does not reduce the horizon, relax thresholds, change the budget
ceiling, or remove the shared-medium perturbation. It changes the geometric
configuration of the source-backed variant so the shared-medium crossing has
more separation from the merge/leakage boundary and more retained continuity
through the bottleneck link. The limiting link is still
boundary_to_loop_feedback, but it now carries 0.822 instead of 0.800, while
cross-axis continuity rises to 0.823 and boundary separation rises to 0.826.

In flux terms, I8-A is not "less shared-medium stress"; it is a better
channeled shared-medium flow. The perturbation still enters through the
shared-medium path, but less of it becomes merge pressure or neighbor leakage,
and more of the resulting signal remains attributable to the intended
boundary-to-loop feedback channel. That is why budget headroom rises from 0.01
to 0.06 and the minimum continuity margin rises from 0.0 to 0.022.

The composed interpretation is therefore:
I8 proves the minimal edge case survives.
I8-A proves a second source-backed configuration survives with positive
geometric/flux margin.
Together they strengthen the shared-medium L5 story without turning it into
general robustness, original B4/C5 reverse replay, AP8, agency, native
support, or Phase 8 evidence.
```

## Iteration 9. Full Replay, Control, And Classification Matrix

- [x] Run artifact-only reconstruction.
- [x] Run duplicate replay.
- [x] Run snapshot/load replay.
- [x] Run stale-state controls.
- [x] Run post-hoc long-horizon stitching controls.
- [x] Run hidden-native-support controls.
- [x] Run semantic agency, action/perception, goal-ownership, identity, and
      Phase 8 relabel controls.
- [x] Classify the narrow `h4/L5` stress stack as-is without widening horizon,
      recovering `h8`, changing budget policy, or promoting local
      shared-medium separability into general shared-medium robustness.
- [x] Classify I8 and I8-A together as narrow shared-medium evidence: I8 as
      the minimal edge case, I8-A as additional higher-margin evidence, not a
      replacement or generalized robustness result.
- [x] Reproduce the I8 minimal shared-medium row from canonical numeric values
      without rounding drift, hidden state, order effects, or threshold-policy
      changes; preserve inclusive equality-at-floor semantics for the `0.800`
      continuity floor.
- [x] Preserve `boundary_to_loop_feedback` as the final bottleneck unless replay
      produces a source-backed blocker.
- [x] Preserve merge-pressure, budget, and compound shared-medium failure modes
      as distinct classification limits.
- [x] Do not use rejected compound shared-medium stress as positive AP8
      evidence.
- [x] Preserve original B4/C5 reverse replay and derived-as-original relabel
      blockers.
- [x] Classify AP8 only if all gates pass.
- [x] Keep final closeout pending Iteration 10.

Expected artifacts:

- [x] `outputs/n18_long_horizon_control_and_classification_matrix.json`
- [x] `reports/n18_long_horizon_control_and_classification_matrix.md`
- [x] `scripts/build_n18_long_horizon_control_and_classification_matrix.py`

Result:

```text
status = passed
acceptance_state = accepted_limited_ap8_classification_pending_i10_closeout
output_digest = c7b400660c5203a3b975b1921ee808ad447329ebdda199af47ba27e26d1fc734
artifact_sha256 = b9a4c0409a8ae2b9cf12aad0758be26f8047d6234867694e460b64a06b36979b
report_sha256 = d87604a5b4669484b26dd8ca38502005b9a8e37127c75f28dc084e3955e0ac71
script_sha256 = 4b1e8dbe23496103fff540e51a2e58acbd8fcf9c37af0aa3017ef14dda92242b
row_count = 1
classified_ap_level = AP8_limited_artifact_candidate
ap8_classification_supported = true
ap8_candidate_allowed = true
final_ap8_supported = false
final_artifact_level_ap8_frozen = false
max_supported_horizon = h4
highest_positive_stress_ladder_rung = L5
replay_control_ladder_rung = L6
classification_ladder_rung = L7
i8_minimal_result_preserved = true
i8a_margin_role = additional_robustness_evidence_not_i8_replacement
boundary_to_loop_feedback_score = 0.800
minimum_budget_headroom_classified_stack = 0.01
artifact_only_reconstruction_status = stable
duplicate_replay_status = stable
snapshot_load_replay_status = stable
stale_state_control_status = failed_expected
order_inversion_status = failed_expected
post_hoc_stitching_control_status = failed_expected
unsafe_claim_flags_false = true
phase8_opened = false
native_support_opened = false
ready_for_iteration10_closeout = true
failed_checks = []
validator_error_count = 0
```

Interpretation:

```text
Iteration 9 classifies the existing N18 h4/L5 stress stack as a limited
artifact-level AP8 candidate. The classification is intentionally conservative:
the validator row is an L6 artifact-only replay/control row, while the
classification result records the L7 claim boundary around that validated row.

I9 does not widen the horizon, recover h8, change the budget policy, retune
thresholds, or promote shared-medium evidence into general robustness. The
classification preserves I8 as the minimal equality-at-floor shared-medium row
and I8-A as additional higher-margin evidence, not as an I8 replacement.

Geometrically, the classified stack remains pinned to the narrow h4/L5 corridor.
The final active bottleneck is still the boundary-to-loop feedback link at
0.800, with only 0.01 budget headroom in the conservative composed row. I8-A
shows that a second source-backed configuration has positive margin, but I9
keeps the composed AP8 classification bounded by the original I8 edge case.

Replay and controls now pass the L6 gate: artifact-only reconstruction,
duplicate replay, and snapshot/load replay are stable; stale-state,
single-axis stale, order inversion, post-hoc stitching, hidden native support,
semantic agency/action/perception, identity, Phase 8, B4/C5 relabel, general
symmetric multi-basin, and budget-overrun controls fail closed.

The supported claim is therefore:
artifact-level AP8 long-horizon agentic-like closure candidate for a narrow
h4/L5 envelope, pending Iteration 10 final freeze and handoff.

The result does not support final AP8 freeze, Phase 8, native support,
semantic agency, semantic action/perception, identity acceptance, selfhood,
organism/life, or general shared-medium robustness.
```

## Iteration 10. Closeout And Phase 8 Handoff/Defer Record

- [x] Freeze final supported AP level if warranted.
- [x] Preserve the final supported AP level as
      `AP8_limited_artifact_candidate`; do not upgrade to full/general AP8.
- [x] Record final claim ceiling.
- [x] Record `final_claim_ceiling =
      artifact_level_ap8_long_horizon_agentic_like_closure_candidate`.
- [x] Record `max_supported_horizon = h4` and
      `horizon_extrapolation_allowed = false`; do not recover `h8` or `h16`.
- [x] Preserve the I8/I8-A distinction: I8 is the minimal equality-at-floor
      shared-medium edge case, and I8-A is additional higher-margin evidence,
      not an I8 replacement or generalized robustness result.
- [x] Preserve `principal_bottleneck_axis = loop_feedback` and
      `principal_bottleneck_link = boundary_to_loop_feedback`.
- [x] Record final controls and blockers.
- [x] Phrase negative controls as `failed_closed_as_expected` or equivalent,
      not as ambiguous failures.
- [x] Keep stale support, memory, selection, proxy, boundary, and loop-feedback
      controls visible in the final record.
- [x] Confirm `src_diff_empty`.
- [x] Confirm no absolute paths.
- [x] Confirm `phase8_opened = false` unless separately opened.
- [x] Confirm native-supported flags remain false unless separately validated.
- [x] Force unsafe closeout flags false for agency, choice, intention,
      semantic action/perception, semantic goal ownership, selfhood, identity
      acceptance, native support, Phase 8, organism/life, fully native
      integration, and unrestricted autonomy.
- [x] Record whether targeted Phase 8 remains optional/deferred or becomes the
      recommended next step.

Expected artifacts:

- [x] `outputs/n18_closeout_and_handoff.json`
- [x] `reports/n18_closeout_and_handoff.md`
- [x] `scripts/build_n18_closeout_and_handoff.py`

Result:

```text
status = passed
acceptance_state = closed_limited_artifact_level_ap8_long_horizon_agentic_like_closure_candidate
output_digest = 09c0987d19e372d3df86377a843367a8bae8c85b0bc925f8328948b17a743af1
artifact_sha256 = d4b2bacfec3fbb5684cf8aec5aeb3cbc9b2409969ae94ae53ac436191c75407c
report_sha256 = c98605b724db60ca3df6fca7dc628f31a87a81a80dea8fcfe561352ee578f9c7
script_sha256 = 2b995805865c7fd0b8b789a55382148518fb42280c596244b6543bd5aa60387a
final_supported_ap_level = AP8_limited_artifact_candidate
final_ap8_supported = true
final_artifact_level_ap8_frozen = true
general_ap8_supported = false
final_claim_ceiling = artifact_level_ap8_long_horizon_agentic_like_closure_candidate
max_supported_horizon = h4
horizon_extrapolation_allowed = false
h8_recovered = false
h16_recovered = false
highest_positive_stress_ladder_rung = L5
replay_control_ladder_rung = L6
classification_ladder_rung = L7
principal_bottleneck_axis = loop_feedback
principal_bottleneck_link = boundary_to_loop_feedback
principal_bottleneck_score = 0.800
minimum_budget_headroom_classified_stack = 0.01
i8_role = minimal_equality_at_floor_shared_medium_edge_case
i8a_role = additional_higher_margin_shared_medium_evidence
i8a_replaces_i8 = false
phase8_opened = false
native_support_opened = false
fully_native_integration_opened = false
src_diff_empty = true
failed_checks = []
```

Interpretation:

```text
N18 closes as a limited artifact-level AP8 long-horizon agentic-like closure
candidate. The final claim is deliberately not general AP8: it is bounded to
the narrow h4/L5 stress envelope, with h8 and h16 unrecovered and horizon
extrapolation blocked.

The closeout preserves the I8/I8-A distinction. I8 remains the minimal
equality-at-floor shared-medium support row. I8-A remains additional
higher-margin corroboration, not a replacement for I8 and not general
shared-medium robustness.

The final geometric bottleneck is still the loop-feedback axis, specifically
the boundary_to_loop_feedback link at 0.800. The conservative classified stack
also preserves only 0.01 budget headroom.

Replay/control closeout remains clean: artifact-only reconstruction, duplicate
replay, and snapshot/load replay are stable; stale-state, stale support,
stale memory, stale selection, stale proxy, stale boundary, stale loop
feedback, order inversion, post-hoc stitching, hidden native support, semantic
agency/action/perception, identity, Phase 8, original B4/C5 reverse replay,
general symmetric multi-basin, and budget-overrun controls fail closed as
expected.

Phase 8 is deferred, not opened. N18 does not support agency, choice,
intention, semantic action/perception, semantic goal ownership, selfhood,
identity acceptance, native support, organism/life, fully native integration,
or unrestricted autonomy.

General RC theory interpretation is recorded in the closeout artifact/report.
The concise reading is: N18 demonstrates that RC can construct and preserve a
bounded artifact-level agency-prerequisite closure stack across horizon and
stress. The result supports limited AP8 agentic-like closure, not agency. The
main limiting constraint is the boundary-to-loop-feedback link, and the next
theoretical step is native producer-side implementation, not stronger semantic
interpretation.
```

## Initial Setup Result

```text
status = initialized
branch = experiment-N18
src_diff_expected = empty
phase8_opened = false
native_support_opened = false
final_ap8_supported = false
```
