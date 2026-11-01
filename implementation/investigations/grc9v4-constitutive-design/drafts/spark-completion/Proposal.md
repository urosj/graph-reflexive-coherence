# Constructive spark completion in GRC9V4 — self-contained proposal

**Date:** 2026-11-01. **Status:** adopted consolidated proposal, accepted by the
user after review corrections. It presents the accepted scientific constructions,
including the formally adopted shorter endpoints. This document
states the model, construction and proof; large numerical operands are supplied
as computational companions. The separate [full GRC-v4 manuscript](../2026-11-GRC-V4.md)
integrates the result in §15 and Appendix H.

Copyright © 2026 Uroš Jovanovič, CC BY-SA 4.0.

## 1. Scientific question and selected answer

A graph expansion creates new coordinates and edges. It becomes a completed
spark only when ordinary post-event dynamics earns additional stable local
organization. The proposal is to use a precise geometric child criterion and
a full-state contraction certificate to establish that transition. The
construction below supplies ten nonempty examples: two constitutive families,
A and C, crossed with OS, CI, PC, CI+PC and RG2b realizations.

There are three logically separate assertions. First, an actual qualified
source parent undergoes a lawful, charge-preserving expansion. Second, its
post-event state enters an invariant attracting domain of the complete ordinary
map. Third, throughout that domain the parent's lineage footprint contains at
least two qualified spatial descendants, including a new module anchor. The
last assertion earns one additional local child. Neither the expansion itself
nor a small numerical residual earns that child.

The shorter accepted witnesses are primary. Their current-event completion
times are 376 or 377 beats for the first eight realizations, 392 for C_RG2b and
302 for A_RG2b. Durations are respectively 32, 8 and 16; these are sufficient
witnesses for different discrete maps and event preparations, not a ranking or
a claim of earliest possible completion. Every selected certificate is directly
invariant and requires no supporting physical trajectory after its two-beat
completion window.

## 2. Graph, physical state and spatial organization

Let a finite connected graph have oriented incidence matrix $B$, with $+1$ at
an edge's tail and $-1$ at its head. Each endpoint has a port in $\{1,\ldots,9\}$;
ports 1–3, 4–6 and 7–9 form the three fixed rows. Orientation is a coordinate
choice. At vertex $i$ define the weighted row means

$$
g_a(i)=\frac{\sum_{e\ni i,\ \operatorname{row}_i(e)=a}
 w_e(C_{\operatorname{other}(e,i)}-C_i)}
 {\sum_{e\ni i,\ \operatorname{row}_i(e)=a}w_e},
\qquad D_i=(g_1(i),g_2(i),g_3(i)).
$$

Here $\operatorname{other}(e,i)$ is the other endpoint of the incident edge
$e$, independently of its orientation. An empty row has mean zero.
Candidate C uses $w_e=1$; Candidate A uses its
incoming authoritative conductance $w_e=W_e>0$. The classifier consumes these
exact scientific rows, without rounding them to native display predicates.

Choose the same global sign $s_H=-1$ at every vertex and set $\Psi_i=-C_i$.
Include **every** arc $i\to j$ with $\Psi_j<\Psi_i$; a tie creates no arc.
Let $\mathcal T(i)$ be the set of all terminals reachable from $i$, including
terminals that fail qualification. An anchor $a$ is qualified when

$$
\sum_{b=1}^3 g_b(a)^2<16,\qquad
\min_b[-g_b(a)]>\tfrac14,\qquad C_a>\tfrac12,
$$

it has a distinct neighbor, every distinct neighbor satisfies
$\Psi_j-\Psi_a>1/2$, and its complete domain

$$
\mathcal B_a=\{i:\mathcal T(i)=\{a\}\}
\quad\text{satisfies}\quad |\mathcal B_a|\ge2.
$$

Thus qualification requires all three rows to be occupied. One must compute
the complete domain, rather than select a convenient subset of vertices. A
vertex reaching two terminals is unassigned even if only one terminal qualifies.

**Spatial lemma.** The domains of distinct qualified anchors are disjoint.
Every maximal descent route starting in $\mathcal B_a$ terminates at $a$ and stays in
$\mathcal B_a$. Every undirected path between two qualified anchors crosses a
landscape value greater than the larger endpoint value by more than $1/2$.

**Proof.** Strict descent prevents a directed cycle. On a finite graph every
maximal route therefore ends at a terminal in at most $|V|-1$ arcs. If
$\mathcal T(i)=\{a\}$, each successor has a nonempty terminal set contained in
$\{a\}$, and hence has that same set. Disjointness follows from equality of
singleton terminal sets. For the barrier assertion, take the neighbor on the
path next to the endpoint with larger $\Psi$ and apply its every-neighbor
barrier. The assertion is geometric; it does not assert a transport-energy
barrier or identify descent arcs with physical current. $\square$

### 2.1 Parent, lineage and gain

Apply the same classifier to the fresh source state. The expanded vertex $v$
must lie in one qualified complete parent domain $P$; its anchor need not be
$v$. For the new module $M$, the actual lineage map is $\pi(x)=v$ for $x\in M$
and the old vertex identity elsewhere. The parent's target footprint is
$\pi^{-1}(P)$.

Count a target domain only if its **entire** domain lies in that footprint and
its anchor is either in $M$ or the surviving parent anchor. Require at least
two such descendants and at least one new module anchor. The local gain is
$\Delta N=N_{\rm desc}-1\ge1$. An absent source parent makes this criterion
inapplicable; it is not a parent count of zero. This is neither a global basin
count theorem nor a counterfactual claim that no other event could produce the
same organization.

## 3. Completion theorem for the full physical map

Fix a graph, references, context, complete profile and positive duration $h$.
Let $T_h$ be the exact ordinary map on **all** independent physical coordinates:
$C$ for C, $(C,\log W)$ for A, with an additional carrier $Z$ in persistent
realizations. Charge conservation may restrict the resource coordinates to an
affine hyperplane. Derived geometry, solver iterates and clocks are not physical
coordinates; independent conductances and carriers may not be frozen.

**Completion theorem.** Let $K$ be a nonempty closed complete subset of this
physical space, with nonempty relative interior of full physical dimension.
Suppose, in a declared norm,

$$
T_h(K)\subset\operatorname{relint}K,
\qquad \|T_hx-T_hy\|\le q\|x-y\|\quad(x,y\in K),\qquad q<1.
$$

Suppose throughout $K$ the strict edge directions, any exact identity ties,
complete domains and anchor identities are unchanged, with uniform strict
qualification and barrier margins. If positive post-event ordinary evolution
enters $K$, and the parent/descendant test above holds there, the selected
spatial children persist indefinitely under $T_h$. A declared positive
observation window after entry records completion of that occurrence.

**Proof.** Restrict $T_h$ to $K$. It is a contraction on a complete metric
space, so it has exactly one fixed point $x_*$ in $K$. Every orbit starting in
$K$ remains there and satisfies
$\|T_h^n x-x_*\|\le q^n\|x-x_*\|$. Uniform edge directions preserve the
entire descent graph, and thus its complete terminal sets. Uniform strict
predicates preserve the qualified anchors and barriers. The spatial lemma and
lineage test therefore hold at every subsequent beat and at the limit. This
proves the selected stable child organization. The finite window records a
positive occurrence; the invariant domain proves its unlimited continuation.
$\square$

Several spatial children here coexist in **one attracting full-field state**.
The theorem does not claim several independent dynamical systems, several
full-state attractors, global attraction or a continuation spectrum. Inner CI
root contraction and RG2b section contraction are separate existence results;
neither substitutes for contraction of $T_h$.

### 3.1 Represented evolution and the native obligation

Suppose a represented map $\widehat T_h$ stays on the same exact-charge space
and satisfies $\|\widehat T_h(x)-T_h(x)\|\le\epsilon$ uniformly on $K$.
Let $\mathcal P$ be that same physical space, including the exact-charge
constraint. If the certified image has distance $m>\epsilon$ from
$\mathcal P\setminus K$, measured in the declared norm on $\mathcal P$,
represented steps remain in $K$, and

$$
\|\widehat x_n-x_*\|
\le q^n\|\widehat x_0-x_*\|+
\epsilon\frac{1-q^n}{1-q}.
$$

This follows by induction from $e_{n+1}\le qe_n+\epsilon$. A numerical method
with uncontrolled error normal to the charge hyperplane does not satisfy this
hypothesis merely because its total error is small. Native row predicates also
need a certified agreement margin. Thus the exact-equation certificates do not
by themselves complete native numerics or event-accounting implementation.

## 4. Constitutive mechanism and the exact fixed-geometry reads

The selected homogeneous site law is

$$
V(C)=\frac{\mu}{4}\big((C-c_0)^2-a^2\big)^2,
\qquad V'(C)=\mu\big((C-c_0)^3-a^2(C-c_0)\big),
\quad(c_0,a,\mu)=(2,1,1).
$$

Write $s(C)=(C-2)^3-(C-2)$, componentwise. The potential consumes $-s(C)$.
All vertices use the same law: labels do not assign different wells. This
modifies transport without adding a resource source, since the ordinary write
remains $C^+=C-hBJ$ and $\mathbf1^TB=0$. In dimensional form $c_0,a$ have
resource units, $\mu$ has units $[\Phi]/[C]^3$, and $V$ has units $[\Phi][C]$.
It is an explicitly selected optional constitutive slice, not an obligatory
replacement for the substrate baseline.

The choice addresses a concrete obstruction. For the previously considered
zero-site closed-tree subjects, stationarity gives $BJ=0$, hence $J=0$ by
full column rank of tree incidence. The positive fixed-geometry closures then
give zero potential differences. A positive Laplacian potential on a connected
graph forces constant resource, which cannot satisfy the strict seed/barrier
criterion. For A's corresponding stationary writer subjects, $J=0$ also gives
$f=0$, reference geometry and the self-consistent conductance law. This is a
bounded exclusion of those earlier zero-site subjects. It is not an exclusion
of all graph/profile choices, and the source/target graphs below have cycles.
The quartic term permits nonconstant stationary solutions on the conserved
charge space; their existence and attraction still require the certificates.

Let $L_e=B^TB$, $O=|B|^T|B|$, and define the symmetric star source and geometry

$$
S(f)=\tfrac14\operatorname{diag}(f)O\operatorname{diag}(f),
\qquad \mathcal G(f)=I+\tfrac12 S(f).
$$

$O$ is a Gram matrix, so $S(f)\succeq0$ and $\mathcal G(f)\succ0$. The
permitted star support consists of pairs of edges sharing a vertex, including
the diagonal. Individual entries may vanish; in particular $S(0)=0$.
All reference pairings are unit and autonomous context is zero.
Below $H$ denotes the selected edge Hodge matrix and $f$ the causal flat;
neither is an additional persistent state unless explicitly stated.

### 4.1 Candidate C read at fixed H

The selected coefficients are $\eta=1/1024$, $\kappa_\Phi=1/64$,
$\tau_C=1$, $\chi=\zeta=\kappa_H=1/2$ and $\kappa_M=0$. The complete read is

$$
\Phi_C=\tfrac1{64}BHB^TC-s(C),\qquad
j_0=-\tfrac1{1024}B^T\Phi_C,
$$
$$
y=(\tfrac34 I+HL_e)^{-1}j_0,\qquad
J=j_0+\tfrac14y,\qquad f=\tfrac12H^{-1}y.
$$

Both the potential's $H$ and the inverse-flat $H^{-1}$ matter. The nonconstant
spectrum lies strictly above the $1/64$ selector cutoff on the actual graphs
and admitted geometry domains. On both graph charts the unit graph Laplacian
has $\lambda_2(BB^T)>1/28$; the admitted lower bound $H\succeq(127/128)I$
therefore keeps every nonconstant eigenvalue above $127/3584>1/64$.
Thus the selected sector is the constant mode, with projector
$Q=\mathbf 1\mathbf 1^T/|V|$ for the unit vertex measure.
Here $\kappa_M=0$ disables selected-content Hodge modulation, while
generated-Hodge dependence and the explicit resolvent Read-Back remain active.
No retained conductance channel is added to C.

### 4.2 Candidate A read and writer

Use $\eta=1/1024$, $\kappa_c=\kappa_{Ah}=1/64$,
$\chi=\zeta=\kappa_H=1/2$, $\alpha=\beta=\gamma=1/32768$,
$W_{\rm floor}=1/2$ and $\tau_A=32$. Define

$$
\Phi_A=\tfrac1{64}B\operatorname{diag}(W)B^TC-s(C)
          +\tfrac1{64}B(H-I)B^TC,
\qquad j_0=-\tfrac1{1024}\operatorname{diag}(W)B^T\Phi_A,
$$
$$
\mathcal W_e(C,W,j)=\max\left\{\tfrac12,
\exp\left[-\frac{C_u+C_v+\|D_u-D_v\|_2^2+j_e^2}{65536}\right]\right\},
$$
$$
\theta_e=\frac{W_e-\mathcal W_e(C,W,j_0)}{W_e+\mathcal W_e(C,W,j_0)},
\qquad J_e=\frac{j_{0,e}}{1-\theta_e/4},
\qquad f=\tfrac12H^{-1}(\theta\odot J).
$$

After the selected continuity write, the full conductance writer is

$$
\log W^+=e^{-h/32}\log W+
(1-e^{-h/32})\log\mathcal W(C^+,W,J).
$$

The writer recomputes row means at final $C^+$ with **incoming** $W$ and the
same selected current $J$. Newly written $W$ never feeds that beat. Positivity
gives $|\theta|<1$ and closure denominators greater than $3/4$. On the proof
domains $W\in(0.99,1.01)$ and the floor is strictly inactive, so the full map
can be differentiated there. The logarithm retains every independent positive
conductance direction.

At a fixed point, $J=-D B^T\Phi_A$ with a positive diagonal $D$. Multiplying
$BJ=0$ by $\Phi_A^T$ gives $(B^T\Phi_A)^TD(B^T\Phi_A)=0$, hence $J=0$.
The selected flat therefore vanishes. For CI its root identity gives $H=I$.
For PC and CI+PC the stationary carrier writer gives $Z=S(0)=0$, and their
selected geometry is also $I$. For RG2b the section identity at the physical
fixed state gives $\Gamma(X)=\mathcal G(0)=I$.

OS needs an additional staged argument: zero selected current gives zero
corrector flat $f_c$, not directly zero predictor source. At fixed incoming
$x=(C,W)$ define $\mathcal R_x(f)=R_f(x,\mathcal G(f))$, the flat component
of the fixed-geometry read. The predictor and corrector satisfy
$f_p=\mathcal R_x(0)$ and $f_c=\mathcal R_x(f_p)=0$. The target A read has
the uniform bounds

$$
\sup\|\mathcal R_x(f)\|_\infty<4.041\cdot10^{-5}<1/32,
\qquad \operatorname{Lip}_f\mathcal R_x<2.29\cdot10^{-6}<1
$$

on $C\in[0,4]$, $W\in[0.99,1.01]$, $\|f\|_\infty\le1/32$.
These are bounds on the shared fixed-geometry A read, independent of the
physical realization's staging. The entire A_OS anisotropic domain lies
inside this resource/conductance box, as checked from its rational basis,
axis radii and exponential conductance enclosure. The image bound puts $f_p$
in the flat ball, so both arguments are admitted. With the strict contraction
constant $\ell$,

$$
\|f_p\|_\infty
=\|\mathcal R_x(0)-\mathcal R_x(f_p)\|_\infty
\le\ell\|f_p\|_\infty,
$$

which forces $f_p=0$ and $H_p=I$. This proves the original OS staging; it
adds no physical root iteration. In all five cases the stationary conductance
writer gives $W=\mathcal W(C,W,0)$. These stationary identities do not permit
freezing $W$ or $Z$ in a surrounding proof domain.

## 5. The five complete ordinary maps

Denote the read of §4 by $R(C,W,H)=(J,f)$, omitting $W$ for C. Every map uses
one continuity write followed by the A writer when present. The duration is
32 except for the declared RG2b choices below.

**OS.** Read the incoming state at $H=I$ to obtain $f_p$. Form
$H_p=\mathcal G(f_p)$, then read again at $H_p$ on the **same incoming state**.
Use only the corrector current for continuity and the A writer. The selected
split admission uses $\|H_p-\mathcal G(f_c)\|_2\le10^{-11}$, the spectral
operator norm, since the reference Hodge is identity. These witnesses certify
admission using the stronger sufficient bound
$\|H_p-\mathcal G(f_c)\|_F<10^{-11}$. The Frobenius estimate does not
redefine the admission norm or tolerance. There is no iteration until
convergence and no CI equivalence claim.

**CI.** Select the unique root
$f=R_f(C,W,\mathcal G(f))$ in $\|f\|_\infty\le1/32$, where $R_f$ denotes
the flat component of the read, not a derivative. Use its current for continuity
and the writer. The root must be admitted uniformly over the proof domain.

**PC.** The independent carrier $Z$ is a signed symmetric star-supported
matrix. Read at incoming $H=I+Z/2$ and write

$$
Z^+=e^{-h/32}Z+(1-e^{-h/32})S(f).
$$

The carrier source is the same incoming read used for continuity. Recomputing
it from post-continuity $C$ would define a different map.

**CI+PC.** Hold incoming $Z$ fixed while solving
$f=R_f(C,W,I+(Z+S(f))/2)$ in the same flat ball. Use that **one selected flat**
for both immediate geometry and the PC writer. The immediate and persistent
channels are added, not averaged. All conductance and carrier directions and
their cross-couplings remain in the physical map.

**RG2b.** There is no carrier. Geometry is reconstructed as $H=\Gamma(X)$,
where $X=C$ for C and $X=(C,64\log W)$ for A. If $F(X,H)$ denotes the
complete fixed-$H$ physical step, including the A writer, the selected section
satisfies

$$
\Gamma(F(X,\Gamma(X)))=\mathcal G(f(X,\Gamma(X))).
$$

The physical map is $T_hX=F(X,\Gamma(X))$. The section is Lipschitz, not assumed
to be $C^1$. The selected durations are $h=8$ for C and $h=16$ for A; in A,
$\tau_A$ stays 32 and the writer decay is consequently $e^{-1/2}$.

### 5.1 Uniform root and read admission

Root proposals are numerical guesses. For $\mathcal R_x(f)=R_f(x,H(f))$,
prove $\sup\|\mathcal R_x(f)\|_\infty<r$ and
$\sup\|D_f\mathcal R_x(f)\|_\infty\le\ell<1$ on the whole declared ball
$r=1/32$ and all admitted $x$. Banach then selects a unique root; a proposed
$\widehat f$ in that same certified ball has error at most
$\|\mathcal R_x(\widehat f)-\widehat f\|/(1-\ell)$.
Residual certification requires checking this proposal-domain membership.

On $C\in[0,4]$, C_CI's source/target root bounds are respectively below
0.026594 and 0.011467; its image bound is below 0.013133. With signed
$\|Z\|_F\le1/128$, C_CI_PC's source/target bounds are below 0.063351 and
0.019589, and $H\succeq(255/256)I$. C_PC uses the distinct signed carrier
neighborhood $\|Z\|_F\le1/64$, giving Hodge eigenvalues in
$[127/128,129/128]$. For A the additional domain is
$W\in[0.99,1.01]$; the target A_CI root bound is below $2.29\cdot10^{-6}$.

These estimates follow by differentiating the displayed reads, using
$d(M^{-1})=-M^{-1}(dM)M^{-1}$, the weighted row quotient rule and the quadratic
star source. Positivity bounds the denominators and Neumann estimates enclose
the inverses. The exact operands are retained with the certificates. A root
bound on a rectangular input domain is not a proof that the physical map
preserves that domain: prefixes and invariant sets are checked separately.

## 6. RG2b existence without a section derivative

Let $\Pi$ clip **arguments**, coordinatewise, to a declared box; it never clips
the physical state. Write $b(X,H)=F(X,H)-X$ and define auxiliary maps on all
$X$ by

$$
\widehat F(X,H)=X+b(\Pi X,H),\qquad
\widehat G(X,H)=\mathcal G(f(\Pi X,H)).
$$

Use induced infinity norm for symmetric star matrices, geometry radius
$\rho_H=1/1024$ around $I$, and a section class of global Lipschitz constant
$L=1/256$. In the auxiliary state norm use $\|C\|_\infty$ for C and
$\max(\|C\|_\infty,64\|\log W\|_\infty)$ for A. Bound the increment
partials by $A_X,A_H$ and the geometry partials by $G_X,G_H$, uniformly
over all auxiliary $X$ and the admitted symmetric star geometry ball. Define
the geometry **deviation from the reference** by

$$
V\ge\sup_{X,\,H:\,\|H-I\|\le\rho_H}
\|\widehat G(X,H)-I\|,
$$

where $H-I$ is symmetric and star-supported. Thus $V$ bounds the displacement
from $I$, not the absolute norm of the geometry. Suppose

$$
e=A_X+A_HL<1,\qquad v=(1-e)^{-1},\qquad V<\rho_H,
$$
$$
L_{\rm image}=(G_X+G_HL)v\le L,\qquad
q_\Gamma=G_H+(G_X+G_HL)vA_H<1.
$$

**Section lemma.** These inequalities give a unique bounded Lipschitz invariant
section in the declared class.

**Proof.** For any section $\gamma$ and any $Y$, the equation
$X=Y-b(\Pi X,\gamma(X))$ is a contraction with constant $e$ on the complete
auxiliary space. It gives a global inverse of $F_\gamma$ with Lipschitz bound
$v$. Define
$\mathcal T\gamma=\widehat G(\mathrm{id},\gamma)\circ F_\gamma^{-1}$.
Its deviation from $I$ is bounded by $V$ and its Lipschitz bound is
$L_{\rm image}$, so it preserves the closed class. For two sections
separated by $d$ in supremum
norm, their inverse arguments differ by at most $vA_Hd$. The geometry outputs
then differ by at most
$[G_H+(G_X+G_HL)vA_H]d=q_\Gamma d$. The class is complete in supremum norm,
so its transform has a unique fixed point. Composing with $F_\Gamma$ yields
the invariant equation. Only Lipschitz estimates were used. $\square$

For C the source argument box is $[1/2,7/2]$, with nested agreement boxes
$K_-=[7/8,25/8]$ and $K_+=[9/16,55/16]$. Target boxes are respectively
$[-1/16,65/16]$, $[-1/32,129/32]$ and $[-3/64,259/64]$. Coordinates use the
same interval at every vertex. The signed target box accommodates the zero
event core. The source displacement and target cubic bounds prove
$F(K_-)\subset K_+$. A uses the vertex-specific rational argument charts
printed with the exact inputs below and $|64\log W|\le1/16$. Both families
verify every physical query, propagated tube and entire trapping domain inside
argument agreement. No whole-chart forward-invariance claim is needed.

A finite section evaluation uses $N=16$ coupled inverse levels. Write its
proposed chain as $(X_i,H_i)_{i=0}^N$, with $X_0=X$ and $H_N=I$, and verify

$$
r_X\ge\max_{1\le i\le N}
\|X_i+b(\Pi X_i,H_i)-X_{i-1}\|,
\qquad
r_H\ge\max_{1\le i\le N}
\|\widehat G(X_i,H_i)-H_{i-1}\|.
$$

Every proposed geometry must lie in the admitted ball, with $H_i-I$ symmetric
and star-supported. All residual-certified flat proposals must likewise lie
in their certified flat ball. A small residual outside its admitted domain
does not supply the estimate.

Let $\Gamma^{(0)}=I$ and $\Gamma^{(k+1)}=\mathcal T\Gamma^{(k)}$ be the
exact finite sections, and set
$e_i=\|H_i-\Gamma^{(N-i)}(X_i)\|$. Then $e_N=0$. Comparison with the
exact inverse at each level gives

$$
e_{i-1}\le r_H+L_{\rm image}r_X+q_\Gamma e_i.
$$

The inverse comparison contributes at most $v(r_X+A_He_i)$; the geometry
comparison then gives the displayed coefficients. Summing the recurrence,
using $L_{\rm image}\le L$ and
$\|\Gamma^{(N)}-\Gamma\|_{\sup}\le q_\Gamma^NV$, proves the conservative
section error bound

$$
E=\|H_0-\Gamma(X)\|
\le\frac{r_H+Lr_X}{1-q_\Gamma}+q_\Gamma^{16}V.
$$

Proposal Newton derivatives are derivatives at fixed $H$, not derivatives
of $\Gamma$.

For physical contraction, split a difference of $F(X,\Gamma(X))$ into its
fixed-$H$ state difference and its geometry difference. Bound the latter by
the $H$ partial times the proved section Lipschitz bound. A local inverse
footprint can sharpen this bound for the **same** section. The inverse
iteration must map the declared closed footprint into itself for every query
under comparison, and that footprint must contain all required inverse
arguments. If its verified local contraction is $a<1$, then
$\operatorname{Lip}\Gamma_{\rm local}\le
(G_{X,\rm local}+G_{H,\rm local}L)/(1-a)$.
The self-map and contraction give the local inverse; uniqueness of the global
inverse identifies it with the global one. A derivative bound alone does not
establish the footprint. This step
retains both Hodge consumers and, for A, the full conductance writer.

## 7. Exact source, expansion and state transfer

The source vertices are $n_1,\ldots,n_9,p,v,r$, where $r$ is the private
neighbor of $p$. Its thirteen oriented edges, with endpoint ports, are

$$
(v,i)\longrightarrow(n_i,1)\quad(1\le i\le9),
$$
$$
(p,1)\longrightarrow(n_1,4),\quad
(p,4)\longrightarrow(n_5,4),\quad
(p,7)\longrightarrow(n_9,4),\quad
(p,2)\longrightarrow(r,1).
$$

All nine ports of $v$ are occupied. The target replaces $v$ by core $o$ and
satellites $s_1,s_2,s_3$. Replace its old endpoint $(v,i)$ by
$(s_{1+((i-1)\bmod3)},i)$, preserving the other endpoint. Add three internal
edges $(o,k_j)\to(s_j,k_j)$, where $(k_1,k_2,k_3)=(2,6,7)$ for positive
chirality and $(3,4,8)$ for negative chirality. The other four edges are
unchanged. This is a collision-free same-port construction with fifteen
vertices and sixteen edges. The two charts have the same ordered incidence
and row assignments; this fact is checked before sharing physical evolution.

The exact resource prestates are printed below. The current role takes **one
fresh ordinary source beat of its own family**, then a fresh committed-state
read supplies the parent and trigger. The independent reset role is not
advanced at the source. The trigger requires saturation, $\sum_a g_a(v)^2<16$
and signed-Hessian degeneracy $\min_a[-g_a(v)]<1/8$. Each actual source has
the qualified complete parent anchored at $p$, containing all twelve vertices.
Input reuse between families is not trajectory reuse.

At expansion set $C_o=0$, copy exterior resources and set
$C_{s_j}=r_j C_v$ with these exact shares:

| Realizations | $(r_1,r_2,r_3)$ |
| --- | --- |
| C_OS, C_CI, C_PC, C_CI_PC | $(1/64,31/32,1/64)$ |
| A_OS, A_CI, A_PC, A_CI_PC | $(1/128,63/64,1/128)$ |
| C_RG2b, A_RG2b | $(5/2048,1021/1024,1/2048)$ |

Their sums are exactly one, so source and target have charge 21. Allocation
alone has only the old qualified basin and earns no gain. For A, current
source conductances start at $4097/4096$ and reset conductances at $8191/8192$;
the current source beat actually writes them. Each old edge retains its own
incoming conductance, and the three new internal edges start at one.

For PC and CI+PC, current source $Z=2^{-16}I$ and reset source
$Z=-2^{-17}I$. Archive the whole source carrier and explicitly record history
loss: the **whole target** carrier is initialized to zero. Subsequent ordinary
carrier writers remain active. RG2b rebuilds the target section from its own
graph and state; derived $H$ is not transported as history.

On every selected trapping domain in both charts the full qualified roster is

$$
\mathcal B_p=\{p,r\},\qquad
\mathcal B_{s_2}=\{s_2,n_2,n_8\}.
$$

Other vertices are not assigned by convenience. These two complete domains
lie in the source parent's lineage footprint and one is anchored in the new
module, giving $N_{\rm desc}=2$ and local gain one.

## 8. Anisotropic full-state certificates

For a C resource domain let $E:\mathbb R^{14}\to\{\delta C:\mathbf1^T\delta C=0\}$
be a full-rank charge embedding, $R$ its left inverse, $T$ an exact invertible
rational matrix and $r_k>0$ rational axis radii. Set

$$
S=ET\operatorname{diag}(r),\qquad
U=\operatorname{diag}(r)^{-1}T^{-1}R,\qquad US=I,
$$
$$
K=\{x_0+Su:\|u\|_\infty\le1\}.
$$

For A use the same construction on all thirty coordinates of $(C,\log W)$
relative to charge. The center $x_0$ is an exact rational proposal, not assumed
to be a fixed point. Define

$$
d=\|U(T_h(x_0)-x_0)\|_\infty,\qquad
q=\sup_{x\in K}\|U(DT_h(x))S\|_\infty.
$$

The line segment between any pair in a parallelotope stays in it. Integrating
the derivative gives pairwise contraction $q$; integrating from the center
gives $\|U(T_h(x)-x_0)\|\le d+q$. Thus $q<1$ and $d+q<1$ prove the theorem's
metric hypotheses with strict dimensionless image margin $1-d-q$.

For persistent cases use the product with $\|Z-Z_0\|_F\le r_Z$, where
$r_Z=10^{-8}$ for C and $r_Z=2^{-30}$ for A. The norm is
$\max(\|U\delta x\|_\infty,\|\delta Z\|_F/r_Z)$. Bound all four derivative
blocks in their induced norms by $a,b,c,d_Z$. Then the complete map's
contraction is at most $\max(a+b,c+d_Z)$. Both cross-blocks are necessary.
The target star space has 46 independent signed symmetric directions, so the
full dimensions are 60 for C_PC/C_CI_PC and 76 for A_PC/A_CI_PC. Positive
semidefiniteness of the generated source is not a reason to remove signed
carrier perturbations from these domains.

For CI differentiate the selected equation $f=\mathcal R(x,f)$:

$$
D_xf=(I-D_f\mathcal R)^{-1}D_x\mathcal R,
\qquad D_xJ=\partial_xJ+\partial_fJ\,D_xf.
$$

The root contraction makes the first inverse valid. Propagate these derivatives
through continuity, the final-C A writer and the carrier writer. For OS,
differentiate both reads and their geometry connection. In every case certify
the complete classifier over the same domain. In particular an edge contrast
has exact support radius $\sum_k|S_{ik}-S_{jk}|$ in resource coordinates.
Bounding the two endpoints independently loses these correlations and can
destroy the crucial strict edge order.

### 8.1 Correlated OS split bound

For C_OS write $D=H_p-I$, $y_0=2f_p$ and $M_0=3I/4+L_e$. Subtract the
two exact read equations before taking interval bounds:

$$
(M_0+DL_e)(y-y_0)=\delta j-DL_e y_0,
$$
$$
f_c-f_p=(I+D)^{-1}\big((y-y_0)/2-Df_p\big).
$$

This retains the shared incoming state's correlation. For $\Delta f=f_c-f_p$,
expand the difference of star sources into the two cross terms in
$f_p,\Delta f$ and the quadratic term in $\Delta f$. On the earlier domain
this bounds the split below $2.687\cdot10^{-21}$, inside the original
$10^{-11}$ admission tolerance. Subtracting independently enclosed geometries
gave $2.021\cdot10^{-11}$ and could not prove admission. The improvement is a
stronger enclosure of the same map, not a relaxed tolerance.

### 8.2 Certified quantitative margins

| Realization | Upper bound on full-map contraction | Strict image margin, greater than |
| --- | ---: | ---: |
| C_OS | 0.995426167 | 0.0043488775 |
| C_CI | 0.995426412 | 0.0043488775 |
| C_PC | 0.995650793 | 0.0043488775 |
| C_CI_PC | 0.995651123 | 0.0043488775 |
| A_OS | 0.995934130 | 0.00406586 |
| A_CI | 0.995934130 | 0.00406587 |
| A_PC | 0.995942 | 0.004058 |
| A_CI_PC | 0.995942 | 0.004058 |

These rounded bounds are conservative; the center defects are included in the
image margins. Margins use each domain's scaled norm and are not physical
error budgets in a common unit. The exact rational basis matrices, centers,
interval inequalities and membership records are computational certificate
operands linked below. They are not replaced by a spectrum at the center.

## 9. Direct curved domains for RG2b

For C let
$A_0=B[I+(3I/4+L_e)^{-1}/4]B^T$ and
$P=(A_0+\mathbf1\mathbf1^T/n)^{-1}$. On the charge tangent use
$\|\delta C\|_P=(\delta C^TP\delta C)^{1/2}$.
For A take $A_0=BB^T$, the corresponding $P$, $Y=64\log W$ and
$\|(\delta C,\delta Y)\|=\max(\|\delta C\|_P,\|\delta Y\|_2)$.

Let $p(s)$ be an exact rational degree-40 polynomial on $[0,1]$ and set

$$
K=\{p(s)+v:0\le s\le1,\ \mathbf1^Tv_C=0,\ \|v\|\le R\},
\qquad R=1/4096,\qquad \rho=999/1000.
$$

Its resource coefficients sum to charge 21 in the constant coefficient and
zero in every other coefficient. This is a compact continuum of full
14-dimensional C balls or 30-dimensional A balls. The set need not be convex.
Therefore contraction is proved for every pair in $K$ using a common
surrounding domain, not just separately inside its constituent balls.

**Curved-domain lemma.** If that pairwise contraction is $q<1$ and
$\delta\ge\sup_{0\le s\le1}\|T_h(p(s))-p(\rho s)\|$ satisfies
$qR+\delta<R$, then $K$ is strictly invariant.

**Proof.** For $x=p(s)+v$, the triangle inequality gives
$\|T_hx-p(\rho s)\|\le q\|v\|+\delta\le qR+\delta<R$.
Since $\rho s\in[0,1]$, this is an interior point of a constituent full-state
ball and hence of $K$. Compactness gives completeness, and the common pairwise
bound permits the completion theorem. No future orbit is an input. $\square$

For C the fixed-$I$ physical reference is cubic:

$$
F_I(C)=C+\tfrac1{128}A_0[BB^TC/64-s(C)].
$$

The degree-120 residual $F_I(p(s))-p(\rho s)$ is evaluated by exact Chebyshev
multiplication and composition. If its coefficients are $r_k$, then
$\sup\|r(s)\|_P\le\sum_k\sqrt{r_k^TPr_k}$ because $|T_k(2s-1)|\le1$.
This gives approximately $3.35685\cdot10^{-13}$; the physical section correction
is below $1.44791\cdot10^{-8}$. Full pairwise contraction is below 0.997397
and the strict image margin exceeds $6.21038\cdot10^{-7}$.

For A, the reference read and writer contain exponentials and weighted row
ratios. Exact Bernstein ranges and a fourth-order interval Taylor residual
bound cover a gap-free partition of 67 rational parameter cells. Scalar
FLINT series evaluate the entire fixed-$I$ read and writer. The physical
section correction includes full C/W dependence; the resulting functional
defect is below $8.858\cdot10^{-8}$, pairwise contraction below 0.998534 and
strict image margin above $2.6939\cdot10^{-7}$. Weighted edge margins exceed
$8.3817\cdot10^{-5}$. No sampled parameter grid substitutes for these bounds.

The C proposal uses only a stationary reference and the current endpoint at
390; the A proposal uses a stationary reference and reset endpoint at 300.
Their rational coefficients are then frozen, and the domain checker takes no
executed trajectory as input. C's current/reset entry checks use $s=1$; A's
use $s=9997/10000$ and $s=1$ respectively. Subsequent two-beat membership checks
multiply these parameters by $\rho$ and $\rho^2$. This directly removes the
old dependency on a later supporting trajectory.

## 10. Accepted shorter witnesses and their meaning

| Realization | Physical dimension | Current entry → completion | Reset entry → window end | Beat duration | Current target time |
| --- | ---: | ---: | ---: | ---: | ---: |
| C_OS | 14 | **374 → 376** | 375 → 377 | 32 | 12032 |
| C_CI | 14 | **374 → 376** | 375 → 377 | 32 | 12032 |
| C_PC | 60 | **374 → 376** | 375 → 377 | 32 | 12032 |
| C_CI_PC | 60 | **374 → 376** | 375 → 377 | 32 | 12032 |
| A_OS | 30 | **375 → 377** | 372 → 374 | 32 | 12064 |
| A_CI | 30 | **375 → 377** | 372 → 374 | 32 | 12064 |
| A_PC | 76 | **375 → 377** | 372 → 374 | 32 | 12064 |
| A_CI_PC | 76 | **375 → 377** | 372 → 374 | 32 | 12064 |
| C_RG2b | 14 | **390 → 392** | 390 → 392 | 8 | 3136 |
| A_RG2b | 30 | **300 → 302** | 300 → 302 | 16 | 4832 |

Target time is $h$ times target completion beat and excludes the source beat.
Each window is two committed positive ordinary beats after certified entry.
Current counts one child for its original event; reset, read-only replay and
certificate replacement count zero additional live gain. Both chiral charts
are checked without counting two births. All ten rows have zero required
supporting physical steps after their displayed windows.

The first eight rows have matching durations but family-specific physical maps
and source histories. RG2b also changes duration and allocation. Duration 32
remains uncertified for these RG2b constructions; failure of the available
bound is not a mathematical impossibility theorem. The table establishes
nonempty applicability, not an optimum, a matched performance comparison or
the necessity of every mechanism for this example.

Anisotropy shortens the sufficient certificate on the declared dynamics. It
does not accelerate that dynamics by changing its norm. For example, the
A_OS current trajectory reverses a relevant edge order between beats 364 and
365. A domain with the selected uniform edge order cannot include the earlier
state on that same trajectory. This explains why larger trapping sets have
limits; no below-100 claim is made.

## 11. Verified evolution, lifecycle and reproducibility

The first eight family constructions use fixed 8192-bit FLINT/Arb outward
evolution and 512-bit trapping calculations. Saved 112-bit outward inspection
coordinates are a storage representation, not the integration precision.
C_RG2b uses 512-bit certified tubes and finite-section residuals. A_RG2b uses
768-bit certification, 384-bit proposals and 320-bit dyadic physical centers.
The centers have exact charge; all projection, section, allocation and rounding
errors enter the outward radius. Schematically,

$$
r_{n+1}\ge q_n r_n+
\|T_h(c_n)-c_{n+1}\|,
$$

with the second term enclosing the full physical evaluation error. A proposal
midpoint is never substituted for exact evolution. Transition overlap is a
consistency check, not an independent proof of the recurrence's provenance.

Immutable incidence, rational graph algebra and fixed-reference inverses are
cached. A selected read is reused only on an identical state. RG2b may reuse a
section enclosure through its proved invariant identity, but must include the
full C/log-W center displacement and verify fresh inverse-chain checkpoints.
That optimization does not promote geometry to persistent physical state.
Precision, admission tolerances and certificate inequalities are unchanged by
these optimizations. Fourth-order Taylor bounds improve the continuous A_RG2b
residual calculation without replacing it by sampling.

The mathematical observation window has a lifecycle counterpart. A candidate
must bind the actual source parent, event, lineage, target profile and charge.
Only successfully committed positive ordinary steps advance its window.
Failed or rolled-back steps, zero-duration calls, inspection and replay do not.
Reset, rebase, graph/context/reference/profile changes and disabled reduction
invalidate the old candidate unless an explicit successor contract re-admits
it. Completion publication and gain accounting must be atomic and at most once
for the occurrence; a replacement certificate does not create a second event.

The selected C-family earlier evidence retains 3012 compressed states ending
at the displayed windows. A_OS still authenticates its original 1041/1024
archives, with membership checked at the adopted earlier endpoints; no new
short execution archive is asserted. A_CI, A_PC and A_CI_PC have fresh 377/374
prefixes. C_RG2b retains 784 selected states and A_RG2b 604. Earlier discovery
records and generators remain useful for failed allocations, numerical method
history and provenance, while retired redundant trajectories are not primary
scientific evidence. No new numerical campaign is required by this editorial
presentation.

## 12. Scope of adoption and remaining work

The proposal adopts one sufficient meaning of stable child organization and
ten bounded exact-equation constructions that satisfy it. It supplies the
definitions, governing maps, source/event construction and proof arguments in
one place. Large exact basis matrices, polynomial coefficients, interval
operands and verified trajectory coordinates remain machine-readable
companions, as numerical data rather than missing scientific definitions.

The result belongs in the full GRC-v4 paper as a constructive application of
its profile-explicit dynamics and lifecycle. The theorem itself is graph
generic once a spatial classifier is chosen; its fixed-row classifier, event
and ten witnesses here are specifically GRC9V4. The full manuscript presents
that result after the inheritance/reduction account and supplies these exact
technical details in Appendix H.

This does not promote a particular family to the universal substrate, establish
arbitrary-graph attraction, prove physical nonabsorbability, supply a general
autonomous topology-selection law or discharge native completion/hierarchy
execution. Those are distinct claims. The accepted shorter endpoint contracts
are current scientific authority; historical family drafts retain their dated
counts and dispositions. Native numerics/lifecycle (P9-9.1a), aggregate
reconciliation (P9-10.5/10.6) and G4 remain open.

## 13. Exact initial resources and reconstruction charts

These tables specify prestates, not nominal post-beat targets. Apply the source
beat and event in §7 to obtain the actual current target state. No search or
midpoint normalization is part of their definition.

### 13.1 First eight realizations

For current, divide each numerator below by $2^{80}$. Reset values
are exact fractions. The private vertex is $r$. Each column sums exactly to 21.

| Vertex | Current numerator | Reset resource |
| --- | ---: | ---: |
| n1 | 2661368957059453683041378 | 709/320 |
| n2 | 2009140577515771537181844 | 1051/640 |
| n3 | 2524087292391079302155713 | 6663/3200 |
| n4 | 1878728270507446918365963 | 77/50 |
| n5 | 1862623815678864281501297 | 3/2 |
| n6 | 1878728270507446918365963 | 77/50 |
| n7 | 1878728270507446918365963 | 77/50 |
| n8 | 1878728270507446918365963 | 77/50 |
| n9 | 1862623815678864281501297 | 3/2 |
| p | 3293685644561895032816200 | 14/5 |
| v | 2432027866086821561836965 | 21/10 |
| r | 1226971160904675315331150 | 1 |

### 13.2 C_RG2b

For current, divide each numerator below by $2^{240}$. Reset values
are exact fractions. The private vertex is $r$. Each column sums exactly to 21.

| Vertex | Current numerator | Reset resource |
| --- | ---: | ---: |
| n1 | 3916620906842994267644569737602390571305837205767750421493859114070390073 | 4540541/2048000 |
| n2 | 3502794928760471283119637305010260470832304031848964721553928785151402686 | 8114051/4096000 |
| n3 | 3418744188688452087500886334735083303542192871426942478674439091559596269 | 7917443/4096000 |
| n4 | 2699791151386743143360294193030406552117862577429887621105395649121099055 | 457/300 |
| n5 | 2628031311769073440459953403280835158214126064545021648285239572791165329 | 554/375 |
| n6 | 2482775793173965599868064970298418635448784850715123507686603758698290163 | 4201/3000 |
| n7 | 2615191922543511873905872102306285781744007513463055964934033058741400719 | 2213/1500 |
| n8 | 2631062540465643358936476009769195730269300359237049031912756753002212161 | 4453/3000 |
| n9 | 2628031311769073440459953403280835158214126064545021648285239572791165329 | 554/375 |
| p | 5169188669366474013203603080773756924601353592975540084426245559053146714 | 2937/1000 |
| v | 3761945043075827347113245011442897895386908055774268449763111272039094164 | 2161/1000 |
| r | 1649610592503841065676691964070922650700358646659372542432878040126052634 | 933/1000 |

### 13.3 A_RG2b

For current, divide each numerator below by $2^{48}$. Reset values
are exact fractions. The private vertex is $r$. Each column sums exactly to 21.

| Vertex | Current numerator | Reset resource |
| --- | ---: | ---: |
| n1 | 624060997025546 | 4540541/2048000 |
| n2 | 558388024696576 | 8114051/4096000 |
| n3 | 545087252683694 | 7917443/4096000 |
| n4 | 431143038829943 | 457/300 |
| n5 | 421172125067949 | 554/375 |
| n6 | 396613583070540 | 4201/3000 |
| n7 | 417692862902909 | 2213/1500 |
| n8 | 420217044578393 | 4453/3000 |
| n9 | 421172125067949 | 554/375 |
| p | 820315002687263 | 2937/1000 |
| v | 591951121902904 | 2161/1000 |
| r | 263161332410110 | 933/1000 |

### 13.4 A_RG2b argument charts

These bound auxiliary arguments; physical states are not clipped. Both charts
also require $|64\log W_e|\le1/16$. A dash denotes an absent vertex.

| Vertex | Source resource interval | Target resource interval |
| --- | --- | --- |
| n1 | [139/64, 9/4] | [17/16, 9/4] |
| n2 | [31/16, 129/64] | [69/64, 133/64] |
| n3 | [121/64, 63/32] | [69/64, 63/32] |
| n4 | [95/64, 25/16] | [65/64, 25/16] |
| n5 | [91/64, 49/32] | [57/64, 97/64] |
| n6 | [87/64, 23/16] | [63/64, 23/16] |
| n7 | [23/16, 97/64] | [1, 97/64] |
| n8 | [23/16, 49/32] | [57/64, 97/64] |
| n9 | [91/64, 49/32] | [63/64, 97/64] |
| p | [185/64, 191/64] | [185/64, 51/16] |
| v | [67/32, 143/64] | — |
| r | [57/64, 31/32] | [57/64, 37/32] |
| o | — | [-1/64, 37/32] |
| s1 | — | [-1/64, 19/16] |
| s2 | — | [115/64, 205/64] |
| s3 | — | [-1/64, 19/16] |

## 14. Computational companions and provenance

The [section-to-claim/debt correspondence](./Traceability.md) connects this
proposal and Appendix H to the accepted contracts, specification chains and
side-tool surfaces, including the native obligations that remain open.

The mathematical definitions and proofs above do not require a family draft.
The following records supply large numerical operands and reproducible checks.
Exact rational bases and polynomial coefficients are certificate data, analogous
to a numerical dataset; reproducing them from an optimizer is unnecessary.

| Certificate subject | Exact operands and checked inequalities |
| --- | --- |
| Earlier C domains | [Rational domain](../../evidence/spark-completion/applicability/earlier-closure/CEarlierDomain.json), [full-map proofs](../../evidence/spark-completion/applicability/earlier-closure/CEarlierProofs.json), [prefix membership](../../evidence/spark-completion/applicability/earlier-closure/CEarlierResearch.json) |
| Earlier A_OS domain | [Joint rational domain](../../evidence/spark-completion/applicability/earlier-closure/AOSAnisotropicDomain.json), [checks](../../evidence/spark-completion/applicability/earlier-closure/AOSEarlierChecks.json.xz) |
| A_CI, A_PC, A_CI_PC | [A_CI proof and membership](../../evidence/spark-completion/applicability/ACIResearchProgress.json), [A_PC](../../evidence/spark-completion/applicability/APCResearchProgress.json), [A_CI_PC](../../evidence/spark-completion/applicability/ACIPCResearchProgress.json) |
| C_RG2b direct domain | [Degree-40 curve](../../evidence/spark-completion/applicability/CRG2bDirectDomain.json), [continuous certificate](../../evidence/spark-completion/applicability/CRG2bDirectCertificate.json), [declaration](../../evidence/spark-completion/applicability/CRG2bDirectDeclaration.json) |
| A_RG2b direct domain | [Joint degree-40 curve](../../evidence/spark-completion/applicability/ARG2bDirectDomain.json), [continuous certificate](../../evidence/spark-completion/applicability/ARG2bDirectCertificate.json.xz), [declaration](../../evidence/spark-completion/applicability/ARG2bDeclaration.json) |

The [research implementations](../../research) contain the exact equations,
derivatives, rational operands and outward interval producers. The
[verification scripts](../../scripts) reconstruct the domain and membership
checks. The [side-tool guide](../../tools/exploratory-side-tool/docs/SparkCompletionOverview.md)
connects the same accepted subjects to read-only inspection. Evidence remains
compressed. No new physical run or scientific authority is created by this
document integration.

### 14.1 Historical results for specific questions


Consult these initial witnesses when their particular original proof, source
preparation, transfer or audit history is needed. Their longer counts describe
the first accepted sufficient certificates, not the primary endpoints in §10.

| Initial result | Historical endpoint/support | Specific reason to consult it |
| --- | --- | --- |
| [C_OS first proof](../2026-10-GRC9V4-Spark-Completion.md) | Current 902 | Original common criterion/theorem, homogeneous site binding and complete source-to-event construction. Reset entry was 867; the initial record did not execute a two-beat reset window. |
| [C_CI first proof](../2026-10-GRC9V4-Spark-Completion-CCI.md) | Current 851, reset 819 | Selected joint-root construction and original full-CI derivatives. |
| [C_PC first proof](../2026-10-GRC9V4-Spark-Completion-CPC.md) | Current 851, reset 819 | Carrier domain, read/write and event-history treatment. |
| [C_CI_PC first proof](../2026-10-GRC9V4-Spark-Completion-CCIPC.md) | Current 851, reset 819 | Same-source immediate/carrier composition and selected root. |
| [A_OS first proof](../2026-10-GRC9V4-Spark-Completion-AOS.md) | Current 1041, reset 1024 | Original joint C/W construction and retained trajectories. The [anisotropic derivation](../../decisions/SparkCompletionAOSEarlierClosure.md) explains the adopted reduction. |
| [C_RG2b investigation](../../decisions/SparkCompletionCRG2bApplicability.md) | Superseded finite-union proof needed supporting evolution through 2089 | Proof-development history and generator lineage. The current direct continuous-domain construction is given in §9. |

The [C-family earlier-domain derivation](../../decisions/SparkCompletionCEarlierClosure.md)
supplies the parallelotope, carrier product, correlated C_OS split estimate and
prefix provenance. The [adoption specification](../../../../../specs/grc-9-v4-spark-completion-earlier.md)
and its [source manifest](../../../../../specs/grc-9-v4-spark-completion-earlier-source-manifest.json)
bind the five revised endpoint contracts. The dated research documents retain
their original pending flags; the accepted successor controls their present
endpoint status.

The five later primary family papers carry their own authority and
specification chains. The [all-ten applicability record](../../decisions/SparkCompletionAllTenApplicability.md)
and [side-tool guide](../../tools/exploratory-side-tool/docs/SparkCompletionOverview.md)
provide the program and inspection views. Initial payloads already retained for
accepted provenance remain; retired exploratory payloads are not restored.
