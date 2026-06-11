#!/usr/bin/env python3
"""Build N04 Iteration 17-C ring geometry closeout."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER17_PATH = N04 / "outputs/n04_iter17_ring_transfer_report.json"
ITER17A_PATH = N04 / "outputs/n04_iter17a_ring_unwrap_robustness_report.json"
ITER17B_PATH = N04 / "outputs/n04_iter17b_circular_ring_motion_evidence_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter17c_ring_geometry_closeout.json"
REPORT_PATH = N04 / "reports/n04_iter17c_ring_geometry_closeout.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_iter17c_ring_geometry_closeout.py"
)


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


def build_closeout() -> dict[str, Any]:
    iter17 = _load_json(ITER17_PATH)
    iter17a = _load_json(ITER17A_PATH)
    iter17b = _load_json(ITER17B_PATH)
    checks = {
        "iteration_17_passed": iter17["status"] == "passed",
        "iteration_17a_passed": iter17a["status"] == "passed",
        "iteration_17b_passed": iter17b["status"] == "passed",
        "single_unwrap_ring_transfer_passed": (
            iter17["claim_ceiling"]
            == "s1_ring_m6_transfer_candidate_under_declared_unwrap"
        ),
        "unwrap_robustness_passed": (
            iter17a["claim_ceiling"] == "s1_ring_unwrap_robust_transfer_candidate"
        ),
        "circular_motion_evidence_passed": (
            iter17b["claim_ceiling"]
            == "s1_ring_circular_motion_evidence_candidate"
        ),
        "all_ring_results_m6_candidate": all(
            artifact["achieved_movement_level"] == "M6"
            for artifact in [iter17, iter17a, iter17b]
        ),
        "all_ring_results_t6_candidate": all(
            artifact["persistence_axis"]["persistence_level"] == "T6_candidate"
            for artifact in [iter17, iter17a, iter17b]
        ),
        "unwrap_robustness_has_seam_controls": bool(iter17a["seam_sensitive_controls"]),
        "circular_result_has_controls": all(
            control["passed_negative_control"]
            for control in iter17b["controls"].values()
        ),
        "circular_forward_reversed_signs_passed": (
            iter17b["circular_motion_summary"][
                "forward_circular_displacement_nodes"
            ]
            > 0
            and iter17b["circular_motion_summary"][
                "reversed_circular_displacement_nodes"
            ]
            < 0
        ),
        "broader_claims_blocked": all(
            artifact["claim_flags"]["locomotion_like_claim_allowed"] is False
            and artifact["claim_flags"]["adaptive_topology_entry_allowed"] is False
            and artifact["claim_flags"]["unrestricted_movement_claim_allowed"] is False
            for artifact in [iter17, iter17a, iter17b]
        ),
        "summary_only_no_new_probe": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s1_ring_circular_motion_evidence_candidate_with_unwrap_robustness"
        if status == "passed"
        else "s1_ring_geometry_closeout_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter17c_ring_geometry_closeout_v1",
        "iteration": "17-C",
        "status": status,
        "purpose": "ring_geometry_series_closeout_no_new_probe",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "ring",
        "source_artifacts": {
            "iteration_17": _artifact_record(ITER17_PATH),
            "iteration_17a": _artifact_record(ITER17A_PATH),
            "iteration_17b": _artifact_record(ITER17B_PATH),
        },
        "claim_ceiling": claim_ceiling,
        "achieved_movement_level": "M6" if checks["all_ring_results_m6_candidate"] else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if checks["all_ring_results_t6_candidate"]
            else "not_measured",
            "persistence_basis": "s1_ring_circular_motion_with_unwrap_robustness",
            "self_renewed_cycle_count": min(
                iter17["persistence_axis"]["self_renewed_cycle_count"],
                iter17a["persistence_axis"]["self_renewed_cycle_count"],
                iter17b["persistence_axis"]["self_renewed_cycle_count"],
            ),
            "repeatability_status": "ring_series_forward_reversed_three_cycle_recovery",
            "recovery_status": "recovers_0_15_single_unwrap_multi_unwrap_and_circular_wrap_route",
            "recovery_tested": True,
            "recovery_passed": checks["all_ring_results_t6_candidate"],
            "recovery_perturbation": 0.15,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "ring_series_only_no_grid_or_port_graph_transfer",
        },
        "ring_series_summary": {
            "iteration_17_ceiling": iter17["claim_ceiling"],
            "iteration_17a_ceiling": iter17a["claim_ceiling"],
            "iteration_17b_ceiling": iter17b["claim_ceiling"],
            "accepted_unwrap_origin_count": len(
                iter17a["unwrap_robustness_policy"]["accepted_origins"]
            ),
            "seam_control_origin_count": len(
                iter17a["unwrap_robustness_policy"]["seam_control_origins"]
            ),
            "forward_circular_displacement_nodes": iter17b[
                "circular_motion_summary"
            ]["forward_circular_displacement_nodes"],
            "reversed_circular_displacement_nodes": iter17b[
                "circular_motion_summary"
            ]["reversed_circular_displacement_nodes"],
            "forward_phase_error_to_target_nodes": iter17b[
                "circular_motion_summary"
            ]["forward_final_phase_error_to_target_nodes"],
            "reversed_phase_error_to_target_nodes": iter17b[
                "circular_motion_summary"
            ]["reversed_final_phase_error_to_target_nodes"],
            "interpretation": (
                "The ring series supports a scoped S1 ring circular-motion "
                "evidence candidate with unwrap robustness: the result first "
                "passed under a declared unwrap, then across all equivalent "
                "non-seam unwraps, then on the wrap edge under a circular phase "
                "metric. It remains a ring evidence candidate, not broad "
                "geometry transfer or locomotion-like movement."
            ),
        },
        "claim_flags": {
            "native_m6": checks["all_ring_results_m6_candidate"],
            "native_m6_candidate_gate_passed": checks["all_ring_results_m6_candidate"],
            "circular_motion_evidence_candidate_gate_passed": status == "passed",
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
        "checks": checks,
        "go_no_go_for_iteration_18": {
            "iteration_18_allowed": status == "passed",
            "grid_transfer_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 18 may test whether the ring-series ceiling transfers "
                "to S3 grid route-defined front/rear geometry. Ring evidence "
                "does not automatically promote grid, port-graph, broad "
                "geometry-transfer, locomotion-like, or adaptive-topology claims."
            ),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "status_short": _run_git(["status", "--short"]),
            "head": _run_git(["rev-parse", "HEAD"]),
        },
        "next_iteration": "18_s3_grid_route_defined_front_rear",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["ring_series_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 17-C Ring Geometry Closeout",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 17-C is a summary-only closeout for the ring series. It runs no new probe.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- Iteration 17 ceiling: `{summary['iteration_17_ceiling']}`",
        f"- Iteration 17-A ceiling: `{summary['iteration_17a_ceiling']}`",
        f"- Iteration 17-B ceiling: `{summary['iteration_17b_ceiling']}`",
        f"- accepted unwrap origins: `{summary['accepted_unwrap_origin_count']}`",
        f"- seam-control origins: `{summary['seam_control_origin_count']}`",
        f"- forward circular displacement: `{summary['forward_circular_displacement_nodes']}`",
        f"- reversed circular displacement: `{summary['reversed_circular_displacement_nodes']}`",
        "",
        summary["interpretation"],
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_18"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The combined ceiling is still a scoped S1 ring evidence candidate. It does not promote locomotion-like, broad geometry-transfer, adaptive-topology, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement claims.",
            "",
            "## Command",
            "",
            f"```bash\n{COMMAND}\n```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_closeout()
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
