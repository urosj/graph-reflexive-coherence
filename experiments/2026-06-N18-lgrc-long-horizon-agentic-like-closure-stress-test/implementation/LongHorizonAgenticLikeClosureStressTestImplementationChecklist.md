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

- [ ] Replay the N17 AP7 closeout at the declared baseline horizon.
- [ ] Treat AP7 replay as an AP8 active null.
- [ ] Confirm source-current loop traces remain present.
- [ ] Confirm boundary separation remains present.
- [ ] Confirm AP8 is not claimed from baseline replay alone.
- [ ] Run stale-state and hidden-native-support controls.

Expected artifacts:

- [ ] `outputs/n18_short_horizon_ap7_replay_baseline.json`
- [ ] `reports/n18_short_horizon_ap7_replay_baseline.md`
- [ ] `scripts/build_n18_short_horizon_ap7_replay_baseline.py`

Expected acceptance:

```text
accepted_short_horizon_ap7_replay_baseline_no_ap8
```

## Iteration 4. Horizon Window Sweep

- [ ] Run longer horizon windows without added perturbation.
- [ ] Track support, memory, regulation, selection, proxy, boundary, and loop
      continuity per window.
- [ ] Record drift and budget surface.
- [ ] Reject windows outside source-backed envelope.
- [ ] Confirm AP8 remains provisional pending stress controls.

Expected artifacts:

- [ ] `outputs/n18_horizon_window_sweep.json`
- [ ] `reports/n18_horizon_window_sweep.md`
- [ ] `scripts/build_n18_horizon_window_sweep.py`

## Iteration 5. Support Withdrawal And Proxy Perturbation

- [ ] Apply support withdrawal and restoration stress.
- [ ] Apply proxy/target perturbation stress.
- [ ] Confirm bounded regulation and proxy formation remain source-current.
- [ ] Reject hidden goal-ownership or native-support relabels.
- [ ] Record whether the AP7 loop remains closed under stress.

Expected artifacts:

- [ ] `outputs/n18_support_proxy_stress_matrix.json`
- [ ] `reports/n18_support_proxy_stress_matrix.md`
- [ ] `scripts/build_n18_support_proxy_stress_matrix.py`

## Iteration 6. Route/Context Reversal And Memory Relaxation

- [ ] Apply route/context reversal variants.
- [ ] Apply memory relaxation stress.
- [ ] Confirm consequence-sensitive selection remains bounded and
      claim-clean.
- [ ] Confirm memory effects remain source-backed and do not become native
      identity acceptance.
- [ ] Record whether loop closure survives the reversal/relaxation matrix.

Expected artifacts:

- [ ] `outputs/n18_route_memory_stress_matrix.json`
- [ ] `reports/n18_route_memory_stress_matrix.md`
- [ ] `scripts/build_n18_route_memory_stress_matrix.py`

## Iteration 7. Environment/Resource Perturbation

- [ ] Apply environment/resource perturbation stress.
- [ ] Confirm boundary separation remains preserved.
- [ ] Confirm resource/support closure does not become goal ownership.
- [ ] Reject resource-as-self relabels.
- [ ] Record long-horizon budget and replay status.

Expected artifacts:

- [ ] `outputs/n18_environment_resource_stress_matrix.json`
- [ ] `reports/n18_environment_resource_stress_matrix.md`
- [ ] `scripts/build_n18_environment_resource_stress_matrix.py`

## Iteration 8. Shared-Medium Perturbation And Merge Controls

- [ ] Apply shared-medium perturbation stress.
- [ ] Confirm basin separability and no-merge controls.
- [ ] Preserve N17 caveat that original B4/C5 reverse replay remains blocked.
- [ ] Distinguish derived paired-perspective evidence from original B4/C5
      relabeling.
- [ ] Reject resource/shared-medium merge relabels.

Expected artifacts:

- [ ] `outputs/n18_shared_medium_stress_matrix.json`
- [ ] `reports/n18_shared_medium_stress_matrix.md`
- [ ] `scripts/build_n18_shared_medium_stress_matrix.py`

## Iteration 9. Full Replay, Control, And Classification Matrix

- [ ] Run artifact-only reconstruction.
- [ ] Run duplicate replay.
- [ ] Run snapshot/load replay.
- [ ] Run stale-state controls.
- [ ] Run post-hoc long-horizon stitching controls.
- [ ] Run hidden-native-support controls.
- [ ] Run semantic agency, action/perception, goal-ownership, identity, and
      Phase 8 relabel controls.
- [ ] Classify AP8 only if all gates pass.
- [ ] Keep final closeout pending Iteration 10.

Expected artifacts:

- [ ] `outputs/n18_long_horizon_control_and_classification_matrix.json`
- [ ] `reports/n18_long_horizon_control_and_classification_matrix.md`
- [ ] `scripts/build_n18_long_horizon_control_and_classification_matrix.py`

## Iteration 10. Closeout And Phase 8 Handoff/Defer Record

- [ ] Freeze final supported AP level if warranted.
- [ ] Record final claim ceiling.
- [ ] Record final controls and blockers.
- [ ] Confirm `src_diff_empty`.
- [ ] Confirm no absolute paths.
- [ ] Confirm `phase8_opened = false` unless separately opened.
- [ ] Confirm native-supported flags remain false unless separately validated.
- [ ] Record whether targeted Phase 8 remains optional/deferred or becomes the
      recommended next step.

Expected artifacts:

- [ ] `outputs/n18_closeout_and_handoff.json`
- [ ] `reports/n18_closeout_and_handoff.md`
- [ ] `scripts/build_n18_closeout_and_handoff.py`

## Initial Setup Result

```text
status = initialized
branch = experiment-N18
src_diff_expected = empty
phase8_opened = false
native_support_opened = false
final_ap8_supported = false
```
