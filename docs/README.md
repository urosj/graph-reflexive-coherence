# PyGRC Documentation

This directory contains operator-facing documentation for PyGRC.

- `reference/` contains reference guides and user guides for runtime families,
  telemetry, landscape language, inference, motion, visualization, and evidence
  catalogs.
- `status/` contains current-state records and policy notes that are not
  implementation checklists.
- `../examples/` contains runnable usage paths and example plans.
- `../implementation/` contains engineering plans, implementation checklists,
  retrospective notes, and phase history. Its
  [`corrections/`](../implementation/corrections/README.md) index records
  bounded repairs to existing contracts separately from new implementation
  phases. Its
  [`investigations/`](../implementation/investigations/README.md) index records
  gated implementation studies that closed without runtime change but shaped
  later specifications or implementation directions.

For day-to-day usage, start with `reference/README.md`.

For runnable usage paths, start with [examples/README.md](../examples/README.md).

Current guides:

- [Catalogs And Evidence](reference/Catalogs-And-Evidence-ReferenceGuide.md)
- [Graph Visualization](reference/GraphVisualization-ReferenceGuide.md)
- [GRC Runtime](reference/GRC-Runtime-ReferenceGuide.md)
- [GRC/LGRC Causal Pathway Guide](reference/GRC-LGRC-CausalPathwayGuide.md)
- [GRC/LGRC Causal Pathway Binding And Claim Provenance](reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md)
- [GRC/LGRC Composition Matrix](reference/GRC-LGRC-CompositionMatrix.md)
- [GRCL](reference/GRCL-ReferenceGuide.md)
- [Landscape Language](reference/LandscapeLanguage-ReferenceGuide.md)
- [Landscape Compiler And Lowering](reference/LandscapeCompiler-ReferenceGuide.md)
- [Landscape Inference](reference/LandscapeInference-ReferenceGuide.md)
- [Motion](reference/Motion-ReferenceGuide.md)
- [Telemetry](reference/Telemetry-ReferenceGuide.md)

The causal pathway guide is an evidence-derived selection surface from the
completed Phase 8 causal-pathway consolidation tranche. Iteration 111 closes
the source-complete V1 audit, 23-pathway registry, 52-row stage-local evidence
crosswalk, 26-row directional composition matrix, six-class worked selection
guide, and 20-rule conformance policy. Its 22 expert-normalized pressure cases,
seven raw-domain demands, and answer-free blind replay preserve mechanism
ownership, novelty, and claim boundaries without hidden source reading. The
replay is frozen before a separate oracle validates recovery. No runtime
dispatcher or behavior was added. Reproducibility builders live under
`scripts/`; essential lifecycle documents remain at the `implementation/`
root, and the source audit plus I106-I111 supporting evidence are indexed in
`implementation/investigations/causal-pathway-consolidation/`. The path-only
evidence-identity transitions are recorded explicitly.

The causal-pathway binding guide covers the Iterations 112-116 binding plane:
exact mechanism-specific linkage, pre-execution locks, actual-use receipts,
candidate declarations, conservative claim provenance, and prospective
conformance. It does not add a runtime dispatcher or change GRC/LGRC dynamics.

Status notes:

- [LGRC9V3 Causal Time Design Observations](status/LGRC9V3-Causal-Time-Design-Observations.md)
- [LGRC9V3 Implementation State And Design Tension](status/LGRC9V3-Implementation-State-And-Design-Tension.md)
- [PyGRC Library Shape And Refactor Policy](status/PyGRC-Library-Shape-And-Refactor-Policy.md)

For why a behavior exists or how it was implemented, follow the guide links
back to the corresponding implementation checklist.
