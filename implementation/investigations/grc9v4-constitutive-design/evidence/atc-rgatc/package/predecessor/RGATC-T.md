# RGATC-T — section-mediated fission and continuation

**Date:** 2026-09-24  
**Status:** proposed mathematical results, with internal algebraic pressure; not independently reviewed, source-admitted, or native-implemented.  
**Scope:** Candidate A, reconstructed-geometry realization RG2b, one fixed positive beat duration and frozen completion per profile.  
**Companion:** `RGATC-A.md` constructs a nonempty example satisfying the hypotheses below. `check_rgatc_ta.py` checks its quantitative bounds without evaluating an RG section.

## 1. What is inherited, and what is new

The retained RG design [RG] supplies the lagged invariant-section architecture, a fixed-domain graph transform, the inverse/self-map/contraction obligations, and a Lipschitz-only claim ceiling. The Phase-9 graph review [P9-RG] implements a particular finite completion and emphasizes that one-beat containment is not indefinite physical continuation. The CI domain derivation [CI] supplies fixed-geometry Candidate-A current, history, source-obstruction, and target-spectrum estimates. These are used as fixed-geometry lemmas, not as a CI root or CI realization.

The new contribution is a theorem connecting those objects across a source-selected binary fission, together with an explicit boundary-coverage obligation. We also give the graph-transform proof directly in Lipschitz estimates: differentiability of the invariant section, or of every auxiliary completion surface, is unnecessary. This is a mathematical extension of the sufficient construction, not a claim that the existing native completion identifiers already admit every completion covered here.

Three qualifications to the preceding outline are essential.

* A section belongs to a **frozen positive-duration map**. The old variable-request interval cannot be inherited without a new family-of-sections compatibility theorem. Here the duration is fixed.
* A compact set inside the strictly positive resource orthant cannot contain all positive charge-nine states approaching zero. A genuine resource-positivity obstruction requires section coverage through that limiting corridor; a small positive chart alone proves only exit from that chart.
* The old first-step entry below radius 2/3 is duration dependent. Small-duration sections require a new target argument rather than retaining that conclusion by analogy.

These issues are resolved explicitly in RGATC-A, not silently assumed away.

## 2. State, current, and the two different maps

For topology g, let E_g be its finite-dimensional authoritative-state coordinate space, with X=(C,W). Let H_g be the symmetric star-supported geometry space, with reference identity I_g. The identity matrices differ in dimension between the four-edge source and five-edge target.

The fixed-geometry Candidate-A physical proposal is

\[
F_{g,\Delta}(X,H)=(C^+,W^+).
\]

It solves the ordinary fixed-H A current, applies continuity once, rebuilds the descriptor at C^+, and writes W using the current that drove continuity. Define the structural generation map

\[
G_g(X,H)=I_g+\kappa_H S_g(X,H).
\]

The geometry H is held during the ordinary proposal. G does not produce a same-beat corrector.

A frozen completion supplies globally defined maps

\[
\widehat F_g(X,H)=X+\widehat f_g(X,H),\qquad
\widehat G_g(X,H)=I_g+\kappa_H\widehat S_g(X,H).
\]

They agree with the actual physical formulas on a declared physical-agreement set D_g. Auxiliary coordinates used to define these functions are not automatically physically admissible states.

The RG2b section solves

\[
\Gamma_g(\widehat F_g(X,\Gamma_g(X)))
  =\widehat G_g(X,\Gamma_g(X)). \tag{T1}
\]

The physical reduced map is

\[
R_g(X)=F_{g,\Delta}(X,\Gamma_g(X)),\quad X\in D_g, \tag{T2}
\]

subject to ordinary resource and history admission. Neither H nor a previous section value is authoritative state.

In particular, (T1) is not the CI equation

\[
\Gamma_g(X)=G_g(X,\Gamma_g(X)).
\]

The difference in the argument of Gamma is load-bearing.

## 3. A quantitative section theorem

Use the coordinate sup norm on E_g and the Frobenius norm on H_g. On the closed geometry ball B_rho(I_g), assume global bounds for the completed maps:

\[
\begin{aligned}
\|\widehat f(X,H)-\widehat f(Y,H)\|_\infty
 &\le A_X\|X-Y\|_\infty,\\
\|\widehat f(X,H)-\widehat f(X,K)\|_\infty
 &\le A_H\|H-K\|_F,\\
\|\widehat S(X,H)\|_F&\le M_S,\\
\|\widehat S(X,H)-\widehat S(Y,H)\|_F
 &\le B_X\|X-Y\|_\infty,\\
\|\widehat S(X,H)-\widehat S(X,K)\|_F
 &\le B_H\|H-K\|_F.
\end{aligned} \tag{T3}
\]

The geometry ball is required to be positive definite. Choose a section Lipschitz ceiling L and define

\[
\ell=A_X+A_HL<1,\qquad M_{\rm inv}=(1-\ell)^{-1}. \tag{T4}
\]

Require

\[
\kappa_HM_S\le\rho, \tag{T5}
\]

\[
L_{\rm image}=\kappa_H(B_X+B_HL)M_{\rm inv}\le L, \tag{T6}
\]

and

\[
q_\Gamma=\kappa_H\left[B_H+(B_X+B_HL)M_{\rm inv}A_H\right]<1. \tag{T7}
\]

Here kappa_H is positive for the construction below. Absolute value gives the corresponding general gain estimates.

**Theorem T-1.** Under (T3)–(T7), there is exactly one fixed section in the class

\[
\mathcal S=\{\Gamma:E_g\to B_\rho(I_g):\operatorname{Lip}(\Gamma)\le L\}.
\]

It is bounded and Lipschitz, and satisfies (T1). In fact its value bound improves to

\[
\|\Gamma(X)-I_g\|_F\le\kappa_HM_S. \tag{T8}
\]

**Proof.** For Gamma in S, put Psi_Gamma(X)=X+f_hat(X,Gamma(X)). Its increment has Lipschitz constant at most ell. For each Y, X=Y-f_hat(X,Gamma(X)) is a contraction on the complete coordinate space. Thus Psi_Gamma has a unique global inverse, with Lipschitz constant M_inv.

Define

\[
(\mathcal T\Gamma)(Y)
 =I_g+\kappa_H\widehat S(X,\Gamma(X)),
\qquad X=\Psi_\Gamma^{-1}(Y). \tag{T9}
\]

(T5) bounds its values. (T6) bounds its Lipschitz constant. The section class is complete in the uniform norm: it is a closed subset of bounded continuous functions, and the range ball and Lipschitz constraint are closed.

For two sections Gamma and Lambda, let X and Y be the inverse points at the same output coordinate. Then

\[
\|X-Y\|_\infty\le M_{\rm inv}A_H\|\Gamma-\Lambda\|_\infty.
\]

Combining this with

\[
\|\Gamma(X)-\Lambda(Y)\|_F
 \le\|\Gamma-\Lambda\|_\infty+L\|X-Y\|_\infty
\]

gives (T7) as the uniform contraction constant of T. The contraction theorem proves existence and uniqueness. Substitution of the fixed section in (T9) gives (T1) and (T8). No classical derivative of Gamma is used. The inverse is a bi-Lipschitz homeomorphism; no unjustified claim that it is a C1 diffeomorphism is needed. QED.

This uniqueness is **completion-relative**. It does not compare sections selected by different frozen completions.

### Equivariance

Assume the completed maps commute with the decorated graph action, using vertex permutation on C, unsigned edge permutation on W, and signed edge congruence on H. Assume the metrics and section class are invariant under that action. Then T commutes with the induced action on sections. By uniqueness, the fixed section is equivariant. Therefore exact paired C/W states produce exactly paired geometry and current, and ordinary evolution preserves those pairings.

This is an exact theorem, not a conclusion from overlapping interval enclosures. It also applies covariantly across relabeled copies of a declared topology.

### Finite approximation, without claiming an implementation

Starting from Gamma_0=I and applying the exact graph transform gives

\[
\|\Gamma_N-\Gamma\|_\infty
 \le \kappa_HM_S q_\Gamma^N.
\]

A finite evaluator must additionally account for inverse-query and arithmetic errors. This inequality is a mathematical approximation budget, not evidence that such an evaluator was run or that native binary64 publication preserves its bounds.

## 4. Substitution of a certified section into uniform fixed-H estimates

**Lemma T-2.** If a predicate or inequality P(X,F(X,H)) holds for every X in D and every H in a geometry ball, and Gamma(D) lies in that ball, then P(X,R(X)) holds for the RG reduced map.

The proof is substitution. It needs no smoothness or derivative of Gamma. This elementary point is the main reason the existing fixed-H A mathematics can be reused.

The lemma does **not** allow import of a request interval, a CI root certificate, or an asymptotic formula that specifically uses the CI same-state geometry equation. Such premises must be checked separately.

Suppose the source estimates give, for every successful positive proposal,

\[
x(R_s(X))\ge(1+\mu_s\Delta)x(X),\qquad\mu_s>0,
\]

and preserve the history interval and pairings while resources stay positive. If exact charge bounds x above by 9 and the section remains available throughout that entire positive corridor, an indefinitely positive unsplit trajectory is impossible.

The italicized coverage condition is indispensable. Leaving a small certification chart must not be renamed physical resource failure.

## 5. Reconstructive fission

At a successful ordinary poststate X_s^-, compute

\[
H_{\rm evt}=\Gamma_s(X_s^-),\qquad
J_{\rm evt}=J_s(X_s^-,H_{\rm evt}).
\]

A source-only guard and uniquely resolved dyadic current share select k. No reset state or target outcome participates in selection.

Let T_k be the already-declared resource/W fission map: surviving leaf resources unchanged, parent resource split by k/2^16, old W transported by edge lineage, bridge W=1. Use that same k for the current and independent reset roles.

The target section is determined by the target instance of the **predeclared completion recipe**, not chosen after observing target behavior. Define

\[
X_t=T_kX_s^-,\qquad H_t=\Gamma_t(X_t).
\]

There is no state transport of Gamma or H. The two sections have different domains and codomains. There is no need to impose a commutation identity equating source and target geometry across the event. Such an additional identity would be a new contract, not inherited RG2b semantics.

**Theorem T-3.** Suppose each source and target completion satisfies T-1; the source guard is resolved and source-only; both actual role images under T_k lie in a target domain D_t; and uniform fixed-H target inequalities show R_t(D_t) is contained in D_t with positive resources and lawful W. Then the zero-time fission has separately admitted target currents for both roles and each role has indefinite physical RG continuation.

**Proof.** The resource/W maps give the two authoritative target states. Their membership in D_t permits the corresponding section evaluations and current admissions. T-2 supplies one-step invariance of D_t. Induction supplies every subsequent ordinary step. The section values are reconstructed each time; no event geometry history has been introduced. QED.

This is a mathematical event-admission theorem. Atomic publication, receipts, replay, rounding policy, and a production event scheduler are distinct implementation obligations.

## 6. Target convergence and a non-CI discriminator

Assume, in addition,

\[
X_{n+1}\le qX_n,\quad q<1,\qquad
\|S_n\|_F\le sX_n^2,
\]

where X_n now denotes the resource radius, not the full state vector. Along the target physical trajectory, invariance gives

\[
H_{n+1}-I=\kappa_HS_n. \tag{T10}
\]

Consequently

\[
\|H_{n+1}-I\|_F\le\kappa_Hs q^{2n}X_0^2\to0.
\]

The fixed-H current bounds give J_n→0. If the refreshed conductance drive tends to exp(-3 alpha/2), the log writer with a fixed decay in (0,1) gives W_n→exp(-3 alpha/2). Thus the target limits are resource equilibration, zero current, and reconstructed geometry approaching I, without any persistent Z variable.

There is also a useful exact discriminator. The same-state CI geometry residual evaluated on the RG trajectory is

\[
H_n-[I+\kappa_HS_n]=H_n-H_{n+1}. \tag{T11}
\]

If some target H_j differs from I but H_n→I, this residual cannot vanish at every subsequent state. Therefore the complete reconstructed-geometry realization is not secretly a CI fixed-point realization along that whole trajectory. This does not claim a quantified difference in C trajectories between two independently initialized realizations.

## 7. Boundary coverage is a scientific obligation, not chart bookkeeping

For epsilon>0, the source states

\[
C=(\epsilon,\epsilon,\epsilon,\epsilon,9-4\epsilon)
\]

are positive and have x=9-5 epsilon. They approach the resource boundary while remaining in the obstruction cone. Every compact K strictly inside C>0 has a positive minimum resource and excludes sufficiently small epsilon. Therefore the earlier proposed compact positive chart cannot establish coverage of the whole cone.

RGATC-A uses an explicitly declared auxiliary completion through C=0. Negative auxiliary C values are permitted only in the mathematical construction of the frozen section. The physical state and proposal acceptance rules continue to require positive C. This is a **new proposed completion**, not an invocation of the existing native positive-chart certificate outside its domain.

An alternative would require a separately proved boundary-covering atlas or another compatible completion. Merely adding more local runs is not a proof of that compatibility.

## 8. Claim boundary

T establishes a conditional section-mediated ATC theorem and identifies its exact obligations. It does not supply source admission, a native profile, whole-box event formation, arbitrary environments, repeated-event/non-Zeno behavior, a classical section derivative, or completion-independent uniqueness.

RGATC-A now provides an explicit positive-parameter instantiation, rather than leaving the nonemptiness of these hypotheses to future trajectory code.

## Sources

[RG] Retained `GeometryTemporalRealizationSuccessorReconstructedGeometry(3).md`, record GRC9V4-GTRS-RG-v1, sections “RG-2b” and “Local Existence Argument.” Indexed source used; original raw bytes were not available for materialization in this turn.

[P9-RG] Retained `P9-6.4c-Review.md`, “Frozen recipe and norms,” “Theorem tests and finite error,” and the explicit one-beat-versus-indefinite-containment limit. Indexed source used; not a new native-code audit.

[CI] Mounted `ATCCIDomainsAndReference(1).md`, fixed-H estimates and source/target algebra. The prior positive-duration CI conclusions are not relabeled as RG conclusions; the duration-dependent inequalities are rederived in A.

[G5] Retained `ATCSectorChannelsAndRequests.md`, fixed physical writer tau, full-channel current/writer ordering, and ridge-one host descriptor.
