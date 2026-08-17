# GRC/LGRC Causal Pathway Bindings

**Status:** Round-five R5-B01 corrected author-side; full independent re-audit
pending

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
must have a trusted claim-qualifying effect. Every non-explicit-adapter row
freezes its own source-stage/port to target-stage/port dataflow contract. Raw
invocation records expose receivers, arguments, results, and their established
state/base-state carriers. Most rows require exact live-object identity across
the two selected ports; module-function rows instead name the actual argument
or result port that carries their crossing.

CMP-04 uses a narrower consumer-bound equivalent-state-copy contract. Before
lock, the consumer declares a deferred target owner from the exact diagnostic
construction handle. Inside the evidence scope it invokes that source, creates
the GRC diagnostic target, and binds the target to the exact returned source
and equivalent source/target state fingerprints before invoking the target
stage. The binder observes and records this derivation but does not construct,
select, or dispatch the diagnostic mechanics. A wrong return, a distinct state
carrier, or an unresolved reference fails before target delegation.

The receipt's raw execution transcript is digested separately from its derived
witness, graph, and claim envelope. BCF-019 accepts a registered edge only when
the checker is given that digest from an independent trust source and it equals
the checker-recomputed digest of the lock-linked raw transcript. The receipt's
self-reported digest does not establish trust. A coherently resealed object-ID,
lock, witness, graph, and envelope rewrite therefore cannot reuse the original
trusted transcript identity.

CMP-26 has the stronger explicit-adapter rule. Before lock, its source stages
must bind to the same declared GRC instance consumed by the adapter, and its
target stages must bind to the adapter's deferred LGRC result reference. The
real registered adapter must produce a claim-qualifying effect after all source
stages and before all target stages. Missing, substituted, out-of-order,
non-qualifying, or unrelated-instance crossings cannot form an exercised
composition edge.

Ordered CMP-04 calls on an unrelated GRC object remain pathway evidence only
and cannot claim the diagnostic composition. The I116 diagnostic dry run uses
the consumer-bound derivation and now exercises CMP-04 without widening its
diagnostic-only ceiling.

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
the lock, receipt, and use graph. Literal and load-bearing-token restatements
are rejected, and the free-text proposed relation is explicitly descriptive,
unreviewed, and not claim-qualified. A remaining distinct relation requires a
separately supplied, independently trusted structural-review digest that binds
the exact candidate, endpoints, prose, conflicts, blocks, and executable
content address. The reviewed executable must return a distinct nonempty
mapping that supplies the follow-on request; `None`, pass-through, scalar, or
empty results cannot witness a candidate edge. The checker independently
validates the review, executable source shape, runtime structural-result flag,
and raw execution transcript before accepting the experimental edge.

The R4-B01 correction makes “supplies” an observed dataflow relation rather
than an order-and-shape assertion. A reviewed candidate handle exposes its
JSON request as a read-only provenance-carrying mapping. Expanding that mapping
into the exact declared target preserves the candidate-result origin of every
target keyword. The raw transcript links the qualifying source result to the
candidate argument, records the distinct candidate-result object, and records
the exact candidate submapping and canonical request digest consumed by the
target. A target call made with equivalent hard-coded values has no such raw
request-flow record and cannot produce a reviewed candidate witness or edge.

R5-B01 closes the source-side ambiguity. The trusted relation review is now a
v2 record that freezes one exact `source_result_parameter` from the pinned
candidate callable. Runtime flow accepts the qualifying source-result
descriptor only at that named argument; it never substitutes another matching
argument. The checker also requires the pinned mapping-return expression to
reference the reviewed parameter and requires the raw witness to name it. An
exact source object carried only through unused `context` is therefore presence
without consumption and cannot witness the candidate edge.

R6-B01 distinguishes a source mention from a source-dependent request. Once an
exact candidate-result path is expanded into the target call, the runtime
safely evaluates that pinned return subtree with the reviewed source parameter
present and absent. The two nonempty canonical request mappings must have
different digests, and the present digest must equal the live target request.
The raw request-flow record freezes the path and both digests. The checker
independently reconstructs the same counterfactual proof from source. Equal
branches, algebraically equivalent results, and unsupported expression forms
fail closed and cannot witness a reviewed candidate edge.

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
