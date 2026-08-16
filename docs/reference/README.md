# Reference Guides

Canonical operator-facing guides live here. Implementation plans and checklists remain under `implementation/`.

## Available Now

- [Catalogs And Evidence Reference Guide](Catalogs-And-Evidence-ReferenceGuide.md)
- [Claim Boundary Index](ClaimBoundaryIndex.md)
- [Landscape Inference Reference Guide](LandscapeInference-ReferenceGuide.md)
- [Graph Visualization Reference Guide](GraphVisualization-ReferenceGuide.md)
- [GRC Runtime Reference Guide](GRC-Runtime-ReferenceGuide.md)
- [GRC/LGRC Causal Pathway Guide](GRC-LGRC-CausalPathwayGuide.md)
- [GRC/LGRC Composition Matrix](GRC-LGRC-CompositionMatrix.md)
- [GRCL Reference Guide](GRCL-ReferenceGuide.md)
- [Landscape Compiler And Lowering Reference Guide](LandscapeCompiler-ReferenceGuide.md)
- [Landscape Language Reference Guide](LandscapeLanguage-ReferenceGuide.md)
- [LGRC9V3 Causal-History Reference Guide](LGRC9V3-CausalHistory-ReferenceGuide.md)
- [Motion Reference Guide](Motion-ReferenceGuide.md)
- [Telemetry Reference Guide](Telemetry-ReferenceGuide.md)

## Status

All planned guides in the current documentation checklist are present and
cross-linked. Future additions should extend this index and update
`Documentation-Checklist.md`.

The causal pathway guide is frozen as a Phase 8 evidence-derived selection
surface. The intrinsic 23-pathway registry, 52-row stage-local evidence
crosswalk, 26-row directional composition matrix, ten worked selection cases,
and 20-rule machine conformance policy are complete through Iteration 111. The
20 global negative controls and 19 non-digest rule-isolation controls fail
closed. A 22-row, 11-category expert pressure corpus, seven raw-domain demands,
and one answer-free blind replay pass without hidden source reading or claim
promotion. The raw layer preserves pathway-only and genuinely unregistered
outcomes; the replay is frozen before separate oracle validation. These
artifacts do not introduce runtime behavior, and the policy retains versioned
stale-to-reviewed re-admission. I106-I111 builders live under `scripts/`; their
supporting evidence is indexed under
`implementation/investigations/causal-pathway-consolidation/`, and earlier
bundle identities remain explicit provenance rather than alternate authority.

GRC9V3 Lane B interpretation is split by responsibility:
`GRC-Runtime-ReferenceGuide.md` covers lane behavior, `Telemetry-ReferenceGuide.md`
covers evidence fields, and `GraphVisualization-ReferenceGuide.md` covers visual
rendering of Lane A/Lane B candidate classes.

Progress is tracked in [Documentation-Checklist.md](../../implementation/Documentation-Checklist.md).
