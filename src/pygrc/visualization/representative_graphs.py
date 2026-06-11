"""Representative graph-facing visualization entrypoints."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pygrc.telemetry import (
    DEFAULT_GRC9_LANDSCAPE_EXPERIMENT_PATH,
    DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
    DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
    DEFAULT_GRC9_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH,
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_GRCV3_REPRESENTATIVE_LANE,
    DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_REPRESENTATIVE_FAMILY,
    DEFAULT_TELEMETRY_ROOT,
    TelemetryArtifactLayout,
    build_telemetry_artifact_layout,
    load_telemetry_artifact_pack,
)

from .graph_render import (
    render_graph_comparison_visual_bundle,
    render_graph_run_visual_bundle,
)
from .layout import (
    GraphComparisonVisualizationLayout,
    GraphRunVisualizationLayout,
    build_graph_comparison_visualization_layout,
    build_graph_run_visualization_layout,
)


DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH: Final[Path] = (
    Path("phase-t-grc9v3") / "representative"
)
DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME: Final[str] = "appendix_e_cell_division"
_REQUIRED_GRC9V3_CHECKPOINT_OVERLAYS: Final[tuple[str, ...]] = (
    "node_overlay",
    "port_overlay",
    "edge_overlay",
    "module_overlay",
    "choice_overlay",
)


@dataclass(frozen=True)
class RepresentativeGraphVisualizationResult:
    """Saved graph-facing outputs for the canonical representative run lane."""

    cell1_telemetry_layout: TelemetryArtifactLayout
    cell4_telemetry_layout: TelemetryArtifactLayout
    cell1_graph_visualization_layout: GraphRunVisualizationLayout
    cell4_graph_visualization_layout: GraphRunVisualizationLayout
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout


@dataclass(frozen=True)
class GRCV3RepresentativeGraphVisualizationResult:
    """Saved graph-facing outputs for the representative GRCV3 replay lane."""

    primary_telemetry_layout: TelemetryArtifactLayout
    replay_telemetry_layout: TelemetryArtifactLayout
    primary_graph_visualization_layout: GraphRunVisualizationLayout
    replay_graph_visualization_layout: GraphRunVisualizationLayout
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout


@dataclass(frozen=True)
class GRC9RepresentativeGraphVisualizationResult:
    """Saved graph-facing outputs for the representative GRC9 replay lane."""

    primary_telemetry_layout: TelemetryArtifactLayout
    replay_telemetry_layout: TelemetryArtifactLayout
    primary_graph_visualization_layout: GraphRunVisualizationLayout
    replay_graph_visualization_layout: GraphRunVisualizationLayout
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout


@dataclass(frozen=True)
class GRC9LandscapeGraphVisualizationResult:
    """Saved graph-facing outputs for the seed-driven GRC9 cell pair lane."""

    cell1_telemetry_layout: TelemetryArtifactLayout
    cell4_telemetry_layout: TelemetryArtifactLayout
    cell1_graph_visualization_layout: GraphRunVisualizationLayout
    cell4_graph_visualization_layout: GraphRunVisualizationLayout
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout


@dataclass(frozen=True)
class GRC9V3RepresentativeGraphVisualizationResult:
    """Saved graph-facing outputs for the representative GRC9V3 fixture lane."""

    telemetry_layout: TelemetryArtifactLayout
    graph_visualization_layout: GraphRunVisualizationLayout


@dataclass(frozen=True)
class GRCV3LandscapeGraphVisualizationResult:
    """Saved graph-facing outputs for the seed-driven GRCV3 cell pair lane."""

    cell1_telemetry_layout: TelemetryArtifactLayout
    cell4_telemetry_layout: TelemetryArtifactLayout
    cell1_graph_visualization_layout: GraphRunVisualizationLayout
    cell4_graph_visualization_layout: GraphRunVisualizationLayout
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout


def render_grc9v3_representative_graph_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    fixture_name: str = DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME,
    artifact_path: str | Path | None = None,
) -> GRC9V3RepresentativeGraphVisualizationResult:
    """Render checkpoint-backed graph visuals for the representative GRC9V3 lane."""

    if artifact_path is None:
        fixture_root = Path(telemetry_root) / Path(telemetry_experiment_path) / fixture_name
        telemetry_layout = _discover_latest_run_layout(fixture_root)
    else:
        telemetry_layout = _layout_from_artifact_path(Path(artifact_path))
    pack = load_telemetry_artifact_pack(telemetry_layout)
    if not pack.graph_checkpoints:
        raise ValueError(
            "GRC9V3 representative graph visualization requires saved graph "
            "checkpoints; rerun the representative telemetry lane with checkpoint "
            "capture enabled"
        )
    _require_grc9v3_checkpoint_overlays(pack.graph_checkpoints)

    graph_layout = build_graph_run_visualization_layout(
        telemetry_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / fixture_name
        ),
    )

    render_graph_run_visual_bundle(pack, layout=graph_layout)

    return GRC9V3RepresentativeGraphVisualizationResult(
        telemetry_layout=telemetry_layout,
        graph_visualization_layout=graph_layout,
    )


def render_grcv2_representative_graph_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    family_name: str = DEFAULT_REPRESENTATIVE_FAMILY,
) -> RepresentativeGraphVisualizationResult:
    """Render checkpoint-backed graph visuals for the representative GRCV2 lane."""

    family_root = Path(telemetry_root) / Path(telemetry_experiment_path) / family_name
    cell1_layout = _discover_single_run_layout(family_root / "cell-1")
    cell4_layout = _discover_single_run_layout(family_root / "cell-4")
    cell1_pack = load_telemetry_artifact_pack(cell1_layout)
    cell4_pack = load_telemetry_artifact_pack(cell4_layout)
    if not cell1_pack.graph_checkpoints or not cell4_pack.graph_checkpoints:
        raise ValueError(
            "representative graph visualization requires saved graph checkpoints for both "
            "cell-1 and cell-4; rerun the representative experiment with "
            "record_graph_checkpoints=True"
        )

    cell1_graph_layout = build_graph_run_visualization_layout(
        cell1_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / family_name / "cell-1"
        ),
    )
    cell4_graph_layout = build_graph_run_visualization_layout(
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / family_name / "cell-4"
        ),
    )
    graph_comparison_layout = build_graph_comparison_visualization_layout(
        cell1_layout,
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / family_name
        ),
    )

    render_graph_run_visual_bundle(cell1_pack, layout=cell1_graph_layout)
    render_graph_run_visual_bundle(cell4_pack, layout=cell4_graph_layout)
    render_graph_comparison_visual_bundle(
        cell1_pack,
        cell4_pack,
        layout=graph_comparison_layout,
    )

    return RepresentativeGraphVisualizationResult(
        cell1_telemetry_layout=cell1_layout,
        cell4_telemetry_layout=cell4_layout,
        cell1_graph_visualization_layout=cell1_graph_layout,
        cell4_graph_visualization_layout=cell4_graph_layout,
        graph_comparison_visualization_layout=graph_comparison_layout,
    )


def render_grc9_landscape_graph_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRC9_LANDSCAPE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    profile_name: str = DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
) -> GRC9LandscapeGraphVisualizationResult:
    """Render checkpoint-backed graph visuals for the seed-driven GRC9 lane."""

    family_root = Path(telemetry_root) / Path(telemetry_experiment_path) / profile_name
    cell1_layout = _discover_single_run_layout(family_root / "cell-1")
    cell4_layout = _discover_single_run_layout(family_root / "cell-4")
    cell1_pack = load_telemetry_artifact_pack(cell1_layout)
    cell4_pack = load_telemetry_artifact_pack(cell4_layout)
    if not cell1_pack.graph_checkpoints or not cell4_pack.graph_checkpoints:
        raise ValueError(
            "GRC9 landscape graph visualization requires saved graph "
            "checkpoints for both cell-1 and cell-4; rerun the landscape "
            "experiment with record_graph_checkpoints=True"
        )

    cell1_graph_layout = build_graph_run_visualization_layout(
        cell1_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name / "cell-1"
        ),
    )
    cell4_graph_layout = build_graph_run_visualization_layout(
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name / "cell-4"
        ),
    )
    graph_comparison_layout = build_graph_comparison_visualization_layout(
        cell1_layout,
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name
        ),
    )

    render_graph_run_visual_bundle(cell1_pack, layout=cell1_graph_layout)
    render_graph_run_visual_bundle(cell4_pack, layout=cell4_graph_layout)
    render_graph_comparison_visual_bundle(
        cell1_pack,
        cell4_pack,
        layout=graph_comparison_layout,
    )

    return GRC9LandscapeGraphVisualizationResult(
        cell1_telemetry_layout=cell1_layout,
        cell4_telemetry_layout=cell4_layout,
        cell1_graph_visualization_layout=cell1_graph_layout,
        cell4_graph_visualization_layout=cell4_graph_layout,
        graph_comparison_visualization_layout=graph_comparison_layout,
    )


def render_grc9_representative_graph_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRC9_REPRESENTATIVE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    lane_name: str = DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
) -> GRC9RepresentativeGraphVisualizationResult:
    """Render checkpoint-backed graph visuals for the representative GRC9 lane."""

    lane_root = Path(telemetry_root) / Path(telemetry_experiment_path) / lane_name
    primary_layout = _discover_single_run_layout(lane_root / "primary")
    replay_layout = _discover_single_run_layout(lane_root / "replay")
    primary_pack = load_telemetry_artifact_pack(primary_layout)
    replay_pack = load_telemetry_artifact_pack(replay_layout)
    if not primary_pack.graph_checkpoints or not replay_pack.graph_checkpoints:
        raise ValueError(
            "GRC9 representative graph visualization requires saved graph "
            "checkpoints for both primary and replay; rerun the representative "
            "experiment with record_graph_checkpoints=True"
        )

    primary_graph_layout = build_graph_run_visualization_layout(
        primary_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name / "primary"
        ),
    )
    replay_graph_layout = build_graph_run_visualization_layout(
        replay_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name / "replay"
        ),
    )
    graph_comparison_layout = build_graph_comparison_visualization_layout(
        primary_layout,
        replay_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name
        ),
    )

    render_graph_run_visual_bundle(primary_pack, layout=primary_graph_layout)
    render_graph_run_visual_bundle(replay_pack, layout=replay_graph_layout)
    render_graph_comparison_visual_bundle(
        primary_pack,
        replay_pack,
        layout=graph_comparison_layout,
    )

    return GRC9RepresentativeGraphVisualizationResult(
        primary_telemetry_layout=primary_layout,
        replay_telemetry_layout=replay_layout,
        primary_graph_visualization_layout=primary_graph_layout,
        replay_graph_visualization_layout=replay_graph_layout,
        graph_comparison_visualization_layout=graph_comparison_layout,
    )


def render_grcv3_representative_graph_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    lane_name: str = DEFAULT_GRCV3_REPRESENTATIVE_LANE,
) -> GRCV3RepresentativeGraphVisualizationResult:
    """Render checkpoint-backed graph visuals for the representative GRCV3 lane."""

    lane_root = Path(telemetry_root) / Path(telemetry_experiment_path) / lane_name
    primary_layout = _discover_single_run_layout(lane_root / "primary")
    replay_layout = _discover_single_run_layout(lane_root / "replay")
    primary_pack = load_telemetry_artifact_pack(primary_layout)
    replay_pack = load_telemetry_artifact_pack(replay_layout)
    if not primary_pack.graph_checkpoints or not replay_pack.graph_checkpoints:
        raise ValueError(
            "GRCV3 representative graph visualization requires saved graph "
            "checkpoints for both primary and replay; rerun the representative "
            "experiment with record_graph_checkpoints=True"
        )

    primary_graph_layout = build_graph_run_visualization_layout(
        primary_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name / "primary"
        ),
    )
    replay_graph_layout = build_graph_run_visualization_layout(
        replay_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name / "replay"
        ),
    )
    graph_comparison_layout = build_graph_comparison_visualization_layout(
        primary_layout,
        replay_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name
        ),
    )

    render_graph_run_visual_bundle(primary_pack, layout=primary_graph_layout)
    render_graph_run_visual_bundle(replay_pack, layout=replay_graph_layout)
    render_graph_comparison_visual_bundle(
        primary_pack,
        replay_pack,
        layout=graph_comparison_layout,
    )

    return GRCV3RepresentativeGraphVisualizationResult(
        primary_telemetry_layout=primary_layout,
        replay_telemetry_layout=replay_layout,
        primary_graph_visualization_layout=primary_graph_layout,
        replay_graph_visualization_layout=replay_graph_layout,
        graph_comparison_visualization_layout=graph_comparison_layout,
    )


def render_grcv3_landscape_graph_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
) -> GRCV3LandscapeGraphVisualizationResult:
    """Render checkpoint-backed graph visuals for the seed-driven GRCV3 lane."""

    family_root = Path(telemetry_root) / Path(telemetry_experiment_path) / profile_name
    cell1_layout = _discover_single_run_layout(family_root / "cell-1")
    cell4_layout = _discover_single_run_layout(family_root / "cell-4")
    cell1_pack = load_telemetry_artifact_pack(cell1_layout)
    cell4_pack = load_telemetry_artifact_pack(cell4_layout)
    if not cell1_pack.graph_checkpoints or not cell4_pack.graph_checkpoints:
        raise ValueError(
            "GRCV3 landscape graph visualization requires saved graph "
            "checkpoints for both cell-1 and cell-4; rerun the landscape "
            "experiment with record_graph_checkpoints=True"
        )

    cell1_graph_layout = build_graph_run_visualization_layout(
        cell1_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name / "cell-1"
        ),
    )
    cell4_graph_layout = build_graph_run_visualization_layout(
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name / "cell-4"
        ),
    )
    graph_comparison_layout = build_graph_comparison_visualization_layout(
        cell1_layout,
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name
        ),
    )

    render_graph_run_visual_bundle(cell1_pack, layout=cell1_graph_layout)
    render_graph_run_visual_bundle(cell4_pack, layout=cell4_graph_layout)
    render_graph_comparison_visual_bundle(
        cell1_pack,
        cell4_pack,
        layout=graph_comparison_layout,
    )

    return GRCV3LandscapeGraphVisualizationResult(
        cell1_telemetry_layout=cell1_layout,
        cell4_telemetry_layout=cell4_layout,
        cell1_graph_visualization_layout=cell1_graph_layout,
        cell4_graph_visualization_layout=cell4_graph_layout,
        graph_comparison_visualization_layout=graph_comparison_layout,
    )


def _discover_single_run_layout(seed_root: Path) -> TelemetryArtifactLayout:
    run_dirs = sorted(path for path in seed_root.iterdir() if path.is_dir())
    if len(run_dirs) != 1:
        raise ValueError(
            f"expected exactly one representative run directory under {seed_root.as_posix()}; "
            f"found {len(run_dirs)}"
        )
    run_dir = run_dirs[0]
    return build_telemetry_artifact_layout(
        run_dir.name,
        root_dir=seed_root,
    )


def _discover_latest_run_layout(seed_root: Path) -> TelemetryArtifactLayout:
    if not seed_root.exists():
        raise ValueError(f"representative artifact root does not exist: {seed_root.as_posix()}")
    run_dirs = sorted(
        (path for path in seed_root.iterdir() if path.is_dir() and (path / "telemetry").is_dir()),
        key=lambda path: (path.stat().st_mtime_ns, path.name),
    )
    if not run_dirs:
        raise ValueError(
            f"expected at least one representative run directory under {seed_root.as_posix()}; "
            "found 0"
        )
    run_dir = run_dirs[-1]
    return build_telemetry_artifact_layout(run_dir.name, root_dir=seed_root)


def _layout_from_artifact_path(artifact_path: Path) -> TelemetryArtifactLayout:
    run_dir = artifact_path.parent if artifact_path.name == "telemetry" else artifact_path
    if not (run_dir / "telemetry").is_dir():
        raise ValueError(
            "artifact_path must point to a telemetry run directory or its telemetry subdirectory; "
            f"got {artifact_path.as_posix()}"
        )
    return build_telemetry_artifact_layout(run_dir.name, root_dir=run_dir.parent)


def _require_grc9v3_checkpoint_overlays(checkpoints: object) -> None:
    for checkpoint in checkpoints:
        grc9v3_payload = checkpoint.family_extensions.get("grc9v3")
        if not isinstance(grc9v3_payload, Mapping):
            raise ValueError(
                "GRC9V3 representative graph visualization requires grc9v3 "
                "checkpoint overlay family extensions"
            )
        if grc9v3_payload.get("overlay_status") != "enabled":
            raise ValueError(
                "GRC9V3 representative graph visualization requires enabled "
                "checkpoint overlays"
            )
        missing = [
            overlay_name
            for overlay_name in _REQUIRED_GRC9V3_CHECKPOINT_OVERLAYS
            if overlay_name not in grc9v3_payload
        ]
        if missing:
            raise ValueError(
                "GRC9V3 representative graph visualization requires checkpoint "
                f"overlays {', '.join(_REQUIRED_GRC9V3_CHECKPOINT_OVERLAYS)}; "
                f"missing {', '.join(missing)}"
            )


__all__ = [
    "DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME",
    "GRC9LandscapeGraphVisualizationResult",
    "GRC9RepresentativeGraphVisualizationResult",
    "GRC9V3RepresentativeGraphVisualizationResult",
    "GRCV3LandscapeGraphVisualizationResult",
    "GRCV3RepresentativeGraphVisualizationResult",
    "RepresentativeGraphVisualizationResult",
    "render_grc9_landscape_graph_suite",
    "render_grc9_representative_graph_suite",
    "render_grc9v3_representative_graph_suite",
    "render_grcv3_landscape_graph_suite",
    "render_grcv3_representative_graph_suite",
    "render_grcv2_representative_graph_suite",
]
