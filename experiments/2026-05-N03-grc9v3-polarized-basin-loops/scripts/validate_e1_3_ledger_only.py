#!/usr/bin/env python3
"""Validate E1 D2.3 claims from converted LGRC-style ledgers only.

E1.3 reads the E1.2 JSONL ledgers and validates packet lineage, route order,
self-rearm causality, controls, and direction symmetry without reading the
original D2.3 time-series rows.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from loop_observables import load_json, write_json  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
E1_SUMMARY_PATH = EXPERIMENT_ROOT / "outputs" / "e1_d2_3_lgrc_event_ledger_summary.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e1_ledger_only_validation.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e1_ledger_only_validation.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/validate_e1_3_ledger_only.py"
)

BUDGET_TOLERANCE = 1e-9
N_CYCLES_MIN = 3
ROUTES = {
    "d2_3_cw_closed_loop": (
        "S1_to_K2",
        "K2_to_S2",
        "S2_to_K1",
        "K1_to_S1",
    ),
    "d2_3_ccw_closed_loop": (
        "S1_to_K1_rev",
        "K1_to_S2_rev",
        "S2_to_K2_rev",
        "K2_to_S1_rev",
    ),
}
KNOWN_CHANNELS = sorted({channel for route in ROUTES.values() for channel in route})


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _amount_equal(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is right
    return abs(float(left) - float(right)) <= BUDGET_TOLERANCE


def _route_for(record: Mapping[str, Any]) -> tuple[str, ...]:
    return ROUTES.get(str(record["declared_route_id"]), ())


def _computed_cycle_count(records: Sequence[Mapping[str, Any]]) -> int:
    route = _route_for(records[0]) if records else ()
    if not route:
        return 0
    index = 0
    cycles = 0
    for record in records:
        if record["event_kind"] != "packet_arrival":
            continue
        channel_id = record.get("channel_id")
        if channel_id == route[index]:
            index += 1
            if index == len(route):
                cycles += 1
                index = 0
        else:
            index = 1 if channel_id == route[0] else 0
    return cycles


def _validate_lane(
    lane_summary: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    lane_id = str(lane_summary["lane_id"])
    event_ids = [str(record["event_id"]) for record in records]
    duplicate_event_ids = sorted(
        event_id for event_id, count in Counter(event_ids).items() if count > 1
    )
    if duplicate_event_ids:
        errors.append(f"{lane_id}: duplicate event ids {duplicate_event_ids}")

    scheduler_indices = [int(record["scheduler_event_index"]) for record in records]
    if scheduler_indices != sorted(scheduler_indices):
        errors.append(f"{lane_id}: scheduler_event_index is not monotone")
    if scheduler_indices and scheduler_indices != list(range(len(scheduler_indices))):
        errors.append(f"{lane_id}: scheduler_event_index is not contiguous")

    event_times = [float(record["event_time_key"]) for record in records]
    if event_times != sorted(event_times):
        errors.append(f"{lane_id}: event_time_key is not monotone")

    departures: dict[str, Mapping[str, Any]] = {}
    arrivals: dict[str, Mapping[str, Any]] = {}
    for record in records:
        channel_id = record.get("channel_id")
        if channel_id is not None and channel_id not in KNOWN_CHANNELS:
            errors.append(f"{lane_id}: unknown channel {channel_id!r}")
        if abs(
            (float(record["node_budget"]) + float(record["in_flight_packet_budget"]))
            - float(record["total_budget"])
        ) > BUDGET_TOLERANCE:
            errors.append(f"{lane_id}: node+packet budget does not equal total")
        if abs(float(record["total_budget"]) - 1.0) > BUDGET_TOLERANCE:
            errors.append(f"{lane_id}: total budget is not conserved")

        packet_id = record.get("packet_id")
        if record["event_kind"] == "packet_departure" and packet_id is not None:
            if packet_id in departures:
                errors.append(f"{lane_id}: duplicate packet departure {packet_id}")
            departures[str(packet_id)] = record
        if record["event_kind"] == "packet_arrival" and packet_id is not None:
            if packet_id in arrivals:
                errors.append(f"{lane_id}: duplicate packet arrival {packet_id}")
            arrivals[str(packet_id)] = record

    for packet_id, arrival in arrivals.items():
        departure = departures.get(packet_id)
        if departure is None:
            errors.append(f"{lane_id}: arrival without departure for {packet_id}")
            continue
        if not _amount_equal(arrival.get("amount"), departure.get("amount")):
            errors.append(f"{lane_id}: amount mismatch for {packet_id}")
        if int(arrival["scheduler_event_index"]) <= int(departure["scheduler_event_index"]):
            errors.append(f"{lane_id}: arrival not after departure for {packet_id}")
        if float(arrival["event_time_key"]) < float(departure["event_time_key"]):
            errors.append(f"{lane_id}: arrival event_time before departure for {packet_id}")

    unresolved_parent_ids: list[str] = []
    for record in records:
        parent_packet_id = record.get("parent_packet_id")
        if parent_packet_id is None:
            continue
        if str(parent_packet_id) not in departures:
            unresolved_parent_ids.append(str(parent_packet_id))
    if unresolved_parent_ids:
        errors.append(
            f"{lane_id}: unresolved parent packet ids {sorted(set(unresolved_parent_ids))}"
        )

    route = _route_for(records[0]) if records else ()
    cycle_records = [record for record in records if record["event_kind"] == "cycle_complete"]
    self_rearm_records = [record for record in records if record["event_kind"] == "self_rearm"]
    state_trigger_records = [record for record in records if record["event_kind"] == "state_trigger"]
    computed_cycles = _computed_cycle_count(records)
    if len(cycle_records) != computed_cycles:
        errors.append(
            f"{lane_id}: cycle_complete count {len(cycle_records)} != computed cycles {computed_cycles}"
        )
    if route:
        final_channel = route[-1]
        first_channel = route[0]
        for record in cycle_records:
            packet_id = record.get("packet_id")
            arrival = arrivals.get(str(packet_id))
            if arrival is None:
                errors.append(f"{lane_id}: cycle_complete without final arrival {packet_id}")
            elif arrival.get("channel_id") != final_channel:
                errors.append(f"{lane_id}: cycle_complete packet did not arrive on final channel")
        for record in self_rearm_records:
            parent_packet_id = str(record.get("parent_packet_id"))
            child_packet_id = str(record.get("packet_id"))
            parent_arrival = arrivals.get(parent_packet_id)
            child_departure = departures.get(child_packet_id)
            if parent_arrival is None:
                errors.append(f"{lane_id}: self_rearm parent did not arrive")
                continue
            if parent_arrival.get("channel_id") != final_channel:
                errors.append(f"{lane_id}: self_rearm parent did not arrive on final channel")
            if child_departure is None:
                errors.append(f"{lane_id}: self_rearm child did not depart")
                continue
            if child_departure.get("channel_id") != first_channel:
                errors.append(f"{lane_id}: self_rearm child did not depart on first channel")
            if int(child_departure["scheduler_event_index"]) >= int(record["scheduler_event_index"]):
                errors.append(f"{lane_id}: self_rearm label precedes child departure check failed")
            if int(parent_arrival["scheduler_event_index"]) >= int(record["scheduler_event_index"]):
                errors.append(f"{lane_id}: self_rearm label precedes parent arrival check failed")

    for trigger in state_trigger_records:
        packet_id = trigger.get("packet_id")
        if packet_id is None:
            continue
        departure = departures.get(str(packet_id))
        if departure is None:
            errors.append(f"{lane_id}: state_trigger did not produce packet departure")
            continue
        if trigger.get("channel_id") != departure.get("channel_id"):
            errors.append(f"{lane_id}: state_trigger/departure channel mismatch")
        if trigger.get("parent_packet_id") != departure.get("parent_packet_id"):
            errors.append(f"{lane_id}: state_trigger/departure parent mismatch")

    control_blocked_count = sum(
        1 for record in records if record["event_kind"] == "control_blocked"
    )
    ledger_positive = (
        len(cycle_records) >= N_CYCLES_MIN
        and len(self_rearm_records) >= max(1, N_CYCLES_MIN - 1)
        and control_blocked_count == 0
        and not errors
    )
    expected_positive = bool(lane_summary["expected_positive"])
    if ledger_positive is not expected_positive:
        errors.append(
            f"{lane_id}: ledger_positive={ledger_positive} expected={expected_positive}"
        )
    if not expected_positive and control_blocked_count < 1:
        errors.append(f"{lane_id}: negative/control lane lacks control_blocked event")

    event_counts = Counter(str(record["event_kind"]) for record in records)
    return {
        "lane_id": lane_id,
        "ledger_path": lane_summary["ledger_path"],
        "expected_positive": expected_positive,
        "ledger_positive": ledger_positive,
        "event_count": len(records),
        "packet_departure_count": event_counts["packet_departure"],
        "packet_arrival_count": event_counts["packet_arrival"],
        "state_trigger_count": event_counts["state_trigger"],
        "self_rearm_count": len(self_rearm_records),
        "cycle_complete_count": len(cycle_records),
        "computed_cycle_count": computed_cycles,
        "control_blocked_count": control_blocked_count,
        "unarrived_packet_count": len(set(departures) - set(arrivals)),
        "errors": errors,
    }


def _symmetry_audit(lane_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_id = {str(result["lane_id"]): result for result in lane_results}
    cw = by_id.get("D2.3-P-self-rearming-cw")
    ccw = by_id.get("D2.3-R-self-rearming-ccw")
    if cw is None or ccw is None:
        return {"passed": False, "reason": "missing cw or ccw positive lane"}
    comparable_fields = [
        "event_count",
        "packet_departure_count",
        "packet_arrival_count",
        "state_trigger_count",
        "self_rearm_count",
        "cycle_complete_count",
        "computed_cycle_count",
        "unarrived_packet_count",
    ]
    deltas = {
        field: int(cw[field]) - int(ccw[field])
        for field in comparable_fields
    }
    return {
        "passed": all(value == 0 for value in deltas.values())
        and bool(cw["ledger_positive"])
        and bool(ccw["ledger_positive"]),
        "cw_lane": cw["lane_id"],
        "ccw_lane": ccw["lane_id"],
        "deltas": deltas,
    }


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E1.3 Ledger-Only Validation",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Validated lanes: `{result['validated_lane_count']}`",
        f"Positive lanes from ledger: `{', '.join(result['ledger_positive_lanes'])}`",
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
        "## Checks",
        "",
    ]
    for check_name, passed in result["checks"].items():
        lines.append(f"- `{check_name}`: `{passed}`")
    lines.extend(["", "## Lane Summary", ""])
    lines.extend(
        [
            "| Lane | Expected | Ledger Positive | Cycles | Self-Rearms | Departures | Arrivals | Blocked | Errors |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for lane in result["lane_results"]:
        lines.append(
            "| {lane_id} | {expected} | {positive} | {cycles} | {rearms} | {departures} | {arrivals} | {blocked} | {errors} |".format(
                lane_id=lane["lane_id"],
                expected=lane["expected_positive"],
                positive=lane["ledger_positive"],
                cycles=lane["cycle_complete_count"],
                rearms=lane["self_rearm_count"],
                departures=lane["packet_departure_count"],
                arrivals=lane["packet_arrival_count"],
                blocked=lane["control_blocked_count"],
                errors=len(lane["errors"]),
            )
        )
    lines.extend(["", "## Direction Symmetry", "", "```json"])
    lines.append(json.dumps(result["symmetry_audit"], sort_keys=True))
    lines.extend(["```", "", "## Errors", ""])
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    e1_summary = load_json(E1_SUMMARY_PATH)
    lane_results: list[dict[str, Any]] = []
    errors: list[str] = []
    for lane_summary in e1_summary["lane_summaries"]:
        ledger_path = EXPERIMENT_ROOT / str(lane_summary["ledger_path"])
        records = _load_jsonl(ledger_path)
        lane_result = _validate_lane(lane_summary, records)
        lane_results.append(lane_result)
        errors.extend(lane_result["errors"])

    symmetry = _symmetry_audit(lane_results)
    if not symmetry["passed"]:
        errors.append("clockwise/counter-clockwise symmetry failed")

    checks = {
        "packet_ids_unique": not any(
            "duplicate packet departure" in error for error in errors
        ),
        "parent_packet_ids_resolve": not any(
            "unresolved parent packet ids" in error for error in errors
        ),
        "no_unknown_channels": not any("unknown channel" in error for error in errors),
        "departure_arrival_amounts_preserved": not any(
            "amount mismatch" in error for error in errors
        ),
        "node_plus_packet_budget_reconstructable": not any(
            "budget" in error for error in errors
        ),
        "cycles_match_canonical_route": not any(
            "cycle_complete" in error for error in errors
        ),
        "self_rearm_after_returned_arrival": not any(
            "self_rearm" in error for error in errors
        ),
        "controls_remain_negative": not any(
            "lacks control_blocked" in error or "ledger_positive=True expected=False" in error
            for error in errors
        ),
        "clockwise_counter_clockwise_symmetry": bool(symmetry["passed"]),
    }
    ledger_positive_lanes = [
        lane["lane_id"] for lane in lane_results if lane["ledger_positive"]
    ]
    result = {
        "schema": "n03_e1_ledger_only_validation_v1",
        "branch": "E1.3",
        "command": COMMAND,
        "status": "passed" if not errors and all(checks.values()) else "failed",
        "source_summary": str(E1_SUMMARY_PATH.relative_to(EXPERIMENT_ROOT)),
        "validated_lane_count": len(lane_results),
        "ledger_positive_lanes": ledger_positive_lanes,
        "checks": checks,
        "symmetry_audit": symmetry,
        "lane_results": lane_results,
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": False,
            "adapter_only": True,
            "movement_claim_allowed": False,
        },
        "errors": errors,
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "validated_lane_count": result["validated_lane_count"],
                "ledger_positive_lanes": ledger_positive_lanes,
                "errors": len(errors),
                "symmetry_passed": symmetry["passed"],
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
