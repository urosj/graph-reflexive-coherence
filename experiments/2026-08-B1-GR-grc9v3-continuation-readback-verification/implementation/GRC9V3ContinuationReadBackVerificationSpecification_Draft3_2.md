# GRC9V3 Continuation and Read-Back Verification Specification

## B1-GS0 — Theory Basis, Unchanged-Substrate Reproduction, and LGRC Handoff

**Date:** 2026-08-19  
**Status:** Draft 3.2 — theory-hardened pre-execution propagation-audit revision  
**Supersedes:** Draft 3.1  
**Target repository:** `github.com/urosj/graph-reflexive-coherence`  
**Theory repository:** `github.com/urosj/geometric-reflexive-coherence`  
**Target runtime:** unchanged `GRC9V3`  
**Proposed repository path:**

```text
experiments/2026-08-B1-grc9v3-continuation-readback-verification/
  implementation/
    GRC9V3ContinuationReadBackVerificationSpecification.md
```

```text
specification_id = b1_grc9v3_continuation_readback_verification_v3_2
specification_state = draft_pre_execution
theory_basis_state = assumption_operationalized_decision_grade_pre_execution
runtime_change_authorized = false
src_change_authorized = false
existing_test_change_authorized = false
pygrc_analysis_authorized = false
new_readback_runtime_authorized = false
n32_selected = false
l04_selected = false
lgrc_execution_authorized = false
baseline_commit_sha = REQUIRED_BEFORE_EXECUTION
theory_commit_sha = REQUIRED_BEFORE_EXECUTION
```

---

# 1. Purpose

This specification turns the B1 theory-to-substrate inquiry into a repository-executable verification program for the existing `GRC9V3` runtime.

It has three normative parts.

1. **Part I freezes a decision-grade theoretical basis.** It records what *The Continuation Spectrum* and *Read-Back* establish, what the B1 investigation derived from them, which constructions remain candidates rather than core results, which negative boundaries govern later decisions, and which unresolved theory debts must remain open.
2. **Part II defines an unchanged-runtime GRC verification experiment.** It tests the actual repository checkout, full `GRC9V3.step()` semantics, fixed branches, transition Jacobians, branch-relative slow state, conductance-mediated historical influence, recurrent orbits, and the separation between spatial Hessians and temporal or continuation marginality.
3. **Part III defines the LGRC handoff boundary.** It identifies what must be stabilized in GRC before event queues, packet transit, proper time, lineage, event return maps, and topology-changing history can be interpreted as genuine additions.

The central question is:

```text
What do the current GRC9V3 equations and complete synchronous runtime actually
realize from the continuation, retention, read-back, and write-back distinctions;
what do they realize only in a reduced or analogous form; what is merely
measurable; which negative results constrain later GRC/LGRC design; and which
missing roles justify a later selectable substrate extension or a return to theory?
```

This is not an implementation of the two core papers. It is the verification and decision surface required before such an implementation can be specified responsibly.

## 1.1 Draft 3.2 pre-execution propagation-audit revision

Draft 3.2 preserves the full theoretical contract, unchanged-runtime verification program, fixtures, scientific questions, GRV gate sequence, and GRC-before-LGRC serial order of Draft 3.1. It does not authorize runtime changes.

It preserves the eight pre-execution micro-corrections accepted after review:

1. `T-A05` now uses one consistent assumption envelope; orientation remains a GRV6 measurement convention rather than an assumption of the stationary-gradient-current exclusion.
2. `A-LOOP-INVERT` consistently refers to the full effective current-loop block, with $I-\zeta_C\mathcal R_{M,*}$ retained only as the explicitly reduced frozen zero-background case.
3. The definition of $\mathcal B_{\mathrm{eff},*}$ now forbids current dependence from being hidden inside nominally non-current branch data.
4. `A-STATE-CLOSURE` and the runtime projection now distinguish physical fixed-point equality from causal-state equality and require causally relevant administrative or bookkeeping state to remain in the closure audit.
5. The LGRC handoff schema now serializes `not_applicable` assumption outcomes and references the complete assumption-status matrix.
6. `A-NONNORMAL-CONTROL` now has executable asymptotic-spectral and finite-horizon evidence modes.
7. `A-FAST-SLOW` now requires a preregistered quantitative separation on one declared branch and clock, while permitting `not_applicable` where no independent current-relaxation sector exists.
8. Fixed-topology GRC now has a default ambient coordinate identification, with a separate declaration required when inner products or state metrics vary.

A subsequent full-text propagation audit identified one additional gate-local clarification, now integrated: before `T-A05` is invoked in `GRV6.1`, the executor must record `A-CLOSED`, `A-MOBILITY`, and `A-CONSERVE`; `A-ORIENTATION` remains separate as a sign, axis, and orientation classification convention in `GRV6.2`.

The eight micro-corrections and this propagation clarification do not add theory claims, proof notes, debts, GRV gates, fixtures, or extension decisions. They make existing assumptions assignable and prevent reduced diagnostics, physical projections, coordinate conventions, or gate-local shorthand from being mistaken for full causal closure.

Draft 3.2 remains a pre-execution verification specification. It does not turn candidate completions into core results, select a unique retained projector or read-back operator, authorize `pygrc.analysis`, select N32 or L04, or authorize substantive LGRC execution.

# 2. Controlling sources and authority

## 2.1 Theory sources

The controlling theory sources are:

- [The Continuation Spectrum](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2026-08-TheContinuationSpectrum.md)
- [Read-Back](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2026-08-ReadBack.md)

The following earlier papers are lineage or context sources only where explicitly identified:

- [Reflexive Coherence](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2025-11-ReflexiveCoherence.md)
- [Seeds of Life](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2025-11-SeedsOfLife.md)
- [Reflexive Coherence: Identity, Choice, and Abundance](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2025-11-RC-IdentityChoiceAbundance.md)

## 2.2 GRC sources

The controlling unchanged-substrate sources are:

- [`specs/README.md`](../../../specs/README.md)
- [`specs/grc-9-v3-spec.md`](../../../specs/grc-9-v3-spec.md)
- [`src/pygrc/models/grc_9_v3.py`](../../../src/pygrc/models/grc_9_v3.py)
- [`src/pygrc/models/grc_9_v3_runtime.py`](../../../src/pygrc/models/grc_9_v3_runtime.py)
- the existing `tests/models/test_grc_9_v3_*.py` suite

The theory papers remain the semantic source of truth for their own claims. The GRC specification and runtime are the source of truth for what the current graph substrate actually executes. Repository experiments are the source of truth for runtime evidence.

## 2.3 Provenance labels

Every final theoretical or substrate claim must carry one provenance label.

| Label | Meaning |
|---|---|
| `core_inherited` | Explicitly established by one of the two controlling core papers. |
| `core_derived` | A mathematical or logical consequence derived in B1 from inherited equations under stated assumptions. |
| `candidate_constitutive_completion` | A coherent realization showing that closure is possible, but not uniquely required by the core. |
| `substrate_requirement` | A role or discriminator that any claimed graph realization must satisfy. |
| `substrate_exact` | Directly executed by unchanged `GRC9V3` and reproduced from repository state transitions. |
| `substrate_reduced` | Valid only under an explicitly declared reduction such as fixed topology, frozen conductance, or selected branch. |
| `substrate_analogical` | Similar causal or mathematical form without a derived or constitutive correspondence. |
| `measurable_not_constitutive` | Computable from runtime state or transition but not read or enforced by the runtime itself. |
| `open` | The theory or realization does not currently determine the answer. |
| `deferred` | Intentionally left to a later GRC extension or LGRC investigation. |

A `core_derived` or `candidate_constitutive_completion` result must not be written as though it were already proved in the published core paper.

## 2.4 Normative assumption registry

The following assumption identifiers are normative. A claim is admitted only within the assumptions attached to it. Repository evidence must classify each required assumption as:

```text
satisfied
failed
not_identifiable
not_applicable
deferred
```

A failed or unidentifiable assumption blocks the associated claim within the tested envelope; it does not by itself falsify the claim.

| Assumption ID | Statement | Decision use |
|---|---|---|
| `A-PASSIVE` | The passive null $\mathfrak R_M(\mathcal T,h;0)=0$ holds for every admissible retained structure and geometry under the same present-current convention. | Required for explicit read-back and zero-background derivative claims. |
| `A-SMOOTH` | The relevant constitutive, branch, projector, and transition maps possess the differentiability required by the stated derivative or second-variation claim. | $C^1$ for linearization; $C^2$ for perturbative-order and Hessian claims. |
| `A-REGULAR-SLAVING` | The local implicit-function or suitable Fredholm hypotheses hold for noncritical constitutive blocks. | Distinguishes failure of regular elimination from failure of the whole theory. |
| `A-LOOP-INVERT` | $I-\mathcal B_{\mathrm{eff},*}$ is boundedly invertible on the declared current space. The direct condition $I-\zeta_C\mathcal R_{M,*}$ is equivalent only in the explicitly frozen zero-background reduction where no additional first-order current-dependent path survives. | Required for local algebraic current slaving and bounded response. |
| `A-ISOLATION` | The selected eigenvalue or spectral cluster is isolated, has constant algebraic dimension, and has controlled resolvent separation. | Required for individual-mode or Riesz-cluster continuation. |
| `A-MOBILITY` | Mobility or conductance is positive and nondegenerate on the relevant constrained subspace, with any null sector declared. | Required for gradient-flow dissipation and closed stationary-current exclusions. |
| `A-CLOSED` | The branch has no through-flow or external current injection across its declared boundary. | Required for closed stationary-current claims; boundary-driven flow is a different branch. |
| `A-UNIQUENESS` | The deterministic transition/evolution is locally well posed and locally unique under the declared symmetry. | Required before exact symmetric zero is said to remain unable to choose an orientation. |
| `A-BRANCH` | The reference branch, parameter path, and branch gauge or modulation rule are declared before retained displacement is evaluated. | Prevents retrospective branch fitting. |
| `A-CLOCK` | The temporal beat, physical or model clock, persistence horizon, and norm are declared. | Required for slow, retained, relaxation, Floquet, and finite-horizon claims. |
| `A-CONSERVE` | The conserved quantity, node/volume measure, tangent constraint, and any budget correction are declared and controlled. | Required for constrained Hessians and comparable transition spectra. |
| `A-ORIENTATION` | Edge or one-form orientation, coordinate reversal, bundle identification, and covariance conventions are declared. | Required for current-level equivalence and orientation-retention claims. |
| `A-TRANSPORT` | An ambient state-space identification or explicit interspace transport is declared before states, projectors, currents, or modes at different branch points are compared. Fixed-topology GRC may use the canonical coordinate identity only under the conditions in Section 2.4.3. | Required for moving branches and all topology-changing continuation claims. |
| `A-SIGN-EVEN` | The structural channel under study depends on $j$ through $j\otimes j$ or another even function, and no independent linear-$j$ term is included in that channel. | Required for the first-order read versus second-order inscription result. |
| `A-FIXED-TOPOLOGY` | Graph topology, support, state dimension, and edge/node ordering remain fixed during the tested transition family. | Required for fixed-space GRC Jacobians and projector comparisons. |
| `A-REACHABLE` | The tested state is runtime-reachable, or its synthetic-valid status and resulting lower claim ceiling are declared. | Prevents unreachable counterfactuals from being promoted into native branch claims. |
| `A-NONNORMAL-CONTROL` | The claimed asymptotic or finite-horizon interpretation satisfies one of the preregistered evidence modes in Section 2.4.1. | Required before eigenvalue slowness is promoted under non-normal dynamics. |
| `A-FAST-SLOW` | A preregistered quantitative separation between a separately identifiable current-relaxation sector and the slower coherence/retention/geometry sector is established on one declared branch and clock, as specified in Section 2.4.2. | Required for algebraic read-back as a fast attracting limit; may be `not_applicable` if no independent current-relaxation sector exists. |
| `A-STATE-CLOSURE` | The declared present state contains every serialized or reconstructed variable capable of affecting the next transition within the tested envelope. A field excluded from the physical fixed-point norm must be demonstrated causally inert or retained in the closure state. | Required for a positive Markov-sufficiency claim; physical equality and causal-state equality remain separate. |

### 2.4.1 Operational status of `A-NONNORMAL-CONTROL`

`A-NONNORMAL-CONTROL` may be satisfied through either of two preregistered evidence modes.

**Asymptotic spectral interpretation** requires:

- `A-ISOLATION` for the claimed mode or cluster;
- left/right eigenvector, invariant-subspace, or equivalent conditioning information;
- and a declared bound on at least one of: eigenvector/subspace condition number, resolvent norm, pseudospectral exclusion, or another justified asymptotic-control diagnostic.

**Finite-horizon interpretation** requires:

- a declared horizon, clock, state norm, and return or transition map;
- the propagator or semigroup over that horizon;
- and singular values, a propagator-norm bound, or another explicit transient-amplification measure.

The fixture or operator family must preregister its diagnostic and acceptance threshold before scientific interpretation. If neither evidence mode is available, `A-NONNORMAL-CONTROL` is `not_identifiable`, and eigenvalue-only retention, slowness, or stability claims are blocked. `A-ISOLATION` asks whether a spectral cluster is separable; `A-NONNORMAL-CONTROL` asks whether that spectral separation adequately characterizes the dynamics being claimed.

### 2.4.2 Operational status of `A-FAST-SLOW`

`A-FAST-SLOW` is satisfied only when the current-relaxation sector and the slower coherence, retention, or geometry sector are compared on the same declared branch, state representation, beat, and clock. At least one preregistered quantitative separation must be established:

```text
spectral-rate separation
discrete-multiplier or effective-decay-rate separation
return-map cluster separation
validated time-scale ratio
```

The selected measure, operator blocks, threshold, and treatment of neutral or conserved directions must be declared before interpreting algebraic current slaving as a fast limit. If the tested branch has no separately identifiable temporal current-relaxation sector, `A-FAST-SLOW` is `not_applicable`, not `failed`.

### 2.4.3 Fixed-topology ambient identification under `A-TRANSPORT`

For fixed-topology GRV gates, the default ambient identification is the coordinate identity on the canonical serialized chart with fixed:

```text
state dimension
node order
edge order
row or port order
edge orientation
```

If the state inner product, node/edge measure, or metric varies, operator and projector comparisons must additionally declare the isometry, congruence, normalization, or fixed-reference inner-product representation used. Coordinate identity alone does not make projectors orthogonal or operators self-adjoint under changing metrics. This default does not apply across topology, support, or state-dimension change.

### 2.4.4 Physical projection and causal-state closure

Physical fixed-point equality and causal-state equality are separate comparisons.

A field may be excluded from the physical residual because it advances administratively while the physical state is stationary. That exclusion does not certify causal irrelevance. Every excluded field must be classified as:

```text
deterministic administrative advancement
causal runtime state
observer-only state
reconstructed state
unknown
```

Fields classified as `causal runtime state` or `unknown` remain inside the `A-STATE-CLOSURE` audit. A positive closure claim is admitted only after omitted fields have been demonstrated causally inert within the tested envelope.

Assumption identifiers are not implementation requirements by themselves. They state the envelope within which a claim is meaningful.

## 2.5 Authority and backward-correction rule

Repository evidence may pressure this theoretical basis, but it may not silently rewrite it.

A mismatch must be classified as one of:

```text
substrate_nonrealization
candidate_graph_mapping_error
core_derived_claim_too_strong
core_assumption_incompatible_with_this_realization
construct_not_identifiable_with_available_interventions
numerical_or_instrumentation_failure
source_or_specification_mismatch
```

The response depends on provenance.

- A mismatch with `core_inherited` means that the tested substrate does not realize the inherited claim under the declared mapping, or that a separate core-paper revision must be opened. The experiment may not silently weaken the inherited statement.
- A mismatch with `core_derived` may reopen the B1 derivation.
- A mismatch with `candidate_constitutive_completion` may reject that candidate without changing the inherited core.
- A failure of identifiability may block a claim without proving that the mechanism is absent.
- A source or instrumentation mismatch invalidates the affected experimental result.

Every reopened claim must retain its original claim identifier and record the superseding decision.

---

# Part I — Decision-grade theoretical basis

# 3. Claim concordance and decision authority

## 3.1 Claim ledger

The following ledger is binding for interpretation. The assumption identifiers refer to Section 2.4; detailed conditions and derivation notes appear later.

| Claim ID | Statement | Provenance | Source anchor | Required assumptions and limits |
|---|---|---|---|---|
| `T-S01` | The mature primitive coherence state is $(C,J_C)$. | `core_inherited` | *Read-Back*; mature RC state declaration | Does not establish `A-STATE-CLOSURE` for any runtime. |
| `T-S02` | Core primitive state, runtime causal state, and analytical perturbation state are distinct questions. | `core_derived` | B0; B1-C | `A-BRANCH`, `A-CLOCK`, `A-CONSERVE`; branch- and realization-relative. |
| `T-RW01` | Retention, read-back, and write-back are distinct causal roles. | `core_inherited` | *Read-Back* | None implies another; each requires its own acceptance contract. |
| `T-RW02` | Read-back obeys the passive null $\mathfrak R_M(\mathcal T_M,h;0)=0$. | `core_inherited` | *Read-Back* | `A-PASSIVE`; same present-current convention across comparisons. |
| `T-RW03` | $j$ is a derived current-like contribution, not another primitive conserved stream. | `core_inherited` | *Read-Back* | `A-ORIENTATION` for directional claims; realization may be explicit, eliminated, or distributed. |
| `T-RW04` | $j=J_C$ is a declared simplifying limit, not a derivation of general read-back. | `core_inherited` | *Read-Back* | It suppresses retention selectivity by construction. |
| `T-RW05` | Retention capacity, retained content, and historical record are different. | `core_derived` | B1-RW | `A-STATE-CLOSURE` is required before a historical ledger is declared unnecessary. |
| `T-RW06` | Retention, read-back, and write-back must be accepted or rejected arrow by arrow; the full loop is not required to establish one arrow. | `core_derived` | B1-RW pressure result | Full reflexive closure requires all claimed arrows and mediation. |
| `T-RW07` | Baseline current, direct read current, and effective closed-loop feedback are distinct. | `core_inherited` + `core_derived` | *Read-Back*; B1-RW | `A-SMOOTH`; active slaving additionally requires `A-LOOP-INVERT`. |
| `T-RW08` | At zero background, linear read response and sign-even quadratic geometric inscription occur at different perturbative orders. | `core_derived` | B1-Cb-1 | `A-PASSIVE`, `A-SMOOTH`, `A-SIGN-EVEN`; evaluated at $J_*=j_*=0$. |
| `T-RW09` | $j\otimes j$ and sign-even graph quantities preserve magnitude or an unoriented axis, not current orientation. | `core_inherited` + `core_derived` | *Read-Back*; B1-Cb-2.1 | `A-ORIENTATION`, `A-SIGN-EVEN`; an oriented carrier may add information. |
| `T-RW10` | Field-trajectory, current-level, and full reflexive equivalence are progressively stronger claims. | `core_derived` | B1-Cb-1.2; B1-Cb-2 | `A-ORIENTATION`, `A-CONSERVE`; equal divergence does not imply equal current or geometry. |
| `T-RW11` | Sector update, effective retained write, and reflexive write-back are separate claim levels. | `core_derived` | B1-RW | `A-BRANCH`, `A-CLOCK`; projector and branch motion require causal attribution. |
| `T-M01` | Low spatial modes are not generally dynamically slow retained modes. | `core_inherited` | *The Continuation Spectrum*; *Read-Back* | Alignment may be claimed only under an explicitly demonstrated closure and clock. |
| `T-M02` | Dynamic retention belongs to the temporal closure, clock, branch, representation, and horizon actually declared. | `core_inherited` + `core_derived` | Both controlling papers; B1-Cb-1.2 | `A-BRANCH`, `A-CLOCK`, `A-TRANSPORT`; no closure-independent projector. |
| `T-M03` | Stable slow retention, exact neutrality, and growing formative instability are different. | `core_derived` | B1-C | `A-CLOCK`; discrete multipliers and continuous rates must be translated explicitly. |
| `T-M04` | Finite-horizon persistence under non-normal dynamics is generally observer-relative unless the runtime has the required predictive state or declared schedule. | `core_derived` | B1-Cb-3 | `A-CLOCK`, `A-NONNORMAL-CONTROL`, `A-STATE-CLOSURE`; depends on horizon, norm, and path. |
| `T-C01` | Spatial scale, continuation curvature, relaxation rate, read-back gain, spatial Hessian, and transition multiplier are distinct objects. | `core_inherited` | Both controlling papers | Relations require an explicit reduction and shared branch envelope. |
| `T-C02` | The published continuation Hessian applies to no-current, frozen-current, or smoothly slaved-current branches. | `core_inherited` | *The Continuation Spectrum* | `A-BRANCH`, `A-SMOOTH`, `A-CONSERVE`; independently variable active-current continuation remains open. |
| `T-C03` | Structural formation and dynamic realization are separate requirements. | `core_derived` | B1-C | `A-BRANCH`; coincidence requires a compatible temporal closure. |
| `T-B01` | Formed state, formed branch, tracked reference branch, and actual trajectory are different. | `core_inherited` + `core_derived` | *The Continuation Spectrum*; B1-C | `A-BRANCH`; retained displacement is reference-relative. |
| `T-B02` | The reference branch and branch gauge must be declared before evaluating retained displacement. | `core_derived` | B1-C; B1-Cb-3 | `A-BRANCH`; retrospective fitting is inadmissible. |
| `T-B03` | Individual mode identity is valid only while the mode is simple and isolated; otherwise the continuing object is a cluster or subspace. | `core_inherited` + `core_derived` | *The Continuation Spectrum*; B1-Cb-3 | `A-ISOLATION`, `A-TRANSPORT`; non-normal claims also require `A-NONNORMAL-CONTROL`. |
| `T-B04` | Topology-changing continuation requires an explicit interspace transport; lineage is not automatically that transport. | `core_derived` | B0; B1-Cb-3 | `A-TRANSPORT`; deferred to LGRC after GRC stabilization. |
| `T-A01` | Algebraic read-back may be a normally attracting fast temporal limit. | `candidate_constitutive_completion` | B1-Cb-2.2 | `A-SMOOTH`, `A-LOOP-INVERT`, `A-FAST-SLOW`; one admissible class, not a unique law. |
| `T-A02` | Loss of local current-block invertibility prevents the regular algebraic elimination of the corresponding critical current direction; a claimed branch passage must retain that direction as an explicit local coordinate or provide another justified higher-order resolution. | `core_derived` | B1-Cb-2.1/2.2 | `A-SMOOTH`, `A-REGULAR-SLAVING`; does not select one temporal completion. |
| `T-A03` | In a deterministic locally unique reversal-symmetric system, exact symmetric zero cannot select an oriented active branch without a seed, bias, inherited oriented state, boundary asymmetry, or declared stochasticity. | `core_derived` | B1-Cb-2.1/2.2 | `A-UNIQUENESS`, `A-ORIENTATION`; instability amplifies perturbations but does not create distinguishing information. |
| `T-A04` | Current deslavement, structural marginality, spark, basin birth, collapse, and tracking failure are distinct thresholds. | `core_inherited` + `core_derived` | Both controlling papers; B1-Cb-2.1/3 | Their nonlinear ordering is conditional. |
| `T-A05` | On a closed no-through-flow branch with positive nondegenerate mobility and regular gradient/potential current, a nonzero stationary current cannot be supplied by the dissipative gradient sector alone. | `core_derived` | B1-Cb-2 | `A-CLOSED`, `A-MOBILITY`, `A-CONSERVE`; circulation, harmonic/null sectors, boundary drive, or another mechanism remain possible. |
| `T-A06` | Tracking failure can occur while the instantaneous branch remains structurally and temporally stable. | `core_derived` | B1-Cb-3 | `A-BRANCH`, `A-CLOCK`, `A-ISOLATION`; requires finite branch forcing or slow-to-fast leakage. |
| `T-O01` | The scalar or joint retained sector does not yet canonically determine the directional one-form read-back response. | `open` | *Read-Back* open closure; B1-C | `A-ORIENTATION`; the Hodge/cochain construction remains a candidate. |
| `T-O02` | No universal generator yet unifies $\alpha$, $\gamma$, $\beta$, and discrete temporal multipliers. | `core_inherited` | Both controlling papers | A bounded common generator may be derived only under additional assumptions. |
| `T-O03` | Markov sufficiency of the declared present state remains open. | `core_inherited` | *Read-Back* | A positive claim requires `A-STATE-CLOSURE`; delay, phase, or history may require extra state. |

## 3.2 Decision use of the ledger

Every Part II result must cite one or more claim IDs and every required assumption ID.

A result may:

- support a claim within satisfied assumptions;
- show that a required assumption failed or was not identifiable;
- falsify a proposed graph correspondence;
- show that the construct is unidentifiable on the unchanged substrate;
- route the issue to a selectable GRC extension;
- route the issue to LGRC;
- or reopen a `core_derived` or candidate claim.

A claim must not be reported as falsified when one of its required assumptions failed or remained unidentifiable. The correct result is `not_admitted_under_tested_assumptions` unless a separate contradiction is established.

A result may not upgrade a `candidate_constitutive_completion` into substrate fact merely because the implementation resembles it.

## 3.3 Proof and derivation status

`core_derived` means that B1 supplied a derivation under stated assumptions; it does not mean that the result is already a theorem in the controlling papers. Appendix A records concise derivation notes for the highest-consequence derived claims.

The following proof statuses are permitted:

```text
inherited_explicit
derived_with_sketch
conditional_lemma
candidate_witness_class
open_problem
realization_specific
```

Every final claim artifact must cite the relevant proof-note identifier where one exists.

# 4. Causal role grammar and non-equivalence boundaries

## 4.1 Primitive, runtime, and analytical state

The mature primitive coherence state remains

$$
\mathcal S_{\mathrm{coh}}=(C,J_C).
$$

Neither retained structure nor the reconstructed read current is introduced as another primitive field.

Three state questions must remain separate:

$$
\boxed{
\text{core primitive state}
\neq
\text{runtime causal state}
\neq
\text{analytical perturbation state}.
}
$$

- The **core primitive state** states the intended ontology.
- The **runtime causal state** contains whatever a concrete implementation must retain to determine its next transition.
- The **analytical perturbation state** depends on a selected formed branch, constraints, clock, inner product, and the coordinates permitted to vary.

An extra runtime coordinate is not automatically another theoretical primitive or a retained sector. Conversely, a theoretical role may be realized without a separately serialized field.

## 4.2 Retention, read-back, and write-back

The controlling distinction is

$$
\boxed{
\text{retention}
\neq
\text{read-back}
\neq
\text{write-back}.
}
$$

- **Retention** is persistence of formed continuation under an explicitly declared persistence criterion.
- **Read-back** is the return of retained formation into present current activity.
- **Write-back** is present activity changing what is subsequently retained.

The reconstructed read-back class is

$$
\boxed{
j^\flat=
\mathfrak R_M
\bigl(\mathcal T_M,h;J_C^\flat\bigr),
\qquad
\mathfrak R_M(\mathcal T,h;0)=0
\text{ for every admissible }(\mathcal T,h).
}
$$

The passive-null condition is load-bearing:

$$
J_C=0\Longrightarrow j=0,
$$

while retained formation may remain nonzero.

## 4.3 Causal possibility matrix

The experiment must not require the complete loop before accepting evidence for one causal role.

| Retained formation present | Present retained-conditioned read | Activity changes later retained formation | Permitted interpretation |
|---|---|---|---|
| yes | no | no | persistent formation not currently read |
| yes | yes | negligible | elastic or reversible enactment through existing formation |
| forming or weak | no or weak | yes | initial cultivation before a strong read path exists |
| yes | yes | yes | closed reflexive read/write loop |
| no declared retained sector | state affects current | state changes | ordinary recurrence or geometry-conditioned transport; not yet retention/read-back |

The following are therefore valid findings:

$$
\boxed{
\text{read-back may exist without material persistent write-back,}
}
$$

and

$$
\boxed{
\text{write into a retained sector may precede strong read-back.}
}
$$

Failure to establish the full loop does not erase evidence for a bounded arrow. Conversely, evidence for one arrow does not establish the full loop.

## 4.4 Baseline current, direct read current, and effective feedback

The current architecture must be partitioned as

$$
\boxed{
J_C=J_0+\zeta_Cj,
}
$$

where:

- $J_0$ is ordinary baseline current under present coherence, geometry, tensor, boundary conditions, and non-read constitutive terms;
- $j$ is the explicit retention-conditioned directional response;
- the **effective read-back feedback** is the complete first-order closed path through $j$, $K$, geometry, retained-state response, and the total-current relation.

Let $X$ denote the declared non-current branch data and write the algebraic current closure as

$$
\boxed{
J=\Psi_X(J),
\qquad
\mathcal E_J(X,J)=J-\Psi_X(J)=0.
}
$$

At a branch $(X_*,J_*)$, define

$$
\boxed{
\mathcal B_{\mathrm{eff},*}
=
D_J\Psi_{X_*}(J_*),
\qquad
D_J\mathcal E_{J,*}=I-\mathcal B_{\mathrm{eff},*}.
}
$$

The partition between $X$ and $J$ must not hide current dependence. Any quantity such as $K$, $h$, $W$, retained response, or another constitutive intermediate that depends algebraically on $J$ must be eliminated into $\Psi_X(J)$, with its complete chain-rule contribution included in $D_J\Psi_X$, or explicitly declared frozen. A diagnostic that freezes such a path is a reduced-current or reduced-geometry comparison and must not be reported as the full effective loop.

If such a quantity instead carries independent state across temporal transitions rather than being algebraically determined by the instantaneous current closure, it belongs in the joint temporal state. In that case $\mathcal B_{\mathrm{eff},*}$ is only the algebraic current block of the full transition operator.

The direct channel $\zeta_C\mathcal R_{M,*}$ is one contribution to $\mathcal B_{\mathrm{eff},*}$. At an established active current, the full operator may also contain

$$
J\rightarrow j\rightarrow K\rightarrow h\rightarrow J_0,
$$

plus any retained-state response induced by the enacted current.

Local algebraic current slaving requires `A-LOOP-INVERT`:

$$
I-\mathcal B_{\mathrm{eff},*}
\text{ boundedly invertible}.
$$

On a frozen zero-background diagnostic where retained and geometric state are held fixed and no additional first-order current-dependent path survives,

$$
\mathcal B_{\mathrm{eff},*}
=
\zeta_C\mathcal R_{M,*}.
$$

Only in that reduced case is `A-LOOP-INVERT` equivalent to bounded invertibility of $I-\zeta_C\mathcal R_{M,*}$. In every non-reduced case, the full effective operator controls local slaving.

A stored geometry changing later baseline current may be ordinary geometry-conditioned transport, a retained-geometry recurrence, one path inside effective read-back, or a different reflexive mechanism. It is not automatically the explicit read current.

## 4.5 Retention acceptance contract

A positive retention claim requires all applicable conditions below.

1. A carrier or sector is declared before the outcome is inspected.
2. A preparation changes that carrier or its occupied content.
3. The preparation is then stopped or standardized.
4. Persistence is evaluated under a declared branch, clock, horizon, norm, and stability class.
5. If a slow sector is claimed, branch tangents and gauges are removed and the sector is isolated or its non-normal finite-horizon status is stated.
6. Transport still in flight, numerical staging, deterministic reconstruction from a faster state, and hidden forcing are excluded or separately classified.
7. Reset, swap, replacement, freeze, or bypass controls show that later effects follow the proposed carrier where a causal retention role is claimed.
8. Runtime-reachable and synthetic-valid preparations are reported separately under `A-REACHABLE`.

The permitted positive levels are:

```text
persistent_state_candidate
branch_relative_retention_candidate
dynamically_slow_retained_candidate
causally_mediating_retained_carrier
```

None of these alone establishes read-back.

## 4.6 Read-back acceptance contract

A candidate graph realization of read-back must satisfy all applicable conditions below.

1. A retained structure is selected by a criterion independent of the desired response.
2. A present current-like probe is identifiable.
3. The response is current-like or directionally transport-relevant.
4. `A-PASSIVE` holds under the declared present-current convention.
5. The response depends nontrivially on the retained structure.
6. Current direction or mode compatibility matters unless an isotropic limit is explicitly declared.
7. The retained carrier mediates the later response under reset, swap, freeze, replacement, or bypass controls.
8. A bounded locally solvable regime exists; any failure of `A-LOOP-INVERT` is reported separately.
9. Present total current can change later retained formation if full reflexive closure is claimed.

Generic state dependence, predictive performance, or historical correlation is insufficient.

## 4.7 Write-back acceptance contract

A positive write-back claim requires all applicable conditions below.

1. The activity or current term performing the write is identified.
2. A no-activity, matched-activity, or reduced-activity control is present.
3. The proposed retained carrier, retained content, retained basis, or branch parameter changes.
4. External parameter change, boundary change, numerical branch refitting, and passive drift are excluded or separately attributed.
5. The changed object is classified as fast, stable slow, neutral, or growing under the declared clock.
6. If **effective retained write** is claimed, the change enters a sector satisfying the retention contract.
7. If **reflexive write-back** is claimed, the changed retained structure later alters read-back or another established retained-conditioned response.

Ordinary continuity may form retained amplitudes before a strong read path exists. Read-back may also occur elastically with negligible persistent writing.

## 4.8 Status of the read current and the simplifying limit

The read current $j$ is functionally distinct from $J_C$, but it is not another independently conserved stream. It is a derived current-like contribution to the total coherence-current closure.

A substrate does not have to serialize a field named `j`. It may realize the role:

```text
explicitly
as an algebraically eliminated intermediate
as a distributed transition factorization
```

The factorization must nevertheless be recoverable.

The simplifying limit

$$
j=J_C
$$

intentionally declines to distinguish ordinary present activity from activity-through-retention. It is a legitimate declared reduction. It is not a derivation of the general relation and cannot test retention selectivity.

## 4.9 Zero-background perturbative order

Assume `A-PASSIVE`, `A-SMOOTH`, and `A-SIGN-EVEN`, and let

$$
J_{C,*}=j_*=0.
$$

Because the passive null holds identically for every admissible retained structure and geometry,

$$
D_{\mathcal T}\mathfrak R_M\big|_{J=0}=0,
\qquad
D_h\mathfrak R_M\big|_{J=0}=0.
$$

The first-order read response is therefore

$$
\boxed{
\delta j^\flat=\mathcal R_{M,*}\delta J_C^\flat.
}
$$

For the specifically sign-even structural channel $j\otimes j$, with no independent linear-$j$ term included in that channel,

$$
D_j(j\otimes j)\big|_{j=0}=0,
$$

while

$$
D^2_j(j\otimes j)\big|_{j=0}\neq0.
$$

Therefore:

$$
\boxed{
\text{linear present-current read response}
\neq
\text{second-order sign-even geometric inscription}.
}
$$

A graph path such as $J_e^2\rightarrow W_e^+$ may support an analogy to quadratic structural inscription. It does not by itself establish a first-order retained-conditioned read current.

## 4.10 Axis versus orientation

The transformations

$$
j\otimes j
$$

and

$$
J_e^2
$$

are invariant under current reversal:

$$
j\mapsto-j,
\qquad
J\mapsto-J.
$$

They can preserve magnitude and an unoriented axis. They cannot by themselves preserve or select current orientation.

Therefore:

$$
\boxed{
\text{axis retention}
\neq
\text{orientation retention}.
}
$$

A claim involving current branch selection, circulation orientation, or directional historical continuity requires an oriented one-form carrier, inherited current state, oriented boundary condition, chiral constitutive response, declared stochastic asymmetry, or another explicit orientation source.

## 4.11 Field-trajectory, current-level, and full reflexive equivalence

Three equivalence claims must remain separate.

### Field-trajectory equivalence

Two currents may generate the same coherence evolution if

$$
\operatorname{div}J^{(a)}=
\operatorname{div}J^{(b)}.
$$

They may differ by a divergence-free component.

### Current-level equivalence

The currents themselves agree after the declared bundle, edge-orientation, measure, and interspace identifications.

This preserves orientation, circulation, and current-dependent geometry.

### Full reflexive equivalence

The complete causal diagrams agree for

$$
J_C,
\quad j,
\quad K,
\quad h,
\quad
\text{retained write},
\quad
\text{and later current closure}.
$$

The hierarchy is

$$
\boxed{
\text{field-trajectory equivalence}
<
\text{current-level equivalence}
<
\text{full reflexive equivalence}.
}
$$

A reduced graph claim must state which level has been established. Equality of $C(t)$ is not enough when current itself is load-bearing.

## 4.12 Transport in flight, delay, and hidden history

Within the instantaneous core closure, present transport is represented by $J_C$. Retained formation is represented by a declared retained structure.

An earlier cause that remains active because transport, delay, queue phase, or another hidden carrier has not completed is not silently classified as retention.

If two states agree in all declared present coordinates but differ in future response because of omitted delay, event phase, or history, `A-STATE-CLOSURE` has failed.

This distinction becomes an explicit LGRC admission control.

## 4.13 Write levels and causal authorship

For a declared projector $P$,

$$
D_t(PC)=P\,D_tC+(D_tP)C.
$$

Three claim levels must remain separate.

1. **Projected sector update** — the exact product-rule identity once $P$ is declared.
2. **Effective retained write** — the changed component enters a sector satisfying the declared persistence criterion.
3. **Reflexive write-back** — the changed retained structure later modifies read-back or another established retained-conditioned response.

Total $J_C$, not only $j$, may form retained structure. Read-back can therefore be weak or absent during initial cultivation.

Projector drift, branch motion, or parameter change is not automatically activity-induced write-back. A causal attribution must distinguish

$$
\dot\theta=
\dot\theta_{\mathrm{external}}
+
\dot\theta_{\mathrm{activity}}.
$$

Only the activity-mediated part supports internally generated write-back.

Write-back does not imply permanence, monotonic reinforcement, or increasing memory.

## 4.14 Active-current birth and downstream events

The following remain distinct:

```text
regular algebraic current slaving
loss of current-block invertibility
temporal current-mode instability
structural continuation marginality
spatial basin birth
spark
collapse
```

Exact deterministic symmetric zero cannot choose an oriented branch under `A-UNIQUENESS` and `A-ORIENTATION` without a seed, bias, inherited orientation, boundary asymmetry, or declared stochasticity.

Collapse and spark remain downstream finite-organization events. They do not silently repair an unresolved current branch at fixed coherence state.

# 5. Retained sectors, clocks, and temporal persistence

## 5.1 Retention capacity, retained content, and history

The following must remain separate:

$$
\boxed{
\text{retention capacity}
\neq
\text{retained content}
\neq
\text{historical record}.
}
$$

- **Retention capacity** is a sector capable of persisting on a declared branch and horizon.
- **Retained content** is the current amplitude occupying that sector.
- **Historical record** stores how the content formed.

The core requires the first two. A full history ledger is required only if the present declared state does not contain all causally relevant historical information.

## 5.2 Spatial retained component

The inherited spatial component is

$$
C_M^{(\Delta)}=
P_M^{(\Delta)}C,
\qquad
P_M^{(\Delta)}=
\mathbf 1_{[0,\Lambda]}(-\Delta_h).
$$

This is a state-level component once the instantaneous field, geometry, measure, and cutoff are declared.

Low spatial frequency does not prove slow temporal response. A graph Laplacian projector therefore remains a spatial-retention candidate unless a dynamical correspondence is separately shown.

## 5.3 Dynamically retained perturbation

Around a formed branch $C_*$, let

$$
u=C-C_*.
$$

On the declared self-adjoint relaxation branch,

$$
P_{M,u}
=
T_*^{-1}
\mathbf 1_{[0,\Gamma_M]}
(\widetilde{\mathscr G}_*)T_*,
$$

and

$$
u_M^{(\mathrm{dyn})}=P_{M,u}u.
$$

This object is:

- branch-relative;
- closure-relative;
- representation-relative;
- horizon-relative;
- clock-relative;
- and dependent on a retained-cluster isolation gap.

It is not intrinsic state data on the same footing as $C$.

## 5.4 Dynamic retention belongs to the executed temporal law

A dynamically retained sector cannot be defined from one relaxation closure and inserted into any other current law.

For a graph map with joint transition Jacobian $A_*$, an isolated temporal slow cluster may instead be represented by a Riesz projector:

$$
P_M^{\mathrm{loop}}
=
\frac{1}{2\pi i}
\oint_\Gamma
(zI-A_*)^{-1}\,dz.
$$

This is initially an analytical object. It becomes constitutive only if the runtime itself reads that selected sector.

The clock or beat defining temporal persistence must be declared. For GRC this is initially the complete synchronous step. For LGRC, one event is not automatically one reflexive beat.

## 5.5 Stable retention, neutrality, and formative instability

A slow sector must distinguish stable persistence from growth.

For continuous rates:

| Rate | Meaning |
|---|---|
| $0<\gamma\le\Gamma_M$ | stable, slowly relaxing continuation |
| $\gamma=0$ | exact neutrality or marginality requiring separate classification |
| $\gamma<0$ under the paper's decay-sign convention | growing formative instability |

For discrete multipliers:

| Multiplier | Meaning |
|---|---|
| $\lvert\mu\rvert<1$ and close to one | stable slow persistence |
| $\lvert\mu\rvert=1$ | temporal marginality or exact neutral/oscillatory behavior |
| $\lvert\mu\rvert>1$ | growth or instability |

A slowly growing mode may remain visible for a long time. It is not thereby stable retained formation.

## 5.6 Horizon-relative and non-normal persistence

Under strong non-normality, eigenvalues may not characterize finite-time survival.

For a propagator

$$
\Phi_{k+\tau,k}
=
A_{k+\tau-1}\cdots A_k,
$$

a finite-horizon survival operator is

$$
\mathcal C_{k,\tau}
=
\Phi_{k+\tau,k}^{*}
\Phi_{k+\tau,k}.
$$

Its singular subspaces depend on:

- the horizon $\tau$;
- the norm;
- the branch path;
- and potentially future states.

They are generally analysis objects.

A runtime extension may not feed a retrospective or future-dependent slow subspace back into present execution unless the runtime itself declares and possesses the required predictive state or schedule.

## 5.7 Self-consistent dynamic retention

If read-back depends only on a state-level retained component, the temporal generator may be formed first and its dynamic slow sector calculated afterward.

If read-back depends on the dynamically selected slow sector itself, then a fixed-point closure is required:

$$
P_*=
\Pi_{\mathrm{slow}}
\bigl(
\mathscr A_*[P_*]
\bigr).
$$

A local solution requires:

- an isolated slow cluster;
- smooth dependence on $P$;
- and invertibility of the fixed-point derivative.

This is a `core_derived` conditional construction. The exact nonlinear closure remains open.

Loss of spectral isolation and loss of fixed-point uniqueness are different failures.

---

# 6. Continuation, relaxation, read-back, and formed-branch compatibility

## 6.1 Operator hierarchy

The following are different operators on different spaces:

| Object | Space | Meaning |
|---|---|---|
| $-\Delta_h$ or graph Laplacian | spatial scalar field | spatial scale |
| $\mathscr H_*$ | constrained configuration tangent | structural continuation curvature |
| $\widetilde{\mathscr G}_*$ | declared relaxation representation | decay or growth rate on that temporal branch |
| $\mathcal R_M$ | current one-forms | direct read response |
| $\mathcal B_{\mathrm{eff},*}$ | declared current-loop space | complete local current-loop feedback |
| runtime transition Jacobian or return map | runtime causal state | temporal multipliers and mode coupling |
| spatial Hessian | spatial coordinates | local shape and basin diagnostics |

No equality or index correspondence is inherited among them.

## 6.2 Continuation curvature

The constrained continuation operator is

$$
\mathscr H_*
=
\Pi_*D^2(\widehat{\mathcal P}-\eta Q)[C_*]\Pi_*,
$$

with

$$
\mathscr H_*u_n=\alpha_nu_n.
$$

The controlling paper derives this on a no-current, frozen-current, or smoothly slaved-current branch under `A-BRANCH`, `A-SMOOTH`, and `A-CONSERVE`.

A general independently variable active-current continuation object remains open and need not ultimately be a self-adjoint Hessian. It may require a joint transition operator, differential-algebraic pencil, or another local branch object.

## 6.3 Relaxation

On the declared conserved-density gradient-flow branch,

$$
\widetilde{\mathscr G}_*
=
\mathscr A_{\rho,*}^{1/2}
\mathscr H_{\rho,*}
\mathscr A_{\rho,*}^{1/2},
$$

with eigenvalues $\gamma_n$.

The relaxation spectrum is not universal across all current laws. Mobility, density representation, current closure, and clock are part of its definition.

A small $\gamma$ does not prove small $\alpha$. It may result from low mobility or another kinetic bottleneck. Structural marginality produces critical slowing only under the nondegeneracy assumptions of the declared relaxation branch.

## 6.4 Read-back response and effective current loop

Around a fixed retained/current branch,

$$
\delta j^\flat
=
\mathcal R_{M,*}\delta J_C^\flat.
$$

In the narrow zero-background diagnostic,

$$
(I-\zeta_C\mathcal R_{M,*})
\delta J_C^\flat
=
\delta J_0^\flat.
$$

The direct gain belongs to $\zeta_C\mathcal R_{M,*}$. At an established active current, the complete local threshold belongs to

$$
\mathcal B_{\mathrm{eff},*}=D_J\Psi_{X_*}(J_*),
$$

which may include direct read response, $j\rightarrow K\rightarrow h\rightarrow J_0$, retained-state response, and any other declared constitutive path.

`A-LOOP-INVERT` is the precise local slaving condition:

$$
I-\mathcal B_{\mathrm{eff},*}
\text{ boundedly invertible}.
$$

The spectra $\alpha$, $\gamma$, $\beta$, and runtime multipliers are not currently spectra of one established universal generator.

## 6.5 Structural formation and dynamic realization

A structurally formed state satisfies the constrained critical-point conditions of the declared branch.

A dynamically formed state must also be invariant or appropriately tracked under the selected temporal closure.

A positive structural gap does not by itself prove attraction under every current law. A stable temporal multiplier does not by itself prove positive structural continuation curvature.

## 6.6 Common zero-background branch

B1 derived a conditional common reference branch satisfying, schematically,

$$
\begin{aligned}
D\mathcal F_0[C_*]&=0,\\
Q[C_*]&=Q_0,\\
J_{0,*}&=0,\\
J_{C,*}&=0,\\
j_*&=0,\\
h_*&=\mathcal H(K_*),\\
I-\mathcal B_{\mathrm{eff},*}&\text{ boundedly invertible}.
\end{aligned}
$$

This compatibility class is nonempty under an explicit witness envelope. Let the geometry be fixed and regular on a connected compact/no-flux domain or finite graph analogue, let

$$
C_*=c
$$

be constant with the declared conserved budget, and choose the constraint multiplier so that the first variation vanishes. Then

$$
\nabla C_*=0,
\qquad
J_{0,*}=0.
$$

`A-PASSIVE` gives $j_*=0$. The branch must satisfy `A-LOOP-INVERT` for the full effective block. In the explicitly frozen zero-background reduction, where no other first-order current-dependent path survives, this reduces to bounded invertibility of $I-\zeta_C\mathcal R_{M,*}$. Any bounded passive $\mathcal R_{M,*}$ satisfying that reduced condition may be evaluated at the same reference state. Where the structural Hessian is positive on the constrained tangent, the continuation spectrum is also defined there.

This proves only that a nonempty common zero-background reference class exists under the declared assumptions. It does not prove existence for every nonuniform identity, one common temporal generator, or one unique metric/read-back closure.

## 6.7 Algebraic read-back as a temporal fast limit

The instantaneous current closure can be written as

$$
J=\Psi_X(J),
\qquad
\mathcal E_J(X,J)=J-\Psi_X(J)=0.
$$

A minimal discrete temporal completion is the candidate class

$$
J_{k+1}
=
(1-\vartheta)J_k
+
\vartheta\Psi_{X_k}(J_k).
$$

Its fixed points recover the algebraic closure. Under `A-SMOOTH`, `A-LOOP-INVERT`, and `A-FAST-SLOW`, a normally attracting fast-current branch admits algebraic slaving as a reduced limit.

This residual-relaxation map is a `candidate_constitutive_completion`, not a unique core law. A repository experiment must not treat similarity to this map as the only route to temporal current realization.

## 6.8 Active stationary branch

For a closed stationary system under `A-CLOSED` and `A-CONSERVE`,

$$
\operatorname{div}_hJ_*=0.
$$

If the current is regular positive-mobility gradient or potential flow under `A-MOBILITY`, its dissipative gradient component vanishes at a closed stationary state. A nonzero stationary current therefore requires a circulation, harmonic or mobility-null sector, boundary-maintained through-flow, or another current mechanism.

A nonzero active current does not automatically require a joint state if the full constitutive current block remains locally invertible. A joint or differential-algebraic description becomes necessary when current amplitude, orientation, phase, or branch choice remains independently variable.

Boundary-maintained through-flow is a different open stationary branch and must be classified separately.

## 6.9 Critical current modes and exact zero

Under `A-SMOOTH` and `A-REGULAR-SLAVING`, bounded invertibility of the algebraic current block permits local elimination of current. If the block loses invertibility, the regular implicit elimination fails for the corresponding critical direction.

The correct conclusion is limited:

$$
\boxed{
\text{the critical direction cannot be removed by the same regular slaving construction.}
}
$$

A claimed passage through that threshold must retain the critical amplitude as an explicit local coordinate or provide another justified higher-order resolution. The theory does not thereby select one temporal map or require the whole current field to become independently dynamical.

Under `A-UNIQUENESS` and `A-ORIENTATION`, exact deterministic symmetric zero remains unable to select one reversal-related orientation without a seed, bias, inherited oriented state, boundary asymmetry, or declared stochasticity. Instability amplifies available perturbations; it does not create distinguishing information from none.

## 6.10 Tracked active branch

For a discrete graph map

$$
X_{k+1}=F_{\theta_k}(X_k),
$$

with moving reference branch $X_{*,k}$ and perturbation $z_k=X_k-X_{*,k}$,

$$
\boxed{
z_{k+1}
=
A_kz_k-d_k+O(\|z_k\|^2),
}
$$

where $d_k$ is the branch-tracking defect.

Branch tangents, retained slow deviations, and fast tracking errors must be separated. Under `A-BRANCH`, `A-CLOCK`, and `A-ISOLATION`, a trajectory can still fail to track a stable instantaneous branch if branch motion or slow-to-fast leakage exceeds fast contraction.

Tracking failure is distinct from structural marginality, read-back singularity, slow-cluster gap closure, spark, and collapse.

# 7. Branch, mode, clock, and transport boundaries

## 7.1 Four reference objects

The following must remain separate:

1. a **formed structural state** — one constrained critical point;
2. a **formed structural branch** — a smooth family of such states;
3. a **tracked reference branch** — a branch supplied with a parameter or time path;
4. the **actual trajectory** — the runtime state evolving near or away from that reference branch.

A formed structural state is not automatically invariant or attracting under every temporal closure.

## 7.2 Predeclared branch selection

Because retained perturbation is defined relative to a branch,

$$
u=C-C_*,
$$

changing the reference branch changes what appears retained.

Under `A-BRANCH`, the branch-selection rule must be declared before evaluating slow content. It may use a continued fixed branch, an externally declared parameter path, a modulation condition, or another independently specified rule.

It may not be chosen retrospectively to minimize residual or maximize apparent retention.

When a family has neutral tangent or symmetry directions, a phase or modulation condition must separate branch motion from perturbation.

## 7.3 Branch tangents, gauges, and retained modes

A tracked local state should separate

$$
E_B
\oplus
E_M
\oplus
E_F
\quad
(\oplus E_U\ \text{if present}),
$$

where:

- $E_B$ contains branch-tangent and declared gauge directions;
- $E_M$ contains stable slow retained deviations transverse to the branch;
- $E_F$ contains fast stable tracking error;
- $E_U$ contains unresolved unstable directions.

A zero or unit multiplier is not automatically retention. It may be branch motion, symmetry, conservation, exact neutrality, or instability.

## 7.4 Individual modes and clusters

Under `A-ISOLATION`, an individual mode may be tracked only while its eigenvalue or multiplier is simple and isolated.

Near degeneracy, the invariant continuing object is the spectral subspace or projector, not an index such as “mode 3” independently sorted at each step.

Subspace comparisons must use `A-TRANSPORT` together with principal angles, projector distances, an intertwining map, or another invariant cluster-level measure.

## 7.5 Kato transport after ambient identification

A changing state metric or branch requires `A-TRANSPORT`: an ambient state-space identification or connection must be declared before modes are compared.

For fixed-topology GRC, the default ambient map is the coordinate identity on the canonical chart declared in Sections 2.4.3 and 18.4. If the inner product, node/edge measure, or state metric changes, a fixed-reference inner-product representation, isometry, congruence, or normalization must also be declared before orthogonality or self-adjointness is used.

After transport into one fixed Hilbert-space representation, let $P(t)$ be a differentiable family of orthogonal projectors. The Kato generator

$$
\boxed{
\mathcal K_t=[\dot P(t),P(t)]
}
$$

defines the parallel transport $W(t,t_0)$ by

$$
\partial_tW=\mathcal K_tW,
\qquad
W(t_0,t_0)=I,
$$

with the intertwining property

$$
P(t)W(t,t_0)=W(t,t_0)P(t_0).
$$

This transport is canonical only relative to the already declared ambient identification, inner product, and orthogonal-projector convention. It is not a canonical map between otherwise unidentified changing state spaces, does not prove that the runtime transports a retained projector, and does not solve topology-changing transport.

## 7.6 Topology-changing interspace transport

When graph topology, dimension, or support changes,

$$
\mathcal H_k\neq\mathcal H_{k+1}.
$$

A claim that a branch state, current orientation, mode, or retained sector survives requires an explicit interspace map

$$
U_{k\rightarrow k+1}:
\mathcal H_k\rightarrow\mathcal H_{k+1}.
$$

Lineage, node ancestry, endpoint redirection, or packet rerouting may contribute to such a map. None is automatically the canonical continuation or retained-sector transport.

This issue is deferred to LGRC, but the requirement is frozen here.

## 7.7 Clock and beat declaration

Every temporal claim must satisfy `A-CLOCK`.

For unchanged GRC, the initial beat is one complete synchronous `GRC9V3.step()` including both transport refreshes.

For LGRC, the relevant beat may be one event, one route cycle, a queue-drained return, a proper-time interval, or another declared Poincaré section.

Event order, event time, proper time, and causal delay must not be silently merged.

## 7.8 Branch motion and causal write authorship

A moving branch may be caused by external parameter change, current or coherence writing retained geometry, boundary change, topology change, or numerical branch fitting.

Only an established activity-mediated path supports internally generated branch write-back.

Returning to the same endpoint projector does not necessarily erase path-dependent retained content inside a multidimensional slow cluster. If that content is not represented in the declared present state but changes future response, `A-STATE-CLOSURE` has failed.

# 8. Theory-to-graph correspondence and decision standard

## 8.1 Seven assessment axes

Every proposed graph correspondence must be assessed on seven axes.

| Axis | Question |
|---|---|
| Representation | Does a graph object carry the required information and type? |
| Causal role | Does it affect execution at the required place in the loop? |
| Derivation | Is it derived from the core equations or only proposed? |
| Identifiability | Can it be distinguished from rival mechanisms? |
| Reduction envelope | Which topology, branch, clock, and frozen or slaved assumptions are required? |
| Assumption status | Which required assumptions are satisfied, failed, unidentifiable, inapplicable, or deferred? |
| Claim ceiling | What is the strongest statement supported by evidence? |

## 8.2 Realization form

A theoretical role may be:

```text
explicitly realized
algebraically eliminated
distributed across transition stages
represented only diagnostically
absent
unidentifiable under current evidence
```

Inventory alone cannot distinguish these. Causal counterfactuals, factorization, or derivation are required.

An explicit variable with a familiar name does not establish the role. Absence of an explicit variable does not prove the role is absent.

## 8.3 Correspondence levels

| Level | Permitted claim |
|---|---|
| `L0 analogy` | The substrate contains a suggestive resemblance. |
| `L1 representability` | The substrate state can carry a correctly typed candidate object. |
| `L2 operational signature` | Controlled evidence distinguishes the candidate from some rival mechanisms. |
| `L3 constitutive realization` | Interventions establish the required causal factorization. |
| `L4 derived reduced limit` | A declared mathematical reduction connects the core and graph equations. |
| `L5 robust realization` | The mapping survives parameter, relabeling, branch, and held-out stress within scope. |

Operator performance does not substitute for construct validity. Predictive success alone cannot establish read-back.

## 8.4 Required nulls and rival explanations

| Proposed claim | Required rival explanation |
|---|---|
| Retention | ordinary persistent state, slaved state, growth, or slow kinetics |
| Read-back | generic state-dependent or geometry-conditioned transport |
| Write-back | ordinary continuity, passive drift, or exogenous branch motion |
| Dynamic retention | low mobility, timestep choice, numerical staging, delay, growth, or non-normal transient |
| Active-current memory | current reconstructed anew from present potential |
| Orientation retention | sign-even axis or magnitude inscription |
| Continuation softness | local spatial smoothness or local Hessian degeneracy |
| Joint-state necessity | redundant stored values reconstructable from a smaller state |
| Historical influence | unfinished transport, event phase, or producer/policy input |
| Topological retention | lineage or endpoint reassignment without an interspace continuation map |
| Full reflexive equivalence | field-only equality or current equality without matching geometry and write path |

## 8.5 Theory acceptance, substrate realization, and identifiability

The following are different outcomes:

```text
theory claim accepted within assumptions
substrate realizes the claim
substrate can measure a candidate object
experiment can identify the causal role
```

A theoretically accepted claim may be absent from a substrate. A substrate may expose a measurable object without reading it constitutively. A mechanism may exist but remain unidentifiable under available interventions. These outcomes must not be collapsed into one status.

## 8.6 Claim combination rules

The following inference rules are forbidden:

```text
slow -> retained
persistent -> historical
history-sensitive -> read-back
state affects current -> read-back
current changes geometry -> full write-back
J^2 or j tensor -> orientation retention
same C trajectory -> same current mechanism
nonzero recurrent current -> active stationary circulation
spatial Hessian threshold -> continuation marginality
unit multiplier -> spark or collapse
lineage -> retained-mode survival
good predictive performance -> construct validity
failed assumption -> falsified claim
```

## 8.7 Typed graph one-form bridge requirements

A graph-native read-back claim must declare a typed bridge from retained scalar, conductance, basin, or joint state into an oriented edge-current space.

A minimal candidate has the form

$$
\boxed{
\mathfrak R_G:
\mathcal T_M^G\times H_G\times C^1(E)
\longrightarrow
C^1(E),
}
$$

where $C^1(E)$ is the declared oriented edge-cochain space.

The candidate must state:

1. node and edge ordering;
2. edge orientation and the reorientation action $S=\operatorname{diag}(\pm1)$;
3. incidence/divergence operator and edge inner product or measure;
4. orientation covariance, schematically
   $$
   \mathfrak R_G(\mathcal T,H;SJ)=S\,\mathfrak R_G(\mathcal T,H;J)
   $$
   after all oriented inputs are transformed consistently;
5. the decomposition, where relevant, into gradient/cut-space and cycle/harmonic current sectors;
6. `A-PASSIVE`;
7. whether the carrier preserves magnitude, axis, orientation, branch selection, or only some of these;
8. whether the output is baseline current, the explicit read current, or one path inside $\mathcal B_{\mathrm{eff}}$;
9. carrier mediation and reset/swap/bypass controls;
10. `A-TRANSPORT` if the graph or branch changes.

This section does not choose a unique bridge. It makes `D-R03` falsifiable by type and covariance before performance is considered.

## 8.8 Decision routes

Every unresolved result must route to exactly one primary next action:

```text
unchanged_grc_interpretation
analysis_only_measurement
selectable_grc_extension
lgrc_specific_investigation
theory_revision_or_reopening
blocked_by_identifiability
```

A secondary route may be recorded, but the primary route controls the closeout.

# 9. Open theory and realization debt

## 9.1 Debt register

| Debt ID | Open issue | Claim blocked | What may still be measured | Primary GRC decision route | LGRC relevance | Closure or reopening condition |
|---|---|---|---|---|---|---|
| `D-R01` | Exact nonlinear $\mathfrak R_M$ | No unique native read-back operator | response classes, passive null, mediation, gains | selectable extension only after role evidence | event return map may realize delayed response | derive a constitutive class or accept realization-specific family |
| `D-R02` | Exact retained projector and cutoff | No canonical runtime retained sector | spatial, temporal, and joint candidate sectors | analysis-only until a carrier is justified | clock and delay make selection harder | branch-, clock-, and horizon-specific criterion accepted |
| `D-R03` | Scalar or joint retained sector to oriented edge-current bridge | No canonical $\alpha_n\leftrightarrow\beta_a$ or slow-mode-to-current map | type, covariance, mode participation, and causal mediation | oriented read extension only if Section 8.7 requirements are met | packets preserve direction but may remain transport | derive or specify a bridge satisfying the typed cochain contract |
| `D-G01` | Exact metric map $h[K]$ and sign of back-reaction | No universal stiffening, softening, or reinforcement claim | branch-specific sensitivity | clarify legacy mechanism or selectable geometry extension | topology and delay may add metric roles | branch-specific closure with tested sign and invariants |
| `D-G02` | Geometry versus mobility relation | No clean attribution of $\alpha$ versus $\gamma$ when one carrier does both | frozen/full comparisons and causal blocks | geometry-mobility split if ambiguity is load-bearing | LGRC adds clocks and delays but inherits GRC conflation | independent carriers or justified factorization |
| `D-C01` | General active joint continuation object | No automatic promotion of runtime Jacobian to core $\mathscr H_*$ | transition Jacobian, Floquet map, structural comparator | analysis-only or later extension | event return map may be the temporal object | derive the active branch object under declared closure |
| `D-C02` | Unified temporal generator | No universal merger of $\alpha,\gamma,\beta,\mu$ | separate operators and bounded common reductions | keep separate in GRC report | LGRC requires return-map-specific rates | derive a common generator under explicit assumptions |
| `D-M01` | Markov sufficiency | No assumption that queues, delay, phase, or history are redundant | closure tests on declared state | enlarge state only when counterexample exists | central LGRC question | matched present states with different futures identify missing state |
| `D-M02` | Non-normal persistence criterion | No unique active retained projector | Riesz clusters, propagators, singular directions | analysis-only initially | event maps may be strongly non-normal | accepted horizon and constitutive-status rule |
| `D-A01` | Current-branch passage and temporal current law | No unique active-current update | current Jacobian, seed amplification, return maps | selectable GRC extension only if targeted | LGRC may realize event-driven current loops | derive or specify a temporal map with correct fixed and fast limits |
| `D-T01` | Topology-changing state and mode transport | No canonical continuation through refinement | lineage and endpoint correspondences | not a GRC fixed-topology issue | mandatory before LGRC topology claims | explicit interspace transport with invariants |
| `D-B01` | Global branch tracking and branch intersections | No global identity theorem from local continuation | local fixed branches and tracking defects | analysis-only | topology and events add branch jumps | local rules accepted or global theorem derived |
| `D-P01` | Dynamic-projector/read-back fixed point | No automatic use of dynamic slow sector as constitutive memory | sensitivity of operator to candidate projector | defer unless runtime reads slow sector | delayed return maps may create stronger circularity | isolated cluster and fixed-point regularity established |

## 9.2 Decision consequences

An open debt does not block all work. It limits the claim.

Examples:

- `D-R02` permits measuring slow clusters but blocks calling one “the retained sector” without a declared criterion.
- `D-G02` permits documenting a load-bearing scalar conductance but blocks attributing a spectral change uniquely to structure or kinetics.
- `D-M01` permits a compact GRC state if closure tests pass but requires extra LGRC state if matched present states diverge because of queue or phase.
- `D-T01` permits fixed-topology GRC analysis but blocks any LGRC claim that lineage alone preserves continuation modes.

## 9.3 Theory-reopening protocol

When repository evidence conflicts with a B1 result:

1. freeze the exact branch, fixture, code SHA, and evidence;
2. identify the controlling claim ID and debt ID;
3. distinguish nonrealization, mapping error, overstrong derivation, non-identifiability, and numerical failure;
4. state whether the conflict affects `core_inherited`, `core_derived`, or only a candidate completion;
5. update the corrected specification without changing historical evidence;
6. open a separate theory revision only where the conflict reaches an inherited core assumption.

Negative substrate evidence must not be forced into a substrate extension if the more accurate result is that the proposed mapping was wrong.

---

# 10. Theory-to-test traceability

Every scientific gate must report against this matrix.

| Claim or debt | Required assumptions | Primary gate | Required control | Maximum positive claim | Negative or ambiguous result means | GRC extension route | LGRC route | Reopen condition |
|---|---|---|---|---|---|---|---|---|
| `T-S02`, `D-M01` | `A-STATE-CLOSURE`, `A-REACHABLE` | `GRV3` | matched-state closure tests; reached and synthetic states separated | branch-specific runtime causal state | smaller state may suffice, assumption fails, or state is unidentifiable | enlarge state only if closure fails | test queue, delay, phase, proper-time state | same accepted present state, different future |
| `T-RW01`, `T-RW06`, `T-RW11` | `A-BRANCH`, `A-CLOCK`, `A-REACHABLE` | `GRV5`, `GRV8` | retention, read, write, reset, swap, and authorship evaluated separately | bounded arrow or closed-loop evidence | absence of one arrow does not erase others | carrier or read extension only for missing role | separate transit, retention, and native read | causal-role matrix cannot classify outcome |
| `T-RW02`, `T-RW07` | `A-PASSIVE`, `A-SMOOTH`; `A-LOOP-INVERT` for slaving | `GRV5` | zero-present-probe and matched-retained-state controls | passive retained-conditioned response candidate | generic geometry-conditioned transport, failed null, or no read path | oriented read extension only if target requires it | event-driven native read test | passive-null convention cannot be implemented |
| `T-RW08` | `A-PASSIVE`, `A-SMOOTH`, `A-SIGN-EVEN` | `GRV1`, `GRV5` | linear current perturbation and quadratic sign-even write compared | first- versus second-order channel separation | assumption failure, channel conflation, or different mechanism | no extension unless target needs missing order | packet orientation may preserve first-order state | source contradicts perturbative classification |
| `T-RW09` | `A-ORIENTATION`, `A-SIGN-EVEN` | `GRV1-D`, `GRV5`, `GRV6` | $J$ versus $-J$ and cycle-orientation controls | magnitude, axis, or orientation semantics | orientation is reconstructed, erased, or convention is invalid | oriented one-form/cycle channel | packet/route orientation investigation | sign control changes through hidden state |
| `T-RW10` | `A-ORIENTATION`, `A-CONSERVE`, `A-TRANSPORT` where needed | `GRV6` | compare divergence, current, geometry, and future state | field-, current-, or full-level equivalence | field match is insufficient | cycle-current extension only if required | return-map/current equivalence | equivalence level cannot be isolated |
| `T-M01`, `T-C01` | `A-BRANCH`, `A-CLOCK`, `A-CONSERVE` | `GRV4`, `GRV7` | spatial, frozen structural, and full temporal operators compared | bounded relation or non-equivalence | no universal identification | analysis comparator only | preserve same distinction | verified universal relation contradicts boundary |
| `T-M02`, `T-M03`, `D-M02` | `A-BRANCH`, `A-CLOCK`, `A-ISOLATION`, `A-NONNORMAL-CONTROL` as applicable | `GRV3`, `GRV5`, `GRV6` | stable/neutral/unstable classification and finite-horizon controls | branch- and clock-specific slow cluster | growth, staging, delay, or non-normal transient | analysis first; constitutive carrier later | return-map slow sector | no declared clock explains result |
| `T-C02`, `T-C03` | `A-BRANCH`, `A-SMOOTH`, `A-CONSERVE` | `GRV2`, `GRV4` | strong branch, fixed-$W$, and full-map comparison | reduced structural comparator and dynamic branch classification | reduction fails or branch is not dynamically formed | geometry/mobility or branch extension | inherit accepted baseline | source-level sign or branch assumptions fail |
| `T-B02`, `T-B03` | `A-BRANCH`, `A-ISOLATION`, `A-TRANSPORT` | `GRV2`, `GRV3`, `GRV6` | branch rule fixed before spectrum; cluster-level matching | branch-relative mode or subspace evidence | labels are non-invariant or branch fit is retrospective | analysis transport only | needed for event return maps | results depend on retrospective branch fit |
| `T-B04`, `D-T01` | `A-TRANSPORT` | Part III only | explicit interspace map and lineage null | topology-relative continuation candidate | lineage is identity bookkeeping only | none in fixed GRC | mandatory LGRC gate | topology claim attempted without transport |
| `T-A01`, `T-A02`, `D-A01` | `A-SMOOTH`, `A-REGULAR-SLAVING`, `A-LOOP-INVERT`, `A-FAST-SLOW` as applicable | `GRV3`, `GRV6` | current Jacobian, seed, saturation, fixed/return map | temporal current semantics of unchanged GRC | current is overwritten, sign-even, potential-derived, or assumptions fail | selectable temporal/current extension if targeted | event-cycle return map | algebraic fast-limit interpretation contradicted |
| `T-A03`, `T-A04` | `A-UNIQUENESS`, `A-ORIENTATION` | `GRV6`, `GRV8` | exact-zero, finite-seed, sign, spark/collapse exclusion | seed amplification or threshold separation | no autonomous ignition claim | do not add selection unless target requires it | producer/event asymmetry distinguished | exact zero leaves under satisfied symmetry assumptions |
| `T-A05` | `A-CLOSED`, `A-MOBILITY`, `A-CONSERVE` | `GRV6` | closed cycle-current and boundary-drive controls | exclusion of regular gradient stationary circulation | boundary or null-sector alternative remains | cycle-current extension only if targeted | packet through-flow separated from closed circulation | nonzero closed gradient current under satisfied assumptions |
| `T-O01`, `D-R03` | `A-ORIENTATION`, `A-PASSIVE` | `GRV5`, `GRV8` | Section 8.7 typed scalar/joint-to-edge mediation | operational bridge candidate | no canonical read channel | oriented read extension only after evidence | packet direction remains transit until mediation shown | a unique bridge is derived |
| `T-O02`, `D-C02` | branch-specific | `GRV3`, `GRV4`, `GRV6` | separate spectra and full-map comparison | bounded common reduction | keep objects separate | no unified API or runtime label | return-map-specific generator | one generator derived and validated |
| `T-O03`, `D-M01` | `A-STATE-CLOSURE`, `A-REACHABLE` | `GRV3`, `GRV5`, Part III | matched present-state counterfactuals | bounded Markov sufficiency | missing history or phase | add state only if synchronous GRC needs it | central LGRC admission question | future differs under identical accepted state |

The final report must include this matrix with assumption statuses, a result, and a route filled for every row.

# 11. Theory freeze for this verification

The unchanged-GRC verification shall use the following theoretical contract.

1. Every claim is conditional on its registered assumptions; failed or unidentifiable assumptions do not equal falsified theory.
2. Retention, read-back, and write-back remain distinct and are evaluated arrow by arrow.
3. Evidence for one arrow does not establish or require the complete reflexive loop.
4. $j$ is a derived retention-conditioned current contribution, not another primitive conserved current.
5. `A-PASSIVE` is mandatory for an explicit read-back claim.
6. Baseline current, direct read current, and effective closed-loop feedback remain separate.
7. A low spatial mode is not automatically dynamically retained.
8. A dynamically retained sector belongs to the temporal closure, branch, clock, representation, and horizon actually executed.
9. Stable slow persistence, exact neutrality, and growth remain distinct.
10. $\alpha$, $\gamma$, $\beta$, graph transition multipliers, and spatial Hessians remain distinct objects.
11. Linear read response and sign-even quadratic current inscription remain distinct at zero background under `A-PASSIVE`, `A-SMOOTH`, and `A-SIGN-EVEN`.
12. Sign-even magnitude or tensor inscription does not establish current orientation retention.
13. Field-trajectory equivalence does not establish current-level or full reflexive equivalence.
14. A formed structural branch is not automatically dynamically invariant or attracting.
15. The reference branch and branch gauge must be declared before retained perturbations are evaluated.
16. Individual mode identity is not retained through degeneracy; cluster or projector identity is required.
17. Loss of current-block invertibility proves failure of regular algebraic elimination, not one unique temporal completion.
18. Exact deterministic symmetric zero requires a seed or bias to select an oriented active branch under `A-UNIQUENESS` and `A-ORIENTATION`.
19. Current-loop marginality, structural marginality, temporal map marginality, spark, basin birth, collapse, retained-cluster reclassification, and tracking failure remain distinct.
20. A discrete graph map is the primary temporal object for GRC; no PDE is required.
21. A moving or finite-horizon slow bundle is initially analytical unless the runtime reads it constitutively.
22. Projector drift, branch motion, and externally imposed context change do not automatically constitute activity-induced write-back.
23. Kato transport is valid only after an ambient identification has been declared; it does not solve topology-changing transport.
24. Topology-changing continuation requires an explicit interspace transport; lineage alone is insufficient.
25. A graph-native read-back candidate must satisfy the typed oriented-cochain contract of Section 8.7.
26. Open theory debts constrain claims but do not preselect implementation.
27. Repository evidence may reopen `core_derived` or candidate claims under the backward-correction protocol.
28. No result in Part II may silently select N32, L04, a `pygrc.analysis` architecture, a native read-back extension, or an LGRC implementation.

---

# Appendix A — Derivation-status notes for selected B1 claims

This appendix is normative for proof status and claim ceiling. It is not a substitute for a standalone core paper and does not upgrade B1 derivations into `core_inherited` results.

## A.1 `PN-RW08` — zero-background perturbative order

**Claim:** `T-RW08`  
**Assumptions:** `A-PASSIVE`, `A-SMOOTH`, `A-SIGN-EVEN`.

Because $\mathfrak R_M(\mathcal T,h;0)=0$ identically over admissible $(\mathcal T,h)$, differentiation in retained-state and geometry directions at zero current gives zero. Hence the first nonzero read variation is

$$
\delta j=D_J\mathfrak R_M\big|_*\delta J.
$$

For the specifically even structural channel $F(j)=j\otimes j$,

$$
DF(0)=0,
\qquad
D^2F(0)[p,q]=p\otimes q+q\otimes p.
$$

**Claim ceiling:** first-order read and second-order sign-even inscription are distinct channels. No claim is made for a geometry law containing an independent linear-$j$ term.

## A.2 `PN-RW09` — axis is not orientation

**Claim:** `T-RW09`  
**Assumptions:** `A-ORIENTATION`, `A-SIGN-EVEN`.

For any oriented current $j$,

$$
(-j)\otimes(-j)=j\otimes j,
\qquad
(-J_e)^2=J_e^2.
$$

The sign-reversed currents are therefore indistinguishable to these channels. They can encode magnitude and an unoriented axis, but not orientation.

**Claim ceiling:** an oriented branch requires an additional sign-sensitive state, boundary, constitutive response, or stochastic/asymmetric selector.

## A.3 `PN-RW10` — equivalence hierarchy

**Claim:** `T-RW10`  
**Assumptions:** `A-ORIENTATION`, `A-CONSERVE`, and `A-TRANSPORT` when spaces differ.

If

$$
\operatorname{div}J^{(a)}=\operatorname{div}J^{(b)},
$$

then $J^{(a)}-J^{(b)}$ may lie in a divergence-free cycle or harmonic sector. The coherence trajectory can agree while orientation, circulation, $j\otimes j$, geometry, and later current closure differ.

**Claim ceiling:** field equality is weaker than current equality, which is weaker than equality of the full reflexive causal diagram.

## A.4 `PN-C03` — structural formation versus dynamic realization

**Claim:** `T-C03`  
**Assumptions:** `A-BRANCH`, `A-CONSERVE`.

A constrained critical point satisfies a first-variation condition and admits a structural second variation. Dynamic realization additionally requires invariance or attraction under a declared temporal law. Different temporal closures can act on the same structural state with different stability.

**Claim ceiling:** a positive structural gap is not a universal temporal-stability theorem.

## A.5 `PN-A02` — failure of regular current elimination

**Claim:** `T-A02`  
**Assumptions:** `A-SMOOTH`, `A-REGULAR-SLAVING`.

Let

$$
\mathcal E_J(X,J)=0.
$$

If $D_J\mathcal E_J$ is invertible, the implicit-function theorem supplies a local slaving $J=J(X)$. If the block loses invertibility, this regular elimination theorem no longer applies in the critical direction.

**Claim ceiling:** the critical direction cannot be removed by the same regular slaving construction. A temporal amplitude, higher-order differential-algebraic resolution, or another justified local completion is required for branch passage; no unique completion follows from singularity alone.

## A.6 `PN-A03` — exact symmetric zero

**Claim:** `T-A03`  
**Assumptions:** `A-UNIQUENESS`, `A-ORIENTATION`.

For a deterministic locally unique transition equivariant under reversal $R$ and an exactly invariant state $X_0=RX_0$, uniqueness implies that the trajectory remains reversal-symmetric. A selected oriented branch would violate that symmetry unless distinguishing information enters through initial state, boundary, bias, or stochasticity.

**Claim ceiling:** instability can amplify arbitrarily small asymmetry; it does not create orientation from an exactly symmetry-free state.

## A.7 `PN-A05` — closed stationary gradient current

**Claim:** `T-A05`  
**Assumptions:** `A-CLOSED`, `A-MOBILITY`, `A-CONSERVE`.

For a regular gradient/potential current $J=-M\nabla\mu$ with positive nondegenerate $M$, the closed stationary dissipation identity has the form

$$
0=-\langle\nabla\mu,M\nabla\mu\rangle.
$$

Positivity gives $\nabla\mu=0$ and hence zero dissipative gradient current. Nonzero stationary current must belong to a circulation/harmonic or mobility-null sector, be boundary-maintained, or arise from another current law.

**Claim ceiling:** this does not exclude nonzero stationary circulation or open through-flow.

## A.8 `PN-A06` — tracking failure on a stable instantaneous branch

**Claim:** `T-A06`  
**Assumptions:** `A-BRANCH`, `A-CLOCK`, `A-ISOLATION`.

For a moving discrete branch,

$$
z_{k+1}=A_kz_k-d_k+O(\|z_k\|^2).
$$

Even when the fast block of $A_k$ contracts, a sufficiently large branch defect $d_k$ or slow-to-fast leakage can force the trajectory outside the local accommodation neighborhood.

**Claim ceiling:** tracking failure does not imply loss of the instantaneous structural or temporal branch.

## A.9 `PN-M04` — non-normal finite-horizon persistence

**Claim:** `T-M04`  
**Assumptions:** `A-CLOCK`, `A-NONNORMAL-CONTROL`.

For a non-normal propagator $\Phi_{k+\tau,k}$, finite-time survival is governed by singular values of

$$
\Phi_{k+\tau,k}^*\Phi_{k+\tau,k},
$$

not by eigenvalues alone. The resulting subspace depends on the horizon, norm, and branch path.

**Claim ceiling:** a realized finite-horizon subspace is initially an observer-relative analysis object unless the runtime has access to the required predictive state or schedule.

## A.10 `PN-B03` — individual mode versus cluster identity

**Claim:** `T-B03`  
**Assumptions:** `A-ISOLATION`, `A-TRANSPORT`.

An isolated simple eigenvalue admits an individual spectral projector. Near degeneracy, eigenvectors may rotate or exchange labels while the total spectral projector of the cluster remains regular. After ambient identification, Kato transport intertwines the projector ranges.

**Claim ceiling:** mode-index tracking is valid only while isolation holds; otherwise the continuing object is the cluster/subspace.

## A.11 `PN-B04` — topology-changing transport

**Claim:** `T-B04`  
**Assumptions:** `A-TRANSPORT`.

When state spaces differ, equality or overlap of vectors is undefined until an interspace map is supplied. Lineage or endpoint correspondence may help construct such a map, but does not uniquely determine its action on perturbations, currents, measures, or spectral subspaces.

**Claim ceiling:** no topology-changing continuation or retained-mode survival claim is admitted from lineage alone.

## A.12 `PN-ZB01` — nonempty common zero-background witness

**Supports:** Section 6.6  
**Assumptions:** `A-PASSIVE`, `A-SMOOTH`, `A-CLOSED`, `A-CONSERVE`, `A-LOOP-INVERT`.

A constant constrained state on fixed regular geometry has zero spatial gradient and therefore zero baseline gradient current. Choosing the constraint multiplier to satisfy the first variation gives a formed structural reference. Passive read-back yields $j_*=0$. The common branch requires invertible $I-\mathcal B_{\mathrm{eff},*}$. In the frozen zero-background reduction where no additional first-order current-dependent path survives, $\mathcal B_{\mathrm{eff},*}=\zeta_C\mathcal R_{M,*}$, so the condition reduces to invertibility of $I-\zeta_C\mathcal R_{M,*}$.

**Claim ceiling:** at least one compatible reference class exists; no universal nonuniform or common-generator theorem follows.

---

# Part II — Unchanged-GRC9V3 repository verification

# 12. Experimental stance

Part II is bound by the claim ledger, assumption registry, derivation-status appendix, debt register, gate dependency map, and traceability matrix in Part I.

Every scientific output must identify:

```text
claim_ids
debt_ids
assumption_ids
assumption_status
proof_note_ids
provenance
branch and clock
controls
maximum supported claim
explicitly blocked claims
primary decision route
theory-reopening trigger, if any
```

No positive result may be described only in implementation language, and no negative result may be routed automatically to a runtime extension.

This is an observational, mathematical, and counterfactual experiment over unchanged `GRC9V3`.

The experiment may:

```text
construct experiment-local fixtures
solve for candidate branches
run the existing model and public runtime stages
save and restore snapshots
clone and intervene on valid states
numerically differentiate the complete step map
construct comparison operators outside src/
post-process artifacts
produce reports and machine-readable results
```

The experiment must not:

```text
modify src/pygrc
modify the current GRC9V3 spec to make a hypothesis pass
modify existing tests
add hidden runtime telemetry producers
add a retained state or read current
change current, conductance, spark, growth, boundary, or budget semantics
call a comparison operator native GRC mechanics
promote exploratory values into accepted fixtures before reproduction
```

If the current runtime lacks or cannot identify a required causal surface, the primary result must be one of:

```text
absent_from_unchanged_grc
mapping_rejected
analysis_only
selectable_extension_candidate
lgrc_specific_route
theory_reopening_candidate
blocked_by_identifiability
```

The experiment must not patch the runtime in the same evidence revision.

---

# 13. Proposed experiment package

```text
experiments/2026-08-B1-grc9v3-continuation-readback-verification/
  README.md
  hypotheses/
    README.md
    claim_ledger.md
    assumption_registry.md
    derivation_status_appendix.md
    theory_debt_register.md
    theory_test_traceability.md
    gate_dependency_map.md
  implementation/
    GRC9V3ContinuationReadBackVerificationSpecification.md
    GRC9V3ContinuationReadBackVerificationChecklist.md
  configs/
    baseline.json
    numerical_tolerances.json
    fixture_registry.json
  fixtures/
    two_node_transport.json
    two_node_homogeneous_branch.json
    two_node_nonuniform_seed.json
    triangle_same_row_seed.json
    triangle_port_controls.json
  scripts/
    serialize_theory_contract.py
    capture_repository_baseline.py
    validate_instrumentation.py
    solve_strong_fixed_branches.py
    compute_complete_step_jacobian.py
    compare_frozen_and_full_dynamics.py
    run_preparation_persistence_probe.py
    search_return_orbits.py
    sweep_temporal_and_spatial_thresholds.py
    classify_claims_and_extensions.py
    route_contradictions_and_theory_reopening.py
    build_lgrc_handoff.py
    run_all.py
  outputs/
  reports/
    b1_grc9v3_verification_report.md
```

The file names are normative unless repository integration requires a documented path correction. No numbered `N32` identity is assigned.

---

# 14. Repository freeze and preflight

Before any scientific run, record an exact clean baseline.

## 14.1 Required commands

```bash
git status --porcelain
git rev-parse HEAD
git branch --show-current
git describe --always --dirty --tags
python --version
python -m pip --version
sha256sum pyproject.toml uv.lock requirements.txt requirements-dev.txt
python -m unittest discover -s tests -p 'test_*.py'
```

If source-tree execution is used:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

## 14.2 Preconditions

The baseline gate fails if:

- `git status --porcelain` is nonempty;
- the exact commit SHA is not recorded;
- the existing test suite fails;
- the Python version is below the repository minimum;
- dependency-lock hashes are not recorded;
- the experiment scripts import code from an uncommitted local patch;
- or machine-local absolute paths appear in committed evidence.

## 14.3 Baseline manifest

The run must write `outputs/baseline_manifest.json` containing at least:

```json
{
  "schema_version": "b1_grc9v3_verification_v3_2",
  "specification_id": "b1_grc9v3_continuation_readback_verification_v3_2",
  "repository": "github.com/urosj/graph-reflexive-coherence",
  "commit_sha": "<exact sha>",
  "branch_name": "<informational only>",
  "dirty": false,
  "theory_repository": "github.com/urosj/geometric-reflexive-coherence",
  "theory_commit_sha": "<exact sha>",
  "specification_sha256": "<complete specification digest>",
  "theory_contract_sha256": "<canonical Part I and Appendix A digest>",
  "assumption_registry_sha256": "<digest>",
  "python_version": "<version>",
  "dependency_hashes": {},
  "test_command": "<exact command>",
  "test_result": "passed",
  "created_at_utc": "<ISO-8601>",
  "runtime_change_authorized": false
}
```

---

# 15. Canonical artifact rules

All machine-readable evidence must:

- use UTF-8 JSON;
- reject NaN and infinity;
- sort object keys;
- preserve declared node/edge ordering;
- use relative paths;
- record the generating command;
- record fixture and parameter hashes;
- record the exact state projection used;
- and include a SHA-256 digest of the canonical payload.

Recommended canonicalization:

```python
json.dumps(
    payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
)
```

Raw snapshots produced by the model must be retained separately from derived matrices and reports.

Every derived matrix must include:

```text
row coordinate order
column coordinate order
state projection
perturbation convention
finite-difference or analytic method
step size
error/convergence check
```

---

# 16. Fixed-topology verification envelope

All primary B1-G verification rows use the following envelope:

```text
model_family = GRC9V3
fixed_topology = true
frame_mode = fixed_port_chart
boundary_mode = prune
boundary_action_required = prune_noop
curvature_backend = none
spark_lane = current_hybrid_signed_hessian
choice_backend = disabled
quadrature_mode = unit_measure
lambda_birth = 0.0
no_spark_candidates = required
no_expansion_events = required
no_growth_events = required
no_choice_or_collapse_events = required
no_topology_change = required
rng_seed = fixed and serialized
```

All nodes must remain strictly positive under the perturbation envelope so that budget projection or boundary regularization does not create a hidden derivative or branch switch.

The primary perturbation space for coherence is the zero-sum tangent:

$$
\mathcal T_Q^G
=
\left\{u\in\mathbb R^{|V|}:\mathbf 1^Tu=0\right\}.
$$

The experiment must assert that budget correction is a numerical no-op for tangent perturbations. If not, the budget projection must be included explicitly in the complete transition Jacobian and reported as load-bearing.

---

# 17. Fixture registry

The fixture registry must distinguish canonical fixtures from noncanonical candidate seeds.

## 17.1 `F0` — existing two-node transport anchor

Purpose:

- verify that the experiment calls the current runtime correctly;
- reproduce the existing transport test values;
- validate state ordering and edge orientation.

This fixture is copied semantically from the existing repository test and is not new scientific evidence.

## 17.2 `F1` — homogeneous two-node branch family

Topology:

```text
node 0 port 1 <-> node 1 port 1
```

Purpose:

- prove the nonempty homogeneous strong branch;
- sweep site-potential scale, timestep, and transport parameters;
- compare transition multipliers with spatial Hessian diagnostics;
- search for `+1` and `-1` temporal thresholds.

## 17.3 `F2` — nonuniform two-node branch seed

Purpose:

- initialize a branch solver from the exploratory nonuniform candidate;
- require the repository runtime to solve and certify the final branch;
- test whether old conductance and current are independent tangent coordinates on a one-edge motif.

Exploratory values may be used only as solver seeds. They are not accepted evidence until the full repository branch residual passes.

## 17.4 `F3` — same-row triangle

Topology:

```text
edge 0: node 0 port 1 <-> node 1 port 1
edge 1: node 1 port 2 <-> node 2 port 1
edge 2: node 2 port 2 <-> node 0 port 2
```

All occupied ports lie in the same GRC9 row, while each node uses distinct ports.

Purpose:

- permit nontrivial conductance weighting within a row;
- test whether conductance is an independent first-order state coordinate;
- search for nonuniform strong branches and joint slow modes;
- run preparation–persistence–probe interventions.

## 17.5 `F4` — port and orientation controls

Controls include:

- edge orientation reversal with corresponding current-coordinate sign change;
- row-preserving port permutation;
- column-changing port permutation;
- same abstract graph with degree-preserving port relabeling;
- sign-reversed old current under matched $C$ and $W$.

These controls distinguish graph adjacency effects, chart effects, and current-orientation effects.

## 17.6 `F5` — return-orbit search family

Purpose:

- search for period-two or higher return orbits of the full step map;
- determine whether current-carrying recurrence exists despite absence of stationary cycle current;
- classify such states as synchronous transport orbits rather than stationary circulation.

---

# 18. State projections and coordinate order

## 18.1 Nonlinear runtime projection

The primary nonlinear physical projection is

```text
C: node coherence, sorted by node_id
W: base_conductance, sorted by edge_id
J: port_edges[edge_id].flux_uv, sorted by edge_id
Phi: node potential, sorted by node_id
G: row-basis gradients, sorted by node_id and row
Hs: signed row-basis Hessian, sorted by node_id and row
Kcache: cached hybrid node tensors, sorted by node_id
identity: sinks, basins, hierarchy
budget: target, measured total, correction record
```

Bookkeeping such as `step_index`, `time`, event-log append position, trace strings, and observer caches is excluded from the physical fixed-point norm but must be checked separately for expected deterministic advancement.

Exclusion from the physical norm does not certify causal irrelevance. `GRV1` and `GRV3` must inventory every excluded or administratively advancing field and classify it as:

```text
deterministic administrative advancement
causal runtime state
observer-only state
reconstructed state
unknown
```

Any field classified as `causal runtime state` or `unknown` remains inside the `A-STATE-CLOSURE` comparison. Physical equality and causal-state equality must be reported separately.

## 18.2 Jacobian state

The default full nonlinear coordinate is

$$
x=(C,W,J).
$$

The quiescent linear state shall be inferred from Jacobian blocks rather than assumed.

Candidate reductions are:

```text
(C,W,J) nonlinear state
(C,W) quiescent tangent state if D_J F = 0
C-only tangent state only if D_W F is also eliminable on that branch
```

## 18.3 Orientation convention

Each stored edge has one canonical orientation from `node_u` to `node_v`.

Reversing a coordinate orientation must transform:

$$
J_e\mapsto-J_e
$$

without changing physical conclusions. Every current-sensitive result must pass an edge-orientation covariance control.


## 18.4 Default fixed-topology ambient identification

For every fixed-topology GRV gate, the default ambient identification is the identity map on the canonical coordinate chart with fixed state dimension, node order, edge order, row or port order, and edge orientation.

If an operator, projector, or mode uses a branch-dependent inner product, node/edge measure, or state metric, the evidence artifact must additionally record the fixed-reference representation, isometry, congruence, or normalization used for comparison. Coordinate identity alone does not preserve orthogonality or self-adjointness under a changing metric.

This default is invalid across topology, support, or state-dimension change. Such comparisons remain governed by `A-TRANSPORT` and debt `D-T01`.

---

# 19. Numerical methods

## 19.1 Strong fixed-branch residual

A candidate branch is accepted only if both of the following pass.

### Full-step residual

Run the complete unchanged `GRC9V3.step()` and compare the physical projection before and after one step:

$$
R_{\mathrm{step}}(X)=\Pi_{\mathrm{phys}}F(X)-\Pi_{\mathrm{phys}}X.
$$

### Internal strong residual

On a fresh clone, execute the public runtime stages in the exact documented order and capture the physical state after each load-bearing stage.

A strong branch requires no hidden internal alternation among:

```text
initial differential reconstruction
first transport reconstruction
post-flux differential reconstruction
identity reconstruction
no-op semantic/event stages
continuity and budget
final differential/transport refresh
```

Required norms:

```text
L_inf residual
L_2 residual
relative residual
per-block residual for C, W, J, Phi, G, and identity
```

Default acceptance target:

```text
absolute L_inf <= 1e-10 for analytic/homogeneous branches
absolute L_inf <= 1e-9 for numerically solved branches
relative residual <= 1e-8
```

Any larger tolerance must be preregistered with a numerical justification.

## 19.2 Branch solver

The solver may vary only declared branch coordinates and must enforce:

- fixed total coherence;
- positive coherence;
- positive conductance;
- fixed topology;
- no event eligibility;
- and the strong residual rather than only $J=0$.

Multiple starting seeds and symmetry-related solutions must be retained. Deduplication must use a documented permutation/symmetry relation, not only Euclidean distance.

## 19.3 Complete-step Jacobian

The Jacobian is

$$
A_*=D\bigl(\Pi_{\mathrm{phys}}F\bigr)[X_*].
$$

Use central differences on valid state perturbations:

$$
A_*e_i
\approx
\frac{F(X_*+h_ie_i)-F(X_*-h_ie_i)}{2h_i}.
$$

Required step-size sweep:

```text
1e-4, 1e-5, 1e-6, 1e-7 times the declared coordinate scale
```

The selected derivative must lie in a convergence region and include a truncation estimate.

Every perturbed run must:

- restore the exact same baseline snapshot;
- preserve topology;
- emit no events;
- remain positive and valid;
- preserve the budget tangent;
- and use the same RNG state.

If a perturbation crosses an event or validation boundary, that derivative is blocked rather than silently one-sided.

## 19.4 Eigenvalue and slow-cluster analysis

For each accepted branch, report:

- eigenvalues and algebraic/geometric multiplicities;
- left and right eigenvectors where non-normality is present;
- condition numbers or residuals;
- block participation in $C$, $W$, and $J$;
- conserved/gauge directions;
- spectral separation of candidate slow clusters;
- and a pseudospectral or singular-value warning if eigenvectors are ill-conditioned.

A candidate slow cluster must be isolated by a preregistered contour or multiplier window and must survive the finite-difference step-size sweep.

## 19.5 Return-map/Floquet analysis

A period-$p$ orbit must satisfy

$$
\|F^p(X)-X\|\le\varepsilon_{\mathrm{orbit}},
$$

while

$$
\|F^q(X)-X\|>\varepsilon_{\mathrm{primitive}}
$$

for all proper divisors $q<p$.

The return-map Jacobian is

$$
D(F^p)=DF(X_{p-1})\cdots DF(X_0).
$$

The conserved-budget multiplier must be identified separately. A stable orbit requires all other multipliers to lie strictly inside the unit circle within tolerance.

---

# 20. Verification gates

## 20.1 Gate dependency and early-stop rules

The verification is serial:

$$
\boxed{
\mathrm{GRV0}
\rightarrow
\mathrm{GRV1}
\rightarrow
\mathrm{GRV2}
\rightarrow
\mathrm{GRV3}
\rightarrow
\mathrm{GRV4}
\rightarrow
\mathrm{GRV5}
\rightarrow
\mathrm{GRV6}
\rightarrow
\mathrm{GRV7}
\rightarrow
\mathrm{GRV8}.
}
$$

The sequence is scientific, not merely administrative.

- `GRV0` failure stops the run.
- `GRV1` source-fidelity or instrumentation failure invalidates all later scientific evidence.
- `GRV2` must accept at least one strong branch before branch-relative Jacobian, continuation, retention, or return-map claims proceed. Source-level nulls may still be recorded.
- `GRV3` must classify the branch-relative causal state before `GRV4`–`GRV6` interpret temporal modes or mediation.
- `GRV4` establishes whether a reduced comparator is admissible before `GRV5` interprets slow carriers.
- `GRV5` classifies retention, read, and write arrows before `GRV6` interprets recurrent current as memory or active branch semantics.
- `GRV6` establishes current orientation and recurrence semantics before `GRV7` compares temporal thresholds with spatial Hessians.
- `GRV8` is the only gate permitted to assign final implementation status, extension route, LGRC route, or theory reopening.

An early stop must still produce a closeout containing satisfied, failed, and unidentifiable assumptions; passed gates; blocked gates; and the resulting claim ceiling.

# GRV0 — Specification and baseline admission

## Question

Can the experiment be run reproducibly without changing the runtime under test?

## Requirements

- specification accepted;
- exact repository and theory SHAs recorded;
- clean checkout;
- existing test suite passes;
- directory and artifact schemas created;
- Part I claim ledger, assumption registry, derivation-status appendix, debt register, gate dependency map, and traceability matrix serialized;
- contradiction and theory-reopening schemas created;
- no `src/` or existing-test changes.

## Valid outcomes

```text
admitted
blocked_by_dirty_or_failing_baseline
blocked_by_missing_exact_source_identity
```

---

# GRV1 — Instrumentation and source-fidelity validation

## Questions

1. Do experiment-local calls reproduce existing transport fixtures?
2. Does the captured step trace match the runtime order?
3. Which surfaces are actually load-bearing?
4. Is the materialized `K` cache consumed by transport?

## Tests

### GRV1-A — transport anchor

Reproduce the existing two-node transport fixture through the same public methods used by the runtime.

### GRV1-B — full step-order capture

Assert the existing canonical step trace and no-event fixed-topology envelope.

### GRV1-C — `K` counterfactual

After rebuilding differential state, clone two states that agree in all physical load-bearing fields but differ strongly in cached `hybrid_node_tensors`. Run transport reconstruction.

Supporting result for diagnostic-only `K`:

```text
transport outputs remain bitwise or tolerance-equivalent despite changed K cache
```

If transport changes, the source-level load-bearing analysis must be revised.

### GRV1-D — current sign control

Construct matched valid states $(C,W,J)$ and $(C,W,-J)$ and compare the next transport and full-step physical projections.

This tests whether old current orientation survives through any current causal path.

The result must classify separately:

```text
magnitude persistence
unoriented axis persistence
orientation persistence
current reconstructed anew
```

A sign-even result may support a quadratic inscription claim but cannot support orientation retention.

## Claim ceiling

Exact runtime dependency and orientation semantics only.

---

# GRV2 — Strong formed branches

## Hypotheses

```text
H2.1 homogeneous strong zero-current branches exist
H2.2 nonuniform strong zero-current branches exist
H2.3 strong branch status requires the complete double-refresh runtime
```

## Tests

1. certify the homogeneous two-node branch;
2. solve and certify a nonuniform two-node branch;
3. search and certify nonuniform triangle branches;
4. run symmetry and port-relabel controls;
5. save, load, and replay every accepted branch.

## Evidence

`outputs/fixed_branch_registry.json` must record:

```text
branch_id
fixture_id
parameter_hash
state snapshot path and hash
full-step residual
internal-stage residuals
budget residual
event and topology assertions
symmetry class
solver seeds and convergence record
```

## Claim ceiling

Existence and local source identity of GRC formed fixed branches. No continuation or retention claim follows from branch existence alone.

---

# GRV3 — Causal state and complete transition Jacobian

## Hypotheses

```text
H3.1 nonlinear runtime state is at least (C,W,J)
H3.2 at quiescent branches old current is not an independent linear mode
H3.3 generic nonuniform quiescent branches require joint (C,W) perturbations
H3.4 homogeneous branches may admit a stronger C-only linear reduction
H3.5 isolated joint C-W slow clusters may exist
```

## Counterfactual closure tests

1. matched $C,J$, different valid $W$;
2. matched $C,W$, different $J$;
3. matched $C,W$, sign-reversed $J$;
4. matched $C$ with branch-consistent versus perturbed derived surfaces;
5. reachable-history pairs and synthetic-valid pairs reported separately;
6. every field excluded from the physical projection classified under Section 18.1, with causal or unknown fields retained in the closure-state comparison.

## Jacobian outputs

`outputs/complete_step_jacobians.json` must include:

```text
coordinate order
full matrix
C/W/J blocks
eigenvalues
left/right residuals
participation ratios
conservation, branch-tangent, and gauge modes
candidate stable slow clusters
neutral and unstable clusters
mode versus cluster identity
field-level versus current-level response
finite-difference convergence
excluded-field causal inventory
non-normal evidence mode and preregistered threshold
eigenvector or invariant-subspace conditioning
resolvent, pseudospectral, or propagator diagnostic as applicable
finite-horizon clock, norm, horizon, and singular values as applicable
fast-slow measure, threshold, and assumption status
```

## Decision rule

- If $D_WF\neq0$, `W` is a causal tangent coordinate on that branch.
- If $D_JF=0$ at $J=0$, old current is absent as an independent first-order mode on that branch.
- If slow eigenvectors have material support in both $C$ and $W$, the candidate temporal structure is joint rather than conductance-only.
- A multiplier near the unit circle must be classified as stable slow, neutral, oscillatory, or unstable before any retention language is used.
- If a spectral interpretation is used under non-normal dynamics, `A-NONNORMAL-CONTROL` must be assigned through one of the Section 2.4.1 evidence modes; otherwise it is `not_identifiable`.
- If algebraic current slaving is interpreted as a fast limit, the selected `A-FAST-SLOW` measure and threshold from Section 2.4.2 must be reported. Where no independent current-relaxation sector exists, the assumption is `not_applicable`.
- If two states produce the same coherence update but different current or future geometry, field-trajectory equivalence does not establish current-level equivalence.

## Claim ceiling

Runtime causal-state and temporal-mode evidence. A slow joint mode is not yet core retention.

---

# GRV4 — Frozen-conductance versus full recurrence

## Purpose

Determine which continuation/relaxation statements are valid only in the frozen-$W$ reduction and whether evolving conductance changes the stability classification.

## 4.1 Runtime sign audit

For fixed $W$, define the graph functional represented by the runtime potential:

$$
\mathcal P_G[C;W]
=
\frac{\kappa_C}{2}C^TL_WC
-
\sum_iV(C_i).
$$

Verify numerically and analytically which sign is monotone under the implemented flux and continuity equations.

The result must be reported as one of:

```text
P_G decreases
P_G increases and -P_G decreases
neither is monotone under the tested discrete step
monotonicity holds only in a small-step limit
```

No continuation sign convention is accepted before this audit.

## 4.2 Frozen-$W$ structural comparator

Construct outside `src/`:

- the fixed-$W$ constrained second variation;
- the runtime-compatible signed continuation candidate after the sign audit;
- the fixed-$W$ mobility;
- the semidiscrete and explicit-step multipliers.

This operator is a declared analytical comparator, not native runtime state.

## 4.3 Full-map comparison

For every accepted branch, compare:

```text
frozen-W structural eigenvalues
frozen-W predicted temporal multipliers
complete-step transition multipliers
mode overlap or subspace angle
stability classification
```

## Strong result

The reduction and full recurrence disagree on stability or slow-subspace identity for at least one verified branch.

## Claim ceiling

- A frozen-$W$ operator may be classified as `substrate_reduced`.
- The complete GRC temporal continuation classification belongs to the full transition map or a justified elimination of $W$.
- No full-core $\mathscr H_*$ claim is permitted.

---

# GRV5 — Conductance preparation, persistence, and mediation

## Central question

Does conductance merely participate in immediate recurrence, or does it participate in a branch-relative retained structure that persists after forming activity and causally changes a later matched probe?

GRV5 must evaluate the acceptance contracts in Sections 4.5–4.7 separately and record the status of at least:

```text
A-BRANCH
A-CLOCK
A-PASSIVE
A-REACHABLE
A-STATE-CLOSURE
```

It must classify:

```text
retention evidence
read-effect evidence
write evidence
closed-loop evidence
```

The absence of one role must not erase evidence for another.

## Required phases

$$
\text{preparation}
\longrightarrow
\text{persistence interval}
\longrightarrow
\text{matched probe}.
$$

## Preparation lanes

### `P-W` — direct conductance intervention

Apply opposite small $W$ perturbations around an accepted branch while matching $C$ and $J$.

### `P-J` — activity-mediated write

Apply a finite old-current pulse or a reached current history, execute the unchanged runtime, and measure the resulting $W$ and joint-state displacement.

### `P-J-sign` — sign-reversal control

Use matched $J$ and $-J$ preparations. If the only current write channel is quadratic, the conductance inscription should be sign-even after all other variables are matched.

## Persistence lanes

For declared horizons $k\in\{0,1,2,5,10,20,50,100\}$ or a justified replacement:

- let the unchanged runtime advance;
- remove further forming intervention;
- record $C,W,J$ separation;
- project separation onto identified slow/fast subspaces;
- distinguish fast overwrite from slow joint persistence.

## Passive-null and matched-probe mediation

Before the active probe, execute a zero-present-probe control. A retained or conductance difference may remain, but no response may be called an explicit read current merely because geometry-conditioned baseline transport differs.

At each horizon:

1. clone the two prepared states;
2. match $C$ and $J$ through a documented counterfactual intervention;
3. preserve their differing $W$;
4. apply the same small zero-sum coherence/current probe;
5. rebuild immediate transport or run one complete no-event step;
6. compare the current response.

## Mediation controls

- reset both $W$ fields to the same baseline;
- swap $W$ between histories;
- hold $W$ equal while preserving reached $C$ differences;
- verify that the effect disappears or follows the proposed carrier;
- report reached-state and synthetic-valid interventions separately.

## Local evidence ladder

| Rung | Meaning |
|---|---|
| `GRR0` | no attributable conductance/joint carrier |
| `GRR1` | activity changes a causal conductance or joint state |
| `GRR2` | the difference persists after forming intervention stops |
| `GRR3` | the persistent difference occupies an isolated temporal slow cluster |
| `GRR4` | a matched later probe causally depends on the candidate carrier |
| `GRR5` | write, persistence, mediation, reset/swap controls, and replay pass |

Even `GRR5` supports at most a **retained-geometry or joint-retention candidate**. It does not establish core Read-Back unless a present-current-conditioned directional read relation satisfying the passive null is also identified.

The closeout must fill the causal possibility matrix from `T-RW06` and state whether the result is:

```text
retention_without_read
read_effect_without_persistent_write
write_before_read
closed_read_write_loop
ordinary_recurrent_geometry
unidentifiable
```

---

# GRV6 — Current recurrence and recurrent branches

## 6.1 Stationary cycle-current control

Before invoking `T-A05` in this gate, record the status of `A-CLOSED`, `A-MOBILITY`, and `A-CONSERVE`. `A-ORIENTATION` is not an assumption of the stationary-gradient-current exclusion; it is declared separately for sign, axis, and orientation classification in `GRV6.2`.

On a graph containing a cycle, initialize a nonzero divergence-free edge current with matched uniform or fixed coherence. Run transport reconstruction.

Determine whether the current:

- persists as cycle current;
- is overwritten by potential flow;
- changes conductance only through magnitude;
- or induces another current through the coherence/potential path.

This complements the analytic positive-conductance potential-flow result that a closed stationary state cannot retain nonzero gradient current with zero divergence.

## 6.2 Exact-zero, finite-seed, and orientation controls

Before interpreting exact zero or orientation selection, record the status of `A-UNIQUENESS` and `A-ORIENTATION`. Record `A-CLOSED` and `A-MOBILITY` only where a branch-specific comparison independently requires them.

For selected branch families, compare:

```text
exact symmetric zero current
finite positive current seed
finite negative current seed
sign-even magnitude-matched preparation
cycle-space current seed where graph topology permits
```

Record whether the runtime:

- leaves exact zero invariant;
- amplifies or suppresses a finite seed;
- preserves orientation, only magnitude or axis, or neither;
- saturates into a recurrent branch;
- reconstructs current from present potential;
- or requires another state coordinate.

No result may call exact-zero symmetry breaking unless a declared asymmetry or stochastic source is present.

## 6.3 Return-orbit search

Search the complete step map for period-two and higher orbits using:

- parameter sweeps;
- multiplier continuation near $-1$ or complex unit-circle crossings;
- direct return residual minimization;
- and replay from saved snapshots.

## 6.4 Classification

A current-carrying return orbit must be described as one of:

```text
alternating potential-flow transport orbit
higher-period synchronous transport orbit
quasi-periodic/undetermined recurrent state
stationary cycle-space current (only if actually supported)
```

It must not be called active stationary circulation, read-back, or self-sustaining identity merely because current remains nonzero over time.

---

# GRV7 — Spatial Hessians versus temporal and continuation thresholds

## Hypotheses

```text
H7.1 row/signed/WLS Hessians are exact spatial diagnostics
H7.2 they are not the complete transition Jacobian
H7.3 no universal threshold identity links them to +1, -1, or structural continuation marginality
```

## Method

On homogeneous and nonuniform branch families, sweep parameters that move complete-step multipliers through:

```text
+1 real marginality
stable interior
-1 flip marginality
possible complex unit-circle crossing
```

At every parameter value record:

- full transition multipliers;
- frozen-$W$ comparator spectrum;
- row-basis unsigned Hessian;
- signed Hessian;
- weighted-least-squares comparison Hessian;
- sink/basin/spark evidence;
- and event status.

## Strong counterexample

A temporal threshold is crossed while the spatial Hessian diagnostic remains unchanged or fails to cross its own declared threshold.

## Claim ceiling

The experiment may establish non-equivalence. It may not establish that spatial Hessians never correlate with temporal or basin transitions in any regime.

---

# GRV8 — Claim classification, assumption routing, contradiction routing, and extension decision

Every tested claim must first record each required assumption as:

```text
satisfied
failed
not_identifiable
not_applicable
deferred
```

A claim with a failed or unidentifiable required assumption is reported as `not_admitted_under_tested_assumptions` unless an independent contradiction is established. It must not be reported simply as falsified.

Every tested object must then receive one of the required implementation statuses:

```text
already implemented exactly
implemented as a declared simplifying limit
implemented only analogically
measurable from existing state but not constitutive
absent from the substrate
theoretically underdetermined/open
```

It must also receive:

```text
correspondence level L0-L5
claim IDs
debt IDs
assumption IDs and statuses
proof-note IDs
maximum supported claim
blocked claims
primary decision route
```

Every contradiction with Part I must be routed as one of:

```text
substrate_nonrealization
candidate_graph_mapping_error
core_derived_claim_too_strong
core_assumption_incompatible_with_this_realization
required_assumption_failed
required_assumption_not_identifiable
construct_not_identifiable_with_available_interventions
numerical_or_instrumentation_failure
source_or_specification_mismatch
```

The final classification must cover at least:

- formed zero-current branches;
- causal $C,W,J$ state;
- fixed-$W$ constrained continuation comparator;
- complete-step temporal spectrum;
- stable, neutral, and unstable temporal subspaces;
- conductance-mediated retention, read-effect, and write evidence separately;
- distinct read current;
- $j=J_C$ limit;
- magnitude, axis, and orientation retention;
- field-trajectory versus current-level equivalence;
- load-bearing status of `K`;
- geometry/mobility separation;
- active stationary circulation;
- recurrent transport orbits;
- moving retained slow bundle;
- row/signed Hessian relation to continuation;
- and every open-theory debt in Section 9.

The final result may route to theory reopening. A mismatch is not automatically an extension requirement.

---

# 21. Extension decision rules

This unchanged-runtime experiment does not implement extensions. It produces requirements for a revision-distinct implementation tranche only when the evidence supports them.

Before any extension is opened, GRV8 must exclude, as primary explanations:

```text
candidate mapping was wrong
core-derived claim was too strong
construct is not identifiable
numerical or source-fidelity failure
role belongs intrinsically to LGRC
```

An extension must close a named substrate requirement or open-theory debt. It must not be justified only by resemblance to a core symbol.

## 21.1 Geometry–mobility separation

Open a selectable extension contract if all of the following hold:

1. $W$ is load-bearing in both structural and transport roles;
2. full and frozen-$W$ classifications differ materially;
3. the difference cannot be interpreted cleanly as structural curvature versus mobility;
4. the ambiguity blocks mapping of $\alpha$ and $\gamma$.

This extension would primarily address `D-G02` and must preserve the distinction between structural and kinetic evidence.

The extension must define distinct graph objects, provisionally:

$$
H_G\quad\text{structural geometry},
$$

$$
M_G\quad\text{transport mobility}.
$$

Disabled-mode parity with legacy `GRC9V3` is mandatory.

## 21.2 Retained geometric carrier

Open a retained-geometry extension contract if:

- activity produces a reproducible geometry difference;
- the existing $W$ carrier is overwritten too quickly or conflates fast and slow roles;
- a later matched probe requires a persistent mediator not representable by the accepted present state;
- or a declared persistence timescale cannot be controlled independently.

This extension would primarily address `D-R02` and must not silently choose the universal retained projector.

The extension must specify:

```text
carrier type and units
write law
relaxation/persistence law
clock
passive-current behavior
read path
reset/save/load identity
invariant or boundedness rule
```

## 21.3 Oriented read-current or cycle-current channel

Open this contract only if the intended target includes directional Read-Back or closed active circulation and the baseline confirms that:

- old-current orientation is erased or reconstructed anew;
- the $J^2\rightarrow W$ path is sign-even;
- potential-flow transport excludes cycle-space stationary current;
- and no existing load-bearing oriented carrier supplies the missing role.

This extension would primarily address `D-R03` and `D-A01`.

The extension must preserve edge-orientation covariance and distinguish gradient current from cycle or harmonic current. It must state whether it supplies magnitude, axis, orientation, current branch selection, or all four.

## 21.4 `K` decision

The final baseline report must choose one of:

```text
K remains explicitly diagnostic
K becomes load-bearing in a separate extension
K is replaced by a more faithful graph object
```

This decision primarily addresses `D-G01`.

The baseline runtime must not be rewritten merely to make its materialized tensor resemble the continuum equation.

## 21.5 Extension revision boundary

Any extension implementation requires:

1. accepted B1-GR baseline evidence;
2. a new implementation plan and checklist;
3. a default-off/selectable feature contract;
4. unchanged legacy parity when disabled;
5. new tests;
6. rerun of every applicable GRV gate;
7. independent claim classification.

---

# 22. Required outputs

The experiment must produce at least:

```text
outputs/theory_claim_ledger.json
outputs/theory_assumption_registry.json
outputs/theory_derivation_status.json
outputs/theory_debt_register.json
outputs/theory_test_traceability.json
outputs/gate_dependency_map.json
outputs/assumption_status_matrix.json
outputs/contradiction_register.json
outputs/baseline_manifest.json
outputs/fixture_registry.json
outputs/instrumentation_validation.json
outputs/fixed_branch_registry.json
outputs/complete_step_jacobians.json
outputs/slow_cluster_registry.json
outputs/frozen_full_comparison.json
outputs/conductance_retention_probe.json
outputs/return_orbit_registry.json
outputs/spatial_temporal_threshold_matrix.json
outputs/causal_role_matrix.json
outputs/equivalence_classification.json
outputs/final_claim_classification.json
outputs/extension_decision.json
outputs/theory_reopening_decision.json
outputs/lgrc_handoff.json
reports/b1_grc9v3_verification_report.md
```

Every output must state its highest supported claim and explicit blocked claims.

---

# 23. Verification closeout ladder

```text
GRV-C0 = specification, claim ledger, assumption registry, derivation-status appendix, debt register, gate dependency map, and traceability accepted; execution not started
GRV-C1 = exact clean repository baseline and existing tests admitted
GRV-C2 = instrumentation/source-fidelity and no-runtime-change gate passed
GRV-C3 = strong fixed-branch registry and replay evidence complete
GRV-C4 = complete Jacobian, causal-state, slow-cluster, and frozen/full comparison complete
GRV-C5 = retention-mediation, recurrent-orbit, and spatial/temporal threshold evidence complete
GRV-C6 = claim classification, contradiction routing, theory-reopening decision, extension decisions, corrected spec, and LGRC handoff complete
```

`GRV-C6` does not require a positive Read-Back result or any extension selection. A falsification, blocked result, or confirmation that GRC realizes a different reflexive mechanism is valid.

---

# 24. Valid final outcomes

The experiment may close with any source-backed combination of:

```text
homogeneous formed branches only
nonuniform formed branches reproduced
C-only quiescent tangent reduction supported on a bounded branch
joint C-W tangent state supported
isolated joint slow cluster supported
frozen-W comparator agrees with full dynamics
frozen-W comparator fails or reverses stability classification
conductance participates in retained joint organization
conductance is only fast recurrent state
retention supported without explicit read-back
write supported before read-back
read effect supported without persistent write
matched-probe mediation supported
matched-probe mediation unsupported
periodic potential-flow orbit supported
active stationary cycle current excluded
row/signed Hessian non-equivalence supported
K confirmed diagnostic only
geometry-mobility split requirement produced
retained-carrier requirement produced
oriented-current requirement produced
issue routed to LGRC rather than GRC
B1-derived claim reopened
candidate graph mapping rejected
construct remains unidentifiable
no runtime extension justified
```

The final report must not claim:

```text
full core Read-Back
unique retained projector
unified alpha/gamma/beta spectrum
active stationary circulation unless directly supported
spark equivalence with temporal marginality
N32 selection
LGRC retention
agentic ecology result
memory, learning, agency, organism, or life
```

---

# Part III — LGRC handoff boundary

# 25. Why LGRC is deferred

`LGRC9V3` composes an event-driven causal-history substrate over a GRC9V3 base state. Its event queues, packets, delays, proper-time surfaces, lineage, route policies, and topology operations add multiple possible causes of persistence and historical influence.

Without a stable GRC baseline, an LGRC result cannot be attributed cleanly to:

```text
inherited synchronous GRC recurrence
packet transport still in flight
event scheduling
local proper-time progression
route or producer policy
lineage transport
topology change
or genuine retained historical read-back
```

LGRC is therefore included here only as a handoff contract.

The handoff must inherit both positive GRC findings and negative decision boundaries. In particular, LGRC must not be credited with creating a causal role already present in the stabilized GRC base, and it must not use event history to hide an unresolved GRC correspondence.

# 26. Conditions for opening B1-L

B1-L may begin only after:

1. the exact GRC commit and theory commit are frozen;
2. every GRV hypothesis is reproduced, corrected, rejected, or explicitly blocked;
3. legacy GRC9V3 has canonical branch and transition fixtures;
4. the GRC causal state and temporal slow objects are accepted within scope;
5. the status of conductance as fast state, retained carrier, or joint carrier is classified;
6. the geometry–mobility issue is either resolved by extension or retained as an explicit limitation;
7. any foundational GRC extension has disabled-mode legacy parity;
8. the GRC claim ceiling relative to Continuation and Read-Back is accepted;
9. remaining missing roles are classified as synchronous-GRC, event-driven-LGRC, analysis-only, or theory-open;
10. the claim ledger and theory-debt register have accepted GRC outcomes;
11. the status of magnitude, axis, and orientation retention has been frozen;
12. field-trajectory, current-level, and full-reflexive equivalence have been classified where relevant;
13. the assumption registry has accepted GRC statuses and unresolved assumptions are handed off explicitly;
14. the graph one-form bridge status is frozen as absent, candidate, accepted, or theory-open;
15. ambient fixed-topology transport and topology-changing interspace transport are not conflated.

# 27. Required LGRC inheritance record

`outputs/lgrc_handoff.json` must contain:

```json
{
  "schema_version": "b1_grc_to_lgrc_handoff_v3_2",
  "grc_commit_sha": "<sha>",
  "theory_commit_sha": "<sha>",
  "grc_verification_closeout": "GRV-C6",
  "accepted_claim_ids": [],
  "reopened_claim_ids": [],
  "proof_note_ids": [],
  "assumption_status_matrix_path": "outputs/assumption_status_matrix.json",
  "assumption_status_matrix_sha256": "<sha256>",
  "satisfied_assumption_ids": [],
  "failed_assumption_ids": [],
  "not_identifiable_assumption_ids": [],
  "not_applicable_assumption_ids": [],
  "deferred_assumption_ids": [],
  "open_debt_ids": [],
  "accepted_grc_runtime_state": [],
  "accepted_grc_branch_classes": [],
  "accepted_grc_temporal_objects": [],
  "grc_retention_status": "<classification>",
  "grc_readback_status": "<classification>",
  "grc_writeback_status": "<classification>",
  "grc_magnitude_axis_orientation_status": {},
  "grc_equivalence_levels": {},
  "graph_one_form_bridge_status": "<absent_candidate_or_accepted>",
  "grc_clock_and_beat": "<declaration>",
  "grc_extension_set": [],
  "ambient_state_space_transport_status": "<accepted_or_open>",
  "interspace_transport_status": "<not_applicable_or_open>",
  "unresolved_theory_questions": [],
  "lgrc_only_questions": [],
  "analysis_only_questions": [],
  "forbidden_inherited_claims": []
}
```

# 28. Initial B1-L envelope

The first LGRC investigation must begin with:

```text
fixed topology
producers disabled during the probe
route policies fixed
preparatory packets drained before the test probe
explicit event-time and proper-time declarations
matched embedded GRC state
no lineage/topology-change claim in the first lane
```

The queue-drained condition is mandatory. Otherwise later influence may be ordinary delayed transport rather than retention.

# 29. LGRC questions to inherit

B1-L should ask, in order:

1. What is the minimal LGRC Markov state once the GRC base state is fixed?
2. What constitutes one reflexive beat: one event, one route cycle, one queue-drained return, or one proper-time interval?
3. Which packet/queue states are transport still in flight?
4. Which historical surfaces survive after transport transients are exhausted?
5. Which of those surfaces are natively read by later constitutive execution?
6. Is the later read merely routing/scheduling, or a retention-conditioned directional current response?
7. Which clock defines slow persistence?
8. Does a return-map slow subspace exist?
9. Does lineage provide only identity/endpoint transport, or a justified retained-subspace transport?
10. Where does producer-mediated evidence stop and native runtime evidence begin?
11. Does topology change require a new interspace continuation transport?
12. Does Markov sufficiency fail without event history or phase?
13. Which effects preserve only magnitude or axis, and which preserve oriented current?
14. Are field trajectories equivalent while packet/current histories remain distinct?
15. What explicit interspace map is required before lineage can support a continuation or retained-mode claim?
16. Does a finite-horizon return subspace remain analysis-only, or is it read constitutively by the runtime?

# 30. Forbidden LGRC relabels

The following identifications are forbidden without separate evidence:

```text
packet ledger = retained continuation sector
event queue = memory
proper time = relaxation spectrum
causal delay = continuation softness
lineage = canonical retained-projector transport
pulse surface = read-back
producer reading history = native constitutive read-back
N31 producer mechanism = native LGRC retention
queue persistence = durable formed retention
same coherence trajectory = same LGRC current mechanism
sign-even packet count = orientation retention
lineage endpoint mapping = continuation-mode transport
finite-horizon observer subspace = intrinsic present memory
```

---

# 31. Final closeout requirements

Before GRV-C6, the experiment must produce:

- a corrected version of this specification reflecting repository evidence;
- a machine claim-classification matrix;
- a machine assumption-status matrix;
- completed theory claim ledger, assumption registry, derivation-status appendix, debt register, and traceability matrix;
- a contradiction and theory-reopening register;
- explicit provenance for every result;
- a list of superseded exploratory claims;
- a decision on each candidate GRC extension;
- a frozen unchanged-GRC evidence bundle;
- and the LGRC handoff record.

The authoritative sequence is:

$$
\boxed{
\text{conversation}
\rightarrow
\text{pre-execution specification}
\rightarrow
\text{unchanged repository run}
\rightarrow
\text{corrected evidence-grounded specification}
\rightarrow
\text{selectable implementation tranche, if justified}
\rightarrow
\text{LGRC delta investigation}.
}
$$

---

# 32. Pre-execution checklist

## Theory and provenance

- [ ] Record exact theory commit SHA.
- [ ] Confirm controlling versions of *The Continuation Spectrum* and *Read-Back*.
- [ ] Serialize the claim ledger, assumption registry, derivation-status appendix, debt register, gate dependency map, and theory-to-test traceability matrix.
- [ ] Bind every claim to required assumption IDs and proof-note IDs where applicable.
- [ ] Preregister operational evidence modes and thresholds for `A-NONNORMAL-CONTROL` and `A-FAST-SLOW` where applicable.
- [ ] Freeze the fixed-topology ambient coordinate identification and any branch-dependent inner-product transport.
- [ ] Mark every B1-derived result as `core_derived` or `candidate_constitutive_completion`.
- [ ] Preserve all threshold distinctions.
- [ ] Preserve the passive-null and retained-state sensitivity requirements.
- [ ] Preserve the causal possibility matrix and arrow-by-arrow evidence rule.
- [ ] Preserve axis versus orientation and field versus current equivalence.
- [ ] Preserve the typed graph one-form bridge requirements.
- [ ] Preserve stable retention versus neutrality and instability.
- [ ] Freeze branch-selection and cluster-identity rules.
- [ ] Confirm that no N32, L04, or `pygrc.analysis` decision is encoded.

## Repository baseline

- [ ] Record exact GRC commit SHA.
- [ ] Confirm clean checkout.
- [ ] Run and record the complete existing test suite.
- [ ] Hash dependency and configuration files.
- [ ] Freeze canonical step trace.
- [ ] Confirm no experiment-local source patch is imported.

## Fixtures and instrumentation

- [ ] Validate the existing two-node transport anchor.
- [ ] Freeze node/edge/port ordering.
- [ ] Freeze physical state projection.
- [ ] Freeze the separate causal-state inventory for physically excluded or administratively advancing fields.
- [ ] Freeze JSON canonicalization and digests.
- [ ] Freeze numerical tolerances before scientific execution.
- [ ] Verify no event or topology change across all primary perturbations.

## Scientific gates

- [ ] Certify homogeneous strong branches.
- [ ] Search and certify nonuniform strong branches.
- [ ] Compute complete-step Jacobians with convergence checks.
- [ ] Classify causal $C/W/J$ blocks.
- [ ] Identify or reject isolated slow clusters.
- [ ] Complete the runtime sign audit.
- [ ] Compare frozen-$W$ and full recurrence.
- [ ] Run preparation–persistence–matched-probe controls.
- [ ] Search and classify return orbits.
- [ ] Sweep temporal and spatial-Hessian thresholds.
- [ ] Complete `K` load-bearing and information-loss controls.

## Closeout and handoff

- [ ] Assign the six required implementation statuses and L0-L5 correspondence levels to every proposed correspondence.
- [ ] Complete every row of the theory-to-test traceability matrix.
- [ ] Complete every required assumption status, including `not_applicable`, and distinguish failed assumptions from falsified claims.
- [ ] State the maximum supported claim for every positive row.
- [ ] Record every blocked, ambiguous, and falsified hypothesis.
- [ ] Classify every contradiction and decide whether theory reopening is required.
- [ ] Produce extension decision records without implementing them.
- [ ] Correct this specification to the actual repository evidence.
- [ ] Freeze `lgrc_handoff.json`.
- [ ] Do not begin substantive B1-L until the GRC closeout is accepted.

---

# 33. Final claim ceiling of this specification

This specification may establish a reproducible and theory-bounded account of what unchanged `GRC9V3` realizes from continuation, temporal persistence, recurrent geometry, and historical influence.

It may produce exact requirements for later selectable extensions.

It does not itself establish:

- a native GRC implementation of *Read-Back*;
- a full graph implementation of *The Continuation Spectrum*;
- a unique continuation or retained-sector operator;
- a unified spectrum;
- a final GRC or LGRC substrate;
- or the necessity of N32.

Its success criterion is not a positive read-back result. Its success criterion is that the repository evidence, within explicitly satisfied assumptions, determines:

- which bounded causal arrows are present;
- which equivalence level is supported;
- which theory debts remain open;
- whether an extension, LGRC investigation, analysis-only measurement, or theory reopening is the correct next route;
- and the maximum claim supported by unchanged runtime evidence.

Theory terminology, exploratory calculations, available code surfaces, and desired extensions must not decide one another prematurely.
