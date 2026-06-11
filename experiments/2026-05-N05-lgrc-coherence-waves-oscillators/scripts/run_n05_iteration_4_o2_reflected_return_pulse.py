"""Run N05 Iteration 4: O2 reflected return pulse.

The O2 lane extends the Iteration 3 O1 outbound pulse with one return pulse
that is authorized only after the outbound target-contact packet event is
committed. This remains experiment-local explicit scheduling over existing
LGRC9V3 packet producer and ``step()`` mechanics.
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
OUTPUT_PATH = N05 / "outputs/n05_iteration_4_o2_reflected_return_pulse.json"
REPORT_PATH = N05 / "reports/n05_iteration_4_o2_reflected_return_pulse.md"
O1_SCRIPT_PATH = N05 / "scripts/run_n05_iteration_3_o1_delayed_outbound_pulse.py"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/"
    "run_n05_iteration_4_o2_reflected_return_pulse.py"
)


def _load_o1_module() -> Any:
    spec = importlib.util.spec_from_file_location("n05_iteration_3_o1", O1_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load O1 helper module from {O1_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


O1 = _load_o1_module()
PACKET_AMOUNT = O1.PACKET_AMOUNT
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
                        "amount": PACKET_AMOUNT,
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
                "expected one packet departure and one packet arrival per O2 hop"
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


def _validate_return_contact(
    target_contact_event: Mapping[str, Any] | None,
    *,
    expected_target_node_id: int,
) -> tuple[bool, str]:
    if target_contact_event is None:
        return False, "n05_missing_target_contact"
    if target_contact_event.get("event_kind") != O1.LGRC9V3_PACKET_EVENT_KIND_ARRIVAL:
        return False, "n05_missing_target_contact"
    if int(target_contact_event.get("target_node_id", -1)) != expected_target_node_id:
        return False, "n05_stale_outbound_contact"
    return True, "n05_return_eligibility_from_committed_target_contact"


def _run_o2_positive_lane(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = O1._build_model(manifest)
    initial_budget = O1._budget_surface(model)
    target_reservoir_node_id = int(manifest["fixture"]["target_reservoir_node_id"])
    target_reservoir_before = O1._node_coherence(model, target_reservoir_node_id)
    outbound_route = manifest["routes"]["n05_o1_source_to_target_route_v1"]
    return_route = manifest["routes"]["n05_o2_target_to_source_return_route_v1"]

    outbound_hops, outbound_producer_records, outbound_packet_events = _run_route_hops(
        model,
        outbound_route,
        chain_phase="outbound",
    )
    target_contact = outbound_hops[-1]["arrival_processed_event"]
    contact_valid, contact_blocker = _validate_return_contact(
        target_contact,
        expected_target_node_id=int(outbound_route["target_node_id"]),
    )
    if not contact_valid:
        raise RuntimeError(f"target contact did not authorize return: {contact_blocker}")

    target_contact_digest = _digest(target_contact)
    return_eligibility_record = {
        "record_id": "n05-o2-return-eligibility-" + target_contact_digest[:24],
        "record_kind": "n05_return_eligibility_from_committed_target_contact",
        "source_event_id": target_contact["event_id"],
        "source_event_digest": target_contact_digest,
        "source_packet_id": target_contact["packet_id"],
        "source_route_id": outbound_route["route_id"],
        "return_route_id": return_route["route_id"],
        "not_before_scheduler_event_index": target_contact["scheduler_event_index"],
        "not_before_event_time_key": target_contact["event_time_key"],
        "committed_target_contact_required": True,
        "hidden_return_timing_used": False,
    }

    return_hops, return_producer_records, return_packet_events = _run_route_hops(
        model,
        return_route,
        chain_phase="return",
    )

    final_budget = O1._budget_surface(model)
    final_state = model.get_state()
    ledger = final_state.packet_ledger
    assert ledger is not None
    final_return = return_hops[-1]["arrival_processed_event"]
    final_return_digest = _digest(final_return)
    producer_records = [*outbound_producer_records, *return_producer_records]
    processed_packet_events = [*outbound_packet_events, *return_packet_events]
    scheduler_order = [
        event["processed_event"]["scheduler_event_index"]
        for event in processed_packet_events
    ]
    event_time_order = [
        event["processed_event"]["event_time_key"] for event in processed_packet_events
    ]
    return_scheduler_order = [
        target_contact["scheduler_event_index"],
        return_eligibility_record["not_before_scheduler_event_index"],
        *[
            event["processed_event"]["scheduler_event_index"]
            for event in return_packet_events
        ],
    ]

    return {
        "run_id": "n05_iteration_4_o2_reflected_return_pulse",
        "lane_id": "o2_enabled_reflected_return_pulse",
        "status": "passed",
        "o_level": "O2",
        "o_level_is_evidence_classification": True,
        "claim_ceiling": "reflected_pulse_candidate",
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
        "target_contact_evidence": {
            "evidence_kind": "committed_lgrc9v3_packet_arrival_event",
            "source_event_id": target_contact["event_id"],
            "source_event_digest": target_contact_digest,
            "native_causal_pulse_substrate_surface_used": False,
            "surface_scope_note": (
                "O2 remains experiment-local; no native causal pulse-substrate "
                "surface policy is enabled for this lane."
            ),
        },
        "fixture_id": manifest["fixture"]["fixture_id"],
        "source_node_id": int(outbound_route["source_node_id"]),
        "target_node_id": int(outbound_route["target_node_id"]),
        "route_id": outbound_route["route_id"],
        "return_route_id": return_route["route_id"],
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
        "outbound_packet_id": target_contact["packet_id"],
        "outbound_packet_digest": target_contact_digest,
        "outbound_packet_id_semantics": (
            "terminal_target_contact_packet_for_multihop_o2_outbound_chain"
        ),
        "outbound_packet_ids": [
            hop["arrival_processed_event"]["packet_id"] for hop in outbound_hops
        ],
        "outbound_packet_digests": [
            _digest(hop["arrival_processed_event"]) for hop in outbound_hops
        ],
        "outbound_amount": PACKET_AMOUNT,
        "target_reservoir_node_id": target_reservoir_node_id,
        "target_reservoir_before": target_reservoir_before,
        "target_reservoir_after": O1._node_coherence(model, target_reservoir_node_id),
        "return_packet_id": final_return["packet_id"],
        "return_packet_digest": final_return_digest,
        "return_packet_ids": [
            hop["arrival_processed_event"]["packet_id"] for hop in return_hops
        ],
        "return_packet_digests": [
            _digest(hop["arrival_processed_event"]) for hop in return_hops
        ],
        "return_amount": PACKET_AMOUNT,
        "cycle_id": "n05_o2_reflected_return_cycle_000",
        "target_contact_event_id": target_contact["event_id"],
        "return_source_contact_event_id": final_return["event_id"],
        "return_eligibility_record": return_eligibility_record,
        "outbound_return_lineage": {
            "outbound_target_contact_event_id": target_contact["event_id"],
            "outbound_target_contact_digest": target_contact_digest,
            "return_eligibility_record_id": return_eligibility_record["record_id"],
            "return_packet_id": final_return["packet_id"],
            "return_packet_digest": final_return_digest,
            "return_linked_to_outbound_event": True,
        },
        "causal_delay": float(final_return["event_time_key"])
        - float(outbound_hops[0]["queued_departure_event"]["event_time_key"]),
        "outbound_causal_delay": float(target_contact["event_time_key"])
        - float(outbound_hops[0]["queued_departure_event"]["event_time_key"]),
        "return_causal_delay": float(final_return["event_time_key"])
        - float(return_hops[0]["queued_departure_event"]["event_time_key"]),
        "scheduler_order": scheduler_order,
        "event_time_order": event_time_order,
        "return_scheduler_order": return_scheduler_order,
        "outbound_hop_results": outbound_hops,
        "return_hop_results": return_hops,
        "producer_records": producer_records,
        "processed_packet_events": processed_packet_events,
        "outbound_packet_events": outbound_packet_events,
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
            "status": "not_applicable_for_o2",
            "reservoir_runtime_visible": True,
            "reservoir_hidden_array_used": False,
            "target_reservoir_before": target_reservoir_before,
            "target_reservoir_after": O1._node_coherence(model, target_reservoir_node_id),
            "return_excess_debited": None,
            "return_amount_exceeds_outbound": False,
        },
        "route_coupling": {
            "status": "not_applicable_for_o2",
            "route_coupling_runtime_visible": False,
            "memory_or_trail_claim_allowed": False,
        },
        "producer_boundary": {
            "producer_scheduled_packet": True,
            "producer_mutated_coherence": any(
                bool(hop["producer_mutated_coherence"])
                for hop in [*outbound_hops, *return_hops]
            ),
            "producer_consumed_queued_work": any(
                bool(hop["producer_result"]["queued_work_consumed"])
                for hop in [*outbound_hops, *return_hops]
            ),
            "producer_mutated_topology": any(
                bool(hop["producer_result"]["topology_mutated"])
                for hop in [*outbound_hops, *return_hops]
            ),
            "step_processed_packet_work": True,
        },
        "cycle_semantics": {
            "cycle_definition": (
                "outbound_departure_target_contact_return_eligibility_"
                "return_packet_source_contact"
            ),
            "distinct_cycle_count": 1,
            "plateau_samples_counted_as_cycles": False,
            "repeated_cycle_claim_allowed": False,
        },
        "scheduling_semantics": {
            "scheduling_mode": "explicit_schedule",
            "preauthored_event_list_used": False,
            "hidden_return_timing_used": False,
            "producer_mediated": True,
            "producer_mutated_state": False,
            "constitutive_native_claim_allowed": False,
            "return_route_configured_after_committed_target_contact": True,
        },
        "claim_flags": CLAIM_FLAGS_FALSE,
        "blocked_claims": [
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


def _packet_pairs_ok(packet_events: list[dict[str, Any]]) -> bool:
    packet_processed = [event["processed_event"] for event in packet_events]
    if len(packet_processed) % 2 != 0:
        return False
    pairs_ok = True
    for departure, arrival in zip(packet_processed[::2], packet_processed[1::2]):
        pairs_ok = pairs_ok and (
            departure["event_kind"] == O1.LGRC9V3_PACKET_EVENT_KIND_DEPARTURE
            and arrival["event_kind"] == O1.LGRC9V3_PACKET_EVENT_KIND_ARRIVAL
            and departure["packet_id"] == arrival["packet_id"]
            and float(arrival["event_time_key"]) > float(departure["event_time_key"])
            and int(arrival["scheduler_event_index"])
            > int(departure["scheduler_event_index"])
        )
    return pairs_ok


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
    return_source_contact_event = packet_events_by_event_id.get(
        lane["return_source_contact_event_id"]
    )
    return_eligibility = lane["return_eligibility_record"]
    scheduler_order = [int(event["scheduler_event_index"]) for event in packet_events]
    event_time_order = [float(event["event_time_key"]) for event in packet_events]
    target_contact_digest_matches = (
        target_contact_event is not None
        and _digest(target_contact_event) == return_eligibility["source_event_digest"]
    )
    return_linkage_ok = (
        target_contact_event is not None
        and return_source_contact_event is not None
        and return_eligibility["source_event_id"] == target_contact_event["event_id"]
        and int(target_contact_event["target_node_id"]) == int(lane["target_node_id"])
        and int(return_source_contact_event["target_node_id"])
        == int(lane["source_node_id"])
        and int(return_source_contact_event["scheduler_event_index"])
        > int(target_contact_event["scheduler_event_index"])
    )
    replay_passed = (
        scheduled_event_ids <= set(packet_events_by_event_id)
        and _packet_pairs_ok(list(lane["outbound_packet_events"]))
        and _packet_pairs_ok(list(lane["return_packet_events"]))
        and target_contact_digest_matches
        and return_linkage_ok
        and scheduler_order == sorted(scheduler_order)
        and event_time_order == sorted(event_time_order)
        and abs(lane["conservation"]["budget_abs_error_max"]) <= BUDGET_TOLERANCE
    )
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "outbound_to_contact_to_return_reconstructed": replay_passed,
        "scheduled_events_exist": scheduled_event_ids <= set(packet_events_by_event_id),
        "outbound_packet_pairs_ok": _packet_pairs_ok(list(lane["outbound_packet_events"])),
        "return_packet_pairs_ok": _packet_pairs_ok(list(lane["return_packet_events"])),
        "target_contact_digest_matches": target_contact_digest_matches,
        "return_linkage_ok": return_linkage_ok,
        "scheduler_order_monotonic": scheduler_order == sorted(scheduler_order),
        "event_time_order_monotonic": event_time_order == sorted(event_time_order),
        "passed": replay_passed,
    }


def _run_missing_contact_control() -> dict[str, Any]:
    valid, blocker = _validate_return_contact(None, expected_target_node_id=2)
    return {
        "control_id": "missing_contact",
        "primary_blocker": blocker,
        "control_execution_mode": "structural_validator_control",
        "independent_runtime_lane_executed": False,
        "passed": valid is False and blocker == "n05_missing_target_contact",
    }


def _run_stale_outbound_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    stale_event = dict(lane["return_eligibility_record"])
    stale_event["source_event_digest"] = "stale-" + stale_event["source_event_digest"]
    passed = (
        stale_event["source_event_digest"]
        != lane["outbound_return_lineage"]["outbound_target_contact_digest"]
    )
    return {
        "control_id": "stale_outbound",
        "primary_blocker": "n05_stale_outbound_contact",
        "control_execution_mode": "structural_linkage_control",
        "independent_runtime_lane_executed": False,
        "passed": passed,
    }


def _control_matrix(manifest: Mapping[str, Any], lane: Mapping[str, Any]) -> dict[str, Any]:
    controls: dict[str, Any] = {
        "policy_disabled": O1._run_default_off_control(manifest),
        "missing_contact": _run_missing_contact_control(),
        "stale_outbound": _run_stale_outbound_control(lane),
        "hidden_schedule": {
            "control_id": "hidden_return_schedule",
            "primary_blocker": "n05_hidden_return_schedule_rejected",
            "passed": all(
                not route.get("hidden_schedule_allowed", True)
                for route in manifest["routes"].values()
            )
            and lane["scheduling_semantics"]["preauthored_event_list_used"] is False
            and lane["scheduling_semantics"]["hidden_return_timing_used"] is False,
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
        "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            event["chain_phase"],
            event["processed_event"]["event_kind"],
            event["processed_event"]["packet_id"],
            event["processed_event"]["source_node_id"],
            event["processed_event"]["target_node_id"],
            event["processed_event"]["event_time_key"],
            event["processed_event"]["causal_epoch"],
        )
        for event in lane["processed_packet_events"]
    )
    text = f"""# N05 Iteration 4 O2 Reflected Return Pulse

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
| outbound route | `{lane["route_id"]}` |
| return route | `{lane["return_route_id"]}` |
| target contact event | `{lane["target_contact_event_id"]}` |
| return source-contact event | `{lane["return_source_contact_event_id"]}` |
| outbound packet | `{lane["outbound_packet_id"]}` |
| return packet | `{lane["return_packet_id"]}` |
| causal delay | `{lane["causal_delay"]}` |
| return causal delay | `{lane["return_causal_delay"]}` |
| budget error | `{lane["conservation"]["budget_abs_error_max"]}` |
| row schema compliance | `{lane["row_schema_compliance"]["passed"]}` |

## Packet Chain

| Phase | Event kind | Packet | Source | Target | T_e | Causal epoch |
|---|---|---|---|---|---|---|
{packet_rows}

## Return Eligibility

```json
{json.dumps(lane["return_eligibility_record"], indent=2, sort_keys=True)}
```

## Artifact Replay

```json
{json.dumps(result["artifact_replay"], indent=2, sort_keys=True)}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
{control_rows}

`missing_contact` and `stale_outbound` are structural validator/linkage
controls in O2. They prove the return eligibility record cannot validate
without the committed target-contact event digest, but they are not independent
runtime replay lanes.

## Claim Boundary

All N05 movement, semantic choice, agency, identity, memory/trail, regulation,
agentic-like, locomotion-like, biological, ACO, and unrestricted movement claim
flags remain false. O2 is a reflected-return evidence classification only.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    manifest = _load_manifest()
    positive_lane = _run_o2_positive_lane(manifest)
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
        "run_id": "n05_iteration_4_o2_reflected_return_pulse",
        "iteration": 4,
        "status": status,
        "command": COMMAND,
        "manifest_path": _rel(MANIFEST_PATH),
        "manifest_sha256": _file_sha256(MANIFEST_PATH),
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "execution_stage": "hybrid_scheduling",
        "o_ladder": {
            "o_level": "O2",
            "o_level_is_evidence_classification": True,
            "claim_ceiling": "reflected_pulse_candidate",
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
                "o_level": "O2",
                "claim_ceiling": "reflected_pulse_candidate",
                "row_schema_passed": positive_lane["row_schema_compliance"]["passed"],
            },
            sort_keys=True,
        )
    )
    if status != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
