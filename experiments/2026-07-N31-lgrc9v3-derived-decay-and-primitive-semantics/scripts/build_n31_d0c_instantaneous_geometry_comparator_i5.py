#!/usr/bin/env python3
"""Build N31 Iteration 5 D0c instantaneous-geometry comparator artifacts."""

from __future__ import annotations

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
    lgrc9v3_restoration_identity_v1,
)


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
I2_OUTPUT = EXPERIMENT / "outputs" / "n31_semantic_representation_control_schema_i2.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n31_active_nulls_and_failure_baselines_i3.json"
I3R1_OUTPUT = EXPERIMENT / "outputs" / "n31_i3_revision_lineage_r1.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n31_d0a_representation_gate_i4.json"
I4R1_OUTPUT = EXPERIMENT / "outputs" / "n31_i4_revision_lineage_r1.json"
TRACE = EXPERIMENT / "outputs" / "n31_i5_d0c_source_current_trace.json"
OUTPUT = EXPERIMENT / "outputs" / "n31_d0c_instantaneous_geometry_comparator_i5.json"
REPORT = EXPERIMENT / "reports" / "n31_d0c_instantaneous_geometry_comparator_i5.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_d0c_instantaneous_geometry_comparator_i5.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"
I5_GOVERNANCE_BASE_REVISION = "a5fcdd67ed49a5a1e11456dd4d7fb4a5e32ba95b"
PROTECTED_RUNTIME_BASE_REVISION = I5_GOVERNANCE_BASE_REVISION
I2_OUTPUT_DIGEST = "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf"
I2_ARTIFACT_SHA256 = "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6"
I3_OUTPUT_DIGEST = "e95b230d76113691d71282e227c61da15a5a1f7d5fa89c194af26ae4d653ddea"
I3_ARTIFACT_SHA256 = "b41d43e6b0a0e411b488ce7a9692ccd9183b9a023da4d479cd2f531e3de026ff"
I3R1_OUTPUT_DIGEST = "b6f6c1948f723d5fbb6008348b804b778993718da18c4b7efb3a499a8757de64"
I3R1_ARTIFACT_SHA256 = "2ac6582625b0898fd799c545de385a757925226eae4d38803d903549e2133398"
I4_OUTPUT_DIGEST = "b7b6f34e3978ec4a410a77e36bc1b548f1baf96dbda7987803d544fc737c3597"
I4_ARTIFACT_SHA256 = "eab3b993ad9990c2a7ba47e2445f62b520e003d9c938bc9cbc9590e428dd3782"
I4_PRIOR_OUTPUT_DIGEST = "0c23bd575fdaf139badf589bb796244961d12456eec0a52460523a6012e22f8e"
I4_PRIOR_ARTIFACT_SHA256 = "358d425674dbca3fa96ccf1cade0da7ce8afe81e537b8cc40bdf35b5f6a8bc49"

ROUTE_SUPPORT = (0, 1, 2)
ANCHOR_NODE_ID = 2
PACKET_AMOUNT = 0.1
DEPARTURE_TIME = 0.0
ARRIVAL_TIME = 1.0
THRESHOLDS = {
    "threshold_record_id": "n31_i5_d0c_thresholds_v1",
    "declared_before_runtime_execution": True,
    "forming_packet_current_l1_minimum": 0.25,
    "post_withdrawal_packet_current_l1_maximum": 1e-12,
    "route_mass_tolerance": 1e-12,
    "coherence_coordinate_tolerance": 1e-12,
    "closed_system_budget_tolerance": 1e-12,
    "static_edge_flux_l1_maximum": 1e-12,
    "positive_D0c_requires": (
        "source-current packet-current component above minimum during transit and "
        "at or below maximum at the first native post-arrival checkpoint"
    ),
}

I4_NORMALIZED_SCIENTIFIC_OUTCOME = {
    "D0a_representation_status": "represented_by_exact_projection",
    "standalone_carrier_lane": "spatial_distribution",
    "spatial_representation_gate_open": True,
    "temporal_representation_gate_open": False,
    "arrival_distribution_representation_gate_open": False,
    "mixed_representation_gate_open": False,
    "identity_roundtrip_exact": True,
    "observed_reconstruction_error": 0.0,
    "positive_evidence_opened": False,
    "decay_relation_ladder_ceiling": "DR0_no_source_current_decay_evidence",
    "n31_progress_ceiling": (
        "N31-C2_active_nulls_and_representation_boundary_established"
    ),
    "ready_for_iteration_5_D0c_comparator": True,
}

BLOCKED_RELABELS = [
    "durable_aftereffect",
    "D0a_persistence",
    "D0a_weakening",
    "causal_decay",
    "causal_mediation",
    "trail_or_stigmergic_field",
    "semantic_memory",
    "learning",
    "communication",
    "agency",
    "selfhood",
    "sentience",
    "organism_or_life",
    "native_support",
    "phase8_completion",
    "unrestricted_autonomy",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
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


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(marker not in text for marker in forbidden)


def git_diff_empty(base: str, path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", base, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def build_i4_revision_lineage(i4: dict[str, Any]) -> dict[str, Any]:
    check_map = {row["check_id"]: row for row in i4["checks"]}
    gate = i4["D0a_representation_gate"]
    current_outcome = {
        "D0a_representation_status": gate["global_status"],
        "standalone_carrier_lane": "spatial_distribution",
        "spatial_representation_gate_open": gate[
            "spatial_D0a_representation_gate_open"
        ],
        "temporal_representation_gate_open": gate[
            "temporal_D0a_representation_gate_open"
        ],
        "arrival_distribution_representation_gate_open": gate[
            "arrival_distribution_D0a_representation_gate_open"
        ],
        "mixed_representation_gate_open": gate[
            "mixed_D0a_representation_gate_open"
        ],
        "identity_roundtrip_exact": check_map[
            "exact_projection_roundtrip_passed"
        ]["passed"],
        "observed_reconstruction_error": i4["exact_projection_contract"][
            "observed_reconstruction_error"
        ],
        "positive_evidence_opened": i4["positive_evidence_opened"],
        "decay_relation_ladder_ceiling": i4["decay_relation_ladder_ceiling"],
        "n31_progress_ceiling": i4["n31_closeout_ceiling"],
        "ready_for_iteration_5_D0c_comparator": i4[
            "ready_for_iteration_5_D0c_comparator"
        ],
    }
    prior_digest = digest_value(I4_NORMALIZED_SCIENTIFIC_OUTCOME)
    current_digest = digest_value(current_outcome)
    checks = [
        check(
            "current_I4_identity_exact",
            i4["output_digest"] == I4_OUTPUT_DIGEST
            and sha256_file(I4_OUTPUT) == I4_ARTIFACT_SHA256,
            i4["output_digest"],
        ),
        check(
            "normalized_scientific_outcome_unchanged",
            current_outcome == I4_NORMALIZED_SCIENTIFIC_OUTCOME
            and current_digest == prior_digest,
            current_digest,
        ),
        check(
            "evidence_and_DR_ceiling_unchanged",
            not i4["positive_evidence_opened"]
            and i4["decay_relation_ladder_ceiling"]
            == "DR0_no_source_current_decay_evidence",
            i4["decay_relation_ladder_ceiling"],
        ),
        check(
            "I5_admission_unchanged",
            i4["ready_for_iteration_5_D0c_comparator"],
            i4["ready_for_iteration_5_D0c_comparator"],
        ),
    ]
    lineage: dict[str, Any] = {
        "experiment": "N31",
        "artifact_kind": "I4_revision_lineage",
        "artifact_schema_version": "n31_i4_revision_lineage_v1",
        "revision_id": "N31-I4R1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_I4R1_provenance_and_scientific_outcome_invariance_closed"
        ),
        "prior_review_package": {
            "label": "N31-I4-pre-review-hardening-package",
            "output_digest": I4_PRIOR_OUTPUT_DIGEST,
            "artifact_sha256": I4_PRIOR_ARTIFACT_SHA256,
            "full_artifact_retained_in_repository": False,
            "identity_source": "external_reviewed_package_identity",
            "consumed_by_I5": False,
        },
        "current_committed_artifact": {
            "label": "N31-I4R1",
            "path": I4_OUTPUT.relative_to(ROOT).as_posix(),
            "commit": I5_GOVERNANCE_BASE_REVISION,
            "output_digest": i4["output_digest"],
            "artifact_sha256": sha256_file(I4_OUTPUT),
            "consumed_by_I5": True,
        },
        "revision_reason": [
            "closed I3-to-I3R1 provenance lineage",
            "made projection coordinate mapping machine-readable",
            "separated spatial organization from boundary transfer",
            "bounded set_state to surgical-clamp representation evidence",
            "froze I7 weakening-order and route-window prerequisites",
            "clarified N31-C2 progress versus terminal closeout assignment",
        ],
        "comparison_policy": {
            "comparison_kind": "normalized_scientific_outcome",
            "why_not_full_artifact_equality": (
                "I4R1 intentionally changes provenance and contract detail while retaining "
                "the reviewed representation conclusion and claim ceiling"
            ),
            "prior_normalized_outcome_source": (
                "reviewed I4 result block and scientific disposition"
            ),
            "prior_normalized_outcome": I4_NORMALIZED_SCIENTIFIC_OUTCOME,
            "current_normalized_outcome": current_outcome,
            "prior_normalized_outcome_digest": prior_digest,
            "current_normalized_outcome_digest": current_digest,
            "scientific_outcome_changed": False,
            "contract_and_provenance_detail_changed": True,
        },
        "checks": checks,
    }
    lineage["failed_checks"] = [
        row["check_id"] for row in checks if not row["passed"]
    ]
    if lineage["failed_checks"]:
        lineage["status"] = "failed"
        lineage["acceptance_state"] = "blocked_I4R1_lineage_not_closed"
    lineage["output_digest"] = digest_value(
        {key: value for key, value in lineage.items() if key != "output_digest"}
    )
    return lineage


def build_model() -> tuple[LGRC9V3, dict[str, int]]:
    graph = PortGraphBackend()
    for label in ("cycle_a", "cycle_b", "cycle_c", "outside_receiver"):
        graph.add_node({"label": label})

    edge_specs = (
        ("cycle_ab", 0, 1, 0, 0, "route_internal"),
        ("cycle_bc", 1, 2, 1, 0, "route_internal"),
        ("cycle_ca", 2, 0, 1, 1, "route_internal"),
        ("route_boundary", 2, 3, 2, 0, "route_boundary"),
    )
    edge_ids: dict[str, int] = {}
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for edge_name, source, target, source_slot, target_slot, kind in edge_specs:
        edge_id = graph.connect_ports(
            source,
            source_slot,
            target,
            target_slot,
            {"kind": kind, "edge_name": edge_name},
        )
        edge_ids[edge_name] = edge_id
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
        flux_coupling[edge_id] = 0.25

    state = GRC9V3State(
        topology=graph,
        nodes={
            0: GRC9V3NodeState(coherence=1.2),
            1: GRC9V3NodeState(coherence=1.0),
            2: GRC9V3NodeState(coherence=0.8),
            3: GRC9V3NodeState(coherence=0.5),
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )
    return LGRC9V3.from_state(state, {"dt": 1.0}), edge_ids


def schedule_forming_cycle(model: LGRC9V3, edge_ids: dict[str, int]) -> None:
    cycle = (
        (0, 1, edge_ids["cycle_ab"]),
        (1, 2, edge_ids["cycle_bc"]),
        (2, 0, edge_ids["cycle_ca"]),
    )
    for index, (source, target, edge_id) in enumerate(cycle):
        model.schedule_packet_departure(
            source_node_id=source,
            target_node_id=target,
            edge_id=edge_id,
            amount=PACKET_AMOUNT,
            departure_event_time_key=DEPARTURE_TIME,
            arrival_event_time_key=ARRIVAL_TIME,
            scheduler_event_index=(2 * index) + 1,
        )


def route_edges(model: LGRC9V3) -> tuple[list[int], list[int]]:
    support = set(ROUTE_SUPPORT)
    internal: list[int] = []
    boundary: list[int] = []
    for edge_id, edge in sorted(model.get_state().base_state.port_edges.items()):
        endpoint_count = int(edge.node_u in support) + int(edge.node_v in support)
        if endpoint_count == 2:
            internal.append(int(edge_id))
        elif endpoint_count == 1:
            boundary.append(int(edge_id))
    return internal, boundary


def checkpoint(
    model: LGRC9V3,
    checkpoint_id: str,
    edge_ids: dict[str, int],
) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    snapshot = model.snapshot()
    identity = lgrc9v3_restoration_identity_v1(snapshot)
    internal_edges, boundary_edges = route_edges(model)
    coherence = {
        str(node_id): float(state.base_state.nodes[node_id].coherence)
        for node_id in ROUTE_SUPPORT
    }
    anchor = coherence[str(ANCHOR_NODE_ID)]
    coherence_coordinates = {
        str(node_id): coherence[str(node_id)] - anchor
        for node_id in ROUTE_SUPPORT
        if node_id != ANCHOR_NODE_ID
    }
    registered_orientation_by_edge = {
        str(edge_ids["cycle_ab"]): {
            "source_node_id": 0,
            "target_node_id": 1,
            "orientation": "registered_cycle_forward_positive",
        },
        str(edge_ids["cycle_bc"]): {
            "source_node_id": 1,
            "target_node_id": 2,
            "orientation": "registered_cycle_forward_positive",
        },
        str(edge_ids["cycle_ca"]): {
            "source_node_id": 2,
            "target_node_id": 0,
            "orientation": "registered_cycle_forward_positive",
        },
    }
    identity_edges = identity["embedded_grc9v3_state"]["state"]["port_edges"]
    native_identity_orientation_by_edge = {
        str(edge_id): {
            "source_node_id": int(identity_edges[str(edge_id)]["node_u"]),
            "target_node_id": int(identity_edges[str(edge_id)]["node_v"]),
            "orientation": "canonical_restoration_identity_node_u_to_node_v_positive",
        }
        for edge_id in internal_edges
    }
    current_registered = {str(edge_id): 0.0 for edge_id in internal_edges}
    current_native_identity = {str(edge_id): 0.0 for edge_id in internal_edges}
    active_packet_ids: list[str] = []
    historical_packet_ids: list[str] = []
    internal_in_flight_mass = 0.0
    support = set(ROUTE_SUPPORT)
    for packet in ledger.packet_records:
        historical_packet_ids.append(packet.packet_id)
        if packet.packet_state != "in_flight":
            continue
        if (
            int(packet.source_node_id) not in support
            or int(packet.target_node_id) not in support
        ):
            continue
        duration = float(packet.arrival_event_time_key) - float(
            packet.departure_event_time_key
        )
        if duration <= 0.0:
            raise ValueError(f"packet {packet.packet_id} has non-positive duration")
        registered = registered_orientation_by_edge[str(packet.edge_id)]
        registered_sign = (
            1.0
            if (
                int(packet.source_node_id) == registered["source_node_id"]
                and int(packet.target_node_id) == registered["target_node_id"]
            )
            else -1.0
        )
        native_identity = native_identity_orientation_by_edge[str(packet.edge_id)]
        native_identity_sign = (
            1.0
            if (
                int(packet.source_node_id) == native_identity["source_node_id"]
                and int(packet.target_node_id) == native_identity["target_node_id"]
            )
            else -1.0
        )
        rate = float(packet.amount) / duration
        current_registered[str(packet.edge_id)] += registered_sign * rate
        current_native_identity[str(packet.edge_id)] += native_identity_sign * rate
        internal_in_flight_mass += float(packet.amount)
        active_packet_ids.append(packet.packet_id)

    route_node_mass = sum(coherence.values())
    route_mass = route_node_mass + internal_in_flight_mass
    packet_current_l1 = sum(abs(value) for value in current_registered.values())
    node_current_divergence = {str(node_id): 0.0 for node_id in ROUTE_SUPPORT}
    native_node_current_divergence = {
        str(node_id): 0.0 for node_id in ROUTE_SUPPORT
    }
    for edge_id, signed_rate in current_registered.items():
        orientation = registered_orientation_by_edge[edge_id]
        source_id = str(orientation["source_node_id"])
        target_id = str(orientation["target_node_id"])
        node_current_divergence[source_id] += signed_rate
        node_current_divergence[target_id] -= signed_rate
    for edge_id, signed_rate in current_native_identity.items():
        orientation = native_identity_orientation_by_edge[edge_id]
        source_id = str(orientation["source_node_id"])
        target_id = str(orientation["target_node_id"])
        native_node_current_divergence[source_id] += signed_rate
        native_node_current_divergence[target_id] -= signed_rate
    static_edge_flux = {
        str(edge_id): float(state.base_state.port_edges[edge_id].flux_uv)
        for edge_id in internal_edges + boundary_edges
    }
    return {
        "checkpoint_id": checkpoint_id,
        "restoration_identity_schema": "lgrc9v3_restoration_identity_v1",
        "restoration_identity_digest": digest_lgrc9v3_restoration_identity_v1(
            snapshot
        ),
        "reset_sensitive_identity_schema": "lgrc9v3_restoration_identity_v2",
        "reset_sensitive_identity_digest": digest_lgrc9v3_restoration_identity_v2(
            snapshot
        ),
        "scientific_state_identity": identity,
        "route_state": {
            "support_node_ids": list(ROUTE_SUPPORT),
            "internal_edge_ids": internal_edges,
            "boundary_edge_ids": boundary_edges,
            "anchor_node_id": ANCHOR_NODE_ID,
            "node_coherence": coherence,
            "coherence_coordinates_node_minus_anchor": coherence_coordinates,
            "route_node_coherence_mass": route_node_mass,
            "internal_in_flight_packet_mass": internal_in_flight_mass,
            "registered_route_mass": route_mass,
            "registered_current_orientation_by_edge": (
                registered_orientation_by_edge
            ),
            "native_identity_current_orientation_by_edge": (
                native_identity_orientation_by_edge
            ),
            "signed_packet_current_by_registered_orientation": current_registered,
            "signed_packet_current_by_native_edge_orientation": (
                current_native_identity
            ),
            "node_current_divergence_outflow_minus_inflow": (
                node_current_divergence
            ),
            "maximum_absolute_node_current_divergence": max(
                (abs(value) for value in node_current_divergence.values()),
                default=0.0,
            ),
            "node_current_divergence_by_native_edge_orientation": (
                native_node_current_divergence
            ),
            "maximum_absolute_native_edge_node_current_divergence": max(
                (abs(value) for value in native_node_current_divergence.values()),
                default=0.0,
            ),
            "packet_current_l1_norm": packet_current_l1,
            "packet_current_units": "coherence_per_event_time",
            "static_native_edge_flux_uv": static_edge_flux,
            "static_native_edge_flux_l1_norm": sum(
                abs(value) for value in static_edge_flux.values()
            ),
        },
        "runtime_state": {
            "active_internal_packet_ids": sorted(active_packet_ids),
            "historical_packet_ids": sorted(historical_packet_ids),
            "in_flight_packet_total": float(ledger.in_flight_packet_total),
            "event_queue_record_count": len(ledger.event_queue_records),
            "packet_record_count": len(ledger.packet_records),
            "node_coherence_total": float(ledger.node_coherence_total),
            "conserved_budget_total": float(ledger.conserved_budget_total),
            "budget_error": float(ledger.budget_error),
        },
    }


def result_event_receipt(results: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_index": result.bookkeeping["checkpoint_index"],
            "event_time_key": result.bookkeeping["event_time_key"],
            "event_kinds": [event.kind for event in result.events],
        }
        for result in results
    ]


def max_coordinate_error(a: dict[str, Any], b: dict[str, Any]) -> float:
    a_values = a["route_state"]["coherence_coordinates_node_minus_anchor"]
    b_values = b["route_state"]["coherence_coordinates_node_minus_anchor"]
    return max(
        (abs(float(a_values[key]) - float(b_values[key])) for key in a_values),
        default=0.0,
    )


def build_trace() -> dict[str, Any]:
    model, edge_ids = build_model()
    baseline = checkpoint(model, "baseline_before_forming_cycle", edge_ids)
    schedule_forming_cycle(model, edge_ids)
    departure_results = model.run_event_queue(max_events=3)
    forming = checkpoint(model, "forming_cycle_packets_in_flight", edge_ids)
    arrival_results = model.run_event_queue(max_events=3)
    post = checkpoint(
        model,
        "first_post_withdrawal_arrival_complete",
        edge_ids,
    )

    forming_current = forming["route_state"]["packet_current_l1_norm"]
    post_current = post["route_state"]["packet_current_l1_norm"]
    mass_error = abs(
        float(forming["route_state"]["registered_route_mass"])
        - float(post["route_state"]["registered_route_mass"])
    )
    coordinate_error = max_coordinate_error(forming, post)
    baseline_return_error = max_coordinate_error(baseline, post)
    budget_values = [
        float(row["runtime_state"]["conserved_budget_total"])
        for row in (baseline, forming, post)
    ]
    budget_span = max(budget_values) - min(budget_values)
    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "5",
        "artifact_kind": "D0c_source_current_runtime_trace",
        "artifact_schema_version": "n31_i5_d0c_source_current_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_native_packet_cycle_D0c_source_current_trace_no_persistence"
        ),
        "derived_report_only": False,
        "source_current_runtime_artifact": True,
        "threshold_declaration": THRESHOLDS,
        "threshold_declaration_digest": digest_value(THRESHOLDS),
        "fixture_contract": {
            "fixture_id": "n31_i5_three_node_balanced_native_packet_cycle_v1",
            "registered_route_support": list(ROUTE_SUPPORT),
            "anchor_node_id": ANCHOR_NODE_ID,
            "cycle_edge_ids": [
                edge_ids["cycle_ab"],
                edge_ids["cycle_bc"],
                edge_ids["cycle_ca"],
            ],
            "boundary_edge_ids": [edge_ids["route_boundary"]],
            "forming_packets": [
                {
                    "source_node_id": 0,
                    "target_node_id": 1,
                    "edge_id": edge_ids["cycle_ab"],
                    "amount": PACKET_AMOUNT,
                },
                {
                    "source_node_id": 1,
                    "target_node_id": 2,
                    "edge_id": edge_ids["cycle_bc"],
                    "amount": PACKET_AMOUNT,
                },
                {
                    "source_node_id": 2,
                    "target_node_id": 0,
                    "edge_id": edge_ids["cycle_ca"],
                    "amount": PACKET_AMOUNT,
                },
            ],
            "forming_schedule_owner": "experiment_fixture_pre_formation_only",
            "formation_input_stop_condition": (
                "all_three_predeclared_departure_inputs_processed"
            ),
            "formation_input_stopped": True,
            "formation_input_stop_checkpoint": forming["checkpoint_id"],
            "forming_carrier_exhaustion_condition": (
                "all_three_native_packet_arrivals_committed_and_event_queue_empty"
            ),
            "forming_carrier_exhausted": True,
            "forming_carrier_exhaustion_checkpoint": post["checkpoint_id"],
            "active_forming_carrier_interval": {
                "start_event_time_key": DEPARTURE_TIME,
                "end_event_time_key": ARRIVAL_TIME,
                "classification": "continued_propagation_of_forming_packets",
                "post_formation_persistence_window": False,
            },
            "post_formation_producer_calls": [],
            "set_state_used": False,
            "hidden_current_cancellation_used": False,
            "static_edge_flux_uv_set_to_zero": True,
        },
        "runtime_execution": {
            "model_family": "LGRC9V3",
            "public_operations": [
                "LGRC9V3.from_state",
                "LGRC9V3.schedule_packet_departure",
                "LGRC9V3.run_event_queue",
                "LGRC9V3.get_state",
                "LGRC9V3.snapshot",
                "lgrc9v3_restoration_identity_v1",
            ],
            "departure_event_receipts": result_event_receipt(departure_results),
            "arrival_event_receipts": result_event_receipt(arrival_results),
            "departure_result_count": len(departure_results),
            "arrival_result_count": len(arrival_results),
            "wall_clock_used_as_causal_input": False,
        },
        "checkpoints": [baseline, forming, post],
        "D0c_relation": {
            "equation_or_relation_id": "n31_i5_D0c_packet_current_geometry_v1",
            "definition": (
                "G_D0c(t) = (anchor-relative route C coordinates, oriented in-flight "
                "packet amount divided by native event-time transit duration); signed "
                "currents are retained in registered-route and canonical native-edge "
                "orientations"
            ),
            "authority": "exact_derived_projection_from_current_native_LGRC9V3_state",
            "projection_persisted_as_state": False,
            "projection_fed_back_into_transport": False,
            "forming_packet_current_l1_norm": forming_current,
            "post_withdrawal_packet_current_l1_norm": post_current,
            "current_component_formed": (
                forming_current
                >= THRESHOLDS["forming_packet_current_l1_minimum"]
            ),
            "current_component_absent_first_post_checkpoint": (
                post_current
                <= THRESHOLDS["post_withdrawal_packet_current_l1_maximum"]
            ),
            "route_mass_error_forming_to_post": mass_error,
            "coherence_coordinate_error_forming_to_post": coordinate_error,
            "coherence_coordinate_error_baseline_to_post": baseline_return_error,
            "closed_system_budget_span": budget_span,
            "historical_packet_records_remain_post_withdrawal": bool(
                post["runtime_state"]["historical_packet_ids"]
            ),
            "historical_records_used_as_current": False,
            "persistence_supported": False,
            "weakening_supported": False,
            "causal_mediation_supported": False,
        },
    }
    relation = trace["D0c_relation"]
    trace["checks"] = [
        check(
            "three_native_departures_processed",
            len(departure_results) == 3
            and all(
                [event.kind for event in result.events]
                == ["lgrc9v3_packet_departure"]
                for result in departure_results
            ),
            len(departure_results),
        ),
        check(
            "three_native_arrivals_processed",
            len(arrival_results) == 3
            and all(
                "lgrc9v3_packet_arrival" in [event.kind for event in result.events]
                for result in arrival_results
            ),
            len(arrival_results),
        ),
        check(
            "forming_current_component_source_current",
            relation["current_component_formed"]
            and len(forming["runtime_state"]["active_internal_packet_ids"]) == 3,
            forming_current,
        ),
        check(
            "current_component_absent_after_native_exhaustion",
            relation["current_component_absent_first_post_checkpoint"]
            and post["runtime_state"]["event_queue_record_count"] == 0
            and post["runtime_state"]["in_flight_packet_total"] == 0.0,
            post_current,
        ),
        check(
            "route_mass_constant",
            mass_error <= THRESHOLDS["route_mass_tolerance"],
            mass_error,
        ),
        check(
            "coherence_coordinates_return_and_remain_matched",
            coordinate_error <= THRESHOLDS["coherence_coordinate_tolerance"]
            and baseline_return_error
            <= THRESHOLDS["coherence_coordinate_tolerance"],
            {
                "forming_to_post": coordinate_error,
                "baseline_to_post": baseline_return_error,
            },
        ),
        check(
            "closed_system_budget_constant",
            budget_span <= THRESHOLDS["closed_system_budget_tolerance"]
            and all(
                float(row["runtime_state"]["budget_error"])
                <= THRESHOLDS["closed_system_budget_tolerance"]
                for row in (baseline, forming, post)
            ),
            budget_span,
        ),
        check(
            "static_edge_flux_not_confounding_packet_current",
            all(
                float(row["route_state"]["static_native_edge_flux_l1_norm"])
                <= THRESHOLDS["static_edge_flux_l1_maximum"]
                for row in (baseline, forming, post)
            ),
            "all registered static edge flux values are zero",
        ),
        check(
            "orientation_contract_and_balanced_divergence_exact",
            forming["route_state"][
                "signed_packet_current_by_registered_orientation"
            ]
            == {"0": 0.1, "1": 0.1, "2": 0.1}
            and forming["route_state"][
                "signed_packet_current_by_native_edge_orientation"
            ]
            == {"0": 0.1, "1": 0.1, "2": -0.1}
            and forming["route_state"][
                "maximum_absolute_node_current_divergence"
            ]
            <= THRESHOLDS["closed_system_budget_tolerance"]
            and forming["route_state"][
                "maximum_absolute_native_edge_node_current_divergence"
            ]
            <= THRESHOLDS["closed_system_budget_tolerance"],
            {
                "registered": forming["route_state"][
                    "signed_packet_current_by_registered_orientation"
                ],
                "native_edge": forming["route_state"][
                    "signed_packet_current_by_native_edge_orientation"
                ],
                "node_divergence": forming["route_state"][
                    "node_current_divergence_outflow_minus_inflow"
                ],
                "native_edge_node_divergence": forming["route_state"][
                    "node_current_divergence_by_native_edge_orientation"
                ],
            },
        ),
        check(
            "history_not_relabelled_as_current",
            relation["historical_packet_records_remain_post_withdrawal"]
            and not relation["historical_records_used_as_current"]
            and post_current == 0.0,
            post["runtime_state"]["historical_packet_ids"],
        ),
        check(
            "D0c_semantic_ceiling_preserved",
            not relation["persistence_supported"]
            and not relation["weakening_supported"]
            and not relation["causal_mediation_supported"],
            "DR1",
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_D0c_runtime_trace_validation_failed"
    trace["output_digest"] = digest_value(
        {key: value for key, value in trace.items() if key != "output_digest"}
    )
    return trace


def na(reason: str) -> dict[str, Any]:
    return {"status": "not_applicable", "scope_reason": reason}


def build_candidate(
    trace: dict[str, Any],
    required_fields: list[str],
    i3: dict[str, Any],
) -> dict[str, Any]:
    baseline, forming, post = trace["checkpoints"]
    relation = trace["D0c_relation"]
    trace_path = TRACE.relative_to(ROOT).as_posix()
    mass_before = float(forming["route_state"]["registered_route_mass"])
    mass_after = float(post["route_state"]["registered_route_mass"])
    mass_delta = mass_after - mass_before
    net_outward_boundary_flux = 0.0
    continuity_residual = mass_delta + net_outward_boundary_flux
    candidate_semantic_contract = {
        "primary_semantic_class": "D0c",
        "representation_or_authority_class": "exact_derived_projection",
        "organization_domain": "functional_coupling",
        "load_bearing_organization_domain": "functional_coupling",
        "candidate_specific_schema_id": "n31_i5_D0c_candidate_schema_v1",
        "carrier_contract_id": "n31_i5_packet_current_carrier_v1",
        "continuation_state_contract_id": (
            "n31_i5_complete_LGRC9V3_current_state_v1"
        ),
        "internal_time_policy": "model_owned_event_time_wall_clock_excluded_v1",
    }
    candidate_semantic_contract_digest = digest_value(candidate_semantic_contract)
    i3_rows = {row["control_id"]: row for row in i3["active_null_rows"]}
    control_results = [
        {
            "control_id": "label_only_decay",
            "control_status": "passed",
            "blocked_condition": "label_or_report_without_source_current_relation",
            "expected_result": "source_current_trace_required",
            "actual_result": "native_packet_current_trace_and_full_identities_present",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks_DR1_plus",
            "scope_reason_if_not_applicable": None,
        },
        {
            "control_id": "forming_activity_never_stopped",
            "control_status": "passed",
            "blocked_condition": "continued_departures_masquerade_as_post_formation",
            "expected_result": "forming_schedule_exhausted",
            "actual_result": "all_packets_arrived_queue_empty_no_post_calls",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks_post_formation_language",
            "scope_reason_if_not_applicable": None,
        },
        {
            "control_id": "instantaneous_geometry_as_durable_decay",
            "control_status": "failed_closed",
            "blocked_condition": "D0c_current_component_relabelled_as_durable_decay",
            "expected_result": "durable_claim_rejected_when_current_component_is_zero",
            "actual_result": "first_post_checkpoint_current_component_equals_zero",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "caps_candidate_at_DR1",
            "scope_reason_if_not_applicable": None,
        },
        {
            "control_id": "route_mass_loss_as_organization_weakening_relabel",
            "control_status": "passed",
            "blocked_condition": "mass_change_substitutes_for_geometry_evidence",
            "expected_result": "route_mass_matched",
            "actual_result": "forming_and_post_route_mass_equal",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks_organization_inference",
            "scope_reason_if_not_applicable": None,
        },
        {
            "control_id": "D0c_persistence_retained_as_same_D0c_row",
            "control_status": "not_applicable",
            "blocked_condition": "persistent_D0c_keeps_same_candidate_identity",
            "expected_result": "new_D0a_identity_if_persistence_appears",
            "actual_result": "no_persistence_observed",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks_in_place_semantic_upgrade",
            "scope_reason_if_not_applicable": "no_persistent_relation_exists_in_I5",
        },
        {
            "control_id": "post_withdrawal_history_as_current_candidate_specific",
            "control_status": "failed_closed",
            "blocked_condition": "arrived_packet_history_counted_as_active_current",
            "expected_result": "only_in_flight_records_contribute_to_packet_current",
            "actual_result": "history_present_but_projected_current_is_zero",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks_false_D0c_persistence",
            "scope_reason_if_not_applicable": None,
        },
    ]
    comparability_fields = list(candidate_semantic_contract)
    for result in control_results:
        source_control_id = result["control_id"]
        source_row = i3_rows.get(source_control_id)
        result["candidate_control_execution_id"] = (
            f"n31_i5_regenerated_{source_control_id}_v1"
        )
        result["control_execution_artifact"] = trace_path
        result["control_execution_checkpoints"] = [
            forming["checkpoint_id"],
            post["checkpoint_id"],
        ]
        result["candidate_semantic_contract_digest"] = (
            candidate_semantic_contract_digest
        )
        if source_row is None:
            result["control_origin"] = "candidate_specific_no_I3_source_control"
            result["source_I3_control_id"] = None
            result["source_I3_row_digest"] = None
            result["matched_to_I3_null"] = False
            result["regenerated_for_I5_candidate"] = True
            result["semantic_comparability_mismatches"] = [
                "no_frozen_I3_control_identity"
            ]
            result["semantic_comparability_digest"] = digest_value(
                {
                    "source_I3_contract": None,
                    "candidate_contract": candidate_semantic_contract,
                }
            )
            continue
        source_contract = {
            field: source_row.get(field) for field in comparability_fields
        }
        mismatches = [
            field
            for field in comparability_fields
            if source_contract[field] != candidate_semantic_contract[field]
        ]
        result["control_origin"] = "regenerated_candidate_specific"
        result["source_I3_control_id"] = source_control_id
        result["source_I3_row_digest"] = source_row["row_digest"]
        result["matched_to_I3_null"] = not mismatches
        result["regenerated_for_I5_candidate"] = True
        result["semantic_comparability_mismatches"] = mismatches
        result["semantic_comparability_digest"] = digest_value(
            {
                "source_I3_contract": source_contract,
                "candidate_contract": candidate_semantic_contract,
            }
        )
    route_mass_contract = {
        "route_mass_contract_id": "n31_i5_balanced_cycle_route_mass_v1",
        "registered_route_support": list(ROUTE_SUPPORT),
        "registered_route_boundary": forming["route_state"]["boundary_edge_ids"],
        "metric_measure_and_boundary_convention": (
            "node coherence plus internal in-flight packet coherence; boundary edge 3; "
            "outward positive"
        ),
        "post_formation_integration_window": {
            "status": "not_applicable",
            "scope_reason": (
                "event_time_0_to_1_is_the_active_forming_carrier_interval_not_a_"
                "post_formation_persistence_window"
            ),
        },
        "active_forming_carrier_interval": trace["fixture_contract"][
            "active_forming_carrier_interval"
        ],
        "flux_quantity_semantics": "time_integrated_exported_coherence",
        "boundary_measure": "registered boundary edge crossings",
        "mass_before": mass_before,
        "mass_after": mass_after,
        "mass_delta": mass_delta,
        "boundary_flux_sign_policy": "positive_outward",
        "net_outward_boundary_flux": net_outward_boundary_flux,
        "in_flight_boundary_treatment": (
            "internal in-flight packets counted once; no packet crosses boundary"
        ),
        "boundary_crossing_count_policy": "each_packet_or_flux_transfer_counted_exactly_once",
        "departure_arrival_accounting_policy": (
            "internal departure debits node and adds in-flight amount; internal arrival "
            "removes in-flight amount and credits node"
        ),
        "receiver_inside_or_outside_support": "all_cycle_receivers_inside_support",
        "moving_support_or_measure_correction": "not_applicable_fixed_support",
        "continuity_tolerance": THRESHOLDS["route_mass_tolerance"],
        "continuity_residual": continuity_residual,
        "continuity_closed": (
            abs(continuity_residual) <= THRESHOLDS["route_mass_tolerance"]
        ),
    }
    route_organization_contract = {
        "route_organization_contract_id": "n31_i5_D0c_geometry_contract_v1",
        "organization_observable_id": "n31_i5_anchor_C_plus_packet_J_tuple_v1",
        "organization_definition": trace["D0c_relation"]["definition"],
        "organization_inputs": [
            "current route node coherence",
            "current in-flight internal packet records",
            "packet departure and arrival event-time keys",
            "registered route orientation",
            "canonical native restoration-identity edge orientation",
        ],
        "organization_domain": "functional_coupling",
        "observed_diagnostic_domains": [
            "spatial_distribution",
            "functional_coupling",
        ],
        "load_bearing_organization_domain": "functional_coupling",
        "mixed_domain_mediation_resolution": "not_applicable",
        "organization_before": {
            "checkpoint": forming["checkpoint_id"],
            "packet_current_l1_norm": relation[
                "forming_packet_current_l1_norm"
            ],
            "coherence_coordinates": forming["route_state"][
                "coherence_coordinates_node_minus_anchor"
            ],
        },
        "organization_after": {
            "checkpoint": post["checkpoint_id"],
            "packet_current_l1_norm": relation[
                "post_withdrawal_packet_current_l1_norm"
            ],
            "coherence_coordinates": post["route_state"][
                "coherence_coordinates_node_minus_anchor"
            ],
        },
        "organization_weakened": False,
        "instantaneous_current_component_withdrawn": True,
        "organization_authority": "exact_derived_projection",
        "organization_update_owner": "native_LGRC9V3_packet_transport",
        "organization_has_independent_causal_freedom": False,
        "organization_recomputation_status": "passed_exact",
    }
    causal_contract = {
        "causal_mediation_contract_id": "n31_i5_no_causal_mediation_D0c_v1",
        "later_local_readout_definition": "not_run_I5_is_instantaneous_comparator",
        "later_readout_changed": False,
        "organization_intervention_definition": "not_run",
        "mass_matched_during_organization_intervention": False,
        "packet_amount_matched_during_organization_intervention": False,
        "spatial_organization_matched_during_temporal_intervention": False,
        "other_continuation_state_matched": False,
        "temporal_intervention_matching_status": "not_applicable",
        "organization_intervention_valid": False,
        "local_transport_intervention_status": "not_run",
        "direct_readout_path_excluded": True,
        "hidden_selector_excluded": True,
        "added_coincidence_or_resonance_policy_present": False,
        "later_readout_probe_relation": "unresolved",
        "formation_packet_exclusion_status": "not_applicable",
        "organization_mediated_readout_change": False,
        "mediation_strength": "absent",
    }
    candidate: dict[str, Any] = {
        "candidate_id": "n31_i5_D0c_balanced_native_packet_cycle",
        "candidate_schema_version": "n31_decay_candidate_schema_v2",
        "schema_change_record_id": "n31_pre_i1_mass_organization_mediation_normalization_v2",
        "source_iteration": "N31-I5",
        "primary_semantic_class": "D0c",
        "representation_or_authority_class": "exact_derived_projection",
        "candidate_disposition": "supported",
        "d0_subclass": "not_applicable",
        "weakening_mode": "none",
        "weakening_trajectory_class": "transient",
        "formation_source": "native_source_current_packet_cycle",
        "carrier_definition": (
            "current native route C distribution plus in-flight packet current rates"
        ),
        "continuation_state_definition": (
            "complete LGRC9V3 current scientific state under restoration identity v1"
        ),
        "route_local_surface": "registered three-node internal packet cycle",
        "route_mass_contract": route_mass_contract,
        "route_organization_contract": route_organization_contract,
        "causal_mediation_contract": causal_contract,
        "route_mass_decreased": False,
        "route_organization_weakened": False,
        "later_readout_changed": False,
        "organization_mediated_readout_change": False,
        "ordinary_post_formation_flux_generated": False,
        "added_export_policy_present": False,
        "export_policy_owner": "not_applicable_no_export",
        "export_policy_inputs": [],
        "producer_authors_aftereffect": False,
        "d0_to_br_bridge_status": "not_tested",
        "added_mechanism_admission_reason": "not_applicable_D0c_native_comparator",
        "post_formation_producer_call_policy": "no_calls",
        "post_formation_producer_calls": [],
        "post_formation_state_mutating_producer_calls": [],
        "producer_call_audit_status": "complete_no_mutation",
        "topology_contract_id": "n31_i5_three_node_cycle_plus_boundary_v1",
        "internal_time_owner": "native_LGRC9V3_event_queue",
        "internal_time_advance_event": "lgrc9v3_packet_arrival",
        "update_phase": "native_packet_transit_then_immediate_arrival_completion",
        "equation_or_relation_id": "n31_i5_D0c_packet_current_geometry_v1",
        "units_by_state": {
            "node_coherence": "coherence",
            "route_mass": "coherence",
            "packet_current": "coherence_per_event_time",
            "event_time": "native_event_time_key",
        },
        "invariant_id": "closed_system_node_plus_in_flight_coherence",
        "coherence_budget_before": baseline["runtime_state"][
            "conserved_budget_total"
        ],
        "coherence_budget_after": post["runtime_state"][
            "conserved_budget_total"
        ],
        "invariant_tolerance": THRESHOLDS["closed_system_budget_tolerance"],
        "forming_activity_present": True,
        "forming_activity_stopped": True,
        "formation_input_stopped": True,
        "formation_input_stop_checkpoint": forming["checkpoint_id"],
        "forming_carrier_exhausted": True,
        "forming_carrier_exhaustion_checkpoint": post["checkpoint_id"],
        "active_forming_carrier_interval": trace["fixture_contract"][
            "active_forming_carrier_interval"
        ],
        "post_formation_window": (
            "single_first_checkpoint_after_forming_carrier_exhaustion_no_persistence_window"
        ),
        "formation_trace": {
            "artifact_path": trace_path,
            "checkpoint_id": forming["checkpoint_id"],
        },
        "persistence_trace": {
            "artifact_path": trace_path,
            "result": "current_component_zero_at_first_post_checkpoint",
            "persistence_supported": False,
        },
        "weakening_trace": na("no_persistent_relation_exists_to_weaken"),
        "local_readout_trace": na("I5_is_instantaneous_comparator_not_mediation_probe"),
        "mediator_intervention_trace": na("I5_does_not_test_causal_mediation"),
        "destination_trace_if_mass_moves": na("route_mass_does_not_move_across_boundary"),
        "complete_state_identity": {
            "baseline": baseline["restoration_identity_digest"],
            "forming": forming["restoration_identity_digest"],
            "post_withdrawal": post["restoration_identity_digest"],
        },
        "restoration_identity_schema": "lgrc9v3_restoration_identity_v1",
        "snapshot_load_status": "not_run_pending_iteration_8",
        "reset_status": "not_applicable_no_reset_sensitive_operation",
        "branch_continuation_status": "not_run_pending_iteration_8",
        "derived_cache_status": "not_persisted_exact_projection",
        "derived_cache_recomputation_status": "passed_exact",
        "execution_reconstruction_status": "not_run_pending_iteration_8",
        "producer_roles": ["experiment_fixture_pre_formation_packet_schedule_only"],
        "producer_residue": [
            "the forming packet cycle is experiment-scheduled input; no producer acts after formation"
        ],
        "naturalization_debt": [
            "autonomous native formation of the same packet cycle is not claimed",
            "persistence weakening and causal mediation remain untested",
        ],
        "source_current_inputs": [
            "LGRC9V3RuntimeState.base_state.nodes[*].coherence",
            "LGRC9V3RuntimeState.packet_ledger.packet_records",
            "LGRC9V3RuntimeState.packet_ledger.event_queue_records",
            "LGRC9V3RuntimeState.base_state.port_edges[*]",
        ],
        "artifact_manifest": [
            {
                "path": trace_path,
                "sha256": sha256_file(TRACE),
                "artifact_role": "source_current_D0c_runtime_trace",
            }
        ],
        "artifact_sha256": sha256_file(TRACE),
        "all_artifact_sha256_match_file_contents": True,
        "row_specific_thresholds_declared_before_use": THRESHOLDS,
        "decay_relation_ladder_rung": "DR1",
        "row_decision": "supported",
        "claim_ceiling": (
            "source_current_instantaneous_state_flux_geometry_comparator_no_persistence"
        ),
        "blocked_relabels": BLOCKED_RELABELS,
        "unsafe_claim_flags": {
            f"{claim}_claim_allowed": False for claim in BLOCKED_RELABELS
        },
        "control_results": control_results,
        "candidate_semantic_contract": candidate_semantic_contract,
        "candidate_semantic_contract_digest": candidate_semantic_contract_digest,
        "direct_I3_null_consumption_count": sum(
            bool(row["matched_to_I3_null"]) for row in control_results
        ),
        "candidate_specific_control_regeneration_count": sum(
            bool(row["regenerated_for_I5_candidate"]) for row in control_results
        ),
    }
    candidate["missing_required_fields"] = sorted(
        set(required_fields) - set(candidate)
    )
    candidate["row_digest"] = digest_value(
        {key: value for key, value in candidate.items() if key != "row_digest"}
    )
    return candidate


def build_payload(
    trace: dict[str, Any], i4r1: dict[str, Any]
) -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i3r1 = load_json(I3R1_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    required_fields = i2["schema"]["candidate_row_schema"]["required_fields"]
    candidate = build_candidate(trace, required_fields, i3)
    protected_paths_clean = all(
        git_diff_empty(PROTECTED_RUNTIME_BASE_REVISION, path)
        for path in ("src", "specs", "tests")
    )
    checks = [
        check(
            "I2_source_chain_exact",
            i2["output_digest"] == I2_OUTPUT_DIGEST
            and sha256_file(I2_OUTPUT) == I2_ARTIFACT_SHA256,
            i2["output_digest"],
        ),
        check(
            "I3R1_source_chain_exact",
            i3["output_digest"] == I3_OUTPUT_DIGEST
            and sha256_file(I3_OUTPUT) == I3_ARTIFACT_SHA256
            and i3r1["output_digest"] == I3R1_OUTPUT_DIGEST
            and sha256_file(I3R1_OUTPUT) == I3R1_ARTIFACT_SHA256,
            i3r1["revision_id"],
        ),
        check(
            "I4_handoff_exact_and_I5_ready",
            i4["output_digest"] == I4_OUTPUT_DIGEST
            and sha256_file(I4_OUTPUT) == I4_ARTIFACT_SHA256
            and i4["ready_for_iteration_5_D0c_comparator"],
            i4["output_digest"],
        ),
        check(
            "I4R1_revision_lineage_closed",
            i4r1["status"] == "passed"
            and not i4r1["failed_checks"]
            and i4r1["current_committed_artifact"]["consumed_by_I5"]
            and not i4r1["comparison_policy"]["scientific_outcome_changed"],
            i4r1["revision_id"],
        ),
        check(
            "runtime_trace_passed",
            trace["status"] == "passed" and not trace["failed_checks"],
            trace["output_digest"],
        ),
        check(
            "candidate_schema_complete",
            not candidate["missing_required_fields"],
            candidate["missing_required_fields"],
        ),
        check(
            "source_current_D0c_relation_formed",
            trace["D0c_relation"]["current_component_formed"]
            and candidate["primary_semantic_class"] == "D0c"
            and candidate["decay_relation_ladder_rung"] == "DR1",
            trace["D0c_relation"]["forming_packet_current_l1_norm"],
        ),
        check(
            "instantaneous_component_absent_after_withdrawal",
            trace["D0c_relation"][
                "current_component_absent_first_post_checkpoint"
            ]
            and not trace["D0c_relation"]["persistence_supported"],
            trace["D0c_relation"]["post_withdrawal_packet_current_l1_norm"],
        ),
        check(
            "mass_and_budget_invariants_pass",
            candidate["route_mass_contract"]["continuity_closed"]
            and candidate["coherence_budget_before"]
            == candidate["coherence_budget_after"],
            candidate["route_mass_contract"]["continuity_residual"],
        ),
        check(
            "no_post_formation_producer_authorship",
            not candidate["post_formation_producer_calls"]
            and not candidate["post_formation_state_mutating_producer_calls"]
            and not candidate["producer_authors_aftereffect"],
            candidate["producer_call_audit_status"],
        ),
        check(
            "instantaneous_as_durable_control_failed_closed",
            any(
                row["source_I3_control_id"]
                == "instantaneous_geometry_as_durable_decay"
                and row["control_status"] == "failed_closed"
                for row in candidate["control_results"]
            ),
            "DR1 ceiling",
        ),
        check(
            "candidate_specific_controls_regenerated",
            candidate["direct_I3_null_consumption_count"] == 0
            and candidate["candidate_specific_control_regeneration_count"]
            == len(candidate["control_results"])
            and all(
                row["control_execution_artifact"]
                == TRACE.relative_to(ROOT).as_posix()
                for row in candidate["control_results"]
            ),
            {
                "direct_I3": candidate["direct_I3_null_consumption_count"],
                "regenerated": candidate[
                    "candidate_specific_control_regeneration_count"
                ],
            },
        ),
        check(
            "current_orientation_and_divergence_contract_passed",
            any(
                row["check_id"]
                == "orientation_contract_and_balanced_divergence_exact"
                and row["passed"]
                for row in trace["checks"]
            ),
            "registered and native orientation vectors retained",
        ),
        check(
            "formation_input_and_carrier_exhaustion_separate",
            candidate["formation_input_stopped"]
            and candidate["forming_carrier_exhausted"]
            and candidate["formation_input_stop_checkpoint"]
            != candidate["forming_carrier_exhaustion_checkpoint"]
            and not candidate["active_forming_carrier_interval"][
                "post_formation_persistence_window"
            ],
            candidate["active_forming_carrier_interval"],
        ),
        check(
            "artifact_manifest_exact",
            all(
                sha256_file(ROOT / row["path"]) == row["sha256"]
                for row in candidate["artifact_manifest"]
            ),
            candidate["artifact_manifest"],
        ),
        check(
            "positive_decay_claims_remain_closed",
            candidate["candidate_disposition"] == "supported"
            and candidate["row_decision"] == "supported"
            and not candidate["route_organization_weakened"]
            and not candidate["organization_mediated_readout_change"]
            and all(not value for value in candidate["unsafe_claim_flags"].values()),
            candidate["claim_ceiling"],
        ),
        check(
            "protected_runtime_contract_diff_empty",
            protected_paths_clean,
            protected_paths_clean,
        ),
    ]
    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "5",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_source_current_D0c_DR1_instantaneous_geometry_comparator_"
            "no_persistence_no_decay"
        ),
        "source_chain": {
            "I2": {
                "path": I2_OUTPUT.relative_to(ROOT).as_posix(),
                "output_digest": i2["output_digest"],
                "artifact_sha256": sha256_file(I2_OUTPUT),
            },
            "I3R1": {
                "I3_path": I3_OUTPUT.relative_to(ROOT).as_posix(),
                "I3_output_digest": i3["output_digest"],
                "I3_artifact_sha256": sha256_file(I3_OUTPUT),
                "lineage_path": I3R1_OUTPUT.relative_to(ROOT).as_posix(),
                "lineage_output_digest": i3r1["output_digest"],
                "lineage_artifact_sha256": sha256_file(I3R1_OUTPUT),
            },
            "I4": {
                "path": I4_OUTPUT.relative_to(ROOT).as_posix(),
                "output_digest": i4["output_digest"],
                "artifact_sha256": sha256_file(I4_OUTPUT),
                "revision_id": i4r1["revision_id"],
                "revision_lineage_path": I4R1_OUTPUT.relative_to(ROOT).as_posix(),
                "revision_lineage_output_digest": i4r1["output_digest"],
                "revision_lineage_artifact_sha256": sha256_file(I4R1_OUTPUT),
                "consumed_as": "D0_representation_and_I5_admission_boundary",
            },
        },
        "graph_scope": {
            "I5_governance_base_revision": I5_GOVERNANCE_BASE_REVISION,
            "src_diff_empty": git_diff_empty(PROTECTED_RUNTIME_BASE_REVISION, "src"),
            "protected_runtime_contract_diff_empty": protected_paths_clean,
            "runtime_modified": False,
        },
        "threshold_declaration": THRESHOLDS,
        "threshold_declaration_digest": digest_value(THRESHOLDS),
        "source_current_trace": {
            "path": TRACE.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(TRACE),
            "output_digest": trace["output_digest"],
            "artifact_role": "source_current_D0c_runtime_trace",
        },
        "artifact_manifest": [
            {
                "path": I4R1_OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(I4R1_OUTPUT),
                "artifact_role": "I4R1_provenance_and_scientific_outcome_lineage",
            },
            {
                "path": TRACE.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(TRACE),
                "artifact_role": "source_current_D0c_runtime_trace",
            },
        ],
        "candidate_rows": [candidate],
        "candidate_row_count": 1,
        "source_current_D0c_candidate_supported": True,
        "positive_evidence_opened": True,
        "positive_evidence_scope": "source_current_D0c_instantaneous_comparator_only",
        "positive_decay_evidence_opened": False,
        "D0a_persistence_supported": False,
        "D0a_weakening_supported": False,
        "causal_mediation_supported": False,
        "candidate_rows_classified": True,
        "decay_relation_ladder_rung_assigned": True,
        "decay_relation_ladder_rung": "DR1",
        "decay_relation_ladder_ceiling": "DR1_attributable_route_local_relation_formed",
        "n31_progress_rung_assigned": True,
        "n31_progress_rung": (
            "N31-C2_active_nulls_and_representation_boundary_established"
        ),
        "n31_closeout_ceiling": (
            "N31-C2_active_nulls_and_representation_boundary_established"
        ),
        "n31_closeout_ladder_rung_assigned": False,
        "n31_c3_D0c_classification_component_satisfied": True,
        "n31_c3_overall_pending_D0b_and_D0a_classification": True,
        "ready_for_iteration_6_D0b_finite_window_relation": True,
        "ready_for_iteration_7_spatial_D0a_probe": i4[
            "ready_for_iteration_7_spatial_D0a_probe"
        ],
        "claim_boundary": {
            "claim_ceiling": (
                "source_current_D0c_instantaneous_state_flux_geometry_comparator_DR1"
            ),
            "blocked_relabels": BLOCKED_RELABELS,
            "unsafe_claim_flags": {
                f"{claim}_claim_allowed": False for claim in BLOCKED_RELABELS
            },
        },
        "checks": checks,
    }
    checks.append(
        check("no_absolute_paths_in_records", no_absolute_paths(payload), "recursive")
    )
    payload["failed_checks"] = [
        row["check_id"] for row in checks if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_D0c_comparator_validation_failed"
        payload["source_current_D0c_candidate_supported"] = False
        payload["positive_evidence_opened"] = False
        payload["decay_relation_ladder_rung_assigned"] = False
        payload["ready_for_iteration_6_D0b_finite_window_relation"] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    candidate = payload["candidate_rows"][0]
    trace = load_json(TRACE)
    baseline, forming, post = trace["checkpoints"]
    controls = "\n".join(
        "- `{control}` = `{status}` (`{origin}`): {result}".format(
            control=row["control_id"],
            status=row["control_status"],
            origin=row["control_origin"],
            result=row["actual_result"],
        )
        for row in candidate["control_results"]
    )
    checks = "\n".join(
        f"- `{row['check_id']}` = `{str(row['passed']).lower()}`"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 5 - D0c Instantaneous Geometry Comparator

Status: `{payload['status']}`

Acceptance state: `{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## I4 Revision Lineage

I5 consumes the committed I4 artifact as `N31-I4R1`. The pre-hardening reviewed
package had a different artifact/output identity. The generated lineage retains
both identities and records that I4R1 added provenance, machine projection,
channel-separation, surgical-clamp, and I7-preregistration detail without
changing the scoped exact-representation result, DR0 ceiling, evidence
quarantine, or I5 admission.

```text
I4R1 lineage = {payload['source_chain']['I4']['revision_lineage_path']}
I4R1 lineage digest = {payload['source_chain']['I4']['revision_lineage_output_digest']}
```

## Result

I5 supports one source-current `D0c` comparator at `DR1`:

```text
forming packet-current L1 = {trace['D0c_relation']['forming_packet_current_l1_norm']}
first post-withdrawal packet-current L1 = {trace['D0c_relation']['post_withdrawal_packet_current_l1_norm']}
registered route mass, forming = {forming['route_state']['registered_route_mass']}
registered route mass, post = {post['route_state']['registered_route_mass']}
persistence supported = false
weakening supported = false
causal mediation supported = false
```

This is positive evidence for an instantaneous state/flux geometry relation,
not positive evidence for decay.

## State-Flux Dynamics

The registered route is a three-node cycle. Three equal native LGRC packets
depart simultaneously, one on each oriented internal edge. During transit,
the node-coherence distribution is shifted uniformly, so its anchor-relative
coordinates remain unchanged, while the oriented packet-current cycle is
nonzero. Route mass remains constant because each internal departure is counted
as one in-flight packet amount.

The current signs are stored in two explicit conventions:

```text
registered cycle orientation = {forming['route_state']['signed_packet_current_by_registered_orientation']}
canonical native edge orientation = {forming['route_state']['signed_packet_current_by_native_edge_orientation']}
node divergence (outflow - inflow) = {forming['route_state']['node_current_divergence_outflow_minus_inflow']}
```

Edge `2` is positive in the registered `2 -> 0` cycle direction and negative in
the canonical restoration-identity `0 -> 2` edge direction. Both vectors encode
the same physical transport. The zero node divergence verifies that the cycle
is balanced.

The next three native events are the corresponding arrivals. They restore the
original node-coherence distribution, empty the in-flight ledger and event
queue, and make the exact packet-current projection zero. No `set_state()`,
post-formation producer, static edge-flux cancellation, or hidden label is used.

```text
baseline C coordinates = {baseline['route_state']['coherence_coordinates_node_minus_anchor']}
forming C coordinates = {forming['route_state']['coherence_coordinates_node_minus_anchor']}
post C coordinates = {post['route_state']['coherence_coordinates_node_minus_anchor']}
```

This isolates the instantaneous `J_C` component from route mass and the
spatial `C` coordinates. It is an instantaneous state-flux geometry comparator,
not an induced metric, curvature, Hessian, or geometric transport intervention.
It demonstrates that current-indexed transport geometry can be formed and
removed by native packet transport. Because the selected component
is already zero at the first post-arrival checkpoint, it does not demonstrate a
durable aftereffect or a relation that persists and later weakens.

## Withdrawal Meaning

Two lifecycle boundaries are retained. Formation input stops after the final
predeclared departure is processed. The three packets then remain the active
forming carrier from event time `0` to `1`; this is not a post-formation
persistence window. Carrier exhaustion occurs only after all three arrivals
commit and the queue becomes empty. Historical arrived-packet records remain in
the scientific state, but the exact projection counts only currently in-flight
packets. Those records therefore cannot backfill current or persistence.

## Authority And Residue

The D0c observable is an exact recomputable projection of current LGRC9V3
state. It has no independent causal freedom and is not fed back into transport.
The experiment owns the initial packet schedule, which remains producer residue
for formation. No producer acts after formation. Autonomous native production
of the cycle, persistence, weakening, and mediation remain debt.

## Controls

{controls}

`failed_closed` means the attempted stronger relabel was rejected. In
particular, `instantaneous_geometry_as_durable_decay` fails closed and caps the
row at DR1. Every frozen-I3 control meaning used here is regenerated against
the exact I5 contract (`D0c`, exact-derived authority, functional-coupling
domain, packet-current carrier). None of the generic I3 fixtures is directly
consumed as if it already matched this candidate.

## Classification

```text
primary semantic class = D0c
authority = exact_derived_projection
candidate disposition = supported
DR rung = DR1
N31 progress ceiling = N31-C2
N31-C3 D0c component = satisfied
N31-C3 overall = pending I6/I7 classifications
```

## Checks

{checks}
""",
        encoding="utf-8",
    )


def main() -> None:
    i4r1 = build_i4_revision_lineage(load_json(I4_OUTPUT))
    I4R1_OUTPUT.write_text(canonical_json(i4r1), encoding="utf-8")
    if i4r1["failed_checks"]:
        raise SystemExit(
            "N31 I4R1 lineage failed: " + ", ".join(i4r1["failed_checks"])
        )
    trace = build_trace()
    TRACE.write_text(canonical_json(trace), encoding="utf-8")
    if trace["failed_checks"]:
        raise SystemExit(
            "N31 I5 trace failed: " + ", ".join(trace["failed_checks"])
        )
    payload = build_payload(trace, i4r1)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    if payload["failed_checks"]:
        raise SystemExit(
            "N31 I5 failed: " + ", ".join(payload["failed_checks"])
        )


if __name__ == "__main__":
    main()
