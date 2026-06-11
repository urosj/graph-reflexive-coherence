#!/usr/bin/env python3
"""Inventory LGRC9V3 surfaces relevant to N03 D2.3 alignment.

E1.0 is experiment-local.  It inspects existing LGRC9V3 code surfaces and
records whether D2.3 can be translated into LGRC-style event/packet artifacts.
It does not modify `src/*`.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
import inspect
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from loop_observables import write_json  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e1_lgrc9v3_surface_inventory.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e1_lgrc9v3_surface_inventory.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_e1_0_lgrc9v3_surface_inventory.py"
)


def _source_ref(obj: object) -> dict[str, Any]:
    path = inspect.getsourcefile(obj)
    try:
        _, lineno = inspect.getsourcelines(obj)
    except (OSError, TypeError):
        lineno = None
    if path is None:
        return {"path": None, "line": lineno}
    source_path = Path(path).resolve()
    try:
        rel_path = source_path.relative_to(REPO_ROOT)
    except ValueError:
        rel_path = source_path
    return {"path": str(rel_path), "line": lineno}


def _dataclass_fields(cls: type[Any]) -> list[str]:
    if not is_dataclass(cls):
        return []
    return [field.name for field in fields(cls)]


def _function_surface(fn: Callable[..., Any]) -> dict[str, Any]:
    return {
        "name": fn.__name__,
        "source": _source_ref(fn),
        "signature": str(inspect.signature(fn)),
    }


def _class_surface(cls: type[Any]) -> dict[str, Any]:
    return {
        "name": cls.__name__,
        "source": _source_ref(cls),
        "fields": _dataclass_fields(cls),
    }


def _contains_all(container: list[str], required: list[str]) -> bool:
    return all(item in container for item in required)


def _build_inventory() -> dict[str, Any]:
    from pygrc.models import lgrc_9_v3_packets as packets
    from pygrc.models import lgrc_9_v3_runtime as runtime
    from pygrc.models import lgrc_9_v3_runtime_state as runtime_state
    from pygrc.telemetry import lgrc9v3_contract as telemetry

    packet_record_fields = _dataclass_fields(packets.LGRC9V3PacketRecord)
    queue_event_fields = _dataclass_fields(packets.LGRC9V3PacketQueueEventRecord)
    ledger_fields = _dataclass_fields(packets.LGRC9V3PacketLedger)
    runtime_state_fields = _dataclass_fields(runtime_state.LGRC9V3RuntimeState)

    surfaces = {
        "classes": {
            "LGRC9V3PacketRecord": _class_surface(packets.LGRC9V3PacketRecord),
            "LGRC9V3PacketQueueEventRecord": _class_surface(
                packets.LGRC9V3PacketQueueEventRecord
            ),
            "LGRC9V3PacketLedger": _class_surface(packets.LGRC9V3PacketLedger),
            "LGRC9V3RuntimeState": _class_surface(runtime_state.LGRC9V3RuntimeState),
            "LGRC9V3": _class_surface(runtime.LGRC9V3),
        },
        "functions": {
            "build_lgrc9v3_packet_ledger": _function_surface(
                packets.build_lgrc9v3_packet_ledger
            ),
            "schedule_lgrc9v3_packet_departure": _function_surface(
                packets.schedule_lgrc9v3_packet_departure
            ),
            "process_lgrc9v3_packet_departure": _function_surface(
                packets.process_lgrc9v3_packet_departure
            ),
            "process_lgrc9v3_packet_arrival": _function_surface(
                packets.process_lgrc9v3_packet_arrival
            ),
            "process_lgrc9v3_next_packet_event": _function_surface(
                packets.process_lgrc9v3_next_packet_event
            ),
            "derive_lgrc9v3_packet_arrival_event_time_key": _function_surface(
                packets.derive_lgrc9v3_packet_arrival_event_time_key
            ),
            "ordered_lgrc9v3_event_queue": _function_surface(
                runtime_state.ordered_lgrc9v3_event_queue
            ),
            "restore_lgrc9v3_runtime_state_artifact": _function_surface(
                runtime_state.restore_lgrc9v3_runtime_state_artifact
            ),
            "classify_lgrc9v3_step_extension": _function_surface(
                telemetry.classify_lgrc9v3_step_extension
            ),
            "build_lgrc9v3_graph_checkpoint": _function_surface(
                telemetry.build_lgrc9v3_graph_checkpoint
            ),
        },
        "runtime_methods": {
            "LGRC9V3.schedule_packet_departure": _function_surface(
                runtime.LGRC9V3.schedule_packet_departure
            ),
            "LGRC9V3.step": _function_surface(runtime.LGRC9V3.step),
            "LGRC9V3.run_event_queue": _function_surface(
                runtime.LGRC9V3.run_event_queue
            ),
            "LGRC9V3.set_causal_flux_routes": _function_surface(
                runtime.LGRC9V3.set_causal_flux_routes
            ),
            "LGRC9V3.produce_events": _function_surface(runtime.LGRC9V3.produce_events),
            "LGRC9V3.run_autonomous": _function_surface(runtime.LGRC9V3.run_autonomous),
        },
    }

    findings = {
        "packet_departure_records_exist": _contains_all(
            queue_event_fields,
            [
                "event_kind",
                "event_time_key",
                "scheduler_event_index",
                "packet_id",
                "source_node_id",
                "target_node_id",
                "edge_id",
                "amount",
            ],
        )
        and hasattr(packets, "LGRC9V3_PACKET_EVENT_KIND_DEPARTURE"),
        "packet_arrival_records_exist": _contains_all(
            queue_event_fields,
            [
                "event_kind",
                "event_time_key",
                "scheduler_event_index",
                "packet_id",
                "source_node_id",
                "target_node_id",
                "edge_id",
                "amount",
            ],
        )
        and hasattr(packets, "LGRC9V3_PACKET_EVENT_KIND_ARRIVAL"),
        "packet_ledger_with_in_flight_amount_exists": _contains_all(
            ledger_fields,
            [
                "packet_records",
                "packet_event_records",
                "event_queue_records",
                "node_coherence_total",
                "in_flight_packet_total",
                "conserved_budget_total",
                "budget_error",
            ],
        ),
        "event_time_key_serialized": "event_time_key" in runtime_state_fields
        and "event_time_key" in queue_event_fields,
        "proper_time_serialized": _contains_all(
            runtime_state_fields,
            [
                "node_proper_time",
                "node_last_update_proper_time",
                "node_last_update_event_time_key",
            ],
        ),
        "event_time_key_distinct_from_node_proper_time": _contains_all(
            runtime_state_fields,
            ["event_time_key", "node_proper_time"],
        ),
        "budget_reconstructable": _contains_all(
            ledger_fields,
            [
                "node_coherence_total",
                "in_flight_packet_total",
                "conserved_budget_total",
            ],
        ),
        "route_or_channel_surface_exists": "causal_flux_routes" in runtime_state_fields
        and hasattr(runtime.LGRC9V3, "set_causal_flux_routes"),
        "native_state_trigger_surface_exists": False,
    }

    required_questions = [
        {
            "question": "Does LGRC9V3 already expose packet departure / arrival records?",
            "answer": "yes",
            "evidence": [
                "LGRC9V3PacketQueueEventRecord",
                "LGRC9V3_PACKET_EVENT_KIND_DEPARTURE",
                "LGRC9V3_PACKET_EVENT_KIND_ARRIVAL",
                "schedule_lgrc9v3_packet_departure",
                "process_lgrc9v3_packet_arrival",
            ],
        },
        {
            "question": "Does LGRC9V3 already expose a packet ledger with in-flight amount?",
            "answer": "yes",
            "evidence": [
                "LGRC9V3PacketLedger.in_flight_packet_total",
                "LGRC9V3PacketLedger.packet_records",
                "LGRC9V3PacketLedger.event_queue_records",
            ],
        },
        {
            "question": "Does LGRC9V3 serialize event-time key, proper time, and node update timing?",
            "answer": "yes",
            "evidence": [
                "LGRC9V3RuntimeState.event_time_key",
                "LGRC9V3RuntimeState.node_proper_time",
                "LGRC9V3RuntimeState.node_last_update_proper_time",
                "LGRC9V3RuntimeState.node_last_update_event_time_key",
                "classify_lgrc9v3_step_extension",
                "build_lgrc9v3_graph_checkpoint",
            ],
        },
        {
            "question": "Does LGRC9V3 distinguish event-time key from node proper time?",
            "answer": "yes",
            "evidence": [
                "LGRC9V3RuntimeState.event_time_key",
                "LGRC9V3RuntimeState.node_proper_time",
                "LGRC9V3.step advances a local node proper-time surface from processed packet events",
            ],
        },
        {
            "question": "Does LGRC9V3 expose enough state to reconstruct budget: sum(C_i) + sum(packet_amount)?",
            "answer": "yes",
            "evidence": [
                "LGRC9V3PacketLedger.node_coherence_total",
                "LGRC9V3PacketLedger.in_flight_packet_total",
                "LGRC9V3PacketLedger.conserved_budget_total",
                "LGRC9V3PacketLedger.budget_error",
            ],
        },
        {
            "question": "Does LGRC9V3 have a route/causal channel abstraction, or must E1 define an experiment-local route manifest?",
            "answer": "partial",
            "evidence": [
                "LGRC9V3RuntimeState.causal_flux_routes",
                "LGRC9V3.set_causal_flux_routes",
                "LGRC9V3.produce_events can schedule packet departures from flux routes",
            ],
            "gap": (
                "D2.3 pole/channel cycle semantics are not a native LGRC9V3 route "
                "manifest. E1 still needs an experiment-local route mapping from "
                "D2.3 poles/channels to LGRC9V3 node/edge packet routes."
            ),
        },
        {
            "question": "Does LGRC9V3 have a native state-trigger surface, or is D2.3's trigger an experiment-local policy?",
            "answer": "experiment-local policy",
            "evidence": [
                "LGRC9V3 has autonomous packet production from configured flux routes",
                "No native source-pole-mass-minus-reference threshold trigger was found",
            ],
            "gap": (
                "D2.3's measured pole-surplus threshold trigger should be represented "
                "as an experiment-local policy in E1. A native trigger primitive would "
                "require a separate core task."
            ),
        },
    ]

    alignment = {
        "classification": "adapter_compatible",
        "native_grc9v3_evidence": False,
        "native_lgrc9v3_execution": False,
        "adapter_only": True,
        "movement_claim_allowed": False,
        "summary": (
            "Existing LGRC9V3 surfaces are sufficient for packet records, event "
            "queue ordering, in-flight packet budgets, causal clocks, runtime "
            "state snapshots, telemetry/checkpoint overlays, and queued packet "
            "execution. D2.3 still needs an experiment-local adapter for pole/"
            "channel route semantics and measured pole-surplus state triggers."
        ),
    }

    missing_surfaces = [
        {
            "surface": "d2_3_pole_channel_route_manifest",
            "status": "experiment_local_adapter_required",
            "reason": (
                "LGRC9V3 supports node/edge causal flux routes, but D2.3 defines "
                "poles and ordered channels at experiment level."
            ),
        },
        {
            "surface": "source_pole_surplus_trigger_policy",
            "status": "experiment_local_adapter_required",
            "reason": (
                "LGRC9V3 does not expose a native trigger of the form "
                "source_pole_mass - reference_pole_mass >= threshold."
            ),
        },
        {
            "surface": "d2_3_self_rearm_event_kind",
            "status": "experiment_local_adapter_required",
            "reason": (
                "LGRC9V3 can represent the packet arrival and next departure, but "
                "D2.3's semantic self_rearm label is experiment-level evidence."
            ),
        },
    ]

    sufficient_surfaces = [
        "LGRC9V3PacketRecord",
        "LGRC9V3PacketQueueEventRecord",
        "LGRC9V3PacketLedger",
        "LGRC9V3RuntimeState",
        "schedule_lgrc9v3_packet_departure",
        "process_lgrc9v3_packet_departure",
        "process_lgrc9v3_packet_arrival",
        "process_lgrc9v3_next_packet_event",
        "LGRC9V3.schedule_packet_departure",
        "LGRC9V3.step",
        "LGRC9V3.run_event_queue",
        "LGRC9V3.set_causal_flux_routes",
        "classify_lgrc9v3_step_extension",
        "build_lgrc9v3_graph_checkpoint",
    ]

    return {
        "schema": "n03_e1_lgrc9v3_surface_inventory_v1",
        "experiment_id": "2026-05-N03-grc9v3-polarized-basin-loops",
        "branch": "E1.0",
        "command": COMMAND,
        "status": "complete",
        "src_modified": False,
        "alignment": alignment,
        "findings": findings,
        "required_questions": required_questions,
        "sufficient_surfaces": sufficient_surfaces,
        "missing_surfaces": missing_surfaces,
        "surfaces": surfaces,
    }


def _write_markdown(inventory: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E1.0 LGRC9V3 Surface Inventory",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{inventory['status']}`",
        "",
        f"Classification: `{inventory['alignment']['classification']}`",
        "",
        "Boundary:",
        "",
        "```text",
        f"native_grc9v3_evidence = {str(inventory['alignment']['native_grc9v3_evidence']).lower()}",
        f"native_lgrc9v3_execution = {str(inventory['alignment']['native_lgrc9v3_execution']).lower()}",
        f"adapter_only = {str(inventory['alignment']['adapter_only']).lower()}",
        f"movement_claim_allowed = {str(inventory['alignment']['movement_claim_allowed']).lower()}",
        "```",
        "",
        "## Summary",
        "",
        inventory["alignment"]["summary"],
        "",
        "## Required Questions",
        "",
    ]
    for item in inventory["required_questions"]:
        lines.extend(
            [
                f"### {item['question']}",
                "",
                f"Answer: `{item['answer']}`",
                "",
                "Evidence:",
                "",
            ]
        )
        lines.extend(f"- {evidence}" for evidence in item["evidence"])
        if "gap" in item:
            lines.extend(["", "Gap:", "", item["gap"]])
        lines.append("")
    lines.extend(["## Sufficient Existing Surfaces", ""])
    lines.extend(f"- `{surface}`" for surface in inventory["sufficient_surfaces"])
    lines.extend(["", "## Missing Or Adapter-Only Surfaces", ""])
    for surface in inventory["missing_surfaces"]:
        lines.extend(
            [
                f"- `{surface['surface']}`: `{surface['status']}`",
                f"  {surface['reason']}",
            ]
        )
    lines.extend(["", "## Source References", ""])
    for group_name, group in inventory["surfaces"].items():
        lines.extend([f"### {group_name}", ""])
        for name, surface in group.items():
            source = surface["source"]
            lines.append(f"- `{name}` -> `{source['path']}:{source['line']}`")
        lines.append("")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    inventory = _build_inventory()
    write_json(OUTPUT_PATH, inventory)
    _write_markdown(inventory)
    print(
        json.dumps(
            {
                "status": inventory["status"],
                "classification": inventory["alignment"]["classification"],
                "adapter_only": inventory["alignment"]["adapter_only"],
                "missing_surface_count": len(inventory["missing_surfaces"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
