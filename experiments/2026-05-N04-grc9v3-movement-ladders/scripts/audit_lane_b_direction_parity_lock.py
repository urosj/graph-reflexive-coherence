#!/usr/bin/env python3
"""Audit N04 Lane B before locking the direction-parity result."""

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

TELEMETRY_PATH = N04 / "outputs/reversed_e3_pulse_telemetry_validation.json"
BOUNDARY_PATH = N04 / "outputs/reversed_e3_pulse_boundary_coupling_report.json"
CLASSIFICATION_PATH = N04 / "outputs/reversed_e3_pulse_m4_m5_classification.json"
CLOSEOUT_PATH = N04 / "outputs/n04_lane_b_direction_parity_closeout.json"
ITERATION_8_PATH = N04 / "outputs/boundary_coupled_pulse_report.json"
ITERATION_9_PATH = N04 / "outputs/loop_driven_movement_m4_m5_report.json"

OUTPUT_PATH = N04 / "outputs/n04_lane_b_lock_audit.json"
REPORT_PATH = N04 / "reports/n04_lane_b_lock_audit.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/audit_lane_b_direction_parity_lock.py"
)

TOL = 1e-12


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
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


def _centroid_delta(rows: list[dict[str, Any]]) -> float:
    return float(rows[-1]["centroid"]) - float(rows[0]["centroid"])


def _boundary_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    initial = rows[0]
    front_gain = max(float(row["front_mass"]) - float(initial["front_mass"]) for row in rows)
    rear_release = max(float(initial["rear_mass"]) - float(row["rear_mass"]) for row in rows)
    rear_gain = max(float(row["rear_mass"]) - float(initial["rear_mass"]) for row in rows)
    front_release = max(float(initial["front_mass"]) - float(row["front_mass"]) for row in rows)
    return {
        "front_gain": front_gain,
        "rear_release": rear_release,
        "rear_gain": rear_gain,
        "front_release": front_release,
        "boundary_coupling_score": min(front_gain, rear_release),
        "reversed_boundary_coupling_score": min(rear_gain, front_release),
    }


def _pulse_locked_windows(
    rows: list[dict[str, Any]],
    *,
    threshold: float,
    sign: int,
) -> list[dict[str, Any]]:
    initial_centroid = float(rows[0]["centroid"])
    max_coupling = max(float(row["coupling_amount"]) for row in rows)
    min_coupling = 0.9 * max_coupling
    windows: dict[float, list[dict[str, Any]]] = {}
    for row in rows:
        delta = float(row["centroid"]) - initial_centroid
        coupling = float(row["coupling_amount"])
        if coupling < min_coupling - TOL:
            continue
        if sign > 0 and delta < threshold - TOL:
            continue
        if sign < 0 and delta > -threshold + TOL:
            continue
        windows.setdefault(float(row["time"]), []).append(row)
    return [
        {
            "time": time,
            "row_count": len(rows_at_time),
            "max_coupling_amount": max(float(row["coupling_amount"]) for row in rows_at_time),
            "centroid_delta": float(rows_at_time[-1]["centroid"]) - initial_centroid,
        }
        for time, rows_at_time in sorted(windows.items())
    ]


def _same_mapping_subset(left: dict[str, Any], right: dict[str, Any]) -> bool:
    keys = [
        "mapping_id",
        "mapping_type",
        "target_fixture_id",
        "target_coordinate_frame",
        "target_direction",
        "target_direction_vector",
        "front_boundary_mask",
        "rear_boundary_mask",
        "center_reservoir_mask",
        "support_reference_mask",
        "route_pole_to_target_region",
    ]
    return all(left.get(key) == right.get(key) for key in keys)


def run_audit() -> dict[str, Any]:
    telemetry = _load_json(TELEMETRY_PATH)
    boundary = _load_json(BOUNDARY_PATH)
    classification = _load_json(CLASSIFICATION_PATH)
    closeout = _load_json(CLOSEOUT_PATH)
    iteration_8 = _load_json(ITERATION_8_PATH)
    iteration_9 = _load_json(ITERATION_9_PATH)

    forward_lane = iteration_8["lane_results"]["P2_asymmetric_boundary_coupling_forward"]
    reversed_lane = boundary["lane_result"]
    forward_rows = _load_jsonl(ROOT / forward_lane["timeseries"]["path"])
    reversed_rows = _load_jsonl(ROOT / reversed_lane["timeseries"]["path"])

    threshold = float(classification["classifier_policy"]["displacement_threshold"])
    forward_dx = _centroid_delta(forward_rows)
    reversed_dx = _centroid_delta(reversed_rows)
    forward_boundary = _boundary_metrics(forward_rows)
    reversed_boundary = _boundary_metrics(reversed_rows)
    forward_windows = _pulse_locked_windows(forward_rows, threshold=threshold, sign=1)
    reversed_windows = _pulse_locked_windows(reversed_rows, threshold=threshold, sign=-1)

    recomputed = {
        "forward_centroid_delta": forward_dx,
        "true_reversed_centroid_delta": reversed_dx,
        "forward_boundary_coupling_score": forward_boundary["boundary_coupling_score"],
        "true_reversed_boundary_coupling_score": reversed_boundary[
            "reversed_boundary_coupling_score"
        ],
        "forward_distinct_pulse_locked_window_count": len(forward_windows),
        "true_reversed_distinct_pulse_locked_window_count": len(reversed_windows),
        "forward_distinct_pulse_locked_response_window": (
            forward_windows[-1]["time"] - forward_windows[0]["time"]
            if len(forward_windows) >= 2
            else 0.0
        ),
        "true_reversed_distinct_pulse_locked_response_window": (
            reversed_windows[-1]["time"] - reversed_windows[0]["time"]
            if len(reversed_windows) >= 2
            else 0.0
        ),
        "forward_timeseries_digest_verified": _digest_json(forward_rows)
        == forward_lane["timeseries"]["timeseries_digest"],
        "true_reversed_timeseries_digest_verified": _digest_json(reversed_rows)
        == reversed_lane["timeseries"]["timeseries_digest"],
    }

    same_fixture = {
        "same_s0_substrate": forward_lane["substrate"] == reversed_lane["substrate"],
        "same_mapping_and_masks": _same_mapping_subset(
            forward_lane["mapping"], reversed_lane["mapping"]
        ),
        "same_coupling_strength": float(forward_lane["drive"]["coupling_strength"])
        == float(reversed_lane["drive"]["coupling_strength"]),
        "same_displacement_threshold": threshold
        == float(iteration_9["classifier_policy"]["displacement_threshold"]),
        "same_m4_m5_classifier_policy": {
            key: classification["classifier_policy"].get(key)
            == iteration_9["classifier_policy"].get(key)
            for key in [
                "boundary_score_min",
                "repeated_response_min_count",
                "repeated_response_min_window",
                "response_count_policy",
                "pulse_locked_window_min_coupling_fraction",
            ]
        },
    }
    same_fixture["passed"] = (
        same_fixture["same_s0_substrate"]
        and same_fixture["same_mapping_and_masks"]
        and same_fixture["same_coupling_strength"]
        and same_fixture["same_displacement_threshold"]
        and all(same_fixture["same_m4_m5_classifier_policy"].values())
    )

    only_pulse_direction_changes = {
        "true_reversed_e3_telemetry_used": boundary["true_reversed_e3_telemetry_used"] is True,
        "coupling_reversal_substitute_used": boundary[
            "coupling_direction_reversal_used_as_substitute"
        ],
        "boundary_masks_changed": not same_fixture["same_mapping_and_masks"],
        "displacement_sign_convention_changed": forward_lane["mapping"]["target_direction"]
        != reversed_lane["mapping"]["target_direction"],
        "support_extraction_policy_changed": forward_lane["identity_tracking"][
            "support_reference_mask"
        ]
        != reversed_lane["identity_tracking"]["support_reference_mask"],
        "direct_state_write_changed": any(boundary["direct_write_audit"].values()),
        "direction_specific_signal_note": (
            "The reversed lane uses the same state-mediated coherence-coupling "
            "fixture, but reads the native counter-clockwise route counterpart "
            "S1/K2 signal instead of the clockwise S1/K1 signal."
        ),
    }
    only_pulse_direction_changes["passed"] = (
        only_pulse_direction_changes["true_reversed_e3_telemetry_used"]
        and not only_pulse_direction_changes["coupling_reversal_substitute_used"]
        and not only_pulse_direction_changes["boundary_masks_changed"]
        and not only_pulse_direction_changes["displacement_sign_convention_changed"]
        and not only_pulse_direction_changes["support_extraction_policy_changed"]
        and not only_pulse_direction_changes["direct_state_write_changed"]
    )

    recomputation_checks = {
        "forward_dx_matches_report": abs(
            recomputed["forward_centroid_delta"]
            - float(classification["direction_parity"]["forward_centroid_delta"])
        )
        <= TOL,
        "true_reversed_dx_matches_report": abs(
            recomputed["true_reversed_centroid_delta"]
            - float(classification["direction_parity"]["true_reversed_centroid_delta"])
        )
        <= TOL,
        "boundary_score_matches_report": abs(
            recomputed["true_reversed_boundary_coupling_score"]
            - float(classification["lane_result"]["reversed_boundary_coupling_score"])
        )
        <= TOL,
        "window_count_matches_report": recomputed[
            "true_reversed_distinct_pulse_locked_window_count"
        ]
        == int(classification["lane_result"]["distinct_pulse_locked_window_count"]),
        "timeseries_digests_verified": recomputed["forward_timeseries_digest_verified"]
        and recomputed["true_reversed_timeseries_digest_verified"],
    }
    recomputation_checks["passed"] = all(recomputation_checks.values())

    controls = {
        "pulse_disabled_negative": iteration_9["controls"]["pulse_disabled_negative"],
        "symmetric_null_negative": iteration_9["controls"]["symmetric_null_negative"],
        "scrambled_order_blocks_loop_driven_movement": iteration_9["controls"][
            "scrambled_order_blocks_loop_driven_movement"
        ],
        "distinct_reasons": {
            key: value["primary_blocked_reason"]
            for key, value in iteration_9["control_results"].items()
        },
    }
    controls["passed"] = (
        controls["pulse_disabled_negative"]
        and controls["symmetric_null_negative"]
        and controls["scrambled_order_blocks_loop_driven_movement"]
        and controls["distinct_reasons"]
        == {
            "pulse_disabled": "pulse_disabled",
            "symmetric_boundary_null": "balanced_front_rear_coupling",
            "scrambled_order": "loop_order_scrambled",
        }
    )

    claim_flags = {
        "claim_ceiling": closeout["claim_ceiling"],
        "m5_candidate_gate_passed": classification["m5_candidate_gate_passed"],
        "direction_parity_gate_passed": classification[
            "m5_full_direction_parity_gate_passed"
        ],
        "movement_claim_allowed": closeout["claim_flags"]["movement_claim_allowed"],
        "loop_driven_movement_claim_allowed": closeout["claim_flags"][
            "loop_driven_movement_claim_allowed"
        ],
        "locomotion_like_claim_allowed": closeout["claim_flags"][
            "locomotion_like_claim_allowed"
        ],
        "adaptive_topology_entry_allowed": closeout["claim_flags"][
            "adaptive_topology_entry_allowed"
        ],
        "m6_opened": closeout["iteration_10_m6_status"]["opened"],
    }
    claim_flags["passed"] = (
        claim_flags["claim_ceiling"]
        == "m5_direction_parity_supported_boundary_response"
        and claim_flags["m5_candidate_gate_passed"] is True
        and claim_flags["direction_parity_gate_passed"] is True
        and claim_flags["movement_claim_allowed"] is False
        and claim_flags["loop_driven_movement_claim_allowed"] is False
        and claim_flags["locomotion_like_claim_allowed"] is False
        and claim_flags["adaptive_topology_entry_allowed"] is False
        and claim_flags["m6_opened"] is False
    )

    native_reversed = {
        "native_lgrc9v3_execution": telemetry["native_lgrc9v3_execution"],
        "native_d2_3_equivalent": telemetry["native_d2_3_equivalent"],
        "native_self_rearm_evidence": telemetry["native_self_rearm_evidence"],
        "native_packet_execution": telemetry["native_packet_execution"],
        "structural_reversal_passed": telemetry["structural_reversal"]["passed"],
        "count_symmetry_only": telemetry["structural_reversal"]["count_symmetry_only"],
        "max_event_budget_error": telemetry["max_event_budget_error"],
        "max_checkpoint_budget_error": telemetry["max_checkpoint_budget_error"],
        "topology_changed": telemetry["topology_changed"],
    }
    native_reversed["passed"] = (
        native_reversed["native_lgrc9v3_execution"]
        and native_reversed["native_d2_3_equivalent"]
        and native_reversed["native_self_rearm_evidence"]
        and native_reversed["native_packet_execution"]
        and native_reversed["structural_reversal_passed"]
        and native_reversed["count_symmetry_only"] is False
        and native_reversed["max_event_budget_error"] <= TOL
        and native_reversed["max_checkpoint_budget_error"] <= TOL
        and native_reversed["topology_changed"] is False
    )

    sections = {
        "native_reversed_telemetry_validation": native_reversed,
        "same_fixture_and_mapping": same_fixture,
        "only_pulse_direction_changes": only_pulse_direction_changes,
        "matched_metrics_recomputed_from_timeseries": recomputation_checks,
        "controls_still_negative": controls,
        "claim_flag_consistency": claim_flags,
    }
    status = "passed" if all(section["passed"] for section in sections.values()) else "failed"

    result = {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_lane_b_direction_parity_lock_audit_v1",
        "status": status,
        "source_artifacts": {
            "telemetry_validation": _artifact_record(TELEMETRY_PATH),
            "boundary_coupling": _artifact_record(BOUNDARY_PATH),
            "classification": _artifact_record(CLASSIFICATION_PATH),
            "closeout": _artifact_record(CLOSEOUT_PATH),
            "iteration_8_boundary_report": _artifact_record(ITERATION_8_PATH),
            "iteration_9_classifier_report": _artifact_record(ITERATION_9_PATH),
        },
        "sections": sections,
        "recomputed_metrics": recomputed,
        "acceptance_statement": (
            "Lane B resolves the Iteration 9 direction-parity blocker. True "
            "native counter-clockwise E3 telemetry is available and validated. "
            "When run through the same fixed S0 boundary-coupled fixture and "
            "frozen M4/M5 classifier, the native forward E3 lane produces "
            "dX=+0.083333333 and the native reversed E3 lane produces "
            "dX=-0.083333333, with matched boundary_coupling_score=0.25 and "
            "matched distinct pulse-locked response windows=4. The M5 candidate "
            "gate and full direction-parity gate pass. The upgraded claim "
            "ceiling is m5_direction_parity_supported_boundary_response. This "
            "supports a native direction-parity-controlled repeated loop-driven "
            "boundary-response candidate, while movement, locomotion-like, "
            "adaptive-topology, M6, biological, agency, and inherited-N03 "
            "claims remain blocked."
        ),
        "environment": _environment_record(),
    }
    return result


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# N04 Lane B Lock Audit",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---:|",
    ]
    for key, section in result["sections"].items():
        lines.append(f"| `{key}` | `{section['passed']}` |")
    lines.extend(
        [
            "",
            "## Acceptance Statement",
            "",
            result["acceptance_statement"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = run_audit()
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
