"""Test whether existing structural vocabulary already authors secondary-support reentry."""

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
    DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED,
    DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS,
    build_grcv3_landscape_secondary_support_authorability_trace,
)


DEFAULT_EXPLICIT_PATH_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-split-child-inheriting-settlement-probe.seed.yaml"
)
DEFAULT_EXPLICIT_DIRECT_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-carrier-site-split-child-inheriting-settlement-probe.seed.yaml"
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Test whether existing structural vocabulary already authors the "
            "descendant secondary-support reentry condition."
        )
    )
    parser.add_argument(
        "--structural-path-seed",
        default=str(DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED),
        help="Existing-structure path lane seed path.",
    )
    parser.add_argument(
        "--explicit-path-seed",
        default=str(DEFAULT_EXPLICIT_PATH_SEED),
        help="Explicit settlement-regime path lane seed path.",
    )
    parser.add_argument(
        "--structural-direct-seed",
        default=str(DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED),
        help="Existing-structure direct lane seed path.",
    )
    parser.add_argument(
        "--explicit-direct-seed",
        default=str(DEFAULT_EXPLICIT_DIRECT_SEED),
        help="Explicit settlement-regime direct lane seed path.",
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
        default=DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS,
        help="Number of steps to compare after the shared initial state.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    trace = build_grcv3_landscape_secondary_support_authorability_trace(
        structural_path_seed_path=Path(args.structural_path_seed),
        explicit_path_seed_path=Path(args.explicit_path_seed),
        structural_direct_seed_path=Path(args.structural_direct_seed),
        explicit_direct_seed_path=Path(args.explicit_direct_seed),
        profile_name=args.profile,
        primitive_id=args.primitive_id,
        num_steps=args.steps,
    )
    print(json.dumps(trace, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
