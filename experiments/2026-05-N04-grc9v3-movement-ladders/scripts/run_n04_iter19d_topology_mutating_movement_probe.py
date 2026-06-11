#!/usr/bin/env python3
"""Run N04 Iteration 19-D topology-mutating movement probe.

19-C established adaptive-topology entry evidence: surface rows can be
transported/superseded through committed topology events and producers can read
the transported digest. 19-D asks the stricter movement question: can native
post-topology packet work be scheduled and processed as movement evidence after
that topology event?
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
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pygrc.models import (  # noqa: E402
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts,
)

import run_n04_iter19c_s7_adaptive_gate_with_native_surface_lineage as iter19c  # noqa: E402


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER19A_PATH = N04 / "outputs/n04_iter19a_s7_fixed_port_execution_report.json"
ITER19C_PATH = (
    N04 / "outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json"
)
PHASE8_CLOSEOUT_PATH = (
    ROOT / "implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json"
)
OUTPUT_PATH = N04 / "outputs/n04_iter19d_topology_mutating_movement_probe.json"
REPORT_PATH = N04 / "reports/n04_iter19d_topology_mutating_movement_probe.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter19d_topology_mutating_movement_probe.py"
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


def _node_coherence_total(model: Any) -> float:
    return float(sum(node.coherence for node in model.get_state().base_state.nodes.values()))


def _topology_signature(model: Any) -> dict[str, Any]:
    topology = model.get_state().base_state.topology
    return {
        "nodes": sorted(int(node_id) for node_id in topology.iter_live_node_ids()),
        "edges": sorted(int(edge_id) for edge_id in topology.iter_live_edge_ids()),
    }


def _classify_exception(exc: BaseException) -> str:
    message = str(exc)
    if "node_coherence_total does not match state" in message:
        return "packet_ledger_state_reabsorption_mismatch_after_topology_event"
    if "requires unchanged fixed topology" in message:
        return "packet_ledger_fixed_topology_signature_blocks_post_topology_packet_work"
    if "source node" in message and "not live" in message:
        return "post_topology_source_node_not_live"
    if "target node" in message and "not live" in message:
        return "post_topology_target_node_not_live"
    return "post_topology_packet_work_failed_closed"


def _run_topology_mutating_movement_attempt() -> dict[str, Any]:
    model = iter19c.LGRC9V3.from_state(iter19c._three_node_state(), iter19c._params())
    topology_signature_before = _topology_signature(model)
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
    topology_signature_after_initial_packet = _topology_signature(model)
    collapse_events = model.process_causal_collapse_reabsorption(
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        competing_sink_ids=[0, 1],
        selected_sink_id=0,
        losing_sink_ids=[1],
        transferred_node_ids=[1, 2],
        lineage_transfer_map={1: "0", 2: "0"},
        source_lineage_ids={1: "source-port", 2: "target-port"},
        target_lineage_id="0",
        coherence_transfer_amount=0.0,
    )
    topology_signature_after_topology_event = _topology_signature(model)
    transported_row = model.get_state().causal_pulse_substrate_surface_log[-1]
    lineage_record = model.get_state().causal_pulse_substrate_surface_lineage_log[-1]
    ledger_after_topology = model.get_state().packet_ledger
    assert ledger_after_topology is not None
    ledger_state_after_topology = {
        "base_node_coherence_total": _node_coherence_total(model),
        "ledger_node_coherence_total": float(ledger_after_topology.node_coherence_total),
        "ledger_in_flight_packet_total": float(ledger_after_topology.in_flight_packet_total),
        "ledger_conserved_budget_total": float(
            ledger_after_topology.conserved_budget_total
        ),
        "node_total_delta_ledger_minus_state": float(
            ledger_after_topology.node_coherence_total - _node_coherence_total(model)
        ),
    }
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=2,
        threshold=0.0,
        packet_amount=0.1,
        source_node_selector="surface_source",
    )

    producer_result_artifact: dict[str, Any] | None = None
    producer_record_artifact: dict[str, Any] | None = None
    scheduled_packet_event_id: str | None = None
    processed_post_topology_packet = False
    failure: dict[str, Any] | None = None
    try:
        producer_result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        producer_result_artifact = producer_result.to_artifact()
        producer_record = producer_result.production_records[0]
        producer_record_artifact = producer_record.to_artifact()
        scheduled_packet_event_id = producer_record.scheduled_event_id
        if (
            producer_record.reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
            and scheduled_packet_event_id is not None
        ):
            model.step()
            processed_post_topology_packet = True
    except Exception as exc:  # noqa: BLE001 - experiment records fail-closed blocker.
        failure = {
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "primary_blocker": _classify_exception(exc),
        }

    artifacts = iter19c._lineage_artifacts(model)
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
        events=artifacts["events"],
        surface_rows=artifacts["surface_rows"],
        surface_lineage_records=artifacts["surface_lineage_records"],
    )
    topology_event_logged = len(model.get_state().topology_event_log) > 0
    active_graph_topology_mutated = (
        topology_signature_after_topology_event != topology_signature_before
    )
    topology_event_packet_work_supported = (
        failure is None
        and scheduled_packet_event_id is not None
        and processed_post_topology_packet
    )
    return {
        "source_surface_id": source_row.surface_id,
        "source_surface_digest": source_row.surface_digest,
        "topology_event_id": collapse_events[0].payload["topology_event_id"],
        "topology_event_logged": topology_event_logged,
        "active_graph_topology_mutated": active_graph_topology_mutated,
        "topology_signature_before": topology_signature_before,
        "topology_signature_after_initial_packet": topology_signature_after_initial_packet,
        "topology_signature_after_topology_event": topology_signature_after_topology_event,
        "lineage_action": lineage_record.lineage_action,
        "lineage_status": lineage_record.lineage_status,
        "lineage_record_digest": lineage_record.lineage_record_digest,
        "transported_surface_id": transported_row.surface_id,
        "transported_surface_digest": transported_row.surface_digest,
        "transported_surface_row_emitted": (
            lineage_record.lineage_action
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
            and lineage_record.lineage_status
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED
        ),
        "ledger_state_after_topology": ledger_state_after_topology,
        "post_topology_producer_attempted": True,
        "producer_result_artifact": producer_result_artifact,
        "producer_record_artifact": producer_record_artifact,
        "post_topology_packet_scheduled": scheduled_packet_event_id is not None,
        "scheduled_packet_event_id": scheduled_packet_event_id,
        "post_topology_packet_processed_by_step": processed_post_topology_packet,
        "post_topology_packet_work_supported": topology_event_packet_work_supported,
        "failure": failure,
        "artifact_validator": validation,
        "passed_fail_closed_probe": (
            topology_event_logged
            and not active_graph_topology_mutated
            and lineage_record.lineage_action
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
            and failure is not None
            and failure["primary_blocker"]
            == "packet_ledger_state_reabsorption_mismatch_after_topology_event"
            and validation["valid"] is True
        ),
        "required_runtime_mechanism": (
            "native topology-state reabsorption must update/rebase active graph "
            "state and packet ledger totals together before post-topology "
            "packet work can become topology-mutating movement evidence"
        ),
    }


def build_report() -> dict[str, Any]:
    iter19a = _load_json(ITER19A_PATH)
    iter19c_report = _load_json(ITER19C_PATH)
    phase8 = _load_json(PHASE8_CLOSEOUT_PATH)
    attempt = _run_topology_mutating_movement_attempt()
    subthreshold_entry_control = iter19c._run_transport_lane()
    supersession_control = iter19c._run_supersession_control()
    claim_flags = {
        "native_m6": iter19a["claim_flags"]["native_m6"],
        "native_m6_candidate_gate_passed": iter19a["claim_flags"][
            "native_m6_candidate_gate_passed"
        ],
        "s7_fixed_port_composed_gate_candidate_passed": iter19a["claim_flags"][
            "s7_fixed_port_composed_gate_candidate_passed"
        ],
        "adaptive_topology_entry_allowed": iter19c_report["claim_flags"][
            "adaptive_topology_entry_allowed"
        ],
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
    }
    checks = {
        "iteration_19a_fixed_port_baseline_passed": iter19a["status"] == "passed",
        "iteration_19c_adaptive_entry_passed": (
            iter19c_report["status"] == "passed"
            and iter19c_report["claim_ceiling"] == "adaptive_topology_entry_candidate"
        ),
        "phase8_surface_lineage_transport_supported": (
            phase8["status"] == "passed"
            and phase8["supported"][
                "native_causal_pulse_substrate_surface_lineage_transport"
            ]
            is True
        ),
        "committed_topology_event_logged": attempt["topology_event_logged"],
        "transported_surface_row_emitted": attempt["transported_surface_row_emitted"],
        "artifact_only_lineage_replay_still_passes": attempt["artifact_validator"][
            "valid"
        ],
        "post_topology_packet_work_attempted": attempt[
            "post_topology_producer_attempted"
        ],
        "post_topology_packet_work_not_supported": not attempt[
            "post_topology_packet_work_supported"
        ],
        "blocker_is_state_ledger_reabsorption_gap": (
            attempt["failure"] is not None
            and attempt["failure"]["primary_blocker"]
            == "packet_ledger_state_reabsorption_mismatch_after_topology_event"
        ),
        "subthreshold_entry_control_still_passes": subthreshold_entry_control["passed"],
        "superseded_source_read_control_still_passes": supersession_control[
            "passed_negative_control"
        ],
        "claim_boundary_preserved": (
            claim_flags["topology_mutating_movement_claim_allowed"] is False
            and claim_flags["movement_claim_allowed"] is False
            and claim_flags["adaptive_topology_entry_allowed"] is True
        ),
    }
    status = "passed" if all(checks.values()) else "failed"
    primary_blocker = (
        attempt["failure"]["primary_blocker"]
        if attempt["failure"] is not None
        else "topology_mutating_movement_support_not_blocked"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter19d_topology_mutating_movement_probe_v1",
        "iteration": "19-D",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S7_port_graph_topology_lineage_probe_v1",
        "geometry_scope": "topology_mutating",
        "substrate_class": "port_graph",
        "source_artifacts": {
            "iteration_19a": _artifact_record(ITER19A_PATH),
            "iteration_19c": _artifact_record(ITER19C_PATH),
            "phase8_lineage_closeout": _artifact_record(PHASE8_CLOSEOUT_PATH),
        },
        "input_ceiling": iter19c_report["claim_ceiling"],
        "claim_ceiling": iter19c_report["claim_ceiling"],
        "attempted_promotion": "topology_mutating_movement_candidate",
        "promotion_result": "blocked",
        "primary_blocker": primary_blocker,
        "topology_mutating_movement_attempt": attempt,
        "controls": {
            "subthreshold_entry_control": {
                "passed_positive_control": subthreshold_entry_control["passed"],
                "primary_reason": "adaptive_entry_without_post_topology_packet_work",
            },
            "superseded_source_stale_read_control": {
                "passed_negative_control": supersession_control[
                    "passed_negative_control"
                ],
                "primary_blocker": "producer_stale_surface_read_blocked",
            },
            "topology_only_claim_promotion_control": {
                "passed_negative_control": (
                    claim_flags["topology_mutating_movement_claim_allowed"] is False
                    and claim_flags["movement_claim_allowed"] is False
                ),
                "primary_blocker": (
                    "topology_lineage_transport_plus_logged_topology_event_is_not_"
                    "topology_mutating_movement"
                ),
            },
        },
        "checks": checks,
        "claim_flags": claim_flags,
        "blocked_claims": [
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
        "boundary": {
            "supports_adaptive_topology_entry_candidate": True,
            "does_not_support_topology_mutating_movement": True,
            "does_not_support_native_lgrc_choice_selection": True,
            "does_not_support_rc_identity_collapse": True,
            "does_not_support_agency_or_locomotion": True,
            "runtime_gap": attempt["required_runtime_mechanism"],
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
        "next_work": "lgrc_topology_state_reabsorption_support_or_n04_closeout",
    }


def write_report(report: dict[str, Any]) -> None:
    attempt = report["topology_mutating_movement_attempt"]
    failure = attempt["failure"] or {}
    lines = [
        "# N04 Iteration 19-D Topology-Mutating Movement Probe",
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
        "Iteration 19-D tests the stricter claim that topology-lineage entry can become post-topology packet work and topology-mutating movement evidence.",
        "",
        "## Topology-Mutating Movement Attempt",
        "",
        f"- topology event logged: `{attempt['topology_event_logged']}`",
        f"- active graph topology mutated: `{attempt['active_graph_topology_mutated']}`",
        f"- transported surface row emitted: `{attempt['transported_surface_row_emitted']}`",
        f"- post-topology packet scheduled: `{attempt['post_topology_packet_scheduled']}`",
        f"- post-topology packet processed by step: `{attempt['post_topology_packet_processed_by_step']}`",
        f"- artifact-only lineage replay passed: `{attempt['artifact_validator']['valid']}`",
        f"- node total delta ledger minus state: `{attempt['ledger_state_after_topology']['node_total_delta_ledger_minus_state']}`",
        f"- failure type: `{failure.get('exception_type')}`",
        f"- failure message: `{failure.get('message')}`",
        "",
        "## Controls",
        "",
    ]
    for key, value in report["controls"].items():
        passed = value.get("passed_positive_control", value.get("passed_negative_control"))
        reason = value.get("primary_reason", value.get("primary_blocker"))
        lines.append(f"- `{key}`: passed=`{passed}`, reason=`{reason}`")
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "19-D preserves the 19-C ceiling. Native surface lineage supports adaptive-topology entry, but actual topology-mutating movement remains blocked because current LGRC records the topology/lineage event and transports surface evidence without completing a native active-state plus packet-ledger reabsorption path for post-topology packet work.",
            "",
            "## Required Runtime Mechanism",
            "",
            report["boundary"]["runtime_gap"],
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
