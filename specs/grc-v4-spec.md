# GRCV4 Specification

## Status and authority

This file is the normative implementation contract for the D10-backed,
graph-generic `GRCV4` substrate and the current admitted profile population,
subject to the D11 holds below. Candidate C implementation conformance is on
bounded hold until D11-C accepts a baseline-transport law. The displayed
D11-C candidate is retained for evaluation but is not yet normative.

Primary sources:

- [GRC-v4 substrate paper][paper]
- [GRC-v4 proposal and provenance crosswalk][proposal]
- [D10 design synthesis and specification-writing decision][d10]
- [D10.2 substrate provenance and promotion audit][d10-2]
- [D11 bounded successor opening][d11-open]
- [D11-C Candidate C transport preregistration][d11-c]
- [V4 source identity manifest](grc-v4-source-manifest.json)
- [V4 conformance fixture contract](grc-v4-conformance-fixtures.json)
- [Common GRC interface](grc-common-interface.md)
- [Common GRC interface: V4 extension](grc-common-interface-v4-ext.md)

The paper owns the mathematical meaning. The proposal supplies the complete
claim and provenance crosswalk. D10 and D10.2 preserve claim status and the
bounded source classification. This specification translates those sources
into implementation requirements; it does not create scientific evidence.

The accepted forensic reconstruction used for this translation has source
bundle digest
`79e84f7839e1b65f3e55eeadb980e6d8d9b57d240aced93a8bf3a7e82851dffc`
and graph digest
`2776d2aa1aca51f7759c94ed0e9677a04934429b070bb8ea47683cbcd8f218ae`.
It contains 39 current claims, 67 normative objects, 152 equation contracts,
and 10 current complete profiles. The forensic contract edges retain
`indeterminate_requires_review` support semantics; this spec does not promote
those edges into stronger evidence. The source-local label
`D10_2_CL_N_001` is a provenance reference, not a queryable claim node.

The typed contract destinations map into the specs as follows:

| Forensic destination | Contracts | Normative destination |
|---|---:|---|
| `GRCV4_current_promoted_common_core` | 14 | Common resource, transport, charge, and differential sections below. |
| `GRCV4_current_promoted_common_core+GRCV4_current_promoted_common_lifecycle` | 1 | Charge gate in the complete-step transaction. |
| `GRCV4_current_promoted_common_geometry` | 10 | Structural geometry and current typing. |
| `GRCV4_current_promoted_common_transport` | 2 | Candidate-specific mobility boundary. |
| `GRCV4_current_promoted_core_theory_basis` | 1 | Abstract $K$ versus graph $K_4$ boundary. |
| `GRCV4_reference_profile` | 1 | Unit-measure charge profile. |
| `GRCV4_candidate_A` | 7 | Candidate A contract. |
| `GRCV4_candidate_A_lifecycle` | 1 | Candidate A history-free initializer. |
| `GRCV4_candidate_C` | 10 | Candidate C contract. |
| `GRCV4_optional_realization` | 29 | Five realization contracts. |
| `GRCV4_current_promoted_common_lifecycle` | 15 | Step, migration, event, snapshot, and atomicity contracts. |
| `GRCV4_current_population_specification_grammar` | 8 | Profile identity, claims, and successor admission. |
| `GRC9V4_specialization` | 53 | [`grc-9-v4-spec.md`](grc-9-v4-spec.md). |

### D11 successor hold and preregistration boundary

The September 2026 specification-stack audit identified two places where the
accepted source graph names a required object without fixing an executable
map: Candidate C's baseline transport and the collision-free GRC9 expansion
port allocation. These are genuine gaps in accepted authority, not extraction
omissions. Two separate investigations are therefore open in sequence:

- D11-C is active for the graph-generic Candidate C direct-transport law; and
- D11-G9 is queued behind D11-C for the GRC9V4-only port allocation.

The existing formulas remain in place as preregistered candidates so the D11
investigations can pressure them directly. They are not post-D10 normative
closures, backward evidence, or implementation authority. An accepted D11
result must first be propagated into the GRC-v4 paper and only then extracted
back into the affected spec clauses. `GRCV3`, `GRC9`, and `GRC9V3` remain
unchanged read-only sources or reduction targets; all adaptation remains
V4-owned.

## Conformance language

The words **must**, **must not**, **required**, **shall**, and **shall not** are
normative. **May** identifies an admitted option. **Should** is implementation
guidance.

Claim classes are applied as follows:

- normative claims become common requirements;
- optional claims become named opt-in candidate or realization contracts;
- conditional claims remain gates on stronger conformance or evidence claims;
- open claims remain nonimplemented or explicitly experimental surfaces; and
- negative claims become prohibited relabels or overclaims.

An implementation conforms to `GRCV4` only if it implements the common
contract and at least one complete profile identity from the current
population. It may support any nonempty subset of that population, but it must
name the exact subset. Supporting one profile does not imply support for any
other profile. While D11-C is open, the five Candidate C identities remain
admitted design profiles but are unavailable for implementation-conformance
claims; a presently conforming subset may contain Candidate A profiles only.

## Class

```python
class GRCV4(GRCModel):
    ...
```

`GRCV4` must implement the [common GRC interface](grc-common-interface.md) as
strengthened by the
[V4 common-interface extension](grc-common-interface-v4-ext.md). There is no
executable candidate-free or realization-free `GRCV4` transition.

## Capabilities

Every conforming instance must advertise:

- `profile_explicit_v4`
- `single_resource_ledger`
- `authoritative_current`
- `structural_hodge_geometry`
- `typed_topology_events`
- `profile_migration`
- `quadrature_budget`

It must advertise candidate and realization capabilities only when the named
profiles are implemented:

| Supported content | Required capability |
|---|---|
| Candidate A | `v4_candidate_a_retained_mobility` |
| Candidate C | `v4_candidate_c_derived_sector` |
| CI | `v4_realization_ci` |
| OS | `v4_realization_os` |
| RG2b | `v4_realization_rg2b` |
| PC | `v4_realization_pc` |
| CI+PC | `v4_realization_ci_pc` |

Capabilities report implemented behavior, not planned support or scientific
evidence. `GRCV4` must not advertise nine-port mechanics; those belong to
[`GRC9V4`](grc-9-v4-spec.md).

## Complete profile identity

The current population is

$$
\{\mathrm A,\mathrm C\}
\times
\{\mathrm{CI},\mathrm{OS},\mathrm{RG2b},\mathrm{PC},\mathrm{CI+PC}\}.
$$

The canonical identifiers are:

```text
A_CI       C_CI
A_OS       C_OS
A_RG2b     C_RG2b
A_PC       C_PC
A_CI_PC    C_CI_PC
```

Every executable state must bind exactly one of these identities. Candidate,
realization, geometry profile, differential backend, charge profile, units,
gauge, normalization, domain, solver/root selector, composition gain,
lifecycle policy, and all trajectory-changing coefficients are part of the
complete identity.

```python
CandidateId = Literal["A", "C"]
RealizationId = Literal["CI", "OS", "RG2b", "PC", "CI+PC"]
ProfileFamilyId = Literal[
    "A_CI", "C_CI", "A_OS", "C_OS", "A_RG2b", "C_RG2b",
    "A_PC", "C_PC", "A_CI_PC", "C_CI_PC",
]

@dataclass(frozen=True)
class GRCV4ResolvedParams:
    schema_version: Literal["grcv4-resolved-params-v1"]
    common: Mapping[str, JSONValue]
    candidate: Mapping[str, JSONValue]
    realization: Mapping[str, JSONValue]
    geometry: Mapping[str, JSONValue]
    solver: Mapping[str, JSONValue]
    lifecycle: Mapping[str, JSONValue]

@dataclass(frozen=True)
class GRCV4Profile:
    profile_family_id: ProfileFamilyId
    complete_profile_id: str
    candidate: CandidateId
    realization: RealizationId
    differential_backend_id: str
    charge_profile_id: str
    geometry_profile_id: str
    context_contract_id: str
    units_id: str
    gauge_id: str
    normalization_id: str
    domain_id: str
    solver_id: str
    lifecycle_policy_id: str
    candidate_c_transport_id: str | None
    composition_gain: float | None
    params_resolved: GRCV4ResolvedParams
    params_hash: str
```

`profile_family_id`, `candidate`, and `realization` must agree exactly. The
family identifier is not by itself a complete identity. `params_resolved` is
serialized as UTF-8 JSON with lexicographically ordered object keys, preserved
array order, no insignificant whitespace, and finite JSON numbers only. NaN,
infinity, negative zero, duplicate keys, and implementation-native object
encodings are forbidden. `params_hash` is
`"sha256:" + SHA256(canonical_params_bytes)`, and `complete_profile_id` is the
same construction over the family identifier, every identity field above,
and `params_hash`.

A different composition gain, writer, geometry map, Candidate C transport
law, selector policy, solver, units, normalization, or lifecycle rule
therefore produces a different `complete_profile_id`. A snapshot must carry
both the resolved payload and its digest; a digest without the payload is not
reconstructible authority. Schema evolution requires a new schema version and
an explicit typed migration, never in-place reinterpretation.

Candidate B is reserved and nonexecutable. It may be admitted only after a
source-backed $U_B$ formation, retention, release, capacity, and lifecycle
writer has passed successor admission. Candidate B is routed, not rejected;
Candidate A, Candidate C, and PC must not be relabeled as B.

## State and authority

### Authoritative dynamic state

| Complete profile | Authoritative dynamic coordinates | Independent realization history |
|---|---|---|
| `A_CI`, `A_OS`, `A_RG2b` | $C,W_A$ | none |
| `C_CI`, `C_OS`, `C_RG2b` | $C$ | none |
| `A_PC`, `A_CI_PC` | $C,W_A,Z_{4,A}$ | $Z_{4,A}$ |
| `C_PC`, `C_CI_PC` | $C,Z_{4,C}$ | $Z_{4,C}$ |

$C$ is the only resource coordinate. $W_A$ and $Z_{4,a}$ are authoritative
nonresource coordinates only in the rows that declare them. Candidate C has
no independent $T_C$ state.

```python
@dataclass(frozen=True)
class GRCV4AuthoritativeState:
    C: ArrayLike
    W_A: ArrayLike | None
    Z_4: ArrayLike | None

@dataclass(frozen=True)
class GRCV4ResetBaseline:
    authoritative: GRCV4AuthoritativeState
    graph_identity: str
    orientation_identity: str
    complete_profile_id: str
    context_contract_id: str

@dataclass(frozen=True)
class GRCV4LifecycleState:
    step_index: int
    time: float
    graph: SerializedGraphState
    orientation_identity: str
    profile: GRCV4Profile
    context_identity: str
    current: GRCV4AuthoritativeState
    reset: GRCV4ResetBaseline
    Q_target: float
    lifecycle_receipts: tuple[LifecycleReceipt, ...]

@dataclass(frozen=True)
class GRCV4State(GRCState):
    lifecycle: GRCV4LifecycleState
```

`GRCV4State.budget_target` is a compatibility property backed by
`lifecycle.Q_target`; it is not separately stored. The lifecycle object is the
single owner of graph, profile, reset, target, clock, and persistent receipt
authority. The reset baseline contains only reset-authoritative scientific
coordinates and the identities needed to readmit them; it is not a second
live runtime with independent caches, receipts, RNG, or clock.

The current V4 population is deterministic. It has no scientific `rng_state`.
A stochastic successor must add an identity-bearing RNG algorithm, seed/state,
sampling stage, distribution, serialization, and replay contract under a new
profile identity.

The implementation must validate the tagged state shape:

- Candidate A requires positive edge-valued $W_A$; Candidate C requires
  `W_A is None`.
- PC and CI+PC require candidate-local $Z_4$ in the admitted $K_4$ carrier
  space; CI, OS, and RG2b require `Z_4 is None`.
- `current` and `reset` states must bind compatible graph, context, profile,
  parameter, charge, and lifecycle identities.
- `graph` must contain the canonical serialized graph payload or an exact
  reconstructible graph identity; a family state with neither is invalid.

Authoritative arrays and mappings exposed through `get_state()` must be
immutable/read-only or deep copies. Mutation outside `set_state()` or a typed
V4 transaction must be impossible. Derived caches live outside scientific
state; if a snapshot carries a cache for inspection, it is representation-only,
provenance-bound, excluded from scientific equality, and rejected or rebuilt
when stale.

### Derived and transient surfaces

Potential, baseline current, Read-Back current, authoritative same-beat
current, selector, $T_C$, Hodge operators, $K_4$, $h_4$, solver roots,
predictors, correctors, RG2b section values, and analysis operators are derived
or transient. They may be cached or serialized for exact inspection, but that
does not give them cross-beat authority.

Every cache must carry the identities and stage inputs from which it was
derived. A stale or mismatched cache must be rebuilt or rejected; it must never
silently enter a transition.

## Graph and differential backend

The graph is finite and oriented for coordinate purposes. With $B$ mapping
oriented edge fluxes to vertex divergence,

$$
d_0:=B^\top.
$$

The selected backend must deterministically provide:

- stable vertex and oriented-edge order;
- incidence and boundary semantics;
- scalar-to-edge differential operations;
- declared vertex and one-form pairings;
- graph relabeling and signed-edge reorientation actions; and
- reproducible reconstruction from serialized identity.

No nine-port row basis is part of this generic contract. A backend that
changes values, regularity, normalization, or semantic interpretation is part
of complete profile identity.

## Common resource and transport contract

For positive scalar edge mobility $W_e>0$, the inherited reference channel is

$$
\Phi_i
=
\kappa\sum_j W_{ij}(C_i-C_j)-V'(C_i),
$$

$$
J_{0,e}=-\eta W_e(B^\top\Phi)_e.
$$

The selected candidate and realization may add Read-Back and geometry
coupling. Potential flow is therefore not universally identical to the one
authoritative current $J_C$.

Continuity executes exactly once:

$$
C_{\mathrm{next}}
=C-\Delta t\,BJ_C+B_{\mathrm{ext}}+S_{\mathrm{ext}}.
$$

External terms must be typed by the active ordinary-step or event contract.
The current population uses a closed-internal ordinary beat with
$B_{\mathrm{ext}}=S_{\mathrm{ext}}=0$.

## Charge contract

For the declared charge covector $\varpi$,

$$
Q_\varpi(C)=\varpi^\top C,
\qquad
DQ_\varpi[\delta X]=\varpi^\top\delta C.
$$

In particular, geometry is outside the resource functional:

$$
D_hQ_\varpi=0.
$$

Thus

$$
V_{Q,\varpi}
=\{\delta X:\varpi^\top\delta C=0\}.
$$

Nonresource coordinates do not contribute to charge. The current reference
profile uses $\varpi=\mathbf 1$ and $Q(C)=\sum_iC_i$, but unit measure is a
named profile rather than a universal theorem.

For positive vertex Hodge operator $H_0$, the resource-sector projector is

$$
\Pi_{Q,C,H_0}(\delta C)
=\delta C-H_0^{-1}\varpi
\frac{\varpi^\top\delta C}{\varpi^\top H_0^{-1}\varpi}.
$$

Its canonical full-tangent retraction is

$$
R_Q(\delta C,\delta X_{\mathrm{nr}})
=\bigl(\Pi_{Q,C,H_0}(\delta C),\delta X_{\mathrm{nr}}\bigr).
$$

This is not a full-state orthogonal projector without a separately declared
product metric.

After continuity and before any final-$C$ writer, the implementation must
validate

$$
C_{\mathrm{next}}\ge0,
\qquad
Q_\varpi(C_{\mathrm{next}})=Q_{\mathrm{target,next}}.
$$

For current unit-measure profiles, a budget projection must be an identity/no-op;
a nontrivial repair fails the beat.

## Structural geometry and current typing

$K_4$ is a graph-local symmetric bilinear object on oriented one-forms. It is
not the abstract core role $K$, a legacy node tensor, transport mobility, or a
persistent state coordinate.

For vertex-star restrictions $R_v$ and overlap weights
$(D_v)_{ee}=m_e^{-1/2}$,

$$
\sum_vR_v^\top D_v^2R_v=I,
$$

$$
\mathcal A_\star(j^\flat)
=\sum_vR_v^\top\bigl(D_vR_vj^\flat\bigr)
\bigl(D_vR_vj^\flat\bigr)^\top R_v.
$$

Candidate $a$ converts this assembly into $S_a=\Delta K_{4,a}$ through
its typed adapter and declared gain. The exact A and C equations below govern
that conversion; the common layer does not infer a universal gain or absorb an
external candidate gain into $\iota_a$.

The reference package is

$$
H_{0,\mathrm{ref}}=\operatorname{Diag}(\mu),
\qquad
H_{1,\mathrm{form,ref}}=\operatorname{Diag}(W_{\mathrm{ref}}),
\qquad
G_{J,\mathrm{ref}}=\operatorname{Diag}(W_{\mathrm{ref}}^{-1}).
$$

The reference geometry package is

$$
h_{4,\mathrm{ref}}
=\bigl(
H_{0,\mathrm{ref}},H_{1,\mathrm{form,ref}},
B_{\mathrm{ref}},\mathrm{boundary}_{\mathrm{ref}}
\bigr).
$$

$G_J$ lowers physical flux to structural one-form coordinates:

$$
j_{\mathrm{struct}}^\flat=G_J(h)j_{\mathrm{flux}}.
$$

For the accepted affine reference-relative geometry profile,

$$
\Theta_4
=\kappa_HH_{1,\mathrm{form,ref}}^{-1/2}
\Delta K_4H_{1,\mathrm{form,ref}}^{-1/2},
\qquad I+\Theta_4\succ0,
$$

$$
H_{1,\mathrm{form}}^+
=H_{1,\mathrm{form,ref}}+\kappa_H\Delta K_4,
\qquad
H_0^+=H_{0,\mathrm{ref}},
\qquad
G_J(h_4^+)=\bigl(H_{1,\mathrm{form}}^+\bigr)^{-1}.
$$

The load-bearing crossing is

$$
K_4\longrightarrow(H_0,H_{1,\mathrm{form}},G_J)\longrightarrow h_4.
$$

The geometry profile has one canonical signature:

```python
def H_profile(
    K_4: K4Tensor,
    *,
    reference: GRCV4ReferenceGeometry,
    context: GRCV4Context,
    profile: GRCV4Profile,
) -> GRCV4Geometry:
    ...
```

Every shorter mathematical occurrence such as
$H_{\mathrm{profile}}(K_4)$ suppresses arguments already bound by the active
complete profile; it is not a different overload or permission to choose new
defaults. Reference, context, or profile changes that can change the result
change the complete identity or require a typed migration.

The implementation must preserve the distinct types

$$
M_4\ne H_{1,\mathrm{form}}\ne G_J\ne h_4
\ne\mathcal A_\star(j^\flat).
$$

Graph relabeling and signed edge reorientation act covariantly. If $U$ is the
signed edge permutation, then

$$
\Delta K_4'=U\Delta K_4U^\top,
\qquad
H_{1,\mathrm{form}}'=UH_{1,\mathrm{form}}U^\top.
$$

Fixed-space covariance does not define transport across topology changes.

## Candidate A contract

Candidate A is optional, normalized, nondimensional, and revision-specific.
It is not inherited core and is not the unique V4 completion.

Its transport mobility is

$$
M_{4,A}(W_A)=\eta\operatorname{Diag}(W_A),
\qquad W_{A,e}>0.
$$

At reference geometry,

$$
\Phi_{A,i}^{D7}
=\kappa_c\sum_{e\sim i}W_{A,e}
\bigl(C_i-C_{\operatorname{nbr}(e,i)}\bigr)
-V_{\mathrm{site}}'(C_i),
$$

$$
J_{0,A}^{D7}=-M_{4,A}(W_A)d_0\Phi_A^{D7}.
$$

When the realization supplies nonreference geometry,

$$
\Delta_0(h)
=H_{0,\mathrm{ref}}^{-1}BH_{1,\mathrm{form}}(h)B^\top,
$$

$$
\Phi_A(C,W_A,h)
=\Phi_A^{D7}(C,W_A)
+\kappa_{Ah}\bigl[\Delta_0(h)-\Delta_0(h_{\mathrm{ref}})\bigr]C,
$$

$$
J_{0,A}(C,W_A,h)=-M_{4,A}(W_A)d_0\Phi_A(C,W_A,h).
$$

This geometry consumer does not transfer mobility authority from $W_A$ to
$h_4$.

The accepted curvature-disabled conductance functional is

$$
G_{W,e}(C,J)
=\max\!\left(
W_{\mathrm{floor}},
\exp\!\left[
-\alpha\frac{C_u+C_v}{2}
-\frac{\beta}{2}\lVert D_u(C)-D_v(C)\rVert^2
-\frac{\gamma}{2}J_e^2
\right]
\right).
$$

At the fresh pre-read stage,

$$
\widehat W_A=G_W(C,J_{0,A}),
\qquad
q_{A,e}=\frac{W_{A,e}-\widehat W_{A,e}}
{W_{A,e}+\widehat W_{A,e}}.
$$

The explicit read and current closure are

$$
j_{A,\mathrm{flux}}
=\chi_A\operatorname{Diag}(q_A)J_{C,A},
\qquad
J_{C,A}=J_{0,A}+\zeta_Aj_{A,\mathrm{flux}}.
$$

On a regular fixed-geometry profile this gives, edgewise,

$$
J_{C,A,e}=\frac{J_{0,A,e}}
{1-\zeta_A\chi_Aq_{A,e}}.
$$

The structural source is

$$
j_A^\flat=G_J(h)j_{A,\mathrm{flux}},
\qquad
S_A(J,h)=\zeta_A\iota_A\!\left(
\mathcal A_\star(j_A^\flat)
\right).
$$

After continuity and charge admission, rebuild all final-$C$ differential
inputs and define

$$
W_{\mathrm{drv},A,k}=G_W(C_{k+1},J_{C,A,k}),
\qquad
a_{A,k}=\exp\!\left(-\frac{\Delta t_k}{\tau_A}\right).
$$

The single retained writer is

$$
\log W_{A,k+1}
=a_{A,k}\log W_{A,k}
+(1-a_{A,k})\log W_{\mathrm{drv},A,k}.
$$

The new $W_{A,k+1}$ must not re-enter the beat-$k$ current solve.

## Candidate C contract

Candidate C is optional and revision-specific. $C$ remains its only candidate
state; its selector, selected sector, Hodge response, and Read-Back surfaces
must be rederived.

At prestate geometry,

$$
L_{0,\mathrm{sym,pre}}
=H_{0,\mathrm{pre}}^{-1/2}B
H_{1,\mathrm{form,pre}}B^\top
H_{0,\mathrm{pre}}^{-1/2},
$$

$$
Q_M=\mathbf 1_{[0,\Lambda_C]}(L_{0,\mathrm{sym,pre}}),
\qquad
P_M^\Delta=H_{0,\mathrm{pre}}^{-1/2}Q_MH_{0,\mathrm{pre}}^{1/2},
\qquad
T_C=P_M^\Delta C.
$$

A smooth selector chart must declare a rank gap
$\lambda_m<\Lambda_C<\lambda_{m+1}$.

Define

$$
\rho_{C,v}=\tanh\!\left(\frac{T_{C,v}}{C_{\mathrm{ref}}}\right),
\qquad
r_{C,e}=\frac{\rho_{C,u}+\rho_{C,v}}{2},
$$

$$
\mathsf{D}_C
=\operatorname{Diag}\!\left(
\exp\!\left[\frac{\kappa_{M,C}}{2}r_C\right]
\right),
$$

$$
H_{0,M}=H_{0,\mathrm{pre}},
\qquad
H_{1,\mathrm{form},M}
=\mathsf{D}_C H_{1,\mathrm{form,pre}}\mathsf{D}_C,
\qquad
I_{4M}=H_{1,\mathrm{form},M}H_{1,\mathrm{form,pre}}^{-1},
$$

### Candidate C V4 baseline transport candidate D11-C-T1

> **Preregistered, non-normative candidate.** The following C-T1 law is kept
> for D11-C pressure and does not authorize Candidate C implementation or
> conformance. See the [D11-C preregistration][d11-c].

C-T1 proposes using the inherited scalar-mobility potential-flow channel
through an explicit V4-only typed adapter. It does not infer transport
mobility from $H_{1,\mathrm{form},M}$, $G_J$, or $h_4$ by equal dimensions or
matrix coincidence.

At the exact stage selected by the realization, define the derived positive
edge mobility

$$
W_{0,C,e}(C,T_C(h),h,U)
=W_{\mathrm{ref},e}
\exp\!\left(
\kappa_{J,C}\kappa_{M,C}r_{C,e}(T_C(h),h)
\right),
$$

where $W_{\mathrm{ref},e}>0$, $C_{\mathrm{ref}}>0$, and
$\kappa_{J,C}$ are resolved Candidate C parameters. The typed transport map is

$$
\mathcal M_C^{\mathrm{V4}}:
(C,T_C,h,U;\theta_C)\longmapsto
M_{4,C}=\eta_C\operatorname{Diag}(W_{0,C}),
$$

on physical current space. This displayed map is the authority transfer; no
Hodge matrix is silently retyped as mobility. The Candidate C potential and
baseline current are

$$
\Phi_{C,i}
=\kappa_C\sum_{e\sim i}W_{0,C,e}
\bigl(C_i-C_{\operatorname{nbr}(e,i)}\bigr)
-V_C'(C_i;U),
$$

$$
\boxed{
J_{0,C}(C,T_C(h),h,U)
=-M_{4,C}(C,T_C(h),h,U)\,d_0\Phi_C
}.
$$

$r_C$, $\kappa_{J,C}$, and $\kappa_{M,C}$ are dimensionless;
$W_{\mathrm{ref}}$ carries scalar-mobility units; $\eta_C$ converts the
potential differential to physical flux. $V_C'$ and $\kappa_C$ must be
resolved so both terms of $\Phi_C$ have the same units. The scalar potential
gauge is immaterial because only $d_0\Phi_C$ enters the current. The map is
finite, positive, graph-relabel covariant, and sign-even under stored-edge
reorientation on its declared fixed-topology selector stratum.

If C-T1 is accepted, the resulting V4 Candidate C profile would bind
`candidate_c_transport_id = "candidate_c_log_sector_potential_flow_v1"` and
the canonical parameters and site-potential definition in
`params_resolved`. A different evaluator or coefficient has a different
complete profile identity. $W_{0,C}$ and $M_{4,C}$ are derived same-beat
surfaces, never retained state.

The controls are exact:

- $\kappa_{M,C}=0$ returns $W_{0,C}=W_{\mathrm{ref}}$ and removes the
  selected-content baseline conditioning;
- $\chi_C=0$ removes the explicit causal Read-Back but leaves the conditioned
  $J_{0,C}$ active; and
- $\zeta_C=0$ makes the authoritative current equal to $J_{0,C}$ while any
  read remains diagnostic only.

After a topology event, profile migration, or target reconstruction,
$W_{0,C}$ is rebuilt from the target $C$, selector, graph, reference mobility,
geometry, context, and resolved parameters before readmission. It is never
resized or transported as history.

$$
\Delta_{1,M}=B^\top H_{0,M}^{-1}BH_{1,\mathrm{form},M},
\qquad
\widehat R_{C,M}=(I+\tau_C\Delta_{1,M})^{-1}.
$$

The physical-flux to selected-form identification is

$$
\boxed{Q_C=I_{4M}G_J}.
$$

The causal gate is applied exactly once:

$$
r_C^\flat(J,h)
=I_{4M}^{-1}\widehat R_{C,M}I_{4M}G_J(h)J,
$$

$$
j_C^\flat=\chi_Cr_C^\flat,
\qquad
j_{C,\mathrm{flux}}=G_J(h)^{-1}j_C^\flat.
$$

The fixed-geometry current closure is

$$
J_{C,C}=J_{0,C}+\zeta_Cj_{C,\mathrm{flux}}(J_{C,C},h).
$$

With

$$
\widehat R_{C,\mathrm{flux}}
=Q_C^{-1}\widehat R_{C,M}Q_C,
\qquad
L_{C,\mathrm{flux}}
=I-\zeta_C\chi_C\widehat R_{C,\mathrm{flux}},
$$

the solution is $J_{C,C}=L_{C,\mathrm{flux}}^{-1}J_{0,C}$. It is admitted
only where that block is invertible and the declared conditioning certificate
passes. If $\nu_i$ are retained-coordinate eigenvalues, exact regularity
requires

$$
1-\zeta_C\chi_C(1+\tau_C\nu_i)^{-1}\ne0
$$

for every admitted mode. Physical invertibility transfers by similarity
through $Q_C$; retained-space singular-value margins do not transfer
unchanged. The structural source is

$$
S_C(J,h)=\zeta_C\iota_C\!\left(
\mathcal A_\star(j_C^\flat(J,h))
\right).
$$

After continuity, Candidate C rederives all target selector and Hodge
surfaces from $C_{k+1}$. No independent $T_C$ or Hodge writer exists.

## Realization contracts

### Coupled Implicit (`CI`)

CI solves a simultaneous candidate-local root

$$
F_a(J_a,h_a;X_{a,k},U_k)=0.
$$

For A, $\widehat W_A(h)$ must be recomputed inside every residual evaluation.
For C, every trial $h$ must rebuild the selector-to-resolvent chain. A
conforming solver must return the unique admitted regular local root on the
declared bounded branch. C additionally requires exactly one self-consistent
root across the admitted fixed-rank strata. No root, multiple roots, a
singular root, a disconnected root, or a nonfinite root fails closed.

The exact A residual is

$$
F_{J,A}
=J-J_{0,A}(C_k,W_{A,k},h)-\zeta_Aj_{A,\mathrm{flux}}(J,h)=0,
$$

$$
F_{h,A}
=h-H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}+S_A(J,h),h_{4,\mathrm{ref}},U_k
\right)=0.
$$

The exact C residual is

$$
F_{J,C}
=J-J_{0,C}(C_k,T_C(h),h,U_k)
-\zeta_Cj_{C,\mathrm{flux}}(J,h)=0,
$$

$$
F_{h,C}
=h-H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}+S_C(J,h),h_{4,\mathrm{ref}},U_k
\right)=0.
$$

Bounded self-map/contraction uniqueness is local. It is not a global root or
stability theorem.

### Operator Split (`OS`)

OS executes exactly one pass:

```text
X_k -> J^(0) -> j_flat^(0) -> Delta K4^(0)
    -> h^(1) -> J^(1) -> X_(k+1)
```

At fixed $h^{(1)}$, A must recompute its potential, baseline current,
$\widehat W_A$, and $q_A$ before the corrector. C must rebuild its selector,
Hodge package, identification, resolvent, $G_J$, and baseline current. Only
$J^{(1)}$ enters continuity.

The split residual is

$$
r_{h,a}^{OS}
=h_a^{(1)}-H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}+S_a(J_a^{(1)},h_a^{(1)})
\right).
$$

A bounded nonzero residual is part of the profile and is not automatically a
failure or a time-truncation error. A silent second iteration is forbidden and
would define a new realization.

### Reconstructed Geometry (`RG2b`)

RG2b uses a deterministic family-local invariant section $\Gamma_a$, not
persistent geometry state:

$$
\Psi_{a,\Gamma}(X)=\Phi_{a,\mathrm{lag}}(X,\Gamma(X)),
$$

$$
G_{a,\kappa}(X,h)
=H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}+S_a(C_a(h;X,U),h)
\right),
$$

$$
\Gamma_a(\Psi_{a,\Gamma_a}(X))
=G_{a,\kappa}(X,\Gamma_a(X)).
$$

The profile must bind the frozen completion, compact domains
$K_-\Subset K\Subset U$, containment, and a $C^0$ graph-transform contraction
$q_0<1$. The admitted result is a bounded Lipschitz section relative to that
completion. The implementation must not expose a classical RG2b Jacobian or
spectrum without a separately admitted $C^1$ successor.

$C_a(h;X,U)$ is the candidate-$a$ fixed-$h$ physical-current solution. It is
derived solver output, not resource state.

### Persistent Carrier (`PC`)

PC adds authoritative $Z_{4,a}$ and reads old committed history:

$$
K_{4,a,k}=K_{4,\mathrm{base}}+Z_{4,a,k},
\qquad
h_{a,k}=H_{\mathrm{profile}}(K_{4,a,k}).
$$

With $\tau_{\mathrm{PC},a}>0$,

$$
a_{\mathrm{PC},a,k}
=\exp\!\left(-\frac{\Delta t_k}{\tau_{\mathrm{PC},a}}\right),
$$

$$
Z_{4,a,k+1}
=a_{\mathrm{PC},a,k}Z_{4,a,k}
+(1-a_{\mathrm{PC},a,k})S_{a,k}.
$$

$S_{a,k}$ is held constant over the beat. The profile must declare a closed
carrier ball, source envelope, norm, and admitted geometry image. Native
zero-source release is exponential; reset or migration-driven history removal
must not be labeled native release. PC is not Candidate B.

Specifically,

$K_{X,a}$ is the compact admitted base-state chart for candidate $a$.
$\mathcal H_{\mathrm{adm}}$ is the admitted geometry class on which the
canonical $H_{\mathrm{profile}}$ call and selected current solve are lawful.
Both are resolved, identity-bearing profile domains rather than inferred
solver neighborhoods.

$$
\mathcal B_{R,a}=\{Z:\lVert Z\rVert_K\le R_a\},
$$

$$
m_a(R_a)
=\sup_{X\in K_{X,a},\,Z\in\mathcal B_{R,a}}
\lVert S_a(X,Z)\rVert_K\le R_a,
$$

$$
H_{\mathrm{profile}}(K_{4,\mathrm{base}}+\mathcal B_{R,a})
\subseteq\mathcal H_{\mathrm{adm}}.
$$

The current solve must remain regular throughout the declared chart. Under
matched future forcing, any carrier-difference contraction claim must include
the declared writer coefficient and source Lipschitz contribution and require
their preregistered total to be strictly below one.

### Coupled Implicit plus Persistent Carrier (`CI+PC`)

CI+PC reads old $Z_{4,a,k}$ inside a simultaneous root and uses the same root
source for immediate geometry and the prospective history writer:

$$
K_{\mathrm{eff},a}
=K_{4,\mathrm{base}}+Z_{4,a,k}
+\rho_{\mathrm{inst},a}S_a(J_a,h_a).
$$

The current population fixes $\rho_{\mathrm{inst},a}=1$. For constant source,
the steady structural input approaches $K_{4,\mathrm{base}}+2S$. This gain-two
property is identity-bearing and is not amplitude equivalence with CI or PC.

After a valid root, the PC writer uses that same $S_a(J_a^\star,h_a^\star)$.
A second post-continuity source is forbidden. A and C retain their respective
bounded contraction and root-selection requirements.

The geometry residual and history writer are

$$
F_{h,a}
=h_a-H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}+Z_{4,a,k}
+\rho_{\mathrm{inst},a}S_a(J_a,h_a),
h_{4,\mathrm{ref}},U_k
\right)=0,
$$

$$
Z_{4,a,k+1}
=a_{\mathrm{PC},a,k}Z_{4,a,k}
+(1-a_{\mathrm{PC},a,k})S_a(J_a^\star,h_a^\star).
$$

Exact realization ablations are:

| Enabled profile | Controlled change | Accepted reduction |
|---|---|---|
| CI+PC | $\rho_{\mathrm{inst}}=0$ with PC retained | PC |
| CI+PC | $Z_{4,a,k}=0$, PC disabled, $\rho_{\mathrm{inst}}=1$ | CI |
| CI+PC | $\rho_{\mathrm{inst}}=0$, PC disabled, $Z_{4,a,k}=0$ | fixed-reference transition |
| A | $\chi_A=0$ | explicit A read off; direct $W_A$ mobility remains |
| C | $\chi_C=0$ | explicit C read off; intrinsic response may remain diagnostic |
| A or C | $\zeta_a=0$ | read has no causal current or structural consumer |
| PC | $S_{a,k}=0$ | native exponential carrier release |

## Parameters

`GRCV4` must resolve an immutable complete-profile parameter record at
construction. At minimum it must bind:

- graph orientation, boundary, differential, and measure identities;
- charge covector/profile and ordinary external-exchange policy;
- $K_{4,\mathrm{base}}$, reference Hodge package, star cover, overlap
  normalization, $\kappa_H$, geometry domain, and flat/sharp solver;
- candidate ID and every candidate coefficient, gate, floor, selector,
  regularity, adapter, units, and gauge choice;
- realization ID and its root, split, reconstruction, carrier, composition,
  tolerance, domain, and deterministic selection choices;
- lifecycle, migration, topology-event, history-transport/loss, reset,
  receipt, and target-readmission policies; and
- semantic and format versions plus canonical parameter identity.

Candidate A parameters include $\eta$, $\kappa_c$, site potential,
$W_{\mathrm{floor}}$, $\alpha$, $\beta$, $\gamma$, $\kappa_{Ah}$,
$\chi_A$, $\zeta_A$, $\tau_A$, and the admitted $D/G_W$ backend. The
accepted D11-C result must freeze Candidate C's transport parameters. Under
the provisional C-T1 candidate these would include $\Lambda_C$, selector
boundary policy, $C_{\mathrm{ref}}$, $\kappa_{M,C}$, $\kappa_{J,C}$,
$\eta_C$, $\kappa_C$, $W_{\mathrm{ref}}$, the exact $V_C'$ evaluator,
`candidate_c_log_sector_potential_flow_v1`, $\tau_C$, $\chi_C$, $\zeta_C$,
and the current-block conditioning policy. PC and CI+PC additionally bind
$\tau_{\mathrm{PC},a}$, $R_a$, $K_{X,a}$, carrier norm/source envelope, and,
for CI+PC, $\rho_{\mathrm{inst},a}=1$.

Numeric tolerances that change root selection, domain admission, event
classification, or the state trajectory are model parameters. Performance,
telemetry, storage cadence, and device placement remain runtime configuration.

## Complete-step transaction

`step_v4(request)` is the normative input-bearing operation and must be an
atomic transaction in this order. The inherited zero-argument `step()` may
delegate only through the immutable, serialized default request defined by the
[V4 interface extension](grc-common-interface-v4-ext.md#v4-input-bearing-operations).

1. Admit the complete profile, graph, context, current/reset state,
   $Q_{\mathrm{target}}$, time, solver, and domain identities.
2. Rebuild every required pre-read differential, selector, Hodge, baseline,
   carrier-derived, or RG2b surface from authoritative prestate.
3. Execute the exact candidate/realization stage order provisionally.
4. Classify the solver disposition; only `valid_root` may continue.
5. Select one finite, typed, branch/stratum-consistent $J_C$.
6. Execute continuity exactly once into provisional $C_{k+1}$.
7. Validate nonnegativity, finiteness, and the post-write charge target.
8. Rebuild every final-$C$ surface; stale pre-continuity caches are forbidden.
9. Execute the Candidate A writer or Candidate C target rederivation.
10. Execute the PC/CI+PC history writer where enabled, without reading new
    history in the same beat.
11. Validate complete state, geometry, current, carrier, serializer,
    lifecycle, capability, and receipt postconditions.
12. Commit every authoritative coordinate together, or preserve the complete
    prestate unchanged.

For $\Delta t>0$, the regular profile domain applies. For $\Delta t=0$, the
ordinary transition is identity only on an already admitted state with no
impulse and no writer advancement. Negative duration fails closed. An
instantaneous exchange is a typed event, not a zero-duration beat.

Required solver dispositions are:

```text
valid_root
domain_failure
singular
conditioning_failure
nonfinite
no_admitted_root
multiple_admitted_roots
```

No failure disposition authorizes a fallback current, cached root, hidden
regularization, partial write, or post-hoc root selection.

## Lifecycle, migration, and topology events

The scientific lifecycle identity is

$$
\mathfrak X
=(X_{\mathrm{current}},X_{\mathrm{reset}},Q_{\mathrm{target}})
$$

together with graph, orientation, boundary, context-contract, complete
profile, capability, parameter, and ordered-receipt identity.

Snapshot and restoration must preserve enough information to reconstruct and
re-admit that identity. `set_state()` changes current authoritative state only;
it must not silently rebase reset, charge target, graph, profile, or history.
Reset returns to the transformed current reset baseline, not obsolete
pre-event bytes. Duplication must deep-copy all mutable authority.

A profile migration is an ordered map

$$
\mathcal M_{p\to q}:X_p\to X_q
$$

applied to both current and reset state before target reconstruction,
readmission, and atomic commit. Directional loss, history initialization,
archive/drop policy, and target admission must be receipted. Endpoint support
does not prove crossing support.

| Migration | Required state policy |
|---|---|
| Same candidate, nonhistory to nonhistory | Preserve candidate-authoritative state; rebuild and readmit target realization surfaces. |
| Same candidate, nonhistory to PC/CI+PC | Preserve candidate state; initialize current/reset $Z_{4,a}=0$ and receipt that no history was reconstructed. |
| Same candidate, PC/CI+PC to nonhistory | Preserve candidate state; archive/drop current/reset $Z_{4,a}$ and receipt administrative history removal. |
| PC to CI+PC | Preserve $Z_{4,a}$ only under exact carrier, $K_4$, geometry, writer, $\tau_{\mathrm{PC}}$, norm, and domain identity; admit the composite root. |
| CI+PC to PC | Preserve $Z_{4,a}$; remove the immediate path; admit the fixed-$h$ PC target. |
| A to C | Preserve $C$; archive/drop $W_A$ and A-specific $Z_{4,A}$; initialize target $Z_{4,C}=0$ when needed; rebuild C surfaces. |
| C to A | Preserve $C$; construct $W_A$ with $I_A^{\mathrm{GRC}}$; initialize target $Z_{4,A}=0$ when needed; readmit the A target. |

A change to geometry, baseline structure, carrier time constant, composition
gain, norm/domain, writer, RG2b completion, selector, A policy, root selector,
context semantics, or charge-target rule is a migration rather than an
in-place parameter edit.

Candidate A history-free target construction uses the graph-generic
$I_A^{\mathrm{GRC}}$: rebuild target differentials, evaluate the admitted
curvature-disabled $G_W$ at the target reference-current stage, construct
positive current/reset $W_A$, and record that history was not preserved or
fabricated. A specialization may bind a stricter initializer.

A topology event is typed across graph/profile spaces:

$$
C^+=T_{C,\mathrm{evt}}C^-+\Delta C_{\mathrm{event}},
$$

$$
\varpi_+^\top T_{C,\mathrm{evt}}=\varpi_-^\top,
\qquad
\Delta Q_{\mathrm{event}}
=\varpi_+^\top C^+-\varpi_-^\top C^-,
$$

$$
Q_{\mathrm{target}}^+
=Q_{\mathrm{target}}^-+\Delta Q_{\mathrm{event}}.
$$

The same event policy must transform current and reset resource state,
Candidate A edge history, persistent $K_4$ history, graph/context/profile
identity, and receipts. Candidate C surfaces are rederived. Persistent history
may cross only through a typed bounded covariant $L_{K4,\mathrm{evt}}$;
otherwise it is archived/dropped and target $Z_4$ is canonically zeroed with a
loss receipt. Untyped array resizing is not an event.

Every migration or event receipt must bind the ordered source/target graph,
context, and complete-profile identities; current/reset maps; charge-target
policy and actual resource/charge deltas; candidate and carrier history
preserved/initialized/archived/dropped status; target reconstruction and
readmission disposition; information-loss classification; and atomic commit
identity.

Receipt ownership is separated from ordinary event reporting:

```text
StepResult.events
    events emitted by this attempted or committed operation only

lifecycle_receipts
    persistent scientific migration, topology, charge, and information-loss
    receipts owned by GRCV4LifecycleState

telemetry log
    nonauthoritative runtime observations excluded from scientific equality
```

A rejected operation may expose a failure event in its returned result, but it
must not append that event or a commit receipt to persistent lifecycle state.
Reset restores the reset baseline and appends a reset receipt to the existing
lifecycle lineage; it does not resurrect a stale receipt list from the reset
payload. Rebase replaces the reset baseline and appends a rebase receipt.
Save/load preserves persistent receipts, while duplicate deep-copies them.
Telemetry is neither restored as authority nor compared for scientific state
equality. A migration into the GRC9V4 disabled branch transfers receipt
authority to the explicit V4 wrapper while the embedded legacy delegate
retains exactly its native lifecycle representation.

## Analysis interfaces

Structural Hessians, complete-step Jacobians, direct Read-Back derivatives,
spatial operators, projectors, spectra, and sensitivity chains are analysis
objects. They must never write runtime state.

An implementation may expose signatures equivalent to:

```python
def structural_operator(request: StructuralOperatorRequest) -> LinearOperator: ...
def transition_jacobian(request: JacobianRequest) -> LinearOperator: ...
def readback_derivative(request: ReadBackDerivativeRequest) -> LinearOperator: ...
def spatial_operator(request: SpatialOperatorRequest) -> LinearOperator: ...
def local_regularity_certificate(
    request: RegularityRequest,
) -> RegularityCertificate: ...
```

Such an interface must bind the exact formed branch, complete profile,
operator domain, normalization, metric, active selector/regularity stratum,
and differentiation convention. RG2b remains Lipschitz-only. Formula
availability alone does not authorize numeric $\alpha$, $\mu$, $\gamma$,
$\beta$, or $\lambda$, stability, slow-mode, nonnormality, endpoint, or
cross-profile comparison claims.

When a coupled-root tangent uses product coordinates $(\delta J,\delta h)$,
the current-block projection is explicitly

$$
P_J(\delta J,\delta h)=\delta J.
$$

## Observables

In addition to common observables, every instance must expose:

- `complete_profile_id`
- `candidate_id`
- `realization_id`
- `charge_target`
- `charge_current`
- `charge_error`
- `solver_disposition`
- `authoritative_current`
- `geometry_profile_id`
- `lifecycle_receipts`

Candidate/realization observables are exposed only when implemented. Derived
surfaces must be labeled by stage and must not be presented as authoritative
state. Claim-ceiling metadata may be exposed as diagnostics but is not causal
state.

## Serialization

A snapshot must preserve, directly or by stable reconstructible identity:

- model family and format version;
- full complete-profile identity and canonical resolved parameters;
- graph, live order, orientation, boundary, and differential backend identity;
- context, units, gauge, normalization, geometry, solver, and domain identity;
- authoritative current and reset coordinates for the selected profile;
- $Q_{\mathrm{target}}$ and charge profile;
- ordered migration/event/loss receipts; and
- cache provenance sufficient to reject or rebuild derived surfaces.

Restoration must validate the entire payload before exposing target state. It
must not silently rebase charge, create history, promote caches, or substitute
a different profile. Canonical serialization does not imply byte identity
after lawful deterministic reconstruction.

## Errors and atomicity

The implementation must raise or return an explicit typed failure for:

- invalid or unsupported complete profile;
- state/profile authority mismatch;
- invalid graph, orientation, boundary, or differential identity;
- nonpositive A mobility or an invalid carrier/geometry domain;
- selector rank-gap or stratum inconsistency;
- singular, underconditioned, nonfinite, absent, multiple, or disconnected
  roots;
- nonfinite or negative resource state;
- charge mismatch or nonidentity current-profile budget repair;
- stale stage cache entering a load-bearing consumer;
- missing migration/event/history map or malformed receipt;
- failed target reconstruction or readmission; and
- incompatible or unreconstructible snapshot identity.

Every such failure leaves the complete authoritative prestate unchanged.

The machine-readable
[V4 conformance fixture contract](grc-v4-conformance-fixtures.json) is
normative for D10-backed case identifiers, inputs, expected dispositions,
digest checks, and the independent $10\times4$ disabled matrix. Its exact
Candidate C baseline and GRC9V4 expansion rows are preregistered D11 fixtures,
not conformance authority, until the corresponding results are accepted and
propagated. It is a preimplementation fixture contract: passing its schema
audit does not claim that a runtime implementation has executed the cases.

## Claim conformance matrix

Each source link below resolves to the paper and proposal section that carries
the named claim and its ceiling. The short implementation effect does not
replace that source text.

| Claim | Class | Implementation effect | Sources |
|---|---|---|---|
| `D10-CL-N-001` | normative | Common profile-explicit architecture; no flattening or ranking. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-N-002` | normative | $C$ is the only resource; publish exact nonresource authority. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-N-003` | normative | One staged, atomic complete step and one resource write. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-N-004` | normative | Charge and tangent follow the actual resource path. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-N-005` | normative | Whole-lifecycle identity and typed ordered crossings. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-N-006` | normative | Correct one-form/Hodge typing and event transport. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-N-007` | normative | Four independent GRC9V3 reduction surfaces per profile; specialization-owned. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-N-008` | normative | Numeric and semantic choices are complete-profile identity. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-N-009` | normative | Bind exactly one candidate and one realization. | [paper][paper-n] · [proposal][proposal-n] |
| `D10-CL-O-001` | optional | Admit revision-specific Candidate A without core/uniqueness claims. | [paper][paper-o] · [proposal][proposal-o] |
| `D10-CL-O-002` | optional | Admit derived-sector Candidate C without hidden state. | [paper][paper-o] · [proposal][proposal-o] |
| `D10-CL-O-003` | optional | Admit bounded CI roots under exact A/C rules. | [paper][paper-o] · [proposal][proposal-o] |
| `D10-CL-O-004` | optional | Admit one-pass OS and preserve its split residual. | [paper][paper-o] · [proposal][proposal-o] |
| `D10-CL-O-005` | optional | Admit extension-relative Lipschitz RG2b only. | [paper][paper-o] · [proposal][proposal-o] |
| `D10-CL-O-006` | optional | Admit scalar-ZOH, one-$\tau_{\mathrm{PC}}$ persistent carrier. | [paper][paper-o] · [proposal][proposal-o] |
| `D10-CL-O-007` | optional | Admit the exact gain-two CI+PC composition. | [paper][paper-o] · [proposal][proposal-o] |
| `D10-CL-C-001` | conditional | Gate classical Hessian/$\alpha$ claims on a formed $C^2$ branch and complete operator. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-002` | conditional | Default to archive/reset without typed event lineage. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-003` | conditional | Fail closed at singular boundaries pending a named successor. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-004` | conditional | Require complete-chain evidence for endpoint/hysteresis claims. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-005` | conditional | Require formed numeric operators and metrics for stability/spectra. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-006` | conditional | Keep executable SPD/covariance conformance separately verified. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-007` | conditional | No physical/nonabsorbability claim without a baseline model and proof. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-008` | conditional | No preference/ranking without matched formed-branch evidence. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-009` | conditional | No RG2b classical derivative without a regularized successor. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-010` | conditional | Keep dimensions, capacity, gain, and magnitude profile-local. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-011` | conditional | Reopen provenance for materially broader substrate promotion. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-C-012` | conditional | Current ten-profile roster is not future-exhaustive. | [paper][paper-c] · [proposal][proposal-c] |
| `D10-CL-U-001` | open | Reserve nonexecutable Candidate B; do not relabel another path. | [paper][paper-u] · [proposal][proposal-u] |
| `D10-CL-U-002` | open | Runtime formation, retention, release, replay, and endpoint remain evidence work. | [paper][paper-u] · [proposal][proposal-u] |
| `D10-CL-U-003` | open | Physical attribution and nonabsorbability remain open. | [paper][paper-u] · [proposal][proposal-u] |
| `D10-CL-U-004` | open | Numeric structural, temporal, and comparison evidence remains open. | [paper][paper-u] · [proposal][proposal-u] |
| `D10-CL-U-005` | open | Alternative Hodge/DEC profiles require successor identity. | [paper][paper-u] · [proposal][proposal-u] |
| `D10-CL-X-001` | negative | No generic lossless history transport without sufficient lineage. | [paper][paper-x] · [proposal][proposal-x] |
| `D10-CL-X-002` | negative | No unique/preferred candidate, realization, or composition. | [paper][paper-x] · [proposal][proposal-x] |
| `D10-CL-X-003` | negative | Constructibility, regularity, lifecycle validity, and persistence are not stability. | [paper][paper-x] · [proposal][proposal-x] |
| `D10-CL-X-004` | negative | Present Candidate A is not inherited core. | [paper][paper-x] · [proposal][proposal-x] |
| `D10-CL-X-005` | negative | PC is not Candidate B. | [paper][paper-x] · [proposal][proposal-x] |
| `D10-CL-X-006` | negative | Candidate A is not the unique V4 completion. | [paper][paper-x] · [proposal][proposal-x] |

## Explicit nonclaims

Conformance to this document does not establish runtime evidence, a reached
formed branch, endpoint hysteresis, physical channel attribution,
nonabsorbability, dimensionalization, stability, continuation spectra,
nonnormal amplification, cross-profile comparability, preference, unique
Hodge normalization, lossless generic event history, singular continuation,
or future-exhaustive profile coverage.

[paper]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md
[proposal]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md
[d10]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D10DesignSynthesisAndSpecWritingDecision.md
[d10-2]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.md
[d11-open]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D11SuccessorInvestigationOpening.md
[d11-c]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateCBaselineTransportAndMobilityClosure.md
[paper-n]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#151-normative-common-architecture-claims
[proposal-n]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#151-normative-common-architecture-claims
[paper-o]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#152-optional-admitted-profile-claims
[proposal-o]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#152-optional-admitted-profile-claims
[paper-c]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#153-conditional-claims
[proposal-c]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#153-conditional-claims
[paper-u]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#154-open-claims
[proposal-u]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#154-open-claims
[paper-x]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#155-negative-claims-and-blocked-relabels
[proposal-x]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#155-negative-claims-and-blocked-relabels
