"""LGRC9V3 telemetry and graph-checkpoint extension contracts.

The active LGRC9V3 runtime reuses GRC9V3 substrate state, but its telemetry
surface is causal: packet events, local updates, causal spark diagnostics,
topology integration, collapse/reabsorption, and identity acceptance are
classified by runtime event payloads rather than by the shared event kind alone.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pygrc.core import GRCEvent
from pygrc.models.grc_9_ports import slot_to_port_id
from pygrc.models.lgrc_9_v3 import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
    LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_BOUNDARY_BIRTH,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED,
)
from pygrc.models.lgrc_9_v3_runtime import (
    LGRC9V3,
    LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
    LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND,
    LGRC9V3_LOCAL_UPDATE_EVENT_KIND,
    LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY,
    LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND,
    LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY,
)
from pygrc.models.lgrc_9_v3_runtime_state import (
    LGRC9V3_RUNTIME_STATE_SCHEMA_VERSION,
    LGRC9V3RuntimeState,
)

from .schema import (
    GraphCheckpointArtifact,
    RunTelemetryIdentity,
    TelemetryFamilyExtensions,
)


LGRC9V3_TELEMETRY_FAMILY = "lgrc9v3"
LGRC9V3_TELEMETRY_CONTRACT_VERSION = "phase8_lgrc9v3_iter56_v1"
LGRC9V3_EVENT_EXTENSION_SCHEMA_VERSION = "lgrc9v3_event_extension_v1"
LGRC9V3_STEP_EXTENSION_SCHEMA_VERSION = "lgrc9v3_step_extension_v1"
LGRC9V3_RUN_SUMMARY_EXTENSION_SCHEMA_VERSION = "lgrc9v3_run_summary_extension_v1"
LGRC9V3_GRAPH_CHECKPOINT_SCHEMA_VERSION = "lgrc9v3_graph_checkpoint_v1"
LGRC9V3_GRAPH_CHECKPOINT_SURFACE = "lgrc9v3_runtime_causal_overlay"

LGRC9V3_EVENT_DOMAIN_PACKET = "packet"
LGRC9V3_EVENT_DOMAIN_LOCAL_UPDATE = "local_update"
LGRC9V3_EVENT_DOMAIN_SELF_REARM = "self_rearm"
LGRC9V3_EVENT_DOMAIN_PULSE_SUBSTRATE_SURFACE = "pulse_substrate_surface"
LGRC9V3_EVENT_DOMAIN_SPARK = "spark"
LGRC9V3_EVENT_DOMAIN_TOPOLOGY = "topology"
LGRC9V3_EVENT_DOMAIN_COLLAPSE = "collapse"
LGRC9V3_EVENT_DOMAIN_IDENTITY = "identity"
LGRC9V3_EVENT_DOMAIN_OTHER = "other"

_PACKET_EVENT_KINDS = frozenset(
    {
        LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
        LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
    }
)

_TOPOLOGY_EVENT_KINDS = frozenset(
    {
        "hybrid_mechanical_expansion",
        "hybrid_spark_completed",
        LGRC9V3_TOPOLOGY_EVENT_KIND_BOUNDARY_BIRTH,
        LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
        LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
    }
)

_COLLAPSE_EVENT_KINDS = frozenset(
    {
        LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
    }
)


def _optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return int(value)
    return None


def _optional_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _string_keyed_float_map(values: Mapping[int, float]) -> dict[str, float]:
    return {str(int(key)): float(values[key]) for key in sorted(values)}


def _node_id_from_payload(payload: Mapping[str, Any]) -> int | None:
    for key in (
        "target_node_id",
        "source_node_id",
        "candidate_node_id",
        "sink_node_id",
        "parent_node_id",
        "child_node_id",
        "expanded_node_id",
        "selected_sink_id",
    ):
        value = _optional_int(payload.get(key))
        if value is not None:
            return value
    return None


def _event_id_from_payload(event_kind: str, payload: Mapping[str, Any]) -> str | None:
    for key in (
        "event_id",
        "packet_event_id",
        "arrival_event_id",
        "departure_event_id",
        "local_update_event_id",
        "causal_candidate_event_id",
        "candidate_event_id",
        "topology_event_id",
        "self_rearm_evidence_id",
        "candidate_self_rearm_evidence_id",
        "causal_boundary_birth_event_id",
        "expansion_id",
    ):
        value = _optional_string(payload.get(key))
        if value:
            return value
    if event_kind == "hybrid_spark_completed":
        return _optional_string(payload.get("completed_event_id"))
    return None


def _event_domain_and_stage(
    event_kind: str,
    payload: Mapping[str, Any],
) -> tuple[str, str]:
    if event_kind in _PACKET_EVENT_KINDS:
        if event_kind == LGRC9V3_PACKET_EVENT_KIND_DEPARTURE:
            return (LGRC9V3_EVENT_DOMAIN_PACKET, "departure")
        if event_kind == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL:
            return (LGRC9V3_EVENT_DOMAIN_PACKET, "arrival")
        return (LGRC9V3_EVENT_DOMAIN_PACKET, "arrival_eligibility")
    if event_kind == LGRC9V3_LOCAL_UPDATE_EVENT_KIND:
        return (LGRC9V3_EVENT_DOMAIN_LOCAL_UPDATE, "arrival_local_update")
    if event_kind == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND:
        return (
            LGRC9V3_EVENT_DOMAIN_SELF_REARM,
            str(payload.get("self_rearm_status", "unknown")),
        )
    if event_kind == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND:
        return (
            LGRC9V3_EVENT_DOMAIN_PULSE_SUBSTRATE_SURFACE,
            str(payload.get("surface_kind", "unknown")),
        )
    if event_kind == LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND:
        return (LGRC9V3_EVENT_DOMAIN_SPARK, "candidate")
    if event_kind == LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE:
        return (LGRC9V3_EVENT_DOMAIN_IDENTITY, "accepted")
    if event_kind in _COLLAPSE_EVENT_KINDS:
        return (LGRC9V3_EVENT_DOMAIN_COLLAPSE, event_kind.removeprefix("lgrc9v3_causal_"))
    if event_kind in _TOPOLOGY_EVENT_KINDS:
        if event_kind == "hybrid_mechanical_expansion":
            return (LGRC9V3_EVENT_DOMAIN_TOPOLOGY, "mechanical_expansion")
        if event_kind == "hybrid_spark_completed":
            return (LGRC9V3_EVENT_DOMAIN_TOPOLOGY, "spark_completion")
        return (LGRC9V3_EVENT_DOMAIN_TOPOLOGY, event_kind.removeprefix("lgrc9v3_"))
    if str(payload.get("runtime_family", "")) == "LGRC9V3":
        return (LGRC9V3_EVENT_DOMAIN_TOPOLOGY, "runtime_family_event")
    return (LGRC9V3_EVENT_DOMAIN_OTHER, "other")


def classify_lgrc9v3_event_extension(
    event_kind: str,
    payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Return the LGRC9V3 event telemetry extension for one runtime event."""

    event_domain, lifecycle_stage = _event_domain_and_stage(event_kind, payload)
    return {
        "contract_version": LGRC9V3_TELEMETRY_CONTRACT_VERSION,
        "event_extension_schema_version": LGRC9V3_EVENT_EXTENSION_SCHEMA_VERSION,
        "runtime_family": payload.get("runtime_family", "LGRC9V3"),
        "event_kind": str(event_kind),
        "event_domain": event_domain,
        "lifecycle_stage": lifecycle_stage,
        "event_id": _event_id_from_payload(event_kind, payload),
        "event_schema_version": _optional_string(payload.get("event_schema_version")),
        "scheduler_event_index": _optional_int(payload.get("scheduler_event_index")),
        "checkpoint_index": _optional_int(payload.get("checkpoint_index")),
        "event_time_key": _optional_float(payload.get("event_time_key")),
        "causal_layer_mode": _optional_string(payload.get("causal_layer_mode")),
        "lgrc_runtime_level": _optional_string(payload.get("lgrc_runtime_level")),
        "state_mutated": bool(payload.get("state_mutated", False)),
        "topology_mutated": bool(payload.get("topology_mutated", False)),
        "packetized_flux_applied": bool(payload.get("packetized_flux_applied", False)),
        "delayed_evaluation_applied": bool(payload.get("delayed_evaluation_applied", False)),
        "spark_event_emitted": bool(payload.get("spark_event_emitted", False)),
        "mechanical_expansion_emitted": bool(payload.get("mechanical_expansion_emitted", False)),
        "packet_transport_emitted": bool(payload.get("packet_transport_emitted", False)),
        "identity_acceptance_emitted": bool(payload.get("identity_acceptance_emitted", False)),
        "budget_before": _optional_float(payload.get("budget_before")),
        "budget_after": _optional_float(payload.get("budget_after")),
        "budget_error": _optional_float(payload.get("budget_error")),
        "primary_node_id": _node_id_from_payload(payload),
        "primary_edge_id": _optional_int(payload.get("edge_id", payload.get("primary_edge_id"))),
        "packet_id": _optional_string(payload.get("packet_id")),
        "source_packet_ids": list(payload.get("source_packet_ids", ())),
        "transported_packet_ids": list(payload.get("transported_packet_ids", ())),
        "settled_packet_ids": list(payload.get("settled_packet_ids", ())),
        "spark_lane": _optional_string(payload.get("spark_lane")),
        "gate_reasons": list(payload.get("gate_reasons", ())),
        "column_h_branch_hit": payload.get("column_h_branch_hit"),
        "lane_b_candidate_hit": payload.get("lane_b_candidate_hit"),
        "source_candidate_event_id": _optional_string(
            payload.get("source_candidate_event_id")
            or payload.get("source_causal_candidate_event_id")
            or payload.get("source_grc9v3_candidate_event_id")
        ),
        "causal_spark_evaluation_index": _optional_int(
            payload.get("causal_spark_evaluation_index")
        ),
        "topology_event_id": _optional_string(payload.get("topology_event_id")),
        "native_route_arbitration_record_id": _optional_string(
            payload.get("native_route_arbitration_record_id")
        ),
        "native_route_arbitration_digest": _optional_string(
            payload.get("native_route_arbitration_digest")
        ),
        "native_route_candidate_set_digest": _optional_string(
            payload.get("native_route_candidate_set_digest")
        ),
        "native_route_selected_candidate_route_id": _optional_string(
            payload.get("native_route_selected_candidate_route_id")
        ),
        "native_route_selected_candidate_route_digest": _optional_string(
            payload.get("native_route_selected_candidate_route_digest")
        ),
        "expansion_id": _optional_string(payload.get("expansion_id")),
        "source_expansion_event_id": _optional_string(
            payload.get("source_expansion_event_id")
        ),
        "source_identity_evaluation_id": _optional_string(
            payload.get("source_identity_evaluation_id")
        ),
        "identity_clock_policy": _optional_string(payload.get("identity_clock_policy")),
        "route_aspect_id": _optional_string(payload.get("route_aspect_id")),
        "route_aspect_digest": _optional_string(payload.get("route_aspect_digest")),
        "surface_id": _optional_string(payload.get("surface_id")),
        "surface_policy_id": _optional_string(payload.get("surface_policy_id")),
        "surface_policy_enabled": bool(payload.get("surface_policy_enabled", False)),
        "surface_policy_validated": bool(
            payload.get("surface_policy_validated", False)
        ),
        "surface_kind": _optional_string(payload.get("surface_kind")),
        "surface_digest": _optional_string(payload.get("surface_digest")),
        "surface_budget_surface": _optional_string(
            payload.get("surface_budget_surface")
        ),
        "surface_budget_error": _optional_float(payload.get("surface_budget_error")),
        "pulse_event_id": _optional_string(payload.get("pulse_event_id")),
        "pulse_packet_id": _optional_string(payload.get("pulse_packet_id")),
        "pulse_event_kind": _optional_string(payload.get("pulse_event_kind")),
        "pulse_channel_id": _optional_string(payload.get("pulse_channel_id")),
        "contact_amount": _optional_float(payload.get("contact_amount")),
        "lineage_status": _optional_string(payload.get("lineage_status")),
        "producer_record_id": _optional_string(payload.get("producer_record_id")),
        "parent_packet_id": _optional_string(payload.get("parent_packet_id")),
        "child_packet_id": _optional_string(payload.get("child_packet_id")),
        "parent_arrival_event_id": _optional_string(
            payload.get("parent_arrival_event_id")
        ),
        "child_departure_event_id": _optional_string(
            payload.get("child_departure_event_id")
        ),
        "self_rearm_status": _optional_string(payload.get("self_rearm_status")),
        "native_self_rearm_evidence": bool(
            payload.get("native_self_rearm_evidence", False)
        ),
        "native_d2_3_equivalent": bool(payload.get("native_d2_3_equivalent", False)),
        "movement_claim_allowed": bool(payload.get("movement_claim_allowed", False)),
    }


def lgrc9v3_event_family_extensions(
    event_kind: str,
    payload: Mapping[str, Any],
) -> TelemetryFamilyExtensions:
    """Wrap one LGRC9V3 event extension under the family key."""

    return {
        LGRC9V3_TELEMETRY_FAMILY: classify_lgrc9v3_event_extension(
            event_kind,
            payload,
        )
    }


def lgrc9v3_event_family_extensions_for_events(
    events: Sequence[GRCEvent],
) -> tuple[TelemetryFamilyExtensions, ...]:
    """Return per-event LGRC9V3 family extensions for an ordered event list."""

    return tuple(
        lgrc9v3_event_family_extensions(event.kind, event.payload)
        for event in events
    )


def _runtime_state_from_model_or_state(model_or_state: LGRC9V3 | LGRC9V3RuntimeState) -> LGRC9V3RuntimeState:
    if isinstance(model_or_state, LGRC9V3RuntimeState):
        return model_or_state
    return model_or_state.get_state()


def _packet_ledger_surface(state: LGRC9V3RuntimeState) -> Mapping[str, Any]:
    ledger = state.packet_ledger
    if ledger is None:
        return {
            "packet_count": 0,
            "event_queue_length": 0,
            "in_flight_packet_total": 0.0,
            "conserved_budget_total": 0.0,
        }
    return {
        "packet_count": len(ledger.packet_records),
        "packet_event_count": len(ledger.packet_event_records),
        "event_queue_length": len(ledger.event_queue_records),
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "conserved_budget_total": float(ledger.conserved_budget_total),
        "budget_error": float(ledger.budget_error),
    }


def _packet_loop_surface(state: LGRC9V3RuntimeState) -> Mapping[str, Any]:
    trigger_config = state.cached_quantities.get(
        LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY,
        {},
    )
    self_rearm_log = state.cached_quantities.get(
        LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY,
        [],
    )
    production_log = state.cached_quantities.get(
        LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
        [],
    )
    route_digest = None
    producer_policy = None
    latest_reason_code = None
    if isinstance(trigger_config, Mapping):
        route_digest = trigger_config.get("route_aspect_digest")
        producer_policy = "packet_departure_from_route_surplus"
    if isinstance(production_log, Sequence) and not isinstance(production_log, str):
        for result in reversed(production_log):
            if not isinstance(result, Mapping):
                continue
            producer_policy = result.get("producer_policy", producer_policy)
            records = result.get("production_records", ())
            if isinstance(records, Sequence) and not isinstance(records, str):
                for record in reversed(records):
                    if isinstance(record, Mapping):
                        latest_reason_code = record.get("reason_code")
                        break
            break
    completed_count = 0
    if isinstance(self_rearm_log, Sequence) and not isinstance(self_rearm_log, str):
        completed_count = sum(
            1
            for record in self_rearm_log
            if isinstance(record, Mapping)
            and record.get("self_rearm_status") == "child_departure_processed"
        )
    return {
        "native_lgrc9v3_execution": True,
        "native_packet_execution": True,
        "route_aspect_surplus_trigger_configured": isinstance(
            trigger_config, Mapping
        )
        and bool(trigger_config),
        "route_aspect_digest": None if route_digest is None else str(route_digest),
        "producer_policy": None if producer_policy is None else str(producer_policy),
        "latest_reason_code": None
        if latest_reason_code is None
        else str(latest_reason_code),
        "autonomous_production_result_count": len(production_log)
        if isinstance(production_log, Sequence)
        and not isinstance(production_log, str)
        else 0,
        "self_rearm_evidence_count": len(self_rearm_log)
        if isinstance(self_rearm_log, Sequence)
        and not isinstance(self_rearm_log, str)
        else 0,
        "completed_self_rearm_count": completed_count,
        "native_surplus_trigger": isinstance(production_log, Sequence)
        and not isinstance(production_log, str)
        and len(production_log) > 0,
        "native_self_rearm_evidence": completed_count > 0,
        "native_d2_3_equivalent": False,
        "native_d2_3_equivalent_requires_control_parity": True,
        "adapter_required_for_d2_3_semantics": completed_count <= 0,
        "native_static_route_only": False,
        "native_grc9v3_loop_evidence": False,
        "movement_claim_allowed": False,
    }


def _pulse_substrate_surface(state: LGRC9V3RuntimeState) -> Mapping[str, Any]:
    surface_log = state.causal_pulse_substrate_surface_log
    lineage_log = state.causal_pulse_substrate_surface_lineage_log
    production_log = state.cached_quantities.get(
        LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
        [],
    )
    lineage_enabled = bool(
        state.causal_modes.get(
            "causal_pulse_substrate_surface_lineage_transport_enabled",
            False,
        )
    )
    surface_producer_policies = {
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
    }
    surface_producer_count = 0
    latest_reason_code = None
    stale_surface_read_blocked_count = 0
    pre_reabsorption_state_read_blocked_count = 0
    if isinstance(production_log, Sequence) and not isinstance(production_log, str):
        for result in production_log:
            if not isinstance(result, Mapping):
                continue
            if result.get("producer_policy") not in surface_producer_policies:
                continue
            surface_producer_count += 1
            records = result.get("production_records", ())
            if isinstance(records, Sequence) and not isinstance(records, str):
                for record in records:
                    if isinstance(record, Mapping):
                        reason_code = record.get("reason_code")
                        latest_reason_code = reason_code
                        stale_blocked = (
                            reason_code
                            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED
                        )
                        if (
                            stale_blocked
                        ):
                            stale_surface_read_blocked_count += 1
                        if (
                            reason_code
                            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED
                        ):
                            pre_reabsorption_state_read_blocked_count += 1
                        evidence = record.get("observed_evidence", {})
                        if (
                            not stale_blocked
                            and isinstance(evidence, Mapping)
                            and evidence.get("primary_blocker")
                            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED
                        ):
                            stale_surface_read_blocked_count += 1
    latest_row = surface_log[-1] if surface_log else None
    latest_lineage_record = lineage_log[-1] if lineage_log else None
    budget_surfaces = sorted(
        {
            str(row.surface_budget_surface)
            for row in surface_log
            if row.surface_budget_surface
        }
    )
    summary: dict[str, Any] = {
        "native_causal_pulse_substrate_surface_enabled": bool(
            state.causal_modes.get("causal_pulse_substrate_surface_enabled", False)
        ),
        "native_causal_pulse_substrate_surface_validated": bool(
            state.causal_modes.get("causal_pulse_substrate_surface_validated", False)
        ),
        "surface_policy": _optional_string(
            state.causal_modes.get("causal_pulse_substrate_surface_policy")
        ),
        "surface_row_count": len(surface_log),
        "route_local_pulse_contact_count": sum(
            1
            for row in surface_log
            if row.surface_kind == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT
        ),
        "feedback_eligibility_count": sum(
            1
            for row in surface_log
            if row.surface_kind == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY
        ),
        "latest_surface_kind": None if latest_row is None else latest_row.surface_kind,
        "latest_surface_digest": None if latest_row is None else latest_row.surface_digest,
        "surface_budget_surfaces": budget_surfaces,
        "surface_producer_result_count": surface_producer_count,
        "latest_surface_producer_reason_code": None
        if latest_reason_code is None
        else str(latest_reason_code),
        "movement_claim_allowed": False,
        "native_m6": False,
    }
    if lineage_enabled:
        summary.update(
            {
                "native_causal_pulse_substrate_surface_lineage_transport_enabled": True,
                "native_causal_pulse_substrate_surface_lineage_transport_validated": bool(
                    state.causal_modes.get(
                        "causal_pulse_substrate_surface_lineage_transport_validated",
                        False,
                    )
                ),
                "native_causal_pulse_substrate_surface_lineage_transport_supported": bool(
                    state.causal_modes.get(
                        "causal_pulse_substrate_surface_lineage_transport_supported",
                        False,
                    )
                ),
                "surface_lineage_transport_policy": _optional_string(
                    state.causal_modes.get(
                        "causal_pulse_substrate_surface_lineage_transport_policy"
                    )
                ),
                "surface_lineage_record_count": len(lineage_log),
                "transported_lineage_record_count": sum(
                    1
                    for record in lineage_log
                    if record.lineage_action
                    == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
                ),
                "superseded_lineage_record_count": sum(
                    1
                    for record in lineage_log
                    if record.lineage_action
                    == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED
                ),
                "transported_surface_row_count": sum(
                    1
                    for row in surface_log
                    if bool(
                        row.surface_values_after.get(
                            "transported_surface_current",
                            False,
                        )
                    )
                ),
                "latest_surface_lineage_record_id": None
                if latest_lineage_record is None
                else latest_lineage_record.surface_lineage_record_id,
                "latest_surface_lineage_record_digest": None
                if latest_lineage_record is None
                else latest_lineage_record.lineage_record_digest,
                "latest_surface_lineage_action": None
                if latest_lineage_record is None
                else latest_lineage_record.lineage_action,
                "latest_surface_lineage_status": None
                if latest_lineage_record is None
                else latest_lineage_record.lineage_status,
                "producer_stale_surface_read_blocked_count": (
                    stale_surface_read_blocked_count
                ),
                "producer_pre_reabsorption_state_read_blocked_count": (
                    pre_reabsorption_state_read_blocked_count
                ),
                "adaptive_topology_entry_allowed": False,
            }
        )
    return summary


def _topology_state_reabsorption_surface(
    state: LGRC9V3RuntimeState,
) -> Mapping[str, Any]:
    records = state.topology_state_reabsorption_log
    latest = records[-1] if records else None
    return {
        "native_topology_state_reabsorption_enabled": bool(
            state.causal_modes.get("causal_topology_state_reabsorption_enabled", False)
        ),
        "native_topology_state_reabsorption_validated": bool(
            state.causal_modes.get(
                "causal_topology_state_reabsorption_validated",
                False,
            )
        ),
        "native_topology_state_reabsorption_supported": bool(
            state.causal_modes.get(
                "causal_topology_state_reabsorption_supported",
                False,
            )
        ),
        "topology_state_reabsorption_policy": _optional_string(
            state.causal_modes.get("causal_topology_state_reabsorption_policy")
        ),
        "topology_state_reabsorption_record_count": len(records),
        "latest_topology_state_reabsorption_record_id": None
        if latest is None
        else latest.topology_state_reabsorption_record_id,
        "latest_topology_state_reabsorption_digest": None
        if latest is None
        else latest.topology_state_reabsorption_digest,
        "latest_topology_event_digest": None
        if latest is None
        else latest.topology_event_digest,
        "latest_state_reabsorption_action": None
        if latest is None
        else latest.state_reabsorption_action,
        "active_node_state_total_after": None
        if latest is None
        else float(latest.active_node_state_total_after),
        "packet_ledger_node_total_after": None
        if latest is None
        else float(latest.packet_ledger_node_total_after),
        "node_plus_packet_budget_error": None
        if latest is None
        else float(latest.node_plus_packet_budget_error),
        "movement_claim_allowed": False,
        "adaptive_topology_movement_claim_allowed": False,
        "topology_mutating_movement_claim_allowed": False,
        "agency_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
    }


def _topology_event_payload(event: GRCEvent | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(event, GRCEvent):
        return event.payload
    payload = event.get("payload")
    if isinstance(payload, Mapping):
        return payload
    return event


def _native_route_arbitration_surface(state: LGRC9V3RuntimeState) -> Mapping[str, Any]:
    candidate_log = state.native_route_candidate_log
    candidate_set_log = state.native_route_candidate_set_log
    arbitration_log = state.native_route_arbitration_log
    latest_candidate_set = candidate_set_log[-1] if candidate_set_log else None
    latest_arbitration = arbitration_log[-1] if arbitration_log else None
    selected_arbitrations = [
        record for record in arbitration_log if record.selected_candidate_route_digest
    ]
    committed_selected_events = [
        _topology_event_payload(event)
        for event in state.topology_event_log
        if _topology_event_payload(event).get("native_route_arbitration_record_id")
    ]
    return {
        "native_lgrc_route_arbitration_enabled": bool(
            state.causal_modes.get("native_lgrc_route_arbitration_enabled", False)
        ),
        "native_lgrc_route_arbitration_validated": bool(
            state.causal_modes.get("native_lgrc_route_arbitration_validated", False)
        ),
        "native_lgrc_route_arbitration_supported": bool(
            state.causal_modes.get("native_lgrc_route_arbitration_supported", False)
        ),
        "native_lgrc_route_arbitration_policy": _optional_string(
            state.causal_modes.get("native_lgrc_route_arbitration_policy")
        ),
        "candidate_route_record_count": len(candidate_log),
        "candidate_set_record_count": len(candidate_set_log),
        "route_arbitration_record_count": len(arbitration_log),
        "selected_route_arbitration_record_count": len(selected_arbitrations),
        "committed_selected_topology_event_count": len(committed_selected_events),
        "latest_candidate_set_digest": None
        if latest_candidate_set is None
        else latest_candidate_set.candidate_set_digest,
        "latest_route_arbitration_digest": None
        if latest_arbitration is None
        else latest_arbitration.native_route_arbitration_digest,
        "latest_route_arbitration_reason_code": None
        if latest_arbitration is None
        else latest_arbitration.arbitration_reason_code,
        "latest_selected_candidate_route_digest": None
        if latest_arbitration is None
        else latest_arbitration.selected_candidate_route_digest,
        "latest_selected_topology_event_digest": None
        if latest_arbitration is None
        else latest_arbitration.selected_topology_event_digest,
        "semantic_choice_claim_allowed": False,
        "agency_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "biological_claim_allowed": False,
        "unrestricted_movement_claim_allowed": False,
    }


def _topology_state_reabsorption_should_emit(state: LGRC9V3RuntimeState) -> bool:
    if bool(state.causal_modes.get("causal_topology_state_reabsorption_enabled", False)):
        return True
    if state.topology_state_reabsorption_log:
        return True
    policy = state.causal_modes.get("causal_topology_state_reabsorption_policy")
    return bool(policy and policy != LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED)


def _native_route_arbitration_should_emit(state: LGRC9V3RuntimeState) -> bool:
    if bool(state.causal_modes.get("native_lgrc_route_arbitration_enabled", False)):
        return True
    if (
        state.native_route_candidate_log
        or state.native_route_candidate_set_log
        or state.native_route_arbitration_log
    ):
        return True
    return False


def _pulse_substrate_surface_should_emit(state: LGRC9V3RuntimeState) -> bool:
    if bool(state.causal_modes.get("causal_pulse_substrate_surface_enabled", False)):
        return True
    if state.causal_pulse_substrate_surface_log:
        return True
    production_log = state.cached_quantities.get(
        LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
        [],
    )
    surface_producer_policies = {
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
    }
    if isinstance(production_log, Sequence) and not isinstance(production_log, str):
        return any(
            isinstance(result, Mapping)
            and result.get("producer_policy") in surface_producer_policies
            for result in production_log
        )
    return False


def classify_lgrc9v3_step_extension(
    model_or_state: LGRC9V3 | LGRC9V3RuntimeState,
) -> Mapping[str, Any]:
    """Return the LGRC9V3 step/checkpoint clock extension."""

    state = _runtime_state_from_model_or_state(model_or_state)
    extension: dict[str, Any] = {
        "contract_version": LGRC9V3_TELEMETRY_CONTRACT_VERSION,
        "step_extension_schema_version": LGRC9V3_STEP_EXTENSION_SCHEMA_VERSION,
        "runtime_state_schema_version": LGRC9V3_RUNTIME_STATE_SCHEMA_VERSION,
        "runtime_family": "LGRC9V3",
        "causal_layer_mode": state.causal_layer_mode,
        "lgrc_runtime_level": state.lgrc_runtime_level,
        "scheduler_event_index": int(state.scheduler_event_index),
        "checkpoint_index": int(state.checkpoint_index),
        "event_time_key": float(state.event_time_key),
        "node_proper_time": _string_keyed_float_map(state.node_proper_time),
        "node_last_update_event_time_key": _string_keyed_float_map(
            state.node_last_update_event_time_key
        ),
        "edge_causal_delay": _string_keyed_float_map(state.edge_causal_delay),
        "lapse": _string_keyed_float_map(state.lapse),
        "packet_ledger": _packet_ledger_surface(state),
        "packet_loop": _packet_loop_surface(state),
        "topology_event_count": len(state.topology_event_log),
        "local_update_count": len(state.local_update_log),
        "causal_spark_evaluation_index": int(state.causal_spark_evaluation_index),
        "causal_spark_diagnostic_count": len(state.causal_spark_diagnostic_log),
        "boundary_birth_trial_queue_length": len(state.boundary_birth_trial_queue),
    }
    if _pulse_substrate_surface_should_emit(state):
        extension["causal_pulse_substrate_surface"] = _pulse_substrate_surface(state)
    if _topology_state_reabsorption_should_emit(state):
        extension["topology_state_reabsorption"] = (
            _topology_state_reabsorption_surface(state)
        )
    if _native_route_arbitration_should_emit(state):
        extension["native_route_arbitration"] = _native_route_arbitration_surface(
            state
        )
    return extension


def lgrc9v3_step_family_extensions(
    model_or_state: LGRC9V3 | LGRC9V3RuntimeState,
) -> TelemetryFamilyExtensions:
    """Wrap one LGRC9V3 step extension under the family key."""

    return {
        LGRC9V3_TELEMETRY_FAMILY: classify_lgrc9v3_step_extension(model_or_state)
    }


def lgrc9v3_run_summary_family_extensions(
    model_or_state: LGRC9V3 | LGRC9V3RuntimeState,
) -> TelemetryFamilyExtensions:
    """Return a compact LGRC9V3 run-summary extension from current runtime state."""

    state = _runtime_state_from_model_or_state(model_or_state)
    step_extension = classify_lgrc9v3_step_extension(state)
    summary = {
        "contract_version": LGRC9V3_TELEMETRY_CONTRACT_VERSION,
        "run_summary_extension_schema_version": (
            LGRC9V3_RUN_SUMMARY_EXTENSION_SCHEMA_VERSION
        ),
        "runtime_family": "LGRC9V3",
        "final_causal_clock": {
            "scheduler_event_index": step_extension["scheduler_event_index"],
            "checkpoint_index": step_extension["checkpoint_index"],
            "event_time_key": step_extension["event_time_key"],
        },
        "final_packet_ledger": step_extension["packet_ledger"],
        "final_packet_loop": step_extension["packet_loop"],
        "topology_event_count": step_extension["topology_event_count"],
        "causal_spark_diagnostic_count": step_extension[
            "causal_spark_diagnostic_count"
        ],
    }
    if "causal_pulse_substrate_surface" in step_extension:
        summary["final_causal_pulse_substrate_surface"] = step_extension[
            "causal_pulse_substrate_surface"
        ]
    if "topology_state_reabsorption" in step_extension:
        summary["final_topology_state_reabsorption"] = step_extension[
            "topology_state_reabsorption"
        ]
    if "native_route_arbitration" in step_extension:
        summary["final_native_route_arbitration"] = step_extension[
            "native_route_arbitration"
        ]
    return {
        LGRC9V3_TELEMETRY_FAMILY: summary
    }


def _node_records(state: LGRC9V3RuntimeState) -> tuple[Mapping[str, Any], ...]:
    base_state = state.base_state
    records: list[Mapping[str, Any]] = []
    for node_id in sorted(base_state.topology.iter_live_node_ids()):
        node_state = base_state.nodes.get(node_id)
        records.append(
            {
                "node_id": int(node_id),
                "payload": dict(base_state.topology.node_payload(node_id)),
                "coherence": None if node_state is None else float(node_state.coherence),
                "basin_id": None if node_state is None else node_state.basin_id,
                "parent_id": None if node_state is None else node_state.parent_id,
                "depth": None if node_state is None else int(node_state.depth),
                "node_proper_time": float(state.node_proper_time.get(node_id, 0.0)),
                "node_last_update_proper_time": float(
                    state.node_last_update_proper_time.get(node_id, 0.0)
                ),
                "node_last_update_event_time_key": float(
                    state.node_last_update_event_time_key.get(node_id, 0.0)
                ),
                "lapse": float(state.lapse.get(node_id, 1.0)),
            }
        )
    return tuple(records)


def _edge_records(state: LGRC9V3RuntimeState) -> tuple[Mapping[str, Any], ...]:
    base_state = state.base_state
    records: list[Mapping[str, Any]] = []
    for edge_id in sorted(base_state.topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = base_state.topology.edge_ports(edge_id)
        port_edge = base_state.port_edges.get(edge_id)
        if port_edge is None:
            source_node_id, source_slot = endpoint_a
            target_node_id, target_slot = endpoint_b
            source_port_id = slot_to_port_id(int(source_slot))
            target_port_id = slot_to_port_id(int(target_slot))
            conductance = None
            flux_uv = None
        else:
            source_node_id = int(port_edge.node_u)
            target_node_id = int(port_edge.node_v)
            source_port_id = int(port_edge.port_u)
            target_port_id = int(port_edge.port_v)
            conductance = float(port_edge.conductance)
            flux_uv = float(port_edge.flux_uv)
        records.append(
            {
                "edge_id": int(edge_id),
                "source_node_id": int(source_node_id),
                "source_port_id": int(source_port_id),
                "target_node_id": int(target_node_id),
                "target_port_id": int(target_port_id),
                "payload": dict(base_state.topology.edge_payload(edge_id)),
                "conductance": conductance,
                "flux_uv": flux_uv,
                "base_conductance": base_state.base_conductance.get(edge_id),
                "geometric_length": base_state.geometric_length.get(edge_id),
                "temporal_delay": base_state.temporal_delay.get(edge_id),
                "edge_causal_delay": state.edge_causal_delay.get(edge_id),
            }
        )
    return tuple(records)


def _topology_event_records(state: LGRC9V3RuntimeState) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    for event in state.topology_event_log:
        if isinstance(event, GRCEvent):
            records.append(
                {
                    "kind": event.kind,
                    "step_index": int(event.step_index),
                    "payload": dict(event.payload),
                    "source_family": event.source_family,
                }
            )
        else:
            records.append(dict(event))
    return records


def build_lgrc9v3_graph_checkpoint(
    model_or_state: LGRC9V3 | LGRC9V3RuntimeState,
    *,
    identity: RunTelemetryIdentity,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str | None = None,
    event_count_window: int = 0,
    event_counts_by_kind_window: Mapping[str, int] | None = None,
) -> GraphCheckpointArtifact:
    """Build one graph checkpoint with LGRC9V3 causal runtime overlays."""

    state = _runtime_state_from_model_or_state(model_or_state)
    nodes = _node_records(state)
    edges = _edge_records(state)
    runtime_artifact = state.to_artifact()
    family_extension = {
        "contract_version": LGRC9V3_TELEMETRY_CONTRACT_VERSION,
        "checkpoint_schema_version": LGRC9V3_GRAPH_CHECKPOINT_SCHEMA_VERSION,
        "checkpoint_surface": LGRC9V3_GRAPH_CHECKPOINT_SURFACE,
        "runtime_state_schema_version": LGRC9V3_RUNTIME_STATE_SCHEMA_VERSION,
        "causal_layer_mode": state.causal_layer_mode,
        "lgrc_runtime_level": state.lgrc_runtime_level,
        "causal_clocks": {
            "scheduler_event_index": int(state.scheduler_event_index),
            "checkpoint_index": int(state.checkpoint_index),
            "event_time_key": float(state.event_time_key),
            "node_proper_time": _string_keyed_float_map(state.node_proper_time),
            "node_last_update_proper_time": _string_keyed_float_map(
                state.node_last_update_proper_time
            ),
            "node_last_update_event_time_key": _string_keyed_float_map(
                state.node_last_update_event_time_key
            ),
            "lapse": _string_keyed_float_map(state.lapse),
        },
        "edge_causal_delay": _string_keyed_float_map(state.edge_causal_delay),
        "packet_ledger": runtime_artifact["packet_ledger"],
        "packet_loop": _packet_loop_surface(state),
        "cached_quantities": dict(runtime_artifact.get("cached_quantities", {})),
        "event_queue_records": runtime_artifact["event_queue_records"],
        "packet_processing_log": runtime_artifact["packet_processing_log"],
        "arrival_eligibility_log": runtime_artifact["arrival_eligibility_log"],
        "local_update_log": runtime_artifact["local_update_log"],
        "causal_flux_routes": runtime_artifact["causal_flux_routes"],
        "causal_spark": {
            "causal_spark_evaluation_index": int(
                state.causal_spark_evaluation_index
            ),
            "causal_spark_diagnostic_log": list(
                runtime_artifact["causal_spark_diagnostic_log"]
            ),
        },
        "topology_history": {
            "topology_event_count": len(state.topology_event_log),
            "topology_event_log": _topology_event_records(state),
        },
        "boundary_birth_trial_queue": list(runtime_artifact["boundary_birth_trial_queue"]),
        "runtime_state": runtime_artifact,
    }
    if _pulse_substrate_surface_should_emit(state):
        family_extension["causal_pulse_substrate_surface"] = (
            _pulse_substrate_surface(state)
        )
        family_extension["causal_pulse_substrate_surface_log"] = runtime_artifact[
            "causal_pulse_substrate_surface_log"
        ]
        if bool(
            state.causal_modes.get(
                "causal_pulse_substrate_surface_lineage_transport_enabled",
                False,
            )
        ):
            family_extension["causal_pulse_substrate_surface_lineage_log"] = (
                runtime_artifact["causal_pulse_substrate_surface_lineage_log"]
            )
    if _topology_state_reabsorption_should_emit(state):
        family_extension["topology_state_reabsorption"] = (
            _topology_state_reabsorption_surface(state)
        )
        family_extension["topology_state_reabsorption_log"] = runtime_artifact[
            "topology_state_reabsorption_log"
        ]
    if _native_route_arbitration_should_emit(state):
        family_extension["native_route_arbitration"] = (
            _native_route_arbitration_surface(state)
        )
        family_extension["native_route_candidate_log"] = runtime_artifact[
            "native_route_candidate_log"
        ]
        family_extension["native_route_candidate_set_log"] = runtime_artifact[
            "native_route_candidate_set_log"
        ]
        family_extension["native_route_arbitration_log"] = runtime_artifact[
            "native_route_arbitration_log"
        ]
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=int(state.scheduler_event_index),
        time=float(state.event_time_key),
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        graph_kind="port_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=nodes,
        edge_records=edges,
        event_count_window=int(event_count_window),
        event_counts_by_kind_window={}
        if event_counts_by_kind_window is None
        else dict(event_counts_by_kind_window),
        flow_representation="packetized_causal_flux",
        flow_cadence="event_queue",
        layout_mode="port_graph",
        layout_dimensions=2,
        label_computation_modes={
            "causal_clock": "runtime_state",
            "packet_ledger": "runtime_state",
            "topology_history": "runtime_state",
        },
        topology_extensions={
            "runtime_family": "LGRC9V3",
            "base_runtime_family": "GRC9V3",
            "next_node_id": int(state.base_state.topology.next_node_id),
            "next_edge_id": int(state.base_state.topology.next_edge_id),
        },
        family_extensions={LGRC9V3_TELEMETRY_FAMILY: family_extension},
    )


__all__ = [
    "LGRC9V3_EVENT_DOMAIN_COLLAPSE",
    "LGRC9V3_EVENT_DOMAIN_IDENTITY",
    "LGRC9V3_EVENT_DOMAIN_LOCAL_UPDATE",
    "LGRC9V3_EVENT_DOMAIN_OTHER",
    "LGRC9V3_EVENT_DOMAIN_PACKET",
    "LGRC9V3_EVENT_DOMAIN_PULSE_SUBSTRATE_SURFACE",
    "LGRC9V3_EVENT_DOMAIN_SELF_REARM",
    "LGRC9V3_EVENT_DOMAIN_SPARK",
    "LGRC9V3_EVENT_DOMAIN_TOPOLOGY",
    "LGRC9V3_EVENT_EXTENSION_SCHEMA_VERSION",
    "LGRC9V3_GRAPH_CHECKPOINT_SCHEMA_VERSION",
    "LGRC9V3_GRAPH_CHECKPOINT_SURFACE",
    "LGRC9V3_RUN_SUMMARY_EXTENSION_SCHEMA_VERSION",
    "LGRC9V3_STEP_EXTENSION_SCHEMA_VERSION",
    "LGRC9V3_TELEMETRY_CONTRACT_VERSION",
    "LGRC9V3_TELEMETRY_FAMILY",
    "build_lgrc9v3_graph_checkpoint",
    "classify_lgrc9v3_event_extension",
    "classify_lgrc9v3_step_extension",
    "lgrc9v3_event_family_extensions",
    "lgrc9v3_event_family_extensions_for_events",
    "lgrc9v3_run_summary_family_extensions",
    "lgrc9v3_step_family_extensions",
]
