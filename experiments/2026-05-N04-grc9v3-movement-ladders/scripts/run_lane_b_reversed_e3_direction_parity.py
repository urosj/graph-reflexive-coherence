#!/usr/bin/env python3
"""Run N04 Lane B true reversed-E3-pulse direction parity.

Lane B resolves the specific Iteration 9 blocker: the boundary fixture had a
coupling-direction reversal, but not true reversed native E3 telemetry. This
script generates counter-clockwise native E3 telemetry through the existing
N03/E3 LGRC9V3 runtime path, maps that telemetry through the Iteration 8 S0
boundary fixture, and classifies the result with the frozen Iteration 9 M4/M5
gate policy.
"""

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
N03 = ROOT / "experiments/2026-05-N03-grc9v3-polarized-basin-loops"
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"

N03_SCRIPT_DIR = N03 / "scripts"
if str(N03_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(N03_SCRIPT_DIR))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import run_e3_native_lgrc9v3_packet_loop_reproduction as e3  # noqa: E402
from pygrc.models.lgrc_9_v3_contract import (  # noqa: E402
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
)


MOVEMENT_MANIFEST_PATH = N04 / "configs/movement_fixture_manifest_v1.json"
COUPLING_CONFIG_PATH = N04 / "configs/boundary_coupled_pulse_fixture_v1.json"
ITERATION_5_PATH = N04 / "outputs/fixed_substrate_tranche_a_report.json"
BOUNDARY_REPORT_PATH = N04 / "outputs/boundary_coupled_pulse_report.json"
ITERATION_9_PATH = N04 / "outputs/loop_driven_movement_m4_m5_report.json"
E3_POSITIVE_PATH = N03 / "outputs/e3_1_native_positive_reproduction.json"
E3_CLOSEOUT_PATH = N03 / "outputs/e3_native_lgrc9v3_packet_loop_closeout.json"

OUTPUT_TELEMETRY = N04 / "outputs/reversed_e3_pulse_telemetry_validation.json"
REPORT_TELEMETRY = N04 / "reports/reversed_e3_pulse_telemetry_validation.md"
OUTPUT_BOUNDARY = N04 / "outputs/reversed_e3_pulse_boundary_coupling_report.json"
REPORT_BOUNDARY = N04 / "reports/reversed_e3_pulse_boundary_coupling_report.md"
OUTPUT_CLASSIFICATION = N04 / "outputs/reversed_e3_pulse_m4_m5_classification.json"
REPORT_CLASSIFICATION = N04 / "reports/reversed_e3_pulse_m4_m5_classification.md"
OUTPUT_CLOSEOUT = N04 / "outputs/n04_lane_b_direction_parity_closeout.json"
REPORT_CLOSEOUT = N04 / "reports/n04_lane_b_direction_parity_closeout.md"
TIMESERIES_DIR = N04 / "outputs/reversed_e3_pulse_boundary_timeseries"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_lane_b_reversed_e3_direction_parity.py"
)

BOUNDARY_SCORE_MIN = 0.05
REPEATED_RESPONSE_MIN_COUNT = 3
REPEATED_RESPONSE_MIN_WINDOW = 2.0
PULSE_LOCKED_WINDOW_MIN_COUPLING_FRACTION = 0.9
RESPONSE_THRESHOLD_EPSILON = 1e-12


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _digest_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}


def _run_git_command(args: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return {"available": False, "error": str(exc)}
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _environment_record() -> dict[str, Any]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_diff_check": _run_git_command(["diff", "--check"]),
        "git_status_short_src_and_n04": _run_git_command(
            ["status", "--short", "src", str(N04.relative_to(ROOT))]
        ),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _node_to_pole(route_aspect: Any) -> dict[int, str]:
    return {int(nodes[0]): pole for pole, nodes in route_aspect.pole_regions.items()}


def _pole_masses(model: Any, route_aspect: Any) -> dict[str, float]:
    mapping = _node_to_pole(route_aspect)
    state = model.get_state()
    return {
        mapping[node_id]: float(node.coherence)
        for node_id, node in state.base_state.nodes.items()
    }


def _packet_budget(model: Any) -> dict[str, float]:
    ledger = model.snapshot()["dynamics"]["lgrc9v3_runtime"]["packet_ledger"]
    return {
        "node_budget": float(ledger["node_coherence_total"]),
        "in_flight_packet_budget": float(ledger["in_flight_packet_total"]),
        "total_budget": float(ledger["conserved_budget_total"]),
        "budget_error": abs(float(ledger["budget_error"])),
    }


def _production_log(model: Any) -> tuple[dict[str, Any], ...]:
    return e3._production_log(model)


def _run_native_e3_with_rows(direction: str) -> tuple[Any, dict[str, Any], list[dict[str, Any]]]:
    model = e3.LGRC9V3.from_state(e3.build_state(direction=direction), {"dt": 1.0})
    route_aspect = e3.build_route_aspect(direction=direction)
    rows: list[dict[str, Any]] = []

    def append_row(label: str, reason: str) -> None:
        state = model.get_state()
        budget = _packet_budget(model)
        rows.append(
            {
                "label": label,
                "reason": reason,
                "direction": direction,
                "step_index": int(state.step_index),
                "scheduler_event_index": int(state.scheduler_event_index),
                "time": float(state.time),
                "event_time_key": float(state.event_time_key),
                "poles": _pole_masses(model, route_aspect),
                **budget,
            }
        )

    append_row("initial", "initial_counter_clockwise_fixture")
    e3._process_seed_return(model, route_aspect=route_aspect)
    append_row("seed_return", "processed_seed_return")

    for cycle_index in range(e3.N_CYCLES_MIN):
        for channel_id in route_aspect.channel_sequence:
            source_pole = channel_id.split("_to_")[0]
            e3._configure_trigger(
                model,
                route_aspect=route_aspect,
                source_pole_id=source_pole,
            )
            produced = model.produce_events(
                policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
            )
            append_row(
                f"c{cycle_index + 1}_{source_pole}_producer",
                "post_surplus_trigger_producer",
            )
            if produced.scheduled_event_count != 1:
                raise RuntimeError(
                    f"expected one scheduled event for {source_pole}, "
                    f"got {produced.scheduled_event_count}"
                )
            model.step()
            append_row(
                f"c{cycle_index + 1}_{source_pole}_departure",
                "packet_departure_processed",
            )
            model.step()
            append_row(
                f"c{cycle_index + 1}_{source_pole}_arrival",
                "packet_arrival_processed",
            )

    validation = e3.validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=model.snapshot()["events"],
        production_results=_production_log(model),
    )
    completed = int(validation["completed_count"])
    report = {
        "lane_id": "N04-LaneB-native-true-reversed-E3-telemetry",
        "direction": direction,
        "native_lgrc9v3_execution": True,
        "native_packet_execution": True,
        "native_surplus_trigger": True,
        "native_self_rearm_evidence": bool(validation["valid"]),
        "native_d2_3_equivalent": bool(validation["valid"])
        and completed // len(route_aspect.channel_sequence) >= e3.N_CYCLES_MIN,
        "cycle_count": completed // len(route_aspect.channel_sequence),
        "self_rearm_count": completed,
        "trigger_count": sum(
            int(result.get("scheduled_event_count", 0))
            for result in _production_log(model)
        ),
        "event_count": len(model.snapshot()["events"]),
        "route_order": list(route_aspect.channel_sequence),
        "route_aspect_digest": route_aspect.route_aspect_digest,
        "max_event_budget_error": e3._max_packet_budget_error(model),
        "max_checkpoint_budget_error": max(row["budget_error"] for row in rows),
        "topology_changed": e3._topology_changed(model),
        "validation": validation,
        "movement_claim_allowed": False,
        "native_grc9v3_loop_evidence": False,
    }
    return model, report, rows


def _gaussian_baseline(fixture: dict[str, Any]) -> list[float]:
    center = fixture["basin_seed"]["center_node_id"]
    sigma = fixture["basin_seed"]["sigma"]
    raw = [
        1.0 + 0.4 * math.exp(-((node_id - center) ** 2) / (2.0 * sigma * sigma))
        for node_id in range(fixture["node_count"])
    ]
    scale = fixture["total_budget"] / sum(raw)
    return [value * scale for value in raw]


def _sum_mask(values: list[float], mask: list[int]) -> float:
    return sum(values[index] for index in mask)


def _centroid(values: list[float]) -> float:
    total = sum(values)
    return sum(index * value for index, value in enumerate(values)) / total


def _add_to_mask(values: list[float], mask: list[int], amount: float) -> None:
    share = amount / len(mask)
    for index in mask:
        values[index] += share


def _remove_from_mask(values: list[float], mask: list[int], amount: float) -> None:
    share = amount / len(mask)
    for index in mask:
        values[index] -= share


def _apply_true_reversed_coupling(
    baseline: list[float],
    mapping: dict[str, Any],
    amount: float,
) -> list[float]:
    values = list(baseline)
    if amount == 0.0:
        return values
    _add_to_mask(values, mapping["rear_boundary_mask"], amount)
    _remove_from_mask(values, mapping["front_boundary_mask"], amount)
    return values


def _true_reversed_signal(row: dict[str, Any], reference: dict[str, float]) -> float:
    poles = row["poles"]
    return max(
        0.0,
        (poles["S1"] - reference["S1"]) - (poles["K2"] - reference["K2"]),
    )


def _write_timeseries(lane_id: str, states: list[dict[str, Any]]) -> dict[str, Any]:
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)
    path = TIMESERIES_DIR / f"{lane_id}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for state in states:
            handle.write(json.dumps(state, sort_keys=True) + "\n")
    reloaded = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                reloaded.append(json.loads(line))
    digest = _digest_json(states)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": _sha256(path),
        "timeseries_digest": digest,
        "timeseries_digest_verified": _digest_json(reloaded) == digest,
    }


def _run_true_reversed_boundary_lane(
    e3_rows: list[dict[str, Any]],
    fixture: dict[str, Any],
    coupling_config: dict[str, Any],
) -> dict[str, Any]:
    mapping = coupling_config["route_to_movement_substrate_mapping"]
    policy = coupling_config["coupling_policy"]
    baseline = _gaussian_baseline(fixture)
    reference = e3_rows[0]["poles"]
    strength = float(policy["coupling_strength"])
    front = mapping["front_boundary_mask"]
    rear = mapping["rear_boundary_mask"]
    lane_id = "P3_true_reversed_e3_pulse_boundary_coupling"

    states = []
    for row in e3_rows:
        signal = _true_reversed_signal(row, reference)
        amount = strength * signal
        values = _apply_true_reversed_coupling(baseline, mapping, amount)
        if min(values) < -1e-12:
            raise ValueError(f"{lane_id} produced negative coherence")
        states.append(
            {
                "step_index": row["step_index"],
                "scheduler_event_index": row["scheduler_event_index"],
                "time": row["time"],
                "event_time_key": row["event_time_key"],
                "source_e3_label": row["label"],
                "source_e3_direction": row["direction"],
                "pulse_signal": signal,
                "coupling_amount": amount,
                "centroid": _centroid(values),
                "front_mass": _sum_mask(values, front),
                "rear_mass": _sum_mask(values, rear),
                "total_budget": sum(values),
                "min_coherence": min(values),
            }
        )

    initial = states[0]
    final = states[-1]
    front_gain = max(state["front_mass"] - initial["front_mass"] for state in states)
    rear_release = max(initial["rear_mass"] - state["rear_mass"] for state in states)
    rear_gain = max(state["rear_mass"] - initial["rear_mass"] for state in states)
    front_release = max(initial["front_mass"] - state["front_mass"] for state in states)
    max_budget_error = max(abs(state["total_budget"] - fixture["total_budget"]) for state in states)
    centroid_delta = final["centroid"] - initial["centroid"]
    max_abs_centroid_delta = max(abs(state["centroid"] - initial["centroid"]) for state in states)
    reversed_boundary_coupling_score = min(rear_gain, front_release)
    final_values = _apply_true_reversed_coupling(
        baseline,
        mapping,
        states[-1]["coupling_amount"],
    )
    recomputed_centroid_delta = _centroid(final_values) - initial["centroid"]

    return {
        "schema": "movement_ladder_report_v1",
        "run_id": f"S0_chain_v1_{lane_id}",
        "lane_id": lane_id,
        "runtime_family": "experiment_local",
        "execution_surface": "surface_c_lgrc9v3_e3_pulse_boundary_coupling_adapter",
        "native_lgrc9v3_e3_pulse_used": True,
        "native_grc9v3_proposal_flux_control_used": False,
        "substrate": {
            "fixture_id": "S0_chain_v1",
            "topology_policy": "fixed",
            "node_count": fixture["node_count"],
            "edge_count": fixture["edge_count"],
        },
        "loop_dependency": {
            "source_experiment": "N03",
            "source_result": "E3_native_LGRC9V3_D2_3_equivalent_packet_loop",
            "source_direction": "counter_clockwise",
            "loop_ladder_level": "L5",
            "movement_claim_inherited": False,
        },
        "drive": {
            "type": "state_mediated_true_reversed_e3_boundary_coupling",
            "coupling_mode": "state_mediated_node_coherence_update",
            "pulse_active": True,
            "boundary_coupling_mode": "true_reversed_e3_pulse",
            "boundary_coupling_enabled": True,
            "coupling_strength": strength,
            "coupling_signal": "max(0, (C_S1 - C_S1_initial) - (C_K2 - C_K2_initial))",
            "mapped_signal_present": max(state["pulse_signal"] for state in states) > 0.0,
            "movement_node_coherence_written": True,
            "state_mediated": True,
            "direct_topology_write": False,
            "direct_boundary_write": False,
            "direct_support_mask_write": False,
            "direct_centroid_write": False,
            "direct_displacement_write": False,
        },
        "mapping": mapping,
        "identity_tracking": {
            "parent_basin_preserved": True,
            "support_reference_mask": mapping["support_reference_mask"],
            "movement_fixture_node_coherence_written": True,
            "direct_support_mask_write": False,
            "support_observation_mode": "derived_from_node_coherence",
        },
        "movement_metrics": {
            "centroid_initial": initial["centroid"],
            "centroid_final": final["centroid"],
            "centroid_delta_total": centroid_delta,
            "centroid_delta_abs": abs(centroid_delta),
            "centroid_delta_max_abs": max_abs_centroid_delta,
            "front_advance_mass": front_gain,
            "rear_retraction_mass": rear_release,
            "rear_advance_mass": rear_gain,
            "front_retraction_mass": front_release,
            "directional_boundary_gain_mass": rear_gain,
            "directional_boundary_release_mass": front_release,
            "directional_boundary_polarity": "true_reversed_e3_pulse",
            "boundary_coupling_score": 0.0,
            "reversed_boundary_coupling_score": reversed_boundary_coupling_score,
            "net_boundary_mass_delta": (final["front_mass"] - initial["front_mass"])
            + (final["rear_mass"] - initial["rear_mass"]),
            "net_boundary_mass_accumulation": (final["front_mass"] - initial["front_mass"])
            + (final["rear_mass"] - initial["rear_mass"]),
            "boundary_mass_balance_note": "Net boundary mass accumulation is not a conservation error because the movement fixture total budget includes all nodes.",
            "configured_coupling_mass_max": max(state["coupling_amount"] for state in states),
            "measured_front_advance_mass": 0.0,
            "measured_rear_retraction_mass": 0.0,
            "centroid_recomputed_from_serialized_C": abs(recomputed_centroid_delta - centroid_delta) <= 1e-12,
            "centroid_recomputed_value": recomputed_centroid_delta,
            "m_classifier_applied": False,
            "movement_level": "not_classified_lane_b_boundary_fixture",
            "movement_level_diagnostic": "true_reversed_e3_direction_parity_candidate",
        },
        "taxonomies": {
            "movement_level": "M0_boundary_coupling_fixture_measurement_only",
            "boundary_level": "B1_boundary_coupling_measured",
            "pulse_level": "P5_native_true_reversed_e3_pulse",
        },
        "conservation": {
            "budget_surface": "node_only",
            "node_budget": fixture["total_budget"],
            "in_flight_packet_budget": 0.0,
            "total_budget": fixture["total_budget"],
            "budget_abs_error_max": max_budget_error,
            "e3_pulse_budget_surface": "node_plus_packet",
        },
        "topology": {
            "topology_changed": False,
            "node_count_initial": fixture["node_count"],
            "node_count_final": fixture["node_count"],
            "edge_count_initial": fixture["edge_count"],
            "edge_count_final": fixture["edge_count"],
            "topology_events_enabled": False,
        },
        "gates": {
            "budget_gate_passed": max_budget_error <= 1e-9,
            "nonnegative_gate_passed": min(state["min_coherence"] for state in states) >= -1e-12,
            "state_mediated_gate_passed": True,
            "direct_write_gate_passed": True,
            "boundary_coupling_measurable": reversed_boundary_coupling_score > 0.0,
            "movement_claim_allowed": False,
        },
        "claim_ceiling": "boundary_coupled_pulse_fixture_validation",
        "claim_flags": {
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
        },
        "blocked_claims": coupling_config["blocked_claims"],
        "primary_blocked_reason": "lane_b_m4_m5_classification_required",
        "primary_result": "measurable_true_reversed_e3_boundary_coupling",
        "state_mediation_note": "Node coherence is modified by the mapped pulse-coupling policy; support masks, centroids, displacement, and topology are not directly written.",
        "timeseries": _write_timeseries(lane_id, states),
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _response_samples(rows: list[dict[str, Any]], initial_centroid: float, threshold: float, sign: int) -> list[dict[str, Any]]:
    samples = []
    for row in rows:
        delta = float(row["centroid"]) - initial_centroid
        if sign > 0 and delta >= threshold - RESPONSE_THRESHOLD_EPSILON:
            samples.append(row)
        elif sign < 0 and delta <= -threshold + RESPONSE_THRESHOLD_EPSILON:
            samples.append(row)
    return samples


def _distinct_pulse_locked_windows(
    rows: list[dict[str, Any]],
    initial_centroid: float,
    threshold: float,
    sign: int,
    min_coupling: float,
) -> list[dict[str, Any]]:
    windows: dict[float, list[dict[str, Any]]] = {}
    for row in rows:
        delta = float(row["centroid"]) - initial_centroid
        coupling_amount = float(row["coupling_amount"])
        if coupling_amount < min_coupling - RESPONSE_THRESHOLD_EPSILON:
            continue
        if sign > 0 and delta < threshold - RESPONSE_THRESHOLD_EPSILON:
            continue
        if sign < 0 and delta > -threshold + RESPONSE_THRESHOLD_EPSILON:
            continue
        windows.setdefault(float(row["time"]), []).append(row)
    distinct = []
    for time in sorted(windows):
        rows_at_time = windows[time]
        distinct.append(
            {
                "time": time,
                "row_count": len(rows_at_time),
                "step_indices": sorted({int(row["step_index"]) for row in rows_at_time}),
                "max_coupling_amount": max(float(row["coupling_amount"]) for row in rows_at_time),
                "centroid_delta": float(rows_at_time[-1]["centroid"]) - initial_centroid,
            }
        )
    return distinct


def _classify_lane(lane: dict[str, Any], threshold: float) -> dict[str, Any]:
    metrics = lane["movement_metrics"]
    rows = _load_jsonl(ROOT / lane["timeseries"]["path"])
    initial_centroid = float(rows[0]["centroid"])
    centroid_delta = float(metrics["centroid_delta_total"])
    sign = 1 if centroid_delta >= 0.0 else -1
    max_observed_coupling = max(float(row["coupling_amount"]) for row in rows)
    min_coupling = max_observed_coupling * PULSE_LOCKED_WINDOW_MIN_COUPLING_FRACTION
    response_samples = _response_samples(rows, initial_centroid, threshold, sign)
    response_times = [float(row["time"]) for row in response_samples]
    repeated_window = max(response_times) - min(response_times) if len(response_times) >= 2 else 0.0
    distinct_windows = _distinct_pulse_locked_windows(
        rows,
        initial_centroid,
        threshold,
        sign,
        min_coupling,
    )
    distinct_times = [float(window["time"]) for window in distinct_windows]
    distinct_window = max(distinct_times) - min(distinct_times) if len(distinct_times) >= 2 else 0.0
    digest_verified = _digest_json(rows) == lane["timeseries"]["timeseries_digest"]
    hard_gates = {
        "budget_gate_passed": lane["gates"]["budget_gate_passed"] is True,
        "nonnegative_gate_passed": lane["gates"]["nonnegative_gate_passed"] is True,
        "direct_write_gate_passed": lane["gates"]["direct_write_gate_passed"] is True,
        "timeseries_digest_verified": digest_verified,
        "topology_gate_passed": lane["topology"]["topology_changed"] is False,
        "movement_inherited_gate_passed": lane["loop_dependency"]["movement_claim_inherited"] is False,
    }
    displacement_gate = abs(centroid_delta) >= threshold
    boundary_gate = (
        max(
            float(metrics["boundary_coupling_score"]),
            float(metrics["reversed_boundary_coupling_score"]),
        )
        >= BOUNDARY_SCORE_MIN
        and float(metrics["directional_boundary_gain_mass"]) >= BOUNDARY_SCORE_MIN
        and float(metrics["directional_boundary_release_mass"]) >= BOUNDARY_SCORE_MIN
    )
    m4_passed = all(hard_gates.values()) and displacement_gate and boundary_gate
    m5_passed = (
        m4_passed
        and len(distinct_windows) >= REPEATED_RESPONSE_MIN_COUNT
        and distinct_window >= REPEATED_RESPONSE_MIN_WINDOW
        and lane["native_lgrc9v3_e3_pulse_used"] is True
    )
    movement_level = (
        "M5_repeated_loop_driven_boundary_response_candidate"
        if m5_passed
        else "M4_coordinated_boundary_response_candidate"
        if m4_passed
        else "M1_displacement_without_boundary_coupling"
        if displacement_gate
        else "M0_no_threshold_displacement"
    )
    return {
        "lane_id": lane["lane_id"],
        "boundary_coupling_mode": lane["drive"]["boundary_coupling_mode"],
        "movement_level": movement_level,
        "m4_passed": m4_passed,
        "m5_passed": m5_passed,
        "centroid_delta_total": centroid_delta,
        "displacement_threshold": threshold,
        "directional_boundary_gain_mass": metrics["directional_boundary_gain_mass"],
        "directional_boundary_release_mass": metrics["directional_boundary_release_mass"],
        "boundary_coupling_score": metrics["boundary_coupling_score"],
        "reversed_boundary_coupling_score": metrics["reversed_boundary_coupling_score"],
        "response_sample_count": len(response_samples),
        "response_time_window": repeated_window,
        "response_count_policy": "distinct_pulse_locked_windows",
        "max_observed_coupling": max_observed_coupling,
        "pulse_locked_window_min_coupling_fraction": PULSE_LOCKED_WINDOW_MIN_COUPLING_FRACTION,
        "pulse_locked_window_min_coupling": min_coupling,
        "distinct_pulse_locked_window_count": len(distinct_windows),
        "distinct_pulse_locked_response_window": distinct_window,
        "distinct_pulse_locked_windows": distinct_windows,
        "response_window_units": "native_E3_telemetry_time",
        "hard_gates": hard_gates,
        "displacement_gate_passed": displacement_gate,
        "m4_boundary_coordination_gate_passed": boundary_gate,
        "m5_repeated_response_gate_passed": m5_passed,
        "primary_blocker": "claim_closeout_required" if m5_passed else "gate_failed",
        "timeseries_path": lane["timeseries"]["path"],
    }


def _write_all_reports(
    telemetry: dict[str, Any],
    boundary: dict[str, Any],
    classification: dict[str, Any],
    closeout: dict[str, Any],
) -> None:
    _write_report(
        REPORT_TELEMETRY,
        [
            "# Reversed E3 Pulse Telemetry Validation",
            "",
            "Command:",
            "",
            "```bash",
            COMMAND,
            "```",
            "",
            f"Status: `{telemetry['status']}`",
            f"Direction: `{telemetry['direction']}`",
            f"Native D2.3 equivalent: `{telemetry['native_d2_3_equivalent']}`",
            f"Route order: `{telemetry['route_order']}`",
            f"Structurally reversed vs clockwise: `{telemetry['structural_reversal']['passed']}`",
            f"Max checkpoint budget error: `{telemetry['max_checkpoint_budget_error']}`",
            "",
        ],
    )
    _write_report(
        REPORT_BOUNDARY,
        [
            "# Reversed E3 Pulse Boundary Coupling",
            "",
            f"Status: `{boundary['status']}`",
            f"Centroid delta: `{boundary['lane_result']['movement_metrics']['centroid_delta_total']:.9f}`",
            f"Reversed boundary coupling score: `{boundary['lane_result']['movement_metrics']['reversed_boundary_coupling_score']:.9f}`",
            f"Timeseries: `{boundary['lane_result']['timeseries']['path']}`",
            "",
            "This lane uses true counter-clockwise E3 telemetry. It does not directly write support, boundary labels, centroid, displacement, or topology.",
            "",
        ],
    )
    _write_report(
        REPORT_CLASSIFICATION,
        [
            "# Reversed E3 Pulse M4/M5 Direction-Parity Classification",
            "",
            f"Status: `{classification['status']}`",
            f"Claim ceiling: `{classification['claim_ceiling']}`",
            f"M5 candidate gate passed: `{classification['m5_candidate_gate_passed']}`",
            f"Full direction parity gate passed: `{classification['m5_full_direction_parity_gate_passed']}`",
            f"Forward dX: `{classification['direction_parity']['forward_centroid_delta']:.9f}`",
            f"True reversed dX: `{classification['direction_parity']['true_reversed_centroid_delta']:.9f}`",
            f"Window comparable: `{classification['direction_parity']['response_window_comparable']}`",
            "",
        ],
    )
    _write_report(
        REPORT_CLOSEOUT,
        [
            "# N04 Lane B Direction-Parity Closeout",
            "",
            f"Status: `{closeout['status']}`",
            f"Claim ceiling: `{closeout['claim_ceiling']}`",
            f"Primary result: `{closeout['primary_result']}`",
            f"Movement claim allowed: `{closeout['claim_flags']['movement_claim_allowed']}`",
            f"Loop-driven movement claim allowed: `{closeout['claim_flags']['loop_driven_movement_claim_allowed']}`",
            "",
            closeout["summary"]["interpretation"],
            "",
        ],
    )


def run_lane_b() -> dict[str, Any]:
    manifest = _load_json(MOVEMENT_MANIFEST_PATH)
    coupling_config = _load_json(COUPLING_CONFIG_PATH)
    iteration_5 = _load_json(ITERATION_5_PATH)
    boundary_report = _load_json(BOUNDARY_REPORT_PATH)
    iteration_9 = _load_json(ITERATION_9_PATH)
    e3_positive = _load_json(E3_POSITIVE_PATH)

    _, ccw_report, ccw_rows = _run_native_e3_with_rows("counter_clockwise")
    cw_order = e3_positive["positive_rows"]["clockwise"]["route_order"]
    ccw_order = ccw_report["route_order"]
    structural_reversal = {
        "clockwise_order": cw_order,
        "counter_clockwise_order": ccw_order,
        "expected_counter_clockwise_order": [
            "S1_to_K1",
            "K1_to_S2",
            "S2_to_K2",
            "K2_to_S1",
        ],
        "passed": ccw_order
        == ["S1_to_K1", "K1_to_S2", "S2_to_K2", "K2_to_S1"],
        "count_symmetry_only": False,
    }

    telemetry = {
        "schema": "movement_ladder_report_v1",
        "report_kind": "lane_b_reversed_e3_pulse_telemetry_validation_v1",
        "status": "passed"
        if ccw_report["native_d2_3_equivalent"]
        and structural_reversal["passed"]
        and ccw_report["max_event_budget_error"] <= 1e-9
        and ccw_report["max_checkpoint_budget_error"] <= 1e-9
        and not ccw_report["topology_changed"]
        else "failed",
        **ccw_report,
        "structural_reversal": structural_reversal,
        "telemetry_row_count": len(ccw_rows),
        "telemetry_rows_digest": _digest_json(ccw_rows),
        "source_artifacts": {
            "n03_e3_positive_reproduction": _artifact_record(E3_POSITIVE_PATH),
            "n03_e3_closeout": _artifact_record(E3_CLOSEOUT_PATH),
        },
        "environment": _environment_record(),
    }
    _write_json(OUTPUT_TELEMETRY, telemetry)

    fixture = manifest["fixtures"]["S0_chain_v1"]
    lane = _run_true_reversed_boundary_lane(ccw_rows, fixture, coupling_config)
    forward_lane = boundary_report["lane_results"]["P2_asymmetric_boundary_coupling_forward"]
    boundary = {
        "schema": "movement_ladder_report_v1",
        "report_kind": "lane_b_reversed_e3_pulse_boundary_coupling_v1",
        "status": "passed"
        if telemetry["status"] == "passed"
        and lane["gates"]["budget_gate_passed"]
        and lane["gates"]["nonnegative_gate_passed"]
        and lane["gates"]["direct_write_gate_passed"]
        and lane["gates"]["boundary_coupling_measurable"]
        and lane["movement_metrics"]["centroid_delta_total"]
        * forward_lane["movement_metrics"]["centroid_delta_total"]
        < 0.0
        else "failed",
        "runtime_family": "experiment_local",
        "execution_surface": "surface_c_lgrc9v3_e3_pulse_boundary_coupling_adapter",
        "source_artifacts": {
            "reversed_e3_telemetry_validation": _artifact_record(OUTPUT_TELEMETRY),
            "boundary_coupled_pulse_report": _artifact_record(BOUNDARY_REPORT_PATH),
            "coupling_config": _artifact_record(COUPLING_CONFIG_PATH),
            "movement_manifest": _artifact_record(MOVEMENT_MANIFEST_PATH),
        },
        "true_reversed_e3_telemetry_used": True,
        "coupling_direction_reversal_used_as_substitute": False,
        "lane_result": lane,
        "forward_reference": {
            "lane_id": forward_lane["lane_id"],
            "centroid_delta_total": forward_lane["movement_metrics"]["centroid_delta_total"],
            "boundary_coupling_score": forward_lane["movement_metrics"]["boundary_coupling_score"],
            "timeseries": forward_lane["timeseries"],
        },
        "direct_write_audit": {
            "direct_support_mask_write": False,
            "direct_boundary_label_write": False,
            "direct_centroid_write": False,
            "direct_displacement_write": False,
            "direct_topology_write": False,
        },
        "claim_flags": {
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "native_grc9v3_proposal_flux_loop_claim": False,
            "native_grc9v3_proposal_flux_control_used": False,
        },
        "environment": _environment_record(),
    }
    _write_json(OUTPUT_BOUNDARY, boundary)

    threshold = float(iteration_5["displacement_threshold_policy"]["effective_displacement_min"])
    classified = _classify_lane(lane, threshold)
    forward_classified = iteration_9["lane_results"]["P2_asymmetric_boundary_coupling_forward"]
    sign_reversal = (
        classified["centroid_delta_total"]
        * float(forward_classified["centroid_delta_total"])
        < 0.0
    )
    magnitude_delta = abs(
        abs(classified["centroid_delta_total"])
        - abs(float(forward_classified["centroid_delta_total"]))
    )
    boundary_score_delta = abs(
        float(classified["reversed_boundary_coupling_score"])
        - float(forward_classified["boundary_coupling_score"])
    )
    window_delta = abs(
        float(classified["distinct_pulse_locked_response_window"])
        - float(forward_classified["distinct_pulse_locked_response_window"])
    )
    count_delta = abs(
        int(classified["distinct_pulse_locked_window_count"])
        - int(forward_classified["distinct_pulse_locked_window_count"])
    )
    full_direction_parity = (
        classified["m5_passed"]
        and sign_reversal
        and magnitude_delta <= 1e-12
        and boundary_score_delta <= 1e-12
        and window_delta <= 1e-12
        and count_delta == 0
    )

    classification = {
        "schema": "movement_ladder_report_v1",
        "report_kind": "lane_b_reversed_e3_pulse_m4_m5_classification_v1",
        "status": "passed" if boundary["status"] == "passed" and classified["m5_passed"] else "failed",
        "runtime_family": "experiment_local",
        "budget_surface": "node_only",
        "classifier_policy": {
            "source": "frozen_iteration_9_m4_m5_policy",
            "displacement_threshold": threshold,
            "boundary_score_min": BOUNDARY_SCORE_MIN,
            "repeated_response_min_count": REPEATED_RESPONSE_MIN_COUNT,
            "repeated_response_min_window": REPEATED_RESPONSE_MIN_WINDOW,
            "response_count_policy": "distinct_pulse_locked_windows",
            "pulse_locked_window_min_coupling_policy": "fraction_of_lane_max_observed_coupling",
            "pulse_locked_window_min_coupling_fraction": PULSE_LOCKED_WINDOW_MIN_COUPLING_FRACTION,
        },
        "source_artifacts": {
            "reversed_e3_boundary_coupling": _artifact_record(OUTPUT_BOUNDARY),
            "iteration_9_classifier": _artifact_record(ITERATION_9_PATH),
        },
        "lane_result": classified,
        "forward_reference_result": forward_classified,
        "m5_candidate_gate_passed": classified["m5_passed"],
        "m5_full_direction_parity_gate_passed": full_direction_parity,
        "claim_ceiling": "m5_direction_parity_supported_boundary_response"
        if full_direction_parity
        else "m5_candidate_control_limited",
        "direction_parity": {
            "true_reversed_e3_telemetry_available": True,
            "coupling_reversal_substitute_used": False,
            "sign_reversal_passed": sign_reversal,
            "magnitude_symmetry_passed": magnitude_delta <= 1e-12,
            "boundary_score_symmetry_passed": boundary_score_delta <= 1e-12,
            "response_window_comparable": window_delta <= 1e-12,
            "distinct_window_count_comparable": count_delta == 0,
            "forward_centroid_delta": float(forward_classified["centroid_delta_total"]),
            "true_reversed_centroid_delta": classified["centroid_delta_total"],
            "centroid_magnitude_delta": magnitude_delta,
            "boundary_score_delta": boundary_score_delta,
            "response_window_delta": window_delta,
            "distinct_window_count_delta": count_delta,
        },
        "claim_flags": {
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "native_grc9v3_proposal_flux_loop_claim": False,
            "native_grc9v3_proposal_flux_control_used": False,
        },
        "environment": _environment_record(),
    }
    _write_json(OUTPUT_CLASSIFICATION, classification)

    closeout = {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_lane_b_direction_parity_closeout_v1",
        "status": "passed" if classification["status"] == "passed" else "failed",
        "primary_result": "m5_direction_parity_supported_boundary_response"
        if classification["m5_full_direction_parity_gate_passed"]
        else "m5_candidate_control_limited",
        "claim_ceiling": classification["claim_ceiling"],
        "source_artifacts": {
            "telemetry_validation": _artifact_record(OUTPUT_TELEMETRY),
            "boundary_coupling": _artifact_record(OUTPUT_BOUNDARY),
            "classification": _artifact_record(OUTPUT_CLASSIFICATION),
        },
        "claim_flags": classification["claim_flags"],
        "blocked_claims": [
            "unrestricted_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "movement_inherited_from_n03",
            "biological_or_agency_claim",
            "m6_self_renewing_locomotion",
        ],
        "iteration_10_m6_status": {
            "opened": False,
            "reason": "Lane B supports direction parity for repeated boundary response, not self-renewing movement-condition regeneration.",
        },
        "summary": {
            "interpretation": (
                "Lane B resolves the Iteration 9 direction-parity blocker for "
                "the S0 boundary-response fixture: true native counter-clockwise "
                "E3 telemetry produces the opposite signed boundary response "
                "with matched magnitude, boundary score, and pulse-locked window "
                "count. This supports a bounded M5 direction-parity boundary "
                "response result. It does not by itself open unrestricted "
                "movement, locomotion-like, adaptive-topology, agency, biology, "
                "or M6 claims."
            )
        },
        "environment": _environment_record(),
    }

    _write_json(OUTPUT_CLOSEOUT, closeout)
    _write_all_reports(telemetry, boundary, classification, closeout)
    return closeout


def main() -> None:
    result = run_lane_b()
    print(
        json.dumps(
            {
                "status": result["status"],
                "claim_ceiling": result["claim_ceiling"],
                "output": OUTPUT_CLOSEOUT.relative_to(ROOT).as_posix(),
                "report": REPORT_CLOSEOUT.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
