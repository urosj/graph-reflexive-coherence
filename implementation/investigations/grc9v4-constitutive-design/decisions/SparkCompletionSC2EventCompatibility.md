# SC-2 — Source, parent and D11 target compatibility

2026-10-31. **Positive exact preflight, not an admitted event or completion.**
This continues the [selected SC-1 definition](./SparkCompletionSC1Adjudication.md)
and [reviewed conditional site mechanism](./SparkCompletionSC2MechanismAnalysis.md).
[Construction, checks, provenance and debt progress](../evidence/spark-completion/SC2EventPreflight.json)
are reproducible without native evolution. The nonlinear site law remains proposed.

## 1. Construct the parent before the target

Use eleven source vertices: expanded vertex $v$, parent anchor $p$, and nine
neighbors $n_1,\ldots,n_9$. Edge $(v,i)$ joins $(n_i,1)$ for every port
$i=1,\ldots,9$. Three further edges join parent ports 1, 4, 7 to port 4 of
$n_1,n_5,n_9$, respectively. All edge/reference weights are one. Thus $v$ is
exactly saturated, $p$ has all three rows, and endpoints do not collide.

Describe a resource family with a uniform offset $d$:

$$
C_v=1+d,\quad C_p=3+d,\quad
C_{n_1,n_5,n_9}=3/2+d,\quad C_{\text{other }n_i}=3/4+d.
$$

Each row at $v$ has one high and two low neighbors, so its exact row mean
difference is zero. With the already stated geometric thresholds
$s_H=-1$, $\epsilon_g=4$, $\epsilon_H=1/4$,
$\Delta_\Psi=c_{\min}=1/2$, and spark threshold $\epsilon_{\rm spark}=1/8$,
the source meets the algebraic hybrid candidate predicate. Parent rows are
$(-3/2,-3/2,-3/2)$; its gradient-square slack is $37/4$, signed-row slack $5/4$
and neighbor-barrier slack 1. Every increasing-resource route ends at $p$.
Consequently its qualified parent basin is the **entire source graph**, including
$v$. This avoids substituting zero for a missing parent.

These are exact supplied-state diagnostic facts, not a claim that an ordinary
beat formed this state or that a native fresh postbeat read admitted it. The
source graph has two cycles; its qualification does not use the earlier tree
equilibrium exclusion or assume that exclusion is a universal theorem.

## 2. Derive charge compatibility without moving the wells

Keep the proposed global site parameters $c_0=2$, $a=\mu=1$ and the SC-2
equation parameters unchanged. Set desired external capacity 9, giving the
accepted four-node D11 module floor. Replacing $v$ produces fourteen vertices.
For a branch with three upper-well nodes its center charge is

$$
Q_0=14(c_0-a)+2a(3)=20.
$$

The unshifted source has charge 13. At radius $r=1/8$, it fails the necessary
charge test for **every** branch with at least two upper nodes:
$|13-(14+2k)|>14/8$ for $k\geq2$. This excludes those boxes, not every possible
organized equilibrium under the law.

The source family has $Q=13+11d$, so choose **$d=7/11$**, derived from exact
charge compatibility before trajectories. This preserves row differences and
the parent predicate, not constitutive dynamics: the fixed nonlinear potential
is not translation invariant. No node-specific potential, modified well or
outcome-fitted threshold is introduced.

An independent reset source adds $1/64$ at $n_1$ and subtracts $1/128$ at each
of $n_2,n_3$. Its charge and zero expanded-node rows are unchanged; its qualified
parent remains the whole graph. The two roles are checked separately.

## 3. Use the D11 allocation rather than supplying a desired graph

The research check calls the existing pure allocation kernel for both
chiralities, with no extras and no active growth phase, and independently compares
every endpoint with the literal boundary and spine equations. The target has
14 vertices and 15 edges, including the unchanged three parent edges. All nine
old boundary ports move to their column satellite; the internal ports are
$(2,6,7)$ for positive chirality and $(3,4,8)$ for negative chirality.

This is use of the mechanical allocation kernel only. Its research role namespace
is not a computed native event identity; no complete profile/request, source
readmission, current solve, transaction or committed event is being claimed.

Fix the event-supplied dyadic tuple $(1/2,3/8,1/8)$ before any trajectory.
It is an explicit asymmetric mechanical input, not an autonomous partition law
or evidence that ensuing dynamics selects the desired equilibrium branch.
Both roles use the accepted map: zero core, $C_{s_b}=p_b C_v$, unchanged exterior.
Here the satellite resources are $(9/11,27/44,9/44)$ and total charge is exactly
20. The target classifier still has only the old parent basin. **Mechanical
allocation alone earns no completion gain.** The new zero core also lies outside
the strictly positive branch box below.

## 4. Recompute the conditional stationary bounds on this actual layout

Consider the branch with upper nodes $p,s_1,s_2$, all other eleven nodes lower.
The target is connected, has maximum degree 4 and diameter 4. At the well center,
$\|L\|_\infty=\|LC^0\|_\infty=8$, while $\|P\|_\infty=13/7$.
The same general equilibrium argument from SC-2 gives

$$
M=829/7168<r=1/8,\qquad r-M=67/7168,\qquad q_{\rm eq}=719/896<1.
$$

This proves an exact equilibrium in that charge-20 branch box. No numerically
selected root or trajectory supplies the existence argument.

For the full exact C_OS derivative, retain $\kappa=1/64$, $\eta_C=\tau_C=1$,
$\chi_C=\zeta_C=1/2$, $\kappa_H=1/2$, $\kappa_{M,C}=0$ and $h=1/32$.
The graph-dependent bounds now are

$$
(75/64)I\preceq D\preceq(179/64)I,\qquad
(1/26)I_E\preceq A|_E\preceq(32/3)I_E.
$$

Thus $h a_{\max}d_{\max}=179/192<1$ and

$$
\|DT_{\rm OS}(C^*)\|_{A^{-1}}\leq53173/53248<1.
$$

The same smoothness argument proves local exact attraction; it does not quantify
a physical trapping radius. The selector cutoff $1/64$ remains below the proved
spectral lower bound $1/26$. These are newly checked target-specific constants,
not transferred numerical bounds from the ten-node example.

Throughout the branch box, each of $s_1,s_2$ is a qualified seed with all-neighbor
contrast at least $7/4$. Repeated neighbors within one row still give weighted
means in $[7/4,9/4]$, preserving the previous strict row margins. Each has two
private degree-one leaves: $s_1$ has $n_4,n_7$, and $s_2$ has $n_2,n_8$.
These leaves have only their own satellite as a higher neighbor, proving two
distinct nontrivial guaranteed domains. Since the lifted parent footprint is
the entire target, both are eligible new descendants. The stationary branch
therefore has at least two eligible child basins, conditional on this proposed law.

Only these guaranteed subsets are certified uniformly here. Low–low edges can
change their descent ordering across the box; complete basin membership and one
uniform descent DAG have **not** been proved. The box is still an equilibrium
proof domain, not a physical self-map. Neither transferred role is in it, and
local equilibrium attraction is not a proof of approach from the event state.

## 5. Disposition and next work

This removes the missing-parent, literal-D11-layout and charge incompatibilities
for a concrete proposed source/target construction. The scoped scientific result
is a positive compatibility preflight plus a conditional stationary branch with
eligible new children. It does not establish a lawful completed-spark trajectory.

Next check the proposed complete C_OS source and transferred-role admission, then
study actual post-event evolution and whether it reaches an organized branch.
Keep an explicit failure if admission or entry fails. If entry is obtained,
certify the actual complete basin roster/descent relations and a quantitative
full-OS trapping neighborhood there, with the required constraint and diagnostic
numerical lift. SC-2's quartic binding still needs its own adjudication; SC-1
stays closed. No production evaluator, native event, propagation or G4 support
is added by this preflight.

    .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_event_preflight.py --check
