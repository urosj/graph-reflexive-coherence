"""Widen the post-spark collapse boundary pass to inspect late-window convergence."""

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
    DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED,
    DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED,
    DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED,
    DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP,
    DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS,
    build_grcv3_landscape_post_spark_late_window_stability_trace,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Widen the rich-v4 post-spark collapse comparison to test whether "
            "the blocked control converges later in the run."
        )
    )
    parser.add_argument(
        "--baseline-seed",
        default=str(DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED),
        help="Baseline post-spark collapse seed path.",
    )
    parser.add_argument(
        "--blocked-control-seed",
        default=str(DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED),
        help="Blocked center-coupling control seed path.",
    )
    parser.add_argument(
        "--refined-control-seed",
        default=str(DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED),
        help="Refined center-coupling control seed path.",
    )
    parser.add_argument(
        "--profile",
        default="seed_baseline",
        help="Landscape profile name.",
    )
    parser.add_argument(
        "--primitive-id",
        default="spindle_core",
        help="Primitive id to monitor.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS,
        help="Number of steps to simulate.",
    )
    parser.add_argument(
        "--late-window-start-step",
        type=int,
        default=DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP,
        help="Collapse events after this step are treated as late-window behavior.",
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
    if args.steps <= 0:
        parser.error("--steps must be > 0")
    if args.late_window_start_step < 0:
        parser.error("--late-window-start-step must be >= 0")

    trace = build_grcv3_landscape_post_spark_late_window_stability_trace(
        baseline_seed_path=Path(args.baseline_seed),
        blocked_control_seed_path=Path(args.blocked_control_seed),
        refined_control_seed_path=Path(args.refined_control_seed),
        profile_name=args.profile,
        primitive_id=args.primitive_id,
        num_steps=args.steps,
        late_window_start_step=args.late_window_start_step,
        epsilon_choice=args.epsilon_choice,
        epsilon_collapse=args.epsilon_collapse,
    )
    print(json.dumps(trace, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
