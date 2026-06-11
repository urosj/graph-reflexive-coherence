#!/usr/bin/env python3
"""Build N04 Iteration 18-H S3 grid series closeout."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER18_PATH = N04 / "outputs/n04_iter18_grid_transfer_report.json"
ITER18B_PATH = N04 / "outputs/n04_iter18b_grid_two_axis_turn_report.json"
ITER18C_PATH = N04 / "outputs/n04_iter18c_grid_state_gated_routing_report.json"
ITER18D_PATH = N04 / "outputs/n04_iter18d_grid_geometry_selection_report.json"
ITER18E_PATH = N04 / "outputs/n04_iter18e_grid_composed_1d_fork_competition_report.json"
ITER18F_PATH = N04 / "outputs/n04_iter18f_balanced_local_preference_fork_report.json"
ITER18G_PATH = N04 / "outputs/n04_iter18g_integrated_2d_composed_gate_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter18h_s3_grid_series_closeout.json"
REPORT_PATH = N04 / "reports/n04_iter18h_s3_grid_series_closeout.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_iter18h_s3_grid_series_closeout.py"
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
    iter18 = _load_json(ITER18_PATH)
    iter18b = _load_json(ITER18B_PATH)
    iter18c = _load_json(ITER18C_PATH)
    iter18d = _load_json(ITER18D_PATH)
    iter18e = _load_json(ITER18E_PATH)
    iter18f = _load_json(ITER18F_PATH)
    iter18g = _load_json(ITER18G_PATH)
    artifacts = [iter18, iter18b, iter18c, iter18d, iter18e, iter18f, iter18g]
    checks = {
        "iteration_18_passed": iter18["status"] == "passed",
        "iteration_18b_passed": iter18b["status"] == "passed",
        "iteration_18c_passed": iter18c["status"] == "passed",
        "iteration_18d_passed": iter18d["status"] == "passed",
        "iteration_18e_passed": iter18e["status"] == "passed",
        "iteration_18f_passed": iter18f["status"] == "passed",
        "iteration_18g_passed": iter18g["status"] == "passed",
        "route_defined_grid_survived": (
            iter18["claim_ceiling"] == "s3_grid_route_defined_m6_transfer_candidate"
        ),
        "two_axis_turn_passed": (
            iter18b["claim_ceiling"] == "s3_grid_two_axis_turn_m6_transfer_candidate"
        ),
        "state_gated_routing_passed": (
            iter18c["claim_ceiling"]
            == "s3_grid_state_gated_two_input_two_output_routing_candidate"
        ),
        "external_scorer_blocker_recorded": (
            iter18d["native_support_boundary"]["selection_logic_kind"]
            == "external_experiment_scoring_logic"
        ),
        "composed_fork_without_external_scorer_passed": (
            iter18e["claim_ceiling"] == "s3_grid_composed_1d_fork_competition_candidate"
        ),
        "balanced_local_preference_passed": (
            iter18f["claim_ceiling"]
            == "s3_grid_balanced_local_preference_fork_competition_candidate"
            and iter18f["checks"]["global_preference_sum_zero"]
        ),
        "integrated_2d_gate_passed": (
            iter18g["claim_ceiling"] == "s3_grid_integrated_2d_composed_gate_candidate"
        ),
        "all_grid_results_m6_candidate": all(
            artifact["achieved_movement_level"] == "M6" for artifact in artifacts
        ),
        "all_grid_results_t6_candidate": all(
            artifact["persistence_axis"]["persistence_level"] == "T6_candidate"
            for artifact in artifacts
        ),
        "broader_claims_blocked": all(
            artifact["claim_flags"]["locomotion_like_claim_allowed"] is False
            and artifact["claim_flags"]["adaptive_topology_entry_allowed"] is False
            and artifact["claim_flags"]["unrestricted_movement_claim_allowed"] is False
            and artifact["claim_flags"]["agency_claim_allowed"] is False
            and artifact["claim_flags"]["identity_acceptance_claim_allowed"] is False
            for artifact in artifacts
        ),
        "summary_only_no_new_probe": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s3_grid_integrated_2d_composed_gate_candidate"
        if status == "passed"
        else "s3_grid_series_closeout_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter18h_s3_grid_series_closeout_v1",
        "iteration": "18-H",
        "status": status,
        "purpose": "s3_grid_series_closeout_no_new_probe",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "grid",
        "source_artifacts": {
            "iteration_18": _artifact_record(ITER18_PATH),
            "iteration_18b": _artifact_record(ITER18B_PATH),
            "iteration_18c": _artifact_record(ITER18C_PATH),
            "iteration_18d": _artifact_record(ITER18D_PATH),
            "iteration_18e": _artifact_record(ITER18E_PATH),
            "iteration_18f": _artifact_record(ITER18F_PATH),
            "iteration_18g": _artifact_record(ITER18G_PATH),
        },
        "claim_ceiling": claim_ceiling,
        "achieved_movement_level": "M6"
        if checks["all_grid_results_m6_candidate"]
        else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if checks["all_grid_results_t6_candidate"]
            else "not_measured",
            "persistence_basis": "s3_grid_integrated_2d_composed_gate_series",
            "self_renewed_cycle_count": min(
                artifact["persistence_axis"]["self_renewed_cycle_count"]
                for artifact in artifacts
            ),
            "repeatability_status": "s3_grid_route_turn_gate_selection_composition_and_integrated_gate_passed",
            "recovery_status": "recovers_0_15_across_s3_grid_series",
            "recovery_tested": True,
            "recovery_passed": checks["all_grid_results_t6_candidate"],
            "recovery_perturbation": 0.15,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "fixed_topology_grid_series_not_port_graph_or_adaptive_topology",
        },
        "s3_grid_series_summary": {
            "iteration_18_ceiling": iter18["claim_ceiling"],
            "iteration_18b_ceiling": iter18b["claim_ceiling"],
            "iteration_18c_ceiling": iter18c["claim_ceiling"],
            "iteration_18d_ceiling": iter18d["claim_ceiling"],
            "iteration_18e_ceiling": iter18e["claim_ceiling"],
            "iteration_18f_ceiling": iter18f["claim_ceiling"],
            "iteration_18g_ceiling": iter18g["claim_ceiling"],
            "strongest_scoped_ceiling": claim_ceiling,
            "integration_path": [
                "route_defined_grid_survival",
                "two_axis_turn",
                "two_input_two_output_design",
                "geometry_flux_selection_prototype_external_scorer_blocked",
                "composed_1d_fork_competition_without_external_scorer",
                "balanced_local_preference_tie_breaking_without_global_bias",
                "integrated_fixed_topology_2d_composed_gate",
            ],
            "interpretation": (
                "The S3 grid series supports a scoped fixed-topology 2D "
                "composed-gate candidate. It integrates the two-input/two-output "
                "gate shape, native composed 1D branch competition, and balanced "
                "local preference tie-breaking. It remains below native LGRC "
                "choice selection, RC identity collapse, port-graph transfer, "
                "adaptive topology, and locomotion-like movement."
            ),
        },
        "claim_flags": {
            "native_m6": checks["all_grid_results_m6_candidate"],
            "native_m6_candidate_gate_passed": checks["all_grid_results_m6_candidate"],
            "fixed_topology_2d_gate_candidate_passed": status == "passed",
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
            "native_lgrc_choice_selection_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "port_graph_transfer_claim_allowed": False,
        },
        "blocked_claims": [
            "native_lgrc_choice_selection",
            "rc_identity_collapse",
            "semantic_choice",
            "agency",
            "port_graph_transfer",
            "adaptive_topology_movement",
            "topology_mutating_movement",
            "broad_geometry_transfer",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "checks": checks,
        "go_no_go_for_iteration_19": {
            "iteration_19_allowed": status == "passed",
            "port_graph_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 19 may test whether the fixed-topology 2D composed "
                "gate transfers to S7 port mechanics. Native LGRC choice "
                "selection, RC collapse, and adaptive topology remain blocked "
                "until explicit controls pass."
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
        "next_iteration": "19_s7_port_graph_and_adaptive_topology_gate",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["s3_grid_series_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 18-H S3 Grid Series Closeout",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 18-H is a summary-only closeout for the S3 grid series. It runs no new probe.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- Iteration 18 ceiling: `{summary['iteration_18_ceiling']}`",
        f"- Iteration 18-B ceiling: `{summary['iteration_18b_ceiling']}`",
        f"- Iteration 18-C ceiling: `{summary['iteration_18c_ceiling']}`",
        f"- Iteration 18-D ceiling: `{summary['iteration_18d_ceiling']}`",
        f"- Iteration 18-E ceiling: `{summary['iteration_18e_ceiling']}`",
        f"- Iteration 18-F ceiling: `{summary['iteration_18f_ceiling']}`",
        f"- Iteration 18-G ceiling: `{summary['iteration_18g_ceiling']}`",
        "",
        summary["interpretation"],
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_19"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The combined ceiling is a scoped fixed-topology S3 2D composed-gate candidate. It does not promote native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph transfer, topology-mutating movement, adaptive topology, broad geometry-transfer, locomotion-like behavior, biological behavior, identity acceptance, inherited-N03 movement, or unrestricted movement.",
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
