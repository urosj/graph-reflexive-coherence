# GRC-v4 connected Candidate-C RG2b completion addendum

This addendum records the bounded implementation selection authorized on 2026-10-30.
It supplements the substrate paper without changing its existing RG2b or C1 ceilings.
The contract is `P9-EC-C-RG2B-CONNECTED-COMPLETION`; its conditional claim remains
subject to every hypothesis below. The native realization needs separate conformance.

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


The selected numerical recipe uses six inverse levels and eighteen binary64
sweeps, with a vertex-reduced proposal and fixed 192-bit Arb residual certification.
It has its own identity; it is not the old tree17 binary64/160-bit implementation.
The complete formulas and bounded evidence are retained in the Phase 9 derivation.
Physical resources are never clipped, and no precision escalation or fallback is allowed.
Native acceptance, C1 regularity, spectra and arbitrary-graph positive continuation
are not consequences of this addendum.
