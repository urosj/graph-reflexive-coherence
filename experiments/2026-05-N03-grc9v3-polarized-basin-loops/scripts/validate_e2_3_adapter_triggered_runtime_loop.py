#!/usr/bin/env python3
"""Validate E2.3 adapter-triggered runtime loop evidence from artifacts only.

This hardening pass reads the E2.3 JSON artifact and checks that the adapter
did not rely on hidden D2.3 arrays, that self-rearm ordering is causal, that
cycles and controls can be reproduced from event records, and that symmetry and
per-event budget evidence are preserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from loop_observables import load_json, write_json


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
INPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_3_adapter_triggered_runtime_loop.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_3a_adapter_triggered_runtime_loop_hardening.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e2_3a_adapter_triggered_runtime_loop_hardening.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/validate_e2_3_adapter_triggered_runtime_loop.py"
)

BUDGET_TOLERANCE = 1e-9
N_CYCLES_MIN = 3
CW_SEQUENCE = ("S1_to_K2", "K2_to_S2", "S2_to_K1", "K1_to_S1")
CCW_SEQUENCE = ("S1_to_K1_rev", "K1_to_S2_rev", "S2_to_K2_rev", "K2_to_S1_rev")

ALLOWED_ADAPTER_TRIGGER_FIELDS = {
    "event_kind",
    "event_time_key",
    "native_event",
    "packet_amount",
    "packet_id",
    "parent_packet_id",
    "source_pole",
    "source_pole_surplus",
    "trigger_threshold",
    "triggered_channel",
}

ALLOWED_RUNTIME_EVENT_FIELDS = {
    "event_kind",
    "native_event_id",
    "packet_id",
    "event_time_key",
    "scheduler_event_index",
    "amount",
    "source_node_id",
    "target_node_id",
    "edge_id",
    "channel_id",
    "hop_index",
    "schedule_reason",
    "parent_packet_id",
    "budget_error",
    "proper_time_update",
    "topology_mutated",
}


def _cycle_count(events: Sequence[str], sequence: Sequence[str]) -> int:
    expected_index = 0
    cycles = 0
    for event in events:
        if event == sequence[expected_index]:
            expected_index += 1
            if expected_index == len(sequence):
                cycles += 1
                expected_index = 0
        else:
            expected_index = 1 if event == sequence[0] else 0
    return cycles


def _lane_by_id(result: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(lane["lane_id"]): lane for lane in result["lane_summaries"]}


def _adapter_state_visibility(lane: Mapping[str, Any]) -> dict[str, Any]:
    adapter_events = list(lane["adapter_events"])
    runtime_events = list(lane["runtime_events"])
    unexpected_adapter_fields = sorted(
        {
            field
            for event in adapter_events
            for field in event
            if field not in ALLOWED_ADAPTER_TRIGGER_FIELDS
        }
    )
    unexpected_runtime_fields = sorted(
        {
            field
            for event in runtime_events
            for field in event
            if field not in ALLOWED_RUNTIME_EVENT_FIELDS
        }
    )
    trigger_values_measured = all(
        "source_pole_surplus" in event
        and "trigger_threshold" in event
        and float(event["source_pole_surplus"]) >= float(event["trigger_threshold"])
        for event in adapter_events
    )
    adapter_events_marked_non_native = all(
        event.get("native_event") is False for event in adapter_events
    )
    return {
        "unexpected_adapter_fields": unexpected_adapter_fields,
        "unexpected_runtime_fields": unexpected_runtime_fields,
        "trigger_values_measured": trigger_values_measured,
        "adapter_events_marked_non_native": adapter_events_marked_non_native,
        "passed": (
            not unexpected_adapter_fields
            and not unexpected_runtime_fields
            and trigger_values_measured
            and adapter_events_marked_non_native
        ),
    }


def _events_by_packet_id(events: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for event in events:
        packet_id = event.get("packet_id")
        if packet_id is None:
            continue
        grouped.setdefault(str(packet_id), []).append(event)
    return grouped


def _arrival_by_packet_id(events: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    arrivals: dict[str, Mapping[str, Any]] = {}
    for event in events:
        if event.get("event_kind") == "lgrc9v3_packet_arrival":
            arrivals[str(event["packet_id"])] = event
    return arrivals


def _departure_by_packet_id(events: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    departures: dict[str, Mapping[str, Any]] = {}
    for event in events:
        if event.get("event_kind") == "lgrc9v3_packet_departure":
            departures[str(event["packet_id"])] = event
    return departures


def _self_rearm_causality(lane: Mapping[str, Any]) -> dict[str, Any]:
    events = list(lane["runtime_events"])
    arrivals = _arrival_by_packet_id(events)
    departures = _departure_by_packet_id(events)
    trigger_by_packet_id = {
        str(event["packet_id"]): event for event in lane["adapter_events"]
    }
    failures: list[str] = []
    for rearm in lane["rearm_events"]:
        parent_packet_id = str(rearm["parent_packet_id"])
        child_packet_id = str(rearm["child_packet_id"])
        parent_arrival = arrivals.get(parent_packet_id)
        child_trigger = trigger_by_packet_id.get(child_packet_id)
        child_departure = departures.get(child_packet_id)
        if parent_arrival is None:
            failures.append(f"{child_packet_id}: missing parent arrival")
            continue
        if child_trigger is None:
            failures.append(f"{child_packet_id}: missing child trigger")
            continue
        if child_departure is None:
            failures.append(f"{child_packet_id}: missing child departure")
            continue
        if str(parent_arrival["channel_id"]) != str(rearm["parent_channel_id"]):
            failures.append(f"{child_packet_id}: parent arrival channel mismatch")
        if str(child_trigger["triggered_channel"]) != str(rearm["child_channel_id"]):
            failures.append(f"{child_packet_id}: child trigger channel mismatch")
        if str(child_departure["channel_id"]) != str(rearm["child_channel_id"]):
            failures.append(f"{child_packet_id}: child departure channel mismatch")
        if float(parent_arrival["event_time_key"]) > float(child_trigger["event_time_key"]):
            failures.append(f"{child_packet_id}: trigger before parent arrival")
        if float(child_trigger["event_time_key"]) > float(child_departure["event_time_key"]):
            failures.append(f"{child_packet_id}: departure before trigger")
        if float(child_trigger["source_pole_surplus"]) < float(child_trigger["trigger_threshold"]):
            failures.append(f"{child_packet_id}: trigger below threshold")
    return {
        "checked_rearm_count": len(lane["rearm_events"]),
        "failures": failures,
        "passed": not failures,
    }


def _ledger_only_lane_summary(lane: Mapping[str, Any]) -> dict[str, Any]:
    completed_channels = [str(value) for value in lane["completed_channels"]]
    direction = str(lane["direction"])
    sequence = CW_SEQUENCE if direction == "cw" else CCW_SEQUENCE
    opposite = CCW_SEQUENCE if direction == "cw" else CW_SEQUENCE
    event_groups = _events_by_packet_id(lane["runtime_events"])
    paired_packet_count = sum(
        1
        for events in event_groups.values()
        if {"lgrc9v3_packet_departure", "lgrc9v3_packet_arrival"}.issubset(
            {str(event.get("event_kind")) for event in events}
        )
    )
    max_event_budget_error = max(
        (
            abs(float(event["budget_error"]))
            for event in lane["runtime_events"]
            if event.get("budget_error") is not None
        ),
        default=0.0,
    )
    topology_mutation_count = sum(
        1 for event in lane["runtime_events"] if bool(event.get("topology_mutated"))
    )
    cycle_count = _cycle_count(completed_channels, sequence)
    opposite_cycle_count = _cycle_count(completed_channels, opposite)
    positive = (
        cycle_count >= N_CYCLES_MIN
        and int(lane["rearm_count"]) >= max(1, N_CYCLES_MIN - 1)
        and max_event_budget_error <= BUDGET_TOLERANCE
        and topology_mutation_count == 0
    )
    return {
        "lane_id": lane["lane_id"],
        "cycle_count": cycle_count,
        "opposite_cycle_count": opposite_cycle_count,
        "rearm_count": int(lane["rearm_count"]),
        "paired_packet_count": paired_packet_count,
        "max_event_budget_error": max_event_budget_error,
        "topology_mutation_count": topology_mutation_count,
        "ledger_only_positive": positive,
        "matches_runner_positive": positive is bool(lane["prototype_positive"]),
    }


def _direction_symmetry(lanes: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    cw = lanes["E2.3-P-adapter-triggered-cw"]
    ccw = lanes["E2.3-R-adapter-triggered-ccw"]
    fields = (
        "cycle_count",
        "trigger_count",
        "route_continuation_count",
        "rearm_count",
        "runtime_event_count",
        "departure_count",
        "arrival_count",
    )
    deltas = {
        field: int(cw[field]) - int(ccw[field])
        for field in fields
    }
    budget_error_delta = float(cw["budget_error"]) - float(ccw["budget_error"])
    max_event_budget_error_delta = (
        float(cw["max_event_budget_error"]) - float(ccw["max_event_budget_error"])
    )
    cw_trigger_to_departure = _trigger_to_departure_deltas(cw)
    ccw_trigger_to_departure = _trigger_to_departure_deltas(ccw)
    return {
        "deltas": deltas,
        "budget_error_delta": budget_error_delta,
        "max_event_budget_error_delta": max_event_budget_error_delta,
        "cw_trigger_to_departure_deltas": cw_trigger_to_departure,
        "ccw_trigger_to_departure_deltas": ccw_trigger_to_departure,
        "trigger_to_departure_timing_matches": cw_trigger_to_departure == ccw_trigger_to_departure,
        "passed": (
            all(delta == 0 for delta in deltas.values())
            and abs(budget_error_delta) <= BUDGET_TOLERANCE
            and abs(max_event_budget_error_delta) <= BUDGET_TOLERANCE
            and cw_trigger_to_departure == ccw_trigger_to_departure
        ),
    }


def _trigger_to_departure_deltas(lane: Mapping[str, Any]) -> list[float]:
    departures = _departure_by_packet_id(lane["runtime_events"])
    deltas: list[float] = []
    for trigger in lane["adapter_events"]:
        packet_id = str(trigger["packet_id"])
        departure = departures.get(packet_id)
        if departure is None:
            continue
        deltas.append(float(departure["event_time_key"]) - float(trigger["event_time_key"]))
    return deltas


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E2.3-A Adapter-Triggered Runtime Loop Hardening",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Audit",
        "",
        f"- adapter state visibility: `{result['adapter_state_visibility_passed']}`",
        f"- self-rearm causality: `{result['self_rearm_causality_passed']}`",
        f"- ledger-only validation: `{result['ledger_only_validation_passed']}`",
        f"- direction symmetry details: `{result['direction_symmetry']['passed']}`",
        f"- per-event budget preserved: `{result['per_event_budget_preserved']}`",
        "",
        "## Ledger-Only Lane Summary",
        "",
        "| Lane | Cycles | Opposite | Rearms | Paired Packets | Budget Error | Topology Mutations | Positive | Matches Runner |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in result["ledger_only_lane_summaries"]:
        lines.append(
            "| {lane} | {cycles} | {opposite} | {rearms} | {paired} | {budget:.6g} | {topology} | {positive} | {matches} |".format(
                lane=row["lane_id"],
                cycles=row["cycle_count"],
                opposite=row["opposite_cycle_count"],
                rearms=row["rearm_count"],
                paired=row["paired_packet_count"],
                budget=row["max_event_budget_error"],
                topology=row["topology_mutation_count"],
                positive="yes" if row["ledger_only_positive"] else "no",
                matches="yes" if row["matches_runner_positive"] else "no",
            )
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], ""])
    if result["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    source = load_json(INPUT_PATH)
    lanes = _lane_by_id(source)
    visibility = {
        lane_id: _adapter_state_visibility(lane)
        for lane_id, lane in lanes.items()
    }
    rearm_causality = {
        lane_id: _self_rearm_causality(lane)
        for lane_id, lane in lanes.items()
        if lane["rearm_events"]
    }
    ledger_only = [_ledger_only_lane_summary(lane) for lane in lanes.values()]
    symmetry = _direction_symmetry(lanes)
    adapter_state_visibility_passed = all(row["passed"] for row in visibility.values())
    self_rearm_causality_passed = all(row["passed"] for row in rearm_causality.values())
    ledger_only_validation_passed = all(row["matches_runner_positive"] for row in ledger_only)
    per_event_budget_preserved = all(
        row["max_event_budget_error"] <= BUDGET_TOLERANCE for row in ledger_only
    )
    errors: list[str] = []
    if not adapter_state_visibility_passed:
        errors.append("adapter state visibility failed")
    if not self_rearm_causality_passed:
        errors.append("self-rearm causality failed")
    if not ledger_only_validation_passed:
        errors.append("ledger-only validation failed")
    if not symmetry["passed"]:
        errors.append("direction symmetry detail audit failed")
    if not per_event_budget_preserved:
        errors.append("per-event budget preservation failed")
    result = {
        "schema": "n03_e2_3a_adapter_triggered_runtime_loop_hardening_v1",
        "branch": "E2.3-A",
        "command": COMMAND,
        "source_artifact": str(INPUT_PATH.relative_to(EXPERIMENT_ROOT)),
        "status": "passed" if not errors else "failed",
        "adapter_state_visibility": visibility,
        "adapter_state_visibility_passed": adapter_state_visibility_passed,
        "self_rearm_causality": rearm_causality,
        "self_rearm_causality_passed": self_rearm_causality_passed,
        "ledger_only_lane_summaries": ledger_only,
        "ledger_only_validation_passed": ledger_only_validation_passed,
        "direction_symmetry": symmetry,
        "per_event_budget_preserved": per_event_budget_preserved,
        "errors": errors,
        "interpretation": (
            "E2.3-A hardens the adapter-triggered runtime result using only the "
            "E2.3 artifact. It confirms that adapter triggers expose measured "
            "runtime-state fields, self-rearm labels follow returned-packet "
            "arrival and threshold crossing, ledger-only event records reproduce "
            "positive/control classifications, direction reversal symmetry holds "
            "across event counts and timing, and per-event budget errors remain "
            "within tolerance."
        ),
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "adapter_state_visibility_passed": adapter_state_visibility_passed,
                "self_rearm_causality_passed": self_rearm_causality_passed,
                "ledger_only_validation_passed": ledger_only_validation_passed,
                "direction_symmetry_passed": symmetry["passed"],
                "per_event_budget_preserved": per_event_budget_preserved,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
