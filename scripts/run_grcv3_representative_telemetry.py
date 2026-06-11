"""Run the representative telemetry-backed GRCV3 lane and write artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.telemetry import run_grcv3_representative_experiment


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_LANE_NAME = "phase5_reference"
DEFAULT_STEPS = 3


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the representative telemetry-backed GRCV3 lane."
    )
    parser.add_argument(
        "--outputs-root",
        default=str(DEFAULT_OUTPUTS_ROOT),
        help="Project-relative artifact root.",
    )
    parser.add_argument(
        "--lane-name",
        default=DEFAULT_LANE_NAME,
        help="Representative lane name written under outputs/representative/grcv3/.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of representative GRCV3 steps to run.",
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

    result = run_grcv3_representative_experiment(
        telemetry_root=Path(args.outputs_root),
        lane_name=args.lane_name,
        num_steps=args.steps,
        record_graph_checkpoints=args.record_graph_checkpoints,
        checkpoint_every_step=args.checkpoint_every_step,
        checkpoint_every_n_steps=args.checkpoint_every_n_steps,
        checkpoint_storage_mode=args.checkpoint_storage_mode,
        checkpoint_chunk_size=args.checkpoint_chunk_size,
        include_flow_overlays=args.include_flow_overlays,
    )

    primary_layout = result.primary_run.telemetry.artifact_layout
    replay_layout = result.replay_run.telemetry.artifact_layout
    if primary_layout is None or replay_layout is None:
        raise RuntimeError("representative GRCV3 telemetry run did not write artifacts")

    summary = {
        "lane_name": result.lane_name,
        "steps": result.num_steps,
        "primary_run_id": result.primary_run.telemetry.identity.run_id,
        "replay_run_id": result.replay_run.telemetry.identity.run_id,
        "primary_final_snapshot_digest": result.primary_run.final_snapshot_digest,
        "replay_final_snapshot_digest": result.replay_run.final_snapshot_digest,
        "digests_match": (
            result.primary_run.final_snapshot_digest
            == result.replay_run.final_snapshot_digest
        ),
        "primary_artifact_dir": primary_layout.root_dir.as_posix(),
        "replay_artifact_dir": replay_layout.root_dir.as_posix(),
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
