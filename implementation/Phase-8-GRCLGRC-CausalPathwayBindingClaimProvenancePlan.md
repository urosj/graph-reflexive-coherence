# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Plan

**Status:** Round-five R5-B01 corrected author-side; full independent re-audit
pending

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

## Maximum Claim

If Iterations 112-116 pass, the layer may claim versioned pathway binding and
claim provenance for evidence-bearing GRC/LGRC consumers while existing
mechanism-specific execution remains unchanged.

It may not claim universal causal routing, generic work admission, automatic
selection, native candidate formation, ecological interpretation, agency,
Read-Back, or N32.

## Closeout

Iterations 112-116 are complete. The canonical tranche result is
[the closeout](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceCloseout.md),
with iteration records, prospective conformance evidence, ten consumer dry
runs, and the low-context post-freeze oracle retained under this identity.
