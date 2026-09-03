# GRC9V4 Specification

## Status and authority

This file is the normative implementation contract for `GRC9V4`, the
substantive nine-port specialization of [`GRCV4`](grc-v4-spec.md).

Primary sources:

- [GRC-v4 paper, Appendix A][paper-a]
- [GRC-v4 proposal, Appendix A and provenance crosswalk][proposal-a]
- [G-RC-9 paper](../papers/2026-04-GRC-9.md)
- [GRC9V3 legacy target specification](grc-9-v3-spec.md)
- [D10.2 substrate provenance and promotion audit][d10-2]
- [Common GRC interface: V4 extension](grc-common-interface-v4-ext.md)

The complete [`GRCV4` specification](grc-v4-spec.md) is imported unchanged.
This file adds only nine-port mechanics, the fixed GRC9 differential backend,
GRC9 mechanical event and coarse-graining contracts, and exact profile-scoped
disabled compatibility with `GRC9V3`. It does not redefine the graph-generic
V4 candidate, realization, resource, geometry, or lifecycle laws.

The accepted forensic partition assigns exactly 53 equation contracts to this
specialization: 13 specialization parent contracts and 40 independent
profile/surface compatibility contracts. Their support semantics remain
`indeterminate_requires_review`; the specification preserves their source
classification and does not treat dependency reach as scientific ranking.

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
    expansion_policy_id: str
    expansion_distribution_mode: Literal["equal", "custom"]
    coarse_graining_mode: Literal["nonnegative", "signed_split"]
    grc9v3_target_spec_version: str
    compatibility_branch: Literal["enabled_v4", "disabled_grc9v3"]
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

Each occupied endpoint pair must be unique. For the selected edge orientation,
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
    orientation: int

@dataclass
class GRC9V4State(GRCV4State):
    port_edges: dict[EdgeId, GRC9V4PortEdge]
    hierarchy: Mapping[str | int, list[str | int]]
    basin_identity: Mapping[NodeId, str | int]
    coarse_cache: Mapping[str, Any]
```

The inherited `GRCV4State` authority rules remain controlling. Basin,
hierarchy, event, and graph identity are lifecycle surfaces; row summaries and
coarse caches are derived.

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

The baseline internal edges are

$$
(c,2)\leftrightarrow(s_1,5),\qquad
(c,5)\leftrightarrow(s_2,5),\qquad
(c,8)\leftrightarrow(s_3,5).
$$

Additional nodes attach deterministically under the three satellites when
$n_{\mathrm{canonical}}>4$. An old boundary endpoint in column
$\mathcal C_b$ is redirected to satellite $s_b$ while preserving the port
label.

For the unit-measure equal-split baseline,

$$
C_{s_b}=\frac13C_s,
\qquad C_c=0.
$$

A custom $p_b$ must satisfy $p_b\ge0$ and $\sum_bp_b=1$ and is
identity-bearing event configuration.

Expansion is a typed `GRCV4` topology event. Before atomic commit it must map
both current and reset resource state, update $Q_{\mathrm{target}}$, transport
or explicitly lose A and PC history, rederive Candidate C surfaces, rebuild
RG2b completion, bind graph/profile/hierarchy identity, emit receipts, and pass
target readmission. A graph rewrite alone is not an admitted expansion.

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
V4 topology event must not be relabeled as a GRC9V3 event.

## Step and event ordering

An enabled V4 ordinary beat follows the exact transaction in
[`grc-v4-spec.md`](grc-v4-spec.md#complete-step-transaction), with the fixed
port graph and row backend supplying its specialization context.

Spark processing is lifecycle/event work. Candidate detection may occur at a
declared stage, but an expansion must execute as a typed topology event between
admitted lifecycle states. The post-event state then resumes ordinary V4
stepping; completion is registered only after child-basin stabilization.

The disabled branch executes the legacy `GRC9V3` step as a target transition.
It must not approximate that transition by running enabled V4 equations with
small coefficients.

## Parameters

`GRC9V4` parameters include the complete `GRCV4` profile plus:

- fixed port and chart identity;
- row-basis differential and Hessian sign configuration;
- basin and spark thresholds;
- explicit spark lane;
- expansion capacity and deterministic attachment policy;
- equal or custom resource-distribution policy;
- hierarchy and child-stabilization policy;
- nonnegative and signed column coarse-graining modes;
- exact GRC9V3 target version and projection rules; and
- numeric tolerances used for target readmission and compatibility checks.

Defaults must resolve at construction. No environment variable, cache state,
or solver history may alter these semantics after profile resolution.

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
- resource split or event-charge failure;
- missing history policy or target readmission after expansion;
- coarse/Split domain or reconstruction failure;
- assisted-lane evidence represented by a proxy;
- unsupported GRC9V3 target version; or
- failure of any one disabled transition, state, observable, or lifecycle
  contract.

All ordinary steps, migrations, and expansions commit atomically or leave the
complete prestate authoritative.

## Claim bindings and boundaries

The complete [GRCV4 claim matrix](grc-v4-spec.md#claim-conformance-matrix) is
inherited. `D10-CL-N-007` is discharged here through the 40 independent
compatibility rows. `D10-CL-N-001`, `D10-CL-N-005`, `D10-CL-N-006`, and
`D10-CL-N-008` remain load-bearing in the specialization. The optional,
conditional, open, and negative claims retain their original status.

In particular, this specification does not establish that nine ports are
necessary or unique; that the chart is a continuum primitive; that the
historical row tensor is graph $K_4$; that mechanical expansion alone is a
completed spark; that column coarse-graining is generic graph coarsening; that
the assisted spark lane is the default; that any enabled V4 profile is merely
GRC9V3; or that transition equality proves state, observable, or lifecycle
equality.

Runtime implementation and compatibility evidence remain separate from this
design-level contract.

[paper-a]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#appendix-a-grc9v4-nine-port-specialization-of-grc-v4
[proposal-a]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#appendix-a-grc9v4-nine-port-specialization-of-grc-v4
[d10-2]: ../implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.md
