#!/usr/bin/env python3
"""Run E2.1 scheduled packet route replay through native LGRC9V3.

E2.1 replays the declared D2.3 clockwise packet route by scheduling a bounded
sequence of native LGRC9V3 packet departures.  The experiment controls the
schedule; LGRC9V3 executes the packet departure/arrival events.  This validates
native route-level packet execution, not native trigger or self-rearm autonomy.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from pygrc.models import (
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LAPSE_POLICY_UNIT,
    LGRC9V3,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
)

import run_e2_0_runtime_feasibility as e2_0
from loop_observables import write_json


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_1_scheduled_packet_route_replay.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e2_1_scheduled_packet_route_replay.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_e2_1_scheduled_packet_route_replay.py"
)

ROUTE_ID = "d2_3_cw_closed_loop"
EVENT_SPACING = 2.0


def _load_or_write_route_manifest() -> dict[str, Any]:
    if e2_0.ROUTE_MANIFEST_PATH.exists():
        return json.loads(e2_0.ROUTE_MANIFEST_PATH.read_text(encoding="utf-8"))
    route_manifest = e2_0._build_route_manifest()
    write_json(e2_0.ROUTE_MANIFEST_PATH, route_manifest)
    return route_manifest


def _route_hops(route_manifest: Mapping[str, Any], route_id: str) -> list[dict[str, Any]]:
    channels = route_manifest["channels"]
    route = route_manifest["declared_routes"][route_id]
    hops: list[dict[str, Any]] = []
    route_step_index = 0
    for channel_id in route:
        channel = channels[channel_id]
        for hop_index, hop in enumerate(channel["route_hops"]):
            hops.append(
                {
                    "route_step_index": route_step_index,
                    "channel_id": channel_id,
                    "hop_index": hop_index,
                    "source_node_id": int(hop["source_node_id"]),
                    "target_node_id": int(hop["target_node_id"]),
                    "edge_id": int(hop["edge_id"]),
                }
            )
            route_step_index += 1
    return hops


def _hop_lookup(hops: list[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {int(hop["edge_id"]): hop for hop in hops}


def _event_summary(result: Any, hops_by_edge_id: Mapping[int, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in result.events:
        payload = event.payload
        packet_record = payload.get("packet_record")
        processed_event = payload.get("processed_event")
        route_fields: dict[str, Any] = {}
        if isinstance(packet_record, Mapping):
            hop = hops_by_edge_id.get(int(packet_record["edge_id"]))
            if hop is not None:
                route_fields = {
                    "route_step_index": hop["route_step_index"],
                    "channel_id": hop["channel_id"],
                    "hop_index": hop["hop_index"],
                }
        rows.append(
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "processed_event": processed_event,
                "packet_record": packet_record,
                "budget_error": payload.get("budget_error"),
                "proper_time_update": payload.get("proper_time_update"),
                "topology_mutated": payload.get("topology_mutated"),
                "route_fields": route_fields,
            }
        )
    return rows


def _runtime_steps(results: list[Any], hops_by_edge_id: Mapping[int, Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "processed_event_kind": result.bookkeeping.get("processed_event_kind"),
            "scheduler_event_index": result.bookkeeping.get("scheduler_event_index"),
            "event_time_key": result.bookkeeping.get("event_time_key"),
            "events": _event_summary(result, hops_by_edge_id),
        }
        for result in results
    ]


def _packet_route_records(
    runtime_steps: list[Mapping[str, Any]],
    event_kind: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for step in runtime_steps:
        for event in step["events"]:
            if event["kind"] != event_kind:
                continue
            packet_record = event["packet_record"]
            route_fields = event["route_fields"]
            if not isinstance(packet_record, Mapping) or not route_fields:
                continue
            records.append(
                {
                    "event_kind": event_kind,
                    "scheduler_event_index": step["scheduler_event_index"],
                    "event_time_key": step["event_time_key"],
                    "packet_id": packet_record["packet_id"],
                    "channel_id": route_fields["channel_id"],
                    "hop_index": route_fields["hop_index"],
                    "route_step_index": route_fields["route_step_index"],
                    "source_node_id": packet_record["source_node_id"],
                    "target_node_id": packet_record["target_node_id"],
                    "edge_id": packet_record["edge_id"],
                    "amount": packet_record["amount"],
                }
            )
    return records


def _sequence(records: list[Mapping[str, Any]]) -> list[tuple[str, int]]:
    return [
        (str(record["channel_id"]), int(record["hop_index"]))
        for record in sorted(records, key=lambda item: int(item["route_step_index"]))
    ]


def _records_by_packet_id(records: list[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    return {str(record["packet_id"]): record for record in records}


def _pairing_audit(
    departure_records: list[Mapping[str, Any]],
    arrival_records: list[Mapping[str, Any]],
) -> dict[str, Any]:
    departures = _records_by_packet_id(departure_records)
    arrivals = _records_by_packet_id(arrival_records)
    matched_packet_ids = sorted(set(departures) & set(arrivals))
    unmatched_departure_packet_ids = sorted(set(departures) - set(arrivals))
    unmatched_arrival_packet_ids = sorted(set(arrivals) - set(departures))
    mismatch_packet_ids: list[str] = []
    for packet_id in matched_packet_ids:
        departure = departures[packet_id]
        arrival = arrivals[packet_id]
        for field in (
            "amount",
            "channel_id",
            "route_step_index",
            "hop_index",
            "edge_id",
            "source_node_id",
            "target_node_id",
        ):
            if departure[field] != arrival[field]:
                mismatch_packet_ids.append(packet_id)
                break
    return {
        "matched_packet_count": len(matched_packet_ids),
        "unmatched_departure_packet_ids": unmatched_departure_packet_ids,
        "unmatched_arrival_packet_ids": unmatched_arrival_packet_ids,
        "mismatch_packet_ids": mismatch_packet_ids,
        "each_departure_has_exactly_one_matching_arrival": (
            len(matched_packet_ids) == len(departure_records)
            and not unmatched_departure_packet_ids
            and not unmatched_arrival_packet_ids
            and not mismatch_packet_ids
        ),
    }


def _packet_event_checks(
    runtime_steps: list[Mapping[str, Any]],
) -> dict[str, Any]:
    event_time_keys = [
        float(step["event_time_key"])
        for step in runtime_steps
        if step["event_time_key"] is not None
    ]
    packet_budget_errors: list[float] = []
    topology_mutated_flags: list[bool] = []
    proper_time_nodes: set[int] = set()
    packet_events_with_route_fields = 0
    packet_event_count = 0
    for step in runtime_steps:
        for event in step["events"]:
            if event["kind"] not in (
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            ):
                continue
            packet_event_count += 1
            if event["route_fields"]:
                packet_events_with_route_fields += 1
            if event["budget_error"] is not None:
                packet_budget_errors.append(abs(float(event["budget_error"])))
            topology_mutated_flags.append(bool(event["topology_mutated"]))
            proper_time_update = event["proper_time_update"]
            if isinstance(proper_time_update, Mapping):
                proper_time_nodes.add(int(proper_time_update["node_id"]))
    return {
        "event_time_keys": event_time_keys,
        "event_time_keys_monotonic": event_time_keys == sorted(event_time_keys),
        "packet_event_count": packet_event_count,
        "packet_events_with_route_fields": packet_events_with_route_fields,
        "all_packet_events_mapped_to_route": packet_events_with_route_fields == packet_event_count,
        "all_packet_events_have_budget_error": len(packet_budget_errors) == packet_event_count,
        "max_packet_event_budget_error": max(packet_budget_errors, default=0.0),
        "packet_topology_mutation_count": sum(1 for flag in topology_mutated_flags if flag),
        "proper_time_nodes_recorded_in_packet_events": sorted(proper_time_nodes),
    }


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    audit = result["audit"]
    lines = [
        "# E2.1 Scheduled Packet Route Replay",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "Boundary:",
        "",
        "```text",
        "native_grc9v3_evidence = false",
        "native_lgrc9v3_execution = true",
        "adapter_only = false",
        "movement_claim_allowed = false",
        "```",
        "",
        "Claim ceiling:",
        "",
        "```text",
        "native_packet_execution = true",
        "native_autonomous_trigger = false",
        "native_self_rearm = false",
        "scheduled_route_replay = true",
        "loop_claim_allowed = false",
        "```",
        "",
        "## Audit",
        "",
    ]
    for key, value in audit.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Expected Route",
            "",
            "```text",
            " -> ".join(result["expected_channel_sequence"]),
            "```",
            "",
            "## Runtime Route Records",
            "",
            "| kind | T_e | scheduler | channel | hop | edge | source | target |",
            "|---|---:|---:|---|---:|---:|---:|---:|",
        ]
    )
    combined = sorted(
        result["departure_records"] + result["arrival_records"],
        key=lambda item: (float(item["event_time_key"]), int(item["scheduler_event_index"])),
    )
    for record in combined:
        lines.append(
            "| {kind} | {time} | {scheduler} | {channel} | {hop} | {edge} | {source} | {target} |".format(
                kind=record["event_kind"],
                time=record["event_time_key"],
                scheduler=record["scheduler_event_index"],
                channel=record["channel_id"],
                hop=record["hop_index"],
                edge=record["edge_id"],
                source=record["source_node_id"],
                target=record["target_node_id"],
            )
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    route_manifest = _load_or_write_route_manifest()
    hops = _route_hops(route_manifest, ROUTE_ID)
    hops_by_edge_id = _hop_lookup(hops)
    state = e2_0._build_ring_state()
    initial_signature = e2_0._topology_signature(state)
    initial_node_total = e2_0._node_total(state)
    model = LGRC9V3.from_state(
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
    scheduled_packets: list[dict[str, Any]] = []
    for packet_index, hop in enumerate(hops):
        departure_event_time_key = float(packet_index) * EVENT_SPACING
        scheduler_event_index = (packet_index * 2) + 1
        model.schedule_packet_departure(
            source_node_id=int(hop["source_node_id"]),
            target_node_id=int(hop["target_node_id"]),
            edge_id=int(hop["edge_id"]),
            amount=e2_0.PACKET_AMOUNT,
            departure_event_time_key=departure_event_time_key,
            scheduler_event_index=scheduler_event_index,
            packet_index=packet_index,
        )
        scheduled_packets.append(
            {
                **hop,
                "amount": e2_0.PACKET_AMOUNT,
                "departure_event_time_key": departure_event_time_key,
                "scheduler_event_index": scheduler_event_index,
            }
        )

    results = model.run_event_queue(max_events=(len(hops) * 2) + 4)
    final_state = model.get_state()
    final_signature = e2_0._topology_signature(final_state.base_state)
    packet_ledger = final_state.packet_ledger
    assert packet_ledger is not None
    runtime_steps = _runtime_steps(results, hops_by_edge_id)
    departure_records = _packet_route_records(
        runtime_steps,
        LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
    )
    arrival_records = _packet_route_records(
        runtime_steps,
        LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    )
    expected_sequence = [
        (str(hop["channel_id"]), int(hop["hop_index"]))
        for hop in sorted(hops, key=lambda item: int(item["route_step_index"]))
    ]
    departure_sequence = _sequence(departure_records)
    arrival_sequence = _sequence(arrival_records)
    pairing_audit = _pairing_audit(departure_records, arrival_records)
    packet_event_checks = _packet_event_checks(runtime_steps)
    node_total = e2_0._node_total(final_state.base_state)
    in_flight_total = float(packet_ledger.in_flight_packet_total)
    reconstructed_total = node_total + in_flight_total
    packet_ids = [
        str(record["packet_id"])
        for record in departure_records
    ]
    processed_kinds = [
        step["processed_event_kind"]
        for step in runtime_steps
        if step["processed_event_kind"] is not None
    ]
    expected_route_steps = list(range(len(hops)))
    departure_route_steps = [
        int(record["route_step_index"])
        for record in sorted(departure_records, key=lambda item: int(item["route_step_index"]))
    ]
    arrival_route_steps = [
        int(record["route_step_index"])
        for record in sorted(arrival_records, key=lambda item: int(item["route_step_index"]))
    ]
    touched_route_nodes = sorted(
        {
            int(hop["source_node_id"])
            for hop in hops
        }
        | {
            int(hop["target_node_id"])
            for hop in hops
        }
    )
    final_proper_time_nodes = sorted(int(node_id) for node_id in final_state.node_proper_time)
    audit = {
        "route_id": ROUTE_ID,
        "scheduled_packet_count": len(scheduled_packets),
        "runtime_step_count": len(results),
        "departure_count": len(departure_records),
        "arrival_count": len(arrival_records),
        "expected_hop_count": len(hops),
        "expected_route_steps": expected_route_steps,
        "departure_route_steps": departure_route_steps,
        "arrival_route_steps": arrival_route_steps,
        "departure_sequence_matches_route": departure_sequence == expected_sequence,
        "arrival_sequence_matches_route": arrival_sequence == expected_sequence,
        "departure_route_steps_match": departure_route_steps == expected_route_steps,
        "arrival_route_steps_match": arrival_route_steps == expected_route_steps,
        "each_departure_has_exactly_one_matching_arrival": pairing_audit[
            "each_departure_has_exactly_one_matching_arrival"
        ],
        "matched_packet_count": pairing_audit["matched_packet_count"],
        "unmatched_departure_packet_ids": pairing_audit["unmatched_departure_packet_ids"],
        "unmatched_arrival_packet_ids": pairing_audit["unmatched_arrival_packet_ids"],
        "mismatch_packet_ids": pairing_audit["mismatch_packet_ids"],
        "packet_ids_unique": len(packet_ids) == len(set(packet_ids)),
        "processed_only_packet_events": all(
            kind
            in (
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            )
            for kind in processed_kinds
        ),
        "all_packet_events_mapped_to_route": packet_event_checks[
            "all_packet_events_mapped_to_route"
        ],
        "all_packet_events_have_budget_error": packet_event_checks[
            "all_packet_events_have_budget_error"
        ],
        "max_packet_event_budget_error": packet_event_checks[
            "max_packet_event_budget_error"
        ],
        "event_time_keys": packet_event_checks["event_time_keys"],
        "event_time_keys_monotonic": packet_event_checks["event_time_keys_monotonic"],
        "proper_time_nodes_recorded_in_packet_events": packet_event_checks[
            "proper_time_nodes_recorded_in_packet_events"
        ],
        "touched_route_nodes": touched_route_nodes,
        "all_touched_route_nodes_have_proper_time": set(touched_route_nodes).issubset(
            set(final_proper_time_nodes)
        ),
        "packet_topology_mutation_count": packet_event_checks["packet_topology_mutation_count"],
        "node_plus_packet_budget": reconstructed_total,
        "budget_error": abs(reconstructed_total - initial_node_total),
        "in_flight_packet_total": in_flight_total,
        "topology_unchanged": initial_signature == final_signature,
        "queue_empty": len(packet_ledger.event_queue_records) == 0,
        "native_trigger_claim_made": False,
        "native_self_rearm_claim_made": False,
        "single_packet_continuity_claim_made": False,
        "loop_claim_made": False,
    }
    status = (
        "passed"
        if audit["departure_count"] == audit["expected_hop_count"]
        and audit["arrival_count"] == audit["expected_hop_count"]
        and audit["departure_sequence_matches_route"]
        and audit["arrival_sequence_matches_route"]
        and audit["departure_route_steps_match"]
        and audit["arrival_route_steps_match"]
        and audit["each_departure_has_exactly_one_matching_arrival"]
        and audit["packet_ids_unique"]
        and audit["processed_only_packet_events"]
        and audit["all_packet_events_mapped_to_route"]
        and audit["all_packet_events_have_budget_error"]
        and audit["max_packet_event_budget_error"] <= 1e-9
        and audit["event_time_keys_monotonic"]
        and audit["all_touched_route_nodes_have_proper_time"]
        and audit["packet_topology_mutation_count"] == 0
        and audit["topology_unchanged"]
        and audit["queue_empty"]
        and audit["budget_error"] <= 1e-9
        else "failed"
    )
    result = {
        "schema": "n03_e2_1_lgrc9v3_scheduled_packet_route_replay_v1",
        "branch": "E2.1",
        "command": COMMAND,
        "status": status,
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": True,
            "adapter_only": False,
            "movement_claim_allowed": False,
        },
        "claim_ceiling": {
            "native_packet_execution": True,
            "native_autonomous_trigger": False,
            "native_self_rearm": False,
            "scheduled_route_replay": True,
            "loop_claim_allowed": False,
        },
        "route_manifest": str(e2_0.ROUTE_MANIFEST_PATH.relative_to(EXPERIMENT_ROOT)),
        "route_id": ROUTE_ID,
        "expected_channel_sequence": route_manifest["declared_routes"][ROUTE_ID],
        "expected_hop_sequence": [
            {
                "channel_id": hop["channel_id"],
                "hop_index": hop["hop_index"],
                "edge_id": hop["edge_id"],
                "source_node_id": hop["source_node_id"],
                "target_node_id": hop["target_node_id"],
            }
            for hop in hops
        ],
        "scheduled_packets": scheduled_packets,
        "departure_records": departure_records,
        "arrival_records": arrival_records,
        "initial_topology": initial_signature,
        "final_topology": final_signature,
        "runtime_steps": runtime_steps,
        "audit": audit,
        "non_native_assumptions": [
            "The pole/channel route manifest is experiment-local.",
            "Each route hop is scheduled explicitly by the experiment.",
            "The replay is channel-hop order evidence, not a native surplus trigger.",
            "No self-rearm, autonomous producer, or loop claim is made in E2.1.",
        ],
        "interpretation": (
            "Existing LGRC9V3 runtime methods can replay the declared D2.3 "
            "clockwise route as a scheduled sequence of packet departure and "
            "arrival events with conserved node-plus-packet budget and unchanged "
            "topology. This establishes native scheduled route-level packet "
            "execution only; native trigger production and self-rearm semantics "
            "remain unclaimed."
        ),
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": status,
                "scheduled_packet_count": audit["scheduled_packet_count"],
                "runtime_step_count": audit["runtime_step_count"],
                "departure_sequence_matches_route": audit["departure_sequence_matches_route"],
                "arrival_sequence_matches_route": audit["arrival_sequence_matches_route"],
                "budget_error": audit["budget_error"],
                "topology_unchanged": audit["topology_unchanged"],
            },
            sort_keys=True,
        )
    )
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
