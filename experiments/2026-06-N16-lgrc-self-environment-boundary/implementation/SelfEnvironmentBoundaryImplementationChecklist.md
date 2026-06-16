# N16 Self / Environment Boundary Implementation Checklist

## Global Rules

- [ ] Preserve the N16 claim boundary.
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
- [ ] Do not promote N15 AP5 endogenous proxy formation into semantic goal
      ownership, identity acceptance, agency, or native support.
- [ ] Use direct historic evidence when it exists and is source-backed,
      claim-clean, and control-clean.
- [ ] Prefer construction from old best closed claims as the strongest N16 proof
      path unless direct AP6 evidence is stronger and claim-clean.
- [ ] Treat N16 as stable basin-boundary requirements discovery across
      lineage-derived boundary-state and operational challenge-class
      interaction cells, not as a complete boundary taxonomy.
- [ ] Keep boundary-state sweeps, challenge-class sweeps, and selected
      interaction probes on one common report schema.
- [ ] Derive B0-B4 from prior N** source records; do not treat them as
      freestanding invented boundary classes.
- [ ] Treat C0-C5 as operational challenge classes, not inherited environment
      taxonomy.
- [ ] Treat Iterations 1-2 as mandatory contract-freezing work before any AP6
      interpretation.
- [ ] Treat Iteration 4 as the first core scientific result and first
      closeable MVP result.
- [ ] Treat Iterations 5-6 as requirement-depth extensions unless explicitly
      needed for the current tranche.
- [ ] Postpone selective uptake, resource assimilation, porous boundary
      function, agency-like boundary behavior, semantic recognition, organism
      claims, and life claims.
- [ ] Preserve every source experiment's original claim ceiling during
      old-best-claims construction.
- [ ] Apply the Arc of Becoming method sources by title/filename only; do not
      record absolute paths.
- [ ] Use Classification of Becoming to separate internal-state rows,
      external-state rows, boundary-crossing traces, AP6 candidates, and
      blocked relabels.
- [ ] Use Interrogation of Becoming to treat controls and variants as bounded
      questions rather than proof of selfhood.
- [ ] Use Naturalization of Becoming to keep artifact-level separability
      separate from native regime expression.
- [ ] Use Cultivation of Becoming to cultivate reusable boundary traces and
      fail-closed controls rather than optimize a local boundary label.
- [ ] Keep `phase8_opened = false` unless a separate Phase 8 task is explicitly
      opened.
- [ ] Before closing any turn that edits files, run `git diff --check`.
- [ ] Before closing any turn that edits files, run `git diff -- src`.

## Setup

- [x] Create N16 experiment root.
- [x] Create `README.md`.
- [x] Create `configs/`, `hypotheses/`, `implementation/`, `outputs/`,
      `reports/`, and `scripts/` directories.
- [x] Create N16-specific hypotheses.
- [x] Create implementation plan.
- [x] Create implementation checklist.

## Hypotheses

- [ ] Hypothesis A: boundary source inventory.
- [ ] Hypothesis B: artifact boundary separation.
- [ ] Hypothesis C: selfhood, identity, and agency boundary.

## Iteration 1. Baseline And Boundary Source Inventory

- [ ] Pin N15 AP5 endogenous proxy formation source artifacts.
- [ ] Pin N14 AP4 consequence-sensitive route selection source artifacts.
- [ ] Pin N13 AP3 support-seeking regulation source artifacts.
- [ ] Pin N12 NAT4 readiness source artifacts.
- [ ] Pin N03 polarized basin loop and boundary/coupling source artifacts.
- [ ] Pin N04 movement, substrate, persistence, and identity-continuity source
      artifacts.
- [ ] Pin N07 identity/support persistence and withdrawal/restoration source
      artifacts.
- [ ] Pin N08 route memory / affordance source artifacts.
- [ ] Pin N09 bounded response regulation source artifacts.
- [ ] Record whether direct historic AP6 support exists.
- [ ] Record old-best-claims construction inputs.
- [ ] Record B0-B4 lineage sources, inherited closed claims, constructed
      support, unsupported extensions, required N16 evidence, and claim
      ceilings.
- [ ] Record C0-C5 challenge classes as N16 operational test conditions, not
      inherited environment classes.
- [ ] Record that C3 structured external coherence is external structured
      state by default, not perturbation unless crossing/disruption is
      explicitly recorded.
- [ ] Record Arc of Becoming method mapping for source classification.
- [ ] Classify source rows by internal support state, external resource state,
      external perturbation state, external structured state,
      boundary-crossing trace, readiness, or boundary role.
- [ ] Reject any source row that would exceed its closed claim ceiling.
- [ ] Record provisional AP levels only.
- [ ] Confirm no final AP6 claim is made.

Expected artifacts:

- [ ] `outputs/n16_boundary_source_inventory.json`
- [ ] `reports/n16_boundary_source_inventory.md`
- [ ] `scripts/build_n16_boundary_source_inventory.py`

## Iteration 2. Boundary Schema And AP6 Gate

- [ ] Freeze internal support-relevant state fields.
- [ ] Freeze external resource state fields.
- [ ] Freeze external perturbation state fields.
- [ ] Freeze external structured state fields.
- [ ] Freeze `external_state_role`.
- [ ] Freeze `external_state_role` values:
      `background`, `resource`, `perturbation`,
      `structured_external_state`, `shared_medium`, `coupling_channel`,
      `mixed`, and `not_applicable`.
- [ ] Freeze boundary-side assignment fields.
- [ ] Freeze boundary-crossing trace fields.
- [ ] Freeze freshness and source-window fields.
- [ ] Freeze boundary policy fields.
- [ ] Freeze budget validity fields.
- [ ] Freeze dependency trace fields.
- [ ] Freeze replay digest scope and algorithm.
- [ ] Freeze top-level JSON output shape.
- [ ] Freeze schema validation mechanism or validator requirements.
- [ ] Freeze fail-closed error labels.
- [ ] Materialize `configs/n16_source_registry.json`.
- [ ] Materialize `configs/n16_boundary_policy_v1.json`.
- [ ] Materialize `configs/n16_budget_limits_v1.json`.
- [ ] Materialize `configs/n16_control_variants_v1.json`.
- [ ] Materialize `configs/n16_replay_policy_v1.json`.
- [ ] Freeze artifact-only replay, snapshot/load, and order-inversion
      requirements.
- [ ] Freeze AP6 gates.
- [ ] Freeze negative controls.
- [ ] Freeze lineage-derived boundary-state axis values B0-B4.
- [ ] Freeze operational challenge-class axis values C0-C5.
- [ ] Freeze selected interaction cells.
- [ ] Freeze common matrix-cell report fields.
- [ ] Freeze `row_decision` values:
      `supported`, `blocked`, `partial`, `rejected`, and `not_applicable`.
- [ ] Freeze `row_decision` and `boundary_claim_allowed` rules:
      `supported` does not automatically imply allowed, `partial` keeps final
      AP6 provisional, and `blocked` / `rejected` / `not_applicable` force
      `boundary_claim_allowed = false`.
- [ ] Freeze synthesis mode fields:
      `synthesis_mode`, `included_iterations`, `deferred_iterations`, and
      `final_ap6_closeout_allowed`.
- [ ] Freeze native boundary requirement synthesis fields.
- [ ] Freeze claim flags forced false.
- [ ] State that final AP6 requires later controls and closeout.
- [ ] Add local row/schema validator.

Expected artifacts:

- [ ] `outputs/n16_boundary_schema_v1.json`
- [ ] `reports/n16_boundary_schema_v1.md`
- [ ] `scripts/build_n16_boundary_schema_v1.py`
- [ ] `scripts/validate_n16_row.py`
- [ ] `configs/n16_source_registry.json`
- [ ] `configs/n16_boundary_policy_v1.json`
- [ ] `configs/n16_budget_limits_v1.json`
- [ ] `configs/n16_control_variants_v1.json`
- [ ] `configs/n16_replay_policy_v1.json`

## Iteration 3. Quiet Boundary Calibration

- [ ] Run B0 null / external coherence only under C0 quiet reference.
- [ ] Run B1 localized basin partition under C0 quiet reference.
- [ ] Run B2 support-persistent basin under C0 quiet reference.
- [ ] Confirm boundary edge extraction for B1/B2.
- [ ] Confirm inside/outside partition for B1/B2.
- [ ] Measure minimum basin coherence/support needed for detectable
      persistence.
- [ ] Populate the common matrix-cell report schema.
- [ ] Confirm no externally supplied boundary label is used.
- [ ] Keep AP level provisional.

Expected artifacts:

- [ ] `outputs/n16_quiet_boundary_calibration.json`
- [ ] `reports/n16_quiet_boundary_calibration.md`
- [ ] `scripts/build_n16_quiet_boundary_calibration.py`

## Iteration 4. Challenge-Class Sweep

- [ ] Treat Iteration 4 as the N16-MVP core result.
- [ ] Run B2 x C0 quiet reference.
- [ ] Run B2 x C1 unstructured perturbation.
- [ ] Run B2 x C2 directional flux.
- [ ] Run B2 x C3 structured external coherence.
- [ ] Run B2 x C4 breach and repair.
- [ ] Run B2 x C5 coupled neighbor / shared medium.
- [ ] Measure noise tolerance.
- [ ] Measure flux tolerance.
- [ ] Measure structured-external-coherence rejection pressure.
- [ ] Measure breach/reclosure pressure.
- [ ] Measure shared-medium leakage pressure.
- [ ] Emit MVP requirement summary even if Iterations 5-6 are deferred.
- [ ] Populate the common matrix-cell report schema.

Expected artifacts:

- [ ] `outputs/n16_challenge_sweep_matrix.json`
- [ ] `reports/n16_challenge_sweep_matrix.md`
- [ ] `scripts/build_n16_challenge_sweep_matrix.py`

## Iteration 5. Boundary-State Sweep

- [ ] Confirm B2 has already been evaluated under C0, C1, and C2, or record
      explicit blockers before unlocking B3 repair/reabsorption rows.
- [ ] Run B0 x C2 null under flux.
- [ ] Run B1 x C2 localized weak boundary under flux.
- [ ] Run B2 x C2 persistent boundary under flux.
- [ ] Run B3 x C2 repair-capable boundary under flux.
- [ ] Run B4 x C2 multi-basin candidate under flux.
- [ ] Treat B4 x C2 as a flux stress row; keep B4 separability targeted at
      B4 x C5 in Iteration 6.
- [ ] Mark B4 rows `partial` or `not_applicable` if the multi-basin substrate
      is not sufficiently source-backed.
- [ ] Measure inbound/outbound flux balance.
- [ ] Measure retention capacity.
- [ ] Measure repair/reabsorption.
- [ ] Measure upstream/downstream boundary asymmetry.
- [ ] Populate the common matrix-cell report schema.
- [ ] Mark B3 rows `not_applicable` or `blocked` if the B2 unlock condition is
      not satisfied.

Expected artifacts:

- [ ] `outputs/n16_boundary_state_sweep_matrix.json`
- [ ] `reports/n16_boundary_state_sweep_matrix.md`
- [ ] `scripts/build_n16_boundary_state_sweep_matrix.py`

## Iteration 6. Selected Interaction Probes

- [ ] Confirm B2 has already been evaluated under C0, C1, and C2, or record
      explicit blockers before unlocking B3 x C4 breach/reclosure.
- [ ] Run B0 x C3 structured external coherence active null.
- [ ] Run B1 x C2 weak detectable boundary under flux.
- [ ] Run B2 x C1 persistent boundary under unstructured perturbation.
- [ ] Run B3 x C4 breach and repair / reclosure.
- [ ] Run B4 x C5 multi-basin exclusivity in shared medium.
- [ ] Record `requirements_satisfied`.
- [ ] Record `requirements_failed`.
- [ ] Populate the common matrix-cell report schema.
- [ ] Mark B3 x C4 `not_applicable` or `blocked` if the B2 unlock condition is
      not satisfied.

Expected artifacts:

- [ ] `outputs/n16_selected_interaction_probe_matrix.json`
- [ ] `reports/n16_selected_interaction_probe_matrix.md`
- [ ] `scripts/build_n16_selected_interaction_probe_matrix.py`

## Iteration 7. Comparative Requirements And Control Matrix

- [ ] Support partial MVP mode after Iteration 4.
- [ ] In partial MVP mode, summarize only Iterations 1-4, mark Iterations 5-6
      deferred, and avoid final AP6 closeout language.
- [ ] Emit `synthesis_mode = partial_mvp | full`.
- [ ] Emit `included_iterations`.
- [ ] Emit `deferred_iterations`.
- [ ] Emit `final_ap6_closeout_allowed`.
- [ ] Compare quiet calibration, challenge sweep, boundary-state sweep, and
      selected interaction probes using the common schema.
- [ ] Record `native_boundary_requirements_observed`.
- [ ] Record minimum coherence margin.
- [ ] Record minimum internal support.
- [ ] Record maximum leakage ratio.
- [ ] Record repair/reabsorption requirement.
- [ ] Record flux balance requirement.
- [ ] Record structured-external-coherence rejection requirement.
- [ ] Record inter-basin separation requirement.
- [ ] Externally supplied boundary label control fails closed.
- [ ] Post-hoc boundary labeling control fails closed.
- [ ] Hidden external-state injection control fails closed.
- [ ] Resource relabel as self control fails closed.
- [ ] Self-support relabel as external state control fails closed.
- [ ] Untracked boundary crossing control fails closed.
- [ ] Structured external coherence relabel control fails closed.
- [ ] Multi-basin merge or leakage relabel control fails closed.
- [ ] Identity acceptance relabel control fails closed.
- [ ] Selfhood/personhood relabel control fails closed.
- [ ] Semantic goal ownership relabel control fails closed.
- [ ] Native support relabel control fails closed.
- [ ] Stale internal or external state control fails closed.
- [ ] Missing boundary-side state control fails closed.
- [ ] Boundary drift outside frozen policy control fails closed.
- [ ] Run duplicate replay.
- [ ] Run artifact-only filesystem replay.
- [ ] Run snapshot/load replay.
- [ ] Run order-inversion replay.
- [ ] Record distinct blockers for negative controls.

Expected artifacts:

- [ ] `outputs/n16_basin_boundary_requirements_matrix.json`
- [ ] `reports/n16_basin_boundary_requirements_matrix.md`
- [ ] `scripts/build_n16_basin_boundary_requirements_matrix.py`

## Iteration 8. Claim Boundary And AP6 Classification

- [ ] Resolve every AP6 gate as validated or blocked.
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
- [ ] Audit N15 AP5 target/proxy boundary caveat.
- [ ] Draft whole-experiment interpretation.

Expected artifacts:

- [ ] `outputs/n16_claim_boundary_record.json`
- [ ] `reports/n16_claim_boundary_record.md`
- [ ] `scripts/build_n16_claim_boundary_record.py`

## Iteration 9. Closeout And N17 Handoff

- [ ] Freeze final supported AP level if warranted.
- [ ] Record final claim ceiling.
- [ ] Record final controls.
- [ ] Record final blockers.
- [ ] Record final N17 handoff.
- [ ] Record whether targeted Phase 8 is optional, required, or deferred.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `fully_native_integration_opened = false`.
- [ ] Confirm all source rows receive specific final roles.

Expected artifacts:

- [ ] `outputs/n16_closeout_and_handoff.json`
- [ ] `reports/n16_closeout_and_handoff.md`
- [ ] `scripts/build_n16_closeout_and_handoff.py`

## Setup Verification

- [ ] `git diff --check`
- [ ] `git diff -- src`
