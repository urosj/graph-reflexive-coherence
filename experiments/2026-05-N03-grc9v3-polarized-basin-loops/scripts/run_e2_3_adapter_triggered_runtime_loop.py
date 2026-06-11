#!/usr/bin/env python3
"""Run E2.3 adapter-triggered packet loop through native LGRC9V3.

E2.3 keeps packet processing inside the existing LGRC9V3 runtime while an
experiment-local adapter observes runtime state and schedules the next packet
when a measured pole surplus crosses the serialized trigger threshold.

The trigger and self-rearm labels are adapter-derived.  This is not native
LGRC9V3 autonomy and does not modify `src/*`.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from pygrc.models import (
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LAPSE_POLICY_UNIT,
    LGRC9V3,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
)

import run_d2_conserved_causal_packet_loop as d2
import run_e2_0_runtime_feasibility as e2_0
from loop_observables import write_json


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_3_adapter_triggered_runtime_loop.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e2_3_adapter_triggered_runtime_loop.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_e2_3_adapter_triggered_runtime_loop.py"
)

BUDGET_TOLERANCE = 1e-9
N_CYCLES_MIN = 3
PACKET_AMOUNT = 0.006
TRIGGER_THRESHOLD = 0.003
HOP_DELAY = 1.0
MAX_RUNTIME_EVENTS = 160
RESERVE_NODES = (2, 5, 8, 11)


@dataclass(frozen=True)
class RuntimePacketMeta:
    channel_id: str
    hop_index: int
    route_step_index: int
    parent_packet_id: str | None
    schedule_reason: str


def _reference_pole_mass() -> float:
    return len(d2.POLES["S1"]) / e2_0.NODE_COUNT


def _pole_mass(model: LGRC9V3, pole_id: str) -> float:
    state = model.get_state().base_state
    return sum(float(state.nodes[node_id].coherence) for node_id in d2.POLES[pole_id])


def _apply_initial_surplus(state: Any, *, pole_id: str, surplus: float) -> None:
    if surplus <= 0.0:
        return
    for node_id in d2.POLES[pole_id]:
        state.nodes[node_id].coherence += surplus / len(d2.POLES[pole_id])
    for node_id in RESERVE_NODES:
        state.nodes[node_id].coherence -= surplus / len(RESERVE_NODES)


def _cw_route_hops() -> dict[str, list[dict[str, int]]]:
    route_manifest = e2_0._build_route_manifest()
    return {
        channel_id: [
            {
                "source_node_id": int(hop["source_node_id"]),
                "target_node_id": int(hop["target_node_id"]),
                "edge_id": int(hop["edge_id"]),
            }
            for hop in route_manifest["channels"][channel_id]["route_hops"]
        ]
        for channel_id in route_manifest["declared_routes"]["d2_3_cw_closed_loop"]
    }


def _ccw_route_hops() -> dict[str, list[dict[str, int]]]:
    return {
        "S1_to_K1_rev": [
            {"source_node_id": 0, "target_node_id": 11, "edge_id": 11},
            {"source_node_id": 11, "target_node_id": 10, "edge_id": 10},
        ],
        "K1_to_S2_rev": [
            {"source_node_id": 9, "target_node_id": 8, "edge_id": 8},
            {"source_node_id": 8, "target_node_id": 7, "edge_id": 7},
        ],
        "S2_to_K2_rev": [
            {"source_node_id": 6, "target_node_id": 5, "edge_id": 5},
            {"source_node_id": 5, "target_node_id": 4, "edge_id": 4},
        ],
        "K2_to_S1_rev": [
            {"source_node_id": 3, "target_node_id": 2, "edge_id": 2},
            {"source_node_id": 2, "target_node_id": 1, "edge_id": 1},
        ],
    }


def _routes_for_direction(direction: str) -> dict[str, list[dict[str, int]]]:
    if direction == "cw":
        return _cw_route_hops()
    if direction == "ccw":
        return _ccw_route_hops()
    raise ValueError(f"unsupported direction {direction!r}")


def _sequence(direction: str) -> tuple[str, ...]:
    return d2._sequence(direction)


def _candidate_sequence(config: Mapping[str, Any], sequence: Sequence[str]) -> tuple[str, ...]:
    mode = str(config["mode"])
    if mode == "forward_only":
        return tuple(sequence[:1])
    if mode == "broken_return":
        return tuple(sequence[:-1])
    if mode == "scrambled_order":
        return (sequence[0], sequence[2], sequence[1], sequence[3])
    return tuple(sequence)


def _build_model(config: Mapping[str, Any]) -> LGRC9V3:
    state = e2_0._build_ring_state()
    _apply_initial_surplus(
        state,
        pole_id=str(config.get("initial_surplus_pole", "S1")),
        surplus=float(config.get("initial_surplus", 0.0)),
    )
    return LGRC9V3.from_state(
        state,
        {
            "dt": 1.0,
            "causal_modes": {
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "event_time_policy": "explicit_event_time_key",
                "proper_time_accumulation_policy": "local_event_frontier",
                "causal_topology_integration_allowed": False,
                "causal_spark_expansion_allowed": False,
                "causal_boundary_birth_allowed": False,
            },
        },
    )


def _new_packet_id(model: LGRC9V3, before_packet_ids: set[str]) -> str:
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    after_packet_ids = {packet.packet_id for packet in ledger.packet_records}
    new_packet_ids = sorted(after_packet_ids - before_packet_ids)
    if len(new_packet_ids) != 1:
        raise RuntimeError(f"expected one new packet id, got {new_packet_ids!r}")
    return new_packet_ids[0]


def _schedule_hop(
    model: LGRC9V3,
    *,
    channel_id: str,
    hop_index: int,
    routes: Mapping[str, Sequence[Mapping[str, int]]],
    amount: float,
    parent_packet_id: str | None,
    schedule_reason: str,
    next_packet_index: int,
    metadata: dict[str, RuntimePacketMeta],
) -> tuple[int, str]:
    hop = routes[channel_id][hop_index]
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    before_packet_ids = {packet.packet_id for packet in ledger.packet_records}
    departure_time = float(state.event_time_key)
    model.schedule_packet_departure(
        source_node_id=int(hop["source_node_id"]),
        target_node_id=int(hop["target_node_id"]),
        edge_id=int(hop["edge_id"]),
        amount=amount,
        departure_event_time_key=departure_time,
        arrival_event_time_key=departure_time + HOP_DELAY,
        packet_index=next_packet_index,
    )
    packet_id = _new_packet_id(model, before_packet_ids)
    route_step_index = _candidate_route_step(channel_id, hop_index, routes=routes)
    metadata[packet_id] = RuntimePacketMeta(
        channel_id=channel_id,
        hop_index=hop_index,
        route_step_index=route_step_index,
        parent_packet_id=parent_packet_id,
        schedule_reason=schedule_reason,
    )
    return next_packet_index + 1, packet_id


def _candidate_route_step(
    channel_id: str,
    hop_index: int,
    *,
    routes: Mapping[str, Sequence[Mapping[str, int]]],
) -> int:
    ordered_channels = [channel for channel in (*d2.CW_SEQUENCE, *d2.CCW_SEQUENCE) if channel in routes]
    step = 0
    for current in ordered_channels:
        if current == channel_id:
            return step + hop_index
        step += len(routes[current])
    return hop_index


def _maybe_trigger_channel(
    model: LGRC9V3,
    *,
    config: Mapping[str, Any],
    behavior_sequence: Sequence[str],
    routes: Mapping[str, Sequence[Mapping[str, int]]],
    parent_channel_id: str | None,
    parent_packet_id: str | None,
    next_packet_index: int,
    metadata: dict[str, RuntimePacketMeta],
    adapter_events: list[dict[str, Any]],
) -> tuple[int, str | None]:
    if str(config["mode"]) == "no_trigger":
        return next_packet_index, None
    candidate_sequence = _candidate_sequence(config, behavior_sequence)
    allowed_channel_ids: tuple[str, ...] | None = None
    if parent_channel_id is not None and parent_channel_id in candidate_sequence:
        allowed_channel_ids = (
            candidate_sequence[(candidate_sequence.index(parent_channel_id) + 1) % len(candidate_sequence)],
        )
    for channel_id in allowed_channel_ids or candidate_sequence:
        source_pole = str(({**d2.CW_CHANNELS, **d2.CCW_CHANNELS})[channel_id]["source"])
        surplus = _pole_mass(model, source_pole) - _reference_pole_mass()
        if surplus < float(config["trigger_threshold"]):
            continue
        amount = min(float(config["packet_amount"]), surplus)
        next_packet_index, packet_id = _schedule_hop(
            model,
            channel_id=channel_id,
            hop_index=0,
            routes=routes,
            amount=amount,
            parent_packet_id=parent_packet_id,
            schedule_reason="state_trigger",
            next_packet_index=next_packet_index,
            metadata=metadata,
        )
        adapter_events.append(
            {
                "event_kind": "adapter_state_trigger",
                "event_time_key": model.get_state().event_time_key,
                "triggered_channel": channel_id,
                "packet_id": packet_id,
                "parent_packet_id": parent_packet_id,
                "source_pole": source_pole,
                "source_pole_surplus": surplus,
                "trigger_threshold": float(config["trigger_threshold"]),
                "packet_amount": amount,
                "native_event": False,
            }
        )
        return next_packet_index, packet_id
    return next_packet_index, None


def _packet_events_from_step(result: Any) -> list[Mapping[str, Any]]:
    events: list[Mapping[str, Any]] = []
    for event in result.events:
        if event.kind in (
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        ):
            events.append(event.payload)
    return events


def _cycle_count(events: Sequence[str], sequence: Sequence[str]) -> int:
    return d2._cycle_count(events, sequence)


def _run_lane(config: Mapping[str, Any]) -> dict[str, Any]:
    expected_sequence = _sequence(str(config["direction"]))
    behavior_direction = str(config.get("behavior_direction", config["direction"]))
    behavior_sequence = _sequence(behavior_direction)
    routes = _routes_for_direction(behavior_direction)
    model = _build_model(config)
    initial_signature = e2_0._topology_signature(model.get_state().base_state)
    initial_budget = e2_0._node_total(model.get_state().base_state)
    metadata: dict[str, RuntimePacketMeta] = {}
    adapter_events: list[dict[str, Any]] = []
    runtime_events: list[dict[str, Any]] = []
    completed_channels: list[str] = []
    rearm_events: list[dict[str, Any]] = []
    next_packet_index = 0
    next_packet_index, _ = _maybe_trigger_channel(
        model,
        config=config,
        behavior_sequence=behavior_sequence,
        routes=routes,
        parent_channel_id=None,
        parent_packet_id=None,
        next_packet_index=next_packet_index,
        metadata=metadata,
        adapter_events=adapter_events,
    )
    processed_event_count = 0
    while processed_event_count < MAX_RUNTIME_EVENTS:
        results = model.run_event_queue(max_events=1)
        if not results:
            break
        result = results[0]
        processed_event_count += 1
        for payload in _packet_events_from_step(result):
            processed = payload["processed_event"]
            packet_id = str(processed["packet_id"])
            meta = metadata.get(packet_id)
            runtime_events.append(
                {
                    "event_kind": processed["event_kind"],
                    "native_event_id": processed.get("event_id"),
                    "packet_id": packet_id,
                    "event_time_key": processed["event_time_key"],
                    "scheduler_event_index": processed["scheduler_event_index"],
                    "amount": processed["amount"],
                    "source_node_id": processed["source_node_id"],
                    "target_node_id": processed["target_node_id"],
                    "edge_id": processed["edge_id"],
                    "channel_id": None if meta is None else meta.channel_id,
                    "hop_index": None if meta is None else meta.hop_index,
                    "schedule_reason": None if meta is None else meta.schedule_reason,
                    "parent_packet_id": None if meta is None else meta.parent_packet_id,
                    "budget_error": payload.get("budget_error"),
                    "proper_time_update": payload.get("proper_time_update"),
                    "topology_mutated": payload.get("topology_mutated"),
                }
            )
            if processed["event_kind"] != LGRC9V3_PACKET_EVENT_KIND_ARRIVAL or meta is None:
                continue
            channel_hops = routes[meta.channel_id]
            if meta.hop_index < len(channel_hops) - 1:
                next_packet_index, _ = _schedule_hop(
                    model,
                    channel_id=meta.channel_id,
                    hop_index=meta.hop_index + 1,
                    routes=routes,
                    amount=float(processed["amount"]),
                    parent_packet_id=packet_id,
                    schedule_reason="route_continuation",
                    next_packet_index=next_packet_index,
                    metadata=metadata,
                )
                continue
            completed_channels.append(meta.channel_id)
            before_trigger_count = len(adapter_events)
            next_packet_index, child_packet_id = _maybe_trigger_channel(
                model,
                config=config,
                behavior_sequence=behavior_sequence,
                routes=routes,
                parent_channel_id=meta.channel_id,
                parent_packet_id=packet_id,
                next_packet_index=next_packet_index,
                metadata=metadata,
                adapter_events=adapter_events,
            )
            if (
                child_packet_id is not None
                and len(adapter_events) > before_trigger_count
                and meta.channel_id == expected_sequence[-1]
                and adapter_events[-1]["triggered_channel"] == expected_sequence[0]
            ):
                rearm_events.append(
                    {
                        "event_kind": "adapter_self_rearm",
                        "event_time_key": model.get_state().event_time_key,
                        "parent_packet_id": packet_id,
                        "child_packet_id": child_packet_id,
                        "parent_channel_id": meta.channel_id,
                        "child_channel_id": expected_sequence[0],
                        "native_event": False,
                    }
                )
    packet_ids_with_departure = {
        event["packet_id"]
        for event in runtime_events
        if event["event_kind"] == LGRC9V3_PACKET_EVENT_KIND_DEPARTURE
    }
    terminal_unprocessed_rearm_events = [
        event
        for event in rearm_events
        if str(event["child_packet_id"]) not in packet_ids_with_departure
    ]
    rearm_events = [
        event
        for event in rearm_events
        if str(event["child_packet_id"]) in packet_ids_with_departure
    ]
    final_state = model.get_state()
    final_signature = e2_0._topology_signature(final_state.base_state)
    ledger = final_state.packet_ledger
    assert ledger is not None
    node_total = e2_0._node_total(final_state.base_state)
    budget = node_total + float(ledger.in_flight_packet_total)
    cycle_count = _cycle_count(completed_channels, expected_sequence)
    opposite_cycle_count = _cycle_count(
        completed_channels,
        _sequence("ccw" if str(config["direction"]) == "cw" else "cw"),
    )
    max_event_budget_error = max(
        (abs(float(event["budget_error"])) for event in runtime_events if event["budget_error"] is not None),
        default=0.0,
    )
    duplicate_packet_count = len(metadata) - len(set(metadata))
    packet_ids_with_arrival = {
        event["packet_id"]
        for event in runtime_events
        if event["event_kind"] == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL
    }
    controls_passed = (
        abs(budget - initial_budget) <= BUDGET_TOLERANCE
        and max_event_budget_error <= BUDGET_TOLERANCE
        and initial_signature == final_signature
        and duplicate_packet_count == 0
        and packet_ids_with_departure == packet_ids_with_arrival
    )
    positive = (
        controls_passed
        and cycle_count >= N_CYCLES_MIN
        and len(rearm_events) >= max(1, N_CYCLES_MIN - 1)
    )
    return {
        "lane_id": str(config["lane_id"]),
        "direction": str(config["direction"]),
        "behavior_direction": behavior_direction,
        "mode": str(config["mode"]),
        "expected_positive": bool(config["expected_positive"]),
        "prototype_positive": positive,
        "expectation_passed": positive is bool(config["expected_positive"]),
        "trigger_count": len(adapter_events),
        "route_continuation_count": sum(
            1 for meta in metadata.values() if meta.schedule_reason == "route_continuation"
        ),
        "rearm_count": len(rearm_events),
        "cycle_count": cycle_count,
        "opposite_cycle_count": opposite_cycle_count,
        "completed_channels": completed_channels,
        "runtime_event_count": len(runtime_events),
        "departure_count": len(packet_ids_with_departure),
        "arrival_count": len(packet_ids_with_arrival),
        "packet_pairing_passed": packet_ids_with_departure == packet_ids_with_arrival,
        "node_plus_packet_budget": budget,
        "budget_error": abs(budget - initial_budget),
        "max_event_budget_error": max_event_budget_error,
        "topology_unchanged": initial_signature == final_signature,
        "queue_empty": len(ledger.event_queue_records) == 0,
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "adapter_events": adapter_events,
        "rearm_events": rearm_events,
        "terminal_unprocessed_rearm_events": terminal_unprocessed_rearm_events,
        "runtime_events": runtime_events,
    }


def _scenario_config() -> list[dict[str, Any]]:
    base = {
        "packet_amount": PACKET_AMOUNT,
        "trigger_threshold": TRIGGER_THRESHOLD,
        "initial_surplus": PACKET_AMOUNT,
    }
    return [
        {
            **base,
            "lane_id": "E2.3-U0-no-surplus",
            "direction": "cw",
            "mode": "closed_loop",
            "initial_surplus": 0.0,
            "expected_positive": False,
        },
        {
            **base,
            "lane_id": "E2.3-P-adapter-triggered-cw",
            "direction": "cw",
            "mode": "closed_loop",
            "expected_positive": True,
        },
        {
            **base,
            "lane_id": "E2.3-R-adapter-triggered-ccw",
            "direction": "ccw",
            "mode": "closed_loop",
            "expected_positive": True,
        },
        {
            **base,
            "lane_id": "E2.3-C-subthreshold",
            "direction": "cw",
            "mode": "closed_loop",
            "initial_surplus": TRIGGER_THRESHOLD * 0.5,
            "expected_positive": False,
        },
        {
            **base,
            "lane_id": "E2.3-C-wrong-direction",
            "direction": "cw",
            "behavior_direction": "ccw",
            "mode": "closed_loop",
            "expected_positive": False,
        },
        {
            **base,
            "lane_id": "E2.3-C-forward-only",
            "direction": "cw",
            "mode": "forward_only",
            "expected_positive": False,
        },
        {
            **base,
            "lane_id": "E2.3-C-broken-return",
            "direction": "cw",
            "mode": "broken_return",
            "expected_positive": False,
        },
        {
            **base,
            "lane_id": "E2.3-C-scrambled-order",
            "direction": "cw",
            "mode": "scrambled_order",
            "expected_positive": False,
        },
    ]


def _symmetry_audit(lanes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_id = {str(lane["lane_id"]): lane for lane in lanes}
    cw = by_id["E2.3-P-adapter-triggered-cw"]
    ccw = by_id["E2.3-R-adapter-triggered-ccw"]
    passed = (
        cw["cycle_count"] == ccw["cycle_count"]
        and cw["trigger_count"] == ccw["trigger_count"]
        and cw["rearm_count"] == ccw["rearm_count"]
        and cw["runtime_event_count"] == ccw["runtime_event_count"]
        and bool(cw["prototype_positive"])
        and bool(ccw["prototype_positive"])
    )
    return {
        "passed": passed,
        "cycle_count_delta": int(cw["cycle_count"]) - int(ccw["cycle_count"]),
        "trigger_count_delta": int(cw["trigger_count"]) - int(ccw["trigger_count"]),
        "rearm_count_delta": int(cw["rearm_count"]) - int(ccw["rearm_count"]),
        "runtime_event_count_delta": int(cw["runtime_event_count"]) - int(ccw["runtime_event_count"]),
    }


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E2.3 Adapter-Triggered Runtime Loop",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Classification: `{result['classification']}`",
        "",
        "Boundary:",
        "",
        "```text",
        "native_grc9v3_evidence = false",
        "native_lgrc9v3_execution = true",
        "adapter_only = false",
        "movement_claim_allowed = false",
        "adapter_driven_runtime_execution = true",
        "native_autonomous_runtime_execution = false",
        "```",
        "",
        "## Audit",
        "",
        f"- direction reversal symmetry: `{result['symmetry_audit']['passed']}`",
        f"- max budget error: `{result['max_budget_error']:.6g}`",
        f"- max event budget error: `{result['max_event_budget_error']:.6g}`",
        f"- expectation failures: `{result['expectation_failures']}`",
        "",
        "## Lane Summary",
        "",
        "| Lane | Mode | Direction | Behavior | Triggers | Continuations | Rearms | Runtime Events | Cycles | Opposite | Budget | Topology | Expected | Positive |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for lane in result["lane_summaries"]:
        lines.append(
            "| {lane_id} | {mode} | {direction} | {behavior} | {triggers} | {continuations} | {rearms} | {events} | {cycles} | {opposite} | {budget} | {topology} | {expected} | {positive} |".format(
                lane_id=lane["lane_id"],
                mode=lane["mode"],
                direction=lane["direction"],
                behavior=lane["behavior_direction"],
                triggers=lane["trigger_count"],
                continuations=lane["route_continuation_count"],
                rearms=lane["rearm_count"],
                events=lane["runtime_event_count"],
                cycles=lane["cycle_count"],
                opposite=lane["opposite_cycle_count"],
                budget="pass" if lane["budget_error"] <= BUDGET_TOLERANCE else "fail",
                topology="pass" if lane["topology_unchanged"] else "fail",
                expected="positive" if lane["expected_positive"] else "negative",
                positive="yes" if lane["prototype_positive"] else "no",
            )
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    lanes = [_run_lane(config) for config in _scenario_config()]
    symmetry = _symmetry_audit(lanes)
    expectation_failures = [
        lane["lane_id"]
        for lane in lanes
        if not lane["expectation_passed"]
    ]
    max_budget_error = max((float(lane["budget_error"]) for lane in lanes), default=0.0)
    max_event_budget_error = max(
        (float(lane["max_event_budget_error"]) for lane in lanes),
        default=0.0,
    )
    errors = list(expectation_failures)
    if not symmetry["passed"]:
        errors.append("direction reversal symmetry failed")
    if max_budget_error > BUDGET_TOLERANCE:
        errors.append("budget error exceeded tolerance")
    if max_event_budget_error > BUDGET_TOLERANCE:
        errors.append("event budget error exceeded tolerance")
    positive_rows = [lane["lane_id"] for lane in lanes if lane["prototype_positive"]]
    classification = (
        "adapter_triggered_runtime_loop_with_controls"
        if not errors and positive_rows
        else "adapter_triggered_runtime_loop_failed_or_negative"
    )
    result = {
        "schema": "n03_e2_3_adapter_triggered_runtime_loop_v1",
        "branch": "E2.3",
        "command": COMMAND,
        "status": "passed" if not errors else "failed",
        "classification": classification,
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": True,
            "adapter_only": False,
            "movement_claim_allowed": False,
        },
        "claim_ceiling": {
            "native_packet_execution": True,
            "adapter_driven_runtime_execution": True,
            "native_autonomous_runtime_execution": False,
            "native_autonomous_trigger": False,
            "native_self_rearm": False,
            "adapter_triggered_self_rearm": bool(positive_rows),
            "loop_claim_allowed": False,
        },
        "positive_rows": positive_rows,
        "expectation_failures": expectation_failures,
        "symmetry_audit": symmetry,
        "max_budget_error": max_budget_error,
        "max_event_budget_error": max_event_budget_error,
        "lane_summaries": lanes,
        "errors": errors,
        "interpretation": (
            "E2.3 shows that an experiment-local surplus trigger adapter can "
            "drive existing LGRC9V3 packet execution into repeated route cycles "
            "with returned-packet self-rearm evidence. Packet departure/arrival "
            "processing, budget accounting, event-time, and proper-time mutation "
            "are native LGRC9V3 runtime behavior. Trigger authorization, route "
            "semantics, and self-rearm labels remain adapter-derived, so this is "
            "adapter-driven runtime execution, not native autonomous LGRC9V3 loop "
            "production. Counted self-rearm evidence requires the child departure "
            "to have been processed by the native runtime inside the bounded event "
            "window."
        ),
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": classification,
                "positive_rows": positive_rows,
                "symmetry_passed": symmetry["passed"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
