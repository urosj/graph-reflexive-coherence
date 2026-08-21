# B1-GR GRC9V3 Continuation And Read-Back Verification Implementation Checklist

## Current Status

```text
branch = experiment-B1-continuation-readback
status = grv3_P3_clean_input_prepared_execution_pending
controlling_specification = draft_3_4_1_pre_execution_mathematical_execution_sealed
controlling_specification_sha256 = 7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44
runtime_under_test = unchanged_GRC9V3
runtime_change_authorized = false
src_change_authorized = false
existing_test_change_authorized = false
positive_evidence_opened = true_bounded_physical_branch_existence_only
current_gate = GRV3_P3_input_freeze
verification_closeout_ladder_rung_assigned = true
verification_closeout_rung = GRV-C3
verification_closeout_ceiling = GRV-C3_accepted
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

- [ ] Freeze and test the branch-relative causal-state encoder and decoder.
- [ ] Require coordinate round trip `E_X(D_X(x)) ~= x`.
- [ ] Require reached-state canonicalization `D_X(E_X(S)) ~causal S`.
- [ ] Require transition commutation `E_X(F(S)) ~= F_X(E_X(S))`.
- [ ] Require preregistered bounded-horizon commutation for every codec horizon.
- [ ] Report bounded-horizon causal closure without promoting it to global Markov sufficiency.
- [ ] Apply exact categorical/identifier equality and block-specific numerical
  tolerances with declared per-horizon accumulated-error bounds.
- [ ] Admit a continuous square causal-state coordinate before eigenanalysis.
- [ ] Represent causally relevant categorical state as a discrete stratum and
  differentiate only within a fixed stratum.
- [ ] Record positive two-sided stratum margins and matching runtime paths for every derivative column.
- [ ] Run matched `C,J` with differing valid `W` through canonical interventions.
- [ ] Run matched `C,W` with differing `J`.
- [ ] Run matched `C,W` with sign-reversed `J`.
- [ ] Compare branch-consistent and perturbed derived surfaces.
- [ ] Separate reachable-history and synthetic-valid pairs.
- [ ] Audit every excluded physical/administrative field for causal relevance.
- [ ] Classify synthetic states as structurally valid, constitutively consistent, and runtime reachable separately.
- [ ] Freeze admitted causal coordinate and zero-sum tangent order.
- [ ] Freeze interior-safe `W`, `J`, and zero-coordinate perturbation policies.
- [ ] Compute the square complete-step causal-transition Jacobian.
- [ ] Compute smooth derived response Jacobians separately.
- [ ] Record categorical/event surfaces as margins and threshold records, not eigensystem rows.
- [ ] Verify relative column, matrix norm, eigenvalue-cluster, and subspace-angle convergence.
- [ ] Record `C/W/J` blocks and residuals.
- [ ] Record left/right eigensystems and conditioning.
- [ ] Identify conservation, gauge, and branch-tangent modes.
- [ ] Apply the preregistered nonnormal evidence mode.
- [ ] Apply the preregistered fast/slow rule where applicable.
- [ ] Classify stable slow, neutral, oscillatory, and unstable clusters.
- [ ] Classify counterfactual sensitivity, constitutive independence,
  runtime-causal independence, and eliminability separately for each candidate block.
- [ ] Enforce distinct structural-validity, constitutive-consistency,
  runtime-reachability, and runtime-causal-independence admission gates.
- [ ] Test bounded C-only and joint C-W reductions.
- [ ] Upgrade only codec- and closure-admitted GRV2 branches to `causal_strong_branch`.
- [ ] Emit `complete_step_jacobians.json`, `slow_cluster_registry.json`, and report.
- [ ] Emit and validate the GRV3 result receipt and separate acceptance anchor.
- [ ] Do not equate a slow joint mode with core retention.

## Iteration 5 - GRV4 Frozen-Conductance Versus Full Recurrence

- [ ] Complete the runtime sign audit.
- [ ] State whether `P_G`, `-P_G`, neither, or only a small-step limit is monotone.
- [ ] Separate analytic semidiscrete sign, runtime-timestep behavior, and timestep sweep.
- [ ] Construct the frozen-`W` constrained comparator outside `src/`.
- [ ] Use the same conserved tangent basis as GRV3.
- [ ] Construct the declared mobility, semidiscrete, and explicit-step comparators.
- [ ] Label analytical comparator objects as non-runtime state.
- [ ] Compare frozen spectra with complete-step multipliers.
- [ ] Compare modes/subspaces and stability classifications.
- [ ] Record every reduction and elimination assumption.
- [ ] Emit `frozen_full_comparison.json` and report.
- [ ] Emit and validate the GRV4 result receipt and separate acceptance anchor.
- [ ] Do not claim the full core continuation operator.

## Iteration 6 - GRV5 Preparation, Persistence, And Matched-Probe Mediation

- [ ] Record `A-BRANCH`, `A-CLOCK`, `A-PASSIVE`, `A-REACHABLE`, and `A-STATE-CLOSURE` statuses.
- [ ] Consume the preregistered present-current convention without outcome-driven redefinition.
- [ ] Run direct-conductance preparation.
- [ ] Run activity-mediated preparation.
- [ ] Run sign-reversal preparation.
- [ ] Stop forming intervention before persistence measurement.
- [ ] Evaluate preregistered persistence horizons.
- [ ] Project separation onto accepted slow/fast subspaces.
- [ ] Run zero-present-probe passive-null control.
- [ ] Match `C` and `J` while preserving candidate carrier differences.
- [ ] Apply identical native full-step probes.
- [ ] Apply identical native immediate-transport-stage probes.
- [ ] Apply frozen-`W` probes only as `substrate_reduced` comparators.
- [ ] Classify each probe as coherence/potential, old-current injection, or external-current-like analytical input.
- [ ] Record the exact readout stage and causal path for each lane.
- [ ] Run the complete carrier-by-probe `2x2` design for every candidate read row.
- [ ] Record both no-probe baselines, both within-carrier probe increments, and
  the difference-in-differences with its tolerance.
- [ ] Route baseline-only differences to ordinary geometry-conditioned recurrence.
- [ ] Apply lane-specific claim ceilings to coherence, old-current, and analytical probes.
- [ ] Run a preregistered signed amplitude sweep before using susceptibility,
  gain, derivative, or linear-response language.
- [ ] Run carrier reset control.
- [ ] Run carrier swap control.
- [ ] Run equal-carrier control with reached `C` differences preserved.
- [ ] Separate reached-state and synthetic-valid evidence.
- [ ] Keep off-manifold structurally valid rows below reached or
  constitutively consistent causal claim ceilings.
- [ ] Assign `GRR0`-`GRR5` only from complete gates.
- [ ] Classify retention, read effect, write effect, and loop closure separately.
- [ ] Fill the causal possibility matrix.
- [ ] Emit `conductance_retention_probe.json`, `causal_role_matrix.json`, and report.
- [ ] Emit and validate the GRV5 result receipt and separate acceptance anchor.
- [ ] Keep core Read-Back blocked unless directional present-current-conditioned read and passive-null gates pass.

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
