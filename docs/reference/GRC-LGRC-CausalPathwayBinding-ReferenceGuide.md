# GRC/LGRC Causal Pathway Binding And Claim Provenance

Use this guide when code will make an evidence-bearing claim that it consumed
a particular GRC/LGRC causal pathway or registered composition.

> **Operation-scoped provenance:** `claim_scope = bound_invocations_only`
> certifies only the represented calls made through verified binding handles.
> It does not prove whole-run causal closure, prove that unbound influences were
> absent, or qualify direct execution and unrelated runtime state.

The short version is:

> Use the selection guide to decide what you intend to consume. Use the
> binding layer to make that identity part of the evidence-bearing program.
> Use the existing mechanism-specific callable to execute it.

If no admitted relation exists, declare an unregistered candidate. Do not
invent a native or admitted claim.

For a task-oriented walkthrough, failure interpretation, debugging guidance,
and agent operating rules, use the
[user and agent guide](GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md). The
[five runnable examples](../../examples/causal_pathway_binding/README.md) cover
each supported declaration pattern and the direct-unbound boundary.

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
  and record invocation transport separately from contract-classified effects;
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

## Stable Public Surface

Import public binder objects from `pygrc.causal_pathways` or
`pygrc.causal_pathways.binding`. Those two facades expose the same objects. The
internal provider modules and class ownership are deliberately noncontractual.

The primary entry points are:

```python
CausalPathwayAuthority.load(
    repository_root,
    *,
    acceptance_anchor=None,
    trusted_anchor_digest=None,
)

PathwayBindingSession(authority)
session.bind_pathway(pathway_id, *, stage_ids=None, binding_id=None)
session.bind_composition(composition_id, *, binding_id=None)
session.declare_alternatives(
    *, alternative_set_id, pathway_ids, selection_authority
)
session.declare_candidate(
    *, candidate_id, candidate_kind, purpose, owner,
    consumed_pathway_ids=(), consumed_composition_ids=(),
    proposed_source_pathway_id=None, proposed_target_pathway_id=None,
    proposed_relation=None, authority=None, producer_residue=(),
    adapter_residue=(), configured_residue=(), evidence_owner,
    mechanism_evidence=None, invalid_relabel_relation_review=None,
    trusted_relation_review_digest=None, blocked_claims=(),
)
session.freeze_lock()
session.record_candidate_use(candidate_id)
session.build_receipt()
```

Handle methods preserve mechanism-specific behavior:

| Object | Stable operations |
| --- | --- |
| `BoundPathway` | `symbol(stage_id, *, symbol_id=None, instance=None)` and read-only identity/contract properties. |
| `BoundComposition` | `pathway(pathway_id)`, `evidence_scope()`, `crossing(*, source_instance)`, `flow_derived_target_instance(*, source)`, and read-only matrix properties. |
| `AllowedPathwayAlternatives` | `selection_scope()`; selection remains consumer-owned. |
| `CandidateDeclaration` | `mechanism()`, `evidence_scope()`, `to_record()`, and fixed candidate properties. |
| `VerifiedCallable`, `VerifiedCompositionCrossing`, candidate mechanism handle | Original callable invocation through identity and phase checks. |
| `BindingLock`, `BindingReceipt` | `digest`, defensive `to_record()`, and canonical `write(path)`. |

The complete facade exports are:

- orchestration and handles: `PathwayBindingSession`, `BoundPathway`,
  `BoundComposition`, `VerifiedCallable`, `VerifiedCompositionCrossing`,
  `AllowedPathwayAlternatives`, `AlternativeSelectionScope`,
  `CompositionExecutionScope`, `CandidateExecutionScope`,
  `CrossingResultReference`, and `FlowDerivedInstanceReference`;
- authority, identity, effects, and records: `CausalPathwayAuthority`,
  `BindingAcceptanceAnchor`, `SourceSymbolBinding`,
  `CompositionCrossingBinding`, `CallableIdentity`, `EffectOutcomeContract`,
  `InvocationRecord`, `CrossingInvocationRecord`, `CandidateDeclaration`,
  `CandidateMechanismEvidence`, `CandidateRelationReview`, and
  `CandidateUseRecord`;
- artifacts: `BindingLock` and `BindingReceipt`;
- public errors: `CausalPathwayBindingError`, `AuthorityDriftError`,
  `BindingStateError`, `SymbolBindingError`, `InvalidCandidateError`,
  `UnbindableCompositionError`, `UnknownPathwayError`, and
  `UnknownCompositionError`;
- functions: `canonical_digest`, `sha256_file`, `binding_semantics_digest`,
  `binding_source_manifest_digest`, `composition_dataflow_contract`,
  `execution_transcript_digest`, and `unbound_execution_classification`; and
- constants: `ATTESTED_OBJECT_FLOW_DATAFLOW`, `AUTHORITY_COORDINATES`,
  `CLAIM_QUALIFYING_EFFECT_OUTCOMES`, `EFFECT_OUTCOMES`,
  `EXECUTABLE_COMPOSITION_STATUSES`, `EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT`,
  `INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT`, `RETURN_CATEGORIES`.

The machine-readable signature, exception, property, context-manager, and
return-type baseline is the
[I118 public API compatibility freeze](../../implementation/evidence/causal-pathway-binding/i118/I118PublicAPICompatibilityFreeze.json).
That freeze is normative when this compact reference omits a secondary method.

## Binding One Admitted Pathway

The consumer chooses an exact identity first. It then chooses the exact stage
symbol before locking:

```python
import json
from pathlib import Path

from pygrc.causal_pathways import (
    CausalPathwayAuthority,
    PathwayBindingSession,
    sha256_file,
)

repository_root = Path.cwd()
# Both values below come from trusted caller configuration.
acceptance_anchor = json.loads(trusted_anchor_path.read_text(encoding="utf-8"))
authority = CausalPathwayAuthority.load(
    repository_root,
    acceptance_anchor=acceptance_anchor,
    trusted_anchor_digest=trusted_anchor_digest,
)
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
as actual only stages and symbols whose trusted exact-symbol contracts classify
their effects as `committed` or `observed`.

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
contains a claim-qualifying effect for every matrix-required source and target
stage in order. Endpoint co-use outside that scope forms no edge. CMP-26
additionally requires one claim-qualifying, identity-verified adapter crossing
between those endpoint groups.

Rows with module-function crossings use their frozen argument/result flow
ports. CMP-04 additionally needs a target constructed after its source helper
returns:

```python
prepare = diagnostic.symbol("diagnostic_model_construction")
target_reference = composition.flow_derived_target_instance(source=prepare)
rebuild = diagnostic.symbol("diagnostic_rebuild", instance=target_reference)

lock = session.freeze_lock()
with composition.evidence_scope():
    prepared = prepare(model)
    diagnostic_model = GRC9V3(
        params=prepared.get_params(),
        state=prepared.get_state().base_state,
    )
    target_reference.bind(
        source_result=prepared,
        target_instance=diagnostic_model,
    )
    rebuild()
```

The reference validates the exact returned object and equivalent state
fingerprints before target delegation. It does not construct the target or
choose the mechanics for the consumer.

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
        "evidence_kind": "executable_candidate_mechanism",
        "mechanism_id": "experiment.packet_then_snapshot",
        "path": "implementation/evidence/packet-then-snapshot.json",
        "sha256": sha256_file(
            ROOT / "implementation/evidence/packet-then-snapshot.json"
        ),
    },
)

crossing = candidate.mechanism()
session.freeze_lock()
with candidate.evidence_scope():
    schedule_result = packet_schedule(...)
    crossing(schedule_result)
    snapshot()
session.record_candidate_use(candidate.candidate_id)
```

All omitted authority coordinates become `unresolved`. Candidate claim ceiling
is fixed to `experimental_unregistered`, promotion status is fixed to `none`,
and native/admitted/promotion relabels are blocked.

The evidence path must be repository-relative and name a non-empty version-2
JSON artifact whose schema, mechanism identity, candidate kind, endpoints, and
supported relation match the declaration. The artifact must identify one
repository-relative module-function entrypoint with its source SHA-256. The
binder resolves that unregistered callable directly from its pinned source,
freezes its definition-level identity, and rejects a callable already used by
an admitted stage or registered crossing. Both the artifact and executable
source are revalidated before use.

`candidate.mechanism()` returns only that exact candidate-specific callable.
It may execute once, after lock, inside the same completed
`candidate.evidence_scope()` as the qualifying constituent invocations. For a
composition candidate, every qualifying source call must precede the candidate
mechanism, which must precede every qualifying target call. Then
`record_candidate_use(candidate.candidate_id)` derives the scope, mechanism,
and constituent invocation indices. It accepts no caller-authored evidence
string. A returned candidate call proves identity-verified experimental
execution; it does not promote the callable or independently claim an admitted
effect contract.

Candidate pathway nodes and composition edges are visibly different from
admitted graph elements. A candidate can consume admitted constituents but
cannot inherit their native or admitted status. A candidate over endpoints
occupied by a registered invalid relabel requires a distinct executable
mechanism. Its proposed relation may not restate that row's blocked labels
literally or by retaining their load-bearing semantic tokens. Every conflicting
row and blocked relabel is retained structurally in the lock, receipt, node,
and edge. The proposed free-text relation is marked
`descriptive_unreviewed_not_claim_qualified`; it cannot supersede those
structured prohibitions.

Candidate declaration does not update the registry, matrix, selection guide,
or binding map. Promotion remains a separate evidence and review process.

## Dynamic Consumer Choice

When consumer code may use pathway A or B, declare both pathway bindings and
the allowed set before locking:

```python
alternatives = session.declare_alternatives(
    alternative_set_id="consumer.packet_or_snapshot",
    pathway_ids=(packet.pathway_id, snapshot.pathway_id),
    selection_authority="consumer_boolean_branch",
)

session.freeze_lock()
if consumer_selected_snapshot:
    with alternatives.selection_scope():
        snapshot()
```

The alternatives object has no selection method. Consumer code makes the
choice, then opens `selection_scope()` around that one decision. The first
bound pathway called in the scope fixes the branch. Another member or any
out-of-set pathway in the same scope fails before delegation. Empty,
interrupted, and rejected scopes cannot be sealed into a receipt.

Calls outside the scope remain unrelated bound work and are not inferred as a
dynamic choice merely because their pathway appears—or does not appear—in the
allowed set. The receipt records the allowed set, selection authority,
consumer-selected pathways, exact scope/invocation witnesses, returned and
claim-qualifying invocation indices, actual qualifying paths, and declarations
with no completed selection scope.

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

- returned and raised stage/symbol invocations with return category, trusted
  effect contract, effect outcome, and qualifying flag;
- ordered composition-scope witnesses and explicit-adapter invocations;
- contract-qualified pathway and registered-composition use;
- candidate use, source-pinned executable mechanism identity and invocation,
  and scoped constituent-execution witnesses;
- producer and adapter cuts used;
- declared-but-unused identities;
- consumer-owned dynamic-selection scopes, exact invocations, and allowed
  alternatives actually taken;
- admitted and candidate-distinct graph nodes and edges;
- a structured claim envelope and blocked claims;
- accepted authority/source identities and a receipt digest.

Registered edges cannot be formed by endpoint co-use, order, or mutually
consistent artifact labels alone. The checker independently reconstructs each
witness from scoped invocation indices, global execution order, and the row's
frozen stage/port dataflow contract. Raw records retain receiver, argument,
result, and state-carrier object identities. Most rows require exact
live-object continuity; CMP-04 records the consumer-bound equivalent-state-copy
derivation. CMP-26 retains its stricter declared-adapter-source to
adapter-result-reference rule.

Registered-composition and reviewed invalid-pair-candidate verification also
require `--trusted-execution-transcript-digest` (or the equivalent library
argument) from caller-controlled trust configuration. The checker recomputes
the digest from the lock identity and raw stage/crossing/candidate invocation
arrays. A digest copied from the submitted receipt is only self-consistency
evidence and must not be treated as the independent trust input.

This proof is deliberately fail-closed. A composition whose crossing is not
observable through its row-specific relation remains declared-but-unused even
when its endpoints execute in order. CMP-04 therefore rejects an unrelated GRC
target but can exercise its registered diagnostic edge through the explicit
consumer-bound derivation above. Multiple registered edges still do not
synthesize a larger semantic ceiling unless that larger composition is itself
registered.

The same declaration-is-not-use boundary applies to candidates. The checker
independently re-hashes the candidate artifact and executable source,
reconstructs the exact definition identity and candidate invocation, and
verifies its order within the candidate scope. Metadata-only evidence, an
admitted-callable alias, unscoped co-use, arbitrary strings, and literal or
semantic invalid-relabel restatements do not produce candidate graph elements
or an experimental candidate claim.

A candidate over endpoints already occupied by an `invalid_relabel` row has a
separate acceptance boundary. The declaration must include an exact
`causal_pathway_candidate_relation_review_v2` record and receive its expected
digest through caller-controlled trust input; the checker requires the same
digest through repeatable `--trusted-candidate-review-digest` options. The
review binds the candidate identity, endpoints, proposed relation, every
invalid-row block, mechanism content address, reviewed source-result parameter,
and structural adapter contract. It does not weaken the experimental ceiling
or turn relation prose into a qualified claim.

Such a reviewed callable must consume its source result and return a distinct
nonempty mapping used to construct the follow-on request. The runtime freezes
the review digest and observed structural-result predicate in the raw
candidate invocation transcript. The checker independently validates the
review, the pinned source's nonempty-mapping return structure, the invocation
predicate, graph retention, and external transcript trust. A renamed relation
backed by `return None`, a pass-through result, a scalar, or an empty mapping
therefore cannot form an experimental edge even when all submitted artifacts
are coherently resealed.

A reviewed invalid-pair candidate has a semantic source-to-request contract.
Its verified mechanism returns a read-only provenance-carrying, non-empty
canonical JSON mapping. Consumer code expands that mapping, or a nested mapping
within it, into `target(**request)`. `candidate_request_flow` is recorded only
when every target keyword is the exact value exposed by that mapping; hard-coded
or copied values do not qualify. `bool` and `None` target-keyword leaves cannot
carry provenance identity and do not qualify the request flow.

The qualifying source result must occupy the exact `source_result_parameter`
named by the trusted review. Presence in another unused argument is
insufficient. The exact target-request expression must also change when that
reviewed parameter is supplied versus genuinely omitted with its actual Python
default. The runtime and checker independently evaluate the pinned source in a
small pure-expression subset and compare type-preserving default,
source-present, source-omitted, and live-request digests. A source mention with
equal outcomes is not source-to-request flow.

Supported reviewed defaults are `None`, `bool`, `int`, `float`, `str`, `list`,
`tuple`, and string-keyed `dict`, recursively composed from those values. The
pure expression subset admits constants, the reviewed parameter, dict/list/
tuple construction, conditional expressions, identity and equality
comparisons, boolean `and`/`or`, unary `not`/`+`/`-`, and arithmetic `+`, `-`,
`*`, `/`, `//`, `%`. Tuple and list identity remain distinct in the frozen
default digest. Unsupported analysis fails closed.

The resulting witness links one qualifying source-result descriptor to the
reviewed candidate parameter, the candidate result descriptor to the exact
request derivation, and that derivation to one qualifying target invocation.
The checker reconstructs every link from the raw transcript. This proves only
a reviewed experimental flow; it does not admit or promote the relation.

The claim envelope is an independently reconstructed projection, not a trusted
receipt summary. The checker builds the expected lock envelope from declared
bindings and current registry/matrix authority, then builds the receipt
envelope separately from claim-qualifying stage invocations, valid
composition-flow witnesses, and valid candidate-mechanism witnesses. Exact
structural equality is required for every ceiling, qualifier list, summary
flag, aggregate blocked claim, overall status, and non-synthesis field. Adding,
deleting, reordering, or widening any field fails closed even when artifact
digests are recomputed.

Dynamic selection is likewise reconstructed from scoped invocation indices.
An out-of-set pathway is rejected inside an A/B scope, while an unrelated call
outside it remains unrelated and does not alter the A/B witness.

A self-consistent binding map is distinct from an accepted map. Loading without
an anchor remains available for inspection, but the authority reports
`pending_independent_review` and cannot freeze a claim lock. Acceptance
requires both an anchor record and its expected digest from trusted caller
configuration. The loader never discovers either value automatically. The
anchor pins the full binding-map digest, source revision, stage/crossing
semantic projection, source path/content manifest, exact-symbol effect-outcome
contracts, and their set digest. Those contracts cannot be supplied by a
receipt or inferred from generic Python truthiness.

## Exact Artifact Schemas

`BindingLock.write()` and `BindingReceipt.write()` emit UTF-8 JSON with two-space
indentation, lexicographically sorted keys, and one trailing newline. Digests
use the same canonical JSON value model and exclude only their own digest
field. Field names, schema versions, values, canonical ordering, and digest
derivations are compatibility boundaries.

### Binding Lock V1

The artifact identity is `causal-pathways-binding-lock` with schema version
`causal_pathways_binding_lock_v1`. Its exact top-level fields are:

```text
allowed_pathway_alternatives
artifact
binding_acceptance_anchor_digest
binding_acceptance_status
binding_map_digest
blocked_claims
candidate_declarations
claim_scope
conformance_policy_digest
crosswalk_digest
declared_composition_bindings
declared_pathway_bindings
effect_outcome_contracts_digest
execution_transcript_trust_requirement
explicit_adapters
explicit_producers
lock_digest
matrix_digest
pre_execution_claim_envelope
registry_digest
schema_version
selector_digest
semantic_selection_performed_by_binder
source_revision
unregistered_relation_bound_without_candidate
untracked_execution_observable_by_binding_plane
whole_run_causal_closure_claimed
```

The declaration arrays have these exact row contracts:

| Array | Row fields |
| --- | --- |
| `declared_pathway_bindings` | `activation`, `availability`, `binding_id`, `composition_ids`, `configured_residue`, `declared_stage_ids`, `expected_concrete_symbols`, `mechanism_ownership`, `pathway_id`, `producer_residue` |
| `declared_composition_bindings` | `adapter_id`, `adapter_owner`, `authority_retained`, `authority_transferred`, `binding_id`, `blocked_relabels`, `claim_ceiling`, `composition_id`, `composition_status`, `expected_crossing_callable`, `from_pathway_id`, `from_stage_ids`, `information_lost_or_compressed`, `runtime_dataflow_contract`, `runtime_dataflow_requirement`, `to_pathway_id`, `to_stage_ids` |
| `allowed_pathway_alternatives` | `alternative_set_id`, `pathway_ids`, `selection_authority` |
| `candidate_declarations` | `adapter_residue`, `authority`, `blocked_claims`, `candidate_id`, `candidate_kind`, `candidate_mechanism_link`, `claim_ceiling`, `configured_residue`, `consumed_admitted_composition_ids`, `consumed_admitted_pathway_ids`, `evidence_owner`, `invalid_relabel_blocked_claims`, `invalid_relabel_conflict_ids`, `invalid_relabel_relation_review`, `invalid_relabel_relation_review_trust_requirement`, `mechanism_evidence`, `owner`, `producer_residue`, `promotion_status`, `proposed_relation`, `proposed_relation_claim_status`, `proposed_source_pathway_id`, `proposed_target_pathway_id`, `purpose` |

`expected_concrete_symbols` and `expected_crossing_callable` retain exact module,
qualified symbol, call kind, source path/hash, definition identity, binding role,
required arguments, runtime-instance binding, and trusted effect contract where
applicable.

### Binding Receipt V1

The artifact identity is `causal-pathways-binding-receipt` with schema version
`causal_pathways_binding_receipt_v1`. Its exact top-level fields are:

```text
actual_bound_pathways_used
actual_candidate_mechanism_invocations
actual_composition_crossing_invocations
actual_stage_symbol_invocations
adapters_used
allowed_pathway_alternatives_actual_use
artifact
binding_acceptance_anchor_digest
binding_acceptance_status
binding_lock_digest
binding_map_digest
blocked_claims
candidate_relations_exercised
claim_envelope
claim_qualified
claim_scope
composition_crossing_witnesses
conformance_policy_digest
crosswalk_digest
declared_but_unused
effect_outcome_contracts_digest
effect_outcome_summary
execution_transcript_digest
execution_transcript_trust_requirement
external_or_untracked_causal_input
matrix_digest
pathway_use_graph
producer_cuts_used
receipt_digest
registered_compositions_exercised
registry_digest
schema_version
selector_digest
semantic_selection_performed_by_binder
source_revision
unbound_execution_accepted_as_evidence
undeclared_use_violations
untracked_execution_observable_by_binding_plane
whole_run_causal_closure_claimed
```

The load-bearing receipt rows have these exact fields:

| Array/object | Fields |
| --- | --- |
| `actual_stage_symbol_invocations[]` | `alternative_selection_scope_id`, `binding_id`, `callable_identity`, `candidate_request_flow`, `candidate_scope_id`, `claim_qualifying_effect`, `composition_ids`, `crossing_scope_id`, `effect_contract_id`, `effect_evidence`, `effect_kind`, `effect_outcome`, `error_type`, `execution_event_order`, `invocation_index`, `outcome`, `pathway_id`, `result_type`, `return_category`, `runtime_object_flow`, `stage_id`, `symbol_id` |
| `actual_composition_crossing_invocations[]` | `binding_id`, `callable_identity`, `claim_qualifying_effect`, `composition_id`, `crossing_invocation_index`, `crossing_scope_id`, `effect_contract_id`, `effect_evidence`, `effect_kind`, `effect_outcome`, `error_type`, `execution_event_order`, `outcome`, `result_type`, `return_category`, `source_binding_id`, `symbol_id`, `target_binding_id` |
| `actual_candidate_mechanism_invocations[]` | `callable_identity`, `candidate_id`, `candidate_mechanism_invocation_index`, `candidate_scope_id`, `error_type`, `execution_event_order`, `mechanism_id`, `outcome`, `relation_review_digest`, `result_type`, `runtime_object_flow`, `structural_result_observed`, `symbol_id` |
| `composition_crossing_witnesses[]` | `binding_id`, `composition_id`, `crossing_invocation_indices`, `crossing_scope_id`, `dataflow_requirement`, `dataflow_witness`, `explicit_adapter_observed`, `explicit_adapter_required`, `from_invocation_indices`, `ordering_rule`, `to_invocation_indices` |
| `pathway_use_graph` | `edges`, `larger_chain_claim_synthesized`, `nodes`, `unregistered_edge_synthesized_from_endpoint_co_use` |
| `claim_envelope` | `blocked_claims`, `composition_status_is_maturity_score`, `constituent_composition_claim_ceilings`, `constituent_pathway_claim_ceilings`, `contains_adapter_cut`, `contains_diagnostic_only_relation`, `contains_producer_cut`, `experimental_unregistered`, `overall_claim_status`, `required_qualifiers`, `synthesized_chain_claim` |
| `effect_outcome_summary` | `claim_qualifying_crossing_invocation_indices`, `claim_qualifying_stage_invocation_indices`, `crossing_invocation_counts`, `non_qualifying_returned_crossing_invocation_indices`, `non_qualifying_returned_stage_invocation_indices`, `raised_crossing_invocation_indices`, `raised_stage_invocation_indices`, `stage_invocation_counts` |
| `declared_but_unused` | `candidate_ids`, `composition_binding_ids`, `pathway_binding_ids` |

The full practical examples under
`implementation/evidence/causal-pathway-binding/i116/` are the canonical field
examples for native, producer-mediated, explicit-adapter, diagnostic,
candidate, dynamic-choice, and multi-edge records. The I118 corpus freezes
their bytes and extends coverage to reviewed invalid-pair candidates,
unused declarations, non-qualifying returns, and raised effects.

### Candidate Mechanism And Review Artifacts

`causal_pathway_candidate_mechanism_evidence_v2` has the exact top-level fields
`artifact`, `schema_version`, `candidate_kind`, `mechanism_id`,
`proposed_source_pathway_id`, `proposed_target_pathway_id`,
`supported_relation`, and `executable_symbol`. `executable_symbol` has exactly
`binding_role`, `call_kind`, `module`, `qualified_symbol`, `source_path`,
`source_sha256`, and `symbol_id`.

`causal_pathway_candidate_relation_review_v2` has exactly `artifact`,
`schema_version`, `review_id`, `reviewer`, `review_status`, `candidate_id`,
`candidate_kind`, `proposed_source_pathway_id`,
`proposed_target_pathway_id`, `proposed_relation`,
`invalid_relabel_conflict_ids`, `invalid_relabel_blocked_claims`,
`mechanism_evidence`, `source_result_parameter`, `structural_distinction`, and
`review_digest`. Its expected digest is external trust input.

## Claim Qualification

Claim qualification is operation-scoped. A receipt proves only the callable
identities and outcomes listed in `actual_stage_symbol_invocations`; it does
not prove whole-run causal closure, qualify a direct call, or qualify the final
state of a runtime that may also have been changed outside the binding surface.
The lock and receipt therefore carry `claim_scope = bound_invocations_only`,
`whole_run_causal_closure_claimed = false`, and an explicit statement that
external or untracked causal input is not observable by the binding plane.

A declaration without a contract-qualified bound effect is visible but not
actual-use evidence. A raised call remains visible with effect `unknown`. A
non-raising return is classified by the trusted exact-symbol contract as one
of `committed`, `observed`, `rejected`, `no_op`, or `unknown`; only the first
two qualify. `False`, empty, and unreviewed results therefore cannot become
actual use merely because the callable returned. Producer result contracts can
also inspect a pinned boolean result attribute such as `state_mutated`, making
a normal “no eligible work” result an explicit `no_op`. Guarded mutators that
return `None` can instead pin a bound-instance snapshot method: equal canonical
pre/post digests classify as `no_op`, while a changed digest classifies as
`committed`.

The receipt's `effect_outcome_summary` gives exact stage and crossing counts,
claim-qualifying indices, non-qualifying returned indices, and raised indices.
Actual pathways, composition and candidate witnesses, dynamic actual-use
summaries, graph elements, and `claim_qualified` are all derived from the same
qualifying-effect predicate.

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
.venv/bin/python scripts/check_grc_lgrc_causal_pathway_binding_conformance.py \
  --acceptance-anchor "$TRUSTED_BINDING_ANCHOR_PATH" \
  --trusted-anchor-digest "$TRUSTED_BINDING_ANCHOR_DIGEST"

.venv/bin/python scripts/check_grc_lgrc_causal_pathway_binding_conformance.py \
  --lock path/to/causal-pathways.lock.json \
  --receipt path/to/causal-pathways.receipt.json \
  --acceptance-anchor "$TRUSTED_BINDING_ANCHOR_PATH" \
  --trusted-anchor-digest "$TRUSTED_BINDING_ANCHOR_DIGEST"
```

For a receipt that claims a registered composition, also supply its separately
trusted raw transcript digest with
`--trusted-execution-transcript-digest`. A reviewed candidate over an invalid
endpoint pair requires that option plus one
`--trusted-candidate-review-digest` for each accepted review. Neither value may
be discovered from the submitted lock or receipt and treated as its own trust
root.

Binding/source drift becomes `stale_pending_review` and blocks
claim-qualified artifacts. So does a missing anchor or a self-consistent map
that differs from the independently trusted anchor. BCF-020 also reconstructs
every receipted effect from the trusted contract and checks the aggregate
effect summary. The checker validates structure and provenance; it does not
dispatch or rerun causal dynamics.

## Boundaries

The layer supports versioned pathway binding and conservative provenance. It
does not provide universal causal routing, automatic selection, generic work
admission, native candidate formation, ecological interpretation, agency,
Read-Back, or N32.
