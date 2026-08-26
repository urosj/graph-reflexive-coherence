# D8-A Branch-Appropriate Structural-Target Extraction

**Record:** `GRC9V4-CD-D8A-v1`  
**Status:** accepted bounded  
**Predecessor:** accepted `GRC9V4-CD-D7G-v2`  
**Decision digest:** `5e3af8a6b8b327b3d98b5c5f6ac934ff528f048c3927a085c59194262afba021`  
**Runtime or `src/` changed:** no

## Disposition

D8-A derives the branch-appropriate structural forms for Candidates A and C
and extracts one exact common metric-response target under the typed
graph-Hodge correction recorded by `D7G-post-v2`. It does not calculate a
continuation spectrum, classify stability, or select a temporal geometry
realization.

The bounded result is:

```text
A structural object:
  conditional C structure at frozen W_A
  + accepted D6-v2 smooth current slaving
  -> reduced constrained second-variation form

C structural object:
  C-only structure
  + exact derived T_C tangent
  + accepted D6-v2 smooth current slaving
  -> reduced constrained second-variation form

common direct field target:
  H1_form = structural one-form Hodge / Dirichlet weight
  G_J = dual current / flux resistance metric
  M4 = causally distinct transport mobility
  delta H1_form -> exact change of the field quadratic form

complete Hessian / alpha / gamma / stability:
  not established
```

A and C remain unranked. D8-B remains blocked. If D8-A is accepted, the next
step is the named geometry-temporal realization successor, not D8-B itself.

## Why The Objects Differ

D3 admitted both candidates on smoothly slaved current rows, but it did not
give them the same structural ontology.

Candidate A has independent runtime state `(C,W_A)`, but current theory does
not provide a joint structural functional in `(C,W_A)`. Its lawful structural
object is therefore conditional:

```text
F_struct(C; W_A,star)
delta W_A = 0
delta J_C,A = D_C Phi_A|W_A,star [delta C]
```

`W_A` may parameterize which conditional C landscape is analyzed. It does not
receive an `alpha` spectrum of its own.

Candidate C has no independent retained-sector state. Its lawful object is
C-only:

```text
T_C = P_M(C,h,...) C

delta T_C
  = P_M delta C
  + (D_C P_M[delta C and all declared selector inputs]) C_star

delta J_C,C = D_C Phi_C[delta C].
```

Varying `delta T_C` independently would manufacture a new state direction and
turn C into a different candidate. C therefore has one C-only structural
spectrum, not separate C and retained-sector spectra.

The graph-Hodge type correction also makes C's physical representation
explicit:

```text
J_trial,flux
  -> G_J,pre J_trial,flux
  -> I_4M^pre J_trial,pre^flat
  -> R_C,M J_trial,M^flat
  -> (I_4M^pre)^-1 j_M^flat
  -> G_J,pre^-1 j_pre^flat
  -> j_flux.
```

`I_4M^pre` identifies one-form Hodge spaces; it does not also lower physical
flux. The old C witness uses identity `H1_form` and `G_J`, so its values survive
the corrected pipeline within binary roundoff. General nonidentity
flat/response/sharp conditioning remains explicit pre-D10 debt.

The current then branches by type. Physical `j_flux` is consumed by continuity
and current accounting. Structural `K4` consumes the lowered Read-Back
one-form `j_struct^flat` before the sharp map:

```text
A:
  j_A,flux -> G_J,pre -> j_A,struct^flat
  iota_A(j_A,struct^flat tensor j_A,struct^flat) -> K4_A

C:
  j_C,struct^flat = j_pre^flat
  iota_C(j_C,struct^flat tensor j_C,struct^flat) -> K4_C
  G_J,pre^-1 j_C,struct^flat -> j_C,flux for continuity.
```

For variable geometry,

```text
delta j_struct^flat
  = (delta G_J) j_flux + G_J delta j_flux.
```

The accepted lagged explicit rows freeze pre-read geometry, so
`delta G_J,pre = 0`. Their pullback may use
`delta j_struct^flat = G_J,pre delta j_flux`. A coupled or implicit successor
must retain the first term. The nonidentity correction regression confirms
that `j_flux tensor j_flux` and
`j_struct^flat tensor j_struct^flat` are not interchangeable.

`iota_A` and `iota_C` are the already accepted candidate-specific typed
structural adapters and gains. The correction introduces no generic
`kappa_K`. A future B current-mediated path would require its own admitted
`iota_B`; B is not reopened here.

On their accepted smooth strata, both objects have the formal reduced form

```text
F_a,red[C]
  = P_struct(C, h_a,red[C]; fixed candidate context)
  - eta_a (Q(C,h_a,red[C]) - Q0)

Q_struct,a[u,v]
  = D_C^2 F_a,red[C_star](u,v),
```

restricted to the metric-aware conservation tangent and candidate-specific
authority constraints. A self-adjoint operator may represent this form after
the complete functional, domain, inner product, constraint projector, and
branch are instantiated. D8-A does not assume that completion.

## Graph-Hodge Type Correction

The newer audit found a type conflation rather than a free convention choice.
D5 already freezes

```text
d0 = B^T
delta1 = H0^-1 B H1
<alpha,beta>_1 = alpha^T H1 beta.
```

Thus the `H1` used by the scalar Dirichlet form is a structural one-form
Hodge/Gram weight. B1-GR's `W^-1` object is instead the dual metric on physical
edge currents. The correction receipt therefore freezes three objects:

```text
H1_form:
  structural one-form Hodge / Dirichlet weight
  H1_form,ref = diag(W_V3)

G_J:
  current / flux resistance metric and flat map
  G_J,ref = diag(W_V3^-1)

M4:
  transport mobility with independent causal authority.
```

In the simple paired graph-Hodge profile, `G_J(h) = H1_form(h)^-1`. Numerical
coincidence between `H1_form` and legacy mobility does not merge structural and
transport authority. Richer DEC edge-volume factors remain pre-D10 debt.

The correction is recorded separately in
[`D7GPostv2GraphHodgeTypeCorrection.json`](./D7GPostv2GraphHodgeTypeCorrection.json)
and its
[`interpretation`](./D7GPostv2GraphHodgeTypeCorrection.md). Accepted D4-D7 and
D7G-v2 bytes and decision digests remain unchanged.

The type split has the exact reference duality invariant

```text
e = d0 C
J = H1_form,ref e

e^T H1_form,ref e = J^T G_J,ref J.
```

The nonidentity regression row `H1_form = diag(2,3)`, `e = (0.7,-0.2)` gives
`1.0999999999999999` on both sides with zero error.

The associated nonidentity rank-one regression gives a maximum componentwise
difference of `1.4699999999999998` between the physical-flux and lowered-form
outer products. This is a type-separation check, not a general nonidentity C
response witness.

## Exact Direct Field Target

The Continuation Spectrum paper gives the direct field term

```text
P_field[C]
  = integral [kappa_C/2 |grad C|_h^2 + W(C)] dV_h.
```

Under the corrected typed graph-Hodge contract, write

```text
d0 = B_ref^T

Q_field,h[u,v]
  = kappa_C (d0 u)^T H1_form (d0 v)
  + u^T H0 diag(W_pot''(C_star)) v.
```

`W_pot` denotes the local potential from the core structural functional. It is
not Candidate A's retained conductance `W_A`.

The admitted affine profile changes only `H1`:

```text
delta H0 = 0
delta B = 0
delta boundary = 0
delta H1_form = kappa_H delta K4.
```

The direct field response is therefore exact:

```text
D_H1_form Q_field[delta H1_form](u,v)
  = kappa_C (d0 u)^T delta H1_form (d0 v)

  = kappa_C kappa_H
    (d0 u)^T delta K4 (d0 v).
```

The bilinear form is authoritative. In a declared `H0`-weighted coordinate
representation, its matrix shorthand is the constrained pullback of

```text
kappa_C Pi_a H0^-1 B_ref delta H1_form B_ref^T Pi_a.
```

For a supplied metric direction, D8-A extracts the direct target subspace as

```text
V_target,a(delta H1_form)
  = V_a minus_H0-weighted-orthogonal ker L_field,a(delta H1_form).
```

The orthogonality and closure are taken in the declared `H0`-weighted
candidate structural inner product. Equivalently, for the symmetric projected
representative this is the weighted closure of its range. An admissible `v` is
a direct target direction exactly when
`L_field,a(delta H1_form) v != 0`. The target set is empty exactly when the
projected operator vanishes on the full candidate tangent.

This is a real D8-A result: it identifies how a D7G metric direction can alter
the direct structural field curvature. It is independent of whether generated
geometry is stored, reconstructed, consumed in the same beat, or solved
implicitly, provided the successor preserves the same field functional, typed
`H1_form` graph-Hodge representation, and profile. Changed DEC weights or a
changed profile require rederivation.

## Why Nonzero Geometry Is Not Yet A Nonzero Structural Target

D7G-v2 proved

```text
delta K4 != 0 -> delta H1_form != 0
```

inside the admitted affine profile. D8-A does not promote that statement to

```text
delta C_struct != 0.
```

The constrained pullback can still vanish. A metric increment may be invisible
to exact C-gradient directions, removed by the conservation or gauge
projection, or annihilated on a particular branch. A future instantiated row
must show at least one admissible pair `(u,v)` for which

```text
(d0 u)^T delta H1_form (d0 v) != 0,
```

or record the direction as structurally silent for the direct field term.

Even a nonzero direct field response is not the complete Hessian response. The
full constrained second variation also contains induced-geometry and
constraint terms, including the moving tangent, volume, inner product, and
projector. Those terms can add, cancel, or alter the direct target. D8-A
therefore supports neither hardening nor softening before the complete branch
form is instantiated.

## Realization-Scope Classification

D8-A records ten target rows.

### Realization-invariant targets

Four targets constrain every successor that preserves the admitted ontology
and structural basis:

1. the direct `delta H1_form -> D_H1_form Q_field` metric response for
   successors preserving the typed structural one-form Hodge contract;
2. metric-aware conservation tangent and projector transport;
3. A's rule that `delta W_A` is not a structural coordinate without a joint
   `F_struct(C,W_A)`;
4. C's exact derived-sector tangent and prohibition on independent
   `delta T_C`.

These are structural and authority requirements. They are not statements that
the complete target is nonzero.

### Accepted-lagged-branch targets

Two instantiated pullback chains belong specifically to the accepted
D6-v2/D7G-v2 lagged branch:

```text
A:
  s_A -> D Phi_A -> delta j_A,flux
      -> G_J,pre delta j_A,flux = delta j_A,struct^flat
      -> delta K4_A -> delta H1_form,A
      -> direct field target

C:
  s_C -> exact selector tangent -> D Phi_C
      -> delta j_C,struct^flat before sharp
      -> delta K4_C -> delta H1_form,C -> direct field target.
```

Here `s_a` is a formed-context or cultivation direction. It is not the
continuation test mode `u`. A successor that changes current/geometry slaving,
selector timing, state authority, or stage order must rederive these pullbacks
in D8-B. They cannot be imposed universally.

Two additional lagged-branch structural objects are **potentially derivable
before temporal synthesis**, but are not instantiated by D8-A:

1. the full lagged-branch Hessian, including the complete field,
   induced-geometry, constraint, projector, inner-product, `D_C h_lag`, and
   `D_C^2 h_lag` terms; and
2. its numerical `alpha` spectrum and mode subspaces after fixing a constrained
   critical branch, normalization, domain, null classification, and reference
   transport.

These objects are not temporally undefined. They are uninstantiated bounded
lagged-branch work. They become architecture-final only if the successor
preserves the accepted slaving relation and `H1_form` profile; otherwise
D8-B must rederive them.

### Genuinely not finalizable before temporal realization

Two targets remain unavailable until a complete temporal realization exists:

1. generated-geometry influence on a later runtime transition; and
2. temporal generator rates or map multipliers (`gamma` or `mu`).

This separation prevents a circular argument in which missing temporal
realization is used to declare all structural mathematics unavailable, while
an incomplete structural target is then used to select that realization.

## Derivative Boundary

The following objects remain distinct:

```text
D_(h_pre) F_A
  = not established load-bearing

D_(h_pre) internal C operators
  = load-bearing and conditionally nonzero on named strict-gap directions

D_(h_pre) J_C,C
  = nonzero not established

D_(h_pre) F_C
  = load-bearing and not identically excluded,
    but nonzero full-transition sensitivity is unproved

D_(h_generated) F_A,later
D_(h_generated) F_C,later
  = undefined absent a complete realization, not zero

D_h Q_field
  = the exact structural metric-response target derived here.

D_h of the full accepted lagged structural object
  = potentially derivable before temporal synthesis,
    but not instantiated by D8-A.

D_h of the architecture-final structural object
  = must be rederived if temporal synthesis changes slaving
    or the H1_form profile / graph-DEC weights.
```

An internal C operator derivative cannot be promoted into a current or full
transition derivative. The structural metric derivative cannot be promoted
into runtime generated-geometry feedback. Repeating the known absence of
`Gamma_A` and `Gamma_C` is not D8-A evidence.

## Successor Handoff

Accepted D8-A readies and authorizes
`GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR`. The successor must:

- preserve or explicitly replace every realization-invariant target;
- preserve or explicitly replace the typed structural-Hodge/current-metric
  dictionary and
  rederive the direct response when it changes;
- preserve physical `j_flux` for continuity and lowered `j_struct^flat` for
  rank-one `K4` assembly, and retain `delta G_J` whenever the realization
  makes the metric variable inside the pullback;
- state whether each lagged target is preserved, changed, or inapplicable;
- consume or explicitly defer the pre-temporal lagged full-Hessian and `alpha`
  work without relabeling it as temporally undefined;
- instantiate complete equations, state authority, stage order, accounting,
  regularity, failure semantics, and a linearization surface;
- produce a projected structural-target witness or explicit kernel result;
- keep candidate effects separate from realization effects; and
- retain the derivative typing frozen above.

The four already named realization families remain a non-exhaustive minimum
pressure set. An `S_H` interface alone cannot close the successor. D8-B is not
authorized until a bounded complete realization has been admitted and any
changed authority or stage has reopened the earliest affected gate.

## Debt And Controls

All 24 D7G-v2 debts and all five D7G-post-v2 correction debts receive one
explicit disposition. The D8-A ledger has 28 typed debts. The central new
blockers cover:

```text
complete geometry-temporal realization
full branch functional and second variation
typed H1_form / G_J / M4 separation and graph-DEC alternatives
projected target witness and pullback kernel
A/C lagged target rederivation
C full-transition sensitivity
C dynamic selector and stratum lifecycle
D7G-post-v2 nonidentity flat/sharp validation and normative encoding
D8-B spectrum and stability
normalization, representation, and reference transport
```

Forty controls fail closed against Hessian/transition relabels,
independent-coordinate manufacture, current-metric/field-Hodge inference by
symbol matching, physical-flux outer products used as structural `K4` input,
new common structural gains replacing candidate-specific adapters,
direct-field overpromotion, temporal gaps mislabeled as
structural unavailability, undefined-as-zero, lagged-target universalization,
missing constraint transport, premature stability, candidate ranking,
interface-only closeout, and runtime/spec claims.

## Predecessor Lineage Check

The accepted D7G-v2 source was independently recomputed during this revision:

```text
declared decision digest   = c52912d83797ee294799709b3e770574043df37f80073b51eebfaf8b2fd27efb
recomputed decision digest = c52912d83797ee294799709b3e770574043df37f80073b51eebfaf8b2fd27efb

declared file SHA-256      = 364b1b05ccac3c1220677ac9dbc6e46259beb47ef4cabcafaf381e3bc7ef3c38
recomputed file SHA-256    = 364b1b05ccac3c1220677ac9dbc6e46259beb47ef4cabcafaf381e3bc7ef3c38
```

The earlier `da42d...` digest belongs to a superseded pre-acceptance revision,
not the accepted predecessor consumed by D8-A.

The typed correction source was also recomputed before consumption:

```text
declared decision digest   = 2e2f4d53e0abf3134f586cc60467bf5881cc60414af82df35bf6ac7772400984
recomputed decision digest = 2e2f4d53e0abf3134f586cc60467bf5881cc60414af82df35bf6ac7772400984

declared file SHA-256      = bbef6c37449ab7d58b3388f5d030bffbbd750ba470216d0660573d7af27f895f
recomputed file SHA-256    = bbef6c37449ab7d58b3388f5d030bffbbd750ba470216d0660573d7af27f895f
```

Joint acceptance of D8-A and the correction receipt is now recorded. Neither
record replaces or mutates the accepted D7G-v2 history.

## Claim Ceiling

D8-A supports only:

> Formal branch-appropriate A and C reduced structural forms, one exact direct
> field metric-response target under the typed `H1_form / G_J / M4`
> graph-Hodge correction, typed `j_struct^flat tensor j_struct^flat -> K4`
> candidate pullbacks on the accepted lagged rows, and a scope classification
> separating realization-invariant targets, accepted-lagged-branch targets,
> uninstantiated but pre-temporally derivable lagged structural work, and
> genuinely temporal-only targets.

It does not support:

```text
complete structural Hessian
unique continuum or normative graph-DEC edge-volume discretization
nonzero complete structural target
alpha spectrum or structural marginality
temporal generator, multipliers, or stability
closed generated-geometry runtime feedback
structural cultivation
candidate ranking or architecture selection
normative GRC9V4 specification
runtime implementation or src changes
```

## Acceptance Boundary

Accepted bounded on 2026-08-24 jointly with the graph-Hodge correction. This
authorizes only the named geometry-temporal-realization successor. It does not
authorize D8-B, D9, D10, specification writing, or runtime work.
