"""Render first-pass visuals for the representative GRCV3 replay lane."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from pygrc.telemetry import (
    DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_GRCV3_REPRESENTATIVE_LANE,
    DEFAULT_TELEMETRY_ROOT,
)
from pygrc.visualization import (
    SUPPORTED_SURFACE_MODES,
    SURFACE_MODE_BEHAVIOR,
    render_grcv3_representative_visual_suite,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render first-pass artifact-driven visuals for the representative "
            "GRCV3 replay lane. Behavior, graph, and combined surfaces are "
            "available when the saved lane contains graph checkpoints."
        )
    )
    parser.add_argument(
        "--telemetry-root",
        default=str(DEFAULT_TELEMETRY_ROOT),
        help="Root directory of the experiment artifact tree.",
    )
    parser.add_argument(
        "--experiment-path",
        default=str(DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH),
        help="Relative representative experiment path under the telemetry root.",
    )
    parser.add_argument(
        "--visualization-root",
        default=None,
        help=(
            "Optional override root for visualization outputs. "
            "When omitted, visualization is written alongside telemetry under each run directory."
        ),
    )
    parser.add_argument(
        "--lane-name",
        default=DEFAULT_GRCV3_REPRESENTATIVE_LANE,
        help="Representative GRCV3 lane to render.",
    )
    parser.add_argument(
        "--surface",
        choices=SUPPORTED_SURFACE_MODES,
        default=SURFACE_MODE_BEHAVIOR,
        help=(
            "Visualization surface to render. Graph-facing modes require the "
            "representative lane to have been recorded with "
            "record_graph_checkpoints=True."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        result = render_grcv3_representative_visual_suite(
            telemetry_root=Path(args.telemetry_root),
            telemetry_experiment_path=Path(args.experiment_path),
            visualization_root=(
                None if args.visualization_root is None else Path(args.visualization_root)
            ),
            lane_name=args.lane_name,
            surface_mode=args.surface,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print("Representative GRCV3 visuals complete.")
    print(f"surface={result.surface_mode}")
    print(f"primary visual_dir={result.primary_visualization_layout.run_dir.as_posix()}")
    print(f"replay visual_dir={result.replay_visualization_layout.run_dir.as_posix()}")
    if result.primary_graph_visualization_layout is not None:
        print(
            "primary graph_dir="
            + result.primary_graph_visualization_layout.run_dir.as_posix()
        )
    if result.replay_graph_visualization_layout is not None:
        print(
            "replay graph_dir="
            + result.replay_graph_visualization_layout.run_dir.as_posix()
        )
    print(
        "comparison_dir="
        + result.comparison_visualization_layout.comparison_dir.as_posix()
    )
    if result.graph_comparison_visualization_layout is not None:
        print(
            "graph_comparison_dir="
            + result.graph_comparison_visualization_layout.comparison_dir.as_posix()
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
