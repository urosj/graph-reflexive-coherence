# Phase T GRCV3 Representative Telemetry

## Purpose

This note records the first artifact-backed `GRCV3` telemetry/report surface
implemented in Phase T Iterations 17 and 18.

The purpose of this lane is narrow:

- prove that the shared telemetry framework can capture `GRCV3`
- keep `GRCV3.step()` telemetry-agnostic
- produce saved reports that can be inspected without live runtime access
- use a truthful first comparison surface rather than forcing broader claims

## Selected Lane

The representative lane is the Phase 5 reference runtime:

- intrinsic three-node chain
- induced local frame geometry
- weighted least-squares differential backend
- tensor-exponential metric backend
- spark backend present but effectively suppressed by `eps_spark = 1e6`
- choice backend disabled

This is intentionally the same executable lane already validated in Phase 5,
not a new phenomenology-heavy setup.

The consequence is important for artifact interpretation:

- the first representative lane is intentionally event-light
- over the current `3`-step run it is expected to produce zero spark/split and
  zero choice/collapse events
- zero lifecycle counts here mean "suppressed by the representative threshold
  choice", not "telemetry cannot carry lifecycle events"

## Comparison Surface

The first truthful `GRCV3` comparison surface is:

- `primary`
- versus `replay`

where both runs start from the same deterministic initial state.

This comparison is narrow but honest:

- it checks telemetry-backed replay stability
- it does not pretend to be a broad cross-family comparison
- it does not assume landscape-seed support for `GRCV3`

The saved run identity therefore differs intentionally from the current
`GRCV2` representative lane:

- `seed_path` is synthetic rather than a real file path
- `param_family` is `None`
- `rng_seed` is `None`

This is acceptable for the Phase 5 reference runtime, but it should not be read
as the long-term identity surface for future landscape-driven `GRCV3` runs.

## Artifact Layout

The representative artifacts live under:

- `outputs/representative/grcv3/<lane_name>/primary/`
- `outputs/representative/grcv3/<lane_name>/replay/`

using the standard telemetry subdirectory layout:

- `telemetry/steps.jsonl`
- `telemetry/events.jsonl`
- `telemetry/run_summary.json`
- `telemetry/experiment_report.json`
- `telemetry/comparison_report.json`

For locality, the same pairwise comparison report is currently written into both
the `primary` and `replay` artifact directories, matching the earlier
representative `GRCV2` pattern.

## Contract Surface Used

Each step row carries the `grcv3` family extension with:

- backend summary
- signed-Hessian metadata
- basin summary
- spark/split summary
- hierarchy summary
- choice/collapse summary

Each event row carries the `grcv3` family extension with:

- event domain
- lifecycle stage
- topology mutation flag
- hierarchy mutation flag
- optional subject identifiers

Each run summary carries the `grcv3` family extension with:

- final versions of the step summaries
- fixed-surface lifecycle event counts

The full field-level contract remains in:

- [Phase-T-GRCV3-TelemetryContract.md](./Phase-T-GRCV3-TelemetryContract.md)

## Current Limits

This representative surface does not yet provide:

- `GRCV3` graph checkpoints
- `GRCV3` flow overlays
- `GRCV3` visualization-specific artifacts
- landscape-driven `GRCV3` experiment lanes

Those remain later telemetry or visualization work.
