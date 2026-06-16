# N15 Endogenous Proxy Formation Implementation Checklist

## Global Rules

- [ ] Preserve the N15 claim boundary.
- [ ] Do not edit `src/*`.
- [ ] Use `.venv/bin/python` for local script/test runs.
- [ ] Use source-backed artifacts and SHA-256 digests.
- [ ] Do not promote N12 NAT4 readiness records into native support.
- [ ] Do not promote N13 AP3 support-seeking regulation into selfhood,
      identity acceptance, intention, agency, or goal ownership.
- [ ] Do not promote N14 AP4 consequence-sensitive route selection into
      intention, semantic choice, agency, or goal ownership.
- [ ] Keep N14 constructed support/regulation followout distinct from upstream
      observed route-conditioned support/regulation evidence.
- [ ] Use direct historic evidence when it exists and is source-backed,
      claim-clean, and control-clean.
- [ ] Prefer construction from old best closed claims as the strongest N15 proof
      path.
- [ ] Preserve every source experiment's original claim ceiling during
      old-best-claims construction.
- [ ] Apply the Arc of Becoming method sources by title/filename only; do not
      record absolute paths.
- [ ] Use Classification of Becoming to separate local observation tags,
      reusable/generative classes, AP5 candidates, and blocked relabels.
- [ ] Use Interrogation of Becoming to treat controls and variants as bounded
      questions rather than proof.
- [ ] Use Naturalization of Becoming to keep constructed/support-dependent
      evidence separate from native regime expression.
- [ ] Use Cultivation of Becoming to cultivate the missing function rather than
      optimize a local proxy.
- [ ] Keep `phase8_opened = false` unless a separate Phase 8 task is explicitly
      opened.
- [ ] Before closing any turn that edits files, run `git diff --check`.
- [ ] Before closing any turn that edits files, run `git diff -- src`.

## Setup

- [x] Create N15 experiment root.
- [x] Create `README.md`.
- [x] Create `configs/`, `hypotheses/`, `implementation/`, `outputs/`,
      `reports/`, and `scripts/` directories.
- [x] Create N15-specific hypotheses.
- [x] Create implementation plan.
- [x] Create implementation checklist.

## Hypotheses

- [ ] Hypothesis A: runtime-state proxy sources.
- [ ] Hypothesis B: bounded endogenous proxy formation.
- [ ] Hypothesis C: goal ownership and agency boundary.

## Iteration 1. Baseline And Proxy Source Inventory

- [x] Pin N08 route memory / affordance source artifacts.
- [x] Pin N09 bounded response regulation source artifacts.
- [x] Pin N12 NAT4 readiness source artifacts.
- [x] Pin N13 AP3 support-seeking regulation source artifacts.
- [x] Pin N14 AP4 consequence-sensitive route selection source artifacts.
- [x] Record whether direct historic AP5 support exists.
- [x] Record old-best-claims construction inputs.
- [x] Record Arc of Becoming method mapping for source classification.
- [x] Classify source rows by support, memory, regulation, support/identity
      condition, constructed followout, readiness, or boundary role.
- [x] Reject any source row that would exceed its closed claim ceiling.
- [x] Record provisional AP levels only.
- [x] Confirm no final AP5 claim is made.

Expected artifacts:

- [x] `outputs/n15_proxy_source_inventory.json`
- [x] `reports/n15_proxy_source_inventory.md`
- [x] `scripts/build_n15_proxy_source_inventory.py`

Output digest:

```text
66ebd8bf90e31d3aa1a59d9de46e85bf581f44c3c70e5cf1a3a76d8f535aa4c1
```

Artifact SHA-256:

```text
outputs/n15_proxy_source_inventory.json 67fe966ec46525059eef61d0e38cad73e4e561c1d258a86802f6b82012f9dada
reports/n15_proxy_source_inventory.md 12797a85760e37372413ec0dc5b8542cfbe5038faf8970b54430f644fa0955b5
scripts/build_n15_proxy_source_inventory.py 70576c79f9b35039edf4ab3d3e707ebdc03a8d84acb71b33eb9c424f8e4f7147
```

Acceptance state:

```text
accepted_proxy_source_inventory_only_no_ap5
```

Interpretation:

```text
Iteration 1 pins nine source rows and records the evidence split: direct
historic support exists only as an N13 AP2 support-derived target candidate,
while the strongest N15 path remains old-best-claims construction. No final
AP5, semantic goal ownership, native support, Phase 8, or fully native
integration claim is opened.
```

## Iteration 2. Proxy Formation Schema And AP5 Gate

- [x] Freeze runtime-visible source state fields.
- [x] Freeze freshness and source-window fields.
- [x] Freeze support, memory, regulation, and support/identity-condition
      descriptor fields.
- [x] Freeze declared external proxy absence fields.
- [x] Freeze external target injection rejection policy.
- [x] Freeze hidden target derivation rejection policy.
- [x] Freeze endogenous derivation policy fields.
- [x] Freeze old-best-claims composition fields.
- [x] Freeze direct historic support fields.
- [x] Freeze target condition, target band, and target tolerance fields.
- [x] Freeze target center derivation fields.
- [x] Freeze bounded drift and clamp fields.
- [x] Freeze concrete drift bounds or ordinal step limits.
- [x] Freeze budget validity fields.
- [x] Freeze budget units and validity limits.
- [x] Freeze dependency trace fields.
- [x] Freeze dependency trace completeness criteria.
- [x] Freeze replay digest scope and algorithm.
- [x] Freeze top-level JSON output shape.
- [x] Freeze schema validation mechanism or validator requirements.
- [x] Freeze fail-closed error labels.
- [x] Materialize `configs/n15_source_registry.json`.
- [x] Materialize `configs/n15_derivation_policy_v1.json`.
- [x] Materialize `configs/n15_budget_limits_v1.json`.
- [x] Materialize `configs/n15_control_variants_v1.json`.
- [x] Materialize `configs/n15_replay_policy_v1.json`.
- [x] Freeze artifact-only replay, snapshot/load, and order-inversion
      requirements.
- [x] Freeze AP5 gates.
- [x] Freeze negative controls.
- [x] Freeze claim flags forced false.
- [x] State that final AP5 requires later controls and closeout.
- [x] Add local row/schema validator.

Expected artifacts:

- [x] `outputs/n15_proxy_formation_schema_v1.json`
- [x] `reports/n15_proxy_formation_schema_v1.md`
- [x] `scripts/build_n15_proxy_formation_schema_v1.py`
- [x] `scripts/validate_n15_row.py`
- [x] `configs/n15_source_registry.json`
- [x] `configs/n15_derivation_policy_v1.json`
- [x] `configs/n15_budget_limits_v1.json`
- [x] `configs/n15_control_variants_v1.json`
- [x] `configs/n15_replay_policy_v1.json`

Output digest:

```text
3894554145fe84a7f594983ead562442cda686fd53d6b240164626b578f2ee67
```

Artifact SHA-256:

```text
outputs/n15_proxy_formation_schema_v1.json aa276922df3c39c30bcf09500b7eccfe96468fd681f3992a328a504f0d8c9d5b
reports/n15_proxy_formation_schema_v1.md 040582e46c1542a30c28aa4cda661fc5752e2529d93a0c14fc2f2c3b5e26eba6
scripts/build_n15_proxy_formation_schema_v1.py 200dad631cb719a91b4e846b6ce9c65bb07f5ede27b4c908aad80fe612a852ff
scripts/validate_n15_row.py 41294a0624d4fc113f1bb1ddb2fa9b4b80fcb249a77031e23be9e905f395613c
configs/n15_source_registry.json 361457bb559a4e4255824ee72415ae9c77b661e1ec95f657ea3d65bff4a36e71
configs/n15_derivation_policy_v1.json 9de32ee9717fd813e2a20ded18cde3cc384307c92586212a07f7105d72041c7b
configs/n15_budget_limits_v1.json 8b1314a9d229d70cd48e12bfc5fa4aa978877f78a4880db9e8a3faa867fbe62e
configs/n15_control_variants_v1.json bf4a17c7168c74a21e85c6893ce174b4d76fb159340710e261c16b5ef45984e9
configs/n15_replay_policy_v1.json 356589601130ec5a9edacf3c900b57758768cc6fa73b9e1e09880a2fbab7c7f3
```

Acceptance state:

```text
accepted_schema_freeze_no_row_validation
```

Interpretation:

```text
Iteration 2 freezes the N15 AP5 validation contract, including row schema,
derivation policy, old-best-claims composition, drift, budget, dependency
trace, replay digest, perturbation defaults, controls, materialized config
contracts, split runtime/schema-freeze output contracts, local validator, and
fail-closed labels. It does not generate a target, run candidate row
validation, open Phase 8, open native support, or assign final AP5.
```

Post-review gap closure:

```text
closed: split runtime top-level output fields from Iteration 2 schema-freeze
        metadata fields.
closed: aligned AP5 gate records to canonical machine gate IDs.
closed: materialized five config JSON files from the frozen Iteration 2
        constants.
closed: added scripts/validate_n15_row.py and linked it from
        schema_validation_contract.
not_gap: fixed generated_at remains intentional because N12-N14 deterministic
         artifacts use fixed timestamps and output_digest excludes generated_at.
not_gap: row_validation_started = false is explicit negative scope for
         accepted_schema_freeze_no_row_validation, not redundant evidence.
not_gap: Iteration 6 perturbation defaults and Iteration 7 hypothesis rubric
         are forward contracts frozen early; they do not imply I6/I7 execution.
```

## Iteration 3. Runtime-Derived Target Candidate

- [x] Select source-current state inputs.
- [x] Prefer old-best-claims construction unless direct historic support is
      stronger and claim-clean.
- [x] Derive target band or threshold using the frozen policy.
- [x] Record target formation timing before downstream use.
- [x] Record dependency trace for every target field.
- [x] Record budget validity before target use.
- [x] Record source digests and replay digest inputs.
- [x] Record target consumability by rank or regulation behavior without
      semantic goal ownership relabel.
- [x] Confirm no externally declared target is used.
- [x] Keep AP level provisional.
- [x] Record the direct historic AP2 target-evidence gap.
- [x] Run local row/schema validator.

Expected artifacts:

- [x] `outputs/n15_runtime_derived_target_candidate.json`
- [x] `reports/n15_runtime_derived_target_candidate.md`
- [x] `scripts/build_n15_runtime_derived_target_candidate.py`

Output digest:

```text
7fcb73f4b70fdd4f4aadaa9e931040f8299669ca1598c9a1391c560637a26fbc
```

Artifact SHA-256:

```text
outputs/n15_runtime_derived_target_candidate.json 30c834b47a7decf2bb32f3dabb8dcb436b2b7876be5b0e9c79fe76b7de010873
reports/n15_runtime_derived_target_candidate.md c54c784652e004a23f1283d8e716f370993636b72e4d9ade46f2d9d7c071277c
scripts/build_n15_runtime_derived_target_candidate.py 4c6aae71ffaa390ff7ca96e5d90ecfe09ad33e83559bfd0762ec01ceaeae18be
```

Acceptance state:

```text
accepted_runtime_derived_target_candidate_with_bridge_pending_controls
```

Interpretation:

```text
Iteration 3 generates a provisional runtime-derived target candidate and
bridges the gap between target existence and target-as-input. Direct historic
support remains AP2 context only. The constructed target comes from N13 AP3 +
N14 AP4 + N08/N09/N12 context, and the bridge probe shows the generated target
band is consumed before ranking a bounded regulation response. Final AP5,
external proxy contrast, adversarial controls, bounded drift replay, and
claim-boundary classification remain pending.
```

Explanation section:

```text
reports/n15_runtime_derived_target_candidate.md records the full Iteration 3
Explanation section for the composition, inputs, bridge result, and claim
boundary.
```

Post-review gap closure:

```text
closed: iteration_3_top_level_output_fields declares every I3 top-level key.
closed: idempotency_digest_plan scope matches replay_digest_inputs including
        claim_flags.
closed: n14_constructed_followout is included in candidate_path_used.
closed: dependency_trace covers direct AP2 gap context, N12 readiness,
        N13 AP3 closeout, N14 constructed followout, and bounded bridge
        response fields.
closed: I2 validator required check names are emitted in I3 checks.
closed: control value convention and replay digest design note are recorded.
not_gap: full runtime_state_vector and target_condition objects in
         replay_digest_inputs are intentional; Iteration 6 must rederive
         and compare the full objects.
```

## Iteration 4. External Proxy Contrast Matrix

- [x] Build declared target fixture contrast.
- [x] Block externally injected target variants.
- [x] Block hidden target derivation variants.
- [x] Block post-hoc proxy formation variants.
- [x] Confirm source-current runtime derivation replays.
- [x] Confirm budget validity is checked before target use.
- [x] Record whether the candidate is distinguishable from declared proxy
      regulation.

Expected artifacts:

- [x] `outputs/n15_external_proxy_contrast_matrix.json`
- [x] `reports/n15_external_proxy_contrast_matrix.md`
- [x] `scripts/build_n15_external_proxy_contrast_matrix.py`

Output digest:

```text
bc97c3125ffdc83c0e97a02c7a6534fadfb95e0141f7082af3d1439c974fea59
```

Artifact SHA-256:

```text
outputs/n15_external_proxy_contrast_matrix.json f7201b82f0071e26f05b62111d88396072d669d815153971f93f967e503c0ee8
reports/n15_external_proxy_contrast_matrix.md 3c679397b75bd033df352995265c8cceee71612944729a6991805801509aad8c
scripts/build_n15_external_proxy_contrast_matrix.py 9fc6119581bb5f7ffee968389dbc96ce42940d90169ec3ca84d6fe0c096f97d7
```

Acceptance state:

```text
accepted_external_proxy_contrast_matrix_pending_adversarial_controls_replay_and_claim_boundary
```

Interpretation:

```text
Iteration 4 accepts the external proxy contrast matrix. The I3 candidate is
distinguishable from a declared target fixture, externally injected target,
hidden target derivation, and post-hoc proxy formation. The source-current
target derivation replays from the serialized I3 runtime state vector, and
budget validity is checked before target use. Final AP5, full adversarial
controls, bounded drift replay, and claim-boundary classification remain
pending.
```

Explanation section:

```text
reports/n15_external_proxy_contrast_matrix.md records the full Iteration 4
Explanation section for the contrast inputs, contrast rule, same-band fixture
result, end result, and claim boundary.
```

Scope boundary:

```text
I4 contrast clean != final AP5.
I4 budget-before-use check != full I5 budget ambiguity control.
I4 source-current replay != full I6 artifact-only/snapshot/order replay.
```

## Iteration 5. Adversarial Control Matrix

- [ ] Externally injected target control fails closed.
- [ ] Hidden target derivation control fails closed.
- [ ] Semantic goal ownership relabel control fails closed.
- [ ] Post-hoc proxy formation control fails closed.
- [ ] Unbounded target drift control fails closed.
- [ ] Budget-surface ambiguity control fails closed.
- [ ] Identity acceptance relabel control fails closed.
- [ ] Native support relabel control fails closed.
- [ ] Fixture-label proxy control fails closed.
- [ ] Stale source state control fails closed.
- [ ] Missing source state control fails closed.
- [ ] Dependency trace omission control fails closed.
- [ ] Record distinct blockers for negative controls.

Expected artifacts:

- [ ] `outputs/n15_proxy_control_matrix.json`
- [ ] `reports/n15_proxy_control_matrix.md`
- [ ] `scripts/build_n15_proxy_control_matrix.py`

## Iteration 6. Bounded Drift And Replay Matrix

- [ ] Run support-state perturbation.
- [ ] Run memory-state perturbation.
- [ ] Run regulation-state perturbation.
- [ ] Run stale-state perturbation.
- [ ] Run budget-invalid perturbation.
- [ ] Run unbounded-drift null.
- [ ] Run duplicate replay.
- [ ] Run artifact-only filesystem replay.
- [ ] Run snapshot/load replay.
- [ ] Run order-inversion replay.
- [ ] Use frozen perturbation magnitudes or recorded replacement magnitudes.
- [ ] Confirm target changes only when serialized source-current state changes
      within bounded drift policy.

Expected artifacts:

- [ ] `outputs/n15_bounded_drift_replay_matrix.json`
- [ ] `reports/n15_bounded_drift_replay_matrix.md`
- [ ] `scripts/build_n15_bounded_drift_replay_matrix.py`

## Iteration 7. Claim Boundary And AP5 Classification

- [ ] Resolve every AP5 gate as validated or blocked.
- [ ] Classify Hypothesis A.
- [ ] Classify Hypothesis B.
- [ ] Classify Hypothesis C.
- [ ] Apply supported/deferred/rejected/partial decision rubric.
- [ ] Force unsafe claim flags false.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `fully_native_integration_opened = false`.
- [ ] Audit blocked inputs.
- [ ] Audit N14 constructed followout caveat.
- [ ] Draft whole-experiment interpretation.

Expected artifacts:

- [ ] `outputs/n15_claim_boundary_record.json`
- [ ] `reports/n15_claim_boundary_record.md`
- [ ] `scripts/build_n15_claim_boundary_record.py`

## Iteration 8. N15 Closeout And N16 Handoff

- [ ] Freeze final supported AP level.
- [ ] Record final claim ceiling.
- [ ] Record final controls.
- [ ] Record final blockers.
- [ ] Record final N16 handoff.
- [ ] Record whether targeted Phase 8 is optional, required, or deferred.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `fully_native_integration_opened = false`.
- [ ] Confirm all source rows receive specific final roles.

Expected artifacts:

- [ ] `outputs/n15_closeout_and_handoff.json`
- [ ] `reports/n15_closeout_and_handoff.md`
- [ ] `scripts/build_n15_closeout_and_handoff.py`

## Setup Verification

- [x] `git diff --check`
- [x] `git diff -- src`
