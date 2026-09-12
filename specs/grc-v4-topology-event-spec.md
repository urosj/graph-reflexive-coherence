# GRCV4 topology-event fallback and representation-transport contracts

Status: **contract extension accepted by the user on 2026-09-12; not a released
or implemented event capability**. Acceptance covers the fallback binding and
the separately scoped representation-transport operation contract. Its pending
wire binding and both runtime workstreams remain explicit below. P9-7.2a is
unchanged; aggregate P9-7.2b execution and closure remain open.

## Authority and scope

This additive V4 binding specializes the already permitted fallback in
[proposal §12.7][proposal] and [paper §12.7][paper]. It reuses the
[accepted A reference-pass producer][initializer] without changing its static
policy, numerical staging, recipe domain or construction/pair identities.
The [source crosswalk and forward checks][review] distinguish accepted source
authority from this new wire binding and from future runtime evidence.

The scope is caller-mapped generic events across the ten A/C ×
OS/CI/RG2b/PC/CI+PC families, subject to each complete target's admission.
This is a finite policy definition, not evidence that every ordered pair or
arbitrary graph is executable. Candidate and persistence are separate axes:
only PC and CI+PC have a Z carrier. Pure representation transport is now a
separate current contract workstream below. No topology-changing preserving W
lineage or carrier map,
GRC9 expansion, new constitutive formula, native release, ordinary beat,
G2/G3 widening or alteration of same-graph migration is included.

This is one **explicitly selected history-reconstruction policy**, not the
universal or default meaning of topology continuation. Execute the declared
admitted transport, or the declared admitted reconstruction/loss policy;
otherwise reject. A future admitted transport can make independent choices
for W and Z. Do not attempt preservation and silently reset on failure.

Pure graph relabeling, edge reordering and edge-coordinate reorientation are
representation changes, not this lossy event. Use their declared, validated
typed coordinate action or reject them as unsupported; never route them here
silently. Graph isomorphism or equality alone does not establish the operation
or its correspondence. Conversely, an explicitly requested reconstruction may
have an identity resource/topology map: replacing W/Z still changes active
history and must not be optimized away. An experiment using this policy
combines its topology/resource intervention with the declared history removal;
its effects cannot be attributed to topology alone.

## Pure representation transport: current contract scope

**Included now as a separate operation contract; closed payload/release binding,
runtime implementation and executable covariance verification remain pending.**
This is the declared coordinate action already required by paper §2.1.5 and
the representation-covariance contract, not a new topology-changing law.
It must not be implemented by the lossy fallback request or receipt policy.

The caller must declare complete bijections of source/target vertices and
edges and an orientation sign for each matched edge. Validate uniqueness,
coverage, endpoint correspondence and graph attributes, including loops and
parallel-edge identities. Incidence equality alone cannot distinguish every
loop or parallel-edge correspondence; neither matching names nor an inferred
isomorphism is sufficient authority.

For vertex permutation P and signed edge permutation U, require and apply
independently to current and reset:

$$
B^+=PB^-U^\top,\qquad
C_r^+=PC_r^-,\qquad
W_{A,r}^+=|U|W_{A,r}^-,\qquad
Z_r^+=UZ_r^-U^\top.
$$

Apply W only to A and Z only to persistent realizations; absent channels stay
absent. Positive scalar W is permuted, not sign-flipped. Signed permutation
congruence preserves symmetry, the Frobenius norm and graph-isomorphic star
support of Z. Use indexing/sign changes, not dense interpolation; preserve
binary64 values except required canonicalization of signed zero. No new W/Z
coordinate is initialized or dropped, and neither history channel reports
loss. There is no initializer pair, resource increment, charge-target change,
ordinary beat, physical current reversal or candidate/realization migration.

Transport references, pairings, context coordinates, backend inputs, structural
operators and complete profile declarations consistently with their declared
types. Candidate C's fixed scalar edge reference map is permuted without sign
changes, and its derived surfaces are reconstructed, not relabeled as retained
history. Require the actual target recipe/domain to support the action; opaque
or unsupported backend/chart transformations reject. This scope is graph
relabeling/reordering/reorientation, not arbitrary changes of spatial frame.
Readmit both whole target states before atomic publication; failed declaration,
target admission or publication leaves the entire lifecycle unchanged.

The represented scientific state is unchanged under the declared coordinate
correspondence. Do not confuse this with equality of coordinate-sensitive
serialized bytes or hashes. The separate wire contract must bind the complete
correspondence and both endpoint/reference identities, preserve old evidence
identities, and verify equivalence through the admitted action. It must define
request, receipt, archive/replay and release dispatch without retroactively
changing existing scientific-state IDs or treating a fallback receipt as proof
of coordinate equivalence.

P9-7.2b now tracks this operation separately from reconstruction. Before claiming
support, complete that wire binding and test inverse/round-trip transport,
signed edge permutations (including loops/parallel edges), distinct current/
reset histories, no initializer/loss, target covariance/admission, rollback and
snapshot/restore/reset. The existing fallback schema/vectors do not cover this
operation, and passing their checks does not close representation transport.

## Future improvement: independently admitted history transport

**Genuine topology-changing history transport remains deferred; it is not a
condition for closing the two current P9-7.2b operation workstreams.** The next
bounded candidate is addition of a disconnected zero-resource vertex with
explicit identity lineage for existing edges and retained W/Z. That candidate
still needs a contract for target references, the new vertex/backend inputs,
structural domain, admission and replay. It is not admitted merely because
old edge arrays have unchanged lengths or names, and is not implemented here.

More general topology transport needs separately admitted edge-history maps
$\mathcal M_{W,\mathrm{evt}}$ and/or carrier maps $L_{K4,\mathrm{evt}}$.
Each must bind source/target identities and coordinates, units, covariance,
split/merge semantics, bounds, target compatibility and the reset-state map.
W must retain its positive diagonal edge-mobility type; Z must retain its
declared structural type, star support and norm/domain, with induced geometry
readmitted separately. Initialized new coordinates or losses require explicit
semantics and receipts. Transport need not be injective or lossless.

The resource map alone cannot determine either history map. Even a compatible
flux equation $B^+L=T_CB^-$ leaves cycle-space freedom in L. Arbitrary mixing
can make $L\operatorname{Diag}(W)L^\top$ dense, outside A's diagonal mobility
type; a carrier congruence additionally needs the declared pairings, adjoint,
orientation action and target-domain bounds. Edge-name matching, interpolation,
pseudoinverses and “preserve as much as possible” do not supply this authority.

A future event may therefore transport W while resetting Z, or transport an
admitted Z while initializing W. Select each channel's admitted policy before
construction, then readmit the whole target atomically for current and reset.
Execute the declared transport or declared reconstruction; otherwise reject.
Never switch to loss/reset after preservation fails. This improvement needs
its own bounded contract, release and execution evidence; no new policy IDs,
dispatch paths, preserving-map support or G2/G3 claims are granted here.

## Resource map and construction order

Reuse the closed `grcv4-mapped-topology-event-request-v1` request. The
[extension schema](grc-v4-topology-event-schema.json) restricts its two history
channels to the fallback below; no output, supplied W/flux, edge interpolation
or untyped resize is a request input. Policy is fixed before construction.
Reject a declaration that does not match the actual source/target candidates,
persistence, source history digests or initializer requirement. Never select
a reset policy only after a preserving policy failed admission.

Authenticate the source scientific/reset state, graph and complete target
reference/backend preimages before using them. Resource-transform vertex
orders must equal the respective graph orders, with exactly m×n finite
nonnegative coefficients and m finite increments. This initial recipe retains
the accepted unit-vertex, closed-no-flux boundary; each matrix column sums to
exactly one. Arbitrary quadrature is not newly admitted.

For each role r in {current, reset}, independently form

$$
C_r^+ = T_{C,\mathrm{evt}} C_r^- + \Delta C_{\mathrm{evt}}.
$$

Use the existing event arithmetic: interpret binary64 inputs exactly, sum
each entire affine component exactly, then round it once to binary64. Reject
nonfinite or negative target components. Compute the actual charge change
from the rounded target and source, not merely the sum of declared increments.
The receipt delta and updated Q target must be representable without hiding
a nonzero change. Both resulting states must satisfy the same updated charge
target; a reset-only mismatch rejects the whole event. The scalar receipt is
not a substitute for the full map. Clock and step index do not advance.

After mapping both resource states, construct W/Z according to the fixed
channels below, rebuild derived surfaces and readmit both complete targets.
For A, invoke the accepted producer twice on the respective **mapped** target
C, target graph/profile/context and fixed target differential reference.
Equal operands still require separate role-bound invocations. Source W/Z,
source flux and solver caches are not initializer inputs. This is not a
verbatim reuse of same-graph migration, which leaves C unchanged.

## Candidate history channel

Each source digest below covers the actual source current **and reset**
channel in declared graph coordinates, using the existing history-content
identity. Present history is not declared absent merely because values are
zero or initialized values happen to equal source values.

| Source → target | `policy_id` | `disposition` | Source digest | `target_initializer_id` | `information_loss` |
| --- | --- | --- | --- | --- | --- |
| C → C | `candidate_c_rederive_no_history_v1` | `rederived` | null | null | `none` |
| C → A | `candidate_a_target_reference_pass_initialization_log_history_v1` | `target_initializer` | null | `grcv4-a-target-reference-pass-v1` | `none` |
| A → C | `archive_drop_candidate_history_v1` | `explicit_loss` | required | null | `candidate_history_loss` |
| A → A | `candidate_a_event_loss_reference_pass_v1` | `explicit_loss` | required | `grcv4-a-target-reference-pass-v1` | `candidate_history_loss` |

For A→A, `explicit_loss` describes source history disposition; the non-null
initializer ID specifies production of the replacement complete target W.
It is not identity transport, even for matching edge names or unchanged
policy labels. Both A-target rows require the existing target profile's
reference-pass lifecycle history policy. The event's A→A loss-policy ID does
not replace that profile field or alter the initializer static policy.

C targets have W_A absent and no initializer pair. Supply their exact complete
target W_C,tr stable-edge reference map before reconstruction. Reject missing,
extra, duplicate, unmatched, nonpositive or nonfinite entries; rederive the
selector, sector, Hodge, baseline current, Read-Back and geometry. Do not carry
source-derived arrays as history.

## Carrier history channel

P means PC or CI+PC; NP means OS, CI or RG2b, for either candidate.

| Source → target | `policy_id` | `disposition` | Source digest | `target_initializer_id` | `information_loss` |
| --- | --- | --- | --- | --- | --- |
| NP → NP | `no_persistent_carrier_v1` | `not_applicable` | null | null | `none` |
| NP → P | `canonical_zero_carrier_initialization_v1` | `target_initializer` | null | `canonical_zero_carrier_v1` | `none` |
| P → NP | `archive_drop_carrier_history_v1` | `explicit_loss` | required | null | `carrier_history_loss` |
| P → P | `event_loss_and_zero_target_carrier_v1` | `whole_carrier_reset` | required | `canonical_zero_carrier_v1` | `carrier_history_loss` |

For each persistent target, initialize the **entire** target carrier to zero
in its target K4 coordinates (the current dense implementation has m² entries
for m target edges). Validate carrier dimensions, symmetry, star support and
the declared norm/domain; signed carrier entries are permitted. Independently
validate the induced geometry's positivity, conditioning and candidate/
realization admission. Positivity is not imposed on each Z entry or on Z as
a positive-definite matrix. NP targets have Z absent, not an empty or zero array.
The P→P rule applies even for the same candidate or matching names: this
selected fallback has no admitted carrier map. It does not change 7.2a's
exact-contract preservation rule or its rejection on contract mismatch.

Loss means loss of active history continuation, not destruction of the
inspectable source archive. C→A is candidate-loss-free, but can incur carrier
loss. Fresh NP→P zero initialization loses no carrier history. These labels
make no injectivity or information-preservation claim about the resource map.

## Event, receipt and archive identities

Keep the existing mapped-event identity preimage and resource/history digest
domains: source state and graph, target graph and complete profile, full
resource transform and selected history bundle. Operation ID and diagnostic
metadata do not enter event identity. The target profile/reference binds the
initializer recipes before any output exists; no circular output/profile ID
is introduced. Different output evidence changes receipt/commit identity.

New fallback events use `grcv4-topology-event-receipt-v2`, with exactly
`schema_version`, `core`, `event_id`, `history`, `initializer_pair_id`.
The last field is the existing pair identity for an A target and null for a
C target. This explicit version is used for all new fallback events, not
only A targets. Keep `grc-receipt-sha256:` over the complete JCS payload.

The core binds all source/target graph, profile, authoritative, scientific and
reset identities, actual charge delta, resource/history preimages and the
existing successful-primary parent policy. Its ordered loss tuple is exactly
the union of the two channel losses (candidate before carrier), without
duplicates. Each channel receipt matches the selected declaration and binds
the actual source/target current-plus-reset history digest; absence is null.
Initializer ID is an algorithm; pair ID is output evidence; neither substitutes
for the target history-content digest. Keep separate charge/history receipts
consistent with the primary receipt and publish them in the same commit.

Snapshot layout `pygrc-generic-topology-event-snapshot-v1` has the same closed
top-level fields and transition-row fields as the initializer migration
layout. The difference is explicitly versioned applicability: an event row
now carries a non-null `initializer_pair` for either A-target fallback;
C-target events carry null. Migration rows retain their accepted C→A-only
pair rule, not an event reinterpretation. No new scientific state coordinate,
global proof registry or ambient filesystem dependency is introduced.

Preserve prior migration and C_OS event receipts/archives byte-for-byte at
their original identities. The new layout can contain these prior rows, whose
own receipt versions and policies determine their historical semantics.
Legacy C_OS event rows use null pairs and their original admitted policy
aliases. A v1 event receipt cannot certify a new A initializer or be silently
upgraded to v2. Existing layouts do not acquire event-pair support.

The legacy request branch is limited to candidate aliases
`candidate_c_no_independent_history_v1` and
`candidate_c_rederive_no_history_v1`, and carrier aliases
`no_persistent_carrier_v1` and `carrier_not_applicable_v1`. Semantic replay
must additionally resolve both endpoints as the admitted historical C_OS
scope, check the alias against their actual historical lifecycle policies,
and match that row to its original v1 event receipt. An overlapping request
shape does not select a historical version. New fallback events require v2;
legacy-only aliases do not become new fallback policies. Other historical
aliases require separately established applicability, not acceptance of an
arbitrary string with the right disposition.

## Replay, admission and atomicity

Restore every archived source/target reference and required backend from
bound preimages. Recompute the resource maps for both roles, both initializer
invocations and every retained intermediate, final W/Z and whole-target
admission. Match pair roles, target profile/reference/backend, mapped C,
initialized W, receipt pair ID, all endpoint/history/charge identities and
the commit link. Rehashing forged output evidence must not authenticate it.
For legacy rows, enforce their original semantics instead.

Replay reconstructs and verifies the archived crossing against its declared
inputs, policy, numerical recipe and admission contract. It does not
independently establish that an externally supplied historical execution
occurred. It must not require later ordinarily evolved W/Z to equal the
initializer or zero seed. Preserve F1/F2
known-identity, archived endpoint, repeated-state and lawful unreceipted
assignment checks. Hashes do not attest unobserved external history.

Use existing OS, CI, PC, CI+PC and RG2b numerical owners for final admission.
RG2b state/section admission is not a next-beat entry certificate. Do not
recenter fixed charts, enlarge domains, repair output or switch target/policy.
Validate source and both targets before publishing any authority, reference,
backend, archive, receipt, ledger or commit update. Typed map/declaration,
construction/range and admission failures retain their actual stage;
unexpected programmer exceptions propagate. Reset-only and late-publication
failures roll back the complete lifecycle, not just visible resources.

## Release and verification boundary

Neither the base release nor the accepted initializer release
`grcv4-spec-release-sha256:e44dcd77a78a752c0e62f559243b88faff0bf90af1ee11a587f25d27e8a8abc7`
admits this new receipt/layout. A separately identified release
must bind this spec/schema/vectors, their source crosswalk, inherited schema
bytes and unchanged initializer static-policy digest. Codec dispatch must
explicitly admit the release/layout/receipt combination before execution.
Unknown hash-shaped releases still reject. Do not modify old manifests,
packaged assets, accepted run hashes, or the old layout's null-pair rule.

[Wire vectors](grc-v4-topology-event-vectors.json) and their focused checker
test closed shapes, policy cases, role/pair linkage and canonical identities.
They use synthetic endpoints and do **not** certify arithmetic, producer
execution, target admission, rollback or portability of a numerical run.
Required runtime follow-through is enumerated in the [review][review].
No P9-7.2b or tranche acceptance follows from passing these contract checks.

[proposal]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#127-typed-topology-events-and-whole-lifecycle-continuation
[paper]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#127-typed-topology-events-and-whole-lifecycle-continuation
[initializer]: grc-v4-a-initializer-spec.md
[review]: ../implementation/phase-9-grcv4/tranche-7/P9-7.2b-ContractExtension.md
