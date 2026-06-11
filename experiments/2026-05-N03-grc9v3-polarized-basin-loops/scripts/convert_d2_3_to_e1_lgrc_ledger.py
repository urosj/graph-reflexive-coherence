#!/usr/bin/env python3
"""Convert D2.3 packet-pulse artifacts into E1 LGRC-style event ledgers.

E1.2 is an experiment-local translation step.  It reads the D2.3 summary and
time-series artifacts, emits one JSONL ledger per lane, and marks every field
that is inferred rather than directly serialized by D2.3.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import run_d2_conserved_causal_packet_loop as d2  # noqa: E402
from loop_observables import load_json, write_json, write_jsonl  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = EXPERIMENT_ROOT / "configs" / "e1_lgrc9v3_event_ledger_schema.json"
D2_SUMMARY_PATH = EXPERIMENT_ROOT / "outputs" / "d2_3_self_rearming_packets.json"
OUTPUT_DIR = EXPERIMENT_ROOT / "outputs" / "e1_d2_3_lgrc_event_ledgers"
SUMMARY_PATH = EXPERIMENT_ROOT / "outputs" / "e1_d2_3_lgrc_event_ledger_summary.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e1_d2_3_lgrc_event_ledger_summary.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/convert_d2_3_to_e1_lgrc_ledger.py"
)

TRIGGER_POLICY = "source_pole_surplus_threshold"


def _slug(value: str) -> str:
    return value.lower().replace(".", "_").replace("-", "_")


def _route_id(direction: str) -> str:
    return f"d2_3_{direction}_closed_loop"


def _sequence(direction: str) -> tuple[str, ...]:
    return d2._sequence(direction)


def _channels() -> dict[str, Mapping[str, Any]]:
    return {**d2.CW_CHANNELS, **d2.CCW_CHANNELS}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _channel_step(channel_id: str, direction: str) -> int:
    sequence = _sequence(direction)
    if channel_id in sequence:
        return sequence.index(channel_id)
    return -1


def _channel_source(channel_id: str) -> str | None:
    channel = _channels().get(channel_id)
    return None if channel is None else str(channel["source"])


def _channel_target(channel_id: str) -> str | None:
    channel = _channels().get(channel_id)
    return None if channel is None else str(channel["target"])


def _control_lane(summary: Mapping[str, Any]) -> str:
    if bool(summary["expected_positive"]):
        return "positive"
    mode = str(summary["mode"])
    if mode != "closed_loop":
        return mode
    if float(summary.get("initial_surplus", 0.0)) <= 0.0:
        return "no_surplus"
    if float(summary.get("initial_surplus", 0.0)) < float(summary["trigger_threshold"]):
        return "subthreshold"
    return "negative_control"


def _proper_time(step_index: int, poles: Sequence[str | None]) -> dict[str, float]:
    return {
        pole: float(step_index)
        for pole in sorted({str(pole) for pole in poles if pole is not None})
    }


def _budget_before(row: Mapping[str, Any]) -> float:
    return float(row["total_budget"])


def _budget_after(row: Mapping[str, Any]) -> float:
    return float(row["total_budget"])


def _base_record(
    *,
    event_kind: str,
    scheduler_event_index: int,
    source_step_index: int,
    lane_summary: Mapping[str, Any],
    row: Mapping[str, Any],
    source_artifact: str,
    source_record_ref: Mapping[str, Any],
    source_pole: str | None = None,
    target_pole: str | None = None,
    channel_id: str | None = None,
    packet_id: str | None = None,
    parent_packet_id: str | None = None,
    amount: float | None = None,
    trigger_value: float | None = None,
    trigger_threshold: float | None = None,
    canonical_route_step: int | None = None,
) -> dict[str, Any]:
    direction = str(lane_summary["direction"])
    event_id = (
        f"{_slug(str(lane_summary['lane_id']))}-"
        f"{scheduler_event_index:06d}-{event_kind}"
    )
    inferred_fields = [
        "event_id",
        "scheduler_event_index",
        "event_time_key",
        "node_proper_time",
        "budget_before",
        "budget_after",
    ]
    if event_kind in {"packet_departure", "packet_arrival", "state_trigger"}:
        inferred_fields.append("event_kind")
    if canonical_route_step is None:
        canonical_route_step = (
            _channel_step(channel_id, direction) if channel_id is not None else -1
        )
    poles = (source_pole, target_pole)
    return {
        "event_id": event_id,
        "event_kind": event_kind,
        "scheduler_event_index": scheduler_event_index,
        "event_time_key": float(source_step_index),
        "node_proper_time": _proper_time(source_step_index, poles),
        "source_step_index": int(source_step_index),
        "lane_id": str(lane_summary["lane_id"]),
        "control_lane": _control_lane(lane_summary),
        "direction": direction,
        "mode": str(lane_summary["mode"]),
        "declared_route_id": _route_id(direction),
        "canonical_route_step": int(canonical_route_step),
        "source_pole": source_pole,
        "target_pole": target_pole,
        "channel_id": channel_id,
        "packet_id": packet_id,
        "parent_packet_id": parent_packet_id,
        "amount": None if amount is None else float(amount),
        "trigger_policy": TRIGGER_POLICY if trigger_value is not None else None,
        "trigger_value": None if trigger_value is None else float(trigger_value),
        "trigger_threshold": (
            None if trigger_threshold is None else float(trigger_threshold)
        ),
        "budget_before": _budget_before(row),
        "budget_after": _budget_after(row),
        "in_flight_packet_budget": float(row["packet_budget"]),
        "node_budget": float(row["node_budget"]),
        "total_budget": float(row["total_budget"]),
        "source_artifact": source_artifact,
        "source_record_ref": dict(source_record_ref),
        "inferred_fields": sorted(set(inferred_fields)),
        "inference_notes": {
            "event_id": "Generated deterministically during E1.2 conversion.",
            "scheduler_event_index": "Assigned by ledger event order within the lane.",
            "event_time_key": "Derived from D2.3 source step_index; not native LGRC runtime time.",
            "node_proper_time": "Derived from event_time_key for involved poles; not native LGRC runtime proper time.",
            "budget_before": "D2.3 serializes per-row total budget, not event-local before/after budget.",
            "budget_after": "D2.3 serializes per-row total budget, not event-local before/after budget.",
        },
    }


def _packet_index(rows: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    packets: dict[str, Mapping[str, Any]] = {}
    for line_number, row in enumerate(rows, start=1):
        for packet_event in row["packet_events"]:
            packet_id = str(packet_event["packet_id"])
            packets.setdefault(
                packet_id,
                {
                    **packet_event,
                    "arrival_line": line_number,
                    "arrival_step": int(row["step_index"]),
                },
            )
    return packets


def _new_departures(
    *,
    previous_in_flight: set[str],
    current_in_flight: set[str],
    arrived_ids: set[str],
) -> list[str]:
    surviving = previous_in_flight - arrived_ids
    return sorted(current_in_flight - surviving)


def _initial_departure_records(
    *,
    lane_summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    packet_index: Mapping[str, Mapping[str, Any]],
    source_artifact: str,
    scheduler_event_index: int,
) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    if int(lane_summary["packet_audit"]["initial_trigger_count"]) <= 0:
        return records, scheduler_event_index
    packet = packet_index.get("p000000")
    if packet is None:
        return records, scheduler_event_index
    row = rows[0]
    channel_id = str(packet["channel_id"])
    source_pole = _channel_source(channel_id)
    target_pole = _channel_target(channel_id)
    trigger_value = float(lane_summary["initial_surplus"])
    trigger_threshold = float(lane_summary["trigger_threshold"])
    common_ref = {
        "line": 1,
        "step_index": 0,
        "source": "lane_summary.packet_audit.initial_trigger_count",
    }
    records.append(
        _base_record(
            event_kind="state_trigger",
            scheduler_event_index=scheduler_event_index,
            source_step_index=0,
            lane_summary=lane_summary,
            row=row,
            source_artifact=source_artifact,
            source_record_ref=common_ref,
            source_pole=source_pole,
            channel_id=channel_id,
            trigger_value=trigger_value,
            trigger_threshold=trigger_threshold,
        )
    )
    scheduler_event_index += 1
    records.append(
        _base_record(
            event_kind="packet_departure",
            scheduler_event_index=scheduler_event_index,
            source_step_index=0,
            lane_summary=lane_summary,
            row=row,
            source_artifact=source_artifact,
            source_record_ref={
                **common_ref,
                "packet_id": "p000000",
                "source": "inferred from p000000 future arrival record",
            },
            source_pole=source_pole,
            target_pole=target_pole,
            channel_id=channel_id,
            packet_id="p000000",
            parent_packet_id=None,
            amount=float(packet["amount"]),
        )
    )
    scheduler_event_index += 1
    return records, scheduler_event_index


def _trigger_value(trigger: Mapping[str, Any]) -> float:
    return float(trigger["source_mass_before_departure"]) - float(
        trigger["reference_pole_mass"]
    )


def _convert_lane(
    lane_summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    source_artifact = str(Path(str(lane_summary["timeseries_path"])).name)
    packets_by_id = _packet_index(rows)
    records: list[dict[str, Any]] = []
    scheduler_event_index = 0
    initial_records, scheduler_event_index = _initial_departure_records(
        lane_summary=lane_summary,
        rows=rows,
        packet_index=packets_by_id,
        source_artifact=source_artifact,
        scheduler_event_index=scheduler_event_index,
    )
    records.extend(initial_records)

    previous_in_flight = set()
    for line_number, row in enumerate(rows, start=1):
        source_step_index = int(row["step_index"])
        arrived_ids = {str(event["packet_id"]) for event in row["packet_events"]}
        current_in_flight = {str(packet_id) for packet_id in row["in_flight_packet_ids"]}
        departed_ids = _new_departures(
            previous_in_flight=previous_in_flight,
            current_in_flight=current_in_flight,
            arrived_ids=arrived_ids,
        )
        if source_step_index == 0 and "p000000" in departed_ids:
            departed_ids.remove("p000000")

        for packet_event in row["packet_events"]:
            packet_id = str(packet_event["packet_id"])
            channel_id = str(packet_event["channel_id"])
            records.append(
                _base_record(
                    event_kind="packet_arrival",
                    scheduler_event_index=scheduler_event_index,
                    source_step_index=source_step_index,
                    lane_summary=lane_summary,
                    row=row,
                    source_artifact=source_artifact,
                    source_record_ref={
                        "line": line_number,
                        "step_index": source_step_index,
                        "field": "packet_events",
                        "packet_id": packet_id,
                    },
                    source_pole=_channel_source(channel_id),
                    target_pole=_channel_target(channel_id),
                    channel_id=channel_id,
                    packet_id=packet_id,
                    parent_packet_id=packet_event.get("parent_packet_id"),
                    amount=float(packet_event["amount"]),
                )
            )
            scheduler_event_index += 1

        for trigger_index, trigger in enumerate(row["trigger_events"]):
            channel_id = str(trigger["triggered_channel"])
            source_pole = str(trigger["source_pole"])
            target_pole = _channel_target(channel_id)
            new_packet_id = (
                departed_ids[trigger_index] if trigger_index < len(departed_ids) else None
            )
            trigger_record = _base_record(
                event_kind="state_trigger",
                scheduler_event_index=scheduler_event_index,
                source_step_index=source_step_index,
                lane_summary=lane_summary,
                row=row,
                source_artifact=source_artifact,
                source_record_ref={
                    "line": line_number,
                    "step_index": source_step_index,
                    "field": "trigger_events",
                    "index": trigger_index,
                },
                source_pole=source_pole,
                target_pole=target_pole,
                channel_id=channel_id,
                packet_id=new_packet_id,
                parent_packet_id=trigger.get("parent_packet_id"),
                amount=float(trigger["packet_amount"]),
                trigger_value=_trigger_value(trigger),
                trigger_threshold=float(trigger["trigger_threshold"]),
            )
            records.append(trigger_record)
            scheduler_event_index += 1

            records.append(
                _base_record(
                    event_kind="packet_departure",
                    scheduler_event_index=scheduler_event_index,
                    source_step_index=source_step_index,
                    lane_summary=lane_summary,
                    row=row,
                    source_artifact=source_artifact,
                    source_record_ref={
                        "line": line_number,
                        "step_index": source_step_index,
                        "field": "trigger_events",
                        "index": trigger_index,
                    },
                    source_pole=source_pole,
                    target_pole=target_pole,
                    channel_id=channel_id,
                    packet_id=new_packet_id,
                    parent_packet_id=trigger.get("parent_packet_id"),
                    amount=float(trigger["packet_amount"]),
                )
            )
            scheduler_event_index += 1

        for transition in row["transitions"]:
            if not (
                transition.get("arrived_channel") == _sequence(str(lane_summary["direction"]))[-1]
                and transition.get("next_channel") == _sequence(str(lane_summary["direction"]))[0]
            ):
                continue
            parent_packet_id = str(transition["packet_id"])
            next_channel = str(transition["next_channel"])
            trigger = next(
                (
                    item
                    for item in row["trigger_events"]
                    if item.get("parent_packet_id") == parent_packet_id
                    and item.get("triggered_channel") == next_channel
                ),
                None,
            )
            if trigger is None:
                continue
            child_packet_id = next(
                (
                    record["packet_id"]
                    for record in records
                    if record["event_kind"] == "packet_departure"
                    and record["parent_packet_id"] == parent_packet_id
                    and record["channel_id"] == next_channel
                ),
                None,
            )
            records.append(
                _base_record(
                    event_kind="self_rearm",
                    scheduler_event_index=scheduler_event_index,
                    source_step_index=source_step_index,
                    lane_summary=lane_summary,
                    row=row,
                    source_artifact=source_artifact,
                    source_record_ref={
                        "line": line_number,
                        "step_index": source_step_index,
                        "field": "transitions",
                        "packet_id": parent_packet_id,
                    },
                    source_pole=str(trigger["source_pole"]),
                    target_pole=_channel_target(next_channel),
                    channel_id=next_channel,
                    packet_id=child_packet_id,
                    parent_packet_id=parent_packet_id,
                    amount=float(trigger["packet_amount"]),
                    trigger_value=_trigger_value(trigger),
                    trigger_threshold=float(trigger["trigger_threshold"]),
                )
            )
            scheduler_event_index += 1

        if source_step_index in lane_summary["packet_audit"]["cycle_completion_steps"]:
            final_channel = _sequence(str(lane_summary["direction"]))[-1]
            final_packet_id = next(
                (
                    str(event["packet_id"])
                    for event in row["packet_events"]
                    if str(event["channel_id"]) == final_channel
                ),
                None,
            )
            records.append(
                _base_record(
                    event_kind="cycle_complete",
                    scheduler_event_index=scheduler_event_index,
                    source_step_index=source_step_index,
                    lane_summary=lane_summary,
                    row=row,
                    source_artifact=source_artifact,
                    source_record_ref={
                        "line": line_number,
                        "step_index": source_step_index,
                        "field": "packet_audit.cycle_completion_steps",
                    },
                    packet_id=final_packet_id,
                    canonical_route_step=len(_sequence(str(lane_summary["direction"]))) - 1,
                )
            )
            scheduler_event_index += 1

        previous_in_flight = current_in_flight

    if not bool(lane_summary["prototype_positive"]):
        row = rows[-1]
        records.append(
            _base_record(
                event_kind="control_blocked",
                scheduler_event_index=scheduler_event_index,
                source_step_index=int(row["step_index"]),
                lane_summary=lane_summary,
                row=row,
                source_artifact=source_artifact,
                source_record_ref={
                    "field": "lane_summary.prototype_positive",
                    "value": False,
                },
            )
        )
    return records


def _validate_record(
    record: Mapping[str, Any], schema: Mapping[str, Any]
) -> list[str]:
    errors: list[str] = []
    for field_name in schema["ledger_record_required_fields"]:
        if field_name not in record:
            errors.append(f"{record.get('event_id', '<unknown>')}: missing {field_name}")
    contracts = schema["event_kind_contracts"]
    event_kind = record.get("event_kind")
    if event_kind not in contracts:
        errors.append(f"{record.get('event_id', '<unknown>')}: unknown kind {event_kind}")
        return errors
    for field_name in contracts[event_kind]["non_null_fields"]:
        if record.get(field_name) is None:
            errors.append(
                f"{record.get('event_id', '<unknown>')}: {event_kind} requires {field_name}"
            )
    return errors


def _write_report(summary: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E1.2 D2.3 To LGRC Event Ledger Summary",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{summary['status']}`",
        "",
        f"Converted lanes: `{summary['converted_lane_count']}`",
        f"Total ledger events: `{summary['total_event_count']}`",
        "",
        "Boundary:",
        "",
        "```text",
        "native_grc9v3_evidence = false",
        "native_lgrc9v3_execution = false",
        "adapter_only = true",
        "movement_claim_allowed = false",
        "```",
        "",
        "## Event Counts By Kind",
        "",
    ]
    for event_kind, count in summary["event_counts_by_kind"].items():
        lines.append(f"- `{event_kind}`: `{count}`")
    lines.extend(["", "## Lane Ledgers", ""])
    for lane in summary["lane_summaries"]:
        lines.append(
            "- `{lane_id}` -> `{path}` (`{count}` events)".format(
                lane_id=lane["lane_id"],
                path=lane["ledger_path"],
                count=lane["event_count"],
            )
        )
    lines.extend(["", "## Inference Notes", ""])
    lines.extend(f"- `{field}`" for field in summary["inferred_fields"])
    lines.extend(["", "## Errors", ""])
    if summary["errors"]:
        lines.extend(f"- {error}" for error in summary["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    d2_summary = load_json(D2_SUMMARY_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    lane_outputs: list[dict[str, Any]] = []
    counts_by_kind: dict[str, int] = {kind: 0 for kind in schema["event_kinds"]}
    inferred_fields: set[str] = set()

    for lane_summary in d2_summary["lane_summaries"]:
        timeseries_path = Path(str(lane_summary["timeseries_path"]))
        rows = _load_jsonl(timeseries_path)
        records = _convert_lane(lane_summary, rows)
        for record in records:
            errors.extend(_validate_record(record, schema))
            counts_by_kind[record["event_kind"]] = counts_by_kind.get(record["event_kind"], 0) + 1
            inferred_fields.update(record["inferred_fields"])
        ledger_path = OUTPUT_DIR / f"{_slug(str(lane_summary['lane_id']))}_ledger.jsonl"
        write_jsonl(ledger_path, records)
        lane_outputs.append(
            {
                "lane_id": lane_summary["lane_id"],
                "ledger_path": str(ledger_path.relative_to(EXPERIMENT_ROOT)),
                "event_count": len(records),
                "prototype_positive": bool(lane_summary["prototype_positive"]),
                "expected_positive": bool(lane_summary["expected_positive"]),
            }
        )

    summary = {
        "schema": "n03_e1_d2_3_lgrc_event_ledger_summary_v1",
        "branch": "E1.2",
        "command": COMMAND,
        "status": "passed" if not errors else "failed",
        "source_summary": str(D2_SUMMARY_PATH.relative_to(EXPERIMENT_ROOT)),
        "converted_lane_count": len(lane_outputs),
        "total_event_count": sum(item["event_count"] for item in lane_outputs),
        "event_counts_by_kind": counts_by_kind,
        "lane_summaries": lane_outputs,
        "inferred_fields": sorted(inferred_fields),
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": False,
            "adapter_only": True,
            "movement_claim_allowed": False,
        },
        "errors": errors,
    }
    write_json(SUMMARY_PATH, summary)
    _write_report(summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "converted_lane_count": summary["converted_lane_count"],
                "total_event_count": summary["total_event_count"],
                "event_counts_by_kind": summary["event_counts_by_kind"],
                "errors": len(errors),
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
