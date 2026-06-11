#!/usr/bin/env python3
"""Run D2.2 state-triggered packet departure bridge.

D2.2 asks whether the D2 packet loop can be launched from a measured state
surface instead of an explicit packet seed schedule.  The trigger is still an
experiment-local prototype rule:

    source pole mass exceeds its reference mass by a threshold

When the trigger fires, coherence is moved from the source pole into an
in-flight packet.  The target pole becomes trigger-eligible only when that
packet arrives.  This keeps the mechanism packetized and conserved, but makes
departure timing depend on runtime state rather than a hand-authored event
schedule.

This is not native GRC9V3 evidence and does not modify `src/*`.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

import run_d2_conserved_causal_packet_loop as d2  # noqa: E402
from loop_observables import load_json, write_json, write_jsonl  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d2_2_state_triggered_packets.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d2_2_state_triggered_packets.md"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "d2_2_state_triggered_packets_timeseries"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d2_2_state_triggered_packets.py"
)

BUDGET_TOLERANCE = 1e-9
N_CYCLES_MIN = 3
DEFAULT_PACKET_AMOUNT = 0.006
DEFAULT_TRIGGER_THRESHOLD = 0.003
RESERVE_NODES = (2, 5, 8, 11)


@dataclass(frozen=True)
class Packet:
    packet_id: str
    channel_id: str
    amount: float
    depart_step: int
    arrive_step: int
    parent_packet_id: str | None = None


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _all_channels() -> dict[str, Mapping[str, Any]]:
    return {**d2.CW_CHANNELS, **d2.CCW_CHANNELS}


def _opposite_direction(direction: str) -> str:
    return "ccw" if direction == "cw" else "cw"


def _expected_sequence(config: Mapping[str, Any]) -> tuple[str, ...]:
    return d2._sequence(str(config["direction"]))


def _behavior_sequence(config: Mapping[str, Any]) -> tuple[str, ...]:
    return d2._sequence(str(config.get("behavior_direction", config["direction"])))


def _reference_pole_mass() -> float:
    nodes = d2._initial_nodes()
    return d2._pole_mass(nodes, "S1")


def _initial_nodes(config: Mapping[str, Any]) -> dict[int, float]:
    nodes = d2._initial_nodes()
    surplus = float(config.get("initial_surplus", 0.0))
    surplus_pole = str(config.get("initial_surplus_pole", "S1"))
    if surplus > 0.0:
        for node_id in d2.POLES[surplus_pole]:
            nodes[node_id] += surplus / len(d2.POLES[surplus_pole])
        for node_id in RESERVE_NODES:
            nodes[node_id] -= surplus / len(RESERVE_NODES)
    perturbation = float(config.get("node_perturbation", 0.0))
    if perturbation:
        nodes[0] += perturbation
        nodes[6] -= perturbation
    return nodes


def _next_delay(config: Mapping[str, Any], *, step_index: int, event_index: int) -> int:
    base_delay = int(config["packet_delay"])
    jitter = tuple(int(value) for value in config.get("delay_jitter", ()))
    if not jitter:
        return max(1, base_delay)
    return max(1, base_delay + jitter[(step_index + event_index) % len(jitter)])


def _packet_budget(packets: Sequence[Packet]) -> float:
    return sum(packet.amount for packet in packets)


def _triggerable_channels(
    nodes: Mapping[int, float],
    *,
    config: Mapping[str, Any],
    channels: Mapping[str, Mapping[str, Any]],
    sequence: Sequence[str],
) -> list[tuple[str, float]]:
    reference = _reference_pole_mass()
    threshold = float(config["trigger_threshold"])
    packet_amount = float(config["packet_amount"])
    mode = str(config["mode"])
    if mode == "forward_only":
        candidate_sequence = tuple(sequence[:1])
    elif mode == "broken_return":
        candidate_sequence = tuple(sequence[:-1])
    else:
        candidate_sequence = tuple(sequence)
    candidates: list[tuple[str, float]] = []
    for channel_id in candidate_sequence:
        source = str(channels[channel_id]["source"])
        surplus = d2._pole_mass(nodes, source) - reference
        if surplus >= threshold:
            candidates.append((channel_id, min(packet_amount, surplus)))
    return candidates


def _depart(
    nodes: dict[int, float],
    packets: deque[Packet],
    *,
    channel_id: str,
    channels: Mapping[str, Mapping[str, Any]],
    amount: float,
    depart_step: int,
    arrive_step: int,
    parent_packet_id: str | None,
    next_packet_index: int,
    created: dict[str, Packet],
    duplicate_packet_ids: set[str],
) -> tuple[int, float]:
    actual = d2._subtract_from_source(
        nodes,
        channel_id=channel_id,
        channels=channels,
        amount=amount,
    )
    if actual <= 0.0:
        return next_packet_index, 0.0
    packet_id = f"p{next_packet_index:06d}"
    packet = Packet(
        packet_id=packet_id,
        channel_id=channel_id,
        amount=actual,
        depart_step=depart_step,
        arrive_step=arrive_step,
        parent_packet_id=parent_packet_id,
    )
    if packet_id in created:
        duplicate_packet_ids.add(packet_id)
    created[packet_id] = packet
    packets.append(packet)
    return next_packet_index + 1, actual


def _trigger_departure(
    nodes: dict[int, float],
    packets: deque[Packet],
    *,
    config: Mapping[str, Any],
    channels: Mapping[str, Mapping[str, Any]],
    sequence: Sequence[str],
    step_index: int,
    event_index: int,
    parent_packet_id: str | None,
    next_packet_index: int,
    created: dict[str, Packet],
    duplicate_packet_ids: set[str],
) -> tuple[int, dict[str, Any] | None]:
    if str(config["mode"]) == "no_trigger":
        return next_packet_index, None
    candidates = _triggerable_channels(
        nodes,
        config=config,
        channels=channels,
        sequence=sequence,
    )
    if not candidates:
        return next_packet_index, None
    channel_id, amount = candidates[0]
    before_mass = d2._pole_mass(nodes, str(channels[channel_id]["source"]))
    next_packet_index, actual = _depart(
        nodes,
        packets,
        channel_id=channel_id,
        channels=channels,
        amount=amount,
        depart_step=step_index,
        arrive_step=step_index + _next_delay(config, step_index=step_index, event_index=event_index),
        parent_packet_id=parent_packet_id,
        next_packet_index=next_packet_index,
        created=created,
        duplicate_packet_ids=duplicate_packet_ids,
    )
    if actual <= 0.0:
        return next_packet_index, None
    return next_packet_index, {
        "triggered_channel": channel_id,
        "source_pole": str(channels[channel_id]["source"]),
        "source_mass_before_departure": before_mass,
        "reference_pole_mass": _reference_pole_mass(),
        "trigger_threshold": float(config["trigger_threshold"]),
        "packet_amount": actual,
        "parent_packet_id": parent_packet_id,
    }


def _transition_record(
    *,
    packet: Packet,
    trigger: Mapping[str, Any] | None,
    expected_sequence: Sequence[str],
    behavior_sequence: Sequence[str],
    channels: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    next_channel = None if trigger is None else str(trigger["triggered_channel"])
    canonical_next = (
        expected_sequence[(expected_sequence.index(packet.channel_id) + 1) % len(expected_sequence)]
        if packet.channel_id in expected_sequence
        else None
    )
    behavior_next = (
        behavior_sequence[(behavior_sequence.index(packet.channel_id) + 1) % len(behavior_sequence)]
        if packet.channel_id in behavior_sequence
        else None
    )
    if next_channel is None:
        handoff_contiguous = True
    else:
        handoff_contiguous = (
            channels[packet.channel_id]["target"] == channels[next_channel]["source"]
        )
    return {
        "packet_id": packet.packet_id,
        "arrived_channel": packet.channel_id,
        "next_channel": next_channel,
        "canonical_next_channel": canonical_next,
        "behavior_next_channel": behavior_next,
        "canonical_transition_valid": next_channel is None or next_channel == canonical_next,
        "declared_transition_valid": next_channel is None or next_channel == behavior_next,
        "handoff_contiguous": handoff_contiguous,
    }


def _row(
    *,
    step_index: int,
    config: Mapping[str, Any],
    nodes_pre: Mapping[int, float],
    nodes_post: Mapping[int, float],
    packets: Sequence[Packet],
    events: Sequence[str],
    packet_events: Sequence[Mapping[str, Any]],
    trigger_events: Sequence[Mapping[str, Any]],
    transitions: Sequence[Mapping[str, Any]],
    flux_uv: Mapping[str, float],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "step_index": step_index,
        "lane_id": str(config["lane_id"]),
        "direction": str(config["direction"]),
        "mode": str(config["mode"]),
        "events": list(events),
        "packet_events": list(packet_events),
        "trigger_events": list(trigger_events),
        "transitions": list(transitions),
        "flux_uv": dict(flux_uv),
        **d2._loop_metrics(flux_uv),
        "node_budget": d2._node_budget(nodes_post),
        "packet_budget": _packet_budget(packets),
        "in_flight_packet_ids": [packet.packet_id for packet in packets],
    }
    row["total_budget"] = row["node_budget"] + row["packet_budget"]
    for pole_id in d2.POLES:
        row[f"C_{pole_id}_pre"] = d2._pole_mass(nodes_pre, pole_id)
        row[f"C_{pole_id}_post"] = d2._pole_mass(nodes_post, pole_id)
        row[f"delta_{pole_id}"] = row[f"C_{pole_id}_post"] - row[f"C_{pole_id}_pre"]
    return row


def _run_lane(config: Mapping[str, Any], *, total_steps: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    channels = _all_channels()
    behavior_sequence = _behavior_sequence(config)
    expected_sequence = _expected_sequence(config)
    nodes = _initial_nodes(config)
    packets: deque[Packet] = deque()
    rows: list[dict[str, Any]] = []
    created: dict[str, Packet] = {}
    absorbed: set[str] = set()
    duplicate_packet_ids: set[str] = set()
    next_packet_index = 0
    initial_trigger_count = 0

    # Initial departure is state-triggered from the configured initial surface.
    next_packet_index, initial_trigger = _trigger_departure(
        nodes,
        packets,
        config=config,
        channels=channels,
        sequence=behavior_sequence,
        step_index=0,
        event_index=0,
        parent_packet_id=None,
        next_packet_index=next_packet_index,
        created=created,
        duplicate_packet_ids=duplicate_packet_ids,
    )
    if initial_trigger is not None:
        initial_trigger_count = 1

    for step_index in range(total_steps):
        nodes_pre = dict(nodes)
        events: list[str] = []
        packet_events: list[dict[str, Any]] = []
        trigger_events: list[dict[str, Any]] = []
        transitions: list[dict[str, Any]] = []
        flux_maps: list[dict[str, float]] = []
        arriving = sorted(
            [packet for packet in packets if packet.arrive_step <= step_index],
            key=lambda packet: packet.packet_id,
        )
        packets = deque(packet for packet in packets if packet.arrive_step > step_index)
        for event_index, packet in enumerate(arriving):
            d2._add_to_target(
                nodes,
                channel_id=packet.channel_id,
                channels=channels,
                amount=packet.amount,
            )
            absorbed.add(packet.packet_id)
            events.append(packet.channel_id)
            packet_events.append(
                {
                    "packet_id": packet.packet_id,
                    "channel_id": packet.channel_id,
                    "amount": packet.amount,
                    "depart_step": packet.depart_step,
                    "arrive_step": packet.arrive_step,
                    "parent_packet_id": packet.parent_packet_id,
                }
            )
            flux_maps.append(
                d2._flux_for_event(
                    packet.channel_id,
                    channels=channels,
                    amount=packet.amount,
                )
            )
            next_packet_index, trigger = _trigger_departure(
                nodes,
                packets,
                config=config,
                channels=channels,
                sequence=behavior_sequence,
                step_index=step_index,
                event_index=event_index,
                parent_packet_id=packet.packet_id,
                next_packet_index=next_packet_index,
                created=created,
                duplicate_packet_ids=duplicate_packet_ids,
            )
            if trigger is not None:
                trigger_events.append(trigger)
            transitions.append(
                _transition_record(
                    packet=packet,
                    trigger=trigger,
                    expected_sequence=expected_sequence,
                    behavior_sequence=behavior_sequence,
                    channels=channels,
                )
            )
        rows.append(
            _row(
                step_index=step_index,
                config=config,
                nodes_pre=nodes_pre,
                nodes_post=nodes,
                packets=tuple(packets),
                events=events,
                packet_events=packet_events,
                trigger_events=trigger_events,
                transitions=transitions,
                flux_uv=d2._merge_flux(flux_maps),
            )
        )

    in_flight_ids = {packet.packet_id for packet in packets}
    unknown_parent_ids = {
        packet.parent_packet_id
        for packet in created.values()
        if packet.parent_packet_id is not None and packet.parent_packet_id not in created
    }
    unknown_channel_ids = {
        packet.channel_id for packet in created.values() if packet.channel_id not in channels
    }
    packet_audit = {
        "packets_created_total": len(created),
        "packets_absorbed_total": len(absorbed),
        "packets_in_flight_total": len(in_flight_ids),
        "initial_trigger_count": initial_trigger_count,
        "packet_balance_error": len(created) - len(absorbed) - len(in_flight_ids),
        "duplicate_packet_ids": sorted(duplicate_packet_ids),
        "orphan_parent_ids": sorted(str(value) for value in unknown_parent_ids),
        "unknown_channel_ids": sorted(unknown_channel_ids),
    }
    return rows, packet_audit


def _summarize_lane(
    config: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    packet_audit: Mapping[str, Any],
) -> dict[str, Any]:
    expected_sequence = _expected_sequence(config)
    opposite_sequence = d2._sequence(_opposite_direction(str(config["direction"])))
    events = [event for row in rows for event in row["events"]]
    trigger_events = [event for row in rows for event in row["trigger_events"]]
    trigger_count = int(packet_audit["initial_trigger_count"]) + len(trigger_events)
    transitions = [transition for row in rows for transition in row["transitions"]]
    budget_errors = [abs(float(row["total_budget"]) - d2.TOTAL_BUDGET) for row in rows]
    cycle_count = d2._cycle_count(events, expected_sequence)
    opposite_cycle_count = d2._cycle_count(events, opposite_sequence)
    budget_passed = max(budget_errors, default=0.0) <= BUDGET_TOLERANCE
    packet_audit_passed = (
        int(packet_audit["packet_balance_error"]) == 0
        and not packet_audit["duplicate_packet_ids"]
        and not packet_audit["orphan_parent_ids"]
        and not packet_audit["unknown_channel_ids"]
    )
    canonical_causality_passed = all(
        bool(transition["canonical_transition_valid"]) and bool(transition["handoff_contiguous"])
        for transition in transitions
    )
    declared_causality_passed = all(
        bool(transition["declared_transition_valid"])
        for transition in transitions
    )
    trigger_seen = trigger_count > 0
    prototype_positive = (
        cycle_count >= N_CYCLES_MIN
        and trigger_seen
        and budget_passed
        and packet_audit_passed
        and canonical_causality_passed
    )
    expected_positive = bool(config["expected_positive"])
    return {
        "lane_id": str(config["lane_id"]),
        "direction": str(config["direction"]),
        "behavior_direction": str(config.get("behavior_direction", config["direction"])),
        "mode": str(config["mode"]),
        "packet_delay": int(config["packet_delay"]),
        "packet_amount": float(config["packet_amount"]),
        "trigger_threshold": float(config["trigger_threshold"]),
        "initial_surplus": float(config.get("initial_surplus", 0.0)),
        "expected_positive": expected_positive,
        "event_count": len(events),
        "trigger_count": trigger_count,
        "arrival_trigger_count": len(trigger_events),
        "initial_trigger_count": int(packet_audit["initial_trigger_count"]),
        "cycle_count": cycle_count,
        "opposite_cycle_count": opposite_cycle_count,
        "max_abs_loop_circulation": max(
            (abs(float(row["loop_circulation"])) for row in rows),
            default=0.0,
        ),
        "max_abs_normalized_circulation": max(
            (abs(float(row["loop_normalized_circulation"])) for row in rows),
            default=0.0,
        ),
        "mean_abs_normalized_circulation": _mean(
            [abs(float(row["loop_normalized_circulation"])) for row in rows]
        ),
        "max_budget_error": max(budget_errors, default=0.0),
        "budget_passed": budget_passed,
        "packet_audit_passed": packet_audit_passed,
        "canonical_causality_passed": canonical_causality_passed,
        "declared_causality_passed": declared_causality_passed,
        "trigger_seen": trigger_seen,
        "prototype_positive": prototype_positive,
        "expectation_passed": prototype_positive is expected_positive,
        "packet_audit": dict(packet_audit),
    }


def _scenario_config() -> list[dict[str, Any]]:
    return [
        {
            "lane_id": "D2.2-U0-no-surplus",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": 0.0,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.2-P-cw-state-triggered",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.2-R-ccw-state-triggered",
            "direction": "ccw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.2-P-cw-delay-1",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 1,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.2-P-cw-delay-6",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 6,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.2-C-subthreshold-surface",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_TRIGGER_THRESHOLD * 0.5,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.2-C-wrong-direction-trigger",
            "direction": "cw",
            "behavior_direction": "ccw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.2-C-forward-only",
            "direction": "cw",
            "mode": "forward_only",
            "packet_delay": 3,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.2-C-broken-return",
            "direction": "cw",
            "mode": "broken_return",
            "packet_delay": 3,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.2-S-weak-trigger",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.0005,
            "trigger_threshold": 0.00025,
            "initial_surplus": 0.0005,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.2-S-over-trigger",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.02,
            "trigger_threshold": 0.01,
            "initial_surplus": 0.02,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.2-N-jittered-delay",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "delay_jitter": (-1, 0, 1),
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.2-N-node-perturbation",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": DEFAULT_PACKET_AMOUNT,
            "trigger_threshold": DEFAULT_TRIGGER_THRESHOLD,
            "initial_surplus": DEFAULT_PACKET_AMOUNT,
            "node_perturbation": 0.001,
            "expected_positive": True,
        },
    ]


def _symmetry_audit(summaries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_id = {str(summary["lane_id"]): summary for summary in summaries}
    cw = by_id["D2.2-P-cw-state-triggered"]
    ccw = by_id["D2.2-R-ccw-state-triggered"]
    passed = (
        cw["cycle_count"] == ccw["cycle_count"]
        and cw["event_count"] == ccw["event_count"]
        and cw["trigger_count"] == ccw["trigger_count"]
        and abs(float(cw["max_budget_error"]) - float(ccw["max_budget_error"])) <= BUDGET_TOLERANCE
        and bool(cw["prototype_positive"])
        and bool(ccw["prototype_positive"])
    )
    return {
        "cw_lane": cw["lane_id"],
        "ccw_lane": ccw["lane_id"],
        "cycle_count_delta": int(cw["cycle_count"]) - int(ccw["cycle_count"]),
        "event_count_delta": int(cw["event_count"]) - int(ccw["event_count"]),
        "trigger_count_delta": int(cw["trigger_count"]) - int(ccw["trigger_count"]),
        "max_budget_error_delta": float(cw["max_budget_error"]) - float(ccw["max_budget_error"]),
        "passed": passed,
    }


def _classify(
    summaries: Sequence[Mapping[str, Any]],
    *,
    symmetry: Mapping[str, Any],
) -> str:
    failed_expectations = [row["lane_id"] for row in summaries if not row["expectation_passed"]]
    if failed_expectations:
        return "d2_2_state_triggered_packet_expectation_failure"
    if not symmetry["passed"]:
        return "d2_2_state_triggered_packet_symmetry_failure"
    positives = [row for row in summaries if row["prototype_positive"]]
    if positives:
        return "d2_2_state_triggered_packet_departure_positive_with_controls"
    return "d2_2_state_triggered_packet_departure_no_positive_rows"


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D2.2 State-Triggered Packet Departure",
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
        "D2.2 launches packet departures from measured pole-surplus state",
        "instead of a hand-authored packet seed schedule. It remains",
        "experiment-local packetized prototype evidence, not native GRC9V3",
        "evidence.",
        "",
        "Budget invariant:",
        "",
        "```text",
        "B = sum(node coherence) + sum(in-flight packet coherence)",
        "```",
        "",
        "## Audit",
        "",
        f"- direction reversal symmetry: `{result['symmetry_audit']['passed']}`",
        f"- max node-plus-packet budget error: `{result['max_packet_budget_error']:.6g}`",
        f"- duplicate packet ids: `{result['duplicate_packet_id_count']}`",
        f"- orphan parent ids: `{result['orphan_parent_id_count']}`",
        f"- unknown channel ids: `{result['unknown_channel_id_count']}`",
        "",
        "## Lane Summary",
        "",
        "| Lane | Mode | Direction | Delay | Initial Surplus | Triggers | Events | Cycles | Opposite | Budget | Packet Audit | Causality | Expected | Positive |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in result["lane_summaries"]:
        lines.append(
            "| {lane} | {mode} | {direction} | {delay} | {surplus:.6g} | {triggers} | {events} | {cycles} | {opposite} | {budget} | {packet_audit} | {causality} | {expected} | {positive} |".format(
                lane=row["lane_id"],
                mode=row["mode"],
                direction=row["direction"],
                delay=row["packet_delay"],
                surplus=row["initial_surplus"],
                triggers=row["trigger_count"],
                events=row["event_count"],
                cycles=row["cycle_count"],
                opposite=row["opposite_cycle_count"],
                budget="pass" if row["budget_passed"] else "fail",
                packet_audit="pass" if row["packet_audit_passed"] else "fail",
                causality="pass" if row["canonical_causality_passed"] else "fail",
                expected="positive" if row["expected_positive"] else "negative",
                positive="yes" if row["prototype_positive"] else "no",
            )
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], "", "## Errors", ""])
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    total_steps = int(manifest["runner_config"]["total_steps"])
    lane_summaries: list[dict[str, Any]] = []
    errors: list[str] = []

    for config in _scenario_config():
        rows, packet_audit = _run_lane(config, total_steps=total_steps)
        lane_id = str(config["lane_id"])
        path = TIMESERIES_DIR / f"{lane_id.lower().replace('.', '_').replace('-', '_')}_timeseries.jsonl"
        write_jsonl(path, rows)
        summary = _summarize_lane(config, rows, packet_audit)
        summary["timeseries_path"] = str(path)
        lane_summaries.append(summary)
        if not summary["budget_passed"]:
            errors.append(f"{lane_id} failed budget")
        if not summary["packet_audit_passed"]:
            errors.append(f"{lane_id} failed packet audit")
        if not summary["expectation_passed"]:
            errors.append(f"{lane_id} failed expectation")

    symmetry = _symmetry_audit(lane_summaries)
    if not symmetry["passed"]:
        errors.append("direction reversal symmetry failed")

    classification = _classify(lane_summaries, symmetry=symmetry)
    positive_rows = [row["lane_id"] for row in lane_summaries if row["prototype_positive"]]
    max_packet_budget_error = max(
        (float(row["max_budget_error"]) for row in lane_summaries),
        default=0.0,
    )
    duplicate_packet_id_count = sum(
        len(row["packet_audit"]["duplicate_packet_ids"]) for row in lane_summaries
    )
    orphan_parent_id_count = sum(
        len(row["packet_audit"]["orphan_parent_ids"]) for row in lane_summaries
    )
    unknown_channel_id_count = sum(
        len(row["packet_audit"]["unknown_channel_ids"]) for row in lane_summaries
    )
    interpretation = (
        "D2.2 shows that the D2 packetized prototype can be launched by a "
        "measured state trigger: source-pole mass above a serialized threshold. "
        "Departure timing is derived from the evolving node state plus packet "
        "arrivals, not from a hand-authored packet seed schedule. Positive rows "
        "remain packetized prototype evidence only; native GRC9V3 and movement "
        "claims remain blocked."
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_d2_2_state_triggered_packets_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pass" if not errors else "fail",
        "command": COMMAND,
        "native_evidence": False,
        "positive_loop_claim_allowed": False,
        "budget_invariant": "node_coherence + in_flight_packet_coherence",
        "trigger_policy": "source_pole_mass_minus_reference_mass >= trigger_threshold",
        "classification": classification,
        "n_cycles_min": N_CYCLES_MIN,
        "positive_rows": positive_rows,
        "symmetry_audit": symmetry,
        "max_packet_budget_error": max_packet_budget_error,
        "duplicate_packet_id_count": duplicate_packet_id_count,
        "orphan_parent_id_count": orphan_parent_id_count,
        "unknown_channel_id_count": unknown_channel_id_count,
        "lane_summaries": lane_summaries,
        "interpretation": interpretation,
        "errors": errors,
    }
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
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
