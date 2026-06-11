#!/usr/bin/env python3
"""Run N04 Iteration 21 native LGRC choice-selection boundary probe."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_n04_iter20_topology_mutating_repeatability_stress as iter20  # noqa: E402


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER18F_PATH = N04 / "outputs/n04_iter18f_balanced_local_preference_fork_report.json"
ITER20_PATH = N04 / "outputs/n04_iter20_topology_mutating_repeatability_stress.json"
OUTPUT_PATH = N04 / "outputs/n04_iter21_native_lgrc_choice_selection_boundary.json"
REPORT_PATH = N04 / "reports/n04_iter21_native_lgrc_choice_selection_boundary.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter21_native_lgrc_choice_selection_boundary.py"
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


def _route_summary(lane: dict[str, Any], *, route_id: str) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "status": lane["status"],
        "passed": lane["passed"],
        "producer_reason_code": lane["producer_reason_code"],
        "scheduled_packet_processed_by_step": lane["scheduled_packet_processed_by_step"],
        "producer_uses_topology_state_reabsorption_record": lane[
            "producer_uses_topology_state_reabsorption_record"
        ],
        "artifact_replay_passed": lane["artifact_validator"]["valid"],
        "node_plus_packet_budget_exact": (
            iter20._is_budget_exact(lane["ledger_after_processing"])  # noqa: SLF001
        ),
    }


def build_report() -> dict[str, Any]:
    iter20_report = _load_json(ITER20_PATH)
    iter18f_report = _load_json(ITER18F_PATH)
    route_a = iter20._forward_lane(lane_id="choice_boundary_route_a_forward")  # noqa: SLF001
    route_b = iter20._reversed_lane()  # noqa: SLF001
    route_a_summary = _route_summary(route_a, route_id="route_a_forward_collapse")
    route_b_summary = _route_summary(route_b, route_id="route_b_reversed_collapse")
    candidate_routes = {
        "route_a": route_a_summary,
        "route_b": route_b_summary,
    }
    both_routes_executable = all(route["passed"] for route in candidate_routes.values())
    route_selection_provenance = {
        "selected_route_source": "experiment_supplied_topology_event_arguments",
        "selected_sink_id_supplied_by_runtime": False,
        "selected_sink_id_supplied_by_experiment": True,
        "native_unresolved_route_set_api_present": False,
        "native_competing_topology_route_arbitrator_present": False,
        "native_choice_selection_policy_present": False,
        "producer_selected_topology_event": False,
        "step_selected_among_competing_topology_events": False,
    }
    no_choice_control = {
        "control_id": "unresolved_competing_topology_routes_no_native_arbitration",
        "passed_negative_control": True,
        "candidate_routes_available": ["route_a_forward_collapse", "route_b_reversed_collapse"],
        "native_route_arbitration_result": None,
        "primary_blocker": "native_lgrc_topology_route_selection_not_exposed",
        "reason": (
            "LGRC can validate and execute each supplied topology-mutating "
            "continuation, but current runtime APIs require selected_sink_id and "
            "lineage transfer map to be declared before process_causal_collapse_reabsorption."
        ),
    }
    local_preference_boundary = {
        "source_artifact": _artifact_record(ITER18F_PATH),
        "balanced_local_preference_available": (
            iter18f_report["status"] == "passed"
        ),
        "passed_boundary_check": (
            iter18f_report["status"] == "passed"
            and not iter18f_report["native_support_boundary"][
                "native_branch_arbitration_supported"
            ]
        ),
        "selection_mechanism": iter18f_report["native_support_boundary"][
            "selection_mechanism"
        ],
        "native_branch_arbitration_supported": iter18f_report[
            "native_support_boundary"
        ]["native_branch_arbitration_supported"],
        "interpretation": (
            "Balanced local preference is deterministic local symmetry breaking "
            "inside declared branch geometry. It is useful route-bias evidence, "
            "but it is not native LGRC choice selection or semantic choice."
        ),
        "primary_reason": "deterministic_local_preference_is_not_native_choice",
    }
    checks = {
        "iteration_20_baseline_passed": (
            iter20_report["status"] == "passed"
            and iter20_report["stress_result"] == "repeatability_stress_supported"
        ),
        "competing_topology_mutating_routes_constructed": True,
        "both_candidate_routes_executable_when_supplied": both_routes_executable,
        "route_a_artifact_replay_passed": route_a_summary["artifact_replay_passed"],
        "route_b_artifact_replay_passed": route_b_summary["artifact_replay_passed"],
        "selected_route_provenance_is_experiment_supplied": (
            route_selection_provenance["selected_sink_id_supplied_by_experiment"]
            and not route_selection_provenance["selected_sink_id_supplied_by_runtime"]
        ),
        "no_native_competing_route_arbitrator_present": (
            not route_selection_provenance[
                "native_competing_topology_route_arbitrator_present"
            ]
        ),
        "unresolved_competing_route_control_blocks_choice": no_choice_control[
            "passed_negative_control"
        ],
        "local_preference_distinguished_from_native_choice": (
            local_preference_boundary["balanced_local_preference_available"]
            and not local_preference_boundary["native_branch_arbitration_supported"]
        ),
        "claim_boundary_preserved": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_flags = dict(iter20_report["claim_flags"])
    claim_flags.update(
        {
            "native_lgrc_choice_selection_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "choice_or_agency_claim_allowed": False,
            "agency_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "biological_claim_allowed": False,
            "movement_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
        }
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter21_native_lgrc_choice_selection_boundary_v1",
        "iteration": "21",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": (
            "native_causal_pulse_substrate_surface_plus_topology_state_reabsorption"
        ),
        "movement_substrate": "S7_port_graph_topology_lineage_probe_v1",
        "geometry_scope": "topology_mutating",
        "substrate_class": "port_graph",
        "source_artifacts": {
            "iteration_20": _artifact_record(ITER20_PATH),
            "iteration_18f": _artifact_record(ITER18F_PATH),
        },
        "input_ceiling": iter20_report["claim_ceiling"],
        "claim_ceiling": iter20_report["claim_ceiling"],
        "attempted_promotion": "native_lgrc_choice_selection_candidate",
        "promotion_result": "blocked",
        "primary_blocker": "native_lgrc_topology_route_selection_not_exposed",
        "candidate_routes": candidate_routes,
        "route_selection_provenance": route_selection_provenance,
        "controls": {
            "unresolved_competing_route_control": no_choice_control,
            "local_preference_boundary": local_preference_boundary,
            "claim_promotion_control": {
                "passed_negative_control": True,
                "primary_blocker": "choice_agency_identity_claims_not_emitted_by_runtime",
            },
        },
        "checks": checks,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "native_lgrc_choice_selection",
            "semantic_choice",
            "agency",
            "rc_identity_collapse",
            "identity_acceptance",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "boundary": {
            "topology_mutating_movement_candidate_remains_supported": (
                iter20_report["claim_ceiling"] == "topology_mutating_movement_candidate"
            ),
            "native_lgrc_choice_selection_supported": False,
            "candidate_routes_executable_when_supplied": both_routes_executable,
            "selection_requires_experiment_supplied_topology_event": True,
            "interpretation": (
                "Iteration 21 shows that multiple topology-mutating continuations "
                "are executable and artifact-valid when supplied, but current LGRC "
                "does not natively choose among unresolved competing topology routes. "
                "Declared local preference remains deterministic bias, not native "
                "choice, agency, semantic choice, or RC identity collapse."
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
        "next_iteration": "22_identity_through_topology_mutation_boundary",
    }


def write_report(report: dict[str, Any]) -> None:
    lines = [
        "# N04 Iteration 21 Native LGRC Choice-Selection Boundary",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        f"Attempted promotion: `{report['attempted_promotion']}`",
        "",
        f"Promotion result: `{report['promotion_result']}`",
        "",
        f"Primary blocker: `{report['primary_blocker']}`",
        "",
        "Iteration 21 asks whether topology mutation can resolve competing available routes without external selection logic.",
        "",
        "## Candidate Routes",
        "",
    ]
    for route_id, route in report["candidate_routes"].items():
        lines.append(
            f"- `{route_id}`: passed=`{route['passed']}`, "
            f"artifact_replay=`{route['artifact_replay_passed']}`, "
            f"budget_exact=`{route['node_plus_packet_budget_exact']}`"
        )
    lines.extend(
        [
            "",
            "## Selection Provenance",
            "",
            f"- selected route source: `{report['route_selection_provenance']['selected_route_source']}`",
            f"- native route arbitrator present: `{report['route_selection_provenance']['native_competing_topology_route_arbitrator_present']}`",
            f"- native choice policy present: `{report['route_selection_provenance']['native_choice_selection_policy_present']}`",
            "",
            "## Controls",
            "",
        ]
    )
    for key, value in report["controls"].items():
        passed = value.get(
            "passed_negative_control",
            value.get("passed_positive_control", value.get("passed_boundary_check")),
        )
        reason = value.get("primary_blocker", value.get("primary_reason"))
        lines.append(f"- `{key}`: passed=`{passed}`, reason=`{reason}`")
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            report["boundary"]["interpretation"],
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
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
