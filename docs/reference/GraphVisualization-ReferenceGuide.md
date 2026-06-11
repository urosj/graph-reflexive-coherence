# Graph Visualization Reference Guide

This guide describes the PyGRC visualization layer: telemetry plots,
graph/checkpoint rendering, GRCL lowered-source visual review, and motion
visualization.

Visuals are supporting evidence only. They help inspect telemetry and
checkpoint artifacts, but they do not create new runtime, selector, landscape,
or motion claims.

## Scope

Use this guide when you want to:

- render time-series and event panels from telemetry,
- render graph checkpoint sequences and animations,
- review GRCL-9 and GRCL-9V3 lowered-source visual artifacts,
- render static or animated motion visuals,
- understand where visual outputs are written,
- trace visuals back to telemetry rows, checkpoints, selectors, and catalogs.

## Prerequisites

The visualization package is headless and artifact-driven. Run examples from
the repository root with the project environment:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.motion --help
```

Runtime requirements are declared in `pyproject.toml`:

- Python `>=3.11`
- `matplotlib>=3.8`
- `networkx>=3.2`
- `pyvis>=0.3.2`
- `PyYAML>=6.0`

GIF rendering imports `Pillow` through `PIL.Image`. In the current environment
it is available through the installed visualization stack; if a minimal install
omits it, install `Pillow` before rendering graph or motion animations.

## Getting Started

Visualization starts from existing artifacts. For a first run, create or reuse a
motion session, then render one example:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.landscapes.motion_examples \
  --session-id S9001 \
  --example identity_walking_control

PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.motion \
  --session-root outputs/motion/sessions/S9001 \
  --example identity_walking_control
```

Expected outputs:

- `outputs/motion/sessions/S9001/visualizations/identity_walking_control/motion_graph.png`
- `outputs/motion/sessions/S9001/visualizations/identity_walking_control/motion_timeline.png`
- `outputs/motion/sessions/S9001/visualizations/identity_walking_control/motion_visual_summary.json`

Replace `S9001` with a fresh local session id. Generated session ids in this
guide are examples, not canonical evidence ids.

## Data Flow

The visualization layer does not run dynamics. It reads artifacts and writes
supporting surfaces:

```text
runtime / replay / inference session
  -> telemetry artifact layout
  -> TelemetryArtifactPack + checkpoint artifacts + selector/motion records
  -> deterministic layout and sampling
  -> PNG / GIF / HTML / JSON / Markdown visual outputs
```

If a required upstream artifact is missing, visualization should fail rather
than invent a substitute.

## Main Modules

| Module | Purpose |
|---|---|
| `src/pygrc/visualization/layout.py` | Deterministic output path builders and visualization layout dataclasses. |
| `src/pygrc/visualization/render.py` | Generic trajectory, event, and report-panel rendering. |
| `src/pygrc/visualization/graph_render.py` | Graph checkpoint sequence, snapshot, HTML, and animation rendering. |
| `src/pygrc/visualization/representative.py` | Representative visual suites for GRCV2, GRCV3, GRC9, GRC9V3, and landscape lanes. |
| `src/pygrc/visualization/representative_graphs.py` | Representative graph visualization suites. |
| `src/pygrc/visualization/grcl9_lowering.py` | GRCL-9 lowered-source visual session renderer. |
| `src/pygrc/visualization/grcl9v3_lowering.py` | GRCL-9V3 selector-backed lowered-source visual review renderer. |
| `src/pygrc/visualization/motion.py` | Static and animated motion visual renderers. |

Module roles:

- `render.py` is the generic behavior renderer. It turns telemetry rows and run
  reports into trajectory plots, event timelines, and report panels.
- `graph_render.py` is the generic checkpoint renderer. It renders checkpoint
  snapshots, sequence sheets, GIF animations, HTML graph views, and comparison
  graphs.
- `representative.py` is a convenience suite for known representative lanes. It
  combines behavior plots and, when requested, graph outputs for GRCV2, GRCV3,
  GRC9, GRC9V3, and landscape lanes.
- `representative_graphs.py` is the graph-only half of the representative
  suites. Use it when behavior plots already exist or when checking checkpoint
  overlays only.
- `grcl9_lowering.py` and `grcl9v3_lowering.py` know the lowered-source session
  layouts and selector artifacts for the GRCL families.
- `motion.py` renders static two-checkpoint motion summaries and multi-frame
  motion animations.

Public imports are exposed from `pygrc.visualization` via `__all__`. Heavy
GRCL and motion renderers are lazily imported so simple layout imports do not
load every renderer.

## Visual Surfaces

### Generic Telemetry Surfaces

Generic run visual bundles render:

- `trajectories.png`
- `events.png`
- `report_panel.png`

Generic comparison bundles render:

- `comparison_trajectories.png`
- `comparison_panel.png`

These surfaces are built from `TelemetryArtifactPack` data and are useful for
observables, event counts, and run-summary inspection.

### Graph Checkpoint Surfaces

Graph visualization bundles render:

- `graph_snapshots/`
- `graph_html/final_graph.html`
- `graph_sequence.png`
- `graph_animation.gif`
- `graph_layouts.json`

Graph comparison bundles render:

- `graph_comparison.png`

Graph renderers require checkpoint artifacts. If a run only has step rows and
summary data, graph visuals cannot reconstruct per-node or per-edge state.

### GRC9V3 Lane B Visuals

GRC9V3 Lane B uses the same runtime lifecycle and the same
`hybrid_spark_candidate` event kind as Lane A. Visual renderers therefore use
payload evidence, not the event kind alone, to distinguish candidate classes.

The generic event timeline and report panel classify GRC9V3 spark candidates as:

| Visual class | Evidence |
|---|---|
| `lane_a_signed_hessian_candidate` | `hybrid_spark_candidate` without Lane B spark-lane evidence. |
| `lane_b_signed_hessian_candidate` | `payload.spark_lane = "grc9v3_column_h_assisted"` and `column_h_branch_hit = false`. |
| `lane_b_column_h_branch_candidate` | `payload.spark_lane = "grc9v3_column_h_assisted"` and `column_h_branch_hit = true`, or a column-H reason in `gate_reasons`. |

The default GRC9V3 run observables include numeric Lane B diagnostic series:

```text
family_extensions.grc9v3.hybrid_spark_state.last_candidate_min_abs_column_h
family_extensions.grc9v3.hybrid_spark_state.last_candidate_column_h_branch_hit
```

`last_candidate_spark_lane` is used as report and timeline metadata rather than
as a numeric trajectory series.

Graph checkpoint visualization also reads GRC9V3 node overlays. A node with:

```text
node_overlay.<node_id>.column_h_branch_hit = true
```

is rendered with the Lane B column-H branch styling: a green border, thicker
stroke, and an `H` suffix on the node label. HTML graph titles include
supporting overlay details such as `spark_lane`, `min_abs_column_h`, and
`column_h_gate_reasons` when present.

These visuals make the Lane A/Lane B distinction legible, but they remain
supporting evidence. The event payload and telemetry contract remain
authoritative for whether the column-H proxy branch fired.

### GRCL Lowering Review Surfaces

GRCL lowered-source visual review overlays source/lowering metadata on runtime
telemetry and checkpoints.

GRCL-9 visual sessions can include:

- overlay images,
- boundary/source-runtime panels,
- overlay summaries,
- phase-diagram summaries for relevant batches,
- visual index files.

GRCL-9V3 visual sessions include:

- `visual_index.json`
- `reports/visual_review_report.json`
- `reports/visual_review_summary.md`
- `visualizations/`
- per-lane overlays and source/runtime boundary summaries.

### Motion Visual Surfaces

Motion static visuals render:

- `motion_graph.png`
- `motion_timeline.png`
- `motion_visual_summary.json`

Motion animated visuals render:

- `motion_animation.gif`
- `motion_sequence.png`
- `motion_frames/`
- `motion_animated_summary.json`
- graph-engine animation outputs under `graph_engine/`
- `animated_visual_manifest.json`
- `animated_visual_review_report.json`

Motion visuals always link back to motion records and checkpoint IDs.

## Claim Boundary

Visualization metadata should preserve these rules:

- visuals do not create new claims,
- visual-only promotion is forbidden,
- selector records and observer records remain authoritative,
- source-authored conditions are not runtime proof,
- ambiguous or diagnostic records remain ambiguous or diagnostic even if the
  graph looks suggestive.

Motion visual summaries explicitly include:

```json
{
  "visual_claims": "none",
  "no_visual_only_promotion": true
}
```

Use visuals to inspect and communicate evidence, not to replace selectors,
catalog review, or inference records.

## Output Layouts

Default filenames are defined in `layout.py`.

| Constant | Filename |
|---|---|
| `TRAJECTORY_FIGURE_FILENAME` | `trajectories.png` |
| `EVENT_TIMELINE_FILENAME` | `events.png` |
| `RUN_REPORT_PANEL_FILENAME` | `report_panel.png` |
| `GRAPH_SEQUENCE_FIGURE_FILENAME` | `graph_sequence.png` |
| `GRAPH_ANIMATION_FILENAME` | `graph_animation.gif` |
| `GRAPH_LAYOUT_FILENAME` | `graph_layouts.json` |
| `GRAPH_FINAL_HTML_FILENAME` | `final_graph.html` |
| `GRAPH_COMPARISON_FIGURE_FILENAME` | `graph_comparison.png` |

Motion-specific filenames are defined in `motion.py`.

Typical output trees:

```text
<visualization-root>/<run-id>/
  trajectories.png
  events.png
  report_panel.png
  graph_snapshots/
  graph_html/final_graph.html
  graph_sequence.png
  graph_animation.gif
  graph_layouts.json
```

```text
outputs/motion/sessions/<SESSION_ID>/visualizations/<example>/
  motion_graph.png
  motion_timeline.png
  motion_visual_summary.json
  motion_animation.gif
  motion_sequence.png
  motion_frames/
  graph_engine/
  motion_animated_summary.json
```

```text
outputs/grcl9v3/lowering/sessions/<VISUAL_SESSION_ID>/
  visual_index.json
  reports/visual_review_report.json
  reports/visual_review_summary.md
  visualizations/
```

## CLI Examples

### GRCL-9 Lowered-Source Visuals

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9_lowering \
  --session-root outputs/grcl9/lowering/sessions/SESSION_ID \
  --fixture corrected_pressure_boundary_positive_high
```

Options:

- `--session-root`: lowered-source session root. Default:
  `outputs/grcl9/lowering/sessions/S0001`.
- `--fixture`: fixture/lane to render; can be supplied multiple times.
- `--force-legacy-growth`: required for quarantined legacy broad-growth
  sessions. Outputs remain diagnostic non-evidence.

### GRCL-9V3 Lowered-Source Visual Review

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering \
  --session-id VISUAL_SESSION_ID \
  --selector-session-id SELECTOR_SESSION_ID \
  --output-root outputs/grcl9v3/lowering
```

Options:

- `--session-id`: output visual session ID. Default: `S0003`.
- `--selector-session-id`: selector-validation session to visualize. Default:
  `S0002`.
- `--output-root`: GRCL-9V3 lowering output root. Default:
  `outputs/grcl9v3/lowering`.

### Motion Static Visuals

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.motion \
  --session-root outputs/motion/sessions/SESSION_ID \
  --example identity_walking_control
```

Options:

- `--session-root`: motion session root. Default:
  `outputs/motion/sessions/S0001`.
- `--example`: example to render; can be supplied multiple times.

### Motion Animated Visuals

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.motion \
  --session-root outputs/motion/sessions/SESSION_ID \
  --animated \
  --example motion_long_relay_walk_frontier
```

Add `--no-static` with `--animated` to skip regenerating the static visuals.
The API equivalent is `render_static=False`; the default is `True`.

## API Examples

### Render Motion Static Visuals

```python
from pygrc.visualization.motion import render_motion_visual_session

session = render_motion_visual_session(
    session_root="outputs/motion/sessions/S0001",
    example_names=("identity_walking_control",),
)

print(session.visual_root)
print(len(session.records))
```

### Render Motion Animated Visuals

```python
from pygrc.visualization.motion import render_motion_animated_visual_session

session = render_motion_animated_visual_session(
    session_root="outputs/motion/sessions/S0003",
    example_names=("motion_long_relay_walk_frontier",),
    render_static=False,
)

print(session.animated_manifest_path)
```

### Render GRCL-9V3 Visual Review

```python
from pathlib import Path
from pygrc.visualization.grcl9v3_lowering import render_grcl9v3_lowering_visual_review

session = render_grcl9v3_lowering_visual_review(
    session_id="S9003",
    selector_session_id="S9002",
    output_root=Path("outputs/grcl9v3/lowering"),
)

print(session.visual_index_path)
```

### Use Generic Graph Rendering

```python
from pygrc.telemetry.io import build_telemetry_artifact_layout, load_telemetry_artifact_pack
from pygrc.visualization import (
    build_graph_run_visualization_layout,
    render_graph_run_visual_bundle,
)

layout = build_telemetry_artifact_layout(
    "example-run-id",
    root_dir="outputs/example_telemetry",
)
pack = load_telemetry_artifact_pack(layout)
visual_layout = build_graph_run_visualization_layout(pack.layout)
render_graph_run_visual_bundle(pack, layout=visual_layout)
```

This generic API is useful for standard telemetry packs. Session-specific lanes
often use dedicated renderers because they already know the session layout.

## Reading Visual Summaries

Visual summary JSON files are the best machine-readable entry point.

For motion:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

summary = json.loads(
    Path(
        "outputs/motion/sessions/S0001/visualizations/"
        "identity_walking_control/motion_visual_summary.json"
    ).read_text(encoding="utf-8")
)

print(summary["claim_boundary"])
print(summary["checkpoint_linkage"])
print(summary["rendered_surfaces"])
PY
```

For GRCL-9V3:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

index = json.loads(
    Path("outputs/grcl9v3/lowering/sessions/S9003/visual_index.json")
    .read_text(encoding="utf-8")
)

print(index.keys())
PY
```

## Dense And Sparse Graphs

The renderer currently uses two complementary strategies:

- sparse graph overlays for checkpoint-local inspection,
- dense record panels, sequence sheets, or confidence/time sampling when many
  records or checkpoints would overload a single graph panel.

For dense motion windows, prefer animated visual sessions and sequence sheets.
For large checkpoint fields, use visual summaries and catalogs as the review
entry point before opening every image.

## Troubleshooting

Common issues:

- `FileNotFoundError` for a session root, `selector_manifest.json`,
  `selector_validation_report.json`, or visual summary: the upstream replay,
  selector, or motion session has not been generated at that path.
- Missing graph outputs: the source telemetry did not include graph
  checkpoints, so graph renderers cannot reconstruct per-node or per-edge
  state.
- Static motion rendering fails with `ValueError`: the selected run has fewer
  than two checkpoints.
- Animation rendering fails with `ValueError`: the selected run has fewer than
  two checkpoints or no frame images can be produced.
- Empty visual session: selector records were rejected, weak, or skipped by the
  visual renderer.
- Legacy growth refusal: pass `--force-legacy-growth` only for diagnostic
  historical review.
- Dense graph unreadable: inspect `motion_visual_summary.json`,
  `visual_index.json`, and sequence images before reviewing individual frames.

## Current Evidence Anchors

Representative visual outputs in this workspace include:

- `outputs/grcl9v3/lowering/sessions/S0070/`
- `outputs/motion/sessions/S0001/visualizations/`
- `outputs/motion/sessions/S0003/visualizations/`
- `outputs/motion/sessions/S0004/visualizations/`
- `outputs/phase-t-grc9v3/representative/appendix_e_cell_division/`

Generated session IDs are workspace artifacts. Use each session's manifest,
visual index, or visual summary to interpret it.

## Related Guides

- [Telemetry Reference Guide](Telemetry-ReferenceGuide.md)
- [Landscape Compiler And Lowering Reference Guide](LandscapeCompiler-ReferenceGuide.md)
- [Landscape Inference Reference Guide](LandscapeInference-ReferenceGuide.md)
- [Motion Reference Guide](Motion-ReferenceGuide.md)
