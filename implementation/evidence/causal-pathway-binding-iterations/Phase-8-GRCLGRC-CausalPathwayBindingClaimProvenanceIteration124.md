# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 124

**Iteration:** 124 — Binder Examples And Guidance

**Status:** Passed

**Date:** 2026-08-21

**Production runtime behavior changed:** No

## Outcome

Iteration 124 adds the stable operator-facing layer after the binder's public
surface and modular implementation settled. Five runnable examples now cover
an admitted pathway, registered composition, explicit consumer-owned dynamic
choice, executable unregistered candidate, and valid direct-unbound versus
bound execution.

A new user-and-agent guide presents the complete workflow as `select -> bind ->
lock -> execute -> seal -> validate`. The stable reference now lists the
complete 48-name facade, primary signatures and handle behaviors, exact V1 lock
and receipt top-level fields, load-bearing nested row fields, candidate
mechanism/review artifact fields, and the final reviewed-candidate
source-to-request contract directly.

The guides and examples state the operation-scoped boundary prominently:
`claim_scope = bound_invocations_only` certifies only represented calls through
verified handles. It does not prove whole-run causal closure, prove the absence
of unbound influences, or qualify direct execution. Repository indexes make
those guides and examples discoverable.

I124 changes no file under `src/pygrc`, no knowledge or binding authority, no
artifact schema, no conformance policy or checker, and no runtime behavior.

## Runnable Examples

[`examples/causal_pathway_binding/`](../../../examples/causal_pathway_binding/README.md)
contains five entry points:

1. `admitted_pathway.py` binds the complete explicit packet lifecycle and
   produces an `admitted_bounded` receipt.
2. `registered_composition.py` executes `CMP-02` inside one evidence scope and
   produces its row-specific runtime object-flow witness and graph edge.
3. `dynamic_choice.py` declares packet/snapshot alternatives while the
   `--choice` consumer argument controls the branch. Both branches are tested.
4. `unregistered_candidate.py` executes a source-pinned distinct mechanism and
   retains `experimental_unregistered`, `promotion_status = none`, and
   `descriptive_unreviewed_not_claim_qualified`.
5. `direct_unbound.py` contrasts a valid direct mechanism call, classified as
   unbound and non-qualifying, with a separate represented bound invocation.

Each script prints one deterministic JSON summary and optionally writes its
canonical lock and receipt with `--output-dir`. Shared runtime construction and
trusted example configuration live in `_shared.py`. The candidate example owns
its mechanism source and version-2 content-addressed mechanism-evidence JSON;
it does not depend on a test fixture.

## User And Agent Guide

The
[user and agent guide](../../../docs/reference/GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md)
covers:

- consumer-owned semantic selection and the four binder outcomes;
- accepted authority loading with separate anchor record and trusted digest;
- pathway, composition, alternatives, and candidate declarations;
- pre-execution locking and phase boundaries;
- verified calls, composition scopes, dynamic scopes, and direct-unbound use;
- sealing, actual-use interpretation, claim qualification, and claim ceilings;
- independent validation and external transcript/review trust inputs;
- final candidate and reviewed invalid-pair candidate contracts;
- public error interpretation and a sequenced debugging checklist;
- safe authority, pathway, composition, symbol, candidate, schema, and checker
  extension practices; and
- explicit agent operating rules that prohibit internal-provider coupling and
  claim promotion.

## Stable Reference

The revised
[binding reference](../../../docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md)
keeps both supported facade import paths contractual while stating that
internal provider paths and class ownership are not. It directly describes the
final candidate contract and removes correction-round chronology from stable
guidance; historical R4-B01 through R8-B01 context remains in implementation
and independent-audit evidence.

The reference records:

- all 48 I118-frozen public exports;
- primary authority, session, declaration, lock, seal, and handle operations;
- exact lock/receipt artifact identities and schema versions;
- all exact V1 top-level fields;
- exact declaration, invocation, composition-witness, use-graph,
  claim-envelope, effect-summary, and declared-unused row fields;
- candidate mechanism and relation-review artifact fields; and
- canonical UTF-8 JSON serialization, digest exclusion, and ordering rules.

The I124 test derives the public export inventory from the I118 freeze and the
top-level schema inventories from canonical I116 artifacts, then requires every
name in the stable reference.

## Repository Discovery

The additions are linked from every planned repository-level discovery
surface:

- the root `README.md`;
- `docs/README.md`;
- `docs/reference/README.md`;
- `docs/reference/ClaimBoundaryIndex.md`;
- `examples/README.md` and the new local example README;
- `specs/README.md`; and
- `implementation/Documentation-Checklist.md`.

The claim-boundary index adds a dedicated binding and provenance section with
the exact claim ceiling and trust/evidence pointers.

## Related Files And Artifacts

Guidance and discovery:

- [user and agent guide](../../../docs/reference/GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md)
- [stable binding reference](../../../docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md)
- [claim-boundary index](../../../docs/reference/ClaimBoundaryIndex.md)
- [example index](../../../examples/causal_pathway_binding/README.md)
- [root README](../../../README.md)
- [docs index](../../../docs/README.md)
- [reference index](../../../docs/reference/README.md)
- [repository examples index](../../../examples/README.md)
- [specifications index](../../../specs/README.md)
- [documentation checklist](../../Documentation-Checklist.md)

Runnable examples and enforcement:

- [admitted pathway example](../../../examples/causal_pathway_binding/admitted_pathway.py)
- [registered composition example](../../../examples/causal_pathway_binding/registered_composition.py)
- [dynamic choice example](../../../examples/causal_pathway_binding/dynamic_choice.py)
- [unregistered candidate example](../../../examples/causal_pathway_binding/unregistered_candidate.py)
- [direct-unbound example](../../../examples/causal_pathway_binding/direct_unbound.py)
- [candidate mechanism](../../../examples/causal_pathway_binding/candidate_mechanism.py)
- [candidate mechanism evidence](../../../examples/causal_pathway_binding/candidate_mechanism_evidence.json)
- [shared example support](../../../examples/causal_pathway_binding/_shared.py)
- [I124 documentation/example tests](../../../tests/integrations/test_causal_pathway_binding_i124.py)

Frozen authority and compatibility inputs:

- [I118 public API freeze](../causal-pathway-binding/i118/I118PublicAPICompatibilityFreeze.json)
- [I118 artifact/runtime freeze](../causal-pathway-binding/i118/I118ArtifactRuntimeFreeze.json)
- [I118 checker-independence freeze](../causal-pathway-binding/i118/I118CheckerIndependenceFreeze.json)
- [I116 practical artifact examples](../causal-pathway-binding/i116)
- [binding acceptance anchor](../causal-pathway-binding/binding-acceptance-anchor.json)
- [binding conformance policy](../../../specs/grc-lgrc-causal-pathway-binding-conformance.json)

Planning and predecessor:

- [plan](../../Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenancePlan.md)
- [checklist](../../Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceChecklist.md)
- [I123 record](Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceIteration123.md)

## Verification

All commands used the repository `.venv` and `PYTHONPATH=src:.` where package
loading required it. The standalone binder checker passed when supplied the
required acceptance anchor and independently pinned digest. The full project
suite is intentionally deferred to the I125 closeout under the tranche plan.

| Gate | Result |
| --- | --- |
| Five runnable examples | Passed; all five scripts, both dynamic branches, conservative outputs |
| I124 documentation/example tests | 6/6 passed |
| I118 API/artifact/runtime/checker freeze | Passed; 48 exports, 12 cases, 26 files |
| Complete focused binding suite | 143/143 passed in 65.806 seconds |
| Binding conformance | 20/20 passed, zero issues; digest `eb54f646569cf4b91e5f410fe94d6bbd0aae6706871e83431ee9d919cc42c823` |
| Predecessor conformance | 20/20 passed, zero issues; digest `14a4ee2a4cc2dc4beca4ce056a15548df90ed4f0d33a707d33facc1a1ce1c6b2` |
| Binder/example-scoped Ruff | Passed |
| Binder/example-focused mypy under Python 3.12 | Passed; 31 source files |
| `compileall src tests scripts examples` | Passed |
| `git diff --check` | Passed |

## I125 Boundary

Iteration 125 is independent pressure and closeout. It must recheck the complete
public behavioral API freeze, byte-stable artifact corpus, runtime-state and
return behavior, retained mutation falsifiers, accepted 68-case independent
gate, both conformance policies, all five examples, the full project suite, and
all static checks.

I125 may not widen the maximum claim or treat documentation success as runtime
evidence. Closeout requires zero semantic, artifact, or runtime differences
attributable to the refactor and documentation tranche.
