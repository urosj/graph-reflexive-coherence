# D11-G9 Axis-Preserving Chiral Same-Port Expansion Resolution

**Gate:** D11-G9
**Status:** Accepted bounded
**Record:** `GRC9V4-CD-D11-G9-RESOLUTION-v1`
**Predecessor:** `GRC9V4-CD-D11-G9-v1`
**Decision digest:** `a0813ceead2c992ec197790abd8a0ceea167ae2d952f853cf48f1db4d8001615`
**Selected candidate:** D11-G9-P4a
**Selected profile:** `grc9v4_axis_preserving_chiral_same_port_expansion_v1`
**Human acceptance:** Accepted bounded on 2026-09-03

## Decision

D11-G9 accepts the submitted axis-preserving chiral same-port construction,
with three bounded corrections:

1. `growth_phase` is `none` exactly when the extra-node remainder is zero and
   is required to be `1`, `2`, or `3` otherwise;
2. stable event, node, and edge identity uses the exact grammar retained from
   the earlier P1a audit; and
3. Candidate C and persistent $K_4$ event handling remain bound to accepted
   D11-C and whole-carrier lifecycle authority.

The result is GRC9V4 specialization authority only. It changes neither
graph-generic GRCV4 mathematics nor GRC9/GRC9V3 source artifacts. It closes a
design-level mechanical and lifecycle contract; it does not claim runtime
conformance, a completed child, stability, endpoint effect, physical
chirality selection, or uniqueness among all possible GRC9 expansions.

## Evidence Boundary

The forensic surface confirms that D10.2 contains the parent
`column_preserving_mechanical_expansion` contract but no collision-free
internal port plan. The load-bearing receipts remain:

| Query | Disposition |
|---|---|
| `contract_provenance(D10.2-EC-PARENT-GRC9-MECHANICAL-EXPANSION)` | `indeterminate_requires_review`; trace `4c8c2010503d76c0c6d927b7932e334aeb2887f8d06e3cd46bf02b2e482e22b8` |
| `object_dependents(GRC9-MECHANICAL-EXPANSION)` | source-exact dependency trace `8ffa09b524b4b880a010a8878af07c260f33b6211e8e0f05c8aaf51fc2a6e4e9` |
| `contract_provenance(D10.2-EC-PARENT-L-TOPOLOGY-EVENT)` | `indeterminate_requires_review`; trace `382b72723eb4f331c45a22bc7d4eccf9422a1f631d994b81a17997b4737dbc3b` |
| `negative_claims()` | 14 rows; trace `f8887156d233772b858dd18980bbfd67782076fc5f424f7b5e50dbf318a51cc3` |

The live forensic build continues to fail closed on unprocessed D11 sources;
these queries were therefore run through the same forensic functions against
the clean pre-D11 accepted snapshot. The result is new authority, not an
extraction of authority already present in D10.2.

## Confirmed Legacy Conflict

The accepted source is exactly saturated, so old source port $5$ exists. Its
column-preserving boundary map requires

$$
(s,5)\longmapsto(s_2,5).
$$

The inherited second spine edge also requires

$$
(c,5)\leftrightarrow(s_2,5).
$$

Two different edges therefore claim the same local target endpoint. Operation
order and parallel-edge support cannot repair this port-capacity violation.

## Selected Primary Spine

For rows and columns $a,b\in\{1,2,3\}$, port $r$ is

$$
r=b+3(a-1).
$$

Define three-cycle addition by

$$
x\oplus_3 k=1+((x-1+k)\bmod 3).
$$

For explicit module chirality $\epsilon\in\{-1,+1\}$, define

$$
\beta_\epsilon(b)=b\oplus_3\epsilon,
\qquad
r_b^\epsilon=\beta_\epsilon(b)+3(b-1).
$$

The selected primary edges are

$$
\boxed{
(c,r_b^\epsilon)\leftrightarrow(s_b,r_b^\epsilon),
\qquad b=1,2,3.
}
$$

The two mirror realizations are

$$
\epsilon=+1:
\quad
(c,2)\leftrightarrow(s_1,2),\qquad
(c,6)\leftrightarrow(s_2,6),\qquad
(c,7)\leftrightarrow(s_3,7),
$$

and

$$
\epsilon=-1:
\quad
(c,3)\leftrightarrow(s_1,3),\qquad
(c,4)\leftrightarrow(s_2,4),\qquad
(c,8)\leftrightarrow(s_3,8).
$$

Each primary edge uses the same port type at both endpoints. Each row and each
column appears exactly once. Because $\beta_\epsilon(b)\ne b$, the internal
satellite port lies outside the satellite's inherited boundary column.

## Exact Boundary Map

All nine old boundary endpoints are reserved before internal allocation. For
an old edge whose source endpoint is $(s,r)$ and external endpoint is $(j,t)$,

$$
\boxed{
((s,r),(j,t))
\longmapsto
((s_{b(r)},r),(j,t)).
}
$$

The map preserves old edge identity, the external endpoint, local port, row,
column, and declared coordinate orientation.

## Arbitrary-Size Tree

For integer desired capacity $D_{\mathrm{eff}}\ge9$,

$$
n_{\mathrm{cap}}
=\left\lceil\frac{D_{\mathrm{eff}}-2}{7}\right\rceil,
\qquad
n_{\mathrm{canonical}}=\max(4,n_{\mathrm{cap}}).
$$

Let $m=n_{\mathrm{canonical}}-4=3q+\rho$. When $\rho=0$,
`growth_phase` must be `none`. When $\rho>0$, an explicit
$\phi\in\{1,2,3\}$ selects the first remainder branch, and a second remainder
follows in chirality order. Thus branch counts differ by at most one.

Every internal edge in branch $b$ uses row $b$. At a branch node with incoming
column $c$, the ordered outward rotor is

$$
\mathcal O_\epsilon(c)
=\left(c\oplus_3\epsilon,c\oplus_3(-\epsilon)\right).
$$

Within each branch, the first creation-order node with an unused rotor port is
the parent. The next local-ordinal child uses that identical port at its own
endpoint. This is a creation-order breadth-first same-port tree.

Each primary branch begins with one free recursive valence. Each child consumes
one parent valence and contributes two, so available valence changes by $+1$.
The allocator cannot stall for any finite admitted module size.

The completed module is connected and acyclic with $n-1$ internal edges. Its
external capacity is

$$
\boxed{
D_{\mathrm{ext,max}}(n)
=9n-2(n-1)
=7n+2.
}
$$

Internal row counts and internal column counts each differ by at most one.

## Chirality, Phase, and Covariance

Chirality is explicit event identity. A symmetric source without an admitted
chirality fails with `module_chirality_required`. An active remainder without
a phase fails with `module_growth_phase_required`; supplying a phase when no
remainder exists is also noncanonical and fails closed.

No port number, node-ID parity, iteration order, thread schedule, global event
counter, or hidden random state selects either phase.

Simultaneous cyclic row, column, and branch rotation rotates an active growth
phase and preserves chirality. Reflection flips chirality and reflects an
active phase. The two primary spines are therefore equal-standing mirrors.

## Stable Identity

The event ID has grammar
`grc-event-sha256:<64-lowercase-hex-digits>`. Its digest payload binds the
source graph and sink, $D_{\mathrm{eff}}$, module size, chirality, canonical
growth phase, port policies, bond seed, resource map, and candidate/history
policies.

Base role IDs are:

```text
<event-id>/core
<event-id>/satellite/1
<event-id>/satellite/2
<event-id>/satellite/3
<event-id>/internal/1
<event-id>/internal/2
<event-id>/internal/3
```

For $w=\max(1,\operatorname{len}(\operatorname{decimal}(m)))$, extra roles are:

```text
<event-id>/extra/<b>/<local-ordinal-zero-padded-to-w>
<event-id>/internal/extra/<b>/<local-ordinal-zero-padded-to-w>
```

Old edge IDs are preserved. Missing, duplicate, or colliding role IDs reject
the event before commit.

## Bond, Resource, and Lifecycle Closure

The selected profile uses one resolved $w_{\mathrm{bond}}>0$ on every new
internal reference edge and sets its incoming/reference current to zero. This
chart-neutral seed is not Candidate A history, Candidate C state, persistent
$Z_4$, or a completed current solve.

For the unit-measure profile,

$$
C_c^+=0,
\qquad
C_{s_b}^+=p_b C_s^-,
\qquad
C_{x_{b,\ell}}^+=0,
$$

where $p_b\ge0$ and $\sum_b p_b=1$; the canonical baseline is
$p_1=p_2=p_3=1/3$. The same typed map applies to current and reset resource
state, and $\Delta Q_{\mathrm{event}}=0$ for this unit-measure profile.

The accepted lifecycle boundary is:

- Candidate A uses exact old-edge lineage and an admitted positive target
  initializer, another admitted full target policy, or explicit full-target
  history loss;
- Candidate C's complete target profile supplies the entire exact
  $W_{C,\mathrm{tr}}$ map before $T_C$, Hodge, $\Phi_{0,C}$, $J_{0,C}$,
  response, geometry, and analysis surfaces are rederived;
- persistent $K_4$ history uses one typed whole-carrier
  $L_{K4,\mathrm{evt}}$ or archives the whole source carrier, resets the whole
  target $Z_4$ carrier to zero, and emits a loss receipt; and
- RG2b and every realization rebuild target surfaces and pass target
  readmission before one atomic commit.

Partial $K_4$ preservation with zero-filled new components remains forbidden.
Any failed target check preserves the complete source lifecycle state.

## Legacy Compatibility Boundary

GRC9 and GRC9V3 remain unchanged. Exact disabled compatibility is claimed only
on the domain where the selected legacy authority determines a unique target.
The saturated port-5 expansion is outside that domain.

If the disabled branch reaches this event, it returns
`legacy_expansion_target_undefined`, identifies the conflicting clauses, and
commits no graph, resource, state, history, reset, or receipt mutation. It does
not execute the enabled chiral V4 rule and relabel it exact V3. A pinned legacy
runtime emulation would be a separate digest-bound non-normative profile.

## Comparison Disposition

| Candidate | Result |
|---|---|
| Inherited all-center spine | Rejected: saturated port 5 collision. |
| D11-G9-P3 minimum endpoint repair | Superseded: collision-free but still center-axis privileged and type-mismatched. |
| D11-G9-P1/P1a cyclic satellite repair | Superseded: collision-free and lifecycle-complete after refinement, but internal endpoints have mismatched port types and canonicality depends on chart-number order. |
| D11-G9-P2 inverse repair | Not selected for the same axis/type reason. |
| D11-G9-P4 submitted chiral same-port law | Refined to correct phase, identity, Candidate C, and $K_4$ lifecycle boundaries. |
| **D11-G9-P4a** | **Selected accepted bounded.** |

## Witness and Claim Ceiling

The executable witness checks all integer $D_{\mathrm{eff}}=9,\ldots,5000$,
both chiralities, every active phase, 1,000 source-edge order shuffles, and
rotation/reflection covariance. It passes 23,256 admitted plan cases with:

```text
positive primary spine             = (2, 6, 7)
negative primary spine             = (3, 4, 8)
unique local endpoint occupancy    = pass
exact inherited boundary ports     = pass
same-port internal typing          = pass
connected acyclic tree             = pass
row/column imbalance at most one   = pass
capacity 7n+2                      = pass
inactive/missing phase rejection   = pass
rotation/reflection covariance     = pass
```

This is finite combinatorial, identity, and covariance evidence. Runtime
atomicity, history transport, target readmission, child-basin formation,
stability, and endpoint effect remain forward obligations.

## Claim, Debt, and Provenance Effect

The append-only provenance supplement adds:

- one `GRC9V4_specialization_normative` successor claim,
  `D11-G9-CL-N-001`;
- nine reciprocal claim edges without rewriting or reclassifying predecessor
  claims;
- ten GRC9V4-only normative specialization objects; and
- twenty subordinate equation/lifecycle contracts.

The accumulated current population is therefore 80 objects and 183 equation
contracts: D10.2's 67/152, D11-C's 3/11, and D11-G9's 10/20. All 39 current D10
claims, 29 historical claim nodes, 29 prior debt transformations, and the
accepted D11-C successor claim remain unchanged.

`D11-G9-DEBT-CANONICAL-PORT-ALLOCATION` is resolved boundedly by P4a. The ten
inherited pending forward obligations, three D11-C obligations, and four new
D11-G9 obligations remain pending, for seventeen total. No implementation
evidence has been silently discharged.

## Propagation State

D11-G9 is now closed accepted bounded. The paper is the next authorized
surface; specification propagation remains blocked until the paper records
this result. The current P1 text in the specification remains explicitly
provisional and unchanged in this resolution step. Implementation and changes
to GRC9/GRC9V3 remain unauthorized.

Authoritative companion registry:

- [`D11G9AxisPreservingExpansionProvenanceSupplement.json`](./D11G9AxisPreservingExpansionProvenanceSupplement.json)

Executable witness:

- [`witness_d11_g9_canonical_expansion.py`](../scripts/witness_d11_g9_canonical_expansion.py)
