#!/usr/bin/env python3
"""Build N31 I9-C.2 native exact-history closure admission records."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.models import LGRC9V3, PortEdge
from pygrc.models.grc_9_v3_runtime import (
    compute_base_conductance,
    compute_flux,
    compute_potential,
)


GENERATED_AT = "2026-07-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i9c2_native_exact_history_closure_artifacts"
I9C1 = OUTPUTS / "n31_exact_derived_susceptibility_i9c1.json"
I9C1_TRACE = OUTPUTS / "n31_i9c1_exact_derived_susceptibility_source_current_trace.json"
I9C1_PREREGISTRATION = (
    OUTPUTS
    / "n31_i9c1_exact_derived_susceptibility_artifacts"
    / "n31_i9c1_preregistration.json"
)
I9C_ARTIFACTS = OUTPUTS / "n31_i9c_susceptibility_relaxation_artifacts"
FORMED_SOURCE = I9C_ARTIFACTS / "n31_i9c_post_formation_snapshot.json"
RELAXED_SOURCE = I9C_ARTIFACTS / "n31_i9c_active_progression_snapshot.json"
RUNTIME = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime.py"
CONTRACT = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_contract.py"
RUNTIME_STATE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime_state.py"
PACKETS = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_packets.py"
SPEC = ROOT / "specs" / "lgrc-9-v3-spec.md"
EXAMPLE_README = ROOT / "examples" / "lgrc9v3" / "README.md"
EXAMPLE_PRODUCE_STEP = (
    ROOT / "examples" / "lgrc9v3" / "autonomous_produce_then_step.py"
)
EXAMPLE_NATIVE_LOOP = ROOT / "examples" / "lgrc9v3" / "native_packet_loop.py"
EXAMPLE_HELPER_CHAIN = (
    ROOT / "examples" / "lgrc9v3" / "active_lgrc3_causal_history.py"
)
PREREGISTRATION = ARTIFACT_DIR / "n31_i9c2_preregistration.json"
RUNTIME_GAP_AUDIT = ARTIFACT_DIR / "n31_i9c2_runtime_gap_audit.json"
NATIVE_CONTRACT = ARTIFACT_DIR / "n31_i9c2_native_extension_contract.json"
CONTROL_PLAN = ARTIFACT_DIR / "n31_i9c2_invariance_and_null_plan.json"
PHASE8_HANDOFF = ARTIFACT_DIR / "n31_i9c2_phase8_handoff.json"
C1_REVISION_RECEIPT = ARTIFACT_DIR / "n31_i9c2_c1_revision_receipt.json"
DERIVATION_MATRIX = ARTIFACT_DIR / "n31_i9c2_generalized_derivation_matrix.json"
RESTORATION_MATRIX = ARTIFACT_DIR / "n31_i9c2_native_restoration_matrix.json"
INVARIANCE_MATRIX = ARTIFACT_DIR / "n31_i9c2_invariance_matrix.json"
PRODUCER_STEP_MATRIX = ARTIFACT_DIR / "n31_i9c2_producer_step_matrix.json"
TRACE = OUTPUTS / "n31_i9c2_native_exact_history_closure_admission_trace.json"
OUTPUT = OUTPUTS / "n31_native_exact_history_closure_i9c2.json"
REPORT = REPORTS / "n31_native_exact_history_closure_i9c2.md"
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_native_exact_history_closure_i9c2.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
GOVERNANCE_BASE_REVISION = "236351695e36f88be85b7ed429911d58fad57b32"
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
    I9C1: {
        "sha256": "30d2ceca6c208d11097bae5c699cdc90aa9e2b91c1ef2988bd3d333d3a89dbe9",
        "output_digest": "2853511bbb0e8604e69b5b1b805c6e49f22eb8b6b17d1630f669064adae3015e",
    },
    I9C1_TRACE: {
        "sha256": "57e9ab2ca3239a4feda40e0bcb7963548824ec75baa97029bd4516288bee3353",
        "output_digest": None,
    },
    I9C1_PREREGISTRATION: {
        "sha256": "13d3958117ad404ed0a8e8831bdbbe6f61577198dbe1de0e3f3d786a8941f038",
        "output_digest": "17454fd22814459390790078113c661c175656a83369fc13b2804777fcb355fb",
    },
    FORMED_SOURCE: {
        "sha256": "67ca45402fdd64ea8ac7d57f72720cc05623e863a4a8d9dedf200302611b79d3",
        "output_digest": None,
    },
    RELAXED_SOURCE: {
        "sha256": "21a6269e429bd9e2c23a0e4cc9646dcb4902ffdfd3b420234666b58a3751d79f",
        "output_digest": None,
    },
    RUNTIME: {
        "sha256": "55d05aa03a4cf62cb42f18753aa572119011b6c4424bf2051a7ed0f6c78932d4",
        "output_digest": None,
    },
    CONTRACT: {
        "sha256": "b86fb41ab530a7aa01abdf01dbc048da10c2e312a18c8b874cbd1386c4794680",
        "output_digest": None,
    },
    RUNTIME_STATE: {
        "sha256": "ef409403954749a45fbf444116a9a253b95b3e2d74a119006f1cbb364a83630c",
        "output_digest": None,
    },
    PACKETS: {
        "sha256": "14d99292e18e2fe34e0fd5c6a1f69051e82115a051d142f10792775e2321e58f",
        "output_digest": None,
    },
    SPEC: {
        "sha256": "a272102d8463359c2f9d7a40ce63b3be52509b517da67579127ab6845ff36dc4",
        "output_digest": None,
    },
    EXAMPLE_README: {
        "sha256": "1d479c3b3b7c7c8adaaca23b6371914717f73c408b6f9b735f89cbf18858f6b4",
        "output_digest": None,
    },
    EXAMPLE_PRODUCE_STEP: {
        "sha256": "37274cc63ff90696689de807609fe184e167fc3a0c4adcb5421eeabbd2440c1f",
        "output_digest": None,
    },
    EXAMPLE_NATIVE_LOOP: {
        "sha256": "3bff7c0f85a664c1ee5d57d07cec82ff88baa48ef1aa1b87978f0fd6656c0a3b",
        "output_digest": None,
    },
    EXAMPLE_HELPER_CHAIN: {
        "sha256": "7057cf41f9f59ad6f9b00ea616ff97716abeea95b858a9bb8a21bb0c2851e9e2",
        "output_digest": None,
    },
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


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    if "output_digest" not in value:
        return False
    return value["output_digest"] == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def source_record(path: Path) -> dict[str, Any]:
    expected = SOURCE_IDENTITIES[path]
    actual_sha = sha256_file(path)
    record: dict[str, Any] = {
        "path": relative(path),
        "expected_sha256": expected["sha256"],
        "actual_sha256": actual_sha,
        "sha256_exact": actual_sha == expected["sha256"],
    }
    if expected["output_digest"] is not None:
        value = load_json(path)
        record.update(
            {
                "expected_output_digest": expected["output_digest"],
                "actual_output_digest": value.get("output_digest"),
                "internal_output_digest_exact": internal_output_digest_exact(value),
                "output_digest_exact": (
                    value.get("output_digest") == expected["output_digest"]
                ),
            }
        )
    return record


def git_diff_empty(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", GOVERNANCE_BASE_REVISION, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def write_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(record)
    value.pop("output_digest", None)
    value["output_digest"] = digest_value(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8")
    return value


def native_runtime(snapshot: dict[str, Any]) -> dict[str, Any]:
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    if not isinstance(runtime, dict):
        raise TypeError("native LGRC runtime artifact must be a mapping")
    return runtime


def arrival_history(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in native_runtime(snapshot)["packet_processing_log"]:
        event = result["processed_event"]
        if event["event_kind"] != "lgrc9v3_packet_arrival":
            continue
        rows.append(dict(event))
    return rows


def topology_edge_endpoints(snapshot: dict[str, Any]) -> dict[int, frozenset[int]]:
    return {
        int(edge["edge_id"]): frozenset(
            {
                int(edge["endpoint_a"]["node_id"]),
                int(edge["endpoint_b"]["node_id"]),
            }
        )
        for edge in snapshot["topology"]["edges"]
    }


def generalized_relation_contract(
    source_contract: dict[str, Any],
) -> dict[str, Any]:
    fixture_relation = source_contract["relation_contract"]
    formation = fixture_relation["formation_receipt_predicate"]
    contract = {
        "relation_schema": "n31_C2_general_physical_history_susceptibility_v1",
        "S_floor": float(fixture_relation["S_floor"]),
        "S_max": float(fixture_relation["S_max"]),
        "alpha": float(fixture_relation["alpha"]),
        "rho": float(fixture_relation["rho"]),
        "registered_susceptibility_route": {
            "edge_id": int(formation["edge_id"]),
            "source_node_id": int(formation["source_node_id"]),
            "target_node_id": int(formation["target_node_id"]),
        },
        "formation_rule": (
            "every_committed_arrival_on_registered_edge_in_registered_orientation"
        ),
        "progression_rule": (
            "later_committed_arrivals_on_physical_edges_incident_to_route_source_"
            "excluding_registered_susceptibility_edge"
        ),
        "causal_order_source": "native_packet_processing_log_sequence",
        "relation": (
            "S_e=S_floor+clip(sum(alpha*q_r*rho^N_later_local_progression),"
            "0,S_max-S_floor)"
        ),
        "identifier_fields_used_for_duplicate_integrity_only": (
            "event_id",
            "packet_id",
        ),
        "causal_fields": (
            "committed_event_kind",
            "transferred_coherence_amount",
            "physical_edge",
            "physical_orientation",
            "causal_sequence_order",
            "registered_route_support",
        ),
        "noncausal_fields": (
            "event_id",
            "packet_id",
            "lineage_label",
            "absolute_scheduler_index",
            "absolute_event_time",
            "topology_semantic_label",
        ),
        "fixture_specific_match_fields": (),
        "hard_coded_fixture_node_numbers": False,
        "registered_node_edge_ids_are_addressing_not_semantics": True,
        "independent_S_state_allowed": False,
        "external_history_archive_allowed": False,
    }
    return {**contract, "relation_identity": digest_value(contract)}


def derive_generalized_s(
    snapshot: dict[str, Any],
    relation: dict[str, Any],
) -> dict[str, Any]:
    history = arrival_history(snapshot)
    event_ids = [str(row["event_id"]) for row in history]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError("duplicate committed arrival identity")

    route = relation["registered_susceptibility_route"]
    edge_id = int(route["edge_id"])
    source_node_id = int(route["source_node_id"])
    target_node_id = int(route["target_node_id"])
    endpoints = topology_edge_endpoints(snapshot)
    if endpoints.get(edge_id) != frozenset({source_node_id, target_node_id}):
        raise ValueError("registered susceptibility route does not match topology")
    progression_edge_ids = {
        candidate_edge_id
        for candidate_edge_id, candidate_endpoints in endpoints.items()
        if candidate_edge_id != edge_id and source_node_id in candidate_endpoints
    }

    formation_rows: list[tuple[int, dict[str, Any]]] = []
    for index, row in enumerate(history):
        if (
            int(row["edge_id"]) == edge_id
            and int(row["source_node_id"]) == source_node_id
            and int(row["target_node_id"]) == target_node_id
        ):
            formation_rows.append((index, row))

    contributions: list[dict[str, Any]] = []
    for formation_index, formation in formation_rows:
        later_progression = [
            row
            for row in history[formation_index + 1 :]
            if int(row["edge_id"]) in progression_edge_ids
        ]
        causal_distance = len(later_progression)
        contribution = (
            float(relation["alpha"])
            * float(formation["amount"])
            * float(relation["rho"]) ** causal_distance
        )
        contributions.append(
            {
                "formation_physical_record": {
                    "event_kind": formation["event_kind"],
                    "edge_id": int(formation["edge_id"]),
                    "source_node_id": int(formation["source_node_id"]),
                    "target_node_id": int(formation["target_node_id"]),
                    "amount": float(formation["amount"]),
                },
                "causal_distance": causal_distance,
                "contribution": contribution,
            }
        )

    raw_contribution = sum(row["contribution"] for row in contributions)
    clipped_contribution = min(
        max(raw_contribution, 0.0),
        float(relation["S_max"]) - float(relation["S_floor"]),
    )
    derived_s = float(relation["S_floor"]) + clipped_contribution
    physical_history = [
        {
            "event_kind": row["event_kind"],
            "edge_id": int(row["edge_id"]),
            "source_node_id": int(row["source_node_id"]),
            "target_node_id": int(row["target_node_id"]),
            "amount": float(row["amount"]),
        }
        for row in history
    ]
    return {
        "derived_S": derived_s,
        "formation_count": len(formation_rows),
        "formation_contributions": contributions,
        "progression_edge_ids": sorted(progression_edge_ids),
        "raw_contribution": raw_contribution,
        "clipped_contribution": clipped_contribution,
        "physical_history_identity": digest_value(physical_history),
        "relation_identity": relation["relation_identity"],
        "stored_S_state_present": False,
        "external_history_archive_required": False,
    }


def derive_or_block(
    snapshot: dict[str, Any], relation: dict[str, Any]
) -> dict[str, Any]:
    try:
        return {"status": "derived", **derive_generalized_s(snapshot, relation)}
    except (KeyError, TypeError, ValueError) as exc:
        return {"status": "blocked", "reason": str(exc)}


def mutate_noncausal_fields(snapshot: dict[str, Any], mutation: str) -> dict[str, Any]:
    value = deepcopy(snapshot)
    log = native_runtime(value)["packet_processing_log"]
    if mutation == "identifiers":
        for ordinal, row in enumerate(log):
            row["processed_event"]["event_id"] = f"permuted-event-{ordinal}"
            row["processed_event"]["packet_id"] = f"permuted-packet-{ordinal}"
            row["packet_record"]["packet_id"] = f"permuted-packet-{ordinal}"
    elif mutation == "lineage_labels":
        for ordinal, row in enumerate(log):
            row["packet_record"]["source_lineage_id"] = f"renamed-source-{ordinal}"
            row["packet_record"]["target_lineage_id"] = f"renamed-target-{ordinal}"
    elif mutation == "scheduler_shift":
        for row in log:
            row["processed_event"]["scheduler_event_index"] += 1000
    elif mutation == "time_translation":
        for row in log:
            row["processed_event"]["event_time_key"] += 1000.0
    elif mutation == "semantic_labels":
        for node in value["topology"]["nodes"]:
            node["payload"] = {"renamed_semantic_label": f"node-{node['node_id']}"}
        for edge in value["topology"]["edges"]:
            edge["payload"] = {"renamed_semantic_label": f"edge-{edge['edge_id']}"}
    elif mutation == "wrong_direction_interspersion":
        formation = next(
            row
            for row in log
            if row["processed_event"]["event_kind"]
            == "lgrc9v3_packet_arrival"
            and int(row["processed_event"]["edge_id"]) == 1
        )
        inserted = deepcopy(formation)
        event = inserted["processed_event"]
        event["event_id"] = "wrong-direction-interspersed-event"
        event["packet_id"] = "wrong-direction-interspersed-packet"
        event["source_node_id"], event["target_node_id"] = (
            event["target_node_id"],
            event["source_node_id"],
        )
        inserted["packet_record"]["packet_id"] = event["packet_id"]
        log.append(inserted)
    else:
        raise ValueError(f"unknown noncausal mutation {mutation!r}")
    return value


def remap_roles(
    snapshot: dict[str, Any], relation: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    value = deepcopy(snapshot)
    node_map = {0: 10, 1: 20, 2: 30}
    edge_map = {0: 100, 1: 200}
    for node in value["topology"]["nodes"]:
        node["node_id"] = node_map[int(node["node_id"])]
    for edge in value["topology"]["edges"]:
        edge["edge_id"] = edge_map[int(edge["edge_id"])]
        edge["endpoint_a"]["node_id"] = node_map[int(edge["endpoint_a"]["node_id"])]
        edge["endpoint_b"]["node_id"] = node_map[int(edge["endpoint_b"]["node_id"])]
    for result in native_runtime(value)["packet_processing_log"]:
        event = result["processed_event"]
        event["edge_id"] = edge_map[int(event["edge_id"])]
        event["source_node_id"] = node_map[int(event["source_node_id"])]
        event["target_node_id"] = node_map[int(event["target_node_id"])]
    remapped_relation = deepcopy(relation)
    route = remapped_relation["registered_susceptibility_route"]
    route["edge_id"] = edge_map[int(route["edge_id"])]
    route["source_node_id"] = node_map[int(route["source_node_id"])]
    route["target_node_id"] = node_map[int(route["target_node_id"])]
    remapped_relation.pop("relation_identity", None)
    remapped_relation["relation_identity"] = digest_value(remapped_relation)
    return value, remapped_relation


def remove_last_progression(snapshot: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(snapshot)
    log = native_runtime(value)["packet_processing_log"]
    for index in range(len(log) - 1, -1, -1):
        event = log[index]["processed_event"]
        if (
            event["event_kind"] == "lgrc9v3_packet_arrival"
            and int(event["edge_id"]) == 0
        ):
            log.pop(index)
            return value
    raise ValueError("no progression receipt available")


def duplicate_committed_arrival(snapshot: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(snapshot)
    log = native_runtime(value)["packet_processing_log"]
    arrival = next(
        row
        for row in log
        if row["processed_event"]["event_kind"] == "lgrc9v3_packet_arrival"
    )
    log.append(deepcopy(arrival))
    return value


def node_plus_packet_budget(model: LGRC9V3) -> float:
    state = model.get_state()
    ledger = state.packet_ledger
    if ledger is None:
        raise ValueError("LGRC packet ledger is required")
    return sum(float(node.coherence) for node in state.base_state.nodes.values()) + float(
        ledger.in_flight_packet_total
    )


def run_lgrc_faithful_candidate_step(
    source_path: Path,
    relation: dict[str, Any],
    *,
    row_id: str,
    transport_scale: float = 0.25,
) -> dict[str, Any]:
    """Run a producer/step composition without modifying the LGRC runtime."""

    model = LGRC9V3.load(str(source_path))
    pre_snapshot = model.snapshot()
    pre_derived = derive_generalized_s(pre_snapshot, relation)
    params = model.get_params()
    state = model.get_state()
    work_state = deepcopy(state.base_state)
    compute_base_conductance(
        work_state,
        evolution=params.evolution,
        modes=params.constitutive_semantic_modes,
    )
    route = relation["registered_susceptibility_route"]
    edge_id = int(route["edge_id"])
    source_node_id = int(route["source_node_id"])
    target_node_id = int(route["target_node_id"])
    edge = work_state.port_edges[edge_id]
    g_native = float(work_state.base_conductance[edge_id])
    g_effective = g_native * float(pre_derived["derived_S"])
    work_state.base_conductance[edge_id] = g_effective
    work_state.port_edges[edge_id] = PortEdge(
        edge.node_u,
        edge.port_u,
        edge.node_v,
        edge.port_v,
        conductance=g_effective,
        flux_uv=edge.flux_uv,
    )
    compute_potential(work_state, evolution=params.evolution)
    compute_flux(work_state, evolution=params.evolution)
    computed_edge = work_state.port_edges[edge_id]
    if (
        int(computed_edge.node_u) == source_node_id
        and int(computed_edge.node_v) == target_node_id
    ):
        oriented_flux = float(computed_edge.flux_uv)
    elif (
        int(computed_edge.node_v) == source_node_id
        and int(computed_edge.node_u) == target_node_id
    ):
        oriented_flux = -float(computed_edge.flux_uv)
    else:
        raise ValueError("registered route orientation does not match native edge")
    packet_amount = max(0.0, oriented_flux) * float(transport_scale)
    if packet_amount <= 0.0:
        raise ValueError("history-conditioned native flux does not admit transport")

    budget_before = node_plus_packet_budget(model)
    source_before = float(
        model.get_state().base_state.nodes[source_node_id].coherence
    )
    receiver_before = float(
        model.get_state().base_state.nodes[target_node_id].coherence
    )
    runtime_state = model.get_state()
    ledger = runtime_state.packet_ledger
    assert ledger is not None
    model.schedule_packet_departure(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        edge_id=edge_id,
        amount=packet_amount,
        departure_event_time_key=float(runtime_state.event_time_key) + 1.0,
        arrival_event_time_key=float(runtime_state.event_time_key) + 2.0,
        scheduler_event_index=int(runtime_state.scheduler_event_index) + 1,
        packet_index=len(ledger.packet_records),
    )
    scheduled_budget = node_plus_packet_budget(model)
    departure_result = model.step()
    source_after_departure = float(
        model.get_state().base_state.nodes[source_node_id].coherence
    )
    budget_after_departure = node_plus_packet_budget(model)
    arrival_result = model.step()
    receiver_after_arrival = float(
        model.get_state().base_state.nodes[target_node_id].coherence
    )
    budget_after_arrival = node_plus_packet_budget(model)
    post_snapshot = model.snapshot()
    post_derived = derive_generalized_s(post_snapshot, relation)

    source_debit = source_before - source_after_departure
    receiver_credit = receiver_after_arrival - receiver_before
    return {
        "row_id": row_id,
        "source_snapshot": relative(source_path),
        "step_class": "experiment_owned_LGRC_faithful_producer_executor_step",
        "geometry_computation_authority": "native_GRC9V3_kernels_on_state_copy",
        "packet_scheduling_authority": "experiment_candidate_producer",
        "packet_execution_authority": "LGRC9V3.step",
        "runtime_source_modified": False,
        "pre_derived_S": pre_derived["derived_S"],
        "g_native": g_native,
        "g_effective": g_effective,
        "oriented_flux": oriented_flux,
        "transport_scale": transport_scale,
        "packet_amount": packet_amount,
        "source_debit": source_debit,
        "receiver_credit": receiver_credit,
        "budget_before": budget_before,
        "budget_after_schedule": scheduled_budget,
        "budget_after_departure": budget_after_departure,
        "budget_after_arrival": budget_after_arrival,
        "conservation_error": budget_after_arrival - budget_before,
        "source_debit_matches_packet": abs(source_debit - packet_amount) <= 1e-12,
        "receiver_credit_matches_packet": abs(receiver_credit - packet_amount) <= 1e-12,
        "node_plus_packet_budget_conserved": (
            abs(scheduled_budget - budget_before) <= 1e-12
            and abs(budget_after_departure - budget_before) <= 1e-12
            and abs(budget_after_arrival - budget_before) <= 1e-12
        ),
        "departure_processed_event_kind": departure_result.bookkeeping.get(
            "processed_event_kind"
        ),
        "arrival_processed_event_kind": arrival_result.bookkeeping.get(
            "processed_event_kind"
        ),
        "post_derived_S": post_derived["derived_S"],
        "transport_entered_native_history": (
            post_derived["formation_count"] > pre_derived["formation_count"]
        ),
        "later_geometry_relation_changed": (
            post_derived["derived_S"] != pre_derived["derived_S"]
        ),
        "ordinary_native_step_derived_S_itself": False,
        "existing_native_support": False,
    }


def build() -> dict[str, Any]:
    source_records = [source_record(path) for path in SOURCE_IDENTITIES]
    i9c1 = load_json(I9C1)
    i9c1_preregistration = load_json(I9C1_PREREGISTRATION)
    formed_source = load_json(FORMED_SOURCE)
    relaxed_source = load_json(RELAXED_SOURCE)
    runtime_text = RUNTIME.read_text(encoding="utf-8")
    contract_text = CONTRACT.read_text(encoding="utf-8")
    spec_text = SPEC.read_text(encoding="utf-8")

    relation = generalized_relation_contract(i9c1_preregistration)
    formed_derived = derive_generalized_s(formed_source, relation)
    relaxed_derived = derive_generalized_s(relaxed_source, relation)

    formed_restored_snapshot = LGRC9V3.load(str(FORMED_SOURCE)).snapshot()
    relaxed_restored_snapshot = LGRC9V3.load(str(RELAXED_SOURCE)).snapshot()
    formed_restored = derive_generalized_s(formed_restored_snapshot, relation)
    relaxed_restored = derive_generalized_s(relaxed_restored_snapshot, relation)

    invariant_mutations = (
        "identifiers",
        "lineage_labels",
        "scheduler_shift",
        "time_translation",
        "semantic_labels",
        "wrong_direction_interspersion",
    )
    invariant_rows = [
        {
            "control_id": mutation,
            "baseline_S": relaxed_derived["derived_S"],
            "mutated_S": derive_generalized_s(
                mutate_noncausal_fields(relaxed_source, mutation), relation
            )["derived_S"],
        }
        for mutation in invariant_mutations
    ]
    remapped_snapshot, remapped_relation = remap_roles(relaxed_source, relation)
    remapped_derived = derive_generalized_s(remapped_snapshot, remapped_relation)
    physically_changed = derive_generalized_s(
        remove_last_progression(relaxed_source), relation
    )
    duplicate_result = derive_or_block(
        duplicate_committed_arrival(relaxed_source), relation
    )
    history_removed = deepcopy(formed_source)
    native_runtime(history_removed)["packet_processing_log"] = []
    history_removed_result = derive_generalized_s(history_removed, relation)
    injected_s = deepcopy(relaxed_source)
    native_runtime(injected_s).setdefault("cached_quantities", {})[
        "injected_authoritative_S"
    ] = 0.999
    injected_s_result = derive_generalized_s(injected_s, relation)

    dr1_formation_supported = (
        formed_derived["formation_count"] >= 1
        and formed_derived["derived_S"] > relation["S_floor"]
    )
    dr2_restoration_supported = (
        dr1_formation_supported
        and formed_restored["derived_S"] == formed_derived["derived_S"]
        and relaxed_restored["derived_S"] == relaxed_derived["derived_S"]
    )
    weakening_direction_observed = (
        formed_derived["derived_S"] > relaxed_derived["derived_S"]
    )
    formed_candidate_step = run_lgrc_faithful_candidate_step(
        FORMED_SOURCE,
        relation,
        row_id="formed_history_candidate_step",
    )
    relaxed_candidate_step = run_lgrc_faithful_candidate_step(
        RELAXED_SOURCE,
        relation,
        row_id="progressed_history_candidate_step",
    )
    producer_dr3_weakening_supported = weakening_direction_observed
    producer_dr4_transport_supported = (
        formed_candidate_step["node_plus_packet_budget_conserved"]
        and relaxed_candidate_step["node_plus_packet_budget_conserved"]
        and formed_candidate_step["packet_amount"]
        != relaxed_candidate_step["packet_amount"]
        and formed_candidate_step["transport_entered_native_history"]
        and relaxed_candidate_step["transport_entered_native_history"]
        and formed_candidate_step["later_geometry_relation_changed"]
        and relaxed_candidate_step["later_geometry_relation_changed"]
    )
    dr3_native_internal_weakening_supported = False
    dr4_ordinary_native_transport_supported = False
    relation_lane_rung = "DR2" if dr2_restoration_supported else (
        "DR1" if dr1_formation_supported else "DR0"
    )
    producer_extension_lane_rung = (
        "DR4"
        if producer_dr4_transport_supported
        else "DR3"
        if producer_dr3_weakening_supported
        else relation_lane_rung
    )
    native_runtime_lane_rung = "DR0"

    current_runtime_audit = {
        "audit_scope": "current_accepted_LGRC9V3_runtime_before_C2",
        "native_packet_history_serialized": (
            '"packet_processing_log"' in RUNTIME_STATE.read_text(encoding="utf-8")
        ),
        "ordinary_step_routes_arrival_local_update": (
            "self._apply_arrival_local_update(" in runtime_text
        ),
        "ordinary_step_rebuilds_GRC9V3_transport_geometry": (
            "rebuild_grc9v3_transport_state(" in runtime_text[
                runtime_text.index("    def step(self)") :
            ]
        ),
        "history_derived_susceptibility_mode_present": (
            "native_lgrc_exact_history_constitutive_closure" in contract_text
        ),
        "history_derived_geometry_consumption_present": (
            "derive_exact_history_susceptibility" in runtime_text
        ),
        "current_spec_defines_native_exact_history_closure": (
            "Native Exact-History Constitutive Closure" in spec_text
        ),
        "current_route_amount_inputs": (
            "absolute amount",
            "arrival amount_fraction",
            "arrival amount fallback",
        ),
        "current_runtime_conclusion": (
            "serialized_history_exists_but_ordinary_step_has_no_native_"
            "exact_history_constitutive_consumption_hook"
        ),
    }

    preregistration = write_record(
        PREREGISTRATION,
        {
            "artifact_kind": "n31_i9c2_preregistration",
            "artifact_schema_version": "n31_i9c2_preregistration_v1",
            "generated_at": GENERATED_AT,
            "iteration": "I9-C.2",
            "title": "Native Exact-History Constitutive Closure",
            "candidate_id": "C_native_exact_history_constitutive_closure",
            "source_candidate": "C_derived_history_susceptibility",
            "initial_rung": "DR0",
            "representation_class": (
                "proposed_native_added_mechanism_exact_history_closure"
            ),
            "experiment_runtime_mutation_allowed": False,
            "src_changes_allowed": False,
            "admission_question": (
                "Can an authorized future native LGRC extension derive route "
                "susceptibility from admitted serialized coherence-current history, "
                "consume it in ordinary transport, conserve coherence, and feed the "
                "resulting current back into later derivation without authoritative S?"
            ),
            "non_admissible_shortcuts": (
                "experiment_wrapper_conductance_write",
                "experiment_defined_LGRC_subclass_claimed_as_native",
                "stored_or_injected_authoritative_S",
                "diagnostic_flux_without_executed_transport",
                "fixture_identifier_or_timestamp_matching",
                "retroactive_inheritance_of_I9C1_DR4",
            ),
            "execution_decision": (
                "execute_generalized_relation_native_restoration_and_LGRC_faithful_"
                "producer_step_gates_without_runtime_mutation_then_handoff_native_gap"
            ),
            "rung_assignment_policy": (
                "assign_relation_carrier_and_native_runtime_lanes_separately_"
                "from_observed_gates"
            ),
            "lane_status_policy": {
                "relation_carrier_lane": "DR2",
                "producer_extension_lane": "provisional_DR4_pending_I10",
                "native_runtime_lane": "DR0",
                "highest_observed_evidence_ceiling": "DR4",
                "unqualified_native_C2_DR4_allowed": False,
            },
            "weakening_semantics": {
                "name": "activity_indexed_local_susceptibility_relaxation",
                "quiescence_decay": False,
                "wall_clock_decay": False,
                "route_use_reinforcement": True,
                "other_incident_activity_relaxation": True,
                "autonomous_temporal_decay_claim_allowed": False,
            },
            "susceptibility_scale_semantics": {
                "S_equals_1": "unattenuated_native_conductance",
                "S_equals_floor": "unformed_candidate_mode_conductance_floor",
                "formation": "reduces_candidate_attenuation",
                "relaxation": "returns_toward_candidate_attenuation_floor",
                "conductance_enhancement_above_native_allowed": False,
            },
        },
    )

    derivation_matrix = write_record(
        DERIVATION_MATRIX,
        {
            "artifact_kind": "n31_i9c2_generalized_derivation_matrix",
            "artifact_schema_version": "n31_i9c2_generalized_derivation_matrix_v1",
            "generated_at": GENERATED_AT,
            "relation": relation,
            "rows": (
                {
                    "row_id": "formed_native_history",
                    "source_snapshot": relative(FORMED_SOURCE),
                    **formed_derived,
                },
                {
                    "row_id": "progressed_native_history",
                    "source_snapshot": relative(RELAXED_SOURCE),
                    **relaxed_derived,
                },
            ),
            "formation_supported": dr1_formation_supported,
            "weakening_direction_observed": weakening_direction_observed,
            "weakening_amount": (
                formed_derived["derived_S"] - relaxed_derived["derived_S"]
            ),
            "source_progression_authority": (
                "experiment_scheduled_native_packet_processing_from_I9C"
            ),
            "native_autonomous_progression_supported": False,
            "weakening_class": "activity_indexed_local_susceptibility_relaxation",
            "quiescence_decay": False,
            "wall_clock_decay": False,
            "route_use_reinforcement": True,
            "other_incident_activity_relaxation": True,
            "packetization_invariance": {
                "status": "not_run_blocks_native_admission",
                "current_distance_measure": "qualifying_committed_arrival_count",
                "comparison_required": (
                    "one_0.10_progression_packet",
                    "two_0.05_progression_packets",
                ),
                "matched_integrated_coherence_required": True,
                "matched_physical_interval_required": True,
                "decision_required": (
                    "equal_derived_S_or_event_granularity_declared_physically_"
                    "load_bearing"
                ),
                "preferred_future_measure": (
                    "integrated_local_activity_or_registered_proper_time_distance"
                ),
            },
        },
    )

    restoration_matrix = write_record(
        RESTORATION_MATRIX,
        {
            "artifact_kind": "n31_i9c2_native_restoration_matrix",
            "artifact_schema_version": "n31_i9c2_native_restoration_matrix_v1",
            "generated_at": GENERATED_AT,
            "rows": (
                {
                    "row_id": "formed_snapshot_load_rederive",
                    "before_S": formed_derived["derived_S"],
                    "after_load_S": formed_restored["derived_S"],
                    "exact": (
                        formed_derived["derived_S"]
                        == formed_restored["derived_S"]
                    ),
                },
                {
                    "row_id": "progressed_snapshot_load_rederive",
                    "before_S": relaxed_derived["derived_S"],
                    "after_load_S": relaxed_restored["derived_S"],
                    "exact": (
                        relaxed_derived["derived_S"]
                        == relaxed_restored["derived_S"]
                    ),
                },
            ),
            "native_snapshot_load_used": True,
            "stored_S_required": False,
            "external_history_archive_required": False,
            "DR2_relation_lane_gate_passed": dr2_restoration_supported,
        },
    )

    invariance_matrix = write_record(
        INVARIANCE_MATRIX,
        {
            "artifact_kind": "n31_i9c2_invariance_matrix",
            "artifact_schema_version": "n31_i9c2_invariance_matrix_v1",
            "generated_at": GENERATED_AT,
            "invariant_rows": tuple(
                {
                    **row,
                    "invariant": row["baseline_S"] == row["mutated_S"],
                }
                for row in invariant_rows
            ),
            "role_preserving_renumbering": {
                "baseline_S": relaxed_derived["derived_S"],
                "remapped_S": remapped_derived["derived_S"],
                "invariant": (
                    relaxed_derived["derived_S"]
                    == remapped_derived["derived_S"]
                ),
            },
            "physically_different_history": {
                "baseline_S": relaxed_derived["derived_S"],
                "changed_S": physically_changed["derived_S"],
                "predictable_change": (
                    physically_changed["derived_S"]
                    > relaxed_derived["derived_S"]
                ),
            },
            "duplicate_committed_arrival": {
                "result": duplicate_result,
                "failed_closed": duplicate_result["status"] == "blocked",
            },
            "history_removed": {
                "derived_S": history_removed_result["derived_S"],
                "baseline_floor": relation["S_floor"],
                "returned_to_floor": (
                    history_removed_result["derived_S"] == relation["S_floor"]
                ),
            },
            "injected_S": {
                "injected_value": 0.999,
                "derived_S": injected_s_result["derived_S"],
                "baseline_S": relaxed_derived["derived_S"],
                "no_authority": (
                    injected_s_result["derived_S"]
                    == relaxed_derived["derived_S"]
                ),
            },
            "runtime_only_controls_pending": (
                "feature_enabled_no_history_candidate_floor_behavior",
                "common_S_clamp",
                "derived_S_bypass",
                "same_S_different_histories_same_packet_amount",
                "same_history_recomputed_S_same_packet_amount",
                "feature_disabled_byte_identical_baseline",
                "unrelated_edge_native_conductance_unchanged",
                "ordinary_step_transport_dependency",
                "reflexive_feedback_second_derivation",
                "packetization_invariance",
                "multi_cycle_stability",
                "topology_lifecycle",
            ),
            "control_scope_status": {
                "control_plan_complete": True,
                "relation_controls_executed": True,
                "producer_transport_controls_executed": True,
                "native_runtime_controls_executed": False,
            },
        },
    )

    producer_step_matrix = write_record(
        PRODUCER_STEP_MATRIX,
        {
            "artifact_kind": "n31_i9c2_producer_step_matrix",
            "artifact_schema_version": "n31_i9c2_producer_step_matrix_v1",
            "generated_at": GENERATED_AT,
            "composition_contract": {
                "producer_phase": (
                    "derive_history_relation_compute_native_geometry_and_schedule_"
                    "one_packet"
                ),
                "executor_phase": "LGRC9V3_step_processes_departure_then_arrival",
                "producer_processes_packet_itself": False,
                "producer_mutates_live_conductance": False,
                "producer_mutates_node_coherence": False,
                "runtime_source_modified": False,
                "source_pattern": (
                    "examples_lgrc9v3_producer_then_step_and_helper_chain"
                ),
            },
            "rows": (formed_candidate_step, relaxed_candidate_step),
            "same_reduced_current_projection": i9c1.get("result_summary", {}).get(
                "current_C_JC_geometry_projection_equal"
            ),
            "different_history_changes_transport_amount": (
                formed_candidate_step["packet_amount"]
                != relaxed_candidate_step["packet_amount"]
            ),
            "producer_mediated_DR3_supported": producer_dr3_weakening_supported,
            "producer_mediated_DR4_supported": producer_dr4_transport_supported,
            "producer_extension_lane_rung": "provisional_DR4_pending_I10",
            "producer_extension_lane_ceiling": producer_extension_lane_rung,
            "native_runtime_lane_rung": native_runtime_lane_rung,
            "existing_native_support": False,
            "ordinary_LGRC_step_derives_relation": False,
            "producer_input_audit": {
                "allowed": (
                    "derived_S",
                    "exact_current_native_state_copy",
                    "registered_route",
                    "frozen_transport_integration_parameter",
                ),
                "forbidden": (
                    "branch_id",
                    "source_snapshot_name",
                    "outcome_history",
                    "semantic_labels",
                    "expected_packet_amount",
                ),
                "current_implementation_uses_forbidden_inputs": False,
            },
            "direct_mediation_controls": {
                "status": "not_run_pending_I10",
                "required": (
                    "common_S_clamp_removes_packet_split",
                    "derived_S_bypass_removes_history_conditioning",
                    "same_S_different_histories_same_packet_amount",
                    "same_history_recomputed_S_same_packet_amount",
                ),
            },
            "transport_integration_contract": {
                "equation": "q_packet=max(0,J_e)*delta_tau",
                "executed_delta_tau": 0.25,
                "current_authority": "preregistered_experiment_producer_parameter",
                "physical_or_numerical_meaning": "unresolved_naturalization_debt",
                "outcome_tuned": False,
                "future_required_semantics": (
                    "native_integration_interval_or_packetization_interval_or_"
                    "another_dimensioned_transport_measure"
                ),
                "future_required_controls": (
                    "flux_times_interval_units_close_to_coherence",
                    "zero_flux_emits_no_packet",
                    "negative_flux_reverses_or_refuses_by_frozen_rule",
                    "insufficient_source_refuses_atomically_or_clips_by_frozen_rule",
                    "packet_never_exceeds_available_source_coherence",
                ),
            },
            "feedback_depth": {
                "completed_transport_to_second_derivation": "passed",
                "second_derivation_to_second_transport_to_third_derivation": (
                    "not_run"
                ),
                "complete_native_cycle_count": 1,
                "multi_cycle_stability_supported": False,
            },
        },
    )

    native_contract = write_record(
        NATIVE_CONTRACT,
        {
            "artifact_kind": "n31_i9c2_native_extension_contract",
            "artifact_schema_version": "n31_i9c2_native_extension_contract_v1",
            "generated_at": GENERATED_AT,
            "candidate_id": "C_native_exact_history_constitutive_closure",
            "required_native_loop": (
                "native_discrete_coherence_current_history",
                "native_exact_derivation_of_S_e",
                "native_effective_conductance",
                "native_potential_and_flux",
                "native_packet_admission_and_transport",
                "conservative_C_update",
                "packet_current_history_update",
                "next_S_e_derived_from_changed_history",
            ),
            "relation": {
                "form": (
                    "S_e(t)=S_floor+clip(sum(alpha*q_r*rho^delta_tau),"
                    "0,S_max-S_floor)"
                ),
                "history_domain": (
                    "admitted_coherence_current_history_for_edge_or_registered_"
                    "local_route_support"
                ),
                "allowed_causal_inputs": (
                    "transferred_coherence_amount",
                    "physical_edge_and_orientation",
                    "committed_event_kind",
                    "causal_order_or_local_proper_time_distance",
                    "registered_route_support",
                ),
                "forbidden_causal_inputs": (
                    "event_id",
                    "packet_id",
                    "lineage_string_or_semantic_label",
                    "absolute_scheduler_index",
                    "hard_coded_timestamp",
                    "fixture_node_number",
                ),
                "executed_generalized_relation": relation,
                "theory_correspondence": (
                    "discrete_coherence_current_history_functional"
                ),
                "broader_J_C_equivalence_established": False,
                "weakening_class": (
                    "activity_indexed_local_susceptibility_relaxation"
                ),
                "S_semantics": {
                    "S_floor": relation["S_floor"],
                    "S_max": relation["S_max"],
                    "S_floor_effect": (
                        "candidate_mode_conductance_is_floor_times_native"
                    ),
                    "S_max_effect": "unattenuated_native_conductance",
                    "above_native_enhancement": False,
                },
                "packetization_invariance_status": (
                    "not_run_blocks_native_admission"
                ),
            },
            "state_authority": {
                "authoritative_state": "serialized_native_C_JC_history",
                "stored_S_allowed": False,
                "exact_recomputation_required": True,
                "exact_cache_allowed": True,
                "cache_independent_write_authority_allowed": False,
                "cache_history_mismatch_action": "fail_closed",
                "injected_cache_can_change_result": False,
                "cache_identity_must_include": (
                    "relation_parameters",
                    "topology_version",
                    "history_identity",
                ),
                "full_history_recomputation_must_equal_incremental_cache": True,
                "history_pruning_requires_declared_error_or_cutoff_contract": True,
                "approximate_truncated_cache_may_be_called_exact": False,
            },
            "native_architecture_options": {
                "integrated_native_step": (
                    "step_derives_relation_computes_geometry_admits_and_executes_"
                    "transport"
                ),
                "library_owned_native_producer_plus_executor": (
                    "canonical_library_producer_derives_relation_computes_geometry_"
                    "and_schedules_work_then_step_executes_it"
                ),
                "either_architecture_may_be_native": True,
                "native_requirements": (
                    "library_owned_provider",
                    "native_spec_contract",
                    "canonical_runtime_invocation",
                    "no_experiment_harness_required",
                    "complete_provider_identity_restored",
                    "feature_default_off",
                    "derived_relation_has_no_external_authority",
                    "native_conservative_executor",
                ),
            },
            "topology_lifecycle_contract": {
                "status": "unresolved_blocks_reusable_native_contract",
                "events_requiring_policy": (
                    "registered_edge_deleted",
                    "registered_edge_recreated",
                    "route_orientation_reversed",
                    "parallel_edge_replaces_original",
                    "route_source_changes",
                    "topology_version_changes",
                ),
                "admissible_policy_families": (
                    "frozen_topology_invalidates_relation",
                    "versioned_route_identity",
                    "explicit_registered_migration",
                ),
                "silent_identifier_reuse_allowed": False,
            },
            "stability_contract": {
                "status": "not_run_blocks_native_admission",
                "required": (
                    "bounded_or_declared_oscillatory_repeated_route_use",
                    "S_never_exceeds_S_max",
                    "one_arrival_adds_exactly_one_contribution",
                    "departure_arrival_not_double_counted",
                    "no_unbounded_recursive_event_cascade",
                    "saturation_behavior_explicit",
                    "progression_attenuation_exact_for_old_and_new_contributions",
                    "long_run_coherence_conserved_and_nonnegative",
                ),
            },
            "ordinary_runtime_requirements": {
                "feature_default_off": True,
                "ordinary_step_consumes_history_derived_geometry": True,
                "experiment_wrapper_conductance_write_required": False,
                "manual_cleanup_required": False,
                "changed_packet_transition_required": True,
                "node_plus_packet_coherence_conserved": True,
                "reflexive_second_derivation_required": True,
                "second_complete_transport_cycle_required": True,
            },
            "rung_contract": {
                "DR0": "contract_or_unexecuted_candidate_only",
                "DR1": "native_history_derived_susceptibility_forms",
                "DR2": "native_restoration_preserves_exact_derivability",
                "DR3": "native_internal_progression_weakens_relation",
                "DR4": "ordinary_native_transport_causally_depends_on_relation",
                "DR5": "later_replay_invariants_controls_and_mismatch_refusal",
                "DR6": "later_reusable_generalized_native_contract",
            },
            "claim_boundary": {
                "existing_native_support": False,
                "native_candidate_extension_supported": False,
                "current_state_D0a_supported": False,
                "native_D0a_ceiling": "DR2",
                "ordinary_D0_R_bridge_tested": False,
                "relation_carrier_lane_rung": relation_lane_rung,
                "producer_extension_lane_rung": (
                    "provisional_DR4_pending_I10"
                ),
                "producer_extension_lane_ceiling": producer_extension_lane_rung,
                "native_runtime_lane_rung": native_runtime_lane_rung,
                "DR1_relation_formation_supported": dr1_formation_supported,
                "DR2_relation_restoration_supported": dr2_restoration_supported,
                "DR3_native_internal_weakening_supported": (
                    dr3_native_internal_weakening_supported
                ),
                "DR4_ordinary_native_transport_supported": (
                    dr4_ordinary_native_transport_supported
                ),
                "DR3_producer_mediated_weakening_supported": (
                    producer_dr3_weakening_supported
                ),
                "DR4_producer_mediated_transport_supported": (
                    producer_dr4_transport_supported
                ),
                "RCAE_admission_status": (
                    "blocked_until_DR5_and_reusable_provider_contract"
                ),
            },
        },
    )

    control_plan = write_record(
        CONTROL_PLAN,
        {
            "artifact_kind": "n31_i9c2_invariance_and_null_plan",
            "artifact_schema_version": "n31_i9c2_invariance_and_null_plan_v1",
            "generated_at": GENERATED_AT,
            "required_invariance_controls": (
                "event_ID_permutation",
                "packet_ID_permutation",
                "lineage_label_renaming",
                "absolute_scheduler_index_shift",
                "absolute_time_translation_with_intervals_preserved",
                "role_preserving_node_edge_renumbering",
                "irrelevant_interspersed_events",
                "physically_different_current_history",
            ),
            "required_active_nulls": (
                "history_removed",
                "feature_enabled_no_history_candidate_floor_behavior",
                "duplicate_qualifying_receipt",
                "wrong_edge_or_direction",
                "semantic_label_only",
                "injected_S_has_no_authority",
                "derived_S_bypass",
                "feature_disabled_byte_identical_baseline",
                "unrelated_edge_unchanged",
            ),
            "required_execution_tests": (
                "native_formation",
                "snapshot_load_exact_derivability",
                "native_internal_weakening",
                "same_reduced_projection_different_history_ordinary_step",
                "actual_conservative_transport",
                "reflexive_feedback_second_derivation",
            ),
            "deferred_naturalization_controls": {
                "packetization": (
                    "one_0.10_vs_two_0.05_progression_packets",
                    "matched_integrated_coherence",
                    "matched_physical_interval",
                ),
                "direct_mediation": (
                    "common_S_clamp",
                    "derived_S_bypass",
                    "same_S_different_histories",
                    "same_history_recomputed_S",
                ),
                "transport_integration": (
                    "zero_flux",
                    "negative_flux",
                    "insufficient_source_coherence",
                    "packet_amount_bounded_by_source",
                    "units_close",
                ),
                "multi_cycle_stability": (
                    "at_least_two_complete_native_cycles",
                    "saturation_or_oscillation_declared",
                    "no_double_counting",
                    "no_unbounded_cascade",
                    "long_run_conservation_and_nonnegativity",
                ),
                "topology_lifecycle": (
                    "edge_deletion",
                    "edge_recreation",
                    "orientation_reversal",
                    "parallel_edge_replacement",
                    "route_source_change",
                    "topology_version_change",
                ),
                "cache_and_pruning": (
                    "full_recompute_equals_cache",
                    "cache_removal_neutral",
                    "cache_injection_no_authority",
                    "cache_history_mismatch_fails_closed",
                    "pruning_contract_explicit",
                ),
            },
            "execution_status": (
                "relation_restoration_and_producer_step_executed_native_runtime_"
                "consumption_controls_deferred_unless_naturalization_selected"
            ),
            "control_status": {
                "control_plan_complete": True,
                "relation_level_invariance_controls": "executed",
                "producer_step_transport_controls": "executed",
                "native_runtime_consumption_controls": (
                    "not_run_runtime_change_not_authorized_in_N31"
                ),
                "packetization_invariance": "not_run",
                "direct_mediation_controls": "not_run",
                "multi_cycle_stability_controls": "not_run",
                "topology_lifecycle_controls": "not_run",
                "cache_pruning_controls": "not_run",
            },
        },
    )

    runtime_gap_audit = write_record(
        RUNTIME_GAP_AUDIT,
        {
            "artifact_kind": "n31_i9c2_runtime_gap_audit",
            "artifact_schema_version": "n31_i9c2_runtime_gap_audit_v1",
            "generated_at": GENERATED_AT,
            "source_records": source_records,
            "current_runtime_audit": current_runtime_audit,
            "gap_classification": {
                "serialized_native_history_missing": False,
                "generalized_experiment_relation_missing": False,
                "native_exact_history_functional_missing": True,
                "ordinary_constitutive_consumption_hook_missing": True,
                "ordinary_history_conditioned_packet_transport_missing": True,
                "reflexive_feedback_to_next_geometry_missing": True,
                "gap_owner": "future_authorized_LGRC_phase8_extension",
                "gap_may_be_closed_inside_N31_experiment": False,
            },
            "wrapper_boundary": {
                "I9C1_wrapper_diagnostic_retained": True,
                "wrapper_or_subclass_can_satisfy_native_C2": False,
                "LGRC_faithful_producer_step_candidate_allowed": True,
                "producer_step_can_upgrade_existing_native_support": False,
                "reason": (
                    "native_C2_requires_library_owned_ordinary_step_consumption_"
                    "and_transport_under_a_default_off_runtime_contract"
                ),
            },
        },
    )

    c1_revision_receipt = write_record(
        C1_REVISION_RECEIPT,
        {
            "artifact_kind": "n31_i9c2_c1_revision_receipt",
            "artifact_schema_version": "n31_i9c2_c1_revision_receipt_v1",
            "generated_at": GENERATED_AT,
            "lineage_role": "informational_revision_lineage_not_evidence_source",
            "previous_reviewed_artifact": {
                "output_digest_prefix": "33e77c892977",
                "full_output_digest_available": False,
                "artifact_retained_in_repository": False,
                "consumed_by_C2": False,
            },
            "current_corrected_artifact": {
                "path": relative(I9C1),
                "sha256": sha256_file(I9C1),
                "output_digest": i9c1["output_digest"],
                "consumed_by_C2": True,
                "source_identity_exact": True,
            },
            "correction_classes": (
                "same_reduced_projection_not_same_complete_native_state",
                "causal_history_state_retained_after_independent_S_elimination",
                "fixture_bound_functional_and_generality_ceiling_recorded",
                "packet_log_named_discrete_coherence_current_history_proxy",
                "independent_classification_separated_from_fresh_execution",
                "history_changes_partitioned_from_integrity_and_storage_controls",
                "control_statuses_normalized",
            ),
            "scientific_conclusion_change": (
                "provisional_DR4_unchanged_scope_authority_and_debt_tightened"
            ),
            "C2_source_rule": (
                "consume_only_current_corrected_exact_artifact_and_record_earlier_"
                "review_identity_as_non_authoritative_lineage"
            ),
        },
    )

    phase8_handoff = write_record(
        PHASE8_HANDOFF,
        {
            "artifact_kind": "n31_i9c2_phase8_handoff",
            "artifact_schema_version": "n31_i9c2_phase8_handoff_v1",
            "generated_at": GENERATED_AT,
            "handoff_status": (
                "deferred_conditional_naturalization_requirements_recorded"
            ),
            "candidate_id": "C_native_exact_history_constitutive_closure",
            "implementation_selection_status": "not_selected_by_N31",
            "blocks_N31_iteration_10": False,
            "required_change_scope": (
                "default_off_LGRC9V3_mode_and_policy_contract",
                "general_exact_history_derivation_surface",
                "ordinary_step_constitutive_geometry_consumption",
                "conservative_packet_admission_and_transport",
                "derived_only_telemetry_and_snapshot_recomputation",
                "candidate_specific_and_disabled_baseline_tests",
                "spec_and_phase_checklist_updates",
            ),
            "future_governance": {
                "candidate_native_extension_diff_authorized": (
                    "must_be_true_only_on_future_implementation_branch"
                ),
                "diff_allowlist_exact": True,
                "feature_default_off": True,
                "existing_runtime_behavior_unchanged_when_disabled": True,
                "full_baseline_conformance_required": True,
                "candidate_specific_conformance_required": True,
            },
            "native_architecture_decision": {
                "status": "open_before_implementation",
                "integrated_step_allowed": True,
                "library_owned_producer_plus_step_allowed": True,
                "experiment_owned_producer_is_native": False,
                "decision_criterion": (
                    "library_ownership_native_spec_canonical_invocation_complete_"
                    "restoration_default_off_and_conservative_execution"
                ),
            },
            "native_readmission_gates": {
                "DR1": (
                    "canonical_native_provider_derives_formation_from_native_history"
                ),
                "DR2": (
                    "save_load_and_cache_removal_preserve_exact_derivation"
                ),
                "DR3": (
                    "canonical_native_progression_weakens_without_experiment_"
                    "scheduling_being_load_bearing"
                ),
                "DR4": (
                    "canonical_native_producer_or_step_consumes_relation_and_"
                    "executes_changed_conservative_transport"
                ),
                "feedback": (
                    "completed_transport_changes_next_geometry_and_that_geometry_"
                    "is_consumed_in_a_subsequent_native_cycle"
                ),
                "baseline": (
                    "feature_disabled_is_byte_identical_to_accepted_LGRC"
                ),
                "provider": (
                    "wrong_policy_topology_parameters_or_history_identity_refuses"
                ),
            },
            "deferred_naturalization_debt": {
                "packetization_invariance": "open",
                "transport_interval_naturalization": "open",
                "direct_mediation_controls": "open",
                "multi_cycle_stability": "open",
                "topology_lifecycle": "open",
                "cache_and_history_pruning": "open",
            },
            "N31_consumption_after_future_implementation": (
                "do_not_rewrite_I9C_or_I9C1",
                "readmit_native_runtime_lane_from_DR0",
                "consume_relation_lane_DR2_as_prerequisite_not_runtime_upgrade",
                "record_new_provider_revision_and_contract_digest",
                "execute_DR1_through_DR4_gates_before_I10",
                "retain_existing_native_D0a_DR2_boundary",
            ),
            "producer_DR4_inherited_by_native_lane": False,
            "RCAE_admission_status": (
                "blocked_until_DR5_and_reusable_provider_contract"
            ),
            "I10_opened": False,
        },
    )

    artifacts = (
        preregistration,
        derivation_matrix,
        restoration_matrix,
        invariance_matrix,
        producer_step_matrix,
        runtime_gap_audit,
        native_contract,
        control_plan,
        c1_revision_receipt,
        phase8_handoff,
    )
    artifact_paths = (
        PREREGISTRATION,
        DERIVATION_MATRIX,
        RESTORATION_MATRIX,
        INVARIANCE_MATRIX,
        PRODUCER_STEP_MATRIX,
        RUNTIME_GAP_AUDIT,
        NATIVE_CONTRACT,
        CONTROL_PLAN,
        C1_REVISION_RECEIPT,
        PHASE8_HANDOFF,
    )
    manifest = [
        {
            "path": relative(path),
            "sha256": sha256_file(path),
            "artifact_role": artifact["artifact_kind"],
            "output_digest": artifact["output_digest"],
        }
        for path, artifact in zip(artifact_paths, artifacts, strict=True)
    ]

    checks = [
        check(
            "source_identities_exact",
            all(
                row["sha256_exact"]
                and row.get("output_digest_exact", True)
                and row.get("internal_output_digest_exact", True)
                for row in source_records
            ),
            source_records,
        ),
        check(
            "C_and_C1_preserved_as_separate_evidence",
            i9c1.get("classification", {}).get(
                "I9C_independent_state_result_replaced"
            )
            is False,
            "C2_is_additional_and_starts_at_DR0",
        ),
        check(
            "current_runtime_gap_classified_from_source",
            current_runtime_audit["native_packet_history_serialized"]
            and current_runtime_audit["ordinary_step_routes_arrival_local_update"]
            and not current_runtime_audit[
                "ordinary_step_rebuilds_GRC9V3_transport_geometry"
            ]
            and not current_runtime_audit[
                "history_derived_susceptibility_mode_present"
            ]
            and not current_runtime_audit[
                "history_derived_geometry_consumption_present"
            ],
            current_runtime_audit,
        ),
        check(
            "general_physical_history_contract_frozen",
            "fixture_node_number"
            in native_contract["relation"]["forbidden_causal_inputs"]
            and "transferred_coherence_amount"
            in native_contract["relation"]["allowed_causal_inputs"],
            native_contract["relation"],
        ),
        check(
            "independent_S_authority_forbidden",
            native_contract["state_authority"]["stored_S_allowed"] is False
            and native_contract["state_authority"][
                "cache_independent_write_authority_allowed"
            ]
            is False,
            native_contract["state_authority"],
        ),
        check(
            "ordinary_native_transport_gate_not_backfilled_by_wrapper",
            preregistration["execution_decision"]
            == "execute_generalized_relation_native_restoration_and_LGRC_faithful_"
            "producer_step_gates_without_runtime_mutation_then_handoff_native_gap"
            and native_contract["ordinary_runtime_requirements"][
                "experiment_wrapper_conductance_write_required"
            ]
            is False,
            preregistration["non_admissible_shortcuts"],
        ),
        check(
            "control_plan_declared_and_execution_scope_explicit",
            len(control_plan["required_invariance_controls"]) == 8
            and len(control_plan["required_active_nulls"]) == 9
            and len(control_plan["required_execution_tests"]) == 6
            and control_plan["control_status"]["control_plan_complete"]
            and control_plan["control_status"]["native_runtime_consumption_controls"]
            == "not_run_runtime_change_not_authorized_in_N31",
            {
                "invariance_count": len(control_plan["required_invariance_controls"]),
                "null_count": len(control_plan["required_active_nulls"]),
                "execution_test_count": len(control_plan["required_execution_tests"]),
            },
        ),
        check(
            "generalized_relation_formation_gate_passed",
            dr1_formation_supported
            and formed_derived["derived_S"] > relation["S_floor"]
            and formed_derived["formation_count"] >= 1,
            formed_derived,
        ),
        check(
            "native_restoration_exact_derivability_gate_passed",
            dr2_restoration_supported,
            restoration_matrix["rows"],
        ),
        check(
            "generalized_relation_invariance_controls_passed",
            all(row["invariant"] for row in invariance_matrix["invariant_rows"])
            and invariance_matrix["role_preserving_renumbering"]["invariant"]
            and invariance_matrix["physically_different_history"][
                "predictable_change"
            ]
            and invariance_matrix["duplicate_committed_arrival"]["failed_closed"]
            and invariance_matrix["history_removed"]["returned_to_floor"]
            and invariance_matrix["injected_S"]["no_authority"],
            invariance_matrix,
        ),
        check(
            "LGRC_faithful_producer_step_executes_conservative_transport",
            producer_dr4_transport_supported
            and producer_step_matrix["different_history_changes_transport_amount"]
            and all(
                row["source_debit_matches_packet"]
                and row["receiver_credit_matches_packet"]
                and row["node_plus_packet_budget_conserved"]
                and row["transport_entered_native_history"]
                and row["later_geometry_relation_changed"]
                for row in producer_step_matrix["rows"]
            ),
            producer_step_matrix,
        ),
        check(
            "relation_and_native_runtime_lanes_separated",
            preregistration["initial_rung"] == "DR0"
            and native_contract["claim_boundary"]["relation_carrier_lane_rung"]
            == relation_lane_rung
            and native_contract["claim_boundary"]["native_runtime_lane_rung"]
            == "DR0"
            and native_contract["claim_boundary"]["producer_extension_lane_rung"]
            == "provisional_DR4_pending_I10"
            and native_contract["claim_boundary"]["producer_extension_lane_ceiling"]
            == producer_extension_lane_rung
            and native_contract["claim_boundary"][
                "native_candidate_extension_supported"
            ]
            is False,
            native_contract["claim_boundary"],
        ),
        check(
            "deferred_naturalization_handoff_is_explicit",
            phase8_handoff["handoff_status"]
            == "deferred_conditional_naturalization_requirements_recorded"
            and phase8_handoff["implementation_selection_status"]
            == "not_selected_by_N31"
            and phase8_handoff["blocks_N31_iteration_10"] is False
            and len(phase8_handoff["required_change_scope"]) == 7,
            phase8_handoff["required_change_scope"],
        ),
        check(
            "weakening_and_susceptibility_semantics_are_explicit",
            preregistration["weakening_semantics"]["quiescence_decay"] is False
            and preregistration["weakening_semantics"]["wall_clock_decay"] is False
            and preregistration["weakening_semantics"]["route_use_reinforcement"]
            and preregistration["susceptibility_scale_semantics"][
                "conductance_enhancement_above_native_allowed"
            ]
            is False,
            {
                "weakening": preregistration["weakening_semantics"],
                "S": preregistration["susceptibility_scale_semantics"],
            },
        ),
        check(
            "deferred_naturalization_debt_and_readmission_gates_are_explicit",
            all(
                status == "open"
                for status in phase8_handoff[
                    "deferred_naturalization_debt"
                ].values()
            )
            and phase8_handoff["producer_DR4_inherited_by_native_lane"] is False
            and phase8_handoff["RCAE_admission_status"]
            == "blocked_until_DR5_and_reusable_provider_contract",
            {
                "debt": phase8_handoff["deferred_naturalization_debt"],
                "gates": phase8_handoff["native_readmission_gates"],
            },
        ),
        check(
            "C1_revision_lineage_is_explicit",
            c1_revision_receipt["current_corrected_artifact"]["output_digest"]
            == i9c1["output_digest"]
            and c1_revision_receipt["current_corrected_artifact"][
                "source_identity_exact"
            ]
            and c1_revision_receipt["previous_reviewed_artifact"]["consumed_by_C2"]
            is False,
            c1_revision_receipt,
        ),
        check(
            "src_and_protected_contracts_unchanged",
            git_diff_empty("src")
            and all(git_diff_empty(path) for path in PROTECTED_PATHS),
            {
                "governance_base_revision": GOVERNANCE_BASE_REVISION,
                "src_diff_empty": git_diff_empty("src"),
                "protected_paths_diff_empty": all(
                    git_diff_empty(path) for path in PROTECTED_PATHS
                ),
            },
        ),
        check(
            "I10_remains_unopened",
            phase8_handoff["I10_opened"] is False,
            "C2_execution_must_precede_any_I10_consumption",
        ),
        check(
            "no_absolute_paths_in_records",
            no_absolute_paths(
                {
                    "preregistration": preregistration,
                    "runtime_gap_audit": runtime_gap_audit,
                    "derivation_matrix": derivation_matrix,
                    "restoration_matrix": restoration_matrix,
                    "invariance_matrix": invariance_matrix,
                    "producer_step_matrix": producer_step_matrix,
                    "native_contract": native_contract,
                    "control_plan": control_plan,
                    "c1_revision_receipt": c1_revision_receipt,
                    "phase8_handoff": phase8_handoff,
                    "manifest": manifest,
                }
            ),
            True,
        ),
    ]
    failed_checks = [row["check_id"] for row in checks if not row["passed"]]

    trace = write_record(
        TRACE,
        {
            "artifact_kind": "n31_i9c2_native_exact_history_closure_admission_trace",
            "artifact_schema_version": (
                "n31_i9c2_native_exact_history_closure_admission_trace_v1"
            ),
            "generated_at": GENERATED_AT,
            "candidate_id": "C_native_exact_history_constitutive_closure",
            "source_candidate": "C_derived_history_susceptibility",
            "status": "passed" if not failed_checks else "failed",
            "acceptance_state": (
                "accepted_generalized_relation_and_native_restoration_"
                f"{relation_lane_rung}_and_LGRC_faithful_producer_step_"
                f"provisional_{producer_extension_lane_rung}_pending_I10_with_"
                "native_runtime_lane_DR0_and_deferred_conditional_"
                "naturalization_requirements_recorded"
            ),
            "relation_carrier_lane_rung": relation_lane_rung,
            "producer_extension_lane_rung": "provisional_DR4_pending_I10",
            "producer_extension_lane_ceiling": producer_extension_lane_rung,
            "native_runtime_lane_rung": native_runtime_lane_rung,
            "highest_observed_evidence_ceiling": producer_extension_lane_rung,
            "highest_observed_evidence_status": "provisional_pending_I10",
            "native_runtime_extension_executed": False,
            "native_runtime_extension_blocker": "N31_src_changes_not_allowed",
            "LGRC_faithful_producer_step_executed": True,
            "formed_derived_S": formed_derived["derived_S"],
            "progressed_derived_S": relaxed_derived["derived_S"],
            "weakening_direction_observed": weakening_direction_observed,
            "DR3_blocker": (
                "source_progression_was_experiment_scheduled_not_native_autonomous_"
                "ordinary_progression"
            ),
            "DR4_blocker": (
                "ordinary_LGRC_step_does_not_consume_history_derived_geometry"
            ),
            "current_runtime_audit": current_runtime_audit,
            "derivation_matrix_digest": derivation_matrix["output_digest"],
            "restoration_matrix_digest": restoration_matrix["output_digest"],
            "invariance_matrix_digest": invariance_matrix["output_digest"],
            "producer_step_matrix_digest": producer_step_matrix["output_digest"],
            "contract_digest": native_contract["output_digest"],
            "control_plan_digest": control_plan["output_digest"],
            "phase8_handoff_digest": phase8_handoff["output_digest"],
            "C1_revision_receipt_digest": c1_revision_receipt["output_digest"],
            "scientific_conclusion": (
                "C2_generalized_relation_forms_from_native_packet_history_and_"
                "survives_native_restoration_and_an_LGRC_faithful_producer_step_"
                "executes_history_conditioned_conservative_transport_with_feedback_"
                "but_existing_native_runtime_consumption_remains_unimplemented"
            ),
            "claim_boundary": native_contract["claim_boundary"],
            "checks": checks,
            "failed_checks": failed_checks,
        },
    )
    manifest.append(
        {
            "path": relative(TRACE),
            "sha256": sha256_file(TRACE),
            "artifact_role": trace["artifact_kind"],
            "output_digest": trace["output_digest"],
        }
    )

    payload = {
        "artifact_kind": "n31_native_exact_history_closure_i9c2",
        "artifact_schema_version": "n31_native_exact_history_closure_i9c2_v1",
        "generated_at": GENERATED_AT,
        "iteration": "I9-C.2",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": trace["acceptance_state"],
        "command": COMMAND,
        "candidate_identity": {
            "candidate_id": "C_native_exact_history_constitutive_closure",
            "source_candidate": "C_derived_history_susceptibility",
            "initial_rung": "DR0",
            "representation_class": (
                "proposed_native_added_mechanism_exact_history_closure"
            ),
        },
        "result_summary": {
            "relation_carrier_lane_rung": relation_lane_rung,
            "producer_extension_lane_rung": "provisional_DR4_pending_I10",
            "producer_extension_lane_ceiling": producer_extension_lane_rung,
            "native_runtime_lane_rung": native_runtime_lane_rung,
            "highest_observed_evidence_ceiling": producer_extension_lane_rung,
            "highest_observed_evidence_status": "provisional_pending_I10",
            "contract_supported": True,
            "current_runtime_gap_supported": True,
            "native_runtime_extension_executed": False,
            "LGRC_faithful_producer_step_executed": True,
            "native_candidate_extension_supported": False,
            "DR1_relation_formation_supported": dr1_formation_supported,
            "DR2_relation_restoration_supported": dr2_restoration_supported,
            "DR3_native_internal_weakening_supported": False,
            "DR4_ordinary_native_transport_supported": False,
            "DR3_producer_mediated_weakening_supported": (
                producer_dr3_weakening_supported
            ),
            "DR4_producer_mediated_transport_supported": (
                producer_dr4_transport_supported
            ),
            "weakening_direction_observed": weakening_direction_observed,
            "formed_derived_S": formed_derived["derived_S"],
            "progressed_derived_S": relaxed_derived["derived_S"],
            "current_state_D0a_supported": False,
            "native_D0a_unchanged": "DR2",
            "I9C_replaced": False,
            "I9C1_replaced": False,
            "I10_opened": False,
            "weakening_class": "activity_indexed_local_susceptibility_relaxation",
            "quiescence_decay": False,
            "RCAE_admission_status": (
                "blocked_until_DR5_and_reusable_provider_contract"
            ),
            "next_action": "iteration_10_added_mechanism_replay_and_controls",
        },
        "source_records": source_records,
        "generalized_derivation_matrix": derivation_matrix,
        "native_restoration_matrix": restoration_matrix,
        "invariance_matrix": invariance_matrix,
        "producer_step_matrix": producer_step_matrix,
        "runtime_gap_audit": runtime_gap_audit,
        "native_extension_contract": native_contract,
        "control_plan": control_plan,
        "C1_revision_receipt": c1_revision_receipt,
        "phase8_handoff": phase8_handoff,
        "governance": {
            "governance_base_revision": GOVERNANCE_BASE_REVISION,
            "src_changes_allowed": False,
            "src_diff_empty": git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(path) for path in PROTECTED_PATHS
            ),
        },
        "artifact_manifest": manifest,
        "checks": checks,
        "failed_checks": failed_checks,
    }
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    checks = "\n".join(
        f"| `{row['check_id']}` | {str(row['passed']).lower()} |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 9-C.2 - Native Exact-History Constitutive Closure

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
candidate = C_native_exact_history_constitutive_closure
relation/carrier lane = {payload['result_summary']['relation_carrier_lane_rung']}
producer extension lane = {payload['result_summary']['producer_extension_lane_rung']}
native runtime lane = {payload['result_summary']['native_runtime_lane_rung']}
highest observed evidence ceiling = {payload['result_summary']['highest_observed_evidence_ceiling']}
highest observed evidence status = {payload['result_summary']['highest_observed_evidence_status']}
LGRC-faithful producer step executed = true
native candidate extension supported = false
RCAE admission = blocked until DR5 and reusable provider contract
next action = Iteration 10 added-mechanism replay and controls
```

## What N31 Could Establish

C.2 replaces C.1's fixture matcher with a structural relation. A committed
arrival on the registered oriented route contributes transferred coherence.
Later committed arrivals on other physical edges incident to that route's
source advance causal distance. The relation consumes packet-processing order,
amount, edge, orientation, and registered route support; it does not consume
event IDs, packet IDs, lineage labels, absolute times, scheduler indices, or
fixture-specific node numbers.

The generalized relation forms at
`S={payload['result_summary']['formed_derived_S']}` and the progressed history
derives `S={payload['result_summary']['progressed_derived_S']}`. Native
`LGRC9V3.load()` round trips preserve both values exactly. Identifier, lineage,
clock, semantic-label, wrong-direction interspersion, and role-preserving
renumbering controls leave the value unchanged; removing a real progression
receipt changes it predictably; duplicate committed identity fails closed; and
injected `S` has no authority.

These gates support a **generalized relation/carrier lane at `DR2`**: formation
from native serialized history plus exact native restoration. This is stronger
than a contract-only `DR0` result, but it is not a native runtime extension.

The operational source is **native discrete coherence-current history**. Packet
amount represents transferred coherence, edge and orientation represent current
support and direction, and committed record order supplies causal ordering.
Equivalence to a broader continuous `J_C` representation is not established.

The current distance is the count of qualifying committed arrivals. Therefore
packetization invariance is still open: one `0.10` progression packet has not
yet been compared with two `0.05` packets under matched integrated coherence
and physical interval. Native admission must either prove equal `S` or declare
event granularity physically load-bearing. Integrated local activity or a
registered proper-time distance is the preferred future interpretation.

## What Susceptibility Means Here

`S` is a bounded multiplier on native conductance, not an enhancement beyond
native geometry:

```text
S = 1.0   unattenuated native conductance
S = 0.5   unformed candidate-mode conductance floor
formation reduces candidate attenuation
relaxation returns toward the candidate floor
```

The weakening is **activity-indexed local susceptibility relaxation**. It does
not proceed during quiescence or from wall-clock time. Route use reinforces the
relation; other committed incident activity advances attenuation. Generic
passive or autonomous temporal decay remains unsupported. A feature-on,
history-absent producer/runtime control at the `S=0.5` floor remains pending.

## LGRC-Faithful Producer Step

The existing examples establish a producer/executor pattern: producer logic
may inspect current LGRC state and schedule causal work, while `LGRC9V3.step()`
owns packet debit, in-flight accounting, arrival credit, and history emission.
C.2 uses that same boundary rather than requiring all candidate logic inside
the library's current `step()` implementation.

For both the formed and progressed histories, an experiment-owned candidate
step derives `S`, runs native GRC9V3 conductance/potential/flux kernels on a
state copy, converts the oriented flux into a preregistered packet amount, and
schedules one public LGRC packet departure. It does not mutate live
conductance, node coherence, or packet state. Two ordinary `LGRC9V3.step()`
calls then execute departure and arrival.

The equal reduced-state branches schedule different packet amounts:

```text
formed history packet = {payload['producer_step_matrix']['rows'][0]['packet_amount']}
progressed history packet = {payload['producer_step_matrix']['rows'][1]['packet_amount']}
```

In both rows, source debit equals packet amount, receiver credit equals packet
amount, and node-plus-packet coherence remains invariant. The completed packet
enters native history and changes the next derived relation. This supports a
**producer-mediated candidate-extension lane at provisional `DR4` pending
I10**: generalized formation, native restoration, producer-mediated weakening,
causal transport, and one feedback derivation. It is stronger than C.1's
diagnostic-only wrapper because transport actually executes and changes native
state.

The exact causal chain still requires direct mediation controls. A common-`S`
clamp, derived-`S` bypass, same-`S`/different-history comparison, and
same-history/recomputed-`S` comparison remain unrun. Those controls must prove
that the packet split is specifically caused by
`history -> S -> geometry -> flux -> packet`, not hidden branch logic.

The producer uses `q_packet=max(0,J_e)*0.25`. The coefficient is preregistered
and not outcome-tuned, but its physical or numerical meaning is unresolved.
Before native admission it must become a dimensioned integration or
packetization interval, with zero/negative flux, insufficient-source,
source-bound, and unit-closure controls.

Only one feedback depth has been demonstrated:

```text
transport -> changed native history -> second S derivation
```

A second `S -> geometry -> transport -> history` cycle, saturation behavior,
double-counting rejection, cascade bounds, and long-run nonnegative coherence
remain pending. The present positive reinforcement is bounded by `S_max`, but
multi-cycle stability has not been established.

## Why The Native Runtime Lane Remains DR0

C.2 asks for a native loop that the current accepted LGRC9V3 runtime does not
implement: serialized packet history must determine a route susceptibility,
ordinary `LGRC9V3.step()` must consume that relation as constitutive geometry,
the resulting flux must cause an actual conservative packet transition, and
that current must enter the history used by the next derivation.

The current runtime already serializes `packet_processing_log` and routes
arrival-triggered work through its ordinary local-update path. It does not,
however, derive susceptibility from that history or rebuild and consume
history-conditioned conductance, potential, and flux during the ordinary step.
That is the precise native gap. N31 is not authorized to change `src/*`, so it
cannot execute the runtime-consumption lane honestly.

The producer step is LGRC-faithful, but it is still experiment-owned candidate
logic. It therefore cannot upgrade `existing_native_support`, claim that the
current library's ordinary step derives susceptibility, or raise the native
runtime lane above `DR0`. Likewise, the weakening trajectory is
producer-mediated: its progression packets were scheduled by I9-C rather than
generated by an ordinary autonomous native progression rule.

Native ownership does not require all logic to live literally inside
`LGRC9V3.step()`. Either an integrated native step or a canonical library-owned
producer plus the native executor may qualify. In both cases the provider must
be library-owned, specified, invoked canonically without an experiment harness,
fully restored by provider identity, default-off, derived-only, and
conservative.

## Frozen Native Contract

The future native runtime lane starts at `DR0` and must implement:

```text
native discrete coherence-current history
-> exact derived S_e with no independent authority
-> native effective conductance
-> native potential and flux
-> native packet admission and transport
-> conservative C update
-> changed packet/current history
-> next S_e derived from that history
```

The relation may consume transferred coherence amount, physical edge and
orientation, committed event kind, causal order or local proper-time distance,
and registered route support. It may not causally consume event or packet IDs,
semantic lineage labels, absolute scheduler indices, hard-coded timestamps, or
fixture node numbers. A removable exact cache is allowed; authoritative stored
`S` is not.

Topology lifecycle is unresolved. Edge deletion/recreation, orientation
reversal, parallel replacement, route-source change, and topology-version
change need a frozen invalidation, versioned-identity, or explicit-migration
policy. Historical contributions may never silently attach to a reused ID.

Exact full-history scanning also remains a scaling debt. An incremental cache
is acceptable only if full recomputation is exact, cache removal is neutral,
injection has no authority, mismatches fail closed, identity includes relation
parameters and topology version, and pruning has an explicit cutoff/error
contract.

## Handoff

The generated handoff is a deferred conditional naturalization record, not an
implementation selection. It freezes the required default-off runtime surface,
canonical provider/executor integration, conservative transport, derived-only
telemetry, invariance controls, and disabled-baseline conformance. It does not
block I10. If an authorized implementation is selected later, its native lane
must restart at `DR0`; relation-lane `DR2` is a prerequisite, not an automatic
runtime upgrade. I9-C and I9-C.1 remain separate evidence and are not rewritten.
I10 remains unopened by C.2 and is the next N31 iteration.

The native tranche must re-earn `DR1` through `DR4`, including canonical
formation, exact restoration/cache removal, non-experiment-authored
progression, canonical relation-dependent conservative transport, a subsequent
native feedback cycle, byte-identical disabled baseline, and provider mismatch
refusal. It cannot inherit producer `DR4`. RCAE admission remains blocked until
`DR5` and a reusable provider contract.

## C.1 Revision Lineage

C.2 consumes corrected C.1 output digest
`2853511bbb0e8604e69b5b1b805c6e49f22eb8b6b17d1630f669064adae3015e`.
An earlier reviewed, non-repository artifact was identified by digest prefix
`33e77c892977`. It is recorded only as lineage and is not consumed. Corrections
separated reduced projection from complete native state, retained causal
history from eliminated independent `S`, fixture scope from generality,
classification from fresh execution, and normalized control meanings. The
provisional C.1 ceiling did not change; scope, authority, and debt became more
precise.

## Control Status

```text
control_plan_complete = true
relation_controls_executed = true
producer_transport_controls_executed = true
native_runtime_controls_executed = false
packetization_invariance = not_run
direct_mediation_controls = not_run
multi_cycle_stability_controls = not_run
topology_lifecycle_controls = not_run
cache_pruning_controls = not_run
```

`control_plan_complete` means the required control surface is declared. It does
not mean every runtime control has executed.

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
