# B1-GR GRC9V3 Continuation And Read-Back Verification Implementation Plan

## Purpose

Execute the accepted B1-GR verification specification against unchanged
`GRC9V3` and produce a decision-grade account of the substrate's relation to
*The Continuation Spectrum* and *Read-Back*.

This plan implements the **verification experiment**, not the theoretical
papers and not a new runtime mechanism. Experiment-local fixtures, numerical
operators, counterfactual interventions, reports, and machine artifacts are
allowed. Changes to `src/`, existing tests, runtime semantics, or protected
specifications are not.

## Controlling Authority

The controlling source order is:

1. *The Continuation Spectrum* and *Read-Back* for theory claims and open
   boundaries;
2. the B1-GR verification specification for assumptions, gates, evidence
   contracts, and claim ceilings;
3. current GRC specifications, source, and tests for executed substrate
   semantics;
4. B1-GR artifacts for experiment evidence.

The implementation plan and checklist organize execution. They are not
evidence and cannot strengthen a claim from the controlling specification.

```text
controlling_specification_id = b1_grc9v3_continuation_readback_verification_v3_4_1
controlling_specification_sha256 = 7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44
```

The clean `P0` input must reproduce this digest. A different digest is a
protocol-readmission event, not an implementation-only correction.

## Experiment Boundary

```text
allowed:
  experiment-local configs and fixtures
  calls through existing public/runtime surfaces
  exact snapshot and replay
  branch search and branch certification
  complete-step numerical differentiation
  experiment-local reduced/comparison operators
  counterfactual state clones and interventions
  JSON/Markdown evidence generation

blocked:
  src changes
  existing-test changes
  hidden monkey patches or replacement runtime methods
  new constitutive state or telemetry in GRC9V3
  post-outcome threshold selection
  LGRC execution
  N32 selection
  runtime extension implementation
```

## Baseline And Revision Identity

GRV0 must freeze two identities separately:

```text
substrate_base_revision:
  exact revision whose protected GRC source/spec/test tree is under test

experiment_execution_revision:
  exact revision containing accepted B1-GR experiment code and governance
```

The input revision must be clean when a gate is run. The protected
runtime/spec/test path manifest must remain byte-identical to the admitted
substrate base throughout B1-GR. Generated evidence must never be used to hide
an unrelated worktree diff.

The exact controlling theory revision and SHA-256 digests of both core papers
must also be frozen before scientific execution.

## Evidence And Artifact Policy

Every scientific artifact should be deterministic or record why a numerical
search is only reproducible within a declared tolerance. Machine artifacts use
canonical JSON and repository-relative paths.

Every positive or negative row records at least:

```text
claim_ids
provenance_label
assumption_ids_and_statuses
fixture_and_branch_ids
source_revision_and_artifact_digests
method_and_preregistered_thresholds
observed_result
implementation_status
correspondence_level
maximum_supported_claim
blocked_claims
debt_ids
decision_route
```

Raw runtime snapshots remain distinct from derived matrices and reports.
Experiment-local analytical objects must be labeled `substrate_reduced`,
`substrate_analogical`, or `measurable_not_constitutive` as appropriate; their
presence in an output file does not make them runtime state.

Machine artifacts use a semantic `payload` plus `payload_sha256`; volatile
metadata is excluded from that digest. Each artifact declares whether it is
byte-reproducible, tolerance-reproducible, or search-reproducible with a fixed
seed and budget.

Changes between clean gate-input revisions are classified before execution as:

```text
mechanical_frozen_protocol_implementation
bug_fix_preserving_protocol
scientific_method_change
threshold_or_config_change
fixture_change
claim_envelope_change
```

Only the first two may proceed without protocol readmission. The remaining
classes require a preregistration amendment or contradiction route before
evidence generation; a clean commit alone does not authorize method drift.

## Executable Package Contract

GRV0 instantiates the normative package from the controlling specification.
The six `hypotheses/` documents are human-readable projections of the claim,
assumption, derivation, debt, traceability, and gate records; they do not open
positive hypotheses.

The named script-to-gate map is:

| Gate | Primary scripts |
|---|---|
| GRV0 | `serialize_theory_contract.py`, `capture_repository_baseline.py`, `artifact_io.py`, `gate_receipts.py` |
| GRV1 | `validate_instrumentation.py`, `interventions.py` |
| GRV2 | `solve_strong_fixed_branches.py` |
| GRV3 | `compute_complete_step_jacobian.py`, `state_codec.py`, `tangent_basis.py`, `numerical_convergence.py`, `interventions.py` |
| GRV4 | `compare_frozen_and_full_dynamics.py` |
| GRV5 | `run_preparation_persistence_probe.py`, `interventions.py` |
| GRV6 | `search_return_orbits.py`, `grv6_methods.py`, `branch_continuation.py`, `edge_space.py` |
| GRV7 | `sweep_temporal_and_spatial_thresholds.py`, `branch_continuation.py` |
| GRV8 | `classify_claims_and_extensions.py`, `route_contradictions_and_theory_reopening.py`, `build_lgrc_handoff.py` |
| orchestration | `run_all.py` |

Experiment-local schemas validate common artifacts, result receipts,
acceptance anchors, baseline manifests, branch registries, complete-step
Jacobians, interventions, assumption status, return-orbit/cycle decomposition,
the evidence bundle, and the LGRC handoff. Dedicated schemas or named common
definitions also cover every manifest and final decision record named by the
controlling specification. The package must materialize those schemas rather
than leaving them implicit in prose. Experiment-local tests cover canonical
JSON, schemas, state cloning, state-codec faithfulness, tangent bases,
intervention rebuild order, gate dependencies, receipt/anchor separation,
edge-space/projector algebra, and numerical convergence.
`test_edge_space.py` is the required GRV6 algebra/covariance test surface.
`test_spec_propagation.py` must verify that the committed README, plan, and
checklist identify Draft 3.4.1, reference the computed controlling-specification
digest through the P0 manifest, contain current gate/artifact names, and include
every required GRV0 admission item.

The numerical environment policy records the exact Python executable, direct
analysis dependencies, BLAS/LAPACK provider, thread controls, hash seed,
locale, and floating-point information. Analysis dependencies are pinned in an
experiment-local requirements file only when needed; runtime project
dependencies remain unchanged.

## Gate Dependency And Stopping Rules

The GRV gates execute in order. Each iteration consumes an accepted prerequisite
anchor, its result-receipt digest, and its output digests.

The documentation scaffold is committed before execution. GRV0 preparation
then materializes the named package surfaces in a separate clean revision `P0`;
GRV0 executes only after `P0` is committed. Later gate-local implementation
changes likewise become clean input revisions before the affected gate runs.
Gate execution writes evidence and reports, never uncommitted code.

```text
clean accepted input revision
  -> execute one gate
  -> validate artifacts and protected paths
  -> write candidate result receipt
  -> commit result artifacts as R_n
  -> perform declared scientific review
  -> write acceptance anchor for R_n
  -> freeze the anchor as A_n
  -> next gate consumes A_n
```

The result receipt excludes itself from its payload digest and never embeds the
future SHA of its own commit. It records prerequisite result-receipt digests and
accepted anchor digests/references separately; only the anchors authorize
progression. The acceptance anchor records its preregistered human authority,
review method, result revision, receipt digest, status, and immutable reference.
`run_all.py` refuses to cross a missing, rejected, blocked, or superseded
acceptance anchor. It may perform mechanical validation but cannot decide
scientific acceptance.

Every result receipt is bound to the substrate base revision, accepted
protected-manifest digest, clean experiment input revision/tree digest, and
accepted prerequisite anchors. If a revision-distinct baseline is admitted,
the transitive dependency graph marks every result/anchor derived from the old
baseline `superseded` or `blocked` until rerun; artifact existence does not
preserve acceptance.

The generic `positive_evidence_opened` flag remains false through GRV1. It may
become true only when GRV2 or a later gate accepts a source-current scientific
row. Role-specific continuation, retention, read, write, and recurrence flags
remain independent.

```text
GRV0 failure:
  stop all scientific execution

GRV1 source-fidelity failure:
  stop dependent runtime interpretation until instrumentation is corrected

GRV2 missing branch family:
  block only analyses requiring that family; preserve bounded negative result

GRV3 nonidentifiable causal state or unconverged Jacobian:
  block dependent spectral and mediation claims

GRV4 sign/comparator failure:
  block structural-continuation correspondence, not full-map observations

GRV5 missing retention/read/write arrow:
  classify arrows separately; do not erase independent arrows

GRV6 no recurrent orbit:
  valid negative result; do not manufacture circulation

GRV7 non-equivalence:
  valid evidence against threshold relabeling

GRV8:
  only gate permitted to assign final route; GRV-C6 requires the separate
  GRV8 closeout acceptance anchor
```

## Iteration 1 - GRV0 Specification And Baseline Admission

### Objective

Make the theory, source, assumption, gate, and repository identities executable
without opening scientific evidence.

### Work

1. Confirm Draft 3.4.1 as the accepted controlling specification while
   preserving Drafts 3.2, 3.3, and 3.4 unchanged.
2. Materialize the named package surfaces, complete GRV0 executables/tests,
   and commit the clean package-preparation revision `P0` before execution.
3. Record exact graph, experiment-input, and theory revisions.
4. Digest controlling papers in `theory_source_manifest.json` and emit
   `protected_path_manifest_v0` for the
   protected GRC source/spec/test paths at the exact substrate base revision.
5. Run the complete existing test suite in `.venv` and preserve its command,
   environment, duration, pass/fail/skip counts, and logs.
6. Serialize the theory claim ledger, assumption registry, derivation-status
   appendix, debt register, proof-note registry, gate dependency map, and
   theory-to-test traceability matrix.
7. Freeze contradiction, theory-reopening, manifest, decision, result-receipt,
   acceptance-anchor, and evidence-bundle schema coverage.
8. Materialize the normative `hypotheses/` views and all named package surfaces.
9. Preregister acceptance authority/review rules, the present-current
   convention, nonnormal diagnostic/threshold, and applicable fast/slow
   measure/threshold.
10. Freeze the complete fixed-topology envelope and verify every
    specification-name to runtime-parameter mapping.
11. Freeze zero-sum tangent bases, ambient coordinate identification, and
    branch-dependent metric transport.
12. Freeze block-specific causal-equivalence semantics: exact categorical and
    identifier equality; absolute/relative `C/W/J` tolerances; RNG treatment;
    administrative advancement; duplicate-surface reconciliation; and
    per-horizon accumulated-error rules.
13. Freeze the gate-input revision-change classification and readmission rules.
14. Freeze numerical dependencies, execution environment, thread controls, and
    semantic artifact digest policy.
15. Freeze `experiment_path_manifest.json` and the non-self-referential scope
    of `experiment_tree_sha256`.
16. Run `test_spec_propagation.py` against the current specification digest,
    README, plan, checklist, gate names, artifacts, and GRV0 admission items.
17. Verify no `src/` or existing-test diff.
18. Keep all generic and role-specific positive-evidence flags false.

### Required outputs

```text
outputs/theory_claim_ledger.json
outputs/theory_assumption_registry.json
outputs/theory_derivation_status.json
outputs/theory_debt_register.json
outputs/theory_test_traceability.json
outputs/gate_dependency_map.json
outputs/baseline_manifest.json
outputs/protected_path_manifest_v0.json
outputs/experiment_path_manifest.json
outputs/theory_source_manifest.json
outputs/numerical_environment.json
outputs/contradiction_register.json
outputs/gates/grv0_result_receipt.json
outputs/gates/grv0_acceptance_anchor.json
reports/b1_grv0_baseline_admission.md
```

### Ceiling

```text
GRV-C1 only after exact clean baseline and existing tests are admitted
no continuation, retention, read-back, or write-back evidence
```

## Iteration 2 - GRV1 Instrumentation And Source Fidelity

### Objective

Prove that experiment-local observation reproduces the existing runtime rather
than replacing it.

### Work

1. Reproduce the canonical two-node transport anchor through runtime methods.
2. Capture and verify complete `step()` order under the fixed-topology envelope.
3. Run separate transport-stage and full-step materialized-`K`
   counterfactuals and classify use versus overwrite.
4. Run physical `J -> -J` and edge-coordinate reorientation controls
   separately; classify magnitude, axis, orientation, covariance, and current
   reconstruction.
5. Inventory every excluded or administratively advancing field and carry
   causal/unknown fields into GRV3 closure candidates.
6. Validate canonical intervention cloning and rebuild semantics.
7. Verify canonical artifact serialization and exact/tolerance replay rules.
8. Emit `protected_path_manifest_v1`, adding only newly discovered load-bearing
   paths whose contents match the frozen substrate base revision; emit an
   explicit unchanged v1 successor when no paths are added.
9. Freeze the rule that any later-discovered load-bearing path creates a
   `source_or_specification_mismatch` contradiction and blocks dependent work;
   v1 is never silently amended.
10. Before GRV1 acceptance, strengthen source fidelity with observation
    noninterference, deep-clone isolation, duplicated-surface authority,
    structurally valid multi-amplitude `K`, stagewise `J -> -J`, involutive
    coordinate reorientation, public-stage replay, call multiplicity and
    boundary digests, transition-environment/RNG accounting, and fresh-process
    replay controls. These controls refine instrumentation only; they do not
    change the sealed method or claim ceiling.

### Required outputs

```text
outputs/instrumentation_validation.json
outputs/fixture_registry.json
outputs/intervention_registry.json
outputs/surface_authority_map.json
outputs/protected_path_manifest_v1.json
outputs/gates/grv1_result_receipt.json
outputs/gates/grv1_acceptance_anchor.json
reports/b1_grv1_instrumentation_and_source_fidelity.md
```

### Ceiling

Exact runtime dependency and orientation semantics only. Passing GRV1 does not
establish a formed branch or retained state.

## Iteration 3 - GRV2 Strong Formed Branches

### Objective

Construct and replay a bounded registry of strong homogeneous and nonuniform
zero-current branches under complete double-refresh runtime semantics.

### Work

1. Certify the homogeneous two-node branch.
2. Search for a nonuniform two-node branch and certify every accepted result.
3. Search for nonuniform triangle branches and certify every accepted result.
4. Run symmetry and port-relabel controls.
5. Save, load, and replay every accepted branch.
6. Record full-step and per-block `C/W/J/Phi/G/identity/budget` internal
   residuals, pre/post-continuity states, the budget correction vector and
   no-op status, final refresh, events, and topology.
7. Classify `provisional_physical_strong_branch`, projection-supported,
   step-boundary-only, and internally periodic states separately. GRV3 may
   upgrade a provisional physical branch to `causal_strong_branch` only after
   causal-state closure passes.
8. Record distance from every non-smooth validity/event boundary.
9. Preserve a bounded negative search record when no nonuniform branch is found
   within the preregistered budget; do not treat that as global nonexistence or
   as failure of an otherwise valid homogeneous GRV2 result.
10. Record the full search space and budget, every seed, accepted and rejected
    root, deduplication rule, continuation lineage, selection rule, and a
    held-out replay/validation run for selected branches.

### Committed P2 search realization

GRV2 realizes the sealed method with a bounded, source-derived parameter grid,
not an outcome-conditioned search. `F1` certifies the homogeneous two-node
family directly. `F2` and `F3` use damped Newton search in reduced zero-sum
coherence coordinates under fixed total coherence. The committed grid varies
quadratic site-potential scale, timestep, and transport rate; keeps the existing
source-valid near-neutral anchor `alpha = beta = gamma = 1e-12`, fixed topology,
disabled choice, zero birth rate, and unit-measure budget enforcement; and stays
below the accepted budget of 256 rows per family.

The grid includes the source-derived scales at which the occupied graph
Laplacian and quadratic site-potential derivative can balance, but this does
not admit a branch by construction. Every retained row must still pass the
unchanged complete step, fresh internal-stage replay, numerical no-op budget
correction, event/topology exclusion, symmetry and port controls, save/load
replay, and a selection-independent held-out replay. Symmetry siblings remain
visible and receive permutation-orbit identifiers rather than being discarded
by Euclidean deduplication.

### P2.2 unaccepted execution result

The complete clean run executes 144 rows and retains 48 provisional physical
strong-branch candidates: 16 homogeneous F1 rows, 16 nonuniform F2 rows at
scale `1.0`, and 16 nonuniform F3 rows at scale `1.5`. The remaining 96 F2/F3
rows converge to homogeneous roots and are rejected from the nonuniform target.
All retained rows pass the full step, every internal block, budget no-op,
event/topology, and save/load replay gates; all symmetry/port and selected
held-out fresh-process controls pass. The maximum full-step and internal-stage
`L_inf` residual is approximately `1.63e-10`, below the numerical branch limit
of `1e-9`.

This is a `GRV-C3` candidate pending human acceptance. The zero-current
basin/sink boundary and fields excluded from the physical projection keep the
causal-state upgrade in GRV3. No continuation or retention claim is opened.

### P2.3 preacceptance adversarial hardening

P2.2 is not accepted. Adversarial review requires the complete gate to expose
three previously implicit controls before acceptance:

1. quantify raw-candidate to canonical-state changes separately for `C`,
   authoritative `W`, and authoritative old `J`, while recording derived and
   identity reconstruction without treating those surfaces as solver variables;
2. record continuity deltas, budget correction, active-set identity, clipping
   status, and positive active-set margin explicitly;
3. hold every accepted physical branch for four complete unperturbed beats as
   `step_index` and time advance, checking each beat's staged residual, budget
   no-op, topology/event status, authoritative current, and cumulative physical
   residual.

P2.3 also records full canonical branch signatures, symmetry-orbit counts, and
that accepted row count is not an independent-branch count. The hold tests
administrative-phase dependence of the physical projection only. Cache refresh,
complete causal-state closure, stability, retention, and continuation remain
outside GRV2 and cannot be inferred from a passing hold.

This is a revision-distinct preacceptance instrumentation strengthening. It
changes no search row, solver, fixture, runtime parameter, numerical branch
threshold, or claim ceiling. The P2.2 receipt remains historical and cannot
authorize GRV3; a complete clean P2.3 rerun and separate human acceptance are
required.

### P2.3 execution result

The complete rerun from clean input revision `228e1d4` executes all 144 rows
and preserves the bounded P2.2 portfolio: 48 provisional physical strong-branch
rows and 96 homogeneous roots rejected from the F2/F3 nonuniform target. The
accepted rows occupy 32 canonical symmetry orbits. All accepted rows pass the
new canonicalization, authoritative-current, conductance consistency, budget
active-set, no-clipping, and four-beat physical-hold gates.

The 192 total hold beats have a maximum cumulative physical `L_inf` residual of
approximately `6.54e-10`, within the declared `1e-9` numerical limit. The
minimum budget active-set margin remains above `1.0`, and the maximum admitted
authoritative current is approximately `6.12e-11`, below its `1e-10` tolerance.
All non-cache excluded state is exact across the hold. Cache refresh is observed
on every branch and remains GRV3 closure debt, so P2.3 neither claims a causal
fixed state nor upgrades branch existence to stability, continuation, or
retention. Receipt `73450d2a445770fc3f4b0f2871d3d10c865e097fdd305d97945e41dd7b707c63`
records the result at a `GRV-C3` candidate ceiling pending human acceptance.

The experiment owner subsequently accepts this bounded result. The acceptance
opens only source-current physical formed-branch existence at `GRV-C3` and does
not upgrade any row to `causal_strong_branch` or support stability,
continuation, retention, read-back, or write-back. GRV3 must consume the exact
registry and receipt through the separate GRV2 acceptance anchor.

### Required outputs

```text
outputs/fixed_branch_registry.json
outputs/gates/grv2_result_receipt.json
outputs/gates/grv2_acceptance_anchor.json
reports/b1_grv2_strong_formed_branches.md
```

### Ceiling

Branch existence and source identity only. Branch existence is not continuation
or retention evidence.

## Iteration 4 - GRV3 Causal State And Complete Transition Jacobian

### Objective

Determine the branch-local causal coordinates and temporal mode structure of
the complete synchronous transition.

### Pre-Execution Scope Freeze

GRV3 consumes every one of the 48 accepted GRV2 registry rows. The 32
symmetry-orbit labels state dependence between rows; they are not an execution
reduction and cannot be used to select interesting branches after spectra are
visible. This rule and the exact GRV2 registry digest are frozen in
`configs/grv3_causal_state.json` before GRV3 executes.

GRV3 proceeds in strict order:

```text
GRV3-A causal-state codec and discrete-stratum admission
  -> GRV3-B square transition Jacobian only on admitted branches/columns
  -> GRV3-C smooth response Jacobians plus separate categorical surfaces
```

A branch may pass bounded GRV3-A causal closure while GRV3-B is blocked. In
particular, a zero-current branch on the sink/basin identity boundary has zero
two-sided stratum margin. Such a result is recorded as a non-smooth derivative
boundary, never as an unconverged finite difference and never as a matrix or
spectrum.

The first unaccepted P3 execution exposed a runner-completeness defect: it
applied GRV3-B only to the full `(C,W,J)` chart even when a preregistered `C-W`
or `C` reduction codec passed. P3.1 does not alter branches, fixtures,
thresholds, or reduction definitions. It applies the same GRV3-B/C gates to
every codec-admitted frozen candidate and reports all admitted candidates
without selecting a preferred coordinate after spectra are visible.

The unaccepted P3.1 execution then exposed an interpretation-gate defect rather
than a branch or finite-difference failure. Its reduced matrices converged and
had bounded finite-horizon amplification, but some eigenvector matrices were
severely ill-conditioned; response Jacobians and eigenvalue/subspace convergence
were diagnostic rather than complete machine gates. P3.2 preserves the same
branches, fixtures, coordinate candidates, thresholds, runtime, and claim
ceiling. It gates each derivative column, eigenvalue set, near-unit and fast
invariant subspace, smooth response surface, and finite-horizon nonnormal
diagnostic. Individual eigenvectors are interpretation-blocked when the frozen
condition-number limit fails; a cluster is admissible only when its full span
is resolved and its invariant-subspace residual passes. Neither path supports
retention.

P3.3 is a traceability-only completion discovered before scientific acceptance.
It moves the already committed P3.2 spectral partition (`0.9`), neutral and
cluster tolerances (`1e-6`), and invariant-subspace residual limit (`1e-8`)
into `configs/grv3_causal_state.json` without changing their values. It also
records the final interpretation-blocked matrix identities in the machine
summary. This does not change the method or respond to observed spectra by
moving a threshold; a complete rerun remains required to bind the explicit
contract to the output receipt.

P3.3 remains unaccepted after adversarial causal-state review. P3.4 is a
preacceptance method completion, not a threshold response to the P3.3 spectra.
It preserves the exact branch registry, fixtures, runtime, coordinate
candidates, finite-difference steps, spectral thresholds, and claim ceiling,
while adding validity gates already required by the sealed causal-closure and
covariance discipline:

```text
administrative phase / step-index derivative invariance
per-subfield omitted-state and cache decomposition
decoder correction relative to each derivative step
RNG start, consumption, and post-step equality
formed-branch residual relative to each derivative step
separate first-order J and sign-even J^2 response diagnostics
declared cross-block metric with joint C-W claims disabled
alternate zero-sum basis covariance
symmetry-orbit Jacobian conjugacy
```

P3.4 does not repair zero-current stratum crossings, admit the full cache as a
state block, reinterpret a first-order `J` null as nonlinear eliminability, or
promote endpoint symmetry labels into crossing evidence. A reduced matrix may
remain measured while its fixed-operator spectral interpretation is blocked by
phase, basis, or symmetry covariance. P3.3 artifacts remain preliminary and
are superseded by the complete clean P3.4 rerun; no GRV3 acceptance anchor is
created automatically.

### Work

1. Admit a branch-relative continuous causal-state encoder/decoder and classify
   candidate fields as causal, reconstructed, administrative, observer-only, or
   unknown.
2. Require coordinate round trip, reached-state causal canonicalization, and
   one- plus preregistered multi-step transition commutation before admitting
   the encoded transition map; report only bounded-horizon causal closure unless
   exact exclusion is independently proved.
3. Represent causally relevant categorical fields as a discrete stratum and
   differentiate only within a fixed stratum with declared two-sided margins
   and matching runtime paths.
4. Run canonical matched-state counterfactuals over `C`, `W`, and `J` without
   mutating live `get_state()` objects or leaving hybrid duplicate fields.
5. Freeze the zero-sum coherence tangent basis and interior-safe coordinates for
   conductance, current, and any additional admitted block.
6. Compute the square causal-state transition Jacobian with block-specific
   absolute floors, maximum valid steps, and finite-difference convergence.
7. Compute separate smooth response Jacobians for derived surfaces and
   categorical margin records for discontinuous outputs.
8. Report admitted blocks, eigenpairs, invariant subspaces, conservation/gauge
   modes, and participation ratios.
9. Apply preregistered nonnormal and finite-horizon diagnostics.
10. Verify column, matrix, eigenvalue-cluster, and subspace convergence.
11. Classify stable slow, neutral, oscillatory, and unstable objects separately.
12. Classify counterfactual sensitivity, constitutive independence,
    runtime-causal independence, and eliminability separately for every
    candidate state block.
13. Prove or reject derivative-level invariance across the preregistered
    administrative phase offsets before interpreting a fixed `A_*`.
14. Decompose omitted cache and placeholder fields one by one over the bounded
    codec horizons; never admit the serialization dictionary wholesale.
15. Gate every derivative column on decoder correction, RNG consumption
    equality, and branch-residual-to-step separation.
16. Keep odd first-order `J` response and even quadratic `J^2` response outside
    the transition eigensystem and outside eliminability claims.
17. Report raw and declared-scale block participation as diagnostic only, with
    joint `C-W` mode claims disabled.
18. Require alternate-basis covariance and symmetry-orbit conjugacy before a
    reduced matrix supports temporal interpretation.
13. Assign structural validity, constitutive consistency, runtime reachability,
    and runtime-causal independence from their separate operational gates.
14. Test whether a C-only or C-W reduction is valid on any bounded branch.
15. Upgrade GRV2 branches to `causal_strong_branch` only where excluded fields
    are stationary, reconstructible, or causally irrelevant under the admitted
    codec.
16. Apply and report block-specific causal-equivalence tolerances and
    per-horizon accumulated-error bounds; never replace them with one broad
    aggregate norm.

### Required outputs

```text
outputs/complete_step_jacobians.json
outputs/slow_cluster_registry.json
outputs/gates/grv3_result_receipt.json
outputs/gates/grv3_acceptance_anchor.json
reports/b1_grv3_causal_state_and_transition_jacobian.md
```

### Ceiling

Causal-state and temporal-mode evidence. A slow joint mode is not automatically
the core retained sector.

## Iteration 5 - GRV4 Frozen-Conductance Versus Full Recurrence

### Objective

Separate an experiment-local frozen-`W` structural comparator from the full
runtime recurrence and determine where the two agree or diverge.

### Work

1. Complete the runtime sign audit for the fixed-`W` graph functional.
2. Separate analytic semidiscrete sign, finite-step monotonicity at the runtime
   timestep, and a preregistered timestep sweep.
3. Construct the constrained frozen-`W` second variation outside `src/` using
   the same tangent basis as GRV3.
4. Construct runtime-compatible mobility, semidiscrete, and explicit-step
   comparators.
5. Compare frozen spectra and predicted multipliers with complete-step
   multipliers, mode overlap, and stability class for each accepted branch.
6. Record every assumption needed for elimination or reduction.

### Frozen P4 Execution Contract

The first P4 execution at commit `1c18bda` is useful but unaccepted preliminary
evidence. The thirty-point GRV4 review exposed operator, metric, clustering, and
uncertainty assumptions that require a full P4.1 rerun. No GRV4 acceptance
anchor exists, and P4.1 supersedes rather than edits that result in prose.

P4 consumes the accepted bounded GRV3 result without selecting branches or
coordinates after observing spectra. It constructs a standalone frozen-`W`
comparator for all 48 accepted branches. The primary full-map relation is
evaluated on exactly the 32 branches where GRV3 admitted the `C` transition;
the 16 zero-current categorical-boundary rows remain explicit blocked
comparisons. `C-W` is secondary diagnostic evidence only and inherits every
GRV3 temporal-interpretation block.

The sign audit freezes the graph functional, potential, mobility, and
continuity identities before execution. It checks every canonical tangent
direction plus deduplicated structural-eigenvector and deterministic mixed
directions in both signs at amplitudes `1e-3` and `1e-2`, over runtime timestep
multipliers `0.125, 0.25, 0.5, 1, 2, 4`. The staged comparator calls the
unchanged potential, flux, and continuity implementations while holding `W`
fixed. Conductance reconstruction and semantic/topology stages are excluded by
construction and recorded as reduction assumptions. Weak monotonicity includes
stationary equality; it is not reported as strict increase.

P4.1 defines `H_P` as the fixed-`W` second derivative of the runtime-compatible
functional and `H_cont = -H_P` as the restoring-sign comparator. Structural
curvature, the temporal relaxation operator `A_W H_cont`, and the explicit map
`I - dt A_W H_cont` are reported separately. The self-adjoint representative
`A_W^(1/2) H_cont A_W^(1/2)` supplies rates only after its modes and projectors
are mapped back to physical `C` coordinates. The comparator is classified as
`clamped_counterfactual_only`: algebraic elimination and fast slaving remain
unverified.

Frozen/full comparisons use the accepted GRV3 block metric, declared `C`
embedding and projection, real invariant planes for complex pairs, clustered
subspaces near degeneracy, explicit exclusion of deadbeat overwrite modes, and
an uncertainty budget combining finite-difference, branch-residual, matrix,
eigenvector-condition, and cluster terms. Symmetry is checked by matrix
conjugacy, not spectrum equality alone. A full-map timestep sweep is not used as
continuous-time numerical convergence because the conductance recurrence does
not share a demonstrated timestep scaling with continuity.

No resolved difference within the admitted uncertainty is a valid bounded
result. A strong result requires a verified stability-class or slow-subspace
disagreement, but absence of a resolved difference does not fail the gate and
does not establish equivalence. Neither outcome permits `W` elimination, a
joint `C-W` mode, or a full core continuation operator claim.

### P4.1 Thirty-Point Review Disposition

| # | Disposition frozen before rerun |
|---:|---|
| 1 | Full comparison only on GRV3-admitted temporal maps; blocked branches remain explicit. |
| 2 | `W` is clamped for the whole analytical comparator beat in structural and mobility uses; one `C` update is recorded. |
| 3 | Every row is `clamped_counterfactual_only`; elimination/slaving are not inferred. |
| 4 | Evaluate `F_clamp(C*)-C*`; failure blocks temporal stability but not structural calculation. |
| 5 | Verify runtime potential, flux, functional directional derivative, and sign numerically. |
| 6 | Probe canonical, structural, and mixed zero-sum directions in both signs and amplitudes. |
| 7 | Separate semidiscrete, local discrete, and runtime-timestep signs; projection/clipping/boundary must remain absent. |
| 8 | Frozen timestep sweep tests its discretization; no full-map continuous-time convergence claim is made. |
| 9 | Reuse the exact GRV3 tangent; record `H_P`, `H_cont=-H_P`, and finite-difference/factor audit. |
| 10 | Report structural spectrum, `A_W H_cont`, explicit multipliers, and the mobility/Hessian commutator separately. |
| 11 | Map symmetrized modes/projectors back through `A_W^(1/2)` / `A_W^(-1/2)`. |
| 12 | Record connectivity, `W` range/floor distance, reduced conditioning, and extra mobility nulls. |
| 13 | State that clamping freezes geometry and mobility together; no separate attribution is allowed. |
| 14 | Consume authoritative branch `base_conductance`, digest it, and verify duplicate port-edge consistency. |
| 15 | Record the exact site backend and finite-difference `V''`; nonsmooth rows would block. |
| 16 | Keep potential gauge outside the continuation spectrum. |
| 17 | Declare `iota_C`, `pi_C`, outside-`C` fraction, and embedded-subspace invariance defect. |
| 18 | Reuse the GRV3 block metric and report physical `C` projection separately. |
| 19 | Compare complex pairs as real invariant planes. |
| 20 | Compare near-degenerate modes as clustered subspaces/projectors. |
| 21 | Count and exclude deadbeat overwrite modes from slow disagreement. |
| 22 | Report structural, semidiscrete, and discrete-beat classifications separately. |
| 23 | Require uncertainty-aware robust unit-circle and subspace disagreement. |
| 24 | Verify matrix-level symmetry conjugacy for `H_cont`, mobility, frozen map, and admitted full `C` map. |
| 25 | Retain the preregistered 48/32 branch scope without post-spectrum selection. |
| 26 | Bind branch, parameters, ordering, tangent, metric, and timestep locally per row. |
| 27 | Interpret robust disagreement only as conductance-recurrence dependence. |
| 28 | Interpret no resolved difference only within the tested uncertainty envelope; do not promote it to equivalence. |
| 29 | Keep the gate first-order local; finite-amplitude `J^2 -> W` effects remain open. |
| 30 | Open no preparation, persistence, retention, mediation, read-back, or write-back claim. |

The first clean hardening execution from revision `69382c8` failed closed
before artifact emission. Two representation defects were identified: relative
matrix-conjugacy error was ill-conditioned for near-zero `H_cont`, and a
near-real conjugate pair was collapsed to one real direction instead of kept as
a two-dimensional real invariant plane. P4.1a reuses the already frozen
near-zero absolute Hessian criterion and preserves resolved conjugate planes.
It changes neither branch scope nor scientific thresholds and requires another
clean committed full rerun.

### P4.1 Artifact-Semantics Correction

The reviewed numerical execution remains revision `01389d9`. A later
schema-only correction does not rerun the branch matrix and does not change the
classifier or any numerical leaf. It:

- renames `frozen_semidiscrete_rates` to
  `frozen_semidiscrete_generator_eigenvalues`, because the values belong to
  `-A_W H_cont = A_W H_P`, not to relaxation operator `A_W H_cont`;
- replaces `agreement` with
  `no_resolved_difference_within_uncertainty` and explicitly records that
  equivalence is unsupported;
- records the GRV3 immutable acceptance anchor as the prerequisite authority,
  rather than copying the historical pre-acceptance result-receipt status; and
- binds the source v1 result payload and receipt hashes inside the v2 artifacts.

The correction is lifecycle and interpretation hardening. It neither opens
`GRV-C4` nor changes the 48/32/16 branch scope, the 32 unresolved primary
relations, the 16 blocked full-map comparisons, or any downstream claim.

### Required outputs

```text
outputs/frozen_full_comparison.json
outputs/gates/grv4_result_receipt.json
outputs/gates/grv4_acceptance_anchor.json
reports/b1_grv4_frozen_conductance_full_recurrence.md
```

### Ceiling

The frozen operator may be `substrate_reduced`. It cannot be relabeled as the
full core continuation operator.

## Iteration 6 - GRV5 Preparation, Persistence, And Matched-Probe Mediation

### Objective

Test retention, read effect, write effect, and loop closure as separate causal
arrows.

### Work

1. Execute direct-conductance, activity-mediated, and sign-reversal preparation
   lanes.
2. Consume the preregistered present-current convention without redefining
   probe classes after observing outcomes.
3. Remove forming intervention and measure declared persistence horizons.
4. Project state separation onto accepted slow/fast subspaces.
5. Run the zero-present-probe passive-null control.
6. Match `C` and `J`, preserve candidate `W` differences, and apply identical
   later probes through separate native full-step, native immediate-stage, and
   frozen-`W` reduced lanes.
7. Classify probe input as coherence/potential, old-current state injection, or
   external-current-like analytical input and record the exact readout stage.
8. For each candidate read row, run the full carrier-by-probe `2x2` design and
   report the no-probe baselines, within-carrier probe increments, and their
   difference-in-differences. A baseline difference alone is ordinary
   geometry-conditioned recurrence, not a read effect.
9. Run a preregistered signed amplitude sweep before using linear
   susceptibility, gain, or derivative language; otherwise retain a
   finite-probe interaction ceiling.
10. Run reset, swap, equal-`W`, reached-state, and synthetic-valid controls using
   the canonical intervention registry.
11. Apply a lower ceiling to off-manifold structurally valid rows than to
    reached or constitutively consistent rows.
12. Assign local `GRR0`-`GRR5` only from satisfied gates.
13. Fill the causal possibility matrix without requiring all arrows to agree.

### P5.3 Acceptance Hardening

The 36-point causal-identification review is a revision-distinct confirmatory
pass after the preliminary P5.1/P5.2 results. It may demote or block a result,
but it may not raise the existing rung merely by adding a better description.
Branch selection, primary persistence thresholds, and the present-current
convention remain unchanged.

The clean P5.3 execution must account for every review point separately:

1. freeze `H-W`, `H-CW`, `H-transfer`, and `H-none` carrier hypotheses;
2. preserve GRV3-admitted and GRV3-blocked branch ceilings separately;
3. record preparation stages and define `k=0`/`k=1` exactly;
4. distinguish passive, activity-maintained, regenerated, transferred, and
   absent persistence;
5. keep direct `W` preparation below write-back;
6. separate synthetic old-current input from reached current history;
7. stage direct `J^2 -> W` and indirect `J -> C -> W` consequences;
8. compare `+J/-J` both immediately and after the standardized full step;
9. run a confirmatory preparation-amplitude ladder without adaptive selection;
10. audit direct-`W` metric symmetry, positivity, and conductance floors;
11. record signed carrier vectors, alignment, and orthogonal leakage;
12. keep the original branch fixed throughout persistence;
13. classify instability separately from stable retention;
14. interpret only accepted GRV3 slow subspaces and permit no slow projection;
15. retain the transient/deadbeat mediation category;
16. use fresh unprobed clones for every horizon and probe cell;
17. match all GRV3-admitted non-carrier state plus categorical/admin state;
18. prove that matching preserves authoritative `W`;
19. state that a `W`-only null cannot reject a joint/transferred carrier;
20. keep full-step, immediate-stage, and frozen-`W` lanes separate;
21. retain the preregistered present-current convention;
22. retain all four carrier-by-probe cells;
23. compute oriented vector interactions before norms;
24. classify zero-probe baseline differences separately from read effects;
25. record carrier state before and after every probe readout;
26. report signed-sweep fit and odd/even response decomposition;
27. require multi-edge wrong-location controls for route-selectivity language;
28. classify reset/swap/equal/shuffle mediation outcomes by degree;
29. verify that controls update authoritative and duplicate `W` surfaces;
30. separate write occurrence from retained write;
31. require one linked branch/clock/carrier chain for loop closure;
32. require separate response and later-write clones if the loop gate opens;
33. report detection floors, carrier amplitude, and positive-control sensitivity;
34. report every frozen horizon without best-horizon selection;
35. fail closed on positivity, budget, topology, event, RNG, or stratum failure;
36. keep core Read-Back blocked without its independent directional relation.

The machine-readable audit must record a disposition, evidence location, and
claim effect for all 36 points. A blocked or out-of-scope point may be complete
when the corresponding stronger claim is explicitly unavailable; it may not be
silently marked as positive evidence.

### P5.4 Acceptance Clarification

The P5.3 acceptance review exposed three interpretation boundaries that must be
machine-visible before GRV5 can be accepted. This clarification is
non-upgrading: it cannot change branch scope, thresholds, numerical methods, or
the existing `GRR2` ceiling.

1. Audit whether each `GRR2` displacement lies in the admitted GRV3 `C`
   coordinate. Because GRV3 did not separately identify a branch tangent,
   persistence in that neutral coordinate must retain branch relocation as an
   unresolved rival. It cannot be called transverse branch-relative retention.
2. Keep the native stage-local `J^2 -> W` write separate from the later
   `C`-dominated consequence. Without a stage-matched intervention isolating
   transient `W` from every other consequence of the synthetic old-current
   preparation, specific mediation of later `C` by transient `W` is not
   established.
3. State reachability precisely. The complete-step state is produced by the
   unchanged runtime *from a synthetic intervention*. It is not shown reachable
   from an accepted branch by unchanged runtime evolution alone, and shorthand
   `runtime-reached` wording is prohibited.

Any GRV5 acceptance anchor must bind the original P5.2 evidence identities and
the superseding P5.4 result, audit, receipt, and execution revision. The P5.3
audit source digest must bind the current source result rather than only its
predecessor.

### Required outputs

```text
outputs/conductance_retention_probe.json
outputs/causal_role_matrix.json
outputs/grv5_intervention_registry.json
outputs/grv5_36_point_review_audit.json
outputs/gates/grv5_result_receipt.json
outputs/gates/grv5_acceptance_anchor.json
reports/b1_grv5_retention_read_write_mediation.md
```

### Ceiling

Even `GRR5` is a retained-geometry or joint-retention candidate unless a
present-current-conditioned directional read relation and passive null are
independently established.

## Iteration 7 - GRV6 Current Recurrence And Return Orbits

### Objective

Determine whether current orientation, cycle current, or recurrent transport
survives the unchanged runtime and classify any return orbit precisely.

### Work

1. Freeze the oriented edge order, incidence convention, primary native
   conductance-compatible metric `W_*^-1`, cycle/potential projectors,
   branch/orbit metric policy, divergence tolerance, rank tolerance, and
   edge-reorientation covariance rule before measuring cycle content. Any
   alternative primary metric must prove native potential-flow annihilation;
   other metrics are sensitivity analyses only.
2. Preregister the minimum admitted conductance, condition-number limits for
   `W_*` and `Z^T W_*^-1 Z`, singularity/rejection threshold, and a policy that
   blocks or explicitly reduces ill-conditioned rows rather than silently
   clipping, regularizing, or pseudoinverting them.
3. Certify cycle seeds against the declared incidence matrix and projectors
   before running stationary divergence-free cycle-current controls.
4. Compare exact zero, positive seed, negative seed, sign-even preparation,
   and cycle-space seeds.
5. Search for period-two and higher return orbits using parameter sweeps,
   multiplier continuation, residual minimization, and replay.
6. Record the full orbit search space/budget, all seeds and roots, rejection
   and deduplication rules, continuation lineage, selection rule, and held-out
   replay/validation for every selected orbit.
7. Require full causal-state return, relevant categorical-state equality, and
   only expected administrative advancement; classify physical-only closure as
   `physical_projection_return`.
8. Compute ordinary Floquet multipliers only from the admitted causal-map
   derivatives when every intermediate point and derivative probe remains in
   one continuous stratum. Record stratum-crossing cycles as hybrid/categorical
   returns without a Floquet spectrum unless transition derivatives are added
   in a later validated analysis.
9. Record initial cycle content, sign-even conductance inscription,
   reconstructed current, and remaining cycle projection separately.
10. Verify native potential-flow annihilation, projector idempotence, metric
    orthogonality, decomposition reconstruction, divergence residual, and
    orientation covariance.
11. Separate potential-flow transport orbits from stationary cycle current.
12. Record the statuses of closure, mobility, conservation, uniqueness, and
   orientation assumptions before interpreting exclusions or selection.

### Frozen GRV6 Execution Contract

GRV6 consumes all 48 certified GRV2 branches in committed registry order. The
current-control matrix runs on every branch, while stationary cycle-current
controls run on all 16 `F3` triangle branches because only that admitted family
has nonzero cycle-space dimension. This is topology scope, not post-outcome
selection.

The return search executes exactly 256 deterministic candidates for each
preregistered period `2, 3, 4, 5, 6, 8`, allocated round-robin over all 48
branches. Search coordinates are branch-relative `(C,W)` coordinates with `J`
reset from the source snapshot; every resulting candidate is then judged in
the complete physical `(C,W,J)` projection and categorical causal state.
Period-one and all other proper divisors are tested before a primitive period
is admitted. Failure to find an orbit is bounded search evidence, never a
global nonexistence proof.

The primary cycle projector is constructed directly from a rank-revealed basis
of `ker(B)` and the native `W_*^-1` metric. The implementation does not silently
regularize or pseudoinvert an ill-conditioned primary cycle Gram matrix.
Ordinary Floquet analysis remains row-local and is blocked unless every orbit
point and every finite-difference probe remains in one admitted causal stratum.

### Required outputs

```text
outputs/return_orbit_registry.json
outputs/grv6_contract_audit.json
outputs/grv6_36_point_review_audit.json
outputs/gates/grv6_result_receipt.json
outputs/gates/grv6_acceptance_anchor.json
reports/b1_grv6_current_recurrence_and_return_orbits.md
```

### Ceiling

Nonzero recurrent current is not automatically active circulation, Read-Back,
or self-sustaining identity.

### P6.1 Pre-Acceptance 36-Point Hardening

The first mechanically complete GRV6 result remains unaccepted. A subsequent
36-point review found that its bounded orbit-search accounting was intact, but
that the current-control half needed stronger evidence before the phrase
`cycle_seed_overwritten_by_native_potential_flow` could be accepted. P6.1
therefore hardens the method without changing the runtime, branch envelope,
periods, search budget, root method, or numerical thresholds.

The load-bearing hardening adds:

1. incidence rank, cycle dimension, inverse-conductance metric condition, and
   projected cycle-Gram condition records;
2. divergence and fixed-reference/phase-local cycle projections as separate
   absolute measurements, without near-zero cycle fractions;
3. full pre-runtime seed certification including cycle membership, current
   floor, matched state, topology, RNG, phase, and positive conductance;
   high-amplitude synthetic seeds use frozen absolute-plus-relative seed
   tolerances so floating-point residuals are judged against seed scale without
   relaxing the underlying cycle-space requirement;
4. public-method traces through every native stage that can read, write, or
   overwrite current, plus exact physical parity with `step()`;
5. four preregistered activity amplitudes in both signs, with the native
   quadratic conductance response and budget/floor/event support audited;
6. machine separation of genuinely symmetric F1 exact-zero controls from
   nonsymmetric zero-input potential-flow residuals; and
7. a 36-point audit artifact that distinguishes executed requirements from
   controls that are conditional on an admitted positive orbit.

No admitted orbit exists in the first result. Consequently, phase-shift and
graph-symmetry deduplication, relative-periodic classification, per-block
minimal periods, phase-point reset controls, cycle-averaged pumping, per-phase
codec revalidation, fresh-process candidate replay, and full Floquet
uncertainty analysis remain explicitly **not executed**. P6.1 treats them as
mandatory positive-candidate gates rather than marking them passed. The bounded
negative claim is also narrowed to exact causal-state returns in the declared
search envelope; it does not exclude relative periodic orbits or count
ill-conditioned search rows as negative evidence.

The committed result at revision `1134009` remains historical preliminary
evidence. A clean P6.1 rerun must supersede it before scientific acceptance can
be considered.

### P6.2 Source-Kernel Stage And Eligibility Hardening

P6.1 traced every public GRC9V3 method used by `step()`, but its transport trace
observed `rebuild_transport_state()` as one stage. Review point 7 is stricter:
conductance formation, potential reconstruction, and native current
reconstruction must be distinguishable. P6.2 uses the unchanged source-current
transport kernels as diagnostic functions, records both first and final
transport sequences, then compares their final physical and transport surfaces
against the authoritative public wrapper. A mismatch blocks point 7.

P6.2 also replaces the seed certificate's declarative no-event statement with
measured hybrid-spark eligibility parity plus explicit choice, growth,
boundary-pruning, and external-current-surface checks. These diagnostics do not
create an alternative runtime step, authorize source changes, or make the
experiment-authored seeds runtime-reached. They only expose the native wrapper's
internal source semantics at the resolution required by the review.

### P6.3 Boundary-State Replay And Search Diagnostics

P6.2 review found one reduced `(C,W)` root that converges within the solver
tolerance but fails full-state return because old current changes by about
eight. P6.3 does not expand or retune the orbit search. It selects every row
matching the preregistered diagnostic condition of reduced convergence plus
full-state current failure, takes the beat-one complete state, and replays that
state locally, through snapshot/load, and in a fresh process. Manual stage
instrumentation must match `step()` while exposing continuity and budget
corrections. The allowed classification distinguishes constraint-supported
nonzero-current fixed state, budget-projection support, positivity-boundary
support, physical-only fixed state, and failed reproduction.

P6.3 also makes the existing solver gate auditable by serializing finite-
difference Jacobian singular values, condition number, declared limit, matrix
digest, residual, and no-regularization status. Search accounting is stratified
by fixture and period, including the frozen repeated round-robin offset. Generic
finite activity seeds receive explicit non-applicable divergence and cycle-
membership statuses. Accepted wording must distinguish 22 executed current-
result requirements from 14 deferred positive-orbit gates and preserve the
branch-relative `(C,W)` search-chart scope.

## Iteration 8 - GRV7 Spatial, Temporal, And Continuation Thresholds

### Objective

Test whether exact runtime spatial Hessian diagnostics can or cannot be
identified with temporal and continuation thresholds.

### Work

The scientific discriminator is prioritized as:

```text
operator identity
-> branch identity
-> reduction validity
-> critical-subspace identity
-> uncertainty-separated threshold relation
-> categorical-boundary separation
```

Conditional controls such as complex-plane tracking or WLS conditioning become
load-bearing only when the corresponding surface is used. Generic provenance
hygiene remains required for the artifact lifecycle but is not itself evidence
for the threshold relation.

1. Type `H_row`, `H_signed`, `H_WLS`, `H_cont^{W*}`, `A_W H_cont^{W*}`, and
   `A_full` by domain, metric, sign convention, and threshold rule before
   comparing them. Do not pair modes by sorted eigenvalue index. A reproducible
   WLS output is not identifying threshold evidence when its raw quadratic
   design is rank deficient; declared regularization must remain visible.
2. Continue accepted branch families across `+1`, stable-interior, `-1`, and
   any complex unit-circle transition available in scope using preregistered
   branch matching, cluster matching, parameter-step, and restart rules.
3. Audit every reduced comparison at each point. A failed reduction or stratum
   gate blocks the comparison; it is not threshold disagreement. Record current
   slaving and loop-invertibility as not applicable where the comparator is a
   clamped-`W` construction rather than an elimination.
4. Compare critical invariant subspaces through a declared common domain or
   embedding, including dimension, projector/principal-angle, physical support,
   and symmetry character where a crossing is claimed.
5. Record full transition multipliers, frozen comparators, row/signed/WLS
   Hessians, event status, and basin/spark evidence.
6. Audit any admitted complete-step `+1` cluster for conservation, gauge,
   branch-tangent, block-participation, conditioning, and uncertainty status.
   If nontriviality is unresolved, retain it as an admitted near-unit spectrum
   rather than an informative temporal threshold.
7. Require an uncertainty-separated threshold witness and off-threshold bracket
   for a decisive counterexample.
8. Stop smooth continuation at event, topology, sink/basin, budget-active-set,
   clipping, or other categorical boundaries.
9. Map every selected source branch to each primary or symmetry path use so
   repeated branch use across parameter axes cannot look like post-spectrum
   branch omission.
10. Preserve bounded correlation findings without universalizing them.

### Required outputs

```text
outputs/spatial_temporal_threshold_matrix.json
outputs/gates/grv7_result_receipt.json
outputs/gates/grv7_acceptance_anchor.json
reports/b1_grv7_spatial_temporal_continuation_thresholds.md
```

### Ceiling

The gate may establish bounded non-equivalence. It may record correlations but
cannot promote them to a universal threshold identity or prove they never occur.

## Iteration 9 - GRV8 Classification, Route Decision, And B1-L Handoff

### Objective

Close B1-GR without requiring a positive Read-Back result and decide the honest
next route for every tested role.

### Work

GRV8 executes in two separately reviewed stages. Stage 1 emits the scientific
classification, routing artifacts, protected-path successor, complete-suite
result, report, and `grv8_result_receipt.json`. It stops with
`awaiting_scientific_review`: the evidence bundle, successor specification,
LGRC handoff, closeout anchor, and `GRV-C6` do not yet exist. Stage 2 may begin
only after a human acceptance anchor binds the Stage 1 receipt. It then freezes
the non-self-referential evidence bundle, emits the evidence-grounded successor
and handoff, and submits those closeout artifacts for their separate acceptance.

The first P8 Stage 1 candidate at revision `1448757` remains unaccepted and is
superseded by P8.1. P8.1 hardens classification without adding a new scientific
probe. It must:

1. classify native current recurrence separately from the `j = J_C` mapping;
2. decompose transport conductance, stage-local write, post-activity
   persistence, durable carrier, later mediation, baseline transport, reduced
   susceptibility, magnitude, axis, orientation, cycle current, and typed
   one-form bridge roles;
3. bind every cross-gate fact to an accepted gate revision, acceptance-anchor
   digest, artifact digest, exact field or row, and consumed-value digest;
4. serialize the controlling L0-L5 wording unchanged;
5. record branch/fixture envelope, runtime stage, continuous stratum, secondary
   qualifiers, and outside-envelope uncertainty for every object;
6. preserve the GRR2 synthetic-input ceiling and branch-relocation rival in an
   arrow-by-arrow causal-role matrix;
7. distinguish current temporalization, retained-carrier, oriented-current,
   unchanged-runtime constructibility, analysis-only, theory-open, and LGRC
   routes rather than selecting one global next architecture;
8. prepare a two-sided LGRC boundary while keeping the final handoff blocked
   until Stage 1 acceptance and distinguishing legacy B1-L from future LGRC-N;
9. retain a primary cause, secondary alternatives, rejected routes, and next
   action for every contradiction entry; and
10. preserve reasons and replacement wording for superseded exploratory claims.

The P8.1 result at revision `bb9be8d` also remains unaccepted and is superseded
by P8.2. P8.2 is a classification correction, not another scientific gate. It
must:

1. preserve the accepted controlling traceability matrix while recording a
   final-row correction that separates `T-S02` from duplicated `D-M01`
   ownership and leaves `D-M01` with `TR-17`;
2. derive every other final traceability assumption envelope from that row's
   own `Required assumptions` field and deduplicate exact evidence records;
3. classify `A-TRANSPORT` as satisfied only for the declared canonical
   fixed-topology coordinate identity while keeping topology-changing
   interspace transport untested under `D-T01`;
4. route stationary cycle-space current nonrealization separately from the
   bounded, ill-conditioned, and incomplete return-orbit search;
5. require an explicit commuting reduction before assigning L4 to the bounded
   runtime causal state; absent that derivation, preserve the runtime fact as
   exact L3 and block a declared core-reduction claim; and
6. leave every accepted GRV0-GRV7 artifact, scientific claim ceiling, Stage 2
   artifact, acceptance anchor, and `GRV-C6` boundary unchanged.

1. Assign all required assumption statuses before classifying claims.
2. Assign one of the six implementation statuses and L0-L5 correspondence to
   every tested object.
3. Complete contradiction and theory-reopening routing.
4. Decide each candidate extension without implementing it.
5. Decide whether no extension, analysis-only treatment, theory reopening,
   selectable GRC extension, or B1-L is justified.
6. Accept the GRV8 scientific classification through its ordinary result
   receipt and acceptance anchor.
7. Freeze a non-self-referential evidence-bundle manifest over accepted
   GRV0-GRV8 evidence before generating the successor.
8. Produce a versioned evidence-grounded successor specification while keeping
   Drafts 3.2, 3.3, and 3.4 and the accepted controlling Draft 3.4.1 unchanged,
   then accept the bundle/successor through the separate GRV8 closeout anchor.
9. Emit the superseded-claims register.
10. Freeze `lgrc_handoff.json`, including positive and negative inherited
   boundaries.
11. Complete every traceability-matrix row with assumptions, result, and route.
12. Rerun the complete existing suite from the GRV8 clean input revision.
13. Freeze the unchanged-GRC evidence bundle and verify protected runtime/spec/test
    paths remain unchanged.

### Required outputs

```text
outputs/assumption_status_matrix.json
outputs/final_contradiction_routing.json
outputs/equivalence_classification.json
outputs/final_causal_role_classification.json
outputs/final_claim_classification.json
outputs/final_theory_debt_register.json
outputs/final_theory_test_traceability.json
outputs/extension_decision.json
outputs/theory_reopening_decision.json
outputs/evidence_bundle_manifest.json
outputs/superseded_exploratory_claims.json
outputs/lgrc_handoff.json
outputs/gates/grv8_result_receipt.json
outputs/gates/grv8_acceptance_anchor.json
outputs/gates/grv8_closeout_acceptance_anchor.json
reports/b1_grc9v3_verification_report.md
```

### Ceiling

`GRV-C6` means the verification and routing are complete. It does not mean
Read-Back, continuation-spectrum implementation, a runtime extension, or B1-L
execution has succeeded or even been selected.

## Verification Strategy

Use `.venv` for all Python execution. Each iteration should run:

1. the narrow experiment-local tests for its scripts and schemas;
2. the targeted existing GRC tests whose behavior it consumes;
3. deterministic artifact rebuild and digest comparison;
4. protected-path diff verification;
5. the complete existing suite only where the gate or source change warrants
   it, with GRV0 requiring the complete suite.

Numerical searches must record seeds, tolerances, convergence, failed searches,
and rejected branches. A search failure is not evidence of mathematical
nonexistence outside the declared envelope.

## Final Route Discipline

B1-GR is successful when unchanged-runtime evidence determines the maximum
supported correspondence and the next route. It is not required to select an
extension or open B1-L.

Any runtime implementation must occur in a later revision-distinct plan and
checklist with default-off compatibility and applicable GRV reruns. Any LGRC
investigation must begin from the accepted B1-GR handoff and must not inherit a
positive claim that B1-GR did not establish.
