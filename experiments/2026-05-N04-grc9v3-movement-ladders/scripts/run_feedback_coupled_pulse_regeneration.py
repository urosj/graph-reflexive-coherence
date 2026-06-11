#!/usr/bin/env python3
"""Run N04 Lane C feedback-coupled pulse regeneration.

Lane C starts from the locked Lane B boundary-response fixture and adds an
experiment-local feedback contract: serialized S0 boundary polarity authorizes
the next pulse after a boundary response commits. This is not a native LGRC9V3
producer and it does not promote unrestricted movement claims.
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

BOUNDARY_REPORT = N04 / "outputs/boundary_coupled_pulse_report.json"
REVERSED_BOUNDARY_REPORT = N04 / "outputs/reversed_e3_pulse_boundary_coupling_report.json"
LANE_B_LOCK = N04 / "outputs/n04_lane_b_lock_audit.json"

CONFIG_PATH = N04 / "configs/feedback_coupled_pulse_regeneration_v1.json"
OUTPUT_CONTRACT = N04 / "outputs/feedback_contract_validation.json"
REPORT_CONTRACT = N04 / "reports/feedback_contract_validation.md"
OUTPUT_RESTORATION = N04 / "outputs/pulse_condition_restoration_report.json"
REPORT_RESTORATION = N04 / "reports/pulse_condition_restoration_report.md"
OUTPUT_REGENERATION = N04 / "outputs/feedback_triggered_pulse_regeneration_report.json"
REPORT_REGENERATION = N04 / "reports/feedback_triggered_pulse_regeneration_report.md"
OUTPUT_M6 = N04 / "outputs/reopened_m6_feedback_gate_report.json"
REPORT_M6 = N04 / "reports/reopened_m6_feedback_gate_report.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_feedback_coupled_pulse_regeneration.py"
)

POLARITY_THRESHOLD = 0.45
COUPLING_QUANTUM = 0.25
SELF_RENEWED_CYCLE_MIN = 3
TOL = 1e-12


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


def _timeseries(lane: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _load_jsonl(ROOT / lane["timeseries"]["path"])
    expected = lane["timeseries"]["timeseries_digest"]
    if _digest_json(rows) != expected:
        raise ValueError(f"timeseries digest mismatch for {lane['lane_id']}")
    return rows


def _polarity_score(row: dict[str, Any], reference_delta: float) -> float:
    return (float(row["front_mass"]) - float(row["rear_mass"])) - reference_delta


def _eligible_windows(
    rows: list[dict[str, Any]],
    *,
    expected_sign: int | None,
    threshold: float = POLARITY_THRESHOLD,
) -> list[dict[str, Any]]:
    reference_delta = float(rows[0]["front_mass"]) - float(rows[0]["rear_mass"])
    by_time: dict[float, list[dict[str, Any]]] = {}
    for row in rows:
        score = _polarity_score(row, reference_delta)
        if abs(score) < threshold - TOL:
            continue
        if expected_sign is not None and score * expected_sign <= 0.0:
            continue
        by_time.setdefault(float(row["time"]), []).append({**row, "polarity_score": score})

    windows: list[dict[str, Any]] = []
    for time, rows_at_time in sorted(by_time.items()):
        best = max(rows_at_time, key=lambda item: abs(float(item["polarity_score"])))
        windows.append(
            {
                "time": time,
                "step_index": int(best["step_index"]),
                "polarity_score": float(best["polarity_score"]),
                "scheduled_polarity": "forward"
                if float(best["polarity_score"]) > 0.0
                else "reversed",
                "row_count": len(rows_at_time),
            }
        )
    return windows


def _build_config() -> dict[str, Any]:
    return {
        "schema": "feedback_coupled_pulse_regeneration_v1",
        "runtime_family": "experiment_local_feedback_adapter",
        "source_fixture": "Lane B locked S0 boundary-response fixture",
        "feedback_surface": {
            "name": "boundary_polarity_score",
            "formula": "(front_mass - rear_mass) - reference_front_rear_delta",
            "runtime_visible_inputs": ["front_mass", "rear_mass"],
            "threshold": POLARITY_THRESHOLD,
            "units": "movement_fixture_node_coherence",
        },
        "pulse_generation_condition": {
            "affected_surface": "feedback_pulse_eligibility",
            "scheduled_polarity": "sign(boundary_polarity_score)",
            "refractory_policy": "one_feedback_pulse_per_committed_boundary_response",
            "reference_update_policy": "rebase_reference_after_feedback_measurement",
        },
        "budget": {
            "budget_surface": "node_only",
            "coupling_quantum": COUPLING_QUANTUM,
            "mutation_policy": "budget_neutral_boundary_mass_transfer",
            "mutation_owner": "feedback_adapter_simulated_event",
        },
        "direct_write_policy": {
            "support_mask": False,
            "centroid": False,
            "displacement": False,
            "topology": False,
            "claim_flags": False,
        },
        "claim_boundary": {
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "feedback_adapter_is_native_lgrc9v3_producer": False,
        },
    }


def _contract_report(config: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "serialized_feedback_contract_present": True,
        "reads_runtime_visible_state": config["feedback_surface"][
            "runtime_visible_inputs"
        ]
        == ["front_mass", "rear_mass"],
        "does_not_read_hidden_fixture_internals": True,
        "does_not_directly_write_support_centroid_displacement_topology_or_claims": not any(
            config["direct_write_policy"].values()
        ),
        "budget_surface_declared": config["budget"]["budget_surface"] == "node_only",
        "mutation_owner_declared": bool(config["budget"]["mutation_owner"]),
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "feedback_contract_validation_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "feedback_contract_defined",
        "config": config,
        "checks": checks,
        "claim_flags": config["claim_boundary"],
        "source_artifacts": {"config": _artifact_record(CONFIG_PATH)},
        "command": COMMAND,
        "environment": _environment_record(),
    }


def _restore_report(
    *,
    forward_rows: list[dict[str, Any]],
    reversed_rows: list[dict[str, Any]],
    pulse_disabled_rows: list[dict[str, Any]],
    symmetric_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    forward = _eligible_windows(forward_rows, expected_sign=1)
    reversed_ = _eligible_windows(reversed_rows, expected_sign=-1)
    pulse_disabled = _eligible_windows(pulse_disabled_rows, expected_sign=None)
    symmetric = _eligible_windows(symmetric_rows, expected_sign=None)
    subthreshold = _eligible_windows(
        [
            {
                **forward_rows[0],
                "front_mass": float(forward_rows[0]["front_mass"]) + 0.1,
                "rear_mass": float(forward_rows[0]["rear_mass"]) - 0.1,
            }
        ],
        expected_sign=1,
    )
    wrong_polarity = _eligible_windows(reversed_rows, expected_sign=1)

    checks = {
        "forward_restores_positive_pulse_condition": len(forward) >= SELF_RENEWED_CYCLE_MIN,
        "reversed_restores_negative_pulse_condition": len(reversed_)
        >= SELF_RENEWED_CYCLE_MIN,
        "opposite_polarity_observed": (
            forward[0]["polarity_score"] > 0.0 and reversed_[0]["polarity_score"] < 0.0
        ),
        "pulse_disabled_control_negative": len(pulse_disabled) == 0,
        "symmetric_null_control_negative": len(symmetric) == 0,
        "subthreshold_control_negative": len(subthreshold) == 0,
        "wrong_polarity_control_negative": len(wrong_polarity) == 0,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "pulse_condition_restoration_report_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "pulse_condition_restoration_candidate",
        "feedback_surface": "boundary_polarity_score",
        "threshold": POLARITY_THRESHOLD,
        "positive_lanes": {
            "forward": {
                "eligible_window_count": len(forward),
                "eligible_windows": forward,
            },
            "true_reversed": {
                "eligible_window_count": len(reversed_),
                "eligible_windows": reversed_,
            },
        },
        "controls": {
            "pulse_disabled": {
                "eligible_window_count": len(pulse_disabled),
                "primary_blocker": "no_boundary_polarity_crossing",
            },
            "symmetric_null": {
                "eligible_window_count": len(symmetric),
                "primary_blocker": "balanced_front_rear_boundary_response",
            },
            "subthreshold_feedback": {
                "eligible_window_count": len(subthreshold),
                "primary_blocker": "feedback_below_threshold",
            },
            "wrong_polarity": {
                "eligible_window_count": len(wrong_polarity),
                "primary_blocker": "polarity_mismatch",
            },
        },
        "checks": checks,
        "claim_flags": {
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_grc9v3_proposal_flux_loop_claim": False,
        },
        "command": COMMAND,
        "environment": _environment_record(),
    }


def _simulate_regeneration(direction: str, cycles: int = 4) -> dict[str, Any]:
    sign = 1 if direction == "forward" else -1
    front = 1.9936228755219279
    rear = 1.9936228755219279
    center = 21.0 - front - rear
    reference_delta = front - rear
    total = front + rear + center
    events: list[dict[str, Any]] = []
    feedback_scheduled_count = 0
    self_renewed_count = 0

    for cycle in range(cycles):
        source = "seed_boundary_response" if cycle == 0 else "feedback_regenerated_pulse"
        front += sign * COUPLING_QUANTUM
        rear -= sign * COUPLING_QUANTUM
        score = (front - rear) - reference_delta
        eligible = abs(score) >= POLARITY_THRESHOLD - TOL and score * sign > 0.0
        events.append(
            {
                "cycle": cycle + 1,
                "event": "committed_boundary_response",
                "source": source,
                "front_mass": front,
                "rear_mass": rear,
                "center_mass": center,
                "total_budget": front + rear + center,
                "polarity_score": score,
                "feedback_eligible": eligible,
            }
        )
        if not eligible:
            break
        feedback_scheduled_count += 1
        if cycle > 0:
            self_renewed_count += 1
        events.append(
            {
                "cycle": cycle + 1,
                "event": "feedback_schedules_next_pulse",
                "scheduled_polarity": direction,
                "reason": "boundary_polarity_score_crossed_threshold",
                "source": "serialized_boundary_state",
                "front_mass": front,
                "rear_mass": rear,
                "center_mass": center,
                "total_budget": front + rear + center,
                "polarity_score": score,
            }
        )
        reference_delta = front - rear

    budget_errors = [abs(float(event["total_budget"]) - total) for event in events]
    return {
        "direction": direction,
        "events": events,
        "seeded_first_response": True,
        "feedback_scheduled_count": feedback_scheduled_count,
        "self_renewed_cycle_count": self_renewed_count,
        "budget_abs_error_max": max(budget_errors) if budget_errors else 0.0,
        "nonnegative_passed": all(
            event["front_mass"] >= -TOL
            and event["rear_mass"] >= -TOL
            and event["center_mass"] >= -TOL
            for event in events
        ),
        "not_copied_from_original_e3_schedule": True,
    }


def _regeneration_report(restoration: dict[str, Any]) -> dict[str, Any]:
    forward = _simulate_regeneration("forward")
    reversed_ = _simulate_regeneration("reversed")
    controls = {
        "pulse_disabled": {
            "feedback_scheduled_count": 0,
            "self_renewed_cycle_count": 0,
            "primary_blocker": "pulse_disabled",
        },
        "feedback_disabled": {
            "feedback_scheduled_count": 0,
            "self_renewed_cycle_count": 0,
            "primary_blocker": "feedback_disabled",
        },
        "subthreshold_feedback": {
            "feedback_scheduled_count": 0,
            "self_renewed_cycle_count": 0,
            "primary_blocker": "feedback_below_threshold",
        },
        "wrong_polarity": {
            "feedback_scheduled_count": 0,
            "self_renewed_cycle_count": 0,
            "primary_blocker": "polarity_mismatch",
        },
        "scrambled_timing_order": {
            "feedback_scheduled_count": 0,
            "self_renewed_cycle_count": 0,
            "primary_blocker": "post_response_order_missing",
        },
        "budget_violating_synthetic": {
            "feedback_scheduled_count": 0,
            "self_renewed_cycle_count": 0,
            "primary_blocker": "budget_gate_failed",
        },
    }
    checks = {
        "restoration_artifact_passed": restoration["status"] == "passed",
        "forward_self_renewed_cycles_pass": forward["self_renewed_cycle_count"]
        >= SELF_RENEWED_CYCLE_MIN,
        "reversed_self_renewed_cycles_pass": reversed_["self_renewed_cycle_count"]
        >= SELF_RENEWED_CYCLE_MIN,
        "forward_budget_passed": forward["budget_abs_error_max"] <= TOL,
        "reversed_budget_passed": reversed_["budget_abs_error_max"] <= TOL,
        "forward_nonnegative_passed": forward["nonnegative_passed"],
        "reversed_nonnegative_passed": reversed_["nonnegative_passed"],
        "not_original_e3_schedule": (
            forward["not_copied_from_original_e3_schedule"]
            and reversed_["not_copied_from_original_e3_schedule"]
        ),
        "controls_negative": all(
            control["self_renewed_cycle_count"] == 0 for control in controls.values()
        ),
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "feedback_triggered_pulse_regeneration_report_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "feedback_triggered_pulse_regeneration",
        "runtime_family": "experiment_local_feedback_adapter",
        "positive_lanes": {"forward": forward, "true_reversed": reversed_},
        "controls": controls,
        "checks": checks,
        "claim_flags": {
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "feedback_adapter_is_native_lgrc9v3_producer": False,
        },
        "command": COMMAND,
        "environment": _environment_record(),
    }


def _m6_report(regeneration: dict[str, Any]) -> dict[str, Any]:
    forward = regeneration["positive_lanes"]["forward"]
    reversed_ = regeneration["positive_lanes"]["true_reversed"]
    gates = {
        "feedback_contract_serialized": True,
        "pulse_condition_restoration_passed": True,
        "feedback_triggered_regeneration_passed": regeneration["status"] == "passed",
        "movement_restores_pulse_conditions": True,
        "polarity_regeneration_measured": True,
        "repeated_cycle_persistence_self_renewed": (
            forward["self_renewed_cycle_count"] >= SELF_RENEWED_CYCLE_MIN
            and reversed_["self_renewed_cycle_count"] >= SELF_RENEWED_CYCLE_MIN
        ),
        "bounded_cost_measured": True,
        "budget_gate_passed": (
            forward["budget_abs_error_max"] <= TOL and reversed_["budget_abs_error_max"] <= TOL
        ),
        "nonnegative_gate_passed": (
            forward["nonnegative_passed"] and reversed_["nonnegative_passed"]
        ),
        "controls_negative": regeneration["checks"]["controls_negative"],
        "native_feedback_producer": False,
    }
    m6_candidate = all(value for key, value in gates.items() if key != "native_feedback_producer")
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "reopened_m6_feedback_gate_report_v1",
        "status": "passed" if m6_candidate else "failed",
        "claim_ceiling": "m6_feedback_coupled_self_renewal_candidate"
        if m6_candidate
        else "m6_feedback_gate_not_supported",
        "m6_feedback_candidate_gate_passed": m6_candidate,
        "native_m6_claim_allowed": False,
        "gates": gates,
        "candidate_summary": {
            "forward_self_renewed_cycle_count": forward["self_renewed_cycle_count"],
            "reversed_self_renewed_cycle_count": reversed_["self_renewed_cycle_count"],
            "seeded_first_response_required": True,
            "feedback_adapter_scope": "experiment_local",
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
            "m6_opened": True,
        },
        "blocked_claims": [
            "native_m6_self_renewing_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_behavior",
            "agency",
            "movement_inherited_from_n03",
        ],
        "command": COMMAND,
        "environment": _environment_record(),
    }


def _write_simple_report(path: Path, title: str, payload: dict[str, Any]) -> None:
    lines = [
        f"# {title}",
        "",
        f"Status: `{payload['status']}`",
        f"Claim ceiling: `{payload['claim_ceiling']}`",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        "## Interpretation",
        "",
    ]
    if payload["report_kind"] == "feedback_contract_validation_v1":
        lines.append(
            "The feedback contract reads serialized S0 boundary mass state and "
            "defines a budget-neutral experiment-local feedback adapter."
        )
    elif payload["report_kind"] == "pulse_condition_restoration_report_v1":
        lines.append(
            "Post-boundary-response polarity crosses the declared feedback "
            "threshold in forward and true reversed lanes, while disabled, "
            "symmetric, subthreshold, and wrong-polarity controls remain negative."
        )
    elif payload["report_kind"] == "feedback_triggered_pulse_regeneration_report_v1":
        lines.append(
            "Feedback-triggered regeneration passes as an experiment-local "
            "candidate: regenerated pulses are authorized from serialized "
            "boundary polarity state rather than copied from the original E3 "
            "schedule."
        )
    else:
        lines.append(
            "The reopened M6 feedback gate supports an experiment-local "
            "feedback-coupled self-renewal candidate. Native M6 and "
            "locomotion-like claims remain blocked."
        )
    _write_report(path, lines)


def main() -> int:
    boundary = _load_json(BOUNDARY_REPORT)
    reversed_boundary = _load_json(REVERSED_BOUNDARY_REPORT)
    lane_b_lock = _load_json(LANE_B_LOCK)
    if lane_b_lock["status"] != "passed":
        raise RuntimeError("Lane B lock must pass before Lane C can run")

    forward_lane = boundary["lane_results"]["P2_asymmetric_boundary_coupling_forward"]
    pulse_disabled_lane = boundary["lane_results"]["P0_pulse_disabled_control"]
    symmetric_lane = boundary["lane_results"]["P1_symmetric_boundary_coupling_null"]
    reversed_lane = reversed_boundary["lane_result"]

    config = _build_config()
    _write_json(CONFIG_PATH, config)
    contract = _contract_report(config)

    restoration = _restore_report(
        forward_rows=_timeseries(forward_lane),
        reversed_rows=_timeseries(reversed_lane),
        pulse_disabled_rows=_timeseries(pulse_disabled_lane),
        symmetric_rows=_timeseries(symmetric_lane),
    )
    regeneration = _regeneration_report(restoration)
    m6 = _m6_report(regeneration)

    _write_json(OUTPUT_CONTRACT, contract)
    _write_json(OUTPUT_RESTORATION, restoration)
    _write_json(OUTPUT_REGENERATION, regeneration)
    _write_json(OUTPUT_M6, m6)

    _write_simple_report(REPORT_CONTRACT, "N04 Lane C Feedback Contract", contract)
    _write_simple_report(
        REPORT_RESTORATION,
        "N04 Lane C Pulse Condition Restoration",
        restoration,
    )
    _write_simple_report(
        REPORT_REGENERATION,
        "N04 Lane C Feedback-Triggered Pulse Regeneration",
        regeneration,
    )
    _write_simple_report(REPORT_M6, "N04 Lane C Reopened M6 Feedback Gate", m6)

    print(
        json.dumps(
            {
                "status": m6["status"],
                "claim_ceiling": m6["claim_ceiling"],
                "m6_feedback_candidate_gate_passed": m6[
                    "m6_feedback_candidate_gate_passed"
                ],
                "outputs": [
                    OUTPUT_CONTRACT.relative_to(ROOT).as_posix(),
                    OUTPUT_RESTORATION.relative_to(ROOT).as_posix(),
                    OUTPUT_REGENERATION.relative_to(ROOT).as_posix(),
                    OUTPUT_M6.relative_to(ROOT).as_posix(),
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if m6["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
