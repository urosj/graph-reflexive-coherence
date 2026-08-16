# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 117

**Status:** B-01/B-02/B-03/B-04/B-05/B-06 correction slices complete; tranche remains open

**Checkpoint commit:** `976c660`

**Independent-audit disposition:** `reject_pending_correction`

## Purpose

Iteration 117 reopens the Iteration 112-116 tranche against the independent
adversarial audit. The checkpoint preserves the exact audited implementation;
it is not an acceptance commit. No closeout or maximum claim is current until
the blocker and major findings are corrected and independently replayed.

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
source stage to return before every matrix target stage. Endpoint calls outside
that scope remain pathway invocation evidence but cannot synthesize a
composition edge, adapter/producer cut, or composition claim ceiling.

CMP-26 additionally freezes the exact
`build_lgrc9v3_corrected_cascade_runtime(...)` callable. Its source-stage
handles must use the exact GRC instance declared as the adapter input, while
its target-stage handles use the adapter's deferred result reference. The real
adapter must return between the source and target stages. The receipt records
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
`candidate.evidence_scope()` observes returned calls through the declared
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
selected pathway, invocation indices, and returned-invocation indices. BCF-017
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
anchor digest.

BCF-014 independently repeats the anchor validation. A missing external anchor
blocks current-looking artifacts as `stale_pending_review`. The focused
controls also recompute the binding-map digest and binding-policy digest after
(1) changing packet scheduling to `LGRC9V3.step` and (2) substituting an
all-zero source revision. Both coordinated candidates remain pending because
they cannot change the independently supplied anchor or its trusted digest.

## Verification Gate

Iteration 117 remains open until repository tests and the independent
falsifiers agree. Commands use `.venv`; tool and dependency configuration
comes from `pyproject.toml`.

The completed focused slices close B-01 through B-06 at the implementation
gate. Finding M-01 remains an acceptance blocker and must not be described as
resolved. A second full independent revision is deferred until M-01 is
complete, as agreed for the combined B-06/M-01 correction boundary.

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

This remains author-side correction evidence. M-01 and the deferred full
independent revision remain open.
