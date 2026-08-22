# B1-GR GRC9V3 Continuation And Read-Back Verification Implementation Checklist

## Current Status

```text
branch = experiment-B1-continuation-readback
status = grv4_P4_1_mechanically_passed_awaiting_human_review
controlling_specification = draft_3_4_1_pre_execution_mathematical_execution_sealed
controlling_specification_sha256 = 7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44
runtime_under_test = unchanged_GRC9V3
runtime_change_authorized = false
src_change_authorized = false
existing_test_change_authorized = false
positive_evidence_opened = true_bounded_physical_branch_existence_only
current_gate = GRV4_P4_1_scientific_review
verification_closeout_ladder_rung_assigned = true
verification_closeout_rung = GRV-C3
verification_closeout_ceiling = GRV-C4_candidate_pending_acceptance
B1_L_execution_authorized = false
N32_selected = false
l04_selected = false
```

## Initialization

- [x] Create a dedicated B1 experiment branch.
- [x] Create the B1-GR experiment directory.
- [x] Integrate Draft 3.2 as the experiment-local intake specification.
- [x] Preserve the accepted Draft 3.2 intake beside the controlling revision.
- [x] Advance the controlling specification to Draft 3.3 for pre-execution hardening.
- [x] Preserve Draft 3.3 beside the controlling revision.
- [x] Advance the controlling specification to Draft 3.4 for identification,
  codec, causal-inference, and evidence-lifecycle hardening.
- [x] Preserve Draft 3.4 beside the controlling revision.
- [x] Advance the controlling specification to Draft 3.4.1 for mathematical
  correctness and execution sealing.
- [x] Add the B1-GR README.
- [x] Add the B1-GR implementation plan.
- [x] Add the B1-GR implementation checklist.
- [x] Map Iterations 1-9 one-to-one to GRV0-GRV8.
- [x] Document the accepted B1-GR path and implementation-file name corrections.
- [x] Preserve unchanged-runtime, no-`src/`, and no-existing-test-change boundaries.
- [x] Keep N32 unselected.
- [x] Create B1-L as a deferred provenance/prerequisite record only.
- [x] Review and accept the B1-GR specification, plan, and checklist before GRV0.

## Global Execution Rules

- [ ] Execute GRV gates serially and consume accepted prerequisite digests.
- [ ] Consume prerequisite result digests for provenance and accepted-anchor
  digests/references for authorization; never treat a receipt alone as acceptance.
- [ ] Commit each gate's executable experiment code in its clean input revision
  before running that gate.
- [ ] Classify every gate-input code/config/fixture change and require protocol
  readmission for scientific-method, threshold/config, fixture, or
  claim-envelope changes.
- [ ] Start each gate from a clean accepted input revision.
- [ ] Write and validate a non-self-referential result receipt before committing gate results.
- [ ] Record scientific acceptance in a separate authority-bearing acceptance anchor.
- [ ] Record result revision, receipt payload digest, accepting identity and
  role, review method and timestamp, acceptance status, and immutable
  signature/reference in every acceptance anchor.
- [ ] Refuse to cross a missing, rejected, blocked, or superseded prerequisite acceptance anchor.
- [ ] Preregister authorized human acceptors/roles, review methods, self-review,
  and independent-review requirements before outcomes.
- [ ] Run Python commands through `.venv`.
- [ ] Use repository-relative paths in committed artifacts.
- [ ] Hash canonical semantic payloads without self-reference or volatile metadata.
- [ ] Declare byte, tolerance, or seeded-search reproducibility per artifact.
- [ ] Keep raw snapshots separate from derived matrices and reports.
- [ ] Declare thresholds, norms, clocks, and horizons before outcome inspection.
- [ ] Record reached-state and synthetic-valid counterfactuals separately.
- [ ] Record failed searches and blocked gates rather than omitting them.
- [ ] Keep `alpha`, `gamma`, `beta`, transition multipliers, and spatial Hessians distinct.
- [ ] Keep retention, read effect, write effect, and closed-loop evidence distinct.
- [ ] Keep field, current, axis, orientation, and full-reflexive equivalence distinct.
- [ ] Keep assumptions failed or unidentifiable separate from falsified claims.
- [ ] Verify protected GRC source/spec/test paths remain unchanged after each gate.
- [ ] Route any post-GRV1 protected-path discovery as
  `source_or_specification_mismatch`; never silently amend manifest v1.
- [ ] Bind every result to substrate revision, protected-manifest digest,
  experiment input revision/tree digest, and accepted prerequisite anchors.
- [ ] Supersede or block the complete transitive downstream acceptance graph
  when a revision-distinct baseline is admitted.
- [ ] Keep generic positive evidence false through GRV1 and open it only from an
  accepted GRV2+ source-current scientific row; keep role flags separate.
- [ ] Keep B1-L unopened until accepted GRV-C6 and handoff admission.
- [ ] Keep preserved Drafts 3.2, 3.3, and 3.4 and controlling Draft 3.4.1 immutable during execution.

## Iteration 1 - GRV0 Specification And Baseline Admission

- [x] Accept Draft 3.4.1 as the exact controlling specification version.
- [x] Materialize GRV0 package surfaces and commit the clean `P0`
  package-preparation revision before execution.
- [x] Record exact graph repository revision.
- [x] Record exact geometric-theory repository revision.
- [x] Digest both controlling core papers.
- [x] Record both paper paths, roles, blob identities where available, and
  SHA-256 digests in `theory_source_manifest.json`.
- [x] Freeze `protected_path_manifest_v0` for GRC source/spec/test paths.
- [x] Freeze `experiment_path_manifest.json` and the exact non-self-referential experiment-tree digest scope.
- [x] Include every discovered load-bearing source in the protected manifest.
- [x] Record substrate base and experiment execution revisions separately.
- [x] Verify a clean execution checkout.
- [x] Run the complete existing test suite in `.venv`.
- [x] Record test command, environment, duration, pass/fail/skip counts, and logs.
- [x] Serialize the theory claim ledger.
- [x] Serialize the theory assumption registry.
- [x] Serialize the derivation-status appendix.
- [x] Serialize the theory debt register.
- [x] Serialize proof-note and traceability records.
- [x] Serialize the gate dependency map.
- [x] Materialize all six normative `hypotheses/` views.
- [x] Materialize and map all normative scripts to GRV gates.
- [x] Freeze contradiction and theory-reopening schemas.
- [x] Freeze canonical JSON, semantic digest, path, artifact, result-receipt, and acceptance-anchor schemas.
- [x] Verify dedicated schema or named `$defs` coverage for every required
  manifest and final decision artifact.
- [x] Add experiment-local schema, state-codec, tangent-basis, intervention, receipt, and convergence tests.
- [x] Add and pass `test_edge_space.py` for projector algebra and covariance.
- [x] Add and pass `test_spec_propagation.py` against the current specification
  ID/digest, README, plan, checklist, gate/artifact names, and GRV0 obligations.
- [x] Freeze experiment-local numerical dependency policy.
- [x] Emit the complete numerical environment record.
- [x] Preregister the `A-NONNORMAL-CONTROL` evidence mode and threshold.
- [x] Preregister the `A-FAST-SLOW` measure and threshold where applicable.
- [x] Preregister the present-current convention and acceptance authority/review policy.
- [x] Serialize the complete fixed-topology envelope implementation for GRV0 emission.
- [x] Validate every specification-name to exact runtime-parameter mapping in the envelope implementation.
- [x] Freeze orthonormal zero-sum coherence tangent bases.
- [x] Freeze ambient coordinate identification and branch-dependent metric transport.
- [x] Freeze block-specific causal-equivalence tolerances, RNG treatment,
  administrative advancement, duplicate-surface reconciliation, and
  per-horizon accumulated-error rules.
- [x] Freeze gate-input revision-change classifications and protocol-readmission rules.
- [x] Verify no `src/` or existing-test diff during P0 preparation.
- [x] Emit GRV0 JSON artifacts and report.
- [x] Emit and validate the GRV0 result receipt.
- [x] Record GRV0 scientific acceptance in a separate accepted anchor before GRV1.
- [x] Assign `GRV-C1` only if exact baseline and tests are admitted.
- [x] Keep all scientific evidence flags false.

GRV0 mechanical result:

```text
clean_input_revision = 5f9297378a26b8093f523cd11f8cb9f0f0aef723
result_revision = 97a9a6bf9cd20ca6c1adcc0feee26712df9569fb
substrate_base_revision = 589f933e5649c34d3ad54a5f8dbdba2a20e968d7
theory_revision = 5a8b01ae60165054da617db649c5a039755a18ec
protected_tree_sha256 = 4a398c1b50a55c40418bfae3af4e4e3dc07a1a313f79b3747a546dfa27c453a2
experiment_tree_sha256 = f132c8917da074118b47563c1d8d4020e20243a93dd7fb6c471f9cdb79783c8d
receipt_payload_sha256 = a583d763b2d5e72af3f3e2ad5401aca8c143eff1aa73427404c2f8286e1ed9df
existing_tests = 1354_passed_0_failed_0_skipped
mechanical_status = passed
receipt_status = awaiting_scientific_review
scientific_acceptance = accepted_anchor_commit_454b2c55d1682c3ead46f6036ed725445b37fc08
positive_evidence_opened = false
```

Stop condition:

```text
dirty_or_failing_baseline or missing_exact_source_identity stops execution
```

## Iteration 2 - GRV1 Instrumentation And Source Fidelity

- [x] Reproduce the existing two-node transport anchor.
- [x] Capture and verify complete canonical `step()` order.
- [x] Verify fixed topology and no-event envelope.
- [x] Run separate transport-stage and full-step materialized-`K` counterfactuals.
- [x] Classify direct use, overwrite-before-use, diagnostic status, or unknown; route source mismatch separately.
- [x] Run physical `J -> -J` controls.
- [x] Run edge-coordinate reorientation/covariance controls separately.
- [x] Classify magnitude, axis, orientation, and reconstruction separately.
- [x] Inventory every excluded or administratively advancing field.
- [x] Carry causal and unknown excluded fields into GRV3 closure candidates.
- [x] Validate canonical deep-clone intervention and rebuild behavior.
- [x] Validate raw snapshot and derived-artifact separation.
- [x] Validate replay tolerances and canonical serialization.
- [x] Emit `protected_path_manifest_v1` with only source-base-matching additions,
  or as an explicit unchanged successor when GRV1 discovers no added path.
- [x] Freeze the post-GRV1 contradiction route for any later protected-path discovery.
- [x] Emit `instrumentation_validation.json`, `fixture_registry.json`, and report.
- [x] Emit and validate the GRV1 result receipt.
- [x] Record GRV1 scientific acceptance in a separate accepted anchor before GRV2.
- [x] Assign no branch, continuation, retention, or read-back claim.

GRV1 mechanical result:

```text
clean_input_revision = cbe52fe454c82c8cb10ad3f66175c711bc0c803e
substrate_base_revision = 589f933e5649c34d3ad54a5f8dbdba2a20e968d7
input_experiment_tree_sha256 = d4ae404c001c08e755f2a8f20f93775f34f750b8f5d0da2ce4bf9361bb331bfe
protected_tree_sha256 = 4a398c1b50a55c40418bfae3af4e4e3dc07a1a313f79b3747a546dfa27c453a2
protected_file_count = 379
receipt_payload_sha256 = c8f51f4cc1f816726aa65d56e9165809ba54a5d47f4259e4e3f3318712f5b1bf
mechanical_status = passed
scientific_acceptance = never_accepted_superseded_by_P1.1
candidate_closeout_ceiling = GRV-C2
positive_evidence_opened = false
```

Bounded interpretation:

```text
K cache = diagnostic-only for transport and overwritten before full-step use
old J magnitude = exact sign-even J^2 source path, unresolved at the F0 W tolerance
old J orientation = not retained across transport or the complete step
edge-coordinate reversal plus J sign mapping = covariant
current = reconstructed anew by transport
formed branch / continuation / retention / read-back / write-back = unsupported
```

Pre-acceptance review disposition:

```text
candidate_result_revision = 45435c8e2da28908fabe58ba93c2c1af4b08930c
candidate_receipt_payload_sha256 = c8f51f4cc1f816726aa65d56e9165809ba54a5d47f4259e4e3f3318712f5b1bf
acceptance_status = never_accepted
disposition = superseded_by_P1_1_source_fidelity_strengthening
specification_change = false
claim_ceiling_change = false
```

GRV1 P1.1 hardening:

- [x] Prove snapshot, diagnostic read, hashing, save, and load observation are nonmutating.
- [x] Prove nested clone isolation for conductance, current, caches, K, and RNG state.
- [x] Emit and validate the W/J/K duplicated-surface authority map.
- [x] Replace arbitrary K perturbation with structurally valid small, moderate,
  and large fixed-path counterfactuals.
- [x] Record stagewise `J -> -J` use, sign erasure, and overwrite boundaries.
- [x] Verify coordinate reorientation is involutive and compare after inverse identification.
- [x] Prove native `step()` and exact public-stage replay agree at every captured boundary.
- [x] Record call ordinal, multiplicity, input/output digests, and changed fields.
- [x] Record fixed transition environment and explicit RNG before/after status.
- [x] Reproduce the F0 result under same-input object reuse, fresh instance,
  snapshot/load, and a fresh Python process.
- [x] Expand the confirmed load-bearing source map without altering the protected tree.
- [x] Keep all scientific evidence flags false and preserve the GRV1 claim ceiling.

GRV1 P1.1 mechanical result:

```text
clean_input_revision = 416f49e9cc05a21a86aaa7c7765cd9d64690f709
substrate_base_revision = 589f933e5649c34d3ad54a5f8dbdba2a20e968d7
input_experiment_tree_sha256 = fb8cb0577f3937dcbfec735d0d9dfabdaee87a2f38f97db0488ad3e9cdc40b5a
protected_tree_sha256 = 4a398c1b50a55c40418bfae3af4e4e3dc07a1a313f79b3747a546dfa27c453a2
protected_file_count = 379
receipt_payload_sha256 = 9535c80100c6813b69a327cfa80f0180f2288ee7e87e6e550c3168261353855a
superseded_candidate_receipt = c8f51f4cc1f816726aa65d56e9165809ba54a5d47f4259e4e3f3318712f5b1bf
mechanical_status = passed
receipt_status = awaiting_scientific_review
scientific_acceptance = accepted_anchor_commit_bc12787e885b9dcc7d939c98a7e2e3ea84f2d213
candidate_closeout_ceiling = GRV-C2
positive_evidence_opened = false
```

P1.1 strengthening outcome:

```text
instrumentation / ordinary complete state = exact
native step / public-stage boundary trace = exact
observation mutation = none detected
nested clone aliasing = none detected
W authority = state.base_conductance
J authority = state.port_edges[*].flux_uv
K consumer on tested F0 path = not identified
K global causal absence = not claimed
old J sign = visible pre-transport, erased by current reconstruction
coordinate reorientation = involutive and covariant
RNG = causal state, unchanged in lambda-birth-zero F0
fresh-process replay = exact
node_values / edge_values = unknown and carried into GRV3 closure
```

## Iteration 3 - GRV2 Strong Formed Branches

- [x] Certify a homogeneous two-node zero-current branch.
- [x] Search for a nonuniform two-node branch and certify every accepted result.
- [x] Search for and classify nonuniform triangle branches and certify every accepted result.
- [x] Preserve bounded negative search evidence when no nonuniform branch is
  found; do not infer global nonexistence or fail a valid homogeneous result.
- [x] Run symmetry controls.
- [x] Run port-relabel controls.
- [x] Record full-step residuals.
- [x] Record per-block `C/W/J/Phi/G/identity/budget` internal-stage residuals,
  including budget-correction no-op status.
- [x] Record pre-continuity, pre-budget, budget-correction, post-budget, and final-refresh states.
- [x] Require budget correction to be a numerical no-op for an unqualified strong branch.
- [x] Classify provisional physical strong, projection-supported,
  step-boundary-only, and internally periodic alternatives explicitly.
- [x] Defer `causal_strong_branch` upgrade until the GRV3 closure audit passes.
- [x] Verify event and topology assertions.
- [x] Save, load, and replay every accepted branch.
- [x] Record solver seeds, tolerance, convergence, and rejected searches.
- [x] Record the complete search space/budget, all accepted and rejected roots,
  deduplication, continuation lineage, selection rule, and held-out replay for
  each selected branch.
- [x] Record distance from positivity, conductance-floor, spark, basin/sink, growth, and event boundaries.
- [x] Emit `fixed_branch_registry.json` and report.
- [x] Emit and validate the GRV2 result receipt.
- [x] Record the GRV2 acceptance decision in a separate human anchor after review.
- [x] State explicitly that branch existence is not continuation or retention.

### P2.2 provisional result, never accepted

```text
input_revision = d224a10302bfa030da817105dbf65c2a23f41483
mechanical_status = passed
scientific_acceptance = never_accepted_superseded_by_P2_3_adversarial_hardening
receipt_payload_sha256 = 967f1adc5d8b36c2cdf0fb5c0153ac43b37e14f5fd6c0f1bcb76d92f38f43c94
search_rows = 144
accepted_provisional_physical_strong_branches = 48
F1_homogeneous_branches = 16
F2_nonuniform_branches = 16_at_site_potential_scale_1.0
F3_nonuniform_branches = 16_at_site_potential_scale_1.5
rejected_nonuniform_rows = 96_homogeneous_roots_outside_target
maximum_full_step_l_inf = 1.6344259279321705e-10
maximum_internal_stage_l_inf = 1.6344259279321705e-10
maximum_budget_correction_l_inf = 2.220446049250313e-16
save_load_replay = 48_of_48_passed
symmetry_and_port_controls = 9_of_9_passed
held_out_fresh_process_replay = 3_of_3_passed
protected_runtime_spec_root_test_tree = unchanged
branch_class = provisional_physical_strong_branch
causal_strong_branch = deferred_to_GRV3
candidate_closeout_ceiling = GRV-C3
positive_evidence_opened = true_bounded_physical_branch_existence_only
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
```

The accepted candidate rows show that the current unchanged GRC9V3 runtime has
bounded homogeneous and nonuniform formed fixed branches under the committed
near-neutral transport envelope. The F2/F3 scale localization is evidence from
the declared grid, not a global branch theorem. Every zero-current row remains
on a basin/sink identity boundary, so GRV3 must still determine whether the
excluded and administrative fields admit a closed causal state before any
`causal_strong_branch` upgrade or transition-Jacobian interpretation.

### P2.3 preacceptance adversarial hardening

- [x] Preserve the exact P2.2 search grid, solver, fixtures, runtime, thresholds,
  and claim ceiling.
- [x] Record raw-candidate to canonical `C/W/J` deltas and require load-bearing
  canonicalization admission.
- [x] Require authoritative old-current zero and authoritative conductance-surface
  consistency within declared tolerances.
- [x] Record continuity delta, budget correction, active-set identity, clipping,
  and active-set margin per branch.
- [x] Add a four-beat unperturbed physical hold across advancing `step_index` and time.
- [x] Keep cache refresh and complete causal-state closure explicitly deferred to GRV3.
- [x] Record full canonical branch signatures, symmetry-orbit counts, and row-count
  nonindependence.
- [x] Add experiment-local regression tests for the new controls.
- [x] Commit the clean P2.3 input revision before execution.
- [x] Rerun all 144 rows from the clean P2.3 input.
- [x] Regenerate and validate every branch snapshot, registry, ledger, report,
  protected manifest, and GRV2 receipt.
- [x] Record the superseding P2.3 result and keep scientific acceptance pending
  a separate authorized human anchor.

Adversarial-review disposition:

- [x] Require complete-step and internal-stage certification; classify internal
  excursion/cycle and projection-supported alternatives separately.
- [x] Require numerical-no-op budget correction, unchanged active set, no
  clipping, and positive active-set margin.
- [x] Record the representable nonsmooth margin vector and carry the intrinsic
  zero-current sink/basin boundary into GRV3 rather than rejecting GRV2.
- [x] Canonicalize through native reconstruction, quantify raw-to-canonical
  load-bearing deltas, and exclude reconstructed fields from solver coordinates.
- [x] Require authoritative old `J` to be zero within tolerance and authoritative
  conductance surfaces to agree.
- [x] Hold every accepted physical branch for four unperturbed complete beats;
  do not promote this to stability, retention, or causal-state closure.
- [x] Keep solver convergence and independent branch certification separate.
- [x] Require absolute and relative blockwise residuals for `C/W/J/Phi/G`,
  identity, and budget surfaces.
- [x] Require explicit nonuniform contrast and distance from the homogeneous
  branch for F2/F3.
- [x] Preserve raw branch IDs, full canonical signatures, symmetry-orbit IDs,
  nontrivial F2/F3 controls, opposite seed directions, and row-count
  nonindependence.
- [x] Keep exploratory values as seeds only and emit new solved-state digests and
  certificates.
- [x] Keep complete bounded-search accounting and classify numerical failures as
  unresolved rather than negative branch evidence.
- [x] Preserve the committed parameter grid and fixed exogenous parameters.
- [x] Treat the complete double-refresh beat as authoritative without claiming
  that its second refresh is causally necessary.
- [x] Use the runtime canonical potential gauge.
- [x] Require save/load replay for every branch and selected fresh-process replay.
- [x] Record that a solver-tolerance sweep is not part of sealed GRV2 and make no
  numerical-tolerance-robustness claim.

P2.3 result:

```text
input_revision = 228e1d4f1f13af7ab7ff464dca592d4decd609f9
mechanical_status = passed
scientific_acceptance = accepted_anchor_pending_commit_reference
receipt_payload_sha256 = 73450d2a445770fc3f4b0f2871d3d10c865e097fdd305d97945e41dd7b707c63
search_rows = 144
accepted_provisional_physical_strong_branch_rows = 48
unique_canonical_symmetry_orbits = 32
rejected_nonuniform_rows = 96_homogeneous_roots_outside_target
administrative_phase_hold_beats_per_branch = 4
administrative_phase_hold_rows = 192
maximum_four_beat_cumulative_physical_l_inf = 6.537703711728682e-10
maximum_authoritative_current_l_inf = 6.117240047785867e-11
minimum_budget_active_set_margin = 1.0000000000020002
all_canonicalization_admissions = passed
all_authoritative_surface_assertions = passed
all_budget_active_set_and_no_clipping_controls = passed
all_four_beat_physical_holds = passed
all_noncache_excluded_state_exact = true
cache_refresh_observed = 48_of_48_branches
cache_and_complete_causal_state_status = deferred_to_GRV3
causal_strong_branch = deferred_to_GRV3
candidate_closeout_ceiling = GRV-C3
positive_evidence_opened = false_pending_authorized_human_acceptance
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
```

GRV2 acceptance disposition:

```text
acceptance_status = accepted
acceptance_role = experiment_owner
accepted_result_revision = e1dc01f4948b7791c733eb62c15179d04619cd8e
accepted_receipt_payload_sha256 = 73450d2a445770fc3f4b0f2871d3d10c865e097fdd305d97945e41dd7b707c63
accepted_closeout_rung = GRV-C3
physical_formed_branch_existence = accepted_bounded_candidate_evidence
causal_strong_branch = deferred_to_GRV3
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
```

## Iteration 4 - GRV3 Causal State And Complete Transition Jacobian

### Pre-Execution Contract

- [x] Bind GRV3 to the exact accepted GRV2 registry, receipt, and acceptance anchor.
- [x] Freeze execution over all 48 accepted branch rows before spectra.
- [x] Keep all 32 symmetry-orbit labels as dependence metadata, not branch selection.
- [x] Forbid post-spectrum branch selection.
- [x] Freeze `GRV3-A -> GRV3-B -> GRV3-C` execution order.
- [x] Permit GRV3-A to pass while GRV3-B is blocked on a non-smooth stratum.
- [x] Require positive two-sided stratum margin for every classical derivative column.
- [x] Classify a failed stratum gate as blocked, not unconverged.
- [x] Freeze the `(C,W,J)` candidate chart, bounded reductions, horizons, step sizes,
  categorical surfaces, and claim ceiling in `configs/grv3_causal_state.json`.
- [x] Keep runtime, `src/`, and pre-existing tests unchanged.
- [x] Supersede the unaccepted P3 execution because the runner audited reduced
  codecs but did not apply GRV3-B/C to codec-admitted reductions.
- [x] Preserve branches, fixtures, thresholds, reduction definitions, and claim ceiling.
- [x] Apply GRV3-B/C to every codec-admitted `C-W` and `C` candidate in P3.1.
- [x] Forbid outcome-driven selection of one primary reduced coordinate.
- [x] Supersede unaccepted P3.1 because spectral/subspace, response, and
  ill-conditioned-eigenvector diagnostics were not yet complete machine gates.
- [x] Preserve the exact P3.1 branch scope, fixtures, coordinate candidates,
  finite-difference steps, thresholds, runtime, and claim ceiling in P3.2.
- [x] Require eigenvalue-set and invariant-subspace convergence before temporal
  mode evidence, and response-surface convergence before response evidence.
- [x] Apply the preregistered nonnormal condition and finite-horizon bounds;
  block individual eigenvector interpretation when conditioning fails.
- [x] Require a full-rank, low-residual cluster span before using a cluster as
  the fallback interpretation object.
- [x] Surface the unchanged P3.2 spectral window, cluster, and residual values
  in the explicit P3.3 method config before scientific acceptance.
- [x] Record every otherwise admitted but interpretation-blocked matrix by
  branch and coordinate in the final machine summary.
- [x] Supersede unaccepted P3.3 after adversarial review identified missing
  phase, omitted-state, decoder, RNG, residual, nonlinear-current, metric, and
  covariance admission gates.
- [x] Preserve the P3.3 branch scope, fixtures, runtime, coordinate candidates,
  finite-difference steps, spectral thresholds, and claim ceiling in P3.4.
- [x] Freeze derivative-level administrative phase offsets and require phase
  invariance before fixed-operator spectral interpretation.
- [x] Freeze per-cache-key and placeholder-field omission audits over the
  declared codec horizons; forbid whole-cache admission.
- [x] Freeze decoder-correction-over-`h`, RNG-consumption, and
  branch-residual-over-`h` gates for every derivative column.
- [x] Freeze separate odd first-order and even quadratic `J` diagnostics without
  using either as eigensystem or eliminability evidence.
- [x] Freeze a declared branch-scale block metric, retain raw and normalized
  participation as diagnostic only, and block joint `C-W` mode claims.
- [x] Freeze alternate zero-sum basis covariance and symmetry-orbit conjugacy.
- [x] Execute P3.4.1 from a clean committed input revision.
- [x] Confirm all P3.4 machine gates and classify any blocked matrices without
  numerical repair.

- [x] Freeze and test the branch-relative causal-state encoder and decoder.
- [x] Require coordinate round trip `E_X(D_X(x)) ~= x`.
- [x] Require reached-state canonicalization `D_X(E_X(S)) ~causal S`.
- [x] Require transition commutation `E_X(F(S)) ~= F_X(E_X(S))`.
- [x] Require preregistered bounded-horizon commutation for every codec horizon.
- [x] Report bounded-horizon causal closure without promoting it to global Markov sufficiency.
- [x] Apply exact categorical/identifier equality and block-specific numerical
  tolerances with declared per-horizon accumulated-error bounds.
- [x] Admit a continuous square causal-state coordinate before eigenanalysis.
- [x] Represent causally relevant categorical state as a discrete stratum and
  differentiate only within a fixed stratum.
- [x] Record positive two-sided stratum margins and matching runtime paths for every derivative column.
- [x] Run matched `C,J` with differing valid `W` through canonical interventions.
- [x] Run matched `C,W` with differing `J`.
- [x] Run matched `C,W` with sign-reversed `J`.
- [x] Compare branch-consistent and perturbed derived surfaces.
- [x] Separate reachable-history and synthetic-valid pairs.
- [x] Audit every excluded physical/administrative field for causal relevance.
- [x] Classify synthetic states as structurally valid, constitutively consistent, and runtime reachable separately.
- [x] Freeze admitted causal coordinate and zero-sum tangent order.
- [x] Freeze interior-safe `W`, `J`, and zero-coordinate perturbation policies.
- [x] Compute square complete-step causal-transition Jacobians only for admitted charts.
- [x] Compute smooth derived response Jacobians separately.
- [x] Record categorical/event surfaces as margins and threshold records, not eigensystem rows.
- [x] Verify relative column, matrix norm, eigenvalue-cluster, and subspace-angle convergence.
- [x] Record `C/W/J` blocks and residuals.
- [x] Record left/right eigensystems and conditioning.
- [x] Record conservation, gauge, and branch-tangent identification statuses.
- [x] Apply the preregistered nonnormal evidence mode.
- [x] Apply the preregistered fast/slow rule where applicable.
- [x] Classify stable slow, neutral, oscillatory, and unstable clusters.
- [x] Classify counterfactual sensitivity, constitutive independence,
  runtime-causal independence, and eliminability separately for each candidate block.
- [x] Enforce distinct structural-validity, constitutive-consistency,
  runtime-reachability, and runtime-causal-independence admission gates.
- [x] Test bounded C-only and joint C-W reductions.
- [x] Gate `causal_strong_branch` candidate status on codec and closure admission;
  leave the scientific upgrade pending human review.
- [x] Emit `complete_step_jacobians.json`, `slow_cluster_registry.json`, and report.
- [x] Emit and validate the GRV3 result receipt.
- [x] Emit a separate GRV3 acceptance anchor only after human scientific review.
- [x] Do not equate a slow joint mode with core retention.

### Iteration 4 Result

P3.3 is retained as superseded preliminary evidence. It has no scientific
acceptance anchor and cannot authorize GRV4. The P3.4 result will replace the
block below after clean execution.

```text
result_status = superseded_unaccepted_by_P3_4_method_completion
input_execution_revision = 0a323d2d5920b3bedaef052fd193777942add9be
receipt_payload_sha256 = 7cf749fa8a46f6b219a27515504e4ad671a386144b2ef8626fb14e63a4fb104d
mechanical_status = passed
scientific_acceptance = never_accepted_superseded_by_P3_4
branches_audited = 48
bounded_C_W_J_codec_closure_candidates = 48
full_C_W_J_square_jacobians = 0
reduced_square_jacobians = 64
reduced_branch_rows = 32
reduced_symmetry_orbits = 16
temporal_mode_interpretation_pass_matrices = 61
response_convergence_pass_matrices = 64
finite_horizon_nonnormal_pass_matrices = 64
individual_eigenvector_condition_block_matrices = 2
cluster_fallback_block_matrices = 2
branches_with_at_least_one_temporal_candidate = 32
GRV_C4 = unsupported_pending_GRV4
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
```

Every full `(C,W,J)` chart is blocked at the classical derivative gate by at
least one non-smooth current/sink/basin stratum column. This does not undo the
48 bounded codec-closure candidates. The two frozen reductions admit 64
matrices: `C-W` and `C` on each of 32 F2/F3 branch rows. Sixty-one matrices pass
the complete temporal interpretation gate. `grv2-f3-036/C-W` is blocked by a
fast-subspace dimension change across the step sweep;
`grv2-f3-037/C-W` and `grv2-f3-041/C-W` are additionally blocked by the frozen
eigenvector-condition and full-cluster fallback gates. The separately frozen
`C` chart passes on all three rows, so no branch was retained through post-hoc
coordinate selection.

All 64 admitted matrices pass response convergence and the finite-horizon
nonnormal bound; maximum amplification is about `1.00000000004` against the
frozen ceiling `2.0`. Maximum adjacent derivative-column error is about
`1.74e-11`; maximum response error is about `7.38e-11`. The two ill-conditioned
`C-W` eigensystems reach condition number about `9.13e38`, so their individual
eigenvectors are diagnostic only and their unresolved cluster spans do not
rescue interpretation. The fast/slow current assumption is `not_applicable` on
all admitted matrices because no separate current-relaxation sector or two
finite decaying clusters were identified.

The 192 counterfactual rows are structurally valid synthetic pairs, not reached
history pairs. `W` and `J` changes produce no resolved next-step physical
sensitivity in this bounded test, and the derived-potential perturbation is
overwritten by the complete step. These results constrain candidate-block
interpretation; they do not establish global eliminability. The result opens no
stability, continuation, retention, read-back, or write-back claim. GRV4 remains
required before `GRV-C4` can be considered.

### P3.4.1 Current Result

```text
input_execution_revision = b1c233be164c6e88d21f5386ae2483cb2e08ecad
receipt_payload_sha256 = 83a2650f57fe3d1a814155bf6e8621881d01468b36cde0f1b460af02339b92cc
mechanical_status = passed
scientific_acceptance = accepted_bounded_result_at_revision_0dedbf9
branches_audited = 48
bounded_causal_closure_candidates = 48
omitted_state_decomposition_pass_branches = 48
full_C_W_J_square_jacobians = 0
reduced_square_jacobians = 64
phase_operator_pass_matrices = 64
basis_covariance_pass_matrices = 64
symmetry_covariance_pass_pairs = 32
symmetry_covariance_failed_or_blocked_pairs = 0
temporal_mode_interpretation_pass_matrices = 61
response_convergence_pass_matrices = 64
GRV_C4 = unsupported_pending_GRV4
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
```

P3.4.1 preserves the P3.3 matrix result while establishing why a fixed reduced
operator is admissible on the tested envelope. All 64 reduced matrices pass the
administrative-phase and alternate-basis covariance gates; all 32 declared
multirow symmetry comparisons pass. All 48 branches pass the per-key omitted
state audit, covering 1,536 reconstructed-or-inert cache rows and 96 absent
placeholder rows without admitting the whole cache or claiming global
eliminability. All 1,188 derivative-column attempts pass decoder and RNG
controls. The maximum decoder correction divided by `h` is about `7.19e-12`,
the maximum branch residual divided by `h` is about `5.47e-7` against the
frozen `1e-3` ceiling, the maximum phase matrix error is about `2.02e-11`, and
the maximum alternate-basis conjugacy error is about `2.20e-11`.

The complete-beat odd/even `J` diagnostic is unresolved at the declared steps.
This does not erase GRV1's stage-local sign-even `J^2` path, does not establish
`J` eliminability, and does not reopen the non-smooth full-chart derivative.
Raw and declared-scale participation remain diagnostic and no joint `C-W` mode
claim is made. The same three `C-W` interpretations remain blocked as in P3.3;
their separately frozen `C` candidates pass. The experiment owner accepted the
bounded result at revision `0dedbf9`; the acceptance anchor binds that revision
and its exact result-receipt digest. GRV4 is authorized without upgrading any
blocked full-state or continuation interpretation.

## Iteration 5 - GRV4 Frozen-Conductance Versus Full Recurrence

### P4 Method Freeze

```text
branch_scope = all_48_certified_GRV2_rows
standalone_frozen_comparator_scope = all_48_rows
primary_full_map_comparison_scope = exactly_32_GRV3_admitted_C_rows
zero_current_boundary_rows = retained_as_blocked_full_comparisons
tangent_basis = canonical_zero_sum_identical_to_GRV3
sign_probe_amplitudes = [0.001, 0.01]
runtime_dt_multipliers = [0.125, 0.25, 0.5, 1.0, 2.0, 4.0]
weak_monotonicity_includes_stationary_equality = true
post_spectrum_branch_or_coordinate_selection = false
frozen_operator_class = substrate_reduced_clamped_counterfactual_only
H_P = runtime_functional_second_variation
H_cont = -H_P
temporal_operator = A_W_H_cont_not_H_cont_alone
state_metric = accepted_GRV3_branch_metric
mode_matching = clustered_real_invariant_subspaces
unit_circle_decisions = uncertainty_aware
symmetry_check = matrix_conjugacy
W_elimination_claim = blocked
fast_slaving_claim = blocked
geometry_only_or_mobility_only_attribution = blocked
joint_C_W_mode_claim = blocked
full_core_continuation_operator_claim = blocked
```

The staged sign comparator consumes the unchanged `compute_potential`,
`compute_flux`, and `apply_continuity` implementations while holding the
accepted branch `W` fixed. It is not a replacement `step()`: conductance
reconstruction, identity, spark, choice, growth, boundary, budget, and final
refresh stages are excluded and recorded as reduction assumptions. The
complete-step side is consumed from the accepted GRV3 matrices; P4 does not
rerun or reinterpret blocked GRV3 derivatives.

- [x] Complete the runtime sign audit.
- [x] State whether `P_G`, `-P_G`, neither, or only a small-step limit is monotone.
- [x] Separate analytic semidiscrete sign, runtime-timestep behavior, and timestep sweep.
- [x] Construct the frozen-`W` constrained comparator outside `src/`.
- [x] Use the same conserved tangent basis as GRV3.
- [x] Construct the declared mobility, semidiscrete, and explicit-step comparators.
- [x] Label analytical comparator objects as non-runtime state.
- [x] Compare frozen spectra with complete-step multipliers.
- [x] Compare modes/subspaces and stability classifications.
- [x] Record every reduction and elimination assumption.
- [x] Emit `frozen_full_comparison.json` and report.
- [x] Emit and validate the GRV4 result receipt.
- [ ] Emit a separate GRV4 acceptance anchor only after human scientific review.
- [x] Do not claim the full core continuation operator.

### Preliminary P4 Result Superseded Before Acceptance

```text
input_execution_revision = e21ec2cd9f3dcfdacb2b707d707b6480ce856bf0
receipt_payload_sha256 = 46420b14840bda5258d415463e7376bbc929557a907055b10f4d2fb23b4fc3fc
mechanical_status = passed
scientific_acceptance = awaiting_human_review
review_disposition = unaccepted_preliminary_evidence_superseded_by_P4_1
acceptance_anchor_exists = false
branches_audited = 48
standalone_frozen_comparators = 48
primary_full_map_comparisons = 32
blocked_full_map_comparisons = 16
primary_agreement_count = 32
primary_bounded_difference_count = 0
secondary_C_W_comparison_count = 29
secondary_C_W_GRV3_block_count = 3
verified_strong_disagreement_count = 0
sign_audit_rows = 1536
positive_functional_delta_rows = 288
stationary_within_tolerance_rows = 1248
negative_functional_delta_rows = 0
runtime_sign = P_G_weakly_increases_and_negative_P_G_weakly_decreases
GRV_C4 = candidate_pending_human_review
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
```

GRV4 supports a bounded agreement result rather than the stronger disagreement
case. Across the 32 GRV3-admitted primary `C` comparisons, the maximum slow
multiplier-set error is about `2.27e-11`, the maximum slow-subspace angle is
about `2.59e-8` radians, and no stability classification changes. The
secondary evolving-conductance diagnostic agrees on 29 rows; the same three
`C-W` rows blocked by GRV3 remain diagnostic-only and are not rescued here.

The sign audit separates the exact semidiscrete identity from finite explicit
steps. Across both tangent signs, two amplitudes, and six timestep multipliers,
the minimum computed functional change is about `-6.39e-15`, inside the frozen
`1e-12` tolerance. Maximum staged-runtime equivalence error is about
`1.78e-15`; the potential and flux identities agree to about `8.89e-16` and
`2.23e-15`. The result therefore uses weak monotonicity, including stationary
equality, and makes no strict-increase claim.

The 16 exact-zero-current boundary rows still receive frozen structural
comparators, but their full-map relation remains blocked by GRV3 coordinate
admission. Agreement on the other rows does not make the analytical comparator
native runtime state, eliminate `W`, identify a joint `C-W` mode, or establish
the full core continuation operator.

### P4.1 Thirty-Point Hardening

- [x] Preserve the P4 result at commit `1c18bda` as preliminary evidence.
- [x] Keep GRV4 unaccepted and create no acceptance anchor.
- [x] Freeze whole-beat clamped-`W` semantics separately from elimination and slaving.
- [x] Freeze `H_P`, restoring `H_cont = -H_P`, `A_W H_cont`, and explicit-map roles.
- [x] Add runtime-potential directional derivatives and finite-difference Hessian/site checks.
- [x] Add canonical, structural, and deterministic mixed directions.
- [x] Add exact frozen-map branch residual and projection/clipping/boundary no-op checks.
- [x] Add conductance authority, duplicate consistency, connectivity, floor, nullity, and conditioning records.
- [x] Add the self-adjoint representative and physical mode/projector mapping rules.
- [x] Reuse the GRV3 state metric with explicit embedding/projection diagnostics.
- [x] Compare complex pairs and near-degenerate modes as real invariant subspaces.
- [x] Exclude deadbeat overwrite modes from slow-subspace disagreement.
- [x] Add finite-difference, residual, conditioning, cluster, and unit-circle uncertainty records.
- [x] Replace spectrum-only symmetry checks with matrix-level conjugacy checks.
- [x] Preserve first-order-local, nonlinear-`J^2`, and no-retention boundaries.
- [x] Commit the complete P4.1 method revision at `69382c8`.
- [x] Execute P4.1 from that clean committed revision and fail closed before artifact emission.
- [x] Record the near-zero relative-conjugacy and near-real invariant-plane representation defects.
- [x] Correct those representations without changing branch scope or scientific thresholds.
- [x] Commit the P4.1a representation correction at `c276fcc`.
- [x] Execute P4.1a from that clean committed revision.
- [x] Record the mechanically passing `c276fcc` run without accepting it.
- [x] Add explicit local comparison identity and mapped-projector records.
- [x] Expand the generated report to expose the hardening controls and bounded result.
- [x] Commit the final artifact-schema/report completion at `01389d9`.
- [x] Execute the final P4.1 full clean rerun.
- [x] Verify all mechanical controls and inspect every branch-level classification.
- [x] Emit a superseding GRV4 result receipt pending human scientific review.
- [ ] Emit a GRV4 acceptance anchor only after that review.

### Final P4.1 Review Candidate

```text
input_execution_revision = 01389d9877bfdf68daa3e31786f832ab17742c86
source_v1_receipt_payload_sha256 = 2554b83c03b89cb7621297af959ef4310836f6944d1f3b7fa9995c96b3b26f6e
source_v1_result_payload_sha256 = 48f9193407772f34f2aefb113f20461312112255ed7381d370d13e85059c993a
corrected_v2_receipt_payload_sha256 = 1e236ed3ee7407125ba166157401712e76ca6337c09990ba0bfc6121c0b96c10
corrected_v2_result_payload_sha256 = 34eabb8e4b65d225943e8cfb0c77db617b7a96a536b6c46edf224e2e818ad7a3
mechanical_status = passed
scientific_acceptance = awaiting_human_review
branches_audited = 48
primary_full_map_comparisons = 32
blocked_full_map_comparisons = 16
primary_no_resolved_difference_within_uncertainty_count = 32
primary_equivalence_supported = false
verified_strong_disagreement_count = 0
sign_audit_rows = 3072
negative_functional_delta_rows = 0
maximum_frozen_map_fixed_point_residual = 1.11609e-11
maximum_H_P_absolute_finite_difference_error = 9.28939e-10
maximum_directional_functional_error = 7.07858e-09
maximum_site_V_second_error = 1.30751e-09
maximum_primary_metric_subspace_angle_radians = 2.10734e-08
primary_unit_circle_uncertainty = 1e-6
secondary_deadbeat_overwrite_modes_excluded = 55
matrix_symmetry_failed_pair_count = 0
reduction_classification = clamped_counterfactual_only
GRV_C4 = candidate_pending_human_review
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
```

All 48 weighted graphs are connected and their reduced mobility is positive
definite. Authoritative branch conductance and duplicate port-edge surfaces
agree exactly. The potential, flux, functional, site derivative, restoring
sign, mobility/Hessian, mapped projector, state-metric, cluster, deadbeat,
uncertainty, and matrix-symmetry controls pass. Thirty-six near-zero `H_P` rows
use the frozen absolute finite-difference gate; the 12 nonzero rows have maximum
relative Hessian error about `8.66e-11`.

The result finds no robust stability-class or clustered slow-subspace
disagreement between the whole-beat clamped-`W` comparator and the admitted full
`C` recurrence in this envelope. All primary modes are marginal within the
frozen `1e-6` uncertainty. This is no resolved difference under the admitted
first-order uncertainty, not equivalence and not proof of algebraic elimination,
fast slaving, geometry-only or mobility-only causation, universal validity,
retention, or the core continuation operator. The 16 frozen rows with more
informative stable/unstable structure still lack an admitted full GRV3 Jacobian.
Finite-amplitude `J^2 -> W` effects remain open.

### P4.1 Artifact-Semantics Correction

- [x] Verify that stability classification consumes the correctly signed frozen
  multiplier and relaxation operator, not the misnamed emitted rate field.
- [x] Rename the emitted evolution-generator eigenvalue field without changing
  its numerical values.
- [x] Replace agreement wording with no-resolved-difference wording.
- [x] Record `primary_equivalence_supported = false`.
- [x] Preserve the 16 blocked full-map comparisons prominently.
- [x] Replace the copied historical prerequisite receipt status with the
  authoritative accepted GRV3 anchor status.
- [x] Bind source v1 payload and receipt hashes in the corrected v2 artifacts.
- [x] Verify that the correction changed no numerical leaf and performed no
  numerical recomputation.
- [x] Record human acceptance of the corrected v2 result in a separate GRV4
  acceptance anchor binding revision `e99a8a3` and receipt `1e236ed3...`.

Verification:

```text
B1_GR_and_GRC9V3_model_tests = 181_passed_122_subtests_passed
repository_wide_suite = 1858_passed_26_failed_1041_subtests_passed
repository_wide_failure_scope = 25_ignored_output_fixture_dependencies_plus_1_unrelated_telemetry_snapshot_digest_mismatch
src_files_changed_by_GRV4 = 0
protected_path_manifest_unchanged = true
```

The repository-wide failures are not promoted to GRV4 failures: the discovery
and cross-family telemetry tests depend on ignored session artifacts absent
from this checkout, and the remaining representative-telemetry digest mismatch
is outside the B1-GR surfaces. They remain visible rather than being repaired or
excluded from the reported run.

## Iteration 6 - GRV5 Preparation, Persistence, And Matched-Probe Mediation

- [x] Record `A-BRANCH`, `A-CLOCK`, `A-PASSIVE`, `A-REACHABLE`, and `A-STATE-CLOSURE` statuses.
- [x] Consume the preregistered present-current convention without outcome-driven redefinition.
- [x] Run direct-conductance preparation.
- [x] Run activity-mediated preparation at the exact first native transport
  stage and through one complete native step.
- [x] Run sign-reversal preparation.
- [x] Stop forming intervention before persistence measurement.
- [x] Evaluate preregistered persistence horizons.
- [x] Project separation onto accepted slow/fast subspaces.
- [x] Run zero-present-probe passive-null control.
- [x] Match `C` and `J` while preserving candidate carrier differences.
- [x] Apply identical native full-step probes.
- [x] Apply identical native immediate-transport-stage probes.
- [x] Apply frozen-`W` probes only as `substrate_reduced` comparators.
- [x] Classify each probe as coherence/potential, old-current injection, or external-current-like analytical input.
- [x] Record the exact readout stage and causal path for each lane.
- [x] Run the complete carrier-by-probe `2x2` design for every candidate read row.
- [x] Record both no-probe baselines, both within-carrier probe increments, and
  the difference-in-differences with its tolerance.
- [x] Route baseline-only differences to ordinary geometry-conditioned recurrence.
- [x] Apply lane-specific claim ceilings to coherence, old-current, and analytical probes.
- [x] Run a preregistered signed amplitude sweep before using susceptibility,
  gain, derivative, or linear-response language.
- [x] Run carrier reset control.
- [x] Run carrier swap control.
- [x] Run equal-carrier control with reached `C` differences preserved.
- [x] Separate reached-state and synthetic-valid evidence.
- [x] Keep off-manifold structurally valid rows below reached or
  constitutively consistent causal claim ceilings.
- [x] Emit a GRV5-specific canonical intervention registry with all required
  field, rebuild, validity, projection, and reachability records.
- [x] Assign `GRR0`-`GRR5` only from complete gates.
- [x] Classify retention, read effect, write effect, and loop closure separately.
- [x] Fill the causal possibility matrix.
- [x] Emit `conductance_retention_probe.json`, `causal_role_matrix.json`,
  `grv5_intervention_registry.json`, `grv5_36_point_review_audit.json`, and
  report.
- [x] Emit and validate the GRV5 result receipt.
- [ ] Record human acceptance in a separate GRV5 acceptance anchor.
- [x] Keep core Read-Back blocked unless directional present-current-conditioned read and passive-null gates pass.

### P5.3 36-Point Acceptance Hardening

This is a revision-distinct confirmatory audit after P5.1/P5.2. It may block or
demote the result, but cannot upgrade the existing rung. The final
machine-readable dispositions live in `outputs/grv5_36_point_review_audit.json`.

- [ ] 01. Freeze carrier hypotheses without retrospective rung promotion.
- [ ] 02. Preserve separate GRV3-admitted and GRV3-blocked claim ceilings.
- [ ] 03. Record preparation boundaries and exact `k=0`/`k=1` semantics.
- [ ] 04. Measure endogenous activity and classify the persistence path.
- [ ] 05. Keep direct experiment-authored `W` below write-back.
- [ ] 06. Separate synthetic old-current input from reached current history.
- [ ] 07. Stage direct `J^2 -> W` and indirect `J -> C -> W` effects.
- [ ] 08. Compare `+J/-J` immediately and after the standardized full step.
- [ ] 09. Run the fixed confirmatory preparation-amplitude ladder.
- [ ] 10. Audit direct-`W` metric symmetry, positivity, and surfaces.
- [ ] 11. Record carrier vectors, correlation, projection, and leakage.
- [ ] 12. Keep the original branch fixed through all horizons.
- [ ] 13. Separate growing displacement from stable retention.
- [ ] 14. Use only accepted slow subspaces and allow no interpreted projection.
- [ ] 15. Preserve transient/deadbeat mediation as its own class.
- [ ] 16. Use fresh unprobed clones for horizons and `2x2` cells.
- [ ] 17. Audit full admitted non-carrier and categorical matching.
- [ ] 18. Prove matching preserves authoritative `W`.
- [ ] 19. Keep `W`-only nulls from rejecting joint/transferred carriers.
- [ ] 20. Keep full-step, immediate-stage, and frozen-`W` lanes separate.
- [ ] 21. Preserve the preregistered present-current convention.
- [ ] 22. Record the full carrier-by-probe `2x2` cells.
- [ ] 23. Compute the oriented interaction vector before norms.
- [ ] 24. Keep zero-probe baseline transport separate from read effect.
- [ ] 25. Record carrier state before and after each probe readout.
- [ ] 26. Record signed fits plus odd/even decomposition.
- [ ] 27. Run wrong-location controls where a multi-edge route exists.
- [ ] 28. Record graded reset/swap/equal/shuffle mediation.
- [ ] 29. Verify authoritative and duplicate conductance surfaces.
- [ ] 30. Separate instantaneous write from retained write.
- [ ] 31. Require one linked chain before loop closure.
- [ ] 32. Freeze separate response/later-write clone policy.
- [ ] 33. Record detection floors and frozen-`W` positive sensitivity.
- [ ] 34. Report all frozen horizons without post-hoc selection.
- [ ] 35. Fail closed on event, topology, stratum, budget, RNG, or positivity debt.
- [ ] 36. Keep core Read-Back below its independent directional gate.

Result:

```text
input_execution_revision = 319b523fcc5be379f3b80afd38251e62b07e4764
mechanical_status = passed
scientific_acceptance = awaiting_human_review
branch_count = 48
preparation_candidate_row_count = 144
GRR0_row_count = 64
GRR1_row_count = 48
GRR2_row_count = 32
GRR3_or_stronger_row_count = 0
activity_stage_write_count = 48
activity_complete_step_joint_write_count = 32
bounded_persistence_count = 32
native_mediation_count = 0
substrate_reduced_sensitivity_count = 96
forming_old_current_amplitude = 141421.35623730952
forming_old_current_input_runtime_reached = false
maximum_local_evidence_ladder_rung = GRR2
GRV_C5_candidate_pending_human_review = true
native_readback_supported = false
writeback_supported = false
closed_loop_supported = false
protected_path_manifest_unchanged = true
```

The 48 direct-`W` rows are authored carrier diagnostics and stop at `GRR0`.
The 48 exact first-transport-stage rows show a sign-even `J^2 -> W` write and
reach `GRR1`, but the conductance separation is overwritten by the next full
step. The forming old-current value is a synthetic experiment input, not a
runtime-reached native history; its magnitude follows from the frozen
`gamma = 1e-12` and the preregistered `0.01` attenuation exponent.

On the 32 nonuniform F2/F3 branches, the transient stage-local write leaves a
complete-step reached, coherence-dominated joint-state displacement. That
separation persists with approximately unit ratio through horizon 10 and
passes snapshot/load plus equal-input replay, supporting bounded `GRR2` joint-
state persistence. The 16 homogeneous F1 branches produce no such complete-
step displacement and remain `GRR0` in this lane.

No candidate occupies an accepted isolated slow cluster, so `GRR3` is blocked.
All native full-step and immediate-stage carrier-by-probe interactions remain
unresolved. The 192 resolved interactions occur only in frozen-`W` reduced
comparators; reset, equal-carrier, swap, zero-probe, replay, event, and topology
controls all pass. Thus the causal matrix closes as 32
`retention_without_read`, 48 `write_before_read`, and 64 ordinary/authored
carrier rows. It does not establish core Read-Back, orientation retention,
write-back, memory, learning, or a closed read/write loop.

Verification:

```text
B1_GR_tests = 68_passed
ruff = passed
required_replay_rows = 432_passed
canonical_intervention_records = 192_complete
candidate_rows_payload_sha256 = 97f1fa6c65554f1fcdde85083654c6643730bb0051a64f9312c9a0f655baa71a
P5_1_to_P5_2_candidate_rows_unchanged = true
conductance_retention_payload_sha256 = 494cfe1cb1d6254519114682bba10dd7634086e614271a2b01b701d81223ed5a
causal_role_matrix_payload_sha256 = 0d09aae9ff0899c1801a304c6f15d54cefce08645f5e9f34ff209e34e7c34340
intervention_registry_payload_sha256 = 2b1bc150d8246279524bfa31df2164b11e131c37a0d038fe0390e6bc1ef5530b
protected_manifest_payload_sha256 = 8374740696b6572effd66326cb72f8e24a95e367debef27c94e5e0b438fa692f
result_receipt_payload_sha256 = 5eaefdc228293ee5f1f1a1ad66c07b0138b6a960d6586044bc7f7035aa45d95a
src_files_changed_by_GRV5 = 0
```

## Iteration 7 - GRV6 Current Recurrence And Return Orbits

- [ ] Record closure, mobility, conservation, uniqueness, and orientation assumption statuses where required.
- [ ] Freeze oriented edge order and node-by-edge incidence convention.
- [ ] Freeze `W_*^-1` as the primary native conductance-compatible edge metric,
  or prove that another primary metric annihilates native potential-flow cycle projection.
- [ ] Preregister minimum conductance, `W_*` and projected-Gram condition limits,
  singularity/rejection thresholds, and a no-silent-regularization policy.
- [ ] Freeze cycle-space and potential-complement projectors, branch/orbit
  metric policy, plus rank and divergence tolerances.
- [ ] Verify projector idempotence, metric orthogonality, and decomposition reconstruction.
- [ ] Verify native weighted potential-flow annihilation under the primary projector.
- [ ] Verify edge-reorientation covariance of incidence, current, metric, and cycle projection.
- [ ] Certify each cycle seed against the declared incidence/orientation convention.
- [ ] Run a stationary divergence-free cycle-current control.
- [ ] Test exact-zero current.
- [ ] Test positive and negative finite current seeds.
- [ ] Test sign-even magnitude-matched preparations.
- [ ] Test cycle-space seeds where topology permits.
- [ ] Record initial cycle content, conductance inscription, reconstructed current, and remaining cycle projection.
- [ ] Search period-two return orbits.
- [ ] Search higher-period and possible complex-unit-circle return behavior.
- [ ] Record complete orbit search space/budget, all seeds and roots,
  rejection/deduplication rules, continuation lineage, selection rule, and
  held-out replay for selected orbits.
- [ ] Require causal-state return and reject all proper divisors in causal coordinates.
- [ ] Require one continuous causal stratum at every intermediate orbit point and derivative probe before assigning Floquet multipliers.
- [ ] Compute the monodromy product only from admitted causal-map derivatives.
- [ ] Record stratum-crossing cycles as hybrid/categorical returns without an ordinary Floquet spectrum.
- [ ] Require causally relevant categorical event-state equality at return.
- [ ] Classify physical-only closure as `physical_projection_return`.
- [ ] Replay every accepted return orbit from snapshots.
- [ ] Classify potential-flow orbit, synchronous transport orbit, undetermined recurrence, or stationary cycle current.
- [ ] Emit `return_orbit_registry.json` and report.
- [ ] Emit and validate the GRV6 result receipt and separate acceptance anchor.
- [ ] Do not relabel recurrent nonzero current as active circulation or Read-Back.

## Iteration 8 - GRV7 Spatial, Temporal, And Continuation Thresholds

- [ ] Select admitted homogeneous and nonuniform branch families.
- [ ] Preregister branch matching, cluster matching, maximum step, and bifurcation restart rules.
- [ ] Preregister parameter sweeps and threshold rules.
- [ ] Sweep `+1`, stable-interior, `-1`, and available complex crossings.
- [ ] Record complete-step multipliers.
- [ ] Record frozen-`W` comparator spectrum.
- [ ] Record row-basis unsigned Hessian.
- [ ] Record signed Hessian.
- [ ] Record WLS comparison Hessian.
- [ ] Record event, sink, basin, collapse, and spark evidence separately.
- [ ] Search for a strong temporal/spatial non-equivalence counterexample.
- [ ] Record bounded correlations without universalizing them.
- [ ] Emit `spatial_temporal_threshold_matrix.json` and report.
- [ ] Emit and validate the GRV7 result receipt and separate acceptance anchor.

## Iteration 9 - GRV8 Classification, Route Decision, And Handoff

- [ ] Assign every required assumption status first.
- [ ] Mark claims with failed/unidentifiable assumptions as not admitted unless independently contradicted.
- [ ] Assign one of the six implementation statuses to every tested object.
- [ ] Assign L0-L5 correspondence levels.
- [ ] Bind claim, debt, assumption, proof-note, and source IDs.
- [ ] State maximum supported and blocked claims for every result.
- [ ] Complete contradiction routing.
- [ ] Complete theory-reopening decision.
- [ ] Decide geometry/mobility separation route.
- [ ] Decide retained-carrier route.
- [ ] Decide oriented-current route.
- [ ] Decide `K` route.
- [ ] Exclude mapping, theory-strength, identifiability, numerical, and source-fidelity explanations before recommending an extension.
- [ ] Produce extension decisions without implementing them.
- [ ] Produce the versioned evidence-grounded successor specification.
- [ ] Preserve Drafts 3.2, 3.3, and 3.4 and the accepted controlling Draft 3.4.1 unchanged.
- [ ] Emit and accept `equivalence_classification.json` with the final scientific classification set.
- [ ] Freeze `evidence_bundle_manifest.json` only after GRV8 scientific acceptance and before successor generation.
- [ ] Exclude the evidence-bundle manifest, successor, and later closeout anchor from the bundle payload.
- [ ] Emit and accept `outputs/gates/grv8_closeout_acceptance_anchor.json`
  before assigning `GRV-C6`.
- [ ] Record predecessor/evidence digests and changed claim/assumption/debt rows.
- [ ] Emit `superseded_exploratory_claims.json`.
- [ ] Complete every theory-to-test traceability row with assumption statuses, result, and route.
- [ ] Freeze the unchanged-GRC evidence bundle.
- [ ] Produce `lgrc_handoff.json` with positive and negative boundaries.
- [ ] Rerun and record the complete existing suite from the GRV8 clean input revision.
- [ ] Verify all protected paths remain unchanged.
- [ ] Emit and validate the GRV8 result receipt and separate acceptance anchor.
- [ ] Assign `GRV-C6` only when classification and routing are complete.
- [ ] Keep B1-L unopened unless its complete entry contract is accepted.

## Final Claim Audit

- [ ] Do not claim full core Read-Back without direct evidence.
- [ ] Do not claim a unique retained projector.
- [ ] Do not combine `alpha`, `gamma`, and `beta` into one spectrum.
- [ ] Do not equate temporal marginality with spark or basin birth.
- [ ] Do not claim active stationary circulation from recurrent transport alone.
- [ ] Do not claim LGRC retention or Read-Back.
- [ ] Do not select N32 through B1-GR bookkeeping.
- [ ] Do not claim memory, learning, agency, organism, or life.
- [ ] Treat a negative, blocked, mixed, or no-extension result as a valid closeout when source-backed.
