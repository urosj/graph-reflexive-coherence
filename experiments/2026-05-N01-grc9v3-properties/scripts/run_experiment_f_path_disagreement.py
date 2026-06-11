"""Experiment F: path disagreement across GRC9V3 edge-label criteria."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.models import GRC9V3
from pygrc.models.grc_9_ports import port_id_to_slot

from grc9v3_fixture_harness import (
    ARTIFACT_SCHEMA_VERSION,
    LANE_ID,
    PORT_IDS,
    artifact_entry_points,
    blocked_observations_schema,
    comparison_report_schema,
    degree_preserving_random_relabel_map,
    run_id_convention,
    runtime_assumptions,
)


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ID = "experiment_f_path_disagreement"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_experiment_f_path_disagreement.py"
)
START_NODE_ID = 0
END_NODE_ID = 9
PATH_TIE_BREAK = "prefer fewer edges, then lexicographic edge-id tuple"
TEMPORAL_DELAY_MODE = "transport_ratio_from_fixed_labels"


BASE_EDGES = (
    {
        "edge_id": 0,
        "corridor": "A_metric_short",
        "node_u": 0,
        "port_u": 1,
        "node_v": 1,
        "port_v": 1,
        "geometric_length": 1.0,
        "signed_flux": 1.0,
    },
    {
        "edge_id": 1,
        "corridor": "A_metric_short",
        "node_u": 1,
        "port_u": 2,
        "node_v": 9,
        "port_v": 1,
        "geometric_length": 1.0,
        "signed_flux": 1.0,
    },
    {
        "edge_id": 2,
        "corridor": "B_delay_fast",
        "node_u": 0,
        "port_u": 2,
        "node_v": 2,
        "port_v": 1,
        "geometric_length": 2.0,
        "signed_flux": 10.0,
    },
    {
        "edge_id": 3,
        "corridor": "B_delay_fast",
        "node_u": 2,
        "port_u": 2,
        "node_v": 9,
        "port_v": 2,
        "geometric_length": 2.0,
        "signed_flux": 10.0,
    },
    {
        "edge_id": 4,
        "corridor": "C_flux_strong",
        "node_u": 0,
        "port_u": 3,
        "node_v": 3,
        "port_v": 1,
        "geometric_length": 4.0,
        "signed_flux": 20.0,
    },
    {
        "edge_id": 5,
        "corridor": "C_flux_strong",
        "node_u": 3,
        "port_u": 2,
        "node_v": 9,
        "port_v": 3,
        "geometric_length": 4.0,
        "signed_flux": 20.0,
    },
)


def _git_value(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
            cwd=EXPERIMENT_ROOT.parents[1],
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _params(seed: int) -> dict[str, Any]:
    return {
        "dt": 0.1,
        "evolution": {
            "rng_seed": seed,
            "v0": 1.0,
            "rho": 1.0,
            "eps_tau": 1e-12,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
        },
        "constitutive_semantic_modes": {
            "edge_label_selection": "all",
            "hessian_backend": "row_basis_diagonal",
            "boundary_mode": "prune",
        },
    }


def _remap_port(port_id: int, port_map: dict[int, int]) -> int:
    return int(port_map.get(port_id, port_id))


def _variant_edges(
    *,
    variant_id: str,
    port_map: dict[int, int],
) -> list[dict[str, Any]]:
    edges = []
    for edge in BASE_EDGES:
        geometric_length = float(edge["geometric_length"])
        signed_flux = float(edge["signed_flux"])
        temporal_delay: float | None = None
        if variant_id == "equalized_geometric_labels":
            geometric_length = 1.0
        elif variant_id == "equalized_temporal_labels":
            temporal_delay = 1.0
        elif variant_id == "equalized_flux_labels":
            signed_flux = 1.0
        elif variant_id == "all_equalized_labels":
            geometric_length = 1.0
            signed_flux = 1.0
        elif variant_id != "base_disagreement":
            raise ValueError(f"unknown variant {variant_id!r}")
        edges.append(
            {
                **edge,
                "port_u": _remap_port(int(edge["port_u"]), port_map),
                "port_v": _remap_port(int(edge["port_v"]), port_map),
                "geometric_length": geometric_length,
                "signed_flux": signed_flux,
                "temporal_delay": (
                    temporal_delay
                    if temporal_delay is not None
                    else geometric_length / (1.0 + abs(signed_flux) + 1e-12)
                ),
            }
        )
    return edges


def _topology(edges: list[dict[str, Any]]) -> dict[str, Any]:
    node_ids = {START_NODE_ID, END_NODE_ID}
    incidence: dict[str, list[int]] = {}
    topology_edges: list[dict[str, Any]] = []
    for edge in edges:
        edge_id = int(edge["edge_id"])
        node_u = int(edge["node_u"])
        node_v = int(edge["node_v"])
        node_ids.update({node_u, node_v})
        incidence.setdefault(str(node_u), []).append(edge_id)
        incidence.setdefault(str(node_v), []).append(edge_id)
        topology_edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {
                    "node_id": node_u,
                    "slot": port_id_to_slot(int(edge["port_u"])),
                },
                "endpoint_b": {
                    "node_id": node_v,
                    "slot": port_id_to_slot(int(edge["port_v"])),
                },
                "payload": {"corridor": str(edge["corridor"])},
            }
        )
    return {
        "nodes": [{"node_id": node_id, "payload": {}} for node_id in sorted(node_ids)],
        "edges": sorted(topology_edges, key=lambda item: int(item["edge_id"])),
        "incidence": {
            node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
        },
        "port_structure": {},
    }


def fixture_state(
    *,
    variant_id: str,
    port_map: dict[int, int],
) -> dict[str, Any]:
    edges = _variant_edges(variant_id=variant_id, port_map=port_map)
    node_ids = sorted(
        {int(edge["node_u"]) for edge in edges}
        | {int(edge["node_v"]) for edge in edges}
    )
    nodes = {
        str(node_id): {
            "coherence": 1.0,
            "basin_mass": 1.0,
            "basin_id": "path_fixture",
            "depth": 0,
        }
        for node_id in node_ids
    }
    port_edges = {
        str(int(edge["edge_id"])): {
            "node_u": int(edge["node_u"]),
            "port_u": int(edge["port_u"]),
            "node_v": int(edge["node_v"]),
            "port_v": int(edge["port_v"]),
            "conductance": 1.0 / float(edge["geometric_length"]),
            "flux_uv": float(edge["signed_flux"]),
        }
        for edge in edges
    }
    base_conductance = {
        str(int(edge["edge_id"])): 1.0 / float(edge["geometric_length"])
        for edge in edges
    }
    geometric_length = {
        str(int(edge["edge_id"])): float(edge["geometric_length"])
        for edge in edges
    }
    flux_coupling = {
        str(int(edge["edge_id"])): abs(float(edge["signed_flux"]))
        for edge in edges
    }
    temporal_delay = {
        str(int(edge["edge_id"])): float(edge["temporal_delay"])
        for edge in edges
    }
    return {
        "topology": _topology(edges),
        "nodes": nodes,
        "port_edges": port_edges,
        "base_conductance": base_conductance,
        "geometric_length": geometric_length,
        "temporal_delay": temporal_delay,
        "flux_coupling": flux_coupling,
        "edge_label_computation_mode": {
            "base_conductance": "experiment_fixed_inverse_geometric_length",
            "geometric_length": "experiment_fixed_corridor_fixture",
            "temporal_delay": TEMPORAL_DELAY_MODE,
            "flux_coupling": "absolute_flux",
        },
        "edge_label_params": {
            "selection": "all",
            "tie_break": PATH_TIE_BREAK,
            "flux_score": "absolute signed flux and flux_coupling reported separately",
        },
        "sink_set": [],
        "basins": {},
    }


def _adjacency(state: Any) -> dict[int, list[tuple[int, int]]]:
    adjacency: dict[int, list[tuple[int, int]]] = {}
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        node_a, _ = endpoint_a
        node_b, _ = endpoint_b
        adjacency.setdefault(node_a, []).append((edge_id, node_b))
        adjacency.setdefault(node_b, []).append((edge_id, node_a))
    return adjacency


def _simple_paths(state: Any) -> list[tuple[int, ...]]:
    adjacency = _adjacency(state)
    paths: list[tuple[int, ...]] = []

    def visit(node_id: int, seen_nodes: set[int], edge_path: list[int]) -> None:
        if node_id == END_NODE_ID:
            paths.append(tuple(edge_path))
            return
        for edge_id, neighbor_id in sorted(adjacency.get(node_id, [])):
            if neighbor_id in seen_nodes:
                continue
            visit(neighbor_id, {*seen_nodes, neighbor_id}, [*edge_path, edge_id])

    visit(START_NODE_ID, {START_NODE_ID}, [])
    return sorted(paths, key=lambda path: (len(path), path))


def _path_nodes(state: Any, path: tuple[int, ...]) -> tuple[int, ...]:
    nodes = [START_NODE_ID]
    current = START_NODE_ID
    for edge_id in path:
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        node_a, _ = endpoint_a
        node_b, _ = endpoint_b
        current = node_b if current == node_a else node_a
        nodes.append(current)
    return tuple(nodes)


def _path_metrics(state: Any, path: tuple[int, ...]) -> dict[str, Any]:
    signed_fluxes = [float(state.port_edges[edge_id].flux_uv) for edge_id in path]
    abs_fluxes = [abs(value) for value in signed_fluxes]
    couplings = [float(state.flux_coupling[edge_id]) for edge_id in path]
    return {
        "path_edges": path,
        "path_nodes": _path_nodes(state, path),
        "edge_count": len(path),
        "metric_total": sum(float(state.geometric_length[edge_id]) for edge_id in path),
        "delay_total": sum(float(state.temporal_delay[edge_id]) for edge_id in path),
        "flux_bottleneck": min(abs_fluxes) if abs_fluxes else 0.0,
        "coupling_bottleneck": min(couplings) if couplings else 0.0,
        "flux_cumulative": sum(abs_fluxes),
        "coupling_cumulative": sum(couplings),
        "signed_fluxes": signed_fluxes,
    }


def _tie_payload(
    paths: list[dict[str, Any]],
    *,
    field: str,
    best_value: float,
) -> dict[str, Any]:
    score_tied = [
        path for path in paths if abs(float(path[field]) - best_value) <= 1e-12
    ]
    shortest_tied_count = min(int(path["edge_count"]) for path in score_tied)
    edge_count_tied = [
        path for path in score_tied if int(path["edge_count"]) == shortest_tied_count
    ]
    return {
        "score_tie_count": len(score_tied),
        "tie_count_before_lex": len(edge_count_tied),
        "tie_candidate_path_ids": " ".join(
            str(path["path_id"])
            for path in sorted(edge_count_tied, key=lambda path: path["path_edges"])
        ),
        "unresolved_tie": False,
    }


def _choose_min(
    paths: list[dict[str, Any]],
    field: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    best_value = min(float(path[field]) for path in paths)
    tied = [path for path in paths if abs(float(path[field]) - best_value) <= 1e-12]
    tied = sorted(tied, key=lambda path: (int(path["edge_count"]), path["path_edges"]))
    return tied[0], _tie_payload(paths, field=field, best_value=best_value)


def _choose_max(
    paths: list[dict[str, Any]],
    field: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    best_value = max(float(path[field]) for path in paths)
    tied = [path for path in paths if abs(float(path[field]) - best_value) <= 1e-12]
    tied = sorted(tied, key=lambda path: (int(path["edge_count"]), path["path_edges"]))
    return tied[0], _tie_payload(paths, field=field, best_value=best_value)


def _criterion_rows(
    *,
    variant_id: str,
    transform_id: str,
    seed: int,
    path_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    criteria = (
        ("P_metric", "minimize_sum_geometric_length", "metric_total", "min"),
        ("P_delay", "minimize_sum_temporal_delay", "delay_total", "min"),
        ("P_flux_bottleneck", "maximize_min_abs_signed_flux", "flux_bottleneck", "max"),
        (
            "P_coupling_bottleneck",
            "maximize_min_flux_coupling",
            "coupling_bottleneck",
            "max",
        ),
        ("P_flux_cumulative", "maximize_sum_abs_signed_flux", "flux_cumulative", "max"),
        (
            "P_coupling_cumulative",
            "maximize_sum_flux_coupling",
            "coupling_cumulative",
            "max",
        ),
    )
    rows = []
    for criterion_id, scoring_rule, score_field, direction in criteria:
        chosen, tie_payload = (
            _choose_min(path_rows, score_field)
            if direction == "min"
            else _choose_max(path_rows, score_field)
        )
        rows.append(
            {
                "experiment": EXPERIMENT_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": seed,
                "variant_id": variant_id,
                "transform_id": transform_id,
                "criterion_id": criterion_id,
                "scoring_rule": scoring_rule,
                "score_field": score_field,
                "direction": direction,
                "selected_path_id": chosen["path_id"],
                "selected_path_edges": " ".join(str(edge) for edge in chosen["path_edges"]),
                "selected_path_nodes": " ".join(str(node) for node in chosen["path_nodes"]),
                "selected_score": chosen[score_field],
                "score_tie_count": tie_payload["score_tie_count"],
                "tie_count_before_lex": tie_payload["tie_count_before_lex"],
                "tie_candidate_path_ids": tie_payload["tie_candidate_path_ids"],
                "unresolved_tie": tie_payload["unresolved_tie"],
                "tie_break_rule": PATH_TIE_BREAK,
            }
        )
    return rows


def _edge_rows(
    *,
    state: Any,
    variant_id: str,
    transform_id: str,
    seed: int,
) -> list[dict[str, Any]]:
    rows = []
    edge_corridors = {
        int(edge["edge_id"]): str(edge["corridor"]) for edge in BASE_EDGES
    }
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        node_u, slot_u = endpoint_a
        node_v, slot_v = endpoint_b
        port_edge = state.port_edges[edge_id]
        signed_flux = float(state.port_edges[edge_id].flux_uv)
        rows.append(
            {
                "experiment": EXPERIMENT_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": seed,
                "variant_id": variant_id,
                "transform_id": transform_id,
                "edge_id": edge_id,
                "corridor": edge_corridors[edge_id],
                "node_u": port_edge.node_u,
                "port_u": port_edge.port_u,
                "endpoint_u_slot": slot_u,
                "node_v": port_edge.node_v,
                "port_v": port_edge.port_v,
                "endpoint_v_slot": slot_v,
                "base_conductance": state.base_conductance[edge_id],
                "geometric_length": state.geometric_length[edge_id],
                "temporal_delay": state.temporal_delay[edge_id],
                "signed_flux": signed_flux,
                "absolute_signed_flux": abs(signed_flux),
                "flux_coupling": state.flux_coupling[edge_id],
                "edge_label_modes_json": json.dumps(
                    state.edge_label_computation_mode,
                    sort_keys=True,
                ),
            }
        )
    return rows


def evaluate_variant(
    *,
    variant_id: str,
    transform_id: str,
    port_map: dict[int, int],
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    model = GRC9V3.from_state(
        state=fixture_state(variant_id=variant_id, port_map=port_map),
        params=_params(seed),
    )
    state = model.get_state()
    paths = [_path_metrics(state, path) for path in _simple_paths(state)]
    path_rows = []
    for index, path in enumerate(paths):
        corridor = {
            (0, 1): "A_metric_short",
            (2, 3): "B_delay_fast",
            (4, 5): "C_flux_strong",
        }.get(tuple(path["path_edges"]), "mixed")
        row = {
            "experiment": EXPERIMENT_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "seed": seed,
            "variant_id": variant_id,
            "transform_id": transform_id,
            "path_id": f"path_{index}_{corridor}",
            "corridor": corridor,
            "path_edges": path["path_edges"],
            "path_nodes": path["path_nodes"],
            "edge_count": path["edge_count"],
            "metric_total": path["metric_total"],
            "delay_total": path["delay_total"],
            "flux_bottleneck": path["flux_bottleneck"],
            "coupling_bottleneck": path["coupling_bottleneck"],
            "flux_cumulative": path["flux_cumulative"],
            "coupling_cumulative": path["coupling_cumulative"],
            "signed_fluxes_json": json.dumps(path["signed_fluxes"]),
            "edge_label_modes_json": json.dumps(
                state.edge_label_computation_mode,
                sort_keys=True,
            ),
        }
        path_rows.append(row)
    criterion_rows = _criterion_rows(
        variant_id=variant_id,
        transform_id=transform_id,
        seed=seed,
        path_rows=path_rows,
    )
    selected = {row["criterion_id"]: row["selected_path_id"] for row in criterion_rows}
    summary_row = {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "variant_id": variant_id,
        "transform_id": transform_id,
        "path_count": len(path_rows),
        "metric_path": selected["P_metric"],
        "delay_path": selected["P_delay"],
        "flux_bottleneck_path": selected["P_flux_bottleneck"],
        "coupling_bottleneck_path": selected["P_coupling_bottleneck"],
        "flux_cumulative_path": selected["P_flux_cumulative"],
        "coupling_cumulative_path": selected["P_coupling_cumulative"],
        "metric_delay_flux_disagree": len(
            {
                selected["P_metric"],
                selected["P_delay"],
                selected["P_flux_bottleneck"],
            }
        )
        >= 2,
        "all_primary_paths_distinct": len(
            {
                selected["P_metric"],
                selected["P_delay"],
                selected["P_flux_bottleneck"],
            }
        )
        == 3,
        "tie_count": sum(
            1 for row in criterion_rows if int(row["tie_count_before_lex"]) > 1
        ),
        "unresolved_tie_count": sum(
            1 for row in criterion_rows if bool(row["unresolved_tie"])
        ),
        "artifact_sources": (
            "GRC9V3State.geometric_length, temporal_delay, flux_coupling, "
            "PortEdge.flux_uv, topology edge endpoints"
        ),
    }
    return (
        _edge_rows(
            state=state,
            variant_id=variant_id,
            transform_id=transform_id,
            seed=seed,
        ),
        path_rows,
        criterion_rows,
        summary_row,
    )


def run_experiment(
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    variants = (
        "base_disagreement",
        "equalized_geometric_labels",
        "equalized_temporal_labels",
        "equalized_flux_labels",
        "all_equalized_labels",
    )
    transforms = {
        "identity": {port: port for port in PORT_IDS},
        "degree_preserving_random_relabel": degree_preserving_random_relabel_map(
            seed + 1000
        ),
    }
    edge_rows: list[dict[str, Any]] = []
    path_rows: list[dict[str, Any]] = []
    criterion_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for variant_id in variants:
        for transform_id, port_map in transforms.items():
            edges, paths, criteria, summary_row = evaluate_variant(
                variant_id=variant_id,
                transform_id=transform_id,
                port_map=port_map,
                seed=seed,
            )
            edge_rows.extend(edges)
            path_rows.extend(paths)
            criterion_rows.extend(criteria)
            summary_rows.append(summary_row)
    base_identity = next(
        row
        for row in summary_rows
        if row["variant_id"] == "base_disagreement"
        and row["transform_id"] == "identity"
    )
    equalized_flux_identity = next(
        row
        for row in summary_rows
        if row["variant_id"] == "equalized_flux_labels"
        and row["transform_id"] == "identity"
    )
    all_equalized_identity = next(
        row
        for row in summary_rows
        if row["variant_id"] == "all_equalized_labels"
        and row["transform_id"] == "identity"
    )
    equalized_temporal_identity = next(
        row
        for row in summary_rows
        if row["variant_id"] == "equalized_temporal_labels"
        and row["transform_id"] == "identity"
    )
    summary = {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "run_id_convention": run_id_convention(),
        "runtime_assumptions": runtime_assumptions(),
        "artifact_entry_points": artifact_entry_points(),
        "comparison_report_schema": comparison_report_schema(),
        "blocked_observations_schema": blocked_observations_schema(),
        "scoring_conventions": {
            "metric_path": "minimize sum geometric_length(e)",
            "delay_path": "minimize sum temporal_delay(e)",
            "primary_flux_path": "maximize min_e abs(signed_flux(e))",
            "primary_coupling_path": "maximize min_e flux_coupling(e)",
            "secondary_flux_diagnostic": "maximize sum abs(signed_flux(e))",
            "secondary_coupling_diagnostic": "maximize sum flux_coupling(e)",
            "tie_break": PATH_TIE_BREAK,
        },
        "edge_label_modes": {
            "geometric_length": "experiment_fixed_corridor_fixture",
            "temporal_delay": TEMPORAL_DELAY_MODE,
            "flux_coupling": "absolute_flux",
            "signed_flux": "PortEdge.flux_uv orientation",
        },
        "base_primary_paths_all_distinct": bool(base_identity["all_primary_paths_distinct"]),
        "base_metric_delay_flux_disagree": bool(
            base_identity["metric_delay_flux_disagree"]
        ),
        "equalized_flux_collapses_flux_path_to_metric_path": (
            equalized_flux_identity["flux_bottleneck_path"]
            == equalized_flux_identity["metric_path"]
        ),
        "equalized_temporal_removes_delay_specific_winner": (
            equalized_temporal_identity["delay_path"]
            == equalized_temporal_identity["metric_path"]
        ),
        "all_equalized_paths_collapse_to_tie_broken_path": len(
            {
                all_equalized_identity["metric_path"],
                all_equalized_identity["delay_path"],
                all_equalized_identity["flux_bottleneck_path"],
                all_equalized_identity["coupling_bottleneck_path"],
            }
        )
        == 1,
        "port_relabel_preserves_path_choices": all(
            identity_row["metric_path"] == relabel_row["metric_path"]
            and identity_row["delay_path"] == relabel_row["delay_path"]
            and identity_row["flux_bottleneck_path"]
            == relabel_row["flux_bottleneck_path"]
            for identity_row in summary_rows
            for relabel_row in summary_rows
            if identity_row["variant_id"] == relabel_row["variant_id"]
            and identity_row["transform_id"] == "identity"
            and relabel_row["transform_id"] == "degree_preserving_random_relabel"
        ),
        "path_disagreement_claim_scope": (
            "auditable edge-label path separation; not direct row_column semantic evidence"
        ),
    }
    return edge_rows, path_rows, criterion_rows, summary_rows, summary


def blocked_observation_rows() -> list[dict[str, str]]:
    return [
        {
            "experiment": EXPERIMENT_ID,
            "observation": "runtime_path_solver",
            "status": "inconclusive",
            "artifact_source": "experiment-local path analyzer",
            "reconstruction_attempt": "Enumerated simple paths over GRC9V3 topology.",
            "notes": "The edge labels are runtime state surfaces; path solving is experiment-local analysis.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "row_column_path_semantic_claim",
            "status": "inconclusive",
            "artifact_source": "path fixture",
            "reconstruction_attempt": "Port ids are recorded, but path disagreement is label-driven.",
            "notes": "Experiment F supports multi-label path disagreement, not direct row/column semantic separation.",
        },
    ]


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    serialized = dict(row)
    for key in ("path_edges", "path_nodes"):
        if key in serialized and isinstance(serialized[key], tuple):
            serialized[key] = " ".join(str(value) for value in serialized[key])
    return serialized


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_manifest(
    *,
    seed: int,
    summary: dict[str, Any],
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "iteration": 8,
        "script_path": SCRIPT_PATH,
        "command": (
            "PYTHONPATH=src .venv/bin/python "
            f"{SCRIPT_PATH} --write-defaults --seed {seed}"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_branch": _git_value(["branch", "--show-current"]),
        "lane_id": LANE_ID,
        "runtime_params": _params(seed),
        "seed": seed,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "scoring_conventions": summary["scoring_conventions"],
        "output_paths": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in output_paths.items()
        },
        "validation_commands": [
            (
                "PYTHONPATH=src .venv/bin/python -m py_compile "
                f"{SCRIPT_PATH}"
            ),
            (
                "PYTHONPATH=src .venv/bin/python -m ruff check "
                f"{SCRIPT_PATH} "
                "experiments/2026-05-N01-grc9v3-properties/scripts/grc9v3_fixture_harness.py"
            ),
            (
                ".venv/bin/python -m json.tool "
                "experiments/2026-05-N01-grc9v3-properties/outputs/"
                "experiment_f_path_disagreement_summary.json"
            ),
        ],
        "reuse_notes": {
            "d2": "Use path-label criteria as feature targets.",
            "d7": "Use path rows only as edge-label evidence unless port grouping comparisons are added.",
        },
    }


def _write_report(
    path: Path,
    criteria_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    base_criteria = [
        row
        for row in criteria_rows
        if row["variant_id"] == "base_disagreement"
        and row["transform_id"] == "identity"
    ]
    identity_summaries = [row for row in summary_rows if row["transform_id"] == "identity"]
    lines = [
        "# Experiment F Path Disagreement",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report tests whether metric, temporal-delay, and strongest-flux",
        "path notions can disagree while remaining auditable edge by edge under",
        "the Lane A baseline.",
        "",
        "Path disagreement is reported as edge-label evidence, not direct",
        "row/column semantic evidence.",
        "",
        "## Scoring",
        "",
        "- metric path: `minimize sum geometric_length(e)`",
        "- delay path: `minimize sum temporal_delay(e)`",
        "- primary flux path: `maximize min_e abs(signed_flux(e))`",
        "- primary coupling path: `maximize min_e flux_coupling(e)`",
        "- secondary flux diagnostic: `maximize sum abs(signed_flux(e))`",
        "- secondary coupling diagnostic: `maximize sum flux_coupling(e)`",
        f"- tie-break: `{PATH_TIE_BREAK}`",
        "",
        "## Base Fixture Choices",
        "",
        "| Criterion | Selected Path | Score | Tie |",
        "| --- | --- | ---: | --- |",
    ]
    for row in base_criteria:
        lines.append(
            "| "
            f"{row['criterion_id']} | "
            f"{row['selected_path_id']} | "
            f"{float(row['selected_score']):.12g} | "
            f"`{row['tie_count_before_lex']}` |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Variant | Metric Path | Delay Path | Flux Bottleneck Path | Coupling Bottleneck Path | Ties |",
            "| --- | --- | --- | --- | --- | ---: |",
        ]
    )
    for row in identity_summaries:
        lines.append(
            "| "
            f"{row['variant_id']} | "
            f"{row['metric_path']} | "
            f"{row['delay_path']} | "
            f"{row['flux_bottleneck_path']} | "
            f"{row['coupling_bottleneck_path']} | "
            f"{row['tie_count']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "- base primary paths all distinct: "
            f"`{json.dumps(summary['base_primary_paths_all_distinct'])}`",
            "- base metric/delay/flux paths disagree: "
            f"`{json.dumps(summary['base_metric_delay_flux_disagree'])}`",
            "- equalized flux collapses flux path to metric path: "
            f"`{json.dumps(summary['equalized_flux_collapses_flux_path_to_metric_path'])}`",
            "- equalized temporal labels remove delay-specific winner: "
            f"`{json.dumps(summary['equalized_temporal_removes_delay_specific_winner'])}`",
            "- all equalized paths collapse to tie-broken path: "
            f"`{json.dumps(summary['all_equalized_paths_collapse_to_tie_broken_path'])}`",
            "- port relabel preserves path choices: "
            f"`{json.dumps(summary['port_relabel_preserves_path_choices'])}`",
            "",
            "## Interpretation",
            "",
            "Experiment F supports auditable multi-label path disagreement in the",
            "clean three-corridor fixture. The metric path, delay path, and primary",
            "strongest-flux path select different corridors in the base fixture.",
            "Equalized controls show the differences are driven by the intended",
            "edge-label surfaces rather than nondeterministic path ordering.",
            "",
            "The result does not by itself support row/column semantic separation.",
            "It supports that the available GRC9V3 edge-label and flux artifacts can",
            "back multiple distinct path notions with edge-by-edge explanations.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(seed: int) -> dict[str, Path]:
    edge_rows, path_rows, criterion_rows, summary_rows, summary = run_experiment(seed)
    edge_rows = [_serialize_row(row) for row in edge_rows]
    path_rows = [_serialize_row(row) for row in path_rows]
    edges_path = EXPERIMENT_ROOT / "outputs" / "experiment_f_path_disagreement_edges.csv"
    paths_path = EXPERIMENT_ROOT / "outputs" / "experiment_f_path_disagreement_paths.csv"
    criteria_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_f_path_disagreement_criteria.csv"
    )
    variants_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_f_path_disagreement_variants.csv"
    )
    summary_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_f_path_disagreement_summary.json"
    )
    manifest_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_f_path_disagreement_manifest.json"
    )
    blocked_path = (
        EXPERIMENT_ROOT
        / "reports"
        / "experiment_f_path_disagreement_blocked_observations.csv"
    )
    report_path = EXPERIMENT_ROOT / "reports" / "experiment_f_path_disagreement.md"
    output_paths = {
        "edges_csv": edges_path,
        "paths_csv": paths_path,
        "criteria_csv": criteria_path,
        "variants_csv": variants_path,
        "summary_json": summary_path,
        "manifest_json": manifest_path,
        "blocked_observations_csv": blocked_path,
        "report_md": report_path,
    }
    _write_csv(edges_path, edge_rows)
    _write_csv(paths_path, path_rows)
    _write_csv(criteria_path, criterion_rows)
    _write_csv(variants_path, summary_rows)
    _write_json(summary_path, summary)
    _write_json(
        manifest_path,
        _build_manifest(seed=seed, summary=summary, output_paths=output_paths),
    )
    _write_csv(blocked_path, blocked_observation_rows())
    _write_report(report_path, criterion_rows, summary_rows, summary)
    return output_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--write-defaults", action="store_true")
    args = parser.parse_args()
    if args.write_defaults:
        paths = write_outputs(args.seed)
        print(json.dumps({key: str(path) for key, path in paths.items()}, indent=2))
    else:
        edge_rows, path_rows, criterion_rows, summary_rows, summary = run_experiment(
            args.seed
        )
        print(
            json.dumps(
                {
                    "summary": summary,
                    "edges": [_serialize_row(row) for row in edge_rows],
                    "paths": [_serialize_row(row) for row in path_rows],
                    "criteria": criterion_rows,
                    "variants": summary_rows,
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
