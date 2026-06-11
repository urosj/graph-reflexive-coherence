"""Characterize spark-forming settlement loci across two rich.v4 lanes."""

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
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED,
    DEFAULT_GRCV3_SETTLEMENT_LOCUS_COMPARISON_SEED,
    DEFAULT_GRCV3_SETTLEMENT_LOCUS_STEPS,
    build_grcv3_landscape_settlement_locus_regime_trace,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Characterize operative settlement loci for two spark-forming "
            "rich.v4 lanes."
        )
    )
    parser.add_argument(
        "--baseline-seed",
        default=str(DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED),
        help="Baseline lane seed path.",
    )
    parser.add_argument(
        "--comparison-seed",
        default=str(DEFAULT_GRCV3_SETTLEMENT_LOCUS_COMPARISON_SEED),
        help="Comparison lane seed path.",
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
        default=DEFAULT_GRCV3_SETTLEMENT_LOCUS_STEPS,
        help="Number of steps to compare after the shared initial state.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    trace = build_grcv3_landscape_settlement_locus_regime_trace(
        baseline_seed_path=Path(args.baseline_seed),
        comparison_seed_path=Path(args.comparison_seed),
        profile_name=args.profile,
        primitive_id=args.primitive_id,
        num_steps=args.steps,
    )
    print(json.dumps(trace, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
