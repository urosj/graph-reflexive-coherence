# RGATC-A — an explicit theoretical A_RG2b fission law

**Date:** 2026-09-24  
**Status:** proposed constructive theorem; sufficient constants and section-envelope implications checked by exact rational/outward arithmetic. Not independently reviewed, source-admitted, or native-implemented.  
**Dependency:** the proved sufficient theorem in `RGATC-T.md`.  
**Reproduction:** `python check_rgatc_ta.py` and `python pressure_rgatc_ta.py`.

## 1. Result and the two real departures from earlier profiles

There is an explicit nonempty A_RG2b research profile for which a successful ordinary source beat produces a source-only fission prescription; both authoritative roles transfer to independently reconstructed target geometry; no-split and W-reset-only controls cannot maintain positive resources indefinitely; and the target has indefinite positive RG2b continuation.

The profile has the same nonzero Candidate-A readback, descriptor, conductance and nonlinear site-potential channels as the previous A work. Its section is genuinely lagged and nonneutral. It has no Z coordinate and uses no CI root or OS corrector.

Two differences must remain explicit:

1. The beat and geometry gain are new, conservative positive values. The old request interval, 71-beat horizon, and first-target-beat radius below 2/3 are not inherited.
2. The completion is a new floor-preserving auxiliary recipe whose resource coordinates extend through zero. It is not already admitted by the shipped strictly positive compact-chart completion. Physical negative resources remain forbidden.

This construction demonstrates theoretical nonemptiness and a complete causal chain. It is not a claim that the selected constants are useful or maximal native operating parameters.

## 2. Fixed graphs, references, and ordinary equations

Use the retained paired graphs:

\[
E_s=\{(0,4),(1,4),(2,4),(3,4)\},
\]

\[
E_t=\{(0,4),(1,4),(2,5),(3,5),(4,5)\}.
\]

Host positions are (1,1,1,1,0) and (1,1,1,1,0,0), respectively. Reference weights, vertex measures, and descriptor ridge are one; H_ref=I and K_base=0. The orientation uses B_ie=+1 at the edge's first endpoint and -1 at its second. Positive source J therefore flows inward from a leaf to its parent.

For fixed H, put

\[
\begin{aligned}
d&=B^TC,\\
\phi&=BWd-p(C)+\kappa_{Ah}B(H-I)d,\\
b&=-WB^T\phi,\\
D_i(C)&=\frac{\sum_{j\sim i}(r_j-r_i)(C_j-C_i)}{1+\sum_{j\sim i}(r_j-r_i)^2},\\
E_e(C,D,j)&=\tfrac12[\alpha(C_u+C_v)+\beta(D_u-D_v)^2+\gamma j_e^2],\\
g_e&=\max(1/2,e^{-E_e(C,D,b)}),\\
q_e&=(W_e-g_e)/(W_e+g_e),\\
J_e&=b_e/(1-\chi q_e),\\
v&=H^{-1}\chi\operatorname{diag}(q)J,\\
S&=\operatorname{Star}(v).
\end{aligned} \tag{A1}
\]

Here W denotes both the edge vector and its diagonal matrix where appropriate; eta, kappa_c, and zeta are one. For these simple graphs Star has entries one on the diagonal times v_i squared, and one-half v_i v_j on edges sharing a vertex. It is symmetric, star-supported and PSD, with trace equal to ||v||_2 squared.

The ordinary proposal at the frozen duration Delta is

\[
C^+=C-\Delta BJ,
\]

\[
\log W^+=a_\Delta\log W+(1-a_\Delta)\log g^+,
\quad a_\Delta=e^{-\Delta/\tau_A},
\]

where g^+ uses D(C^+), C^+, and the same selected J. The structural source is that of the pre-continuity read. These are the retained fixed-H Candidate-A equations, not a new current or writer law.

## 3. Explicit positive parameters

Fix

\[
\begin{gathered}
\alpha=\beta=3/8192,\qquad \gamma=3/4096,\qquad
\chi=3/64,\qquad \kappa_{Ah}=3/4,\\
p(c)=\frac{19}{4}c+\frac{c^2}{2\cdot65536},\qquad
\tau_A=\frac1{8\log2},\\
\boxed{\Delta=2^{-25},\qquad \kappa_H=2^{-32}.}
\end{gathered} \tag{A2}
\]

On [0,9], the nonlinear slope deviation is at most 9/65536<1/2048. All conductance channels, readback, geometry-to-potential coupling, and structural generation are nonzero.

The new beat is approximately 2.98e-8 and the geometry gain approximately 2.33e-10. They are deliberately conservative existence parameters. The physical tau is unchanged; it is not retuned to make the writer a half-step.

A zero-duration read would inspect the section belonging to this positive Delta. It must not replace the frozen section by a zero-duration section.

## 4. The proposed completion

For a real interval [a,b] inside [A,B], define a cubic cutoff equal to one on [a,b], zero outside (A,B), and use 3t^2-2t^3 on each transition after rescaling. It takes values in [0,1] and has zero endpoint derivative.

Use the resource cutoff

\[
\vartheta_C=1\text{ on }[-1,10],\quad
\vartheta_C=0\text{ outside }(-2,11),
\]

and the mobility cutoff

\[
\vartheta_W=1\text{ on }[3/4,5/4],\quad
\vartheta_W=0\text{ outside }(1/2,3/2).
\]

For each graph, set

\[
\beta_g(X)=\prod_i\vartheta_C(C_i)\prod_e\vartheta_W(W_e).
\]

Let f_raw=F_raw-X be the literal algebraic proposal from (A1), including its conductance floor and refreshed writer. Its auxiliary evaluation permits real C in the support rectangle but always has W>0 and H positive definite. Define

\[
\widehat F_g=X+\beta_g f_{\rm raw,g},\qquad
\widehat G_g=I+\kappa_H\beta_g S_g. \tag{A3}
\]

Where beta is zero, the completed maps are defined directly as X and I; logarithms at nonpositive auxiliary W are never evaluated.

The conductance floor is preserved, not silently removed. In the auxiliary region its effective exponent is min(E,log2). This cap is 1-Lipschitz, so all estimates below remain valid across its kink. The completion is globally Lipschitz; its physical-agreement regions are floor-inactive and smooth. T-1 does not require a C1 auxiliary cap or a C1 invariant section.

Every positive charge-nine source state, and every target state used below, has 0<C_i<9 and W in [24/25,1]. Hence beta is exactly one there. No resource cutoff is activated as a positive unsplit trajectory approaches zero.

The negative C values are **auxiliary completion coordinates only**. A physical proposal with any C_i^+<=0 fails before history publication. The completion is not an authorization to continue a physical trajectory with negative charge density.

The source and target use the same cutoff formula and endpoints. Only their graph incidence and number of coordinates differ. There is no outcome-selected target completion. The section is nevertheless completion-relative: this recipe is a constitutive configuration, not a uniquely forced choice among all possible completions.

## 5. Quantitative confirmation of T-1

Use state sup norm, geometry Frobenius norm, and

\[
\rho=1/4096,\qquad L=1/2.
\]

The common graph counts are n<=6, m<=5, and maximum degree at most four. Every host increment has magnitude at most one. On the outer support, |C_i|<=11 and 1/2<=W_e<=3/2. A WLS row has l1 norm less than two, so |D_i|<=22 and |D_u-D_v|<=44.

The following are sufficient common bounds, for the whole old positive scalar box in alpha, beta, gamma, chi, kappa_Ah and the quadratic potential subclass. They are not fitted to the anchor:

| Quantity | Value bound | State Lipschitz bound | Geometry Lipschitz bound |
|---|---:|---:|---:|
| Baseline b, edge sup norm | 600 | 2^10 | 2^9 |
| Selected J, edge sup norm | 2^10 | 2^16 | 2^14 |
| Causal-flat v, Euclidean norm | 2^9 | 2^19 | 2^17 |
| Raw S, Frobenius norm | 2^18 | 2^29 | 2^27 |
| Raw complete state increment f | 2^16 Delta | 2^22 Delta | 2^20 Delta |

The main derivations are as follows.

**Baseline.** ||B^TC||_2<50, each incidence row has Euclidean norm at most two, the weighted stiffness at a vertex is at most 132, and |p(C_i)|<53. Therefore |phi_i|<186 and |b_e|<600. State variations give a stiffness bound 100, site-slope bound 5, and geometry-to-state contribution below 10 rho, hence a phi state bound below 106. Its H bound is at most 100. The displayed baseline Lipschitz constants follow by the product rule with W<=3/2.

**Current.** The read exponent has bounds |E|<256, Lip_X(E)<2^10, Lip_H(E)<2^9. Clipping E to min(E,log2) does not enlarge these bounds. Since log W has Lipschitz constant two, q has bounds |q|<1, Lip_X(q)<=2^10 and Lip_H(q)<=2^8. The current denominator is at least 15/16. Product/quotient estimates give the stated J constants.

**Source.** ||H^-1||_2<2 and its inverse-difference coefficient is below four. Applying these to v=H^-1 chi qJ gives its displayed constants. The normalized Star map satisfies ||Star(v)||_F<=||v||_2^2 and the bilinear difference bound (||v||+||w||)||v-w||. Thus its constants are 2^18, 2^29, 2^27.

**Writer.** For Delta<=2^-22, the post-C values are bounded by 12 and their state Lipschitz coefficient is below two. The refreshed writer exponent has bounds 2^10, 2^17 and 2^15. Also theta=1-a_Delta<8 Delta and |log W|<1. Writing f_W=W(exp(z)-1), with z=theta(log g^+-log W), gives |z|<2^14 Delta. The bounds exp(|z|)<2 and |exp(z)-1|<=2|z| give the increment constants in the table. The current in g^+ is the selected current, not a poststate current.

**Cutoff.** The product cutoff has sup-norm Lipschitz constant at most (3/2)n+6m<=39<64. Consequently the completed constants can be taken as

\[
A_X=2^{23}\Delta,\quad A_H=2^{20}\Delta,
\quad M_S=2^{18},\quad B_X=2^{30},\quad B_H=2^{27}. \tag{A4}
\]

At (A2), direct rational substitution gives

\[
\boxed{\ell=17/64,\qquad M_{\rm inv}=64/47,}
\]

\[
\boxed{L_{\rm image}=17/47<1/2,\qquad q_\Gamma=2/47<1,}
\]

\[
\boxed{\|\Gamma_g-I\|_{\infty,F}\le2^{-14}<\rho.} \tag{A5}
\]

The same proof works separately for source and target. T-1 therefore supplies their unique bounded Lipschitz sections, and equivariance supplies their exact decorated symmetry. These statements precede any numerical section evaluation. The checker reproduces these exact fractions.

Because the inequalities are strict, the construction is not confined to a single isolated parameter point. Nearby fixed profiles also satisfy them. This statement does not authorize changing the beat or completion during a run.

## 6. New duration-dependent physical inequalities

Let K=1/2048, r=1/783, M=24/25, rho=1/4096. The inherited fixed-H source-current error is

\[
E_s=90\rho+r(11/2+90\rho).
\]

Before substituting a request endpoint, the source incidence inequality is linear in the actual beat duration. Thus

\[
x^+\ge(1+\mu_s\Delta)x,
\]

\[
\mu_s=\frac52\left(\frac{19}{250}-6K-\frac23E_s\right)
=\frac{16152197}{120268800}>\frac18. \tag{A6}
\]

This holds on the paired positive source cone x>=3, Q=9, W in [M,1], for every section value in the rho ball. The history interval is invariant for any positive Delta whenever the resource proposal succeeds, because the refreshed conductance is in [M,1] and the log writer is a convex interpolation. No half-writer assumption is involved.

The target weighted spectral interval on the mean-zero space is

\[
\lambda\in[M(7/16),73/16].
\]

For 0<Delta<=1/8, all bare multipliers 1-Delta lambda(19/4-lambda) are positive. Their damping rate is bounded below by

\[
\delta_0=219/256.
\]

The fixed-H potential/readback/geometry error rate is

\[
E_t=\frac52\left[\frac52K+\frac{125}{8}\rho
+r\left(4+\frac52K+\frac{125}{8}\rho\right)\right].
\]

Therefore

\[
X^+\le(1-\delta_t\Delta)X,
\qquad
\delta_t=\delta_0-E_t
=\frac{2662247}{3207168}>\frac34, \tag{A7}
\]

where X=||C-(3/2)1||_2. These are new h-dependent conclusions from the retained fixed-H algebra. They do not extend the old CI root or request certificate by assertion.

### Positivity on the larger target ball

The target starts in X<=3/2, not necessarily X<2/3. Charge nine gives sum(C_i-3/2)=0, hence

\[
|C_i-3/2|\le\sqrt{5/6}\,X<(11/12)X.
\]

Thus X<=3/2 implies every C_i>1/8. By (A7), the entire target ball is invariant; positivity and W invariance follow inductively. Eventually X<2/3 and the familiar 5/6 lower resource bound applies, but no first-beat claim of that kind is made.

## 7. A source-only onset and allocator, without evaluating Gamma

The existence of a section is not used as an excuse to insert a hand-picked H. The certificate instead bounds every H in its proved global ball. Choose the exact inactive source

\[
x_0=3-\Delta,\quad y_0=2^{-24},\quad
u_0=99/100-2^{-30},\quad v_0=99/100+2^{-30}.
\]

Here u_0 and v_0 are the two source edge weights. Resources are

\[
C_0=((9-x_0)/5+y_0,(9-x_0)/5+y_0,
      (9-x_0)/5-y_0,(9-x_0)/5-y_0,(9+4x_0)/5),
\]

with W=(u,u,v,v). The two exact decorated sectors are distinct because u<v.

Enclose the unknown initial section value using ||Gamma_s-I||_F<=2^-14. Evaluate the fixed-H ordinary formulas on an entrywise interval box containing that entire Frobenius ball. The resulting intervals contain the exact RG ordinary successor, even though Gamma_s was never approximated.

At the poststate use a stronger **RG-specific** implication:

\[
\Gamma_s(X_1)-I=\kappa_HS(X_0,\Gamma_s(X_0)). \tag{A8}
\]

The preceding read bounds the right-hand side. This gives a much smaller fresh-event geometry ball, rather than solving a CI root or carrying the old geometry as state.

Outward rational arithmetic proves the following rounded display enclosures (the JSON retains exact endpoints):

\[
3.0000000582690<x_1<3.0000000590793,
\]

\[
5.95236\times10^{-8}<y_1<5.96857\times10^{-8}.
\]

The poststate W sectors remain strictly ordered. Both fresh sector inflows are positive, and

\[
32768.0116284
<2^{16}\frac{J_0+J_1}{J_0+J_1+J_2+J_3}
<32768.0124878.
\]

The complete interval lies strictly inside the round-even cell (32767.5,32768.5). Consequently

\[
\boxed{k_{\rm RG}=32768,\qquad \lambda_{\rm RG}=1/2.} \tag{A9}
\]

This value is a proved consequence of the source envelopes, not a prescribed target value. The calculation uses neither reset data nor target evaluation. The geometry bound at this event is below 1.406e-17. Its diagonal is nevertheless provably nonneutral: (Gamma_s(X_1)-I)_00>3.44e-18.

These are interval **implications for the unknown exact invariant section**, not a numerical RG trajectory, a section table, or a search over candidate sections.

## 8. Complete transfer and target continuation

Use the independent reset source

\[
x_r=13/4,\quad y_r=-1/100,\quad u_r=97/100,\quad v_r=99/100.
\]

It has its own C/W and no vote in the allocator. Apply (A9) to both roles: parent C is halved, leaves survive, old W follows lineage, bridge W=1. Exact charge is preserved by the transfer matrix; equality of outward interval sums is not the charge proof.

The general reviewed transfer coordinates satisfy

\[
X_t^2\le12(2/5)^2+4(1/50)^2+2(23/320)^2
=2472873/1280000<9/4,
\]

and the funding surplus is at least

\[
\boxed{1303/1600>0.}
\]

For the two particular roles, conservative interval target radii are approximately 1.039231 and 1.212601. Both are in the target invariant ball and have positive resources and lawful histories.

For each, independently define H_t=Gamma_t(C_t,W_t) and solve the fixed-H A current. T-1 and the fixed-H current margin guarantee admission. No source H or Gamma is transported and no independent carrier is initialized. By (A7), every subsequent ordinary target step is admitted in exact-real arithmetic.

The existing operation-support discrimination is unchanged:

\[
5M-19/4=1/20>0,
\qquad
19/4-73/16=3/16>0.
\]

The four-contact source carries the obstructed support; the two-sector double-star fission changes that support and moves the target spectrum to the restorative side. This is not a grouping-only result.

## 9. Physical counterfactuals and limits

Without the split, and after a one-time reset W:=1 without splitting, (A6) holds on every successful positive source beat. Both stay within the physical-agreement region whenever resources stay positive; the auxiliary cutoff cannot rescue them by changing the equations.

Using the weaker multiplier 1+Delta/8, let

\[
N=16/\Delta=536870912.
\]

Strict Bernoulli gives (1+Delta/8)^N>3. Thus x_N>9 from x_0>=3, contradicting positive charge-nine resources. Some proposal must therefore fail resource positivity by that bound. This is not a claim that N beats were executed. The bound is loose and equals 16 model-time units; it is an existence argument, not an efficient simulation specification.

There is no state-level H reset or Gamma reset. Replacing the section by I would be a profile ablation, not the analog of resetting PC's authoritative Z.

On the target, (A7) gives X_n<=q^n X_0 with q=1-(3/4)Delta. Uniform fixed-H bounds give J_n→0 and ||S_n||_F<=sX_n^2. The lagged identity (A8), now on the target, gives

\[
\Gamma_t(X_{n+1})-I=\kappa_HS_n\to0.
\]

The actual fixed-tau log writer gives W_n→exp(-3 alpha/2)1. Therefore

\[
\boxed{C_n\to(3/2)1,\quad J_n\to0,\quad
W_n\to e^{-3\alpha/2}1,\quad\Gamma_t(X_n)\to I.} \tag{A10}
\]

The envelope certificate also proves S_00>0 at an ordinary target read for each role. Hence a subsequent target section value is nonneutral. Together with (A10), T-11 proves that the CI same-state geometry residual is nonzero somewhere on the target continuation. RG2b has not collapsed into CI or a constant identity section.

At the source event the preceding causal-flat components have the same nonzero sign, and all leaf-parent resource differences have the opposite sign. The resulting S has positive diagonal and nonnegative entries. Thus S B^TC is nonzero. Since the source is a tree, its incidence has trivial edge kernel, so the geometry-to-potential contribution B(Gamma-I)B^TC is genuinely nonzero as well. The nonzero H is not merely an unused decoration.

## 10. What was actually checked

`check_rgatc_ta.py` checks the powers-of-two majorants, the exact T fractions, the new source and target rates, the transfer/funding inequalities, and whole-section-envelope source onset/selection and both-role target admission. It uses one unchanged retained outward arithmetic kernel; it does not call its old scientific trajectory routines.

`pressure_rgatc_ta.py` regenerates the certificate twice, checks equality to the retained JSON, verifies the exact theorem fractions, checks the dyadic-cell margin, exhibits the positive-boundary coverage problem, and explicitly rejects reuse of the old large-step first-entry conclusion. These are internal checks, not an independent auditor's PASS.

There were **zero RG section evaluations**, no native A_RG2b steps, no CI roots, no OS passes, and no PC carriers. The computational aid verifies finite mathematical inequalities; it does not search for the mechanism or claim an executed RG reference.

## 11. Disposition and next boundary

RGATC-T has a proved sufficient theorem. RGATC-A satisfies it with an explicit frozen completion and positive profile, and supplies a bounded exact-real ATC causal chain. The conclusion is not merely “provided a suitable section happens to exist.”

The proposed completion and its new duration/gain still require independent scientific review and source admission. Its auxiliary negative-C construction and global Lipschitz floor handling must be stated in any successor specification. The existing native completion identifiers must not be reinterpreted silently.

An executable RG section/reference, numerical error and rounding contracts, native profile support, lifecycle/replay, broader useful parameter domains, active environments, and aggregate ATC-2 remain open. The very conservative existence profile does not demonstrate practicality or full strength at the larger gains used by CI/PC.

No origin or realization-local debt ledger is modified by this package. The natural next step is review of this theorem and completion, not another search for a partition or another history-transport policy.
