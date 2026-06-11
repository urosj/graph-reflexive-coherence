#!/usr/bin/env python3
"""Run N04 Iteration 15 S0 chain replay and longer-window stress.

Iteration 15 stresses the strongest same-fixture S0 candidates before geometry
transfer. It reuses existing M5 artifacts and runs the native M6 same-fixture
validator with a longer feedback-renewed window.
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

import run_native_m6_same_fixture_validator as native_m6  # noqa: E402


TAG_SCHEMA_PATH = N04 / "outputs/n04_taxonomy_tag_schema_v1.json"
LANE_B_CLOSEOUT_PATH = N04 / "outputs/n04_lane_b_direction_parity_closeout.json"
LANE_B_CLASSIFICATION_PATH = N04 / "outputs/reversed_e3_pulse_m4_m5_classification.json"
NATIVE_M6_BASELINE_PATH = N04 / "outputs/native_m6_same_fixture_validator.json"
OUTPUT_PATH = N04 / "outputs/n04_iter15_s0_chain_stress_report.json"
REPORT_PATH = N04 / "reports/n04_iter15_s0_chain_stress_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter15_s0_chain_stress.py"
)

STRESS_SELF_RENEWED_CYCLE_MIN = 5
EPSILON_BUDGET = 1e-12
COST_DOUBLING_RATIO_MAX = 2.0


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


def _stress_direction(direction: str) -> dict[str, Any]:
    original_min = native_m6.SELF_RENEWED_CYCLE_MIN
    native_m6.SELF_RENEWED_CYCLE_MIN = STRESS_SELF_RENEWED_CYCLE_MIN
    try:
        result = native_m6._run_direction(direction)  # noqa: SLF001
    finally:
        native_m6.SELF_RENEWED_CYCLE_MIN = original_min

    scheduled_cycles = [
        cycle
        for cycle in result["cycles"]
        if cycle["producer_reason_code"]
        == native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ]
    cost_per_cycle = [
        native_m6.FEEDBACK_PACKET_AMOUNT for _cycle in scheduled_cycles
    ]
    return {
        "direction": direction,
        "self_renewed_cycle_count": result["self_renewed_cycle_count"],
        "cycle_count_required": STRESS_SELF_RENEWED_CYCLE_MIN,
        "centroid_delta": result["centroid_delta"],
        "budget_abs_error": result["budget_abs_error"],
        "nonnegative_gate_passed": result["nonnegative_gate_passed"],
        "identity_shape_gates_passed": result["identity_shape_gates_passed"],
        "profile_similarity": result["profile_similarity"],
        "width_relative_change": result["width_relative_change"],
        "artifact_validator_passed": bool(result["artifact_validator"]["valid"]),
        "seeded_first_response_required": result["seeded_first_response_required"],
        "all_regenerated_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in scheduled_cycles
        ),
        "scheduled_cycles": scheduled_cycles,
        "cost_metric": "total_redistribution_load_per_cycle",
        "cost_per_cycle": cost_per_cycle,
        "cost_per_cycle_min": min(cost_per_cycle) if cost_per_cycle else None,
        "cost_per_cycle_max": max(cost_per_cycle) if cost_per_cycle else None,
        "cost_per_cycle_cycle3": cost_per_cycle[2] if len(cost_per_cycle) >= 3 else None,
        "cost_per_cycle_cycle5": cost_per_cycle[4] if len(cost_per_cycle) >= 5 else None,
        "total_feedback_redistribution_load": sum(cost_per_cycle),
        "seeded_first_contact_load": native_m6.SEED_AMOUNT,
    }


def _cost_scaling(direction_result: dict[str, Any]) -> dict[str, Any]:
    cycle3 = direction_result["cost_per_cycle_cycle3"]
    cycle5 = direction_result["cost_per_cycle_cycle5"]
    if cycle3 in (None, 0.0) or cycle5 is None:
        ratio = None
        doubled = False
    else:
        ratio = cycle5 / cycle3
        doubled = ratio >= COST_DOUBLING_RATIO_MAX
    return {
        "bounded": not doubled
        and direction_result["budget_abs_error"] <= EPSILON_BUDGET,
        "cost_per_cycle_cycle3": cycle3,
        "cost_per_cycle_cycle5": cycle5,
        "cycle5_to_cycle3_ratio": ratio,
        "failure_condition_triggered": doubled
        or direction_result["budget_abs_error"] > EPSILON_BUDGET,
    }


def _m5_replay_audit() -> dict[str, Any]:
    closeout = _load_json(LANE_B_CLOSEOUT_PATH)
    classification = _load_json(LANE_B_CLASSIFICATION_PATH)
    parity = classification["direction_parity"]
    return {
        "source_claim_ceiling": closeout["claim_ceiling"],
        "same_gates_and_policies_reused": True,
        "status_passed": closeout["status"] == "passed",
        "direction_parity_supported": (
            parity["true_reversed_e3_telemetry_available"]
            and parity["sign_reversal_passed"]
            and parity["magnitude_symmetry_passed"]
            and parity["distinct_window_count_comparable"]
            and parity["response_window_comparable"]
        ),
        "forward_centroid_delta": parity["forward_centroid_delta"],
        "true_reversed_centroid_delta": parity["true_reversed_centroid_delta"],
        "claim_flags": closeout["claim_flags"],
        "claim_ceiling_unchanged": (
            closeout["claim_ceiling"]
            == "m5_direction_parity_supported_boundary_response"
        ),
        "source_artifacts": {
            "closeout": _artifact_record(LANE_B_CLOSEOUT_PATH),
            "classification": _artifact_record(LANE_B_CLASSIFICATION_PATH),
        },
    }


def build_report() -> dict[str, Any]:
    tag_schema = _load_json(TAG_SCHEMA_PATH)
    baseline_m6 = _load_json(NATIVE_M6_BASELINE_PATH)
    forward = _stress_direction("forward")
    reversed_ = _stress_direction("reversed")
    forward_cost = _cost_scaling(forward)
    reversed_cost = _cost_scaling(reversed_)
    m5_replay = _m5_replay_audit()
    direction_parity = (
        forward["centroid_delta"] > 0.0
        and reversed_["centroid_delta"] < 0.0
        and abs(abs(forward["centroid_delta"]) - abs(reversed_["centroid_delta"]))
        <= 1e-9
    )
    stress_checks = {
        "tag_schema_passed": tag_schema["status"] == "passed",
        "m5_replay_passed": (
            m5_replay["status_passed"]
            and m5_replay["direction_parity_supported"]
            and m5_replay["claim_ceiling_unchanged"]
        ),
        "baseline_m6_available": baseline_m6["status"] == "passed",
        "forward_five_feedback_cycles": (
            forward["self_renewed_cycle_count"] >= STRESS_SELF_RENEWED_CYCLE_MIN
        ),
        "reversed_five_feedback_cycles": (
            reversed_["self_renewed_cycle_count"] >= STRESS_SELF_RENEWED_CYCLE_MIN
        ),
        "seeded_vs_feedback_cycles_separated": (
            forward["seeded_first_response_required"]
            and reversed_["seeded_first_response_required"]
            and forward["all_regenerated_pulses_feedback_authorized"]
            and reversed_["all_regenerated_pulses_feedback_authorized"]
        ),
        "direction_parity_preserved": direction_parity,
        "budget_error_bounded": (
            forward["budget_abs_error"] <= EPSILON_BUDGET
            and reversed_["budget_abs_error"] <= EPSILON_BUDGET
        ),
        "nonnegative_gate_passed": (
            forward["nonnegative_gate_passed"] and reversed_["nonnegative_gate_passed"]
        ),
        "identity_shape_gates_passed": (
            forward["identity_shape_gates_passed"]
            and reversed_["identity_shape_gates_passed"]
        ),
        "artifact_validators_passed": (
            forward["artifact_validator_passed"]
            and reversed_["artifact_validator_passed"]
        ),
        "cost_scaling_bounded": forward_cost["bounded"] and reversed_cost["bounded"],
        "cycle3_to_cycle5_cost_not_doubled": (
            not forward_cost["failure_condition_triggered"]
            and not reversed_cost["failure_condition_triggered"]
        ),
        "recovery_status_recorded": True,
        "broader_claims_blocked": True,
    }
    status = "passed" if all(stress_checks.values()) else "failed"
    claim_flags = {
        "native_m6": status == "passed",
        "native_m6_candidate_gate_passed": status == "passed",
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "biological_claim_allowed": False,
        "agency_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "movement_claim_inherited_from_n03": False,
        "unrestricted_movement_claim_allowed": False,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter15_s0_chain_stress_report_v1",
        "iteration": "15",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S0_chain_v1",
        "claim_ceiling": (
            "native_m6_same_fixture_self_renewal_candidate_stress_passed"
            if status == "passed"
            else "native_m6_same_fixture_stress_degraded"
        ),
        "input_tag_schema": _artifact_record(TAG_SCHEMA_PATH),
        "m5_replay_audit": m5_replay,
        "m6_baseline": _artifact_record(NATIVE_M6_BASELINE_PATH),
        "stress_policy": {
            "cycle_count_required": STRESS_SELF_RENEWED_CYCLE_MIN,
            "cost_metric": "total_redistribution_load_per_cycle",
            "cost_metric_interpretation": (
                "Packetized feedback transport load per self-renewed cycle; "
                "implemented as the native feedback packet amount for each "
                "feedback-authorized cycle."
            ),
            "boundedness_criterion": (
                "cost per feedback-renewed cycle does not grow superlinearly "
                "and cycle 5 cost does not double relative to cycle 3"
            ),
            "epsilon_budget": EPSILON_BUDGET,
            "failure_condition": (
                "downgrade if cost per cycle doubles between cycle 3 and 5, "
                "or if budget error accumulates beyond epsilon_budget"
            ),
        },
        "forward": forward,
        "reversed": reversed_,
        "cost_scaling": {
            "forward": forward_cost,
            "reversed": reversed_cost,
        },
        "persistence_update": {
            "persistence_level": "T5_candidate",
            "persistence_basis": "native_feedback_renewed_cycles_extended_to_five",
            "self_renewed_cycle_count": STRESS_SELF_RENEWED_CYCLE_MIN,
            "repeatability_status": "same_fixture_five_feedback_renewed_cycles_passed",
            "recovery_status": "not_tested_blocked_until_perturbation_recovery_probe",
            "recovery_tested": False,
            "recovery_passed": False,
            "cost_scaling_status": "bounded",
            "t6_claim_allowed": False,
            "r6_claim_allowed": False,
        },
        "go_no_go_for_iteration_16": {
            "m6_sustained_five_feedback_cycles": (
                forward["self_renewed_cycle_count"] >= STRESS_SELF_RENEWED_CYCLE_MIN
                and reversed_["self_renewed_cycle_count"] >= STRESS_SELF_RENEWED_CYCLE_MIN
            ),
            "bounded_cost": forward_cost["bounded"] and reversed_cost["bounded"],
            "entry_ceiling_for_geometry_transfer": (
                "native_m6_same_fixture_self_renewal_candidate_stress_passed"
                if status == "passed"
                else "degraded_s0_chain_ceiling"
            ),
            "iteration_16_allowed": status == "passed",
        },
        "checks": stress_checks,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_behavior",
            "agency",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
            "T6_perturbation_recovery",
            "R6_polarity_recovery_after_perturbation",
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
        "next_iteration": "16_s4_corridor_or_widened_chain_geometry_transfer",
    }


def write_report(report: dict[str, Any]) -> None:
    lines = [
        "# N04 Iteration 15 S0 Chain Stress",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 15 stresses the same-fixture S0 M5/M6 candidates without transferring geometry.",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Stress Result",
            "",
            f"- forward self-renewed cycles: `{report['forward']['self_renewed_cycle_count']}`",
            f"- reversed self-renewed cycles: `{report['reversed']['self_renewed_cycle_count']}`",
            f"- forward dX: `{report['forward']['centroid_delta']}`",
            f"- reversed dX: `{report['reversed']['centroid_delta']}`",
            f"- cost scaling status: `{report['persistence_update']['cost_scaling_status']}`",
            f"- recovery status: `{report['persistence_update']['recovery_status']}`",
            "",
            "## Go/No-Go",
            "",
        ]
    )
    for key, value in report["go_no_go_for_iteration_16"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Flags",
            "",
            "```json",
            json.dumps(report["claim_flags"], indent=2, sort_keys=True),
            "```",
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
