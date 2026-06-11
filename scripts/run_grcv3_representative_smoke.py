"""Run the representative deterministic GRCV3 smoke lane and write artifacts.

The Phase 5 representative lane is intentionally small:

- intrinsic three-node chain
- `choice=disabled`
- spark suppressed through a large `eps_spark`
- deterministic save/load replay check

The script writes a compact evidence bundle under `outputs/<experiment_id>/grcv3`
so the lane can be rerun later without reconstructing it manually.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    WeightedGraphBackend,
    build_backend_selection,
    build_backend_selection_payload,
    digest_snapshot,
)
from pygrc.models import GRCV3


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_EXPERIMENT_ID = "phase5-grcv3-smoke"
DEFAULT_STEPS = 3


def _node_attributes(
    *,
    coherence: float,
    basin_id: str | int,
) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": [[1.0, 0.0], [0.0, 1.0]],
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": None,
        "depth": 0,
    }


def build_representative_model() -> GRCV3:
    graph = WeightedGraphBackend()
    left = graph.add_node({"kind": "representative"})
    center = graph.add_node({"kind": "representative"})
    right = graph.add_node({"kind": "representative"})
    edge_left = graph.add_edge(left, center, {"kind": "representative"})
    edge_right = graph.add_edge(center, right, {"kind": "representative"})

    model = GRCV3.from_state(
        state={
            "nodes": {
                str(left): _node_attributes(coherence=1.2, basin_id=left),
                str(center): _node_attributes(coherence=0.75, basin_id=center),
                str(right): _node_attributes(coherence=0.35, basin_id=right),
            },
            "base_conductance": {
                str(edge_left): 1.0,
                str(edge_right): 1.0,
            },
        },
        params={
            "dt": 0.05,
            "evolution": {
                "eps_gradient": 1e-3,
                "eps_hessian": 1e-3,
                "eps_spark": 1e6,
                "tau_split": 2.0,
            },
            "constitutive_semantic_modes": {
                BACKEND_SELECTIONS_KEY: build_backend_selection_payload(
                    [build_backend_selection(category="choice", name="disabled")]
                )
            },
        },
    )
    model.get_state().topology = graph
    return model


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the representative deterministic GRCV3 smoke lane."
    )
    parser.add_argument(
        "--outputs-root",
        default=str(DEFAULT_OUTPUTS_ROOT),
        help="Project-relative artifact root.",
    )
    parser.add_argument(
        "--experiment-id",
        default=DEFAULT_EXPERIMENT_ID,
        help="Experiment id written directly under the outputs root.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of deterministic GRCV3 steps to run.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    outputs_root = Path(args.outputs_root)
    run_dir = outputs_root / args.experiment_id / "grcv3"
    run_dir.mkdir(parents=True, exist_ok=True)

    model = build_representative_model()
    step_rows: list[dict[str, object]] = []
    for _ in range(args.steps):
        result = model.step()
        step_rows.append(
            {
                "step_index": result.step_index,
                "time": result.time,
                "events": [
                    {
                        "kind": event.kind,
                        "step_index": event.step_index,
                        "payload": dict(event.payload),
                        "source_family": event.source_family,
                    }
                    for event in result.events
                ],
                "observables": dict(result.observables),
                "bookkeeping": dict(result.bookkeeping),
            }
        )

    final_snapshot_path = run_dir / "final_snapshot.json"
    model.save(str(final_snapshot_path))

    report = {
        "experiment_id": args.experiment_id,
        "family": "GRCV3",
        "steps": args.steps,
        "step_rows": step_rows,
        "final_snapshot_digest": digest_snapshot(model.snapshot()),
        "final_snapshot_path": final_snapshot_path.as_posix(),
    }
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(f"experiment_id={args.experiment_id}")
    print("family=GRCV3")
    print(f"steps={args.steps}")
    print(f"run_dir={run_dir.as_posix()}")
    print(f"final_snapshot={final_snapshot_path.as_posix()}")
    print(f"report={report_path.as_posix()}")
    print(f"final_snapshot_digest={report['final_snapshot_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
