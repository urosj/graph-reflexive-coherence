# P9-10.1a — Baseline basin interface authority proposal

Date: 2026-10-28. Status: **proposed; not accepted or implemented**.
Owner: P9-10.1a. Baseline: `1735d671` after bounded P9-9.6 acceptance.
The [authority audit and open debt](../evidence/p9-basin-interface/AuthorityAudit.json)
retain exact forensic queries and their limitations. This proposal is outside
the accepted claim graph. No D10/D11 claim or legacy version is changed.

The [independent review](../evidence/p9-basin-interface/IndependentReview.md)
passes the finite represented-flow mathematics and supports the diagnostic
direction, with BIF-1/BIF-2/BIF-3 corrections incorporated below. This is not user
acceptance. Initial native implementation scope is exactly **C_OS, C_CI, A_CI,
A_PC**, as in the [accepted P9-9.6 decision](../../../phase-9-grcv4/tranche-9/P9-9.6-Acceptance.json).
The graph argument itself grants no runtime support to any family.

## Finding

The missing public interface exposes an earlier contract gap. The
[V4 specialization spec](../../../../specs/grc-9-v4-spec.md#capabilities)
requires `basin_attributes`, and its lifecycle state includes `basin_identity`.
Its seed inequality and the [paper A.5](../drafts/2026-09-GRC-V4.md#a5-saturation-and-the-hybrid-spark-candidate)
define a local geometric test. Neither selects a complete enabled-V4 rule for
membership, ambiguous flow, cycles, identity assignment or identity lifetime.
The completion section explicitly withholds a default child-stability classifier.
Those are different obligations: completion-off does not erase the baseline gap.

The existing runtime implements the local test, fresh row summaries and spark
candidate detection. That is useful implemented authority, not a basin partition.
The forensic API resolves the row, spark, completion, snapshot and disabled
lifecycle contracts, retaining their original `indeterminate_requires_review`
support dispositions. `GRC_basin_identity` appears as a premise string in D10.2
but `object_dependents` cannot resolve it as a normative object. This rejection
and the inventory search are bounded observations, not proof that no conceivable
source can supply a rule. The textual source audit also finds no selected V4
membership/ID producer in the relevant paper/spec contracts.

The [V3 identity semantics](../../../../specs/grc-v3-spec.md#identity-semantics)
give useful direction: expose flux-topological and geometric layers separately.
The legacy runtime selects the strongest positive outgoing edge, resolves ties
with node/edge labels, and optionally renames a region using a unique geometric
seed. This is exact disabled-branch behavior. Transferring it to enabled V4
would be a new choice, including its treatment of competing routes and cycles.
The [D4 ownership record](D4GeometryMobilityAndTopologyOwnership.json) additionally
forbids treating geometry/mobility changes as basin birth and requires typed
interspace transport and accounting when identity changes enter its state-space
or cross-state comparison contract. Direct dynamical feedback is not the only
way that requirement can apply; section 4 states the diagnostic bridge.

## Recommended bounded contract for review

Select a **read-only flow-region identity with separate geometric attributes**,
named `grc9v4-terminal-flow-regions-v1`. It describes the present represented
current. It does not claim a dynamical attraction basin, stability, identity
persistence, basin birth, abundance or completed sparks. The scientific choice
is explicit and must be accepted before capability advertisement.

### 1. Inputs and stage

Capture one admitted enabled state, its port graph, complete model identity,
context and numerical policy. Reconstruct the fresh current from that state's
current C/W/Z and its selected realization, using the existing poststate
readmission contract. Bind the actual read stage and input state digest.
Do not substitute the preceding beat's consumed current, predictor, old W/Z,
or cached rows. A successful operation uses the fully reconstructed prospective
target before publication; a read-only query uses one captured publication.
Both current and reset roles are reconstructed independently when needed.

**One capture per observation (BIF-2).** The observation binds the current/reset
role, exact profile/model and graph/orientation identities, context contract and
value digest, numerical policy and exact backend, evaluator/release identity,
actual read stage, and the applicable root/solver/certificate binding. Membership,
cycle evidence, flux summaries and seed attributes consume that one captured
fresh read and its associated C/W/Z/row operands. They may not independently
re-solve the state to assemble different fields of one observation. An absent
optional certificate reference is explicit null, not an invented proof.

Use an existing read identity only if it binds these operands and their exact
represented values. Otherwise derive `operand_digest` from a canonical, typed
capture: stable-edge-indexed current values, typed endpoints, associated row
gradient/signed-Hessian/net-flux operands, and resolved sign/threshold values.
Encode each binary64 operand losslessly (canonical `float.hex()` strings,
including signed zero); edge identities and ordering follow the declared graph.
This is a read witness, not another authoritative current or retained history.
If arcs are not listed separately, this witness must remain retrievable with
an exported observation; a digest without the operands is not the arc evidence.

The closed observation binding includes `role_state_digest`: for current, use
the existing `GRC9V4NativeEventState.scientific_payload` projection (generic
scientific preimage plus active model and reset digest); for reset, use its
existing `reset_payload` projection, then bind the reset role's reconstructed
read and context explicitly. These predecessor projections exclude the new
basin bundle, observation digest and derived labels. Hash the binding plus
`operand_digest` and policy/schema IDs to obtain `observation_digest`.
Do not make the bundle its own digest preimage. These are content bindings:
identical reset/replay content can produce the same observation digest, and no
unique temporal occurrence or persistent basin identity is asserted.

For each represented edge current J, positive means tail-to-head under the V4
outward-incidence convention; negative reverses the arc. Both signed zeros add
no arc. No epsilon, clipping or flux aggregation is introduced. Opposing flows
on distinct parallel edges remain distinct arcs. Invalid/nonfinite inputs fail
explicitly. Exact-real current signs or uniform robustness to perturbations are
not inferred from represented signs, especially near zero.

### 2. Membership without an external tie-break

Use every nonzero directed arc. Contract strongly connected components (SCCs)
to the finite condensation DAG. For each node v, let R(v) be the nonempty set
of terminal SCCs reachable from its component, including that component itself
when terminal. Retain this set as structural evidence, not as probabilities.

Classify a terminal component as follows:

- **sink:** one node, no self-loop, and at least one incoming arc from outside;
- **recirculating:** multiple nodes, or a nonzero self-loop;
- **quiescent:** one node with no nonzero incident arcs.

A node with exactly one reachable terminal, which is a sink, belongs to that
sink's flow region. A node reaching multiple terminals is **ambiguous** and
has no basin assignment. A node reaching only a recirculating or quiescent
terminal reports that status and has no basin assignment. These are meaningful
diagnostic outcomes, not model admission failures or synthetic singleton basins.
The map `basin_identity` is explicitly partial; all nodes have status and
reachable-terminal information, so missing assignment cannot be mistaken for
an absent record. Do not silently select the strongest edge or break a symmetry
using labels. This proposal intentionally differs from the legacy classifier.

This is a finite graph definition. Every component reaches a terminal in a
finite DAG. The uniquely assigned regions are disjoint: a node cannot have
two distinct singleton reachable-terminal sets. They need not cover the graph.
Each assigned region is forward-closed in this frozen directed graph: if v is
assigned to sink s and v points to w, the nonempty R(w) is a subset of R(v)={{s}}.
Each assigned node has a directed path to s inside that region. A quiescent
terminal cannot have a distinct upstream node, since an incoming arc would
contradict quiescence. These are frozen-input properties, not temporal invariants.
Following a current path forever, future convergence, or stability under V4
evolution is not established by these facts. A current-cycle upstream of a sink
does not become a proved dynamical attractor or disappear from the evidence.

**Full cycle evidence (BIF-1).** Retain every SCC, terminal and nonterminal, with
its members, terminal flag and `cyclic` flag (multiple members or a nonzero
self-loop). Each node names its own component independently of its reachable
terminal set/status. A node upstream of a recirculating terminal need not itself
be cyclic. Retaining terminal components alone cannot distinguish a→b→s from
a↔b→s, although both assign all three nodes to s. A condensation-edge list is
optional because the bound, retrievable current-read witness supplies all arcs.

Zero flow gives only quiescent nodes and no assignments. On a closed graph,
exactly divergence-free represented current also gives no assignments: a
singleton sink would have strictly negative outward divergence equal to minus
its positive incoming magnitudes. This contradicts B J=0. Cycles and zero flow
can therefore yield an empty assignment while meaningful geometry remains.
That is a policy consequence, not failed admission or evidence that stable
dynamical structures are absent. Geometric seeds never override membership.

### 3. Geometry remains a separate layer

Expose the declared row gradient, signed row Hessian and net-flux summary,
with the local geometric seed flag

$$
\|g_i\|^2 < \varepsilon_\nabla^2,
\qquad \min\operatorname{diag}(\widetilde H_i)>\varepsilon_H>0.
$$

Square both the represented coordinates and represented threshold exactly for
the first inequality; do not first form rounded squares that can underflow or
overflow. Equality fails both strict tests. Resolve thresholds and the sign
through the declared binding and use the existing diagonal fixed-row contract.
Seed classification does not require nine-port saturation. Report seed nodes
inside each assigned region, including zero/one/multiple seeds; do not rename,
merge or certify that region merely because a seed exists. A geometric seed
outside an assigned flow region remains visible. No new numeric abundance is
defined, and neither layer controls current, writers, admission or spark gating.

### 4. Identity and public representation

The proposed interface has a closed typed `basin_attributes` bundle containing:
policy/schema IDs, the observation binding and read witness from section 1,
all components with members/cyclicity/terminal flag (terminal kind is null for
nonterminals), per-node own-component/terminal-set/status/optional-ID records,
assigned regions with members, and geometric seed attributes. Public state
exposes the same **derived**, partial `basin_identity` map reconstructed from
that state. Current/reset views are never interchangeable.

**Typed wire identity.** Normalize IDs through the existing V4 node-ID contract,
then preserve integer versus string identity in typed per-node entries:
`{"kind":"int","value":0}` differs from `{"kind":"str","value":"0"}`.
The empty string is an ordinary supported node ID. Do not use stringified node
IDs as JSON object keys. Unassigned basin ID is explicit null; the node's entry
must still exist. Reject duplicate typed IDs, absent node entries, invalid
component references and inconsistent membership.

Canonical order is representation-only: integers before strings, then unsigned
lexicographic comparison of each typed ID's canonical JSON bytes. Sort component
members by that key, components lexicographically by their member-key tuples,
and use their zero-based canonical indices as local component references. Sort
terminal references numerically and per-node/region entries by typed node key.
Never use this ordering to choose between flow destinations. Node-bearing
identity preimages, including `sink_node_id` below, use the same typed encoding.

For an assigned sink s, define

```text
basin_id = "grc9v4-flow-basin-sha256:" + SHA256(JCS({
  policy_id, graph_digest, sink_node_id: s
}))
```

This identifies a flow region by its terminal on the declared graph. Membership
can change while this label stays the same; the observation state digest records
the state content and the observation digest binds the actual captured read.
A label reused after disappearance does not prove
persistent physical identity. Graph changes produce graph-scoped new IDs, with
no implied parent/child lineage. Node relabeling transports members and terminal
references and recomputes IDs; raw hash equality is not the covariance criterion.
Orientation reversal together with current sign reversal leaves the physical
directed graph, partition and statuses unchanged. If that representation change
changes the declared graph digest, IDs are recomputed from the transported
binding. Permuting serialized edge/vertex order likewise preserves semantic
classification; neither transformation promises raw hash equality across
different graph encodings. Covariance here assumes transported represented
operands. Re-solving after coordinate reordering at finite precision is a
separate numerical conformance obligation, not a consequence of this graph proof.

The new policy must be explicitly bound in a V4 specialization/schema successor;
it must not be inferred for old complete-model identities. Historical models
retain their recorded partial support. Migration to the successor re-admits both
roles and binds the chosen policy. A changed classifier opens a different
binding.

**D4/D9 bridge (BIF-3).** These flow-region labels are derived diagnostic
references, not transported physical basin identities. Recomputing them supplies
no interspace identification. Any use of regions or their changes to define
causal state, normalization, hierarchy, events, or cross-state comparisons
invoking D4/D9 must satisfy the separately applicable transport and accounting
contract, even if there is no direct feedback into current. Equality of a basin
hash while membership changes cannot authorize comparison of basin-indexed
coordinates. An unrelated graph edit can change every graph-scoped hash without
establishing physical basin birth.

The schema successor marks this field as derived and cannot silently overwrite
older snapshot meaning. Reject unreviewed use of these labels as an authoritative
admission, spark or writer input. Do not emit physical events for harmless
diagnostic relabeling. Ambiguous, quiescent and recirculating observations remain
successful diagnostic results; a classifier/serialization error is different.

### 5. Lifecycle and failure semantics

Reconstruct the bundle on construction, fresh observation, ordinary commit,
assignment, expansion, migration, reset and load. Rebase changes which state is
the reset baseline; it must not copy a stale current bundle into another role.
Snapshots bind the policy/schema and contain enough admitted state to reconstruct
both roles. If a captured observation is serialized for exact replay, retain its
read witness/binding and require exact reconstructed binding and operand identity
before claiming the same observation or exact derived-label replay. Incompatible
read identity fails explicitly; it cannot silently accept different signs merely
because a numerical tolerance passed. A state-only historical restore without
such an observation can produce a **new observation**, with its own explicit read
binding; it does not claim equality to an unretained observation. This mode is
explicit, not a fallback after failed exact-observation replay.

The [numerical policy](../../../../specs/grc-v4-numerical-policy.md) certifies
staged rounded solves where applicable, and explicitly separates execution
policy from scientific state. That alone is not a proof of deterministic signs
for every whole-model read. Propagation must name the supported evaluator/backend/
policy/release scope and native conformance must demonstrate repeated fresh reads,
reset/load and replay against captured operands for each selected family.
If an existing read contract supplies exact reconstruction, cite and verify it;
do not infer it from a residual/error tolerance. No cross-policy or cross-platform
bitwise promise is added by this proposal, nor an epsilon or exact-real sign claim.
No second mutable owner, hidden basin history or new numerical current is added.
Preparation computes and validates the advertised target surface before sole
publication. A classifier/serialization failure aborts that operation with full
rollback; it cannot publish stale data or downgrade a promised capability.

Historical snapshots lack this selected producer. They remain readable under
their historical schema; no silent upgrade supplies new basin semantics. The
disabled branch keeps exact native GRC9V3 state/observable/lifecycle behavior.
Enabled V4 flow labels are not transplanted into that delegate.

## Alternatives and evidence needed

| Choice | Consequence |
| --- | --- |
| Expose seed flags only | Useful partial work; leaves membership and lifecycle identity undefined. |
| Copy V3's strongest-flow successor | Concrete legacy convention, but chooses among lawful competing V4 routes and introduces label-dependent tie selection. Needs separate acceptance if preferred. |
| Assign every node to its own basin | Invents a partition unrelated to the flux/geometry contract. |
| Proposed all-route terminal classification | No arbitrary winner; explicitly represents ambiguity, recirculation and no-flow cases. Does not establish attracting basins. |

The [small exact checks](../scripts/check_p9_basin_interface_proposal.py) pressure
this proposed finite graph rule against a separate reachability oracle, plus
branching, cycles, zero flow, parallel opposite currents, relabeling/orientation
and strict seed boundaries. They are investigation-local conditional mathematics,
not native V4 execution or scientific acceptance of the selected classifier.
Review regressions additionally retain the upstream-cycle distinction, typed
IDs, exact capture/replay mismatch, forward-closure/quiescent properties,
divergence-free exclusions and underflow/overflow-sensitive seed comparisons.
The independent review reports a larger external campaign, but its `pressure.py`
and `integrity.json` were not supplied with the review. Those reported runs are
not presented as locally rerun or authenticated execution evidence.

Before production: review/adjudicate the new claim/debt; admit the accepted
successor through the side-tool; update proposal, review then paper; propagate
the V4-only spec/schema contract. Only then implement P9-10.1a for the four
selected families using small native fixtures and full lifecycle/atomicity
checks. Include actual fresh C/W/Z read stages and both histories. Keep the
other six runtime families, completed sparks/hierarchy, numeric abundance and
P9-10.1b/c outside this acceptance. Do not rerun Tranche 8 campaigns.

The bounded choice requiring review is whether these **flow-region labels and
separate seed attributes** are the intended baseline basin surface. If the
baseline must instead identify genuine stable attraction basins, a stability
classifier and temporal semantics are required; this proposal does not provide
that stronger scientific result. P9-10.1a remains open until the intended
contract is accepted, propagated and implemented.
