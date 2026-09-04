# GRC9V4 Specification

## Status and authority

This file is the normative implementation contract for `GRC9V4`, the
substantive nine-port specialization of [`GRCV4`](grc-v4-spec.md). It combines
the D10-backed specialization with the accepted D11-G9 chiral same-port
expansion and legacy-defined-domain boundary. Runtime conformance remains
unclaimed until an implementation passes the required fixtures.

Primary sources:

- [GRC-v4 paper, Appendix A][paper-a]
- [GRC-v4 proposal, Appendix A and provenance crosswalk][proposal-a]
- [G-RC-9 paper](../papers/2026-04-GRC-9.md)
- [GRC9V3 legacy target specification](grc-9-v3-spec.md)
- [D10.2 substrate provenance and promotion audit][d10-2]
- [D11 bounded successor opening][d11-open]
- [Accepted D11-G9 expansion-port resolution][d11-g9-resolution]
- [D11-G9 append-only provenance supplement][d11-g9-provenance]
- [Common GRC interface: V4 extension](grc-common-interface-v4-ext.md)

The complete [`GRCV4` specification](grc-v4-spec.md) is imported unchanged.
This file adds only nine-port mechanics, the fixed GRC9 differential backend,
GRC9 mechanical event and coarse-graining contracts, and exact profile-scoped
disabled compatibility with `GRC9V3`. It does not redefine the graph-generic
V4 candidate, realization, resource, geometry, or lifecycle laws.

The accepted forensic partition assigns 73 equation contracts to this
specialization: 13 D10 specialization contracts, 40 independent D10
profile/surface compatibility contracts, and 20 append-only D11-G9 contracts.
The specification preserves each result's source-bound support semantics and
does not treat dependency reach as scientific ranking.

The September 2026 stack-audit corrections in this document are V4-owned.
They do not edit or reinterpret the G-RC-9 paper or the `GRC9V3`
specification. The disabled-state wrapper and
`grc9v4_axis_preserving_chiral_same_port_expansion_v1` are GRC9V4
requirements. The older artifacts remain read-only provenance and reduction
targets.

## Conformance language

The words **must**, **must not**, **required**, **shall**, and **shall not** are
normative. **May** identifies an admitted option. **Should** is implementation
guidance.

An implementation conforms to `GRC9V4` only if it:

1. conforms to `GRCV4` for a named nonempty subset of the ten current complete
   profiles;
2. implements every GRC9 specialization rule in this file; and
3. implements all four disabled-reduction surfaces for every V4 profile it
   claims to support.

Transition compatibility alone is not full compatibility.
Until D11-G9 accepts and the paper propagates a canonical expansion map, no
implementation may claim full `GRC9V4` conformance. This hold does not suspend
the authority of unaffected D10-backed specialization clauses.

## Class

```python
class GRC9V4(GRCV4):
    ...
```

`GRC9V4` must also satisfy the [common GRC interface](grc-common-interface.md)
as strengthened by the
[V4 common-interface extension](grc-common-interface-v4-ext.md). It must not
alter `GRC9V3` behavior to obtain compatibility; the legacy spec is the
reduction target.

## Capabilities

Every `GRC9V4` instance must advertise all capabilities required by its
selected `GRCV4` profile plus:

- `port_graph`
- `mechanical_refinement`
- `column_coarse_graining`
- `basin_attributes`
- `hierarchy_tracking`
- `quadrature_budget`
- `intrinsic_frame`
- `grc9v3_disabled_compatibility`

It must not advertise `host_embedding_frame`. The opt-in
`grc9v3_column_h_assisted` spark lane must have a separate capability or
profile flag and must not silently replace the baseline lane.

## Specialization identity

In addition to the complete `GRCV4` identity, the specialization identity must
bind:

```python
@dataclass(frozen=True)
class GRC9CoarsePolicy:
    nonnegative_field_mode: Literal["simplex_profile"]
    signed_flux_mode: Literal["positive_negative_split"]

@dataclass(frozen=True)
class GRC9V4ExpansionPolicy:
    schema_version: Literal["grc9v4-expansion-policy-v1"]
    policy_id: Literal[
        "grc9v4_axis_preserving_chiral_same_port_expansion_v1"
    ]
    boundary_policy: Literal["reserve_exact_old_port_map_first"]
    primary_spine_policy: Literal["chiral_latin_same_port_transversal"]
    recursive_tree_policy: Literal["creation_order_bfs_same_port_rotor"]
    stable_id_policy: Literal["grc_event_sha256_role_grammar_v1"]
    bond_seed: float
    resource_distribution: tuple[float, float, float]

@dataclass(frozen=True)
class GRC9V4ExpansionEventIdentity:
    event_id: str
    target_effective_degree: int
    module_chirality: Literal[-1, 1]
    growth_phase: Literal[1, 2, 3] | None

@dataclass(frozen=True)
class GRC9V4ResolvedSpecialization:
    schema_version: Literal["grc9v4-resolved-specialization-v1"]
    port_chart: Mapping[str, JSONValue]
    spark: Mapping[str, JSONValue]
    expansion: GRC9V4ExpansionPolicy
    coarse_graining: GRC9CoarsePolicy
    compatibility: Mapping[str, JSONValue]

@dataclass(frozen=True)
class GRC9V4Specialization:
    port_count: Literal[9]
    port_chart_id: Literal["fixed_3x3_row_column"]
    frame_mode: Literal["fixed_port_chart"]
    hessian_backend: Literal["row_basis_diagonal"]
    hessian_sign: Literal[-1, 1]
    spark_lane: Literal[
        "current_hybrid_signed_hessian",
        "grc9v3_column_h_assisted",
    ]
    expansion_policy_id: Literal[
        "grc9v4_axis_preserving_chiral_same_port_expansion_v1"
    ]
    expansion_distribution_mode: Literal["equal", "custom"]
    coarse_policy: GRC9CoarsePolicy
    grc9v3_target_spec_version: str
    compatibility_branch: Literal["enabled_v4", "disabled_grc9v3"]
    params_resolved: GRC9V4ResolvedSpecialization
    params_hash: str
```

Any change to the port count, chart, default row backend, Hessian sign,
spark lane, expansion policy, resource split, coarse representation, or legacy
target version is identity-bearing.

## Specialization contract register

The 13 nonprofile parent contracts are:

| Contract | Required specialization content | Boundary |
|---|---|---|
| `D10.2-EC-PARENT-BASE-GRC9-ROW-BASIS-DIFFERENTIAL` | Fixed three-row gradient, Hessian, and flux summaries. | Not the generic V4 backend. |
| `D10.2-EC-PARENT-GRC9-ORDERED-PORTS` | Nine ordered ports per node. | Not generic GRCV4. |
| `D10.2-EC-PARENT-GRC9-ROW-COLUMN-CHART` | Fixed $3\times3$ chart. | Not a host-space frame. |
| `D10.2-EC-PARENT-GRC9-SATURATION` | Exact nine-active-port gate. | Not generic graph-degree pressure. |
| `D10.2-EC-PARENT-GRC9-MECHANICAL-EXPANSION` | Column-preserving module replacement. | Not generic topology change. |
| `D10.2-EC-PARENT-GRC9-HYBRID-SPARK` | Saturation plus semantic degeneracy candidate. | Both parts remain load-bearing. |
| `D10.2-EC-PARENT-GRC9-CHILD-BASIN-STABILIZATION` | Post-expansion child basin/attractor gain. | Candidate or expansion alone is not completion. |
| `D10.2-EC-PARENT-GRC9-COLUMN-COARSE-GRAINING` | Actual $\mathcal G$/Split operator. | Cache refresh is not the operator. |
| `D10.2-EC-PARENT-L-A-INITIALIZER-GRC9V3` | Exact GRC9V3 Candidate-A initializer binding. | Not graph-generic migration law. |
| `D10.2-EC-PARENT-BASE-DISABLED-TRANSITION` | Exact disabled transition target. | Does not imply other surfaces. |
| `D10.2-EC-PARENT-BASE-DISABLED-STATE` | Exact disabled authoritative-state projection. | Not implied by transition equality. |
| `D10.2-EC-PARENT-BASE-DISABLED-OBSERVABLE` | Exact equality on the GRC9V3 observable set. | V4-only diagnostics are projected out. |
| `D10.2-EC-PARENT-BASE-DISABLED-LIFECYCLE` | Exact branch-scoped GRC9V3 lifecycle. | Enabled V4 events remain V4 events. |

## Port graph

The graph is

$$
\Gamma=(V,E,\sigma),
$$

where every undirected edge occupies one ordered port at each endpoint:

$$
\sigma(e)=((i,r),(j,s)),
\qquad r,s\in\{1,\ldots,9\}.
$$

The active degree obeys

$$
\deg_{\mathrm{act}}(i)\le9.
$$

Each live `(node_id, port)` endpoint occurs in at most one live edge. This
port-capacity invariant is stronger than uniqueness of the two-ended endpoint
pair and applies even when parallel graph edges have distinct edge IDs. For
the selected edge orientation,
$w_{ij}=w_{ji}$ and $J_{ji}=-J_{ij}$. Multiple edges require stable edge
identity and explicit aggregation; a single port lookup must not hide them.

Port labels are mechanical interface data and lifecycle identity. They do not
add a resource coordinate or make port caches authoritative state.

```python
@dataclass(frozen=True)
class GRC9V4PortEndpoint:
    node_id: NodeId
    port: int  # 1..9

@dataclass(frozen=True)
class GRC9V4PortEdge:
    edge_id: EdgeId
    source: GRC9V4PortEndpoint
    target: GRC9V4PortEndpoint
    orientation: Literal[-1, 1]

@dataclass(frozen=True)
class EnabledGRC9V4State(GRCV4State):
    port_edges: dict[EdgeId, GRC9V4PortEdge]
    hierarchy: Mapping[str | int, list[str | int]]
    basin_identity: Mapping[NodeId, str | int]

@dataclass(frozen=True)
class DisabledGRC9V3State:
    delegate: ExactGRC9V3State
    target_spec_version: str
    entry_receipt: LifecycleReceipt

GRC9V4ScientificState = EnabledGRC9V4State | DisabledGRC9V3State
```

The inherited `GRCV4State` authority rules remain controlling. Basin,
hierarchy, event, and graph identity are lifecycle surfaces. Row summaries and
coarse caches are derived, representation-only, and excluded from scientific
state equality. The disabled branch delegates its scientific state and
transition to the exact legacy target; the V4 wrapper owns only the branch
tag, ordered crossing receipt, and target-version binding.

## Fixed $3\times3$ chart

Map port $r$ to mode row $a$ and polarity column $b$ by

$$
a,b\in\{1,2,3\},
\qquad
r=b+3(a-1).
$$

The partitions are

$$
\mathcal R_1=\{1,2,3\},\quad
\mathcal R_2=\{4,5,6\},\quad
\mathcal R_3=\{7,8,9\},
$$

$$
\mathcal C_1=\{1,4,7\},\quad
\mathcal C_2=\{2,5,8\},\quad
\mathcal C_3=\{3,6,9\}.
$$

Rows own the fixed directional differential classes. Columns own stable
interface families for reassignment, refinement, and coarse-graining. The
chart is neither a dynamical field nor a continuum primitive.

## Fixed row-basis differential backend

Let $\mathcal T_i^{(a)}$ be occupied edges at node $i$ in row $a$ and

$$
Z_i^{(a)}=\sum_{j:(i,j)\in\mathcal T_i^{(a)}}w_{ij}.
$$

A zero denominator produces the exact zero row contribution. Otherwise,

$$
\mathbf g_i
=\sum_{a=1}^3
\left(
\frac{1}{Z_i^{(a)}}
\sum_{j:(i,j)\in\mathcal T_i^{(a)}}w_{ij}(C_j-C_i)
\right)\mathbf e_a,
$$

$$
H_i
=\sum_{a=1}^3
\left(
\frac{1}{Z_i^{(a)}}
\sum_{j:(i,j)\in\mathcal T_i^{(a)}}w_{ij}(C_j-C_i)
\right)\mathbf e_a\otimes\mathbf e_a,
$$

$$
\widetilde H_i=s_HH_i,
\qquad s_H\in\{+1,-1\},
$$

with $s_H$ chosen so stable basin interiors are positive-definite under the
declared convention.

The row net-flux summary is

$$
\mathbf J_i^{\mathrm{net}}
=\sum_{a=1}^3
\left(\sum_{e\in\mathcal T_i^{(a)}}J_{i,e}\right)\mathbf e_a.
$$

The historical GRC9V3 node tensor remains diagonal:

$$
K_i[a,a]
=\lambda_cC_i
+\xi_c\sum_{j\in\mathrm{row}\ a}w_{ij}(C_j-C_i)^2
+\zeta_c\left(\sum_jJ_{ij}\right)^2.
$$

The $\xi_c$ term is row-local, not an outer product of $\mathbf g_i$. The
$\zeta_c$ term is an isotropic scalar added to each diagonal entry, not
$\mathbf J_i^{\mathrm{net}}(\mathbf J_i^{\mathrm{net}})^\top$. This legacy
node tensor must never be labeled graph $K_4$.

The baseline fixes:

```text
frame_mode = fixed_port_chart
hessian_backend = row_basis_diagonal
```

A weighted-least-squares comparison backend may exist only under a distinct,
serialized comparison identity; it cannot silently become the default.

## Saturation and hybrid spark semantics

Mechanical saturation is exact:

$$
\deg_{\mathrm{act}}(s)=9.
$$

The baseline basin seed satisfies

$$
\lVert\mathbf g_i\rVert<\varepsilon_\nabla,
\qquad
\lambda_{\min}(\widetilde H_i)>\varepsilon_H>0.
$$

The baseline `current_hybrid_signed_hessian` candidate condition is

$$
\deg_{\mathrm{act}}(s)=9
\quad\wedge\quad
\lVert\mathbf g_s\rVert<\varepsilon_\nabla
\quad\wedge\quad
\lambda_{\min}(\widetilde H_s)<\varepsilon_{\mathrm{spark}}.
$$

The per-column diagnostic

$$
H_s^{(b)}
=\sum_{a=1}^3w_{s,a,b}
\bigl(C_{n(s,a,b)}-C_s\bigr)
$$

enters gating only under the named opt-in
`grc9v3_column_h_assisted` lane. A proxy or cache must not be reported as
direct column-$H$ evidence.

The implementation must distinguish:

1. hybrid spark candidate;
2. mechanical expansion; and
3. completed spark after post-expansion stable child-basin or attractor gain.

No earlier stage may emit a completed-spark event.

## Mechanical expansion

For desired external capacity $D_{\mathrm{eff}}(s)$, the maximum external
capacity of a tree-connected $n$-node nine-port module is

$$
D_{\mathrm{ext,max}}(n)=9n-2(n-1)=7n+2.
$$

The capacity lower bound and canonical module size are

$$
n_{\mathrm{cap}}
=\left\lceil\frac{D_{\mathrm{eff}}(s)-2}{7}\right\rceil,
$$

$$
\boxed{
n_{\mathrm{canonical}}
=\max\!\left(4,n_{\mathrm{cap}}\right)
}.
$$

The four-node floor is mandatory: one core and three primary satellites. This
corrected equation, not $\lceil D_{\mathrm{eff}}/7\rceil$, governs GRC9V4.

### Accepted D11-G9 chiral same-port expansion

The normative enabled policy is
`grc9v4_axis_preserving_chiral_same_port_expansion_v1`, selected by
`D11-G9-P4a`. It applies only to an exactly saturated source $s$ with each
source port $1,\ldots,9$ occupied once. The inherited all-center spine is not
admissible at saturation: both the old boundary edge at source port 5 and its
second internal edge claim $(s_2,5)$. Parallel-edge support or operation order
does not repair duplicate endpoint-port occupancy.

#### Boundary reservation and primary spine

All nine inherited boundary endpoints must be reserved before any internal
endpoint is allocated. For an old edge with source endpoint $(s,r)$ and
external endpoint $(j,t)$, let $b(r)$ be the column of port $r$. The exact map
is

$$
\boxed{
((s,r),(j,t))
\longmapsto
((s_{b(r)},r),(j,t)).
}
$$

It preserves the old edge identity, external endpoint, local port, row,
column, and declared coordinate orientation.

Define

$$
x\oplus_3k=1+((x-1+k)\bmod3).
$$

Every event binds explicit `module_chirality`
$\epsilon\in\{-1,+1\}$ and

$$
\beta_\epsilon(b)=b\oplus_3\epsilon,
\qquad
r_b^\epsilon=\beta_\epsilon(b)+3(b-1).
$$

The three primary internal edges are

$$
\boxed{
(c,r_b^\epsilon)\leftrightarrow(s_b,r_b^\epsilon),
\qquad b=1,2,3.
}
$$

Thus the two admitted mirror spines are

$$
\epsilon=+1:
\quad
(c,2)\leftrightarrow(s_1,2),\quad
(c,6)\leftrightarrow(s_2,6),\quad
(c,7)\leftrightarrow(s_3,7),
$$

$$
\epsilon=-1:
\quad
(c,3)\leftrightarrow(s_1,3),\quad
(c,4)\leftrightarrow(s_2,4),\quad
(c,8)\leftrightarrow(s_3,8).
$$

Every internal edge uses the same local port at both endpoints. Each row and
column occurs exactly once in the primary spine, and every satellite internal
port is outside that satellite's inherited boundary column.

#### Conditional phase and arbitrary-size tree

Let

$$
m=n_{\mathrm{canonical}}-4=3q+\rho,
\qquad \rho\in\{0,1,2\}.
$$

When $\rho=0$, `growth_phase` is exactly `None`. When $\rho>0$, the event
binds $\phi\in\{1,2,3\}$ as the first remainder branch; a second remainder
follows in chirality order. Admission fails before mutation with:

```text
missing module_chirality
  -> module_chirality_required

rho > 0 and growth_phase is absent
  -> module_growth_phase_required

rho = 0 and growth_phase is not None
  -> reject_noncanonical_inactive_growth_phase
```

Every internal edge in branch $b$ uses row $b$. At a branch node whose
incoming edge uses column $c$, its ordered outward rotor is

$$
\mathcal O_\epsilon(c)
=\left(c\oplus_3\epsilon,c\oplus_3(-\epsilon)\right).
$$

The parent is the first creation-order node in the branch with an unused
rotor port. The child uses that same port at its own endpoint. This
creation-order breadth-first rule starts each primary branch with one free
recursive valence and changes available valence by $+1$ per child, so it does
not stall for any finite admitted module size. The result is connected and
acyclic with $n-1$ internal edges and exact capacity $7n+2$.

Internal row counts and internal column counts may differ by at most one.
Simultaneous cyclic row, column, and branch rotation rotates an active phase
and preserves chirality; reflection flips chirality and reflects the active
phase. A port number, node-ID parity, iteration order, thread schedule, global
counter, or hidden RNG must not select chirality or phase.

#### Stable identity and initialization

`event_id` must match `grc-event-sha256:<64-lowercase-hex-digits>`. Its digest
payload binds the source graph and source node, $D_{\mathrm{eff}}$, module
size, chirality, canonical phase, port policies, $w_{\mathrm{bond}}$, resource
map, and candidate/history policies. Base role IDs are

```text
<event-id>/core
<event-id>/satellite/1
<event-id>/satellite/2
<event-id>/satellite/3
<event-id>/internal/1
<event-id>/internal/2
<event-id>/internal/3
```

For $w=\max(1,\operatorname{len}(\operatorname{decimal}(m)))$, extra roles
are

```text
<event-id>/extra/<b>/<local-ordinal-zero-padded-to-w>
<event-id>/internal/extra/<b>/<local-ordinal-zero-padded-to-w>
```

Old edge IDs are preserved. A missing, duplicate, or colliding role ID rejects
before commit. Every new internal reference edge receives the same resolved
$w_{\mathrm{bond}}>0$ and zero incoming/reference current. This bond is a
chart-neutral reference seed, not Candidate A history, Candidate C state,
persistent $Z_4$, or a completed current solve.

For the unit-measure profile, current and reset resource state use the same
map

$$
C_c^+=0,
\qquad
C_{s_b}^+=p_bC_s^-,
\qquad
C_{x_{b,\ell}}^+=0,
$$

where $p_b\geq0$, $\sum_bp_b=1$, and the canonical baseline is
$p_1=p_2=p_3=1/3$. The exact tuple is identity-bearing; a bare `custom` label
is invalid. This unit-measure map has $\Delta Q_{\mathrm{event}}=0$.

#### Whole-lifecycle completion and legacy boundary

Candidate A must select before target construction one of: exact old-edge
lineage plus an admitted positive initializer, another admitted full-target
edge-history policy, or explicit full-target history loss. Candidate C's
target profile must supply the entire exact $W_{C,\mathrm{tr}}$ map before
selector, Hodge, $\Phi_{0,C}$, $J_{0,C}$, response, geometry, and analysis
surfaces are rederived. Persistent $K_4$ history uses one typed whole-carrier
$L_{K4,\mathrm{evt}}$, or the whole source carrier is archived and the whole
target carrier reset to zero with a loss receipt. Partial $K_4$ preservation
with zero-filled new components is forbidden.

Current state, reset state, resource, history, profile, event receipt, target
surface reconstruction, and target readmission commit atomically or not at
all. The complete plan is a pure function of admitted source lifecycle state,
event identity, and the resolved expansion policy and must match the canonical
fixtures.

GRC9 and GRC9V3 remain unchanged. Exact disabled compatibility applies only
on

$$
\mathcal D_{\mathrm{V3,defined}}
=\{\text{source states for which unchanged legacy authority determines one unique target}\}.
$$

The saturated port-5 conflict is outside this domain and returns
`legacy_expansion_target_undefined` with no graph, resource, state, history,
reset, or receipt mutation. The enabled chiral V4 rule must not be executed
and relabeled exact V3 behavior.

The governing claim is `D11-G9-CL-N-001`. Its twenty append-only contracts
map into this specification as follows:

| Contract | Required implementation surface |
|---|---|
| `D11-G9-EC-SATURATED-SOURCE-PORT-BIJECTION` | Exactly one old edge at each source port $1,\ldots,9$. |
| `D11-G9-EC-N-CAPACITY-FLOOR` | Capacity-derived node count with the four-node floor. |
| `D11-G9-EC-BOUNDARY-RESERVE-FIRST` | Reserve all inherited target endpoints before internal allocation. |
| `D11-G9-EC-EXACT-OLD-PORT-MAP` | Preserve old edge IDs, external endpoints, ports, rows, columns, and orientation. |
| `D11-G9-EC-MODULE-CHIRALITY` | Explicit event-bound mirror choice. |
| `D11-G9-EC-PRIMARY-LATIN-TRANSVERSAL` | Three-edge chiral same-port primary spine. |
| `D11-G9-EC-GROWTH-PHASE` | Conditional canonical remainder phase and exact failure dispositions. |
| `D11-G9-EC-BRANCH-ROW-IDENTITY` | Fixed row identity for every branch edge. |
| `D11-G9-EC-LOCAL-COLUMN-ROTOR` | Chirality-ordered outward column rotor. |
| `D11-G9-EC-BRANCH-BFS-PARENT` | Deterministic creation-order breadth-first parent selection. |
| `D11-G9-EC-SAME-PORT-INTERNAL-EDGE` | Identical local port at both internal endpoints. |
| `D11-G9-EC-RECURSIVE-NONSTALL` | Finite-size nonstall invariant. |
| `D11-G9-EC-ROW-COLUMN-BALANCE` | Row and column internal-count imbalance at most one. |
| `D11-G9-EC-TREE-AND-CAPACITY` | Connected acyclic module and exact $7n+2$ capacity. |
| `D11-G9-EC-FIXED-BOND-SEED` | One positive chart-neutral new-edge reference seed. |
| `D11-G9-EC-RESOURCE-DISTRIBUTION` | One current/reset resource map and charge receipt. |
| `D11-G9-EC-PORT-PLAN-DETERMINISM` | Digest-bound, replayable plan and stable role IDs. |
| `D11-G9-EC-DIHEDRAL-COVARIANCE` | Rotation/reflection covariance of chirality and phase. |
| `D11-G9-EC-LIFECYCLE-READMISSION` | Whole-lifecycle reconstruction, validation, and atomic target admission. |
| `D11-G9-EC-LEGACY-DEFINED-DOMAIN` | Mutation-free failure where unchanged legacy authority has no unique target. |

## Child-basin completion

After expansion, ordinary reflexive dynamics runs on the target module. A
completed spark is registered only after the declared stability criterion
finds at least one additional stable child basin or attractor relative to the
parent organization.

```text
nine-port saturation
  + basin-interior signed-Hessian degeneracy
  -> hybrid spark candidate
  -> typed mechanical expansion
  -> post-event reflexive evolution
  -> stable child basin or attractor gain
  -> completed spark and hierarchy update
```

Expansion without stabilization remains mechanical refinement. A transient
child-like feature is not completion.

## Column coarse-graining and Split

Coarse encoding is field-typed rather than selected by one global mode:

```python
@dataclass(frozen=True)
class GRC9CoarsePolicy:
    nonnegative_field_mode: Literal["simplex_profile"]
    signed_flux_mode: Literal["positive_negative_split"]
```

Every enabled specialization uses both fields. A capability request names the
field family, and dispatch to the other encoding is a typed error.

For a nonnegative port-attached field $X_{i,a,b}$,

$$
\bar X_{i,b}=\sum_{a=1}^3X_{i,a,b},
$$

$$
\pi^X_{i,a\mid b}
=
\begin{cases}
X_{i,a,b}/\bar X_{i,b},&\bar X_{i,b}>0,\\
1/3,&\bar X_{i,b}=0,
\end{cases}
$$

$$
\mathcal G(X)=(\bar X,\pi^X),
\qquad
\operatorname{Split}(\bar X,\pi^X)_{i,a,b}
=\pi^X_{i,a\mid b}\bar X_{i,b}.
$$

On the admitted simplex domain and with the same canonical uniform zero-total
profile,

$$
\operatorname{Split}\circ\mathcal G=\operatorname{Id},
\qquad
\mathcal G\circ\operatorname{Split}=\operatorname{Id}.
$$

Signed flux must use the exact split mode
$J=J^+-J^-$ with $J^+=\max(J,0)$ and $J^-=\max(-J,0)$, applying
$\mathcal G$/Split independently to both parts. A signed total plus an
absolute profile is lossy and may be exposed only as a diagnostic.

Cache invalidation is required after relevant value or topology change, but
cache hygiene alone does not implement `column_coarse_graining`. This operator
is GRC9 chart-specific and must not be advertised as generic graph coarsening.

## Exact Candidate-A initializer binding

When GRC9V4 needs history-free Candidate-A target initialization, it binds the
generic $I_A^{\mathrm{GRC}}$ role to the exact GRC9V3 base-conductance
reconstruction:

$$
I_A^{\mathrm{GRC9V3}}(C,U,G)_e
=\max\!\left(
10^{-12},
\exp\!\left[
-\alpha\frac{C_u+C_v}{2}
-\frac{\beta}{2}\lVert\mathbf g_u(C)-\mathbf g_v(C)\rVert^2
-\frac{\gamma}{2}J_{e,\mathrm{in}}^2
\right]
\right).
$$

The target stage must use the fixed-row gradient, declared incoming/reference
current, and the binding

```text
frame_mode = fixed_port_chart
hessian_backend = row_basis_diagonal
curvature_backend = none
```

The Hessian backend remains load-bearing for basin and spark readmission but
does not enter the exponent. The initializer is history-free and must emit a
direction-specific history-loss receipt. It must not claim native formation or
history preservation.

## Exact disabled GRC9V3 compatibility

Exact compatibility is defined only on
$\mathcal D_{\mathrm{V3,defined}}$, the source states for which unchanged
legacy authority determines one unique target. Outside that domain, including
the saturated port-5 expansion conflict, the wrapper returns
`legacy_expansion_target_undefined` without mutation. It must not substitute
the enabled V4 expansion.

Every supported profile has four independent disabled surfaces:

- **transition** — execute the exact declared `GRC9V3` transition;
- **state** — project authoritative state to the exact `GRC9V3` state surface;
- **observable** — require equality only on the `GRC9V3` observable set; and
- **lifecycle** — use `GRC9V3` snapshot, reset, event, and step semantics only
  after explicit migration to the disabled branch.

The complete 40-contract matrix is:

| Profile | Transition | State | Observable | Lifecycle |
|---|---|---|---|---|
| `A_CI` | `D10.2-EC-DISABLED-A_CI-TRANSITION` | `D10.2-EC-DISABLED-A_CI-STATE` | `D10.2-EC-DISABLED-A_CI-OBSERVABLE` | `D10.2-EC-DISABLED-A_CI-LIFECYCLE` |
| `C_CI` | `D10.2-EC-DISABLED-C_CI-TRANSITION` | `D10.2-EC-DISABLED-C_CI-STATE` | `D10.2-EC-DISABLED-C_CI-OBSERVABLE` | `D10.2-EC-DISABLED-C_CI-LIFECYCLE` |
| `A_OS` | `D10.2-EC-DISABLED-A_OS-TRANSITION` | `D10.2-EC-DISABLED-A_OS-STATE` | `D10.2-EC-DISABLED-A_OS-OBSERVABLE` | `D10.2-EC-DISABLED-A_OS-LIFECYCLE` |
| `C_OS` | `D10.2-EC-DISABLED-C_OS-TRANSITION` | `D10.2-EC-DISABLED-C_OS-STATE` | `D10.2-EC-DISABLED-C_OS-OBSERVABLE` | `D10.2-EC-DISABLED-C_OS-LIFECYCLE` |
| `A_RG2b` | `D10.2-EC-DISABLED-A_RG2b-TRANSITION` | `D10.2-EC-DISABLED-A_RG2b-STATE` | `D10.2-EC-DISABLED-A_RG2b-OBSERVABLE` | `D10.2-EC-DISABLED-A_RG2b-LIFECYCLE` |
| `C_RG2b` | `D10.2-EC-DISABLED-C_RG2b-TRANSITION` | `D10.2-EC-DISABLED-C_RG2b-STATE` | `D10.2-EC-DISABLED-C_RG2b-OBSERVABLE` | `D10.2-EC-DISABLED-C_RG2b-LIFECYCLE` |
| `A_PC` | `D10.2-EC-DISABLED-A_PC-TRANSITION` | `D10.2-EC-DISABLED-A_PC-STATE` | `D10.2-EC-DISABLED-A_PC-OBSERVABLE` | `D10.2-EC-DISABLED-A_PC-LIFECYCLE` |
| `C_PC` | `D10.2-EC-DISABLED-C_PC-TRANSITION` | `D10.2-EC-DISABLED-C_PC-STATE` | `D10.2-EC-DISABLED-C_PC-OBSERVABLE` | `D10.2-EC-DISABLED-C_PC-LIFECYCLE` |
| `A_CI_PC` | `D10.2-EC-DISABLED-A_CI_PC-TRANSITION` | `D10.2-EC-DISABLED-A_CI_PC-STATE` | `D10.2-EC-DISABLED-A_CI_PC-OBSERVABLE` | `D10.2-EC-DISABLED-A_CI_PC-LIFECYCLE` |
| `C_CI_PC` | `D10.2-EC-DISABLED-C_CI_PC-TRANSITION` | `D10.2-EC-DISABLED-C_CI_PC-STATE` | `D10.2-EC-DISABLED-C_CI_PC-OBSERVABLE` | `D10.2-EC-DISABLED-C_CI_PC-LIFECYCLE` |

No row or column is implied by another.

The executable representation is discriminated by `compatibility_branch`:

```python
GRC9V4ScientificState = EnabledGRC9V4State | DisabledGRC9V3State
```

`enabled_v4 -> disabled_grc9v3` performs an explicit V4 migration: map current
and reset resource state, reconstruct the target base conductance at the exact
legacy stage, archive/drop V4-only $W_A$ and $Z_4$ authority with receipts,
project V4-only observables, instantiate the exact target snapshot family, and
pass target readmission before commit. `disabled_grc9v3 -> enabled_v4`
performs the inverse-direction V4 migration: preserve admitted resource and
graph coordinates, initialize candidate/realization state using the selected
V4 target rules, bind a new V4 reset baseline, and receipt every noninvertible
history choice. Neither direction mutates or extends `GRC9V3`.

### Transition projection

| Profile class | Required disabled transition |
|---|---|
| A-CI | Disable temporal $W_A$ and CI, reconstruct exact GRC9V3 base conductance, then execute the exact GRC9V3 step. |
| C-CI | Disable C-sector Read-Back and CI, project C-sector surfaces to diagnostic-only, then execute the exact GRC9V3 step. |
| A-OS | Disable temporal $W_A$ and the OS geometry channel, then execute the exact GRC9V3 step. |
| C-OS | Disable C-sector Read-Back and the OS geometry channel, then execute the exact GRC9V3 step. |
| A-RG2b | Disable temporal $W_A$ and RG2b, then execute the exact GRC9V3 step. |
| C-RG2b | Disable C-sector Read-Back and RG2b, then execute the exact GRC9V3 step. |
| A-PC | Disable temporal $W_A$ and PC, set $Z_{4,A}=0$, then execute the exact GRC9V3 step. |
| C-PC | Disable C-sector Read-Back and PC, set $Z_{4,C}=0$, then execute the exact GRC9V3 step. |
| A-CI+PC | Disable temporal $W_A$, CI, and PC, set $Z_{4,A}=0$, then execute the exact GRC9V3 step. |
| C-CI+PC | Disable C-sector Read-Back, CI, and PC, set $Z_{4,C}=0$, then execute the exact GRC9V3 step. |

### State projection

For A profiles, disabled state removes temporal-$W_A$ authority and
reconstructs the exact GRC9V3 base conductance at its native stage. For C
profiles, $T_C$, $P_M$, the selected Hodge package, resolvent, and related V4
causal surfaces are projected out or diagnostic-only. Persistent profiles set
$Z_{4,a}$ to canonical zero or archive it through an explicit loss receipt.

### Observable projection

Equality is required on the observable set declared by
[`grc-9-v3-spec.md`](grc-9-v3-spec.md), not on the full snapshot bytes. V4-only
profile metadata, solver receipts, split residuals, carrier diagnostics,
selector diagnostics, and typed event receipts are projected out.

### Lifecycle projection

Enabled V4 lifecycle semantics remain controlling until a typed, receipted,
atomic migration into the disabled branch passes target readmission. Only then
may GRC9V3 snapshot, reset, event, and transition semantics govern. An enabled
V4 topology event must not be relabeled as a GRC9V3 event. A disabled legacy
event outside $\mathcal D_{\mathrm{V3,defined}}$ returns
`legacy_expansion_target_undefined` and leaves the entire scientific prestate
and receipt ledger unchanged.

## Step and event ordering

An enabled V4 ordinary beat follows the exact transaction in
[`grc-v4-spec.md`](grc-v4-spec.md#complete-step-transaction), with the fixed
port graph and row backend supplying its specialization context.

Spark processing is lifecycle/event work. Candidate detection occurs from the
fresh final-$C$, fixed-row differential, and basin surfaces after a successful
ordinary beat has committed and before the next ordinary beat. An expansion
then executes as a separate typed topology transaction between admitted
lifecycle states. The post-event state resumes ordinary V4 stepping;
completion is registered only after child-basin stabilization under the
resolved policy. Predictor, stale-cache, or partially committed values cannot
trigger expansion.

The disabled branch executes the legacy `GRC9V3` step as a target transition.
It must not approximate that transition by running enabled V4 equations with
small coefficients.

## Parameters

`GRC9V4` parameters include the complete `GRCV4` profile plus:

- fixed port and chart identity;
- row-basis differential and Hessian sign configuration;
- basin and spark thresholds;
- explicit spark lane;
- `grc9v4_axis_preserving_chiral_same_port_expansion_v1`, the exact boundary,
  primary-spine, branch-row, rotor, breadth-first parent, same-port, stable-ID,
  orientation, and fixed-bond policies;
- event-bound desired capacity, explicit module chirality, conditional
  canonical growth phase, and digest payload;
- equal or custom resource-distribution policy with exact `(p_1,p_2,p_3)`;
- Candidate A full-target history policy, Candidate C target
  $W_{C,\mathrm{tr}}$ authority, and persistent whole-carrier disposition;
- hierarchy and child-stabilization policy;
- nonnegative and signed column coarse-graining modes;
- exact GRC9V3 target version and projection rules; and
- numeric tolerances used for target readmission and compatibility checks.

Defaults must resolve at construction. No environment variable, cache state,
or solver history may alter these semantics after profile resolution.
`GRC9V4ResolvedSpecialization` is canonicalized and hashed under the same
finite-JSON rules as `GRCV4ResolvedParams`; its payload and digest are both
serialized. A policy label without the resolved payload is invalid.

## Observables

In addition to enabled `GRCV4` observables, expose:

- `active_port_degree`
- `port_occupancy`
- `row_gradient`
- `signed_row_hessian`
- `row_net_flux`
- `hybrid_spark_candidates`
- `mechanical_expansions`
- `completed_sparks`
- `hierarchy`
- `coarse_columns`
- `coarse_profiles`
- `compatibility_branch`
- `grc9v3_target_version`

The per-column $H_s^{(b)}$ diagnostic is required only for the named assisted
lane or when explicitly selected as a diagnostic. Candidate, expansion, and
completion counts must remain distinct.

## Serialization

A snapshot must satisfy the full `GRCV4` contract and preserve:

- unique edge and occupied endpoint-port identities;
- fixed chart, row backend, sign, and spark-lane identity;
- basin and hierarchy lifecycle identity;
- expansion policy and distribution configuration;
- every expansion event's canonical digest payload, module chirality,
  conditional growth phase, role-ID allocation, port plan, bond seed,
  resource/history disposition, and target-readmission receipt;
- coarse-graining mode and enough provenance to rebuild or reject caches;
- enabled/disabled branch identity;
- exact GRC9V3 target specification identity; and
- migration, event, history-loss, and compatibility receipts.

Port or topology changes invalidate dependent row, basin, current, geometry,
and coarse caches. Restoration must reconstruct and readmit them before state
is exposed.

## Errors and atomicity

In addition to `GRCV4` failures, the implementation must fail closed for:

- duplicate or invalid port occupancy;
- invalid row/column chart identity;
- a nonbaseline backend presented as baseline;
- saturation or spark-lane ambiguity;
- capacity, attachment, or redirection failure during expansion;
- `module_chirality_required`, `module_growth_phase_required`, or
  `reject_noncanonical_inactive_growth_phase`;
- missing, duplicate, or colliding expansion role identities;
- resource split or event-charge failure;
- missing history policy or target readmission after expansion;
- coarse/Split domain or reconstruction failure;
- assisted-lane evidence represented by a proxy;
- unsupported GRC9V3 target version; or
- `legacy_expansion_target_undefined` outside
  $\mathcal D_{\mathrm{V3,defined}}$; or
- failure of any one disabled transition, state, observable, or lifecycle
  contract.

All ordinary steps, migrations, and expansions commit atomically or leave the
complete prestate authoritative.

## Claim bindings and boundaries

The complete [GRCV4 claim matrix](grc-v4-spec.md#claim-conformance-matrix) is
inherited. `D10-CL-N-007` is normatively represented here by 40 independent
compatibility requirements. `D10-CL-N-001`, `D10-CL-N-005`, `D10-CL-N-006`, and
`D10-CL-N-008` remain load-bearing in the specialization.
`D11-G9-CL-N-001` binds the exact enabled expansion and legacy-domain
boundary, while inherited `D11-C-CL-O-001` controls target Candidate C
reconstruction. The optional,
conditional, open, and negative claims retain their original status.

In particular, this specification does not establish that nine ports are
necessary or unique; that the chart is a continuum primitive; that the
historical row tensor is graph $K_4$; that mechanical expansion alone is a
completed spark; that column coarse-graining is generic graph coarsening; that
the assisted spark lane is the default; that any enabled V4 profile is merely
GRC9V3; or that transition equality proves state, observable, or lifecycle
equality. It also does not claim that the accepted chirality is physically
selected or that this expansion is unique among all possible GRC9V4 designs.

Runtime implementation and compatibility evidence remain separate from this
design-level contract.

[paper-a]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#appendix-a-grc9v4-nine-port-specialization-of-grc-v4
[proposal-a]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#appendix-a-grc9v4-nine-port-specialization-of-grc-v4
[d10-2]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.md
[d11-open]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D11SuccessorInvestigationOpening.md
[d11-g9-resolution]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationResolution.md
[d11-g9-provenance]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D11G9AxisPreservingExpansionProvenanceSupplement.json
