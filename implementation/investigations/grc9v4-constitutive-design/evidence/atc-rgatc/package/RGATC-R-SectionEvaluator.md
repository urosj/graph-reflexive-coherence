# RGATC-R — certified finite invariant-section evaluation

**Date:** 2026-09-24  
**Status:** new research implementation and accompanying proof, internally tested; not independently accepted, source-admitted, or native-implemented.  
**Dependencies:** the frozen `predecessor/RGATC-T.md` and `predecessor/RGATC-A.md`. Their completion, physical parameters, and theorem are unchanged.

## 1. The missing executable object

T/A proved that a unique invariant section exists for each of the paired graphs, and derived a complete causal witness using enclosures for all admissible section values. It executed no section queries. The present evaluator computes a finite approximation to the actual completion-relative section, with an explicit error bound. It does not select a convenient H from the geometry ball.

The fixed parameters remain

\[
\Delta=2^{-25},\qquad\kappa_H=2^{-32},\qquad
\tau_A=\frac1{8\log2}.
\]

The current, descriptor, conductance, floor, refreshed W writer, and auxiliary cutoff are the exact T/A formulas. There is no CI solve and no PC carrier. The source and target differ only through their predeclared incidence and host-reference data.

## 2. A finite forward ladder is an iterated graph transform

Write the completed skew-product map as

\[
\mathcal A(X,H)=\bigl(\widehat F(X,H),\widehat G(X,H)\bigr).
\]

Let \(\Gamma_0(X)=I\), and \(\Gamma_{i+1}=\mathcal T\Gamma_i\), where \(\mathcal T\) is the graph transform of RGATC-T. For an arbitrary exact initial coordinate \(X_0\), define the finite auxiliary ladder

\[
(X_{i+1},H_{i+1})=\mathcal A(X_i,H_i),\qquad H_0=I.
\]

**Lemma R-1.** Every ladder point satisfies

\[
H_i=\Gamma_i(X_i).
\]

**Proof.** This holds for \(i=0\). If it holds at \(i\), then
\(X_{i+1}=\Psi_{\Gamma_i}(X_i)\). The globally invertible base map from T/A gives
\(X_i=\Psi_{\Gamma_i}^{-1}(X_{i+1})\). The definition of the graph transform therefore gives
\(H_{i+1}=\widehat G(X_i,\Gamma_i(X_i))=\Gamma_{i+1}(X_{i+1})\). Induction proves the assertion. No same-state current/geometry equation is substituted. QED.

Consequently, to evaluate \(\Gamma_N(Y)\), one can solve for an initial ladder coordinate whose final state is Y. This avoids recursively nesting an inverse solver inside every graph-transform evaluation.

The ladder is numerical work inside one section query. Its intermediate H values are **not previous physical geometry**, and its intermediate C/W coordinates are **not additional physical beats**. Every fresh query starts again at \(H_0=I\). Neither the ladder nor its initial-coordinate guess is serialized as authoritative state.

## 3. An output-residual certificate

The retained T/A constants are

\[
R=\frac1{16384},\qquad q_\Gamma=\frac2{47},\qquad L=\frac12.
\]

Thus

\[
\|\Gamma_N-\Gamma\|_\infty\le Rq_\Gamma^N,
\qquad \operatorname{Lip}(\Gamma_N)\le L.
\]

Take an exact rational ladder seed. An outward interval execution encloses its exact final state \(X_N\) by \(\mathbb X_N\), and its exact final geometry \(H_N\) by \(\mathbb H_N\). Let \(H_c\) be a rational midpoint matrix. For a query center \(Y_c\), define

\[
e_H\ge\sup_{H\in\mathbb H_N}\|H-H_c\|_F,
\]

\[
e_X\ge\sup_{X\in\mathbb X_N}\|X-Y_c\|_\infty.
\]

For a query box \(\mathbb Y\), let

\[
w\ge\sup_{Y\in\mathbb Y}\|Y-Y_c\|_\infty.
\]

**Theorem R-2.** Every exact query point \(Y\in\mathbb Y\) satisfies

\[
\boxed{
\|\Gamma(Y)-H_c\|_F
\le e_H+L(e_X+w)+Rq_\Gamma^N.
}
\]

**Proof.** By Lemma R-1, the exact ladder endpoint obeys \(H_N=\Gamma_N(X_N)\). Insert \(\Gamma_N(Y)\) and use, successively, the uniform graph-transform tail, the Lipschitz bound of \(\Gamma_N\), and the arithmetic enclosure of \(H_N\):

\[
\begin{aligned}
\|\Gamma(Y)-H_c\|_F
&\le \|\Gamma(Y)-\Gamma_N(Y)\|_F
 +\|\Gamma_N(Y)-\Gamma_N(X_N)\|_F
 +\|H_N-H_c\|_F\\
&\le Rq_\Gamma^N+L\|Y-X_N\|_\infty+e_H\\
&\le Rq_\Gamma^N+L(w+e_X)+e_H.
\end{aligned}
\]

QED.

The residual is measured at the **final output coordinate**, so no additional multiplication by an N-fold inverse Lipschitz constant is needed. Such a factor would be required to bound the initial seed error, which is not the quantity used here.

The numerical inverse iteration is only a proposal mechanism. Its apparent convergence does not prove section existence, uniqueness, or approximation accuracy. The accepted output must pass the displayed inequality.

## 4. The concrete query algorithm

The reference uses N=24 and at most 16 deterministic inverse corrections. Its initial seed is the query midpoint. One correction is

\[
X_0\leftarrow X_0-\bigl(\operatorname{mid}(\mathbb X_N)-Y_c\bigr).
\]

Each correction executes the entire completed ladder from identity. It then computes all four terms in Theorem R-2. The query returns only if their sum is at most \(10^{-34}\), and its resulting matrix enclosure lies in the inherited H ball of radius \(1/4096\).

At N=24, the exact global truncation term is

\[
\frac1{16384}\left(\frac2{47}\right)^{24}
\approx7.5849263161\times10^{-38}.
\]

The inverse work is bounded by 24×16=384 completed-map evaluations per ordinary section query. Matrix dimensions are fixed at four or five. A query whose input width, truncation term, or residual prevents certification fails closed. The reference does not claim that this finite budget succeeds at every point of the global mathematical section domain.

A depth-28 refinement with a \(10^{-40}\) budget is included as pressure. A deliberately insufficient depth and deliberately insufficient inverse work both reject. This prevents numerical stagnation from being mistaken for a certified section.

## 5. Arithmetic, cutoff, and floor

The original 256-bit outward fixed-grid rational interval kernel is retained byte-for-byte. New interval exp and log wrappers have explicit remainders:

* Exponential endpoints are range-reduced to absolute argument at most 1/8. A degree-50 Taylor polynomial is enclosed with remainder no greater than \((1/8)^{51}/(51!\,[1-1/(8\cdot52)])\), then squared back with outward operations.
* For log on [1/2,3/2], the atanh series uses 96 terms and the bound \(2(1/3)^{193}/(193[1-1/9])\).

Endpoint monotonicity produces interval enclosures. These formulas are separately compared with 110-digit Decimal evaluations; the comparisons are diagnostics, while the explicit remainder inequalities justify the enclosures.

The auxiliary conductance is implemented through the algebraically equivalent capped exponent

\[
\log g=-\min(E,\log2).
\]

It is not a floor-free substitute. An auxiliary test actually activates the floor and cutoff. A separate outside-support test uses nonpositive W and proves that the zero-cutoff branch returns identity without attempting an invalid logarithm. None of those auxiliary coordinates becomes a physical state.

Where an interval straddles an outer support boundary, raw coordinates may be clipped to the support for evaluation of the bounded increment. The cutoff includes zero on the outside portion. This encloses the completed increment without evaluating logarithms at nonpositive W; the original coordinate, not its clipped value, remains the identity term of \(\widehat F\).

## 6. Independent numerical implementation

`rgatc_oracle.py` imports only Decimal and Fraction. It builds the fixed-H equations in edge-local form, implements its own dense causal-flat solve, preserves the same floor and cutoff, and uses 110-digit arithmetic. It evaluates a deeper N=28 graph transform and begins its inverse search from a predicted backward displacement rather than the reference's unshifted midpoint.

It shares the declared mathematics and input profile, not the reference's arithmetic, current evaluator, section solver, writer, or transfer function. It is an independent numerical cross-check, not independent scientific acceptance and not a second proof of Banach's theorem.

## 7. Readmission and the RG/CI distinction

An ordinary physical step performs:

\[
(C,W)\to\Gamma(C,W)\to J\to C^+\to D(C^+)\to W^+.
\]

It then evaluates \(\Gamma(C^+,W^+)\) afresh. The generated geometry from the consumed read is compared with that independent new query. Their certified difference encloses zero, as the lagged invariance equation requires.

By contrast, the same-state CI residual

\[
\Gamma(C,W)-[I+\kappa_HS(C,W,\Gamma(C,W))]
\]

is demonstrably nonzero at the actual source and target witnesses. Its magnitude is resolved well above the section error. The implementation is not a CI fixed point wearing an RG2b name.

## 8. Authority and limits

The section geometry, inverse seed, and ladder history are derived diagnostic objects. Authoritative state contains only C/W and immutable provenance/lifecycle fields. Both topology roles reconstruct their target geometry independently; no source H is resized or transported.

This evaluator implements the **new T/A completion**, not the previously shipped native RG2b completion identifier. T/A's auxiliary extension and conservative parameters remain scientific conditions requiring independent review. The finite reference is a certified subset of the exact mathematical domain; failed finite certification is not itself a physical-obstruction theorem.
