"""Demonstrate column coarse-graining and Split for GRC9 and GRC9V3."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9, GRC9V3


def _topology_from_connections(
    connections: list[tuple[int, int, int, int, int]],
) -> dict[str, object]:
    node_ids: set[int] = set()
    incidence: dict[str, list[int]] = {}
    edges: list[dict[str, object]] = []
    for edge_id, node_a, slot_a, node_b, slot_b in connections:
        node_ids.update({node_a, node_b})
        incidence.setdefault(str(node_a), []).append(edge_id)
        incidence.setdefault(str(node_b), []).append(edge_id)
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": slot_a},
                "endpoint_b": {"node_id": node_b, "slot": slot_b},
                "payload": {},
            }
        )
    return {
        "nodes": [{"node_id": node_id, "payload": {}} for node_id in sorted(node_ids)],
        "edges": sorted(edges, key=lambda edge: int(edge["edge_id"])),
        "incidence": {
            node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
        },
        "port_structure": {},
    }


def _port_edge_payload(
    *,
    node_u: int,
    port_u: int,
    node_v: int,
    port_v: int,
    conductance: float,
    flux_uv: float = 0.0,
) -> dict[str, float | int]:
    return {
        "node_u": node_u,
        "port_u": port_u,
        "node_v": node_v,
        "port_v": port_v,
        "conductance": conductance,
        "flux_uv": flux_uv,
    }


def _grc9_params() -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1.0,
            "beta": 1.0,
            "gamma": 1.0,
            "delta": 1.0,
            "eta": 1.0,
            "lambda_birth": 0.0,
            "alpha_seed": 0.1,
            "rng_seed": 0,
            "w_bond": 1.0,
        },
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "curvature_backend": "none",
            "boundary_mode": "prune",
            "expansion_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


def _grc9v3_params() -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1e-12,
            "beta": 1e-12,
            "gamma": 1e-12,
            "eta": 1.0,
            "kappa_c": 1.0,
            "v0": 1.0,
            "rho": 1.0,
            "eps_tau": 1e-12,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
            "eps_gradient": 0.5,
            "eps_hessian": 0.1,
        },
        "constitutive_semantic_modes": {
            "edge_label_selection": "all",
        },
    }


def _grc9_demo() -> dict[str, Any]:
    model = GRC9.from_state(
        state={
            "topology": _topology_from_connections(
                [
                    (0, 0, 0, 1, 0),
                    (1, 0, 1, 2, 0),
                    (2, 0, 3, 3, 0),
                    (3, 0, 4, 4, 0),
                ]
            ),
            "node_coherence": {
                "0": 1.0,
                "1": 1.0,
                "2": 1.0,
                "3": 1.0,
                "4": 1.0,
            },
            "port_edges": {
                "0": _port_edge_payload(
                    node_u=0,
                    port_u=1,
                    node_v=1,
                    port_v=1,
                    conductance=2.0,
                ),
                "1": _port_edge_payload(
                    node_u=0,
                    port_u=2,
                    node_v=2,
                    port_v=1,
                    conductance=1.0,
                ),
                "2": _port_edge_payload(
                    node_u=0,
                    port_u=4,
                    node_v=3,
                    port_v=1,
                    conductance=3.0,
                ),
                "3": _port_edge_payload(
                    node_u=0,
                    port_u=5,
                    node_v=4,
                    port_v=1,
                    conductance=6.0,
                ),
            },
        },
        params=_grc9_params(),
    )
    coarse_state = model.coarse_grain_columns("conductance")
    split_state = model.split_columns(coarse_state)
    reconstructed_node_zero = split_state["port_field"]["0"]
    expected_node_zero = {
        "1": 2.0,
        "2": 1.0,
        "3": 0.0,
        "4": 3.0,
        "5": 6.0,
        "6": 0.0,
        "7": 0.0,
        "8": 0.0,
        "9": 0.0,
    }
    return {
        "family": "grc9",
        "field": "conductance",
        "meaning": "mechanical bond strength pooled by GRC9 port column",
        "coarse_mode": coarse_state["mode"],
        "node_0_column_totals": coarse_state["by_node"]["0"]["column_totals"],
        "node_0_profiles": coarse_state["by_node"]["0"]["profiles"],
        "split_exact_for_node_0": reconstructed_node_zero == expected_node_zero,
        "reconstructed_node_0": reconstructed_node_zero,
    }


def _grc9v3_demo() -> dict[str, Any]:
    model = GRC9V3.from_state(
        state={
            "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
            "nodes": {
                "0": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 0},
                "1": {"coherence": 3.0, "basin_mass": 3.0, "basin_id": 1},
            },
            "port_edges": {
                "0": _port_edge_payload(
                    node_u=0,
                    port_u=1,
                    node_v=1,
                    port_v=1,
                    conductance=0.5,
                )
            },
        },
        params=_grc9v3_params(),
    )
    model.rebuild_differential_state()
    model.rebuild_transport_state()

    coarse_state = model.coarse_grain_columns("signed_flux")
    split_state = model.split_columns(coarse_state)
    state = model.get_state()
    expected_node_zero = {
        "1": state.port_edges[0].flux_uv,
        "2": 0.0,
        "3": 0.0,
        "4": 0.0,
        "5": 0.0,
        "6": 0.0,
        "7": 0.0,
        "8": 0.0,
        "9": 0.0,
    }
    return {
        "family": "grc9v3",
        "field": "signed_flux",
        "meaning": "hybrid transport direction on the GRC9 port chart",
        "coarse_mode": coarse_state["mode"],
        "node_0_positive_column_totals": coarse_state["positive"]["by_node"]["0"][
            "column_totals"
        ],
        "node_0_negative_column_totals": coarse_state["negative"]["by_node"]["0"][
            "column_totals"
        ],
        "split_exact_for_node_0": split_state["port_field"]["0"] == expected_node_zero,
        "reconstructed_node_0": split_state["port_field"]["0"],
        "coarse_cache_keys": sorted(state.coarse_cache),
        "coarse_cache_refresh_mode": state.cached_quantities.get(
            "coarse_cache_refresh_mode"
        ),
    }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show exact GRC9/GRC9V3 column coarse-graining examples."
    )
    parser.add_argument(
        "--family",
        choices=("all", "grc9", "grc9v3"),
        default="all",
        help="Select which example to print.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    examples = []
    if args.family in {"all", "grc9"}:
        examples.append(_grc9_demo())
    if args.family in {"all", "grc9v3"}:
        examples.append(_grc9v3_demo())
    print(json.dumps({"examples": examples}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
