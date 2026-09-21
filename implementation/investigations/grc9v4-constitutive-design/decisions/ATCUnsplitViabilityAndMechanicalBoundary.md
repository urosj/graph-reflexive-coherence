> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# Unsplit continuation obstruction and the missing mechanical fission law

Status: independently reviewed conditional mathematics, PASS. The review
reconstructed the exact bounds, energies, modes and enabled scalar trajectory;
it did not execute the repository checker/forensic stage end-to-end. No accepted claim/debt, native
potential, event guard, topology policy, paper or specification is changed.
All reviewed predecessor evidence remains unchanged.

The user redirected the investigation from improving grouping evidence to the
physical question: **can remaining unsplit obstruct a required continuation,
and can refinement resolve that obstruction?** The earlier three-way
resource/history/current comparison is no longer a milestone in its own right.
Grouping observables are useful only insofar as they discriminate a mechanism.

This step supplies two results, neither a completed autonomous split law:

- A declared symmetric A_OS source cannot continue indefinitely inside its
  positive resource domain, despite well-defined fresh reads, geometry and
  evolving retained history. Equal incident currents persist throughout.
- Fixed-topology dynamics do not determine a cross-topology creation-energy
  offset. Even a chosen zero-offset energy decrease does not discriminate the
  previously reviewed restorative 2+2 map from its unstable 1+3 counterexample.

These identify a concrete continuation problem and a missing constitutive
choice, not a new clustering threshold.

## 1. What continuation is required here

Use the affine research declaration from the reviewed
[partition/OS theorem](./ATCPartitionOSFeedback.md): p(c)=19c/4,
eta=kappa_c=zeta_A=1, alpha=beta=0, no carrier, unit reference edge weights,
identity reference Hodge pairings and identity common star-tensor adapter.
The gain box remains

$$
0\le\gamma\le2^{-16},\quad0\le\chi_A\le1/2,\quad
0\le\kappa_H,\kappa_{Ah}\le1.
$$

The declared research floor is 1/2 and split-residual tolerance 2^-9. Neither
the affine potential nor this tolerance is silently admitted to native V4.

Consider the closed four-leaf star, with identical leaf resources r, parent
resource s, charge 4r+s=9, and identical old log histories y in [-1/256,0].
Define the source concentration x=s-r. Then

$$
r=\frac{9-x}{5},\qquad s=\frac{9+4x}{5},\qquad 0<x<9.
$$

The starting state is (1,1,1,1,5), so x0=4. The continuation requirement is
indefinite **closed, positive-resource, fixed-topology ordinary evolution**
under this same law. No external resource injection, new profile, clipping,
projection or changed potential is permitted in that comparison.

This is a deliberately explicit research requirement, not a theorem that every
V4 profile has this positive chart or owes indefinite operation. A fixed-graph
execution may instead fail closed. Nor does absence of this long-run
continuation mean the initial present-state read has no solution: it does.
We do not assert that every possible continuation set is empty.

## 2. Complete symmetric A_OS reconstruction

Symmetry is preserved by both ordinary resource and history writes. Each
canonical leaf-to-parent current has the same scalar value. Write w=exp(y).
The predictor baseline and fresh read are

$$
v_0=w(5w-19/4)x,\qquad
q(v)=\tanh\!\left(\frac{y+\gamma v^2/2}{2}\right),\qquad
F_y(v)=\frac{v}{1-\chi_Aq(v)},\qquad f_0=F_y(v_0)-v_0.
$$

The normalized star tensor is S0=f0 squared (I+11-transpose)/2. It has
uniform eigenvalue (5/2)f0 squared and three contrast eigenvalues f0 squared/2.
The fresh Hodge is H1=I+kappa_H S0, and its potential consumer gives

$$
v_1=v_0+\frac{25}{2}\kappa_{Ah}\kappa_H w x f_0^2,\qquad
j=F_y(v_1),\qquad
f_1=\frac{\chi_Aq(v_1)j}{1+(5/2)\kappa_H f_0^2}.
$$

This includes the generated geometry and a fresh corrector pre-read. The
corrector's inverse pairing is used for the residual, not to select a second
corrector. Only j enters continuity and the subsequent retained writer:

$$
r^+=r-hj,\qquad s^+=s+4hj,\qquad x^+=x+5hj,
$$

$$
y^+=(1-\rho)y-\rho\frac\gamma2j^2,
\qquad \rho=1-e^{-h/\tau_A}.
$$

At h=1/8, tau_A=(1/8)/log(2), rho=1/2, exactly as in the predecessor.
An invalid resource proposal is not committed and does not execute the writer.
Reset and event histories play no role in this research continuation.

## 3. A uniform barrier to indefinite positive continuation

Let b=Q=1/256. Over 0<x<9 and -b<=y<=0, w>=255/256, so

$$
\frac{15045}{65536}x\le v_0<\frac94.
$$

Use the ordered bootstrap predictor → generated geometry → fresh corrector.
For predictor and corrector components bounded by 5/2,

$$
|q(v)|\le\frac12(b+\gamma v^2/2)<Q,\qquad
1-\chi_Aq(v)\ge511/512,\qquad
\frac{\chi_A|q|}{1-\chi_A|q|}\le1/511.
$$

The geometry correction is nonnegative in this symmetric source and satisfies

$$
0\le v_1-v_0\le\frac{225}{2}\left(\frac9{4\cdot511}\right)^2
=\frac{18225}{8355872}<\frac14.
$$

Thus v1<5/2, closing the bootstrap. Both pre-read floors stay inactive.
H1 is positive definite, and the residual has the sufficient bound

$$
\|R_h\|_2\le\|R_h\|_F
\le4\left[\left(\frac9{4\cdot511}\right)^2+
\left(\frac5{2\cdot511}\right)^2\right]
=\frac{181}{1044484}<2^{-9}.
$$

Furthermore j<1280/511 and

$$
\frac\gamma2j^2\le\frac{25}{522242}<b.
$$

The writer is a convex combination of two values in [-b,0]. Therefore the
history interval is invariant after every positive ordinary update. History
is not frozen to obtain the result.

Since the geometry correction is nonnegative and the read denominator is at
most 513/512, the selected inward current satisfies

$$
j\ge c_* x,\qquad c_*:=\frac{5015}{21888}>0.2291.
$$

Consequently every positive update obeys

$$
x^+\ge(1+5hc_*)x.
$$

If the source could remain positive indefinitely at any fixed h>0, this would
force x to exceed 9, contradicting r>0. At h=1/8 the lower multiplier is
200179/175104, and exact rational arithmetic gives

$$
4(200179/175104)^6<9<4(200179/175104)^7.
$$

Thus a nonpositive resource proposal must occur **by the seventh attempted
ordinary update**, throughout the stated gain/history box. All preceding
source reads remain within the proved current, floor and residual bounds.
This is a resource-domain obstruction, not a root-solver failure.

### It is not cured by simply choosing a smaller fixed step

The same current and convex-writer estimates hold for every fixed h>0 with
the same tau_A and its corresponding rho. Smaller h delays the discrete
failure; it does not make indefinite positive continuation possible. This
did not originally analyze arbitrary adaptive schedules. The reviewed checker
and certificate remain unchanged. The successor
[adaptive-step proof](./ATCCriticalModeAndRefinementTest.md#1-review-integration-and-adaptive-stepping)
now excludes indefinite positive continuation for every positive non-Zeno
schedule under the same law; this does not authorize native adaptive stepping.

In the exact zero-channel control, w=1 and j=x/4. The resource generator is
dx/dt=5x/4, so x(t)=4 exp(5t/4) reaches x=9 at

$$
t_*=(4/5)\log(9/4)\approx0.648744.
$$

At that boundary the leaf rate is -9/4, directed out of the nonnegative domain.
This continuous-time control identifies genuine loss of positivity, not only
Euler overshoot. It is not a newly asserted continuous-time contract for every
feedback realization. The full-feedback result above is the discrete theorem.

## 4. What the obstruction does and does not select

All four selected activities remain equal. Their within-block variance is
zero for **every** binary partition, even along the failing continuation.
An activity-heterogeneity threshold is therefore not a detector of this
obstruction. The full symmetric source still cannot select one labeled binary
partition equivariantly; generated geometry supplies no preferred contrast
direction. This is an instance of the reviewed
[symmetry obstruction](./ATCSourcePartitionSymmetry.md), not an implementation tie.

In the zero-channel control, the charge-zero concentration mode
(-1,-1,-1,-1,4) has Laplacian eigenvalue 5 and growth rate 5/4. Its Euler
multiplier is 37/32. The three leaf-contrast modes have eigenvalue 1, rate
-15/4 and multiplier 17/32. The unstable direction distinguishes the parent
from **all** leaves, not one subset of its contacts from another. It is not a
mechanical half-edge lift. The instability is already present initially; this
work proves endogenous approach to resource failure, not a newly crossed
instability onset.

The homogeneous source C=(9/5)1 instead has exactly zero current and constant
resources; depressed uniform history relaxes toward one. It remains a valid
exact trajectory, but is not thereby robustly stable against the concentration
mode. This separates occupying the unstable direction from merely having
an unstable linearized mode available.

### What can be reused from the supplied-refinement theorem

At the **same initial** (1,1,1,1,5) source, the already reviewed supplied 2+2
map yields (1,1,1,1,5/2,5/2). Under the same gain box, any target old-edge
histories in the box and a unit new bridge, the predecessor proves entry into
positive full-state return. Its supplied 1+3 control retains an expanding
mode and positive-resource first-step expansion. No new target campaign is
needed to repeat those statements.

This shows that the continuation problem can depend on topology under the
same constitutive law. It does **not** show that fission is the only remedy,
that the affine research law is the right law for all sources, or that every
other unsplit continuation is impossible. Nor does it derive the 2+2 partition:
using favorable target outcomes to choose that map would be the forbidden
lookahead. Both supplied targets preserve resource charge but change the
number of unit-measure sites; neither is a neutral subdivision.

The target theorem is for the original prestate, not every later depleted
source along this new trajectory. Its bounds cannot silently be transferred
to a late split or to a changed allocator/history policy.

## 5. Why a mechanical energy trigger still needs a contract

For the zero-channel unit-W control, a compatible fixed-graph resource energy is

$$
E_\mu(C,T)=\sum_{i\in V(T)}\left(\frac{19}{8}C_i^2+\mu\right)
-\frac12\sum_{e\in E(T)}(B^\top C)_e^2.
$$

Here mu has energy units per unit-measure site. Every value gives the same
gradient (19/4)C-LC and the same fixed-graph Hessian and current. In the
declared full-feedback equations, the fresh conductance, read, geometry and
writer also depend on derivative/baseline quantities, not this additive
constant. Thus varying mu does not alter that ordinary source evolution.

But a charge-preserving binary split adds one site, giving

$$
\Delta E_\mu=\Delta E_0+\mu.
$$

Fixed-topology trajectories cannot determine the sign of this cross-topology
energy difference. A mechanical birth-energy principle would need an
independently justified topology/creation-energy reference and any associated
barrier or work budget. Choosing mu=0 is a possible convention, not a
consequence of the ordinary dynamics. A new contract could settle it; this is
not an impossibility theorem against energy-based ATC.

There is also a distinct counterexample even at mu=0. Exact energies of the
already supplied source and targets are

| State | E0 | Difference from source |
| --- | --- | --- |
| Unsplit (1,1,1,1,5) | 295/8 | 0 |
| Supplied 2+2 | 555/16 | -35/16 |
| Supplied 1+3 | 2055/64 | -305/64 |

The 1+3 target has the greater energy drop despite its reviewed nonrestorative
mode and first-step expansion. An initial energy drop is not a stability or
support certificate. Mu=3 reverses the 2+2 birth-energy sign; mu=5 reverses
both signs while preserving all fixed-topology derivatives. These are algebraic
tests of an insufficient proposed principle, not an implemented target ranking.
E0 is not asserted to be a Lyapunov function of the full feedback system.

## 6. Four-part mechanism test and the causal boundary

The user's supplied comment sharpens what a completed mechanism would need:

| Scientific requirement | What this step establishes |
| --- | --- |
| Condition develops under ordinary source dynamics | Positive sources approach a resource-domain exit with actual C/W evolution; instability itself is present initially, not a demonstrated new onset. |
| Obstruction to the declared unsplit continuation | No indefinite closed positive continuation in this declared family; the present read still exists and this is not a universal V4 requirement. |
| Partition mechanically connected to that obstruction | **Open.** The concentration mode and S4 symmetry do not choose a binary contact partition. |
| Refinement resolves the obstruction under the contracts | A reviewed supplied 2+2 remedy exists at the initial prestate; a mechanically selected, correctly timed and fully admitted event remains **open**. |

Therefore this is not yet evidence of a completed autonomous split mechanism.
Repeated failures to find an obstruction in other bounded fixtures would also
not prove that no V4 profile/topology can have one. Likewise a numerical solver
failure cannot substitute for proof of absent constitutive solutions.

[K0](./ATC1CausalBoundaryProposal.md#5-two-transactions-under-one-serialized-evolution-operation)
evaluates ATC only after a successful ordinary commit. A resource-rejected beat
does not invoke ATC and cannot be repaired retrospectively as a successful
split. A future mechanism must identify and justify an eligible earlier
successful source boundary, or separately reopen the schedule. The step-seven
bound is an analysis result, **not** permission to use clocks, step counts,
requested durations or failure counters as physical trigger inputs.
K0's OS witness is reference-stage, whereas the ordinary evolution proved
here consumes a fresh OS corrector; no implicit witness-stage change is made.

## 7. Evidence and the next scientific task

The [checker](../scripts/certify_atc_unsplit_viability.py) emits the
[certificate](../evidence/autonomous-topology-change/ATCUnsplitViabilityCertificate.json).
Exact rational inequalities prove the full stated box, concentration and
contrast modes, and cross-topology energy arithmetic. Fifty-one exact centered
energy differences confirm gradient independence from the three test offsets
on the retained source and two supplied targets.

Two Decimal96 source continuations execute ten positive mathematical resource/
writer updates in total. Both propose a negative leaf resource at attempt six;
neither rejected proposal is committed or writes history. Fourteen complete
source reads include those two rejected-update prestates, one homogeneous
control and one signed/reordered representation. Independent scalar and dense
incidence/Hodge reconstructions agree. There are no native steps, topology
events or new target dynamic runs. These are finite diagnostics, not certified
rounding enclosures or a substituted proof of the universal inequalities.

At the fully enabled corner, the last positive leaf resource is about
0.164725; the next proposal is about -0.090356. Uniform old y has evolved from
-1/512 to about -0.00007978. In the zero-channel control the corresponding
resources are 0.146711 and -0.111615, with y remaining zero despite executed
writers. Both histories are retained explicitly.

The checker verifies the reviewed partition/OS digest and its source bindings.
Six typed forensic queries match its retained traces; full additional
continuity and writer-target traces retain `indeterminate_requires_review`.
Those source/edge references supply equation lineage, not admission of this
new viability theorem or a mechanical energy law. The accepted records,
original paper/specifications and production sources remain unchanged.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_unsplit_viability.py
```

This prints a new deterministic record without overwriting retained evidence.

The independent review verified canonical certificate digest
`1351c25a8765f2eb41f09b63e976127342c15cd35246057e6ee26ad6e759f2d5`
and checker SHA-256
`d3c6017f53fb9e46ab16e50e9f6b3e9c8f889f1567c2608450494c334a744d46`.
Its reconstruction supports the bounded obstruction, history invariance,
symmetry negative and unit-site energy non-identifiability, not autonomous
fission or a fresh repository forensic rerun. The historical machine record
retains its original pre-review status. The review also correctly asks whether
a conserved-measure subdivision would cancel the constant energy contribution;
the successor inspects that separate possibility rather than asserting every
future fission must create a new unit-measure site.

The next scientific task, now pursued in the
[critical-mode investigation](./ATCCriticalModeAndRefinementTest.md), is an **obstruction-linked refinement
principle and partition**, not another three-way grouping benchmark. Seek a
lawful source condition whose mechanically meaningful distinction actually
decomposes the obstructed organization; use resource/history/current partitions
only to discriminate that hypothesis. This example's symmetric depletion
cannot supply that lift. Any cross-topology energy argument must first bind
its missing creation-energy reference rather than tuning an offset to favor
birth. Timing, conservative funding/history transport and whole-target
continuation remain separate obligations; no late-target success is assumed.

The result bears on DB-07/27's physical-operation meaning and exposes limits
on DB-08's lift and DB-05/06's functional route. It does not close those debts,
any capability/family cell, or CAN-B's structural claim. Claims/debts → reviewed
topology proposal → extension paper → specifications → native 7T remains the
propagation order.
