# Phase V Handoff

This document defines the downstream contract that **Phase V: Visualization
Surfaces** must obey after the completion of Phase T.

For the family-level implementation status that this visualization layer now
rests on, see [`GRCV2-Closeout.md`](./GRCV2-Closeout.md).

Phase T established that `PyGRC` now has:

- deterministic telemetry row and run-summary schemas,
- deterministic artifact layout and save/load support,
- runner-level telemetry capture for seed-driven `GRCV2`,
- report builders for trajectory-summary and pairwise comparison payloads,
- graph checkpoint telemetry for topology/overlay/flow artifacts,
- dense checkpoint streaming support for every-step graph-evolution capture,
- and a representative `cell-1` / `cell-4` experiment lane.

Phase V must treat those outputs as the authoritative evidence layer.

That current evidence layer now supports both:

- behavior-visible output from scalar telemetry/report artifacts,
- and graph/flow-visible input artifacts through saved checkpoint telemetry.

At handoff time, it did **not** yet provide finished graph rendering. The Phase
V implementation work is responsible for turning those saved checkpoint
artifacts into visible surfaces while staying within the artifact-first
boundary defined here.

## 1. What Visualization May Consume

Phase V may consume:

- `steps.jsonl`
- `events.jsonl`
- `run_summary.json`
- `experiment_report.json`
- `comparison_report.json`
- `graph_checkpoints/index.json`
- checkpoint payload files or chunked checkpoint JSONL files under
  `graph_checkpoints/`

and the corresponding in-memory telemetry/report objects produced by the same
contracts.

Phase V should prefer artifact-driven rendering even when in-memory objects are
available, because the point of the visualization phase is to make saved
experiment evidence legible rather than to reopen live model internals.

Phase V may assume the existence of:

- graph checkpoint artifacts
- checkpoint node/edge overlay artifacts
- checkpoint flow artifacts

## 2. What Visualization Must Not Do

Phase V must not:

- reach directly into family model internals when the same information already
  exists in telemetry/report artifacts,
- silently invent derived semantics that are not recorded in telemetry or
  report payloads,
- treat plotting choices as evidence,
- hide telemetry limitations behind polished visuals,
- or make machine-local absolute paths part of the visualization contract.

In particular, visualization must not imply that:

- `PyGRC` already matches the PDE-side `25*` classification discipline,
- trajectory windows/checkpoints exist where telemetry has not yet defined them,
- graph-visible output is richer or denser than the saved checkpoint cadence
  actually supports,
- or absence of event rows proves absence of meaningful internal structure
  beyond the telemetry/report scope.

## 3. Required Visualization Inputs

At minimum, Phase V should be able to render from:

- one `TelemetryArtifactPack`
- one `TelemetryExperimentReport`
- one `TelemetryComparisonReport`
- one checkpoint index plus its referenced checkpoint payloads/chunks

without requiring a live `GRCV2` model instance.

## 4. Visualization Responsibilities

Phase V should focus on making the current telemetry/report layer more legible,
not more speculative.

The first useful visualization surfaces should therefore correspond directly to
existing telemetry/report structures:

- trajectory plots for numeric observable evolution,
- event timelines from `events.jsonl`,
- report panels for:
  - changed observables
  - event counts
  - checkpoint overview
  - pairwise final-summary deltas
- experiment comparison views keyed by run/report identity
- graph snapshot views from saved checkpoint artifacts
- and flow-overlay views from saved checkpoint edge/node payloads.

These are the currently justified visible outputs.

## 5. Known Upstream Limits That Phase V Must Respect

Phase T closes with explicit limits that remain upstream of visualization:

- only `GRCV2` is currently wired into the telemetry-backed experiment lane,
- report comparison is still summary-first and centered on final observables,
- checkpoint/window discipline is still minimal,
- graph checkpoint telemetry exists, but richer rendering conventions still
  need to stay downstream of the saved checkpoint contract,
- telemetry is strong enough for first experiment inspection but not yet at the
  full PDE-side `25*` classification richness,
- and classification-oriented trajectory features such as onset windows,
  stability intervals, or oscillation descriptors are not yet first-class
  report fields.

Phase V must reflect those limits rather than smoothing them away.

## 6. Recommended Phase V Starting Point

The first Phase V implementation should begin from the representative telemetry
lane already established in Phase T:

- `cell-1`
- `cell-4`
- `balanced_baseline`
- `num_steps = 100`
- `rng_seed = 7`

That lane is the correct baseline because it is the one already backed by:

- deterministic telemetry capture,
- saved artifact packs,
- per-run experiment reports,
- and a pairwise comparison report.

## 7. Acceptance Boundary

Phase V should be considered aligned with Phase T only if:

- every first-pass visual can be regenerated from saved telemetry/report
  artifacts,
- visual labels and panels map back to explicit telemetry/report fields,
- graph/flow visuals consume saved checkpoint telemetry rather than live state,
- and removing the live model object does not break the visualization contract.
