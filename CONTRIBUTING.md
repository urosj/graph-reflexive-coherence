# Contributing and Participating

This repository is one locally governed continuation of graph-based Reflexive
Coherence research and the PyGRC reference implementation. Direct
contributions are welcome, but participation in the wider research ecology does
not require convergence into this repository.

A pull request remains the route for changing this repository, but it is not
the definition of contributing to the research ecology.

## Participation Orientation

For the wider participation orientation, see
[Research as Participation](https://github.com/urosj/geometric-reflexive-coherence/blob/main/docs/2026-08-ResearchAsParticipation.md).
That paper remains Draft 1. This file defines the current local participation
and admission boundary of the graph-RC repository; it does not claim that a
distributed research ecology has already been demonstrated.

## Local Authority and Independent Continuation

Participation depends on two freedoms that remain together:

1. You may continue and publish an independent graph runtime, substrate
   interpretation, producer policy, experiment family, or research line.
2. This repository decides what enters its own maintained runtime,
   specifications, evidence history, and public claim boundary.

Acceptance means that a contribution has been admitted into this repository's
continuation. It does not make the contribution universally authoritative.
Declining admission means only that the work is not entering this continuation
in its present form. It may remain a legitimate independent substrate
extension, experiment, negative result, or research continuation.

## Participation Paths

| Path | Purpose | Local admission required? |
| --- | --- | ---: |
| **Direct contribution** | Enter this maintained runtime, specification, or evidence history | Yes |
| **Independent graph/substrate continuation** | Develop another runtime, substrate, extension policy, or implementation lineage | No |
| **External experiment or evidence return** | Publish evidence related to this work without moving implementation here | No |
| **Independent use** | Consume PyGRC and its published contracts within the license | No |

## Local Admission Boundary

This repository has two connected local admission lanes.

### Substrate Development

Substrate development includes graph-runtime semantics, specifications,
implementation changes, compatibility boundaries, serialization, tests,
fixtures, telemetry and visualization surfaces, reusable examples, reference
documentation, and explicit promotion of experiment-discovered capabilities.
It is not limited to Python changes under `src/pygrc/`.

Appropriate direct contributions include:

- fixes or clarifications to graph/LGRC papers in `papers/`;
- implementation, test, or documentation changes for `src/pygrc/`;
- updates to specifications, reference guides, examples, and landscape
  fixtures;
- compatibility, persistence, telemetry, visualization, or reconstruction
  corrections;
- bounded runtime extensions with explicit native or producer-mediated status.

### Evidence Experiments

Evidence experiments use the graph substrates to investigate bounded RC,
substrate, realization, composition, and ecological-handoff questions under
explicit evidence boundaries. Current lines include boundary, loop closure,
continuation, susceptibility, optionality, multi-basin formation, transfer,
generative/extractive persistence, shared-medium participation, and derived
decay semantics.

Appropriate direct contributions include:

- new primitive, building-block, motif, or regime candidates with evidence;
- controls, negative results, replications, and failed paths;
- reproducibility corrections for experiment scripts, reports, or artifacts;
- corrections to roadmaps, candidate directions, claim boundaries, debt
  records, or failure classifications;
- evidence-backed updates clarifying what an experiment supports, blocks, or
  leaves as future work.

For N30+ experiment orientation, use:

- [N30+ Experiment Catalog Roadmap](experiments/N30_plus_experiment_catalog_roadmap.md)
- [N30+ Candidate Directions](experiments/N30_plus_candidate_directions.md)

New contributors do not need to master the full catalog vocabulary before
participating. Where the catalog applies, identify the experiment's primary
position (primitive, building block, motif, or regime) and the evidence ceiling
that prevents stronger relabeling. The roadmap is orientation, not source
evidence: claims should consume the actual experiment artifacts, controls,
reports, and runtime records.

Work that belongs primarily to geometric theory, PDE/voxel simulation,
agentic protocol, agentic ecology, or the Reflexive Organism Model origin line
may fit better in the related repositories. Those repositories define their
own admission boundaries; an independent continuation does not require this
repository's placement decision.

## Direct Contribution Requirements

Before proposing a substantial direct change, identify:

- the question, defect, or pressure that produced the change;
- the source paper, specification, contract, commit, experiment, or artifact
  being consumed;
- the exact repository surface affected;
- the evidence supporting the change and the strongest claim it permits;
- what remains unresolved, producer-mediated, externally supplied, or
  realization-specific;
- compatibility and downstream-consumption consequences.

For substrate changes, include as applicable:

- the specification or theoretical basis;
- the runtime behavior added or modified;
- native versus producer-mediated status;
- serialization, restoration, API, telemetry, and compatibility effects;
- focused tests and reconstruction instructions;
- remaining implementation or naturalization debt.

For experiment changes, include as applicable:

- hypotheses, preregistered thresholds, and consumed source artifacts;
- scripts, configuration, evidence fixing the consumed source and runtime
  state, and replay instructions;
- controls, falsifiers, negative results, and failure classification;
- catalog position, claim ceiling, and blocked relabels;
- producer/native status and remaining debt;
- handoff or return conditions for downstream work.

Small corrections, broken links, formatting repairs, and obvious metadata fixes
do not need the full structure above.

## Promotion and Reusable Surfaces

Experiments incubate candidate patterns, controls, runtime extensions, and
composition contracts. Reusable graph-substrate surfaces require a separate
local promotion decision:

```text
experiment candidate
  -> bounded evidence
  -> classified result
  -> explicit promotion decision
  -> specification / runtime / reusable example
```

An experiment result does not become a reusable PyGRC capability merely
because it succeeds. Admission into `specs/`, `src/pygrc/`, or another reusable
surface requires its own prospective implementation, compatibility, and claim
decision.

A later implementation, native realization, or stronger contract does not
retroactively change an earlier experiment. Historical experiments retain the
runtime, producer/native boundary, controls, debts, and claim ceiling under
which they actually ran. Downstream projects may re-admit a reusable contract,
but they do not inherit the experiment's positive evidence; they must generate
evidence in their own realization. New combinations are new candidates and
need their own attribution and controls.

Accepted experiment records should therefore be corrected additively when
replacing an artifact would obscure the runtime, evidence, decision, or failure
history under which the original claim was formed.

Conversely, an ecology-side demand or interpretation does not determine the
graph-side implementation or experiment identity. This repository
independently admits, realizes, tests, promotes, or declines substrate demands
under its own evidence boundary.

An experiment may discover a capability, but only explicit local promotion
makes that capability part of the reusable graph substrate.

## External Returns and Independent Continuations

An external result can become consequential here without moving its
implementation into this repository. To make a later local encounter
reconstructable, a participant who wants to preserve the relation to this
lineage should expose, as applicable:

- source repository and revision;
- the exact PyGRC model, specification, pattern, contract, and extension set
  consumed;
- relevant artifacts or reproduction instructions;
- the source-reported result;
- native, producer-mediated, or externally reimplemented status;
- claim ceiling and unresolved debt;
- the proposed relation to this repository.

This is guidance, not a mandatory global return schema. Until this repository
inspects, reproduces, or locally admits an external result, it remains a
source-reported external result rather than local validation. Publication does
not update this repository automatically, require attention, or create an
obligation to merge, endorse, review, or respond.

## Generated Artifacts

Do not commit top-level scratch outputs by default. Experiment-local outputs
under `experiments/**/outputs/` may be committed when they are part of the
historical evidence record.

When a result depends on generated artifacts, commit the script, configuration,
report, output artifact, and enough reconstruction detail for another
participant to rerun it. Committed artifacts should use repository-relative
paths and should not contain machine-local absolute paths.

## Direct Contribution Workflow

For work proposed for local admission:

1. Create a focused branch.
2. Keep changes scoped to one model family, experiment lane, or documentation
   surface when possible.
3. Use relative links and paths. Avoid home-directory paths, drive-letter
   paths, or IDE-specific links.
4. Run the relevant tests or explain why they were not run.
5. Open a pull request with a concise summary, verification notes, source and
   compatibility implications, and the claim boundary affected.

## Testing

Common commands:

```bash
python -m unittest discover -s tests -p 'test_*.py'
python -m ruff check src tests
python -m mypy src tests
```

For experiment-only changes, run the relevant experiment script or validator
and include the command in the contribution notes. Passing a test does not by
itself establish the wider theoretical interpretation.

## Issues and Local Attention

When opening an issue, include:

- the file, model family, specification, or experiment lane involved;
- the command you ran, if any;
- the expected behavior and observed behavior;
- links to relevant papers, specifications, reports, or generated artifacts;
- whether the issue concerns documentation, implementation, reproducibility,
  compatibility, or claim framing.

Issues are a direct local interaction channel, not a requirement for external
participation. Keep reports focused and bounded; no participant is entitled to
another research world's attention.

## Conduct

Please follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Keep direct discussion
focused on making the graph RC model family clearer, more reproducible, and
easier to inspect, while respecting independent continuation outside this
repository.
