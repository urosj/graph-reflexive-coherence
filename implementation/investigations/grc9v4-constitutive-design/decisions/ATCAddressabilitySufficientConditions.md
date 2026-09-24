> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# Beyond the root-tuned witness: sufficient structure for addressable support

**Status:** independent mathematical review PASS, with precision amendments
applied; uniform non-root family certificate and affine exclusion also PASS.
This is a conditional research result, not accepted claim authority, native
conformance or generic fission closure. The reviewed fixture remains unchanged.

The [independent review](./ATCSupportLocalResearch.md#research-review-disposition)
closes the bounded research realization and causal questions and recommends
moving outward rather than repeating their F/D/N experiment. This note separates
conditions on source participation, the fixed fission map and target response.
The sufficient criterion below does **not** assume the old polynomial roots.
The subsequent [theorem review](#6-review-disposition-and-remaining-work) finds
no mathematical blocker and does not reopen the bounded N-R/C-R results.

## 1. Fixed graph and reduced constitutive class

Keep unit measure, identity Hodge, all-one W, zero context, no carrier and no
conductance/geometry/readback feedback. Let p = V' be continuously differentiable
on an open interval containing a compact interval J that covers the source
points and the target intervals specified below. For eta > 0,
kappa >= 0 and exact arithmetic, the ordinary law is

$$
f(C)=-\eta L[p(C)-\kappa LC],\qquad C^+=C+h f(C),\quad h>0.
$$

Use the three-node source path (a,b,c) with C- = (r,2x,r), where x > r > 0.
The same conservative binary map gives target order (a,c,v0,v1) with
C0 = (r,r,x,x), and edges a--v0--v1--c. Source and target charge is 2(r+x).
The theorem concerns this degree-two template and its ordinary continuation,
not higher-degree partition selection or composition with other event laws.

### Source participation and fixed endowment

The two inward source currents have magnitude

$$
j_s=\eta[3\kappa(2x-r)+p(r)-p(2x)].
$$

Require j_s > 0. The symmetric two-current allocation is one-half to each
child, whose resource x exceeds its exterior neighbor r. Thus the exact-law
version of F2's participation/endowment conditions holds at the sole degree-two
source vertex. For a concrete binary64 implementation its represented current
and funding guards must additionally pass; this theorem is not a substitute
for those numerical domain checks.

At the target, the exterior inflow magnitude is

$$
j_t=\eta[2\kappa(x-r)+p(r)-p(x)].
$$

It need not equal j_s, and the hypotheses below do not require it to be
positive. Positive operational response and return are not the same property
as instantaneous resource gain. The old ratio j_t/j_s = 1/6 belongs to its
particular potential/operating point, not to this sufficient-condition theorem.
In the notation of the equilibrium condition below,

$$
j_t=-\eta g(0).
$$

Its sign therefore indicates the initial state's side of the symmetric
equilibrium condition, not whether the return theorem applies.

## 2. Target hypotheses

Choose compact closed intervals I_o, I_c contained in (0,infinity), with r and
x in their respective interiors. Let B = I_o squared times I_c squared and
choose J to contain I_o union I_c union {2x}. Suppose throughout these intervals

$$
m_o\le p'(c)\le M\quad(c\in I_o),\qquad
m_c\le p'(c)\le M\quad(c\in I_c),
$$

and define mu = min(m_o,m_c) - 4 kappa > 0. This uses the conservative bound
0 <= L <= 4I for the target path. Its energy

$$
E(C)=\sum_i V(C_i)-\frac{\kappa}{2}C^\top LC
$$

has mu I <= Hess E <= M I throughout B.

### Equilibrium and clearance

Find a bracket [t_-,t_+] wholly inside B's symmetric charge plane, such that

$$
g(t)=p(x+t)-p(r-t)-2\kappa(x-r+2t),\qquad
g(t_-)<0<g(t_+).
$$

Its derivative is at least m_o+m_c-4 kappa > 0, so there is exactly one root
in that bracket. C* = (r-t*,r-t*,x+t*,x+t*) is stationary on the entire
charge plane: its energy gradient is constant across all four vertices.
Strong convexity gives uniqueness in B on that plane, not merely on the
symmetric line. Let d_* be a certified positive Euclidean boundary clearance:

$$
0<d_*\le\operatorname{dist}_2(C^*,\partial B).
$$

For the charge-tangent space $T=\{u:\mathbf1^\top u=0\}$, let
$P_T=I-\mathbf1\mathbf1^\top/4$ and $g_0=g(0)$.
The initial projected gradient is explicitly

$$
P_T\nabla E(C_0)=\frac12(-g_0,-g_0,g_0,g_0),\qquad
\|P_T\nabla E(C_0)\|^2=g_0^2.
$$

Strong convexity on that plane therefore gives

$$
E(C_0)-E(C^*)\le e_0:=\frac{g(0)^2}{2\mu},\qquad
\|C_0-C^*\|\le r_0:=\frac{|g(0)|}{\mu}.
$$

These are convenient sufficient bounds, not the only possible certificates.

### Finite-step trapping and one encounter

Choose R > 0, load bound D and h such that

$$
4h\eta M<2,\qquad (1+4h\eta M)R<d_*,
$$

$$
r_0+D<d_*,\qquad
e_0+M r_0 D+\frac{M}{2}D^2<\frac{\mu R^2}{2}.
$$

For epsilon > 0 and the two child loads w0 = (1,0,-2,1), w1 = (0,1,1,-2),
independently signed amplitudes |a|,|b| <= epsilon satisfy

$$
\|a w_0+b w_1\|^2=6a^2-8ab+6b^2\le20\epsilon^2.
$$

The maximum is attained at opposite-sign corners. Thus D = sqrt(20) epsilon,
or a larger rational bound such as 5 epsilon, suffices. The loads preserve
charge and alter no potential, reference, W or hidden history.

## 3. Consequences and proof

Within B on the charge plane, the sublevel E-E* <= mu R squared/2 has distance
at most R from C*. Because L annihilates the constant equilibrium gradient, the next
Euler displacement is at most 4h eta M R. The clearance inequality keeps the
step segment inside B before the energy estimate is applied. Taylor's theorem
then gives

$$
E(C^+)-E(C)\le-h\eta(1-2h\eta M)\nabla E^\top L\nabla E.
$$

This closes the trapping induction, rather than assuming the next state is
already in the box. The path's charge-tangent spectral gap exceeds 1/2, and
strong convexity gives

$$
\nabla E^\top L\nabla E
\ge\lambda_2(L)\|P_T\nabla E\|^2
\ge2\lambda_2(L)\mu(E-E^*)\ge\mu(E-E^*).
$$

Consequently the geometric energy contraction is bounded by

$$
q=1-h\eta\mu(1-2h\eta M),\qquad 0<q<1.
$$

At any age of the unencountered trajectory, the energy excess is at most e0
and the distance is at most r0. The loaded state and load segment remain in B
by r0+D < d_*. For the load d = a w0 + b w1, charge preservation and the
constant equilibrium gradient give the crucial cancellation

$$
\mathbf1^\top d=0,\qquad \nabla E(C^*)=\alpha\mathbf1,
\qquad \nabla E(C^*)^\top d=0.
$$

Thus, before applying Taylor's theorem,

$$
|\nabla E(C)^\top d|
=|[\nabla E(C)-\nabla E(C^*)]^\top d|
\le M\|C-C^*\|\|d\|\le M r_0D.
$$

Taylor's theorem on this segment now bounds the loaded energy excess by
e0+M r0 D+M D squared/2. It is therefore inside the trapping
sublevel and returns to C*. This is a theorem for **one encounter at any
unencountered age**, including joint signed loads, not arbitrary repeated use.

### Individually addressable operations

For child i, w_i = -L e_i. Define the average derivative on each loaded
coordinate segment by

$$
D_j=\int_0^1 p'(C_j+s\epsilon w_{i,j})\,ds.
$$

When w_{i,j} is nonzero this is the secant slope; when it is zero the integral
is p'(C_j). In either case
p(C_j+epsilon w_{i,j})-p(C_j) = epsilon w_{i,j} D_j.
Exact subtraction of the unchallenged field yields

$$
Q_i(C;\epsilon)=\frac{h}{2\epsilon}
[f_i(C+\epsilon w_i)-f_i(C)]
=\frac{h\eta}{2}(4D_i+D_{n_o}+D_{n_c}-19\kappa).
$$

The coefficient 19 is (L cubed)_ii for either interior child. Hence

$$
Q_i\ge\frac{h\eta}{2}(5m_c+m_o-19\kappa)>0.
$$

The final positivity follows already from mu > 0: both m_o and m_c exceed
4 kappa, so 5m_c+m_o-19 kappa > 5 kappa >= 0, including strict positivity
when kappa = 0. **Positive individual restorative response is a consequence
of target strong convexity and this load geometry, not an independent physical
discriminator.** Both child operations stay available along the unencountered
trajectory and their separate loads return.
The load Gram matrix is [[6,-4],[-4,6]], with determinant 20: the perturbations
are distinct and linearly independent, while their response channels need not
have unequal values or be dynamically independent. Both projected source loads
can also be linearly independent; this is not a claim that the source had only
one possible input or that all source response sites are replaced by two.
It identifies two **child-centered output/operation sites** descended from the
selected parent-centered site. Positive separate responses plus joint return
do not prove uncoupled positive intake under every joint load. Here
"addressable" means restorative response at two distinct child loci under the
specified Laplacian-local deficit loads, not controllability or the appearance
of two arbitrary functional operations.

Together, source participation/endowment, the fixed map, and these local target
conditions imply two child-centered restorative operations in this stated
sense. They do not imply
greater aggregate response, a causal effect for every comparison observable,
independent child identities, fission necessity or a general F2 law derivation.

## 4. Uniform family that does not retain the exact operating roots

The [exact check](../scripts/certify_atc_addressability_conditions.py) applies
the criterion to

$$
p_\lambda(c)=p_0(c)+\lambda c,\qquad |\lambda|\le1/8192,
$$

where p0 is the original polynomial, with the same r=1, x=3/2, kappa=1/1024,
eta=1/4, h=1/64, epsilon=1/4096, boxes and equilibrium bracket. This family was
chosen as a small strict-margin perturbation for an analytical test, not as a
replacement for the preregistered experiment or a target-selection filter.

Exact Bernstein bounds on p0' and affine dependence on lambda cover the
**entire interval**, not a collection of trajectory samples. The
[retained certificate](../evidence/autonomous-topology-change/ATCAddressabilityConditions.json)
verifies all inequalities uniformly, including

$$
j_s\ge23/16384>0,\quad
\mu=105221/1048576>0,\quad
Q_i\ge360111/268435456>0.
$$

It retains exact equilibrium signs, energy margins, load bounds and contraction
factor. For every nonzero lambda, p_lambda(1), p_lambda(3/2) and p_lambda(3)
are nonzero. Therefore the construction does not require those operating
levels to be exact site-potential roots. The original reviewed
existence witness is one member of a uniformly certified mathematical family.
No new polynomial was substituted into its content-addressed binding or run.

More generally, the criterion's strict margins persist under sufficiently
small C1 perturbations of p on the compact interval J containing
I_o union I_c union {2x}, hence also the coordinate values of the fixed
equilibrium bracket. Source participation, derivative and bracket bounds,
equilibrium clearance and the energy/load inequalities vary continuously with
p and p' on this fixed domain. This establishes local robustness of these sufficient
conditions, not robustness to unrestricted parameter changes or nonzero
history/geometry feedback. The family certificate is exact-arithmetic evidence;
its members have no new binary64 execution certificate or runtime identity.

## 5. Necessary slope softening and affine exclusion

Source participation gives a necessary shape constraint for this sufficient
route:

$$
j_s>0\quad\Longrightarrow\quad
\frac{p(2x)-p(r)}{2x-r}<3\kappa.
$$

Because p is continuously differentiable on an interval containing [r,2x],
the mean-value theorem implies

$$
\exists\xi\in(r,2x):\quad p'(\xi)<3\kappa.
$$

But the target hypotheses require p'(c) > 4 kappa throughout I_o and I_c.
Thus the softer point lies outside those stable operating intervals:
**stiff target neighborhoods must coexist with a softer source-route slope**.
For kappa = 0 the contrast is positive slopes on the target intervals versus
a negative secant average, and therefore a negative derivative somewhere on
the source interval. This is necessary for the stated participation-plus-
convex-return route; slope softening alone is not sufficient for return or
addressability. It explains a role for the multiwell-like shape without
requiring particular zeros, a specific number of wells or universal fission.

For affine p(c)=a c+b, inward source participation demands a<3 kappa. Strong
convexity of the target energy on its charge plane would demand
a>(2+sqrt(2)) kappa, since that is its largest Laplacian eigenvalue. These cannot
both hold (also impossible at kappa=0). The incompatibility survives replacing
the theorem's conservative spectral bound 4 by the exact value 2+sqrt(2) > 3;
it is not an artifact of that conservative estimate. Thus a globally affine
site derivative cannot satisfy this participation-plus-convex-return route. This is an
exclusion for this sufficient structure, not a no-go theorem for every notion
of support, topology law or other V4 constitutive channel.

## 6. Review disposition and remaining work

The supplied independent review reports rederiving the currents, equilibrium,
convexity/trapping and encounter bounds, response coefficient and affine
exclusion. It also reconstructs the Bernstein coefficients directly from the
monomial polynomial, reproduces the retained exact rational bounds and verifies
the certificate digest. Its dispositions are PASS for the conditional theorem,
uniform non-root family certificate and affine exclusion, with no mathematical
blocker. The compact-domain, projected-gradient, charge-cancellation and secant
definitions above apply its proof-presentation amendments; the current/equilibrium
identity, operational interpretation and slope-softening corollary apply its
additional scientific clarifications.

The certificate and its checker remain unchanged. Its
`proposed_conditional_theorem_not_universal_or_admitted` field records the
pre-review evidence state; this note records the subsequent mathematical PASS,
not admission into the accepted claim graph. N-R/C-R remain closed and N-P/C-P
remain deferred. No new execution law or runtime scope is implied.

Next, map bounded claim/debt successors and use the stiff-target/soft-source
constraint to investigate how the conditions transform with nonzero
geometry/history feedback or higher-degree partitions. Those extensions,
all-ten-family and autonomous runtime obligations remain open. Do not repeat
the fixed F/D/N campaign or another old-polynomial fixture to substitute for
these distinct questions.

The user subsequently chose graph/partition dependence first. The separate
[double-star continuation](./ATCPartitionDependentStability.md) derives the
exact affine restorative-curvature boundary for supplied binary star partitions
with unit old edges and child bridge:
singleton blocks retain the exclusion, while two blocks of size at least two
permit an affine window for kappa > 0. It also certifies positive-resource
encounter return for the smallest 2+2 case, with a separate Euler step bound.
Independent mathematical review of that continuation now passes, with class-count
and scope corrections and added exact partition pressure. It does not revise
this degree-two theorem or widen CAN-F2.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_addressability_conditions.py
```
