# Phase V Milestone 1

This note records the first stable visualization milestone reached during
**Phase V**.

The milestone is intentionally modest in scope and strong in evidence
discipline:

- it is fully artifact-driven,
- it does not depend on a live model object,
- it covers trajectories, event timelines, and report/comparison panels,
- and it stops short of graph rendering until topology/flow artifacts exist.

## Representative Validation Lane

The milestone is validated on the saved representative lane:

- `cell-1`
- `cell-4`
- `balanced_baseline`
- `num_steps = 100`
- `rng_seed = 7`

Rendered outputs now exist under:

- `outputs/experiments/grcv2/representative/balanced_baseline/`

with:

- per-run trajectory figures,
- per-run event timelines,
- per-run report panels,
- one comparison trajectory figure,
- and one comparison report panel.

The current representative visualization entrypoint is intentionally scoped to
the behavior surface only:

- `./.venv/bin/python -m pygrc.cli.grcv2_representative_visuals --family balanced_baseline --surface behavior`

If graph-facing rendering is requested, the CLI should fail explicitly until
the topology/flow artifact bridge exists.

That future graph path is now named explicitly as well:

- `./.venv/bin/python -m pygrc.cli.grcv2_representative_graphs --family balanced_baseline`

At this milestone it remains a deliberate blocker command rather than a partial
renderer.

## What This Milestone Already Shows

The current visualization slice is already sufficient to make the main
behavioral difference legible without manual JSON inspection:

- `cell-1` behaves as a quiescent / settling run
- `cell-4` behaves as a delayed-growth / birth-rich run
- budget conservation is directly inspectable and visually flat in both runs
- event absence versus event-rich behavior is directly visible
- topology-count divergence is visible through:
  - `num_nodes`
  - `num_edges`
  - `sink_count`
  - `birth_count`
- report panels expose:
  - changed observables
  - event counts
  - checkpoint overview
  - parameter provenance
- comparison panels expose the final-summary delta surface directly from saved
  report artifacts

## Why This Counts As A Real Milestone

This is not just a plotting milestone. It confirms that the Phase T artifact
contract is already strong enough to support experiment-facing review of the
first meaningful `GRCV2` runs.

That matters because it means:

- the scalar/report side of the experiment loop is now inspectable,
- visualization is downstream of telemetry rather than a replacement for it,
- and the project has a stable evidence layer before attempting graph-local
  rendering.

## What This Milestone Does Not Yet Claim

This milestone does **not** yet provide:

- graph-evolution rendering over checkpoints,
- graph-local event overlays,
- per-edge flow visuals,
- or PDE-style spatial heatmap equivalents.

Those remain blocked by missing artifact surfaces, not by visualization
libraries.

## Next Step

The next meaningful step is the topology/flow artifact bridge:

- define checkpoint topology exports,
- define node/edge overlay attributes,
- define flow export requirements,
- then begin `networkx` / `pyvis` graph-facing work on top of those saved
  artifacts.
