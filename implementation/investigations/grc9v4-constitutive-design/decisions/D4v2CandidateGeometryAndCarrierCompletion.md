# D4-v2 Candidate Geometry And Carrier Completion

Status: `accepted_bounded`.

Record: `GRC9V4-CD-D4V2-v1`.

Predecessor: accepted D7-v1 decision
`7ffaf92b1672aa4fb116539ca5da36aef8bc7f3caf088827fd71f3ec7b483fea`.

Superseded scope: accepted D4-v1 Candidate B/C completion routes and the common
future-`H_4` input interface. All unaffected D0-D7 contracts remain in force.

## Corrected Constitutive Standard

D4-v2 does not require core theory to uniquely name a Candidate B or Candidate
C implementation. Both are revision-level constitutive candidates. The gate
must first derive their admissible representation classes and may then select a
bounded graph-native realization that satisfies the frozen theory and target
constraints.

```text
theory does not uniquely select a representation
  !=
no defensible constitutive representation exists
```

The selected objects are therefore V4 candidate completions, not core theorems
and not architecture selection.

## Audit Hardening Disposition

| Audit pressure | Resolution |
|---|---|
| B units/type | `T_B` now has `H_1,pre` bilinear-form units; `Theta_B` and `H_1,pre^(-1)T_B` are dimensionless |
| B locality | `L_B` is the radius-one line-graph mask with graph-covariant, array-order-independent reconstruction |
| Common `K_4` locality | The initial domain is finite-radius local assembly; arbitrary dense global edge coupling is outside the gate |
| C projector | The weighted scalar graph Laplacian, boundary convention, preregistered cutoff, strict gap, and covariance are explicit |
| C load-bearing geometry | A same-state `kappa_M,C` on/off intervention isolates `H_M`; no direct `T_C -> K_4` route is admitted |
| C structural route | Global cultivation remains the source-backed retained-mediated `j_C^(M) -> (I_4M^pre)^-1 -> j_C^phys tensor j_C^phys -> K_4` path |
| Broader B family | General graph-local endomorphism / symmetric-plus-skew B remains admissible; the selected symmetric family contains the diagonal minimal subprofile |
| C neutral/log scope | `T_C=0` is only algebraically neutral, and `log(D_C^2)` is only the local diagonal scaling generator |
| C cutoff and inner map | Cutoff units/gauge and metric lifecycle are explicit; `tanh` and endpoint averaging are pressured V4 choices, not theory-selected formulas |
| A provenance | A's causal architecture is unchanged, but vertex-star `K_4` assembly is newly typed by D4-v2 |
| Inherited debt | All 2 immediate and 20 transitive live rows are bound by exact ID, status, blocker flag, source SHA, and D7 digest |

## Common Structural Domain

D4-v2 freezes the graph-domain crossing:

```text
S_4^a -> iota_a -> K_4^a -> deferred H_4 -> deferred h_4
```

For the initial fixed-live-edge stratum, `K_4` is an **assembled graph-local**
symmetric bilinear form on the oriented edge one-form space `Omega^1_G`. It is
not an arbitrary dense edge-by-edge matrix. Local stalk contributions are
assembled as:

```text
K_4 = sum_s R_s^T K_4,s R_s
```

where `R_s` restricts to a declared node star or other preregistered
finite-radius neighborhood. Any local quadrature or partition weight is part
of the corresponding `K_4,s`; unrecorded overlap multiplicity is not an
admissible normalization. D4-v2 freezes the exact locality/covariance class,
not one numerical partition. D7G must freeze the assembly weights and units.
The initial A contribution is assembled from
vertex-star `j_v tensor j_v` terms, B has radius-one line-graph support, and C
can enter only through the same local current-tensor route after retained
mediation and current closure. A graph-global nonlocal `K_4` would require a
named successor rather than arising from a global `j j^T` array operation.
With `U` a signed edge permutation, covariance requires:

```text
K_4' = U K_4 U^T
```

`K_4` is derived, nonresource, and not transport mobility. Each candidate
declares its payload units and a typed conversion into common `K_4` units;
dimensionlessness is not assumed globally. Absolute metric scale, measure
response, and dimension-changing topology transport remain D7G/D9 debt.

An adapter claimed as a direct retained structural crossing is load-bearing
only when a lawful matched retained-state intervention changes its output
`K_4^a`. Type-correct but structurally inert adapters fail closed. C makes no
such direct claim at D4-v2; its common route remains deferred.

Candidate A's causal architecture is carried unchanged. D4-v2 nevertheless adds
one new common-interface result by typing its previously abstract
`j_A tensor j_A` contribution as graph-local vertex-star assembly. This does
not reopen A's retained/read/write architecture or close `H_4`.

## Candidate B Representation Pressure

D4-v2 pressured six graph representation families.

| Family | Disposition | Reason |
|---|---|---|
| Node scalar | Restricted isotropic subprofile | Needs a lift before it can act directionally on one-forms |
| Unoriented edge scalar | Diagonal subprofile | Structurally usable only if kept distinct from A mobility |
| Oriented edge cochain | Broader admissible family, not selected | Can retain sign but needs a separately typed structural or Read-Back consumer; one rank-one lift losing sign does not reject oriented content |
| Unrestricted dense edge operator | Outside initial profile | Permits nonlocal capacity without a graph-locality contract |
| Bounded graph-local general endomorphism / symmetric plus skew carrier | Broader admissible family, not selected | Symmetric content can enter `K_4`; skew/non-normal content could remain for D5, but those extra degrees are not required and have no D4 structural consumer |
| Bounded graph-local symmetric edge bilinear form | Selected bounded family | Contains the diagonal minimal subprofile and optional radius-one route relations, has a native structural consumer, and remains distinct from A/C |

The selected independent carrier is:

```text
T_B in Sym_L(Omega^1_G x Omega^1_G)

T_B = T_B^T
T_B' = U T_B U^T
support(T_B) subset of declared line-graph locality mask L_B
L_B(e,f) = 1 iff d_L(G)(e,f) <= 1

[T_B] = [H_1,pre]
Theta_B = H_1,pre^(-1/2) T_B H_1,pre^(-1/2)
||Theta_B|| <= t_B,max
```

Thus `T_B` is metric-typed, while `Theta_B` and the conditioning endomorphism
`H_1,pre^(-1) T_B` are dimensionless. `L_B` permits only identical or incident
live-edge pairs, is reconstructed from the unordered graph, and transforms
with graph relabeling rather than array order. D9 must define how `T_B` and its
mask cross topology events.

Its generalized spectrum may be signed. The sign records only the direction of
the candidate contribution in the `K_4` bilinear representation; it does not
establish continuation hardening or softening before `H_4` and D8. `T_B = 0`
is neutral. `T_B` is independent, serialized, nonresource, and contains all
persistent B information; hidden history is forbidden.

Because the capacity bound is measured through `Theta_B` relative to
`H_1,pre`, a later accepted `h_4/H_1` change can change admissibility even when
stored `T_B` is unchanged. D7G must recompute `Theta_B` and readmit the B state
domain. It may not preserve admission through silent clipping,
renormalization, or threshold retuning.

This is explicitly a revision-level V4 extension candidate. It is not inherited
or derived from the coherence-only primitive state. In a disabled profile,
`T_B` has no writer, consumer, serialization authority, or causal effect.

The selected B geometry completion is:

```text
S_4^B = G_B(C,T_B,K_4,base) = T_B
K_4^B = K_4,base + kappa_B S_4^B
iota_B(S) = kappa_B S
```

`kappa_B` is a finite, preregistered, nonzero coefficient frozen before
candidate evaluation, with units converting an
`H_1,pre`-typed bilinear form into `K_4`. The map is injective, neutral at
`T_B = 0`, and does not write mobility or coherence resource. A matched
admissible `T_B` intervention therefore changes `K_4^B`.

The future B Read-Back operator acts on the declared pre-read physical
one-form space `Omega^1(h_4,pre)`. The carrier induces a typed conditioning
endomorphism `H_1,pre^(-1) T_B`, but D4-v2 does not equate that object with
`R_B`. D5-v2 must derive the actual directional response.

Candidate B result:

```text
D4v2 disposition = admitted_bounded_candidate_geometry_and_carrier_completion
D5v2 eligible = true
```

Its exact writer, release/reconfiguration law, total-current closure, topology
lifecycle, and complete transition remain later-gate debt.

## Candidate C Retained Geometry Completion

The initial C profile uses only the state-level spatial retained sector:

```text
L_0,sym,pre = H_0,pre^(-1/2) B_pre H_1,pre B_pre^T H_0,pre^(-1/2)
Q_M = 1_[0,Lambda_C](L_0,sym,pre)
P_M^Delta = H_0,pre^(-1/2) Q_M H_0,pre^(1/2)
T_C,k = P_M^Delta C_k
```

`Lambda_C` is a preregistered finite constitutive profile parameter, not selected
after observing D4-v2 outcomes. The initial profile uses the declared
self-adjoint closed/no-flux boundary incidence. It admits only fixed-topology,
fixed-boundary strata with positive diagonal Hodge stars and a strict gap
`lambda_m < Lambda_C < lambda_(m+1)`. Exact cutoff degeneracy, rank loss, or gap
loss exits the smooth stratum rather than selecting modes by array order. The
weighted projector is deterministic derived state, `H_0,pre`-orthogonal, and
graph-isomorphism covariant. The branch-relative dynamic sector remains
analysis-only.

The cutoff is typed against the preregistered pre-read scalar-Laplacian scale:

```text
Lambda_C = bar_Lambda_C sigma_L,pre
[Lambda_C] = [L_0,sym,pre]
bar_Lambda_C = finite dimensionless constitutive profile parameter
```

The scale `sigma_L,pre` is frozen with the pre-read metric and boundary context
as a profile-owned dimensional reference declared before candidate evaluation.
It is not computed from observed eigenvalues, candidate outcomes, or desired
mode membership. Under a pure units/gauge change it co-transforms with
`L_0,sym,pre` and `Lambda_C`; a physical `h_4` change does not retune it. D7G
must recompute the selector and revalidate its strict gap and rank after an
accepted physical `h_4` scale change; it may not preserve membership by
silently clipping, renormalizing, or retuning the cutoff.

D4-v2 selects a bounded positive graph-Hodge specialization of the open
`H_M` family. Let:

```text
rho_C,v = tanh(T_C,v / C_ref)
r_C,e = (rho_C,u + rho_C,v) / 2
D_C = diag(exp(kappa_M,C r_C / 2))

H_0,M = H_0,pre
H_1,M = D_C H_1,pre D_C
h_M^G = (H_0,M, H_1,M, declared incidence/boundary context)
```

`C_ref > 0`, dimensionless `kappa_M,C` is finite, and the pre-read Hodge stars
are positive diagonal graph Hodge stars. The congruence therefore preserves
positivity. `T_C = 0` or `kappa_M,C = 0` returns the pre-read graph geometry
algebraically. `T_C = 0` is not presumed reachable or physically neutral: a
runtime neutral/reference requires a matched admissible C state, or the
explicit disabled `kappa_M,C = 0` profile. The sign of `kappa_M,C` is
constitutive and does not claim a universal reinforcement or softening law.

This choice follows a parallel family pressure. Identity `h_M = h_4,pre` is
structurally inert. An additive Hodge update needs an extra positivity
projection. A joint conformal `H_0/H_1` update is admissible but confounds this
gate with volume and resource-measure response. A dense anisotropic update adds
cross-edge structure not carried by the selected scalar sector. The diagonal
positive congruence is the minimal non-erasing bounded profile that preserves
`H_0` while changing one-form geometry.

The inner retained-to-edge map was pressured independently of that outer Hodge
choice:

| Inner-map family | D4-v2 disposition |
|---|---|
| Unsaturated normalized amplitude | Admissible local linear profile, but unbounded unless the retained-state domain supplies a separate bound |
| Smooth bounded odd map | Admissible family; preserves sign and avoids clipping state |
| `tanh(T_C/C_ref)` | Selected bounded V4 representative, not theory-selected |
| Gradient/even edge lift | Admissible for a different role, but loses the selected sign-sensitive endpoint content |
| Symmetric endpoint mean | Selected unoriented-edge lift; orientation-independent and graph-local |

Thus neither `tanh` nor endpoint averaging is promoted to a unique core-theory
formula. They are pressure-tested constitutive choices whose replacements
would reopen the affected C maps.

This map is graph-native, covariant, nonresource, nonserialized, and explicitly
staged:

```text
h_4,pre -> P_M^Delta -> T_C -> H_M -> h_M
```

It avoids a same-beat selector/geometry fixed point without claiming that this
is the only possible C staging.

Here the retained sector and schematic `H_M` role are source-backed; the
positive graph-Hodge formula is the revision-specific candidate specialization.

The positive `(H_0,M,H_1,M)` pair is a graph-Hodge geometry package. D4-v2 does
not claim that every such pair is the discretization of one continuum
Riemannian metric; D7G/D8 must classify that compatibility before a stronger
geometry claim.

The canonical candidate-local current identification is now instantiated:

```text
I_4M^pre = H_1,M H_1,pre^(-1)
(I_4M^pre)^(-1) = H_1,pre H_1,M^(-1)

I_4M^pre:
  Omega^1(h_4,pre) -> Omega^1(h_M)
```

It is signed-edge-basis covariant, invertible on the positive fixed-dimension
profile, and represents the same physical vector under different metric
lowerings. It is not assumed isometric. This explicitly reopens the prior
parameterized C isometry assumption for D6-v2.

The candidate-local scaling generator is:

```text
log(D_C^2) = kappa_M,C diag(r_C)
```

Because both `D_C` and the initial `H_1,pre` Hodge star are diagonal, this is a
valid local coordinate scaling generator. It is not promoted to a basis-free
relative logarithm of global `H_4`.

The retained geometry is load-bearing under a same-state intervention:

```text
C, P_M^Delta, T_C, topology, boundary, and H_1,pre matched
kappa_M,C != 0  versus  kappa_M,C = 0
nonzero r_C     implies H_1,M differs
```

This isolates `T_C -> H_M -> h_M` without varying `C` and therefore without
confounding the result with ordinary baseline `C` or gradient geometry.

D4-v2 does **not** add a direct `T_C -> diag(r_C) -> K_4` adapter. Such a term
would be a second revision-specific structural mechanism, and a `delta C`
intervention could not isolate it because `K_4,base(C,grad C,...)` also changes.
The common structural route for C remains the source-backed retained-mediated
current path, with an explicit return to the common physical one-form
representation:

```text
T_C -> H_M -> R_C -> j_C^(M,flat)
j_C^(phys,flat) = (I_4M^pre)^(-1) j_C^(M,flat)
    -> graph-local vertex-star assembly of
       j_C^phys tensor j_C^phys
    -> K_4
```

D5-v2 must first establish genuine retained mediation, D6-v2 must close the
authoritative current relation, and D7G must type and integrate the resulting
local tensor contribution. Raw `h_M`-coordinate arrays may not enter common
`K_4` merely because their edge dimension matches.

The three C switches remain separate:

```text
retained_geometry_off: kappa_M,C = 0
  removes T_C conditioning from h_M and its direct J_0,C baseline path

read_off: chi_C = 0
  removes explicit j_C and the j_C tensor structural route
  preserves T_C-conditioned h_M -> J_0,C

gain_off: zeta_C = 0
  diagnostic j_C may remain
  j_C cannot change total current or K_4
  preserves T_C-conditioned h_M -> J_0,C
```

No direct `T_C -> K_4` route survives or bypasses current closure. The
retained-conditioned baseline path and explicit Read-Back structural path may
not be averaged together or counted as the same evidence.

Candidate C result:

```text
D4v2 disposition = admitted_bounded_candidate_retained_geometry_completion
D5v2 eligible = true
```

D5-v2 must now test whether the accepted Hodge response becomes genuinely
`T_C`-conditioned through this `H_M`, rather than merely parameterized by an
externally supplied metric.

## Scientific Result

| Candidate | D4-v2 completion | Next unresolved crossing |
|---|---|---|
| A | Causal architecture carried unchanged; vertex-star `j_A tensor j_A` assembly newly typed in the common `K_4` domain | Global `H_4` and prior A debts |
| B | Independent bounded graph-local structural carrier, `G_B`, adapter, and current space | `R_B`, current closure, writer, lifecycle |
| C | Spatial retained sector, positive graph-Hodge `H_M`, and non-isometric `I_4M^pre`; direct `T_C -> K_4` adapter not admitted | On-manifold `R_C`, current closure, inverse-`I_4M^pre` physical-current back-map, source-backed `j_C^phys tensor j_C^phys -> K_4` route, write/read transition, global compatibility |

No candidate is selected or ranked. B and C are now D5-v2 eligible for distinct
reasons and with distinct ontologies.

The hardened decision has 46 fail-closed controls. In addition to the original
authority and relabel controls, it rejects B unit mismatch or undefined
locality, B minimality/sign overclaim, stale metric-relative B capacity,
unbounded or post-hoc `kappa_B`, an
uninstantiated or degenerate C selector, a direct retained-state
`K_4` mechanism disguised as the source-backed current route, `delta C`
misattribution, C switch conflation, raw `h_M` current insertion, adaptive
cutoff selection, cutoff unit/gauge drift, unpressured inner-map selection,
algebraic-neutral/runtime-neutral conflation, local-log/global-log promotion,
arbitrary dense or multiplicity-dependent `K_4` assembly, A-provenance erasure,
and count-only inherited debt carry-forward.

## Claim Ceiling

D4-v2 supports bounded candidate constitutive completions for B and C at the
carrier/retained-geometry layer. It does not support:

- B or C directional Read-Back closure;
- B or C total-current or complete transition closure;
- uniqueness or core-theorem status of either selected specialization;
- common `H_4 -> h_4` closure;
- runtime reachability, stability, or empirical mediation;
- candidate ranking, normative specification, or implementation authority.

## Next Gate

D4-v2 is accepted bounded. D5-v2 is authorized, but not started, to derive
separately typed B and C directional
Read-Back operators from these objects. Candidate A's causal architecture
remains unchanged unless a new causal dependency reopens its earlier record;
the D4-v2 vertex-star discretization remains a new common-interface result.
If D5-v2 gives B a source-patterned `j_B tensor j_B -> K_4` path, it must keep
that route distinct from B's admitted direct `T_B -> K_4` route under read-off,
gain-off, and path-overlap controls; neither route may double-count the other as
evidence.

Decision digest:
`5862cbab0d36e1137dc647d7d21d48f77666a77bf9e7b178c830d323e4ed6309`.
