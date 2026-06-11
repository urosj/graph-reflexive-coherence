# PyGRC Library Shape And Refactor Policy

Date: 2026-05-06
Updated: 2026-05-16

Status: current shape recorded; large structural refactors deferred until usage
creates concrete pressure.

## Purpose

This note records the current shape of `src/pygrc` after the GRC9V3 Lane B
implementation and post-closeout telemetry/visualization catch-up.

It is not an implementation checklist. It is a status and decision record for
how to treat PyGRC as a codebase right now: a research/runtime workspace with
strong core foundations, not yet a public-library stabilization target.

The guiding rule is:

```text
Do not create code geometry changes unless there is tension.
```

In GRC terms, refactoring should be a response to flow and pressure in actual
usage. Structural rearrangement without observed tension is restructuring for
its own sake.

## Current Package Shape

The package is organized into these main subpackages:

| Package | Current role |
|---|---|
| `pygrc.core` | Shared runtime interfaces, typed records, graph protocols/backends, params, serialization, storage, events, errors, capabilities. |
| `pygrc.models` | Executable runtime families: `GRCV2`, `GRCV3`, `GRC9`, `GRC9V3`, state types, lowering adapters, landscape runtime helpers, port/coarse-graining helpers. |
| `pygrc.landscapes` | Landscape seed models, validation, PDE translation, inference surfaces, motion inference, GRCL extension schemas/examples/fixtures. |
| `pygrc.telemetry` | Step/event/run-summary contracts, artifact IO, capture, replay sessions, selector validation, experiment and report helpers. |
| `pygrc.visualization` | Behavior plots, graph checkpoint rendering, representative visuals, GRCL visual review, motion visuals. |
| `pygrc.discovery` | Mechanism ledgers, hypothesis catalogs, seed generation, selector validation, reviewed catalogs, discovery runners. |
| `pygrc.integrations` | Adapter boundaries for graph and visualization interop. |
| `pygrc.cli` | Some centralized CLI wrappers. |
| `pygrc.utils` | Currently empty placeholder package. |

This shape is coherent for a research workspace. It gives the project a single
repository where runtime behavior, telemetry, visualization, experiments,
catalog review, and reference documentation can evolve together.

Current LGRC9V3 extension status:

```text
native packet-loop surfaces are supported;
native causal pulse-substrate surfaces are supported;
native feedback/coupling producers are supported as policy-gated schedulers;
N04 supports a bounded native_m6_same_fixture_self_renewal_candidate;
locomotion-like, adaptive-topology, biological, agency, identity-acceptance,
inherited-N03 movement, and unrestricted movement claims remain blocked.
```

## Strengths To Preserve

The strongest library-quality foundations are already in place:

- `pygrc.core` has a clean abstraction layer around `GRCModel`, `GRCParams`,
  `GRCState`, `StepResult`, events, errors, capabilities, and storage.
- Graph backends use protocol-style boundaries and deterministic reference
  implementations.
- Runtime parameters are immutable and content-addressed through canonical
  hashing.
- JSON serialization is deterministic and uses atomic write patterns.
- Runtime families are executable and covered by targeted tests.
- GRC9/GRC9V3 port, expansion, budget, and coarse-graining surfaces are
  operator-backed rather than report-only.
- GRC9V3 Lane A/Lane B behavior is now explicit:
  - Lane A: `current_hybrid_signed_hessian`;
  - Lane B v1: `grc9v3_column_h_assisted`.
- Telemetry now distinguishes lane selection from branch attribution.
- Visualization now distinguishes Lane A signed-Hessian, Lane B signed-Hessian,
  and Lane B column-H-branch candidate classes.
- Reference guides explain runtime behavior, telemetry evidence, and visual
  interpretation.

These are real capabilities. They should not be disrupted by cosmetic
rearrangement.

## Known Friction Points

The following are known engineering pressure points, but they are not automatic
refactor triggers.

| Area | Current friction | Current decision |
|---|---|---|
| Root imports | `pygrc.__init__` eagerly imports broad subpackages, including telemetry and visualization. This makes root import heavier than a mature library should be. | Defer unless examples or users show import-time or dependency pain. |
| Public API surface | `models`, `landscapes`, and `telemetry` expose broad convenience facades. | Keep while usage patterns settle. Later split stable API from experiment/replay conveniences. |
| Mandatory dependencies | `pyproject.toml` currently lists visualization and graph dependencies as hard dependencies. | Accept for workspace use. Consider optional extras only when packaging becomes a target. |
| Large modules | Some runtime, telemetry, landscape, and visualization modules are large. | Do not split solely by line count. Split only when a concrete change repeatedly touches unrelated concerns. |
| CLI/library blending | Several non-`cli` modules include command-line parsing or script-style helpers. | Accept for current research workflow. Move to `pygrc.cli` only when examples or packaging require it. |
| Lint hygiene | Full `ruff check src/pygrc` currently reports unused imports/locals and at least one annotation-name issue in broader telemetry code. | Clean opportunistically when touching files. Do not start a broad lint-only refactor unless it becomes a release gate. |
| Empty `utils` package | `pygrc.utils` exists as a placeholder. | Leave harmless for now; remove or populate during public API cleanup. |
| Documentation depth | Reference guides are useful; public API docstrings are not yet comprehensive. | Focus on examples first. Let examples reveal which APIs deserve stable docs. |
| Quickstart orchestration | The `spark_a_cell.py` quickstart exposes a long but real path: load seed, extract GRCL9V3 extension, compile source, lower to `GRC9V3State`, construct `GRC9V3`, run, build telemetry identity, export checkpoints, capture telemetry, and render visuals. | Record as observed usage tension. Do not refactor immediately; use more examples to confirm the helper shape. |
| Example fixture helpers | `examples/grc9v3/_fixtures.py` contains reusable-looking fixture and inspection helpers. | Keep local for now. Promote only if telemetry, visual, and landscape examples repeatedly need the same helpers. |

## Refactor Policy

Structural refactors should be triggered by observed tension, not by an abstract
preference for cleaner layout.

Examples of real tension:

- a usage example needs awkward or unstable imports;
- a user cannot tell which API is stable;
- telemetry capture requires hidden or repeated setup;
- visualization requires non-obvious artifact wiring;
- Lane A/Lane B comparison requires bespoke code outside examples;
- import cost becomes a practical problem for normal usage;
- tests become hard to write because seams are unclear;
- a change repeatedly edits unrelated responsibilities in the same large file;
- optional visualization dependencies block runtime-only use.

Non-triggers:

- a module is large but locally coherent;
- a facade exports many symbols but examples remain clear;
- an internal helper could be placed somewhere more elegant;
- a future public API might want a different package shape;
- a refactor would look cleaner but does not reduce current friction.

## Near-Term Direction

The next useful work should be usage-first. The examples scaffold now lives in
`examples/`, with quickstart, GRC9V3 runtime, and landscape source-to-runtime
paths.

Build out examples that exercise real workflows:

```text
examples/
  README.md
  quickstart/
    README.md
    spark_a_cell.py
  grc9v3/
    README.md
    lane_a_baseline.py
    lane_b_column_h.py
    lane_a_vs_lane_b.py
    telemetry_capture.py
    visual_bundle.py
  landscapes/
    README.md
    define_seed.py
    load_seed.py
    run_seed_grc9v3.py
    telemetry_and_visuals.py
```

Those examples should answer:

- How do I construct and run `GRC9V3`?
- How do I select Lane A or Lane B?
- How do I inspect candidate event evidence?
- How do I capture telemetry?
- How do I render the visual bundle?
- How do I define/load/lower a landscape seed?
- What files should I open to see a run?
- Which imports feel stable enough to document?

Refactor only where those examples expose pressure.

## Observed Usage Tension From Quickstart

The quickstart `examples/quickstart/spark_a_cell.py` is useful because it shows
the full source-to-visible-result path:

```text
landscape seed
  -> GRCL9V3 landscape extension extraction
  -> GRCL9V3 source compilation
  -> GRC9V3 lowering
  -> GRC9V3 runtime execution
  -> telemetry identity and artifact layout
  -> graph checkpoint export
  -> telemetry capture
  -> behavior and graph visualization
```

This is exactly the kind of friction the example layer is meant to reveal. A
future public helper may be justified, but the helper should follow this actual
workflow rather than a hypothetical generic utility.

Possible future helper shapes, if the pressure repeats:

```python
build_grc9v3_from_grcl9v3_seed(seed_path)
capture_and_render_run(model, output_root=...)
run_landscape_seed_to_visuals(seed_path, runtime_target="grc9v3", output_root=...)
```

These are not current implementation tasks. They are recorded as future
candidate surfaces if repeated examples or users need the same orchestration.

## Observed API Tension From Examples Review

A review of the `examples/grc9v3/` and `examples/landscapes/` workflows
identified several API pressure points. These observations are not refactor
instructions. They are recorded so future usage can confirm or weaken the
pattern.

High-signal tensions:

| Area | Observed tension | Current decision |
|---|---|---|
| GRC9V3 landscape lowering | The path from `LandscapeSeed` to `GRC9V3` currently requires explicit chaining: extract GRCL9V3 extension, compile source, lower to `GRC9V3State`, then call `GRC9V3.from_state(...)`. | Record pressure for a possible facade such as `build_grc9v3_from_grcl9v3_seed(...)`; do not add it yet. |
| Telemetry capture | `capture_run_telemetry(...)` is powerful but has a long keyword surface and requires users to assemble identity, layout, step results, checkpoints, and config. | Record pressure for a runner-level wrapper; keep the explicit API for now. |
| Graph checkpoint export | Examples currently build `GraphCheckpointArtifact` records manually from model state. | Record pressure for a model or telemetry helper that exports graph checkpoints; do not add a generic helper until repeated usage confirms the needed shape. |
| Event payload schemas | `GRCEvent` is simple, but event payloads are `dict[str, Any]`; users need docs or helper functions to know which fields matter. | Record pressure for typed/discoverable event payload schemas or public constants; defer broader schema work. |
| GRC9V3 runtime-state construction | `from_state(...)` accepts a runtime-state mapping; users need to know the nested structure unless they rely on examples or fixtures. | Record pressure for a builder or documented typed construction path; defer until more usage clarifies what users actually build. |

Lower-priority or broader tensions:

- config validation is manual and not schema-driven;
- GRCL9V3 extension payloads are nested dictionaries;
- some model methods are public in practice but not introduced by examples;
- visualization is intentionally artifact-driven, so direct rendering from a
  live model is not available;
- lazy imports and broad package facades remain packaging/public-library
  concerns.

The strongest current pattern is orchestration friction, not a failure of the
core runtime layers. If repeated usage keeps asking for the same orchestration,
the most likely future helper surfaces are:

```python
build_grc9v3_from_grcl9v3_seed(seed_or_path, *, params=None)
capture_model_run_telemetry(model, step_results, *, output_root, seed=..., checkpoints=True)
run_grcl9v3_seed_to_grc9v3_artifacts(seed_path, *, output_root, steps=1)
```

These names are placeholders, not accepted API. They should be revisited only
after more usage examples or user requests confirm the pattern.

## Deferred Public-Library Hardening

If and when the project targets a public library release, likely hardening work
includes:

- make `pygrc` root import lightweight;
- define `__version__` and release/version policy;
- split dependencies into core, telemetry, visualization, landscape, and dev
  extras;
- reduce top-level public facades;
- move CLI parsing into `pygrc.cli` or console entry-point modules;
- clean `ruff check src/pygrc` to zero;
- add import-boundary tests that prevent visualization dependencies from loading
  during runtime-only imports;
- add focused public API docstrings;
- split large modules at seams proven by usage pressure;
- document stable versus research/experiment APIs.

This is deferred deliberately. The current priority is to stabilize usage paths
before stabilizing public-library geometry.

## Decision

PyGRC should not be treated as public-library-complete yet.

It should be treated as:

```text
a strong research/runtime workspace with executable runtimes, telemetry,
visualization, reference documentation, and tested GRC9V3 Lane B behavior.
```

The next phase should emphasize examples and practical use. Refactoring remains
available, but only as a response to observed tension in those usage paths.
