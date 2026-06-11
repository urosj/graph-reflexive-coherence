"""Artifact-driven visualization helpers for PyGRC."""

from importlib import import_module

from .layout import (
    COMPARISON_REPORT_PANEL_FILENAME,
    COMPARISON_TRAJECTORY_FIGURE_FILENAME,
    DEFAULT_VISUALIZATION_ROOT,
    EVENT_TIMELINE_FILENAME,
    GRAPH_ANIMATION_FILENAME,
    GRAPH_COMPARISON_FIGURE_FILENAME,
    GRAPH_FINAL_HTML_FILENAME,
    GRAPH_LAYOUT_FILENAME,
    GRAPH_SEQUENCE_FIGURE_FILENAME,
    GRAPH_SNAPSHOTS_DIRNAME,
    ComparisonVisualizationLayout,
    GraphComparisonVisualizationLayout,
    GraphRunVisualizationLayout,
    RUN_REPORT_PANEL_FILENAME,
    RunVisualizationLayout,
    TRAJECTORY_FIGURE_FILENAME,
    build_graph_comparison_visualization_layout,
    build_graph_run_visualization_layout,
    build_comparison_visualization_layout,
    build_run_visualization_layout,
    map_telemetry_root_to_visualization_root,
)
from .graph_render import (
    render_graph_comparison_visual_bundle,
    render_graph_run_visual_bundle,
)
from .render import (
    DEFAULT_COMPARISON_OBSERVABLES,
    DEFAULT_GRC9_COMPARISON_OBSERVABLES,
    DEFAULT_GRC9_RUN_OBSERVABLES,
    DEFAULT_GRC9V3_RUN_OBSERVABLES,
    DEFAULT_LGRC9V3_RUN_OBSERVABLES,
    DEFAULT_GRCV3_COMPARISON_OBSERVABLES,
    DEFAULT_GRCV3_RUN_OBSERVABLES,
    DEFAULT_RUN_OBSERVABLES,
    render_comparison_visual_bundle,
    render_run_visual_bundle,
)
from .representative import (
    DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME,
    GRC9LandscapeVisualizationResult,
    GRC9RepresentativeVisualizationResult,
    GRC9V3RepresentativeVisualizationResult,
    GRCV3LandscapeVisualizationResult,
    GRCV3RepresentativeVisualizationResult,
    RepresentativeVisualizationResult,
    SUPPORTED_SURFACE_MODES,
    SURFACE_MODE_ALL,
    SURFACE_MODE_BEHAVIOR,
    SURFACE_MODE_GRAPH,
    render_grc9_landscape_visual_suite,
    render_grc9_representative_visual_suite,
    render_grc9v3_representative_visual_suite,
    render_grcv3_landscape_visual_suite,
    render_grcv3_representative_visual_suite,
    render_grcv2_representative_visual_suite,
)
from .representative_graphs import (
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

_GRCL9_VISUALIZATION_EXPORTS = {
    "GRCL9_BOUNDARY_PANEL_FILENAME",
    "GRCL9_OVERLAY_FILENAME",
    "GRCL9_OVERLAY_SUMMARY_FILENAME",
    "GRCL9_VISUALIZATION_VERSION",
    "GRCL9VisualizationLaneResult",
    "GRCL9VisualizationSessionResult",
    "render_grcl9_lowering_visual_session",
}

_GRCL9V3_VISUALIZATION_EXPORTS = {
    "GRCL9V3_BOUNDARY_PANEL_FILENAME",
    "GRCL9V3_OVERLAY_FILENAME",
    "GRCL9V3_OVERLAY_SUMMARY_FILENAME",
    "GRCL9V3_VISUALIZATION_VERSION",
    "GRCL9V3SkippedVisualRecord",
    "GRCL9V3VisualLaneRecord",
    "GRCL9V3VisualReviewSession",
    "render_grcl9v3_lowering_visual_review",
}

_MOTION_VISUALIZATION_EXPORTS = {
    "MOTION_ANIMATED_VISUALIZATION_VERSION",
    "MOTION_VISUALIZATION_VERSION",
    "MotionAnimatedVisualRecord",
    "MotionAnimatedVisualReviewSession",
    "MotionVisualRecord",
    "MotionVisualReviewSession",
    "render_motion_animated_visual_session",
    "render_motion_visual_session",
}


def __getattr__(name: str) -> object:
    if name in _GRCL9_VISUALIZATION_EXPORTS:
        lowering = import_module(".grcl9_lowering", __name__)
        value = getattr(lowering, name)
        globals()[name] = value
        return value
    if name in _GRCL9V3_VISUALIZATION_EXPORTS:
        lowering = import_module(".grcl9v3_lowering", __name__)
        value = getattr(lowering, name)
        globals()[name] = value
        return value
    if name in _MOTION_VISUALIZATION_EXPORTS:
        motion = import_module(".motion", __name__)
        value = getattr(motion, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "COMPARISON_REPORT_PANEL_FILENAME",
    "COMPARISON_TRAJECTORY_FIGURE_FILENAME",
    "DEFAULT_COMPARISON_OBSERVABLES",
    "DEFAULT_GRC9_COMPARISON_OBSERVABLES",
    "DEFAULT_GRC9_RUN_OBSERVABLES",
    "DEFAULT_GRC9V3_RUN_OBSERVABLES",
    "DEFAULT_LGRC9V3_RUN_OBSERVABLES",
    "DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME",
    "DEFAULT_GRCV3_COMPARISON_OBSERVABLES",
    "DEFAULT_GRCV3_RUN_OBSERVABLES",
    "DEFAULT_RUN_OBSERVABLES",
    "DEFAULT_VISUALIZATION_ROOT",
    "EVENT_TIMELINE_FILENAME",
    "GRAPH_ANIMATION_FILENAME",
    "GRAPH_COMPARISON_FIGURE_FILENAME",
    "GRAPH_FINAL_HTML_FILENAME",
    "GRAPH_LAYOUT_FILENAME",
    "GRAPH_SEQUENCE_FIGURE_FILENAME",
    "GRAPH_SNAPSHOTS_DIRNAME",
    "GRCL9_BOUNDARY_PANEL_FILENAME",
    "GRCL9_OVERLAY_FILENAME",
    "GRCL9_OVERLAY_SUMMARY_FILENAME",
    "GRCL9_VISUALIZATION_VERSION",
    "GRCL9V3_BOUNDARY_PANEL_FILENAME",
    "GRCL9V3_OVERLAY_FILENAME",
    "GRCL9V3_OVERLAY_SUMMARY_FILENAME",
    "GRCL9V3_VISUALIZATION_VERSION",
    "GRCL9V3SkippedVisualRecord",
    "GRCL9V3VisualLaneRecord",
    "GRCL9V3VisualReviewSession",
    "ComparisonVisualizationLayout",
    "GraphComparisonVisualizationLayout",
    "GraphRunVisualizationLayout",
    "GRC9LandscapeGraphVisualizationResult",
    "GRC9LandscapeVisualizationResult",
    "GRC9RepresentativeGraphVisualizationResult",
    "GRC9RepresentativeVisualizationResult",
    "GRC9V3RepresentativeGraphVisualizationResult",
    "GRC9V3RepresentativeVisualizationResult",
    "GRCL9VisualizationLaneResult",
    "GRCL9VisualizationSessionResult",
    "GRCV3LandscapeGraphVisualizationResult",
    "GRCV3LandscapeVisualizationResult",
    "GRCV3RepresentativeGraphVisualizationResult",
    "GRCV3RepresentativeVisualizationResult",
    "MOTION_VISUALIZATION_VERSION",
    "MOTION_ANIMATED_VISUALIZATION_VERSION",
    "MotionAnimatedVisualRecord",
    "MotionAnimatedVisualReviewSession",
    "MotionVisualRecord",
    "MotionVisualReviewSession",
    "RUN_REPORT_PANEL_FILENAME",
    "RepresentativeGraphVisualizationResult",
    "RepresentativeVisualizationResult",
    "RunVisualizationLayout",
    "SUPPORTED_SURFACE_MODES",
    "SURFACE_MODE_ALL",
    "SURFACE_MODE_BEHAVIOR",
    "SURFACE_MODE_GRAPH",
    "TRAJECTORY_FIGURE_FILENAME",
    "build_graph_comparison_visualization_layout",
    "build_graph_run_visualization_layout",
    "build_comparison_visualization_layout",
    "build_run_visualization_layout",
    "map_telemetry_root_to_visualization_root",
    "render_comparison_visual_bundle",
    "render_graph_comparison_visual_bundle",
    "render_grcl9_lowering_visual_session",
    "render_grcl9v3_lowering_visual_review",
    "render_grc9_landscape_graph_suite",
    "render_grc9_landscape_visual_suite",
    "render_grc9_representative_graph_suite",
    "render_grc9_representative_visual_suite",
    "render_grc9v3_representative_graph_suite",
    "render_grc9v3_representative_visual_suite",
    "render_grcv3_landscape_graph_suite",
    "render_grcv3_landscape_visual_suite",
    "render_grcv3_representative_graph_suite",
    "render_grcv3_representative_visual_suite",
    "render_grcv2_representative_graph_suite",
    "render_grcv2_representative_visual_suite",
    "render_graph_run_visual_bundle",
    "render_motion_animated_visual_session",
    "render_motion_visual_session",
    "render_run_visual_bundle",
]
