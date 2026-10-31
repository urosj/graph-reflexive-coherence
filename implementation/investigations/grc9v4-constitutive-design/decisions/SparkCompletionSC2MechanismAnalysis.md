# SC-2 — Mechanism analysis before a completion witness

2026-10-31. **Scientifically reviewed conditional result, not admitted policy or
native completion.** The [independent review disposition](../evidence/spark-completion/review/SC2ScientificPressureReview.md)
passes the stated mathematics and records additional limits. Follows the
[SC-1 audit resolution](./SparkCompletionSC1EquilibriumExclusion.md).
[Ledger](../evidence/spark-completion/SC2ClaimDebtLedger.json) and
[exact checks/provenance](../evidence/spark-completion/SC2MechanismChecks.json).

## 1. Outcome and authority distinction

The inherited **site-potential channel** supplies a mathematically productive
route. A homogeneous nonlinear site potential can support locally attracting
nonconstant exact C_OS states with the proposed SC-1 spatial basins. This
replaces the imposed affine return map with an argument using the actual
baseline, Read-Back, star-source, geometry and OS continuity equations.

The channel $-V'(C_i)$ already occurs in the
[V4 specification](../../../../specs/grc-v4-spec.md), common transport and
Candidate A/C sections, and [paper](../drafts/2026-09-GRC-V4.md), §4.1.
The **particular nonlinear binding below is new and proposed**, not inferred
from the presence of a configurable identifier. The shipped A and C current
implementations admit only the declared zero-derivative site evaluator.
Nothing here installs a new evaluator or treats it as an admitted complete
profile. The side-tool traces preserve that boundary.

The route is motivated by the older [V2 site-potential discussion](../../../../papers/2025-12-GRC-V2.md),
which explicitly mentions double wells. Its stability language is not imported.
All signs and staging below are derived from V4's actual continuity and current
equations. The same potential is used at every node and is independent of node
labels, graph size and the selected pattern.

## 2. Mechanisms examined

| Possible change | Finding under the present contracts |
| --- | --- |
| Longer evolution or new positive thresholds | Cannot remove the proven zero-site tree equilibrium obstruction. |
| Larger source or extra occupied rows | Can resolve a missing parent/seed topology, but does not supply an equilibrium mechanism. |
| Add cycles | Does not remove A_CI/A_PC's positive-denominator exclusion. A general C circulation route is not established here. |
| Change K4_base | Not a permanent deformation under the admitted affine reference-relative profile; see below. |
| Leave a nonzero PC carrier at equilibrium | At zero current the quadratic source vanishes; the finite-time PC writer forces stationary Z=0. Initial Z is transient, not permanent forcing. |
| Change positive reference mobility/Hodge | Positive stiffness still forces constant resources at zero-site equilibrium in the stated excluded domains. |
| Set stiffness to zero | In the simple reference zero-site branch the C map is identity, giving neutral states rather than the required strict full-state contraction. No completion follows. |
| External exchange or a driven context | Would change the closed/constant-zero context contract and require its own authority; no such binding is selected. |
| Homogeneous nonlinear site potential | Existing equation channel; new evaluator/binding needed. Conditional stationary and local-stability result supplied below. |

**K4_base is not an additive external field.** The admitted geometry is

$$
H_1=H_{1,\rm ref}+\kappa_H\Delta K_4,\qquad
\Delta K_4=K_4-K_{4,\rm base}.
$$

At zero structural increment it is exactly the reference Hodge, regardless of
the numerical baseline. The implementation consumes the separate increment.
Thus merely changing K4_base cannot defeat the A_CI/A_PC zero-source argument.
Within this reference-relative profile, that part of the earlier exclusion does
not actually require a zero numerical baseline. The zero-source/zero-increment
premise is what matters. A profile with genuinely permanent deformation would
be a different declared geometry contract, not a new value of the anchor.

No previously admitted ATC construction is used to infer this result.

## 3. Proposed homogeneous site law

Take fixed global parameters $c_0>a>0$, $\mu>0$ and

$$
V(C)=\frac{\mu}{4}\big((C-c_0)^2-a^2\big)^2,
\qquad
V'(C)=\mu\big((C-c_0)^3-a^2(C-c_0)\big).
$$

This is a local conservative site term in the potential, not a resource source.
Ordinary continuity still preserves total charge exactly in the real equations.
The prospective design name is **SC2-homogeneous-quartic-site-proposal**;
it is deliberately not an executable evaluator ID.

For a connected finite unweighted graph let $L=BB^\top$ and first use the
declared C reference reduction: unit measures, $W_{C,\rm tr}=1$,
$H_{1,\rm ref}=I$, $\kappa_{M,C}=0$, and positive stiffness $\kappa$.
The potential is

$$
\Phi(C)=\kappa LC-V'(C).
$$

The retained-Hodge deformation switch is off in this analytic slice.
Read-Back and structural geometry gains need not be off; §5 keeps them nonzero.

Let $\sigma_i\in\{-1,+1\}$ describe a nonuniform equilibrium branch, and
$C_i^0=c_0+a\sigma_i$. Set the fixed charge $Q=\sum_iC_i^0$.
The signs specify the branch whose existence is being proved; they are **not**
a per-node field in $V$, a runtime partition chooser, or proof of event-driven
formation. Both labels and the branch transform under graph relabeling.

Write $C=C^0+y$, $E=\{y:\mathbf1^\top y=0\}$, and let
$P=I-\mathbf1\mathbf1^\top/n$. Stationarity of the reference current is
equivalent to $P\Phi=0$. Expanding the same polynomial at every node gives

$$
V'(C^0+y)=2\mu a^2y+\mu(3a\sigma\odot y^2+y^3).
$$

Therefore equilibrium is exactly the fixed-point equation on $E$

$$
y=\mathcal G(y):=
\frac{\kappa}{2\mu a^2}L(C^0+y)
-\frac{1}{2a^2}P(3a\sigma\odot y^2+y^3).
$$

This is an equilibrium proof map, **not** the physical ordinary-step update.

## 4. Quantitative existence before a trajectory

Let $\ell=\|L\|_\infty$, $b=\|LC^0\|_\infty$ and
$p=\|P\|_\infty=2(1-1/n)$. For $K_{\rm eq}=\{y\in E:\|y\|_\infty\leq r\}$,

$$
\|\mathcal G(y)\|_\infty\leq
M:=\frac{\kappa}{2\mu a^2}(b+\ell r)
+\frac{p}{2a^2}(3ar^2+r^3),
$$

$$
\operatorname{Lip}_\infty(\mathcal G|K_{\rm eq})\leq
q_{\rm eq}:=\frac{\kappa\ell}{2\mu a^2}
+\frac{p}{2a^2}(6ar+3r^2).
$$

If $r<c_0-a$, $M<r$ and $q_{\rm eq}<1$, the map preserves the exact charge
space and has a unique equilibrium in this box. This is a contraction of the
**equilibrium solver map**; physical stability is a separate argument below.

A finite check uses the existing ten-node abstract target topology, with peaks
p,x,y; private neighbors a,b / d,f / e,g; and the shared saddle m.
All nine edges join a peak to a low node. The maximum degree is 3 and diameter
4; each peak occupies all three fixed rows. Choose, before any trajectory,

$$
c_0=2,\ a=\mu=1,\ \kappa=1/64,\ r=1/8,\qquad
\sigma_{p,x,y}=+1,\quad \sigma_{\rm others}=-1.
$$

Then $Q=16$, $\ell=b=6$, $p=9/5$, and exactly

$$
M=99/1024<1/8,\qquad
r-M=29/1024,\qquad q_{\rm eq}=489/640<1.
$$

This proves a nonconstant equilibrium of the declared polynomial equations;
no rounded root or small numerical residual substitutes for existence.
It is a new scientific parameter proposal, not a reuse of an accepted profile.

Throughout this equilibrium box, high resources lie in $[23/8,25/8]$ and
low resources in $[7/8,9/8]$. Neighbor contrasts lie in $[7/4,9/4]$.
With the already proposed SC-1 diagnostic choices
$s_H=-1$, $\epsilon_g=4$, $\epsilon_H=1/4$,
$\Delta_\Psi=c_{\min}=1/2$, the strict margins are:

| Requirement | Uniform margin/bound |
| --- | --- |
| Resource positivity | minimum 7/8 |
| Gradient-square threshold | at least 13/16 |
| Signed row Hessian threshold | at least 3/2 |
| Neighbor barrier threshold | at least 5/4 |
| Spatial domains | p:{p,a,b}, x:{x,d,f}, y:{y,e,g}; m unassigned |

The margins are analytical whole-box bounds. Each low private neighbor has
only one reachable peak; m reaches all three and is not assigned. The pattern
is therefore inside the proposed geometric-basin class. This topology is
**not** claimed as a D11-G9 target of a completed source/event construction.
The exact check assigns each node's successive edge occurrences to ports
1, 4 and 7. The four degree-three nodes occupy all rows without a collision;
the six private neighbors have one occupied row and cannot become seeds.

## 5. Actual C_OS staging and full-state local stability

Keep $\tau_C=1$, $\chi_C=\zeta_C=1/2$,
$\beta=\zeta_C\chi_C=1/4$, $\eta_C=1$ and $\kappa_H=1/2$.
At reference geometry and $\kappa_{M,C}=0$,

$$
R=(I+\tau_CB^\top B)^{-1},\qquad F=I-\beta R,\qquad
A=\eta_CBF^{-1}B^\top.
$$

$F$ is positive definite for $0\leq\beta<1$; $A$ is positive definite on $E$.
An equilibrium found above has constant $\Phi$, hence baseline current zero.
Its predictor, lowered Read-Back and quadratic star source are zero, so OS
generates the reference geometry. The fresh corrector also has zero current.
Thus it is a fixed point of the **full exact C_OS pass**, not only the
equilibrium proof map. This does not equate corrector and restart off equilibrium.

At the equilibrium the derivative of the quadratic structural source is zero.
Consequently the geometry increment has zero first derivative, and the full
OS derivative on the fixed-charge state space is

$$
DT_{\rm OS}(C^*)=I-hAD,\qquad
D=\operatorname{Diag}(V''(C_i^*))-\kappa L
$$

(with restriction/projection onto $E$ understood).
C_OS has no W or persistent Z coordinate to omit. This argument does not
establish A, PC, CI or RG2b full-state stability.

Here $V''(C)=\mu(3(C-c_0)^2-a^2)$. Over the equilibrium box,

$$
(77/64)I\preceq D\preceq(179/64)I.
$$

In the $A^{-1}$ norm on $E$, $AD$ is self-adjoint and positive definite.
For a connected n-node graph of diameter d, the path inequality and
$\sum_{i<j}(u_i-u_j)^2=n\|u\|_2^2$ for mean-zero u give
$\lambda_2(L)\geq2/((n-1)d)$. Thus here
$\lambda_2(L)\geq1/18$, $\lambda_{\max}(L)\leq6$, and

$$
(1/18)I_E\preceq A|_E\preceq8I_E.
$$

For the fixed positive ordinary duration $h=1/32$,

$$
0<h\lambda_{\max}(A^{1/2}DA^{1/2})\leq179/256<1,
$$

$$
\|DT_{\rm OS}(C^*)\|_{A^{-1}}
\leq1-\frac{77}{36864}
=\frac{36787}{36864}<1.
$$

A selector cutoff $1/64$ lies strictly between the constant mode and the
proved nonconstant spectral lower bound. Near the equilibrium its gap,
positive Hodge, current regularity and any fixed positive OS split tolerance
remain valid by continuity. The exact polynomial/resolvent/star/geometry map
is smooth there. By continuity of its **full OS derivative**, a sufficiently
small closed $A^{-1}$ ball in the fixed-charge space has contraction constant
less than one and strict image margin, while retaining the basin predicates.
This supplies an existence proof of a physical trapping neighborhood.

**Limits of that statement:** the explicit box above proves equilibrium and
basin structure, not physical invariance of the whole box. No quantitative
radius or represented-error budget for the full OS trapping ball is produced
here. Gains being nonzero does not demonstrate a numerically resolved
off-equilibrium effect. The polynomial evaluator, target-domain admission,
exact/represented row agreement and charge-preserving numerical lift remain
unimplemented/unproved for native use. A spectral bound on the derivative at
one point is used only with the stated smoothness/continuity argument, not
reported as a uniform whole-box contraction certificate.

There is also a **qualitative continuation** to small nonzero retained-Hodge
gain $\kappa_{M,C}$. At zero gain, the derivative of $P\Phi$ on the charge
space is $-P D|_E$, which is invertible. On the fixed selector stratum, its
potential and operator dependence is smooth. The implicit-function theorem
therefore continues this equilibrium for sufficiently small gain; the reference
predictor remains zero, hence so does its star source and corrector. Strict
stability, positivity and basin margins persist by continuity. This proves
existence of a nearby enabled-gain interval under the same proposed site law;
it supplies **neither an endpoint nor a certified nonzero numerical point**.
The numerical values above remain claims about $\kappa_{M,C}=0$ only.

## 6. Review pressure and mechanism attribution

The independent review finds no blocking defect in the equilibrium or full exact
C_OS local-stability argument. It also identifies limits that matter for the
next construction.

**Existence does not select the organized branch.** Any three of the ten nodes
can carry the upper-well signs, at the same charge 16 and with the same global
potential. Maximum degree three gives $\|LC^0\|_\infty\leq6$ for every placement.
All 120 choices therefore satisfy the same equilibrium and local physical
stability bounds. Different centers differ by 2 in some coordinate, so their
radius-1/8 boxes are disjoint. There are **at least 120 distinct locally attracting
equilibria**, not one globally selected equilibrium. Uniqueness above is local
to the selected branch box.

For the upper-well choice $\{a,b,d\}$, the image bound improves to $83/1024$.
This branch is stable but has no qualified geometric basin throughout its box:
the upper nodes are degree-one leaves missing two rows; each lower node either
has an upper neighbor, defeating the required extremum, or has only lower
neighbors with contrasts at most $2r=1/4<\Delta_\Psi=1/2$. The local exact checker
reproduces all 120 branch bounds and this uniform no-basin control. Formation
must distinguish entry into an organized branch from entry into such alternatives.

**The equilibrium box is not a physical trap.** The independent review reports
an exact rational algebraic OS pass from

$$
C_p=C_x=C_y=23/8,\qquad C_m=C_g=7/8,\qquad
C_a=C_b=C_d=C_f=C_e=9/8
$$

at charge 16, with $0.867635028592011<C_m^+<0.867635028592012<7/8$.
This is retained as a reviewer-reported counterexample, not as a locally replayed
execution: its separate executable package was not supplied with this review.
It does not assert admission at an undeclared split tolerance. Whether the corner
exits algebraically or is rejected, the solver-box bounds alone supply no admitted
physical self-map. The independently derived smaller local-neighborhood result
is unchanged.

**The site curvature is the restoring mechanism.** On the frozen-reference slice,

$$
\mathcal E(C)=\sum_i V(C_i)-\frac{\kappa}{2}C^\top LC,
\qquad \Phi=-\nabla\mathcal E,
\qquad D=\nabla^2\mathcal E.
$$

The graph contribution has a negative sign; it is not a positive interface
penalty. No global Lyapunov property for the generated-geometry OS map follows.
Read-Back changes the mobility $A$ and linear relaxation. Generated geometry has
zero first derivative at equilibrium and enters at second order nearby. Setting
the geometry gain to zero leaves the local derivative unchanged; setting explicit
Read-Back to zero gives $A=\eta_C L$, which also satisfies strict local stability
at these parameters. The result proves compatibility with enabled feedback,
not its necessity for organization or a native resolved off-equilibrium effect.

The three spatial basins are geometric routing objects. At this equilibrium
physical current is zero, so they must not be relabeled as nonempty physical-flow
regions in the existing classifier.

## 7. What this advances, and the next bounded task

This supplies a **positive conditional stationary mechanism** in place of the
old affine toy's imposed return law. The potential is homogeneous, uses an
existing constitutive channel, and has a nonempty exact C_OS equilibrium/stability
domain with the proposed geometric basins. It does not close SC-2's
source → admitted expansion → target-entry requirement, establish local gain
relative to a real parent, or admit a completed spark.

The exact check also rejects controls with insufficient equilibrium-map
bounds, an excessive ordinary timestep, the wrong continuity/potential sign,
and attempted use of pointwise/solver bounds as a whole OS-domain certificate.
It establishes arithmetic and identities subordinate to the derivation.

The next bounded task is **source/parent/D11 target compatibility and event
reachability under the proposed global site law**, before an expensive trapping
enclosure. First fix the actual source and target topology, charge and lineage,
and test inexpensive necessary conditions. For a radius-$r$ box around a center
with $k$ upper wells among $n$ nodes,

$$
\left|Q-\big[n(c_0-a)+2ak\big]\right|\leq nr
$$

is necessary, not sufficient. The present charge-tangent proof additionally
sets $Q$ equal to the center charge; applying it at a different compatible
charge requires a revised equilibrium argument. Check target degree/spectral
bounds, row occupancy and possible descendant basins on that actual graph.
D11-created zero-resource coordinates start outside the present positive box;
they need an admitted approach trajectory, not an assertion of immediate trap
entry. Do not refit node-specific wells or declare the favorable branch selected.

Then establish entry into an organized branch and quantify a full-OS trapping
domain there, with exact-charge and diagnostic/step-error certificates before
represented completion claims. The concrete nonlinear binding still needs scoped
adjudication and authority → paper → spec propagation before native registration.
No rerun of excluded zero-site witnesses, weakening of SC-1, or automatic profile
promotion follows from this review.
