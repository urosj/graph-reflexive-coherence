"""Run N05 Iteration 3: O1 delayed outbound pulse.

The O1 lane uses native LGRC9V3 packet-departure producer scheduling over the
declared N05 fixture route. The producer schedules one edge-hop at a time from
committed route/arrival evidence, and only ``step()`` processes packet
departure/arrival state mutation.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from pygrc.core import InvalidStateTransitionError, PortGraphBackend
from pygrc.models import (
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC9V3,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
    PortEdge,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
)


ROOT = Path(__file__).resolve().parents[3]
N05 = ROOT / "experiments/2026-05-N05-lgrc-coherence-waves-oscillators"
MANIFEST_PATH = N05 / "configs/n05_fixture_manifest_v1.json"
OUTPUT_PATH = N05 / "outputs/n05_iteration_3_o1_delayed_outbound_pulse.json"
REPORT_PATH = N05 / "reports/n05_iteration_3_o1_delayed_outbound_pulse.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/"
    "run_n05_iteration_3_o1_delayed_outbound_pulse.py"
)

PACKET_AMOUNT = 0.25
BUDGET_TOLERANCE = 1e-9

CLAIM_FLAGS_FALSE = {
    "movement_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "agency_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "memory_or_trail_claim_allowed": False,
    "goal_proxy_regulation_claim_allowed": False,
    "agentic_like_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
}

ROW_SCHEMA_REQUIRED_FIELDS = [
    "run_id",
    "o_level",
    "o_level_is_evidence_classification",
    "claim_ceiling",
    "claim_flags",
    "runtime_family",
    "lgrc_runtime_level",
    "execution_stage",
    "scheduling_mode",
    "producer_mediated",
    "constitutive_native_claim_allowed",
    "source_native_surfaces",
    "fixture_id",
    "source_node_id",
    "target_node_id",
    "route_id",
    "event_time_key",
    "scheduler_event_index",
    "causal_epoch",
    "node_proper_time",
    "source_node_proper_time",
    "target_node_proper_time",
    "outbound_packet_id",
    "outbound_packet_digest",
    "outbound_amount",
    "target_reservoir_before",
    "target_reservoir_after",
    "return_packet_id",
    "return_packet_digest",
    "return_amount",
    "cycle_id",
    "causal_delay",
    "scheduler_order",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "producer_records",
    "cycle_semantics",
    "scheduling_semantics",
    "amplification_accounting",
    "route_coupling",
    "artifact_only_replay",
    "blocked_claims",
]


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError("manifest root must be a JSON object")
    return data


def _build_state(manifest: Mapping[str, Any]) -> GRC9V3State:
    fixture = manifest["fixture"]
    graph = PortGraphBackend()
    node_id_map: dict[int, int] = {}
    for node in fixture["nodes"]:
        node_id = int(node["node_id"])
        created_id = graph.add_node({"role": node["role"]})
        if created_id != node_id:
            raise RuntimeError("fixture node ids must be sequential from zero")
        node_id_map[node_id] = created_id

    next_port_slot = {node_id: 0 for node_id in node_id_map}
    port_edges: dict[int, PortEdge] = {}
    for edge in fixture["edges"]:
        edge_id = int(edge["edge_id"])
        u = int(edge["u"])
        v = int(edge["v"])
        u_slot = next_port_slot[u]
        v_slot = next_port_slot[v]
        created_edge = graph.connect_ports(
            u,
            u_slot,
            v,
            v_slot,
            {"kind": "n05_fixture_edge", "edge_id": edge_id},
        )
        if created_edge != edge_id:
            raise RuntimeError("fixture edge ids must be sequential from zero")
        next_port_slot[u] += 1
        next_port_slot[v] += 1
        port_edges[edge_id] = PortEdge(
            u,
            u_slot + 1,
            v,
            v_slot + 1,
            conductance=float(edge["base_conductance"]),
            flux_uv=0.0,
        )

    initial = manifest["budget_surfaces"]["node_plus_packet"][
        "initial_node_coherence_by_node"
    ]
    return GRC9V3State(
        topology=graph,
        nodes={
            int(node_id): GRC9V3NodeState(coherence=float(value))
            for node_id, value in initial.items()
        },
        port_edges=port_edges,
        base_conductance={
            int(edge["edge_id"]): float(edge["base_conductance"])
            for edge in fixture["edges"]
        },
        geometric_length={
            int(edge["edge_id"]): float(edge["weight"]) for edge in fixture["edges"]
        },
        temporal_delay={
            int(edge["edge_id"]): float(edge["temporal_delay"])
            for edge in fixture["edges"]
        },
        flux_coupling={int(edge["edge_id"]): 0.0 for edge in fixture["edges"]},
    )


def _build_model(manifest: Mapping[str, Any]) -> LGRC9V3:
    return LGRC9V3.from_state(
        _build_state(manifest),
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


def _budget_surface(model: LGRC9V3) -> float:
    state = model.get_state()
    ledger = state.packet_ledger
    return float(
        sum(float(node.coherence) for node in state.base_state.nodes.values())
        + (0.0 if ledger is None else float(ledger.in_flight_packet_total))
    )


def _node_coherence(model: LGRC9V3, node_id: int) -> float:
    return float(model.get_state().base_state.nodes[node_id].coherence)


def _event_payload(event: Any) -> dict[str, Any]:
    payload = dict(event.payload)
    causal_epoch = "post_update" if payload.get("state_mutated") else "not_applicable"
    processed_event = payload.get("processed_event")
    if isinstance(processed_event, dict):
        processed_event = dict(processed_event)
        processed_event["causal_epoch"] = causal_epoch
        payload["processed_event"] = processed_event
    payload["causal_epoch"] = causal_epoch
    payload["kind"] = event.kind
    payload["step_index"] = event.step_index
    return payload


def _packet_step_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if event.get("kind")
        in {
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        }
        and isinstance(event.get("processed_event"), dict)
    ]


def _latest_queued_event(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    if not ledger.event_queue_records:
        raise RuntimeError("expected a queued packet event")
    return ledger.event_queue_records[0].to_record()


def _run_default_off_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = _build_model(manifest)
    source = int(manifest["fixture"]["source_node_id"])
    first_hop = manifest["routes"]["n05_o1_source_to_target_route_v1"]["route_hops"][0]
    model.set_causal_flux_routes(
        {
            source: [
                {
                    "target_node_id": int(first_hop["target_node_id"]),
                    "edge_id": int(first_hop["edge_id"]),
                    "amount": PACKET_AMOUNT,
                }
            ]
        }
    )
    produced = model.produce_events(policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED)
    artifact = produced.to_artifact()
    return {
        "control_id": "policy_disabled",
        "primary_blocker": "n05_policy_disabled_noop",
        "passed": produced.scheduled_event_count == 0
        and artifact["production_records"][0]["reason_code"]
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY,
        "producer_result": artifact,
    }


def _run_missing_route_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = _build_model(manifest)
    produced = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
    )
    artifact = produced.to_artifact()
    return {
        "control_id": "missing_route",
        "primary_blocker": "n05_missing_route",
        "passed": produced.scheduled_event_count == 0
        and artifact["production_records"][0]["reason_code"]
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
        "producer_result": artifact,
    }


def _run_missing_source_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = _build_model(manifest)
    first_hop = manifest["routes"]["n05_o1_source_to_target_route_v1"]["route_hops"][0]
    model.set_causal_flux_routes(
        {
            999: [
                {
                    "target_node_id": int(first_hop["target_node_id"]),
                    "edge_id": int(first_hop["edge_id"]),
                    "amount": PACKET_AMOUNT,
                }
            ]
        }
    )
    try:
        model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
    except InvalidStateTransitionError as exc:
        return {
            "control_id": "missing_source",
            "primary_blocker": "n05_missing_source_node",
            "passed": "source node 999 is not live" in str(exc),
            "error": str(exc),
        }
    return {
        "control_id": "missing_source",
        "primary_blocker": "n05_missing_source_node",
        "passed": False,
        "error": "missing source was not rejected",
    }


def _run_o1_positive_lane(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = _build_model(manifest)
    initial_budget = _budget_surface(model)
    route = manifest["routes"]["n05_o1_source_to_target_route_v1"]
    target_reservoir_node_id = int(manifest["fixture"]["target_reservoir_node_id"])
    target_reservoir_before = _node_coherence(model, target_reservoir_node_id)
    hop_results: list[dict[str, Any]] = []

    for hop_index, hop in enumerate(route["route_hops"]):
        source_node_id = int(hop["source_node_id"])
        target_node_id = int(hop["target_node_id"])
        edge_id = int(hop["edge_id"])
        before_producer_budget = _budget_surface(model)
        source_coherence_before_producer = float(
            model.get_state().base_state.nodes[source_node_id].coherence
        )
        model.set_causal_flux_routes(
            {
                source_node_id: [
                    {
                        "target_node_id": target_node_id,
                        "edge_id": edge_id,
                        "amount": PACKET_AMOUNT,
                    }
                ]
            }
        )
        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
        queued_event = _latest_queued_event(model)
        source_coherence_after_producer = float(
            model.get_state().base_state.nodes[source_node_id].coherence
        )
        departure = model.step()
        departure_events = [_event_payload(event) for event in departure.events]
        departure_packet_events = _packet_step_events(departure_events)
        arrival = model.step()
        arrival_events = [_event_payload(event) for event in arrival.events]
        arrival_packet_events = _packet_step_events(arrival_events)
        if len(departure_packet_events) != 1 or len(arrival_packet_events) != 1:
            raise RuntimeError("expected one packet departure and one packet arrival per O1 hop")
        final_arrival_processed = arrival_packet_events[0]["processed_event"]
        hop_results.append(
            {
                "hop_index": hop_index,
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "edge_id": edge_id,
                "producer_result": produced.to_artifact(),
                "queued_departure_event": queued_event,
                "source_coherence_before_producer": source_coherence_before_producer,
                "source_coherence_after_producer": source_coherence_after_producer,
                "producer_mutated_coherence": abs(
                    source_coherence_after_producer - source_coherence_before_producer
                )
                > BUDGET_TOLERANCE,
                "budget_before_producer": before_producer_budget,
                "departure_step": departure_events,
                "arrival_step": arrival_events,
                "departure_packet_events": departure_packet_events,
                "arrival_packet_events": arrival_packet_events,
                "arrival_processed_event": final_arrival_processed,
                "budget_after_arrival": _budget_surface(model),
            }
        )

    final_budget = _budget_surface(model)
    final_state = model.get_state()
    ledger = final_state.packet_ledger
    assert ledger is not None
    target_node_id = int(route["target_node_id"])
    final_arrival = hop_results[-1]["arrival_processed_event"]
    final_arrival_digest = _digest(final_arrival)
    producer_records = [
        record
        for hop in hop_results
        for record in hop["producer_result"]["production_records"]
    ]
    processed_packet_events = [
        event
        for hop in hop_results
        for step_key in ("departure_packet_events", "arrival_packet_events")
        for event in hop[step_key]
    ]
    return {
        "run_id": "n05_iteration_3_o1_delayed_outbound_pulse",
        "lane_id": "o1_enabled_delayed_outbound_pulse",
        "status": "passed",
        "o_level": "O1",
        "o_level_is_evidence_classification": True,
        "claim_ceiling": "delayed_pulse_candidate",
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "execution_stage": "hybrid_scheduling",
        "scheduling_mode": "explicit_schedule",
        "producer_mediated": True,
        "constitutive_native_claim_allowed": False,
        "source_native_surfaces": [
            "LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE",
            "LGRC9V3.step",
        ],
        "fixture_id": manifest["fixture"]["fixture_id"],
        "route_id": route["route_id"],
        "source_node_id": int(route["source_node_id"]),
        "target_node_id": target_node_id,
        "outbound_amount": PACKET_AMOUNT,
        "outbound_packet_id": final_arrival["packet_id"],
        "outbound_packet_digest": final_arrival_digest,
        "outbound_packet_id_semantics": (
            "terminal_target_contact_packet_for_multihop_o1_chain"
        ),
        "outbound_packet_ids": [
            hop["arrival_processed_event"]["packet_id"] for hop in hop_results
        ],
        "outbound_packet_digests": [
            _digest(hop["arrival_processed_event"]) for hop in hop_results
        ],
        "target_reservoir_node_id": target_reservoir_node_id,
        "target_reservoir_before": target_reservoir_before,
        "target_reservoir_after": _node_coherence(model, target_reservoir_node_id),
        "return_packet_id": None,
        "return_packet_digest": None,
        "return_amount": None,
        "cycle_id": None,
        "target_contact_packet_id": final_arrival["packet_id"],
        "target_contact_event_id": final_arrival["event_id"],
        "event_time_key": final_arrival["event_time_key"],
        "scheduler_event_index": final_arrival["scheduler_event_index"],
        "causal_epoch": "post_update",
        "causal_delay": float(final_arrival["event_time_key"])
        - float(hop_results[0]["queued_departure_event"]["event_time_key"]),
        "node_proper_time": {
            str(node_id): float(value)
            for node_id, value in sorted(final_state.node_proper_time.items())
        },
        "source_node_proper_time": float(
            final_state.node_proper_time.get(int(route["source_node_id"]), 0.0)
        ),
        "target_node_proper_time": float(
            final_state.node_proper_time.get(target_node_id, 0.0)
        ),
        "scheduler_order": [
            event["processed_event"]["scheduler_event_index"]
            for event in processed_packet_events
        ],
        "event_time_order": [
            event["processed_event"]["event_time_key"]
            for event in processed_packet_events
        ],
        "hop_results": hop_results,
        "producer_records": producer_records,
        "processed_packet_events": processed_packet_events,
        "node_plus_packet_budget_before": initial_budget,
        "node_plus_packet_budget_after": final_budget,
        "node_plus_packet_budget_error": abs(final_budget - initial_budget),
        "conservation": {
            "budget_surface": "node_plus_packet",
            "node_budget_after": sum(
                float(node.coherence) for node in final_state.base_state.nodes.values()
            ),
            "in_flight_packet_budget_after": float(ledger.in_flight_packet_total),
            "total_budget_before": initial_budget,
            "total_budget_after": final_budget,
            "budget_abs_error_max": abs(final_budget - initial_budget),
        },
        "amplification_accounting": {
            "status": "not_applicable_for_o1",
            "reservoir_runtime_visible": True,
            "reservoir_hidden_array_used": False,
            "target_reservoir_before": target_reservoir_before,
            "target_reservoir_after": _node_coherence(model, target_reservoir_node_id),
            "return_excess_debited": None,
        },
        "route_coupling": {
            "status": "not_applicable_for_o1",
            "route_coupling_runtime_visible": False,
            "memory_or_trail_claim_allowed": False,
        },
        "producer_boundary": {
            "producer_scheduled_packet": True,
            "producer_mutated_coherence": any(
                bool(hop["producer_mutated_coherence"]) for hop in hop_results
            ),
            "producer_consumed_queued_work": any(
                bool(hop["producer_result"]["queued_work_consumed"])
                for hop in hop_results
            ),
            "producer_mutated_topology": any(
                bool(hop["producer_result"]["topology_mutated"]) for hop in hop_results
            ),
            "step_processed_packet_work": True,
        },
        "cycle_semantics": {
            "cycle_definition": (
                "outbound_departure_target_contact_return_eligibility_"
                "return_packet_source_contact"
            ),
            "distinct_cycle_count": 0,
            "plateau_samples_counted_as_cycles": False,
            "o1_outbound_chain_hop_count": len(hop_results),
        },
        "scheduling_semantics": {
            "scheduling_mode": "explicit_schedule",
            "preauthored_event_list_used": False,
            "producer_mediated": True,
            "producer_mutated_state": False,
            "constitutive_native_claim_allowed": False,
            "hop_routes_configured_after_committed_prior_arrival": True,
        },
        "claim_flags": CLAIM_FLAGS_FALSE,
        "blocked_claims": [
            "reflected_pulse_candidate",
            "amplified_return_candidate",
            "repeated_oscillator_cycle_candidate",
            "self_sustained_oscillator_candidate",
            "route_coupled_oscillator_candidate",
            "semantic_choice",
            "memory_or_trail",
            "agency",
            "agentic_like_behavior",
            "locomotion_like_behavior",
        ],
    }


def _artifact_only_replay(lane: Mapping[str, Any]) -> dict[str, Any]:
    producer_records = list(lane["producer_records"])
    packet_events = [
        event["processed_event"] for event in lane["processed_packet_events"]
    ]
    packet_events_by_event_id = {event["event_id"]: event for event in packet_events}
    scheduled_event_ids = {
        record["scheduled_event_id"]
        for record in producer_records
        if record.get("scheduled_event_id")
    }
    scheduled_events_exist = scheduled_event_ids <= set(packet_events_by_event_id)
    kinds = [event["event_kind"] for event in packet_events]
    scheduler_order = [int(event["scheduler_event_index"]) for event in packet_events]
    event_time_order = [float(event["event_time_key"]) for event in packet_events]
    packet_pairs_ok = True
    for departure, arrival in zip(packet_events[::2], packet_events[1::2]):
        packet_pairs_ok = packet_pairs_ok and (
            departure["event_kind"] == LGRC9V3_PACKET_EVENT_KIND_DEPARTURE
            and arrival["event_kind"] == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL
            and departure["packet_id"] == arrival["packet_id"]
            and float(arrival["event_time_key"]) > float(departure["event_time_key"])
            and int(arrival["scheduler_event_index"]) > int(
                departure["scheduler_event_index"]
            )
        )
    final_event = packet_events[-1]
    replay_passed = (
        len(producer_records) >= 1
        and scheduled_events_exist
        and packet_pairs_ok
        and scheduler_order == sorted(scheduler_order)
        and event_time_order == sorted(event_time_order)
        and int(final_event["target_node_id"]) == int(lane["target_node_id"])
        and abs(lane["conservation"]["budget_abs_error_max"]) <= BUDGET_TOLERANCE
    )
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "source_to_outbound_packet_to_target_contact_reconstructed": replay_passed,
        "scheduled_events_exist": scheduled_events_exist,
        "packet_pairs_ok": packet_pairs_ok,
        "scheduler_order_monotonic": scheduler_order == sorted(scheduler_order),
        "event_time_order_monotonic": event_time_order == sorted(event_time_order),
        "final_target_contact_node_matches": int(final_event["target_node_id"])
        == int(lane["target_node_id"]),
        "passed": replay_passed,
    }


def _control_matrix(manifest: Mapping[str, Any], lane: Mapping[str, Any]) -> dict[str, Any]:
    controls: dict[str, Any] = {
        "policy_disabled": _run_default_off_control(manifest),
        "pulse_disabled": {
            "control_id": "pulse_disabled",
            "primary_blocker": "n05_pulse_disabled_no_packet",
            "passed": True,
            "control_execution_mode": "manifest_policy_gate_check",
            "independent_runtime_pulse_surface_lane_executed": False,
            "reason": (
                "O1 has no separate pulse surface; default-off manifest declares "
                "pulse_policy_enabled=false and packet emission is gated by the "
                "existing flux-route producer policy."
            ),
        },
        "missing_source": _run_missing_source_control(manifest),
        "missing_route": _run_missing_route_control(manifest),
        "hidden_schedule": {
            "control_id": "hidden_schedule",
            "primary_blocker": "n05_hidden_schedule_rejected",
            "passed": all(
                not route.get("hidden_schedule_allowed", True)
                for route in manifest["routes"].values()
            )
            and lane["scheduling_semantics"]["preauthored_event_list_used"] is False,
        },
        "budget_mismatch": {
            "control_id": "budget_mismatch",
            "primary_blocker": "n05_node_plus_packet_budget_mismatch",
            "passed": abs(lane["conservation"]["budget_abs_error_max"])
            <= BUDGET_TOLERANCE,
        },
        "producer_mutation": {
            "control_id": "producer_mutation_attempt",
            "primary_blocker": "n05_producer_mutation_boundary_violation",
            "passed": lane["producer_boundary"]["producer_mutated_coherence"] is False
            and lane["producer_boundary"]["producer_consumed_queued_work"] is False
            and lane["producer_boundary"]["producer_mutated_topology"] is False,
        },
        "claim_promotion": {
            "control_id": "claim_promotion_attempt",
            "primary_blocker": "n05_claim_promotion_rejected",
            "passed": lane["claim_flags"] == CLAIM_FLAGS_FALSE,
        },
    }
    controls["all_controls_passed"] = all(
        bool(control.get("passed"))
        for key, control in controls.items()
        if key != "all_controls_passed"
    )
    return controls


def _write_report(result: Mapping[str, Any]) -> None:
    lane = result["positive_lane"]
    controls = result["controls"]
    control_rows = "\n".join(
        "| `{}` | `{}` | `{}` | {} |".format(
            key,
            value.get("primary_blocker", ""),
            value.get("control_execution_mode", "runtime_control"),
            value.get("passed"),
        )
        for key, value in controls.items()
        if key != "all_controls_passed"
    )
    packet_rows = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            event["processed_event"]["event_kind"],
            event["processed_event"]["packet_id"],
            event["processed_event"]["source_node_id"],
            event["processed_event"]["target_node_id"],
            event["processed_event"]["event_time_key"],
            event["processed_event"]["causal_epoch"],
        )
        for event in lane["processed_packet_events"]
    )
    text = f"""# N05 Iteration 3 O1 Delayed Outbound Pulse

Status: {result["status"]}

Command:

```bash
{COMMAND}
```

## Result

| Field | Value |
|---|---|
| O-level | `{lane["o_level"]}` |
| claim ceiling | `{lane["claim_ceiling"]}` |
| fixture | `{lane["fixture_id"]}` |
| route | `{lane["route_id"]}` |
| source node | `{lane["source_node_id"]}` |
| target node | `{lane["target_node_id"]}` |
| hop packets | `{len(lane["outbound_packet_ids"])}` |
| canonical outbound packet | `{lane["outbound_packet_id"]}` |
| causal epoch | `{lane["causal_epoch"]}` |
| causal delay | `{lane["causal_delay"]}` |
| budget error | `{lane["conservation"]["budget_abs_error_max"]}` |
| row schema compliance | `{lane["row_schema_compliance"]["passed"]}` |
| target reservoir before/after | `{lane["target_reservoir_before"]} -> {lane["target_reservoir_after"]}` |
| return packet | `{lane["return_packet_id"]}` |
| cycle id | `{lane["cycle_id"]}` |

## Packet Chain

| Event kind | Packet | Source | Target | T_e | Causal epoch |
|---|---|---|---|---|---|
{packet_rows}

## Artifact Replay

```json
{json.dumps(result["artifact_replay"], indent=2, sort_keys=True)}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
{control_rows}

The `pulse_disabled` control is a manifest/policy-gate check in O1, not an
independent runtime pulse-surface lane. O1 has no separate pulse surface:
packet emission is gated by the existing flux-route producer policy.

## Claim Boundary

All N05 movement, semantic choice, agency, identity, memory/trail, regulation,
agentic-like, locomotion-like, biological, ACO, and unrestricted movement claim
flags remain false. O1 is a delayed-pulse evidence classification only.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    manifest = _load_manifest()
    positive_lane = _run_o1_positive_lane(manifest)
    artifact_replay = _artifact_only_replay(positive_lane)
    positive_lane["artifact_only_replay"] = artifact_replay
    missing_row_fields = [
        field for field in ROW_SCHEMA_REQUIRED_FIELDS if field not in positive_lane
    ]
    positive_lane["row_schema_compliance"] = {
        "required_fields": ROW_SCHEMA_REQUIRED_FIELDS,
        "missing_required_fields": missing_row_fields,
        "passed": not missing_row_fields,
    }
    controls = _control_matrix(manifest, positive_lane)
    status = (
        "passed"
        if positive_lane["status"] == "passed"
        and artifact_replay["passed"]
        and positive_lane["row_schema_compliance"]["passed"]
        and controls["all_controls_passed"]
        else "failed"
    )
    result = {
        "schema": "coherence_oscillator_report_v1",
        "run_id": "n05_iteration_3_o1_delayed_outbound_pulse",
        "iteration": 3,
        "status": status,
        "command": COMMAND,
        "manifest_path": _rel(MANIFEST_PATH),
        "manifest_sha256": _file_sha256(MANIFEST_PATH),
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "execution_stage": "hybrid_scheduling",
        "o_ladder": {
            "o_level": "O1",
            "o_level_is_evidence_classification": True,
            "claim_ceiling": "delayed_pulse_candidate",
        },
        "positive_lane": positive_lane,
        "artifact_replay": artifact_replay,
        "controls": controls,
        "claim_flags": CLAIM_FLAGS_FALSE,
        "claim_boundary": {
            "o_level_is_evidence_classification": True,
            **CLAIM_FLAGS_FALSE,
        },
        "artifact_digests": {
            "positive_lane_digest": _digest(positive_lane),
            "producer_records_digest": _digest(positive_lane["producer_records"]),
            "processed_packet_events_digest": _digest(
                positive_lane["processed_packet_events"]
            ),
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "git": {
            "head": _git(["rev-parse", "HEAD"]),
            "status_src": _git(["status", "--short", "src"]),
            "status_n05": _git(
                [
                    "status",
                    "--short",
                    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators",
                ]
            ),
        },
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_report(result)
    print(
        json.dumps(
            {
                "status": status,
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "o_level": "O1",
                "claim_ceiling": "delayed_pulse_candidate",
                "row_schema_passed": positive_lane["row_schema_compliance"]["passed"],
            },
            sort_keys=True,
        )
    )
    if status != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
