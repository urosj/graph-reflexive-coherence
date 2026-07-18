#!/usr/bin/env python3
"""Run N31 Iteration 9-C route-susceptibility relaxation probe."""

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
from pygrc.models.grc_9_v3_runtime import (
    compute_base_conductance,
    compute_flux,
    compute_potential,
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
ARTIFACT_DIR = OUTPUTS / "n31_i9c_susceptibility_relaxation_artifacts"
I2 = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I9 = OUTPUTS / "n31_added_mechanism_admission_i9.json"
I9_CONTRACT = (
    OUTPUTS
    / "n31_i9_added_mechanism_admission_artifacts"
    / "n31_i9_candidate_contract_bundle.json"
)
PREREGISTRATION = ARTIFACT_DIR / "n31_i9c_preregistration.json"
POST_FORMATION = ARTIFACT_DIR / "n31_i9c_post_formation_snapshot.json"
FORMED_CLOSURE = ARTIFACT_DIR / "n31_i9c_formed_susceptibility_closure.json"
ACTIVE_FINAL = ARTIFACT_DIR / "n31_i9c_active_progression_snapshot.json"
OMITTED_FINAL = ARTIFACT_DIR / "n31_i9c_omitted_progression_snapshot.json"
RELAXED_CLOSURE = ARTIFACT_DIR / "n31_i9c_relaxed_susceptibility_closure.json"
PROGRESSION_MATRIX = ARTIFACT_DIR / "n31_i9c_progression_receipt_matrix.json"
READOUT_MATRIX = ARTIFACT_DIR / "n31_i9c_native_readout_matrix.json"
CONTROL_MATRIX = ARTIFACT_DIR / "n31_i9c_control_matrix.json"
COMPOSED_IDENTITIES = ARTIFACT_DIR / "n31_i9c_composed_identities.json"
GRC_KERNEL_SOURCE = ROOT / "src" / "pygrc" / "models" / "grc_9_v3_runtime.py"
LGRC_RUNTIME_SOURCE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime.py"
TRACE = OUTPUTS / "n31_i9c_susceptibility_relaxation_source_current_trace.json"
OUTPUT = OUTPUTS / "n31_susceptibility_relaxation_i9c.json"
REPORT = REPORTS / "n31_susceptibility_relaxation_i9c.md"
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_susceptibility_relaxation_i9c.py"
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

INITIAL_C = {0: 0.9, 1: 1.0, 2: 0.0}
ROUTE_USE_AMOUNT = 0.4
PROGRESSION_AMOUNT = 0.05
S_FLOOR = 0.5
S_MAX = 1.0
ALPHA = 1.0
RHO = 0.75
EXPECTED_FORMED_S = 0.9
EXPECTED_RELAXATION_SEQUENCE = (0.8, 0.725, 0.66875, 0.6265625)
MIN_S_WEAKENING = 0.25
MIN_EFFECTIVE_CONDUCTANCE_WEAKENING = 0.15
MIN_SIGNED_FLUX_CHANGE = 0.02
TOLERANCE = 1e-12
REGISTERED_EDGE_ID = 1
PROGRESSION_EDGE_ID = 0
FORMATION_LINEAGE = "n31_C_registered_route_use"
PROGRESSION_SPECS = (
    (0, 1, 2.0, 20, "n31_C_progression_1"),
    (1, 0, 3.0, 30, "n31_C_progression_2"),
    (0, 1, 4.0, 40, "n31_C_progression_3"),
    (1, 0, 5.0, 50, "n31_C_progression_4"),
)
FORMATION_INPUT_PATHS = (
    "closure.S_by_edge.1",
    "closure.formation_receipt_id",
    "policy.S_max",
    "policy.alpha",
    "receipt.event_kind",
    "receipt.edge_id",
    "receipt.source_node_id",
    "receipt.target_node_id",
    "receipt.source_lineage_id",
    "receipt.amount",
)
RELAXATION_INPUT_PATHS = (
    "closure.S_by_edge.1",
    "closure.processed_progression_event_ids",
    "policy.S_floor",
    "policy.rho",
    "receipt.event_kind",
    "receipt.event_id",
    "receipt.edge_id",
    "receipt.source_node_id",
    "receipt.target_node_id",
    "receipt.event_time_key",
    "receipt.scheduler_event_index",
    "receipt.source_lineage_id",
    "receipt.amount",
)
READOUT_INPUT_PATHS = (
    "closure.complete_validated_state",
    "closure.S_by_edge.1",
    "policy.registered_edge_id",
    "native.base_conductance.registered_edge",
    "native.constitutive_semantic_modes",
    "native.evolution_parameters",
    "pipeline.after_compute_base_conductance_before_compute_potential",
)
PROHIBITED_CLOSURE_INPUTS = (
    "global_event_count",
    "wall_clock",
    "outcome_history",
    "global_node_scan",
    "semantic_route_labels",
    "readout_result_feedback",
    "unregistered_receipt_history",
)


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
    record = deepcopy(record)
    record.pop("output_digest", None)
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


def candidate_c_contract(i9: dict[str, Any]) -> dict[str, Any]:
    rows = [
        row
        for row in i9["added_mechanism_decay_classifications"]
        if row["candidate_id"] == "C_route_susceptibility_relaxation"
    ]
    if len(rows) != 1:
        raise ValueError("I9 must contain exactly one Candidate C contract")
    return rows[0]


def topology_identity() -> dict[str, Any]:
    return {
        "node_ids": [0, 1, 2],
        "edge_ids": [0, 1],
        "node_payloads": [
            {"node_id": 0, "payload": {"fixture_role": "source"}},
            {
                "node_id": 1,
                "payload": {"fixture_role": "susceptible_route_node"},
            },
            {
                "node_id": 2,
                "payload": {"fixture_role": "local_readout_receiver"},
            },
        ],
        "edge_payloads": [
            {
                "edge_id": 0,
                "source_node_id": 0,
                "source_port_id": 1,
                "target_node_id": 1,
                "target_port_id": 1,
                "orientation": "canonical_source_to_target",
                "delay": 1.0,
                "conductance": 1.0,
                "payload": {"fixture_relation": "source_to_susceptible_route"},
            },
            {
                "edge_id": 1,
                "source_node_id": 1,
                "source_port_id": 2,
                "target_node_id": 2,
                "target_port_id": 1,
                "orientation": "canonical_source_to_target",
                "delay": 1.0,
                "conductance": 1.0,
                "payload": {
                    "fixture_relation": "susceptible_route_to_local_readout"
                },
            },
        ],
        "role_to_node_id": {
            "source": 0,
            "susceptible_route_node": 1,
            "local_readout_receiver": 2,
        },
    }


def build_fixture() -> tuple[LGRC9V3, dict[str, Any]]:
    graph = PortGraphBackend()
    for role in ("source", "susceptible_route_node", "local_readout_receiver"):
        graph.add_node({"fixture_role": role})
    edge_specs = (
        (0, 0, 1, 0, "source_to_susceptible_route"),
        (1, 1, 2, 0, "susceptible_route_to_local_readout"),
    )
    port_edges: dict[int, PortEdge] = {}
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
    state = GRC9V3State(
        topology=graph,
        nodes={
            node_id: GRC9V3NodeState(coherence=coherence)
            for node_id, coherence in INITIAL_C.items()
        },
        port_edges=port_edges,
        base_conductance={0: 1.0, 1: 1.0},
        geometric_length={0: 1.0, 1: 1.0},
        temporal_delay={0: 1.0, 1: 1.0},
        flux_coupling={0: 0.0, 1: 0.0},
    )
    identity = topology_identity()
    return LGRC9V3.from_state(state, {"dt": 1.0}), identity


def native_identities(model: LGRC9V3) -> dict[str, str]:
    return {
        "v1": digest_lgrc9v3_restoration_identity_v1(model),
        "v2": digest_lgrc9v3_restoration_identity_v2(model),
    }


def coherence_by_node(model: LGRC9V3) -> dict[str, float]:
    return {
        str(node_id): float(node.coherence)
        for node_id, node in sorted(model.get_state().base_state.nodes.items())
    }


def native_budget(model: LGRC9V3) -> dict[str, float]:
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    return {
        "node_coherence_total": float(ledger.node_coherence_total),
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "conserved_budget_total": float(ledger.conserved_budget_total),
        "budget_error": float(ledger.budget_error),
    }


def compact_processing_receipts(result: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in result.events:
        processed = event.payload.get("processed_event")
        packet = event.payload.get("packet_record")
        if not isinstance(processed, dict) or not isinstance(packet, dict):
            continue
        rows.append(
            {
                "event_kind": str(processed["event_kind"]),
                "event_id": str(processed["event_id"]),
                "event_time_key": float(processed["event_time_key"]),
                "scheduler_event_index": int(processed["scheduler_event_index"]),
                "edge_id": int(processed["edge_id"]),
                "source_node_id": int(processed["source_node_id"]),
                "target_node_id": int(processed["target_node_id"]),
                "amount": float(processed["amount"]),
                "packet_id": str(processed["packet_id"]),
                "source_lineage_id": str(packet.get("source_lineage_id")),
                "budget_error": float(event.payload.get("budget_error", 0.0)),
            }
        )
    return rows


def drain_queue(model: LGRC9V3) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    while ledger.event_queue_records:
        rows.extend(compact_processing_receipts(model.step()))
        ledger = model.get_state().packet_ledger
        assert ledger is not None
    return rows


def arrival_receipt(
    receipts: list[dict[str, Any]], lineage: str
) -> dict[str, Any]:
    rows = [
        row
        for row in receipts
        if row["event_kind"] == "lgrc9v3_packet_arrival"
        and row["source_lineage_id"] == lineage
    ]
    if len(rows) != 1:
        raise ValueError(f"expected one arrival receipt for {lineage!r}")
    return rows[0]


def empty_closure() -> dict[str, Any]:
    return {
        "artifact_kind": "n31_C_route_susceptibility_closure",
        "artifact_schema_version": "n31_candidate_C_susceptibility_identity_v1",
        "S_by_edge": {"1": S_FLOOR},
        "q_use_by_edge": {"1": 0.0},
        "formation_receipt_id": None,
        "formation_update_count": 0,
        "processed_progression_event_ids": [],
        "processed_progression_event_count": 0,
        "relaxation_update_count": 0,
        "update_count": 0,
        "wall_clock_state_present": False,
        "global_event_count_state_present": False,
        "outcome_history_state_present": False,
    }


def closure_without_digest(closure: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(closure)
    value.pop("output_digest", None)
    return value


def validate_closure(closure: dict[str, Any]) -> bool:
    s_value = float(closure["S_by_edge"]["1"])
    progression_ids = closure["processed_progression_event_ids"]
    return (
        S_FLOOR - TOLERANCE <= s_value <= S_MAX + TOLERANCE
        and int(closure["processed_progression_event_count"])
        == len(progression_ids)
        and int(closure["relaxation_update_count"]) == len(progression_ids)
        and int(closure["update_count"])
        == int(closure["formation_update_count"])
        + int(closure["relaxation_update_count"])
        and len(progression_ids) == len(set(progression_ids))
        and not closure["wall_clock_state_present"]
        and not closure["global_event_count_state_present"]
        and not closure["outcome_history_state_present"]
    )


def apply_route_use(
    closure: dict[str, Any], receipt: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = closure_without_digest(closure)
    exact = (
        receipt["event_kind"] == "lgrc9v3_packet_arrival"
        and receipt["edge_id"] == REGISTERED_EDGE_ID
        and receipt["source_node_id"] == 1
        and receipt["target_node_id"] == 2
        and receipt["source_lineage_id"] == FORMATION_LINEAGE
        and abs(receipt["amount"] - ROUTE_USE_AMOUNT) <= TOLERANCE
    )
    first = updated["formation_receipt_id"] is None
    applied = exact and first
    s_before = float(updated["S_by_edge"]["1"])
    if applied:
        s_after = min(S_MAX, s_before + ALPHA * receipt["amount"])
        updated["S_by_edge"]["1"] = s_after
        updated["q_use_by_edge"]["1"] = receipt["amount"]
        updated["formation_receipt_id"] = receipt["event_id"]
        updated["formation_update_count"] = 1
        updated["update_count"] = int(updated["update_count"]) + 1
    else:
        s_after = s_before
    return updated, {
        "receipt_matched_exact_registered_route_use": exact,
        "first_formation_receipt": first,
        "formation_update_applied": applied,
        "S_before": s_before,
        "S_after": s_after,
        "q_use": receipt["amount"],
        "declared_input_paths": list(FORMATION_INPUT_PATHS),
        "observed_input_paths": list(FORMATION_INPUT_PATHS),
        "exact_allowlist_match": True,
        "unlisted_input_read_status": "none_observed",
    }


def progression_receipt_matches(receipt: dict[str, Any]) -> bool:
    allowed = {
        (source, target, event_time + 1.0, scheduler + 1, lineage)
        for source, target, event_time, scheduler, lineage in PROGRESSION_SPECS
    }
    candidate = (
        receipt["source_node_id"],
        receipt["target_node_id"],
        receipt["event_time_key"],
        receipt["scheduler_event_index"],
        receipt["source_lineage_id"],
    )
    return (
        receipt["event_kind"] == "lgrc9v3_packet_arrival"
        and receipt["edge_id"] == PROGRESSION_EDGE_ID
        and abs(receipt["amount"] - PROGRESSION_AMOUNT) <= TOLERANCE
        and candidate in allowed
    )


def apply_relaxation(
    closure: dict[str, Any], receipt: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = closure_without_digest(closure)
    exact = progression_receipt_matches(receipt)
    duplicate = receipt["event_id"] in updated["processed_progression_event_ids"]
    applied = exact and not duplicate
    s_before = float(updated["S_by_edge"]["1"])
    if applied:
        s_after = S_FLOOR + RHO * (s_before - S_FLOOR)
        updated["S_by_edge"]["1"] = s_after
        updated["processed_progression_event_ids"].append(receipt["event_id"])
        updated["processed_progression_event_count"] = int(
            updated["processed_progression_event_count"]
        ) + 1
        updated["relaxation_update_count"] = int(
            updated["relaxation_update_count"]
        ) + 1
        updated["update_count"] = int(updated["update_count"]) + 1
    else:
        s_after = s_before
    return updated, {
        "receipt_matched_exact_progression_predicate": exact,
        "duplicate_receipt": duplicate,
        "relaxation_update_applied": applied,
        "S_before": s_before,
        "S_after": s_after,
        "delta_S": s_after - s_before,
        "receipt": receipt,
        "declared_input_paths": list(RELAXATION_INPUT_PATHS),
        "observed_input_paths": list(RELAXATION_INPUT_PATHS),
        "exact_allowlist_match": True,
        "unlisted_input_read_status": "none_observed",
    }


def execute_progression_branch(
    native_snapshot: Path,
    closure: dict[str, Any],
    *,
    apply_candidate_closure: bool,
    save_to: Path,
) -> tuple[LGRC9V3, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    model = LGRC9V3.load(str(native_snapshot))
    updated = closure_without_digest(closure)
    receipts: list[dict[str, Any]] = []
    updates: list[dict[str, Any]] = []
    for source, target, event_time, scheduler, lineage in PROGRESSION_SPECS:
        model.schedule_packet_departure(
            source_node_id=source,
            target_node_id=target,
            edge_id=PROGRESSION_EDGE_ID,
            amount=PROGRESSION_AMOUNT,
            departure_event_time_key=event_time,
            scheduler_event_index=scheduler,
            source_lineage_id=lineage,
        )
        processed = drain_queue(model)
        receipt = arrival_receipt(processed, lineage)
        receipts.append(receipt)
        if apply_candidate_closure:
            updated, update = apply_relaxation(updated, receipt)
            updates.append(update)
    model.save(str(save_to))
    return model, updated, receipts, updates


def closure_s_for_readout(closure: dict[str, Any] | None) -> float:
    if closure is None:
        raise ValueError("Candidate C readout requires restored closure state")
    if not validate_closure(closure):
        raise ValueError("Candidate C closure state is malformed")
    return float(closure["S_by_edge"]["1"])


def apply_partial_native_pipeline(
    native_snapshot: Path, closure: dict[str, Any], row_id: str
) -> dict[str, Any]:
    s_value = closure_s_for_readout(closure)
    model = LGRC9V3.load(str(native_snapshot))
    params = model.get_params()
    pre_state = deepcopy(model.get_state())
    pre_snapshot = model.snapshot()
    pre_identity = native_identities(model)
    coherence_before = coherence_by_node(model)
    budget_before = native_budget(model)

    work_state = deepcopy(pre_state)
    base_state = work_state.base_state
    compute_base_conductance(
        base_state,
        evolution=params.evolution,
        modes=params.constitutive_semantic_modes,
    )
    g_native = float(base_state.base_conductance[REGISTERED_EDGE_ID])
    g_effective = s_value * g_native
    edge = base_state.port_edges[REGISTERED_EDGE_ID]
    base_state.base_conductance[REGISTERED_EDGE_ID] = g_effective
    base_state.port_edges[REGISTERED_EDGE_ID] = PortEdge(
        edge.node_u,
        edge.port_u,
        edge.node_v,
        edge.port_v,
        conductance=g_effective,
        flux_uv=edge.flux_uv,
    )
    compute_potential(base_state, evolution=params.evolution)
    compute_flux(base_state, evolution=params.evolution)
    model.set_state(work_state)
    coherence_after = coherence_by_node(model)
    budget_after = native_budget(model)
    readout_edge = model.get_state().base_state.port_edges[REGISTERED_EDGE_ID]
    readout = {
        "row_id": row_id,
        "S": s_value,
        "closure_identity": closure.get(
            "output_digest", digest_value(closure_without_digest(closure))
        ),
        "g_native": g_native,
        "g_effective": g_effective,
        "potential_by_node": {
            str(key): float(value)
            for key, value in sorted(model.get_state().base_state.potential.items())
        },
        "signed_flux_on_registered_edge": float(readout_edge.flux_uv),
        "pre_application_native_identity": pre_identity,
        "coherence_before": coherence_before,
        "coherence_after": coherence_after,
        "coherence_unchanged": coherence_before == coherence_after,
        "budget_before": budget_before,
        "budget_after": budget_after,
        "budget_unchanged": budget_before == budget_after,
        "topology_digest": digest_value(topology_identity()),
        "packet_amount_scaled_by_closure": False,
        "packet_export_scheduled_by_closure": False,
        "readout_kind": "native_potential_flux_diagnostic",
        "readout_request_authority": "experiment_harness",
        "susceptibility_and_conductance_insertion_authority": (
            "candidate_C_closure"
        ),
        "potential_flux_computation_authority": "native_GRC9V3_kernels",
        "ordinary_LGRC_step_consumes_S": False,
        "packet_transport_executed_during_readout": False,
        "coherence_transition_caused_by_readout": False,
        "state_mutating_native_transport_consequence_supported": False,
        "input_audit": {
            "declared_input_paths": list(READOUT_INPUT_PATHS),
            "observed_input_paths": list(READOUT_INPUT_PATHS),
            "exact_allowlist_match": True,
            "unlisted_input_read_status": "none_observed",
            "prohibited_input_paths": list(PROHIBITED_CLOSURE_INPUTS),
            "prohibited_inputs_observed": [],
        },
        "native_consumers": [
            "pygrc.models.grc_9_v3_runtime.compute_potential",
            "pygrc.models.grc_9_v3_runtime.compute_flux",
        ],
    }

    cleanup_probe_state = deepcopy(pre_state)
    compute_base_conductance(
        cleanup_probe_state.base_state,
        evolution=params.evolution,
        modes=params.constitutive_semantic_modes,
    )
    native_conductance_after_cleanup = float(
        cleanup_probe_state.base_state.base_conductance[REGISTERED_EDGE_ID]
    )
    model.set_state(deepcopy(pre_state))
    post_cleanup_identity = native_identities(model)
    post_cleanup_snapshot = model.snapshot()
    complete_snapshot_exact_after_cleanup = pre_snapshot == post_cleanup_snapshot
    readout["cleanup"] = {
        "native_conductance_after_cleanup": native_conductance_after_cleanup,
        "original_native_conductance_restored": abs(
            native_conductance_after_cleanup - g_native
        )
        <= TOLERANCE,
        "closure_conductance_not_left_for_unqualified_step": abs(
            native_conductance_after_cleanup - g_effective
        )
        > TOLERANCE,
        "pre_application_native_identity_v1": pre_identity["v1"],
        "post_cleanup_native_identity_v1": post_cleanup_identity["v1"],
        "pre_application_native_identity_v2": pre_identity["v2"],
        "post_cleanup_native_identity_v2": post_cleanup_identity["v2"],
        "native_identity_v1_exact_after_cleanup": (
            pre_identity["v1"] == post_cleanup_identity["v1"]
        ),
        "native_identity_v2_exact_after_cleanup": (
            pre_identity["v2"] == post_cleanup_identity["v2"]
        ),
        "complete_snapshot_exact_after_cleanup": (
            complete_snapshot_exact_after_cleanup
        ),
        "complete_changed_path_diff_after_cleanup": (
            []
            if complete_snapshot_exact_after_cleanup
            else ["unresolved_nonidentical_snapshot"]
        ),
    }
    readout["scientific_readout_digest"] = digest_value(
        {key: value for key, value in readout.items() if key != "row_id"}
    )
    readout["readout_digest"] = digest_value(readout)
    return readout


def label_only_control(native_snapshot: Path) -> dict[str, Any]:
    model = LGRC9V3.load(str(native_snapshot))
    params = model.get_params()
    baseline_state = deepcopy(model.get_state())
    compute_base_conductance(
        baseline_state.base_state,
        evolution=params.evolution,
        modes=params.constitutive_semantic_modes,
    )
    baseline = float(
        baseline_state.base_state.base_conductance[REGISTERED_EDGE_ID]
    )
    state = deepcopy(model.get_state())
    edge = state.base_state.port_edges[REGISTERED_EDGE_ID]
    state.base_state.base_conductance[REGISTERED_EDGE_ID] = 0.123
    state.base_state.port_edges[REGISTERED_EDGE_ID] = PortEdge(
        edge.node_u,
        edge.port_u,
        edge.node_v,
        edge.port_v,
        conductance=0.123,
        flux_uv=edge.flux_uv,
    )
    compute_base_conductance(
        state.base_state,
        evolution=params.evolution,
        modes=params.constitutive_semantic_modes,
    )
    recomputed = float(state.base_state.base_conductance[REGISTERED_EDGE_ID])
    return {
        "control_id": "conductance_label_only",
        "control_status": "failed_closed",
        "injected_cache_value": 0.123,
        "native_recomputed_value": recomputed,
        "native_baseline_value": baseline,
        "cache_write_erased_by_native_rebuild": abs(
            recomputed - baseline
        )
        <= TOLERANCE,
        "positive_claim_allowed": False,
    }


def policy_configuration() -> dict[str, Any]:
    policy = {
        "policy_schema": "n31_C_susceptibility_relaxation_v1",
        "registered_edge_id": REGISTERED_EDGE_ID,
        "S_floor": S_FLOOR,
        "S_max": S_MAX,
        "alpha": ALPHA,
        "rho": RHO,
        "formation_relation": "S_after_use = min(S_max, S + alpha * q_use)",
        "relaxation_relation": "S_next = S_floor + rho * (S - S_floor)",
        "readout_relation": "g_effective = S * g_native",
        "formation_receipt_predicate": {
            "event_kind": "lgrc9v3_packet_arrival",
            "edge_id": REGISTERED_EDGE_ID,
            "source_node_id": 1,
            "target_node_id": 2,
            "source_lineage_id": FORMATION_LINEAGE,
            "amount": ROUTE_USE_AMOUNT,
        },
        "progression_receipt_predicate": {
            "event_kind": "lgrc9v3_packet_arrival",
            "edge_id": PROGRESSION_EDGE_ID,
            "amount": PROGRESSION_AMOUNT,
            "exact_registered_specs": [list(row) for row in PROGRESSION_SPECS],
        },
        "conductance_insertion_phase": (
            "after_native_compute_base_conductance_before_native_compute_potential"
        ),
        "cleanup_phase": "restore_exact_pre_application_native_state",
        "implementation_bindings": {
            "closure_script_path": SCRIPT_RELATIVE,
            "closure_script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE),
            "grc9v3_kernel_path": relative(GRC_KERNEL_SOURCE),
            "grc9v3_kernel_sha256": sha256_file(GRC_KERNEL_SOURCE),
            "lgrc9v3_runtime_path": relative(LGRC_RUNTIME_SOURCE),
            "lgrc9v3_runtime_sha256": sha256_file(LGRC_RUNTIME_SOURCE),
            "runtime_revision": GOVERNANCE_BASE_REVISION,
        },
        "outcome_tuning_allowed": False,
    }
    return {**policy, "policy_identity": digest_value(policy)}


def preregistration_record(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_kind": "n31_i9c_preregistration",
        "artifact_schema_version": "n31_i9c_preregistration_v1",
        "generated_at": GENERATED_AT,
        "candidate_id": contract["candidate_id"],
        "declared_before_use": True,
        "policy": policy_configuration(),
        "initial_coherence": INITIAL_C,
        "registered_route_use": {
            "source_node_id": 1,
            "target_node_id": 2,
            "edge_id": REGISTERED_EDGE_ID,
            "amount": ROUTE_USE_AMOUNT,
            "lineage": FORMATION_LINEAGE,
        },
        "progression_specs": [
            {
                "source_node_id": source,
                "target_node_id": target,
                "edge_id": PROGRESSION_EDGE_ID,
                "amount": PROGRESSION_AMOUNT,
                "event_time_key": event_time,
                "scheduler_event_index": scheduler,
                "expected_arrival_event_time_key": event_time + 1.0,
                "expected_arrival_scheduler_event_index": scheduler + 1,
                "lineage": lineage,
            }
            for source, target, event_time, scheduler, lineage in PROGRESSION_SPECS
        ],
        "expected_formed_S": EXPECTED_FORMED_S,
        "expected_relaxation_sequence": list(EXPECTED_RELAXATION_SEQUENCE),
        "minimum_S_weakening": MIN_S_WEAKENING,
        "minimum_effective_conductance_weakening": (
            MIN_EFFECTIVE_CONDUCTANCE_WEAKENING
        ),
        "minimum_signed_flux_change": MIN_SIGNED_FLUX_CHANGE,
        "readout_contract": {
            "common_native_state_required": True,
            "only_pre_application_difference": "restored_candidate_closure_S",
            "native_consumers": contract["executable_conductance_path"][
                "native_operation_consumers"
            ],
            "signed_flux_must_decrease_as_S_relaxes": True,
            "packet_amount_scaling_allowed": False,
            "export_scheduling_allowed": False,
            "readout_request_authority": "experiment_harness",
            "susceptibility_and_conductance_insertion_authority": (
                "candidate_C_closure"
            ),
            "potential_flux_computation_authority": "native_GRC9V3_kernels",
            "ordinary_LGRC_step_consumes_S": False,
            "state_mutating_native_transport_consequence_supported": False,
        },
        "input_allowlists": {
            "formation": list(FORMATION_INPUT_PATHS),
            "relaxation": list(RELAXATION_INPUT_PATHS),
            "readout": list(READOUT_INPUT_PATHS),
            "prohibited": list(PROHIBITED_CLOSURE_INPUTS),
        },
        "claim_ceiling": "provisional_producer_mediated_C_R_DR4_pending_I10",
        "DR5_or_DR6_allowed": False,
    }


def theory_positioning() -> dict[str, Any]:
    return {
        "strict_2025_11_coherence_only_ontology": {
            "alignment_order": ["D0a", "Candidate_B", "Candidate_A", "Candidate_C"],
            "closest_added_mechanism": "Candidate_B",
            "candidate_C_disposition": (
                "effective_closure_or_possible_theory_extension_candidate"
            ),
            "candidate_C_is_closest": False,
            "reason": (
                "independently_restored_noncoherence_S_changes_the_registered_"
                "readout_under_identical_complete_native_C_state"
            ),
        },
        "functional_reflexive_geometry_resemblance": {
            "resemblance_order": ["Candidate_C", "D0a", "Candidate_B", "Candidate_A"],
            "candidate_C_is_closest": True,
            "reason": (
                "prior_route_use_changes_S_then_effective_geometry_then_native_"
                "potential_flux_diagnostic"
            ),
            "functional_resemblance_is_not_ontological_fidelity": True,
        },
        "candidate_C_naturalization_target": {
            "preferred_form": (
                "S_is_exactly_derived_from_source_current_C_JC_history_with_no_"
                "independent_causal_freedom"
            ),
            "stronger_form": (
                "C_fast_C_slow_decomposition_where_route_use_changes_C_slow_and_"
                "ordinary_C_JC_dynamics_relax_it"
            ),
            "same_complete_C_JC_history_implies_same_S_required": True,
            "remove_and_recompute_S_must_recover_same_value": True,
        },
    }


def artifact_record(path: Path, role: str) -> dict[str, str]:
    return {"path": relative(path), "sha256": sha256_file(path), "artifact_role": role}


def build() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i9 = load_json(I9)
    contract = candidate_c_contract(i9)
    sources = [source_record(path) for path in SOURCE_IDENTITIES]
    preregistration = write_record(PREREGISTRATION, preregistration_record(contract))

    model, reconstructed_topology = build_fixture()
    reconstructed_topology_digest = digest_value(reconstructed_topology)
    initial_budget = native_budget(model)
    initial_identity = native_identities(model)
    closure = empty_closure()
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=REGISTERED_EDGE_ID,
        amount=ROUTE_USE_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=10,
        source_lineage_id=FORMATION_LINEAGE,
    )
    formation_receipts = drain_queue(model)
    formation_arrival = arrival_receipt(formation_receipts, FORMATION_LINEAGE)
    closure, formation_update = apply_route_use(closure, formation_arrival)
    model.save(str(POST_FORMATION))
    formed_closure = write_record(FORMED_CLOSURE, closure)
    post_formation_identity = native_identities(model)
    post_formation_budget = native_budget(model)

    active_model, active_closure, active_receipts, active_updates = (
        execute_progression_branch(
            POST_FORMATION,
            formed_closure,
            apply_candidate_closure=True,
            save_to=ACTIVE_FINAL,
        )
    )
    omitted_model, omitted_closure, omitted_receipts, omitted_updates = (
        execute_progression_branch(
            POST_FORMATION,
            formed_closure,
            apply_candidate_closure=False,
            save_to=OMITTED_FINAL,
        )
    )
    relaxed_closure = write_record(RELAXED_CLOSURE, active_closure)
    active_identity = native_identities(active_model)
    omitted_identity = native_identities(omitted_model)
    active_budget = native_budget(active_model)
    omitted_budget = native_budget(omitted_model)

    progression_matrix = write_record(
        PROGRESSION_MATRIX,
        {
            "artifact_kind": "n31_i9c_progression_receipt_matrix",
            "artifact_schema_version": "n31_i9c_progression_receipt_matrix_v1",
            "generated_at": GENERATED_AT,
            "active_branch_receipts": active_receipts,
            "omitted_branch_receipts": omitted_receipts,
            "active_branch_updates": active_updates,
            "omitted_branch_updates": omitted_updates,
            "native_v1_identity_equal_after_matched_progression": (
                active_identity["v1"] == omitted_identity["v1"]
            ),
            "native_v2_identity_equal_after_matched_progression": (
                active_identity["v2"] == omitted_identity["v2"]
            ),
            "native_budget_equal_after_matched_progression": (
                active_budget == omitted_budget
            ),
            "active_S_sequence": [row["S_after"] for row in active_updates],
            "omitted_S": omitted_closure["S_by_edge"]["1"],
            "progression_is_native": True,
            "progression_is_experiment_scheduled": True,
            "closure_callback_is_producer_owned": True,
            "ordinary_autonomous_relaxation_claimed": False,
        },
    )

    loaded_formed = load_json(FORMED_CLOSURE)
    loaded_relaxed = load_json(RELAXED_CLOSURE)
    trajectory_closures = [loaded_formed]
    replayed_closure = loaded_formed
    for receipt in active_receipts:
        replayed_closure, _ = apply_relaxation(replayed_closure, receipt)
        trajectory_closures.append(replayed_closure)
    s_rows = [
        ("formed_hold", trajectory_closures[0]),
        *[
            (f"relaxation_step_{index}", closure_row)
            for index, closure_row in enumerate(trajectory_closures[1:], start=1)
        ],
    ]
    s_values = [closure_s_for_readout(row[1]) for row in s_rows]
    readout_rows = [
        apply_partial_native_pipeline(ACTIVE_FINAL, closure_row, row_id)
        for row_id, closure_row in s_rows
    ]
    formed_readout = readout_rows[0]
    relaxed_readout = readout_rows[-1]
    g_values = [row["g_effective"] for row in readout_rows]
    flux_values = [row["signed_flux_on_registered_edge"] for row in readout_rows]
    readout_matrix = write_record(
        READOUT_MATRIX,
        {
            "artifact_kind": "n31_i9c_native_readout_matrix",
            "artifact_schema_version": "n31_i9c_native_readout_matrix_v1",
            "generated_at": GENERATED_AT,
            "common_native_snapshot": relative(ACTIVE_FINAL),
            "common_native_v1_identity": active_identity["v1"],
            "common_native_v2_identity": active_identity["v2"],
            "rows": readout_rows,
            "S_monotonic_decrease": all(
                left > right for left, right in zip(s_values, s_values[1:])
            ),
            "g_effective_monotonic_decrease": all(
                left > right for left, right in zip(g_values, g_values[1:])
            ),
            "signed_flux_monotonic_decrease": all(
                left > right for left, right in zip(flux_values, flux_values[1:])
            ),
            "formed_to_relaxed_S_weakening": (
                formed_readout["S"] - relaxed_readout["S"]
            ),
            "formed_to_relaxed_g_effective_weakening": (
                formed_readout["g_effective"] - relaxed_readout["g_effective"]
            ),
            "formed_to_relaxed_signed_flux_change": (
                formed_readout["signed_flux_on_registered_edge"]
                - relaxed_readout["signed_flux_on_registered_edge"]
            ),
            "same_complete_native_state_different_S_changes_registered_readout": (
                abs(
                    formed_readout["signed_flux_on_registered_edge"]
                    - relaxed_readout["signed_flux_on_registered_edge"]
                )
                >= MIN_SIGNED_FLUX_CHANGE
            ),
            "mediation_strength": (
                "bounded_partial_registered_edge_conductance"
            ),
            "load_bearing_mediator": (
                "closure_S_applied_to_edge_1_conductance"
            ),
            "intervention_site": "registered_edge_1",
            "potential_solution_scope": "graph_level_native_kernel_computation",
            "complete_native_state_mediation": False,
            "complete_state_mediation_claimed": False,
            "readout_authority": {
                "request": "experiment_harness",
                "susceptibility_and_conductance_insertion": "candidate_C_closure",
                "potential_flux_computation": "native_GRC9V3_kernels",
            },
            "ordinary_LGRC_step_consumes_S": False,
            "readout_kind": "native_potential_flux_diagnostic",
            "state_mutating_native_transport_consequence_supported": False,
        },
    )

    formed_replay = apply_partial_native_pipeline(
        ACTIVE_FINAL, loaded_formed, "formed_replay"
    )
    relaxed_replay = apply_partial_native_pipeline(
        ACTIVE_FINAL, loaded_relaxed, "relaxed_replay"
    )
    label_control = label_only_control(ACTIVE_FINAL)
    malformed_closure = closure_without_digest(loaded_relaxed)
    malformed_closure["processed_progression_event_count"] = 99
    try:
        closure_s_for_readout(None)
    except ValueError:
        missing_closure_blocked = True
    else:
        missing_closure_blocked = False
    controls = [
        label_control,
        {
            "control_id": "susceptibility_without_restoration",
            "control_status": "failed_closed",
            "missing_closure_blocked": missing_closure_blocked,
            "positive_claim_allowed": False,
        },
        {
            "control_id": "history_carried_by_hidden_producer",
            "control_status": "failed_closed",
            "malformed_closure_rejected": not validate_closure(malformed_closure),
            "exact_receipt_ids_restored": (
                loaded_relaxed["processed_progression_event_ids"]
                == active_closure["processed_progression_event_ids"]
            ),
            "positive_claim_allowed": False,
        },
        {
            "control_id": "same_complete_C_different_S_changes_future",
            "control_status": "passed",
            "same_native_v1_identity": (
                formed_readout["pre_application_native_identity"]["v1"]
                == relaxed_readout["pre_application_native_identity"]["v1"]
            ),
            "same_native_v2_identity": (
                formed_readout["pre_application_native_identity"]["v2"]
                == relaxed_readout["pre_application_native_identity"]["v2"]
            ),
            "registered_readout_changed": readout_matrix[
                "same_complete_native_state_different_S_changes_registered_readout"
            ],
            "strict_coherence_only_boundary_crossed": True,
            "positive_claim_allowed": True,
        },
        {
            "control_id": "producer_closure_as_native_memory",
            "control_status": "failed_closed",
            "native_identity_excludes_candidate_closure": True,
            "candidate_closure_required_for_effect": True,
            "native_memory_claim_allowed": False,
            "positive_claim_allowed": False,
        },
        {
            "control_id": "wall_clock_decay",
            "control_status": "passed",
            "event_receipt_count_is_internal_time": True,
            "wall_clock_state_present": False,
            "positive_claim_allowed": True,
        },
        {
            "control_id": "producer_scheduled_D0_decay",
            "control_status": "failed_closed",
            "relation_authority": "producer_mediated",
            "native_D0_upgrade_allowed": False,
            "positive_claim_allowed": False,
        },
    ]
    control_matrix = write_record(
        CONTROL_MATRIX,
        {
            "artifact_kind": "n31_i9c_control_matrix",
            "artifact_schema_version": "n31_i9c_control_matrix_v1",
            "generated_at": GENERATED_AT,
            "controls": controls,
            "lane_specific_control_count": 5,
            "lane_specific_controls_resolved": 5,
            "auxiliary_control_count": 2,
            "complete_I10_control_matrix_claimed": False,
            "DR5_control_gate_complete": False,
        },
    )

    composed_identities = write_record(
        COMPOSED_IDENTITIES,
        {
            "artifact_kind": "n31_i9c_composed_candidate_identities",
            "artifact_schema_version": "n31_i9c_composed_candidate_identities_v1",
            "generated_at": GENERATED_AT,
            "policy_identity": policy_configuration()["policy_identity"],
            "implementation_bindings": policy_configuration()[
                "implementation_bindings"
            ],
            "topology_identity": reconstructed_topology_digest,
            "formed": {
                "native_v1": active_identity["v1"],
                "native_v2": active_identity["v2"],
                "closure_output_digest": loaded_formed["output_digest"],
                "composed_identity": digest_value(
                    {
                        "native_v1": active_identity["v1"],
                        "native_v2": active_identity["v2"],
                        "closure": loaded_formed["output_digest"],
                        "policy": policy_configuration()["policy_identity"],
                        "topology": reconstructed_topology_digest,
                    }
                ),
            },
            "relaxed": {
                "native_v1": active_identity["v1"],
                "native_v2": active_identity["v2"],
                "closure_output_digest": loaded_relaxed["output_digest"],
                "composed_identity": digest_value(
                    {
                        "native_v1": active_identity["v1"],
                        "native_v2": active_identity["v2"],
                        "closure": loaded_relaxed["output_digest"],
                        "policy": policy_configuration()["policy_identity"],
                        "topology": reconstructed_topology_digest,
                    }
                ),
            },
            "native_identity_same_closure_identity_different": (
                loaded_formed["output_digest"] != loaded_relaxed["output_digest"]
            ),
        },
    )

    artifact_paths = (
        PREREGISTRATION,
        POST_FORMATION,
        FORMED_CLOSURE,
        ACTIVE_FINAL,
        OMITTED_FINAL,
        RELAXED_CLOSURE,
        PROGRESSION_MATRIX,
        READOUT_MATRIX,
        CONTROL_MATRIX,
        COMPOSED_IDENTITIES,
    )
    artifact_roles = (
        "pre_outcome_candidate_C_contract",
        "post_registered_route_use_native_snapshot",
        "formed_susceptibility_closure",
        "post_progression_active_native_snapshot",
        "post_progression_omitted_native_snapshot",
        "relaxed_susceptibility_closure",
        "matched_native_progression_and_receipts",
        "native_conductance_potential_flux_readout",
        "candidate_C_selected_controls",
        "native_closure_policy_topology_identity",
    )
    artifact_manifest = [
        artifact_record(path, role)
        for path, role in zip(artifact_paths, artifact_roles)
    ]

    s_weakening = readout_matrix["formed_to_relaxed_S_weakening"]
    g_weakening = readout_matrix["formed_to_relaxed_g_effective_weakening"]
    flux_change = readout_matrix["formed_to_relaxed_signed_flux_change"]
    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-C",
        "artifact_kind": "route_susceptibility_relaxation_source_current_trace",
        "artifact_schema_version": "n31_i9c_susceptibility_relaxation_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_provisional_producer_mediated_C_R_DR4_route_"
            "susceptibility_relaxation_pending_I10"
        ),
        "source_chain": sources,
        "derived_report_only": False,
        "source_current_runtime_artifact": True,
        "candidate_id": contract["candidate_id"],
        "semantic_class": "C",
        "semantic_subtype": "C_R_route_susceptibility_relaxation",
        "relation_authority": "producer_mediated_effective_non_markovian_closure",
        "readout_authority": {
            "readout_request_authority": "experiment_harness",
            "susceptibility_and_conductance_insertion_authority": (
                "candidate_C_closure"
            ),
            "potential_flux_computation_authority": "native_GRC9V3_kernels",
            "runtime_layer": "LGRC9V3",
            "embedded_computational_layer": "GRC9V3_native_kernels",
            "ordinary_LGRC_step_consumes_S": False,
            "state_mutating_native_transport_consequence_supported": False,
        },
        "topology": {
            "reconstructed_identity": reconstructed_topology,
            "reconstructed_digest": reconstructed_topology_digest,
            "frozen_digest": contract["topology"]["canonical_topology_digest"],
            "matches_frozen_contract": (
                reconstructed_topology_digest
                == contract["topology"]["canonical_topology_digest"]
            ),
        },
        "preregistration": {
            "path": relative(PREREGISTRATION),
            "sha256": sha256_file(PREREGISTRATION),
            "output_digest": preregistration["output_digest"],
        },
        "formation": {
            "registered_route_use_amount": ROUTE_USE_AMOUNT,
            "receipt": formation_arrival,
            "closure_update": formation_update,
            "initial_S": S_FLOOR,
            "formed_S": formed_closure["S_by_edge"]["1"],
            "native_identity_before": initial_identity,
            "native_identity_after": post_formation_identity,
            "budget_before": initial_budget,
            "budget_after": post_formation_budget,
            "formation_packet_exhausted": (
                post_formation_budget["in_flight_packet_total"] == 0.0
            ),
            "authority": (
                "registered_native_route_use_triggers_producer_owned_"
                "susceptibility_formation"
            ),
        },
        "progression": progression_matrix,
        "relaxation": {
            "S_sequence": [S_FLOOR, EXPECTED_FORMED_S]
            + progression_matrix["active_S_sequence"],
            "formed_S": formed_closure["S_by_edge"]["1"],
            "relaxed_S": relaxed_closure["S_by_edge"]["1"],
            "S_weakening": s_weakening,
            "internal_time_units": "declared_disjoint_native_progression_receipts",
            "progression_schedule_authority": "experiment_fixture",
            "relaxation_callback_authority": "candidate_C_closure",
            "susceptibility_state_locality": "edge_1",
            "clock_trigger_locality": "edge_0_progression_receipts",
            "route_local_proper_time_decay_supported": False,
            "ordinary_autonomous_relaxation_claimed": False,
        },
        "native_readout": {
            "path": relative(READOUT_MATRIX),
            "sha256": sha256_file(READOUT_MATRIX),
            "output_digest": readout_matrix["output_digest"],
            "g_effective_weakening": g_weakening,
            "signed_flux_change": flux_change,
            "mediation_strength": readout_matrix["mediation_strength"],
            "load_bearing_mediator": readout_matrix["load_bearing_mediator"],
            "readout_kind": readout_matrix["readout_kind"],
            "packet_transport_executed_during_readout": False,
            "coherence_transition_caused_by_readout": False,
            "state_mutating_future_behavior_supported": False,
            "complete_state_mediation_claimed": False,
        },
        "restoration": {
            "formed_closure_internal_digest_exact": internal_output_digest_exact(
                loaded_formed
            ),
            "relaxed_closure_internal_digest_exact": internal_output_digest_exact(
                loaded_relaxed
            ),
            "formed_readout_replay_exact": (
                formed_replay["scientific_readout_digest"]
                == formed_readout["scientific_readout_digest"]
            ),
            "relaxed_readout_replay_exact": (
                relaxed_replay["scientific_readout_digest"]
                == relaxed_readout["scientific_readout_digest"]
            ),
            "composed_identity_path": relative(COMPOSED_IDENTITIES),
            "composed_identity_output_digest": composed_identities["output_digest"],
        },
        "controls": {
            "path": relative(CONTROL_MATRIX),
            "sha256": sha256_file(CONTROL_MATRIX),
            "output_digest": control_matrix["output_digest"],
            "lane_specific_controls_resolved": 5,
            "complete_I10_control_matrix_claimed": False,
        },
        "representation_boundary": {
            "causal_carrier": "versioned_candidate_closure_S_by_edge_1",
            "susceptibility_update_magnitude_ledger_role": "report_only_noncausal",
            "native_susceptibility_state_present": False,
            "closure_state_is_native_memory": False,
            "resource_cost_supported": False,
            "free_noncoherence_state_naturalized": False,
            "ordinary_LGRC_step_compatible_without_hook": False,
        },
        "input_audit": {
            "formation_exact_allowlist_match": formation_update[
                "exact_allowlist_match"
            ],
            "relaxation_exact_allowlist_match": all(
                row["exact_allowlist_match"] for row in active_updates
            ),
            "readout_exact_allowlist_match": all(
                row["input_audit"]["exact_allowlist_match"]
                for row in readout_rows
            ),
            "prohibited_inputs_observed": [],
            "unlisted_input_read_status": "none_observed",
            "audit_method": (
                "explicit_closure_function_field_read_review_and_emitted_paths"
            ),
        },
        "theory_positioning": theory_positioning(),
        "classification": {
            "current_decay_relation_ladder_rung": "DR4",
            "DR4_supported": True,
            "DR5_supported": False,
            "DR6_supported": False,
            "candidate_rung_status": "provisional_pending_I10",
            "native_decay_classification_unchanged": "D0a_DR2",
            "D0_R_bridge_status": "not_tested",
            "native_upgrade_allowed": False,
        },
        "producer_residue": sorted(
            set(contract["producer_residue"])
            | {
                "experiment_authored_progression_schedule",
                "cross_edge_receipt_clock_coupling",
                "closure_orchestrated_partial_native_readout_pipeline",
            }
        ),
        "naturalization_debt": sorted(
            (
                set(contract["naturalization_debt"])
                - {"susceptibility_cost_not_naturalized_into_RC_coherence"}
            )
            | {
                "independent_S_is_additional_causal_degree",
                "independent_S_resource_cost_relation_missing",
                "receipt_indexed_relaxation_clock_not_route_local_proper_time",
                "state_mutating_native_transport_consequence_missing",
            }
        ),
        "artifact_manifest": artifact_manifest,
        "unsafe_claim_flags": {
            "native_decay": False,
            "native_memory": False,
            "native_susceptibility": False,
            "ordinary_D0_R": False,
            "autonomous_relaxation": False,
            "free_naturalized_noncoherence_state": False,
            "trail_or_stigmergy": False,
            "communication": False,
            "agency": False,
            "native_support": False,
            "candidate_C_closest_to_strict_RC_ontology": False,
        },
    }

    trace["checks"] = [
        check("exact_sources_consumed", all(row["identity_exact"] for row in sources), sources),
        check(
            "topology_matches_frozen_candidate_C_contract",
            trace["topology"]["matches_frozen_contract"],
            trace["topology"],
        ),
        check(
            "registered_native_route_use_triggers_producer_owned_susceptibility_formation",
            formation_update["formation_update_applied"]
            and abs(formed_closure["S_by_edge"]["1"] - EXPECTED_FORMED_S)
            <= TOLERANCE
            and trace["formation"]["formation_packet_exhausted"],
            trace["formation"],
        ),
        check(
            "formed_closure_restores_before_progression",
            internal_output_digest_exact(loaded_formed)
            and validate_closure(loaded_formed),
            loaded_formed,
        ),
        check(
            "matched_native_progression_is_identical_between_closure_lanes",
            progression_matrix["native_v1_identity_equal_after_matched_progression"]
            and progression_matrix["native_v2_identity_equal_after_matched_progression"]
            and progression_matrix["native_budget_equal_after_matched_progression"],
            progression_matrix,
        ),
        check(
            "exact_receipts_drive_monotonic_bounded_relaxation",
            all(
                abs(observed - expected) <= TOLERANCE
                for observed, expected in zip(
                    progression_matrix["active_S_sequence"],
                    EXPECTED_RELAXATION_SEQUENCE,
                )
            )
            and len(progression_matrix["active_S_sequence"])
            == len(EXPECTED_RELAXATION_SEQUENCE)
            and validate_closure(loaded_relaxed)
            and s_weakening >= MIN_S_WEAKENING,
            trace["relaxation"],
        ),
        check(
            "same_native_state_different_S_changes_native_readout",
            readout_matrix[
                "same_complete_native_state_different_S_changes_registered_readout"
            ]
            and g_weakening >= MIN_EFFECTIVE_CONDUCTANCE_WEAKENING
            and flux_change >= MIN_SIGNED_FLUX_CHANGE,
            trace["native_readout"],
        ),
        check(
            "readout_shape_is_monotonic_and_local",
            readout_matrix["S_monotonic_decrease"]
            and readout_matrix["g_effective_monotonic_decrease"]
            and readout_matrix["signed_flux_monotonic_decrease"]
            and not readout_matrix["complete_state_mediation_claimed"],
            readout_matrix,
        ),
        check(
            "native_coherence_budget_and_topology_preserved_during_readout",
            all(
                row["coherence_unchanged"]
                and row["budget_unchanged"]
                and row["cleanup"]["original_native_conductance_restored"]
                and row["cleanup"][
                    "closure_conductance_not_left_for_unqualified_step"
                ]
                and row["cleanup"]["native_identity_v1_exact_after_cleanup"]
                and row["cleanup"]["native_identity_v2_exact_after_cleanup"]
                and row["cleanup"]["complete_snapshot_exact_after_cleanup"]
                and not row["cleanup"][
                    "complete_changed_path_diff_after_cleanup"
                ]
                for row in readout_rows
            ),
            readout_rows,
        ),
        check(
            "closure_observed_inputs_match_declared_allowlists",
            trace["input_audit"]["formation_exact_allowlist_match"]
            and trace["input_audit"]["relaxation_exact_allowlist_match"]
            and trace["input_audit"]["readout_exact_allowlist_match"]
            and not trace["input_audit"]["prohibited_inputs_observed"],
            trace["input_audit"],
        ),
        check(
            "readout_authority_and_diagnostic_boundary_explicit",
            trace["readout_authority"]["readout_request_authority"]
            == "experiment_harness"
            and trace["readout_authority"][
                "susceptibility_and_conductance_insertion_authority"
            ]
            == "candidate_C_closure"
            and trace["readout_authority"]["potential_flux_computation_authority"]
            == "native_GRC9V3_kernels"
            and not trace["readout_authority"]["ordinary_LGRC_step_consumes_S"]
            and not trace["native_readout"][
                "state_mutating_future_behavior_supported"
            ],
            {
                "authority": trace["readout_authority"],
                "readout": trace["native_readout"],
            },
        ),
        check(
            "closure_and_native_readout_replay_exact",
            trace["restoration"]["formed_closure_internal_digest_exact"]
            and trace["restoration"]["relaxed_closure_internal_digest_exact"]
            and trace["restoration"]["formed_readout_replay_exact"]
            and trace["restoration"]["relaxed_readout_replay_exact"],
            trace["restoration"],
        ),
        check(
            "candidate_C_lane_controls_resolved",
            control_matrix["lane_specific_controls_resolved"] == 5
            and all(
                row["control_status"] in {"passed", "failed_closed"}
                for row in controls
            ),
            control_matrix,
        ),
        check(
            "carrier_ledger_and_native_memory_boundaries_preserved",
            trace["representation_boundary"][
                "susceptibility_update_magnitude_ledger_role"
            ]
            == "report_only_noncausal"
            and not trace["representation_boundary"][
                "native_susceptibility_state_present"
            ]
            and not trace["representation_boundary"][
                "closure_state_is_native_memory"
            ]
            and not trace["representation_boundary"]["resource_cost_supported"]
            and not trace["representation_boundary"][
                "free_noncoherence_state_naturalized"
            ],
            trace["representation_boundary"],
        ),
        check(
            "functional_resemblance_not_overpromoted_as_strict_ontological_fidelity",
            not trace["theory_positioning"][
                "strict_2025_11_coherence_only_ontology"
            ]["candidate_C_is_closest"]
            and trace["theory_positioning"][
                "strict_2025_11_coherence_only_ontology"
            ]["closest_added_mechanism"]
            == "Candidate_B"
            and trace["theory_positioning"][
                "functional_reflexive_geometry_resemblance"
            ]["candidate_C_is_closest"]
            and trace["theory_positioning"][
                "functional_reflexive_geometry_resemblance"
            ]["functional_resemblance_is_not_ontological_fidelity"],
            trace["theory_positioning"],
        ),
        check(
            "producer_C_R_DR4_ceiling_preserved",
            trace["classification"]["current_decay_relation_ladder_rung"] == "DR4"
            and trace["classification"]["DR4_supported"]
            and not trace["classification"]["DR5_supported"]
            and not trace["classification"]["DR6_supported"]
            and not trace["classification"]["native_upgrade_allowed"],
            trace["classification"],
        ),
        check(
            "protected_runtime_contracts_unchanged",
            all(git_diff_empty(path) for path in PROTECTED_PATHS),
            list(PROTECTED_PATHS),
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
        check("no_absolute_paths_in_records", no_absolute_paths(trace), None),
        check(
            "unsafe_claim_flags_false",
            not any(trace["unsafe_claim_flags"].values()),
            trace["unsafe_claim_flags"],
        ),
        check(
            "I10_obligations_preserved",
            not control_matrix["complete_I10_control_matrix_claimed"]
            and not control_matrix["DR5_control_gate_complete"],
            control_matrix,
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_I9C_candidate_checks_failed"
    trace["output_digest"] = digest_value(trace)
    TRACE.write_text(canonical_json(trace), encoding="utf-8")

    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-C",
        "artifact_kind": "route_susceptibility_relaxation_candidate",
        "artifact_schema_version": "n31_i9c_susceptibility_relaxation_candidate_v1",
        "generated_at": GENERATED_AT,
        "status": trace["status"],
        "acceptance_state": trace["acceptance_state"],
        "command": COMMAND,
        "script": SCRIPT_RELATIVE,
        "source_trace": {
            "path": relative(TRACE),
            "sha256": sha256_file(TRACE),
            "output_digest": trace["output_digest"],
        },
        "result_summary": {
            "initial_S": S_FLOOR,
            "formed_S": formed_closure["S_by_edge"]["1"],
            "relaxed_S": relaxed_closure["S_by_edge"]["1"],
            "S_weakening": s_weakening,
            "g_native": formed_readout["g_native"],
            "formed_g_effective": formed_readout["g_effective"],
            "relaxed_g_effective": relaxed_readout["g_effective"],
            "g_effective_weakening": g_weakening,
            "formed_signed_flux": formed_readout[
                "signed_flux_on_registered_edge"
            ],
            "relaxed_signed_flux": relaxed_readout[
                "signed_flux_on_registered_edge"
            ],
            "signed_flux_change": flux_change,
            "matched_native_progression_identity_exact": (
                active_identity == omitted_identity
            ),
            "relation_authority": trace["relation_authority"],
            "mediation_strength": readout_matrix["mediation_strength"],
            "readout_kind": readout_matrix["readout_kind"],
        },
        "classification": trace["classification"],
        "representation_boundary": trace["representation_boundary"],
        "producer_residue": trace["producer_residue"],
        "naturalization_debt": trace["naturalization_debt"],
        "theory_positioning": trace["theory_positioning"],
        "I10_handoff": {
            "I9C_consumption_role": "core_positive_candidate_C_execution",
            "formal_recursive_candidate_row_pending": True,
            "complete_control_matrix_pending": True,
            "DR5_pending": True,
            "DR6_pending": True,
            "candidate_C_reusable_contract_pending": True,
            "remaining_candidate_C_controls": [
                "duplicate_progression_receipt",
                "wrong_lineage_same_event_kind",
                "correct_lineage_wrong_edge",
                "nonqualifying_native_event",
                "restored_processed_receipt_set_duplicate_suppression",
            ],
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
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    result = payload["result_summary"]
    checks = "\n".join(
        f"| `{row['check_id']}` | {str(row['passed']).lower()} |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 9-C - Route-Susceptibility Relaxation

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
current rung = provisional producer-mediated C-R / DR4
DR5_supported = false
DR6_supported = false
native lane = D0a / DR2 unchanged
```

## Geometry And Formation

The three-node fixture contains a source route `0--1` and a registered
susceptible/readout edge `1--2`. A native `0.4` route-use packet crosses edge 1
from node 1 to node 2. Its exact arrival receipt triggers the producer-owned
closure, which raises susceptibility from `{result['initial_S']}` to
`{result['formed_S']}` under the frozen formation equation. Native route use
does not itself form susceptibility.

The packet changes native coherence conservatively. It does not directly write
conductance. The separately restored closure state is the only carrier of `S`.

## Relaxation Under Matched Progression

Two restored branches execute the same four native packet events on disjoint
edge 0. Their complete native v1/v2 identities and budgets remain equal. In the
active branch, the producer-owned closure consumes each exact arrival receipt
and applies `S_next = 0.5 + 0.75 * (S - 0.5)`. In the omitted branch, `S`
remains formed.

```text
formed S = {result['formed_S']}
relaxed S = {result['relaxed_S']}
S weakening = {result['S_weakening']}
```

The native events are experiment-scheduled and the closure callback is
producer-owned. This is not autonomous native susceptibility decay.

## Closure-Orchestrated Native-Kernel Readout

Before readout, both rows consume the same complete native state. The experiment
harness requests the readout; the Candidate C closure inserts the effective
edge-1 conductance after native conductance reconstruction; native GRC9V3
kernels compute potential and flux:

```text
g_native = {result['g_native']}
formed g_effective = {result['formed_g_effective']}
relaxed g_effective = {result['relaxed_g_effective']}
g_effective weakening = {result['g_effective_weakening']}

formed signed flux = {result['formed_signed_flux']}
relaxed signed flux = {result['relaxed_signed_flux']}
signed flux change = {result['signed_flux_change']}
```

This establishes bounded partial mediation through the registered edge's
conductance. The potential solution is graph-level. The result is a diagnostic
native-kernel flux computation, not packet transport, a coherence transition,
or an ordinary `LGRC9V3.step()` that consumes `S`. Exact pre-application native
v1/v2 identities and the complete snapshot are restored after every hook.

## Representation And Claim Boundary

`S` is versioned non-coherence closure state. The susceptibility-update
magnitude ledger is report-only and noncausal; it is not a cost ledger. Native
LGRC has no susceptibility memory or ordinary hook for this partial pipeline.
No resource cost is established, and the independently causal non-coherence
state is not naturalized into RC coherence. The weakening clock is the sequence
of experiment-scheduled edge-0 arrival receipts, not route-local proper time.

## Theory Positioning

Candidate C is closest to the *functional appearance* of reflexive geometry:
prior route use changes `S`, `S` changes effective conductance, and native
potential/flux diagnostics change. It is not closest to the strict 2025-11
coherence-only ontology. Under identical complete native coherence state,
independently restored `S` changes the readout, so `S` is an additional causal
degree of freedom. Candidate B is the closest added mechanism to the strict
ontology; D0a remains the preferred overall theory target.

Candidate C is therefore an effective closure or possible theory-extension
candidate. Naturalization would require `S` to be exactly reconstructable from
source-current `C/J_C` history with no independent freedom, or a native
`C_fast/C_slow` decomposition in which route use and ordinary coherence
dynamics form and relax the slow mode.

Candidate C therefore reaches provisional producer-mediated `C-R / DR4`.
`DR5` still requires I10's formal recursive row and complete control matrix;
`DR6` additionally requires a reusable closure contract. Native D0a remains at
`DR2`, and ordinary D0-R remains untested.

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
