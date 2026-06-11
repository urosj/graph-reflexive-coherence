"""Run the Phase 7 representative GRC9V3 runtime lane."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.core import StepResult, digest_snapshot
from pygrc.models import GRC9V3


DEFAULT_OUTPUTS_ROOT = Path("outputs")
DEFAULT_EXPERIMENT_ID = "phase7-grc9v3-representative"
DEFAULT_FIXTURE_NAME = "appendix_e_cell_division"
DEFAULT_STEPS = 3


def build_appendix_e_cell_division_state() -> dict[str, Any]:
    """Build a deterministic Appendix E-style spark/division fixture.

    The pre-spark state has one saturated candidate node with a basin-like
    boundary. The boundary poles and bipolar expansion parameters bias the
    post-expansion reflexive loop toward two module sinks without directly
    creating those sinks as an event action.
    """

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    incidence: dict[str, list[int]] = {}
    node_states: dict[str, dict[str, Any]] = {}
    port_edges: dict[str, dict[str, Any]] = {}
    next_edge_id = 0

    def add_node(node_id: int, *, coherence: float, role: str) -> None:
        nodes.append({"node_id": node_id, "payload": {"role": role}})
        incidence[str(node_id)] = []
        node_states[str(node_id)] = {
            "coherence": coherence,
            "basin_mass": coherence,
            "basin_id": "root" if node_id == 0 else node_id,
            "depth": 0,
        }

    def add_edge(
        node_a: int,
        port_a: int,
        node_b: int,
        port_b: int,
        *,
        conductance: float,
        role: str,
    ) -> None:
        nonlocal next_edge_id
        edge_id = next_edge_id
        next_edge_id += 1
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": port_a - 1},
                "endpoint_b": {"node_id": node_b, "slot": port_b - 1},
                "payload": {"role": role},
            }
        )
        incidence[str(node_a)].append(edge_id)
        incidence[str(node_b)].append(edge_id)
        port_edges[str(edge_id)] = {
            "node_u": node_a,
            "port_u": port_a,
            "node_v": node_b,
            "port_v": port_b,
            "conductance": conductance,
            "flux_uv": 0.0,
        }

    add_node(0, coherence=9.0, role="saturated_parent_identity")
    for node_id in range(1, 10):
        add_node(node_id, coherence=9.0, role="pre_spark_boundary_member")
    add_node(10, coherence=9.0, role="prospective_daughter_support_a")
    add_node(11, coherence=9.0, role="prospective_daughter_support_b")

    for port_id in range(1, 10):
        add_edge(
            0,
            port_id,
            port_id,
            1,
            conductance=1.0,
            role="saturating_parent_boundary",
        )

    for support_port, node_id in enumerate((1, 2, 4, 5, 7, 8), start=1):
        add_edge(
            node_id,
            2,
            10,
            support_port,
            conductance=1.0,
            role="daughter_a_support",
        )
    for support_port, node_id in enumerate((3, 6, 9), start=1):
        add_edge(
            node_id,
            2,
            11,
            support_port,
            conductance=1.0,
            role="daughter_b_support",
        )

    return {
        "topology": {
            "nodes": nodes,
            "edges": edges,
            "incidence": incidence,
            "port_structure": {},
        },
        "next_node_id": 12,
        "next_edge_id": next_edge_id,
        "nodes": node_states,
        "port_edges": port_edges,
        "sink_set": [0],
        "basins": {"0": list(range(12))},
    }


def build_appendix_e_cell_division_params() -> dict[str, Any]:
    """Return deterministic GRC9V3 parameters for the Appendix E fixture."""

    return {
        "dt": 0.05,
        "evolution": {
            "alpha": 1e-12,
            "beta": 1e-12,
            "gamma": 1e-12,
            "eta": 1.0,
            "site_potential_params": {"mu": 0.0, "scale": 2.0},
            "eps_gradient": 1e-6,
            "eps_hessian": 1e-6,
            "eps_spark": 1e-6,
            "D_eff_target": 16,
            "w_bond": 0.05,
            "expansion_custom_weights": [0.5, 0.0, 0.5],
            "rng_seed": 0,
        },
        "constitutive_semantic_modes": {
            "expansion_distribution_mode": "custom",
        },
    }


def build_representative_hybrid_model() -> GRC9V3:
    """Construct the default Phase 7 representative GRC9V3 model."""

    return GRC9V3.from_state(
        state=build_appendix_e_cell_division_state(),
        params=build_appendix_e_cell_division_params(),
    )


def _event_to_mapping(event: Any) -> dict[str, Any]:
    return {
        "kind": event.kind,
        "step_index": event.step_index,
        "payload": dict(event.payload),
        "source_family": event.source_family,
    }


def _step_result_to_mapping(result: StepResult) -> dict[str, Any]:
    return {
        "step_index": result.step_index,
        "time": result.time,
        "events": [_event_to_mapping(event) for event in result.events],
        "observables": dict(result.observables),
        "bookkeeping": dict(result.bookkeeping),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _run_steps(
    model: GRC9V3,
    *,
    steps: int,
    checkpoint_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    step_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    if checkpoint_dir is not None:
        model.save(str(checkpoint_dir / "step-00000000.json"))

    for _ in range(steps):
        result = model.step()
        step_row = _step_result_to_mapping(result)
        step_rows.append(step_row)
        for event in result.events:
            event_rows.append(
                {
                    "step_index": result.step_index,
                    "time": result.time,
                    **_event_to_mapping(event),
                }
            )
        if checkpoint_dir is not None:
            model.save(str(checkpoint_dir / f"step-{result.step_index:08d}.json"))
    return step_rows, event_rows


def _build_run_summary(
    *,
    model: GRC9V3,
    steps: int,
    event_rows: list[dict[str, Any]],
    final_snapshot_path: Path,
) -> dict[str, Any]:
    state = model.get_state()
    event_counts = Counter(str(row["kind"]) for row in event_rows)
    stabilization = state.cached_quantities.get("last_child_basin_stabilization", {})
    if not isinstance(stabilization, dict):
        stabilization = {}
    expansion = state.cached_quantities.get("last_hybrid_expansion", {})
    if not isinstance(expansion, dict):
        expansion = {}
    return {
        "family": model.MODEL_FAMILY,
        "fixture_name": DEFAULT_FIXTURE_NAME,
        "steps": steps,
        "event_count": len(event_rows),
        "event_counts_by_kind": dict(sorted(event_counts.items())),
        "final_step_index": state.step_index,
        "final_time": state.time,
        "final_node_count": len(tuple(state.topology.iter_live_node_ids())),
        "final_edge_count": len(tuple(state.topology.iter_live_edge_ids())),
        "final_sink_set": sorted(state.sink_set),
        "final_hierarchy": dict(state.hierarchy),
        "hybrid_spark_completed_count": event_counts.get("hybrid_spark_completed", 0),
        "daughter_sink_count": int(stabilization.get("stable_child_basin_count", 0)),
        "daughter_sink_node_ids": list(stabilization.get("stabilized_child_node_ids", [])),
        "module_sink_node_ids": list(stabilization.get("module_sink_nodes", [])),
        "module_basin_mass": dict(stabilization.get("module_basin_mass", {})),
        "expansion_id": expansion.get("expansion_id"),
        "budget_target": state.budget_target,
        "final_budget": sum(node.coherence for node in state.nodes.values()),
        "final_snapshot_path": final_snapshot_path.as_posix(),
        "final_snapshot_digest": digest_snapshot(model.snapshot()),
    }


def run_representative_runtime(
    *,
    outputs_root: Path,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    steps: int = DEFAULT_STEPS,
) -> dict[str, Any]:
    """Run the representative lane, write artifacts, and return a report."""

    if steps <= 0:
        raise ValueError("steps must be > 0")

    run_dir = outputs_root / experiment_id / "grc9v3" / DEFAULT_FIXTURE_NAME
    checkpoint_dir = run_dir / "checkpoints"
    run_dir.mkdir(parents=True, exist_ok=True)

    model = build_representative_hybrid_model()
    initial_snapshot_path = run_dir / "initial_snapshot.json"
    final_snapshot_path = run_dir / "final_snapshot.json"
    model.save(str(initial_snapshot_path))
    step_rows, event_rows = _run_steps(
        model,
        steps=steps,
        checkpoint_dir=checkpoint_dir,
    )
    model.save(str(final_snapshot_path))
    run_summary = _build_run_summary(
        model=model,
        steps=steps,
        event_rows=event_rows,
        final_snapshot_path=final_snapshot_path,
    )

    replay_model = GRC9V3.load(str(initial_snapshot_path))
    replay_step_rows, replay_event_rows = _run_steps(replay_model, steps=steps)
    replay_digest = digest_snapshot(replay_model.snapshot())

    report = {
        "experiment_id": experiment_id,
        "fixture_name": DEFAULT_FIXTURE_NAME,
        "family": model.MODEL_FAMILY,
        "steps": steps,
        "run_dir": run_dir.as_posix(),
        "initial_snapshot_path": initial_snapshot_path.as_posix(),
        "final_snapshot_path": final_snapshot_path.as_posix(),
        "checkpoints_dir": checkpoint_dir.as_posix(),
        "steps_path": (run_dir / "steps.jsonl").as_posix(),
        "events_path": (run_dir / "events.jsonl").as_posix(),
        "run_summary_path": (run_dir / "run_summary.json").as_posix(),
        "run_summary": run_summary,
        "replay": {
            "step_rows_match": replay_step_rows == step_rows,
            "event_rows_match": replay_event_rows == event_rows,
            "final_snapshot_digest": replay_digest,
            "digests_match": replay_digest == run_summary["final_snapshot_digest"],
        },
    }

    _write_jsonl(run_dir / "steps.jsonl", step_rows)
    _write_jsonl(run_dir / "events.jsonl", event_rows)
    _write_json(run_dir / "run_summary.json", run_summary)
    _write_json(run_dir / "report.json", report)
    return report


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the Phase 7 representative GRC9V3 runtime lane."
    )
    parser.add_argument(
        "--outputs-root",
        default=str(DEFAULT_OUTPUTS_ROOT),
        help="Project-relative artifact root.",
    )
    parser.add_argument(
        "--experiment-id",
        default=DEFAULT_EXPERIMENT_ID,
        help="Experiment id written under the outputs root.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of deterministic GRC9V3 steps to run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    if args.steps <= 0:
        parser.error("--steps must be > 0")

    report = run_representative_runtime(
        outputs_root=Path(args.outputs_root),
        experiment_id=args.experiment_id,
        steps=args.steps,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
