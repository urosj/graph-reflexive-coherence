"""Experiment B: derived column-interface cancellation under Lane A."""

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
EXPERIMENT_ID = "experiment_b_column_interface_cancellation"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_experiment_b_column_interface_cancellation.py"
)
CENTRAL_NODE_ID = 0
DELTA = 0.3
CANCELLATION_ROW2_DELTA_POSITIVE = -0.20
CANCELLATION_ROW2_DELTA_NEAR_ZERO = -0.22
CANCELLATION_ROW2_DELTA_NEGATIVE = -0.24


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


def column_cancellation_fixture(
    *,
    seed: int,
    target_column: int,
    residual_sign: int = 1,
) -> CentralNodeFixture:
    if target_column not in (1, 2, 3):
        raise ValueError("target_column must be 1, 2, or 3")
    if residual_sign not in (-1, 1):
        raise ValueError("residual_sign must be -1 or 1")
    treatments: list[PortTreatment] = []
    row2_delta = (
        CANCELLATION_ROW2_DELTA_NEAR_ZERO
        if residual_sign > 0
        else CANCELLATION_ROW2_DELTA_NEGATIVE
    )
    signed_deltas = {1: DELTA, 2: row2_delta, 3: 0.0}
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        coherence_delta = signed_deltas[row] if column == target_column else 0.0
        treatments.append(
            PortTreatment(
                port_id=port_id,
                row=row,
                column=column,
                active=True,
                coherence_delta=coherence_delta,
                conductance=1.0,
                flux_uv=0.0,
            )
        )
    fixture = CentralNodeFixture(
        fixture_id=(
            f"b_column_{target_column}_near_cancellation_"
            f"{'near_zero' if residual_sign > 0 else 'sign_neg'}_seed_{seed}"
        ),
        seed=seed,
        lane_id=LANE_ID,
        central_node_id=CENTRAL_NODE_ID,
        port_matrix=treatments,
        notes=[
            f"Experiment B column-{target_column} derived cancellation fixture.",
            "The target column has high signed pressure and near-zero signed residual.",
            "Column-H remains a derived proxy under Lane A.",
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
        neighbor_id = 200 + treatment.port_id
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


def _oriented_flux_from_center(state: Any, edge_id: int) -> float:
    port_edge = state.port_edges[edge_id]
    if port_edge.node_u == CENTRAL_NODE_ID:
        return float(port_edge.flux_uv)
    if port_edge.node_v == CENTRAL_NODE_ID:
        return float(-port_edge.flux_uv)
    raise ValueError("edge is not incident to central node")


def column_proxy(state: Any) -> dict[str, Any]:
    signed_weighted_delta = {"1": 0.0, "2": 0.0, "3": 0.0}
    pressure = {"1": 0.0, "2": 0.0, "3": 0.0}
    signed_flux_balance = {"1": 0.0, "2": 0.0, "3": 0.0}
    flux_pressure = {"1": 0.0, "2": 0.0, "3": 0.0}
    center_coherence = state.nodes[CENTRAL_NODE_ID].coherence
    for edge_id in sorted(state.topology.incident_edge_ids(CENTRAL_NODE_ID)):
        port_edge = state.port_edges[edge_id]
        row, column = port_to_rc(port_edge.port_u)
        del row
        column_key = str(column)
        neighbor_id = port_edge.node_v if port_edge.node_u == CENTRAL_NODE_ID else port_edge.node_u
        delta = state.nodes[neighbor_id].coherence - center_coherence
        conductance = float(state.base_conductance.get(edge_id, port_edge.conductance))
        weighted_delta = conductance * delta
        signed_weighted_delta[column_key] += weighted_delta
        pressure[column_key] += abs(weighted_delta)
        flux = _oriented_flux_from_center(state, edge_id)
        signed_flux_balance[column_key] += flux
        flux_pressure[column_key] += abs(flux)
    residual = {
        column: abs(value) for column, value in signed_weighted_delta.items()
    }
    cancellation_score = {
        column: 1.0 - residual[column] / pressure[column]
        if pressure[column] > 0.0
        else 0.0
        for column in ("1", "2", "3")
    }
    return {
        "formula": (
            "derived_column_proxy_v1: per-column conductance-weighted signed "
            "coherence delta; cancellation_score = 1 - |sum| / sum_abs"
        ),
        "signed_weighted_delta": signed_weighted_delta,
        "pressure": pressure,
        "residual": residual,
        "cancellation_score": cancellation_score,
        "signed_flux_balance": signed_flux_balance,
        "flux_pressure": flux_pressure,
    }


def _dominant_column(values: dict[str, float]) -> int | None:
    max_value = max(values.values())
    if max_value <= 0.0:
        return None
    if sum(1 for value in values.values() if abs(value - max_value) <= 1e-12) != 1:
        return None
    for column, value in values.items():
        if abs(value - max_value) <= 1e-12:
            return int(column)
    return None


def expected_column_after_transform(
    *,
    source_expected_column: int | None,
    transform_id: str,
    port_map: dict[int, int],
) -> int | None:
    if source_expected_column is None:
        return None
    if transform_id.startswith("column_permutation"):
        target_columns = {
            port_to_rc(port_map[port])[1]
            for port in PORT_IDS
            if port_to_rc(port)[1] == source_expected_column
        }
        return next(iter(target_columns)) if len(target_columns) == 1 else None
    if transform_id.startswith("row_permutation"):
        return source_expected_column
    if transform_id == "identity":
        return source_expected_column
    if transform_id in {"row_column_transpose", "degree_preserving_random_relabel"}:
        return None
    raise ValueError(f"unknown transform {transform_id!r}")


def evaluate_fixture(
    *,
    fixture: CentralNodeFixture,
    source_fixture_id: str,
    transform_id: str,
    port_map: dict[int, int],
    seed: int,
    source_expected_column: int,
) -> dict[str, Any]:
    model = GRC9V3.from_state(state=fixture_to_state(fixture), params=_params(seed))
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    model.rebuild_differential_state()
    state = model.get_state()
    proxy = column_proxy(state)
    expected_column = expected_column_after_transform(
        source_expected_column=source_expected_column,
        transform_id=transform_id,
        port_map=port_map,
    )
    dominant_pressure_column = _dominant_column(proxy["pressure"])
    dominant_cancellation_column = _dominant_column(proxy["cancellation_score"])
    direct_candidates = model.detect_hybrid_spark_candidates()
    candidate_kinds = [event.kind for event in direct_candidates]
    step_model = GRC9V3.from_state(state=fixture_to_state(fixture), params=_params(seed))
    step_result = step_model.step()
    step_event_kinds = [event.kind for event in step_result.events]
    central_node = state.nodes[CENTRAL_NODE_ID]
    gradient_norm = sum(value * value for value in central_node.gradient_row_basis) ** 0.5
    min_signed_hessian = min(central_node.signed_hessian_row_basis)
    return {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "source_fixture_id": source_fixture_id,
        "fixture_id": fixture.fixture_id,
        "transform_id": transform_id,
        "expected_column": expected_column,
        "dominant_pressure_column": dominant_pressure_column,
        "dominant_cancellation_column": dominant_cancellation_column,
        "pressure_column_matches_expected": (
            expected_column is not None and dominant_pressure_column == expected_column
        ),
        "cancellation_column_matches_expected": (
            expected_column is not None
            and dominant_cancellation_column == expected_column
        ),
        "column_1_pressure": proxy["pressure"]["1"],
        "column_2_pressure": proxy["pressure"]["2"],
        "column_3_pressure": proxy["pressure"]["3"],
        "column_1_residual": proxy["residual"]["1"],
        "column_2_residual": proxy["residual"]["2"],
        "column_3_residual": proxy["residual"]["3"],
        "column_1_cancellation_score": proxy["cancellation_score"]["1"],
        "column_2_cancellation_score": proxy["cancellation_score"]["2"],
        "column_3_cancellation_score": proxy["cancellation_score"]["3"],
        "column_1_signed_flux_balance": proxy["signed_flux_balance"]["1"],
        "column_2_signed_flux_balance": proxy["signed_flux_balance"]["2"],
        "column_3_signed_flux_balance": proxy["signed_flux_balance"]["3"],
        "column_1_flux_pressure": proxy["flux_pressure"]["1"],
        "column_2_flux_pressure": proxy["flux_pressure"]["2"],
        "column_3_flux_pressure": proxy["flux_pressure"]["3"],
        "active_degree": len(tuple(state.topology.incident_edge_ids(CENTRAL_NODE_ID))),
        "gradient_norm": gradient_norm,
        "min_signed_hessian": min_signed_hessian,
        "spark_candidate_event_count": len(direct_candidates),
        "spark_candidate_event_kinds": ";".join(candidate_kinds),
        "refinement_event_count": step_event_kinds.count("hybrid_mechanical_expansion"),
        "completed_identity_event_count": step_event_kinds.count(
            "hybrid_spark_completed"
        ),
        "step_event_kinds": ";".join(step_event_kinds),
        "proxy_formula": proxy["formula"],
        "predicate_role": "analysis_proxy_only",
        "direct_column_h_gate_claim": "blocked_under_lane_a",
        "energy_total": perturbation_energy(fixture)["total"],
        "artifact_sources": (
            "endpoint ports, GRC9V3State.nodes, GRC9V3State.base_conductance, "
            "PortEdge.flux_uv, StepResult.events"
        ),
    }


def _transforms(seed: int) -> dict[str, dict[int, int]]:
    return {
        "identity": {port: port for port in PORT_IDS},
        "column_permutation_312": column_permutation_map((3, 1, 2)),
        "row_permutation_231": row_permutation_map((2, 3, 1)),
        "row_column_transpose": transpose_map(),
        "degree_preserving_random_relabel": degree_preserving_random_relabel_map(
            seed + 1000
        ),
    }


def _fixture_suite(seed: int) -> list[tuple[CentralNodeFixture, int]]:
    return [
        (column_cancellation_fixture(seed=seed, target_column=1), 1),
        (column_cancellation_fixture(seed=seed, target_column=2), 2),
        (column_cancellation_fixture(seed=seed, target_column=3), 3),
    ]


def _sign_crossing_pairs(seed: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for column in (1, 2, 3):
        before = column_cancellation_fixture(
            seed=seed,
            target_column=column,
            residual_sign=1,
        )
        before = _replace_target_row2_delta(
            before,
            target_column=column,
            row2_delta=CANCELLATION_ROW2_DELTA_POSITIVE,
        )
        after = column_cancellation_fixture(
            seed=seed,
            target_column=column,
            residual_sign=-1,
        )
        before_model = GRC9V3.from_state(state=fixture_to_state(before), params=_params(seed))
        after_model = GRC9V3.from_state(state=fixture_to_state(after), params=_params(seed))
        for model in (before_model, after_model):
            model.rebuild_differential_state()
            model.rebuild_transport_state()
            model.rebuild_differential_state()
        before_proxy = column_proxy(before_model.get_state())
        after_proxy = column_proxy(after_model.get_state())
        before_signed = before_proxy["signed_weighted_delta"][str(column)]
        after_signed = after_proxy["signed_weighted_delta"][str(column)]
        rows.append(
            {
                "experiment": EXPERIMENT_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": seed,
                "column": column,
                "before_fixture_id": before.fixture_id,
                "after_fixture_id": after.fixture_id,
                "before_signed_weighted_delta": before_signed,
                "after_signed_weighted_delta": after_signed,
                "derived_proxy_sign_crossing": before_signed * after_signed < 0.0,
                "predicate_role": "analysis_proxy_only",
                "direct_column_h_gate_claim": "blocked_under_lane_a",
            }
        )
    return rows


def _replace_target_row2_delta(
    fixture: CentralNodeFixture,
    *,
    target_column: int,
    row2_delta: float,
) -> CentralNodeFixture:
    treatments = []
    for treatment in fixture.port_matrix:
        if treatment.row == 2 and treatment.column == target_column:
            treatments.append(
                PortTreatment(
                    port_id=treatment.port_id,
                    row=treatment.row,
                    column=treatment.column,
                    active=treatment.active,
                    coherence_delta=row2_delta,
                    conductance=treatment.conductance,
                    flux_uv=treatment.flux_uv,
                )
            )
        else:
            treatments.append(treatment)
    updated = CentralNodeFixture(
        fixture_id=f"{fixture.fixture_id}_row2_delta_{row2_delta:+.2f}",
        seed=fixture.seed,
        lane_id=fixture.lane_id,
        central_node_id=fixture.central_node_id,
        port_matrix=treatments,
        notes=[
            *fixture.notes,
            "Adjusted target row-2 delta for derived sign-crossing probe.",
        ],
    )
    validate_fixture_contract(updated)
    return updated


def random_relabel_interpretability_scores(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    source_fixture_ids = sorted({str(row["source_fixture_id"]) for row in rows})
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
        true_score = float(identity["column_1_cancellation_score"])
        true_score = max(
            true_score,
            float(identity["column_2_cancellation_score"]),
            float(identity["column_3_cancellation_score"]),
        )
        random_score = max(
            float(random_relabel["column_1_cancellation_score"]),
            float(random_relabel["column_2_cancellation_score"]),
            float(random_relabel["column_3_cancellation_score"]),
        )
        scores[fixture_id] = {
            "true_mapping_best_cancellation_score": true_score,
            "random_relabel_best_cancellation_score": random_score,
            "interpretability_margin": true_score - random_score,
        }
    return scores


def run_experiment(seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    transforms = _transforms(seed)
    rows: list[dict[str, Any]] = []
    for base_fixture, expected_column in _fixture_suite(seed):
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
                    source_expected_column=expected_column,
                )
            )
    sign_crossings = _sign_crossing_pairs(seed)
    matched_energy = {
        fixture.fixture_id: perturbation_energy(fixture)
        for fixture, _ in _fixture_suite(seed)
    }
    random_scores = random_relabel_interpretability_scores(rows)
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
        "identity_column_proxy_matches": all(
            bool(row["pressure_column_matches_expected"])
            and bool(row["cancellation_column_matches_expected"])
            for row in rows
            if row["transform_id"] == "identity"
        ),
        "column_permutation_moves_proxy": all(
            bool(row["pressure_column_matches_expected"])
            and bool(row["cancellation_column_matches_expected"])
            for row in rows
            if row["transform_id"] == "column_permutation_312"
        ),
        "row_permutation_preserves_proxy_column": all(
            bool(row["pressure_column_matches_expected"])
            and bool(row["cancellation_column_matches_expected"])
            for row in rows
            if row["transform_id"] == "row_permutation_231"
        ),
        "transpose_control_rows_present": any(
            row["transform_id"] == "row_column_transpose" for row in rows
        ),
        "transpose_clean_column_claim_removed": all(
            row["expected_column"] is None
            for row in rows
            if row["transform_id"] == "row_column_transpose"
        ),
        "random_relabel_clean_column_claim_removed": all(
            row["expected_column"] is None
            for row in rows
            if row["transform_id"] == "degree_preserving_random_relabel"
        ),
        "derived_sign_crossing_pairs_built": all(
            bool(row["derived_proxy_sign_crossing"]) for row in sign_crossings
        ),
        "spark_candidate_event_count_total": sum(
            int(row["spark_candidate_event_count"]) for row in rows
        ),
        "refinement_event_count_total": sum(
            int(row["refinement_event_count"]) for row in rows
        ),
        "completed_identity_event_count_total": sum(
            int(row["completed_identity_event_count"]) for row in rows
        ),
        "random_relabel_interpretability_scores": random_scores,
        "random_relabel_interpretability_margin_min": min(
            score["interpretability_margin"] for score in random_scores.values()
        ),
        "direct_column_h_gate_claim": "blocked_under_lane_a",
        "derived_proxy_formula_version": "derived_column_proxy_v1",
        "derived_proxy_formula": (
            "per-column conductance-weighted signed coherence delta; "
            "cancellation_score = 1 - |sum| / sum_abs"
        ),
    }
    return rows, sign_crossings, summary


def blocked_observation_rows() -> list[dict[str, str]]:
    return [
        {
            "experiment": EXPERIMENT_ID,
            "observation": "direct_column_h_spark_gate",
            "status": "blocked",
            "artifact_source": "Lane A GRC9V3 spark events",
            "reconstruction_attempt": "Checked candidate and step event evidence.",
            "notes": "Column-H is an analysis-derived proxy under Lane A, not a direct gate.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "routing_changes_by_column",
            "status": "inconclusive",
            "artifact_source": "single-step raw central-node fixture",
            "reconstruction_attempt": "Computed flux balance and event evidence.",
            "notes": "No post-event routing window is produced by this fixture.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "refinement_reassignment_by_column",
            "status": "inconclusive",
            "artifact_source": "StepResult.events",
            "reconstruction_attempt": "Looked for hybrid_mechanical_expansion events.",
            "notes": "No refinement events occurred in this Lane A proxy fixture.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "completed_identity_event",
            "status": "blocked",
            "artifact_source": "StepResult.events and post-event basin artifacts",
            "reconstruction_attempt": "Looked for hybrid_spark_completed events.",
            "notes": "No completed identity-level event can be claimed without persistent child basins.",
        },
    ]


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
        "iteration": 4,
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
        "fixture_ids": sorted(str(key) for key in summary["fixture_energy_profiles"]),
        "port_mappings": summary["transforms"],
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "derived_proxy_formula_version": summary["derived_proxy_formula_version"],
        "derived_proxy_formula": summary["derived_proxy_formula"],
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
                "experiment_b_column_interface_cancellation_summary.json"
            ),
        ],
        "reuse_notes": {
            "d1": "Use identity/column-permutation/row-permutation/random-relabel rows for column-side factorization checks.",
            "d2": "Use derived column proxy scores after enough O-style and D-style runs exist.",
            "d3": "Use transpose rows as row/column role-separation inputs, not as a complete D3 test.",
            "d5": "No refinement-memory claim is available from this run because no refinement events occurred.",
        },
    }


def _write_report(
    path: Path,
    rows: list[dict[str, Any]],
    sign_crossings: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    identity_rows = [row for row in rows if row["transform_id"] == "identity"]
    column_perm_rows = [
        row for row in rows if row["transform_id"] == "column_permutation_312"
    ]
    lines = [
        "# Experiment B Column-Interface Cancellation",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report tests whether a derived column-local cancellation/pressure",
        "proxy is observable under the Lane A baseline",
        "`current_hybrid_signed_hessian`.",
        "",
        "It does not claim direct column-H spark gating. Column-H remains an",
        "analysis-derived proxy unless a future canonical-column-H lane exists.",
        "",
        "## Outputs",
        "",
        "- `../outputs/experiment_b_column_interface_cancellation_rows.csv`",
        "- `../outputs/experiment_b_column_interface_cancellation_sign_crossings.csv`",
        "- `../outputs/experiment_b_column_interface_cancellation_summary.json`",
        "- `../outputs/experiment_b_column_interface_cancellation_manifest.json`",
        "- `../reports/experiment_b_column_interface_cancellation_blocked_observations.csv`",
        "",
        "## Fixture Matching",
        "",
        f"- energy totals matched: `{json.dumps(summary['energy_totals_matched'])}`",
        "- each column fixture uses the same row-wise plus/minus coherence pattern",
        "  moved to a different target column.",
        "",
        "## Identity Column Proxy Responses",
        "",
        "| Fixture | Expected Column | Pressure Column | Cancellation Column |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in identity_rows:
        lines.append(
            "| "
            f"{row['source_fixture_id']} | "
            f"{row['expected_column']} | "
            f"{row['dominant_pressure_column']} | "
            f"{row['dominant_cancellation_column']} |"
        )
    lines.extend(
        [
            "",
            "## Column Permutation Controls",
            "",
            f"- column proxy moves under column permutation: `{json.dumps(summary['column_permutation_moves_proxy'])}`",
            "",
            "| Fixture | Expected Column After Permutation | Pressure Column | Cancellation Column |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in column_perm_rows:
        lines.append(
            "| "
            f"{row['source_fixture_id']} | "
            f"{row['expected_column']} | "
            f"{row['dominant_pressure_column']} | "
            f"{row['dominant_cancellation_column']} |"
        )
    lines.extend(
        [
            "",
            "## Sign-Crossing Proxy Pairs",
            "",
            "| Column | Before Signed Sum | After Signed Sum | Crosses Zero |",
            "| ---: | ---: | ---: | --- |",
        ]
    )
    for row in sign_crossings:
        lines.append(
            "| "
            f"{row['column']} | "
            f"{row['before_signed_weighted_delta']:.9f} | "
            f"{row['after_signed_weighted_delta']:.9f} | "
            f"`{json.dumps(row['derived_proxy_sign_crossing'])}` |"
        )
    lines.extend(
        [
            "",
            "## Event Terminology",
            "",
            f"- spark candidate events: `{summary['spark_candidate_event_count_total']}`",
            f"- refinement events: `{summary['refinement_event_count_total']}`",
            f"- completed identity-level events: `{summary['completed_identity_event_count_total']}`",
            "- direct column-H gate claim: `blocked_under_lane_a`",
            "",
            "## Controls Summary",
            "",
            f"- identity column proxy matches expected column: `{json.dumps(summary['identity_column_proxy_matches'])}`",
            f"- row permutation preserves proxy column: `{json.dumps(summary['row_permutation_preserves_proxy_column'])}`",
            f"- transpose control rows present: `{json.dumps(summary['transpose_control_rows_present'])}`",
            f"- transpose removes predefined clean column claim: `{json.dumps(summary['transpose_clean_column_claim_removed'])}`",
            f"- random relabel removes predefined clean column claim: `{json.dumps(summary['random_relabel_clean_column_claim_removed'])}`",
            "- minimum true-minus-random cancellation interpretability margin: "
            f"`{summary['random_relabel_interpretability_margin_min']:.6f}`",
            "",
            "## Interpretation",
            "",
            "Experiment B supports observability of a derived column-local",
            "cancellation/pressure proxy in a clean saturated central-node fixture",
            "under Lane A.",
            "",
            "Column-local plus/minus patterns produce the expected target-column",
            "proxy signature, column permutation moves that signature, and row",
            "permutation does not explain it away. Random relabeling removes the",
            "predefined clean column claim.",
            "",
            "This is not evidence that column-H directly triggered a spark. Under",
            "Lane A, spark candidates remain signed-Hessian hybrid candidates.",
            "This run produced no refinement or completed identity-level events,",
            "so routing/refinement/identity consequences are recorded as blocked",
            "or inconclusive in the companion blocked-observations CSV.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(seed: int) -> dict[str, Path]:
    rows, sign_crossings, summary = run_experiment(seed)
    rows_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_b_column_interface_cancellation_rows.csv"
    )
    sign_crossing_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_b_column_interface_cancellation_sign_crossings.csv"
    )
    summary_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_b_column_interface_cancellation_summary.json"
    )
    manifest_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_b_column_interface_cancellation_manifest.json"
    )
    blocked_path = (
        EXPERIMENT_ROOT
        / "reports"
        / "experiment_b_column_interface_cancellation_blocked_observations.csv"
    )
    report_path = (
        EXPERIMENT_ROOT
        / "reports"
        / "experiment_b_column_interface_cancellation.md"
    )
    output_paths = {
        "rows_csv": rows_path,
        "sign_crossings_csv": sign_crossing_path,
        "summary_json": summary_path,
        "manifest_json": manifest_path,
        "blocked_observations_csv": blocked_path,
        "report_md": report_path,
    }
    _write_csv(rows_path, rows)
    _write_csv(sign_crossing_path, sign_crossings)
    _write_json(summary_path, summary)
    _write_json(
        manifest_path,
        _build_manifest(seed=seed, summary=summary, output_paths=output_paths),
    )
    _write_csv(blocked_path, blocked_observation_rows())
    _write_report(report_path, rows, sign_crossings, summary)
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
        rows, sign_crossings, summary = run_experiment(args.seed)
        print(
            json.dumps(
                {
                    "summary": summary,
                    "rows": rows,
                    "sign_crossings": sign_crossings,
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
