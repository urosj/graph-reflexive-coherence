# Connected-graph C_RG2b completion: research prerequisite

This is a proposed graph-domain extension of the accepted signed
[argument-retraction completion](./P9-8.0-RG2bCompletion.md), not native
support. It changes neither the physical equations nor the auxiliary
retraction, state/geometry norms, timestep or scientific coefficients.
Its purpose is to discharge the graph-size/tree hypotheses for the actual
deep and large subjects before implementing their numerical sections.

Let $B$ be the outward-tail incidence, $D=B^TB$, $A_\star=|B|^T|B|/2$,
$H=I+E$, $E=E^T$ star-supported, and $\|E\|_\infty\le\rho=2^{-12}$.
Only simple connected nine-port graphs with unit reference measures/weights
and zero base carrier enter this calculation. Physical C is never clipped.
The auxiliary maps still evaluate their increments at
$P(C)=\operatorname{clip}_{[-1,5]}C$, retaining the unmodified outer C.
The accepted signed charts and section Lipschitz limit $L=2^{-10}$ remain.

For a graph with $n$ vertices and diameter $d_g$, the zero-mean variance
bound and a shortest path between extreme values give

$$
\|x\|_2^2\le n(\max x-\min x)^2/4,
\qquad (\max x-\min x)^2\le d_g\,x^TBB^Tx.
$$

Consequently $\lambda_2(BHB^T)\ge(1-\rho)4/(nd_g)$. Strict comparison
with $\Lambda_C=1/512$ certifies the constant selector on the entire H ball.
Connectivity alone is insufficient; an inconclusive bound grants no selector
credit. The scalar modulation is therefore
$t=\exp(2^{-24}\tanh(\operatorname{mean}C))$, with
$1-2^{-24}\le t\le t_*=(1-2^{-24})^{-1}$ and
$t_X\le t_*2^{-24}$ on the complete retracted chart.

The old estimate $\sqrt m(1+\rho)/(1-\rho)$ loses too much on large
graphs. Instead calculate exactly, once per graph,

$$
R_0=(I+D)^{-1}=I-B^T(I+BB^T)^{-1}B,
\quad r_0=\|R_0\|_\infty,\quad s_0=\|I-R_0\|_\infty.
$$

FLINT solves the rational vertex system. No floating inverse, eigenvalue
estimate or approximate norm is used as proof. For $R=(I+tHD)^{-1}$ put

$$
\delta=(t_*-1+t_*\rho)s_0<1,
\quad r=\frac{r_0}{1-\delta},
\quad s=s_0+\frac{r_0\delta}{1-\delta}.
$$

Indeed $I+tHD=(I+F)(I+D)$ with $F=(tH-I)DR_0$. Thus
$R=R_0(I+F)^{-1}$, $\|R\|_\infty\le r$ and
$\|I-R\|_\infty\le s$ uniformly. No commutation of H and D is used.
This norm argument includes indefinite symmetric H perturbations; it is
not restricted to the generated positive structural source.

Write $d=\|D\|_\infty$, $b=\|B\|_\infty$,
$a=\|A_\star\|_\infty$, $h=(1-\rho)^{-1}$,
$\chi=16$, $\zeta=2^{-37}$ and $p=\chi\zeta$. The unchanged equations are

$$
J_0=-tDH B^TC,\qquad J=(I-pR)^{-1}J_0,\qquad
c=\chi RJ,\quad v=H^{-1}c,\quad S=\zeta A_\star\odot vv^T.
$$

Use $\theta=pr<1$, $j_0=t_*d(1+\rho)6$,
$j_{0X}=d(1+\rho)(2t_*+6t_X)$, $j_{0H}=6t_*d$,
$R_X=r^2t_X(1+\rho)d$ and $R_H=r^2t_*d$. Then

$$
j=\frac{j_0}{1-\theta},\quad
j_X=\frac{j_{0X}+pR_Xj}{1-\theta},\quad
j_H=\frac{j_{0H}+pR_Hj}{1-\theta}.
$$

The exact identity $RJ_0=(R-I)B^TC-Rt(DH-HD)B^TC$ yields the sharper value
bound $c_*=6\chi(s+2rt_*d\rho)/(1-\theta)$. Slope bounds remain
$c_X=\chi(R_Xj+rj_X)$ and $c_H=\chi(R_Hj+rj_H)$.
Set $v_*=hc_*$, $v_X=hc_X$, $v_H=hc_H+h^2c_*$, giving

$$
M_S=\zeta a v_*^2,\quad B_X=2\zeta a v_*v_X,\quad
B_H=2\zeta a v_*v_H,
\quad A_X=2^{-12}bj_X,\quad A_H=2^{-12}bj_H,\quad M_f=2^{-12}bj.
$$

The original Banach argument applies when

$$
\ell=A_X+A_HL<1,\quad M_f<1/4,\quad
V=\tfrac12M_S<\rho,\quad
L'=\frac{B_X+B_HL}{2(1-\ell)}\le L,
$$

$$
q=\tfrac12\left[B_H+\frac{(B_X+B_HL)A_H}{1-\ell}\right]<1.
$$

It then supplies a unique completion-relative bounded Lipschitz section.
It does not close `GTRS-RG-DEBT-C1-SECTION-REGULARITY`, establish a classical
spectrum, or prove physical positivity of a trajectory. The six-level
theoretical tail $q^6V$ is checked separately against $2^{-48}$; even a
passing tail does not replace actual inverse-chain residuals, represented
rounding, conditioning, effect-separation or continuation checks.

The checker binds 32 accepted small target graphs as regression subjects,
20 deeper mechanical target graphs (no borrowed C_OS numerical evidence),
and the prepared C_RG2b large source/target graphs. Each graph receives its
own exact certificate. No existing profile identity or acceptance changes.

Run from the repository root:

```sh
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest test_p9_crg2b_completion
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/p9_crg2b_completion.py --run --workers 12
```

`--check --workers 12` authenticates retained source/subject bindings and
recomputes all exact graph inequalities. It executes no native trajectories.

## Bounded result, 2026-10-30

All **54** exact graph checks pass: 32 accepted smaller graph shapes,
20 deep target shapes with 18–23 vertices, and the two cyclic large graphs.
This borrows only topology from the C_OS deep manifest; C_RG2b's coefficients,
auxiliary completion and equations own every bound.

| Graph | Vertices / edges | Uniform contraction upper | Six-level tail upper | Exact graph check time |
| --- | --- | --- | --- | --- |
| Large source | 100 / 400 | 0.007156 | 3.884e-19 | 2.81 s |
| Large prepared target | 107 / 407 | 0.004267 | 1.337e-20 | 2.94 s |

The table rounds bounds upward for display; the retained
[exact-rational record](./P9-CRG2b-CompletionFeasibility.json) owns the
inequalities. These are uniform bounds on the stated auxiliary chart, not
uniform bounds for a physical ten-step trajectory.

The [finite-section checker](../verification/p9_crg2b_section.py) preserves
six inverse levels, eighteen sweeps and terminal identity. It proposes
binary64 work, then uses fixed 192-bit Arb balls to certify every signed
state residual and full H-matrix residual. For $s_p=1-p>0$, its vertex solve

$$
u=\frac{J_0-tHB^T(s_pI+tBHB^T)^{-1}BJ_0}{s_p},
\qquad J=J_0+pu
$$

is algebraically identical to $(I+tHD-pI)u=J_0$. Small cyclic/noncommuting
tests compare it with an independently assembled full edge inverse. The
research policy is explicit: binary64 proposals followed by 192-bit Arb
certification, with no precision escalation or fallback. It does **not**
claim byte-identical proposals to the old edge-solve recipe or silently
replace that recipe under its existing identity. Adoption requires a newly
named numerical policy and corresponding native conformance.

The coupled residual estimate is unchanged. With
$a=\sum_{i=1}^6(1-A_X)^{-i}$ and
$d_c=1-(B_H+B_XaA_H)/2>0$, use

$$
e_H=\frac{r_H+B_Xa r_X/2}{d_c},\qquad
e_X=a(r_X+A_He_H),\qquad e_{\rm section}=e_H+q^6V.
$$

The first inverse state's infinite-section error includes
$M_{\rm inv}A_Hq^5V$ in addition to $e_X$. Geometry symmetry, actual star
support, the whole matrix ball, exact query and terminal identity are checked
before any residual. The certificate rejects stale intermediate geometry even
when its associated current is unchanged.

| Prepared query | Section error upper | Exact-real next-resource lower |
| --- | --- | --- |
| Source current | 1.094e-16 | 1.9841 |
| Source reset | 1.116e-16 | 1.9682 |
| Target current | 1.116e-16 | 1.0545e-13 |
| Target reset | 1.116e-16 | 1.0547e-13 |

Errors are rounded upward, lower bounds downward. Section tolerance remains
$2^{-48}\simeq3.553\times10^{-15}$. Positivity includes the full uniform
$J_H$ times section error, propagated through continuity, and outward Arb
evaluation. It concerns the **exact-real first step at these prepared
queries**, not represented native continuity, post-source-step transfers,
actual event admission, ten-step positivity or a trajectory tube.

The four independent jobs ran in parallel: proposals took 1.66–1.83 s,
certification 25.95–27.89 s per job. No native runtime timing is inferred.
The [lossless XZ record](./P9-CRG2b-SectionFeasibility.json.xz) retains every
inverse-state vector and nonzero upper-triangular H coordinate; decoding
restores exact symmetric binary64 matrices with zero omitted entries.
This saves about 2.6 MB uncompressed in about 0.7 MB. Failure pressure covers
wrong query/terminal, nonfinite work, stale H, duplicate sparse coordinates,
noncommutation, domain boundaries and inconclusive sufficient bounds.

```sh
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest test_p9_crg2b_completion test_p9_crg2b_section
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/p9_crg2b_section.py --check --workers 4
```

The second command re-evaluates retained equations and residuals, without
rerunning proposals or native trajectories. `--run --workers 4` creates a
fresh record only when the destination is absent.

## Authority and next adoption boundary

The [forensic traces](./P9-CRG2b-Authority.json) were obtained through the
side-tool API for the eight existing RG/lifecycle contracts and the C1 debt.
They retain source/edge references, claim classifications and trace digests.
They do not resolve this new graph-domain certificate as already accepted
authority. `GTRS-RG-DEBT-C1-SECTION-REGULARITY` remains narrowed and unresolved;
no derivative or classical-spectrum conclusion is made.

The proposed claim is bounded: these declared graphs admit the stated
completion-relative Lipschitz section, and the four prepared large queries
have certified finite research approximations. Before native adoption,
record the scoped extension in the authority chain and propagate the exact
conditions and new numerical policy through the paper/spec boundary. Then
implement against the retained oracle and pressure native staged reads,
physical continuation, both-role event admission and rollback. The original
tree17 authority, profile identities, rejection record and eight accepted
native families stay intact.

The proposed policy tuple for that adoption is concrete:

| Field | Proposed value |
| --- | --- |
| Extension | `grc9v4_c_rg2b_connected_signed_argument_completion_v1` |
| Containment certificate | `grc9v4_c_rg2b_connected_resolvent_global_certificate_v1` |
| Approximation | `grc9v4_c_rg2b_chain6_sweeps18_vertex_binary64_arb192_v1` |
| Error norm | existing `grc9v4_rg2b_hodge_induced_infinity_v1` |
| Section tolerance | unchanged `2^-48` |
| Deterministic work | six levels, eighteen sweeps, six residual evaluations |
| Failure | explicit rejection of unproved graph/domain/conditioning, nonfinite work or unresolved error; no fallback |

These identifiers are **proposed only**, not registered native policies.
The certificate consumes exact graph norms and reference-resolvent bounds,
the strict selector inequality and all containment/contraction inequalities
above; it has no size-only authorization. Native staged current reads retain
their own existing conditioning and numerical-policy checks. A fresh profile
identity must bind this tuple after adoption; old tree17 profiles keep their
original semantics and rejection behavior.
