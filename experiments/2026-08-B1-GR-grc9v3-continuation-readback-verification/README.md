# B1-GR - GRC9V3 Continuation And Read-Back Verification

B1-GR is a foundational theory-to-substrate verification experiment over the
unchanged `GRC9V3` runtime. It is inside the repository experiment discipline,
but outside the N-series agency/catalog sequence.

The experiment is grounded in the two controlling core papers:

- *The Continuation Spectrum*;
- *Read-Back*.

Its job is not to implement those papers. Its job is to determine what the
current synchronous graph substrate realizes exactly, in a declared reduction,
only analogically, as a measurable diagnostic, or not at all.

## Experiment State

```text
experiment_id = B1-GR
status = grv6_P6_1_mechanically_passed_awaiting_human_review
specification_state = draft_3_4_1_pre_execution_mathematical_execution_sealed
controlling_specification_sha256 = 7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44
runtime_under_test = unchanged_GRC9V3
runtime_change_authorized = false
src_change_authorized = false
existing_test_change_authorized = false
positive_continuation_evidence_opened = false
positive_retention_evidence_opened = bounded_GRR2_neutral_coordinate_persistence_only
positive_readback_evidence_opened = false
positive_writeback_evidence_opened = false
verification_closeout_rung = GRV-C4
verification_closeout_ceiling = GRV-C5_blocked_pending_GRV6_acceptance_and_GRV7
B1_L_execution_authorized = false
N32_selected = false
l04_selected = false
```

The digest above is the SHA-256 of the controlling specification committed in
the documentation scaffold. GRV0 must reproduce it from the clean `P0` input
revision; changing the specification requires protocol readmission.

The first unaccepted GRV0 result revision (`05fc8f6`) exposed one packaging
omission: `baseline_manifest.json` carried the correct specification digest but
not the separately required `specification_id`. The correction is classified
as `bug_fix_preserving_protocol`; it changes no fixture, threshold, method,
runtime, theory contract, or claim envelope. The original result remains in
history and is superseded by replacement result revision `97a9a6b`, generated
from clean P0.2 input revision `5f92973`.

The first replacement attempt from `431dcf8` then failed closed before receipt
emission because the orchestrator included the existing unaccepted receipt in
the replacement receipt's output-artifact set. P0.2 excludes the exact receipt
target from its own digest enumeration and adds a rerun regression test. This
is also packaging-only: no partial P0.1 result was admitted. The complete P0.2
rerun passed mechanically with receipt digest `a583d763b2d5e72af3f3e2ad5401aca8c143eff1aa73427404c2f8286e1ed9df`.
GRV0 scientific acceptance is recorded separately in anchor commit `454b2c5`.
Iteration 1 is closed at GRV-C1; this does not open scientific continuation,
retention, read-back, or write-back evidence.

GRV1 then executed from clean committed P1 revision `cbe52fe`. Its mechanical
source-fidelity checks pass, and result receipt
`c8f51f4cc1f816726aa65d56e9165809ba54a5d47f4259e4e3f3318712f5b1bf`
binds the generated artifacts to that input revision and the accepted GRV0
anchor. GRV1 remains at a `GRV-C2` candidate ceiling until a separate
authorized human acceptance anchor is recorded. It opens no branch,
continuation, retention, read-back, or write-back evidence.

Before acceptance, source-fidelity review identified additional controls needed
to make later stage-local interpretation safer. The unaccepted GRV1 candidate
at `45435c8` is therefore superseded, not rejected, by a P1.1 instrumentation
strengthening. P1.1 preserves the sealed specification and claim ceiling while
adding observation noninterference, clone isolation, W/J/K authority mapping,
valid multi-amplitude K interventions, stagewise sign attribution, public-stage
and fresh-process replay, and explicit transition-environment/RNG accounting.
The strengthened rerun from clean input revision `416f49e` passes mechanically.
Receipt `9535c80100c6813b69a327cfa80f0180f2288ee7e87e6e550c3168261353855a`
binds the new authority map and instrumentation artifacts and explicitly
supersedes the earlier unaccepted receipt. That receipt remained a `GRV-C2`
candidate until the separate acceptance below.

The strengthened GRV1 result is accepted by the experiment owner in separate
anchor commit `bc12787`. Iteration 2 is therefore closed at `GRV-C2`, still
without branch, continuation, retention, read-back, or write-back evidence.
GRV2 is prepared as the first gate eligible to produce a source-current formed-
branch candidate; its output remains provisional until separately accepted.

The first GRV2 execution from P2 commit `5bf082d` failed closed before receipt
emission. A triangle snapshot reload re-canonicalized one closing-edge current
whose theoretical branch value is zero; the observed load delta was about
`3.22e-11`, below the already frozen `J` tolerance of `1e-10`, but the P2
replay check had incorrectly required exact numeric equality. P2.1 applies the
accepted per-block tolerances while continuing to report raw representation
normalization separately. No partial snapshot is evidence, and the complete
gate must be rerun from clean committed input.

The P2.1 rerun from `050639a` passed the first triangle rows but failed closed on
a more asymmetric row. That exposed the underlying experiment-builder defect:
the undirected closing edge retained topology endpoint order `2 -> 0` while the
runtime current coordinate had already been canonicalized to `0 -> 2`. P2.2
canonicalizes the topology endpoint and `PortEdge` orientation together, as
required by the frozen orientation convention. The graph, parameter grid,
thresholds, runtime, and claim ceiling are unchanged; all partial outputs remain
unadmitted and a complete clean rerun is required.

The complete GRV2 rerun from clean P2.2 input revision `d224a10` passes
mechanically. It executes all 144 preregistered rows and retains 48 provisional
physical strong-branch candidates: 16 homogeneous F1 rows, 16 nonuniform F2
rows at site-potential scale `1.0`, and 16 nonuniform F3 rows at scale `1.5`.
The other 96 nonuniform-search rows converge only to homogeneous roots and are
rejected from the nonuniform target; this is bounded search evidence, not a
global nonexistence result. All accepted candidates pass internal-stage,
budget, event/topology, save/load, symmetry/port, and held-out replay controls.
Receipt `967f1adc5d8b36c2cdf0fb5c0153ac43b37e14f5fd6c0f1bcb76d92f38f43c94`
binds the result to P2.2 and the accepted GRV1 anchor.

GRV2 therefore reaches only a `GRV-C3` candidate ceiling pending separate
scientific acceptance. The branches remain
`provisional_physical_strong_branch`; the zero-current identity boundary and
excluded causal fields keep `causal_strong_branch` deferred to GRV3. Branch
existence does not establish continuation, retention, read-back, or write-back.

Before acceptance, adversarial review identified three controls that P2.2 made
implicit rather than machine-visible: raw-candidate to canonical load-bearing
state deltas, budget active-set/clipping status, and physical stationarity over
several unperturbed beats while administrative phase advances. The P2.2 result
at `d150a07` is therefore never accepted and is superseded by P2.3 hardening.
P2.3 preserves the sealed search grid, solver, fixtures, runtime, thresholds,
and claim ceiling. It adds a four-beat physical hold, explicit authoritative
`W/J` admission, continuity/budget diagnostics, and symmetry-orbit
nonindependence accounting. Cache refresh and complete causal-state closure
remain GRV3 debt. A full gate rerun from a clean committed P2.3 input was
therefore required before GRV2 could be reviewed for acceptance.

The complete P2.3 rerun from clean input revision `228e1d4` passes. It preserves
the 144-row search result: 48 provisional branch rows and 96 bounded
nonuniform-search rejections. The 48 rows occupy 32 canonical symmetry orbits;
the row count is not an independent-branch count. Every retained row passes
canonical load-bearing-state admission, authoritative `W/J` checks, continuity
and budget active-set controls, save/load replay, and the four-beat physical
hold. Across 192 hold beats, the maximum cumulative physical `L_inf` residual
is about `6.54e-10`, below the declared `1e-9` numerical branch limit. All
non-cache excluded state stays exact; cache refresh occurs on every row and
remains explicit GRV3 causal-closure debt. Receipt
`73450d2a445770fc3f4b0f2871d3d10c865e097fdd305d97945e41dd7b707c63`
binds the superseding result to P2.3. GRV2 remains a `GRV-C3` candidate pending
separate scientific acceptance.

The experiment owner accepts the bounded P2.3 result in a separate GRV2 anchor
at the next commit. GRV2 is therefore closed at `GRV-C3`: source-current
physical formed-branch existence is accepted under the declared envelope.
`causal_strong_branch`, stability, continuation, retention, read-back, and
write-back remain unopened. GRV3 is next and must begin with causal-state and
stratum admission over all 48 accepted rows before any Jacobian or spectrum is
interpreted.

The clean GRV3 P3 input now freezes that scope explicitly. All 48 rows will be
audited; symmetry orbits are interpretation metadata only. GRV3-A tests the
branch-relative causal codec first. GRV3-B/C can emit a classical derivative,
response matrix, or spectrum only where every two-sided perturbation remains
inside one declared causal stratum. The known zero-current sink/basin boundary
may therefore admit causal closure while blocking ordinary Jacobians, which is
a valid bounded result rather than a GRV2 failure.

The final GRV3 P3.3 rerun from clean input revision `0a323d2` passes
mechanically and remains pending human scientific review. All 48 accepted GRV2
rows pass bounded `(C,W,J)` codec closure through horizons 1, 2, 5, and 10, but
no full `(C,W,J)` classical Jacobian is admitted because every full chart meets
a non-smooth current/sink/basin stratum boundary. The two preregistered reduced
charts produce 64 square matrices across 32 rows and 16 symmetry orbits. All 64
pass response convergence and finite-horizon nonnormal control; 61 pass the
complete temporal interpretation gate. The three blocked interpretations are
the `C-W` candidates on `grv2-f3-036`, `grv2-f3-037`, and `grv2-f3-041`:
the first changes fast-subspace dimension across the step sweep, while the last
two also fail the frozen eigenvector-condition and full-cluster fallback gates.
Their separately preregistered `C` candidates pass, so all 32 reduced-coordinate
rows retain at least one bounded temporal candidate. No primary reduced chart
is selected after seeing the spectra.

Receipt `7cf749fa8a46f6b219a27515504e4ad671a386144b2ef8626fb14e63a4fb104d`
binds the result to P3.3. GRV3 supports at most bounded causal-state,
reduced-transition, temporal-cluster, and response candidates pending review.
Individual eigenvectors remain blocked where conditioning fails; fast/slow
current slaving is `not_applicable` because no separate current-relaxation
sector or two finite decaying clusters were identified. Stability,
continuation, retention, read-back, write-back, and `GRV-C4` remain unsupported;
GRV4 is still required for the frozen/full comparison.

Adversarial review keeps that P3.3 result unaccepted and supersedes it with a
frozen P3.4 hardening pass. The earlier result reset omitted causal state while
testing encoded iteration and did not machine-gate derivative invariance across
`step_index`, per-subfield cache omission, decoder correction, RNG consumption,
branch residual relative to `h`, odd versus even `J` response, declared block
normalization, alternate-basis covariance, or symmetry conjugacy. P3.4 adds
those checks without changing `src/`, GRV2 branches, fixtures, finite-difference
steps, spectral thresholds, or the claim ceiling. Until its clean rerun is
reviewed, P3.3 remains preliminary evidence and GRV4 is blocked.

The report-complete P3.4.1 rerun from clean revision `b1c233b` passes
mechanically. All 48 branches pass bounded causal closure and per-subfield
omitted-state decomposition. All 64 reduced matrices pass derivative-level
administrative-phase invariance and alternate-basis covariance, and all 32
declared multirow symmetry comparisons pass. Decoder correction, RNG
consumption equality, and branch-residual-to-step separation pass for every
derivative attempt. The 61 previously interpretable reduced matrices remain
interpretable; the same three `C-W` candidates remain blocked by frozen
spectral/conditioning gates, while their separately frozen `C` candidates pass.

Receipt `83a2650f57fe3d1a814155bf6e8621881d01468b36cde0f1b460af02339b92cc`
binds the current result. No full `(C,W,J)` classical derivative, joint `C-W`
mode claim, global cache eliminability, continuation, retention, read-back, or
write-back is supported. The complete-beat odd/even `J` response is unresolved
and does not negate the GRV1 stage-local `J^2` path. The experiment owner
accepted this bounded GRV3 result at revision `0dedbf9`. The acceptance does
not upgrade any blocked full-state, stability, continuation, retention,
read-back, or write-back interpretation. GRV4 is now authorized and remains
required before `GRV-C4` can be considered.

GRV4 P4 freezes the next comparison without changing `src/`. Every accepted
branch receives a fixed-`W` structural comparator in the same conserved tangent
basis used by GRV3. The primary relation to complete recurrence is evaluated
only on the 32 branches whose `C` transition matrix GRV3 admitted; the 16
zero-current categorical-boundary rows remain explicit blocked comparisons.
The sign audit separates the semidiscrete identity, staged runtime behavior at
the native timestep, and a preregistered timestep/amplitude sweep. Its staged
path calls the existing potential, flux, and continuity implementations while
holding `W` fixed, so it is a declared reduction rather than an alternative
native `step()`.

The clean GRV4 run from P4 revision `e21ec2c` passed its original mechanical
checks and emitted 48
standalone fixed-`W` comparators and the preregistered 32 primary full-map
comparisons. All 32 agree in stability class, slow multiplier set, and slow
subspace within the frozen thresholds; no strong disagreement is supported.
The maximum primary slow-multiplier error is about `2.27e-11`, and the maximum
primary slow-subspace angle is about `2.59e-8` radians. The secondary `C-W`
diagnostic agrees on 29 rows and preserves the three GRV3 temporal blocks.

The 1,536-row sign matrix has 288 positive and 1,248 stationary-within-tolerance
functional changes, with no negative row beyond the `1e-12` tolerance. Its
maximum staged-runtime equivalence error is about `1.78e-15`. This supports the
weak sign classification only for the declared fixed-`W` reduction. Receipt
`46420b14840bda5258d415463e7376bbc929557a907055b10f4d2fb23b4fc3fc`
binds that preliminary result. A subsequent thirty-point operator review found
that its metric, cluster, uncertainty, restoring-sign, mode-mapping, mobility,
and matrix-symmetry controls were not sufficient for acceptance. No GRV4
acceptance anchor was created. P4.1 therefore preserves commit `1c18bda` as
useful unaccepted evidence and requires a full clean rerun with `H_cont=-H_P`,
`A_W H_cont` temporal rates, GRV3-metric embeddings, real invariant clusters,
deadbeat exclusion, uncertainty-aware decisions, and matrix-level symmetry
conjugacy. Until that result is reviewed, `GRV-C4` is not assigned; no
continuation, retention, read-back, write-back, joint `C-W`, or `W`
eliminability claim is opened.

The superseding P4.1 execution from revision `01389d9` passes all hardened
mechanical controls. It preserves the 48/32/16 preregistered scope. All 32
admitted primary rows show no resolved difference under the GRV3 block metric,
real invariant-cluster comparison, deadbeat exclusion, and a `1e-6`
unit-circle uncertainty. This is not an equivalence result: all admitted
primary modes are marginal within that uncertainty, while the more informative
frozen stable/unstable cases are among the 16 rows whose full GRV3 Jacobians
remain blocked. All 48 clamps are fixed within `1.12e-11`; matrix-level
symmetry covariance has no failed pair.

A post-run schema-only correction renamed the eigenvalues of
`-A_W H_cont = A_W H_P` as semidiscrete **generator** eigenvalues, replaced
the ambiguous agreement wording, and made the accepted GRV3 anchor
authoritative over its historical pre-acceptance receipt status. It performed
no numerical recomputation and changed no classifier. Corrected result payload
`34eabb8e4b65d225943e8cfb0c77db617b7a96a536b6c46edf224e2e818ad7a3`
and receipt `1e236ed3ee7407125ba166157401712e76ca6337c09990ba0bfc6121c0b96c10`
supersede the reviewed v1 schema while retaining its hashes in provenance.
The corrected bounded result is accepted at revision `e99a8a3` by
`outputs/gates/grv4_acceptance_anchor.json`, assigning `GRV-C4` without opening
equivalence, continuation, retention, read-back, or write-back. GRV5 is now
authorized.

GRV5 then executed through P5.4 from clean method revision `83c2cbc`; committed
result revision `317092e` and receipt `a42ccda9...` bind the 144-row preparation,
persistence, and matched-probe matrix. The accepted ceiling is `GRR2`: 32
nonuniform rows retain a C-dominated neutral-direction displacement after the
synthetic forming intervention stops. Branch relocation remains unresolved
because GRV3 did not separately identify a branch tangent. The native
stage-local `W` write is not identified as the specific mediator of later `C`,
and the unchanged-runtime successor is not shown reachable from an accepted
branch without the synthetic intervention. Native read-back, write-back,
`GRR3+`, and closed-loop claims remain blocked.

The experiment owner accepted that bounded result in
`outputs/gates/grv5_acceptance_anchor.json`. This authorized GRV6 but did not
assign `GRV-C5`, which also requires accepted GRV6 and GRV7 threshold evidence.

The preliminary GRV6 result executed mechanically from clean revision
`69f1a11`. All 48
certified branches receive exact-zero and signed finite-current controls; all
16 triangle branches receive both orientations of a certified divergence-free
cycle seed. None of the 32 cycle seeds persists after native potential-flow
reconstruction, with maximum post-step cycle component
`1.3498100806892346e-26`. Conservation closes to
`1.7763568394002505e-15`, and topology/event controls remain clean.

The bounded period-`2,3,4,5,6,8` search executes all 1,536 preregistered rows.
Of 671 converged numerical candidates, 670 are rejected as period-one or other
proper-divisor closures and one misses the return tolerance. The other 865
rows are blocked by an ill-conditioned return Jacobian under the frozen
no-silent-regularization rule and remain unresolved; they are not negative
orbit evidence. No primitive causal-state orbit, physical-only return,
hybrid/categorical return, or ordinary Floquet spectrum is admitted. This is a
bounded negative recurrence result, not a global nonexistence result.

Its result receipt is `2d266835...` and remains superseded for acceptance. A
subsequent 36-point review preserved its bounded orbit-search accounting but
required stronger current-control evidence before acceptance. P6.1 now freezes
projector condition records, full cycle-seed certification, divergence and
fixed/phase-local projections, public-method stage traces, four-level signed
activity ladders, constraint-support checks, and machine-level exact-zero
symmetry classifications.

Orbit-only requirements such as full phase/symmetry deduplication,
relative-periodic classification, cycle-averaged pumping, per-phase codec
revalidation, dependency resets, fresh-process candidate replay, and extended
Floquet controls were not executed because no orbit was admitted. They remain
explicit positive-candidate gates rather than being marked passed.

The superseding P6.1 execution completed from clean method revision `50aa178`.
Its scientific counts are unchanged from the preliminary result, while the
stronger current controls add 256 signed amplitude-ladder rows, 16 exact native
stage-trace pairs, scale-aware full seed certification, and explicit symmetric
versus nonsymmetric exact-zero classification. The external-review audit
accounts for all 36 points with 20 direct passes, 14 positive-orbit-conditional
gates, one bounded-scope disposition, one current-pass/orbit-conditional
disposition, and zero current-result acceptance blockers. Its receipt is
`f9c89506...` and remains `awaiting_scientific_review`; no GRV6 acceptance
anchor exists, `GRV-C5` is not assigned, and GRV7 remains blocked. Active
circulation, Read-Back, write-back, and self-sustaining identity remain
unopened.

## Central Question

```text
What do the current GRC9V3 equations and complete synchronous runtime actually
realize from continuation, temporal persistence, retention, read-back, and
write-back; which correspondences are reduced, analogical, diagnostic, absent,
or theory-open; and what next route is justified by unchanged-runtime evidence?
```

## Required Distinctions

B1-GR must keep these objects separate throughout execution:

```text
continuation stiffness alpha
temporal relaxation gamma
read-back gain beta

retention
read effect
write effect
closed read/write loop

spatial Hessian
frozen-conductance comparator
complete transition Jacobian

temporal marginality
continuation marginality
spark / basin birth
collapse
```

Branch existence, a slow observable, persistent conductance, nonzero current,
or a useful diagnostic cannot by itself establish Read-Back.

## Serial Gate Order

```text
GRV0 baseline admission
  -> GRV1 instrumentation and source fidelity
  -> GRV2 strong formed branches
  -> GRV3 causal state and complete transition Jacobian
  -> GRV4 frozen-conductance versus full recurrence
  -> GRV5 conductance preparation, persistence, and mediation
  -> GRV6 current recurrence and return orbits
  -> GRV7 spatial versus temporal/continuation thresholds
  -> GRV8 claim classification and route decision
```

The gates are serial. A blocked prerequisite limits or stops dependent work;
later iterations cannot repair an earlier missing source identity by relabeling
or interpretation.

## Claim Boundary

B1-GR may establish bounded causal arrows and implementation correspondence
levels for unchanged `GRC9V3`. It may end with a positive, negative, blocked,
mixed, or theory-reopening result.

It does not initially authorize:

```text
new GRC runtime behavior
new read-back state or current
LGRC execution
N32 selection
unique retained projector
unified alpha/gamma/beta spectrum
memory, learning, agency, organism, or life claims
```

Only GRV8 may recommend a revision-distinct selectable GRC extension, an
analysis-only route, theory reopening, no extension, or the deferred B1-L
investigation.

## B1-L Relationship

[B1-L](../2026-08-B1-L-lgrc9v3-continuation-readback-delta/README.md) is a
deferred downstream experiment identity only. It originates in Part III of the
B1-GR specification and cannot begin before accepted `GRV-C6` evidence and an
accepted `lgrc_handoff.json`.

## Documents

- [Controlling verification specification](implementation/GRC9V3ContinuationReadBackVerificationSpecification.md)
- [Preserved Draft 3.2 intake](implementation/GRC9V3ContinuationReadBackVerificationSpecification_Draft3_2.md)
- [Preserved Draft 3.3 implementation-hardening revision](implementation/GRC9V3ContinuationReadBackVerificationSpecification_Draft3_3.md)
- [Preserved Draft 3.4 identification/lifecycle revision](implementation/GRC9V3ContinuationReadBackVerificationSpecification_Draft3_4.md)
- [Implementation plan](implementation/GRC9V3ContinuationReadBackVerificationImplementationPlan.md)
- [Implementation checklist](implementation/GRC9V3ContinuationReadBackVerificationImplementationChecklist.md)
