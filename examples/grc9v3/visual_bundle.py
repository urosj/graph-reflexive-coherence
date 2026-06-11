"""Render behavior and graph visuals from the GRC9V3 telemetry example.

What this example does:
    Loads the telemetry artifact pack produced by `telemetry_capture.py` and
    renders the public visualization bundles:

    - behavior trajectories;
    - event timeline;
    - graph snapshots;
    - graph sequence/contact sheet;
    - final interactive HTML graph;
    - graph animation when more than one checkpoint is present.

Why it is needed:
    Visualization should consume saved telemetry artifacts, not a live model.
    This keeps visuals as supporting evidence for the same rows/events that
    reports inspect.

Alternatives:
    Use the visualization package directly for custom layouts. Use experiment
    renderers for full representative suites.

References:
    docs/reference/GraphVisualization-ReferenceGuide.md
    docs/reference/Telemetry-ReferenceGuide.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from _fixtures import print_json
from telemetry_capture import (
    EXAMPLE_OUTPUT_ROOT,
    TELEMETRY_RUN_DIR_NAME,
    capture_example_telemetry,
)
from pygrc.telemetry import build_telemetry_artifact_layout, load_telemetry_artifact_pack
from pygrc.visualization import (
    DEFAULT_GRC9V3_RUN_OBSERVABLES,
    build_graph_run_visualization_layout,
    build_run_visualization_layout,
    render_graph_run_visual_bundle,
    render_run_visual_bundle,
)


def render_example_visuals() -> dict[str, Any]:
    """Load telemetry artifacts and render behavior plus graph visuals."""

    telemetry_layout = build_telemetry_artifact_layout(
        TELEMETRY_RUN_DIR_NAME,
        root_dir=EXAMPLE_OUTPUT_ROOT,
    )
    if not telemetry_layout.run_summary_path.exists():
        capture_example_telemetry()

    pack = load_telemetry_artifact_pack(telemetry_layout)
    behavior_layout = build_run_visualization_layout(telemetry_layout)
    graph_layout = build_graph_run_visualization_layout(telemetry_layout)

    render_run_visual_bundle(
        pack,
        layout=behavior_layout,
        observables=DEFAULT_GRC9V3_RUN_OBSERVABLES,
    )
    render_graph_run_visual_bundle(pack, layout=graph_layout)

    outputs = {
        "telemetry_run_dir": str(telemetry_layout.run_dir),
        "behavior_visualization_dir": str(behavior_layout.run_dir),
        "graph_visualization_dir": str(graph_layout.run_dir),
        "trajectories": str(behavior_layout.trajectory_figure_path),
        "events": str(behavior_layout.event_timeline_path),
        "graph_sequence": str(graph_layout.sequence_figure_path),
        "final_graph_html": str(graph_layout.final_html_path),
        "graph_layouts": str(graph_layout.layout_json_path),
    }
    if graph_layout.animation_path.exists():
        outputs["graph_animation"] = str(graph_layout.animation_path)
    snapshot_count = len(tuple(graph_layout.snapshots_dir.glob("*.png")))
    outputs["graph_snapshot_count"] = snapshot_count
    return outputs


def main() -> None:
    """Render visuals and print output paths."""

    print("GRC9V3 Lane B visual bundle")
    print_json("visual_outputs", render_example_visuals())
    print(
        "\nInterpretation: visuals distinguish the Lane B column-H branch by "
        "using saved event/checkpoint evidence. Telemetry remains the "
        "authoritative source."
    )


if __name__ == "__main__":
    main()
