"""Experiment C: saturation and near-saturation under Lane A."""

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
    row_permutation_map,
    run_id_convention,
    runtime_assumptions,
    runtime_binding_requirements,
    state_mapping_convention,
    transpose_map,
)


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ID = "experiment_c_saturation"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_experiment_c_saturation.py"
)
CENTRAL_NODE_ID = 0
STRESSED_SIGNED_HESSIAN = (-0.1, 0.2, 0.3)
STABLE_SIGNED_HESSIAN = (0.2, 0.3, 0.4)
CENTRAL_COHERENCE = 9.0
LEAF_COHERENCE = 1.0
EPS_GRADIENT = 0.01
EPS_SPARK = 0.0
BUDGET_TOLERANCE = 1e-12


def _params(seed: int) -> dict[str, Any]:
    return {
        "dt": 0.1,
        "evolution": {
            "rng_seed": seed,
            "eps_gradient": EPS_GRADIENT,
            "eps_spark": EPS_SPARK,
            "eps_hessian": 0.01,
            "D_eff_target": 30,
            "w_bond": 1.0,
            "alpha": 1e-12,
            "beta": 1e-12,
            "gamma": 1e-12,
            "kappa_c": 1e-12,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
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
                "payload": {"kind": "experiment_c_boundary"},
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


def saturation_fixture_state(
    *,
    active_ports: tuple[int, ...],
    signed_hessian: tuple[float, float, float],
) -> dict[str, Any]:
    connections: list[tuple[int, int, int, int, int]] = []
    nodes: dict[str, dict[str, Any]] = {
        str(CENTRAL_NODE_ID): {
            "coherence": CENTRAL_COHERENCE,
            "gradient_row_basis": [0.0, 0.0, 0.0],
            "signed_hessian_row_basis": list(signed_hessian),
            "basin_mass": CENTRAL_COHERENCE,
            "basin_id": "root",
            "depth": 0,
        }
    }
    port_edges: dict[str, dict[str, int | float]] = {}
    for edge_id, port_id in enumerate(active_ports):
        neighbor_id = 400 + port_id
        connections.append((edge_id, CENTRAL_NODE_ID, port_id, neighbor_id, 1))
        nodes[str(neighbor_id)] = {
            "coherence": LEAF_COHERENCE,
            "gradient_row_basis": [1.0, 0.0, 0.0],
            "signed_hessian_row_basis": [1.0, 1.0, 1.0],
            "basin_mass": LEAF_COHERENCE,
            "basin_id": neighbor_id,
            "depth": 0,
        }
        port_edges[str(edge_id)] = _port_edge(
            node_u=CENTRAL_NODE_ID,
            port_u=port_id,
            node_v=neighbor_id,
            port_v=1,
            conductance=1.0,
            flux_uv=0.0,
        )
    return {
        "topology": _topology(connections),
        "nodes": nodes,
        "port_edges": port_edges,
        "sink_set": [CENTRAL_NODE_ID],
        "basins": {
            str(CENTRAL_NODE_ID): sorted(int(node_id) for node_id in nodes)
        },
    }


def _gradient_norm(values: list[float] | tuple[float, ...]) -> float:
    return sum(float(value) * float(value) for value in values) ** 0.5


def _column_diagnostic(state: Any) -> dict[str, Any]:
    signed_weighted_delta = {"1": 0.0, "2": 0.0, "3": 0.0}
    pressure = {"1": 0.0, "2": 0.0, "3": 0.0}
    center_coherence = state.nodes[CENTRAL_NODE_ID].coherence
    for edge_id in sorted(state.topology.incident_edge_ids(CENTRAL_NODE_ID)):
        port_edge = state.port_edges[edge_id]
        _, column = port_to_rc(port_edge.port_u)
        column_key = str(column)
        neighbor_id = port_edge.node_v if port_edge.node_u == CENTRAL_NODE_ID else port_edge.node_u
        delta = state.nodes[neighbor_id].coherence - center_coherence
        conductance = float(state.base_conductance.get(edge_id, port_edge.conductance))
        weighted_delta = conductance * delta
        signed_weighted_delta[column_key] += weighted_delta
        pressure[column_key] += abs(weighted_delta)
    residual = {column: abs(value) for column, value in signed_weighted_delta.items()}
    cancellation_score = {
        column: 1.0 - residual[column] / pressure[column]
        if pressure[column] > 0.0
        else 0.0
        for column in ("1", "2", "3")
    }
    return {
        "formula": (
            "derived_column_diagnostic_v1: per-column conductance-weighted "
            "coherence delta; diagnostic only, not a Lane A gate"
        ),
        "signed_weighted_delta": signed_weighted_delta,
        "pressure": pressure,
        "residual": residual,
        "cancellation_score": cancellation_score,
    }


def _condition_suite(seed: int) -> list[dict[str, Any]]:
    del seed
    return [
        {
            "condition_id": "C1_degree_7_stressed",
            "condition_class": "same_instability_without_saturation",
            "active_ports": tuple(range(1, 8)),
            "signed_hessian": STRESSED_SIGNED_HESSIAN,
            "expected_canonical_candidate": False,
            "notes": "Active degree 7 with the same central signed-Hessian stress as C3.",
        },
        {
            "condition_id": "C2_degree_8_stressed",
            "condition_class": "same_instability_without_saturation",
            "active_ports": tuple(range(1, 9)),
            "signed_hessian": STRESSED_SIGNED_HESSIAN,
            "expected_canonical_candidate": False,
            "notes": "Active degree 8 near-saturation fixture; canonical Lane A still requires degree 9.",
        },
        {
            "condition_id": "C3_degree_9_stressed",
            "condition_class": "canonical_saturation_with_instability",
            "active_ports": PORT_IDS,
            "signed_hessian": STRESSED_SIGNED_HESSIAN,
            "expected_canonical_candidate": True,
            "notes": "Canonical saturated stressed fixture.",
        },
        {
            "condition_id": "C5_degree_9_stable_hessian",
            "condition_class": "same_saturation_without_instability",
            "active_ports": PORT_IDS,
            "signed_hessian": STABLE_SIGNED_HESSIAN,
            "expected_canonical_candidate": False,
            "notes": "Saturated control with no signed-Hessian degeneracy.",
        },
    ]


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


def _active_ports_after_transform(
    active_ports: tuple[int, ...],
    port_map: dict[int, int],
) -> tuple[int, ...]:
    return tuple(sorted(port_map[port] for port in active_ports))


def evaluate_condition(
    *,
    condition: dict[str, Any],
    transform_id: str,
    port_map: dict[int, int],
    seed: int,
) -> dict[str, Any]:
    active_ports = _active_ports_after_transform(condition["active_ports"], port_map)
    inactive_ports = tuple(port for port in PORT_IDS if port not in active_ports)
    state_payload = saturation_fixture_state(
        active_ports=active_ports,
        signed_hessian=condition["signed_hessian"],
    )
    detect_model = GRC9V3.from_state(state=state_payload, params=_params(seed))
    state = detect_model.get_state()
    central_node = state.nodes[CENTRAL_NODE_ID]
    active_degree = len(tuple(state.topology.incident_edge_ids(CENTRAL_NODE_ID)))
    gradient_norm = _gradient_norm(central_node.gradient_row_basis)
    min_signed_hessian = min(float(value) for value in central_node.signed_hessian_row_basis)
    saturation_gate = active_degree == 9
    basin_interior_gate = gradient_norm < EPS_GRADIENT
    degeneracy_gate = min_signed_hessian < EPS_SPARK
    candidate_predicate = saturation_gate and basin_interior_gate and degeneracy_gate
    candidates = detect_model.detect_hybrid_spark_candidates()
    diagnostic = _column_diagnostic(state)

    apply_model = GRC9V3.from_state(state=state_payload, params=_params(seed))
    emitted_events = apply_model.apply_hybrid_sparks()
    apply_state = apply_model.get_state()
    event_kinds = [event.kind for event in emitted_events]
    expansion_events = [
        event for event in emitted_events if event.kind == "hybrid_mechanical_expansion"
    ]
    expansion_payload = expansion_events[0].payload if expansion_events else {}
    candidate_payload = candidates[0].payload if candidates else {}
    emitted_event_sequence = [
        f"{index}:{event.kind}@step_{event.step_index}"
        for index, event in enumerate(emitted_events)
    ]
    child_basin_evidence = apply_state.cached_quantities.get(
        "last_child_basin_stabilization",
        {},
    )
    reassignment_map = expansion_payload.get("reassignment_map", {})
    budget_evidence_available = all(
        key in expansion_payload
        for key in ("budget_before", "budget_after", "budget_error")
    )

    return {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "condition_id": condition["condition_id"],
        "condition_class": condition["condition_class"],
        "transform_id": transform_id,
        "active_degree": active_degree,
        "active_ports": " ".join(str(port) for port in active_ports),
        "inactive_ports": " ".join(str(port) for port in inactive_ports),
        "inactive_port_count": len(inactive_ports),
        "is_sink_before": CENTRAL_NODE_ID in state.sink_set,
        "basin_id_before": central_node.basin_id,
        "central_coherence": central_node.coherence,
        "gradient_norm": gradient_norm,
        "eps_gradient": EPS_GRADIENT,
        "basin_interior_gate": basin_interior_gate,
        "min_signed_hessian": min_signed_hessian,
        "eps_spark": EPS_SPARK,
        "signed_hessian_degeneracy_gate": degeneracy_gate,
        "saturation_gate": saturation_gate,
        "canonical_candidate_predicate": candidate_predicate,
        "expected_canonical_candidate": condition["expected_canonical_candidate"],
        "candidate_event_count": len(candidates),
        "candidate_matches_expected": (
            len(candidates) == (1 if condition["expected_canonical_candidate"] else 0)
        ),
        "candidate_event_step_indices": " ".join(
            str(event.step_index) for event in candidates
        ),
        "candidate_event_payload_json": json.dumps(candidate_payload, sort_keys=True),
        "event_kinds": ";".join(event_kinds),
        "event_sequence": ";".join(emitted_event_sequence),
        "event_step_indices": " ".join(str(event.step_index) for event in emitted_events),
        "refinement_event_count": event_kinds.count("hybrid_mechanical_expansion"),
        "completed_identity_event_count": event_kinds.count("hybrid_spark_completed"),
        "parent_node_present_after_apply": apply_state.topology.has_node(CENTRAL_NODE_ID),
        "budget_before": expansion_payload.get("budget_before", ""),
        "budget_after": expansion_payload.get("budget_after", ""),
        "budget_error": expansion_payload.get("budget_error", ""),
        "budget_tolerance": BUDGET_TOLERANCE,
        "budget_evidence_available": budget_evidence_available,
        "budget_evidence_source": (
            "hybrid_mechanical_expansion.payload"
            if budget_evidence_available
            else ""
        ),
        "budget_preservation_path": expansion_payload.get("budget_preservation_path", ""),
        "reassignment_map_available": bool(reassignment_map),
        "reassignment_edge_count": len(reassignment_map),
        "module_node_count": len(expansion_payload.get("module_node_ids", [])),
        "mechanical_expansion_event_payload_json": json.dumps(
            expansion_payload,
            sort_keys=True,
        ),
        "child_basin_stabilization_pass": child_basin_evidence.get(
            "stabilization_pass",
            "",
        ),
        "stable_child_basin_count": child_basin_evidence.get(
            "stable_child_basin_count",
            "",
        ),
        "near_saturation_policy": "not_implemented_in_lane_a",
        "derived_column_diagnostic_role": "analysis_diagnostic_only",
        "column_1_pressure": diagnostic["pressure"]["1"],
        "column_2_pressure": diagnostic["pressure"]["2"],
        "column_3_pressure": diagnostic["pressure"]["3"],
        "column_1_cancellation_score": diagnostic["cancellation_score"]["1"],
        "column_2_cancellation_score": diagnostic["cancellation_score"]["2"],
        "column_3_cancellation_score": diagnostic["cancellation_score"]["3"],
        "diagnostic_formula": diagnostic["formula"],
        "condition_notes": condition["notes"],
        "artifact_sources": (
            "GRC9V3State topology/nodes/sink_set, detect_hybrid_spark_candidates, "
            "apply_hybrid_sparks, hybrid_mechanical_expansion payload"
        ),
    }


def run_experiment(seed: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    transforms = _transforms(seed)
    rows: list[dict[str, Any]] = []
    for condition in _condition_suite(seed):
        for transform_id, port_map in transforms.items():
            rows.append(
                evaluate_condition(
                    condition=condition,
                    transform_id=transform_id,
                    port_map=port_map,
                    seed=seed,
                )
            )
    identity_rows = [row for row in rows if row["transform_id"] == "identity"]
    stressed_identity = [
        row
        for row in identity_rows
        if row["condition_id"] in {
            "C1_degree_7_stressed",
            "C2_degree_8_stressed",
            "C3_degree_9_stressed",
        }
    ]
    saturated_stable = next(
        row for row in identity_rows if row["condition_id"] == "C5_degree_9_stable_hessian"
    )
    canonical_positive = next(
        row for row in identity_rows if row["condition_id"] == "C3_degree_9_stressed"
    )
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
        "canonical_gate_formula": (
            "active_degree == 9 AND gradient_norm < eps_gradient AND "
            "min_signed_hessian < eps_spark"
        ),
        "near_saturation_policy": "not_implemented_in_lane_a",
        "central_instability_matched_for_stressed_degree_7_8_9": len(
            {
                (
                    round(float(row["gradient_norm"]), 12),
                    round(float(row["min_signed_hessian"]), 12),
                )
                for row in stressed_identity
            }
        )
        == 1,
        "active_degree_7_or_8_stressed_nontrigger": all(
            int(row["candidate_event_count"]) == 0
            and int(row["refinement_event_count"]) == 0
            for row in stressed_identity
            if int(row["active_degree"]) in {7, 8}
        ),
        "degree_9_stressed_candidate": int(canonical_positive["candidate_event_count"]) == 1,
        "degree_9_stressed_refines": int(canonical_positive["refinement_event_count"]) == 1,
        "degree_9_without_instability_nontrigger": (
            int(saturated_stable["candidate_event_count"]) == 0
            and int(saturated_stable["refinement_event_count"]) == 0
        ),
        "candidate_detection_matches_formula_all_rows": all(
            bool(row["canonical_candidate_predicate"])
            == (int(row["candidate_event_count"]) == 1)
            for row in rows
        ),
        "candidate_expectations_match_all_rows": all(
            bool(row["candidate_matches_expected"]) for row in rows
        ),
        "transform_candidate_invariance": {
            condition["condition_id"]: len(
                {
                    (
                        int(row["candidate_event_count"]),
                        int(row["refinement_event_count"]),
                    )
                    for row in rows
                    if row["condition_id"] == condition["condition_id"]
                }
            )
            == 1
            for condition in _condition_suite(seed)
        },
        "budget_evidence_available_for_canonical_positive": (
            canonical_positive["budget_before"] != ""
            and canonical_positive["budget_after"] != ""
            and canonical_positive["budget_error"] != ""
        ),
        "budget_tolerance": BUDGET_TOLERANCE,
        "canonical_positive_budget_error": canonical_positive["budget_error"],
        "canonical_positive_budget_within_tolerance": (
            canonical_positive["budget_error"] != ""
            and abs(float(canonical_positive["budget_error"])) <= BUDGET_TOLERANCE
        ),
        "canonical_positive_candidate_payload_available": (
            canonical_positive["candidate_event_payload_json"] != "{}"
        ),
        "canonical_positive_expansion_payload_available": (
            canonical_positive["mechanical_expansion_event_payload_json"] != "{}"
        ),
        "canonical_positive_reassignment_map_available": bool(
            canonical_positive["reassignment_map_available"]
        ),
        "canonical_positive_budget_evidence_source": canonical_positive[
            "budget_evidence_source"
        ],
        "canonical_positive_completed_identity_event_count": canonical_positive[
            "completed_identity_event_count"
        ],
        "identity_level_persistence_claim": "not_made_in_iteration_6",
        "derived_column_diagnostic_role": "reported_separately_not_gate_evidence",
        "transform_invariance_interpretation": (
            "expected_for_lane_a_capacity_signed_hessian_gate; not_row_column_semantic_evidence"
        ),
    }
    return rows, summary


def blocked_observation_rows() -> list[dict[str, str]]:
    return [
        {
            "experiment": EXPERIMENT_ID,
            "observation": "near_saturation_policy_degree_8",
            "status": "blocked",
            "artifact_source": "Lane A GRC9V3 candidate predicate",
            "reconstruction_attempt": "Checked candidate predicate and runtime modes.",
            "notes": "Lane A canonical gate is active_degree == 9; no degree-8 near-saturation policy is implemented.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "direct_column_h_saturation_gate",
            "status": "blocked",
            "artifact_source": "Lane A GRC9V3 spark events",
            "reconstruction_attempt": "Separated derived column diagnostic from candidate event payload.",
            "notes": "Column-H remains an analysis diagnostic under Lane A, not a direct saturation/refinement gate.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "persistent_child_identity_after_saturation",
            "status": "inconclusive",
            "artifact_source": "single application of apply_hybrid_sparks",
            "reconstruction_attempt": "Captured completed event and child basin stabilization payload when expansion occurred.",
            "notes": "Iteration 6 records event-level evidence only; persistent post-event identity windows are deferred to Experiment D.",
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
        "iteration": 6,
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
        "condition_ids": [condition["condition_id"] for condition in _condition_suite(seed)],
        "port_mappings": summary["transforms"],
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "canonical_gate_formula": summary["canonical_gate_formula"],
        "budget_tolerance": summary["budget_tolerance"],
        "near_saturation_policy": summary["near_saturation_policy"],
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
                "experiment_c_saturation_summary.json"
            ),
        ],
        "reuse_notes": {
            "d1": "Use degree and transform rows as active-degree gate controls.",
            "d2": "Use canonical predicate fields as supervised gate features.",
            "d5": "Use event/budget fields only as event-level evidence; persistent identity remains deferred.",
        },
    }


def _write_report(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    identity_rows = [row for row in rows if row["transform_id"] == "identity"]
    transform_flags = summary["transform_candidate_invariance"]
    lines = [
        "# Experiment C Saturation And Near-Saturation",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report tests whether canonical Lane A saturation behaves as a",
        "meaningful refinement gate under `current_hybrid_signed_hessian`.",
        "",
        "The Lane A candidate predicate is active-degree saturation plus basin",
        "interior evidence plus signed-Hessian degeneracy. Direct column-H and",
        "near-saturation policies are not claimed.",
        "",
        "## Outputs",
        "",
        "- `../outputs/experiment_c_saturation_rows.csv`",
        "- `../outputs/experiment_c_saturation_summary.json`",
        "- `../outputs/experiment_c_saturation_manifest.json`",
        "- `../reports/experiment_c_saturation_blocked_observations.csv`",
        "",
        "## Canonical Gate",
        "",
        f"- formula: `{summary['canonical_gate_formula']}`",
        f"- near-saturation policy: `{summary['near_saturation_policy']}`",
        "- derived column diagnostic role: `reported separately; not gate evidence`",
        f"- budget tolerance: `{summary['budget_tolerance']}`",
        "",
        "## Identity Transform Rows",
        "",
        "| Condition | Degree | Saturation | Basin Interior | Degeneracy | Candidates | Refinements | Budget Error |",
        "| --- | ---: | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in identity_rows:
        budget_error = row["budget_error"] if row["budget_error"] != "" else ""
        lines.append(
            "| "
            f"{row['condition_id']} | "
            f"{row['active_degree']} | "
            f"`{json.dumps(row['saturation_gate'])}` | "
            f"`{json.dumps(row['basin_interior_gate'])}` | "
            f"`{json.dumps(row['signed_hessian_degeneracy_gate'])}` | "
            f"{row['candidate_event_count']} | "
            f"{row['refinement_event_count']} | "
            f"{budget_error} |"
        )
    lines.extend(
        [
            "",
            "## Controls Summary",
            "",
            "- central instability matched for stressed degree 7/8/9: "
            f"`{json.dumps(summary['central_instability_matched_for_stressed_degree_7_8_9'])}`",
            "- degree 7 or 8 stressed non-trigger: "
            f"`{json.dumps(summary['active_degree_7_or_8_stressed_nontrigger'])}`",
            "- degree 9 stressed candidate: "
            f"`{json.dumps(summary['degree_9_stressed_candidate'])}`",
            "- degree 9 stressed refines: "
            f"`{json.dumps(summary['degree_9_stressed_refines'])}`",
            "- degree 9 without instability non-trigger: "
            f"`{json.dumps(summary['degree_9_without_instability_nontrigger'])}`",
            "- candidate detection matches formula for all rows: "
            f"`{json.dumps(summary['candidate_detection_matches_formula_all_rows'])}`",
            "- budget evidence available for canonical positive: "
            f"`{json.dumps(summary['budget_evidence_available_for_canonical_positive'])}`",
            "- canonical positive budget within tolerance: "
            f"`{json.dumps(summary['canonical_positive_budget_within_tolerance'])}`",
            "- canonical positive candidate payload available: "
            f"`{json.dumps(summary['canonical_positive_candidate_payload_available'])}`",
            "- canonical positive expansion payload available: "
            f"`{json.dumps(summary['canonical_positive_expansion_payload_available'])}`",
            "- canonical positive reassignment map available: "
            f"`{json.dumps(summary['canonical_positive_reassignment_map_available'])}`",
            "- canonical positive budget evidence source: "
            f"`{summary['canonical_positive_budget_evidence_source']}`",
            "",
            "## Transform Invariance",
            "",
            "| Condition | Candidate/refinement counts invariant across transforms |",
            "| --- | --- |",
        ]
    )
    for condition_id, invariant in transform_flags.items():
        lines.append(f"| {condition_id} | `{json.dumps(invariant)}` |")
    lines.extend(
        [
            "",
            "This invariance is expected for the Lane A gate because the predicate",
            "depends on active degree, basin-interior evidence, and signed-Hessian",
            "degeneracy. It supports capacity plus signed-Hessian bottleneck",
            "behavior, not direct row/column semantic separation.",
            "",
            "## Interpretation",
            "",
            "Experiment C supports the Lane A representational-bottleneck claim.",
            "Under the current `current_hybrid_signed_hessian` gate, active-degree",
            "7 and active-degree 8 stressed fixtures do not produce spark candidates",
            "or refinement events, even when matched to the central signed-Hessian",
            "stress of the positive degree-9 fixture.",
            "",
            "The active-degree 9 stressed fixture produces one spark candidate and",
            "one mechanical expansion with budget evidence. The active-degree 9",
            "stable-Hessian control does not trigger merely because all ports are",
            "occupied. Therefore, under Lane A, fullness alone is insufficient,",
            "signed-Hessian stress alone is insufficient when unsaturated, and the",
            "positive event requires the combination of full nine-port occupancy",
            "and signed-Hessian degeneracy.",
            "",
            "Near-saturation remains blocked under Lane A because no active-degree-8",
            "policy is implemented. Direct column-H gate evidence remains blocked",
            "under Lane A. The observed expansion is event-level mechanical evidence",
            "only; persistent child identity claims are deferred to Experiment D.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(seed: int) -> dict[str, Path]:
    rows, summary = run_experiment(seed)
    rows_path = EXPERIMENT_ROOT / "outputs" / "experiment_c_saturation_rows.csv"
    summary_path = EXPERIMENT_ROOT / "outputs" / "experiment_c_saturation_summary.json"
    manifest_path = EXPERIMENT_ROOT / "outputs" / "experiment_c_saturation_manifest.json"
    blocked_path = (
        EXPERIMENT_ROOT
        / "reports"
        / "experiment_c_saturation_blocked_observations.csv"
    )
    report_path = EXPERIMENT_ROOT / "reports" / "experiment_c_saturation.md"
    output_paths = {
        "rows_csv": rows_path,
        "summary_json": summary_path,
        "manifest_json": manifest_path,
        "blocked_observations_csv": blocked_path,
        "report_md": report_path,
    }
    _write_csv(rows_path, rows)
    _write_json(summary_path, summary)
    _write_json(
        manifest_path,
        _build_manifest(seed=seed, summary=summary, output_paths=output_paths),
    )
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
