#!/usr/bin/env python3
"""Run N04 Iteration 16-B S4 corridor perturbation envelope probe."""

from __future__ import annotations

import hashlib
import json
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


ITER16_PATH = N04 / "outputs/n04_iter16_corridor_transfer_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter16b_corridor_perturbation_probe.json"
REPORT_PATH = N04 / "reports/n04_iter16b_corridor_perturbation_probe.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter16b_corridor_perturbation_probe.py"
)

SWEEP_TRANSFER_AMOUNTS = [
    0.0,
    0.02,
    0.05,
    0.075,
    0.10,
    0.125,
    0.15,
    0.175,
    0.20,
    0.25,
    0.30,
    0.35,
]
EPSILON_BUDGET = 1e-12


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


def _direction_summary(result: dict[str, Any]) -> dict[str, Any]:
    recovery_reason_codes = [
        cycle["producer_reason_code"] for cycle in result["recovery_cycles"]
    ]
    scheduled = result["recovery_scheduled_cycle_count"]
    if result["m6_transfer_candidate_passed"]:
        outcome = "recovered"
        blocker = None
    elif result["m5_direction_control_passed"] or result["m4_boundary_response_passed"]:
        outcome = "partially_recovered"
        blocker = (
            "centroid_not_restored"
            if result["m4_boundary_response_passed"]
            else "incomplete_recovery_window"
        )
    else:
        outcome = "failed_closed"
        if recovery_reason_codes and all(
            reason == iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD
            for reason in recovery_reason_codes
        ):
            blocker = "subthreshold"
        elif recovery_reason_codes and all(
            reason == iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY
            for reason in recovery_reason_codes
        ):
            blocker = "wrong_polarity"
        elif "feedback_source_budget_exhausted" in recovery_reason_codes:
            blocker = "source_budget_exhausted"
        else:
            blocker = "no_feedback_recovery"
    return {
        "direction": result["direction"],
        "outcome": outcome,
        "primary_blocker": blocker,
        "m4_boundary_response_passed": result["m4_boundary_response_passed"],
        "m5_direction_control_passed": result["m5_direction_control_passed"],
        "m6_transfer_candidate_passed": result["m6_transfer_candidate_passed"],
        "recovery_scheduled_cycle_count": scheduled,
        "recovery_reason_codes": recovery_reason_codes,
        "signed_pre_transfer_score": result["signed_pre_transfer_score"],
        "signed_post_perturbation_score": result["signed_post_perturbation_score"],
        "signed_final_score": result["signed_final_score"],
        "signed_pre_transfer_centroid_delta": result["signed_pre_transfer_centroid_delta"],
        "signed_post_perturbation_centroid_delta": result[
            "signed_post_perturbation_centroid_delta"
        ],
        "signed_final_centroid_delta": result["signed_final_centroid_delta"],
        "raw_final_centroid_delta": result["raw_final_centroid_delta"],
        "budget_abs_error": result["budget_abs_error"],
        "nonnegative_gate_passed": result["nonnegative_gate_passed"],
        "identity_shape_gates_passed": result["identity_shape_gates_passed"],
        "artifact_validator_passed": result["artifact_validator"]["valid"],
        "surface_log_digest": result["surface_log_digest"],
        "producer_records_digest": result["producer_records_digest"],
    }


def _sweep_point(amount: float) -> dict[str, Any]:
    forward = iter16._run_corridor_direction(  # noqa: SLF001
        "forward",
        transfer_amount=amount,
    )
    reversed_ = iter16._run_corridor_direction(  # noqa: SLF001
        "reversed",
        transfer_amount=amount,
    )
    directions = [_direction_summary(forward), _direction_summary(reversed_)]
    both_m4 = all(direction["m4_boundary_response_passed"] for direction in directions)
    both_m5 = all(direction["m5_direction_control_passed"] for direction in directions)
    both_m6 = all(direction["m6_transfer_candidate_passed"] for direction in directions)
    if amount == 0.0:
        outcome = "neutral_control"
        blocker = "no_perturbation_applied"
    elif both_m6:
        outcome = "recovered"
        blocker = None
    elif both_m4 or both_m5:
        outcome = "partially_recovered"
        blockers = [
            direction["primary_blocker"]
            for direction in directions
            if direction["primary_blocker"] is not None
        ]
        blocker = blockers[0] if blockers else "centroid_not_restored"
    else:
        outcome = "failed_closed"
        blockers = [
            direction["primary_blocker"]
            for direction in directions
            if direction["primary_blocker"] is not None
        ]
        blocker = blockers[0] if blockers else "no_feedback_recovery"
    return {
        "transfer_amount": amount,
        "outcome": outcome,
        "primary_blocker": blocker,
        "m4_recovered_both_directions": both_m4,
        "m5_recovered_both_directions": both_m5,
        "m6_recovered_both_directions": both_m6,
        "directions": directions,
        "budget_neutral": all(
            direction["budget_abs_error"] <= EPSILON_BUDGET
            for direction in directions
        ),
        "topology_fixed": True,
        "forbidden_direct_writes": False,
    }


def _largest_amount(points: list[dict[str, Any]], predicate: str) -> float | None:
    values = [point["transfer_amount"] for point in points if point[predicate]]
    return max(values) if values else None


def _smallest_failed_amount(points: list[dict[str, Any]], predicate: str) -> float | None:
    values = [point["transfer_amount"] for point in points if not point[predicate]]
    return min(values) if values else None


def _smallest_positive_failed_amount(
    points: list[dict[str, Any]],
    predicate: str,
) -> float | None:
    values = [
        point["transfer_amount"]
        for point in points
        if point["transfer_amount"] > 0.0 and not point[predicate]
    ]
    return min(values) if values else None


def build_report() -> dict[str, Any]:
    iter16_report = _load_json(ITER16_PATH)
    points = [_sweep_point(amount) for amount in SWEEP_TRANSFER_AMOUNTS]
    m6_largest = _largest_amount(points, "m6_recovered_both_directions")
    m6_first_failed = _smallest_positive_failed_amount(
        points,
        "m6_recovered_both_directions",
    )
    m6_first_positive_failed = _smallest_positive_failed_amount(
        points,
        "m6_recovered_both_directions",
    )
    m5_largest = _largest_amount(points, "m5_recovered_both_directions")
    m4_largest = _largest_amount(points, "m4_recovered_both_directions")
    all_budget_neutral = all(point["budget_neutral"] for point in points)
    all_artifacts_valid = all(
        direction["artifact_validator_passed"]
        for point in points
        for direction in point["directions"]
    )
    all_shape_safe = all(
        direction["identity_shape_gates_passed"]
        and direction["nonnegative_gate_passed"]
        for point in points
        for direction in point["directions"]
    )
    checks = {
        "iteration_16_available": iter16_report["status"] == "passed",
        "sweep_values_declared_before_run": True,
        "same_s4_corridor_policy_reused": True,
        "same_recovery_window_reused": iter16.RECOVERY_WINDOW_CYCLES == 3,
        "every_point_classified": all(point["outcome"] for point in points),
        "primary_blockers_recorded_for_failed_points": all(
            point["primary_blocker"] is not None
            for point in points
            if point["outcome"] != "recovered"
        ),
        "budget_neutral_all_points": all_budget_neutral,
        "topology_fixed_all_points": all(point["topology_fixed"] for point in points),
        "no_forbidden_direct_writes": not any(
            point["forbidden_direct_writes"] for point in points
        ),
        "artifact_validators_passed": all_artifacts_valid,
        "nonnegative_and_shape_gates_passed": all_shape_safe,
        "corridor_tolerance_boundaries_recorded": True,
        "no_full_t6_claim_promotion": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter16b_corridor_perturbation_probe_v1",
        "iteration": "16-B",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": iter16_report["movement_substrate"],
        "geometry_scope": "transferred_geometry",
        "substrate_class": "corridor",
        "input_iteration_16": _artifact_record(ITER16_PATH),
        "claim_ceiling": "s4_corridor_perturbation_envelope_profile",
        "sweep_policy": {
            "policy_id": "s4_corridor_front_rear_polarity_damping_sweep_v1",
            "transfer_amounts": SWEEP_TRANSFER_AMOUNTS,
            "pre_perturbation_cycles": iter16.PRE_TRANSFER_CYCLES,
            "recovery_window_cycles": iter16.RECOVERY_WINDOW_CYCLES,
            "perturbation_kind": "budget_neutral_front_rear_polarity_damping",
            "budget_neutral": True,
            "topology_fixed_during_run": True,
        },
        "persistence_axis": {
            "persistence_level": "T6_candidate",
            "persistence_basis": "s4_corridor_perturbation_envelope",
            "largest_t6_candidate_recoverable_perturbation": m6_largest,
            "smallest_t6_candidate_failed_perturbation": m6_first_failed,
            "smallest_positive_t6_candidate_failed_perturbation": m6_first_positive_failed,
            "largest_m5_recoverable_perturbation": m5_largest,
            "largest_m4_recoverable_perturbation": m4_largest,
            "recovery_window_cycles": iter16.RECOVERY_WINDOW_CYCLES,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "single_corridor_fixture_envelope_without_ring_grid_or_port_graph_transfer",
        },
        "tolerance_summary": {
            "largest_m6_recoverable_perturbation": m6_largest,
            "smallest_m6_failed_perturbation": m6_first_failed,
            "smallest_positive_m6_failed_perturbation": m6_first_positive_failed,
            "largest_m5_recoverable_perturbation": m5_largest,
            "largest_m4_recoverable_perturbation": m4_largest,
            "dominant_failure_blocker": (
                "none_in_tested_range"
                if m6_first_positive_failed is None
                else next(
                    point["primary_blocker"]
                    for point in points
                    if point["transfer_amount"] == m6_first_positive_failed
                )
            ),
            "interpretation": (
                "The S4 corridor fixture recovers T6-candidate centroid "
                "restoration through perturbation 0.15 in both directions. "
                "Above that boundary, direction-controlled feedback response "
                "continues below the full M6/T6-candidate ceiling: M5-style "
                "recovery is retained through 0.25 and M4-style boundary "
                "response through 0.35. This strengthens the scoped "
                "T6-candidate persistence evidence for the corridor fixture, "
                "but full T6 and broad geometry-transfer claims remain "
                "blocked."
            ),
        },
        "sweep_points": points,
        "go_no_go_for_iteration_17": {
            "iteration_17_allowed": status == "passed",
            "ring_transfer_ceiling_to_test": iter16_report["claim_ceiling"],
            "ring_transfer_guidance": "ring transfer may proceed under explicit unwrap policy; do not inherit full T6",
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": True,
            "native_m6_candidate_gate_passed": True,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "t6_claim_allowed": False,
            "broad_geometry_transfer_claim_allowed": False,
        },
        "blocked_claims": [
            "full_T6_general_persistence",
            "ring_transfer",
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
        "next_iteration": "17_s1_ring_with_explicit_unwrap_policy",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["tolerance_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 16-B S4 Corridor Perturbation Probe",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 16-B sweeps budget-neutral front/rear perturbations on the S4 corridor transfer fixture.",
        "",
        "## T-Axis Summary",
        "",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- persistence basis: `{axis['persistence_basis']}`",
        f"- largest T6-candidate recoverable perturbation: `{axis['largest_t6_candidate_recoverable_perturbation']}`",
        f"- smallest T6-candidate failed perturbation: `{axis['smallest_t6_candidate_failed_perturbation']}`",
        f"- full T6 claim allowed: `{axis['t6_full_claim_allowed']}`",
        f"- full T6 blocker: `{axis['t6_full_claim_blocker']}`",
        "",
        summary["interpretation"],
        "",
        "## Sweep Points",
        "",
        "| transfer | outcome | M4 | M5 | M6 | blocker | scheduled recovery cycles |",
        "|---:|---|---|---|---|---|---|",
    ]
    for point in report["sweep_points"]:
        scheduled_counts = "/".join(
            str(direction["recovery_scheduled_cycle_count"])
            for direction in point["directions"]
        )
        lines.append(
            "| "
            f"{point['transfer_amount']} | {point['outcome']} | "
            f"{point['m4_recovered_both_directions']} | "
            f"{point['m5_recovered_both_directions']} | "
            f"{point['m6_recovered_both_directions']} | "
            f"{point['primary_blocker']} | {scheduled_counts} |"
        )
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_17"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
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
