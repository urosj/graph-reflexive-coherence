> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# ATC — partition-dependent participation and restorative stability

**Status:** independent mathematical review PASS; wording/evidence corrections
and exact review-pressure additions applied. Supplied binary maps, zero feedback,
no new accepted claim, autonomous generator, runtime potential or initializer.
The reviewed degree-two theorem and original execution records remain unchanged.

The user authorized the [next question](./ATCAddressabilitySufficientConditions.md#6-review-disposition-and-remaining-work):
determine how participation versus stability depends on graph/partition before
introducing feedback. The result is a genuine distinction within one declared
unit-bridge family: **a singleton half-edge block excludes an affine
participation/restorative-curvature window, whereas two blocks of size at least
two permit it for kappa > 0**. A slope in that window admits a stable sufficiently
small positive Euler step; an arbitrary fixed step need not be stable.
Slope softening is therefore
not necessary for every supplied higher-degree split. This does not contradict
the degree-two theorem or select a topology-change law.

## 1. Fixed law, source and supplied map

Keep the same reduced exact-arithmetic law, unit vertex measure, unit edge
weights, identity Hodge, all-one W, no carrier and zero feedback:

$$
f(C)=-\eta L[p(C)-\kappa LC],\qquad C^+=C+h f(C),
\quad \eta,h>0,\quad\kappa\ge0.
$$

The source is a star with d leaves, each holding r > 0, and a parent holding
s > r. Supply a partition of its incident edges into two nonempty blocks of
sizes m,n, where d=m+n. Replace the parent by two children u,v, attach each old
leaf to its block's child, and add one unit-weight u--v edge. Call this target
the double star D(m,n). No edges among the exterior leaves are added.

Equal source inflows give block activity shares m/d,n/d. Here these are
**declared exact rational allocation shares**, not the F2 binary64 allocator:

$$
x_u=\frac{m}{d}s,\qquad x_v=\frac{n}{d}s,\qquad
x_u+x_v=s.
$$

Strict child endowment requires

$$
s>\frac{d}{\min(m,n)}r.
$$

The total resource dr+s is preserved, but the number of unit-measure vertices
changes from d+1 to d+2. This is constitutive fission, not a measure-aware neutral
refinement. Source symmetry supplies no preferred labeled partition: supplied
maps remain external hypotheses, even where a favorable block size exists.
For a symmetric degree-four source there are three distinct labeled 2+2
partitions. An equivariant autonomous generator still needs physical asymmetry,
an explicitly justified invariant set-valued/batch outcome, or `unresolved`;
vertex or edge IDs cannot break that symmetry. Classifying the size class does
not resolve its members.
The degree-at-most-two CAN-F2 implementation remains unchanged and does not
execute these higher-degree maps.

## 2. Source participation has a graph-dependent threshold

At a source leaf, (LC)_leaf = r-s; at the parent, (LC)_parent = d(s-r).
The magnitude of each current directed inward to the parent is therefore

$$
j_s=\eta[(d+1)\kappa(s-r)+p(r)-p(s)].
$$

The parent field is d j_s and each leaf field is -j_s. Thus

$$
j_s>0\quad\Longleftrightarrow\quad
\frac{p(s)-p(r)}{s-r}<(d+1)\kappa.
$$

For p continuously differentiable on an interval containing [r,s], this implies
p'(xi) < (d+1) kappa for some xi in (r,s). Whether that slope must be softer
than the target operating slopes depends on the target, not the source degree
alone. Endowment remains a separate inequality and does not imply stability.

## 3. Exact affine compatibility classification

Let p(c)=a c+b, with the same a,b before and after the supplied split. On the
target charge plane the energy Hessian is aI-kappa L_t. Connectedness makes
the nonconstant Laplacian modes the charge-tangent modes. Write
Lambda_t = lambda_max(L_t). Exact target strong convexity requires
a > kappa Lambda_t, whereas source inward participation requires
a < kappa(d+1). Consequently the affine source-participation/target-restorative-
curvature window is exactly

$$
\kappa\Lambda_t<a<\kappa(d+1).
$$

At kappa=0 there is no window: a>0 and a<0 conflict. For kappa>0 its existence
is equivalent to Lambda_t < d+1.

For every slope in that window, the continuous-time restoring rates
eta lambda(a-kappa lambda) are positive. A sufficiently small h > 0 makes all
Euler modes stable. For a preassigned h, one must additionally check

$$
0<h\eta\lambda(a-\kappa\lambda)<2
\quad\text{for every nonzero target eigenvalue }\lambda.
$$

The partition iff is not a fixed-step stability theorem. For example, the
compatible 2+2 slope 19/4 below has lambda=3 multiplier -17/4 at h=1,
eta=kappa=1, and is therefore unstable at that larger step.

### Proof of the partition boundary

In leaf-first order, eliminate the d leaf entries of (d+1)I-L_t. Their block
is dI. The remaining symmetric Schur complement is

$$
S=\begin{pmatrix}
n-m/d&1\\
1&m-n/d
\end{pmatrix},\qquad
\det S=\frac{d+1}{d^2}
\left[(d+1)(m-1)(n-1)-1\right].
$$

Both diagonal entries are positive for every m,n >= 1. If either block has
size one, the determinant is negative, hence S is indefinite and
Lambda_t > d+1. If both have size at least two, the determinant is positive,
so S and the full matrix are positive definite and Lambda_t < d+1. Equality
never occurs in this family. Therefore

$$
\boxed{\text{nonempty affine restorative-curvature window}
\quad\Longleftrightarrow\quad
\kappa>0,\ m\ge2,\ n\ge2.}
$$

This is an all-integer algebraic result for the declared double-star family,
not an inference from a finite graph scan. It classifies source participation
plus target curvature; resources, step size and a positive return domain
still need their own certificates.

As an independent matrix identity, the target characteristic polynomial is

$$
\det(tI-L_t)=(t-1)^{d-2}t
\left[t^3-(d+4)t^2+(mn+2d+5)t-(d+2)\right].
$$

It follows by separating leaf-difference modes from the four group-constant
coordinates. The [exact checker](../scripts/certify_atc_partition_stability.py)
also reconstructs each full Laplacian and checks its determinant polynomial,
Schur sign and load identities for all **16 unordered partition-size/isomorphism
classes** with 2 <= d <= 8. These represent 247 labeled unordered nonempty
binary partitions, since a labeled d-edge star has 2^(d-1)-1 such partitions.
The checker does not enumerate those 247 maps: complete source symmetry and
unit weights make maps in the same size class equivalent by leaf permutations
and possible child exchange. This argument does not cover asymmetric sources.

| Source degree and partition | Target spectral relation | Affine window, kappa > 0 |
| --- | --- | --- |
| d=2, 1+1 | Lambda_t = 2+sqrt(2) > 3 | None; recovers the reviewed exclusion |
| d=3, 1+2 | Lambda_t > 4 | None |
| d=4, 1+3 | Lambda_t > 5 | None |
| d=4, 2+2 | Lambda_t = (5+sqrt(17))/2 < 5 | Nonempty; smallest such partition |
| Any d, singleton block | Lambda_t > d+1 | None |
| Any d, both blocks >= 2 | Lambda_t < d+1 | Nonempty |

### Unit child bridge is part of the theorem, not a dispensable convention

As scope pressure only, replace the child bridge's weight by tau > 0 while
keeping old-edge weights one, using that weighted Laplacian in both occurrences
of L in the reduced equation. At the same source threshold d+1, the Schur
complement becomes

$$
S_\tau=\begin{pmatrix}
n+1-\tau-m/d&\tau\\
\tau&m+1-\tau-n/d
\end{pmatrix},\qquad
\det S_\tau=\frac{d+1}{d^2}[mn(d+1)-\tau d^2].
$$

The diagonal entries remain positive below the determinant-zero threshold
tau = mn(d+1)/d squared. Thus a 1+3 split permits an affine window for
0 < tau < 15/16, whereas the 2+2 window disappears at tau >= 5/4. At equality,
Lambda_t=d+1, so the strict affine interval is empty. These exact scope checks
show why the unit-bridge cardinality boundary cannot be exported to arbitrary
weighted graphs. They do not extend the current theorem's declared family,
admit a weighted runtime contract, or identify bridge weight with a genuine
V4 geometry/history feedback channel. No weighted continuation campaign is
opened here.

## 4. What happens to the nonlinear return and response conditions

The old proof generalizes with graph-dependent constants, not an unchanged
universal slope threshold. Let B be a compact closed positive coordinate box
containing the target initial state C0=(r,...,r,x_u,x_v),
p be C1 on a surrounding interval also covering [r,s], and
ell <= p' <= M throughout B's coordinate intervals. A sufficient curvature
bound is

$$
\mu=\ell-\kappa\Lambda_t>0.
$$

This uniform bound is sufficient, not a characterization of all nonuniform
charge-tangent Hessians. If a singleton block is present, it requires target
slopes above kappa Lambda_t > kappa(d+1) when kappa>0, while the source secant
is below kappa(d+1). A softer derivative must then occur outside the target
operating intervals. At kappa=0 positive target slopes likewise contrast with
a negative source secant. For two larger blocks and kappa>0 there is no such
forced contrast: a single constant slope can lie in the affine window.

### Conditional nonlinear encounter-return statement

Require, rather than infer from participation, an interior target equilibrium
C* with constant energy gradient and the correct charge. Strong convexity gives
its uniqueness in B on that charge plane. Let N=d+2, P_T=I-11^T/N,
g0=||P_T grad E(C0)||, e0=g0 squared/(2 mu), r0=g0/mu, and let d_* be a positive
lower bound on dist_2(C*, boundary B). Sufficient conditions are

$$
h\eta\Lambda_t M<2,\qquad
(1+h\eta\Lambda_t M)R<d_*,\qquad r_0+D<d_*,
$$

$$
e_0+Mr_0D+\frac M2D^2<\frac{\mu R^2}{2}.
$$

For lambda_2 = lambda_2(L_t)>0, the same displacement-first trapping argument,
followed by Taylor's theorem and charge cancellation, yields

$$
E^+-E^*\le q(E-E^*),\quad
q=1-2h\eta\lambda_2\mu
\left(1-\frac{h\eta\Lambda_t M}{2}\right),\quad 0\le q<1.
$$

For completeness, set x=h eta Lambda_t M in (0,2) and
rho=lambda_2 mu/(Lambda_t M) in (0,1]. Then

$$
0<1-q=2\rho x(1-x/2)\le2x-x^2\le1,
$$

which proves the stated range of q.

Here L_t squared <= Lambda_t L_t replaces the old bound 4 L_t. As before,
one charge-preserving encounter of norm <= D at any unencountered age returns
to C*. This does not guarantee an equilibrium or feasible inequalities for
every nonlinear potential/partition, nor repeated encounters.

### Child-centered loads and response

Use w_i=-L_t e_i. Child degrees are d_u=m+1, d_v=n+1, so a positive epsilon
load removes d_i epsilon at the addressed child. Normalize by that deficit:

$$
Q_i=\frac{h}{d_i\epsilon}
[f_i(C+\epsilon w_i)-f_i(C)]
=\frac{h\eta}{d_i}(L_t e_i)^\top
[\operatorname{diag}(D_j)-\kappa L_t](L_t e_i),
$$

where D_j is the integral of p'(C_j+z epsilon w_ij) for 0 <= z <= 1.
On a certified load segment, Q_i >= h eta mu (d_i+1) > 0. Positivity remains
a consequence of curvature and the chosen deficit loads, not an independent
physical discriminator or general functional differentiation.

The exact load Gram matrix and joint-load bound are

$$
G=\begin{pmatrix}
(m+1)(m+2)&-(d+2)\\
-(d+2)&(n+1)(n+2)
\end{pmatrix},
$$

$$
\max_{|A|,|B|\le\epsilon}\|Aw_u+Bw_v\|^2
=\epsilon^2(m^2+n^2+5d+8).
$$

The maximum occurs at opposite-sign corners. G is positive definite: if a
linear combination of L_t e_u,L_t e_v vanishes, the corresponding vector
supported only on u,v must be constant by connectedness, hence zero because
there are exterior leaves. These are two independent load directions, not
dynamically independent child identities. For m=n=1 the old Gram matrix and
20 epsilon squared bound are recovered.

## 5. Smallest affine example: funded participation and positive return

Choose m=n=2, r=1, s=3 and declare

$$
p(c)=\frac{19}{4}c,\quad \kappa=\eta=1,\quad h=\frac18,
\quad\epsilon=\frac1{64}.
$$

These are explicit mathematical parameters, not a native V4 binding. The
source has four resource-one leaves and a resource-three parent. Each inward
current is 1/2. The fixed equal split gives

$$
C_0=(1,1,1,1,3/2,3/2),\qquad Q=7,
\qquad C^*=(7/6)\mathbf1.
$$

Both children exceed their attached leaves by 1/2. The target spectrum is
0,1,1,3,(5-sqrt(17))/2,(5+sqrt(17))/2. Its nonzero eigenvalues satisfy

$$
\frac38<\lambda<\frac{37}{8}<\frac{19}{4}.
$$

Thus the target is strongly convex, while the source's highest Laplacian mode
has eigenvalue 5 and negative energy curvature 19/4-5=-1/4. The graph change
alters stability with no change of constitutive slope and no multiwell potential.
This is not a proof that the source must split or that a runtime should select
this partition.

The actual states give a sharper mode-switch, not just a comparison of extreme
eigenvalues. The centered source C- minus (7/5)1 lies entirely in lambda=5;
the centered mapped target C0 minus (7/6)1 lies entirely in lambda=3. Their
amplitude multipliers at the same h=1/8 are

$$
1-\frac18\,5(19/4-5)=\frac{37}{32}>1,
\qquad
1-\frac18\,3(19/4-3)=\frac{11}{32}<1.
$$

Thus the declared source mode expands while the mapped target mode contracts
under the same affine slope. Each amplitude is relative to its own graph's
homogeneous equilibrium; this is not an equality between source and target
norms in different-dimensional state spaces.

### Exact linear return and a positive-resource domain

On the target, let z=C-C*. Each eigenmode evolves by

$$
z^+_\lambda=[1-h\eta\lambda(a-\kappa\lambda)]z_\lambda,
\qquad a=19/4.
$$

The rational spectral bounds give mu=1/8 and

$$
\frac3{64}<\lambda(a-\lambda)\le\frac{361}{64},\qquad
0<\frac{151}{512}\le1-h\lambda(a-\lambda)<\frac{509}{512}<1.
$$

Therefore the Euclidean distance contracts by at most 509/512 per step on the
whole charge plane. This direct affine argument does not require the more
conservative nonlinear energy-sublevel certificate of section 4.

The initial distance squared is 1/3, hence distance < 3/5. Here the load Gram
matrix is [[12,-6],[-6,12]], determinant 108. Every signed joint encounter has
norm <= 6 epsilon = 3/32. At any unencountered age the loaded distance is below

$$
\frac35+\frac3{32}=\frac{111}{160}<\frac34<\frac76.
$$

The radius-3/4 ball about C* is invariant under the linear update, so every
coordinate stays above 7/6-3/4=5/12 and the loaded state returns geometrically
to C*. This certifies positivity, not merely linear stability in an unphysical
negative-resource region. It is exact-arithmetic, one-encounter-at-any-age
return, not a rounded trajectory or unlimited repeated-use theorem.

For either child, (L_t squared)_ii=12 and (L_t cubed)_ii=50, giving

$$
Q_u=Q_v=\frac{1/8}{3}\left(\frac{19}{4}\,12-50\right)
=\frac7{24}>0.
$$

Yet the initial target child field is -7/4 at each child, with +7/8 at each
leaf. Positive restorative response and return do not require initial child
accumulation. The resulting homogeneous equilibrium also does not demonstrate
persistent differentiated identities; the addressed sites are fixed by the
supplied topology and the specified loads.

### Funded but unstable partition control

For the same affine law and a 1+3 partition, use r=1,s=5 so both blocks are
strictly funded (minimum margin 1/4) and each source inflow is 1. Nevertheless
Lambda_t>5>a and target curvature is indefinite. The exact LDL pivots end in
-1349/2980. Neither insufficient endowment nor absent source participation
explains this failure; the partition's target spectrum does. Resources differ
from the positive example, so this is a curvature control, not a matched causal
campaign or a quantitative intervention-effect comparison.

### Same-source exact partition pressure

The review supplies a cleaner comparison without changing the law or running
a trajectory campaign. Use the same source (1,1,1,1,5) for both maps, with
a=19/4, kappa=eta=1, h=1/8. Both source inflows are 1 per edge and both targets
have charge 9 and homogeneous equilibrium (3/2)1. Let D_k squared denote the
squared Euclidean distance to that equilibrium.

| Supplied partition | Child resources | Minimum funding margin | D_0 squared | D_1 squared | D_1 squared / D_0 squared | Child Q values |
| --- | --- | --- | --- | --- | --- | --- |
| 2+2 | 5/2, 5/2 | 3/2 | 3 | 363/1024 | 121/1024 < 1 | 7/24, 7/24 |
| 1+3 | 5/4, 15/4 | 1/4 | 49/8 | 66211/8192 | 66211/50176 > 1 | 15/32, -3/16 |

The 2+2 displacement is again exactly the lambda=3 mode. Direct rational
evaluation gives the 1+3 ratio and its negative three-edge-child response.
Both exact one-step images remain positive and conserve charge. With the same
source, total resource, constitutive law and step size, the supplied 2+2 map
contracts while 1+3 expands over this step and lacks two positive restorative
child channels. The intervention varies the partition and its declared
activity-based allocation together, not topology alone at a fixed target C.
This does not transfer the s=3 positive-ball encounter certificate to s=5,
prove indefinite positive-resource expansion, or select a partition autonomously.

## 6. Evidence, claim limits and continuation

The [original reviewed certificate](../evidence/autonomous-topology-change/ATCPartitionStabilityCertificate.json)
contains rational parameters, source/target fields, spectral and return bounds,
all 16 partition-size-class checks, 142 direct characteristic-determinant evaluations,
the negative control and source hashes. It performs no trajectory updates,
native steps or topology events. The all-integer Schur argument is the proof;
the finite exact checks discriminate algebra and implementation errors.

The [current review successor certificate](../evidence/autonomous-topology-change/ATCPartitionStabilityReviewCertificate.json)
uses the corrected field `unordered_partition_size_classes`, with explicit
symmetry coverage rather than claimed enumeration of 247 labeled partitions.
The old `unordered_partitions` field is a historical label error, not extra
evidence. The successor reproduces the original record unchanged, binds it and
its checker, and adds the fixed-step counterexample, four exact Euler images
for the mode switch and same-source pressure, and twelve rational bridge-scope
checks. There is no native step, trajectory campaign or rewritten acceptance
evidence.

The supplied independent review gives mathematical PASS for the partition
curvature-window theorem, nonlinear continuation, 2+2 funded/return witness,
and 1+3 funded instability control. It reports independent symbolic and
numerical pressure and verifies the original evidence identities. The corrected
scope and additional exact pressure above implement its recommendations;
mathematical PASS is not formal admission of claim nodes or closure of an
autonomous capability.

| Bounded result | Claim/debt consequence |
| --- | --- |
| Exact affine window iff kappa>0 and both supplied blocks have size >=2 | Proposed mathematical successor to the degree-two exclusion; that old claim stays valid on its original graph. No accepted graph node is created. |
| Positive-resource affine return and two restorative child responses | Strengthens the mathematical refinement/support evidence relevant to DB-07/27, without closing general physical discrimination or DB-17–20's stronger formation/identity interpretations. |
| Explicit supplied partition and exact resource map | Partial construction evidence only; endogenous witness/resolution/partition, target integration and continued autonomy under DB-02/09/12/14/15/16/26/28 remain open. |
| Zero-feedback reduced law | Does not discharge structural-functional DB-05/06/08, native N-P/C-P, all-family capability cells or feedback/composition obligations. |

The debt references follow the existing
[capability continuation](./ATCCapabilityClosureContinuation.md#6-claims-debts-and-review-retention).
They are research dispositions, not formal accepted debt transformations.
In particular, the source-only CAN-F2 guard must not gain a target-stability
filter from this calculation. No parameter, map or event is selected by a
future outcome; this is a mathematical comparison of declared maps.

The next distinct question is now **one actual V4 feedback channel on the old
degree-two map**, keeping this graph-only result separate. Restore its genuine
coupled state evolution, identify an appropriate equilibrium or invariant
object, and derive a non-vacuous coupling/stability domain or obstruction.
Freezing a history variable or merely changing kappa would not establish that
result. Combining feedback with higher-degree partitions follows those
separate analyses. The graph-only mathematical review now passes; stop extending
this zero-feedback star family for now. Formal bounded claim/debt admission
remains outstanding; none of the thirty capability cells is closed here.

That next question now has a separate
[Candidate A retained-history derivation](./ATCHistoryFeedbackContinuation.md):
an explicit finite gamma interval with coupled resource/history return and
verified writer-to-next-current effect on the degree-two graph with
conductance-depressed W<=1. Its independent mathematical review now passes,
with scope/debt clarifications and unchanged evidence. It does not change this
graph-only theorem, combine the two extensions or admit the new research law
into the native substrate.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_partition_review.py
```

The checker prints a fresh record and does not overwrite the retained evidence.
