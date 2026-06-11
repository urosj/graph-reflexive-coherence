"""Render visuals for the representative Phase T-GRC9V3 Appendix E lane."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from pygrc.telemetry import DEFAULT_TELEMETRY_ROOT
from pygrc.visualization import (
    DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME,
    SUPPORTED_SURFACE_MODES,
    SURFACE_MODE_BEHAVIOR,
    render_grc9v3_representative_visual_suite,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render artifact-driven visuals for the representative Phase T-GRC9V3 "
            "Appendix E lane. Graph-facing modes require saved port-graph "
            "checkpoints with GRC9V3 overlays."
        )
    )
    parser.add_argument(
        "--telemetry-root",
        default=str(DEFAULT_TELEMETRY_ROOT),
        help="Root directory of the experiment artifact tree.",
    )
    parser.add_argument(
        "--experiment-path",
        default=str(DEFAULT_GRC9V3_REPRESENTATIVE_EXPERIMENT_PATH),
        help="Relative representative experiment path under the telemetry root.",
    )
    parser.add_argument(
        "--visualization-root",
        default=None,
        help=(
            "Optional override root for visualization outputs. "
            "When omitted, visualization is written alongside telemetry under the run directory."
        ),
    )
    parser.add_argument(
        "--fixture-name",
        default=DEFAULT_GRC9V3_REPRESENTATIVE_FIXTURE_NAME,
        help="Representative GRC9V3 fixture to render.",
    )
    parser.add_argument(
        "--artifact-path",
        default=None,
        help=(
            "Optional explicit telemetry run directory, or its telemetry subdirectory. "
            "When provided, this pins the exact artifact pack instead of discovering "
            "the latest fixture run."
        ),
    )
    parser.add_argument(
        "--surface",
        choices=SUPPORTED_SURFACE_MODES,
        default=SURFACE_MODE_BEHAVIOR,
        help=(
            "Visualization surface to render. Graph-facing modes require the "
            "representative lane to contain saved graph checkpoints with enabled "
            "GRC9V3 overlays."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        result = render_grc9v3_representative_visual_suite(
            telemetry_root=Path(args.telemetry_root),
            telemetry_experiment_path=Path(args.experiment_path),
            visualization_root=(
                None if args.visualization_root is None else Path(args.visualization_root)
            ),
            fixture_name=args.fixture_name,
            artifact_path=(
                None if args.artifact_path is None else Path(args.artifact_path)
            ),
            surface_mode=args.surface,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print("Representative GRC9V3 visuals complete.")
    print(f"surface={result.surface_mode}")
    print(f"fixture={result.fixture_name}")
    print(f"visual_dir={result.visualization_layout.run_dir.as_posix()}")
    if result.graph_visualization_layout is not None:
        print(f"graph_dir={result.graph_visualization_layout.run_dir.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
