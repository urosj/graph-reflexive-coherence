# N09 Goal-Proxy Regulation Implementation Checklist

This checklist tracks implementation of
`2026-05-N09-lgrc-goal-proxy-regulation`.

Status keys:

```text
Pending     not started
In Progress work has begun
Complete    implemented, run, and recorded
Blocked     cannot proceed without a decision or upstream result
Deferred    intentionally postponed
```

## Global Constraints

- [ ] Keep N09 experiment-local unless a separate Phase 8/core task is opened.
- [ ] Stop before changing `src/*`.
- [ ] Treat N05 O5 as oscillator/circuit background only.
- [ ] Treat N05 O6 as blocked by `missing_route_conductance_memory_policy`.
- [ ] Treat N06 SC6 as route-choice infrastructure, not regulation evidence.
- [ ] Treat N07 ID6 as identity/support context, not identity acceptance.
- [ ] Treat N08 Hypothesis A as scoped artifact-only serialized route
      memory/trail evidence only.
- [ ] Treat N08 Hypothesis B as bounded static geometry route-response
      evidence only, with `native_route_conductance_memory_policy_missing`
      still active.
- [ ] Treat N09 Hypothesis B as staged, not discarded: inventory possible
      native/substrate-mediated ingredients now, and block only full native
      absorption until a minimal LGRC policy surface is identified.
- [ ] Keep N09 scoped to goal-proxy regulation.
- [ ] Do not promote intention, agency, desire, reward optimization, semantic
      goal understanding, goal ownership, identity acceptance, RC identity
      collapse, ACO, locomotion, biological, personhood, unrestricted identity,
      or unrestricted movement claims.
- [ ] Keep producer scheduling labeled as scheduling/evidence, not agency.
- [ ] Keep `step()` as the packet mutation boundary.
- [ ] Preserve node-plus-packet budget accounting for every run.
- [ ] Keep proxy/error bookkeeping separate from node-plus-packet budgets.
- [ ] Keep memory-budget surfaces separate from proxy and node-plus-packet
      budgets.
- [ ] Include a memory-shaped regulation lane and a no-memory comparator lane
      before claiming roadmap memory-shaped regulation.
- [ ] Record identity/support preservation or disruption when regulation
      consumes N07 support evidence.
- [ ] Treat identity-continuous regulation as N10 handoff material, not an N09
      agency or identity-acceptance claim.
- [ ] Keep N09 single-variable unless a later extension explicitly opens
      multi-variable or cross-context regulation.
- [ ] Serialize proxy, error, policy, route/producer, packet, and response
      records for artifact-only replay.
- [ ] Record exact replay commands for every generated artifact.
- [ ] Record SHA-256 digests for positive fixture artifacts.

## Iteration 0. Planning And Stubs

Status: Complete.

- [x] Create N09 experiment root.
- [x] Create N09 root README.
- [x] Create implementation README.
- [x] Create implementation plan.
- [x] Create implementation checklist.
- [x] Create `configs/`, `outputs/`, `reports/`, `scripts/`, and
      `hypotheses/` stubs.
- [x] Record inherited N05 result:
      `self_sustained_oscillator_candidate`.
- [x] Record inherited N05 blocker:
      `missing_route_conductance_memory_policy`.
- [x] Record inherited N06 result:
      `artifact_only_semantic_route_choice_candidate`.
- [x] Record inherited N07 result:
      `artifact-only source-specific ID6 bounded_non_destructive_exchange`.
- [x] Record inherited N08 Hypothesis A result:
      `artifact_only_route_memory_or_trail_affordance_candidate`.
- [x] Record inherited N08 Hypothesis B result:
      `static_positive_geometry_route_response_persistence_candidate`.
- [x] Freeze initial GPR0-GPR6 ladder.
- [x] Freeze initial claim boundary.
- [x] Record N09 as goal-proxy regulation, not intention or agency.
- [x] Record the Arc-of-Becoming orienting question and interpretation axis.
- [x] Record A4/A5 boundary: N09 targets A4 and records A5-relevant
      identity/support outcomes as handoff tags.
- [x] Record Hypothesis B as staged, with full native absorption blocked until
      a minimal native policy surface is identified.
- [x] Record memory-shaped lane and no-memory comparator requirement.
- [x] Record single-variable scope and N10 handoff boundary.

Acceptance statement:

```text
N09 starts from a clean claim boundary: N05 supplies oscillator/circuit
background, N06 supplies route-choice artifacts, N07 supplies identity/support
anchors, and N08 supplies scoped memory/trail evidence plus a bounded geometry
route-response design direction. N09 opens only goal-proxy regulation evidence.
A valid N09 positive result requires runtime-visible proxy measurement,
serialized target/error policy, proxy-conditioned route or producer evidence,
budget-safe response, controls, and artifact-only replay.
```

Arc-of-Becoming orienting question:

```text
Can this system regulate something it can observe, using memory-shaped choice,
while preserving identity/support and clean claim boundaries?
```

Interpretation axis:

```text
no regulation
wrong-direction response
probe-supported correction
repeated bounded correction
support-dependent regulation
identity-anchored regulation
artifact-only regulation candidate
native-policy gap or native expression candidate
```

A-ladder boundary:

```text
N09 target = A4 goal-proxy regulation
N09 may record A5-relevant identity/support outcomes
N10 consumes identity-continuous regulation if supported
```

Initial Hypothesis B status:

```text
staged
B0 = inventory native/substrate-mediated ingredients from N05-N08
B1 = later geometry/substrate-mediated regulation probe if A-path identifies
     load-bearing proxy variables and response laws
B2 = native absorption blocker if pure LGRC regulation needs missing policy
     surface
expected blocker = native_goal_proxy_regulation_policy_missing
```

Implementation record:

- Added `experiments/2026-05-N09-lgrc-goal-proxy-regulation/README.md`.
- Added `implementation/README.md`.
- Added `implementation/GoalProxyRegulationImplementationPlan.md`.
- Added `implementation/GoalProxyRegulationImplementationChecklist.md`.
- Added `hypotheses/README.md`.
- Recorded the Arc-of-Becoming orienting question in the README, plan, and
  checklist.
- Recorded the N09 A4/A5 boundary, memory-shaped lane requirement, no-memory
  comparator, Hypothesis B staged path, single-variable scope, and N10 handoff
  expectations.
- Created placeholder `configs/`, `outputs/`, `reports/`, and `scripts`
  directories.
- Created placeholder `hypotheses/` directory.
- No N09 probes have been run yet.
- No `src/*` changes are required for Iteration 0.

## Iteration 1. Baseline And Source Inventory

Status: Passed.

- [x] Inventory N05 closeout artifacts:
  - [x] O5 oscillator/circuit result
  - [x] O6 route-conductance blocker
- [x] Inventory N06 closeout artifacts:
  - [x] candidate route records
  - [x] native route-arbitration records
  - [x] context/affordance evidence
  - [x] selected/rejected route digests
- [x] Inventory N07 closeout artifacts:
  - [x] ID6 support/identity evidence
  - [x] support area digests
  - [x] bounded non-destructive exchange records
- [x] Inventory N08 closeout artifacts:
  - [x] Hypothesis A artifact-only serialized memory/trail closeout
  - [x] Hypothesis B bounded static geometry response closeout
  - [x] native route-conductance policy blocker
- [x] Inventory available native/producers surfaces for proxy measurement.
- [x] Inventory available native/producers surfaces for proxy-conditioned
      action eligibility.
- [x] Inventory missing native goal-proxy regulation policy surfaces.
- [x] Record Hypothesis B staged status and initial native-absorption blocker:
      `native_goal_proxy_regulation_policy_missing`.
- [x] Inventory whether N08 memory surfaces can be consumed as regulation
      evidence.
- [x] Inventory N07 identity/support fields required for preservation or
      disruption tags.
- [x] Inventory N05 oscillator amplitude fields and mark oscillator regulation
      as default-deferred or available as a secondary fixture.
- [x] Freeze GPR row schema.
- [x] Freeze regulation outcome taxonomy.
- [x] Freeze ceiling algorithm.
- [x] Freeze N10 handoff field list.
- [x] Freeze claim flags.
- [x] Ensure no regulation probe is run in Iteration 1.

Expected artifacts:

- [x] `outputs/n09_iteration_1_baseline_inventory.json`
- [x] `reports/n09_iteration_1_baseline_inventory.md`

Acceptance statement:

```text
Iteration 1 passes if N09 has a source-backed inventory of inherited
N05/N06/N07/N08 artifacts, available proxy/regulation surfaces, missing native
policy surfaces, Hypothesis B staged status, memory and identity/support source
fields, frozen GPR row schema, regulation outcome taxonomy, ceiling algorithm,
N10 handoff fields, clean claim boundaries, and no regulation probe execution.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/build_n09_iteration_1_baseline_inventory.py`.
- Generated `outputs/n09_iteration_1_baseline_inventory.json`.
- Generated `reports/n09_iteration_1_baseline_inventory.md`.
- Source-backed inventory reads:
  - N05 O5/O6 closeout:
    `n05_iteration_7_o5_self_sustained_boundary.json`,
    `n05_iteration_8_o6_closeout.json`
  - N06 SC6 closeout:
    `n06_iteration_8_sc6_closeout.json`
  - N07 ID6 support/identity closeout:
    `n07_iteration_11b_neutral_absorber_reservoir.json`,
    `n07_iteration_12_long_horizon_compatibility_closeout.json`
  - N08 Hypothesis A/B closeouts:
    `n08_iteration_4_mem2_memory_surface.json`,
    `n08_iteration_7_mem5_repeated_memory_selection.json`,
    `n08_iteration_8_mem6_closeout.json`,
    `n08_iteration_13_native_geometry_trail_closeout.json`
- Recorded N08 Hypothesis A as consumable for N09 memory-shaped regulation
  only as serialized producer/policy memory evidence.
- Recorded N08/N07 support-anchor consistency:
  N08 memory-surface source support digests match the N07 support-area digest,
  and the target support digest matches the N07 11-B B-support-area digest.
- Recorded N08 Hypothesis B as staged and not discarded:
  B0 inventory complete, B1 substrate-mediated probe planned after A-path
  load-bearing variables are known, and B2 full native absorption blocked by
  `native_goal_proxy_regulation_policy_missing`.
- Enumerated B0 considered surfaces for Hypothesis B rather than treating B0
  completeness as an unchecked assertion.
- Recorded default proxy-measurement surfaces:
  `active_node_coherence_band`, `route_arbitration_context_surface`,
  `n08_serialized_memory_surface_strength`, `n07_identity_support_area`, and
  `n05_oscillator_return_amount`.
- Recorded proxy-conditioned action surfaces:
  `producer_scheduling_eligibility_record`,
  `native_route_candidate_score_components`,
  `n08_memory_shaped_candidate_score_components`, and
  `n08_static_positive_geometry_route_response`.
- Frozen GPR schema includes proxy, error, response, memory, identity/support,
  budget, source, and claim-flag fields.
- Frozen outcome taxonomy includes negative and partial classes:
  `no_response_to_error`, `wrong_direction_response`,
  `overshoot_oscillation`, `saturation_no_recovery`, `policy_saturation`,
  `memory_poisoning`, `identity_disrupted_under_regulation`,
  `identity_preserved_under_regulation`, and `native_policy_gap`.
- Frozen ceiling algorithm records highest passing GPR rung with fallback
  blocker, while identity/support disruption blocks N10 consumption without
  automatically erasing lower valid N09 proxy-regulation evidence.
- Recorded review-hardening constraints:
  - N06 route arbitration is selection-only for N09 and supplies no inherited
    scheduled/processed packet evidence for GPR4+.
  - N06 unknown-source rejection carries forward as
    `native_route_candidate_committed_source_surface_required`.
  - N07 withdrawal stability is not tested, so N09 must supply its own
    identity/support withdrawal baseline or control before using disruption
    tags for N10 handoff.
  - N07 `support_dependency_status` is recorded for N09 identity/support
    preservation and disruption checks.
  - N05 oscillator amplitude inventory includes return amount, return route,
    cycle basis, route aspect, channel sequence, route edges, causal-delay
    status, and amplification-accounting status.
- Stable inventory digest scope excludes generated timestamp, inventory digest,
  and git metadata so the inventory content digest is not changed by unrelated
  worktree state.
- N10 handoff fields are frozen with snake_case names:
  `mechanism_status_tags` and `native_policy_gap_records`.
- No N09 regulation probe was run.
- No `src/*` changes were made.

Run record:

```text
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/build_n09_iteration_1_baseline_inventory.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/build_n09_iteration_1_baseline_inventory.py
.venv/bin/python -m json.tool experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_1_baseline_inventory.json
git diff --check -- experiments/2026-05-N09-lgrc-goal-proxy-regulation
```

Focused assertion result:

```json
{
  "status": "passed",
  "checks": 34,
  "n06_packet_inherited": false,
  "n07_withdrawal": "not_tested",
  "support_anchor_ok": true,
  "b0_surfaces": 4
}
```

Inventory digest:

```text
78865ce35a12e73d1071b6a124a262e0fb946f90a77e997e505f4245358fd7a3
```

Artifact SHA-256:

```text
4d4a702f7d9eeaf9fc9d63f133ff4be751a8a21a11b5adef9c0ac18b853078c8  scripts/build_n09_iteration_1_baseline_inventory.py
edc727a034e4216262ed7e2f6c3e95ad99765d66d50de97ccaa89c32ef8b3c4c  outputs/n09_iteration_1_baseline_inventory.json
8981f040243ddd4c97002e9086ebfd7abee726ceff3160468538bb49eeb9bbf0  reports/n09_iteration_1_baseline_inventory.md
```

## Iteration 2. Fixture Manifest And Proxy-Regulation Contract

Status: Passed.

- [x] Define proxy surface row schema.
- [x] Define target-band schema.
- [x] Define error metric and error policy schema.
- [x] Define regulation policy schema.
- [x] Define memory-shaped lane and no-memory comparator lane.
- [x] Define route/producer evidence fields.
- [x] Define packet/scheduling response fields.
- [x] Define proxy budget and node-plus-packet budget separation.
- [x] Define perturbation amplitude/duration schema.
- [x] Define support-withdrawal depth/duration schema.
- [x] Define identity/support outcome tags.
- [x] Define regulation outcome taxonomy.
- [x] Define ceiling algorithm.
- [x] Define N10 handoff artifact fields.
- [x] Mark oscillator regulation fixture as deferred secondary fixture unless
      explicitly selected.
- [x] Define artifact-only replay requirements.
- [x] Define negative controls and distinct blockers.
- [x] Define default fixture family.

Expected artifacts:

- [x] `configs/n09_fixture_manifest_v1.json`
- [x] `outputs/n09_iteration_2_fixture_manifest_validation.json`
- [x] `reports/n09_iteration_2_fixture_manifest_validation.md`

Acceptance statement:

```text
Iteration 2 passes if N09 has a replayable proxy-regulation fixture contract
with target/error policies, producer/route boundaries, budget separation,
memory/no-memory lanes, perturbation/support schemas, identity/support outcome
tags, ceiling algorithm, N10 handoff fields, controls, and claim flags frozen
before any positive regulation probe.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/build_n09_iteration_2_fixture_manifest.py`.
- Generated `configs/n09_fixture_manifest_v1.json`.
- Generated `outputs/n09_iteration_2_fixture_manifest_validation.json`.
- Generated `reports/n09_iteration_2_fixture_manifest_validation.md`.
- Defined the default fixture family as
  `n09_default_active_node_band_regulation_v1`, a directly budget-auditable
  active-node coherence band before oscillator-return or multi-variable
  fixtures.
- Froze proxy surface, target-band, error-signal, regulation-policy, and
  regulation-response schemas with canonical digest rules.
- Excluded `n07_identity_support_area` from `allowed_proxy_kinds` because it is
  not runtime-visible and is an identity/support anchor rather than a regulated
  variable surface.
- Added validation that all allowed proxy kinds are runtime-visible and that
  route-arbitration-context proxy use carries the GPR4+ scheduling/processing
  constraint.
- Required the memory-shaped lane and no-memory comparator lane for GPR3+.
  The comparator must use the same proxy, target, and policy and must not read
  a memory surface.
- Attached memory-lane fields to the regulation response schema and mapped N09
  field names to N08 source names: `memory_policy_digest` and
  `memory_strength`.
- Added memory-budget and identity/support join fields to regulation response
  rows, with nullable/no-memory semantics recorded in the manifest.
- Preserved the N06 boundary: route arbitration may provide selection
  evidence, but N09 cannot inherit scheduled/processed packet evidence from
  N06. GPR4+ must produce its own scheduled and processed packet chain.
- Preserved the N06 committed-source blocker:
  `native_route_candidate_committed_source_surface_required`.
- Recorded that N06 closeout rows do not serialize direct
  `candidate_budget_prediction`; missing prediction now has the distinct
  blocker `candidate_budget_prediction_missing`.
- Defined route/producer evidence fields and packet scheduling/processing
  response fields. Producers may schedule only; `step()` remains the mutation
  boundary.
- Added a structured `producer_record_linkage_schema` with causal surface
  digest, reason code, scheduler event index, and scheduled packet id.
- Separated node-plus-packet budget, proxy budget, and N08 memory budget.
  Proxy or memory bookkeeping cannot repair node-plus-packet drift.
- Added perturbation amplitude/duration schema and support-withdrawal
  depth/duration schema.
- Added perturbation recovery fields:
  `expected_recovery_window_count` and `recovery_success_criterion`.
- Added `support_withdrawal_kind` and support-withdrawal kind values.
- Preserved the N07 withdrawal gap:
  `n07_identity_withdrawal_baseline_not_available`.
- Revalidated N08/N07 support-anchor consistency in the Iteration 2 validation
  checks.
- Declared the regulation-policy digest field/rule and recorded the strict
  `1e-9` error threshold as a serialized baseline design choice.
- Inherited the Iteration 1 regulation outcome taxonomy, ceiling algorithm,
  GPR ladder, N10 handoff fields, and claim flags.
- Marked oscillator-return regulation as a deferred secondary fixture requiring
  explicit opt-in.
- Added artifact-only replay requirements for the ordered chain from fixture
  manifest through proxy, target, error, optional perturbation/withdrawal,
  route/producer evidence, scheduled/processed packet, post-response proxy row,
  and response artifact.
- Added 28 negative controls with distinct primary blockers.
- Recorded native policy gaps without promoting any native goal-proxy claim.
- No N09 regulation probe was run.
- No positive regulation evidence was generated.
- No `src/*` changes were made.

Run record:

```text
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/build_n09_iteration_2_fixture_manifest.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/build_n09_iteration_1_baseline_inventory.py experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/build_n09_iteration_2_fixture_manifest.py
.venv/bin/python -m json.tool experiments/2026-05-N09-lgrc-goal-proxy-regulation/configs/n09_fixture_manifest_v1.json
.venv/bin/python -m json.tool experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_2_fixture_manifest_validation.json
git diff --check -- experiments/2026-05-N09-lgrc-goal-proxy-regulation
```

Focused assertion result:

```json
{
  "status": "passed",
  "checks": 46,
  "controls": 28,
  "n07_proxy_allowed": false,
  "perturbation_recovery_fields": true,
  "memory_response_fields": true
}
```

Manifest digest:

```text
084925ff201f49c53db6040e22fa9970736ca9a5e7ad4d090165966bd8efab2a
```

Validation digest:

```text
6c49700ab9f3a735bbfe2fec2b88b5e0c6920fc935fd896b5587e6f1dc9059ac
```

Artifact SHA-256:

```text
f0a62c88aa692581fd766822dd0c9c5186cdd74484d27100d7aa7026059d815a  scripts/build_n09_iteration_2_fixture_manifest.py
e8ac646605f8524e344f378ae060bb6c25420c6701024f8802a7972e77d59c45  configs/n09_fixture_manifest_v1.json
87be43f215007ea760b001b471795b2ebe1bb2a639d69d84a2c5bf25020f72d7  outputs/n09_iteration_2_fixture_manifest_validation.json
14ff4572e151bfe6aca80611d3cae9fa3dec380b51c42333d95cd671584cf867  reports/n09_iteration_2_fixture_manifest_validation.md
```

## Iteration 3. GPR1 Proxy Measurement

Status: Passed.

- [x] Emit proxy measurement rows from runtime-visible state.
- [x] Serialize regulated variable, target band, event order, and digest.
- [x] Confirm measurement is not hidden fixture/report state.
- [x] Keep regulation action disabled.
- [x] Controls: missing proxy surface, digest mismatch, hidden proxy target,
      post-hoc target change, claim promotion.
- [x] Additional control: hidden proxy source rejected.

Expected artifacts:

- [x] `outputs/n09_iteration_3_gpr1_proxy_measurement.json`
- [x] `reports/n09_iteration_3_gpr1_proxy_measurement.md`

Acceptance statement:

```text
Iteration 3 passes if a runtime-visible proxy condition and declared target
band are serialized with digest and order evidence, without regulation action
or claim promotion.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n09_iteration_3_gpr1_proxy_measurement.py`.
- Generated `outputs/n09_iteration_3_gpr1_proxy_measurement.json`.
- Generated `reports/n09_iteration_3_gpr1_proxy_measurement.md`.
- Used a live `LGRC9V3.from_state(...)` runtime snapshot as the proxy
  measurement source.
- Measured `source_reservoir_node_coherence` from
  `LGRC9V3.get_state().base_state.nodes[source_node_id].coherence`.
- Serialized target band `0.45 <= coherence <= 0.55` from the Iteration 2
  manifest's declared target-band policy.
- Recorded measurement value `0.62` as `above_target_band`, but did not compute
  a GPR2 error signal.
- Recorded GPR level `GPR1` and claim ceiling
  `goal_proxy_measurement_candidate`.
- Recorded proxy surface digest
  `4c0ed3d7a3a70607a1d8b4f175025d895cb7d190160dc0f1fc7cb9136157636f`.
- Recorded target band digest
  `72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b`.
- Recorded runtime state digest
  `9995d3daaca6b3bb84f7fdaa187ddba96f2e1d39c97b86781b7907b7d081406d`.
- Recorded packet ledger digest
  `905a83adfb01428f82e6fff5bb6212d574a162c1b716ee772adf213f0f3d3362`.
- Recorded artifact digest
  `43056efa42ed16f0dee246ec6b1f27ec9291560b8ef8a03d057c11bdd173cceb`.
- Confirmed `node_plus_packet_budget_error = 0.0`.
- Confirmed no regulation action, no error signal, no producer scheduling, no
  scheduled packets, no processed packets, no `step()` call, and no state
  mutation after measurement.
- Confirmed all claim flags remain `false`.
- Controls passed with distinct blockers:
  - `missing_proxy_surface -> proxy_surface_missing`
  - `proxy_surface_digest_mismatch -> proxy_surface_digest_mismatch`
  - `hidden_proxy_target -> hidden_proxy_target_rejected`
  - `posthoc_target_change -> posthoc_target_change_rejected`
  - `claim_promotion -> claim_promotion_blocked`
  - `hidden_proxy_source -> hidden_proxy_source_rejected`

Run record:

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_3_gpr1_proxy_measurement.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_3_gpr1_proxy_measurement.py
```

Focused assertion:

```text
n09_iteration_3_gpr1_proxy_measurement_assertions_passed
```

SHA-256:

```text
9544e48fe324d070d9f0fe375d925b5bdbce6f05842998a5e52db9da43e85177  scripts/run_n09_iteration_3_gpr1_proxy_measurement.py
29a3ea964ef38f1eae1be1b5d420453a5119c02dde6e5174328341ddd2c7df15  outputs/n09_iteration_3_gpr1_proxy_measurement.json
3537c4ddacaf4820d229e421d6dfa045df7d2f502f7d42d682d35c298ee3138f  reports/n09_iteration_3_gpr1_proxy_measurement.md
```

## Iteration 4. GPR2 Error Signal

Status: Passed.

- [x] Compute proxy error from serialized measurement and target band.
- [x] Serialize error metric, error value, and policy digest.
- [x] Verify error recomputes from artifacts.
- [x] Controls: proxy error mismatch, hidden reward input, post-hoc threshold,
      order inversion, claim promotion.
- [x] Additional control: missing error policy rejected.

Expected artifacts:

- [x] `outputs/n09_iteration_4_gpr2_error_signal.json`
- [x] `reports/n09_iteration_4_gpr2_error_signal.md`

Acceptance statement:

```text
Iteration 4 passes if proxy error is computed from serialized runtime-visible
evidence under a declared policy and all hidden reward/target controls fail
closed.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n09_iteration_4_gpr2_error_signal.py`.
- Generated `outputs/n09_iteration_4_gpr2_error_signal.json`.
- Generated `reports/n09_iteration_4_gpr2_error_signal.md`.
- Consumed the serialized Iteration 3 proxy row and target-band row as the
  only measurement inputs.
- Did not read live LGRC runtime state and did not inspect the Iteration 3
  runtime-state snapshot for error computation.
- Used the Iteration 2 manifest error policy
  `n09_signed_band_error_policy_v1`.
- Computed `signed_distance_to_declared_band` from
  `measurement_value = 0.62`, `upper_bound = 0.55`, producing
  `error_value = 0.07`.
- Recorded `error_direction = decrease_proxy` and `in_band = false`.
- Recorded GPR level `GPR2` and claim ceiling `proxy_error_signal_candidate`.
- Recorded error signal digest
  `a82a3a9c72aacfe7935c8f332d333aef0eb44d26982ced4040539403cfc09e48`.
- Recorded artifact digest
  `1391fa2fb8434a3e96df84bf175bc88c57f946b3d3fb3775f72f8313671f3044`.
- Confirmed source Iteration 3 artifact digest recomputes.
- Confirmed proxy row digest, target-band digest, error-policy digest, and
  error-signal digest recompute.
- Confirmed no regulation action, no eligibility/route evidence, no producer
  scheduling, no scheduled packets, no processed packets, no `step()` call,
  and no state mutation.
- Confirmed all claim flags remain `false`.
- Controls passed with distinct blockers:
  - `proxy_error_mismatch -> error_signal_digest_mismatch`
  - `hidden_reward_input -> hidden_reward_or_goal_label_rejected`
  - `posthoc_threshold_change -> posthoc_target_change_rejected`
  - `order_inversion -> artifact_order_inversion`
  - `claim_promotion -> claim_promotion_blocked`
  - `error_policy_missing -> error_policy_missing`

Run record:

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_4_gpr2_error_signal.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_4_gpr2_error_signal.py
```

Focused assertion:

```text
n09_iteration_4_gpr2_error_signal_assertions_passed
```

SHA-256:

```text
b92c6552e9c58f78c46f03e2a550f983ac025ccf7e765506a5ae6877f7656cc9  scripts/run_n09_iteration_4_gpr2_error_signal.py
dff8dac7dc821cff08c802b0505a9548ab3f2902de6d736e04d2c79775707fc7  outputs/n09_iteration_4_gpr2_error_signal.json
d8cb8687d6abc04f432f27e31332b954b1a9ca38fed839b7d5fdd7971ac5ce41  reports/n09_iteration_4_gpr2_error_signal.md
```

## Iteration 5. GPR3 Proxy-Conditioned Eligibility

Status: Passed.

- [x] Show route candidate, producer eligibility, or schedule request changes
      because of proxy error.
- [x] Include a memory-shaped lane consuming N08 Hypothesis A memory evidence.
- [x] Include a no-memory comparator lane using the same proxy, target, and
      policy.
- [x] Record whether memory changes eligibility or response classification.
- [x] Record mechanism status tags.
- [x] Verify producer does not mutate state.
- [x] Compare with no-error or wrong-error controls.
- [x] Controls: experiment-side if/else, hidden proxy, producer mutation,
      stale proxy read, memory surface missing, memory surface not used,
      claim promotion.
- [x] Additional control: no-memory lane must not read memory surface.

Expected artifacts:

- [x] `outputs/n09_iteration_5_gpr3_proxy_conditioned_eligibility.json`
- [x] `reports/n09_iteration_5_gpr3_proxy_conditioned_eligibility.md`

Acceptance statement:

```text
Iteration 5 passes if proxy error changes eligibility or route evidence through
serialized runtime-visible inputs while preserving the producer/step boundary
and claim boundaries, and if the memory-shaped lane is explicitly compared
against a no-memory control.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n09_iteration_5_gpr3_proxy_conditioned_eligibility.py`.
- Generated `outputs/n09_iteration_5_gpr3_proxy_conditioned_eligibility.json`.
- Generated `reports/n09_iteration_5_gpr3_proxy_conditioned_eligibility.md`.
- Consumed `outputs/n09_iteration_4_gpr2_error_signal.json` as the serialized
  proxy/error input.
- Consumed N08 Hypothesis A evidence from
  `n08_iteration_7_mem5_repeated_memory_selection.json`.
- Used regulation policy `n09_proxy_error_threshold_schedule_policy_v1`.
- Recorded GPR level `GPR3` and claim ceiling
  `proxy_conditioned_route_selection_candidate`.
- Built two paired lanes with the same proxy surface digest, target-band digest,
  error-signal digest, and regulation-policy digest:
  - memory-shaped lane:
    `n09_memory_shaped_proxy_regulation_lane_v1`
  - no-memory comparator:
    `n09_no_memory_proxy_regulation_comparator_v1`
- Memory-shaped lane consumed N08 serialized memory evidence:
  - memory surface digest:
    `b21c093d70245fab02088b8ebed42ac931629c41f6e45d618f5b5a67d9bea627`
  - memory policy digest:
    `bd003905a6c189a1c44babbeb80d931b2dd4d3ce27eb3b1788aefbaefb8198eb`
  - memory strength: `0.7`
- No-memory comparator used the same proxy, target, error, and policy but kept
  memory surface fields null/zero.
- Recorded no-memory candidate scores `[1.07, 1.07]`, producing
  `no_memory_proxy_conditioned_eligibility_tied_candidates`.
- Recorded memory-shaped candidate scores `[1.825, 1.87]`, producing
  `memory_shaped_proxy_conditioned_eligibility_ranked_candidates`.
- Confirmed memory changes candidate ranking, while remaining score evidence
  only and not physical flux or node-plus-packet budget.
- Recorded memory-shaped candidate set digest
  `134e35907533c2da88e567dfcfa83db5e68b885f55c25f6c09e478395f328ffa`.
- Recorded no-memory candidate set digest
  `a0b0828fcadc58fbc69af2dfc2ca74973870abb8fd04e6ed999d7b32749ccfb1`.
- Recorded artifact digest
  `d8ee8a31d7fa739c91a0cdc30823af9b8a361c700066592cc353a5fe22633d29`.
- Confirmed candidate route digests, candidate set digests, producer record
  digests, score component sums, source GPR2 digest, regulation policy digest,
  and error-signal digest recompute.
- Confirmed candidate budget predictions are present and have
  `node_plus_packet_budget_error = 0.0`.
- Confirmed producer linkage fields are present:
  `causal_surface_digest`, `reason_code`, `scheduler_event_index`, and
  `scheduled_packet_id`.
- Confirmed no route-arbitration record, no committed route selection, no
  topology event, no schedule request, no scheduled packet, no processed
  packet, no producer scheduling, no `step()` call, no state mutation, and no
  packet-ledger mutation.
- Confirmed all claim flags remain `false`.
- Controls passed with distinct blockers:
  - `experiment_side_if_else -> experiment_side_if_else_rejected`
  - `hidden_proxy -> hidden_proxy_source_rejected`
  - `producer_mutation -> producer_direct_mutation_blocked`
  - `stale_proxy_read -> stale_proxy_read_blocked`
  - `memory_surface_missing -> memory_surface_missing_for_memory_lane`
  - `memory_surface_not_used -> memory_surface_not_used`
  - `memory_surface_read_in_no_memory_lane -> memory_surface_read_in_no_memory_lane`
  - `no_error_control -> no_error_non_trigger`
  - `wrong_error_control -> wrong_direction_response`
  - `claim_promotion -> claim_promotion_blocked`

Run record:

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_5_gpr3_proxy_conditioned_eligibility.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_5_gpr3_proxy_conditioned_eligibility.py
```

Focused assertion:

```text
n09_iteration_5_gpr3_proxy_conditioned_eligibility_assertions_passed
```

SHA-256:

```text
b8842e14b204472890689551bab815ca53a8ae3aeed2397ecdef7cf4829581f7  scripts/run_n09_iteration_5_gpr3_proxy_conditioned_eligibility.py
7d31f6d593cc43ec15223292cb70e8981a503b17276a1f0f9a2823a1850b5242  outputs/n09_iteration_5_gpr3_proxy_conditioned_eligibility.json
2aa27635dbaadbb90f365fa0071952d1b238c620b8d67431196e99b539285435  reports/n09_iteration_5_gpr3_proxy_conditioned_eligibility.md
```

## Iteration 6. GPR4 Single-Cycle Correction

Status: Passed.

- [x] Process one selected correction action through LGRC scheduling/step
      where packet work is used.
- [x] Measure proxy state before and after.
- [x] Verify response direction is correct relative to error.
- [x] Verify exact node-plus-packet budget accounting.
- [x] Controls: wrong-direction response, no response to error, direct rewrite,
      budget discontinuity, claim promotion.

Expected artifacts:

- [x] `outputs/n09_iteration_6_gpr4_single_cycle_correction.json`
- [x] `reports/n09_iteration_6_gpr4_single_cycle_correction.md`

Acceptance statement:

```text
Iteration 6 passes if one proxy-conditioned action causes a replayable,
budget-safe proxy-state response in the expected direction without direct
producer mutation or claim promotion.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n09_iteration_6_gpr4_single_cycle_correction.py`.
- Generated `outputs/n09_iteration_6_gpr4_single_cycle_correction.json`.
- Generated `reports/n09_iteration_6_gpr4_single_cycle_correction.md`.
- Consumed Iteration 5 GPR3 output as serialized proxy-conditioned
  eligibility evidence.
- Consumed Iteration 4 GPR2 output for the proxy surface and target-band
  records.
- Selected the top-ranked memory-shaped Iteration 5 candidate:
  - route source id: `route_b`
  - selected candidate route digest:
    `c6901dc48bc5862977cc9d9da4607e0a763ffd378f35459e9b5800265646a74d`
  - selected candidate route score: `1.87`
  - selection policy:
    `highest_memory_shaped_candidate_score_from_iteration_5`
  - semantic-choice claim: `false`
- Scheduled one LGRC packet through native packet scheduling:
  - packet id: `lgrc9v3-packet-9c24c0be8ffcfd9f`
  - source node id: `0`
  - target node id: `2`
  - edge id: `2`
  - packet amount: `0.07`
  - departure event time key: `1.0`
  - arrival event time key: `2.0`
  - scheduler event index: `1`
- Processed the packet through two `step()` calls:
  - departure step
  - arrival/settlement step
- Recorded GPR level `GPR4` and claim ceiling
  `single_cycle_proxy_correction_candidate`.
- Recorded proxy measurement before correction: `0.62`.
- Recorded proxy measurement after correction: `0.55`.
- Recorded target band `[0.48, 0.55]`.
- Recorded error before correction: `0.07`.
- Recorded error after correction: `0.0`.
- Recorded error reduction: `0.07`.
- Recorded response tag `single_cycle_band_return`.
- Confirmed response direction was correct relative to the serialized error:
  `decrease_proxy`.
- Confirmed final event queue count `0` and final in-flight packet total
  `0.0`.
- Confirmed node-plus-packet budget before `1.5`, after `1.5`, with error
  `0.0`.
- Confirmed no route-arbitration record, no topology event, no direct producer
  mutation, no direct state rewrite, and no claim promotion.
- Recorded regulation response digest
  `0fb4b387ee17274f1295070d8324cfcbd8c33550f7db66e1dfb874401994c24a`.
- Recorded packet response digest
  `3733406f9e3bb04765ee6844e5986d96532aec3bbc8430b9048ebba1e7f16ca0`.
- Recorded post-correction proxy surface digest
  `c3d14108fce03673d8a2740c2908a36f40992857f25a3a193695a69742171c5f`.
- Recorded artifact digest
  `3a614aa68353396240b24975b4207993a2af6448c5c362baf7afe77925c9e2b9`.
- Controls passed with distinct blockers:
  - `wrong_direction_response -> wrong_direction_response`
  - `no_response_to_error -> no_response_to_error`
  - `direct_rewrite -> direct_rewrite_blocked`
  - `budget_discontinuity -> node_plus_packet_budget_discontinuity`
  - `scheduled_packet_missing -> scheduled_packet_missing`
  - `processed_packet_missing -> processed_packet_missing`
  - `claim_promotion -> claim_promotion_blocked`
  - `positive_response_reduces_error -> single_cycle_error_not_reduced`
- Confirmed all claim flags remain `false`, including movement,
  semantic-choice, agency, agentic-like, goal-proxy-regulation,
  identity-acceptance, locomotion-like, biological, and ant-colony claims.

Run record:

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_6_gpr4_single_cycle_correction.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_6_gpr4_single_cycle_correction.py
```

Focused assertion:

```text
n09_iteration_6_gpr4_single_cycle_correction_assertions_passed
```

SHA-256:

```text
a6e0b2b13760b9f1409c5edfab51bea3803667ac1d12c280d418aa073edf4762  scripts/run_n09_iteration_6_gpr4_single_cycle_correction.py
49570e9cb1210c4f334faf8947deb4eb11acba119bb8c8e03ae389252de88f88  outputs/n09_iteration_6_gpr4_single_cycle_correction.json
b0a74dbf8e3dd5810cf7d90b5f1092bb3d599d0c3727adeeff69074d921e5ceb  reports/n09_iteration_6_gpr4_single_cycle_correction.md
```

## Iteration 7. GPR5 Repeated Bounded Regulation

Status: Passed.

- [x] Run repeated regulation windows under the same serialized policy.
- [x] Track boundedness, overshoot, saturation, oscillation, or failure.
- [x] Classify each run with the regulation outcome taxonomy.
- [x] Compare against no-regulation and wrong-policy controls.
- [x] Compare memory-shaped repeated regulation against no-memory repeated
      regulation where applicable.
- [x] Preserve identity/support and memory provenance where used.
- [x] Controls: duplicate proxy update, stale proxy read, hidden target drift,
      cross-cycle leakage, budget drift, claim promotion.

Expected artifacts:

- [x] `outputs/n09_iteration_7_gpr5_repeated_bounded_regulation.json`
- [x] `reports/n09_iteration_7_gpr5_repeated_bounded_regulation.md`

Acceptance statement:

```text
Iteration 7 passes if repeated proxy-conditioned cycles keep the proxy bounded
or characterize the failure mode with artifact-visible evidence and distinct
controls, including memory/no-memory comparison when memory is used.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n09_iteration_7_gpr5_repeated_bounded_regulation.py`.
- Generated `outputs/n09_iteration_7_gpr5_repeated_bounded_regulation.json`.
- Generated `reports/n09_iteration_7_gpr5_repeated_bounded_regulation.md`.
- Consumed Iteration 5 GPR3 proxy-conditioned eligibility evidence.
- Consumed Iteration 6 GPR4 single-cycle packet-correction evidence.
- Used the same regulation policy digest across all windows:
  `896133e8af4cdbb6cabb1436d9cb6f41a2ad1ad300f0ceca79f460d392358d40`.
- Used the same target-band digest across all windows:
  `72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b`.
- Ran four serialized regulation windows.
- Each window used an explicit serialized disturbance packet of amount `0.07`
  to move the source-reservoir proxy above the target band before correction.
- Memory-shaped lane:
  - consumed N08 memory evidence from the Iteration 5 memory lane;
  - reused selected route source id `route_b`;
  - reused selected candidate route digest
    `c6901dc48bc5862977cc9d9da4607e0a763ffd378f35459e9b5800265646a74d`;
  - scheduled and processed one correction packet per window through LGRC
    scheduling and `step()`;
  - recorded pre-correction measurements `[0.62, 0.62, 0.62, 0.62]`;
  - recorded post-correction measurements `[0.55, 0.55, 0.55, 0.55]`;
  - recorded post-correction errors `[0.0, 0.0, 0.0, 0.0]`;
  - recorded max post-correction error `0.0`;
  - recorded max node-plus-packet budget error `0.0`;
  - classified the lane as `bounded_repeated_regulation`.
- No-memory comparator lane:
  - used the same window inputs, proxy surface, target band, and regulation
    policy;
  - preserved the Iteration 5 no-memory candidate tie;
  - recorded blocker `no_memory_candidate_tie_unresolved`;
  - scheduled no correction packets;
  - recorded measurements after window inputs `[0.62, 0.69, 0.76, 0.83]`;
  - recorded errors after window inputs `[0.07, 0.14, 0.21, 0.28]`;
  - classified the comparator as `policy_saturation`.
- Recorded GPR level `GPR5` and claim ceiling
  `repeated_bounded_proxy_regulation_candidate`.
- Recorded the mechanism tags:
  `producer_mediated`, `threshold_authorized`, `memory_shaped`,
  `native_policy_gap`.
- Recorded native-policy gap
  `repeated_proxy_regulation_policy_not_constitutive_native`.
- Recorded identity/support outcome as not tested under regulation; no
  identity-support evidence was consumed in this iteration.
- Confirmed no route-arbitration record, no topology event, no direct producer
  mutation, no direct state rewrite, no semantic-choice claim, no
  goal-understanding claim, and no claim promotion.
- Recorded artifact digest
  `887befc2df4e6c729076e45057ac12f041a941953c66939c97d17d725ef66746`.
- Memory cycle digests:
  - `189bca5547434e31a39ed98a7bcbb0f93c6b535c99d2ce69ebdd7b59198b8327`
  - `2f4592d7eb1ee8b27b0b2b33eb452e0fc2d04b21b2f20b29716ba01227084b19`
  - `291dc7e30436d2ad5e7abb3659221f411a2e54833d52050e20156adad444dc38`
  - `ee26c9171e8df5ef587cefed6de8975e58932ec9f86cfa14e6fe3d9d0027dc78`
- Controls passed with distinct blockers:
  - `duplicate_proxy_update -> duplicate_proxy_update`
  - `stale_proxy_read -> stale_proxy_read_blocked`
  - `hidden_target_drift -> hidden_target_drift`
  - `cross_cycle_leakage -> cross_cycle_leakage`
  - `budget_drift -> budget_drift`
  - `claim_promotion -> claim_promotion_blocked`
  - `no_regulation_control -> no_response_to_error`
  - `wrong_policy_control -> wrong_direction_response`
- Confirmed all claim flags remain `false`, including movement,
  semantic-choice, goal-proxy-regulation, semantic-goal-understanding, agency,
  agentic-like, identity-acceptance, locomotion-like, biological, ant-colony,
  personhood, and unrestricted claims.

Run record:

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_7_gpr5_repeated_bounded_regulation.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_7_gpr5_repeated_bounded_regulation.py
```

Focused assertion:

```text
n09_iteration_7_gpr5_repeated_bounded_regulation_assertions_passed
```

SHA-256:

```text
f9d0427d088acae9f75ac44340f0f06e92266bb254cc910c3fc8ce82ee053c4e  scripts/run_n09_iteration_7_gpr5_repeated_bounded_regulation.py
0aa631930ff59776764fd3147285669eb006942ee656e27b1b748dbe3e2bf483  outputs/n09_iteration_7_gpr5_repeated_bounded_regulation.json
3efb750baaf35095eafe2b9595bbf2d0de4750115fe4f0930b77b860da7c4fba  reports/n09_iteration_7_gpr5_repeated_bounded_regulation.md
```

## Iteration 8. Perturbation, Withdrawal, And Support Checks

Status: Passed.

- [x] Apply small perturbation to the regulated proxy condition.
- [x] Serialize perturbation magnitude and duration.
- [x] Test recovery or bounded degradation.
- [x] Weaken or withdraw scaffolded support where meaningful.
- [x] Serialize support-withdrawal depth and duration where used.
- [x] Verify source/support specificity if N07 evidence is consumed.
- [x] Record identity/support outcome tag:
      `identity_preserved_under_regulation`,
      `identity_disrupted_under_regulation`,
      `identity_not_tested_under_regulation`, or
      `identity_support_withdrawal_baseline_missing`.
- [x] Controls: unsupported recovery, hidden reset, support label only,
      identity acceptance overclaim, claim promotion.

Expected artifacts:

- [x] `outputs/n09_iteration_8_perturbation_withdrawal_support.json`
- [x] `reports/n09_iteration_8_perturbation_withdrawal_support.md`

Acceptance statement:

```text
Iteration 8 passes if regulation recovery or bounded degradation is classified
under perturbation/support changes without identity-acceptance or agency
promotion, and if identity/support preservation or disruption is recorded as a
handoff tag rather than a promoted identity claim.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n09_iteration_8_perturbation_withdrawal_support.py`.
- Generated `outputs/n09_iteration_8_perturbation_withdrawal_support.json`.
- Generated `reports/n09_iteration_8_perturbation_withdrawal_support.md`.
- Consumed Iteration 7 GPR5 repeated bounded regulation evidence.
- Consumed Iteration 5 GPR3 memory-shaped candidate evidence for the selected
  correction route.
- Kept GPR level `GPR5` and claim ceiling
  `repeated_bounded_proxy_regulation_candidate`.
- Applied an explicit serialized perturbation packet:
  - perturbation kind: `serialized_packet_proxy_increase`
  - perturbation amount: `0.09`
  - duration steps: `2`
  - before perturbation proxy measurement: `0.55`
  - after perturbation proxy measurement: `0.64`
  - perturbation error after: `0.09`
- Scheduled one memory-shaped recovery packet through LGRC scheduling and
  processed it through `step()`.
- Recorded post-recovery proxy measurement `0.55`.
- Recorded post-recovery error `0.0`.
- Recorded recovery classification `perturbation_recovered_to_band`.
- Recorded recovery outcome tag `bounded_repeated_regulation`.
- Recorded node-plus-packet budget error `0.0`.
- Serialized the support-withdrawal boundary:
  - support withdrawal kind: `partial_support_weakening`
  - withdrawal depth: `0.25`
  - duration steps: `2`
  - identity/support digest:
    `c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb`
  - identity/support outcome tag:
    `identity_support_withdrawal_baseline_missing`
  - primary blocker:
    `n07_identity_withdrawal_baseline_not_available`
- Recorded that N10 consumption is not allowed from the support-withdrawal
  lane because the N07 withdrawal baseline is unavailable.
- Recorded that lower GPR5 perturbation-recovery evidence remains valid even
  though identity/support withdrawal is baseline-limited.
- Confirmed no route-arbitration record, no topology event, no hidden reset,
  no direct producer mutation, no direct state rewrite, no agency claim, no
  identity-acceptance claim, and no claim promotion.
- Recorded native-policy gaps:
  - `perturbation_recovery_policy_not_constitutive_native`
  - `n07_identity_withdrawal_baseline_not_available`
- Recorded artifact digest
  `f109fe171ccd0e2980ed9cdab5262c40edc250c8dec072fd9c7ea914b9beaff9`.
- Recorded perturbation digest
  `28df8c72d85e9a8c38a91ee9d0d5ff00b8c408bdd5ddf4996ac50e6d25cf0ee4`.
- Recorded support-withdrawal digest
  `8e09a8de0b8d66e57e425a6c15a52abdf2e5090c65878eaf434c0751cc43fd84`.
- Recorded regulation response digest
  `7f33759d102c3eee102f4b32bb515b9d0cf8eecb40cd22057de7c475dcde9d34`.
- Recorded packet response digest
  `8d839e3667b873018aefdefbfa6a40aabb6fbe613a37d7f33a802f853ce82086`.
- Controls passed with distinct blockers:
  - `unsupported_recovery -> unsupported_recovery`
  - `hidden_reset -> hidden_reset_blocked`
  - `support_label_only -> support_label_only_blocked`
  - `identity_acceptance_overclaim -> identity_acceptance_overclaim`
  - `claim_promotion -> claim_promotion_blocked`
  - `hidden_perturbation -> hidden_perturbation_blocked`
  - `budget_discontinuity -> budget_discontinuity`
- Confirmed all claim flags remain `false`, including movement,
  semantic-choice, goal-proxy-regulation, semantic-goal-understanding, agency,
  agentic-like, identity-acceptance, runtime identity acceptance, locomotion,
  biological, ant-colony, personhood, and unrestricted claims.

Run record:

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_8_perturbation_withdrawal_support.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_8_perturbation_withdrawal_support.py
```

Focused assertion:

```text
n09_iteration_8_perturbation_withdrawal_support_assertions_passed
```

SHA-256:

```text
1c67b5d8edd0c6ac631c04c0a43f03cb6e8fcf818e3a34bbb7ef6cca01117116  scripts/run_n09_iteration_8_perturbation_withdrawal_support.py
873114340bf655becf39f47dbbd4758f46204eee05a1fb93a0a7457db3caa472  outputs/n09_iteration_8_perturbation_withdrawal_support.json
9d72834521f0b4f30bc83747992c41acb3eada9661e0d04d0c5a51302e6a710b  reports/n09_iteration_8_perturbation_withdrawal_support.md
```

## Iteration 9. GPR6 Artifact-Only Replay And Closeout

Status: Passed.

- [x] Replay proxy measurement, target/error policy, route/producer evidence,
      packet work, proxy response, budgets, and controls from artifacts only.
- [x] Recompute proxy, error, route, producer, and response digests.
- [x] Freeze strongest N09 ceiling.
- [x] Apply the ceiling algorithm and record primary blocker for any failed
      higher rung.
- [x] Record native-policy gaps if regulation remains scaffolded.
- [x] Emit N10 handoff fields:
  - [x] `goal_proxy_regulation_policy_digest`
  - [x] `proxy_surface_digest`
  - [x] `error_policy_digest`
  - [x] `regulation_response_digest`
  - [x] `memory_surface_digest` if memory-shaped
  - [x] `identity_support_digest` if identity-anchored
  - [x] `mechanism_status_tags`
  - [x] `regulation_outcome_tag`
  - [x] `identity_support_outcome_tag`
  - [x] `native_policy_gap_records`
- [x] Preserve intention, agency, identity acceptance, ACO, locomotion,
      biological, personhood, and unrestricted claims as blocked.

Expected artifacts:

- [x] `outputs/n09_iteration_9_gpr6_closeout.json`
- [x] `reports/n09_iteration_9_gpr6_closeout.md`

Acceptance statement:

```text
Iteration 9 passes if the goal-proxy regulation chain can be reconstructed
from artifacts only, freezing either an artifact_only_goal_proxy_regulation
candidate ceiling or explicit blockers under the ceiling algorithm, emitting
N10 handoff fields, while preserving all stronger intention, agency, identity,
ACO, locomotion, biological, and unrestricted claims as blocked.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n09_iteration_9_gpr6_closeout.py`.
- Generated `outputs/n09_iteration_9_gpr6_closeout.json`.
- Generated `reports/n09_iteration_9_gpr6_closeout.md`.
- Replayed the N09 Hypothesis A chain from artifacts only:
  - fixture manifest;
  - GPR1 proxy surface row and target band;
  - GPR2 error signal;
  - GPR3 memory-shaped route/producer evidence;
  - GPR4 scheduled/processed packet correction;
  - GPR5 repeated bounded regulation;
  - GPR8 perturbation recovery and support-withdrawal boundary.
- Confirmed `artifact_only = true` and `runtime_state_used = false`.
- Recomputed artifact digests for GPR1, GPR2, GPR3, GPR4, GPR5, GPR8, and
  the fixture manifest.
- Recomputed load-bearing row digests:
  - proxy surface rows;
  - target-band row;
  - error-signal row;
  - memory-shaped candidate set;
  - memory-shaped producer record;
  - schedule requests;
  - packet response records;
  - regulation response records;
  - repeated cycle records;
  - perturbation record;
  - support-withdrawal record.
- Confirmed ordered chain reconstruction:
  - artifact dependency order is valid;
  - within-window scheduler order is valid;
  - candidate selection reconstructs from the memory-shaped candidate set;
  - scheduled and processed packet ids reconstruct from packet response
    artifacts;
  - perturbation recovery reconstructs from the serialized perturbation,
    packet response, and post-recovery proxy row.
- Froze strongest N09 Hypothesis A ceiling:
  `artifact_only_goal_proxy_regulation_candidate`.
- Recorded GPR level `GPR6`.
- Recorded Hypothesis A status `closed`.
- Recorded Hypothesis B status `staged_native_policy_gap`.
- Recorded primary Hypothesis B blocker:
  `native_goal_proxy_regulation_policy_missing`.
- Preserved N07 support-withdrawal blocker for N10:
  `n07_identity_withdrawal_baseline_not_available`.
- Recorded that lower GPR5 evidence remains valid despite the support-lane
  blocker.
- Emitted N10 handoff fields:
  - `goal_proxy_regulation_policy_digest`:
    `896133e8af4cdbb6cabb1436d9cb6f41a2ad1ad300f0ceca79f460d392358d40`
  - latest `proxy_surface_digest`:
    `e16abbd31147af9312ff37e4de308c6199ed385a3bbe9d8e441ed275fa82f7af`
  - `error_policy_digest`:
    `61c34d66e9416772b40a8db54dff3cf7a34f5a6ece4a18428a590f8d9594b706`
  - `regulation_response_digest`:
    `7f33759d102c3eee102f4b32bb515b9d0cf8eecb40cd22057de7c475dcde9d34`
  - `memory_surface_digest`:
    `b21c093d70245fab02088b8ebed42ac931629c41f6e45d618f5b5a67d9bea627`
  - `identity_support_digest`:
    `c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb`
  - `mechanism_status_tags`:
    `producer_mediated`, `threshold_authorized`, `memory_shaped`,
    `native_policy_gap`
  - `regulation_outcome_tag`: `bounded_repeated_regulation`
  - `identity_support_outcome_tag`:
    `identity_support_withdrawal_baseline_missing`
  - `native_policy_gap_records`, including native goal-proxy regulation,
    native proxy/error/response policy gaps, native memory-shaped regulation
    surface gap, native identity-preserving regulation validator gap,
    perturbation-recovery constitutive-native gap, and the N07 withdrawal
    baseline gap.
- Recorded N10 consumption:
  - goal-proxy regulation artifact candidate: `true`;
  - identity-support lane consumption allowed: `false`;
  - identity-support primary blocker:
    `n07_identity_withdrawal_baseline_not_available`;
  - Hypothesis A path closed: `true`;
  - Hypothesis B path staged: `true`.
- Controls passed with distinct blockers:
  - `artifact_runtime_fallback -> runtime_state_fallback_blocked`
  - `proxy_digest_mismatch -> proxy_surface_digest_mismatch`
  - `error_mismatch -> proxy_error_mismatch`
  - `route_or_producer_missing -> route_or_producer_evidence_missing`
  - `scheduled_packet_missing -> scheduled_packet_missing`
  - `processed_packet_missing -> processed_packet_missing`
  - `budget_violation -> budget_violation`
  - `support_withdrawal_baseline_missing -> n07_identity_withdrawal_baseline_not_available`
  - `native_policy_gap -> native_goal_proxy_regulation_policy_missing`
  - `claim_promotion -> claim_promotion_blocked`
- Confirmed all claim flags remain `false`, including movement,
  semantic-choice, goal-proxy-regulation, semantic-goal-understanding, agency,
  agentic-like, identity-acceptance, runtime identity acceptance, ACO,
  ant-colony, locomotion, biological, personhood, and unrestricted claims.
- Recorded artifact digest
  `45083c4e9fecc817a8e54a7683828ecc201ade747090f0a519bcb681909eaa88`.

Run record:

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_9_gpr6_closeout.py
.venv/bin/python -m py_compile experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_9_gpr6_closeout.py
```

Focused assertion:

```text
n09_iteration_9_gpr6_closeout_assertions_passed
```

SHA-256:

```text
b3160fc280f37530dbac028f079715826617cd9dfb487d08f51f9020af7a43c2  scripts/run_n09_iteration_9_gpr6_closeout.py
f2023e4b3aa456ac7aa301494b25e4a190226260fb90adc1c292182dccee3b68  outputs/n09_iteration_9_gpr6_closeout.json
9fc0e91a58892746a55d67c0a5d6c0ab29912a40c8790a9f186091d56f7319f0  reports/n09_iteration_9_gpr6_closeout.md
```

## Iteration 10. Hypothesis B0 Native/Substrate Inventory

Status: Passed.

- [x] Reopen the staged Hypothesis B path without changing the closed
      Hypothesis A ceiling.
- [x] Inventory load-bearing A-path variables:
  - [x] proxy surface;
  - [x] target band;
  - [x] error sign and magnitude;
  - [x] response direction;
  - [x] packet correction amount;
  - [x] repeated boundedness;
  - [x] perturbation recovery;
  - [x] memory-shaped route evidence;
  - [x] support/identity anchor.
- [x] Inventory native/substrate ingredients already available from N05-N08
      and current LGRC:
  - [x] N05 oscillation/return channels;
  - [x] N06 route arbitration/context evidence;
  - [x] N07 support/identity anchors;
  - [x] N08 Hypothesis B static geometry response evidence;
  - [x] LGRC packet, flux, conductance, topology, route arbitration, and
        state-reabsorption mechanisms.
- [x] Classify which A-path variables can be represented as native/substrate
      evidence without producer correction scheduling.
- [x] Classify which A-path variables still require serialized producer or
      experiment-local policy.
- [x] Record expected B-path blockers, including
      `native_goal_proxy_regulation_policy_missing` and any refined
      proxy/error/response policy blockers.
- [x] Preserve all A-path and stronger claim boundaries.

Expected artifacts:

- [x] `outputs/n09_iteration_10_hypothesis_b0_native_substrate_inventory.json`
- [x] `reports/n09_iteration_10_hypothesis_b0_native_substrate_inventory.md`

Acceptance statement:

```text
Iteration 10 passes if the closed A-path result is preserved while the B-path
native/substrate inventory maps A-path proxy, error, response, repeated
boundedness, perturbation, memory, and support ingredients to available LGRC
and N05-N08 substrate mechanisms, explicitly recording which pieces are native
representable and which remain blocked by missing native policy surfaces.
```

Acceptance state: Achieved.

Implementation record:

- Command:
  `.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_10_hypothesis_b0_native_substrate_inventory.py`
- Script:
  `scripts/run_n09_iteration_10_hypothesis_b0_native_substrate_inventory.py`
- Output:
  `outputs/n09_iteration_10_hypothesis_b0_native_substrate_inventory.json`
- Report:
  `reports/n09_iteration_10_hypothesis_b0_native_substrate_inventory.md`
- Result:
  - Status: `passed`.
  - Acceptance state: `achieved`.
  - Preserved A-path ceiling:
    `artifact_only_goal_proxy_regulation_candidate`.
  - Preserved GPR level: `GPR6`.
  - Hypothesis B status: `reopened_for_inventory_only`.
  - Native/substrate-mediated goal-proxy regulation support: `false`.
  - Primary B-path blocker:
    `native_goal_proxy_regulation_policy_missing`.
  - Strongest possible Iteration 11 positive ceiling:
    `native_substrate_mediated_goal_proxy_regulation_design_candidate`.

Inventory summary:

- A-path variable rows recorded: `9`.
- Substrate ingredient rows recorded: `5`.
- B-path blocker refinement rows recorded: `22`.
- Variables classified as `producer_policy_required`:
  `target_band`, `error_sign_and_magnitude`, `perturbation_recovery`.
- Variables classified as `partially_native_representable`:
  `proxy_surface`, `response_direction`, `packet_correction_amount`,
  `repeated_boundedness`, `memory_shaped_route_evidence`,
  `support_identity_anchor`.
- N05 ingredient:
  O5 oscillation/return channels are usable as return-channel background, but
  O6 route-coupled oscillator support remains blocked by missing route
  conductance memory and related native policy surfaces.
- N06 ingredient:
  native route arbitration/context selection is usable as route-selection
  background, but not as semantic choice.
- N07 ingredient:
  support/identity evidence is usable as a boundary anchor, but not as runtime
  identity acceptance or RC identity collapse.
- N08 ingredient:
  static positive geometry route-response persistence is usable as a design
  direction, but not as adaptive/native trail memory.
- Current LGRC ingredients:
  packet scheduling, step-owned packet processing, node-plus-packet budget
  accounting, native route arbitration, topology lineage, and topology-state
  reabsorption are available as mechanisms, not as a native goal-proxy
  regulation policy.

Validation:

- `source_artifacts_present = true`
- `source_reports_present = true`
- `all_source_artifacts_passed = true`
- `n09_a_path_closeout_preserved = true`
- `hypothesis_a_closed = true`
- `hypothesis_b_staged = true`
- `native_substrate_b_claim_not_supported = true`
- `required_a_path_variables_inventory_complete = true`
- `n05_n08_ingredient_inventory_complete = true`
- `all_inventory_rows_have_sources = true`
- `primary_b_path_blocker_recorded = true`
- `refined_proxy_policy_blockers_recorded = true`
- `claim_flags_all_false = true`
- `controls_all_passed = true`
- `no_new_probe_run = true`

Controls:

- No-new-probe control passed with blocker
  `new_probe_run_in_inventory_iteration`.
- A-path ceiling preservation control passed with blocker
  `a_path_claim_ceiling_mutated`.
- B-path non-promotion control passed with blocker
  `hypothesis_b_claim_promotion_blocked`.
- Claim-promotion control passed with blocker `claim_promotion_blocked`.
- Non-artifact source-of-truth control passed with blocker
  `non_artifact_source_of_truth_rejected`.

Claim boundary:

- Iteration 10 is inventory-only.
- It does not support native substrate-mediated goal-proxy regulation.
- Semantic goal understanding, agency, identity acceptance, RC identity
  collapse, ACO-like behavior, locomotion-like behavior, biological behavior,
  and unrestricted movement remain blocked.

## Iteration 11. Hypothesis B1 Geometry/Substrate-Mediated Probe

Status: Passed.

- [x] Run one minimal geometry/substrate-mediated probe against the same
      runtime-visible proxy and target band.
- [x] Apply an explicit serialized perturbation to the proxy condition.
- [x] Observe whether fixed geometry, conductance, flux, or existing LGRC
      substrate dynamics move the proxy toward the band without A-path
      producer correction scheduling.
- [x] Serialize the geometry/substrate response mechanism under test.
- [x] Record whether producer correction scheduling was absent.
- [x] Classify the result:
  - [ ] native/substrate return candidate;
  - [ ] bounded degradation;
  - [ ] wrong-direction response;
  - [ ] saturation/no recovery;
  - [x] no response;
  - [x] native policy gap.
- [x] Preserve exact node-plus-packet budget accounting.
- [x] Controls: hidden correction scheduler, hidden reset, producer correction
      leakage, budget drift, posthoc geometry change, native claim promotion.
- [x] Preserve identity/support blockers as handoff material, not claims.

Expected artifacts:

- [x] `outputs/n09_iteration_11_hypothesis_b1_geometry_substrate_probe.json`
- [x] `reports/n09_iteration_11_hypothesis_b1_geometry_substrate_probe.md`

Acceptance statement:

```text
Iteration 11 passes if a serialized geometry/substrate-mediated probe tests
whether the N09 proxy can move toward or remain bounded around the declared
band after perturbation without A-path producer correction scheduling. The
result may be positive or negative, but it must classify the substrate response
with artifact-visible evidence, exact budget accounting, and distinct controls.
```

Acceptance state: Achieved.

Implementation record:

- Command:
  `.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_11_hypothesis_b1_geometry_substrate_probe.py`
- Script:
  `scripts/run_n09_iteration_11_hypothesis_b1_geometry_substrate_probe.py`
- Output:
  `outputs/n09_iteration_11_hypothesis_b1_geometry_substrate_probe.json`
- Report:
  `reports/n09_iteration_11_hypothesis_b1_geometry_substrate_probe.md`
- Result:
  - Status: `passed`.
  - Acceptance state: `achieved`.
  - Claim ceiling:
    `hypothesis_b_no_response_native_policy_gap`.
  - Primary blocker:
    `native_goal_proxy_regulation_policy_missing`.
  - Native/substrate-mediated goal-proxy regulation design candidate support:
    `false`.
  - A-path ceiling preserved:
    `artifact_only_goal_proxy_regulation_candidate`.

Probe record:

- Initial proxy measurement: `0.55`.
- Explicit perturbation amount: `0.09`.
- Post-perturbation proxy measurement: `0.64`.
- Target band: `[0.45, 0.55]`.
- Post-perturbation error: `0.09`.
- Passive fixed-geometry step count: `3`.
- Final passive-probe proxy measurement: `0.64`.
- Final error: `0.09`.
- Error reduction after passive steps: `0.0`.
- Result classification: `no_response_native_policy_gap`.

Mechanism under test:

- Mechanism id:
  `n09_b1_fixed_geometry_passive_response_probe_v1`.
- Mechanism kind:
  `fixed_geometry_empty_queue_passive_lgrc_step_probe`.
- A-path producer correction scheduler used: `false`.
- A-path candidate set consumed: `false`.
- A-path producer record consumed: `false`.
- Native route arbitration used: `false`.
- Topology mutation used: `false`.
- Conductance update used: `false`.
- Custom node potential used: `false`.
- Flux-facilitated metric map used: `false`.
- Geometry digest unchanged before/after passive probe.

Interpretation:

- Current fixed-topology LGRC packet/geometry mechanics preserve the perturbed
  state and budget, but do not create target-band return when the event queue
  is empty and no producer correction packet is scheduled.
- This is a useful negative result for Hypothesis B: pure fixed geometry is
  not enough for N09 regulation under current LGRC. Native/substrate-mediated
  regulation still requires a native goal-proxy response policy surface or
  remains producer-mediated.

Budget:

- Node-plus-packet budget before: `1.5`.
- Node-plus-packet budget after perturbation: `1.5`.
- Node-plus-packet budget after passive probe: `1.5`.
- Node-plus-packet budget error: `0.0`.
- Active node total after passive probe: `1.5`.
- Packet ledger node total after passive probe: `1.5`.
- In-flight packet total after passive probe: `0.0`.
- Active state and packet ledger agree: `true`.

Controls:

- Hidden correction scheduler control passed with blocker
  `hidden_correction_scheduler_blocked`.
- Hidden reset control passed with blocker `hidden_reset_blocked`.
- Producer correction leakage control passed with blocker
  `producer_correction_leakage_blocked`.
- Budget drift control passed with blocker `node_plus_packet_budget_drift`.
- Posthoc geometry change control passed with blocker
  `posthoc_geometry_change_blocked`.
- Native claim promotion control passed with blocker
  `native_claim_promotion_blocked`.

Validation:

- `source_b0_status_passed = true`
- `source_b0_acceptance_achieved = true`
- `a_path_ceiling_preserved = true`
- `explicit_perturbation_serialized = true`
- `perturbation_moved_proxy_out_of_band = true`
- `producer_correction_scheduler_absent = true`
- `a_path_candidate_set_not_consumed = true`
- `passive_steps_ran = true`
- `passive_steps_empty_queue = true`
- `geometry_digest_unchanged = true`
- `budget_exact = true`
- `result_classification_recorded = true`
- `no_native_regulation_claim = true`
- `controls_all_passed = true`
- `claim_flags_all_false = true`

Claim boundary:

- Iteration 11 does not support native substrate-mediated goal-proxy
  regulation.
- It records a B-path native policy gap, not a positive native-regulation
  candidate.
- Semantic goal understanding, agency, identity acceptance, RC identity
  collapse, ACO-like behavior, locomotion-like behavior, biological behavior,
  and unrestricted movement remain blocked.

## Iteration 11-A. Positive Geometry Return-Scaffold Probe

Status: Passed.

- [x] Use Iteration 11 as the inert fixed-geometry baseline.
- [x] Add one predeclared conserved return-channel scaffold before the
      post-perturbation error exists.
- [x] Verify the return scaffold does not consume the A-path producer
      correction scheduler, candidate set, or producer record.
- [x] Apply the same explicit serialized proxy perturbation.
- [x] Process the predeclared return channel through LGRC packet events and
      `step()`.
- [x] Verify the proxy returns to the declared band.
- [x] Preserve exact node-plus-packet budget accounting.
- [x] Controls: post-perturbation error-conditioned schedule, A-path producer
      correction leakage, hidden reset, budget drift, posthoc geometry change,
      native claim promotion, and generalization overclaim.
- [x] Preserve all stronger claim boundaries.

Expected artifacts:

- [x] `outputs/n09_iteration_11a_positive_geometry_return_scaffold_probe.json`
- [x] `reports/n09_iteration_11a_positive_geometry_return_scaffold_probe.md`

Acceptance statement:

```text
Iteration 11-A passes if a predeclared conserved return-channel scaffold
returns the perturbed N09 proxy toward or into the declared band without
reading the post-perturbation error through the A-path producer correction
scheduler. The result may support only a scoped design candidate, with exact
budget accounting and explicit controls against hidden correction, reset,
posthoc geometry changes, and general native-regulation overclaim.
```

Acceptance state: Achieved.

Implementation record:

- Command:
  `.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_11a_positive_geometry_return_scaffold_probe.py`
- Script:
  `scripts/run_n09_iteration_11a_positive_geometry_return_scaffold_probe.py`
- Output:
  `outputs/n09_iteration_11a_positive_geometry_return_scaffold_probe.json`
- Report:
  `reports/n09_iteration_11a_positive_geometry_return_scaffold_probe.md`
- Result:
  - Status: `passed`.
  - Acceptance state: `achieved`.
  - Claim ceiling:
    `native_substrate_mediated_goal_proxy_regulation_design_candidate`.
  - Result classification:
    `predeclared_return_scaffold_band_return_design_candidate`.
  - Primary blocker for general native regulation:
    `native_goal_proxy_response_policy_missing_for_general_regulation`.
  - General native goal-proxy regulation support: `false`.

Probe record:

- Initial proxy measurement: `0.55`.
- Explicit perturbation amount: `0.09`.
- Post-perturbation proxy measurement: `0.64`.
- Target band: `[0.45, 0.55]`.
- Post-perturbation error: `0.09`.
- Return scaffold amount: `0.09`.
- Final proxy measurement: `0.55`.
- Final error: `0.0`.
- Error reduction after return scaffold: `0.09`.
- Final proxy in band: `true`.

Mechanism under test:

- Scaffold id:
  `n09_b1a_predeclared_positive_geometry_return_channel_v1`.
- Scaffold kind:
  `predeclared_conserved_packet_return_channel`.
- Schedule declaration time:
  `before_post_perturbation_proxy_error_exists`.
- A-path producer correction scheduler used: `false`.
- A-path candidate set consumed: `false`.
- Hidden goal/reward label used: `false`.
- Posthoc geometry change used: `false`.
- Native proxy/error/response policy available: `false`.

Event sequence:

- `perturbation_departure`: proxy `0.55 -> 0.55`.
- `perturbation_arrival`: proxy `0.55 -> 0.64`.
- `return_channel_departure`: proxy `0.64 -> 0.55`.
- `return_channel_arrival`: proxy `0.55 -> 0.55`.

Interpretation:

- Iteration 11 showed that empty fixed geometry gives no response.
- Iteration 11-A shows that a predeclared conserved return channel can return
  the proxy to the declared band without reading the post-perturbation error
  and without using the A-path producer correction scheduler.
- This improves Hypothesis B from inert fixed-geometry evidence to a scoped
  return-scaffold design candidate.
- It still does not prove general native goal-proxy regulation: the return
  channel is predeclared and does not compute proxy error, response direction,
  or response magnitude as a native policy.

Budget:

- Node-plus-packet budget before: `1.5`.
- Node-plus-packet budget after perturbation: `1.5`.
- Node-plus-packet budget after return scaffold: `1.5`.
- Node-plus-packet budget error: `0.0`.
- Active node total after return scaffold: `1.5`.
- Packet ledger node total after return scaffold: `1.5`.
- In-flight packet total after return scaffold: `0.0`.
- Active state and packet ledger agree: `true`.

Controls:

- Schedule-declared-before-error control passed with blocker
  `post_perturbation_error_conditioned_schedule_blocked`.
- A-path producer correction leakage control passed with blocker
  `a_path_producer_correction_leakage_blocked`.
- Hidden reset control passed with blocker `hidden_reset_blocked`.
- Budget drift control passed with blocker `node_plus_packet_budget_drift`.
- Posthoc geometry change control passed with blocker
  `posthoc_geometry_change_blocked`.
- Native claim promotion control passed with blocker
  `native_claim_promotion_blocked`.
- Generalization overclaim control passed with blocker
  `general_native_regulation_overclaim_blocked`.

Validation:

- `source_b0_status_passed = true`
- `source_b1_status_passed = true`
- `source_b1_negative_result_consumed = true`
- `a_path_ceiling_preserved = true`
- `explicit_perturbation_serialized = true`
- `return_scaffold_serialized = true`
- `return_scheduled_before_error_evaluation = true`
- `post_perturbation_moved_proxy_out_of_band = true`
- `return_scaffold_moved_proxy_toward_band = true`
- `final_proxy_in_band = true`
- `a_path_producer_correction_absent = true`
- `geometry_digest_unchanged = true`
- `budget_exact = true`
- `result_classification_recorded = true`
- `claim_flags_all_false = true`
- `controls_all_passed = true`

Claim boundary:

- Iteration 11-A supports only a scoped predeclared return-scaffold design
  candidate.
- It does not support general native goal-proxy regulation.
- Semantic goal understanding, agency, identity acceptance, RC identity
  collapse, ACO-like behavior, locomotion-like behavior, biological behavior,
  and unrestricted movement remain blocked.

## Iteration 11-B. Band-Buffered Return-Scaffold Family Probe

Status: Passed.

- [x] Use Arc-of-Becoming method to reinterpret Iterations 11 and 11-A as a
      regime question rather than a single true/false endpoint.
- [x] Keep one fixed predeclared return amount across a perturbation family.
- [x] Verify all return schedules are declared before post-perturbation error
      rows exist.
- [x] Verify no lane consumes the A-path producer correction scheduler,
      candidate set, or producer record.
- [x] Measure band return, bounded partial return, and overclaim boundary.
- [x] Preserve exact node-plus-packet budget accounting in every lane.
- [x] Controls: fixed-return family, post-error schedule, A-path producer
      leakage, hidden reset, budget drift, posthoc geometry change,
      envelope overclaim, and native claim promotion.
- [x] Preserve all stronger claim boundaries.

Expected artifacts:

- [x] `outputs/n09_iteration_11b_band_buffered_return_scaffold_probe.json`
- [x] `reports/n09_iteration_11b_band_buffered_return_scaffold_probe.md`

Acceptance statement:

```text
Iteration 11-B passes if one fixed, predeclared return scaffold is tested
across a perturbation family and produces a source-backed finite response
envelope without adapting to post-perturbation error. The result may support
only a scoped native/substrate-mediated design candidate. It must record the
band-return and partial-return boundary, keep exact budget accounting, reject
hidden A-path correction or posthoc geometry changes, and preserve all stronger
claims as blocked.
```

Acceptance state: Achieved.

Implementation record:

- Command:
  `.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_11b_band_buffered_return_scaffold_probe.py`
- Script:
  `scripts/run_n09_iteration_11b_band_buffered_return_scaffold_probe.py`
- Output:
  `outputs/n09_iteration_11b_band_buffered_return_scaffold_probe.json`
- Report:
  `reports/n09_iteration_11b_band_buffered_return_scaffold_probe.md`
- Result:
  - Status: `passed`.
  - Acceptance state: `achieved`.
  - Claim ceiling:
    `native_substrate_mediated_goal_proxy_regulation_design_candidate`.
  - Result classification:
    `finite_envelope_band_buffered_return_scaffold_candidate`.
  - Primary blocker:
    `native_response_magnitude_policy_missing_for_unbounded_perturbations`.
  - General native goal-proxy regulation support: `false`.

Arc-of-Becoming record:

- Question:
  What kind of regulation-like becoming does the predeclared return scaffold
  express when perturbation amplitude varies?
- Redirection:
  Iteration 11-B should not chase one perfect endpoint. It should ask whether
  geometry supports a finite response envelope and where that envelope begins
  to degrade.
- Observation:
  the same return geometry gives band return for smaller/matched
  perturbations and bounded partial return for a larger perturbation.
- Cultivation next:
  a wider envelope would require either multi-stage predeclared geometry or a
  native response-magnitude policy.

Probe record:

| Lane | Perturbation | Fixed return | Post proxy | Final proxy | Final error | In band | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| `perturbation_0_07` | `0.07` | `0.09` | `0.62` | `0.53` | `0.0` | `true` | `band_return_with_fixed_return_amount` |
| `perturbation_0_09` | `0.09` | `0.09` | `0.64` | `0.55` | `0.0` | `true` | `band_return_with_fixed_return_amount` |
| `perturbation_0_11` | `0.11` | `0.09` | `0.66` | `0.57` | `0.02` | `false` | `bounded_partial_return_with_fixed_return_amount` |

Interpretation:

- Geometry improved the Hypothesis B result: the return scaffold is no longer
  merely a one-off matched cancellation.
- The evidence now supports a finite, band-buffered response envelope.
- The larger perturbation is improved but remains outside band, which makes
  the boundary explicit: conserved packet handling works, but native response
  magnitude selection is still missing for broader regulation.
- This remains a scaffolded substrate design candidate, not general native
  goal-proxy regulation.

Controls:

- Fixed-return family control passed with blocker
  `adaptive_response_amount_hidden_policy_blocked`.
- Schedule-declared-before-error control passed with blocker
  `post_perturbation_error_conditioned_schedule_blocked`.
- A-path producer correction leakage control passed with blocker
  `a_path_producer_correction_leakage_blocked`.
- Hidden reset control passed with blocker `hidden_reset_blocked`.
- Budget drift control passed with blocker `node_plus_packet_budget_drift`.
- Posthoc geometry change control passed with blocker
  `posthoc_geometry_change_blocked`.
- Envelope overclaim control passed with blocker
  `general_native_regulation_overclaim_blocked`.
- Native claim promotion control passed with blocker
  `native_claim_promotion_blocked`.

Validation:

- `source_b0_status_passed = true`
- `source_b1_status_passed = true`
- `source_b1a_status_passed = true`
- `source_b1_negative_result_consumed = true`
- `source_b1a_design_candidate_consumed = true`
- `a_path_ceiling_preserved = true`
- `perturbation_family_serialized = true`
- `fixed_return_amount_across_family = true`
- `all_lanes_moved_out_of_band_after_perturbation = true`
- `all_lanes_improved_after_return = true`
- `at_least_two_lanes_returned_to_band = true`
- `larger_perturbation_recorded_as_partial_not_failure = true`
- `arc_of_becoming_interpretation_recorded = true`
- `a_path_producer_correction_absent = true`
- `budget_exact = true`
- `result_classification_recorded = true`
- `no_general_native_regulation_claim = true`
- `claim_flags_all_false = true`
- `controls_all_passed = true`

Claim boundary:

- Iteration 11-B supports only a finite-envelope, predeclared return-scaffold
  design candidate.
- It does not support general native goal-proxy regulation.
- Semantic goal understanding, agency, identity acceptance, RC identity
  collapse, ACO-like behavior, locomotion-like behavior, biological behavior,
  and unrestricted movement remain blocked.

## Iteration 12. Hypothesis B2 Native/Substrate Closeout

Status: Passed.

- [x] Replay Iteration 10 inventory, Iteration 11 probe, Iteration 11-A
      refinement, and Iteration 11-B family artifacts without private runtime
      state.
- [x] Freeze the B-path ceiling:
  - [x] scoped `native_substrate_mediated_goal_proxy_regulation_design_candidate`
        if supported;
  - [x] explicit native-policy blockers for general native regulation.
- [x] Record refined missing policy surfaces, if any:
  - [x] native proxy-surface policy;
  - [x] native proxy-error policy;
  - [x] native proxy-conditioned response policy;
  - [x] native response-magnitude policy;
  - [x] native geometry/conductance memory policy;
  - [x] native artifact replay validator.
- [x] Confirm Hypothesis A remains closed and is not promoted into B.
- [x] Emit N10/Phase-8 handoff fields for any native/substrate blocker.
- [x] Record optional 11-C geometry-envelope cultivation as deferred and not
      blocking N09 closeout.
- [x] Preserve all stronger claims as blocked:
      intention, agency, identity acceptance, ACO, locomotion, biological,
      personhood, and unrestricted claims.

Expected artifacts:

- [x] `outputs/n09_iteration_12_hypothesis_b2_native_substrate_closeout.json`
- [x] `reports/n09_iteration_12_hypothesis_b2_native_substrate_closeout.md`

Acceptance statement:

```text
Iteration 12 passes if the B-path inventory and probe are replayed from
artifacts, freezing either a scoped native/substrate-mediated regulation design
candidate or explicit blockers. The closeout must keep Hypothesis A closed,
avoid promoting producer scaffolds into native support, and emit clear N10 or
Phase-8 handoff records for any missing native policy surface.
```

Acceptance state: Achieved.

Implementation record:

- Command:
  `.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_12_hypothesis_b2_native_substrate_closeout.py`
- Script:
  `scripts/run_n09_iteration_12_hypothesis_b2_native_substrate_closeout.py`
- Output:
  `outputs/n09_iteration_12_hypothesis_b2_native_substrate_closeout.json`
- Report:
  `reports/n09_iteration_12_hypothesis_b2_native_substrate_closeout.md`
- Result:
  - Status: `passed`.
  - Acceptance state: `achieved`.
  - A-path ceiling:
    `artifact_only_goal_proxy_regulation_candidate`.
  - B-path ceiling:
    `native_substrate_mediated_goal_proxy_regulation_design_candidate`.
  - B-path strongest evidence:
    `finite_envelope_band_buffered_return_scaffold_candidate`.
  - General native goal-proxy regulation support: `false`.
  - Primary blocker:
    `native_response_magnitude_policy_missing_for_unbounded_perturbations`.

B-path closeout interpretation:

- Iteration 11 showed that fixed geometry alone does not regulate the proxy.
- Iteration 11-A showed that one predeclared return scaffold can return one
  matched perturbation to the band.
- Iteration 11-B showed that geometry improves the result into a finite
  envelope: two perturbations returned to band and a larger perturbation
  improved but remained outside band.
- The closeout boundary is response-magnitude selection, not packet
  conservation or step-owned processing.

Deferred 11-C record:

- Candidate: `11-C`.
- Status: `deferred_optional_not_n09_blocker`.
- Topic: `geometry_envelope_cultivation`.
- Question:
  Can multi-stage predeclared geometry widen the finite response envelope
  without reading post-perturbation error?
- Would test:
  multiple fixed return channels, delayed staged returns, wider perturbation
  families, and whether bounded partial return can become wider band return.
- Why deferred:
  Iteration 11-B already established the N09-B evidence needed for closeout:
  geometry can improve regulation-like behavior inside a finite envelope, and
  the remaining blocker is native response-magnitude selection.

Validation:

- `artifact_only_replay_used = true`
- `runtime_state_not_used = true`
- `all_source_artifacts_passed = true`
- `all_source_acceptance_achieved = true`
- `all_artifact_digests_recompute = true`
- `b_path_replay_chain_reconstructed = true`
- `hypothesis_a_ceiling_preserved = true`
- `b1_no_response_boundary_preserved = true`
- `b1a_scaffold_design_candidate_preserved = true`
- `b1b_finite_envelope_preserved = true`
- `b_path_ceiling_frozen = true`
- `general_native_regulation_blocked = true`
- `missing_policy_surfaces_recorded = true`
- `future_11c_deferred_not_blocking = true`
- `claim_flags_all_false = true`
- `controls_all_passed = true`

Controls:

- Artifact runtime fallback control passed with blocker
  `runtime_state_fallback_blocked`.
- Hypothesis A promotion-to-B control passed with blocker
  `hypothesis_a_to_b_promotion_blocked`.
- General native regulation overclaim control passed with blocker
  `general_native_regulation_overclaim_blocked`.
- Missing policy surfaces control passed with blocker
  `missing_policy_surface_record_absent`.
- Future 11-C not-blocking control passed with blocker
  `optional_cultivation_misclassified_as_closeout_blocker`.
- Claim promotion control passed with blocker `claim_promotion_blocked`.

Claim boundary:

- N09 closes with Hypothesis A as an artifact-only goal-proxy regulation
  candidate and Hypothesis B as a scoped substrate-mediated design candidate.
- N09 does not support general native goal-proxy regulation, semantic goal
  understanding, agency, identity acceptance, RC identity collapse, ACO-like
  behavior, locomotion-like behavior, biological behavior, or unrestricted
  claims.
