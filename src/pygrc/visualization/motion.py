"""Visualization review for motion inference reports."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/pygrc-matplotlib")

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from PIL import Image

from pygrc.core import canonical_json_dumps, canonicalize_json_value
from pygrc.telemetry import GraphCheckpointArtifact, TelemetryArtifactPack
from pygrc.telemetry.io import (
    build_telemetry_artifact_layout,
    load_telemetry_artifact_pack,
)
from pygrc.visualization.graph_render import render_graph_run_visual_bundle
from pygrc.visualization.layout import GraphRunVisualizationLayout


MOTION_VISUALIZATION_VERSION = "motion_visualization_iter9_v1"
MOTION_ANIMATED_VISUALIZATION_VERSION = "motion_visualization_iter12_v1"
DEFAULT_MOTION_VISUALIZATION_SESSION_ROOT = Path("outputs/motion/sessions/S0001")
MOTION_GRAPH_FILENAME = "motion_graph.png"
MOTION_TIMELINE_FILENAME = "motion_timeline.png"
MOTION_VISUAL_SUMMARY_FILENAME = "motion_visual_summary.json"
MOTION_ANIMATION_FILENAME = "motion_animation.gif"
MOTION_SEQUENCE_FILENAME = "motion_sequence.png"
MOTION_ANIMATED_SUMMARY_FILENAME = "motion_animated_summary.json"

_CLAIM_BOUNDARY = (
    "supporting_visual_only_motion_claims_come_from_motion_reports_not_from_visuals"
)
_MAX_TIMELINE_RECORDS = 120


@dataclass(frozen=True)
class MotionVisualRecord:
    """One rendered motion visualization record."""

    example_name: str
    runtime_family: str
    run_dir: Path
    visual_dir: Path
    graph_path: Path
    timeline_path: Path
    summary_path: Path
    motion_report_paths: tuple[Path, ...]
    motion_record_ids: tuple[str, ...]
    checkpoint_ids: tuple[str, ...]
    visual_status: str = "rendered_supporting_only"

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "visualization_version": MOTION_VISUALIZATION_VERSION,
                "example_name": self.example_name,
                "runtime_family": self.runtime_family,
                "run_dir": str(self.run_dir),
                "visual_dir": str(self.visual_dir),
                "graph_path": str(self.graph_path),
                "timeline_path": str(self.timeline_path),
                "summary_path": str(self.summary_path),
                "motion_report_paths": [str(path) for path in self.motion_report_paths],
                "motion_record_ids": list(self.motion_record_ids),
                "checkpoint_ids": list(self.checkpoint_ids),
                "visual_status": self.visual_status,
                "claim_boundary": _CLAIM_BOUNDARY,
            }
        )


@dataclass(frozen=True)
class MotionVisualReviewSession:
    """Iteration 9 visual review session."""

    session_root: Path
    visual_root: Path
    records: tuple[MotionVisualRecord, ...]
    visual_manifest_path: Path
    report_path: Path
    readme_path: Path

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "visualization_version": MOTION_VISUALIZATION_VERSION,
                "source_session_root": str(self.session_root),
                "visual_root": str(self.visual_root),
                "visual_count": len(self.records),
                "records": [record.to_mapping() for record in self.records],
                "claim_boundary": _CLAIM_BOUNDARY,
                "temporal_rendering_status": (
                    "static_two_checkpoint_rendering_complete_temporal_animation_deferred"
                ),
            }
        )


@dataclass(frozen=True)
class MotionAnimatedVisualRecord:
    """One graph-engine-backed animated motion visualization record."""

    example_name: str
    runtime_family: str
    run_dir: Path
    visual_dir: Path
    graph_engine_dir: Path
    graph_engine_sequence_path: Path
    graph_engine_animation_path: Path
    motion_frames_dir: Path
    motion_sequence_path: Path
    motion_animation_path: Path
    animated_summary_path: Path
    motion_report_paths: tuple[Path, ...]
    motion_record_ids: tuple[str, ...]
    checkpoint_ids: tuple[str, ...]
    frame_count: int
    visual_status: str = "rendered_supporting_only"

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "visualization_version": MOTION_ANIMATED_VISUALIZATION_VERSION,
                "example_name": self.example_name,
                "runtime_family": self.runtime_family,
                "run_dir": str(self.run_dir),
                "visual_dir": str(self.visual_dir),
                "graph_engine_dir": str(self.graph_engine_dir),
                "graph_engine_sequence_path": str(self.graph_engine_sequence_path),
                "graph_engine_animation_path": str(self.graph_engine_animation_path),
                "motion_frames_dir": str(self.motion_frames_dir),
                "motion_sequence_path": str(self.motion_sequence_path),
                "motion_animation_path": str(self.motion_animation_path),
                "animated_summary_path": str(self.animated_summary_path),
                "motion_report_paths": [str(path) for path in self.motion_report_paths],
                "motion_record_ids": list(self.motion_record_ids),
                "checkpoint_ids": list(self.checkpoint_ids),
                "frame_count": self.frame_count,
                "visual_status": self.visual_status,
                "claim_boundary": _CLAIM_BOUNDARY,
            }
        )


@dataclass(frozen=True)
class MotionAnimatedVisualReviewSession:
    """Iteration 12 animated visual review session."""

    session_root: Path
    visual_root: Path
    records: tuple[MotionAnimatedVisualRecord, ...]
    animated_manifest_path: Path
    report_path: Path
    readme_path: Path
    static_session: MotionVisualReviewSession | None = None

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "visualization_version": MOTION_ANIMATED_VISUALIZATION_VERSION,
                "source_session_root": str(self.session_root),
                "visual_root": str(self.visual_root),
                "animated_visual_count": len(self.records),
                "records": [record.to_mapping() for record in self.records],
                "claim_boundary": _CLAIM_BOUNDARY,
                "temporal_rendering_status": "graph_engine_sequence_and_motion_animation_complete",
                "static_visualization_manifest": (
                    None
                    if self.static_session is None
                    else str(self.static_session.visual_manifest_path)
                ),
            }
        )


def render_motion_visual_session(
    *,
    session_root: str | Path = DEFAULT_MOTION_VISUALIZATION_SESSION_ROOT,
    example_names: Sequence[str] | None = None,
) -> MotionVisualReviewSession:
    """Render visual evidence for one Iteration 8 motion example session."""

    root = Path(session_root)
    run_report_path = root / "run_report.json"
    if not run_report_path.exists():
        raise FileNotFoundError(f"motion example run_report.json not found: {run_report_path}")
    run_report = _read_json(run_report_path)
    selected_names = None if example_names is None else set(example_names)
    visual_root = root / "visualizations"
    visual_root.mkdir(parents=True, exist_ok=True)

    records: list[MotionVisualRecord] = []
    for example in _run_entries_from_report(run_report):
        example_name = str(example["example_name"])
        if selected_names is not None and example_name not in selected_names:
            continue
        record = _render_example_visual(
            visual_root=visual_root,
            example_name=example_name,
            runtime_family=str(example["runtime_family"]),
            run_dir=Path(str(example["run_dir"])),
        )
        records.append(record)

    session = MotionVisualReviewSession(
        session_root=root,
        visual_root=visual_root,
        records=tuple(records),
        visual_manifest_path=visual_root / "visual_manifest.json",
        report_path=visual_root / "visual_review_report.json",
        readme_path=visual_root / "README.md",
    )
    _write_json(session.visual_manifest_path, session.to_mapping())
    _write_json(session.report_path, _review_report(session))
    _write_text(session.readme_path, _readme(session))
    return session


def render_motion_animated_visual_session(
    *,
    session_root: str | Path = DEFAULT_MOTION_VISUALIZATION_SESSION_ROOT,
    example_names: Sequence[str] | None = None,
    render_static: bool = True,
) -> MotionAnimatedVisualReviewSession:
    """Render graph-engine-backed animated visual evidence for motion sessions."""

    root = Path(session_root)
    static_session = (
        render_motion_visual_session(session_root=root, example_names=example_names)
        if render_static
        else None
    )
    run_report_path = root / "run_report.json"
    if not run_report_path.exists():
        raise FileNotFoundError(f"motion example run_report.json not found: {run_report_path}")
    run_report = _read_json(run_report_path)
    selected_names = None if example_names is None else set(example_names)
    visual_root = root / "visualizations"
    visual_root.mkdir(parents=True, exist_ok=True)

    records: list[MotionAnimatedVisualRecord] = []
    for example in _run_entries_from_report(run_report):
        example_name = str(example["example_name"])
        if selected_names is not None and example_name not in selected_names:
            continue
        records.append(
            _render_example_animation(
                visual_root=visual_root,
                example_name=example_name,
                runtime_family=str(example["runtime_family"]),
                run_dir=Path(str(example["run_dir"])),
            )
        )

    session = MotionAnimatedVisualReviewSession(
        session_root=root,
        visual_root=visual_root,
        records=tuple(records),
        animated_manifest_path=visual_root / "animated_visual_manifest.json",
        report_path=visual_root / "animated_visual_review_report.json",
        readme_path=visual_root / "ANIMATION_README.md",
        static_session=static_session,
    )
    _write_json(session.animated_manifest_path, session.to_mapping())
    _write_json(session.report_path, _animated_review_report(session))
    _write_text(session.readme_path, _animated_readme(session))
    return session


def _run_entries_from_report(run_report: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    direct_examples = run_report.get("examples", ())
    if isinstance(direct_examples, Sequence) and not isinstance(direct_examples, str | bytes):
        entries = tuple(item for item in direct_examples if isinstance(item, Mapping))
        if entries:
            return entries
    authored_runs = run_report.get("runs", ())
    entries: list[Mapping[str, Any]] = []
    if isinstance(authored_runs, Sequence) and not isinstance(authored_runs, str | bytes):
        for run in authored_runs:
            if not isinstance(run, Mapping):
                continue
            if "example_name" in run and "run_dir" in run:
                entries.append(run)
                continue
            projected = run.get("projected_runs", ())
            if not isinstance(projected, Sequence) or isinstance(projected, str | bytes):
                continue
            entries.extend(item for item in projected if isinstance(item, Mapping))
    return tuple(entries)


def _render_example_visual(
    *,
    visual_root: Path,
    example_name: str,
    runtime_family: str,
    run_dir: Path,
) -> MotionVisualRecord:
    pack = _load_pack_from_run_dir(run_dir)
    reports = _load_motion_reports(run_dir)
    motion_records = tuple(
        record
        for report in reports
        for record in tuple(report.get("records", ()))
        if isinstance(record, Mapping)
    )
    checkpoints = _sorted_checkpoints(pack.graph_checkpoints)
    if len(checkpoints) < 2:
        raise ValueError(f"motion visualization requires at least two checkpoints: {run_dir}")

    visual_dir = visual_root / example_name
    visual_dir.mkdir(parents=True, exist_ok=True)
    graph_path = visual_dir / MOTION_GRAPH_FILENAME
    timeline_path = visual_dir / MOTION_TIMELINE_FILENAME
    summary_path = visual_dir / MOTION_VISUAL_SUMMARY_FILENAME

    positions = _union_positions(checkpoints)
    _render_graph_overlay(
        checkpoints=checkpoints,
        motion_records=motion_records,
        positions=positions,
        output_path=graph_path,
        title=example_name,
    )
    _render_motion_timeline(
        motion_records=motion_records,
        output_path=timeline_path,
        title=example_name,
    )
    report_paths = _motion_report_paths(run_dir)
    motion_record_ids = tuple(
        str(record.get("motion_id"))
        for record in motion_records
        if isinstance(record.get("motion_id"), str)
    )
    checkpoint_ids = tuple(checkpoint.checkpoint_id for checkpoint in checkpoints)
    visual_record = MotionVisualRecord(
        example_name=example_name,
        runtime_family=runtime_family,
        run_dir=run_dir,
        visual_dir=visual_dir,
        graph_path=graph_path,
        timeline_path=timeline_path,
        summary_path=summary_path,
        motion_report_paths=report_paths,
        motion_record_ids=motion_record_ids,
        checkpoint_ids=checkpoint_ids,
    )
    _write_json(
        summary_path,
        _visual_summary(
            visual_record,
            pack=pack,
            motion_records=motion_records,
            report_paths=report_paths,
        ),
    )
    return visual_record


def _render_example_animation(
    *,
    visual_root: Path,
    example_name: str,
    runtime_family: str,
    run_dir: Path,
) -> MotionAnimatedVisualRecord:
    pack = _load_pack_from_run_dir(run_dir)
    reports = _load_motion_reports(run_dir)
    motion_records = tuple(
        record
        for report in reports
        for record in tuple(report.get("records", ()))
        if isinstance(record, Mapping)
    )
    checkpoints = _sorted_checkpoints(pack.graph_checkpoints)
    if len(checkpoints) < 2:
        raise ValueError(f"motion animation requires at least two checkpoints: {run_dir}")

    visual_dir = visual_root / example_name
    visual_dir.mkdir(parents=True, exist_ok=True)
    graph_engine_layout = _graph_engine_layout(pack, visual_dir=visual_dir)
    render_graph_run_visual_bundle(pack, layout=graph_engine_layout)
    positions = _positions_from_graph_engine_layout(graph_engine_layout)
    if not positions:
        positions = _union_positions(checkpoints)

    frames_dir = visual_dir / "motion_frames"
    frame_paths = _render_motion_animation_frames(
        checkpoints=checkpoints,
        motion_records=motion_records,
        positions=positions,
        output_dir=frames_dir,
        title=example_name,
    )
    sequence_path = visual_dir / MOTION_SEQUENCE_FILENAME
    animation_path = visual_dir / MOTION_ANIMATION_FILENAME
    _render_motion_sequence_from_frames(frame_paths, output_path=sequence_path, title=example_name)
    _render_gif(frame_paths, output_path=animation_path)

    report_paths = _motion_report_paths(run_dir)
    motion_record_ids = tuple(
        str(record.get("motion_id"))
        for record in motion_records
        if isinstance(record.get("motion_id"), str)
    )
    checkpoint_ids = tuple(checkpoint.checkpoint_id for checkpoint in checkpoints)
    animated_record = MotionAnimatedVisualRecord(
        example_name=example_name,
        runtime_family=runtime_family,
        run_dir=run_dir,
        visual_dir=visual_dir,
        graph_engine_dir=graph_engine_layout.run_dir,
        graph_engine_sequence_path=graph_engine_layout.sequence_figure_path,
        graph_engine_animation_path=graph_engine_layout.animation_path,
        motion_frames_dir=frames_dir,
        motion_sequence_path=sequence_path,
        motion_animation_path=animation_path,
        animated_summary_path=visual_dir / MOTION_ANIMATED_SUMMARY_FILENAME,
        motion_report_paths=report_paths,
        motion_record_ids=motion_record_ids,
        checkpoint_ids=checkpoint_ids,
        frame_count=len(frame_paths),
    )
    _write_json(
        animated_record.animated_summary_path,
        _animated_visual_summary(
            animated_record,
            pack=pack,
            motion_records=motion_records,
            frame_paths=frame_paths,
        ),
    )
    _merge_static_summary_with_animation(visual_dir / MOTION_VISUAL_SUMMARY_FILENAME, animated_record)
    return animated_record


def _graph_engine_layout(
    pack: TelemetryArtifactPack,
    *,
    visual_dir: Path,
) -> GraphRunVisualizationLayout:
    graph_engine_dir = visual_dir / "graph_engine"
    run_id = pack.run_summary.identity.run_id
    return GraphRunVisualizationLayout(
        root_dir=graph_engine_dir,
        run_id=run_id,
        run_dir=graph_engine_dir,
        snapshots_dir=graph_engine_dir / "graph_snapshots",
        html_dir=graph_engine_dir / "graph_html",
        sequence_figure_path=graph_engine_dir / "graph_sequence.png",
        animation_path=graph_engine_dir / "graph_animation.gif",
        layout_json_path=graph_engine_dir / "graph_layouts.json",
        final_html_path=graph_engine_dir / "graph_html" / "final_graph.html",
    )


def _positions_from_graph_engine_layout(
    layout: GraphRunVisualizationLayout,
) -> dict[int, tuple[float, float]]:
    if not layout.layout_json_path.exists():
        return {}
    payload = _read_json(layout.layout_json_path)
    raw_positions = payload.get("node_positions")
    if not isinstance(raw_positions, Mapping):
        return {}
    positions: dict[int, tuple[float, float]] = {}
    for raw_node_id, value in raw_positions.items():
        if not isinstance(value, Mapping):
            continue
        x_value = _optional_float(value.get("x"))
        y_value = _optional_float(value.get("y"))
        if x_value is None or y_value is None:
            continue
        try:
            node_id = int(raw_node_id)
        except (TypeError, ValueError):
            continue
        positions[node_id] = (x_value, y_value)
    return positions


def _load_pack_from_run_dir(run_dir: Path) -> TelemetryArtifactPack:
    layout = build_telemetry_artifact_layout(run_dir.name, root_dir=run_dir.parent)
    return load_telemetry_artifact_pack(layout)


def _load_motion_reports(run_dir: Path) -> tuple[Mapping[str, Any], ...]:
    return tuple(_read_json(path) for path in _motion_report_paths(run_dir))


def _motion_report_paths(run_dir: Path) -> tuple[Path, ...]:
    for report_dir in (run_dir / "motion_reports", run_dir.parent / "motion_reports"):
        if report_dir.exists():
            return tuple(sorted(report_dir.glob("*_report.json")))
    return ()


def _sorted_checkpoints(
    checkpoints: Sequence[GraphCheckpointArtifact],
) -> tuple[GraphCheckpointArtifact, ...]:
    return tuple(
        sorted(
            checkpoints,
            key=lambda checkpoint: (
                checkpoint.step_index,
                checkpoint.time,
                checkpoint.checkpoint_id,
            ),
        )
    )


def _union_positions(
    checkpoints: Sequence[GraphCheckpointArtifact],
) -> dict[int, tuple[float, float]]:
    node_ids: set[int] = set()
    hints: dict[int, tuple[float, float]] = {}
    for checkpoint in checkpoints:
        for node in checkpoint.node_records:
            node_id = int(node["node_id"])
            node_ids.add(node_id)
            hint = _chart_hint(node)
            if hint is not None:
                hints.setdefault(node_id, hint)
    sorted_ids = sorted(node_ids)
    if not sorted_ids:
        raise ValueError("motion visualization requires checkpoint nodes")
    if len(sorted_ids) == 1:
        node_id = sorted_ids[0]
        return {node_id: hints.get(node_id, (0.0, 0.0))}
    positions: dict[int, tuple[float, float]] = {}
    for index, node_id in enumerate(sorted_ids):
        if node_id in hints:
            positions[node_id] = hints[node_id]
            continue
        angle = (2.0 * math.pi * index) / len(sorted_ids)
        positions[node_id] = (math.cos(angle), math.sin(angle))
    return positions


def _chart_hint(node: Mapping[str, Any]) -> tuple[float, float] | None:
    candidates = (node.get("chart_center_hint"), _payload(node).get("chart_center_hint"))
    for candidate in candidates:
        if (
            isinstance(candidate, Sequence)
            and not isinstance(candidate, str | bytes)
            and len(candidate) >= 2
        ):
            try:
                return (float(candidate[0]), float(candidate[1]))
            except (TypeError, ValueError):
                return None
    return None


def _render_graph_overlay(
    *,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
    motion_records: tuple[Mapping[str, Any], ...],
    positions: Mapping[int, tuple[float, float]],
    output_path: Path,
    title: str,
) -> None:
    initial = checkpoints[0]
    final = checkpoints[-1]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(1, 3, figsize=(15, 5), gridspec_kw={"width_ratios": [1, 1, 1.15]})
    old_ids = _carrier_node_ids(motion_records, "old_carriers")
    new_ids = _carrier_node_ids(motion_records, "new_carriers")
    topological_born_ids = _topological_node_ids(motion_records, "new_carriers")
    topological_removed_ids = _topological_node_ids(motion_records, "old_carriers")
    topological_evidence_ids = _topological_evidence_node_ids(motion_records)
    evidence_edge_ids = _evidence_edge_ids(motion_records)
    _draw_checkpoint_panel(
        axes[0],
        initial,
        positions=positions,
        old_ids=old_ids,
        new_ids=new_ids,
        topological_born_ids=topological_born_ids,
        topological_removed_ids=topological_removed_ids,
        topological_evidence_ids=topological_evidence_ids,
        evidence_edge_ids=evidence_edge_ids,
        panel_title="initial",
    )
    _draw_checkpoint_panel(
        axes[1],
        final,
        positions=positions,
        old_ids=old_ids,
        new_ids=new_ids,
        topological_born_ids=topological_born_ids,
        topological_removed_ids=topological_removed_ids,
        topological_evidence_ids=topological_evidence_ids,
        evidence_edge_ids=evidence_edge_ids,
        panel_title="final",
    )
    _draw_record_panel(axes[2], motion_records)
    figure.suptitle(f"Motion evidence: {title}", fontsize=13)
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def _draw_checkpoint_panel(
    axis: Any,
    checkpoint: GraphCheckpointArtifact,
    *,
    positions: Mapping[int, tuple[float, float]],
    old_ids: set[int],
    new_ids: set[int],
    topological_born_ids: set[int],
    topological_removed_ids: set[int],
    topological_evidence_ids: set[int],
    evidence_edge_ids: set[int],
    panel_title: str,
) -> None:
    axis.set_title(f"{panel_title}\n{checkpoint.checkpoint_id} step={checkpoint.step_index}", fontsize=10)
    node_by_id = {int(node["node_id"]): node for node in checkpoint.node_records}
    present_ids = set(node_by_id)
    for edge in checkpoint.edge_records:
        source = int(edge["source_node_id"])
        target = int(edge["target_node_id"])
        if source not in positions or target not in positions:
            continue
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_id = int(edge["edge_id"])
        color = "#2563eb" if edge_id in evidence_edge_ids else "#9ca3af"
        width = 2.2 if edge_id in evidence_edge_ids else 1.0
        axis.plot([x0, x1], [y0, y1], color=color, linewidth=width, zorder=1)
        flux = _signed_flux(edge)
        if abs(flux) > 1e-12:
            arrow_color = "#0f766e" if flux > 0 else "#b91c1c"
            axis.annotate(
                "",
                xy=(x0 * 0.45 + x1 * 0.55, y0 * 0.45 + y1 * 0.55),
                xytext=(x0 * 0.55 + x1 * 0.45, y0 * 0.55 + y1 * 0.45),
                arrowprops={"arrowstyle": "->", "color": arrow_color, "lw": 1.4},
                zorder=2,
            )
            axis.text(
                (x0 + x1) / 2.0,
                (y0 + y1) / 2.0,
                f"{flux:.2g}",
                fontsize=7,
                color=arrow_color,
                ha="center",
                va="bottom",
            )
    for node_id in sorted(positions):
        x, y = positions[node_id]
        present = node_id in present_ids
        face = _node_face(node_id, present=present)
        edge_color, line_width, marker = _node_motion_style(
            node_id,
            old_ids=old_ids,
            new_ids=new_ids,
            topological_born_ids=topological_born_ids,
            topological_removed_ids=topological_removed_ids,
            topological_evidence_ids=topological_evidence_ids,
        )
        if present:
            axis.scatter(
                [x],
                [y],
                s=580,
                marker=marker,
                c=face,
                edgecolors=edge_color,
                linewidths=line_width,
                zorder=3,
            )
            label = _node_label(node_by_id[node_id])
        else:
            axis.scatter(
                [x],
                [y],
                s=420,
                marker="x",
                c="#cbd5e1",
                linewidths=1.8,
                zorder=2,
            )
            label = f"{node_id}\nabsent"
        axis.text(x, y, label, ha="center", va="center", fontsize=8, zorder=4)
    axis.set_aspect("equal")
    axis.axis("off")


def _node_face(node_id: int, *, present: bool) -> str:
    del node_id
    return "#f8fafc" if present else "#f3f4f6"


def _node_motion_style(
    node_id: int,
    *,
    old_ids: set[int],
    new_ids: set[int],
    topological_born_ids: set[int],
    topological_removed_ids: set[int],
    topological_evidence_ids: set[int],
) -> tuple[str, float, str]:
    if node_id in topological_born_ids:
        return ("#059669", 3.4, "s")
    if node_id in topological_removed_ids:
        return ("#dc2626", 3.4, "X")
    if node_id in topological_evidence_ids:
        return ("#0891b2", 2.8, "D")
    if node_id in old_ids and node_id in new_ids:
        return ("#7c3aed", 3.0, "o")
    if node_id in old_ids:
        return ("#f97316", 3.0, "o")
    if node_id in new_ids:
        return ("#16a34a", 3.0, "o")
    return ("#64748b", 1.2, "o")


def _node_label(node: Mapping[str, Any]) -> str:
    label = str(node["node_id"])
    basin = node.get("basin_id")
    if basin is not None:
        label = f"{label}\n{basin}"
    coherence = _optional_float(node.get("coherence"))
    if coherence is not None:
        label = f"{label}\nC={coherence:.2g}"
    return label


def _draw_record_panel(axis: Any, motion_records: tuple[Mapping[str, Any], ...]) -> None:
    axis.axis("off")
    lines = [
        "Observed motion records",
        "",
        "Visual boundary: records are rendered, not created here.",
        "",
    ]
    if not motion_records:
        lines.append("No motion records in selected reports.")
    for record in motion_records[:11]:
        transferred_mass = record.get("transferred_mass")
        mass_text = ""
        if isinstance(transferred_mass, int | float):
            mass_text = f", mass={float(transferred_mass):.3g}"
        lines.append(
            f"- {record.get('motion_id')} [{record.get('motion_kind')}] "
            f"{record.get('relationship')} c={float(record.get('confidence', 0.0)):.2f}{mass_text}"
        )
        evidence = record.get("evidence", {})
        if isinstance(evidence, Mapping):
            checkpoints = evidence.get("checkpoint_ids", ())
            nodes = evidence.get("node_ids", ())
            if checkpoints or nodes:
                lines.append(f"  checkpoints={list(checkpoints)} nodes={list(nodes)}")
    if len(motion_records) > 11:
        lines.append(f"... {len(motion_records) - 11} additional records omitted from panel")
    axis.text(
        0.0,
        1.0,
        "\n".join(lines),
        ha="left",
        va="top",
        fontsize=8,
        family="monospace",
        transform=axis.transAxes,
    )


def _render_motion_animation_frames(
    *,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
    motion_records: tuple[Mapping[str, Any], ...],
    positions: Mapping[int, tuple[float, float]],
    output_dir: Path,
    title: str,
) -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for checkpoint in checkpoints:
        active_records = _records_active_at_step(motion_records, checkpoint.step_index)
        recent_records = _records_recent_at_step(motion_records, checkpoint.step_index)
        path = output_dir / f"frame_{checkpoint.step_index:04d}_{checkpoint.checkpoint_id}.png"
        figure, axes = plt.subplots(1, 2, figsize=(11, 5), gridspec_kw={"width_ratios": [1.25, 1.0]})
        _draw_checkpoint_panel(
            axes[0],
            checkpoint,
            positions=positions,
            old_ids=_carrier_node_ids(active_records, "old_carriers"),
            new_ids=_carrier_node_ids(active_records, "new_carriers"),
            topological_born_ids=_topological_node_ids(active_records, "new_carriers"),
            topological_removed_ids=_topological_node_ids(active_records, "old_carriers"),
            topological_evidence_ids=_topological_evidence_node_ids(active_records),
            evidence_edge_ids=_evidence_edge_ids(active_records),
            panel_title=f"frame {checkpoint.step_index}",
        )
        _draw_animation_record_panel(
            axes[1],
            active_records=active_records,
            recent_records=recent_records,
            checkpoint=checkpoint,
        )
        figure.suptitle(f"Motion animation: {title}", fontsize=13)
        figure.tight_layout()
        figure.savefig(path, dpi=120)
        plt.close(figure)
        paths.append(path)
    return tuple(paths)


def _draw_animation_record_panel(
    axis: Any,
    *,
    active_records: tuple[Mapping[str, Any], ...],
    recent_records: tuple[Mapping[str, Any], ...],
    checkpoint: GraphCheckpointArtifact,
) -> None:
    axis.axis("off")
    lines = [
        f"checkpoint={checkpoint.checkpoint_id}",
        f"step={checkpoint.step_index} t={checkpoint.time:.3f}",
        "",
        "Active motion records",
        "",
    ]
    if not active_records:
        lines.append("none")
    for record in active_records[:8]:
        lines.append(
            f"- {record.get('motion_kind')} {record.get('relationship')} "
            f"{record.get('motion_id')}"
        )
    if len(active_records) > 8:
        lines.append(f"... {len(active_records) - 8} more active records")
    lines.extend(["", "Recent / stationary context", ""])
    if not recent_records:
        lines.append("none")
    for record in recent_records[:6]:
        lines.append(
            f"- {record.get('motion_kind')} {record.get('relationship')} "
            f"{record.get('motion_id')}"
        )
    if len(recent_records) > 6:
        lines.append(f"... {len(recent_records) - 6} more recent records")
    lines.extend(["", "Visual boundary: no visual-only promotion."])
    axis.text(
        0.0,
        1.0,
        "\n".join(lines),
        ha="left",
        va="top",
        fontsize=8,
        family="monospace",
        transform=axis.transAxes,
    )


def _records_active_at_step(
    motion_records: tuple[Mapping[str, Any], ...],
    step_index: int,
) -> tuple[Mapping[str, Any], ...]:
    active: list[Mapping[str, Any]] = []
    for record in motion_records:
        start, end = _record_step_window(record)
        if start <= step_index <= end and record.get("relationship") != "stationary":
            active.append(record)
    return tuple(active)


def _records_recent_at_step(
    motion_records: tuple[Mapping[str, Any], ...],
    step_index: int,
) -> tuple[Mapping[str, Any], ...]:
    recent: list[Mapping[str, Any]] = []
    for record in motion_records:
        start, end = _record_step_window(record)
        if start <= step_index <= end:
            recent.append(record)
    return tuple(recent)


def _record_step_window(record: Mapping[str, Any]) -> tuple[int, int]:
    step_window = record.get("step_window", (0, 0))
    if isinstance(step_window, Sequence) and not isinstance(step_window, str | bytes) and len(step_window) == 2:
        try:
            return (int(step_window[0]), int(step_window[1]))
        except (TypeError, ValueError):
            return (0, 0)
    return (0, 0)


def _render_motion_sequence_from_frames(
    frame_paths: Sequence[Path],
    *,
    output_path: Path,
    title: str,
) -> None:
    if not frame_paths:
        raise ValueError("motion sequence requires at least one rendered frame")
    selected_indices = _sample_frame_indices(len(frame_paths), max_panels=6)
    selected_paths = [frame_paths[index] for index in selected_indices]
    images: list[Image.Image] = []
    try:
        for path in selected_paths:
            images.append(Image.open(path).convert("RGB"))
        ncols = min(3, len(images))
        nrows = int(math.ceil(len(images) / ncols))
        width, height = images[0].size
        figure, axes = plt.subplots(nrows, ncols, figsize=(5.0 * ncols, 3.2 * nrows))
        axis_list = list(axes.flat) if hasattr(axes, "flat") else [axes]
        for axis, image, frame_index in zip(axis_list, images, selected_indices, strict=False):
            axis.imshow(image)
            axis.set_title(f"frame {frame_index}", fontsize=9)
            axis.axis("off")
        for axis in axis_list[len(images) :]:
            axis.axis("off")
        figure.suptitle(f"Motion frame sequence: {title}", fontsize=13)
        figure.tight_layout()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(output_path, dpi=120)
        plt.close(figure)
        del width, height
    finally:
        for image in images:
            image.close()


def _sample_frame_indices(count: int, *, max_panels: int) -> list[int]:
    if count <= max_panels:
        return list(range(count))
    indices: list[int] = []
    for index in range(max_panels):
        value = round(index * (count - 1) / (max_panels - 1))
        if not indices or value != indices[-1]:
            indices.append(int(value))
    while len(indices) < max_panels:
        indices.append(count - 1)
    return indices


def _render_gif(frame_paths: Sequence[Path], *, output_path: Path) -> None:
    if not frame_paths:
        raise ValueError("motion animation requires at least one frame")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    images: list[Image.Image] = []
    try:
        for path in frame_paths:
            with Image.open(path) as raw_image:
                images.append(raw_image.convert("P", palette=Image.ADAPTIVE))
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=420,
            loop=0,
            optimize=False,
            disposal=2,
        )
    finally:
        for image in images:
            image.close()


def _render_motion_timeline(
    *,
    motion_records: tuple[Mapping[str, Any], ...],
    output_path: Path,
    title: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plotted_records = _records_for_timeline(motion_records)
    figure, axis = plt.subplots(
        figsize=(10, min(18.0, max(3.0, 0.33 * max(1, len(plotted_records)) + 1.0)))
    )
    if plotted_records:
        for index, record in enumerate(plotted_records):
            step_window = record.get("step_window", (0, 0))
            if not isinstance(step_window, Sequence) or len(step_window) != 2:
                step_window = (0, 0)
            start = int(step_window[0])
            end = int(step_window[1])
            color = _relationship_color(str(record.get("relationship", "ambiguous")))
            axis.plot([start, end], [index, index], color=color, linewidth=5, solid_capstyle="round")
            axis.scatter([start, end], [index, index], color=color, s=36)
            axis.text(
                end + 0.03,
                index,
                f"{record.get('motion_id')} {record.get('relationship')}",
                va="center",
                fontsize=8,
            )
        axis.set_ylim(-0.8, len(plotted_records) - 0.2)
        if len(plotted_records) < len(motion_records):
            axis.text(
                0.01,
                0.01,
                f"showing {len(plotted_records)} of {len(motion_records)} records; "
                "dense timeline sampled by confidence and time",
                ha="left",
                va="bottom",
                fontsize=8,
                transform=axis.transAxes,
                color="#475569",
            )
    else:
        axis.text(0.5, 0.5, "No motion records", ha="center", va="center", transform=axis.transAxes)
        axis.set_ylim(-1, 1)
    axis.set_xlabel("step")
    axis.set_ylabel("motion record")
    axis.set_yticks([])
    axis.set_title(f"Motion record timeline: {title}", fontsize=12)
    axis.grid(axis="x", color="#e5e7eb")
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def _records_for_timeline(
    motion_records: tuple[Mapping[str, Any], ...],
) -> tuple[Mapping[str, Any], ...]:
    if len(motion_records) <= _MAX_TIMELINE_RECORDS:
        return motion_records
    non_stationary = [record for record in motion_records if record.get("relationship") != "stationary"]
    source = non_stationary if len(non_stationary) >= _MAX_TIMELINE_RECORDS else list(motion_records)
    ranked = sorted(
        enumerate(source),
        key=lambda item: (
            -float(item[1].get("confidence", 0.0) or 0.0),
            _record_step_window(item[1]),
            item[0],
        ),
    )
    selected = {index for index, _ in ranked[:_MAX_TIMELINE_RECORDS]}
    return tuple(record for index, record in enumerate(source) if index in selected)


def _relationship_color(relationship: str) -> str:
    return {
        "stationary": "#64748b",
        "drifted": "#2563eb",
        "walked": "#16a34a",
        "split": "#9333ea",
        "merged": "#0f766e",
        "collapsed": "#dc2626",
        "dissolved": "#f97316",
        "emerged": "#22c55e",
        "ambiguous": "#a16207",
    }.get(relationship, "#64748b")


def _visual_summary(
    record: MotionVisualRecord,
    *,
    pack: TelemetryArtifactPack,
    motion_records: tuple[Mapping[str, Any], ...],
    report_paths: tuple[Path, ...],
) -> dict[str, Any]:
    relationships = sorted(
        {
            str(item.get("relationship"))
            for item in motion_records
            if isinstance(item.get("relationship"), str)
        }
    )
    motion_kinds = sorted(
        {
            str(item.get("motion_kind"))
            for item in motion_records
            if isinstance(item.get("motion_kind"), str)
        }
    )
    non_stationary_motion_ids = tuple(
        str(item.get("motion_id"))
        for item in motion_records
        if isinstance(item.get("motion_id"), str) and item.get("relationship") != "stationary"
    )
    return canonicalize_json_value(
        {
            **record.to_mapping(),
            "visual_claims": "none",
            "no_visual_only_promotion": True,
            "source_telemetry": {
                "run_id": pack.run_summary.identity.run_id,
                "step_rows_path": str(pack.layout.step_rows_path),
                "event_rows_path": str(pack.layout.event_rows_path),
                "run_summary_path": str(pack.layout.run_summary_path),
                "graph_checkpoint_index_path": str(pack.layout.graph_checkpoint_index_path),
                "motion_report_paths": [str(path) for path in report_paths],
            },
            "motion_record_count": len(motion_records),
            "non_stationary_motion_record_ids": list(non_stationary_motion_ids),
            "motion_kinds": motion_kinds,
            "relationships": relationships,
            "motion_highlights": {
                "old_carrier_node_ids": sorted(_carrier_node_ids(motion_records, "old_carriers")),
                "new_carrier_node_ids": sorted(_carrier_node_ids(motion_records, "new_carriers")),
                "topological_born_node_ids": sorted(
                    _topological_node_ids(motion_records, "new_carriers")
                ),
                "topological_removed_node_ids": sorted(
                    _topological_node_ids(motion_records, "old_carriers")
                ),
                "topological_evidence_node_ids": sorted(
                    _topological_evidence_node_ids(motion_records)
                ),
            },
            "rendered_surfaces": {
                "graph_overlay": str(record.graph_path),
                "record_timeline": str(record.timeline_path),
                "static_two_checkpoint": True,
                "temporal_checkpoint_series_animation": "deferred_future_motion_visual_refinement",
                "graph_surface_modes": ["sparse_graph_overlay", "dense_record_panel"],
                "layout_policy": "chart_center_hint_when_available_else_deterministic_circle",
            },
            "checkpoint_linkage": {
                "checkpoint_ids": list(record.checkpoint_ids),
                "initial_checkpoint_id": record.checkpoint_ids[0] if record.checkpoint_ids else None,
                "final_checkpoint_id": record.checkpoint_ids[-1] if record.checkpoint_ids else None,
            },
            "motion_record_linkage": [
                {
                    "motion_id": item.get("motion_id"),
                    "motion_kind": item.get("motion_kind"),
                    "relationship": item.get("relationship"),
                    "checkpoint_ids": list(_record_checkpoint_ids(item)),
                    "step_ids": list(_record_step_ids(item)),
                }
                for item in motion_records
            ],
        }
    )


def _animated_visual_summary(
    record: MotionAnimatedVisualRecord,
    *,
    pack: TelemetryArtifactPack,
    motion_records: tuple[Mapping[str, Any], ...],
    frame_paths: tuple[Path, ...],
) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            **record.to_mapping(),
            "visual_claims": "none",
            "no_visual_only_promotion": True,
            "source_telemetry": {
                "run_id": pack.run_summary.identity.run_id,
                "step_rows_path": str(pack.layout.step_rows_path),
                "event_rows_path": str(pack.layout.event_rows_path),
                "run_summary_path": str(pack.layout.run_summary_path),
                "graph_checkpoint_index_path": str(pack.layout.graph_checkpoint_index_path),
            },
            "rendered_surfaces": {
                "graph_engine_sequence": str(record.graph_engine_sequence_path),
                "graph_engine_animation": str(record.graph_engine_animation_path),
                "graph_engine_final_html": str(record.graph_engine_dir / "graph_html" / "final_graph.html"),
                "motion_sequence": str(record.motion_sequence_path),
                "motion_animation": str(record.motion_animation_path),
                "motion_frames_dir": str(record.motion_frames_dir),
                "motion_frame_count": len(frame_paths),
                "static_two_checkpoint": str(record.visual_dir / MOTION_GRAPH_FILENAME),
                "layout_policy": "graph_render_union_layout_reused_for_motion_frames",
            },
            "frame_checkpoint_linkage": [
                {
                    "frame_path": str(frame_path),
                    "checkpoint_id": checkpoint_id,
                    "step_index": step_index,
                    "active_motion_record_ids": [
                        str(item.get("motion_id"))
                        for item in _records_active_at_step(motion_records, step_index)
                        if isinstance(item.get("motion_id"), str)
                    ],
                }
                for frame_path, checkpoint_id, step_index in zip(
                    frame_paths,
                    record.checkpoint_ids,
                    _checkpoint_step_indices(pack.graph_checkpoints),
                    strict=False,
                )
            ],
            "motion_record_linkage": [
                {
                    "motion_id": item.get("motion_id"),
                    "motion_kind": item.get("motion_kind"),
                    "relationship": item.get("relationship"),
                    "checkpoint_ids": list(_record_checkpoint_ids(item)),
                    "step_ids": list(_record_step_ids(item)),
                }
                for item in motion_records
            ],
            "recommended_use": (
                "static_visuals_for_record_inspection_animation_for_temporal_motion_review"
            ),
        }
    )


def _checkpoint_step_indices(
    checkpoints: Sequence[GraphCheckpointArtifact],
) -> tuple[int, ...]:
    return tuple(checkpoint.step_index for checkpoint in _sorted_checkpoints(checkpoints))


def _merge_static_summary_with_animation(
    summary_path: Path,
    animated_record: MotionAnimatedVisualRecord,
) -> None:
    if not summary_path.exists():
        return
    payload = dict(_read_json(summary_path))
    payload["animated_surfaces"] = {
        "animation_summary": str(animated_record.animated_summary_path),
        "motion_animation": str(animated_record.motion_animation_path),
        "motion_sequence": str(animated_record.motion_sequence_path),
        "graph_engine_animation": str(animated_record.graph_engine_animation_path),
        "graph_engine_sequence": str(animated_record.graph_engine_sequence_path),
        "frame_count": animated_record.frame_count,
    }
    payload["rendered_surfaces"] = dict(payload.get("rendered_surfaces", {}))
    payload["rendered_surfaces"]["temporal_checkpoint_series_animation"] = (
        "rendered_graph_engine_and_motion_overlay_animation"
    )
    _write_json(summary_path, payload)


def _review_report(session: MotionVisualReviewSession) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "visualization_version": MOTION_VISUALIZATION_VERSION,
            "source_session_root": str(session.session_root),
            "visual_count": len(session.records),
            "rendered_examples": [record.example_name for record in session.records],
            "claim_boundary": _CLAIM_BOUNDARY,
            "static_two_checkpoint_rendering": True,
            "temporal_checkpoint_series_rendering": "deferred",
            "visuals_create_new_motion_claims": False,
        }
    )


def _animated_review_report(session: MotionAnimatedVisualReviewSession) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "visualization_version": MOTION_ANIMATED_VISUALIZATION_VERSION,
            "source_session_root": str(session.session_root),
            "animated_visual_count": len(session.records),
            "rendered_examples": [record.example_name for record in session.records],
            "claim_boundary": _CLAIM_BOUNDARY,
            "graph_engine_sequence_rendering": True,
            "graph_engine_animation_rendering": True,
            "motion_overlay_animation_rendering": True,
            "visuals_create_new_motion_claims": False,
        }
    )


def _readme(session: MotionVisualReviewSession) -> str:
    lines = [
        "# Motion Visualization Review",
        "",
        f"- visualization version: `{MOTION_VISUALIZATION_VERSION}`",
        f"- source session: `{session.session_root}`",
        f"- rendered examples: `{len(session.records)}`",
        "",
        "Visuals are supporting evidence only. Motion claims come from the",
        "motion reports stored next to each telemetry run.",
        "",
        "Temporal animation is explicitly deferred; this pass renders a stable",
        "two-checkpoint comparison plus a record timeline for each example.",
        "",
        "## Examples",
        "",
    ]
    lines.extend(
        f"- `{record.example_name}`: `{record.graph_path.name}`, `{record.timeline_path.name}`"
        for record in session.records
    )
    lines.append("")
    return "\n".join(lines)


def _animated_readme(session: MotionAnimatedVisualReviewSession) -> str:
    lines = [
        "# Motion Animated Visualization Review",
        "",
        f"- visualization version: `{MOTION_ANIMATED_VISUALIZATION_VERSION}`",
        f"- source session: `{session.session_root}`",
        f"- rendered animated examples: `{len(session.records)}`",
        "",
        "Animations are supporting evidence only. Motion claims come from the",
        "motion reports stored next to each telemetry run.",
        "",
        "Each example includes graph-engine sequence/GIF outputs plus",
        "motion-overlay frames, a motion sequence sheet, and a motion GIF.",
        "",
        "## Examples",
        "",
    ]
    lines.extend(
        f"- `{record.example_name}`: `{record.motion_animation_path.name}`, "
        f"`{record.motion_sequence_path.name}`, frames=`{record.frame_count}`"
        for record in session.records
    )
    lines.append("")
    return "\n".join(lines)


def _carrier_node_ids(
    records: tuple[Mapping[str, Any], ...],
    carrier_key: str,
) -> set[int]:
    ids: set[int] = set()
    for record in records:
        if record.get("relationship") == "stationary":
            continue
        carriers = record.get(carrier_key)
        if not isinstance(carriers, Mapping):
            continue
        for node_id in carriers.get("node_ids", ()):
            try:
                ids.add(int(node_id))
            except (TypeError, ValueError):
                continue
    return ids


def _topological_node_ids(
    records: tuple[Mapping[str, Any], ...],
    carrier_key: str,
) -> set[int]:
    ids: set[int] = set()
    for record in records:
        if record.get("motion_kind") != "topological":
            continue
        carriers = record.get(carrier_key)
        if not isinstance(carriers, Mapping):
            continue
        for node_id in carriers.get("node_ids", ()):
            try:
                ids.add(int(node_id))
            except (TypeError, ValueError):
                continue
    return ids


def _topological_evidence_node_ids(records: tuple[Mapping[str, Any], ...]) -> set[int]:
    ids: set[int] = set()
    for record in records:
        if record.get("motion_kind") != "topological":
            continue
        evidence = record.get("evidence")
        if not isinstance(evidence, Mapping):
            continue
        for node_id in evidence.get("node_ids", ()):
            try:
                ids.add(int(node_id))
            except (TypeError, ValueError):
                continue
    return ids


def _evidence_edge_ids(records: tuple[Mapping[str, Any], ...]) -> set[int]:
    ids: set[int] = set()
    for record in records:
        evidence = record.get("evidence")
        if not isinstance(evidence, Mapping):
            continue
        for edge_id in evidence.get("edge_ids", ()):
            try:
                ids.add(int(edge_id))
            except (TypeError, ValueError):
                continue
    return ids


def _record_checkpoint_ids(record: Mapping[str, Any]) -> tuple[str, ...]:
    evidence = record.get("evidence")
    if not isinstance(evidence, Mapping):
        return ()
    return tuple(str(item) for item in evidence.get("checkpoint_ids", ()))


def _record_step_ids(record: Mapping[str, Any]) -> tuple[int, ...]:
    evidence = record.get("evidence")
    if not isinstance(evidence, Mapping):
        return ()
    step_ids: list[int] = []
    for step_id in evidence.get("step_ids", ()):
        try:
            step_ids.append(int(step_id))
        except (TypeError, ValueError):
            continue
    return tuple(step_ids)


def _signed_flux(edge: Mapping[str, Any]) -> float:
    for key in (
        "signed_flux",
        "signed_flux_source",
        "signed_flux_source_to_target",
        "flux_uv",
    ):
        value = _optional_float(edge.get(key))
        if value is not None:
            return value
    payload = _payload(edge)
    value = _optional_float(payload.get("signed_flux"))
    return 0.0 if value is None else value


def _optional_float(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _payload(record: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = record.get("payload")
    return payload if isinstance(payload, Mapping) else {}


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload), encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--session-root",
        default=str(DEFAULT_MOTION_VISUALIZATION_SESSION_ROOT),
        help="Motion example session root, e.g. outputs/motion/sessions/S0001.",
    )
    parser.add_argument(
        "--example",
        action="append",
        default=None,
        help="Example name to render. Can be supplied multiple times.",
    )
    parser.add_argument(
        "--animated",
        action="store_true",
        help="Render Iteration 12 graph-engine sequence and motion animations.",
    )
    parser.add_argument(
        "--no-static",
        action="store_true",
        help="With --animated, skip regenerating Iteration 9 static visuals.",
    )
    args = parser.parse_args(argv)
    if args.animated:
        animated_session = render_motion_animated_visual_session(
            session_root=args.session_root,
            example_names=args.example,
            render_static=not args.no_static,
        )
        print(
            f"Rendered {len(animated_session.records)} animated motion visual examples "
            f"at {animated_session.visual_root}"
        )
        return 0
    session = render_motion_visual_session(session_root=args.session_root, example_names=args.example)
    print(f"Rendered {len(session.records)} motion visual examples at {session.visual_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
