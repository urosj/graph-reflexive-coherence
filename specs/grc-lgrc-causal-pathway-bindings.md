# GRC/LGRC Causal Pathway Bindings

**Status:** Iteration 117 B-03 crossing-evidence extension; tranche remains open

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
composition evidence scope and in matrix order. The receipt records the scope,
the ordered endpoint invocation indices, and any required crossing-callable
invocation.

CMP-26 has the stronger explicit-adapter rule. Before lock, its source stages
must bind to the same declared GRC instance consumed by the adapter, and its
target stages must bind to the adapter's deferred LGRC result reference. The
real registered adapter must return after all source stages and before all
target stages. Missing, substituted, out-of-order, or unrelated-instance
crossings cannot form an exercised composition edge.

See the
[binding and claim-provenance reference guide](../docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md)
for lock, receipt, candidate, dynamic-choice, and conformance usage.
