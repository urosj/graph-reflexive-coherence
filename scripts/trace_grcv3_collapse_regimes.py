"""Characterize collapse loci across the saved spindle-lane controls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.telemetry import (
    DEFAULT_GRCV3_COLLAPSE_TRACE_DIRECT_SEED,
    DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
    DEFAULT_GRCV3_COLLAPSE_TRACE_PATH_SEED,
    DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_DIRECT_SEED,
    DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_PATH_SEED,
    DEFAULT_GRCV3_COLLAPSE_TRACE_STEPS,
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    build_grcv3_landscape_collapse_regime_trace,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Characterize collapse loci across direct, path, and split-child "
            "spindle-lane controls under the recorded choice/collapse envelope."
        )
    )
    parser.add_argument(
        "--direct-seed",
        default=str(DEFAULT_GRCV3_COLLAPSE_TRACE_DIRECT_SEED),
        help="Carrier-site direct control seed path.",
    )
    parser.add_argument(
        "--path-seed",
        default=str(DEFAULT_GRCV3_COLLAPSE_TRACE_PATH_SEED),
        help="Path-node comparison seed path.",
    )
    parser.add_argument(
        "--split-path-seed",
        default=str(DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_PATH_SEED),
        help="Split-child path-regime seed path.",
    )
    parser.add_argument(
        "--split-direct-seed",
        default=str(DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_DIRECT_SEED),
        help="Split-child direct-regime seed path.",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_GRCV3_LANDSCAPE_PROFILE,
        help="GRCV3 landscape profile to use.",
    )
    parser.add_argument(
        "--primitive-id",
        default="spindle_core",
        help="Primitive id to monitor.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_GRCV3_COLLAPSE_TRACE_STEPS,
        help="Number of steps to compare after the shared initial state.",
    )
    parser.add_argument(
        "--epsilon-choice",
        type=float,
        default=DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
        help="Choice ambiguity threshold for the sink-compatibility backend.",
    )
    parser.add_argument(
        "--epsilon-collapse",
        type=float,
        default=DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
        help="Collapse winner-margin threshold for the sink-compatibility backend.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    trace = build_grcv3_landscape_collapse_regime_trace(
        direct_seed_path=Path(args.direct_seed),
        path_seed_path=Path(args.path_seed),
        split_path_seed_path=Path(args.split_path_seed),
        split_direct_seed_path=Path(args.split_direct_seed),
        profile_name=args.profile,
        primitive_id=args.primitive_id,
        num_steps=args.steps,
        epsilon_choice=args.epsilon_choice,
        epsilon_collapse=args.epsilon_collapse,
    )
    print(json.dumps(trace, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
