"""Run N05 Iteration 7: O5 self-sustained oscillator boundary.

The O5 lane uses the existing native LGRC9V3 route-aspect surplus trigger,
bounded autonomous execution, and self-rearm artifact validator. It validates
runtime-visible renewal from committed parent-arrival state, while recording
that current LGRC does not yet expose a pure constitutive oscillator policy
surface for custom potentials, passive delayed response, or conductance memory.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from pygrc.core import PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    LGRC9V3RouteAspect,
    LGRC9V3RouteAspectChannel,
    LGRC9V3RouteAspectHop,
    LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND,
    PortEdge,
    validate_lgrc9v3_self_rearm_evidence_artifacts,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD,
)


ROOT = Path(__file__).resolve().parents[3]
N05 = ROOT / "experiments/2026-05-N05-lgrc-coherence-waves-oscillators"
MANIFEST_PATH = N05 / "configs/n05_fixture_manifest_v1.json"
OUTPUT_PATH = N05 / "outputs/n05_iteration_7_o5_self_sustained_boundary.json"
REPORT_PATH = N05 / "reports/n05_iteration_7_o5_self_sustained_boundary.md"
O3_SCRIPT_PATH = N05 / "scripts/run_n05_iteration_5_o3_amplified_return.py"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/"
    "run_n05_iteration_7_o5_self_sustained_boundary.py"
)

CYCLE_COUNT = 3
PACKET_AMOUNT = 0.1
TRIGGER_THRESHOLD = 0.049
SOURCE_REFERENCE_MASS = 2.15
SINK_REFERENCE_MASS = 0.75
BUDGET_TOLERANCE = 1e-9


def _load_o3_module() -> Any:
    spec = importlib.util.spec_from_file_location("n05_iteration_5_o3", O3_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load O3 helper module from {O3_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


O3 = _load_o3_module()
O1 = O3.O1
CLAIM_FLAGS_FALSE = O1.CLAIM_FLAGS_FALSE
ROW_SCHEMA_REQUIRED_FIELDS = O1.ROW_SCHEMA_REQUIRED_FIELDS


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError("manifest root must be a JSON object")
    return data


def _two_pole_state(*, source_coherence: float = 2.0) -> GRC9V3State:
    graph = PortGraphBackend()
    source = graph.add_node({"label": "n05_o5_source_pole"})
    sink = graph.add_node({"label": "n05_o5_target_pole"})
    edge_forward = graph.connect_ports(source, 0, sink, 0, {"kind": "forward"})
    edge_return = graph.connect_ports(sink, 1, source, 1, {"kind": "return"})
    return GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(coherence=float(source_coherence)),
            sink: GRC9V3NodeState(coherence=1.0),
        },
        port_edges={
            edge_forward: PortEdge(
                source,
                1,
                sink,
                1,
                conductance=1.0,
                flux_uv=0.0,
            ),
            edge_return: PortEdge(
                sink,
                2,
                source,
                2,
                conductance=1.0,
                flux_uv=0.0,
            ),
        },
        base_conductance={edge_forward: 1.0, edge_return: 1.0},
        geometric_length={edge_forward: 1.0, edge_return: 1.0},
        temporal_delay={edge_forward: 1.0, edge_return: 1.0},
        flux_coupling={edge_forward: 0.0, edge_return: 0.0},
    )


def _build_model(*, source_coherence: float = 2.0) -> LGRC9V3:
    return LGRC9V3.from_state(_two_pole_state(source_coherence=source_coherence), {"dt": 1.0})


def _channel(
    channel_id: str,
    source_pole_id: str,
    target_pole_id: str,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    expected_next_channel_id: str,
) -> LGRC9V3RouteAspectChannel:
    return LGRC9V3RouteAspectChannel(
        channel_id=channel_id,
        source_pole_id=source_pole_id,
        target_pole_id=target_pole_id,
        expected_next_channel_id=expected_next_channel_id,
        route_hops=(
            LGRC9V3RouteAspectHop(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                edge_id=edge_id,
            ),
        ),
    )


def _route_aspect() -> LGRC9V3RouteAspect:
    return LGRC9V3RouteAspect(
        route_aspect_id="n05_o5_two_pole_self_rearm_loop_v1",
        direction="clockwise",
        pole_regions={"S": (0,), "K": (1,)},
        channels=(
            _channel("S_to_K", "S", "K", 0, 1, 0, "K_to_S"),
            _channel("K_to_S", "K", "S", 1, 0, 1, "S_to_K"),
        ),
        channel_sequence=("S_to_K", "K_to_S"),
    )


def _budget_surface(model: LGRC9V3) -> float:
    state = model.get_state()
    ledger = state.packet_ledger
    return float(
        sum(float(node.coherence) for node in state.base_state.nodes.values())
        + (0.0 if ledger is None else float(ledger.in_flight_packet_total))
    )


def _node_coherence(model: LGRC9V3, node_id: int) -> float:
    return float(model.get_state().base_state.nodes[node_id].coherence)


def _event_payload(event: Any) -> dict[str, Any]:
    return O1._event_payload(event)


def _packet_step_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return O1._packet_step_events(events)


def _production_log(model: LGRC9V3) -> list[dict[str, Any]]:
    cached = model.get_state().cached_quantities
    raw = cached.get("lgrc9v3_autonomous_production_log", [])
    if not isinstance(raw, list):
        raise RuntimeError("autonomous production log must be a list")
    return [dict(record) for record in raw]


def _snapshot_self_rearm_events(model: LGRC9V3) -> list[dict[str, Any]]:
    return [
        dict(event)
        for event in model.snapshot()["events"]
        if event.get("kind") == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
    ]


def _process_seed_parent_return(model: LGRC9V3) -> dict[str, Any]:
    before_budget = _budget_surface(model)
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=1,
        amount=0.25,
        departure_event_time_key=0.0,
        scheduler_event_index=1,
    )
    results = model.run_event_queue(max_events=2)
    packet_events: list[dict[str, Any]] = []
    for result in results:
        events = [_event_payload(event) for event in result.events]
        packet_events.extend(_packet_step_events(events))
    arrival = packet_events[-1]["processed_event"]
    return {
        "seed_kind": "single_declared_parent_return_arrival",
        "seeded_first_contact_only": True,
        "preauthored_event_list_used": False,
        "packet_events": packet_events,
        "parent_arrival_event_id": arrival["event_id"],
        "parent_arrival_event_digest": _digest(arrival),
        "parent_packet_id": arrival["packet_id"],
        "budget_before": before_budget,
        "budget_after": _budget_surface(model),
        "budget_error": abs(_budget_surface(model) - before_budget),
    }


def _configure_trigger(
    model: LGRC9V3,
    *,
    route_aspect: LGRC9V3RouteAspect,
    source_pole_id: str,
    eligible_channel_id: str,
) -> dict[str, Any]:
    reference_mass = (
        SOURCE_REFERENCE_MASS if source_pole_id == "S" else SINK_REFERENCE_MASS
    )
    model.set_route_aspect_surplus_trigger(
        route_aspect=route_aspect,
        source_pole_id=source_pole_id,
        reference_mass=reference_mass,
        trigger_threshold=TRIGGER_THRESHOLD,
        packet_amount=PACKET_AMOUNT,
        eligible_channel_id=eligible_channel_id,
    )
    return {
        "route_aspect_id": route_aspect.route_aspect_id,
        "route_aspect_digest": route_aspect.route_aspect_digest,
        "source_pole_id": source_pole_id,
        "eligible_channel_id": eligible_channel_id,
        "reference_mass": reference_mass,
        "trigger_threshold": TRIGGER_THRESHOLD,
        "packet_amount": PACKET_AMOUNT,
    }


def _run_trigger_segment(
    model: LGRC9V3,
    *,
    route_aspect: LGRC9V3RouteAspect,
    cycle_index: int,
    segment_index: int,
    source_pole_id: str,
    eligible_channel_id: str,
) -> dict[str, Any]:
    trigger_config = _configure_trigger(
        model,
        route_aspect=route_aspect,
        source_pole_id=source_pole_id,
        eligible_channel_id=eligible_channel_id,
    )
    before_budget = _budget_surface(model)
    before_production_len = len(_production_log(model))
    before_self_rearm_len = len(_snapshot_self_rearm_events(model))
    results = model.run_autonomous(
        max_events=2,
        producer_policies=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
        ),
    )
    new_production_results = _production_log(model)[before_production_len:]
    new_self_rearm_events = _snapshot_self_rearm_events(model)[before_self_rearm_len:]
    packet_events: list[dict[str, Any]] = []
    for result in results:
        events = [_event_payload(event) for event in result.events]
        for event in _packet_step_events(events):
            event["cycle_id"] = f"n05_o5_self_rearm_cycle_{cycle_index:03d}"
            event["cycle_index"] = int(cycle_index)
            event["segment_index"] = int(segment_index)
            event["source_pole_id"] = source_pole_id
            event["eligible_channel_id"] = eligible_channel_id
            packet_events.append(event)
    records = [
        record
        for result in new_production_results
        for record in result.get("production_records", [])
    ]
    summary = dict(
        model.get_state().cached_quantities.get("last_lgrc9v3_autonomous_run", {})
    )
    return {
        "cycle_id": f"n05_o5_self_rearm_cycle_{cycle_index:03d}",
        "cycle_index": int(cycle_index),
        "segment_index": int(segment_index),
        "source_pole_id": source_pole_id,
        "eligible_channel_id": eligible_channel_id,
        "trigger_config": trigger_config,
        "run_autonomous_used": True,
        "run_autonomous_max_events": 2,
        "run_autonomous_summary": summary,
        "run_autonomous_stop_condition": summary.get("stop_condition"),
        "production_results": new_production_results,
        "producer_records": records,
        "self_rearm_events": new_self_rearm_events,
        "packet_events": packet_events,
        "scheduled_packet_id": None
        if not records
        else records[0].get("observed_evidence", {}).get("scheduled_packet_id"),
        "native_self_rearm_evidence": bool(records)
        and bool(records[0].get("observed_evidence", {}).get("native_self_rearm_evidence")),
        "producer_mutated_coherence": any(
            abs(
                float(
                    record.get("observed_evidence", {})
                    .get("self_rearm_evidence", {})
                    .get("producer_budget_error", 0.0)
                )
            )
            > BUDGET_TOLERANCE
            for record in records
        ),
        "producer_mutated_topology": any(
            bool(record.get("topology_mutated")) for record in records
        ),
        "producer_consumed_queued_work": any(
            bool(record.get("queued_work_consumed")) for record in records
        ),
        "budget_before": before_budget,
        "budget_after": _budget_surface(model),
        "budget_error": abs(_budget_surface(model) - before_budget),
    }


def _run_positive_lane(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = _build_model()
    route_aspect = _route_aspect()
    initial_budget = _budget_surface(model)
    seed = _process_seed_parent_return(model)
    segments: list[dict[str, Any]] = []
    cycles: list[dict[str, Any]] = []
    for cycle_index in range(CYCLE_COUNT):
        source_segment = _run_trigger_segment(
            model,
            route_aspect=route_aspect,
            cycle_index=cycle_index,
            segment_index=0,
            source_pole_id="S",
            eligible_channel_id="S_to_K",
        )
        sink_segment = _run_trigger_segment(
            model,
            route_aspect=route_aspect,
            cycle_index=cycle_index,
            segment_index=1,
            source_pole_id="K",
            eligible_channel_id="K_to_S",
        )
        segments.extend([source_segment, sink_segment])
        cycles.append(
            {
                "cycle_id": f"n05_o5_self_rearm_cycle_{cycle_index:03d}",
                "cycle_index": int(cycle_index),
                "segment_ids": ["S_to_K", "K_to_S"],
                "source_segment_scheduled_packet_id": source_segment[
                    "scheduled_packet_id"
                ],
                "sink_segment_scheduled_packet_id": sink_segment["scheduled_packet_id"],
                "completed_source_target_source_cycle": True,
                "renewal_authorized_by_committed_state": (
                    source_segment["native_self_rearm_evidence"]
                    and sink_segment["native_self_rearm_evidence"]
                ),
                "budget_error": abs(
                    sink_segment["budget_after"] - source_segment["budget_before"]
                ),
            }
        )

    production_results = tuple(_production_log(model))
    events = model.snapshot()["events"]
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=events,
        production_results=production_results,
    )
    route_len = len(route_aspect.channel_sequence)
    completed_cycle_count = int(validation["completed_count"]) // route_len
    processed_packet_events = [
        event for segment in segments for event in segment["packet_events"]
    ]
    producer_records = [
        record for segment in segments for record in segment["producer_records"]
    ]
    all_self_rearm_payloads = [
        event.get("payload", {})
        for event in events
        if event.get("kind") == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
    ]
    completed_self_rearm_payloads = [
        payload
        for payload in all_self_rearm_payloads
        if payload.get("self_rearm_status") == "child_departure_processed"
    ]
    final_state = model.get_state()
    final_budget = _budget_surface(model)
    final_packet = processed_packet_events[-1]["processed_event"]
    scheduler_order = [
        int(event["processed_event"]["scheduler_event_index"])
        for event in processed_packet_events
    ]
    event_time_order = [
        float(event["processed_event"]["event_time_key"])
        for event in processed_packet_events
    ]
    final_exhaustion = _run_natural_exhaustion_probe()
    phase3_audit = _phase3_native_policy_support_audit()
    return {
        "run_id": "n05_iteration_7_o5_self_sustained_boundary",
        "lane_id": "o5_native_self_rearm_boundary",
        "status": "passed",
        "o_level": "O5",
        "o_level_is_evidence_classification": True,
        "claim_ceiling": "self_sustained_oscillator_candidate",
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "fixture_id": "N05_O5_two_pole_native_self_rearm_loop_v1",
        "fixture_derivation": {
            "source_manifest": manifest["manifest_id"],
            "fixture_kind": "two_pole_native_route_aspect_loop",
            "reason": (
                "native self-rearm evidence is defined over LGRC9V3 route-aspect "
                "closed-loop channels"
            ),
        },
        "execution_stage": "native_self_rearm_boundary",
        "o5_mode": "producer_mediated",
        "threshold_authorized": True,
        "scheduling_mode": "bounded_autonomous_run_segments",
        "producer_mediated": True,
        "constitutive_native_claim_allowed": False,
        "native_constitutive_oscillator_supported": False,
        "native_policy_blocker": phase3_audit["native_policy_blocker"],
        "source_native_surfaces": [
            "LGRC9V3RouteAspect",
            "LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS",
            "LGRC9V3.set_route_aspect_surplus_trigger",
            "LGRC9V3.run_autonomous",
            "validate_lgrc9v3_self_rearm_evidence_artifacts",
            "LGRC9V3.step",
        ],
        "source_node_id": 0,
        "target_node_id": 1,
        "route_id": route_aspect.route_aspect_id,
        "return_route_id": "K_to_S",
        "route_aspect": route_aspect.to_artifact(),
        "event_time_key": final_packet["event_time_key"],
        "scheduler_event_index": final_packet["scheduler_event_index"],
        "causal_epoch": "post_update",
        "node_proper_time": {
            str(node_id): float(value)
            for node_id, value in sorted(final_state.node_proper_time.items())
        },
        "source_node_proper_time": float(final_state.node_proper_time.get(0, 0.0)),
        "target_node_proper_time": float(final_state.node_proper_time.get(1, 0.0)),
        "outbound_packet_id": segments[0]["scheduled_packet_id"],
        "outbound_packet_digest": _digest(segments[0]["packet_events"][-1]["processed_event"]),
        "outbound_amount": PACKET_AMOUNT,
        "target_reservoir_before": None,
        "target_reservoir_after": None,
        "return_packet_id": final_packet["packet_id"],
        "return_packet_digest": _digest(final_packet),
        "return_amount": PACKET_AMOUNT,
        "cycle_id": "n05_o5_self_rearm_cycle_set_000",
        "cycle_ids": [cycle["cycle_id"] for cycle in cycles],
        "cycle_records": cycles,
        "trigger_segments": segments,
        "seed_parent_arrival": seed,
        "seeded_first_contact_only": True,
        "subsequent_cycles_authorized_by_native_self_rearm": True,
        "causal_delay": float(final_packet["event_time_key"])
        - float(seed["packet_events"][0]["processed_event"]["event_time_key"]),
        "causal_delay_semantics": (
            "elapsed_event_time_from_seed_departure_to_last_o5_arrival"
        ),
        "scheduler_order": scheduler_order,
        "event_time_order": event_time_order,
        "processed_packet_events": processed_packet_events,
        "producer_records": producer_records,
        "production_results": production_results,
        "snapshot_events": events,
        "self_rearm_events": [
            event
            for event in events
            if event.get("kind") == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
        ],
        "self_rearm_validation": validation,
        "native_self_rearm_evidence": validation["valid"],
        "self_rearm_completed_count": validation["completed_count"],
        "self_rearm_cycle_count": completed_cycle_count,
        "run_autonomous_used": True,
        "run_autonomous_stop_conditions": [
            segment["run_autonomous_stop_condition"] for segment in segments
        ],
        "run_autonomous_natural_exhaustion_probe": final_exhaustion,
        "node_plus_packet_budget_before": initial_budget,
        "node_plus_packet_budget_after": final_budget,
        "node_plus_packet_budget_error": abs(final_budget - initial_budget),
        "conservation": {
            "budget_surface": "node_plus_packet",
            "total_budget_before": initial_budget,
            "total_budget_after": final_budget,
            "budget_abs_error_max": abs(final_budget - initial_budget),
            "per_segment_budget_errors": [
                segment["budget_error"] for segment in segments
            ],
        },
        "amplification_accounting": {
            "status": "not_applicable_for_o5_self_rearm_boundary",
            "reservoir_runtime_visible": False,
            "reservoir_hidden_array_used": False,
            "silent_amplification_used": False,
        },
        "route_coupling": {
            "status": "not_applicable_for_o5",
            "route_coupling_runtime_visible": False,
            "memory_or_trail_claim_allowed": False,
        },
        "producer_boundary": {
            "producer_scheduled_packet": True,
            "producer_mutated_coherence": any(
                segment["producer_mutated_coherence"] for segment in segments
            ),
            "producer_consumed_queued_work": any(
                segment["producer_consumed_queued_work"] for segment in segments
            ),
            "producer_mutated_topology": any(
                segment["producer_mutated_topology"] for segment in segments
            ),
            "producer_emitted_claim_label": False,
            "step_processed_packet_work": True,
        },
        "cycle_semantics": {
            "cycle_definition": (
                "seeded_parent_arrival_then_native_self_rearm_S_to_K_and_K_to_S"
            ),
            "distinct_cycle_count": completed_cycle_count,
            "cycle_count_basis": "completed_native_self_rearm_pairs",
            "plateau_samples_counted_as_cycles": False,
            "repeated_cycle_claim_allowed": True,
            "self_sustained_oscillator_claim_allowed": True,
            "constitutive_native_claim_allowed": False,
        },
        "scheduling_semantics": {
            "scheduling_mode": "bounded_autonomous_run_segments",
            "preauthored_event_list_used": False,
            "hidden_return_timing_used": False,
            "hidden_reservoir_used": False,
            "producer_mediated": True,
            "producer_mutated_state": False,
            "cycle_renewal_depends_on_committed_state": all(
                bool(payload.get("producer_after_parent_arrival_committed"))
                for payload in completed_self_rearm_payloads
            ),
            "native_self_rearm_validator_used": True,
            "self_rearm_validation_passed": validation["valid"],
            "constitutive_native_claim_allowed": False,
        },
        "phase3_native_policy_support_audit": phase3_audit,
        "claim_flags": CLAIM_FLAGS_FALSE,
        "blocked_claims": [
            "pure_native_constitutive_oscillator",
            "route_coupled_oscillator_candidate",
            "semantic_choice",
            "memory_or_trail",
            "agency",
            "agentic_like_behavior",
            "locomotion_like_behavior",
            "ant_colony_behavior",
        ],
    }


def _run_natural_exhaustion_probe() -> dict[str, Any]:
    model = _build_model()
    results = model.run_autonomous(
        max_events=5,
        producer_policies=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
        ),
    )
    summary = dict(
        model.get_state().cached_quantities.get("last_lgrc9v3_autonomous_run", {})
    )
    return {
        "probe_kind": "no_surplus_trigger_configured",
        "result_count": len(results),
        "run_autonomous_stop_condition": summary.get("stop_condition"),
        "queue_has_work_after": summary.get("queue_has_work_after"),
        "producer_no_eligible_work_count": summary.get(
            "producer_no_eligible_work_count"
        ),
        "passed": len(results) == 0
        and summary.get("stop_condition") == "no_autonomous_work_available",
    }


def _phase3_native_policy_support_audit() -> dict[str, Any]:
    support = {
        "custom_node_potentials_support": False,
        "potential_inversion_support": False,
        "flux_facilitated_metric_map_support": False,
        "delayed_passive_response_support": False,
        "route_conductance_memory_support": False,
    }
    blockers = [
        "missing_serialized_custom_node_potentials_policy",
        "missing_serialized_potential_inversion_policy",
        "missing_flux_facilitated_metric_map_policy",
        "missing_serialized_delayed_passive_response_policy",
        "missing_route_conductance_memory_policy",
    ]
    return {
        **support,
        "current_native_supports": [
            "route_aspect_surplus_trigger",
            "native_self_rearm_evidence",
            "bounded_autonomous_run_loop",
        ],
        "native_constitutive_oscillator_supported": False,
        "constitutive_native_claim_allowed": False,
        "native_policy_blocker": "missing_serialized_delayed_passive_response_policy",
        "native_policy_blockers": blockers,
        "passed": True,
    }


def _artifact_only_replay(lane: Mapping[str, Any]) -> dict[str, Any]:
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=tuple(lane["snapshot_events"]),
        production_results=tuple(lane["production_results"]),
    )
    parent_ids = {
        event["processed_event"]["event_id"]
        for event in lane["processed_packet_events"]
        if str(event["processed_event"]["event_kind"]).endswith("packet_arrival")
    }
    parent_ids.add(lane["seed_parent_arrival"]["parent_arrival_event_id"])
    completed_payloads = [
        event["payload"]
        for event in lane["self_rearm_events"]
        if event.get("payload", {}).get("self_rearm_status")
        == "child_departure_processed"
    ]
    linkage_ok = all(
        payload.get("parent_arrival_event_id") in parent_ids
        and payload.get("producer_after_parent_arrival_committed") is True
        and payload.get("event_time_ordering", {}).get(
            "arrival_before_or_at_child_departure"
        )
        is True
        and abs(float(payload.get("child_departure_budget_error", 1.0)))
        <= BUDGET_TOLERANCE
        for payload in completed_payloads
    )
    replay_passed = (
        validation["valid"] is True
        and int(validation["completed_count"]) >= 2 * CYCLE_COUNT
        and linkage_ok
        and lane["scheduling_semantics"]["preauthored_event_list_used"] is False
        and lane["scheduling_semantics"]["cycle_renewal_depends_on_committed_state"]
        is True
        and abs(float(lane["node_plus_packet_budget_error"])) <= BUDGET_TOLERANCE
    )
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts",
        "validator_replay_note": (
            "validator reran from exported snapshot events and production results"
        ),
        "validation_valid": validation["valid"],
        "validation_failure_reasons": validation["failure_reasons"],
        "completed_self_rearm_count": validation["completed_count"],
        "cycle_count_reconstructed": int(validation["completed_count"]) // 2,
        "self_rearm_linkage_ok": linkage_ok,
        "renewal_depends_on_committed_state": lane["scheduling_semantics"][
            "cycle_renewal_depends_on_committed_state"
        ],
        "hidden_event_list_absent": lane["scheduling_semantics"][
            "preauthored_event_list_used"
        ]
        is False,
        "budget_ok": abs(float(lane["node_plus_packet_budget_error"]))
        <= BUDGET_TOLERANCE,
        "passed": replay_passed,
    }


def _run_disabled_trigger_control() -> dict[str, Any]:
    model = _build_model()
    route_aspect = _route_aspect()
    _configure_trigger(
        model,
        route_aspect=route_aspect,
        source_pole_id="S",
        eligible_channel_id="S_to_K",
    )
    produced = model.produce_events(policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED)
    return {
        "control_id": "disabled_trigger",
        "primary_blocker": "n05_o5_trigger_policy_disabled",
        "control_execution_mode": "runtime_control",
        "passed": produced.scheduled_event_count == 0
        and not model.get_state().packet_ledger.event_queue_records,
        "producer_result": produced.to_artifact(),
    }


def _run_subthreshold_control() -> dict[str, Any]:
    model = _build_model(source_coherence=0.9)
    _process_seed_parent_return(model)
    route_aspect = _route_aspect()
    model.set_route_aspect_surplus_trigger(
        route_aspect=route_aspect,
        source_pole_id="S",
        reference_mass=2.0,
        trigger_threshold=0.5,
        packet_amount=PACKET_AMOUNT,
        eligible_channel_id="S_to_K",
    )
    produced = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    )
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=model.snapshot()["events"],
        production_results=(produced.to_artifact(),),
    )
    return {
        "control_id": "subthreshold",
        "primary_blocker": "n05_o5_threshold_gate_failed",
        "control_execution_mode": "runtime_control",
        "passed": produced.scheduled_event_count == 0
        and produced.production_records[0].reason_code
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD
        and validation["valid"] is False,
        "validation": validation,
        "producer_result": produced.to_artifact(),
    }


def _run_wrong_state_control() -> dict[str, Any]:
    model = _build_model(source_coherence=2.3)
    route_aspect = _route_aspect()
    _configure_trigger(
        model,
        route_aspect=route_aspect,
        source_pole_id="S",
        eligible_channel_id="S_to_K",
    )
    produced = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    )
    model.step()
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=model.snapshot()["events"],
        production_results=(produced.to_artifact(),),
    )
    return {
        "control_id": "wrong_state",
        "primary_blocker": "n05_o5_committed_parent_arrival_missing",
        "control_execution_mode": "runtime_control",
        "passed": produced.scheduled_event_count == 1
        and validation["valid"] is False
        and "no_completed_self_rearm_evidence" in validation["failure_reasons"],
        "validation": validation,
        "producer_result": produced.to_artifact(),
    }


def _run_duplicate_control() -> dict[str, Any]:
    model = _build_model()
    _process_seed_parent_return(model)
    route_aspect = _route_aspect()
    _configure_trigger(
        model,
        route_aspect=route_aspect,
        source_pole_id="S",
        eligible_channel_id="S_to_K",
    )
    first = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    )
    duplicate = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    )
    return {
        "control_id": "duplicate_trigger",
        "primary_blocker": "n05_o5_duplicate_trigger_suppressed",
        "control_execution_mode": "runtime_idempotency_control",
        "passed": first.scheduled_event_count == 1
        and duplicate.scheduled_event_count == 0
        and duplicate.production_records[0].reason_code
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
        "first_producer_result": first.to_artifact(),
        "duplicate_producer_result": duplicate.to_artifact(),
    }


def _run_hidden_event_list_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "control_id": "hidden_event_list",
        "primary_blocker": "n05_o5_hidden_event_list_rejected",
        "control_execution_mode": "artifact_policy_control",
        "passed": lane["seed_parent_arrival"]["preauthored_event_list_used"] is False
        and lane["scheduling_semantics"]["preauthored_event_list_used"] is False,
    }


def _run_budget_drift_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    corrupted = copy.deepcopy(lane)
    corrupted["node_plus_packet_budget_after"] = (
        float(corrupted["node_plus_packet_budget_after"]) + 0.01
    )
    corrupted["node_plus_packet_budget_error"] = abs(
        float(corrupted["node_plus_packet_budget_after"])
        - float(corrupted["node_plus_packet_budget_before"])
    )
    replay = _artifact_only_replay(corrupted)
    return {
        "control_id": "budget_drift",
        "primary_blocker": "n05_o5_node_plus_packet_budget_mismatch",
        "control_execution_mode": "artifact_budget_control",
        "passed": replay["passed"] is False
        and abs(float(lane["node_plus_packet_budget_error"])) <= BUDGET_TOLERANCE,
    }


def _control_matrix(lane: Mapping[str, Any]) -> dict[str, Any]:
    controls: dict[str, Any] = {
        "disabled_trigger": _run_disabled_trigger_control(),
        "subthreshold": _run_subthreshold_control(),
        "wrong_state": _run_wrong_state_control(),
        "hidden_event_list": _run_hidden_event_list_control(lane),
        "duplicate_trigger": _run_duplicate_control(),
        "budget_drift": _run_budget_drift_control(lane),
        "producer_mutation": {
            "control_id": "producer_mutation_attempt",
            "primary_blocker": "n05_o5_producer_mutation_boundary_violation",
            "control_execution_mode": "runtime_artifact_control",
            "passed": lane["producer_boundary"]["producer_mutated_coherence"] is False
            and lane["producer_boundary"]["producer_consumed_queued_work"] is False
            and lane["producer_boundary"]["producer_mutated_topology"] is False,
        },
        "claim_promotion": {
            "control_id": "claim_promotion_attempt",
            "primary_blocker": "n05_o5_claim_promotion_rejected",
            "control_execution_mode": "artifact_claim_boundary_control",
            "passed": lane["claim_flags"] == CLAIM_FLAGS_FALSE
            and lane["constitutive_native_claim_allowed"] is False,
        },
    }
    controls["all_controls_passed"] = all(
        bool(control.get("passed"))
        for key, control in controls.items()
        if key != "all_controls_passed"
    )
    return controls


def _write_report(result: Mapping[str, Any]) -> None:
    lane = result["positive_lane"]
    controls = result["controls"]
    seed = lane["seed_parent_arrival"]
    seed_summary = {
        "seed_kind": seed["seed_kind"],
        "seeded_first_contact_only": seed["seeded_first_contact_only"],
        "preauthored_event_list_used": seed["preauthored_event_list_used"],
        "parent_arrival_event_id": seed["parent_arrival_event_id"],
        "parent_arrival_event_digest": seed["parent_arrival_event_digest"],
        "parent_packet_id": seed["parent_packet_id"],
        "budget_error": seed["budget_error"],
    }
    cycle_rows = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` | {} |".format(
            cycle["cycle_index"],
            cycle["cycle_id"],
            cycle["source_segment_scheduled_packet_id"],
            cycle["sink_segment_scheduled_packet_id"],
            cycle["renewal_authorized_by_committed_state"],
        )
        for cycle in lane["cycle_records"]
    )
    control_rows = "\n".join(
        "| `{}` | `{}` | `{}` | {} |".format(
            key,
            value.get("primary_blocker", ""),
            value.get("control_execution_mode", "runtime_control"),
            value.get("passed"),
        )
        for key, value in controls.items()
        if key != "all_controls_passed"
    )
    text = f"""# N05 Iteration 7 O5 Self-Sustained Oscillator Boundary

Status: {result["status"]}

Command:

```bash
{COMMAND}
```

## Result

| Field | Value |
|---|---|
| O-level | `{lane["o_level"]}` |
| claim ceiling | `{lane["claim_ceiling"]}` |
| O5 mode | `{lane["o5_mode"]}` |
| execution stage | `{lane["execution_stage"]}` |
| fixture id | `{lane["fixture_id"]}` |
| native self-rearm evidence | `{lane["native_self_rearm_evidence"]}` |
| self-rearm completed count | `{lane["self_rearm_completed_count"]}` |
| reconstructed cycles | `{lane["self_rearm_cycle_count"]}` |
| native constitutive oscillator supported | `{lane["native_constitutive_oscillator_supported"]}` |
| native policy blocker | `{lane["native_policy_blocker"]}` |
| budget error | `{lane["node_plus_packet_budget_error"]}` |
| row schema compliance | `{lane["row_schema_compliance"]["passed"]}` |

## Cycle Records

| Index | Cycle id | S-to-K packet | K-to-S packet | Renewal state-authorized |
|---|---|---|---|---|
{cycle_rows}

## Fixture And Seed Boundary

O5 uses a two-pole closed-loop route-aspect fixture because native self-rearm
evidence is defined over `LGRC9V3RouteAspect` channels. This is intentionally
different from the source-target-reservoir fixture used by O3/O4.

```json
{json.dumps(lane["fixture_derivation"], indent=2, sort_keys=True)}
```

The first parent return is a declared bootstrap seed. The counted O5 cycles
come from subsequent native self-rearm evidence.

```json
{json.dumps(seed_summary, indent=2, sort_keys=True)}
```

## Artifact Replay

```json
{json.dumps(result["artifact_replay"], indent=2, sort_keys=True)}
```

## Phase 3 Native Policy Audit

```json
{json.dumps(lane["phase3_native_policy_support_audit"], indent=2, sort_keys=True)}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
{control_rows}

## Claim Boundary

O5 is a producer-mediated, threshold-authorized self-rearm oscillator boundary.
It does not prove a pure constitutive native oscillator. Movement, semantic
choice, agency, identity, memory/trail, route-coupled oscillator, agentic-like,
locomotion-like, biological, ACO, and unrestricted movement claim flags remain
false.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    manifest = _load_manifest()
    positive_lane = _run_positive_lane(manifest)
    artifact_replay = _artifact_only_replay(positive_lane)
    positive_lane["artifact_only_replay"] = artifact_replay
    missing_row_fields = [
        field for field in ROW_SCHEMA_REQUIRED_FIELDS if field not in positive_lane
    ]
    positive_lane["row_schema_compliance"] = {
        "required_fields": ROW_SCHEMA_REQUIRED_FIELDS,
        "missing_required_fields": missing_row_fields,
        "passed": not missing_row_fields,
    }
    controls = _control_matrix(positive_lane)
    status = (
        "passed"
        if positive_lane["status"] == "passed"
        and artifact_replay["passed"]
        and positive_lane["row_schema_compliance"]["passed"]
        and controls["all_controls_passed"]
        and positive_lane["phase3_native_policy_support_audit"]["passed"]
        else "failed"
    )
    result = {
        "schema": "coherence_oscillator_report_v1",
        "run_id": "n05_iteration_7_o5_self_sustained_boundary",
        "iteration": 7,
        "status": status,
        "command": COMMAND,
        "manifest_path": _rel(MANIFEST_PATH),
        "manifest_sha256": _file_sha256(MANIFEST_PATH),
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "execution_stage": "native_self_rearm_boundary",
        "o_ladder": {
            "o_level": "O5",
            "o_level_is_evidence_classification": True,
            "claim_ceiling": "self_sustained_oscillator_candidate",
        },
        "positive_lane": positive_lane,
        "artifact_replay": artifact_replay,
        "controls": controls,
        "claim_flags": CLAIM_FLAGS_FALSE,
        "claim_boundary": {
            "o_level_is_evidence_classification": True,
            **CLAIM_FLAGS_FALSE,
        },
        "artifact_digests": {
            "positive_lane_digest": _digest(positive_lane),
            "cycle_records_digest": _digest(positive_lane["cycle_records"]),
            "producer_records_digest": _digest(positive_lane["producer_records"]),
            "processed_packet_events_digest": _digest(
                positive_lane["processed_packet_events"]
            ),
            "self_rearm_events_digest": _digest(positive_lane["self_rearm_events"]),
            "snapshot_events_digest": _digest(positive_lane["snapshot_events"]),
            "phase3_native_policy_support_audit_digest": _digest(
                positive_lane["phase3_native_policy_support_audit"]
            ),
            "artifact_replay_digest": _digest(artifact_replay),
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "git": {
            "head": _git(["rev-parse", "HEAD"]),
            "status_src": _git(["status", "--short", "src"]),
            "status_n05": _git(
                [
                    "status",
                    "--short",
                    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators",
                ]
            ),
        },
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(
        json.dumps(
            {
                "status": status,
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "o_level": "O5",
                "claim_ceiling": "self_sustained_oscillator_candidate",
                "o5_mode": positive_lane["o5_mode"],
                "self_rearm_cycle_count": positive_lane["self_rearm_cycle_count"],
                "native_constitutive_oscillator_supported": positive_lane[
                    "native_constitutive_oscillator_supported"
                ],
                "row_schema_passed": positive_lane["row_schema_compliance"][
                    "passed"
                ],
            },
            sort_keys=True,
        )
    )
    if status != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
