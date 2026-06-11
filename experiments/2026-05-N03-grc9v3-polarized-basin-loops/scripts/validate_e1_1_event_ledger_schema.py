#!/usr/bin/env python3
"""Validate the E1.1 event-ledger schema against representative records.

This is an experiment-local schema check.  It does not import or modify
`src/pygrc`; it validates that E1.1 defines the six event kinds and the fields
needed for the D2.3-to-LGRC ledger converter.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from loop_observables import load_json, write_json  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = EXPERIMENT_ROOT / "configs" / "e1_lgrc9v3_event_ledger_schema.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e1_event_ledger_schema_validation.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e1_event_ledger_schema_validation.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/validate_e1_1_event_ledger_schema.py"
)


def _sample_base(event_kind: str) -> dict[str, Any]:
    return {
        "event_id": f"sample-{event_kind}-000001",
        "event_kind": event_kind,
        "scheduler_event_index": 1,
        "event_time_key": 3.0,
        "node_proper_time": {"S1": 3.0, "K2": 3.0},
        "source_step_index": 3,
        "lane_id": "D2.3-P-self-rearming-cw",
        "control_lane": "positive",
        "direction": "cw",
        "mode": "closed_loop",
        "declared_route_id": "d2_3_cw_closed_loop",
        "canonical_route_step": 0,
        "source_pole": None,
        "target_pole": None,
        "channel_id": None,
        "packet_id": None,
        "parent_packet_id": None,
        "amount": None,
        "trigger_policy": None,
        "trigger_value": None,
        "trigger_threshold": None,
        "budget_before": 1.0,
        "budget_after": 1.0,
        "in_flight_packet_budget": 0.006,
        "node_budget": 0.994,
        "total_budget": 1.0,
        "source_artifact": "d2_3_self_rearming_packets_timeseries/sample.jsonl",
        "source_record_ref": {"line": 4, "step_index": 3},
        "inferred_fields": ["event_id", "event_time_key", "node_proper_time"],
        "inference_notes": {
            "event_id": "Synthetic validation sample.",
            "event_time_key": "Derived from D2.3 source step index for E1.1 validation.",
            "node_proper_time": "Set equal to event_time_key for E1.1 validation only.",
        },
    }


def _sample_records() -> list[dict[str, Any]]:
    departure = _sample_base("packet_departure")
    departure.update(
        {
            "source_pole": "S1",
            "target_pole": "K2",
            "channel_id": "S1_to_K2",
            "packet_id": "p000001",
            "amount": 0.006,
        }
    )

    arrival = _sample_base("packet_arrival")
    arrival.update(
        {
            "source_pole": "S1",
            "target_pole": "K2",
            "channel_id": "S1_to_K2",
            "packet_id": "p000001",
            "amount": 0.006,
        }
    )

    trigger = _sample_base("state_trigger")
    trigger.update(
        {
            "source_pole": "K2",
            "channel_id": "K2_to_S2",
            "trigger_policy": "source_pole_surplus_threshold",
            "trigger_value": 0.006,
            "trigger_threshold": 0.003,
        }
    )

    rearm = _sample_base("self_rearm")
    rearm.update(
        {
            "source_pole": "S1",
            "channel_id": "S1_to_K2",
            "packet_id": "p000046",
            "parent_packet_id": "p000045",
            "trigger_policy": "source_pole_surplus_threshold",
            "trigger_value": 0.006,
            "trigger_threshold": 0.003,
        }
    )

    cycle = _sample_base("cycle_complete")
    cycle.update(
        {
            "packet_id": "p000044",
            "canonical_route_step": 3,
        }
    )

    blocked = _sample_base("control_blocked")
    blocked.update(
        {
            "control_lane": "broken_return",
            "mode": "broken_return",
            "source_record_ref": {"lane_id": "D2.3-C-broken-return"},
        }
    )

    return [departure, arrival, trigger, rearm, cycle, blocked]


def _matches_type(value: Any, type_spec: str, event_kinds: Sequence[str]) -> bool:
    if type_spec == "string":
        return isinstance(value, str)
    if type_spec == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_spec == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_spec == "object[string, number]":
        return isinstance(value, dict) and all(
            isinstance(key, str)
            and isinstance(item, (int, float))
            and not isinstance(item, bool)
            for key, item in value.items()
        )
    if type_spec == "object[string, string]":
        return isinstance(value, dict) and all(
            isinstance(key, str) and isinstance(item, str)
            for key, item in value.items()
        )
    if type_spec == "object":
        return isinstance(value, dict)
    if type_spec == "array[string]":
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    if type_spec == "string|null":
        return value is None or isinstance(value, str)
    if type_spec == "number|null":
        return value is None or (
            isinstance(value, (int, float)) and not isinstance(value, bool)
        )
    if type_spec == "enum[event_kinds]":
        return isinstance(value, str) and value in event_kinds
    return False


def _validate_record(
    record: Mapping[str, Any], schema: Mapping[str, Any]
) -> list[str]:
    errors: list[str] = []
    required_fields = schema["ledger_record_required_fields"]
    field_types = schema["ledger_record_field_types"]
    event_kinds = schema["event_kinds"]
    for field_name in required_fields:
        if field_name not in record:
            errors.append(f"missing required field {field_name!r}")
            continue
        if not _matches_type(record[field_name], field_types[field_name], event_kinds):
            errors.append(
                f"field {field_name!r} does not match type {field_types[field_name]!r}"
            )

    event_kind = record.get("event_kind")
    contracts = schema["event_kind_contracts"]
    if event_kind in contracts:
        for field_name in contracts[event_kind]["non_null_fields"]:
            if record.get(field_name) is None:
                errors.append(
                    f"event kind {event_kind!r} requires non-null field {field_name!r}"
                )
    else:
        errors.append(f"unknown event kind {event_kind!r}")

    return errors


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E1.1 Event-Ledger Schema Validation",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Schema: `{result['schema']}`",
        "",
        f"Sample record count: `{result['sample_record_count']}`",
        "",
        "Validated event kinds:",
        "",
    ]
    lines.extend(f"- `{kind}`" for kind in result["validated_event_kinds"])
    lines.extend(
        [
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
            "Errors:",
            "",
        ]
    )
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    records = _sample_records()
    errors: list[str] = []
    for record in records:
        errors.extend(
            f"{record['event_kind']}: {error}"
            for error in _validate_record(record, schema)
        )
    validated_event_kinds = sorted({record["event_kind"] for record in records})
    missing_event_kinds = sorted(set(schema["event_kinds"]) - set(validated_event_kinds))
    errors.extend(f"missing sample for event kind {kind!r}" for kind in missing_event_kinds)

    result = {
        "schema": "n03_e1_event_ledger_schema_validation_v1",
        "branch": "E1.1",
        "command": COMMAND,
        "status": "passed" if not errors else "failed",
        "validated_schema": str(SCHEMA_PATH.relative_to(EXPERIMENT_ROOT)),
        "sample_record_count": len(records),
        "validated_event_kinds": validated_event_kinds,
        "errors": errors,
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": False,
            "adapter_only": True,
            "movement_claim_allowed": False,
        },
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "sample_record_count": result["sample_record_count"],
                "validated_event_kinds": result["validated_event_kinds"],
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
