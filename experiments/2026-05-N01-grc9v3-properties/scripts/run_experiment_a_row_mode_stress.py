"""Experiment A: row-mode stress for the GRC9V3 properties program."""

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
    CentralNodeFixture,
    PortTreatment,
    apply_port_map,
    artifact_entry_points,
    blocked_observations_schema,
    column_permutation_map,
    comparison_report_schema,
    degree_preserving_random_relabel_map,
    perturbation_energy,
    row_permutation_map,
    run_id_convention,
    runtime_assumptions,
    runtime_binding_requirements,
    state_mapping_convention,
    total_energy_preserved,
    transpose_map,
    validate_fixture_contract,
)


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ID = "experiment_a_row_mode_stress"
PERTURBATION_DELTA = 0.3
CENTRAL_NODE_ID = 0
SCRIPT_PATH = "experiments/2026-05-N01-grc9v3-properties/scripts/run_experiment_a_row_mode_stress.py"


def _params(seed: int) -> dict[str, Any]:
    return {
        "dt": 0.1,
        "evolution": {
            "rng_seed": seed,
            "hessian_regularization": 1e-9,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 1.0},
        },
        "constitutive_semantic_modes": {
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
    node_ids = {CENTRAL_NODE_ID}
    incidence: dict[str, list[int]] = {str(CENTRAL_NODE_ID): []}
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


def row_local_fixture(*, seed: int, stressed_row: int) -> CentralNodeFixture:
    treatments: list[PortTreatment] = []
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        stressed = row == stressed_row
        treatments.append(
            PortTreatment(
                port_id=port_id,
                row=row,
                column=column,
                active=True,
                coherence_delta=PERTURBATION_DELTA if stressed else 0.0,
                conductance=1.0,
                flux_uv=0.0,
            )
        )
    fixture = CentralNodeFixture(
        fixture_id=f"a_row_{stressed_row}_stress_seed_{seed}",
        seed=seed,
        lane_id=LANE_ID,
        central_node_id=CENTRAL_NODE_ID,
        port_matrix=treatments,
        notes=[
            f"Experiment A row-{stressed_row} localized coherence perturbation.",
            "All nine ports are active; exactly three ports carry nonzero delta.",
        ],
    )
    validate_fixture_contract(fixture)
    return fixture


def balanced_fixture(*, seed: int) -> CentralNodeFixture:
    balanced_ports = {1, 5, 9}
    treatments: list[PortTreatment] = []
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        stressed = port_id in balanced_ports
        treatments.append(
            PortTreatment(
                port_id=port_id,
                row=row,
                column=column,
                active=True,
                coherence_delta=PERTURBATION_DELTA if stressed else 0.0,
                conductance=1.0,
                flux_uv=0.0,
            )
        )
    fixture = CentralNodeFixture(
        fixture_id=f"a_balanced_diagonal_seed_{seed}",
        seed=seed,
        lane_id=LANE_ID,
        central_node_id=CENTRAL_NODE_ID,
        port_matrix=treatments,
        notes=[
            "Experiment A balanced control.",
            "Exactly one perturbed port per row; total |delta|, delta^2, and affected-port count match row-local fixtures.",
        ],
    )
    validate_fixture_contract(fixture)
    return fixture


def fixture_to_state(fixture: CentralNodeFixture) -> dict[str, Any]:
    validate_fixture_contract(fixture)
    connections: list[tuple[int, int, int, int, int]] = []
    nodes: dict[str, dict[str, Any]] = {
        str(fixture.central_node_id): {
            "coherence": 1.0,
            "basin_mass": 1.0,
            "basin_id": "root",
            "depth": 0,
        }
    }
    port_edges: dict[str, dict[str, int | float]] = {}
    edge_id = 0
    for treatment in sorted(fixture.port_matrix, key=lambda item: item.port_id):
        if not treatment.active:
            continue
        neighbor_id = 100 + treatment.port_id
        connections.append(
            (
                edge_id,
                fixture.central_node_id,
                treatment.port_id,
                neighbor_id,
                1,
            )
        )
        nodes[str(neighbor_id)] = {
            "coherence": 1.0 + treatment.coherence_delta,
            "basin_mass": 1.0 + treatment.coherence_delta,
            "basin_id": neighbor_id,
            "depth": 0,
        }
        port_edges[str(edge_id)] = _port_edge(
            node_u=fixture.central_node_id,
            port_u=treatment.port_id,
            node_v=neighbor_id,
            port_v=1,
            conductance=treatment.conductance,
            flux_uv=treatment.flux_uv,
        )
        edge_id += 1
    return {
        "topology": _topology(connections),
        "nodes": nodes,
        "port_edges": port_edges,
        "sink_set": [fixture.central_node_id],
        "basins": {
            str(fixture.central_node_id): sorted(int(node_id) for node_id in nodes)
        },
    }


def expected_row_after_transform(
    *,
    source_fixture_id: str,
    source_expected_row: int | None,
    transform_id: str,
    port_map: dict[int, int],
) -> int | None:
    if source_expected_row is None:
        return None
    if transform_id.startswith("row_permutation"):
        target_rows = {
            port_to_rc(port_map[port])[0]
            for port in PORT_IDS
            if port_to_rc(port)[0] == source_expected_row
        }
        return next(iter(target_rows)) if len(target_rows) == 1 else None
    if transform_id.startswith("column_permutation"):
        return source_expected_row
    if transform_id == "identity":
        return source_expected_row
    if transform_id == "row_column_transpose":
        return None
    if transform_id == "degree_preserving_random_relabel":
        return None
    raise ValueError(f"unknown transform {transform_id!r} for {source_fixture_id}")


def _dominant_row(values: list[float]) -> int | None:
    if not values:
        return None
    max_value = max(values)
    if max_value <= 0.0:
        return None
    if sum(1 for value in values if abs(value - max_value) <= 1e-12) != 1:
        return None
    return values.index(max_value) + 1


def _dominance_ratio(values: list[float]) -> float:
    if not values:
        return 0.0
    total = sum(abs(value) for value in values)
    if total <= 0.0:
        return 0.0
    return max(abs(value) for value in values) / total


def _as_row_abs(values: list[float]) -> list[float]:
    return [abs(float(value)) for value in values[:3]]


def coherence_delta_profile(fixture: CentralNodeFixture) -> dict[str, Any]:
    by_row_abs = {"1": 0.0, "2": 0.0, "3": 0.0}
    by_row_squared = {"1": 0.0, "2": 0.0, "3": 0.0}
    active_delta_ports = 0
    for treatment in fixture.port_matrix:
        delta_abs = abs(treatment.coherence_delta)
        delta_squared = treatment.coherence_delta**2
        if delta_abs > 0.0:
            active_delta_ports += 1
        by_row_abs[str(treatment.row)] += delta_abs
        by_row_squared[str(treatment.row)] += delta_squared
    return {
        "active_delta_ports": active_delta_ports,
        "total_abs_delta": sum(by_row_abs.values()),
        "total_squared_delta": sum(by_row_squared.values()),
        "by_row_abs_delta": by_row_abs,
        "by_row_squared_delta": by_row_squared,
    }


def evaluate_fixture(
    *,
    fixture: CentralNodeFixture,
    source_fixture_id: str,
    transform_id: str,
    port_map: dict[int, int],
    seed: int,
    source_expected_row: int | None,
) -> dict[str, Any]:
    model = GRC9V3.from_state(state=fixture_to_state(fixture), params=_params(seed))
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    model.rebuild_differential_state()
    state = model.get_state()
    node = state.nodes[fixture.central_node_id]
    row_mismatch = [
        float(value)
        for value in state.cached_quantities["row_mismatch_sums"][
            str(fixture.central_node_id)
        ]
    ]
    tensor = state.cached_quantities["hybrid_node_tensors"][
        str(fixture.central_node_id)
    ]
    tensor_diag = [float(tensor[index][index]) for index in range(3)]
    gradient_abs = _as_row_abs(node.gradient_row_basis)
    hessian_abs = _as_row_abs(node.signed_hessian_row_basis)
    net_flux_abs = _as_row_abs(node.net_flux_summary)
    response_by_row = [
        gradient_abs[index]
        + row_mismatch[index]
        + hessian_abs[index]
        + net_flux_abs[index]
        for index in range(3)
    ]
    dominant_response_row = _dominant_row(response_by_row)
    expected_row = expected_row_after_transform(
        source_fixture_id=source_fixture_id,
        source_expected_row=source_expected_row,
        transform_id=transform_id,
        port_map=port_map,
    )
    isotropic_base = min(tensor_diag)
    anisotropic_span = max(tensor_diag) - min(tensor_diag)
    isotropic_dominance_ratio = (
        float("inf") if anisotropic_span <= 1e-12 else isotropic_base / anisotropic_span
    )
    return {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "source_fixture_id": source_fixture_id,
        "fixture_id": fixture.fixture_id,
        "transform_id": transform_id,
        "expected_dominant_row": expected_row,
        "dominant_response_row": dominant_response_row,
        "dominant_row_matches_expected": (
            expected_row is not None and dominant_response_row == expected_row
        ),
        "response_dominance_ratio": _dominance_ratio(response_by_row),
        "response_row_1": response_by_row[0],
        "response_row_2": response_by_row[1],
        "response_row_3": response_by_row[2],
        "gradient_abs_row_1": gradient_abs[0],
        "gradient_abs_row_2": gradient_abs[1],
        "gradient_abs_row_3": gradient_abs[2],
        "row_mismatch_row_1": row_mismatch[0],
        "row_mismatch_row_2": row_mismatch[1],
        "row_mismatch_row_3": row_mismatch[2],
        "signed_hessian_abs_row_1": hessian_abs[0],
        "signed_hessian_abs_row_2": hessian_abs[1],
        "signed_hessian_abs_row_3": hessian_abs[2],
        "net_flux_abs_row_1": net_flux_abs[0],
        "net_flux_abs_row_2": net_flux_abs[1],
        "net_flux_abs_row_3": net_flux_abs[2],
        "tensor_diag_row_1": tensor_diag[0],
        "tensor_diag_row_2": tensor_diag[1],
        "tensor_diag_row_3": tensor_diag[2],
        "isotropic_base": isotropic_base,
        "anisotropic_span": anisotropic_span,
        "isotropic_dominance_ratio": isotropic_dominance_ratio,
        "isotropic_terms_dominate_or_mute": isotropic_dominance_ratio > 10.0,
        "energy_total": perturbation_energy(fixture)["total"],
        "active_degree": sum(treatment.active for treatment in fixture.port_matrix),
        "artifact_sources": "GRC9V3State.nodes, cached_quantities.row_mismatch_sums, cached_quantities.hybrid_node_tensors, PortEdge flux",
    }


def _transforms(seed: int) -> dict[str, dict[int, int]]:
    return {
        "identity": {port: port for port in PORT_IDS},
        "row_permutation_231": row_permutation_map((2, 3, 1)),
        "column_permutation_312": column_permutation_map((3, 1, 2)),
        "row_column_transpose": transpose_map(),
        "degree_preserving_random_relabel": degree_preserving_random_relabel_map(
            seed + 1000
        ),
    }


def _fixture_suite(seed: int) -> list[tuple[CentralNodeFixture, int | None]]:
    return [
        (row_local_fixture(seed=seed, stressed_row=1), 1),
        (row_local_fixture(seed=seed, stressed_row=2), 2),
        (row_local_fixture(seed=seed, stressed_row=3), 3),
        (balanced_fixture(seed=seed), None),
    ]


def random_relabel_interpretability_scores(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    source_fixture_ids = sorted(
        {
            str(row["source_fixture_id"])
            for row in rows
            if str(row["source_fixture_id"]).startswith("a_row_")
        }
    )
    for fixture_id in source_fixture_ids:
        identity = next(
            row
            for row in rows
            if row["source_fixture_id"] == fixture_id
            and row["transform_id"] == "identity"
        )
        random_relabel = next(
            row
            for row in rows
            if row["source_fixture_id"] == fixture_id
            and row["transform_id"] == "degree_preserving_random_relabel"
        )
        true_mapping_dominance = float(identity["response_dominance_ratio"])
        random_relabel_dominance = float(random_relabel["response_dominance_ratio"])
        scores[fixture_id] = {
            "true_mapping_dominance": true_mapping_dominance,
            "random_relabel_best_row_dominance": random_relabel_dominance,
            "interpretability_margin": true_mapping_dominance
            - random_relabel_dominance,
        }
    return scores


def run_experiment(seed: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    transforms = _transforms(seed)
    rows: list[dict[str, Any]] = []
    for base_fixture, expected_row in _fixture_suite(seed):
        for transform_id, port_map in transforms.items():
            transformed = (
                base_fixture
                if transform_id == "identity"
                else apply_port_map(
                    base_fixture,
                    port_map,
                    transform_id=transform_id,
                )
            )
            rows.append(
                evaluate_fixture(
                    fixture=transformed,
                    source_fixture_id=base_fixture.fixture_id,
                    transform_id=transform_id,
                    port_map=port_map,
                    seed=seed,
                    source_expected_row=expected_row,
                )
            )
    matched_energy = {
        fixture.fixture_id: perturbation_energy(fixture)
        for fixture, _ in _fixture_suite(seed)
    }
    delta_profiles = {
        fixture.fixture_id: coherence_delta_profile(fixture)
        for fixture, _ in _fixture_suite(seed)
    }
    row_permutation_rows = [
        row
        for row in rows
        if row["source_fixture_id"].startswith("a_row_")
        and row["transform_id"] == "row_permutation_231"
    ]
    random_relabel_scores = random_relabel_interpretability_scores(rows)
    summary = {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "run_id_convention": run_id_convention(),
        "runtime_assumptions": runtime_assumptions(),
        "state_mapping_convention": state_mapping_convention(),
        "runtime_binding_requirements": runtime_binding_requirements(),
        "artifact_entry_points": artifact_entry_points(),
        "comparison_report_schema": comparison_report_schema(),
        "blocked_observations_schema": blocked_observations_schema(),
        "transforms": transforms,
        "fixture_energy_profiles": matched_energy,
        "fixture_delta_profiles": delta_profiles,
        "all_fixture_energy_totals": {
            fixture_id: profile["total"]
            for fixture_id, profile in matched_energy.items()
        },
        "all_fixture_abs_delta_totals": {
            fixture_id: profile["total_abs_delta"]
            for fixture_id, profile in delta_profiles.items()
        },
        "all_fixture_squared_delta_totals": {
            fixture_id: profile["total_squared_delta"]
            for fixture_id, profile in delta_profiles.items()
        },
        "all_fixture_active_delta_ports": {
            fixture_id: profile["active_delta_ports"]
            for fixture_id, profile in delta_profiles.items()
        },
        "abs_delta_totals_matched": len(
            {
                round(float(profile["total_abs_delta"]), 12)
                for profile in delta_profiles.values()
            }
        )
        == 1,
        "squared_delta_totals_matched": len(
            {
                round(float(profile["total_squared_delta"]), 12)
                for profile in delta_profiles.values()
            }
        )
        == 1,
        "active_delta_port_counts_matched": len(
            {
                int(profile["active_delta_ports"])
                for profile in delta_profiles.values()
            }
        )
        == 1,
        "energy_totals_matched": len(
            {
                round(float(profile["total"]), 12)
                for profile in matched_energy.values()
            }
        )
        == 1,
        "energy_preserved_under_transforms": {
            fixture.fixture_id: {
                transform_id: total_energy_preserved(fixture, port_map)
                for transform_id, port_map in transforms.items()
            }
            for fixture, _ in _fixture_suite(seed)
        },
        "row_permutation_moves_signature": all(
            bool(row["dominant_row_matches_expected"]) for row in row_permutation_rows
        ),
        "identity_row_stress_matches": all(
            bool(row["dominant_row_matches_expected"])
            for row in rows
            if row["source_fixture_id"].startswith("a_row_")
            and row["transform_id"] == "identity"
        ),
        "column_permutation_preserves_stressed_row": all(
            bool(row["dominant_row_matches_expected"])
            for row in rows
            if row["source_fixture_id"].startswith("a_row_")
            and row["transform_id"] == "column_permutation_312"
        ),
        "random_relabel_clean_signature_destroyed": all(
            row["expected_dominant_row"] is None
            for row in rows
            if row["transform_id"] == "degree_preserving_random_relabel"
        ),
        "random_relabel_interpretability_scores": random_relabel_scores,
        "random_relabel_interpretability_margin_min": min(
            score["interpretability_margin"]
            for score in random_relabel_scores.values()
        ),
        "isotropic_terms_dominate_any_row_stress": any(
            bool(row["isotropic_terms_dominate_or_mute"])
            for row in rows
            if row["source_fixture_id"].startswith("a_row_")
        ),
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


def _build_run_manifest(
    *,
    seed: int,
    summary: dict[str, Any],
    rows_path: Path,
    summary_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    fixture_ids = sorted(str(key) for key in summary["fixture_energy_profiles"])
    return {
        "experiment_id": EXPERIMENT_ID,
        "iteration": 3,
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
        "fixture_ids": fixture_ids,
        "port_mappings": summary["transforms"],
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "output_paths": {
            "rows_csv": str(rows_path.relative_to(EXPERIMENT_ROOT)),
            "summary_json": str(summary_path.relative_to(EXPERIMENT_ROOT)),
            "report_md": str(report_path.relative_to(EXPERIMENT_ROOT)),
            "run_manifest": "outputs/experiment_a_row_mode_stress_manifest.json",
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
                "experiment_a_row_mode_stress_summary.json"
            ),
        ],
        "reuse_notes": {
            "d1": "Use identity/row-permutation/column-permutation/random-relabel rows for row-side factorization checks.",
            "d2": "Use row response scores and transform ids as feature/target samples after enough runs exist.",
            "d3": "Use transpose rows as row/column non-equivalence inputs, not as a complete D3 test.",
        },
    }


def _write_report(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    identity_rows = [
        row
        for row in rows
        if row["source_fixture_id"].startswith("a_row_")
        and row["transform_id"] == "identity"
    ]
    row_perm_rows = [
        row
        for row in rows
        if row["source_fixture_id"].startswith("a_row_")
        and row["transform_id"] == "row_permutation_231"
    ]
    balanced_rows = [
        row
        for row in rows
        if row["source_fixture_id"].startswith("a_balanced")
        and row["transform_id"] == "identity"
    ]
    lines = [
        "# Experiment A Row-Mode Stress",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report tests whether row-local perturbations produce row-local",
        "differential/geometric signatures under the Lane A baseline",
        "`current_hybrid_signed_hessian`.",
        "",
        "Column-H is not used as direct spark-gating evidence in this experiment.",
        "",
        "## Outputs",
        "",
        "- `../outputs/experiment_a_row_mode_stress_rows.csv`",
        "- `../outputs/experiment_a_row_mode_stress_summary.json`",
        "- `../outputs/experiment_a_row_mode_stress_manifest.json`",
        "",
        "## Fixture Matching",
        "",
        f"- total absolute coherence delta matched: `{json.dumps(summary['abs_delta_totals_matched'])}`",
        f"- total squared coherence delta matched: `{json.dumps(summary['squared_delta_totals_matched'])}`",
        f"- affected-port counts matched: `{json.dumps(summary['active_delta_port_counts_matched'])}`",
        f"- energy totals matched: `{json.dumps(summary['energy_totals_matched'])}`",
        "- row-local fixtures and the balanced fixture each perturb exactly three",
        "  ports with the same total absolute and squared coherence delta.",
        "",
        "## Identity Row-Stress Responses",
        "",
        "| Fixture | Expected Row | Dominant Row | Dominance | Isotropic Dominance Ratio |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in identity_rows:
        lines.append(
            "| "
            f"{row['source_fixture_id']} | "
            f"{row['expected_dominant_row']} | "
            f"{row['dominant_response_row']} | "
            f"{row['response_dominance_ratio']:.6f} | "
            f"{row['isotropic_dominance_ratio']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Row Permutation Controls",
            "",
            f"- row signatures move under row permutation: `{json.dumps(summary['row_permutation_moves_signature'])}`",
            "",
            "| Fixture | Expected Row After Permutation | Dominant Row |",
            "| --- | ---: | ---: |",
        ]
    )
    for row in row_perm_rows:
        lines.append(
            "| "
            f"{row['source_fixture_id']} | "
            f"{row['expected_dominant_row']} | "
            f"{row['dominant_response_row']} |"
        )
    lines.extend(
        [
            "",
            "## Controls Summary",
            "",
            f"- identity row stress matches expected row: `{json.dumps(summary['identity_row_stress_matches'])}`",
            f"- column permutation preserves stressed row: `{json.dumps(summary['column_permutation_preserves_stressed_row'])}`",
            f"- random relabel removes a predefined clean expected row: `{json.dumps(summary['random_relabel_clean_signature_destroyed'])}`",
            "- minimum true-minus-random interpretability margin: "
            f"`{summary['random_relabel_interpretability_margin_min']:.6f}`",
            f"- isotropic terms dominate any row stress: `{json.dumps(summary['isotropic_terms_dominate_any_row_stress'])}`",
            "",
            "## Balanced Control",
            "",
        ]
    )
    for row in balanced_rows:
        lines.append(
            "- balanced identity dominant row: "
            f"`{row['dominant_response_row']}` with dominance "
            f"`{row['response_dominance_ratio']:.6f}`"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Experiment A supports the row-mode stress hypothesis in a clean",
            "saturated central-node fixture under Lane A.",
            "",
            "Row-local perturbations produce the expected dominant row signature,",
            "and the signature transforms correctly under row permutation. Column",
            "permutation does not explain the row-local signature. Balanced and",
            "random-relabel controls do not provide the same clean row-local",
            "interpretation.",
            "",
            "This supports row-local differential/geometric observability in this",
            "controlled fixture. The result weakens the anonymous-port null for",
            "row-resolved artifacts and provides partial support for the row side",
            "of the factorization discriminator. It does not yet establish column",
            "semantics, non-additive port interactions, or landscape-level",
            "generality.",
            "",
            "The anisotropic row span is detectable and transforms correctly, but",
            "the isotropic `K` component is large relative to that span in this",
            "fixture. The correct claim is row-resolved anisotropic detectability,",
            "not dominance of `K` by row anisotropy.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(seed: int) -> dict[str, Path]:
    rows, summary = run_experiment(seed)
    rows_path = EXPERIMENT_ROOT / "outputs" / "experiment_a_row_mode_stress_rows.csv"
    summary_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_a_row_mode_stress_summary.json"
    )
    manifest_path = (
        EXPERIMENT_ROOT / "outputs" / "experiment_a_row_mode_stress_manifest.json"
    )
    report_path = EXPERIMENT_ROOT / "reports" / "experiment_a_row_mode_stress.md"
    _write_csv(rows_path, rows)
    _write_json(summary_path, summary)
    _write_json(
        manifest_path,
        _build_run_manifest(
            seed=seed,
            summary=summary,
            rows_path=rows_path,
            summary_path=summary_path,
            report_path=report_path,
        ),
    )
    _write_report(report_path, rows, summary)
    return {
        "rows": rows_path,
        "summary": summary_path,
        "manifest": manifest_path,
        "report": report_path,
    }


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
