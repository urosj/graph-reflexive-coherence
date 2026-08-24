# Geometry-Temporal Realization Successor: Coupled/Implicit Family

**Record:** `GRC9V4-GTRS-CI-v1`  
**Status:** `accepted_bounded`  
**Decision digest:** `a0292d35d3dfc18e6386a78c26ae9bc2a4b6de9f31e505cf67edf7c094aea3a3`  
**Runtime or `src/` changed:** `false`

## Purpose

This is the first concrete family pass in the named
`GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR`. It is not D8-B and it does
not repeat D8-A. D8-A established which structural objects and target tests a
realization must preserve or rederive. This pass asks whether generated
geometry can participate in a complete constitutive step.

The first family is coupled/implicit:

```text
solve authoritative current and generated geometry together;
commit the candidate transition only after the joint root is regular.
```

This family is first because accepted current closures provide regular
reference points and the core effective loop permits same-solve dependence.
It is not preferred over operator-split, persistent-carrier, or reconstructed
realizations. Those family pressures remain open.

## Sources And Exact Boundary

The result binds D4, D6-v2, D7, D7-v2, D7G-v2, the D7G-post-v2 Hodge
correction, and D8-A by exact decision digest and file SHA-256. D4 and D7 are
consumed directly because the A completion depends on their accepted
geometry/mobility ownership, baseline current, pre-read target, and writer
contracts. Later summaries are orientation only.

The accepted typing remains:

```text
physical current:     J_flux and j_flux
lowered current form: j_flat = G_J j_flux
structural input:     A_star(j_flat), a typed quadratic lift
structural adapter:   candidate-specific iota_a
shared causal gain:   zeta_a, applied once outside each causal use
field Hodge:          H1_form
current flat metric:  G_J
transport mobility:   M4
```

`chi_a` gates the explicit read current. `zeta_a` gates its contribution to
the total current and its structural use. `zeta_a` is not inserted into
`j_flat` before the quadratic lift because that would create a spurious
`zeta_a^2` structural term.

## Common Coupled Contract

For candidate `a`, the algebraic unknown is

```text
Y_a = (J_a,flux, h_a).
```

On the admitted fixed stratum, `h_a` denotes independent symmetric
`H1_form` coordinates in the declared oriented-edge basis. Incidence,
boundary, live order, and the graph stratum are fixed. Candidate operators,
metric identifications, mobility, selectors, and response maps are derived or
candidate-owned; they are not additional root coordinates.

The committed candidate state, graph context, and parameters determine

```text
F_a(Y_a; X_a,k) = 0.
```

Only the unique local branch connected to the accepted `kappa_H = 0`
reference is admitted. `J` and `h` are same-step algebraic variables, not new
persistent state. Domain loss, singular or underconditioned full blocks,
failed residuals, nonfinite values, or departure from the local chart commit
nothing. Solver convergence alone is not regularity evidence.

## Candidate C

### Corrected Typed System

Candidate C has the selector and retained-response chain

```text
h
 -> P_M(h)
 -> T_C = P_M(h) C_k
 -> H_M(T_C,h)
 -> I_4M(T_C,h)
 -> Rhat_C,M(T_C,h).
```

The explicit `T_C` argument of `I_4M` is load-bearing. It prevents a later
derivative from omitting

```text
h -> P_M -> T_C -> H_M -> I_4M.
```

Freeze the ungated resolvent

```text
Rhat_C,M(T_C,h)
  = (I + tau_C Delta_1,M(T_C,h))^-1.
```

Historical D5-v2 notation included `chi_C` inside `R_C,M`. This successor uses
the accepted D6/D7 ungated convention explicitly so `chi_C` cannot be applied
twice. Separate intrinsic response from causal read:

```text
r_C^flat(J,h)
  = I_4M(T_C,h)^-1
    Rhat_C,M(T_C,h)
    I_4M(T_C,h)
    G_J(h) J

j_C^flat(J,h) = chi_C r_C^flat(J,h)

j_C,flux(J,h) = G_J(h)^-1 j_C^flat(J,h).
```

The structural branch is

```text
Delta K4_C(J,h)
  = zeta_C iota_C(A_star(j_C^flat(J,h))).
```

`iota_C` excludes the accepted shared `zeta_C`; the gain is an external
multiplier, so no linearity or homogeneity of `iota_C` is assumed. The coupled
root is

```text
F_J,C
  = J
    - J0_C(C_k,T_C,h,context)
    - zeta_C j_C,flux(J,h)
  = 0

F_h,C
  = h
    - H_profile(
        K4_base + Delta K4_C(J,h),
        h4_ref,
        context)
  = 0.
```

The two switch contracts are exact:

```text
chi_C = 0
  -> j_C^flat = j_C,flux = 0
  -> no j-derived structural increment;

zeta_C = 0
  -> J = J0_C
  -> no j-derived structural increment.
```

An ungated intrinsic `r_C^flat` may remain diagnostic when `zeta_C = 0`; it
has no causal consumer. After a regular root, physical `J` enters continuity
and only `C_(k+1)` commits. Geometry, current, selectors, and response objects
remain same-step derived surfaces.

### Reference Regularity Through Similarity

At `kappa_H = 0`, `h = h4_ref`. The Hodge correction means the physical
current block is not literally the old retained-coordinate D6-v2 matrix.
Define

```text
Q_C,ref
  = I_4M(T_C,ref,h4_ref) G_J(h4_ref)

Rhat_C,flux,ref
  = Q_C,ref^-1 Rhat_C,M,ref Q_C,ref

L_C,flux,ref
  = I - zeta_C chi_C Rhat_C,flux,ref
  = Q_C,ref^-1
    (I - zeta_C chi_C Rhat_C,M,ref)
    Q_C,ref.
```

Exact invertibility transfers by similarity from the accepted retained D6-v2
block. The old physical singular-value margin does not transfer unchanged.
Robust physical conditioning additionally requires finite `cond(Q_C,ref)`;
under the retained contraction bound, the available inverse estimate is no
stronger than

```text
||L_C,flux,ref^-1||
  <= cond(Q_C,ref) / (1 - zeta_bar_C).
```

The reference joint Jacobian is

```text
[ L_C,flux,ref  B_C ]
[       0        I  ].
```

It is invertible on the declared smooth SPD, fixed-rank, fixed-topology domain.
The implicit function theorem therefore gives some `epsilon > 0` and a unique
local smooth coupled branch for `|kappa_H| < epsilon`. This is an existential
local result, not a numeric radius, global branch, or stability result.

### Full C Derivative

Away from the reference, the authoritative regularity object is

```text
B_full,C = [ A_JJ  A_Jh ]
           [ A_hJ  A_hh ].
```

Its blocks retain `chi_C` inside the read current:

```text
A_JJ = I - zeta_C D_J j_C,flux

A_Jh = -D_h J0_C - zeta_C D_h j_C,flux

A_hJ = -D_K H_profile D_jflat K4_C D_J j_C^flat

A_hh = I - D_K H_profile D_jflat K4_C D_h j_C^flat.
```

The tangent includes every active derivative through `P_M`, `T_C`, `H_M`,
`I_4M`, `Rhat_C,M`, `G_J`, flat/sharp, `K4`, and `H_profile`, including
`(delta G_J) J`. A Schur reduction is valid only after its geometry pivot is
separately regular.

## Candidate A

### Why A Can Be Completed In This Family

D4 distinguishes structural geometry from transport mobility while admitting
both as typed inputs to A's baseline transport construction. D7 freezes the
reference baseline potential and current:

```text
Phi_A^D7(C,W_A)

J0_A^D7
  = -eta Diag(W_A) d0 Phi_A^D7.
```

The successor therefore does not invent a generic `h -> W_A` writer. It adds
a named reference-relative geometry contribution to the baseline potential
while keeping `W_A` as the sole mobility owner.

Define

```text
Delta_0(h)
  = H0,ref^-1 B H1_form(h) B^T

Phi_A^CI(C,W_A,h)
  = Phi_A^D7(C,W_A)
    + kappa_Ah [Delta_0(h) - Delta_0(h_ref)] C

M4_A(W_A)
  = eta Diag(W_A)

J0_A^CI
  = -M4_A(W_A) d0 Phi_A^CI.
```

`kappa_Ah` is a typed revision-specific geometry-to-potential coefficient:

```text
[kappa_Ah] = [Phi_A] / ([Delta_0] [C]).

enabled reference profile:
  kappa_Ah = +1.0 in the declared unit basis;

ablation profile:
  kappa_Ah = 0.
```

The enabled value was selected before D8-B and is not optimized for visibility
or stability. Its sign is a profile choice, not a theory-fixed sign. It is not
silently identified with D7 `kappa_c`; units and gauge equivalence require an
explicit later audit. At `h = h_ref`, the added term is exactly zero, so the
accepted D7 baseline is recovered exactly as a mathematical map.

The accepted A stages then remain:

```text
W_hat_A(h) = G_W(C,J0_A^CI(h))

q_A = (W_A - W_hat_A) / (W_A + W_hat_A)

j_A,flux = chi_A Diag(q_A) J

j_A^flat = G_J(h) j_A,flux

Delta K4_A = zeta_A iota_A(A_star(j_A^flat)).
```

`W_hat_A(h)` is recomputed inside every joint-root residual evaluation, after
`J0_A^CI(h)` and before `q_A`. It is pre-read in that internal stage order; it
is not frozen outside the root. `zeta_A` is external to `iota_A`, so no
unstated adapter homogeneity is required.

The joint root is

```text
F_J,A
  = J
    - J0_A^CI(C_k,W_A,k,h)
    - zeta_A j_A,flux(J,h)
  = 0

F_h,A
  = h
    - H_profile(K4_base + Delta K4_A(J,h),h4_ref,context)
  = 0.
```

After the root, the accepted D7 writer is unchanged:

```text
C_(k+1) = C_k - Delta_t B J + declared boundary terms

W_drv,A = G_W(C_(k+1),J)

W_A,(k+1)
  = W_A,k^a_A W_drv,A^(1-a_A).
```

Generated geometry does not write `W_A` directly. It changes the potential,
baseline current, authoritative total current, and continuity; the existing
writer then consumes post-continuity `C` and authoritative `J`.

### A Reference Regularity And Full Chain

At `kappa_H = 0`, `h = h_ref`, the reference-relative correction vanishes,
and the current equation is the accepted D6/D7 A closure. On the smooth chart
where the `G_W` floor is inactive, the reference Jacobian is

```text
[ L_A  B_A ]
[  0    I  ].
```

The accepted bound

```text
sigma_min(L_A) >= 1 - zeta_bar_A > 0
```

therefore supplies the same local IFT foothold. A has a unique local smooth
coupled branch for sufficiently small structural coupling on that chart.

Away from the reference, D8-B must retain the complete chain

```text
h
 -> Delta_0
 -> Phi_A^CI
 -> J0_A^CI
 -> W_hat_A
 -> q_A
 -> j_A,flux
 -> j_A^flat
 -> Delta K4_A
 -> H_profile.
```

Crossing the `G_W` floor is not covered by the classical derivative. It needs
a separately admitted active-set or stratified derivative contract. Baseline
and explicit Read-Back paths remain distinct and must not be counted twice.

This A construction is a minimal revision-specific constitutive profile
derived from D4's geometry/mobility factorization and D8-A's graph-Hodge
operator. It is not claimed to be uniquely required by core theory or already
normative GRC9V4.

## Structural Visibility And D8-B

For each candidate and admitted branch point, D8-A's exact test remains:

```text
there exist u,v in V_a such that

(d0 u)^T delta H1_form,a (d0 v) != 0.
```

The coupled realizations divide into visible and projected-kernel subdomains.
A regular complete root may lie in the kernel and remain constitutively valid,
but it cannot support a nonzero constrained structural-target claim. This
successor now provides one formal constitutive receipt for each candidate.

### C Visibility Receipt

D5-v2's three-node selected-sector witness, on identity reference `H1`, gives

```text
j_C,base     = [0.5533580484879859, -0.1140752267340116]
j_C,selected = [0.5518299665764390, -0.10823883523404387].
```

For normalized two-edge star assembly,

```text
A_star(j) = [ j1^2       0.5 j1 j2 ]
            [ 0.5 j1 j2     j2^2  ],
```

the selected-minus-base increment is

```text
[ -0.001688817814678334    0.0016975060084410305 ]
[  0.0016975060084410305  -0.0012975119015936586 ].
```

With `u = (1,-1,0)` and `d0 u = (-2,1)` in the declared path orientation,
the pre-adapter projected value is

```text
(d0 u)^T delta A_star (d0 u)
  = -0.014842807194071116 != 0.
```

For nonzero `kappa_H`, nonzero `zeta_C`, and the accepted non-erasing C
adapter/profile, the resulting `delta H1_form,C` is nonzero. On a connected
three-node tree, `d0` restricted to the zero-sum node tangent is an isomorphism
onto the two-edge form space. Therefore some admissible post-adapter `u,v`
have nonzero projected bilinear response even if `iota_C` changes the displayed
pre-adapter coordinates. This is a formal direct-field visibility witness, not
runtime or full-chain evidence.

### A Visibility Receipt

An admitted A operator-domain construction uses

```text
chi_A     = 1
J_A       = [1.0, -0.4]
q_A,base  = [0.5, -0.25]
q_A,sel   = [0.6, -0.25]

j_A,base  = [0.5, 0.1]
j_A,sel   = [0.6, 0.1]
```

under identity reference `G_J`. Both contrast rows lie strictly inside the
accepted `-1 <= q_A < 1` domain. Their star increment is

```text
[ 0.10999999999999999    0.0049999999999999975 ]
[ 0.0049999999999999975  0.0                  ].
```

The same `d0 u = (-2,1)` gives the pre-adapter value

```text
(d0 u)^T delta A_star (d0 u)
  = 0.41999999999999993 != 0.
```

The accepted non-erasing A adapter/profile with nonzero `kappa_H` and
`zeta_A` produces nonzero `delta H1_form,A`; tree exact-gradient surjectivity
then supplies an admissible post-adapter pair. This is also formal
constitutive evidence, not a runtime probe.

These receipts close the D8-A successor projected-witness obligation for the
instantiated branches. They do not close the complete `h -> transition`
nonannihilation, Hessian, `alpha`, temporal, or stability obligations. Nonzero
`Delta K4` alone remains insufficient outside the explicit receipts.

On a regular chart, each later analysis surface is

```text
D_X Y_a = -B_full,a^-1 D_X F_a,
```

composed with continuity and the candidate commit map. Human acceptance now
authorizes A and C separately for architecture-local D8-B rederivation.
Comparative D8-B remains blocked.

## Family Disposition

```text
coupled/implicit A:
  accepted bounded complete realization candidate

coupled/implicit C:
  accepted bounded complete realization candidate

operator-split:
  not yet pressured

persistent carrier:
  not yet pressured

reconstructed geometry:
  not yet pressured.
```

The two candidates use the same evidential burden but different
ontology-specific equations. Their admission does not rank A or C, select the
coupled family, reject B, or close the overall geometry-temporal successor.
The coupled/implicit family record is complete and accepted; the overall
successor remains open on minimum pressure for the other realization families.

## Debt And Controls

All 28 D8-A debts receive one explicit disposition. Twenty-three are carried
by exact predecessor identity; two are narrowed, two superseded, and the
projected-target witness debt is resolved by the two receipts above. Ten
current successor debts produce a 33-row live union for D10. They preserve:

```text
remaining realization-family pressure;
A and C architecture-local D8-B rederivation;
A and C nonzero complete-chain witnesses;
A and C quantitative local-branch work;
C Q_C conditioning;
A and C global-root/topology boundaries;
continuation, stability, and later comparative analysis.
```

Fifty-five controls separately fail closed against read/gain mistakes,
historically gated C resolvents, `zeta^2`, gain placement inside an adapter,
omitted C identification dependence, false reuse of the old physical C margin,
arbitrary A consumers, out-of-root `W_hat_A`, untyped or post-hoc `kappa_Ah`,
geometry/mobility conflation, direct geometry writers, incomplete A chain
rules, deferred visibility, candidate ranking, hidden state, topology-crossing
IFT claims, runtime relabeling, and normative overclaim.

## Claim Ceiling

This pass supports only:

> Two bounded local coupled/implicit complete-step candidates, A and C, with
> explicit full joint blocks, reference IFT routes, and formal constitutive
> nonempty projected direct-field visibility receipts under their declared
> smooth fixed-stratum domains.

It does not establish nonzero complete-transition chain sensitivity, numeric
or global branch margins, temporal or structural stability, cross-candidate or
cross-family comparison, architecture selection, runtime implementation,
normative GRC9V4, a unique core-theory law, learning, choice, agency, or
ecology.
