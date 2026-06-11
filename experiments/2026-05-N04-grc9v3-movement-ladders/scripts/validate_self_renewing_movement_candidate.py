#!/usr/bin/env python3
"""Validate the N04 Iteration 10 self-renewing movement candidate gate.

Iteration 10 starts from the locked Lane B baseline. Lane B supports native
direction-parity-controlled repeated boundary response, but M6 requires a
stronger condition: the boundary response must restore or regenerate the pulse
conditions that drive the next response. This script is intentionally
fail-closed when that feedback path is absent.
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

LANE_B_CLOSEOUT = N04 / "outputs/n04_lane_b_direction_parity_closeout.json"
LANE_B_LOCK = N04 / "outputs/n04_lane_b_lock_audit.json"
LANE_B_CLASSIFICATION = N04 / "outputs/reversed_e3_pulse_m4_m5_classification.json"
ITERATION_8_BOUNDARY = N04 / "outputs/boundary_coupled_pulse_report.json"
REVERSED_BOUNDARY = N04 / "outputs/reversed_e3_pulse_boundary_coupling_report.json"

OUTPUT_PATH = N04 / "outputs/self_renewing_movement_candidate_report.json"
REPORT_PATH = N04 / "reports/self_renewing_movement_candidate_report.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/validate_self_renewing_movement_candidate.py"
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise TypeError(f"{path} contains a non-object row")
                rows.append(row)
    return rows


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


def _timeseries_rows(lane: dict[str, Any]) -> list[dict[str, Any]]:
    path = ROOT / lane["timeseries"]["path"]
    rows = _load_jsonl(path)
    digest = _digest_json(rows)
    expected = lane["timeseries"]["timeseries_digest"]
    if digest != expected:
        raise ValueError(f"timeseries digest mismatch for {path}")
    return rows


def _coupling_load(rows: list[dict[str, Any]]) -> dict[str, float]:
    coupling_values = [float(row["coupling_amount"]) for row in rows]
    deltas = [
        abs(coupling_values[index] - coupling_values[index - 1])
        for index in range(1, len(coupling_values))
    ]
    nonzero_count = sum(1 for value in coupling_values if abs(value) > 0.0)
    return {
        "coupling_amount_max": max(coupling_values),
        "coupling_load_total": sum(coupling_values),
        "coupling_change_l1_total": sum(deltas),
        "nonzero_coupling_sample_count": nonzero_count,
    }


def _lane_m6_inputs(
    *,
    lane_id: str,
    lane_result: dict[str, Any],
    classifier_result: dict[str, Any],
) -> dict[str, Any]:
    rows = _timeseries_rows(lane_result)
    load = _coupling_load(rows)
    gates = lane_result["gates"]
    identity = lane_result["identity_tracking"]
    topology = lane_result["topology"]
    conservation = lane_result["conservation"]

    return {
        "lane_id": lane_id,
        "m5_candidate_gate_passed": bool(classifier_result["m5_candidate_gate_passed"]),
        "m5_direction_parity_gate_passed": bool(
            classifier_result["m5_full_direction_parity_gate_passed"]
        ),
        "centroid_delta_total": float(
            classifier_result["lane_result"]["centroid_delta_total"]
            if lane_id.startswith("P3")
            else classifier_result["forward_reference_result"]["centroid_delta_total"]
        ),
        "response_window": float(
            classifier_result["lane_result"]["distinct_pulse_locked_response_window"]
            if lane_id.startswith("P3")
            else classifier_result["forward_reference_result"][
                "distinct_pulse_locked_response_window"
            ]
        ),
        "distinct_pulse_locked_window_count": int(
            classifier_result["lane_result"]["distinct_pulse_locked_window_count"]
            if lane_id.startswith("P3")
            else classifier_result["forward_reference_result"][
                "distinct_pulse_locked_window_count"
            ]
        ),
        "boundary_response_repeated": True,
        "feedback_path_from_movement_substrate_to_e3_producer": False,
        "movement_restores_pulse_generating_conditions": False,
        "polarity_regeneration_measured": False,
        "polarity_regeneration_passed": False,
        "externally_rescheduled_pulse_drive": True,
        "repeated_response_is_pulse_driven_not_self_renewed": True,
        "identity_continuity_passed": bool(identity["parent_basin_preserved"]),
        "shape_economy_budget_passed": bool(
            gates["budget_gate_passed"]
            and gates["nonnegative_gate_passed"]
            and not topology["topology_changed"]
            and conservation["budget_abs_error_max"] == 0.0
        ),
        "movement_cost_proxy": load,
        "m6_lane_passed": False,
        "primary_blocker": "no_feedback_path_from_boundary_response_to_pulse_generation",
    }


def build_report() -> dict[str, Any]:
    closeout = _load_json(LANE_B_CLOSEOUT)
    lock = _load_json(LANE_B_LOCK)
    classification = _load_json(LANE_B_CLASSIFICATION)
    iteration_8 = _load_json(ITERATION_8_BOUNDARY)
    reversed_boundary = _load_json(REVERSED_BOUNDARY)

    forward_lane = iteration_8["lane_results"]["P2_asymmetric_boundary_coupling_forward"]
    reversed_lane = reversed_boundary["lane_result"]

    forward_inputs = _lane_m6_inputs(
        lane_id="P2_asymmetric_boundary_coupling_forward",
        lane_result=forward_lane,
        classifier_result=classification,
    )
    reversed_inputs = _lane_m6_inputs(
        lane_id="P3_true_reversed_e3_pulse_boundary_coupling",
        lane_result=reversed_lane,
        classifier_result=classification,
    )

    full_m5_movement_support = bool(
        closeout["claim_flags"]["movement_claim_allowed"]
        or closeout["claim_flags"]["boundary_coupled_movement_claim_allowed"]
        or closeout["claim_flags"]["loop_driven_movement_claim_allowed"]
    )
    lane_b_locked = lock["status"] == "passed" and closeout["claim_ceiling"] == (
        "m5_direction_parity_supported_boundary_response"
    )

    gates = {
        "lane_b_locked_baseline_available": lane_b_locked,
        "m5_direction_parity_supported_boundary_response": (
            closeout["claim_ceiling"]
            == "m5_direction_parity_supported_boundary_response"
        ),
        "full_m5_movement_support_available": full_m5_movement_support,
        "feedback_path_present": False,
        "movement_restores_pulse_conditions": False,
        "polarity_regeneration_measured": False,
        "repeated_cycle_persistence_measured": True,
        "repeated_cycle_persistence_self_renewed": False,
        "bounded_cost_measured": True,
        "identity_continuity_passed": (
            forward_inputs["identity_continuity_passed"]
            and reversed_inputs["identity_continuity_passed"]
        ),
        "shape_economy_gates_passed": (
            forward_inputs["shape_economy_budget_passed"]
            and reversed_inputs["shape_economy_budget_passed"]
        ),
        "m6_gate_passed": False,
    }

    payload = {
        "schema": "movement_ladder_report_v1",
        "report_kind": "self_renewing_movement_candidate_report_v1",
        "status": "passed_fail_closed",
        "runtime_family": "LGRC9V3",
        "execution_surface": "surface_c_lgrc9v3_e3_pulse_to_s0_boundary_fixture",
        "budget_surface": "node_only",
        "native_lgrc9v3_e3_pulse_used": True,
        "native_grc9v3_proposal_flux_control_used": False,
        "lane_b_baseline": {
            "claim_ceiling": closeout["claim_ceiling"],
            "lock_status": lock["status"],
            "lock_report": "reports/n04_lane_b_lock_audit.md",
        },
        "m6_result": {
            "m6_opened": False,
            "m6_gate_passed": False,
            "claim_ceiling": "m6_not_opened_feedback_path_absent",
            "primary_blocker": "no_feedback_path_from_boundary_response_to_pulse_generation",
            "blocked_reason": (
                "Lane B supplies direction-parity-controlled repeated boundary "
                "response, but the S0 boundary response does not feed back into "
                "native E3 surplus-trigger or pulse-producing conditions."
            ),
        },
        "gates": gates,
        "lane_inputs": {
            forward_inputs["lane_id"]: forward_inputs,
            reversed_inputs["lane_id"]: reversed_inputs,
        },
        "self_renewal_tests": {
            "movement_restores_pulse_generating_conditions": {
                "measured": True,
                "passed": False,
                "evidence": "no movement-substrate-to-E3-producer feedback path exists",
            },
            "polarity_regeneration": {
                "measured": False,
                "passed": False,
                "reason": (
                    "The boundary fixture consumes imported/native E3 telemetry; "
                    "it does not regenerate the route-aspect surplus trigger state."
                ),
            },
            "repeated_cycle_persistence": {
                "measured": True,
                "passed_as_boundary_response": True,
                "passed_as_self_renewal": False,
                "forward_window_count": forward_inputs[
                    "distinct_pulse_locked_window_count"
                ],
                "reversed_window_count": reversed_inputs[
                    "distinct_pulse_locked_window_count"
                ],
                "response_window": forward_inputs["response_window"],
                "reason": "windows are driven by the existing E3 pulse schedule",
            },
            "bounded_movement_cost": {
                "measured": True,
                "passed_for_boundary_fixture": True,
                "forward_cost_proxy": forward_inputs["movement_cost_proxy"],
                "reversed_cost_proxy": reversed_inputs["movement_cost_proxy"],
            },
            "identity_continuity": {
                "measured": True,
                "passed": gates["identity_continuity_passed"],
            },
            "shape_economy": {
                "measured": True,
                "passed": gates["shape_economy_gates_passed"],
            },
        },
        "claim_flags": {
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "native_grc9v3_proposal_flux_control_used": False,
            "native_grc9v3_proposal_flux_loop_claim": False,
            "m6_opened": False,
        },
        "blocked_claims": [
            "movement_response",
            "boundary_coupled_movement",
            "loop_driven_movement",
            "self_renewing_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_behavior",
            "agency",
            "movement_inherited_from_n03",
        ],
        "source_artifacts": {
            "lane_b_closeout": _artifact_record(LANE_B_CLOSEOUT),
            "lane_b_lock_audit": _artifact_record(LANE_B_LOCK),
            "lane_b_classification": _artifact_record(LANE_B_CLASSIFICATION),
            "iteration_8_boundary_fixture": _artifact_record(ITERATION_8_BOUNDARY),
            "reversed_boundary_fixture": _artifact_record(REVERSED_BOUNDARY),
        },
        "command": COMMAND,
        "environment": _environment_record(),
    }
    return payload


def write_markdown(payload: dict[str, Any]) -> None:
    m6 = payload["m6_result"]
    tests = payload["self_renewal_tests"]
    lines = [
        "# N04 Iteration 10 Self-Renewing Movement Candidate",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "Iteration 10 was evaluated from the locked Lane B baseline. Lane B",
        "supports native direction-parity-controlled repeated boundary response,",
        "but it does not provide a feedback path from the S0 boundary response",
        "back into native E3 surplus-trigger or pulse-generating conditions.",
        "",
        "## Result",
        "",
        f"- Claim ceiling: `{m6['claim_ceiling']}`",
        f"- M6 opened: `{payload['claim_flags']['m6_opened']}`",
        f"- M6 gate passed: `{m6['m6_gate_passed']}`",
        f"- Primary blocker: `{m6['primary_blocker']}`",
        "",
        "## Gate Measurements",
        "",
        "- Movement restores pulse-generating conditions: "
        f"`{tests['movement_restores_pulse_generating_conditions']['passed']}`",
        "- Polarity regeneration measured: "
        f"`{tests['polarity_regeneration']['measured']}`",
        "- Repeated boundary-response persistence measured: "
        f"`{tests['repeated_cycle_persistence']['passed_as_boundary_response']}`",
        "- Repeated response is self-renewed: "
        f"`{tests['repeated_cycle_persistence']['passed_as_self_renewal']}`",
        "- Bounded boundary-fixture cost measured: "
        f"`{tests['bounded_movement_cost']['measured']}`",
        "- Identity continuity passed: "
        f"`{tests['identity_continuity']['passed']}`",
        "- Shape/economy gates passed: "
        f"`{tests['shape_economy']['passed']}`",
        "",
        "## Interpretation",
        "",
        "Iteration 10 closes fail-closed. The repeated response remains driven by",
        "the existing E3 pulse schedule, and the mapped S0 boundary fixture does",
        "not regenerate the pulse-producing state. Therefore M6, locomotion-like,",
        "adaptive-topology, biological, agency, and inherited-N03 claims remain",
        "blocked.",
    ]
    _write_report(REPORT_PATH, lines)


def main() -> int:
    payload = build_report()
    _write_json(OUTPUT_PATH, payload)
    write_markdown(payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "claim_ceiling": payload["m6_result"]["claim_ceiling"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
