"""Contract tests for the LGRC9V3 timing schema and config surface."""

from __future__ import annotations

import json
import unittest

from pygrc.core import (
    CAUSAL_LAYER,
    GRCEvent,
    InvalidParamsError,
    InvalidStateTransitionError,
    SNAPSHOT_SCHEMA,
    SNAPSHOT_VERSION,
    SnapshotCompatibilityError,
    snapshot_from_json,
    snapshot_to_json,
    validate_snapshot_contract,
)
from pygrc.models import (
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    EDGE_DELAY_POLICY_GEOMETRY_BASELINE,
    EDGE_DELAY_POLICY_GRCV3_TEMPORAL_LABEL,
    FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE,
    LAPSE_POLICY_BOUNDED_DENSITY_TENSION,
    LAPSE_POLICY_UNIT,
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    PROPER_TIME_POLICY_GLOBAL_SCHEDULER,
    GRC9,
    GRC9V3,
    GRC9V3NodeState,
    GRC9V3State,
    LGRC_RUNTIME_LEVEL_LGRC2,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3_DERIVED_EVIDENCE_CLASS,
    LGRC9V3_SEMICAUSAL_EVIDENCE_CLASS,
    LGRC9V3_ANNOTATION_MODE_VERSION,
    LGRC9V3_CAUSAL_ARTIFACT_KEY,
    LGRC9V3_CAUSAL_ARTIFACT_KIND,
    LGRC9V3_CAUSAL_ARTIFACT_SCHEMA_VERSION,
    LGRC9V3_CAUSAL_MODES_KEY,
    LGRC9V3_DEFAULT_CAUSAL_MODES,
    LGRC9V3_TIMING_ALIASES,
    LGRC9V3_TIMING_FIELD_NAMES,
    LGRC9V3_LGRC2_MODE_VERSION,
    LGRC9V3_LGRC2_PACKET_CONTRACT_KIND,
    LGRC9V3_LGRC2_PACKET_CONTRACT_SCHEMA_VERSION,
    LGRC9V3_LGRC2_PACKET_LEDGER_KIND,
    LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION,
    LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_KIND,
    LGRC9V3_LGRC3_MODE_VERSION,
    LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_KIND,
    LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION,
    LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_KIND,
    LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_SCHEMA_VERSION,
    LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_KIND,
    LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_SCHEMA_VERSION,
    LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_KIND,
    LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION,
    LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND,
    LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_SCHEMA_VERSION,
    LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVENT_SCHEMA_VERSION,
    LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_KIND,
    LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_SCHEMA_VERSION,
    LGRC9V3_LGRC3_POLICY_CONTRACT_KIND,
    LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION,
    LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_KIND,
    LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_SCHEMA_VERSION,
    LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_IN_SCOPE,
    LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_OUT_OF_SCOPE,
    LGRC9V3_PACKET_BUDGET_INVARIANT,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
    LGRC9V3_PACKET_EVENT_KINDS,
    LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY,
    LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_DELAY_DERIVED,
    LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_EXPLICIT,
    LGRC9V3_PACKET_FIELD_NAMES,
    LGRC9V3_PACKET_LEDGER_FIELD_NAMES,
    LGRC9V3_PACKET_REQUIRED_FIELDS,
    LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_EVIDENCE_CLASS,
    LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
    LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT,
    LGRC9V3_PENDING_FLUX_EVIDENCE_CLASS,
    LGRC9V3_TOPOLOGY_CONTRACT_EVIDENCE_CLASS,
    LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES,
    LGRC9V3_PACKET_TRANSPORT_EVIDENCE_CLASS,
    LGRC9V3_PROPER_TIME_INHERITANCE_EVIDENCE_CLASS,
    LGRC9V3_COLLAPSE_REABSORPTION_EVIDENCE_CLASS,
    LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS,
    LGRC9V3_PROPER_TIME_IDENTITY_EVALUATION_EVIDENCE_CLASS,
    LGRC9V3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVIDENCE_CLASS,
    LGRC9V3_TOPOLOGY_REPLAY_VALIDATION_EVIDENCE_CLASS,
    LGRC9V3_COLLAPSE_PACKET_TRANSPORT_POLICY_REDIRECT_OR_SETTLE,
    LGRC9V3_LGRC3_POLICY_CONTRACT_EVIDENCE_CLASS,
    LGRC9V3_COLLAPSE_REABSORPTION_REQUIRED_FIELDS,
    LGRC9V3_PROPER_TIME_IDENTITY_REQUIRED_FIELDS,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
    LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
    LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
    LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT,
    LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0,
    LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY,
    LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP,
    LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING,
    LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL,
    LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY,
    LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER,
    LGRC9V3_REFINEMENT_LINEAGE_REQUIRED_FIELDS,
    LGRC9V3_PACKET_TRANSPORT_REQUIRED_FIELDS,
    LGRC9V3_PROPER_TIME_INHERITANCE_REQUIRED_FIELDS,
    LGRC9V3_PACKET_STATE_ARRIVED,
    LGRC9V3_PACKET_STATE_IN_FLIGHT,
    LGRC9V3_PACKET_STATE_SCHEDULED,
    LGRC9V3_PACKET_STATES,
    LGRC9V3_PACKETIZED_EVIDENCE_CLASS,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_BOUNDARY_POLARITY_SCORE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_LOCAL_SUPPORT_MASS,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_PROPER_TIME_PHASE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_SURFACE_DEFORMATION,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_BLOCKER_REQUIRES_LGRC3,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_NODE_ONLY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_KIND,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_SCHEMA_VERSION,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_KIND,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_SCHEMA_VERSION,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_FIELD_NAMES,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KIND_INPUTS,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_REQUIRED_FIELDS,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_SCHEMA_VERSION,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_BLOCKER_REQUIRES_LGRC3,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_KIND,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_SCHEMA_VERSION,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_KIND,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_SCHEMA_VERSION,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_KIND,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_SCHEMA_VERSION,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_KIND,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_SCHEMA_VERSION,
    LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    LGRC9V3PacketArrivalEligibility,
    LGRC9V3CausalPulseSubstrateSurfacePolicy,
    LGRC9V3CausalPulseSubstrateSurfaceLineageRecord,
    LGRC9V3CausalPulseSubstrateSurfaceRow,
    LGRC9V3NativeRouteArbitrationRecord,
    LGRC9V3NativeRouteCandidateRecord,
    LGRC9V3NativeRouteCandidateSetRecord,
    LGRC9V3TopologyStateReabsorptionRecord,
    LGRC9V3PendingFluxLedger,
    LGRC9V3PacketLedger,
    LGRC9V3PacketProcessingResult,
    LGRC9V3PacketQueueEventRecord,
    LGRC9V3PacketRecord,
    LGRC9V3CollapseReabsorptionResult,
    LGRC9V3CollapsePacketTransportResult,
    LGRC9V3ProperTimeInheritanceResult,
    LGRC9V3ProperTimeIdentityPersistenceEvaluation,
    LGRC9V3TopologyReplayValidationResult,
    LGRC9V3RefinementPacketTransportResult,
    LGRC9V3TimingFieldNames,
    PortEdge,
    annotate_lgrc9v3_causal_history,
    attach_lgrc9v3_causal_history_artifact,
    build_lgrc9v3_causal_history_artifact,
    build_lgrc9v3_causal_pulse_substrate_surface_contract_artifact,
    build_lgrc9v3_causal_pulse_substrate_surface_digest,
    build_lgrc9v3_causal_pulse_substrate_surface_lineage_record_digest,
    build_lgrc9v3_disabled_causal_pulse_substrate_surface_policy,
    build_lgrc9v3_topology_event_digest,
    build_lgrc9v3_topology_state_reabsorption_record_digest,
    build_lgrc9v3_native_route_arbitration_record_digest,
    build_lgrc9v3_native_route_candidate_record_digest,
    build_lgrc9v3_native_route_candidate_set_record_digest,
    build_lgrc9v3_packet_event_id,
    build_lgrc9v3_packet_id,
    build_lgrc9v3_packet_contract_artifact,
    build_lgrc9v3_packet_ledger,
    build_lgrc9v3_lgrc3_policy_contract_artifact,
    build_lgrc9v3_topology_contract_artifact,
    compact_lgrc9v3_packet_ledger,
    compute_lgrc9v3_causal_distances,
    compute_lgrc9v3_edge_causal_delay,
    compute_lgrc9v3_fixed_topology_eligibility,
    compute_lgrc9v3_functional_distances,
    compute_lgrc9v3_geometric_distances,
    compute_lgrc9v3_lapse_by_node,
    create_lgrc9v3_packet_queue_event_record,
    create_lgrc9v3_packet_record,
    derive_lgrc9v3_packet_arrival_eligibility,
    derive_lgrc9v3_packet_arrival_event_time_key,
    evaluate_lgrc9v3_proper_time_identity_persistence,
    emit_lgrc9v3_proper_time_identity_acceptance,
    validate_lgrc9v3_topology_event_replay,
    extract_lgrc9v3_causal_history_artifact,
    process_lgrc9v3_next_packet_event,
    process_lgrc9v3_packet_arrival,
    process_lgrc9v3_packet_departure,
    process_lgrc9v3_collapse_reabsorption,
    process_lgrc9v3_proper_time_inheritance,
    schedule_lgrc9v3_packet_departure,
    transport_lgrc9v3_packets_through_collapse_reabsorption,
    transport_lgrc9v3_packets_through_refinement,
    restore_lgrc9v3_causal_annotation_artifact,
    restore_lgrc9v3_causal_pulse_substrate_surface_policy_artifact,
    restore_lgrc9v3_causal_pulse_substrate_surface_lineage_record_artifact,
    restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact,
    restore_lgrc9v3_topology_state_reabsorption_record_artifact,
    restore_lgrc9v3_native_route_arbitration_record_artifact,
    restore_lgrc9v3_native_route_candidate_record_artifact,
    restore_lgrc9v3_native_route_candidate_set_record_artifact,
    restore_lgrc9v3_collapse_reabsorption_artifact,
    restore_lgrc9v3_collapse_packet_transport_artifact,
    restore_lgrc9v3_lgrc3_policy_contract_artifact,
    restore_lgrc9v3_pending_flux_ledger_artifact,
    restore_lgrc9v3_packet_ledger_artifact,
    restore_lgrc9v3_packet_queue_event_record,
    restore_lgrc9v3_packet_record,
    restore_lgrc9v3_proper_time_inheritance_artifact,
    restore_lgrc9v3_proper_time_identity_evaluation_artifact,
    validate_lgrc9v3_causal_modes,
)
from pygrc.core import PortGraphBackend
from tests.models.test_grc_9_v3_column_h_assisted import (
    _column_h_state as _lane_b_column_h_state,
    _config as _lane_b_config,
)
from tests.models.test_grc_9_v3_sparks import (
    _saturated_candidate_state as _lane_a_saturated_candidate_state,
    _spark_params as _lane_a_spark_params,
)


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
            node_0: GRC9V3NodeState(coherence=1.0, gradient_row_basis=[0.0, 0.0, 0.0]),
            node_1: GRC9V3NodeState(coherence=2.0, gradient_row_basis=[3.0, 4.0, 0.0]),
            node_2: GRC9V3NodeState(coherence=3.0, gradient_row_basis=[0.0, 0.0, 0.0]),
        },
        port_edges={
            edge_01: PortEdge(node_0, 1, node_1, 1, conductance=100.0, flux_uv=0.0),
            edge_12: PortEdge(node_1, 2, node_2, 1, conductance=100.0, flux_uv=1.0),
            edge_02: PortEdge(node_0, 2, node_2, 2, conductance=1.0, flux_uv=4.0),
        },
        base_conductance={edge_01: 100.0, edge_12: 100.0, edge_02: 1.0},
        geometric_length={edge_01: 2.0, edge_12: 2.0, edge_02: 5.0},
        temporal_delay={edge_01: 11.0, edge_12: 12.0, edge_02: 13.0},
        flux_coupling={edge_01: 0.0, edge_12: 1.0, edge_02: 4.0},
    )


def _minimal_snapshot() -> dict[str, object]:
    return {
        "metadata": {
            "snapshot_schema": SNAPSHOT_SCHEMA,
            "snapshot_version": SNAPSHOT_VERSION,
            "model_family": "GRC9V3",
            "step_index": 0,
            "params": {},
            "resolved_params": {},
            "params_hash": "test",
            "capabilities": [],
        },
        "topology": {},
    }


def _fake_refinement_expansion_event() -> GRCEvent:
    return GRCEvent(
        kind="hybrid_mechanical_expansion",
        step_index=0,
        payload={
            "sink_node_id": 0,
            "expansion_id": "hybrid-spark-0-0",
            "source_candidate_event_id": "candidate-0",
            "module_node_ids": [3, 4, 5, 6],
            "internal_edge_ids": [10, 11, 12],
            "reassignment_map": {
                "0": {
                    "from_port_id": 1,
                    "to_node_id": 3,
                    "to_port_id": 4,
                }
            },
        },
    )


def _fake_post_refinement_topology_signature() -> dict[str, object]:
    return {
        "node_ids": [1, 2, 3, 4, 5, 6],
        "edge_records": [
            {
                "edge_id": 0,
                "endpoints": [[3, 3], [1, 0]],
            },
            {
                "edge_id": 1,
                "endpoints": [[1, 1], [2, 0]],
            },
        ],
    }


def _valid_lgrc3_replay_items() -> tuple[object, ...]:
    state = _three_node_state()
    ledger = build_lgrc9v3_packet_ledger(state=state)
    departure = process_lgrc9v3_packet_departure(
        state,
        ledger,
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        arrival_event_time_key=3.0,
        scheduler_event_index=1,
        source_lineage_id="source-root",
        target_lineage_id="target-root",
    )
    refinement_transport = transport_lgrc9v3_packets_through_refinement(
        departure.ledger,
        _fake_refinement_expansion_event(),
        post_topology_signature=_fake_post_refinement_topology_signature(),
        pending_flux_ledger=compact_lgrc9v3_packet_ledger(departure.ledger),
    )
    inheritance = process_lgrc9v3_proper_time_inheritance(
        _fake_refinement_expansion_event(),
        parent_node_proper_time={0: 1.0},
        event_time_key=1.0,
        scheduler_event_index=2,
        checkpoint_index=1,
    )
    collapse = process_lgrc9v3_collapse_reabsorption(
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        competing_sink_ids=(0, 2),
        selected_sink_id=2,
        losing_sink_ids=(0,),
        transferred_node_ids=(0,),
        lineage_transfer_map={0: "sink-2"},
        source_lineage_ids={0: "sink-0"},
        target_lineage_id="sink-2",
        node_proper_time={0: 4.0, 2: 9.0},
        coherence_transfer_amount=1.0,
        budget_before=refinement_transport.budget_after,
        event_time_key=8.0,
        scheduler_event_index=6,
        checkpoint_index=3,
        packet_ledger=departure.ledger,
        collapse_reabsorption_allowed=True,
    )
    collapse_transport = transport_lgrc9v3_packets_through_collapse_reabsorption(
        departure.ledger,
        collapse,
        pending_flux_ledger=compact_lgrc9v3_packet_ledger(departure.ledger),
    )
    evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
        source_topology_event_ids=(collapse.topology_event_id,),
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        sink_node_id=2,
        lineage_id="sink-2",
        basin_node_ids=(2, 5),
        node_proper_time={2: 13.0, 5: 12.0},
        window_start_sink_proper_time=4.0,
        window_start_event_time_key=8.0,
        window_end_event_time_key=12.0,
        scheduler_event_index=8,
        checkpoint_index=4,
        event_time_key=12.0,
        local_median_edge_delay=2.0,
        source_basin_evidence_id="basin-core-sink-2",
        budget_before=collapse_transport.budget_after,
        budget_after=collapse_transport.budget_after,
    )
    identity_event = emit_lgrc9v3_proper_time_identity_acceptance(
        evaluation,
        identity_acceptance_allowed=True,
    )
    return (
        refinement_transport.to_artifact(),
        inheritance.to_artifact(),
        collapse.to_artifact(),
        collapse_transport.to_artifact(),
        evaluation.to_artifact(),
        identity_event,
    )


def _valid_pulse_surface_row(**overrides: object) -> LGRC9V3CausalPulseSubstrateSurfaceRow:
    values: dict[str, object] = {
        "surface_id": "surface-row-1",
        "surface_policy_id": "surface-policy-test",
        "surface_policy_enabled": True,
        "surface_policy_validated": False,
        "route_aspect_id": "route-aspect-cw",
        "route_aspect_digest": "route-digest",
        "pulse_event_id": "packet-event-1",
        "pulse_packet_id": "packet-1",
        "pulse_event_kind": LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        "pulse_channel_id": "S1_to_K2",
        "pulse_route_step": 1,
        "event_time_key": 2.0,
        "scheduler_event_index": 3,
        "node_proper_time": {1: 2.0, 2: 2.5},
        "source_node_id": 1,
        "target_node_id": 2,
        "contact_amount": 0.25,
        "surface_state_id": "surface-state-1",
        "surface_state_digest": "surface-state-digest",
        "surface_kind": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
        "surface_nodes": (1, 2),
        "surface_values_before": {"contact_mass": 0.0},
        "surface_values_after": {"contact_mass": 0.25},
        "runtime_visible_inputs": (
            "committed_packet_event",
            "route_aspect_digest",
            "pulse_channel_id",
        ),
        "surface_update_policy": {
            "policy_id": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED,
            "version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
            "activation_gate": "committed_packet_event",
            "allowed_surface_kinds": [
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT
            ],
        },
        "surface_budget_surface": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_NODE_ONLY,
        "surface_budget_before": 1.0,
        "surface_budget_after": 1.0,
        "surface_budget_error": 0.0,
        "lineage_status": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
        "producer_records": (),
        "claim_flags": {
            "movement_claim_allowed": False,
            "native_m6": False,
        },
    }
    values.update(overrides)
    return LGRC9V3CausalPulseSubstrateSurfaceRow(**values)  # type: ignore[arg-type]


def _valid_surface_lineage_record(
    **overrides: object,
) -> LGRC9V3CausalPulseSubstrateSurfaceLineageRecord:
    source_row = _valid_pulse_surface_row()
    topology_event = {
        "artifact_kind": "lgrc9v3_refinement_topology_event",
        "topology_event_id": "topology-event-1",
        "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT,
        "scheduler_event_index": 4,
        "checkpoint_index": 2,
        "event_time_key": 3.0,
    }
    values: dict[str, object] = {
        "surface_lineage_record_id": "surface-lineage-1",
        "surface_lineage_policy_id": "surface-lineage-policy-v1",
        "surface_lineage_transport_enabled": True,
        "surface_lineage_transport_validated": False,
        "source_surface_id": source_row.surface_id,
        "source_surface_digest": source_row.surface_digest,
        "topology_event_id": "topology-event-1",
        "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT,
        "topology_event_digest": build_lgrc9v3_topology_event_digest(topology_event),
        "event_time_key": 3.0,
        "scheduler_event_index": 4,
        "checkpoint_index": 2,
        "lineage_transfer_map": {"1": "10", "2": "11"},
        "source_surface_nodes": (1, 2),
        "target_surface_nodes": (10, 11),
        "source_surface_ports": None,
        "target_surface_ports": None,
        "lineage_action": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
        "lineage_status": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
        "surface_budget_surface": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_NODE_ONLY,
        "surface_budget_before": 1.0,
        "surface_budget_after": 1.0,
        "surface_budget_error": 0.0,
        "node_plus_packet_budget_before": 5.0,
        "node_plus_packet_budget_after": 5.0,
        "node_plus_packet_budget_error": 0.0,
        "transported_surface_id": "surface-row-1-transported",
        "transported_surface_digest": "transported-surface-digest",
        "superseded_surface_id": None,
        "producer_stale_read_blocker": None,
        "claim_flags": {
            "movement_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
        },
    }
    values.update(overrides)
    return LGRC9V3CausalPulseSubstrateSurfaceLineageRecord(**values)  # type: ignore[arg-type]


def _valid_topology_state_reabsorption_record(
    **overrides: object,
) -> LGRC9V3TopologyStateReabsorptionRecord:
    topology_event = {
        "artifact_kind": "lgrc9v3_refinement_topology_event",
        "topology_event_id": "topology-event-1",
        "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT,
        "scheduler_event_index": 4,
        "checkpoint_index": 2,
        "event_time_key": 3.0,
    }
    values: dict[str, object] = {
        "topology_state_reabsorption_record_id": "state-reabsorption-1",
        "topology_state_reabsorption_policy_id": (
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
        ),
        "topology_state_reabsorption_enabled": True,
        "topology_state_reabsorption_validated": False,
        "topology_event_id": "topology-event-1",
        "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT,
        "topology_event_digest": build_lgrc9v3_topology_event_digest(topology_event),
        "topology_event_committed": True,
        "event_time_key": 3.0,
        "scheduler_event_index": 4,
        "checkpoint_index": 2,
        "lineage_transfer_map": {"1": "10", "2": "11"},
        "source_node_ids": (1, 2),
        "target_node_ids": (10, 11),
        "retired_node_ids": (1, 2),
        "source_edge_ids": (5,),
        "target_edge_ids": (50,),
        "retired_edge_ids": (5,),
        "node_state_before": {1: 0.4, 2: 0.6},
        "node_state_after": {10: 0.4, 11: 0.6},
        "edge_state_before": {5: {1: 1.0, 2: 1.0}},
        "edge_state_after": {50: {10: 1.0, 11: 1.0}},
        "packet_ledger_digest_before": "packet-ledger-before",
        "packet_ledger_digest_after": "packet-ledger-after",
        "active_node_state_total_before": 1.0,
        "active_node_state_total_after": 1.0,
        "packet_ledger_node_total_before": 1.0,
        "packet_ledger_node_total_after": 1.0,
        "packet_ledger_in_flight_packet_total_before": 5.0,
        "packet_ledger_in_flight_packet_total_after": 5.0,
        "packet_ledger_conserved_budget_total_before": 6.0,
        "packet_ledger_conserved_budget_total_after": 6.0,
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_after": 6.0,
        "node_plus_packet_budget_error": 0.0,
        "active_state_digest_before": "active-state-before",
        "active_state_digest_after": "active-state-after",
        "state_reabsorption_action": LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED,
        "claim_flags": {
            "movement_claim_allowed": False,
            "topology_mutating_movement_claim_allowed": False,
        },
    }
    values.update(overrides)
    return LGRC9V3TopologyStateReabsorptionRecord(**values)  # type: ignore[arg-type]


def _valid_native_route_candidate_record(
    **overrides: object,
) -> LGRC9V3NativeRouteCandidateRecord:
    values: dict[str, object] = {
        "candidate_route_id": "route-candidate-a",
        "native_route_arbitration_policy_id": (
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
        ),
        "native_route_arbitration_enabled": True,
        "candidate_set_id": "candidate-set-1",
        "candidate_source_surface_digest": "surface-digest-a",
        "candidate_source_producer_record_id": "producer-record-a",
        "candidate_source_topology_state_reabsorption_digest": (
            "state-reabsorption-digest-a"
        ),
        "route_intent": LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
        "candidate_topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        "candidate_competing_sink_ids": (10, 11),
        "candidate_losing_sink_ids": (11,),
        "candidate_selected_sink_id": 10,
        "candidate_transferred_node_ids": (4, 5),
        "candidate_lineage_transfer_map": {"4": "10", "5": "10"},
        "candidate_source_node_ids": (4, 5),
        "candidate_target_node_ids": (10,),
        "candidate_retired_node_ids": (4, 5),
        "candidate_source_edge_ids": (7,),
        "candidate_target_edge_ids": (17,),
        "candidate_retired_edge_ids": (7,),
        "candidate_route_score": 1.25,
        "candidate_score_components": {
            "surface_polarity": 1.0,
            "local_preference": 0.25,
        },
        "candidate_budget_prediction": {
            "node_plus_packet_budget_before": 6.0,
            "node_plus_packet_budget_after": 6.0,
            "node_plus_packet_budget_error": 0.0,
        },
        "candidate_order_key": (
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
        ),
        "candidate_runtime_visible_inputs": (
            "surface_polarity",
            "local_preference",
            "declared_policy_weight",
        ),
        "event_time_key": 4.0,
        "scheduler_event_index": 8,
        "claim_flags": {
            "movement_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
        },
    }
    values.update(overrides)
    return LGRC9V3NativeRouteCandidateRecord(**values)  # type: ignore[arg-type]


def _valid_native_route_candidate_set_record(
    **overrides: object,
) -> LGRC9V3NativeRouteCandidateSetRecord:
    candidate = _valid_native_route_candidate_record()
    values: dict[str, object] = {
        "candidate_set_id": "candidate-set-1",
        "native_route_arbitration_policy_id": (
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
        ),
        "native_route_arbitration_enabled": True,
        "arbitration_window_id": "window-1",
        "event_time_key": 4.0,
        "scheduler_event_index": 9,
        "candidate_route_digests": (candidate.candidate_route_digest,),
        "candidate_set_order_key": (
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
        ),
        "unresolved_tie_policy": LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
        "claim_flags": {
            "movement_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
        },
    }
    values.update(overrides)
    return LGRC9V3NativeRouteCandidateSetRecord(**values)  # type: ignore[arg-type]


def _valid_native_route_arbitration_record(
    **overrides: object,
) -> LGRC9V3NativeRouteArbitrationRecord:
    candidate = _valid_native_route_candidate_record()
    candidate_set = _valid_native_route_candidate_set_record(
        candidate_route_digests=(candidate.candidate_route_digest,)
    )
    values: dict[str, object] = {
        "native_route_arbitration_record_id": "route-arbitration-1",
        "native_route_arbitration_policy_id": (
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
        ),
        "native_route_arbitration_enabled": True,
        "candidate_set_id": candidate_set.candidate_set_id,
        "candidate_set_digest": candidate_set.candidate_set_digest,
        "selected_candidate_route_id": candidate.candidate_route_id,
        "selected_candidate_route_digest": candidate.candidate_route_digest,
        "rejected_candidate_route_digests": ("rejected-route-digest",),
        "arbitration_reason_code": (
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE
        ),
        "arbitration_score": 1.25,
        "arbitration_rule": (
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
        ),
        "arbitration_runtime_visible_inputs": (
            "candidate_route_score",
            "candidate_order_key",
            "declared_policy_weight",
        ),
        "selected_topology_event_id": "selected-topology-event-1",
        "selected_topology_event_digest": "selected-topology-event-digest",
        "event_time_key": 4.5,
        "scheduler_event_index": 10,
        "claim_flags": {
            "movement_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
        },
    }
    values.update(overrides)
    return LGRC9V3NativeRouteArbitrationRecord(**values)  # type: ignore[arg-type]


class LGRC9V3ContractTest(unittest.TestCase):
    """Validate Phase 8 Iteration 1 without changing GRC9V3 behavior."""

    def test_causal_pulse_substrate_contract_is_default_off(self) -> None:
        contract = build_lgrc9v3_causal_pulse_substrate_surface_contract_artifact()
        policy = contract["surface_policy"]

        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_KIND,
            contract["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_SCHEMA_VERSION,
            contract["artifact_schema_version"],
        )
        self.assertEqual("lgrc2", contract["required_lgrc_level"])
        self.assertTrue(contract["fixed_topology_only"])
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED,
            contract["topology_lineage_status"],
        )
        self.assertEqual(2, contract["min_lgrc_level"])
        self.assertEqual(
            "sha256",
            contract["digest_specification"]["algorithm"],
        )
        self.assertIn(
            "surface_digest",
            contract["digest_specification"]["excluded_fields"],
        )
        self.assertIn(
            "lgrc_runtime_level",
            contract["system_only_fields"],
        )
        self.assertEqual(
            ["producer_records", "scheduling_eligibility"],
            contract["producer_writable_fields"],
        )
        self.assertFalse(
            contract["synchronous_limit_behavior"]["causal_advantage_claim_allowed"]
        )
        self.assertFalse(policy["surface_policy_enabled"])
        self.assertFalse(policy["surface_policy_validated"])
        self.assertFalse(policy["native_lgrc_pulse_substrate_supported"])
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED,
            policy["surface_policy"],
        )
        self.assertFalse(policy["disabled_semantics"]["surface_rows_emitted"])
        self.assertFalse(
            policy["disabled_semantics"]["producers_evaluate_eligibility"]
        )
        self.assertFalse(contract["native_claim_flags"]["movement_claim_allowed"])
        self.assertFalse(contract["native_claim_flags"]["native_m6"])

    def test_causal_pulse_substrate_kind_inputs_are_declared(self) -> None:
        expected_kinds = {
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_LOCAL_SUPPORT_MASS,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_BOUNDARY_POLARITY_SCORE,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_PROPER_TIME_PHASE,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_SURFACE_DEFORMATION,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY,
        }

        self.assertEqual(expected_kinds, set(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KIND_INPUTS))
        self.assertIn(
            "front_mask",
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KIND_INPUTS[
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_BOUNDARY_POLARITY_SCORE
            ],
        )
        self.assertIn(
            "route_aspect_digest",
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KIND_INPUTS[
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT
            ],
        )
        self.assertIn(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_FIELD_NAMES.surface_digest,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_REQUIRED_FIELDS,
        )

    def test_causal_pulse_substrate_policy_round_trips(self) -> None:
        policy = build_lgrc9v3_disabled_causal_pulse_substrate_surface_policy()
        restored = restore_lgrc9v3_causal_pulse_substrate_surface_policy_artifact(
            json.loads(json.dumps(policy.to_artifact()))
        )

        self.assertEqual(policy, restored)
        self.assertIsInstance(restored, LGRC9V3CausalPulseSubstrateSurfacePolicy)
        with self.assertRaises(ValueError):
            LGRC9V3CausalPulseSubstrateSurfacePolicy(
                surface_policy_id="bad",
                surface_policy=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED,
                surface_policy_enabled=True,
            )

    def test_causal_pulse_substrate_surface_row_round_trips(self) -> None:
        row = _valid_pulse_surface_row()
        artifact = row.to_artifact()
        restored = restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact(
            json.loads(json.dumps(artifact))
        )

        self.assertEqual(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND, artifact["artifact_kind"])
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(row, restored)
        self.assertEqual(
            artifact["surface_digest"],
            build_lgrc9v3_causal_pulse_substrate_surface_digest(
                row.to_artifact(include_digest=False)
            ),
        )

    def test_causal_pulse_substrate_digest_is_stable_and_sensitive(self) -> None:
        row = _valid_pulse_surface_row()
        same = _valid_pulse_surface_row()
        changed = _valid_pulse_surface_row(
            contact_amount=0.5,
            surface_values_after={"contact_mass": 0.5},
        )

        self.assertEqual(row.surface_digest, same.surface_digest)
        self.assertNotEqual(row.surface_digest, changed.surface_digest)

    def test_causal_pulse_substrate_schema_rejects_hidden_inputs(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(
                surface_values_after={
                    "contact_mass": 0.25,
                    "preauthored_itinerary": [1, 2, 3],
                }
            )

    def test_causal_pulse_substrate_schema_rejects_below_lgrc2(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(lgrc_runtime_level="lgrc1")

    def test_causal_pulse_substrate_schema_rejects_merged_budget_fields(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(
                surface_values_before={"node_plus_packet_budget": 5.0},
            )

    def test_causal_pulse_substrate_schema_rejects_producer_system_writes(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(
                producer_records=(
                    {
                        "record_id": "producer-write",
                        "direct_centroid_write": True,
                    },
                )
            )

    def test_causal_pulse_substrate_schema_rejects_unknown_surface_kind(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(surface_kind="unknown_surface_kind")

    def test_causal_pulse_substrate_schema_rejects_invalid_update_policy(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(
                surface_update_policy={
                    "policy_id": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED,
                    "version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
                    "activation_gate": "committed_packet_event",
                }
            )

    def test_causal_pulse_substrate_schema_rejects_nonfixed_lineage(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(
                lineage_status=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED,
            )

    def test_causal_pulse_substrate_schema_rejects_claim_promotion(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(
                claim_flags={
                    "movement_claim_allowed": True,
                }
            )

    def test_causal_pulse_substrate_schema_rejects_missing_kind_inputs(self) -> None:
        with self.assertRaises(ValueError):
            _valid_pulse_surface_row(
                surface_kind=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_BOUNDARY_POLARITY_SCORE,
                runtime_visible_inputs=("node_coherence", "front_mask"),
            )

    def test_causal_pulse_substrate_default_off_is_synchronous_noop(self) -> None:
        policy = build_lgrc9v3_disabled_causal_pulse_substrate_surface_policy()
        contract = build_lgrc9v3_causal_pulse_substrate_surface_contract_artifact()

        self.assertFalse(policy.surface_policy_enabled)
        self.assertFalse(policy.coupling_producer_enabled)
        self.assertFalse(policy.feedback_producer_enabled)
        self.assertFalse(contract["surface_policy"]["surface_policy_enabled"])
        self.assertEqual([], contract.get("surface_rows", []))

    def test_causal_pulse_substrate_synchronous_limit_row_has_no_claim(self) -> None:
        row = _valid_pulse_surface_row(
            node_proper_time={1: 1.0, 2: 1.0},
            claim_flags={
                "movement_claim_allowed": False,
                "causal_advantage_claim_allowed": False,
            },
        )

        self.assertFalse(row.to_artifact()["claim_flags"]["movement_claim_allowed"])
        self.assertFalse(
            row.to_artifact()["claim_flags"]["causal_advantage_claim_allowed"]
        )

    def test_causal_pulse_substrate_lineage_record_round_trips(self) -> None:
        record = _valid_surface_lineage_record()
        artifact = record.to_artifact()
        restored = restore_lgrc9v3_causal_pulse_substrate_surface_lineage_record_artifact(
            json.loads(json.dumps(artifact))
        )

        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(record, restored)
        self.assertEqual(
            artifact["lineage_record_digest"],
            build_lgrc9v3_causal_pulse_substrate_surface_lineage_record_digest(
                record.to_artifact(include_digest=False)
            ),
        )

    def test_causal_pulse_substrate_lineage_digest_is_stable_and_sensitive(
        self,
    ) -> None:
        record = _valid_surface_lineage_record()
        same = _valid_surface_lineage_record()
        changed = _valid_surface_lineage_record(
            lineage_transfer_map={"1": "10", "2": "12"},
            target_surface_nodes=(10, 12),
        )

        self.assertEqual(record.lineage_record_digest, same.lineage_record_digest)
        self.assertEqual(record.idempotency_key, same.idempotency_key)
        self.assertNotEqual(
            record.lineage_record_digest,
            changed.lineage_record_digest,
        )
        self.assertNotEqual(record.idempotency_key, changed.idempotency_key)

    def test_topology_event_digest_is_stable_and_derived(self) -> None:
        topology_event = {
            "topology_event_id": "topology-event-1",
            "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT,
            "scheduler_event_index": 4,
        }
        digest = build_lgrc9v3_topology_event_digest(topology_event)
        with_digest = dict(topology_event)
        with_digest["topology_event_digest"] = "ignored-digest"

        self.assertEqual(digest, build_lgrc9v3_topology_event_digest(with_digest))
        changed = dict(topology_event)
        changed["scheduler_event_index"] = 5
        self.assertNotEqual(digest, build_lgrc9v3_topology_event_digest(changed))

    def test_causal_pulse_substrate_lineage_schema_rejects_below_lgrc3(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_BLOCKER_REQUIRES_LGRC3,
        ):
            _valid_surface_lineage_record(lgrc_runtime_level=LGRC_RUNTIME_LEVEL_LGRC2)

    def test_causal_pulse_substrate_lineage_schema_rejects_bad_inputs(self) -> None:
        bad_cases = (
            {"topology_event_id": ""},
            {"lineage_transfer_map": {}},
            {"surface_budget_surface": "node_plus_packet"},
            {"claim_flags": {"movement_claim_allowed": True}},
        )
        for overrides in bad_cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    _valid_surface_lineage_record(**overrides)

    def test_causal_pulse_substrate_lineage_schema_supports_supersession(
        self,
    ) -> None:
        record = _valid_surface_lineage_record(
            lineage_action=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED,
            lineage_status=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED,
            target_surface_nodes=(),
            transported_surface_id=None,
            transported_surface_digest=None,
            superseded_surface_id="surface-row-1",
            producer_stale_read_blocker="surface_row_superseded_by_topology_event",
        )

        artifact = record.to_artifact()
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED,
            artifact["lineage_action"],
        )
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED,
            artifact["lineage_status"],
        )

    def test_causal_modes_allow_lineage_transport_only_in_lgrc3(self) -> None:
        with self.assertRaisesRegex(
            InvalidParamsError,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_BLOCKER_REQUIRES_LGRC3,
        ):
            validate_lgrc9v3_causal_modes(
                {
                    "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
                    "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
                    "causal_pulse_substrate_surface_enabled": True,
                    "causal_pulse_substrate_surface_policy": (
                        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
                    ),
                    "causal_pulse_substrate_surface_lineage_transport_enabled": True,
                    "causal_pulse_substrate_surface_lineage_transport_policy": (
                        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
                    ),
                }
            )

        modes = validate_lgrc9v3_causal_modes(
            {
                "causal_layer_mode": (
                    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
                ),
                "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
                "proper_time_accumulation_policy": PROPER_TIME_POLICY_GLOBAL_SCHEDULER,
                "causal_pulse_substrate_surface_enabled": True,
                "causal_pulse_substrate_surface_policy": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
                ),
                "causal_pulse_substrate_surface_lineage_transport_enabled": True,
                "causal_pulse_substrate_surface_lineage_transport_policy": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
                ),
            }
        )

        self.assertTrue(
            modes["causal_pulse_substrate_surface_lineage_transport_enabled"]
        )

    def test_topology_state_reabsorption_default_modes_are_disabled(self) -> None:
        modes = validate_lgrc9v3_causal_modes()

        self.assertFalse(modes["causal_topology_state_reabsorption_enabled"])
        self.assertEqual(
            "disabled",
            modes["causal_topology_state_reabsorption_policy"],
        )
        self.assertFalse(modes["causal_topology_state_reabsorption_validated"])
        self.assertFalse(modes["causal_topology_state_reabsorption_supported"])

    def test_topology_state_reabsorption_record_round_trips(self) -> None:
        record = _valid_topology_state_reabsorption_record()
        artifact = record.to_artifact()
        restored = restore_lgrc9v3_topology_state_reabsorption_record_artifact(
            json.loads(json.dumps(artifact))
        )

        self.assertEqual(
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(record, restored)
        self.assertEqual(
            artifact["topology_state_reabsorption_digest"],
            build_lgrc9v3_topology_state_reabsorption_record_digest(
                record.to_artifact(include_digest=False)
            ),
        )

    def test_topology_state_reabsorption_digest_is_stable_and_sensitive(
        self,
    ) -> None:
        record = _valid_topology_state_reabsorption_record()
        same = _valid_topology_state_reabsorption_record()
        changed = _valid_topology_state_reabsorption_record(
            lineage_transfer_map={"1": "10", "2": "12"},
            target_node_ids=(10, 12),
            node_state_after={10: 0.4, 12: 0.6},
        )

        self.assertEqual(
            record.topology_state_reabsorption_digest,
            same.topology_state_reabsorption_digest,
        )
        self.assertEqual(record.idempotency_key, same.idempotency_key)
        self.assertNotEqual(
            record.topology_state_reabsorption_digest,
            changed.topology_state_reabsorption_digest,
        )
        self.assertNotEqual(record.idempotency_key, changed.idempotency_key)

    def test_topology_state_reabsorption_schema_rejects_bad_inputs(self) -> None:
        bad_cases = (
            {"topology_event_id": ""},
            {"topology_event_committed": False},
            {"lineage_transfer_map": {}},
            {"lineage_transfer_map": {"1": "10"}},
            {"source_node_ids": ()},
            {"claim_flags": {"movement_claim_allowed": True}},
            {
                "node_plus_packet_budget_before": 6.0,
                "node_plus_packet_budget_after": 5.9,
                "node_plus_packet_budget_error": 0.0,
            },
            {"active_node_state_total_after": 0.9},
            {"packet_ledger_node_total_after": 0.9},
            {"packet_ledger_conserved_budget_total_after": 5.9},
            {
                "state_reabsorption_action": (
                    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED
                ),
                "target_node_ids": (),
            },
        )
        for overrides in bad_cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    _valid_topology_state_reabsorption_record(**overrides)

    def test_topology_state_reabsorption_schema_rejects_below_lgrc3(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_BLOCKER_REQUIRES_LGRC3,
        ):
            _valid_topology_state_reabsorption_record(
                lgrc_runtime_level=LGRC_RUNTIME_LEVEL_LGRC2
            )

    def test_causal_modes_gate_topology_state_reabsorption_to_lgrc3(self) -> None:
        with self.assertRaisesRegex(
            InvalidParamsError,
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_BLOCKER_REQUIRES_LGRC3,
        ):
            validate_lgrc9v3_causal_modes(
                {
                    "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
                    "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
                    "causal_topology_integration_allowed": True,
                    "causal_topology_state_reabsorption_enabled": True,
                    "causal_topology_state_reabsorption_policy": (
                        LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
                    ),
                }
            )

        modes = validate_lgrc9v3_causal_modes(
            {
                "causal_layer_mode": (
                    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
                ),
                "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
                "proper_time_accumulation_policy": PROPER_TIME_POLICY_GLOBAL_SCHEDULER,
                "causal_topology_integration_allowed": True,
                "causal_topology_state_reabsorption_enabled": True,
                "causal_topology_state_reabsorption_policy": (
                    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
                ),
            }
        )

        self.assertTrue(modes["causal_topology_state_reabsorption_enabled"])

    def test_causal_modes_reject_topology_state_flag_mismatches(self) -> None:
        bad_modes = (
            {
                "causal_topology_state_reabsorption_policy": (
                    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
                ),
            },
            {
                "causal_topology_state_reabsorption_validated": True,
            },
            {
                "causal_topology_state_reabsorption_supported": True,
            },
            {
                "causal_topology_state_reabsorption_enabled": True,
                "causal_topology_state_reabsorption_policy": (
                    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
                ),
            },
        )
        for modes in bad_modes:
            with self.subTest(modes=modes):
                with self.assertRaises(InvalidParamsError):
                    validate_lgrc9v3_causal_modes(modes)

    def test_native_route_arbitration_default_modes_are_disabled(self) -> None:
        modes = validate_lgrc9v3_causal_modes()

        self.assertFalse(modes["native_lgrc_route_arbitration_enabled"])
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED,
            modes["native_lgrc_route_arbitration_policy"],
        )
        self.assertFalse(modes["native_lgrc_route_arbitration_validated"])
        self.assertFalse(modes["native_lgrc_route_arbitration_supported"])

    def test_causal_modes_gate_native_route_arbitration_to_lgrc3(self) -> None:
        with self.assertRaisesRegex(
            InvalidParamsError,
            "native_lgrc_route_arbitration_requires_lgrc3",
        ):
            validate_lgrc9v3_causal_modes(
                {
                    "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
                    "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
                    "native_lgrc_route_arbitration_enabled": True,
                    "native_lgrc_route_arbitration_policy": (
                        LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
                    ),
                }
            )

        modes = validate_lgrc9v3_causal_modes(
            {
                "causal_layer_mode": (
                    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
                ),
                "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
                "proper_time_accumulation_policy": PROPER_TIME_POLICY_GLOBAL_SCHEDULER,
                "causal_topology_integration_allowed": True,
                "causal_pulse_substrate_surface_enabled": True,
                "causal_pulse_substrate_surface_policy": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
                ),
                "causal_pulse_substrate_surface_lineage_transport_enabled": True,
                "causal_pulse_substrate_surface_lineage_transport_policy": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
                ),
                "causal_pulse_substrate_surface_lineage_transport_validated": True,
                "causal_pulse_substrate_surface_lineage_transport_supported": True,
                "causal_topology_state_reabsorption_enabled": True,
                "causal_topology_state_reabsorption_policy": (
                    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
                ),
                "causal_topology_state_reabsorption_validated": True,
                "causal_topology_state_reabsorption_supported": True,
                "native_lgrc_route_arbitration_enabled": True,
                "native_lgrc_route_arbitration_policy": (
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
                ),
            }
        )

        self.assertTrue(modes["native_lgrc_route_arbitration_enabled"])

    def test_causal_modes_reject_native_route_arbitration_flag_mismatches(
        self,
    ) -> None:
        bad_modes = (
            {
                "native_lgrc_route_arbitration_policy": (
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
                ),
            },
            {"native_lgrc_route_arbitration_validated": True},
            {"native_lgrc_route_arbitration_supported": True},
            {
                "causal_layer_mode": (
                    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
                ),
                "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
                "proper_time_accumulation_policy": PROPER_TIME_POLICY_GLOBAL_SCHEDULER,
                "causal_topology_integration_allowed": True,
                "native_lgrc_route_arbitration_enabled": True,
                "native_lgrc_route_arbitration_policy": (
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
                ),
            },
        )
        for modes in bad_modes:
            with self.subTest(modes=modes):
                with self.assertRaises(InvalidParamsError):
                    validate_lgrc9v3_causal_modes(modes)

    def test_native_route_candidate_record_round_trips(self) -> None:
        record = _valid_native_route_candidate_record()
        artifact = record.to_artifact()
        restored = restore_lgrc9v3_native_route_candidate_record_artifact(
            json.loads(json.dumps(artifact))
        )

        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(record, restored)
        self.assertEqual(
            artifact["candidate_route_digest"],
            build_lgrc9v3_native_route_candidate_record_digest(
                record.to_artifact(include_digest=False)
            ),
        )

    def test_native_route_candidate_set_record_round_trips(self) -> None:
        record = _valid_native_route_candidate_set_record()
        artifact = record.to_artifact()
        restored = restore_lgrc9v3_native_route_candidate_set_record_artifact(
            json.loads(json.dumps(artifact))
        )

        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(record, restored)
        self.assertEqual(
            artifact["candidate_set_digest"],
            build_lgrc9v3_native_route_candidate_set_record_digest(
                record.to_artifact(include_digest=False)
            ),
        )

    def test_native_route_arbitration_record_round_trips(self) -> None:
        record = _valid_native_route_arbitration_record()
        artifact = record.to_artifact()
        restored = restore_lgrc9v3_native_route_arbitration_record_artifact(
            json.loads(json.dumps(artifact))
        )

        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(record, restored)
        self.assertEqual(
            artifact["native_route_arbitration_digest"],
            build_lgrc9v3_native_route_arbitration_record_digest(
                record.to_artifact(include_digest=False)
            ),
        )

    def test_native_route_arbitration_digests_are_stable_and_sensitive(
        self,
    ) -> None:
        candidate = _valid_native_route_candidate_record()
        same_candidate = _valid_native_route_candidate_record()
        changed_candidate = _valid_native_route_candidate_record(
            candidate_score_components={
                "surface_polarity": 0.5,
                "local_preference": 0.25,
            },
            candidate_route_score=0.75,
        )
        candidate_set = _valid_native_route_candidate_set_record()
        same_candidate_set = _valid_native_route_candidate_set_record()
        changed_candidate_set = _valid_native_route_candidate_set_record(
            arbitration_window_id="window-2"
        )
        arbitration = _valid_native_route_arbitration_record()
        same_arbitration = _valid_native_route_arbitration_record()
        changed_arbitration = _valid_native_route_arbitration_record(
            arbitration_score=1.5
        )

        self.assertEqual(
            candidate.candidate_route_digest,
            same_candidate.candidate_route_digest,
        )
        self.assertNotEqual(
            candidate.candidate_route_digest,
            changed_candidate.candidate_route_digest,
        )
        self.assertEqual(
            candidate_set.candidate_set_digest,
            same_candidate_set.candidate_set_digest,
        )
        self.assertEqual(candidate_set.idempotency_key, same_candidate_set.idempotency_key)
        self.assertNotEqual(
            candidate_set.candidate_set_digest,
            changed_candidate_set.candidate_set_digest,
        )
        self.assertNotEqual(
            candidate_set.idempotency_key,
            changed_candidate_set.idempotency_key,
        )
        self.assertEqual(
            arbitration.native_route_arbitration_digest,
            same_arbitration.native_route_arbitration_digest,
        )
        self.assertEqual(arbitration.idempotency_key, same_arbitration.idempotency_key)
        self.assertNotEqual(
            arbitration.native_route_arbitration_digest,
            changed_arbitration.native_route_arbitration_digest,
        )

    def test_native_route_candidate_schema_rejects_bad_inputs(self) -> None:
        bad_cases = (
            {"native_route_arbitration_enabled": False},
            {
                "native_route_arbitration_policy_id": (
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED
                )
            },
            {"lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2},
            {"candidate_runtime_visible_inputs": ("hidden_fixture_array",)},
            {"candidate_score_components": {"hidden_fixture_array": 1.0}},
            {"candidate_route_score": 2.0},
            {
                "candidate_budget_prediction": {
                    "node_plus_packet_budget_before": 6.0,
                    "node_plus_packet_budget_after": 5.9,
                    "node_plus_packet_budget_error": 0.0,
                }
            },
            {"candidate_lineage_transfer_map": {"4": "10"}},
            {"claim_flags": {"movement_claim_allowed": True}},
        )
        for overrides in bad_cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    _valid_native_route_candidate_record(**overrides)

    def test_native_route_candidate_set_schema_rejects_bad_inputs(self) -> None:
        with self.assertRaises(ValueError):
            _valid_native_route_candidate_set_record(
                candidate_route_digests=("digest-a", "digest-a")
            )
        with self.assertRaises(ValueError):
            _valid_native_route_candidate_set_record(
                claim_flags={"movement_claim_allowed": True}
            )
        with self.assertRaises(ValueError):
            _valid_native_route_candidate_set_record(
                candidate_set_order_key="undeclared_order_policy"
            )
        with self.assertRaises(ValueError):
            _valid_native_route_candidate_set_record(
                unresolved_tie_policy="select_first_by_accident"
            )
        with self.assertRaises(ValueError):
            _valid_native_route_candidate_set_record(
                candidate_set_order_key=(
                    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING
                ),
                candidate_route_digests=("z-digest", "a-digest"),
            )
        digest_ordered = _valid_native_route_candidate_set_record(
            candidate_set_order_key=(
                LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING
            ),
            candidate_route_digests=("a-digest", "z-digest"),
        )
        self.assertEqual(
            ("a-digest", "z-digest"),
            tuple(digest_ordered.candidate_route_digests),
        )

    def test_native_route_arbitration_schema_rejects_bad_inputs(self) -> None:
        bad_cases = (
            {
                "arbitration_reason_code": (
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES
                )
            },
            {"arbitration_runtime_visible_inputs": ("experiment_if_else",)},
            {"rejected_candidate_route_digests": ("same", "same")},
            {"rejected_candidate_route_digests": (_valid_native_route_candidate_record().candidate_route_digest,)},
            {"claim_flags": {"movement_claim_allowed": True}},
            {"claim_flags": {"semantic_choice_claim_allowed": True}},
            {"claim_flags": {"rc_identity_collapse_claim_allowed": True}},
        )
        for overrides in bad_cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    _valid_native_route_arbitration_record(**overrides)

    def test_timing_field_names_are_stable_and_distinct(self) -> None:
        fields = LGRC9V3_TIMING_FIELD_NAMES

        self.assertIsInstance(fields, LGRC9V3TimingFieldNames)
        self.assertEqual("scheduler_event_index", fields.scheduler_event_index)
        self.assertEqual("checkpoint_index", fields.checkpoint_index)
        self.assertEqual("event_time_key", fields.event_time_key)
        self.assertEqual("node_proper_time", fields.node_proper_time)
        self.assertEqual("edge_causal_delay", fields.edge_causal_delay)
        self.assertEqual("kappa", LGRC9V3_TIMING_ALIASES["scheduler_event_index"])
        self.assertEqual("k", LGRC9V3_TIMING_ALIASES["checkpoint_index"])
        self.assertEqual("T_e", LGRC9V3_TIMING_ALIASES["event_time_key"])
        self.assertEqual("tau_i", LGRC9V3_TIMING_ALIASES["node_proper_time"])
        self.assertEqual("tau_ij", LGRC9V3_TIMING_ALIASES["edge_causal_delay"])

        serialized_names = {
            fields.scheduler_event_index,
            fields.checkpoint_index,
            fields.event_time_key,
            fields.node_proper_time,
            fields.edge_causal_delay,
        }
        self.assertEqual(5, len(serialized_names))

    def test_default_causal_modes_are_lgrc0_annotation(self) -> None:
        modes = validate_lgrc9v3_causal_modes()

        self.assertEqual(LGRC9V3_DEFAULT_CAUSAL_MODES, modes)
        self.assertEqual("causal_history", LGRC9V3_CAUSAL_MODES_KEY)
        self.assertEqual("causal_history", LGRC9V3_CAUSAL_ARTIFACT_KEY)
        self.assertEqual("annotation", modes["causal_layer_mode"])
        self.assertEqual("lgrc0", modes["lgrc_runtime_level"])
        self.assertEqual("annotation", modes["proper_time_accumulation_policy"])
        self.assertTrue(modes["require_fixed_topology_for_lgrc2"])
        self.assertEqual(
            "derived_from_synchronous_step",
            modes["event_time_policy"],
        )

    def test_lgrc1_semicausal_fixed_topology_config_is_accepted(self) -> None:
        modes = validate_lgrc9v3_causal_modes(
            {
                "causal_layer_mode": "fixed_topology_semicausal",
                "lgrc_runtime_level": "lgrc1",
                "event_time_policy": "explicit_event_time_key",
                "proper_time_accumulation_policy": "global_scheduler",
                "edge_delay_policy": "grcv3_temporal_label",
                "require_fixed_topology_for_lgrc1": True,
            }
        )

        self.assertEqual("fixed_topology_semicausal", modes["causal_layer_mode"])
        self.assertEqual("lgrc1", modes["lgrc_runtime_level"])
        self.assertEqual(
            "global_scheduler",
            modes["proper_time_accumulation_policy"],
        )
        self.assertTrue(modes["require_fixed_topology_for_lgrc1"])

    def test_lgrc2_packetized_fixed_topology_config_is_accepted(self) -> None:
        modes = validate_lgrc9v3_causal_modes(
            {
                "causal_layer_mode": "packetized_fixed_topology",
                "lgrc_runtime_level": "lgrc2",
                "event_time_policy": "explicit_event_time_key",
                "proper_time_accumulation_policy": "local_event_frontier",
                "edge_delay_policy": "grcv3_temporal_label",
                "require_fixed_topology_for_lgrc2": True,
            }
        )

        self.assertEqual("packetized_fixed_topology", modes["causal_layer_mode"])
        self.assertEqual("lgrc2", modes["lgrc_runtime_level"])
        self.assertEqual(
            "local_event_frontier",
            modes["proper_time_accumulation_policy"],
        )
        self.assertTrue(modes["require_fixed_topology_for_lgrc2"])

    def test_ambiguous_causal_mode_combinations_are_rejected(self) -> None:
        invalid_modes = (
            {"unknown_policy": "x"},
            {"causal_layer_mode": "fixed_topology_semicausal"},
            {
                "lgrc_runtime_level": "lgrc1",
                "causal_layer_mode": "annotation",
                "proper_time_accumulation_policy": "global_scheduler",
            },
            {
                "lgrc_runtime_level": "lgrc1",
                "causal_layer_mode": "fixed_topology_semicausal",
                "proper_time_accumulation_policy": "annotation",
            },
            {
                "lgrc_runtime_level": "lgrc1",
                "causal_layer_mode": "fixed_topology_semicausal",
                "proper_time_accumulation_policy": "global_scheduler",
                "require_fixed_topology_for_lgrc1": False,
            },
            {"edge_delay_policy": "directed_delay"},
            {"require_fixed_topology_for_lgrc1": "yes"},
            {"require_fixed_topology_for_lgrc2": "yes"},
            {
                "lgrc_runtime_level": "lgrc2",
                "causal_layer_mode": "fixed_topology_semicausal",
                "proper_time_accumulation_policy": "local_event_frontier",
            },
            {
                "lgrc_runtime_level": "lgrc2",
                "causal_layer_mode": "packetized_fixed_topology",
                "proper_time_accumulation_policy": "annotation",
            },
            {
                "lgrc_runtime_level": "lgrc2",
                "causal_layer_mode": "packetized_fixed_topology",
                "proper_time_accumulation_policy": "local_event_frontier",
                "require_fixed_topology_for_lgrc2": False,
            },
        )

        for modes in invalid_modes:
            with self.subTest(modes=modes):
                with self.assertRaises(InvalidParamsError):
                    validate_lgrc9v3_causal_modes(modes)

    def test_existing_grc9v3_default_does_not_claim_causal_layer(self) -> None:
        model = GRC9V3.from_config({"dt": 0.1})

        self.assertNotIn(CAUSAL_LAYER, model.list_capabilities())
        self.assertNotIn(
            LGRC9V3_CAUSAL_MODES_KEY,
            dict(model.get_params().constitutive_semantic_modes),
        )

    def test_lgrc2_packet_contract_names_are_stable(self) -> None:
        packet_fields = LGRC9V3_PACKET_FIELD_NAMES
        ledger_fields = LGRC9V3_PACKET_LEDGER_FIELD_NAMES

        self.assertEqual("packet_id", packet_fields.packet_id)
        self.assertEqual("packet_state", packet_fields.packet_state)
        self.assertEqual("source_node_id", packet_fields.source_node_id)
        self.assertEqual("target_node_id", packet_fields.target_node_id)
        self.assertEqual("edge_id", packet_fields.edge_id)
        self.assertEqual("amount", packet_fields.amount)
        self.assertEqual(
            "departure_event_time_key",
            packet_fields.departure_event_time_key,
        )
        self.assertEqual("arrival_event_time_key", packet_fields.arrival_event_time_key)
        self.assertEqual("packet_records", ledger_fields.packet_records)
        self.assertEqual("packet_event_records", ledger_fields.packet_event_records)
        self.assertEqual(
            "event_queue_tie_break_policy",
            ledger_fields.event_queue_tie_break_policy,
        )
        self.assertEqual(
            "sum_node_coherence_plus_packets",
            LGRC9V3_PACKET_BUDGET_INVARIANT,
        )
        self.assertEqual(
            "event_time_key_then_scheduler_event_index_then_event_id",
            LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY,
        )
        self.assertIn(LGRC9V3_PACKET_STATE_SCHEDULED, LGRC9V3_PACKET_STATES)
        self.assertIn(LGRC9V3_PACKET_STATE_IN_FLIGHT, LGRC9V3_PACKET_STATES)
        self.assertIn(LGRC9V3_PACKET_STATE_ARRIVED, LGRC9V3_PACKET_STATES)
        self.assertEqual(
            {
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            },
            set(LGRC9V3_PACKET_EVENT_KINDS),
        )
        self.assertTrue(
            {
                "packet_id",
                "packet_state",
                "source_node_id",
                "target_node_id",
                "edge_id",
                "amount",
                "departure_event_time_key",
                "arrival_event_time_key",
            }.issubset(LGRC9V3_PACKET_REQUIRED_FIELDS)
        )

    def test_lgrc2_packet_contract_artifact_is_boundary_explicit(self) -> None:
        artifact = build_lgrc9v3_packet_contract_artifact()
        round_tripped = json.loads(json.dumps(artifact, sort_keys=True))

        self.assertEqual(artifact, round_tripped)
        self.assertEqual(LGRC9V3_LGRC2_PACKET_CONTRACT_KIND, artifact["artifact_kind"])
        self.assertEqual(
            LGRC9V3_LGRC2_PACKET_CONTRACT_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(LGRC9V3_LGRC2_MODE_VERSION, artifact["mode_version"])
        self.assertEqual(LGRC9V3_PACKETIZED_EVIDENCE_CLASS, artifact["evidence_class"])
        self.assertEqual("packetized_fixed_topology", artifact["causal_layer_mode"])
        self.assertEqual("lgrc2", artifact["lgrc_runtime_level"])
        self.assertTrue(artifact["packetized_flux"])
        self.assertTrue(artifact["fixed_topology"])
        self.assertFalse(artifact["topology_change_allowed"])
        self.assertFalse(artifact["packet_transport_through_topology_change"])
        self.assertFalse(artifact["identity_acceptance_allowed"])
        self.assertFalse(artifact["collapse_allowed"])
        self.assertEqual(
            LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY,
            artifact["event_queue_tie_break_policy"],
        )
        self.assertEqual(
            LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_DELAY_DERIVED,
            artifact["normal_arrival_event_time_key_policy"],
        )
        self.assertEqual(
            LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_EXPLICIT,
            artifact["explicit_arrival_event_time_key_policy"],
        )
        self.assertEqual(
            LGRC9V3_PACKET_BUDGET_INVARIANT,
            artifact["packet_budget_invariant"],
        )
        self.assertEqual(
            sorted(LGRC9V3_PACKET_EVENT_KINDS),
            artifact["packet_event_kinds"],
        )
        self.assertEqual(sorted(LGRC9V3_PACKET_STATES), artifact["packet_states"])
        self.assertEqual(
            sorted(LGRC9V3_PACKET_REQUIRED_FIELDS),
            artifact["packet_required_fields"],
        )

    def test_lgrc3_topology_contract_artifact_is_boundary_explicit(self) -> None:
        artifact = build_lgrc9v3_topology_contract_artifact()
        round_tripped = json.loads(json.dumps(artifact, sort_keys=True))

        self.assertEqual(artifact, round_tripped)
        self.assertEqual(LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_KIND, artifact["artifact_kind"])
        self.assertEqual(
            LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(LGRC9V3_LGRC3_MODE_VERSION, artifact["mode_version"])
        self.assertEqual(LGRC9V3_TOPOLOGY_CONTRACT_EVIDENCE_CLASS, artifact["evidence_class"])
        self.assertEqual("topology_changing_causal_history", artifact["causal_layer_mode"])
        self.assertEqual("lgrc3", artifact["lgrc_runtime_level"])
        self.assertTrue(artifact["contract_only"])
        self.assertTrue(artifact["topology_change_contract_defined"])
        self.assertFalse(artifact["topology_change_processing_implemented"])
        self.assertFalse(
            artifact["packet_transport_through_topology_change_implemented"]
        )
        self.assertFalse(artifact["collapse_reabsorption_in_scope"])
        self.assertFalse(artifact["proper_time_identity_in_scope"])
        self.assertTrue(artifact["builds_on_lgrc2_packet_accounting"])
        self.assertTrue(artifact["builds_on_pending_flux_compaction"])
        self.assertEqual(
            LGRC9V3_PACKET_BUDGET_INVARIANT,
            artifact["source_packet_budget_invariant"],
        )
        self.assertEqual(
            LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT,
            artifact["source_pending_flux_compaction_policy"],
        )
        self.assertEqual(
            sorted(LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_IN_SCOPE),
            artifact["topology_event_kinds_in_scope"],
        )
        self.assertEqual(
            sorted(LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_OUT_OF_SCOPE),
            artifact["topology_event_kinds_out_of_scope"],
        )
        self.assertIn(
            LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT,
            artifact["topology_event_kinds_in_scope"],
        )
        self.assertIn(
            LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
            artifact["topology_event_kinds_in_scope"],
        )
        self.assertIn(
            LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            artifact["topology_event_kinds_in_scope"],
        )
        self.assertIn(
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            artifact["topology_event_kinds_out_of_scope"],
        )
        self.assertIn(
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            artifact["topology_event_kinds_out_of_scope"],
        )
        self.assertIn(
            LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
            artifact["topology_event_kinds_out_of_scope"],
        )
        self.assertEqual(
            LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT,
            artifact["proper_time_inheritance_policy"],
        )
        self.assertEqual(
            LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0,
            artifact["internal_edge_delay_policy"],
        )
        self.assertTrue(artifact["collapse_reabsorption_policy_defined"])
        self.assertTrue(artifact["proper_time_identity_policy_defined"])
        self.assertEqual(
            LGRC9V3_LGRC3_POLICY_CONTRACT_KIND,
            artifact["collapse_identity_policy_contract_kind"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION,
            artifact["collapse_identity_policy_contract_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL,
            artifact["identity_clock_policy"],
        )

    def test_lgrc3_topology_contract_names_required_audit_fields(self) -> None:
        artifact = build_lgrc9v3_topology_contract_artifact()
        fields = LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES

        self.assertEqual("refinement_lineage_map", fields.refinement_lineage_map)
        self.assertEqual("packet_transport_records", fields.packet_transport_records)
        self.assertEqual(
            "proper_time_inheritance_records",
            fields.proper_time_inheritance_records,
        )
        self.assertEqual(
            sorted(LGRC9V3_REFINEMENT_LINEAGE_REQUIRED_FIELDS),
            artifact["refinement_lineage_required_fields"],
        )
        self.assertEqual(
            sorted(LGRC9V3_PACKET_TRANSPORT_REQUIRED_FIELDS),
            artifact["packet_transport_required_fields"],
        )
        self.assertEqual(
            sorted(LGRC9V3_PROPER_TIME_INHERITANCE_REQUIRED_FIELDS),
            artifact["proper_time_inheritance_required_fields"],
        )
        self.assertIn(
            fields.boundary_reassignment_map,
            artifact["refinement_lineage_required_fields"],
        )
        self.assertIn(
            fields.identity_acceptance_emitted,
            artifact["packet_transport_required_fields"],
        )
        self.assertEqual(
            sorted(LGRC9V3_COLLAPSE_REABSORPTION_REQUIRED_FIELDS),
            artifact["collapse_reabsorption_required_fields"],
        )
        self.assertEqual(
            sorted(LGRC9V3_PROPER_TIME_IDENTITY_REQUIRED_FIELDS),
            artifact["proper_time_identity_required_fields"],
        )

    def test_lgrc3_policy_contract_defaults_disable_collapse_and_identity(self) -> None:
        artifact = build_lgrc9v3_lgrc3_policy_contract_artifact()

        self.assertEqual(
            LGRC9V3_LGRC3_POLICY_CONTRACT_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_POLICY_CONTRACT_EVIDENCE_CLASS,
            artifact["evidence_class"],
        )
        self.assertTrue(artifact["contract_only"])
        self.assertFalse(artifact["collapse_reabsorption_allowed"])
        self.assertFalse(artifact["identity_acceptance_allowed"])
        self.assertFalse(artifact["collapse_reabsorption_processing_implemented"])
        self.assertFalse(artifact["proper_time_identity_processing_implemented"])
        self.assertFalse(artifact["mechanical_expansion_is_identity_acceptance"])
        self.assertFalse(artifact["refinement_packet_transport_is_identity_transfer"])
        self.assertEqual(
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            artifact["collapse_event_kind"],
        )
        self.assertEqual(
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            artifact["reabsorption_event_kind"],
        )
        self.assertEqual(
            LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
            artifact["identity_acceptance_event_kind"],
        )
        self.assertEqual(
            LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY,
            artifact["proper_time_transfer_policy"],
        )
        self.assertEqual(
            LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP,
            artifact["lineage_transfer_policy"],
        )
        self.assertEqual(
            LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING,
            artifact["budget_transfer_policy"],
        )
        self.assertEqual(
            LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL,
            artifact["identity_clock_policy"],
        )
        self.assertEqual(
            LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY,
            artifact["identity_threshold_calibration_policy"],
        )
        self.assertEqual(
            LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER,
            artifact["identity_threshold_multiplier"],
        )

    def test_lgrc3_policy_contract_round_trips_budget_and_lineage_fields(self) -> None:
        artifact = build_lgrc9v3_lgrc3_policy_contract_artifact()
        round_tripped = json.loads(json.dumps(artifact, sort_keys=True))
        restored = restore_lgrc9v3_lgrc3_policy_contract_artifact(round_tripped)

        self.assertIsNotNone(restored)
        self.assertEqual(artifact, restored.to_artifact())
        self.assertIn(
            "lineage_transfer_map",
            artifact["collapse_reabsorption_required_fields"],
        )
        self.assertIn(
            "budget_before",
            artifact["collapse_reabsorption_required_fields"],
        )
        self.assertIn(
            "budget_after",
            artifact["collapse_reabsorption_required_fields"],
        )
        self.assertIn(
            "budget_error",
            artifact["collapse_reabsorption_required_fields"],
        )
        self.assertIn(
            "proper_time_transfer_policy",
            artifact["collapse_reabsorption_required_fields"],
        )
        self.assertIn(
            "identity_clock_policy",
            artifact["proper_time_identity_required_fields"],
        )
        self.assertIn(
            "proper_time_persistence_threshold",
            artifact["proper_time_identity_required_fields"],
        )
        self.assertIn(
            "local_median_edge_delay",
            artifact["proper_time_identity_required_fields"],
        )

    def test_lgrc3_policy_contract_rejects_unknown_policy(self) -> None:
        with self.assertRaises(ValueError):
            build_lgrc9v3_lgrc3_policy_contract_artifact(
                identity_clock_policy="global_observer_clock",
            )

        artifact = build_lgrc9v3_lgrc3_policy_contract_artifact()
        mutated = json.loads(json.dumps(artifact, sort_keys=True))
        mutated["mechanical_expansion_is_identity_acceptance"] = True
        with self.assertRaises(SnapshotCompatibilityError):
            restore_lgrc9v3_lgrc3_policy_contract_artifact(mutated)

    def test_lgrc3_runtime_mode_requires_operational_proper_time(self) -> None:
        with self.assertRaisesRegex(
            InvalidParamsError,
            "proper-time",
        ):
            validate_lgrc9v3_causal_modes(
                {
                    "causal_layer_mode": "topology_changing_causal_history",
                    "lgrc_runtime_level": "lgrc3",
                }
            )

        resolved = validate_lgrc9v3_causal_modes(
            {
                "causal_layer_mode": "topology_changing_causal_history",
                "lgrc_runtime_level": "lgrc3",
                "proper_time_accumulation_policy": "local_event_frontier",
            }
        )
        self.assertEqual("lgrc3", resolved["lgrc_runtime_level"])
        self.assertFalse(resolved["causal_boundary_birth_allowed"])

    def test_lgrc3_proper_time_inheritance_uses_parent_event_clock(self) -> None:
        result = process_lgrc9v3_proper_time_inheritance(
            _fake_refinement_expansion_event(),
            parent_node_proper_time={0: 7.5, 1: 2.0},
            explicit_internal_edge_delay={10: 0.25},
            tau_0=1.5,
            scheduler_event_index=12,
            checkpoint_index=4,
            event_time_key=9.25,
        )
        artifact = result.to_artifact()

        self.assertIsInstance(result, LGRC9V3ProperTimeInheritanceResult)
        self.assertEqual(
            LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            artifact["topology_event_kind"],
        )
        self.assertEqual(
            LGRC9V3_PROPER_TIME_INHERITANCE_EVIDENCE_CLASS,
            artifact["evidence_class"],
        )
        self.assertEqual(12, artifact["scheduler_event_index"])
        self.assertEqual(4, artifact["checkpoint_index"])
        self.assertEqual(9.25, artifact["event_time_key"])
        self.assertEqual(7.5, artifact["parent_proper_time"])
        self.assertEqual({"3": 7.5, "4": 7.5, "5": 7.5, "6": 7.5}, artifact["child_proper_time"])
        self.assertEqual({"10": 0.25, "11": 1.5, "12": 1.5}, artifact["internal_edge_delay"])
        self.assertEqual(
            LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT,
            artifact["proper_time_inheritance_policy"],
        )
        self.assertEqual(
            LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0,
            artifact["internal_edge_delay_policy"],
        )
        self.assertFalse(artifact["identity_acceptance_emitted"])
        self.assertFalse(artifact["refinement_lineage_identity_persistence"])
        self.assertFalse(artifact["state_mutated"])
        self.assertFalse(artifact["topology_mutated"])
        self.assertEqual(4, len(artifact["proper_time_inheritance_records"]))
        self.assertTrue(
            all(
                record["child_proper_time"] == record["parent_proper_time"] == 7.5
                for record in artifact["proper_time_inheritance_records"]
            )
        )

    def test_lgrc3_proper_time_inheritance_round_trips_through_json(self) -> None:
        result = process_lgrc9v3_proper_time_inheritance(
            _fake_refinement_expansion_event(),
            parent_node_proper_time={0: 6.0},
            tau_0=2.0,
        )
        round_tripped = json.loads(json.dumps(result.to_artifact(), sort_keys=True))
        restored = restore_lgrc9v3_proper_time_inheritance_artifact(round_tripped)

        self.assertIsNotNone(restored)
        self.assertEqual(result, restored)
        assert restored is not None
        self.assertEqual((3, 4, 5, 6), restored.replacement_node_ids)
        self.assertEqual((10, 11, 12), restored.internal_edge_ids)
        self.assertEqual({10: 2.0, 11: 2.0, 12: 2.0}, restored.internal_edge_delay)
        self.assertFalse(restored.identity_acceptance_emitted)

    def test_lgrc3_proper_time_inheritance_rejects_missing_parent_clock(self) -> None:
        with self.assertRaisesRegex(InvalidStateTransitionError, "proper-time surface"):
            process_lgrc9v3_proper_time_inheritance(
                _fake_refinement_expansion_event(),
                parent_node_proper_time={1: 7.5},
            )

    def test_lgrc3_proper_time_inheritance_rejects_unknown_internal_edge_delay(self) -> None:
        with self.assertRaisesRegex(InvalidStateTransitionError, "unknown edges"):
            process_lgrc9v3_proper_time_inheritance(
                _fake_refinement_expansion_event(),
                parent_node_proper_time={0: 7.5},
                explicit_internal_edge_delay={99: 0.5},
            )

    def test_lgrc3_collapse_reabsorption_records_budget_lineage_and_ledgers(self) -> None:
        state = _three_node_state()
        departure = process_lgrc9v3_packet_departure(
            state,
            build_lgrc9v3_packet_ledger(state=state),
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=1,
            source_lineage_id="sink-0",
            target_lineage_id="node-1",
        )
        compact = compact_lgrc9v3_packet_ledger(departure.ledger)

        result = process_lgrc9v3_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=(0, 2),
            selected_sink_id=2,
            losing_sink_ids=(0,),
            transferred_node_ids=(0, 1),
            lineage_transfer_map={0: "sink-2", 1: "sink-2"},
            source_lineage_ids={0: "sink-0", 1: "node-1"},
            target_lineage_id="sink-2",
            node_proper_time={0: 4.0, 1: 5.0, 2: 9.0},
            coherence_transfer_amount=1.5,
            budget_before=departure.ledger.conserved_budget_total,
            event_time_key=8.0,
            scheduler_event_index=6,
            checkpoint_index=3,
            packet_ledger=departure.ledger,
            pending_flux_ledger=compact,
            collapse_reabsorption_allowed=True,
        )
        artifact = result.to_artifact()

        self.assertIsInstance(result, LGRC9V3CollapseReabsorptionResult)
        self.assertEqual(
            LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_COLLAPSE_REABSORPTION_EVIDENCE_CLASS,
            artifact["evidence_class"],
        )
        self.assertEqual(
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            artifact["topology_event_kind"],
        )
        self.assertEqual([0, 2], artifact["competing_sink_ids"])
        self.assertEqual(2, artifact["selected_sink_id"])
        self.assertEqual([0], artifact["losing_sink_ids"])
        self.assertEqual({"0": "sink-2", "1": "sink-2"}, artifact["lineage_transfer_map"])
        self.assertEqual({"0": "sink-0", "1": "node-1"}, artifact["source_lineage_ids"])
        self.assertEqual("sink-2", artifact["target_lineage_id"])
        self.assertEqual([0, 1], artifact["transferred_node_ids"])
        self.assertEqual(
            [departure.packet_record.packet_id],
            artifact["transferred_packet_ids"],
        )
        self.assertEqual(
            [compact.pending_flux_entries[0].entry_id],
            artifact["transferred_pending_flux_entry_ids"],
        )
        self.assertEqual("lgrc9v3_packet_ledger_v1", artifact["source_packet_ledger_schema_version"])
        self.assertEqual(
            "lgrc9v3_pending_flux_ledger_v1",
            artifact["source_pending_flux_ledger_schema_version"],
        )
        self.assertAlmostEqual(departure.ledger.conserved_budget_total, artifact["budget_before"])
        self.assertAlmostEqual(artifact["budget_before"], artifact["budget_after"])
        self.assertAlmostEqual(0.0, artifact["budget_error"])
        self.assertEqual(
            LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING,
            artifact["budget_transfer_policy"],
        )
        self.assertEqual(
            LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP,
            artifact["lineage_transfer_policy"],
        )
        self.assertEqual(
            LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY,
            artifact["proper_time_transfer_policy"],
        )
        self.assertTrue(artifact["collapse_reabsorption_allowed"])
        self.assertTrue(artifact["collapse_reabsorption_processing_implemented"])
        self.assertFalse(artifact["identity_acceptance_emitted"])
        self.assertFalse(artifact["packet_transport_emitted"])

    def test_lgrc3_reabsorption_event_round_trips_through_json(self) -> None:
        result = process_lgrc9v3_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            competing_sink_ids=(1, 2),
            selected_sink_id=2,
            losing_sink_ids=(1,),
            transferred_node_ids=(1,),
            lineage_transfer_map={1: "sink-2"},
            source_lineage_ids={1: "sink-1"},
            target_lineage_id="sink-2",
            node_proper_time={1: 4.0, 2: 7.0},
            coherence_transfer_amount=0.5,
            budget_before=6.0,
            event_time_key=9.0,
            scheduler_event_index=5,
            checkpoint_index=2,
            collapse_reabsorption_allowed=True,
        )
        restored = restore_lgrc9v3_collapse_reabsorption_artifact(
            json.loads(json.dumps(result.to_artifact(), sort_keys=True))
        )

        self.assertEqual(result, restored)
        assert restored is not None
        self.assertEqual(
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            restored.topology_event_kind,
        )
        self.assertEqual((), restored.transferred_packet_ids)
        self.assertFalse(restored.identity_acceptance_emitted)

    def test_lgrc3_collapse_reabsorption_requires_explicit_policy_enablement(self) -> None:
        with self.assertRaisesRegex(InvalidParamsError, "explicit policy"):
            process_lgrc9v3_collapse_reabsorption(
                topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                competing_sink_ids=(0, 2),
                selected_sink_id=2,
                losing_sink_ids=(0,),
                transferred_node_ids=(0,),
                lineage_transfer_map={0: "sink-2"},
                source_lineage_ids={0: "sink-0"},
                target_lineage_id="sink-2",
                node_proper_time={0: 4.0, 2: 9.0},
                coherence_transfer_amount=1.0,
                budget_before=6.0,
                event_time_key=8.0,
                scheduler_event_index=6,
                checkpoint_index=3,
            )

    def test_lgrc3_collapse_reabsorption_requires_complete_lineage_map(self) -> None:
        with self.assertRaisesRegex(ValueError, "lineage_transfer_map"):
            process_lgrc9v3_collapse_reabsorption(
                topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                competing_sink_ids=(0, 2),
                selected_sink_id=2,
                losing_sink_ids=(0,),
                transferred_node_ids=(0, 1),
                lineage_transfer_map={0: "sink-2"},
                source_lineage_ids={0: "sink-0", 1: "node-1"},
                target_lineage_id="sink-2",
                node_proper_time={0: 4.0, 2: 9.0},
                coherence_transfer_amount=1.0,
                budget_before=6.0,
                event_time_key=8.0,
                scheduler_event_index=6,
                checkpoint_index=3,
                collapse_reabsorption_allowed=True,
            )

    def test_lgrc3_collapse_packet_transport_redirects_and_settles_packets(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        first = process_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=1,
            packet_index=0,
            source_lineage_id="sink-0",
            target_lineage_id="node-1",
        )
        second = process_lgrc9v3_packet_departure(
            state,
            first.ledger,
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            amount=0.5,
            departure_event_time_key=1.5,
            arrival_event_time_key=4.0,
            scheduler_event_index=2,
            packet_index=1,
            source_lineage_id="sink-0",
            target_lineage_id="sink-2",
        )
        compact = compact_lgrc9v3_packet_ledger(second.ledger)
        collapse = process_lgrc9v3_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=(0, 2),
            selected_sink_id=2,
            losing_sink_ids=(0,),
            transferred_node_ids=(0,),
            lineage_transfer_map={0: "sink-2"},
            source_lineage_ids={0: "sink-0"},
            target_lineage_id="sink-2",
            node_proper_time={0: 4.0, 2: 9.0},
            coherence_transfer_amount=1.0,
            budget_before=second.ledger.conserved_budget_total,
            event_time_key=8.0,
            scheduler_event_index=6,
            checkpoint_index=3,
            packet_ledger=second.ledger,
            pending_flux_ledger=compact,
            collapse_reabsorption_allowed=True,
        )

        transport = transport_lgrc9v3_packets_through_collapse_reabsorption(
            second.ledger,
            collapse,
            pending_flux_ledger=compact,
        )
        artifact = transport.to_artifact()

        self.assertIsInstance(transport, LGRC9V3CollapsePacketTransportResult)
        self.assertEqual(
            LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS,
            artifact["evidence_class"],
        )
        self.assertEqual(
            LGRC9V3_COLLAPSE_PACKET_TRANSPORT_POLICY_REDIRECT_OR_SETTLE,
            artifact["transport_policy"],
        )
        self.assertEqual(
            {first.packet_record.packet_id, second.packet_record.packet_id},
            set(artifact["source_packet_ids"]),
        )
        self.assertEqual([first.packet_record.packet_id], artifact["transported_packet_ids"])
        self.assertEqual([second.packet_record.packet_id], artifact["settled_packet_ids"])
        self.assertAlmostEqual(0.75, artifact["amount_total"])
        self.assertAlmostEqual(0.5, artifact["settled_amount_total"])
        self.assertAlmostEqual(second.ledger.conserved_budget_total, artifact["budget_before"])
        self.assertAlmostEqual(artifact["budget_before"], artifact["budget_after"])
        self.assertAlmostEqual(0.0, artifact["budget_error"])
        self.assertFalse(artifact["identity_acceptance_emitted"])
        self.assertFalse(artifact["packet_transport_identity_transfer"])

        transported_ledger = transport.transported_ledger
        self.assertEqual(second.ledger.packet_event_records, transported_ledger.packet_event_records)
        self.assertAlmostEqual(0.25, transported_ledger.in_flight_packet_total)
        self.assertAlmostEqual(
            second.ledger.node_coherence_total + 0.5,
            transported_ledger.node_coherence_total,
        )
        queued = transported_ledger.event_queue_records
        self.assertEqual(1, len(queued))
        self.assertEqual(first.packet_record.packet_id, queued[0].packet_id)
        self.assertEqual(2, queued[0].source_node_id)
        self.assertEqual(1, queued[0].target_node_id)
        settled_packet = [
            packet
            for packet in transported_ledger.packet_records
            if packet.packet_id == second.packet_record.packet_id
        ][0]
        self.assertEqual(LGRC9V3_PACKET_STATE_ARRIVED, settled_packet.packet_state)
        self.assertEqual(2, settled_packet.source_node_id)
        self.assertEqual(2, settled_packet.target_node_id)

        pending = transport.transported_pending_flux_ledger
        self.assertIsNotNone(pending)
        assert pending is not None
        self.assertAlmostEqual(0.25, pending.pending_flux_total)
        self.assertEqual(1, len(pending.pending_flux_entries))
        self.assertEqual(2, pending.pending_flux_entries[0].source_node_id)
        self.assertEqual(1, pending.pending_flux_entries[0].target_node_id)
        self.assertEqual(
            set(artifact["source_pending_flux_entry_ids"]),
            {
                compact.pending_flux_entries[0].entry_id,
                compact.pending_flux_entries[1].entry_id,
            },
        )
        self.assertEqual(1, len(artifact["transported_pending_flux_entry_ids"]))
        self.assertEqual(1, len(artifact["settled_pending_flux_entry_ids"]))

    def test_lgrc3_collapse_packet_transport_round_trips_json(self) -> None:
        state = _three_node_state()
        departure = process_lgrc9v3_packet_departure(
            state,
            build_lgrc9v3_packet_ledger(state=state),
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=1,
            source_lineage_id="sink-0",
            target_lineage_id="node-1",
        )
        collapse = process_lgrc9v3_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            competing_sink_ids=(0, 2),
            selected_sink_id=2,
            losing_sink_ids=(0,),
            transferred_node_ids=(0,),
            lineage_transfer_map={0: "sink-2"},
            source_lineage_ids={0: "sink-0"},
            target_lineage_id="sink-2",
            node_proper_time={0: 4.0, 2: 9.0},
            coherence_transfer_amount=1.0,
            budget_before=departure.ledger.conserved_budget_total,
            event_time_key=8.0,
            scheduler_event_index=6,
            checkpoint_index=3,
            packet_ledger=departure.ledger,
            collapse_reabsorption_allowed=True,
        )
        transport = transport_lgrc9v3_packets_through_collapse_reabsorption(
            departure.ledger,
            collapse,
        )
        restored = restore_lgrc9v3_collapse_packet_transport_artifact(
            json.loads(json.dumps(transport.to_artifact(), sort_keys=True))
        )

        self.assertEqual(transport, restored)
        assert restored is not None
        self.assertEqual(collapse.topology_event_id, restored.source_topology_event_id)
        self.assertEqual((departure.packet_record.packet_id,), restored.transported_packet_ids)

    def test_lgrc3_proper_time_identity_short_lived_refinement_fails(self) -> None:
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=("topology-1",),
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            sink_node_id=0,
            lineage_id="child-lineage",
            basin_node_ids=(0, 1, 2),
            node_proper_time={0: 7.0, 1: 6.5, 2: 6.0},
            window_start_sink_proper_time=0.0,
            window_start_event_time_key=1.0,
            window_end_event_time_key=9.0,
            scheduler_event_index=10,
            checkpoint_index=4,
            event_time_key=9.0,
            local_edge_delay={0: 2.0, 1: 2.0, 2: 4.0},
            budget_before=6.0,
        )
        artifact = evaluation.to_artifact()

        self.assertIsInstance(
            evaluation,
            LGRC9V3ProperTimeIdentityPersistenceEvaluation,
        )
        self.assertEqual(
            LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_PROPER_TIME_IDENTITY_EVALUATION_EVIDENCE_CLASS,
            artifact["evidence_class"],
        )
        self.assertEqual(
            LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            artifact["topology_event_kind"],
        )
        self.assertAlmostEqual(2.0, artifact["local_median_edge_delay"])
        self.assertAlmostEqual(
            LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER * 2.0,
            artifact["proper_time_persistence_threshold"],
        )
        self.assertAlmostEqual(7.0, artifact["observed_persistence_duration"])
        self.assertFalse(artifact["persistence_passed"])
        self.assertFalse(artifact["identity_acceptance_allowed"])
        self.assertFalse(artifact["identity_acceptance_emitted"])
        self.assertTrue(artifact["proper_time_identity_processing_implemented"])
        self.assertEqual(
            LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL,
            artifact["identity_clock_policy"],
        )
        self.assertEqual(
            LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY,
            artifact["threshold_calibration_policy"],
        )

    def test_lgrc3_proper_time_identity_persistent_basin_passes(self) -> None:
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=("topology-2", "topology-1"),
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            sink_node_id=2,
            lineage_id="sink-2-lineage",
            basin_node_ids=(2, 5),
            node_proper_time={2: 9.0, 5: 8.5},
            window_start_sink_proper_time=1.0,
            window_start_event_time_key=2.0,
            window_end_event_time_key=11.0,
            scheduler_event_index=12,
            checkpoint_index=5,
            event_time_key=11.0,
            local_median_edge_delay=2.0,
            source_basin_evidence_id="basin-core-2",
            budget_before=5.0,
            budget_after=5.0,
        )

        self.assertTrue(evaluation.persistence_passed)
        self.assertEqual("topology-1", evaluation.topology_event_id)
        self.assertEqual(("topology-1", "topology-2"), evaluation.source_topology_event_ids)
        self.assertEqual("basin-core-2", evaluation.source_basin_evidence_id)
        self.assertAlmostEqual(8.0, evaluation.observed_persistence_duration)
        self.assertAlmostEqual(8.0, evaluation.proper_time_persistence_threshold)
        self.assertFalse(evaluation.identity_acceptance_emitted)

    def test_lgrc3_proper_time_identity_evaluation_round_trips_json(self) -> None:
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=("topology-roundtrip",),
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            sink_node_id=0,
            lineage_id="lineage-roundtrip",
            basin_node_ids=(0, 1),
            node_proper_time={0: 8.0, 1: 7.5},
            window_start_sink_proper_time=0.0,
            window_start_event_time_key=1.0,
            window_end_event_time_key=9.0,
            scheduler_event_index=13,
            checkpoint_index=6,
            event_time_key=9.0,
            local_edge_delay=(2.0, 2.0, 4.0),
            budget_before=4.0,
        )
        restored = restore_lgrc9v3_proper_time_identity_evaluation_artifact(
            json.loads(json.dumps(evaluation.to_artifact(), sort_keys=True))
        )

        self.assertEqual(evaluation, restored)
        assert restored is not None
        self.assertFalse(restored.identity_acceptance_emitted)

    def test_lgrc3_proper_time_identity_requires_topology_and_basin_evidence(self) -> None:
        with self.assertRaisesRegex(InvalidStateTransitionError, "topology"):
            evaluate_lgrc9v3_proper_time_identity_persistence(
                source_topology_event_ids=(),
                topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
                sink_node_id=0,
                lineage_id="lineage",
                basin_node_ids=(0,),
                node_proper_time={0: 8.0},
                window_start_sink_proper_time=0.0,
                window_start_event_time_key=1.0,
                window_end_event_time_key=9.0,
                scheduler_event_index=13,
                checkpoint_index=6,
                event_time_key=9.0,
                local_median_edge_delay=2.0,
            )

        with self.assertRaisesRegex(InvalidStateTransitionError, "basin"):
            evaluate_lgrc9v3_proper_time_identity_persistence(
                source_topology_event_ids=("topology",),
                topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
                sink_node_id=0,
                lineage_id="lineage",
                basin_node_ids=(1,),
                node_proper_time={0: 8.0, 1: 8.0},
                window_start_sink_proper_time=0.0,
                window_start_event_time_key=1.0,
                window_end_event_time_key=9.0,
                scheduler_event_index=13,
                checkpoint_index=6,
                event_time_key=9.0,
                local_median_edge_delay=2.0,
            )

    def test_lgrc3_identity_acceptance_disabled_policy_prevents_emission(self) -> None:
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=("topology-pass-disabled",),
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            sink_node_id=0,
            lineage_id="lineage-pass-disabled",
            basin_node_ids=(0, 1),
            node_proper_time={0: 9.0, 1: 8.5},
            window_start_sink_proper_time=1.0,
            window_start_event_time_key=1.0,
            window_end_event_time_key=9.0,
            scheduler_event_index=14,
            checkpoint_index=6,
            event_time_key=9.0,
            local_median_edge_delay=2.0,
        )

        self.assertTrue(evaluation.persistence_passed)
        with self.assertRaisesRegex(InvalidParamsError, "identity acceptance"):
            emit_lgrc9v3_proper_time_identity_acceptance(evaluation)

    def test_lgrc3_identity_acceptance_failed_persistence_prevents_emission(self) -> None:
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=("topology-fail",),
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            sink_node_id=0,
            lineage_id="lineage-fail",
            basin_node_ids=(0, 1),
            node_proper_time={0: 3.0, 1: 3.0},
            window_start_sink_proper_time=0.0,
            window_start_event_time_key=1.0,
            window_end_event_time_key=4.0,
            scheduler_event_index=15,
            checkpoint_index=7,
            event_time_key=4.0,
            local_median_edge_delay=2.0,
        )

        self.assertFalse(evaluation.persistence_passed)
        with self.assertRaisesRegex(InvalidStateTransitionError, "passing"):
            emit_lgrc9v3_proper_time_identity_acceptance(
                evaluation,
                identity_acceptance_allowed=True,
            )

    def test_lgrc3_identity_acceptance_emits_one_event_after_passing_evaluation(self) -> None:
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=("topology-pass-2", "topology-pass-1"),
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            sink_node_id=2,
            lineage_id="accepted-lineage",
            basin_node_ids=(2, 5),
            node_proper_time={2: 10.0, 5: 9.0},
            window_start_sink_proper_time=1.0,
            window_start_event_time_key=2.0,
            window_end_event_time_key=12.0,
            scheduler_event_index=16,
            checkpoint_index=8,
            event_time_key=12.0,
            local_median_edge_delay=2.0,
            source_basin_evidence_id="basin-core-accepted",
            budget_before=5.0,
            budget_after=5.0,
        )

        event = emit_lgrc9v3_proper_time_identity_acceptance(
            evaluation,
            identity_acceptance_allowed=True,
        )
        events = [event]
        payload = event.payload

        self.assertEqual(1, len(events))
        self.assertEqual(LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE, event.kind)
        self.assertEqual(16, event.step_index)
        self.assertEqual("LGRC9V3", event.source_family)
        self.assertEqual(
            LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVENT_SCHEMA_VERSION,
            payload["event_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVIDENCE_CLASS,
            payload["evidence_class"],
        )
        self.assertEqual(
            LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
            payload["topology_event_kind"],
        )
        self.assertEqual(evaluation.evaluation_id, payload["source_identity_evaluation_id"])
        self.assertEqual(
            ["topology-pass-1", "topology-pass-2"],
            payload["source_topology_event_ids"],
        )
        self.assertEqual("basin-core-accepted", payload["source_basin_evidence_id"])
        self.assertEqual("accepted-lineage", payload["lineage_id"])
        self.assertTrue(payload["persistence_passed"])
        self.assertTrue(payload["identity_acceptance_allowed"])
        self.assertTrue(payload["identity_acceptance_emitted"])
        self.assertAlmostEqual(0.0, payload["budget_error"])

    def test_lgrc3_identity_acceptance_payload_distinguishes_identity_from_transport(self) -> None:
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=("topology-identity-boundary",),
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
            sink_node_id=0,
            lineage_id="identity-boundary",
            basin_node_ids=(0,),
            node_proper_time={0: 8.0},
            window_start_sink_proper_time=0.0,
            window_start_event_time_key=1.0,
            window_end_event_time_key=9.0,
            scheduler_event_index=17,
            checkpoint_index=9,
            event_time_key=9.0,
            local_median_edge_delay=2.0,
        )

        event = emit_lgrc9v3_proper_time_identity_acceptance(
            evaluation,
            identity_acceptance_allowed=True,
        )
        payload = event.payload

        self.assertFalse(payload["mechanical_expansion_emitted"])
        self.assertFalse(payload["packet_transport_emitted"])
        self.assertFalse(payload["mechanical_expansion_is_identity_acceptance"])
        self.assertFalse(payload["refinement_packet_transport_is_identity_transfer"])
        self.assertFalse(payload["state_mutated"])
        self.assertFalse(payload["topology_mutated"])

    def test_lgrc3_topology_replay_accepts_valid_deterministic_fixture(self) -> None:
        result = validate_lgrc9v3_topology_event_replay(_valid_lgrc3_replay_items())
        artifact = result.to_artifact()

        self.assertIsInstance(result, LGRC9V3TopologyReplayValidationResult)
        self.assertEqual(
            LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_TOPOLOGY_REPLAY_VALIDATION_EVIDENCE_CLASS,
            artifact["evidence_class"],
        )
        self.assertEqual(6, artifact["accepted_artifact_count"])
        self.assertTrue(artifact["event_time_order_valid"])
        self.assertTrue(artifact["lineage_continuity_valid"])
        self.assertTrue(artifact["budget_conservation_valid"])
        self.assertTrue(artifact["replay_valid"])
        self.assertAlmostEqual(0.0, artifact["budget_error"])
        self.assertEqual(
            [
                "lgrc9v3_refinement_packet_transport_result",
                "lgrc9v3_proper_time_inheritance_result",
                "lgrc9v3_collapse_reabsorption_result",
                "lgrc9v3_collapse_reabsorption_packet_transport_result",
                "lgrc9v3_proper_time_identity_persistence_evaluation",
                "lgrc9v3_proper_time_identity_acceptance",
            ],
            [record["record_kind"] for record in artifact["replay_records"]],
        )

    def test_lgrc3_topology_replay_rejects_missing_lineage(self) -> None:
        items = list(_valid_lgrc3_replay_items())
        identity_event = items[-1]
        assert isinstance(identity_event, GRCEvent)
        mutated_event = GRCEvent(
            kind=identity_event.kind,
            step_index=identity_event.step_index,
            payload=dict(identity_event.payload),
            source_family=identity_event.source_family,
        )
        mutated_event.payload["lineage_id"] = ""
        items[-1] = mutated_event

        with self.assertRaisesRegex(ValueError, "lineage"):
            validate_lgrc9v3_topology_event_replay(items)

    def test_lgrc3_topology_replay_rejects_budget_mismatch(self) -> None:
        items = list(_valid_lgrc3_replay_items())
        collapse_artifact = json.loads(json.dumps(items[2], sort_keys=True))
        collapse_artifact["budget_before"] = collapse_artifact["budget_before"] + 1.0
        collapse_artifact["budget_after"] = collapse_artifact["budget_before"]
        collapse_artifact["budget_error"] = 0.0
        items[2] = collapse_artifact

        with self.assertRaisesRegex(InvalidStateTransitionError, "budget"):
            validate_lgrc9v3_topology_event_replay(items)

    def test_lgrc3_topology_replay_rejects_impossible_event_time_ordering(self) -> None:
        items = list(_valid_lgrc3_replay_items())
        items[1], items[2] = items[2], items[1]

        with self.assertRaisesRegex(InvalidStateTransitionError, "event-time"):
            validate_lgrc9v3_topology_event_replay(items)

    def test_lgrc3_packet_transport_through_one_refinement_preserves_budget(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        edge_delay = compute_lgrc9v3_edge_causal_delay(
            state,
            policy=EDGE_DELAY_POLICY_CONSTANT_DELAY,
            tau_0=2.0,
        )
        arrival_key = derive_lgrc9v3_packet_arrival_event_time_key(
            departure_event_time_key=1.0,
            edge_id=0,
            edge_causal_delay=edge_delay,
        )
        departure = process_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=arrival_key,
            scheduler_event_index=1,
            source_lineage_id="source-root",
            target_lineage_id="target-root",
        )
        compact = compact_lgrc9v3_packet_ledger(departure.ledger)

        transport = transport_lgrc9v3_packets_through_refinement(
            departure.ledger,
            _fake_refinement_expansion_event(),
            post_topology_signature=_fake_post_refinement_topology_signature(),
            pending_flux_ledger=compact,
        )
        artifact = json.loads(json.dumps(transport.to_artifact(), sort_keys=True))

        self.assertIsInstance(transport, LGRC9V3RefinementPacketTransportResult)
        self.assertEqual(
            LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(LGRC9V3_PACKET_TRANSPORT_EVIDENCE_CLASS, transport.evidence_class)
        self.assertAlmostEqual(
            departure.ledger.conserved_budget_total,
            transport.budget_before,
        )
        self.assertAlmostEqual(transport.budget_before, transport.budget_after)
        self.assertAlmostEqual(0.0, transport.budget_error)
        self.assertAlmostEqual(0.25, transport.amount_total)
        self.assertFalse(transport.identity_acceptance_emitted)
        self.assertFalse(transport.packet_transport_identity_transfer)
        self.assertEqual("hybrid-spark-0-0", transport.source_expansion_event_id)
        self.assertEqual("candidate-0", transport.source_candidate_event_id)
        self.assertEqual((departure.packet_record.packet_id,), transport.source_packet_ids)
        record = transport.packet_transport_records[0]
        self.assertEqual(0, record.source_node_id_before)
        self.assertEqual(3, record.source_node_id_after)
        self.assertEqual(1, record.target_node_id_after)
        self.assertTrue(record.endpoint_transported)
        self.assertEqual(1, record.old_parent_port)
        self.assertEqual(4, record.new_endpoint_port)
        self.assertEqual(1, record.old_parent_column)
        self.assertEqual(1, record.new_endpoint_column)
        self.assertEqual(
            "source-root|node:0->node:3",
            record.source_lineage_id_after,
        )
        transported_packet = transport.transported_ledger.packet_records[0]
        self.assertEqual(3, transported_packet.source_node_id)
        self.assertEqual(record.source_packet_id, transported_packet.packet_id)
        queued_arrival = transport.transported_ledger.event_queue_records[0]
        self.assertEqual(3, queued_arrival.source_node_id)

    def test_lgrc3_packet_transport_handles_multiple_packets_deterministically(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        first = process_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=1,
            packet_index=0,
        )
        second = process_lgrc9v3_packet_departure(
            state,
            first.ledger,
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.5,
            departure_event_time_key=1.5,
            arrival_event_time_key=3.5,
            scheduler_event_index=2,
            packet_index=1,
        )

        transport = transport_lgrc9v3_packets_through_refinement(
            second.ledger,
            _fake_refinement_expansion_event(),
            post_topology_signature=_fake_post_refinement_topology_signature(),
        )

        self.assertEqual(2, len(transport.packet_transport_records))
        self.assertEqual(
            tuple(sorted(transport.source_packet_ids)),
            transport.source_packet_ids,
        )
        self.assertAlmostEqual(0.75, transport.amount_total)
        endpoint_flags = {
            record.source_packet_id: record.endpoint_transported
            for record in transport.packet_transport_records
        }
        self.assertEqual(1, sum(1 for transported in endpoint_flags.values() if transported))

    def test_lgrc3_packet_transport_rejects_missing_reassignment_for_expanded_node(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        departure = process_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=1,
        )

        with self.assertRaisesRegex(InvalidStateTransitionError, "reassignment"):
            transport_lgrc9v3_packets_through_refinement(
                departure.ledger,
                _fake_refinement_expansion_event(),
                post_topology_signature=_fake_post_refinement_topology_signature(),
            )

    def test_lgrc2_packet_ids_are_deterministic(self) -> None:
        first_id = build_lgrc9v3_packet_id(
            source_node_id=0,
            target_node_id=1,
            edge_id=2,
            amount=0.5,
            departure_event_time_key=1.0,
            arrival_event_time_key=2.0,
            packet_index=3,
        )
        second_id = build_lgrc9v3_packet_id(
            source_node_id=0,
            target_node_id=1,
            edge_id=2,
            amount=0.5,
            departure_event_time_key=1.0,
            arrival_event_time_key=2.0,
            packet_index=3,
        )
        changed_id = build_lgrc9v3_packet_id(
            source_node_id=0,
            target_node_id=1,
            edge_id=2,
            amount=0.5,
            departure_event_time_key=1.0,
            arrival_event_time_key=2.0,
            packet_index=4,
        )

        self.assertEqual(first_id, second_id)
        self.assertNotEqual(first_id, changed_id)
        self.assertTrue(first_id.startswith("lgrc9v3-packet-"))

    def test_lgrc2_arrival_event_time_key_derives_from_captured_delay(self) -> None:
        state = _three_node_state()
        edge_delay = compute_lgrc9v3_edge_causal_delay(
            state,
            policy=EDGE_DELAY_POLICY_CONSTANT_DELAY,
            tau_0=2.25,
        )

        arrival_key = derive_lgrc9v3_packet_arrival_event_time_key(
            departure_event_time_key=1.5,
            edge_id=0,
            edge_causal_delay=edge_delay,
        )
        self.assertAlmostEqual(3.75, arrival_key)

        ledger = build_lgrc9v3_packet_ledger(state=state)
        scheduled = schedule_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.5,
            arrival_event_time_key=arrival_key,
            scheduler_event_index=2,
        )

        packet = scheduled.packet_records[0]
        self.assertEqual(1.5, packet.departure_event_time_key)
        self.assertEqual(arrival_key, packet.arrival_event_time_key)

    def test_lgrc2_arrival_event_time_key_is_not_node_proper_time(self) -> None:
        state = _three_node_state()
        arrival_key = derive_lgrc9v3_packet_arrival_event_time_key(
            departure_event_time_key=1.0,
            edge_id=0,
            edge_causal_delay={0: 2.0},
        )

        eligibility = compute_lgrc9v3_fixed_topology_eligibility(
            state,
            causal_modes={
                "causal_layer_mode": "fixed_topology_semicausal",
                "lgrc_runtime_level": "lgrc1",
                "proper_time_accumulation_policy": "global_scheduler",
                "lapse_policy": LAPSE_POLICY_BOUNDED_DENSITY_TENSION,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "require_fixed_topology_for_lgrc1": True,
            },
            event_time_key=arrival_key,
            lapse_kwargs={
                "lambda_n": 0.5,
                "mu_n": 0.25,
                "c_ref": 2.0,
                "g_ref": 5.0,
                "n_min": 0.1,
                "n_max": 2.0,
            },
        )

        self.assertEqual(3.0, arrival_key)
        self.assertNotEqual(arrival_key, eligibility.node_proper_time[1])
        self.assertAlmostEqual(3.75, eligibility.node_proper_time[1])

    def test_lgrc2_explicit_arrival_event_time_key_remains_replay_fixture_path(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        derived_key = derive_lgrc9v3_packet_arrival_event_time_key(
            departure_event_time_key=1.0,
            edge_id=0,
            edge_causal_delay={0: 2.0},
        )

        scheduled = schedule_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=4.5,
            scheduler_event_index=2,
        )

        self.assertEqual(3.0, derived_key)
        self.assertEqual(4.5, scheduled.packet_records[0].arrival_event_time_key)

    def test_lgrc2_packet_and_event_records_round_trip(self) -> None:
        packet = create_lgrc9v3_packet_record(
            source_node_id=0,
            target_node_id=1,
            edge_id=2,
            amount=0.5,
            departure_event_time_key=1.0,
            arrival_event_time_key=2.0,
            packet_state=LGRC9V3_PACKET_STATE_IN_FLIGHT,
            packet_index=0,
            source_lineage_id="source-lineage",
            target_lineage_id="target-lineage",
        )
        departure_event = create_lgrc9v3_packet_queue_event_record(
            event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            event_time_key=1.0,
            scheduler_event_index=4,
            packet_id=packet.packet_id,
        )

        packet_round_trip = restore_lgrc9v3_packet_record(
            json.loads(json.dumps(packet.to_record(), sort_keys=True))
        )
        event_round_trip = restore_lgrc9v3_packet_queue_event_record(
            json.loads(json.dumps(departure_event.to_record(), sort_keys=True))
        )

        self.assertIsInstance(packet_round_trip, LGRC9V3PacketRecord)
        self.assertEqual(packet, packet_round_trip)
        self.assertIsInstance(event_round_trip, LGRC9V3PacketQueueEventRecord)
        self.assertEqual(departure_event, event_round_trip)
        self.assertEqual(
            departure_event.event_id,
            build_lgrc9v3_packet_event_id(
                event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                event_time_key=1.0,
                scheduler_event_index=4,
                packet_id=packet.packet_id,
            ),
        )

    def test_lgrc2_packet_ledger_round_trips_without_mutating_state(self) -> None:
        state = _three_node_state()
        before_nodes = dict(state.nodes)
        before_edges = dict(state.port_edges)
        packet = create_lgrc9v3_packet_record(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            packet_state=LGRC9V3_PACKET_STATE_IN_FLIGHT,
        )
        queued_arrival = create_lgrc9v3_packet_queue_event_record(
            event_kind=LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            event_time_key=3.0,
            scheduler_event_index=8,
            packet_id=packet.packet_id,
        )

        ledger = build_lgrc9v3_packet_ledger(
            state=state,
            packet_records=(packet,),
            event_queue_records=(queued_arrival,),
            policies={"lgrc_runtime_level": "lgrc2"},
        )
        artifact = ledger.to_artifact()
        restored = restore_lgrc9v3_packet_ledger_artifact(
            json.loads(json.dumps(artifact, sort_keys=True))
        )

        self.assertIsInstance(ledger, LGRC9V3PacketLedger)
        self.assertEqual(LGRC9V3_LGRC2_PACKET_LEDGER_KIND, artifact["artifact_kind"])
        self.assertEqual(
            LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(6.0, ledger.node_coherence_total)
        self.assertEqual(0.25, ledger.in_flight_packet_total)
        self.assertEqual(6.25, ledger.conserved_budget_total)
        self.assertEqual(0.0, ledger.budget_error)
        self.assertEqual(ledger, restored)
        self.assertEqual(before_nodes, state.nodes)
        self.assertEqual(before_edges, state.port_edges)

    def test_lgrc2_empty_packet_ledger_round_trips(self) -> None:
        ledger = build_lgrc9v3_packet_ledger(node_coherence_total=0.0)
        restored = restore_lgrc9v3_packet_ledger_artifact(
            json.loads(json.dumps(ledger.to_artifact(), sort_keys=True))
        )

        self.assertEqual((), ledger.packet_records)
        self.assertEqual(0.0, ledger.conserved_budget_total)
        self.assertEqual(ledger, restored)

    def test_lgrc2_multiple_packets_on_one_edge_have_deterministic_order(self) -> None:
        first = create_lgrc9v3_packet_record(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=2.0,
            packet_state=LGRC9V3_PACKET_STATE_IN_FLIGHT,
            packet_index=0,
        )
        second = create_lgrc9v3_packet_record(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.5,
            departure_event_time_key=1.0,
            arrival_event_time_key=2.5,
            packet_state=LGRC9V3_PACKET_STATE_IN_FLIGHT,
            packet_index=1,
        )

        forward = build_lgrc9v3_packet_ledger(
            node_coherence_total=10.0,
            packet_records=(first, second),
        )
        reversed_ledger = build_lgrc9v3_packet_ledger(
            node_coherence_total=10.0,
            packet_records=(second, first),
        )

        self.assertEqual(
            [packet.packet_id for packet in forward.packet_records],
            [packet.packet_id for packet in reversed_ledger.packet_records],
        )
        self.assertEqual(0.75, forward.in_flight_packet_total)
        self.assertEqual(10.75, forward.conserved_budget_total)

    def test_lgrc2_packet_ledger_orders_queue_events_deterministically(self) -> None:
        packet = create_lgrc9v3_packet_record(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=1.0,
            departure_event_time_key=1.0,
            arrival_event_time_key=2.0,
            packet_state=LGRC9V3_PACKET_STATE_IN_FLIGHT,
        )
        later = create_lgrc9v3_packet_queue_event_record(
            event_kind=LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            event_time_key=2.0,
            scheduler_event_index=3,
            packet_id=packet.packet_id,
        )
        earlier = create_lgrc9v3_packet_queue_event_record(
            event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            event_time_key=1.0,
            scheduler_event_index=2,
            packet_id=packet.packet_id,
        )

        ledger = build_lgrc9v3_packet_ledger(
            node_coherence_total=10.0,
            packet_records=(packet,),
            event_queue_records=(later, earlier),
        )

        self.assertEqual(
            [earlier.event_id, later.event_id],
            [event.event_id for event in ledger.event_queue_records],
        )

    def test_lgrc2_packet_ledger_rejects_budget_inconsistency(self) -> None:
        packet = create_lgrc9v3_packet_record(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=1.0,
            departure_event_time_key=1.0,
            arrival_event_time_key=2.0,
            packet_state=LGRC9V3_PACKET_STATE_IN_FLIGHT,
        )

        with self.assertRaises(ValueError):
            LGRC9V3PacketLedger(
                packet_records=(packet,),
                packet_event_records=(),
                event_queue_records=(),
                node_coherence_total=10.0,
                in_flight_packet_total=0.0,
                conserved_budget_total=10.0,
                budget_before=10.0,
                budget_after=10.0,
                budget_error=0.0,
                fixed_topology_signature={},
                policies={},
            )

    def test_lgrc2_packet_departure_debits_source_and_adds_in_flight(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)

        result = process_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=4,
        )
        artifact = result.to_artifact()

        self.assertIsInstance(result, LGRC9V3PacketProcessingResult)
        self.assertAlmostEqual(0.75, state.nodes[0].coherence)
        self.assertAlmostEqual(5.75, result.ledger.node_coherence_total)
        self.assertAlmostEqual(0.25, result.ledger.in_flight_packet_total)
        self.assertAlmostEqual(6.0, result.ledger.conserved_budget_total)
        self.assertAlmostEqual(6.0, result.budget_before)
        self.assertAlmostEqual(6.0, result.budget_after)
        self.assertAlmostEqual(0.0, result.budget_error)
        self.assertEqual(LGRC9V3_PACKET_STATE_IN_FLIGHT, result.packet_record.packet_state)
        self.assertEqual(
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            result.processed_event.event_kind,
        )
        self.assertEqual(4, result.processed_event.scheduler_event_index)
        self.assertEqual(1.0, result.processed_event.event_time_key)
        self.assertEqual(0, result.processed_event.source_node_id)
        self.assertEqual(1, result.processed_event.target_node_id)
        self.assertEqual(0, result.processed_event.edge_id)
        self.assertEqual(0.25, result.processed_event.amount)
        self.assertEqual(6.0, result.processed_event.budget_before)
        self.assertEqual(6.0, result.processed_event.budget_after)
        self.assertEqual(0.0, result.processed_event.budget_error)
        self.assertEqual(1, len(result.ledger.event_queue_records))
        self.assertEqual(
            LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            result.ledger.event_queue_records[0].event_kind,
        )
        self.assertTrue(result.state_mutated)
        self.assertFalse(result.topology_mutated)
        self.assertFalse(result.spark_event_emitted)
        self.assertFalse(result.mechanical_expansion_emitted)
        self.assertFalse(result.identity_acceptance_emitted)
        self.assertEqual(
            result.processed_event.to_record(),
            artifact["processed_event"],
        )

    def test_lgrc2_packet_arrival_credits_target_and_removes_in_flight(self) -> None:
        state = _three_node_state()
        departure = process_lgrc9v3_packet_departure(
            state,
            build_lgrc9v3_packet_ledger(state=state),
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=4,
        )

        arrival = process_lgrc9v3_packet_arrival(
            state,
            departure.ledger,
            packet_id=departure.packet_record.packet_id,
        )

        self.assertAlmostEqual(0.75, state.nodes[0].coherence)
        self.assertAlmostEqual(2.25, state.nodes[1].coherence)
        self.assertAlmostEqual(6.0, arrival.ledger.node_coherence_total)
        self.assertAlmostEqual(0.0, arrival.ledger.in_flight_packet_total)
        self.assertAlmostEqual(6.0, arrival.ledger.conserved_budget_total)
        self.assertAlmostEqual(6.0, arrival.budget_before)
        self.assertAlmostEqual(6.0, arrival.budget_after)
        self.assertAlmostEqual(0.0, arrival.budget_error)
        self.assertEqual(LGRC9V3_PACKET_STATE_ARRIVED, arrival.packet_record.packet_state)
        self.assertEqual(
            LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            arrival.processed_event.event_kind,
        )
        self.assertEqual((), arrival.ledger.event_queue_records)
        self.assertFalse(arrival.topology_mutated)
        self.assertFalse(arrival.spark_event_emitted)
        self.assertFalse(arrival.mechanical_expansion_emitted)
        self.assertFalse(arrival.identity_acceptance_emitted)

    def test_lgrc2_scheduled_packet_processes_departure_then_arrival(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)

        scheduled = schedule_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=4,
        )

        self.assertAlmostEqual(1.0, state.nodes[0].coherence)
        self.assertEqual(1, len(scheduled.packet_records))
        self.assertEqual(
            LGRC9V3_PACKET_STATE_SCHEDULED,
            scheduled.packet_records[0].packet_state,
        )
        self.assertEqual(0.0, scheduled.in_flight_packet_total)
        self.assertEqual(
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            scheduled.event_queue_records[0].event_kind,
        )

        departure = process_lgrc9v3_next_packet_event(state, scheduled)

        self.assertAlmostEqual(0.75, state.nodes[0].coherence)
        self.assertEqual(
            LGRC9V3_PACKET_STATE_IN_FLIGHT,
            departure.packet_record.packet_state,
        )
        self.assertEqual(0.25, departure.ledger.in_flight_packet_total)
        self.assertEqual(
            LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            departure.ledger.event_queue_records[0].event_kind,
        )

        arrival = process_lgrc9v3_next_packet_event(state, departure.ledger)

        self.assertEqual(LGRC9V3_PACKET_STATE_ARRIVED, arrival.packet_record.packet_state)
        self.assertEqual(0.0, arrival.ledger.in_flight_packet_total)
        self.assertAlmostEqual(2.25, state.nodes[1].coherence)

    def test_lgrc2_next_packet_event_processes_earliest_arrival(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        later_departure = process_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=5.0,
            scheduler_event_index=1,
            packet_index=0,
        )
        earlier_departure = process_lgrc9v3_packet_departure(
            state,
            later_departure.ledger,
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            amount=0.25,
            departure_event_time_key=1.5,
            arrival_event_time_key=3.0,
            scheduler_event_index=2,
            packet_index=1,
        )

        self.assertEqual(
            [3.0, 5.0],
            [
                event.event_time_key
                for event in earlier_departure.ledger.event_queue_records
            ],
        )

        processed = process_lgrc9v3_next_packet_event(state, earlier_departure.ledger)

        self.assertEqual(
            earlier_departure.packet_record.packet_id,
            processed.packet_record.packet_id,
        )
        self.assertEqual(3.0, processed.processed_event.event_time_key)
        self.assertAlmostEqual(3.25, state.nodes[2].coherence)
        self.assertEqual(1, len(processed.ledger.event_queue_records))
        self.assertEqual(5.0, processed.ledger.event_queue_records[0].event_time_key)

    def test_lgrc2_packet_processing_rejects_topology_drift(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        extra_node = state.topology.add_node({"label": "drift"})
        state.nodes[extra_node] = GRC9V3NodeState(
            coherence=0.1,
            gradient_row_basis=[0.0, 0.0, 0.0],
        )

        with self.assertRaises(InvalidStateTransitionError):
            process_lgrc9v3_packet_departure(
                state,
                ledger,
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
                departure_event_time_key=1.0,
                arrival_event_time_key=3.0,
                scheduler_event_index=4,
            )

    def test_lgrc2_arrival_does_not_emit_spark_expansion_or_identity(self) -> None:
        state = _three_node_state()
        before_topology = (
            tuple(state.topology.iter_live_node_ids()),
            tuple(state.topology.iter_live_edge_ids()),
        )
        before_event_log = list(state.event_log)
        departure = process_lgrc9v3_packet_departure(
            state,
            build_lgrc9v3_packet_ledger(state=state),
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=4,
        )

        arrival = process_lgrc9v3_next_packet_event(state, departure.ledger)
        after_topology = (
            tuple(state.topology.iter_live_node_ids()),
            tuple(state.topology.iter_live_edge_ids()),
        )

        self.assertEqual(before_topology, after_topology)
        self.assertEqual(before_event_log, state.event_log)
        self.assertFalse(arrival.topology_mutated)
        self.assertFalse(arrival.spark_event_emitted)
        self.assertFalse(arrival.mechanical_expansion_emitted)
        self.assertFalse(arrival.identity_acceptance_emitted)

    def test_lgrc2_arrival_exposes_update_and_diagnostic_eligibility(self) -> None:
        state = _three_node_state()
        departure = process_lgrc9v3_packet_departure(
            state,
            build_lgrc9v3_packet_ledger(state=state),
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=4,
        )
        arrival = process_lgrc9v3_next_packet_event(state, departure.ledger)

        eligibility = derive_lgrc9v3_packet_arrival_eligibility(arrival)
        artifact = eligibility.to_artifact()

        self.assertIsInstance(eligibility, LGRC9V3PacketArrivalEligibility)
        self.assertEqual(
            LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
            artifact["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_EVIDENCE_CLASS,
            eligibility.evidence_class,
        )
        self.assertEqual(arrival.packet_record.packet_id, eligibility.packet_id)
        self.assertEqual(1, eligibility.target_node_id)
        self.assertTrue(eligibility.local_update_eligible)
        self.assertTrue(eligibility.spark_diagnostic_eligible)
        self.assertFalse(eligibility.spark_event_emitted)
        self.assertFalse(eligibility.mechanical_expansion_emitted)
        self.assertFalse(eligibility.identity_acceptance_emitted)

        with self.assertRaises(InvalidStateTransitionError):
            derive_lgrc9v3_packet_arrival_eligibility(departure)

    def test_lgrc2_departure_arrival_cycle_round_trips_and_preserves_budget(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)

        departure = process_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.4,
            departure_event_time_key=2.0,
            arrival_event_time_key=5.0,
            scheduler_event_index=7,
        )
        departure_ledger_round_trip = restore_lgrc9v3_packet_ledger_artifact(
            json.loads(json.dumps(departure.ledger.to_artifact(), sort_keys=True))
        )

        arrival = process_lgrc9v3_next_packet_event(state, departure.ledger)
        arrival_ledger_round_trip = restore_lgrc9v3_packet_ledger_artifact(
            json.loads(json.dumps(arrival.ledger.to_artifact(), sort_keys=True))
        )
        arrival_artifact_round_trip = json.loads(
            json.dumps(arrival.to_artifact(), sort_keys=True)
        )

        self.assertEqual(departure.ledger, departure_ledger_round_trip)
        self.assertEqual(arrival.ledger, arrival_ledger_round_trip)
        self.assertAlmostEqual(6.0, departure.budget_before)
        self.assertAlmostEqual(6.0, departure.budget_after)
        self.assertAlmostEqual(6.0, arrival.budget_before)
        self.assertAlmostEqual(6.0, arrival.budget_after)
        self.assertAlmostEqual(0.0, departure.budget_error)
        self.assertAlmostEqual(0.0, arrival.budget_error)
        self.assertAlmostEqual(6.0, arrival.ledger.conserved_budget_total)
        self.assertEqual(2, len(arrival.ledger.packet_event_records))
        self.assertEqual(
            "lgrc9v3_packet_processing_result",
            arrival_artifact_round_trip["artifact_kind"],
        )
        self.assertFalse(arrival_artifact_round_trip["topology_mutated"])
        self.assertFalse(arrival_artifact_round_trip["spark_event_emitted"])

    def test_lgrc2_processing_remains_external_to_grc9v3_model_defaults(self) -> None:
        model = GRC9V3.from_config({"dt": 0.1})
        state = model.get_state()

        self.assertNotIn(CAUSAL_LAYER, model.list_capabilities())
        self.assertNotIn(
            LGRC9V3_CAUSAL_MODES_KEY,
            dict(model.get_params().constitutive_semantic_modes),
        )
        self.assertNotIn("lgrc9v3_packet_ledger", state.cached_quantities)
        self.assertNotIn("lgrc_runtime_level", state.cached_quantities)

    def test_lgrc2_pending_flux_compaction_preserves_budget_and_lineage(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        first = process_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=4,
            packet_index=0,
            source_lineage_id="source-lineage",
            target_lineage_id="target-lineage",
        )
        second = process_lgrc9v3_packet_departure(
            state,
            first.ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.5,
            departure_event_time_key=1.5,
            arrival_event_time_key=3.0,
            scheduler_event_index=5,
            packet_index=1,
            source_lineage_id="source-lineage",
            target_lineage_id="target-lineage",
        )

        compact = compact_lgrc9v3_packet_ledger(second.ledger)
        artifact = compact.to_artifact()

        self.assertIsInstance(compact, LGRC9V3PendingFluxLedger)
        self.assertEqual(LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_KIND, artifact["artifact_kind"])
        self.assertEqual(LGRC9V3_PENDING_FLUX_EVIDENCE_CLASS, compact.evidence_class)
        self.assertEqual(
            LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT,
            compact.compaction_policy,
        )
        self.assertEqual(2, compact.expanded_packet_count)
        self.assertEqual(1, compact.compact_entry_count)
        self.assertAlmostEqual(second.ledger.in_flight_packet_total, compact.pending_flux_total)
        self.assertAlmostEqual(
            second.ledger.conserved_budget_total,
            compact.conserved_budget_total,
        )
        entry = compact.pending_flux_entries[0]
        self.assertEqual(0, entry.edge_id)
        self.assertEqual(0, entry.source_node_id)
        self.assertEqual(1, entry.target_node_id)
        self.assertEqual(3.0, entry.arrival_event_time_key)
        self.assertEqual("source-lineage", entry.source_lineage_id)
        self.assertEqual("target-lineage", entry.target_lineage_id)
        self.assertEqual(2, entry.packet_count)
        self.assertAlmostEqual(0.75, entry.amount_total)
        self.assertEqual(
            {
                first.packet_record.packet_id,
                second.packet_record.packet_id,
            },
            set(entry.packet_ids),
        )
        self.assertEqual((1.0, 1.5), entry.departure_event_time_keys)
        self.assertTrue(compact.lineage_preserved)
        self.assertTrue(compact.transport_ready_for_refinement)
        self.assertFalse(compact.topology_change_allowed)
        self.assertFalse(compact.packet_transport_through_topology_change)

    def test_lgrc2_pending_flux_ledger_round_trips_and_ignores_scheduled_packets(self) -> None:
        state = _three_node_state()
        ledger = build_lgrc9v3_packet_ledger(state=state)
        scheduled = schedule_lgrc9v3_packet_departure(
            state,
            ledger,
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            arrival_event_time_key=3.0,
            scheduler_event_index=4,
        )
        departure = process_lgrc9v3_packet_departure(
            state,
            scheduled,
            source_node_id=0,
            target_node_id=2,
            edge_id=2,
            amount=0.25,
            departure_event_time_key=1.25,
            arrival_event_time_key=4.0,
            scheduler_event_index=5,
            packet_index=1,
        )

        compact = compact_lgrc9v3_packet_ledger(departure.ledger)
        restored = restore_lgrc9v3_pending_flux_ledger_artifact(
            json.loads(json.dumps(compact.to_artifact(), sort_keys=True))
        )

        self.assertEqual(compact, restored)
        self.assertEqual(1, compact.expanded_packet_count)
        self.assertEqual(1, compact.compact_entry_count)
        self.assertAlmostEqual(0.25, compact.pending_flux_total)
        self.assertAlmostEqual(
            departure.ledger.conserved_budget_total,
            compact.conserved_budget_total,
        )
        self.assertEqual(
            "lgrc9v3_packet_ledger_v1",
            compact.source_packet_ledger_schema_version,
        )


class LGRC9V3HelperTest(unittest.TestCase):
    """Validate pure Iteration 2 lapse, delay, and distance helpers."""

    def test_lapse_helper_supports_unit_and_bounded_density_tension(self) -> None:
        state = _three_node_state()

        unit_lapse = compute_lgrc9v3_lapse_by_node(
            state,
            policy=LAPSE_POLICY_UNIT,
        )
        bounded_lapse = compute_lgrc9v3_lapse_by_node(
            state,
            policy=LAPSE_POLICY_BOUNDED_DENSITY_TENSION,
            lambda_n=0.5,
            mu_n=0.25,
            c_ref=2.0,
            g_ref=5.0,
            n_min=0.1,
            n_max=2.0,
        )

        self.assertEqual({0: 1.0, 1: 1.0, 2: 1.0}, unit_lapse)
        self.assertAlmostEqual(0.75, bounded_lapse[0])
        self.assertAlmostEqual(1.25, bounded_lapse[1])
        self.assertAlmostEqual(1.25, bounded_lapse[2])

    def test_edge_delay_helpers_are_policy_specific_and_side_effect_free(self) -> None:
        state = _three_node_state()
        before_geometric_length = dict(state.geometric_length)
        before_temporal_delay = dict(state.temporal_delay)

        geometry_delay = compute_lgrc9v3_edge_causal_delay(
            state,
            policy=EDGE_DELAY_POLICY_GEOMETRY_BASELINE,
            tau_0=2.0,
        )
        constant_delay = compute_lgrc9v3_edge_causal_delay(
            state,
            policy=EDGE_DELAY_POLICY_CONSTANT_DELAY,
            tau_0=7.0,
        )
        grcv3_delay = compute_lgrc9v3_edge_causal_delay(
            state,
            policy=EDGE_DELAY_POLICY_GRCV3_TEMPORAL_LABEL,
            v0=1.0,
            rho=1.0,
            eps_tau=1e-12,
        )

        self.assertEqual({0: 4.0, 1: 4.0, 2: 10.0}, geometry_delay)
        self.assertEqual({0: 7.0, 1: 7.0, 2: 7.0}, constant_delay)
        self.assertAlmostEqual(2.0, grcv3_delay[0])
        self.assertAlmostEqual(1.0, grcv3_delay[1])
        self.assertAlmostEqual(1.0, grcv3_delay[2])
        self.assertEqual(before_geometric_length, state.geometric_length)
        self.assertEqual(before_temporal_delay, state.temporal_delay)

    def test_three_distance_surfaces_are_not_conflated(self) -> None:
        state = _three_node_state()
        edge_causal_delay = {0: 5.0, 1: 5.0, 2: 1.0}

        geometric = compute_lgrc9v3_geometric_distances(state, source_node_id=0)
        causal = compute_lgrc9v3_causal_distances(
            state,
            source_node_id=0,
            edge_causal_delay=edge_causal_delay,
        )
        functional = compute_lgrc9v3_functional_distances(
            state,
            source_node_id=0,
            policy=FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE,
        )

        self.assertEqual({0: 0.0, 1: 2.0, 2: 4.0}, geometric)
        self.assertEqual({0: 0.0, 1: 5.0, 2: 1.0}, causal)
        self.assertAlmostEqual(0.01, functional[1])
        self.assertAlmostEqual(0.02, functional[2])
        self.assertNotEqual(geometric, causal)
        self.assertNotEqual(causal, functional)
        self.assertNotEqual(geometric, functional)

    def test_helpers_fail_clearly_on_invalid_inputs(self) -> None:
        state = _three_node_state()
        state.geometric_length[1] = float("nan")

        with self.assertRaisesRegex(ValueError, "geometric_length"):
            compute_lgrc9v3_edge_causal_delay(
                state,
                policy=EDGE_DELAY_POLICY_GEOMETRY_BASELINE,
            )
        with self.assertRaisesRegex(ValueError, "unsupported edge delay policy"):
            compute_lgrc9v3_edge_causal_delay(state, policy="directed_delay")
        with self.assertRaisesRegex(ValueError, "unsupported lapse policy"):
            compute_lgrc9v3_lapse_by_node(state, policy="observer_clock")

    def test_helpers_handle_empty_and_single_node_states(self) -> None:
        empty_state = GRC9V3State(topology=PortGraphBackend())

        self.assertEqual({}, compute_lgrc9v3_lapse_by_node(empty_state))
        self.assertEqual({}, compute_lgrc9v3_edge_causal_delay(empty_state))

        single_graph = PortGraphBackend()
        node_id = single_graph.add_node({"label": "single"})
        single_state = GRC9V3State(
            topology=single_graph,
            nodes={
                node_id: GRC9V3NodeState(
                    coherence=1.0,
                    gradient_row_basis=[0.0, 0.0, 0.0],
                )
            },
        )

        self.assertEqual(
            {node_id: 1.0},
            compute_lgrc9v3_lapse_by_node(single_state, policy=LAPSE_POLICY_UNIT),
        )
        self.assertEqual({}, compute_lgrc9v3_edge_causal_delay(single_state))
        self.assertEqual(
            {node_id: 0.0},
            compute_lgrc9v3_geometric_distances(
                single_state,
                source_node_id=node_id,
            ),
        )


class LGRC9V3AnnotationTest(unittest.TestCase):
    """Validate pure LGRC-0 causal annotations from Iteration 3."""

    def test_lgrc0_annotation_artifact_round_trips_through_json(self) -> None:
        state = _three_node_state()
        state.step_index = 3
        state.sink_set = {2}
        state.basins = {2: {0, 1, 2}}
        events = (
            GRCEvent(
                kind="hybrid_spark_candidate",
                step_index=3,
                payload={"node_id": 2},
                source_family="GRC9V3",
            ),
        )

        annotation = annotate_lgrc9v3_causal_history(
            state,
            events=events,
            causal_modes={
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "event_time_policy": "synchronous_limit",
            },
            edge_delay_kwargs={"tau_0": 2.5},
        )
        artifact = annotation.to_artifact()
        round_tripped = json.loads(json.dumps(artifact, sort_keys=True))

        self.assertTrue(round_tripped["annotation_only"])
        self.assertEqual(LGRC9V3_DERIVED_EVIDENCE_CLASS, round_tripped["evidence_class"])
        self.assertEqual("lgrc0", round_tripped["lgrc_runtime_level"])
        self.assertEqual(3, round_tripped["checkpoint_index"])
        self.assertEqual(3.0, round_tripped["event_time_key"])
        self.assertEqual({"0": 3.0, "1": 3.0, "2": 3.0}, round_tripped["node_proper_time"])
        self.assertEqual({"0": 2.5, "1": 2.5, "2": 2.5}, round_tripped["edge_causal_delay"])
        self.assertEqual(3.0, round_tripped["event_time_records"][0]["event_time_key"])
        self.assertEqual(
            LGRC9V3_DERIVED_EVIDENCE_CLASS,
            round_tripped["causal_basin_core_evidence_class"],
        )

    def test_lgrc0_annotation_does_not_mutate_synchronous_state(self) -> None:
        state = _three_node_state()
        state.step_index = 4
        state.observables = {"budget": 6.0}
        state.event_log = [GRCEvent(kind="existing", step_index=4)]
        before_edges = tuple(state.topology.iter_live_edge_ids())
        before_geometric_length = dict(state.geometric_length)
        before_temporal_delay = dict(state.temporal_delay)
        before_event_log = list(state.event_log)
        before_observables = dict(state.observables)

        annotate_lgrc9v3_causal_history(
            state,
            causal_modes={
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_GEOMETRY_BASELINE,
            },
        )

        self.assertEqual(before_edges, tuple(state.topology.iter_live_edge_ids()))
        self.assertEqual(before_geometric_length, state.geometric_length)
        self.assertEqual(before_temporal_delay, state.temporal_delay)
        self.assertEqual(before_event_log, state.event_log)
        self.assertEqual(before_observables, state.observables)
        self.assertEqual(4, state.step_index)

    def test_causal_cone_and_basin_core_are_bounded_derived_overlays(self) -> None:
        state = _three_node_state()
        state.sink_set = {2}
        state.basins = {2: {0, 1, 2}}

        annotation = annotate_lgrc9v3_causal_history(
            state,
            causal_modes={
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_GEOMETRY_BASELINE,
            },
            causal_cone_horizon=3.0,
        )

        # Geometry-baseline delay uses the fixture lengths directly: edge 0-2
        # costs 5.0 and path 0-1-2 costs 4.0, so horizon 3.0 reaches only 0
        # and 1 from source 0. This is still an undirected LGRC-0 overlay.
        self.assertEqual((0, 1), annotation.causal_cone_by_source[0])
        self.assertEqual((1, 2), annotation.causal_basin_core_by_sink[2])
        self.assertEqual(LGRC9V3_DERIVED_EVIDENCE_CLASS, annotation.evidence_class)
        self.assertTrue(annotation.annotation_only)

    def test_lgrc0_annotation_with_no_events_is_still_valid(self) -> None:
        state = _three_node_state()

        annotation = annotate_lgrc9v3_causal_history(state, events=())
        artifact = annotation.to_artifact()

        self.assertEqual((), annotation.event_time_records)
        self.assertEqual([], artifact["event_time_records"])
        self.assertTrue(annotation.annotation_only)
        self.assertEqual(LGRC9V3_DERIVED_EVIDENCE_CLASS, annotation.evidence_class)

    def test_explicit_event_time_policy_requires_event_payload_key(self) -> None:
        state = _three_node_state()

        with self.assertRaisesRegex(ValueError, "explicit_event_time_key"):
            annotate_lgrc9v3_causal_history(
                state,
                events=(GRCEvent(kind="candidate", step_index=1),),
                causal_modes={
                    "event_time_policy": "explicit_event_time_key",
                },
            )

        annotation = annotate_lgrc9v3_causal_history(
            state,
            events=(
                GRCEvent(
                    kind="candidate",
                    step_index=1,
                    payload={"event_time_key": 12.5},
                ),
            ),
            causal_modes={"event_time_policy": "explicit_event_time_key"},
        )
        self.assertEqual(12.5, annotation.event_time_records[0]["event_time_key"])


class LGRC9V3ArtifactReplayTest(unittest.TestCase):
    """Validate LGRC-0 core artifact and replay surfaces from Iteration 4."""

    def test_causal_history_artifact_restores_with_timing_fields_distinct(self) -> None:
        state = _three_node_state()
        state.step_index = 6
        annotation = annotate_lgrc9v3_causal_history(
            state,
            events=(
                GRCEvent(
                    kind="hybrid_spark_candidate",
                    step_index=6,
                    payload={"node_id": 2},
                    source_family="GRC9V3",
                ),
            ),
            causal_modes={
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "event_time_policy": "synchronous_limit",
            },
            edge_delay_kwargs={"tau_0": 1.5},
        )

        envelope = build_lgrc9v3_causal_history_artifact(annotation)
        round_tripped = json.loads(json.dumps(envelope, sort_keys=True))
        restored = restore_lgrc9v3_causal_annotation_artifact(round_tripped)

        self.assertEqual(LGRC9V3_CAUSAL_ARTIFACT_KIND, envelope["artifact_kind"])
        self.assertEqual(
            LGRC9V3_CAUSAL_ARTIFACT_SCHEMA_VERSION,
            envelope["artifact_schema_version"],
        )
        causal_block = round_tripped[LGRC9V3_CAUSAL_ARTIFACT_KEY]
        self.assertEqual(
            LGRC9V3_ANNOTATION_MODE_VERSION,
            causal_block["annotation_mode_version"],
        )
        self.assertEqual("unit", causal_block["policies"]["lapse_policy"])
        self.assertEqual(
            "constant_delay",
            causal_block["policies"]["edge_delay_policy"],
        )
        self.assertIsNotNone(restored)
        assert restored is not None
        self.assertEqual(6, restored.checkpoint_index)
        self.assertEqual(6, restored.scheduler_event_index)
        self.assertEqual(6.0, restored.event_time_key)
        self.assertEqual({0: 6.0, 1: 6.0, 2: 6.0}, restored.node_proper_time)
        self.assertEqual({0: 1.5, 1: 1.5, 2: 1.5}, restored.edge_causal_delay)
        self.assertEqual(6, restored.event_time_records[0]["step_index"])
        self.assertEqual(6.0, restored.event_time_records[0]["event_time_key"])

    def test_optional_causal_history_preserves_old_snapshot_readers(self) -> None:
        snapshot = _minimal_snapshot()

        validate_snapshot_contract(snapshot)
        self.assertIsNone(extract_lgrc9v3_causal_history_artifact(snapshot))
        self.assertIsNone(restore_lgrc9v3_causal_annotation_artifact(snapshot))
        self.assertIsNone(
            restore_lgrc9v3_causal_annotation_artifact(
                snapshot_from_json(snapshot_to_json(snapshot))
            )
        )

        state = _three_node_state()
        annotation = annotate_lgrc9v3_causal_history(
            state,
            causal_modes={
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            },
        )
        attached = attach_lgrc9v3_causal_history_artifact(snapshot, annotation)
        loaded = snapshot_from_json(snapshot_to_json(attached))
        restored = restore_lgrc9v3_causal_annotation_artifact(loaded)

        self.assertIn(LGRC9V3_CAUSAL_ARTIFACT_KEY, loaded)
        self.assertIsNotNone(restored)
        assert restored is not None
        self.assertTrue(restored.annotation_only)
        self.assertEqual("derived_annotation", restored.evidence_class)

    def test_causal_history_restore_validates_serialized_evidence_constants(self) -> None:
        state = _three_node_state()
        annotation = annotate_lgrc9v3_causal_history(
            state,
            causal_modes={
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            },
        )
        envelope = build_lgrc9v3_causal_history_artifact(annotation)

        for key in (
            "diagnostic_source",
            "evidence_class",
            "causal_basin_core_evidence_class",
            "causal_layer_mode",
            "lgrc_runtime_level",
        ):
            with self.subTest(key=key):
                mutated = json.loads(json.dumps(envelope))
                mutated[LGRC9V3_CAUSAL_ARTIFACT_KEY][key] = "wrong"
                with self.assertRaises(SnapshotCompatibilityError):
                    restore_lgrc9v3_causal_annotation_artifact(mutated)


class LGRC9V3FixedTopologyEligibilityTest(unittest.TestCase):
    """Validate opt-in LGRC-1 fixed-topology semi-causal eligibility."""

    def _lgrc1_modes(self) -> dict[str, object]:
        return {
            "causal_layer_mode": "fixed_topology_semicausal",
            "lgrc_runtime_level": "lgrc1",
            "proper_time_accumulation_policy": "global_scheduler",
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "require_fixed_topology_for_lgrc1": True,
        }

    def test_fixed_topology_eligibility_is_opt_in_and_semi_causal(self) -> None:
        state = _three_node_state()
        state.step_index = 3

        result = compute_lgrc9v3_fixed_topology_eligibility(
            state,
            causal_modes=self._lgrc1_modes(),
            min_delta_tau=2.0,
            node_last_update_proper_time={0: 1.0, 1: 3.0, 2: 0.0},
            processed_node_ids=(0,),
            edge_delay_kwargs={"tau_0": 1.5},
        )
        artifact = result.to_artifact()

        self.assertEqual((0, 2), result.eligible_node_ids)
        self.assertEqual((1,), result.ineligible_node_ids)
        self.assertEqual({0: 2.0, 1: 0.0, 2: 3.0}, result.node_elapsed_proper_time)
        self.assertEqual(3.0, result.next_node_last_update_proper_time[0])
        self.assertEqual(3.0, result.next_node_last_update_proper_time[1])
        self.assertEqual(0.0, result.next_node_last_update_proper_time[2])
        self.assertTrue(result.semi_causal)
        self.assertFalse(result.causal_availability_buffers)
        self.assertFalse(result.packetized_flux)
        self.assertFalse(result.mechanical_expansion_allowed)
        self.assertFalse(result.collapse_allowed)
        self.assertFalse(result.identity_acceptance_allowed)
        self.assertEqual(0.0, result.budget_error)
        self.assertEqual(LGRC9V3_SEMICAUSAL_EVIDENCE_CLASS, result.evidence_class)
        self.assertEqual("fixed_topology_semicausal", artifact["causal_layer_mode"])
        self.assertEqual("lgrc1", artifact["lgrc_runtime_level"])
        self.assertEqual("constant_delay", artifact["policies"]["edge_delay_policy"])

    def test_lgrc1_rejects_annotation_modes_and_topology_change(self) -> None:
        state = _three_node_state()

        with self.assertRaises(InvalidParamsError):
            compute_lgrc9v3_fixed_topology_eligibility(
                state,
                causal_modes={"lgrc_runtime_level": "lgrc0"},
            )

        signature = compute_lgrc9v3_fixed_topology_eligibility(
            state,
            causal_modes=self._lgrc1_modes(),
        ).topology_signature
        changed_state = _three_node_state()
        extra_node = changed_state.topology.add_node({"label": "new"})
        changed_state.nodes[extra_node] = GRC9V3NodeState(
            coherence=0.5,
            gradient_row_basis=[0.0, 0.0, 0.0],
        )

        with self.assertRaises(InvalidStateTransitionError):
            compute_lgrc9v3_fixed_topology_eligibility(
                changed_state,
                causal_modes=self._lgrc1_modes(),
                previous_topology_signature=signature,
            )

    def test_lgrc1_rejects_topology_changing_and_packet_claims(self) -> None:
        state = _three_node_state()

        rejected_kwargs = (
            {"mechanical_expansion_requested": True},
            {"collapse_requested": True},
            {"identity_acceptance_requested": True},
            {"packetized_flux_requested": True},
        )

        for kwargs in rejected_kwargs:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(InvalidParamsError):
                    compute_lgrc9v3_fixed_topology_eligibility(
                        state,
                        causal_modes=self._lgrc1_modes(),
                        **kwargs,
                    )

    def test_lgrc1_eligibility_is_side_effect_free_and_preserves_budget(self) -> None:
        state = _three_node_state()
        before_nodes = tuple(state.topology.iter_live_node_ids())
        before_edges = tuple(state.topology.iter_live_edge_ids())
        before_event_count = len(state.event_log)
        before_budget = sum(node.coherence for node in state.nodes.values())

        result = compute_lgrc9v3_fixed_topology_eligibility(
            state,
            causal_modes=self._lgrc1_modes(),
            event_time_key=4.0,
            min_delta_tau=1.0,
        )

        self.assertEqual(before_nodes, tuple(state.topology.iter_live_node_ids()))
        self.assertEqual(before_edges, tuple(state.topology.iter_live_edge_ids()))
        self.assertEqual(before_event_count, len(state.event_log))
        self.assertAlmostEqual(before_budget, result.budget_before)
        self.assertAlmostEqual(before_budget, result.budget_after)
        self.assertEqual(0.0, result.budget_error)
        self.assertEqual((0, 1, 2), result.eligible_node_ids)


class LGRC9V3SynchronousLimitNoRegressionTest(unittest.TestCase):
    """Validate Iteration 6 synchronous-limit and no-regression boundaries."""

    def _populate_unit_distance_labels(self, model: GRC9V3) -> None:
        state = model.get_state()
        for edge_id in state.topology.iter_live_edge_ids():
            state.geometric_length.setdefault(edge_id, 1.0)
            state.base_conductance.setdefault(edge_id, 1.0)

    def _apply_external_lgrc_helpers(self, model: GRC9V3) -> None:
        annotate_lgrc9v3_causal_history(
            model.get_state(),
            causal_modes={
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            },
        )
        compute_lgrc9v3_fixed_topology_eligibility(
            model.get_state(),
            causal_modes={
                "causal_layer_mode": "fixed_topology_semicausal",
                "lgrc_runtime_level": "lgrc1",
                "proper_time_accumulation_policy": "global_scheduler",
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "require_fixed_topology_for_lgrc1": True,
            },
        )

    def test_lgrc0_synchronous_limit_uses_unit_lapse_and_constant_delay(self) -> None:
        state = _three_node_state()
        state.step_index = 4
        state.time = 1.0
        before_event_count = len(state.event_log)
        before_nodes = tuple(state.topology.iter_live_node_ids())
        before_edges = tuple(state.topology.iter_live_edge_ids())

        annotation = annotate_lgrc9v3_causal_history(
            state,
            events=(
                GRCEvent(kind="sync_event", step_index=4, payload={}),
            ),
            causal_modes={
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "event_time_policy": "synchronous_limit",
            },
            event_time_scale=0.25,
            edge_delay_kwargs={"tau_0": 0.25},
        )

        self.assertEqual(1.0, annotation.event_time_key)
        self.assertEqual({0: 1.0, 1: 1.0, 2: 1.0}, annotation.node_proper_time)
        self.assertEqual({0: 0.25, 1: 0.25, 2: 0.25}, annotation.edge_causal_delay)
        self.assertEqual(1.0, annotation.event_time_records[0]["event_time_key"])
        self.assertEqual(before_event_count, len(state.event_log))
        self.assertEqual(before_nodes, tuple(state.topology.iter_live_node_ids()))
        self.assertEqual(before_edges, tuple(state.topology.iter_live_edge_ids()))

    def test_constant_delay_policy_is_standalone_synchronous_limit_case(self) -> None:
        state = _three_node_state()

        delays = compute_lgrc9v3_edge_causal_delay(
            state,
            policy=EDGE_DELAY_POLICY_CONSTANT_DELAY,
            tau_0=0.25,
        )

        self.assertEqual({0: 0.25, 1: 0.25, 2: 0.25}, delays)

    def test_lgrc1_synchronous_eligibility_has_no_in_flight_retention(self) -> None:
        state = _three_node_state()
        state.step_index = 4
        result = compute_lgrc9v3_fixed_topology_eligibility(
            state,
            causal_modes={
                "causal_layer_mode": "fixed_topology_semicausal",
                "lgrc_runtime_level": "lgrc1",
                "proper_time_accumulation_policy": "synchronous_limit",
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "event_time_policy": "synchronous_limit",
                "require_fixed_topology_for_lgrc1": True,
            },
            event_time_scale=0.25,
            min_delta_tau=1.0,
            edge_delay_kwargs={"tau_0": 0.25},
        )
        artifact = result.to_artifact()

        self.assertEqual((0, 1, 2), result.eligible_node_ids)
        self.assertEqual((), result.ineligible_node_ids)
        self.assertEqual({0: 1.0, 1: 1.0, 2: 1.0}, result.node_proper_time)
        self.assertEqual({0: 1.0, 1: 1.0, 2: 1.0}, result.node_elapsed_proper_time)
        self.assertFalse(result.packetized_flux)
        self.assertFalse(result.causal_availability_buffers)
        self.assertEqual(0.0, result.budget_error)
        self.assertFalse(artifact["packetized_flux"])
        self.assertNotIn("in_flight_packets", artifact)
        self.assertNotIn("pending_flux_ledger", artifact)

    def test_existing_default_models_do_not_claim_causal_layer(self) -> None:
        grc9 = GRC9.from_config({"dt": 0.1})
        grc9v3 = GRC9V3.from_config({"dt": 0.1})

        self.assertNotIn(CAUSAL_LAYER, grc9.list_capabilities())
        self.assertNotIn(CAUSAL_LAYER, grc9v3.list_capabilities())
        self.assertNotIn(
            LGRC9V3_CAUSAL_MODES_KEY,
            dict(grc9v3.get_params().constitutive_semantic_modes),
        )

    def test_lane_a_signed_hessian_spark_evidence_unchanged_when_lgrc_disabled(self) -> None:
        model = GRC9V3.from_state(
            _lane_a_saturated_candidate_state(),
            _lane_a_spark_params(),
        )
        self._populate_unit_distance_labels(model)
        before_candidates = model.detect_hybrid_spark_candidates()
        before_event_count = len(model.get_state().event_log)
        before_topology = (
            tuple(model.get_state().topology.iter_live_node_ids()),
            tuple(model.get_state().topology.iter_live_edge_ids()),
        )

        self._apply_external_lgrc_helpers(model)

        after_candidates = model.detect_hybrid_spark_candidates()
        after_topology = (
            tuple(model.get_state().topology.iter_live_node_ids()),
            tuple(model.get_state().topology.iter_live_edge_ids()),
        )
        self.assertEqual(1, len(before_candidates))
        self.assertTrue(before_candidates[0].payload["signed_hessian_degeneracy_gate"])
        self.assertNotIn("spark_lane", before_candidates[0].payload)
        self.assertNotIn("column_h", before_candidates[0].payload)
        self.assertEqual(before_candidates, after_candidates)
        self.assertEqual(before_event_count, len(model.get_state().event_log))
        self.assertEqual(before_topology, after_topology)

    def test_lane_b_column_h_spark_evidence_unchanged_when_lgrc_disabled(self) -> None:
        model = GRC9V3.from_state(
            _lane_b_column_h_state(),
            _lane_b_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        self._populate_unit_distance_labels(model)
        before_candidates = model.detect_hybrid_spark_candidates()
        before_event_count = len(model.get_state().event_log)
        before_topology = (
            tuple(model.get_state().topology.iter_live_node_ids()),
            tuple(model.get_state().topology.iter_live_edge_ids()),
        )

        self._apply_external_lgrc_helpers(model)

        after_candidates = model.detect_hybrid_spark_candidates()
        after_topology = (
            tuple(model.get_state().topology.iter_live_node_ids()),
            tuple(model.get_state().topology.iter_live_edge_ids()),
        )
        self.assertEqual(1, len(before_candidates))
        self.assertEqual(
            ["column_h_threshold_hit"],
            before_candidates[0].payload["gate_reasons"],
        )
        self.assertTrue(before_candidates[0].payload["column_h_branch_hit"])
        self.assertFalse(before_candidates[0].payload["signed_hessian_hit"])
        self.assertEqual(before_candidates, after_candidates)
        self.assertEqual(before_event_count, len(model.get_state().event_log))
        self.assertEqual(before_topology, after_topology)
