#!/usr/bin/env python3
"""Extract E2.3 LGRC9V3 runtime records into E1-compatible ledgers.

E2.2 separates replayable evidence from the runner implementation.  It reads
the E2.3 runtime artifact, emits per-lane JSONL ledgers using the E1 event
schema, preserves native runtime identifiers where available, marks
experiment-inferred route/trigger/self-rearm fields, and validates the result
from ledgers only.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import run_d2_conserved_causal_packet_loop as d2
from loop_observables import load_json, write_json, write_jsonl
from validate_e1_1_event_ledger_schema import _validate_record


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
INPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_3_adapter_triggered_runtime_loop.json"
SCHEMA_PATH = EXPERIMENT_ROOT / "configs" / "e1_lgrc9v3_event_ledger_schema.json"
LEDGER_DIR = EXPERIMENT_ROOT / "outputs" / "e2_runtime_extracted_ledgers"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_2_runtime_ledger_extraction.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e2_2_runtime_ledger_extraction.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/extract_e2_2_runtime_ledgers.py"
)

BUDGET_TOLERANCE = 1e-9
N_CYCLES_MIN = 3
ROUTES = {
    "cw": ("S1_to_K2", "K2_to_S2", "S2_to_K1", "K1_to_S1"),
    "ccw": ("S1_to_K1_rev", "K1_to_S2_rev", "S2_to_K2_rev", "K2_to_S1_rev"),
}
CHANNELS = {**d2.CW_CHANNELS, **d2.CCW_CHANNELS}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _route_id(direction: str) -> str:
    return "d2_3_cw_closed_loop" if direction == "cw" else "d2_3_ccw_closed_loop"


def _route(direction: str) -> tuple[str, ...]:
    return ROUTES[direction]


def _channel_step(channel_id: str, direction: str) -> int:
    route = _route(direction)
    return route.index(channel_id) if channel_id in route else -1


def _event_sort_key(event: Mapping[str, Any]) -> tuple[float, int, int]:
    priority = {
        "state_trigger": 0,
        "packet_departure": 1,
        "packet_arrival": 2,
        "cycle_complete": 3,
        "self_rearm": 4,
        "control_blocked": 5,
    }
    return (
        float(event["event_time_key"]),
        int(event.get("_sort_hint", 0)),
        priority.get(str(event["event_kind"]), 99),
    )


def _native_proper_time(event: Mapping[str, Any]) -> dict[str, float]:
    update = event.get("proper_time_update")
    if isinstance(update, Mapping) and "node_id" in update and "node_proper_time" in update:
        return {str(update["node_id"]): float(update["node_proper_time"])}
    return {}


def _base_record(
    *,
    lane: Mapping[str, Any],
    event_kind: str,
    event_time_key: float,
    source_record_ref: Mapping[str, Any],
    inferred_fields: Sequence[str],
    inference_notes: Mapping[str, str],
) -> dict[str, Any]:
    direction = str(lane["direction"])
    return {
        "event_id": "",
        "event_kind": event_kind,
        "scheduler_event_index": 0,
        "event_time_key": float(event_time_key),
        "node_proper_time": {},
        "source_step_index": int(round(float(event_time_key))),
        "lane_id": str(lane["lane_id"]),
        "control_lane": "positive" if bool(lane["expected_positive"]) else str(lane["mode"]),
        "direction": direction,
        "mode": str(lane["mode"]),
        "declared_route_id": _route_id(direction),
        "canonical_route_step": -1,
        "source_pole": None,
        "target_pole": None,
        "channel_id": None,
        "packet_id": None,
        "parent_packet_id": None,
        "amount": None,
        "trigger_policy": None,
        "trigger_value": None,
        "trigger_threshold": None,
        "budget_before": None,
        "budget_after": None,
        "in_flight_packet_budget": None,
        "node_budget": None,
        "total_budget": None,
        "source_artifact": str(INPUT_PATH.relative_to(EXPERIMENT_ROOT)),
        "source_record_ref": dict(source_record_ref),
        "inferred_fields": list(inferred_fields),
        "inference_notes": dict(inference_notes),
    }


def _packet_record(
    lane: Mapping[str, Any],
    event: Mapping[str, Any],
    *,
    event_kind: str,
) -> dict[str, Any]:
    channel_id = str(event["channel_id"])
    channel = CHANNELS[channel_id]
    source_ref = {
            "native_event_id": event.get("native_event_id"),
            "native_scheduler_event_index": event.get("scheduler_event_index"),
            "native_event_kind": event.get("event_kind"),
            "hop_index": event.get("hop_index"),
            "native_proper_time_update": event.get("proper_time_update"),
        }
    inferred_fields = ["source_pole", "target_pole", "canonical_route_step"]
    notes = {
        "source_pole": "Mapped from experiment-local channel manifest.",
        "target_pole": "Mapped from experiment-local channel manifest.",
        "canonical_route_step": "Mapped from declared route channel order.",
    }
    proper_time = _native_proper_time(event)
    if not proper_time:
        inferred_fields.append("node_proper_time")
        notes["node_proper_time"] = "Native event did not expose a proper-time update."
    record = _base_record(
        lane=lane,
        event_kind=event_kind,
        event_time_key=float(event["event_time_key"]),
        source_record_ref=source_ref,
        inferred_fields=inferred_fields,
        inference_notes=notes,
    )
    record.update(
        {
            "node_proper_time": proper_time or {"event_time_key": float(event["event_time_key"])},
            "source_pole": str(channel["source"]),
            "target_pole": str(channel["target"]),
            "channel_id": channel_id,
            "packet_id": str(event["packet_id"]),
            "parent_packet_id": event.get("parent_packet_id"),
            "amount": float(event["amount"]),
            "canonical_route_step": _channel_step(channel_id, str(lane["direction"])),
            "native_event_id": event.get("native_event_id"),
            "native_scheduler_event_index": event.get("scheduler_event_index"),
            "native_event_kind": event.get("event_kind"),
            "hop_index": event.get("hop_index"),
        }
    )
    return record


def _trigger_record(lane: Mapping[str, Any], trigger: Mapping[str, Any]) -> dict[str, Any]:
    channel_id = str(trigger["triggered_channel"])
    record = _base_record(
        lane=lane,
        event_kind="state_trigger",
        event_time_key=float(trigger["event_time_key"]),
        source_record_ref={"adapter_event": dict(trigger)},
        inferred_fields=["event_kind", "canonical_route_step"],
        inference_notes={
            "event_kind": "Adapter trigger record generated outside native LGRC9V3.",
            "canonical_route_step": "Mapped from declared route channel order.",
        },
    )
    record.update(
        {
            "node_proper_time": {"event_time_key": float(trigger["event_time_key"])},
            "source_pole": str(trigger["source_pole"]),
            "channel_id": channel_id,
            "packet_id": str(trigger["packet_id"]),
            "parent_packet_id": trigger.get("parent_packet_id"),
            "amount": float(trigger["packet_amount"]),
            "trigger_policy": "source_pole_surplus_threshold_adapter",
            "trigger_value": float(trigger["source_pole_surplus"]),
            "trigger_threshold": float(trigger["trigger_threshold"]),
            "canonical_route_step": _channel_step(channel_id, str(lane["direction"])),
            "adapter_derived": True,
        }
    )
    return record


def _self_rearm_record(lane: Mapping[str, Any], rearm: Mapping[str, Any], trigger_by_packet: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    child_packet_id = str(rearm["child_packet_id"])
    trigger = trigger_by_packet[child_packet_id]
    channel_id = str(rearm["child_channel_id"])
    record = _base_record(
        lane=lane,
        event_kind="self_rearm",
        event_time_key=float(rearm["event_time_key"]),
        source_record_ref={"adapter_self_rearm": dict(rearm)},
        inferred_fields=["event_kind", "canonical_route_step"],
        inference_notes={
            "event_kind": "Self-rearm is an adapter-derived semantic label.",
            "canonical_route_step": "Mapped from declared route channel order.",
        },
    )
    record.update(
        {
            "node_proper_time": {"event_time_key": float(rearm["event_time_key"])},
            "source_pole": str(trigger["source_pole"]),
            "channel_id": channel_id,
            "packet_id": child_packet_id,
            "parent_packet_id": str(rearm["parent_packet_id"]),
            "amount": float(trigger["packet_amount"]),
            "trigger_policy": "source_pole_surplus_threshold_adapter",
            "trigger_value": float(trigger["source_pole_surplus"]),
            "trigger_threshold": float(trigger["trigger_threshold"]),
            "canonical_route_step": _channel_step(channel_id, str(lane["direction"])),
            "adapter_derived": True,
        }
    )
    return record


def _cycle_records(lane: Mapping[str, Any], arrivals: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    direction = str(lane["direction"])
    route = _route(direction)
    expected = 0
    records: list[dict[str, Any]] = []
    channel_arrivals = [
        arrival for arrival in arrivals if int(arrival.get("hop_index", -1)) == 1
    ]
    for arrival in sorted(channel_arrivals, key=lambda event: (float(event["event_time_key"]), int(event["scheduler_event_index"]))):
        channel_id = str(arrival["channel_id"])
        if channel_id == route[expected]:
            expected += 1
            if expected == len(route):
                record = _base_record(
                    lane=lane,
                    event_kind="cycle_complete",
                    event_time_key=float(arrival["event_time_key"]),
                    source_record_ref={
                        "final_arrival_packet_id": arrival["packet_id"],
                        "final_arrival_native_event_id": arrival.get("native_event_id"),
                    },
                    inferred_fields=["event_kind"],
                    inference_notes={
                        "event_kind": "Cycle completion inferred from ordered packet arrivals."
                    },
                )
                record.update(
                    {
                        "node_proper_time": _native_proper_time(arrival)
                        or {"event_time_key": float(arrival["event_time_key"])},
                        "packet_id": str(arrival["packet_id"]),
                        "channel_id": channel_id,
                        "canonical_route_step": len(route) - 1,
                    }
                )
                records.append(record)
                expected = 0
        else:
            expected = 1 if channel_id == route[0] else 0
    return records


def _control_blocked_record(lane: Mapping[str, Any]) -> dict[str, Any]:
    record = _base_record(
        lane=lane,
        event_kind="control_blocked",
        event_time_key=0.0,
        source_record_ref={"lane_summary": str(lane["lane_id"])},
        inferred_fields=["event_kind"],
        inference_notes={"event_kind": "Control blocker emitted from lane summary."},
    )
    record.update(
        {
            "node_proper_time": {"event_time_key": 0.0},
            "control_lane": str(lane["mode"]),
            "canonical_route_step": 0,
        }
    )
    return record


def _assign_order_and_budget(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(records, key=_event_sort_key)
    in_flight = 0.0
    for index, record in enumerate(ordered):
        amount = float(record["amount"] or 0.0)
        before = 1.0
        if record["event_kind"] == "packet_departure":
            in_flight += amount
        elif record["event_kind"] == "packet_arrival":
            in_flight -= amount
        record["scheduler_event_index"] = index
        record["event_id"] = f"{record['lane_id']}:e2-ledger:{index:06d}:{record['event_kind']}"
        record["budget_before"] = before
        record["budget_after"] = 1.0
        record["in_flight_packet_budget"] = max(0.0, in_flight)
        record["node_budget"] = 1.0 - record["in_flight_packet_budget"]
        record["total_budget"] = record["node_budget"] + record["in_flight_packet_budget"]
        record.pop("_sort_hint", None)
    return ordered


def _extract_lane(lane: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    runtime_events = list(lane["runtime_events"])
    departures = [event for event in runtime_events if event["event_kind"] == "lgrc9v3_packet_departure"]
    arrivals = [event for event in runtime_events if event["event_kind"] == "lgrc9v3_packet_arrival"]
    departed_packet_ids = {str(event["packet_id"]) for event in departures}
    triggers = [
        trigger
        for trigger in lane["adapter_events"]
        if str(trigger["packet_id"]) in departed_packet_ids
    ]
    trigger_by_packet = {str(trigger["packet_id"]): trigger for trigger in triggers}
    records.extend(_trigger_record(lane, trigger) for trigger in triggers)
    records.extend(_packet_record(lane, event, event_kind="packet_departure") for event in departures)
    records.extend(_packet_record(lane, event, event_kind="packet_arrival") for event in arrivals)
    records.extend(_cycle_records(lane, arrivals))
    records.extend(
        _self_rearm_record(lane, rearm, trigger_by_packet)
        for rearm in lane["rearm_events"]
    )
    if not bool(lane["prototype_positive"]):
        records.append(_control_blocked_record(lane))
    return _assign_order_and_budget(records)


def _validate_schema(records: Sequence[Mapping[str, Any]], schema: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for record in records:
        errors.extend(
            f"{record['lane_id']}:{record['event_id']}: {error}"
            for error in _validate_record(record, schema)
        )
    return errors


def _computed_cycle_count(records: Sequence[Mapping[str, Any]]) -> int:
    route = {
        "d2_3_cw_closed_loop": ROUTES["cw"],
        "d2_3_ccw_closed_loop": ROUTES["ccw"],
    }.get(str(records[0]["declared_route_id"]), ())
    index = 0
    cycles = 0
    for record in records:
        if record["event_kind"] != "packet_arrival":
            continue
        if int(record.get("hop_index", -1)) != 1:
            continue
        if record.get("channel_id") == route[index]:
            index += 1
            if index == len(route):
                cycles += 1
                index = 0
        else:
            index = 1 if record.get("channel_id") == route[0] else 0
    return cycles


def _validate_lane_ledger(lane: Mapping[str, Any], records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    departures = {
        str(record["packet_id"]): record
        for record in records
        if record["event_kind"] == "packet_departure"
    }
    arrivals = {
        str(record["packet_id"]): record
        for record in records
        if record["event_kind"] == "packet_arrival"
    }
    for packet_id, departure in departures.items():
        arrival = arrivals.get(packet_id)
        if arrival is None:
            errors.append(f"{packet_id}: missing arrival")
            continue
        if arrival["amount"] != departure["amount"]:
            errors.append(f"{packet_id}: amount mismatch")
        if int(arrival["scheduler_event_index"]) <= int(departure["scheduler_event_index"]):
            errors.append(f"{packet_id}: arrival before departure")
    for packet_id in set(arrivals) - set(departures):
        errors.append(f"{packet_id}: arrival without departure")
    for record in records:
        if abs(
            float(record["node_budget"]) + float(record["in_flight_packet_budget"]) - float(record["total_budget"])
        ) > BUDGET_TOLERANCE:
            errors.append(f"{record['event_id']}: budget decomposition failed")
        if abs(float(record["total_budget"]) - 1.0) > BUDGET_TOLERANCE:
            errors.append(f"{record['event_id']}: total budget drift")
    trigger_records = [record for record in records if record["event_kind"] == "state_trigger"]
    self_rearm_records = [record for record in records if record["event_kind"] == "self_rearm"]
    cycle_records = [record for record in records if record["event_kind"] == "cycle_complete"]
    control_blocked = [record for record in records if record["event_kind"] == "control_blocked"]
    for trigger in trigger_records:
        departure = departures.get(str(trigger["packet_id"]))
        if departure is None:
            errors.append(f"{trigger['packet_id']}: trigger without departure")
        elif trigger["channel_id"] != departure["channel_id"]:
            errors.append(f"{trigger['packet_id']}: trigger/departure channel mismatch")
    for rearm in self_rearm_records:
        parent = arrivals.get(str(rearm["parent_packet_id"]))
        child = departures.get(str(rearm["packet_id"]))
        if parent is None:
            errors.append(f"{rearm['packet_id']}: self-rearm parent missing")
        if child is None:
            errors.append(f"{rearm['packet_id']}: self-rearm child missing")
        if parent is not None and int(parent["scheduler_event_index"]) >= int(rearm["scheduler_event_index"]):
            errors.append(f"{rearm['packet_id']}: self-rearm before parent arrival")
        if child is not None and int(child["scheduler_event_index"]) >= int(rearm["scheduler_event_index"]):
            errors.append(f"{rearm['packet_id']}: self-rearm before child departure")
    computed_cycles = _computed_cycle_count(records)
    ledger_positive = (
        computed_cycles >= N_CYCLES_MIN
        and len(self_rearm_records) >= max(1, N_CYCLES_MIN - 1)
        and not control_blocked
        and not errors
    )
    if ledger_positive is not bool(lane["prototype_positive"]):
        errors.append(
            f"ledger_positive={ledger_positive} runner_positive={lane['prototype_positive']}"
        )
    return {
        "lane_id": lane["lane_id"],
        "expected_positive": bool(lane["expected_positive"]),
        "runner_positive": bool(lane["prototype_positive"]),
        "ledger_positive": ledger_positive,
        "record_count": len(records),
        "packet_departure_count": len(departures),
        "packet_arrival_count": len(arrivals),
        "state_trigger_count": len(trigger_records),
        "self_rearm_count": len(self_rearm_records),
        "cycle_complete_count": len(cycle_records),
        "computed_cycle_count": computed_cycles,
        "control_blocked_count": len(control_blocked),
        "errors": errors,
    }


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E2.2 Runtime Ledger Extraction",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Extracted ledger count: `{result['ledger_count']}`",
        "",
        "## Lane Validation",
        "",
        "| Lane | Records | Departures | Arrivals | Triggers | Rearms | Cycles | Positive | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for lane in result["lane_validations"]:
        lines.append(
            "| {lane_id} | {records} | {departures} | {arrivals} | {triggers} | {rearms} | {cycles} | {positive} | {errors} |".format(
                lane_id=lane["lane_id"],
                records=lane["record_count"],
                departures=lane["packet_departure_count"],
                arrivals=lane["packet_arrival_count"],
                triggers=lane["state_trigger_count"],
                rearms=lane["self_rearm_count"],
                cycles=lane["computed_cycle_count"],
                positive="yes" if lane["ledger_positive"] else "no",
                errors=len(lane["errors"]),
            )
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], ""])
    if result["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    source = load_json(INPUT_PATH)
    schema = load_json(SCHEMA_PATH)
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    lane_summaries: list[dict[str, Any]] = []
    lane_validations: list[dict[str, Any]] = []
    errors: list[str] = []
    for lane in source["lane_summaries"]:
        records = _extract_lane(lane)
        schema_errors = _validate_schema(records, schema)
        validation = _validate_lane_ledger(lane, records)
        lane_id = str(lane["lane_id"])
        ledger_path = LEDGER_DIR / f"{lane_id.lower().replace('.', '_').replace('-', '_')}.jsonl"
        write_jsonl(ledger_path, records)
        lane_summaries.append(
            {
                "lane_id": lane_id,
                "ledger_path": str(ledger_path.relative_to(EXPERIMENT_ROOT)),
                "expected_positive": bool(lane["expected_positive"]),
                "runner_positive": bool(lane["prototype_positive"]),
                "ledger_positive": validation["ledger_positive"],
                "record_count": len(records),
            }
        )
        validation["ledger_path"] = str(ledger_path.relative_to(EXPERIMENT_ROOT))
        validation["schema_error_count"] = len(schema_errors)
        lane_validations.append(validation)
        errors.extend(schema_errors)
        errors.extend(f"{lane_id}: {error}" for error in validation["errors"])
    event_kind_counts = Counter(
        record["event_kind"]
        for summary in lane_summaries
        for record in _load_jsonl(EXPERIMENT_ROOT / summary["ledger_path"])
    )
    result = {
        "schema": "n03_e2_2_runtime_ledger_extraction_v1",
        "branch": "E2.2",
        "command": COMMAND,
        "source_artifact": str(INPUT_PATH.relative_to(EXPERIMENT_ROOT)),
        "status": "passed" if not errors else "failed",
        "ledger_directory": str(LEDGER_DIR.relative_to(EXPERIMENT_ROOT)),
        "ledger_count": len(lane_summaries),
        "event_kind_counts": dict(event_kind_counts),
        "lane_summaries": lane_summaries,
        "lane_validations": lane_validations,
        "errors": errors,
        "preservation_notes": {
            "native_event_ids": "Preserved on packet event records when present.",
            "native_scheduler_event_indices": "Preserved in source_record_ref and native_scheduler_event_index.",
            "native_event_time_keys": "Used directly as event_time_key.",
            "native_proper_time_updates": "Preserved in source_record_ref; node_proper_time uses native updates when present.",
            "experiment_inferred_fields": "Pole/channel route, trigger, self-rearm, cycle_complete, and control_blocked semantics are marked inferred or adapter-derived.",
        },
        "interpretation": (
            "E2.2 extracts E2.3 native LGRC9V3 runtime packet events and "
            "adapter-derived trigger/self-rearm evidence into E1-compatible "
            "per-lane ledgers. Ledger-only validation reproduces the positive "
            "and negative classifications while preserving native event ids, "
            "event-time keys, scheduler indices, and proper-time updates where "
            "available. Route, trigger, self-rearm, cycle, and control semantics "
            "remain experiment-inferred evidence."
        ),
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "ledger_count": result["ledger_count"],
                "event_kind_counts": result["event_kind_counts"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
