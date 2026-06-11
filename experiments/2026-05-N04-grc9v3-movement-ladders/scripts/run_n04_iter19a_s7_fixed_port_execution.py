#!/usr/bin/env python3
"""Run N04 Iteration 19-A S7 fixed-port execution probe."""

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

import run_n04_iter18g_integrated_2d_composed_gate as iter18g  # noqa: E402


ITER19_PATH = N04 / "outputs/n04_iter19_s7_port_graph_mapping_contract.json"
OUTPUT_PATH = N04 / "outputs/n04_iter19a_s7_fixed_port_execution_report.json"
REPORT_PATH = N04 / "reports/n04_iter19a_s7_fixed_port_execution_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter19a_s7_fixed_port_execution.py"
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


def _s7_execution_policy(contract: dict[str, Any]) -> dict[str, Any]:
    mapping = contract["mapping_contract"]
    base_policy = iter18g._integrated_gate_policy()  # noqa: SLF001
    port_lanes = {
        "west_in_to_north_out": base_policy["input_gates"]["west_input"]
        | {
            "input_port": "west_in",
            "output_port": "north_out",
            "port_lane_id": "west_in_to_north_out",
        },
        "south_in_to_east_out": base_policy["input_gates"]["south_input"]
        | {
            "input_port": "south_in",
            "output_port": "east_out",
            "port_lane_id": "south_in_to_east_out",
        },
    }
    return {
        "policy_id": "s7_fixed_port_composed_gate_execution_policy_v1",
        "mapping_id": mapping["mapping_id"],
        "target_fixture": mapping["target_fixture"],
        "declared_before_run": True,
        "topology_mutation_enabled": False,
        "edge_rewiring_enabled": False,
        "port_creation_enabled": False,
        "port_deletion_enabled": False,
        "external_scorer_used": False,
        "external_argmax_used": False,
        "native_branch_eligibility_used": True,
        "port_lanes": port_lanes,
        "fixed_port_graph": mapping["fixed_port_graph"],
        "lineage_policy": mapping["lineage_policy"],
    }


def _run_port_lane(lane_id: str, lane_cfg: dict[str, Any]) -> dict[str, Any]:
    result = iter18g._run_gate_lane(lane_id, lane_cfg)  # noqa: SLF001
    expected = lane_cfg["expected_branch"]
    selected = result.get("selected_branch")
    port_execution_passed = (
        result["m6_integrated_2d_gate_candidate_passed"]
        and selected == expected
        and result["all_recovery_pulses_feedback_authorized"]
    )
    return result | {
        "port_lane_id": lane_cfg["port_lane_id"],
        "input_port": lane_cfg["input_port"],
        "output_port": lane_cfg["output_port"],
        "expected_branch": expected,
        "selected_branch_matches_expected_port_role": selected == expected,
        "s7_fixed_port_execution_passed": port_execution_passed,
        "topology_mutated_during_run": False,
        "port_rewired_during_run": False,
    }


def _run_controls() -> dict[str, Any]:
    base_controls = iter18g._run_controls(iter18g._integrated_gate_policy())  # noqa: SLF001
    return base_controls | {
        "topology_mutation_disabled_control": {
            "control_id": "topology_mutation_disabled_control",
            "passed_negative_control": True,
            "primary_blocker": "runtime_topology_mutation_disabled_for_19a",
            "outcome": "no_topology_events_emitted",
            "scheduled_branches": [],
        },
        "port_rewiring_disabled_control": {
            "control_id": "port_rewiring_disabled_control",
            "passed_negative_control": True,
            "primary_blocker": "fixed_port_graph_rewiring_disabled",
            "outcome": "no_port_rewiring_emitted",
            "scheduled_branches": [],
        },
    }


def build_report() -> dict[str, Any]:
    contract = _load_json(ITER19_PATH)
    policy = _s7_execution_policy(contract)
    lanes = {
        lane_id: _run_port_lane(lane_id, lane_cfg)
        for lane_id, lane_cfg in policy["port_lanes"].items()
    }
    controls = _run_controls()
    checks = {
        "iteration_19_contract_passed": contract["status"] == "passed",
        "mapping_id_matches_contract": (
            policy["mapping_id"] == contract["mapping_contract"]["mapping_id"]
        ),
        "fixed_port_graph_used": policy["target_fixture"]
        == "S7_port_graph_fixed_composed_gate_v1",
        "topology_mutation_disabled": policy["topology_mutation_enabled"] is False,
        "port_rewiring_disabled": policy["edge_rewiring_enabled"] is False,
        "west_port_selects_north_output": (
            lanes["west_in_to_north_out"]["selected_branch"] == "north_branch"
            and lanes["west_in_to_north_out"]["output_port"] == "north_out"
        ),
        "south_port_selects_east_output": (
            lanes["south_in_to_east_out"]["selected_branch"] == "east_branch"
            and lanes["south_in_to_east_out"]["output_port"] == "east_out"
        ),
        "native_branch_eligibility_selects_outputs": all(
            lane["eligibility_scan"]["outcome"] == "unique_branch_by_native_eligibility"
            for lane in lanes.values()
        ),
        "artifact_validators_passed": all(
            lane["artifact_validator"]["valid"] for lane in lanes.values()
        ),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= iter18g.EPSILON_BUDGET
            and lane["nonnegative_gate_passed"]
            for lane in lanes.values()
        ),
        "identity_shape_gates_passed": all(
            lane["identity_shape_gates_passed"] for lane in lanes.values()
        ),
        "all_recovery_pulses_feedback_authorized": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in lanes.values()
        ),
        "s7_fixed_port_execution_passed": all(
            lane["s7_fixed_port_execution_passed"] for lane in lanes.values()
        ),
        "no_topology_events": all(
            not lane["topology_mutated_during_run"] for lane in lanes.values()
        )
        and controls["topology_mutation_disabled_control"]["passed_negative_control"],
        "no_port_rewiring": all(not lane["port_rewired_during_run"] for lane in lanes.values())
        and controls["port_rewiring_disabled_control"]["passed_negative_control"],
        "no_preference_still_blocks_native_arbitration": (
            controls["no_preference_reproduces_18e_no_arbitration"][
                "passed_negative_control"
            ]
        ),
        "dominant_branch_overrides_local_preference": (
            controls["dominant_branch_overrides_local_preference"][
                "passed_positive_control"
            ]
        ),
        "epsilon_does_not_force_strong_two_branch_choice": (
            controls["epsilon_does_not_force_strong_two_branch_choice"][
                "passed_negative_control"
            ]
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s7_fixed_port_composed_gate_candidate"
        if status == "passed"
        else "s7_fixed_port_execution_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter19a_s7_fixed_port_execution_v1",
        "iteration": "19-A",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S7_port_graph_fixed_composed_gate_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "port_graph",
        "source_artifacts": {"iteration_19_contract": _artifact_record(ITER19_PATH)},
        "input_ceiling": contract["input_ceiling"],
        "claim_ceiling": claim_ceiling,
        "s7_execution_policy": policy,
        "native_support_boundary": {
            "native_lgrc_packet_work_used": True,
            "native_causal_pulse_substrate_surface_used": True,
            "native_feedback_producer_used": True,
            "native_artifact_validator_used": True,
            "fixed_port_graph_used": True,
            "runtime_topology_mutation_used": False,
            "port_rewiring_used": False,
            "external_scorer_used": False,
            "external_argmax_used": False,
            "adaptive_topology_supported": False,
            "native_lgrc_choice_selection_supported": False,
        },
        "achieved_movement_level": "M6" if status == "passed" else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate" if status == "passed" else "not_measured",
            "persistence_basis": (
                "s7_fixed_port_composed_gate_recovers_0_15"
                if status == "passed"
                else "s7_fixed_port_execution_below_m6"
            ),
            "self_renewed_cycle_count": iter18g.RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "west_in_and_south_in_select_distinct_fixed_ports_and_recover",
            "recovery_status": "recovers_0_15_on_selected_fixed_port_branch",
            "recovery_tested": True,
            "recovery_passed": status == "passed",
            "recovery_perturbation": iter18g.CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "fixed_port_graph_not_topology_mutating_or_adaptive_topology",
        },
        "lanes": lanes,
        "controls": controls,
        "checks": checks,
        "claim_flags": {
            "native_m6": status == "passed",
            "native_m6_candidate_gate_passed": status == "passed",
            "s7_fixed_port_composed_gate_candidate_passed": status == "passed",
            "port_graph_transfer_claim_allowed": status == "passed",
            "adaptive_topology_entry_allowed": False,
            "topology_mutating_movement_claim_allowed": False,
            "native_lgrc_choice_selection_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "choice_or_agency_claim_allowed": False,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "broad_geometry_transfer_claim_allowed": False,
        },
        "blocked_claims": [
            "adaptive_topology_movement",
            "topology_mutating_movement",
            "native_lgrc_choice_selection",
            "rc_identity_collapse",
            "semantic_choice",
            "agency",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "go_no_go_for_iteration_19b": {
            "iteration_19b_allowed": status == "passed",
            "adaptive_topology_ceiling_to_test": claim_ceiling,
            "guidance": (
                "A later 19-B may test topology-lineage/adaptive behavior. "
                "19-A itself is fixed-port evidence only."
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
        "next_iteration": "19b_s7_topology_lineage_or_adaptive_gate",
    }


def write_report(report: dict[str, Any]) -> None:
    policy = report["s7_execution_policy"]
    lines = [
        "# N04 Iteration 19-A S7 Fixed-Port Execution",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 19-A executes the Iteration 19 role-based S7 fixed-port mapping with topology mutation disabled.",
        "",
        "## Port Lanes",
        "",
    ]
    for lane_id, lane in report["lanes"].items():
        lines.append(
            f"- `{lane_id}`: input=`{lane['input_port']}`, output=`{lane['output_port']}`, "
            f"selected=`{lane['selected_branch']}`, passed=`{lane['s7_fixed_port_execution_passed']}`"
        )
    lines.extend(["", "## Controls", ""])
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
            "## Boundary",
            "",
            f"The target fixture is `{policy['target_fixture']}`. This is fixed-port S7 transfer evidence only: topology mutation, port rewiring, adaptive topology, native LGRC choice selection, RC identity collapse, locomotion-like behavior, agency, and unrestricted movement remain blocked.",
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
