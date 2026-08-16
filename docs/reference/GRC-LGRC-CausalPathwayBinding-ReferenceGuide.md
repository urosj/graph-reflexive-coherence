# GRC/LGRC Causal Pathway Binding And Claim Provenance

Use this guide when code will make an evidence-bearing claim that it consumed
a particular GRC/LGRC causal pathway or registered composition.

The short version is:

> Use the selection guide to decide what you intend to consume. Use the
> binding layer to make that identity part of the evidence-bearing program.
> Use the existing mechanism-specific callable to execute it.

If no admitted relation exists, declare an unregistered candidate. Do not
invent a native or admitted claim.

## The Three Planes

### Knowledge Plane

The knowledge plane defines what is known and what may be claimed:

- the [pathway guide](GRC-LGRC-CausalPathwayGuide.md) helps a researcher decide
  which exact pathway or crossing matches the intended semantics;
- the [registry](../../specs/grc-lgrc-causal-pathway-contracts.json) owns
  pathway and stage facts;
- the [evidence crosswalk](../../specs/grc-lgrc-causal-pathway-evidence-crosswalk.json)
  owns source and test relations;
- the [composition matrix](../../specs/grc-lgrc-causal-pathway-composition-matrix.json)
  owns directional crossing facts;
- the selection guide derives bounded choices from those authorities.

The knowledge plane does not execute a mechanism.

### Binding Plane

The binding plane records the declared identity, exact Python symbol, actual
use, and conservative claim provenance:

- `CausalPathwayAuthority` validates current knowledge and source-link
  identities;
- `PathwayBindingSession` declares admitted pathways, registered executable
  compositions, candidates, and allowed dynamic alternatives;
- `BoundPathway.symbol(...)` links one exact stage to its real callable and
  freezes a content-addressed callable identity;
- `freeze_lock()` closes declarations before claim-bearing execution;
- verified callables re-resolve that identity immediately before delegation
  and record returned and raised invocations;
- `build_receipt()` emits actual use, the use graph, and the claim envelope.

The [binding-symbol map](../../specs/grc-lgrc-causal-pathway-bindings.json) is
separate from the registry. It maps every admitted stage to the current module,
qualified symbol, call kind, source path, and source hash.

The binding plane never chooses pathway semantics and has no generic
`execute(pathway_id, **generic_args)` operation.

### Execution Plane

GRC9V3, LGRC9V3, their producers, adapters, diagnostic helpers, and
mechanism-specific module functions remain the execution plane. A verified
callable delegates the original arguments and result without translating them
into a common causal-work schema.

Existing unbound code remains executable for compatibility. It is classified
as unbound and cannot appear among the receipt's recorded bound invocations.
The binding plane is not a process-wide tracer and cannot establish that no
other direct causal work occurred.

## Binding One Admitted Pathway

The consumer chooses an exact identity first. It then chooses the exact stage
symbol before locking:

```python
from pathlib import Path

from pygrc.causal_pathways import (
    CausalPathwayAuthority,
    PathwayBindingSession,
    sha256_file,
)

authority = CausalPathwayAuthority.load(Path.cwd())
session = PathwayBindingSession(authority)
packet = session.bind_pathway(
    "lgrc9v3.explicit_packet_transport",
    stage_ids=("packet_schedule",),
)
schedule = packet.symbol("packet_schedule", instance=model)

lock = session.freeze_lock()
schedule(
    source_node_id=0,
    target_node_id=1,
    edge_id=0,
    amount=0.25,
)
receipt = session.build_receipt()

lock.write("causal-pathways.lock.json")
receipt.write("causal-pathways.receipt.json")
```

The handle exposes the real scheduling signature. Another pathway may expose
a completely different signature or several exact symbols. There is no shared
mechanism interface.

Declaring the packet pathway does not create a composition. The receipt lists
only stages and symbols that actually returned through the bound surface.

## Binding A Registered Composition

Use an exact matrix identity when the intended claim crosses pathways:

```python
composition = session.bind_composition("CMP-20")
producer = composition.pathway("lgrc9v3.feedback_eligibility_producer")
transport = composition.pathway("lgrc9v3.explicit_packet_transport")

produce = producer.symbol("feedback_packet_schedule", instance=model)
schedule = transport.symbol("packet_schedule", instance=model)

lock = session.freeze_lock()
with composition.evidence_scope():
    produce(policy="packet_departure_from_feedback_eligibility_policy")
    schedule(...)
# Run the remaining matrix-required target stages in the same scope.
```

The lock and receipt retain the matrix status and ceiling. For CMP-20 they also
retain the feedback producer identity, installed-producer owner, and the
producer-owned eligibility, direction, threshold, and schedule authorities.
The combined result cannot be relabeled `lawful_native`.

An explicit-adapter composition additionally binds its exact adapter callable.
For CMP-26, call `composition.crossing(source_instance=grc_model)` before the
lock, bind target-stage handles to `crossing.result_reference`, then invoke the
adapter between the required source and target calls inside the evidence
scope. The source handles, adapter argument, and target result reference are
checked as one object-flow relation.

A diagnostic-only composition retains the diagnostic cut; no behavioral claim
may cross it. Unsupported missing crossings and invalid relabels cannot be
bound as admitted executable compositions.

A composition counts as exercised only when one completed evidence scope
contains every matrix-required source and target stage in order. Endpoint
co-use outside that scope forms no edge. CMP-26 additionally requires one
returned, identity-verified adapter crossing between those endpoint groups.

## Declaring An Unregistered Candidate

Candidate declaration is the explicit open continuation route:

```python
candidate = session.declare_candidate(
    candidate_id="experiment.packet_to_snapshot_relation",
    candidate_kind="composition",
    purpose="Pressure a new fixture-only relation.",
    owner="experiment_fixture",
    consumed_pathway_ids=(packet.pathway_id, snapshot.pathway_id),
    proposed_source_pathway_id=packet.pathway_id,
    proposed_target_pathway_id=snapshot.pathway_id,
    proposed_relation="new post-packet snapshot relation",
    authority={"direction": "experiment producer"},
    evidence_owner="experiment_fixture",
    mechanism_evidence={
        "evidence_kind": "content_addressed_artifact",
        "mechanism_id": "experiment.packet_then_snapshot",
        "path": "implementation/evidence/packet-then-snapshot.json",
        "sha256": sha256_file(
            ROOT / "implementation/evidence/packet-then-snapshot.json"
        ),
    },
)
```

All omitted authority coordinates become `unresolved`. Candidate claim ceiling
is fixed to `experimental_unregistered`, promotion status is fixed to `none`,
and native/admitted/promotion relabels are blocked.

The evidence path must be repository-relative and name a non-empty JSON
artifact whose schema, mechanism identity, candidate kind, endpoints, and
supported relation match the declaration. Its SHA-256 is frozen before use.
For a composition candidate, execute the declared source and target handles in
order inside `with candidate.evidence_scope():`, then call
`record_candidate_use(candidate.candidate_id)`. The method accepts no free-form
evidence string and revalidates the artifact before recording the derived
scope and invocation indices.

Candidate pathway nodes and composition edges are visibly different from
admitted graph elements. A candidate can consume admitted constituents but
cannot inherit their native or admitted status. A candidate over endpoints
occupied by a registered invalid relabel requires a distinct content-addressed
mechanism, and its proposed relation may not restate that row's blocked labels.

Candidate declaration does not update the registry, matrix, selection guide,
or binding map. Promotion remains a separate evidence and review process.

## Dynamic Consumer Choice

When consumer code may use pathway A or B, declare both pathway bindings and
the allowed set before locking:

```python
session.declare_alternatives(
    alternative_set_id="consumer.packet_or_snapshot",
    pathway_ids=(packet.pathway_id, snapshot.pathway_id),
    selection_authority="consumer_boolean_branch",
)
```

The alternatives object has no selection method. Consumer code makes the
choice. The receipt reports the allowed set, selection authority, paths
actually used, and declared-but-unused alternatives.

If the selection mechanism itself is claimed as native causal behavior, that
mechanism needs its own admitted pathway or composition. Native arbitration is
not native candidate formation.

## Lock, Receipt, And Use Graph

The lock is a causal-architecture record, not a dependency lockfile. It freezes
current authority and binding-map digests, declared identities, exact symbols,
callable fingerprints and source hashes, producer and adapter cuts, residue,
alternatives, candidates, blocked claims, and the pre-execution claim envelope.

No verified callable can run before the lock. Declarations and symbol choices
close after it. Authority or source drift at lock or receipt time fails closed.

The receipt links to the exact lock digest and records:

- returned and raised stage/symbol invocations;
- ordered composition-scope witnesses and explicit-adapter invocations;
- returned pathway and registered-composition use under the current outcome
  vocabulary;
- candidate use, content-addressed mechanism evidence, and scoped execution
  witnesses;
- producer and adapter cuts used;
- declared-but-unused identities;
- allowed dynamic alternatives actually taken;
- admitted and candidate-distinct graph nodes and edges;
- a structured claim envelope and blocked claims;
- accepted authority/source identities and a receipt digest.

The Iteration 117 B-03 correction prevents registered edges from being formed
by endpoint co-use alone. The checker independently reconstructs each witness
from scoped invocation indices and global execution order; CMP-26 also checks
the frozen and invoked adapter identity. Multiple registered edges still do
not synthesize a larger semantic ceiling unless that larger composition is
itself registered.

The B-04 correction applies the same declaration-is-not-use boundary to
candidates. The checker re-hashes candidate evidence and reconstructs the
candidate scope from invocation indices; unscoped co-use, arbitrary strings,
and renamed invalid-relabel restatements do not produce candidate graph
elements or an experimental candidate claim.

## Claim Qualification

Claim qualification is operation-scoped. A receipt proves only the callable
identities and outcomes listed in `actual_stage_symbol_invocations`; it does
not prove whole-run causal closure, qualify a direct call, or qualify the final
state of a runtime that may also have been changed outside the binding surface.
The lock and receipt therefore carry `claim_scope = bound_invocations_only`,
`whole_run_causal_closure_claimed = false`, and an explicit statement that
external or untracked causal input is not observable by the binding plane.

A declaration without returned bound use is visible but not invocation
evidence. A raised call remains visible but does not become returned behavioral
evidence. The returned/committed/no-op distinction remains part of the open
Iteration 117 correction gate.

For direct legacy execution, use:

```python
from pygrc.causal_pathways import unbound_execution_classification

classification = unbound_execution_classification()
```

It returns `causal_pathway_provenance = unbound`, `claim_qualified = false`,
and `accepted_binding_receipt = false`.

This rule applies to claim-bearing or promotion-bearing consumers, not to
every internal Python call inside an admitted mechanism.

## Conformance

Validate the frozen prospective fixture or supply another exact lock/receipt:

```bash
.venv/bin/python scripts/check_grc_lgrc_causal_pathway_binding_conformance.py

.venv/bin/python scripts/check_grc_lgrc_causal_pathway_binding_conformance.py \
  --lock path/to/causal-pathways.lock.json \
  --receipt path/to/causal-pathways.receipt.json
```

Binding/source drift becomes `stale_pending_review` and blocks
claim-qualified artifacts. The checker validates structure and provenance; it
does not dispatch or rerun causal dynamics.

## Boundaries

The layer supports versioned pathway binding and conservative provenance. It
does not provide universal causal routing, automatic selection, generic work
admission, native candidate formation, ecological interpretation, agency,
Read-Back, or N32.
