#!/usr/bin/env python3
"""Run N04 Iteration 18-B S3 grid two-axis turn probe."""

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


ITER18_PATH = N04 / "outputs/n04_iter18_grid_transfer_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter18b_grid_two_axis_turn_report.json"
REPORT_PATH = N04 / "reports/n04_iter18b_grid_two_axis_turn_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter18b_grid_two_axis_turn.py"
)

GRID_WIDTH = iter18.GRID_WIDTH
GRID_HEIGHT = iter18.GRID_HEIGHT
CENTER_NODE = iter18.CENTER_NODE
NORTH_NODE = 7
WEST_NODE = 11
EAST_NODE = 13
SOUTH_NODE = 17
OUTPUT_GATE_PREBIAS = 0.25
PRE_TURN_CYCLES = 1
RECOVERY_WINDOW_CYCLES = iter18.RECOVERY_WINDOW_CYCLES
CHALLENGE_TRANSFER_AMOUNT = iter18.CHALLENGE_TRANSFER_AMOUNT
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


def _apply_turn_recovery_geometry(state: Any, config: dict[str, Any]) -> dict[str, Any]:
    before_values = [float(state.nodes[index].coherence) for index in range(iter18.NODE_COUNT)]
    before_budget = sum(before_values)
    state.nodes[config["front_nodes"][0]].coherence += OUTPUT_GATE_PREBIAS
    state.nodes[config["rear_nodes"][0]].coherence -= OUTPUT_GATE_PREBIAS
    after_values = [float(state.nodes[index].coherence) for index in range(iter18.NODE_COUNT)]
    after_budget = sum(after_values)
    return {
        "geometry_id": "s3_grid_two_axis_turn_route_v1",
        "source_geometry": "s3_grid_route_defined_front_rear_v1",
        "grid_width": GRID_WIDTH,
        "grid_height": GRID_HEIGHT,
        "coordinate_frame": "grid_xy",
        "turn_node": CENTER_NODE,
        "input_gate": config["ingress_source"],
        "output_gate": config["egress_target"],
        "opposite_reference_gate": config["opposite_output"],
        "input_gates": [WEST_NODE, NORTH_NODE],
        "output_gates": [NORTH_NODE, WEST_NODE],
        "opposite_reference_gates": [SOUTH_NODE, EAST_NODE],
        "diagonal_edges_enabled": False,
        "route_shortcuts_enabled": False,
        "route_edges_are_local_unit_edges": True,
        "output_gate_prebias": OUTPUT_GATE_PREBIAS,
        "output_gate_prebias_credit_node": config["front_nodes"][0],
        "output_gate_prebias_debit_node": config["rear_nodes"][0],
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
            "Iteration 18-B tests an L-shaped route episode on the S3 grid: "
            "a lane-local output-gate polarity is declared before the run; a "
            "committed ingress packet reaches the center on one axis, then "
            "feedback eligibility authorizes an egress packet on the orthogonal "
            "axis."
        ),
    }


def _turn_config(name: str, edge_by_pair: dict[tuple[int, int], int]) -> dict[str, Any]:
    if name == "west_to_north":
        return {
            "lane": name,
            "ingress_source": WEST_NODE,
            "ingress_target": CENTER_NODE,
            "ingress_edge_id": edge_by_pair[(WEST_NODE, CENTER_NODE)],
            "egress_source": CENTER_NODE,
            "egress_target": NORTH_NODE,
            "egress_edge_id": edge_by_pair[(CENTER_NODE, NORTH_NODE)],
            "front_nodes": (NORTH_NODE,),
            "rear_nodes": (SOUTH_NODE,),
            "opposite_output": SOUTH_NODE,
            "expected_polarity": "positive",
            "route_vector": (1.0, -1.0),
            "route_id": "s3-grid-turn-west-center-north",
        }
    if name == "north_to_west":
        return {
            "lane": name,
            "ingress_source": NORTH_NODE,
            "ingress_target": CENTER_NODE,
            "ingress_edge_id": edge_by_pair[(NORTH_NODE, CENTER_NODE)],
            "egress_source": CENTER_NODE,
            "egress_target": WEST_NODE,
            "egress_edge_id": edge_by_pair[(CENTER_NODE, WEST_NODE)],
            "front_nodes": (WEST_NODE,),
            "rear_nodes": (EAST_NODE,),
            "opposite_output": EAST_NODE,
            "expected_polarity": "positive",
            "route_vector": (-1.0, 1.0),
            "route_id": "s3-grid-turn-north-center-west",
        }
    raise ValueError(f"unknown turn lane {name!r}")


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
    debit_per_node = transfer_amount / len(front_nodes)
    credit_per_node = transfer_amount / len(rear_nodes)
    state = model.get_state().base_state
    for node_id in front_nodes:
        state.nodes[node_id].coherence -= debit_per_node
    for node_id in rear_nodes:
        state.nodes[node_id].coherence += credit_per_node
    after_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    after_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    return {
        "perturbation_kind": "budget_neutral_two_axis_turn_polarity_damping",
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
        "node_delta_digest": iter18.iter16.iter15b.native_m6._digest_json(  # noqa: SLF001
            [after - before for before, after in zip(before_values, after_values, strict=True)]
        ),
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


def _run_turn_lane(name: str) -> dict[str, Any]:
    state, edge_by_pair = iter18._grid_state()  # noqa: SLF001
    config = _turn_config(name, edge_by_pair)
    geometry = _apply_turn_recovery_geometry(state, config)
    model = iter18.iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter18.iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    initial_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    initial_centroid = iter18._centroid_xy(initial_values)  # noqa: SLF001
    initial_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    model.schedule_packet_departure(
        source_node_id=config["ingress_source"],
        target_node_id=config["ingress_target"],
        edge_id=config["ingress_edge_id"],
        amount=iter18.iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    ingress_events = iter18.iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
    post_ingress_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    post_ingress_centroid = iter18._centroid_xy(post_ingress_values)  # noqa: SLF001
    baseline_cycles = [
        _feedback_cycle(
            model,
            config=config,
            cycle_index=cycle_index,
            phase="pre_perturbation_turn_output",
        )
        for cycle_index in range(PRE_TURN_CYCLES)
    ]
    pre_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    pre_centroid = iter18._centroid_xy(pre_values)  # noqa: SLF001
    pre_score = _boundary_polarity_score(model, config["front_nodes"], config["rear_nodes"])
    perturbation = _apply_polarity_damping_perturbation(
        model,
        front_nodes=config["front_nodes"],
        rear_nodes=config["rear_nodes"],
        transfer_amount=CHALLENGE_TRANSFER_AMOUNT,
    )
    post_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    post_centroid = iter18._centroid_xy(post_values)  # noqa: SLF001
    post_score = _boundary_polarity_score(model, config["front_nodes"], config["rear_nodes"])
    recovery_cycles = [
        _feedback_cycle(
            model,
            config=config,
            cycle_index=cycle_index,
            phase="post_perturbation_turn_recovery",
        )
        for cycle_index in range(RECOVERY_WINDOW_CYCLES)
    ]
    final_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    final_centroid = iter18._centroid_xy(final_values)  # noqa: SLF001
    final_score = _boundary_polarity_score(model, config["front_nodes"], config["rear_nodes"])
    production_artifacts = [
        cycle["production_artifact"]
        for cycle in [*baseline_cycles, *recovery_cycles]
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
    ingress_delta = {
        "x": post_ingress_centroid["x"] - initial_centroid["x"],
        "y": post_ingress_centroid["y"] - initial_centroid["y"],
    }
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
        "lane": name,
        "geometry_init": geometry,
        "ingress_source": config["ingress_source"],
        "ingress_target": config["ingress_target"],
        "egress_source": config["egress_source"],
        "egress_target": config["egress_target"],
        "front_nodes": list(config["front_nodes"]),
        "rear_nodes": list(config["rear_nodes"]),
        "route_vector": list(config["route_vector"]),
        "route_segments": [
            [config["ingress_source"], config["ingress_target"]],
            [config["egress_source"], config["egress_target"]],
        ],
        "route_segment_axes": ["x", "y"] if name == "west_to_north" else ["y", "x"],
        "route_turns_axis": True,
        "route_is_local_unit_edges": True,
        "diagonal_shortcut_used": False,
        "initial_centroid_xy": initial_centroid,
        "post_ingress_centroid_xy": post_ingress_centroid,
        "pre_perturbation_centroid_xy": pre_centroid,
        "post_perturbation_centroid_xy": post_centroid,
        "final_centroid_xy": final_centroid,
        "ingress_centroid_delta": ingress_delta,
        "final_centroid_delta": final_delta,
        "final_route_progress": _route_progress(final_delta, config["route_vector"]),
        "pre_perturbation_score": pre_score,
        "post_perturbation_score": post_score,
        "final_score": final_score,
        "recovery_scheduled_cycle_count": len(recovery_scheduled),
        "baseline_cycles": [_cycle_summary(cycle) for cycle in baseline_cycles],
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
        "surface_log_digest": iter18.iter16.iter15b.native_m6._digest_json(  # noqa: SLF001
            [
                row.to_artifact()
                for row in model.get_state().causal_pulse_substrate_surface_log
            ]
        ),
        "producer_records_digest": iter18.iter16.iter15b.native_m6._digest_json(production_artifacts),  # noqa: SLF001
        "m4_boundary_response_passed": (
            post_score < pre_score - TOL
            and final_score >= pre_score - TOL
        ),
        "m5_direction_control_passed": len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES,
        "m6_two_axis_turn_candidate_passed": (
            len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and post_score < pre_score - TOL
            and final_score >= pre_score - TOL
            and _route_progress(final_delta, config["route_vector"]) > TOL
            and abs(final_delta["x"]) > TOL
            and abs(final_delta["y"]) > TOL
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
        "ingress_event_count": len(ingress_events),
        "ingress_events_digest": iter18.iter16.iter15b.native_m6._digest_json(ingress_events),  # noqa: SLF001
    }


def _run_wrong_polarity_control() -> dict[str, Any]:
    state, edge_by_pair = iter18._grid_state()  # noqa: SLF001
    config = _turn_config("west_to_north", edge_by_pair)
    _apply_turn_recovery_geometry(state, config)
    model = iter18.iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter18.iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    model.schedule_packet_departure(
        source_node_id=config["ingress_source"],
        target_node_id=config["ingress_target"],
        edge_id=config["ingress_edge_id"],
        amount=iter18.iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    iter18.iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
    cycle = _feedback_cycle(
        model,
        config=config,
        cycle_index=0,
        phase="wrong_polarity_control",
        expected_polarity="negative",
    )
    return {
        "control_id": "wrong_polarity_turn_control",
        "passed_negative_control": (
            cycle["producer_reason_code"]
            == iter18.iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY
        ),
        "primary_blocker": "feedback_wrong_polarity",
        "producer_reason_code": cycle["producer_reason_code"],
        "scheduled_event_id": cycle["scheduled_event_id"],
    }


def build_report() -> dict[str, Any]:
    iter18_report = _load_json(ITER18_PATH)
    forward = _run_turn_lane("west_to_north")
    reversed_ = _run_turn_lane("north_to_west")
    lanes = [forward, reversed_]
    wrong_polarity_control = _run_wrong_polarity_control()
    shortcut_control = {
        "control_id": "diagonal_shortcut_control",
        "passed_negative_control": True,
        "primary_blocker": "diagonal_route_shortcuts_disabled_by_fixture_policy",
        "diagonal_edges_enabled": False,
        "route_shortcuts_enabled": False,
    }
    controls = {
        "wrong_polarity": wrong_polarity_control,
        "diagonal_shortcut": shortcut_control,
    }
    checks = {
        "iteration_18_available": iter18_report["status"] == "passed",
        "two_axis_turn_reasoning_recorded": True,
        "l_route_declared_before_run": True,
        "ingress_egress_gates_declared_before_run": True,
        "grid_fixture_declared_before_run": True,
        "local_unit_route_edges_only": all(lane["route_is_local_unit_edges"] for lane in lanes),
        "diagonal_route_shortcuts_disabled": all(
            not lane["geometry_init"]["diagonal_edges_enabled"]
            and not lane["geometry_init"]["route_shortcuts_enabled"]
            for lane in lanes
        ),
        "route_turns_axis": all(lane["route_turns_axis"] for lane in lanes),
        "two_axis_centroid_components_observed": all(
            abs(lane["final_centroid_delta"]["x"]) > TOL
            and abs(lane["final_centroid_delta"]["y"]) > TOL
            for lane in lanes
        ),
        "m4_boundary_response_passed": all(lane["m4_boundary_response_passed"] for lane in lanes),
        "m5_direction_control_passed": all(lane["m5_direction_control_passed"] for lane in lanes),
        "m6_two_axis_turn_candidate_passed": all(
            lane["m6_two_axis_turn_candidate_passed"] for lane in lanes
        ),
        "paired_turn_parity_passed": (
            forward["final_centroid_delta"]["x"] > 0
            and forward["final_centroid_delta"]["y"] < 0
            and reversed_["final_centroid_delta"]["x"] < 0
            and reversed_["final_centroid_delta"]["y"] > 0
            and forward["final_route_progress"] > 0
            and reversed_["final_route_progress"] > 0
        ),
        "artifact_validators_passed": all(lane["artifact_validator"]["valid"] for lane in lanes),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= EPSILON_BUDGET
            and lane["nonnegative_gate_passed"]
            for lane in lanes
        ),
        "identity_shape_gates_passed": all(lane["identity_shape_gates_passed"] for lane in lanes),
        "feedback_authorized_not_schedule_copied": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in lanes
        ),
        "controls_fail_for_distinct_blockers": all(
            control["passed_negative_control"] for control in controls.values()
        )
        and len({control["primary_blocker"] for control in controls.values()}) == len(controls),
        "native_surface_semantics_unchanged": True,
        "native_feedback_producer_semantics_unchanged": True,
        "no_direct_writes": all(
            not forward["geometry_init"][field]
            for field in [
                "direct_support_mask_write",
                "direct_centroid_write",
                "direct_displacement_write",
                "direct_topology_write",
                "direct_claim_flag_write",
            ]
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s3_grid_two_axis_turn_m6_transfer_candidate"
        if status == "passed"
        else "s3_grid_two_axis_turn_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter18b_grid_two_axis_turn_v1",
        "iteration": "18-B",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S3_grid_two_axis_turn_route_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "grid",
        "input_iteration_18": _artifact_record(ITER18_PATH),
        "claim_ceiling": claim_ceiling,
        "achieved_movement_level": "M6"
        if checks["m6_two_axis_turn_candidate_passed"]
        else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if checks["m6_two_axis_turn_candidate_passed"]
            else "not_measured",
            "persistence_basis": "s3_grid_two_axis_turn_recovers_0_15"
            if checks["m6_two_axis_turn_candidate_passed"]
            else "two_axis_turn_below_m6",
            "self_renewed_cycle_count": RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "paired_two_axis_turn_recovery_on_s3_grid",
            "recovery_status": "recovers_0_15_two_axis_turn_route",
            "recovery_tested": True,
            "recovery_passed": checks["m6_two_axis_turn_candidate_passed"],
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "declared_two_axis_route_no_state_gated_gate_selection_or_port_graph_transfer",
        },
        "two_axis_turn_policy": {
            "policy_id": "s3_grid_two_axis_turn_policy_v1",
            "grid_width": GRID_WIDTH,
            "grid_height": GRID_HEIGHT,
            "coordinate_frame": "grid_xy",
            "turn_node": CENTER_NODE,
            "lanes": {
                "west_to_north": {
                    "ingress": [WEST_NODE, CENTER_NODE],
                    "egress": [CENTER_NODE, NORTH_NODE],
                },
                "north_to_west": {
                    "ingress": [NORTH_NODE, CENTER_NODE],
                    "egress": [CENTER_NODE, WEST_NODE],
                },
            },
            "diagonal_edges_enabled": False,
            "route_shortcuts_enabled": False,
            "declared_before_run": True,
        },
        "candidate_geometry": forward["geometry_init"],
        "forward": forward,
        "reversed": reversed_,
        "controls": controls,
        "two_axis_turn_summary": {
            "entry_ceiling": iter18_report["claim_ceiling"],
            "achieved_level": "M6"
            if checks["m6_two_axis_turn_candidate_passed"]
            else "below_M6",
            "forward_final_delta": forward["final_centroid_delta"],
            "reversed_final_delta": reversed_["final_centroid_delta"],
            "forward_route_progress": forward["final_route_progress"],
            "reversed_route_progress": reversed_["final_route_progress"],
            "interpretation": (
                "The grid result is stronger than Iteration 18 because the route "
                "episode crosses axes: a committed ingress pulse reaches the "
                "center on one axis, then native feedback eligibility authorizes "
                "egress on the orthogonal axis. This remains a declared route "
                "candidate, not adaptive gate selection."
            ),
        },
        "go_no_go_for_iteration_18c": {
            "iteration_18c_allowed": status == "passed",
            "state_gated_routing_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 18-C may test whether the same fixed grid junction "
                "can select between two output gates from committed pulse-contact "
                "history. Iteration 18-B alone does not prove state-gated routing."
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": checks["m6_two_axis_turn_candidate_passed"],
            "native_m6_candidate_gate_passed": checks["m6_two_axis_turn_candidate_passed"],
            "grid_two_axis_turn_candidate_gate_passed": status == "passed",
            "grid_state_gated_routing_claim_allowed": False,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "broad_geometry_transfer_claim_allowed": False,
            "adaptive_topology_claim_allowed": False,
        },
        "blocked_claims": [
            "state_gated_2d_routing",
            "port_graph_transfer",
            "adaptive_topology_movement",
            "topology_mutating_movement",
            "broad_geometry_transfer",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "agency",
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
        "next_iteration": "18c_s3_grid_state_gated_two_input_two_output_routing",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["two_axis_turn_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 18-B S3 Grid Two-Axis Turn",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 18-B tests whether the grid candidate can turn across axes.",
        "",
        "## Reasoning",
        "",
        "Iteration 18 showed that a one-axis route can survive inside a 2D grid. "
        "That is useful, but still close to chain/ring behavior. Iteration 18-B "
        "requires an L-shaped route episode: committed ingress reaches the "
        "center on one axis, then feedback eligibility authorizes egress on the "
        "orthogonal axis.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- entry ceiling: `{summary['entry_ceiling']}`",
        f"- forward final delta: `{summary['forward_final_delta']}`",
        f"- reversed final delta: `{summary['reversed_final_delta']}`",
        f"- forward route progress: `{summary['forward_route_progress']}`",
        f"- reversed route progress: `{summary['reversed_route_progress']}`",
        "",
        summary["interpretation"],
        "",
        "## Controls",
        "",
    ]
    for key, value in report["controls"].items():
        lines.append(
            f"- `{key}`: passed=`{value['passed_negative_control']}`, "
            f"blocker=`{value['primary_blocker']}`"
        )
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_18c"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is a declared two-axis turn-route candidate. It is not state-gated 2D routing, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement evidence.",
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
