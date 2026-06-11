"""Experiment G: mixed row/column motion observer over port histories."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.models import GRC9V3
from pygrc.models.grc_9_ports import port_id_to_slot, port_to_rc

from grc9v3_fixture_harness import (
    ARTIFACT_SCHEMA_VERSION,
    LANE_ID,
    PORT_IDS,
    artifact_entry_points,
    blocked_observations_schema,
    column_permutation_map,
    comparison_report_schema,
    degree_preserving_random_relabel_map,
    is_row_column_factorized,
    is_transpose_factorized,
    row_permutation_map,
    run_id_convention,
    runtime_assumptions,
)


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ID = "experiment_g_mixed_motion"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_experiment_g_mixed_motion.py"
)
CENTRAL_NODE_ID = 0
LOW_BACKGROUND_FLUX = 1.0
DOMINANT_FLUX = 10.0
FLUX_TIE_TOLERANCE = 1e-12


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
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
        },
        "constitutive_semantic_modes": {
            "hessian_backend": "row_basis_diagonal",
            "boundary_mode": "prune",
        },
    }


def _condition_suite() -> list[dict[str, Any]]:
    return [
        {
            "condition_id": "g_row_preserving_column_changing",
            "condition_class": "row_preserving_column_changing",
            "dominant_ports": (4, 5, 6),
            "expected_identity_class": "row_preserving_column_changing",
            "notes": "Row 2 ports sweep from column 1 to 3.",
        },
        {
            "condition_id": "g_column_preserving_row_changing",
            "condition_class": "column_preserving_row_changing",
            "dominant_ports": (3, 6, 9),
            "expected_identity_class": "column_preserving_row_changing",
            "notes": "Column 3 ports sweep from row 1 to 3.",
        },
        {
            "condition_id": "g_static_no_motion_baseline",
            "condition_class": "static_no_motion_baseline",
            "dominant_ports": (5, 5, 5),
            "expected_identity_class": "neither_changing",
            "notes": "Static central port control.",
        },
    ]


def _transforms(seed: int) -> dict[str, dict[int, int]]:
    return {
        "identity": {port: port for port in PORT_IDS},
        "row_permutation_231": row_permutation_map((2, 3, 1)),
        "column_permutation_312": column_permutation_map((3, 1, 2)),
        "degree_preserving_random_relabel": degree_preserving_random_relabel_map(
            seed + 1000
        ),
    }


def _factorization_class(port_map: dict[int, int]) -> str:
    if is_row_column_factorized(port_map):
        return "row_column"
    if is_transpose_factorized(port_map):
        return "transpose"
    return "non_factorized"


def _mapped_sequence(
    dominant_ports: tuple[int, ...],
    port_map: dict[int, int],
) -> tuple[int, ...]:
    return tuple(port_map[port] for port in dominant_ports)


def _topology_for_ports(port_sequence: tuple[int, ...]) -> tuple[dict[str, Any], dict[int, int]]:
    unique_ports = tuple(dict.fromkeys(port_sequence))
    port_to_edge_id = {port_id: index for index, port_id in enumerate(unique_ports)}
    nodes = [{"node_id": CENTRAL_NODE_ID, "payload": {"role": "central"}}]
    edges = []
    incidence: dict[str, list[int]] = {str(CENTRAL_NODE_ID): []}
    for edge_id, port_id in enumerate(unique_ports):
        neighbor_id = edge_id + 1
        nodes.append(
            {
                "node_id": neighbor_id,
                "payload": {"role": "successor", "central_port": port_id},
            }
        )
        incidence[str(CENTRAL_NODE_ID)].append(edge_id)
        incidence[str(neighbor_id)] = [edge_id]
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {
                    "node_id": CENTRAL_NODE_ID,
                    "slot": port_id_to_slot(port_id),
                },
                "endpoint_b": {"node_id": neighbor_id, "slot": port_id_to_slot(1)},
                "payload": {"central_port": port_id},
            }
        )
    return (
        {
            "nodes": nodes,
            "edges": edges,
            "incidence": {
                node_id: sorted(edge_ids)
                for node_id, edge_ids in sorted(incidence.items())
            },
            "port_structure": {},
        },
        port_to_edge_id,
    )


def _snapshot_state(
    *,
    port_sequence: tuple[int, ...],
    active_port: int,
    step_index: int,
) -> dict[str, Any]:
    topology, port_to_edge_id = _topology_for_ports(port_sequence)
    node_ids = [int(node["node_id"]) for node in topology["nodes"]]
    nodes = {
        str(node_id): {
            "coherence": 1.0 + 0.1 * step_index if node_id == CENTRAL_NODE_ID else 1.0,
            "basin_mass": 1.0,
            "basin_id": f"motion_step_{step_index}",
            "depth": 0 if node_id == CENTRAL_NODE_ID else 1,
            "parent_id": None if node_id == CENTRAL_NODE_ID else CENTRAL_NODE_ID,
        }
        for node_id in node_ids
    }
    port_edges = {}
    base_conductance = {}
    flux_coupling = {}
    for port_id, edge_id in port_to_edge_id.items():
        signed_flux = DOMINANT_FLUX if port_id == active_port else LOW_BACKGROUND_FLUX
        neighbor_id = edge_id + 1
        port_edges[str(edge_id)] = {
            "node_u": CENTRAL_NODE_ID,
            "port_u": port_id,
            "node_v": neighbor_id,
            "port_v": 1,
            "conductance": 1.0,
            "flux_uv": signed_flux,
        }
        base_conductance[str(edge_id)] = 1.0
        flux_coupling[str(edge_id)] = abs(signed_flux)
    return {
        "topology": topology,
        "nodes": nodes,
        "port_edges": port_edges,
        "base_conductance": base_conductance,
        "flux_coupling": flux_coupling,
        "edge_label_computation_mode": {
            "flux_coupling": "experiment_fixed_absolute_flux",
            "motion_source": "experiment_local_checkpoint_overlay",
        },
        "edge_label_params": {
            "dominant_flux": {
                "background": LOW_BACKGROUND_FLUX,
                "dominant": DOMINANT_FLUX,
            }
        },
        "sink_set": [edge_id + 1 for edge_id in port_to_edge_id.values()],
        "basins": {
            str(edge_id + 1): [edge_id + 1]
            for edge_id in port_to_edge_id.values()
        },
        "cached_quantities": {
            "experiment_g_checkpoint_overlay": {
                "step_index": step_index,
                "active_port": active_port,
            }
        },
    }


def _dominant_edge_row(
    *,
    state: Any,
    condition: dict[str, Any],
    transform_id: str,
    factorization_class: str,
    step_index: int,
    seed: int,
) -> dict[str, Any]:
    edge_scores = [
        (abs(float(port_edge.flux_uv)), edge_id, port_edge)
        for edge_id, port_edge in state.port_edges.items()
        if port_edge.node_u == CENTRAL_NODE_ID or port_edge.node_v == CENTRAL_NODE_ID
    ]
    edge_scores.sort(key=lambda item: (-item[0], item[1]))
    best_score, edge_id, port_edge = edge_scores[0]
    tied_edges = [
        candidate_edge_id
        for score, candidate_edge_id, _ in edge_scores
        if abs(score - best_score) <= FLUX_TIE_TOLERANCE
    ]
    central_port = (
        port_edge.port_u
        if port_edge.node_u == CENTRAL_NODE_ID
        else port_edge.port_v
    )
    successor_node_id = (
        port_edge.node_v
        if port_edge.node_u == CENTRAL_NODE_ID
        else port_edge.node_u
    )
    row, column = port_to_rc(central_port)
    return {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "condition_id": condition["condition_id"],
        "condition_class": condition["condition_class"],
        "transform_id": transform_id,
        "factorization_class": factorization_class,
        "semantic_interpretability": (
            "canonical_row_column"
            if factorization_class == "row_column"
            else "weakened_by_non_factorized_relabel"
        ),
        "step_index": step_index,
        "dominant_flux_edge_id": edge_id,
        "dominant_flux_abs": best_score,
        "dominant_flux_signed": float(port_edge.flux_uv),
        "dominant_tie_count": len(tied_edges),
        "dominant_tied_edge_ids": " ".join(str(value) for value in tied_edges),
        "central_node_id": CENTRAL_NODE_ID,
        "central_port": central_port,
        "central_row": row,
        "central_column": column,
        "successor_node_id": successor_node_id,
        "successor_basin_id": state.nodes[successor_node_id].basin_id,
        "dominant_boundary_source": "central-node incident edge with max abs(PortEdge.flux_uv)",
        "artifact_source": "GRC9V3State.port_edges plus topology edge endpoints",
    }


def _edge_history_rows(
    *,
    state: Any,
    condition: dict[str, Any],
    transform_id: str,
    step_index: int,
    seed: int,
) -> list[dict[str, Any]]:
    rows = []
    for edge_id, port_edge in sorted(state.port_edges.items()):
        central_port = (
            port_edge.port_u
            if port_edge.node_u == CENTRAL_NODE_ID
            else port_edge.port_v
        )
        row, column = port_to_rc(central_port)
        rows.append(
            {
                "experiment": EXPERIMENT_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": seed,
                "condition_id": condition["condition_id"],
                "condition_class": condition["condition_class"],
                "transform_id": transform_id,
                "step_index": step_index,
                "edge_id": edge_id,
                "node_u": port_edge.node_u,
                "port_u": port_edge.port_u,
                "node_v": port_edge.node_v,
                "port_v": port_edge.port_v,
                "central_port": central_port,
                "central_row": row,
                "central_column": column,
                "signed_flux": float(port_edge.flux_uv),
                "absolute_flux": abs(float(port_edge.flux_uv)),
                "flux_coupling": state.flux_coupling[edge_id],
            }
        )
    return rows


def _transition_class(previous: dict[str, Any], current: dict[str, Any]) -> str:
    row_same = int(previous["central_row"]) == int(current["central_row"])
    column_same = int(previous["central_column"]) == int(current["central_column"])
    if row_same and not column_same:
        return "row_preserving_column_changing"
    if column_same and not row_same:
        return "column_preserving_row_changing"
    if not row_same and not column_same:
        return "both_changing"
    return "neither_changing"


def _transition_rows(port_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for previous, current in zip(port_rows, port_rows[1:], strict=False):
        rows.append(
            {
                "experiment": EXPERIMENT_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": previous["seed"],
                "condition_id": previous["condition_id"],
                "condition_class": previous["condition_class"],
                "transform_id": previous["transform_id"],
                "factorization_class": previous["factorization_class"],
                "semantic_interpretability": previous["semantic_interpretability"],
                "from_step": previous["step_index"],
                "to_step": current["step_index"],
                "from_port": previous["central_port"],
                "to_port": current["central_port"],
                "from_row": previous["central_row"],
                "to_row": current["central_row"],
                "from_column": previous["central_column"],
                "to_column": current["central_column"],
                "from_successor_node_id": previous["successor_node_id"],
                "to_successor_node_id": current["successor_node_id"],
                "successor_changed": (
                    previous["successor_node_id"] != current["successor_node_id"]
                ),
                "transition_class": _transition_class(previous, current),
                "artifact_source": "dominant flux/boundary port history",
            }
        )
    return rows


def evaluate_condition(
    *,
    condition: dict[str, Any],
    transform_id: str,
    port_map: dict[int, int],
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    factorization_class = _factorization_class(port_map)
    mapped_ports = _mapped_sequence(condition["dominant_ports"], port_map)
    port_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    for step_index, active_port in enumerate(mapped_ports):
        model = GRC9V3.from_state(
            state=_snapshot_state(
                port_sequence=mapped_ports,
                active_port=active_port,
                step_index=step_index,
            ),
            params=_params(seed),
        )
        state = model.get_state()
        edge_rows.extend(
            _edge_history_rows(
                state=state,
                condition=condition,
                transform_id=transform_id,
                step_index=step_index,
                seed=seed,
            )
        )
        port_rows.append(
            _dominant_edge_row(
                state=state,
                condition=condition,
                transform_id=transform_id,
                factorization_class=factorization_class,
                step_index=step_index,
                seed=seed,
            )
        )
    transition_rows = _transition_rows(port_rows)
    observed_classes = tuple(row["transition_class"] for row in transition_rows)
    canonical_interpretability = factorization_class == "row_column"
    expected_class = condition["expected_identity_class"]
    expected_match = (
        canonical_interpretability
        and all(transition_class == expected_class for transition_class in observed_classes)
    )
    summary_row = {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "condition_id": condition["condition_id"],
        "condition_class": condition["condition_class"],
        "transform_id": transform_id,
        "factorization_class": factorization_class,
        "semantic_interpretability": (
            "canonical_row_column"
            if canonical_interpretability
            else "weakened_by_non_factorized_relabel"
        ),
        "mapped_dominant_ports": " ".join(str(port) for port in mapped_ports),
        "dominant_rows": " ".join(str(row["central_row"]) for row in port_rows),
        "dominant_columns": " ".join(str(row["central_column"]) for row in port_rows),
        "observed_transition_classes": " | ".join(observed_classes),
        "expected_identity_class": expected_class,
        "expected_class_match": expected_match,
        "successor_change_count": sum(
            1 for row in transition_rows if bool(row["successor_changed"])
        ),
        "dominant_tie_count_max": max(
            int(row["dominant_tie_count"]) for row in port_rows
        ),
        "motion_claim_level": (
            "supported_by_experiment_local_checkpoint_overlay"
            if canonical_interpretability
            else "semantic_interpretability_weakened_by_random_relabel"
        ),
        "notes": condition["notes"],
    }
    return edge_rows, port_rows, transition_rows, summary_row


def run_experiment(
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    transforms = _transforms(seed)
    edge_rows: list[dict[str, Any]] = []
    port_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    condition_rows: list[dict[str, Any]] = []
    for condition in _condition_suite():
        for transform_id, port_map in transforms.items():
            edges, ports, transitions, summary_row = evaluate_condition(
                condition=condition,
                transform_id=transform_id,
                port_map=port_map,
                seed=seed,
            )
            edge_rows.extend(edges)
            port_rows.extend(ports)
            transition_rows.extend(transitions)
            condition_rows.append(summary_row)

    canonical_rows = [
        row for row in condition_rows if row["factorization_class"] == "row_column"
    ]
    random_rows = [
        row for row in condition_rows if row["factorization_class"] == "non_factorized"
    ]
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
        "transforms": transforms,
        "observation_surface": (
            "experiment-local checkpoint overlay over GRC9V3State.port_edges/topology"
        ),
        "dominant_flux_rule": (
            "select central-node incident edge with maximum abs(PortEdge.flux_uv); "
            "ties break by edge id and are reported"
        ),
        "transition_classes": [
            "row_preserving_column_changing",
            "column_preserving_row_changing",
            "both_changing",
            "neither_changing",
        ],
        "canonical_controls_match_expected": all(
            bool(row["expected_class_match"]) for row in canonical_rows
        ),
        "random_relabel_weakens_semantic_interpretability": all(
            row["motion_claim_level"]
            == "semantic_interpretability_weakened_by_random_relabel"
            for row in random_rows
        ),
        "static_no_motion_supported": all(
            row["expected_class_match"]
            for row in canonical_rows
            if row["condition_id"] == "g_static_no_motion_baseline"
        ),
        "row_preserving_column_changing_supported": all(
            row["expected_class_match"]
            for row in canonical_rows
            if row["condition_id"] == "g_row_preserving_column_changing"
        ),
        "column_preserving_row_changing_supported": all(
            row["expected_class_match"]
            for row in canonical_rows
            if row["condition_id"] == "g_column_preserving_row_changing"
        ),
        "claim_scope": (
            "observer-local mixed row/column transition classification in clean fixtures; "
            "full reusable motion-loader port history remains partial"
        ),
    }
    return edge_rows, port_rows, transition_rows, condition_rows, summary


def blocked_observation_rows() -> list[dict[str, str]]:
    return [
        {
            "experiment": EXPERIMENT_ID,
            "observation": "full_reusable_motion_loader_port_history",
            "status": "inconclusive",
            "artifact_source": "motion loader plus graph checkpoint overlays",
            "reconstruction_attempt": "Used experiment-local GRC9V3State checkpoint overlay analyzer.",
            "notes": "Current motion loader records port matrix availability, not normalized full per-port histories.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "basin_assignment_motion",
            "status": "inconclusive",
            "artifact_source": "GRC9V3State.nodes[*].basin_id and basins",
            "reconstruction_attempt": "Recorded successor changes from dominant edge endpoints.",
            "notes": "This iteration supports successor/port transition classification, not basin-motion dynamics.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "landscape_general_motion_semantics",
            "status": "inconclusive",
            "artifact_source": "clean synthetic checkpoint-overlay fixtures",
            "reconstruction_attempt": "Ran deterministic three-step fixtures and transform controls.",
            "notes": "Landscape-seed robustness remains outside this raw O-style pass.",
        },
    ]


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"cannot write empty CSV {path}")
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _build_manifest(
    *,
    seed: int,
    summary: dict[str, Any],
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "iteration": 9,
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
        "condition_ids": [condition["condition_id"] for condition in _condition_suite()],
        "port_mappings": summary["transforms"],
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "dominant_flux_rule": summary["dominant_flux_rule"],
        "transition_classes": summary["transition_classes"],
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
                "experiment_g_mixed_motion_summary.json"
            ),
        ],
        "reuse_notes": {
            "o_synthesis": "Use as observer-local mixed row/column motion evidence.",
            "future_runtime": "Reusable motion loader port histories remain a candidate implementation surface.",
        },
    }


def _write_report(
    path: Path,
    condition_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    canonical_rows = [
        row for row in condition_rows if row["factorization_class"] == "row_column"
    ]
    random_rows = [
        row for row in condition_rows if row["factorization_class"] == "non_factorized"
    ]
    lines = [
        "# Experiment G Mixed Row/Column Motion",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report tests whether an experiment-local checkpoint-overlay",
        "observer can classify dominant central-port motion as row-preserving",
        "and column-changing, column-preserving and row-changing, both-changing,",
        "or neither-changing.",
        "",
        "The evidence surface is `GRC9V3State.port_edges` plus topology endpoint",
        "metadata. Full reusable motion-loader port histories remain partial.",
        "",
        "## Observer Rule",
        "",
        "- dominant flux edge: central-node incident edge with maximum",
        "  `abs(PortEdge.flux_uv)`",
        "- dominant boundary edge: same selected central-node incident edge",
        "- successor: opposite endpoint of the selected dominant edge",
        "- port coordinates: canonical `port_to_rc(central_port)`",
        "- ties: break by edge id and report tie count",
        "",
        "## Canonical Controls",
        "",
        "| Condition | Transform | Ports | Rows | Columns | Classes | Match |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in canonical_rows:
        lines.append(
            "| "
            f"{row['condition_id']} | "
            f"{row['transform_id']} | "
            f"{row['mapped_dominant_ports']} | "
            f"{row['dominant_rows']} | "
            f"{row['dominant_columns']} | "
            f"{row['observed_transition_classes']} | "
            f"`{json.dumps(row['expected_class_match'])}` |"
        )
    lines.extend(
        [
            "",
            "## Random Relabel Controls",
            "",
            "| Condition | Ports | Rows | Columns | Observed Classes | Interpretation |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in random_rows:
        lines.append(
            "| "
            f"{row['condition_id']} | "
            f"{row['mapped_dominant_ports']} | "
            f"{row['dominant_rows']} | "
            f"{row['dominant_columns']} | "
            f"{row['observed_transition_classes']} | "
            f"{row['motion_claim_level']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "- canonical controls match expected classes: "
            f"`{json.dumps(summary['canonical_controls_match_expected'])}`",
            "- row-preserving/column-changing supported: "
            f"`{json.dumps(summary['row_preserving_column_changing_supported'])}`",
            "- column-preserving/row-changing supported: "
            f"`{json.dumps(summary['column_preserving_row_changing_supported'])}`",
            "- static no-motion baseline supported: "
            f"`{json.dumps(summary['static_no_motion_supported'])}`",
            "- random relabel weakens semantic interpretability: "
            f"`{json.dumps(summary['random_relabel_weakens_semantic_interpretability'])}`",
            "",
            "## Interpretation",
            "",
            "Experiment G supports observer-local mixed row/column motion",
            "classification in clean checkpoint-overlay fixtures. Dominant",
            "edge/port histories are sufficient to classify row-preserving",
            "column-changing and column-preserving row-changing transitions under",
            "identity, row-permutation, and column-permutation controls.",
            "",
            "The random degree-preserving port relabel is non-factorized, so the",
            "canonical row/column interpretation is intentionally weakened rather",
            "than treated as a failed canonical class.",
            "",
            "This result does not establish landscape-general motion behavior or",
            "full reusable motion-loader support for normalized port histories.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(seed: int) -> dict[str, Path]:
    edge_rows, port_rows, transition_rows, condition_rows, summary = run_experiment(seed)
    edge_history_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_g_mixed_motion_edge_history.csv"
    )
    port_history_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_g_mixed_motion_port_history.csv"
    )
    transitions_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_g_mixed_motion_transitions.csv"
    )
    conditions_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_g_mixed_motion_conditions.csv"
    )
    summary_path = EXPERIMENT_ROOT / "outputs" / "experiment_g_mixed_motion_summary.json"
    manifest_path = EXPERIMENT_ROOT / "outputs" / "experiment_g_mixed_motion_manifest.json"
    blocked_path = (
        EXPERIMENT_ROOT
        / "reports"
        / "experiment_g_mixed_motion_blocked_observations.csv"
    )
    report_path = EXPERIMENT_ROOT / "reports" / "experiment_g_mixed_motion.md"
    output_paths = {
        "edge_history_csv": edge_history_path,
        "port_history_csv": port_history_path,
        "transitions_csv": transitions_path,
        "conditions_csv": conditions_path,
        "summary_json": summary_path,
        "manifest_json": manifest_path,
        "blocked_observations_csv": blocked_path,
        "report_md": report_path,
    }
    _write_csv(edge_history_path, edge_rows)
    _write_csv(port_history_path, port_rows)
    _write_csv(transitions_path, transition_rows)
    _write_csv(conditions_path, condition_rows)
    _write_json(summary_path, summary)
    _write_json(
        manifest_path,
        _build_manifest(seed=seed, summary=summary, output_paths=output_paths),
    )
    _write_csv(blocked_path, blocked_observation_rows())
    _write_report(report_path, condition_rows, summary)
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
        edge_rows, port_rows, transition_rows, condition_rows, summary = run_experiment(
            args.seed
        )
        print(
            json.dumps(
                {
                    "summary": summary,
                    "edge_history": edge_rows,
                    "port_history": port_rows,
                    "transitions": transition_rows,
                    "conditions": condition_rows,
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
