#!/usr/bin/env python3
"""Run E2.4 native LGRC9V3 autonomy feasibility audit.

E2.4 asks whether existing LGRC9V3 producer/autonomy surfaces can natively
produce the D2.3 packet loop without the E2.3 experiment-local surplus trigger
adapter.  It does not add primitives or modify `src/*`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from pygrc.models import (
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LAPSE_POLICY_UNIT,
    LGRC9V3,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
    LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1,
    LGRC9V3_LOCAL_UPDATE_EVENT_KIND,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
)

import run_e2_0_runtime_feasibility as e2_0
from loop_observables import write_json


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_4_native_autonomy_feasibility.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e2_4_native_autonomy_feasibility.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_e2_4_native_autonomy_feasibility.py"
)

PACKET_AMOUNT = 0.006
MAX_EVENTS = 80
BUDGET_TOLERANCE = 1e-9


def _build_model() -> LGRC9V3:
    state = e2_0._build_ring_state()
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


def _native_closed_ring_routes() -> dict[int, list[dict[str, Any]]]:
    routes: dict[int, list[dict[str, Any]]] = {}
    for source_node_id in range(e2_0.NODE_COUNT):
        target_node_id = (source_node_id + 1) % e2_0.NODE_COUNT
        route: dict[str, Any] = {
            "target_node_id": target_node_id,
            "edge_id": source_node_id,
        }
        if source_node_id == 1:
            route["amount"] = PACKET_AMOUNT
        routes[source_node_id] = [route]
    return routes


def _event_counts(results: list[Any]) -> dict[str, int]:
    counts = {
        LGRC9V3_PACKET_EVENT_KIND_DEPARTURE: 0,
        LGRC9V3_PACKET_EVENT_KIND_ARRIVAL: 0,
        LGRC9V3_LOCAL_UPDATE_EVENT_KIND: 0,
    }
    for result in results:
        for event in result.events:
            if event.kind in counts:
                counts[event.kind] += 1
    return counts


def _runtime_records(results: list[Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for result in results:
        for event in result.events:
            if event.kind not in (
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
                LGRC9V3_LOCAL_UPDATE_EVENT_KIND,
            ):
                continue
            payload = dict(event.payload)
            processed = payload.get("processed_event", {})
            records.append(
                {
                    "kind": event.kind,
                    "step_index": event.step_index,
                    "event_time_key": payload.get("event_time_key"),
                    "scheduler_event_index": payload.get("scheduler_event_index"),
                    "packet_id": processed.get("packet_id") if isinstance(processed, Mapping) else None,
                    "source_node_id": processed.get("source_node_id") if isinstance(processed, Mapping) else payload.get("target_node_id"),
                    "target_node_id": processed.get("target_node_id") if isinstance(processed, Mapping) else None,
                    "edge_id": processed.get("edge_id") if isinstance(processed, Mapping) else None,
                    "scheduled_packet_count": payload.get("scheduled_packet_count"),
                    "budget_error": payload.get("budget_error"),
                    "topology_mutated": payload.get("topology_mutated"),
                }
            )
    return records


def _summarize_production(summary: Mapping[str, Any]) -> dict[str, Any]:
    production_results = list(summary.get("production_results", []))
    records = [
        record
        for result in production_results
        for record in result.get("production_records", [])
    ]
    reason_counts: dict[str, int] = {}
    for record in records:
        reason = str(record.get("reason_code"))
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
    return {
        "producer_policies": list(summary.get("producer_policies", [])),
        "stop_condition": summary.get("stop_condition"),
        "scheduled_event_count": summary.get("scheduled_event_count"),
        "consumed_event_count": summary.get("consumed_event_count"),
        "production_record_count": len(records),
        "reason_counts": reason_counts,
    }


def _run_static_route_autonomy_probe() -> dict[str, Any]:
    model = _build_model()
    initial_signature = e2_0._topology_signature(model.get_state().base_state)
    initial_budget = e2_0._node_total(model.get_state().base_state)
    model.set_causal_flux_routes(_native_closed_ring_routes())
    results = model.run_autonomous(
        max_events=MAX_EVENTS,
        policy=LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1,
        producer_policies=(LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,),
    )
    final_state = model.get_state()
    final_signature = e2_0._topology_signature(final_state.base_state)
    ledger = final_state.packet_ledger
    assert ledger is not None
    final_budget = e2_0._node_total(final_state.base_state) + float(
        ledger.in_flight_packet_total
    )
    event_counts = _event_counts(results)
    runtime_records = _runtime_records(results)
    autonomy_summary = dict(
        final_state.cached_quantities.get("last_lgrc9v3_autonomous_run", {})
    )
    return {
        "probe_id": "native_static_closed_route_probe",
        "status": "passed"
        if results
        and event_counts[LGRC9V3_PACKET_EVENT_KIND_DEPARTURE] > 0
        and event_counts[LGRC9V3_PACKET_EVENT_KIND_ARRIVAL] > 0
        and initial_signature == final_signature
        and abs(final_budget - initial_budget) <= BUDGET_TOLERANCE
        else "failed",
        "route_policy": (
            "node_keyed_causal_flux_routes; initial source route has fixed "
            "amount, downstream routes forward arrival amount"
        ),
        "runtime_step_count": len(results),
        "event_counts": event_counts,
        "initial_topology": initial_signature,
        "final_topology": final_signature,
        "topology_unchanged": initial_signature == final_signature,
        "budget_error": abs(final_budget - initial_budget),
        "queue_empty": len(ledger.event_queue_records) == 0,
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "autonomy_summary": _summarize_production(autonomy_summary),
        "runtime_records_sample": runtime_records[:24],
    }


def _surface_inventory() -> dict[str, Any]:
    return {
        "set_causal_flux_routes": {
            "exists": hasattr(LGRC9V3, "set_causal_flux_routes"),
            "meaning": "node/edge keyed route table; no pole-mask semantics",
        },
        "produce_events": {
            "exists": hasattr(LGRC9V3, "produce_events"),
            "supported_policies": [
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
            ],
        },
        "run_autonomous": {
            "exists": hasattr(LGRC9V3, "run_autonomous"),
            "policy": LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1,
        },
    }


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    probe = result["native_static_route_probe"]
    lines = [
        "# E2.4 Native Autonomy Feasibility",
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
        "movement_claim_allowed = false",
        "core_task_requested = false",
        "```",
        "",
        "## Native Probe",
        "",
        f"- probe status: `{probe['status']}`",
        f"- runtime steps: `{probe['runtime_step_count']}`",
        f"- packet departures: `{probe['event_counts'][LGRC9V3_PACKET_EVENT_KIND_DEPARTURE]}`",
        f"- packet arrivals: `{probe['event_counts'][LGRC9V3_PACKET_EVENT_KIND_ARRIVAL]}`",
        f"- local updates: `{probe['event_counts'][LGRC9V3_LOCAL_UPDATE_EVENT_KIND]}`",
        f"- budget error: `{probe['budget_error']}`",
        f"- topology unchanged: `{probe['topology_unchanged']}`",
        "",
        "## Equivalence Audit",
        "",
    ]
    for key, value in result["d2_3_equivalence_audit"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Interpretation", "", result["interpretation"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    surface_inventory = _surface_inventory()
    static_route_probe = _run_static_route_autonomy_probe()
    d2_3_equivalence_audit = {
        "native_packet_route_production_exists": (
            static_route_probe["status"] == "passed"
        ),
        "native_arrival_triggered_route_forwarding_exists": (
            static_route_probe["event_counts"][LGRC9V3_LOCAL_UPDATE_EVENT_KIND] > 0
        ),
        "native_pole_mask_route_semantics_exists": False,
        "native_source_pole_surplus_threshold_trigger_exists": False,
        "native_d2_3_self_rearm_label_exists": False,
        "native_d2_3_equivalent": False,
        "adapter_required_for_d2_3_semantics": True,
    }
    classification = (
        "native_static_route_autonomy_feasible_d2_3_surplus_trigger_missing"
        if static_route_probe["status"] == "passed"
        else "missing_trigger_primitive"
    )
    result = {
        "schema": "n03_e2_4_native_autonomy_feasibility_v1",
        "branch": "E2.4",
        "command": COMMAND,
        "status": "passed" if static_route_probe["status"] == "passed" else "failed",
        "classification": classification,
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": True,
            "movement_claim_allowed": False,
            "core_task_requested": False,
        },
        "surface_inventory": surface_inventory,
        "native_static_route_probe": static_route_probe,
        "d2_3_equivalence_audit": d2_3_equivalence_audit,
        "core_task_recommendation": {
            "requested": False,
            "reason": (
                "Existing LGRC9V3 can produce static node/edge flux-route "
                "packet work and arrival-triggered route forwarding. It does "
                "not currently expose D2.3's pole-surplus trigger or semantic "
                "self-rearm label as native primitives."
            ),
        },
        "interpretation": (
            "E2.4 finds that native LGRC9V3 autonomy is stronger than the E1 "
            "adapter-only result: existing `produce_events`, `run_autonomous`, "
            "and `causal_flux_routes` can generate and execute a bounded closed "
            "packet route under exact budget and fixed topology. However, that "
            "native surface is node/edge keyed and route-table driven. It is "
            "not equivalent to D2.3's measured pole-surplus threshold trigger, "
            "and it does not emit D2.3 self-rearm semantics as native evidence. "
            "Therefore E2.3 remains the correct D2.3-aligned runtime result, "
            "while E2.4 records a native static-route autonomy surface and a "
            "missing native surplus-trigger primitive."
        ),
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": classification,
                "native_static_route_probe": static_route_probe["status"],
                "native_d2_3_equivalent": d2_3_equivalence_audit[
                    "native_d2_3_equivalent"
                ],
                "adapter_required_for_d2_3_semantics": d2_3_equivalence_audit[
                    "adapter_required_for_d2_3_semantics"
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
