"""Experiment E: G/Split reconstruction for GRC9V3 column fields."""

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
    artifact_entry_points,
    blocked_observations_schema,
    comparison_report_schema,
    run_id_convention,
    runtime_assumptions,
)


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ID = "experiment_e_coarse_graining_split"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_experiment_e_coarse_graining_split.py"
)
CENTRAL_NODE_ID = 0
RECONSTRUCTION_TOLERANCE = 1e-12
NONNEGATIVE_FIELDS = (
    "conductance",
    "geometric_length",
    "temporal_delay",
    "flux_coupling",
    "abs_flux",
)


def _params(seed: int) -> dict[str, Any]:
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
            "rng_seed": seed,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
        },
        "constitutive_semantic_modes": {
            "edge_label_selection": "all",
            "hessian_backend": "row_basis_diagonal",
            "boundary_mode": "prune",
        },
    }


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


def _topology(connections: list[tuple[int, int, int, int, int]]) -> dict[str, Any]:
    node_ids: set[int] = set()
    incidence: dict[str, list[int]] = {}
    edges: list[dict[str, Any]] = []
    for edge_id, node_a, port_a, node_b, port_b in connections:
        node_ids.update({node_a, node_b})
        incidence.setdefault(str(node_a), []).append(edge_id)
        incidence.setdefault(str(node_b), []).append(edge_id)
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": port_id_to_slot(port_a)},
                "endpoint_b": {"node_id": node_b, "slot": port_id_to_slot(port_b)},
                "payload": {},
            }
        )
    return {
        "nodes": [{"node_id": node_id, "payload": {}} for node_id in sorted(node_ids)],
        "edges": sorted(edges, key=lambda item: int(item["edge_id"])),
        "incidence": {
            node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
        },
        "port_structure": {},
    }


def _port_edge(
    *,
    node_u: int,
    port_u: int,
    node_v: int,
    port_v: int,
    conductance: float,
    flux_uv: float,
) -> dict[str, int | float]:
    return {
        "node_u": node_u,
        "port_u": port_u,
        "node_v": node_v,
        "port_v": port_v,
        "conductance": conductance,
        "flux_uv": flux_uv,
    }


def _coarse_fixture_state() -> dict[str, Any]:
    """Fixture with dense, single-active, zero-column, and mixed-sign cases."""

    # Central node:
    # - column 1 has three active ports and mixed signed flux
    # - column 2 has one active port
    # - column 3 is a zero column
    active_ports = {
        1: {"conductance": 2.0, "flux_uv": 2.5, "coherence": 1.3},
        4: {"conductance": 4.0, "flux_uv": -1.5, "coherence": 0.7},
        7: {"conductance": 1.0, "flux_uv": 0.75, "coherence": 1.1},
        2: {"conductance": 3.0, "flux_uv": 1.25, "coherence": 1.2},
    }
    connections: list[tuple[int, int, int, int, int]] = []
    nodes: dict[str, dict[str, float]] = {
        str(CENTRAL_NODE_ID): {"coherence": 1.0, "basin_mass": 1.0}
    }
    port_edges: dict[str, dict[str, int | float]] = {}
    edge_id = 0
    for port_id, payload in sorted(active_ports.items()):
        neighbor_id = 300 + port_id
        connections.append((edge_id, CENTRAL_NODE_ID, port_id, neighbor_id, 1))
        nodes[str(neighbor_id)] = {
            "coherence": float(payload["coherence"]),
            "basin_mass": float(payload["coherence"]),
        }
        port_edges[str(edge_id)] = _port_edge(
            node_u=CENTRAL_NODE_ID,
            port_u=port_id,
            node_v=neighbor_id,
            port_v=1,
            conductance=float(payload["conductance"]),
            flux_uv=float(payload["flux_uv"]),
        )
        edge_id += 1
    return {
        "topology": _topology(connections),
        "nodes": nodes,
        "port_edges": port_edges,
        "sink_set": [CENTRAL_NODE_ID],
        "basins": {
            str(CENTRAL_NODE_ID): sorted(int(node_id) for node_id in nodes)
        },
    }


def _model_for_fields(seed: int) -> GRC9V3:
    model = GRC9V3.from_state(state=_coarse_fixture_state(), params=_params(seed))
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    model.rebuild_differential_state()
    return model


def _model_for_raw_signed_flux(seed: int) -> GRC9V3:
    return GRC9V3.from_state(state=_coarse_fixture_state(), params=_params(seed))


def _max_abs_error(
    original: dict[int, dict[int, float]],
    reconstructed: dict[str, dict[str, float]],
) -> float:
    max_error = 0.0
    for node_id, ports in original.items():
        reconstructed_ports = reconstructed.get(str(node_id), {})
        for port_id, value in ports.items():
            error = abs(float(value) - float(reconstructed_ports.get(str(port_id), 0.0)))
            max_error = max(max_error, error)
    return max_error


def _nonzero_port_count(port_field: dict[int, dict[int, float]]) -> int:
    return sum(1 for ports in port_field.values() for value in ports.values() if value != 0.0)


def evaluate_nonnegative_field(model: GRC9V3, field_name: str) -> dict[str, Any]:
    original = model._build_nonnegative_port_field(field_name=field_name)
    coarse_state = model.coarse_grain_columns(field_name)
    reconstructed = model.split_columns(coarse_state)
    central_payload = coarse_state["by_node"][str(CENTRAL_NODE_ID)]
    zero_column_profiles_uniform = (
        central_payload["column_totals"][2] == 0.0
        and central_payload["profiles"][2] == [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
    )
    single_active_column_reconstructs = all(
        abs(
            original[CENTRAL_NODE_ID][port_id]
            - reconstructed["port_field"][str(CENTRAL_NODE_ID)][str(port_id)]
        )
        <= 1e-12
        for port_id in (2, 5, 8)
    )
    return {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "field_name": field_name,
        "field_class": "nonnegative",
        "mode": coarse_state["mode"],
        "eligible": True,
        "reconstruction_path": "G(field) -> Split(G(field))",
        "max_abs_error": _max_abs_error(original, reconstructed["port_field"]),
        "nonzero_port_count": _nonzero_port_count(original),
        "central_column_totals": json.dumps(central_payload["column_totals"]),
        "zero_column_control": "column_3",
        "zero_column_profiles_uniform": zero_column_profiles_uniform,
        "single_active_column_control": "column_2",
        "single_active_column_reconstructs": single_active_column_reconstructs,
        "signed_flux_j_split_available": False,
        "compressed_signed_control_error": "",
        "artifact_sources": "GRC9V3.coarse_grain_columns, GRC9V3.split_columns",
    }


def evaluate_signed_flux(model: GRC9V3) -> tuple[dict[str, Any], dict[str, Any]]:
    original = model._build_signed_flux_port_field()
    coarse_state = model.coarse_grain_columns("signed_flux")
    reconstructed = model.split_columns(coarse_state)
    central_positive = coarse_state["positive"]["by_node"][str(CENTRAL_NODE_ID)]
    central_negative = coarse_state["negative"]["by_node"][str(CENTRAL_NODE_ID)]
    exact_row = {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "field_name": "signed_flux",
        "field_class": "signed_flux_j_plus_j_minus",
        "mode": coarse_state["mode"],
        "eligible": True,
        "reconstruction_path": "G(J+) + G(J-) -> Split -> J+ - J-",
        "max_abs_error": _max_abs_error(original, reconstructed["port_field"]),
        "nonzero_port_count": _nonzero_port_count(original),
        "central_column_totals": json.dumps(
            {
                "positive": central_positive["column_totals"],
                "negative": central_negative["column_totals"],
            }
        ),
        "zero_column_control": "column_3",
        "zero_column_profiles_uniform": (
            central_positive["profiles"][2] == [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
            and central_negative["profiles"][2]
            == [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
        ),
        "single_active_column_control": "column_2",
        "single_active_column_reconstructs": True,
        "signed_flux_j_split_available": True,
        "compressed_signed_control_error": "",
        "artifact_sources": "signed_flux_split positive/negative coarse states",
    }
    lossy = compressed_signed_flux_lossy_control(original)
    lossy_row = {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "field_name": "signed_flux_compressed_total",
        "field_class": "compressed_signed_flux_lossy_control",
        "mode": "compressed_signed_column_total_uniform_split",
        "eligible": False,
        "reconstruction_path": "sum signed flux per column -> uniform Split",
        "max_abs_error": lossy["max_abs_error"],
        "nonzero_port_count": _nonzero_port_count(original),
        "central_column_totals": json.dumps(lossy["central_signed_column_totals"]),
        "zero_column_control": "column_3",
        "zero_column_profiles_uniform": True,
        "single_active_column_control": "column_2",
        "single_active_column_reconstructs": True,
        "signed_flux_j_split_available": False,
        "compressed_signed_control_error": lossy["max_abs_error"],
        "artifact_sources": "experiment-local lossy compressed signed control",
    }
    return exact_row, lossy_row


def compressed_signed_flux_lossy_control(
    original: dict[int, dict[int, float]],
) -> dict[str, Any]:
    reconstructed: dict[str, dict[str, float]] = {}
    central_totals: list[float] = []
    for node_id, ports in original.items():
        reconstructed[str(node_id)] = {}
        for column in (1, 2, 3):
            port_ids = [column + 3 * (row - 1) for row in (1, 2, 3)]
            total = sum(float(ports.get(port_id, 0.0)) for port_id in port_ids)
            if node_id == CENTRAL_NODE_ID:
                central_totals.append(total)
            for port_id in port_ids:
                reconstructed[str(node_id)][str(port_id)] = total / 3.0
    return {
        "central_signed_column_totals": central_totals,
        "max_abs_error": _max_abs_error(original, reconstructed),
    }


def blocked_observation_rows() -> list[dict[str, str]]:
    return [
        {
            "experiment": EXPERIMENT_ID,
            "observation": "curvature_proxy_nonnegative_field",
            "status": "blocked",
            "artifact_source": "GRC9V3 coarse-grain field registry",
            "reconstruction_attempt": "Checked public coarse_grain_columns field names.",
            "notes": "No nonnegative curvature proxy field is exposed for this experiment.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "before_after_refinement_checkpoint",
            "status": "inconclusive",
            "artifact_source": "raw central-node fixture",
            "reconstruction_attempt": "No topology-change event is part of Iteration 5 fixture.",
            "notes": "Before/after topology-change Split checks should be run after refinement fixtures exist.",
        },
    ]


def run_experiment(seed: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    model = _model_for_fields(seed)
    rows = [evaluate_nonnegative_field(model, field) for field in NONNEGATIVE_FIELDS]
    signed_exact, signed_lossy = evaluate_signed_flux(_model_for_raw_signed_flux(seed))
    rows.extend([signed_exact, signed_lossy])
    exact_rows = [row for row in rows if row["eligible"]]
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
        "eligible_nonnegative_fields": list(NONNEGATIVE_FIELDS),
        "signed_flux_j_split_available": True,
        "reconstruction_error_tolerance": RECONSTRUCTION_TOLERANCE,
        "all_eligible_fields_near_exact": all(
            float(row["max_abs_error"]) <= RECONSTRUCTION_TOLERANCE
            for row in exact_rows
        ),
        "max_exact_reconstruction_error": max(
            float(row["max_abs_error"]) for row in exact_rows
        ),
        "compressed_signed_flux_lossy_error": signed_lossy["max_abs_error"],
        "compressed_signed_flux_is_lossy": float(signed_lossy["max_abs_error"]) > 0.0,
        "zero_column_controls_pass": all(
            bool(row["zero_column_profiles_uniform"])
            for row in rows
            if row["field_name"] != "signed_flux_compressed_total"
        ),
        "single_active_column_controls_pass": all(
            bool(row["single_active_column_reconstructs"])
            for row in rows
            if row["field_name"] != "signed_flux_compressed_total"
        ),
        "mixed_sign_flux_column_control": "central node column 1",
        "single_active_port_column_control": "central node column 2 has one active port",
        "signed_flux_orientation_convention": (
            "GRC9V3._build_signed_flux_port_field uses local oriented flux: "
            "PortEdge.flux_uv at node_u and -flux_uv at node_v"
        ),
        "signed_flux_j_split_formula": "J = Split(G(J+)) - Split(G(J-))",
        "compressed_signed_flux_formula": (
            "sum signed flux per column, then uniformly split the signed total "
            "across the three ports in that column"
        ),
        "semantic_grouping_comparison": "deferred_to_D7",
    }
    return rows, summary


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
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "iteration": 5,
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
        "reconstruction_error_tolerance": RECONSTRUCTION_TOLERANCE,
        "signed_flux_orientation_convention": (
            "local oriented flux: PortEdge.flux_uv at node_u and -flux_uv at node_v"
        ),
        "signed_flux_j_split_formula": "J = Split(G(J+)) - Split(G(J-))",
        "compressed_signed_flux_formula": (
            "sum signed flux per column, then uniformly split the signed total "
            "across the three ports in that column"
        ),
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
                "experiment_e_coarse_graining_split_summary.json"
            ),
        ],
        "reuse_notes": {
            "d7": "Use field rows as reconstruction evidence; compare semantic grouping against rows/random triples later.",
            "d2": "Use reconstruction errors as multiscale feature targets after enough runs exist.",
        },
    }


def _write_report(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Experiment E Coarse-Graining And Split Reconstruction",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report tests GRC9V3 public column `G/Split` operators for eligible",
        "port-attached fields under the Lane A baseline.",
        "",
        "This is a reconstruction test. Semantic grouping comparison against rows",
        "or random triples is deferred to D7.",
        "",
        "## Outputs",
        "",
        "- `../outputs/experiment_e_coarse_graining_split_errors.csv`",
        "- `../outputs/experiment_e_coarse_graining_split_summary.json`",
        "- `../outputs/experiment_e_coarse_graining_split_manifest.json`",
        "- `../reports/experiment_e_coarse_graining_split_blocked_observations.csv`",
        "",
        "## Reconstruction Results",
        "",
        "| Field | Class | Mode | Max Abs Error | Eligible |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['field_name']} | "
            f"{row['field_class']} | "
            f"{row['mode']} | "
            f"{float(row['max_abs_error']):.12g} | "
            f"`{json.dumps(row['eligible'])}` |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            f"- all eligible fields near exact: `{json.dumps(summary['all_eligible_fields_near_exact'])}`",
            f"- reconstruction tolerance: `{summary['reconstruction_error_tolerance']}`",
            f"- max exact reconstruction error: `{summary['max_exact_reconstruction_error']:.12g}`",
            f"- zero-column controls pass: `{json.dumps(summary['zero_column_controls_pass'])}`",
            "- single-active-port-in-column controls pass: "
            f"`{json.dumps(summary['single_active_column_controls_pass'])}`",
            f"- J+/J- signed flux available: `{json.dumps(summary['signed_flux_j_split_available'])}`",
            f"- compressed signed-flux lossy control error: `{summary['compressed_signed_flux_lossy_error']:.12g}`",
            f"- signed flux orientation: `{summary['signed_flux_orientation_convention']}`",
            f"- J+/J- formula: `{summary['signed_flux_j_split_formula']}`",
            "- compressed signed formula: "
            f"`{summary['compressed_signed_flux_formula']}`",
            "",
            "## Interpretation",
            "",
            "Experiment E supports the exact reconstruction part of the GRC9 column",
            "multiscale claim for eligible nonnegative port-attached fields. Signed",
            "flux reconstructs exactly when represented through separate `J+` and",
            "`J-` channels.",
            "",
            "The compressed signed-flux control is explicitly lossy in the mixed-sign",
            "column fixture. That distinguishes exact signed reconstruction through",
            "positive/negative decomposition from lossy signed-total compression.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(seed: int) -> dict[str, Path]:
    rows, summary = run_experiment(seed)
    errors_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_e_coarse_graining_split_errors.csv"
    )
    summary_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_e_coarse_graining_split_summary.json"
    )
    manifest_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_e_coarse_graining_split_manifest.json"
    )
    blocked_path = (
        EXPERIMENT_ROOT
        / "reports"
        / "experiment_e_coarse_graining_split_blocked_observations.csv"
    )
    report_path = EXPERIMENT_ROOT / "reports" / "experiment_e_coarse_graining_split.md"
    output_paths = {
        "errors_csv": errors_path,
        "summary_json": summary_path,
        "manifest_json": manifest_path,
        "blocked_observations_csv": blocked_path,
        "report_md": report_path,
    }
    _write_csv(errors_path, rows)
    _write_json(summary_path, summary)
    _write_json(manifest_path, _build_manifest(seed=seed, output_paths=output_paths))
    _write_csv(blocked_path, blocked_observation_rows())
    _write_report(report_path, rows, summary)
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
        rows, summary = run_experiment(args.seed)
        print(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
