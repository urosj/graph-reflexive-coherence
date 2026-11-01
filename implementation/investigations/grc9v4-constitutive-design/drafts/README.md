# GRC-v4 and GRC9V4 drafts

## Manuscript succession

This is the stable entry point for the GRC-v4 manuscript. **New reviews and
editorial work should use [2026-11-GRC-V4.md](./2026-11-GRC-V4.md).**

| Edition | Status | Reference use |
| --- | --- | --- |
| [2026-09-GRC-V4.md](./2026-09-GRC-V4.md) | Frozen predecessor | Existing contracts and historical source citations retain this exact edition. |
| [2026-11-GRC-V4.md](./2026-11-GRC-V4.md) | Current adopted manuscript; accepted 2026-11-01 | Review, further manuscript development and proposed new integrations start here. |

The succession is **2026-09-GRC-V4 → 2026-11-GRC-V4**. The exact predecessor
used by this successor is the file at repository commit
`4d247e7bbcfd0c8251b5b40b6971ef904e0c2e76`, with SHA-256
`dd538ba5f731808d9cb8d95337a36fe2cb8ddfacece90c0f3001399381f63768`.
The successor incorporates the full substrate account, spark §15 and technical
Appendix H, shorter accepted witnesses, and corresponding abstract,
contribution, claim and conclusion changes.

The user's acceptance and commit request on 2026-11-01 adopts the corrected
full manuscript and consolidated spark proposal. The manuscript header records
this decision. Existing frozen source bindings keep their historical meaning; changing
one requires its own explicit successor binding. When a later manuscript
supersedes this one, extend this chain and update the current link here and the
handoff. A feature proposal or supplement is not implicitly a new main edition.

## Spark proposal and reading guide

[Claim/debt and section correspondence](./spark-completion/Traceability.md) maps
the current prose to the accepted contracts and the remaining native obligations.

1. [Self-contained spark proposal](./spark-completion/Proposal.md): the classifier,
   completion theorem and proofs, all ten complete maps, exact source/event
   construction, certificate methods and accepted shorter witnesses.
2. [Full GRC-v4 paper](./2026-11-GRC-V4.md): the complete manuscript
   successor, with spark completion integrated in §15 and technical Appendix H.
   Its abstract, contributions, claims, conclusion and GRC9V4 appendix include
   the result. This is the current adopted manuscript.
3. [Side-tool reading guide](../tools/exploratory-side-tool/docs/SparkCompletionOverview.md):
   the primary accepted endpoints and the inspection surface for each result.

These adopted editorial documents are grounded in accepted scientific
contracts. They follow the [formal adoption of the five earlier endpoints](../decisions/SparkCompletionEarlierSC3Authority.md).
The shorter results are primary. Initial longer proofs are historical references
for specific derivations, source identities or retrospective checks, rather than
the default presentation of completion time.

The family proposal/paper pairs in this directory remain their original,
hash-bound technical records. Their dated population counts and pending flags
describe their historical stages. The current documents contain the scientific
argument themselves; their computational companions supply large exact operands.
Use the historical source map for a particular earlier derivation or audit.
Original evidence, execution identities and normative source files are preserved.

## Substrate and related investigations

- [Substrate proposal](./GRCV4-proposal.md) and [earlier main paper](./2026-09-GRC-V4.md):
  the source-bound substrate account before spark integration. The full paper
  linked above preserves that architecture and adds the constructive result;
  the earlier manuscript remains unchanged for accepted provenance.
- [Connected C_RG2b addendum](./2026-09-GRC-V4-Connected-RG2b-Addendum.md) and
  [connected A_RG2b addendum](./2026-09-GRC-V4-Connected-A-RG2b-Addendum.md):
  the earlier connected-section work, with its own scope.
- [Autonomous topology change](./autonomous-topology-change/README.md):
  a separate investigation. The spark witnesses below use declared D11 events;
  they do not supply a general autonomous topology-selection law.
