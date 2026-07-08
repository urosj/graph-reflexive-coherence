# Contributing

This repository is the home for graph-based Reflexive Coherence and the PyGRC
reference implementation. Contributions should stay within that scope.

## Repository Shape

This repository has two connected contribution lanes:

1. **Substrate development**: runtime, specs, tests, examples, telemetry,
   visualization, fixtures, and reference documentation for graph/LGRC
   substrates, including `src/pygrc/`.
2. **Evidence experiments**: experiments that use those substrates to test
   bounded properties of Reflexive Coherence theory, especially
   agency-adjacent claims such as boundary, loop closure, continuation,
   susceptibility, optionality, multi-basin formation, transfer,
   generative/extractive persistence, and shared-medium ecology.

Runtime changes should state what substrate capability they add or modify.
Experiment changes should state what claim boundary they affect and should
consume source artifacts directly rather than relying on roadmap summaries.

For N30+ experiment design, use:

- [N30+ Experiment Catalog Roadmap](experiments/N30_plus_experiment_catalog_roadmap.md)
- [N30+ Candidate Directions](experiments/N30_plus_candidate_directions.md)

New contributors do not need to master the full catalog vocabulary upfront.
Use the roadmap as orientation, and keep proposals clear about what evidence or
runtime behavior they intend to add or clarify.

Appropriate contributions include:

- fixes or clarifications to graph/LGRC papers in `papers/`;
- implementation, test, or documentation changes for `src/pygrc/`;
- updates to specs, reference guides, examples, and landscape fixtures;
- new catalog entries or experiment proposals that extend the primitive,
  building-block, motif, or regime catalog;
- reproducibility fixes for experiment scripts, reports, or claim boundaries;
- corrections to experiment roadmaps, candidate directions, claim boundaries,
  debt notes, or failure classifications;
- evidence-backed updates that clarify what an experiment supports, blocks, or
  leaves as future work;
- broken-link fixes, path cleanup, and citation/license metadata corrections.

Please use the related repositories for work that belongs primarily to
geometric theory, PDE/voxel simulation, agentic protocol, or the Reflexive
Organism Model origin line.

## Generated Artifacts

Do not commit top-level scratch outputs by default. Experiment-local outputs
under `experiments/**/outputs/` may be committed when they are part of the
historical evidence record.

When a result depends on generated artifacts, commit the script, config, report,
output artifact, and enough reconstruction detail for someone else to rerun it.
Committed artifacts must use relative paths only and must not contain
machine-local absolute paths.

## Workflow

1. Create a focused branch.
2. Keep changes scoped to one model family, experiment lane, or documentation
   surface when possible.
3. Use relative links and paths. Avoid home-directory paths, drive-letter paths,
   or IDE-specific links.
4. Run the relevant tests or explain why they were not run.
5. Open a pull request with a concise summary, verification notes, and the claim
   boundary affected by the change.

## Testing

Common commands:

```bash
python -m unittest discover -s tests -p 'test_*.py'
python -m ruff check src tests
python -m mypy src tests
```

For experiment-only changes, run the relevant experiment script or validator and
include the command in the PR notes.

## Issues

When opening an issue, include:

- the file, model family, or experiment lane involved;
- the command you ran, if any;
- the expected behavior and observed behavior;
- links to relevant papers, specs, reports, or generated artifacts;
- whether the issue is documentation, implementation, reproducibility, or claim
  framing.

## Conduct

Please follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Keep discussion focused
on making the graph RC model family clearer, more reproducible, and easier to
inspect.
