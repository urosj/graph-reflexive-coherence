# D8-B Coupled Architecture-Local Continuation Analysis

**Record:** `GRC9V4-CD-D8B-CI-v1`  
**Status:** accepted bounded  
**Decision digest:** `53ed6d6ee616ab42c59ce6dabb6bc106a595f5c70ad1acaedc445c7fa73a5b7f`  
**Scope:** coupled/implicit Candidate A and Candidate C, analyzed separately

## Decision

D8-B now has a complete design-level operator contract for each accepted
coupled/implicit architecture:

```text
Candidate A:
  committed state       = (C, W_A)
  same-step root        = (J_A, h_A)
  structural domain     = C at fixed W_A

Candidate C:
  committed state       = C
  same-step root        = (J_C, h_C)
  structural domain     = C with derived T_C tangent
```

For both architectures the accepted root equations determine:

```text
full implicit first and second derivatives
charge-parametric architecture-local constrained structural second variation
complete-step Jacobian
direct Read-Back derivative
spatial graph operator
projector and representation transport rules
nonnormality and stability tests
```

This is a real completion of the D8-B **design surface**. It is not a numerical
formed-branch spectrum. No V4 runtime branch, normalized functional parameter
set, or numerical root derivative has been instantiated. Therefore this record
does not emit `alpha`, `beta`, `gamma`, `mu`, or `lambda` values and does not
classify either architecture as stable, marginal, or unstable.

Candidate A and Candidate C are not compared or ranked. Comparative D8-B is
still blocked by the unpressured realization families and the absence of a
common instantiated reference space.

## Why A Root And C Root Are Enough For The Derivative Surface

For either architecture, write the accepted coupled system as

```text
F_a(Y_a; X_a) = 0
Y_a = (J_a, h_a)
```

on its declared smooth local chart. Let

```text
B_a = D_Y F_a.
```

The accepted successor already establishes a `C1` local branch through
invertibility of `B_a` at the reference point. That is enough for the first
derivative,

```text
D_X Y_a[u] = -B_a^-1 D_X F_a[u].
```

but not by itself for a classical Hessian. D8-B therefore restricts the
structural analysis to declared `C2` subcharts: A is fixed-topology,
fixed-boundary, floor-inactive, and `G_W`-smooth; C additionally has fixed
selector rank and a strict selector gap. On those subcharts, the second
derivative is not obtained by differentiating a cached or lagged geometry. It
is the full implicit derivative:

```text
D_X^2 Y_a[u,v] = -B_a^-1 (
    D_XX^2 F_a[u,v]
  + D_XY^2 F_a[u, D_X Y_a[v]]
  + D_YX^2 F_a[D_X Y_a[u], v]
  + D_YY^2 F_a[D_X Y_a[u], D_X Y_a[v]]
).
```

This is the decisive D8-B rederivation. The D8-A lagged pullbacks are no
longer architecture-final because `J` and `h` are jointly solved. The equations
above retain the changed slaving relation without promoting either root
variable into persistent state.

Solver convergence is not evidence that `B_a` is regular. At a singular block,
selector-rank crossing, topology boundary, or nonsmooth active-set crossing,
the classical derivative is blocked rather than reported as zero or merely
unconverged.

## Structural Continuation: `alpha`

The architecture-local reduced functional has the form

```text
F_struct,a^red(C)
  = P_struct(C, h_a(C); fixed candidate context)
  - eta_a [Q(C, h_a(C)) - Q0].
```

Write the unslaved constrained integrand as

```text
L_a(C,h) = P_struct(C,h) - eta_a [Q(C,h)-Q0].
```

The root supplies `h_a(C)` and its first and second derivatives. The complete
second variation of `L_a(C,h_a(C))` therefore contains:

```text
D_CC^2 L[u,v]
+ D_Ch^2 L[u, D h[v]]
+ D_hC^2 L[D h[u], v]
+ D_hh^2 L[D h[u], D h[v]]
+ D_h L[D^2 h[u,v]].
```

This is already the constrained Lagrangian second variation. Constraint
curvature is the `-eta_a D^2 Q` part of `D^2 L`; measure dependence enters
through the `h`/`H0` dependence of `P_struct` and `Q`; and any explicit
boundary term remains inside the functional while boundary/support conditions
restrict the domain. None is appended a second time. Projector or tangent
transport belongs to moving-branch comparison, not to the additive local
Hessian at one formed state.

For the instantiated graph field functional used by this design basis,

```text
P_G(C,H)
  = (kappa_C/2) (d0 C)^T H (d0 C)
  + sum_i H0_ii W_pot(C_i),
```

the field contribution to the full second variation is explicitly

```text
Q_a[u,v]
  = kappa_C (d0 u)^T H_a (d0 v)
  + u^T H0 Diag(W_pot''(C*)) v
  + kappa_C (d0 u)^T H_a'[v] e*
  + kappa_C (d0 v)^T H_a'[u] e*
  + (kappa_C/2) e*^T H_a''[u,v] e*,

e* = d0 C*.
```

This remains only the graph-field contribution to the normalized constrained
second variation. The remaining contributions are obtained by differentiating
the full `L_a`; they are not appended as generic extra terms.

On the declared admissible tangent `V_a`, the closed bilinear form is
represented by `C_struct,a` through

```text
Q_struct,a[u,v] = <u, C_struct,a v>_a.
```

Only then is

```text
C_struct,a u_n = alpha_n u_n
```

an `alpha` statement.

The tangent and projector must be built from the conserved quantity of the
**complete candidate transition**. Neither `H0` nor an analysis inner product
defines that charge by itself. Event-free fixed-topology GRC9V3 continuity
historically preserves the unweighted node sum before later budget, boundary,
and event stages; that is a source-backed predecessor fact, not an automatic
V4 charge selection. Once the charge is fixed, a tangent basis `Z_a` solves

```text
Z_a^T K_a Z_a xi_n
  = alpha_n Z_a^T H0 Z_a xi_n
```

after protected null directions are removed.

The exact D8-A direct field term remains one term in this expression:

```text
kappa_C (d0 u)^T delta_H1_form (d0 v).
```

Its nonzero finite receipts prove a nonempty direct metric-response subdomain.
They do not determine the sign or nonzero value of the complete Hessian after
the induced-geometry, constraint, and second-order terms are included.

### Candidate A

Candidate A remains a conditional structural problem:

```text
structural coordinate = delta_C
fixed parameter       = W_A*
delta_W_A             = 0 during structural variation
```

`delta_J_A` and `delta_h_A` are derived from the full implicit root. The
rederived chain includes the reference-relative `Delta_0(h)` correction,
`J0_A`, the in-root refresh of `W_hat_A`, `q_A`, the read current, `Delta_K4_A`,
and the geometry profile. D8-B does not manufacture an independent
`alpha(W_A)`.

### Candidate C

Candidate C remains C-only. Its retained sector tangent is derived:

```text
delta_T_C
  = P_M delta_C
  + (D_C P_M[delta_C] + D_h P_M[delta_h_C]) C*.
```

The second variation also requires all second selector derivatives and the
second implicit geometry derivative. The full chain retains

```text
h -> P_M -> T_C -> H_M -> I_4M -> Rhat_C,M -> G_J
```

and, critically, the `(delta G_J) J` contribution. `T_C` is not promoted to an
independent structural coordinate and receives no separate alpha spectrum.

### Why There Are No Numeric Alpha Values

The design records do not instantiate a V4 constrained critical branch with
the complete `P_struct`, constraint normalization, functional coefficients,
and perturbation metric. A raw matrix assembled from only the graph-Hodge term
would therefore be a partial operator mislabeled as the continuation Hessian.

D8-B closes the architecture-local **formula and domain**. Numerical alpha
classification remains a formed-branch obligation, conditionally pre-D10 if
architecture selection is made to require it, otherwise post-specification
implementation verification.

## Complete Temporal Transition: `mu` And `gamma`

The primary temporal object for these discrete architectures is the derivative
of the complete committed-state map:

```text
M_a = D_X Phi_a.
```

Its eigenvalues are multipliers `mu`. A continuous rate

```text
gamma = -log(mu) / Delta_t
```

is valid only with a declared clock and logarithm branch, or when a separate
continuous generator has been derived. `(I-M)/Delta_t` is not automatically a
normative generator.

### Candidate A Complete Step

After the coupled root:

```text
delta_C+ = delta_C - Delta_t B_ref delta_J_A
           + D boundary_A[delta_X].
```

The writer derivative is

```text
delta_W+
  = a_A Diag(W+/W_A) delta_W_A
  + (1-a_A) Diag(W+/W_drv,A)
      D G_W[delta_C+, delta_J_A].
```

All differential inputs to `G_W` are rebuilt from post-continuity `C+` and the
authoritative root current. Pre-continuity caches are inadmissible. Geometry
has no direct writer authority; it affects the writer through the accepted
current and continuity chain.

This yields the exact formal map

```text
M_A = D_(C,W_A) (C+, W_A+).
```

Writing `J_C = D_C J_A` and `J_W = D_W J_A`, the block construction is

```text
P_C = I - Delta_t B_ref J_C + D_C boundary_A
P_W =   - Delta_t B_ref J_W + D_W boundary_A

D_C W_drv = G_C,W P_C + G_J,W J_C
D_W W_drv = G_C,W P_W + G_J,W J_W

M_A = [[P_C, P_W],
       [D_C W+, D_W W+]].
```

The local coordinate `omega = log(W_A/W_ref)` is useful on the positive
mobility chart and is similarity-equivalent at a fixed point. On a moving
branch its pre- and post-step coordinate transports remain distinct.

### Candidate C Complete Step

Candidate C commits only `C+`, so

```text
M_C
  = I
  - Delta_t B_ref P_J (-B_C^-1 D_C F_C)
  + D boundary_C.
```

`T_C`, `J_C`, and `h_C` remain same-step derived variables. Giving any of them
an independent temporal coordinate would change Candidate C's ontology.

### Stability Boundary

For an instantiated branch, asymptotic linear step stability requires

```text
rho(M_a) < 1
```

on unprotected admissible modes. This is not sufficient to control transient
growth for a nonnormal map. D8-B therefore also requires singular values,
conditioned invariant subspaces, Schur or equivalent stable subspace
representations, resolvent or pseudospectral checks near the boundary, and
finite-horizon norms of powers of `M_a`.

The local implicit-function theorem proves algebraic well-posedness of the
same-step root. It does not prove temporal stability of `M_a`.

Nor does one fixed-point multiplier spectrum describe a moving formed branch.
If `M_k : T_(X_k) -> T_(X_(k+1))`, its fixed-reference representative is

```text
M_tilde_k = U_(k+1 -> 0) M_k U_(0 -> k).
```

The reference-space cocycle is

```text
M_tilde_(n:0) = M_tilde_(n-1) ... M_tilde_1 M_tilde_0.
```

Equivalently, compose the native-space maps first and transport only the two
endpoints. Using `U_(k -> 0)` on the output is type-incorrect because the
output belongs to `T_(X_(k+1))`.

## Direct Read-Back: `beta`

The direct frozen-state Read-Back operator is

```text
B_rb,a = zeta_a D_J j_a.
```

It is useful to separate the intrinsic direct response

```text
R_dir,a = D_J j_a,       eigenvalue r_a
```

from the enacted Read-Back gain

```text
B_rb,a = zeta_a R_dir,a, eigenvalue beta_a = zeta_a r_a.
```

The alternative ungained formulas are therefore valid as `r_a`, not as
`beta_a`. This is one current subloop inside the complete root and transition.
It is not the complete-step multiplier and not structural stiffness.

`beta_n` remains an eigenvalue in `Spec(B_rb,a)` even when the operator is
nonnormal or defective. In that case isolated spectral clusters and Riesz
projectors replace fragile individual eigenvectors. Singular values
`sigma_rb,n = sigma_n(B_rb,a)` are reported separately as direct response
amplification; they are not renamed `beta`.

### Candidate A

At fixed committed state and fixed same-step geometry reference,

```text
B_rb,A = zeta_A chi_A Diag(q_A*).
```

Thus `r_A,e = chi_A q_A,e` and
`beta_A,e = zeta_A chi_A q_A,e`.

The total dependence of `q_A` on geometry and baseline current remains in the
full root block and `M_A`; it is not double-counted inside the direct beta
operator.

### Candidate C

Let

```text
Q_C = I_4M G_J.
```

Then

```text
B_rb,C   = zeta_C chi_C Q_C^-1 Rhat_C,M Q_C,
B_rb,C,M = zeta_C chi_C Rhat_C,M.
```

These operators are similar and therefore have the same eigenvalues. Their
Euclidean singular values and apparent nonnormality need not agree. Response
norms use the retained metric `H1_M` or its explicit physical pullback
`Q_C^T H1_M Q_C`. The physical operator is self-adjoint in that pulled-back
metric when `Rhat_C,M` is `H1_M`-self-adjoint; this is not an unweighted
Euclidean self-adjointness claim. If `lambda_M,m` is an eigenvalue of the
retained one-form Hodge operator, then

```text
r_C,m    = chi_C / (1 + tau_C lambda_M,m),
beta_C,m = zeta_C chi_C / (1 + tau_C lambda_M,m).
```

The kinetic threshold `1 in Spec(B_rb,a)` blocks the frozen direct current
inverse. It does not by itself establish `alpha = 0`, `|mu| = 1`, basin birth,
or topology change.

## Spatial Scale: `lambda`

For either architecture the positive graph spatial operator at its own formed
geometry is

```text
L_sp,a = Delta_0(h_a*)
       = H0_ref^-1 B_ref H1_form(h_a*) B_ref^T.
```

The weighted generalized eigenproblem is

```text
B_ref H1_form B_ref^T phi_n
  = lambda_n H0_ref phi_n.
```

This lives on the node-field domain with declared boundary and constant or
conservation-mode handling. Candidate C's internal one-form operator
`Delta_1,M` belongs to its retained response and has its own `lambda_M`
spectrum. It is not the field-level `lambda` operator.

`lambda` describes spatial scale. It cannot be relabeled as `alpha`, `beta`,
`gamma`, or `mu`.

## Projectors, Moving Spaces, And Covariance

D8-B compares invariant subspaces only through isolated cluster projectors.
Sorted eigenvalue indices are not cross-operator identities.

The four projector families live in different spaces:

```text
structural projector -> constrained C tangent with structural metric
temporal projector   -> committed-state tangent
Read-Back projector  -> current/form response space
spatial projector    -> node-field spatial space
```

Candidate A makes the domain mismatch explicit: its structural object lives on
`delta_C` at fixed `W_A`, while its complete temporal map lives on
`(delta_C, delta_W_A)`. A comparison requires a declared injection/projection;
there is no identity map by notation.

Candidate C uses C coordinates for both structural and temporal objects, but
the metrics and operator meanings still differ. Shared coordinates do not make
the projectors identical.

Across a smooth tracked branch, a reference transport must carry:

```text
measure weight
cochain/fiber metric
constraint tangent
candidate representation
isolated cluster projector
```

before any mode or subspace comparison. Node relabeling acts by similarity on
operators and congruence on forms. Edge reorientation has its own signed
cochain transformation. Neither analysis projector becomes runtime state.

Cross-rank and cross-topology transport remain blocked until D9 or another
explicit interspace contract.

## Conditioning, Nonnormality, And Complete-Chain Witnesses

After an architecture is instantiated, nonnormality is measured in a declared
analysis metric:

```text
M^dagger = W_analysis^-1 M^T W_analysis
commutator = ||M^dagger M - M M^dagger||_W
G_H = max_(0 <= k <= H) ||M^k||_W
```

with the corresponding transported cocycle norm on a moving branch. Candidate
C has the natural committed-state metric `H0`. Candidate A has a natural
`log(W_A/W_ref)` coordinate, but the relative weight between `C` and `log W_A`
is not fixed by the current sources. Absolute A nonnormality magnitudes,
cross-block angles, and cross-architecture temporal comparisons remain blocked
until that metric is declared.

The existing direct-field receipts also do not prove that the complete
transition consumes the geometry channel. For either architecture the exact
parameter sensitivity is

```text
Y_kappa = -B_a^-1 F_kappa,
partial_kappa Phi_a = Phi_Y Y_kappa + Phi_kappa.
```

A future preregistered witness must show a nonzero complete-transition
sensitivity or a matched enabled-versus-consumer-off derivative difference.
No direction may be selected after seeing the result.

The local regularity certificate is likewise quantitative rather than a solver
success flag. With reference block `B0_a`,

```text
eta_a = ||B0_a^-1 (B_a - B0_a)|| < 1
```

implies

```text
||B_a^-1|| <= ||B0_a^-1|| / (1 - eta_a).
```

A Lipschitz bound on `B_a-B0_a` can turn this into a conservative local radius.
No numerical radius is instantiated in D8-B.

These operations belong to a pure analysis layer: it may consume a candidate
state and coupled root and emit derivatives, spectra, projectors, conditioning,
and controls. It may not mutate the transition, become causal state, or feed an
analysis-selected projector back into runtime. D8-B observes the complete
coupled V4 step; it does not become part of that step.

## B1 And B2 Consumption

B1 and B2 remain historical method and control sources, not V4 numerical
evidence.

```text
B1 GRV3 causal-state/stratum audit:
  V4-specific adaptation required.

B1 complete-step finite differences:
  odd/even, step-size, residual-over-h, and decoder audits reusable after
  implementation; V3 matrices are not reusable.

B1 frozen/full comparison:
  requires architecture-specific V4 ablations.

B1 retention and return probes:
  post-implementation and candidate-specific; C may not be given an
  independent retained carrier merely to mirror A.

B1 GRV7 cluster/projector rules:
  method reused; V3 spectra and thresholds inapplicable as V4 evidence.

B2 active nulls:
  provenance and relabel control shapes remain useful.

B2 empty unchanged-runtime search:
  legacy fact only; it neither rejects nor selects a V4 architecture.
```

Endpoint coverage of the old V3 pathways is not evidence for the new coupled
crossing or complete V4 transition.

## Debt Result

D8-B consumes the complete predecessor live union:

```text
10 immediate GTRS-CI debts
23 transitive D8-A debts
= 33 predecessor debts with explicit dispositions
```

The equation-level A/C structural rederivation, operator separation, and local
representation contracts are closed. The live union becomes:

```text
7 carried immediate debts
20 carried transitive debts
7 current D8-B debts
= 34 live debts
```

The seven current debts preserve:

```text
A formed-branch numeric alpha and structural stability
C formed-branch numeric alpha and structural stability
A complete-step numeric multipliers and temporal stability
C complete-step numeric multipliers and temporal stability
cross-architecture reference-space and comparison closure
complete-step conserved-charge and structural-projector selection
Candidate A complete-state analysis-metric selection
```

The first four are conditionally pre-D10: if architecture selection is made to
require numerical stability before specification, they become blockers.
Otherwise they remain explicit post-specification implementation-verification
obligations. Comparative reference-space closure is a D10 blocker unless D10
adopts an explicit noncomparative disposition. The conserved-charge/projector
debt is a D10 blocker because the normative complete-step accounting cannot
leave the structural tangent ambiguous. The A metric debt becomes pre-D10 only
if architecture selection consumes absolute nonnormality or cross-architecture
temporal magnitudes.

The earlier A and C complete-chain nonannihilation witnesses, quantitative IFT
margins, global-root boundaries, topology/event boundaries, and remaining
realization-family pressure are still carried. Direct-field visibility does
not silently close them.

## Claim Boundary

D8-B supports:

```text
exact architecture-local A and C implicit derivative surfaces
declared C2 subcharts required for classical second variation
charge-parametric architecture-local second-variation construction, complete
once the D9 charge/tangent contract is frozen
exact complete-step Jacobian construction
typed direct Read-Back operators and beta semantics
intrinsic response r_a separated from enacted gain beta_a = zeta_a r_a
typed spatial operators and lambda semantics
cluster/projector/transport/covariance contracts
nonnormality and stability test contracts
B1/B2 discriminator applicability map
```

D8-B does not support:

```text
numeric alpha, beta, gamma, mu, or lambda values
formed V4 branch evidence
nonzero complete transition-chain sensitivity
structural or temporal stability
global root uniqueness
cross-rank or cross-topology continuation
cross-candidate or cross-family comparison
candidate ranking or selection
runtime implementation
normative GRC9V4 specification
```

The bounded result is therefore:

> The accepted coupled/implicit A and C architectures are analytically closed
> enough to define every architecture-local D8-B operator and falsification
> surface, parametrically in the still-unfrozen complete-step charge. They are
> not yet numerically instantiated strongly enough to assign continuation
> spectra or stability classifications.
