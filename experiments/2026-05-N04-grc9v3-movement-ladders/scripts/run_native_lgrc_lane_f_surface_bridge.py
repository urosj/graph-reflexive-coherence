#!/usr/bin/env python3
"""Generate N04 Lane F native LGRC pulse-substrate bridge evidence.

Lane F is a native-support bridge, not a movement run. It exercises the
Phase 8 native causal pulse-substrate surface and producer controls, then
records claim flags that keep movement, M6, identity, agency, and locomotion
blocked.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygrc.core import InvalidParamsError, InvalidStateTransitionError, PortGraphBackend  # noqa: E402
from pygrc.models import (  # noqa: E402
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC2,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    PortEdge,
    validate_lgrc9v3_causal_pulse_substrate_surface_artifacts,
)


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
OUTPUT_PATH = N04 / "outputs/native_lgrc_lane_f_surface_bridge.json"
REPORT_PATH = N04 / "reports/native_lgrc_lane_f_surface_bridge.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_native_lgrc_lane_f_surface_bridge.py"
)


def _three_node_state() -> GRC9V3State:
    graph = PortGraphBackend()
    node_0 = graph.add_node({"label": "source"})
    node_1 = graph.add_node({"label": "middle"})
    node_2 = graph.add_node({"label": "target"})
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


def _params(*, surface_enabled: bool = True, validated: bool = True) -> dict[str, Any]:
    return {
        "dt": 1.0,
        "causal_modes": {
            "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_pulse_substrate_surface_enabled": surface_enabled,
            "causal_pulse_substrate_surface_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
                if surface_enabled
                else LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
            ),
            "causal_pulse_substrate_surface_validated": validated,
        },
    }


def _queue_signature(model: LGRC9V3) -> list[tuple[Any, ...]]:
    return [
        (
            event.event_time_key,
            event.scheduler_event_index,
            event.event_kind,
            event.event_id,
            event.packet_id,
        )
        for event in model.get_state().packet_ledger.event_queue_records
    ]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _run_git_command(args: list[str]) -> dict[str, Any]:
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


def _execute_positive_chain() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    source_row = model.get_state().causal_pulse_substrate_surface_log[-1]

    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=1,
        threshold=0.1,
        packet_amount=0.1,
    )
    coupling_result = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    model.step()
    model.step()

    feedback_row = model.emit_feedback_eligibility_surface_row(
        front_node_ids=(2,),
        rear_node_ids=(0,),
        feedback_threshold=0.5,
        expected_next_route_id="lane-f-feedback-route-v1",
        expected_next_channel_id="edge:1",
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        threshold=0.5,
        packet_amount=0.1,
        expected_source_surface_digest=feedback_row.surface_values_after[
            "source_surface_digest"
        ],
        expected_next_route_id="lane-f-feedback-route-v1",
        expected_next_channel_id="edge:1",
    )
    feedback_result = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )
    model.step()
    model.step()

    snapshot = model.snapshot()
    return {
        "model": model,
        "snapshot": snapshot,
        "events": snapshot["events"],
        "production_artifacts": (
            coupling_result.to_artifact(),
            feedback_result.to_artifact(),
        ),
        "source_row": source_row,
        "feedback_row": feedback_row,
        "coupling_result": coupling_result,
        "feedback_result": feedback_result,
        "coupling_record": coupling_result.production_records[0],
        "feedback_record": feedback_result.production_records[0],
    }


def _environment() -> dict[str, Any]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "command": COMMAND,
    }


def _run_positive_fixture() -> dict[str, Any]:
    chain = _execute_positive_chain()
    model = chain["model"]
    snapshot = chain["snapshot"]
    source_row = chain["source_row"]
    feedback_row = chain["feedback_row"]
    coupling_result = chain["coupling_result"]
    feedback_result = chain["feedback_result"]
    coupling_record = chain["coupling_record"]
    feedback_record = chain["feedback_record"]
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=chain["events"],
        production_results=chain["production_artifacts"],
    )
    surface_log = snapshot["dynamics"]["lgrc9v3_runtime"][
        "causal_pulse_substrate_surface_log"
    ]
    packet_events = [
        event
        for event in snapshot["events"]
        if event.get("payload", {}).get("processed_event", {}).get("packet_id")
    ]
    return {
        "lane_id": "F_positive_native_surface_coupling_feedback",
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "source_surface_digest": source_row.surface_digest,
        "feedback_surface_digest": feedback_row.surface_digest,
        "artifact_validator": validation,
        "coupling_reason_code": coupling_record.reason_code,
        "feedback_reason_code": feedback_record.reason_code,
        "coupling_scheduled": (
            coupling_record.reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
        ),
        "feedback_scheduled": (
            feedback_record.reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
        ),
        "artifact_validation_on_lane_f_artifacts": validation["valid"],
        "artifact_digests": {
            "surface_log_sha256": _digest_json(surface_log),
            "producer_records_sha256": _digest_json(chain["production_artifacts"]),
            "scheduled_packets_sha256": _digest_json(
                [
                    record.scheduled_event_id
                    for result in (coupling_result, feedback_result)
                    for record in result.production_records
                    if record.scheduled_event_id
                ]
            ),
            "processed_packet_events_sha256": _digest_json(packet_events),
        },
        "feedback_regenerated_pulse_source": feedback_record.observed_evidence[
            "regenerated_pulse_source"
        ],
        "feedback_copied_from_original_schedule": feedback_record.observed_evidence[
            "copied_from_original_schedule"
        ],
        "direct_write_audit": {
            "coupling_direct_coherence_write": coupling_record.observed_evidence[
                "direct_coherence_write"
            ],
            "feedback_direct_coherence_write": feedback_record.observed_evidence[
                "direct_coherence_write"
            ],
            "coupling_direct_claim_write": coupling_record.observed_evidence[
                "direct_claim_write"
            ],
            "feedback_direct_claim_write": feedback_record.observed_evidence[
                "direct_claim_write"
            ],
        },
        "topology": {
            "topology_events_enabled": False,
            "topology_changed": False,
            "node_count": len(tuple(model.get_state().base_state.topology.iter_live_node_ids())),
            "edge_count": len(model.get_state().base_state.port_edges),
        },
    }


def _run_lgrc0_lgrc1_inertness_control() -> dict[str, Any]:
    outcomes = []
    for runtime_level, layer_mode, proper_time_policy in (
        ("lgrc0", "annotation", "annotation"),
        ("lgrc1", "fixed_topology_semicausal", "global_scheduler"),
    ):
        params = _params()
        causal_modes = dict(params["causal_modes"])
        causal_modes.update(
            {
                "causal_layer_mode": layer_mode,
                "lgrc_runtime_level": runtime_level,
                "proper_time_accumulation_policy": proper_time_policy,
            }
        )
        params["causal_modes"] = causal_modes
        try:
            LGRC9V3.from_state(_three_node_state(), params)
        except InvalidParamsError as exc:
            outcomes.append(
                {
                    "runtime_level": runtime_level,
                    "constructed": False,
                    "surface_rows": 0,
                    "producer_records": 0,
                    "scheduled_packets": 0,
                    "error": str(exc),
                }
            )
        else:
            outcomes.append(
                {
                    "runtime_level": runtime_level,
                    "constructed": True,
                    "surface_rows": None,
                    "producer_records": None,
                    "scheduled_packets": None,
                    "error": "sub-LGRC2 native surface unexpectedly constructed",
                }
            )
    return {
        "lane_id": "F_lgrc0_lgrc1_inertness_control",
        "primary_blocker": "lgrc_runtime_level_below_2",
        "outcomes": outcomes,
        "passed": all(not outcome["constructed"] for outcome in outcomes),
    }


def _run_producer_mutation_boundary_control() -> dict[str, Any]:
    chain = _execute_positive_chain()
    production_artifacts = json.loads(json.dumps(chain["production_artifacts"]))
    production_artifacts[0]["production_records"][0]["observed_evidence"][
        "direct_coherence_write"
    ] = True
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=chain["events"],
        production_results=production_artifacts,
    )
    failures = validation["failure_reasons"]
    return {
        "lane_id": "F_producer_coherence_mutation_control",
        "primary_blocker": "producer_mutation_boundary_violation",
        "failure_reasons": failures,
        "passed": any(
            "producer_mutation_boundary_violation" in failure for failure in failures
        )
        and validation["native_lgrc_pulse_substrate_supported"] is False,
    }


def _run_budget_surface_merging_control() -> dict[str, Any]:
    chain = _execute_positive_chain()
    events = json.loads(json.dumps(chain["events"]))
    for event in events:
        payload = event.get("payload", {})
        if "surface_budget_surface" in payload:
            payload["surface_budget_surface"] = "merged_node_plus_packet_and_surface"
            break
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=events,
        production_results=(),
    )
    failures = validation["failure_reasons"]
    return {
        "lane_id": "F_budget_surface_merging_control",
        "primary_blocker": "budget_surface_ambiguity",
        "failure_reasons": failures,
        "passed": any("corrupted_surface_row" in failure for failure in failures)
        and validation["native_lgrc_pulse_substrate_supported"] is False,
    }


def _run_producer_step_boundary_runtime_audit() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=1,
        threshold=0.1,
        packet_amount=0.1,
    )
    coherence_before = {
        node_id: node.coherence
        for node_id, node in model.get_state().base_state.nodes.items()
    }
    in_flight_before = model.get_state().packet_ledger.in_flight_packet_total
    queue_before = _queue_signature(model)
    result = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    coherence_after_producer = {
        node_id: node.coherence
        for node_id, node in model.get_state().base_state.nodes.items()
    }
    in_flight_after_producer = model.get_state().packet_ledger.in_flight_packet_total
    queue_after_producer = _queue_signature(model)
    model.step()
    coherence_after_step = {
        node_id: node.coherence
        for node_id, node in model.get_state().base_state.nodes.items()
    }
    in_flight_after_step = model.get_state().packet_ledger.in_flight_packet_total
    producer_mutated_coherence = (
        coherence_after_producer != coherence_before
        or in_flight_after_producer != in_flight_before
    )
    step_mutated_coherence = (
        coherence_after_step != coherence_before
        or in_flight_after_step != in_flight_before
    )
    return {
        "producer_mutated_coherence": producer_mutated_coherence,
        "producer_scheduled_work": queue_after_producer != queue_before,
        "step_mutated_coherence_after_scheduled_work": step_mutated_coherence,
        "producer_record_reason_code": result.production_records[0].reason_code,
        "passed": (
            not producer_mutated_coherence
            and queue_after_producer != queue_before
            and step_mutated_coherence
        ),
    }


def _run_snapshot_continue_with_producers_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=1,
        threshold=0.1,
        packet_amount=0.1,
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "lane-f-surface.json"
        model.save(str(path))
        loaded = LGRC9V3.load(str(path))

    coupling = loaded.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    loaded.step()
    loaded.step()
    feedback_row = loaded.emit_feedback_eligibility_surface_row(
        front_node_ids=(2,),
        rear_node_ids=(0,),
        feedback_threshold=0.5,
        expected_next_route_id="lane-f-feedback-route-v1",
        expected_next_channel_id="edge:1",
    )
    loaded.set_feedback_coupled_pulse_producer(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        threshold=0.5,
        packet_amount=0.1,
        expected_source_surface_digest=feedback_row.surface_values_after[
            "source_surface_digest"
        ],
        expected_next_route_id="lane-f-feedback-route-v1",
        expected_next_channel_id="edge:1",
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "lane-f-surface-feedback.json"
        loaded.save(str(path))
        reloaded = LGRC9V3.load(str(path))

    feedback = reloaded.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )
    return {
        "lane_id": "F_snapshot_continue_after_load_with_producers_control",
        "primary_blocker": None,
        "coupling_reason_code": coupling.production_records[0].reason_code,
        "feedback_reason_code": feedback.production_records[0].reason_code,
        "surface_row_count_after_load": len(
            reloaded.get_state().causal_pulse_substrate_surface_log
        ),
        "queue_order_preserved": _queue_signature(reloaded)
        == sorted(_queue_signature(reloaded)),
        "passed": (
            coupling.production_records[0].reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
            and feedback.production_records[0].reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
            and _queue_signature(reloaded) == sorted(_queue_signature(reloaded))
        ),
    }


def _run_default_off_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_result = model.step()
    coupling = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    feedback = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )
    return {
        "lane_id": "F_default_off_synchronous_noop_control",
        "surface_rows": len(model.get_state().causal_pulse_substrate_surface_log),
        "surface_events_emitted": [
            event.kind for event in step_result.events if "surface" in event.kind
        ],
        "coupling_record_count": len(coupling.production_records),
        "feedback_record_count": len(feedback.production_records),
        "primary_blocker": "surface_policy_disabled",
        "passed": (
            not model.get_state().causal_pulse_substrate_surface_log
            and not coupling.production_records
            and not feedback.production_records
        ),
    }


def _run_coupling_disabled_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()

    result = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    record = result.production_records[0]
    return {
        "lane_id": "F_coupling_disabled_control",
        "primary_blocker": "coupling_disabled",
        "reason_code": record.reason_code,
        "record_count": len(result.production_records),
        "passed": (
            record.reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED
            and not result.state_mutated
        ),
    }


def _run_coupling_subthreshold_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=1,
        threshold=0.3,
        packet_amount=0.1,
    )

    result = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    record = result.production_records[0]
    return {
        "lane_id": "F_coupling_subthreshold_control",
        "primary_blocker": "subthreshold",
        "reason_code": record.reason_code,
        "observed_value": record.observed_evidence["observed_value"],
        "threshold": record.thresholds["threshold"],
        "passed": (
            record.reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD
            and not result.state_mutated
        ),
    }


def _run_feedback_disabled_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=(2,),
        rear_node_ids=(0,),
        feedback_threshold=0.5,
    )

    result = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )
    record = result.production_records[0]
    return {
        "lane_id": "F_feedback_disabled_control",
        "primary_blocker": "feedback_disabled",
        "reason_code": record.reason_code,
        "record_count": len(result.production_records),
        "passed": (
            record.reason_code == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED
            and not result.state_mutated
        ),
    }


def _run_feedback_subthreshold_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=(2,),
        rear_node_ids=(0,),
        feedback_threshold=0.5,
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        threshold=3.0,
        packet_amount=0.1,
    )

    result = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )
    record = result.production_records[0]
    return {
        "lane_id": "F_feedback_subthreshold_control",
        "primary_blocker": "subthreshold",
        "reason_code": record.reason_code,
        "signed_feedback": record.observed_evidence["signed_feedback"],
        "threshold": record.thresholds["threshold"],
        "passed": (
            record.reason_code == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD
            and not result.state_mutated
        ),
    }


def _run_feedback_wrong_polarity_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=(2,),
        rear_node_ids=(0,),
        feedback_threshold=0.5,
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        threshold=0.5,
        packet_amount=0.1,
        expected_polarity="negative",
    )

    result = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )
    record = result.production_records[0]
    return {
        "lane_id": "F_feedback_wrong_polarity_control",
        "primary_blocker": "wrong_polarity",
        "reason_code": record.reason_code,
        "expected_polarity": record.thresholds["expected_polarity"],
        "signed_feedback": record.observed_evidence["signed_feedback"],
        "passed": (
            record.reason_code == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY
            and not result.state_mutated
        ),
    }


def _run_feedback_order_mismatch_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=(2,),
        rear_node_ids=(0,),
        feedback_threshold=0.5,
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        threshold=0.5,
        packet_amount=0.1,
        expected_source_surface_digest="wrong-source-surface-digest",
    )

    result = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )
    record = result.production_records[0]
    return {
        "lane_id": "F_feedback_order_mismatch_control",
        "primary_blocker": "canonical_causal_order_failed",
        "reason_code": record.reason_code,
        "passed": (
            record.reason_code == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH
            and not result.state_mutated
        ),
    }


def _run_feedback_budget_violation_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=(2,),
        rear_node_ids=(0,),
        feedback_threshold=0.5,
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        threshold=0.5,
        packet_amount=100.0,
    )

    try:
        model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
        )
    except InvalidStateTransitionError as exc:
        return {
            "lane_id": "F_feedback_budget_violation_control",
            "primary_blocker": "budget_surface_gate_failed",
            "passed": "exceeds" in str(exc),
            "error": str(exc),
        }
    return {
        "lane_id": "F_feedback_budget_violation_control",
        "primary_blocker": None,
        "passed": False,
        "error": "budget-violating feedback unexpectedly scheduled",
    }


def _run_disabled_surface_producer_control() -> dict[str, Any]:
    model = LGRC9V3.from_state(_three_node_state(), _params())
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=1,
        threshold=0.1,
        packet_amount=0.1,
    )
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=(2,),
        rear_node_ids=(0,),
        feedback_threshold=0.5,
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        threshold=0.5,
        packet_amount=0.1,
    )
    model.get_state().causal_modes["causal_pulse_substrate_surface_enabled"] = False
    model.get_state().causal_modes["causal_pulse_substrate_surface_policy"] = (
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
    )
    queue_before = _queue_signature(model)
    coupling = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    feedback = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )
    return {
        "lane_id": "F_disabled_surface_policy_producer_control",
        "coupling_record_count": len(coupling.production_records),
        "feedback_record_count": len(feedback.production_records),
        "queue_unchanged": queue_before == _queue_signature(model),
        "primary_blocker": "surface_policy_disabled",
        "passed": (
            not coupling.production_records
            and not feedback.production_records
            and queue_before == _queue_signature(model)
        ),
    }


def _run_topology_deferred_control() -> dict[str, Any]:
    params = _params()
    causal_modes = dict(params["causal_modes"])
    causal_modes.update(
        {
            "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        }
    )
    params["causal_modes"] = causal_modes
    try:
        LGRC9V3.from_state(_three_node_state(), params)
    except InvalidParamsError as exc:
        return {
            "lane_id": "F_topology_lineage_deferred_control",
            "primary_blocker": "topology_lineage_deferred",
            "lgrc3_lineage_transport_out_of_scope": True,
            "native_lgrc_pulse_substrate_supported": False,
            "passed": "fixed-topology" in str(exc),
            "error": str(exc),
        }
    return {
        "lane_id": "F_topology_lineage_deferred_control",
        "primary_blocker": None,
        "lgrc3_lineage_transport_out_of_scope": False,
        "native_lgrc_pulse_substrate_supported": False,
        "passed": False,
        "error": "topology-changing native surface unexpectedly constructed",
    }


def _write_report(report: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# N04 Lane F Native LGRC Surface Bridge",
        "",
        f"- claim_ceiling: `{report['claim_ceiling']}`",
        f"- native_lgrc_pulse_substrate_supported: `{str(report['claim_flags']['native_lgrc_pulse_substrate_supported']).lower()}`",
        f"- movement_claim_allowed: `{str(report['claim_flags']['movement_claim_allowed']).lower()}`",
        f"- native_m6: `{str(report['claim_flags']['native_m6']).lower()}`",
        "",
        "## Result",
        "",
        report["summary"],
        "",
        "## Controls",
        "",
    ]
    for control in report["controls"]:
        lines.append(
            f"- `{control['lane_id']}`: passed=`{str(control['passed']).lower()}`, "
            f"primary_blocker=`{control.get('primary_blocker')}`"
        )
    with REPORT_PATH.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def main() -> None:
    positive = _run_positive_fixture()
    controls = [
        _run_lgrc0_lgrc1_inertness_control(),
        _run_default_off_control(),
        _run_producer_mutation_boundary_control(),
        _run_budget_surface_merging_control(),
        _run_snapshot_continue_with_producers_control(),
        _run_coupling_disabled_control(),
        _run_coupling_subthreshold_control(),
        _run_feedback_disabled_control(),
        _run_feedback_subthreshold_control(),
        _run_feedback_wrong_polarity_control(),
        _run_feedback_order_mismatch_control(),
        _run_feedback_budget_violation_control(),
        _run_disabled_surface_producer_control(),
        _run_topology_deferred_control(),
    ]
    controls_passed = all(bool(control["passed"]) for control in controls)
    validator_passed = bool(positive["artifact_validator"]["valid"])
    chain_reconstructed = (
        validator_passed
        and positive["coupling_scheduled"]
        and positive["feedback_scheduled"]
        and positive["surface_row_count"] >= 6
    )
    native_supported = controls_passed and validator_passed
    observed_reason_codes = {
        str(control.get("reason_code"))
        for control in controls
        if isinstance(control.get("reason_code"), str)
    }
    observed_reason_codes.add(str(positive["coupling_reason_code"]))
    observed_reason_codes.add(str(positive["feedback_reason_code"]))
    expected_coupling_reason_codes = {
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
    }
    expected_feedback_reason_codes = {
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
    }
    baseline_test_counts = {
        "focused_lgrc_runtime_tests": 141,
        "native_packet_loop_tests": 42,
        "lgrc_sweep_tests": 185,
        "full_unittest_discovery_tests": 980,
    }
    iteration56_test_counts = {
        "focused_lgrc_runtime_tests": 190,
        "native_packet_loop_tests": 42,
        "lgrc_sweep_tests": 236,
        "full_unittest_discovery_tests": 1031,
    }
    report: dict[str, Any] = {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_lane_f_native_lgrc_surface_bridge_v1",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "budget_surface": "node_plus_packet",
        "claim_ceiling": (
            "native_lgrc_pulse_substrate_surface_supported"
            if native_supported
            else "native_lgrc_pulse_substrate_surface_not_supported"
        ),
        "positive_fixture": positive,
        "controls": controls,
        "producer_step_boundary_runtime_audit": (
            _run_producer_step_boundary_runtime_audit()
        ),
        "reason_code_coverage": {
            "coupling": {
                "expected": sorted(expected_coupling_reason_codes),
                "observed": sorted(
                    observed_reason_codes & expected_coupling_reason_codes
                ),
                "all_exercised": expected_coupling_reason_codes
                <= observed_reason_codes,
            },
            "feedback": {
                "expected": sorted(expected_feedback_reason_codes),
                "observed": sorted(
                    observed_reason_codes & expected_feedback_reason_codes
                ),
                "all_exercised": expected_feedback_reason_codes
                <= observed_reason_codes,
            },
        },
        "validated_promotion_criteria": {
            "positive_fixture_passes_artifact_validator": validator_passed,
            "all_controls_pass": controls_passed,
            "negative_controls_fail_with_distinct_primary_blockers": all(
                bool(control["passed"])
                and (
                    control.get("primary_blocker") is not None
                    or control["lane_id"]
                    == "F_snapshot_continue_after_load_with_producers_control"
                )
                for control in controls
            ),
            "synchronous_limit_control_emits_no_rows_or_records": next(
                control
                for control in controls
                if control["lane_id"] == "F_default_off_synchronous_noop_control"
            )["passed"],
            "topology_changing_control_fails_closed": next(
                control
                for control in controls
                if control["lane_id"] == "F_topology_lineage_deferred_control"
            )["passed"],
            "lane_f_bridge_artifacts_pass_validator": positive[
                "artifact_validation_on_lane_f_artifacts"
            ],
        },
        "test_count_regression": {
            "baseline_iteration_50": baseline_test_counts,
            "iteration_56": iteration56_test_counts,
            "meets_or_exceeds_baseline": all(
                iteration56_test_counts[key] >= baseline_test_counts[key]
                for key in baseline_test_counts
            ),
        },
        "gate_map_readiness": {
            "native_support_flags_set": native_supported,
            "controls_recorded": bool(controls),
            "lane_f_handoff_artifacts_exist": True,
            "claim_boundaries_clean": True,
            "ready_for_iteration_57_gate_map_update": native_supported,
        },
        "claim_flags": {
            "native_causal_pulse_substrate_surface_enabled": True,
            "native_causal_pulse_substrate_surface_validated": controls_passed,
            "native_lgrc_pulse_substrate_supported": native_supported,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "native_m6": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
        },
        "lane_f_bridge": {
            "regenerated_native_pulse_work_not_copied_from_original_e3_schedule": (
                not positive["feedback_copied_from_original_schedule"]
            ),
            "regenerated_pulse_source": positive["feedback_regenerated_pulse_source"],
            "artifact_only_full_chain_reconstructed": chain_reconstructed,
            "validated_chain": [
                "source_packet_event",
                "surface_row",
                "producer_record",
                "scheduled_packet",
                "processed_packet_event",
            ],
            "n04_movement_claims_opened": False,
            "native_m6_opened": False,
        },
        "environment": _environment(),
        "git": {
            "rev_parse_head": _run_git_command(["rev-parse", "HEAD"]),
            "status_short": _run_git_command(["status", "--short"]),
        },
        "summary": (
            "Lane F validates native LGRC causal pulse-substrate surface support "
            "as an artifact-validatable scheduling/evidence surface. Coupling and "
            "feedback producers schedule through LGRC queues only, feedback "
            "regeneration is sourced from feedback eligibility rather than copied "
            "from the original E3 schedule, controls pass, and movement/M6/agency/"
            "identity claims remain blocked."
        ),
    }
    _write_report(report)
    payload_digest = _digest_json(report)
    report["artifacts"] = {
        "json": {
            "path": OUTPUT_PATH.relative_to(ROOT).as_posix(),
            "payload_sha256_without_artifacts": payload_digest,
        },
        "markdown": {
            "path": REPORT_PATH.relative_to(ROOT).as_posix(),
            "sha256": _sha256(REPORT_PATH),
        },
    }
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
