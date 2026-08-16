# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Closeout

**Status:** Reopened at Iteration 117; independent audit corrections pending

**Branch:** `feat/causal-pathway-binding-claim-provenance`

**Consumed source revision:** `f612a93154ba31b5b62fa0f7d3b7590035468d3a`

## Decision

The Iteration 116 closeout is superseded by the Iteration 117 independent-audit
correction gate. The text below records the pre-audit checkpoint and is not a
current acceptance decision.

At the Iteration 116 checkpoint, one explicit linker model handled admitted
native pathways, producer-mediated and adapter/diagnostic registered
compositions, dynamic caller choice, and genuinely unregistered candidates
without a generic causal dispatcher or common mechanism API.

Evidence-bearing consumers now have exactly three structural routes:

```text
bind an admitted pathway
bind an admitted executable registered composition
declare a distinct experimental unregistered candidate
```

Verified mechanism-specific callables require an exact pre-execution lock.
Post-use receipts record actual stage/symbol use, registered edges exercised,
candidate use, declared-but-unused identities, the pathway-use graph, authority
and source identities, blocked claims, and a structured conservative claim
envelope.

## Acceptance Criteria

- Native pathway use binds without inventing a composition.
- CMP-20 preserves feedback producer identity and producer-owned authority.
- CMP-26 preserves explicit adapter identity and non-native ownership.
- Diagnostic relations cannot become behavioral crossings.
- Unsupported and invalid matrix rows cannot bind as admitted execution.
- Candidate work remains usable, unregistered, unpromoted, and claim-bounded.
- Dynamic alternatives remain caller-selected and actual use is receipted.
- Endpoint co-use and registered chains do not synthesize new edges or claims.
- Binding/source drift becomes `stale_pending_review` and blocks claims.
- Unbound legacy code remains executable but cannot masquerade as
  claim-qualified pathway evidence.
- Existing GRC/LGRC mechanism and numerical behavior is unchanged.

## Frozen Surface

The closeout consists of:

- the separate 23-pathway, 52-stage, 55-symbol binding map;
- `pygrc.causal_pathways` authority, declaration, lock, callable-link,
  receipt, graph, candidate, and unbound-classification surfaces;
- canonical lock/receipt JSON artifacts and digests;
- the 20-rule binding conformance policy and checker;
- 20 global and 20 target-only negative controls;
- ten consumer dry runs and a separately-oracled low-context replay;
- the Knowledge/Binding/Execution reference and contribution boundary.

The accepted knowledge-plane digests remain unchanged:

```text
registry  a266b33da10778e8caf5ad7d4a4bfe4b71aed9d0df563fd6c74e7d4ed6cb486b
crosswalk 0036dcdf54f4663bed183387db1c8f657eb44a694252ef44421be56fb239ff06
matrix    d1dbbdcb911cf34b399562c2dfe5122606c0de8d48d9634bc6af1e3d92e09e90
selector  f57545997fac63c9e465d21e0c840971aee073bd89aff135fb5d93a1ce134e1b
policy    7227c764e41b3d9964f306eff2830ded17afd8ace30df2eec4a58b0296ababf9
bindings  fde515ea4d3337c3ac0a17772e573bb546a9edf5e25f87621a56c24c6851b5ea
binding conformance policy
          8ed42bdd9984e37917108d4963ccb3ef85236bf8b4e21d160ccb1f153c51e027
```

## Maximum Claim

GRC/LGRC provides a versioned causal-pathway binding and provenance layer
through which evidence-bearing consumers can bind admitted pathways and
compositions or explicitly declare unregistered candidates, producing a
validated pathway-use graph and conservative claim envelope while leaving
mechanism-specific runtime execution unchanged.

## Remaining Boundaries

This closeout does not claim or provide:

- universal causal routing or a generic causal-work API;
- automatic pathway or ownership-model selection;
- generic work admission or candidate promotion;
- native candidate or route formation where registry residue remains;
- ecological meaning, support, coordination, cooperation, or agency;
- native Read-Back;
- N32 selection or implementation;
- RCAE L04 implementation.

New experimental relations have an explicit continuation route through
candidate declaration, evidence, source audit, pathway/stage contracts,
composition and selection evidence, conformance, and a separate explicit
promotion decision. This tranche does not automate that route.
