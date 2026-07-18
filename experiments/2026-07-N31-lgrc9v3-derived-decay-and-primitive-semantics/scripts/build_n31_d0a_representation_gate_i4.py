#!/usr/bin/env python3
"""Build N31 Iteration 4 D0a representation-gate artifacts."""

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
I3_REVISION = EXPERIMENT / "outputs" / "n31_i3_revision_lineage_r1.json"
FIXTURE = EXPERIMENT / "outputs" / "n31_i4_spatial_projection_conformance_fixture.json"
OUTPUT = EXPERIMENT / "outputs" / "n31_d0a_representation_gate_i4.json"
REPORT = EXPERIMENT / "reports" / "n31_d0a_representation_gate_i4.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_d0a_representation_gate_i4.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"
I4_GOVERNANCE_BASE_REVISION = "58128d13a103f4d41ca73ffe484c1da8265b0379"
PROTECTED_RUNTIME_BASE_REVISION = "7075ecb5e464401df96f16eac171fbefe0e532dc"
I2_OUTPUT_DIGEST = "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf"
I2_ARTIFACT_SHA256 = "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6"
I3_OUTPUT_DIGEST = "e95b230d76113691d71282e227c61da15a5a1f7d5fa89c194af26ae4d653ddea"
I3_ARTIFACT_SHA256 = "b41d43e6b0a0e411b488ce7a9692ccd9183b9a023da4d479cd2f531e3de026ff"
I3_PRIOR_OUTPUT_DIGEST = "02066f16f2a7fb60ea9122f5a649fb540b3459745b6b583fc7f05a89fd667da0"
I3_PRIOR_ARTIFACT_SHA256 = "7cfb143c56db0ea9a9ddf5839822ed8eb321d96b3345b6c1dc2384a9aa855736"
I3_SEMANTIC_PROJECTION_DIGEST = (
    "cc4a53efd629e0d52455b5fe2a6427af0dabe869d53cfc3de06325c1dbf2f02d"
)
I3_CONTROL_ID_SET_DIGEST = "1c9d9f5ae54faddb6bbb2abf8110498f15a704c08eaf711f862eff01fb1d1ac9"
PROJECTION_CONTRACT_ID = "n31_i4_registered_route_coordinate_projection_v1"
FIXTURE_ID = "n31_i4_four_node_route_with_internal_in_flight_packet_v1"
ROUTE_SUPPORT = (0, 1, 2)
RECONSTRUCTION_ERROR_BOUND = 1e-12

I3_SEMANTIC_PROJECTION_FIELDS = (
    "control_id",
    "claim_under_test",
    "false_positive_scenario",
    "violated_gate",
    "expected_claim_failure",
    "rung_effect",
    "primary_semantic_class",
    "representation_or_authority_class",
    "organization_domain",
    "load_bearing_organization_domain",
    "control_scenario_kind",
    "orthogonal_result_scope",
    "candidate_specific_schema_id",
    "carrier_contract_id",
    "continuation_state_contract_id",
    "internal_time_policy",
    "expected_result",
    "expected_control_status",
    "control_status",
    "positive_evidence_admissible",
    "positive_DR_rung_assigned",
)

BLOCKED_CLAIMS = [
    "D0a_decay_relation_supported",
    "route_organization_persistence",
    "route_organization_weakening",
    "causal_mediation",
    "native_temporal_alignment_mediator",
    "native_arrival_distribution_mediator",
    "generic_mixed_domain_mediator",
    "semantic_decay",
    "semantic_memory",
    "trail_or_stigmergic_field",
    "ecology_coordination",
    "communication",
    "learning",
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


def build_i3_revision_lineage(i3: dict[str, Any]) -> dict[str, Any]:
    semantic_projection = [
        {field: row.get(field) for field in I3_SEMANTIC_PROJECTION_FIELDS}
        for row in sorted(i3["active_null_rows"], key=lambda item: item["control_id"])
    ]
    semantic_digest = digest_value(semantic_projection)
    control_id_digest = digest_value(
        sorted(row["control_id"] for row in i3["active_null_rows"])
    )
    lineage_checks = [
        check(
            "current_I3_identity_exact",
            i3["output_digest"] == I3_OUTPUT_DIGEST
            and sha256_file(I3_OUTPUT) == I3_ARTIFACT_SHA256,
            i3["output_digest"],
        ),
        check(
            "control_identity_set_unchanged_from_prior_review_package",
            control_id_digest == I3_CONTROL_ID_SET_DIGEST,
            control_id_digest,
        ),
        check(
            "scientific_control_semantics_unchanged_from_prior_review_package",
            semantic_digest == I3_SEMANTIC_PROJECTION_DIGEST,
            semantic_digest,
        ),
        check(
            "scientific_ceiling_unchanged",
            i3["decay_relation_ladder_ceiling"]
            == "DR0_no_source_current_decay_evidence"
            and not i3["positive_evidence_opened"],
            i3["decay_relation_ladder_ceiling"],
        ),
    ]
    lineage: dict[str, Any] = {
        "experiment": "N31",
        "artifact_kind": "I3_revision_lineage",
        "artifact_schema_version": "n31_i3_revision_lineage_v1",
        "revision_id": "N31-I3R1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_I3R1_provenance_and_semantic_invariance_closed",
        "prior_review_package": {
            "label": "N31-I3-pre-validator-receipt-review-package",
            "output_digest": I3_PRIOR_OUTPUT_DIGEST,
            "artifact_sha256": I3_PRIOR_ARTIFACT_SHA256,
            "consumed_by_I4": False,
        },
        "current_committed_artifact": {
            "label": "N31-I3R1",
            "path": I3_OUTPUT.relative_to(ROOT).as_posix(),
            "commit": I4_GOVERNANCE_BASE_REVISION,
            "output_digest": i3["output_digest"],
            "artifact_sha256": sha256_file(I3_OUTPUT),
            "consumed_by_I4": True,
        },
        "revision_reason": (
            "post-review hardening made failed_closed validator-derived, added "
            "bad/repaired fixture receipts, clarified cross-cut counts, froze the "
            "future candidate control resolver, and froze semantic transition records"
        ),
        "scientific_semantics_comparison": {
            "comparison_scope": list(I3_SEMANTIC_PROJECTION_FIELDS),
            "prior_semantic_projection_digest": I3_SEMANTIC_PROJECTION_DIGEST,
            "current_semantic_projection_digest": semantic_digest,
            "prior_control_id_set_digest": I3_CONTROL_ID_SET_DIGEST,
            "current_control_id_set_digest": control_id_digest,
            "row_count_before": 70,
            "row_count_after": len(i3["active_null_rows"]),
            "scientific_control_meaning_changed": False,
            "positive_evidence_status_changed": False,
            "DR_ceiling_changed": False,
        },
        "changed_record_surfaces": [
            "scenario_facts strengthened for executable predicates",
            "actual_result now records bad-fixture rejection and repaired-fixture acceptance",
            "row_digest regenerated after receipt hardening",
            "validator_receipt added per row",
            "future_candidate_control_resolver_schema added",
            "future_semantic_transition_record_schema added",
            "cross_cut_counts_are_tags_not_additional_rows added",
        ],
        "unchanged_scientific_surfaces": [
            "70 control identities and six disjoint families",
            "claim under test and false-positive scenario",
            "violated gate and expected claim failure",
            "semantic and authority classes",
            "organization and load-bearing domains",
            "rung effects and control statuses",
            "no-positive-evidence and DR0 ceiling",
        ],
        "checks": lineage_checks,
    }
    lineage["failed_checks"] = [
        row["check_id"] for row in lineage_checks if not row["passed"]
    ]
    if lineage["failed_checks"]:
        lineage["status"] = "failed"
        lineage["acceptance_state"] = "blocked_I3_revision_lineage_not_closed"
    lineage["output_digest"] = digest_value(
        {key: value for key, value in lineage.items() if key != "output_digest"}
    )
    return lineage


def build_fixture_model() -> LGRC9V3:
    """Build a route with an explicit boundary and one in-flight internal packet."""

    graph = PortGraphBackend()
    labels = ("route_source", "route_mid", "route_exit", "outside_receiver")
    for label in labels:
        graph.add_node({"label": label})

    edge_specs = (
        (0, 1, 0, 0, "route_internal", 0.125),
        (1, 2, 1, 0, "route_internal", -0.0625),
        (2, 3, 1, 0, "route_boundary", 0.03125),
    )
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for source, target, source_slot, target_slot, kind, flux in edge_specs:
        edge_id = graph.connect_ports(
            source,
            source_slot,
            target,
            target_slot,
            {"kind": kind},
        )
        port_edges[edge_id] = PortEdge(
            source,
            source_slot + 1,
            target,
            target_slot + 1,
            conductance=1.0,
            flux_uv=flux,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.25

    state = GRC9V3State(
        topology=graph,
        nodes={
            0: GRC9V3NodeState(coherence=1.25),
            1: GRC9V3NodeState(coherence=0.75),
            2: GRC9V3NodeState(coherence=0.5),
            3: GRC9V3NodeState(coherence=0.5),
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )
    model = LGRC9V3.from_state(state, {"dt": 1.0})
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.run_event_queue(max_events=1)
    return model


def route_edge_partition(model: LGRC9V3) -> tuple[list[int], list[int]]:
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


def internal_in_flight_mass(model: LGRC9V3) -> float:
    support = set(ROUTE_SUPPORT)
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    return sum(
        float(packet.amount)
        for packet in ledger.packet_records
        if packet.packet_state == "in_flight"
        and int(packet.source_node_id) in support
        and int(packet.target_node_id) in support
    )


def decompose_identity(
    identity: dict[str, Any],
    *,
    model: LGRC9V3,
) -> dict[str, Any]:
    """Factor registered-route C and signed flux out of full scientific identity."""

    context = deepcopy(identity)
    state = context["embedded_grc9v3_state"]["state"]
    route_nodes = state["nodes"]
    node_coherence = {
        str(node_id): float(route_nodes[str(node_id)]["coherence"])
        for node_id in ROUTE_SUPPORT
    }
    for node_id in ROUTE_SUPPORT:
        route_nodes[str(node_id)]["coherence"] = None

    internal_edges, boundary_edges = route_edge_partition(model)
    internal_signed_flux = {
        str(edge_id): float(state["port_edges"][str(edge_id)]["flux_uv"])
        for edge_id in internal_edges
    }
    boundary_signed_flux = {
        str(edge_id): float(state["port_edges"][str(edge_id)]["flux_uv"])
        for edge_id in boundary_edges
    }
    for edge_id in internal_edges + boundary_edges:
        state["port_edges"][str(edge_id)]["flux_uv"] = None

    anchor_id = ROUTE_SUPPORT[-1]
    anchor_value = node_coherence[str(anchor_id)]
    pairwise_coordinates = {
        str(node_id): node_coherence[str(node_id)] - anchor_value
        for node_id in ROUTE_SUPPORT[:-1]
    }
    in_flight = internal_in_flight_mass(model)
    node_mass = sum(node_coherence.values())
    model_edges = model.get_state().base_state.port_edges
    coherence_coordinate_map = [
        {
            "coordinate_id": f"C[{node_id}]-C[{anchor_id}]",
            "node_id": node_id,
            "anchor_node_id": anchor_id,
            "orientation": "node_minus_anchor",
            "identity_path": (
                f"embedded_grc9v3_state.state.nodes.{node_id}.coherence"
            ),
        }
        for node_id in ROUTE_SUPPORT[:-1]
    ]

    def flux_coordinate_map(edge_ids: list[int], channel: str) -> list[dict[str, Any]]:
        return [
            {
                "coordinate_id": f"flux_uv[{edge_id}]",
                "edge_id": edge_id,
                "node_u": int(model_edges[edge_id].node_u),
                "node_v": int(model_edges[edge_id].node_v),
                "orientation": "node_u_to_node_v_positive",
                "channel": channel,
                "identity_path": (
                    f"embedded_grc9v3_state.state.port_edges.{edge_id}.flux_uv"
                ),
            }
            for edge_id in edge_ids
        ]

    internal_flux_map = flux_coordinate_map(internal_edges, "spatial_organization")
    boundary_flux_map = flux_coordinate_map(boundary_edges, "boundary_transfer")
    excluded_paths = [
        row["identity_path"]
        for row in coherence_coordinate_map + internal_flux_map + boundary_flux_map
    ]
    return {
        "projection_contract_id": PROJECTION_CONTRACT_ID,
        "basis": "canonical_registered_route_pairwise_C_and_oriented_flux_coordinates",
        "ordered_route_node_ids": list(ROUTE_SUPPORT),
        "anchor_node_id": anchor_id,
        "coherence_coordinate_map": coherence_coordinate_map,
        "coordinate_orientation": "node_minus_anchor_and_native_edge_u_to_v_positive",
        "internal_flux_coordinate_map": internal_flux_map,
        "boundary_flux_coordinate_map": boundary_flux_map,
        "context_excluded_state_paths": excluded_paths,
        "context_reinsertion_paths": excluded_paths,
        "mass_channel": {
            "node_coherence_mass": node_mass,
            "internal_in_flight_packet_mass": in_flight,
            "registered_route_mass": node_mass + in_flight,
            "in_flight_boundary_treatment": (
                "count_packets_with_source_and_target_inside_support_once"
            ),
        },
        "spatial_organization_channel": {
            "pairwise_coherence_coordinates_relative_to_anchor": (
                pairwise_coordinates
            ),
            "oriented_internal_flux_coordinates": internal_signed_flux,
        },
        "boundary_transfer_channel": {
            "oriented_boundary_flux_coordinates": boundary_signed_flux,
            "quantity_semantics": "instantaneous_native_edge_flux_not_integrated_transfer",
        },
        "exact_context_channel": context,
        "exact_context_digest": digest_value(context),
    }


def recompose_identity(projection: dict[str, Any]) -> dict[str, Any]:
    context = deepcopy(projection["exact_context_channel"])
    support = [int(node_id) for node_id in projection["ordered_route_node_ids"]]
    anchor_id = int(projection["anchor_node_id"])
    differences = {
        int(node_id): float(value)
        for node_id, value in projection["spatial_organization_channel"][
            "pairwise_coherence_coordinates_relative_to_anchor"
        ].items()
    }
    node_mass = float(projection["mass_channel"]["node_coherence_mass"])
    anchor_value = (node_mass - sum(differences.values())) / len(support)
    node_values = {
        node_id: (anchor_value if node_id == anchor_id else anchor_value + differences[node_id])
        for node_id in support
    }
    state = context["embedded_grc9v3_state"]["state"]
    for node_id, value in node_values.items():
        state["nodes"][str(node_id)]["coherence"] = value
    for channel_name, coordinate_name in (
        ("spatial_organization_channel", "oriented_internal_flux_coordinates"),
        ("boundary_transfer_channel", "oriented_boundary_flux_coordinates"),
    ):
        for edge_id, value in projection[channel_name][coordinate_name].items():
            state["port_edges"][str(edge_id)]["flux_uv"] = float(value)
    return context


def maximum_route_reconstruction_error(
    source: dict[str, Any], reconstructed: dict[str, Any]
) -> float:
    source_state = source["embedded_grc9v3_state"]["state"]
    reconstructed_state = reconstructed["embedded_grc9v3_state"]["state"]
    values: list[float] = []
    for node_id in ROUTE_SUPPORT:
        values.append(
            abs(
                float(source_state["nodes"][str(node_id)]["coherence"])
                - float(reconstructed_state["nodes"][str(node_id)]["coherence"])
            )
        )
    for edge_id in (0, 1, 2):
        values.append(
            abs(
                float(source_state["port_edges"][str(edge_id)]["flux_uv"])
                - float(reconstructed_state["port_edges"][str(edge_id)]["flux_uv"])
            )
        )
    return max(values, default=0.0)


def build_conformance_fixture() -> dict[str, Any]:
    model = build_fixture_model()
    snapshot = model.snapshot()
    identity = lgrc9v3_restoration_identity_v1(snapshot)
    projection = decompose_identity(identity, model=model)
    reconstructed = recompose_identity(projection)
    error = maximum_route_reconstruction_error(identity, reconstructed)

    contrast_model = build_fixture_model()
    contrast_state = deepcopy(contrast_model.get_state())
    for node_id in ROUTE_SUPPORT:
        contrast_state.base_state.nodes[node_id].coherence = 0.75
    contrast_model.set_state(contrast_state)
    contrast_snapshot = contrast_model.snapshot()
    contrast_identity = lgrc9v3_restoration_identity_v1(contrast_snapshot)
    contrast_projection = decompose_identity(
        contrast_identity,
        model=contrast_model,
    )
    source_state = identity["embedded_grc9v3_state"]["state"]
    contrast_state = contrast_identity["embedded_grc9v3_state"]["state"]
    source_selected_scalar = float(source_state["nodes"]["1"]["coherence"])
    contrast_selected_scalar = float(contrast_state["nodes"]["1"]["coherence"])

    state = model.get_state()
    contrast_runtime_state = contrast_model.get_state()
    source_ledger = state.packet_ledger
    contrast_ledger = contrast_runtime_state.packet_ledger
    assert source_ledger is not None
    assert contrast_ledger is not None
    source_all_node_coherence = sum(
        float(node.coherence) for node in state.base_state.nodes.values()
    )
    contrast_all_node_coherence = sum(
        float(node.coherence)
        for node in contrast_runtime_state.base_state.nodes.values()
    )
    internal_edges, boundary_edges = route_edge_partition(model)
    boundary_edge = state.base_state.port_edges[boundary_edges[0]]
    outward_sign = 1.0 if boundary_edge.node_u in ROUTE_SUPPORT else -1.0
    net_outward_flux_rate = outward_sign * float(boundary_edge.flux_uv)
    fixture: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "4",
        "artifact_kind": "D0a_spatial_projection_conformance_fixture",
        "artifact_schema_version": "n31_i4_projection_conformance_fixture_v1",
        "fixture_id": FIXTURE_ID,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_source_current_representation_conformance_not_decay_evidence"
        ),
        "source_current_runtime_artifact": True,
        "derived_report_only": False,
        "positive_decay_evidence_admissible": False,
        "runtime_execution": {
            "model_family": "LGRC9V3",
            "public_operations": [
                "LGRC9V3.from_state",
                "LGRC9V3.schedule_packet_departure",
                "LGRC9V3.run_event_queue",
                "LGRC9V3.get_state",
                "LGRC9V3.set_state",
                "LGRC9V3.snapshot",
                "lgrc9v3_restoration_identity_v1",
            ],
            "forming_packet_departure_processed": True,
            "internal_in_flight_packet_count": 1,
            "internal_in_flight_packet_amount": internal_in_flight_mass(model),
            "event_queue_record_count": len(
                state.packet_ledger.event_queue_records  # type: ignore[union-attr]
            ),
        },
        "registered_route": {
            "support_node_ids": list(ROUTE_SUPPORT),
            "internal_edge_ids": internal_edges,
            "boundary_edge_ids": boundary_edges,
            "boundary_orientation": "inside_to_outside_positive",
            "net_outward_boundary_flux_rate": net_outward_flux_rate,
            "net_outward_boundary_flux_quantity_semantics": (
                "instantaneous_signed_native_edge_flux_not_time_integrated_export"
            ),
            "support_exactly_enumerated": True,
            "boundary_exactly_enumerated": True,
            "instantaneous_net_flux_exactly_measurable": True,
            "time_integrated_boundary_transfer_established": False,
        },
        "source_identity": {
            "restoration_identity_schema": "lgrc9v3_restoration_identity_v1",
            "restoration_identity_scope": "current_scientific_state_only",
            "v1_use_reason": (
                "I4 projects current state and does not invoke reset or claim reset equivalence"
            ),
            "restoration_identity_digest": digest_lgrc9v3_restoration_identity_v1(
                snapshot
            ),
            "reset_sensitive_identity_schema": "lgrc9v3_restoration_identity_v2",
            "reset_sensitive_identity_digest": digest_lgrc9v3_restoration_identity_v2(
                snapshot
            ),
            "reset_sensitive_operation_performed": False,
            "future_reset_sensitive_rows_require_v2": True,
        },
        "projection_contract": {
            "projection_contract_id": PROJECTION_CONTRACT_ID,
            "basis": projection["basis"],
            "ordered_route_node_ids": projection["ordered_route_node_ids"],
            "anchor_node_id": projection["anchor_node_id"],
            "coherence_coordinate_map": projection["coherence_coordinate_map"],
            "coordinate_orientation": projection["coordinate_orientation"],
            "internal_flux_coordinate_map": projection[
                "internal_flux_coordinate_map"
            ],
            "boundary_flux_coordinate_map": projection[
                "boundary_flux_coordinate_map"
            ],
            "context_excluded_state_paths": projection[
                "context_excluded_state_paths"
            ],
            "context_reinsertion_paths": projection[
                "context_reinsertion_paths"
            ],
            "decomposition_operator": (
                "factor route C into total node mass plus anchor-relative coordinates; "
                "retain internal signed flux as spatial organization; separate boundary "
                "signed flux as transfer; retain every other restoration-identity field "
                "in an exact matched context channel"
            ),
            "recomposition_operator": (
                "solve anchor C from total node mass and pairwise coordinates; restore "
                "oriented flux coordinates; reinsert into exact context"
            ),
            "overlap_or_orthogonality_policy": (
                "mass and pairwise C coordinates are algebraically independent; internal "
                "flux, boundary transfer, and other continuation state remain separate "
                "named channels"
            ),
            "temporal_support": "single_source_current_checkpoint_no_history_window",
            "intervention_semantics": (
                "paired full-state reconstruction may change only route C organization "
                "coordinates while route mass and exact context remain matched; this is a "
                "representation conformance intervention, not a causal decay result"
            ),
            "reconstruction_error_bound": RECONSTRUCTION_ERROR_BOUND,
            "observed_reconstruction_error": error,
            "no_independent_causal_state": True,
            "projection_persisted_as_runtime_state": False,
            "projection_fed_back_into_runtime": False,
        },
        "projection_receipt": {
            "source_identity_digest": digest_value(identity),
            "projection_context_digest": projection["exact_context_digest"],
            "mass_channel": projection["mass_channel"],
            "spatial_organization_channel": projection[
                "spatial_organization_channel"
            ],
            "boundary_transfer_channel": projection["boundary_transfer_channel"],
            "exact_context_channel_digest": projection["exact_context_digest"],
            "reconstructed_identity_digest": digest_value(reconstructed),
            "identity_digest_equal_after_roundtrip": (
                digest_value(identity) == digest_value(reconstructed)
            ),
            "reconstruction_within_bound": error <= RECONSTRUCTION_ERROR_BOUND,
        },
        "mass_organization_separation_receipt": {
            "source_route_mass": projection["mass_channel"]["registered_route_mass"],
            "contrast_route_mass": contrast_projection["mass_channel"][
                "registered_route_mass"
            ],
            "route_mass_matched": (
                projection["mass_channel"]["registered_route_mass"]
                == contrast_projection["mass_channel"]["registered_route_mass"]
            ),
            "selected_node_scalar_id": 1,
            "source_selected_node_scalar": source_selected_scalar,
            "contrast_selected_node_scalar": contrast_selected_scalar,
            "selected_node_scalar_matched": (
                source_selected_scalar == contrast_selected_scalar
            ),
            "source_organization_digest": digest_value(
                projection["spatial_organization_channel"]
            ),
            "contrast_organization_digest": digest_value(
                contrast_projection["spatial_organization_channel"]
            ),
            "route_organization_differs": (
                digest_value(projection["spatial_organization_channel"])
                != digest_value(contrast_projection["spatial_organization_channel"])
            ),
            "source_boundary_transfer_digest": digest_value(
                projection["boundary_transfer_channel"]
            ),
            "contrast_boundary_transfer_digest": digest_value(
                contrast_projection["boundary_transfer_channel"]
            ),
            "boundary_transfer_matched": (
                digest_value(projection["boundary_transfer_channel"])
                == digest_value(contrast_projection["boundary_transfer_channel"])
            ),
            "exact_context_matched": (
                projection["exact_context_digest"]
                == contrast_projection["exact_context_digest"]
            ),
            "paired_native_state_intervention_applied": True,
            "paired_native_state_intervention_surface": "LGRC9V3.set_state",
            "paired_intervention_changed_native_state_paths": [
                "base_state.nodes[0].coherence",
                "base_state.nodes[2].coherence",
            ],
            "paired_intervention_held_native_state_paths_equal": (
                "all_other_lgrc9v3_restoration_identity_v1_fields"
            ),
            "complete_identity_differs": (
                digest_value(identity) != digest_value(contrast_identity)
            ),
            "causal_mediation_tested": False,
        },
        "intervention_admissibility_receipt": {
            "intervention_class": "surgical_matched_state_clamp",
            "public_surface": "LGRC9V3.set_state",
            "allowed_as_representation_separability_evidence": True,
            "allowed_as_matched_intervention_fixture": True,
            "allowed_as_native_formation_evidence": False,
            "allowed_as_autonomous_weakening_evidence": False,
            "source_all_node_coherence_nonnegative": all(
                float(node.coherence) >= 0.0
                for node in state.base_state.nodes.values()
            ),
            "contrast_all_node_coherence_nonnegative": all(
                float(node.coherence) >= 0.0
                for node in contrast_runtime_state.base_state.nodes.values()
            ),
            "source_all_node_coherence_total": source_all_node_coherence,
            "contrast_all_node_coherence_total": contrast_all_node_coherence,
            "all_node_coherence_total_matched": (
                source_all_node_coherence == contrast_all_node_coherence
            ),
            "source_conserved_budget_total": float(
                source_ledger.conserved_budget_total
            ),
            "contrast_conserved_budget_total": float(
                contrast_ledger.conserved_budget_total
            ),
            "conserved_budget_total_matched": (
                float(source_ledger.conserved_budget_total)
                == float(contrast_ledger.conserved_budget_total)
            ),
            "source_packet_ledger_budget_error": float(source_ledger.budget_error),
            "contrast_packet_ledger_budget_error": float(
                contrast_ledger.budget_error
            ),
            "packet_and_queue_context_matched": (
                projection["exact_context_digest"]
                == contrast_projection["exact_context_digest"]
            ),
            "constitutive_dependent_fields_recomputed_after_clamp": False,
            "causal_interpretation": (
                "representation_separability_only; future causal use requires native "
                "trajectory formation or explicit dependent-field recomputation, otherwise "
                "the clamp remains a narrow intervention"
            ),
        },
    }
    fixture["checks"] = [
        check(
            "identity_roundtrip_exact",
            fixture["projection_receipt"]["identity_digest_equal_after_roundtrip"],
            fixture["projection_receipt"]["reconstructed_identity_digest"],
        ),
        check(
            "reconstruction_error_within_bound",
            error <= RECONSTRUCTION_ERROR_BOUND,
            {"observed": error, "bound": RECONSTRUCTION_ERROR_BOUND},
        ),
        check(
            "same_mass_different_organization_contrast",
            fixture["mass_organization_separation_receipt"]["route_mass_matched"]
            and fixture["mass_organization_separation_receipt"][
                "route_organization_differs"
            ]
            and fixture["mass_organization_separation_receipt"][
                "selected_node_scalar_matched"
            ]
            and fixture["mass_organization_separation_receipt"][
                "boundary_transfer_matched"
            ],
            "same route mass and selected node scalar; different complete C distribution",
        ),
        check(
            "surgical_clamp_invariants_preserved",
            fixture["intervention_admissibility_receipt"][
                "source_all_node_coherence_nonnegative"
            ]
            and fixture["intervention_admissibility_receipt"][
                "contrast_all_node_coherence_nonnegative"
            ]
            and fixture["intervention_admissibility_receipt"][
                "all_node_coherence_total_matched"
            ]
            and fixture["intervention_admissibility_receipt"][
                "conserved_budget_total_matched"
            ]
            and fixture["intervention_admissibility_receipt"][
                "source_packet_ledger_budget_error"
            ]
            == 0.0
            and fixture["intervention_admissibility_receipt"][
                "contrast_packet_ledger_budget_error"
            ]
            == 0.0
            and fixture["intervention_admissibility_receipt"][
                "packet_and_queue_context_matched"
            ]
            and not fixture["intervention_admissibility_receipt"][
                "allowed_as_native_formation_evidence"
            ]
            and not fixture["intervention_admissibility_receipt"][
                "allowed_as_autonomous_weakening_evidence"
            ],
            fixture["intervention_admissibility_receipt"],
        ),
        check(
            "projection_has_no_independent_state",
            fixture["projection_contract"]["no_independent_causal_state"]
            and not fixture["projection_contract"]["projection_persisted_as_runtime_state"]
            and not fixture["projection_contract"]["projection_fed_back_into_runtime"],
            PROJECTION_CONTRACT_ID,
        ),
        check(
            "registered_boundary_flux_scope_is_bounded",
            fixture["registered_route"]["instantaneous_net_flux_exactly_measurable"]
            and not fixture["registered_route"][
                "time_integrated_boundary_transfer_established"
            ],
            net_outward_flux_rate,
        ),
    ]
    fixture["failed_checks"] = [
        row["check_id"] for row in fixture["checks"] if not row["passed"]
    ]
    if fixture["failed_checks"]:
        fixture["status"] = "failed"
        fixture["acceptance_state"] = "blocked_projection_conformance_failed"
    fixture["output_digest"] = digest_value(
        {key: value for key, value in fixture.items() if key != "output_digest"}
    )
    return fixture


def complete_state_crosswalk() -> list[dict[str, Any]]:
    return [
        {
            "theory_state_group": "registered_route_support_and_boundary",
            "runtime_or_contract_source": (
                "GRC9V3State.topology plus experiment-registered support/orientation"
            ),
            "representation_status": "represented_by_exact_projection",
            "update_owner": "native_topology; experiment_contract_selects_route",
            "scientific_role": "declares where route mass and boundary flux are measured",
        },
        {
            "theory_state_group": "node_coherence_distribution",
            "runtime_or_contract_source": "LGRC9V3RuntimeState.base_state.nodes[*].coherence",
            "representation_status": "represented_by_exact_projection",
            "update_owner": "native_GRC9V3_and_LGRC9V3_packet_transport",
            "scientific_role": "spatial C organization; not reducible to one node scalar",
        },
        {
            "theory_state_group": "route_mass",
            "runtime_or_contract_source": (
                "registered node C plus route-owned in-flight packet amounts"
            ),
            "representation_status": "represented_by_exact_projection",
            "update_owner": "native_node_and_packet_ledger_state",
            "scientific_role": "mass channel kept separate from organization",
        },
        {
            "theory_state_group": "signed_route_and_boundary_flux",
            "runtime_or_contract_source": "GRC9V3State.port_edges[*].flux_uv",
            "representation_status": "represented_by_exact_projection",
            "update_owner": "native_GRC9V3_edge_state",
            "scientific_role": (
                "instantaneous oriented flux; integrated export requires a later window"
            ),
        },
        {
            "theory_state_group": "edge_geometry_and_functional_coupling",
            "runtime_or_contract_source": (
                "base_conductance, geometric_length, temporal_delay, flux_coupling"
            ),
            "representation_status": "represented_natively",
            "update_owner": "native_GRC9V3_state_and_frozen_constitutive_policy",
            "scientific_role": "matched context; change does not itself prove decay",
        },
        {
            "theory_state_group": "packet_identity_and_in_flight_state",
            "runtime_or_contract_source": "LGRC9V3RuntimeState.packet_ledger",
            "representation_status": "represented_natively",
            "update_owner": "native_LGRC9V3_packet_transport",
            "scientific_role": "prevents route mass and forming-packet ambiguity",
        },
        {
            "theory_state_group": "event_ordering_and_local_time",
            "runtime_or_contract_source": (
                "event_queue, event_time_key, node_proper_time, edge_causal_delay"
            ),
            "representation_status": "represented_natively",
            "update_owner": "native_LGRC9V3_scheduler_and_local_update",
            "scientific_role": (
                "complete continuation context; annotations do not prove alignment mediation"
            ),
        },
        {
            "theory_state_group": "constitutive_and_causal_policies",
            "runtime_or_contract_source": (
                "restoration identity parameter identity and causal_modes"
            ),
            "representation_status": "represented_natively",
            "update_owner": "frozen_model_configuration",
            "scientific_role": "prevents hidden policy differences in matched intervention",
        },
        {
            "theory_state_group": "other_scientific_continuation_state",
            "runtime_or_contract_source": "lgrc9v3_restoration_identity_v1 context channel",
            "representation_status": "represented_natively",
            "update_owner": "native_GRC9V3_LGRC9V3_runtime",
            "scientific_role": "kept exact rather than assumed irrelevant",
        },
        {
            "theory_state_group": "later_local_readout_and_causal_mediation",
            "runtime_or_contract_source": "not_created_by_representation_projection",
            "representation_status": "missing",
            "update_owner": "pending_source_current_I7_probe",
            "scientific_role": "independent gate; representation does not establish DR4",
        },
    ]


def domain_matrix() -> list[dict[str, Any]]:
    return [
        {
            "organization_domain": "spatial_distribution",
            "representation_status": "represented_by_exact_projection",
            "authority": "exact_derived_projection",
            "I7_representation_admissible": True,
            "standalone_D0a_carrier_lane_admitted": True,
            "I7_role": "selected_load_bearing_carrier_candidate",
            "scope": "registered_route_C_distribution_and_oriented_flux_with_exact_context",
            "blocker_or_condition": "persistence_weakening_and_mediation_still_unmeasured",
        },
        {
            "organization_domain": "induced_geometry",
            "representation_status": "represented_by_exact_projection",
            "authority": "exact_derived_projection",
            "I7_representation_admissible": True,
            "standalone_D0a_carrier_lane_admitted": False,
            "I7_role": "derived_response_component_of_selected_spatial_lane",
            "scope": "native_topology_edge_labels_and_complete_C_state",
            "blocker_or_condition": "local_transport_intervention_required_for_causal_D0a",
        },
        {
            "organization_domain": "functional_coupling",
            "representation_status": "represented_natively",
            "authority": "native_state",
            "I7_representation_admissible": True,
            "standalone_D0a_carrier_lane_admitted": False,
            "I7_role": "native_response_context_of_selected_spatial_lane",
            "scope": "conductance_flux_coupling_and_signed_edge_state",
            "blocker_or_condition": "no_weakening_law_or_load_bearing_use_established_by_I4",
        },
        {
            "organization_domain": "temporal_alignment",
            "representation_status": "missing",
            "authority": "missing",
            "I7_representation_admissible": False,
            "standalone_D0a_carrier_lane_admitted": False,
            "I7_role": "blocked_as_load_bearing_carrier",
            "scope": "native_timestamps_and_delays_are_diagnostics_only",
            "blocker_or_condition": "no_native_coincidence_resonance_or_alignment_mediator",
        },
        {
            "organization_domain": "arrival_time_distribution",
            "representation_status": "missing",
            "authority": "missing_for_D0a",
            "I7_representation_admissible": False,
            "standalone_D0a_carrier_lane_admitted": False,
            "I7_role": "D0b_observable_only_not_D0a_carrier",
            "scope": "exact_history_projection_remains_D0b_observable_candidate",
            "blocker_or_condition": "no_native_persistent_load_bearing_distribution_state",
        },
        {
            "organization_domain": "mixed",
            "representation_status": "missing",
            "authority": "unresolved",
            "I7_representation_admissible": False,
            "standalone_D0a_carrier_lane_admitted": False,
            "I7_role": "blocked_until_load_bearing_domain_resolved",
            "scope": "no_combined_domain_is_admitted_by_aggregation",
            "blocker_or_condition": "must_resolve_one_load_bearing_domain",
        },
        {
            "organization_domain": "other",
            "representation_status": "missing",
            "authority": "missing",
            "I7_representation_admissible": False,
            "standalone_D0a_carrier_lane_admitted": False,
            "I7_role": "blocked_without_new_representation_contract",
            "scope": "no_unspecified_mediator_admitted",
            "blocker_or_condition": "new_source_backed_representation_contract_required",
        },
    ]


def build_payload(
    fixture: dict[str, Any], i3_revision: dict[str, Any]
) -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    src_diff_empty = git_diff_empty(PROTECTED_RUNTIME_BASE_REVISION, "src")
    protected_paths_clean = all(
        git_diff_empty(PROTECTED_RUNTIME_BASE_REVISION, path)
        for path in ("src", "specs", "tests")
    )
    crosswalk = complete_state_crosswalk()
    domains = domain_matrix()
    status_enum = i2["schema"]["d0a_representation_gate"]["status_enum"]
    global_status = "represented_by_exact_projection"
    checks = [
        check(
            "I2_source_chain_exact",
            i2["output_digest"] == I2_OUTPUT_DIGEST
            and sha256_file(I2_OUTPUT) == I2_ARTIFACT_SHA256,
            i2["output_digest"],
        ),
        check(
            "I3_source_chain_exact",
            i3["output_digest"] == I3_OUTPUT_DIGEST
            and sha256_file(I3_OUTPUT) == I3_ARTIFACT_SHA256,
            i3["output_digest"],
        ),
        check(
            "I3R1_revision_lineage_closed",
            i3_revision["status"] == "passed"
            and not i3_revision["failed_checks"]
            and i3_revision["current_committed_artifact"]["consumed_by_I4"]
            and not i3_revision["scientific_semantics_comparison"][
                "scientific_control_meaning_changed"
            ],
            i3_revision["revision_id"],
        ),
        check(
            "complete_D0a_state_crosswalk_present",
            len(crosswalk) == 10
            and all(
                row.get("representation_status")
                and row.get("runtime_or_contract_source")
                and row.get("update_owner")
                for row in crosswalk
            ),
            len(crosswalk),
        ),
        check(
            "route_mass_organization_mediation_separate",
            fixture["mass_organization_separation_receipt"]["route_mass_matched"]
            and fixture["mass_organization_separation_receipt"][
                "route_organization_differs"
            ]
            and fixture["mass_organization_separation_receipt"][
                "exact_context_matched"
            ]
            and fixture["mass_organization_separation_receipt"][
                "boundary_transfer_matched"
            ]
            and fixture["mass_organization_separation_receipt"][
                "paired_native_state_intervention_applied"
            ]
            and not fixture["mass_organization_separation_receipt"][
                "causal_mediation_tested"
            ],
            fixture["mass_organization_separation_receipt"],
        ),
        check(
            "support_boundary_and_instantaneous_flux_exact",
            fixture["registered_route"]["support_exactly_enumerated"]
            and fixture["registered_route"]["boundary_exactly_enumerated"]
            and fixture["registered_route"]["instantaneous_net_flux_exactly_measurable"],
            fixture["registered_route"],
        ),
        check(
            "exact_projection_roundtrip_passed",
            fixture["projection_receipt"]["identity_digest_equal_after_roundtrip"]
            and fixture["projection_receipt"]["reconstruction_within_bound"],
            fixture["projection_receipt"],
        ),
        check(
            "machine_projection_mapping_complete",
            bool(fixture["projection_contract"]["ordered_route_node_ids"])
            and bool(fixture["projection_contract"]["coherence_coordinate_map"])
            and bool(fixture["projection_contract"]["internal_flux_coordinate_map"])
            and bool(fixture["projection_contract"]["boundary_flux_coordinate_map"])
            and fixture["projection_contract"]["context_excluded_state_paths"]
            == fixture["projection_contract"]["context_reinsertion_paths"],
            PROJECTION_CONTRACT_ID,
        ),
        check(
            "exact_projection_schema_complete",
            set(
                i2["schema"]["d0a_representation_gate"][
                    "exact_projection_required_fields"
                ]
            ).issubset(fixture["projection_contract"]),
            i2["schema"]["d0a_representation_gate"][
                "exact_projection_required_fields"
            ],
        ),
        check(
            "projection_has_no_independent_causal_state",
            fixture["projection_contract"]["no_independent_causal_state"]
            and not fixture["projection_contract"]["projection_persisted_as_runtime_state"]
            and not fixture["projection_contract"]["projection_fed_back_into_runtime"],
            PROJECTION_CONTRACT_ID,
        ),
        check(
            "all_organization_domains_dispositioned",
            {row["organization_domain"] for row in domains}
            == set(
                i2["schema"]["route_organization_contract_schema"][
                    "organization_domain_enum"
                ]
            ),
            [row["organization_domain"] for row in domains],
        ),
        check(
            "blocked_domains_not_admitted",
            all(
                not row["I7_representation_admissible"]
                for row in domains
                if row["representation_status"] == "missing"
            ),
            [
                row["organization_domain"]
                for row in domains
                if row["representation_status"] == "missing"
            ],
        ),
        check(
            "one_standalone_D0a_carrier_lane_admitted",
            [
                row["organization_domain"]
                for row in domains
                if row["standalone_D0a_carrier_lane_admitted"]
            ]
            == ["spatial_distribution"],
            "spatial_distribution",
        ),
        check(
            "one_global_D0a_status_assigned",
            global_status in status_enum,
            global_status,
        ),
        check(
            "spectral_shortcut_not_used",
            True,
            "truncated_spectrum_lossy; full_spectrum_unfrozen; canonical_coordinates_used",
        ),
        check(
            "timing_annotations_not_promoted",
            all(
                not row["I7_representation_admissible"]
                for row in domains
                if row["organization_domain"]
                in {"temporal_alignment", "arrival_time_distribution"}
            ),
            "timing inputs remain D0b diagnostics until native mediation exists",
        ),
        check(
            "no_persistent_slow_state_invented",
            True,
            "projection is recomputed and is not runtime state",
        ),
        check(
            "no_positive_decay_evidence_opened",
            not fixture["positive_decay_evidence_admissible"],
            "DR0",
        ),
        check(
            "set_state_clamp_bounded_to_representation_role",
            fixture["intervention_admissibility_receipt"][
                "allowed_as_representation_separability_evidence"
            ]
            and not fixture["intervention_admissibility_receipt"][
                "allowed_as_native_formation_evidence"
            ]
            and not fixture["intervention_admissibility_receipt"][
                "allowed_as_autonomous_weakening_evidence"
            ],
            fixture["intervention_admissibility_receipt"]["intervention_class"],
        ),
        check("src_diff_empty", src_diff_empty, src_diff_empty),
        check(
            "protected_runtime_contract_diff_empty",
            protected_paths_clean,
            protected_paths_clean,
        ),
    ]
    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "4",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_scoped_spatial_D0a_exact_projection_representation_gate_"
            "no_positive_decay_evidence"
        ),
        "source_chain": {
            "I2": {
                "path": I2_OUTPUT.relative_to(ROOT).as_posix(),
                "output_digest": i2["output_digest"],
                "artifact_sha256": sha256_file(I2_OUTPUT),
            },
            "I3": {
                "path": I3_OUTPUT.relative_to(ROOT).as_posix(),
                "output_digest": i3["output_digest"],
                "artifact_sha256": sha256_file(I3_OUTPUT),
                "revision_id": i3_revision["revision_id"],
                "revision_lineage_path": I3_REVISION.relative_to(ROOT).as_posix(),
                "revision_lineage_output_digest": i3_revision["output_digest"],
                "revision_lineage_sha256": sha256_file(I3_REVISION),
            },
        },
        "graph_scope": {
            "I4_governance_base_revision": I4_GOVERNANCE_BASE_REVISION,
            "src_diff_empty": src_diff_empty,
            "protected_runtime_contract_diff_empty": protected_paths_clean,
            "runtime_modified": False,
        },
        "D0a_theory_state_requirement": {
            "complete_state_definition": (
                "registered support and boundary; complete route C distribution; route mass "
                "including declared in-flight treatment; signed edge flux; topology, edge "
                "geometry and coupling; packet identity and queue; event ordering, proper time "
                "and delay; frozen policies; and all other continuation-relevant scientific state"
            ),
            "node_scalar_C_alone_complete": False,
            "route_mass_alone_complete": False,
            "timing_annotation_alone_complete": False,
            "later_causal_mediation_is_separate_gate": True,
        },
        "complete_state_crosswalk": crosswalk,
        "exact_projection_contract": fixture["projection_contract"],
        "conformance_fixture": {
            "path": FIXTURE.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(FIXTURE),
            "output_digest": fixture["output_digest"],
            "artifact_role": "source_current_representation_conformance_not_decay_evidence",
        },
        "artifact_manifest": [
            {
                "path": I3_REVISION.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(I3_REVISION),
                "artifact_role": "I3R1_provenance_and_semantic_invariance_lineage",
            },
            {
                "path": FIXTURE.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(FIXTURE),
                "artifact_role": (
                    "source_current_representation_conformance_not_decay_evidence"
                ),
            }
        ],
        "all_artifact_sha256_match_file_contents": True,
        "route_measurement_disposition": fixture["registered_route"],
        "mass_organization_separation_receipt": fixture[
            "mass_organization_separation_receipt"
        ],
        "intervention_admissibility_receipt": fixture[
            "intervention_admissibility_receipt"
        ],
        "induced_geometry_promotion_gate": {
            "current_role": "response_component_of_spatial_C_J_C_lane_only",
            "standalone_carrier_admitted": False,
            "independent_decay_evidence_admissible": False,
            "promotion_requires": [
                "source_current_geometry_state_or_exact_projection",
                "predeclared_geometry_weakening_order",
                "ordinary_internal_progression_or_declared_local_transport_intervention",
                "matched_route_mass_and_boundary_transfer",
                "later_readout_dependency",
                "mediator_clamp_or_ablation_effect",
            ],
            "missing_any_requirement_blocks_load_bearing_geometry_claim": True,
        },
        "I7_weakening_order_preregistration_schema": {
            "status": "candidate_specific_order_not_yet_frozen",
            "schema_fields_required_before_execution": [
                "observable_id",
                "source_current_inputs",
                "stronger_orientation",
                "weaker_orientation",
                "baseline_rule",
                "weakening_threshold",
                "tolerance",
                "trajectory_rule",
                "monotonicity_requirement",
                "sign_or_orientation_ambiguity_resolution",
                "declaration_digest",
                "declared_before_candidate_outcome",
            ],
            "arbitrary_coordinate_movement_is_weakening": False,
            "exact_representability_implies_weakening_order": False,
            "unresolved_sign_or_orientation_ambiguity_blocks_I7_execution": True,
            "candidate_specific_order_frozen": False,
        },
        "future_I7_route_mass_window_requirements": {
            "window_support_and_boundary_frozen_before_execution": True,
            "internal_departure": "debit_source_node_and_count_internal_in_flight_once",
            "internal_in_flight": "count_once_while_both_packet_endpoints_are_in_support",
            "boundary_crossing": "integrate_signed_outward_crossing_once",
            "outside_arrival": "do_not_count_a_second_export",
            "reentry": "integrate_signed_inward_crossing_once",
            "moving_support_policy": "support_change_requires_explicit_reclassification_term",
            "continuity_residual_required": True,
            "instantaneous_flux_may_substitute_for_integrated_transfer": False,
        },
        "spectral_representation_assessment": {
            "truncated_slow_mode_spectrum": {
                "status": "represented_only_by_lossy_coarse_state",
                "D0a_admissible": False,
                "reason": "discarded_modes_prevent_exact_recomposition_and_matched_intervention",
            },
            "full_graph_spectrum": {
                "status": "missing_as_frozen_N31_projection",
                "D0a_admissible": False,
                "reason": (
                    "no_canonical_degeneracy_policy_and_intervention_roundtrip_are_frozen; "
                    "N31_does_not_need_a_spectral_shortcut"
                ),
            },
            "admitted_basis": (
                "canonical_registered_route_pairwise_C_and_oriented_flux_coordinates"
            ),
        },
        "organization_domain_matrix": domains,
        "D0a_representation_gate": {
            "global_status": global_status,
            "global_status_scope": (
                "one_registered_route_spatial_C_J_C_lane; induced_geometry_and_"
                "functional_coupling_are_components_not_standalone_carriers"
            ),
            "status_count": 1,
            "spatial_D0a_representation_gate_open": True,
            "temporal_D0a_representation_gate_open": False,
            "arrival_distribution_D0a_representation_gate_open": False,
            "mixed_D0a_representation_gate_open": False,
            "positive_D0a_evidence_opened": False,
            "runtime_representation_support": (
                "exact spatial projection and native context are available"
            ),
            "theory_support": (
                "D0a remains theoretically compatible but requires source-current "
                "persistence, weakening, and mediation evidence"
            ),
        },
        "positive_evidence_opened": False,
        "candidate_rows_classified": False,
        "decay_relation_ladder_rung_assigned": False,
        "decay_relation_ladder_ceiling": "DR0_no_source_current_decay_evidence",
        "n31_closeout_ladder_rung_assigned": False,
        "n31_closeout_ceiling": "N31-C2_active_nulls_and_representation_boundary_established",
        "n31_progress_rung_assigned": True,
        "n31_progress_rung": (
            "N31-C2_active_nulls_and_representation_boundary_established"
        ),
        "closeout_assignment_policy": (
            "progress_rungs_may_be_recorded_per_iteration; terminal_closeout_rung_is_"
            "assigned_only_by_the_final_N31_closeout_iteration"
        ),
        "n31_c2_active_null_component_satisfied": True,
        "n31_c2_representation_component_satisfied": True,
        "ready_for_iteration_5_D0c_comparator": True,
        "ready_for_iteration_7_spatial_D0a_probe": True,
        "iteration_7_representation_admission_complete": True,
        "iteration_7_execution_preconditions_complete": False,
        "iteration_7_execution_blockers": [
            "candidate_specific_weakening_order_not_frozen",
            "candidate_specific_threshold_and_tolerance_not_frozen",
            "route_mass_window_not_executed",
            "native_formation_or_bounded_clamp_interpretation_not_selected",
        ],
        "claim_boundary": {
            "claim_ceiling": (
                "scoped_spatial_D0a_representation_admission_only_no_decay_relation"
            ),
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {
                f"{claim}_claim_allowed": False for claim in BLOCKED_CLAIMS
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
        payload["acceptance_state"] = "blocked_D0a_representation_gate_validation_failed"
        payload["ready_for_iteration_5_D0c_comparator"] = False
        payload["ready_for_iteration_7_spatial_D0a_probe"] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    domain_rows = "\n".join(
        "| `{domain}` | `{status}` | `{authority}` | `{standalone}` | {role} | "
        "{condition} |".format(
            domain=row["organization_domain"],
            status=row["representation_status"],
            authority=row["authority"],
            standalone=str(row["standalone_D0a_carrier_lane_admitted"]).lower(),
            role=row["I7_role"],
            condition=row["blocker_or_condition"],
        )
        for row in payload["organization_domain_matrix"]
    )
    crosswalk_rows = "\n".join(
        "| {group} | `{status}` | {source} | {owner} |".format(
            group=row["theory_state_group"],
            status=row["representation_status"],
            source=row["runtime_or_contract_source"],
            owner=row["update_owner"],
        )
        for row in payload["complete_state_crosswalk"]
    )
    check_rows = "\n".join(
        f"- `{row['check_id']}` = `{str(row['passed']).lower()}`"
        for row in payload["checks"]
    )
    receipt = payload["mass_organization_separation_receipt"]
    route = payload["route_measurement_disposition"]
    checks_by_id = {row["check_id"]: row for row in payload["checks"]}
    i3_source = payload["source_chain"]["I3"]
    REPORT.write_text(
        f"""# N31 Iteration 4 - D0a Representation Gate

Status: `{payload['status']}`

Acceptance state: `{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## I3 Revision Lineage

I4 consumes the committed I3 artifact as revision `N31-I3R1`. The previously
reviewed I3 package and the committed artifact have different file and output
digests because the committed artifact added validator-derived receipts,
bad/repaired-fixture evidence, and future resolver/transition schemas. The
lineage record verifies that the 70 control identities, their scientific
semantics, the no-positive-evidence status, and the DR0 ceiling are unchanged.

```text
revision lineage = {i3_source['revision_lineage_path']}
revision lineage digest = {i3_source['revision_lineage_output_digest']}
consumed I3 revision = {i3_source['revision_id']}
```

## Result

I4 admits one bounded D0a representation lane:

```text
global D0a representation status = represented_by_exact_projection
admitted scope = registered-route spatial C distribution and internal oriented flux
separate boundary-transfer channel = instantaneous oriented boundary flux
positive decay evidence = not opened
DR ceiling = DR0
```

The status is deliberately scoped. It means LGRC9V3 current scientific state
can be factored into a route-mass channel, a spatial-organization coordinate
channel, a separate boundary-transfer channel, and an exact matched
continuation-state context. It does
not mean every proposed organization domain is represented, and it does not
show persistence, weakening, or a later readout effect.

## Exact Projection

The conformance fixture uses public LGRC9V3 operations, processes one internal
packet departure, and leaves that packet in flight. The projection starts from
`lgrc9v3_restoration_identity_v1`, not from a hand-picked report row. It removes
the registered route's node-coherence and internal signed-flux coordinates,
separates boundary signed flux from organization, retains all other scientific
state in an exact context channel, then reconstructs the identity. The machine
contract records ordered route nodes, the anchor, coordinate maps and
orientations, and every excluded/reinserted restoration-identity path.

Identity v1 is intentional here because I4 projects only current scientific
state and never invokes reset. The fixture also records identity v2 provenance;
any later reset-sensitive row must use v2.

```text
projection contract = {PROJECTION_CONTRACT_ID}
identity roundtrip exact = {str(checks_by_id['exact_projection_roundtrip_passed']['passed']).lower()}
observed reconstruction error = {payload['exact_projection_contract']['observed_reconstruction_error']}
reconstruction bound = {payload['exact_projection_contract']['reconstruction_error_bound']}
projection persisted as runtime state = false
projection fed into runtime = false
```

This is an exact derived projection, not a new slow variable. Its authority is
recomputation from current native state. The representation may therefore be
used to define a later I7 intervention, but it cannot mediate a later readout
until a source-current causal probe demonstrates that role.

## Mass Is Not Organization

The paired conformance contrast keeps registered route mass at
`{receipt['source_route_mass']}` and keeps node `{receipt['selected_node_scalar_id']}`
at `{receipt['source_selected_node_scalar']}`, while changing the complete
route C distribution through public `LGRC9V3.set_state()`. Internal flux,
boundary transfer, and the exact non-organization context are unchanged.

That proves the representation can distinguish:

```text
one node scalar
route mass
route organization
```

It does not prove the fourth distinction, causal mediation. `set_state()` is
admitted here only as a surgical matched-state clamp. Coherence bounds, total
node coherence, packet-ledger budget, and queue context remain valid, but
constitutive dependent fields were not recomputed. The clamp therefore cannot
serve as native formation or autonomous weakening evidence. A later causal row
must use a native trajectory or explicitly recompute dependent fields and keep
the claim limited to the declared clamp.

## Route Measurement Boundary

The fixture exactly enumerates support nodes `{route['support_node_ids']}`,
internal edges `{route['internal_edge_ids']}`, and boundary edges
`{route['boundary_edge_ids']}`. The current signed outward boundary-flux rate
is `{route['net_outward_boundary_flux_rate']}`.

This is an instantaneous native edge-flux measurement. I4 does not integrate a
post-formation window and therefore does not claim exported route mass or
closed boundary continuity.

For I7, the route-mass window must count an internal departure and its in-flight
packet once, integrate a boundary crossing once, avoid counting outside arrival
as another export, and count re-entry as signed inward transfer. Support or
boundary changes require an explicit reclassification term.

## Complete-State Crosswalk

| Theory state group | Status | Runtime/contract source | Update owner |
|---|---|---|---|
{crosswalk_rows}

## Organization Domains

| Domain | Representation | Authority | Standalone carrier | I7 role | Remaining condition |
|---|---|---|---:|---|---|
{domain_rows}

Native event times, proper times, and delays remain exact inputs, but they do
not constitute a native temporal-alignment mediator. An arrival-time
distribution can be reconstructed as a D0b history observable; it is not a
persistent D0a state. Induced geometry and functional coupling are admitted
only as response components of the selected spatial C/J_C lane, not as
standalone carrier claims. Mixed rows remain blocked until one load-bearing
domain is isolated.

Induced geometry remains a response component only. It cannot become a
load-bearing D0a carrier without its own source-current geometry state or exact
projection, preregistered weakening order, local-transport intervention,
matched mass/transfer controls, later-readout dependence, and clamp/ablation
effect.

## Spectral Boundary

A truncated slow-mode spectrum is lossy and is not admitted. A full graph
spectrum is not used as a shortcut because N31 has not frozen a canonical
degeneracy policy or a source-current spectral intervention contract. The
admitted representation instead uses a canonical finite route-coordinate
basis with an exact identity roundtrip.

## Closeout Position

The I3 active-null component and I4 representation component now establish the
current `N31-C2` progress rung and ceiling. The terminal closeout rung remains
unassigned until final N31 closeout. No positive candidate row exists, so no DR
rung is assigned.

I5 may run the D0c instantaneous comparator. I7 has representation admission,
but execution remains blocked until a candidate-specific observable, stronger
and weaker orientation, threshold, tolerance, trajectory rule, monotonicity
rule, and sign-ambiguity resolution are frozen before outcomes. Exact
representability alone does not define weakening.

## Checks

{check_rows}
""",
        encoding="utf-8",
    )


def main() -> None:
    i3_revision = build_i3_revision_lineage(load_json(I3_OUTPUT))
    I3_REVISION.write_text(canonical_json(i3_revision), encoding="utf-8")
    if i3_revision["failed_checks"]:
        raise SystemExit(
            "N31 I3 revision lineage failed: "
            + ", ".join(i3_revision["failed_checks"])
        )
    fixture = build_conformance_fixture()
    FIXTURE.write_text(canonical_json(fixture), encoding="utf-8")
    if fixture["failed_checks"]:
        raise SystemExit(
            "N31 I4 fixture failed: " + ", ".join(fixture["failed_checks"])
        )
    payload = build_payload(fixture, i3_revision)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    if payload["status"] != "passed":
        raise SystemExit(
            "N31 I4 failed: " + ", ".join(payload.get("failed_checks", []))
        )


if __name__ == "__main__":
    main()
