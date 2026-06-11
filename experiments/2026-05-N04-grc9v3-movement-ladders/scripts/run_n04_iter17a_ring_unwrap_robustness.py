#!/usr/bin/env python3
"""Run N04 Iteration 17-A ring unwrap-robustness probe."""

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


ITER17_PATH = N04 / "outputs/n04_iter17_ring_transfer_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter17a_ring_unwrap_robustness_report.json"
REPORT_PATH = N04 / "reports/n04_iter17a_ring_unwrap_robustness_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter17a_ring_unwrap_robustness.py"
)

NODE_COUNT = iter16.iter15b.native_m6.NODE_COUNT
RECOVERY_WINDOW_CYCLES = iter17.RECOVERY_WINDOW_CYCLES
CHALLENGE_TRANSFER_AMOUNT = iter17.CHALLENGE_TRANSFER_AMOUNT
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


def _edge_key(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u <= v else (v, u)


ACTIVE_ROUTE_EDGES = {
    _edge_key(10, 11),
    _edge_key(11, 12),
    _edge_key(12, 13),
    _edge_key(13, 14),
    _edge_key(10, 9),
    _edge_key(9, 8),
    _edge_key(8, 7),
    _edge_key(7, 6),
}


def _unwrap_seam(origin: int) -> list[int]:
    return [(origin - 1) % NODE_COUNT, origin]


def _seam_crosses_active_route(origin: int) -> bool:
    seam = _unwrap_seam(origin)
    return _edge_key(seam[0], seam[1]) in ACTIVE_ROUTE_EDGES


def _unwrapped_coordinates(origin: int) -> list[float]:
    return [float((node - origin) % NODE_COUNT) for node in range(NODE_COUNT)]


def _unwrapped_centroid(values: list[float], *, origin: int) -> float:
    coords = _unwrapped_coordinates(origin)
    total = sum(values)
    if total <= 0:
        return math.nan
    return sum(value * coord for value, coord in zip(values, coords, strict=True)) / total


def _direction_config(direction: str, geometry: dict[str, Any]) -> dict[str, Any]:
    return iter17._direction_config(direction, geometry)  # noqa: SLF001


def _run_direction_for_origin(direction: str, *, origin: int) -> dict[str, Any]:
    state, _edges = iter16.iter15b.native_m6._s0_chain_state()  # noqa: SLF001
    geometry = iter17._apply_ring_geometry(state)  # noqa: SLF001
    seam = _unwrap_seam(origin)
    geometry |= {
        "unwrap_policy_id": f"s1_ring_unwrap_policy_origin_{origin}_v1",
        "coordinate_frame": "ring_unwrapped_linear",
        "unwrap_origin_node": origin,
        "unwrap_seam": seam,
        "route_crosses_unwrap_seam": _seam_crosses_active_route(origin),
    }
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
        iter16.iter15b._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            edge_id=config["edge_id"],
            cycle_index=cycle_index,
            phase="pre_perturbation_baseline",
        )
        for cycle_index in range(iter16.PRE_TRANSFER_CYCLES)
    ]
    pre_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    pre_score = iter16.iter15b._boundary_polarity_score(model)  # noqa: SLF001
    perturbation = iter16.iter15b._apply_polarity_damping_perturbation(  # noqa: SLF001
        model,
        direction=direction,
        transfer_amount=CHALLENGE_TRANSFER_AMOUNT,
    )
    post_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    post_score = iter16.iter15b._boundary_polarity_score(model)  # noqa: SLF001
    recovery_cycles = [
        iter16.iter15b._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            edge_id=config["edge_id"],
            cycle_index=cycle_index,
            phase="post_perturbation_recovery",
        )
        for cycle_index in range(RECOVERY_WINDOW_CYCLES)
    ]
    final_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_budget = iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    final_score = iter16.iter15b._boundary_polarity_score(model)  # noqa: SLF001
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
    initial_centroid = _unwrapped_centroid(initial_values, origin=origin)
    raw_pre_centroid = _unwrapped_centroid(pre_values, origin=origin) - initial_centroid
    raw_post_centroid = _unwrapped_centroid(post_values, origin=origin) - initial_centroid
    raw_final_centroid = _unwrapped_centroid(final_values, origin=origin) - initial_centroid
    signed_pre_score = sign * pre_score
    signed_post_score = sign * post_score
    signed_final_score = sign * final_score
    signed_pre_centroid = sign * raw_pre_centroid
    signed_post_centroid = sign * raw_post_centroid
    signed_final_centroid = sign * raw_final_centroid
    width_initial = iter16.iter15b.native_m6._width(initial_values)  # noqa: SLF001
    width_final = iter16.iter15b.native_m6._width(final_values)  # noqa: SLF001
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = iter16.iter15b.native_m6._profile_similarity(initial_values, final_values)  # noqa: SLF001
    return {
        "direction": direction,
        "unwrap_origin_node": origin,
        "unwrap_seam": seam,
        "route_crosses_unwrap_seam": geometry["route_crosses_unwrap_seam"],
        "source_node_id": config["source"],
        "target_node_id": config["target"],
        "edge_id": config["edge_id"],
        "recovery_scheduled_cycle_count": len(recovery_scheduled),
        "perturbation": perturbation,
        "signed_pre_transfer_score": signed_pre_score,
        "signed_post_perturbation_score": signed_post_score,
        "signed_final_score": signed_final_score,
        "signed_pre_transfer_centroid_delta": signed_pre_centroid,
        "signed_post_perturbation_centroid_delta": signed_post_centroid,
        "signed_final_centroid_delta": signed_final_centroid,
        "raw_pre_transfer_centroid_delta": raw_pre_centroid,
        "raw_post_perturbation_centroid_delta": raw_post_centroid,
        "raw_final_centroid_delta": raw_final_centroid,
        "centroid_coordinate_frame": "ring_unwrapped_linear",
        "centroid_delta_frame": "direction_normalized_recovery_delta",
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
        "m6_transfer_candidate_passed": (
            len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and signed_post_score < signed_pre_score - TOL
            and signed_final_score >= signed_pre_score - TOL
            and signed_post_centroid < signed_pre_centroid - TOL
            and signed_final_centroid >= signed_pre_centroid - TOL
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
        "seeded_event_count": len(seeded_events),
        "seeded_events_digest": iter16.iter15b.native_m6._digest_json(seeded_events),  # noqa: SLF001
    }


def _achieved_level(forward: dict[str, Any], reversed_: dict[str, Any]) -> str:
    lanes = [forward, reversed_]
    if all(lane["m6_transfer_candidate_passed"] for lane in lanes):
        return "M6"
    if all(lane["m5_direction_control_passed"] for lane in lanes):
        return "M5"
    if all(lane["m4_boundary_response_passed"] for lane in lanes):
        return "M4"
    return "below_M4"


def _origin_result(origin: int) -> dict[str, Any]:
    forward = _run_direction_for_origin("forward", origin=origin)
    reversed_ = _run_direction_for_origin("reversed", origin=origin)
    achieved_level = _achieved_level(forward, reversed_)
    return {
        "unwrap_origin_node": origin,
        "unwrap_seam": _unwrap_seam(origin),
        "route_crosses_unwrap_seam": _seam_crosses_active_route(origin),
        "accepted_for_robustness": not _seam_crosses_active_route(origin),
        "achieved_movement_level": achieved_level,
        "forward": forward,
        "reversed": reversed_,
        "direction_parity_passed": (
            forward["signed_final_centroid_delta"] > 0
            and reversed_["signed_final_centroid_delta"] > 0
            and forward["raw_final_centroid_delta"] > 0
            and reversed_["raw_final_centroid_delta"] < 0
        ),
        "artifact_validators_passed": all(
            lane["artifact_validator"]["valid"] for lane in [forward, reversed_]
        ),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= TOL and lane["nonnegative_gate_passed"]
            for lane in [forward, reversed_]
        ),
        "identity_shape_gates_passed": all(
            lane["identity_shape_gates_passed"] for lane in [forward, reversed_]
        ),
        "feedback_authorized_not_schedule_copied": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in [forward, reversed_]
        ),
    }


def build_report() -> dict[str, Any]:
    iter17_report = _load_json(ITER17_PATH)
    accepted_origins = [
        origin for origin in range(NODE_COUNT) if not _seam_crosses_active_route(origin)
    ]
    seam_control_origins = [
        origin for origin in range(NODE_COUNT) if _seam_crosses_active_route(origin)
    ]
    origin_results = [_origin_result(origin) for origin in accepted_origins]
    seam_controls = [
        {
            "unwrap_origin_node": origin,
            "unwrap_seam": _unwrap_seam(origin),
            "route_crosses_unwrap_seam": True,
            "accepted_for_robustness": False,
            "primary_blocker": "unwrap_seam_intersects_active_route",
        }
        for origin in seam_control_origins
    ]
    signed_forward = [row["forward"]["signed_final_centroid_delta"] for row in origin_results]
    signed_reversed = [row["reversed"]["signed_final_centroid_delta"] for row in origin_results]
    forward_spread = max(signed_forward) - min(signed_forward)
    reversed_spread = max(signed_reversed) - min(signed_reversed)
    checks = {
        "iteration_17_available": iter17_report["status"] == "passed",
        "multiple_unwrap_origins_declared": len(accepted_origins) >= 3,
        "accepted_unwraps_keep_route_off_seam": all(
            not row["route_crosses_unwrap_seam"] for row in origin_results
        ),
        "seam_intersecting_controls_recorded": len(seam_controls) == len(seam_control_origins)
        and len(seam_controls) > 0,
        "candidate_gates_recomputed_per_origin": all(
            row["forward"]["surface_log_digest"] != ""
            and row["reversed"]["surface_log_digest"] != ""
            for row in origin_results
        ),
        "all_accepted_origins_reach_m6": all(
            row["achieved_movement_level"] == "M6" for row in origin_results
        ),
        "direction_parity_passed_all_accepted_origins": all(
            row["direction_parity_passed"] for row in origin_results
        ),
        "artifact_validators_passed": all(
            row["artifact_validators_passed"] for row in origin_results
        ),
        "budget_and_nonnegative_gates_passed": all(
            row["budget_and_nonnegative_gates_passed"] for row in origin_results
        ),
        "identity_shape_gates_passed": all(
            row["identity_shape_gates_passed"] for row in origin_results
        ),
        "feedback_authorized_not_schedule_copied": all(
            row["feedback_authorized_not_schedule_copied"] for row in origin_results
        ),
        "signed_centroid_magnitude_stable": forward_spread <= TOL
        and reversed_spread <= TOL,
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s1_ring_unwrap_robust_transfer_candidate"
        if status == "passed"
        else "s1_ring_unwrap_robustness_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter17a_ring_unwrap_robustness_v1",
        "iteration": "17-A",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S1_ring_absorber_corridor_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "ring",
        "input_iteration_17": _artifact_record(ITER17_PATH),
        "claim_ceiling": claim_ceiling,
        "achieved_movement_level": "M6"
        if checks["all_accepted_origins_reach_m6"]
        else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if checks["all_accepted_origins_reach_m6"]
            else "not_measured",
            "persistence_basis": "s1_ring_multiple_unwraps_recover_0_15"
            if checks["all_accepted_origins_reach_m6"]
            else "unwrap_robustness_below_m6",
            "self_renewed_cycle_count": RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "forward_and_reversed_three_cycle_recovery_across_equivalent_unwraps",
            "recovery_status": "recovers_0_15_across_equivalent_unwraps",
            "recovery_tested": True,
            "recovery_passed": checks["all_accepted_origins_reach_m6"],
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "unwrap_robustness_only_no_circular_metric_or_grid_transfer",
        },
        "unwrap_robustness_policy": {
            "origin_set": list(range(NODE_COUNT)),
            "accepted_origins": accepted_origins,
            "seam_control_origins": seam_control_origins,
            "active_route_edges": [list(edge) for edge in sorted(ACTIVE_ROUTE_EDGES)],
            "accepted_origin_rule": "unwrap seam must not intersect the active forward/reversed route edges",
            "seam_control_rule": "seam-intersecting origins are controls and cannot promote robustness",
            "centroid_policy": "linear_centroid_on_each_declared_unwrap",
            "positive_direction": "increasing_unwrapped_index",
        },
        "accepted_origin_results": origin_results,
        "seam_sensitive_controls": seam_controls,
        "robustness_summary": {
            "accepted_origin_count": len(accepted_origins),
            "seam_control_count": len(seam_controls),
            "forward_signed_final_centroid_delta_min": min(signed_forward),
            "forward_signed_final_centroid_delta_max": max(signed_forward),
            "reversed_signed_final_centroid_delta_min": min(signed_reversed),
            "reversed_signed_final_centroid_delta_max": max(signed_reversed),
            "signed_centroid_spread_tolerance": TOL,
            "interpretation": (
                "The Iteration 17 ring M6 candidate is robust across all "
                "declared unwrap origins whose seam does not intersect the "
                "active route. Seam-intersecting unwraps are recorded as "
                "controls and do not promote circular or wrap-crossing claims."
            ),
        },
        "go_no_go_for_iteration_17b": {
            "iteration_17b_allowed": status == "passed",
            "circular_motion_ceiling_to_test": claim_ceiling,
            "guidance": (
                "17-B may test circular metrics and seam-crossing routes; it "
                "must not inherit circular claims from unwrap robustness alone."
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": checks["all_accepted_origins_reach_m6"],
            "native_m6_candidate_gate_passed": checks["all_accepted_origins_reach_m6"],
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
            "wrap_crossing_movement",
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
        "next_iteration": "17b_circular_ring_motion_evidence_probe",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["robustness_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 17-A Ring Unwrap Robustness",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 17-A tests whether the S1 ring result is robust across declared unwrap origins.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- persistence basis: `{axis['persistence_basis']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- accepted unwrap origins: `{report['unwrap_robustness_policy']['accepted_origins']}`",
        f"- seam-control origins: `{report['unwrap_robustness_policy']['seam_control_origins']}`",
        f"- forward signed centroid range: `{summary['forward_signed_final_centroid_delta_min']}` to `{summary['forward_signed_final_centroid_delta_max']}`",
        f"- reversed signed centroid range: `{summary['reversed_signed_final_centroid_delta_min']}` to `{summary['reversed_signed_final_centroid_delta_max']}`",
        "",
        summary["interpretation"],
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_17b"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is unwrap-robust ring-transfer evidence, not circular locomotion or wrap-crossing movement evidence.",
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
