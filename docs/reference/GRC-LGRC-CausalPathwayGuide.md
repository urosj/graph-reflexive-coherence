# GRC/LGRC Causal Pathway Guide

**Status:** Draft selection guide pending Phase 8 Iteration 109

**Registry:** [`grc-lgrc-causal-pathway-contracts.json`](../../specs/grc-lgrc-causal-pathway-contracts.json)
**Composition matrix:** [`GRC-LGRC-CompositionMatrix.md`](./GRC-LGRC-CompositionMatrix.md)

## Why This Guide Exists

GRC and LGRC expose several ways to reconstruct current, move coherence,
evaluate candidates, schedule events, commit topology, retain history, and
restore state. Similar-looking outputs do not imply identical causal paths.

Use this guide to choose an existing pathway and keep its authority and claim
boundary visible. Do not use it as evidence that a pathway ran.

The first guide version is limited to GRC9V3, LGRC9V3, and directly consumed
shared PyGRC utilities. It is derived from the registry, evidence crosswalk,
and composition matrix. It must not introduce pathway or composition facts
that those sources do not contain.

## First Question: What Time Semantics Are Required?

### Global synchronous update

Use `grc9v3.synchronous_transport` when graph state should be reconstructed and
advanced through the ordinary synchronous GRC9V3 step.

This supports native synchronous GRC transport. It is not LGRC packet
execution.

### Causal delay and event ordering

Use `lgrc9v3.explicit_packet_transport` when the route and packet work are
known and the experiment needs source debit, in-flight state, deterministic
event order, delayed arrival, and target credit.

The mechanics are native. The supplied route and work do not become
substrate-formed.

### Synchronous-limit observation over LGRC state

Use `lgrc9v3.diagnostic_grc_reconstruction` when a checkpoint or explicit
helper should expose GRC differential, transport, choice, or identity surfaces
over LGRC base state.

This is diagnostic unless a separate admitted adapter consumes the result.

### Snapshot, reset, or replay equivalence

Use `pygrc.restoration_replay_identity`. Restoration identity establishes the
declared state-equivalence boundary, not work eligibility or semantic
identity.

## Second Question: Is The Route Known, Arbitrated, Or Expected To Form?

### Route is explicitly part of the fixture

Use explicit packet transport or `lgrc9v3.configured_flux_route`.

Record the configured route as residue. Do not call it native route formation.

### Route aspect and pole semantics are declared

Use `lgrc9v3.route_aspect_surplus` when the intended contract is a configured
pole-mass surplus threshold that schedules work along a declared channel.

The runtime owns surplus evaluation, budget checks, scheduling records, and
packet mechanics. It does not own the pole's ecological or agentic meaning.

### Candidates exist and selection is the subject

Use `lgrc9v3.native_route_arbitration` when candidate records, scores, and
budget predictions are available and native validation/selection/commitment is
what is being tested.

Candidate and score formation remain separately attributed.

### Route should arise from state, history, or current

No generic native pathway is admitted. Use a bounded producer probe or record
an unsupported crossing. Do not join current reconstruction to packet
scheduling and call the result native without a new source-backed contract.

## Third Question: Which Part Is Claimed Native?

Answer separately:

| Question | Example native owner | Typical residue |
| --- | --- | --- |
| What determines direction? | GRC oriented flux, spark detector, arbitration record | configured route or candidate score |
| What supplies funding? | source/parent coherence, budget invariant | configured packet amount |
| What establishes eligibility? | mechanism-specific native predicate | producer threshold or mask |
| What schedules work? | native producer, runtime rebuild, caller | external orchestration |
| What commits mutation? | `step()`, topology integrator, choice rebuild | none if only diagnostic |
| What receives the result? | target node, selected sink, child topology | experiment-level interpretation |

Native commitment does not naturalize externally authored eligibility.

## Fourth Question: What Retained Relation Is Needed?

### Present state

Consume current model state under the chosen pathway.

### Causal history

Use packet, event, lineage, or topology records only at their declared runtime
scope.

### Derived history functional

Classify it as diagnostic or producer-mediated unless the runtime natively
consumes it in later constitutive dynamics.

### Persistent geometry or topology

Use source-backed topology and restoration pathways. Persistence does not by
itself establish semantic identity or Read-Back.

### Configured policy

Keep it visible as policy state. Configuration is not formation evidence.

## Common Choices

### Sink compatibility or collapse

Use `grc9v3.sink_compatibility_choice` when native outgoing flux should be
aggregated by reachable sink and the choice/collapse registry is the intended
surface.

Do not treat the compatibility score as the generator of current or an
automatic packet schedule.

### Flux-conditioned topology growth

Use `lgrc9v3.boundary_birth` for the specific default-off contract that combines
outward flux pressure, eligible parent capacity, parent funding, birth policy,
queued trial, and topology commit.

Do not generalize this specialized chain into universal current-to-action
admission.

### Spark-driven refinement

Use `lgrc9v3.spark_topology_integration` when hybrid spark diagnostics and
enabled LGRC-3 topology integration are the intended path.

Diagnostic candidate detection remains distinct from identity acceptance or
semantic creation.

### Collapse/reabsorption transport

Use `lgrc9v3.collapse_reabsorption` when explicit or natively arbitrated
topology events should transport packet, lineage, and active-state records.

Selection input and RC identity claims remain separately gated.

## When No Pathway Fits

Record:

```text
consumed pathway IDs
required missing crossing
producer or adapter proposed
native mechanics retained
claim ceiling
controls that isolate the missing crossing
```

This turns an ambiguous mechanism request into a precise substrate demand.

## Pressure Consumers

L04 support-side work, boundary exchange, circulation, AP4/AP5, shared-medium
response, role migration, and future N32 candidates may use this guide as an
acceptance probe. They do not inherit support, ecology, agency, or native
admission from it.

## Claim Boundary

The guide helps select and describe pathways. Only runtime artifacts, tests,
and experiment evidence can establish that a pathway executed and support a
bounded claim. A pathway selection also does not admit a primitive, building
block, motif, or regime in the N30+ experiment catalog.
