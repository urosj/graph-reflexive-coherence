#!/usr/bin/env python3
"""Run N04 Iteration 19-C with native pulse-surface lineage transport."""

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
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygrc.core import PortGraphBackend  # noqa: E402
from pygrc.models import (  # noqa: E402
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    PortEdge,
    validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts,
)


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER19A_PATH = N04 / "outputs/n04_iter19a_s7_fixed_port_execution_report.json"
ITER19B_PATH = N04 / "outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json"
PHASE8_CLOSEOUT_PATH = (
    ROOT / "implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json"
)
OUTPUT_PATH = N04 / "outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json"
REPORT_PATH = N04 / "reports/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.py"
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


def _three_node_state() -> GRC9V3State:
    graph = PortGraphBackend()
    node_0 = graph.add_node({"label": "adaptive_sink"})
    node_1 = graph.add_node({"label": "source_port"})
    node_2 = graph.add_node({"label": "target_port"})
    edge_01 = graph.connect_ports(node_0, 0, node_1, 0, {"kind": "01"})
    edge_12 = graph.connect_ports(node_1, 1, node_2, 0, {"kind": "12"})
    edge_02 = graph.connect_ports(node_0, 1, node_2, 1, {"kind": "02"})
    return GRC9V3State(
        topology=graph,
        nodes={
            node_0: GRC9V3NodeState(coherence=1.0),
            node_1: GRC9V3NodeState(coherence=2.0),
            node_2: GRC9V3NodeState(coherence=3.0),
        },
        port_edges={
            edge_01: PortEdge(node_0, 1, node_1, 1, conductance=1.0, flux_uv=0.0),
            edge_12: PortEdge(node_1, 2, node_2, 1, conductance=1.0, flux_uv=0.0),
            edge_02: PortEdge(node_0, 2, node_2, 2, conductance=1.0, flux_uv=0.0),
        },
        base_conductance={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        geometric_length={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        temporal_delay={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        flux_coupling={edge_01: 0.0, edge_12: 0.0, edge_02: 0.0},
    )


def _params() -> dict[str, Any]:
    return {
        "dt": 1.0,
        "causal_modes": {
            "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_topology_integration_allowed": True,
            "causal_spark_expansion_allowed": True,
            "causal_refinement_packet_transport_allowed": True,
            "causal_proper_time_inheritance_allowed": True,
            "causal_collapse_reabsorption_allowed": True,
            "causal_identity_acceptance_allowed": False,
            "causal_pulse_substrate_surface_enabled": True,
            "causal_pulse_substrate_surface_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
            ),
            "causal_pulse_substrate_surface_validated": True,
            "causal_pulse_substrate_surface_lineage_transport_enabled": True,
            "causal_pulse_substrate_surface_lineage_transport_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
            ),
            "causal_pulse_substrate_surface_lineage_transport_validated": True,
            "causal_pulse_substrate_surface_lineage_transport_supported": True,
        },
    }


def _lineage_artifacts(model: LGRC9V3) -> dict[str, Any]:
    snapshot = model.snapshot()
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    return {
        "events": snapshot["events"],
        "surface_rows": runtime["causal_pulse_substrate_surface_log"],
        "surface_lineage_records": runtime["causal_pulse_substrate_surface_lineage_log"],
    }


def _run_transport_lane() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
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
    transported_row = model.get_state().causal_pulse_substrate_surface_log[-1]
    lineage_record = model.get_state().causal_pulse_substrate_surface_lineage_log[-1]
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=2,
        threshold=999.0,
        packet_amount=0.1,
        source_node_selector="surface_source",
    )
    producer_result = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    producer_record = producer_result.production_records[0]
    artifacts = _lineage_artifacts(model)
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
        events=artifacts["events"],
        surface_rows=artifacts["surface_rows"],
        surface_lineage_records=artifacts["surface_lineage_records"],
    )
    return {
        "source_surface_id": source_row.surface_id,
        "source_surface_digest": source_row.surface_digest,
        "topology_event_id": collapse_events[0].payload["topology_event_id"],
        "lineage_action": lineage_record.lineage_action,
        "lineage_status": lineage_record.lineage_status,
        "lineage_record_digest": lineage_record.lineage_record_digest,
        "transported_surface_id": transported_row.surface_id,
        "transported_surface_digest": transported_row.surface_digest,
        "producer_reason_code": producer_record.reason_code,
        "producer_causal_surface_digest": producer_record.causal_surface_digest,
        "producer_scheduled_event_id": producer_record.scheduled_event_id,
        "producer_references_transported_digest": (
            producer_record.causal_surface_digest == transported_row.surface_digest
        ),
        "producer_references_source_digest": (
            producer_record.causal_surface_digest == source_row.surface_digest
        ),
        "scheduled_packet_exists": producer_record.scheduled_event_id is not None,
        "artifact_validator": validation,
        "producer_linkage_validation_scope": {
            "producer_record_digest_available": False,
            "producer_record_validated_by_linkage": True,
            "linkage_fields": [
                "causal_surface_digest",
                "reason_code",
                "scheduled_event_id",
                "transported_surface_digest",
            ],
            "scope_limitation": (
                "19-C validates artifact-only surface lineage replay separately "
                "from producer linkage because the current producer record "
                "contract still lacks canonical producer_record_digest."
            ),
        },
        "artifact_chain": {
            "event_count": len(artifacts["events"]),
            "surface_row_count": len(artifacts["surface_rows"]),
            "surface_lineage_record_count": len(artifacts["surface_lineage_records"]),
            "production_record_count": len(producer_result.production_records),
        },
        "passed": (
            lineage_record.lineage_action
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
            and lineage_record.lineage_status
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED
            and producer_record.reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD
            and producer_record.causal_surface_digest == transported_row.surface_digest
            and producer_record.scheduled_event_id is None
            and validation["valid"] is True
        ),
    }


def _run_supersession_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
    model.process_causal_collapse_reabsorption(
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        competing_sink_ids=[0, 1],
        selected_sink_id=0,
        losing_sink_ids=[1],
        transferred_node_ids=[1],
        lineage_transfer_map={1: "0"},
        source_lineage_ids={1: "source-port"},
        target_lineage_id="0",
        coherence_transfer_amount=0.0,
    )
    lineage_record = model.get_state().causal_pulse_substrate_surface_lineage_log[-1]
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
    artifacts = _lineage_artifacts(model)
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
        events=artifacts["events"],
        surface_rows=artifacts["surface_rows"],
        surface_lineage_records=artifacts["surface_lineage_records"],
        production_results=[producer_result.to_artifact()],
    )
    return {
        "source_surface_id": source_row.surface_id,
        "source_surface_digest": source_row.surface_digest,
        "lineage_action": lineage_record.lineage_action,
        "lineage_status": lineage_record.lineage_status,
        "producer_reason_code": producer_record.reason_code,
        "producer_primary_blocker": producer_record.observed_evidence.get(
            "primary_blocker"
        ),
        "scheduled_packet_exists": producer_record.scheduled_event_id is not None,
        "artifact_validator": validation,
        "passed_negative_control": (
            producer_record.reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED
            and producer_record.observed_evidence.get("primary_blocker")
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED
            and producer_record.scheduled_event_id is None
            and validation["valid"] is True
        ),
    }


def _run_topology_only_promotion_control(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "passed_negative_control": (
            report["claim_flags"]["topology_mutating_movement_claim_allowed"] is False
            and report["claim_flags"]["movement_claim_allowed"] is False
            and report["claim_flags"]["adaptive_topology_entry_allowed"] is True
        ),
        "primary_blocker": "topology_lineage_transport_is_entry_evidence_not_topology_mutating_movement",
    }


def build_report() -> dict[str, Any]:
    iter19a = _load_json(ITER19A_PATH)
    iter19b = _load_json(ITER19B_PATH)
    phase8 = _load_json(PHASE8_CLOSEOUT_PATH)
    transport_lane = _run_transport_lane()
    supersession_control = _run_supersession_control()
    claim_flags = {
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
        "iteration_19b_boundary_passed_fail_closed": (
            iter19b["status"] == "passed"
            and iter19b["promotion_result"] == "blocked"
        ),
        "phase8_surface_lineage_transport_supported": (
            phase8["status"] == "passed"
            and phase8["supported"][
                "native_causal_pulse_substrate_surface_lineage_transport"
            ]
            is True
        ),
        "transported_surface_row_emitted": transport_lane["lineage_action"]
        == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
        "producer_reads_transported_digest": transport_lane[
            "producer_references_transported_digest"
        ],
        "producer_does_not_read_stale_source_digest": not transport_lane[
            "producer_references_source_digest"
        ],
        "artifact_only_lineage_replay_passed": transport_lane["artifact_validator"][
            "valid"
        ],
        "superseded_source_read_blocked": supersession_control[
            "passed_negative_control"
        ],
        "topology_mutating_movement_still_blocked": claim_flags[
            "topology_mutating_movement_claim_allowed"
        ]
        is False,
        "broader_claims_blocked": True,
    }
    adaptive_entry_passed = all(checks.values())
    claim_flags["adaptive_topology_entry_allowed"] = adaptive_entry_passed
    claim_ceiling = (
        "adaptive_topology_entry_candidate"
        if adaptive_entry_passed
        else "s7_fixed_port_composed_gate_candidate"
    )
    controls = {
        "transported_surface_successor_control": {
            "passed_positive_control": transport_lane["passed"],
            "primary_reason": "producer_reads_transported_successor_surface_digest",
        },
        "superseded_source_stale_read_control": {
            "passed_negative_control": supersession_control["passed_negative_control"],
            "primary_blocker": LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
        },
        "topology_only_claim_promotion_control": _run_topology_only_promotion_control(
            {"claim_flags": claim_flags}
        ),
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter19c_s7_adaptive_gate_with_native_surface_lineage_v1",
        "iteration": "19-C",
        "status": "passed" if adaptive_entry_passed else "failed",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S7_port_graph_fixed_composed_gate_v1",
        "geometry_scope": "topology_lineage_probe",
        "substrate_class": "port_graph",
        "source_artifacts": {
            "iteration_19a": _artifact_record(ITER19A_PATH),
            "iteration_19b": _artifact_record(ITER19B_PATH),
            "phase8_lineage_closeout": _artifact_record(PHASE8_CLOSEOUT_PATH),
        },
        "input_ceiling": iter19a["claim_ceiling"],
        "claim_ceiling": claim_ceiling,
        "attempted_promotion": "adaptive_topology_entry_candidate",
        "promotion_result": "supported" if adaptive_entry_passed else "blocked",
        "transport_lane": transport_lane,
        "supersession_control": supersession_control,
        "controls": controls,
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
            "supports_adaptive_topology_entry_candidate": adaptive_entry_passed,
            "does_not_support_topology_mutating_movement": True,
            "does_not_support_native_lgrc_choice_selection": True,
            "does_not_support_rc_identity_collapse": True,
            "does_not_support_agency_or_locomotion": True,
            "producer_record_digest_validated": False,
            "reason": (
                "19-C validates native pulse-surface lineage transport and "
                "lineage-current producer reads as an adaptive-topology entry "
                "gate over the S7 boundary, but it does not validate "
                "post-topology packet scheduling as movement, topology-mutating "
                "movement, choice semantics, or identity-collapse claims."
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
        "next_iteration": "taxonomy_closeout_or_topology_mutating_movement_review",
    }


def write_report(report: dict[str, Any]) -> None:
    lines = [
        "# N04 Iteration 19-C S7 Adaptive Gate With Native Surface Lineage",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        f"Promotion result: `{report['promotion_result']}`",
        "",
        "Iteration 19-C reruns the Iteration 19-B adaptive-topology entry gate after Phase 8 added native causal pulse-substrate surface lineage transport.",
        "",
        "## Positive Lineage Lane",
        "",
        f"- source surface digest: `{report['transport_lane']['source_surface_digest']}`",
        f"- transported surface digest: `{report['transport_lane']['transported_surface_digest']}`",
        f"- producer reads transported digest: `{report['transport_lane']['producer_references_transported_digest']}`",
        f"- artifact-only validator passed: `{report['transport_lane']['artifact_validator']['valid']}`",
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
            "This supports an adaptive-topology entry candidate only. Topology-mutating movement, native LGRC choice selection, RC identity collapse, semantic choice, agency, locomotion-like behavior, biological behavior, identity acceptance, inherited-N03 movement, and unrestricted movement remain blocked.",
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
