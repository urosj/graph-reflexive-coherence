> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# CAN-LSF — first and second Read-Back lifts

**Status:** proposed conformance lift, not accepted constitutive scope. The
[bounded zero-channel acceptance](./ATCSectorConstitutiveAcceptance.md) remains
unchanged. The [review motivating this work](../evidence/autonomous-topology-change/review/CAN-LSF-ReadBack-Lift-Review.md)
asks whether the **same** source-selected fission survives genuinely consumed
Read-Back and geometry/history feedback. It does not authorize target search,
another grouping rule or an automatic transfer of the old cone theorem.

## 1. Fixed subject, two distinct conclusions

Retain a=19/4, h0=1/8, tau_A=h0/log(2), eta=kappa_c=zeta_A=1, alpha=beta=0,
W_floor=1/2, unit reference pairings/weights, no carrier and the affine research
potential p(c)=a c. Retain the oriented four-star (i,4), i=0,...,3, with

$$
C_0=(1,1,1,1,5),\qquad
W_0=((19/20)^2,(19/20)^2,(77/80)^2,(77/80)^2).
$$

Reset stays independently at (C0,W0), not a copy of the eventual live state.
Retain the exact two-sector test, source-only round-even allocator, funding,
unit-site binary surgery, old-edge lineage and bridge seed one. Read source
conditions only at successful ordinary boundaries under K0. The initially
inactive check is diagnostic, not a new pre-ordinary event opportunity.

**Lift 1:** examine the fixed enabled point

$$
\chi_A=1/16,\quad\gamma=1/1024,\quad
\kappa_H=\kappa_{Ah}=1.
$$

**Lift 2:** attempt a uniform proof on the declared compact positive box

$$
\chi_A\in[1/32,1/16],\quad\gamma\in[1/2048,1/1024],
\quad\kappa_H,\kappa_{Ah}\in[1/2,1].
$$

These are proposed research parameters, not admitted native profile IDs.
The point and box are specified before running their checker. Failure remains
a result: no quiet shrinkage, new source, changed allocator or improved target.
A justified successor proposal may change a failed assumption explicitly.
The box has positive lower bounds; 0<chi<=bar_chi alone would not be compact.
Alpha/beta, arbitrary initial histories and other realizations are excluded.

## 2. The actual one-pass equations and stage question

Use tail-positive B, D=Diag(W), d=B^T C and L_W=B D B^T. H^[0]=I and
H^[1] below are **two edge-Hodge stages**; they are not vertex H0 versus edge
H1. Let b0 denote the baseline current at reference geometry:

$$
b_0=D B^\top(aI-L_W)C.
$$

For any stage baseline b, define componentwise

$$
\widehat W(b)=\max(1/2,\exp(-\gamma b^2/2)),\qquad
q(b)=\frac{W-\widehat W(b)}{W+\widehat W(b)},
$$

$$
F(b)=\frac{b}{1-\chi_A q(b)},\qquad
r(b)=\chi_A q(b)F(b).
$$

The denominator is strictly positive for this parameter box because |q|<1
and chi_A<=1/16. The pre-read target uses **baseline b**, not F(b).
At reference geometry J_ref=F(b0) and f0=r(b0). For these loopless graphs,
normalized star assembly is

$$
S(f)_{ij}=\tfrac12\#\{v:i,j\in\operatorname{star}(v)\}f_i f_j,
\qquad\operatorname{tr}S(f)=\|f\|_2^2.
$$

Then one fresh geometry and one fresh selected current are

$$
H^{[1]}=I+\kappa_H S(f_0),\qquad
b_1=b_0-\kappa_{Ah}D B^\top B(H^{[1]}-I)d,
\qquad J_{\rm fresh}=F(b_1).
$$

The regenerated structural form is f1=(H^[1])^-1 r(b1), **not** r(b1).
The split residual is kappa_H[S(f0)-S(f1)], checked in the reference-whitened
edge operator norm; a Frobenius upper bound suffices. Fix research tolerance
1/512 before execution. Exceeding it is a realization-admission failure, not
physical negative-resource evidence and not permission for a second corrector.

Only after the selected fresh read and positive resource admission:

$$
C^+=C-h_0B J_{\rm fresh},\qquad
y^+=\tfrac12 y+\tfrac12\log\max(1/2,\exp(-\gamma J_{\rm fresh}^2/2)),
\quad y=\log W.
$$

Where the floor is inactive this is y+=y/2-gamma J_fresh^2/4. Every next
ordinary beat starts again from reference geometry. No trial geometry, stale
current or provisional writer state is retained as physical state.

This follows the stage structure in
[Candidate A](../../../../src/pygrc/models/grc_v4_candidate_a.py),
[OS realization](../../../../src/pygrc/models/grc_v4_realizations.py) and
[star assembly](../../../../src/pygrc/models/grc_v4_geometry.py), and the earlier
[research reduction](./ATCPartitionOSFeedback.md). It is an investigation-local
affine-potential extension, not execution of the native zero-potential profile.
Earlier fixtures' numerical bounds do not transfer to this source.

**K0 operand:** recompute the selected **reference-stage** J_ref at the
committed poststate. At nonzero chi this is neither bare b0 nor J_fresh, and
neither is necessarily the last beat's consumed current. The allocator uses
J_ref. J_fresh and no-event continuation are diagnostic consumers only. If the
source test ceases to predict the obstruction of complete fresh OS evolution,
report that failed implication. If a fresh-current event consumer is needed,
propose its explicit stage/authority successor; do not substitute it here.

## 3. Structural symmetry, not a fitted tolerance

The source leaf swaps (0 1) and (2 3), with their corresponding edge swaps,
fix C0,W0, the unit references and every scalar constitutive parameter. B,
componentwise targets/current blocks, normalized star assembly, H inversion,
continuity and the writer are equivariant under those swaps. Consequently the
fixed subspace C0=C1, C2=C3, W0=W1, W2=W3 is invariant under the complete map,
including nonzero feedback. The same leaf swaps remain target symmetries.
This is an exact-real argument about the whole bound data, not a claim that
arbitrary backend/reference choices or numerical roundoff preserve equality.

It does **not** prove that the two different sectors stay ordered forever.
Unlike the zero-gamma square-root writer, different current-dependent writes
can change their separation. Verify strict inter-sector separation through
the event boundary; do not import the old all-finite-time u<v theorem. If the
sectors merge or the required cone signs fail, retain that failure. There is
no approximate-equality repair or generic symmetry-breaking claim.

## 4. Lift 1 evidence obligations

Run only one prepared source and its fixed prescription, with two independent
target roles. The bounded diagnostic is capped at 16 no-event attempted beats
and three target beats per role; this is not a trajectory campaign or a proof
of indefinite restoration. Every attempted beat must distinguish OS residual,
resource and writer admission; a failed beat publishes nothing.

Required distinctions are:

1. Initial no-event and a later successful committed source with all unchanged
   activation conditions, exact paired equalities, strict sector separation,
   and positive funding. Record the actual dyadic k; do not demand 30876.
2. Nonzero J_ref-b0, J_fresh-J_ref, generated edge-Hodge increment, consumed
   geometry potential and gamma-dependent writer contribution. Compare
   same-input chi=0 and kappa_Ah=0 controls; nonzero parameter declarations
   without a consumed correction are insufficient. No control selects a target.
3. Establish what happens under **enabled** no-event continuation, not the old
   reduced cone recurrence. If finite execution fails, identify whether this
   is physical resource loss, OS admission, or another domain boundary. A
   Decimal diagnostic is not a rounded enclosure or an analytic proof.
4. Use the one reference-selected resource map on live and actual reset, with
   their own old W plus bridge seed one. Recompute both target entries under
   the enabled equations. Check charge, positivity and the return domain.
5. Keep the no-split and history-reset-without-split comparisons separate.
   Retain homogeneous nonfiring and the already reviewed unresolved/blocked
   controls; do not rerun their old campaigns to inflate evidence counts.

Even a positive diagnostic does not certify every source satisfying the old
guard. The nonzero successor's proved activation/restoration domain must be
stated explicitly at review. The old broad obstruction theorem cannot be
relabelled as a full-feedback theorem.

## 5. Lift 2: a conditional target theorem and the remaining uniform chain

There is a useful analytic route that does not require constant histories or
commuting Laplacians. On the fixed double-star, consider

$$
X=\|C-(3/2)\mathbf1\|_2\le R=2/3,\quad
-b\le y_e\le0,\quad b=1/8,\quad\sum C=9.
$$

Since exp(-b)>1-b=7/8, the nonzero spectrum of L_W lies between 49/128 and
73/16. The reduced resource map at **each incoming W** contracts the charge-zero
space by at most q0=1829/2048; its eigenvalues are positive. Also ||B||<5/2
and ||b0||<=4X, because D^2<=D and
max(lambda(a-lambda)^2)=4a^3/27<16 on this spectral interval.

The [focused checker](../scripts/check_atc_sector_readback_lift.py) evaluates
the following sufficient inequalities with rational arithmetic. Set Q=1/15,
c=1/16, g=1/1024, A=4, L=73/16, N=5/2 and

$$
r=\frac{cQ}{1-cQ},\quad M=AR,\quad
E=LNR\,r^2M,\quad G=201/200.
$$

The inequalities (b+g M^2/2)/2<Q and
(b+g((1+E)M)^2/2)/2<Q bound both contrasts using
|tanh(z)|<=|z|. The floor is inactive on these bounds. Since
(1+E)/(1-cQ)<G, the complete selected current differs from b0 by at most
(G-1)AX. Therefore

$$
X^+\le q_X X,\qquad
q_X=q_0+h_0N(G-1)A=q_0+1/160<9/10.
$$

The history condition g(GM)^2/2<b keeps y+ in [-b,0]; both structural forms
give split-residual bound (rM)^2+(cQGM)^2<1/512. Thus this is a **uniform
conditional positive-return theorem**, for the whole proposed parameter box,
once a separately admitted target role enters this domain. Every coordinate
stays at least 5/6. X decays geometrically; the writer recursion then implies
y tends to zero. It is not necessary to claim that the joint (C,y) map is a
contraction in an undeclared metric.

This theorem does **not** prove that the source fires or that its actual
current/reset target entries lie in the ball. Uniform closure still needs:

- Initial nonactivation, a successful eligible boundary and the full-OS
  obstruction on a stated source domain, with certified margins throughout
  the proposed box. A spectral certificate alone is insufficient.
- Symmetry as above plus strict separation and source-cone/current signs.
- Enclosed activity ratios and funding. If the ratio crosses dyadic rounding
  boundaries, bound all possible prescribed k values; no assumption that k
  stays constant and no target selection among those values.
- Actual independent current/reset entry, OS residual and floor/domain
  admission, before invoking the uniform return theorem.
- Nonvacuity throughout whatever enabled scope is claimed, not just its corner.

A sweep or corner samples do not establish these statements. Use explicit
analytic inequalities or outward enclosures, retaining the first failed
implication if they do not close. Strict margins plus continuity might prove
existence of a smaller neighborhood; that does not certify this particular
box. Exact sector invariance is a separate structural premise, and the dyadic
map is discontinuous at ties. No generic continuity shortcut crosses either.

## 6. Review and second adjudication

The new [evidence record](../evidence/autonomous-topology-change/ATCSectorReadBackLiftChecks.json)
must separate rational sufficient bounds from finite Decimal diagnostics.
Neither is independently reviewed by the supplied reviews, which predate this
lift. Conditional return is not full-box causal-chain closure.

After review, adjudicate only the demonstrated increments: reference-stage
consumer validity (DB-02/03/04/08), enabled discrimination (DB-07), exact
symmetry/represented decisions (DB-10), role-local history/entry (DB-15/16),
and actual enabled restoration (DB-19). DB-20 formation, DB-23 native
execution, DB-24 source readmission and DB-26 other-family scope remain
separate. Do not change the first acceptance's zero-channel domain in place.

The accepted positive scaling ray does not automatically lift: gamma J^2 and
the quadratic structural geometry break resource homogeneity at fixed
parameters. New A_OS evidence does not cover A_CI/A_PC/A_CI_PC/A_RG2b or any
C family. Native lifecycle, source readmission, topology-only proposal/paper/
specification and 7T implementation remain later propagation work.
