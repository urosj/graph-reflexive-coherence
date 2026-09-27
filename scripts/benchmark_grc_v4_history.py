"""Time an evolving V4 fixture without projecting its entire history each step.

Run from the repository root with PYTHONPATH=src:.:tests. Setup, request
construction and checkpoint snapshots are outside step timers. Optional profiling
covers only the last step and is excluded from ordinary timing totals.
"""

import argparse
import cProfile
import hashlib
import json
import time
from pathlib import Path

from pygrc.models.grc_v4_codec import canonical_json_bytes
from tests.models.test_grc_v4_generic_lifecycle import FAMILIES, fixture, model
from tests.models.test_grc_v4_lifecycle import request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--family", choices=FAMILIES, default="A_OS")
    parser.add_argument("--profile-last", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("--steps must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    inputs, _ = fixture(args.family)
    graph = inputs.geometry.reference.graph
    owner = model(args.family)
    seconds = []
    checkpoints = {}
    profile_seconds = None
    for index in range(args.steps):
        command = request(inputs.dt, f"long-comparison-{index}")
        profiler = cProfile.Profile() if args.profile_last and index == args.steps - 1 else None
        started = time.perf_counter()
        result = (owner.step_v4_input(command) if profiler is None
                  else profiler.runcall(owner.step_v4_input, command))
        elapsed = time.perf_counter() - started
        if not result.committed:
            raise RuntimeError(f"step {index + 1} rejected: {result.failure}")
        if profiler is None:
            seconds.append(elapsed)
        else:
            profile_seconds = elapsed
            profiler.dump_stats(str(args.output.with_suffix(".prof")))
        if index + 1 in (50, args.steps):
            encoded = canonical_json_bytes(owner.snapshot())
            checkpoints[str(index + 1)] = {
                "ordinary_seconds": sum(seconds),
                "snapshot_sha256": hashlib.sha256(encoded).hexdigest(),
                "snapshot_bytes": len(encoded),
            }
        report = {
            "family": args.family,
            "nodes": len(graph.live_node_ids),
            "edges": len(graph.oriented_edges),
            "committed_steps": index + 1,
            "seconds": seconds,
            "ordinary_total_seconds": sum(seconds),
            "profiled_last_seconds": profile_seconds,
            "checkpoints": checkpoints,
            "method": "evolving public steps; setup, requests and checkpoint projections excluded; profiled last step excluded from ordinary totals",
        }
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        if (index + 1) % 5 == 0 or index == args.steps - 1:
            print(json.dumps({"step": index + 1, "ordinary_seconds": round(sum(seconds), 3), "last_step_seconds": round(elapsed, 3)}), flush=True)


if __name__ == "__main__":
    main()
