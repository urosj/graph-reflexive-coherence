# GRC/LGRC Causal Pathway Consolidation Evidence

**Status:** Accepted supporting evidence for the completed Phase 8
documentation and conformance tranche

This directory contains source-audit, iteration, execution, replay, control,
freeze, and provenance records for Iterations 106-111. It is an investigation
package because it examined and consolidated existing GRC/LGRC pathways without
changing runtime behavior. Its location does not mean the result was abandoned
or inconclusive.

## Essential Tranche Documents

- [Plan](../../Phase-8-GRCLGRC-CausalPathwayConsolidationPlan.md)
- [Checklist](../../Phase-8-GRCLGRC-CausalPathwayConsolidationChecklist.md)
- [Baseline freeze](../../Phase-8-GRCLGRC-CausalPathwayConsolidationBaselineFreeze.md)
- [Machine baseline freeze](../../Phase-8-GRCLGRC-CausalPathwayConsolidationBaselineFreeze.json)
- [Closeout](../../Phase-8-GRCLGRC-CausalPathwayConsolidationCloseout.md)

## Canonical Products

- [Pathway registry](../../../specs/grc-lgrc-causal-pathway-contracts.json)
- [Evidence crosswalk](../../../specs/grc-lgrc-causal-pathway-evidence-crosswalk.json)
- [Composition matrix](../../../specs/grc-lgrc-causal-pathway-composition-matrix.json)
- [Selection guide](../../../specs/grc-lgrc-causal-pathway-selection-guide.json)
- [Conformance policy](../../../specs/grc-lgrc-causal-pathway-conformance.json)
- [Human pathway guide](../../../docs/reference/GRC-LGRC-CausalPathwayGuide.md)
- [Human composition matrix](../../../docs/reference/GRC-LGRC-CompositionMatrix.md)

## Evidence Sequence

- [Iteration 106](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.md):
  source-complete pathway registry and unmapped-surface audit.
- [Iteration 107](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.md):
  stage-local source and test evidence crosswalk.
- [Iteration 108](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.md):
  directional composition and crossing evidence.
- [Iteration 109](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.md):
  evidence-derived selection semantics.
- [Iteration 110](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.md):
  machine conformance, negative controls, and maintenance lifecycle.
- [Iteration 111](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111.md):
  pressure consumers, raw demands, blind recovery, and tranche closeout.

## Layout Provenance

The [layout relocation record](./Phase-8-GRCLGRC-CausalPathwayConsolidationLayoutRelocation.json)
maps the original top-level evidence identities, the temporary builder-only
layout, and the accepted final package. Path relocation changes artifact-bundle
identity but does not change scientific classifications, evidence rows,
selection meanings, conformance meanings, pressure outcomes, or runtime
behavior.

Reproducibility builders and validators live under [`scripts/`](../../../scripts/).
