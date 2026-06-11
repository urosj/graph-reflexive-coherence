#!/usr/bin/env python3
"""Build N04 Iteration 19 S7 port-graph mapping contract."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER18H_PATH = N04 / "outputs/n04_iter18h_s3_grid_series_closeout.json"
OUTPUT_PATH = N04 / "outputs/n04_iter19_s7_port_graph_mapping_contract.json"
REPORT_PATH = N04 / "reports/n04_iter19_s7_port_graph_mapping_contract.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_iter19_s7_port_graph_mapping_contract.py"
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


def _port_mapping() -> dict[str, Any]:
    return {
        "mapping_id": "s3_integrated_2d_gate_to_s7_fixed_port_graph_v1",
        "mapping_type": "role_based_port_mapping",
        "source_fixture": "S3_grid_integrated_2d_composed_gate_v1",
        "target_fixture": "S7_port_graph_fixed_composed_gate_v1",
        "node_id_preserving": False,
        "declared_before_execution": True,
        "role_mapping": {
            "shared_fork": {
                "source_node": 12,
                "target_module": "junction_module",
                "target_port": "junction_center",
            },
            "west_input": {
                "source_node": 11,
                "target_module": "west_input_module",
                "target_port": "west_in",
                "expected_output_port": "north_out",
            },
            "south_input": {
                "source_node": 17,
                "target_module": "south_input_module",
                "target_port": "south_in",
                "expected_output_port": "east_out",
            },
            "north_branch": {
                "source_node": 7,
                "target_module": "north_branch_module",
                "target_port": "north_out",
            },
            "east_branch": {
                "source_node": 13,
                "target_module": "east_branch_module",
                "target_port": "east_out",
            },
            "rear_balance_for_north": {
                "source_node": 17,
                "target_module": "south_input_module",
                "target_port": "south_balance",
            },
            "rear_balance_for_east": {
                "source_node": 11,
                "target_module": "west_input_module",
                "target_port": "west_balance",
            },
        },
        "fixed_port_graph": {
            "modules": [
                "west_input_module",
                "south_input_module",
                "junction_module",
                "north_branch_module",
                "east_branch_module",
            ],
            "ports": {
                "west_input_module": ["west_in", "west_balance"],
                "south_input_module": ["south_in", "south_balance"],
                "junction_module": ["junction_center", "north_branch_edge", "east_branch_edge"],
                "north_branch_module": ["north_out"],
                "east_branch_module": ["east_out"],
            },
            "declared_edges": [
                ["west_in", "junction_center"],
                ["south_in", "junction_center"],
                ["junction_center", "north_out"],
                ["junction_center", "east_out"],
            ],
            "topology_mutation_enabled": False,
            "edge_rewiring_enabled": False,
            "port_creation_enabled": False,
            "port_deletion_enabled": False,
        },
        "balanced_local_preference_representation": {
            "preference_policy": "paired_local_epsilon_preferences",
            "epsilon": 0.03,
            "global_branch_preference_sum": {"north_branch": 0.0, "east_branch": 0.0},
            "hidden_global_selector_allowed": False,
        },
        "lineage_policy": {
            "topology_lineage_mode": "fixed_topology_lineage_only",
            "runtime_topology_events_allowed": False,
            "source_to_target_lineage_recorded": True,
            "adaptive_topology_lineage_deferred": True,
        },
    }


def build_report() -> dict[str, Any]:
    iter18h = _load_json(ITER18H_PATH)
    mapping = _port_mapping()
    checks = {
        "source_18h_passed": iter18h["status"] == "passed",
        "source_ceiling_is_integrated_2d_gate": (
            iter18h["claim_ceiling"] == "s3_grid_integrated_2d_composed_gate_candidate"
        ),
        "mapping_is_role_based_not_node_id_preserving": (
            mapping["mapping_type"] == "role_based_port_mapping"
            and mapping["node_id_preserving"] is False
        ),
        "all_required_ports_declared": set(
            port
            for ports in mapping["fixed_port_graph"]["ports"].values()
            for port in ports
        )
        >= {"west_in", "south_in", "junction_center", "north_out", "east_out"},
        "topology_mutation_disabled_by_default": (
            mapping["fixed_port_graph"]["topology_mutation_enabled"] is False
            and mapping["lineage_policy"]["runtime_topology_events_allowed"] is False
        ),
        "balanced_preference_has_zero_global_sum": all(
            abs(value) <= 1e-12
            for value in mapping["balanced_local_preference_representation"][
                "global_branch_preference_sum"
            ].values()
        ),
        "summary_only_no_new_probe": True,
        "no_claim_promotion": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s7_port_graph_mapping_contract_only"
        if status == "passed"
        else "s7_port_graph_mapping_contract_failed_closed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter19_s7_port_graph_mapping_contract_v1",
        "iteration": "19",
        "status": status,
        "purpose": "s7_port_graph_mapping_contract_no_new_behavior_probe",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "geometry_scope": "port_graph_mapping_contract",
        "substrate_class": "port_graph",
        "source_artifacts": {"iteration_18h": _artifact_record(ITER18H_PATH)},
        "input_ceiling": iter18h["claim_ceiling"],
        "claim_ceiling": claim_ceiling,
        "mapping_contract": mapping,
        "contract_boundary": {
            "behavior_executed": False,
            "topology_mutated_during_run": False,
            "adaptive_topology_entry_allowed": False,
            "port_graph_transfer_claim_allowed": False,
            "native_lgrc_choice_selection_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
        },
        "claim_flags": {
            "native_m6": False,
            "native_m6_candidate_gate_passed": False,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "port_graph_transfer_claim_allowed": False,
            "topology_mutating_movement_claim_allowed": False,
            "native_lgrc_choice_selection_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
        },
        "blocked_claims": [
            "port_graph_transfer",
            "topology_mutating_movement",
            "adaptive_topology_movement",
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
        "checks": checks,
        "go_no_go_for_iteration_19a": {
            "iteration_19a_allowed": status == "passed",
            "fixed_port_execution_ceiling_to_test": "s3_grid_integrated_2d_composed_gate_candidate",
            "guidance": (
                "Iteration 19-A may execute the mapped S7 fixed-port graph with "
                "topology mutation disabled. Adaptive topology remains blocked."
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
        "next_iteration": "19a_s7_fixed_port_execution",
    }


def write_report(report: dict[str, Any]) -> None:
    mapping = report["mapping_contract"]
    lines = [
        "# N04 Iteration 19 S7 Port-Graph Mapping Contract",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 19 freezes a role-based S3-to-S7 port mapping. It runs no behavior probe.",
        "",
        "## Mapping",
        "",
        f"- mapping id: `{mapping['mapping_id']}`",
        f"- mapping type: `{mapping['mapping_type']}`",
        f"- node-id preserving: `{mapping['node_id_preserving']}`",
        f"- target fixture: `{mapping['target_fixture']}`",
        f"- topology mutation enabled: `{mapping['fixed_port_graph']['topology_mutation_enabled']}`",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This contract is not behavior evidence. It only freezes the S7 fixed-port role mapping before Iteration 19-A execution. Port-graph transfer, adaptive topology, topology-mutating movement, native LGRC choice selection, RC identity collapse, locomotion-like behavior, agency, and unrestricted movement remain blocked.",
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
