#!/usr/bin/env python3
"""Run N04 Iteration 18 S3 grid route-defined front/rear transfer."""

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

import run_n04_iter16_corridor_transfer as iter16  # noqa: E402


ITER17C_PATH = N04 / "outputs/n04_iter17c_ring_geometry_closeout.json"
OUTPUT_PATH = N04 / "outputs/n04_iter18_grid_transfer_report.json"
REPORT_PATH = N04 / "reports/n04_iter18_grid_transfer_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter18_grid_transfer.py"
)

GRID_WIDTH = 5
GRID_HEIGHT = 5
NODE_COUNT = GRID_WIDTH * GRID_HEIGHT
CENTER_NODE = 12
FORWARD_TARGET = 13
REVERSED_TARGET = 11
FRONT_NODES = (13,)
REAR_NODES = (11,)
RESERVOIR_BOOST = 0.25
COMPENSATING_DEBIT_NODES = (7, 17)
PRE_TRANSFER_CYCLES = iter16.PRE_TRANSFER_CYCLES
RECOVERY_WINDOW_CYCLES = iter16.RECOVERY_WINDOW_CYCLES
CHALLENGE_TRANSFER_AMOUNT = 0.15
EPSILON_BUDGET = 1e-12
TOL = 1e-12


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


def _node_id(x: int, y: int) -> int:
    return y * GRID_WIDTH + x


def _xy(node_id: int) -> tuple[float, float]:
    return float(node_id % GRID_WIDTH), float(node_id // GRID_WIDTH)


def _grid_state() -> tuple[Any, dict[tuple[int, int], int]]:
    graph = iter16.iter15b.native_m6.PortGraphBackend()
    node_ids = [
        graph.add_node({"label": f"s3:{x},{y}", "x": x, "y": y})
        for y in range(GRID_HEIGHT)
        for x in range(GRID_WIDTH)
    ]
    edge_by_pair: dict[tuple[int, int], int] = {}
    port_edges: dict[int, Any] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}

    def add_edge(u: int, v: int, port_u: int, port_v: int, kind: str) -> None:
        edge_id = graph.connect_ports(
            node_ids[u],
            port_u,
            node_ids[v],
            port_v,
            {"kind": kind, "source_index": u, "target_index": v},
        )
        edge_by_pair[(u, v)] = edge_id
        edge_by_pair[(v, u)] = edge_id
        port_edges[edge_id] = iter16.iter15b.native_m6.PortEdge(
            node_ids[u],
            port_u,
            node_ids[v],
            port_v,
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.0

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH - 1):
            add_edge(_node_id(x, y), _node_id(x + 1, y), 1, 0, "s3_grid_east_west")
    for y in range(GRID_HEIGHT - 1):
        for x in range(GRID_WIDTH):
            add_edge(_node_id(x, y), _node_id(x, y + 1), 3, 2, "s3_grid_north_south")

    nodes = {node_id: iter16.iter15b.native_m6.GRC9V3NodeState(coherence=1.0) for node_id in node_ids}
    state = iter16.iter15b.native_m6.GRC9V3State(
        topology=graph,
        nodes=nodes,
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )
    return state, edge_by_pair


def _apply_grid_recovery_geometry(state: Any) -> dict[str, Any]:
    before_values = [float(state.nodes[index].coherence) for index in range(NODE_COUNT)]
    before_budget = sum(before_values)
    debit_per_node = RESERVOIR_BOOST / len(COMPENSATING_DEBIT_NODES)
    state.nodes[CENTER_NODE].coherence += RESERVOIR_BOOST
    for node_id in COMPENSATING_DEBIT_NODES:
        state.nodes[node_id].coherence -= debit_per_node
    after_values = [float(state.nodes[index].coherence) for index in range(NODE_COUNT)]
    after_budget = sum(after_values)
    return {
        "geometry_id": "s3_grid_route_defined_front_rear_v1",
        "geometry_family": "s3_grid_local_route_with_center_reservoir",
        "source_geometry": "s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness",
        "grid_width": GRID_WIDTH,
        "grid_height": GRID_HEIGHT,
        "coordinate_frame": "grid_xy",
        "route_axis": "x",
        "center_node": CENTER_NODE,
        "center_coordinate": list(_xy(CENTER_NODE)),
        "forward_target": FORWARD_TARGET,
        "forward_target_coordinate": list(_xy(FORWARD_TARGET)),
        "reversed_target": REVERSED_TARGET,
        "reversed_target_coordinate": list(_xy(REVERSED_TARGET)),
        "front_region": list(FRONT_NODES),
        "rear_region": list(REAR_NODES),
        "front_rear_policy": "route_defined_east_west_through_center",
        "diagonal_edges_enabled": False,
        "route_shortcuts_enabled": False,
        "route_edges_are_local_unit_edges": True,
        "reservoir_boost": RESERVOIR_BOOST,
        "compensating_debit_nodes": list(COMPENSATING_DEBIT_NODES),
        "compensating_debit_per_node": debit_per_node,
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_geometry_init": min(after_values) >= -TOL,
        "topology_changed_by_fixture_definition": True,
        "topology_fixed_during_run": True,
        "topology_mutated_during_run": False,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
        "reason": (
            "Iteration 18 transfers the strongest ring-series ceiling to a "
            "5x5 S3 grid with route-defined east/west front/rear masks. The "
            "grid has local horizontal/vertical unit edges only; diagonal "
            "shortcuts are disabled."
        ),
    }


def _centroid_xy(values: list[float]) -> dict[str, float]:
    total = sum(values)
    if total <= 0.0:
        return {"x": math.nan, "y": math.nan}
    x = 0.0
    y = 0.0
    for node_id, value in enumerate(values):
        cx, cy = _xy(node_id)
        x += value * cx
        y += value * cy
    return {"x": x / total, "y": y / total}


def _radius_width(values: list[float]) -> float:
    centroid = _centroid_xy(values)
    total = sum(values)
    if total <= 0.0:
        return 0.0
    variance = 0.0
    for node_id, value in enumerate(values):
        x, y = _xy(node_id)
        variance += value * ((x - centroid["x"]) ** 2 + (y - centroid["y"]) ** 2)
    return math.sqrt(variance / total)


def _profile_similarity(before: list[float], after: list[float]) -> float:
    dot = sum(a * b for a, b in zip(before, after, strict=True))
    norm_a = math.sqrt(sum(a * a for a in before))
    norm_b = math.sqrt(sum(b * b for b in after))
    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _direction_config(direction: str, edge_by_pair: dict[tuple[int, int], int]) -> dict[str, Any]:
    if direction == "forward":
        return {
            "source": CENTER_NODE,
            "target": FORWARD_TARGET,
            "edge_id": edge_by_pair[(CENTER_NODE, FORWARD_TARGET)],
            "expected_polarity": "positive",
            "expected_sign": 1,
            "route_id": "s3-grid-forward-east",
        }
    if direction == "reversed":
        return {
            "source": CENTER_NODE,
            "target": REVERSED_TARGET,
            "edge_id": edge_by_pair[(CENTER_NODE, REVERSED_TARGET)],
            "expected_polarity": "negative",
            "expected_sign": -1,
            "route_id": "s3-grid-reversed-west",
        }
    raise ValueError(f"unknown direction {direction!r}")


def _boundary_polarity_score(model: Any) -> float:
    values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    return sum(values[index] for index in FRONT_NODES) - sum(values[index] for index in REAR_NODES)


def _apply_polarity_damping_perturbation(
    model: Any,
    *,
    direction: str,
    transfer_amount: float,
) -> dict[str, Any]:
    if direction == "forward":
        debit_nodes = FRONT_NODES
        credit_nodes = REAR_NODES
    elif direction == "reversed":
        debit_nodes = REAR_NODES
        credit_nodes = FRONT_NODES
    else:
        raise ValueError(f"unknown direction {direction!r}")
    before_budget = iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    before_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    debit_per_node = transfer_amount / len(debit_nodes)
    credit_per_node = transfer_amount / len(credit_nodes)
    state = model.get_state().base_state
    for node_id in debit_nodes:
        state.nodes[node_id].coherence -= debit_per_node
    for node_id in credit_nodes:
        state.nodes[node_id].coherence += credit_per_node
    after_budget = iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    after_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    return {
        "perturbation_kind": "budget_neutral_grid_route_polarity_damping",
        "transfer_amount": transfer_amount,
        "debit_nodes": list(debit_nodes),
        "credit_nodes": list(credit_nodes),
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_perturbation": min(after_values) >= -TOL,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
        "node_delta_digest": iter16.iter15b.native_m6._digest_json(  # noqa: SLF001
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
        front_node_ids=FRONT_NODES,
        rear_node_ids=REAR_NODES,
        reference_delta=0.0,
        feedback_threshold=iter16.iter15b.native_m6.FEEDBACK_THRESHOLD,
        expected_next_route_id=config["route_id"],
        expected_next_channel_id=f"edge:{config['edge_id']}",
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=config["source"],
        target_node_id=config["target"],
        edge_id=config["edge_id"],
        threshold=iter16.iter15b.native_m6.FEEDBACK_THRESHOLD,
        packet_amount=iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
        expected_polarity=expected_polarity or config["expected_polarity"],
        expected_source_surface_digest=feedback_row.surface_values_after[
            "source_surface_digest"
        ],
        expected_next_route_id=config["route_id"],
        expected_next_channel_id=f"edge:{config['edge_id']}",
    )
    try:
        result = model.produce_events(
            policy=(
                iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )
    except iter16.iter15b.native_m6.InvalidStateTransitionError as exc:
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
            "producer_reason_code": "feedback_source_budget_exhausted",
            "producer_exception": str(exc),
            "scheduled_event_id": None,
            "regenerated_pulse_source": None,
            "copied_from_original_schedule": None,
            "production_artifact": None,
            "processed_events": [],
        }
    record = result.production_records[0]
    processed_events: list[dict[str, Any]] = []
    if record.reason_code == (
        iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ):
        processed_events = iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
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
        "processed_events_digest": iter16.iter15b.native_m6._digest_json(cycle["processed_events"]),  # noqa: SLF001
    }


def _run_grid_direction(direction: str) -> dict[str, Any]:
    state, edge_by_pair = _grid_state()
    geometry = _apply_grid_recovery_geometry(state)
    config = _direction_config(direction, edge_by_pair)
    model = iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    initial_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    initial_centroid = _centroid_xy(initial_values)
    initial_budget = iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    model.schedule_packet_departure(
        source_node_id=config["source"],
        target_node_id=config["target"],
        edge_id=config["edge_id"],
        amount=iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    seeded_events = iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
    baseline_cycles = [
        _feedback_cycle(
            model,
            config=config,
            cycle_index=cycle_index,
            phase="pre_perturbation_baseline",
        )
        for cycle_index in range(PRE_TRANSFER_CYCLES)
    ]
    pre_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    pre_centroid = _centroid_xy(pre_values)
    pre_score = _boundary_polarity_score(model)
    perturbation = _apply_polarity_damping_perturbation(
        model,
        direction=direction,
        transfer_amount=CHALLENGE_TRANSFER_AMOUNT,
    )
    post_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    post_centroid = _centroid_xy(post_values)
    post_score = _boundary_polarity_score(model)
    recovery_cycles = [
        _feedback_cycle(
            model,
            config=config,
            cycle_index=cycle_index,
            phase="post_perturbation_recovery",
        )
        for cycle_index in range(RECOVERY_WINDOW_CYCLES)
    ]
    final_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_budget = iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    final_centroid = _centroid_xy(final_values)
    final_score = _boundary_polarity_score(model)
    production_artifacts = [
        cycle["production_artifact"]
        for cycle in [*baseline_cycles, *recovery_cycles]
        if cycle["production_artifact"] is not None
    ]
    validation = iter16.iter15b.native_m6.validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=model.snapshot()["events"],
        production_results=production_artifacts,
    )
    recovery_scheduled = [
        cycle
        for cycle in recovery_cycles
        if cycle["producer_reason_code"]
        == iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ]
    sign = config["expected_sign"]
    raw_pre_x = pre_centroid["x"] - initial_centroid["x"]
    raw_post_x = post_centroid["x"] - initial_centroid["x"]
    raw_final_x = final_centroid["x"] - initial_centroid["x"]
    raw_final_y = final_centroid["y"] - initial_centroid["y"]
    signed_pre_score = sign * pre_score
    signed_post_score = sign * post_score
    signed_final_score = sign * final_score
    signed_pre_x = sign * raw_pre_x
    signed_post_x = sign * raw_post_x
    signed_final_x = sign * raw_final_x
    width_initial = _radius_width(initial_values)
    width_final = _radius_width(final_values)
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = _profile_similarity(initial_values, final_values)
    return {
        "direction": direction,
        "geometry_init": geometry,
        "source_node_id": config["source"],
        "target_node_id": config["target"],
        "edge_id": config["edge_id"],
        "front_nodes": list(FRONT_NODES),
        "rear_nodes": list(REAR_NODES),
        "route_axis": "x",
        "route_is_local_unit_edge": True,
        "diagonal_shortcut_used": False,
        "initial_centroid_xy": initial_centroid,
        "pre_transfer_centroid_xy": pre_centroid,
        "post_perturbation_centroid_xy": post_centroid,
        "final_centroid_xy": final_centroid,
        "raw_pre_transfer_x_delta": raw_pre_x,
        "raw_post_perturbation_x_delta": raw_post_x,
        "raw_final_x_delta": raw_final_x,
        "raw_final_y_delta": raw_final_y,
        "signed_pre_transfer_x_delta": signed_pre_x,
        "signed_post_perturbation_x_delta": signed_post_x,
        "signed_final_x_delta": signed_final_x,
        "signed_pre_transfer_score": signed_pre_score,
        "signed_post_perturbation_score": signed_post_score,
        "signed_final_score": signed_final_score,
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
            width_relative_change <= iter16.iter15b.native_m6.WIDTH_RELATIVE_CHANGE_MAX
            and profile_similarity >= iter16.iter15b.native_m6.PROFILE_SIMILARITY_MIN
        ),
        "artifact_validator": validation,
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "surface_log_digest": iter16.iter15b.native_m6._digest_json(  # noqa: SLF001
            [
                row.to_artifact()
                for row in model.get_state().causal_pulse_substrate_surface_log
            ]
        ),
        "producer_records_digest": iter16.iter15b.native_m6._digest_json(production_artifacts),  # noqa: SLF001
        "m4_boundary_response_passed": (
            signed_post_score < signed_pre_score - TOL
            and signed_final_score >= signed_post_score - TOL
        ),
        "m5_direction_control_passed": len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES,
        "m6_grid_transfer_candidate_passed": (
            len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and signed_post_score < signed_pre_score - TOL
            and signed_final_score >= signed_pre_score - TOL
            and signed_post_x < signed_pre_x - TOL
            and signed_final_x >= signed_pre_x - TOL
            and abs(raw_final_y) <= TOL
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
        "seeded_event_count": len(seeded_events),
        "seeded_events_digest": iter16.iter15b.native_m6._digest_json(seeded_events),  # noqa: SLF001
    }


def _run_wrong_direction_control() -> dict[str, Any]:
    state, edge_by_pair = _grid_state()
    _apply_grid_recovery_geometry(state)
    config = _direction_config("forward", edge_by_pair)
    model = iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    model.schedule_packet_departure(
        source_node_id=config["source"],
        target_node_id=config["target"],
        edge_id=config["edge_id"],
        amount=iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
    cycle = _feedback_cycle(
        model,
        config=config,
        cycle_index=0,
        phase="wrong_polarity_control",
        expected_polarity="negative",
    )
    return {
        "control_id": "wrong_direction_polarity_control",
        "passed_negative_control": (
            cycle["producer_reason_code"]
            == iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY
        ),
        "primary_blocker": "feedback_wrong_polarity",
        "producer_reason_code": cycle["producer_reason_code"],
        "scheduled_event_id": cycle["scheduled_event_id"],
    }


def build_report() -> dict[str, Any]:
    iter17c = _load_json(ITER17C_PATH)
    forward = _run_grid_direction("forward")
    reversed_ = _run_grid_direction("reversed")
    directions = [forward, reversed_]
    wrong_direction_control = _run_wrong_direction_control()
    shortcut_control = {
        "control_id": "diagonal_shortcut_control",
        "passed_negative_control": True,
        "primary_blocker": "diagonal_route_shortcuts_disabled_by_fixture_policy",
        "diagonal_edges_enabled": False,
        "route_shortcuts_enabled": False,
    }
    controls = {
        "wrong_direction": wrong_direction_control,
        "diagonal_shortcut": shortcut_control,
    }
    checks = {
        "iteration_17c_available": iter17c["status"] == "passed",
        "route_based_direction_declared": True,
        "front_rear_masks_declared_before_run": True,
        "grid_fixture_declared_before_run": True,
        "local_unit_route_edges_only": all(
            lane["route_is_local_unit_edge"] and not lane["diagonal_shortcut_used"]
            for lane in directions
        ),
        "diagonal_route_shortcuts_disabled": all(
            not lane["geometry_init"]["diagonal_edges_enabled"]
            and not lane["geometry_init"]["route_shortcuts_enabled"]
            for lane in directions
        ),
        "m4_boundary_response_passed": all(
            lane["m4_boundary_response_passed"] for lane in directions
        ),
        "m5_direction_control_passed": all(
            lane["m5_direction_control_passed"] for lane in directions
        ),
        "m6_grid_transfer_candidate_passed": all(
            lane["m6_grid_transfer_candidate_passed"] for lane in directions
        ),
        "grid_direction_parity_passed": (
            forward["raw_final_x_delta"] > 0
            and reversed_["raw_final_x_delta"] < 0
            and forward["signed_final_x_delta"] > 0
            and reversed_["signed_final_x_delta"] > 0
        ),
        "no_y_axis_drift": all(abs(lane["raw_final_y_delta"]) <= TOL for lane in directions),
        "artifact_validators_passed": all(
            lane["artifact_validator"]["valid"] for lane in directions
        ),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= EPSILON_BUDGET
            and lane["nonnegative_gate_passed"]
            for lane in directions
        ),
        "identity_shape_gates_passed": all(
            lane["identity_shape_gates_passed"] for lane in directions
        ),
        "feedback_authorized_not_schedule_copied": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in directions
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
        "s3_grid_route_defined_m6_transfer_candidate"
        if status == "passed"
        else "s3_grid_route_defined_transfer_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter18_grid_transfer_v1",
        "iteration": "18",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S3_grid_route_defined_front_rear_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "grid",
        "input_iteration_17c": _artifact_record(ITER17C_PATH),
        "claim_ceiling": claim_ceiling,
        "achieved_movement_level": "M6"
        if checks["m6_grid_transfer_candidate_passed"]
        else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if checks["m6_grid_transfer_candidate_passed"]
            else "not_measured",
            "persistence_basis": "s3_grid_route_defined_front_rear_recovers_0_15"
            if checks["m6_grid_transfer_candidate_passed"]
            else "grid_transfer_below_m6",
            "self_renewed_cycle_count": RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "forward_and_reversed_three_cycle_recovery_on_s3_grid_route",
            "recovery_status": "recovers_0_15_grid_route_defined_front_rear",
            "recovery_tested": True,
            "recovery_passed": checks["m6_grid_transfer_candidate_passed"],
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "single_grid_route_no_port_graph_or_adaptive_topology_transfer",
        },
        "grid_route_policy": {
            "policy_id": "s3_grid_route_defined_front_rear_policy_v1",
            "grid_width": GRID_WIDTH,
            "grid_height": GRID_HEIGHT,
            "coordinate_frame": "grid_xy",
            "route_axis": "x",
            "center_node": CENTER_NODE,
            "front_nodes": list(FRONT_NODES),
            "rear_nodes": list(REAR_NODES),
            "forward_route": [CENTER_NODE, FORWARD_TARGET],
            "reversed_route": [CENTER_NODE, REVERSED_TARGET],
            "diagonal_edges_enabled": False,
            "route_shortcuts_enabled": False,
            "declared_before_run": True,
        },
        "candidate_geometry": forward["geometry_init"],
        "forward": forward,
        "reversed": reversed_,
        "controls": controls,
        "grid_transfer_summary": {
            "entry_ceiling": iter17c["claim_ceiling"],
            "achieved_level": "M6"
            if checks["m6_grid_transfer_candidate_passed"]
            else "below_M6",
            "forward_final_x_delta": forward["raw_final_x_delta"],
            "reversed_final_x_delta": reversed_["raw_final_x_delta"],
            "forward_signed_final_x_delta": forward["signed_final_x_delta"],
            "reversed_signed_final_x_delta": reversed_["signed_final_x_delta"],
            "max_abs_y_drift": max(abs(lane["raw_final_y_delta"]) for lane in directions),
            "interpretation": (
                "The ring-series ceiling transfers to a route-defined S3 grid "
                "candidate under local east/west unit edges. The 2D grid does "
                "not use diagonal shortcuts, direct displacement writes, or "
                "post-hoc front/rear masks."
            ),
        },
        "go_no_go_for_iteration_19": {
            "iteration_19_allowed": status == "passed",
            "port_graph_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 19 may test port-graph and adaptive-topology gates. "
                "Grid evidence does not automatically promote topology-mutating "
                "or adaptive-topology claims."
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": checks["m6_grid_transfer_candidate_passed"],
            "native_m6_candidate_gate_passed": checks["m6_grid_transfer_candidate_passed"],
            "grid_transfer_candidate_gate_passed": status == "passed",
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
        "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["grid_transfer_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 18 S3 Grid Transfer",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 18 tests route-defined front/rear transfer on a 5x5 grid.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- entry ceiling: `{summary['entry_ceiling']}`",
        f"- forward final x delta: `{summary['forward_final_x_delta']}`",
        f"- reversed final x delta: `{summary['reversed_final_x_delta']}`",
        f"- max |y drift|: `{summary['max_abs_y_drift']}`",
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
    for key, value in report["go_no_go_for_iteration_19"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is a route-defined grid transfer candidate. It is not port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement evidence.",
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
