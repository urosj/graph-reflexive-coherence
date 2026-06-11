"""Run the canonical seed-driven GRCV3 cell pair telemetry lane and write artifacts."""

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
    run_grcv3_landscape_experiment,
)


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_EXPERIMENT_PATH = Path("representative") / "grcv3_landscape"
DEFAULT_STEPS = 3


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the canonical seed-driven GRCV3 cell-1/cell-4 telemetry lane."
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
        default=DEFAULT_GRCV3_LANDSCAPE_PROFILE,
        help="Seed-driven GRCV3 landscape profile to run.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of GRCV3 steps to run for each seed.",
    )
    parser.add_argument(
        "--record-graph-checkpoints",
        action="store_true",
        help="Record graph checkpoint artifacts in addition to behavior telemetry.",
    )
    parser.add_argument(
        "--checkpoint-every-step",
        action="store_true",
        help="Capture a graph checkpoint after every step.",
    )
    parser.add_argument(
        "--checkpoint-every-n-steps",
        type=int,
        default=None,
        help="Capture graph checkpoints every N steps.",
    )
    parser.add_argument(
        "--checkpoint-storage-mode",
        choices=("per_checkpoint_files", "jsonl_chunks"),
        default=None,
        help="Storage mode for graph checkpoints.",
    )
    parser.add_argument(
        "--checkpoint-chunk-size",
        type=int,
        default=100,
        help="Chunk size for jsonl_chunks checkpoint storage.",
    )
    parser.add_argument(
        "--include-flow-overlays",
        action="store_true",
        help="Export honest flow overlays when checkpoint artifacts are recorded.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    result = run_grcv3_landscape_experiment(
        telemetry_root=Path(args.outputs_root),
        telemetry_experiment_path=Path(args.experiment_path),
        profile_name=args.profile,
        num_steps=args.steps,
        record_graph_checkpoints=args.record_graph_checkpoints,
        checkpoint_every_step=args.checkpoint_every_step,
        checkpoint_every_n_steps=args.checkpoint_every_n_steps,
        checkpoint_storage_mode=args.checkpoint_storage_mode,
        checkpoint_chunk_size=args.checkpoint_chunk_size,
        include_flow_overlays=args.include_flow_overlays,
    )

    assert result.cell1_run.telemetry is not None
    assert result.cell4_run.telemetry is not None
    cell1_layout = result.cell1_run.telemetry.artifact_layout
    cell4_layout = result.cell4_run.telemetry.artifact_layout
    if cell1_layout is None or cell4_layout is None:
        raise RuntimeError("GRCV3 landscape experiment did not write artifacts")

    summary = {
        "profile_name": result.profile_name,
        "steps": result.num_steps,
        "cell1_run_id": result.cell1_run.telemetry.identity.run_id,
        "cell4_run_id": result.cell4_run.telemetry.identity.run_id,
        "cell1_artifact_dir": cell1_layout.root_dir.as_posix(),
        "cell4_artifact_dir": cell4_layout.root_dir.as_posix(),
        "cell1_changed_observables": result.cell1_report.common["changed_observables"],
        "cell4_changed_observables": result.cell4_report.common["changed_observables"],
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
