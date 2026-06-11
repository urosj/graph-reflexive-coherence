#!/usr/bin/env python3
"""Manual GRCV3 spark probes that bypass landscape projection."""

from __future__ import annotations

import argparse
from typing import Any

from pygrc.core import WeightedGraphBackend
from pygrc.models import GRCV3


def _attributes(
    *,
    coherence: float,
    hessian: list[list[float]],
    basin_id: str | int,
    parent_id: str | int | None = None,
    depth: int = 0,
) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": hessian,
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": parent_id,
        "depth": depth,
    }


def build_single_node_probe() -> GRCV3:
    graph = WeightedGraphBackend()
    parent = graph.add_node({"label": "spark_parent"})

    model = GRCV3.from_state(
        state={
            "nodes": {
                str(parent): _attributes(
                    coherence=1.2,
                    hessian=[[0.0001, 0.0], [0.0, 2.0]],
                    basin_id=parent,
                )
            },
            "hessian_sign": 1,
        },
        params={"dt": 0.1},
    )
    model.get_state().topology = graph
    model.rebuild_identity_state()
    return model


def build_three_node_probe() -> GRCV3:
    graph = WeightedGraphBackend()
    left = graph.add_node({"label": "left"})
    center = graph.add_node({"label": "candidate_center"})
    right = graph.add_node({"label": "right"})
    edge_left = graph.add_edge(left, center, {"role": "support"})
    edge_right = graph.add_edge(center, right, {"role": "support"})

    model = GRCV3.from_state(
        state={
            "nodes": {
                str(left): _attributes(
                    coherence=0.0,
                    hessian=[[2.0, 0.0], [0.0, 2.0]],
                    basin_id=left,
                ),
                str(center): _attributes(
                    coherence=0.0,
                    hessian=[[0.0001, 0.0], [0.0, 2.0]],
                    basin_id=center,
                ),
                str(right): _attributes(
                    coherence=0.0,
                    hessian=[[2.0, 0.0], [0.0, 2.0]],
                    basin_id=right,
                ),
            },
            "base_conductance": {
                str(edge_left): 1.0,
                str(edge_right): 1.0,
            },
            "hessian_sign": 1,
        },
        params={
            "dt": 0.1,
            "constitutive_semantic_modes": {
                "backend_selections": {
                    "spark": {
                        "name": "signed_hessian_plus_attractor_delta",
                        "params": {"min_child_basins": 3},
                    }
                }
            },
        },
    )
    model.get_state().topology = graph
    model.rebuild_identity_state()
    return model


def summarize_events(events: list[Any]) -> None:
    print(f"event_count={len(events)}")
    for event in events:
        print(f"  kind={event.kind} step={event.step_index} payload={event.payload}")


def summarize_state(model: GRCV3) -> None:
    state = model.get_state()
    print(
        "state "
        f"nodes={len(tuple(state.topology.iter_live_node_ids()))} "
        f"edges={len(tuple(state.topology.iter_live_edge_ids()))} "
        f"split_registry_size={len(state.cached_quantities.get('split_registry', {}))}"
    )
    for node_id in sorted(state.topology.iter_live_node_ids()):
        attrs = state.nodes[node_id]
        print(
            "  "
            f"node={node_id} coherence={attrs.coherence} basin_id={attrs.basin_id} "
            f"parent_id={attrs.parent_id} depth={attrs.depth} hessian={attrs.hessian}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run manual GRCV3 spark probes.")
    parser.add_argument(
        "--probe",
        choices=("single-node", "three-node"),
        default="single-node",
        help="Which manual spark fixture to run.",
    )
    parser.add_argument(
        "--advance",
        type=int,
        default=0,
        help="Number of split-progress advancement steps to run after spark detection.",
    )
    args = parser.parse_args()

    model = build_single_node_probe() if args.probe == "single-node" else build_three_node_probe()

    print(f"probe={args.probe}")
    summarize_state(model)

    candidates = model.detect_spark_candidates()
    print("candidates")
    summarize_events(candidates)

    events = model.rebuild_spark_state()
    print("after_rebuild_spark_state")
    summarize_events(events)
    summarize_state(model)

    for index in range(args.advance):
        progress_events = model.advance_split_state()
        print(f"after_advance_{index + 1}")
        summarize_events(progress_events)
        summarize_state(model)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
