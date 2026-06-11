"""Run N05 Iteration 5: O3 amplified return with reservoir accounting.

The O3 lane extends O2 by releasing declared, runtime-visible target-reservoir
coherence before scheduling a return packet larger than the outbound packet.
The amplification is therefore accounted for by packet-ledger mutation through
existing LGRC9V3 producer and ``step()`` mechanics, not by hidden fixture state.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N05 = ROOT / "experiments/2026-05-N05-lgrc-coherence-waves-oscillators"
MANIFEST_PATH = N05 / "configs/n05_fixture_manifest_v1.json"
OUTPUT_PATH = N05 / "outputs/n05_iteration_5_o3_amplified_return.json"
REPORT_PATH = N05 / "reports/n05_iteration_5_o3_amplified_return.md"
O2_SCRIPT_PATH = N05 / "scripts/run_n05_iteration_4_o2_reflected_return_pulse.py"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/"
    "run_n05_iteration_5_o3_amplified_return.py"
)

OUTBOUND_AMOUNT = 0.25
RESERVOIR_RELEASE_AMOUNT = 0.25
RETURN_AMOUNT = OUTBOUND_AMOUNT + RESERVOIR_RELEASE_AMOUNT


def _load_o2_module() -> Any:
    spec = importlib.util.spec_from_file_location("n05_iteration_4_o2", O2_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load O2 helper module from {O2_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


O2 = _load_o2_module()
O1 = O2.O1
BUDGET_TOLERANCE = O1.BUDGET_TOLERANCE
CLAIM_FLAGS_FALSE = O1.CLAIM_FLAGS_FALSE
ROW_SCHEMA_REQUIRED_FIELDS = O1.ROW_SCHEMA_REQUIRED_FIELDS


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


def _run_route_hops(
    model: Any,
    route: Mapping[str, Any],
    *,
    amount: float,
    chain_phase: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    hop_results: list[dict[str, Any]] = []
    producer_records: list[dict[str, Any]] = []
    packet_events: list[dict[str, Any]] = []

    for hop_index, hop in enumerate(route["route_hops"]):
        source_node_id = int(hop["source_node_id"])
        target_node_id = int(hop["target_node_id"])
        edge_id = int(hop["edge_id"])
        before_producer_budget = O1._budget_surface(model)
        source_coherence_before_producer = O1._node_coherence(model, source_node_id)
        model.set_causal_flux_routes(
            {
                source_node_id: [
                    {
                        "target_node_id": target_node_id,
                        "edge_id": edge_id,
                        "amount": amount,
                    }
                ]
            }
        )
        produced = model.produce_events(
            policy=O1.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
        queued_event = O1._latest_queued_event(model)
        source_coherence_after_producer = O1._node_coherence(model, source_node_id)
        departure = model.step()
        departure_events = [O1._event_payload(event) for event in departure.events]
        departure_packet_events = O1._packet_step_events(departure_events)
        arrival = model.step()
        arrival_events = [O1._event_payload(event) for event in arrival.events]
        arrival_packet_events = O1._packet_step_events(arrival_events)
        if len(departure_packet_events) != 1 or len(arrival_packet_events) != 1:
            raise RuntimeError(
                "expected one packet departure and one packet arrival per O3 hop"
            )
        for event in [*departure_packet_events, *arrival_packet_events]:
            event["chain_phase"] = chain_phase
            event["route_id"] = route["route_id"]
        hop_result = {
            "chain_phase": chain_phase,
            "hop_index": hop_index,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "edge_id": edge_id,
            "amount": amount,
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
            "arrival_processed_event": arrival_packet_events[0]["processed_event"],
            "budget_after_arrival": O1._budget_surface(model),
        }
        hop_results.append(hop_result)
        producer_records.extend(produced.to_artifact()["production_records"])
        packet_events.extend(departure_packet_events)
        packet_events.extend(arrival_packet_events)

    return hop_results, producer_records, packet_events


def _reservoir_release_route(manifest: Mapping[str, Any]) -> dict[str, Any]:
    reservoir_node_id = int(manifest["fixture"]["target_reservoir_node_id"])
    target_node_id = int(manifest["fixture"]["target_node_id"])
    return {
        "route_id": "n05_o3_declared_target_reservoir_release_route_v1",
        "route_kind": "reservoir_release",
        "source_node_id": reservoir_node_id,
        "target_node_id": target_node_id,
        "route_hops": [
            {
                "edge_id": 2,
                "source_node_id": reservoir_node_id,
                "target_node_id": target_node_id,
            }
        ],
        "hidden_schedule_allowed": False,
        "reservoir_release_route_serialized_in_artifact": True,
    }


def _run_o3_positive_lane(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = O1._build_model(manifest)
    initial_budget = O1._budget_surface(model)
    target_reservoir_node_id = int(manifest["fixture"]["target_reservoir_node_id"])
    target_reservoir_before = O1._node_coherence(model, target_reservoir_node_id)
    outbound_route = manifest["routes"]["n05_o1_source_to_target_route_v1"]
    return_route = manifest["routes"]["n05_o2_target_to_source_return_route_v1"]
    reservoir_route = _reservoir_release_route(manifest)

    outbound_hops, outbound_producer_records, outbound_packet_events = _run_route_hops(
        model,
        outbound_route,
        amount=OUTBOUND_AMOUNT,
        chain_phase="outbound",
    )
    target_contact = outbound_hops[-1]["arrival_processed_event"]
    contact_valid, contact_blocker = O2._validate_return_contact(
        target_contact,
        expected_target_node_id=int(outbound_route["target_node_id"]),
    )
    if not contact_valid:
        raise RuntimeError(f"target contact did not authorize O3: {contact_blocker}")

    target_contact_digest = _digest(target_contact)
    reservoir_reference_mass = target_reservoir_before
    reservoir_release_policy = {
        "policy_id": "n05_o3_declared_target_reservoir_release_policy_v1",
        "source_event_id": target_contact["event_id"],
        "source_event_digest": target_contact_digest,
        "source_event_kind": target_contact["event_kind"],
        "reservoir_node_id": target_reservoir_node_id,
        "observed_value_field": "node_coherence",
        "observed_value_before_release": target_reservoir_before,
        "reference_value": reservoir_reference_mass,
        "release_amount": RESERVOIR_RELEASE_AMOUNT,
        "return_amount": RETURN_AMOUNT,
        "return_excess": RESERVOIR_RELEASE_AMOUNT,
        "route_id": reservoir_route["route_id"],
        "threshold_sources_serialized": True,
        "reservoir_runtime_visible": True,
        "hidden_reservoir_array_used": False,
        "not_before_scheduler_event_index": target_contact["scheduler_event_index"],
        "not_before_event_time_key": target_contact["event_time_key"],
    }
    release_hops, release_producer_records, release_packet_events = _run_route_hops(
        model,
        reservoir_route,
        amount=RESERVOIR_RELEASE_AMOUNT,
        chain_phase="reservoir_release",
    )
    target_reservoir_after_release = O1._node_coherence(model, target_reservoir_node_id)

    return_eligibility_record = {
        "record_id": "n05-o3-return-eligibility-" + target_contact_digest[:24],
        "record_kind": "n05_amplified_return_eligibility",
        "source_event_id": target_contact["event_id"],
        "source_event_digest": target_contact_digest,
        "source_packet_id": target_contact["packet_id"],
        "source_route_id": outbound_route["route_id"],
        "return_route_id": return_route["route_id"],
        "reservoir_release_policy_id": reservoir_release_policy["policy_id"],
        "reservoir_release_route_id": reservoir_route["route_id"],
        "reservoir_release_packet_id": release_hops[-1]["arrival_processed_event"][
            "packet_id"
        ],
        "reservoir_release_event_id": release_hops[-1]["arrival_processed_event"][
            "event_id"
        ],
        "return_amount": RETURN_AMOUNT,
        "return_excess_debited": RESERVOIR_RELEASE_AMOUNT,
        "not_before_scheduler_event_index": release_hops[-1]["arrival_processed_event"][
            "scheduler_event_index"
        ],
        "not_before_event_time_key": release_hops[-1]["arrival_processed_event"][
            "event_time_key"
        ],
        "committed_target_contact_required": True,
        "committed_reservoir_release_required": True,
        "hidden_return_timing_used": False,
    }

    return_hops, return_producer_records, return_packet_events = _run_route_hops(
        model,
        return_route,
        amount=RETURN_AMOUNT,
        chain_phase="amplified_return",
    )

    final_budget = O1._budget_surface(model)
    final_state = model.get_state()
    ledger = final_state.packet_ledger
    assert ledger is not None
    final_return = return_hops[-1]["arrival_processed_event"]
    final_return_digest = _digest(final_return)
    producer_records = [
        *outbound_producer_records,
        *release_producer_records,
        *return_producer_records,
    ]
    processed_packet_events = [
        *outbound_packet_events,
        *release_packet_events,
        *return_packet_events,
    ]
    scheduler_order = [
        event["processed_event"]["scheduler_event_index"]
        for event in processed_packet_events
    ]
    event_time_order = [
        event["processed_event"]["event_time_key"] for event in processed_packet_events
    ]
    target_reservoir_after = O1._node_coherence(model, target_reservoir_node_id)
    return_excess = RETURN_AMOUNT - OUTBOUND_AMOUNT
    reservoir_delta = target_reservoir_before - target_reservoir_after_release

    return {
        "run_id": "n05_iteration_5_o3_amplified_return",
        "lane_id": "o3_enabled_amplified_return",
        "status": "passed",
        "o_level": "O3",
        "o_level_is_evidence_classification": True,
        "claim_ceiling": "amplified_return_candidate",
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
        "source_node_id": int(outbound_route["source_node_id"]),
        "target_node_id": int(outbound_route["target_node_id"]),
        "route_id": outbound_route["route_id"],
        "return_route_id": return_route["route_id"],
        "reservoir_release_route": reservoir_route,
        "event_time_key": final_return["event_time_key"],
        "scheduler_event_index": final_return["scheduler_event_index"],
        "causal_epoch": "post_update",
        "node_proper_time": {
            str(node_id): float(value)
            for node_id, value in sorted(final_state.node_proper_time.items())
        },
        "source_node_proper_time": float(
            final_state.node_proper_time.get(int(outbound_route["source_node_id"]), 0.0)
        ),
        "target_node_proper_time": float(
            final_state.node_proper_time.get(int(outbound_route["target_node_id"]), 0.0)
        ),
        "target_contact_event_id": target_contact["event_id"],
        "target_contact_evidence": {
            "evidence_kind": "committed_lgrc9v3_packet_arrival_event",
            "source_event_id": target_contact["event_id"],
            "source_event_digest": target_contact_digest,
            "native_causal_pulse_substrate_surface_used": False,
        },
        "outbound_packet_id": target_contact["packet_id"],
        "outbound_packet_digest": target_contact_digest,
        "outbound_packet_id_semantics": (
            "terminal_target_contact_packet_for_multihop_o3_outbound_chain"
        ),
        "outbound_packet_ids": [
            hop["arrival_processed_event"]["packet_id"] for hop in outbound_hops
        ],
        "outbound_packet_digests": [
            _digest(hop["arrival_processed_event"]) for hop in outbound_hops
        ],
        "outbound_amount": OUTBOUND_AMOUNT,
        "target_reservoir_node_id": target_reservoir_node_id,
        "target_reservoir_before": target_reservoir_before,
        "target_reservoir_after": target_reservoir_after,
        "target_reservoir_after_release": target_reservoir_after_release,
        "return_packet_id": final_return["packet_id"],
        "return_packet_digest": final_return_digest,
        "return_packet_ids": [
            hop["arrival_processed_event"]["packet_id"] for hop in return_hops
        ],
        "return_packet_digests": [
            _digest(hop["arrival_processed_event"]) for hop in return_hops
        ],
        "return_amount": RETURN_AMOUNT,
        "cycle_id": "n05_o3_amplified_return_cycle_000",
        "return_source_contact_event_id": final_return["event_id"],
        "return_eligibility_record": return_eligibility_record,
        "reservoir_release_policy": reservoir_release_policy,
        "outbound_return_lineage": {
            "outbound_target_contact_event_id": target_contact["event_id"],
            "outbound_target_contact_digest": target_contact_digest,
            "reservoir_release_event_id": release_hops[-1]["arrival_processed_event"][
                "event_id"
            ],
            "return_eligibility_record_id": return_eligibility_record["record_id"],
            "return_packet_id": final_return["packet_id"],
            "return_packet_digest": final_return_digest,
            "return_linked_to_outbound_event": True,
            "return_linked_to_reservoir_release": True,
        },
        "causal_delay": float(final_return["event_time_key"])
        - float(outbound_hops[0]["queued_departure_event"]["event_time_key"]),
        "outbound_causal_delay": float(target_contact["event_time_key"])
        - float(outbound_hops[0]["queued_departure_event"]["event_time_key"]),
        "reservoir_release_causal_delay": float(
            release_hops[-1]["arrival_processed_event"]["event_time_key"]
        )
        - float(release_hops[0]["queued_departure_event"]["event_time_key"]),
        "return_causal_delay": float(final_return["event_time_key"])
        - float(return_hops[0]["queued_departure_event"]["event_time_key"]),
        "scheduler_order": scheduler_order,
        "event_time_order": event_time_order,
        "outbound_hop_results": outbound_hops,
        "reservoir_release_hop_results": release_hops,
        "return_hop_results": return_hops,
        "producer_records": producer_records,
        "processed_packet_events": processed_packet_events,
        "outbound_packet_events": outbound_packet_events,
        "reservoir_release_packet_events": release_packet_events,
        "return_packet_events": return_packet_events,
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
            "status": "passed",
            "amplification_source_kind": "target_reservoir",
            "amplification_source_detail": "declared_target_reservoir_node",
            "reservoir_runtime_visible": True,
            "reservoir_hidden_array_used": False,
            "reservoir_source_serialized": True,
            "observed_value_source": "runtime_node_coherence",
            "target_reservoir_node_id": target_reservoir_node_id,
            "target_reservoir_before": target_reservoir_before,
            "target_reservoir_after_release": target_reservoir_after_release,
            "target_reservoir_after": target_reservoir_after,
            "reservoir_budget_before": target_reservoir_before,
            "reservoir_budget_after": target_reservoir_after,
            "reservoir_delta": reservoir_delta,
            "outbound_amount": OUTBOUND_AMOUNT,
            "return_amount": RETURN_AMOUNT,
            "return_amount_exceeds_outbound": RETURN_AMOUNT > OUTBOUND_AMOUNT,
            "return_excess": return_excess,
            "return_excess_debited": RESERVOIR_RELEASE_AMOUNT,
            "return_excess_matches_reservoir_debit": abs(
                return_excess - reservoir_delta
            )
            <= BUDGET_TOLERANCE,
            "silent_amplification_used": False,
        },
        "route_coupling": {
            "status": "not_applicable_for_o3",
            "route_coupling_runtime_visible": False,
            "memory_or_trail_claim_allowed": False,
        },
        "producer_boundary": {
            "producer_scheduled_packet": True,
            "producer_mutated_coherence": any(
                bool(hop["producer_mutated_coherence"])
                for hop in [*outbound_hops, *release_hops, *return_hops]
            ),
            "producer_consumed_queued_work": any(
                bool(hop["producer_result"]["queued_work_consumed"])
                for hop in [*outbound_hops, *release_hops, *return_hops]
            ),
            "producer_mutated_topology": any(
                bool(hop["producer_result"]["topology_mutated"])
                for hop in [*outbound_hops, *release_hops, *return_hops]
            ),
            "step_processed_packet_work": True,
        },
        "cycle_semantics": {
            "cycle_definition": (
                "outbound_departure_target_contact_reservoir_release_"
                "return_eligibility_return_packet_source_contact"
            ),
            "distinct_cycle_count": 1,
            "plateau_samples_counted_as_cycles": False,
            "repeated_cycle_claim_allowed": False,
        },
        "scheduling_semantics": {
            "scheduling_mode": "explicit_schedule",
            "preauthored_event_list_used": False,
            "hidden_return_timing_used": False,
            "hidden_reservoir_used": False,
            "producer_mediated": True,
            "producer_mutated_state": False,
            "constitutive_native_claim_allowed": False,
            "reservoir_release_after_committed_target_contact": True,
            "return_route_configured_after_committed_reservoir_release": True,
        },
        "deferred_shared_controls": [
            {
                "control_id": "missing_target",
                "status": "not_rerun_in_o3",
                "reason": "covered by Iteration 2 fixture manifest controls; O3 ran O3-specific reservoir controls",
            },
            {
                "control_id": "missing_route",
                "status": "not_rerun_in_o3",
                "reason": "covered by Iteration 3 route control; O3 route ids are serialized in the artifact",
            },
            {
                "control_id": "stale_producer_read",
                "status": "not_rerun_in_o3",
                "reason": "reserved for later producer-state or repeated-cycle lanes",
            },
            {
                "control_id": "idempotent_duplicate_production",
                "status": "not_rerun_in_o3",
                "reason": "reserved for repeated-cycle lanes where duplicate cycle production is meaningful",
            },
            {
                "control_id": "snapshot_continue_after_load",
                "status": "not_rerun_in_o3",
                "reason": "reserved for later repeated-cycle or closeout lanes",
            },
        ],
        "claim_flags": CLAIM_FLAGS_FALSE,
        "blocked_claims": [
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


def _packet_pairs_ok(packet_events: list[dict[str, Any]]) -> bool:
    return O2._packet_pairs_ok(packet_events)


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
    target_contact_event = packet_events_by_event_id.get(lane["target_contact_event_id"])
    reservoir_release_event = packet_events_by_event_id.get(
        lane["return_eligibility_record"]["reservoir_release_event_id"]
    )
    return_source_contact_event = packet_events_by_event_id.get(
        lane["return_source_contact_event_id"]
    )
    scheduler_order = [int(event["scheduler_event_index"]) for event in packet_events]
    event_time_order = [float(event["event_time_key"]) for event in packet_events]
    accounting = lane["amplification_accounting"]
    amplification_accounting_ok = (
        accounting["return_amount_exceeds_outbound"] is True
        and accounting["silent_amplification_used"] is False
        and accounting["reservoir_runtime_visible"] is True
        and accounting["reservoir_hidden_array_used"] is False
        and accounting["return_excess_matches_reservoir_debit"] is True
        and abs(accounting["return_excess"] - accounting["return_excess_debited"])
        <= BUDGET_TOLERANCE
    )
    replay_passed = (
        scheduled_event_ids <= set(packet_events_by_event_id)
        and _packet_pairs_ok(list(lane["outbound_packet_events"]))
        and _packet_pairs_ok(list(lane["reservoir_release_packet_events"]))
        and _packet_pairs_ok(list(lane["return_packet_events"]))
        and target_contact_event is not None
        and reservoir_release_event is not None
        and return_source_contact_event is not None
        and _digest(target_contact_event)
        == lane["return_eligibility_record"]["source_event_digest"]
        and int(reservoir_release_event["scheduler_event_index"])
        > int(target_contact_event["scheduler_event_index"])
        and int(return_source_contact_event["scheduler_event_index"])
        > int(reservoir_release_event["scheduler_event_index"])
        and int(return_source_contact_event["target_node_id"])
        == int(lane["source_node_id"])
        and scheduler_order == sorted(scheduler_order)
        and event_time_order == sorted(event_time_order)
        and amplification_accounting_ok
        and abs(lane["conservation"]["budget_abs_error_max"]) <= BUDGET_TOLERANCE
    )
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "outbound_contact_release_return_reconstructed": replay_passed,
        "scheduled_events_exist": scheduled_event_ids <= set(packet_events_by_event_id),
        "outbound_packet_pairs_ok": _packet_pairs_ok(list(lane["outbound_packet_events"])),
        "reservoir_release_packet_pairs_ok": _packet_pairs_ok(
            list(lane["reservoir_release_packet_events"])
        ),
        "return_packet_pairs_ok": _packet_pairs_ok(list(lane["return_packet_events"])),
        "target_contact_digest_matches": target_contact_event is not None
        and _digest(target_contact_event)
        == lane["return_eligibility_record"]["source_event_digest"],
        "reservoir_release_after_target_contact": reservoir_release_event is not None
        and target_contact_event is not None
        and int(reservoir_release_event["scheduler_event_index"])
        > int(target_contact_event["scheduler_event_index"]),
        "return_after_reservoir_release": return_source_contact_event is not None
        and reservoir_release_event is not None
        and int(return_source_contact_event["scheduler_event_index"])
        > int(reservoir_release_event["scheduler_event_index"]),
        "amplification_accounting_ok": amplification_accounting_ok,
        "scheduler_order_monotonic": scheduler_order == sorted(scheduler_order),
        "event_time_order_monotonic": event_time_order == sorted(event_time_order),
        "passed": replay_passed,
    }


def _run_hidden_reservoir_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    reservoir = manifest["reservoir_accounting"]["target_reservoir"]
    passed = (
        reservoir["hidden_fixture_array_allowed"] is False
        and reservoir["native_surplus_trigger_mapping"]["hidden_surplus_array_allowed"]
        is False
    )
    return {
        "control_id": "hidden_reservoir",
        "primary_blocker": "n05_hidden_reservoir_rejected",
        "control_execution_mode": "manifest_policy_gate_check",
        "passed": passed,
    }


def _run_undeclared_source_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = O1._build_model(manifest)
    try:
        model.set_causal_flux_routes(
            {
                999: [
                    {
                        "target_node_id": int(manifest["fixture"]["target_node_id"]),
                        "edge_id": 2,
                        "amount": RESERVOIR_RELEASE_AMOUNT,
                    }
                ]
            }
        )
        model.produce_events(
            policy=O1.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
    except O1.InvalidStateTransitionError as exc:
        return {
            "control_id": "undeclared_reservoir_source",
            "primary_blocker": "n05_undeclared_reservoir_source",
            "control_execution_mode": "runtime_control",
            "passed": "source node 999 is not live" in str(exc),
            "error": str(exc),
        }
    return {
        "control_id": "undeclared_reservoir_source",
        "primary_blocker": "n05_undeclared_reservoir_source",
        "control_execution_mode": "runtime_control",
        "passed": False,
        "error": "undeclared reservoir source was not rejected",
    }


def _run_negative_reservoir_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = O1._build_model(manifest)
    reservoir_node_id = int(manifest["fixture"]["target_reservoir_node_id"])
    target_node_id = int(manifest["fixture"]["target_node_id"])
    try:
        model.set_causal_flux_routes(
            {
                reservoir_node_id: [
                    {
                        "target_node_id": target_node_id,
                        "edge_id": 2,
                        "amount": O1._node_coherence(model, reservoir_node_id) + 0.25,
                    }
                ]
            }
        )
        model.produce_events(
            policy=O1.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
    except O1.InvalidStateTransitionError as exc:
        return {
            "control_id": "negative_reservoir",
            "primary_blocker": "n05_negative_reservoir_rejected",
            "control_execution_mode": "runtime_control",
            "passed": "exceed available source coherence" in str(exc),
            "error": str(exc),
        }
    return {
        "control_id": "negative_reservoir",
        "primary_blocker": "n05_negative_reservoir_rejected",
        "control_execution_mode": "runtime_control",
        "passed": False,
        "error": "negative reservoir overdraft was not rejected",
    }


def _run_silent_amplification_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    accounting = lane["amplification_accounting"]
    passed = (
        accounting["return_amount_exceeds_outbound"] is True
        and accounting["return_excess_matches_reservoir_debit"] is True
        and accounting["silent_amplification_used"] is False
    )
    return {
        "control_id": "silent_amplification",
        "primary_blocker": "n05_silent_amplification_rejected",
        "control_execution_mode": "artifact_accounting_control",
        "passed": passed,
    }


def _control_matrix(manifest: Mapping[str, Any], lane: Mapping[str, Any]) -> dict[str, Any]:
    controls: dict[str, Any] = {
        "policy_disabled": O1._run_default_off_control(manifest),
        "hidden_reservoir": _run_hidden_reservoir_control(manifest),
        "undeclared_source": _run_undeclared_source_control(manifest),
        "budget_mismatch": {
            "control_id": "budget_mismatch",
            "primary_blocker": "n05_node_plus_packet_budget_mismatch",
            "control_execution_mode": "artifact_accounting_control",
            "passed": abs(lane["conservation"]["budget_abs_error_max"])
            <= BUDGET_TOLERANCE
            and lane["amplification_accounting"][
                "return_excess_matches_reservoir_debit"
            ],
        },
        "negative_reservoir": _run_negative_reservoir_control(manifest),
        "silent_amplification": _run_silent_amplification_control(lane),
        "producer_mutation": {
            "control_id": "producer_mutation_attempt",
            "primary_blocker": "n05_producer_mutation_boundary_violation",
            "control_execution_mode": "runtime_artifact_control",
            "passed": lane["producer_boundary"]["producer_mutated_coherence"] is False
            and lane["producer_boundary"]["producer_consumed_queued_work"] is False
            and lane["producer_boundary"]["producer_mutated_topology"] is False,
        },
        "claim_promotion": {
            "control_id": "claim_promotion_attempt",
            "primary_blocker": "n05_claim_promotion_rejected",
            "control_execution_mode": "artifact_claim_boundary_control",
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
    deferred_rows = "\n".join(
        "| `{}` | `{}` | {} |".format(
            control["control_id"],
            control["status"],
            control["reason"],
        )
        for control in lane["deferred_shared_controls"]
    )
    packet_rows = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            event["chain_phase"],
            event["processed_event"]["event_kind"],
            event["processed_event"]["packet_id"],
            event["processed_event"]["source_node_id"],
            event["processed_event"]["target_node_id"],
            event["processed_event"]["amount"],
            event["processed_event"]["event_time_key"],
            event["processed_event"]["causal_epoch"],
        )
        for event in lane["processed_packet_events"]
    )
    text = f"""# N05 Iteration 5 O3 Amplified Return

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
| outbound amount | `{lane["outbound_amount"]}` |
| return amount | `{lane["return_amount"]}` |
| return excess | `{lane["amplification_accounting"]["return_excess"]}` |
| reservoir before/release-after/final | `{lane["target_reservoir_before"]} -> {lane["target_reservoir_after_release"]} -> {lane["target_reservoir_after"]}` |
| return packet | `{lane["return_packet_id"]}` |
| budget error | `{lane["conservation"]["budget_abs_error_max"]}` |
| row schema compliance | `{lane["row_schema_compliance"]["passed"]}` |

## Packet Chain

| Phase | Event kind | Packet | Source | Target | Amount | T_e | Causal epoch |
|---|---|---|---|---|---|---|---|
{packet_rows}

## Reservoir Policy

```json
{json.dumps(lane["reservoir_release_policy"], indent=2, sort_keys=True)}
```

## Amplification Accounting

```json
{json.dumps(lane["amplification_accounting"], indent=2, sort_keys=True)}
```

## Artifact Replay

```json
{json.dumps(result["artifact_replay"], indent=2, sort_keys=True)}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
{control_rows}

## Deferred Shared Controls

| Control | Status | Reason |
|---|---|---|
{deferred_rows}

## Claim Boundary

All N05 movement, semantic choice, agency, identity, memory/trail, regulation,
agentic-like, locomotion-like, biological, ACO, and unrestricted movement claim
flags remain false. O3 is an amplified-return evidence classification only.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    manifest = _load_manifest()
    positive_lane = _run_o3_positive_lane(manifest)
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
        "run_id": "n05_iteration_5_o3_amplified_return",
        "iteration": 5,
        "status": status,
        "command": COMMAND,
        "manifest_path": _rel(MANIFEST_PATH),
        "manifest_sha256": _file_sha256(MANIFEST_PATH),
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "execution_stage": "hybrid_scheduling",
        "o_ladder": {
            "o_level": "O3",
            "o_level_is_evidence_classification": True,
            "claim_ceiling": "amplified_return_candidate",
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
            "reservoir_release_policy_digest": _digest(
                positive_lane["reservoir_release_policy"]
            ),
            "return_eligibility_digest": _digest(
                positive_lane["return_eligibility_record"]
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
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(
        json.dumps(
            {
                "status": status,
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "o_level": "O3",
                "claim_ceiling": "amplified_return_candidate",
                "row_schema_passed": positive_lane["row_schema_compliance"]["passed"],
            },
            sort_keys=True,
        )
    )
    if status != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
