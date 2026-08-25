# Geometry-Temporal Realization Successor: Operator-Split Same-Beat

**Record:** `GRC9V4-GTRS-OS-v1`  
**Status:** `accepted_bounded`  
**Decision digest:** `36c98542c7920d468e932287872cf4dabf8720d5d2c6b0c0e30e6f94b113605f`  
**Runtime or `src/` changed:** `false`

## Purpose

This is the second realization-family pressure after the accepted
coupled/implicit A and C constructions. It asks whether the same admitted
candidate-local constitutive content can form a complete same-beat step
without a simultaneous current-geometry root and without adding persistent
state.

It does not rank the coupled and operator-split families. It also does not
rerun D8-A, instantiate a formed V4 branch, or claim numeric stability.

## Preregistered Primary Split

The primary realization is exactly one predictor, one geometry update, one
fixed-geometry corrector, and one atomic commit:

```text
X_k
  -> J^(0)
  -> j_flat^(0)
  -> Delta K4^(0)
  -> h^(1)
  -> J^(1)
  -> X_(k+1).
```

`J^(1)` cannot alter `h^(1)` in this row. A second correction or a different
stage order would be a separately named successor realization. This prevents
the split from being improved after its defect is observed.

## Candidate C

At `h_ref`, solve the accepted fixed-geometry C current:

```text
J_C^(0)
  = J0_C(C_k,T_C(h_ref),h_ref)
    + zeta_C j_C,flux(J_C^(0),h_ref).
```

Form the once-gated causal read and geometry:

```text
j_C^flat,(0)
  = chi_C I_4M^-1 Rhat_C,M I_4M G_J J_C^(0)

Delta K4_C^(0)
  = zeta_C iota_C(A_star(j_C^flat,(0)))

h_C^(1)
  = H_profile(K4_base + Delta K4_C^(0)).
```

At fixed `h_C^(1)`, recompute the entire geometry-dependent chain

```text
P_M -> T_C -> H_M -> I_4M -> Rhat_C,M -> G_J -> J0_C
```

and solve

```text
J_C^(1)
  = J0_C(C_k,T_C(h_C^(1)),h_C^(1))
    + zeta_C j_C,flux(J_C^(1),h_C^(1)).
```

Only `J_C^(1)` enters continuity. Only `C_(k+1)` commits. `T_C` remains
derived; predictor caches have no corrector authority.

## Candidate A

Solve the accepted A reference current at `h_ref`, then use its causal read to
produce `h_A^(1)`. At fixed `h_A^(1)`, the admitted geometry consumer is

```text
Phi_A^OS
  = Phi_A^D7
    + kappa_Ah
      [Delta_0(h_A^(1)) - Delta_0(h_ref)] C_k.
```

Recompute

```text
J0_A^OS -> W_hat_A -> q_A
```

and solve the A corrector current `J_A^(1)`. That current enters continuity;
all differential summaries consumed by the writer are then refreshed from
`C_(k+1)`, and the unchanged D7 writer produces `W_A,(k+1)`. `W_A` remains
the sole mobility authority. Geometry has no direct writer authority.

## Split-Consistency Residual

The final corrector current generally generates a different geometry from the
predictor current. Define

```text
h_hat^(1)
  = H_profile(
      K4_base + Delta K4(J^(1),h^(1)))

r_h^OS
  = h^(1) - h_hat^(1).
```

The coupled root has `r_h = 0` by construction. The one-pass split does not.
That nonzero residual is the explicit price of replacing the simultaneous root
with ordered substages; it is not automatically a failed complete step.

The residual has a sharper exact interpretation. Let

```text
F_a^CI = (F_J,a, F_h,a)
```

be the accepted coupled root. The corrector solves `F_J,a` exactly at fixed
`h_a^(1)`, so the operator-split pair satisfies

```text
F_a^CI(J_a^(1),h_a^(1)) = (0,r_h,a^OS).
```

The split is therefore exactly current-consistent with the coupled
constitutive equations. Its sole coupled-equation residual is the geometry
fixed point that the one-pass architecture deliberately does not reclose.

The residual is measured in the relative Hodge operator norm

```text
||delta h||_(H1,ref)
  = ||H1_form,ref^(-1/2)
       delta H1_form
       H1_form,ref^(-1/2)||_2.
```

The structural output is not measured in that norm directly. Freeze

```text
S_a(J,h) = Delta K4_a(J,h) in K_4

P_0 = (1/kappa_H) D_K H_profile : K_4 -> T_h H1_form

G_a,kappa(J,h)
  = D_K H_profile[S_a(J,h)]
  = kappa_H P_0[S_a(J,h)].
```

Use a reference-scaled operator norm `||.||_K` on the accepted common `K_4`
coordinate/unit basis and define

```text
g_0 = ||P_0||_(K->H)
g_H = |kappa_H| g_0.
```

Only the pushed-forward `G_a,kappa` is `H1_form`-valued. This prevents
`Delta K4` and Hodge geometry from being silently assigned the same units.

The residual is not assumed to be `O(Delta_t)`. Write the fixed-geometry
current solution as `J=C_a(h)`. The affine-profile split is

```text
J^(0) = C_a(h_ref)
h^(1) = h_ref + kappa_H P_0[S_a(J^(0),h_ref)]
J^(1) = C_a(h^(1)).
```

On the D8-B `C2` subcharts--A floor-inactive and C fixed-rank with strict
selector gap--suppose

```text
||C_a(h)-C_a(h_tilde)||_J
  <= L_C ||h-h_tilde||_(H1,ref)

||S_a(J,h)-S_a(J_tilde,h_tilde)||_K
  <= L_S (
       ||J-J_tilde||_J
       + ||h-h_tilde||_(H1,ref))

M_S = ||S_a(J^(0),h_ref)||_K < infinity

M_G = ||P_0[S_a(J^(0),h_ref)]||_(H1,ref)
    <= g_0 M_S.
```

Then

```text
||h^(1)-h_ref||_(H1,ref)
  <= |kappa_H| M_G
  <= g_H M_S

||J^(1)-J^(0)||_J
  <= L_C |kappa_H| M_G
  <= L_C g_H M_S

||r_h^OS||_(H1,ref)
  <= |kappa_H|^2 g_0^2 L_S M_S (1+L_C)
   = g_H^2 L_S M_S (1+L_C).
```

This proves the local quadratic coupling defect under named hypotheses. It is
not valid across floor, selector-rank, gap, topology, or other nonsmooth
boundaries.

For comparison, define

```text
T_a(h) = P_0[S_a(C_a(h),h)].
```

The coupled geometry is the fixed point

```text
h_star = h_ref + kappa_H T_a(h_star),
```

whereas `h^(1)` is its first Picard iterate from `h_ref`. If `T_a` is
`L_T`-Lipschitz and `|kappa_H| L_T < 1`, then

```text
||h_star-h^(1)||_(H1,ref)
  <= |kappa_H|^2 L_T M_G
     / (1-|kappa_H| L_T),

M_G <= g_0 M_S.
```

Local smoothness of the corrector and commit map transfers the same
`O(kappa_H^2)` order to `Psi_a^OS-Psi_a^CI` on matched local branches; its
continuity component additionally carries `Delta_t`. These are normed,
conditional local bounds, not instantiated numeric or uniform margins.

## Result

Both primary rows receive:

```text
A operator split = bounded_complete_realization
C operator split = bounded_complete_realization
```

The basis is equation-level and local:

- each predictor is the accepted regular fixed-geometry current solve;
- each geometry map is defined on the accepted smooth fixed stratum;
- each corrector remains locally regular for a sufficiently small geometry
  departure while its declared domain and inverse margins remain positive;
- generated geometry is an explicit equation-level input to the later
  corrector, not merely emitted;
- the complete map is Markovian in the accepted candidate state and declared
  context;
- only final physical current enters coherence accounting;
- no new persistent carrier is introduced;
- every failure is atomic.

The exact positive wording is:

```text
bounded complete realization with an explicit equation-level same-beat
geometry consumer; executed complete-chain nonannihilation remains open.
```

For A, `h_A^(1)` parameterizes `Phi_A^OS`, `J0_A^OS`, `W_hat_A`, `q_A`, and
the fixed-geometry current equation. For C, it parameterizes the entire
selector, Hodge, identification, response, baseline-current, and current-
closure chain. D8-A/D8-B direct-field receipts do not prove
`D_h J_a^(1) != 0` or a nonzero enabled-minus-consumer-off complete map. The
future exact witness surface is

```text
D_h J_a^(1)
  = -(D_J F_J,a)^(-1) D_h F_J,a
```

on the regular corrector chart. No finite complete-chain nonannihilation
witness or quantitative split envelope was executed here. Those remain
explicit debts and cannot be inferred from the positive design disposition.

## Controls And Boundaries

The primary result preserves:

```text
chi_a = 0 read-off semantics
zeta_a = 0 gain-off semantics
kappa_H = 0 fixed-geometry reduction
A W_A mobility and D7 writer authority
C derived T_C authority
no cache, solver-history, or RNG authority
all-or-nothing commit
```

It forbids a retroactive geometry correction, post-hoc conservation repair,
candidate ranking, or relabeling the formal local split order as numeric
coupled equivalence.

## Claim Ceiling And Route

The result supports two local equation-level one-pass operator-split complete
realizations with an explicit split defect. It does not support:

```text
numeric or uniform split margins
O(Delta_t) split order
executed complete-chain nonannihilation
numeric coupled/operator-split equivalence
alpha, beta, gamma, mu, lambda, or stability values
global or event continuation
runtime implementation
normative GRC9V4 specification
architecture or candidate selection
```

The operator-split primary pressure is accepted bounded and complete. The next
authorized family is `GTRS-RG`, reconstructed geometry. Persistent-carrier pressure,
comparative synthesis, D9, D10, specification, and implementation remain
blocked.
