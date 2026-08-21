# GRC/LGRC Causal-Pathway Binding User And Agent Guide

This guide is the task-oriented path for people and coding agents that need to
produce evidence-bearing causal-pathway claims. Use the
[stable reference](GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md) for exact
API and artifact fields, and the
[selection guide](GRC-LGRC-CausalPathwayGuide.md) for semantic selection.

> **Operation-scoped provenance:** every accepted lock and receipt uses
> `claim_scope = bound_invocations_only`. A receipt certifies only represented
> calls made through its verified binding handles. It does not prove whole-run causal closure,
> prove that unbound influences were absent, or qualify the
> final state of a runtime that may also have changed outside the binding
> surface.

## The Workflow

Use one sequence consistently:

```text
select -> bind -> lock -> execute -> seal -> validate
```

| Step | Owner | Result |
| --- | --- | --- |
| Select | Consumer | An exact admitted pathway, exact registered composition, bounded dynamic set, or determination that the relation is unregistered. |
| Bind | Consumer plus frozen authority | Exact mechanism-specific Python symbols and explicit claim ceilings. |
| Lock | Binder | A content-addressed pre-execution architecture record. |
| Execute | Existing runtime through verified handles | Original callable arguments, results, exceptions, and state changes, plus operation-scoped invocation evidence. |
| Seal | Binder | Actual use, witnesses, use graph, claim envelope, and receipt digest. |
| Validate | Independent checker plus caller trust inputs | A fail-closed conformance result; not new behavioral evidence. |

The binder never selects semantics for the consumer and never exposes a
generic causal-work dispatcher. Semantic selection remains consumer-owned and
must happen before binding, in consumer code or configuration.

## 1. Select

Start with the knowledge-plane artifacts:

- `specs/grc-lgrc-causal-pathway-contracts.json` for admitted pathway and
  stage identities;
- `specs/grc-lgrc-causal-pathway-selection-guide.json` for bounded worked
  selections;
- `specs/grc-lgrc-causal-pathway-composition-matrix.json` for directional
  crossing status and claim ceilings; and
- `specs/grc-lgrc-causal-pathway-bindings.json` only after semantic selection,
  to resolve exact Python symbols.

Choose among four outcomes:

| Selection result | Binder action |
| --- | --- |
| One admitted pathway | `session.bind_pathway(pathway_id, ...)` |
| One executable registered crossing | `session.bind_composition(composition_id)` |
| Consumer may choose A or B at runtime | Bind both, then `session.declare_alternatives(...)` |
| No admitted relation matches | `session.declare_candidate(...)` and retain `experimental_unregistered` |

Do not create a plausible-looking pathway ID, composition ID, or native label
when selection returns no admitted relation.

## 2. Load Accepted Authority And Bind

Load authority from the repository and provide two independently controlled
trust inputs: the anchor record and its expected digest.

```python
import json
from pathlib import Path

from pygrc.causal_pathways import CausalPathwayAuthority, PathwayBindingSession

root = Path.cwd()
anchor = json.loads(trusted_anchor_path.read_text(encoding="utf-8"))
authority = CausalPathwayAuthority.load(
    root,
    acceptance_anchor=anchor,
    trusted_anchor_digest=trusted_anchor_digest,
)
session = PathwayBindingSession(authority)
```

Do not read `trusted_anchor_digest` from the submitted anchor and call that
independent trust. Loading without both values is useful for inspection, but
the authority remains `pending_independent_review` and cannot freeze a
claim-bearing lock.

Bind only the stages the consumer intends to expose:

```python
packet = session.bind_pathway(
    "lgrc9v3.explicit_packet_transport",
    stage_ids=("packet_schedule", "source_debit", "target_credit"),
)
schedule = packet.symbol("packet_schedule", instance=model)
debit = packet.symbol("source_debit")
credit = packet.symbol("target_credit")
```

If a stage has more than one registered symbol, pass the exact `symbol_id`.
Instance methods require the exact runtime instance or the explicit crossing or
flow-derived reference required by the matrix row. Linking freezes callable
definition identity and source content; it does not wrap the mechanism in a
common argument schema.

### Registered Compositions

```python
composition = session.bind_composition("CMP-02")
packet = composition.pathway("lgrc9v3.explicit_packet_transport")
schedule = packet.symbol("packet_schedule", instance=model)
debit = packet.symbol("source_debit")
credit = packet.symbol("target_credit")
```

Only matrix rows with an executable status can be bound. A composition that
requires an explicit adapter must link it with `composition.crossing(...)`
before lock. A row with a flow-derived target instance must declare and bind
that reference before lock. These are row-specific dataflow contracts, not
generic composition behavior.

### Dynamic Alternatives

Bind every allowed pathway, then declare the set:

```python
alternatives = session.declare_alternatives(
    alternative_set_id="consumer.packet_or_snapshot",
    pathway_ids=(packet.pathway_id, restoration.pathway_id),
    selection_authority="consumer request field",
)
```

The alternatives object deliberately has no `select()` method. Consumer code
makes the choice during execution.

## 3. Lock

After every declaration and symbol link is complete:

```python
lock = session.freeze_lock()
```

Locking rechecks current authorities, the independent acceptance anchor,
candidate evidence, exact source identities, alternatives, and required
crossings. It then closes declaration. Verified calls before lock and new
declarations after lock fail with `BindingStateError`.

Persist the lock when the run is evidence-bearing:

```python
lock.write("causal-pathways.lock.json")
```

## 4. Execute Through Verified Handles

Call verified handles with the original mechanism-specific signature:

```python
schedule(
    source_node_id=0,
    target_node_id=1,
    edge_id=0,
    amount=0.25,
)
```

The wrapper verifies current source identity immediately before delegation and
returns or raises exactly as the underlying callable does. It separately
records the returned category, trusted effect contract, effect outcome, object
flow, and whether the effect qualifies a claim.

Use scopes only for the relation they represent:

```python
with composition.evidence_scope():
    source_stage(...)
    target_stage(...)

with alternatives.selection_scope():
    if consumer_choice == "packet":
        schedule(...)
    else:
        snapshot()
```

A composition scope must contain its matrix-required qualifying stages in the
required order and satisfy the row-specific dataflow contract. Endpoint co-use
outside the scope, or ordered calls without the required object flow, does not
form a composition edge. An alternative scope accepts exactly one allowed
branch; empty, interrupted, out-of-set, or multi-branch scopes cannot be
sealed.

Direct calls remain valid runtime operations, but they are unbound:

```python
from pygrc.causal_pathways import unbound_execution_classification

model.step()
classification = unbound_execution_classification()
assert classification["causal_pathway_provenance"] == "unbound"
assert not classification["claim_qualified"]
```

The binder is not a process-wide tracer. A direct call cannot appear among the
receipt's represented invocations.

## 5. Seal

After all scopes have closed:

```python
receipt = session.build_receipt()
receipt.write("causal-pathways.receipt.json")
```

Sealing rechecks authority and source currency, requires no active scope,
derives actual use only from contract-qualified effects, reconstructs
composition and candidate witnesses, builds the pathway-use graph and claim
envelope, and links the receipt to the exact lock digest. The session is then
sealed.

Interpret the receipt conservatively:

- `claim_qualified = true` means at least one represented bound operation
  meets the trusted effect contract and the entire receipt is internally
  eligible for validation;
- `actual_bound_pathways_used` is derived from qualifying effects, not from
  declarations;
- `registered_compositions_exercised` requires a valid scoped dataflow
  witness;
- `candidate_relations_exercised` remains experimental; and
- `declared_but_unused` is expected when a declaration or alternative was not
  exercised.

Even a claim-qualified receipt retains
`whole_run_causal_closure_claimed = false` and
`untracked_execution_observable_by_binding_plane = false`.

## 6. Validate Independently

Run the binding conformance checker with trusted inputs supplied outside the
submitted lock and receipt:

```bash
.venv/bin/python scripts/check_grc_lgrc_causal_pathway_binding_conformance.py \
  --lock causal-pathways.lock.json \
  --receipt causal-pathways.receipt.json \
  --acceptance-anchor "$TRUSTED_BINDING_ANCHOR_PATH" \
  --trusted-anchor-digest "$TRUSTED_BINDING_ANCHOR_DIGEST"
```

A registered-composition claim, or a reviewed candidate over an invalid
endpoint pair, also requires the separately trusted raw execution-transcript
digest:

```bash
  --trusted-execution-transcript-digest "$TRUSTED_TRANSCRIPT_DIGEST"
```

Supply each accepted invalid-pair relation-review digest separately:

```bash
  --trusted-candidate-review-digest "$TRUSTED_REVIEW_DIGEST"
```

Never copy either trusted value from the receipt being checked. The checker
reconstructs the receipt semantics independently; passing conformance proves
schema, identity, and provenance consistency, not that the checker reran the
causal dynamics.

## When No Relation Is Admitted

The safe continuation is:

```text
declare candidate -> execute exact candidate mechanism -> experimental provenance
```

It is never:

```text
invent native identity -> promote from one successful run
```

An executable composition candidate requires a version-2 mechanism-evidence
JSON artifact. It must content-address one non-empty repository-relative JSON
file and one repository-relative module-function source, and it must bind the
candidate kind, mechanism ID, exact endpoints, supported relation, symbol ID,
module, qualified symbol, call kind, binding role, source path, and source
SHA-256. The callable must be distinct from every admitted stage and registered
crossing.

Before lock, call `candidate.mechanism()` to obtain the exact verified handle.
During execution, one completed `candidate.evidence_scope()` must contain all
qualifying source calls, then exactly one returned mechanism call, then all
qualifying target calls. After the scope, call
`session.record_candidate_use(candidate.candidate_id)`. The record is derived;
the caller cannot substitute a prose witness.

Every candidate has:

- `claim_ceiling = experimental_unregistered`;
- `promotion_status = none`;
- a proposed relation classified as
  `descriptive_unreviewed_not_claim_qualified`; and
- structured unresolved authority coordinates and blocked claims where
  evidence is absent.

Declaration, execution, and conformance do not update the registry, matrix,
selection guide, or binding map.

### Candidates Over Invalid-Relabel Endpoint Pairs

This stricter case requires an independently trusted
`causal_pathway_candidate_relation_review_v2` record. The review must bind the
candidate identity, kind, endpoints, exact proposed relation, every conflicting
invalid matrix row and blocked relabel, the mechanism content address, an exact
`source_result_parameter`, and the fixed structural-distinction contract.

The final executable contract is semantic rather than merely syntactic:

1. The qualifying source result must occupy the exact reviewed parameter.
2. The candidate must return a distinct, non-empty canonical JSON mapping.
3. The exact mapping, or a nested mapping within it, must provide every target
   keyword value by preserved object identity; hard-coded or copied values do
   not qualify. `bool` and `None` target-keyword leaves cannot carry this
   provenance identity and therefore cannot qualify the request flow.
4. The exact target-request expression must change when the reviewed source
   parameter is supplied versus genuinely omitted using its actual Python
   default. A source mention with equal outcomes is not dependency.
5. The frozen default preserves Python type. Supported defaults are `None`,
   `bool`, `int`, `float`, `str`, `list`, `tuple`, and string-keyed `dict`,
   recursively composed from those values.
6. Dependency expressions use only the reviewed pure subset: constants, the
   reviewed parameter, dict/list/tuple construction, conditional expressions,
   `is`, `is not`, equality/inequality, boolean `and`/`or`, unary `not`/`+`/`-`,
   and arithmetic `+`, `-`, `*`, `/`, `//`, `%`. Unsupported source analysis
   fails closed.

These constraints establish a reviewed experimental source-to-request flow.
They do not admit the relation or weaken its experimental ceiling.

## Failure Interpretation

| Failure | Usually means | First check |
| --- | --- | --- |
| `UnknownPathwayError` | The selected pathway is not in current authority. | Selection output and exact pathway ID. |
| `UnknownCompositionError` | The matrix has no such composition row. | Exact composition ID and matrix version. |
| `UnbindableCompositionError` | The row is unsupported or an invalid relabel. | Use a genuinely distinct candidate only if new work exists. |
| `SymbolBindingError` | Stage/symbol, call kind, instance, source path, or source identity is wrong or stale. | Binding map, exact `symbol_id`, instance ownership, and source diff. |
| `AuthorityDriftError` | Authority digests, source manifests, anchor, or candidate evidence no longer match. | Stop the run; re-review and reseal authority rather than bypassing the check. |
| `InvalidCandidateError` | Candidate identity, evidence, relation, review, source dependency, or witness is incomplete. | Candidate artifact, source hash, scope order, reviewed parameter, and exact target kwargs. |
| `BindingStateError` | A call occurred in the wrong phase or an execution scope is incomplete. | Declare/link before lock; execute after lock; close scopes before seal. |
| Checker rule failure | Submitted artifacts do not reconstruct under independent authority and trust. | The exact rule output, then the raw lock/receipt fields it names. |

Do not catch these errors and emit a claim-bearing receipt anyway. They are
fail-closed provenance boundaries.

## Debugging Checklist

For a failed run, inspect in this order:

1. Confirm the repository root and authority files are the intended revision.
2. Confirm the anchor record came from trusted configuration and the expected
   digest came from a separate trusted channel.
3. Confirm semantic selection happened before binder calls.
4. Compare each declared stage and exact `symbol_id` with
   `authority.stage_ids(...)` and `authority.symbols(...)`.
5. Confirm every instance method is bound to the intended runtime object.
6. Confirm all declarations, candidate mechanism links, and composition
   crossings happened before `freeze_lock()`.
7. Inspect returned versus qualifying invocation rows; a returned call may be
   `no_op`, `rejected`, or `unknown`.
8. For compositions, inspect the completed scope, required order, and
   `dataflow_witness` ports.
9. For dynamic choice, confirm exactly one allowed pathway ran inside the
   scope.
10. For candidates, re-hash both evidence JSON and executable source, then
    inspect source-mechanism-target order and exact object flow.
11. Run the independent checker with genuinely external transcript and review
    digests where required.

The [five runnable examples](../../examples/causal_pathway_binding/README.md)
are small known-good baselines for comparing each declaration form.

## Safe Extension Practices

Treat changes according to the authority they affect:

- New consumer usage of an existing admitted pathway usually needs only a new
  selection, binding declarations, and tests.
- A new exact symbol for an existing stage changes the binding map, source
  manifest, acceptance anchor, and compatibility evidence.
- A new pathway changes the registry, crosswalk, selection surface, binding
  map, anchor, and both conformance stories.
- A new composition requires directional crossing evidence and matrix review;
  endpoint co-use is insufficient.
- A candidate can gather experimental evidence but cannot self-promote.
- Artifact schemas, digest fields, canonical ordering, claim envelopes, and
  checker derivations are compatibility and trust boundaries, not convenient
  extension points.

Keep runtime mechanics in their mechanism-specific modules. Keep semantic
selection in consumer-owned logic. Keep validation independent of the binder's
load-bearing derivations.

## Agent Operating Rules

An agent modifying or generating a binder consumer should:

1. read the selection and matrix authorities before choosing IDs;
2. cite the chosen pathway/composition and its claim ceiling in the change;
3. use only public imports from `pygrc.causal_pathways` or
   `pygrc.causal_pathways.binding`;
4. never depend on the binder's internal module layout;
5. preserve original callable signatures and consumer-owned branch logic;
6. never infer claim qualification from truthiness or successful return alone;
7. retain `bound_invocations_only` in every interpretation;
8. treat candidate provenance as experimental and non-promoting;
9. run the example or focused test matching the changed declaration form; and
10. run independent conformance before presenting an artifact as accepted.
