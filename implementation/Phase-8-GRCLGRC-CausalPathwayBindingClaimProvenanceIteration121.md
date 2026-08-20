# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 121

**Iteration:** 121 — Candidate Subsystem

**Status:** Passed

**Date:** 2026-08-20

**Production runtime behavior changed:** No

## Outcome

Iteration 121 makes candidate admission and proof construction a first-class
provider responsibility. Candidate declarations, mechanism evidence, relation
reviews, invalid-relabel controls, verified mechanisms, request provenance,
typed source defaults, omission counterfactuals, source-dependency proofs, and
candidate witnesses now live in `candidates.py` without importing the temporary
compatibility implementation or its concrete session and scope classes.

The change starts from the reviewed I120 checkpoint `0b0de21`. The temporary
compatibility implementation falls from 4,979 to 3,474 lines. The new candidate
provider occupies 1,757 lines behind the unchanged 48-name public surface; the
facade is 115 lines. The I119 identity provider remains 459 lines, the I120
effects provider remains 317 lines, and the I120 authority provider remains 664
lines.

## Candidate Provider

[`binding/candidates.py`](../src/pygrc/causal_pathways/binding/candidates.py)
owns:

- `CandidateDeclaration`, `CandidateMechanismEvidence`,
  `CandidateRelationReview`, `CandidateUseRecord`, and
  `InvalidCandidateError`;
- authority-coordinate completion, invalid-relabel detection, semantic
  restatement rejection, independently trusted structural reviews, and the
  declaration factory;
- exact candidate source loading, content-address verification, alias
  rejection, callable identity guards, and `VerifiedCandidateMechanism`;
- candidate request wrappers that preserve nested mapping and scalar object
  identity through target keyword expansion;
- the restricted AST expression evaluator, recursively type-preserving default
  records, omission counterfactuals, and source-dependent request proofs; and
- reviewed target-request flow, source-to-candidate-to-target dataflow, and
  completed candidate-use witness construction.

The candidate provider replaces its former internal use of the broad public
`BindingStateError` with a private request-normalization failure. That failure
is still caught at the same boundaries and does not change any public exception,
result, artifact, or claim behavior.

## Runtime Host Boundary

`candidates.py` defines a structural `PathwayBindingSession` protocol solely to
preserve the frozen public annotation while requiring only six operations:

- cached callable-identity guard acquisition;
- candidate evidence-scope creation;
- verified-mechanism lookup;
- active-scope invocation authorization;
- runtime object-flow observation; and
- candidate mechanism event recording.

The provider imports only `authority.py` and `identity.py`. It does not import
`_legacy.py`, a concrete session, or a concrete scope. The runtime supplies two
small adapters added in I121: one creates its concrete candidate scope and one
translates a candidate-owned event into the existing invocation ledger record.
`PathwayBindingSession.declare_candidate(...)` retains its exact signature but
now performs phase control, invokes `_build_candidate_declaration(...)`, and
stores the returned declaration and optional mechanism handle.

Candidate execution scope ownership remains intentionally in `_legacy.py` for
I122. Its target-request and exercise-witness methods delegate their proof work
to the candidate provider while retaining active-scope state and ledger
orchestration.

## Pressure Replay

The focused suite replays the complete candidate surface. The I121 architecture
gate explicitly retains and the focused run executes the five sequential audit
regressions:

- R4-B01: an ignored candidate mapping cannot form the target request;
- R5-B01: source presence in an unused argument cannot substitute for the
  reviewed source parameter;
- R6-B01: a syntactic source mention with equal results is not dependency;
- R7-B01: omission uses the callable's frozen actual default; and
- R8-B01: tuple and list defaults remain type-distinct.

It also retains the forged-module alias, semantic-paraphrase, metadata-only,
stale-content-address, and reviewed synonym/no-op mutation controls. All remain
fail-closed after extraction.

## Dependency Boundary

The permanent provider direction after I121 is:

```text
identity -> effects -> authority
    \                    \
     +------------------> candidates
```

The arrows express foundation-to-consumer layering. In import terms,
`identity.py` is a leaf, `effects.py` imports identity, `authority.py` imports
effects and identity, and `candidates.py` imports authority and identity.
`_legacy.py` consumes all four providers; none imports `_legacy.py`.

The public facade imports candidate-owned public objects directly. All 48 root
and facade exports retain exact object identity, signatures, exception
hierarchy, and I118-observed behavior. Internal defining-module paths remain
noncontractual.

## Architecture Enforcement

[I121 architecture tests](../tests/integrations/test_causal_pathway_binding_i121.py)
enforce:

- the candidate provider's exact acyclic imports and structural six-method host;
- candidate public ownership plus root/facade/provider object identity;
- ownership of candidate validation, request, proof, and witness primitives and
  their absence from `_legacy.py`;
- a thin session declaration adapter with no retained candidate validation; and
- retained R4-B01 through R8-B01 and mutation-pressure test identities.

The I120 architecture gate now includes `candidates.py` in the full provider,
compatibility-module, and facade import graph while preserving every earlier
identity, effect, and authority dependency assertion.

## Related Files And Frozen Artifacts

Implementation and enforcement:

- [`binding/candidates.py`](../src/pygrc/causal_pathways/binding/candidates.py)
- [`binding/_legacy.py`](../src/pygrc/causal_pathways/binding/_legacy.py)
- [`binding/__init__.py`](../src/pygrc/causal_pathways/binding/__init__.py)
- [I121 architecture tests](../tests/integrations/test_causal_pathway_binding_i121.py)
- [I120 dependency tests](../tests/integrations/test_causal_pathway_binding_i120.py)
- [focused binding and pressure tests](../tests/integrations/test_causal_pathway_binding.py)
- [binding conformance tests](../tests/integrations/test_causal_pathway_binding_conformance.py)

Frozen compatibility and authority inputs:

- [I118 public API freeze](evidence/causal-pathway-binding/i118/I118PublicAPICompatibilityFreeze.json)
- [I118 artifact/runtime freeze](evidence/causal-pathway-binding/i118/I118ArtifactRuntimeFreeze.json)
- [I118 checker-independence freeze](evidence/causal-pathway-binding/i118/I118CheckerIndependenceFreeze.json)
- [I118 golden corpus](evidence/causal-pathway-binding/i118/corpus)
- [binding acceptance anchor](evidence/causal-pathway-binding/binding-acceptance-anchor.json)
- [binding conformance policy](../specs/grc-lgrc-causal-pathway-binding-conformance.json)
- [predecessor conformance policy](../specs/grc-lgrc-causal-pathway-conformance.json)

Planning and iteration control:

- [plan](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenancePlan.md)
- [checklist](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceChecklist.md)
- [I120 record](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration120.md)

## Verification

All commands used the repository `.venv` and `PYTHONPATH=src:.` where package
loading required it.

| Gate | Result |
| --- | --- |
| I118 API/artifact/runtime/checker freeze | Passed; 48 exports, 12 cases, 26 files |
| I121 architecture tests | 5/5 passed |
| R4-B01 through R8-B01 direct replay | 5/5 passed |
| Complete focused binding suite | 124/124 passed |
| Binding conformance | 20/20 passed, zero issues; digest `eb54f646569cf4b91e5f410fe94d6bbd0aae6706871e83431ee9d919cc42c823` |
| Predecessor conformance | 20/20 passed, zero issues; digest `14a4ee2a4cc2dc4beca4ce056a15548df90ed4f0d33a707d33facc1a1ce1c6b2` |
| Binder-scoped Ruff | Passed |
| Binder-focused mypy under Python 3.12 | Passed; 17 source files |
| `compileall src tests scripts examples` | Passed |
| Standard-library provider discovery | Passed |
| `git diff --check` | Passed |

The full project suite is intentionally not repeated in I121. The tranche plan
requires it after structural completion in I123 and again at I125 closeout.

## I122 Boundary

Iteration 122 may extract invocation, crossing, and candidate records; crossing
and flow-derived references; and composition, alternative-selection, and
candidate execution scopes into `scopes.py`. It may introduce cohesive owners
for invocation ledgers, active-scope state, and runtime object-flow identity,
using narrow collaborator protocols instead of concrete session dependencies.
It must replay composition-flow, dynamic-choice, and owner-erasure pressures and
preserve the I118 oracle plus every I121 dependency and candidate-proof rule.

I121 authorizes no artifact, session-phase, claim-envelope, checker,
conformance, or public API semantic change.
