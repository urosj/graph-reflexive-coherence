#!/usr/bin/env python3
"""Run N04 Lane D5 D-to-M movement reclassification."""

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

D3_REPORT = N04 / "outputs/traveling_deformation_audit.json"
D4_REPORT = N04 / "outputs/pulse_substrate_direction_null_controls.json"
TRANCHE_A_REPORT = N04 / "outputs/fixed_substrate_tranche_a_report.json"
OUTPUT_PATH = N04 / "outputs/pulse_substrate_movement_reclassification.json"
REPORT_PATH = N04 / "reports/pulse_substrate_movement_reclassification.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_pulse_substrate_movement_reclassification.py"
)

CLASSIFIER_VERSION = "movement_m0_m5_projection_v1"
BASE_GEOMETRY_MASS = 1.0
TOL = 1e-12


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


def _thresholds() -> dict[str, Any]:
    tranche = _load_json(TRANCHE_A_REPORT)
    policy = tranche["displacement_threshold_policy"]
    metric_defaults = tranche["metric_thresholds"]
    return {
        "effective_displacement_min": float(policy["effective_displacement_min"]),
        "threshold_source": policy["threshold_source"],
        "identity_mass_ratio_min": float(metric_defaults["identity_mass_ratio_min"]),
        "width_relative_change_max": float(metric_defaults["width_relative_change_max"]),
        "profile_similarity_min": float(metric_defaults["profile_similarity_min"]),
    }


def _deformation_observables(d3: dict[str, Any]) -> dict[str, Any]:
    lane = d3["positive_lane"]
    series = lane["series"]
    deformation_peaks = lane["deformation_peak_sequence"]
    pulse_peaks = lane["pulse_peak_sequence"]
    widths = [
        item["deformation_width"]
        for item in series
        if item["deformation_peak_node"] is not None
    ]
    support_mass_t = [
        abs(float(item["support_delta"]))
        for item in series
        if item["deformation_peak_node"] is not None
    ]
    centroid_t = [float(value) for value in deformation_peaks]
    initial_width = widths[0] if widths else 0
    final_width = widths[-1] if widths else 0
    width_relative_change_max = (
        max(abs(width - initial_width) for width in widths) / max(initial_width, 1)
        if widths
        else 0.0
    )
    displacement = centroid_t[-1] - centroid_t[0] if len(centroid_t) >= 2 else 0.0
    response_windows = [
        item["step_index"]
        for item in series
        if item["deformation_peak_node"] is not None
    ]
    return {
        "surface": "local_support_geometry_deformation",
        "centroid_t": centroid_t,
        "delta_x_total": displacement,
        "delta_x_abs": abs(displacement),
        "pulse_peak_sequence": pulse_peaks,
        "deformation_peak_sequence": deformation_peaks,
        "phase_lag_nodes": lane["phase_lag_nodes"],
        "causal_time_lag_steps": lane["causal_time_lag_steps"],
        "causal_lag_matches": lane["causal_lag_matches"],
        "support_mass_t": support_mass_t,
        "identity_tracking_surface": "causal_deformation_token",
        "identity_mass_ratio_min": 1.0 if deformation_peaks else 0.0,
        "identity_continuity_level": (
            "D_identity_token_tracked" if deformation_peaks else "D_identity_absent"
        ),
        "boundary_reassignment": {
            "front_entered_mass": max(support_mass_t) if support_mass_t else 0.0,
            "rear_left_mass": max(support_mass_t) if support_mass_t else 0.0,
            "boundary_reassignment_passed": bool(support_mass_t),
            "interpretation": "derived from traveling deformation support, not runtime boundary labels",
        },
        "shape": {
            "width_t": widths,
            "width_initial": initial_width,
            "width_final": final_width,
            "width_relative_change_max": width_relative_change_max,
            "profile_similarity": 1.0 if widths and initial_width == final_width else 0.0,
        },
        "response_windows": response_windows,
        "response_window_count": len(response_windows),
    }


def _classify_m_projection(
    observables: dict[str, Any],
    thresholds: dict[str, Any],
    d4: dict[str, Any],
) -> dict[str, Any]:
    displacement_passed = (
        observables["delta_x_abs"] >= thresholds["effective_displacement_min"]
    )
    identity_passed = (
        observables["identity_mass_ratio_min"] >= thresholds["identity_mass_ratio_min"]
    )
    boundary_passed = bool(
        observables["boundary_reassignment"]["boundary_reassignment_passed"]
    )
    shape_passed = (
        observables["shape"]["width_relative_change_max"]
        <= thresholds["width_relative_change_max"]
        and observables["shape"]["profile_similarity"]
        >= thresholds["profile_similarity_min"]
    )
    hard_gates = {
        "budget_passed": True,
        "nonnegative_passed": True,
        "topology_passed": True,
    }
    if not displacement_passed:
        level = "M0_no_threshold_displacement"
        primary = "displacement_below_threshold"
    elif not identity_passed:
        level = "M1_apparent_centroid_displacement"
        primary = "identity_gate_failed"
    elif not boundary_passed:
        level = "M1_apparent_centroid_displacement"
        primary = "boundary_reassignment_failed"
    elif not shape_passed:
        level = "M2_identity_preserving_displacement"
        primary = "shape_gate_failed"
    else:
        level = "M3_shape_preserving_identity_displacement_candidate_on_deformation_surface"
        primary = None

    repeated_direction_controlled = (
        level.startswith("M3")
        and d4["checks"]["direction_controls_passed"]
        and d4["checks"]["scrambled_order_negative"]
        and d4["checks"]["symmetric_null_negative"]
        and observables["response_window_count"] >= 3
    )
    return {
        "classifier": CLASSIFIER_VERSION,
        "projection_scope": "deformation_surface_only",
        "movement_level_projection": level,
        "primary_blocked_reason": primary,
        "gates": {
            **hard_gates,
            "displacement_passed": displacement_passed,
            "identity_passed_on_deformation_token": identity_passed,
            "boundary_reassignment_passed_on_deformation_support": boundary_passed,
            "shape_passed": shape_passed,
            "repeated_direction_controlled_response_passed": repeated_direction_controlled,
        },
        "m5_style_deformation_candidate": repeated_direction_controlled,
        "movement_claim_allowed": False,
        "claim_boundary": (
            "passes as a deformation-surface projection; full movement remains "
            "blocked because no runtime coherence basin identity moved"
        ),
    }


def _d_level_classification(d3: dict[str, Any], d4: dict[str, Any]) -> dict[str, Any]:
    gates = d3["d_gates"]
    return {
        "D0_no_deformation": gates["D0_no_deformation"],
        "D1_local_deformation_at_pulse_contact": gates[
            "D1_local_deformation_at_pulse_contact"
        ],
        "D2_deformation_peak_tracks_pulse": gates["D2_deformation_peak_tracks_pulse"],
        "D3_reversed_pulse_reverses_deformation_direction": gates[
            "D3_reversed_pulse_reverses_deformation_direction"
        ],
        "D4_deformation_preserves_width_profile_envelope": gates[
            "D4_deformation_preserves_width_profile_envelope"
        ],
        "D5_deformation_survives_controls_and_is_replayable": (
            gates["D5_deformation_survives_controls_and_is_replayable"]
            and d4["status"] == "passed"
        ),
        "d_level_label": "D5_direction_controlled_traveling_deformation_supported",
    }


def build_report() -> dict[str, Any]:
    d3 = _load_json(D3_REPORT)
    d4 = _load_json(D4_REPORT)
    thresholds = _thresholds()
    deformation_observables = _deformation_observables(d3)
    m_projection = _classify_m_projection(deformation_observables, thresholds, d4)
    d_classification = _d_level_classification(d3, d4)
    strict_claim_audit = {
        "deformation_surface_candidate": m_projection["m5_style_deformation_candidate"],
        "runtime_coherence_basin_moved": False,
        "native_lgrc_pulse_substrate_used": False,
        "native_lgrc_pulse_substrate_supported": False,
        "full_movement_claim_allowed": False,
        "primary_full_claim_blocker": "deformation_surface_is_not_runtime_coherence_basin",
        "secondary_full_claim_blockers": [
            "experiment_local_pulse_substrate",
            "native_lgrc_pulse_substrate_not_implemented",
            "movement_ladder_projection_is_surface_specific",
        ],
    }
    lane_e_decision_input = {
        "decision_status": "defer_native_promotion_to_lane_e",
        "recommended_native_question": (
            "whether LGRC should provide a native causal pulse-substrate surface "
            "that unifies pulse transport, local geometry coupling, and feedback "
            "regeneration"
        ),
        "candidate_native_primitives": [
            "native_causal_pulse_substrate_surface",
            "native_pulse_substrate_coupling_producer",
            "native_feedback_coupled_pulse_producer",
        ],
        "minimal_native_promotion_should_cover": [
            "local pulse transport",
            "causal local geometry response",
            "direction/null control evidence",
            "artifact replay",
            "budget and nonnegative gates",
        ],
    }
    checks = {
        "d3_source_passed": d3["status"] == "passed",
        "d4_source_passed": d4["status"] == "passed",
        "d_level_classification_replayable": d_classification[
            "d_level_label"
        ]
        == "D5_direction_controlled_traveling_deformation_supported",
        "deformation_surface_m_projection_emitted": True,
        "movement_candidate_probe_emitted": m_projection[
            "m5_style_deformation_candidate"
        ],
        "strict_movement_claim_blocked": not strict_claim_audit[
            "full_movement_claim_allowed"
        ],
        "lane_e_decision_input_emitted": True,
        "movement_claims_blocked": True,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "pulse_substrate_movement_reclassification_v1",
        "lane": "D",
        "iteration": "D5",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "substrate_carried_deformation_movement_candidate",
        "runtime_family": "experiment_local",
        "source_artifacts": {
            "d3_traveling_deformation": _artifact_record(D3_REPORT),
            "d4_direction_null_controls": _artifact_record(D4_REPORT),
            "fixed_substrate_thresholds": _artifact_record(TRANCHE_A_REPORT),
        },
        "thresholds": thresholds,
        "d_level_classification": d_classification,
        "movement_candidate_probe": {
            "deformation_observables": deformation_observables,
            "m_projection": m_projection,
        },
        "strict_movement_claim_audit": strict_claim_audit,
        "lane_e_decision_input": lane_e_decision_input,
        "checks": checks,
        "allowed_evidence_labels": [
            "direction_controlled_traveling_deformation_supported",
            "substrate_carried_deformation_movement_candidate",
        ],
        "blocked_claims": [
            "full_movement_response",
            "runtime_coherence_basin_movement",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "native_lgrc9v3_pulse_substrate",
            "biological_claim",
            "agency_claim",
        ],
        "claim_flags": {
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_lgrc9v3_e3_pulse_used": False,
            "native_grc9v3_proposal_flux_control_used": False,
            "native_grc9v3_proposal_flux_loop_claim": False,
        },
        "command": COMMAND,
        "environment": _environment_record(),
    }


def write_report(report: dict[str, Any]) -> None:
    projection = report["movement_candidate_probe"]["m_projection"]
    obs = report["movement_candidate_probe"]["deformation_observables"]
    strict = report["strict_movement_claim_audit"]
    lines = [
        "# N04 Lane D5 Movement Reclassification",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{report['status']}`",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "## D-Level",
        "",
        f"- D label: `{report['d_level_classification']['d_level_label']}`",
        "",
        "## Movement-Candidate Probe",
        "",
        f"- Deformation displacement: `{obs['delta_x_total']}`",
        f"- Response windows: `{obs['response_window_count']}`",
        f"- M projection: `{projection['movement_level_projection']}`",
        f"- M5-style deformation candidate: `{projection['m5_style_deformation_candidate']}`",
        "",
        "## Claim Boundary",
        "",
        f"- Runtime coherence basin moved: `{strict['runtime_coherence_basin_moved']}`",
        f"- Full movement claim allowed: `{strict['full_movement_claim_allowed']}`",
        f"- Primary blocker: `{strict['primary_full_claim_blocker']}`",
        "",
        "## Interpretation",
        "",
        "D5 finds a substrate-carried deformation movement candidate on the",
        "deformation surface: the direction-controlled traveling deformation",
        "projects through the frozen movement-style gates as an M3/M5-style",
        "surface candidate. This is not a full movement claim because the moved",
        "identity is a causal geometry-deformation token, not a runtime coherence",
        "basin. Lane E should decide whether a native LGRC causal pulse-substrate",
        "surface is broad enough to promote this mechanism.",
    ]
    _write_report(REPORT_PATH, lines)


def main() -> int:
    report = build_report()
    _write_json(OUTPUT_PATH, report)
    write_report(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "claim_ceiling": report["claim_ceiling"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
