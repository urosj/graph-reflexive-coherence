#!/usr/bin/env python3
"""Run E2.0 LGRC9V3 runtime feasibility probe.

E2.0 instantiates a fixed-topology 12-node ported ring as an LGRC9V3 runtime
target, schedules one packet through the existing runtime API, processes it
with `run_event_queue`, and audits the resulting packet evidence.  It does not
modify `src/*` and does not claim autonomous trigger or loop execution.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from pygrc.core import PortGraphBackend
from pygrc.models import (
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC9V3,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
    PortEdge,
)

from loop_observables import write_json  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
ROUTE_MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "e2_lgrc9v3_route_manifest.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_0_runtime_feasibility.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e2_0_runtime_feasibility.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_e2_0_runtime_feasibility.py"
)

NODE_COUNT = 12
TOTAL_BUDGET = 1.0
PACKET_AMOUNT = 0.006
TAU_EDGE = 1.0


def _build_ring_state() -> GRC9V3State:
    graph = PortGraphBackend()
    node_ids = [graph.add_node({"label": f"ring_{index}"}) for index in range(NODE_COUNT)]
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for index, source_node_id in enumerate(node_ids):
        target_node_id = node_ids[(index + 1) % NODE_COUNT]
        edge_id = graph.connect_ports(
            source_node_id,
            5,
            target_node_id,
            3,
            {"kind": "e2_ported_ring_clockwise", "clockwise_edge_index": index},
        )
        port_edges[edge_id] = PortEdge(
            source_node_id,
            6,
            target_node_id,
            4,
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = TAU_EDGE
        flux_coupling[edge_id] = 0.0
    return GRC9V3State(
        topology=graph,
        nodes={
            node_id: GRC9V3NodeState(coherence=TOTAL_BUDGET / NODE_COUNT)
            for node_id in node_ids
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )


def _build_route_manifest() -> dict[str, Any]:
    channels = {
        "S1_to_K2": {
            "source_pole": "S1",
            "target_pole": "K2",
            "route_hops": [
                {"source_node_id": 1, "target_node_id": 2, "edge_id": 1},
                {"source_node_id": 2, "target_node_id": 3, "edge_id": 2},
            ],
        },
        "K2_to_S2": {
            "source_pole": "K2",
            "target_pole": "S2",
            "route_hops": [
                {"source_node_id": 4, "target_node_id": 5, "edge_id": 4},
                {"source_node_id": 5, "target_node_id": 6, "edge_id": 5},
            ],
        },
        "S2_to_K1": {
            "source_pole": "S2",
            "target_pole": "K1",
            "route_hops": [
                {"source_node_id": 7, "target_node_id": 8, "edge_id": 7},
                {"source_node_id": 8, "target_node_id": 9, "edge_id": 8},
            ],
        },
        "K1_to_S1": {
            "source_pole": "K1",
            "target_pole": "S1",
            "route_hops": [
                {"source_node_id": 10, "target_node_id": 11, "edge_id": 10},
                {"source_node_id": 11, "target_node_id": 0, "edge_id": 11},
            ],
        },
    }
    return {
        "schema": "n03_e2_lgrc9v3_route_manifest_v1",
        "experiment_id": "2026-05-N03-grc9v3-polarized-basin-loops",
        "branch": "E2.0",
        "fixture": "e2_lgrc9v3_ported_ring_v1",
        "node_count": NODE_COUNT,
        "edge_count": NODE_COUNT,
        "ports": {
            "clockwise_out_port": 6,
            "clockwise_in_port": 4,
            "port_numbering": "PortEdge records use 1-based ports; graph construction uses zero-based slots.",
        },
        "poles": {
            "S1": [0, 1],
            "K2": [3, 4],
            "S2": [6, 7],
            "K1": [9, 10],
        },
        "declared_routes": {
            "d2_3_cw_closed_loop": [
                "S1_to_K2",
                "K2_to_S2",
                "S2_to_K1",
                "K1_to_S1",
            ]
        },
        "channels": channels,
        "e2_0_probe": {
            "channel_id": "S1_to_K2",
            "hop_index": 0,
            "source_node_id": 1,
            "target_node_id": 2,
            "edge_id": 1,
            "amount": PACKET_AMOUNT,
        },
    }


def _topology_signature(state: GRC9V3State) -> dict[str, int]:
    return {
        "node_count": len(tuple(state.topology.iter_live_node_ids())),
        "edge_count": len(tuple(state.topology.iter_live_edge_ids())),
    }


def _event_summary(result: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in result.events:
        rows.append(
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "payload": event.payload,
            }
        )
    return rows


def _node_total(state: GRC9V3State) -> float:
    return sum(float(node.coherence) for node in state.nodes.values())


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E2.0 LGRC9V3 Runtime Feasibility",
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
        "loop_claim_allowed = false",
        "```",
        "",
        "## Audit",
        "",
    ]
    for key, value in result["audit"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Runtime Steps", ""])
    for step in result["runtime_steps"]:
        lines.append(
            "- `{kind}` at event_time `{time}` with scheduler index `{index}`".format(
                kind=step["processed_event_kind"],
                time=step["event_time_key"],
                index=step["scheduler_event_index"],
            )
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    route_manifest = _build_route_manifest()
    write_json(ROUTE_MANIFEST_PATH, route_manifest)
    state = _build_ring_state()
    initial_signature = _topology_signature(state)
    initial_node_total = _node_total(state)
    params = {
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
    }
    model = LGRC9V3.from_state(state, params)
    probe = route_manifest["e2_0_probe"]
    model.schedule_packet_departure(
        source_node_id=int(probe["source_node_id"]),
        target_node_id=int(probe["target_node_id"]),
        edge_id=int(probe["edge_id"]),
        amount=float(probe["amount"]),
        departure_event_time_key=0.0,
        scheduler_event_index=1,
    )
    results = model.run_event_queue(max_events=4)
    final_state = model.get_state()
    final_signature = _topology_signature(final_state.base_state)
    packet_ledger = final_state.packet_ledger
    assert packet_ledger is not None

    runtime_steps = [
        {
            "processed_event_kind": result.bookkeeping.get("processed_event_kind"),
            "scheduler_event_index": result.bookkeeping.get("scheduler_event_index"),
            "event_time_key": result.bookkeeping.get("event_time_key"),
            "events": _event_summary(result),
        }
        for result in results
    ]
    event_kinds = [
        str(step["processed_event_kind"])
        for step in runtime_steps
        if step["processed_event_kind"] is not None
    ]
    node_total = _node_total(final_state.base_state)
    in_flight_total = float(packet_ledger.in_flight_packet_total)
    reconstructed_total = node_total + in_flight_total
    audit = {
        "scheduled_packet_count": 1,
        "runtime_step_count": len(results),
        "departure_seen": LGRC9V3_PACKET_EVENT_KIND_DEPARTURE in event_kinds,
        "arrival_seen": LGRC9V3_PACKET_EVENT_KIND_ARRIVAL in event_kinds,
        "event_time_advanced": float(final_state.event_time_key) > 0.0,
        "source_node_proper_time_recorded": int(probe["source_node_id"])
        in final_state.node_proper_time,
        "target_node_proper_time_recorded": int(probe["target_node_id"])
        in final_state.node_proper_time,
        "node_plus_packet_budget": reconstructed_total,
        "budget_error": abs(reconstructed_total - initial_node_total),
        "in_flight_packet_total": in_flight_total,
        "topology_unchanged": initial_signature == final_signature,
        "queue_empty": len(packet_ledger.event_queue_records) == 0,
        "packet_processing_log_count": len(final_state.packet_processing_log),
        "arrival_eligibility_log_count": len(final_state.arrival_eligibility_log),
        "local_update_log_count": len(final_state.local_update_log),
    }
    status = (
        "passed"
        if audit["departure_seen"]
        and audit["arrival_seen"]
        and audit["topology_unchanged"]
        and audit["queue_empty"]
        and audit["budget_error"] <= 1e-9
        else "failed"
    )
    result = {
        "schema": "n03_e2_0_lgrc9v3_runtime_feasibility_v1",
        "branch": "E2.0",
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
            "loop_claim_allowed": False,
        },
        "route_manifest": str(ROUTE_MANIFEST_PATH.relative_to(EXPERIMENT_ROOT)),
        "probe": probe,
        "initial_topology": initial_signature,
        "final_topology": final_signature,
        "runtime_steps": runtime_steps,
        "audit": audit,
        "non_native_assumptions": [
            "The pole/channel route manifest is experiment-local.",
            "The probe packet is scheduled explicitly by the experiment.",
            "No state-trigger or self-rearm semantics are claimed in E2.0.",
        ],
        "interpretation": (
            "Existing LGRC9V3 runtime methods can execute one scheduled packet "
            "departure/arrival on the N03 ported-ring fixture with conserved "
            "node-plus-packet budget and unchanged topology. This establishes "
            "native packet execution feasibility only; it does not establish "
            "native autonomous trigger production, self-rearm semantics, or a "
            "loop claim."
        ),
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": status,
                "runtime_step_count": audit["runtime_step_count"],
                "departure_seen": audit["departure_seen"],
                "arrival_seen": audit["arrival_seen"],
                "budget_error": audit["budget_error"],
                "topology_unchanged": audit["topology_unchanged"],
            },
            sort_keys=True,
        )
    )
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
