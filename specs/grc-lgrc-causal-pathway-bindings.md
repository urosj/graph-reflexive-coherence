# GRC/LGRC Causal Pathway Bindings

**Status:** Frozen linkage authority consumed through Iteration 116

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

## Binding Roles

- `mechanism_entrypoint` identifies an ordinary mechanism-specific public
  callable.
- `stage_entrypoint` identifies a stage-specific module function.
- `load_bearing_internal` records an exact internal stage when no public
  callable isolates that relation.
- `diagnostic_entrypoint` remains diagnostic.
- `producer_entrypoint` retains producer ownership.
- `restoration_entrypoint` remains bounded to restoration/replay identity.

Binding an internal symbol does not promote it to stable general-purpose API.
The map versions the exact source relation for claim provenance.

## Multiplexed Producer Entry Points

`LGRC9V3.produce_events(...)` is a mechanism-specific producer entrypoint used
by several admitted pathways. Those bindings carry an exact required `policy`
keyword. The verified callable refuses a mismatched policy before delegation,
so a feedback binding cannot silently execute the flux-route or surplus
producer.

## Non-Dispatch Rule

The binder imports the recorded callable and delegates the caller's native
arguments unchanged. It does not expose `execute(pathway_id, **kwargs)`, infer
a pathway from intent, translate arguments into common causal-work fields, or
synthesize compositions from endpoint co-use.

Direct unbound calls remain available. They do not produce claim-qualified
binding provenance.

See the
[binding and claim-provenance reference guide](../docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md)
for lock, receipt, candidate, dynamic-choice, and conformance usage.
