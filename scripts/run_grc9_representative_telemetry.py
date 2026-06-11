"""Run the representative telemetry-backed GRC9 lane and write artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.core import digest_snapshot
from pygrc.telemetry import run_grc9_representative_experiment


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_LANE_NAME = "phase6_mechanical_baseline"
DEFAULT_STEPS = 4


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the representative telemetry-backed GRC9 lane."
    )
    parser.add_argument(
        "--outputs-root",
        default=str(DEFAULT_OUTPUTS_ROOT),
        help="Project-relative artifact root.",
    )
    parser.add_argument(
        "--lane-name",
        default=DEFAULT_LANE_NAME,
        help="Representative lane name written under outputs/representative/grc9/.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of representative GRC9 steps to run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    result = run_grc9_representative_experiment(
        telemetry_root=Path(args.outputs_root),
        lane_name=args.lane_name,
        num_steps=args.steps,
    )

    primary_layout = result.primary_run.telemetry.artifact_layout
    replay_layout = result.replay_run.telemetry.artifact_layout
    if primary_layout is None or replay_layout is None:
        raise RuntimeError("representative GRC9 telemetry run did not write artifacts")

    summary = {
        "lane_name": result.lane_name,
        "steps": result.num_steps,
        "primary_run_id": result.primary_run.telemetry.identity.run_id,
        "replay_run_id": result.replay_run.telemetry.identity.run_id,
        "primary_final_snapshot_digest": digest_snapshot(result.primary_run.model.snapshot()),
        "replay_final_snapshot_digest": digest_snapshot(result.replay_run.model.snapshot()),
        "digests_match": (
            digest_snapshot(result.primary_run.model.snapshot())
            == digest_snapshot(result.replay_run.model.snapshot())
        ),
        "primary_artifact_dir": primary_layout.root_dir.as_posix(),
        "replay_artifact_dir": replay_layout.root_dir.as_posix(),
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
