# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 123

**Iteration:** 123 — Artifacts And Session Consolidation

**Status:** Passed

**Date:** 2026-08-20

**Production runtime behavior changed:** No

## Outcome

Iteration 123 completes the binder's internal modular architecture. Canonical
binding locks, receipts, pathway-use graphs, execution transcripts,
claim-envelope derivation, effect summaries, declared-versus-used projections,
and JSON artifact serialization now live in `artifacts.py`. Binding handles and
the remaining phase, declaration, link, freeze, seal, callable-identity cache,
and collaborator orchestration now live in `session.py`.

The temporary `_legacy.py` compatibility module is removed. The stable
`binding/__init__.py` facade continues to expose the same 48 public names with
exact root/facade/provider identity and I118-frozen signatures, exceptions,
runtime behavior, and artifact bytes.

I123 continues directly from the uncommitted I122 review state atop the I121
checkpoint `6610873`, as requested. The final providers occupy 459 lines for
identity, 317 for effects, 664 for authority, 1,763 for candidates, 1,503 for
scopes, 922 for artifacts, and 1,444 for session; the facade is 119 lines. The
2,208-line I122 compatibility module no longer exists.

## Artifact Provider

[`binding/artifacts.py`](../../../src/pygrc/causal_pathways/binding/artifacts.py)
owns:

- `BindingLock`, `BindingReceipt`, and their immutable canonical artifact base;
- execution-transcript canonicalization and digest construction;
- pathway and composition record projection;
- claim-envelope derivation, including producer, adapter, diagnostic,
  configured-semantics, candidate, and blocked-claim cuts;
- registered and candidate pathway-use graph construction;
- stage, crossing, candidate-mechanism, alternative-selection, and effect
  outcome projections;
- complete lock and receipt record assembly plus their canonical digests; and
- the public direct-unbound classification.

The two artifact builders consume authority lookups, binding/candidate records,
and immutable runtime ledger snapshots. They return new immutable artifacts and
do not import or mutate a binding session. Artifact schema versions, field
names, field order under canonical serialization, digest exclusions, and byte
content remain unchanged under the I118 corpus.

## Session Provider

[`binding/session.py`](../../../src/pygrc/causal_pathways/binding/session.py) owns:

- `BoundPathway`, `BoundComposition`, `VerifiedCallable`, and
  `VerifiedCompositionCrossing` handles;
- `PathwayBindingSession` and `UnbindableCompositionError`;
- pathway, composition, alternative, and candidate declaration orchestration;
- symbol and crossing linkage plus explicit-adapter owner validation;
- callable-identity cache orchestration;
- lock-time authority and declaration validation;
- receipt-time active-scope, candidate-witness, and source-current validation;
  and
- delegation to the scope runtime and canonical artifact builders.

`freeze_lock()` and `build_receipt()` each call exactly one artifact builder.
The session contains no lock/receipt schema fields, graph construction,
claim-envelope derivation, execution-transcript serialization, or artifact
digest construction.

## Cohesive State Ownership

The concrete session now retains seven top-level collaborators or values:
authority, phase state, declaration state, link state, artifact state, runtime
scope state, and identity-cache state.

Five small internal state owners replace the former flat mutable fields:

- `_SessionPhaseState` owns the declaration/locked/sealed phase;
- `_DeclarationState` owns pathway, composition, candidate, mechanism-handle,
  and alternative declarations;
- `_LinkState` owns stage-symbol, runtime-instance, crossing, and crossing-owner
  links;
- `_ArtifactState` owns candidate-use records and the active lock; and
- `_IdentityCacheState` owns resolved paths, verified source files, and callable
  identity guards.

Live invocation ledgers, deterministic runtime object identity, and active
scope state remain in the I122 `_RuntimeScopeState` collaborator. Public
behavior remains session-oriented while internal mutation has explicit owners.

## Complete Dependency DAG

The final provider-first direction is:

```text
identity -> effects -> authority -> candidates -> scopes -> artifacts -> session
```

Each provider may skip earlier layers but imports no later layer:

- `identity.py` imports no binder provider;
- `effects.py` imports identity;
- `authority.py` imports effects and identity;
- `candidates.py` imports authority and identity;
- `scopes.py` imports candidates and identity;
- `artifacts.py` imports authority, candidates, effects, identity, and scopes;
  and
- `session.py` imports all preceding providers.

The facade imports public objects directly from their defining provider. No
provider imports the facade or a compatibility module, and `_legacy.py` is
absent.

## Checker Independence

The production artifact provider and the independent binding conformance
checker remain separate implementations. The checker imports no production
`pygrc.causal_pathways` module and independently derives transcript digests,
claim envelopes, graph constraints, schema checks, and all 20 binding rules.
The I118 checker-independence digest and file manifest remain unchanged.

## Architecture Enforcement

[I123 architecture tests](../../../tests/integrations/test_causal_pathway_binding_i123.py)
enforce:

- the exact complete seven-provider DAG and absence of `_legacy.py`;
- artifact ownership and root/facade/provider identity;
- session-independent canonical artifact derivation with no session duplicate;
- session ownership of handles and orchestration objects;
- exact phase, declaration, link, artifact, and identity-cache state owners;
- one canonical builder delegation from each freeze/seal method; and
- the independent checker's lack of production derivation imports.

The evolved I119-I122 architecture tests now target the final session provider
and complete dependency graph while retaining every earlier ownership,
protocol, and pressure-test assertion.

## Related Files And Frozen Artifacts

Implementation and enforcement:

- [`binding/artifacts.py`](../../../src/pygrc/causal_pathways/binding/artifacts.py)
- [`binding/session.py`](../../../src/pygrc/causal_pathways/binding/session.py)
- [`binding/scopes.py`](../../../src/pygrc/causal_pathways/binding/scopes.py)
- [`binding/candidates.py`](../../../src/pygrc/causal_pathways/binding/candidates.py)
- [`binding/__init__.py`](../../../src/pygrc/causal_pathways/binding/__init__.py)
- [I123 architecture tests](../../../tests/integrations/test_causal_pathway_binding_i123.py)
- [I122 architecture tests](../../../tests/integrations/test_causal_pathway_binding_i122.py)
- [focused binding and pressure tests](../../../tests/integrations/test_causal_pathway_binding.py)
- [binding conformance tests](../../../tests/integrations/test_causal_pathway_binding_conformance.py)
- [independent binding checker](../../../scripts/check_grc_lgrc_causal_pathway_binding_conformance.py)

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
- [I122 record](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration122.md)

## Verification

All commands used the repository `.venv` and `PYTHONPATH=src:.` where package
loading required it. The full project gate used the repository's documented
`unittest` discovery command; pytest is not installed in this environment.

| Gate | Result |
| --- | --- |
| I118 API/artifact/runtime/checker freeze | Passed; 48 exports, 12 cases, 26 files |
| Evolved I119-I123 architecture tests | 28/28 passed |
| I123 architecture tests | 7/7 passed |
| Complete focused binding suite | 137/137 passed in 37.781 seconds |
| Full project suite | 1,348/1,348 passed in 357.374 seconds |
| Binding conformance | 20/20 passed, zero issues; digest `eb54f646569cf4b91e5f410fe94d6bbd0aae6706871e83431ee9d919cc42c823` |
| Predecessor conformance | 20/20 passed, zero issues; digest `14a4ee2a4cc2dc4beca4ce056a15548df90ed4f0d33a707d33facc1a1ce1c6b2` |
| Binder-scoped Ruff | Passed |
| Binder-focused mypy under Python 3.12 | Passed; 23 source files |
| `compileall src tests scripts examples` | Passed |
| Standard-library provider discovery | Passed; 48 exports and exact artifact/session identity |
| `git diff --check` | Passed |

## I124 Boundary

Iteration 124 is documentation and examples only. It may add the five planned
runnable examples, the user-and-agent guide, the stable public reference, the
operation-scoped provenance warning, and repository discovery links. It must
describe the final candidate contract directly and keep internal provider
layout noncontractual.

I124 may not change runtime behavior, public signatures, artifact schemas,
claim-envelope semantics, conformance policy, checker derivations, or the
provider dependency DAG. It must preserve the I118 oracle and run every new
example plus the focused documentation-relevant gates.
