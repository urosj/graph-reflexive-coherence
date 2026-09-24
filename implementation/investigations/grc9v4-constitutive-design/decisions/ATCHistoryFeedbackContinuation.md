> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# Degree-two support with Candidate A retained-history feedback

Status: independent review PASS for the coupled conditional mathematics,
with scope/debt clarifications applied. This restores one genuine V4 channel
without changing the reviewed checker/certificate, zero-feedback experiments,
admitted claims, substrate, paper or specifications. Mathematical review is
not formal claim admission or native conformance.

The [partition review](./ATCPartitionDependentStability.md) settled the separate
graph-only question. Here the graph returns to the original degree-two map.
The result is a nonzero finite coupling interval with full resource/history
return, not a calculation that freezes history while testing resources.
Its theorem is for the fixed four-node tree and the conductance-depressed
domain exp(-1/128)<=W_e<=1, not arbitrary small positive or negative log history.

## 1. Selected channel and authority boundary

Candidate A is useful here because retained W enters both its direct mobility
and the stiffness term in its direct potential. Its current-squared writer
then changes W for the next beat. We restore that channel alone:

$$
\alpha=\beta=\chi_A=\zeta_A=\kappa_{Ah}=0,\qquad \gamma\ge0.
$$

Use the OS reduced slice with fixed identity Hodge, zero structural geometry
source, no carrier and no read-back contribution. Its predictor and selected
corrector coincide on this slice. Zero structural source does not turn off
the Candidate A W writer; W is an independent, evolving state coordinate.

The equations come from [the specification's Candidate A contract](../../../../specs/grc-v4-spec.md)
and [the paper's §§8.8–8.10](../drafts/2026-09-GRC-V4.md), checked against
[the production current/writer definitions](../../../../src/pygrc/models/grc_v4_candidate_a.py)
without modifying or executing a new production law. The writer receives
post-continuity resources and the **selected incoming-state current**. Since
alpha=beta=0, its resource/gradient dependence vanishes here, but its staging
does not change. W written on this beat cannot enter the same beat's current.

Typed forensic `contract_provenance` queries are retained in the
[certificate](../evidence/autonomous-topology-change/ATCHistoryFeedbackCertificate.json).
The three parent contracts `D10.2-EC-PARENT-A-GW-FUNCTIONAL`,
`D10.2-EC-PARENT-A-WRITER-TARGET` and `D10.2-EC-PARENT-A-RETAINED-WRITER`
still report `indeterminate_requires_review`. The optional
`P9-EC-A-INITIALIZER-REFERENCE-PASS` has support disposition `["required"]`
within its own claim/domain boundary. Exact current-source discovery is not
promotion of those parent edges or admission of this research model.

The multiwell potential remains absent from the native evaluator/initializer
domain. The old proposed potential binding fixes gamma=0 and all-one W; it
is neither edited nor reused as authority for the present channel. This new
research declaration is `ATC-A-CURRENT-SQUARED-HISTORY-v1_not_runtime_registered`.
No claim that an installed profile or event owner accepts it is made.

## 2. Full staged research map

Keep the original polynomial and parameters:

$$
p(c)=(c-1)(c-5/4)(c-3/2)(c-9/4)(c-3),\quad
\eta=1/4,\quad \kappa=1/1024,\quad h=1/64.
$$

The target order is (a,c,u,v), with edges a to u, v to c and u to v. Its
tail-positive incidence and unweighted Laplacian are

$$
B=\begin{pmatrix}1&0&0\\0&-1&0\\-1&0&1\\0&1&-1\end{pmatrix},
\qquad L_0=BB^\top.
$$

Let y=log W, D_w=diag(exp y), L_w=B D_w B-transpose. Choose
W_floor=1/2 and tau_A=h/log 2, so the exact retention factor rho=1/2.
With componentwise squares, the selected current and full state update are

$$
g_w(C)=p(C)-\kappa L_wC,\qquad
J=\eta D_w B^\top g_w(C),\qquad C^+=C-hBJ,
$$

$$
y^+=\rho y+(1-\rho)\log\max(W_{\rm floor},e^{-\gamma J^{\odot2}/2}).
$$

The floor is proved inactive below, giving
y+ = rho y - (1-rho) gamma J squared/2. Both factors D_w in the current
matter: using W in mobility while silently keeping the stiffness at L_0
would be a different law. tau_A=h/log 2 and all the return bounds are exact
mathematics, not claims about bit-exact binary64 tau or infinite rounded runs.

### Equilibrium and actual coupled tangent

On the charge-5 plane, the old equilibrium persists:

$$
C^*=(1-t_*,1-t_*,3/2+t_*,3/2+t_*),\quad 0<t_*<1/256,
\qquad W^*=\mathbf1,\quad J^*=0.
$$

Here t* is the unique root in that interval of

$$
g(t)=p(3/2+t)-p(1-t)-2\kappa(1/2+2t).
$$

The original slope bounds imply g'>0 and the exact endpoint values have
opposite signs. On this closed tree, a stationary C requires BJ=0. Since B
has full column rank, J=0; a stationary writer then requires y=0. Thus this
channel produces consequential transient memory, not nonzero resting memory.

The tree supplies this immediate rank argument and, critically, the unique
edge coordinates and positive edge-coordinate spectral gap used in the return
proof below. On a cyclic graph BJ=0 alone does not imply J=0. However, the
review's proposed stationary-cycle-current exception does not occur under
this particular purely gradient law with positive D_w: on any closed graph,

$$
0=g_w^\top BJ
=\eta(B^\top g_w)^\top D_w(B^\top g_w)
\quad\Longrightarrow\quad B^\top g_w=0\quad\Longrightarrow\quad J=0.
$$

Thus any full equilibrium of this reduced channel also has W=1, even on a
cyclic graph. That stationary implication does not prove existence, uniqueness
or return there. Cycles can carry nonzero divergence-free currents for other
current laws; here such a current cannot simultaneously be this weighted
potential gradient. The full finite-domain return theorem remains specific
to the declared tree. No cyclic-graph return result is added.

Write C=C*+Bx, uniquely on the charge plane, and define A=B-transpose B and
d*=B-transpose C*. Then

$$
A=\begin{pmatrix}2&0&-1\\0&2&-1\\-1&-1&2\end{pmatrix},\qquad
\operatorname{spec}(A)=\{2,2-\sqrt2,2+\sqrt2\}.
$$

If H_edge=B-transpose [diag(p'(C*))-kappa L_0] B, the full linearization in
(x,y) is

$$
\begin{pmatrix}
I-h\eta H_{\rm edge}&h\eta\kappa A\operatorname{diag}(d_*)\\
0&\rho I
\end{pmatrix}.
$$

The off-diagonal history-to-resource block is nonzero. The reverse forcing
starts quadratically because the derivative of gamma J squared vanishes at
J*=0. Consequently the local eigenvalues do not depend on gamma; this does
**not** prove a finite basin for arbitrary gamma. The following nonlinear
estimate supplies an explicit finite domain instead.

This is the bounded theoretical distinction: absence of a linear eigenvalue
effect does not imply causal absence. The finite-amplitude writer-to-next-read
effect is proved in §5, and the nonlinear sufficient bounds depend on gamma.
We do not infer that the actual attraction basin changes with gamma merely
because its sufficient certificate does.

## 3. Uniform finite-domain return, including evolving history

Use the reviewed coordinate box I_o=[31/32,33/32], I_c=[47/32,49/32].
The old exact Bernstein bounds, independently reconstructed by this checker,
give

$$
m_o=\frac{193221}{1048576},\quad m_c=\frac{109445}{1048576},\quad
M=\frac{493253}{1048576},\quad
\mu=\min(m_o,m_c)-4\kappa=\frac{105349}{1048576}>0.
$$

The equilibrium's coordinate-boundary clearance is at least 7/256. Define

$$
X=\|x\|_2,\quad Y=\|y\|_\infty,\quad R=\bar b=1/128,
\quad X\le R,\quad -\bar b\le y_e\le0.
$$

Since ||Bx|| <= 2X <= 1/64 < 7/256, this rectangle lies inside the slope
box. Its resources are at least 251/256. Also W >= exp(-1/128) > 127/128,
well above the floor. On this domain ||D_w||<=1 and ||D_w-I||<=Y.
The one-sided, conductance-depressed condition is essential to both estimates:
for W>1 the corresponding bounds acquire exponential factors. This theorem
does not extend to arbitrary inherited Candidate-A histories by calling them
"small." The boundary W=exp(-1/128) is included.

Let g_0(x)=B-transpose [p(C)-kappa L_0 C], which vanishes at x=0. Then

$$
J=\eta D_w\{g_0(x)-\kappa A(D_w-I)(d_*+Ax)\}.
$$

The derivative of g_0 has eigenvalues in [mu/2,4M], and h eta 4M<1.
The unit-W resource map therefore contracts X by at most 1-h eta mu/2.
Use ||d*|| < T=195/256 and ||A||<4. Direct perturbation gives

$$
X^+\le q_xX+B_cY,\qquad \|J\|_2\le\eta(A_jX+D_cY),
$$

where all constants are fixed independently of the incoming state:

$$
A_0=4M+16\kappa,\quad A_j=4M+16\kappa\bar b,\quad D_c=4\kappa T,
$$

$$
q_x=1-h\eta(\mu/2-A_0\bar b),\qquad B_c=h\eta D_c.
$$

Specifically the perturbation from D_w-I contributes at most
eta Y[(4M+16 kappa)X+4 kappa T] to the unit-W current. The resource bound
uses Y<=bbar in its X coefficient, while the current bound uses
||D_w||<=1. They must not be conflated.

Take Gamma=256. The current norm is at most
j_max=494065/134217728. The following exact margins prove invariance:

$$
R-q_xR-B_c\bar b=\frac{1088395}{1099511627776}>0,
$$

$$
\bar b-\Gamma j_{\max}^2/2
=\frac{855411403551}{140737488355328}>0.
$$

The resource margin is small, approximately 9.90e-7, but exactly positive;
it is not a numerical tolerance or an allowance for rounded execution error.

In particular every writer target is above exp(-bbar), so the floor really
is inactive. The convex logarithmic writer keeps y in [-bbar,0]. The
resource estimate only integrates the derivative along the segment from
C* to the incoming C, already in the box; these margins establish that the
outgoing state stays in it, rather than assuming this in the proof.

For 0<=gamma<=Gamma, put

$$
c=\frac{(1-\rho)\Gamma\eta^2}{2}(A_jR+D_c\bar b)
=\frac{494065}{8388608}.
$$

Using the current bound once quadratically and once at its rectangle maximum,

$$
Y^+\le cA_jX+(\rho+cD_c)Y.
$$

Choose the auxiliary Lyapunov norm S=X+K Y, K=1/1024. This is a proof weight
for these nondimensional coordinates, not a new authoritative physical
metric or the paper's general nonnormality weighting. Then

$$
S^+\le qS,\qquad
q=\max(q_x+KcA_j,\;B_c/K+\rho+cD_c)
=\frac{2251732039862933}{2251799813685248}<1.
$$

Thus the entire invariant rectangle returns to (C*,W=1), including arbitrary
nonuniform negative log histories in that rectangle, for every gamma in
[0,256]. This is a conservative sufficient interval, not a maximal coupling
range or a physical threshold. The slow bound q approximately 0.99997 is
stability evidence, not a performance/return-time claim. At gamma=512 the **same bound**
exceeds one: the certificate reports failure of that bound, not instability
of the dynamics.

## 4. Initialization, source endowment and a bounded encounter

At target C0=(1,1,3/2,3/2), the mathematical one-pass reference preparation
starts with W_base=1, reads J_ref=(1/4096,-1/4096,0), then sets

$$
y_0=(-a,-a,0),\qquad a=\gamma(1/4096)^2/2\le1/131072.
$$

This follows the reference-pass formula on the declared research law; it is
not a successful call to the native initializer with an unadmitted potential.
It also does not claim source-history preservation across a topology event.

The same mathematical preparation at source (1,3,1) has reference inflow
3/2048 on both edges. Its initialized equal weight is
exp[-gamma (3/2048)^2/2], and actual inflow is (3/2048) times that weight
squared, still positive. Half allocation and strict child endowment remain
available, with margin 1/2. These are formula-level source/target checks,
not an executed F2 event or proof of its general physical necessity.

For the prepared target, x0=(t*,-t*,0) and

$$
S_0<\frac{786433}{134217728}.
$$

Keep the previously declared, fixed-reference loads w_i=-L_0 e_i at the two
children, with independently signed amplitudes |a_load|,|b_load|<=epsilon,
epsilon=1/4096. They alter C, not W. They are not history-adaptive loads
-L_w e_i; changing the operation that way requires a separate theorem.
In edge coordinates the load vectors
are -B-transpose e_i and have Gram matrix [[2,-1],[-1,2]]. Consequently

$$
\|\delta x\|\le\sqrt6\epsilon<\frac52\epsilon=\frac5{8192}.
$$

At any unencountered age S<=S0; after one such load,

$$
X_{\rm loaded}\le S_{\rm loaded}
<\frac{868353}{134217728}<R.
$$

The old history is unchanged and still in its rectangle. Thus the loaded
full state remains in the invariant domain and returns to (C*,1). This is
one encounter at any unencountered age, not arbitrary repeated loads or
reset/save-load semantics.

### Positive individual response with nonuniform history

For f_w(C)=-eta L_w[p(C)-kappa L_w C], keep the original instantaneous
response definition at fixed incoming W:

$$
Q_i=\frac{h}{2\epsilon}[f_{w,i}(C+\epsilon w_i)-f_{w,i}(C)]
=\frac{h\eta}{2}e_i^\top L_w(\bar D-\kappa L_w)L_0e_i.
$$

Here Dbar contains the exact averaged p' along the load segment. Both
loaded and unchallenged states lie in the slope box. The unit-W lower bound
is Q0=360495/268435456. Since ||L_w-L_0||<=4Y,
||L_w squared-L_0 squared||<=32Y and ||L_0 e_i||=sqrt(6)<5/2,

$$
|Q_i-Q_i^{(0)}|\le5h\eta Y(M+8\kappa),\qquad
Q_i\ge\frac{43636135}{34359738368}>0.
$$

This demonstrates two available restorative response sites during evolving
history, not dynamically independent children, positive intake under every
joint load, generic controllability or differentiated persistent identities.
The full-state return theorem, separately, covers the signed joint encounter.

## 5. Is the channel actually used?

Two matched gamma=256 versus gamma=0 one-beat comparisons start from
identical incoming C and W. The control is not separately initialized.
Their selected currents and resource updates agree on that beat; their
written W and next current reads differ.

- A supplied neutral prestate y=0 demonstrates formation from neutral
  history. It lies in the proven mathematical domain, but is not the gamma>0
  reference-pass preparation.
- The reference-pass prepared prestate y=(-a,-a,0) demonstrates a writer
  effect along the specified preparation. Both branches release toward zero
  on this first beat, but the enabled channel retains an attributable
  depression relative to the gamma-off control. Net depression from the
  initial state is not asserted here.

For the prepared case, let w=exp(-a), j=(1/4096)w squared and u=h j.
Both branches have C+=(1-u,1-u,3/2+u,3/2+u), while their outer-edge logs are

$$
y_{\rm on}^+=-\frac a2(1+e^{-4a}),\qquad y_{\rm off}^+=-a/2.
$$

The next outer-edge read at common C+ and new weight w_new is

$$
j_{\rm next}(w_{\rm new})
=\eta w_{\rm new}\{2\kappa w_{\rm new}(1/2+2u)
-[p(3/2+u)-p(1-u)]\}.
$$

At gamma=256, using exp(-z)>=1-z and the slope bound M gives exact
strictly positive lower bounds for the writer log gap, weight gap and
next-current difference. In detail, for
delta=a exp(-4a)/2, we have delta>=a(1-4a)/2 and
1-exp(-delta)>=delta/2 since 0<=delta<=1. Hence

$$
w_{\rm off}^+-w_{\rm on}^+
\ge(1-a/2)a(1-4a)/4.
$$

After factoring this weight difference out of the next-current difference,
its remaining bracket is at least 2 kappa (1-a)-2M h/4096>0. In particular,

$$
j_{\rm next,off}-j_{\rm next,on}
\ge\frac{2301509387521290555}{2475880078570760549798248448}>0.
$$

The certificate retains the intermediate factors. This analytically excludes
a dynamically unused channel; the retained Decimal80 values illustrate it
but are not certified rounding enclosures. The dense expanded-polynomial
next reads also agree with a separate factored-polynomial scalar oracle.
Four finite staged evaluations
also discriminate three wrong implementations: early reuse of new W,
writing with a recomputed next-state current, and freezing potential stiffness
while changing only mobility. No trajectory campaign is needed for this test.

## 6. Evidence and next obligations

The [checker](../scripts/certify_atc_a_history_feedback.py) prints the
[retained certificate](../evidence/autonomous-topology-change/ATCHistoryFeedbackCertificate.json)
from repository-local inputs. It binds its own source, the unchanged reviewed
support certificate, the source equations and four full authority traces.
It checks exact rational slope/invariance/gain/response bounds and four finite
Decimal80 research steps, with two next-read comparisons: zero native steps,
zero topology events and zero trajectory campaigns.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_a_history_feedback.py
```

The substantive advance is a finite-domain full-state return theorem with
demonstrably active history feedback on the original graph. This belongs to
the retained-history/constitutive-feedback and support/discrimination lane,
with bounded relevance to DB-07/27 but no debt closure or accepted claim nodes.
It does not materially advance CAN-B's DB-05/06/08 structural-trigger debts:
no qualified topology-changing structural functional, critical branch,
selected structural mode or equivariant mode-to-half-edge partition lift is
derived. In particular DB-08 remains unchanged. The source/target potential,
new nonzero-gamma binding and native initializer domain still need their own
authority route before N-P/C-P.

### Independent-review disposition

The supplied review finds no mathematical blocker and gives PASS to the
coupled return theorem, finite interval [0,256], one bounded encounter,
positive child restorative response and writer-to-next-current causal
activation. It independently reconstructs the exact bounds and verifies:

- Certificate canonical digest:
  `b2e3ca3131d46d04a92febaf65556a8a9d9b9ff848d5b39b51a5ed41956a9c83`.
- Checker SHA-256:
  `9dec98628ed2a3482bd9f0fa9ab38ecfd2a63c64ced5ecc418f440b209258068`.

Those artifacts remain unchanged, including the certificate's historical
pre-review status. This note records the current mathematical disposition.
The review's scope requests are applied: conductance depression is explicit,
fixed-reference loads are distinguished from adaptive ones, the CAN-B debt
implication is removed, and the tree's role is explained. The additional
gradient identity in §2 qualifies the review's cyclic-equilibrium suggestion;
it is an integration clarification, not a claim of independently reviewed
cyclic return. The gamma-dependent certificate is likewise not evidence that
the actual basin boundary has moved. The forensic authority ceilings remain
unchanged; no new accepted graph node or native profile follows from this PASS.

Next separately address another genuine geometry/read-back feedback channel;
combination with the reviewed higher-degree analysis remains a separate task.
Neither extension follows by substituting a Laplacian: W now changes both
mobility and stiffness.
The theorem does not cover W>1, gamma<0, other retention factors, arbitrary
repeated use, cyclic graphs, other realizations or all ten families. It does
not establish durable differentiation, an endogenous partition or continued
autonomous topology operation. The thirty capability cells and composition
obligations remain open. CAN-F2's source-only guard and all earlier reviewed
evidence remain unchanged; no target-return filter is inserted into its law.

The next channel now has a separate
[OS geometry/read-back successor](./ATCOSGeometryFeedbackContinuation.md):
the retained writer remains active while explicit Read-Back generates a
tensor that changes the corrector's potential. Its finite-domain return,
one-encounter and residual bounds now have independent mathematical PASS,
with explicit return/causality, activation-quantifier, endpoint-rounding and
research-tolerance limits. This does not change the present reviewed theorem
or either reviewed checker/certificate.
