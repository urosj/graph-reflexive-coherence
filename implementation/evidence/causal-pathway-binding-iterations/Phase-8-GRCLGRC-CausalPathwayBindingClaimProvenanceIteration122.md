# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 122

**Iteration:** 122 — Runtime Scopes And State Ownership

**Status:** Passed

**Date:** 2026-08-20

**Production runtime behavior changed:** No

## Outcome

Iteration 122 makes live invocation state and evidence-scope coordination a
first-class provider responsibility. Invocation, crossing, and candidate
mechanism records; crossing and flow-derived result references; registered
composition scopes; dynamic-alternative scopes; candidate execution scopes;
row-specific dataflow contracts; and their witness derivations now live in
`scopes.py` without importing the temporary compatibility implementation or a
concrete session.

The change starts from the reviewed I121 checkpoint `6610873`. The temporary
compatibility implementation falls from 3,474 to 2,208 lines. The new runtime
scope provider occupies 1,503 lines behind the unchanged 48-name public
surface; the facade is 117 lines. The I119 identity provider remains 459 lines,
the I120 effects and authority providers remain 317 and 664 lines, and the
candidate provider is 1,763 lines after adding its narrow runtime protocol.

## Scope Provider

[`binding/scopes.py`](../../../src/pygrc/causal_pathways/binding/scopes.py) owns:

- `InvocationRecord`, `CrossingInvocationRecord`, and the private
  candidate-mechanism invocation record consumed by receipt construction;
- `CrossingResultReference` and `FlowDerivedInstanceReference`, including
  exact source-result retention and consumer-created equivalent-state binding;
- `CompositionExecutionScope`, `AlternativeSelectionScope`, and
  `CandidateExecutionScope`, including their ordered execution witnesses;
- registered row-specific object-flow and explicit-adapter dataflow contracts;
  and
- `AllowedPathwayAlternatives` and `BindingStateError`, preserving their exact
  public identities and signatures through the facade.

The provider imports only `candidates.py` and `identity.py`. It imports no
authority, effect, artifact, compatibility, or concrete session module.

## Cohesive Runtime State

The private `_RuntimeScopeState` collaborator now owns the complete live
execution concern:

- direct runtime-instance and transcript object-identity registries;
- stage, crossing, and candidate mechanism invocation ledgers;
- retained live invocation results used by flow-derived owner validation;
- global event ordering;
- composition, candidate, and alternative scope histories; and
- the three active-scope slots and their open, close, authorization, witness,
  and seal-completion rules.

`PathwayBindingSession` retains one `_runtime` collaborator instead of the 13
unrelated mutable fields above. Its public invocation-record properties and
artifact-building inputs expose immutable tuples from that owner. The session
continues to own declaration, link, phase, lock, and callable-identity caches,
which remain orchestration concerns until I123.

## Narrow Collaborator Boundaries

Scope objects use a structural one-method host solely to acquire their runtime
collaborator. `_RuntimeScopeState` itself uses a structural host exposing only
phase, lock, and the three declaration-membership predicates. No scope class
retains a concrete session.

`VerifiedCallable` and `VerifiedCompositionCrossing` also retain the runtime
collaborator and authority provider directly. Their invocation paths no longer
fan out through session methods for authorization, object-flow observation,
event recording, or result retention. Flow-derived source validation is an
encapsulated handle operation, so `BoundComposition` no longer reads another
object's private session, binding, pathway, stage, or composition fields.

The I121 candidate boundary becomes narrower as part of this extraction. Its
session protocol now supplies candidate construction operations plus one
runtime collaborator. A separate three-method `_CandidateRuntime` protocol
covers mechanism authorization, object-flow observation, and event recording;
`VerifiedCandidateMechanism` retains that collaborator instead of repeatedly
calling six broad session methods.

## Pressure Replay

The focused suite directly replayed 15 scope-sensitive controls:

- exact object-flow contracts for ordinary and special registered rows,
  including CMP-02 and CMP-04;
- exact source-result and distinct-carrier rejection for flow-derived owners;
- required explicit-adapter execution and owner continuity for CMP-26;
- declaration-only dynamic alternatives, one actual consumer-owned choice,
  out-of-set rejection, and second-branch rejection;
- distinct endpoint-owner rejection for CMP-04 and CMP-20;
- endpoint co-use outside a composition scope; and
- out-of-order composition execution.

All 15 passed directly and again as part of the complete focused suite. The
result preserves the central boundary: scoped endpoint use is necessary but
does not itself prove registered composition without exact runtime flow and
owner continuity.

## Dependency Boundary

The permanent provider direction after I122 is:

```text
identity -> effects -> authority -> candidates -> scopes
```

Providers may skip layers: candidates also imports identity directly, and
scopes imports candidates and identity. In import terms, no provider imports
`_legacy.py`; the compatibility module consumes all five providers. The public
facade imports scope-owned public objects directly.

All 48 root and facade exports retain exact object identity, signatures,
exception hierarchy, and I118-observed behavior. Internal defining-module
paths remain noncontractual.

## Architecture Enforcement

[I122 architecture tests](../../../tests/integrations/test_causal_pathway_binding_i122.py)
enforce:

- the scope provider's exact acyclic imports and structural one-method host;
- scope public ownership plus root/facade/provider object identity;
- ownership of the moved records, references, contracts, and scopes and their
  absence from `_legacy.py`;
- exclusive runtime-state ownership of all invocation ledgers, live result and
  object identity, event ordering, and active scopes;
- runtime-collaborator use by scopes and executable wrappers, plus the absence
  of the former cross-object private-field reads; and
- retained composition-flow, dynamic-choice, owner, adapter, and co-use
  pressure-test identities.

The I120 architecture gate now includes `scopes.py` in the complete provider,
compatibility-module, and facade import graph. The I121 gate enforces the
reduced candidate host and separate three-method runtime protocol.

## Related Files And Frozen Artifacts

Implementation and enforcement:

- [`binding/scopes.py`](../../../src/pygrc/causal_pathways/binding/scopes.py)
- [`binding/candidates.py`](../../../src/pygrc/causal_pathways/binding/candidates.py)
- [`binding/session.py`](../../../src/pygrc/causal_pathways/binding/session.py), the
  I123 successor to the temporary compatibility module
- [`binding/__init__.py`](../../../src/pygrc/causal_pathways/binding/__init__.py)
- [I122 architecture tests](../../../tests/integrations/test_causal_pathway_binding_i122.py)
- [I121 candidate-boundary tests](../../../tests/integrations/test_causal_pathway_binding_i121.py)
- [I120 dependency tests](../../../tests/integrations/test_causal_pathway_binding_i120.py)
- [focused binding and pressure tests](../../../tests/integrations/test_causal_pathway_binding.py)
- [binding conformance tests](../../../tests/integrations/test_causal_pathway_binding_conformance.py)

Frozen compatibility and authority inputs:

- [I118 public API freeze](../causal-pathway-binding/i118/I118PublicAPICompatibilityFreeze.json)
- [I118 artifact/runtime freeze](../causal-pathway-binding/i118/I118ArtifactRuntimeFreeze.json)
- [I118 checker-independence freeze](../causal-pathway-binding/i118/I118CheckerIndependenceFreeze.json)
- [I118 golden corpus](../causal-pathway-binding/i118/corpus)
- [binding acceptance anchor](../causal-pathway-binding/binding-acceptance-anchor.json)
- [binding conformance policy](../../../specs/grc-lgrc-causal-pathway-binding-conformance.json)
- [predecessor conformance policy](../../../specs/grc-lgrc-causal-pathway-conformance.json)

Planning and iteration control:

- [plan](../../Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenancePlan.md)
- [checklist](../../Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceChecklist.md)
- [I121 record](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration121.md)

## Verification

All commands used the repository `.venv` and `PYTHONPATH=src:.` where package
loading required it.

| Gate | Result |
| --- | --- |
| I118 API/artifact/runtime/checker freeze | Passed; 48 exports, 12 cases, 26 files |
| I122 architecture tests | 6/6 passed |
| Scope-sensitive pressure replay | 15/15 passed |
| Complete focused binding suite | 130/130 passed in 38.579 seconds |
| Binding conformance | 20/20 passed, zero issues; digest `eb54f646569cf4b91e5f410fe94d6bbd0aae6706871e83431ee9d919cc42c823` |
| Predecessor conformance | 20/20 passed, zero issues; digest `14a4ee2a4cc2dc4beca4ce056a15548df90ed4f0d33a707d33facc1a1ce1c6b2` |
| Binder-scoped Ruff | Passed |
| Binder-focused mypy under Python 3.12 | Passed; 21 source files |
| `compileall src tests scripts examples` | Passed |
| Standard-library provider discovery | Passed; 48 exports and exact scope identity |
| `git diff --check` | Passed |

The full project suite is intentionally not repeated in I122. The tranche plan
requires it after structural completion in I123 and again at I125 closeout.

## I123 Boundary

Iteration 123 may extract binding locks, receipts, use graphs, execution
transcript digests, claim-envelope construction, and canonical artifact
serialization into `artifacts.py`. It may create `session.py` for the remaining
declaration, linking, phase, identity-cache, freeze, seal, and collaborator
orchestration responsibilities and remove `_legacy.py`.

It must preserve the complete provider-first dependency direction, keep the
independent binding checker independently implemented, run the full project
suite after structural completion, and preserve the I118 oracle plus every
I122 scope, flow, ownership, and candidate-proof boundary.

I122 authorizes no artifact, session-phase, claim-envelope, checker,
conformance, or public API semantic change.
