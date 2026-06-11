#!/usr/bin/env python3
"""Build a focused N04 Lane A review of the Iteration 10 M6 failure."""

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

ITERATION_10 = N04 / "outputs/self_renewing_movement_candidate_report.json"
LANE_B_LOCK = N04 / "outputs/n04_lane_b_lock_audit.json"
LANE_B_CLOSEOUT = N04 / "outputs/n04_lane_b_direction_parity_closeout.json"

OUTPUT_PATH = N04 / "outputs/n04_iteration10_failure_review.json"
REPORT_PATH = N04 / "reports/n04_iteration10_failure_review.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_iteration10_failure_review.py"
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


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


def build_review() -> dict[str, Any]:
    iteration_10 = _load_json(ITERATION_10)
    lane_b_lock = _load_json(LANE_B_LOCK)
    lane_b_closeout = _load_json(LANE_B_CLOSEOUT)

    tests = iteration_10["self_renewal_tests"]
    gates = iteration_10["gates"]
    m6 = iteration_10["m6_result"]
    lane_inputs = iteration_10["lane_inputs"]

    passed_before_failure = {
        "lane_b_locked_baseline_available": gates["lane_b_locked_baseline_available"],
        "m5_direction_parity_supported_boundary_response": gates[
            "m5_direction_parity_supported_boundary_response"
        ],
        "repeated_boundary_response_measured": tests["repeated_cycle_persistence"][
            "passed_as_boundary_response"
        ],
        "bounded_boundary_fixture_cost_measured": tests["bounded_movement_cost"][
            "measured"
        ],
        "identity_continuity_passed": tests["identity_continuity"]["passed"],
        "shape_economy_passed": tests["shape_economy"]["passed"],
    }

    failed_gates = {
        "feedback_path_present": gates["feedback_path_present"],
        "movement_restores_pulse_conditions": gates["movement_restores_pulse_conditions"],
        "polarity_regeneration_measured": gates["polarity_regeneration_measured"],
        "repeated_cycle_persistence_self_renewed": gates[
            "repeated_cycle_persistence_self_renewed"
        ],
        "full_m5_movement_support_available": gates["full_m5_movement_support_available"],
        "m6_gate_passed": gates["m6_gate_passed"],
    }

    diagnosis = {
        "failure_is_expected_from_fixture_design": True,
        "failure_is_not_due_to_direction_parity": lane_b_closeout["claim_ceiling"]
        == "m5_direction_parity_supported_boundary_response",
        "failure_is_not_due_to_budget_identity_or_shape": (
            passed_before_failure["bounded_boundary_fixture_cost_measured"]
            and passed_before_failure["identity_continuity_passed"]
            and passed_before_failure["shape_economy_passed"]
        ),
        "failure_is_due_to_absent_feedback_loop": True,
        "pulse_drive_is_external_to_s0_movement_substrate": True,
        "boundary_response_is_readout_not_rearm_source": True,
    }

    needed_to_reopen_m6 = [
        {
            "requirement": "define_feedback_path",
            "description": (
                "Define a runtime-visible path by which S0 movement-substrate "
                "state changes alter native pulse-producing surplus/route "
                "conditions."
            ),
        },
        {
            "requirement": "measure_post_response_pulse_condition_restoration",
            "description": (
                "Measure that a boundary response restores or raises the next "
                "pulse eligibility condition without external rescheduling."
            ),
        },
        {
            "requirement": "measure_polarity_regeneration",
            "description": (
                "Show that post-response state regenerates the correct forward "
                "or reversed polarity rather than consuming imported telemetry."
            ),
        },
        {
            "requirement": "distinguish_self_renewed_windows_from_pulse_schedule",
            "description": (
                "Count only response windows caused by regenerated pulse "
                "conditions, not windows inherited from the original E3 pulse "
                "schedule."
            ),
        },
    ]

    checks = {
        "iteration_10_artifact_fail_closed": iteration_10["status"] == "passed_fail_closed",
        "lane_b_lock_available": lane_b_lock["status"] == "passed",
        "primary_blocker_is_feedback_absence": m6["primary_blocker"]
        == "no_feedback_path_from_boundary_response_to_pulse_generation",
        "passed_gates_do_not_imply_m6": all(passed_before_failure.values())
        and not gates["m6_gate_passed"],
        "blocked_claim_flags_remain_false": all(
            iteration_10["claim_flags"][key] is False
            for key in [
                "movement_claim_allowed",
                "boundary_coupled_movement_claim_allowed",
                "loop_driven_movement_claim_allowed",
                "locomotion_like_claim_allowed",
                "adaptive_topology_entry_allowed",
                "movement_claim_inherited_from_n03",
                "m6_opened",
            ]
        ),
    }

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iteration10_failure_review_v1",
        "lane": "A",
        "iteration": "A3",
        "status": "passed" if all(checks.values()) else "failed",
        "review_subject": "Iteration 10 M6 failure",
        "claim_ceiling_after_failure": "m5_direction_parity_supported_boundary_response",
        "iteration_10_result": {
            "status": iteration_10["status"],
            "claim_ceiling": m6["claim_ceiling"],
            "m6_opened": m6["m6_opened"],
            "m6_gate_passed": m6["m6_gate_passed"],
            "primary_blocker": m6["primary_blocker"],
        },
        "passed_before_failure": passed_before_failure,
        "failed_gates": failed_gates,
        "diagnosis": diagnosis,
        "lane_input_summary": {
            lane_id: {
                "centroid_delta_total": row["centroid_delta_total"],
                "distinct_pulse_locked_window_count": row[
                    "distinct_pulse_locked_window_count"
                ],
                "externally_rescheduled_pulse_drive": row[
                    "externally_rescheduled_pulse_drive"
                ],
                "feedback_path_from_movement_substrate_to_e3_producer": row[
                    "feedback_path_from_movement_substrate_to_e3_producer"
                ],
                "movement_restores_pulse_generating_conditions": row[
                    "movement_restores_pulse_generating_conditions"
                ],
                "polarity_regeneration_measured": row[
                    "polarity_regeneration_measured"
                ],
                "m6_lane_passed": row["m6_lane_passed"],
            }
            for lane_id, row in lane_inputs.items()
        },
        "what_this_rules_out": [
            "The current S0 boundary fixture does not demonstrate self-renewing movement.",
            "Repeated boundary-response windows are not evidence of M6 when they are inherited from the E3 pulse schedule.",
            "Direction-parity-supported boundary response is not sufficient for locomotion-like dynamics.",
        ],
        "what_this_does_not_rule_out": [
            "A future fixture with explicit movement-substrate-to-pulse feedback could reopen M6.",
            "A native pulse-through-substrate mechanism could be tested separately.",
            "Adaptive topology remains blocked here, not disproven in general.",
        ],
        "needed_to_reopen_m6": needed_to_reopen_m6,
        "recommended_next_decision": (
            "Close N04 at direction-parity-supported boundary response, or open "
            "a separate mechanism task that explicitly defines feedback from "
            "movement-substrate state to pulse-generation conditions."
        ),
        "claim_flags": iteration_10["claim_flags"],
        "checks": checks,
        "source_artifacts": {
            "iteration_10_m6": _artifact_record(ITERATION_10),
            "lane_b_lock": _artifact_record(LANE_B_LOCK),
            "lane_b_closeout": _artifact_record(LANE_B_CLOSEOUT),
        },
        "command": COMMAND,
        "environment": _environment_record(),
    }


def write_report(review: dict[str, Any]) -> None:
    result = review["iteration_10_result"]
    lines = [
        "# N04 Iteration 10 Failure Review",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{review['status']}`",
        f"Review subject: `{review['review_subject']}`",
        f"Claim ceiling after failure: `{review['claim_ceiling_after_failure']}`",
        "",
        "## Failure",
        "",
        f"- Iteration 10 status: `{result['status']}`",
        f"- M6 opened: `{result['m6_opened']}`",
        f"- M6 gate passed: `{result['m6_gate_passed']}`",
        f"- Primary blocker: `{result['primary_blocker']}`",
        "",
        "## What Passed Before The Failure",
        "",
    ]
    for key, value in review["passed_before_failure"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Failed Gates", ""])
    for key, value in review["failed_gates"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Diagnosis", ""])
    for key, value in review["diagnosis"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Needed To Reopen M6", ""])
    for item in review["needed_to_reopen_m6"]:
        lines.append(f"- `{item['requirement']}`: {item['description']}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Iteration 10 failed for the right reason: the current fixture has",
            "direction-parity-supported repeated boundary response, but no feedback",
            "from the S0 movement substrate back into native E3 pulse-generating",
            "conditions. Budget, identity, shape/economy, and direction parity were",
            "not the limiting failures. The limiting failure is causal closure of",
            "the drive loop.",
            "",
        ]
    )
    _write_report(REPORT_PATH, lines)


def main() -> int:
    review = build_review()
    _write_json(OUTPUT_PATH, review)
    write_report(review)
    print(
        json.dumps(
            {
                "status": review["status"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if review["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
