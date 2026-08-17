# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 117

**Status:** Round-four R4-B01 corrected author-side; full independent re-audit
pending

**Checkpoint commit:** `976c660`

**Independent-audit disposition:** `reject_pending_correction`

## Purpose

Iteration 117 reopens the Iteration 112-116 tranche against the independent
adversarial audit. The checkpoint preserves the exact audited implementation;
it is not an acceptance commit. No closeout or maximum claim is current until
the blocker and major findings are corrected and independently replayed.

The second independent audit closed B-01, B-02, B-05, B-06, and M-01, partially
closed B-03 and B-04, and reported three new blocker IDs: R2-B01 for missing
non-explicit composition object flow, R2-B02 for metadata-only candidate use
and invalid-relabel paraphrases, and R2-B03 for incomplete claim-envelope
canonicalization. The sections below retain the first-round correction record;
the round-two correction ledger follows it.

## Correction Contract

| Finding | Required correction | Acceptance evidence |
| --- | --- | --- |
| B-01 | Scope every receipt to invocations observed through its frozen binding surface. State that the binding plane cannot establish whole-run closure or the absence of external/untracked causal work. Never let an unbound call appear among qualified invocation evidence. | Mixed bound/direct execution remains explicitly operation-scoped and cannot qualify the direct operation or a whole-run claim. |
| B-02 | Resolve and fingerprint the concrete callable at link time, freeze that identity, and re-resolve it immediately before invocation. Reject changed qualified names, definitions, bound owners, or source fingerprints before delegation. | Post-load P1-to-P2 substitution and post-lock target substitution both fail before execution; receipts retain the actual verified identity. |
| B-03 | Require composition-specific crossing evidence, including the registered adapter/producer where applicable. Endpoint returns alone cannot exercise an edge. | CMP-26 cannot be receipted as exercised without the real adapter crossing. |
| B-04 | Replace candidate string-only use attestation with executable or content-addressed evidence and reject known invalid-relabel restatements without a distinct mechanism. | Declaration alone and arbitrary strings stay unqualified; invalid relabel laundering fails. |
| B-05 | Associate runtime choice with an explicit alternative-set scope and reject a choice outside that scope while permitting unrelated bindings outside it. | A/B selection records A or B; C in the same selection scope fails closed. |
| B-06 | Separate self-consistency from acceptance. Accepted claim artifacts require a trusted binding-map/source anchor supplied independently of the candidate bundle. | Coordinated map/policy or false-revision edits remain pending review without the external anchor. |
| M-01 | Separate invocation/return from mechanism-specific committed, rejected, no-op, and unknown effect outcomes. | A non-raising return cannot imply committed causal work without an explicit outcome contract. |
| N-01 | Keep closeout and reference language within demonstrated semantics. | Final documentation names operation scope and every remaining limitation. |

## B-01 Receipt Semantics

The binding plane is an operation-scoped linker, not a process-wide tracer.
An accepted receipt therefore proves only the identities and outcomes of the
invocations serialized in `actual_stage_symbol_invocations`.

Every lock and receipt must carry:

```text
claim_scope = bound_invocations_only
whole_run_causal_closure_claimed = false
untracked_execution_observable_by_binding_plane = false
```

Every receipt must additionally state that external or untracked causal input
is `not_observable_by_binding_plane`. A positive `claim_qualified` value is
limited to the recorded bound invocations. It cannot qualify a final runtime
state, a direct call, or all causal work performed by the consumer.

This boundary preserves backward-compatible direct execution without
pretending that the binding layer observed it.

## B-02 Callable Identity

For each linked symbol the lock freezes a callable-identity record containing:

```text
module
qualified symbol
source path and full-file SHA-256
definition first line
definition-source SHA-256
callable-identity digest
```

The wrapper re-resolves the registered symbol immediately before each call and
compares the current definition and bound owner with the frozen target. Any
identity drift raises `SymbolBindingError` before the target executes. The
receipt copies the verified identity into the invocation record so the
conformance checker can compare it with the exact locked link.

## B-03 Composition Crossing Evidence

A registered composition is exercised only by a completed
`composition.evidence_scope()` witness. The witness requires every matrix
source stage to produce a claim-qualifying effect before every matrix target
stage does. Endpoint calls outside
that scope remain pathway invocation evidence but cannot synthesize a
composition edge, adapter/producer cut, or composition claim ceiling.

CMP-26 additionally freezes the exact
`build_lgrc9v3_corrected_cascade_runtime(...)` callable. Its source-stage
handles must use the exact GRC instance declared as the adapter input, while
its target-stage handles use the adapter's deferred result reference. The real
adapter must produce a claim-qualifying effect between the source and target
stages. The receipt records
the crossing callable identity, global execution order, and endpoint/crossing
indices; the conformance checker reconstructs and validates that ordering.

The correction therefore rejects all three forms of the audit falsifier:

- endpoint co-use outside a composition scope forms no edge;
- CMP-26 cannot freeze with a missing crossing or unrelated target instance;
- a receipt with a removed or substituted CMP-26 adapter invocation fails
  conformance.

## B-04 Candidate Mechanism Evidence

Candidate declaration remains open and non-promoting, but declaration is not
use. A candidate can enter a receipt only when its lock freezes a repository-
relative content-addressed JSON mechanism artifact and one completed
`candidate.evidence_scope()` observes claim-qualifying effects through the declared
constituent bindings. Composition candidates require all observed source calls
before all observed target calls. Ordinary endpoint co-use outside this scope
does not exercise the candidate.

`record_candidate_use(...)` accepts only the candidate identity. It re-hashes
and re-validates the frozen artifact and derives invocation indices from the
completed scope; it no longer accepts a caller-authored evidence-reference
string. The receipt and graph retain the exact artifact identity, candidate
scope, binding identities, invocation indices, and ordering rule. BCF-004
independently reconstructs that evidence from current repository content and
the receipted invocation records.

Composition-candidate declarations are also compared with every registered
`invalid_relabel` row sharing the same ordered endpoints. Known blocked-relabel
vocabulary is rejected even under a new candidate ID. A genuinely different
relation over that endpoint pair must disclose the conflicting row and supply
a distinct content-addressed mechanism; BCF-011 independently repeats those
checks. The CMP-05 `diagnostic_as_behavior`/`native packet admission`
restatement therefore fails at declaration and in forged artifacts.

## B-05 Selection-Scoped Dynamic Alternatives

An alternatives declaration still performs no semantic selection. After the
lock, the consumer opens `alternatives.selection_scope()` around one runtime
decision. The first bound pathway call in that scope fixes the selected member.
A call to a pathway outside the declared set, or to a second distinct member in
the same scope, raises `BindingStateError` before callable resolution or
delegation. An empty, interrupted, or rejected scope cannot be sealed into a
receipt.

Successful receipts tag every scoped invocation with its exact selection-scope
identity and record the alternative set, selection authority, consumer-owned
selected pathway, invocation indices, returned-invocation indices, and
claim-qualifying invocation indices. BCF-017
reconstructs each witness and requires complete equality with the invocation
records. A scoped invocation omitted from its witness, a forged C choice, or a
scope spanning both A and B fails conformance.

The constraint is deliberately local. A bound C call outside the A/B scope is
ordinary unrelated work and retains a null alternative-scope identity. The
I116 dynamic fixture executes such a GRC call before selecting the restoration
branch, proving both the rejection and non-interference boundaries without
claiming that the binder made the choice.

## B-06 Independent Binding Acceptance

Authority loading now separates internal consistency from acceptance. A
binding map can be loaded without an acceptance anchor for inspection, but its
status is `pending_independent_review`; `freeze_lock()` fails before producing
a claim-bearing artifact. An accepted load requires two caller-supplied inputs:

```text
acceptance anchor record
expected SHA-256 of that exact anchor from an independent trust source
```

Neither input is auto-discovered by the runtime or checker. The anchor pins the
binding-map digest, declared source revision, a canonical stage/crossing
semantic projection, and a canonical manifest of source paths and content
hashes. Its `automatic_re_admission` field is false. Accepted locks and
receipts retain both `binding_acceptance_status = accepted` and the trusted
anchor digest. The anchor also carries the exact-symbol effect contracts used
by M-01 and a digest over that contract set.

BCF-014 independently repeats the anchor validation. A missing external anchor
blocks current-looking artifacts as `stale_pending_review`. The focused
controls also recompute the binding-map digest and binding-policy digest after
(1) changing packet scheduling to `LGRC9V3.step` and (2) substituting an
all-zero source revision. Both coordinated candidates remain pending because
they cannot change the independently supplied anchor or its trusted digest.

## M-01 Effect Outcome Contracts

Invocation transport and causal effect are now separate receipt facts. A
wrapper still records whether the callable `returned` or `raised`, but actual
pathway use, composition/candidate witnesses, dynamic actual-use summaries,
the use graph, and `claim_qualified` depend only on a trusted effect outcome.

The independently supplied acceptance anchor carries exact-symbol contracts
with the closed vocabulary:

```text
committed
observed
rejected
no_op
unknown
```

Only `committed` and `observed` may qualify. Stable Python return categories
(`false`, `true`, `none`, `empty`, and `other`) have no generic truthiness
meaning; each reviewed symbol maps them explicitly. An exact symbol without a
reviewed contract returns `unknown` and stays non-qualifying. Producer result
objects additionally use a contract-pinned `state_mutated` boolean probe, so a
normal “no eligible work” result becomes `no_op`, not committed work. The
guarded front-propagation mutator pins canonical pre/post `snapshot()` digests;
an unchanged `None` return is therefore `no_op`, while only a changed snapshot
is `committed`.

Locks freeze each symbol's exact contract or an explicit null for an unreviewed
symbol. Receipts record return category, contract identity, effect kind,
outcome, qualifying flag, optional probe evidence, and aggregate outcome
counts. BCF-020 reconstructs those fields from the trusted anchor, verifies
the lock copy and receipt summary, and derives actual use from qualifying
effects rather than non-raising returns.

The focused controls cover the audit's controlled `False` return, an empty
commit result, a producer result with `state_mutated = false`, a guarded `None`
return with an unchanged bound-instance snapshot, an unreviewed symbol return,
and forged `False`/`no_op`/`unknown` receipt claims. None can become actual or
claim-qualified use.

## Verification Gate

Iteration 117 remains open until repository tests and the independent
falsifiers agree. Commands use `.venv`; tool and dependency configuration
comes from `pyproject.toml`.

The completed focused slices closed B-01 through B-06 and M-01 at the author
implementation gate. The second full independent revision then returned
`reject_pending_correction`. This is not an acceptance result; another full
independent revision remains required after all round-two blockers close.

## First-Slice Verification

```text
.venv focused binding/conformance/replay/import tests = 32 passed
.venv full unittest discovery = 1,242 passed
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

The exact independent P1-wrapper-to-P2 substitution now passes its falsifier.
The direct-method, imported-alias, and exposed-bound-object mixed-use cases
also pass the audit's stated operation-scope criterion. The producer-plus-
direct-packet case in the original harness still tests invalidation only and
does not apply its sibling cases' explicit-scope alternative. That predicate
must be aligned before the independent suite can report the B-01 correction
consistently; the implementation does not write a false undeclared-use
violation merely to satisfy the inconsistent predicate.

## B-03 Focused Verification

```text
.venv focused binding and conformance tests = 35 passed
CMP-26 real adapter/dataflow dry run = passed
I116 consumer dry runs and low-context replay = passed
binding conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
compileall selected changed surfaces = passed
```

This is author-side focused correction evidence, not the deferred second full
independent revision and not final tranche acceptance.

## B-04 Focused Verification

The B-04 gate covers declaration-only, legacy arbitrary-string, unscoped
endpoint co-use, stale/mismatched content evidence, renamed CMP-05 relabel,
and conformance-witness mutation controls. The I116 candidate dry run freezes
the mechanism artifact and source-before-target invocation witness.

```text
.venv focused binding/conformance/replay tests = 45 passed
.venv full unittest discovery = 1,256 passed
I115/I116 evidence regeneration = passed
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
```

This is author-side focused correction evidence; the full independent revision
remains deferred until B-06 and M-01 are complete.

## B-05 Focused Verification

The B-05 gate covers A or B selection, C rejection inside A/B, a second branch
in one scope, incomplete/rejected scopes, forged C witnesses, removed scope
tags, and unrelated C use outside the scope. The I116 dynamic dry run retains
the exact consumer-owned selection witness and the unrelated null-scoped
invocation.

```text
.venv focused binding/conformance/replay tests = 49 passed
.venv full unittest discovery = 1,260 passed
I115/I116 evidence regeneration = passed
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

This remains author-side correction evidence, not the deferred full independent
revision.

## B-06 Focused Verification

The B-06 gate covers an accepted external anchor, a self-consistent but
unanchored authority, a wrong trusted anchor digest, coordinated binding-map
and policy changes, a false source revision, and exact anchor identity in locks
and receipts. The I115 negative-control record includes both coordinated
mutation cases and requires each to fail BCF-014 in isolation as
`stale_pending_review`.

```text
.venv focused binding/conformance tests = 53 passed
.venv full unittest discovery = 1,267 passed
I115 independent-anchor mutation controls = 2 passed, 0 failed open
I115/I116 evidence regeneration with caller-supplied trust root = passed
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

This remains author-side correction evidence. The deferred full independent
revision remains open.

## M-01 Focused Verification

The M-01 gate covers real committed/observed effects, exceptions, controlled
`False`, empty/no-op returns, producer mutation probes, unreviewed symbols,
contract drift, summary drift, and forged claim-qualifying outcomes. I115 adds
three BCF-020-only effect forgery controls, all of which fail closed.

```text
.venv focused binding/conformance/replay tests = 62 passed
.venv full unittest discovery = 1,273 passed
I115 effect-outcome mutation controls = 3 passed, 0 failed open
I115/I116 evidence regeneration with trusted outcome contracts = passed
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

This is author-side correction evidence only. The full independent revision
that followed rejected the candidate on R2-B01, R2-B02, and R2-B03.

## Round-Two Re-Audit Result

The independent round-two audit executed 40 cases: 34 passed, six failed their
criterion, and none errored. It recorded three blocker classes and no separate
major or minor findings:

```text
R2-B01 non-explicit composition edge lacks runtime dataflow closure
R2-B02 candidate use remains self-attestable and relabels paraphraseable
R2-B03 checker does not canonicalize the complete claim envelope
disposition = reject_pending_correction
```

## R2-B01 Runtime Dataflow Closure

R2-B01 is corrected author-side by making runtime flow an explicit frozen
composition obligation. CMP-26 continues to require the exact declared adapter
source and deferred adapter-result reference. Every other executable status
requires at least one claim-qualifying source invocation and one
claim-qualifying target invocation bound to the exact same direct Python
runtime object. Locks serialize a deterministic session-local owner identity;
witnesses cite the exact invocation pair, symbols, and owner identity; BCF-019
reconstructs the relation from the locked links and receipt records.

The rule is conservative. If direct object continuity is not observable, the
composition is not exercised: no witness, graph edge, composition ceiling, or
cut is emitted. The audited CMP-04 falsifier now returns LGRC runtime A from
`prepare_lgrc9v3_grc9v3_diagnostics(...)`, invokes diagnostic rebuild on
unrelated GRC runtime B, and leaves CMP-04 declared-but-unused. The existing
CMP-04 I116 case is frozen with the same honest zero-edge result because its
former target was also unrelated. CMP-20 remains positive because its producer
and packet stages act on one exact LGRC runtime.

The runtime controls cover CMP-04 on unrelated endpoints and CMP-20 on two
distinct owners. A digest-resealed BCF-019 control forges the positive CMP-20
owner identity and fails closed. Frozen I116 assertions record the positive
CMP-20 flow identity and the negative CMP-04 witness/edge counts.

```text
.venv focused binding/conformance/I116 tests = 65 passed
.venv full unittest discovery = 1,276 passed
I115/I116 evidence regeneration = passed
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

This is author-side correction evidence only. The following R2-B02 correction
does not close R2-B03, and a new full independent audit remains the acceptance
gate.

## R2-B02 Candidate-Specific Executable Provenance

R2-B02 is corrected author-side by replacing metadata-only candidate
attestation with one exact candidate-specific executable. The version-2
candidate artifact names a repository-relative module function, source
SHA-256, mechanism ID, candidate shape, endpoints, and supported relation. The
binder resolves the function directly from the pinned source, freezes its
definition-level callable identity, and rejects any callable already registered
as an admitted stage or crossing. Both the JSON artifact and executable source
are revalidated at use and receipt time.

Every exercised candidate now has exactly one returned candidate-mechanism
invocation inside its completed evidence scope. For a composition candidate,
the checker reconstructs the stricter event order:

```text
all qualifying source calls
< exact candidate mechanism call
< all qualifying target calls
```

The receipt retains that invocation separately from admitted effect evidence.
Its return proves execution of the identity-verified experimental mechanism;
it does not imply an admitted `committed` or `observed` effect contract.
Removing the invocation or substituting a forged executable identity fails
BCF-004 even when both admitted endpoint calls remain.

The invalid-row boundary is structural as well as lexical. Every matching
`invalid_relabel` ID and every blocked relabel from those rows is copied into
the candidate declaration, lock, receipt, graph node, and graph edge. A
proposed relation is rejected when it is a literal restatement or preserves
the load-bearing semantic tokens of a blocked relabel. Any permitted relation
prose is marked `descriptive_unreviewed_not_claim_qualified`; it cannot replace
or weaken the structured blocks. The audited CMP-05 paraphrase is rejected,
while a separate positive control remains usable only with a distinct
executable crossing and retains both CMP-05 blocked relabels.

```text
.venv focused binding/conformance/I116 tests = 72 passed
.venv full unittest discovery = 1,283 passed
I115/I116 evidence regeneration = passed
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

At this checkpoint R2-B03 remained open. The following correction closes it
author-side; a new full independent audit remains the acceptance gate.

## R2-B03 Complete Claim-Envelope Canonicalization

R2-B03 is corrected author-side by making BCF-015 independently construct the
entire expected claim envelope. The lock derivation consumes current registry
and matrix authority plus exact declared pathway, composition, and candidate
records. The receipt derivation starts separately from claim-qualifying stage
invocations, composition witnesses that pass exact order/dataflow validation,
and candidate uses that pass exact executable-witness validation. Neither
derivation reads the submitted envelope to decide its expected claims.

The checker requires exact structural equality for:

- constituent pathway and composition ceilings;
- configured-semantics, producer, adapter, diagnostic, and candidate
  qualifiers;
- producer/adapter/diagnostic/candidate summary flags;
- aggregate blocked claims and overall claim status; and
- composition-maturity and synthesized-chain non-claim fields.

The lock's top-level blocked claims and explicit producer/adapter records, and
the receipt's blocked claims and used producer/adapter records, must match the
same canonical envelopes. Candidate and composition ordering is deterministic,
so list order cannot become an unchecked degree of freedom.

The controls reproduce the audit's digest-resealed diagnostic mutation
(`bounded_with_diagnostic_cut` to `admitted_bounded` with its diagnostic flag
cleared), mutate every top-level and qualifier lock/receipt envelope field
under target-only BCF-015, delete producer/adapter projections, and clear replay
blocked-claim aggregates. Nine varied I116 lock/receipt pairs remain positive
controls.

```text
.venv focused binding/conformance/I116 tests = 77 passed
.venv full unittest discovery = 1,288 passed
I115/I116 evidence regeneration = passed
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

This remains author-side correction evidence only. All reported round-two
blockers are now corrected author-side; the new full independent audit remains
the acceptance gate.

## Round-Three Independent Audit Disposition

The round-three independent audit reviewed checkpoint
`a77f669b5b340facd2869e2b70c40143fbfbdba1` and returned
`reject_pending_correction`. Its 44-case independent suite reported 41 passing
criteria, three failures, and no errors:

```text
R3-B01 coherently resealed shared-instance composition forgery = blocker
R3-B02 synonym-renamed invalid relation plus no-op candidate = blocker
R3-M01 six structurally unwitnessable registered rows = major
prior complete claim-envelope blocker = independently closed
```

The first round-three correction slice closed R3-B01 and R3-M01 author-side
together. The following R3-B02 slice closes the remaining reported finding
author-side. No round-three acceptance is claimed before another full
independent audit completes.

## R3-B01 Independently Trusted Execution Transcript

The serialized `session-instance:N` label is retained as a lock-local
declaration aid but no longer proves runtime continuity. Every invocation now
records raw live-object descriptors for its receiver, receiver state and base
state, named arguments, result, and result state and base state. The receipt
separately computes `execution_transcript_digest` from only:

```text
binding_lock_digest
actual_stage_symbol_invocations
actual_composition_crossing_invocations
actual_candidate_mechanism_invocations
```

Derived composition witnesses, graph edges, exercised projections, claim
envelopes, and the receipt digest are outside this transcript digest. Locks and
receipts freeze
`externally_supplied_digest_for_registered_composition_or_reviewed_candidate`
as the trust requirement. BCF-019 independently recomputes the raw transcript
digest and accepts a registered witness only when the caller also supplies the
exact trusted digest through a separate checker argument. The R3-B02
correction applies that same external transcript requirement to reviewed
invalid-pair candidate witnesses. A digest read from the submitted receipt
proves only self-consistency and is not an independent trust source.

The focused falsifier changes CMP-20's target lock and actual-use owner from
`session-instance:1` to `session-instance:0`, changes the target raw object ID
to the source object ID, and reseals the lock, transcript, receipt, witness,
and projections. The rewritten candidate cannot reuse the trusted digest of
the distinct-object execution and fails BCF-019. Missing external transcript
trust also fails BCF-019 even for an otherwise canonical registered edge.

## R3-M01 Per-Composition Dataflow Contracts

The policy, lock, library, and checker now freeze and independently derive an
exact stage/port contract for every executable composition. The six rows that
cannot use the default receiver-to-receiver identity predicate are:

| Row | Source flow port | Target flow port | Continuity |
| --- | --- | --- | --- |
| CMP-01 | `transport_rebuild argument:state` | `continuity_and_invariants receiver_state` | exact object identity |
| CMP-02 | `source_debit argument:state` | `target_credit argument:state` | exact object identity |
| CMP-03 | `transport_rebuild argument:state` | `packet_schedule receiver_base_state` | exact object identity |
| CMP-04 | `diagnostic_model_construction result_base_state` | `diagnostic_rebuild receiver_state` | consumer-bound equivalent-state copy |
| CMP-17 | `assemble_causal_annotation result` | `transport_rebuild argument:evolution` | exact object identity |
| CMP-21 | `target_credit result` | `surface_row_emission argument:processing_result` | exact object identity |

Static checker and library controls inventory all 17 executable rows and fail
if either endpoint port is not representable by the binding map's actual call
shape. CMP-02 supplies an exercised module-argument positive control.

CMP-04 additionally exposes `flow_derived_target_instance(source=...)`. The
consumer declares this reference and target handle before lock, invokes the
diagnostic construction source inside the composition scope, constructs the
GRC diagnostic target itself, then explicitly binds the exact source return to
the target. The reference verifies the live source result, source and target
state fingerprints, active scope, and invocation cardinality before target
delegation. The raw target invocation records the derivation. The binder does
not construct, select, or invoke the diagnostic target for the consumer.
Wrong-return and distinct-carrier controls fail before delegation; the I116
CMP-04 dry run now emits one diagnostic-only registered edge and remains under
its matrix claim ceiling.

## R3-B02 Independently Reviewed Candidate Distinction

R3-B02 is corrected author-side by separating relation prose and executable
novelty from an accepted structural distinction. Any composition candidate
whose ordered endpoints conflict with an `invalid_relabel` row must supply a
`causal_pathway_candidate_relation_review_v1` record and the expected digest
of that exact record through caller-controlled trust configuration. The
review binds all load-bearing facts:

```text
candidate ID and kind
source and target pathway IDs
proposed relation
invalid-row IDs and blocked relabels
candidate mechanism ID, artifact path, and SHA-256
reviewed structural-distinction contract
```

The record cannot be self-trusting: the binder compares it with the separately
supplied expected digest, and BCF-011 requires its digest in the checker's
external trusted-review set. A review on a non-conflicting endpoint pair is
also rejected. Structured invalid-row blocks remain in the declaration,
receipt, claim envelope, graph node or edge, and cannot be displaced by the
review.

The reviewed structural contract requires the candidate callable to consume
the source result and produce a distinct nonempty mapping that supplies the
follow-on request. Runtime invocation records freeze the review digest and a
`structural_result_observed` predicate. Only a distinct nonempty mapping can
set that predicate; a returned `None`, pass-through object, scalar, empty
mapping, or raised call cannot yield a candidate-use witness. The checker also
parses the content-addressed executable source and requires the narrow
nonempty-mapping return structure rather than trusting the receipted flag.
Finally, a reviewed candidate edge requires the independently supplied digest
of its raw lock-linked execution transcript.

The exact audit falsifier is frozen as
`forensic reconstruction dictates routine packet conduct` backed by a
distinct synchronous function whose body returns `None`. Declaration without
an independent review fails. Even with a coherent review, a forged positive
structural flag, a recomputed transcript, fully resealed lock and receipt, and
both external digest arguments supplied, BCF-011 rejects the no-op executable
and no experimental edge is accepted. A positive CMP-05-endpoint control uses
a separately reviewed executable that returns a distinct packet-request
mapping and retains both CMP-05 blocked relabels.

## Round-Three Author-Side Verification

```text
.venv focused binding/conformance/I116 tests = 84 passed
.venv full unittest discovery = 1,295 passed
I115/I116 evidence regeneration = passed
I116 checker-evaluated consumer cases = 8 passed, 0 issues
binding conformance (I115, CMP-20, CMP-04) = 20 passed, 0 issues each
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

These results cover the R3-B01/R3-M01 slice. The R3-B02 verification below
supersedes the open-finding statement; the full independent re-audit remains
pending.

## R3-B02 Author-Side Verification

The final author-side gate reproduces both the runtime and checker forms of the
synonym/no-op falsifier. It also covers missing review, a self-issued review
digest, reviewed positive mapping flow, graph review retention, and the
ordinary non-conflicting candidate path.

```text
.venv focused binding/conformance/I116 tests = 88 passed
.venv full unittest discovery = 1,299 passed
I115/I116 evidence regeneration = passed
I116 checker-evaluated consumer cases = 10 passed, 0 issues
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

These results are author-side correction evidence only. All round-three
findings are corrected author-side; a new full independent audit remains the
acceptance gate.

## Round-Four Disposition And R4-B01 Correction

The round-four independent audit returned `reject_pending_correction` with one
remaining blocker. A reviewed candidate could return a valid mapping, the
consumer could ignore that mapping and call the target with equivalent
hard-coded arguments, and the runtime and checker still emitted and accepted
the experimental edge. The flowed and ignored cases had identical trusted raw
transcript digests. The audit independently confirmed R3-B01, R3-B02, R3-M01,
and the complete claim-envelope correction as closed.

R4-B01 is corrected author-side by replacing the candidate witness's
order-and-shape inference with an exact three-event dataflow proof:

```text
qualifying source result object
  -> exact candidate argument descriptor
  -> distinct provenance-carrying candidate result mapping
  -> exact expanded target keyword request
  -> qualifying declared target invocation
```

The reviewed candidate handle snapshots its nonempty JSON result in a
read-only mapping. Integer, float, and string request leaves retain unique
request-local identity when expanded as keywords; nested request mappings
retain the same root candidate identity and an explicit path. This preserves
the established `target(**request)` consumer form without adding semantic
selection or a generic dispatcher. Boolean or null request leaves cannot be
used as identity evidence because their process-wide singleton identities are
not provenance-bearing.

Raw candidate invocation records now include the same receiver/argument/result
object-flow schema used for admitted stage calls. Raw target invocation records
include `candidate_request_flow` only after the runtime matches the complete
keyword request to one exact candidate-result mapping or nested submapping.
That record freezes the candidate scope and mechanism index, candidate-result
descriptor, request path, canonical request digest, and exact target binding,
pathway, and symbol. It is part of the separately digested raw transcript.

The runtime will not create a reviewed candidate-use witness unless one
qualifying source result is the candidate input and one qualifying target
invocation carries the exact request-flow record for that candidate result.
The checker independently reconstructs those links and exact invocation
indices before retaining the candidate use or graph edge. A hard-coded target
call therefore remains valid pathway work but cannot qualify the reviewed
candidate relation. Removing the raw request flow and coherently resealing the
receipt also fails closed even when the new transcript and review digests are
supplied through the explicit trust inputs.

## R4-B01 Author-Side Verification

The focused controls reproduce both audited executions: the flowed mapping
produces a checker-accepted raw dataflow witness, while the distinct mapping
followed by equivalent hard-coded target arguments has no request-flow record
and cannot be recorded as candidate use. A separately resealed checker control
removes the raw target-request flow from the positive bundle and fails closed
even when the recomputed transcript digest and candidate-review digest are
explicitly trusted.

```text
.venv focused binding/conformance/I116 tests = 90 passed
.venv full unittest discovery = 1,301 passed
I115/I116 evidence regeneration = passed
I116 checker-evaluated consumer cases = 10 passed, 0 issues
binding conformance = 20 passed, 0 issues
predecessor consolidation conformance = 20 passed, 0 issues
ruff selected changed surfaces = passed
mypy --python-version 3.12 selected binding surfaces = passed
compileall selected changed surfaces = passed
git diff --check = passed
```

This is author-side correction evidence only. R4-B01 is corrected author-side;
a new full independent audit remains the acceptance gate.
