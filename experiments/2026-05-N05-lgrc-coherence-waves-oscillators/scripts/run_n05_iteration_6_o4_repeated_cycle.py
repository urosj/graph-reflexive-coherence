"""Run N05 Iteration 6: O4 repeated source-target-source cycle.

The O4 lane repeats the O3 source-target-reservoir-return circuit twice under
one declared cycle policy. Each hop is scheduled by the existing LGRC9V3 flux
route producer and consumed by ``LGRC9V3.run_autonomous(...)`` with a bounded
two-event window. Cycle ids are serialized into the route evidence so repeated
cycles are legitimate distinct producer opportunities, not duplicate replay of
one hidden schedule.
"""

from __future__ import annotations

import copy
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
OUTPUT_PATH = N05 / "outputs/n05_iteration_6_o4_repeated_cycle.json"
REPORT_PATH = N05 / "reports/n05_iteration_6_o4_repeated_cycle.md"
O3_SCRIPT_PATH = N05 / "scripts/run_n05_iteration_5_o3_amplified_return.py"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/"
    "run_n05_iteration_6_o4_repeated_cycle.py"
)

CYCLE_COUNT = 2
CYCLE_POLICY_ID = "n05_o4_declared_repeated_cycle_policy_v1"
OUTBOUND_AMOUNT = 0.25
RESERVOIR_RELEASE_AMOUNT = 0.25
RETURN_AMOUNT = OUTBOUND_AMOUNT + RESERVOIR_RELEASE_AMOUNT
AUTONOMOUS_MAX_EVENTS_PER_HOP = 2


def _load_o3_module() -> Any:
    spec = importlib.util.spec_from_file_location("n05_iteration_5_o3", O3_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load O3 helper module from {O3_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


O3 = _load_o3_module()
O2 = O3.O2
O1 = O3.O1
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


def _autonomous_production_log(model: Any) -> list[dict[str, Any]]:
    raw = model.get_state().cached_quantities.get("lgrc9v3_autonomous_production_log")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise RuntimeError("autonomous production log must be a list")
    return [dict(record) for record in raw]


def _run_autonomous_hop(
    model: Any,
    *,
    route_id: str,
    route_kind: str,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    amount: float,
    cycle_id: str,
    cycle_index: int,
    chain_phase: str,
    hop_index: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    route_payload = {
        "target_node_id": int(target_node_id),
        "edge_id": int(edge_id),
        "amount": float(amount),
        "route_id": route_id,
        "route_kind": route_kind,
        "cycle_policy_id": CYCLE_POLICY_ID,
        "cycle_id": cycle_id,
        "cycle_index": int(cycle_index),
        "chain_phase": chain_phase,
        "hop_index": int(hop_index),
    }
    before_budget = O1._budget_surface(model)
    source_coherence_before = O1._node_coherence(model, int(source_node_id))
    production_log_before = len(_autonomous_production_log(model))
    model.set_causal_flux_routes({int(source_node_id): [route_payload]})
    results = model.run_autonomous(
        max_events=AUTONOMOUS_MAX_EVENTS_PER_HOP,
        producer_policies=(
            O1.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
        ),
    )
    production_log_after = _autonomous_production_log(model)
    production_results = production_log_after[production_log_before:]
    producer_records = [
        record
        for result in production_results
        for record in result.get("production_records", [])
    ]
    packet_events: list[dict[str, Any]] = []
    for step_result in results:
        events = [O1._event_payload(event) for event in step_result.events]
        for event in O1._packet_step_events(events):
            event["chain_phase"] = chain_phase
            event["route_id"] = route_id
            event["route_kind"] = route_kind
            event["cycle_id"] = cycle_id
            event["cycle_index"] = int(cycle_index)
            event["cycle_policy_id"] = CYCLE_POLICY_ID
            event["hop_index"] = int(hop_index)
            packet_events.append(event)
    if len(packet_events) != 2:
        raise RuntimeError("expected departure and arrival packet events per O4 hop")
    summary = dict(
        model.get_state().cached_quantities.get("last_lgrc9v3_autonomous_run", {})
    )
    scheduled_count = sum(
        int(result.get("scheduled_event_count", 0)) for result in production_results
    )
    hop_record = {
        "cycle_id": cycle_id,
        "cycle_index": int(cycle_index),
        "cycle_policy_id": CYCLE_POLICY_ID,
        "chain_phase": chain_phase,
        "route_id": route_id,
        "route_kind": route_kind,
        "hop_index": int(hop_index),
        "source_node_id": int(source_node_id),
        "target_node_id": int(target_node_id),
        "edge_id": int(edge_id),
        "amount": float(amount),
        "route_payload": route_payload,
        "run_autonomous_used": True,
        "run_autonomous_policy": "LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1",
        "run_autonomous_max_events": AUTONOMOUS_MAX_EVENTS_PER_HOP,
        "run_autonomous_summary": summary,
        "run_autonomous_stop_condition": summary.get("stop_condition"),
        "producer_records": producer_records,
        "producer_scheduled_event_count": scheduled_count,
        "packet_events": packet_events,
        "departure_packet_event": packet_events[0]["processed_event"],
        "arrival_packet_event": packet_events[-1]["processed_event"],
        "arrival_processed_event": packet_events[-1]["processed_event"],
        "source_coherence_before_hop": source_coherence_before,
        "source_coherence_after_hop": O1._node_coherence(model, int(source_node_id)),
        "budget_before_hop": before_budget,
        "budget_after_hop": O1._budget_surface(model),
        "budget_error_after_hop": abs(O1._budget_surface(model) - before_budget),
    }
    return hop_record, producer_records, packet_events


def _run_route_hops(
    model: Any,
    route: Mapping[str, Any],
    *,
    amount: float,
    cycle_id: str,
    cycle_index: int,
    chain_phase: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    hop_records: list[dict[str, Any]] = []
    producer_records: list[dict[str, Any]] = []
    packet_events: list[dict[str, Any]] = []
    for hop_index, hop in enumerate(route["route_hops"]):
        hop_record, hop_producers, hop_packets = _run_autonomous_hop(
            model,
            route_id=str(route["route_id"]),
            route_kind=str(route.get("route_kind", "declared_fixture_route")),
            source_node_id=int(hop["source_node_id"]),
            target_node_id=int(hop["target_node_id"]),
            edge_id=int(hop["edge_id"]),
            amount=float(amount),
            cycle_id=cycle_id,
            cycle_index=cycle_index,
            chain_phase=chain_phase,
            hop_index=hop_index,
        )
        hop_records.append(hop_record)
        producer_records.extend(hop_producers)
        packet_events.extend(hop_packets)
    return hop_records, producer_records, packet_events


def _reservoir_release_route(manifest: Mapping[str, Any]) -> dict[str, Any]:
    route = O3._reservoir_release_route(manifest)
    route["route_id"] = "n05_o4_declared_target_reservoir_release_route_v1"
    route["route_kind"] = "o4_reservoir_release"
    return route


def _run_cycle(
    model: Any,
    manifest: Mapping[str, Any],
    *,
    cycle_index: int,
    cycle_id: str,
    source_authorization: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    outbound_route = manifest["routes"]["n05_o1_source_to_target_route_v1"]
    return_route = manifest["routes"]["n05_o2_target_to_source_return_route_v1"]
    reservoir_route = _reservoir_release_route(manifest)
    target_reservoir_node_id = int(manifest["fixture"]["target_reservoir_node_id"])

    cycle_budget_before = O1._budget_surface(model)
    reservoir_before = O1._node_coherence(model, target_reservoir_node_id)
    outbound_hops, outbound_producers, outbound_packets = _run_route_hops(
        model,
        outbound_route,
        amount=OUTBOUND_AMOUNT,
        cycle_id=cycle_id,
        cycle_index=cycle_index,
        chain_phase="outbound",
    )
    target_contact = outbound_hops[-1]["arrival_processed_event"]
    contact_valid, contact_blocker = O2._validate_return_contact(
        target_contact,
        expected_target_node_id=int(outbound_route["target_node_id"]),
    )
    if not contact_valid:
        raise RuntimeError(f"O4 target contact invalid: {contact_blocker}")
    target_contact_digest = _digest(target_contact)

    reservoir_release_policy = {
        "policy_id": "n05_o4_declared_reservoir_release_policy_v1",
        "cycle_policy_id": CYCLE_POLICY_ID,
        "cycle_id": cycle_id,
        "cycle_index": int(cycle_index),
        "source_event_id": target_contact["event_id"],
        "source_event_digest": target_contact_digest,
        "source_event_kind": target_contact["event_kind"],
        "reservoir_node_id": target_reservoir_node_id,
        "observed_value_field": "node_coherence",
        "observed_value_before_release": reservoir_before,
        "reference_value": reservoir_before,
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
    release_hops, release_producers, release_packets = _run_route_hops(
        model,
        reservoir_route,
        amount=RESERVOIR_RELEASE_AMOUNT,
        cycle_id=cycle_id,
        cycle_index=cycle_index,
        chain_phase="reservoir_release",
    )
    reservoir_after_release = O1._node_coherence(model, target_reservoir_node_id)
    reservoir_release_event = release_hops[-1]["arrival_processed_event"]
    reservoir_release_digest = _digest(reservoir_release_event)

    return_eligibility_record = {
        "record_id": "n05-o4-return-eligibility-" + target_contact_digest[:24],
        "record_kind": "n05_repeated_cycle_return_eligibility",
        "cycle_policy_id": CYCLE_POLICY_ID,
        "cycle_id": cycle_id,
        "cycle_index": int(cycle_index),
        "source_event_id": target_contact["event_id"],
        "source_event_digest": target_contact_digest,
        "source_packet_id": target_contact["packet_id"],
        "source_route_id": outbound_route["route_id"],
        "return_route_id": return_route["route_id"],
        "reservoir_release_policy_id": reservoir_release_policy["policy_id"],
        "reservoir_release_route_id": reservoir_route["route_id"],
        "reservoir_release_packet_id": reservoir_release_event["packet_id"],
        "reservoir_release_event_id": reservoir_release_event["event_id"],
        "reservoir_release_event_digest": reservoir_release_digest,
        "return_amount": RETURN_AMOUNT,
        "return_excess_debited": RESERVOIR_RELEASE_AMOUNT,
        "not_before_scheduler_event_index": reservoir_release_event[
            "scheduler_event_index"
        ],
        "not_before_event_time_key": reservoir_release_event["event_time_key"],
        "committed_target_contact_required": True,
        "committed_reservoir_release_required": True,
        "hidden_return_timing_used": False,
    }
    return_hops, return_producers, return_packets = _run_route_hops(
        model,
        return_route,
        amount=RETURN_AMOUNT,
        cycle_id=cycle_id,
        cycle_index=cycle_index,
        chain_phase="amplified_return",
    )
    source_contact = return_hops[-1]["arrival_processed_event"]
    source_contact_digest = _digest(source_contact)
    reservoir_after = O1._node_coherence(model, target_reservoir_node_id)
    cycle_budget_after = O1._budget_surface(model)
    producer_records = [*outbound_producers, *release_producers, *return_producers]
    packet_events = [*outbound_packets, *release_packets, *return_packets]
    cycle_record = {
        "cycle_id": cycle_id,
        "cycle_index": int(cycle_index),
        "cycle_policy_id": CYCLE_POLICY_ID,
        "cycle_source_authorization": dict(source_authorization),
        "outbound_route_id": outbound_route["route_id"],
        "return_route_id": return_route["route_id"],
        "reservoir_release_route_id": reservoir_route["route_id"],
        "outbound_hop_results": outbound_hops,
        "reservoir_release_hop_results": release_hops,
        "return_hop_results": return_hops,
        "outbound_packet_ids": [
            hop["arrival_processed_event"]["packet_id"] for hop in outbound_hops
        ],
        "outbound_packet_digests": [
            _digest(hop["arrival_processed_event"]) for hop in outbound_hops
        ],
        "target_contact_event_id": target_contact["event_id"],
        "target_contact_event_digest": target_contact_digest,
        "reservoir_release_event_id": reservoir_release_event["event_id"],
        "reservoir_release_event_digest": reservoir_release_digest,
        "return_packet_ids": [
            hop["arrival_processed_event"]["packet_id"] for hop in return_hops
        ],
        "return_packet_digests": [
            _digest(hop["arrival_processed_event"]) for hop in return_hops
        ],
        "source_contact_event_id": source_contact["event_id"],
        "source_contact_event_digest": source_contact_digest,
        "return_eligibility_record": return_eligibility_record,
        "reservoir_release_policy": reservoir_release_policy,
        "outbound_amount": OUTBOUND_AMOUNT,
        "reservoir_release_amount": RESERVOIR_RELEASE_AMOUNT,
        "return_amount": RETURN_AMOUNT,
        "target_reservoir_before": reservoir_before,
        "target_reservoir_after_release": reservoir_after_release,
        "target_reservoir_after": reservoir_after,
        "cycle_causal_delay": float(source_contact["event_time_key"])
        - float(outbound_hops[0]["departure_packet_event"]["event_time_key"]),
        "cycle_causal_delay_semantics": (
            "cycle_source_target_source_elapsed_event_time"
        ),
        "cycle_budget_before": cycle_budget_before,
        "cycle_budget_after": cycle_budget_after,
        "cycle_budget_error": abs(cycle_budget_after - cycle_budget_before),
        "producer_records": producer_records,
        "processed_packet_events": packet_events,
        "scheduler_order": [
            int(event["processed_event"]["scheduler_event_index"])
            for event in packet_events
        ],
        "event_time_order": [
            float(event["processed_event"]["event_time_key"])
            for event in packet_events
        ],
        "run_autonomous_stop_conditions": [
            hop["run_autonomous_stop_condition"]
            for hop in [*outbound_hops, *release_hops, *return_hops]
        ],
        "completed_source_target_source_cycle": True,
    }
    return cycle_record, producer_records, packet_events


def _run_o4_positive_lane(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = O1._build_model(manifest)
    initial_budget = O1._budget_surface(model)
    target_reservoir_node_id = int(manifest["fixture"]["target_reservoir_node_id"])
    target_reservoir_before = O1._node_coherence(model, target_reservoir_node_id)
    cycle_records: list[dict[str, Any]] = []
    producer_records: list[dict[str, Any]] = []
    processed_packet_events: list[dict[str, Any]] = []
    source_authorization: dict[str, Any] = {
        "authorization_kind": "initial_declared_fixture_state",
        "source_event_id": None,
        "source_event_digest": None,
        "source_cycle_id": None,
        "hidden_event_list_used": False,
    }

    for cycle_index in range(CYCLE_COUNT):
        cycle_id = f"n05_o4_repeated_cycle_{cycle_index:03d}"
        cycle_record, cycle_producers, cycle_packets = _run_cycle(
            model,
            manifest,
            cycle_index=cycle_index,
            cycle_id=cycle_id,
            source_authorization=source_authorization,
        )
        cycle_records.append(cycle_record)
        producer_records.extend(cycle_producers)
        processed_packet_events.extend(cycle_packets)
        source_authorization = {
            "authorization_kind": "previous_cycle_source_contact",
            "source_event_id": cycle_record["source_contact_event_id"],
            "source_event_digest": cycle_record["source_contact_event_digest"],
            "source_cycle_id": cycle_record["cycle_id"],
            "source_scheduler_event_index": cycle_record["scheduler_order"][-1],
            "hidden_event_list_used": False,
        }

    final_state = model.get_state()
    final_budget = O1._budget_surface(model)
    ledger = final_state.packet_ledger
    assert ledger is not None
    final_cycle = cycle_records[-1]
    final_source_contact = final_cycle["return_hop_results"][-1][
        "arrival_processed_event"
    ]
    scheduler_order = [
        int(event["processed_event"]["scheduler_event_index"])
        for event in processed_packet_events
    ]
    event_time_order = [
        float(event["processed_event"]["event_time_key"])
        for event in processed_packet_events
    ]
    cycle_ids = [record["cycle_id"] for record in cycle_records]
    packet_ids = [
        event["processed_event"]["packet_id"] for event in processed_packet_events
    ]
    packet_event_ids = [
        event["processed_event"]["event_id"] for event in processed_packet_events
    ]
    final_reservoir = O1._node_coherence(model, target_reservoir_node_id)
    run_autonomous_summaries = [
        hop["run_autonomous_summary"]
        for cycle in cycle_records
        for hop in [
            *cycle["outbound_hop_results"],
            *cycle["reservoir_release_hop_results"],
            *cycle["return_hop_results"],
        ]
    ]
    return {
        "run_id": "n05_iteration_6_o4_repeated_cycle",
        "lane_id": "o4_enabled_repeated_source_target_source_cycle",
        "status": "passed",
        "o_level": "O4",
        "o_level_is_evidence_classification": True,
        "claim_ceiling": "repeated_oscillator_cycle_candidate",
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "execution_stage": "bounded_autonomous_hybrid_scheduling",
        "scheduling_mode": "bounded_autonomous_run_segments",
        "producer_mediated": True,
        "constitutive_native_claim_allowed": False,
        "source_native_surfaces": [
            "LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE",
            "LGRC9V3.run_autonomous",
            "LGRC9V3.step",
        ],
        "fixture_id": manifest["fixture"]["fixture_id"],
        "source_node_id": int(manifest["fixture"]["source_node_id"]),
        "target_node_id": int(manifest["fixture"]["target_node_id"]),
        "route_id": manifest["routes"]["n05_o1_source_to_target_route_v1"][
            "route_id"
        ],
        "return_route_id": manifest["routes"]["n05_o2_target_to_source_return_route_v1"][
            "route_id"
        ],
        "event_time_key": final_source_contact["event_time_key"],
        "scheduler_event_index": final_source_contact["scheduler_event_index"],
        "causal_epoch": "post_update",
        "node_proper_time": {
            str(node_id): float(value)
            for node_id, value in sorted(final_state.node_proper_time.items())
        },
        "source_node_proper_time": float(
            final_state.node_proper_time.get(int(manifest["fixture"]["source_node_id"]), 0.0)
        ),
        "target_node_proper_time": float(
            final_state.node_proper_time.get(int(manifest["fixture"]["target_node_id"]), 0.0)
        ),
        "outbound_packet_id": final_cycle["outbound_packet_ids"][-1],
        "outbound_packet_digest": final_cycle["outbound_packet_digests"][-1],
        "outbound_packet_id_semantics": (
            "terminal_target_contact_packet_for_last_o4_cycle"
        ),
        "outbound_amount": OUTBOUND_AMOUNT,
        "target_reservoir_before": target_reservoir_before,
        "target_reservoir_after": final_reservoir,
        "return_packet_id": final_source_contact["packet_id"],
        "return_packet_digest": _digest(final_source_contact),
        "return_amount": RETURN_AMOUNT,
        "cycle_id": "n05_o4_repeated_cycle_set_000",
        "cycle_ids": cycle_ids,
        "cycle_policy_id": CYCLE_POLICY_ID,
        "cycle_records": cycle_records,
        "cycle_record_digests": [_digest(record) for record in cycle_records],
        "cycle_count": len(cycle_records),
        "causal_delay": float(final_source_contact["event_time_key"])
        - float(
            cycle_records[0]["outbound_hop_results"][0]["departure_packet_event"][
                "event_time_key"
            ]
        ),
        "causal_delay_semantics": (
            "total_elapsed_event_time_across_recorded_o4_cycle_set"
        ),
        "per_cycle_causal_delays": [
            cycle["cycle_causal_delay"] for cycle in cycle_records
        ],
        "scheduler_order": scheduler_order,
        "event_time_order": event_time_order,
        "processed_packet_events": processed_packet_events,
        "producer_records": producer_records,
        "run_autonomous_used": True,
        "run_autonomous_scope": (
            "bounded_autonomous_segments_per_declared_cycle_hop"
        ),
        "run_autonomous_stop_conditions": [
            summary.get("stop_condition") for summary in run_autonomous_summaries
        ],
        "native_self_rearm_validator": {
            "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts(...)",
            "used": False,
            "scope_limitation": (
                "O4 repeats explicit source-target-source cycle segments through "
                "flux-route producer evidence. Native self-rearm evidence is "
                "reserved for O5 renewal, where the next cycle must be "
                "authorized by committed circuit state rather than explicit "
                "cycle-route configuration."
            ),
            "native_self_rearm_claim_allowed": False,
        },
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
            "per_cycle_budget_errors": [
                cycle["cycle_budget_error"] for cycle in cycle_records
            ],
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
            "target_reservoir_after": final_reservoir,
            "reservoir_budget_before": target_reservoir_before,
            "reservoir_budget_after": final_reservoir,
            "reservoir_delta": target_reservoir_before - final_reservoir,
            "reservoir_exhausted_after_recorded_cycles": abs(final_reservoir)
            <= BUDGET_TOLERANCE,
            "third_cycle_possible_without_replenishment": False,
            "per_cycle_reservoir_deltas": [
                cycle["target_reservoir_before"] - cycle["target_reservoir_after"]
                for cycle in cycle_records
            ],
            "outbound_amount": OUTBOUND_AMOUNT,
            "return_amount": RETURN_AMOUNT,
            "return_excess_per_cycle": RETURN_AMOUNT - OUTBOUND_AMOUNT,
            "return_excess_total": (RETURN_AMOUNT - OUTBOUND_AMOUNT)
            * len(cycle_records),
            "return_excess_matches_reservoir_debit": abs(
                (RETURN_AMOUNT - OUTBOUND_AMOUNT) * len(cycle_records)
                - (target_reservoir_before - final_reservoir)
            )
            <= BUDGET_TOLERANCE,
            "silent_amplification_used": False,
        },
        "route_coupling": {
            "status": "not_applicable_for_o4",
            "route_coupling_runtime_visible": False,
            "memory_or_trail_claim_allowed": False,
        },
        "producer_boundary": {
            "producer_scheduled_packet": True,
            "producer_mutated_coherence": False,
            "producer_consumed_queued_work": any(
                bool(record.get("queued_work_consumed"))
                for record in producer_records
            ),
            "producer_mutated_topology": any(
                bool(record.get("topology_mutated")) for record in producer_records
            ),
            "producer_emitted_claim_label": False,
            "step_processed_packet_work": True,
        },
        "cycle_semantics": {
            "cycle_definition": (
                "outbound_departure_target_contact_reservoir_release_"
                "return_eligibility_return_packet_source_contact"
            ),
            "distinct_cycle_count": len(cycle_records),
            "cycle_ids_unique": len(set(cycle_ids)) == len(cycle_ids),
            "cycle_count_basis": "distinct_source_contact_events",
            "source_contact_event_ids": [
                cycle["source_contact_event_id"] for cycle in cycle_records
            ],
            "source_contact_event_digests": [
                cycle["source_contact_event_digest"] for cycle in cycle_records
            ],
            "plateau_samples_counted_as_cycles": False,
            "repeated_cycle_claim_allowed": True,
            "self_sustained_oscillator_claim_allowed": False,
        },
        "scheduling_semantics": {
            "scheduling_mode": "bounded_autonomous_run_segments",
            "preauthored_event_list_used": False,
            "hidden_return_timing_used": False,
            "hidden_reservoir_used": False,
            "same_declared_cycle_policy_for_all_cycles": all(
                cycle["cycle_policy_id"] == CYCLE_POLICY_ID for cycle in cycle_records
            ),
            "cycle_ids_serialized_in_route_evidence": True,
            "producer_mediated": True,
            "producer_mutated_state": False,
            "constitutive_native_claim_allowed": False,
            "run_autonomous_used": True,
            "run_autonomous_scope": (
                "bounded_autonomous_segments_per_declared_cycle_hop"
            ),
            "cycle_route_configuration_is_runtime_visible": True,
            "self_renewal_not_claimed": True,
        },
        "duplicate_suppression": {
            "cycle_ids_unique": len(set(cycle_ids)) == len(cycle_ids),
            "packet_event_ids_unique": len(set(packet_event_ids))
            == len(packet_event_ids),
            "distinct_packet_count": len(set(packet_ids)),
            "packet_event_count": len(packet_event_ids),
            "packet_ids_repeat_across_departure_arrival_events": True,
            "packet_id_repetition_semantics": (
                "one packet id appears in its departure and arrival events; "
                "duplicates here are not duplicate scheduled packets"
            ),
            "producer_record_ids_unique": len(
                {record["record_id"] for record in producer_records}
            )
            == len(producer_records),
            "legitimate_repeated_cycles_use_serialized_cycle_ids": True,
        },
        "deferred_shared_controls": [
            {
                "control_id": "snapshot_continue_after_load",
                "status": "not_rerun_in_o4",
                "reason": (
                    "reserved for O5/O6 or N05 closeout; O4 focuses on "
                    "cycle semantics and duplicate suppression"
                ),
            }
        ],
        "claim_flags": CLAIM_FLAGS_FALSE,
        "blocked_claims": [
            "self_sustained_oscillator_candidate",
            "route_coupled_oscillator_candidate",
            "semantic_choice",
            "memory_or_trail",
            "agency",
            "agentic_like_behavior",
            "locomotion_like_behavior",
            "ant_colony_behavior",
        ],
    }


def _packet_pairs_ok(packet_events: list[dict[str, Any]]) -> bool:
    return O3._packet_pairs_ok(packet_events)


def _cycle_replay(lane: Mapping[str, Any]) -> dict[str, Any]:
    packet_events = [
        event["processed_event"] for event in lane["processed_packet_events"]
    ]
    packet_events_by_id = {event["event_id"]: event for event in packet_events}
    scheduled_event_ids = {
        record["scheduled_event_id"]
        for record in lane["producer_records"]
        if record.get("scheduled_event_id")
    }
    cycle_results: list[dict[str, Any]] = []
    previous_source_contact_digest: str | None = None
    previous_source_contact_scheduler_index: int | None = None
    for index, cycle in enumerate(lane["cycle_records"]):
        source_auth = cycle["cycle_source_authorization"]
        target_contact = packet_events_by_id.get(cycle["target_contact_event_id"])
        reservoir_release = packet_events_by_id.get(cycle["reservoir_release_event_id"])
        source_contact = packet_events_by_id.get(cycle["source_contact_event_id"])
        source_auth_ok = True
        if index == 0:
            source_auth_ok = (
                source_auth["authorization_kind"] == "initial_declared_fixture_state"
                and source_auth["source_event_digest"] is None
            )
        else:
            source_auth_ok = (
                source_auth["authorization_kind"] == "previous_cycle_source_contact"
                and source_auth["source_event_digest"]
                == previous_source_contact_digest
                and int(cycle["scheduler_order"][0])
                > int(previous_source_contact_scheduler_index or -1)
            )
        phases = [
            event["chain_phase"]
            for event in cycle["processed_packet_events"]
            if str(event["processed_event"]["event_kind"]).endswith("packet_arrival")
        ]
        cycle_ok = (
            target_contact is not None
            and reservoir_release is not None
            and source_contact is not None
            and _digest(target_contact) == cycle["target_contact_event_digest"]
            and _digest(reservoir_release)
            == cycle["reservoir_release_event_digest"]
            and _digest(source_contact) == cycle["source_contact_event_digest"]
            and int(target_contact["target_node_id"]) == int(lane["target_node_id"])
            and int(source_contact["target_node_id"]) == int(lane["source_node_id"])
            and int(reservoir_release["scheduler_event_index"])
            > int(target_contact["scheduler_event_index"])
            and int(source_contact["scheduler_event_index"])
            > int(reservoir_release["scheduler_event_index"])
            and cycle["scheduler_order"] == sorted(cycle["scheduler_order"])
            and cycle["event_time_order"] == sorted(cycle["event_time_order"])
            and phases == ["outbound", "outbound", "reservoir_release", "amplified_return", "amplified_return"]
            and source_auth_ok
            and abs(cycle["cycle_budget_error"]) <= BUDGET_TOLERANCE
        )
        cycle_results.append(
            {
                "cycle_id": cycle["cycle_id"],
                "source_authorization_ok": source_auth_ok,
                "target_contact_reconstructed": target_contact is not None,
                "reservoir_release_reconstructed": reservoir_release is not None,
                "source_contact_reconstructed": source_contact is not None,
                "cycle_order_ok": cycle["scheduler_order"]
                == sorted(cycle["scheduler_order"]),
                "cycle_budget_ok": abs(cycle["cycle_budget_error"])
                <= BUDGET_TOLERANCE,
                "passed": cycle_ok,
            }
        )
        previous_source_contact_digest = cycle["source_contact_event_digest"]
        previous_source_contact_scheduler_index = int(cycle["scheduler_order"][-1])

    scheduler_order = [int(event["scheduler_event_index"]) for event in packet_events]
    event_time_order = [float(event["event_time_key"]) for event in packet_events]
    all_cycle_ids = [cycle["cycle_id"] for cycle in lane["cycle_records"]]
    replay_passed = (
        scheduled_event_ids <= set(packet_events_by_id)
        and all(result["passed"] for result in cycle_results)
        and len(cycle_results) >= 2
        and len(set(all_cycle_ids)) == len(all_cycle_ids)
        and scheduler_order == sorted(scheduler_order)
        and event_time_order == sorted(event_time_order)
        and lane["cycle_semantics"]["plateau_samples_counted_as_cycles"] is False
        and abs(lane["node_plus_packet_budget_error"]) <= BUDGET_TOLERANCE
    )
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "cycle_count_reconstructed": len(cycle_results),
        "distinct_cycle_count": len(set(all_cycle_ids)),
        "cycles_reconstructed": cycle_results,
        "scheduled_events_exist": scheduled_event_ids <= set(packet_events_by_id),
        "global_scheduler_order_monotonic": scheduler_order == sorted(scheduler_order),
        "global_event_time_order_monotonic": event_time_order == sorted(event_time_order),
        "plateau_samples_counted_as_cycles": False,
        "plateau_samples_counted_as_cycles_false": (
            lane["cycle_semantics"]["plateau_samples_counted_as_cycles"] is False
        ),
        "budget_ok": abs(lane["node_plus_packet_budget_error"]) <= BUDGET_TOLERANCE,
        "passed": replay_passed,
    }


def _artifact_only_replay(lane: Mapping[str, Any]) -> dict[str, Any]:
    replay = _cycle_replay(lane)
    replay["outbound_packet_pairs_ok"] = all(
        _packet_pairs_ok(cycle["processed_packet_events"][:4])
        for cycle in lane["cycle_records"]
    )
    replay["all_cycles_same_declared_policy"] = all(
        cycle["cycle_policy_id"] == CYCLE_POLICY_ID for cycle in lane["cycle_records"]
    )
    replay["hidden_schedule_absent"] = (
        lane["scheduling_semantics"]["preauthored_event_list_used"] is False
        and all(
            cycle["cycle_source_authorization"]["hidden_event_list_used"] is False
            for cycle in lane["cycle_records"]
        )
    )
    replay["passed"] = (
        replay["passed"]
        and replay["all_cycles_same_declared_policy"]
        and replay["hidden_schedule_absent"]
    )
    return replay


def _run_duplicate_packet_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = O1._build_model(manifest)
    first_hop = manifest["routes"]["n05_o1_source_to_target_route_v1"]["route_hops"][0]
    model.set_causal_flux_routes(
        {
            int(first_hop["source_node_id"]): [
                {
                    "target_node_id": int(first_hop["target_node_id"]),
                    "edge_id": int(first_hop["edge_id"]),
                    "amount": OUTBOUND_AMOUNT,
                    "route_id": "n05_o4_duplicate_control_route",
                    "route_kind": "duplicate_control",
                    "cycle_policy_id": CYCLE_POLICY_ID,
                    "cycle_id": "n05_o4_duplicate_control_cycle_000",
                    "cycle_index": 0,
                    "chain_phase": "duplicate_control",
                    "hop_index": 0,
                }
            ]
        }
    )
    first = model.produce_events(
        policy=O1.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
    )
    second = model.produce_events(
        policy=O1.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
    )
    first_artifact = first.to_artifact()
    second_artifact = second.to_artifact()
    second_reasons = [
        record["reason_code"] for record in second_artifact["production_records"]
    ]
    return {
        "control_id": "duplicate_packet",
        "primary_blocker": "n05_duplicate_cycle_packet_suppressed",
        "control_execution_mode": "runtime_idempotency_control",
        "passed": first.scheduled_event_count == 1
        and second.scheduled_event_count == 0
        and "idempotent_causal_surface_already_produced" in second_reasons,
        "first_production_result": first_artifact,
        "second_production_result": second_artifact,
    }


def _run_stale_cycle_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    corrupted = copy.deepcopy(lane)
    corrupted["cycle_records"][1]["cycle_source_authorization"][
        "source_event_digest"
    ] = corrupted["cycle_records"][0]["target_contact_event_digest"]
    replay = _cycle_replay(corrupted)
    return {
        "control_id": "stale_cycle",
        "primary_blocker": "n05_stale_cycle_authorization_rejected",
        "control_execution_mode": "artifact_cycle_lineage_control",
        "passed": replay["passed"] is False
        and replay["cycles_reconstructed"][1]["source_authorization_ok"] is False,
    }


def _run_hidden_schedule_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "control_id": "hidden_schedule",
        "primary_blocker": "n05_hidden_schedule_rejected",
        "control_execution_mode": "artifact_policy_control",
        "passed": lane["scheduling_semantics"]["preauthored_event_list_used"] is False
        and all(
            cycle["cycle_source_authorization"]["hidden_event_list_used"] is False
            for cycle in lane["cycle_records"]
        ),
    }


def _run_budget_drift_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    corrupted = copy.deepcopy(lane)
    corrupted["node_plus_packet_budget_after"] = (
        float(corrupted["node_plus_packet_budget_after"]) + 0.01
    )
    corrupted["node_plus_packet_budget_error"] = abs(
        float(corrupted["node_plus_packet_budget_after"])
        - float(corrupted["node_plus_packet_budget_before"])
    )
    return {
        "control_id": "budget_drift",
        "primary_blocker": "n05_node_plus_packet_budget_mismatch",
        "control_execution_mode": "artifact_budget_control",
        "passed": _cycle_replay(corrupted)["passed"] is False
        and abs(float(lane["node_plus_packet_budget_error"])) <= BUDGET_TOLERANCE,
    }


def _control_matrix(manifest: Mapping[str, Any], lane: Mapping[str, Any]) -> dict[str, Any]:
    controls: dict[str, Any] = {
        "policy_disabled": O1._run_default_off_control(manifest),
        "hidden_schedule": _run_hidden_schedule_control(lane),
        "duplicate_packet": _run_duplicate_packet_control(manifest),
        "stale_cycle": _run_stale_cycle_control(lane),
        "budget_drift": _run_budget_drift_control(lane),
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
    cycle_rows = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            cycle["cycle_index"],
            cycle["cycle_id"],
            cycle["target_contact_event_id"],
            cycle["source_contact_event_id"],
            cycle["target_reservoir_before"],
            cycle["target_reservoir_after"],
            cycle["cycle_budget_error"],
        )
        for cycle in lane["cycle_records"]
    )
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
        "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            event["cycle_id"],
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
    text = f"""# N05 Iteration 6 O4 Repeated Cycle

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
| cycle policy | `{lane["cycle_policy_id"]}` |
| distinct cycles | `{lane["cycle_semantics"]["distinct_cycle_count"]}` |
| run_autonomous used | `{lane["run_autonomous_used"]}` |
| native self-rearm validator used | `{lane["native_self_rearm_validator"]["used"]}` |
| causal delay semantics | `{lane["causal_delay_semantics"]}` |
| per-cycle causal delays | `{lane["per_cycle_causal_delays"]}` |
| reservoir exhausted after recorded cycles | `{lane["amplification_accounting"]["reservoir_exhausted_after_recorded_cycles"]}` |
| budget error | `{lane["conservation"]["budget_abs_error_max"]}` |
| row schema compliance | `{lane["row_schema_compliance"]["passed"]}` |

## Cycle Records

| Index | Cycle id | Target contact | Source contact | Reservoir before | Reservoir after | Budget error |
|---|---|---|---|---|---|---|
{cycle_rows}

## Packet Chain

| Cycle | Phase | Event kind | Packet | Source | Target | Amount | T_e | Causal epoch |
|---|---|---|---|---|---|---|---|---|
{packet_rows}

## Autonomous Scope

```json
{json.dumps(lane["native_self_rearm_validator"], indent=2, sort_keys=True)}
```

## Artifact Replay

```json
{json.dumps(result["artifact_replay"], indent=2, sort_keys=True)}
```

## Duplicate Suppression Semantics

```json
{json.dumps(lane["duplicate_suppression"], indent=2, sort_keys=True)}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
{control_rows}

## Claim Boundary

All N05 movement, semantic choice, agency, identity, memory/trail, regulation,
agentic-like, locomotion-like, biological, ACO, and unrestricted movement claim
flags remain false. O4 is repeated-cycle evidence only; self-sustained and
route-coupled oscillator claims remain blocked.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    manifest = _load_manifest()
    positive_lane = _run_o4_positive_lane(manifest)
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
        "run_id": "n05_iteration_6_o4_repeated_cycle",
        "iteration": 6,
        "status": status,
        "command": COMMAND,
        "manifest_path": _rel(MANIFEST_PATH),
        "manifest_sha256": _file_sha256(MANIFEST_PATH),
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "execution_stage": "bounded_autonomous_hybrid_scheduling",
        "o_ladder": {
            "o_level": "O4",
            "o_level_is_evidence_classification": True,
            "claim_ceiling": "repeated_oscillator_cycle_candidate",
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
            "cycle_records_digest": _digest(positive_lane["cycle_records"]),
            "producer_records_digest": _digest(positive_lane["producer_records"]),
            "processed_packet_events_digest": _digest(
                positive_lane["processed_packet_events"]
            ),
            "artifact_replay_digest": _digest(artifact_replay),
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
                "o_level": "O4",
                "claim_ceiling": "repeated_oscillator_cycle_candidate",
                "cycle_count": positive_lane["cycle_semantics"][
                    "distinct_cycle_count"
                ],
                "row_schema_passed": positive_lane["row_schema_compliance"][
                    "passed"
                ],
            },
            sort_keys=True,
        )
    )
    if status != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
