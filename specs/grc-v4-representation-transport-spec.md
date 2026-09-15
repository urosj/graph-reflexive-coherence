# GRCV4 pure representation-transport wire contract

This completes the separately scoped coordinate-operation binding authorized
after [P9-7.2b contract acceptance][review]. It is a contract/package, **not
runtime representation transport, executable covariance or P9-7.2b closure**.
The coordinate law and boundaries in the [parent specification][parent] apply
unchanged. The lossy fallback is a different explicitly selected operation.

## Correspondence, declaration and identity

Policy `grcv4-pure-representation-transport-v1` permits only complete graph
relabeling, edge reordering and edge-coordinate reorientation. No vertex/edge
addition, deletion, split, merge, resource increment, candidate/realization
change, W initializer, carrier reset, ordinary writer or clock advance occurs.

The [closed schema](grc-v4-representation-transport-schema.json) uses the same
I-JSON/JCS requirements as its pinned base/initializer/event schemas. Reject
duplicate JSON keys, unsafe integers, nonfinite numbers, negative zero,
coercions, unknown versions, extra fields and malformed identity suffixes.

| Definition | Fields | Identity prefix |
| --- | --- | --- |
| `correspondence_payload` | `schema_version`, `policy_id`, `source_graph_digest`, `target_graph_digest`, `vertex_map`, `edge_map` | `grcv4-coordinate-map-sha256:` |
| `correspondence_record` | `correspondence_id`, `payload` | ID is recomputed from payload |
| `request` | `schema_version`, `operation_id`, `source_state_digest`, `source_graph_digest`, `target_graph`, `target_profile_id`, `correspondence`, `metadata` | No request-output identity cycle |
| `operation_identity_payload` | `schema_version`, `policy_id`, `source_state_digest`, `source_graph_digest`, `target_graph_digest`, `target_profile_id`, `correspondence_id` | `grcv4-representation-change-sha256:` |
| `receipt_payload` | `schema_version`, `core`, `representation_id`, `correspondence_id`, `history`, `charge` | `grc-receipt-sha256:` |
| `operation_group` | `commit_record`, `receipts` (exactly one representation envelope) | Existing receipt and commit identity domains |

Each vertex-map row is exactly `{source_vertex_id, target_vertex_id}`; each
edge-map row is exactly `{source_edge_id, target_edge_id, orientation}` with
orientation the integer +1 or -1. Rows follow **source** live vertex/edge order.
Targets cover their live identities exactly once, but may occur in any target
order. Integer and string vertex IDs are distinct. Edge IDs are nonempty strings.
No matrix of arbitrary coefficients, inferred sorting or partial map is accepted.

Check the exact source/target serialized graph hashes, unique IDs and endpoint
membership. For each edge, mapped source endpoints must equal target endpoints
in the declared orientation. Loops still require explicit edge identity and
sign; parallel edges remain distinct. Incidence equality alone is insufficient.
The closed generic graph currently carries only vertices and oriented edges;
any future graph attributes need a separately defined transport, not silent loss.

The source-state digest includes its existing reset commitment. Target profile
and the fixed reference/backend preimages must resolve before construction.
The operation identity excludes operation ID and diagnostic metadata, but binds
the full correspondence through its ID. Successful receipts additionally bind
the actual outputs. No initializer pair or equivalence-invariant replacement
for the existing scientific-state hash is introduced.

## Typed action and endpoint coherence

Independently map current and reset by the declared P and signed permutation U:

$$
C_r^+=PC_r^-,\qquad W_{A,r}^+=|U|W_{A,r}^-,\qquad
Z_r^+=UZ_r^-U^\top,\qquad B^+=PB^-U^\top.
$$

Use index/sign operations with canonical positive zero for zero outputs.
W and Z are absent where the source candidate/realization has no such channel;
presence cannot change. Preserve charge target, time and step index. Permuted
resource accumulation must still pass the existing target charge admission;
do not repair C or change Q to accommodate a rounding failure.

The target complete profile has the same candidate and realization and the
same physical parameters, recipes and domains under the declared action.
Coordinate-bound profile/reference hashes may change and must recompute.
Map fixed scalar edge references without sign, vertex data by P and edge
operators by their typed signed action. Structural-star coordinates follow
the induced vertex/star-edge correspondence, not a guessed tensor resize.
Host-frame differential positions and weights follow the declared node/edge
maps; this is not a new spatial rotation backend. Target chart/support and
context transformation must be explicitly supported by the corresponding
recipe. Reject unresolved or opaque transformations and incompatible targets.

Reconstruct derived C sector/Hodge/baseline/current and A/realization surfaces
through their existing owners; caches do not become retained authority.
Readmit both complete targets and verify the typed endpoint action before
one atomic publication. No target substitution, chart enlargement, initializer
or fallback after failed transport is permitted.

## Receipts and snapshot dispatch

`grcv4-representation-transport-receipt-v1` has its own closed core: the existing
receipt core **except** `resource_transform_digest` and `history_bundle_digest`.
The payload's `correspondence_id` replaces neither field under an old receipt
version; it is the explicitly versioned coordinate-map binding. All other core
endpoint, graph, model, authority, reset, operation and parent fields remain.
Require zero actual charge delta and an empty loss tuple.

### Charge meaning and evidence (R1)

**For this representation receipt version only**, `actual_charge_delta = 0`
denotes the exact charge-preserving typed coordinate action. The existing
ordered balanced binary64 reductions of source and target resources may
differ. Their difference is not external resource exchange, does not change
Q, and must not be reported as exact numerical equality. This does not change
the reduced-charge meaning of older receipts or the reconstruction contract.

The required closed `charge` object has `schema_version =
grcv4-representation-charge-evidence-v1`, `delta_semantics =
exact_coordinate_action`, and `current` and `reset` records. Each role has
`source` and `target` evaluations, each exactly `{target_charge,
admitted_charge, residual}` using the existing charge owner's meanings:
`admitted_charge` is the ordered tree result and `residual` is the signed
actual-minus-target difference rounded once to binary64. All four evaluations
use the unchanged Q target and their resolved endpoint charge policies. Runtime
publication/replay must recompute them from the archived resources, require
all four admissions, and bind them into the primary receipt identity. Schema
admission alone does not establish these numerical facts.

For example, with e = 2^-53, the coordinate permutation from `(1,e,e)` to
`(e,e,1)` preserves the exact sum but changes the tree result from 1 to
1 + 2^-52. At Q = 1 and absolute tolerance 2^-52 (relative tolerance zero),
both charge checks pass and the representation delta is still zero; at zero
tolerance the target rejects. Do not sort, repair C, adjust Q, insert a hidden
remainder or add a numerical-equality admission condition. Wire negative zero
rejects; computed zero outputs are canonical positive zero.

### Complete successful operation group (R2)

One successful representation operation emits **exactly one receipt**: its
`grcv4-representation-transport-receipt-v1` primary in the existing successful
envelope shape. Its embedded `charge` supplies the operation's charge evidence;
its embedded `history` supplies both history-channel dispositions. No separate
legacy charge/history auxiliaries are emitted. The complete ordered commit
`emitted_receipt_ids` is `[primary_receipt_id]`; the receipt ID hashes the full
primary, the commit ID hashes the existing commit payload, and the envelope's
backlink equals that commit ID. Commit operation/source/target fields equal
the primary core and target clock/index are unchanged from the source.

This successor explicitly adds representation transport to the successful
primary kinds under `grcv4-previous-successful-primary-v1`. Its parent list
is empty only for the first operation, otherwise exactly the preceding
successful primary ID. It advances the head even for an identity coordinate
map or zero-duration operation. The next successful operation parents this
primary. Failure emits no successful group and does not advance the head.
The complete ordered groups still partition the ledger without duplication,
omission or prefix rewriting. Mixed archives apply this singleton rule only
to representation operations; old operation groups retain their own rules.

`operation_group` provides the closed commit-plus-emitted-envelopes wire
fixture. The package group checker verifies its IDs, links and the supplied
previous-head declaration; full ledger partition and numerical/source-state
admission remain lifecycle responsibilities. Do not fabricate resource/history
map hashes or weaken old cores to reuse their auxiliaries.

Candidate A history receipts use `exact_transport` with both source/target
current-plus-reset history digests. Candidate C uses `rederived` and null
history digests. Persistent carriers use `exact_transport` with both digests;
nonpersistent carriers use `not_applicable` with null digests. Every channel
has `information_loss = none`. Equal history-content digests are neither
required nor sufficient for coordinate equivalence.

Layout `pygrc-generic-coordinate-transport-snapshot-v1` retains all top-level
fields of the event snapshot, extending only the versioned request/receipt
unions. A representation transition has exactly `commit_id`, `request`,
`source`, `source_reset`, `target`, `target_reset`, `initializer_pair`; the last
field **must be null**. The request retains the correspondence preimage.
Archived source/target references and differential recipes are recovered from
the existing registries; no new global map registry or hidden state is added.

The layout also admits the already defined migration and fallback transition
shapes. Their pair and loss rules remain operation-specific: C→A migration and
A-target fallback need their respective pair; preserving A→A migration,
C-target events, legacy C_OS events and representation transport do not gain
one. Historical rows retain original receipt IDs and policies. New operations
cannot acquire legacy semantics merely through a matching shape.

Replay verifies map/operation/receipt/commit identities, registry resolution,
source and reset commitments, the exact typed coordinate action, both final
admissions and history digests. It checks the archived crossing, not equality
between historical transformed outputs and later ordinarily evolved state.
F1 programmer-versus-domain failures and F2 repeated/known-state consistency
remain unchanged. Verification does not attest an unobserved historical run.

## Joint package and remaining runtime work

The additive [joint release](grc-v4-event-contract-release.json) binds the
fallback and representation schemas, vectors, controlling documents and
unchanged initializer static-policy digest. It admits both new layout shapes
through an explicit package decoder; the predecessor codecs retain their
original behavior. Old releases and arbitrary hash-shaped IDs cannot select
the new schemas. The release hash is **not** embedded in its own schema.
Missing, altered or mismatched packaged assets reject before wire validation.

The package decoder is an explicit wire/declaration entry point, not a new
`GRCV4` lifecycle dispatcher. Existing model restoration must continue to reject
these unimplemented layouts. Runtime integration must add operation-specific
admission, mixed-version replay, publication and failure handling; package
availability alone cannot advertise model capability or grant G2/G3 support.

Focused contract tests cover bijection/order/endpoint/sign pressure, canonical
identities, both operation families, mixed-version wire archives, missing and
altered assets, unknown releases and predecessor rejection. They are not
actual transport, target solver, rollback, reset or covariance executions.
Those tests remain required before runtime acceptance. General topology-history
maps, including the isolated-vertex candidate, remain deferred.

Runtime acceptance must additionally distinguish scientific inverse transport
from ledger rollback: with no intervening scientific operation, a map and its
inverse recover current/reset C/W/Z and reference/profile preimages, but retain
two successful groups and a changed lifecycle digest. Compare identity
representation against explicit identity reconstruction with nontrivial A and
persistent histories: only the latter initializes/resets and records losses.
Exercise preserving migration → representation → ordinary evolution → lossy
event → restore/reset, retaining historical pair rules and receipt identities
without forcing evolved W/Z to equal old initializer outputs. Include the
charge-order witness, signed-zero controls and incompatible target reference,
backend, context and chart rejection, not just graph correspondence examples.

[parent]: grc-v4-topology-event-spec.md#pure-representation-transport-current-contract-scope
[review]: ../implementation/phase-9-grcv4/tranche-7/P9-7.2b-ContractExtension.md
