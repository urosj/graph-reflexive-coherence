# P9-4.9.2 — accepted receipt-parent authority decision

Date: 2026-09-09. Status: **accepted bounded design; admitted and propagated for implementation**.
Accepted policy: `grcv4-previous-successful-primary-v1`.
Owner: P9-4.9.2, discharging the C_OS part of the P9-2.4/P9-7.6 obligation.

The user approved this rule and its ordered acceptance/propagation route on
2026-09-09 ("yes, i approve"). This accepts the bounded V4 design contract below,
not runtime conformance or a rewritten D10/D11 claim. The proposal filename is
retained for link continuity; the contract text is unchanged by acceptance.
The [structured authority and debt resolution](P9ReceiptParentAuthority.json)
is admitted through the side-tool's append-only P9 overlay, then propagated to
proposal/paper §12.5.1 and the V4 specification successor. The C_OS runtime now
uses the rule and explicitly declares snapshot layout v3, parent policy and
release. See the [implementation review](../../../phase-9-grcv4/tranche-4/P9-4.9.2-Review.md)
for execution evidence and remaining scope. No historical receipt or run changes;
public-facade completion, complete-profile evidence and G2 remain separate work.

## Decision and scope

For each successful operation, every receipt it emits names exactly the primary
receipt of the immediately preceding successful operation in that owner's
persistent ledger. The first successful operation has no parent. Use the same
rule for ordinary steps, successful zero-duration steps, reset, rebase, profile
migration and caller-mapped topology events.

The meaning is **previous successful ledger operation**, not previous ordinary
beat, previous numerical state, or every physical cause of the current state.
The rule is graph-generic; C_OS is the implementation scope being closed. Other
profiles and GRC9V4 require their own reviewed runtime evidence. This decision
does not change constitutive laws, event maps, history-loss rules or older families.

## Predecessor constraints, not retrospective parent-rule authority

The source review used the successor forensic API and the
[agentic guide](../tools/exploratory-side-tool/docs/AgenticQueryGuide.md).
All four contract queries returned `source_exact_contract_provenance` with
`support_disposition: indeterminate_requires_review` from
`GRC9V4-CD-D10.2-v1` in the [D10.2 record](D10_2FullSubstrateProvenanceAndPromotionAudit.json).

| Contract suffix after `D10.2-EC-` | Source pointer under `/normative_equation_contract_registry` | Constraint and retained query |
| --- | --- | --- |
| `PARENT-L-ORDERED-RECEIPTS` | `/50` | Ordered source/target profile binding; endpoint coverage is not crossing evidence. Full source/edge witnesses in [P9-4.7a](../../../phase-9-grcv4/tranche-4/P9-4.7a-ExecutionRecord.json). Trace `77fee7e8c48800eaf09ff53d4ba53fe20cfb14a749b036f1d37cb2b857fe854a`. |
| `PARENT-L-ATOMICITY` | `/44` | All authoritative coordinates commit together or not at all. Full witnesses in P9-4.7a. Trace `62a376f2a8e613b18a0999ce6bd16367ac45d0566c6b7b76d092fc64fbd11a57`. |
| `PARENT-L-SNAPSHOT-RESET` | `/45` | Snapshot/reset bind state, profile, context, charge and transformed baseline, not cache bytes. Full witnesses in [P9-4.6](../../../phase-9-grcv4/tranche-4/P9-4.6-ExecutionRecord.json). Trace `724545426e8380628505c85d0e3b560eec4388d4cacc711c1b4047a5066bf7dc`. |
| `EVENT-READMISSION-RECEIPT` | `/151` | Target readmission precedes atomic commit; receipts bind ordered endpoints, resource delta and history loss. Full witnesses in [P9-4.7b](../../../phase-9-grcv4/tranche-4/P9-4.7b-ExecutionRecord.json). Trace `2e08b2c901d7b3758d2b9f9c75bec5e18862dde44986a842eab8029db8055b07`. |

The query context matches those records: source bundle
`98c273b3cc097f0d95adfba98ed7dfac0ac494dce9e779bb4b04fe79fef4f6aa`,
graph `44d8c7d33950af5e5f7c61caa4fe6fbd14fc9aedf14218d0a11de7c705542e09`,
authority extension
`833acc5988761f8ba68ca573ad270bf7c87cf2fe32061336a71e42647968630a`.
The source statements constrain this decision; their support classification must
not be promoted to a proof that they already selected it.

Before this decision, the [paper](../drafts/2026-09-GRC-V4.md), §12 and E.11,
required typed ordered crossings and readmission. The
[V4 interface](../../../../specs/grc-common-interface-v4-ext.md) declared
`parent_receipt_ids` and receipt → commit → envelope hashing but did not select
the parent rule. The [generic spec](../../../../specs/grc-v4-spec.md) required
an ordered owned ledger, reset/rebase appends and preserved copies.
Those linked documents now also contain this decision's accepted successor rule.
The [P9-2.4 review](../../../phase-9-grcv4/tranche-2/P9-2.4-Review.md) explicitly
deferred parent semantics; [P9-4.7a](../../../phase-9-grcv4/tranche-4/P9-4.7a-Review.md)
accepted only the tested local convention. No unrelated D10/D11 claim is reopened.

## Alternatives considered

| Alternative | Consequence | Recommendation |
| --- | --- | --- |
| Predecessor ordinary-primary/latest-primary split | Ordinary steps skip intervening administrative/crossing commits; the first ordinary step after an initial reset has no parent despite a nonempty ledger. This is tested local behavior, not proved incorrect physics. | Replace for new conformance: two meanings of “parent” are unnecessary when the intended relation is ledger ancestry. |
| Intra-commit parents only | Can order receipts inside a transaction but does not link successful operations. Commit membership already supplies the intra-operation relation. | Do not select as ledger ancestry. |
| Every earlier receipt as a parent | Repeats transitive ancestry with growing parent lists and additional ordering choices. | No demonstrated need for this closure. |
| Previous successful primary for all emitted receipts | One exact predecessor, includes all successful lifecycle operations, constant parent-list size and no same-commit dependency. | Selected by user acceptance on 2026-09-09. |

These are design tradeoffs, not rejected scientific claims. The decision
adds a specified ledger relation; it does not assert uniqueness from GRC axioms.

## Accepted contract

1. **Owned sequence.** Partition the persistent successful-receipt ledger into
   ordered committed-operation groups using the commit preimages and their
   ordered `emitted_receipt_ids`. Each group is nonempty, has exactly one
   operation-primary receipt first, and contains no duplicate receipt ID locally
   or elsewhere in that ledger. For the C_OS scope, primaries are step-commit,
   reset, rebase, profile-migration or topology-event receipts. Auxiliary charge
   and history receipts are not primaries. This rule does not impose four
   receipts on every future profile; operation-specific contracts own the group.
2. **Exact parents.** Let `p[k]` be group `k`'s primary receipt ID. For every
   receipt `r` in that group:

   ```text
   r.core.parent_receipt_ids = ()          if k == 0
                            = (p[k-1],)   otherwise
   ```

   All auxiliaries share that tuple. A parent is historical and belongs to the
   immediately preceding group, never the current group. There is no caller-
   selectable parent, lexicographic sorting, multi-parent choice or same-commit
   edge. A reordered two-parent tuple is invalid by cardinality, not an example
   of two valid alternative orders. Reordering commit groups is also invalid
   unless the resulting records independently satisfy every admission contract.
3. **What advances the head.** Every successful operation above advances it,
   including a successful zero-duration step or a reset with unchanged C. Clock
   equality does not mean “no commit.” Rejected operations and exceptions leave
   the head/ledger unchanged; returned failure receipts never enter this chain.
   Save, snapshot, load, duplicate, observations and lawful unreceipted
   `set_state` add no operation and do not advance the head.
4. **Scope and forks.** The head comes from the owned ledger, not the current
   graph's live vertices, a process-global counter or an external lookup. A
   migration/event preserves the prefix across graph/profile changes. Restore
   and duplicate preserve IDs and order without regenerating receipts. Copies
   may share an identical prefix and later diverge; the same content ID in a
   shared prefix is not “foreign” merely because another instance also has it.
   Merging unrelated ledgers is not authorized by a graph merge or state copy.
5. **Validation.** Before publication or restored state becomes observable,
   validate content IDs, commit membership/backlinks, primary kinds, full ordered
   partition, uniqueness and the exact tuple above. Missing, skipped, foreign,
   forward, self, cyclic, duplicate, auxiliary-as-parent or extra parents reject.
   Check every auxiliary, not just the primary. Constructors and content-only
   comparators do not become lineage validators; the lifecycle owner enforces
   this with existing atomic publication. Malformed restoration raises the
   existing restoration/identity error at its API boundary; programmer faults
   during live construction preserve the entire prestate. Do not invent a
   solver failure for a receipt failure.
6. **Claim ceiling.** Parent rank strictly decreases by one group on each edge,
   so valid finite projections are acyclic. Primary receipts form one chain;
   auxiliary receipts link to its prior head. The first group's auxiliaries also
   have no parents: group membership, not a fictitious intra-commit edge, binds
   them to the root operation. This is ledger ancestry, not a proof of every
   physical cause, lossless history transport, or uninterrupted state evolution.
   In particular, the next commit's source need not equal the previous target
   when a lawful unreceipted assignment intervenes. Do not erase that operation
   or fabricate a receipt to make a stronger trajectory claim.
7. **Trust ceiling.** A coherent rewrite of the entire ledger can satisfy local
   structure with different content identities. Detecting substitution of an
   accepted run requires its retained external source/output identities; this
   rule is not a signature or hostile-interpreter attestation. Conversely, a
   correctly rehashed record that violates the parent rule must still reject.

## Observable change and compatibility

The following labels denote operation roles, not literal content hashes:

| Operation | Current local parent | Proposed parent |
| --- | --- | --- |
| first step `s0` | none | none |
| reset `r1` | `s0` | `s0` |
| rebase `b2` | `r1` | `r1` |
| step `s3` | `s0` | `b2` |
| migration `m4` | `s3` | `s3` |
| step `s5` | `s3` | `m4` |

After adoption, affected receipt IDs, commit IDs and lifecycle-envelope digests
change, including downstream identities. For identical scientific operations,
this parent change does not change the scientific-state/reset/event preimages
or numerical equations. Historical runs and receipts must not be rehashed or
relabeled as executions of the new rule.

The first public implementation must declare this fixed parent policy in its
versioned snapshot admission contract, bound to the admitted V4 release, not
guess it from whichever shape happens to validate. The internal
`pygrc-c-os-snapshot-v1/v2` conventions remain historical. No implicit conversion
or fallback to the old parent rule is authorized. Unless an explicit historical
reader is separately provided, reject those older layouts clearly; their
accepted executions remain reproducible through the recorded Git sources.
This does not request a new legacy-reader project, global ID registry, ledger
archive, or change to GRC9V3. The public envelope details belong to the facade
integration after this authority decision, with the policy boundary explicit.

## Design pressure and subsequent runtime tests

The small [symbolic checker](../../../phase-9-grcv4/verification/check_p9492_parent_proposal.py)
tests the parent projection only. Its labels are not hashes, and its valid commit
groups are assumptions: it cannot certify scientific truth, receipt typing,
real atomicity, snapshots or production conformance. Run from the repository root:

```sh
.venv/bin/python implementation/phase-9-grcv4/verification/check_p9492_parent_proposal.py
```

It covers empty/root, administrative-first, interleaved, crossing, zero-duration
and shared-prefix copies/forks, plus malformed parent/ledger projections. The
rank-decrease argument above supplies the general acyclicity reasoning; finite
examples alone do not establish a theorem or justify the policy choice.
The design check passed: 9 valid symbolic cases and 16 rejected mutations,
with zero runtime executions and no hash/atomicity or authority-acceptance claim.

After acceptance, reuse and extend the
[lifecycle tests](../../../../tests/models/test_grc_v4_lifecycle.py):

- update the interleaved parent expectations and second-beat receipt checks;
- add initial reset/rebase followed by the first ordinary step, and step after
  migration/event, including zero-duration successes and failed operations;
- mutate real receipts, coherently recompute their IDs and containing commit/
  envelope identities, and require rejection for each malformed projection;
- verify auxiliaries, duplicate groups, reordered groups, strict prefix ownership,
  shared-prefix duplicates, restoration, assignment and future replay;
- preserve scientific state and the full publication tuple on rejected input or
  injected prepublication faults; keep content-only foundation credit separate;
- bind new exact-profile results and identities at P9-4.9.3/4.8B. No changed
  parent test or symbolic pass can grant G2 or all-profile conformance.

## Acceptance and propagation

User acceptance of the design decision is recorded above. Next, record the
bounded successor contract and its debt/claim routing without
rewriting D10/D11; admit the new source through the side tool so paper checks can
consume it. Admission must preserve the historical D10/D11 graph and expose the
new contract through the existing forensic queries and affected notebook/browser
projections, with design acceptance distinct from pending propagation/runtime
verification. The symbolic checker does not evaluate or grant human acceptance.
Propagate the accepted clause through proposal, reviewed paper and
V4 specification successor release. Only then implement the corresponding
receipt rule with the facade/gap corrections. Keep one current verification
path and preserve historical checkers for their historical source.

The authority choice is accepted; the full obligation is not closed by that
decision alone. P9-4.9.2 completion also needs aligned paper/specification and
runtime conformance evidence. P9-4.8B remains the single integrated G2 decision.
