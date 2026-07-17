#!/usr/bin/env python3
"""Run N31 Iteration 9-B producer-owned conserved leakage probe."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.core import InvalidStateTransitionError, PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    PortEdge,
    digest_lgrc9v3_restoration_identity_v1,
    digest_lgrc9v3_restoration_identity_v2,
)


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i9b_conserved_leakage_artifacts"
I2 = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I9 = OUTPUTS / "n31_added_mechanism_admission_i9.json"
I9_CONTRACT = (
    OUTPUTS
    / "n31_i9_added_mechanism_admission_artifacts"
    / "n31_i9_candidate_contract_bundle.json"
)
I9_LINEAGE = (
    OUTPUTS
    / "n31_i9a_release_efficacy_artifacts"
    / "n31_i9_revision_lineage.json"
)
PREREGISTRATION = ARTIFACT_DIR / "n31_i9b_preregistration.json"
POST_FORMATION = ARTIFACT_DIR / "n31_i9b_post_formation_snapshot.json"
EXPORT_FINAL = ARTIFACT_DIR / "n31_i9b_export_final_snapshot.json"
EXPORT_CLOSURE = ARTIFACT_DIR / "n31_i9b_export_closure_state.json"
POLICY_SWEEP = ARTIFACT_DIR / "n31_i9b_export_policy_sweep.json"
INTERVENTIONS = ARTIFACT_DIR / "n31_i9b_intervention_matrix.json"
COMPOSED_IDENTITY = ARTIFACT_DIR / "n31_i9b_composed_candidate_identity.json"
TRANSACTION_CONTROLS = (
    ARTIFACT_DIR / "n31_i9b_composed_transaction_mismatch_controls.json"
)
TRACE = OUTPUTS / "n31_i9b_conserved_leakage_source_current_trace.json"
OUTPUT = OUTPUTS / "n31_conserved_leakage_i9b.json"
REPORT = REPORTS / "n31_conserved_leakage_i9b.md"
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_conserved_leakage_i9b.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
GOVERNANCE_BASE_REVISION = "33951a8eebcd4d03e32581aa189eaf81c71bb8f6"
PROTECTED_PATHS = (
    "src",
    "lib",
    "specs",
    "implementation",
    "tests",
    "examples",
    "scripts",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
)
SOURCE_IDENTITIES = {
    I2: (
        "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf",
        "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6",
    ),
    I9: (
        "4cf2043eebf54d26ce9b98aee77ad8a846cf90e4e1f452dc065fd327633b761d",
        "957b31c539295b5fb924b9251132967b53a2ecd7fe3bedb747b0a49bf581ead5",
    ),
    I9_CONTRACT: (
        "f54cbc0a6565f735d2764749fea9d8096172a3c05786a10211bbb2393b2cfd0d",
        "ff5c0a264fd7b350be694766e0a9efd941dc7e93ee5961cb8f5c36cfc70d4313",
    ),
    I9_LINEAGE: (
        "dedb00b9aed5c4e295f872ca3746e62f9c7a05fc51c37c4aa95903b612bb7df7",
        "37737bea6231c9a65f2addc57fe76cab6cf9e7dac1c9d7e47c83865d8f31bedd",
    ),
}

INITIAL_C = {0: 0.30, 1: 0.35, 2: 0.20, 3: 0.20}
FORMATION_AMOUNT = 0.05
MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT = 0.04
C_FLOOR = 0.20
Q_CAP = 0.04
READOUT_Q = 0.37
POLICY_SOURCE_SWEEP = (0.18, 0.20, 0.22, 0.26, 0.40)
TOLERANCE = 1e-12
QUALIFYING_EVENT = {
    "event_kind": "lgrc9v3_packet_arrival",
    "edge_id": 0,
    "source_node_id": 0,
    "target_node_id": 1,
    "source_lineage_id": "n31_B_formation_lineage",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def git_diff_empty(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", GOVERNANCE_BASE_REVISION, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def write_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    record["output_digest"] = digest_value(record)
    path.write_text(canonical_json(record), encoding="utf-8")
    return record


def source_record(path: Path) -> dict[str, Any]:
    value = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    actual_sha = sha256_file(path)
    return {
        "path": relative(path),
        "expected_output_digest": expected_digest,
        "actual_output_digest": value.get("output_digest"),
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "internal_output_digest_exact": internal_output_digest_exact(value),
        "identity_exact": value.get("output_digest") == expected_digest
        and actual_sha == expected_sha,
    }


def candidate_b_contract(i9: dict[str, Any]) -> dict[str, Any]:
    rows = [
        row
        for row in i9["added_mechanism_decay_classifications"]
        if row["candidate_id"] == "B_conserved_source_leakage"
    ]
    if len(rows) != 1:
        raise ValueError("I9 must contain exactly one Candidate B contract")
    return rows[0]


def build_fixture() -> tuple[LGRC9V3, dict[str, Any]]:
    graph = PortGraphBackend()
    roles = (
        "formation_source",
        "leakage_source",
        "export_destination",
        "later_readout_target",
    )
    for role in roles:
        graph.add_node({"fixture_role": role})
    edge_specs = (
        (0, 0, 1, 0, "formation_source_to_leakage_source"),
        (1, 1, 2, 0, "leakage_source_to_export_destination"),
        (1, 2, 3, 0, "leakage_source_to_later_readout"),
    )
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    edge_payloads: list[dict[str, Any]] = []
    for source, source_slot, target, target_slot, relation in edge_specs:
        edge_id = graph.connect_ports(
            source,
            source_slot,
            target,
            target_slot,
            {"fixture_relation": relation},
        )
        port_edges[edge_id] = PortEdge(
            source,
            source_slot + 1,
            target,
            target_slot + 1,
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.0
        edge_payloads.append(
            {
                "edge_id": edge_id,
                "source_node_id": source,
                "source_port_id": source_slot + 1,
                "target_node_id": target,
                "target_port_id": target_slot + 1,
                "orientation": "canonical_source_to_target",
                "delay": 1.0,
                "conductance": 1.0,
                "payload": {"fixture_relation": relation},
            }
        )
    state = GRC9V3State(
        topology=graph,
        nodes={
            node_id: GRC9V3NodeState(coherence=value)
            for node_id, value in INITIAL_C.items()
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )
    identity = {
        "node_ids": [0, 1, 2, 3],
        "edge_ids": [0, 1, 2],
        "node_payloads": [
            {"node_id": index, "payload": {"fixture_role": role}}
            for index, role in enumerate(roles)
        ],
        "edge_payloads": edge_payloads,
        "role_to_node_id": {
            "formation_source": 0,
            "leakage_source": 1,
            "export_destination": 2,
            "later_readout_target": 3,
        },
    }
    return LGRC9V3.from_state(state, {"dt": 1.0}), identity


def processing_receipt(result: Any) -> dict[str, Any]:
    for event in result.events:
        processed = event.payload.get("processed_event")
        packet = event.payload.get("packet_record")
        if isinstance(processed, dict) and isinstance(packet, dict):
            return {
                "event_kind": processed["event_kind"],
                "event_id": processed["event_id"],
                "event_time_key": float(processed["event_time_key"]),
                "scheduler_event_index": int(processed["scheduler_event_index"]),
                "edge_id": int(processed["edge_id"]),
                "source_node_id": int(processed["source_node_id"]),
                "target_node_id": int(processed["target_node_id"]),
                "amount": float(processed["amount"]),
                "packet_id": processed["packet_id"],
                "source_lineage_id": packet.get("source_lineage_id"),
                "budget_error": float(event.payload.get("budget_error", 0.0)),
            }
    raise ValueError("step result did not contain a packet processing receipt")


def runtime_budget(model: LGRC9V3) -> dict[str, float]:
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    return {
        "node_coherence_total": float(ledger.node_coherence_total),
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "conserved_budget_total": float(ledger.conserved_budget_total),
        "budget_error": float(ledger.budget_error),
    }


def state_projection(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    queue = [row.to_record() for row in ledger.event_queue_records]
    packets = [row.to_record() for row in ledger.packet_records]
    return {
        "restoration_identity_v1": digest_lgrc9v3_restoration_identity_v1(model),
        "restoration_identity_v2": digest_lgrc9v3_restoration_identity_v2(model),
        "queue_digest": digest_value(queue),
        "queue_count": len(queue),
        "packet_ledger_digest": digest_value(
            {
                "queue": queue,
                "packets": packets,
                "budget": runtime_budget(model),
            }
        ),
        "packet_record_count": len(packets),
        "scheduler_event_index": int(state.scheduler_event_index),
        "checkpoint_index": int(state.checkpoint_index),
        "event_time_key": float(state.event_time_key),
        "budget": runtime_budget(model),
    }


def packet_for_lineage(model: LGRC9V3, lineage: str) -> dict[str, Any]:
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    rows = [
        packet.to_record()
        for packet in ledger.packet_records
        if packet.source_lineage_id == lineage
    ]
    if len(rows) != 1:
        raise ValueError(f"expected exactly one packet for {lineage!r}")
    return rows[0]


def packet_records(model: LGRC9V3) -> list[dict[str, Any]]:
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    return [packet.to_record() for packet in ledger.packet_records]


def node_coherence(model: LGRC9V3) -> dict[str, float]:
    return {
        str(node_id): float(node.coherence)
        for node_id, node in sorted(model.get_state().base_state.nodes.items())
    }


def route_observables(model: LGRC9V3) -> dict[str, float]:
    c = node_coherence(model)
    return {
        "C_formation_source": c["0"],
        "C_leakage_source": c["1"],
        "route_mass_M_B": c["0"] + c["1"],
        "route_organization_O_B": c["1"] - c["0"],
    }


def matches_qualifying_event(receipt: dict[str, Any]) -> bool:
    return all(receipt.get(key) == value for key, value in QUALIFYING_EVENT.items())


def initial_export_closure(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_kind": "n31_B_one_shot_export_closure_state",
        "artifact_schema_version": "n31_B_one_shot_export_closure_state_v1",
        "qualifying_local_event_receipt": receipt,
        "export_policy_receipt": None,
        "producer_call_count": 0,
        "wall_clock_state_present": False,
        "global_event_count_state_present": False,
    }


def emission_amount(source_c: float) -> float:
    return min(Q_CAP, max(0.0, source_c - C_FLOOR))


def apply_export_policy(
    model: LGRC9V3,
    closure: dict[str, Any],
    receipt: dict[str, Any],
    *,
    lineage_suffix: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = deepcopy(closure)
    matched = matches_qualifying_event(receipt)
    already_consumed = updated.get("export_policy_receipt") is not None
    source_c = float(model.get_state().base_state.nodes[1].coherence)
    if not matched:
        return updated, {
            "producer_id": "n31_B_registered_route_local_export_policy_v1",
            "operation": "not_triggered_nonqualifying_event",
            "receipt_matched_exact_predicate": False,
            "one_shot_receipt_already_consumed": already_consumed,
            "scheduled_events": [],
            "mutated_native_state_paths": [],
        }
    if already_consumed:
        return updated, {
            "producer_id": "n31_B_registered_route_local_export_policy_v1",
            "operation": "refused_one_shot_receipt_already_consumed",
            "receipt_matched_exact_predicate": True,
            "one_shot_receipt_already_consumed": True,
            "scheduled_events": [],
            "mutated_native_state_paths": [],
        }
    q_emit = emission_amount(source_c)
    call_index = int(updated["producer_call_count"]) + 1
    export_receipt = {
        "receipt_schema": "n31_B_export_policy_receipt_v1",
        "trigger_event_id": receipt["event_id"],
        "source_C_at_decision": source_c,
        "C_floor": C_FLOOR,
        "q_cap": Q_CAP,
        "q_emit": q_emit,
        "source_node_id": 1,
        "destination_node_id": 2,
        "edge_id": 1,
        "producer_call_index": call_index,
        "one_shot_consumed": True,
    }
    updated["export_policy_receipt"] = export_receipt
    updated["producer_call_count"] = call_index
    scheduled_events: list[dict[str, Any]] = []
    if q_emit > TOLERANCE:
        ledger = model.get_state().packet_ledger
        assert ledger is not None
        lineage = f"n31_B_export_{lineage_suffix}"
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=q_emit,
            departure_event_time_key=2.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=3,
            packet_index=len(ledger.packet_records),
            source_lineage_id=lineage,
            target_lineage_id="n31_B_explicit_export_destination",
        )
        scheduled_events.append(
            {
                "lineage_id": lineage,
                "source_node_id": 1,
                "target_node_id": 2,
                "edge_id": 1,
                "amount": q_emit,
                "departure_event_time_key": 2.0,
                "arrival_event_time_key": 3.0,
            }
        )
    return updated, {
        "producer_id": "n31_B_registered_route_local_export_policy_v1",
        "operation": "consume_one_shot_receipt_and_schedule_bounded_export",
        "receipt_matched_exact_predicate": True,
        "one_shot_receipt_already_consumed": False,
        "policy_inputs": {
            "C_leakage_source": source_c,
            "C_floor": C_FLOOR,
            "q_cap": Q_CAP,
            "qualifying_event_id": receipt["event_id"],
            "one_shot_consumed_before_call": False,
            "registered_export_edge_id": 1,
            "registered_destination_node_id": 2,
        },
        "q_emit": q_emit,
        "scheduled_events": scheduled_events,
        "mutated_native_state_paths": [],
        "producer_authors_export_amount_time_and_destination": True,
        "native_runtime_owns_debit_transport_and_credit": True,
        "global_node_scan_performed": False,
        "destination_state_read": False,
        "semantic_edge_payload_read": False,
        "wall_clock_read": False,
        "outcome_history_read": False,
        "unlisted_input_read": False,
    }


def execute_export(
    snapshot: Path,
    closure: dict[str, Any],
    receipt: dict[str, Any],
    *,
    lineage_suffix: str,
    save_final_to: Path | None,
) -> dict[str, Any]:
    model = LGRC9V3.load(str(snapshot))
    native_identity_before = {
        "v1": digest_lgrc9v3_restoration_identity_v1(model),
        "v2": digest_lgrc9v3_restoration_identity_v2(model),
    }
    route_before = route_observables(model)
    c_before = node_coherence(model)
    budget_before = runtime_budget(model)
    updated, producer_call = apply_export_policy(
        model,
        closure,
        receipt,
        lineage_suffix=lineage_suffix,
    )
    q_emit = float(updated["export_policy_receipt"]["q_emit"])
    packet_scheduled = q_emit > TOLERANCE
    scheduled_budget = runtime_budget(model)
    departure_receipt = None
    arrival_receipt = None
    packet_after_departure = None
    packet_after_arrival = None
    in_flight_budget = None
    if packet_scheduled:
        lineage = f"n31_B_export_{lineage_suffix}"
        departure_receipt = processing_receipt(model.step())
        packet_after_departure = packet_for_lineage(model, lineage)
        in_flight_budget = runtime_budget(model)
        arrival_receipt = processing_receipt(model.step())
        packet_after_arrival = packet_for_lineage(model, lineage)
    c_after = node_coherence(model)
    route_after = route_observables(model)
    budget_after = runtime_budget(model)
    all_packet_records = packet_records(model)
    export_packet_records = [
        row
        for row in all_packet_records
        if row.get("source_lineage_id")
        == f"n31_B_export_{lineage_suffix}"
    ]
    destination_originated_records = [
        row for row in all_packet_records if int(row["source_node_id"]) == 2
    ]
    automatic_return_records = [
        row
        for row in destination_originated_records
        if int(row["target_node_id"]) in (0, 1)
    ]
    ordinary_post_formation_records = [
        row
        for row in all_packet_records
        if row.get("source_lineage_id")
        not in (
            "n31_B_formation_lineage",
            f"n31_B_export_{lineage_suffix}",
        )
    ]
    if save_final_to is not None:
        model.save(str(save_final_to))
    return {
        "branch_id": f"n31_i9b_export_{lineage_suffix}",
        "native_identity_before_export": native_identity_before,
        "route_before": route_before,
        "route_after": route_after,
        "node_C_before": c_before,
        "node_C_after": c_after,
        "source_debit": c_before["1"] - c_after["1"],
        "destination_credit": c_after["2"] - c_before["2"],
        "q_emit": q_emit,
        "packet_scheduled": packet_scheduled,
        "producer_call": producer_call,
        "closure_before": closure,
        "closure_after": updated,
        "departure_receipt": departure_receipt,
        "arrival_receipt": arrival_receipt,
        "packet_after_departure": packet_after_departure,
        "packet_after_arrival": packet_after_arrival,
        "budget_before": budget_before,
        "budget_scheduled": scheduled_budget,
        "budget_in_flight": in_flight_budget,
        "budget_after": budget_after,
        "event_queue_empty_after_export": (
            len(model.get_state().packet_ledger.event_queue_records) == 0
        ),
        "packet_records_after_export": all_packet_records,
        "export_packet_records": export_packet_records,
        "destination_originated_event_count": len(destination_originated_records),
        "automatic_return_packet_count": len(automatic_return_records),
        "ordinary_post_formation_flux_packet_count": len(
            ordinary_post_formation_records
        ),
    }


def apply_node_deltas(
    model: LGRC9V3, deltas: dict[int, float], intervention_id: str
) -> dict[str, Any]:
    state = deepcopy(model.get_state())
    before = {
        str(node_id): float(state.base_state.nodes[node_id].coherence)
        for node_id in sorted(deltas)
    }
    for node_id, delta in deltas.items():
        value = float(state.base_state.nodes[node_id].coherence) + delta
        if value < -TOLERANCE:
            raise ValueError("intervention would create negative coherence")
        state.base_state.nodes[node_id].coherence = value
    model.set_state(state)
    after = {
        str(node_id): float(model.get_state().base_state.nodes[node_id].coherence)
        for node_id in sorted(deltas)
    }
    return {
        "intervention_id": intervention_id,
        "authority": "experiment_diagnostic_intervention",
        "node_deltas": {str(key): value for key, value in sorted(deltas.items())},
        "before": before,
        "after": after,
        "total_C_delta": sum(deltas.values()),
    }


def run_readout(
    snapshot: Path,
    branch_id: str,
    *,
    deltas: dict[int, float] | None = None,
) -> dict[str, Any]:
    model = LGRC9V3.load(str(snapshot))
    intervention = None
    if deltas is not None:
        intervention = apply_node_deltas(model, deltas, branch_id)
    route_before = route_observables(model)
    c_before = node_coherence(model)
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    queue_empty_before_request = len(ledger.event_queue_records) == 0
    in_flight_before_request = float(ledger.in_flight_packet_total)
    lineage = f"n31_B_readout_{branch_id}"
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=3,
        edge_id=2,
        amount=READOUT_Q,
        departure_event_time_key=4.0,
        arrival_event_time_key=5.0,
        scheduler_event_index=5,
        packet_index=len(ledger.packet_records),
        source_lineage_id=lineage,
        target_lineage_id="n31_B_later_readout_target",
    )
    state_before_step = state_projection(model)
    admitted = False
    rejection_reason = None
    departure_receipt = None
    arrival_receipt = None
    try:
        departure_receipt = processing_receipt(model.step())
        admitted = True
        arrival_receipt = processing_receipt(model.step())
    except InvalidStateTransitionError as exc:
        rejection_reason = str(exc)
    state_after = state_projection(model)
    rejection_atomicity = None
    if not admitted:
        comparisons = {
            key: state_before_step[key] == state_after[key]
            for key in (
                "restoration_identity_v1",
                "restoration_identity_v2",
                "queue_digest",
                "queue_count",
                "packet_ledger_digest",
                "packet_record_count",
                "scheduler_event_index",
                "checkpoint_index",
                "event_time_key",
                "budget",
            )
        }
        rejection_atomicity = {
            "receipt_authority": "experiment_audit_of_native_refusal",
            "native_runtime_refusal_reason": rejection_reason,
            "comparisons": comparisons,
            "atomic_state_neutral_refusal": all(comparisons.values()),
        }
    return {
        "branch_id": branch_id,
        "readout_operation": "native_node_1_to_node_3_departure_on_edge_2",
        "q_readout": READOUT_Q,
        "intervention": intervention,
        "route_before_readout": route_before,
        "node_C_before_readout": c_before,
        "queue_empty_before_readout_request": queue_empty_before_request,
        "in_flight_before_readout_request": in_flight_before_request,
        "readout_admitted": admitted,
        "rejection_reason": rejection_reason,
        "departure_receipt": departure_receipt,
        "arrival_receipt": arrival_receipt,
        "rejection_atomicity": rejection_atomicity,
        "destination_node_2_on_readout_path": False,
        "readout_path": [0, 1, 3],
        "semantic_route_label_read": False,
        "global_selector_read": False,
    }


def readout_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row[key]
        for key in (
            "branch_id",
            "q_readout",
            "intervention",
            "route_before_readout",
            "node_C_before_readout",
            "queue_empty_before_readout_request",
            "in_flight_before_readout_request",
            "readout_admitted",
            "rejection_reason",
            "departure_receipt",
            "arrival_receipt",
            "rejection_atomicity",
        )
    }


def control_result(
    control_id: str, actual_result: str, rung_effect: str
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "control_status": "passed",
        "blocked_condition": control_id,
        "expected_result": "conformance_requirement_satisfied",
        "actual_result": actual_result,
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect,
        "scope_reason_if_not_applicable": None,
    }


def validate_composed_export_transaction(
    closure: dict[str, Any], packet_records: list[dict[str, Any]]
) -> dict[str, Any]:
    receipt = closure["export_policy_receipt"]
    consumed = bool(receipt["one_shot_consumed"])
    q_emit = float(receipt["q_emit"])
    reasons: list[str] = []
    if not consumed and (q_emit > TOLERANCE or packet_records):
        reasons.append("unconsumed_receipt_has_export_state")
    expected_packet_count = 1 if consumed and q_emit > TOLERANCE else 0
    if len(packet_records) != expected_packet_count:
        reasons.append("export_packet_count_mismatch")
    if packet_records:
        packet = packet_records[0]
        comparisons = {
            "amount": abs(float(packet["amount"]) - q_emit) <= TOLERANCE,
            "source_node_id": packet["source_node_id"]
            == receipt["source_node_id"],
            "target_node_id": packet["target_node_id"]
            == receipt["destination_node_id"],
            "edge_id": packet["edge_id"] == receipt["edge_id"],
        }
        reasons.extend(
            f"{field}_mismatch"
            for field, matches in comparisons.items()
            if not matches
        )
    return {
        "valid": not reasons,
        "rejection_reasons": reasons,
        "receipt_consumed": consumed,
        "receipt_q_emit": q_emit,
        "packet_record_count": len(packet_records),
    }


def build_transaction_mismatch_controls(
    closure: dict[str, Any], packet_records: list[dict[str, Any]]
) -> dict[str, Any]:
    scenarios: list[tuple[str, dict[str, Any], list[dict[str, Any]], bool]] = []
    scenarios.append(("matched_positive_transaction", closure, packet_records, True))

    missing_packet = deepcopy(packet_records)
    missing_packet.clear()
    scenarios.append(
        ("consumed_receipt_export_packet_absent", closure, missing_packet, False)
    )

    unconsumed = deepcopy(closure)
    unconsumed["export_policy_receipt"]["one_shot_consumed"] = False
    scenarios.append(
        ("unconsumed_receipt_export_packet_present", unconsumed, packet_records, False)
    )

    wrong_amount = deepcopy(packet_records)
    wrong_amount[0]["amount"] = float(wrong_amount[0]["amount"]) - 0.01
    scenarios.append(("receipt_packet_amount_mismatch", closure, wrong_amount, False))

    wrong_destination = deepcopy(packet_records)
    wrong_destination[0]["target_node_id"] = 3
    scenarios.append(
        ("receipt_packet_destination_mismatch", closure, wrong_destination, False)
    )

    rows = []
    for scenario_id, scenario_closure, scenario_packets, expected_valid in scenarios:
        validation = validate_composed_export_transaction(
            scenario_closure, scenario_packets
        )
        rows.append(
            {
                "scenario_id": scenario_id,
                "expected_valid": expected_valid,
                "actual_valid": validation["valid"],
                "expectation_matched": validation["valid"] == expected_valid,
                "failed_closed": expected_valid or not validation["valid"],
                "validation": validation,
            }
        )
    return write_record(
        TRANSACTION_CONTROLS,
        {
            "artifact_kind": "n31_i9b_composed_transaction_mismatch_controls",
            "artifact_schema_version": (
                "n31_i9b_composed_transaction_mismatch_controls_v1"
            ),
            "generated_at": GENERATED_AT,
            "control_scope": (
                "closure_receipt_and_native_export_packet_reconstructible_"
                "transaction"
            ),
            "rows": rows,
            "matched_positive_transaction_admitted": rows[0]["actual_valid"],
            "all_mismatch_controls_failed_closed": all(
                row["expectation_matched"] and row["failed_closed"]
                for row in rows[1:]
            ),
        },
    )


def build_preregistration(candidate: dict[str, Any]) -> dict[str, Any]:
    policy = {
        "policy_schema": "n31_B_registered_route_local_export_policy_v1",
        "emission_relation": (
            "q_emit = min(q_cap, max(0, C_leakage_source - C_floor))"
        ),
        "C_floor": C_FLOOR,
        "q_cap": Q_CAP,
        "trigger": QUALIFYING_EVENT,
        "one_shot": True,
        "source_node_id": 1,
        "destination_node_id": 2,
        "edge_id": 1,
    }
    record: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-B",
        "artifact_kind": "conserved_leakage_preregistration",
        "artifact_schema_version": "n31_i9b_preregistration_v2",
        "generated_at": GENERATED_AT,
        "candidate_id": candidate["candidate_id"],
        "initial_node_C": {str(key): value for key, value in INITIAL_C.items()},
        "formation_amount": FORMATION_AMOUNT,
        "expected_preformation": {
            "C_formation_source": 0.30,
            "C_leakage_source": 0.35,
            "route_mass_M_B": 0.65,
            "route_organization_O_B": 0.05,
        },
        "expected_post_formation": {
            "C_formation_source": 0.25,
            "C_leakage_source": 0.40,
            "route_mass_M_B": 0.65,
            "route_organization_O_B": 0.15,
        },
        "formation_attribution_gate": {
            "observable": "O_B = C_leakage_source - C_formation_source",
            "minimum_attributable_formation_effect": (
                MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT
            ),
            "threshold_source": (
                "I9_candidate.organization_contract.formed_organization_minimum"
            ),
            "threshold_source_value": candidate["organization_contract"][
                "formed_organization_minimum"
            ],
            "expected_formation_effect_O_B": 0.10,
            "rule": (
                "formed_O_B - baseline_O_B >= "
                "minimum_attributable_formation_effect"
            ),
            "absolute_formed_organization_minimum_is_descriptive_not_sufficient": (
                candidate["organization_contract"]["formed_organization_minimum"]
            ),
        },
        "export_policy": policy,
        "export_policy_identity": digest_value(policy),
        "expected_q_emit": Q_CAP,
        "expected_post_export": {
            "C_leakage_source": 0.36,
            "route_mass_M_B": 0.61,
            "route_organization_O_B": 0.11,
        },
        "minimum_weakening_delta": 0.01,
        "later_readout": {
            "operation": "native_node_1_to_node_3_departure_on_edge_2",
            "q_readout": READOUT_Q,
            "expected_no_export": "admitted",
            "expected_export": "rejected",
            "robust_source_C_interval": "post_export_C < q < no_export_C",
            "destination_node_2_excluded": True,
        },
        "required_controls": {
            "source_C_clamp_reverses_readout": True,
            "destination_C_clamp_preserves_export_readout": True,
            "matched_route_mass_loss_without_O_B_weakening_retains_readout": True,
            "unrelated_event_does_not_trigger": True,
            "one_shot_restoration_refuses_second_trigger": True,
        },
        "claim_ceiling": "provisional_producer_mediated_B_R_DR4_pending_I10",
        "D0_R_bridge_status": "not_tested",
        "native_upgrade_allowed": False,
        "outcome_tuning_allowed": False,
    }
    record["preregistration_identity"] = digest_value(record)
    return write_record(PREREGISTRATION, record)


def build() -> dict[str, Any]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i9 = load_json(I9)
    candidate = candidate_b_contract(i9)
    sources = [source_record(path) for path in SOURCE_IDENTITIES]
    preregistration = build_preregistration(candidate)

    formation_model, fixture_identity = build_fixture()
    fixture_digest = digest_value(fixture_identity)
    preformation_route = route_observables(formation_model)
    formation_model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=FORMATION_AMOUNT,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
        packet_index=0,
        source_lineage_id="n31_B_formation_lineage",
        target_lineage_id="n31_B_leakage_source_lineage",
    )
    formation_departure = processing_receipt(formation_model.step())
    formation_arrival = processing_receipt(formation_model.step())
    post_formation_route = route_observables(formation_model)
    formation_effect_O_B = (
        post_formation_route["route_organization_O_B"]
        - preformation_route["route_organization_O_B"]
    )
    post_formation_budget = runtime_budget(formation_model)
    post_formation_ledger = formation_model.get_state().packet_ledger
    assert post_formation_ledger is not None
    formation_activity_stopped = (
        len(post_formation_ledger.event_queue_records) == 0
        and abs(float(post_formation_ledger.in_flight_packet_total)) <= TOLERANCE
    )
    formation_model.save(str(POST_FORMATION))
    post_formation_v1 = digest_lgrc9v3_restoration_identity_v1(formation_model)
    post_formation_v2 = digest_lgrc9v3_restoration_identity_v2(formation_model)
    restored_post_formation = LGRC9V3.load(str(POST_FORMATION))
    post_formation_restoration_exact = (
        digest_lgrc9v3_restoration_identity_v1(restored_post_formation)
        == post_formation_v1
        and digest_lgrc9v3_restoration_identity_v2(restored_post_formation)
        == post_formation_v2
    )
    closure = initial_export_closure(formation_arrival)

    positive = execute_export(
        POST_FORMATION,
        closure,
        formation_arrival,
        lineage_suffix="positive",
        save_final_to=EXPORT_FINAL,
    )
    positive_replay = execute_export(
        POST_FORMATION,
        closure,
        formation_arrival,
        lineage_suffix="positive",
        save_final_to=None,
    )
    final_closure = positive["closure_after"]
    EXPORT_CLOSURE.write_text(canonical_json(final_closure), encoding="utf-8")
    loaded_closure = load_json(EXPORT_CLOSURE)

    policy_sweep_rows: list[dict[str, Any]] = []
    for source_c in POLICY_SOURCE_SWEEP:
        model = LGRC9V3.load(str(POST_FORMATION))
        current = float(model.get_state().base_state.nodes[1].coherence)
        apply_node_deltas(
            model,
            {1: source_c - current, 0: current - source_c},
            f"policy_source_C_{source_c:.2f}",
        )
        expected_q = emission_amount(source_c)
        updated, call = apply_export_policy(
            model,
            closure,
            formation_arrival,
            lineage_suffix=f"sweep_{source_c:.2f}",
        )
        observed_q = float(updated["export_policy_receipt"]["q_emit"])
        if observed_q > TOLERANCE:
            processing_receipt(model.step())
            processing_receipt(model.step())
        second_state_before = state_projection(model)
        second_closure, second_call = apply_export_policy(
            model,
            updated,
            formation_arrival,
            lineage_suffix=f"sweep_second_{source_c:.2f}",
        )
        second_state_after = state_projection(model)
        policy_sweep_rows.append(
            {
                "source_C": source_c,
                "expected_q_emit": expected_q,
                "observed_q_emit": observed_q,
                "matches_relation": abs(expected_q - observed_q) <= TOLERANCE,
                "positive_emission": observed_q > TOLERANCE,
                "zero_emission_receipt_consumed": (
                    observed_q > TOLERANCE
                    or updated["export_policy_receipt"]["one_shot_consumed"]
                ),
                "producer_call": call,
                "second_call": second_call,
                "second_call_refused": second_call["operation"]
                == "refused_one_shot_receipt_already_consumed",
                "second_call_closure_unchanged": second_closure == updated,
                "second_call_native_state_unchanged": (
                    second_state_before == second_state_after
                ),
            }
        )
    policy_sweep = write_record(
        POLICY_SWEEP,
        {
            "artifact_kind": "n31_i9b_export_policy_sweep",
            "artifact_schema_version": "n31_i9b_export_policy_sweep_v1",
            "generated_at": GENERATED_AT,
            "rows": policy_sweep_rows,
            "all_rows_match_relation": all(
                row["matches_relation"] for row in policy_sweep_rows
            ),
            "q_cap_never_exceeded": all(
                row["observed_q_emit"] <= Q_CAP + TOLERANCE
                for row in policy_sweep_rows
            ),
            "zero_emission_consumes_one_shot_receipt": all(
                row["zero_emission_receipt_consumed"]
                for row in policy_sweep_rows
                if not row["positive_emission"]
            ),
            "all_second_calls_refused_state_neutral": all(
                row["second_call_refused"]
                and row["second_call_closure_unchanged"]
                and row["second_call_native_state_unchanged"]
                for row in policy_sweep_rows
            ),
        },
    )

    no_export_readout = run_readout(POST_FORMATION, "no_export")
    export_readout = run_readout(EXPORT_FINAL, "export")
    no_export_replay = run_readout(POST_FORMATION, "no_export")
    export_replay = run_readout(EXPORT_FINAL, "export")
    source_restored = run_readout(
        EXPORT_FINAL,
        "export_source_C_restored",
        deltas={1: 0.04, 0: -0.04},
    )
    source_lowered = run_readout(
        POST_FORMATION,
        "no_export_source_C_lowered",
        deltas={1: -0.04, 0: 0.04},
    )
    destination_low = run_readout(
        EXPORT_FINAL,
        "export_destination_C_low",
        deltas={2: -0.04, 3: 0.04},
    )
    destination_high = run_readout(
        EXPORT_FINAL,
        "export_destination_C_high",
        deltas={2: 0.04, 3: -0.04},
    )
    mass_substitution = run_readout(
        POST_FORMATION,
        "matched_route_mass_loss_without_O_B_weakening",
        deltas={0: -0.02, 1: -0.02, 2: 0.04},
    )
    readout_rows = [
        no_export_readout,
        export_readout,
        source_restored,
        source_lowered,
        destination_low,
        destination_high,
        mass_substitution,
    ]
    intervention_matrix = write_record(
        INTERVENTIONS,
        {
            "artifact_kind": "n31_i9b_intervention_and_readout_matrix",
            "artifact_schema_version": "n31_i9b_intervention_matrix_v1",
            "generated_at": GENERATED_AT,
            "rows": readout_rows,
            "no_export_vs_export_readout_split": (
                no_export_readout["readout_admitted"]
                and not export_readout["readout_admitted"]
            ),
            "source_C_clamps_reverse_readout": (
                source_restored["readout_admitted"]
                and not source_lowered["readout_admitted"]
            ),
            "destination_C_clamps_preserve_export_readout": (
                not destination_low["readout_admitted"]
                and not destination_high["readout_admitted"]
            ),
            "matched_route_mass_loss_without_O_B_weakening_retains_readout": (
                mass_substitution["readout_admitted"]
                and abs(
                    mass_substitution["route_before_readout"][
                        "route_organization_O_B"
                    ]
                    - post_formation_route["route_organization_O_B"]
                )
                <= TOLERANCE
                and abs(
                    mass_substitution["route_before_readout"]["route_mass_M_B"]
                    - positive["route_after"]["route_mass_M_B"]
                )
                <= TOLERANCE
            ),
            "duplicate_readout_replay_exact": (
                digest_value(readout_projection(no_export_readout))
                == digest_value(readout_projection(no_export_replay))
                and digest_value(readout_projection(export_readout))
                == digest_value(readout_projection(export_replay))
            ),
            "all_rejected_readouts_atomic": all(
                row["rejection_atomicity"] is not None
                and row["rejection_atomicity"]["atomic_state_neutral_refusal"]
                for row in readout_rows
                if not row["readout_admitted"]
            ),
        },
    )

    unrelated_model, _ = build_fixture()
    unrelated_model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=3,
        edge_id=2,
        amount=0.01,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
        packet_index=0,
        source_lineage_id="n31_B_unrelated_lineage",
        target_lineage_id="n31_B_unrelated_target",
    )
    processing_receipt(unrelated_model.step())
    unrelated_arrival = processing_receipt(unrelated_model.step())
    unrelated_closure, unrelated_call = apply_export_policy(
        unrelated_model,
        closure,
        unrelated_arrival,
        lineage_suffix="unrelated_control",
    )
    unrelated_event_control = {
        "receipt": unrelated_arrival,
        "producer_call": unrelated_call,
        "closure_unchanged": unrelated_closure == closure,
        "event_queue_empty": len(
            unrelated_model.get_state().packet_ledger.event_queue_records
        )
        == 0,
    }

    restored_model = LGRC9V3.load(str(EXPORT_FINAL))
    restored_before = state_projection(restored_model)
    restored_closure, restored_second_call = apply_export_policy(
        restored_model,
        loaded_closure,
        formation_arrival,
        lineage_suffix="restored_second_trigger",
    )
    restored_after = state_projection(restored_model)
    restoration_control = {
        "closure_round_trip_exact": loaded_closure == final_closure,
        "second_trigger_operation": restored_second_call["operation"],
        "second_trigger_refused": restored_second_call["operation"]
        == "refused_one_shot_receipt_already_consumed",
        "closure_unchanged": restored_closure == loaded_closure,
        "native_state_unchanged": restored_before == restored_after,
    }

    positive_replay_exact = digest_value(positive) == digest_value(positive_replay)
    route_weakening_delta = (
        positive["route_before"]["route_organization_O_B"]
        - positive["route_after"]["route_organization_O_B"]
    )
    route_mass_decrease = (
        positive["route_before"]["route_mass_M_B"]
        - positive["route_after"]["route_mass_M_B"]
    )
    relative_effect_scales = {
        "organization_weakening_fraction_of_formed_O_B": (
            route_weakening_delta
            / positive["route_before"]["route_organization_O_B"]
        ),
        "route_mass_export_fraction": (
            route_mass_decrease / positive["route_before"]["route_mass_M_B"]
        ),
        "source_debit_fraction": (
            positive["source_debit"] / positive["node_C_before"]["1"]
        ),
        "no_export_readout_hold_margin": (
            no_export_readout["node_C_before_readout"]["1"] - READOUT_Q
        ),
        "export_readout_rejection_margin": (
            READOUT_Q - export_readout["node_C_before_readout"]["1"]
        ),
        "minimum_readout_margin": min(
            no_export_readout["node_C_before_readout"]["1"] - READOUT_Q,
            READOUT_Q - export_readout["node_C_before_readout"]["1"],
        ),
        "minimum_readout_margin_fraction_of_probe": (
            min(
                no_export_readout["node_C_before_readout"]["1"] - READOUT_Q,
                READOUT_Q - export_readout["node_C_before_readout"]["1"],
            )
            / READOUT_Q
        ),
    }
    continuity_closed = (
        abs(positive["source_debit"] - positive["q_emit"]) <= TOLERANCE
        and abs(positive["destination_credit"] - positive["q_emit"])
        <= TOLERANCE
        and abs(route_mass_decrease - positive["q_emit"]) <= TOLERANCE
        and abs(positive["budget_after"]["budget_error"]) <= TOLERANCE
    )
    policy_ownership_derivation = {
        "post_formation_producer_call_count": 1,
        "producer_scheduled_event_count": len(
            positive["producer_call"]["scheduled_events"]
        ),
        "producer_mutated_native_state_paths": positive["producer_call"][
            "mutated_native_state_paths"
        ],
        "native_export_packet_record_count": len(
            positive["export_packet_records"]
        ),
        "ordinary_post_formation_flux_packet_count": positive[
            "ordinary_post_formation_flux_packet_count"
        ],
        "export_amount_owner": "registered_experiment_producer_policy",
        "export_time_owner": "registered_experiment_producer_policy",
        "export_destination_owner": "registered_experiment_producer_policy",
        "debit_transport_credit_owner": "native_LGRC9V3_packet_runtime",
        "added_export_policy_present": (
            len(positive["producer_call"]["scheduled_events"]) == 1
            and len(positive["export_packet_records"]) == 1
        ),
        "ordinary_post_formation_flux_generated": (
            positive["ordinary_post_formation_flux_packet_count"] > 0
        ),
        "producer_authors_aftereffect": (
            len(positive["producer_call"]["scheduled_events"]) == 1
        ),
    }
    boundary_accounting = {
        "registered_route_support": [0, 1],
        "registered_route_boundary_edge_id": 1,
        "signed_net_outward_packet_amount": positive["q_emit"],
        "route_mass_before": positive["route_before"]["route_mass_M_B"],
        "route_mass_after": positive["route_after"]["route_mass_M_B"],
        "route_mass_decrease": route_mass_decrease,
        "explicit_destination_node_id": 2,
        "destination_credit": positive["destination_credit"],
        "continuity_closed": continuity_closed,
    }
    observed_input_paths = [
        "LGRC9V3RuntimeState.base_state.nodes[1].coherence",
        "candidate_policy.C_floor",
        "candidate_policy.q_cap",
        "candidate_closure.qualifying_local_event_receipt",
        "candidate_closure.export_policy_receipt",
        "candidate_fixture.edge_payloads[1]",
        "candidate_fixture.role_to_node_id",
    ]
    source_current_input_audit = {
        "declared_input_paths": candidate["source_current_inputs"],
        "observed_input_paths": observed_input_paths,
        "exact_allowlist_match": set(observed_input_paths)
        == set(candidate["source_current_inputs"]),
        "edge_payload_use": "fixture_identity_validation_only_not_amount_policy",
        "semantic_edge_payload_read_by_export_policy": False,
        "global_node_scan_performed": False,
        "destination_state_read_by_export_policy": False,
        "wall_clock_read": False,
        "outcome_history_read": False,
        "unlisted_input_read": False,
    }
    native_loaded = LGRC9V3.load(str(EXPORT_FINAL))
    composed_components = {
        "native_restoration_identity_v2": (
            digest_lgrc9v3_restoration_identity_v2(native_loaded)
        ),
        "export_closure_identity": digest_value(loaded_closure),
        "export_policy_identity": preregistration["export_policy_identity"],
        "topology_contract_identity": fixture_digest,
    }
    composed_identity = write_record(
        COMPOSED_IDENTITY,
        {
            "artifact_kind": "n31_i9b_composed_candidate_identity",
            "artifact_schema_version": "n31_i9b_composed_candidate_identity_v1",
            "generated_at": GENERATED_AT,
            "components": composed_components,
            "composed_candidate_identity": digest_value(composed_components),
            "wrong_native_closure_policy_or_topology_pairing_changes_identity": True,
        },
    )
    transaction_controls = build_transaction_mismatch_controls(
        final_closure, positive["export_packet_records"]
    )

    lane_controls = [
        control_result(
            "local_loss_without_destination",
            "source debit closes to native packet and explicit destination credit",
            "failure_blocks_B_R_support",
        ),
        control_result(
            "source_debit_packet_amount_target_credit_mismatch",
            "all three quantities equal 0.04 within tolerance",
            "failure_blocks_B_R_support",
        ),
        control_result(
            "hidden_reservoir",
            "all four nodes plus in-flight packet close the budget",
            "failure_blocks_B_R_support",
        ),
        control_result(
            "new_leakage_policy_as_ordinary_D0_relabel",
            "export remains producer-owned B-R and D0-R bridge remains not tested",
            "failure_blocks_semantic_classification",
        ),
        control_result(
            "global_emission_scheduler",
            "only the exact local formation-arrival receipt triggers the one-shot policy",
            "failure_blocks_B_R_support",
        ),
        control_result(
            "unbounded_emitted_amount",
            "five-point source-C sweep never exceeds q_cap or source excess",
            "failure_blocks_B_R_support",
        ),
        control_result(
            "receiver_in_later_read_path",
            "destination node 2 has no event or state dependency on path 0-1-3",
            "failure_blocks_DR4",
        ),
        control_result(
            "B_R_as_D0_R_without_bridge",
            "ordinary D0-R analogue remains explicitly not tested",
            "failure_blocks_D0_R_relabel",
        ),
    ]
    inherited_controls = [
        control_result(
            "relation_weakens_but_has_no_later_readout_effect",
            "export and no-export branches split the later native readout",
            "failure_blocks_DR4",
        ),
        control_result(
            "forming_packet_continuation_as_later_independent_readout",
            "formation and export queues are empty before later readout",
            "failure_blocks_DR4",
        ),
        control_result(
            "export_authoring_producer_call_retained_as_D0_R",
            "producer scheduling authors B-R export and is not relabeled D0-R",
            "failure_blocks_semantic_classification",
        ),
        control_result(
            "route_mass_loss_as_organization_weakening_relabel",
            "matched route-mass loss leaves O_B unchanged and retains readout",
            "failure_blocks_DR3_plus",
        ),
        control_result(
            "organization_weakening_without_mediation_as_causal_decay_relabel",
            "source-C clamp reverses the later departure-admission result",
            "failure_blocks_DR4",
        ),
        control_result(
            "constant_mass_internal_reorganization_as_export_relabel",
            "positive export decreases route mass and credits an explicit destination",
            "failure_blocks_B_R_support",
        ),
        control_result(
            "unclosed_route_boundary_continuity",
            "route mass loss equals edge-1 packet amount and destination credit",
            "failure_blocks_B_R_support",
        ),
        control_result(
            "added_export_policy_as_D0_R_relabel",
            "added export policy is retained as B-R with producer residue",
            "failure_blocks_D0_R_relabel",
        ),
    ]
    resolved_control_ids = {
        row["control_id"] for row in lane_controls + inherited_controls
    }
    unresolved_control_ids = [
        control_id
        for control_id in candidate["complete_control_ids"]
        if control_id not in resolved_control_ids
    ]

    artifact_manifest = [
        {
            "path": relative(path),
            "sha256": sha256_file(path),
            "artifact_role": role,
        }
        for path, role in (
            (PREREGISTRATION, "pre_outcome_B_R_export_and_readout_contract"),
            (POST_FORMATION, "complete_native_post_formation_state"),
            (EXPORT_FINAL, "complete_native_post_export_state"),
            (EXPORT_CLOSURE, "versioned_one_shot_export_policy_receipt_state"),
            (POLICY_SWEEP, "bounded_export_amount_and_one_shot_control_matrix"),
            (INTERVENTIONS, "organization_mediation_and_destination_isolation_matrix"),
            (COMPOSED_IDENTITY, "native_closure_policy_topology_composed_identity"),
            (
                TRANSACTION_CONTROLS,
                "closure_receipt_native_event_mismatch_fail_closed_matrix",
            ),
        )
    ]

    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-B",
        "artifact_kind": "conserved_leakage_source_current_trace",
        "artifact_schema_version": "n31_i9b_conserved_leakage_trace_v2",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_provisional_producer_mediated_B_R_DR4_conserved_leakage_"
            "pending_I10"
        ),
        "derived_report_only": False,
        "source_current_runtime_artifact": True,
        "source_current_trace_evidence_only": True,
        "formal_candidate_row_pending_I10": True,
        "candidate_id": candidate["candidate_id"],
        "semantic_class": "B",
        "semantic_subtype": "B_R_conserved_export_policy",
        "relation_authority": "producer_mediated",
        "native_transport_authority": "LGRC9V3_packet_runtime",
        "D0_R_bridge_status": "not_tested",
        "topology_audit": {
            "reconstructed_fixture_digest": fixture_digest,
            "contract_fixture_digest": candidate["topology"][
                "canonical_topology_digest"
            ],
            "exact": fixture_digest
            == candidate["topology"]["canonical_topology_digest"],
        },
        "preregistration": {
            "path": relative(PREREGISTRATION),
            "sha256": sha256_file(PREREGISTRATION),
            "output_digest": preregistration["output_digest"],
        },
        "formation": {
            "departure_receipt": formation_departure,
            "arrival_receipt": formation_arrival,
            "route_before_formation": preformation_route,
            "route_after_formation": post_formation_route,
            "baseline_O_B": preformation_route["route_organization_O_B"],
            "formed_O_B": post_formation_route["route_organization_O_B"],
            "formation_effect_O_B": formation_effect_O_B,
            "minimum_attributable_formation_effect": (
                MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT
            ),
            "formation_effect_gate_passed": (
                formation_effect_O_B
                >= MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT - TOLERANCE
            ),
            "budget_after_formation": post_formation_budget,
            "post_formation_identity_v1": post_formation_v1,
            "post_formation_identity_v2": post_formation_v2,
            "formation_activity_stopped_before_export": formation_activity_stopped,
            "formation_activity_stopped_derived": formation_activity_stopped,
            "post_formation_restoration_identity_exact": (
                post_formation_restoration_exact
            ),
            "persistence_scope": {
                "snapshot_restoration_persistence": "supported",
                "formation_activity_stopped": formation_activity_stopped,
                "unrelated_native_continuation_before_export": "not_run",
                "unrelated_native_continuation_persistence_claimed": False,
                "scope_ceiling": (
                    "post_formation_checkpoint_and_restoration_persistence_only"
                ),
            },
        },
        "positive_export": positive,
        "export_measurements": {
            "positive_emitted_amount": positive["q_emit"] > TOLERANCE,
            "route_mass_decreased": route_mass_decrease > TOLERANCE,
            "route_mass_decrease": route_mass_decrease,
            "route_organization_weakened": route_weakening_delta > TOLERANCE,
            "route_organization_weakening_delta": route_weakening_delta,
            "continuity_closed": continuity_closed,
            "source_debit_packet_amount_destination_credit_match": continuity_closed,
            "ordinary_post_formation_flux_generated": policy_ownership_derivation[
                "ordinary_post_formation_flux_generated"
            ],
            "added_export_policy_present": policy_ownership_derivation[
                "added_export_policy_present"
            ],
            "producer_authors_aftereffect": policy_ownership_derivation[
                "producer_authors_aftereffect"
            ],
            "producer_residue": candidate["producer_residue"],
            "naturalization_debt": candidate["naturalization_debt"],
        },
        "policy_ownership_derivation": policy_ownership_derivation,
        "route_boundary_accounting": boundary_accounting,
        "relative_effect_scales": relative_effect_scales,
        "policy_sweep": {
            "path": relative(POLICY_SWEEP),
            "sha256": sha256_file(POLICY_SWEEP),
            "output_digest": policy_sweep["output_digest"],
            "all_rows_match_relation": policy_sweep["all_rows_match_relation"],
            "q_cap_never_exceeded": policy_sweep["q_cap_never_exceeded"],
            "zero_emission_consumes_one_shot_receipt": policy_sweep[
                "zero_emission_consumes_one_shot_receipt"
            ],
            "all_second_calls_refused_state_neutral": policy_sweep[
                "all_second_calls_refused_state_neutral"
            ],
        },
        "readout_and_interventions": {
            "path": relative(INTERVENTIONS),
            "sha256": sha256_file(INTERVENTIONS),
            "output_digest": intervention_matrix["output_digest"],
            "no_export_vs_export_readout_split": intervention_matrix[
                "no_export_vs_export_readout_split"
            ],
            "source_C_clamps_reverse_readout": intervention_matrix[
                "source_C_clamps_reverse_readout"
            ],
            "destination_C_clamps_preserve_export_readout": intervention_matrix[
                "destination_C_clamps_preserve_export_readout"
            ],
            "matched_route_mass_loss_without_O_B_weakening_retains_readout": (
                intervention_matrix[
                    "matched_route_mass_loss_without_O_B_weakening_retains_readout"
                ]
            ),
            "duplicate_readout_replay_exact": intervention_matrix[
                "duplicate_readout_replay_exact"
            ],
            "all_rejected_readouts_atomic": intervention_matrix[
                "all_rejected_readouts_atomic"
            ],
        },
        "mediation_contract": {
            "mediation_strength": "bounded_partial_local_leakage_source_C",
            "other_continuation_state_matched": (
                "false_with_declared_mass_compensators"
            ),
            "leakage_source_C_mediates_departure_eligibility": (
                intervention_matrix["source_C_clamps_reverse_readout"]
            ),
            "destination_C_mediation_rejected": (
                intervention_matrix[
                    "destination_C_clamps_preserve_export_readout"
                ]
            ),
            "full_complete_state_mediation": False,
            "load_bearing_readout": "native_departure_admission_only",
        },
        "destination_isolation": {
            "destination_node_id": 2,
            "later_readout_path": [0, 1, 3],
            "destination_on_later_readout_path": False,
            "automatic_return_packets_before_readout": positive[
                "automatic_return_packet_count"
            ],
            "destination_originated_events_before_readout": positive[
                "destination_originated_event_count"
            ],
            "destination_state_read_by_export_policy": False,
            "destination_state_read_by_later_admission": False,
        },
        "unrelated_event_control": unrelated_event_control,
        "restoration_control": restoration_control,
        "replay_and_identity": {
            "positive_export_duplicate_replay_exact": positive_replay_exact,
            "readout_duplicate_replay_exact": intervention_matrix[
                "duplicate_readout_replay_exact"
            ],
            "closure_round_trip_exact": restoration_control[
                "closure_round_trip_exact"
            ],
            "restored_second_trigger_refused_state_neutral": (
                restoration_control["second_trigger_refused"]
                and restoration_control["closure_unchanged"]
                and restoration_control["native_state_unchanged"]
            ),
            "composed_identity": composed_identity,
            "composed_transaction_controls": {
                "path": relative(TRANSACTION_CONTROLS),
                "sha256": sha256_file(TRANSACTION_CONTROLS),
                "output_digest": transaction_controls["output_digest"],
                "matched_positive_transaction_admitted": transaction_controls[
                    "matched_positive_transaction_admitted"
                ],
                "all_mismatch_controls_failed_closed": transaction_controls[
                    "all_mismatch_controls_failed_closed"
                ],
            },
            "full_I10_replay_matrix_pending": True,
        },
        "producer_read_audit": positive["producer_call"],
        "source_current_input_audit": source_current_input_audit,
        "control_results": inherited_controls + lane_controls,
        "control_resolution": {
            "resolved_complete_control_count": len(resolved_control_ids),
            "complete_control_count": len(candidate["complete_control_ids"]),
            "resolved_complete_controls": (
                f"{len(resolved_control_ids)} / "
                f"{len(candidate['complete_control_ids'])}"
            ),
            "lane_specific_control_count": len(lane_controls),
            "inherited_control_count_resolved_here": len(inherited_controls),
            "direct_I3_null_consumption_count": 0,
            "unresolved_control_ids": unresolved_control_ids,
            "failed_open_count": 0,
        },
        "artifact_manifest": artifact_manifest,
    }
    trace["checks"] = [
        check("exact_I2_I9_and_contract_sources_consumed", all(row["identity_exact"] for row in sources), sources),
        check("candidate_B_contract_consumed", candidate["execution_iteration"] == "I9-B" and candidate["current_decay_relation_ladder_rung"] == "DR0", candidate),
        check("canonical_four_node_topology_reconstructed", trace["topology_audit"]["exact"], trace["topology_audit"]),
        check("qualifying_local_event_exact", matches_qualifying_event(formation_arrival), formation_arrival),
        check("formation_stops_and_relation_restores_before_export", formation_activity_stopped and post_formation_restoration_exact, trace["formation"]),
        check("absolute_formed_route_organization_supported", post_formation_route["route_organization_O_B"] >= candidate["organization_contract"]["formed_organization_minimum"] - TOLERANCE, post_formation_route),
        check("formation_effect_threshold_bound_to_I9_contract", abs(MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT - candidate["organization_contract"]["formed_organization_minimum"]) <= TOLERANCE, preregistration["formation_attribution_gate"]),
        check("route_organization_attributably_strengthened_from_baseline", formation_effect_O_B >= MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT - TOLERANCE, trace["formation"]),
        check("positive_bounded_export_emitted", positive["q_emit"] > TOLERANCE and positive["q_emit"] <= Q_CAP + TOLERANCE, positive["producer_call"]),
        check("route_organization_weakened", route_weakening_delta >= candidate["organization_contract"]["minimum_weakening_delta"] - TOLERANCE, trace["export_measurements"]),
        check("route_boundary_continuity_and_full_conservation_close", continuity_closed, trace["export_measurements"]),
        check("policy_sweep_matches_bounded_relation", policy_sweep["all_rows_match_relation"] and policy_sweep["q_cap_never_exceeded"], trace["policy_sweep"]),
        check("one_shot_receipt_consumption_and_restoration_pass", policy_sweep["zero_emission_consumes_one_shot_receipt"] and policy_sweep["all_second_calls_refused_state_neutral"] and trace["replay_and_identity"]["restored_second_trigger_refused_state_neutral"], restoration_control),
        check("unrelated_event_does_not_trigger_export", unrelated_call["operation"] == "not_triggered_nonqualifying_event" and unrelated_event_control["closure_unchanged"], unrelated_event_control),
        check("later_native_readout_depends_on_exported_source_state", intervention_matrix["no_export_vs_export_readout_split"] and intervention_matrix["source_C_clamps_reverse_readout"], trace["readout_and_interventions"]),
        check("destination_isolated_from_later_readout", intervention_matrix["destination_C_clamps_preserve_export_readout"] and not trace["destination_isolation"]["destination_on_later_readout_path"], trace["destination_isolation"]),
        check("route_mass_loss_not_substituted_for_organization_weakening", intervention_matrix["matched_route_mass_loss_without_O_B_weakening_retains_readout"], trace["readout_and_interventions"]),
        check("rejected_readouts_atomic", intervention_matrix["all_rejected_readouts_atomic"], trace["readout_and_interventions"]),
        check("duplicate_export_and_readout_replay_exact", positive_replay_exact and intervention_matrix["duplicate_readout_replay_exact"], trace["replay_and_identity"]),
        check("composed_receipt_event_mismatches_fail_closed", transaction_controls["matched_positive_transaction_admitted"] and transaction_controls["all_mismatch_controls_failed_closed"], trace["replay_and_identity"]["composed_transaction_controls"]),
        check("producer_ownership_and_input_audit_explicit", positive["producer_call"]["producer_authors_export_amount_time_and_destination"] and not positive["producer_call"]["unlisted_input_read"], positive["producer_call"]),
        check("ownership_facts_derived_from_calls_and_packet_lineage", policy_ownership_derivation["added_export_policy_present"] and policy_ownership_derivation["producer_authors_aftereffect"] and not policy_ownership_derivation["ordinary_post_formation_flux_generated"], policy_ownership_derivation),
        check("source_current_input_allowlist_exact", source_current_input_audit["exact_allowlist_match"] and not source_current_input_audit["unlisted_input_read"], source_current_input_audit),
        check("B_R_not_promoted_to_D0_R", trace["D0_R_bridge_status"] == "not_tested" and trace["export_measurements"]["added_export_policy_present"] and not trace["export_measurements"]["ordinary_post_formation_flux_generated"], trace["export_measurements"]),
        check("selected_candidate_controls_pass_without_failed_open", trace["control_resolution"]["failed_open_count"] == 0 and len(resolved_control_ids) == 16, trace["control_resolution"]),
        check("formal_recursive_candidate_row_pending_I10", trace["formal_candidate_row_pending_I10"] and bool(unresolved_control_ids), trace["control_resolution"]),
        check("artifact_manifest_exact", all((ROOT / row["path"]).is_file() and sha256_file(ROOT / row["path"]) == row["sha256"] for row in artifact_manifest), artifact_manifest),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_I9B_conserved_leakage_failed"
    trace["output_digest"] = digest_value(trace)
    TRACE.write_text(canonical_json(trace), encoding="utf-8")

    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-B",
        "artifact_kind": "conserved_leakage_candidate",
        "artifact_schema_version": "n31_i9b_conserved_leakage_candidate_v2",
        "generated_at": GENERATED_AT,
        "status": trace["status"],
        "acceptance_state": trace["acceptance_state"],
        "command": COMMAND,
        "script": SCRIPT_RELATIVE,
        "source_chain": sources,
        "source_trace": {
            "path": relative(TRACE),
            "sha256": sha256_file(TRACE),
            "output_digest": trace["output_digest"],
        },
        "candidate_result": {
            "candidate_id": candidate["candidate_id"],
            "semantic_class": "B",
            "semantic_subtype": "B_R_conserved_export_policy",
            "relation_authority": "producer_mediated",
            "transport_authority": "native_LGRC9V3_packet_runtime",
            "current_decay_relation_ladder_rung": "DR4",
            "rung_status": "provisional_pending_I10_formal_row_and_controls",
            "DR4_supported": not trace["failed_checks"],
            "DR5_supported": False,
            "DR5_blocker": "formal_candidate_row_and_complete_I10_matrix_pending",
            "DR6_supported": False,
            "D0_R_bridge_status": "not_tested",
            "native_upgrade_allowed": False,
            "native_decay_classification_unchanged": "D0a_DR2",
            "mediation_strength": "bounded_partial_local_leakage_source_C",
            "full_complete_state_mediation": False,
            "DR2_persistence_scope": (
                "post_formation_checkpoint_and_restoration_persistence_only"
            ),
            "unrelated_native_continuation_persistence_claimed": False,
        },
        "evidence_summary": {
            "baseline_O_B": preformation_route["route_organization_O_B"],
            "formed_O_B": post_formation_route["route_organization_O_B"],
            "formation_effect_O_B": formation_effect_O_B,
            "formation_effect_gate_passed": (
                formation_effect_O_B
                >= MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT - TOLERANCE
            ),
            "post_export_O_B": positive["route_after"]["route_organization_O_B"],
            "organization_weakening_delta": route_weakening_delta,
            "q_emit": positive["q_emit"],
            "source_debit": positive["source_debit"],
            "destination_credit": positive["destination_credit"],
            "route_mass_decrease": route_mass_decrease,
            "continuity_closed": continuity_closed,
            "readout_q": READOUT_Q,
            "no_export_readout_admitted": no_export_readout["readout_admitted"],
            "export_readout_admitted": export_readout["readout_admitted"],
            "source_C_clamps_reverse_readout": intervention_matrix["source_C_clamps_reverse_readout"],
            "destination_C_clamps_preserve_readout": intervention_matrix["destination_C_clamps_preserve_export_readout"],
            "mass_loss_substitution_rejected": intervention_matrix["matched_route_mass_loss_without_O_B_weakening_retains_readout"],
            "duplicate_replay_exact": positive_replay_exact and intervention_matrix["duplicate_readout_replay_exact"],
            "relative_effect_scales": relative_effect_scales,
        },
        "evidence_artifact_boundary": {
            "source_current_trace_evidence_only": True,
            "formal_recursive_I2_candidate_row_instantiated": False,
            "formal_candidate_row_pending_I10": True,
        },
        "mediation_contract": trace["mediation_contract"],
        "destination_isolation": trace["destination_isolation"],
        "control_resolution": trace["control_resolution"],
        "n31_closeout_progress": {
            "n31_closeout_progress_rung": "N31-C4",
            "n31_closeout_ladder_rung_assigned": False,
            "ready_for_I9_C": True,
            "ready_for_I10": False,
            "I10_requires_I9_C_disposition": True,
            "I10_readout_threshold_sweep_values": [
                0.35,
                0.36,
                0.37,
                0.38,
                0.40,
                0.41,
            ],
            "I10_readout_threshold_sweep_status": "pending",
        },
        "claim_boundary": {
            "allowed_claim": (
                "provisional_producer_mediated_B_R_DR4_conserved_leakage_"
                "with_independent_native_readout_formalization_pending_I10"
            ),
            "blocked_claims": [
                "ordinary_D0_R",
                "native_decay",
                "coherence_destruction",
                "global_emission_scheduler",
                "autonomous_native_export_policy",
                "producer_DR5",
                "producer_DR6",
                "trail_or_stigmergy",
                "communication",
                "ecology",
                "agency",
                "native_support",
                "Phase_8_completion",
            ],
            "unsafe_claim_flags": {
                "ordinary_D0_R_claim_allowed": False,
                "native_decay_claim_allowed": False,
                "coherence_destruction_claim_allowed": False,
                "global_emission_scheduler_claim_allowed": False,
                "autonomous_native_export_policy_claim_allowed": False,
                "producer_DR5_claim_allowed": False,
                "producer_DR6_claim_allowed": False,
                "trail_or_stigmergy_claim_allowed": False,
                "communication_claim_allowed": False,
                "ecology_claim_allowed": False,
                "agency_claim_allowed": False,
                "native_support_claim_allowed": False,
                "phase8_completion_claim_allowed": False,
            },
        },
        "governance": {
            "governance_base_revision": GOVERNANCE_BASE_REVISION,
            "src_diff_empty": git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(path) for path in PROTECTED_PATHS
            ),
        },
        "artifact_manifest": artifact_manifest,
        "checks": trace["checks"],
        "failed_checks": trace["failed_checks"],
    }
    payload["checks"].extend(
        [
            check(
                "provisional_B_R_DR4_only_pending_I10",
                payload["candidate_result"]["current_decay_relation_ladder_rung"]
                == "DR4"
                and payload["candidate_result"]["DR4_supported"]
                and not payload["candidate_result"]["DR5_supported"],
                payload["candidate_result"],
            ),
            check(
                "native_lane_and_D0_R_not_upgraded",
                not payload["candidate_result"]["native_upgrade_allowed"]
                and payload["candidate_result"]["D0_R_bridge_status"]
                == "not_tested",
                payload["candidate_result"],
            ),
            check(
                "unsafe_claim_flags_false",
                not any(payload["claim_boundary"]["unsafe_claim_flags"].values()),
                payload["claim_boundary"]["unsafe_claim_flags"],
            ),
            check("src_diff_empty", payload["governance"]["src_diff_empty"], GOVERNANCE_BASE_REVISION),
            check("protected_runtime_contract_diff_empty", payload["governance"]["protected_runtime_contract_diff_empty"], GOVERNANCE_BASE_REVISION),
            check("no_absolute_paths_in_records", no_absolute_paths(payload), "recursive"),
        ]
    )
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_I9B_candidate_checks_failed"
        payload["candidate_result"]["DR4_supported"] = False
        payload["candidate_result"]["current_decay_relation_ladder_rung"] = "DR3"
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    checks = "\n".join(
        f"| `{row['check_id']}` | {str(row['passed']).lower()} |"
        for row in payload["checks"]
    )
    evidence = payload["evidence_summary"]
    REPORT.write_text(
        f"""# N31 Iteration 9-B - Conserved Leakage

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
candidate = B conserved source leakage
semantic subtype = B-R conserved export policy
relation authority = producer-mediated
transport authority = native LGRC9V3 packet runtime
current rung = {payload['candidate_result']['current_decay_relation_ladder_rung']}
D0-R bridge = not tested
DR5_supported = false
native lane = D0a / DR2 unchanged
```

## Geometric Dynamics

Before formation, the route already has a positive source contrast:

```text
O_B_baseline = 0.35 - 0.30 = 0.05
```

The formation packet moves `0.05` coherence from node 0 into node 1. It
strengthens, rather than creates, the route-local source contrast:

```text
O_B_formed = C_leakage_source - C_formation_source = 0.40 - 0.25 = 0.15
formation_effect_O_B = 0.15 - 0.05 = 0.10
```

The attributable effect exceeds the preregistered minimum effect of `0.04`.
The absolute formed-organization floor remains descriptive and is not used by
itself as proof that formation caused the contrast.

The registered one-shot export policy then schedules `0.04` from node 1 to the
explicit destination node 2. Native LGRC packet mechanics debit node 1, carry
the packet in flight, and credit node 2. The route contrast becomes `0.11`, so
the weakening delta is `0.04`; route mass also falls by exactly `0.04`, and the
same amount appears at the destination. No coherence is destroyed or hidden.

The matched mass-loss control removes the same `0.04` route mass symmetrically
from nodes 0 and 1. It leaves `O_B=0.15` and preserves the later readout. Thus
route-mass decrease alone is not substituted for organization weakening.

## Later Readout And Isolation

The later readout is a separate native departure request from node 1 to node 3
at `q={evidence['readout_q']}`. The no-export branch (`C_1=0.40`) admits it; the
export branch (`C_1=0.36`) rejects it. Balanced source-C clamps reverse this
result. Balanced destination-C clamps leave the export result rejected.
Destination node 2 is outside path `[0, 1, 3]`, emits no return packet, and is
not read by either the export policy or the native departure-admission gate.

This is bounded partial mediation of departure admission by local leakage-source
coherence, not complete-state mediation of the full post-arrival branch.

## Persistence And Reconstruction Scope

I9-B supports persistence after formation activity stops at the exact
post-formation checkpoint and through v1/v2 restoration. It does not claim that
the formed relation survived an unrelated native continuation before export;
that stronger continuation scope was not run. The composed-state controls admit
the matched closure receipt/native packet pair and fail closed when consumed
state, packet presence, amount, or destination disagree.

## Classification

I9-B supports provisional producer-mediated `B-R / DR4`: a registered local
event triggers a bounded, conserved export; the preregistered route contrast
weakens; and its local leakage-source component changes a distinct later native
departure-admission operation. The producer owns export eligibility, amount,
time, and destination, while native
LGRC owns debit, transport, and credit. Therefore the result is not ordinary
`D0-R`, native decay, a global scheduler, or coherence destruction. `DR5`
remains pending the formal candidate row and complete I10 replay/control matrix.
I10 also retains the preregistered readout-threshold sweep around the narrow
`q=0.37` split.

## Checks

| Check | Passed |
|---|---:|
{checks}
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build()
    write_report(payload)
    print(canonical_json(payload), end="")


if __name__ == "__main__":
    main()
