# GRC/LGRC Causal Pathway Bindings

**Status:** All round-two blockers corrected author-side; full independent
re-audit pending

**Machine map:** [`grc-lgrc-causal-pathway-bindings.json`](./grc-lgrc-causal-pathway-bindings.json)

## Purpose

The canonical pathway registry explains what each pathway and stage means. The
binding-symbol map separately explains how an evidence-bearing Python consumer
links that exact identity to the current implementation.

The separation is deliberate:

```text
registry fact != Python linkage fact
```

The map covers all 23 V1 pathways and all 52 authority-bearing stages. Each
stage records one or more exact modules, qualified symbols, call kinds, binding
roles, source paths, and source hashes. Shared symbols remain shared. A stage
with several load-bearing entrypoints retains all of them.

The map additionally closes the explicit-adapter crossing set. CMP-26 binds
`build_lgrc9v3_corrected_cascade_runtime(...)` as its exact composition
adapter; the map contains no generic crossing dispatcher.

## Binding Roles

- `mechanism_entrypoint` identifies an ordinary mechanism-specific public
  callable.
- `stage_entrypoint` identifies a stage-specific module function.
- `load_bearing_internal` records an exact internal stage when no public
  callable isolates that relation.
- `diagnostic_entrypoint` remains diagnostic.
- `producer_entrypoint` retains producer ownership.
- `restoration_entrypoint` remains bounded to restoration/replay identity.
- `composition_adapter_entrypoint` identifies an exact registered adapter
  callable that must execute between the composition's source and target
  stages.

Binding an internal symbol does not promote it to stable general-purpose API.
The map versions the exact source relation for claim provenance.

## Multiplexed Producer Entry Points

`LGRC9V3.produce_events(...)` is a mechanism-specific producer entrypoint used
by several admitted pathways. Those bindings carry an exact required `policy`
keyword. The verified callable refuses a mismatched policy before delegation,
so a feedback binding cannot silently execute the flux-route or surplus
producer.

## Non-Dispatch Rule

The binder imports the recorded callable, freezes a definition fingerprint,
re-resolves it immediately before every invocation, and delegates the caller's
native arguments unchanged. It does not expose `execute(pathway_id, **kwargs)`,
infer a pathway from intent, or translate arguments into common causal-work
fields.

Direct unbound calls remain available. They do not produce claim-qualified
binding invocation provenance. Receipts are scoped to bound invocations and do
not claim process-wide observation or whole-run causal closure.

## Composition Crossing Evidence

Returned endpoint stages do not by themselves establish a composition. A
consumer must run the required source and target stages inside one explicit
composition evidence scope and in matrix order, and every required invocation
must have a trusted claim-qualifying effect. Every non-explicit-adapter
composition additionally requires one qualifying source invocation and one
qualifying target invocation bound to the exact same direct runtime instance.
The lock assigns that owner a deterministic session-local identity, and the
receipt records the exact source/target invocation pair that shares it. If the
binding surface cannot prove this continuity, the composition remains
declared-but-unused and emits no graph edge or composition claim.

CMP-26 has the stronger explicit-adapter rule. Before lock, its source stages
must bind to the same declared GRC instance consumed by the adapter, and its
target stages must bind to the adapter's deferred LGRC result reference. The
real registered adapter must produce a claim-qualifying effect after all source
stages and before all target stages. Missing, substituted, out-of-order,
non-qualifying, or unrelated-instance crossings cannot form an exercised
composition edge.

This rule intentionally leaves CMP-04 unexercised with the current binding
surface. `prepare_lgrc9v3_grc9v3_diagnostics(...)` returns its LGRC input, but
the separately bound `GRC9V3.rebuild_transport_state()` owner is not that
object. Ordered calls on an unrelated GRC object therefore remain pathway
evidence only and cannot claim the diagnostic composition.

## Candidate Executable Provenance

An unregistered candidate is exercisable only when its declaration freezes a
version-2 candidate-mechanism artifact and one exact executable module
function. The artifact, executable source, definition fingerprint, and
callable identity are content-addressed and revalidated. A candidate callable
cannot alias an admitted stage or registered crossing callable.

The exact candidate mechanism must return once inside the completed candidate
evidence scope. For a composition candidate it must execute after every
qualifying source invocation and before every qualifying target invocation.
Metadata-only evidence and endpoint co-use cannot form a candidate graph
element. Candidate execution remains experimental and unregistered; it is not
an admitted effect contract.

For a candidate over an endpoint pair occupied by an `invalid_relabel` matrix
row, all conflicting IDs and blocked relabels remain structured prohibitions in
the lock and receipt. Literal and load-bearing-token restatements are rejected,
and the free-text proposed relation is explicitly descriptive, unreviewed, and
not claim-qualified.

## Complete Claim-Envelope Canonicalization

The binding checker independently derives the entire pre-execution and receipt
claim envelopes. Lock derivation uses current registry and matrix authority plus
the exact declared pathway, composition, and candidate records. Receipt
derivation uses qualifying stage invocations, validated composition witnesses,
and validated candidate-mechanism witnesses; it does not trust the submitted
claim envelope to decide what was used.

The submitted envelope must exactly equal the canonical structure, including
constituent ceilings, configured semantics, producer/adapter/diagnostic cuts,
candidate relations, every summary boolean, aggregate blocked claims, overall
claim status, and the maturity/chain non-synthesis fields. Lock and receipt
copies of aggregate blocks and producer/adapter cuts must match the same
derivation. Digest-resealed omissions or widenings therefore fail BCF-015.

## Effect Outcome Contracts

Invocation transport (`returned` or `raised`) is distinct from effect outcome.
The independently trusted binding-acceptance anchor pins exact-symbol mappings
to `committed`, `observed`, `rejected`, `no_op`, or `unknown`. Only committed
and observed effects count as actual use. `False`, empty, unreviewed, and
producer `state_mutated = false` results remain non-qualifying even though the
call returned normally. A guarded `None`-returning mutator may additionally
require a changed canonical bound-instance snapshot before it qualifies. Locks
freeze the applicable contract and receipts carry the classified outcome and
aggregate summary for BCF-020 reconstruction.

See the
[binding and claim-provenance reference guide](../docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md)
for lock, receipt, candidate, dynamic-choice, and conformance usage.
