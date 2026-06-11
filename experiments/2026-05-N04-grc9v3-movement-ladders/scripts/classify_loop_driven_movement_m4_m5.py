"""Classify N04 Iteration 9 M4-M5 loop-driven movement gates.

This classifier consumes the Iteration 8 boundary-coupled pulse fixture
artifacts. It does not introduce a new coupling mechanism. The classifier can
identify M4/M5 candidates, but full loop-driven movement claims remain blocked
unless the required controls are present.
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

BOUNDARY_REPORT_PATH = N04 / "outputs/boundary_coupled_pulse_report.json"
ITERATION_5_PATH = N04 / "outputs/fixed_substrate_tranche_a_report.json"

OUTPUT_PATH = N04 / "outputs/loop_driven_movement_m4_m5_report.json"
REPORT_PATH = N04 / "reports/loop_driven_movement_m4_m5_report.md"

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


def _response_samples(
    rows: list[dict[str, Any]],
    initial_centroid: float,
    threshold: float,
    sign: int,
) -> list[dict[str, Any]]:
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
                "step_indices": sorted(
                    {int(row["step_index"]) for row in rows_at_time}
                ),
                "max_coupling_amount": max(
                    float(row["coupling_amount"]) for row in rows_at_time
                ),
                "centroid_delta": (
                    float(rows_at_time[-1]["centroid"]) - initial_centroid
                ),
            }
        )
    return distinct


def _classify_lane(
    lane: dict[str, Any],
    threshold: float,
) -> dict[str, Any]:
    metrics = lane["movement_metrics"]
    timeseries_path = ROOT / lane["timeseries"]["path"]
    rows = _load_jsonl(timeseries_path)
    initial_centroid = float(rows[0]["centroid"])
    centroid_delta = float(metrics["centroid_delta_total"])
    sign = 1 if centroid_delta >= 0.0 else -1
    max_observed_coupling = max(float(row["coupling_amount"]) for row in rows)
    pulse_locked_window_min_coupling = (
        max_observed_coupling * PULSE_LOCKED_WINDOW_MIN_COUPLING_FRACTION
    )
    response_samples = _response_samples(rows, initial_centroid, threshold, sign)
    response_times = [float(row["time"]) for row in response_samples]
    repeated_window = (
        max(response_times) - min(response_times) if len(response_times) >= 2 else 0.0
    )
    distinct_windows = _distinct_pulse_locked_windows(
        rows, initial_centroid, threshold, sign, pulse_locked_window_min_coupling
    )
    distinct_window_times = [float(window["time"]) for window in distinct_windows]
    distinct_response_window = (
        max(distinct_window_times) - min(distinct_window_times)
        if len(distinct_window_times) >= 2
        else 0.0
    )

    digest_verified = _digest_json(rows) == lane["timeseries"]["timeseries_digest"]
    hard_gates = {
        "budget_gate_passed": lane["gates"]["budget_gate_passed"] is True,
        "nonnegative_gate_passed": lane["gates"]["nonnegative_gate_passed"] is True,
        "direct_write_gate_passed": lane["gates"]["direct_write_gate_passed"] is True,
        "timeseries_digest_verified": digest_verified,
        "topology_gate_passed": lane["topology"]["topology_changed"] is False,
        "movement_inherited_gate_passed": lane["loop_dependency"][
            "movement_claim_inherited"
        ]
        is False,
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
        and distinct_response_window >= REPEATED_RESPONSE_MIN_WINDOW
        and lane["native_lgrc9v3_e3_pulse_used"] is True
    )

    if m5_passed:
        movement_level = "M5_repeated_loop_driven_boundary_response_candidate"
    elif m4_passed:
        movement_level = "M4_coordinated_boundary_response_candidate"
    elif displacement_gate:
        movement_level = "M1_displacement_without_boundary_coupling"
    else:
        movement_level = "M0_no_threshold_displacement"

    failed = [
        key
        for key, value in {
            **hard_gates,
            "displacement_gate_passed": displacement_gate,
            "m4_boundary_coordination_gate_passed": boundary_gate,
            "m5_repeated_response_gate_passed": m5_passed,
        }.items()
        if not value
    ]
    blocker_labels = {
        "budget_gate_passed": "budget_gate_failed",
        "nonnegative_gate_passed": "nonnegative_gate_failed",
        "direct_write_gate_passed": "direct_write_gate_failed",
        "timeseries_digest_verified": "timeseries_digest_failed",
        "topology_gate_passed": "topology_changed",
        "movement_inherited_gate_passed": "movement_inherited_from_n03",
        "displacement_gate_passed": "displacement_below_threshold",
        "m4_boundary_coordination_gate_passed": "m4_boundary_coordination_failed",
        "m5_repeated_response_gate_passed": "m5_repeated_response_failed",
    }
    primary_blocker = (
        blocker_labels[failed[0]] if failed else "claim_parity_controls_not_complete"
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
        "directional_boundary_release_mass": metrics[
            "directional_boundary_release_mass"
        ],
        "boundary_coupling_score": metrics["boundary_coupling_score"],
        "reversed_boundary_coupling_score": metrics["reversed_boundary_coupling_score"],
        "response_sample_count": len(response_samples),
        "response_time_window": repeated_window,
        "response_count_policy": "distinct_pulse_locked_windows",
        "diagnostic_threshold_sample_count": len(response_samples),
        "count_persistent_plateau_as_one": True,
        "response_threshold_epsilon": RESPONSE_THRESHOLD_EPSILON,
        "max_observed_coupling": max_observed_coupling,
        "pulse_locked_window_min_coupling_fraction": PULSE_LOCKED_WINDOW_MIN_COUPLING_FRACTION,
        "pulse_locked_window_min_coupling": pulse_locked_window_min_coupling,
        "distinct_pulse_locked_window_count": len(distinct_windows),
        "distinct_pulse_locked_response_window": distinct_response_window,
        "distinct_pulse_locked_windows": distinct_windows,
        "response_window_units": "native_E3_telemetry_time",
        "window_policy": "frozen_iteration_9_classifier_policy",
        "window_deduplication_key": "time",
        "window_deduplication_limitation": "distinct co-temporal pulse peaks would be collapsed; current E3 peak windows occur at distinct times",
        "hard_gates": hard_gates,
        "displacement_gate_passed": displacement_gate,
        "m4_boundary_coordination_gate_passed": boundary_gate,
        "m5_repeated_response_gate_passed": m5_passed,
        "failed_gates": failed,
        "primary_blocker": primary_blocker,
        "timeseries_path": lane["timeseries"]["path"],
    }


def _scrambled_order_control(
    forward: dict[str, Any],
    threshold: float,
) -> dict[str, Any]:
    """Classifier sanity control: same magnitudes, invalid pulse order."""

    return {
        "control_id": "scrambled_order_control_from_forward_lane",
        "source_lane_id": forward["lane_id"],
        "packet_activity_present": True,
        "magnitude_profile_reused": True,
        "canonical_pulse_order_valid": False,
        "empirical_fixture_lane": False,
        "control_kind": "synthetic_classifier_sanity_check",
        "empirical_scrambled_pulse_fixture_status": "deferred",
        "displacement_threshold": threshold,
        "movement_level": "M0_blocked_scrambled_order",
        "m4_passed": False,
        "m5_passed": False,
        "primary_blocker": "canonical_pulse_order_failed",
        "movement_claim_allowed": False,
    }


def run_classifier() -> dict[str, Any]:
    boundary_report = _load_json(BOUNDARY_REPORT_PATH)
    iteration_5 = _load_json(ITERATION_5_PATH)
    threshold = float(
        iteration_5["displacement_threshold_policy"]["effective_displacement_min"]
    )
    lane_results = {
        lane_id: _classify_lane(lane, threshold)
        for lane_id, lane in boundary_report["lane_results"].items()
    }
    forward = lane_results["P2_asymmetric_boundary_coupling_forward"]
    reversed_lane = lane_results["P2_asymmetric_boundary_coupling_reversed"]
    disabled = lane_results["P0_pulse_disabled_control"]
    symmetric = lane_results["P1_symmetric_boundary_coupling_null"]
    scrambled = _scrambled_order_control(forward, threshold)

    coupling_reversal_symmetry = {
        "passed": (
            forward["m5_passed"]
            and reversed_lane["m5_passed"]
            and forward["centroid_delta_total"] * reversed_lane["centroid_delta_total"]
            < 0.0
            and abs(
                abs(forward["centroid_delta_total"])
                - abs(reversed_lane["centroid_delta_total"])
            )
            <= 1e-12
        ),
        "scope": "coupling_direction_reversal_only",
        "uses_reversed_e3_telemetry": False,
    }
    true_reversed_e3_pulse_control = {
        "available": False,
        "status": "not_available_in_native_e3_animation_telemetry",
        "claim_impact": "blocks_full_direction_parity_claim_but_not_forward_m5_candidate",
    }
    controls = {
        "pulse_disabled_negative": disabled["m4_passed"] is False
        and disabled["m5_passed"] is False,
        "symmetric_null_negative": symmetric["m4_passed"] is False
        and symmetric["m5_passed"] is False,
        "coupling_reversal_symmetry": coupling_reversal_symmetry["passed"],
        "scrambled_order_blocks_loop_driven_movement": scrambled["m5_passed"] is False,
        "true_reversed_e3_pulse_control_available": true_reversed_e3_pulse_control[
            "available"
        ],
    }
    control_results = {
        "pulse_disabled": {
            "m4_passed": disabled["m4_passed"],
            "m5_passed": disabled["m5_passed"],
            "primary_blocked_reason": "pulse_disabled",
        },
        "symmetric_boundary_null": {
            "m4_passed": symmetric["m4_passed"],
            "m5_passed": symmetric["m5_passed"],
            "primary_blocked_reason": "balanced_front_rear_coupling",
        },
        "scrambled_order": {
            "m4_passed": scrambled["m4_passed"],
            "m5_passed": scrambled["m5_passed"],
            "primary_blocked_reason": "loop_order_scrambled",
        },
    }

    candidate_lanes = [
        lane_id for lane_id, row in lane_results.items() if row["m5_passed"]
    ]
    full_claim_controls_passed = all(controls.values())
    m5_candidate_supported = bool(candidate_lanes)

    claim_flags = {
        "movement_claim_allowed": False,
        "boundary_coupled_movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "movement_claim_inherited_from_n03": False,
        "native_lgrc9v3_e3_pulse_used": True,
        "native_grc9v3_proposal_flux_loop_claim": False,
        "native_grc9v3_proposal_flux_control_used": False,
    }
    if m5_candidate_supported and full_claim_controls_passed:
        claim_ceiling = "m5_loop_driven_movement_supported"
        claim_flags["movement_claim_allowed"] = True
        claim_flags["boundary_coupled_movement_claim_allowed"] = True
        claim_flags["loop_driven_movement_claim_allowed"] = True
        primary_result = "m5_loop_driven_movement_supported"
    elif m5_candidate_supported:
        claim_ceiling = "m5_candidate_control_limited"
        primary_result = "m5_candidate_blocked_by_incomplete_direction_parity_controls"
    else:
        claim_ceiling = "m4_m5_not_supported"
        primary_result = "no_loop_driven_movement_candidate"

    checks = {
        "iteration_8_dependency_passed": boundary_report["status"] == "passed",
        "iteration_8_boundary_report_uses_external_timeseries": all(
            isinstance(lane.get("timeseries"), dict)
            and "path" in lane["timeseries"]
            and "timeseries_digest" in lane["timeseries"]
            for lane in boundary_report["lane_results"].values()
        ),
        "pulse_disabled_control_negative": controls["pulse_disabled_negative"],
        "symmetric_null_control_negative": controls["symmetric_null_negative"],
        "coupling_reversal_symmetry_passed": controls["coupling_reversal_symmetry"],
        "scrambled_order_control_negative": controls[
            "scrambled_order_blocks_loop_driven_movement"
        ],
        "true_reversed_e3_pulse_control_recorded": True,
        "candidate_lanes_present": m5_candidate_supported,
        "full_claim_controls_passed": full_claim_controls_passed,
        "claims_fail_closed_when_controls_incomplete": (
            not full_claim_controls_passed
            and claim_flags["loop_driven_movement_claim_allowed"] is False
        )
        or full_claim_controls_passed,
    }
    required_status_checks = {
        key: checks[key]
        for key in [
            "iteration_8_dependency_passed",
            "iteration_8_boundary_report_uses_external_timeseries",
            "pulse_disabled_control_negative",
            "symmetric_null_control_negative",
            "coupling_reversal_symmetry_passed",
            "scrambled_order_control_negative",
            "true_reversed_e3_pulse_control_recorded",
            "candidate_lanes_present",
            "claims_fail_closed_when_controls_incomplete",
        ]
    }

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "loop_driven_movement_m4_m5_v1",
        "status": "passed" if all(required_status_checks.values()) else "failed",
        "runtime_family": "experiment_local",
        "execution_surface": "surface_c_lgrc9v3_e3_pulse_boundary_coupling_adapter",
        "budget_surface": "node_only",
        "source_artifacts": {
            "boundary_coupled_pulse_report": _artifact_record(BOUNDARY_REPORT_PATH),
            "iteration_5_fixed_substrate_tranche": _artifact_record(ITERATION_5_PATH),
        },
        "source_artifact_requirements": {
            "boundary_report_external_timeseries_required": True,
            "boundary_report_sha256_consumed": _sha256(BOUNDARY_REPORT_PATH),
        },
        "classifier_policy": {
            "displacement_threshold": threshold,
            "boundary_score_min": BOUNDARY_SCORE_MIN,
            "repeated_response_min_count": REPEATED_RESPONSE_MIN_COUNT,
            "repeated_response_min_window": REPEATED_RESPONSE_MIN_WINDOW,
            "response_count_policy": "distinct_pulse_locked_windows",
            "pulse_locked_window_min_coupling_policy": "fraction_of_lane_max_observed_coupling",
            "pulse_locked_window_min_coupling_fraction": PULSE_LOCKED_WINDOW_MIN_COUPLING_FRACTION,
            "response_threshold_epsilon": RESPONSE_THRESHOLD_EPSILON,
            "count_persistent_plateau_as_one": True,
            "response_window_units": "native_E3_telemetry_time",
            "window_deduplication_key": "time",
            "window_deduplication_limitation": "co-temporal distinct pulse peaks would be collapsed by this policy; current E3 peak windows are at distinct times",
            "m4_m5_gate_scope": "boundary_response_structure",
            "relationship_to_m0_m3": "parallel_boundary_response_ladder_not_identity_shape_superset",
            "full_movement_claim_requires_m0_m3_identity_shape_and_m4_m5_direction_parity": True,
            "response_count_interpretation": "window count is coupled to E3 pulse-cycle structure; it validates repeated pulse-locked response, not independent substrate responses between pulses or post-pulse persistence",
            "m4_definition": "threshold displacement plus coordinated directional front/rear boundary exchange under hard gates",
            "m5_definition": "M4 plus repeated distinct pulse-locked response windows over a finite native E3 telemetry-time interval",
        },
        "claim_ceiling": claim_ceiling,
        "primary_result": primary_result,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "full_loop_driven_movement_without_true_reversed_e3_pulse_control",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "movement_inherited_from_n03",
            "biological_or_agency_claim",
        ],
        "controls": controls,
        "control_results": control_results,
        "coupling_reversal_symmetry": coupling_reversal_symmetry,
        "true_reversed_e3_pulse_control": true_reversed_e3_pulse_control,
        "scrambled_order_control": scrambled,
        "scrambled_order_control_scope": {
            "empirical_fixture_lane": False,
            "classification": "synthetic_classifier_sanity_check",
            "deferred_empirical_control": "scrambled_E3_pulse_fixture_lane",
        },
        "lane_results": lane_results,
        "candidate_lanes": candidate_lanes,
        "s0_only_scope": {
            "movement_substrate": "S0_chain_v1",
            "s1_ring_mapping_used": False,
            "s1_ring_mapping_status": "deferred",
        },
        "m6_status": {
            "opened": False,
            "polarity_regeneration_measured": False,
            "movement_restores_pulse_conditions": False,
            "reason": "full_m5_movement_support_blocked_by_missing_true_reversed_e3_pulse_control",
        },
        "direct_write_audit": {
            "direct_support_mask_write": False,
            "direct_boundary_label_write": False,
            "direct_centroid_write": False,
            "direct_displacement_write": False,
            "direct_topology_write": False,
        },
        "identity_shape_gate_scope": {
            "m0_m3_identity_shape_gates_rerun_here": False,
            "m4_m5_classifies_boundary_response_structure": True,
            "full_movement_claim_requires_identity_shape_support": True,
        },
        "budget_pipeline": {
            "native_e3_budget_surface": "node_plus_packet",
            "movement_fixture_budget_surface": "node_only",
            "coupling_budget_neutral": all(
                lane["hard_gates"]["budget_gate_passed"]
                for lane in lane_results.values()
            ),
            "movement_fixture_budget_abs_error_max": max(
                boundary_report["lane_results"][lane_id]["conservation"][
                    "budget_abs_error_max"
                ]
                for lane_id in lane_results
            ),
            "nonnegative_gate_passed": all(
                lane["hard_gates"]["nonnegative_gate_passed"]
                for lane in lane_results.values()
            ),
        },
        "checks": checks,
        "required_status_checks": required_status_checks,
        "summary": {
            "m5_candidate_supported": m5_candidate_supported,
            "full_claim_controls_passed": full_claim_controls_passed,
            "forward_level": forward["movement_level"],
            "reversed_coupling_level": reversed_lane["movement_level"],
            "pulse_disabled_level": disabled["movement_level"],
            "symmetric_null_level": symmetric["movement_level"],
            "interpretation": "Iteration 9 finds M5-style repeated boundary-response candidates in the asymmetric coupling lanes, but full loop-driven movement claims remain blocked because native true reversed-E3-pulse telemetry is not available in the current artifact set.",
        },
        "environment": _environment_record(),
    }


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Loop-Driven Movement M4-M5 Classifier",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/classify_loop_driven_movement_m4_m5.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- Claim ceiling: `{result['claim_ceiling']}`",
        f"- Budget surface: `{result['budget_surface']}`",
        f"- Primary result: `{result['primary_result']}`",
        f"- M5 candidate supported: `{result['summary']['m5_candidate_supported']}`",
        f"- Full claim controls passed: `{result['summary']['full_claim_controls_passed']}`",
        f"- Loop-driven movement claim allowed: `{result['claim_flags']['loop_driven_movement_claim_allowed']}`",
        f"- True reversed E3 pulse control: `{result['true_reversed_e3_pulse_control']['status']}`",
        f"- Boundary report SHA-256 consumed: `{result['source_artifact_requirements']['boundary_report_sha256_consumed']}`",
        "",
        "## Lanes",
        "",
        "| Lane | Level | M4 | M5 | dX | Response Count | Window | Primary Blocker |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for lane_id, lane in result["lane_results"].items():
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{:.9f}` | `{}` | `{:.3f}` | `{}` |".format(
                lane_id,
                lane["movement_level"],
                lane["m4_passed"],
                lane["m5_passed"],
                lane["centroid_delta_total"],
                lane["distinct_pulse_locked_window_count"],
                lane["distinct_pulse_locked_response_window"],
                lane["primary_blocker"],
            )
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Control | Passed |",
            "|---|---:|",
        ]
    )
    for key, value in result["controls"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            result["summary"]["interpretation"],
            "",
            "Response counts use `distinct_pulse_locked_windows`; repeated samples on the same plateau are counted as one window.",
            "",
            "`pulse_locked_window_min_coupling` is derived per lane as `0.9 * max_observed_coupling`; it is not a fixed absolute coupling threshold.",
            "",
            "The scrambled-order control is a synthetic classifier sanity check, not an empirical scrambled telemetry fixture lane. An empirical scrambled-pulse fixture remains deferred.",
            "",
            "M4/M5 gates classify boundary-response structure. They do not replace the M0-M3 identity/shape ladder; a full movement claim would require both identity/shape support and completed M4/M5 direction-parity controls.",
            "",
            "The distinct pulse-locked window count is coupled to the E3 pulse-cycle structure. It validates repeated pulse-locked responses, not substrate response between pulses or post-pulse persistence.",
            "",
            "The classifier preserves the positive boundary-response signal, but it keeps movement, loop-driven movement, locomotion-like, adaptive-topology, biological, and agency claims blocked until the missing native true reversed-E3-pulse control is available.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = run_classifier()
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
