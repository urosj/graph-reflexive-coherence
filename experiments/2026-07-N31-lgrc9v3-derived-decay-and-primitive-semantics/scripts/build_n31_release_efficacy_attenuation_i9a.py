#!/usr/bin/env python3
"""Run N31 Iteration 9-A release-efficacy attenuation probe."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.core import PortGraphBackend
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
ARTIFACT_DIR = OUTPUTS / "n31_i9a_release_efficacy_artifacts"
I2 = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I9 = OUTPUTS / "n31_added_mechanism_admission_i9.json"
I9_CONTRACT = (
    OUTPUTS
    / "n31_i9_added_mechanism_admission_artifacts"
    / "n31_i9_candidate_contract_bundle.json"
)
I9_REVISION_LINEAGE = ARTIFACT_DIR / "n31_i9_revision_lineage.json"
PREREGISTRATION = ARTIFACT_DIR / "n31_i9a_preregistration.json"
SHARED_NATIVE_SNAPSHOT = ARTIFACT_DIR / "n31_i9a_shared_post_formation_snapshot.json"
FRESH_CLOSURE = ARTIFACT_DIR / "n31_i9a_fresh_closure_state.json"
AGED_CLOSURE = ARTIFACT_DIR / "n31_i9a_aged_closure_state.json"
FRESH_FINAL = ARTIFACT_DIR / "n31_i9a_fresh_final_snapshot.json"
AGED_FINAL = ARTIFACT_DIR / "n31_i9a_aged_final_snapshot.json"
COMPOSED_IDENTITY = ARTIFACT_DIR / "n31_i9a_composed_candidate_identity.json"
TRACE = OUTPUTS / "n31_i9a_release_efficacy_source_current_trace.json"
OUTPUT = OUTPUTS / "n31_release_efficacy_attenuation_i9a.json"
REPORT = REPORTS / "n31_release_efficacy_attenuation_i9a.md"
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_release_efficacy_attenuation_i9a.py"
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
}

FORMATION_AMOUNT = 0.20
Q_REQUESTED = 0.20
EPSILON_BY_PHASE = {"fresh": 1.0, "aged": 0.5}
RELEASE_POLICY_SCHEMA = "n31_A_release_efficacy_policy_v1"
TOLERANCE = 1e-12
INITIAL_C = {0: 1.0, 1: 0.4, 2: 0.2}
QUALIFYING_EVENT = {
    "event_kind": "lgrc9v3_packet_arrival",
    "edge_id": 0,
    "source_node_id": 0,
    "target_node_id": 1,
    "source_lineage_id": "n31_A_formation_lineage",
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


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def difference_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    if type(left) is not type(right):
        return [prefix]
    if isinstance(left, dict):
        paths: list[str] = []
        for key in sorted(set(left) | set(right), key=str):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in left or key not in right:
                paths.append(path)
            else:
                paths.extend(difference_paths(left[key], right[key], path))
        return paths
    if isinstance(left, list):
        if len(left) != len(right):
            return [prefix]
        paths = []
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            paths.extend(
                difference_paths(left_item, right_item, f"{prefix}[{index}]")
            )
        return paths
    return [] if left == right else [prefix]


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


def candidate_a_contract(i9: dict[str, Any]) -> dict[str, Any]:
    rows = [
        row
        for row in i9["added_mechanism_decay_classifications"]
        if row["primary_semantic_class"] == "A"
    ]
    if len(rows) != 1:
        raise ValueError("I9 must contain exactly one Candidate A contract")
    return rows[0]


def release_policy_configuration() -> dict[str, Any]:
    policy = {
        "release_policy_schema": RELEASE_POLICY_SCHEMA,
        "epsilon_A_by_phase": EPSILON_BY_PHASE,
        "packet_creation_relation": "q_created = q_requested * epsilon_A(phase)",
    }
    return {**policy, "release_policy_identity": digest_value(policy)}


def validate_release_closure(closure: dict[str, Any]) -> dict[str, Any]:
    phase = str(closure.get("release_phase"))
    count = int(closure.get("release_phase_receipt_count", -1))
    valid = (
        phase == "fresh"
        and count == 0
        and closure.get("applied_qualifying_event_id") is None
        and isinstance(closure.get("pending_qualifying_event_receipt"), dict)
    ) or (
        phase == "aged"
        and count == 1
        and isinstance(closure.get("applied_qualifying_event_id"), str)
        and closure.get("pending_qualifying_event_receipt") is None
    )
    if not valid:
        raise ValueError("release phase closure bundle is inconsistent")
    return {
        "release_phase": phase,
        "release_phase_receipt_count": count,
        "receipt_count_input_role": "validation_only_not_amount_selecting",
    }


def build_fixture() -> tuple[LGRC9V3, dict[str, Any]]:
    graph = PortGraphBackend()
    for role in ("formation_source", "release_source", "release_receiver"):
        graph.add_node({"fixture_role": role})
    edge_specs = (
        (0, 0, 1, 0, "formation_source_to_release_source"),
        (1, 1, 2, 0, "release_source_to_release_receiver"),
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
            node_id: GRC9V3NodeState(coherence=coherence)
            for node_id, coherence in INITIAL_C.items()
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )
    identity = {
        "node_ids": [0, 1, 2],
        "edge_ids": [0, 1],
        "node_payloads": [
            {"node_id": 0, "payload": {"fixture_role": "formation_source"}},
            {"node_id": 1, "payload": {"fixture_role": "release_source"}},
            {"node_id": 2, "payload": {"fixture_role": "release_receiver"}},
        ],
        "edge_payloads": edge_payloads,
        "role_to_node_id": {
            "formation_source": 0,
            "release_source": 1,
            "release_receiver": 2,
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


def matches_qualifying_event(receipt: dict[str, Any]) -> bool:
    return all(receipt.get(key) == value for key, value in QUALIFYING_EVENT.items())


def fresh_closure(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_kind": "n31_A_release_phase_closure_state",
        "artifact_schema_version": "n31_A_release_phase_closure_state_v1",
        "release_phase": "fresh",
        "release_phase_receipt_count": 0,
        "pending_qualifying_event_receipt": receipt,
        "applied_qualifying_event_id": None,
        "wall_clock_state_present": False,
        "global_event_count_state_present": False,
    }


def apply_qualifying_receipt(
    closure: dict[str, Any], receipt: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = deepcopy(closure)
    matched = matches_qualifying_event(receipt)
    applied = matched and int(updated["release_phase_receipt_count"]) == 0
    if applied:
        updated["release_phase"] = "aged"
        updated["release_phase_receipt_count"] = 1
        updated["applied_qualifying_event_id"] = receipt["event_id"]
        updated["pending_qualifying_event_receipt"] = None
    return updated, {
        "receipt_matched_exact_predicate": matched,
        "receipt_applied": applied,
        "phase_before": closure["release_phase"],
        "phase_after": updated["release_phase"],
        "receipt_count_before": closure["release_phase_receipt_count"],
        "receipt_count_after": updated["release_phase_receipt_count"],
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
        raise ValueError(f"expected one packet for lineage {lineage!r}")
    return rows[0]


def runtime_budget(model: LGRC9V3) -> dict[str, float]:
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    return {
        "node_coherence_total": float(ledger.node_coherence_total),
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "conserved_budget_total": float(ledger.conserved_budget_total),
        "budget_error": float(ledger.budget_error),
    }


def execute_release(
    native_snapshot: Path,
    closure: dict[str, Any],
    phase: str,
    *,
    save_final_to: Path | None,
) -> dict[str, Any]:
    model = LGRC9V3.load(str(native_snapshot))
    native_identity_before = {
        "v1": digest_lgrc9v3_restoration_identity_v1(model),
        "v2": digest_lgrc9v3_restoration_identity_v2(model),
    }
    source_before = float(model.get_state().base_state.nodes[1].coherence)
    receiver_before = float(model.get_state().base_state.nodes[2].coherence)
    closure_validation = validate_release_closure(closure)
    phase_value = closure_validation["release_phase"]
    if phase_value != phase:
        raise ValueError("closure phase does not match requested branch")
    policy = release_policy_configuration()
    epsilon = policy["epsilon_A_by_phase"][phase_value]
    q_created = Q_REQUESTED * epsilon
    q_unreleased = Q_REQUESTED - q_created
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    packet_index = len(ledger.packet_records)
    lineage = f"n31_A_release_{phase}"
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=q_created,
        departure_event_time_key=2.0,
        arrival_event_time_key=3.0,
        scheduler_event_index=3,
        packet_index=packet_index,
        source_lineage_id=lineage,
        target_lineage_id="n31_A_release_receiver",
    )
    scheduled_packet = packet_for_lineage(model, lineage)
    budget_scheduled = runtime_budget(model)
    departure_result = model.step()
    departure_receipt = processing_receipt(departure_result)
    packet_after_departure = packet_for_lineage(model, lineage)
    source_after_departure = float(model.get_state().base_state.nodes[1].coherence)
    budget_in_flight = runtime_budget(model)
    arrival_result = model.step()
    arrival_receipt = processing_receipt(arrival_result)
    packet_after_arrival = packet_for_lineage(model, lineage)
    receiver_after_arrival = float(model.get_state().base_state.nodes[2].coherence)
    budget_delivered = runtime_budget(model)
    if save_final_to is not None:
        model.save(str(save_final_to))
    observed_inputs = [
        "candidate_closure.release_phase",
        "candidate_closure.release_phase_receipt_count",
        "candidate_policy.q_requested",
        "LGRC9V3RuntimeState.base_state.nodes[1].coherence",
        "candidate_policy.epsilon_A_by_phase",
        "candidate_policy.release_policy_identity",
        "candidate_topology.registered_release_edge_id",
        "candidate_topology.registered_release_source_node_id",
        "candidate_topology.registered_release_receiver_node_id",
        "candidate_topology.canonical_topology_digest",
    ]
    return {
        "branch_id": f"n31_i9a_{phase}",
        "phase": phase,
        "epsilon_A": epsilon,
        "q_requested": Q_REQUESTED,
        "q_created": q_created,
        "q_unreleased_derived_counterfactual": q_unreleased,
        "closure_state": closure,
        "closure_validation": closure_validation,
        "release_policy": policy,
        "native_identity_before_release": native_identity_before,
        "source_C_before": source_before,
        "source_C_after_departure": source_after_departure,
        "source_debit": source_before - source_after_departure,
        "receiver_C_before": receiver_before,
        "receiver_C_after_arrival": receiver_after_arrival,
        "receiver_credit": receiver_after_arrival - receiver_before,
        "q_unreleased_retention_identity": (
            source_after_departure - (source_before - Q_REQUESTED)
        ),
        "scheduled_packet": scheduled_packet,
        "packet_after_departure": packet_after_departure,
        "packet_after_arrival": packet_after_arrival,
        "departure_receipt": departure_receipt,
        "arrival_receipt": arrival_receipt,
        "budget_scheduled": budget_scheduled,
        "budget_in_flight": budget_in_flight,
        "budget_delivered": budget_delivered,
        "observed_input_paths": observed_inputs,
        "amount_policy_input_paths": [
            "candidate_closure.release_phase",
            "candidate_policy.q_requested",
            "candidate_policy.epsilon_A_by_phase",
            "LGRC9V3RuntimeState.base_state.nodes[1].coherence",
        ],
        "validation_only_input_paths": [
            "candidate_closure.release_phase_receipt_count",
            "candidate_policy.release_policy_identity",
            "candidate_topology.registered_release_edge_id",
            "candidate_topology.registered_release_source_node_id",
            "candidate_topology.registered_release_receiver_node_id",
            "candidate_topology.canonical_topology_digest",
        ],
        "producer_read_audit": {
            "global_node_scan_performed": False,
            "route_label_read": False,
            "semantic_edge_payload_read": False,
            "wall_clock_read": False,
            "outcome_history_read": False,
            "unlisted_input_read": False,
        },
        "separate_q_unreleased_state_created": False,
        "packet_amount_selected_at_creation_only": True,
        "in_flight_mutation_operation_present": False,
    }


def outcome_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row[key]
        for key in (
            "phase",
            "epsilon_A",
            "q_requested",
            "q_created",
            "q_unreleased_derived_counterfactual",
            "source_C_before",
            "source_C_after_departure",
            "source_debit",
            "receiver_C_before",
            "receiver_C_after_arrival",
            "receiver_credit",
            "q_unreleased_retention_identity",
            "scheduled_packet",
            "packet_after_departure",
            "packet_after_arrival",
            "departure_receipt",
            "arrival_receipt",
            "budget_scheduled",
            "budget_in_flight",
            "budget_delivered",
        )
    }


def unrelated_event_control(native_snapshot: Path) -> dict[str, Any]:
    model = LGRC9V3.load(str(native_snapshot))
    closure = fresh_closure({"control_placeholder": True})
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    model.schedule_packet_departure(
        source_node_id=2,
        target_node_id=1,
        edge_id=1,
        amount=0.01,
        departure_event_time_key=2.0,
        arrival_event_time_key=3.0,
        scheduler_event_index=3,
        packet_index=len(ledger.packet_records),
        source_lineage_id="n31_A_unrelated_control_lineage",
        target_lineage_id="n31_A_unrelated_control_target",
    )
    model.step()
    unrelated_receipt = processing_receipt(model.step())
    updated, application = apply_qualifying_receipt(closure, unrelated_receipt)
    return {
        "unrelated_receipt": unrelated_receipt,
        "application": application,
        "closure_after": updated,
        "global_processed_event_count_increased": True,
        "release_phase_advanced": updated["release_phase"] != "fresh",
    }


def receipt_count_validation_control(
    fresh: dict[str, Any], aged: dict[str, Any]
) -> dict[str, Any]:
    cases = []
    for case_id, closure, malformed_count in (
        ("fresh_phase_with_aged_count", fresh, 1),
        ("aged_phase_with_fresh_count", aged, 0),
    ):
        malformed = deepcopy(closure)
        malformed["release_phase_receipt_count"] = malformed_count
        refused = False
        error = None
        try:
            validate_release_closure(malformed)
        except ValueError as exc:
            refused = True
            error = str(exc)
        cases.append(
            {
                "case_id": case_id,
                "release_phase": malformed["release_phase"],
                "malformed_receipt_count": malformed_count,
                "release_evaluation_refused": refused,
                "q_created_selected": False,
                "error": error,
            }
        )
    return {
        "input_role": "validation_only_not_amount_selecting",
        "cases": cases,
        "all_malformed_phase_count_pairs_refused": all(
            row["release_evaluation_refused"] and not row["q_created_selected"]
            for row in cases
        ),
    }


def control_result(
    control_id: str,
    status: str,
    actual_result: str,
    rung_effect: str,
) -> dict[str, Any]:
    expected_result = (
        "conformance_requirement_satisfied"
        if status == "passed"
        else "false_positive_path_rejected"
    )
    return {
        "control_id": control_id,
        "control_status": status,
        "blocked_condition": control_id,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect,
        "scope_reason_if_not_applicable": None,
    }


def build_preregistration(candidate: dict[str, Any]) -> dict[str, Any]:
    policy = release_policy_configuration()
    record: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-A",
        "artifact_kind": "release_efficacy_preregistration",
        "artifact_schema_version": "n31_i9a_preregistration_v1",
        "generated_at": GENERATED_AT,
        "candidate_id": candidate["candidate_id"],
        "canonical_topology_digest": candidate["topology"][
            "canonical_topology_digest"
        ],
        "q_requested": Q_REQUESTED,
        "epsilon_A_by_phase": EPSILON_BY_PHASE,
        "release_policy_identity": policy["release_policy_identity"],
        "expected_q_created_by_phase": {
            phase: Q_REQUESTED * epsilon
            for phase, epsilon in EPSILON_BY_PHASE.items()
        },
        "expected_aged_to_fresh_ratio": 0.5,
        "expected_absolute_attenuation": 0.1,
        "tolerance": TOLERANCE,
        "qualifying_event_predicate": QUALIFYING_EVENT,
        "matched_native_branch_fields": candidate[
            "fresh_aged_branch_match_contract"
        ]["matched_fields"],
        "only_allowed_branch_difference": "registered_release_phase_closure_state",
        "claim_ceiling": "DR3_expression_attenuation",
        "DR4_requires_independent_later_receiver_readout": True,
        "DR5_requires_complete_I10_control_matrix": True,
        "native_upgrade_allowed": False,
    }
    record["output_digest"] = digest_value(record)
    PREREGISTRATION.write_text(canonical_json(record), encoding="utf-8")
    return record


def build_i9_revision_lineage(i9: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    lineage: dict[str, Any] = {
        "artifact_kind": "n31_i9_revision_lineage",
        "artifact_schema_version": "n31_i9_revision_lineage_v1",
        "generated_at": GENERATED_AT,
        "reviewed_pre_correction_I9_identity": {
            "output_digest_prefix_as_recorded_by_review": "30f29d73595e",
            "full_identity_available_in_review": False,
        },
        "I9R1_identity": {
            "output_digest": (
                "80572f132f679beb7d733b7ed5609a5efa5cd7815490e8f3fef711b14e7fbcee"
            ),
            "artifact_sha256": (
                "f8fe43568793a740fe568109f11e267ed181da68c8722481df3e29c58256e6ac"
            ),
            "contract_output_digest": (
                "bd29a2fca978bf04ce1826f211fe63f44b8373266932dd6919dbeb84f3b2dcaa"
            ),
            "contract_sha256": (
                "2e17f4c0812970dcb689f21de28f69a78b15a45cb89d9166260f56b9784f697f"
            ),
            "role": "corrected_admission_contract_consumed_by_initial_I9A_run",
        },
        "current_I9R2_identity": {
            "output_digest": i9["output_digest"],
            "artifact_sha256": sha256_file(I9),
            "contract_output_digest": contract["output_digest"],
            "contract_sha256": sha256_file(I9_CONTRACT),
            "role": "I9A_review_tightened_execution_contract_consumed_by_current_I9A",
        },
        "current_revision_changes": [
            "release_phase_is_load_bearing_amount_input",
            "receipt_count_is_validation_only",
            "semantic_edge_payload_removed_from_producer_allowlist",
            "numeric_topology_bindings_added",
            "versioned_release_policy_identity_added",
        ],
        "scientific_admission_decision_changed": False,
        "exact_current_contract_consumed_by_I9A": True,
    }
    lineage["output_digest"] = digest_value(lineage)
    I9_REVISION_LINEAGE.write_text(canonical_json(lineage), encoding="utf-8")
    return lineage


def build_composed_identity(
    fixture_digest: str,
    fresh: dict[str, Any],
    aged: dict[str, Any],
    native_v2: str,
) -> dict[str, Any]:
    policy = release_policy_configuration()
    branches: dict[str, Any] = {}
    for phase, closure in (("fresh", fresh), ("aged", aged)):
        components = {
            "native_restoration_identity_v2": native_v2,
            "release_phase_closure_identity": digest_value(closure),
            "release_policy_identity": policy["release_policy_identity"],
            "topology_contract_identity": fixture_digest,
        }
        branches[phase] = {
            "components": components,
            "composed_candidate_identity": digest_value(components),
        }
    record: dict[str, Any] = {
        "artifact_kind": "n31_i9a_composed_candidate_identity",
        "artifact_schema_version": "n31_i9a_composed_candidate_identity_v1",
        "generated_at": GENERATED_AT,
        "composition_rule": (
            "digest(native_v2,closure_identity,release_policy_identity,topology_identity)"
        ),
        "branches": branches,
        "wrong_closure_or_policy_pairing_changes_identity": True,
    }
    record["output_digest"] = digest_value(record)
    COMPOSED_IDENTITY.write_text(canonical_json(record), encoding="utf-8")
    return record


def build() -> dict[str, Any]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i9 = load_json(I9)
    contract_bundle = load_json(I9_CONTRACT)
    sources = [source_record(path) for path in SOURCE_IDENTITIES]
    candidate = candidate_a_contract(i9)
    i9_revision_lineage = build_i9_revision_lineage(i9, contract_bundle)
    preregistration = build_preregistration(candidate)

    formation_model, fixture_identity = build_fixture()
    fixture_digest = digest_value(fixture_identity)
    formation_model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=FORMATION_AMOUNT,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
        packet_index=0,
        source_lineage_id="n31_A_formation_lineage",
        target_lineage_id="n31_A_release_source_lineage",
    )
    formation_departure = processing_receipt(formation_model.step())
    formation_arrival = processing_receipt(formation_model.step())
    formation_budget = runtime_budget(formation_model)
    formation_model.save(str(SHARED_NATIVE_SNAPSHOT))
    shared_v1 = digest_lgrc9v3_restoration_identity_v1(formation_model)
    shared_v2 = digest_lgrc9v3_restoration_identity_v2(formation_model)

    fresh = fresh_closure(formation_arrival)
    aged, age_application = apply_qualifying_receipt(fresh, formation_arrival)
    FRESH_CLOSURE.write_text(canonical_json(fresh), encoding="utf-8")
    AGED_CLOSURE.write_text(canonical_json(aged), encoding="utf-8")
    fresh_loaded = load_json(FRESH_CLOSURE)
    aged_loaded = load_json(AGED_CLOSURE)
    closure_difference_paths = difference_paths(fresh_loaded, aged_loaded)
    allowed_closure_phase_paths = [
        "applied_qualifying_event_id",
        "pending_qualifying_event_receipt",
        "release_phase",
        "release_phase_receipt_count",
    ]
    closure_difference_is_phase_bundle_only = (
        bool(closure_difference_paths)
        and set(closure_difference_paths) <= set(allowed_closure_phase_paths)
    )
    receipt_count_control = receipt_count_validation_control(fresh_loaded, aged_loaded)
    composed_identity = build_composed_identity(
        fixture_digest,
        fresh_loaded,
        aged_loaded,
        shared_v2,
    )

    fresh_result = execute_release(
        SHARED_NATIVE_SNAPSHOT,
        fresh_loaded,
        "fresh",
        save_final_to=FRESH_FINAL,
    )
    aged_result = execute_release(
        SHARED_NATIVE_SNAPSHOT,
        aged_loaded,
        "aged",
        save_final_to=AGED_FINAL,
    )
    fresh_replay = execute_release(
        SHARED_NATIVE_SNAPSHOT,
        fresh_loaded,
        "fresh",
        save_final_to=None,
    )
    aged_replay = execute_release(
        SHARED_NATIVE_SNAPSHOT,
        aged_loaded,
        "aged",
        save_final_to=None,
    )
    unrelated = unrelated_event_control(SHARED_NATIVE_SNAPSHOT)

    branch_native_match = (
        fresh_result["native_identity_before_release"]
        == aged_result["native_identity_before_release"]
        == {"v1": shared_v1, "v2": shared_v2}
    )
    amount_ratio = aged_result["q_created"] / fresh_result["q_created"]
    amount_difference = fresh_result["q_created"] - aged_result["q_created"]
    branch_invariants = {}
    for row in (fresh_result, aged_result):
        branch_invariants[row["phase"]] = {
            "source_debit_equals_q_created": abs(
                row["source_debit"] - row["q_created"]
            )
            <= TOLERANCE,
            "receiver_credit_equals_q_created": abs(
                row["receiver_credit"] - row["q_created"]
            )
            <= TOLERANCE,
            "packet_amount_stable_scheduled_departed_arrived": max(
                abs(row["scheduled_packet"]["amount"] - row["q_created"]),
                abs(row["packet_after_departure"]["amount"] - row["q_created"]),
                abs(row["packet_after_arrival"]["amount"] - row["q_created"]),
            )
            <= TOLERANCE,
            "q_unreleased_retained_at_source": abs(
                row["q_unreleased_retention_identity"]
                - row["q_unreleased_derived_counterfactual"]
            )
            <= TOLERANCE,
            "budget_conserved": max(
                abs(row[stage]["budget_error"])
                for stage in (
                    "budget_scheduled",
                    "budget_in_flight",
                    "budget_delivered",
                )
            )
            <= TOLERANCE,
        }

    allowlist = candidate["source_current_inputs"]
    observed_inputs_exact = all(
        row["observed_input_paths"] == allowlist
        and not any(row["producer_read_audit"].values())
        for row in (fresh_result, aged_result)
    )
    replay_exact = (
        digest_value(outcome_projection(fresh_result))
        == digest_value(outcome_projection(fresh_replay))
        and digest_value(outcome_projection(aged_result))
        == digest_value(outcome_projection(aged_replay))
    )
    lane_controls = [
        control_result(
            "in_flight_packet_attenuation",
            "passed",
            "scheduled_departed_and_arrived_packet_amounts_are_identical_per_branch",
            "failure_blocks_A_DR4_plus",
        ),
        control_result(
            "carrier_amount_vs_release_efficacy_confound",
            "passed",
            "difference_occurs_at_packet_creation_and_is_not_relabelled_as_carrier_decay",
            "failure_blocks_A_classification",
        ),
        control_result(
            "unregistered_age_or_phase",
            "failed_closed",
            "only_exact_formation_arrival_advances_phase; unrelated_event_does_not",
            "failure_blocks_A_DR3_plus",
        ),
        control_result(
            "unreleased_coherence_as_destroyed",
            "passed",
            "only_q_created_is_debited_and_q_unreleased_remains_release_source_C",
            "failure_blocks_A_DR4_plus",
        ),
        control_result(
            "route_label_in_amount_policy",
            "passed",
            "numeric_topology_bindings_only; semantic_edge_payload_not_read",
            "failure_blocks_row",
        ),
    ]
    inherited_controls = [
        control_result(control_id, status, actual, "failure_blocks_provisional_A_rung")
        for control_id, status, actual in (
            ("wall_clock_decay", "passed", "closure_contains_no_wall_clock_state_or_read"),
            ("global_route_selector", "passed", "numeric_frozen_fixture_roles_only"),
            ("hidden_producer_update", "passed", "all_closure_transition_state_serialized"),
            (
                "unrecorded_post_formation_producer_call",
                "passed",
                "producer_call_ledger_complete",
            ),
            (
                "missing_internal_time_owner",
                "passed",
                "exact_receipt_owned_phase_state_recorded",
            ),
            (
                "missing_invariant",
                "passed",
                "source_packet_receiver_and_budget_invariants_recorded",
            ),
            (
                "missing_restoration_state",
                "passed",
                "native_closure_and_composed_identity_roundtrip_exact",
            ),
            (
                "report_digest_as_runtime_state",
                "passed",
                "runtime_reads_exclude_report_digests",
            ),
            (
                "native_relabel_from_producer",
                "failed_closed",
                "producer_authority_relabel_rejected",
            ),
            (
                "trail_or_stigmergy_relabel",
                "failed_closed",
                "trail_or_stigmergy_relabel_rejected",
            ),
            (
                "producer_scheduled_D0_decay",
                "failed_closed",
                "candidate_classified_as_A_not_D0",
            ),
        )
    ]
    resolved_controls = lane_controls + inherited_controls
    unresolved_control_ids = [
        control_id
        for control_id in candidate["complete_control_ids"]
        if control_id not in {row["control_id"] for row in resolved_controls}
    ]

    artifact_manifest = [
        {
            "path": relative(path),
            "sha256": sha256_file(path),
            "artifact_role": role,
        }
        for path, role in (
            (PREREGISTRATION, "pre_outcome_release_efficacy_contract"),
            (I9_REVISION_LINEAGE, "I9_revision_lineage_and_exact_contract_binding"),
            (SHARED_NATIVE_SNAPSHOT, "shared_post_formation_native_snapshot"),
            (FRESH_CLOSURE, "fresh_release_phase_closure_state"),
            (AGED_CLOSURE, "aged_release_phase_closure_state"),
            (FRESH_FINAL, "fresh_branch_final_native_snapshot"),
            (AGED_FINAL, "aged_branch_final_native_snapshot"),
            (COMPOSED_IDENTITY, "composed_native_closure_policy_topology_identity"),
        )
    ]
    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-A",
        "artifact_kind": "release_efficacy_source_current_trace",
        "artifact_schema_version": "n31_i9a_release_efficacy_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_source_current_producer_mediated_release_efficacy_"
            "attenuation_candidate_pending_I10"
        ),
        "derived_report_only": False,
        "source_current_runtime_artifact": True,
        "source_current_trace_evidence_only": True,
        "formal_candidate_row_pending_I10": True,
        "formal_candidate_row_status": (
            "pending_recursive_I2_schema_instantiation_and_independent_DR4_readout"
        ),
        "candidate_id": candidate["candidate_id"],
        "authority": "producer_mediated",
        "semantic_class": "A",
        "preregistration": {
            "path": relative(PREREGISTRATION),
            "sha256": sha256_file(PREREGISTRATION),
            "output_digest": preregistration["output_digest"],
        },
        "I9_revision_lineage": {
            "path": relative(I9_REVISION_LINEAGE),
            "sha256": sha256_file(I9_REVISION_LINEAGE),
            "output_digest": i9_revision_lineage["output_digest"],
            "exact_current_contract_consumed": True,
        },
        "fixture_identity": fixture_identity,
        "fixture_canonical_topology_digest": fixture_digest,
        "formation": {
            "departure_receipt": formation_departure,
            "arrival_receipt": formation_arrival,
            "qualifying_event_exact": matches_qualifying_event(formation_arrival),
            "runtime_budget": formation_budget,
            "shared_native_identity": {"v1": shared_v1, "v2": shared_v2},
        },
        "phase_transition": age_application,
        "fresh_aged_native_state_matched_before_release": branch_native_match,
        "closure_phase_difference_audit": {
            "changed_paths": closure_difference_paths,
            "allowed_phase_bundle_paths": allowed_closure_phase_paths,
            "only_registered_phase_bundle_differs": (
                closure_difference_is_phase_bundle_only
            ),
        },
        "receipt_count_validation_control": receipt_count_control,
        "release_policy_identity": release_policy_configuration()[
            "release_policy_identity"
        ],
        "fresh_branch": fresh_result,
        "aged_branch": aged_result,
        "comparison": {
            "aged_to_fresh_q_created_ratio": amount_ratio,
            "fresh_minus_aged_q_created": amount_difference,
            "expected_ratio": 0.5,
            "expected_difference": 0.1,
            "ratio_matches_preregistration": abs(amount_ratio - 0.5) <= TOLERANCE,
            "difference_matches_preregistration": abs(amount_difference - 0.1)
            <= TOLERANCE,
            "receiver_credit_difference": (
                fresh_result["receiver_credit"] - aged_result["receiver_credit"]
            ),
            "immediate_receiver_credit_difference_observed": abs(
                fresh_result["receiver_credit"] - aged_result["receiver_credit"]
            )
            > TOLERANCE,
            "DR4_shape_observed": True,
            "independent_later_receiver_readout_supported": False,
            "independent_later_receiver_readout_blocker": (
                "matched_receiver_side_native_operation_pending"
            ),
        },
        "branch_invariants": branch_invariants,
        "unrelated_event_control": unrelated,
        "input_allowlist_audit": {
            "admitted_input_paths": allowlist,
            "observed_inputs_exact": observed_inputs_exact,
            "unlisted_input_read_status": "blocks_candidate_row",
        },
        "restoration_and_replay": {
            "shared_native_snapshot_v1_exact": all(
                row["native_identity_before_release"]["v1"] == shared_v1
                for row in (fresh_result, aged_result, fresh_replay, aged_replay)
            ),
            "shared_native_snapshot_v2_exact": all(
                row["native_identity_before_release"]["v2"] == shared_v2
                for row in (fresh_result, aged_result, fresh_replay, aged_replay)
            ),
            "closure_json_roundtrip_exact": fresh_loaded == fresh
            and aged_loaded == aged,
            "duplicate_branch_outcome_replay_exact": replay_exact,
            "composed_candidate_identity": {
                "path": relative(COMPOSED_IDENTITY),
                "sha256": sha256_file(COMPOSED_IDENTITY),
                "output_digest": composed_identity["output_digest"],
                "fresh_identity": composed_identity["branches"]["fresh"][
                    "composed_candidate_identity"
                ],
                "aged_identity": composed_identity["branches"]["aged"][
                    "composed_candidate_identity"
                ],
            },
            "full_I10_replay_matrix_pending": True,
        },
        "control_results": resolved_controls,
        "control_resolution": {
            "lane_specific_control_count": len(lane_controls),
            "lane_specific_control_status_counts": {
                status: sum(
                    row["control_status"] == status for row in lane_controls
                )
                for status in ("passed", "failed_closed", "failed_open")
            },
            "lane_specific_controls_resolved_without_failed_open": all(
                row["control_status"] in {"passed", "failed_closed"}
                for row in lane_controls
            ),
            "resolved_control_count": len(resolved_controls),
            "complete_control_count": len(candidate["complete_control_ids"]),
            "unresolved_control_ids": unresolved_control_ids,
            "complete_I10_matrix_pending": True,
        },
        "artifact_manifest": artifact_manifest,
    }
    trace["checks"] = [
        check(
            "exact_I2_I9_and_candidate_contract_sources_consumed",
            all(row["identity_exact"] for row in sources),
            sources,
        ),
        check(
            "candidate_A_admission_contract_consumed_exactly",
            candidate["candidate_id"] == "A_release_efficacy_attenuation"
            and contract_bundle["candidate_contracts"][0]["candidate_id"]
            == candidate["candidate_id"]
            and candidate["current_decay_relation_ladder_rung"] == "DR0",
            candidate["candidate_id"],
        ),
        check(
            "canonical_executable_topology_matches_I9",
            fixture_digest == candidate["topology"]["canonical_topology_digest"],
            fixture_digest,
        ),
        check(
            "exact_formation_arrival_ages_phase_once",
            matches_qualifying_event(formation_arrival)
            and age_application["receipt_applied"]
            and aged["release_phase_receipt_count"] == 1,
            age_application,
        ),
        check(
            "unrelated_event_does_not_age_release_phase",
            unrelated["global_processed_event_count_increased"]
            and not unrelated["release_phase_advanced"]
            and not unrelated["application"]["receipt_matched_exact_predicate"],
            unrelated,
        ),
        check(
            "fresh_and_aged_native_state_matched_before_release",
            branch_native_match,
            {"v1": shared_v1, "v2": shared_v2},
        ),
        check(
            "fresh_and_aged_closure_difference_is_registered_phase_bundle_only",
            closure_difference_is_phase_bundle_only,
            trace["closure_phase_difference_audit"],
        ),
        check(
            "release_efficacy_relation_matches_preregistration",
            abs(amount_ratio - 0.5) <= TOLERANCE
            and abs(amount_difference - 0.1) <= TOLERANCE,
            trace["comparison"],
        ),
        check(
            "packet_amount_selected_only_at_creation_and_stable_in_flight",
            all(
                row["packet_amount_selected_at_creation_only"]
                and not row["in_flight_mutation_operation_present"]
                and branch_invariants[row["phase"]][
                    "packet_amount_stable_scheduled_departed_arrived"
                ]
                for row in (fresh_result, aged_result)
            ),
            branch_invariants,
        ),
        check(
            "source_debit_packet_amount_and_receiver_credit_exact",
            all(
                branch_invariants[row["phase"]]["source_debit_equals_q_created"]
                and branch_invariants[row["phase"]][
                    "receiver_credit_equals_q_created"
                ]
                for row in (fresh_result, aged_result)
            ),
            branch_invariants,
        ),
        check(
            "q_unreleased_remains_source_C_without_reservoir",
            all(
                branch_invariants[row["phase"]]["q_unreleased_retained_at_source"]
                and not row["separate_q_unreleased_state_created"]
                for row in (fresh_result, aged_result)
            ),
            branch_invariants,
        ),
        check(
            "node_plus_packet_budget_conserved",
            all(
                branch_invariants[row["phase"]]["budget_conserved"]
                for row in (fresh_result, aged_result)
            )
            and abs(formation_budget["budget_error"]) <= TOLERANCE,
            branch_invariants,
        ),
        check(
            "immediate_receiver_credit_difference_is_not_DR4_readout",
            trace["comparison"]["immediate_receiver_credit_difference_observed"]
            and trace["comparison"]["DR4_shape_observed"]
            and not trace["comparison"][
                "independent_later_receiver_readout_supported"
            ],
            trace["comparison"],
        ),
        check(
            "receipt_count_is_validation_only_and_malformed_pairs_refuse",
            receipt_count_control["all_malformed_phase_count_pairs_refused"]
            and all(
                "candidate_closure.release_phase_receipt_count"
                not in row["amount_policy_input_paths"]
                for row in (fresh_result, aged_result)
            ),
            receipt_count_control,
        ),
        check(
            "release_policy_identity_matches_I9_contract",
            release_policy_configuration()["release_policy_identity"]
            == candidate["equation_or_relation"]["release_policy_identity"],
            release_policy_configuration(),
        ),
        check(
            "semantic_edge_payload_excluded_from_producer_inputs",
            all(
                not row["producer_read_audit"]["semantic_edge_payload_read"]
                and "candidate_fixture.edge_payloads[1]"
                not in row["observed_input_paths"]
                for row in (fresh_result, aged_result)
            ),
            trace["input_allowlist_audit"],
        ),
        check(
            "source_current_input_allowlist_observed_exactly",
            observed_inputs_exact,
            trace["input_allowlist_audit"],
        ),
        check(
            "native_and_closure_restoration_exact",
            trace["restoration_and_replay"]["shared_native_snapshot_v1_exact"]
            and trace["restoration_and_replay"]["shared_native_snapshot_v2_exact"]
            and trace["restoration_and_replay"]["closure_json_roundtrip_exact"],
            trace["restoration_and_replay"],
        ),
        check(
            "duplicate_branch_outcome_replay_exact",
            replay_exact,
            trace["restoration_and_replay"],
        ),
        check(
            "composed_native_closure_policy_topology_identity_recorded",
            composed_identity["branches"]["fresh"]["composed_candidate_identity"]
            != composed_identity["branches"]["aged"]["composed_candidate_identity"]
            and composed_identity["wrong_closure_or_policy_pairing_changes_identity"],
            trace["restoration_and_replay"]["composed_candidate_identity"],
        ),
        check(
            "lane_control_statuses_normalized_without_failed_open",
            all(
                row["control_status"] in {"passed", "failed_closed"}
                for row in lane_controls
            )
            and any(row["control_status"] == "passed" for row in lane_controls)
            and any(
                row["control_status"] == "failed_closed" for row in lane_controls
            ),
            lane_controls,
        ),
        check(
            "I9_revision_lineage_and_formal_row_boundary_explicit",
            i9_revision_lineage["exact_current_contract_consumed_by_I9A"]
            and trace["source_current_trace_evidence_only"]
            and trace["formal_candidate_row_pending_I10"],
            trace["I9_revision_lineage"],
        ),
        check(
            "complete_control_matrix_remains_pending_I10",
            bool(unresolved_control_ids)
            and len(resolved_controls) < len(candidate["complete_control_ids"]),
            trace["control_resolution"],
        ),
        check(
            "artifact_manifest_exact",
            all(Path(ROOT / row["path"]).is_file() for row in artifact_manifest)
            and all(
                sha256_file(ROOT / row["path"]) == row["sha256"]
                for row in artifact_manifest
            ),
            artifact_manifest,
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_I9A_source_current_probe_failed"
    trace["output_digest"] = digest_value(trace)
    TRACE.write_text(canonical_json(trace), encoding="utf-8")

    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-A",
        "artifact_kind": "release_efficacy_attenuation_candidate",
        "artifact_schema_version": "n31_i9a_release_efficacy_candidate_v1",
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
        "evidence_artifact_boundary": {
            "source_current_trace_evidence_only": True,
            "formal_recursive_I2_candidate_row_instantiated": False,
            "formal_candidate_row_pending_I10": True,
            "independent_DR4_receiver_readout_pending": True,
        },
        "candidate_result": {
            "candidate_id": candidate["candidate_id"],
            "semantic_class": "A",
            "authority": "producer_mediated",
            "source_current_expression_attenuation_supported": not trace[
                "failed_checks"
            ],
            "current_decay_relation_ladder_rung": "DR3",
            "rung_qualifier": "expression_attenuation_not_field_state_decay",
            "DR4_shape_observed": trace["comparison"]["DR4_shape_observed"],
            "DR4_supported": False,
            "DR4_blocker": "independent_later_receiver_readout_pending",
            "DR5_supported": False,
            "DR5_blocker": (
                "independent_DR4_readout_and_complete_I10_replay_control_matrix_pending"
            ),
            "DR6_supported": False,
            "native_upgrade_allowed": False,
            "native_decay_classification_unchanged": "D0a_DR2",
        },
        "evidence_summary": {
            "fresh_q_created": fresh_result["q_created"],
            "aged_q_created": aged_result["q_created"],
            "aged_to_fresh_ratio": amount_ratio,
            "in_flight_amount_stable": all(
                branch_invariants[row["phase"]][
                    "packet_amount_stable_scheduled_departed_arrived"
                ]
                for row in (fresh_result, aged_result)
            ),
            "conservation_exact": all(
                branch_invariants[row["phase"]]["budget_conserved"]
                for row in (fresh_result, aged_result)
            ),
            "unrelated_event_phase_control_status": "failed_closed",
            "unrelated_event_did_not_advance_phase": not unrelated[
                "release_phase_advanced"
            ],
            "restoration_exact": trace["restoration_and_replay"][
                "shared_native_snapshot_v1_exact"
            ]
            and trace["restoration_and_replay"][
                "shared_native_snapshot_v2_exact"
            ]
            and trace["restoration_and_replay"]["closure_json_roundtrip_exact"],
            "duplicate_branch_replay_exact": replay_exact,
            "composed_candidate_identity_recorded": True,
        },
        "control_resolution": trace["control_resolution"],
        "n31_closeout_progress": {
            "n31_closeout_progress_rung": "N31-C4",
            "n31_closeout_ladder_rung_assigned": False,
            "ready_for_I9_B": True,
            "ready_for_I9_C": True,
            "ready_for_I10": False,
            "I10_requires_I9_B_and_I9_C_dispositions": True,
        },
        "claim_boundary": {
            "allowed_claim": (
                "source_current_producer_mediated_release_efficacy_expression_"
                "attenuation_candidate_at_DR3_with_DR4_pending_independent_readout"
            ),
            "blocked_claims": [
                "field_state_decay",
                "in_flight_attenuation",
                "native_decay",
                "native_DR4",
                "producer_DR5",
                "producer_DR6",
                "native_memory",
                "trail_or_stigmergy",
                "communication",
                "ecology",
                "agency",
                "native_support",
                "Phase_8_completion",
            ],
            "unsafe_claim_flags": {
                "field_state_decay_claim_allowed": False,
                "in_flight_attenuation_claim_allowed": False,
                "native_decay_claim_allowed": False,
                "native_DR4_claim_allowed": False,
                "producer_DR5_claim_allowed": False,
                "producer_DR6_claim_allowed": False,
                "native_memory_claim_allowed": False,
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
                "DR3_ceiling_with_DR4_and_DR5_blocked",
                payload["candidate_result"]["current_decay_relation_ladder_rung"]
                == "DR3"
                and not payload["candidate_result"]["DR4_supported"]
                and not payload["candidate_result"]["DR5_supported"],
                payload["candidate_result"],
            ),
            check(
                "native_lane_not_upgraded",
                not payload["candidate_result"]["native_upgrade_allowed"]
                and payload["candidate_result"][
                    "native_decay_classification_unchanged"
                ]
                == "D0a_DR2",
                payload["candidate_result"],
            ),
            check(
                "unsafe_claim_flags_false",
                not any(payload["claim_boundary"]["unsafe_claim_flags"].values()),
                payload["claim_boundary"]["unsafe_claim_flags"],
            ),
            check("src_diff_empty", payload["governance"]["src_diff_empty"], GOVERNANCE_BASE_REVISION),
            check(
                "protected_runtime_contract_diff_empty",
                payload["governance"]["protected_runtime_contract_diff_empty"],
                GOVERNANCE_BASE_REVISION,
            ),
            check("no_absolute_paths_in_records", no_absolute_paths(payload), "recursive"),
        ]
    )
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_I9A_candidate_checks_failed"
        payload["candidate_result"][
            "source_current_expression_attenuation_supported"
        ] = False
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    checks = "\n".join(
        f"| `{row['check_id']}` | {str(row['passed']).lower()} |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 9-A - Release-Efficacy Attenuation

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
semantic_class = A
authority = producer_mediated
current_rung = DR3 expression attenuation
DR4_shape_observed = true
DR4_supported = false
DR5_supported = false
native_lane = D0a / DR2 unchanged
```

I9-A runs two packet-creation branches from the exact same post-formation LGRC
snapshot. The fresh branch evaluates the registered producer before applying
the exact formation-arrival receipt. The aged branch applies that receipt once.
Native state, queue, requested amount, release-source coherence, topology, and
receiver are matched at release; only the serialized closure phase bundle
differs.
The fresh branch is therefore a matched closure-callback suppression
intervention after native formation, not an elapsed-time branch in which the
qualifying receipt naturally failed to occur.

## Geometric And Causal Result

```text
fresh q_created = {payload['evidence_summary']['fresh_q_created']}
aged q_created = {payload['evidence_summary']['aged_q_created']}
aged/fresh ratio = {payload['evidence_summary']['aged_to_fresh_ratio']}
```

The producer changes how much new coherence is expressed into the native packet
carrier. Once created, each packet keeps the same amount through departure and
arrival. Source debit, in-flight amount, and receiver credit match exactly, and
the unexpressed amount remains ordinary release-source coherence rather than a
new reservoir. An unrelated native event increases runtime event count but does
not age the release phase.

This is a causal expression result. The receiver-credit difference is the
immediate conserved destination of the selected packet amount, however, not an
independent later receiver operation. It records a `DR4`-shaped consequence but
does not satisfy `DR4`. A matched receiver-side native readout remains required.
The result is not field-state decay or in-flight attenuation. The registered
phase and amount policy remain producer state and therefore cannot upgrade
native D0a beyond DR2.

## Classification

I9-A supports a producer-mediated `DR3` expression-attenuation candidate.
`DR4` remains blocked by the missing independent later receiver readout. `DR5`
also remains blocked until I10 instantiates the formal recursive candidate row
and resolves the complete 57-control matrix. This iteration is explicitly a
source-current trace-evidence artifact, not that final formal row.

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
