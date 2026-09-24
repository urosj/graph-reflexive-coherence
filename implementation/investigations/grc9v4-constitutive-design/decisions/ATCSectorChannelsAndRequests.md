> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# CAN-LSF G5–G6 — active A channels, potential class and request domain

**Status: bounded mathematical results, pending independent review.**
The [accepted G1–G4 research](./ATCSectorStateDomainAdjudication.md), its
certificate and all four earlier adjudications remain unchanged. This is a
successor research result, not a revision of their accepted parameter scope.
The [exact checker](../scripts/certify_atc_sector_channels.py) emits the
[G5–G6 certificate](../evidence/autonomous-topology-change/ATCSectorChannelsAndRequestsCertificate.json).
The separate [native-readiness probe](../scripts/probe_atc_sector_channels_native.py)
and [record](../evidence/autonomous-topology-change/ATCSectorChannelsNativeReadiness.json)
exercise existing primitives only. **G7, native ATC and aggregate ATC-2 remain open.**

## 1. Result and exact scope

G5 activates both remaining A conductance channels and replaces the single
affine site law by a small, genuinely nonlinear potential class. G6 then
extends the request step while keeping the physical writer time constant
fixed. Both retain the original positive feedback box, source-stage chooser,
two equal-cardinality sectors, dyadic allocation, surgery and old-edge history
transport. There is no target selection or fitted sector tolerance.

| Quantity | G5 | G6 |
| --- | --- | --- |
| alpha, beta | Each in [1/4096, 1/2048] | Same |
| chi_A, gamma, kappa_H, kappa_Ah | Original [1/32,1/16] × [1/2048,1/1024] × [1/2,1]² | Same |
| Common site law | C¹ on [0,9], derivative within 1/2048 of 19/4 | Same |
| Requested h | 1/8 | Every request in [3/25,1/8] |
| Fixed tau_A | 1/(8 log 2) | Same, not h/log 2 |
| Paired-source failure horizon | At most 56 further proposals | At most 67 |
| Embedded-source failure horizon | At most 7 further proposals | At most 10 |
| Paired target resource factor | Less than 9/10 | Less than 9/10 |
| Whole embedded target resource factor | Less than 49/50 | Less than 49/50 |
| Target history limit | exp(-alpha c) | exp(-alpha c) |

The horizons apply to the unsplit and history-reset-to-one-only controls;
they are **upper bounds**, not identical failure steps for every state.
The target estimates cover arbitrary mean-zero perturbations inside their
declared balls, not just paired modes. Source/event domains retain exact
pairing. This is neither arbitrary-state nor arbitrary-environment closure.
Formation into these domains and indefinite repeated fission remain separate.

The fixed constitutive parameters and site law may be chosen anywhere in the
declared class. G6 estimates are uniform even for a sequence of requested h
values in the interval, with the same fixed tau and other parameters. This is
**not** invariance under subdivision, a zero-step limit, an arbitrary request
policy, or an authorization to change constitutive parameters each beat.

## 2. Bind the descriptor instead of hiding it in beta

Use the existing Candidate-A host-frame reference-weighted gradient formula
in one dimension, with unit reference edge weights and regularization one:

$$
D_i(C)=\frac{\sum_{j\sim i}(r_j-r_i)(C_j-C_i)}
                 {1+\sum_{j\sim i}(r_j-r_i)^2}.
$$

These are fixed physical reference positions, not functions of resource,
history, trial outcome or stable IDs. In the vertex orders of
[G1–G4](./ATCSectorStateDomain.md), bind:

| Graph | Host positions |
| --- | --- |
| Paired source | (1,1,1,1,0) |
| Paired target | (1,1,1,1,0,0) |
| Embedded source | (1,1,1,1,0,2,2) |
| Embedded target | (1,1,1,1,0,0,2,2) |

Both children inherit the parent's position; external vertices keep theirs.
The bridge has zero host displacement but positive graph/reference weight.
Positive regularization makes the differential recipe well-defined even with
coincident positions. This is an explicit **proposed research reference and
transfer binding**; the old zero-beta theorem did not need it, and no new
native topology/reference policy is implicitly admitted here.

The exact descriptor matrices annihilate constants. Every edge-row contrast
has squared Euclidean norm at most four; hence for C=c1+z,

$$
|D_u(C)-D_v(C)|\le2\|z\|_2.
$$

The checker verifies these matrices and their covariance under decorated pair
swaps, including the corresponding external vertices. More generally, WLS
commutes with vertex relabeling that transports these reference decorations;
edge orientation does not change the WLS normal equations. G3's decorated-orbit
argument therefore still applies. This does not authorize arbitrary orbit
sizes or pooling unequal microscopic descriptors.

The conductance law now actually used in the reference/fresh reads and writer is

$$
G_e(C,D,b)=\max\left\{\frac12,
 \exp\left[-\alpha\frac{C_u+C_v}{2}
           -\frac\beta2(D_u-D_v)^2-\frac\gamma2 b_e^2\right]\right\}.
$$

Read uses that stage's baseline b; the writer uses the **selected fresh current**
and **post-resource** C and rebuilt D(C). Writer histories never feed back into
the current of the same beat. Both new channels have strictly positive
exponents at the paired event domain's reference read, and on every embedded
source reference edge, including the environment. They are not merely nonzero
parameter labels. Beta naturally vanishes at the uniform target equilibrium;
we do not claim that every channel stays nonzero forever.

An exact stage-pressure example distinguishes old descriptor contrast squared
196/625 from post-state contrast squared 1849/5625 for charge-preserving
resources. It rejects substitution of source descriptors for the writer's
post-state descriptors; it is an operand test, not an additional trajectory.

## 3. Potential class and source obstruction

Put a0=19/4, K=1/2048 and choose one common fixed law

$$
p\in C^1([0,9]),\qquad |p'(c)-a_0|\le K.
$$

An arbitrary additive constant cancels from all edge differences. With
g(c)=p(c)-a0 c, the mean-value bound gives

$$
|g(c_i)-g(c_j)|\le K|c_i-c_j|.
$$

This includes the genuinely nonlinear subclass

$$
p(c)=a c+\frac\nu2c^2,\quad
|a-a_0|\le1/4096,\quad \nu\in[1/131072,1/65536],
$$

because 1/4096+9/65536 < K. The theorem does not require p'' or assume this
quadratic subclass is the entire class. All feasible resource values lie in
[0,9], so no extrapolation of the slope bound is used.

The reference baseline remains

$$
b_0=\operatorname{diag}(W)B^T[p(C)-L_W C],\quad
L_W=B\operatorname{diag}(W)B^T.
$$

This sign and nonzero site law are research authority, not the production
zero-derivative potential under a new name. The staged geometry and fresh
read are exactly the earlier full A_OS research map.

### Paired cone and event domain

Use m=24/25 and r=1/783. On the G2 cone O (charge nine, paired nonnegative
resources, x>=3 and u,v in [m,1]), WLS gives

$$
D_{u}-D_s=3x/10+y/2,\qquad D_v-D_s=3x/10-y/2.
$$

Their absolute values are at most 27/10. Resource means are at most 9/2.
The new potential changes each old baseline by at most 9K. The old sharper
bound 2697/500 plus 9K remains below B0=11/2. With

$$
\delta=(225/2)(rB_0)^2,\qquad
\epsilon=\delta+r(B_0+\delta),\qquad
J_*=(1+r)(B_0+\delta),
$$

every required source read/writer exponent is bounded by

$$
E_* = \alpha_{max}\frac92+
       \frac{\beta_{max}}2\left(\frac{27}{10}\right)^2+
       \frac{J_*^2}{2048}<1-m.
$$

Thus all conductance targets exceed m and the floor is inactive. For the
writer, use the actual admitted post-resource state: if it remains
nonnegative it has the same charge and paired cone bounds. Log interpolation
then preserves W in [m,1]. The reference/fresh read contrast remains bounded
by r and the OS residual by 4[(rB0)²+(r(B0+delta))²]<1/512.

The old baseline sum loses at most 18K, or 6Kx since x>=3. Hence

$$
x^+\ge\left[1+\frac52 h_{min}
  \left(\frac{19}{250}-6K-\frac{2\epsilon}{3}\right)\right]x.
$$

The growth margin exceeds 1/50 at h=1/8 and 1/60 on G6. Nonnegative resources
require x<=9; 3(51/50)^56>9 and 3(61/60)^67>9. This proves uniform source
obstruction, including the history-reset-only control, not just a bare
spectral warning. Earlier rejection by a stricter resource chart is allowed.

Define E_p using G1's x,y,u,v ranges and **balance of the actual p-baselines**:
b_u^p,b_v^p>0 and |b_u^p-b_v^p|<=(b_u^p+b_v^p)/64. Do not silently reuse
balance of the affine surrogate. The common strict interior witness
(13/4,1/100,97/100,99/100) satisfies these inequalities for every admitted p,
even with the conservative 9K per-current error. Thus E_p remains nonempty
and full-dimensional in the paired quotient. It lies in O.

The independent reset domain B is unchanged: x in [3,7/2], |y|<=1/50 and
u,v independently in [m,1], with the same charge/pairing, no current-balance
or history-order condition. The chooser still uses only current's selected
**reference** current. All rounded outcomes remain in [31/64,33/64] and both
roles retain funding at least 1303/1600. This encloses the prescribed result;
it does not give a set of targets from which to choose.

On E_p, edge resource mean is at least 269/100 and descriptor contrast
absolute value at least 89/100. Therefore alpha and beta contribute strictly
positive reference-stage exponent terms throughout the event domain.

## 4. Target entry and return with a shifted history limit

On either target write X=||C-c1||. Full mean-zero rational positive-pivot
certificates bound the **unweighted** nonzero Laplacian spectrum by
[7/16,73/16] for the six-vertex paired target and [3/10,47/10] for the entire
eight-vertex embedded target. Multiplying the lower bounds by m and leaving
upper bounds unchanged covers every history vector in [m,1].

Relative to the affine bare polynomial P_h(L)=I+hL(L-a0 I), the potential
remainder has current norm at most (5/2)K X. Set

$$
B_{eff}=4+(5/2)K,\qquad
\delta(X)=\frac{125}{8}X(rB_{eff}X)^2.
$$

Here ||B||<=5/2 and the affine baseline norm is at most 4X. The complete
potential/geometry/fresh-read resource error is bounded by

$$
E_C(X)=h_{max}\frac52\left[(5/2)KX+
          \delta(X)+r(B_{eff}X+\delta(X))\right].
$$

For paired entry, reuse G1's exact t,y,e polynomial expansions. For every
h in [hmin,hmax], bound each leaf and parent respectively by

$$
\begin{aligned}
L_*&=(1-3h_{min}7/4)(2/5)+(1-h_{min}7/4)(1/50)+h_{max}(23/320)/4,\\
P_*&=[2-6h_{min}(7/4-1/25)](2/5)
       +h_{max}(1/50)/2+(1-h_{min})(23/320).
\end{aligned}
$$

The resulting squared norm 4L_*²+2P_*² is below (3/5)² for G5 and (5/8)²
for G6. Adding E_C(3/2) gives X+ <0.60340 and <0.62840 respectively, both
strictly below 2/3. Reads and the rebuilt post-resource writer have exponent
budget at most alpha_max(c+X)+2 beta_max X²+J_*²/2048 <1-m. Residual is below
1/512; both independently transported roles enter the return domain.

For a return radius R and weighted spectral interval [l,u], use

$$
q_0=\max\{1+h_{min}l(l-a_0),1+h_{min}u(u-a_0)\},
$$

$$
q=q_0+h_{max}\frac52\left[(5/2)K+
       \frac{125}{8}(rB_{eff}R)^2+
       r\left(B_{eff}+\frac{125}{8}(rB_{eff}R)^2\right)\right].
$$

The polynomial multipliers stay positive, since 1-hmax a0²/4>0; convexity
places their maximum at an endpoint. Exact bounds give:

| Domain | G5 upper bound (rounded upward here) | G6 upper bound (rounded upward here) | Uniform conclusion |
| --- | --- | --- | --- |
| Paired, c=3/2, R=2/3 | 0.895102 | 0.899379 | X+ <= (9/10)X, resources >5/6 |
| Embedded, c=41/40, R=1/4 | 0.972612 | 0.973787 | X+ <= (49/50)X, resources >31/40 |

Resource floors are strict after the first positive-duration return step;
on the closed entry balls the non-strict lower bounds suffice for admission.
The same exponent and residual checks keep W in [m,1] and every OS step
admitted. These are resource contraction estimates, **not a claimed joint
(C,W) contraction**.

At C=c1, descriptors and all currents vanish, but G=e^(-alpha c), not one.
Put e_n=log W_n+alpha c. With rho_n=exp(-h_n/tau_A), the writer satisfies

$$
e_{n+1}=\rho_n e_n-(1-\rho_n)\left[
 \alpha(\bar C_{e,n+1}-c)
 +\frac\beta2(D_u(C_{n+1})-D_v(C_{n+1}))^2
 +\frac\gamma2J_{fresh,e,n}^2\right].
$$

The bracket tends to zero as resources contract. With fixed tau_A=1/(8 log 2),
G6 has 0<rho_n<=25/37<1 (use log 2>1/2 and exp(t)>=1+t). The stable scalar
recursion implies e_n→0 and W_n→exp(-alpha c), inside [m,1]. This proof works
for any request sequence in G6's interval. Replacing rho by 1/2 when h changes
would not be this law.

## 5. Active embedding: finite source enclosure and whole-target return

Keep exactly G4's seven-/eight-vertex graphs and source/reset box with
epsilon=1/10000 and charge 41/5. Current still requires r_u>=r_v; independent
actual reset does not. The certificate encloses the larger box, without
filtering trajectories by eventual target success.

With d=(r_u-s,r_v-s,r_u-z), the four distinct descriptors are

$$
D_u=(d_u-d_e)/3,\quad D_v=d_v/2,\quad
D_s=2(d_u+d_v)/5,\quad D_z=-d_e/2.
$$

Exact basis checks identify these with the full WLS matrix. For each edge
type add an interval remainder w_e[-K|d_e|,K|d_e|] to the affine baseline.
This forgets correlations of the common p, conservatively including every
fixed law in the class; it does not authorize a different physical p per edge
or beat. Use the unchanged generated star, fresh read and reduced continuity
equations. Evaluate I+h Q_W(Q_W-a0 I), grouping h to limit interval wrapping.

Selected source inflows and external reference current remain strictly
positive. All alpha/beta source exponent intervals have positive lower
endpoints. The current-selected dyadic share is universally enclosed by
[15/32,17/32], slightly wider than G4's **output enclosure**, not a change to
the allocator or its allowed choices. Both-role funding remains positive and
direct target entry has X²<1/16. The whole-target theorem above then includes
the environment for both roles.

For the unsplit controls, all intervals are outward-rounded on the unchanged
256-bit grid. If a proposal is uniformly resource-negative, reject it and do
not evaluate a writer. When wrapping includes both positive and negative
possibilities, propagate only an **enclosure of possible nonnegative survivors**:
intersect each resource coordinate with [0,41/5], then intersect the independently
computed d+ with its exact differences (C0-C4,C2-C4,C0-C5). Actual survivors
must satisfy both descriptions. Disjoint intervals prove that none survive.

This intersection is a proof operation, **not resource clamping, a physical
repair, acceptance of a rejected beat or selection by target outcome**. Failed
trajectories stop at their first rejection. The writer for surviving members
uses the full WLS map of post-resource C, fresh J and the true rho(h).
Interval independence only enlarges this survivor enclosure.

Every unsplit and reset-to-one-only trajectory rejects by attempt seven for
G5 and by attempt ten for G6, with OS residuals still below 1/512 on the
enclosed attempted states. G6's terminal certificate is an empty intersection
of exact resource descriptions, not a claim that its displayed minimum
interval is uniformly negative. The retained rows distinguish full admission,
conditional survivor propagation and terminal rejection. No finite failure
horizon is extrapolated into a target theorem; infinite target continuation
comes from §4.

The excluded second-parent environment remains excluded. Its untouched target
mode has weighted Rayleigh lower bound m(26/5)>a0+K. At the shifted uniform
equilibrium the resource linearization therefore has an expanding mode.
Dependence on W vanishes in that resource linearization at uniform C; alpha
adds C-to-W forcing but cannot remove the unstable diagonal resource block.
Read-Back/geometry terms are higher order there. This remains a counterexample
to an arbitrary-environment return claim, not a claim that every trajectory fails.

## 6. Reproduction and G7 boundary

From the repository root:

```sh
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_sector_channels.py
PYTHONPATH=src .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/probe_atc_sector_channels_native.py
```

Both commands print records without modifying files. The mathematical checker
verifies the exact accepted G1–G4 adjudication and its bound sources, preserves
the prior interval kernels, and binds its own note/script. All retained paths
are repository-relative. Log uses an outward rational 96-term atanh series
with a proven tail bound; exp and square root use the unchanged reviewed
kernel. Rational log/exp probes and the h-dependent decay check run alongside
descriptor identities, full-space spectral pivots and the domain proofs.
The JSON retains exact inequalities and endpoint witnesses, not just decimal
success summaries.

The native probe compares all four graph descriptors to independent exact
rational normal equations and two log-writer requests to an outward interval
oracle, with unique binary64 rounding. It pins actual binary64 inputs,
including tau; that represented tau is **not** identified with the exact
transcendental theorem parameter. The near-lower-endpoint request uses the next
float above 3/25, because binary64 `0.12` lies just below the theorem interval.
These are primitive comparisons, not event/lifecycle or profile admission.

Source inspection confirms `CandidateACurrent` still rejects any site potential
ID other than `quadratic_site_potential_zero_derivative_v1`; its current does
not implement this nonzero p. That boundary is explicitly recorded as static
inspection, not fabricated runtime rejection evidence. An existing A_OS G2
support declaration cannot supply this missing ATC potential/profile authority.

Accordingly G7 cannot be completed by calling the research checker a native
run. Its remaining work is concrete:

1. Independently review G5–G6 and adjudicate their bounded claims/debts, without
   changing accepted predecessor scope or declaring aggregate ATC-2 closed.
2. Propagate reviewed topology authority through the topology proposal,
   separate extension paper and specification before production changes.
3. Admit revision-distinct potential, descriptor/host transfer, mixed history,
   request and owner bindings. Preserve existing potential/profile identities.
4. Bridge exact-real bounds to represented parameters and **all staged**
   numerical errors, including current-dependent dyadic rounding.
5. Execute native source/event/current/reset, continuation, failure rollback,
   lineage and replay conformance against the independent research oracle.

No production code, runtime tests, paper, specification, graph claims or gates
are changed here. The next action is scientific review of this successor, not
another source fixture or an unreviewed substrate extension.
