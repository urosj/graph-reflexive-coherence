"""A closed grid with resource transport and relaxing A_OS edge history.

Checkout-only declaration construction follows the other examples in this folder.
Evolution uses the strict public GRCV4 lifecycle, with receipts and result capture.
Run with PYTHONPATH=src:.:tests from the repository root.
"""

import argparse
import hashlib
import json
import math
import time
from fractions import Fraction
from pathlib import Path

from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_v4_candidate_a import current_fixture

DEFAULT_ROWS = 4
DEFAULT_COLS = 5
DT = 2**-6


def make_inputs(rows=DEFAULT_ROWS, cols=DEFAULT_COLS, *, resource_span=None):
    """Local couplings on a physical 2-D grid, with a nonuniform closed budget."""
    nodes = tuple(f"r{row}c{col}" for row in range(rows) for col in range(cols))
    positions = tuple(
        (float(col), float(row)) for row in range(rows) for col in range(cols)
    )
    edges = []
    weights = {}
    for row in range(rows):
        for col in range(cols):
            node = f"r{row}c{col}"
            if col + 1 < cols:
                edge = f"h{row}_{col}"
                edges.append(OrientedEdge(edge, node, f"r{row}c{col + 1}"))
                weights[edge] = 1.0 + row / 8
            if row + 1 < rows:
                edge = f"v{row}_{col}"
                edges.append(OrientedEdge(edge, node, f"r{row + 1}c{col}"))
                weights[edge] = 1.125 + col / 16
    graph = GRCV4Graph(nodes, tuple(edges))
    resource = [
        2.0 + ((cols - 1) / 2 - col) / 8 + ((rows - 1) / 2 - row) / 16
        for row in range(rows)
        for col in range(cols)
    ]
    upper_middle_row = (rows - 1) // 2
    middle_col = cols // 2
    resource[upper_middle_row * cols + middle_col] += 0.25
    resource[(upper_middle_row + 1) * cols + middle_col] -= 0.25
    if resource_span is not None:
        spread = max(abs(c - 2.0) for c in resource)
        factor = min(1.0, resource_span / spread)
        resource = [2.0 + factor * (c - 2.0) for c in resource]
    history = tuple(1.5 + (index % 5) / 16 for index in range(len(edges)))
    return current_fixture(
        graph=graph,
        dimension=2,
        positions=positions,
        weights=weights,
        ridge=1.0,
        C=tuple(resource),
        W=history,
        dt=DT,
        eta=0.125,
        kappa_c=0.25,
        kappa_Ah=0.125,
        alpha=0.02,
        beta=0.1,
        gamma=0.05,
        chi_A=0.25,
        zeta_A=0.25,
        tau_A=0.125,
        changes={
            "geometry": {"kappa_H": 0.09375},
            "realization": {"tolerance": 1e-8},
            "charge": {"absolute_tolerance": 1e-11},
        },
    )


def run(steps, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
    started = time.perf_counter()
    inputs, backend = make_inputs(rows, cols)
    return run_inputs(inputs, backend, steps, rows, cols, started=started)


def run_inputs(inputs, backend, steps, rows, cols, *, started=None):
    """Measure an evolving grid through the strict public lifecycle."""
    if started is None:
        started = time.perf_counter()
    dt = inputs.dt
    family = inputs.geometry.reference.profile.identity_payload.profile_family_id
    request_prefix = (
        "grid-transport" if family == "A_OS" else f"grid-transport-{family}"
    )
    owner = GRCV4(inputs, differential_reference=backend)
    setup_seconds = time.perf_counter() - started
    initial = inputs.current
    initial_inputs = inputs.to_payload()
    backend_payload = backend.to_payload()
    step_records = []
    simulation_started = time.perf_counter()
    for index in range(steps):
        previous_time = owner.state.lifecycle.time
        command = GRCV4StepRequestInput(
            "grcv4-step-request-input-v1",
            f"{request_prefix}-{index}",
            dt,
            FrozenJSONMap({}),
        )
        step_started = time.perf_counter()
        result = owner.step_v4_input(command)
        elapsed = time.perf_counter() - step_started
        if not result.committed:
            raise RuntimeError(f"step {index + 1} rejected: {result.failure}")
        state = owner.state.lifecycle
        current = state.current
        charge = math.fsum(current.C)
        if (
            not math.isclose(charge, inputs.Q_target, rel_tol=0, abs_tol=1e-11)
            or any(not math.isfinite(value) or value < 0 for value in current.C)
            or current.W_A is None
            or any(not math.isfinite(value) or value <= 0 for value in current.W_A)
            or state.step_index != index + 1
            or state.time != float(Fraction(previous_time) + Fraction(dt))
        ):
            raise RuntimeError("committed grid step violates example invariants")
        step_records.append(
            {
                "step": index + 1,
                "seconds": elapsed,
                "physical_time": state.time,
                "resource": list(current.C),
                "W_A": list(current.W_A),
                "Z_4": None if current.Z_4 is None else list(current.Z_4),
                "total_resource": charge,
                "receipt_count": len(state.receipt_ledger),
            }
        )
        print(
            json.dumps(
                {
                    "step": index + 1,
                    "seconds": round(elapsed, 6),
                    "total_resource": charge,
                }
            ),
            flush=True,
        )
    simulation_seconds = time.perf_counter() - simulation_started
    snapshot_started = time.perf_counter()
    snapshot_bytes = canonical_json_bytes(owner.snapshot())
    snapshot_seconds = time.perf_counter() - snapshot_started
    total = sum(record["seconds"] for record in step_records)
    final = owner.state.lifecycle.current
    return {
        "example": f"closed_{rows}x{cols}_grid_transport",
        "grid_rows": rows,
        "grid_cols": cols,
        "family": family,
        "nodes": len(inputs.geometry.reference.graph.live_node_ids),
        "edges": len(inputs.geometry.reference.graph.oriented_edges),
        "steps": steps,
        "dt": dt,
        "setup_seconds": setup_seconds,
        "total_step_seconds": total,
        "mean_step_seconds": total / steps,
        "simulation_wall_seconds": simulation_seconds,
        "final_snapshot_seconds": snapshot_seconds,
        "work_wall_seconds": time.perf_counter() - started,
        "initial_inputs": initial_inputs,
        "differential_reference": backend_payload,
        "step_records": step_records,
        "max_resource_change": max(
            abs(a - b) for a, b in zip(initial.C, final.C, strict=True)
        ),
        "max_carrier_magnitude": None if final.Z_4 is None else max(map(abs, final.Z_4)),
        "max_history_change": max(
            abs(a - b) for a, b in zip(initial.W_A, final.W_A, strict=True)
        ),
        "final_snapshot_sha256": hashlib.sha256(snapshot_bytes).hexdigest(),
        "final_snapshot_bytes": len(snapshot_bytes),
        "timing_method": (
            "Ordinary strict public evolving steps, no profiler. Step timers include "
            "public admission, numerical stages, validation and result/history capture. "
            "Setup, request construction, diagnostics, progress output and final snapshot "
            "are outside step timers. Simulation wall includes loop overhead; work wall "
            "includes setup and snapshot but excludes imports and final report writing."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("--steps must be positive")
    if args.rows < 2 or args.cols < 2:
        parser.error("--rows and --cols must each be at least 2")
    report = run(args.steps, args.rows, args.cols)
    default_name = (
        f"grid_transport_{args.steps}.json"
        if (args.rows, args.cols) == (DEFAULT_ROWS, DEFAULT_COLS)
        else f"grid_transport_{args.rows}x{args.cols}_{args.steps}.json"
    )
    output = args.output or Path(__file__).parent / "results" / default_name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                key: report[key]
                for key in (
                    "nodes",
                    "edges",
                    "steps",
                    "setup_seconds",
                    "total_step_seconds",
                    "mean_step_seconds",
                    "work_wall_seconds",
                    "max_resource_change",
                    "max_history_change",
                )
            },
            indent=2,
        )
    )
    print(f"Report: {output}")


if __name__ == "__main__":
    main()
