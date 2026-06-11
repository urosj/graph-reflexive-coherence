"""Deterministic output layout helpers for visualization artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from pygrc.telemetry import DEFAULT_EXPERIMENTS_ROOT, TelemetryArtifactLayout


DEFAULT_VISUALIZATION_ROOT = DEFAULT_EXPERIMENTS_ROOT
VISUALIZATION_DIRNAME = "visualization"
TRAJECTORY_FIGURE_FILENAME = "trajectories.png"
EVENT_TIMELINE_FILENAME = "events.png"
RUN_REPORT_PANEL_FILENAME = "report_panel.png"
COMPARISON_TRAJECTORY_FIGURE_FILENAME = "comparison_trajectories.png"
COMPARISON_REPORT_PANEL_FILENAME = "comparison_panel.png"
GRAPH_SNAPSHOTS_DIRNAME = "graph_snapshots"
GRAPH_HTML_DIRNAME = "graph_html"
GRAPH_SEQUENCE_FIGURE_FILENAME = "graph_sequence.png"
GRAPH_ANIMATION_FILENAME = "graph_animation.gif"
GRAPH_LAYOUT_FILENAME = "graph_layouts.json"
GRAPH_FINAL_HTML_FILENAME = "final_graph.html"
GRAPH_COMPARISON_FIGURE_FILENAME = "graph_comparison.png"


@dataclass(frozen=True)
class RunVisualizationLayout:
    """Deterministic visualization output layout for one telemetry run."""

    root_dir: Path
    run_id: str
    run_dir: Path
    trajectory_figure_path: Path
    event_timeline_path: Path
    report_panel_path: Path


@dataclass(frozen=True)
class ComparisonVisualizationLayout:
    """Deterministic visualization output layout for one comparison bundle."""

    root_dir: Path
    comparison_id: str
    comparison_dir: Path
    trajectory_figure_path: Path
    report_panel_path: Path


@dataclass(frozen=True)
class GraphRunVisualizationLayout:
    """Deterministic graph-visualization output layout for one telemetry run."""

    root_dir: Path
    run_id: str
    run_dir: Path
    snapshots_dir: Path
    html_dir: Path
    sequence_figure_path: Path
    animation_path: Path
    layout_json_path: Path
    final_html_path: Path


@dataclass(frozen=True)
class GraphComparisonVisualizationLayout:
    """Deterministic graph-comparison layout for one pairwise bundle."""

    root_dir: Path
    comparison_id: str
    comparison_dir: Path
    final_comparison_path: Path


def map_telemetry_root_to_visualization_root(
    telemetry_root: str | Path,
    *,
    default_visualization_root: str | Path = DEFAULT_VISUALIZATION_ROOT,
) -> Path:
    """Map an artifact root into the visualization parent root."""

    path = Path(telemetry_root)
    parts = list(path.parts)
    if "telemetry" in parts:
        index = parts.index("telemetry")
        suffix = parts[index + 1 :]
        return Path(default_visualization_root).joinpath(*suffix)
    if "experiments" in parts:
        index = parts.index("experiments")
        suffix = parts[index + 1 :]
        return Path(default_visualization_root).joinpath(*suffix)
    default_root = Path(default_visualization_root)
    return default_root / path.name


def build_run_visualization_layout(
    telemetry_layout: TelemetryArtifactLayout,
    *,
    visualization_root: str | Path | None = None,
) -> RunVisualizationLayout:
    """Build the visualization layout for one telemetry run."""

    root_dir = (
        telemetry_layout.run_dir if visualization_root is None else Path(visualization_root) / telemetry_layout.run_id
    )
    run_dir = root_dir / VISUALIZATION_DIRNAME
    return RunVisualizationLayout(
        root_dir=root_dir,
        run_id=telemetry_layout.run_id,
        run_dir=run_dir,
        trajectory_figure_path=run_dir / TRAJECTORY_FIGURE_FILENAME,
        event_timeline_path=run_dir / EVENT_TIMELINE_FILENAME,
        report_panel_path=run_dir / RUN_REPORT_PANEL_FILENAME,
    )


def build_comparison_visualization_layout(
    left: TelemetryArtifactLayout,
    right: TelemetryArtifactLayout,
    *,
    visualization_root: str | Path | None = None,
) -> ComparisonVisualizationLayout:
    """Build the visualization layout for one pairwise comparison."""

    common_root = Path(os.path.commonpath([str(left.root_dir), str(right.root_dir)]))
    root_dir = (
        common_root
        if visualization_root is None
        else Path(visualization_root)
    )
    comparison_id = f"{left.run_id}__vs__{right.run_id}"
    comparison_dir = root_dir / "comparison" / comparison_id / VISUALIZATION_DIRNAME
    return ComparisonVisualizationLayout(
        root_dir=root_dir,
        comparison_id=comparison_id,
        comparison_dir=comparison_dir,
        trajectory_figure_path=comparison_dir / COMPARISON_TRAJECTORY_FIGURE_FILENAME,
        report_panel_path=comparison_dir / COMPARISON_REPORT_PANEL_FILENAME,
    )


def build_graph_run_visualization_layout(
    telemetry_layout: TelemetryArtifactLayout,
    *,
    visualization_root: str | Path | None = None,
) -> GraphRunVisualizationLayout:
    """Build the graph-visualization layout for one telemetry run."""

    root_dir = (
        telemetry_layout.run_dir if visualization_root is None else Path(visualization_root) / telemetry_layout.run_id
    )
    run_dir = root_dir / VISUALIZATION_DIRNAME
    return GraphRunVisualizationLayout(
        root_dir=root_dir,
        run_id=telemetry_layout.run_id,
        run_dir=run_dir,
        snapshots_dir=run_dir / GRAPH_SNAPSHOTS_DIRNAME,
        html_dir=run_dir / GRAPH_HTML_DIRNAME,
        sequence_figure_path=run_dir / GRAPH_SEQUENCE_FIGURE_FILENAME,
        animation_path=run_dir / GRAPH_ANIMATION_FILENAME,
        layout_json_path=run_dir / GRAPH_LAYOUT_FILENAME,
        final_html_path=run_dir / GRAPH_HTML_DIRNAME / GRAPH_FINAL_HTML_FILENAME,
    )


def build_graph_comparison_visualization_layout(
    left: TelemetryArtifactLayout,
    right: TelemetryArtifactLayout,
    *,
    visualization_root: str | Path | None = None,
) -> GraphComparisonVisualizationLayout:
    """Build the graph-comparison layout for one pairwise comparison."""

    common_root = Path(os.path.commonpath([str(left.root_dir), str(right.root_dir)]))
    root_dir = (
        common_root
        if visualization_root is None
        else Path(visualization_root)
    )
    comparison_id = f"{left.run_id}__vs__{right.run_id}"
    comparison_dir = root_dir / "comparison" / comparison_id / VISUALIZATION_DIRNAME
    return GraphComparisonVisualizationLayout(
        root_dir=root_dir,
        comparison_id=comparison_id,
        comparison_dir=comparison_dir,
        final_comparison_path=comparison_dir / GRAPH_COMPARISON_FIGURE_FILENAME,
    )
__all__ = [
    "COMPARISON_REPORT_PANEL_FILENAME",
    "COMPARISON_TRAJECTORY_FIGURE_FILENAME",
    "DEFAULT_VISUALIZATION_ROOT",
    "EVENT_TIMELINE_FILENAME",
    "GRAPH_ANIMATION_FILENAME",
    "GRAPH_COMPARISON_FIGURE_FILENAME",
    "GRAPH_FINAL_HTML_FILENAME",
    "GRAPH_HTML_DIRNAME",
    "GRAPH_LAYOUT_FILENAME",
    "GRAPH_SEQUENCE_FIGURE_FILENAME",
    "GRAPH_SNAPSHOTS_DIRNAME",
    "ComparisonVisualizationLayout",
    "GraphComparisonVisualizationLayout",
    "GraphRunVisualizationLayout",
    "RUN_REPORT_PANEL_FILENAME",
    "RunVisualizationLayout",
    "TRAJECTORY_FIGURE_FILENAME",
    "VISUALIZATION_DIRNAME",
    "build_graph_comparison_visualization_layout",
    "build_graph_run_visualization_layout",
    "build_comparison_visualization_layout",
    "build_run_visualization_layout",
    "map_telemetry_root_to_visualization_root",
]
