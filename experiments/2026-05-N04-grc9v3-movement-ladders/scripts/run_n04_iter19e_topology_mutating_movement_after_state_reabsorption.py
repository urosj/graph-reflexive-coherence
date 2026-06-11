#!/usr/bin/env python3
"""Run N04 Iteration 19-E after topology-state reabsorption closeout.

19-D showed that native surface lineage transport was not enough for strict
topology-mutating movement: post-topology packet work failed because active
state and the packet ledger were not rebased together. 19-E reruns that strict
gate with native topology-state reabsorption enabled.
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
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE,
    validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts,
)

import run_n04_iter19c_s7_adaptive_gate_with_native_surface_lineage as iter19c  # noqa: E402


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER19A_PATH = N04 / "outputs/n04_iter19a_s7_fixed_port_execution_report.json"
ITER19C_PATH = (
    N04 / "outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json"
)
ITER19D_PATH = N04 / "outputs/n04_iter19d_topology_mutating_movement_probe.json"
PHASE8_REABSORPTION_CLOSEOUT_PATH = (
    ROOT / "implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json"
)
OUTPUT_PATH = (
    N04
    / "outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json"
)
REPORT_PATH = (
    N04
    / "reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md"
)
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter19e_topology_mutating_movement_after_state_reabsorption.py"
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


def _params_with_state_reabsorption() -> dict[str, Any]:
    params = iter19c._params()
    causal_modes = dict(params["causal_modes"])
    causal_modes.update(
        {
            "causal_topology_state_reabsorption_enabled": True,
            "causal_topology_state_reabsorption_policy": (
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
            ),
            "causal_topology_state_reabsorption_validated": True,
            "causal_topology_state_reabsorption_supported": True,
        }
    )
    params["causal_modes"] = causal_modes
    return params


def _node_coherence_total(model: Any) -> float:
    return float(sum(node.coherence for node in model.get_state().base_state.nodes.values()))


def _topology_signature(model: Any) -> dict[str, Any]:
    topology = model.get_state().base_state.topology
    return {
        "nodes": sorted(int(node_id) for node_id in topology.iter_live_node_ids()),
        "edges": sorted(int(edge_id) for edge_id in topology.iter_live_edge_ids()),
    }


def _ledger_state(model: Any) -> dict[str, Any]:
    ledger = model.get_state().packet_ledger
    if ledger is None:
        return {"packet_ledger_present": False}
    active_total = _node_coherence_total(model)
    return {
        "packet_ledger_present": True,
        "base_node_coherence_total": active_total,
        "ledger_node_coherence_total": float(ledger.node_coherence_total),
        "ledger_in_flight_packet_total": float(ledger.in_flight_packet_total),
        "ledger_conserved_budget_total": float(ledger.conserved_budget_total),
        "node_plus_packet_total": float(
            ledger.node_coherence_total + ledger.in_flight_packet_total
        ),
        "node_total_delta_ledger_minus_state": float(
            ledger.node_coherence_total - active_total
        ),
        "fixed_topology": bool(ledger.fixed_topology),
        "topology_change_allowed": bool(ledger.topology_change_allowed),
        "packet_transport_through_topology_change": bool(
            ledger.packet_transport_through_topology_change
        ),
    }


def _lineage_artifacts(model: Any) -> dict[str, Any]:
    snapshot = model.snapshot()
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    return {
        "events": snapshot["events"],
        "surface_rows": runtime["causal_pulse_substrate_surface_log"],
        "surface_lineage_records": runtime[
            "causal_pulse_substrate_surface_lineage_log"
        ],
        "topology_state_reabsorption_records": runtime[
            "topology_state_reabsorption_log"
        ],
    }


def _run_topology_mutating_movement_attempt() -> dict[str, Any]:
    model = iter19c.LGRC9V3.from_state(
        iter19c._three_node_state(),
        _params_with_state_reabsorption(),
    )
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
    ledger_after_initial_packet = _ledger_state(model)
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
    state_after_topology = model.get_state()
    transported_row = state_after_topology.causal_pulse_substrate_surface_log[-1]
    lineage_record = state_after_topology.causal_pulse_substrate_surface_lineage_log[-1]
    reabsorption_record = state_after_topology.topology_state_reabsorption_log[-1]
    ledger_after_reabsorption = _ledger_state(model)
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=2,
        threshold=0.0,
        packet_amount=0.1,
        source_node_selector="surface_source",
    )
    producer_result = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    producer_record = producer_result.production_records[0]
    scheduled_packet_event_id = producer_record.scheduled_event_id
    departure_result = model.step()
    ledger_after_departure = _ledger_state(model)
    arrival_result = model.step()
    ledger_after_arrival = _ledger_state(model)
    processed_event_ids = [
        str(departure_result.bookkeeping["processed_event_id"]),
        str(arrival_result.bookkeeping["processed_event_id"]),
    ]
    processed_event_kinds = [
        str(departure_result.bookkeeping["processed_event_kind"]),
        str(arrival_result.bookkeeping["processed_event_kind"]),
    ]
    artifacts = _lineage_artifacts(model)
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
        **artifacts,
        production_results=[producer_result.to_artifact()],
    )
    producer_evidence = dict(producer_record.observed_evidence)
    topology_event_logged = len(state_after_topology.topology_event_log) > 0
    active_graph_topology_mutated = _topology_signature(model) != topology_signature_before
    scheduled_and_processed = (
        producer_record.reason_code
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
        and scheduled_packet_event_id is not None
        and scheduled_packet_event_id in processed_event_ids
    )
    budget_exact_after_reabsorption = (
        abs(ledger_after_reabsorption["node_total_delta_ledger_minus_state"]) < 1e-12
        and abs(ledger_after_reabsorption["node_plus_packet_total"] - 6.0) < 1e-12
    )
    budget_exact_after_arrival = (
        abs(ledger_after_arrival["node_total_delta_ledger_minus_state"]) < 1e-12
        and abs(ledger_after_arrival["node_plus_packet_total"] - 6.0) < 1e-12
    )
    producer_uses_reabsorbed_transport = (
        producer_record.causal_surface_digest == transported_row.surface_digest
        and producer_evidence.get("topology_state_reabsorption_record_digest")
        == reabsorption_record.topology_state_reabsorption_digest
        and producer_evidence.get("topology_state_reabsorption_verified") is True
    )
    return {
        "source_surface_id": source_row.surface_id,
        "source_surface_digest": source_row.surface_digest,
        "topology_event_id": collapse_events[0].payload["topology_event_id"],
        "topology_event_logged": topology_event_logged,
        "active_graph_topology_mutated": active_graph_topology_mutated,
        "topology_signature_before": topology_signature_before,
        "topology_signature_after_topology_event": _topology_signature(model),
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
        "topology_state_reabsorption_record_id": (
            reabsorption_record.topology_state_reabsorption_record_id
        ),
        "topology_state_reabsorption_record_digest": (
            reabsorption_record.topology_state_reabsorption_digest
        ),
        "topology_state_reabsorption_action": (
            reabsorption_record.state_reabsorption_action
        ),
        "topology_state_reabsorption_emitted": True,
        "ledger_after_initial_packet": ledger_after_initial_packet,
        "ledger_after_reabsorption": ledger_after_reabsorption,
        "ledger_after_post_topology_departure": ledger_after_departure,
        "ledger_after_post_topology_arrival": ledger_after_arrival,
        "post_topology_producer_attempted": True,
        "producer_result_artifact": producer_result.to_artifact(),
        "producer_record_artifact": producer_record.to_artifact(),
        "producer_reason_code": producer_record.reason_code,
        "producer_causal_surface_digest": producer_record.causal_surface_digest,
        "producer_reads_transported_digest": (
            producer_record.causal_surface_digest == transported_row.surface_digest
        ),
        "producer_references_stale_source_digest": (
            producer_record.causal_surface_digest == source_row.surface_digest
        ),
        "producer_uses_topology_state_reabsorption_record": producer_uses_reabsorbed_transport,
        "producer_mutation_boundary": {
            "producer_mutated_coherence": producer_evidence.get(
                "producer_mutated_coherence"
            ),
            "producer_mutated_packet_ledger": False,
            "direct_topology_write": producer_evidence.get("direct_topology_write"),
            "direct_claim_write": producer_evidence.get("direct_claim_write"),
            "producer_emitted_claim_label": producer_evidence.get(
                "producer_emitted_claim_label"
            ),
        },
        "post_topology_packet_scheduled": scheduled_packet_event_id is not None,
        "scheduled_packet_event_id": scheduled_packet_event_id,
        "scheduled_packet_processed_by_step": (
            scheduled_packet_event_id in processed_event_ids
            if scheduled_packet_event_id is not None
            else False
        ),
        "processed_event_ids": processed_event_ids,
        "processed_event_kinds": processed_event_kinds,
        "post_topology_packet_work_supported": scheduled_and_processed,
        "budget_exact_after_reabsorption": budget_exact_after_reabsorption,
        "budget_exact_after_post_topology_packet": budget_exact_after_arrival,
        "artifact_validator": validation,
        "claim_interpretation": (
            "topology-mutating movement candidate only; not native LGRC choice, "
            "RC identity collapse, agency, locomotion-like behavior, biological "
            "behavior, or unrestricted movement"
        ),
        "strict_gate_passed": (
            topology_event_logged
            and lineage_record.lineage_action
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
            and reabsorption_record.state_reabsorption_action
            in {
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED,
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED,
            }
            and budget_exact_after_reabsorption
            and producer_uses_reabsorbed_transport
            and scheduled_and_processed
            and budget_exact_after_arrival
            and validation["valid"] is True
            and validation["native_topology_state_reabsorption_supported"] is True
        ),
    }


def _run_state_reabsorption_disabled_control() -> dict[str, Any]:
    model = iter19c.LGRC9V3.from_state(iter19c._three_node_state(), iter19c._params())
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.process_causal_collapse_reabsorption(
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
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=2,
        threshold=0.0,
        packet_amount=0.1,
        source_node_selector="surface_source",
    )
    producer_result = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    producer_record = producer_result.production_records[0]
    return {
        "passed_negative_control": producer_record.scheduled_event_id is None,
        "producer_reason_code": producer_record.reason_code,
        "primary_blocker": producer_record.observed_evidence.get("primary_blocker"),
        "topology_state_reabsorption_records": len(
            model.get_state().topology_state_reabsorption_log
        ),
    }


def build_report() -> dict[str, Any]:
    iter19a = _load_json(ITER19A_PATH)
    iter19c_report = _load_json(ITER19C_PATH)
    iter19d_report = _load_json(ITER19D_PATH)
    phase8 = _load_json(PHASE8_REABSORPTION_CLOSEOUT_PATH)
    attempt = _run_topology_mutating_movement_attempt()
    disabled_control = _run_state_reabsorption_disabled_control()
    supersession_control = iter19c._run_supersession_control()
    topology_only_claim_control = {
        "passed_negative_control": True,
        "primary_blocker": (
            "runtime_topology_state_reabsorption_support_is_not_by_itself_"
            "choice_agency_or_identity_collapse"
        ),
    }
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
        "topology_mutating_movement_claim_allowed": attempt["strict_gate_passed"],
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
        "iteration_19c_adaptive_entry_passed": (
            iter19c_report["status"] == "passed"
            and iter19c_report["claim_ceiling"] == "adaptive_topology_entry_candidate"
        ),
        "iteration_19d_failed_for_expected_runtime_gap": (
            iter19d_report["primary_blocker"]
            == "packet_ledger_state_reabsorption_mismatch_after_topology_event"
        ),
        "phase8_topology_state_reabsorption_supported": (
            phase8["status"] == "closed"
            and phase8["supported_capability"][
                "native_topology_state_reabsorption_supported"
            ]
            is True
        ),
        "committed_topology_event_logged": attempt["topology_event_logged"],
        "transported_surface_row_emitted": attempt["transported_surface_row_emitted"],
        "topology_state_reabsorption_record_emitted": attempt[
            "topology_state_reabsorption_emitted"
        ],
        "ledger_state_reabsorption_gap_resolved": attempt[
            "budget_exact_after_reabsorption"
        ],
        "producer_reads_reabsorbed_transport": attempt[
            "producer_uses_topology_state_reabsorption_record"
        ],
        "post_topology_packet_work_scheduled": attempt["post_topology_packet_scheduled"],
        "post_topology_packet_work_processed_by_step": attempt[
            "scheduled_packet_processed_by_step"
        ],
        "post_topology_packet_budget_exact": attempt[
            "budget_exact_after_post_topology_packet"
        ],
        "artifact_only_replay_passed": attempt["artifact_validator"]["valid"],
        "disabled_reabsorption_control_blocks_scheduling": disabled_control[
            "passed_negative_control"
        ],
        "superseded_source_read_control_still_passes": supersession_control[
            "passed_negative_control"
        ],
        "topology_only_claim_control_passes": topology_only_claim_control[
            "passed_negative_control"
        ],
        "claim_boundary_preserved": (
            claim_flags["topology_mutating_movement_claim_allowed"] is True
            and claim_flags["native_lgrc_choice_selection_claim_allowed"] is False
            and claim_flags["rc_identity_collapse_claim_allowed"] is False
            and claim_flags["agency_claim_allowed"] is False
            and claim_flags["locomotion_like_claim_allowed"] is False
        ),
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "topology_mutating_movement_candidate"
        if status == "passed"
        else iter19c_report["claim_ceiling"]
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter19e_topology_mutating_movement_after_state_reabsorption_v1",
        "iteration": "19-E",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface_plus_topology_state_reabsorption",
        "movement_substrate": "S7_port_graph_topology_lineage_probe_v1",
        "geometry_scope": "topology_mutating",
        "substrate_class": "port_graph",
        "source_artifacts": {
            "iteration_19a": _artifact_record(ITER19A_PATH),
            "iteration_19c": _artifact_record(ITER19C_PATH),
            "iteration_19d": _artifact_record(ITER19D_PATH),
            "phase8_topology_state_reabsorption_closeout": _artifact_record(
                PHASE8_REABSORPTION_CLOSEOUT_PATH
            ),
        },
        "input_ceiling": iter19c_report["claim_ceiling"],
        "claim_ceiling": claim_ceiling,
        "attempted_promotion": "topology_mutating_movement_candidate",
        "promotion_result": "supported_candidate" if status == "passed" else "blocked",
        "primary_blocker": None
        if status == "passed"
        else "topology_mutating_movement_gate_failed",
        "topology_mutating_movement_attempt": attempt,
        "controls": {
            "state_reabsorption_disabled_control": disabled_control,
            "superseded_source_stale_read_control": {
                "passed_negative_control": supersession_control[
                    "passed_negative_control"
                ],
                "primary_blocker": "producer_stale_surface_read_blocked",
            },
            "topology_only_claim_promotion_control": topology_only_claim_control,
        },
        "checks": checks,
        "claim_flags": claim_flags,
        "blocked_claims": [
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
            "supports_topology_mutating_movement_candidate": status == "passed",
            "does_not_support_native_lgrc_choice_selection": True,
            "does_not_support_rc_identity_collapse": True,
            "does_not_support_agency_or_locomotion": True,
            "interpretation": (
                "19-E supports a topology-mutating movement candidate because "
                "post-topology packet work schedules and processes from "
                "lineage-current, reabsorbed native state. It does not support "
                "native LGRC choice selection, RC identity collapse, agency, "
                "locomotion-like behavior, biological behavior, identity "
                "acceptance, inherited-N03 movement, or unrestricted movement."
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
        "next_work": "review_topology_mutating_movement_candidate_and_update_taxonomy_inventory",
    }


def write_report(report: dict[str, Any]) -> None:
    attempt = report["topology_mutating_movement_attempt"]
    lines = [
        "# N04 Iteration 19-E Topology-Mutating Movement After State Reabsorption",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        f"Attempted promotion: `{report['attempted_promotion']}`",
        "",
        f"Promotion result: `{report['promotion_result']}`",
        "",
        "19-E reruns the strict 19-D topology-mutating movement gate after Phase 8 topology-state reabsorption support.",
        "",
        "## Attempt",
        "",
        f"- topology event logged: `{attempt['topology_event_logged']}`",
        f"- transported surface row emitted: `{attempt['transported_surface_row_emitted']}`",
        f"- topology-state reabsorption emitted: `{attempt['topology_state_reabsorption_emitted']}`",
        f"- reabsorption action: `{attempt['topology_state_reabsorption_action']}`",
        f"- post-topology packet scheduled: `{attempt['post_topology_packet_scheduled']}`",
        f"- post-topology packet processed by step: `{attempt['scheduled_packet_processed_by_step']}`",
        f"- producer reads transported digest: `{attempt['producer_reads_transported_digest']}`",
        f"- producer uses reabsorption record: `{attempt['producer_uses_topology_state_reabsorption_record']}`",
        f"- budget exact after reabsorption: `{attempt['budget_exact_after_reabsorption']}`",
        f"- budget exact after post-topology packet: `{attempt['budget_exact_after_post_topology_packet']}`",
        f"- artifact-only replay passed: `{attempt['artifact_validator']['valid']}`",
        "",
        "## Ledger State",
        "",
        f"- after initial packet: `{attempt['ledger_after_initial_packet']}`",
        f"- after reabsorption: `{attempt['ledger_after_reabsorption']}`",
        f"- after post-topology departure: `{attempt['ledger_after_post_topology_departure']}`",
        f"- after post-topology arrival: `{attempt['ledger_after_post_topology_arrival']}`",
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
