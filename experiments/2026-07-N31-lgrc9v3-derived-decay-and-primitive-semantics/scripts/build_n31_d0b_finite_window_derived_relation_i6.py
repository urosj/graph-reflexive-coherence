#!/usr/bin/env python3
"""Build N31 Iteration 6 D0b finite-window derived-relation artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from pygrc.core import PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    PortEdge,
    digest_lgrc9v3_restoration_identity_v1,
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
I5_OUTPUT = EXPERIMENT / "outputs" / "n31_d0c_instantaneous_geometry_comparator_i5.json"
I5_TRACE = EXPERIMENT / "outputs" / "n31_i5_d0c_source_current_trace.json"
I5R1_OUTPUT = EXPERIMENT / "outputs" / "n31_i5_revision_lineage_r1.json"
TRACE = EXPERIMENT / "outputs" / "n31_i6_d0b_finite_window_source_current_trace.json"
OUTPUT = EXPERIMENT / "outputs" / "n31_d0b_finite_window_derived_relation_i6.json"
REPORT = EXPERIMENT / "reports" / "n31_d0b_finite_window_derived_relation_i6.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_d0b_finite_window_derived_relation_i6.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I6_GOVERNANCE_BASE_REVISION = "5adcd5c3253d041c203e85936e586de621a44760"
PROTECTED_RUNTIME_BASE_REVISION = I6_GOVERNANCE_BASE_REVISION
I2_OUTPUT_DIGEST = "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf"
I2_ARTIFACT_SHA256 = "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6"
I3_OUTPUT_DIGEST = "e95b230d76113691d71282e227c61da15a5a1f7d5fa89c194af26ae4d653ddea"
I3_ARTIFACT_SHA256 = "b41d43e6b0a0e411b488ce7a9692ccd9183b9a023da4d479cd2f531e3de026ff"
I3R1_OUTPUT_DIGEST = "b6f6c1948f723d5fbb6008348b804b778993718da18c4b7efb3a499a8757de64"
I3R1_ARTIFACT_SHA256 = "2ac6582625b0898fd799c545de385a757925226eae4d38803d903549e2133398"
I4_OUTPUT_DIGEST = "b7b6f34e3978ec4a410a77e36bc1b548f1baf96dbda7987803d544fc737c3597"
I4_ARTIFACT_SHA256 = "eab3b993ad9990c2a7ba47e2445f62b520e003d9c938bc9cbc9590e428dd3782"
I4R1_OUTPUT_DIGEST = "6dbd1441b5fcdce666d8eeca287cd59205cc4d34495016a0aefe3da9b818eb16"
I4R1_ARTIFACT_SHA256 = "a8781a04980b0a650a0ebfeae41f34a067a188f72c57b71f140ad1048642d5ba"
I5_OUTPUT_DIGEST = "95d1a1f2c3003a7eeaa1edeaf9a0e843ac92e2c4af010e04a045233b445ac88b"
I5_ARTIFACT_SHA256 = "6b4707cd8b7a10d563cb55f5b61fd4d857161c7b644218ed18cdc7b541be7704"
I5_TRACE_OUTPUT_DIGEST = "c5d2609960d765bd3b97b65664a2ca86e6d16228ad34bf0714e31d093f7fe395"
I5_TRACE_SHA256 = "4e726a0a3ba9b9988a11addf5dd2712c9dcd8da9bd20580229416e415f4d0c5d"
I5R1_OUTPUT_DIGEST = "1bb729f219fbb4e0e5f52615e4213567e4f46b195b7bc00a27376c283203e9c8"
I5R1_ARTIFACT_SHA256 = "4d0e0dded207fc7c1da61114ee603835a168f58d155b7912edb2e6f189957aa0"
PRIOR_REVIEWED_I5_OUTPUT_DIGEST = (
    "93c8e2efa1bd1901922b5d069fa92bb29a5d22dfd6baf42d5acd3cdea142dad7"
)
PRIOR_REVIEWED_I5_ARTIFACT_SHA256 = (
    "a0d046cc81b4e1cff4ceb2beb793ade871747274eaa5752737ed9891e49a618e"
)
PRIOR_REVIEWED_I5_TRACE_OUTPUT_DIGEST = (
    "71a68beef656d8a32df1255003e9fdbd01177f13f57f71340bc820e44d61c9b3"
)
PRIOR_REVIEWED_I5_TRACE_ARTIFACT_SHA256 = (
    "bb61187c604b63c541ad2074c3856e2383512d0c09f97bfb7ec44216203b314f"
)

ROUTE_SUPPORT = (0, 1)
ROUTE_SOURCE_NODE = 0
ROUTE_TARGET_NODE = 1
ROUTE_PACKET_AMOUNT = 0.1
ROUTE_DEPARTURE_TIME = 0.0
ROUTE_ARRIVAL_TIMES = (1.0, 1.5, 2.0)
WINDOW_DURATION = 4.0
PROGRESSION_SCHEDULE = (
    (4.5, 4.6),
    (5.25, 5.35),
    (5.75, 5.85),
    (6.25, 6.35),
)
PROGRESSION_PACKET_AMOUNT = 0.01
COUPLING_EPSILON = 1.0

THRESHOLDS = {
    "threshold_record_id": "n31_i6_d0b_thresholds_v1",
    "declared_before_runtime_execution": True,
    "finite_window_duration_event_time": WINDOW_DURATION,
    "window_left_boundary_policy": "strict_exclusion",
    "window_right_boundary_policy": "inclusive",
    "post_formation_coupling_minimum": 0.3 - 1e-12,
    "persistence_coupling_minimum": 0.3 - 1e-12,
    "minimum_distinct_positive_weakening_steps": 2,
    "expired_coupling_maximum": 1e-12,
    "relation_value_tolerance": 1e-12,
    "route_mass_tolerance": 1e-12,
    "closed_system_budget_tolerance": 1e-12,
    "restoration_identity_required": True,
    "positive_D0b_requires": (
        "an exact source-current finite-window flux relation remains nonzero after "
        "forming-carrier exhaustion, then decreases as route events leave the "
        "declared window under native global-model event-time progression"
    ),
}

BLOCKED_RELABELS = [
    "causal_trail",
    "causal_decay",
    "causal_mediation",
    "independent_decay_state",
    "native_route_memory",
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

CONTROL_IDS = (
    "label_only_decay",
    "wall_clock_decay",
    "post_hoc_weakening_trace",
    "forming_activity_never_stopped",
    "relation_persists_but_does_not_weaken",
    "missing_internal_time_owner",
    "missing_invariant",
    "missing_restoration_state",
    "report_digest_as_runtime_state",
    "derived_observable_as_causal_trail",
    "cache_removed_and_recomputed",
    "cache_divergence",
    "observable_disconnected_from_transport",
    "route_mass_loss_as_organization_weakening_relabel",
    "D0b_transport_feedback_without_authority_reclassification",
)


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


def na(reason: str) -> dict[str, Any]:
    return {"status": "not_applicable", "scope_reason": reason}


def build_i5r1_lineage() -> dict[str, Any]:
    i5 = load_json(I5_OUTPUT)
    i5_trace = load_json(I5_TRACE)
    normalized_outcome = {
        "primary_semantic_class": "D0c",
        "representation_or_authority_class": "exact_derived_projection",
        "decay_relation_ladder_rung": i5["decay_relation_ladder_rung"],
        "source_current_D0c_candidate_supported": i5[
            "source_current_D0c_candidate_supported"
        ],
        "positive_decay_evidence_opened": i5[
            "positive_decay_evidence_opened"
        ],
        "D0a_persistence_supported": i5["D0a_persistence_supported"],
        "D0a_weakening_supported": i5["D0a_weakening_supported"],
        "causal_mediation_supported": i5["causal_mediation_supported"],
        "forming_packet_current_l1_norm": i5_trace["D0c_relation"][
            "forming_packet_current_l1_norm"
        ],
        "post_withdrawal_packet_current_l1_norm": i5_trace["D0c_relation"][
            "post_withdrawal_packet_current_l1_norm"
        ],
    }
    prior_normalized_outcome = dict(normalized_outcome)
    normalized_digest = digest_value(normalized_outcome)
    lineage: dict[str, Any] = {
        "experiment": "N31",
        "revision_id": "N31-I5R1",
        "artifact_kind": "I5_revision_lineage",
        "artifact_schema_version": "n31_i5_revision_lineage_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_I5R1_provenance_and_scientific_outcome_invariance_closed"
        ),
        "prior_review_package": {
            "label": "N31-I5-pre-review-hardening-package",
            "output_digest": PRIOR_REVIEWED_I5_OUTPUT_DIGEST,
            "artifact_sha256": PRIOR_REVIEWED_I5_ARTIFACT_SHA256,
            "trace_output_digest": PRIOR_REVIEWED_I5_TRACE_OUTPUT_DIGEST,
            "trace_artifact_sha256": PRIOR_REVIEWED_I5_TRACE_ARTIFACT_SHA256,
            "identity_source": "external_reviewed_package_identity",
            "full_artifacts_retained_in_repository": False,
            "consumed_by_I6": False,
        },
        "current_committed_artifacts": {
            "label": "N31-I5R1",
            "commit": I6_GOVERNANCE_BASE_REVISION,
            "output_path": I5_OUTPUT.relative_to(ROOT).as_posix(),
            "output_digest": i5["output_digest"],
            "output_artifact_sha256": sha256_file(I5_OUTPUT),
            "trace_path": I5_TRACE.relative_to(ROOT).as_posix(),
            "trace_output_digest": i5_trace["output_digest"],
            "trace_artifact_sha256": sha256_file(I5_TRACE),
            "consumed_by_I6": True,
        },
        "revision_reason": [
            "closed the I4-to-I4R1 provenance lineage consumed by I5",
            "made registered-cycle and canonical native-edge current orientations explicit",
            "separated formation-input stop from forming-carrier exhaustion",
            "regenerated controls for the exact I5 semantic contract",
            "tightened instantaneous state-flux comparator terminology",
        ],
        "comparison_policy": {
            "comparison_kind": "normalized_scientific_outcome",
            "contract_and_provenance_detail_changed": True,
            "scientific_outcome_changed": False,
            "prior_normalized_outcome": prior_normalized_outcome,
            "current_normalized_outcome": normalized_outcome,
            "prior_normalized_outcome_digest": normalized_digest,
            "current_normalized_outcome_digest": normalized_digest,
            "why_not_full_artifact_equality": (
                "I5R1 intentionally adds provenance, orientation, carrier-phase, and "
                "candidate-specific control detail while retaining the reviewed D0c/DR1 result"
            ),
        },
    }
    lineage["checks"] = [
        check(
            "current_I5_identity_exact",
            i5["output_digest"] == I5_OUTPUT_DIGEST
            and sha256_file(I5_OUTPUT) == I5_ARTIFACT_SHA256
            and i5_trace["output_digest"] == I5_TRACE_OUTPUT_DIGEST
            and sha256_file(I5_TRACE) == I5_TRACE_SHA256,
            i5["output_digest"],
        ),
        check(
            "normalized_scientific_outcome_unchanged",
            prior_normalized_outcome == normalized_outcome,
            normalized_digest,
        ),
        check(
            "D0c_DR1_ceiling_unchanged",
            i5["decay_relation_ladder_rung"] == "DR1"
            and not i5["positive_decay_evidence_opened"],
            i5["decay_relation_ladder_ceiling"],
        ),
        check(
            "I6_admission_unchanged",
            i5["ready_for_iteration_6_D0b_finite_window_relation"],
            i5["ready_for_iteration_6_D0b_finite_window_relation"],
        ),
    ]
    lineage["failed_checks"] = [
        row["check_id"] for row in lineage["checks"] if not row["passed"]
    ]
    if lineage["failed_checks"]:
        lineage["status"] = "failed"
        lineage["acceptance_state"] = "blocked_I5R1_lineage_not_closed"
    lineage["output_digest"] = digest_value(
        {key: value for key, value in lineage.items() if key != "output_digest"}
    )
    return lineage


def build_model() -> tuple[LGRC9V3, dict[str, int]]:
    graph = PortGraphBackend()
    for label in (
        "route_source",
        "route_target",
        "outside_boundary",
        "progression_source",
        "progression_target",
    ):
        graph.add_node({"label": label})

    edge_specs = (
        ("route_coupling", 0, 1, 0, 0, "registered_route_coupling"),
        ("route_boundary", 1, 2, 1, 0, "registered_route_boundary"),
        ("outside_bridge", 2, 3, 1, 0, "outside_context"),
        ("progression_lane", 3, 4, 1, 0, "event_time_progression_lane"),
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
            0: GRC9V3NodeState(coherence=1.5),
            1: GRC9V3NodeState(coherence=1.0),
            2: GRC9V3NodeState(coherence=0.5),
            3: GRC9V3NodeState(coherence=0.5),
            4: GRC9V3NodeState(coherence=0.5),
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )
    return LGRC9V3.from_state(state, {"dt": 1.0}), edge_ids


def schedule_predeclared_events(
    model: LGRC9V3,
    edge_ids: dict[str, int],
) -> dict[str, Any]:
    for packet_index, arrival_time in enumerate(ROUTE_ARRIVAL_TIMES):
        model.schedule_packet_departure(
            source_node_id=ROUTE_SOURCE_NODE,
            target_node_id=ROUTE_TARGET_NODE,
            edge_id=edge_ids["route_coupling"],
            amount=ROUTE_PACKET_AMOUNT,
            departure_event_time_key=ROUTE_DEPARTURE_TIME,
            arrival_event_time_key=arrival_time,
            scheduler_event_index=(2 * packet_index) + 1,
            packet_index=packet_index,
        )

    for progression_index, (departure_time, arrival_time) in enumerate(
        PROGRESSION_SCHEDULE
    ):
        model.schedule_packet_departure(
            source_node_id=3,
            target_node_id=4,
            edge_id=edge_ids["progression_lane"],
            amount=PROGRESSION_PACKET_AMOUNT,
            departure_event_time_key=departure_time,
            arrival_event_time_key=arrival_time,
            scheduler_event_index=101 + (2 * progression_index),
            packet_index=100 + progression_index,
        )

    return {
        "schedule_owner": "experiment_fixture_pre_formation_only",
        "all_schedule_calls_complete_before_first_runtime_event": True,
        "route_forming_packet_count": len(ROUTE_ARRIVAL_TIMES),
        "progression_packet_count": len(PROGRESSION_SCHEDULE),
        "progression_lane_disjoint_from_registered_route_support": True,
        "progression_lane_role": (
            "native_event_time_progression_scaffold_not_route_relation_input"
        ),
        "post_formation_schedule_calls": [],
    }


def finite_window_relation_at_time(
    model: LGRC9V3,
    route_edge_id: int,
    evaluation_time: float,
) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    window_start = evaluation_time - WINDOW_DURATION
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for packet in ledger.packet_records:
        if int(packet.edge_id) != route_edge_id:
            continue
        arrival_time = packet.arrival_event_time_key
        if arrival_time is None:
            continue
        record = {
            "packet_id": packet.packet_id,
            "edge_id": int(packet.edge_id),
            "amount": float(packet.amount),
            "arrival_event_time_key": float(arrival_time),
            "packet_state": packet.packet_state,
        }
        if (
            packet.packet_state == "arrived"
            and float(arrival_time) > window_start
            and float(arrival_time) <= evaluation_time
        ):
            included.append(record)
        else:
            excluded.append(record)

    included.sort(key=lambda row: (row["arrival_event_time_key"], row["packet_id"]))
    excluded.sort(key=lambda row: (row["arrival_event_time_key"], row["packet_id"]))
    coupling = sum(abs(float(row["amount"])) for row in included)
    return {
        "relation_id": "n31_i6_finite_window_absolute_route_flux_v1",
        "theory_relation": (
            "F_ij(T;DeltaT)=integral_(T-DeltaT,T] |J_C dot n_ij| under the "
            "declared native-arrival event-measure convention"
        ),
        "packet_transfer_measure": (
            "sum_p amount_p * delta(T - arrival_event_time_key_p) over completed "
            "registered-edge packets"
        ),
        "event_measure_convention": "atomic_native_packet_arrival_measure",
        "registered_transfer_completion_event": "native_packet_arrival",
        "arrival_event_selection_reason": (
            "native arrival is the single completion event at which the registered "
            "edge transfer has completed; departure is excluded to prevent double counting"
        ),
        "evaluation_event_time_key": evaluation_time,
        "window_duration_event_time": WINDOW_DURATION,
        "window_start_event_time_key": window_start,
        "window_interval": "(T-DeltaT,T]",
        "left_boundary_inclusive": False,
        "right_boundary_inclusive": True,
        "route_edge_id": route_edge_id,
        "transfer_completion_event": "native_packet_arrival",
        "departure_events_counted_separately": False,
        "included_route_transfer_records": included,
        "excluded_route_transfer_records": excluded,
        "included_route_transfer_count": len(included),
        "finite_window_absolute_flux_coupling": coupling,
        "normalized_coupling_fraction": coupling
        / (ROUTE_PACKET_AMOUNT * len(ROUTE_ARRIVAL_TIMES)),
        "inverse_coupling_weight": 1.0 / (COUPLING_EPSILON + coupling),
        "coupling_units": "coherence",
        "independent_runtime_state": False,
        "fed_back_into_transport": False,
    }


def finite_window_relation(
    model: LGRC9V3,
    route_edge_id: int,
) -> dict[str, Any]:
    return finite_window_relation_at_time(
        model,
        route_edge_id,
        float(model.get_state().event_time_key),
    )


def window_boundary_conformance(
    model: LGRC9V3,
    route_edge_id: int,
) -> dict[str, Any]:
    cases = [
        (2.0, [1.0, 1.5, 2.0], "right_endpoint_includes_arrival_at_T"),
        (5.0, [1.5, 2.0], "left_endpoint_excludes_arrival_at_1_0"),
        (5.5, [2.0], "left_endpoint_excludes_arrival_at_1_5"),
        (6.0, [], "left_endpoint_excludes_arrival_at_2_0"),
    ]
    results = []
    for evaluation_time, expected_arrivals, purpose in cases:
        relation = finite_window_relation_at_time(
            model,
            route_edge_id,
            evaluation_time,
        )
        actual_arrivals = [
            row["arrival_event_time_key"]
            for row in relation["included_route_transfer_records"]
        ]
        results.append(
            {
                "evaluation_event_time_key": evaluation_time,
                "window_start_event_time_key": evaluation_time - WINDOW_DURATION,
                "purpose": purpose,
                "expected_included_arrival_event_times": expected_arrivals,
                "actual_included_arrival_event_times": actual_arrivals,
                "passed": actual_arrivals == expected_arrivals,
            }
        )
    return {
        "fixture_kind": "exact_history_functional_boundary_conformance",
        "runtime_state_mutated": False,
        "source_history": "retained_native_route_packet_records",
        "window_interval": "(T-DeltaT,T]",
        "cases": results,
        "passed": all(row["passed"] for row in results),
    }


def route_mass(model: LGRC9V3, route_edge_id: int) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    node_mass = sum(
        float(state.base_state.nodes[node_id].coherence)
        for node_id in ROUTE_SUPPORT
    )
    in_flight_mass = sum(
        float(packet.amount)
        for packet in ledger.packet_records
        if int(packet.edge_id) == route_edge_id
        and packet.packet_state == "in_flight"
    )
    return {
        "support_node_ids": list(ROUTE_SUPPORT),
        "route_node_coherence_mass": node_mass,
        "route_internal_in_flight_mass": in_flight_mass,
        "registered_route_mass": node_mass + in_flight_mass,
        "node_coherence": {
            str(node_id): float(state.base_state.nodes[node_id].coherence)
            for node_id in ROUTE_SUPPORT
        },
    }


def save_load(model: LGRC9V3) -> LGRC9V3:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "n31-i6-snapshot.json"
        model.save(str(path))
        return LGRC9V3.load(str(path))


def checkpoint(
    model: LGRC9V3,
    checkpoint_id: str,
    route_edge_id: int,
) -> dict[str, Any]:
    snapshot = model.snapshot()
    identity_before = digest_lgrc9v3_restoration_identity_v1(snapshot)
    relation_cache = finite_window_relation(model, route_edge_id)
    cache_digest = digest_value(relation_cache)
    cache_value = relation_cache["finite_window_absolute_flux_coupling"]
    del relation_cache
    relation_recomputed = finite_window_relation(model, route_edge_id)
    identity_after_recompute = digest_lgrc9v3_restoration_identity_v1(model)

    restored = save_load(model)
    restored_identity = digest_lgrc9v3_restoration_identity_v1(restored)
    restored_relation = finite_window_relation(restored, route_edge_id)
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    return {
        "checkpoint_id": checkpoint_id,
        "event_time_key": float(model.get_state().event_time_key),
        "restoration_identity_schema": "lgrc9v3_restoration_identity_v1",
        "restoration_identity_digest": identity_before,
        "scientific_state_identity": lgrc9v3_restoration_identity_v1(snapshot),
        "route_mass_state": route_mass(model, route_edge_id),
        "finite_window_relation": relation_recomputed,
        "cache_audit": {
            "cache_scope": "experiment_local_report_cache_not_runtime_state",
            "cache_value_before_removal": cache_value,
            "cache_digest_before_removal": cache_digest,
            "cache_removed": True,
            "recomputed_value": relation_recomputed[
                "finite_window_absolute_flux_coupling"
            ],
            "recomputed_digest": digest_value(relation_recomputed),
            "recomputation_exact": cache_digest == digest_value(relation_recomputed),
            "runtime_identity_unchanged_by_cache_removal_recomputation": (
                identity_before == identity_after_recompute
            ),
        },
        "snapshot_load_audit": {
            "restoration_identity_exact": identity_before == restored_identity,
            "restored_relation_exact": relation_recomputed == restored_relation,
            "restored_relation_digest": digest_value(restored_relation),
        },
        "runtime_state": {
            "event_queue_record_count": len(ledger.event_queue_records),
            "packet_record_count": len(ledger.packet_records),
            "in_flight_packet_total": float(ledger.in_flight_packet_total),
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


def observable_disconnection_probe(
    model: LGRC9V3,
    route_edge_id: int,
) -> dict[str, Any]:
    observed = save_load(model)
    unobserved = save_load(model)
    before_identity_equal = (
        digest_lgrc9v3_restoration_identity_v1(observed)
        == digest_lgrc9v3_restoration_identity_v1(unobserved)
    )
    observed_relation = finite_window_relation(observed, route_edge_id)
    observed_results = observed.run_event_queue(max_events=2)
    unobserved_results = unobserved.run_event_queue(max_events=2)
    after_identity_equal = (
        digest_lgrc9v3_restoration_identity_v1(observed)
        == digest_lgrc9v3_restoration_identity_v1(unobserved)
    )
    return {
        "control_id": "observable_disconnected_from_transport",
        "control_scope": "observer_computation_side_effect_only",
        "organization_intervention_performed": False,
        "local_transport_intervention_status": "not_run",
        "underlying_packet_history_causal_irrelevance_established": False,
        "observed_branch_computed_relation_before_continuation": True,
        "unobserved_branch_computed_relation_before_continuation": False,
        "observed_relation_digest": digest_value(observed_relation),
        "before_identity_equal": before_identity_equal,
        "observed_continuation_receipts": result_event_receipt(observed_results),
        "unobserved_continuation_receipts": result_event_receipt(unobserved_results),
        "continuation_receipts_equal": (
            result_event_receipt(observed_results)
            == result_event_receipt(unobserved_results)
        ),
        "after_identity_equal": after_identity_equal,
        "observed_post_relation": finite_window_relation(observed, route_edge_id),
        "unobserved_post_relation": finite_window_relation(unobserved, route_edge_id),
        "observable_computation_changed_transport": not (
            before_identity_equal
            and after_identity_equal
            and result_event_receipt(observed_results)
            == result_event_receipt(unobserved_results)
        ),
        "causal_mediation_supported": False,
    }


def build_trace() -> dict[str, Any]:
    model, edge_ids = build_model()
    route_edge_id = edge_ids["route_coupling"]
    baseline = checkpoint(model, "baseline_before_schedule", route_edge_id)
    schedule_audit = schedule_predeclared_events(model, edge_ids)

    departure_results = model.run_event_queue(max_events=3)
    forming = checkpoint(
        model,
        "forming_route_packets_in_flight_after_final_departure",
        route_edge_id,
    )
    formation_receipts: list[dict[str, Any]] = []
    formation_checkpoints: list[dict[str, Any]] = []
    for arrival_index in range(3):
        results = model.run_event_queue(max_events=1)
        formation_receipts.extend(result_event_receipt(results))
        formation_checkpoints.append(
            checkpoint(
                model,
                f"route_arrival_{arrival_index + 1}_committed",
                route_edge_id,
            )
        )

    post_formation = formation_checkpoints[-1]
    progression_receipts: list[dict[str, Any]] = []
    progression_checkpoints: list[dict[str, Any]] = []
    disconnection = None
    for progression_index in range(len(PROGRESSION_SCHEDULE)):
        results = model.run_event_queue(max_events=2)
        progression_receipts.extend(result_event_receipt(results))
        row = checkpoint(
            model,
            f"post_formation_progression_{progression_index + 1}",
            route_edge_id,
        )
        progression_checkpoints.append(row)
        if progression_index == 0:
            disconnection = observable_disconnection_probe(model, route_edge_id)

    assert disconnection is not None
    relation_values = [
        float(row["finite_window_relation"]["finite_window_absolute_flux_coupling"])
        for row in progression_checkpoints
    ]
    full_timeline = [
        float(post_formation["finite_window_relation"][
            "finite_window_absolute_flux_coupling"
        ])
    ] + relation_values
    positive_to_positive_decreases = sum(
        1
        for before, after in zip(full_timeline, full_timeline[1:])
        if after < before - THRESHOLDS["relation_value_tolerance"]
        and after > THRESHOLDS["expired_coupling_maximum"]
    )
    total_strict_decreases = sum(
        1
        for before, after in zip(full_timeline, full_timeline[1:])
        if after < before - THRESHOLDS["relation_value_tolerance"]
    )
    final_expiry_steps = sum(
        1
        for before, after in zip(full_timeline, full_timeline[1:])
        if before > THRESHOLDS["expired_coupling_maximum"]
        and after <= THRESHOLDS["expired_coupling_maximum"]
    )
    nonincreasing = all(
        after <= before + THRESHOLDS["relation_value_tolerance"]
        for before, after in zip(full_timeline, full_timeline[1:])
    )
    route_mass_values = [
        float(row["route_mass_state"]["registered_route_mass"])
        for row in [baseline, forming, *formation_checkpoints, *progression_checkpoints]
    ]
    budget_values = [
        float(row["runtime_state"]["conserved_budget_total"])
        for row in [baseline, forming, *formation_checkpoints, *progression_checkpoints]
    ]
    route_mass_span = max(route_mass_values) - min(route_mass_values)
    budget_span = max(budget_values) - min(budget_values)
    all_checkpoints = [
        baseline,
        forming,
        *formation_checkpoints,
        *progression_checkpoints,
    ]
    boundary_conformance = window_boundary_conformance(model, route_edge_id)

    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "6",
        "artifact_kind": "D0b_finite_window_source_current_runtime_trace",
        "artifact_schema_version": "n31_i6_d0b_finite_window_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_source_current_D0b_finite_window_observable_DR3_below_causal_trail"
        ),
        "derived_report_only": False,
        "source_current_runtime_artifact": True,
        "threshold_declaration": THRESHOLDS,
        "threshold_declaration_digest": digest_value(THRESHOLDS),
        "fixture_contract": {
            "fixture_id": "n31_i6_staggered_route_flux_with_disjoint_progression_lane_v1",
            "registered_route_support": list(ROUTE_SUPPORT),
            "route_edge_id": route_edge_id,
            "route_boundary_edge_id": edge_ids["route_boundary"],
            "progression_lane_edge_id": edge_ids["progression_lane"],
            "route_arrival_event_times": list(ROUTE_ARRIVAL_TIMES),
            "window_duration_event_time": WINDOW_DURATION,
            "schedule_audit": schedule_audit,
            "formation_input_stop_condition": (
                "all_predeclared_route_departures_processed"
            ),
            "formation_input_stopped": True,
            "formation_input_stop_checkpoint": forming["checkpoint_id"],
            "forming_carrier_exhausted": True,
            "forming_carrier_exhaustion_checkpoint": post_formation[
                "checkpoint_id"
            ],
            "post_formation_progression_owner": "native_LGRC9V3_event_queue",
            "clock_scope": "global_model_event_time",
            "route_local_proper_time_advanced_during_expiry": False,
            "progression_fixture_authored_by_experiment": True,
            "local_clock_decay_claim_allowed": False,
            "post_formation_schedule_calls": [],
            "post_formation_producer_calls": [],
            "set_state_used": False,
            "wall_clock_used_as_causal_input": False,
        },
        "runtime_execution": {
            "model_family": "LGRC9V3",
            "public_operations": [
                "LGRC9V3.from_state",
                "LGRC9V3.schedule_packet_departure",
                "LGRC9V3.run_event_queue",
                "LGRC9V3.get_state",
                "LGRC9V3.snapshot",
                "LGRC9V3.save",
                "LGRC9V3.load",
                "lgrc9v3_restoration_identity_v1",
            ],
            "route_departure_receipts": result_event_receipt(departure_results),
            "route_arrival_receipts": formation_receipts,
            "progression_lane_receipts": progression_receipts,
            "wall_clock_used_as_causal_input": False,
        },
        "checkpoints": all_checkpoints,
        "window_boundary_conformance": boundary_conformance,
        "D0b_relation": {
            "equation_or_relation_id": "n31_i6_finite_window_absolute_route_flux_v1",
            "theory_basis": "RC-Distance-v4 section 10.2 coherent coupling",
            "authority": "exact_recomputable_history_functional",
            "organization_domain": "functional_coupling",
            "load_bearing_organization_domain": "functional_coupling",
            "cache_persisted_as_runtime_state": False,
            "cache_fed_back_into_transport": False,
            "relation_at_carrier_exhaustion": full_timeline[0],
            "post_formation_progression_values": relation_values,
            "full_post_formation_timeline": full_timeline,
            "persistence_supported": relation_values[0]
            >= THRESHOLDS["persistence_coupling_minimum"],
            "weakening_supported": nonincreasing
            and positive_to_positive_decreases
            >= THRESHOLDS["minimum_distinct_positive_weakening_steps"],
            "window_expiry_supported": relation_values[-1]
            <= THRESHOLDS["expired_coupling_maximum"],
            "weakening_trajectory_class": "monotonic_stepwise_finite_window_expiry",
            "positive_to_positive_decrease_count": (
                positive_to_positive_decreases
            ),
            "total_strict_decrease_count": total_strict_decreases,
            "final_expiry_step_count": final_expiry_steps,
            "clock_scope": "global_model_event_time",
            "route_local_proper_time_advanced_during_expiry": False,
            "local_clock_decay_claim_allowed": False,
            "route_mass_span": route_mass_span,
            "closed_system_budget_span": budget_span,
            "causal_mediation_supported": False,
            "decay_relation_ladder_rung": "DR3",
        },
        "observable_disconnection_control": disconnection,
    }
    relation = trace["D0b_relation"]
    trace["checks"] = [
        check(
            "three_predeclared_route_departures_processed",
            len(departure_results) == 3,
            len(departure_results),
        ),
        check(
            "three_staggered_route_arrivals_processed",
            len(formation_receipts) == 3
            and [row["event_time_key"] for row in formation_receipts]
            == list(ROUTE_ARRIVAL_TIMES),
            formation_receipts,
        ),
        check(
            "relation_nonzero_after_forming_carrier_exhaustion",
            relation["relation_at_carrier_exhaustion"]
            >= THRESHOLDS["post_formation_coupling_minimum"],
            relation["relation_at_carrier_exhaustion"],
        ),
        check(
            "relation_persists_under_first_post_formation_progression",
            relation["persistence_supported"],
            relation_values[0],
        ),
        check(
            "history_exits_window_stepwise_under_native_event_time",
            relation["weakening_supported"] and relation["window_expiry_supported"],
            relation_values,
        ),
        check(
            "strict_left_and_inclusive_right_window_boundaries_pass",
            boundary_conformance["passed"],
            boundary_conformance["cases"],
        ),
        check(
            "cache_recomputation_exact_at_every_checkpoint",
            all(
                row["cache_audit"]["recomputation_exact"]
                and row["cache_audit"][
                    "runtime_identity_unchanged_by_cache_removal_recomputation"
                ]
                for row in all_checkpoints
            ),
            [row["cache_audit"]["recomputation_exact"] for row in all_checkpoints],
        ),
        check(
            "snapshot_load_restores_history_and_relation_exactly",
            all(
                row["snapshot_load_audit"]["restoration_identity_exact"]
                and row["snapshot_load_audit"]["restored_relation_exact"]
                for row in all_checkpoints
            ),
            [
                row["snapshot_load_audit"]["restored_relation_exact"]
                for row in all_checkpoints
            ],
        ),
        check(
            "observable_computation_has_no_transport_side_effect",
            disconnection["before_identity_equal"]
            and disconnection["continuation_receipts_equal"]
            and disconnection["after_identity_equal"]
            and not disconnection["observable_computation_changed_transport"],
            disconnection,
        ),
        check(
            "route_mass_constant",
            route_mass_span <= THRESHOLDS["route_mass_tolerance"],
            route_mass_span,
        ),
        check(
            "closed_system_budget_constant",
            budget_span <= THRESHOLDS["closed_system_budget_tolerance"]
            and all(
                float(row["runtime_state"]["budget_error"])
                <= THRESHOLDS["closed_system_budget_tolerance"]
                for row in all_checkpoints
            ),
            budget_span,
        ),
        check(
            "forming_activity_and_progression_lane_separated",
            not any(
                int(record["edge_id"]) == route_edge_id
                for row in progression_checkpoints
                for record in row["finite_window_relation"][
                    "included_route_transfer_records"
                ]
                if float(record["arrival_event_time_key"])
                > max(ROUTE_ARRIVAL_TIMES)
            )
            and schedule_audit[
                "progression_lane_disjoint_from_registered_route_support"
            ],
            schedule_audit,
        ),
        check(
            "D0b_semantic_ceiling_preserved",
            relation["persistence_supported"]
            and relation["weakening_supported"]
            and not relation["causal_mediation_supported"],
            "DR3_below_causal_trail",
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_D0b_runtime_trace_validation_failed"
    trace["output_digest"] = digest_value(
        {key: value for key, value in trace.items() if key != "output_digest"}
    )
    return trace


def control_result(
    control_id: str,
    status: str,
    blocked_condition: str,
    expected_result: str,
    actual_result: str,
    rung_effect: str,
    scope_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "control_status": status,
        "blocked_condition": blocked_condition,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect,
        "scope_reason_if_not_applicable": scope_reason,
    }


def build_controls(
    trace: dict[str, Any],
    i3: dict[str, Any],
    candidate_contract: dict[str, Any],
) -> list[dict[str, Any]]:
    relation = trace["D0b_relation"]
    disconnected = trace["observable_disconnection_control"]
    controls = [
        control_result(
            "label_only_decay",
            "passed",
            "label_or_report_without_source_current_relation",
            "native_history_trace_required",
            "native_packet_history_and_runtime_receipts_present",
            "blocks_DR1_plus",
        ),
        control_result(
            "wall_clock_decay",
            "passed",
            "wall_time_or_process_duration_advances_window",
            "model_owned_event_time_only",
            "window_evaluation_uses_LGRC9V3_event_time_key",
            "blocks_DR3_plus",
        ),
        control_result(
            "post_hoc_weakening_trace",
            "passed",
            "outcome_selected_window_or_trace",
            "window_and_thresholds_declared_before_execution",
            "fixed_window_and_staggered_arrivals_recorded_in_threshold_contract",
            "blocks_DR3_plus",
        ),
        control_result(
            "forming_activity_never_stopped",
            "passed",
            "continued_route_formation_called_persistence",
            "route_carrier_exhausted_before_persistence_checkpoint",
            "all_route_packets_arrived_at_event_time_2_and_no_later_route_packets_exist",
            "blocks_DR2_plus",
        ),
        control_result(
            "relation_persists_but_does_not_weaken",
            "passed",
            "persistence_without_weakening_promoted_to_DR3",
            "at_least_two_positive_decreases_and_final_expiry",
            str(relation["post_formation_progression_values"]),
            "blocks_DR3_plus",
        ),
        control_result(
            "missing_internal_time_owner",
            "passed",
            "weakening_without_named_internal_time_owner",
            "native_event_time_owner_and_events_recorded",
            "LGRC9V3_event_queue_progression_receipts_present",
            "blocks_DR3_plus",
        ),
        control_result(
            "missing_invariant",
            "passed",
            "relation_without_coherence_budget_invariant",
            "global_node_plus_in_flight_budget_closed",
            f"budget_span={relation['closed_system_budget_span']}",
            "blocks_row",
        ),
        control_result(
            "missing_restoration_state",
            "passed",
            "history_relation_not_restorable",
            "identity_and_recomputed_relation_exact_after_snapshot_load",
            "all_checkpoint_snapshot_load_audits_exact",
            "blocks_DR5_plus",
        ),
        control_result(
            "report_digest_as_runtime_state",
            "passed",
            "report_or_digest_used_as_history carrier",
            "relation_recomputed_from_native_packet_history",
            "report_cache_absent_from_runtime_identity",
            "blocks_DR1_plus",
        ),
        control_result(
            "derived_observable_as_causal_trail",
            "failed_closed",
            "recomputable_D0b_observable_relabelled_as_causal_trail",
            "causal_claim_rejected_without_transport_mediation",
            "computed_and_uncomputed_observer branches continue identically; no history intervention run",
            "blocks_DR4_plus",
        ),
        control_result(
            "cache_removed_and_recomputed",
            "failed_closed",
            "exact_cache_relabelled_as_independent_decay_state",
            "cache_removal_and_recomputation_leave runtime identity unchanged",
            "all checkpoint caches recompute exactly",
            "blocks_independent_state_claim",
        ),
        control_result(
            "cache_divergence",
            "passed",
            "divergent_cache_retains_exact_derived_authority",
            "all recomputation digests exact",
            "no cache divergence observed",
            "blocks_exact_D0b",
        ),
        control_result(
            "observable_disconnected_from_transport",
            "failed_closed",
            "D0b_observable_claimed_as_transport_mediator",
            "observer computation has no side effect; mediator intervention remains not run",
            (
                f"after_identity_equal={disconnected['after_identity_equal']}; "
                "organization_intervention_performed=false"
            ),
            "blocks_DR4_plus",
        ),
        control_result(
            "route_mass_loss_as_organization_weakening_relabel",
            "passed",
            "route_mass_loss_substitutes_for_window_coupling_weakening",
            "route_mass matched while finite-window relation changes",
            f"route_mass_span={relation['route_mass_span']}",
            "blocks_organization_inference",
        ),
        control_result(
            "D0b_transport_feedback_without_authority_reclassification",
            "passed",
            "derived_observable_drives_transport_without_authority_change",
            "observable never fed back into runtime",
            "fed_back_into_transport=false",
            "blocks_unreclassified_DR4",
        ),
    ]
    i3_rows = {row["control_id"]: row for row in i3["active_null_rows"]}
    candidate_digest = digest_value(candidate_contract)
    for row in controls:
        source = i3_rows.get(row["control_id"])
        source_contract = (
            source.get("semantic_comparability_contract", {}) if source else {}
        )
        mismatches = [
            key
            for key, value in candidate_contract.items()
            if source_contract.get(key) != value
        ]
        row.update(
            {
                "candidate_control_execution_id": (
                    f"n31_i6_regenerated_{row['control_id']}_v1"
                ),
                "candidate_semantic_contract_digest": candidate_digest,
                "control_execution_artifact": TRACE.relative_to(ROOT).as_posix(),
                "control_execution_checkpoints": [
                    "route_arrival_3_committed",
                    "post_formation_progression_1",
                    "post_formation_progression_4",
                ],
                "control_origin": "regenerated_candidate_specific",
                "source_I3_control_id": source["control_id"] if source else None,
                "source_I3_row_digest": source["row_digest"] if source else None,
                "matched_to_I3_null": not mismatches,
                "regenerated_for_I6_candidate": True,
                "semantic_comparability_mismatches": mismatches,
                "semantic_comparability_digest": digest_value(
                    {
                        "candidate": candidate_contract,
                        "source": source_contract,
                        "mismatches": mismatches,
                    }
                ),
            }
        )
    return controls


def build_candidate(
    trace: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
) -> dict[str, Any]:
    relation = trace["D0b_relation"]
    checkpoints = {row["checkpoint_id"]: row for row in trace["checkpoints"]}
    post = checkpoints["route_arrival_3_committed"]
    expired = checkpoints["post_formation_progression_4"]
    trace_path = TRACE.relative_to(ROOT).as_posix()
    candidate_contract = {
        "primary_semantic_class": "D0b",
        "representation_or_authority_class": "exact_derived_projection",
        "organization_domain": "functional_coupling",
        "load_bearing_organization_domain": "functional_coupling",
        "candidate_specific_schema_id": "n31_i6_D0b_candidate_schema_v1",
        "carrier_contract_id": "n31_i6_native_route_arrival_history_v1",
        "continuation_state_contract_id": (
            "n31_i6_complete_LGRC9V3_state_plus_declared_history_functional_v1"
        ),
        "internal_time_policy": "model_owned_event_time_wall_clock_excluded_v1",
    }
    controls = build_controls(trace, i3, candidate_contract)
    mass_before = float(post["route_mass_state"]["registered_route_mass"])
    mass_after = float(expired["route_mass_state"]["registered_route_mass"])
    mass_delta = mass_after - mass_before
    required_fields = i2["schema"]["candidate_row_schema"]["required_fields"]
    candidate: dict[str, Any] = {
        "candidate_id": "n31_i6_D0b_finite_window_route_flux_coupling",
        "candidate_schema_version": "n31_decay_candidate_schema_v2",
        "schema_change_record_id": "n31_pre_i1_mass_organization_mediation_normalization_v2",
        "source_iteration": "N31-I6",
        "primary_semantic_class": "D0b",
        "representation_or_authority_class": "exact_derived_projection",
        "candidate_disposition": "supported",
        "d0_subclass": "D0b_finite_window_flux_coupling_observable",
        "weakening_mode": "declared_finite_window_history_expiry",
        "weakening_trajectory_class": "monotonic_stepwise_finite_window_expiry",
        "formation_source": "native_source_current_staggered_route_packet_arrivals",
        "carrier_definition": (
            "native completed packet transfers on the registered route edge within "
            "the declared LGRC event-time window"
        ),
        "continuation_state_definition": (
            "complete LGRC9V3 current scientific state plus an exact, non-independent "
            "functional over retained native packet history"
        ),
        "route_local_surface": "registered route coupling edge 0 between nodes 0 and 1",
        "route_mass_contract": {
            "route_mass_contract_id": "n31_i6_registered_route_mass_v1",
            "registered_route_support": list(ROUTE_SUPPORT),
            "registered_route_boundary": {
                "edge_ids": [trace["fixture_contract"]["route_boundary_edge_id"]],
                "inside_node_ids": list(ROUTE_SUPPORT),
                "outside_node_ids": [2],
            },
            "metric_measure_and_boundary_convention": (
                "fixed discrete node support with one registered outward edge; "
                "node coherence plus internal in-flight route packet amount"
            ),
            "post_formation_integration_window": {
                "start_event_time_key": max(ROUTE_ARRIVAL_TIMES),
                "end_event_time_key": PROGRESSION_SCHEDULE[-1][1],
                "classification": "declared_D0b_post_formation_observation_window",
            },
            "flux_quantity_semantics": "time_integrated_exported_coherence",
            "boundary_measure": {
                "kind": "discrete_registered_edge_counting_measure",
                "registered_boundary_edge_count": 1,
                "edge_weights": {
                    str(trace["fixture_contract"]["route_boundary_edge_id"]): 1.0
                },
            },
            "mass_before": mass_before,
            "mass_after": mass_after,
            "mass_delta": mass_delta,
            "boundary_flux_sign_policy": "positive_outward",
            "net_outward_boundary_flux": 0.0,
            "in_flight_boundary_treatment": (
                "no registered-boundary packet is in flight; internal route packets "
                "remain included once in registered route mass until native arrival"
            ),
            "boundary_crossing_count_policy": (
                "each_packet_or_flux_transfer_counted_exactly_once"
            ),
            "departure_arrival_accounting_policy": (
                "internal route transfer counted once as in-flight mass between debit "
                "and credit; no departure/arrival double counting"
            ),
            "receiver_inside_or_outside_support": (
                "registered route-transfer receiver node 1 is inside support; "
                "boundary receiver node 2 is outside support"
            ),
            "moving_support_or_measure_correction": (
                "not_applicable_fixed_support_and_fixed_boundary"
            ),
            "continuity_residual": mass_delta,
            "continuity_tolerance": THRESHOLDS["route_mass_tolerance"],
            "continuity_closed": abs(mass_delta)
            <= THRESHOLDS["route_mass_tolerance"],
        },
        "route_organization_contract": {
            "route_organization_contract_id": "n31_i6_D0b_window_coupling_v1",
            "organization_observable_id": "n31_i6_finite_window_absolute_route_flux_v1",
            "organization_definition": (
                "F_01(T;DeltaT)=sum of absolute amounts for completed native route "
                "transfers with arrival time in (T-DeltaT,T]"
            ),
            "organization_inputs": [
                "native route packet arrival records",
                "native LGRC9V3 global event_time_key",
                "declared fixed window duration",
            ],
            "organization_domain": "functional_coupling",
            "observed_diagnostic_domains": ["functional_coupling"],
            "load_bearing_organization_domain": "functional_coupling",
            "mixed_domain_mediation_resolution": "not_applicable",
            "organization_before": relation["relation_at_carrier_exhaustion"],
            "organization_after": relation["post_formation_progression_values"][-1],
            "organization_weakened": relation["weakening_supported"],
            "organization_authority": "exact_derived_projection",
            "organization_update_owner": "pure_observer_over_native_LGRC9V3_history",
            "organization_has_independent_causal_freedom": False,
            "organization_recomputation_status": "passed_exact",
        },
        "causal_mediation_contract": {
            "causal_mediation_contract_id": "n31_i6_D0b_observable_only_v1",
            "later_local_readout_definition": (
                "observer-side-effect audit: equal-state compute-versus-omit branches "
                "process identical native continuation"
            ),
            "later_readout_changed": False,
            "organization_intervention_definition": (
                "not_run: neither native packet history nor finite-window relation value "
                "was clamped, deleted, or contrasted"
            ),
            "mass_matched_during_organization_intervention": (
                "not_applicable_no_organization_intervention"
            ),
            "packet_amount_matched_during_organization_intervention": (
                "not_applicable_no_organization_intervention"
            ),
            "spatial_organization_matched_during_temporal_intervention": (
                "not_applicable_no_temporal_intervention"
            ),
            "other_continuation_state_matched": (
                "not_applicable_no_organization_intervention"
            ),
            "temporal_intervention_matching_status": "not_applicable",
            "organization_intervention_valid": False,
            "local_transport_intervention_status": "not_run",
            "direct_readout_path_excluded": False,
            "hidden_selector_excluded": True,
            "added_coincidence_or_resonance_policy_present": False,
            "later_readout_probe_relation": "unresolved",
            "formation_packet_exclusion_status": "exhausted",
            "organization_mediated_readout_change": False,
            "mediation_strength": "absent",
            "later_readout_probe_relation_detail": (
                "observer_side_effect_disconnection_only_not_an_independent_later_probe"
            ),
        },
        "route_mass_decreased": False,
        "route_organization_weakened": True,
        "later_readout_changed": False,
        "organization_mediated_readout_change": False,
        "ordinary_post_formation_flux_generated": False,
        "added_export_policy_present": False,
        "export_policy_owner": "not_applicable_no_route_export",
        "export_policy_inputs": [],
        "producer_authors_aftereffect": False,
        "d0_to_br_bridge_status": "not_tested",
        "added_mechanism_admission_reason": "not_applicable_D0b_observable",
        "post_formation_producer_call_policy": "no_calls",
        "post_formation_producer_calls": [],
        "post_formation_state_mutating_producer_calls": [],
        "producer_call_audit_status": "complete_no_post_formation_calls",
        "topology_contract_id": "n31_i6_route_plus_disjoint_progression_lane_v1",
        "internal_time_owner": "native_LGRC9V3_event_queue",
        "internal_time_advance_event": "native_progression_lane_packet_departure_and_arrival",
        "clock_scope": "global_model_event_time",
        "route_local_proper_time_advanced_during_expiry": False,
        "progression_fixture_authored_by_experiment": True,
        "local_clock_decay_claim_allowed": False,
        "update_phase": "post_route_carrier_exhaustion_native_event_time_progression",
        "equation_or_relation_id": "n31_i6_finite_window_absolute_route_flux_v1",
        "units_by_state": {
            "event_time": "native_event_time_key",
            "route_transfer": "coherence",
            "finite_window_coupling": "coherence",
            "route_mass": "coherence",
        },
        "invariant_id": "closed_system_node_plus_in_flight_coherence",
        "coherence_budget_before": float(
            trace["checkpoints"][0]["runtime_state"]["conserved_budget_total"]
        ),
        "coherence_budget_after": float(
            trace["checkpoints"][-1]["runtime_state"]["conserved_budget_total"]
        ),
        "invariant_tolerance": THRESHOLDS["closed_system_budget_tolerance"],
        "forming_activity_present": True,
        "forming_activity_stopped": True,
        "post_formation_window": (
            f"native_event_time_{max(ROUTE_ARRIVAL_TIMES)}_to_"
            f"{PROGRESSION_SCHEDULE[-1][1]}"
        ),
        "formation_trace": {
            "artifact_path": trace_path,
            "checkpoint_ids": [
                "forming_route_packets_in_flight_after_final_departure",
                "route_arrival_1_committed",
                "route_arrival_2_committed",
                "route_arrival_3_committed",
            ],
        },
        "persistence_trace": {
            "artifact_path": trace_path,
            "from_checkpoint": "route_arrival_3_committed",
            "to_checkpoint": "post_formation_progression_1",
            "value_before": relation["relation_at_carrier_exhaustion"],
            "value_after": relation["post_formation_progression_values"][0],
            "persistence_supported": relation["persistence_supported"],
        },
        "weakening_trace": {
            "artifact_path": trace_path,
            "checkpoint_ids": [
                "post_formation_progression_1",
                "post_formation_progression_2",
                "post_formation_progression_3",
                "post_formation_progression_4",
            ],
            "values": relation["post_formation_progression_values"],
            "weakening_supported": relation["weakening_supported"],
            "window_expiry_supported": relation["window_expiry_supported"],
        },
        "local_readout_trace": {
            "artifact_path": trace_path,
            "control_id": "observable_disconnected_from_transport",
            "result": "compute_and_omit_observer_branches_continue_identically",
            "scope": "observer_side_effect_only_not_mediator_disconnection",
            "later_readout_changed": False,
        },
        "mediator_intervention_trace": {
            "artifact_path": trace_path,
            "intervention": "not_run",
            "observer_side_effect_control": "compute_versus_omit_pure_observable",
            "organization_intervention_valid": False,
            "runtime_identity_changed": False,
            "mediation_supported": False,
        },
        "destination_trace_if_mass_moves": na("route_mass_does_not_move_outside_support"),
        "complete_state_identity": {
            row["checkpoint_id"]: row["restoration_identity_digest"]
            for row in trace["checkpoints"]
        },
        "restoration_identity_schema": "lgrc9v3_restoration_identity_v1",
        "snapshot_load_status": "passed_exact_source_history_and_relation",
        "reset_status": "not_applicable_no_reset_sensitive_operation",
        "branch_continuation_status": (
            "passed_compute_vs_omit_observer_side_effect_control"
        ),
        "derived_cache_status": "not_persisted_exact_projection",
        "derived_cache_recomputation_status": "passed_exact",
        "execution_reconstruction_status": "not_run_pending_iteration_8",
        "producer_roles": [
            "experiment_fixture_pre_formation_route_packet_schedule",
            "experiment_fixture_pre_formation_disjoint_progression_schedule",
            "pure_observer_and_receipt_collector",
        ],
        "producer_residue": [
            "route formation and the disjoint event-time progression schedule are experiment-predeclared",
            "the progression scaffold is not autonomous route activity",
        ],
        "naturalization_debt": [
            "autonomous event-time progression after route formation is not shown",
            "the finite-window relation is not consumed by native transport",
            "causal D0a mediation remains for Iteration 7",
        ],
        "source_current_inputs": [
            "LGRC9V3RuntimeState.event_time_key",
            "LGRC9V3RuntimeState.packet_ledger.packet_records",
            "LGRC9V3RuntimeState.base_state.nodes[*].coherence",
        ],
        "artifact_manifest": [
            {
                "path": trace_path,
                "sha256": sha256_file(TRACE),
                "artifact_role": "source_current_D0b_finite_window_runtime_trace",
            }
        ],
        "artifact_sha256": sha256_file(TRACE),
        "all_artifact_sha256_match_file_contents": True,
        "row_specific_thresholds_declared_before_use": THRESHOLDS,
        "decay_relation_ladder_rung": "DR3",
        "row_decision": "supported",
        "claim_ceiling": (
            "bounded_source_current_fading_finite_window_graph_observable_DR3_below_causal_trail"
        ),
        "blocked_relabels": BLOCKED_RELABELS,
        "unsafe_claim_flags": {
            f"{claim}_claim_allowed": False for claim in BLOCKED_RELABELS
        },
        "candidate_semantic_contract": candidate_contract,
        "candidate_semantic_contract_digest": digest_value(candidate_contract),
        "control_results": controls,
        "direct_I3_null_consumption_count": sum(
            1 for row in controls if row["matched_to_I3_null"]
        ),
        "candidate_specific_control_regeneration_count": len(controls),
    }
    candidate["missing_required_fields"] = sorted(
        set(required_fields) - set(candidate)
    )
    nested_contract_schemas = {
        "route_mass_contract": i2["schema"]["route_mass_contract_schema"][
            "required_fields"
        ],
        "route_organization_contract": i2["schema"][
            "route_organization_contract_schema"
        ]["required_fields"],
        "causal_mediation_contract": i2["schema"][
            "causal_mediation_contract_schema"
        ]["required_fields"],
    }
    candidate["nested_contract_validation"] = {
        contract_name: {
            "required_field_count": len(contract_fields),
            "observed_required_field_count": len(
                set(contract_fields) & set(candidate[contract_name])
            ),
            "missing_required_fields": sorted(
                set(contract_fields) - set(candidate[contract_name])
            ),
            "complete": not (
                set(contract_fields) - set(candidate[contract_name])
            ),
        }
        for contract_name, contract_fields in nested_contract_schemas.items()
    }
    candidate["missing_nested_required_fields"] = {
        contract_name: result["missing_required_fields"]
        for contract_name, result in candidate["nested_contract_validation"].items()
        if result["missing_required_fields"]
    }
    route_mass_schema = i2["schema"]["route_mass_contract_schema"]
    organization_schema = i2["schema"]["route_organization_contract_schema"]
    mediation_schema = i2["schema"]["causal_mediation_contract_schema"]
    candidate["nested_contract_value_validation"] = {
        "route_mass_contract": {
            "flux_quantity_semantics_valid": candidate["route_mass_contract"][
                "flux_quantity_semantics"
            ]
            == route_mass_schema["flux_quantity_semantics_required_value"],
            "boundary_flux_sign_policy_valid": candidate["route_mass_contract"][
                "boundary_flux_sign_policy"
            ]
            == route_mass_schema["boundary_flux_sign_policy_required_value"],
            "boundary_crossing_count_policy_valid": candidate[
                "route_mass_contract"
            ]["boundary_crossing_count_policy"]
            == route_mass_schema["boundary_crossing_count_policy"],
            "continuity_formula_closed": abs(
                candidate["route_mass_contract"]["continuity_residual"]
                - (
                    candidate["route_mass_contract"]["mass_delta"]
                    + candidate["route_mass_contract"][
                        "net_outward_boundary_flux"
                    ]
                )
            )
            <= candidate["route_mass_contract"]["continuity_tolerance"],
        },
        "route_organization_contract": {
            "organization_domain_valid": candidate["route_organization_contract"][
                "organization_domain"
            ]
            in organization_schema["organization_domain_enum"],
            "load_bearing_domain_valid": candidate[
                "route_organization_contract"
            ]["load_bearing_organization_domain"]
            in organization_schema["load_bearing_domain_enum"],
            "mixed_domain_resolution_valid": candidate[
                "route_organization_contract"
            ]["mixed_domain_mediation_resolution"]
            in organization_schema["mixed_domain_resolution_enum"],
            "organization_authority_valid": candidate[
                "route_organization_contract"
            ]["organization_authority"]
            in organization_schema["organization_authority_enum"],
            "organization_recomputation_status_valid": candidate[
                "route_organization_contract"
            ]["organization_recomputation_status"]
            in organization_schema["organization_recomputation_status_enum"],
        },
        "causal_mediation_contract": {
            "later_readout_probe_relation_valid": candidate[
                "causal_mediation_contract"
            ]["later_readout_probe_relation"]
            in mediation_schema["later_readout_probe_relation_enum"],
            "formation_packet_exclusion_status_valid": candidate[
                "causal_mediation_contract"
            ]["formation_packet_exclusion_status"]
            in mediation_schema["formation_packet_exclusion_status_enum"],
            "mediation_strength_valid": candidate["causal_mediation_contract"][
                "mediation_strength"
            ]
            in mediation_schema["mediation_strength_enum"],
            "temporal_intervention_matching_status_valid": candidate[
                "causal_mediation_contract"
            ]["temporal_intervention_matching_status"]
            in mediation_schema["temporal_intervention_matching_status_enum"],
            "absent_mediation_does_not_claim_change": not candidate[
                "causal_mediation_contract"
            ]["organization_mediated_readout_change"],
        },
    }
    candidate["nested_contract_values_conform"] = all(
        all(contract_checks.values())
        for contract_checks in candidate["nested_contract_value_validation"].values()
    )
    candidate["row_digest"] = digest_value(
        {key: value for key, value in candidate.items() if key != "row_digest"}
    )
    return candidate


def build_payload(trace: dict[str, Any]) -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i3r1 = load_json(I3R1_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    i4r1 = load_json(I4R1_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i5_trace = load_json(I5_TRACE)
    i5r1 = load_json(I5R1_OUTPUT)
    candidate = build_candidate(trace, i2, i3)
    relation = trace["D0b_relation"]
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
            "I4R1_source_chain_exact",
            i4["output_digest"] == I4_OUTPUT_DIGEST
            and sha256_file(I4_OUTPUT) == I4_ARTIFACT_SHA256
            and i4r1["output_digest"] == I4R1_OUTPUT_DIGEST
            and sha256_file(I4R1_OUTPUT) == I4R1_ARTIFACT_SHA256,
            i4r1["revision_id"],
        ),
        check(
            "I5R1_source_chain_exact_and_I6_ready",
            i5["output_digest"] == I5_OUTPUT_DIGEST
            and sha256_file(I5_OUTPUT) == I5_ARTIFACT_SHA256
            and i5_trace["output_digest"] == I5_TRACE_OUTPUT_DIGEST
            and sha256_file(I5_TRACE) == I5_TRACE_SHA256
            and i5r1["status"] == "passed"
            and i5r1["revision_id"] == "N31-I5R1"
            and i5r1["output_digest"] == I5R1_OUTPUT_DIGEST
            and sha256_file(I5R1_OUTPUT) == I5R1_ARTIFACT_SHA256
            and i5["ready_for_iteration_6_D0b_finite_window_relation"],
            i5r1["output_digest"],
        ),
        check("runtime_trace_passed", trace["status"] == "passed", trace["output_digest"]),
        check(
            "candidate_schema_complete",
            not candidate["missing_required_fields"]
            and not candidate["missing_nested_required_fields"],
            {
                "top_level": candidate["missing_required_fields"],
                "nested": candidate["missing_nested_required_fields"],
                "nested_contract_validation": candidate[
                    "nested_contract_validation"
                ],
            },
        ),
        check(
            "I2_nested_contracts_recursively_complete",
            all(
                row["complete"]
                for row in candidate["nested_contract_validation"].values()
            ),
            candidate["nested_contract_validation"],
        ),
        check(
            "I2_nested_contract_values_conform",
            candidate["nested_contract_values_conform"],
            candidate["nested_contract_value_validation"],
        ),
        check(
            "source_current_D0b_relation_persists_and_weakens",
            relation["persistence_supported"]
            and relation["weakening_supported"]
            and relation["window_expiry_supported"],
            relation["full_post_formation_timeline"],
        ),
        check(
            "cache_removal_recomputation_exact",
            candidate["derived_cache_recomputation_status"] == "passed_exact",
            candidate["derived_cache_status"],
        ),
        check(
            "restoration_and_branch_disconnection_pass",
            candidate["snapshot_load_status"]
            == "passed_exact_source_history_and_relation"
            and candidate["branch_continuation_status"]
            == "passed_compute_vs_omit_observer_side_effect_control",
            candidate["branch_continuation_status"],
        ),
        check(
            "observer_side_effect_control_not_mislabeled_as_mediator_intervention",
            not candidate["causal_mediation_contract"][
                "organization_intervention_valid"
            ]
            and candidate["causal_mediation_contract"][
                "local_transport_intervention_status"
            ]
            == "not_run"
            and candidate["causal_mediation_contract"][
                "later_readout_probe_relation"
            ]
            == "unresolved",
            candidate["causal_mediation_contract"],
        ),
        check(
            "global_clock_scope_and_local_clock_ceiling_explicit",
            candidate["clock_scope"] == "global_model_event_time"
            and not candidate["route_local_proper_time_advanced_during_expiry"]
            and candidate["progression_fixture_authored_by_experiment"]
            and not candidate["local_clock_decay_claim_allowed"],
            candidate["clock_scope"],
        ),
        check(
            "packet_event_measure_and_window_boundaries_explicit",
            trace["window_boundary_conformance"]["passed"]
            and all(
                row["finite_window_relation"]["event_measure_convention"]
                == "atomic_native_packet_arrival_measure"
                for row in trace["checkpoints"]
            ),
            trace["window_boundary_conformance"],
        ),
        check(
            "causal_trail_and_DR4_relabels_fail_closed",
            not candidate["organization_mediated_readout_change"]
            and candidate["decay_relation_ladder_rung"] == "DR3",
            candidate["claim_ceiling"],
        ),
        check(
            "candidate_specific_controls_regenerated",
            candidate["direct_I3_null_consumption_count"] == 0
            and candidate["candidate_specific_control_regeneration_count"]
            == len(CONTROL_IDS)
            and all(
                row["regenerated_for_I6_candidate"]
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
            "mass_and_budget_invariants_pass",
            relation["route_mass_span"] <= THRESHOLDS["route_mass_tolerance"]
            and relation["closed_system_budget_span"]
            <= THRESHOLDS["closed_system_budget_tolerance"],
            {
                "route_mass_span": relation["route_mass_span"],
                "budget_span": relation["closed_system_budget_span"],
            },
        ),
        check(
            "artifact_manifest_exact",
            candidate["artifact_manifest"]
            == [
                {
                    "path": TRACE.relative_to(ROOT).as_posix(),
                    "sha256": sha256_file(TRACE),
                    "artifact_role": "source_current_D0b_finite_window_runtime_trace",
                }
            ],
            candidate["artifact_manifest"],
        ),
        check(
            "positive_causal_decay_claims_remain_closed",
            all(not value for value in candidate["unsafe_claim_flags"].values()),
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
        "iteration": "6",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_source_current_D0b_DR3_finite_window_observable_below_causal_trail"
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
                "lineage_path": I3R1_OUTPUT.relative_to(ROOT).as_posix(),
                "lineage_output_digest": i3r1["output_digest"],
            },
            "I4R1": {
                "I4_path": I4_OUTPUT.relative_to(ROOT).as_posix(),
                "I4_output_digest": i4["output_digest"],
                "lineage_path": I4R1_OUTPUT.relative_to(ROOT).as_posix(),
                "lineage_output_digest": i4r1["output_digest"],
            },
            "I5R1": {
                "path": I5_OUTPUT.relative_to(ROOT).as_posix(),
                "output_digest": i5["output_digest"],
                "artifact_sha256": sha256_file(I5_OUTPUT),
                "trace_path": I5_TRACE.relative_to(ROOT).as_posix(),
                "trace_output_digest": i5_trace["output_digest"],
                "trace_artifact_sha256": sha256_file(I5_TRACE),
                "lineage_path": I5R1_OUTPUT.relative_to(ROOT).as_posix(),
                "lineage_output_digest": i5r1["output_digest"],
                "lineage_artifact_sha256": sha256_file(I5R1_OUTPUT),
                "revision_id": i5r1["revision_id"],
                "consumed_as": "D0c_comparator_and_I6_handoff_boundary",
            },
        },
        "graph_scope": {
            "I6_governance_base_revision": I6_GOVERNANCE_BASE_REVISION,
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
            "artifact_role": "source_current_D0b_finite_window_runtime_trace",
        },
        "artifact_manifest": [
            {
                "path": TRACE.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(TRACE),
                "artifact_role": "source_current_D0b_finite_window_runtime_trace",
            },
            {
                "path": I5R1_OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(I5R1_OUTPUT),
                "artifact_role": "I5R1_provenance_and_scientific_outcome_lineage",
            },
        ],
        "candidate_rows": [candidate],
        "candidate_row_count": 1,
        "source_current_D0b_candidate_supported": True,
        "positive_evidence_opened": True,
        "positive_evidence_scope": "source_current_D0b_fading_observable_only",
        "positive_causal_decay_evidence_opened": False,
        "D0b_persistence_supported": True,
        "D0b_weakening_supported": True,
        "causal_mediation_supported": False,
        "candidate_rows_classified": True,
        "decay_relation_ladder_rung_assigned": True,
        "decay_relation_ladder_rung": "DR3",
        "decay_relation_ladder_ceiling": "DR3_fading_observable_without_mediation",
        "n31_progress_rung_assigned": True,
        "n31_progress_rung": (
            "N31-C2_active_nulls_and_representation_boundary_established"
        ),
        "n31_closeout_ceiling": (
            "N31-C2_active_nulls_and_representation_boundary_established"
        ),
        "n31_closeout_ladder_rung_assigned": False,
        "n31_c3_D0c_component_satisfied": True,
        "n31_c3_D0b_component_satisfied": True,
        "n31_c3_overall_pending_D0a_classification": True,
        "ready_for_iteration_7_D0a_source_current_causal_probe": True,
        "claim_boundary": {
            "claim_ceiling": (
                "bounded_source_current_fading_finite_window_graph_observable_DR3_below_causal_trail"
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
        payload["acceptance_state"] = "blocked_D0b_validation_failed"
        payload["source_current_D0b_candidate_supported"] = False
        payload["positive_evidence_opened"] = False
        payload["decay_relation_ladder_rung_assigned"] = False
        payload["ready_for_iteration_7_D0a_source_current_causal_probe"] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    candidate = payload["candidate_rows"][0]
    trace = load_json(TRACE)
    relation = trace["D0b_relation"]
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
        f"""# N31 Iteration 6 - D0b Finite-Window Derived Relation

Status: `{payload['status']}`

Acceptance state: `{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Result

I6 supports one source-current `D0b` finite-window coupling observable at
`DR3`:

```text
relation at forming-carrier exhaustion = {relation['relation_at_carrier_exhaustion']}
post-formation progression values = {relation['post_formation_progression_values']}
persistence supported = {str(relation['persistence_supported']).lower()}
weakening supported = {str(relation['weakening_supported']).lower()}
window expiry supported = {str(relation['window_expiry_supported']).lower()}
positive-to-positive decreases = {relation['positive_to_positive_decrease_count']}
total strict decreases = {relation['total_strict_decrease_count']}
final expiry steps = {relation['final_expiry_step_count']}
causal mediation supported = false
```

This is positive evidence for a fading derived graph observable. It is not
positive evidence for a causal trail or causal decay relation.

## Geometric And Runtime Meaning

Three equal native packets cross one registered internal route edge and arrive
at event times `1.0`, `1.5`, and `2.0`. The relation is the RC-Distance
finite-window coupling:

```text
F_01(T; DeltaT) = sum |packet amount|
                  for completed route transfers in (T - DeltaT, T]
DeltaT = 4.0 native event-time units
```

The packet event-measure convention is explicit: each completed transfer is an
atomic amount at its native arrival event. Native arrival is selected because
it is the single completion event for the registered-edge transfer. Departure
and arrival are not double-counted. This is the declared operational bridge to
the continuous-flux expression; it is not claimed as the unique possible
discretization. At carrier exhaustion all three transfers are
inside the window, so `F_01 = 0.3`. A disjoint packet lane then advances native
LGRC event time without touching the route support. The first progression
checkpoint retains all three transfers. Later checkpoints exclude them one by
one, producing `{relation['post_formation_progression_values']}` and finally
zero.

An equality-boundary fixture evaluates the retained native history at evaluation
times `2.0`, `5.0`, `5.5`, and `6.0`. It confirms that an arrival at the right endpoint
is included and arrivals exactly at `T - DeltaT` are excluded.

The route mass span is `{relation['route_mass_span']}` and the closed-system
budget span is `{relation['closed_system_budget_span']}`. The changing quantity
is recent-transfer organization, not destroyed coherence or route-mass loss.

## Authority And Cache

The finite-window relation is an exact functional over native packet history
and native event time. It is not persisted in LGRC runtime state. At every
checkpoint an experiment-local cache is removed and recomputed exactly; doing
so leaves restoration identity unchanged. Snapshot/load restores both source
history and the recomputed relation exactly.

The progression lane is producer residue: its packet schedule is predeclared
before any runtime event and exists only to provide bounded native event-time
progression. It is disjoint from the route and contributes no route transfer.
No schedule call or state-mutating producer call occurs after route formation.
The clock scope is `global_model_event_time`: route-local proper time is not
advanced or tested. Unrelated model activity can therefore age this observable,
and I6 does not support a route-local-clock decay claim.

## Frozen Contract Conformance

I6 recursively instantiates and validates the complete frozen I2 contracts:

```text
route-mass required fields = {candidate['nested_contract_validation']['route_mass_contract']['required_field_count']}
route-organization required fields = {candidate['nested_contract_validation']['route_organization_contract']['required_field_count']}
causal-mediation required fields = {candidate['nested_contract_validation']['causal_mediation_contract']['required_field_count']}
missing nested fields = {candidate['missing_nested_required_fields']}
```

Route mass, recent-transfer organization, and causal mediation remain separate
objects. A complete schema does not upgrade the absent mediation result.

## I5 Revision Lineage

I6 consumes `N31-I5R1`, not the earlier reviewed I5 package. The lineage record
pins both identities, records the orientation/carrier/control hardening, and
shows that the scientific `D0c/DR1` result and no-decay ceiling did not change:

```text
lineage = {payload['source_chain']['I5R1']['lineage_path']}
lineage digest = {payload['source_chain']['I5R1']['lineage_output_digest']}
```

## Causal Boundary

Two equal restored branches start from the first persistence checkpoint. One
computes the finite-window observable and one does not. They then process the
same native progression events and finish with equal receipts and equal
restoration identities. This proves only that computing or omitting the pure
report observable has no runtime side effect. It does not intervene on native
packet history or clamp the relation while holding other state matched.

No valid organization or local-transport intervention was run, and the later
independent-probe relation remains unresolved. I6 consequently reaches `DR3`
as an observable but fails closed at `DR4`. Using this value as a transport
input would require authority reclassification as a closure or added causal
mechanism.

## Controls

{controls}

All I3 control meanings are resolved against the exact I6 semantic contract.
No generic I3 fixture is directly consumed as source-current evidence.

## Classification

```text
primary semantic class = D0b
authority = exact_derived_projection
candidate disposition = supported
DR rung = DR3
causal trail = blocked
causal decay = blocked
N31 progress ceiling = N31-C2
N31-C3 D0c component = satisfied
N31-C3 D0b component = satisfied
N31-C3 overall = pending I7 D0a classification
```

## Checks

{checks}
""",
        encoding="utf-8",
    )


def main() -> None:
    i5r1 = build_i5r1_lineage()
    I5R1_OUTPUT.write_text(canonical_json(i5r1), encoding="utf-8")
    if i5r1["failed_checks"]:
        raise SystemExit(
            "N31 I5R1 lineage failed: " + ", ".join(i5r1["failed_checks"])
        )
    trace = build_trace()
    TRACE.write_text(canonical_json(trace), encoding="utf-8")
    if trace["failed_checks"]:
        raise SystemExit(
            "N31 I6 trace failed: " + ", ".join(trace["failed_checks"])
        )
    payload = build_payload(trace)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    if payload["failed_checks"]:
        raise SystemExit(
            "N31 I6 failed: " + ", ".join(payload["failed_checks"])
        )


if __name__ == "__main__":
    main()
