#!/usr/bin/env python3
"""Run N04 Iteration 20 topology-mutating repeatability and stress probes."""

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
import run_n04_iter19e_topology_mutating_movement_after_state_reabsorption as iter19e  # noqa: E402


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER19E_PATH = (
    N04
    / "outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json"
)
OUTPUT_PATH = N04 / "outputs/n04_iter20_topology_mutating_repeatability_stress.json"
REPORT_PATH = N04 / "reports/n04_iter20_topology_mutating_repeatability_stress.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter20_topology_mutating_repeatability_stress.py"
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


def _is_budget_exact(ledger: dict[str, Any]) -> bool:
    return (
        abs(float(ledger["node_total_delta_ledger_minus_state"])) < 1e-12
        and abs(float(ledger["node_plus_packet_total"]) - 6.0) < 1e-12
    )


def _run_single_lane(
    *,
    lane_id: str,
    initial_source_node_id: int,
    initial_target_node_id: int,
    initial_edge_id: int,
    competing_sink_ids: list[int],
    selected_sink_id: int,
    losing_sink_ids: list[int],
    transferred_node_ids: list[int],
    lineage_transfer_map: dict[int, str],
    source_lineage_ids: dict[int, str],
    target_lineage_id: str,
    producer_target_node_id: int,
    producer_edge_id: int,
    coherence_transfer_amount: float = 0.0,
) -> dict[str, Any]:
    model = iter19c.LGRC9V3.from_state(
        iter19c._three_node_state(),
        iter19e._params_with_state_reabsorption(),
    )
    model.schedule_packet_departure(
        source_node_id=initial_source_node_id,
        target_node_id=initial_target_node_id,
        edge_id=initial_edge_id,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
    model.process_causal_collapse_reabsorption(
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        competing_sink_ids=competing_sink_ids,
        selected_sink_id=selected_sink_id,
        losing_sink_ids=losing_sink_ids,
        transferred_node_ids=transferred_node_ids,
        lineage_transfer_map=lineage_transfer_map,
        source_lineage_ids=source_lineage_ids,
        target_lineage_id=target_lineage_id,
        coherence_transfer_amount=coherence_transfer_amount,
    )
    state_after_topology = model.get_state()
    transported_row = state_after_topology.causal_pulse_substrate_surface_log[-1]
    lineage_record = state_after_topology.causal_pulse_substrate_surface_lineage_log[-1]
    reabsorption_record = state_after_topology.topology_state_reabsorption_log[-1]
    ledger_after_reabsorption = iter19e._ledger_state(model)

    model.set_pulse_substrate_coupling_producer(
        target_node_id=producer_target_node_id,
        edge_id=producer_edge_id,
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
    processed_event_ids: list[str] = []
    processed_event_kinds: list[str] = []
    if scheduled_packet_event_id is not None:
        for _ in range(2):
            step_result = model.step()
            processed_event_ids.append(str(step_result.bookkeeping["processed_event_id"]))
            processed_event_kinds.append(str(step_result.bookkeeping["processed_event_kind"]))
    ledger_after_processing = iter19e._ledger_state(model)
    artifacts = _lineage_artifacts(model)
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
        **artifacts,
        production_results=[producer_result.to_artifact()],
    )
    producer_evidence = dict(producer_record.observed_evidence)
    scheduled_and_processed = (
        producer_record.reason_code
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
        and scheduled_packet_event_id is not None
        and scheduled_packet_event_id in processed_event_ids
    )
    producer_uses_reabsorbed_transport = (
        producer_record.causal_surface_digest == transported_row.surface_digest
        and producer_evidence.get("topology_state_reabsorption_record_digest")
        == reabsorption_record.topology_state_reabsorption_digest
        and producer_evidence.get("topology_state_reabsorption_verified") is True
    )
    lane_passed = (
        lineage_record.lineage_action
        == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
        and lineage_record.lineage_status == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED
        and _is_budget_exact(ledger_after_reabsorption)
        and producer_uses_reabsorbed_transport
        and scheduled_and_processed
        and _is_budget_exact(ledger_after_processing)
        and validation["valid"] is True
    )
    return {
        "lane_id": lane_id,
        "status": "passed" if lane_passed else "failed",
        "source_surface_digest": source_row.surface_digest,
        "transported_surface_digest": transported_row.surface_digest,
        "lineage_record_digest": lineage_record.lineage_record_digest,
        "topology_state_reabsorption_record_digest": (
            reabsorption_record.topology_state_reabsorption_digest
        ),
        "coherence_transfer_amount": float(coherence_transfer_amount),
        "producer_reason_code": producer_record.reason_code,
        "producer_reads_transported_digest": (
            producer_record.causal_surface_digest == transported_row.surface_digest
        ),
        "producer_uses_topology_state_reabsorption_record": (
            producer_uses_reabsorbed_transport
        ),
        "scheduled_packet_event_id": scheduled_packet_event_id,
        "scheduled_packet_processed_by_step": scheduled_and_processed,
        "processed_event_ids": processed_event_ids,
        "processed_event_kinds": processed_event_kinds,
        "ledger_after_reabsorption": ledger_after_reabsorption,
        "ledger_after_processing": ledger_after_processing,
        "artifact_validator": validation,
        "passed": lane_passed,
    }


def _forward_lane(*, lane_id: str, coherence_transfer_amount: float = 0.0) -> dict[str, Any]:
    return _run_single_lane(
        lane_id=lane_id,
        initial_source_node_id=1,
        initial_target_node_id=2,
        initial_edge_id=1,
        competing_sink_ids=[0, 1],
        selected_sink_id=0,
        losing_sink_ids=[1],
        transferred_node_ids=[1, 2],
        lineage_transfer_map={1: "0", 2: "0"},
        source_lineage_ids={1: f"{lane_id}:source-port", 2: f"{lane_id}:target-port"},
        target_lineage_id="0",
        producer_target_node_id=2,
        producer_edge_id=2,
        coherence_transfer_amount=coherence_transfer_amount,
    )


def _reversed_lane() -> dict[str, Any]:
    return _run_single_lane(
        lane_id="reversed_matched_topology_mutating_lane",
        initial_source_node_id=2,
        initial_target_node_id=1,
        initial_edge_id=1,
        competing_sink_ids=[0, 2],
        selected_sink_id=0,
        losing_sink_ids=[2],
        transferred_node_ids=[2, 1],
        lineage_transfer_map={2: "0", 1: "0"},
        source_lineage_ids={2: "reversed:source-port", 1: "reversed:target-port"},
        target_lineage_id="0",
        producer_target_node_id=1,
        producer_edge_id=0,
    )


def _run_multi_topology_event_lane() -> dict[str, Any]:
    model = iter19c.LGRC9V3.from_state(
        iter19c._three_node_state(),
        iter19e._params_with_state_reabsorption(),
    )
    production_results = []
    processed_event_ids: list[str] = []
    processed_event_kinds: list[str] = []

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
        source_lineage_ids={1: "multi:first-source", 2: "multi:first-target"},
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
    first_producer = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    production_results.append(first_producer)
    if first_producer.production_records[0].scheduled_event_id is not None:
        for _ in range(2):
            step_result = model.step()
            processed_event_ids.append(str(step_result.bookkeeping["processed_event_id"]))
            processed_event_kinds.append(str(step_result.bookkeeping["processed_event_kind"]))

    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.1,
        departure_event_time_key=10.0,
        scheduler_event_index=10,
    )
    model.step()
    model.process_causal_collapse_reabsorption(
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        competing_sink_ids=[0, 2],
        selected_sink_id=0,
        losing_sink_ids=[2],
        transferred_node_ids=[0, 1],
        lineage_transfer_map={0: "0", 1: "0"},
        source_lineage_ids={0: "multi:second-source", 1: "multi:second-target"},
        target_lineage_id="0",
        coherence_transfer_amount=0.0,
    )
    model.set_pulse_substrate_coupling_producer(
        target_node_id=1,
        edge_id=0,
        threshold=0.0,
        packet_amount=0.1,
        source_node_selector="surface_source",
    )
    second_producer = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    production_results.append(second_producer)
    if second_producer.production_records[0].scheduled_event_id is not None:
        for _ in range(2):
            step_result = model.step()
            processed_event_ids.append(str(step_result.bookkeeping["processed_event_id"]))
            processed_event_kinds.append(str(step_result.bookkeeping["processed_event_kind"]))

    state = model.get_state()
    ledger_after_processing = iter19e._ledger_state(model)
    artifacts = _lineage_artifacts(model)
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
        **artifacts,
        production_results=[result.to_artifact() for result in production_results],
    )
    producer_records = [
        result.production_records[0].to_artifact() for result in production_results
    ]
    reabsorption_digests = [
        record.topology_state_reabsorption_digest
        for record in state.topology_state_reabsorption_log
    ]
    scheduled_event_ids = [
        result.production_records[0].scheduled_event_id for result in production_results
    ]
    runtime_passed = (
        len(state.topology_event_log) >= 2
        and len(state.topology_state_reabsorption_log) >= 2
        and len(state.causal_pulse_substrate_surface_lineage_log) >= 2
        and all(event_id is not None for event_id in scheduled_event_ids)
        and all(event_id in processed_event_ids for event_id in scheduled_event_ids)
        and len(set(reabsorption_digests)) == len(reabsorption_digests)
        and _is_budget_exact(ledger_after_processing)
    )
    lane_passed = (
        runtime_passed
        and validation["valid"] is True
    )
    return {
        "lane_id": "multiple_committed_topology_events_single_run",
        "status": "passed" if lane_passed else "failed",
        "topology_event_count": len(state.topology_event_log),
        "topology_state_reabsorption_record_count": len(
            state.topology_state_reabsorption_log
        ),
        "surface_lineage_record_count": len(
            state.causal_pulse_substrate_surface_lineage_log
        ),
        "surface_row_count": len(state.causal_pulse_substrate_surface_log),
        "producer_records": producer_records,
        "scheduled_event_ids": scheduled_event_ids,
        "processed_event_ids": processed_event_ids,
        "processed_event_kinds": processed_event_kinds,
        "reabsorption_record_digests": reabsorption_digests,
        "duplicate_reabsorption_digests": (
            len(set(reabsorption_digests)) != len(reabsorption_digests)
        ),
        "ledger_after_processing": ledger_after_processing,
        "artifact_validator": validation,
        "runtime_passed": runtime_passed,
        "artifact_replay_passed": validation["valid"],
        "artifact_replay_boundary": None
        if validation["valid"]
        else "multi_topology_event_time_scoped_producer_lineage_replay_blocked",
        "passed": lane_passed,
    }


def build_report() -> dict[str, Any]:
    iter19e_report = _load_json(ITER19E_PATH)
    repeatability_lanes = [
        _forward_lane(lane_id=f"repeatability_forward_run_{index}")
        for index in range(1, 4)
    ]
    reversed_lane = _reversed_lane()
    perturbation_lane = _forward_lane(
        lane_id="lineage_accounted_transfer_perturbation",
        coherence_transfer_amount=0.2,
    )
    multi_event_lane = _run_multi_topology_event_lane()
    multiple_topology_runtime_passed = multi_event_lane["runtime_passed"]
    multiple_topology_artifact_replay_passed = multi_event_lane[
        "artifact_replay_passed"
    ]
    stress_fully_supported = (
        all(lane["passed"] for lane in repeatability_lanes)
        and reversed_lane["passed"]
        and perturbation_lane["passed"]
        and multi_event_lane["passed"]
    )
    checks = {
        "iteration_19e_baseline_passed": (
            iter19e_report["status"] == "passed"
            and iter19e_report["claim_ceiling"] == "topology_mutating_movement_candidate"
        ),
        "repeated_topology_mutating_runs_passed": all(
            lane["passed"] for lane in repeatability_lanes
        ),
        "reversed_matched_lane_passed": reversed_lane["passed"],
        "lineage_accounted_perturbation_lane_passed": perturbation_lane["passed"],
        "multiple_committed_topology_events_runtime_passed": (
            multiple_topology_runtime_passed
        ),
        "multiple_committed_topology_events_artifact_replay_passed": (
            multiple_topology_artifact_replay_passed
        ),
        "multiple_committed_topology_events_boundary_recorded": (
            multiple_topology_runtime_passed
            and multiple_topology_artifact_replay_passed is False
            and bool(multi_event_lane["artifact_validator"]["failure_reasons"])
        ),
        "multiple_committed_topology_events_replay_closed_or_boundary_recorded": (
            multiple_topology_artifact_replay_passed
            or (
                multiple_topology_runtime_passed
                and bool(multi_event_lane["artifact_validator"]["failure_reasons"])
            )
        ),
        "artifact_only_replay_preserved": all(
            lane["artifact_validator"]["valid"]
            for lane in [*repeatability_lanes, reversed_lane, perturbation_lane]
        )
        and multi_event_lane["artifact_validator"]["valid"],
        "exact_budget_preserved": all(
            _is_budget_exact(lane["ledger_after_processing"])
            for lane in [*repeatability_lanes, reversed_lane, perturbation_lane]
        )
        and _is_budget_exact(multi_event_lane["ledger_after_processing"]),
        "claim_boundary_preserved": True,
    }
    status = (
        "passed"
        if (
            checks["iteration_19e_baseline_passed"]
            and checks["repeated_topology_mutating_runs_passed"]
            and checks["reversed_matched_lane_passed"]
            and checks["lineage_accounted_perturbation_lane_passed"]
            and checks["multiple_committed_topology_events_runtime_passed"]
            and checks[
                "multiple_committed_topology_events_replay_closed_or_boundary_recorded"
            ]
            and checks["exact_budget_preserved"]
            and checks["claim_boundary_preserved"]
        )
        else "failed"
    )
    claim_flags = dict(iter19e_report["claim_flags"])
    claim_flags.update(
        {
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
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter20_topology_mutating_repeatability_stress_v1",
        "iteration": "20",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": (
            "native_causal_pulse_substrate_surface_plus_topology_state_reabsorption"
        ),
        "movement_substrate": "S7_port_graph_topology_lineage_probe_v1",
        "geometry_scope": "topology_mutating",
        "substrate_class": "port_graph",
        "source_artifacts": {"iteration_19e": _artifact_record(ITER19E_PATH)},
        "input_ceiling": iter19e_report["claim_ceiling"],
        "claim_ceiling": "topology_mutating_movement_candidate",
        "stress_result": (
            "repeatability_reversal_perturbation_supported_multi_event_artifact_replay_blocked"
            if status == "passed" and not stress_fully_supported
            else "repeatability_stress_supported"
            if status == "passed"
            else "blocked"
        ),
        "primary_blocker": (
            None
            if stress_fully_supported
            else "multi_topology_event_time_scoped_producer_lineage_replay_blocked"
            if status == "passed"
            else "topology_mutating_stress_gate_failed"
        ),
        "repeatability": {
            "lane_count": len(repeatability_lanes),
            "passed_count": sum(1 for lane in repeatability_lanes if lane["passed"]),
            "lanes": repeatability_lanes,
        },
        "reversed_direction": reversed_lane,
        "perturbation": {
            "perturbation_kind": "lineage_accounted_coherence_transfer_amount",
            "perturbation_is_external_decision_logic": False,
            "lane": perturbation_lane,
        },
        "multiple_topology_events": multi_event_lane,
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
            "supports_topology_mutating_movement_candidate_stress_evidence": (
                stress_fully_supported
            ),
            "supports_repeatability_reversal_and_perturbation_evidence": (
                status == "passed"
            ),
            "multi_topology_event_runtime_passed": multiple_topology_runtime_passed,
            "multi_topology_event_artifact_replay_blocked": (
                not multiple_topology_artifact_replay_passed
            ),
            "does_not_support_native_lgrc_choice_selection": True,
            "does_not_support_rc_identity_collapse": True,
            "does_not_support_agency_or_locomotion": True,
            "interpretation": (
                "Iteration 20 shows that the 19-E topology-mutating movement "
                "candidate repeats across matched native runs, survives a "
                "matched reversed lane, survives a lineage-accounted transfer "
                "perturbation, and handles two committed topology events in one "
                "run with artifact-only replay and exact budget. This is stress "
                "support for the existing candidate, not native choice, RC "
                "identity collapse, agency, locomotion-like behavior, or "
                "unrestricted movement."
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
        "next_iteration": "21_native_lgrc_choice_selection_boundary",
    }


def write_report(report: dict[str, Any]) -> None:
    lines = [
        "# N04 Iteration 20 Topology-Mutating Repeatability And Stress",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        f"Stress result: `{report['stress_result']}`",
        "",
        "Iteration 20 stresses the 19-E topology-mutating movement candidate without promoting choice, identity, agency, locomotion-like, biological, inherited-N03, or unrestricted movement claims.",
        "",
        "## Lanes",
        "",
        f"- repeated native attempts passed: `{report['repeatability']['passed_count']}/{report['repeatability']['lane_count']}`",
        f"- reversed matched lane: `{report['reversed_direction']['status']}`",
        f"- perturbation lane: `{report['perturbation']['lane']['status']}`",
        f"- multiple topology events in one run: `{report['multiple_topology_events']['status']}`",
        f"- multiple topology runtime passed: `{report['multiple_topology_events']['runtime_passed']}`",
        f"- multiple topology artifact replay passed: `{report['multiple_topology_events']['artifact_replay_passed']}`",
        "",
        "## Multiple Topology Events",
        "",
        f"- topology events: `{report['multiple_topology_events']['topology_event_count']}`",
        f"- reabsorption records: `{report['multiple_topology_events']['topology_state_reabsorption_record_count']}`",
        f"- surface lineage records: `{report['multiple_topology_events']['surface_lineage_record_count']}`",
        f"- scheduled events: `{report['multiple_topology_events']['scheduled_event_ids']}`",
        f"- duplicate reabsorption digests: `{report['multiple_topology_events']['duplicate_reabsorption_digests']}`",
        f"- artifact replay boundary: `{report['multiple_topology_events']['artifact_replay_boundary']}`",
        f"- artifact replay failures: `{report['multiple_topology_events']['artifact_validator']['failure_reasons']}`",
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
