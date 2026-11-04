# Phase 9 GRCV4 handoff — bounded support recorded, G4 pending

Updated 2026-11-04 on `main`, after no-ff merge `e65dd3c3`.
P9-10.5 acceptance is `33eecf24`; P9-10.6 recording is committed as `80f267aa`.
The accepted P9-10.6 disposition records final bounded support;
**G4 remains a separate decision and Phase 9 is not declared closed.**

## Current state

[Release disposition](./phase-9-grcv4/tranche-10/P9-10.6-ReleaseDisposition.md)
and its [machine record](./phase-9-grcv4/tranche-10/P9-10.6-ReleaseDisposition.json)
are the current support index. All ten families have their declared generic,
nine-port, lifecycle, basin, conservation and optional native spark evidence.
Each surface retains its exact identities and domains; family labels alone
confer no support. There are no pending families within these bounded scopes.

- Tranches 8–9: [all-ten acceptance](./phase-9-grcv4/tranche-9/P9-Tranches8-9-AllTenAcceptance.json), including forty source-model compatibility cells.
- P9-9.1a.6: all nine extensions after C_OS accepted; the parent is checked.
- P9-9.1a.7: [accepted native support reconciliation](./phase-9-grcv4/tranche-9/P9-9.1a.7-Support.json), twenty exact source/target declarations; bounded P9-9.1a closed.
- P9-10.1–10.2: accepted first-four and six subsequent family records, indexed by the release record; exact expanded-target identities remain distinct.
- P9-10.3/10.4: ordinary and native-spark integration/examples accepted; no additional campaign required for publication.
- P9-10.5: [accepted reconciliation](./phase-9-grcv4/tranche-10/P9-10.5-NativeSpark-Acceptance.json); thirty native portions discharged, four explicit hierarchy splits, fourteen spark debt transformations, 29 unchanged inherited D10 transformations.
- P9-10.6: support/acceptance disposition and handoff recorded. P9-G4 remains unchecked and unaccepted.

The [native ledger](./investigations/grc9v4-constitutive-design/evidence/spark-completion/native/ClaimDebtLedger.json)
preserves original scientific claims and links exact accepted native evidence.
Its review-time pending fields are historical; the separate P9-10.5 acceptance
supplies the current decision. The same rule applies to older source snapshots.

## Next decision and limits

**G4 is pending and waiting at the user's request while they work on topology
change.** It is not the active task. A future, separately requested G4 review
would assess the advertised bounded support, accepted evidence, legacy
boundaries and residual routing. This tracking cleanup changes no ATC result,
claim/debt status or implementation authorization.
Do not automatically commit, merge, launch campaigns, develop hierarchy or
expand the supported population from this handoff.

`SC-VO-HIERARCHY-EVOLUTION` remains deferred: atomic new-child insertion and
local occurrence accounting are implemented, broader hierarchy evolution is
not. General ATC, arbitrary graph/parameter conformance, numeric abundance,
distributed exactly-once and full GRC9V4 conformance are not granted. Retain
CI resolution/root limits, pointwise carrier margins, RG2b C1 limitations,
original excluded cases and unexecuted large diagnostics.

## Using and inspecting the work

Start with [ordinary examples](../examples/grc9v4/README.md) and the
[native completed-spark workflow](../examples/grc9v4/native_spark.md).
Inspection, preparation, numerical execution and replay are explicit modes.
The side-tool browser and notebook include current support, workflow and debt
views plus the final release record. `/api/phase9/release` authenticates the
record without executing a numerical campaign.

```bash
.venv/bin/python implementation/phase-9-grcv4/verification/p9106_release.py
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python -m unittest test_p9106_release -v
PYTHONPATH=src .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

Use `.venv`. Before handing off or committing Phase 9 source/planning edits,
run the final current-tree boundary audit after refreshing only authorized
bindings. It verifies the current boundary, not new native numerical execution.
Missing ignored generated reports on a fresh clone do not revoke acceptance;
regenerate only what the intended check needs. Do not rerun long accepted
trajectories merely to accept, commit or update documentation.

## Evidence and working agreements

Accepted source/target campaigns, full cold replay, exact states, receipts and
certificates remain in the repository. Compact archives authenticate retained
objects; omitted diagnostics require explicit reconstruction and exact hash
agreement. A new run is new evidence, not a replacement for the original run.
Use repository-relative paths. Compress new evidence over 1 MB; any retained
blob over 10,000,000 bytes additionally needs the existing bounded storage review.
Do not retain bulk failed sessions without informative scientific content.

The goal is coherence across claims, paper, specs and code, with exact validation
and reproducibility. Preserve older versions and accepted authority. Scientific
changes follow investigation → proposal/paper → specs → native implementation.
A commit request is acceptance; record successor decisions without rewriting
accepted execution records. Choose focused checks for actual changes and run
independent jobs in parallel when useful (up to twelve on the current machine).

The previous accumulating handoff is available in Git at `33eecf24` under this
same path. Its dated next-step instructions are historical, not active work.
Detailed scientific findings and execution evidence remain in their original
linked artifacts; this concise handoff replaces the obsolete continuation queue.

## Historical checkpoint references

The following accepted mechanics notes are retained because the plan/checklist
link to their exact subjects and findings. Their dated next-step instructions
are historical and are superseded by the current disposition above.

## P9-8.1 shared mechanics parent acceptance

2026-10-02: the user explicitly accepts P9-8.1 as a whole and requests merging
its development branch into `main`: "we now have P9-8.1 done, so accept it,
and merge branch into main". The accepted implementation subject is
`c27583cc476b0c4cbdd63d3428d611b423389f04` on
`work/p9-8-1-shared-mechanics`, descended from `main` at `7ba0f61`.

| Completed child | Accepted checkpoint |
| --- | --- |
| P9-8.1a — fixed chart, admitted port graph, envelope and projection | `75a6629` |
| P9-8.1b — row differential and V4 weight bridge | `7f33a42` |
| P9-8.1c — baseline mechanical candidate trigger | `e9dfad7` |
| P9-8.1d — exact column coarse-graining and Split | `a2d3d36` |
| P9-8.1e — exact-backend correction and bounded P9-8.0 audit | `c27583c` |

The `.e` subject includes the final shared runtime correction across `.b`–`.d`.
Its recorded validation comprises 173 regression/backend methods, 14 nested
P9-8.0 probe executions across Python and FLINT, static checks and the current
phase-boundary audit. The child reviews below retain the detailed pressure
evidence and exact subjects. This parent acceptance closes P9-8.1; the
acceptance-only documentation update preserves those runtime bytes and evidence.

P9-8.2 allocator work, profile-specific native integration, later lifecycle
and conformance gates, and the end-of-Tranche-8 performance/cache review keep
their existing scope. P9-8.0's R1–R10 restrictions remain in force.

## P9-8.1a.1 chart and endpoint implementation

2026-10-02, branch `work/p9-8-1-shared-mechanics`, baseline `7ba0f61`.
[Native primitives](../src/pygrc/models/grc_9_v4_topology.py) implement the exact
nine-port chart, immutable row/column partitions and frozen, slotted endpoints.
[Tests](../tests/models/test_grc_9_v4_topology.py) use a literal nine-pair oracle,
distinct row/column partitions and adversarial inputs. This increment implements
only local chart/endpoint values: graph admission, envelope/projection and
integrated review remain `.2`–`.4`.

Ports and row/column coordinates are one-based JSON integers. Integral-valued
Python floats normalize to integers without rounding fractional values; adjacent
floats, bool/string/coercible values, nonfinite numbers and values outside the
chart reject. Endpoint node identity follows the existing generic graph helper:
safe integer normalization, distinct `1` and `"1"`, UTF-8 strings without Unicode
normalization, and rejection of invalid/coercible/unsafe identities. Endpoint
construction does not check graph membership, occupancy or event eligibility.

The user's 2026-10-02 review reports no defect in the numeric/type admission
surface and identifies three obligations for later graph work. Reviewing the
[port-graph contract](../specs/grc-9-v4-spec.md#port-graph) and
[schema](../specs/grc-v4-contract-schema.json) gives these dispositions:

- Empty-string node IDs remain admitted, as in the generic graph and frozen
  schema; only edge IDs carry a nonempty-string requirement. `.2` must cover
  both a live `""` node and a dangling endpoint naming `""`.
- Endpoint equality is sound for the exact normalized fields currently
  admitted. The class docstring now records that invariant and requires
  reassessment if field types change. `.2` retains typed membership/occupancy;
  `.3` uses canonical payload bytes/digests for graph identity.
- Local endpoint construction establishes no graph membership or occupancy.
  `.2` validates the collective graph; `.3` decoding/projection must preserve
  that admission boundary; `.4` pressures both dangling and reoccupied
  endpoints through the actual consumers, including rehashed bad payloads.

These decisions are recorded in the plan/checklist. Runtime behavior is
unchanged by this follow-up. Existing tests already cover `""`, normalized
numeric IDs and the integer/string distinction; the supplied review's extra
probes are user-reported, not a separately retained executable campaign.

Validation commands, from the repository root:

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -v test_grc_9_v4_topology test_grc_v4_geometry.GraphTests
.venv/bin/ruff check src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

The first three commands pass: **23 methods** (7 new, 16 generic graph), Ruff
and mypy. Explicit `PYTHONPATH=src`
is required to test this checkout: the environment also contains an installed
`pygrc` copy, and the initial invocation without it failed to import the new
module. The subsequent run verified the repository module's import origin.
No numerical-family campaign was needed for these discrete primitives.

At the `.1` checkpoint, the [work manifest](./phase-9-grcv4/runtime/RuntimeWorkManifest.json)
added exactly two entries under the existing formal iteration `P9-8.1a`. Its record digest,
accepted G3/path permission and both new hashes check correctly; every previous
entry and authority field is unchanged:

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_topology.py` | `a924c92265d8143f9ef2c64f0aafc0385e765867e3bfab9a01c0106eb444b84e` |
| `tests/models/test_grc_9_v4_topology.py` | `c1ca83efd6e2befed73cbb4affff4c36d68b9bde4bfe4b226c4b8ce70d1b7bf4` |

**Initial phase-boundary result at `.1`: failed.** This failure is resolved by
the later [reconciliation](./phase-9-grcv4/tranche-8/P9-8.1-BindingReconciliation.md).
The initial command stopped at
`implementation maintenance binding drift: implementation/Phase-9-GRCV4-Handoff.md`.
A complete inventory of the two binding lists finds 13 maintenance mismatches
and 25 existing work-entry mismatches, each already different at committed
baseline `7ba0f61`. Separate full `work_entries` validation also rejects with
`work content binding mismatch`. The maintenance set includes planning files,
side-tool files, earlier C verification owners and the event codec; the work
set includes earlier generic source/tests and `pyproject.toml`. These are
broader than this increment's two files, and overlap must not be summed into
a unique-file count. No policy hash or old work entry is changed to mask them.

The initial diagnostic is reproducible from the committed `.1` subject even
after the current binding lists have been reconciled:

```python

## P9-8.1a.2 immutable port-graph admission

2026-10-02, branch `work/p9-8-1-shared-mechanics`, baseline `abafce0`.
The [topology module](../src/pygrc/models/grc_9_v4_topology.py) now provides
frozen, slotted `GRC9V4PortEdge` and `GRC9V4PortGraph` records. Edges validate
nonempty UTF-8 string IDs, exact `boundary`/`spine`/`tree` kinds and typed
endpoints. The graph owns collective admission: duplicate normalized node IDs,
duplicate edge IDs, dangling endpoints and repeated `(node_id, port)`
incidences reject. Declared node/edge order and tail/head orientation remain
unchanged. Each edge and endpoint is copied and revalidated at construction;
caller-owned lists or nested records cannot subsequently change its contents.
Normal mutation is frozen, and `dataclasses.replace()` reruns admission.

Empty graphs, isolates, disconnected components, legal parallel edges and
loops with two distinct ports are admitted. A loop consumes both ports, and
even its own tail/head cannot occupy the same port. D11-G9's expansion-source
loop restriction remains an event rule. Empty-string node IDs stay valid when
live; absent `""` endpoints reject. Normalized `1`/`1.0` IDs coincide while
`1`/`"1"` remain distinct for membership and occupancy. No endpoint field type
has changed: equality remains sound for exact normalized built-in values.

The graph is the structural owner to extend in `.3` with the existing wire
envelope, typed/JCS digest and read-only generic projection. Local endpoint or
edge construction still cannot stand in for graph admission. No codec,
projection, model admission or event eligibility is claimed by this increment.
The parent stays open for `.3` and `.4`.

The [tests](../tests/models/test_grc_9_v4_topology.py) add sixteen methods:
identity/kind/type rejection, ordered input ownership, frozen records and
replacement validation, empty/isolated/parallel/loop graphs, dangling and typed
membership, duplicate IDs, all tail/head collision positions and degree-nine
saturation. Every port reuse on a saturated node rejects in either orientation.
A separate exhaustive literal-token oracle covers all **1,296** ordered
two-edge incidence patterns over integer/string nodes and ports 1/5/9:
**360 admit, 936 reject**, as required by unique incidence occupancy. Input
detachment is checked even after forcibly mutating the caller's original
records; this does not claim to support bypassing `frozen` on the graph's own
records.

Validation from the repository root:

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -v test_grc_9_v4_topology test_grc_v4_geometry.GraphTests
.venv/bin/ruff check src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

All **39 methods pass** (16 new edge/graph, 7 prior chart/endpoint, 16 generic
graph); Ruff and mypy pass. The **current phase-boundary audit passes** after
refreshing exactly the two scoped work entries and the three edited planning
documents' maintenance hashes, plus their containing record digests. The formal
iteration remains `P9-8.1a`. The historical `.1` hashes above remain checkpoint
evidence; current `.2` work identities are:

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_topology.py` | `d02e8df332871cd73edcbdbe655e32f8db5b944b4f5c47145cc0dbd7df6fb1aa` |
| `tests/models/test_grc_9_v4_topology.py` | `f4e0d3d33e7183d20e3ec812fc25a700e4a375be12cb581fa310fb30b75aa2f1` |

The existing reconciliation records and accepted scientific evidence are
unchanged. Its separate retained-source failures are neither rerun nor
reclassified by this structural graph checkpoint.

The user explicitly accepts this checkpoint on 2026-10-02 (“Great, accept and
commit”). Their supplied comparison against the normative port-graph section
reports no discrepancy in the implemented chart, endpoint or structural graph
layer and independently confirms the 360/936 exhaustive-oracle counts. This is
a user-supplied review of the uncommitted source/test hashes above, not a new
runtime or serialization conformance claim. The envelope and generic projection
remain assigned to `.3`, and parent review remains `.4`.

The acceptance retains strict built-in JSON value types and the interpretation
that a loop needs two distinct occupied ports. The review correctly notes that
the specification's “at most one live edge” wording does not expressly settle
two incidences of the same edge on one port; the implementation's stronger
incidence rule is an explicit accepted convention, pinned by tests. Empty-string
node IDs remain admitted under the schema and generic graph contract, as
already examined in the `.1` follow-up and `.2` plan; tightening that contract
would require a separately approved scope change, not an implicit `.3`/`.4`
cleanup. No resource coordinate or authoritative port cache is introduced.

## P9-8.1a.3 graph envelope, identity and projection

2026-10-02, branch `work/p9-8-1-shared-mechanics`, baseline `37f77df`.
The [topology module](../src/pygrc/models/grc_9_v4_topology.py) extends the admitted
owner with the exact `port_graph_payload` and `serialized_port_graph` schemas.
`to_payload()` returns the three-field digest preimage; `to_envelope()` and
`to_canonical_bytes()` include the computed `graph_digest`. `from_payload()`
validates the closed schema and collective graph constraints. `from_envelope()`
also reconstructs and checks the digest. `from_json()` decodes the envelope
through an explicit `configuration` or `canonical` route using the existing V4
codec, with no fallback between routes.

`GRC9V4SerializedPortGraph` is an alias for `GRC9V4PortGraph`, preserving a single
owner. Its `schema_version` and `graph_digest` are read-only computed properties;
callers supply envelope fields through `from_envelope()`, rather than inject
identity into the structural constructor. The existing `payload_identity()`
contract computes `grc-graph-sha256:` plus SHA-256 of the JCS content preimage.
It excludes the digest itself, preserves declared node/edge array order and
normalizes only the previously admitted integral JSON numbers. No fixture,
schema, dependency or generic identity implementation changes are needed.

`generic_projection()` returns a frozen, slotted `GRC9V4GraphProjection` whose
only stored field is the admitted port owner. It derives nodes, oriented edges,
edge IDs, node/edge lookup, incident-edge stars and the outward-incidence matrix.
Loops cancel in incidence but retain their edge coordinates; parallel edges
retain their IDs and order. Graph identity delegates to the owner. Orientation
uses the existing `grcv4-ordered-outward-incidence-v1` descriptor over the port
payload, so ports and kinds remain bound even when generic adjacency is equal.
The view exposes no standalone graph payload/codec. Its constructor rechecks
admission and rejects tampered owners with mutable containers or unnormalized
fields; exported oriented-edge records are disposable copies.

This is a generic topology read surface, not yet numerical backend integration.
Existing `GRCV4Graph` exact-type gates remain enforced. The P9-8.1b differential/
row-weight bridge and later native integration must consume the owner-backed
view without introducing a separately serialized or hashed generic graph.
No lifecycle codec, event eligibility, allocator or profile conformance follows.
The parent remains open for `.4` integrated review.

Sixteen new [test methods](../tests/models/test_grc_9_v4_topology.py) verify:
the frozen `GRC9V4-PORT-GRAPH-PAYLOAD-DIGEST-ENVELOPE` vector and its separate
frozen canonical preimage; payload-only hashing; both JSON routes; malformed,
missing, extra and forged envelope fields; numeric/Unicode boundaries; declared
order, port, kind and orientation identity; input/output detachment; and the
single-owner projection. Seven independently rehashed structural defects each
reject through content admission, envelope admission, configuration JSON and
canonical JSON (28 route/defect cases). These include integer/string membership,
absent empty-string nodes, duplicate IDs, occupancy reuse and same-port loops.
Independent ASCII/integer preimages and a literal UTF-8 preimage supplement the
frozen vector; expected identities are not computed through the new graph codec.

Validation from the repository root:

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -v test_grc_9_v4_topology test_grc_v4_geometry.GraphTests test_grc_v4_codec.CodecTests
.venv/bin/ruff check src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

All **80 methods pass** (39 topology, 16 generic graph, 25 codec), as do Ruff,
mypy and the **current phase-boundary audit**. The two current source/test work
entries remain under `P9-8.1a`; only those hashes and the three edited planning
documents' maintenance hashes are refreshed, along with their record digests.
The `.1`/`.2` hashes above retain their historical checkpoint meaning.

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_topology.py` | `195dd8bb2ee19a2e1a74979311a7ee15bc11b8b99f0df3b3b90da4410c04d747` |
| `tests/models/test_grc_9_v4_topology.py` | `106f2d87eff3ca3d0969e4569e6f85541cb12fc70a9b8a3054cb9c013892c1df` |

Historical scientific-source failures retain the separate scopes recorded in
the binding reconciliation. This discrete graph checkpoint does not rerun or
reclassify them.

## P9-8.1a.4 integrated review and parent completion

2026-10-02, branch `work/p9-8-1-shared-mechanics`, baseline `9b2e96e`.
**Own-review verdict: pass within P9-8.1a's chart/port-graph scope, after one
correction.** All four implementation checkpoints are verified and reviewed;
the parent checklist item is complete. This records the requested own review,
not an external audit, a new user-acceptance statement or later runtime entry.

The review compared the complete module with the
[port-graph contract](../specs/grc-9-v4-spec.md#port-graph),
[common backend extension](../specs/grc-common-interface-v4-ext.md#graph-and-differential-backend-extension),
closed endpoint/edge/payload/envelope schemas and frozen identity vectors.
It found one missing API: the common extension requires **port-to-edge lookup**,
which was derivable from the admitted edges but not exposed as a consumer.
`GRC9V4PortGraph.edge_at(node_id, port)` now validates the endpoint and live
membership, returns its occupying frozen edge, or `None` for an inactive port
on a live node. Unknown nodes raise `KeyError`; malformed IDs/ports reject.
Integer/string identity and the inherited integral-float normalization are
preserved. A loop's two distinct ports resolve to the same stable edge.
The lookup scans the sole admitted graph and adds no cache or state coordinate.

The review found no remaining chart/graph correctness defect in the tested
scope. The evidence is retained in the repository's
[integrated tests](../tests/models/test_grc_9_v4_topology.py), with these results:

| Obligation | Evidence and disposition |
| --- | --- |
| Chart and structural admission | Existing all-nine chart oracle, strict numeric/type guards, typed membership, duplicate IDs and 1,296 direct-construction incidence cases remain passing. Unique occupancy over ports 1..9 establishes the active-port bound; parallel IDs do not relax it. |
| Frozen envelope and graph reconstruction | The source envelope and all 17 frozen expansion-target graph payloads reconstruct with their published digests. Every live node's nine ports are checked against literal fixture incidences through chart conversion and `edge_at()`. Only graph structure/identity is exercised, not construction or native expansion of those targets. |
| Orientation through public consumers | All 512 independent edge reversals of a saturated nine-port star decode from independently encoded canonical envelopes, preserve bytes and edge ordering, and match literal signed incidence columns and port lookups. |
| Collective admission after decoding | All 1,296 two-edge incidence patterns pass through canonical decoding: 360 legal patterns admit and 936 collisions reject. Accepted graphs retain the expected edge IDs through projection and lookup. A valid digest cannot waive occupancy. |
| Capacity outliers | 72 independently rehashed tenth-incidence attempts reject: each of nine occupied ports, both orientations, both configuration/canonical routes, and both nine-spoke and four-loop-plus-spoke layouts. The loop layout saturates nine ports with only five incident edges and zero loop columns in incidence, so a degree/column shortcut cannot hide occupancy. |
| Closed inputs and identity | After warming admission, nine Boolean/type/extra-authority defects reject through both wire routes. Cyclic native input and an escaped duplicate JSON key reject. Existing forged/recursive digests, unsafe numerics, Unicode and array-order controls remain passing. |
| Ownership and single graph authority | Replacement produces a separately admitted graph while the existing view remains attached to its original owner; mutated exported payloads cannot change that owner, its lookup or identities. Computed identity/schema properties and edge records reject ordinary mutation. The projection retains only its owner and has no standalone graph codec. |
| Process determinism | Canonical envelope bytes, graph digest and orientation identity agree in fresh processes with Python hash seeds 0, 1 and 73. Python hashes do not become wire identity. |

The eight new methods bring the focused total to **88 passing methods**:
47 topology, 16 generic graph and 25 codec. Ruff and mypy also pass. Run from
the repository root:

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -v test_grc_9_v4_topology test_grc_v4_geometry.GraphTests test_grc_v4_codec.CodecTests
.venv/bin/ruff check src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

The **current phase-boundary audit passes** on the final `.4` subject, with
only the two scoped source/test work hashes and the three edited planning
maintenance hashes refreshed, plus their containing record digests. Formal
work ownership remains `P9-8.1a`; frozen specifications, scientific evidence
and prior acceptance records are unchanged.

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_topology.py` | `c085dc3b4a746bf3f0720cb68722fcfa150c4b9a0805392467605b8b597299b9` |
| `tests/models/test_grc_9_v4_topology.py` | `f9983f0a5de9709a7f25219b51efe3e2c7d72d395aa4b0493562ede3c0d9e11a` |

The accepted `.2` conventions remain explicit: empty-string node IDs are live
when declared, exact built-in normalized types define endpoint equality, and a
loop needs distinct ports. The serialized graph name remains an alias of the
same owner, with caller envelopes entering through checked factories and
schema/digest exposed as computed properties. Deliberately bypassing frozen
storage on the admitted owner's own objects is not a supported mutation API.

The generic projection is still a topology surface: the numerical/row-weight
bridge, allocator, expansion eligibility/execution, lifecycle, profile and
arbitrary-size conformance remain with their later owners. The seventeen frozen
targets above are not seventeen successful native expansion executions.
Performance optimization, including any lookup/index cache, remains scheduled
at the end of Tranche 8 with the validity obligations below. The separate
historical scientific-source failures retain their reconciliation scopes.

## P9-8.1b row differential and weight bridge

2026-10-02, branch `work/p9-8-1-shared-mechanics`, predecessor `75a6629`.
The user requested the entire leaf in one pass, retaining recorded subitems as
for `.a`. **Own-review verdict: pass within the shared mechanical scope.**
The checklist records `.1` input/policy contract, `.2` equations, `.3` weight
selection and `.4` integrated review as complete together. The user explicitly
accepts the complete reviewed P9-8.1b result on 2026-10-02 (“review passes fully.
commit changes”). This acceptance covers the recorded shared mechanical scope
and its stated integration boundaries; external audit authorship and later
native conformance are not inferred.

Authority is the normative [row backend and bridge](../specs/grc-9-v4-spec.md#fixed-row-basis-differential-backend),
the existing `row_weight_policy` schema and the common backend extension.
The scoped execution successor requires the unchanged accepted G3 set and
the exact committed `.a` source/test subject; it opens only `P9-8.1b` on the
existing topology source/test paths. Historical G3's `.a`-only decision is
unchanged. `.c`/`.d`, expansion, compatibility and facade paths remain closed.
No new gate or specification/schema change is introduced.

The [topology module](../src/pygrc/models/grc_9_v4_topology.py) now provides:

- `GRC9V4RowDifferential`: pure fixed-row gradient, diagonal Hessian, signed
  Hessian and outward row-current sums, in live-node order. Row assignment uses
  the local endpoint port; parallel edges remain separate and a loop supplies
  both endpoint incidences, including both weights when its ports share a row.
  This follows the admitted port-incidence convention; loop delta is zero,
  and its opposite currents cancel when in the same row. Event-source loop
  eligibility still belongs to its later owner.
- `legacy_node_tensors`: the separately named historical diagonal diagnostic,
  preserving the row-local weighted squared mismatch and isotropic square of
  total outward flux. It is never substituted for graph K4.
- `GRC9RowWeightPolicy`: the existing closed, serialized policy, matching the
  frozen specialization vector. Arbitrary source/stage substitutions reject.
- `GRC9V4PostbeatRows`: detached complete profile, committed C/W/Z coordinates,
  physical current, step index, Hessian sign and exact enabled stage. A selects
  committed W_A directly; C selects W_C_tr in stable graph-edge order and
  requires exact key coverage. The profile's eta-scaled mobility, Hodge and
  trial weights are not exposed as alternative sources. Every evaluation is
  fresh; the implementation-local input identity binds all stored inputs and
  the sole port graph's content/orientation identities.
- `delegate_native_row_weights`: read-only sampling of the exact GRC9V3
  delegate's native base-conductance map with native integer edge IDs. It
  neither steps nor rebuilds the delegate. Incomplete native transport state
  rejects rather than falling back to port-edge conductance or enabled V4
  quantities. The compatibility owner will control branch/stage selection.

Numerical inputs inherit the generic finite binary64 vector admission contract,
including negative-zero rejection. Mechanical resource and weights are
nonnegative; the enabled A/C bridge retains strictly positive source weights.
Row expressions accumulate as exact rationals of those admitted binary64 inputs,
then each output rounds once to binary64. Empty and exactly zero-weight rows
produce positive zero; nonzero subnormal denominators stay nonzero. Intermediate
products/sums cannot spuriously overflow or underflow. An unrepresentable final
flux or node-tensor coordinate raises `NonfiniteGeometryError` before returning
any result. This local arithmetic recipe does not change the generic backend,
legacy delegate arithmetic, solver domain, or scientific state.

The [nineteen new test methods](../tests/models/test_grc_9_v4_topology.py) retain
the following portable evidence:

| Obligation | Evidence |
| --- | --- |
| Independent equations | Literal weighted-row/sign/current expectations, a scalar historical tensor example distinguishing both prohibited outer-product substitutions, and 120 reproducible 100-digit Decimal cases over sparse/full stars and loop layouts. The oracle scans literal port sets, independently of production chart helpers and rational accumulation. |
| Orientation and covariance | All 512 orientations of a saturated nine-port star preserve expected physical rows after signed current reorientation. A separate mixed-label node/edge permutation verifies typed identities, port ownership and summation invariance. |
| Boundary cases | Empty graph, isolate, active zero-weight rows with nonzero flux, same-row and cross-row loops, parallel edges, both signs, malformed types/shapes, unsafe integers, nonfinite values and negative zero. |
| Numerical outliers | Minimum subnormal weights and products, maximum finite resources/weights with overflowing naive numerator/denominator, exact large-current cancellation, and explicit rejection of unrepresentable final flux/tensor outputs. |
| Source/stage binding | A post-beat W replacement changes the result and input identity; C map order is immaterial while graph order controls coordinates. Missing/extra/renamed C keys reject even after rehashing; predictor/trial/pre-continuity/history/reset/disabled stage labels reject. Forged complete-profile identity and candidate/carrier/shape mismatches reject. |
| Integrated consumers | All ten accepted generic declarations select the correct candidate source and carrier shape. Real generic A_OS/C_OS lifecycle commits supply their committed resources, updated A W and authoritative same-beat current to the row boundary. This is an explicit test handoff, not native GRC9V4 lifecycle wiring. |
| Ownership and disabled source | Caller mutation and later input replacement preserve older frozen results/identities; no second generic graph is stored or hashed. The real GRC9V3 delegate's snapshot is unchanged by inspection, native weights remain detached, and missing transport weights reject. |
| Scoped permission | Four focused verification methods cover historical G3 tampering, the exact `.b` successor, missing G3/changed predecessor, rejection of later/foreign paths and fresh-process policy import. Current-boundary reconciliation pressure remains passing. |

Validation: **187 runtime/regression methods pass**, including all 66 topology
methods, affected generic graph/codec/profile/state checks and unchanged legacy
differential/transport regressions. Ruff and mypy pass. The focused permission
checks and current-boundary reconciliation pressure pass, and the final
phase-boundary audit passes. Reproduce from the repository root:

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -q test_grc_9_v4_topology test_grc_v4_geometry.GraphTests test_grc_v4_codec.CodecTests test_grc_v4_profile test_grc_v4_state test_grc_9_v3_differential test_grc_9_v3_transport
.venv/bin/ruff check src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
PYTHONPATH=src:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -q test_p978_specialization_review.SpecializationReviewTests.test_acceptance_tampering_and_entry_widening_rejected test_p978_specialization_review.SpecializationReviewTests.test_row_bridge_successor_is_exact_and_preserves_historical_entry test_p978_specialization_review.SpecializationReviewTests.test_row_bridge_requires_the_committed_review_and_accepted_g3 test_p978_specialization_review.SpecializationReviewTests.test_fresh_api_policy_import_resolves_acceptance_helper test_p981_binding_reconciliation
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

Exact final subjects are recorded below and in the current work/maintenance
manifests. Only the two topology work entries move to `.b`; the three planning
documents and three scoped verification files receive new maintenance hashes.
Prior scientific/acceptance evidence and the `.a` subjects above are preserved.

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_topology.py` | `1c3136583ba0148ff708ed980597bf47f3ca5c270f0e6e82fd767a66f2865807` |
| `tests/models/test_grc_9_v4_topology.py` | `00bd5b342011effc413e8a8a0dea3273ad552e84de1863d19a8fc175d411568e` |

Remaining boundaries: the stage input record checks declared content; it cannot
authenticate that a caller actually completed a beat or align a falsely labeled
positional vector. Native lifecycle integration must construct it from the
committed owner and authoritative current at the prescribed stage, with the
combined specialization identity fixing the Hessian sign and policy. Pure row
evaluation, declared-profile shape checks and native conductance inspection do
not admit constitutive/solver domains or establish any of the forty disabled
compatibility cells. The generic numerical classes retain their exact graph
type gates. Trigger, coarse/Split, allocator/events, lifecycle and full profile
conformance retain their later owners. No cache was introduced; measuring and
proving any optimization remains scheduled at the end of Tranche 8.

## P9-8.1c mechanical candidate trigger

2026-10-02, branch `work/p9-8-1-shared-mechanics`, accepted predecessor
`7f33a42f8850dbae57b63c8ad09d85bececbaf6e`. The user requests this leaf in the
same way as `.b`: one implementation pass with recorded subitems.
**Own-review verdict: pass within baseline mechanical candidate detection.**
The checklist records `.1` policy/stage/scope, `.2` exact gates, `.3` admitted
post-commit fixture and `.4` pressure review as complete together. The user
explicitly accepts this complete reviewed result on 2026-10-02 ("accpeted and
commit changes"). Acceptance covers the recorded baseline mechanical scope,
including explicit rejection of the optional column-H lane and the stated
integration limits; it grants no later native conformance or completion scope.

Authority is the normative [saturation and hybrid spark semantics](../specs/grc-9-v4-spec.md#saturation-and-hybrid-spark-semantics),
the closed `spark_policy` schema and the unchanged `.b` row contract. The
scoped execution successor checks accepted G3 and the exact committed `.b`
source/test subject. It opens only `.c` on the already reviewed lifecycle
source/test paths. The historical G3 decision, topology `.b` bindings, generic
support declarations and later leaf permissions are preserved.

The [lifecycle module](../src/pygrc/models/grc_9_v4_lifecycle.py) provides:

- `GRC9SparkPolicy`: the complete closed policy, including detached optional
  child-stabilization content. Exact schema and numeric guards reject malformed
  types, nonfinite values, unsafe integers and negative zero.
- `GRC9V4CandidateDetection`: copies and revalidates `.b` postbeat inputs and
  the baseline policy. Its implementation-local identity binds both. Every
  assessment derives occupancy from the sole port owner and recomputes rows;
  no externally supplied summary, cached verdict or candidate list is consumed.
- `GRC9V4CandidateAssessment`: immutable node diagnostics with exactly nine
  occupied ports, strictly small gradient and strictly low signed Hessian
  combined by AND. The separate basin-seed predicate is small gradient AND
  minimum signed Hessian strictly above its positive tolerance; it is never an
  extra candidate gate. Results preserve live-node order and typed identity.

The gradient comparison uses the exact sum of squares of the fresh `.b`
binary64 output coordinates against the exact squared tolerance. This avoids
square overflow, subnormal underflow and a rounded square root landing on the
threshold. It does not substitute unrounded row arithmetic for `.b`'s output
contract. Signed-Hessian minima use the fixed diagonal backend and the bound
sign. Loops count both occupied endpoint ports; a loop-saturated candidate does
not establish expansion eligibility. No graph mutation, event, hierarchy update,
completion capability or scientific state is introduced.

The optional `grc9v3_column_h_assisted` lane remains schema-recognized but
explicitly rejects execution with `UnsupportedGRC9SparkLane`. Legacy column-H
threshold, history/sign-crossing and sink controls are absent from the closed
V4 policy; this leaf does not invent them. Future opt-in execution requires
bound controls and evidence. This restriction is on an optional lane, not a
dropped A/C realization. Child-stabilization content is retained in identity
without running its later completion semantics.

The [nineteen new test methods](../tests/models/test_grc_9_v4_lifecycle.py)
retain the portable pressure evidence:

| Obligation | Evidence |
| --- | --- |
| Exact predicate | All eight conjunction combinations and all 512 occupancy masks; loops consume both ports, parallel edges preserve separate ports, and empty graphs/isolates produce no candidate. |
| Strict boundaries | Equality and adjacent floats for gradient, spark and basin tolerances; zero gradient tolerance; both Hessian signs; basin seed independent of saturation and candidate classification. |
| Numerical outliers | A norm rounding to the threshold despite lying strictly below it; minimum subnormals; maximum-finite coordinates with a mathematical norm both below and above the finite threshold; atomic rejection of an unrepresentable row flux. |
| Independent oracle | 180 reproducible weighted source cases, literal row-port sets and 100-digit Decimal accumulation, rounded to the existing row-output contract before independent gate comparison. |
| Orientation and identity | 31 orientation patterns with reversed edge order; nine parallel edges between typed-distinct nodes `1` and `"1"`; candidate order follows live-node order. Policy thresholds, sign, beat and current are bound in identity. |
| Input ownership | Replaced committed resources change fresh verdict/identity while older snapshots remain stable. Malformed policy/input types and predictor/trial/pre-continuity/reset/history stage substitutions reject. Caller policy mutation is detached. |
| Scope separation | A direct column-cancellation example cannot bypass baseline Hessian failure. Optional column-H execution rejects. Child policy adds no event/expansion/completion API. All ten generic declaration shapes use the same baseline predicate without asserting ten numerical admissions. |
| Admitted handoff | A saturated C_OS source passes the real generic numerical constructor and ordinary commit before its actual committed resources/current enter the port-owned row/detection boundary. Independent fresh-state inequalities select only the central node. |

The admitted fixture has a unit-weight nine-spoke star (spectrum `{0,1,10}`),
strict `Lambda_C=1/2`, initial central C `3` and leaf C `3+1/64`, with
`kappa_M_C=0`, `kappa_Phi_C=1/64`, `eta_C=tau_C=1/8`, `chi_C=zeta_C=1/4`,
`kappa_H=1/1024` and `dt=1/4096`. The executable helper pins the remaining
numerical controls and the complete declaration
`grcv4-profile-sha256:63f96db281496bebd732b69339cbe8f3a195be46cfc1b6b1769f517783d80fa0`.
The commit uses the authoritative `os_corrector` current consumed by continuity;
reset is unchanged. Each fresh neighbor difference is strictly in `(1/64,1/32)`;
the squared gradient norm is below `1/4`, and sign `-1` gives a negative minimum
signed Hessian. Thus only the saturated center passes the frozen-vector baseline
policy. This is an already eligible source, not an inactive-to-active crossing,
new G2 acceptance or integrated native GRC9V4 lifecycle. Generic numerical
admission remains real; the explicit test handoff adds no second production
graph owner and detection leaves the committed generic owner unchanged.

Validation: **141 model/codec regression methods pass**, including all 19 new
methods and the existing topology/profile/codec coverage. Ruff and mypy pass.
Five focused authorization methods cover accepted G3, exact `.b` predecessor,
the two lifecycle paths, historical `.a`/`.b` scope and fresh-process import.
Three current-boundary pressure methods reject support promotion, unlisted
runtime/research additions and frozen legacy mutation. The final current
phase-boundary audit passes. Reproduce from the repository root:

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -q test_grc_9_v4_lifecycle test_grc_9_v4_topology test_grc_v4_profile test_grc_v4_codec.CodecTests
.venv/bin/ruff check src/pygrc/models/grc_9_v4_lifecycle.py tests/models/test_grc_9_v4_lifecycle.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_lifecycle.py tests/models/test_grc_9_v4_lifecycle.py
PYTHONPATH=src:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -q test_p978_specialization_review.SpecializationReviewTests.test_acceptance_tampering_and_entry_widening_rejected test_p978_specialization_review.SpecializationReviewTests.test_row_bridge_successor_is_exact_and_preserves_historical_entry test_p978_specialization_review.SpecializationReviewTests.test_trigger_successor_uses_only_reviewed_lifecycle_owner test_p978_specialization_review.SpecializationReviewTests.test_trigger_requires_accepted_g3_and_committed_row_subject test_p978_specialization_review.SpecializationReviewTests.test_fresh_api_policy_import_resolves_acceptance_helper
PYTHONPATH=src:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -q test_p981_binding_reconciliation.BindingReconciliationTests.test_rehashed_work_cannot_promote_support test_p981_binding_reconciliation.BindingReconciliationTests.test_unlisted_runtime_and_research_additions_still_reject test_p981_binding_reconciliation.BindingReconciliationTests.test_legacy_source_remains_frozen
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

Exact final subjects are bound as two new `.c` work entries. Only the three
planning documents and three scoped verification files receive maintenance
hash updates. Historical scientific/acceptance evidence and `.b` bytes remain
unchanged.

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_lifecycle.py` | `a65ea279b644f8592cd763d16e55e931661f7e8100c0e34002a345669589c5c3` |
| `tests/models/test_grc_9_v4_lifecycle.py` | `f6a991a8e742361df3a02e0a24d7a9827f484c9d97e56c6697bb6ad042c00b7e` |

Remaining integration duties: native lifecycle code must supply actual committed
inputs at the prescribed stage, with sign/policy fixed by the combined
specialization identity. A detached record validates declared content, not
chronology. Assessments constructed independently are diagnostics, not graph
provenance or expansion admission tokens. Column coarse/Split, allocation,
transactions, expansion, child stabilization, completed sparks, full native
profile conformance and the forty disabled compatibility cells retain their
later owners. No cache is added; the end-of-Tranche-8 review remains scheduled.

## P9-8.1d column coarse-graining and Split

2026-10-02, branch `work/p9-8-1-shared-mechanics`, accepted predecessor
`e9dfad748b16d9c67b6368f8e3689137944f8f47`. The user requests this leaf in one
pass with subtasks based on its content rather than the previous four-part
template. **Own-review verdict: pass on the exact field-encoding domain below.**
Three checkpoints are complete together: `.1` nonnegative column/simplex
algebra, `.2` canonical signed-flux channels, `.3` graph-bound field snapshots
and dispatch. Each includes its own inverse/domain/outlier evidence. The user
explicitly accepts current `.d` on 2026-10-02 and requests committing it before
new `.e`. This acceptance covers the recorded mechanical/default-backend result;
the direct-`Fraction` integration gap below remains assigned to `.e`.

Post-review correction: the accepted V4 backend contract requires `ExactScalar`
and `exact_number`, supporting Python and optional FLINT native rationals.
Direct `Fraction` use in `.b`, `.c` and `.d` bypasses that boundary, and `.d`'s
type guard rejects FLINT scalars. The existing generic source guard omits
`grc_9_v4*.py`, which is why the prior tests did not expose the gap. P9-8.1e
will correct runtime arithmetic, retained-value ownership and guard coverage,
run real backend parity, and classify P9-8.0's independent proof arithmetic.
The prior numerical results stand as default-backend evidence; they did not
establish specialization FLINT support. Binary64 public coordinates and `.d`'s
explicit exact reconstruction domain are separate from the backend correction.

Authority is the normative [column coarse-graining and Split](../specs/grc-9-v4-spec.md#column-coarse-graining-and-split)
and the closed `coarse_policy` schema. The accepted P9-1.5/G3 ownership places
`G9_coarse` in the topology module, superseding the earlier proposed standalone
coarse module. The scoped successor checks accepted G3 and all four committed
topology/lifecycle source/test subjects at `e9dfad7`, then opens only `.d` on
the two topology paths. Historical acceptance records, native generic support,
lifecycle `.c` and later expansion/facade permissions remain unchanged.

The [topology module](../src/pygrc/models/grc_9_v4_topology.py) now adds:

- `GRC9CoarsePolicy`: both schema-fixed encodings are present together.
  Requests explicitly name `nonnegative` or `signed_flux`; dispatch to the
  other encoding raises `CoarseFieldTypeError`, even for all-positive data.
- `GRC9V4PortField`: detached, generic-adapter-normalized binary64 values in
  live-node order and literal ports 1..9. Direct fields cover all chart
  positions, including inactive ones. `from_edge_values` gathers stable-edge
  values at their actual local ports, repeats nonnegative values at both ends,
  reverses outward signed flux at the head, and fills inactive ports with zero.
  A loop contributes at both distinct ports; parallel edges remain distinct.
- `GRC9V4ColumnProfile`: exact rational column total and three row shares.
  Empty columns have the unique exact uniform profile `(1/3,1/3,1/3)`.
- `GRC9V4SignedColumn`: independent nonnegative J+/J- columns with disjoint
  fine-row support. A signed total plus an absolute profile is never substituted.
- `GRC9V4CoarseField`, `coarse_grain_columns` and `split_columns`: the actual
  chart-specific operators. Encodings retain the sole immutable port graph
  and closed policy, with complete implementation-local content identities.
  Split requires the caller's graph binding and revalidates all nested values.
  No fine source values, graph cache or authoritative coarse state are stored.

**Exact arithmetic/domain decision.** Ordinary float division and multiplication
cannot implement the two exact inverse identities for every admitted fine
field. For example, a minimum-subnormal value sharing a column with a
maximum-finite value has a positive profile entry that rounds to float zero.
Three maximum-finite values also have a total outside binary64. This encoding
retains exact `Fraction` totals/profiles derived from the normalized binary64
fine field, so neither case loses information. Fractions are explicit derived
coordinates, not an extension to generic JSON/state admission. Identity encodes
their reduced numerator/denominator as strings, without unsafe JSON integers.
These descriptors are not a new normative serialized model schema.

The admitted coarse domain requires nonnegative total, exactly three
nonnegative shares summing exactly to one, the canonical uniform profile at
zero total, and products that are finite and exactly representable binary64.
No tolerance, renormalization, clipping or silent reconstruction rounding is
used. A hand-supplied `(total=1, uniform thirds)` rejects because its fine
coordinates are not binary64-exact; `(total=3, uniform thirds)` admits and
reconstructs `(1,1,1)`. Total overflow alone is harmless when the individual
products are representable. Unrepresentable, overflowing or underflowing fine
products raise `CoarseDomainError` before returning a field.

The inverse argument is direct. For a fine nonnegative column, let `T=sum(x)`.
When `T>0`, `(x/T)*T=x` exactly; when `T=0`, all entries are zero and the
uniform profile is canonical. Conversely, on an admitted coarse simplex,
`sum(T*pi)=T`; dividing by positive `T` recovers each share, and the canonical
zero case recovers its unique profile. Exact binary64 representability makes
conversion back to fine coordinates lossless. Signed columns apply this
argument to both channels. Disjoint support is necessary: otherwise Split
cancels overlapping channels and re-encoding cannot recover them. Enforcing
canonical max-positive/max-negative support therefore gives both inverse
identities, not just signed-value reconstruction.

The [sixteen new test methods](../tests/models/test_grc_9_v4_topology.py) retain
the portable evidence:

| Obligation | Evidence |
| --- | --- |
| Literal chart algebra | Columns `{1,4,7}`, `{2,5,8}`, `{3,6,9}`, all nine basis fields and all 512 support masks. Zero columns use exact uniform thirds. Both inverse directions are checked, including independently constructed coarse inputs. |
| Signed encoding | All 27 sign patterns in one column, positive/negative/zero fields, exact signed cancellation retaining both channels, independently constructed signed coarse inputs and overlapping-channel rejection. |
| Numerical extremes | Minimum subnormals, adjacent floats, maximum-finite values, totals above the float maximum, profile shares below the float minimum and mixed extreme signed values. |
| Independent oracle | 200 deterministic cases spanning binary64 exponents; literal column membership and 2,200-digit Decimal sums independently check channel totals, with exact reconstruction checks for all row products. |
| Domain/type admission | Missing/extra policy fields, alternate encodings, wrong request families, malformed node/port/column shapes, nonfinite values, negative zero, unsafe source integers, negative nonnegative fields, noncanonical zero profiles, incorrect/adjacent simplex sums and nonrepresentable products. Typed objects are revalidated at the operator boundary. |
| Graph binding | Mixed string/integer node IDs, isolates/empty graph, parallel edges and two local loop incidences. All 16 orientations of a four-edge loop/parallel fixture preserve the signed port field after matching current reversal and edge reorder. Split rejects changed node order/set, edge order/ID/kind, ports or orientation; a reconstructed identical graph is accepted. |
| Ownership/freshness | Caller mutations cannot alter fine values or coarse identities. New values yield new encodings/identities; old snapshots remain unchanged. Frozen slots and detached nested column records retain no mutable source aliases or cache. |

Validation: **163 model/regression methods pass**, including all 82 topology
methods, candidate-trigger, profile, codec and unchanged GRC9V3 coarse tests.
Ruff and mypy pass. Six authorization methods check historical entry boundaries,
the exact `.d` successor, missing G3/changed predecessor and fresh-process import.
Three current-boundary pressure methods reject support promotion, unlisted
runtime/research additions and frozen legacy mutation. The final current
phase-boundary audit passes. Reproduce from the repository root:

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -q test_grc_9_v4_topology test_grc_9_v4_lifecycle test_grc_v4_profile test_grc_v4_codec.CodecTests test_grc_9_v3_coarse
.venv/bin/ruff check src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_topology.py tests/models/test_grc_9_v4_topology.py
PYTHONPATH=src:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -q test_p978_specialization_review.SpecializationReviewTests.test_acceptance_tampering_and_entry_widening_rejected test_p978_specialization_review.SpecializationReviewTests.test_row_bridge_successor_is_exact_and_preserves_historical_entry test_p978_specialization_review.SpecializationReviewTests.test_trigger_successor_uses_only_reviewed_lifecycle_owner test_p978_specialization_review.SpecializationReviewTests.test_coarse_successor_is_exact_and_preserves_historical_owners test_p978_specialization_review.SpecializationReviewTests.test_coarse_requires_accepted_g3_and_committed_shared_subject test_p978_specialization_review.SpecializationReviewTests.test_fresh_api_policy_import_resolves_acceptance_helper
PYTHONPATH=src:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -q test_p981_binding_reconciliation.BindingReconciliationTests.test_rehashed_work_cannot_promote_support test_p981_binding_reconciliation.BindingReconciliationTests.test_unlisted_runtime_and_research_additions_still_reject test_p981_binding_reconciliation.BindingReconciliationTests.test_legacy_source_remains_frozen
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

Only the two topology work entries move from `.b` to `.d`; the three planning
documents and three scoped verification files receive maintenance hash updates.
The historical `.a`/`.b` subjects above remain reconstructible. Lifecycle `.c`
bytes, legacy runtime and scientific/acceptance evidence are unchanged.

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_topology.py` | `f73fd466d2ecbf76d62206f779fde6a22634099641e638c592c19810495e5ed5` |
| `tests/models/test_grc_9_v4_topology.py` | `eeed7dc3c02781a6838b43cdee7e202bf32f21f2b6d01677075021f2b7ea1897` |

Remaining integration duties: callers must gather fresh authoritative values
and supply the correct graph at the actual model stage. Content identity binds
a declared snapshot, not its chronology or a physical field's provenance.
An old encoding on the same graph remains valid as a historical field; it is
not automatically the current field. No cache exists in this leaf, so value
and topology changes cannot leave a hidden operator cache stale. Any future
cache requires complete field/graph/policy dependencies and the scheduled
end-of-Tranche-8 validity/equivalence review. Exact rational profiles and
outlier preservation are part of that obligation. Native facade capability
dispatch, full model serialization, disabled compatibility and scientific
conformance remain later work. This operator creates no graph fission,
generic graph coarsening, event, expansion or completed spark.

## P9-8.1e exact-backend correction and P9-8.0 audit

2026-10-02, branch `work/p9-8-1-shared-mechanics`. The user accepts current
`.d`, requests adding `.e`, committing `.d` first and then executing this
correction. That checkpoint is `a2d3d36ead9186147fb3434a3300084ce04f7e75`.
**Own-review verdict: pass for the scoped exact-backend correction.** All
three recorded obligations are complete. The user's 2026-10-02 request to
"commit changes" accepts this completed correction and its bounded P9-8.0
audit finding. It grants no broader native/FLINT conformance acceptance.

Authority is the accepted [exact CPU backend decision](./corrections/GRCV4-ExactCPUBackend.md),
alongside the unchanged row, trigger and column contracts. Direct runtime
`Fraction` imports bypassed this established boundary in `.b`–`.d`. The source
guard scanned only generic V4 filenames, so earlier default-backend reviews
did not expose the mismatch. This was an integration defect, not evidence that
the exact row or inverse equations were wrong. Historical acceptance and proof
artifacts are preserved; `.e` explicitly corrects the current implementation.

The [topology module](../src/pygrc/models/grc_9_v4_topology.py) and
[trigger module](../src/pygrc/models/grc_9_v4_lifecycle.py) now use `ExactScalar`
annotations and the shared `exact_number` constructor throughout. `ExactScalar`
remains the existing role annotation, not a new wrapper or nominal type.
Transient row/trigger arithmetic follows the active operation scope. Retained
column values and coarse fields capture `ExactBackend`; validation and Split
re-enter that backend after the construction scope exits. Native scalar
substitutions and mixed-backend columns/channels reject. Re-encoding a split
fine field under a different backend is explicit and preserves content identity.
The future native model owner must continue to establish its selected backend
around calls, as the generic lifecycle already does.

Backend-neutral `integer_ratio` extraction replaces representation assumptions.
At the prescribed binary64 boundary, Python integer division of the exact ratio
preserves the original rounding behavior independently of native scalar float
conversion. Coarse reconstruction still additionally requires exact equality
with the resulting binary64 value; nonrepresentable products reject. The
retained backend tag does not enter graph, input or coarse content identity.
Default-backend digests for both field families are pinned from the accepted
`.d` source at `a2d3d36` and pass unchanged on both backends. No generic exact
backend, numerical policy, schema, scientific state or legacy implementation is
rewritten. Three obsolete test type-ignore annotations are removed because
`ExactScalar` is intentionally `Any`.

The [shared backend tests](../tests/models/test_grc_v4_exact_backend.py) now
scan public and private generic V4 **and** GRC9V4 filenames for direct Fraction
imports/references. With the repository-pinned **python-flint 0.9.0 installed**,
four added methods establish:

- Actual native `Fraction`/`fmpq` row intermediates and retained coarse values,
  strict row/trigger result parity, legacy tensor parity, and 166 fine/coarse
  field cases per backend (80 deterministic wide-scale rows plus three outlier
  rows, each in both field families). Both inverse identities and `.d` golden
  content digests remain unchanged.
- FLINT-owned coarse snapshots remain usable outside their construction scope;
  copying preserves their native values. Mixed-backend fields/channels, false
  backend tags and malformed values reject, with scope restoration on failure.
- Halfway rounding cases, signed-zero normalization at computed-output boundaries,
  minimum subnormals, maximum-finite coordinates, unrepresentable thirds,
  underflow/overflow reconstruction and canonical-zero requirements have the
  same disposition on both backends.
- The two P9-8.0 modules importing production APIs execute their unchanged
  seven methods under each backend. These are 14 nested probe executions,
  separately counted from the enclosing test-suite methods.

**P9-8.0 finding.** A source/import audit of all 19 `test_p980*.py` modules
finds 18 using `Fraction` for independent exact or represented-research
calculations. This code is outside the production backend boundary; retaining
an independent rational oracle is appropriate. The additional Tranche-8 Python
file, `rg-numerical-review/export.py`, packages pinned source/evidence and
contains no numerical implementation. Production source imports none of these
P9-8.0 research modules.

Only `test_p980_feasibility.py` and `test_p980_readiness.py` import production
APIs. The former parses existing profile/RG-domain declarations while computing
its rational discriminators independently. The latter constructs native generic
pairings/selectors from binary64 data and uses an independent rational spectral
witness; that witness is not handed into a native exact-scalar field. All seven
unchanged methods pass under both Python and FLINT. The generic runtime paths
already use the shared exact-backend API. No P9-8.0 proof or backend-boundary
defect was identified in this audit, so its accepted bounded mathematics and
R1–R10 restrictions remain unchanged. This is not a rerun of every research
trajectory, nor evidence of all-ten native specialization/FLINT conformance.
The archived represented kernels retain their recorded arithmetic and scope;
they are not silently promoted to selectable production backends.

Validation: **173 model/regression/backend methods pass, with no skips**,
including the existing generic FLINT owner/continuation checks and the four new
methods above. The final source-guard extension to the private GRC9V4 pattern
also passes its focused rerun. Ruff passes on the changed Python source/tests;
mypy passes on both specialization modules and their paired tests. Five scoped
authorization methods and three current-boundary pressure methods pass; the
final current phase-boundary audit passes. Reproduce with the pinned optional
dependency installed:

```bash
.venv/bin/python -m pip install python-flint==0.9.0
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -q test_grc_9_v4_topology test_grc_9_v4_lifecycle test_grc_v4_profile test_grc_v4_codec.CodecTests test_grc_9_v3_coarse test_grc_v4_exact_backend
.venv/bin/ruff check src/pygrc/models/grc_9_v4_topology.py src/pygrc/models/grc_9_v4_lifecycle.py tests/models/test_grc_9_v4_topology.py tests/models/test_grc_v4_exact_backend.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_topology.py src/pygrc/models/grc_9_v4_lifecycle.py tests/models/test_grc_9_v4_topology.py tests/models/test_grc_9_v4_lifecycle.py
PYTHONPATH=src:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -q test_p978_specialization_review.SpecializationReviewTests.test_backend_successor_is_exact_and_preserves_other_owners test_p978_specialization_review.SpecializationReviewTests.test_backend_requires_accepted_g3_and_committed_coarse_subject test_p978_specialization_review.SpecializationReviewTests.test_coarse_successor_is_exact_and_preserves_historical_owners test_p978_specialization_review.SpecializationReviewTests.test_trigger_successor_uses_only_reviewed_lifecycle_owner test_p978_specialization_review.SpecializationReviewTests.test_fresh_api_policy_import_resolves_acceptance_helper
PYTHONPATH=src:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest -q test_p981_binding_reconciliation.BindingReconciliationTests.test_rehashed_work_cannot_promote_support test_p981_binding_reconciliation.BindingReconciliationTests.test_unlisted_runtime_and_research_additions_still_reject test_p981_binding_reconciliation.BindingReconciliationTests.test_legacy_source_remains_frozen
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

The `.e` scoped successor permits the four existing specialization source/test
paths and the shared backend test after checking their exact committed `.d`
subjects. Only four changed runtime work entries move to `.e`; the unchanged
trigger test remains under `.c`. Six existing maintenance bindings refresh.
Generic numerical source, historical P9-8.0 proof/evidence, old reviews and
accepted support records are unchanged. Expansion and later native gates stay
closed until their own scoped openings.

| Current `.e` subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_topology.py` | `f566cfd6c1cd42301d86b825da46ead8ba1d9142fc1d7e357b7d241577656f28` |
| `src/pygrc/models/grc_9_v4_lifecycle.py` | `a79de2f92f85e591980acfb2bcf529d4b8d124a40401e37848333d036fa03527` |
| `tests/models/test_grc_9_v4_topology.py` | `4aa9ba5677eb5328a62dee478fdb1ee55ec98a0635d7d99d5a832c5355212c4b` |
| `tests/models/test_grc_v4_exact_backend.py` | `0a936127aa5994491ce2cb0c77c51cba303e1d645237011419d08988db28accc` |

## P9-8.2 pure expansion allocator

2026-10-03, branch `work/p9-8-2-expansion-allocator`, baseline merge
`184919b352d96605037fd25cda2e9d38ef66b0f1`. The user requests substeps reflecting
the actual scope, delivered in one pass, followed later by P9-8.3. **Own-review
verdict: pass for the pure mechanical allocator.** All three substeps are
complete. The user explicitly accepts this reviewed implementation on
2026-10-03 ("implementation mathches specs and papers, accepted") and requests
commit and merge before P9-8.3C-OS. This accepts the mechanical allocator's
recorded scope; native specialization conformance retains its later owners.

1. **Request and identity admission.** The existing closed policy and input
   schemas produce frozen records. The plan binds the actual ordered port
   graph and the receiver-supplied source-state digest, checks live membership,
   rejects source self-loops and requires all nine occupied ports. Integer
   arithmetic computes `max(4, ceil((D-2)/7))`; explicit chirality and the
   conditional remainder phase select the balanced branch counts. Policy and
   both history-channel digest preimages are recomputed. The noncircular
   event payload determines the namespace; expected IDs/digests only assert
   equality, and a caller target graph or harness-fault field is rejected.
2. **Reserve-first construction.** Old boundary ports are reserved before
   internal allocation. Rewiring preserves each old edge's identity, kind,
   external endpoint and tail/head orientation. Both Latin spines and branch
   row rotors use the same port at both ends. A FIFO of free rotor slots is
   equivalent to the creation-order parent scan: the primary has one free
   slot, and each child consumes one and adds two. Thus every finite branch
   can grow, each new vertex has one parent, and the module is a tree with
   `n-1` internal edges and capacity `7n+2`. Role IDs include canonical padding;
   collisions reject. The immutable target is admitted through the sole port
   graph owner. Each new internal reference edge has the resolved positive
   bond seed and zero reference current; no constitutive state is inferred.
3. **Integrated pressure review.** All 17 frozen expansion graphs, event
   identity preimages/bytes and graph digests match exactly. All three frozen
   metamorphic vectors reproduce namespace/role transport before comparison.
   Four named semantic failure vectors reject before target allocation. A
   separate literal-chart oracle scans creation-order nodes and checks 224
   layouts over 48 sizes, through 1,004-node modules, both chiralities and all
   active phases. Connectivity, tree edge count, unique occupied ports, row/
   column balance, capacity and padding pass. The 4,995 capacity probes include
   safe-integer extrema without allocating those enormous graphs. All 512
   source-edge orientations, parallel external incidences, unaffected loops,
   isolates and typed/empty node IDs pass. Stale bindings, digest assertions,
   collisions, malformed types, deep input ownership, replacement, numerical
   extremes, Python/FLINT parity and three process hash seeds are covered.

Array order remains part of the source graph identity. Permuting source edges
therefore changes the event ID; after namespace normalization it produces the
same allocation. Target nodes use a deterministic typed/JCS scalar order and
target edges use UTF-16 ID order. Each unaffected edge record stays identical.

Resource tuples use the existing strict binary64 wire domain and must sum to
one in the selected exact backend. In particular, three rounded `1/3` values
and `(0.5, 0.5, minimum_subnormal)` reject even though rounded addition displays
one; exact tuples such as `(0.5, 0.25, 0.25)` pass. No silent normalization is
introduced. P9-8.0's rational uniform-third research companions remain their
own evidence. P9-8.3 must bind and verify its actual wire resource tuple and
charge-preserving transfer, rather than substituting rounded thirds for that
rational research input or treating allocation-vector `committed` labels as
new numerical successes.

The plan is a detached mechanical value. Its state/profile/history identities
are declared bindings, not proof of an ordinary beat or executable target
history policy. P9-8.3 retains resource/current/reset transport, candidate and
whole-carrier semantics, complete target references and numerical readmission.
Atomic publication, failure receipts, facade/capability integration, completed
sparks, and later native conformance remain with their existing owners.

Validation: **125 methods pass, no skips**, covering the allocator, topology,
candidate trigger and shared exact-backend suite (including its 14 nested
P9-8.0 executions); **seven scoped-entry checks pass**, including altered
parent subjects and missing G3/ancestor rejection. Ruff and strict mypy pass
for the new source/test pair. The current phase-boundary audit passes with
the allocator work entries and refreshed documentation/verification bindings;
historical scientific-source reconciliation is not promoted by this integrity
check.

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -q test_grc_9_v4_expansion test_grc_9_v4_topology test_grc_9_v4_lifecycle test_grc_v4_exact_backend
.venv/bin/ruff check src/pygrc/models/grc_9_v4_expansion.py tests/models/test_grc_9_v4_expansion.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_expansion.py tests/models/test_grc_9_v4_expansion.py
PYTHONPATH=src:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -q test_p978_specialization_review.SpecializationReviewTests.test_allocator_successor_is_exact_and_preserves_later_boundaries test_p978_specialization_review.SpecializationReviewTests.test_allocator_requires_g3_and_merged_parent_acceptance test_p978_specialization_review.SpecializationReviewTests.test_row_bridge_successor_is_exact_and_preserves_historical_entry test_p978_specialization_review.SpecializationReviewTests.test_trigger_successor_uses_only_reviewed_lifecycle_owner test_p978_specialization_review.SpecializationReviewTests.test_coarse_successor_is_exact_and_preserves_historical_owners test_p978_specialization_review.SpecializationReviewTests.test_backend_successor_is_exact_and_preserves_other_owners test_p978_specialization_review.SpecializationReviewTests.test_fresh_api_policy_import_resolves_acceptance_helper
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

The narrow execution successor checks accepted G3, the merged parent acceptance
and its exact source/test subjects before permitting only the reviewed new
allocator source/test pair. Existing mechanics, frozen specifications, P9-8.0
proofs and support/conformance records are unchanged. R1–R10 remain in force.

| P9-8.2 subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_expansion.py` | `c9edb7b584401b761538d7ad48b257697eabe1d92d16331c98903cf882f60ee3` |
| `tests/models/test_grc_9_v4_expansion.py` | `0e015347abe22457f0ffd3256ef0cbc60bcb7d13af4c809b39bd417e9064c86d` |

## P9-8.3C-OS native event integration

2026-10-03, branch `work/p9-8-3-profile-integration`, from accepted allocator
merge `79e0e8f`. The user requested this C_OS checkpoint after committing and
merging P9-8.2. Implementation and own review are distinct from user acceptance
and from a new G2/native-profile conformance claim.

The three content-specific checkpoints are delivered together:

1. `GRCV4Graph.from_port_graph()` gives the numerical kernels ordered node/edge
   coordinates derived from the immutable port owner. Serialization, graph and
   orientation identities include the ports/kinds; replacement cannot detach
   different coordinates from that owner. Ordinary generic graph bytes stay
   unchanged. Reference/stage reconstruction round-trips the port payload.
   `GRC9V4Specialization` checks resolved-policy/identity consistency;
   `GRC9V4COSState` binds the combined model, native reset and scientific state.
2. `GRC9V4COSExpansion` resolves the source-bound C reference template, preserves
   all old stable-edge weights, seeds every new internal reference edge, and
   reidentifies the complete target C profile/Hodge. Current and reset use the
   same exact affine coefficients independently. Zero core/extra resources
   remain zero, with no clipping or floor. C is rederived; W_A and Z_4 are absent.
   Carrier reset/loss cannot be reported for this absent channel.
3. `GRC9V4COSOperation` checks the actual native source digest, specialization,
   saturation and fresh hybrid predicate, constructs its own target, and
   numerically readmits both roles. All target authority and four native-bound
   receipts publish through one immutable pointer replacement only after result
   validation. Failure receipts remain outside the persistent ledger. The
   internal checkpoint replays requests from the admitted seed and compares
   the entire state/receipt payload, including reset and profile content.

The owner captures `ExactBackend`; all exact arithmetic uses `ExactScalar`
through `exact_number`. Retained state and wire numbers remain binary64, as in
the surrounding V4 kernels. Exact fractions in tests are independent oracles.
No new cache or memoized numerical-admission shortcut is introduced; the
end-of-tranche cache review below remains applicable.

**Exact bounded numerical companion.**
`native_cos_fixture()` in `tests/models/test_grc_9_v4_lifecycle.py` is a
separately identified source/target recipe, not the frozen construction vector
or the P9-8.0 rational experiment. It uses the ten-node saturated unit-weight
star with center `"s"`, exterior integer nodes 1–9 and port r at both ends of
edge `e<r>`. The source current starts at 3 at the center and 193/64 at each
exterior. Reset starts at 2 at the center, 201/64 at exteriors 1–8, and 193/64 at
exterior 9. Both have the same `Q_target=30.140625`. Only current takes one
source beat of `dt=1/4096`; reset remains independently retained.
The baseline hybrid lane uses Hessian sign -1, gradient/basin tolerances 1/2
and spark-Hessian tolerance zero, with no child-stabilization policy.

The event is positive-chirality, phase-three D52 (eight module nodes), with
exactly admitted binary64 shares `(1/2,1/4,1/4)` and bond seed 1. It retains
unit measures, zero structural K4 base and constant-zero context. C parameters
include cutoff `1/512`, kappa_M=`2^-24`, kappa_Phi=eta=tau=1, chi=16,
zeta=`2^-37`, and kappa_H=1/2. Solver residual tolerances are `1e-11`, condition
limit `1e8`, OS tolerance `1e-8`, and charge absolute tolerance `1e-11`; all
remaining explicit parameters are bound by the fixture's full profile ID.

| Identity | Value |
| --- | --- |
| Source profile | `grcv4-profile-sha256:65f2b69cf01246ff5c3f5aa7b968a5f3730911528bcccf05d6a67a802df09048` |
| Target profile | `grcv4-profile-sha256:5547a6331724cfeed1f8b23d601ff3d6c4b7b2051821bc5e69b63b3173b49b64` |
| Specialization | `grc9v4-specialization-sha256:2257e35e18ca0f911f3a13fbf68174a8e8df2c7c18e2b552425e615edbae2503` |
| Event | `grc-event-sha256:6db74a08973ba98381ed9689caf526a3fb5d337a0f48daa9c73d153ba674ffd5` |

Independent expected resources use literal role maps and Fraction products;
event/model identities are independently hashed from declared preimages.
Target numerical continuation uses a literal dense C/OS equation oracle and
exact represented-resource continuity. Both roles complete ten target beats
plus final readmission. Python and real FLINT produce identical event
checkpoints; backend selection stays with the owner after caller scope changes.
The original P9-8.0 cutoff=1 source/target rejection remains a negative
regression. Rational thirds and the research experiment's two different charge
targets are not silently imported into this native fixture. No R1–R10 research
bound is extended to the new recipe by assertion.

Pressure includes nonuniform old-edge weights, distinct seed weights, zero and
extreme resource inputs, independent current/reset failures, absent-history
misdeclarations, late receipt failure, stale IDs, exact-simplex rejection,
candidate gating, concurrent submissions and altered replay payloads. Pure
resource-map extreme tests establish rounding behavior, not numerical admission
of those extreme states. The adapter rejects nonzero structural K4 bases and
specialization changes without inventing a missing transfer policy.

This is an internal C_OS event checkpoint, not the complete Tranche 9 model
facade. Its initial postbeat seed is numerically admitted, not evidence of an
authenticated earlier ordinary-operation/receipt chronology. Public ordinary
steps, reset, save/load, compatibility and capability advertisement remain
separate work. P9-8.4–8.6 deeper/covariance/whole-lifecycle duties and every
other P9-8.3 profile remain open. On 2026-10-03 the user explicitly accepts
this bounded checkpoint and the pressure-review correction below:
"this is much better, great. accept and commit". P9-8.3C-OS is complete for
the reviewed scope, including its recorded continuation limits; the user
requests committing these changes on `work/p9-8-3-profile-integration`.

### P9-8.3C-OS pressure review

The additional review requested on 2026-10-03 found and corrected one runtime
admission defect. The earlier zero-duration `ProvisionalCandidateCOSStep`
read checked resource/charge and reference current, but deliberately skipped
OS predictor/geometry/corrector/split reconstruction. That was insufficient
for the event contract in paper §12.7.5 and Appendix E.10's OS event row.
An ordinary successful continuation of the positive fixture had not exercised
this missing rejection path.

Two genuine counterexamples preserve the baseline source equations and vary
only the declared OS tolerance (and, in the second case, set reset equal to
current). At tolerance `2^-54`, both source roles and target current pass full
OS admission, but target reset fails the split residual. At `2^-56`, both
source roles pass and target current/reset fail. The old zero-step target
gate accepts both counterexamples. The corrected event rejects both at
`target_readmission`, with identical pre/post scientific and lifecycle state,
unchanged checkpoint and no appended receipt. A third `2^-58` regression
rejects an initial seed whose current and zero-step checks pass but whose
reset OS surface fails. These are numerical failures, not injected exceptions.

`_cos_readmit` now checks resource/charge and reconstructs the complete OS
pass and fixed-row analysis independently for current and reset. This applies
at initial/replayed seed admission, source re-admission and target admission.
The existing pure `CandidateCOSPass` API requires positive `dt`; its read
equations do not use duration. The local `dt=1` opens only that read path:
it never calls positive-duration continuity, advances time/index, stores
generated geometry as authority or performs a second OS iteration. Tests
compare subnormal/unit/large durations and commit an event at the largest
admitted step index without advancing its clock.

Mathematical comparison uses the repository
[paper](./investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md),
§§12.7.1–12.7.5, Appendix A.6–A.7 and D.3.2–D.3.5/D.5.3–D.5.4, plus the
[D11-C transport resolution](./investigations/grc9v4-constitutive-design/decisions/D11CCandidateBaselineTransportAndMobilityResolution.md)
and [D11-G9 allocation resolution](./investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationResolution.md).
The independent dense oracle matches the paper's `H_M=D H D`,
`Phi=kappa_Phi B H_M B^T C`, `J0=-eta diag(W) B^T Phi`,
`I_4M=H_M H^-1`, `Q=I_4M G_J`, `G_J=H^-1`, ungated resolvent,
single causal chi factor, predictor-star geometry and full corrector. It uses
NumPy eigen/linear algebra rather than production selector/solve routines;
resource products and continuity expectations use independent Fraction
arithmetic on represented binary64 values. This is bounded numerical
cross-checking, not a new analytic theorem or profile advertisement.

Additional permanent regressions in `NativeCOSEventTests` cover:

- Nonuniform old weights `W(e_i)=i/4`, distinct new-edge seed `1/2`,
  `eta=3/2` and `kappa_M=1/4`, on D9/D31/D52 targets, both chiralities and
  all three active phases. Both roles' predictor/corrector Hodge, potential,
  baseline, physical identification, current and read agree with the
  independent equations at `3e-12` absolute/relative tolerance. Mobility
  remains exactly `eta diag(W)` at both geometry stages; it is not inherited
  from retained Hodge. Target resources match literal satellite-role products.
- Two reversals (alternating old edges and all old edges), together with
  reversed node/edge ordering. Resources agree exactly after event-namespace
  role normalization; corrected-current divergence agrees within `3e-12`.
  This is selected numerical pressure, not closure of the later full
  representation/chart-covariance checklist.
- All three simplex vertices are legal event maps but can leave a zero
  resource coordinate with an outward derivative under this fourth-order
  transport. The independent equation predicts a negative next resource;
  ordinary steps at `dt=2^-12` and `2^-20` correctly fail without repair.
  Event admission alone does not establish positive-cone invariance or
  completed-child continuation. The separately identified baseline fixture
  still carries its own ten-beat current/reset continuation evidence.
- Positive finite bond seeds `2^-1074` and `1e308`: real target flat-map
  conditioning and nonfinite C-stage failures respectively, with atomic
  rollback and no injected failure.
- The exact dyadic simplex `(5421/32768,29653/65536,25041/65536)` produces
  target current charge one binary64 neighbor below `30.140625` under the
  specified adjacent reduction. The event receipts report the actual
  `-2^-48` delta; the zero-injection map retains `Q_target` and only the
  declared charge tolerance permits this rounding error. Reidentifying the
  profile with zero charge tolerances makes the same event reject. The
  implementation does not assert exact stored-sum conservation from an exact
  column-sum identity or silently repair resource coordinates.

The source-bound side tool was queried through
`load_successor_forensic_context(repo_root, side_tool_root)` and
`contract_provenance(context, contract_id)` (module path
`implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src`).
The following trace digests identify the queried contracts; their source
pointers resolve in the two D11 provenance supplements under `decisions/`.

| Contract | Source record / pointer | Trace SHA-256 |
| --- | --- | --- |
| `D11-G9-EC-LIFECYCLE-READMISSION` | `GRC9V4-D11-G9-PROVENANCE-SUPPLEMENT-v1`, `/equation_contracts/18` | `7de5da6b8cd676f15c7e9d7a4c684f008b3fb827cd4ce8fd1a584a0b7c29880c` |
| `D11-G9-EC-RESOURCE-DISTRIBUTION` | Same G9 record, `/equation_contracts/15` | `333da148d836e073a468bc1fffe2c2341e66a4f970981d93002a5032a28254e7` |
| `D11-C-EC-C-J0-LIFECYCLE` | `GRC9V4-D11-C-PROVENANCE-SUPPLEMENT-v1`, `/equation_contracts/10` | `12c7d5adc9fd0d42d0501483d9b5a0a71a442cc18290e05ee9cc9c7b1a6bb2fe` |
| `D11-C-EC-C-M4-FACTORIZATION` | Same C record, `/equation_contracts/1` | `a83b99b84339eca89f2d7427cb6ed6ba087cc6062f1b3ef13fbdfa28ddbbff89` |

The source record digests are respectively
`f39d82405a2a92b198289d71554ed907e18ac9183da4dfa07fc4f4944418ca4a`
and `57d711d80e648c8ee73401f3a7e76a0076374fc43bd4d2d0f3dbe4bb4ee3acb1`;
the source bundle is
`98c273b3cc097f0d95adfba98ed7dfac0ac494dce9e779bb4b04fe79fef4f6aa`.
The lifecycle rows explicitly retain runtime-conformance-pending support,
while the resource/factorization rows have bounded successor support. These
queries establish provenance and scope, not numerical correctness. The side
tool's `tool/scripts/test_iteration10_d11.py` reports
`ET_C10_D11_TEST_PASS checks=12 fail_closed=true`. Frozen paper, side-tool
records and accepted research artifacts were not edited; reproducible pressure
code is in the repository test suite, with no `/tmp` evidence dependency.

Final verification commands (from repository root):

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest tests.models.test_grc_9_v4_expansion tests.models.test_grc_9_v4_topology tests.models.test_grc_9_v4_lifecycle tests.models.test_grc_v4_exact_backend tests.models.test_grc_v4_geometry.GraphTests tests.models.test_grc_v4_geometry.PortOwnedNumericalGraphTests tests.models.test_grc_v4_geometry.ReconstructionTests tests.models.test_grc_v4_geometry.StageCacheTests tests.models.test_grc_v4_events tests.models.test_grc_v4_lifecycle
.venv/bin/ruff check src/pygrc/models/grc_9_v4_expansion.py src/pygrc/models/grc_9_v4_lifecycle.py tests/models/test_grc_9_v4_expansion.py tests/models/test_grc_9_v4_lifecycle.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_expansion.py src/pygrc/models/grc_9_v4_lifecycle.py tests/models/test_grc_9_v4_expansion.py tests/models/test_grc_9_v4_lifecycle.py
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

After the pressure correction, the final regression batch runs **268 methods:
267 pass, one opt-in installed wheel/sdist test skips** (332.2 seconds),
including seven additional permanent pressure methods. Seven focused successor-authorization
checks and all three `test_p980_readiness` methods pass; the authorization
checks cover each later entry, G3/accepted-parent mutation rejection and the
exact six-path C_OS scope. Ruff and strict mypy pass for the expansion/lifecycle
source/test pairs. The side tool's twelve D11 provenance checks also pass.
Whole-file geometry static checking retains its pre-existing
untyped evidence-helper diagnostics; it is not claimed clean by this increment.
The clean installed wheel/sdist primitive test is opt-in and is not part of
this local runtime result.

Reviewed source/test bindings for this checkpoint:

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_v4_geometry.py` | `c965f0ec7165ebe769cf4dd25ece98349213da1ae98f378acc0db8c1d231bebc` |
| `tests/models/test_grc_v4_geometry.py` | `fc58f82d73037f6330aa48b6d372f1f259864ca3c1013952c6f109676f7cab82` |
| `src/pygrc/models/grc_9_v4_expansion.py` | `e00ff377f3da9ce5e17be8722e091cd0787bd4a57f6ea9a2950a7e69aa84529b` |
| `tests/models/test_grc_9_v4_expansion.py` | `68b3be6347d6dc8eb0c180f55e7cf0c2d49e08b1e9ba81e9fed360a05ab85574` |
| `src/pygrc/models/grc_9_v4_lifecycle.py` | `fd7400c61276ef6f61999a7da9740ca15ed319ea1531b0be6d30da5746fe011f` |
| `tests/models/test_grc_9_v4_lifecycle.py` | `8573b3531157dabc0e580d1eea26f4a9374d902e765f18452b1caa12edffe6af` |

Only these six runtime entries and the edited maintenance/permission subjects
are rebound for `P9-8.3C-OS`. Frozen specifications, accepted P9-8.0 evidence,
historical reconciliation records, profile advertisements and other native
profile entries remain unchanged. The current-boundary command above is the
required final check on these bindings before handoff or commit; it does not
replay or recertify every historical scientific evidence bundle.

## P9-8.3C-PC whole-carrier event integration

2026-10-03, requested after accepted C_OS commit `eeb82e9` on
`work/p9-8-3-profile-integration`. C_PC's exact generic G2 declaration
`grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f`
is already in G3's accepted consumed set. The successor opens only the four
existing expansion/lifecycle source/test paths. This is a separately identified
bounded native companion; no new G2 discovery entry, generic PC change, other
native profile, public facade or whole-tranche closure is introduced.
The user accepts this bounded C_PC checkpoint on 2026-10-03
("great, then commit changes"), after confirmation that the review includes
outliers and edge cases, independent paper-equation checks and side-tool claims.
The acceptance includes the fixture, continuation and proof limits recorded
below; it closes P9-8.3C-PC without closing other native profile children.

The three content-specific checkpoints are implemented together:

1. `cpc_history_policy` reproduces the frozen
   `G9-EXPAND-C-PC-CARRIER-RESET` policy and digest convention:
   `whole_carrier_reset_with_loss_receipt_v1`, `whole_carrier_reset`,
   `zero_carrier_v1`, and exactly `carrier_history_loss`. The event owner
   recomputes the declaration from its actual current/reset pair before graph
   allocation. `GRC9V4CPCExpansion` independently checks that binding and
   source dimensions. Shared C construction rebuilds the complete stable-edge
   reference map/profile and uses the same exact affine resource map for both
   roles. Every target carrier coordinate is zero, including old-edge blocks.
2. `GRC9V4CPCState` derives geometry from current's old committed carrier.
   `GRC9V4CPCOperation` uses PC's full zero-duration admission for both roles:
   independent reset geometry, compact resource chart, symmetric star-supported
   carrier ball, whole-ball geometry/selector/current/source certificates,
   fixed-h current and row analysis. No carrier writer or clock increment runs
   during an event. Source policy, candidate gate, target construction, numerical
   readmission, result validation and all archive/receipt work precede one
   immutable publication. Failures append no archive or successful receipt.
3. Native replay starts from the declared postbeat seed, recomputes every event,
   and compares the complete canonical checkpoint, including ordered archives.
   Independent source/target numerical comparisons, delayed carrier effects,
   actual domain negatives, failure injection and backend parity are covered in
   `NativeCPCEventTests`; pure vector/reference checks are in
   `CPCReconstructionTests`.

`carrier_content_payload` uses the existing generic V4 convention: all current
row-major entries followed by all reset row-major entries. Each
`grc9v4-carrier-archive-v1` record retains that complete preimage and its digest,
source edge order, source graph/native-state digest and event ID. The primary
receipt binds both source and zero-target carrier digests, source/target model
and reset identities, and the explicit carrier loss. Candidate C remains
`rederived` with null candidate-history digests and no candidate loss. A present
all-zero source carrier still uses the explicit reset policy and nonnull content
digest. Archives are immutable evidence, never target authority. The new
`grc9v4-cpc-event-checkpoint-v1` format includes them; OS retains its prior format.

Shared private C construction/state/transaction owners avoid copying the event
engine. The closed public OS/PC siblings reject cross-realization states and
checkpoint formats. The accepted `eeb82e9` C_OS owner was executed independently
against the same fixture and compared byte-for-byte with the refactor. The
unchanged full checkpoint SHA-256 is
`b87595b68e6a344b17062de0df5b44fd498780ed3121233e33c27cfbed8b78f4`,
now pinned by a regression. The earlier C_OS binding table identifies its
accepted checkpoint; current shared-owner bindings are recorded below.

**Native numerical recipe and limits.** `native_cpc_fixture` uses the same
literal ten-node port star and baseline specialization as the C_OS companion.
Current starts at `(3,193/64,...,193/64)`; reset starts at
`(2,201/64,...,201/64,193/64)` with eight `201/64` values. Both share
`Q_target=30.140625`. The initial source carrier is
`Z[i,j]=sign(role)*(-1)^(i+j)*A_star[i,j]/16`, with current sign +1, reset -1,
unit diagonal and half-weight off-diagonal overlap on this star. Current takes
one actual PC beat of `dt=2^-12`; reset takes none. The archive binds that
postbeat current and independently retained reset, not a reference probe's
hypothetical writer output.

The complete PC declaration uses `R=1`, compact resource radius `M=16`,
`tau_PC=1`, `kappa_H=2^-16`, and `zeta_C=2^-30`. Remaining C parameters are
`Lambda_C=1/512`, `kappa_M=2^-24`, `kappa_Phi=eta=tau_C=1`, `chi=16`.
It retains zero structural K4 base, unit vertex measures, constant-zero context,
unit old/new reference weights, and the C_OS companion's declared solver/charge
controls. The event is D52, positive chirality, phase three, dyadic shares
`(1/2,1/4,1/4)`, with 16 target edges and a complete 256-entry carrier per role.
Both roles take ten target PC steps and a final readmission.

These PC parameters have their own complete identities. They do not import
P9-8.0's research radius `2^-22`, equal-third resource tuple or different
per-role charge targets into this owner. The frozen C-PC vector's two history
content tokens reproduce its codec identities; they are not interpreted as a
full numerical 9x9 current/reset carrier. All frozen mechanical vectors,
including its D30 allocation, remain unchanged and executed by the allocator
suite. The native full-carrier numerical evidence is the separate D52 recipe.

| Identity | Value |
| --- | --- |
| Source profile | `grcv4-profile-sha256:027fcc14b47d8cb4c0f1465109c1ca2c47cb5fefb3b002f499c9273c3b8c12f8` |
| Target profile | `grcv4-profile-sha256:54f87913e6b495b6828dd6854c57761a4a77c8ca8ac16626b5262152c2a1e630` |
| Specialization | `grc9v4-specialization-sha256:2257e35e18ca0f911f3a13fbf68174a8e8df2c7c18e2b552425e615edbae2503` |
| Event | `grc-event-sha256:982ddd3219ff9d52fbfeddc8d72b7beda369234723311226fab53ff3eda2609f` |
| Source carrier content | `grcv4-history-content-sha256:7d216270d9ab3739dd3f671dd2d061f0818d3ecd531bc0a898463ab0865ac43c` |
| Full native checkpoint SHA-256 | `8ac4c8c8d2cdc608deca4cbbd371e7fef79270f761dfd45931642f6775f1ea47` |

The admitted generic PC certificate reports source/target selector-gap lower
bounds `0.001800537109375` / `0.0018310546875`, Hodge lower bound
`0.9999847412109375`, and uniform source-norm upper bounds approximately
`0.109894` / `0.039074`, each below `R=1`. These are whole-chart certificates,
not inferred from zero target Z. The source and target share the same PC
radius, chart and writer declarations; no target-specific loosening occurs.

**Mathematical review and pressure.** The review compares the
[paper](./investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md)
§§12.7.3–12.7.5, Appendix A.6–A.7, D.3, D.7 and E.10, the
[D11-G9 resolution](./investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationResolution.md),
and the accepted [carrier companion](./phase-9-grcv4/tranche-8/P9-8.0-CarrierEventConstruction.md)
and [CEC-F1 review](./phase-9-grcv4/tranche-8/P9-8.0-CarrierEventIndependentReview.md).
`independent_pc_beat` independently implements old-Z fixed-h C equations,
`S=zeta*A_star(flat(read))`, continuity and the held-source solution
`Z_next=exp(-dt/tau)*Z+(1-exp(-dt/tau))*S` using NumPy, Fraction and a
150-digit Decimal exponential. It calls no production carrier geometry,
source assembler, continuity or ZOH writer. Exact represented Hodge entries
are checked separately against `diag(W)+kappa_H*Z`. Each actual source/target
step is compared with these equations, at `3e-12` relative tolerance, absolute
`3e-12` for resource/current and `3e-20` for source/carrier.

Target Z is zero at event entry. The first write forms nonzero Z; only a later
PC read consumes it. Both roles' step-ten old-Z/zero-Z current comparisons exceed
four times their two independent dense-comparison errors plus eight maximum
output ULPs. This is a bounded cross-implementation effect check, not the
research companion's interval-certified error theorem or a hysteresis claim.

Pressure includes stale current-only/reset-only carrier bindings rejected
before allocation; rehashed wrong loss/initializer/preservation policies;
absent, asymmetric and out-of-ball carriers; wrong old-Z geometry; changed
archive content/order/digests, omitted archives, changed target/reset policy
and stripped losses on replay; independent current/reset charge failures;
late archive/receipt failures; concurrent publication; maximum step index;
present zero carriers; and real Python/FLINT checkpoint/backend-scope parity.
With only bond seed changed to 2, both zero-carrier target point currents are
regular, but the full target uniform source envelope exceeds R. That event
correctly fails at `target_readmission` with unchanged scientific/lifecycle
state, checkpoint, archive and receipt populations. Point solvability alone
cannot replace the PC whole-chart obligation.

The side tool's source-bound queries reproduce
`D11-G9-EC-LIFECYCLE-READMISSION` trace
`7de5da6b8cd676f15c7e9d7a4c684f008b3fb827cd4ce8fd1a584a0b7c29880c`,
`D11-C-EC-C-J0-LIFECYCLE` trace
`12c7d5adc9fd0d42d0501483d9b5a0a71a442cc18290e05ee9cc9c7b1a6bb2fe`,
and `D11-G9-EC-FIXED-BOND-SEED` trace
`640a23034ac44cf894472a05c818477e68f818921ebcad72b433f3554106ee75`.
The first two retain runtime-conformance-pending support; provenance is not
numerical proof. Its twelve D11 regression checks pass. No frozen paper,
specification, vector, side-tool record or research evidence is modified.
All reproducing fixtures/oracles/regressions are retained in repository tests.

As with C_OS, the internal event checkpoint admits its supplied postbeat seed
without authenticating earlier ordinary-operation chronology. Full public
ordinary-step/reset/save/load wiring, P9-8.4–8.6 duties, other native profiles
and broader continuation remain separate. The end-of-tranche caching review
remains deferred; no numerical admission shortcut is introduced here.

Final verification (repository root):

```bash
PYTHONPATH=src:tests/models OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest tests.models.test_grc_9_v4_expansion tests.models.test_grc_9_v4_topology tests.models.test_grc_9_v4_lifecycle tests.models.test_grc_v4_exact_backend tests.models.test_grc_v4_geometry.GraphTests tests.models.test_grc_v4_geometry.PortOwnedNumericalGraphTests tests.models.test_grc_v4_geometry.ReconstructionTests tests.models.test_grc_v4_geometry.StageCacheTests tests.models.test_grc_v4_events tests.models.test_grc_v4_lifecycle tests.models.test_grc_v4_pc
.venv/bin/ruff check src/pygrc/models/grc_9_v4_expansion.py src/pygrc/models/grc_9_v4_lifecycle.py tests/models/test_grc_9_v4_expansion.py tests/models/test_grc_9_v4_lifecycle.py
.venv/bin/mypy --follow-imports=silent src/pygrc/models/grc_9_v4_expansion.py src/pygrc/models/grc_9_v4_lifecycle.py tests/models/test_grc_9_v4_expansion.py tests/models/test_grc_9_v4_lifecycle.py
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
```

The final regression batch runs **329 methods: 328 pass, one opt-in installed
wheel/sdist test skips** (403.6 seconds). This includes 11 native C_PC methods,
two pure C_PC reconstruction methods, the accepted C_OS regressions and all
48 generic PC methods. Thirteen focused successor-authorization/cutoff checks
pass: the prior seven successor checks, three new C_PC scope/G2/G3/predecessor
checks in `test_p978_specialization_review`, and all three
`test_p980_readiness` methods. The original exact-cutoff failure remains a
negative; no frozen fixture is relabeled as numerical success. Ruff and strict
mypy pass on the four expansion/lifecycle source/test files. The side tool's
12 D11 checks also pass. The opt-in packaging test is outside this local result.

Reviewed current C_PC source/test bindings:

| Subject | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_9_v4_expansion.py` | `8307090f3137bf29e4558a90b45a5547ae4bfb303cc5abbbc98694abfea39d22` |
| `tests/models/test_grc_9_v4_expansion.py` | `9fa8ac43bc4d2822a5b3db9c25ac127fc82dffe81779805217bee52d9c09902c` |
| `src/pygrc/models/grc_9_v4_lifecycle.py` | `4e64678878f287574e180f6862ee8700dc3174c8ff4a4b643d47de8f14f920b9` |
| `tests/models/test_grc_9_v4_lifecycle.py` | `40b0f0ddb984175f7c391815413838c3a8c6e704171e92af3c7149b7aef1129c` |

Only these four runtime entries are rebound to `P9-8.3C-PC`. The boundary
refresh covers the edited plan/checklist/handoff and the three edited
permission/review-checker subjects; every other bound subject must retain its
previous hash. This includes generic PC, the accepted C_OS geometry correction,
frozen authority and historical research/reconciliation records. The boundary
audit above is the final required check on these bindings; it does not replay
or recertify every historical scientific evidence bundle.

## Moving to another machine

Transfer `impl/phase-9-grcv4-tranche-7` after committing it through the usual
Git remote before switching machines, or use a later `main` that contains
that commit. No commit, push or merge is implied by this handoff. Keep full Git
history: acceptance checks inspect historical committed subjects.

After obtaining the updated branch, run from the repository root:

```bash
git switch impl/phase-9-grcv4-tranche-7
git status --short
git merge-base --is-ancestor b45d0af HEAD
git log -1 --format='%H %s'
```

Confirm that the checkout includes P9-6.5's `/acceptance` object with
`tranche_6_status: accepted_closed`, not only the numerical predecessor above.
If working from a later merged `main`, use that branch instead. The current
Tranche 7 implementation and record must also be present; Tranche 6 closure
alone is not P9-7.1 execution or acceptance evidence.

Rebuild the checkout-local environment from the committed lock; do not copy a
virtual environment between machines:

```bash
uv sync --frozen --extra v4 --extra dev
GRCV4_TOOL=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool
```

The accepted Tranche 6 runs used Python 3.12.3. Their records retain environment
and source identities; a different platform or resolution is a new execution,
not an exact replay of those observations.

For Node/browser checks, run the full bootstrap once:

```bash
.venv/bin/python "$GRCV4_TOOL/scripts/bootstrap.py"
```

It provisions managed Node, locked frontend dependencies and Chromium under
the ignored tool-local directories. Network access and browser OS libraries
may be needed. Use its managed tools, not global Node/npm. The
[tool README](./investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/README.md)
and [verification guide](./investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/Phase9VerificationGuide.md)
describe the CLI, API, notebook and browser surfaces.
