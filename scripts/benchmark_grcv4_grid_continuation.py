"""Observe bounded numerical continuation on strict public PC/CI+PC/RG2b grid steps.

The disabled control keeps ordinary operation-local reuse and discards only
facts selected for the next publication. There is no production mode switch.
"""

import argparse
import hashlib
import json
import subprocess
from contextlib import ExitStack
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

from examples.grcv4.grid_transport import DEFAULT_COLS, DEFAULT_ROWS
from pygrc.models import _grc_v4_matrix as arithmetic
from pygrc.models import grc_v4_ci as ci
from pygrc.models import grc_v4_numerics as numerical
from pygrc.models import grc_v4_pc as pc
from pygrc.models import grc_v4_rg2b as rg
from pygrc.models import grc_v4_rg2b_graph as rg_graph
from pygrc.models.grc_v4_codec import _OPERATION_CONTEXT
from pygrc.models.grc_v4_linear import _MatrixContinuation, _MatrixFacts
from scripts.benchmark_grcv4_grid_a import run_benchmark


def run(steps=5, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, *, continuation=True, realization="PC", candidate="A"):
    ordinary_retain = _MatrixFacts.retain
    selected = []
    computations = {}
    checks = {}

    def retain(store, reset, current, limit):
        facts = ordinary_retain(store, reset, current, limit)
        retained = facts if continuation else _MatrixContinuation()
        selected.append(len(retained.facts))
        return retained

    def observe(function, kind, *, matrix=False):
        def measured(*args, **kwargs):
            if _OPERATION_CONTEXT.get() is None:
                return function(*args, **kwargs)
            if matrix:
                coefficients = args[0]
                key = f"{kind}:{len(coefficients)}x{len(coefficients[0])}"
                entry = computations.setdefault(key, {"calls": 0, "seconds": 0.0})
                started = perf_counter()
                try:
                    return function(*args, **kwargs)
                finally:
                    entry["calls"] += 1
                    entry["seconds"] += perf_counter() - started
            checks[kind] = checks.get(kind, 0) + 1
            return function(*args, **kwargs)
        return measured

    with ExitStack() as stack:
        stack.enter_context(patch.object(_MatrixFacts, "retain", retain))
        for owner, name, kind, matrix in (
            (arithmetic, "inverse", "inverse", True),
            (arithmetic, "condition_bound", "conditioning", True),
            (numerical, "solve", "certified_solves", False),
            (numerical, "residual_pass", "residual_checks", False),
            (numerical, "_condition_certificate", "fresh_condition_certificates", False),
            (pc, "_base_state", "chart_membership_checks", False),
            (ci.CIContractionCertificate, "__post_init__", "ci_contraction_certificates", False),
            (ci.CITrial, "__post_init__", "ci_trial_residuals", False),
            (pc.PCEnvelopeCertificate, "__post_init__", "pc_envelope_certificates", False),
            (pc, "scalar_zoh", "pc_carrier_writes", False),
            (rg.RG2bCertificate, "__post_init__", "whole_chart_certificates", False),
            (rg_graph, "section", "graph_section_evaluations", False),
            (rg_graph, "native_bridge", "native_arithmetic_bridges", False),
        ):
            original = getattr(owner, name)
            stack.enter_context(patch.object(
                owner, name, observe(original, kind, matrix=matrix)
            ))
        report = run_benchmark(
            realization, steps, rows, cols, reuse=True, candidate=candidate
        )
    sources = (
        "src/pygrc/models/grc_v4_linear.py",
        "src/pygrc/models/grc_v4_numerics.py",
        "src/pygrc/models/_grc_v4_matrix.py",
        "src/pygrc/models/grc_v4_codec.py",
        "src/pygrc/models/grc_v4_lifecycle.py",
        "src/pygrc/models/grc_v4_pc.py",
        "src/pygrc/models/grc_v4_ci.py",
        "src/pygrc/models/grc_v4_rg2b.py",
        "src/pygrc/models/grc_v4_rg2b_graph.py",
        "src/pygrc/models/grc_v4_candidate_a.py",
        "src/pygrc/models/grc_v4_candidate_c.py",
    )
    report.update(
        matrix_continuation="enabled" if continuation else "disabled_control",
        retained_fact_counts=selected,
        numerical_computations=computations,
        fresh_checks=checks,
        runtime_base_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        runtime_source_sha256={
            name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in sources
        },
        continuation_counter_method=(
            "Light timers count scoped exact primitive computations; checks count "
            "gateway invocations. Unscoped setup is excluded. Both controls use "
            "the same observers and retain ordinary within-operation reuse."
        ),
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", choices=("A", "C"), default="A")
    parser.add_argument("--realization", choices=("PC", "CI+PC", "RG2b"), default="PC")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS)
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--disable-continuation", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.steps < 1 or args.rows < 2 or args.cols < 2:
        parser.error("steps must be positive and each grid dimension at least two")
    report = run(
        args.steps, args.rows, args.cols, continuation=not args.disable_continuation,
        realization=args.realization, candidate=args.candidate
    )
    suffix = "disabled" if args.disable_continuation else "enabled"
    name = args.realization.lower().replace("+", "_")
    output = args.output or (
        Path(__file__).resolve().parents[1] / "implementation/evidence/grcv4-performance/runs" /
        f"grid_transport_{args.candidate.lower()}_{name}_{args.rows}x{args.cols}_{args.steps}_continuation_{suffix}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        key: report[key] for key in (
            "matrix_continuation", "total_step_seconds", "retained_fact_counts",
            "numerical_computations", "fresh_checks",
        )
    }, indent=2))
    print(f"Benchmark report: {output}")


if __name__ == "__main__":
    main()
