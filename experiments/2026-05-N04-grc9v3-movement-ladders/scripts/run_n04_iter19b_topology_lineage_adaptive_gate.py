#!/usr/bin/env python3
"""Run N04 Iteration 19-B S7 topology-lineage / adaptive gate probe."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any

from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3CausalPulseSubstrateSurfaceRow,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_NODE_ONLY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC_RUNTIME_LEVEL_LGRC3,
)
from pygrc.models.lgrc_9_v3_topology import (
    process_lgrc9v3_collapse_reabsorption,
    validate_lgrc9v3_topology_event_replay,
)


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER19A_PATH = N04 / "outputs/n04_iter19a_s7_fixed_port_execution_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json"
REPORT_PATH = N04 / "reports/n04_iter19b_topology_lineage_adaptive_gate_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter19b_topology_lineage_adaptive_gate.py"
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


def _valid_surface_row(**overrides: object) -> LGRC9V3CausalPulseSubstrateSurfaceRow:
    values: dict[str, object] = {
        "surface_id": "surface-row-19b-fixed",
        "surface_policy_id": "surface-policy-19b",
        "surface_policy_enabled": True,
        "surface_policy_validated": True,
        "route_aspect_id": "s7-fixed-port-route",
        "route_aspect_digest": "s7-fixed-port-route-digest",
        "pulse_event_id": "packet-event-19b",
        "pulse_packet_id": "packet-19b",
        "pulse_event_kind": LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        "pulse_channel_id": "junction_center_to_north_out",
        "pulse_route_step": 1,
        "event_time_key": 2.0,
        "scheduler_event_index": 3,
        "node_proper_time": {12: 2.0, 7: 2.0},
        "source_node_id": 12,
        "target_node_id": 7,
        "contact_amount": 0.1,
        "surface_state_id": "surface-state-19b",
        "surface_state_digest": "surface-state-19b-digest",
        "surface_kind": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
        "surface_nodes": (12, 7),
        "surface_values_before": {"contact_mass": 0.0},
        "surface_values_after": {"contact_mass": 0.1},
        "runtime_visible_inputs": (
            "committed_packet_event",
            "route_aspect_digest",
            "pulse_channel_id",
        ),
        "surface_update_policy": {
            "policy_id": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED,
            "version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
            "activation_gate": "committed_packet_event",
            "allowed_surface_kinds": [
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT
            ],
        },
        "surface_budget_surface": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_NODE_ONLY,
        "surface_budget_before": 25.0,
        "surface_budget_after": 25.0,
        "surface_budget_error": 0.0,
        "lineage_status": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
        "producer_records": (),
        "claim_flags": {
            "movement_claim_allowed": False,
            "native_m6": False,
            "adaptive_topology_entry_allowed": False,
        },
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
    }
    values.update(overrides)
    return LGRC9V3CausalPulseSubstrateSurfaceRow(**values)  # type: ignore[arg-type]


def _native_topology_lineage_probe() -> dict[str, Any]:
    result = process_lgrc9v3_collapse_reabsorption(
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        competing_sink_ids=[7, 13],
        selected_sink_id=7,
        losing_sink_ids=[13],
        transferred_node_ids=[13],
        lineage_transfer_map={13: "north_out-lineage"},
        source_lineage_ids={13: "east_out-lineage"},
        target_lineage_id="north_out-lineage",
        node_proper_time={7: 4.0, 13: 4.0},
        coherence_transfer_amount=0.0,
        budget_before=25.0,
        budget_after=25.0,
        event_time_key=5.0,
        scheduler_event_index=8,
        checkpoint_index=2,
        collapse_reabsorption_allowed=True,
    )
    artifact = result.to_artifact()
    validation = validate_lgrc9v3_topology_event_replay([artifact]).to_artifact()
    return {
        "topology_artifact": artifact,
        "topology_replay_validation": validation,
        "lineage_budget_passed": (
            abs(artifact["budget_error"]) <= 1e-12
            and validation["budget_conservation_valid"] is True
            and validation["lineage_continuity_valid"] is True
        ),
        "topology_event_kind": artifact["topology_event_kind"],
    }


def _surface_lineage_transport_probe() -> dict[str, Any]:
    fixed_row = _valid_surface_row()
    try:
        _valid_surface_row(
            surface_id="surface-row-19b-lineage-transport-attempt",
            lineage_status=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED,
        )
    except Exception as exc:  # noqa: BLE001 - artifact records exact fail-closed reason.
        return {
            "fixed_topology_surface_row_valid": fixed_row.lineage_status
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
            "lineage_transport_surface_row_constructed": False,
            "primary_blocker": "causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status",
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }
    return {
        "fixed_topology_surface_row_valid": True,
        "lineage_transport_surface_row_constructed": True,
        "primary_blocker": None,
        "exception_type": None,
        "exception_message": None,
    }


def build_report() -> dict[str, Any]:
    iter19a = _load_json(ITER19A_PATH)
    topology_probe = _native_topology_lineage_probe()
    surface_probe = _surface_lineage_transport_probe()
    controls = {
        "topology_disabled_baseline": {
            "passed_control": iter19a["status"] == "passed"
            and iter19a["checks"]["no_topology_events"]
            and iter19a["checks"]["no_port_rewiring"],
            "primary_reason": "iteration_19a_fixed_port_baseline_no_topology_events",
            "source_claim_ceiling": iter19a["claim_ceiling"],
        },
        "native_lgrc3_topology_lineage_available": {
            "passed_control": topology_probe["lineage_budget_passed"],
            "primary_reason": "native_lgrc3_collapse_reabsorption_replay_conserves_budget_and_lineage",
            "topology_event_kind": topology_probe["topology_event_kind"],
        },
        "pulse_surface_lineage_transport_blocked": {
            "passed_negative_control": surface_probe["lineage_transport_surface_row_constructed"]
            is False,
            "primary_blocker": surface_probe["primary_blocker"],
            "exception_type": surface_probe["exception_type"],
        },
        "topology_only_claim_promotion_blocked": {
            "passed_negative_control": True,
            "primary_blocker": "topology_lineage_evidence_without_pulse_surface_lineage_transport_cannot_promote_adaptive_movement",
        },
    }
    checks = {
        "iteration_19a_fixed_port_baseline_passed": iter19a["status"] == "passed",
        "native_lgrc3_topology_lineage_replay_passed": topology_probe["lineage_budget_passed"],
        "surface_v1_fixed_topology_row_valid": surface_probe["fixed_topology_surface_row_valid"],
        "surface_v1_rejects_lineage_transport_rows": (
            surface_probe["lineage_transport_surface_row_constructed"] is False
        ),
        "adaptive_topology_gate_passed": False,
        "topology_mutating_movement_gate_passed": False,
        "claim_ceiling_remains_19a": True,
        "broader_claims_blocked": True,
    }
    expected_fail_closed = (
        checks["iteration_19a_fixed_port_baseline_passed"]
        and checks["native_lgrc3_topology_lineage_replay_passed"]
        and checks["surface_v1_rejects_lineage_transport_rows"]
        and not checks["adaptive_topology_gate_passed"]
    )
    status = "passed" if expected_fail_closed else "failed"
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter19b_topology_lineage_adaptive_gate_v1",
        "iteration": "19-B",
        "status": status,
        "result_kind": "expected_fail_closed_boundary_probe",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S7_port_graph_fixed_composed_gate_v1",
        "geometry_scope": "topology_lineage_probe",
        "substrate_class": "port_graph",
        "source_artifacts": {"iteration_19a": _artifact_record(ITER19A_PATH)},
        "input_ceiling": iter19a["claim_ceiling"],
        "claim_ceiling": iter19a["claim_ceiling"],
        "attempted_promotion": "adaptive_topology_entry_candidate",
        "promotion_result": "blocked",
        "primary_blocker": surface_probe["primary_blocker"],
        "native_topology_lineage_probe": topology_probe,
        "surface_lineage_transport_probe": surface_probe,
        "controls": controls,
        "checks": checks,
        "claim_flags": {
            "native_m6": iter19a["claim_flags"]["native_m6"],
            "native_m6_candidate_gate_passed": iter19a["claim_flags"][
                "native_m6_candidate_gate_passed"
            ],
            "s7_fixed_port_composed_gate_candidate_passed": iter19a["claim_flags"][
                "s7_fixed_port_composed_gate_candidate_passed"
            ],
            "port_graph_transfer_claim_allowed": iter19a["claim_flags"][
                "port_graph_transfer_claim_allowed"
            ],
            "adaptive_topology_entry_allowed": False,
            "adaptive_topology_claim_allowed": False,
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
        },
        "blocked_claims": [
            "adaptive_topology_movement",
            "topology_mutating_movement",
            "native_pulse_surface_topology_lineage_transport",
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
        "next_work": {
            "option": "native_pulse_surface_lineage_transport_extension",
            "reason": (
                "LGRC-3 topology lineage evidence is available, but causal "
                "pulse-substrate surface rows v1 require fixed_topology "
                "lineage_status. Adaptive topology needs a surface lineage "
                "transport contract before it can be tested as movement evidence."
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
        "next_iteration": "review_native_pulse_surface_lineage_transport_extension",
    }


def write_report(report: dict[str, Any]) -> None:
    lines = [
        "# N04 Iteration 19-B S7 Topology-Lineage / Adaptive Gate",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        f"Promotion result: `{report['promotion_result']}`",
        "",
        f"Primary blocker: `{report['primary_blocker']}`",
        "",
        "Iteration 19-B tests whether the S7 fixed-port result can open adaptive topology.",
        "",
        "## Result",
        "",
        "Native LGRC-3 topology lineage replay is available and budget/lineage conserving, but causal pulse-substrate surface rows v1 require `fixed_topology` lineage status. The adaptive-topology gate therefore fails closed and the Iteration 19-A ceiling remains current.",
        "",
        "## Controls",
        "",
    ]
    for key, value in report["controls"].items():
        passed = value.get("passed_control", value.get("passed_negative_control"))
        reason = value.get("primary_reason", value.get("primary_blocker"))
        lines.append(f"- `{key}`: passed=`{passed}`, reason=`{reason}`")
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is a useful negative boundary result. It does not support adaptive topology, topology-mutating movement, native pulse-surface lineage transport, native LGRC choice selection, RC identity collapse, locomotion-like behavior, agency, identity acceptance, or unrestricted movement.",
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
