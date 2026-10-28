# P9-10.1a basin-interface design propagation — independent pressure

Date: 2026-10-28. Subject: the seven uploaded design, specification, schema,
acceptance and manifest files. No repository commit or native implementation was
executed or authenticated in this audit.

## Verdict

**Bounded PASS for the diagnostic mathematics and inspected design propagation.
Two small specification clarifications should be made before native code relies
on the contract.** Neither changes the accepted classifier, parameters, seed
thresholds, scope, or authority distinction.

The earlier BIF-1/BIF-2/BIF-3 concerns are substantively addressed in the supplied
paper and normative supplement. The findings below concern coverage wording and
complete canonical ordering, not a return to the earlier scientific questions.

## BIP-F1 — separate complete vertex coverage from partial region coverage

Location: `specs/grc-9-v4-basin-interface.md`, lines 112–116.

The sentence "Components, per-node rows and assigned regions must agree exactly
and cover every declared node" admits a per-collection coverage interpretation
that is incompatible with the intended partial assignment. The surrounding
paragraph explicitly admits unassigned quiescent/recirculating/ambiguous nodes,
and says zero flow has no assigned regions.

A single isolated node with ID `""`, zero gradient, zero signed Hessian diagonal,
zero row flux and positive thresholds has one quiescent component and one node
record. It has no assigned regions. This is a correct instance of the policy,
and the supplied schema accepts its shape. Its region union cannot cover the
nonempty node set.

The correction is to state:

- SCC member sets partition all declared vertices.
- Witness rows and classification records each cover all vertices exactly once.
- Region members partition exactly the assigned subset.
- Region seed members equal the seed-true subset of those members.

Formally, `union_s B_s = {v : basin_id(v) != null} subseteq V`, not necessarily V.
This is a clarification of the accepted partial rule, not a new admission gate.
Do not manufacture singleton basins or reject no-assignment observations.

## BIP-F2 — explicitly order region member and seed-member arrays

Location: supplement lines 143–149; schema `$defs/region`.

The ordering paragraph explicitly orders component members, components, terminal
references, node records and top-level region records by sink. It does not
explicitly order `region.members` or `region.seed_members`. These are arrays, not
wire sets. Exact-observation replay requires exact recomputed collections.

I constructed a two-node sink-region observation and reversed only its region
member/seed-member arrays. Both shapes pass the submitted schema. Component
order, component member order, node-record order, terminal references and
region-by-sink order remain unchanged. The two records have identical witnesses,
operand digests and observation digests and the same region member sets, but
unequal serialized derived collections.

Schema acceptance alone is not the issue: the schema intentionally delegates
ordering to semantic validation. The omission is that the prose's explicit
ordering list does not finish specifying these two arrays.

Specify that all node-ID arrays use the typed-node key, including region members
and seed members; seed members are the ordered subsequence of members whose
node records have `seed=true`. State that the public partial `basin_identity`
projection preserves the per-node ordering after filtering unassigned nodes.

This does not introduce label-dependent flow selection. No hash-formula or
classifier change is necessary.

## Earlier findings now covered

### BIF-1: full SCC evidence

Supplement lines 100–116 and schema component/node records now retain the full
SCC partition, local `cyclic` and `is_terminal` flags, nullable terminal kind,
each node's own component and its terminal outcome. A noncyclic upstream node
and its recirculating terminal are distinguishable. A leaking upstream cycle
can remain visible even when its nodes are assigned to an ordinary sink.

The previous fixed-multigraph current pair `(1,0,1)` versus `(2,1,1)` again yields
equal assigned regions and different full SCC records. The complete edge
witnesses and their observation digests differ too. These are synthetic graph
checks, not runtime-reached substrate states.

### BIF-2: explicit observation and replay

Supplement lines 48–90 and 173–201 define one captured read, role/context/model/
numerical/evaluator binding, lossless operands, a nonrecursive state projection,
and explicit replay modes. The observation digest does not contain itself or
its derived classification fields; those fields are independently recomputed.

The schema enforces the mode/presence matrix correctly: state-only has two null
observations; exact-observation has both records present. Every other presence
combination rejects. Swapped role records still have a valid schema shape, but
role checks are expressly required as additional semantics. That is not a new
schema defect.

Both signed zeros give the same no-arc classification but different lossless
operand and observation digests. This is correct: semantic support equality and
exact observation identity are different notions.

An exact replay failure cannot silently turn into state-only restoration. The
contract correctly withholds universal numerical determinism and cross-platform
bitwise claims. An implementation must bind/check both restored roles and the
complete captured root where applicable. A self-consistent witness hash alone
is not evidence that the data came from the bound native state.

### BIF-3: diagnostic identity and D4/D9

Supplement lines 165–171 and paper A.5.1 now explicitly include causal state,
normalization, hierarchy, events and basin-indexed cross-state comparisons.
Equal sink labels do not transport changing membership, and changed graph hashes
do not establish physical basin birth. No diagnostic relabel emits an event.

The diagnostic may return successful ambiguity, recirculation, quiescence, or
empty assignment. A classifier/serialization integrity failure still aborts a
transaction. This does not introduce a scientific gate requiring nonempty basins.

## Mathematical and numerical consistency

The inserted paper's arguments remain correct. Finite condensation ensures
nonempty reachable-terminal sets; singleton-sink regions are disjoint and
forward-closed in the frozen support graph; quiescent terminals have no distinct
upstream predecessor. These are not attraction or temporal-invariance results.

For a closed exactly divergence-free represented current, a singleton sink with
incoming nonzero flow would have strictly negative outward divergence. Thus no
assigned region can exist. The paper and supplement now state this consequence
without treating empty diagnostics as absence of physical organization.

The seed comparison uses exact squares of represented values and represented
thresholds, and strict Hessian comparison. The test routine exercised equality,
underflow-sensitive and overflow-sensitive square cases without rounded-square
substitution. The existing fixed-row/sign equations still control native rows;
this audit did not evaluate them on admitted C/W/Z states.

Typed IDs distinguish `0`, `"0"` and `""`; the schema uses tagged values rather
than JSON object-key coercion. A synthetic graph with integer-zero and
string-zero sinks gives distinct basin hashes. An assigned empty-string sink
is not treated as missing.

The explicit v2 specialization/resolved-parameter/complete-model construction
adds the diagnostic policy without replacing the generic constitutive profile.
The frozen v1 base specification remains a predecessor, not implicitly v2. The
new supplement states that historical models/snapshots retain their meanings.
Native configuration/checkpoint integration and migration remain forward work.

## Executed pressure

The unmodified schema passes `Draft202012Validator.check_schema`.

| Check | Result |
|---|---|
| Synthetic observations | 14 schema/limited-reference cases pass |
| Removing required fields in a complete observation | 99 expected schema rejections |
| Adding a field to its closed objects | 26 expected schema rejections |
| Checkpoint mode/presence product | All 8 combinations give the intended result |
| Canonical finite binary64 strings | 10,002 decode/re-encode bit round-trips pass |
| Exact seed arithmetic | 6 boundary/extreme cases pass |
| Schema-accepted semantic substitutions | 10 rejected by the independent limited oracle |
| Typed int/string sink identities | Distinct; empty-string assignment remains present |
| Upstream-cycle evidence | Equal region sets, different full SCC evidence |
| Signed zeros | Same classification, different observation identities |
| Native runtime executions | 0 |

The ten semantic substitutions include stale/wrong digests, wrong seed or
cyclicity, a dangling component reference, duplicate node records, absent
required regions, wrong seed-member subsets, a rehashed reversed current with
stale classification, negative thresholds and noncanonical hex.

These schema acceptances are intentional under its declared split between wire
shape and mandatory semantic checks. I do not misreport them as ten native
checker defects. The independent reference is limited: it does not establish
native freshness, resolve profiles, validate a current/root certificate,
reconstruct row fields from C/W/ports, or execute rollback/replay transactions.
Default synthetic row data are wire/arithmetic probes, not physical examples.
The isolated-node coverage example has exact zero row data.

## Integrity and exact-insertion verification

The four manifest-listed artifacts that were supplied match their raw-byte
hashes: DesignAcceptance, the full paper, the supplement, and the schema.

The manifest and DesignAcceptance `record_digest` values reproduce under the
sorted compact ASCII-escaped JSON record grammar with their own digest removed.
This grammar is kept separate from the JCS-based observation identity grammar.

For the supplied full paper:

- Full file SHA-256: `dd538ba5f731808d9cb8d95337a36fe2cb8ddfacece90c0f3001399381f63768`.
- Exact A.5.1 insertion SHA-256: `0a1a587feeff525be941714cbfdd8c701847a97d436a57e28bf67d8b0574d3b1`.
- Removing only that insertion reconstructs SHA-256
  `6060e28698c07068f91a5e40d5335d1cf8ae2c4292baf3a7c817a36f1ede57a9`, the manifest's
  predecessor paper hash.

Thus this paper is exactly the declared insertion successor, not merely a
similar document. This verifies no chronology by itself, and does not verify
the absent proposal's actual bytes or its equality to the paper.

The parent specialization specification's supplied hash is
`588878aabbe35a8b0c6ae5019f1d1116ab2a3bf15168793e37468abcf369e082`, as in the earlier
uploaded authority audit. Its lack of a v2 rewrite is consistent with the
separate-supplement approach, not evidence of a scientific regression.

## Verification boundary and disposition

`Authority.json`, `P9101aBasinAdmission.json`, the current GRCV4 proposal, updated
README/plan/checklist/decision-ledger files, the propagation verifier, and its
focused test source were not supplied/retrieved. The review's reported ten
conditional tests, six propagation tests, API/notebook/browser checks and native
support projections are not independently replayed here. Older conversation
proposal/check/audit files have different historical subjects and are not
substitutes for the acceptance-bound successors.

The acceptance explicitly names C_OS/C_CI/A_CI/A_PC and keeps native
implementation, P9-10.1a closure and full conformance false. Those limits are
preserved consistently. The mathematical debt need not be reopened.

**Retain the accepted design and propagation. Apply BIP-F1/BIP-F2 as local
specification clarifications, refresh only the affected propagation subjects,
and proceed to the already scoped native tests.** Preserve the separate native
freshness, typed semantic validation, both-role replay and atomicity obligations.
No new witness search, floating-point threshold or Tranche 8 campaign is indicated.
