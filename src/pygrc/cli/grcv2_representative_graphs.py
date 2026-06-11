"""Render graph-facing visuals for the canonical representative GRCV2 lane."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from pygrc.telemetry import (
    DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH,
    DEFAULT_REPRESENTATIVE_FAMILY,
    DEFAULT_TELEMETRY_ROOT,
)
from pygrc.visualization import render_grcv2_representative_graph_suite


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render checkpoint-backed graph visuals for the representative GRCV2 "
            "experiment lane."
        )
    )
    parser.add_argument(
        "--telemetry-root",
        default=str(DEFAULT_TELEMETRY_ROOT),
        help="Root directory of the experiment artifact tree.",
    )
    parser.add_argument(
        "--experiment-path",
        default=str(DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH),
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
        "--family",
        default=DEFAULT_REPRESENTATIVE_FAMILY,
        help="Representative family lane to render.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        result = render_grcv2_representative_graph_suite(
            telemetry_root=Path(args.telemetry_root),
            telemetry_experiment_path=Path(args.experiment_path),
            visualization_root=None if args.visualization_root is None else Path(args.visualization_root),
            family_name=args.family,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print("Representative GRCV2 graph visuals complete.")
    print(
        "cell-1 graph_dir="
        + result.cell1_graph_visualization_layout.run_dir.as_posix()
    )
    print(
        "cell-4 graph_dir="
        + result.cell4_graph_visualization_layout.run_dir.as_posix()
    )
    print(
        "graph_comparison_dir="
        + result.graph_comparison_visualization_layout.comparison_dir.as_posix()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
