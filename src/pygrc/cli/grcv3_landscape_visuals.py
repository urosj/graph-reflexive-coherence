"""Render behavior visuals for the canonical seed-driven GRCV3 cell pair."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from pygrc.telemetry import (
    DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH,
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    DEFAULT_TELEMETRY_ROOT,
)
from pygrc.visualization import (
    SUPPORTED_SURFACE_MODES,
    SURFACE_MODE_BEHAVIOR,
    render_grcv3_landscape_visual_suite,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render first-pass artifact-driven visuals for the canonical "
            "seed-driven GRCV3 cell-1/cell-4 lane. Behavior rendering is "
            "supported now; graph-facing modes fail explicitly until that lane "
            "exports graph checkpoints."
        )
    )
    parser.add_argument(
        "--telemetry-root",
        default=str(DEFAULT_TELEMETRY_ROOT),
        help="Root directory of the experiment artifact tree.",
    )
    parser.add_argument(
        "--experiment-path",
        default=str(DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH),
        help="Relative experiment path under the telemetry root.",
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
        "--profile",
        default=DEFAULT_GRCV3_LANDSCAPE_PROFILE,
        help="Seed-driven GRCV3 landscape profile to render.",
    )
    parser.add_argument(
        "--surface",
        choices=SUPPORTED_SURFACE_MODES,
        default=SURFACE_MODE_BEHAVIOR,
        help=(
            "Visualization surface to render. Graph-facing modes are accepted "
            "but currently fail because the seed-driven landscape lane does "
            "not yet export graph checkpoints."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        result = render_grcv3_landscape_visual_suite(
            telemetry_root=Path(args.telemetry_root),
            telemetry_experiment_path=Path(args.experiment_path),
            visualization_root=(
                None if args.visualization_root is None else Path(args.visualization_root)
            ),
            profile_name=args.profile,
            surface_mode=args.surface,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print("GRCV3 landscape visuals complete.")
    print(f"surface={result.surface_mode}")
    print(f"cell-1 visual_dir={result.cell1_visualization_layout.run_dir.as_posix()}")
    print(f"cell-4 visual_dir={result.cell4_visualization_layout.run_dir.as_posix()}")
    print(
        "comparison_dir="
        + result.comparison_visualization_layout.comparison_dir.as_posix()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
