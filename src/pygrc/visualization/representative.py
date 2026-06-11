"""Representative artifact-driven visualization helpers."""

from __future__ import annotations

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
    TelemetryArtifactPack,
    TelemetryArtifactLayout,
    TelemetryExperimentReport,
    build_telemetry_artifact_layout,
    build_run_experiment_report,
    load_telemetry_artifact_pack,
)

from .layout import (
    ComparisonVisualizationLayout,
    GraphComparisonVisualizationLayout,
    GraphRunVisualizationLayout,
    RunVisualizationLayout,
    build_comparison_visualization_layout,
    build_run_visualization_layout,
)
from .render import (
    DEFAULT_GRC9_COMPARISON_OBSERVABLES,
    DEFAULT_GRC9_RUN_OBSERVABLES,
    DEFAULT_GRC9V3_RUN_OBSERVABLES,
    DEFAULT_GRCV3_COMPARISON_OBSERVABLES,
    DEFAULT_GRCV3_RUN_OBSERVABLES,
    _grc9v3_event_lane_summary,
    render_comparison_visual_bundle,
    render_run_visual_bundle,
)
from .representative_graphs import (
    DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME,
    GRC9LandscapeGraphVisualizationResult,
    GRC9RepresentativeGraphVisualizationResult,
    GRC9V3RepresentativeGraphVisualizationResult,
    GRCV3LandscapeGraphVisualizationResult,
    GRCV3RepresentativeGraphVisualizationResult,
    RepresentativeGraphVisualizationResult,
    render_grc9_landscape_graph_suite,
    render_grc9_representative_graph_suite,
    render_grc9v3_representative_graph_suite,
    render_grcv3_landscape_graph_suite,
    render_grcv3_representative_graph_suite,
    render_grcv2_representative_graph_suite,
)

SURFACE_MODE_BEHAVIOR: Final[str] = "behavior"
SURFACE_MODE_GRAPH: Final[str] = "graph"
SURFACE_MODE_ALL: Final[str] = "all"
SUPPORTED_SURFACE_MODES: Final[tuple[str, ...]] = (
    SURFACE_MODE_BEHAVIOR,
    SURFACE_MODE_GRAPH,
    SURFACE_MODE_ALL,
)


@dataclass(frozen=True)
class RepresentativeVisualizationResult:
    """Saved visualization outputs for the canonical representative run lane."""

    surface_mode: str
    cell1_telemetry_layout: TelemetryArtifactLayout
    cell4_telemetry_layout: TelemetryArtifactLayout
    cell1_visualization_layout: RunVisualizationLayout
    cell4_visualization_layout: RunVisualizationLayout
    comparison_visualization_layout: ComparisonVisualizationLayout
    cell1_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    cell4_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout | None = None


@dataclass(frozen=True)
class GRCV3RepresentativeVisualizationResult:
    """Saved visualization outputs for the representative GRCV3 replay lane."""

    surface_mode: str
    primary_telemetry_layout: TelemetryArtifactLayout
    replay_telemetry_layout: TelemetryArtifactLayout
    primary_visualization_layout: RunVisualizationLayout
    replay_visualization_layout: RunVisualizationLayout
    comparison_visualization_layout: ComparisonVisualizationLayout
    primary_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    replay_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout | None = None


@dataclass(frozen=True)
class GRC9RepresentativeVisualizationResult:
    """Saved visualization outputs for the representative GRC9 replay lane."""

    surface_mode: str
    primary_telemetry_layout: TelemetryArtifactLayout
    replay_telemetry_layout: TelemetryArtifactLayout
    primary_visualization_layout: RunVisualizationLayout
    replay_visualization_layout: RunVisualizationLayout
    comparison_visualization_layout: ComparisonVisualizationLayout
    primary_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    replay_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout | None = None


@dataclass(frozen=True)
class GRC9LandscapeVisualizationResult:
    """Saved visualization outputs for the seed-driven GRC9 cell pair lane."""

    surface_mode: str
    cell1_telemetry_layout: TelemetryArtifactLayout
    cell4_telemetry_layout: TelemetryArtifactLayout
    cell1_visualization_layout: RunVisualizationLayout
    cell4_visualization_layout: RunVisualizationLayout
    comparison_visualization_layout: ComparisonVisualizationLayout
    cell1_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    cell4_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout | None = None


@dataclass(frozen=True)
class GRC9V3RepresentativeVisualizationResult:
    """Saved visualization outputs for the representative GRC9V3 fixture lane."""

    surface_mode: str
    fixture_name: str
    telemetry_layout: TelemetryArtifactLayout
    visualization_layout: RunVisualizationLayout
    graph_visualization_layout: GraphRunVisualizationLayout | None = None


@dataclass(frozen=True)
class GRCV3LandscapeVisualizationResult:
    """Saved visualization outputs for the seed-driven GRCV3 cell pair lane."""

    surface_mode: str
    cell1_telemetry_layout: TelemetryArtifactLayout
    cell4_telemetry_layout: TelemetryArtifactLayout
    cell1_visualization_layout: RunVisualizationLayout
    cell4_visualization_layout: RunVisualizationLayout
    comparison_visualization_layout: ComparisonVisualizationLayout
    cell1_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    cell4_graph_visualization_layout: GraphRunVisualizationLayout | None = None
    graph_comparison_visualization_layout: GraphComparisonVisualizationLayout | None = None


def render_grcv2_representative_visual_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    family_name: str = DEFAULT_REPRESENTATIVE_FAMILY,
    surface_mode: str = SURFACE_MODE_BEHAVIOR,
) -> RepresentativeVisualizationResult:
    """Render the requested representative visualization surface."""

    normalized_surface_mode = _normalize_surface_mode(surface_mode)

    family_root = Path(telemetry_root) / Path(telemetry_experiment_path) / family_name
    cell1_layout = _discover_single_run_layout(family_root / "cell-1")
    cell4_layout = _discover_single_run_layout(family_root / "cell-4")
    cell1_pack = load_telemetry_artifact_pack(cell1_layout)
    cell4_pack = load_telemetry_artifact_pack(cell4_layout)

    cell1_visual_layout = build_run_visualization_layout(
        cell1_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / family_name / "cell-1"
        ),
    )
    cell4_visual_layout = build_run_visualization_layout(
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / family_name / "cell-4"
        ),
    )
    comparison_visual_layout = build_comparison_visualization_layout(
        cell1_layout,
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / family_name
        ),
    )

    if normalized_surface_mode in (SURFACE_MODE_BEHAVIOR, SURFACE_MODE_ALL):
        render_run_visual_bundle(cell1_pack, layout=cell1_visual_layout)
        render_run_visual_bundle(cell4_pack, layout=cell4_visual_layout)
        render_comparison_visual_bundle(
            cell1_pack,
            cell4_pack,
            layout=comparison_visual_layout,
        )

    graph_result: RepresentativeGraphVisualizationResult | None = None
    if normalized_surface_mode in (SURFACE_MODE_GRAPH, SURFACE_MODE_ALL):
        graph_result = render_grcv2_representative_graph_suite(
            telemetry_root=telemetry_root,
            telemetry_experiment_path=telemetry_experiment_path,
            visualization_root=visualization_root,
            family_name=family_name,
        )

    return RepresentativeVisualizationResult(
        surface_mode=normalized_surface_mode,
        cell1_telemetry_layout=cell1_layout,
        cell4_telemetry_layout=cell4_layout,
        cell1_visualization_layout=cell1_visual_layout,
        cell4_visualization_layout=cell4_visual_layout,
        comparison_visualization_layout=comparison_visual_layout,
        cell1_graph_visualization_layout=(
            None if graph_result is None else graph_result.cell1_graph_visualization_layout
        ),
        cell4_graph_visualization_layout=(
            None if graph_result is None else graph_result.cell4_graph_visualization_layout
        ),
        graph_comparison_visualization_layout=(
            None if graph_result is None else graph_result.graph_comparison_visualization_layout
        ),
    )


def render_grc9v3_representative_visual_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    fixture_name: str = DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME,
    artifact_path: str | Path | None = None,
    surface_mode: str = SURFACE_MODE_BEHAVIOR,
) -> GRC9V3RepresentativeVisualizationResult:
    """Render the representative GRC9V3 Appendix E lane from saved artifacts."""

    normalized_surface_mode = _normalize_surface_mode(surface_mode)

    if artifact_path is None:
        fixture_root = Path(telemetry_root) / Path(telemetry_experiment_path) / fixture_name
        telemetry_layout = _discover_latest_run_layout(fixture_root)
    else:
        telemetry_layout = _layout_from_artifact_path(Path(artifact_path))

    pack = load_telemetry_artifact_pack(telemetry_layout)
    visualization_layout = build_run_visualization_layout(
        telemetry_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / fixture_name
        ),
    )

    graph_result: GRC9V3RepresentativeGraphVisualizationResult | None = None
    if normalized_surface_mode in (SURFACE_MODE_GRAPH, SURFACE_MODE_ALL):
        graph_result = render_grc9v3_representative_graph_suite(
            telemetry_root=telemetry_root,
            telemetry_experiment_path=telemetry_experiment_path,
            visualization_root=visualization_root,
            fixture_name=fixture_name,
            artifact_path=artifact_path,
        )

    if normalized_surface_mode in (SURFACE_MODE_BEHAVIOR, SURFACE_MODE_ALL):
        render_run_visual_bundle(
            pack,
            report=_grc9v3_visual_report(pack),
            layout=visualization_layout,
            observables=DEFAULT_GRC9V3_RUN_OBSERVABLES,
        )

    return GRC9V3RepresentativeVisualizationResult(
        surface_mode=normalized_surface_mode,
        fixture_name=fixture_name,
        telemetry_layout=telemetry_layout,
        visualization_layout=visualization_layout,
        graph_visualization_layout=(
            None if graph_result is None else graph_result.graph_visualization_layout
        ),
    )


def render_grc9_representative_visual_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRC9_REPRESENTATIVE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    lane_name: str = DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
    surface_mode: str = SURFACE_MODE_BEHAVIOR,
) -> GRC9RepresentativeVisualizationResult:
    """Render the representative GRC9 behavior lane from saved artifacts."""

    normalized_surface_mode = _normalize_surface_mode(surface_mode)

    lane_root = Path(telemetry_root) / Path(telemetry_experiment_path) / lane_name
    primary_layout = _discover_single_run_layout(lane_root / "primary")
    replay_layout = _discover_single_run_layout(lane_root / "replay")
    primary_pack = load_telemetry_artifact_pack(primary_layout)
    replay_pack = load_telemetry_artifact_pack(replay_layout)

    primary_visual_layout = build_run_visualization_layout(
        primary_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name / "primary"
        ),
    )
    replay_visual_layout = build_run_visualization_layout(
        replay_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name / "replay"
        ),
    )
    comparison_visual_layout = build_comparison_visualization_layout(
        primary_layout,
        replay_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name
        ),
    )

    graph_result: GRC9RepresentativeGraphVisualizationResult | None = None
    if normalized_surface_mode in (SURFACE_MODE_GRAPH, SURFACE_MODE_ALL):
        graph_result = render_grc9_representative_graph_suite(
            telemetry_root=telemetry_root,
            telemetry_experiment_path=telemetry_experiment_path,
            visualization_root=visualization_root,
            lane_name=lane_name,
        )

    if normalized_surface_mode in (SURFACE_MODE_BEHAVIOR, SURFACE_MODE_ALL):
        render_run_visual_bundle(
            primary_pack,
            layout=primary_visual_layout,
            observables=DEFAULT_GRC9_RUN_OBSERVABLES,
        )
        render_run_visual_bundle(
            replay_pack,
            layout=replay_visual_layout,
            observables=DEFAULT_GRC9_RUN_OBSERVABLES,
        )
        render_comparison_visual_bundle(
            primary_pack,
            replay_pack,
            layout=comparison_visual_layout,
            observables=DEFAULT_GRC9_COMPARISON_OBSERVABLES,
        )

    return GRC9RepresentativeVisualizationResult(
        surface_mode=normalized_surface_mode,
        primary_telemetry_layout=primary_layout,
        replay_telemetry_layout=replay_layout,
        primary_visualization_layout=primary_visual_layout,
        replay_visualization_layout=replay_visual_layout,
        comparison_visualization_layout=comparison_visual_layout,
        primary_graph_visualization_layout=(
            None if graph_result is None else graph_result.primary_graph_visualization_layout
        ),
        replay_graph_visualization_layout=(
            None if graph_result is None else graph_result.replay_graph_visualization_layout
        ),
        graph_comparison_visualization_layout=(
            None if graph_result is None else graph_result.graph_comparison_visualization_layout
        ),
    )


def render_grc9_landscape_visual_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRC9_LANDSCAPE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    profile_name: str = DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
    surface_mode: str = SURFACE_MODE_BEHAVIOR,
) -> GRC9LandscapeVisualizationResult:
    """Render the seed-driven GRC9 visualization lane from saved artifacts."""

    normalized_surface_mode = _normalize_surface_mode(surface_mode)

    family_root = Path(telemetry_root) / Path(telemetry_experiment_path) / profile_name
    cell1_layout = _discover_single_run_layout(family_root / "cell-1")
    cell4_layout = _discover_single_run_layout(family_root / "cell-4")
    cell1_pack = load_telemetry_artifact_pack(cell1_layout)
    cell4_pack = load_telemetry_artifact_pack(cell4_layout)

    cell1_visual_layout = build_run_visualization_layout(
        cell1_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name / "cell-1"
        ),
    )
    cell4_visual_layout = build_run_visualization_layout(
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name / "cell-4"
        ),
    )
    comparison_visual_layout = build_comparison_visualization_layout(
        cell1_layout,
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name
        ),
    )

    graph_result: GRC9LandscapeGraphVisualizationResult | None = None
    if normalized_surface_mode in (SURFACE_MODE_GRAPH, SURFACE_MODE_ALL):
        graph_result = render_grc9_landscape_graph_suite(
            telemetry_root=telemetry_root,
            telemetry_experiment_path=telemetry_experiment_path,
            visualization_root=visualization_root,
            profile_name=profile_name,
        )

    if normalized_surface_mode in (SURFACE_MODE_BEHAVIOR, SURFACE_MODE_ALL):
        render_run_visual_bundle(
            cell1_pack,
            layout=cell1_visual_layout,
            observables=DEFAULT_GRC9_RUN_OBSERVABLES,
        )
        render_run_visual_bundle(
            cell4_pack,
            layout=cell4_visual_layout,
            observables=DEFAULT_GRC9_RUN_OBSERVABLES,
        )
        render_comparison_visual_bundle(
            cell1_pack,
            cell4_pack,
            layout=comparison_visual_layout,
            observables=DEFAULT_GRC9_COMPARISON_OBSERVABLES,
        )

    return GRC9LandscapeVisualizationResult(
        surface_mode=normalized_surface_mode,
        cell1_telemetry_layout=cell1_layout,
        cell4_telemetry_layout=cell4_layout,
        cell1_visualization_layout=cell1_visual_layout,
        cell4_visualization_layout=cell4_visual_layout,
        comparison_visualization_layout=comparison_visual_layout,
        cell1_graph_visualization_layout=(
            None if graph_result is None else graph_result.cell1_graph_visualization_layout
        ),
        cell4_graph_visualization_layout=(
            None if graph_result is None else graph_result.cell4_graph_visualization_layout
        ),
        graph_comparison_visualization_layout=(
            None if graph_result is None else graph_result.graph_comparison_visualization_layout
        ),
    )


def render_grcv3_representative_visual_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    lane_name: str = DEFAULT_GRCV3_REPRESENTATIVE_LANE,
    surface_mode: str = SURFACE_MODE_BEHAVIOR,
) -> GRCV3RepresentativeVisualizationResult:
    """Render the representative GRCV3 visualization lane from saved artifacts."""

    normalized_surface_mode = _normalize_surface_mode(surface_mode)

    lane_root = Path(telemetry_root) / Path(telemetry_experiment_path) / lane_name
    primary_layout = _discover_single_run_layout(lane_root / "primary")
    replay_layout = _discover_single_run_layout(lane_root / "replay")
    primary_pack = load_telemetry_artifact_pack(primary_layout)
    replay_pack = load_telemetry_artifact_pack(replay_layout)

    primary_visual_layout = build_run_visualization_layout(
        primary_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name / "primary"
        ),
    )
    replay_visual_layout = build_run_visualization_layout(
        replay_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name / "replay"
        ),
    )
    comparison_visual_layout = build_comparison_visualization_layout(
        primary_layout,
        replay_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / lane_name
        ),
    )

    graph_result: GRCV3RepresentativeGraphVisualizationResult | None = None
    if normalized_surface_mode in (SURFACE_MODE_GRAPH, SURFACE_MODE_ALL):
        graph_result = render_grcv3_representative_graph_suite(
            telemetry_root=telemetry_root,
            telemetry_experiment_path=telemetry_experiment_path,
            visualization_root=visualization_root,
            lane_name=lane_name,
        )

    if normalized_surface_mode in (SURFACE_MODE_BEHAVIOR, SURFACE_MODE_ALL):
        render_run_visual_bundle(
            primary_pack,
            layout=primary_visual_layout,
            observables=DEFAULT_GRCV3_RUN_OBSERVABLES,
        )
        render_run_visual_bundle(
            replay_pack,
            layout=replay_visual_layout,
            observables=DEFAULT_GRCV3_RUN_OBSERVABLES,
        )
        render_comparison_visual_bundle(
            primary_pack,
            replay_pack,
            layout=comparison_visual_layout,
            observables=DEFAULT_GRCV3_COMPARISON_OBSERVABLES,
        )

    return GRCV3RepresentativeVisualizationResult(
        surface_mode=normalized_surface_mode,
        primary_telemetry_layout=primary_layout,
        replay_telemetry_layout=replay_layout,
        primary_visualization_layout=primary_visual_layout,
        replay_visualization_layout=replay_visual_layout,
        comparison_visualization_layout=comparison_visual_layout,
        primary_graph_visualization_layout=(
            None if graph_result is None else graph_result.primary_graph_visualization_layout
        ),
        replay_graph_visualization_layout=(
            None if graph_result is None else graph_result.replay_graph_visualization_layout
        ),
        graph_comparison_visualization_layout=(
            None if graph_result is None else graph_result.graph_comparison_visualization_layout
        ),
    )


def render_grcv3_landscape_visual_suite(
    *,
    telemetry_root: str | Path = DEFAULT_TELEMETRY_ROOT,
    telemetry_experiment_path: str | Path = DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH,
    visualization_root: str | Path | None = None,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    surface_mode: str = SURFACE_MODE_BEHAVIOR,
) -> GRCV3LandscapeVisualizationResult:
    """Render the seed-driven GRCV3 cell-1/cell-4 lane from saved artifacts."""

    normalized_surface_mode = _normalize_surface_mode(surface_mode)

    family_root = Path(telemetry_root) / Path(telemetry_experiment_path) / profile_name
    cell1_layout = _discover_single_run_layout(family_root / "cell-1")
    cell4_layout = _discover_single_run_layout(family_root / "cell-4")
    cell1_pack = load_telemetry_artifact_pack(cell1_layout)
    cell4_pack = load_telemetry_artifact_pack(cell4_layout)

    cell1_visual_layout = build_run_visualization_layout(
        cell1_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name / "cell-1"
        ),
    )
    cell4_visual_layout = build_run_visualization_layout(
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name / "cell-4"
        ),
    )
    comparison_visual_layout = build_comparison_visualization_layout(
        cell1_layout,
        cell4_layout,
        visualization_root=(
            None
            if visualization_root is None
            else Path(visualization_root) / Path(telemetry_experiment_path) / profile_name
        ),
    )

    graph_result: GRCV3LandscapeGraphVisualizationResult | None = None
    if normalized_surface_mode in (SURFACE_MODE_GRAPH, SURFACE_MODE_ALL):
        graph_result = render_grcv3_landscape_graph_suite(
            telemetry_root=telemetry_root,
            telemetry_experiment_path=telemetry_experiment_path,
            visualization_root=visualization_root,
            profile_name=profile_name,
        )

    if normalized_surface_mode in (SURFACE_MODE_BEHAVIOR, SURFACE_MODE_ALL):
        render_run_visual_bundle(
            cell1_pack,
            layout=cell1_visual_layout,
            observables=DEFAULT_GRCV3_RUN_OBSERVABLES,
        )
        render_run_visual_bundle(
            cell4_pack,
            layout=cell4_visual_layout,
            observables=DEFAULT_GRCV3_RUN_OBSERVABLES,
        )
        render_comparison_visual_bundle(
            cell1_pack,
            cell4_pack,
            layout=comparison_visual_layout,
            observables=DEFAULT_GRCV3_COMPARISON_OBSERVABLES,
        )

    return GRCV3LandscapeVisualizationResult(
        surface_mode=normalized_surface_mode,
        cell1_telemetry_layout=cell1_layout,
        cell4_telemetry_layout=cell4_layout,
        cell1_visualization_layout=cell1_visual_layout,
        cell4_visualization_layout=cell4_visual_layout,
        comparison_visualization_layout=comparison_visual_layout,
        cell1_graph_visualization_layout=(
            None if graph_result is None else graph_result.cell1_graph_visualization_layout
        ),
        cell4_graph_visualization_layout=(
            None if graph_result is None else graph_result.cell4_graph_visualization_layout
        ),
        graph_comparison_visualization_layout=(
            None if graph_result is None else graph_result.graph_comparison_visualization_layout
        ),
    )


def _normalize_surface_mode(surface_mode: str) -> str:
    normalized = surface_mode.strip().lower()
    if normalized not in SUPPORTED_SURFACE_MODES:
        raise ValueError(
            "unsupported representative visualization surface mode "
            f"{surface_mode!r}; expected one of {SUPPORTED_SURFACE_MODES}"
        )
    return normalized


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


def _grc9v3_visual_report(pack: TelemetryArtifactPack) -> TelemetryExperimentReport | None:
    experiment_report = pack.experiment_report
    if experiment_report is None:
        return None
    if _has_standard_run_report_common(experiment_report):
        common = dict(experiment_report.common)
        extensions = dict(experiment_report.extensions)
    else:
        base_report = build_run_experiment_report(
            pack.run_summary,
            step_rows=pack.step_rows,
            artifact_layout=pack.layout,
        )
        common = dict(base_report.common)
        for key, value in experiment_report.common.items():
            if key not in common:
                common[key] = value
        extensions = dict(base_report.extensions)
        for key, value in experiment_report.extensions.items():
            extensions[key] = value
    run_extension = pack.run_summary.family_extensions.get("grc9v3")
    if run_extension is not None:
        merged_grc9v3 = dict(extensions.get("grc9v3", {}))
        merged_grc9v3.update(run_extension)
        lane_summary = _grc9v3_event_lane_summary(pack.event_rows)
        if lane_summary:
            merged_grc9v3["visual_event_lane_summary"] = lane_summary
        extensions["grc9v3"] = merged_grc9v3
    return TelemetryExperimentReport(
        family=experiment_report.family,
        common=common,
        extensions=extensions,
    )


def _has_standard_run_report_common(report: TelemetryExperimentReport) -> bool:
    required_keys = (
        "completed_steps",
        "total_event_count",
        "changed_observables",
        "resolved_params",
        "event_counts_by_kind",
        "checkpoint_overview",
    )
    return all(key in report.common for key in required_keys)


__all__ = [
    "DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME",
    "GRC9LandscapeVisualizationResult",
    "GRC9RepresentativeVisualizationResult",
    "GRC9V3RepresentativeVisualizationResult",
    "GRCV3LandscapeVisualizationResult",
    "GRCV3RepresentativeVisualizationResult",
    "RepresentativeVisualizationResult",
    "SUPPORTED_SURFACE_MODES",
    "SURFACE_MODE_ALL",
    "SURFACE_MODE_BEHAVIOR",
    "SURFACE_MODE_GRAPH",
    "render_grc9_landscape_visual_suite",
    "render_grc9_representative_visual_suite",
    "render_grc9v3_representative_visual_suite",
    "render_grcv3_landscape_visual_suite",
    "render_grcv3_representative_visual_suite",
    "render_grcv2_representative_visual_suite",
]
