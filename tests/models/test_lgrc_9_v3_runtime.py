"""Tests for executable LGRC9V3 event-queue orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import json
import math
from pathlib import Path
import tempfile
import unittest

from pygrc.core import (
    CAUSAL_LAYER,
    GRCEvent,
    InvalidParamsError,
    InvalidStateTransitionError,
    PortGraphBackend,
    SnapshotCompatibilityError,
    save_snapshot,
)
from pygrc.models import (
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC2,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_SCHEMA_VERSION,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX,
    LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED,
    LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND,
    LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_SCHEMA_VERSION,
    LGRC9V3_LOCAL_UPDATE_EVENT_KIND,
    LGRC9V3_LOCAL_UPDATE_EVENT_SCHEMA_VERSION,
    LGRC9V3RuntimeState,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_DERIVED_SURFACE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_DECLARED_LOCAL_PREFERENCE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID,
    LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
    LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_POST_REFINEMENT_REPLAY,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_DECLARED_TIEBREAKER,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    LGRC9V3NativeRouteCandidateSetRecord,
    LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
    LGRC9V3_PACKET_STATE_IN_FLIGHT,
    LGRC9V3_RUNTIME_EVENT_SCHEMA_VERSION,
    LGRC9V3_RUNTIME_STATE_KIND,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE,
    PortEdge,
    build_lgrc9v3_causal_pulse_substrate_surface_digest,
    build_lgrc9v3_causal_pulse_substrate_surface_lineage_record_digest,
    build_lgrc9v3_native_route_arbitration_record_digest,
    build_lgrc9v3_native_route_candidate_record_digest,
    build_lgrc9v3_topology_event_digest,
    build_lgrc9v3_topology_state_reabsorption_record_digest,
    evaluate_lgrc9v3_proper_time_identity_persistence,
    validate_lgrc9v3_causal_pulse_substrate_surface_artifacts,
    validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts,
    validate_lgrc9v3_native_route_arbitration_artifacts,
)
from pygrc.telemetry import (
    LGRC9V3_TELEMETRY_FAMILY,
    RunTelemetryIdentity,
    build_lgrc9v3_graph_checkpoint,
    classify_lgrc9v3_step_extension,
    lgrc9v3_run_summary_family_extensions,
)


_PARAMS = {"dt": 1.0}


def _pulse_surface_params(*, validated: bool = False) -> dict[str, object]:
    return {
        "dt": 1.0,
        "causal_modes": {
            "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_pulse_substrate_surface_enabled": True,
            "causal_pulse_substrate_surface_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
            ),
            "causal_pulse_substrate_surface_validated": validated,
        },
    }


def _boundary_birth_params(*, enabled: bool = True) -> dict[str, object]:
    params: dict[str, object] = {
        "dt": 1.0,
        "evolution": {
            "lambda_birth": 1.0,
            "alpha_seed": 0.25,
            "w_bond": 1.5,
        },
    }
    if enabled:
        params["causal_modes"] = {
            "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_boundary_birth_allowed": True,
            "causal_boundary_birth_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
            ),
        }
    return params


def _active_topology_params(
    *,
    spark_lane: str = "grc9v3_column_h_assisted",
    collapse_allowed: bool = False,
    identity_allowed: bool = False,
) -> dict[str, object]:
    params = _spark_params(spark_lane=spark_lane)
    params["causal_modes"] = {
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "lapse_policy": LAPSE_POLICY_UNIT,
        "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
        "event_time_policy": "explicit_event_time_key",
        "proper_time_accumulation_policy": "local_event_frontier",
        "causal_topology_integration_allowed": True,
        "causal_spark_expansion_allowed": True,
        "causal_refinement_packet_transport_allowed": True,
        "causal_proper_time_inheritance_allowed": True,
        "causal_collapse_reabsorption_allowed": collapse_allowed,
        "causal_identity_acceptance_allowed": identity_allowed,
    }
    return params


def _active_topology_with_boundary_birth_params() -> dict[str, object]:
    params = _active_topology_params()
    params["evolution"] = {
        **dict(params.get("evolution", {})),
        "lambda_birth": 1.0,
        "alpha_seed": 0.1,
        "w_bond": 1.0,
    }
    causal_modes = dict(params["causal_modes"])  # type: ignore[index]
    causal_modes.update(
        {
            "causal_boundary_birth_allowed": True,
            "causal_boundary_birth_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
            ),
        }
    )
    params["causal_modes"] = causal_modes
    return params


def _active_topology_with_surface_lineage_params() -> dict[str, object]:
    params = _active_topology_params(
        collapse_allowed=True,
        identity_allowed=False,
    )
    causal_modes = dict(params["causal_modes"])  # type: ignore[index]
    causal_modes.update(
        {
            "causal_pulse_substrate_surface_enabled": True,
            "causal_pulse_substrate_surface_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
            ),
            "causal_pulse_substrate_surface_validated": True,
            "causal_pulse_substrate_surface_lineage_transport_enabled": True,
            "causal_pulse_substrate_surface_lineage_transport_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
            ),
            "causal_pulse_substrate_surface_lineage_transport_validated": False,
            "causal_pulse_substrate_surface_lineage_transport_supported": False,
        }
    )
    params["causal_modes"] = causal_modes
    return params


def _active_topology_with_state_reabsorption_params() -> dict[str, object]:
    params = _active_topology_with_surface_lineage_params()
    causal_modes = dict(params["causal_modes"])  # type: ignore[index]
    causal_modes.update(
        {
            "causal_topology_state_reabsorption_enabled": True,
            "causal_topology_state_reabsorption_policy": (
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
            ),
            "causal_topology_state_reabsorption_validated": False,
            "causal_topology_state_reabsorption_supported": False,
        }
    )
    params["causal_modes"] = causal_modes
    return params


def _active_topology_with_route_arbitration_params() -> dict[str, object]:
    params = _active_topology_with_state_reabsorption_params()
    causal_modes = dict(params["causal_modes"])  # type: ignore[index]
    causal_modes.update(
        {
            "causal_pulse_substrate_surface_lineage_transport_validated": True,
            "causal_pulse_substrate_surface_lineage_transport_supported": True,
            "causal_topology_state_reabsorption_validated": True,
            "causal_topology_state_reabsorption_supported": True,
            "native_lgrc_route_arbitration_enabled": True,
            "native_lgrc_route_arbitration_policy": (
                LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
            ),
        }
    )
    params["causal_modes"] = causal_modes
    return params


def _lineage_validation_artifacts(model: LGRC9V3) -> dict[str, object]:
    snapshot = model.snapshot()
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    return {
        "events": snapshot["events"],
        "surface_rows": runtime["causal_pulse_substrate_surface_log"],
        "surface_lineage_records": runtime[
            "causal_pulse_substrate_surface_lineage_log"
        ],
        "topology_state_reabsorption_records": runtime[
            "topology_state_reabsorption_log"
        ],
    }


def _refresh_lineage_record_digest(record: dict[str, object]) -> dict[str, object]:
    refreshed = dict(record)
    refreshed.pop("lineage_record_digest", None)
    refreshed["lineage_record_digest"] = (
        build_lgrc9v3_causal_pulse_substrate_surface_lineage_record_digest(
            refreshed
        )
    )
    return refreshed


def _refresh_topology_state_reabsorption_digest(
    record: dict[str, object],
) -> dict[str, object]:
    refreshed = dict(record)
    refreshed.pop("topology_state_reabsorption_digest", None)
    refreshed["topology_state_reabsorption_digest"] = (
        build_lgrc9v3_topology_state_reabsorption_record_digest(refreshed)
    )
    return refreshed


def _native_route_candidate_spec(
    *,
    candidate_route_id: str,
    selected_sink_id: int,
    losing_sink_ids: tuple[int, ...],
    score: float,
    order_key: str | None = None,
) -> dict[str, object]:
    return {
        "candidate_route_id": candidate_route_id,
        "route_intent": LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
        "candidate_topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        "candidate_competing_sink_ids": (0, 2),
        "candidate_losing_sink_ids": losing_sink_ids,
        "candidate_selected_sink_id": selected_sink_id,
        "candidate_transferred_node_ids": (1, 2),
        "candidate_lineage_transfer_map": {1: str(selected_sink_id), 2: str(selected_sink_id)},
        "candidate_source_node_ids": (1, 2),
        "candidate_target_node_ids": (selected_sink_id,),
        "candidate_retired_node_ids": losing_sink_ids,
        "candidate_source_edge_ids": (1,),
        "candidate_target_edge_ids": (0,),
        "candidate_retired_edge_ids": (1,),
        "candidate_route_score": score,
        "candidate_score_components": {
            "surface_pulse_contact": score,
        },
        "candidate_budget_prediction": {
            "node_plus_packet_budget_before": 6.0,
            "node_plus_packet_budget_after": 6.0,
            "node_plus_packet_budget_error": 0.0,
        },
        "candidate_order_key": order_key or candidate_route_id,
        "candidate_runtime_visible_inputs": (
            "candidate_source_surface_digest",
            "surface_pulse_contact",
            "serialized_route_arbitration_policy",
        ),
    }


def _route_arbitration_model_with_candidate_set(
    *,
    scores: tuple[float, float] = (0.25, 0.75),
    unresolved_tie_policy: str = LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    multi_basin_enabled: bool = False,
) -> tuple[LGRC9V3, object]:
    params = _active_topology_with_route_arbitration_params()
    if multi_basin_enabled:
        causal_modes = dict(params["causal_modes"])  # type: ignore[index]
        causal_modes.update(
            {
                "native_lgrc_multi_basin_formation_enabled": True,
                "native_lgrc_multi_basin_formation_policy": (
                    LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_POST_REFINEMENT_REPLAY
                ),
                "native_lgrc_multi_basin_formation_validated": False,
                "native_lgrc_multi_basin_formation_supported": False,
            }
        )
        params["causal_modes"] = causal_modes
    model = LGRC9V3.from_state(
        _three_node_state(),
        params,
    )
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
    result = model.emit_native_route_candidate_set(
        arbitration_window_id="window:arbitration",
        source_surface_digest=str(source_surface.surface_digest),
        unresolved_tie_policy=unresolved_tie_policy,
        candidate_routes=(
            _native_route_candidate_spec(
                candidate_route_id="candidate:low",
                selected_sink_id=2,
                losing_sink_ids=(0,),
                score=scores[0],
            ),
            _native_route_candidate_spec(
                candidate_route_id="candidate:high",
                selected_sink_id=0,
                losing_sink_ids=(2,),
                score=scores[1],
            ),
        ),
    )
    candidate_set = result["candidate_set_record"]
    assert candidate_set is not None
    return model, candidate_set


def _route_arbitration_model_with_full_chain() -> tuple[LGRC9V3, object, object]:
    model, candidate_set = _route_arbitration_model_with_candidate_set()
    arbitration = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
    )["route_arbitration_record"]
    model.commit_native_route_arbitration_selection(
        native_route_arbitration_reference=str(
            arbitration.native_route_arbitration_digest
        ),
    )
    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=2,
        threshold=0.0,
        packet_amount=0.1,
        source_node_selector="surface_source",
    )
    model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    model.step()
    return model, candidate_set, arbitration


def _route_arbitration_validation_artifacts(model: LGRC9V3) -> dict[str, object]:
    snapshot = model.snapshot()
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    return {
        "events": snapshot["events"],
        "candidate_route_records": runtime["native_route_candidate_log"],
        "candidate_set_records": runtime["native_route_candidate_set_log"],
        "route_arbitration_records": runtime["native_route_arbitration_log"],
        "surface_rows": runtime["causal_pulse_substrate_surface_log"],
        "surface_lineage_records": runtime[
            "causal_pulse_substrate_surface_lineage_log"
        ],
        "topology_events": [
            event["payload"] for event in runtime["topology_event_log"]
        ],
        "topology_state_reabsorption_records": runtime[
            "topology_state_reabsorption_log"
        ],
        "production_results": runtime["cached_quantities"].get(
            LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
            [],
        ),
    }


def _recanonicalized_native_route_candidate_artifact(
    artifact: Mapping[str, object],
) -> dict[str, object]:
    updated = dict(deepcopy(artifact))
    updated["candidate_route_digest"] = build_lgrc9v3_native_route_candidate_record_digest(
        {
            key: value
            for key, value in updated.items()
            if key != "candidate_route_digest"
        }
    )
    return updated


def _recanonicalized_native_route_arbitration_artifact(
    artifact: Mapping[str, object],
) -> dict[str, object]:
    updated = dict(deepcopy(artifact))
    updated["native_route_arbitration_digest"] = (
        build_lgrc9v3_native_route_arbitration_record_digest(
            {
                key: value
                for key, value in updated.items()
                if key != "native_route_arbitration_digest"
            }
        )
    )
    return updated


def _spark_params(
    *,
    spark_lane: str = "current_hybrid_signed_hessian",
    eps_column_h: float = 1.0,
    enable_column_h_sign_crossing: bool = False,
    store_previous_column_h: bool = False,
) -> dict[str, object]:
    return {
        "dt": 1.0,
        "evolution": {
            "eps_gradient": 0.01,
            "eps_spark": 0.0,
            "eps_column_h": eps_column_h,
            "eps_column_h_crossing_zero": 0.0,
        },
        "constitutive_semantic_modes": {
            "spark_lane": spark_lane,
            "enable_column_h_sign_crossing": enable_column_h_sign_crossing,
            "store_previous_column_h": store_previous_column_h,
        },
    }


def _three_node_state() -> GRC9V3State:
    graph = PortGraphBackend()
    node_0 = graph.add_node({"label": "source"})
    node_1 = graph.add_node({"label": "middle"})
    node_2 = graph.add_node({"label": "target"})
    edge_01 = graph.connect_ports(node_0, 0, node_1, 0, {"kind": "01"})
    edge_12 = graph.connect_ports(node_1, 1, node_2, 0, {"kind": "12"})
    edge_02 = graph.connect_ports(node_0, 1, node_2, 1, {"kind": "02"})
    return GRC9V3State(
        topology=graph,
        nodes={
            node_0: GRC9V3NodeState(coherence=1.0),
            node_1: GRC9V3NodeState(coherence=2.0),
            node_2: GRC9V3NodeState(coherence=3.0),
        },
        port_edges={
            edge_01: PortEdge(node_0, 1, node_1, 1, conductance=1.0, flux_uv=0.0),
            edge_12: PortEdge(node_1, 2, node_2, 1, conductance=1.0, flux_uv=0.0),
            edge_02: PortEdge(node_0, 2, node_2, 2, conductance=1.0, flux_uv=0.0),
        },
        base_conductance={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        geometric_length={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        temporal_delay={edge_01: 1.0, edge_12: 1.0, edge_02: 1.0},
        flux_coupling={edge_01: 0.0, edge_12: 0.0, edge_02: 0.0},
    )


def _boundary_birth_state() -> GRC9V3State:
    state = _three_node_state()
    state.nodes[0] = GRC9V3NodeState(coherence=4.0)
    return state


def _saturated_sink_state(
    *,
    gradient: list[float] | None = None,
    signed_hessian: list[float] | None = None,
    center_coherence: float = 1.0,
    neighbor_coherence: float = 1.0,
) -> GRC9V3State:
    graph = PortGraphBackend()
    center = graph.add_node({"label": "saturated_sink"})
    node_states: dict[int, GRC9V3NodeState] = {
        center: GRC9V3NodeState(
            coherence=center_coherence,
            gradient_row_basis=list(gradient or [0.0, 0.0, 0.0]),
            signed_hessian_row_basis=list(signed_hessian or [1.0, 1.0, 1.0]),
            basin_mass=center_coherence,
            basin_id="sink",
            depth=0,
        )
    }
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for slot in range(9):
        port_id = slot + 1
        neighbor = graph.add_node({"label": f"neighbor_{port_id}"})
        edge_id = graph.connect_ports(
            center,
            slot,
            neighbor,
            0,
            {"kind": "saturated_sink_fixture"},
        )
        node_states[neighbor] = GRC9V3NodeState(
            coherence=neighbor_coherence,
            basin_mass=neighbor_coherence,
            basin_id=f"neighbor_{port_id}",
        )
        port_edges[edge_id] = PortEdge(
            center,
            port_id,
            neighbor,
            1,
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.0
    return GRC9V3State(
        topology=graph,
        nodes=node_states,
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
        sink_set={center},
        basins={center: set(node_states)},
    )


def _runtime_budget_surface(model: LGRC9V3) -> float:
    state = model.get_state()
    node_total = sum(
        float(node.coherence) for node in state.base_state.nodes.values()
    )
    return node_total + float(state.packet_ledger.in_flight_packet_total)


def _event_counts(events: list[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        kind = str(getattr(event, "kind"))
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def _step_event_counts(results: list[object]) -> dict[str, int]:
    events = [
        event
        for result in results
        for event in getattr(result, "events")
    ]
    return _event_counts(events)


def _queue_signature(model: LGRC9V3) -> list[tuple[object, ...]]:
    return [
        (
            event.event_time_key,
            event.scheduler_event_index,
            event.event_kind,
            event.event_id,
            event.packet_id,
        )
        for event in model.get_state().packet_ledger.event_queue_records
    ]


def _comparison_report(
    *,
    fixture_name: str,
    grc9v3_events: list[object],
    lgrc9v3_results: list[object],
    grc9v3_node_count: int,
    lgrc9v3_node_count: int,
    lgrc9v3_model: LGRC9V3,
    supported_claims: list[str],
    open_claims: list[str],
) -> dict[str, object]:
    """Build a narrow Iteration 31 comparison report for tests.

    The report deliberately compares event classes and LGRC proper-time
    surfaces. It does not compare raw synchronous step counts as if they were
    causal event counts.
    """

    lgrc_state = lgrc9v3_model.get_state()
    return {
        "fixture_name": fixture_name,
        "artifact_schema_version": "lgrc9v3_grc9v3_comparison_fixture_v1",
        "comparison_policy": "controlled_fixture_pair",
        "alignment_policy": "proper_time_surfaces_and_event_classes",
        "raw_step_count_alignment_used": False,
        "grc9v3_event_counts": _event_counts(grc9v3_events),
        "lgrc9v3_event_counts": _step_event_counts(lgrc9v3_results),
        "grc9v3_final_node_count": int(grc9v3_node_count),
        "lgrc9v3_final_node_count": int(lgrc9v3_node_count),
        "lgrc9v3_event_time_key": float(lgrc_state.event_time_key),
        "lgrc9v3_node_proper_time": {
            str(int(node_id)): float(value)
            for node_id, value in sorted(lgrc_state.node_proper_time.items())
        },
        "lgrc9v3_event_classes": sorted(_step_event_counts(lgrc9v3_results)),
        "supported_claims": list(supported_claims),
        "open_claims": list(open_claims),
    }


class LGRC9V3RuntimeTest(unittest.TestCase):
    """Validate Iteration 25/26 executable event-queue shell behavior."""

    def test_runtime_model_composes_grc9v3_state(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)

        self.assertIsInstance(model.get_state(), LGRC9V3RuntimeState)
        self.assertNotIsInstance(model, GRC9V3)
        self.assertIn(CAUSAL_LAYER, model.list_capabilities())
        self.assertEqual("LGRC9V3", model.MODEL_FAMILY)
        self.assertEqual(0, model.get_state().scheduler_event_index)
        self.assertEqual(0, model.get_state().checkpoint_index)
        self.assertEqual(0.0, model.get_state().event_time_key)

    def test_empty_queue_step_is_explicit_stop_condition(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)

        result = model.step()

        self.assertEqual([], result.events)
        self.assertEqual("event_queue_empty", result.bookkeeping["stop_condition"])
        self.assertEqual(0, result.bookkeeping["scheduler_event_index"])
        self.assertEqual(0, result.bookkeeping["checkpoint_index"])
        self.assertEqual(0.0, result.bookkeeping["event_time_key"])

    def test_queue_ordering_uses_event_time_then_scheduler_index(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=5.0,
            scheduler_event_index=5,
            packet_index=0,
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
            packet_index=1,
        )

        queued = model.get_state().packet_ledger.event_queue_records
        self.assertEqual([1.0, 5.0], [event.event_time_key for event in queued])

        result = model.step()

        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, result.events[0].kind)
        self.assertEqual(1.0, result.time)
        self.assertEqual(1, result.step_index)
        self.assertEqual(1, result.bookkeeping["scheduler_event_index"])
        self.assertAlmostEqual(
            1.0,
            model.get_state().node_proper_time[1],
        )

    def test_departure_arrival_lifecycle_preserves_budget(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        departure = model.step()
        state_after_departure = model.get_state()

        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, departure.events[0].kind)
        self.assertAlmostEqual(0.75, state_after_departure.base_state.nodes[0].coherence)
        self.assertAlmostEqual(
            0.25,
            state_after_departure.packet_ledger.in_flight_packet_total,
        )
        self.assertEqual(0, departure.bookkeeping["local_update_eligibility_events"])
        self.assertFalse(departure.events[0].payload["topology_mutated"])
        self.assertFalse(departure.events[0].payload["spark_event_emitted"])
        self.assertEqual(
            1.0,
            departure.events[0].payload["proper_time_update"]["node_proper_time"],
        )

        arrival = model.step()
        state_after_arrival = model.get_state()
        arrival_kinds = [event.kind for event in arrival.events]

        self.assertEqual(
            [
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
                LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
                LGRC9V3_LOCAL_UPDATE_EVENT_KIND,
            ],
            arrival_kinds,
        )
        self.assertAlmostEqual(2.25, state_after_arrival.base_state.nodes[1].coherence)
        self.assertAlmostEqual(0.0, state_after_arrival.packet_ledger.in_flight_packet_total)
        self.assertEqual(1, arrival.bookkeeping["local_update_eligibility_events"])
        self.assertEqual(1, arrival.bookkeeping["local_update_events"])
        self.assertFalse(arrival.bookkeeping["delayed_evaluation_applied"])
        self.assertTrue(arrival.bookkeeping["packetized_flux_applied"])
        self.assertEqual(2, arrival.bookkeeping["checkpoint_index"])
        self.assertEqual(2.0, arrival.bookkeeping["event_time_key"])
        self.assertEqual(2.0, state_after_arrival.node_proper_time[1])
        self.assertEqual(2.0, state_after_arrival.node_last_update_event_time_key[1])
        self.assertEqual((), state_after_arrival.packet_ledger.event_queue_records)
        self.assertEqual(2, len(state_after_arrival.packet_processing_log))
        self.assertEqual(1, len(state_after_arrival.arrival_eligibility_log))
        self.assertEqual(1, len(state_after_arrival.local_update_log))
        local_update = arrival.events[2].payload
        self.assertEqual(
            LGRC9V3_LOCAL_UPDATE_EVENT_SCHEMA_VERSION,
            local_update["event_schema_version"],
        )
        self.assertTrue(local_update["packetized_flux_applied"])
        self.assertFalse(local_update["delayed_evaluation_applied"])
        self.assertEqual(0, local_update["scheduled_packet_count"])

    def test_pulse_substrate_surface_is_default_off_for_packet_events(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        result = model.step()

        self.assertNotIn(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
            [event.kind for event in result.events],
        )
        self.assertEqual(
            0,
            result.bookkeeping["causal_pulse_substrate_surface_rows"],
        )
        self.assertEqual([], model.get_state().causal_pulse_substrate_surface_log)
        self.assertNotIn(
            "causal_pulse_substrate_surface_count",
            model.compute_observables(),
        )

    def test_enabled_pulse_substrate_surface_emits_after_committed_packet_event(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        result = model.step()
        surface_events = [
            event
            for event in result.events
            if event.kind == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND
        ]

        self.assertEqual(1, len(surface_events))
        self.assertEqual(1, result.bookkeeping["causal_pulse_substrate_surface_rows"])
        self.assertEqual(1, len(model.get_state().causal_pulse_substrate_surface_log))
        self.assertEqual(
            1.0,
            model.compute_observables()["causal_pulse_substrate_surface_count"],
        )
        payload = surface_events[0].payload
        self.assertEqual(result.bookkeeping["processed_event_id"], payload["pulse_event_id"])
        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, payload["pulse_event_kind"])
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
            payload["surface_kind"],
        )
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_DERIVED_SURFACE,
            payload["surface_budget_surface"],
        )
        self.assertEqual(0.0, payload["surface_budget_error"])
        self.assertGreater(
            payload["scheduler_event_index"],
            result.events[0].payload["processed_event"]["scheduler_event_index"],
        )
        self.assertFalse(payload["claim_flags"]["movement_claim_allowed"])
        self.assertEqual(
            result.bookkeeping["processed_event_id"],
            payload["surface_values_after"]["source_event_id"],
        )

    def test_pulse_substrate_surface_emits_arrival_row_after_arrival_commit(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()

        result = model.step()
        kinds = [event.kind for event in result.events]
        surface_index = kinds.index(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND)

        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_ARRIVAL, kinds[0])
        self.assertEqual(1, surface_index)
        self.assertEqual(LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND, kinds[2])
        self.assertEqual(2, len(model.get_state().causal_pulse_substrate_surface_log))
        payload = result.events[surface_index].payload
        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_ARRIVAL, payload["pulse_event_kind"])
        self.assertEqual(result.bookkeeping["processed_event_id"], payload["pulse_event_id"])
        self.assertEqual(0.25, payload["contact_amount"])
        self.assertNotEqual(LGRC9V3_LOCAL_UPDATE_EVENT_KIND, payload["pulse_event_kind"])
        self.assertEqual(
            2,
            len(
                [
                    row
                    for row in model.get_state().causal_pulse_substrate_surface_log
                    if row.pulse_event_kind
                    in {
                        LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                        LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
                    }
                ]
            ),
        )

    def test_pulse_substrate_surface_emission_is_idempotent_per_packet_event(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        processing_result = model.get_state().packet_processing_log[-1]

        duplicate = model._emit_causal_pulse_substrate_surface_event(  # noqa: SLF001
            processing_result
        )

        self.assertIsNone(duplicate)
        self.assertEqual(1, len(model.get_state().causal_pulse_substrate_surface_log))
        row = model.get_state().causal_pulse_substrate_surface_log[0]
        expected_key = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "source_event_id": row.pulse_event_id,
                "surface_policy_id": row.surface_policy_id,
                "surface_kind": row.surface_kind,
                "route_aspect_digest": row.route_aspect_digest,
            }
        )
        self.assertIn(
            expected_key,
            model.get_state().cached_quantities[
                "lgrc9v3_causal_pulse_substrate_surface_idempotency_keys"
            ],
        )

    def test_pulse_substrate_surface_is_rejected_below_lgrc2(self) -> None:
        for runtime_level, layer_mode, proper_time_policy in (
            ("lgrc0", "annotation", "annotation"),
            ("lgrc1", "fixed_topology_semicausal", "global_scheduler"),
        ):
            params = _pulse_surface_params()
            causal_modes = dict(params["causal_modes"])  # type: ignore[index]
            causal_modes.update(
                {
                    "causal_layer_mode": layer_mode,
                    "lgrc_runtime_level": runtime_level,
                    "proper_time_accumulation_policy": proper_time_policy,
                }
            )
            params["causal_modes"] = causal_modes

            with self.assertRaisesRegex(InvalidParamsError, "LGRC-2"):
                LGRC9V3.from_state(_three_node_state(), params)

    def test_pulse_substrate_surface_rejects_topology_changing_runtime_v1(
        self,
    ) -> None:
        params = _pulse_surface_params()
        causal_modes = dict(params["causal_modes"])  # type: ignore[index]
        causal_modes.update(
            {
                "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
                "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
            }
        )
        params["causal_modes"] = causal_modes

        with self.assertRaisesRegex(InvalidParamsError, "fixed-topology"):
            LGRC9V3.from_state(_three_node_state(), params)

    def test_pulse_substrate_surface_snapshot_round_trip_and_continuation(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        before_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        before_row = before_runtime["causal_pulse_substrate_surface_log"][0]
        before_surface_digests = [
            event["payload"]["surface_digest"]
            for event in model.snapshot()["events"]
            if event["kind"] == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND
        ]
        self.assertEqual(
            before_surface_digests,
            [
                row["surface_digest"]
                for row in before_runtime["causal_pulse_substrate_surface_log"]
            ],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "lgrc9v3-surface.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        loaded_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(before_runtime, loaded_runtime)
        self.assertEqual(
            before_row["surface_digest"],
            loaded_runtime["causal_pulse_substrate_surface_log"][0]["surface_digest"],
        )
        self.assertEqual(
            _queue_signature(model),
            _queue_signature(loaded),
        )

        loaded_next = loaded.step()
        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_ARRIVAL, loaded_next.events[0].kind)
        self.assertEqual(
            2,
            len(loaded.get_state().causal_pulse_substrate_surface_log),
        )
        self.assertEqual(
            1,
            loaded_next.bookkeeping["causal_pulse_substrate_surface_rows"],
        )
        self.assertEqual(
            2,
            len(
                {
                    row.surface_digest
                    for row in loaded.get_state().causal_pulse_substrate_surface_log
                }
            ),
        )

    def test_pulse_substrate_surface_old_snapshot_without_rows_still_loads(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        snapshot = model.snapshot()
        runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
        del runtime["causal_pulse_substrate_surface_log"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "old-lgrc9v3.json"
            save_snapshot(str(path), snapshot)
            loaded = LGRC9V3.load(str(path))

        self.assertEqual([], loaded.get_state().causal_pulse_substrate_surface_log)
        self.assertNotIn(
            "causal_pulse_substrate_surface_count",
            loaded.compute_observables(),
        )

    def test_pulse_substrate_surface_disabled_policy_round_trips_empty_log(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        snapshot = model.snapshot()
        runtime = snapshot["dynamics"]["lgrc9v3_runtime"]

        self.assertIn("causal_pulse_substrate_surface_log", runtime)
        self.assertEqual([], runtime["causal_pulse_substrate_surface_log"])
        self.assertFalse(
            runtime["causal_modes"]["causal_pulse_substrate_surface_enabled"]
        )
        self.assertEqual(
            "disabled",
            runtime["causal_modes"]["causal_pulse_substrate_surface_policy"],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "disabled-lgrc9v3.json"
            save_snapshot(str(path), snapshot)
            loaded = LGRC9V3.load(str(path))

        loaded_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual([], loaded_runtime["causal_pulse_substrate_surface_log"])
        self.assertFalse(
            loaded_runtime["causal_modes"][
                "causal_pulse_substrate_surface_enabled"
            ]
        )

    def test_pulse_substrate_surface_artifact_validator_accepts_snapshot_events(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.step()

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=model.snapshot()["events"],
        )

        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertEqual(2, validation["surface_row_count"])
        self.assertEqual(2, len(validation["validated_surface_ids"]))
        self.assertFalse(validation["movement_claim_allowed"])
        self.assertFalse(validation["native_m6"])
        self.assertTrue(validation["native_lgrc_pulse_substrate_supported"])

    def test_pulse_substrate_surface_synchronous_default_noop_suppresses_producers(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        result = model.step()
        coupling = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        feedback = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        self.assertEqual([], model.get_state().causal_pulse_substrate_surface_log)
        self.assertNotIn(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
            [event.kind for event in result.events],
        )
        self.assertEqual((), coupling.production_records)
        self.assertEqual((), feedback.production_records)
        self.assertFalse(coupling.state_mutated)
        self.assertFalse(feedback.state_mutated)

    def test_pulse_substrate_surface_artifact_validator_rejects_missing_source(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        events = [
            event
            for event in model.snapshot()["events"]
            if event["kind"] != LGRC9V3_PACKET_EVENT_KIND_DEPARTURE
        ]

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=events,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("surface_row_without_committed_source_event:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_digest_mismatch(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        events = []
        for event in model.snapshot()["events"]:
            cloned = dict(event)
            if cloned["kind"] == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND:
                payload = dict(cloned["payload"])
                payload["surface_digest"] = "wrong-digest"
                cloned["payload"] = payload
            events.append(cloned)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=events,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("corrupted_surface_row:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_sub_lgrc2_row(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        events = []
        for event in model.snapshot()["events"]:
            cloned = dict(event)
            if cloned["kind"] == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND:
                payload = dict(cloned["payload"])
                payload["lgrc_runtime_level"] = "lgrc1"
                without_digest = dict(payload)
                without_digest.pop("surface_digest")
                payload["surface_digest"] = (
                    build_lgrc9v3_causal_pulse_substrate_surface_digest(
                        without_digest
                    )
                )
                cloned["payload"] = payload
            events.append(cloned)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=events,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("corrupted_surface_row:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_local_update_row(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        events = []
        for event in model.snapshot()["events"]:
            cloned = dict(event)
            if cloned["kind"] == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND:
                payload = dict(cloned["payload"])
                payload["pulse_event_kind"] = LGRC9V3_LOCAL_UPDATE_EVENT_KIND
                without_digest = dict(payload)
                without_digest.pop("surface_digest")
                payload["surface_digest"] = (
                    build_lgrc9v3_causal_pulse_substrate_surface_digest(
                        without_digest
                    )
                )
                cloned["payload"] = payload
            events.append(cloned)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=events,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("corrupted_surface_row:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_proper_time_mismatch(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        events = []
        for event in model.snapshot()["events"]:
            cloned = dict(event)
            if cloned["kind"] == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND:
                payload = dict(cloned["payload"])
                node_proper_time = dict(payload["node_proper_time"])
                node_proper_time["0"] = 0.0
                payload["node_proper_time"] = node_proper_time
                without_digest = dict(payload)
                without_digest.pop("surface_digest")
                payload["surface_digest"] = (
                    build_lgrc9v3_causal_pulse_substrate_surface_digest(
                        without_digest
                    )
                )
                cloned["payload"] = payload
            events.append(cloned)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=events,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("surface_proper_time_mismatch:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_missing_route_digest(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        events = []
        for event in model.snapshot()["events"]:
            cloned = dict(event)
            if cloned["kind"] == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND:
                payload = dict(cloned["payload"])
                del payload["route_aspect_digest"]
                cloned["payload"] = payload
            events.append(cloned)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=events,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("missing_route_aspect_digest:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_orphaned_producer(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        production_result = {
            "scheduler_event_index": 2,
            "production_records": [
                {
                    "record_id": "orphan-producer",
                    "causal_surface_digest": "missing-surface-digest",
                }
            ],
        }

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=model.snapshot()["events"],
            production_results=(production_result,),
        )

        self.assertFalse(validation["valid"])
        self.assertIn(
            "orphaned_producer_surface_reference:orphan-producer",
            validation["failure_reasons"],
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_early_producer(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        row = model.get_state().causal_pulse_substrate_surface_log[0]
        production_result = {
            "scheduler_event_index": 0,
            "production_records": [
                {
                    "record_id": "early-producer",
                    "causal_surface_digest": row.surface_digest,
                }
            ],
        }

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=model.snapshot()["events"],
            production_results=(production_result,),
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("producer_record_before_source_commitment:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_producer_mutation_gap(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        row = model.get_state().causal_pulse_substrate_surface_log[0]
        production_result = {
            "scheduler_event_index": 2,
            "production_records": [
                {
                    "record_id": "bad-producer",
                    "causal_surface_digest": row.surface_digest,
                    "reason_code": "test_scheduled",
                    "observed_evidence": {
                        "direct_coherence_write": True,
                        "direct_support_mask_write": False,
                        "direct_centroid_write": False,
                        "direct_displacement_write": False,
                        "direct_topology_write": False,
                        "direct_claim_write": False,
                        "producer_mutated_coherence": False,
                        "producer_marked_packet_processed": False,
                        "producer_emitted_claim_label": False,
                    },
                }
            ],
        }

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=model.snapshot()["events"],
            production_results=(production_result,),
        )

        self.assertFalse(validation["valid"])
        self.assertIn(
            "producer_mutation_boundary_violation:bad-producer:direct_coherence_write",
            validation["failure_reasons"],
        )

    def test_pulse_substrate_surface_artifact_validator_rejects_missing_reason_code(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        row = model.get_state().causal_pulse_substrate_surface_log[0]
        production_result = {
            "scheduler_event_index": 2,
            "production_records": [
                {
                    "record_id": "reasonless-producer",
                    "causal_surface_digest": row.surface_digest,
                    "observed_evidence": {
                        "direct_coherence_write": False,
                        "direct_support_mask_write": False,
                        "direct_centroid_write": False,
                        "direct_displacement_write": False,
                        "direct_topology_write": False,
                        "direct_claim_write": False,
                        "producer_mutated_coherence": False,
                        "producer_marked_packet_processed": False,
                        "producer_emitted_claim_label": False,
                    },
                }
            ],
        }

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=model.snapshot()["events"],
            production_results=(production_result,),
        )

        self.assertFalse(validation["valid"])
        self.assertIn(
            "producer_missing_reason_code:reasonless-producer",
            validation["failure_reasons"],
        )

    def test_pulse_substrate_coupling_producer_disabled_by_default(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        queue_before = len(model.get_state().packet_ledger.event_queue_records)

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertEqual(
            queue_before,
            len(model.get_state().packet_ledger.event_queue_records),
        )
        self.assertFalse(result.state_mutated)
        self.assertEqual(1, len(result.production_records))
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED,
            result.production_records[0].reason_code,
        )
        self.assertFalse(
            result.production_records[0].observed_evidence["movement_claim_allowed"]
        )

    def test_pulse_substrate_coupling_producer_suppressed_by_disabled_surface_policy(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=1,
            threshold=0.1,
            packet_amount=0.1,
        )
        model.get_state().causal_modes["causal_pulse_substrate_surface_enabled"] = False
        model.get_state().causal_modes["causal_pulse_substrate_surface_policy"] = (
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
        )
        queue_before = _queue_signature(model)
        log_before = list(
            model.get_state().cached_quantities.get(
                "lgrc9v3_autonomous_production_log",
                [],
            )
        )

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertEqual((), result.production_records)
        self.assertFalse(result.state_mutated)
        self.assertEqual(queue_before, _queue_signature(model))
        self.assertEqual(
            log_before,
            model.get_state().cached_quantities.get(
                "lgrc9v3_autonomous_production_log",
                [],
            ),
        )

    def test_pulse_substrate_coupling_producer_schedules_via_packet_queue_only(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=1,
            threshold=0.1,
            packet_amount=0.1,
        )
        source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
        claim_flags_before = [dict(row.claim_flags) for row in model.get_state().causal_pulse_substrate_surface_log]
        coherence_before = {
            node_id: state.coherence
            for node_id, state in model.get_state().base_state.nodes.items()
        }
        queue_before = _queue_signature(model)

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertEqual(
            len(queue_before) + 1,
            len(model.get_state().packet_ledger.event_queue_records),
        )
        self.assertEqual(
            queue_before,
            _queue_signature(model)[: len(queue_before)],
        )
        self.assertEqual(
            coherence_before,
            {
                node_id: state.coherence
                for node_id, state in model.get_state().base_state.nodes.items()
            },
        )
        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
            record.reason_code,
        )
        self.assertEqual(source_row.surface_digest, record.causal_surface_digest)
        self.assertEqual(source_row.surface_digest, record.observed_evidence["surface_digest"])
        self.assertEqual(1, record.trigger_node_id)
        self.assertEqual(1, record.trigger_edge_id)
        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, record.scheduled_event_kind)
        self.assertIsNotNone(record.scheduled_event_id)
        self.assertEqual(0.25, record.observed_evidence["observed_value"])
        self.assertEqual(0.0, record.observed_evidence["reference_value"])
        self.assertEqual(
            "serialized_producer_policy",
            record.observed_evidence["reference_value_source"],
        )
        self.assertEqual(
            "serialized_producer_policy",
            record.observed_evidence["threshold_source"],
        )
        self.assertEqual(0.1, record.thresholds["threshold"])
        self.assertFalse(record.observed_evidence["direct_coherence_write"])
        self.assertFalse(record.observed_evidence["direct_support_mask_write"])
        self.assertFalse(record.observed_evidence["direct_centroid_write"])
        self.assertFalse(record.observed_evidence["direct_displacement_write"])
        self.assertFalse(record.observed_evidence["direct_topology_write"])
        self.assertFalse(record.observed_evidence["direct_claim_write"])
        self.assertFalse(record.observed_evidence["producer_mutated_coherence"])
        self.assertFalse(record.observed_evidence["producer_marked_packet_processed"])
        self.assertFalse(record.observed_evidence["producer_emitted_claim_label"])
        self.assertFalse(record.observed_evidence["movement_claim_allowed"])
        self.assertEqual(
            claim_flags_before,
            [dict(row.claim_flags) for row in model.get_state().causal_pulse_substrate_surface_log],
        )
        self.assertGreaterEqual(
            result.scheduler_event_index,
            source_row.scheduler_event_index,
        )
        self.assertGreater(
            model.get_state().packet_ledger.event_queue_records[-1].scheduler_event_index,
            result.scheduler_event_index,
        )

        model.step()
        model.step()
        model.step()
        model.step()
        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=model.snapshot()["events"],
            production_results=(result.to_artifact(),),
        )
        self.assertTrue(validation["valid"], validation["failure_reasons"])

    def test_pulse_substrate_coupling_producer_subthreshold_is_negative(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=1,
            threshold=0.3,
            packet_amount=0.1,
        )
        queue_before = len(model.get_state().packet_ledger.event_queue_records)

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertEqual(
            queue_before,
            len(model.get_state().packet_ledger.event_queue_records),
        )
        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD,
            record.reason_code,
        )
        self.assertEqual(0.25, record.observed_evidence["response_value"])
        self.assertEqual(0.3, record.thresholds["threshold"])
        self.assertIsNone(record.scheduled_event_id)

    def test_pulse_substrate_coupling_producer_duplicate_suppression(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=1,
            threshold=0.1,
            packet_amount=0.1,
        )
        first = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        queue_after_first = len(model.get_state().packet_ledger.event_queue_records)

        second = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
            first.production_records[0].reason_code,
        )
        self.assertEqual(
            queue_after_first,
            len(model.get_state().packet_ledger.event_queue_records),
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            second.production_records[0].reason_code,
        )
        self.assertEqual(
            first.production_records[0].idempotency_key,
            second.production_records[0].idempotency_key,
        )

        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=1,
            threshold=0.2,
            packet_amount=0.1,
        )
        third = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
            third.production_records[0].reason_code,
        )
        self.assertNotEqual(
            first.production_records[0].idempotency_key,
            third.production_records[0].idempotency_key,
        )

    def test_pulse_substrate_coupling_producer_policy_round_trips(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=1,
            threshold=0.1,
            packet_amount=0.1,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "coupling-producer.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        result = loaded.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
            result.production_records[0].reason_code,
        )

    def test_feedback_coupled_pulse_producer_disabled_by_default(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        queue_before = len(model.get_state().packet_ledger.event_queue_records)

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        self.assertEqual(
            queue_before,
            len(model.get_state().packet_ledger.event_queue_records),
        )
        self.assertFalse(result.state_mutated)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED,
            result.production_records[0].reason_code,
        )
        self.assertFalse(result.production_records[0].observed_evidence["native_m6"])

    def test_feedback_coupled_pulse_producer_suppressed_by_disabled_surface_policy(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=(2,),
            rear_node_ids=(0,),
            feedback_threshold=0.5,
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            threshold=0.5,
            packet_amount=0.1,
        )
        model.get_state().causal_modes["causal_pulse_substrate_surface_enabled"] = False
        model.get_state().causal_modes["causal_pulse_substrate_surface_policy"] = (
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
        )
        queue_before = _queue_signature(model)

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        self.assertEqual((), result.production_records)
        self.assertFalse(result.state_mutated)
        self.assertEqual(queue_before, _queue_signature(model))

    def test_feedback_surface_and_producer_schedule_via_packet_queue_only(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        feedback_row = model.emit_feedback_eligibility_surface_row(
            front_node_ids=(2,),
            rear_node_ids=(0,),
            feedback_threshold=0.5,
            expected_next_route_id="feedback-route-v1",
            expected_next_channel_id="edge:1",
        )
        self.assertEqual(
            "feedback_eligibility",
            feedback_row.surface_kind,
        )
        self.assertGreater(
            feedback_row.scheduler_event_index,
            source_surface.scheduler_event_index,
        )
        self.assertEqual(
            source_surface.surface_digest,
            feedback_row.surface_values_after["source_surface_digest"],
        )
        self.assertEqual(
            [2],
            feedback_row.surface_update_policy["declared_front_node_ids"],
        )
        self.assertEqual(
            [0],
            feedback_row.surface_update_policy["declared_rear_node_ids"],
        )
        self.assertEqual(
            2.25,
            feedback_row.surface_values_after["boundary_polarity_score"],
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            threshold=0.5,
            packet_amount=0.1,
            expected_source_surface_digest=source_surface.surface_digest,
            expected_next_route_id="feedback-route-v1",
            expected_next_channel_id="edge:1",
        )
        claim_flags_before = [dict(row.claim_flags) for row in model.get_state().causal_pulse_substrate_surface_log]
        coherence_before = {
            node_id: state.coherence
            for node_id, state in model.get_state().base_state.nodes.items()
        }
        queue_before = _queue_signature(model)

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        self.assertEqual(
            coherence_before,
            {
                node_id: state.coherence
                for node_id, state in model.get_state().base_state.nodes.items()
            },
        )
        self.assertEqual(queue_before, _queue_signature(model)[: len(queue_before)])
        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
            record.reason_code,
        )
        self.assertEqual(feedback_row.surface_digest, record.causal_surface_digest)
        self.assertEqual("positive", record.thresholds["expected_polarity"])
        self.assertEqual("feedback-route-v1", record.observed_evidence["expected_next_route_id"])
        self.assertEqual("edge:1", record.observed_evidence["expected_next_channel_id"])
        self.assertEqual(
            "serialized_producer_policy",
            record.observed_evidence["threshold_source"],
        )
        self.assertEqual(
            "serialized_producer_policy",
            record.observed_evidence["polarity_policy_source"],
        )
        self.assertEqual(
            "feedback_eligibility",
            record.observed_evidence["regenerated_pulse_source"],
        )
        self.assertFalse(record.observed_evidence["copied_from_original_schedule"])
        self.assertFalse(record.observed_evidence["direct_claim_write"])
        self.assertFalse(record.observed_evidence["producer_mutated_coherence"])
        self.assertFalse(record.observed_evidence["producer_marked_packet_processed"])
        self.assertFalse(record.observed_evidence["producer_emitted_claim_label"])
        self.assertFalse(record.observed_evidence["native_m6"])
        self.assertFalse(record.observed_evidence["movement_claim_allowed"])
        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, record.scheduled_event_kind)
        self.assertEqual(
            claim_flags_before,
            [dict(row.claim_flags) for row in model.get_state().causal_pulse_substrate_surface_log],
        )
        self.assertGreaterEqual(
            result.scheduler_event_index,
            feedback_row.scheduler_event_index,
        )

        model.step()
        model.step()
        validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
            events=model.snapshot()["events"],
            production_results=(result.to_artifact(),),
        )
        self.assertTrue(validation["valid"], validation["failure_reasons"])

    def test_feedback_coupled_pulse_subthreshold_and_wrong_polarity_are_negative(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=(2,),
            rear_node_ids=(0,),
            feedback_threshold=0.5,
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            threshold=3.0,
            packet_amount=0.1,
        )
        subthreshold = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
            subthreshold.production_records[0].reason_code,
        )

        model.set_feedback_coupled_pulse_producer(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            threshold=0.5,
            packet_amount=0.1,
            expected_polarity="negative",
        )
        wrong_polarity = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
            wrong_polarity.production_records[0].reason_code,
        )

    def test_feedback_coupled_pulse_order_mismatch_blocks_scheduling(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=(2,),
            rear_node_ids=(0,),
            feedback_threshold=0.5,
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            threshold=0.5,
            packet_amount=0.1,
            expected_source_surface_digest="wrong-source-surface-digest",
        )
        queue_before = len(model.get_state().packet_ledger.event_queue_records)

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        self.assertEqual(
            queue_before,
            len(model.get_state().packet_ledger.event_queue_records),
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH,
            result.production_records[0].reason_code,
        )

    def test_feedback_coupled_pulse_duplicate_suppression(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=(2,),
            rear_node_ids=(0,),
            feedback_threshold=0.5,
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            threshold=0.5,
            packet_amount=0.1,
        )
        first = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )
        queue_after_first = len(model.get_state().packet_ledger.event_queue_records)

        second = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
            first.production_records[0].reason_code,
        )
        self.assertEqual(
            queue_after_first,
            len(model.get_state().packet_ledger.event_queue_records),
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            second.production_records[0].reason_code,
        )
        self.assertEqual(
            first.production_records[0].idempotency_key,
            second.production_records[0].idempotency_key,
        )

    def test_feedback_coupled_pulse_producer_policy_round_trips(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=(2,),
            rear_node_ids=(0,),
            feedback_threshold=0.5,
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            threshold=0.5,
            packet_amount=0.1,
            expected_source_surface_digest=source_surface.surface_digest,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "feedback-producer.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        result = loaded.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
            result.production_records[0].reason_code,
        )

    def test_feedback_coupled_pulse_budget_violation_fails_closed(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=(2,),
            rear_node_ids=(0,),
            feedback_threshold=0.5,
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            threshold=0.5,
            packet_amount=100.0,
        )

        with self.assertRaisesRegex(InvalidStateTransitionError, "exceeds"):
            model.produce_events(
                policy=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
                )
            )

    def test_arrival_local_update_can_schedule_outbound_causal_flux(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.set_causal_flux_routes(
            {
                1: [
                    {
                        "target_node_id": 2,
                        "edge_id": 1,
                        "amount_fraction": 1.0,
                    }
                ]
            }
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        results = model.run_event_queue(max_events=10)
        state = model.get_state()

        self.assertEqual(4, len(results))
        self.assertEqual((), state.packet_ledger.event_queue_records)
        self.assertAlmostEqual(0.75, state.base_state.nodes[0].coherence)
        self.assertAlmostEqual(2.0, state.base_state.nodes[1].coherence)
        self.assertAlmostEqual(3.25, state.base_state.nodes[2].coherence)
        self.assertAlmostEqual(0.0, state.packet_ledger.in_flight_packet_total)
        self.assertAlmostEqual(6.0, state.packet_ledger.conserved_budget_total)
        self.assertEqual(2, len(state.local_update_log))
        self.assertEqual(1, state.local_update_log[0]["scheduled_packet_count"])
        self.assertEqual(0, state.local_update_log[1]["scheduled_packet_count"])

    def test_run_event_queue_stops_when_queue_is_empty(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        self.assertEqual([], model.run_event_queue(max_events=0))
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        results = model.run_event_queue(max_events=10)

        self.assertEqual(2, len(results))
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertEqual([], model.run_event_queue(max_events=10))

    def test_run_event_queue_processes_birth_only_queue(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )
        model.schedule_causal_boundary_birth_trial(
            parent_node_id=0,
            parent_port_id=3,
            outward_flux_pressure=2.0,
            rng_sample=0.1,
            event_time_key=4.0,
            scheduler_event_index=4,
            edge_delay=2.5,
        )

        results = model.run_event_queue(max_events=10)

        self.assertEqual(1, len(results))
        self.assertEqual(
            LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND,
            results[0].events[0].kind,
        )
        self.assertEqual(
            "lgrc9v3_causal_boundary_birth_trial",
            results[0].bookkeeping["processed_event_kind"],
        )
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertEqual([], model.get_state().boundary_birth_trial_queue)

    def test_run_event_queue_interleaves_packet_and_birth_queues(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )
        initial_budget = _runtime_budget_surface(model)
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.schedule_causal_boundary_birth_trial(
            parent_node_id=0,
            parent_port_id=3,
            outward_flux_pressure=2.0,
            rng_sample=0.1,
            event_time_key=1.5,
            scheduler_event_index=2,
            edge_delay=2.5,
        )

        results = model.run_event_queue(max_events=10)
        processed_kinds = [
            str(result.bookkeeping["processed_event_kind"]) for result in results
        ]
        event_kinds = [event.kind for result in results for event in result.events]

        self.assertEqual(
            [
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                "lgrc9v3_causal_boundary_birth_trial",
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            ],
            processed_kinds,
        )
        self.assertIn(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, event_kinds)
        self.assertIn(LGRC9V3_PACKET_EVENT_KIND_ARRIVAL, event_kinds)
        self.assertIn(LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND, event_kinds)
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertEqual([], model.get_state().boundary_birth_trial_queue)
        self.assertAlmostEqual(initial_budget, _runtime_budget_surface(model))

    def test_bounded_event_queue_does_not_starve_interleaved_packets(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.set_causal_flux_routes(
            {
                1: [
                    {
                        "target_node_id": 2,
                        "edge_id": 1,
                        "amount_fraction": 0.5,
                    }
                ]
            }
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            amount=0.2,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
            packet_index=0,
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=2,
            packet_index=1,
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.3,
            departure_event_time_key=1.5,
            scheduler_event_index=3,
            packet_index=2,
        )
        initial_event_ids = {
            event.event_id
            for event in model.get_state().packet_ledger.event_queue_records
        }

        results = model.run_event_queue(max_events=20)
        processed_ids = [
            result.bookkeeping["processed_event_id"] for result in results
        ]
        processed_times = [
            float(result.bookkeeping["event_time_key"]) for result in results
        ]
        processed_kinds = [
            result.bookkeeping["processed_event_kind"] for result in results
        ]

        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertLessEqual(len(results), 20)
        self.assertTrue(initial_event_ids.issubset(set(processed_ids)))
        self.assertEqual(len(processed_ids), len(set(processed_ids)))
        self.assertEqual(sorted(processed_times), processed_times)
        self.assertEqual(4, processed_kinds.count(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE))
        self.assertEqual(4, processed_kinds.count(LGRC9V3_PACKET_EVENT_KIND_ARRIVAL))

    def test_many_event_packet_budget_is_audited_after_each_step(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        initial_budget = _runtime_budget_surface(model)
        model.set_causal_flux_routes(
            {
                1: [
                    {
                        "target_node_id": 2,
                        "edge_id": 1,
                        "amount_fraction": 0.5,
                    }
                ]
            }
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            amount=0.2,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
            packet_index=0,
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=2,
            packet_index=1,
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.3,
            departure_event_time_key=1.5,
            scheduler_event_index=3,
            packet_index=2,
        )

        processed = 0
        while model.get_state().packet_ledger.event_queue_records:
            result = model.step()
            processed += 1
            packet_payload = result.events[0].payload
            self.assertAlmostEqual(0.0, packet_payload["budget_error"])
            self.assertAlmostEqual(
                packet_payload["budget_before"],
                packet_payload["budget_after"],
            )
            self.assertAlmostEqual(initial_budget, _runtime_budget_surface(model))
            self.assertAlmostEqual(
                initial_budget,
                model.get_state().packet_ledger.conserved_budget_total,
            )
            for node in model.get_state().base_state.nodes.values():
                self.assertGreaterEqual(node.coherence, -1e-12)

        self.assertGreaterEqual(processed, 5)
        self.assertEqual(0.0, model.get_state().packet_ledger.in_flight_packet_total)

    def test_unit_lapse_constant_delay_is_named_synchronous_limit_surface(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)

        self.assertEqual(LAPSE_POLICY_UNIT, model.get_state().causal_modes["lapse_policy"])
        self.assertEqual(
            EDGE_DELAY_POLICY_CONSTANT_DELAY,
            model.get_state().causal_modes["edge_delay_policy"],
        )
        self.assertEqual({0: 1.0, 1: 1.0, 2: 1.0}, model.get_state().edge_causal_delay)

        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=4.0,
            scheduler_event_index=4,
        )
        departure = model.step()
        arrival = model.step()

        self.assertEqual(4.0, departure.time)
        self.assertEqual(5.0, arrival.time)
        self.assertEqual(4.0, model.get_state().node_proper_time[0])
        self.assertEqual(5.0, model.get_state().node_proper_time[1])
        self.assertEqual(5.0, model.get_state().node_last_update_event_time_key[1])
        self.assertFalse(arrival.bookkeeping["delayed_evaluation_applied"])
        self.assertTrue(arrival.bookkeeping["packetized_flux_applied"])

    def test_large_delay_changes_causal_arrival_surface(self) -> None:
        constant_delay = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        constant_delay.set_causal_flux_routes(
            {1: [{"target_node_id": 2, "edge_id": 1, "amount_fraction": 1.0}]}
        )
        constant_delay.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        constant_delay.run_event_queue(max_events=10)

        large_delay = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        large_delay.get_state().edge_causal_delay[1] = 10.0
        large_delay.set_causal_flux_routes(
            {1: [{"target_node_id": 2, "edge_id": 1, "amount_fraction": 1.0}]}
        )
        large_delay.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        partial = large_delay.run_event_queue(max_events=3)

        self.assertAlmostEqual(3.25, constant_delay.get_state().base_state.nodes[2].coherence)
        self.assertAlmostEqual(3.0, large_delay.get_state().base_state.nodes[2].coherence)
        self.assertEqual(3, len(partial))
        self.assertEqual(1, len(large_delay.get_state().packet_ledger.event_queue_records))
        self.assertEqual(
            12.0,
            large_delay.get_state().packet_ledger.event_queue_records[0].event_time_key,
        )

    def test_arrival_local_update_can_emit_lane_b_causal_column_h_candidate(self) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(),
            _spark_params(spark_lane="grc9v3_column_h_assisted"),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        model.step()
        arrival = model.step()
        causal_candidates = [
            event
            for event in arrival.events
            if event.kind == LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND
        ]

        self.assertEqual(1, len(causal_candidates))
        payload = causal_candidates[0].payload
        self.assertEqual(
            LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_SCHEMA_VERSION,
            payload["event_schema_version"],
        )
        self.assertEqual("grc9v3_column_h_assisted", payload["spark_lane"])
        self.assertTrue(payload["lane_b_candidate_hit"])
        self.assertFalse(payload["signed_hessian_hit"])
        self.assertTrue(payload["column_h_branch_hit"])
        self.assertEqual(["column_h_threshold_hit"], payload["gate_reasons"])
        self.assertEqual(
            "arrival_local_update_completion",
            payload["causal_spark_trigger_source"],
        )
        self.assertEqual(LGRC9V3_LOCAL_UPDATE_EVENT_KIND, payload["causal_spark_trigger_kind"])
        self.assertEqual(2, payload["scheduler_event_index"])
        self.assertEqual(2.0, payload["event_time_key"])
        self.assertFalse(payload["topology_mutated"])
        self.assertFalse(payload["mechanical_expansion_emitted"])
        self.assertFalse(payload["identity_acceptance_emitted"])
        self.assertEqual(10, len(payload["pre_expansion_topology_signature"]["node_ids"]))
        snapshot = model.snapshot()
        runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(1, runtime["causal_spark_evaluation_index"])
        self.assertEqual(1, len(runtime["causal_spark_diagnostic_log"]))
        self.assertEqual(
            [payload["candidate_event_id"]],
            runtime["causal_spark_diagnostic_log"][0]["candidate_event_ids"],
        )

    def test_first_causal_lane_b_evaluation_has_no_previous_h_crossing(self) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(),
            _spark_params(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        model.step()
        arrival = model.step()
        payload = [
            event.payload
            for event in arrival.events
            if event.kind == LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND
        ][0]

        self.assertEqual("unavailable_new_or_first_step", payload["previous_column_h_status"])
        self.assertFalse(payload["column_h_sign_crossing_hit"])
        self.assertEqual(1, payload["causal_spark_evaluation_index"])
        self.assertFalse(payload["synchronous_step_index_used_for_history"])

    def test_causal_lane_b_large_gradient_column_h_hit_is_blocked(self) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(gradient=[1.0, 0.0, 0.0]),
            _spark_params(spark_lane="grc9v3_column_h_assisted"),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        model.step()
        arrival = model.step()

        self.assertFalse(
            [
                event
                for event in arrival.events
                if event.kind == LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND
            ]
        )
        self.assertEqual(1, model.get_state().causal_spark_evaluation_index)

    def test_explicit_causal_diagnostic_preserves_lane_a_signed_hessian_attribution(self) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(signed_hessian=[-0.1, 0.2, 0.3]),
            _spark_params(),
        )

        before_nodes = tuple(model.get_state().base_state.topology.iter_live_node_ids())
        events = model.evaluate_causal_spark_diagnostics(
            trigger_kind="explicit_diagnostic_event",
            trigger_event_id="manual-diagnostic-1",
            trigger_source="explicit_api_call",
            trigger_node_id=0,
        )
        after_nodes = tuple(model.get_state().base_state.topology.iter_live_node_ids())

        self.assertEqual(before_nodes, after_nodes)
        self.assertEqual(1, len(events))
        payload = events[0].payload
        self.assertEqual(LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND, events[0].kind)
        self.assertEqual("current_hybrid_signed_hessian", payload["spark_lane"])
        self.assertTrue(payload["signed_hessian_degeneracy_gate"])
        self.assertNotIn("lane_b_candidate_hit", payload)
        self.assertEqual("explicit_api_call", payload["causal_spark_trigger_source"])
        self.assertFalse(payload["topology_mutated"])
        self.assertFalse(payload["mechanical_expansion_emitted"])

    def test_causal_boundary_birth_is_disabled_by_default(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(enabled=False),
        )
        before_nodes = tuple(model.get_state().base_state.topology.iter_live_node_ids())

        events = model.apply_causal_boundary_birth_trial(
            parent_node_id=0,
            parent_port_id=3,
            outward_flux_pressure=2.0,
            rng_sample=0.0,
            event_time_key=4.0,
            scheduler_event_index=4,
        )

        self.assertEqual([], events)
        self.assertEqual(
            before_nodes,
            tuple(model.get_state().base_state.topology.iter_live_node_ids()),
        )
        self.assertEqual(
            "disabled",
            model.get_state().base_state.cached_quantities[
                "last_causal_boundary_birth_status"
            ],
        )

    def test_causal_boundary_birth_uses_grc9v3_probability_and_preserves_budget(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )
        budget_before = _runtime_budget_surface(model)

        events = model.apply_causal_boundary_birth_trial(
            parent_node_id=0,
            parent_port_id=3,
            outward_flux_pressure=2.0,
            rng_sample=0.1,
            event_time_key=4.0,
            scheduler_event_index=4,
            edge_delay=2.5,
        )

        self.assertEqual(1, len(events))
        event = events[0]
        payload = event.payload
        self.assertEqual(LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND, event.kind)
        self.assertEqual(
            LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_SCHEMA_VERSION,
            payload["event_schema_version"],
        )
        self.assertAlmostEqual(
            1.0 - math.exp(-2.0),
            payload["birth_probability"],
        )
        self.assertEqual(0.1, payload["rng_sample"])
        self.assertEqual(1.0, payload["coherence_transfer"])
        self.assertEqual(4.0, payload["parent_coherence_before"])
        self.assertEqual(3.0, payload["parent_coherence_after"])
        self.assertEqual(1.0, payload["child_coherence"])
        self.assertAlmostEqual(0.0, payload["budget_error"])
        self.assertAlmostEqual(budget_before, _runtime_budget_surface(model))
        self.assertEqual(4.0, model.get_state().node_proper_time[0])
        self.assertEqual(4.0, model.get_state().node_proper_time[payload["child_node_id"]])
        self.assertEqual(2.5, model.get_state().edge_causal_delay[payload["edge_id"]])
        self.assertEqual(2.5, model.get_state().base_state.temporal_delay[payload["edge_id"]])
        self.assertTrue(payload["topology_mutated"])
        self.assertFalse(payload["spark_event_emitted"])
        self.assertFalse(payload["mechanical_expansion_emitted"])
        self.assertFalse(payload["identity_acceptance_emitted"])
        self.assertEqual(
            "packets_scheduled_after_birth_see_child",
            payload["packet_visibility"],
        )
        restored = json.loads(json.dumps(payload, sort_keys=True))
        self.assertEqual(payload["child_node_id"], restored["child_node_id"])
        runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(1, len(runtime["topology_event_log"]))

    def test_causal_boundary_birth_rejects_when_rng_does_not_accept(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )

        events = model.apply_causal_boundary_birth_trial(
            parent_node_id=0,
            parent_port_id=3,
            outward_flux_pressure=0.01,
            rng_sample=0.99,
            event_time_key=4.0,
            scheduler_event_index=4,
        )

        self.assertEqual([], events)
        self.assertEqual(3, len(tuple(model.get_state().base_state.topology.iter_live_node_ids())))
        self.assertEqual(
            "rng_rejected",
            model.get_state().base_state.cached_quantities[
                "last_causal_boundary_birth_status"
            ],
        )

    def test_causal_boundary_birth_rejects_queued_packets_until_topology_routing(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        with self.assertRaises(InvalidStateTransitionError):
            model.apply_causal_boundary_birth_trial(
                parent_node_id=0,
                parent_port_id=3,
                outward_flux_pressure=2.0,
                rng_sample=0.1,
                event_time_key=4.0,
                scheduler_event_index=4,
            )

    def test_scheduled_causal_boundary_birth_routes_through_step(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )
        model.schedule_causal_boundary_birth_trial(
            parent_node_id=0,
            parent_port_id=3,
            outward_flux_pressure=2.0,
            rng_sample=0.1,
            event_time_key=4.0,
            scheduler_event_index=4,
            edge_delay=2.5,
        )

        result = model.step()

        self.assertEqual(1, len(result.events))
        self.assertEqual(LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND, result.events[0].kind)
        self.assertEqual(1, result.bookkeeping["topology_events_routed"])
        self.assertEqual(0, result.bookkeeping["boundary_birth_trial_queue_after"])
        self.assertAlmostEqual(0.0, result.events[0].payload["budget_error"])

    def test_active_topology_integration_expands_causal_lane_b_candidate(self) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(),
            _active_topology_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

        model.step()
        arrival = model.step()
        kinds = [event.kind for event in arrival.events]

        self.assertIn(LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND, kinds)
        self.assertIn("hybrid_mechanical_expansion", kinds)
        self.assertIn(LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT, kinds)
        self.assertIn(LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE, kinds)
        expansion = [
            event for event in arrival.events if event.kind == "hybrid_mechanical_expansion"
        ][0]
        candidate = [
            event
            for event in arrival.events
            if event.kind == LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND
        ][0]
        inheritance = [
            event
            for event in arrival.events
            if event.kind == LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE
        ][0]

        self.assertEqual(
            candidate.payload["candidate_event_id"],
            expansion.payload["source_candidate_event_id"],
        )
        self.assertEqual(2.0, expansion.payload["event_time_key"])
        self.assertAlmostEqual(0.0, expansion.payload["budget_error"])
        self.assertFalse(expansion.payload["identity_acceptance_emitted"])
        self.assertEqual(
            expansion.payload["expansion_id"],
            inheritance.payload["source_expansion_event_id"],
        )
        for child_node_id in expansion.payload["module_node_ids"]:
            self.assertEqual(2.0, model.get_state().node_proper_time[child_node_id])
        self.assertGreater(arrival.bookkeeping["causal_topology_integration_events"], 0)
        self.assertGreater(len(model.get_state().topology_event_log), 0)

    def test_runtime_collapse_and_identity_routes_are_policy_gated(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_params(collapse_allowed=True, identity_allowed=True),
        )
        model.get_state().node_proper_time[0] = 5.0
        collapse_events = model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )

        self.assertEqual(1, len(collapse_events))
        self.assertEqual(LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE, collapse_events[0].kind)
        self.assertAlmostEqual(0.0, collapse_events[0].payload["budget_error"])
        self.assertEqual({"1": "sink-0"}, collapse_events[0].payload["lineage_transfer_map"])
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=[collapse_events[0].payload["topology_event_id"]],
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            sink_node_id=0,
            lineage_id="sink-0",
            basin_node_ids=[0],
            node_proper_time=model.get_state().node_proper_time,
            window_start_sink_proper_time=0.0,
            window_start_event_time_key=0.0,
            window_end_event_time_key=5.0,
            scheduler_event_index=0,
            checkpoint_index=0,
            event_time_key=5.0,
            local_median_edge_delay=1.0,
            threshold_multiplier=1.0,
        )
        identity_event = model.emit_causal_identity_acceptance(evaluation)

        self.assertEqual(LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE, identity_event.kind)
        self.assertTrue(identity_event.payload["identity_acceptance_emitted"])
        self.assertFalse(identity_event.payload["topology_mutated"])
        self.assertAlmostEqual(0.0, identity_event.payload["budget_error"])

        disabled = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_params(collapse_allowed=False, identity_allowed=False),
        )
        with self.assertRaises(Exception):
            disabled.emit_causal_identity_acceptance(evaluation)

    def test_topology_state_reabsorption_updates_active_state_after_collapse(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        ledger_before = model.get_state().packet_ledger
        self.assertIsNotNone(ledger_before)
        self.assertAlmostEqual(5.9, ledger_before.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(0.1, ledger_before.in_flight_packet_total)  # type: ignore[union-attr]

        collapse_events = model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "source-port", 2: "target-port"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        self.assertEqual(2, len(collapse_events))
        state = model.get_state()
        ledger_after = state.packet_ledger
        self.assertIsNotNone(ledger_after)
        active_total = sum(node.coherence for node in state.base_state.nodes.values())
        self.assertAlmostEqual(6.0, active_total)
        self.assertAlmostEqual(ledger_after.node_coherence_total, active_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(0.0, ledger_after.in_flight_packet_total)  # type: ignore[union-attr]
        self.assertFalse(ledger_after.fixed_topology)  # type: ignore[union-attr]
        self.assertTrue(ledger_after.topology_change_allowed)  # type: ignore[union-attr]
        self.assertTrue(ledger_after.packet_transport_through_topology_change)  # type: ignore[union-attr]
        self.assertEqual(LGRC_RUNTIME_LEVEL_LGRC3, ledger_after.lgrc_runtime_level)  # type: ignore[union-attr]
        self.assertEqual(1, len(state.topology_state_reabsorption_log))
        record = state.topology_state_reabsorption_log[0]
        self.assertEqual(
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED,
            record.state_reabsorption_action,
        )
        self.assertEqual(collapse_events[0].payload["topology_event_id"], record.topology_event_id)
        self.assertTrue(record.topology_event_committed)
        self.assertEqual({"1": "0", "2": "0"}, dict(record.lineage_transfer_map))
        self.assertEqual((1, 2), tuple(record.source_node_ids))
        self.assertEqual((0,), tuple(record.target_node_ids))
        self.assertEqual((1,), tuple(record.retired_node_ids))
        self.assertAlmostEqual(5.9, record.active_node_state_total_before)
        self.assertAlmostEqual(6.0, record.active_node_state_total_after)
        self.assertAlmostEqual(0.0, record.node_plus_packet_budget_error)
        self.assertFalse(any(record.claim_flags.values()))

        runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(1, len(runtime["topology_state_reabsorption_log"]))
        self.assertEqual(
            record.to_artifact()["lineage_transfer_map_digest"],
            runtime["topology_state_reabsorption_log"][0][
                "lineage_transfer_map_digest"
            ],
        )
        self.assertEqual(
            record.topology_state_reabsorption_digest,
            runtime["topology_state_reabsorption_log"][0][
                "topology_state_reabsorption_digest"
            ],
        )

    def test_topology_state_reabsorption_default_off_keeps_old_mismatch(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "source-port", 2: "target-port"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        state = model.get_state()
        ledger = state.packet_ledger
        self.assertIsNotNone(ledger)
        active_total = sum(node.coherence for node in state.base_state.nodes.values())
        self.assertAlmostEqual(5.9, active_total)
        self.assertAlmostEqual(6.0, ledger.node_coherence_total)  # type: ignore[union-attr]
        self.assertEqual([], state.topology_state_reabsorption_log)

    def test_lgrc3_packet_processing_continues_after_state_reabsorption(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "source-port", 2: "target-port"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            amount=0.1,
            departure_event_time_key=2.0,
            scheduler_event_index=2,
        )
        departure = model.step()
        ledger_after_departure = model.get_state().packet_ledger
        self.assertIsNotNone(ledger_after_departure)
        active_after_departure = sum(
            node.coherence for node in model.get_state().base_state.nodes.values()
        )
        self.assertIn(
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            [event.kind for event in departure.events],
        )
        self.assertAlmostEqual(5.9, active_after_departure)
        self.assertAlmostEqual(5.9, ledger_after_departure.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(0.1, ledger_after_departure.in_flight_packet_total)  # type: ignore[union-attr]
        self.assertFalse(ledger_after_departure.fixed_topology)  # type: ignore[union-attr]
        self.assertTrue(ledger_after_departure.topology_change_allowed)  # type: ignore[union-attr]

        arrival = model.step()
        ledger_after_arrival = model.get_state().packet_ledger
        self.assertIsNotNone(ledger_after_arrival)
        active_after_arrival = sum(
            node.coherence for node in model.get_state().base_state.nodes.values()
        )
        self.assertIn(
            LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            [event.kind for event in arrival.events],
        )
        self.assertAlmostEqual(6.0, active_after_arrival)
        self.assertAlmostEqual(6.0, ledger_after_arrival.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(0.0, ledger_after_arrival.in_flight_packet_total)  # type: ignore[union-attr]
        self.assertFalse(ledger_after_arrival.fixed_topology)  # type: ignore[union-attr]
        self.assertTrue(ledger_after_arrival.packet_transport_through_topology_change)  # type: ignore[union-attr]

    def test_coupling_producer_schedules_from_reabsorbed_transported_surface(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        state = model.get_state()
        transported_row = state.causal_pulse_substrate_surface_log[-1]
        state_record = state.topology_state_reabsorption_log[-1]
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertTrue(result.state_mutated)
        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
            record.reason_code,
        )
        self.assertEqual(transported_row.surface_digest, record.causal_surface_digest)
        self.assertEqual(
            state_record.topology_event_digest,
            record.observed_evidence["topology_event_digest"],
        )
        self.assertEqual(
            state_record.topology_state_reabsorption_digest,
            record.observed_evidence["topology_state_reabsorption_record_digest"],
        )
        self.assertTrue(
            record.observed_evidence["topology_state_reabsorption_verified"]
        )
        self.assertTrue(record.observed_evidence["producer_reads_transport_successor"])
        self.assertFalse(record.observed_evidence["producer_mutated_coherence"])
        self.assertFalse(record.observed_evidence["direct_topology_write"])
        self.assertFalse(record.observed_evidence["movement_claim_allowed"])
        self.assertIsNotNone(record.scheduled_event_id)

        departure = model.step()
        self.assertIn(
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            [event.kind for event in departure.events],
        )
        ledger = model.get_state().packet_ledger
        self.assertIsNotNone(ledger)
        active_after_departure = sum(
            node.coherence for node in model.get_state().base_state.nodes.values()
        )
        self.assertAlmostEqual(active_after_departure, ledger.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(5.9, ledger.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(0.1, ledger.in_flight_packet_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(6.0, ledger.conserved_budget_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(6.0, active_after_departure + ledger.in_flight_packet_total)  # type: ignore[union-attr]
        self.assertGreaterEqual(
            min(node.coherence for node in model.get_state().base_state.nodes.values()),
            0.0,
        )

    def test_coupling_producer_blocks_transported_surface_without_reabsorption(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        transported_row = model.get_state().causal_pulse_substrate_surface_log[-1]
        self.assertEqual([], model.get_state().topology_state_reabsorption_log)
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertFalse(result.state_mutated)
        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED,
            record.reason_code,
        )
        self.assertEqual(transported_row.surface_digest, record.causal_surface_digest)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED,
            record.observed_evidence["primary_blocker"],
        )
        self.assertFalse(
            record.observed_evidence["topology_state_reabsorption_verified"]
        )
        self.assertIsNone(record.scheduled_event_id)

    def test_feedback_producer_schedules_from_reabsorbed_transported_surface(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=[1],
            rear_node_ids=[2],
            reference_delta=0.0,
            feedback_threshold=0.0,
        )
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        state = model.get_state()
        transported_feedback_row = state.causal_pulse_substrate_surface_log[-1]
        state_record = state.topology_state_reabsorption_log[-1]
        model.set_feedback_coupled_pulse_producer(
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            expected_polarity="negative",
        )

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        self.assertTrue(result.state_mutated)
        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
            record.reason_code,
        )
        self.assertEqual(
            transported_feedback_row.surface_digest,
            record.causal_surface_digest,
        )
        self.assertEqual(
            state_record.topology_event_digest,
            record.observed_evidence["topology_event_digest"],
        )
        self.assertEqual(
            state_record.topology_state_reabsorption_digest,
            record.observed_evidence["topology_state_reabsorption_record_digest"],
        )
        self.assertTrue(
            record.observed_evidence["topology_state_reabsorption_verified"]
        )
        self.assertTrue(record.observed_evidence["producer_reads_transport_successor"])
        self.assertFalse(record.observed_evidence["native_m6"])
        self.assertFalse(record.observed_evidence["movement_claim_allowed"])
        self.assertIsNotNone(record.scheduled_event_id)

        departure = model.step()
        self.assertIn(
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            [event.kind for event in departure.events],
        )
        ledger = model.get_state().packet_ledger
        self.assertIsNotNone(ledger)
        active_after_departure = sum(
            node.coherence for node in model.get_state().base_state.nodes.values()
        )
        self.assertAlmostEqual(active_after_departure, ledger.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(6.0, ledger.conserved_budget_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(
            6.0,
            active_after_departure + ledger.in_flight_packet_total,  # type: ignore[union-attr]
        )
        self.assertGreaterEqual(
            min(node.coherence for node in model.get_state().base_state.nodes.values()),
            0.0,
        )

    def test_topology_state_reabsorption_snapshot_load_preserves_producer_gate(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        before_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        before_record_digest = before_runtime["topology_state_reabsorption_log"][0][
            "topology_state_reabsorption_digest"
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "topology-state-reabsorption.snapshot.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        loaded_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(
            before_runtime["topology_state_reabsorption_log"],
            loaded_runtime["topology_state_reabsorption_log"],
        )
        self.assertEqual(
            before_record_digest,
            loaded_runtime["topology_state_reabsorption_log"][0][
                "topology_state_reabsorption_digest"
            ],
        )
        self.assertEqual(model.compute_observables(), loaded.compute_observables())

        loaded.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        result = loaded.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        loaded.step()

        record = result.production_records[0]
        self.assertEqual(
            before_record_digest,
            record.observed_evidence["topology_state_reabsorption_record_digest"],
        )
        self.assertEqual(
            1,
            len(loaded.get_state().topology_state_reabsorption_log),
        )
        ledger = loaded.get_state().packet_ledger
        self.assertIsNotNone(ledger)
        active_total = sum(
            node.coherence for node in loaded.get_state().base_state.nodes.values()
        )
        self.assertAlmostEqual(active_total, ledger.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(6.0, active_total + ledger.in_flight_packet_total)  # type: ignore[union-attr]

    def test_topology_state_reabsorption_artifact_validator_reconstructs_chain(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        producer_result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        model.step()
        artifacts = _lineage_validation_artifacts(model)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            **artifacts,
            production_results=[producer_result.to_artifact()],
        )

        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertTrue(validation["artifact_only"])
        self.assertFalse(validation["runtime_state_used"])
        self.assertTrue(validation["topology_state_reabsorption_digest_fields_checked"])
        self.assertTrue(validation["native_topology_state_reabsorption_supported"])
        self.assertEqual(1, validation["topology_state_reabsorption_record_count"])
        self.assertEqual(1, validation["producer_record_count"])

    def test_topology_state_reabsorption_artifact_validator_rejects_missing_record(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        producer_result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        model.step()
        artifacts = _lineage_validation_artifacts(model)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],  # type: ignore[index]
            surface_rows=artifacts["surface_rows"],  # type: ignore[index]
            surface_lineage_records=artifacts["surface_lineage_records"],  # type: ignore[index]
            topology_state_reabsorption_records=(),
            production_results=[producer_result.to_artifact()],
        )

        self.assertFalse(validation["valid"])
        self.assertIn(
            "producer_missing_topology_state_reabsorption_digest:"
            f"{producer_result.production_records[0].record_id}",
            validation["failure_reasons"],
        )

    def test_topology_state_reabsorption_artifact_validator_rejects_duplicates(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        artifacts = _lineage_validation_artifacts(model)
        reabsorption_records = artifacts["topology_state_reabsorption_records"]  # type: ignore[index]

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],  # type: ignore[index]
            surface_rows=artifacts["surface_rows"],  # type: ignore[index]
            surface_lineage_records=artifacts["surface_lineage_records"],  # type: ignore[index]
            topology_state_reabsorption_records=[
                *reabsorption_records,  # type: ignore[misc]
                reabsorption_records[0],  # type: ignore[index]
            ],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("duplicate_topology_state_reabsorption_record:")
                for reason in validation["failure_reasons"]
            ),
            validation["failure_reasons"],
        )

    def test_topology_state_reabsorption_artifact_validator_rejects_budget_drift(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        artifacts = _lineage_validation_artifacts(model)
        bad_reabsorption = deepcopy(
            artifacts["topology_state_reabsorption_records"][0]  # type: ignore[index]
        )
        bad_reabsorption["packet_ledger_in_flight_packet_total_after"] = 0.1
        bad_reabsorption["packet_ledger_conserved_budget_total_after"] = 6.1
        bad_reabsorption["node_plus_packet_budget_after"] = 6.1
        bad_reabsorption["node_plus_packet_budget_error"] = 0.1
        bad_reabsorption = _refresh_topology_state_reabsorption_digest(
            bad_reabsorption
        )

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],  # type: ignore[index]
            surface_rows=artifacts["surface_rows"],  # type: ignore[index]
            surface_lineage_records=artifacts["surface_lineage_records"],  # type: ignore[index]
            topology_state_reabsorption_records=[bad_reabsorption],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith(
                    "topology_state_reabsorption_budget_discontinuity:"
                )
                for reason in validation["failure_reasons"]
            ),
            validation["failure_reasons"],
        )

    def test_topology_state_reabsorption_artifact_validator_rejects_claim_promotion(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        artifacts = _lineage_validation_artifacts(model)
        bad_reabsorption = deepcopy(
            artifacts["topology_state_reabsorption_records"][0]  # type: ignore[index]
        )
        claim_flags = dict(bad_reabsorption["claim_flags"])  # type: ignore[arg-type]
        claim_flags["topology_only_claim_promotion_attempted"] = True
        bad_reabsorption["claim_flags"] = claim_flags
        bad_reabsorption = _refresh_topology_state_reabsorption_digest(
            bad_reabsorption
        )

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],  # type: ignore[index]
            surface_rows=artifacts["surface_rows"],  # type: ignore[index]
            surface_lineage_records=artifacts["surface_lineage_records"],  # type: ignore[index]
            topology_state_reabsorption_records=[bad_reabsorption],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("topology_state_reabsorption_promoted_claim:")
                for reason in validation["failure_reasons"]
            ),
            validation["failure_reasons"],
        )

    def test_lgrc3_rebases_in_flight_packet_endpoints_after_topology(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "0"},
            source_lineage_ids={1: "source-port"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        state = model.get_state()
        ledger = state.packet_ledger
        self.assertIsNotNone(ledger)
        in_flight = [
            packet
            for packet in ledger.packet_records  # type: ignore[union-attr]
            if packet.packet_state == LGRC9V3_PACKET_STATE_IN_FLIGHT
        ]
        self.assertEqual(1, len(in_flight))
        self.assertEqual(0, in_flight[0].source_node_id)
        self.assertEqual(2, in_flight[0].target_node_id)
        self.assertNotIn(1, {in_flight[0].source_node_id, in_flight[0].target_node_id})
        self.assertAlmostEqual(5.9, ledger.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(0.1, ledger.in_flight_packet_total)  # type: ignore[union-attr]
        active_total = sum(node.coherence for node in state.base_state.nodes.values())
        self.assertAlmostEqual(5.9, active_total)
        self.assertEqual(1, len(state.topology_state_reabsorption_log))
        transport_event = state.topology_event_log[-1].payload
        self.assertEqual(
            {"1": "0"},
            dict(state.topology_state_reabsorption_log[0].lineage_transfer_map),
        )
        self.assertEqual({"1": "0"}, transport_event["lineage_transfer_map"])

    def test_topology_state_reabsorption_duplicate_attempt_is_suppressed(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        ledger = model.get_state().packet_ledger
        self.assertIsNotNone(ledger)
        topology_event = GRCEvent(
            kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            step_index=0,
            payload={
                "topology_event_id": "topology-event:duplicate",
                "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                "event_time_key": 0.0,
                "scheduler_event_index": 0,
                "checkpoint_index": 0,
            },
            source_family="test",
        )
        state = model.get_state()
        node_state_before = model._active_node_state_map()  # noqa: SLF001
        edge_state_before = model._edge_state_map_for_edges((0, 1, 2))  # noqa: SLF001
        active_state_digest = model._active_state_digest()  # noqa: SLF001
        active_total_before_duplicate = sum(
            node.coherence for node in state.base_state.nodes.values()
        )

        first = model._emit_topology_state_reabsorption_record(  # noqa: SLF001
            topology_event=topology_event,
            source_node_ids=(1,),
            target_node_ids=(0,),
            retired_node_ids=(1,),
            lineage_transfer_map={1: "0"},
            node_state_before=node_state_before,
            edge_state_before=edge_state_before,
            packet_ledger_before=ledger,
            packet_ledger_after=ledger,
            active_state_digest_before=active_state_digest,
            active_state_digest_after=active_state_digest,
            state_reabsorption_action=(
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED
            ),
        )
        duplicate = model._emit_topology_state_reabsorption_record(  # noqa: SLF001
            topology_event=topology_event,
            source_node_ids=(1,),
            target_node_ids=(0,),
            retired_node_ids=(1,),
            lineage_transfer_map={1: "0"},
            node_state_before=node_state_before,
            edge_state_before=edge_state_before,
            packet_ledger_before=ledger,
            packet_ledger_after=ledger,
            active_state_digest_before=active_state_digest,
            active_state_digest_after=active_state_digest,
            state_reabsorption_action=(
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED
            ),
        )

        self.assertIsNotNone(first)
        self.assertIsNone(duplicate)
        self.assertEqual(1, len(state.topology_state_reabsorption_log))
        active_total_after_duplicate = sum(
            node.coherence for node in state.base_state.nodes.values()
        )
        self.assertAlmostEqual(
            active_total_before_duplicate,
            active_total_after_duplicate,
        )

    def test_topology_state_reabsorption_requires_complete_lineage(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()

        with self.assertRaisesRegex(
            ValueError,
            "lineage_transfer_map must cover transferred_node_ids",
        ):
            model.process_causal_collapse_reabsorption(
                topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                competing_sink_ids=[0, 1],
                selected_sink_id=0,
                losing_sink_ids=[1],
                transferred_node_ids=[1, 2],
                lineage_transfer_map={1: "0"},
                source_lineage_ids={1: "source-port", 2: "target-port"},
                target_lineage_id="0",
                coherence_transfer_amount=0.0,
            )

    def test_topology_state_reabsorption_rejects_missing_topology_event(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        ledger = model.get_state().packet_ledger
        self.assertIsNotNone(ledger)

        with self.assertRaisesRegex(
            InvalidStateTransitionError,
            "committed topology event",
        ):
            model._emit_topology_state_reabsorption_record(  # noqa: SLF001
                topology_event=GRCEvent(
                    kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                    step_index=0,
                    payload={},
                    source_family="test",
                ),
                source_node_ids=(1,),
                target_node_ids=(0,),
                retired_node_ids=(1,),
                lineage_transfer_map={1: "0"},
                node_state_before=model._active_node_state_map(),  # noqa: SLF001
                edge_state_before=model._edge_state_map_for_edges((0, 1, 2)),  # noqa: SLF001
                packet_ledger_before=ledger,
                packet_ledger_after=ledger,
                active_state_digest_before=model._active_state_digest(),  # noqa: SLF001
                active_state_digest_after=model._active_state_digest(),  # noqa: SLF001
                state_reabsorption_action=(
                    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED
                ),
            )

    def test_topology_state_reabsorption_rejects_direct_state_rewrite(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        ledger = model.get_state().packet_ledger
        self.assertIsNotNone(ledger)
        node_state_before = model._active_node_state_map()  # noqa: SLF001
        active_state_digest_before = model._active_state_digest()  # noqa: SLF001
        model.get_state().base_state.nodes[0].coherence += 0.5

        with self.assertRaisesRegex(
            ValueError,
            "packet_ledger_node_total_after must match active state total",
        ):
            model._emit_topology_state_reabsorption_record(  # noqa: SLF001
                topology_event=GRCEvent(
                    kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                    step_index=0,
                    payload={
                        "topology_event_id": "topology-event:direct-rewrite",
                        "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                        "event_time_key": 0.0,
                        "scheduler_event_index": 0,
                        "checkpoint_index": 0,
                    },
                    source_family="test",
                ),
                source_node_ids=(1,),
                target_node_ids=(0,),
                retired_node_ids=(1,),
                lineage_transfer_map={1: "0"},
                node_state_before=node_state_before,
                edge_state_before=model._edge_state_map_for_edges((0, 1, 2)),  # noqa: SLF001
                packet_ledger_before=ledger,
                packet_ledger_after=ledger,
                active_state_digest_before=active_state_digest_before,
                active_state_digest_after=model._active_state_digest(),  # noqa: SLF001
                state_reabsorption_action=(
                    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED
                ),
            )

    def test_surface_lineage_transports_rows_with_complete_node_map(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
        source_digest_before = source_row.surface_digest

        collapse_events = model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        lineage_log = model.get_state().causal_pulse_substrate_surface_lineage_log
        self.assertEqual(1, len(lineage_log))
        record = lineage_log[0]
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
            record.lineage_action,
        )
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
            record.lineage_status,
        )
        self.assertEqual(source_row.surface_id, record.source_surface_id)
        self.assertEqual(source_digest_before, record.source_surface_digest)
        self.assertEqual((1, 2), tuple(record.source_surface_nodes))
        self.assertEqual((0,), tuple(record.target_surface_nodes))
        self.assertEqual(
            collapse_events[0].payload["topology_event_id"],
            record.topology_event_id,
        )
        self.assertIsNotNone(record.transported_surface_id)
        self.assertIsNotNone(record.transported_surface_digest)
        self.assertIsNone(record.superseded_surface_id)
        self.assertGreater(record.scheduler_event_index, source_row.scheduler_event_index)
        self.assertAlmostEqual(0.0, record.node_plus_packet_budget_error)
        self.assertAlmostEqual(0.0, record.surface_budget_error)
        self.assertEqual(2, len(model.get_state().causal_pulse_substrate_surface_log))
        transported_row = model.get_state().causal_pulse_substrate_surface_log[-1]
        self.assertNotEqual(source_row.surface_id, transported_row.surface_id)
        self.assertEqual(
            record.transported_surface_digest,
            transported_row.surface_digest,
        )
        self.assertEqual(source_digest_before, transported_row.surface_values_before["transported_from_surface_digest"])
        self.assertFalse(record.claim_flags["adaptive_topology_entry_allowed"])

        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=999.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        self.assertEqual(1, len(result.production_records))
        self.assertEqual(
            transported_row.surface_digest,
            result.production_records[0].causal_surface_digest,
        )
        self.assertEqual(
            transported_row.surface_digest,
            result.production_records[0].observed_evidence["surface_digest"],
        )

    def test_surface_lineage_transport_duplicate_is_suppressed(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        collapse_events = model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        duplicate = model._emit_surface_supersession_for_topology_event(  # noqa: SLF001
            collapse_events[0]
        )

        self.assertEqual((), duplicate)
        self.assertEqual(1, len(model.get_state().causal_pulse_substrate_surface_lineage_log))

    def test_surface_lineage_snapshot_round_trip_and_continue_after_load(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        collapse_events = model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=999.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        producer_result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        self.assertEqual(1, len(producer_result.production_records))

        before_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        before_cached = before_runtime["cached_quantities"]
        self.assertEqual(2, len(before_runtime["causal_pulse_substrate_surface_log"]))
        self.assertEqual(
            1,
            len(before_runtime["causal_pulse_substrate_surface_lineage_log"]),
        )
        self.assertGreaterEqual(len(before_runtime["topology_event_log"]), 1)
        self.assertIn(
            "lgrc9v3_causal_pulse_substrate_surface_lineage_idempotency_keys",
            before_cached,
        )
        self.assertGreater(
            len(before_cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY]),
            0,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "surface-lineage.snapshot.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        loaded_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(
            before_runtime["causal_pulse_substrate_surface_log"],
            loaded_runtime["causal_pulse_substrate_surface_log"],
        )
        self.assertEqual(
            before_runtime["causal_pulse_substrate_surface_lineage_log"],
            loaded_runtime["causal_pulse_substrate_surface_lineage_log"],
        )
        self.assertEqual(
            before_runtime["topology_event_log"],
            loaded_runtime["topology_event_log"],
        )
        self.assertEqual(
            before_cached[
                "lgrc9v3_causal_pulse_substrate_surface_lineage_idempotency_keys"
            ],
            loaded_runtime["cached_quantities"][
                "lgrc9v3_causal_pulse_substrate_surface_lineage_idempotency_keys"
            ],
        )
        self.assertEqual(
            before_cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY],
            loaded_runtime["cached_quantities"][LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY],
        )
        loaded_validation = (
            validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
                events=loaded.snapshot()["events"],
                surface_rows=loaded_runtime["causal_pulse_substrate_surface_log"],
                surface_lineage_records=loaded_runtime[
                    "causal_pulse_substrate_surface_lineage_log"
                ],
            )
        )
        self.assertTrue(loaded_validation["valid"], loaded_validation)

        duplicate = loaded._emit_surface_supersession_for_topology_event(  # noqa: SLF001
            collapse_events[0]
        )

        self.assertEqual((), duplicate)
        after_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(
            loaded_runtime["causal_pulse_substrate_surface_log"],
            after_runtime["causal_pulse_substrate_surface_log"],
        )
        self.assertEqual(
            loaded_runtime["causal_pulse_substrate_surface_lineage_log"],
            after_runtime["causal_pulse_substrate_surface_lineage_log"],
        )
        after_load_result = loaded.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        transported_digest = after_runtime["causal_pulse_substrate_surface_log"][-1][
            "surface_digest"
        ]
        self.assertEqual(
            transported_digest,
            after_load_result.production_records[0].causal_surface_digest,
        )

    def test_surface_lineage_stale_read_prevention_survives_load(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "superseded-surface.snapshot.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        loaded.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        result = loaded.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
            record.reason_code,
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
            record.observed_evidence["primary_blocker"],
        )
        self.assertIsNone(record.scheduled_event_id)

    def test_surface_lineage_transport_partial_map_fails_closed_to_supersession(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
        with self.assertRaises(InvalidStateTransitionError):
            model._build_surface_transport_record(  # noqa: SLF001
                row=source_row,
                topology_event={
                    "topology_event_id": "topology:partial-map",
                    "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                    "lineage_transfer_map": {"1": "0"},
                    "scheduler_event_index": 2,
                    "checkpoint_index": 0,
                    "event_time_key": 1.0,
                },
            )

        records = model._emit_surface_supersession_for_topology_event(  # noqa: SLF001
            {
                "topology_event_id": "topology:partial-map",
                "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                "lineage_transfer_map": {"1": "0"},
                "scheduler_event_index": 2,
                "checkpoint_index": 0,
                "event_time_key": 1.0,
            }
        )

        self.assertEqual(1, len(records))
        self.assertEqual("superseded", records[0].lineage_action)
        self.assertEqual(source_row.surface_id, records[0].superseded_surface_id)

    def test_surface_lineage_supersedes_rows_after_committed_topology_event(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_row = model.get_state().causal_pulse_substrate_surface_log[-1]

        collapse_events = model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )

        self.assertEqual(LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE, collapse_events[0].kind)
        lineage_log = model.get_state().causal_pulse_substrate_surface_lineage_log
        self.assertEqual(1, len(lineage_log))
        record = lineage_log[0]
        self.assertEqual(source_row.surface_id, record.source_surface_id)
        self.assertEqual(source_row.surface_digest, record.source_surface_digest)
        self.assertEqual(
            collapse_events[0].payload["topology_event_id"],
            record.topology_event_id,
        )
        self.assertEqual(source_row.surface_id, record.superseded_surface_id)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
            record.producer_stale_read_blocker,
        )
        self.assertFalse(record.claim_flags["movement_claim_allowed"])
        runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(1, len(runtime["causal_pulse_substrate_surface_lineage_log"]))

    def test_surface_lineage_supersession_is_idempotent(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        collapse_events = model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )

        duplicate = model._emit_surface_supersession_for_topology_event(  # noqa: SLF001
            collapse_events[0]
        )

        self.assertEqual((), duplicate)
        self.assertEqual(1, len(model.get_state().causal_pulse_substrate_surface_lineage_log))

    def test_surface_lineage_missing_topology_or_source_fails_closed(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        missing_source = model._emit_surface_supersession_for_topology_event(  # noqa: SLF001
            {
                "topology_event_id": "topology:missing-source",
                "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                "lineage_transfer_map": {"1": "sink-0"},
                "scheduler_event_index": 1,
                "checkpoint_index": 0,
                "event_time_key": 0.0,
            }
        )
        self.assertEqual((), missing_source)

        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
        with self.assertRaises(InvalidStateTransitionError):
            model._build_surface_supersession_record(  # noqa: SLF001
                row=source_row,
                topology_event={
                    "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                    "lineage_transfer_map": {"1": "sink-0"},
                },
            )

    def test_producers_block_stale_reads_against_superseded_surface_rows(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertEqual(1, len(result.production_records))
        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
            record.reason_code,
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
            record.observed_evidence["producer_stale_read_blocker"],
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
            record.observed_evidence["primary_blocker"],
        )
        self.assertIsNone(record.scheduled_event_id)
        self.assertFalse(result.state_mutated)

    def test_producers_block_source_reads_when_transported_successor_is_missing(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        removed = model.get_state().causal_pulse_substrate_surface_log.pop()
        self.assertTrue(
            removed.surface_values_after.get("transported_surface_current")
        )
        claim_flags_before = [
            dict(row.claim_flags)
            for row in model.get_state().causal_pulse_substrate_surface_log
        ]
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
            record.reason_code,
        )
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
            record.observed_evidence["primary_blocker"],
        )
        self.assertIsNone(record.scheduled_event_id)
        self.assertEqual(
            claim_flags_before,
            [
                dict(row.claim_flags)
                for row in model.get_state().causal_pulse_substrate_surface_log
            ],
        )

    def test_feedback_producer_reads_transported_successor_row(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        feedback_row = model.emit_feedback_eligibility_surface_row(
            front_node_ids=[1],
            rear_node_ids=[2],
            reference_delta=0.0,
            feedback_threshold=0.0,
        )
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        transported_feedback_row = model.get_state().causal_pulse_substrate_surface_log[-1]
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
            model.get_state().causal_pulse_substrate_surface_log[-2].surface_kind,
        )
        self.assertEqual(feedback_row.surface_kind, transported_feedback_row.surface_kind)
        self.assertNotEqual(feedback_row.surface_digest, transported_feedback_row.surface_digest)
        model.set_feedback_coupled_pulse_producer(
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            threshold=999.0,
            packet_amount=0.1,
            expected_polarity="negative",
        )

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
            record.reason_code,
        )
        self.assertEqual(transported_feedback_row.surface_digest, record.causal_surface_digest)
        self.assertTrue(record.observed_evidence["surface_lineage_current"])

    def test_feedback_producer_blocks_stale_superseded_surface_row(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        feedback_row = model.emit_feedback_eligibility_surface_row(
            front_node_ids=[1],
            rear_node_ids=[2],
            reference_delta=0.0,
            feedback_threshold=0.0,
        )
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            expected_polarity="positive",
        )

        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )

        record = result.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
            record.reason_code,
        )
        self.assertEqual(feedback_row.surface_digest, record.causal_surface_digest)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
            record.observed_evidence["primary_blocker"],
        )
        self.assertFalse(record.observed_evidence["surface_lineage_current"])
        self.assertIsNone(record.scheduled_event_id)

    def test_disabled_lineage_policy_blocks_topology_surface_construction(
        self,
    ) -> None:
        params = _active_topology_with_surface_lineage_params()
        causal_modes = dict(params["causal_modes"])  # type: ignore[index]
        causal_modes["causal_pulse_substrate_surface_lineage_transport_enabled"] = False
        causal_modes["causal_pulse_substrate_surface_lineage_transport_policy"] = (
            "disabled"
        )
        params["causal_modes"] = causal_modes
        with self.assertRaises(InvalidParamsError):
            LGRC9V3.from_state(_three_node_state(), params)

    def test_surface_lineage_artifact_validator_reconstructs_transport_chain(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            **_lineage_validation_artifacts(model),
        )

        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertTrue(
            validation[
                "native_causal_pulse_substrate_surface_lineage_transport_supported"
            ]
        )
        self.assertEqual(1, validation["transported_record_count"])
        self.assertEqual(0, validation["superseded_record_count"])
        self.assertEqual(2, validation["surface_row_count"])

    def test_surface_lineage_artifact_validator_reconstructs_supersession_chain(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        stale_blocked = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        artifacts = _lineage_validation_artifacts(model)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],
            surface_rows=artifacts["surface_rows"],
            surface_lineage_records=artifacts["surface_lineage_records"],
            production_results=[stale_blocked.to_artifact()],
        )

        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertEqual(0, validation["transported_record_count"])
        self.assertEqual(1, validation["superseded_record_count"])

    def test_surface_lineage_artifact_validator_rejects_missing_topology_event(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        artifacts = _lineage_validation_artifacts(model)
        events = [
            event
            for event in artifacts["events"]
            if not isinstance(event.get("payload"), dict)
            or "topology_event_id" not in event["payload"]
        ]

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=events,
            surface_rows=artifacts["surface_rows"],
            surface_lineage_records=artifacts["surface_lineage_records"],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("surface_lineage_unknown_topology_event:")
                for reason in validation["failure_reasons"]
            ),
            validation["failure_reasons"],
        )

    def test_surface_lineage_artifact_validator_rejects_missing_surface_digest(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        artifacts = _lineage_validation_artifacts(model)
        events_without_surface_rows = [
            event
            for event in artifacts["events"]
            if event.get("kind") != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND
        ]
        transported_only = [artifacts["surface_rows"][-1]]

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=events_without_surface_rows,
            surface_rows=transported_only,
            surface_lineage_records=artifacts["surface_lineage_records"],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("surface_lineage_unknown_source_surface:")
                for reason in validation["failure_reasons"]
            ),
            validation["failure_reasons"],
        )

    def test_surface_lineage_artifact_validator_rejects_topology_digest_mismatch(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        artifacts = _lineage_validation_artifacts(model)
        events = deepcopy(artifacts["events"])
        for event in events:
            payload = event.get("payload")
            if isinstance(payload, dict) and "topology_event_id" in payload:
                payload["selected_sink_id"] = 2
                break

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=events,
            surface_rows=artifacts["surface_rows"],
            surface_lineage_records=artifacts["surface_lineage_records"],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("surface_lineage_topology_digest_mismatch:")
                for reason in validation["failure_reasons"]
            ),
            validation["failure_reasons"],
        )

    def test_surface_lineage_artifact_validator_rejects_duplicate_and_bad_order(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        artifacts = _lineage_validation_artifacts(model)
        duplicate_validation = (
            validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
                events=artifacts["events"],
                surface_rows=artifacts["surface_rows"],
                surface_lineage_records=[
                    *artifacts["surface_lineage_records"],
                    artifacts["surface_lineage_records"][0],
                ],
            )
        )
        self.assertFalse(duplicate_validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("duplicate_surface_lineage_record:")
                for reason in duplicate_validation["failure_reasons"]
            )
        )

        inverted = deepcopy(artifacts["surface_lineage_records"][0])
        inverted["scheduler_event_index"] = 0
        inverted = _refresh_lineage_record_digest(inverted)
        order_validation = (
            validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
                events=artifacts["events"],
                surface_rows=artifacts["surface_rows"],
                surface_lineage_records=[inverted],
            )
        )
        self.assertFalse(order_validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("surface_lineage_order_inversion:")
                for reason in order_validation["failure_reasons"]
            )
        )

    def test_surface_lineage_artifact_validator_rejects_budget_discontinuity(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        artifacts = _lineage_validation_artifacts(model)
        discontinuous = deepcopy(artifacts["surface_lineage_records"][0])
        discontinuous["surface_budget_after"] = (
            float(discontinuous["surface_budget_before"]) + 0.1
        )
        discontinuous["surface_budget_error"] = 0.1
        discontinuous = _refresh_lineage_record_digest(discontinuous)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],
            surface_rows=artifacts["surface_rows"],
            surface_lineage_records=[discontinuous],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("surface_lineage_surface_budget_discontinuity:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_surface_lineage_artifact_validator_rejects_stale_scheduling(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        bad_result = deepcopy(result.to_artifact())
        bad_record = bad_result["production_records"][0]
        bad_record["reason_code"] = (
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
        )
        bad_record["scheduled_event_id"] = "packet:bad-stale-schedule"
        artifacts = _lineage_validation_artifacts(model)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],
            surface_rows=artifacts["surface_rows"],
            surface_lineage_records=artifacts["surface_lineage_records"],
            production_results=[bad_result],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("stale_producer_record_after_lineage:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_surface_lineage_artifact_validator_rejects_source_read_after_transport(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=999.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        transported_read = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        artifacts = _lineage_validation_artifacts(model)
        source_digest = artifacts["surface_lineage_records"][0]["source_surface_digest"]
        bad_result = deepcopy(transported_read.to_artifact())
        bad_result["production_records"][0]["causal_surface_digest"] = source_digest

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],
            surface_rows=artifacts["surface_rows"],
            surface_lineage_records=artifacts["surface_lineage_records"],
            production_results=[bad_result],
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("producer_used_source_surface_after_transport:")
                for reason in validation["failure_reasons"]
            ),
            validation["failure_reasons"],
        )

    def test_surface_lineage_artifact_validator_time_scopes_producer_reads(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        production_results = []
        processed_event_ids: list[str] = []

        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "first-source", 2: "first-target"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        first_result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        production_results.append(first_result)
        first_scheduled_event_id = first_result.production_records[0].scheduled_event_id
        self.assertIsNotNone(first_scheduled_event_id)
        for _ in range(2):
            step_result = model.step()
            processed_event_ids.append(str(step_result.bookkeeping["processed_event_id"]))

        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=10.0,
            scheduler_event_index=10,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 2],
            selected_sink_id=0,
            losing_sink_ids=[2],
            transferred_node_ids=[0, 1],
            lineage_transfer_map={0: "0", 1: "0"},
            source_lineage_ids={0: "second-source", 1: "second-target"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=1,
            edge_id=0,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        second_result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        production_results.append(second_result)
        second_scheduled_event_id = second_result.production_records[0].scheduled_event_id
        self.assertIsNotNone(second_scheduled_event_id)
        for _ in range(2):
            step_result = model.step()
            processed_event_ids.append(str(step_result.bookkeeping["processed_event_id"]))

        self.assertIn(first_scheduled_event_id, processed_event_ids)
        self.assertIn(second_scheduled_event_id, processed_event_ids)
        artifacts = _lineage_validation_artifacts(model)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            **artifacts,
            production_results=[result.to_artifact() for result in production_results],
        )

        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertFalse(
            any(
                reason.startswith("producer_used_source_surface_after_transport:")
                for reason in validation["failure_reasons"]
            ),
            validation["failure_reasons"],
        )

    def test_surface_lineage_artifact_validator_rejects_missing_scheduled_packet(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=999.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        transported_read = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )
        bad_result = deepcopy(transported_read.to_artifact())
        bad_result["production_records"][0]["reason_code"] = (
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
        )
        bad_result["production_records"][0]["scheduled_event_id"] = (
            "packet-event:missing"
        )
        artifacts = _lineage_validation_artifacts(model)

        validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=artifacts["events"],
            surface_rows=artifacts["surface_rows"],
            surface_lineage_records=artifacts["surface_lineage_records"],
            production_results=[bad_result],
        )

        self.assertFalse(validation["valid"])
        self.assertIn(
            "missing_scheduled_packet_event:packet-event:missing",
            validation["failure_reasons"],
        )

    def test_native_route_candidate_emission_default_off(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        topology_event_count = len(model.get_state().topology_event_log)

        result = model.emit_native_route_candidate_set(
            arbitration_window_id="window:disabled",
            source_surface_digest=str(source_surface.surface_digest),
            candidate_routes=(
                _native_route_candidate_spec(
                    candidate_route_id="candidate:a",
                    selected_sink_id=0,
                    losing_sink_ids=(2,),
                    score=1.0,
                ),
            ),
        )

        self.assertFalse(result["emitted"])
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
            result["reason_code"],
        )
        self.assertEqual([], model.get_state().native_route_candidate_log)
        self.assertEqual([], model.get_state().native_route_candidate_set_log)
        self.assertEqual(topology_event_count, len(model.get_state().topology_event_log))

    def test_native_route_candidate_old_snapshot_without_logs_still_loads(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        snapshot = model.snapshot()
        runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
        del runtime["native_route_candidate_log"]
        del runtime["native_route_candidate_set_log"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "old-lgrc9v3-route-candidates.json"
            save_snapshot(str(path), snapshot)
            loaded = LGRC9V3.load(str(path))

        self.assertEqual([], loaded.get_state().native_route_candidate_log)
        self.assertEqual([], loaded.get_state().native_route_candidate_set_log)

    def test_native_route_candidate_emission_rejects_unknown_source_surface(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )

        with self.assertRaisesRegex(
            InvalidStateTransitionError,
            "committed source surface evidence",
        ):
            model.emit_native_route_candidate_set(
                arbitration_window_id="window:unknown-source",
                source_surface_digest="surface-digest:missing",
                candidate_routes=(
                    _native_route_candidate_spec(
                        candidate_route_id="candidate:missing-source",
                        selected_sink_id=0,
                        losing_sink_ids=(2,),
                        score=1.0,
                    ),
                ),
            )
        self.assertEqual([], model.get_state().native_route_candidate_log)
        self.assertEqual([], model.get_state().native_route_candidate_set_log)

    def test_native_route_candidate_emission_records_candidate_set(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        topology_event_count = len(model.get_state().topology_event_log)
        ledger = model.get_state().packet_ledger
        assert ledger is not None
        event_queue_count = len(ledger.event_queue_records)

        result = model.emit_native_route_candidate_set(
            arbitration_window_id="window:positive",
            source_surface_digest=str(source_surface.surface_digest),
            source_producer_record_id="producer-record:runtime-visible",
            candidate_set_order_key=(
                LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
            ),
            candidate_routes=(
                _native_route_candidate_spec(
                    candidate_route_id="candidate:low",
                    selected_sink_id=2,
                    losing_sink_ids=(0,),
                    score=0.25,
                ),
                _native_route_candidate_spec(
                    candidate_route_id="candidate:high",
                    selected_sink_id=0,
                    losing_sink_ids=(2,),
                    score=0.75,
                ),
            ),
        )

        state = model.get_state()
        self.assertTrue(result["emitted"])
        self.assertEqual(2, len(state.native_route_candidate_log))
        self.assertEqual(1, len(state.native_route_candidate_set_log))
        self.assertEqual(topology_event_count, len(state.topology_event_log))
        assert state.packet_ledger is not None
        self.assertEqual(event_queue_count, len(state.packet_ledger.event_queue_records))
        candidate_set = state.native_route_candidate_set_log[0]
        self.assertEqual(
            [record.candidate_route_digest for record in state.native_route_candidate_log],
            list(candidate_set.candidate_route_digests),
        )
        self.assertEqual(
            ["candidate:high", "candidate:low"],
            [record.candidate_route_id for record in state.native_route_candidate_log],
        )
        for record in state.native_route_candidate_log:
            self.assertEqual(source_surface.surface_digest, record.candidate_source_surface_digest)
            self.assertEqual(
                "producer-record:runtime-visible",
                record.candidate_source_producer_record_id,
            )
            self.assertEqual(
                LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES,
                record.native_route_arbitration_policy_id,
            )
            self.assertEqual(
                record.candidate_route_score,
                sum(record.candidate_score_components.values()),
            )
            self.assertFalse(any(record.claim_flags.values()))
        runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(2, len(runtime["native_route_candidate_log"]))
        self.assertEqual(1, len(runtime["native_route_candidate_set_log"]))
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "lgrc9v3-route-candidates.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))
        loaded_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(
            runtime["native_route_candidate_log"],
            loaded_runtime["native_route_candidate_log"],
        )
        self.assertEqual(
            runtime["native_route_candidate_set_log"],
            loaded_runtime["native_route_candidate_set_log"],
        )

    def test_native_route_candidate_emission_cites_reabsorbed_state(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "source", 2: "target"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        reabsorption = model.get_state().topology_state_reabsorption_log[-1]
        topology_event_count = len(model.get_state().topology_event_log)

        model.emit_native_route_candidate_set(
            arbitration_window_id="window:reabsorbed-state",
            source_surface_digest=str(source_surface.surface_digest),
            source_topology_state_reabsorption_digest=str(
                reabsorption.topology_state_reabsorption_digest
            ),
            candidate_routes=(
                _native_route_candidate_spec(
                    candidate_route_id="candidate:reabsorbed",
                    selected_sink_id=0,
                    losing_sink_ids=(2,),
                    score=0.5,
                ),
            ),
        )

        candidate = model.get_state().native_route_candidate_log[0]
        self.assertEqual(
            reabsorption.topology_state_reabsorption_digest,
            candidate.candidate_source_topology_state_reabsorption_digest,
        )
        self.assertEqual(topology_event_count, len(model.get_state().topology_event_log))

    def test_native_route_candidate_emission_suppresses_duplicates(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        candidates = (
            _native_route_candidate_spec(
                candidate_route_id="candidate:a",
                selected_sink_id=0,
                losing_sink_ids=(2,),
                score=0.5,
            ),
            _native_route_candidate_spec(
                candidate_route_id="candidate:a",
                selected_sink_id=0,
                losing_sink_ids=(2,),
                score=0.5,
            ),
        )

        first = model.emit_native_route_candidate_set(
            arbitration_window_id="window:duplicate",
            source_surface_digest=str(source_surface.surface_digest),
            candidate_routes=candidates,
        )
        second = model.emit_native_route_candidate_set(
            arbitration_window_id="window:duplicate",
            source_surface_digest=str(source_surface.surface_digest),
            candidate_routes=candidates,
        )

        self.assertTrue(first["emitted"])
        self.assertFalse(second["emitted"])
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            second["reason_code"],
        )
        self.assertEqual(1, len(model.get_state().native_route_candidate_log))
        self.assertEqual(1, len(model.get_state().native_route_candidate_set_log))

    def test_native_route_candidate_emission_supports_digest_ordering(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]

        model.emit_native_route_candidate_set(
            arbitration_window_id="window:digest-order",
            source_surface_digest=str(source_surface.surface_digest),
            candidate_set_order_key=LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING,
            candidate_routes=(
                _native_route_candidate_spec(
                    candidate_route_id="candidate:b",
                    selected_sink_id=2,
                    losing_sink_ids=(0,),
                    score=0.25,
                ),
                _native_route_candidate_spec(
                    candidate_route_id="candidate:a",
                    selected_sink_id=0,
                    losing_sink_ids=(2,),
                    score=0.75,
                ),
            ),
        )

        candidate_set = model.get_state().native_route_candidate_set_log[0]
        self.assertEqual(
            sorted(candidate_set.candidate_route_digests),
            list(candidate_set.candidate_route_digests),
        )

    def test_native_route_candidate_emission_rejects_hidden_route_selection(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        candidate = _native_route_candidate_spec(
            candidate_route_id="candidate:hidden",
            selected_sink_id=0,
            losing_sink_ids=(2,),
            score=1.0,
        )
        candidate["candidate_score_components"] = {"hidden_fixture_array": 1.0}
        candidate["candidate_runtime_visible_inputs"] = (
            "candidate_source_surface_digest",
            "hidden_fixture_array",
        )

        with self.assertRaisesRegex(
            InvalidParamsError,
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        ):
            model.emit_native_route_candidate_set(
                arbitration_window_id="window:hidden",
                source_surface_digest=str(source_surface.surface_digest),
                candidate_routes=(candidate,),
            )
        self.assertEqual([], model.get_state().native_route_candidate_log)
        self.assertEqual([], model.get_state().native_route_candidate_set_log)

    def test_native_route_candidate_emission_rejects_missing_budget_prediction(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        candidate = _native_route_candidate_spec(
            candidate_route_id="candidate:missing-budget",
            selected_sink_id=0,
            losing_sink_ids=(2,),
            score=1.0,
        )
        del candidate["candidate_budget_prediction"]

        with self.assertRaisesRegex(
            InvalidParamsError,
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
        ):
            model.emit_native_route_candidate_set(
                arbitration_window_id="window:missing-budget",
                source_surface_digest=str(source_surface.surface_digest),
                candidate_routes=(candidate,),
            )
        self.assertEqual([], model.get_state().native_route_candidate_log)
        self.assertEqual([], model.get_state().native_route_candidate_set_log)

    def test_native_route_candidate_emission_rejects_partial_lineage_map(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        candidate = _native_route_candidate_spec(
            candidate_route_id="candidate:partial-lineage",
            selected_sink_id=0,
            losing_sink_ids=(2,),
            score=1.0,
        )
        candidate["candidate_lineage_transfer_map"] = {1: "0"}

        with self.assertRaisesRegex(
            InvalidParamsError,
            "lineage_transfer_map must cover transferred nodes",
        ):
            model.emit_native_route_candidate_set(
                arbitration_window_id="window:partial-lineage",
                source_surface_digest=str(source_surface.surface_digest),
                candidate_routes=(candidate,),
            )
        self.assertEqual([], model.get_state().native_route_candidate_log)
        self.assertEqual([], model.get_state().native_route_candidate_set_log)

    def test_native_route_candidate_emission_rejects_experiment_if_else_input(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        candidate = _native_route_candidate_spec(
            candidate_route_id="candidate:if-else",
            selected_sink_id=0,
            losing_sink_ids=(2,),
            score=1.0,
        )
        candidate["candidate_runtime_visible_inputs"] = (
            "candidate_source_surface_digest",
            "experiment_if_else",
        )

        with self.assertRaisesRegex(
            InvalidParamsError,
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        ):
            model.emit_native_route_candidate_set(
                arbitration_window_id="window:if-else",
                source_surface_digest=str(source_surface.surface_digest),
                candidate_routes=(candidate,),
            )
        self.assertEqual([], model.get_state().native_route_candidate_log)
        self.assertEqual([], model.get_state().native_route_candidate_set_log)

    def test_native_route_candidate_emission_rejects_preselected_sink_input(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        source_surface = model.get_state().causal_pulse_substrate_surface_log[-1]
        candidate = _native_route_candidate_spec(
            candidate_route_id="candidate:preselected",
            selected_sink_id=0,
            losing_sink_ids=(2,),
            score=1.0,
        )
        candidate["candidate_runtime_visible_inputs"] = (
            "candidate_source_surface_digest",
            "preselected_sink_id",
        )

        with self.assertRaisesRegex(
            InvalidParamsError,
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        ):
            model.emit_native_route_candidate_set(
                arbitration_window_id="window:preselected",
                source_surface_digest=str(source_surface.surface_digest),
                candidate_routes=(candidate,),
            )
        self.assertEqual([], model.get_state().native_route_candidate_log)
        self.assertEqual([], model.get_state().native_route_candidate_set_log)

    def test_native_route_arbitration_default_off(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )

        result = model.arbitrate_native_route_candidate_set(
            candidate_set_digest="candidate-set:missing",
        )

        self.assertFalse(result["emitted"])
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
            result["reason_code"],
        )
        self.assertEqual([], model.get_state().native_route_arbitration_log)

    def test_native_route_arbitration_selects_highest_score_without_commit(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        state_before = model.get_state()
        topology_event_count = len(state_before.topology_event_log)
        assert state_before.packet_ledger is not None
        event_queue_count = len(state_before.packet_ledger.event_queue_records)

        result = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )

        state = model.get_state()
        self.assertTrue(result["emitted"])
        self.assertEqual(1, len(state.native_route_arbitration_log))
        record = state.native_route_arbitration_log[0]
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
            record.arbitration_reason_code,
        )
        self.assertEqual("candidate:high", record.selected_candidate_route_id)
        self.assertIsNotNone(record.selected_candidate_route_digest)
        self.assertIsNotNone(record.selected_topology_event_id)
        self.assertIsNotNone(record.selected_topology_event_digest)
        self.assertIn(
            record.selected_candidate_route_digest,
            candidate_set.candidate_route_digests,
        )
        self.assertEqual(1, len(record.rejected_candidate_route_digests))
        self.assertEqual(
            {
                str(digest)
                for digest in candidate_set.candidate_route_digests
                if str(digest) != record.selected_candidate_route_digest
            },
            set(record.rejected_candidate_route_digests),
        )
        selected_candidate = next(
            candidate
            for candidate in state.native_route_candidate_log
            if candidate.candidate_route_digest
            == record.selected_candidate_route_digest
        )
        self.assertEqual(
            max(
                candidate.candidate_route_score
                for candidate in state.native_route_candidate_log
            ),
            selected_candidate.candidate_route_score,
        )
        self.assertEqual(
            ("candidate_route_score", "candidate_order_key", "candidate_set_order_key"),
            tuple(record.arbitration_runtime_visible_inputs),
        )
        self.assertFalse(any(record.claim_flags.values()))
        self.assertEqual(topology_event_count, len(state.topology_event_log))
        assert state.packet_ledger is not None
        self.assertEqual(event_queue_count, len(state.packet_ledger.event_queue_records))
        runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(1, len(runtime["native_route_arbitration_log"]))

    def test_native_route_arbitration_no_candidates_fails_closed(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_route_arbitration_params(),
        )
        state = model.get_state()
        candidate_set = LGRC9V3NativeRouteCandidateSetRecord(
            candidate_set_id="candidate-set:empty",
            native_route_arbitration_policy_id=(
                LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
            ),
            native_route_arbitration_enabled=True,
            arbitration_window_id="window:empty",
            event_time_key=float(state.event_time_key),
            scheduler_event_index=int(state.scheduler_event_index),
            candidate_route_digests=(),
            candidate_set_order_key=(
                LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
            ),
            unresolved_tie_policy=(
                LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED
            ),
            lgrc_runtime_level=LGRC_RUNTIME_LEVEL_LGRC3,
            causal_layer_mode=CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            claim_flags={},
        )
        state.native_route_candidate_set_log.append(candidate_set)

        result = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )

        record = result["route_arbitration_record"]
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES,
            result["reason_code"],
        )
        self.assertIsNone(record.selected_candidate_route_digest)
        self.assertEqual((), tuple(record.rejected_candidate_route_digests))
        self.assertEqual(1, len(model.get_state().native_route_arbitration_log))

    def test_native_route_arbitration_duplicate_replay_suppresses_record(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()

        first = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )
        second = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )

        first_record = first["route_arbitration_record"]
        second_record = second["route_arbitration_record"]
        self.assertEqual(1, len(model.get_state().native_route_arbitration_log))
        self.assertEqual(first_record.idempotency_key, second_record.idempotency_key)
        self.assertEqual(
            first_record.native_route_arbitration_digest,
            second_record.native_route_arbitration_digest,
        )

    def test_native_route_arbitration_commit_integrates_topology_and_producer(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]

        commit = model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )

        self.assertTrue(commit["committed"])
        self.assertEqual((), commit["post_refinement_flow_window_records"])
        self.assertEqual((), commit["child_basin_state_records"])
        topology_event = commit["topology_events"][0]
        selected_candidate = commit["selected_candidate_route_record"]
        self.assertIsNotNone(selected_candidate)
        self.assertEqual(
            arbitration.native_route_arbitration_record_id,
            topology_event.payload["native_route_arbitration_record_id"],
        )
        self.assertEqual(
            arbitration.native_route_arbitration_digest,
            topology_event.payload["native_route_arbitration_digest"],
        )
        self.assertEqual(
            arbitration.selected_candidate_route_id,
            topology_event.payload["native_route_selected_candidate_route_id"],
        )
        self.assertEqual(
            arbitration.selected_candidate_route_digest,
            topology_event.payload["native_route_selected_candidate_route_digest"],
        )
        self.assertEqual(
            arbitration.candidate_set_digest,
            topology_event.payload["native_route_candidate_set_digest"],
        )
        self.assertEqual(
            arbitration.selected_topology_event_digest,
            build_lgrc9v3_topology_event_digest(topology_event.payload),
        )
        state = model.get_state()
        selected_events = [
            event
            for event in state.topology_event_log
            if event.payload.get("native_route_arbitration_record_id")
            == arbitration.native_route_arbitration_record_id
        ]
        self.assertEqual(1, len(selected_events))
        self.assertFalse(
            set(arbitration.rejected_candidate_route_digests).intersection(
                {
                    str(event.payload.get("native_route_selected_candidate_route_digest"))
                    for event in state.topology_event_log
                }
            )
        )
        self.assertEqual(1, len(state.causal_pulse_substrate_surface_lineage_log))
        self.assertEqual(1, len(state.topology_state_reabsorption_log))
        self.assertEqual([], state.post_refinement_flow_window_log)
        self.assertEqual([], state.child_basin_state_log)
        lineage = state.causal_pulse_substrate_surface_lineage_log[-1]
        reabsorption = state.topology_state_reabsorption_log[-1]
        self.assertEqual(arbitration.selected_topology_event_id, lineage.topology_event_id)
        self.assertEqual(
            arbitration.selected_topology_event_digest,
            lineage.topology_event_digest,
        )
        self.assertEqual(
            arbitration.selected_topology_event_digest,
            reabsorption.topology_event_digest,
        )
        candidate_lineage_map = {
            str(key): str(value)
            for key, value in selected_candidate.candidate_lineage_transfer_map.items()
        }
        self.assertEqual(candidate_lineage_map, topology_event.payload["lineage_transfer_map"])
        self.assertEqual(candidate_lineage_map, dict(lineage.lineage_transfer_map))
        self.assertEqual(candidate_lineage_map, dict(reabsorption.lineage_transfer_map))
        self.assertEqual(
            tuple(selected_candidate.candidate_source_node_ids),
            tuple(reabsorption.source_node_ids),
        )
        self.assertEqual(
            tuple(selected_candidate.candidate_target_node_ids),
            tuple(reabsorption.target_node_ids),
        )
        self.assertEqual(
            tuple(selected_candidate.candidate_retired_node_ids),
            tuple(reabsorption.retired_node_ids),
        )
        self.assertAlmostEqual(0.0, topology_event.payload["budget_error"])
        self.assertAlmostEqual(0.0, lineage.node_plus_packet_budget_error)
        self.assertAlmostEqual(0.0, reabsorption.node_plus_packet_budget_error)
        transported_row = state.causal_pulse_substrate_surface_log[-1]
        self.assertEqual(lineage.transported_surface_digest, transported_row.surface_digest)
        ledger_after_commit = state.packet_ledger
        self.assertIsNotNone(ledger_after_commit)
        active_after_commit = sum(node.coherence for node in state.base_state.nodes.values())
        self.assertAlmostEqual(active_after_commit, ledger_after_commit.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(6.0, active_after_commit + ledger_after_commit.in_flight_packet_total)  # type: ignore[union-attr]

        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        produced = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        producer_record = produced.production_records[0]
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
            producer_record.reason_code,
        )
        self.assertEqual(transported_row.surface_digest, producer_record.causal_surface_digest)
        self.assertEqual(
            reabsorption.topology_state_reabsorption_digest,
            producer_record.observed_evidence[
                "topology_state_reabsorption_record_digest"
            ],
        )
        self.assertTrue(
            producer_record.observed_evidence["topology_state_reabsorption_verified"]
        )
        self.assertTrue(
            producer_record.observed_evidence["producer_reads_transport_successor"]
        )
        self.assertEqual(
            arbitration.selected_topology_event_digest,
            producer_record.observed_evidence["topology_event_digest"],
        )
        self.assertFalse(producer_record.observed_evidence["producer_mutated_coherence"])
        self.assertFalse(producer_record.observed_evidence["direct_topology_write"])
        self.assertFalse(producer_record.observed_evidence["direct_claim_write"])
        self.assertFalse(producer_record.observed_evidence["movement_claim_allowed"])
        ledger_after_producer = model.get_state().packet_ledger
        self.assertIsNotNone(ledger_after_producer)
        self.assertAlmostEqual(6.0, ledger_after_producer.conserved_budget_total)  # type: ignore[union-attr]

        step = model.step()
        self.assertIn(
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            [event.kind for event in step.events],
        )
        ledger = model.get_state().packet_ledger
        self.assertIsNotNone(ledger)
        active_total = sum(
            node.coherence for node in model.get_state().base_state.nodes.values()
        )
        self.assertAlmostEqual(active_total, ledger.node_coherence_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(6.0, active_total + ledger.in_flight_packet_total)  # type: ignore[union-attr]
        self.assertAlmostEqual(6.0, ledger.conserved_budget_total)  # type: ignore[union-attr]

    def test_native_route_commit_emits_multi_basin_candidate_records_when_enabled(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set(
            multi_basin_enabled=True,
        )
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]

        commit = model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )

        self.assertTrue(commit["committed"])
        flow_records = commit["post_refinement_flow_window_records"]
        child_records = commit["child_basin_state_records"]
        self.assertEqual(1, len(flow_records))
        self.assertEqual(1, len(child_records))
        flow = flow_records[0]
        child = child_records[0]
        state = model.get_state()
        self.assertEqual([flow], state.post_refinement_flow_window_log)
        self.assertEqual([child], state.child_basin_state_log)
        self.assertEqual(
            arbitration.selected_topology_event_digest,
            flow.source_topology_event_digest,
        )
        self.assertTrue(flow.source_expansion_id.startswith("native-route-candidate:"))
        self.assertTrue(
            any(
                value.startswith("topology_state_reabsorption_record_digest:")
                for value in flow.runtime_visible_inputs
            )
        )
        self.assertEqual(
            flow.post_refinement_flow_window_digest,
            child.source_flow_window_digest,
        )
        self.assertTrue(flow.refinement_lineage_map)
        self.assertTrue(child.child_basin_membership_by_core)
        child_artifact = child.to_artifact()
        self.assertEqual(
            child.child_basin_membership_digest,
            child_artifact["child_basin_membership_digest"],
        )
        self.assertTrue(child.child_basin_support_floor_records)
        self.assertTrue(child.child_basin_coherence_floor_records)
        self.assertTrue(child.child_basin_boundary_records)
        self.assertTrue(child.child_basin_flux_records)
        self.assertEqual(
            "MB3_candidate_emission_only",
            child.old_basin_relation_trace["candidate_ceiling"],
        )
        self.assertEqual(
            "false",
            child.old_basin_relation_trace["mb4_or_stronger_supported"],
        )
        self.assertFalse(
            state.causal_modes["native_lgrc_multi_basin_formation_validated"]
        )
        self.assertFalse(
            state.causal_modes["native_lgrc_multi_basin_formation_supported"]
        )
        self.assertFalse(any(flow.claim_flags.values()))
        self.assertFalse(any(child.claim_flags.values()))
        snapshot_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(
            flow.to_artifact(),
            snapshot_runtime["post_refinement_flow_window_log"][0],
        )
        self.assertEqual(
            child.to_artifact(),
            snapshot_runtime["child_basin_state_log"][0],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "multi-basin-candidate.snapshot.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        loaded_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual(
            snapshot_runtime["post_refinement_flow_window_log"],
            loaded_runtime["post_refinement_flow_window_log"],
        )
        self.assertEqual(
            snapshot_runtime["child_basin_state_log"],
            loaded_runtime["child_basin_state_log"],
        )

    def test_native_route_multi_basin_duplicate_commit_is_idempotent(self) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set(
            multi_basin_enabled=True,
        )
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]

        first = model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )
        flow_count = len(model.get_state().post_refinement_flow_window_log)
        child_count = len(model.get_state().child_basin_state_log)
        second = model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )

        self.assertTrue(first["committed"])
        self.assertEqual(1, flow_count)
        self.assertEqual(1, child_count)
        self.assertFalse(second["committed"])
        self.assertEqual((), second["post_refinement_flow_window_records"])
        self.assertEqual((), second["child_basin_state_records"])
        self.assertEqual(
            flow_count,
            len(model.get_state().post_refinement_flow_window_log),
        )
        self.assertEqual(child_count, len(model.get_state().child_basin_state_log))

    def test_native_route_multi_basin_wrong_policy_emits_no_records(self) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set(
            multi_basin_enabled=True,
        )
        model.get_state().causal_modes[
            "native_lgrc_multi_basin_formation_policy"
        ] = "disabled"
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]

        commit = model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )

        self.assertTrue(commit["committed"])
        self.assertEqual((), commit["post_refinement_flow_window_records"])
        self.assertEqual((), commit["child_basin_state_records"])
        self.assertEqual([], model.get_state().post_refinement_flow_window_log)
        self.assertEqual([], model.get_state().child_basin_state_log)

    def test_native_route_multi_basin_emitter_fails_closed_on_malformed_event(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set(
            multi_basin_enabled=True,
        )
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]
        candidate = next(
            record
            for record in model.get_state().native_route_candidate_log
            if record.candidate_route_digest
            == arbitration.selected_candidate_route_digest
        )

        with self.assertRaisesRegex(
            InvalidStateTransitionError,
            "requires committed topology event",
        ):
            model._emit_multi_basin_records_for_committed_topology(  # noqa: SLF001
                topology_event=GRCEvent(
                    kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                    step_index=0,
                    payload={"lineage_transfer_map": {"1": "0"}},
                    source_family=None,
                ),
                topology_event_digest="malformed-topology-event",
                candidate=candidate,
            )
        self.assertEqual([], model.get_state().post_refinement_flow_window_log)
        self.assertEqual([], model.get_state().child_basin_state_log)

    def test_runtime_loads_snapshot_without_multi_basin_logs(self) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set(
            multi_basin_enabled=True,
        )
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]
        model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )
        snapshot = deepcopy(model.snapshot())
        runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
        runtime.pop("post_refinement_flow_window_log")
        runtime.pop("child_basin_state_log")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy-without-multi-basin-logs.snapshot.json"
            save_snapshot(str(path), snapshot)
            loaded = LGRC9V3.load(str(path))

        loaded_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        self.assertEqual([], loaded_runtime["post_refinement_flow_window_log"])
        self.assertEqual([], loaded_runtime["child_basin_state_log"])

    def test_native_route_arbitration_commit_duplicate_is_idempotent(self) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]

        first = model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )
        topology_count = len(model.get_state().topology_event_log)
        lineage_count = len(model.get_state().causal_pulse_substrate_surface_lineage_log)
        reabsorption_count = len(model.get_state().topology_state_reabsorption_log)
        second = model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )

        self.assertTrue(first["committed"])
        self.assertFalse(second["committed"])
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            second["reason_code"],
        )
        self.assertEqual(topology_count, len(model.get_state().topology_event_log))
        self.assertEqual(
            lineage_count,
            len(model.get_state().causal_pulse_substrate_surface_lineage_log),
        )
        self.assertEqual(
            reabsorption_count,
            len(model.get_state().topology_state_reabsorption_log),
        )

    def test_native_route_arbitration_commit_rejects_stale_candidate_set(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]
        object.__setattr__(candidate_set, "candidate_route_digests", ())

        with self.assertRaisesRegex(
            InvalidStateTransitionError,
            "selected candidate is outside candidate set",
        ):
            model.commit_native_route_arbitration_selection(
                native_route_arbitration_reference=str(
                    arbitration.native_route_arbitration_digest
                ),
            )
        self.assertEqual([], model.get_state().topology_event_log)

    def test_native_route_arbitration_commit_rejects_missing_candidate_record(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]
        model.get_state().native_route_candidate_log.clear()

        with self.assertRaisesRegex(
            InvalidStateTransitionError,
            "selected candidate is missing",
        ):
            model.commit_native_route_arbitration_selection(
                native_route_arbitration_reference=str(
                    arbitration.native_route_arbitration_digest
                ),
            )
        self.assertEqual([], model.get_state().topology_event_log)

    def test_native_route_arbitration_commit_rejects_candidate_digest_drift(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]
        selected_candidate = next(
            candidate
            for candidate in model.get_state().native_route_candidate_log
            if candidate.candidate_route_digest
            == arbitration.selected_candidate_route_digest
        )
        object.__setattr__(
            selected_candidate,
            "scheduler_event_index",
            int(selected_candidate.scheduler_event_index) + 1,
        )

        with self.assertRaisesRegex(
            InvalidStateTransitionError,
            "native_route_arbitration_stale_candidate",
        ):
            model.commit_native_route_arbitration_selection(
                native_route_arbitration_reference=str(
                    arbitration.native_route_arbitration_digest
                ),
            )
        self.assertEqual([], model.get_state().topology_event_log)

    def test_native_route_topology_event_rejects_wrong_arbitration_record(
        self,
    ) -> None:
        model, _candidate_set = _route_arbitration_model_with_candidate_set()

        with self.assertRaisesRegex(
            InvalidStateTransitionError,
            "arbitration record mismatch",
        ):
            model.process_causal_collapse_reabsorption(
                topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                competing_sink_ids=[0, 2],
                selected_sink_id=0,
                losing_sink_ids=[2],
                transferred_node_ids=[1, 2],
                lineage_transfer_map={1: "0", 2: "0"},
                source_lineage_ids={1: "source-1", 2: "source-2"},
                target_lineage_id="0",
                coherence_transfer_amount=0.0,
                native_route_arbitration_record_id="native-route-arbitration:missing",
                native_route_arbitration_digest="digest:missing",
                native_route_selected_candidate_route_id="candidate:missing",
                native_route_selected_candidate_route_digest="candidate-digest:missing",
                native_route_candidate_set_digest="candidate-set-digest:missing",
            )
        self.assertEqual([], model.get_state().topology_event_log)

    def test_native_route_arbitration_old_snapshot_without_log_still_loads(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )
        snapshot = model.snapshot()
        runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
        del runtime["native_route_arbitration_log"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "old-lgrc9v3-route-arbitration.json"
            save_snapshot(str(path), snapshot)
            loaded = LGRC9V3.load(str(path))

        self.assertEqual([], loaded.get_state().native_route_arbitration_log)

    def test_native_route_arbitration_rejects_experiment_if_else_selection(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()

        result = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
            arbitration_runtime_visible_inputs=("experiment_if_else",),
        )

        record = result["route_arbitration_record"]
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
            result["reason_code"],
        )
        self.assertIsNone(record.selected_candidate_route_digest)
        self.assertEqual(1, len(model.get_state().native_route_arbitration_log))

    def test_native_route_arbitration_unresolved_tie_fails_closed(self) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set(
            scores=(0.5, 0.5),
        )

        result = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )

        record = result["route_arbitration_record"]
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
            result["reason_code"],
        )
        self.assertIsNone(record.selected_candidate_route_digest)
        self.assertEqual(2, len(record.rejected_candidate_route_digests))

    def test_native_route_arbitration_declared_tiebreaker_selects_first_ordered(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set(
            scores=(0.5, 0.5),
            unresolved_tie_policy=(
                LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_DECLARED_TIEBREAKER
            ),
        )

        result = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )

        record = result["route_arbitration_record"]
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_DECLARED_LOCAL_PREFERENCE,
            result["reason_code"],
        )
        self.assertEqual("candidate:high", record.selected_candidate_route_id)

    def test_native_route_arbitration_budget_invalid_fails_closed(self) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        candidate = model.get_state().native_route_candidate_log[0]
        object.__setattr__(
            candidate,
            "candidate_budget_prediction",
            {
                "node_plus_packet_budget_before": 6.0,
                "node_plus_packet_budget_after": 5.9,
                "node_plus_packet_budget_error": 0.1,
            },
        )

        result = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )

        record = result["route_arbitration_record"]
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
            result["reason_code"],
        )
        self.assertIsNone(record.selected_candidate_route_digest)

    def test_native_route_arbitration_order_invalid_fails_closed(self) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        object.__setattr__(
            candidate_set,
            "candidate_route_digests",
            tuple(reversed(tuple(candidate_set.candidate_route_digests))),
        )

        result = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )

        record = result["route_arbitration_record"]
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID,
            result["reason_code"],
        )
        self.assertIsNone(record.selected_candidate_route_digest)

    def test_native_route_arbitration_snapshot_roundtrip_preserves_full_chain(
        self,
    ) -> None:
        model, candidate_set, arbitration = _route_arbitration_model_with_full_chain()
        before_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "lgrc9v3-route-arbitration-full-chain.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        loaded_runtime = loaded.snapshot()["dynamics"]["lgrc9v3_runtime"]
        for key in (
            "native_route_candidate_log",
            "native_route_candidate_set_log",
            "native_route_arbitration_log",
            "topology_event_log",
            "causal_pulse_substrate_surface_lineage_log",
            "topology_state_reabsorption_log",
        ):
            self.assertEqual(before_runtime[key], loaded_runtime[key])
        before_counts = {
            "arbitration": len(loaded.get_state().native_route_arbitration_log),
            "topology": len(loaded.get_state().topology_event_log),
            "lineage": len(
                loaded.get_state().causal_pulse_substrate_surface_lineage_log
            ),
            "reabsorption": len(loaded.get_state().topology_state_reabsorption_log),
        }

        loaded.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )
        loaded.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )

        self.assertEqual(
            before_counts["arbitration"],
            len(loaded.get_state().native_route_arbitration_log),
        )
        self.assertEqual(before_counts["topology"], len(loaded.get_state().topology_event_log))
        self.assertEqual(
            before_counts["lineage"],
            len(loaded.get_state().causal_pulse_substrate_surface_lineage_log),
        )
        self.assertEqual(
            before_counts["reabsorption"],
            len(loaded.get_state().topology_state_reabsorption_log),
        )

    def test_native_route_arbitration_snapshot_reload_suppresses_duplicate_producer(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set()
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]
        model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )
        model.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "lgrc9v3-route-arbitration-producer.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        ledger = loaded.get_state().packet_ledger
        self.assertIsNotNone(ledger)
        queue_length = len(ledger.event_queue_records)  # type: ignore[union-attr]
        loaded.set_pulse_substrate_coupling_producer(
            target_node_id=2,
            edge_id=2,
            threshold=0.0,
            packet_amount=0.1,
            source_node_selector="surface_source",
        )
        produced = loaded.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
            )
        )

        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            produced.production_records[0].reason_code,
        )
        after_ledger = loaded.get_state().packet_ledger
        self.assertIsNotNone(after_ledger)
        self.assertEqual(queue_length, len(after_ledger.event_queue_records))  # type: ignore[union-attr]

    def test_native_route_arbitration_telemetry_is_policy_gated(self) -> None:
        default_model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        default_extension = classify_lgrc9v3_step_extension(default_model)
        self.assertNotIn("native_route_arbitration", default_extension)

        model, _candidate_set, _arbitration = _route_arbitration_model_with_full_chain()
        extension = classify_lgrc9v3_step_extension(model)
        route_surface = extension["native_route_arbitration"]
        self.assertEqual(2, route_surface["candidate_route_record_count"])
        self.assertEqual(1, route_surface["candidate_set_record_count"])
        self.assertEqual(1, route_surface["route_arbitration_record_count"])
        self.assertEqual(1, route_surface["committed_selected_topology_event_count"])
        self.assertFalse(route_surface["semantic_choice_claim_allowed"])
        summary = lgrc9v3_run_summary_family_extensions(model)[
            LGRC9V3_TELEMETRY_FAMILY
        ]
        self.assertIn("final_native_route_arbitration", summary)

        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=RunTelemetryIdentity(
                run_id="run:native-route-arbitration",
                model_family="LGRC9V3",
                params_identity=None,
            ),
            checkpoint_id="checkpoint:native-route-arbitration",
            checkpoint_label="native_route_arbitration",
        )
        checkpoint_extension = checkpoint.family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        self.assertIn("native_route_candidate_log", checkpoint_extension)
        self.assertIn("native_route_candidate_set_log", checkpoint_extension)
        self.assertIn("native_route_arbitration_log", checkpoint_extension)

    def test_native_route_arbitration_artifact_validator_reconstructs_chain(
        self,
    ) -> None:
        model, _candidate_set, _arbitration = _route_arbitration_model_with_full_chain()
        validation = validate_lgrc9v3_native_route_arbitration_artifacts(
            **_route_arbitration_validation_artifacts(model),
        )

        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertTrue(validation["artifact_only"])
        self.assertFalse(validation["runtime_state_used"])
        self.assertTrue(validation["native_lgrc_route_arbitration_supported"])
        self.assertEqual(2, validation["candidate_route_count"])
        self.assertEqual(1, validation["candidate_set_count"])
        self.assertEqual(1, validation["route_arbitration_record_count"])
        self.assertEqual(1, validation["selected_topology_event_count"])
        self.assertEqual(1, validation["post_arbitration_linked_producer_count"])
        self.assertFalse(validation["semantic_choice_claim_allowed"])
        self.assertFalse(validation["agency_claim_allowed"])

    def test_native_route_arbitration_artifact_validator_rejects_duplicate_record(
        self,
    ) -> None:
        model, _candidate_set, _arbitration = _route_arbitration_model_with_full_chain()
        artifacts = _route_arbitration_validation_artifacts(model)
        arbitration_records = list(artifacts["route_arbitration_records"])
        artifacts["route_arbitration_records"] = [
            *arbitration_records,
            arbitration_records[0],
        ]

        validation = validate_lgrc9v3_native_route_arbitration_artifacts(**artifacts)

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("duplicate_native_route_arbitration:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_native_route_arbitration_artifact_validator_rejects_topology_drift(
        self,
    ) -> None:
        model, _candidate_set, _arbitration = _route_arbitration_model_with_full_chain()
        artifacts = _route_arbitration_validation_artifacts(model)
        arbitration_record = artifacts["route_arbitration_records"][0]
        topology_event = dict(artifacts["topology_events"][0])
        topology_event["native_route_selected_candidate_route_digest"] = (
            arbitration_record["rejected_candidate_route_digests"][0]
        )
        artifacts["topology_events"] = [topology_event]

        validation = validate_lgrc9v3_native_route_arbitration_artifacts(**artifacts)

        self.assertFalse(validation["valid"])
        self.assertIn(
            "selected_topology_event_candidate_mismatch:"
            f"{arbitration_record['native_route_arbitration_record_id']}",
            validation["failure_reasons"],
        )

    def test_native_route_arbitration_artifact_validator_rejects_hidden_input(
        self,
    ) -> None:
        model, _candidate_set, _arbitration = _route_arbitration_model_with_full_chain()
        artifacts = _route_arbitration_validation_artifacts(model)
        candidate = dict(deepcopy(artifacts["candidate_route_records"][0]))
        candidate["candidate_runtime_visible_inputs"] = [
            *candidate["candidate_runtime_visible_inputs"],
            "hidden_fixture_array",
        ]
        artifacts["candidate_route_records"] = [
            _recanonicalized_native_route_candidate_artifact(candidate),
            *artifacts["candidate_route_records"][1:],
        ]

        validation = validate_lgrc9v3_native_route_arbitration_artifacts(**artifacts)

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith(
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED
                )
                for reason in validation["failure_reasons"]
            )
        )

    def test_native_route_arbitration_artifact_validator_rejects_budget_mismatch(
        self,
    ) -> None:
        model, _candidate_set, _arbitration = _route_arbitration_model_with_full_chain()
        artifacts = _route_arbitration_validation_artifacts(model)
        candidate = dict(deepcopy(artifacts["candidate_route_records"][0]))
        candidate["candidate_budget_prediction"] = {
            "node_plus_packet_budget_before": 6.0,
            "node_plus_packet_budget_after": 6.25,
            "node_plus_packet_budget_error": 0.25,
        }
        artifacts["candidate_route_records"] = [
            _recanonicalized_native_route_candidate_artifact(candidate),
            *artifacts["candidate_route_records"][1:],
        ]

        validation = validate_lgrc9v3_native_route_arbitration_artifacts(**artifacts)

        self.assertFalse(validation["valid"])
        self.assertIn(
            f"native_route_candidate_budget_mismatch:{candidate['candidate_route_id']}",
            validation["failure_reasons"],
        )

    def test_native_route_arbitration_artifact_validator_rejects_order_inversion(
        self,
    ) -> None:
        model, _candidate_set, _arbitration = _route_arbitration_model_with_full_chain()
        artifacts = _route_arbitration_validation_artifacts(model)
        arbitration = dict(deepcopy(artifacts["route_arbitration_records"][0]))
        arbitration["scheduler_event_index"] = 0
        artifacts["route_arbitration_records"] = [
            _recanonicalized_native_route_arbitration_artifact(arbitration),
        ]

        validation = validate_lgrc9v3_native_route_arbitration_artifacts(**artifacts)

        self.assertFalse(validation["valid"])
        self.assertIn(
            f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID}:"
            f"{arbitration['native_route_arbitration_record_id']}:"
            "arbitration_before_candidate_set",
            validation["failure_reasons"],
        )

    def test_native_route_arbitration_artifact_validator_rejects_claim_promotion(
        self,
    ) -> None:
        model, _candidate_set, _arbitration = _route_arbitration_model_with_full_chain()
        artifacts = _route_arbitration_validation_artifacts(model)
        arbitration = dict(deepcopy(artifacts["route_arbitration_records"][0]))
        claim_flags = dict(arbitration["claim_flags"])
        claim_flags["semantic_choice_claim_allowed"] = True
        arbitration["claim_flags"] = claim_flags
        artifacts["route_arbitration_records"] = [
            _recanonicalized_native_route_arbitration_artifact(arbitration),
        ]

        validation = validate_lgrc9v3_native_route_arbitration_artifacts(**artifacts)

        self.assertFalse(validation["valid"])
        self.assertIn(
            "native_route_arbitration_claim_promotion_blocked:"
            f"{arbitration['native_route_arbitration_record_id']}",
            validation["failure_reasons"],
        )

    def test_native_route_arbitration_artifact_validator_records_fail_closed_controls(
        self,
    ) -> None:
        model, _candidate_set = _route_arbitration_model_with_candidate_set(
            scores=(0.5, 0.5),
        )
        model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(
                model.get_state().native_route_candidate_set_log[0].candidate_set_digest
            ),
        )

        validation = validate_lgrc9v3_native_route_arbitration_artifacts(
            **_route_arbitration_validation_artifacts(model),
        )

        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertFalse(validation["native_lgrc_route_arbitration_supported"])
        self.assertIn(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
            validation["control_blockers"],
        )

    def test_local_update_rejects_overdrawn_route_set(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.set_causal_flux_routes({1: [{"target_node_id": 2, "edge_id": 1, "amount": 3.0}]})
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()

        with self.assertRaises(InvalidStateTransitionError):
            model.step()

    def test_snapshot_serializes_runtime_queue_and_events(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()

        snapshot = model.snapshot()
        restored = json.loads(json.dumps(snapshot, sort_keys=True))
        runtime = restored["dynamics"]["lgrc9v3_runtime"]

        self.assertEqual("LGRC9V3", restored["metadata"]["model_family"])
        self.assertEqual(LGRC9V3_RUNTIME_STATE_KIND, runtime["artifact_kind"])
        self.assertEqual(1, runtime["scheduler_event_index"])
        self.assertEqual(1, runtime["checkpoint_index"])
        self.assertEqual(1.0, runtime["event_time_key"])
        self.assertEqual(1, len(runtime["event_queue_records"]))
        self.assertEqual(1, len(restored["events"]))
        self.assertEqual(
            LGRC9V3_RUNTIME_EVENT_SCHEMA_VERSION,
            restored["events"][0]["payload"]["event_schema_version"],
        )

    def test_native_runtime_snapshot_load_preserves_queue_and_continuation(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )
        model.set_causal_flux_routes(
            {1: [{"target_node_id": 2, "edge_id": 1, "amount_fraction": 0.5}]}
        )
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.2,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.schedule_causal_boundary_birth_trial(
            parent_node_id=0,
            parent_port_id=3,
            outward_flux_pressure=2.0,
            rng_sample=0.1,
            event_time_key=3.0,
            scheduler_event_index=3,
            edge_delay=2.5,
        )
        model.step()
        before_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "lgrc9v3-runtime.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        self.assertEqual(model.MODEL_FAMILY, loaded.MODEL_FAMILY)
        self.assertEqual(
            model.get_state().scheduler_event_index,
            loaded.get_state().scheduler_event_index,
        )
        self.assertEqual(
            model.get_state().checkpoint_index,
            loaded.get_state().checkpoint_index,
        )
        self.assertEqual(model.get_state().event_time_key, loaded.get_state().event_time_key)
        self.assertEqual(_queue_signature(model), _queue_signature(loaded))
        self.assertEqual(
            model.get_state().boundary_birth_trial_queue,
            loaded.get_state().boundary_birth_trial_queue,
        )
        self.assertEqual(
            model.get_state().causal_flux_routes,
            loaded.get_state().causal_flux_routes,
        )
        self.assertEqual(
            before_runtime,
            loaded.snapshot()["dynamics"]["lgrc9v3_runtime"],
        )
        self.assertEqual(
            model.compute_observables(),
            loaded.compute_observables(),
        )

        expected_next = model.step()
        loaded_next = loaded.step()

        self.assertEqual(
            [event.kind for event in expected_next.events],
            [event.kind for event in loaded_next.events],
        )
        self.assertEqual(expected_next.bookkeeping, loaded_next.bookkeeping)
        self.assertEqual(_queue_signature(model), _queue_signature(loaded))
        self.assertAlmostEqual(_runtime_budget_surface(model), _runtime_budget_surface(loaded))

    def test_lgrc9v3_load_rejects_plain_grc9v3_snapshot(self) -> None:
        grc9v3 = GRC9V3.from_state(_three_node_state(), _PARAMS)

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "grc9v3.json"
            grc9v3.save(str(path))
            with self.assertRaises(SnapshotCompatibilityError):
                LGRC9V3.load(str(path))

    def test_lgrc9v3_load_rejects_partial_runtime_snapshot(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        snapshot = model.snapshot()
        del snapshot["dynamics"]["lgrc9v3_runtime"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "partial-lgrc9v3.json"
            save_snapshot(str(path), snapshot)
            with self.assertRaisesRegex(
                SnapshotCompatibilityError,
                "lgrc9v3_runtime",
            ):
                LGRC9V3.load(str(path))

    def test_comparison_synchronous_limit_fixture_matches_timing_baseline(self) -> None:
        grc9v3 = GRC9V3.from_state(_three_node_state(), _PARAMS)
        grc_result = grc9v3.step()

        lgrc9v3 = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        lgrc9v3.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=0.0,
            scheduler_event_index=0,
        )
        lgrc_results = lgrc9v3.run_event_queue(max_events=4)

        report = _comparison_report(
            fixture_name="synchronous_limit_unit_lapse_constant_delay",
            grc9v3_events=list(grc_result.events),
            lgrc9v3_results=lgrc_results,
            grc9v3_node_count=len(tuple(grc9v3.get_state().topology.iter_live_node_ids())),
            lgrc9v3_node_count=len(
                tuple(lgrc9v3.get_state().base_state.topology.iter_live_node_ids())
            ),
            lgrc9v3_model=lgrc9v3,
            supported_claims=[
                "unit_lapse_constant_delay_matches_grc9v3_time_surface",
                "node_and_edge_counts_remain_aligned_without_topology_events",
            ],
            open_claims=[
                "full_grc9v3_step_equivalence_not_claimed",
                "packetized_flux_is_extra_lgrc9v3_event_evidence",
            ],
        )

        self.assertEqual(1, grc9v3.get_state().step_index)
        self.assertEqual(1.0, grc9v3.get_state().time)
        self.assertEqual(1.0, lgrc9v3.get_state().event_time_key)
        self.assertEqual(1.0, lgrc9v3.get_state().node_proper_time[1])
        self.assertEqual(report["grc9v3_final_node_count"], report["lgrc9v3_final_node_count"])
        self.assertEqual("proper_time_surfaces_and_event_classes", report["alignment_policy"])
        self.assertFalse(report["raw_step_count_alignment_used"])
        self.assertIn(
            "unit_lapse_constant_delay_matches_grc9v3_time_surface",
            report["supported_claims"],
        )
        restored = json.loads(json.dumps(report, sort_keys=True))
        self.assertEqual(report["fixture_name"], restored["fixture_name"])

    def test_comparison_delay_sensitive_fixture_reports_causal_history_delta(self) -> None:
        grc9v3 = GRC9V3.from_state(_three_node_state(), _PARAMS)
        grc_result = grc9v3.step()

        constant_delay = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        constant_delay.set_causal_flux_routes(
            {1: [{"target_node_id": 2, "edge_id": 1, "amount_fraction": 1.0}]}
        )
        constant_delay.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        constant_results = constant_delay.run_event_queue(max_events=10)

        large_delay = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        large_delay.get_state().edge_causal_delay[1] = 10.0
        large_delay.set_causal_flux_routes(
            {1: [{"target_node_id": 2, "edge_id": 1, "amount_fraction": 1.0}]}
        )
        large_delay.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        large_results = large_delay.run_event_queue(max_events=3)

        report = _comparison_report(
            fixture_name="delay_sensitive_packet_route",
            grc9v3_events=list(grc_result.events),
            lgrc9v3_results=large_results,
            grc9v3_node_count=len(tuple(grc9v3.get_state().topology.iter_live_node_ids())),
            lgrc9v3_node_count=len(
                tuple(large_delay.get_state().base_state.topology.iter_live_node_ids())
            ),
            lgrc9v3_model=large_delay,
            supported_claims=[
                "larger_edge_delay_defers_downstream_packet_arrival",
                "causal_delta_is_visible_on_event_time_surface",
            ],
            open_claims=[
                "delay_sensitive_delta_is_fixture_local_not_landscape_general",
            ],
        )

        self.assertAlmostEqual(
            3.25,
            constant_delay.get_state().base_state.nodes[2].coherence,
        )
        self.assertAlmostEqual(3.0, large_delay.get_state().base_state.nodes[2].coherence)
        self.assertEqual(1, len(large_delay.get_state().packet_ledger.event_queue_records))
        self.assertEqual(
            12.0,
            large_delay.get_state().packet_ledger.event_queue_records[0].event_time_key,
        )
        self.assertIn(
            "larger_edge_delay_defers_downstream_packet_arrival",
            report["supported_claims"],
        )
        self.assertIn(
            "delay_sensitive_delta_is_fixture_local_not_landscape_general",
            report["open_claims"],
        )
        self.assertGreater(len(constant_results), len(large_results))

    def test_comparison_refinement_fixture_matches_topology_delta_with_causal_evidence(
        self,
    ) -> None:
        grc9v3 = GRC9V3.from_state(
            _saturated_sink_state(),
            _spark_params(spark_lane="grc9v3_column_h_assisted"),
        )
        grc_events = grc9v3.apply_hybrid_sparks()

        lgrc9v3 = LGRC9V3.from_state(_saturated_sink_state(), _active_topology_params())
        lgrc9v3.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        lgrc_results = lgrc9v3.run_event_queue(max_events=4)

        report = _comparison_report(
            fixture_name="lane_b_refinement_transport",
            grc9v3_events=list(grc_events),
            lgrc9v3_results=lgrc_results,
            grc9v3_node_count=len(tuple(grc9v3.get_state().topology.iter_live_node_ids())),
            lgrc9v3_node_count=len(
                tuple(lgrc9v3.get_state().base_state.topology.iter_live_node_ids())
            ),
            lgrc9v3_model=lgrc9v3,
            supported_claims=[
                "grc9v3_and_lgrc9v3_reach_same_refined_node_count",
                "lgrc9v3_adds_event_time_packet_transport_and_inheritance_evidence",
            ],
            open_claims=[
                "mechanical_expansion_is_not_identity_acceptance",
                "full_equivalence_of_all_grc9v3_step_stages_not_claimed",
            ],
        )

        self.assertEqual(14, report["grc9v3_final_node_count"])
        self.assertEqual(14, report["lgrc9v3_final_node_count"])
        self.assertEqual(1, report["grc9v3_event_counts"]["hybrid_mechanical_expansion"])
        self.assertEqual(
            1,
            report["lgrc9v3_event_counts"][LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND],
        )
        self.assertEqual(
            1,
            report["lgrc9v3_event_counts"][LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT],
        )
        self.assertEqual(
            1,
            report["lgrc9v3_event_counts"][LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE],
        )
        self.assertIn(
            "lgrc9v3_adds_event_time_packet_transport_and_inheritance_evidence",
            report["supported_claims"],
        )
        self.assertIn(
            "mechanical_expansion_is_not_identity_acceptance",
            report["open_claims"],
        )

    def test_comparison_identity_fixture_reports_lgrc_only_identity_surface(self) -> None:
        grc9v3 = GRC9V3.from_state(
            _saturated_sink_state(),
            _spark_params(spark_lane="grc9v3_column_h_assisted"),
        )
        grc_events = grc9v3.apply_hybrid_sparks()

        lgrc9v3 = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_params(collapse_allowed=True, identity_allowed=True),
        )
        lgrc9v3.get_state().node_proper_time[0] = 5.0
        collapse_events = lgrc9v3.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1],
            lineage_transfer_map={1: "sink-0"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-0",
            coherence_transfer_amount=0.0,
        )
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=[collapse_events[0].payload["topology_event_id"]],
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            sink_node_id=0,
            lineage_id="sink-0",
            basin_node_ids=[0],
            node_proper_time=lgrc9v3.get_state().node_proper_time,
            window_start_sink_proper_time=0.0,
            window_start_event_time_key=0.0,
            window_end_event_time_key=5.0,
            scheduler_event_index=0,
            checkpoint_index=0,
            event_time_key=5.0,
            local_median_edge_delay=1.0,
            threshold_multiplier=1.0,
        )
        identity_event = lgrc9v3.emit_causal_identity_acceptance(evaluation)

        class _Result:
            events = collapse_events + [identity_event]

        report = _comparison_report(
            fixture_name="proper_time_identity_persistence",
            grc9v3_events=list(grc_events),
            lgrc9v3_results=[_Result()],
            grc9v3_node_count=len(tuple(grc9v3.get_state().topology.iter_live_node_ids())),
            lgrc9v3_node_count=len(
                tuple(lgrc9v3.get_state().base_state.topology.iter_live_node_ids())
            ),
            lgrc9v3_model=lgrc9v3,
            supported_claims=[
                "proper_time_identity_acceptance_is_lgrc9v3_explicit_event",
            ],
            open_claims=[
                "identity_acceptance_has_no_synchronous_grc9v3_step_counterpart",
                "identity_surface_is_policy_gated_not_default_behavior",
            ],
        )

        self.assertFalse(any(event.kind == LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE for event in grc_events))
        self.assertEqual(
            1,
            report["lgrc9v3_event_counts"][LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE],
        )
        self.assertIn(
            "proper_time_identity_acceptance_is_lgrc9v3_explicit_event",
            report["supported_claims"],
        )
        self.assertIn(
            "identity_acceptance_has_no_synchronous_grc9v3_step_counterpart",
            report["open_claims"],
        )

    def test_stress_packet_queue_ties_are_deterministic_and_budget_safe(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        initial_budget = _runtime_budget_surface(model)
        for packet_index in range(40):
            edge_id = 0 if packet_index % 2 == 0 else 2
            target_node_id = 1 if edge_id == 0 else 2
            departure_key = float((packet_index % 5) * 0.1)
            model.schedule_packet_departure(
                source_node_id=0,
                target_node_id=target_node_id,
                edge_id=edge_id,
                amount=0.005,
                departure_event_time_key=departure_key,
                scheduler_event_index=100 - packet_index,
                packet_index=packet_index,
            )

        queued = model.get_state().packet_ledger.event_queue_records
        self.assertEqual(
            sorted(
                (event.event_time_key, event.scheduler_event_index, event.event_id)
                for event in queued
            ),
            [
                (event.event_time_key, event.scheduler_event_index, event.event_id)
                for event in queued
            ],
        )
        initial_departure_ids = {event.event_id for event in queued}
        results = model.run_event_queue(max_events=100)
        processed_ids = [
            str(result.bookkeeping["processed_event_id"]) for result in results
        ]
        processed_times = [
            float(result.bookkeeping["event_time_key"]) for result in results
        ]
        processed_kinds = [
            str(result.bookkeeping["processed_event_kind"]) for result in results
        ]

        self.assertEqual(80, len(results))
        self.assertEqual(80, len(set(processed_ids)))
        self.assertTrue(initial_departure_ids.issubset(set(processed_ids)))
        self.assertEqual(sorted(processed_times), processed_times)
        self.assertEqual(40, processed_kinds.count(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE))
        self.assertEqual(40, processed_kinds.count(LGRC9V3_PACKET_EVENT_KIND_ARRIVAL))
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertAlmostEqual(0.0, model.get_state().packet_ledger.in_flight_packet_total)
        self.assertAlmostEqual(initial_budget, _runtime_budget_surface(model))
        self.assertAlmostEqual(
            initial_budget,
            model.get_state().packet_ledger.conserved_budget_total,
        )
        self.assertTrue(
            all(packet.packet_state == "arrived" for packet in model.get_state().packet_ledger.packet_records)
        )

    def test_stress_mixed_packet_birth_and_lane_b_expansion_preserves_runtime_refs(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(),
            _active_topology_with_boundary_birth_params(),
        )
        initial_budget = _runtime_budget_surface(model)
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.schedule_causal_boundary_birth_trial(
            parent_node_id=1,
            parent_port_id=2,
            outward_flux_pressure=2.0,
            event_time_key=1.5,
            scheduler_event_index=2,
            rng_sample=0.0,
            edge_delay=1.0,
        )

        results = []
        while (
            model.get_state().packet_ledger.event_queue_records
            or model.get_state().boundary_birth_trial_queue
        ):
            results.append(model.step())

        event_times = [float(result.bookkeeping["event_time_key"]) for result in results]
        event_kinds = [event.kind for result in results for event in result.events]
        live_nodes = set(model.get_state().base_state.topology.iter_live_node_ids())
        live_edges = set(model.get_state().base_state.topology.iter_live_edge_ids())

        self.assertEqual([1.0, 1.5, 2.0], event_times)
        self.assertEqual(sorted(event_times), event_times)
        self.assertIn(LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND, event_kinds)
        self.assertIn(LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND, event_kinds)
        self.assertIn("hybrid_mechanical_expansion", event_kinds)
        self.assertIn(LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT, event_kinds)
        self.assertIn(LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE, event_kinds)
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertEqual([], model.get_state().boundary_birth_trial_queue)
        self.assertAlmostEqual(initial_budget, _runtime_budget_surface(model))
        self.assertAlmostEqual(0.0, model.get_state().packet_ledger.in_flight_packet_total)
        for packet in model.get_state().packet_ledger.packet_records:
            # Arrived packets keep historical endpoints; live-ref checks matter for pending work.
            if packet.packet_state == "arrived":
                continue
            self.assertIn(packet.source_node_id, live_nodes)
            self.assertIn(packet.target_node_id, live_nodes)
            self.assertIn(packet.edge_id, live_edges)
        for node_id, event_time_key in model.get_state().node_last_update_event_time_key.items():
            self.assertLessEqual(event_time_key, model.get_state().event_time_key)
            self.assertGreaterEqual(model.get_state().node_proper_time[node_id], 0.0)

    def test_stress_runtime_snapshot_round_trips_after_mixed_events(self) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(),
            _active_topology_with_boundary_birth_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.schedule_causal_boundary_birth_trial(
            parent_node_id=1,
            parent_port_id=2,
            outward_flux_pressure=2.0,
            event_time_key=1.5,
            scheduler_event_index=2,
            rng_sample=0.0,
            edge_delay=1.0,
        )
        model.run_event_queue(max_events=1)
        while model.get_state().boundary_birth_trial_queue or model.get_state().packet_ledger.event_queue_records:
            model.step()

        snapshot = model.snapshot()
        restored = json.loads(json.dumps(snapshot, sort_keys=True))
        runtime = restored["dynamics"]["lgrc9v3_runtime"]
        event_kinds = [event["kind"] for event in restored["events"]]
        topology_kinds = [event["kind"] for event in runtime["topology_event_log"]]

        self.assertEqual("LGRC9V3", restored["metadata"]["model_family"])
        self.assertEqual(LGRC9V3_RUNTIME_STATE_KIND, runtime["artifact_kind"])
        self.assertIn(LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND, event_kinds)
        self.assertIn(LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND, event_kinds)
        self.assertIn(LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND, topology_kinds)
        self.assertIn("hybrid_mechanical_expansion", topology_kinds)
        self.assertIn(
            LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
            topology_kinds,
        )
        self.assertIn(
            LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            topology_kinds,
        )
        self.assertEqual([], runtime["event_queue_records"])
        self.assertEqual([], runtime["boundary_birth_trial_queue"])
        self.assertEqual(1, runtime["causal_spark_evaluation_index"])
        self.assertTrue(runtime["node_proper_time"])

    def test_stress_default_grc9v3_remains_causal_layer_free_after_lgrc_run(self) -> None:
        lgrc9v3 = LGRC9V3.from_state(_three_node_state(), _PARAMS)
        lgrc9v3.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        lgrc9v3.run_event_queue(max_events=4)

        grc9v3 = GRC9V3.from_state(_three_node_state(), _PARAMS)
        grc_result = grc9v3.step()
        snapshot = grc9v3.snapshot()

        self.assertEqual([], grc_result.events)
        self.assertEqual("GRC9V3", snapshot["metadata"]["model_family"])
        self.assertNotIn("lgrc9v3_runtime", snapshot["dynamics"])
        self.assertNotIn(
            "causal_layer_mode",
            grc9v3.get_state().cached_quantities,
        )


if __name__ == "__main__":
    unittest.main()
