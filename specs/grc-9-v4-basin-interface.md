# GRC9V4 baseline basin diagnostic successor

## Status and authority

Normative bounded design, accepted 2026-10-28. This supplement to
[GRC9V4](grc-9-v4-spec.md) implements the meaning selected by
[`P9-10.1a-CL-N-BASIN-001`](../implementation/investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json)
and propagated into [paper A.5.1](../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#a51-baseline-represented-flow-regions-and-geometric-seeds).
The [design acceptance](../implementation/phase-9-grcv4/tranche-10/P9-10.1a-DesignAcceptance.json)
does not establish native conformance. Initial implementation/conformance scope
is C_OS, C_CI, A_CI, A_PC. No other family execution is inferred.

The policy is `grc9v4-terminal-flow-regions-v1`. It defines present represented
flow regions and separate geometric seed attributes. It is not an attracting
basin, temporal stability, physical identity-persistence or completion detector.
The [schema](grc-9-v4-basin-interface-schema.json) gives closed wire shapes;
the cross-field and numerical requirements below are also mandatory.

## Explicit identity and schema successor

Historical v1 specialization/configuration/checkpoint payloads retain their
exact meaning and support limits. This policy must never be inferred for them.
The successor resolved specialization has schema
`grc9v4-resolved-specialization-v2`: exactly the v1 fields with this discriminator
and the additional `basin_policy` object defined by the schema. Its specialization
identity uses `grc9v4-specialization-identity-v2`, exactly the v1 fields with this
discriminator plus `basin_policy_id="grc9v4-terminal-flow-regions-v1"`.
`specialization_params_hash` covers the entire v2 resolved payload, including
`basin_policy`; `specialization_id` covers the entire v2 identity payload. Their
existing digest-prefix/JCS grammars remain unchanged.

The complete-model payload uses `grc9v4-complete-identity-v2`, retaining exactly
`grcv4_complete_profile_id` and `specialization_id` in addition to its discriminator.
Its existing `grc9v4-model-sha256:` grammar therefore yields an explicit new model
identity without changing generic profile physics or identity. The public
configuration successor likewise uses `grc9v4-configuration-v2`, replacing the
contained specialization/model identities with these v2 shapes; all other
configuration fields retain their prior meanings. A decoder must not reinterpret
v1 as v2. Migration is explicit, re-admits both histories and binds the new policy.

The observation and derived-label bundle is not authoritative C/W/Z or another
mutable owner. The existing lifecycle `basin_identity` field denotes the derived
partial assignment under this successor, never persistent physical basin identity.
Its scientific-state digest projection excludes the new diagnostics. A checkpoint
successor must distinguish `state_only` from `exact_observation` as specified below;
these modes cannot be guessed from a missing field in an older checkpoint.

## One fresh captured read

`P9-EC-GRC9-BASIN-INPUTS` requires one fresh poststate realization read for one
captured role. Read-only observation uses the captured publication; an operation
uses the reconstructed prospective target before sole publication. Current and
reset roles use their own C/W/Z and context. Rebase must not copy stale diagnostics
from another role. Consumed currents, predictors, old CI roots, and cached rows
are not valid substitutes. All fields consume this one capture; do not independently
re-solve to assemble flux, membership and seed attributes.

The closed `binding` object names role, role-state digest, exact profile/model,
graph/orientation, context contract/value, numerical policy, scalar backend,
evaluator/release, fresh stage, and applicable complete root/certificate binding.
For CI-like reads, a root binding must identify the joint selected point, including
geometry, rather than current alone. Optional read/certificate references are
explicit null when unavailable; they cannot assert a nonexistent certificate.

For current `role_state_digest`, hash the pre-existing
`GRC9V4NativeEventState.scientific_payload` projection: the generic scientific
preimage plus `active_model_identity` and `reset_digest`. For reset, hash its
pre-existing `reset_payload` projection. Both exclude `basin_attributes`, derived
`basin_identity`, the observation binding and its digests. The binding separately
names the reset read/context. Use the existing canonical SHA-256 record grammar.
These are content identities, not unique occurrence/epoch IDs.

The retrievable witness contains every stable edge, including zero-current edges,
with typed endpoints and represented current; every node's row gradient, signed
Hessian diagonal and row-net-flux vector; and resolved seed thresholds/sign.
All binary64 operands use finite, canonical `float.hex()` strings: decode and
re-encode identically, retaining the sign of zero. No rounded decimal summary or
digest-only witness can substitute. Edge IDs are nonempty strings and follow the
declared stable-edge order; row entries follow typed-node canonical order.

```text
operand_digest = SHA256(JCS(witness))
observation_digest = SHA256(JCS({
  schema_version: "grc9v4-basin-observation-v1", policy_id, binding, operand_digest
}))
```

An existing read identity may be cited only if it binds the full capture; this
does not remove the retrievable witness or its checks. Semantic derived fields
must be recomputed and compared, not trusted merely because the digests match.

## All-route membership and component evidence

`P9-EC-GRC9-BASIN-MEMBERSHIP` directs positive current tail→head and negative
current head→tail. Both signed zeros contribute no arc. Keep opposite parallel
flows distinct; do not aggregate before support extraction. No epsilon, clipping,
strongest-edge rule or label-based tie-breaking is permitted. Reject nonfinite
operands and incomplete/duplicate graph-edge coverage.

Compute every strongly connected component and its condensation DAG. For each
node retain its own component reference and all reachable terminal components.
Classify a terminal as recirculating for multiple members or a nonzero self-loop;
otherwise as a singleton sink if it has external incoming flow, or quiescent if
it has no nonzero incident flow. A node is assigned precisely when its reachable
terminal set is the singleton set containing a singleton sink. Multiple reachable
terminals give `ambiguous`; a unique other terminal gives `recirculating` or
`quiescent`. Those statuses have null assignment and are successful observations.

Retain nonterminal components as well as terminal ones, with `cyclic` and
`is_terminal`; nonterminal `terminal_kind` is null. A noncyclic node may reach a
recirculating terminal. A leaking upstream cycle may belong to an assigned region.
The component member sets partition the complete declared node set. The witness
row array and the per-node classification array each contain exactly one entry
per declared node. Assigned-region members partition exactly the nodes whose
`assigned_sink` and `basin_id` are non-null, not every declared node. Their
memberships, sink references, labels and seed subsets must agree with the
per-node records. The empty graph has empty collections. A single isolated node
has one quiescent component, one witness row and one classification record, with
no assigned regions; this is a valid observation. Do not manufacture a basin for
each isolated node. Assigned regions are disjoint and forward-closed in the frozen
directed graph; this does not prove temporal invariance or attraction. Zero flow
and exactly divergence-free closed represented currents have no assigned regions.

## Separate geometric seeds

`P9-EC-GRC9-BASIN-SEEDS` applies the fixed-row contract with the resolved sign:

$$
\sum_{a=1}^3 g_i[a]^2<\varepsilon_\nabla^2,
\qquad \min_a\widetilde H_i[a,a]>\varepsilon_H>0.
$$

Use exact squares of both represented coordinates and the represented gradient
threshold; do not pre-round underflowing/overflowing squares. Thresholds must be
finite and strictly positive. The signed diagonal must agree with the declared
row-Hessian/sign contract. Equality fails the strict comparisons. `seed` is present
for every node, even outside assigned regions; regions list their seed members.
Seeds do not alter assignments, require saturation, or change admission. The
diagnostic neither changes the hybrid spark test nor supplies child completion.

## Typed identity and deterministic representation

`P9-EC-GRC9-BASIN-IDENTITY` normalizes node IDs through the existing V4 node-ID
contract, then uses `{kind:"int",value:...}` or `{kind:"str",value:...}`. Integers
are safe integers; bool is not an integer ID. Integer zero and string zero are
different, and the empty string is valid. Do not stringify node IDs into JSON
object keys. Every node has an entry; null assignment is not an absent node.

Order typed IDs by integer before string, then unsigned lexicographic comparison
of canonical UTF-8 JSON bytes. Sort component members by that key; sort components
lexicographically by their member-key tuples, assigning zero-based component
references. Sort terminal references numerically and node/region entries by typed
node key (sink key for regions). Every node-ID array, including `region.members`
and `region.seed_members`, is sorted by the same typed-node key. `seed_members`
is the ordered subsequence of `members` whose corresponding node records have
`seed=true`. Public `basin_identity` entries preserve the per-node order after
filtering unassigned records. This order only canonically serializes evidence;
it must not select a flow destination. Reject duplicates, invalid references,
incomplete node/edge coverage, wrong order or inconsistent classification.

```text
basin_id = "grc9v4-flow-basin-sha256:" + SHA256(JCS({
  policy_id, graph_digest: binding.graph_digest, sink_node_id: typed_sink
}))
```

All assigned nodes in one region share that ID. Public `basin_identity` is the
partial map of non-null per-node assignments, serialized as typed entries.
Membership can change while a label remains equal; reappearance is not persistence.
Relabeling transports semantic members/references and recomputes IDs. Swapping
edge endpoints and reversing current signs preserves the directed support; changed
graph encodings may change hashes. Covariance under transported represented
operands does not certify a new finite-precision solve after coordinate reordering.

These labels supply no D4/D9 interspace identification. Any use to define causal
state, normalization, hierarchy, events or basin-indexed cross-state comparisons
must satisfy the applicable transport/accounting contract, even without direct
feedback into current. Equal hashes with changed membership cannot authorize
coordinate comparisons; an unrelated graph edit can change all labels without
physical basin birth. Reject unreviewed use as an authoritative admission, spark
or writer input. Do not emit an event for a diagnostic relabel.

## Lifecycle, snapshots and explicit replay modes

`P9-EC-GRC9-BASIN-LIFECYCLE` requires fresh reconstruction on construction,
observation, ordinary commit, assignment, expansion, migration, rebase, reset and
load. Both roles must be independently admitted when the operation promises both.
The sole publication occurs after the prospective diagnostic validates. A
classifier/read/serialization failure preserves the complete prestate, including
current, reset, context, profile/model, receipts and lifecycle identity. It cannot
publish stale labels, silently drop the capability, or return a success placeholder.

The versioned `grc9v4-basin-checkpoint-extension-v1` accompanies an explicitly
versioned successor checkpoint, never an implicit upgrade of a v1 checkpoint.
It has exactly `schema_version`, `policy_id`, `replay_mode`, `current_observation`
and `reset_observation`. The modes are:

- `state_only`: both observations are null. Restore and readmit the bound v2
  state, then produce a new observation under the explicit execution binding.
  No equality to an unretained observation is claimed.
- `exact_observation`: both observations are present with their witnesses.
  Reconstruct both roles under the same declared evaluation scope and require
  exact binding and operand identity, and exact recomputed derived collections.
  Mismatch rejects before publication. There is no fallback to `state_only`.

State-only mode is chosen when creating the snapshot, not after an exact replay
failure. Accuracy or a residual bound alone does not certify repeated signs near
zero. Existing certified rounding primitives do not prove determinism for an
entire realization read. Native conformance must name evaluator/release/backend/
numerical-policy scope and verify repeated fresh reads and both-role reset/load.
No cross-policy or cross-platform bitwise promise is made here.

Historical models/snapshots stay readable under their own schemas without added
semantics. Disabled GRC9V4 delegates the unchanged GRC9V3 observable/lifecycle
projection; omit the enabled-only bundle and do not reinterpret legacy basin IDs.

## Required native conformance and remaining boundary

`P9-EC-GRC9-BASIN-CEILING` retains the following forward checks for each selected
family. The present conditional graph checks do not discharge them.

| Obligation | Required discrimination |
| --- | --- |
| Freshness | Distinct C/W/Z live/reset states; current, complete joint root/geometry and row fields from one fresh read; reject stale predictor/consumed/old-root substitutions. |
| Graph/seed boundaries | Branch ambiguity, upstream/terminal cycles, loops, zero/subnormal opposing currents, typed IDs, strict seed equality and exact-square extremes. |
| Wire integrity | Duplicates, missing nodes/edges, malformed references, altered source bindings, recomputed hashes with inconsistent semantic fields and signed-zero loss. Complete component/row/node coverage versus partial assigned-region coverage; canonical region-member/seed-member order and filtered public-identity order. |
| Identity | Explicit v1→v2 migration; changed membership with equal sink label; graph/relabel/orientation transport; no implicit historical upgrade. |
| Lifecycle | Ordinary step, assignment, event/expansion, migration, rebase, reset/load; independently prepared histories and exact replay versus new-observation modes. |
| Atomicity | Both-role read/classifier failure, including reset-only failure and late validation failure, with whole-publication rollback. |
| Consumer ceiling | Successful ambiguity/quiescence/recirculation, no diagnostic events, no hidden writer/spark/normalization input or numeric abundance inference. |

No new runtime support, G2/G3 acceptance, full GRC9V4 conformance, completed sparks,
hierarchy or stable-attractor semantics follow from this specification. The design
debt is resolved; P9-10.1a native work and P9-10.1c support reconciliation remain open.
