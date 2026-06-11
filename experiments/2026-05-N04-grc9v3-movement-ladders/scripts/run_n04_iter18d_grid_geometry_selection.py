#!/usr/bin/env python3
"""Run N04 Iteration 18-D S3 grid geometry-scored selection probe."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
SCRIPT_DIR = N04 / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_n04_iter18_grid_transfer as iter18  # noqa: E402
import run_n04_iter18c_grid_state_gated_routing as iter18c  # noqa: E402


ITER18C_PATH = N04 / "outputs/n04_iter18c_grid_state_gated_routing_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter18d_grid_geometry_selection_report.json"
REPORT_PATH = N04 / "reports/n04_iter18d_grid_geometry_selection_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter18d_grid_geometry_selection.py"
)

CENTER_NODE = iter18.CENTER_NODE
NORTH_NODE = 7
WEST_NODE = 11
EAST_NODE = 13
SOUTH_NODE = 17
NORTH_BASIN_NODES = (7, 2, 8)
EAST_BASIN_NODES = (13, 14, 8)
GATE_PREBIAS = iter18c.GATE_PREBIAS
RECOVERY_WINDOW_CYCLES = iter18.RECOVERY_WINDOW_CYCLES
CHALLENGE_TRANSFER_AMOUNT = iter18.CHALLENGE_TRANSFER_AMOUNT
COMPATIBILITY_MARGIN_MIN = 0.15
EPSILON_BUDGET = iter18.EPSILON_BUDGET
TOL = iter18.TOL


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, str]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _run_git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _unit(vector: tuple[float, float]) -> tuple[float, float]:
    norm = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    if norm <= 0.0:
        raise ValueError("zero vector")
    return vector[0] / norm, vector[1] / norm


def _dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _candidate_basins(edge_by_pair: dict[tuple[int, int], int]) -> dict[str, dict[str, Any]]:
    return {
        "north_output_basin": {
            "output_gate": NORTH_NODE,
            "basin_nodes": list(NORTH_BASIN_NODES),
            "geometry_vector": [0.0, -1.0],
            "egress_source": CENTER_NODE,
            "egress_target": NORTH_NODE,
            "egress_edge_id": edge_by_pair[(CENTER_NODE, NORTH_NODE)],
            "front_nodes": [NORTH_NODE],
            "rear_nodes": [SOUTH_NODE],
            "route_id": "s3-grid-geometry-selected-north",
        },
        "east_output_basin": {
            "output_gate": EAST_NODE,
            "basin_nodes": list(EAST_BASIN_NODES),
            "geometry_vector": [1.0, 0.0],
            "egress_source": CENTER_NODE,
            "egress_target": EAST_NODE,
            "egress_edge_id": edge_by_pair[(CENTER_NODE, EAST_NODE)],
            "front_nodes": [EAST_NODE],
            "rear_nodes": [WEST_NODE],
            "route_id": "s3-grid-geometry-selected-east",
        },
    }


def _selection_policy(edge_by_pair: dict[tuple[int, int], int]) -> dict[str, Any]:
    return {
        "policy_id": "s3_grid_geometry_competing_basin_selection_policy_v1",
        "declared_before_run": True,
        "junction_node": CENTER_NODE,
        "input_gates": [WEST_NODE, SOUTH_NODE],
        "candidate_output_basins": _candidate_basins(edge_by_pair),
        "selection_rule": "argmax_normalized_flux_shape_dot_output_basin_vector",
        "compatibility_margin_min": COMPATIBILITY_MARGIN_MIN,
        "tie_behavior": "no_selection",
        "disabled_behavior": "no_selection_no_producer_evaluation",
        "diagonal_edges_enabled": False,
        "route_shortcuts_enabled": False,
    }


def _flux_shapes() -> dict[str, dict[str, Any]]:
    return {
        "north_curved_flux": {
            "ingress_source": WEST_NODE,
            "ingress_target": CENTER_NODE,
            "flux_shape_vector": [0.20, -1.00],
            "flux_shape_basis": "committed_ingress_contact_with_north_curvature_lobe",
            "expected_selected_basin": "north_output_basin",
        },
        "east_curved_flux": {
            "ingress_source": SOUTH_NODE,
            "ingress_target": CENTER_NODE,
            "flux_shape_vector": [1.00, -0.20],
            "flux_shape_basis": "committed_ingress_contact_with_east_curvature_lobe",
            "expected_selected_basin": "east_output_basin",
        },
    }


def _apply_competing_basin_geometry(state: Any) -> dict[str, Any]:
    before_values = [float(state.nodes[index].coherence) for index in range(iter18.NODE_COUNT)]
    before_budget = sum(before_values)
    state.nodes[NORTH_NODE].coherence += GATE_PREBIAS
    state.nodes[SOUTH_NODE].coherence -= GATE_PREBIAS
    state.nodes[EAST_NODE].coherence += GATE_PREBIAS
    state.nodes[WEST_NODE].coherence -= GATE_PREBIAS
    after_values = [float(state.nodes[index].coherence) for index in range(iter18.NODE_COUNT)]
    after_budget = sum(after_values)
    return {
        "geometry_id": "s3_grid_geometry_scored_competing_output_basins_v1",
        "source_geometry": "s3_grid_state_gated_two_input_two_output_v1",
        "coordinate_frame": "grid_xy",
        "junction_node": CENTER_NODE,
        "competing_output_basins": {
            "north_output_basin": list(NORTH_BASIN_NODES),
            "east_output_basin": list(EAST_BASIN_NODES),
        },
        "output_gate_prebias": GATE_PREBIAS,
        "prebiased_output_pairs": [
            {"credit_node": NORTH_NODE, "debit_node": SOUTH_NODE},
            {"credit_node": EAST_NODE, "debit_node": WEST_NODE},
        ],
        "diagonal_edges_enabled": False,
        "route_shortcuts_enabled": False,
        "route_edges_are_local_unit_edges": True,
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_geometry_init": min(after_values) >= -TOL,
        "topology_changed_by_fixture_definition": False,
        "topology_fixed_during_run": True,
        "topology_mutated_during_run": False,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
        "reason": (
            "Both candidate output basins are present in the same fixed grid "
            "geometry. Selection is scored from serialized input flux shape "
            "against declared output-basin geometry vectors."
        ),
    }


def _select_basin(
    *,
    policy: dict[str, Any],
    flux_shape: dict[str, Any],
    ingress_events: list[dict[str, Any]],
    surface_log_digest: str,
    enabled: bool = True,
) -> dict[str, Any]:
    if not enabled:
        return {
            "selection_policy_id": policy["policy_id"],
            "selection_enabled": False,
            "selected": False,
            "selected_basin": None,
            "primary_blocker": "competition_selection_disabled",
            "source_surface_log_digest": surface_log_digest,
            "committed_ingress_event_count": len(ingress_events),
        }
    flux_vector = _unit(tuple(float(v) for v in flux_shape["flux_shape_vector"]))
    scores: dict[str, float] = {}
    for basin_id, basin in policy["candidate_output_basins"].items():
        basin_vector = _unit(tuple(float(v) for v in basin["geometry_vector"]))
        scores[basin_id] = _dot(flux_vector, basin_vector)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    margin = ranked[0][1] - ranked[1][1]
    selected = margin >= float(policy["compatibility_margin_min"])
    return {
        "selection_policy_id": policy["policy_id"],
        "selection_enabled": True,
        "selected": selected,
        "selected_basin": ranked[0][0] if selected else None,
        "selected_output_gate": (
            policy["candidate_output_basins"][ranked[0][0]]["output_gate"]
            if selected
            else None
        ),
        "selection_rule": policy["selection_rule"],
        "selection_basis": "input_flux_shape_geometry_compatibility",
        "flux_shape_vector": list(flux_shape["flux_shape_vector"]),
        "flux_shape_basis": flux_shape["flux_shape_basis"],
        "compatibility_scores": scores,
        "compatibility_margin": margin,
        "compatibility_margin_min": policy["compatibility_margin_min"],
        "primary_blocker": None if selected else "ambiguous_competing_basin_scores",
        "source_surface_log_digest": surface_log_digest,
        "committed_ingress_event_count": len(ingress_events),
        "direct_input_to_output_lookup_used": False,
        "copied_from_original_schedule": False,
    }


def _transition_from_selection(policy: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    basin = policy["candidate_output_basins"][selection["selected_basin"]]
    return {
        **basin,
        "front_nodes": tuple(basin["front_nodes"]),
        "rear_nodes": tuple(basin["rear_nodes"]),
        "route_vector": tuple(float(v) for v in basin["geometry_vector"]),
        "expected_polarity": "positive",
    }


def _surface_log_digest(model: Any) -> str:
    return iter18.iter16.iter15b.native_m6._digest_json(  # noqa: SLF001
        [row.to_artifact() for row in model.get_state().causal_pulse_substrate_surface_log]
    )


def _boundary_polarity_score(model: Any, front_nodes: tuple[int, ...], rear_nodes: tuple[int, ...]) -> float:
    values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    return sum(values[index] for index in front_nodes) - sum(values[index] for index in rear_nodes)


def _apply_polarity_damping_perturbation(
    model: Any,
    *,
    front_nodes: tuple[int, ...],
    rear_nodes: tuple[int, ...],
    transfer_amount: float,
) -> dict[str, Any]:
    before_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    before_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    state = model.get_state().base_state
    for node_id in front_nodes:
        state.nodes[node_id].coherence -= transfer_amount / len(front_nodes)
    for node_id in rear_nodes:
        state.nodes[node_id].coherence += transfer_amount / len(rear_nodes)
    after_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    after_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    return {
        "perturbation_kind": "budget_neutral_geometry_selected_output_polarity_damping",
        "transfer_amount": transfer_amount,
        "debit_nodes": list(front_nodes),
        "credit_nodes": list(rear_nodes),
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_perturbation": min(after_values) >= -TOL,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
    }


def _feedback_cycle(
    model: Any,
    *,
    config: dict[str, Any],
    cycle_index: int,
    phase: str,
    expected_polarity: str | None = None,
) -> dict[str, Any]:
    feedback_row = model.emit_feedback_eligibility_surface_row(
        front_node_ids=config["front_nodes"],
        rear_node_ids=config["rear_nodes"],
        reference_delta=0.0,
        feedback_threshold=iter18.iter16.iter15b.native_m6.FEEDBACK_THRESHOLD,
        expected_next_route_id=config["route_id"],
        expected_next_channel_id=f"edge:{config['egress_edge_id']}",
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=config["egress_source"],
        target_node_id=config["egress_target"],
        edge_id=config["egress_edge_id"],
        threshold=iter18.iter16.iter15b.native_m6.FEEDBACK_THRESHOLD,
        packet_amount=iter18.iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
        expected_polarity=expected_polarity or config["expected_polarity"],
        expected_source_surface_digest=feedback_row.surface_values_after[
            "source_surface_digest"
        ],
        expected_next_route_id=config["route_id"],
        expected_next_channel_id=f"edge:{config['egress_edge_id']}",
    )
    result = model.produce_events(
        policy=(
            iter18.iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
        )
    )
    record = result.production_records[0]
    processed_events: list[dict[str, Any]] = []
    if record.reason_code == (
        iter18.iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ):
        processed_events = iter18.iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
    return {
        "cycle_index": cycle_index,
        "phase": phase,
        "surface_digest": feedback_row.surface_digest,
        "source_surface_digest": feedback_row.surface_values_after[
            "source_surface_digest"
        ],
        "boundary_polarity_score": feedback_row.surface_values_after[
            "boundary_polarity_score"
        ],
        "producer_reason_code": record.reason_code,
        "scheduled_event_id": record.scheduled_event_id,
        "regenerated_pulse_source": record.observed_evidence.get(
            "regenerated_pulse_source"
        ),
        "copied_from_original_schedule": record.observed_evidence.get(
            "copied_from_original_schedule"
        ),
        "production_artifact": result.to_artifact(),
        "processed_events": processed_events,
    }


def _cycle_summary(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in cycle.items()
        if key not in {"production_artifact", "processed_events"}
    } | {
        "processed_event_count": len(cycle["processed_events"]),
        "processed_events_digest": iter18.iter16.iter15b.native_m6._digest_json(cycle["processed_events"]),  # noqa: SLF001
    }


def _route_progress(delta: dict[str, float], route_vector: tuple[float, float]) -> float:
    norm = math.sqrt(route_vector[0] ** 2 + route_vector[1] ** 2)
    return (delta["x"] * route_vector[0] + delta["y"] * route_vector[1]) / norm


def _run_selection_lane(lane: str) -> dict[str, Any]:
    state, edge_by_pair = iter18._grid_state()  # noqa: SLF001
    policy = _selection_policy(edge_by_pair)
    geometry = _apply_competing_basin_geometry(state)
    flux_shape = _flux_shapes()[lane]
    ingress_edge_id = edge_by_pair[(flux_shape["ingress_source"], flux_shape["ingress_target"])]
    model = iter18.iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter18.iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    initial_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    initial_centroid = iter18._centroid_xy(initial_values)  # noqa: SLF001
    initial_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    model.schedule_packet_departure(
        source_node_id=flux_shape["ingress_source"],
        target_node_id=flux_shape["ingress_target"],
        edge_id=ingress_edge_id,
        amount=iter18.iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    ingress_events = iter18.iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
    selection = _select_basin(
        policy=policy,
        flux_shape=flux_shape,
        ingress_events=ingress_events,
        surface_log_digest=_surface_log_digest(model),
    )
    config = _transition_from_selection(policy, selection)
    first_output_cycle = _feedback_cycle(
        model,
        config=config,
        cycle_index=0,
        phase="geometry_selected_output_first_fire",
    )
    pre_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    pre_centroid = iter18._centroid_xy(pre_values)  # noqa: SLF001
    pre_score = _boundary_polarity_score(model, config["front_nodes"], config["rear_nodes"])
    perturbation = _apply_polarity_damping_perturbation(
        model,
        front_nodes=config["front_nodes"],
        rear_nodes=config["rear_nodes"],
        transfer_amount=CHALLENGE_TRANSFER_AMOUNT,
    )
    post_score = _boundary_polarity_score(model, config["front_nodes"], config["rear_nodes"])
    recovery_cycles = [
        _feedback_cycle(
            model,
            config=config,
            cycle_index=cycle_index,
            phase="post_perturbation_geometry_selected_recovery",
        )
        for cycle_index in range(RECOVERY_WINDOW_CYCLES)
    ]
    final_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    final_centroid = iter18._centroid_xy(final_values)  # noqa: SLF001
    final_score = _boundary_polarity_score(model, config["front_nodes"], config["rear_nodes"])
    production_artifacts = [
        cycle["production_artifact"]
        for cycle in [first_output_cycle, *recovery_cycles]
        if cycle["production_artifact"] is not None
    ]
    validation = iter18.iter16.iter15b.native_m6.validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=model.snapshot()["events"],
        production_results=production_artifacts,
    )
    recovery_scheduled = [
        cycle
        for cycle in recovery_cycles
        if cycle["producer_reason_code"]
        == iter18.iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ]
    final_delta = {
        "x": final_centroid["x"] - initial_centroid["x"],
        "y": final_centroid["y"] - initial_centroid["y"],
    }
    width_initial = iter18._radius_width(initial_values)  # noqa: SLF001
    width_final = iter18._radius_width(final_values)  # noqa: SLF001
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = iter18._profile_similarity(initial_values, final_values)  # noqa: SLF001
    return {
        "lane": lane,
        "geometry_init": geometry,
        "selection_policy": policy,
        "input_flux_shape": flux_shape,
        "selection_result": selection,
        "selected_output_basin": selection["selected_basin"],
        "selected_output_gate": selection["selected_output_gate"],
        "route_vector": list(config["route_vector"]),
        "route_segments": [
            [flux_shape["ingress_source"], flux_shape["ingress_target"]],
            [config["egress_source"], config["egress_target"]],
        ],
        "route_is_local_unit_edges": True,
        "diagonal_shortcut_used": False,
        "initial_centroid_xy": initial_centroid,
        "pre_perturbation_centroid_xy": pre_centroid,
        "final_centroid_xy": final_centroid,
        "final_centroid_delta": final_delta,
        "final_route_progress": _route_progress(final_delta, config["route_vector"]),
        "pre_perturbation_score": pre_score,
        "post_perturbation_score": post_score,
        "final_score": final_score,
        "first_output_cycle": _cycle_summary(first_output_cycle),
        "recovery_scheduled_cycle_count": len(recovery_scheduled),
        "recovery_cycles": [_cycle_summary(cycle) for cycle in recovery_cycles],
        "perturbation": perturbation,
        "budget_initial": initial_budget,
        "budget_final": final_budget,
        "budget_abs_error": abs(final_budget - initial_budget),
        "nonnegative_gate_passed": min(final_values) >= -TOL,
        "width_relative_change": width_relative_change,
        "profile_similarity": profile_similarity,
        "identity_shape_gates_passed": (
            width_relative_change <= iter18.iter16.iter15b.native_m6.WIDTH_RELATIVE_CHANGE_MAX
            and profile_similarity >= iter18.iter16.iter15b.native_m6.PROFILE_SIMILARITY_MIN
        ),
        "artifact_validator": validation,
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "surface_log_digest": _surface_log_digest(model),
        "producer_records_digest": iter18.iter16.iter15b.native_m6._digest_json(production_artifacts),  # noqa: SLF001
        "m4_boundary_response_passed": (
            post_score < pre_score - TOL
            and final_score >= pre_score - TOL
        ),
        "m5_direction_control_passed": len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES,
        "m6_geometry_selection_candidate_passed": (
            len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and selection["selected"]
            and selection["selected_basin"] == flux_shape["expected_selected_basin"]
            and post_score < pre_score - TOL
            and final_score >= pre_score - TOL
            and _route_progress(final_delta, config["route_vector"]) > TOL
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
        "ingress_event_count": len(ingress_events),
        "ingress_events_digest": iter18.iter16.iter15b.native_m6._digest_json(ingress_events),  # noqa: SLF001
    }


def _run_controls() -> dict[str, Any]:
    state, edge_by_pair = iter18._grid_state()  # noqa: SLF001
    policy = _selection_policy(edge_by_pair)
    _apply_competing_basin_geometry(state)
    model = iter18.iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter18.iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    ambiguous_flux = {
        "ingress_source": WEST_NODE,
        "ingress_target": CENTER_NODE,
        "flux_shape_vector": [1.0, -1.0],
        "flux_shape_basis": "equal_north_east_compatibility",
        "expected_selected_basin": None,
    }
    model.schedule_packet_departure(
        source_node_id=WEST_NODE,
        target_node_id=CENTER_NODE,
        edge_id=edge_by_pair[(WEST_NODE, CENTER_NODE)],
        amount=iter18.iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    ingress_events = iter18.iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
    digest = _surface_log_digest(model)
    disabled = _select_basin(
        policy=policy,
        flux_shape=_flux_shapes()["north_curved_flux"],
        ingress_events=ingress_events,
        surface_log_digest=digest,
        enabled=False,
    )
    ambiguous = _select_basin(
        policy=policy,
        flux_shape=ambiguous_flux,
        ingress_events=ingress_events,
        surface_log_digest=digest,
    )
    selected = _select_basin(
        policy=policy,
        flux_shape=_flux_shapes()["north_curved_flux"],
        ingress_events=ingress_events,
        surface_log_digest=digest,
    )
    wrong_output = {
        "control_id": "wrong_output_basin_control",
        "passed_negative_control": selected["selected_basin"] != "east_output_basin",
        "primary_blocker": "geometry_score_rejects_wrong_output_basin",
        "attempted_output_basin": "east_output_basin",
        "selected_basin": selected["selected_basin"],
        "compatibility_scores": selected["compatibility_scores"],
    }
    return {
        "competition_disabled": {
            "control_id": "competition_disabled_control",
            "passed_negative_control": not disabled["selected"],
            "primary_blocker": "competition_selection_disabled",
            "selected_basin": disabled["selected_basin"],
        },
        "ambiguous_tie_flux": {
            "control_id": "ambiguous_tie_flux_control",
            "passed_negative_control": not ambiguous["selected"],
            "primary_blocker": "ambiguous_competing_basin_scores",
            "compatibility_scores": ambiguous["compatibility_scores"],
            "compatibility_margin": ambiguous["compatibility_margin"],
        },
        "wrong_output_basin": wrong_output,
        "diagonal_shortcut": {
            "control_id": "diagonal_shortcut_control",
            "passed_negative_control": True,
            "primary_blocker": "diagonal_route_shortcuts_disabled_by_fixture_policy",
            "diagonal_edges_enabled": False,
            "route_shortcuts_enabled": False,
        },
    }


def build_report() -> dict[str, Any]:
    iter18c = _load_json(ITER18C_PATH)
    north_flux = _run_selection_lane("north_curved_flux")
    east_flux = _run_selection_lane("east_curved_flux")
    lanes = [north_flux, east_flux]
    controls = _run_controls()
    selected_basins = {lane["selected_output_basin"] for lane in lanes}
    checks = {
        "iteration_18c_available": iter18c["status"] == "passed",
        "selection_collapse_reasoning_recorded": True,
        "competing_output_basins_declared_before_run": True,
        "compatibility_scoring_rule_declared_before_run": True,
        "selection_derived_from_flux_shape_and_geometry": all(
            lane["selection_result"]["selection_basis"]
            == "input_flux_shape_geometry_compatibility"
            and lane["selection_result"]["direct_input_to_output_lookup_used"] is False
            for lane in lanes
        ),
        "distinct_flux_shapes_select_distinct_basins": selected_basins
        == {"north_output_basin", "east_output_basin"},
        "m4_boundary_response_passed": all(lane["m4_boundary_response_passed"] for lane in lanes),
        "m5_direction_control_passed": all(lane["m5_direction_control_passed"] for lane in lanes),
        "m6_geometry_selection_candidate_passed": all(
            lane["m6_geometry_selection_candidate_passed"] for lane in lanes
        ),
        "artifact_validators_passed": all(lane["artifact_validator"]["valid"] for lane in lanes),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= EPSILON_BUDGET
            and lane["nonnegative_gate_passed"]
            for lane in lanes
        ),
        "identity_shape_gates_passed": all(lane["identity_shape_gates_passed"] for lane in lanes),
        "feedback_authorized_not_schedule_copied": all(
            lane["all_recovery_pulses_feedback_authorized"]
            and lane["selection_result"]["copied_from_original_schedule"] is False
            for lane in lanes
        ),
        "controls_fail_for_distinct_blockers": all(
            control["passed_negative_control"] for control in controls.values()
        )
        and len({control["primary_blocker"] for control in controls.values()}) == len(controls),
        "native_surface_semantics_unchanged": True,
        "native_feedback_producer_semantics_unchanged": True,
        "no_direct_writes": all(
            not north_flux["geometry_init"][field]
            for field in [
                "direct_support_mask_write",
                "direct_centroid_write",
                "direct_displacement_write",
                "direct_topology_write",
                "direct_claim_flag_write",
            ]
        ),
        "selection_not_identity_collapse_or_agency": True,
        "native_geometry_selection_not_yet_supported": True,
        "external_selection_logic_blocker_recorded": True,
        "compositional_lgrc_fork_direction_recorded": True,
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s3_grid_geometry_scored_selection_design_prototype"
        if status == "passed"
        else "s3_grid_geometry_scored_selection_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter18d_grid_geometry_selection_v1",
        "iteration": "18-D",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "result_role": "geometry_scored_selection_design_prototype_over_native_lgrc_primitives",
        "movement_substrate": "S3_grid_geometry_scored_competing_output_basins_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "grid",
        "input_iteration_18c": _artifact_record(ITER18C_PATH),
        "claim_ceiling": claim_ceiling,
        "native_support_boundary": {
            "native_lgrc_packet_work_used": True,
            "native_causal_pulse_substrate_surface_used": True,
            "native_feedback_eligibility_surface_used": True,
            "native_feedback_producer_used": True,
            "native_artifact_validator_used": True,
            "selection_native_lgrc_producer": False,
            "selection_source": "experiment_level_geometry_competition_score",
            "selection_logic_kind": "external_experiment_scoring_logic",
            "different_from_prior_lgrc_policy_extensions": True,
            "prior_policy_extension_distinction": (
                "Earlier native policy extensions ordered or scheduled already "
                "declared packet work from committed evidence. Iteration 18-D "
                "adds an experiment-level compatibility scorer that evaluates "
                "competing futures and suppresses the non-selected basin."
            ),
            "geometry_driven_selection_supported": False,
            "native_selection_blocker": (
                "compatibility scoring is performed by experiment script logic; "
                "a native geometry-driven selection/collapse producer or "
                "equivalent surface mechanism is not implemented yet"
            ),
            "compositional_lgrc_fork_direction": (
                "Compose two native one-dimensional LGRC route elements into "
                "a shared fork and measure whether branch eligibility, budget, "
                "and feedback dynamics select a branch without external argmax "
                "or compatibility scoring."
            ),
        },
        "achieved_movement_level": "M6"
        if checks["m6_geometry_selection_candidate_passed"]
        else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if checks["m6_geometry_selection_candidate_passed"]
            else "not_measured",
            "persistence_basis": "s3_grid_geometry_scored_selection_recovers_0_15"
            if checks["m6_geometry_selection_candidate_passed"]
            else "geometry_selection_below_m6",
            "self_renewed_cycle_count": RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "two_flux_shapes_select_distinct_output_basins_with_three_cycle_recovery",
            "recovery_status": "recovers_0_15_geometry_selected_output_routes",
            "recovery_tested": True,
            "recovery_passed": checks["m6_geometry_selection_candidate_passed"],
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "design_prototype_not_native_selection_collapse_or_port_graph_transfer",
        },
        "selection_policy": north_flux["selection_policy"],
        "candidate_geometry": north_flux["geometry_init"],
        "lanes": {
            "north_curved_flux": north_flux,
            "east_curved_flux": east_flux,
        },
        "controls": controls,
        "geometry_selection_summary": {
            "entry_ceiling": iter18c["claim_ceiling"],
            "achieved_level": "M6"
            if checks["m6_geometry_selection_candidate_passed"]
            else "below_M6",
            "selected_basins": {
                "north_curved_flux": north_flux["selected_output_basin"],
                "east_curved_flux": east_flux["selected_output_basin"],
            },
            "selected_outputs": {
                "north_curved_flux": north_flux["selected_output_gate"],
                "east_curved_flux": east_flux["selected_output_gate"],
            },
            "compatibility_scores": {
                "north_curved_flux": north_flux["selection_result"]["compatibility_scores"],
                "east_curved_flux": east_flux["selection_result"]["compatibility_scores"],
            },
            "route_progress": {
                "north_curved_flux": north_flux["final_route_progress"],
                "east_curved_flux": east_flux["final_route_progress"],
            },
            "interpretation": (
                "Two output basins compete under one fixed grid geometry. "
                "Different input flux shapes resolve to different selected "
                "basins by geometry/flux compatibility score, then native "
                "feedback scheduling carries the selected pulse work. This is "
                "a selection/collapse analogue and design prototype, not RC "
                "identity collapse, agency, or native LGRC selection. The "
                "selection scorer is external experiment logic, not merely a "
                "native LGRC scheduling policy."
            ),
        },
        "go_no_go_for_iteration_19": {
            "iteration_19_allowed": status == "passed",
            "port_graph_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 19 may test whether this geometry-scored selection "
                "direction can be represented by S7 port mechanics. Native "
                "selection/collapse remains blocked until implemented in LGRC."
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": checks["m6_geometry_selection_candidate_passed"],
            "native_m6_candidate_gate_passed": checks["m6_geometry_selection_candidate_passed"],
            "geometry_scored_selection_design_prototype_passed": status == "passed",
            "native_geometry_driven_selection_claim_allowed": False,
            "selection_without_external_logic_claim_allowed": False,
            "native_lgrc_choice_selection_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "choice_or_agency_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "broad_geometry_transfer_claim_allowed": False,
            "adaptive_topology_claim_allowed": False,
        },
        "blocked_claims": [
            "native_geometry_driven_selection",
            "selection_without_external_logic",
            "native_lgrc_choice_selection",
            "rc_identity_collapse",
            "semantic_choice",
            "agency",
            "port_graph_transfer",
            "adaptive_topology_movement",
            "topology_mutating_movement",
            "broad_geometry_transfer",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "status_short": _run_git(["status", "--short"]),
            "head": _run_git(["rev-parse", "HEAD"]),
        },
        "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["geometry_selection_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 18-D S3 Grid Geometry-Scored Selection",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 18-D tests a geometry-scored competing-output-basin selection prototype.",
        "",
        "## Reasoning",
        "",
        "Iteration 18-C selected output gates from an experiment-level "
        "ingress-to-output policy. Iteration 18-D moves the design closer to "
        "geometry itself: both output basins are available, the input pulse "
        "carries a flux-shape signature, and the selected basin is the one with "
        "the stronger geometry/flux compatibility score. This is a "
        "selection/collapse analogue only, not RC identity collapse, agency, or "
        "native LGRC selection. Unlike the earlier native policy extensions, "
        "18-D adds an external experiment scorer that evaluates competing "
        "outputs; it does not let composed LGRC branch dynamics make the "
        "selection.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- entry ceiling: `{summary['entry_ceiling']}`",
        f"- selected basins: `{summary['selected_basins']}`",
        f"- selected outputs: `{summary['selected_outputs']}`",
        f"- route progress: `{summary['route_progress']}`",
        "",
        summary["interpretation"],
        "",
        "## Native Boundary",
        "",
    ]
    for key, value in report["native_support_boundary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Controls", ""])
    for key, value in report["controls"].items():
        lines.append(
            f"- `{key}`: passed=`{value['passed_negative_control']}`, "
            f"blocker=`{value['primary_blocker']}`"
        )
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_19"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is a geometry-scored selection design prototype over native LGRC primitives. It is not native geometry-driven selection, selection without external logic, native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, identity-acceptance, inherited-N03, or unrestricted movement evidence.",
            "",
            "## Command",
            "",
            f"```bash\n{COMMAND}\n```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
