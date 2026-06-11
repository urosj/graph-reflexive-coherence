# GRC9V3 Properties Experiments

## Intent

This experiment family studies `GRC9V3` as a substrate in its own right.
The goal is to test whether the nine-port, three-row, three-column structure
carries observable meaning beyond being a bounded-degree graph convention.

The central question is:

```text
Do rows, columns, and ports separate differential, interface, routing,
refinement, and identity behavior in a way that is observable in runtime
artifacts?
```

These experiments should use the existing `src/pygrc` runtime and telemetry
surfaces. They should not add new runtime behavior directly. If an experiment
reveals a reusable missing capability, that capability should graduate into
`src/` through a separate repo-level `implementation/` task with tests.

May 2026 note: before fixture implementation resumes, the project is recording
a bounded GRC9V3 Hessian / hybrid spark readiness pass under
the repo-level `implementation/` directory:
`../../implementation/GRC9V3-Hessian-ImplementationPlan.md`. The experiment
baseline remains the current signed-Hessian hybrid spark lane. A direct
column-H spark gate, if implemented later, is a separate canonical lane and
should be compared against the baseline rather than silently replacing it.

## Entry Points

- `hypotheses/Index.md` defines the current hypothesis map, including the
  anonymous-port null, original semantic hypotheses, and D1-D8 discriminator
  hypotheses.
- `hypotheses/Experiment-DiscriminatorHypotheses.md` expands the falsifiable
  discriminator hypotheses.
- `implementation/ExperimentSpecification.md` defines the observational
  experiment stance, common artifact requirements, and O-style experiment
  classes.
- `implementation/DiscriminatorExperimentSpecification.md` defines the D1-D8
  discriminator experiment specifications.

## Initial Hypotheses

- Rows behave as local differential modes: row-localized conductance,
  coherence gradients, Hessian signatures, and flux stress should produce
  distinct geometric responses.
- Columns behave as interface and refinement families: column-localized
  cancellation, saturation, or routing should affect boundary/frontier,
  coarse-graining, and spark/refinement behavior.
- Ports are the intersection layer where row semantics and column semantics
  meet; edge behavior should sometimes classify differently depending on
  whether it is grouped row-wise or column-wise.
- GRC9V3 should expose cases where metric shortest path, temporal-delay path,
  and strongest-flux path disagree while remaining auditable through existing
  edge labels.

## Experiment Classes

- Row-mode stress tests.
- Column-interface cancellation and routing tests.
- Port saturation and near-saturation tests.
- Column-preserving refinement and child-identity inheritance tests.
- Coarse-graining and Split reconstruction checks over edge-label fields.
- Motion observer checks for row-preserving but column-changing dynamics.

## Discipline

- Experiment code lives under this directory.
- Reusable library changes do not happen here.
- Outputs and generated reports should remain local to this experiment family.
- Claims must be backed by runtime artifacts, checkpoints, telemetry, and
  observer records rather than source-authored intent alone.
