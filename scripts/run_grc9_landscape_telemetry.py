"""Run the canonical seed-driven GRC9 cell pair telemetry lane and write artifacts."""

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
    DEFAULT_GRC9_LANDSCAPE_PROFILE,
    run_grc9_landscape_experiment,
)
from pygrc.core import digest_snapshot


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_EXPERIMENT_PATH = Path("representative") / "grc9_landscape"
DEFAULT_STEPS = 3


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the canonical seed-driven GRC9 cell-1/cell-4 telemetry lane."
    )
    parser.add_argument(
        "--outputs-root",
        default=str(DEFAULT_OUTPUTS_ROOT),
        help="Project-relative artifact root.",
    )
    parser.add_argument(
        "--experiment-path",
        default=str(DEFAULT_EXPERIMENT_PATH),
        help="Relative experiment path written under outputs/.",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_GRC9_LANDSCAPE_PROFILE,
        help="Seed-driven GRC9 landscape profile to run.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of GRC9 steps to run for each seed.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    result = run_grc9_landscape_experiment(
        telemetry_root=Path(args.outputs_root),
        telemetry_experiment_path=Path(args.experiment_path),
        profile_name=args.profile,
        num_steps=args.steps,
    )

    assert result.cell1_run.telemetry is not None
    assert result.cell4_run.telemetry is not None
    cell1_layout = result.cell1_run.telemetry.artifact_layout
    cell4_layout = result.cell4_run.telemetry.artifact_layout
    if cell1_layout is None or cell4_layout is None:
        raise RuntimeError("GRC9 landscape experiment did not write artifacts")

    summary = {
        "profile_name": result.profile_name,
        "steps": result.num_steps,
        "cell1_run_id": result.cell1_run.telemetry.identity.run_id,
        "cell4_run_id": result.cell4_run.telemetry.identity.run_id,
        "cell1_artifact_dir": cell1_layout.root_dir.as_posix(),
        "cell4_artifact_dir": cell4_layout.root_dir.as_posix(),
        "cell1_final_snapshot_digest": digest_snapshot(result.cell1_run.model.snapshot()),
        "cell4_final_snapshot_digest": digest_snapshot(result.cell4_run.model.snapshot()),
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
