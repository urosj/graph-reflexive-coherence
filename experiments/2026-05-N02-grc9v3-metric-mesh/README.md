# GRC9V3 Metric Mesh Experiments

## Intent

This experiment family treats `GRC9V3` as the space on which RC-like field
patterns live and move.

The goal is to test whether a mostly dormant metric port-graph can replace a
fixed continuous PDE grid for the purposes of RC phenomenology while retaining
graph-native semantics: identity, hierarchy, ports, interfaces, refinement,
motion, and event interpretation.

The central question is:

```text
If GRC9V3 supplies the metric graph space, can seeded coherence patterns move,
split, merge, collapse, or refine in ways that are stronger and more semantic
than fixed-substrate PDE-RC while remaining observer-backed?
```

These experiments should use existing `GRC9V3` runtime, checkpoint, edge-label,
landscape, and motion-inference surfaces. They should not create a new dynamics
engine. If a missing reusable capability appears, it should graduate into
`src/` through a separate implementation task with tests.

## Initial Hypotheses

- A dormant or near-empty GRC9V3 graph can act as a metric support without
  forcing a global Euclidean `dx`.
- `geometric_length`, `temporal_delay`, and `flux_coupling` can define distinct
  notions of graph-space proximity for the same substrate.
- Populated motifs should produce motion claims through existing observers:
  coherence transfer, representative drift, identity continuity, boundary
  motion, and topological change.
- GRC9V3 metric space should express non-Euclidean adjacency and semantic
  routing more naturally than PDE source geometry.
- The experiment must distinguish inactive/dormant support from actual
  coherence budget so that epsilon regularization does not become hidden mass.

## Experiment Classes

- Sparse dormant mesh with active seeded islands.
- Pattern population over authored basins, channels, interfaces, and junctions.
- Variable effective `dx` via edge-label fields.
- Movement comparisons using geometric shortest path, temporal-delay path, and
  flux-coupling path.
- Retained-negative controls for source-authored but non-moving seeds.
- Motion catalog review over populated metric-graph runs.

## Discipline

- Experiment code lives under this directory.
- Reusable library changes do not happen here.
- Outputs and generated reports should remain local to this experiment family.
- Source seeds may declare preconditions, but motion claims require runtime
  artifacts and observer records.

