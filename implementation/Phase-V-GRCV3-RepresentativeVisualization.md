# Phase V GRCV3 Visualization

## Purpose

This note records the current Phase V visualization boundary for `GRCV3`.

Two evidence lanes now matter:

- the earlier `primary` / `replay` representative lane, which first proved that
  saved `GRCV3` telemetry artifacts could already drive behavior figures and
  now also supports checkpoint-backed graph visuals when recorded with graph
  checkpoint export enabled
- the real seed-driven `cell-1` / `cell-4` lane, which now serves as the
  authoritative Phase V closeout surface

The closeout remains intentionally scoped:

- it consumes only saved telemetry/report artifacts
- it renders behavior-facing visuals for both lanes
- it renders graph-visible visuals for both the representative lane and the
  real seed-driven landscape lane when those lanes were recorded with graph
  checkpoints
- it keeps projector/seed-semantics questions separate from the narrower
  telemetry/visualization closeout claim

## Input Lanes

### Bridge Lane

The first bridge lane was the replay-stability surface:

- experiment path:
  - `outputs/representative/grcv3/<lane_name>/`
- run roles:
  - `primary`
  - `replay`
- default lane:
  - `phase5_reference`

This lane remains useful for deterministic replay checks, but it is no longer
the main Phase V closeout evidence.

The concrete representative graph lane now recorded here used:

- `lane_name = "phase_v_iter19_graph"`
- `num_steps = 3`
- primary run id:
  - `e403cd0bf1b0f8808d8105914a2432dadb6d8929ec6aeabcfef2c27964131050`
- replay run id:
  - `c68e00806f946ff0e45d7b917c51543b257b521d12683db49a77cd88a12a6159`
- matching final snapshot digest:
  - `09364e2b22779d26185666d767a3dc54e512992301bc5a4f9ad53efc45594dd9`

### Closeout Lane

The authoritative behavior-facing closeout lane is now the seed-driven pair:

- experiment path:
  - `outputs/representative/grcv3_landscape/<profile_name>/`
- run roles:
  - `cell-1`
  - `cell-4`
- default profile:
  - `seed_baseline`

The concrete artifact-backed closeout lane recorded here used:

- `profile_name = "seed_baseline"`
- `num_steps = 12`
- cell-1 run id:
  - `958f1834b76a03eed800d9c055b35f41d2f087617f6e2fcacf7769329ecb1964`
- cell-4 run id:
  - `4e9f456b7568dfd6080424607a6dbd0cb796d1a09cfaa0e4eafd8fcc8e5203ee`

The concrete checkpoint-backed landscape graph lane recorded here used:

- experiment path:
  - `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/`
- `profile_name = "seed_baseline"`
- `num_steps = 3`
- cell-1 run id:
  - `3f87fb9dbb4e3724d9c3c973b7885ac500bc89304af13eea4caf8e6fe138f823`
- cell-4 run id:
  - `8046610fa18891bd036ffbcba29bf9e762186f4bcae4bfe34973c7cec75dc5a4`

## Rendered Outputs

For each of `cell-1` and `cell-4`, the behavior-facing bundle renders:

- `visualization/trajectories.png`
- `visualization/events.png`
- `visualization/report_panel.png`

For the pairwise comparison, it renders:

- `comparison/<cell1_run_id>__vs__<cell4_run_id>/visualization/comparison_trajectories.png`
- `comparison/<cell1_run_id>__vs__<cell4_run_id>/visualization/comparison_panel.png`

The saved closeout outputs now exist at:

- cell-1:
  - `outputs/representative/grcv3_landscape/seed_baseline/cell-1/958f1834b76a03eed800d9c055b35f41d2f087617f6e2fcacf7769329ecb1964/visualization/`
- cell-4:
  - `outputs/representative/grcv3_landscape/seed_baseline/cell-4/4e9f456b7568dfd6080424607a6dbd0cb796d1a09cfaa0e4eafd8fcc8e5203ee/visualization/`
- comparison:
  - `outputs/representative/grcv3_landscape/seed_baseline/comparison/958f1834b76a03eed800d9c055b35f41d2f087617f6e2fcacf7769329ecb1964__vs__4e9f456b7568dfd6080424607a6dbd0cb796d1a09cfaa0e4eafd8fcc8e5203ee/visualization/`

The expected files were verified on disk:

- per-run:
  - `trajectories.png`
  - `events.png`
  - `report_panel.png`
- comparison:
  - `comparison_trajectories.png`
  - `comparison_panel.png`

For the representative checkpoint-backed graph lane, the saved outputs now
exist at:

- primary:
  - `outputs/representative/grcv3/phase_v_iter19_graph/primary/e403cd0bf1b0f8808d8105914a2432dadb6d8929ec6aeabcfef2c27964131050/visualization/`
- replay:
  - `outputs/representative/grcv3/phase_v_iter19_graph/replay/c68e00806f946ff0e45d7b917c51543b257b521d12683db49a77cd88a12a6159/visualization/`
- comparison:
  - `outputs/representative/grcv3/phase_v_iter19_graph/comparison/e403cd0bf1b0f8808d8105914a2432dadb6d8929ec6aeabcfef2c27964131050__vs__c68e00806f946ff0e45d7b917c51543b257b521d12683db49a77cd88a12a6159/visualization/`

The expected representative graph files were verified on disk:

- per-run behavior:
  - `trajectories.png`
  - `events.png`
  - `report_panel.png`
- per-run graph:
  - `graph_sequence.png`
  - `graph_animation.gif`
  - `graph_html/`
  - `graph_layouts.json`
- pairwise comparison:
  - `comparison_trajectories.png`
  - `comparison_panel.png`
  - `graph_comparison.png`

For the seed-driven checkpoint-backed landscape graph lane, the saved outputs
now exist at:

- cell-1:
  - `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/cell-1/3f87fb9dbb4e3724d9c3c973b7885ac500bc89304af13eea4caf8e6fe138f823/visualization/`
- cell-4:
  - `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/cell-4/8046610fa18891bd036ffbcba29bf9e762186f4bcae4bfe34973c7cec75dc5a4/visualization/`
- comparison:
  - `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/comparison/3f87fb9dbb4e3724d9c3c973b7885ac500bc89304af13eea4caf8e6fe138f823__vs__8046610fa18891bd036ffbcba29bf9e762186f4bcae4bfe34973c7cec75dc5a4/visualization/`

The expected seed-driven graph files were verified on disk:

- per-run behavior:
  - `trajectories.png`
  - `events.png`
  - `report_panel.png`
- per-run graph:
  - `graph_sequence.png`
  - `graph_animation.gif`
  - `graph_html/`
  - `graph_layouts.json`
  - `graph_snapshots/`
- pairwise comparison:
  - `comparison_trajectories.png`
  - `comparison_panel.png`
  - `graph_comparison.png`

## What The Figures Show

The trajectory figures combine:

1. saved `GRCV3` observables, including:
   - `active_basin_count`
   - `max_hierarchy_depth`
   - `geometric_seed_count`
   - `geometric_validated_basin_count`
   - `active_split_count`
   - `spark_event_count`
   - `choice_regime_count`
   - `collapse_event_count`
2. numeric step-row family-extension traces from
   `family_extensions["grcv3"]`, including:
   - `signed_hessian.hessian_sign`
   - `spark_state.split_registry_size`
   - `hierarchy_state.hierarchy_node_count`
   - `choice_state.evaluated_node_count`

The report and comparison panels flatten the saved family extensions, so the
figures expose:

- final `grcv3` run-summary extensions on each run report
- left/right `grcv3` family-extension surfaces on the comparison panel

## Graph Rendering Semantics

The graph-visible surface now uses a two-layer edge interpretation rather than
collapsing all edge activity into one visual channel.

Structural layer:

- edge thickness retains the meaning of saved `base_conductance`
- this answers: where does the graph currently admit stronger or weaker
  structural coupling?

Flow layer:

- when checkpoint artifacts include honest `signed_flux_source`, graph visuals
  now overlay directional flow on top of the structural edge layer
- static checkpoint figures render directed arrows using the saved signed edge
  orientation
- edge width now increases with realized `|signed_flux|` rather than remaining
  conductance-only
- edge color continues to encode signed flow polarity when flux is available
- the final HTML surface is now rendered as directed when checkpoint flow data
  exists

This refinement matters because earlier graph renders were technically honest
but visually conservative:

- node boundary emphasis made sink status easy to see
- edge thickness mostly reflected conductance
- realized edge flow was visible only through color, which was too subtle on
  many lanes

The current rendering now keeps the contract distinction explicit:

- conductance is structure
- flow is activity
- and activity is shown through directed overlays rather than inferred from
  thickness alone

Choice/collapse semantics are now rendered explicitly as well:

- a node with a recorded collapse and no live current choice regime is rendered
  as a faded source node rather than a fully active one
- the sink it collapsed into is highlighted as the target of that resolved
  commitment
- a dashed directed collapse link is drawn from the collapsed source node to
  the collapsed sink target
- if the same node later re-enters a live choice regime, the renderer restores
  the node to its normal active view and suppresses stale collapse styling as
  the dominant visual channel

This matters because collapse in `GRCV3` is not always terminal over the whole
run. A node may carry collapse history while later re-entering ambiguity under
the same longer trajectory. The graph view should therefore distinguish:

- inactive collapsed history
- active current choice
- and current signed flow

rather than letting historical collapse permanently dominate node appearance.

This stays aligned with the Phase V flow contract:

- no arrows are invented from conductance alone
- no flow claims are made when checkpoint artifacts do not contain signed edge
  flux
- directional overlays appear only when the saved checkpoint surface supports
  them

## Closeout Interpretation

For the concrete `cell-1` / `cell-4` closeout run:

- `cell-1` finished with:
  - `active_basin_count = 1`
  - `max_hierarchy_depth = 1`
- `cell-4` finished with:
  - `active_basin_count = 3`
  - `max_hierarchy_depth = 1`
- the final comparison delta was:
  - `active_basin_count_right_minus_left = 2`

So the current lane already makes one real structural difference legible from
artifacts alone:

- `cell-1` stays as a single active basin
- `cell-4` sustains a richer multi-basin outcome under the same seed-baseline
  constitutive profile

This is the key reason the real seed lane supersedes the earlier replay lane
for Phase V closeout.

## Current Boundary

`GRCV3` now has a two-lane but fully closed visualization boundary:

- representative `primary` / `replay`:
  - behavior-facing visuals supported
  - graph-facing visuals supported when checkpoint artifacts were saved
- seed-driven `cell-1` / `cell-4`:
  - behavior-facing visuals supported
  - graph-facing visuals supported when checkpoint artifacts were saved

The current landscape renderer now supports all public surface modes:

- `surface = "behavior"`
- `surface = "graph"`
- `surface = "all"`

It still fails explicitly when a requested lane was recorded without graph
checkpoints, but that is now a lane-artifact error rather than a family-level
hard block.

## Post-Closeout Renderer Refinement

After the initial closeout, the shared graph renderer was tightened so edge
activity became materially more legible.

Implementation-facing effect:

- structural conductance now renders as a lighter background edge layer
- realized signed flow now renders as a directed overlay with stronger width
  response
- the HTML output now preserves directed transport when flux is present

Validation:

- `./.venv/bin/python -m unittest tests.visualization.test_visualization`
  passed after the renderer update

Supplementary artifact-backed evidence:

- the rich single-seed `GRCV3` lane was rerun with the refined renderer:
  - experiment path:
    - `outputs/grcv3-rich-fulltest/grcv3-rich/seed_baseline/`
  - seed:
    - `configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml`
  - steps:
    - `150` as the new default rich fulltest lane
  - run id:
    - `bdbf3d42b68cbb43795b390e4ab84386804c49d0a1afd06d171868ae7da2de8e`
  - visualization root:
    - `outputs/grcv3-rich-fulltest/grcv3-rich/seed_baseline/grcv3-rich-basin-boundary-channel-probe/bdbf3d42b68cbb43795b390e4ab84386804c49d0a1afd06d171868ae7da2de8e/visualization/`

- the dedicated collapse example was rerun through the same renderer so the
  collapse-specific overlay semantics are visible on a lane where collapse
  occurs early and clearly:
  - experiment path:
    - `outputs/grcv3-rich-collapse-example-100/grcv3-rich/hot_exploratory/`
  - seed:
    - `configs/landscapes/seed/grcv3-rich-collapse-example.seed.yaml`
  - steps:
    - `100`
  - run id:
    - `365e4feb0f57492e9814d8dc79d47ba626ba8bbb2801a5c20f765fbd4b8a5df0`
  - visualization root:
    - `outputs/grcv3-rich-collapse-example-100/grcv3-rich/hot_exploratory/grcv3-rich-collapse-example/365e4feb0f57492e9814d8dc79d47ba626ba8bbb2801a5c20f765fbd4b8a5df0/visualization/`
  - visualization root:
    - `outputs/grcv3-rich-fulltest/grcv3-rich/seed_baseline/grcv3-rich-basin-boundary-channel-probe/f7b5a8b6a32fb382572b421cbe0f5b5f0d69f7d7adb2e2c4987e94d6d9e9ad40/visualization/`

This rich lane is not part of the cross-family closeout contract. Its role is
to provide family-native graph evidence under a seed that already carries
`GRCL-v3` semantics, so renderer quality can be judged on a more expressive
substrate as well.

## Landed Entry Points

The behavior-facing lane is exposed through:

- API:
  - [src/pygrc/visualization/representative.py](../src/pygrc/visualization/representative.py)
    - `render_grcv3_representative_visual_suite(...)`
    - `render_grcv3_landscape_visual_suite(...)`
  - [src/pygrc/visualization/representative_graphs.py](../src/pygrc/visualization/representative_graphs.py)
    - `render_grcv3_representative_graph_suite(...)`
    - `render_grcv3_landscape_graph_suite(...)`
- CLIs:
  - [src/pygrc/cli/grcv3_representative_visuals.py](../src/pygrc/cli/grcv3_representative_visuals.py)
  - [src/pygrc/cli/grcv3_landscape_visuals.py](../src/pygrc/cli/grcv3_landscape_visuals.py)
- telemetry runner:
  - [scripts/run_grcv3_landscape_telemetry.py](../scripts/run_grcv3_landscape_telemetry.py)

## Validation

The lane is covered by:

- [tests/models/test_grc_v3_landscape_runtime.py](../tests/models/test_grc_v3_landscape_runtime.py)
- [tests/telemetry/test_experiments.py](../tests/telemetry/test_experiments.py)
- [tests/visualization/test_visualization.py](../tests/visualization/test_visualization.py)

Focused checks include:

- seed-driven `cell-1` / `cell-4` model projection and multi-step execution
- artifact emission for the seed-driven telemetry lane
- behavior-only suite rendering for `cell-1`, `cell-4`, and comparison outputs
- representative graph rendering when checkpoints exist
- representative graph-surface failure when checkpoints do not exist
- seed-driven landscape graph rendering when checkpoints exist
- seed-driven landscape graph-surface failure when checkpoints do not exist
- numeric trajectory access for `grcv3` family-extension step traces

## Artifact-Backed Closeout Evidence

The Phase V closeout is not based on tests alone.

The following end-to-end commands were executed successfully against the real
seed-driven behavior lane:

```bash
./.venv/bin/python scripts/run_grcv3_landscape_telemetry.py \
  --outputs-root outputs \
  --profile seed_baseline \
  --steps 12

./.venv/bin/python -m pygrc.cli.grcv3_landscape_visuals \
  --telemetry-root outputs \
  --profile seed_baseline \
  --surface behavior
```

So the current Phase V `GRCV3` behavior-facing closeout now rests on both:

- automated test coverage
- and a concrete saved `cell-1` / `cell-4` visualization artifact lane under
  `outputs/`

The following end-to-end commands were also executed successfully against the
representative checkpoint-backed graph lane:

```bash
./.venv/bin/python scripts/run_grcv3_representative_telemetry.py \
  --outputs-root outputs \
  --lane-name phase_v_iter19_graph \
  --steps 3 \
  --record-graph-checkpoints \
  --checkpoint-every-step \
  --include-flow-overlays

./.venv/bin/python -m pygrc.cli.grcv3_representative_visuals \
  --telemetry-root outputs \
  --lane-name phase_v_iter19_graph \
  --surface all
```

So the current Phase V `GRCV3` representative graph closeout now rests on
both:

- automated test coverage
- and a concrete saved `primary` / `replay` graph visualization artifact lane
  under `outputs/representative/grcv3/phase_v_iter19_graph/`

The following end-to-end commands were also executed successfully against the
seed-driven checkpoint-backed landscape graph lane:

```bash
./.venv/bin/python scripts/run_grcv3_landscape_telemetry.py \
  --outputs-root outputs \
  --experiment-path representative/grcv3_landscape_checkpoint \
  --profile seed_baseline \
  --steps 3 \
  --record-graph-checkpoints \
  --checkpoint-every-step \
  --include-flow-overlays

./.venv/bin/python -m pygrc.cli.grcv3_landscape_visuals \
  --telemetry-root outputs \
  --experiment-path representative/grcv3_landscape_checkpoint \
  --profile seed_baseline \
  --surface all
```

So the current Phase V `GRCV3` landscape graph closeout now also rests on
both:

- automated test coverage
- and a concrete saved `cell-1` / `cell-4` graph visualization artifact lane
  under `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/`
