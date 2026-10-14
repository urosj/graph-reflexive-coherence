# GRCV4 bounded numerical execution policy

This supplement specifies the opt-in production execution policy
`certified_arb_256_weighted_v1`. It implements the existing staged GRCV4
equations; it does not create a new constitutive law, realization, accepted
profile, public wire schema or specification release. `legacy_exact_v1` remains
the default. Older model versions are unchanged.

The [Phase 9 integration record](../implementation/corrections/GRCV4-CertifiedNumericalPolicy.md)
separates research evidence, production tests, measured scope and remaining work.

## Selection, scope and explicit failure

Select FLINT and this policy **before constructing declarations and owners**:

```python
from pygrc.models.grc_v4_numerics import (
    ExactBackend, exact_backend, NumericalPolicy, numerical_policy,
)

with exact_backend(ExactBackend.FLINT):
    with numerical_policy(NumericalPolicy.CERTIFIED_ARB_256):
        # Construct inputs and then GRCV4(inputs, ...) or a nine-port event owner.
        ...
```

Owners expose `numerical_policy` and retain their choice for steps, reads,
reset/rebase, state assignment and crossings. GRCV4 duplication preserves it;
the nine-port event receiver retains it for expansion. Matrix continuation facts
cannot cross policy/backend boundaries. No numerical evidence is scientific
state, and no rounded result may masquerade as an exact inverse cache fact.

Snapshots/checkpoints keep their existing scientific bytes. They do not serialize
this execution choice: load/replay selects the explicitly active policy, just as
it selects the exact scalar backend. To reproduce execution, callers must record
and reselect the policy, FLINT version and thread settings. An omitted policy
selects the documented legacy default; it is not a fallback after failure.

`CertificationInconclusive` is an **execution-level exception**. It means that
the selected proof, input representation or rounding certificate could not
resolve this case. It is not proof of a singular model, excessive true condition
number or inadmissible topology. It aborts before publication and does not invent
a scientific failure receipt. Existing native residual failures retain their
existing typed behavior. Neither path changes tolerances, retries at higher
precision, performs another OS iteration, or silently invokes legacy elimination.

## Exact replacements

Let RN denote binary64 round-to-nearest, ties-to-even, with native canonical
positive zero. All matrices below use the actual declared/staged coefficients,
not a nearby ideal matrix substituted into the physical equations.

| Site | Previous computation | Selected computation | Required condition |
| --- | --- | --- | --- |
| Rounded solve | Exact inverse X=A^-1, then RN(XB) | Certified RN of the exact solution of AY=B | Exact input representation and unique rounding; unchanged residual checks |
| General conditioning | Exact Gram PSD certification | Exact diagonal ratio or scalar-center norm bound | Positive proved singular-value lower bound and bound within declared limit |
| C resolvent conditioning | Generic exact conditioning | Exact Gram comparison plus perturbation bound | Positive diagonal vertex metric, nonnegative tau, positive comparison scale, bounded perturbation |
| Hodge positivity | Exact integer Sylvester elimination | Exact positive strict diagonal-dominance certificate | Symmetric matrix and positive row margins |
| C mathematical regularity | Construct/discard inverse of regularity block | Positive-Hodge similarity argument | beta<1, tau>=0 and positive H0/H |
| C represented current-block regularity | Construct/discard its inverse | Its actual conditioning certificate proves nonsingularity | Positive lower singular-value bound for that represented block |
| OS split admission | Exact inertia of tD-R and tD+R | Exact weighted row-sum norm bound | Symmetric R, positive diagonal D, bound<=t |

### 1. Rounded solves and arithmetic staging

For a coefficient matrix A and RHS matrix B, the required output remains

$$
Y_{64}=\operatorname{RN}(A^{-1}B).
$$

The selected route is fixed by exact matrix structure **before solving**:

- A diagonal matrix uses exact scalar division, then certified rounding.
- Every non-diagonal matrix uses one Arb LU solve at **256 bits**. Each input
  coefficient must be represented exactly at this precision. An unresolved LU
  or nonfinite enclosure is inconclusive; approximate mode is forbidden.

For each enclosed exact solution entry y in [l,u], endpoints propose a finite
binary64 value v. Acceptance additionally requires exact containment of the
entire closed interval in v's nearest/even rounding cell. Endpoints at neighboring
midpoints belong to v only if its significand is even. The canonical-zero cell
is [-2^-1075,2^-1075]. Overflow cannot become an admitted output entry. Thus a
floating conversion error cannot itself certify the answer.

Arb enclosure is a proof of the rounded exact solution, not a materialized exact
rational inverse. `inverse()` and `solve_positive()` retain their exact-rational
contracts. Existing selector/descriptor callers of those APIs remain exact and
can still be expensive; this is a declared remaining role, not fallback.

Every RHS still passes the existing exact residual test:

$$
\|AY_{64,j}-B_j\|_2
\le a_{\mathrm{tol}}+r_{\mathrm{tol}}\max(1,\|B_j\|_2).
$$

Conditioning is certified before solving. No equation tolerance is changed.
In particular, if a caller materializes RN(H^-1) and later applies that rounded
matrix, those **two stages remain separate**. Directly computing RN(H^-1 j)
instead would generally change results and is not this policy.

### 2. Generic conditioning

The previous general check forms the exact normalized Gram matrix

$$
c=\max_{ij}|A_{ij}|,\qquad G=(A/c)^T(A/c),
\qquad G-aI\succeq0,\quad bI-G\succeq0,
\quad a>0,\quad b/a\le\kappa_{\rm limit}^2.
$$

For a non-diagonal Gram matrix of dimension greater than two, floating SVD
only proposes a,b; exact PSD elimination certifies both inequalities. The
diagonal case uses min/max diagonal G. For a non-diagonal 2-by-2 Gram, with
T=tr(G), d=(G00-G11)^2+4G01^2 and K=kappa_limit^2, the exact decision requires
K>=1, det(G)>0 and (K-1)^2 T^2 >= (K+1)^2 d. The new policy replaces these Gram
constructions/PSD decisions with the following singular-value bounds, not
with unchecked floating SVD endpoints.

For nonempty diagonal A, compute exact singular extrema

$$
\ell=\min_i|A_{ii}|,\qquad u=\max_i|A_{ii}|.
$$

For other non-resolvent matrices, fix s=A_00, require s nonzero, and define

$$
E=A/s-I,\qquad d=\max(\|E\|_1,\|E\|_\infty),
\qquad \ell=|s|(1-d),\quad u=|s|(1+d).
$$

The inequalities ||E||2<=sqrt(||E||1 ||E||infinity)<=d give these singular-value
bounds. Certify only when ell>0 and u<=kappa_limit ell, retaining (u/ell)^2 as
the condition bound. s is a fixed coefficient-derived rule, not a scale search
after failure. The new helper defines condition bound one on an empty system;
this convention alone grants no empty-graph lifecycle admission. A valid matrix outside
this sufficient domain is inconclusive, not singular. The research probe used
role-specific scalar centers; this production rule is separately tested.

### 3. C resolvent conditioning

For actual represented resolvent block A, incidence B, positive diagonal vertex
metric M=diag(mu), retained Hodge H and tau>=0, fix h=max_i H_ii>0 and form

$$
A_0=I+\tau h B^T M^{-1}B,\qquad E=A-A_0,
\qquad e=\max(\|E\|_1,\|E\|_\infty).
$$

All these operations are exact rationals; inverse M here is diagonal division.
A0 is symmetric positive definite, with smallest eigenvalue at least one. Hence

$$
\ell=1-e,\qquad
u=1+\frac{\tau h\|B\|_1\|B\|_\infty}{\min_i\mu_i}+e.
$$

Apply the same positive-lower-bound/condition-limit decision as above. The
perturbation includes **all non-scalar Hodge effects and represented assembly
error**. H is not assumed scalar, reference edge weights need not be one, and
no constant-selector assumption is made. Large perturbations may leave this
certificate inconclusive. It neither substitutes A0 into the solve nor changes
the selector, its cutoff/path guards, or the current law.

### 4. Hodge positivity

The previous exact Sylvester test requires all leading principal minors
det(H[1:k,1:k])>0, calculated by fraction-free integer elimination after exact
positive dyadic scaling. The selected replacement does not calculate them.

For each actual symmetric Hodge operand H, check exactly

$$
H_{ii}>\sum_{j\ne i}|H_{ij}|\quad\text{for every }i.
$$

Strict diagonal dominance with positive diagonal implies positive definiteness.
This is the weighted extension of the earlier fixed identity-center proof.
The exact unrounded affine matrix and its staged represented matrix are checked
**separately**, as before. An SPD matrix outside this sufficient domain is
inconclusive. Symmetry/typing and finite-value validation remain mandatory.

### 5. C regularity: mathematical and represented blocks remain distinct

Write beta=zeta_C chi_C and

$$
T=(1-\beta)I+\tau_C B^T H_0^{-1}B H.
$$

If beta<1, tau_C>=0, H0 is positive diagonal and H is SPD, then T is similar to

$$
(1-\beta)I+\tau_C H^{1/2}B^T H_0^{-1}BH^{1/2},
$$

which is SPD. No square root or inverse of T is computed. The selected Hodge
proof checks the SPD premise; outside this positive-similarity domain the policy
stops as inconclusive, even if a different exact argument could prove regularity.

This does **not** admit the separately rounded physical current block. That
actual block still gets its own conditioning certificate and solved-current
residual checks. Its inverse formerly existed only as a guard; the proved
positive singular-value lower bound now supplies that guard.

More explicitly, with the already staged physical flux response F64, this is

$$
L_{64}=\operatorname{RN}(I-\beta F_{64}),\qquad
J_{64}=\operatorname{RN}(L_{64}^{-1}J_{0,64}).
$$

Constructing/discarding L64^-1 is removed; certifying the actual L64 and solving
its actual RHS is not. F64's existing resolvent/identification materializations
remain unchanged; neither T nor an ideal unrounded L replaces L64.

### 6. Weighted OS split

For the exact difference R of the two staged Hodge matrices and declared positive
diagonal reference D=diag(w), compute

$$
b=\max_i\frac{\sum_j|R_{ij}|}{w_i}.
$$

Since symmetric S=D^-1/2 R D^-1/2 is similar to D^-1 R,

$$
\|S\|_2=\rho(D^{-1}R)\le\|D^{-1}R\|_\infty=b.
$$

b<=t certifies the same split condition previously decided by

$$
tD-R\succeq0\quad\text{and}\quad tD+R\succeq0
\quad\Longleftrightarrow\quad
\|D^{-1/2}RD^{-1/2}\|_2\le t.
$$

Equality is allowed; an exact subnormal defect is
not rounded away. b>t is inconclusive, not rejection. The displayed residual
may be unavailable on overflow without invalidating its exact certificate.
The method applies to any topology with positive diagonal reference weights;
it is shared by A_OS and C_OS, not an extra step in the other realizations.

## Scope and remaining costs

Candidate A's direct diagonal physical-current formula, singularity and condition
tests are unchanged. A shares the rounded flat-solve API, Hodge validation and OS
split certificate with C; it is not rewritten as a C current-block solve.
Shared solve users in other realizations can select this policy, but existence
of a code path is not all-family conformance evidence.

Exact selector/descriptor computations, selector-path certification, nonlinear
CI/RG2b obligations, and whole-lifecycle resource/charge/readmission requirements
remain. Native integration does not close P9-8.4g or authorize 8.4h. Success under
the new proof domain preserves staged values; inability to certify remains
visible rather than triggering a costly alternate execution.
