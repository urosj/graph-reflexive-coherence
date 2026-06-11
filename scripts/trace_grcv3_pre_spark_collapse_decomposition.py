"""Compare the two recorded pre-spark collapse lanes."""

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
    DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
    DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
    DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_BASELINE_SEED,
    DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_COMPARISON_SEED,
    build_grcv3_landscape_pre_spark_collapse_decomposition_trace,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the two recorded collapse-without-prior-spark lanes to see "
            "whether their sink difference already tracks existing structure."
        )
    )
    parser.add_argument(
        "--baseline-seed",
        default=str(DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_BASELINE_SEED),
        help="Baseline pre-spark collapse seed path.",
    )
    parser.add_argument(
        "--comparison-seed",
        default=str(DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_COMPARISON_SEED),
        help="Comparison pre-spark collapse seed path.",
    )
    parser.add_argument(
        "--baseline-profile",
        default="hot_exploratory",
        help="Baseline profile name.",
    )
    parser.add_argument(
        "--comparison-profile",
        default="seed_baseline",
        help="Comparison profile name.",
    )
    parser.add_argument(
        "--baseline-primitive-id",
        default="decision_core",
        help="Baseline primitive id to monitor.",
    )
    parser.add_argument(
        "--comparison-primitive-id",
        default="core_basin",
        help="Comparison primitive id to monitor.",
    )
    parser.add_argument(
        "--baseline-steps",
        type=int,
        default=10,
        help="Baseline number of steps.",
    )
    parser.add_argument(
        "--comparison-steps",
        type=int,
        default=160,
        help="Comparison number of steps.",
    )
    parser.add_argument(
        "--epsilon-choice",
        type=float,
        default=DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE,
        help="Choice ambiguity threshold.",
    )
    parser.add_argument(
        "--epsilon-collapse",
        type=float,
        default=DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE,
        help="Collapse winner-margin threshold.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.baseline_steps <= 0:
        parser.error("--baseline-steps must be > 0")
    if args.comparison_steps <= 0:
        parser.error("--comparison-steps must be > 0")

    trace = build_grcv3_landscape_pre_spark_collapse_decomposition_trace(
        baseline_seed_path=Path(args.baseline_seed),
        comparison_seed_path=Path(args.comparison_seed),
        baseline_profile_name=args.baseline_profile,
        comparison_profile_name=args.comparison_profile,
        baseline_primitive_id=args.baseline_primitive_id,
        comparison_primitive_id=args.comparison_primitive_id,
        baseline_num_steps=args.baseline_steps,
        comparison_num_steps=args.comparison_steps,
        epsilon_choice=args.epsilon_choice,
        epsilon_collapse=args.epsilon_collapse,
    )
    print(json.dumps(trace, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
