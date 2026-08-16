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
- [GRC/LGRC Composition Matrix](reference/GRC-LGRC-CompositionMatrix.md)
- [GRCL](reference/GRCL-ReferenceGuide.md)
- [Landscape Language](reference/LandscapeLanguage-ReferenceGuide.md)
- [Landscape Compiler And Lowering](reference/LandscapeCompiler-ReferenceGuide.md)
- [Landscape Inference](reference/LandscapeInference-ReferenceGuide.md)
- [Motion](reference/Motion-ReferenceGuide.md)
- [Telemetry](reference/Telemetry-ReferenceGuide.md)

The causal pathway guide and composition matrix are draft surfaces from the
Phase 8 causal-pathway consolidation tranche. Iteration 105 has frozen their
initial source anchor and twelve-family admission census; the exhaustive
surface audit, final registry decomposition, crosswalk, matrix, and selection
guidance remain pending Iterations 106-111.

Status notes:

- [LGRC9V3 Causal Time Design Observations](status/LGRC9V3-Causal-Time-Design-Observations.md)
- [LGRC9V3 Implementation State And Design Tension](status/LGRC9V3-Implementation-State-And-Design-Tension.md)
- [PyGRC Library Shape And Refactor Policy](status/PyGRC-Library-Shape-And-Refactor-Policy.md)

For why a behavior exists or how it was implemented, follow the guide links
back to the corresponding implementation checklist.
