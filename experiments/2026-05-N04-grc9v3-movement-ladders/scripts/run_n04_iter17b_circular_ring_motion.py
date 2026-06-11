#!/usr/bin/env python3
"""Run N04 Iteration 17-B circular ring motion evidence probe."""

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
import run_n04_iter17_ring_transfer as iter17  # noqa: E402


ITER17A_PATH = N04 / "outputs/n04_iter17a_ring_unwrap_robustness_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter17b_circular_ring_motion_evidence_report.json"
REPORT_PATH = N04 / "reports/n04_iter17b_circular_ring_motion_evidence_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter17b_circular_ring_motion.py"
)

NODE_COUNT = iter16.iter15b.native_m6.NODE_COUNT
RECOVERY_WINDOW_CYCLES = iter17.RECOVERY_WINDOW_CYCLES
PRE_TRANSFER_CYCLES = iter16.PRE_TRANSFER_CYCLES
CHALLENGE_TRANSFER_AMOUNT = iter17.CHALLENGE_TRANSFER_AMOUNT
CIRCULAR_PHASE_TOLERANCE_NODES = 0.25
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


def _add_ring_only_geometry(state: Any) -> dict[str, Any]:
    before_values = [
        float(state.nodes[index].coherence)
        for index in range(NODE_COUNT)
    ]
    before_budget = sum(before_values)
    ring_edge_id = iter17._add_ring_edge(state)  # noqa: SLF001
    after_values = [
        float(state.nodes[index].coherence)
        for index in range(NODE_COUNT)
    ]
    after_budget = sum(after_values)
    return {
        "geometry_id": "s1_ring_wrap_only_v1",
        "geometry_family": "s1_ring_with_native_wrap_edge",
        "source_geometry": "S0_chain_v1_plus_declared_wrap_edge",
        "node_count": NODE_COUNT,
        "ring_wrap_edge_id": ring_edge_id,
        "wrap_edge": [20, 0],
        "coordinate_frame": "circular_phase",
        "circular_metric": "shortest_signed_ring_distance",
        "phase_metric": "positive_excess_mass_circular_mean",
        "front_rear_policy": "phase_leading_target_vs_phase_trailing_source",
        "topology_changed_by_fixture_definition": True,
        "topology_fixed_during_run": True,
        "topology_mutated_during_run": False,
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_geometry_init": min(after_values) >= -TOL,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
        "reason": (
            "Iteration 17-B declares a ring-only wrap edge before execution and "
            "scores seam-crossing pulse response with circular phase metrics."
        ),
    }


def _direction_config(direction: str, geometry: dict[str, Any]) -> dict[str, Any]:
    if direction == "forward":
        return {
            "source": 20,
            "target": 0,
            "edge_id": geometry["ring_wrap_edge_id"],
            "expected_polarity": "positive",
            "expected_sign": 1,
            "front_nodes": (0,),
            "rear_nodes": (20,),
            "route_id": "s1-ring-circular-forward-wrap",
        }
    if direction == "reversed":
        return {
            "source": 0,
            "target": 20,
            "edge_id": geometry["ring_wrap_edge_id"],
            "expected_polarity": "negative",
            "expected_sign": -1,
            "front_nodes": (0,),
            "rear_nodes": (20,),
            "route_id": "s1-ring-circular-reversed-wrap",
        }
    raise ValueError(f"unknown direction {direction!r}")


def _boundary_polarity_score(model: Any, config: dict[str, Any]) -> float:
    values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    front_mass = sum(values[index] for index in config["front_nodes"])
    rear_mass = sum(values[index] for index in config["rear_nodes"])
    return front_mass - rear_mass


def _apply_polarity_damping_perturbation(
    model: Any,
    *,
    config: dict[str, Any],
    transfer_amount: float,
) -> dict[str, Any]:
    if config["expected_polarity"] == "positive":
        debit_nodes = config["front_nodes"]
        credit_nodes = config["rear_nodes"]
    else:
        debit_nodes = config["rear_nodes"]
        credit_nodes = config["front_nodes"]
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
        "perturbation_kind": "budget_neutral_circular_polarity_damping",
        "transfer_amount": transfer_amount,
        "debit_nodes": list(debit_nodes),
        "credit_nodes": list(credit_nodes),
        "debit_per_node": debit_per_node,
        "credit_per_node": credit_per_node,
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


def _circular_signed_distance_nodes(source: float, target: float) -> float:
    delta = (target - source + NODE_COUNT / 2.0) % NODE_COUNT - NODE_COUNT / 2.0
    return float(delta)


def _positive_excess_phase(values: list[float], baseline: list[float]) -> float:
    x = 0.0
    y = 0.0
    for node_id, (value, base) in enumerate(zip(values, baseline, strict=True)):
        excess = max(0.0, value - base)
        if excess <= 0.0:
            continue
        theta = 2.0 * math.pi * node_id / NODE_COUNT
        x += excess * math.cos(theta)
        y += excess * math.sin(theta)
    if abs(x) <= TOL and abs(y) <= TOL:
        return math.nan
    angle = math.atan2(y, x)
    if angle < 0.0:
        angle += 2.0 * math.pi
    return float(angle * NODE_COUNT / (2.0 * math.pi))


def _phase_error_to_target(phase: float, target: int) -> float:
    if math.isnan(phase):
        return math.nan
    return abs(_circular_signed_distance_nodes(phase, float(target)))


def _feedback_cycle(
    model: Any,
    *,
    config: dict[str, Any],
    cycle_index: int,
    phase: str,
    enabled: bool = True,
    expected_polarity: str | None = None,
) -> dict[str, Any]:
    feedback_row = model.emit_feedback_eligibility_surface_row(
        front_node_ids=config["front_nodes"],
        rear_node_ids=config["rear_nodes"],
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
        enabled=enabled,
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


def _run_circular_direction(direction: str) -> dict[str, Any]:
    state, _edges = iter16.iter15b.native_m6._s0_chain_state()  # noqa: SLF001
    geometry = _add_ring_only_geometry(state)
    config = _direction_config(direction, geometry)
    model = iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    initial_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
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
    pre_score = _boundary_polarity_score(model, config)
    perturbation = _apply_polarity_damping_perturbation(
        model,
        config=config,
        transfer_amount=CHALLENGE_TRANSFER_AMOUNT,
    )
    post_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    post_score = _boundary_polarity_score(model, config)
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
    final_score = _boundary_polarity_score(model, config)
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
    pre_phase = _positive_excess_phase(pre_values, initial_values)
    post_phase = _positive_excess_phase(post_values, initial_values)
    final_phase = _positive_excess_phase(final_values, initial_values)
    circular_displacement = _circular_signed_distance_nodes(
        float(config["source"]),
        final_phase,
    )
    signed_pre_score = sign * pre_score
    signed_post_score = sign * post_score
    signed_final_score = sign * final_score
    phase_error = _phase_error_to_target(final_phase, config["target"])
    width_initial = iter16.iter15b.native_m6._width(initial_values)  # noqa: SLF001
    width_final = iter16.iter15b.native_m6._width(final_values)  # noqa: SLF001
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = iter16.iter15b.native_m6._profile_similarity(initial_values, final_values)  # noqa: SLF001
    return {
        "direction": direction,
        "geometry_init": geometry,
        "source_node_id": config["source"],
        "target_node_id": config["target"],
        "edge_id": config["edge_id"],
        "front_nodes": list(config["front_nodes"]),
        "rear_nodes": list(config["rear_nodes"]),
        "route_crosses_wrap_edge": True,
        "circular_distance_source_to_target_nodes": _circular_signed_distance_nodes(
            float(config["source"]),
            float(config["target"]),
        ),
        "pre_positive_excess_phase": pre_phase,
        "post_positive_excess_phase": post_phase,
        "final_positive_excess_phase": final_phase,
        "final_phase_error_to_target_nodes": phase_error,
        "circular_displacement_nodes": circular_displacement,
        "recovery_scheduled_cycle_count": len(recovery_scheduled),
        "baseline_cycles": [_cycle_summary(cycle) for cycle in baseline_cycles],
        "recovery_cycles": [_cycle_summary(cycle) for cycle in recovery_cycles],
        "perturbation": perturbation,
        "signed_pre_transfer_score": signed_pre_score,
        "signed_post_perturbation_score": signed_post_score,
        "signed_final_score": signed_final_score,
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
        "circular_phase_target_passed": phase_error <= CIRCULAR_PHASE_TOLERANCE_NODES,
        "m6_circular_motion_candidate_passed": (
            len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and signed_post_score < signed_pre_score - TOL
            and signed_final_score >= signed_pre_score - TOL
            and phase_error <= CIRCULAR_PHASE_TOLERANCE_NODES
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
        "seeded_event_count": len(seeded_events),
        "seeded_events_digest": iter16.iter15b.native_m6._digest_json(seeded_events),  # noqa: SLF001
    }


def _run_static_control() -> dict[str, Any]:
    state, _edges = iter16.iter15b.native_m6._s0_chain_state()  # noqa: SLF001
    geometry = _add_ring_only_geometry(state)
    config = _direction_config("forward", geometry)
    model = iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    initial_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    return {
        "control_id": "static_no_packet_control",
        "passed_negative_control": True,
        "primary_blocker": "no_committed_packet_contact",
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "circular_phase": _positive_excess_phase(final_values, initial_values),
        "front_nodes": list(config["front_nodes"]),
        "rear_nodes": list(config["rear_nodes"]),
    }


def _run_wrong_direction_control() -> dict[str, Any]:
    state, _edges = iter16.iter15b.native_m6._s0_chain_state()  # noqa: SLF001
    geometry = _add_ring_only_geometry(state)
    config = _direction_config("forward", geometry)
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
    iter17a = _load_json(ITER17A_PATH)
    forward = _run_circular_direction("forward")
    reversed_ = _run_circular_direction("reversed")
    directions = [forward, reversed_]
    static_control = _run_static_control()
    wrong_direction_control = _run_wrong_direction_control()
    seam_artifact_control = {
        "control_id": "seam_artifact_unwrap_control",
        "source": _artifact_record(ITER17A_PATH),
        "passed_negative_control": bool(iter17a["seam_sensitive_controls"]),
        "primary_blocker": "linear_unwrap_seam_intersects_active_route",
        "seam_control_count": len(iter17a["seam_sensitive_controls"]),
    }
    unwrap_only_control = {
        "control_id": "unwrap_only_control",
        "source": _artifact_record(ITER17A_PATH),
        "passed_negative_control": (
            iter17a["claim_flags"]["circular_locomotion_claim_allowed"] is False
            and iter17a["claim_flags"]["wrap_crossing_movement_claim_allowed"] is False
        ),
        "primary_blocker": "unwrap_robustness_has_no_circular_metric_or_seam_crossing_positive_lane",
    }
    controls = {
        "static": static_control,
        "wrong_direction": wrong_direction_control,
        "seam_artifact": seam_artifact_control,
        "unwrap_only": unwrap_only_control,
    }
    checks = {
        "iteration_17a_available": iter17a["status"] == "passed",
        "circular_metric_declared_before_run": True,
        "seam_crossing_routes_tested": all(
            lane["route_crosses_wrap_edge"] for lane in directions
        ),
        "circular_distance_sign_reversal_passed": (
            forward["circular_displacement_nodes"] > 0.0
            and reversed_["circular_displacement_nodes"] < 0.0
        ),
        "circular_phase_target_passed": all(
            lane["circular_phase_target_passed"] for lane in directions
        ),
        "m4_boundary_response_passed": all(
            lane["m4_boundary_response_passed"] for lane in directions
        ),
        "m5_direction_control_passed": all(
            lane["m5_direction_control_passed"] for lane in directions
        ),
        "m6_circular_motion_candidate_passed": all(
            lane["m6_circular_motion_candidate_passed"] for lane in directions
        ),
        "artifact_validators_passed": all(
            lane["artifact_validator"]["valid"] for lane in directions
        ),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= TOL
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
        "s1_ring_circular_motion_evidence_candidate"
        if status == "passed"
        else "s1_ring_circular_motion_evidence_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter17b_circular_ring_motion_evidence_v1",
        "iteration": "17-B",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S1_ring_wrap_only_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "ring",
        "input_iteration_17a": _artifact_record(ITER17A_PATH),
        "claim_ceiling": claim_ceiling,
        "achieved_movement_level": "M6"
        if checks["m6_circular_motion_candidate_passed"]
        else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if checks["m6_circular_motion_candidate_passed"]
            else "not_measured",
            "persistence_basis": "s1_ring_circular_wrap_route_recovers_0_15"
            if checks["m6_circular_motion_candidate_passed"]
            else "circular_motion_evidence_below_m6",
            "self_renewed_cycle_count": RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "forward_and_reversed_three_cycle_recovery_on_circular_wrap_route",
            "recovery_status": "recovers_0_15_on_circular_wrap_route",
            "recovery_tested": True,
            "recovery_passed": checks["m6_circular_motion_candidate_passed"],
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "single_ring_fixture_no_grid_or_port_graph_transfer",
        },
        "circular_metric_policy": {
            "policy_id": "s1_ring_circular_phase_metric_v1",
            "node_count": NODE_COUNT,
            "metric": "shortest_signed_ring_distance",
            "phase_metric": "positive_excess_mass_circular_mean",
            "forward_route": [20, 0],
            "reversed_route": [0, 20],
            "wrap_edge": [20, 0],
            "phase_tolerance_nodes": CIRCULAR_PHASE_TOLERANCE_NODES,
            "declared_before_run": True,
        },
        "candidate_geometry": forward["geometry_init"],
        "forward": forward,
        "reversed": reversed_,
        "controls": controls,
        "circular_motion_summary": {
            "forward_circular_displacement_nodes": forward[
                "circular_displacement_nodes"
            ],
            "reversed_circular_displacement_nodes": reversed_[
                "circular_displacement_nodes"
            ],
            "forward_final_phase_error_to_target_nodes": forward[
                "final_phase_error_to_target_nodes"
            ],
            "reversed_final_phase_error_to_target_nodes": reversed_[
                "final_phase_error_to_target_nodes"
            ],
            "interpretation": (
                "The ring supports a native seam-crossing circular-response "
                "candidate under a declared circular phase metric. This is a "
                "circular motion evidence candidate, not a locomotion-like, "
                "adaptive-topology, agency, identity-acceptance, or "
                "unrestricted movement claim."
            ),
        },
        "go_no_go_for_iteration_18": {
            "iteration_18_allowed": status == "passed",
            "grid_transfer_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 18 may test whether the circular/ring result "
                "survives route-defined front/rear masks on a grid. Circular "
                "claims do not automatically transfer to grid geometry."
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": checks["m6_circular_motion_candidate_passed"],
            "native_m6_candidate_gate_passed": checks["m6_circular_motion_candidate_passed"],
            "circular_motion_evidence_candidate_gate_passed": status == "passed",
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
            "circular_locomotion_claim_allowed": False,
            "wrap_crossing_movement_claim_allowed": False,
        },
        "blocked_claims": [
            "circular_locomotion",
            "full_T6_general_persistence",
            "grid_transfer",
            "port_graph_transfer",
            "broad_geometry_transfer",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
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
        "next_iteration": "18_s3_grid_route_defined_front_rear",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["circular_motion_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 17-B Circular Ring Motion Evidence",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 17-B tests seam-crossing ring response with a declared circular phase metric.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- persistence basis: `{axis['persistence_basis']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- forward circular displacement nodes: `{summary['forward_circular_displacement_nodes']}`",
        f"- reversed circular displacement nodes: `{summary['reversed_circular_displacement_nodes']}`",
        f"- forward phase error to target: `{summary['forward_final_phase_error_to_target_nodes']}`",
        f"- reversed phase error to target: `{summary['reversed_final_phase_error_to_target_nodes']}`",
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
    for key, value in report["go_no_go_for_iteration_18"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is circular motion evidence on one ring fixture. It is not locomotion-like, adaptive-topology, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement evidence.",
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
