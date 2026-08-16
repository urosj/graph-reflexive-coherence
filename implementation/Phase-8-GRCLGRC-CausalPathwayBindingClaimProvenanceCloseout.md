# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Closeout

**Status:** Reopened by round-two rejection; R2-B01 author correction complete,
R2-B02 and R2-B03 pending

**Branch:** `feat/causal-pathway-binding-claim-provenance`

**Consumed source revision:** `f612a93154ba31b5b62fa0f7d3b7590035468d3a`

## Decision

The Iteration 116 closeout is superseded by the Iteration 117 independent-audit
correction gate. The text below records the pre-audit checkpoint and is not a
current acceptance decision.

The author-side B-01 through B-06 and M-01 correction slices completed before
the second independent audit, which returned `reject_pending_correction` with
three blocker findings. R2-B01 is now corrected author-side: non-explicit
composition edges require exact shared-runtime-owner flow, and a crossing that
cannot prove that relation remains declared-but-unused. R2-B02 and R2-B03
remain open, so this document is not an acceptance record.

Locks and receipts are operation-scoped, callable and crossing identities are
rechecked, candidate and dynamic-choice evidence is scoped, acceptance uses a
separate trust anchor, and only trusted exact-symbol `committed` or `observed`
effects qualify. A further full independent audit remains required after all
round-two blockers are corrected.

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
- Non-explicit composition edges require a qualifying source and target call
  bound to the exact same direct runtime owner; unprovable crossings remain
  declared-but-unused.
- Binding/source drift becomes `stale_pending_review` and blocks claims.
- Unbound legacy code remains executable but cannot appear among a receipt's
  recorded bound invocation evidence; the receipt does not claim whole-run
  closure or absence of direct work.
- A non-raising return is not actual use unless its trusted exact-symbol effect
  contract classifies it as `committed` or `observed`.
- Existing GRC/LGRC mechanism and numerical behavior is unchanged.

## Frozen Surface

The closeout consists of:

- the separate 23-pathway, 52-stage, 55-symbol binding map;
- `pygrc.causal_pathways` authority, declaration, lock, callable-link,
  receipt, graph, candidate, and unbound-classification surfaces;
- canonical lock/receipt JSON artifacts and digests;
- the 20-rule binding conformance policy and checker;
- 20 global and 20 target-only rule controls, plus three target-only M-01
  effect-outcome forgery controls;
- ten consumer dry runs and a separately-oracled low-context replay;
- the Knowledge/Binding/Execution reference and contribution boundary.

The accepted knowledge-plane digests remain unchanged:

```text
registry  a266b33da10778e8caf5ad7d4a4bfe4b71aed9d0df563fd6c74e7d4ed6cb486b
crosswalk 0036dcdf54f4663bed183387db1c8f657eb44a694252ef44421be56fb239ff06
matrix    d1dbbdcb911cf34b399562c2dfe5122606c0de8d48d9634bc6af1e3d92e09e90
selector  f57545997fac63c9e465d21e0c840971aee073bd89aff135fb5d93a1ce134e1b
policy    7227c764e41b3d9964f306eff2830ded17afd8ace30df2eec4a58b0296ababf9
bindings  73d08edb5734b2dc7790ed475713f6eac503913402bb498800b49497f2ef0556
binding conformance policy
          a312f4184a64d548286bc82c14eeb83e1eb3975d4eddb3b0d17645076be62f32
```

## Current Maximum Claim Pending Further Correction And Re-Audit

The author-corrected implementation provides an operation-scoped,
versioned causal-pathway binding and provenance layer. Evidence-bearing
consumers can bind admitted pathways and compositions or explicitly declare
unregistered candidates. A receipt reports only identity-verified bound
invocations whose independently anchored exact-symbol contracts classify their
effects as committed or observed, plus conservative graph and claim-envelope
projections of that recorded evidence. It does not establish whole-run causal
closure, absence of direct work, or final acceptance while R2-B02 and R2-B03
remain open and the next independent audit is pending.

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
