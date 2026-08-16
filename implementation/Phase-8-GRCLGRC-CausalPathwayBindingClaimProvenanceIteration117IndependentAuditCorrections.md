# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 117

**Status:** B-01/B-02/B-03/B-04 correction slices complete; tranche remains open

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

## Verification Gate

Iteration 117 remains open until repository tests and the independent
falsifiers agree. Commands use `.venv`; tool and dependency configuration
comes from `pyproject.toml`.

The completed focused slices close B-01 through B-04 at the implementation
gate. Findings B-05, B-06, and M-01 remain acceptance blockers and must
not be described as resolved. A second full independent revision is deferred
until B-06 and M-01 are complete.

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
