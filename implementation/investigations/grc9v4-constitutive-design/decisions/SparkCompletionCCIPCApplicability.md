# C_CI_PC completion applicability — one selected source and full C/Z return

2026-10-31. Investigation-only successor to accepted C_OS, C_CI and C_PC on
`investigation/grc9v4-spark-completion`, from `87d2f474`. This is bounded
conditional mathematical research. Scientific adjudication remains pending;
no native evaluator, completed-spark owner, hierarchy or G4 grant is added.

## Declared composite map

The [declaration](../evidence/spark-completion/applicability/CCIPCDeclaration.json)
keeps the homogeneous quartic V'(C)=(C-2)^3-(C-2), unit reference Hodges and
transport, zero context, eta=1/1024, kappa_Phi=1/64, duration h=32, tau_C=1,
chi=zeta=kappa_H=1/2, kappa_M=0 and tau_PC=32. Independent state is (C,Z),
where Z is signed, symmetric and supported on vertex stars. For outward
incidence B, L=B^T B and overlap O_ij equal to shared endpoint count, solve

\[
S_{ij}(f)=O_{ij}f_i f_j/4,\qquad H(f,Z)=I+(Z+S(f))/2,
\]
\[
j_0=-\frac1{1024}B^T\left(\frac1{64}BHB^TC-V'(C)\right),
\quad y=(3I/4+HL)^{-1}j_0,\quad F(C,Z,f)=H^{-1}y/2,
\]
\[
f=F(C,Z,f),\qquad J=j_0+y/4,
\quad C^+=C-32BJ,\quad Z^+=e^{-1}Z+(1-e^{-1})S(f).
\]

The **same selected f** supplies immediate geometry, current and the held
persistent source. Fresh poststate reconstruction uses both C+ and Z+;
it cannot replace the pre-continuity writer source. A stationary writer has
Z=S, hence H=I+S: the composite gain is **two** relative to either contribution
alone. A zero-carrier read agrees with CI, but its next carrier is generally
nonzero; that agreement does not reduce the full map to CI. PC omits the
instantaneous term and also gives a different nonstationary current.

## Signed carrier and selected-root domain

Select C in [0,4]^V, ||Z||_F<=1/128 and ||f||_infinity<=R=1/32. The carrier
radius is a new explicit domain choice. The earlier PC radius 1/64 does not
pass this particular uniform source-graph root estimate; failure of that
estimate is not a physical obstruction at larger radius. No parameter or
predicate was adjusted after a long run.

Let s=max_i sum_j O_ij/8, ell=||L||_infinity,
b=||B||_infinity, a=||(3I/4+L)^-1||_infinity, and
z=ceil(sqrt(m))/(2*128). Exact FLINT rational bounds give

\[
d=z+sR^2,\quad u=(1-d)^{-1},\quad N=a/(1-ad\ell),
\]
\[
j_* =2\eta(4\kappa b+6)+4\eta\kappa\ell d,
\quad y_*=Nj_*,\quad f_*=uy_*/2,
\]
\[
L_H=u\left[N(4\eta\kappa\ell+\ell y_*)/2+f_*\right],
\quad q_f=2sR L_H.
\]

Both graphs have d<1, ad ell<1, f_*<R and q_f<1: root contraction is
approximately 0.063351 on the source and 0.019589 on the target. Thus every
state in the declared box has a unique root **within this selected ball**;
no claim excludes roots elsewhere. Real S is a sum of positive star outer
products, so H has lower eigenvalue at least 255/256. The explicit upper
bound 1+1/256+mR^2/4 and the connected-graph spectral separation preserve
selector admission. Neumann bounds establish regularity of the physical
current block, including both occurrences of H.

At the selected root, ||S||_F<=m f_*^2/2<1/128 (below 0.002758 source and
0.002413 target). The exponential writer therefore preserves the carrier
ball while C stays in its chart. Global resource-box invariance is not
claimed. Every trajectory state is checked, and the local trap proves its
own invariance in all physical directions.

Newton calculates midpoint proposals only. The final root enclosure uses

\[
\|f(C,Z)-f_0\|_\infty\le
\sup_{C,Z\text{ in input box}}\|F(C,Z,f_0)-f_0\|_\infty/(1-q_f).
\]

Every physical input box and this residual certificate stay at fixed 8192-bit
Arb precision. Proposal arithmetic follows the declared 128,256,...,8192-bit
schedule, with at most sixteen Newton evaluations per stage. The state never
follows a midpoint, and a failed enclosure rejects explicitly. This schedule
is a root-proposal optimization, not a fallback or trajectory precision switch.

## Full sixty-dimensional contraction and stationary state

Reuse the exact charge-21 center c and metric P=(A0+11^T/15)^-1, where
A0=B[I+(3I/4+L)^-1/4]B^T, under their established algebraic hypotheses.
Independently prove the composite map on

\[
\max(\|C-c\|_P,1024\|Z\|_F)\le 2^{-20},\qquad 1^TC=21.
\]

This includes fourteen resource and forty-six independent symmetric star
carrier directions; offdiagonal basis elements are (E_ij+E_ji)/sqrt(2).
The carrier radius is 2^-30 and includes nonzero signed perturbations.

For independent C,Z,f, differentiate both H consumers:

\[
dj_0=-\eta B^T[\kappa B(dH)B^TC+(\kappa BHB^T-V''(C))dC],
\quad dy=M^{-1}(dj_0-dH Ly),
\]
\[
dF=H^{-1}(dy/2-dH F),\quad dJ=dj_0+dy/4,
\quad dH=dZ/2+DS(f)df/2.
\]

The root theorem gives
D_C f=(I-F_f)^-1 F_C and D_Z f=(I-F_f)^-1 F_Z. Insert both into current
and source derivatives before forming the four physical update blocks.
Thus T_CC=I-32B(J_C+J_f D_C f), T_CZ=-32B(J_Z+J_f D_Z f),
T_ZC=(1-e^-1)DS D_C f and T_ZZ=e^-1 I+(1-e^-1)DS D_Z f.
Frozen-H or C-only derivatives omit required feedback.

Fresh 512-bit Arb bounds over a coordinate box enclosing the whole trap
use the established reference derivative bound q0 and t=tr(P)-1:

\[
b_{CC}=q_0+\sqrt{A_{max}t}\|T_{CC}-T_{ref}\|_F,
\quad b_{CZ}=\sqrt t\|T_{CZ}\|_F,
\]
\[
b_{ZC}=(1-e^{-1})\sqrt{A_{max}}\|DS D_Cf\|_F,
\quad b_{ZZ}=e^{-1}+(1-e^{-1})\|DS D_Zf\|_F.
\]

The maximum weighted row is below 0.997358 and the strict image margin is
above 2.51e-9. This proves full-state contraction and self-mapping, separately
from the much faster auxiliary-root contraction. Complete qualified basins
{p,private} and {satellite2,n2,n8}, including all routing terminals, persist
throughout the same resource enclosure on both chiral charts.

A **separate reference-submap calculation** proves existence of a reference
resource equilibrium inside the ball. The composite Z=0 map itself is CI,
so it is not silently used as that reference submap. At the exact reference
equilibrium B^T Phi=0 and J=f=S=0. Therefore (C*,0) is a fixed point of the
composite map; full contraction proves local uniqueness. This establishes
stationary Z=0 without suppressing nonzero carrier perturbations or writes.

## Actual source, event, approach and observation window

Reuse only the exact SC2SourceBeat resource **prestates**, with source carriers
+2^-16 I for current and -2^-17 I for reset. Execute a new composite current
beat including its writer, then reconstruct its fresh event root. Reset is
independently read and not advanced. The actual postbeat source is positive,
saturated and trigger-eligible with its complete qualified parent.

Literal D11 expansion transfers actual postbeat resources with shares
(1/64,31/32,1/64), zero core and copied exterior. Exact incidence conservation
and shares summing to one establish charge 21. An interval containing 21
alone is not the conservation proof. The declared P→P policy archives both
actual source histories and zeros every dense target carrier entry. This is
explicit carrier-history loss at the event, not native exponential release.
Subsequent ordinary beats regenerate and consume history.

The prioritized campaign runs only the actual current and independent reset
chains needed for this claim, with a 1024-step horizon and one-hour cap per
role. Each must enter the full trap and then commit two positive duration-32
ordinary beats (elapsed 64); only current earns a live gain. There is no
separate generic large-fixture batch or inherited C_CI/C_PC trajectory.
Both original certified executions completed successfully:

| History | First observed final basin roster | Full C/Z trap entry | Two-beat window end | Live gain |
| --- | ---: | ---: | ---: | ---: |
| current | 100 | 849 | 851 | 1 |
| reset | 117 | 817 | 819 | 0 |

Current/reset execution took 445.80/
424.33 seconds respectively, well inside
the declared caps. These are sufficient certified entry/completion times, not
earliest mathematical times. Matching earlier-family step counts does not
establish identical trajectories or dynamics.

The [current](../evidence/spark-completion/applicability/CCIPC-current.json.xz)
and [reset](../evidence/spark-completion/applicability/CCIPC-reset.json.xz)
archives retain 1,670 full C/Z states for the named
all-state classification and recurrence-consistency checker. Lossless compression
reduces 21,053,272 JSON bytes to 2,442,036 bytes. All retained states and both
chiral classifications pass; nineteen rehashed false-completion/subject controls
reject and repeating the same research event earns zero additional gain.

Only full-graph-keyed exact operands and rational root-domain constants are
cached. Derivative right-hand sides share factorizations; a fresh full-state
read is reused only on its identical next-step subject. Numerical incidence
matches across charts, while both port-dependent classifications are checked.
The [preflight](../evidence/spark-completion/applicability/CCIPCPreflight.json)
verified these optimizations before either long campaign. Sampled root reads
improved from 0.589 to 0.262 seconds (source) and 0.637 to 0.312 (target);
the precision-weighted Newton work fell from 81920 to 32896 precision-bit evaluations.
These are local samples, not a whole-campaign speedup claim.

## Evidence and scientific boundary

The [repository review](../evidence/spark-completion/applicability/review/CCIPCScientificReview.md)
distinguishes original certified execution from saved-versus-fresh consistency
checks. Compact outward 112-bit enclosures are inspection storage, never fed
back into evolution or called exact replay checkpoints. Fresh root/read and
recurrence overlap is consistency only; original certified runs establish
trajectory provenance, and proof calculations use fresh interval enclosures.
No independent second reviewer or independent long replay is claimed.

The original producer's post-save diagnostic check rejected a lawful outward
residual enclosure because its lower endpoint was slightly negative. The new
`check_spark_completion_ci_pc_retained.py` is the retained-validation entry:
it permits such outward rounding, rejects bounds that exclude nonnegative
residuals, and checks complete selected f/H/J/S fields against fresh roots.
Residual/error scalars are proposal- and input-width-dependent diagnostics;
they are not required to equal a different fresh solve's bounds. A dedicated
regression covers this distinction. Original producer bytes, source pins and
both execution archives are unchanged; no numerical run was repeated.


The [progress report](../evidence/spark-completion/applicability/CCIPCResearchProgress.json)
keeps three proposed conditional claims and `SC-APP-DEBT-C_CI_PC` pending
explicit adjudication. The accepted C_OS/C_CI/C_PC records are unchanged.
After acceptance, propagate authority → proposal/paper → specification and
route native numerical/lifecycle obligations to P9-9.1a. A_OS follows in the
research order; it has not started here. Aggregate P9-10.5/10.6 remains open.

Read-only inspection is available at
`/api/spark-completion/applicability/ci-pc/research`, its source index and
browser panel, and notebook cell `spark-completion-ci-pc-research`. Refresh
checks retained integrity; it runs no scientific trajectories.

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_ci_pc_research.py --check
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_ci_pc_reconciliation.py
```

The first is the lean restart check; the second recomputes fresh mathematics
and retained consistency. `--run` on the campaign checker refuses to overwrite
a retained execution and requires the matching optimization preflight.
