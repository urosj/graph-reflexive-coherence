# D7G Global Metric And Structural-Cultivation Closure

**Record:** `GRC9V4-CD-D7G-v1`  
**Status:** accepted bounded  
**Predecessor:** accepted `GRC9V4-CD-D7V2-v1`  
**Scope:** typed `K_4 -> H_4 -> h_4` constitutive interface and one common
conditional affine profile family for the accepted A/C survivor set; no
specification, runtime, or `src/` change

## Disposition

D7G freezes a typed constitutive interface for the core-theory-open
`K_4 -> H_4 -> h_4` relation and admits one bounded, common,
reference-relative affine graph-Hodge **profile family**, conditional on an
admitted reference embedding `E_ref`. The family is non-erasing, positive on
an explicit domain, graph covariant, and exactly neutral relative to any
admitted reference surface. Current GRC9V3 source does not define a unique
`E_ref`, so D7G-v1 does not claim that the family is already instantiated.

It does **not** complete D7G. D4-D7 established candidate-local mathematics
conditional on an admitted pre-read geometry; they did not establish closure
uniformly over an admitted geometry class. The next work is therefore a
geometry-parametric A/C closure audit under the typed interface, not an
automatic D4-v3-D7-v3 redesign cycle:

```text
global_structural_disposition =
  H4_interface_frozen_affine_reference_profile_family_conditionally_admitted_
  D7Gv2_embedding_parametric_and_handoff_closure_required

A.H4_upstream_effect = requires_geometry_parametric_closure_audit
C.H4_upstream_effect = requires_geometry_parametric_closure_audit

D7G_complete = false
D8_authorized = false
```

This is an architectural correction to the original late-integration staging.
It is not candidate rejection, a missing-theory closeout, a universal solution
of `g[K]`, or a wholesale restart of D4-D7.

## Source Check: What GRC9V3 Already Implements

The current GRC9V3 runtime is implemented and executable. D7G therefore audited
the source rather than treating V3 as an abstract or missing substrate.

The source has two distinct surfaces:

```text
compute_hybrid_node_tensors()
  -> state.cached_quantities["hybrid_node_tensors"]

compute_base_conductance()
  -> scalar base_conductance
  -> potential
  -> antisymmetric flux
```

The first materializes the GRC9 Eq. (1) row-basis tensor. The second implements
the operative transport geometry:

```text
w_e = exp(
  - alpha (C_u + C_v) / 2
  - beta ||grad_u - grad_v||^2 / 2
  - gamma J_e,in^2 / 2
)
```

for the current `curvature_backend = none` GRC9V3 profile, with the declared
positive floor applied by source.

The source contains no consumer that maps `hybrid_node_tensors` into
`base_conductance`, potential, or flux. The hybrid tensor is consumed by tests,
telemetry, and diagnostic cache surfaces only. The GRC9V3 specification also
states that baseline transport uses scalar `base_conductance`; tensor-derived
or channel-specific transport requires the explicit `anisotropic_edges`
capability.

Thus the source result is narrow:

> GRC9V3 already has an operative scalar geometry/transport law and a separate
> row-basis `K_i` diagnostic. It does not close the non-erasing causal crossing
> `K -> g[K]` required by D7G.

The source boundary does not imply that a V4 physical `h_4` must replace
transport mobility or instantiate `anisotropic_edges`. It establishes only
that current V3 source does not already provide the required crossing. Core RC
also leaves `g[K]` constitutively incomplete; D7G therefore owns an admissible
graph-substrate interface and profiles, not a universal theory formula.

This distinction blocks two incorrect conclusions:

```text
GRC9V3 is unimplemented                         = false
GRC9V3 hybrid tensor already is executed h_4  = false
```

## Common Graph-Local Assembly

D4-v2 froze the common `K_4` domain as finite-radius symmetric bilinear forms
on the oriented live-edge one-form space. D7G closes its pending overlap
normalization.

For every live vertex `v`, let `R_v` restrict a global edge cochain to the
declared vertex star. For every live edge `e`, let `m_e` be the number of
declared stars that contain it. On the local edge coordinates define:

```text
(D_v)ee = m_e^(-1/2)
j_v     = D_v R_v j
```

The normalized current-tensor assembly is:

```text
A_star(j) = sum_v R_v^T (j_v tensor j_v) R_v
```

and satisfies:

```text
sum_v R_v^T D_v^2 R_v = I
```

on the live-edge space. This prevents interior and boundary edges from
receiving different unrecorded multiplicity merely because the cover overlaps.

The assembly is:

- symmetric and positive semidefinite;
- finite-radius and graph local;
- covariant under graph relabeling and signed edge reorientation;
- zero for zero current; and
- independent of array insertion order.

This is a revision-specific bounded partition-of-unity completion, not a
normalization theorem. The partition identity fixes each edge's diagonal
multiplicity, but an off-diagonal edge pair receives the cover-dependent factor
`n_ef / sqrt(m_e m_f)`, where `n_ef` is the number of declared stars containing
both edges. Alternative graph-covariant pair normalizations remain explicit
D8/specification pressure.

A non-load-bearing algebra sanity check on a three-node/two-edge path verified
the partition identity, symmetry and positive semidefiniteness of the assembled
increment, positivity of the affine-reference updated Hodge star, signed-edge
orientation covariance, and non-erasure. This checks the written construction;
it is not runtime or scientific evidence.

Assembly locality does not imply local causal support of `j`. Candidate-local
Read-Back operators may already make `j` depend on a connected component. D7G
does not collapse these two meanings of locality. Nor does sparse/local `H_1`
imply sparse/local `H_1^-1`, `I_4M`, or potential-solver support.

## Constitutive Interface

Core RC supplies the structural route but leaves `g[K]` constitutively open.
GRC9V4 therefore admits a typed profile interface:

```text
H_profile : (Delta K_4, h_4,ref, context[K_4,base]) -> h_4+
```

Every profile must declare and satisfy:

- domain, codomain, positivity, and nondegeneracy;
- graph relabeling and signed-edge covariance;
- locality, support, inverse-support, and solver-support semantics;
- units, gauge, and capacity;
- boundary and topology behavior;
- neutral/disabled reduction;
- temporal stage and any lag or fixed-point semantics;
- the separation or explicit factorization of physical geometry and transport
  mobility; and
- derivative access such as `D_K H_profile` when later analysis consumes it.

`Delta K_4` is the primary profile input. The named profile must declare
`K_4,base` in its context; an unqualified `K_4` may not ambiguously mean either
total structure or structural increment.

Two classes are deliberately separate:

```text
H_adm = admissible geometry states h_4
P_adm = admissible profile maps H_profile whose outputs lie in H_adm
```

Candidate closure over `H_adm` and profile sensitivity through
`D_K H_profile` are different obligations. A regular candidate transition over
many geometry states does not by itself establish a regular or non-erasing
profile map.

The substrate owns this interface and its admissibility rules. A named
constitutive profile owns a particular realization. No profile is promoted to
the universal core-theory `g[K]` law merely because it is admissible.

## Conditional Affine Reference Profile Family

Let:

```text
Delta K_4^a = K_4^a - K_4,base
```

be a candidate's admitted structural increment in the common `K_4` units.
The family requires an explicit revision-specific reference embedding:

```text
E_ref : W_V3 -> H_1,ref
```

from the source-current V3 scalar conductance surface into a positive diagonal
V4 reference one-form Hodge surface. Source and specification inspection found
no unique repository-owned convention for this map. D7G-v2 must define and
admit `E_ref`, or close the affine family without instantiation. An admissible
embedding must declare positivity, covariance, units, gauge, boundary and
zero-mobility semantics, and the exact relation between scalar `W_V3` and the
one-form metric. Given such an embedding, let the resulting package be:

```text
h_4,ref = (H_0,ref, H_1,ref, B_ref, boundary_ref)
```

`E_ref` would be a V4 construction; it would not claim that GRC9V3 already possessed
physical `h_4`. Choose one common finite nonzero conversion coefficient
`kappa_H` with units `H_1 / K_4`. The conditional affine profile family is:

```text
Theta_4^a =
  kappa_H H_1,ref^(-1/2) Delta K_4^a H_1,ref^(-1/2)

H_1,read+^a =
  H_1,ref^(1/2) (I + Theta_4^a) H_1,ref^(1/2)

              = H_1,ref + kappa_H Delta K_4^a

H_0,read+^a = H_0,ref
```

The admitted domain is:

```text
I + Theta_4^a > 0
```

as a positive-definite bilinear form. For the A/C current-tensor subprofile,
`Delta K_4^a` is positive semidefinite, so nonnegative `kappa_H` is sufficient
for positivity.

The exact differential is:

```text
delta H_1,read+ = kappa_H delta K_4
```

Therefore, with nonzero `kappa_H`:

```text
delta K_4 != 0 -> delta h_4 != 0
```

The profile family is common to A and C. It does not introduce
candidate-indexed physical geometry laws. It preserves the graph-local
sparsity of the input increment. Disabling the structural increment returns
the supplied V4 reference surface exactly:

```text
Delta K_4 = 0 -> h_4+ = h_4,ref
```

That exact reference neutrality is not the stronger disabled-transition
reduction, which remains open:

```text
F_V4,disabled = F_V3  # pending D7G-v2/full-factorization audit
```

Profile neutrality does not prove transition equality after state authority,
staging, geometry/mobility factorization, and candidate-local operators have
changed. Nor is this a retroactive claim that V3 already possessed physical
`h_4`.

This is an **admitted reference-relative V4 constitutive profile family,
conditional on `E_ref`**. It is not
claimed to be:

- the unique core-theory `g[K]`;
- a theorem that every positive graph Hodge pair realizes a continuum metric;
- an implemented GRC9V3 behavior; or
- a stability result.

## Profile-Family Pressure

The admitted reference profile was compared against the following alternatives.
An admissible alternative may later be registered under the same interface; it
does not become a candidate-indexed exception or rewrite the reference result.

| Family | Disposition | Reason |
|---|---|---|
| Identity or record-only `H_4` | Rejected | Erases every candidate structural payload from later dynamics |
| Diagonal projection into existing scalar conductance | Rejected | Discards off-diagonal vertex-star structure and is not non-erasing |
| Candidate-indexed `H_4^A`, `H_4^C` | Rejected | No independent theory basis; candidate preservation is not a geometry law |
| Reference-relative affine graph-Hodge update | Admitted bounded profile family, conditional on `E_ref` | Positive on a declared domain, covariant, local, reference-neutral, and non-erasing; exact embedding and full disabled-transition reduction remain open |
| Matrix-exponential congruence | Admissible alternative profile, not instantiated | Positive and covariant but generically densifies a local increment and adds unnecessary nonlinearity |
| Spectral clipping/projection | Rejected | Adds outcome-dependent nonsmooth repair and hides capacity semantics |
| Serialized one-beat `K_4` or `h_4` lag | Rejected at D7G | Adds independent cross-beat state and requires a D1 successor |
| Cache-only lag | Rejected | Introduces hidden unserialized state |
| Same-beat current/geometry fixed point | Admissible architecture family, not selected | Reopens D4-D6 equations and needs a separate existence/uniqueness contract |

## Architectural Correction: Geometry As A Constitutive Parameter

The affine-reference `H_1,read+` is generally a full graph-local one-form bilinear
form. D4-D7 treated pre-read geometry as supplied and deliberately left global
`H_4` open. Their result is therefore best stated as:

> Given an admissible pre-read geometry, which candidate-local retained,
> Read-Back, current, and writer structures are well typed and closed?

Those gates produced useful conditional mathematics, but “complete candidate
transition” must be read as **complete candidate-local transition conditional
on an admitted pre-read geometry law**. D7G does not retroactively invalidate
that work. It makes the missing parameterization explicit.

The physical geometry must become causally operative, but D7G does not identify
geometry with transport mobility:

```text
K_4 != M_4
h_4 != M_4
W_A != h_4
```

Each profile must declare a factorized baseline-current construction such as
`J_0 = T(C, h_4, M_4, boundary, ...)`. A full anisotropic transport operator is
one admissible realization if a declared factorized map selects it; it is not
implied by `H_4` alone and may not displace A's accepted `W_A` mobility
authority silently.

The correction does not erase the earlier substrate results. B's canonical
metric raising `A_B = H_1^-1 T_B` and missing source-backed writer `U_B` remain
a genuine constitutive/formative-law boundary. C's selector-derived retained
sector, retained Hodge response, physical-space identification, and closed
current recurrence remain meaningful conditional constructions. The D4-D7
distinctions among bilinear forms and endomorphisms, retained and physical
norms, invertibility and conditioning, same- and next-beat feedback, geometry
and mobility, and state/write authority remain load-bearing.

### Candidate A

For A, the geometry-parametric audit must determine how the declared profile
and factorized current construction provide the geometry-derived inputs to:

```text
W_hat -> q_A -> J0_A and J_C,A
```

while preserving `W_A` as mobility authority. A receives:

```text
H4_upstream_effect = requires_geometry_parametric_closure_audit
```

A nevertheless reaches the new metric nontrivially at the bounded
constitutive level:

```text
delta W_A != 0
  -> delta j_A != 0
  -> delta K_4^A != 0
  -> delta h_4 != 0
```

The likely A result preserves its D5 operator family, D6 inverse and regularity
argument, and D7 writer/state law while reevaluating geometry-derived inputs.
That survival must be established uniformly over the admitted profile domain,
not assumed from the affine witness. The later transition consequence remains
unclaimed until D7G-v2 supplies that parametric receipt.

### Candidate C

D5-v2 already records a selected-sector intervention with nonzero physical
current response:

```text
delta j_C L2 = 0.00603311694477177
```

while the matched complement remains the control. Under the admitted affine
reference profile:

```text
delta T_C != 0
  -> delta j_C != 0
  -> delta K_4^C != 0
  -> delta h_4 != 0
```

The geometry-parametric C audit must cover:

```text
L_0,sym,pre
P_M^Delta
T_C context
H_M / h_M
I_4M
R_C / Rbar_C
J0_C and J_C,C
```

For a general SPD admitted one-form Hodge surface, the candidate survival route
is:

```text
L_0,sym(h) = H_0^-1/2 B H_1(h) B^T H_0^-1/2
H_1,M(T_C,h) = D_C H_1(h) D_C
```

which preserves positive semidefiniteness of `L_0,sym` and positive
definiteness of `H_1,M` for positive `D_C`. The spectral-gap admission,
selector regularity, identification conditioning, Hodge response, and current
closure must be uniform on a declared subdomain. The current provisional
identification:

```text
I_4M^pre = H_1,M H_1,pre^(-1)
```

is valid only for the old pre-read surface. It must be replaced in the
parametric family by the rederived identification against each
admitted `H_1(h)`; coordinate identity is not an acceptable substitute. C also
receives:

```text
H4_upstream_effect = requires_geometry_parametric_closure_audit
```

## Required Geometry-Parametric Closure And Finalization

D7G-v1 acceptance authorizes one append-only cross-gate audit:

```text
D7G-v2 = A/C geometry-parametric closure under the H_profile interface
```

D7G-v2 does not rewrite accepted D4-v2-D7-v2 evidence. It treats those records
as concrete conditional witnesses and asks whether their operator and
transition families remain well typed and regular over a declared admissible
geometry-state class `H_adm`. Separately, it audits the admitted profile-map
class `P_adm`, including `D_K H_profile` or a declared nonsmooth replacement.
The two classes may not be collapsed.

Before evaluating either candidate, D7G-v2 must freeze quantitative bounds:

```text
lambda_min(H_1) >= h_min > 0
lambda_max(H_1) <= h_max < infinity
selector_gap_C >= gamma_selector > 0
cond(I_4M) <= kappa_I < infinity
D6 current-closure regularity margin >= rho_D6 > 0
```

The constants may be symbolic or numerical, but they must be declared before
candidate evaluation. Pointwise positivity or one fixed witness cannot be
promoted into uniform geometry-parametric closure.

D7G-v2 must also define and admit `E_ref`, or explicitly close the conditional
affine family without instantiation. Exact affine neutrality and full disabled
V4-to-V3 transition reduction remain separate checks.

### Frozen Pre-Acceptance Protocol

D7G-v2 must use `D7G-v2-PREACCEPT-v1`, not another flat pressure pass. Its
ordered review is:

```text
definitions and symbol/noun registry
quantifiers and uniform bounds
geometry-state versus profile-map classification
reference/base definitions
causal beat and committed-state graph
Candidate A proof
Candidate C proof
causal non-erasure and named later consumers
authority mutation / gate reopening
neutral versus full-transition reduction
claim-word audit
debt lineage, counts, cross-document consistency, and digest
```

Every load-bearing symbol must identify its type, space, units/gauge, owner,
independent or derived status, evaluation stage, serialization or reconstruction
rule, and causal consumers. Every load-bearing statement must resolve through
an exact definition, derivation or reproducible witness, bounded
assumption/profile restriction, or named open debt not consumed by its claim
ceiling.

The protocol does not optimize for admitting both candidates. A
geometry-parametric receipt for one candidate and a bounded profile-specific or
terminal receipt for the other is a valid result.

D7G-v2 ends by closing the full per-candidate
`delta T_a -> delta K_4^a -> delta h_4 -> delta F_a,later` chain where
supported, assigning each survivor its final D7G disposition, and routing zero
survivors or a hard structural blocker directly to bounded D10 closeout or a
named theory successor. These are D7G-v2 tasks, not deferred edits to D7G-v1.
Anything genuinely discovered after D7G-v2 acceptance becomes a named
`D7G-post-v2` tranche or an explicit earlier-gate reopening.

For each candidate, D7G-v2 must emit either:

```text
geometry_parametric_equivalence_receipt
bounded_profile_specific_receipt
earlier_gate_reopen_required_for_changed_authority_or_staging
terminal_candidate_disposition
```

Changing from one admitted `H_profile` realization to another does not by
itself reopen D4-D7. An earlier gate reopens only if a profile leaves `H_adm`,
changes state or write authority, changes same-beat staging, or invalidates a
candidate's declared operator family rather than merely reevaluating it.

D7G-v2 must also preserve the lagged structural stage:

```text
J_C[k] -> j[k] -> K_4[k] -> h_4+[k] -> later transition
```

It may not silently turn the chain into a same-beat current/geometry fixed
point. It also may not let `h_4+[k]` become hidden cross-beat cache state. A
later consequence is lawful only if D7G-v2 establishes one of these routes:

```text
h_4+[k] is deterministically reconstructed from committed Markov state;
h_4+[k] is consumed before commit into an already admitted committed effect; or
new persistent geometry state is admitted by a named D1 successor.
```

Before this audit returns:

```text
D8 comparable candidate set = []
architecture selected       = false
specification authorized     = false
implementation authorized    = false
runtime evidence claimed     = false
```

## Claim Boundary

D7G-v1 supports:

> a typed graph-substrate `H_profile` interface and one bounded
> revision-specific affine profile family, conditional on `E_ref`, that
> preserves A/C structural distinctions through `delta K_4 -> delta h_4` for a
> supplied admissible reference surface, while source inspection proves that
> current GRC9V3 does not already execute that crossing.

It does not yet support:

- a complete structural-cultivation loop;
- an admitted exact `E_ref` or instantiated affine reference profile;
- complete disabled V4-to-V3 transition reduction;
- a lawful cross-beat geometry handoff;
- a later transition consequence of the new geometry;
- D8 comparability;
- temporal or structural stability;
- a selected GRC9V4 architecture;
- a normative GRC9V4 specification;
- runtime implementation or evidence;
- memory, learning, choice, agency, or ecology; or
- a universal or uniquely theory-required `g[K]` law.

Human acceptance was recorded on 2026-08-24. D7G-v2 is authorized; D8 remains
blocked until D7G-v2 completes and receives acceptance.
