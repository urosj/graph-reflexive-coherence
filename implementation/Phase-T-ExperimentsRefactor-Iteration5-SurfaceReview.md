# Phase T Experiments Refactor: Iteration 5 Surface Review

## Decisions

### 1. Result types now have a dedicated private home

Moved from inline definitions in `src/pygrc/telemetry/experiments.py` to:

- `src/pygrc/telemetry/_experiment_results.py`

Moved types:

- `GRCV2RepresentativeExperimentResult`
- `GRCV3RepresentativeRunResult`
- `GRCV3RepresentativeExperimentResult`
- `GRCV3LandscapeExperimentResult`

Compatibility rule:

- `src/pygrc/telemetry/experiments.py` still re-exports these names
- `src/pygrc/telemetry/__init__.py` still re-exports these names

### 2. Experiment defaults now have a dedicated private home

Moved from inline definitions in `src/pygrc/telemetry/experiments.py` to:

- `src/pygrc/telemetry/_experiment_defaults.py`

Compatibility rule:

- `src/pygrc/telemetry/experiments.py` still re-exports the deliberate default
  surface used by scripts and package-root imports
- `src/pygrc/telemetry/__init__.py` remains the compatibility-heavy package
  root for broad default imports

Explicit internal note:

- `DEFAULT_GRCV3_REPRESENTATIVE_SOURCE_REFERENCE` remains internal and is not
  added to the public module/package export surface

### 3. `experiments.py` `__all__` is now deliberate

Before Iteration 5, `src/pygrc/telemetry/experiments.py` had a partial
leftover `__all__`:

- it exported only a subset of defaults
- it omitted several public trace helpers
- it did not match the actual compatibility surface exposed by the package root

After Iteration 5:

- `experiments.py` `__all__` now deliberately covers:
  - public defaults intentionally supported at the module surface
  - public result dataclasses
  - representative/landscape experiment runners
  - all public trace builders

## Deferred Decisions

### Additional public config dataclasses

Decision:

- not justified yet

Reason:

- internal refactor seams now exist (`GRCV3CheckpointConfig`, helper modules,
  split test surface), but promoting additional public config dataclasses would
  be an API design change, not a structural cleanup

### Package-root default surface shrink

Decision:

- deferred

Reason:

- the package root intentionally supports broad script/CLI imports
- shrinking that surface now would be a compatibility decision, not a refactor
  hygiene decision

### Remaining structural debt

- `scripts/run_grcv3_rich_fulltest.py` still imports private helper functions
  from `pygrc.telemetry.experiments`
- `src/pygrc/telemetry/__init__.py` remains intentionally broad and should only
  be narrowed with an explicit compatibility decision

## Residual Observations

- `src/pygrc/telemetry/experiments.py` remains a substantial facade file.
  That is intentional: it still owns the public forwarding surface for
  representative runners and trace builders, so it remains the first
  compatibility-bearing navigation point even after the internal extraction.
- `src/pygrc/telemetry/_grcv3_settlement_traces.py` is the largest remaining
  private trace module. In particular,
  `build_grcv3_landscape_secondary_support_authorability_trace(...)` remains a
  comparatively large coordinator because it composes four lane summaries plus
  family comparisons. This is worth noting for any future private-only
  partition, but it is not a current refactor blocker.
- `tests/telemetry/_experiments_test_support.py` is now a sizable shared
  support module, with many seed constants, script paths, and loader helpers.
  That is acceptable for the current test boundary, but later cleanup could
  group seeds and scripts more explicitly if navigation pressure increases.
- `_to_plain_data(...)` in `src/pygrc/telemetry/_telemetry_utils.py` remains a
  generic normalization helper. It is correct where it is today, but it is a
  reasonable candidate for a broader utility home if more telemetry modules
  start sharing similar normalization logic.
- `GRCV3CheckpointConfig` uses the standard frozen-dataclass
  `object.__setattr__(...)` pattern inside `__post_init__`. That is correct,
  but it remains a readability note worth documenting for future maintainers.

## Verification

- import/compile verification:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m py_compile src/pygrc/telemetry/__init__.py src/pygrc/telemetry/experiments.py src/pygrc/telemetry/_experiment_defaults.py src/pygrc/telemetry/_experiment_results.py`
- public-name spot check:
  - `pygrc.telemetry` and `pygrc.telemetry.experiments` both still expose:
    - `DEFAULT_GRCV3_BROAD_COLLAPSE_SURVEY_LANES`
    - `DEFAULT_GRCV3_POST_SPARK_COLLAPSE_STEPS`
    - `GRCV3RepresentativeRunResult`
    - `build_grcv3_landscape_post_collapse_geometry_exclusion_trace`
- full experiments test surface:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
  - `Ran 64 tests in 595.318s`
  - `OK`
