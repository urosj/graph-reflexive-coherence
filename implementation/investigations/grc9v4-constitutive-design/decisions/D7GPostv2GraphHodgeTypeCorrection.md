# D7G-post-v2 Graph-Hodge Edge-Space Type Correction

**Record:** `GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1`  
**Status:** accepted bounded  
**Decision digest:** `2e2f4d53e0abf3134f586cc60467bf5881cc60414af82df35bf6ac7772400984`  
**Accepted historical record bytes changed:** no  
**Runtime or `src/` changed:** no

## Why This Receipt Exists

D5 uses `H1` as the positive one-form Hodge/Gram weight:

```text
d0 = B^T
delta1 = H0^-1 B H1
Delta1 = B^T H0^-1 B H1
<alpha,beta>_1 = alpha^T H1 beta.
```

B1-GR separately uses `W^-1` as the native current/cycle resistance metric.
D7G-v2 placed that inverse-conductance object into its structural `H1` slot,
and D5 treated a runtime flux array as already lowered one-form data. These are
dual edge spaces with equal coordinate dimension, not one untyped object.

This receipt corrects the typing without rewriting accepted D4-D7 or D7G-v2
records and without changing their candidate dispositions.

## Corrected Edge Objects

```text
H1_form:
  structural one-form Hodge/Gram operator
  scalar Dirichlet energy, codifferential, Hodge operators

G_J:
  current/flux resistance metric
  flat_h^G: flux -> one-form
  sharp_h^G: one-form -> flux

M4:
  transport mobility
  candidate/realization authority distinct from both
```

The corrected simple V3 reference embedding is:

```text
H0_ref      = diag(mu_V3)
H1_form_ref = diag(W_V3)
G_J_ref     = diag(W_V3^-1)
B_ref       = oriented live-edge incidence
boundary_ref = declared V3 boundary class.
```

`H1_form_ref` and legacy mobility may contain the same numerical conductances.
That numerical coincidence does not merge structural and transport authority.
The old `W^-1` grounding remains valid as `G_J`; it was attached to the wrong
structural role.

The corrected affine structural profile is:

```text
H1_form,+ = H1_form,ref + kappa_H Delta K4.
```

For the simple paired metric realization:

```text
G_J(h) = H1_form(h)^-1.
```

Richer DEC edge-volume factors remain explicit pre-D10 debt.

## Energy-Duality Invariant

For

```text
e = d0 C
J = H1_form,ref e
G_J,ref = H1_form,ref^-1,
```

the required identity is:

```text
e^T H1_form,ref e = J^T G_J,ref J.
```

The nonidentity regression row uses `H1_form = diag(2,3)`,
`e = (0.7,-0.2)`, and `J = (1.4,-0.6)`. Both sides equal
`1.0999999999999999`; the absolute error is zero.

## Corrected Candidate C Pipeline

The C response now has explicit type transitions:

```text
J_trial,flux
  -> J_trial,pre^flat = G_J,pre J_trial,flux
  -> J_trial,M^flat = I_4M^pre J_trial,pre^flat
  -> j_M^flat = R_C,M J_trial,M^flat
  -> j_pre^flat = (I_4M^pre)^-1 j_M^flat
  -> j_flux = G_J,pre^-1 j_pre^flat.
```

Hence the physical-flux response is:

```text
R_C,flux
  = G_J,pre^-1
    (I_4M^pre)^-1
    R_C,M
    I_4M^pre
    G_J,pre.
```

`I_4M^pre` identifies two one-form Hodge spaces. It does not also perform
flux-to-form lowering. Continuity and D6 consume physical flux coordinates.

## Structural Rank-One Input

The type split also fixes the previously untyped `j tensor j -> K4` crossing.
Physical current and structural one-form output branch after Read-Back:

```text
j_flux:
  consumed by continuity and current accounting

j_struct_flat:
  consumed by the structural rank-one map
  j_struct_flat tensor j_struct_flat -> K4.
```

For Candidate A:

```text
j_A,flux = chi_A q_A J_C,A
j_A,struct^flat = G_J,pre j_A,flux
j_A,struct^flat tensor j_A,struct^flat -> K4_A.
```

For Candidate C, the retained response already produces the needed one-form:

```text
j_C,struct^flat
  = (I_4M^pre)^-1 R_C,M I_4M^pre G_J,pre J_trial,flux.
```

It branches to `G_J,pre^-1 j_C,struct^flat` for physical-current use and to
`j_C,struct^flat tensor j_C,struct^flat` for structural assembly. Sharpening
and then silently treating the flux result as the same one-form is forbidden.

The common typing does not introduce a common structural gain. Assembly is

```text
Delta K4^a = iota_a(A_star(j_a,struct^flat)),
```

where `iota_a` is the already accepted candidate-specific typed structural
adapter and payload gain. A and C retain their accepted coefficients, units,
and authority. If B is later reopened with a current-mediated rank-one path,
the same flux/form typing applies through a separately admitted `iota_B`; this
receipt neither reopens B nor supplies that path.

For a variable metric,

```text
delta j_struct^flat
  = (delta G_J) j_flux + G_J delta j_flux.

G_J = H1_form^-1
  -> delta G_J = -G_J (delta H1_form) G_J.
```

The rank-one derivative is therefore

```text
delta(j_struct^flat tensor j_struct^flat)
  = delta j_struct^flat tensor j_struct^flat
  + j_struct^flat tensor delta j_struct^flat.
```

On the accepted lagged explicit row, pre-read geometry is frozen, so
`delta G_J,pre = 0` and the pullback reduces to
`delta j_struct^flat = G_J,pre delta j_flux`. Coupled or implicit successors
must retain the `delta G_J` term when the metric varies inside the reflexive
chain.

The nonidentity regression makes the crossing observable. With
`G_J = diag(1/2,1/3)` and `j_flux = (1.4,-0.6)`, the lowered one-form is
`j_struct^flat = (0.7,-0.2)`. Their outer products differ by as much as `1.47`
componentwise. The physical-flux outer product is therefore not an alternative
notation for the structural one-form tensor.

## Witness Recalculation

The accepted D5-v2/D6-v2 C witness uses `H1_form,pre = I`; therefore
`G_J,pre = I`. Recalculation through the explicit flat/response/sharp chain
preserves its scientific values:

```text
D5-v2 corrected j_flux = [0.551829966576439, -0.10823883523404383]
D5-v2 recorded j_phys  = [0.551829966576439, -0.10823883523404387]
max component delta    = 4.163336342344337e-17

D6-v2 corrected J_C    = [1.39069504569393, -0.4396646248281818]
D6-v2 recorded J_C     = [1.39069504569393, -0.4396646248281818]

D6-v2 corrected j_flux = [0.78139009138786, -0.0793292496563636]
D6-v2 recorded j_phys  = [0.78139009138786, -0.0793292496563636]

corrected closure residual = 2.0816681711721685e-17
recorded closure residual  = 5.551115123125783e-17
```

Both residuals are machine zero; the difference is evaluation order. The
existing identity-metric witness therefore survives, but it does not validate
general nonidentity flat/sharp conditioning. That remains pre-D10 debt.

## Propagation Boundary

The correction preserves:

```text
A/B/C candidate dispositions
C SPD/Hodge-resolvent arguments
C strict-gap logic
accepted record bytes and digests
D8-A direct-field derivative form.
```

It changes:

```text
D7G reference-embedding edge-space typing
C general physical response composite
D7G j tensor j structural input typing
D8-A A/C candidate-generated pullback staging
future symbol ownership and consumption rules.
```

Future work must consume this receipt alongside the historical accepted
records. It may not silently reuse the old untyped `H1` or treat runtime flux
as already lowered one-form data.

## Claim Ceiling

This receipt supports a typed graph-Hodge correction, the exact simple-reference
energy duality, the nonidentity separation of physical-flux and structural
one-form rank-one tensors, and preservation of the existing identity-metric C
witnesses. It does not support runtime implementation, general nonidentity C
numerical conditioning, temporal realization, stability, or a normative
GRC9V4 spec.

## Acceptance

Accepted bounded on 2026-08-24 jointly with D8-A. This acceptance authorizes
D8-A consumption of the correction. It does not authorize D8-B,
specification writing, implementation, or runtime changes.
