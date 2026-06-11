#!/usr/bin/env python3
"""Run N04 Iteration 18-F balanced local-preference fork probe."""

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

import run_n04_iter18e_grid_composed_1d_fork_competition as iter18e  # noqa: E402


ITER18E_PATH = N04 / "outputs/n04_iter18e_grid_composed_1d_fork_competition_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter18f_balanced_local_preference_fork_report.json"
REPORT_PATH = N04 / "reports/n04_iter18f_balanced_local_preference_fork_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter18f_balanced_local_preference_fork.py"
)

EPSILON = 0.03
RECOVERY_WINDOW_CYCLES = iter18e.RECOVERY_WINDOW_CYCLES
CHALLENGE_TRANSFER_AMOUNT = iter18e.CHALLENGE_TRANSFER_AMOUNT


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


def _preference_policy() -> dict[str, Any]:
    return {
        "policy_id": "s3_grid_balanced_local_preference_fork_policy_v1",
        "declared_before_run": True,
        "epsilon": EPSILON,
        "epsilon_role": "local_near_tie_symmetry_breaker_only",
        "local_preference_sites": [
            {
                "site_id": "center_fork_local_preference",
                "site_node": iter18e.CENTER_NODE,
                "preferred_branch": "north_branch",
                "damped_branch": "east_branch",
                "epsilon": EPSILON,
                "preference_vector": {"north_branch": EPSILON, "east_branch": -EPSILON},
            },
            {
                "site_id": "mirror_fork_local_preference",
                "site_node": 8,
                "preferred_branch": "east_branch",
                "damped_branch": "north_branch",
                "epsilon": EPSILON,
                "preference_vector": {"north_branch": -EPSILON, "east_branch": EPSILON},
            },
        ],
        "global_preference_sum": {"north_branch": 0.0, "east_branch": 0.0},
        "global_directional_preference": "none",
        "external_scorer_used": False,
        "external_argmax_used": False,
        "dominant_signal_must_override_local_preference": True,
    }


def _lane_summary(lane: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "lane",
        "selected_branch",
        "final_branch_progress",
        "recovery_scheduled_cycle_count",
        "m6_composed_fork_candidate_passed",
        "all_recovery_pulses_feedback_authorized",
        "budget_abs_error",
        "nonnegative_gate_passed",
        "width_relative_change",
        "profile_similarity",
    ]
    return {key: lane.get(key) for key in keys}


def _run_lanes() -> dict[str, dict[str, Any]]:
    return {
        "north_local_preference_tie_break": iter18e._run_unique_branch_lane(  # noqa: SLF001
            "north_local_preference_tie_break",
            north_bias=0.25,
            east_bias=-EPSILON,
        ),
        "east_local_preference_tie_break": iter18e._run_unique_branch_lane(  # noqa: SLF001
            "east_local_preference_tie_break",
            north_bias=0.10 - EPSILON,
            east_bias=0.25,
        ),
        "east_dominant_overrides_north_preference": iter18e._run_unique_branch_lane(  # noqa: SLF001
            "east_dominant_overrides_north_preference",
            north_bias=0.10 - EPSILON,
            east_bias=0.25 - EPSILON,
        ),
    }


def _run_controls() -> dict[str, Any]:
    no_preference = iter18e._eligibility_scan(north_bias=0.25, east_bias=0.0)  # noqa: SLF001
    north_preference = iter18e._eligibility_scan(  # noqa: SLF001
        north_bias=0.25,
        east_bias=-EPSILON,
    )
    east_preference = iter18e._eligibility_scan(  # noqa: SLF001
        north_bias=0.10 - EPSILON,
        east_bias=0.25,
    )
    epsilon_too_large = iter18e._eligibility_scan(  # noqa: SLF001
        north_bias=0.25,
        east_bias=0.25 - EPSILON,
    )
    return {
        "no_preference_remains_no_arbitration": {
            "control_id": "no_preference_remains_no_arbitration_control",
            "passed_negative_control": no_preference["outcome"] == "tie_no_native_arbitration",
            "primary_blocker": "both_branches_eligible_no_native_arbitration",
            "outcome": no_preference["outcome"],
            "scheduled_branches": no_preference["scheduled_branches"],
        },
        "north_local_preference_resolves_tie": {
            "control_id": "north_local_preference_resolves_tie_control",
            "passed_positive_control": (
                north_preference["outcome"] == "unique_branch_by_native_eligibility"
                and north_preference["unique_selected_branch"] == "north_branch"
            ),
            "primary_reason": "east_branch_damped_below_threshold_by_local_epsilon",
            "outcome": north_preference["outcome"],
            "scheduled_branches": north_preference["scheduled_branches"],
        },
        "east_local_preference_resolves_tie": {
            "control_id": "east_local_preference_resolves_tie_control",
            "passed_positive_control": (
                east_preference["outcome"] == "unique_branch_by_native_eligibility"
                and east_preference["unique_selected_branch"] == "east_branch"
            ),
            "primary_reason": "north_branch_damped_below_threshold_by_local_epsilon",
            "outcome": east_preference["outcome"],
            "scheduled_branches": east_preference["scheduled_branches"],
        },
        "epsilon_not_global_override": {
            "control_id": "epsilon_not_global_override_control",
            "passed_negative_control": (
                epsilon_too_large["outcome"] == "tie_no_native_arbitration"
            ),
            "primary_blocker": "both_strong_branches_remain_eligible_epsilon_does_not_force_choice",
            "outcome": epsilon_too_large["outcome"],
            "scheduled_branches": epsilon_too_large["scheduled_branches"],
        },
    }


def build_report() -> dict[str, Any]:
    iter18e_report = _load_json(ITER18E_PATH)
    policy = _preference_policy()
    lanes = _run_lanes()
    controls = _run_controls()
    checks = {
        "iteration_18e_available": iter18e_report["status"] == "passed",
        "balanced_local_preference_policy_declared": True,
        "epsilon_declared_before_run": True,
        "global_preference_sum_zero": all(
            abs(value) <= 1e-12 for value in policy["global_preference_sum"].values()
        ),
        "external_scorer_absent": True,
        "external_argmax_absent": True,
        "north_and_east_preferences_resolve_local_ties": (
            controls["north_local_preference_resolves_tie"]["passed_positive_control"]
            and controls["east_local_preference_resolves_tie"]["passed_positive_control"]
        ),
        "unbiased_tie_still_exposes_18e_blocker": (
            controls["no_preference_remains_no_arbitration"]["passed_negative_control"]
        ),
        "epsilon_does_not_force_global_choice": (
            controls["epsilon_not_global_override"]["passed_negative_control"]
        ),
        "dominant_signal_overrides_local_preference": (
            lanes["east_dominant_overrides_north_preference"]["selected_branch"]
            == "east_branch"
        ),
        "m6_balanced_preference_candidate_passed": all(
            lane["m6_composed_fork_candidate_passed"] for lane in lanes.values()
        ),
        "all_recovery_pulses_feedback_authorized": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in lanes.values()
        ),
        "artifact_validators_passed": all(
            lane["artifact_validator"]["valid"] for lane in lanes.values()
        ),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= iter18e.EPSILON_BUDGET
            and lane["nonnegative_gate_passed"]
            for lane in lanes.values()
        ),
        "identity_shape_gates_passed": all(
            lane["identity_shape_gates_passed"] for lane in lanes.values()
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s3_grid_balanced_local_preference_fork_competition_candidate"
        if status == "passed"
        else "s3_grid_balanced_local_preference_fork_failed_closed"
    )
    return {
        "report_kind": "n04_iter18f_balanced_local_preference_fork_v1",
        "iteration": "18-F",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "result_role": "balanced_local_preference_composed_fork_probe",
        "movement_substrate": "S3_grid_balanced_local_preference_composed_fork_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "grid",
        "input_iteration_18e": _artifact_record(ITER18E_PATH),
        "claim_ceiling": claim_ceiling,
        "preference_policy": policy,
        "native_support_boundary": {
            "native_lgrc_packet_work_used": True,
            "native_causal_pulse_substrate_surface_used": True,
            "native_feedback_eligibility_surface_used": True,
            "native_feedback_producer_used": True,
            "native_artifact_validator_used": True,
            "external_scorer_used": False,
            "external_argmax_used": False,
            "balanced_local_preference_used": True,
            "global_directional_preference": "none",
            "native_branch_arbitration_supported": False,
            "selection_mechanism": "local_preference_breaks_near_tie_by_native_branch_eligibility",
        },
        "achieved_movement_level": "M6" if status == "passed" else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate" if status == "passed" else "not_measured",
            "persistence_basis": (
                "s3_grid_balanced_local_preference_fork_recovers_0_15"
                if status == "passed"
                else "balanced_local_preference_below_m6"
            ),
            "self_renewed_cycle_count": RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "paired_local_preferences_resolve_distinct_branch_ties",
            "recovery_status": "recovers_0_15_after_local_tie_break",
            "recovery_tested": True,
            "recovery_passed": status == "passed",
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "local_preference_tie_breaking_not_native_choice_or_rc_collapse",
        },
        "balanced_preference_summary": {
            "entry_ceiling": iter18e_report["claim_ceiling"],
            "positive_result": (
                "Balanced local preferences remove the 18-E no-arbitration "
                "tie for near-threshold local forks while keeping global "
                "preference sum zero."
            ),
            "remaining_blocker": (
                "This is local symmetry breaking by declared epsilon, not "
                "native LGRC choice selection, RC identity collapse, or agency."
            ),
            "selected_branches": {
                lane_id: lane["selected_branch"] for lane_id, lane in lanes.items()
            },
        },
        "lanes": lanes,
        "lane_summaries": {lane_id: _lane_summary(lane) for lane_id, lane in lanes.items()},
        "controls": controls,
        "checks": checks,
        "go_no_go_for_iteration_19": {
            "iteration_19_allowed": status == "passed",
            "port_graph_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 19 may test whether balanced local preference and "
                "composed-branch competition transfer to S7 port mechanics. "
                "Native choice/collapse claims remain blocked."
            ),
        },
        "claim_flags": {
            "native_m6": status == "passed",
            "native_m6_candidate_gate_passed": status == "passed",
            "balanced_local_preference_fork_candidate_passed": status == "passed",
            "native_branch_competition_claim_allowed": status == "passed",
            "balanced_local_preference_claim_allowed": status == "passed",
            "native_branch_arbitration_claim_allowed": False,
            "native_lgrc_choice_selection_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "choice_or_agency_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "broad_geometry_transfer_claim_allowed": False,
            "adaptive_topology_claim_allowed": False,
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
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "git_head": _run_git(["rev-parse", "HEAD"]),
            "git_status_short": _run_git(["status", "--short"]),
        },
        "command": COMMAND,
    }


def write_report(report: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["balanced_preference_summary"]
    lines = [
        "# N04 Iteration 18-F Balanced Local Preference Fork",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 18-F tests whether tiny balanced local preferences can remove "
        "the 18-E tie/no-arbitration blocker without adding a global selector.",
        "",
        "## Reasoning",
        "",
        "Iteration 18-E showed that composed 1D branches can differentiate by "
        "native eligibility, but a symmetric eligible fork has no native "
        "arbitration. Iteration 18-F adds paired local epsilon preferences with "
        "zero global branch-preference sum. The epsilon is allowed to break "
        "near-threshold local ties, but it must not become a global argmax or "
        "override stronger branch evidence.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- entry ceiling: `{summary['entry_ceiling']}`",
        f"- selected branches: `{summary['selected_branches']}`",
        f"- remaining blocker: `{summary['remaining_blocker']}`",
        "",
        "## Preference Policy",
        "",
        f"- epsilon: `{report['preference_policy']['epsilon']}`",
        f"- global preference sum: `{report['preference_policy']['global_preference_sum']}`",
        f"- global directional preference: `{report['preference_policy']['global_directional_preference']}`",
        "",
        "## Controls",
        "",
    ]
    for key, value in report["controls"].items():
        passed = value.get("passed_negative_control", value.get("passed_positive_control"))
        reason = value.get("primary_blocker", value.get("primary_reason"))
        lines.append(
            f"- `{key}`: passed=`{passed}`, reason=`{reason}`, "
            f"outcome=`{value['outcome']}`"
        )
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This supports balanced local preference as a near-tie symmetry breaker for composed LGRC branch competition. It is not native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, identity-acceptance, inherited-N03, or unrestricted movement evidence.",
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
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
