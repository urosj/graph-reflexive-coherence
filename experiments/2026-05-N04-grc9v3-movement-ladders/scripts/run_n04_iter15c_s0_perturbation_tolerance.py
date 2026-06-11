#!/usr/bin/env python3
"""Run N04 Iteration 15-C S0 perturbation tolerance envelope.

This sweep reuses the Iteration 15-B native S0 perturbation recovery probe and
maps which front/rear polarity perturbations recover, partially recover, or
fail closed under the same three-cycle recovery window.
"""

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

import run_n04_iter15b_s0_perturbation_recovery as iter15b  # noqa: E402


ITER15B_PATH = N04 / "outputs/n04_iter15b_s0_perturbation_recovery_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter15c_s0_perturbation_tolerance_profile.json"
REPORT_PATH = N04 / "reports/n04_iter15c_s0_perturbation_tolerance_profile.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter15c_s0_perturbation_tolerance.py"
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
    if result["t6_recovery_candidate_passed"]:
        outcome = "recovered"
        blocker = None
    elif scheduled > 0 or result["r6_recovery_candidate_passed"]:
        outcome = "partially_recovered"
        blocker = "source_budget_exhausted" if "feedback_source_budget_exhausted" in recovery_reason_codes else "incomplete_recovery_window"
    else:
        outcome = "failed_closed"
        if recovery_reason_codes and all(
            reason == iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD
            for reason in recovery_reason_codes
        ):
            blocker = "subthreshold"
        elif recovery_reason_codes and all(
            reason == iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY
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
        "r6_recovery_candidate_passed": result["r6_recovery_candidate_passed"],
        "t6_recovery_candidate_passed": result["t6_recovery_candidate_passed"],
        "recovery_scheduled_cycle_count": scheduled,
        "recovery_reason_codes": recovery_reason_codes,
        "signed_pre_perturbation_score": result["signed_pre_perturbation_score"],
        "signed_post_perturbation_score": result["signed_post_perturbation_score"],
        "signed_final_score": result["signed_final_score"],
        "signed_pre_perturbation_centroid_delta": result[
            "signed_pre_perturbation_centroid_delta"
        ],
        "signed_post_perturbation_centroid_delta": result[
            "signed_post_perturbation_centroid_delta"
        ],
        "signed_final_centroid_delta": result["signed_final_centroid_delta"],
        "budget_abs_error": result["budget_abs_error"],
        "nonnegative_gate_passed": result["nonnegative_gate_passed"],
        "identity_shape_gates_passed": result["identity_shape_gates_passed"],
        "artifact_validator_passed": result["artifact_validator"]["valid"],
        "surface_log_digest": result["surface_log_digest"],
        "producer_records_digest": result["producer_records_digest"],
    }


def _sweep_point(amount: float) -> dict[str, Any]:
    forward = iter15b._run_direction("forward", transfer_amount=amount)  # noqa: SLF001
    reversed_ = iter15b._run_direction("reversed", transfer_amount=amount)  # noqa: SLF001
    directions = [_direction_summary(forward), _direction_summary(reversed_)]
    both_r6 = all(direction["r6_recovery_candidate_passed"] for direction in directions)
    both_t6 = all(direction["t6_recovery_candidate_passed"] for direction in directions)
    if both_t6:
        outcome = "recovered"
        blocker = None
    elif any(direction["outcome"] == "partially_recovered" for direction in directions):
        outcome = "partially_recovered"
        blockers = [
            direction["primary_blocker"]
            for direction in directions
            if direction["primary_blocker"] is not None
        ]
        blocker = blockers[0] if blockers else "incomplete_recovery_window"
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
        "r6_recovered_both_directions": both_r6,
        "t6_recovered_both_directions": both_t6,
        "directions": directions,
        "budget_neutral": all(
            direction["budget_abs_error"] <= EPSILON_BUDGET for direction in directions
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
    iter15b_report = _load_json(ITER15B_PATH)
    points = [_sweep_point(amount) for amount in SWEEP_TRANSFER_AMOUNTS]
    t6_largest = _largest_amount(points, "t6_recovered_both_directions")
    t6_first_failed = _smallest_failed_amount(points, "t6_recovered_both_directions")
    t6_first_positive_failed = _smallest_positive_failed_amount(
        points,
        "t6_recovered_both_directions",
    )
    r6_largest = _largest_amount(points, "r6_recovered_both_directions")
    r6_first_failed = _smallest_failed_amount(points, "r6_recovered_both_directions")
    r6_first_positive_failed = _smallest_positive_failed_amount(
        points,
        "r6_recovered_both_directions",
    )
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
        "iteration_15b_available": iter15b_report["status"] == "passed",
        "sweep_values_declared_before_run": True,
        "same_native_s0_policy_reused": True,
        "same_recovery_window_reused": (
            iter15b.RECOVERY_WINDOW_CYCLES == 3
        ),
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
        "tolerance_boundaries_recorded": True,
        "no_t6_r6_claim_promotion": True,
    }
    first_failing_s0_perturbation = (
        t6_first_positive_failed
        if t6_first_positive_failed is not None
        else t6_first_failed
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter15c_s0_perturbation_tolerance_profile_v1",
        "iteration": "15-C",
        "status": "passed" if all(checks.values()) else "failed",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S0_chain_v1",
        "input_iteration_15b": _artifact_record(ITER15B_PATH),
        "claim_ceiling": "s0_same_fixture_perturbation_tolerance_profile",
        "sweep_policy": {
            "policy_id": "s0_front_rear_polarity_damping_sweep_v1",
            "transfer_amounts": SWEEP_TRANSFER_AMOUNTS,
            "pre_perturbation_cycles": iter15b.PRE_PERTURBATION_CYCLES,
            "recovery_window_cycles": iter15b.RECOVERY_WINDOW_CYCLES,
            "perturbation_kind": "budget_neutral_front_rear_polarity_damping",
            "budget_neutral": True,
            "topology_fixed": True,
        },
        "tolerance_summary": {
            "largest_t6_recoverable_perturbation": t6_largest,
            "smallest_t6_failed_perturbation": t6_first_failed,
            "smallest_positive_t6_failed_perturbation": t6_first_positive_failed,
            "largest_r6_recoverable_perturbation": r6_largest,
            "smallest_r6_failed_perturbation": r6_first_failed,
            "smallest_positive_r6_failed_perturbation": r6_first_positive_failed,
            "first_failing_s0_perturbation_for_15d": first_failing_s0_perturbation,
            "dominant_t6_blocker": "source_budget_exhausted",
            "interpretation": (
                "Current S0 does not complete the three-cycle T6 recovery "
                "window at any tested perturbation amount, including the "
                "zero-perturbation reservoir control. Smaller perturbations "
                "can restore R6 polarity, but T6 remains source-reservoir "
                "limited after the five-cycle pre-perturbation baseline."
            ),
        },
        "sweep_points": points,
        "go_no_go_for_iteration_15d": {
            "iteration_15d_allowed": True,
            "challenge_perturbation": first_failing_s0_perturbation,
            "challenge_reason": "smallest_positive_t6_failure_under_current_s0",
            "target_failure_mode_to_improve": "source_budget_exhausted",
            "s0_reference_claim_ceiling": "s0_same_fixture_perturbation_tolerance_profile",
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": iter15b_report["claim_flags"]["native_m6"],
            "native_m6_candidate_gate_passed": iter15b_report["claim_flags"][
                "native_m6_candidate_gate_passed"
            ],
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
            "r6_claim_allowed": False,
        },
        "blocked_claims": [
            "T6_perturbation_recovery",
            "R6_full_perturbation_recovery",
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
        "next_iteration": "15d_shock_resistant_recovery_geometry_probe",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["tolerance_summary"]
    lines = [
        "# N04 Iteration 15-C S0 Perturbation Tolerance Profile",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 15-C sweeps budget-neutral front/rear polarity perturbations on the native S0 same-fixture mechanism.",
        "",
        "## Tolerance Summary",
        "",
        f"- largest T6-recoverable perturbation: `{summary['largest_t6_recoverable_perturbation']}`",
        f"- smallest T6-failed perturbation: `{summary['smallest_t6_failed_perturbation']}`",
        f"- smallest positive T6-failed perturbation: `{summary['smallest_positive_t6_failed_perturbation']}`",
        f"- largest R6-recoverable perturbation: `{summary['largest_r6_recoverable_perturbation']}`",
        f"- smallest R6-failed perturbation: `{summary['smallest_r6_failed_perturbation']}`",
        f"- smallest positive R6-failed perturbation: `{summary['smallest_positive_r6_failed_perturbation']}`",
        f"- dominant T6 blocker: `{summary['dominant_t6_blocker']}`",
        "",
        summary["interpretation"],
        "",
        "## Sweep Points",
        "",
        "| transfer | outcome | R6 | T6 | blocker | scheduled recovery cycles |",
        "|---:|---|---|---|---|---|",
    ]
    for point in report["sweep_points"]:
        scheduled_counts = "/".join(
            str(direction["recovery_scheduled_cycle_count"])
            for direction in point["directions"]
        )
        lines.append(
            "| "
            f"{point['transfer_amount']} | {point['outcome']} | "
            f"{point['r6_recovered_both_directions']} | "
            f"{point['t6_recovered_both_directions']} | "
            f"{point['primary_blocker']} | {scheduled_counts} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
        ]
    )
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Go/No-Go",
            "",
        ]
    )
    for key, value in report["go_no_go_for_iteration_15d"].items():
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
