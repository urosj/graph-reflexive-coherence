> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# Critical-mode onset, contact lift and a nonrestorative refinement

Status: independently reviewed bounded mathematics, PASS. The candidate
implication “critical contact signs plus parent-only binary refinement imply
restorative autonomous fission” is **refuted in this family; stop this branch**.
ATC-2 and autonomous splitting remain open. Exact
identities and focused Decimal diagnostics are checked by the accompanying
[script](../scripts/certify_atc_critical_mode.py) and retained
[certificate](../evidence/autonomous-topology-change/ATCCriticalModeCertificate.json).
No accepted claim/debt, profile, K0 guard, production code, paper or spec changes.

The question is no longer which observable makes an attractive grouping. It is
whether the **same source instability that obstructs continuation supplies a
binary decomposition**, and whether that decomposition actually remedies it.

This investigation gives a bounded yes to the first question and a counterexample
to the second. Ordinary retained-history recovery crosses a simple critical
mode; its source-only, orientation-independent contact signs specify one
unordered 2+2 partition at a unique parent. A nonzero perturbation in that mode
eventually leaves the positive-resource domain. But the direct conservative
split along those signs **also** loses positivity: it strengthens the relevant
instability. Sign structure is therefore not by itself a mechanical fission law.

## 1. Review integration and adaptive stepping

The supplied audit gives the predecessor's
[unsplit obstruction](./ATCUnsplitViabilityAndMechanicalBoundary.md) a mathematical
PASS. It independently checked the exact bounds, energy differences, modes,
certificate/checker identities and enabled scalar trajectory. It could not run
the complete repository-dependent checker. Preserve that distinction and the
original checker/certificate bytes, including their historical pending status.

The adaptive-step strengthening needs no new trajectory. In the predecessor,
let a0=5c*=25075/21888 and x0=4. For every successful positive update of duration
h_n>0, with its actual writer rho_n=1-exp(-h_n/tau_A),

$$
x_{n+1}-x_n\ge a_0h_nx_n\ge4a_0h_n.
$$

The history interval stays invariant for every such rho_n in (0,1). Summing and
using x_N<9 gives the stronger simple bound

$$
\sum_{n<N}h_n<\frac5{4a_0}=\frac{5472}{5015}.
$$

Thus no positive **non-Zeno** schedule (sum h_n=infinity) can give indefinite
positive continuation. An infinite accepted sequence could accumulate only
finite simulated time; this theorem does not forbid such a Zeno sequence or
authorize a new step-selection policy. Termination, another chart/profile,
external exchange or another topology operation remain outside the declared
comparison. Use “obstruction to the declared unsplit continuation,” not an
unqualified necessity to fission.

## 2. Measure pressure: a possible carrier, not a conservation law

The [paper](../drafts/2026-09-GRC-V4.md#43-general-charge-and-the-current-unit-measure-profile)
and [specification](../../../../specs/grc-v4-spec.md#charge-contract) distinguish
the general charge covector from the current unit-measure population. The
reference geometry has H0_ref=Diag(mu) for positive vertex measure, while the
current runtime constructs unit vertex measure. The accepted affine geometry
update leaves H0 at its reference value. Typed unit-measure, general-charge,
Hodge-update and event-charge provenance traces are retained, with their actual
support dispositions; they do not assert a conserved-substrate fission rule.

Consequently “V4 has no measure quantity” would be incorrect. What is **not
supplied by these inspected contracts** is a law transporting an extensive
substrate measure through fission, a declaration that C is density rather than
amount, and the matching energy, differential and charge transformations.
H0's geometric role alone cannot supply those semantics. The runtime's unit
profile is a bounded implementation fact, not a universal prohibition.

If m_parent=m_1+m_2 is separately declared, an energy term b sum_i m_i cancels
under subdivision. For an extensive resource C and density energy

$$
E_{\rm local}(C,m)=\sum_i m_i u(C_i/m_i),\qquad u(c)=ac^2/2,
$$

splitting (s,1) into (s/2,1/2),(s/2,1/2) preserves the local energy a s^2/2.
The old unit-site construction instead gives a s^2/4. This changes physical
content, not merely the choice of energy zero. New Hodge/transport/history
contracts would need new target mathematics; the old return theorem cannot be
reused. If C instead denotes density, its conservative map and charge covector
must change accordingly rather than silently halving that density.

This cancels the **extensive constant**, not every possible topology term.
For example, an independently chosen site-count or interface energy remains
invisible to fixed-graph resource derivatives. The prior identifiability result
holds for its unit-site maps, but does not prove a per-birth constant is inevitable
for every measure-conservative theory. No such successor is selected here.

## 3. A source graph with a simple contact-resolving mode

Use five vertices (u1,u2,u3,u4,v). Join v once to every ui; join every member
of {u1,u2} to every member of {u3,u4} with **two parallel edges**. There are
twelve edges, all with unit reference mobility and Hodge pairing. Parallel edges
are distinct incidences, not weights silently added to an old graph. The two
leaf classes are encoded in this source graph, not chosen by target outcomes.

For L=B B^T the complete mutually orthogonal eigenbasis is:

| Mode | Laplacian eigenvalue |
| --- | --- |
| (1,1,1,1,1) | 0 |
| (-1,-1,-1,-1,4) | 5 |
| (1,-1,0,0,0) | 5 |
| (0,0,1,-1,0) | 5 |
| phi=(1,1,-1,-1,0) | 9, simple |

This is a **new research fixture and potential**, not the earlier four-edge
star or its p(c)=19c/4 law. Here p(c)=a c, a=15/2, eta=kappa_c=zeta_A=1,
alpha=beta=0, no carrier, unit reference pairings, the same identity normalized
star adapter, h=1/32 and tau_A=h/log(2). These coefficients are declared before
any target calculation; no universal bifurcation result follows.

Initially every edge has W=3/4. In the zero-read control gamma=chi_A=0,
the exact writer is log W^+=(log W)/2, hence

$$
w_n=(3/4)^{2^{-n}}\nearrow1.
$$

This is evolving authoritative history, not an external parameter ramp or
counter-based trigger. The n notation describes the solution only. Structural
geometry is reference in this control; no nonzero feedback claim is made for
its finite-amplitude trajectory.

## 4. Onset from the complete ordinary-step derivative

At homogeneous resources C=R1 with R=9/5, the current is zero and the source
remains homogeneous while W recovers. For this background, allow additionally
0<=gamma<=2^-16, 0<=chi_A<=1/2 and 0<=kappa_H,kappa_Ah<=1.
At each background read q=tanh(log(w)/2), S0=0. Its first variation vanishes
because structural assembly is quadratic in the zero background current.
The pre-read's current-squared term and retained writer drive likewise have
zero first variation. History perturbations alone cannot drive resources from
the homogeneous state. Thus the **full resource/history step Jacobian** is
block diagonal: a resource block and a history block (1/2)I, with resource
generator and modal multipliers

$$
A_C(w)=\frac{wL(wL-aI)}{1-\chi_A\tanh(\log(w)/2)},\qquad
m_\lambda(w)=1+h\frac{w\lambda(w\lambda-a)}{1-\chi_A\tanh(\log(w)/2)}.
$$

This is a derivative of the fresh ordinary A_OS step, not a replacement of
K0's reference-current witness. Geometry gains can be enabled, but their
linearized contribution here is zero; this is not evidence of strong nonlinear
geometry feedback on a perturbed trajectory.

The simple critical surface is w*=a/9=5/6. The scalar growth rate crosses
zero transversely as history recovers. At chi_A=0 its derivative with respect
to w at w* is 9a>0; the positive read denominator preserves that sign.
Equivalently the step multiplier crosses +1, not zero. There is no claim that
the discrete source lands exactly on the continuous state surface. This is a
local multiplier crossing along a nonstationary recovering background, not an
equilibrium bifurcation theorem or a claim that frozen spectra alone determine
all nonautonomous stability. The exact control trajectory below supplies the
separate finite-amplitude obstruction.

Since 3/4<5/6<sqrt(3/4), the first successful writer crosses it. The other
charge-zero eigenvalues are 5, with w*5<a throughout w<=1, so they remain
strictly damped. At chi_A=0, w0=3/4 gives m9=431/512 and m5=287/512;
the history multiplier is 1/2. The initial source is linearly contracting on
the fixed-charge tangent; after the crossing exactly one resource mode grows.
Positive read denominators and h=1/32 keep stable multipliers positive.

For the zero-read control the derivative is also the exact finite-amplitude
resource law. Initialize

$$
C_0=R1+\epsilon_0\phi,\qquad R=9/5,\quad\epsilon_0=1/16.
$$

Then C_n=R1+epsilon_n phi and epsilon_{n+1}=m9(w_n)epsilon_n. The first
step contracts epsilon; later it grows. For n>=1, w_n>=sqrt(3/4)>6/7, so

$$
m_9(w_n)>1+\frac{81}{1568}>1.
$$

It follows that epsilon eventually exceeds R. Indefinite positive continuation
is impossible for any nonzero such initial mode (of either sign) that begins
positive. This is not merely an unstable Jacobian with no excited motion.
The exact homogeneous epsilon=0 trajectory remains positive forever, exposing
the difference between loss of robust stability and inevitable exit of every
state. Enabled nonlinear feedback on nonhomogeneous states is still unproved.

## 5. Orientation-independent partition and parent

Raw oriented edge differences cannot be used as contact signs: changing an
edge's coordinate orientation must not alter a physical split. For an incident
edge e joining v to u, use the incidence-rectified difference

$$
\ell_{v,e}=B_{v,e}(B^\top\phi)_e=\phi_v-\phi_u.
$$

Both factors flip under edge reorientation. The two nonempty strict sign classes
define an unordered partition. Changing phi to -phi exchanges its children;
vertex/edge permutations only transport the sets. Nonzero contact margins and
a simple eigenvalue are essential; ties, zero contacts or multidimensional
critical eigenspaces need separate rules, not numerical tie-breaking.

Only v has both signs in this graph: its values are (-1,-1,+1,+1). Each ui
has the same sign toward all its own neighbours. Thus the source itself yields
both a unique candidate parent and its unordered {u1,u2}|{u3,u4} contact split.
No IDs, noise, activity-variance threshold, target metric or target search is
used. This resolves a limitation of the earlier symmetric star by changing its
physical connectivity, not by breaking symmetry with a label.

The homogeneous recovering state has exactly the same critical mode and sign
partition but does not exit. Instability onset can therefore describe a loss of
robust continuation, not by itself necessity to fire at every such state.

## 6. The mechanically indicated split is not a remedy

Only **after** fixing that source partition, evaluate the direct conservative
unit-site map at the first successfully updated prestate. Retain all twelve
old-edge histories. Replace v by v+ attached to u1,u2 and v- attached to u3,u4,
halve its resource between them, and add a unit-reference bridge with W=1.
Old edges recover uniformly from w1=sqrt(3/4); the new bridge stays at 1 in
this gamma=chi_A=0 control. There are six unit-measure sites and thirteen edges.
This is one explicitly supplied research map, not a native event or accepted
initializer/history-transport policy. Reset/lifecycle admission is not asserted.

On the antisymmetric subspace with leaf values (+z,+z,-z,-z) and child values
(d,-d), the target's retained-mobility Laplacian is

$$
L_{\rm odd}(w)=
\begin{pmatrix}9w&-w\\-2w&2w+2\end{pmatrix}.
$$

Its larger eigenvalue is strictly greater than 9w: the characteristic polynomial
evaluated at 9w is -2w^2<0. At w=1 it is (13+sqrt(33))/2>9. Thus even at the
source critical surface 9w=a the selected target has an unstable mode. The
cross-class old edges that generate the instability were not removed by moving
the parent's contacts. No claim of restored continuation follows from sign lift.

There is also a finite-amplitude evolving-history proof, not merely a frozen
target spectrum. Put t=-d. The target generator restricted to (z,t) is

$$
\begin{pmatrix}
83w^2-\frac{135}{2}w & w(11w-11/2)\\
2w(11w-11/2) & 6w^2-7w-11
\end{pmatrix}.
$$

For 6/7<=w<=1 its upper-left entry is >=153/49, its off-diagonal entries are
positive and its lower-right entry is >=-617/49. At h=1/32 the full update
matrix preserves z>0,t>=0 and

$$
z^+\ge\left(1+\frac{153}{1568}\right)z.
$$

The chosen map starts with z=epsilon_1>0,t=0. If positive target continuation
persisted, fixed total charge 9 would imply z<9/4. Geometric growth contradicts
that bound. The same conclusion follows for exchanged children/sign-reversed
mode. Symmetric resource motion does not remove this independent odd-sector
obstruction. Hence this particular mapped target, with its actual recovering
histories, also cannot continue positively indefinitely.

This refutes “a simple contact-resolving critical mode plus sign split is
sufficient for restorative fission.” It does **not** refute every allocation,
bridge, history, measure law, graph or topology operation. The source graph and
potential were chosen to test the proposed mechanism, not inferred as universal
physical law. In particular, this is not the predecessor's successful 2+2 tree.

## 7. Unaffected-support bound and the branch stop

The review sharpens the reason not to tune this split. For the source mode
phi=(1,1,-1,-1,0), its squared norm is 4. The four parent spokes contribute
4 to phi^T L phi, whereas the eight doubled cross-class edges contribute 32.
Thus the eigenvalue decomposes as

$$
9=\frac4{4}+\frac{32}{4}=1+8.
$$

The dominant contribution is **outside the parent star**. For any parent-only
split retaining the four leaves, their unit measure, the same affine law and
the eight unaffected cross-edge histories, extend the leaf mode by zero on
every new child. The resulting vector psi has sum zero and squared norm 4.
At common cross-edge mobility w, write the target Laplacian as

$$
L_+=L_{\rm cross}(w)+L_{\rm changed},\qquad L_{\rm changed}\succeq0.
$$

Positive-mobility reattached spokes and any positive bridge cannot subtract
from this quadratic form. The Rayleigh bound on the charge-zero tangent gives

$$
\lambda_{\max}(L_+|_{\mathbf1^\perp})
\ge\frac{\psi^\top L_+\psi}{\psi^\top\psi}
\ge8w.
$$

With a=15/2, the unaffected contribution alone exceeds a once w>15/16.
Its existing zero-read history law recovers toward w=1. The resource generator
L_+(L_+-aI) then has a positive eigenvalue irrespective of parent-resource
allocation or positive bridge choice. Allocation cannot change this affine
Jacobian. For the unchanged recovering-history law with fixed reference
weights, the limiting target operator also retains an unstable direction.

This is a **stability-remedy exclusion**, not a theorem that every allocation
or every finely prepared target trajectory exits its positive chart. A positive
eigenvalue alone is not the latter theorem; the explicit map in Section 6 has
its own stronger finite-amplitude proof. The bound is scoped to unit measure,
the affine zero-read law, positive mobilities and untouched cross-edge recovery.
It does not cover new measure/constitutive/history laws, changes to those cross
edges, or arbitrary nonlinear feedback. No universal impossibility of fission
has been established.

Nevertheless this is enough to stop bridge/allocation tuning as a route to
removing the instability: the allowed primitive leaves independently unstable
constitutive support intact. Changing that support would be a different
physical operation or constitutive proposal, not a correction to this split.
Do not launch a measure-refinement campaign to salvage this mechanism.

The arithmetic was checked directly against the retained incidence and mode:
star=4, cross=32, norm squared=4, unaffected threshold=15/16. This short
algebraic strengthening does not rerun trajectories or alter the reviewed
checker/certificate. The bound above states the assumptions needed to extend
the review's argument beyond the one already tested map.

## 8. Evidence, independent review and ATC-2 continuation

The checker retains exact rational incidence/eigenmode identities, adaptive-time
bound, source/target growth bounds, source sign covariance and measure-energy
arithmetic. Decimal96 diagnostics independently reconstruct dense fresh reads
and writer updates, compare their derivatives with the modal formula at three
background states, and compare source/target trajectories against independent
modal/odd-sector recurrences. Rejected resources never execute a retained
writer. Finite differences and Decimal trajectories are diagnostics, not
interval-certified universal bounds; the symbolic derivations above supply
the stated mathematical claims.

The finite nonzero-mode source makes twelve positive updates and rejects its
thirteenth resource proposal. The selected target makes nine positive updates
and rejects its tenth proposal; these counts start at its mapped post-first-beat
prestate, not at the source's original time. There are 29 background/derivative
reads and 23 continuation reads, with 21 positive resource/writer updates and
two rejected proposals. No native steps or topology events execute.
The old obstruction checker and campaigns are not rerun. Typed source traces
retain support boundaries and source/edge identities; they do not admit this
new potential, graph family or critical-mode event consumer.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_critical_mode.py
```

The independent review reproduced the source spectrum/eigenbasis, crossing,
rectified signatures, target odd-sector equations, adaptive predecessor bound
and both zero-read continuations. It verified certificate digest
`6e3a7831bd7ae9ec3f5fa45925d3776837d1e996a6d6dec88e602ca3cf09e647`
and checker SHA-256
`9a10e97c87a521ac9614565a84d1a5729fc8db5527df147d02f3074179e995fc`.
It did not execute the complete repository-dependent forensic checker. Preserve
the original machine evidence, including its historical pending-review status.

| ATC-2 causal link | Current bounded result |
| --- | --- |
| Ordinary source evolution | Established here through retained-history recovery. |
| Endogenous split condition | A simple multiplier crossing and occupied-mode obstruction exist; the homogeneous countercontrol prevents promoting crossing alone to mandatory firing. |
| Source-determined decomposition | Unique parent and unordered orientation-invariant 2+2 lift established. |
| Lawful resource/history transfer | Open: tested charge-conservative map is supplied research, not derived measure/Hodge/history/lifecycle authority. |
| Restored declared continuation | Refuted for the tested map; unaffected-support bound rules out eliminating the instability by parent-only bridge/allocation tuning under the stated law. |
| Autonomous splitting / ATC-2 | Open. This mechanism branch is stopped, not the investigation closed. |

The next candidate must first pass a **scientific operation-compatibility
test**: does its allowed topology primitive actually change a constitutive
component responsible for the obstruction? For binary vertex splitting, seek
a removable component at the split locus and a decomposition of that same
obstruction—not merely an appealing mode sign pattern. This is a necessary
screen, not a sufficient theorem and not a new governance or tooling gate.
If untouched support still suffices for the obstruction, abandon the candidate
before target construction or measure/history elaboration.

Only a candidate surviving that screen merits the remaining derivation:
ordinary evolution → endogenous condition → source-determined decomposition →
lawful resource/history transfer → restored declared continuation. Derive
measure/coarse-fine/energy semantics only as needed to complete that mechanism.
Every further calculation must address a missing link; no partition ranking,
bridge/allocation sweep or standalone measure campaign is the next task here.
If existing V4 dynamics do not supply a compatible mechanism, identify the
specific additional constitutive physics needed through claims/debts rather
than disguising it as a refinement detail. A bounded failed branch alone does
not prove that all existing V4 mechanisms are impossible.

Keep the successful source boundary distinct from a failed ordinary proposal;
K0's timing and witness authority are unchanged. This bounded research neither
installs a spectral trigger nor closes DB-07/27, DB-08, DB-05/06, CAN-F2 or any
family capability cell. Claims/debts → reviewed topology proposal → separate
paper → specs → native 7T remains the propagation order.
