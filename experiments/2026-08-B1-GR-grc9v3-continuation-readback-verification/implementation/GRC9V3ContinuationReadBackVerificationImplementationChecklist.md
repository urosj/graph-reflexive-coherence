# B1-GR GRC9V3 Continuation And Read-Back Verification Implementation Checklist

## Current Status

```text
branch = experiment-B1-continuation-readback
status = grv0_preacceptance_corrections_prepared_pending_reexecution
controlling_specification = draft_3_4_1_pre_execution_mathematical_execution_sealed
controlling_specification_sha256 = 7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44
runtime_under_test = unchanged_GRC9V3
runtime_change_authorized = false
src_change_authorized = false
existing_test_change_authorized = false
positive_evidence_opened = false
current_gate = GRV0_preacceptance_bug_fixes_pending_clean_reexecution
verification_closeout_ladder_rung_assigned = false
verification_closeout_ceiling = GRV-C0_specification_package_initialized_execution_not_started
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
- [ ] Record exact graph repository revision.
- [ ] Record exact geometric-theory repository revision.
- [ ] Digest both controlling core papers.
- [ ] Record both paper paths, roles, blob identities where available, and
  SHA-256 digests in `theory_source_manifest.json`.
- [ ] Freeze `protected_path_manifest_v0` for GRC source/spec/test paths.
- [ ] Freeze `experiment_path_manifest.json` and the exact non-self-referential experiment-tree digest scope.
- [ ] Include every discovered load-bearing source in the protected manifest.
- [ ] Record substrate base and experiment execution revisions separately.
- [ ] Verify a clean execution checkout.
- [ ] Run the complete existing test suite in `.venv`.
- [ ] Record test command, environment, duration, pass/fail/skip counts, and logs.
- [ ] Serialize the theory claim ledger.
- [ ] Serialize the theory assumption registry.
- [ ] Serialize the derivation-status appendix.
- [ ] Serialize the theory debt register.
- [ ] Serialize proof-note and traceability records.
- [ ] Serialize the gate dependency map.
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
- [ ] Emit the complete numerical environment record.
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
- [ ] Emit GRV0 JSON artifacts and report.
- [ ] Emit and validate the GRV0 result receipt.
- [ ] Record GRV0 scientific acceptance in a separate accepted anchor before GRV1.
- [ ] Assign `GRV-C1` only if exact baseline and tests are admitted.
- [ ] Keep all scientific evidence flags false.

Stop condition:

```text
dirty_or_failing_baseline or missing_exact_source_identity stops execution
```

## Iteration 2 - GRV1 Instrumentation And Source Fidelity

- [ ] Reproduce the existing two-node transport anchor.
- [ ] Capture and verify complete canonical `step()` order.
- [ ] Verify fixed topology and no-event envelope.
- [ ] Run separate transport-stage and full-step materialized-`K` counterfactuals.
- [ ] Classify direct use, overwrite-before-use, diagnostic status, or unknown; route source mismatch separately.
- [ ] Run physical `J -> -J` controls.
- [ ] Run edge-coordinate reorientation/covariance controls separately.
- [ ] Classify magnitude, axis, orientation, and reconstruction separately.
- [ ] Inventory every excluded or administratively advancing field.
- [ ] Carry causal and unknown excluded fields into GRV3 closure candidates.
- [ ] Validate canonical deep-clone intervention and rebuild behavior.
- [ ] Validate raw snapshot and derived-artifact separation.
- [ ] Validate replay tolerances and canonical serialization.
- [ ] Emit `protected_path_manifest_v1` with only source-base-matching additions,
  or as an explicit unchanged successor when GRV1 discovers no added path.
- [ ] Freeze the post-GRV1 contradiction route for any later protected-path discovery.
- [ ] Emit `instrumentation_validation.json`, `fixture_registry.json`, and report.
- [ ] Emit and validate the GRV1 result receipt and separate acceptance anchor.
- [ ] Assign no branch, continuation, retention, or read-back claim.

## Iteration 3 - GRV2 Strong Formed Branches

- [ ] Certify a homogeneous two-node zero-current branch.
- [ ] Search for a nonuniform two-node branch and certify every accepted result.
- [ ] Search for and classify nonuniform triangle branches and certify every accepted result.
- [ ] Preserve bounded negative search evidence when no nonuniform branch is
  found; do not infer global nonexistence or fail a valid homogeneous result.
- [ ] Run symmetry controls.
- [ ] Run port-relabel controls.
- [ ] Record full-step residuals.
- [ ] Record per-block `C/W/J/Phi/G/identity/budget` internal-stage residuals,
  including budget-correction no-op status.
- [ ] Record pre-continuity, pre-budget, budget-correction, post-budget, and final-refresh states.
- [ ] Require budget correction to be a numerical no-op for an unqualified strong branch.
- [ ] Classify provisional physical strong, projection-supported,
  step-boundary-only, and internally periodic alternatives explicitly.
- [ ] Defer `causal_strong_branch` upgrade until the GRV3 closure audit passes.
- [ ] Verify event and topology assertions.
- [ ] Save, load, and replay every accepted branch.
- [ ] Record solver seeds, tolerance, convergence, and rejected searches.
- [ ] Record the complete search space/budget, all accepted and rejected roots,
  deduplication, continuation lineage, selection rule, and held-out replay for
  each selected branch.
- [ ] Record distance from positivity, conductance-floor, spark, basin/sink, growth, and event boundaries.
- [ ] Emit `fixed_branch_registry.json` and report.
- [ ] Emit and validate the GRV2 result receipt and separate acceptance anchor.
- [ ] State explicitly that branch existence is not continuation or retention.

## Iteration 4 - GRV3 Causal State And Complete Transition Jacobian

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
