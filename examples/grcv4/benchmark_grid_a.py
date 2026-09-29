"""Count numerical primitive reuse on an A grid through strict public steps.

This checkout benchmark observes ordinary fact lookup. With reuse disabled it
discards the result, forcing the requested primitive to run again. It changes
no declaration, solver policy, residual check or publication validation.
"""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

from examples.grcv4.grid_realizations_a import REALIZATIONS, run
from examples.grcv4.grid_transport import DEFAULT_COLS, DEFAULT_ROWS
from pygrc.models.grc_v4_linear import _MatrixFacts


def run_benchmark(
    realization, steps=5, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, *, reuse=False
):
    ordinary_find = _MatrixFacts.find
    last_cache = None
    scopes = []

    def observe_fact(cache, matrix, limit=None):
        nonlocal last_cache
        if cache is not last_cache:
            # Retain only the latest instance, avoiding id-keyed bookkeeping.
            last_cache = cache
            scopes.append(
                {
                    "inverse_requests": 0,
                    "inverse_hits": 0,
                    "inverse_misses": 0,
                    "conditioning_requests": 0,
                    "conditioning_hits": 0,
                    "conditioning_misses": 0,
                }
            )
        fact = ordinary_find(cache, matrix, limit)
        kind = "inverse" if limit is None else "conditioning"
        scopes[-1][f"{kind}_requests"] += 1
        outcome = "hits" if fact is not None else "misses"
        scopes[-1][f"{kind}_{outcome}"] += 1
        return fact if reuse else None

    with patch.object(_MatrixFacts, "find", observe_fact):
        report = run(realization, steps, rows, cols)
    report.update(
        matrix_fact_reuse="enabled" if reuse else "lookup_disabled_control",
        matrix_fact_scopes=scopes,
        counter_method=(
            "A light lookup counter follows the ordinary bounded LRU lookup. "
            "Enabled runs return its result; disabled controls discard it, forcing "
            "the requested exact inverse or conditioning proof again. "
            "Counters cover cache-scoped public steps; unscoped declaration and "
            "owner setup proofs are outside these lookup counts."
        ),
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--realization", choices=REALIZATIONS, required=True)
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS)
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--reuse", action="store_true", help="Observe enabled reuse.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.steps < 1 or args.rows < 2 or args.cols < 2:
        parser.error("steps must be positive and each grid dimension at least two")
    report = run_benchmark(
        args.realization, args.steps, args.rows, args.cols, reuse=args.reuse
    )
    name = args.realization.lower().replace("+", "_")
    suffix = "primitive_reuse" if args.reuse else "primitive_reuse_disabled"
    output = args.output or (
        Path(__file__).parent / "results" /
        f"grid_transport_a_{name}_{args.rows}x{args.cols}_{args.steps}_{suffix}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        key: report[key] for key in (
            "family", "total_step_seconds", "mean_step_seconds",
            "example_total_wall_seconds", "matrix_fact_scopes",
        )
    }, indent=2))
    print(f"Benchmark report: {output}")


if __name__ == "__main__":
    main()
