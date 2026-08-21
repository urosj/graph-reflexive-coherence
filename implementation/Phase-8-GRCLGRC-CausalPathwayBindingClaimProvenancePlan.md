# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Plan

**Status:** Iterations 118-125 complete; accepted with I125-N01 nonblocking
evidence-reproducibility debt

**Identity:** `Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenance`

## Purpose

Add a binding plane between the completed causal-pathway knowledge plane and
the unchanged GRC/LGRC execution plane. Evidence-bearing consumers must either
bind an admitted pathway, bind an admitted registered composition, or declare
an explicitly unregistered candidate. The binding plane records identity,
source linkage, use, and claim provenance; it does not select or dispatch
causal dynamics.

```text
knowledge plane -> binding plane -> existing execution plane
```

The completed Iterations 105-111 remain authoritative and are consumed without
revision. Event-Local Geometry Integration remains closed. This tranche does
not select N32 or implement RCAE L04.

## Architectural Boundary

The layer is a linker/binder. It may resolve a declared pathway stage to a
current Python symbol and wrap that exact callable to record use. It must not
offer an intent router, a generic causal-work dispatcher, or one execution
interface shared by unlike mechanisms.

Allowed structural operations are:

```text
bind exact admitted pathway
bind exact registered composition
declare distinct experimental candidate
freeze declarations before execution
record invocations through verified mechanism-specific symbols
derive conservative structured claim provenance
```

Disallowed operations include:

```text
route(intent)
execute(pathway_id, generic_args)
automatic pathway selection
implicit composition from co-use
candidate promotion
registry or matrix rewriting
runtime-mechanics normalization
```

Legacy direct calls remain valid execution. They cannot appear among a
receipt's recorded bound evidence; an accepted operation-scoped receipt does
not establish their absence or qualify them.

## Authority Inputs

Iteration 112 freezes the final accepted versions of:

- the 23-pathway, 52-stage registry;
- the stage-local evidence crosswalk;
- the 26-row directional composition matrix;
- the evidence-derived selection guide;
- the Iteration 110 conformance policy and checker;
- the Iteration 111 result and closeout;
- current claim-boundary and reference documents;
- current source, test, and example trees.

The binding layer must fail closed when an accepted digest, source symbol, or
binding-map digest drifts. It may not replace accepted consolidation hashes
with historical intermediate bundle identities.

## Structural Model

The planned public model consists of:

- a repository-loaded immutable authority bundle;
- a binding session with explicit allowed pathway alternatives;
- admitted pathway and registered composition declarations;
- an explicit candidate declaration carrying unresolved authority and debt;
- verified callable links to exact mechanism-specific symbols;
- a pre-execution binding lock;
- an actual-use graph;
- an execution receipt;
- a structured claim envelope.

A verified callable link delegates to the real source callable. It records the
declared pathway, stage, symbol, invocation outcome, and owning binding before
and after delegation. It does not translate arguments into a common causal
ontology.

## Claim Derivation

Pathway-only use inherits only the pathway's registered supported-claim
ceiling and blocked claims. Registered composition use inherits the matrix
row's ceiling, ownership, adapter/producer cuts, and blocked relabels. Endpoint
claims never synthesize a stronger crossing claim.

Candidate presence forces `experimental_unregistered = true`. Invalid relabels
cannot be bound or rehabilitated as candidates. Unsupported crossings require
a distinct candidate identity. Multiple registered edges may be reported
together, but no larger semantic ceiling is synthesized unless that larger
composition is itself registered.

## Iteration 112: Pressure And Baseline

Freeze accepted authorities, protected trees, focused and full-suite results.
Pressure one linker model against:

1. pathway-only explicit packet transport;
2. producer-mediated `CMP-20` feedback eligibility into packet mechanics;
3. a bounded unregistered composition candidate.

Proceed only if all three preserve mechanism-specific execution, producer
ownership, candidate non-promotion, and conservative claims without a generic
dispatcher.

Deliverables:

- baseline freeze in Markdown and JSON;
- pressure report;
- accepted linker decision and rejected alternatives;
- no package-source behavior change.

## Iteration 113: Binding Map And Minimal Linker

Add a separate machine binding map rather than overloading the registry. Every
stage must resolve to one or more exact source symbols with module, qualified
symbol, binding role, call kind, stage relation, and current source hash.

Implement repository authority loading, exact pathway/composition binding,
candidate declaration, allowed dynamic alternatives, and verified callable
links. Unknown, unsupported, invalid, ambiguous, or undeclared identities fail
closed. Run focused tests without broad repository enforcement.

## Iteration 114: Lock, Use Graph, Receipt, And Claims

Freeze a pre-execution lock containing all accepted authority digests,
binding-map identity, declared pathways/stages/compositions, producers,
adapters, residue, candidates, allowed alternatives, and pre-execution claim
envelope.

After bound calls, emit a receipt containing actual successful and failed
uses, declared-but-unused bindings, undeclared-use violations, exercised
registered compositions, candidate use, use graph, and conservative claims.
Pressure dynamic A/B choice and multi-edge constructions without allowing the
binder to choose or synthesize semantics.

## Iteration 115: Conformance And Adversarial Enforcement

Extend the existing conformance approach with binding-specific rules and
target-isolated negative controls. At minimum enforce identity resolution,
symbol existence/hash currency, lock/receipt linkage, declared use, ownership
retention, candidate non-promotion, diagnostic and invalid boundaries,
configured-versus-formed boundaries, ambiguity, chained claims, and unbound
non-qualification.

General digest guards must be suppressed or rebased during target-only rule
isolation so each semantic rule proves its own failure detection.

## Iteration 116: Consumer Dry Runs And Closeout

Exercise pathway-only, producer, adapter, diagnostic, ambiguity, unsupported,
invalid, candidate, dynamic-choice, and multi-edge cases. Run one low-context
consumer replay from public binding documentation and frozen machine
authorities, then validate its lock, graph, and receipt against a separately
held oracle after replay freeze.

Close only after focused, affected GRC/LGRC, existing consolidation, full-suite,
negative-control, replay/restoration, formatting, and protected-behavior checks
pass.

## Round-Four R4-B01 Correction

Close the remaining reviewed-candidate continuity gap without adding a generic
dispatcher. Preserve the existing `target(**request)` consumer call shape, but
have the reviewed candidate handle expose a provenance-carrying request
mapping. The runtime transcript must bind one qualifying source-result object
to the candidate argument, the distinct candidate-result object to the exact
expanded target request, and the target request to its declared binding,
pathway, and symbol. Candidate use fails closed when the target instead receives
equivalent hard-coded values.

BCF-011 and BCF-019 independently reconstruct that three-event relationship
from the externally trusted raw transcript. A coherently resealed receipt that
removes or invents the target-request derivation must not retain an accepted
experimental edge.

## Round-Five R5-B01 Correction

Join source-code review authority to runtime argument identity. The separately
trusted invalid-pair review must use schema v2 and name one exact
`source_result_parameter` in the content-addressed candidate callable. The
runtime must require the qualifying source-result object at that parameter,
whether the call used positional or keyword syntax; a matching object in any
other argument is irrelevant.

The checker must independently establish that the reviewed parameter exists,
is referenced by the pinned callable's returned mapping, equals the witness's
`candidate_argument_name`, and carries the qualifying source descriptor in the
raw candidate invocation. A source object passed only through unused context
must not retain an experimental edge.

## Round-Six R6-B01 Correction

Join the frozen source parameter to the exact target-request value, not merely
to syntax in the candidate return. For the candidate-result path expanded into
the target call, derive source-present and source-absent mappings through a
small side-effect-free AST evaluator. Both must be canonical nonempty request
mappings, their digests must differ, and the live target request must match the
source-present digest.

Freeze the path and both counterfactual digests in raw request flow. BCF-011 and
BCF-019 must validate that record and independently reconstruct it from the
content-addressed executable. Equal-branch and algebraically neutral source
expressions must not retain an experimental edge.

## Round-Seven R7-B01 Correction

Define source absence by the pinned callable's real omission contract. Require
the reviewed parameter to have a safely reconstructable default, verify that
default against the loaded signature, and use it for the selected request-path
counterfactual. Required parameters and unsupported defaults fail closed.

Version the raw dependency proof to freeze the default digest and the exact
source-present and source-omitted request digests. The checker must independently
reconstruct the default and omitted request from content-addressed source. A
non-`None` default that produces the same request as the live source must not
retain a reviewed candidate edge.

## Round-Eight R8-B01 Correction

Preserve the exact recursive Python type of every admitted omission default.
The safe evaluator must distinguish list and tuple literals, and the frozen
default digest must distinguish `None`, booleans, integers, floats, strings,
lists, tuples, and string-keyed mappings at every nesting level. Compare that
typed digest with the loaded signature before evaluating the counterfactual.

Evaluate equality, concatenation, and every other admitted operator with those
Python values before canonical request serialization. Runtime and checker must
produce the same proof as direct Python supplied-versus-omitted behavior for
the frozen default matrix or fail closed. In particular, a tuple default tested
against an empty list must not manufacture a dependency.

## Post-Acceptance Callable-Identity Cache

Keep full content-addressed verification at link and lock boundaries, but cache
the resolved source path, verified source digest, definition identity, and
canonical callable-identity record within the session. Key source verification
by resolved path so multiple symbols in one source do not repeat the file hash.

On every invocation, continue to re-resolve the symbol and compare callable
object identity. Replace the unconditional source hash and source-path
resolution with one `(st_mtime_ns, st_size)` comparison. Stamp drift must force
the pinned SHA-256 check before delegation; mismatched content fails closed,
while identical content refreshes the stamp for subsequent calls.

## Iterations 118-125: Modular Binder Architecture And Guidance

Refactor the binder's internal architecture without changing its public API,
artifact schemas, or canonical output bytes. The current implementation is a
roughly 6.3-KLOC module with dozens of top-level classes, a state-heavy
`PathwayBindingSession`, and frequent cross-class access to `_`-prefixed
attributes and methods. The public surface in `pygrc.causal_pathways` is clean;
Iterations 118-125 make the implementation boundary match that surface.

This is a refactor and usability tranche, not an architectural correction.
The accepted binder already links declared causal identity to exact executable
use, evidence provenance, and a bounded claim without selecting mechanisms for
the consumer or becoming a generic causal-work executor. Preserve that
mechanism-specific execution model and its explicit
`semantic_selection_performed_by_binder = false` boundary.

The documentation must keep the binder's observability boundary prominent. A
binding receipt certifies the causal operations represented in that receipt
under `bound_invocations_only`; it is not proof that no unbound operation or
other influence affected the containing process or experiment. A consumer
making a whole-experiment causal claim must establish its own closed evidence
boundary around the receipts. This tranche must not present the binder as a
process-wide causal monitor.

Replace the monolith with an internal package organized around explicit
responsibilities:

```text
pygrc/causal_pathways/binding/
  __init__.py   compatibility exports for the existing binding module surface
  identity.py   callable/source verification and canonical identity helpers
  effects.py    effect contracts, classification, and evidence records
  authority.py  accepted authority loading, admission, and staleness
  candidates.py candidate declarations, reviews, proofs, and witnesses
  scopes.py     runtime evidence scopes and invocation records
  artifacts.py pure lock, receipt, graph, and claim-envelope construction
  session.py    orchestration and mutation ownership
```

Candidate continuation is a first-class internal subsystem, distinct from the
ordinary admitted-binding path. `candidates.py` owns candidate declarations,
mechanism evidence, relation review, verified candidate mechanisms, request
provenance, invalid-relabel constraints, exact source-result consumption,
omission counterfactuals, type-preserving defaults, and candidate execution
witnesses. This keeps the unusually defensive BCF-011 boundary concentrated in
the exceptional candidate path instead of redistributing it across effects,
scopes, and session orchestration.

Freeze the permitted dependency direction rather than requiring only generic
acyclicity. In dependency-provider-first order, the layers are:

```text
identity
  -> effects
  -> authority
  -> candidates
  -> scopes
  -> artifacts
  -> session
```

Each module may import only preceding layers in that list; dependencies may
skip layers. In particular, `identity.py` should use only the standard library
where practical; `effects.py` may depend on identity; `authority.py` on
identity and effects;
`candidates.py` on identity, effects, and authority; `scopes.py` on identity,
effects, candidates, and narrow protocols; `artifacts.py` on authority,
effects, candidates, and scopes; and `session.py` may orchestrate all preceding
modules. `scopes.py` must never depend on the concrete
`PathwayBindingSession`. A small private `protocols.py` is permitted only if
actual dependency pressure requires it, not as a default extra layer.

Assign the following cohesive responsibilities:

- `identity.py`: canonical digests, source-file verification,
  `CallableIdentity`, `SourceSymbolBinding`, `CompositionCrossingBinding`,
  callable resolution/fingerprinting, and source-manifest semantics, without
  claim interpretation.
- `effects.py`: `EffectOutcomeContract`, return/effect classification, effect
  evidence, effect-level runtime object descriptors, and only those
  source-dependency primitives that are not candidate-specific.
- `authority.py`: `CausalPathwayAuthority`, `BindingAcceptanceAnchor`, registry,
  matrix, and binding-map loading, staleness, admission lookup, and accepted
  effect contracts. Loaded authority state should remain mostly immutable.
- `candidates.py`: the complete candidate subsystem described above, kept
  separable from ordinary admitted binding.
- `scopes.py`: invocation, crossing, and candidate invocation records;
  composition, alternative-selection, and candidate execution scopes; and
  crossing and flow-derived references. Scopes depend on a narrow recorder or
  provenance protocol rather than the session implementation.
- `artifacts.py`: near-pure construction and canonicalization of binding locks,
  receipts, pathway-use graphs, claim envelopes, execution transcript digests,
  and canonical serialization from immutable input records.
- `session.py`: orchestration only, including phase transitions, declarations,
  link registration, active scopes, runtime ledgers, binding handles, freeze,
  and seal. Bound handles and verified callables may live here, but effect,
  authority, and artifact-derivation algorithms may not.

Keep `pygrc.causal_pathways` and `pygrc.causal_pathways.binding` behaviorally
compatible. Before the refactor, freeze public symbol names, import paths,
class and function signatures, method signatures, exception types and
important exception conditions, context-manager behavior, and return object
types in a machine-readable `I118PublicAPICompatibilityFreeze.json` or
equivalent. Internal module paths are explicitly non-contractual. Digest field
names, schema versions, canonical ordering, serialized values, and
lock/receipt/conformance bytes must not change.

Reduce nominal encapsulation by introducing explicit internal collaborator
interfaces. `PathwayBindingSession` remains the public orchestration object but
must not remain a bag of unrelated mutable fields: group runtime ledgers and
scope, object-flow identity, and artifact state behind cohesive owners. Bound
pathways, compositions, candidate scopes, and verified callables should call
narrow collaborator methods instead of reading another object's raw
`_session`, `_binding_id`, or mutable ledgers. Enforce the dependency DAG,
including the absence of concrete session dependencies from scope, effect, and
artifact collaborators, with an architecture test.

Freeze before-refactor canonical bytes and digests for the full practical
accepted I115/I116 binder fixture corpus, not merely representative outputs.
The corpus must cover at least native pathways; producer, adapter, and
diagnostic compositions; dynamic choice; candidate pathways and compositions;
reviewed invalid-pair candidates; unused declarations; non-qualifying returned
effects; raised effects; and multi-edge graphs. Identical frozen inputs must
produce byte-identical locks, receipts, conformance outputs, negative-control
outputs, schemas, fields, ordering, and digests after the refactor. Bound
executions must also preserve runtime state, results, return types, exception
behavior, and context-manager behavior.

Keep the independent binding conformance checker epistemically independent.
It may share schemas or constants where harmless, but it must not import
load-bearing semantic derivation or validation implementations from the new
binder package for binding semantics digests, source manifests, effect
contracts, candidate source dependencies, composition dataflow, claim
envelopes, witnesses, or claim qualification.

Add runnable binder examples for an admitted pathway, a registered
composition, an explicit dynamic choice, and an unregistered candidate with
conservative claim handling. Add a fifth example contrasting valid direct
unbound use, which is deliberately supported but not claim-qualified, with a
bound evidence-bearing invocation.

Build the user-and-agent guide around the conceptual sequence `select -> bind
-> lock -> execute -> seal -> validate`: selection remains consumer-owned;
binding links the selected identity to exact mechanism-specific symbols; lock
freezes expected causal architecture and claim ceiling; execution uses verified
handles; seal derives actual use, witnesses, graph, and claim envelope; and
validation independently checks the receipt against authority and trust
anchors. Present `declare candidate -> experimental provenance` as the path
when no relation is admitted, never invention of a native path identifier.

Revise the stable binding reference so its public API, behaviors, and exact
artifact-field descriptions map to the modular implementation without making
internal paths contractual. Describe the final candidate contract directly;
keep historical R4-B01 through R8-B01 correction chronology in implementation
and audit evidence rather than requiring it in the user-facing guide.

Update every repository-level discovery surface affected by those additions,
including the root README, `docs/README.md`, `docs/reference/README.md`, the
claim-boundary index, `examples/README.md`, `specs/README.md`, and any more
specific example/reference indexes introduced during implementation.

## Iteration 118: Compatibility And Refactor Baseline

Create the machine-readable public behavioral API freeze, freeze the full
practical I115/I116 artifact and runtime corpus, add compatibility and
golden-byte tests, add the independent-checker import guard, and record the
pre-refactor focused and full-suite baselines. This iteration changes tests and
evidence only, not binder runtime code.

Iteration 118 passed with a 48-export public API freeze, 12-case regenerated
artifact/runtime corpus, 26-file canonical I115/I116 manifest, independent
checker guard, 109 focused tests, and 1,320 full-suite tests. See the
[Iteration 118 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration118.md).

### Related files and artifacts

- Iteration control: the
  [I118 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration118.md),
  [plan](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenancePlan.md), and
  [checklist](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceChecklist.md).
- Frozen production inputs: the
  [`pygrc.causal_pathways` public surface](../src/pygrc/causal_pathways/__init__.py),
  pre-refactor binder monolith identified by the I118 source commit, path, and
  SHA-256, its current
  private compatibility successor (removed in I123; see
  [`session.py`](../src/pygrc/causal_pathways/binding/session.py)),
  [project configuration](../pyproject.toml), and
  [binding acceptance anchor](evidence/causal-pathway-binding/binding-acceptance-anchor.json).
- Authority specifications: the
  [pathway registry](../specs/grc-lgrc-causal-pathway-contracts.json),
  [evidence crosswalk](../specs/grc-lgrc-causal-pathway-evidence-crosswalk.json),
  [composition matrix](../specs/grc-lgrc-causal-pathway-composition-matrix.json),
  [selection guide](../specs/grc-lgrc-causal-pathway-selection-guide.json),
  [pathway conformance policy](../specs/grc-lgrc-causal-pathway-conformance.json),
  [binding map](../specs/grc-lgrc-causal-pathway-bindings.json), and
  [binding conformance policy](../specs/grc-lgrc-causal-pathway-binding-conformance.json).
- Builders and checkers: the
  [I118 freeze builder](../scripts/build_phase8_causal_pathway_binding_i118.py),
  [I116 corpus builder](../scripts/build_phase8_causal_pathway_binding_i116.py),
  [binding conformance checker](../scripts/check_grc_lgrc_causal_pathway_binding_conformance.py),
  and [predecessor pathway checker](../scripts/check_grc_lgrc_causal_pathway_conformance.py).
- Tests and fixtures: the
  [I118 enforcement tests](../tests/integrations/test_causal_pathway_binding_i118.py),
  [core binder tests](../tests/integrations/test_causal_pathway_binding.py),
  [binding conformance tests](../tests/integrations/test_causal_pathway_binding_conformance.py),
  [I116 tests](../tests/integrations/test_causal_pathway_binding_i116.py), and
  [reviewed CMP-05 mechanism fixture](../tests/fixtures/causal_pathway_candidate_cmp05_distinct_mechanism_evidence.json).
- I118 machine evidence: the
  [public API freeze](evidence/causal-pathway-binding/i118/I118PublicAPICompatibilityFreeze.json),
  [artifact/runtime freeze](evidence/causal-pathway-binding/i118/I118ArtifactRuntimeFreeze.json),
  [checker-independence freeze](evidence/causal-pathway-binding/i118/I118CheckerIndependenceFreeze.json),
  [baseline execution record](evidence/causal-pathway-binding/i118/I118BaselineExecution.json),
  and [supplemental corpus](evidence/causal-pathway-binding/i118/corpus/).
- Inherited accepted evidence: the
  [I115 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration115.md),
  [I116 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration116.md),
  [I117 correction record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration117IndependentAuditCorrections.md),
  [I116 corpus](evidence/causal-pathway-binding/i116/), I115
  [native lock](evidence/causal-pathway-binding/i115-native-pathway.lock.json),
  [native receipt](evidence/causal-pathway-binding/i115-native-pathway.receipt.json),
  [conformance execution](evidence/causal-pathway-binding/i115-conformance-execution.json),
  [negative-control execution](evidence/causal-pathway-binding/i115-negative-control-execution.json),
  and [I116 low-context consumer specification](evidence/causal-pathway-binding/i116-low-context-consumer-specification.json).

The artifact/runtime freeze is the authoritative exhaustive 26-file inherited
manifest; this subsection is the human navigation index.

## Iteration 119: Package Boundary And Identity Foundation

Atomically replace `binding.py` with the `binding/` package; never leave the
module and package present together. Preserve the unchanged monolith
temporarily as a private implementation module behind `binding/__init__.py`,
then extract `identity.py`. Keep every public re-export stable. Move tests away
from private monolith patch points such as `binding.inspect` and
`binding._load_json`; those hooks are not part of the public compatibility
freeze.

Iteration 119 passed with an atomic module-to-package replacement, a 48-export
compatibility facade, a session-independent `identity.py` provider, explicit
architecture enforcement, removal of the two private monolith test hooks, 114
focused tests, byte-identical I118 corpus output, and both 20-rule conformance
policies. The full project suite remains at the accepted 1,320-test I118
baseline and is next required after structural completion in I123. See the
[Iteration 119 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration119.md).

## Iteration 120: Effects And Authority

Extract `effects.py` and `authority.py`, keep loaded authority state mostly
immutable, and establish the first permanent dependency chain `identity ->
effects -> authority` without changing session behavior.

Iteration 120 passed with effect classification and evidence isolated in an
identity-dependent `effects.py`, authority and acceptance loading isolated in
`authority.py`, an enforced acyclic provider graph, defensive/read-only loaded
authority state, 119 focused tests, byte-identical I118 corpus output, and both
20-rule conformance policies. The full project suite remains deferred to the
planned I123 structural-completion gate. See the
[Iteration 120 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration120.md).

## Iteration 121: Candidate Subsystem

Extract candidate declarations, relation reviews, mechanism evidence, verified
mechanisms, request wrappers, AST and default evaluation, source-consumption
proofs, and invalid-relabel controls into `candidates.py`. Introduce the narrow
factory or recorder protocol needed to avoid candidate/session/scope cycles.
Replay the candidate-focused R4-R8 regressions and mutation pressures at this
checkpoint.

Iteration 121 passed with candidate declaration and invalid-relabel validation,
review authority, executable identity, request provenance, type-preserving
omission counterfactuals, source-dependency proofs, and candidate witness
construction isolated in `candidates.py`. A six-method structural host protocol
and two runtime adapters avoid a candidate/session/scope import cycle. The I118
oracle remained byte-stable, all 124 focused tests passed, both 20-rule
conformance policies retained their accepted digests, and the R4-B01 through
R8-B01 regressions plus candidate mutation controls replayed successfully. The
full project suite remains deferred to the planned I123 structural-completion
gate. See the
[Iteration 121 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration121.md).

## Iteration 122: Runtime Scopes And State Ownership

Extract invocation records, result references, composition scopes, alternative
scopes, and candidate scopes into `scopes.py`. Replace concrete session access
with narrow protocols and introduce cohesive owners for invocation ledgers,
active scopes, object-flow identity, and related runtime state. Replay
composition-flow, dynamic-choice, and owner-erasure pressures.

Iteration 122 passed. Invocation, crossing, and candidate mechanism records;
crossing and flow-derived references; and all three execution scopes now live
in `scopes.py`. A cohesive runtime-state collaborator owns invocation ledgers,
retained results, deterministic object identity, event ordering, and active
scope state. Scope objects and executable wrappers retain that collaborator
instead of a concrete session, and candidate execution uses a three-method
runtime protocol. The I118 oracle remained byte-stable, all 130 focused tests
passed, both 20-rule conformance policies retained their accepted digests, and
the 15 composition-flow, dynamic-choice, producer/adapter-owner, and endpoint
co-use pressures replayed successfully. The full project suite remains
deferred to the planned I123 structural-completion gate. See the
[Iteration 122 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration122.md).

## Iteration 123: Artifacts And Session Consolidation

Extract lock, receipt, use-graph, transcript, and claim-envelope construction
into `artifacts.py`. Reduce `session.py` to phase control, declarations,
linking, binding handles, freeze, seal, and collaborator orchestration. Remove
the temporary monolith and enforce the complete dependency DAG with the
architecture test.

Iteration 123 passed. Canonical lock, receipt, use-graph, transcript, and
claim-envelope construction now lives in the session-independent
`artifacts.py` provider. Binding handles and the remaining declaration, link,
phase, identity-cache, freeze, seal, and collaborator orchestration live in
`session.py`, with cohesive state owners rather than a flat mutable session.
The temporary `_legacy.py` module is removed and the complete provider-first
dependency DAG is enforced. The I118 oracle remained byte-stable, all 137
focused tests passed, the full 1,348-test project suite passed, and both 20-rule
conformance policies retained their accepted digests. See the
[Iteration 123 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration123.md).

## Iteration 124: Binder Examples And Guidance

Add the five runnable examples, the user-and-agent guide, the revised stable
reference, the operation-scoped provenance warning, and all repository
discovery links. Perform this only after the public implementation surface has
settled.

Iteration 124 passed. Five runnable examples now cover admitted pathway use,
registered composition, both branches of consumer-owned dynamic choice, an
executable unregistered candidate, and direct-unbound versus bound execution.
The new user-and-agent guide covers `select -> bind -> lock -> execute -> seal
-> validate`, failures, debugging, conformance, and safe extension. The stable
reference lists all 48 frozen exports, exact V1 lock/receipt fields, and the
final candidate contract directly without making internal modules
contractual. All planned repository discovery surfaces now link both guides and
the examples. The I118 oracle remained byte-stable, all 143 focused tests
passed, and both 20-rule conformance policies retained their accepted digests.
See the
[Iteration 124 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration124.md).

## Iteration 125: Independent Pressure And Closeout

Compare the complete frozen API, artifact, and runtime corpus; replay every
mutation falsifier and the accepted 68-case independent gate when its exact
harness is retained; otherwise record the retention gap and require explicitly
approved independent successor pressure over the same boundaries. Run both
conformance policies, all examples, the full project suite, and all static
checks; close only with no attributable semantic, artifact, or runtime
differences.

Iteration 125 passed with disposition `accept_with_nonblocking_debt`. The
independent audit found zero blockers, zero majors, and one minor
evidence-retention debt. All 48 public exports matched, the runtime probe and
39-file evidence corpus were byte-identical, 21 new independent
mutations/falsifiers and all retained semantic controls passed, the focused
suite passed 143/143, the full suite passed 1,354/1,354, both conformance
policies passed 20/20, and all examples and static gates passed. The historical
external 68-case harness is unavailable, so exact replay is not claimed; the
independently reconstructed successor pressure plus retained focused controls
is explicitly accepted as the I125 replacement gate, with I125-N01 retained as
nonblocking evidence-reproducibility debt. See the
[Iteration 125 record](evidence/causal-pathway-binding-iterations/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration125.md),
[independent audit](evidence/causal-pathway-binding-iterations/CausalPathwayBindingIndependentAudit.md), and
[canonical closeout](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceCloseout.md).
The complete supporting sequence is indexed in the
[iteration and audit evidence package](evidence/causal-pathway-binding-iterations/README.md).

Every code-moving iteration ends in a reviewable checkpoint commit. Run the
focused binder tests, public compatibility freeze, golden corpus, conformance
checks, Ruff, mypy, compileall, and `git diff --check` before proceeding to the
next iteration. Run the full suite in Iteration 118, after the production
refactor becomes structurally complete in Iteration 123, and again at the
Iteration 125 closeout.

Acceptance requires the public behavioral compatibility freeze, the internal
dependency test, exhaustive practical-corpus golden-byte comparison, and
before/after runtime-state and result comparison. Replay mutation falsifiers
for erased producer/adapter owners, source-symbol substitution, candidate
native promotion, diagnostic-to-behavioral and configured-to-formed relabels,
unsupported composition admission, a second dynamic branch, claim-envelope
widening, endpoint co-use without composition flow, hard-coded candidate target
requests, source-present-but-unused candidates, and stale source content. Each
relevant independent gate must still fail closed.

The current 1,354-test project suite, both 20-rule conformance policies, all
examples, Ruff, mypy, compileall, and diff checks passed. Closure found zero
semantic, artifact, or runtime differences attributable to the refactor. The
unavailable historical 68-case script is not represented as replayed; its
successor pressure is accepted under the explicit I125-N01 debt above.

## Maximum Claim

If Iterations 112-116 pass, the layer may claim versioned pathway binding and
claim provenance for evidence-bearing GRC/LGRC consumers while existing
mechanism-specific execution remains unchanged.

Iterations 118-125 do not expand that maximum claim.

It may not claim universal causal routing, generic work admission, automatic
selection, native candidate formation, ecological interpretation, agency,
Read-Back, or N32.

## Closeout

Iterations 112-125 are complete. The canonical tranche result is
[the closeout](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceCloseout.md),
with iteration records, prospective conformance evidence, independent I125
audit reports, ten consumer dry runs, the low-context post-freeze oracle, and
I125-N01 retained under this identity.
