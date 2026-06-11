"""Executable LGRC9V3 runtime shell for event-queue orchestration."""

from __future__ import annotations

from copy import deepcopy
import math
import random
from collections.abc import Mapping, Sequence
from typing import Any

from pygrc.core import (
    CAUSAL_LAYER,
    digest_canonical_data,
    GRCEvent,
    GRCModel,
    GRCParams,
    InvalidParamsError,
    InvalidStateTransitionError,
    SnapshotCompatibilityError,
    StepResult,
    build_snapshot_metadata,
    build_standard_snapshot,
    load_snapshot,
    require_snapshot_family,
    save_snapshot,
)

from .grc_9_v3 import GRC9V3
from .grc_9_ports import port_id_to_slot
from .grc_9_v3_sparks import (
    apply_mechanical_expansion,
    detect_hybrid_spark_candidates,
    evaluate_child_basin_stabilization,
    invalidate_previous_column_h_cache,
    register_completed_hybrid_spark,
)
from .grc_9_v3_state import GRC9V3NodeState, GRC9V3State
from .grc_9_state import PortEdge
from .lgrc_9_v3_contract import (
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC2,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3AutonomousProductionResult,
    LGRC9V3AutonomousProductionRecord,
    LGRC9V3CausalPulseSubstrateSurfaceLineageRecord,
    LGRC9V3CausalPulseSubstrateSurfaceRow,
    LGRC9V3NativeRouteArbitrationRecord,
    LGRC9V3NativeRouteCandidateRecord,
    LGRC9V3NativeRouteCandidateSetRecord,
    LGRC9V3RouteAspect,
    LGRC9V3TopologyStateReabsorptionRecord,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_BOUNDARY_BIRTH_TRIAL_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PACKET_DEPARTURE_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD,
    LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1,
    LGRC9V3_AUTONOMY_MODE_VERSION,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_DERIVED_SURFACE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
    LGRC9V3_DEFAULT_CAUSAL_MODES,
    LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_DECLARED_LOCAL_PREFERENCE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_SELECTED_REASON_CODES,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID,
    LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_DECLARED_TIEBREAKER,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER,
    build_lgrc9v3_autonomous_production_record_id,
    build_lgrc9v3_autonomous_surface_digest,
    build_lgrc9v3_causal_pulse_substrate_surface_digest,
    build_lgrc9v3_disabled_autonomous_production_result,
    build_lgrc9v3_native_route_arbitration_record_digest,
    build_lgrc9v3_native_route_candidate_record_digest,
    build_lgrc9v3_native_route_candidate_set_record_digest,
    build_lgrc9v3_topology_event_digest,
    build_lgrc9v3_topology_state_reabsorption_record_digest,
    restore_lgrc9v3_causal_pulse_substrate_surface_lineage_record_artifact,
    restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact,
    restore_lgrc9v3_native_route_arbitration_record_artifact,
    restore_lgrc9v3_native_route_candidate_record_artifact,
    restore_lgrc9v3_native_route_candidate_set_record_artifact,
    restore_lgrc9v3_route_aspect_artifact,
    restore_lgrc9v3_topology_state_reabsorption_record_artifact,
    validate_lgrc9v3_autonomous_producer_policy,
    validate_lgrc9v3_causal_modes,
    validate_lgrc9v3_route_aspect,
)
from .lgrc_9_v3_identity import (
    emit_lgrc9v3_proper_time_identity_acceptance,
)
from .lgrc_9_v3_packets import (
    LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
    build_lgrc9v3_packet_ledger,
    derive_lgrc9v3_packet_arrival_eligibility,
    derive_lgrc9v3_packet_arrival_event_time_key,
    process_lgrc9v3_next_packet_event,
    schedule_lgrc9v3_packet_departure,
)
from .lgrc_9_v3_timing import (
    compute_lgrc9v3_edge_causal_delay,
    compute_lgrc9v3_lapse_by_node,
)
from .lgrc_9_v3_topology import (
    LGRC9V3_TOPOLOGY_EVENT_KIND_BOUNDARY_BIRTH,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
    LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
    build_lgrc9v3_collapse_reabsorption_event_id,
    process_lgrc9v3_collapse_reabsorption,
    process_lgrc9v3_proper_time_inheritance,
    transport_lgrc9v3_packets_through_collapse_reabsorption,
    transport_lgrc9v3_packets_through_refinement,
)
from .lgrc_9_v3_runtime_state import (
    LGRC9V3RuntimeState,
    restore_lgrc9v3_event_record,
    restore_lgrc9v3_runtime_state_artifact,
    with_ordered_lgrc9v3_event_queue,
)


LGRC9V3_RUNTIME_EVENT_SCHEMA_VERSION = "lgrc9v3_runtime_event_v1"
LGRC9V3_LOCAL_UPDATE_EVENT_KIND = "lgrc9v3_local_update"
LGRC9V3_LOCAL_UPDATE_EVENT_SCHEMA_VERSION = "lgrc9v3_local_update_event_v1"
LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND = "lgrc9v3_causal_spark_candidate"
LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_SCHEMA_VERSION = (
    "lgrc9v3_causal_spark_candidate_event_v1"
)
LGRC9V3_CAUSAL_SPARK_DIAGNOSTIC_SOURCE = (
    "captured_grc9v3_spark_candidate_payload"
)
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND = LGRC9V3_TOPOLOGY_EVENT_KIND_BOUNDARY_BIRTH
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_SCHEMA_VERSION = (
    "lgrc9v3_causal_boundary_birth_event_v1"
)
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_TRIAL_EVENT_KIND = (
    "lgrc9v3_causal_boundary_birth_trial"
)
LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY = (
    "lgrc9v3_route_aspect_surplus_trigger_config"
)
LGRC9V3_PULSE_SUBSTRATE_COUPLING_CONFIG_KEY = (
    "lgrc9v3_pulse_substrate_coupling_config"
)
LGRC9V3_FEEDBACK_COUPLED_PULSE_CONFIG_KEY = (
    "lgrc9v3_feedback_coupled_pulse_config"
)
LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND = "lgrc9v3_self_rearm_evidence"
LGRC9V3_SELF_REARM_EVIDENCE_EVENT_SCHEMA_VERSION = (
    "lgrc9v3_self_rearm_evidence_event_v1"
)
LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY = "lgrc9v3_self_rearm_evidence_log"
LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY = "lgrc9v3_autonomous_production_log"


def _runtime_default_modes(
    modes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    resolved = dict(LGRC9V3_DEFAULT_CAUSAL_MODES)
    resolved.update(
        {
            "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY,
            "proper_time_accumulation_policy": PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER,
            "require_fixed_topology_for_lgrc2": True,
        }
    )
    if modes is not None:
        resolved.update(dict(modes))
    return validate_lgrc9v3_causal_modes(resolved)


def _event_record_payload(record: object) -> dict[str, Any]:
    to_record = getattr(record, "to_record", None)
    if callable(to_record):
        return dict(to_record())
    raise TypeError("event record must expose to_record()")


def _packet_event_payloads_by_id(
    events: Sequence[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    payloads: dict[str, Mapping[str, Any]] = {}
    for event in events:
        if event.get("kind") not in {
            LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
        }:
            continue
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            continue
        processed_event = payload.get("processed_event")
        if not isinstance(processed_event, Mapping):
            continue
        event_id = processed_event.get("event_id")
        if isinstance(event_id, str) and event_id:
            payloads[event_id] = payload
    return payloads


def _self_rearm_payloads(
    events: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    payloads: list[Mapping[str, Any]] = []
    for event in events:
        if event.get("kind") != LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND:
            continue
        payload = event.get("payload")
        if isinstance(payload, Mapping):
            payloads.append(payload)
    return payloads


def _causal_pulse_substrate_surface_payloads(
    events: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    payloads: list[Mapping[str, Any]] = []
    for event in events:
        if event.get("kind") != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND:
            continue
        payload = event.get("payload")
        if isinstance(payload, Mapping):
            payloads.append(payload)
    return payloads


def _topology_event_payloads(
    events: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    payloads: list[Mapping[str, Any]] = []
    for event in events:
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            continue
        if (
            event.get("kind") in LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS
            and _topology_event_id(payload) is not None
        ):
            payloads.append(payload)
            continue
        if isinstance(payload.get("topology_event_id"), str):
            payloads.append(payload)
    return payloads


def _production_records_by_id(
    production_results: Sequence[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    records: dict[str, Mapping[str, Any]] = {}
    for result in production_results:
        raw_records = result.get("production_records", ())
        if not isinstance(raw_records, Sequence) or isinstance(raw_records, str):
            continue
        for record in raw_records:
            if not isinstance(record, Mapping):
                continue
            record_id = record.get("record_id")
            if isinstance(record_id, str) and record_id:
                records[record_id] = record
    return records


def _surface_producer_results(
    production_results: Sequence[Mapping[str, Any]],
) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    records: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
    for result in production_results:
        if not isinstance(result, Mapping):
            continue
        raw_records = result.get("production_records", ())
        if not isinstance(raw_records, Sequence) or isinstance(raw_records, str):
            continue
        for record in raw_records:
            if isinstance(record, Mapping):
                records.append((result, record))
    return records


def _append_if_false(
    failures: list[str],
    condition: bool,
    reason: str,
) -> None:
    if not condition:
        failures.append(reason)


def _topology_event_id(payload: Mapping[str, Any]) -> str | None:
    for key in ("topology_event_id", "expansion_id", "transport_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
    *,
    events: Sequence[Mapping[str, Any]],
    production_results: Sequence[Mapping[str, Any]] = (),
    budget_tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Validate native pulse-substrate surface rows from artifacts only.

    The validator links each serialized surface row to a committed packet event
    already present in the event stream. Future producer records may reference
    the row, but they must occur after the committed source event.
    """

    packet_payloads = _packet_event_payloads_by_id(events)
    surface_payloads = _causal_pulse_substrate_surface_payloads(events)
    producer_results = _surface_producer_results(production_results)
    failures: list[str] = []
    validated_ids: list[str] = []
    surface_digests: set[str] = set()

    if not surface_payloads:
        failures.append("no_causal_pulse_substrate_surface_rows")

    for payload in surface_payloads:
        row_failure_count = len(failures)
        surface_id = str(payload.get("surface_id", "unknown_surface_row"))
        route_digest = payload.get("route_aspect_digest")
        if not isinstance(route_digest, str) or not route_digest:
            failures.append(f"missing_route_aspect_digest:{surface_id}")
            continue
        try:
            row = restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact(payload)
        except (SnapshotCompatibilityError, ValueError) as exc:
            failures.append(f"corrupted_surface_row:{surface_id}:{exc}")
            continue

        source_event = packet_payloads.get(row.pulse_event_id)
        _append_if_false(
            failures,
            source_event is not None,
            f"surface_row_without_committed_source_event:{row.surface_id}",
        )
        if source_event is None:
            continue

        processed = source_event.get("processed_event")
        if not isinstance(processed, Mapping):
            failures.append(f"source_event_missing_processed_payload:{row.pulse_event_id}")
            continue
        _append_if_false(
            failures,
            processed.get("event_id") == row.pulse_event_id,
            f"source_event_id_mismatch:{row.surface_id}",
        )
        _append_if_false(
            failures,
            processed.get("event_kind") == row.pulse_event_kind,
            f"source_event_kind_mismatch:{row.surface_id}",
        )
        _append_if_false(
            failures,
            row.pulse_event_kind
            in {
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            },
            f"unsupported_surface_source_event_kind:{row.surface_id}",
        )
        _append_if_false(
            failures,
            processed.get("packet_id") == row.pulse_packet_id,
            f"source_packet_mismatch:{row.surface_id}",
        )
        _append_if_false(
            failures,
            int(processed.get("scheduler_event_index", -1))
            < int(row.scheduler_event_index),
            f"surface_not_after_source_event:{row.surface_id}",
        )
        _append_if_false(
            failures,
            float(processed.get("event_time_key", -1.0)) <= float(row.event_time_key),
            f"surface_event_time_before_source:{row.surface_id}",
        )
        contact_node_id = (
            row.target_node_id
            if row.pulse_event_kind == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL
            else row.source_node_id
        )
        _append_if_false(
            failures,
            math.isclose(
                float(row.node_proper_time.get(contact_node_id, -1.0)),
                float(row.event_time_key),
                rel_tol=0.0,
                abs_tol=budget_tolerance,
            ),
            f"surface_proper_time_mismatch:{row.surface_id}",
        )
        _append_if_false(
            failures,
            abs(float(source_event.get("budget_error", 0.0))) <= budget_tolerance,
            f"source_budget_error:{row.pulse_event_id}",
        )
        _append_if_false(
            failures,
            abs(float(row.surface_budget_error)) <= budget_tolerance,
            f"surface_budget_error:{row.surface_id}",
        )
        _append_if_false(
            failures,
            not any(bool(value) for value in row.claim_flags.values()),
            f"surface_row_promoted_claim:{row.surface_id}",
        )

        for producer_result, producer_record in producer_results:
            if producer_record.get("causal_surface_digest") != row.surface_digest:
                continue
            record_id = str(producer_record.get("record_id", "unknown_producer"))
            producer_scheduler = int(producer_result.get("scheduler_event_index", -1))
            source_scheduler = int(processed.get("scheduler_event_index", -1))
            reason_code = producer_record.get("reason_code")
            _append_if_false(
                failures,
                isinstance(reason_code, str) and bool(reason_code),
                f"producer_missing_reason_code:{record_id}",
            )
            producer_evidence = producer_record.get("observed_evidence", {})
            if not isinstance(producer_evidence, Mapping):
                failures.append(f"producer_evidence_not_mapping:{record_id}")
                continue
            for mutation_key in (
                "direct_coherence_write",
                "direct_support_mask_write",
                "direct_centroid_write",
                "direct_displacement_write",
                "direct_topology_write",
                "direct_claim_write",
                "producer_mutated_coherence",
                "producer_marked_packet_processed",
                "producer_emitted_claim_label",
            ):
                _append_if_false(
                    failures,
                    mutation_key in producer_evidence
                    and producer_evidence.get(mutation_key) is False,
                    f"producer_mutation_boundary_violation:{record_id}:{mutation_key}",
                )
            for claim_key in (
                "movement_claim_allowed",
                "loop_driven_movement_claim_allowed",
                "locomotion_like_claim_allowed",
                "adaptive_topology_entry_allowed",
                "native_m6",
            ):
                if claim_key in producer_evidence:
                    _append_if_false(
                        failures,
                        producer_evidence.get(claim_key) is False,
                        f"producer_claim_promotion:{record_id}:{claim_key}",
                    )
            _append_if_false(
                failures,
                producer_scheduler > source_scheduler,
                f"producer_record_before_source_commitment:{row.surface_id}",
            )
            scheduled_event_id = producer_record.get("scheduled_event_id")
            if isinstance(scheduled_event_id, str) and scheduled_event_id:
                scheduled_payload = packet_payloads.get(scheduled_event_id)
                _append_if_false(
                    failures,
                    scheduled_payload is not None,
                    f"missing_scheduled_packet_event:{scheduled_event_id}",
                )

        surface_digests.add(str(row.surface_digest))
        if len(failures) == row_failure_count:
            validated_ids.append(row.surface_id)

    for _, producer_record in producer_results:
        digest = producer_record.get("causal_surface_digest")
        if isinstance(digest, str) and digest and digest not in surface_digests:
            record_id = str(producer_record.get("record_id", "unknown_producer"))
            failures.append(f"orphaned_producer_surface_reference:{record_id}")

    return {
        "validator": "validate_lgrc9v3_causal_pulse_substrate_surface_artifacts",
        "valid": not failures,
        "surface_row_count": len(surface_payloads),
        "validated_surface_ids": validated_ids,
        "failure_reasons": failures,
        "movement_claim_allowed": False,
        "native_m6": False,
        "native_lgrc_pulse_substrate_supported": not failures,
    }


def validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
    *,
    events: Sequence[Mapping[str, Any]],
    surface_lineage_records: Sequence[Mapping[str, Any]],
    surface_rows: Sequence[Mapping[str, Any]] = (),
    topology_events: Sequence[Mapping[str, Any]] = (),
    topology_state_reabsorption_records: Sequence[Mapping[str, Any]] = (),
    production_results: Sequence[Mapping[str, Any]] = (),
    budget_tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Validate native surface-lineage replay from artifacts only.

    The validator reconstructs source surface rows, committed topology events,
    lineage records, transported successor rows, and any producer records
    without reading live runtime state.
    """

    surface_replay_events = [*events]
    for row in surface_rows:
        if (
            isinstance(row.get("surface_values_after"), Mapping)
            and "transported_by_topology_event_digest" in row["surface_values_after"]
        ):
            continue
        surface_replay_events.append(
            {
                "kind": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
                "payload": row,
            }
        )
    surface_validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=surface_replay_events,
        budget_tolerance=budget_tolerance,
    )
    failures: list[str] = [
        f"surface_replay:{reason}"
        for reason in surface_validation.get("failure_reasons", ())
    ]
    surface_rows_by_digest: dict[str, LGRC9V3CausalPulseSubstrateSurfaceRow] = {}
    surface_ids: dict[str, LGRC9V3CausalPulseSubstrateSurfaceRow] = {}
    surface_payloads = [
        *_causal_pulse_substrate_surface_payloads(events),
        *surface_rows,
    ]
    for payload in surface_payloads:
        surface_id = str(payload.get("surface_id", "unknown_surface_row"))
        try:
            row = restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact(payload)
        except (SnapshotCompatibilityError, ValueError) as exc:
            failures.append(f"corrupted_surface_row:{surface_id}:{exc}")
            continue
        surface_rows_by_digest[str(row.surface_digest)] = row
        surface_ids[row.surface_id] = row

    topology_events_by_id: dict[str, Mapping[str, Any]] = {}
    topology_events_by_digest: dict[str, Mapping[str, Any]] = {}
    topology_payloads = [
        *_topology_event_payloads(events),
        *topology_events,
    ]
    for payload in topology_payloads:
        event_id = _topology_event_id(payload)
        if event_id is None:
            continue
        digest = build_lgrc9v3_topology_event_digest(payload)
        topology_events_by_id[event_id] = payload
        topology_events_by_digest[digest] = payload

    lineage_records: list[LGRC9V3CausalPulseSubstrateSurfaceLineageRecord] = []
    reabsorption_records: list[LGRC9V3TopologyStateReabsorptionRecord] = []
    reabsorption_by_topology_and_map: dict[
        tuple[str, tuple[tuple[str, str], ...]],
        LGRC9V3TopologyStateReabsorptionRecord,
    ] = {}
    reabsorption_by_digest: dict[str, LGRC9V3TopologyStateReabsorptionRecord] = {}
    seen_reabsorption_keys: set[str] = set()
    seen_lineage_keys: set[str] = set()
    transported_source_digests: set[str] = set()
    superseded_source_digests: set[str] = set()
    transported_successor_by_source_digest: dict[str, str] = {}
    lineage_scheduler_by_source_digest: dict[str, int] = {}
    lineage_schedulers_by_source_digest: dict[str, list[int]] = {}
    packet_payloads = _packet_event_payloads_by_id(events)
    validated_record_ids: list[str] = []
    transported_count = 0
    superseded_count = 0

    if not surface_lineage_records:
        failures.append("no_surface_lineage_records")

    for artifact in topology_state_reabsorption_records:
        raw_id = str(
            artifact.get(
                "topology_state_reabsorption_record_id",
                "unknown_topology_state_reabsorption",
            )
        )
        try:
            record = restore_lgrc9v3_topology_state_reabsorption_record_artifact(
                artifact
            )
        except (SnapshotCompatibilityError, ValueError) as exc:
            failures.append(f"corrupted_topology_state_reabsorption_record:{raw_id}:{exc}")
            continue
        reabsorption_records.append(record)
        if record.idempotency_key in seen_reabsorption_keys:
            failures.append(
                "duplicate_topology_state_reabsorption_record:"
                f"{record.idempotency_key}"
            )
            continue
        seen_reabsorption_keys.add(str(record.idempotency_key))
        topology = topology_events_by_digest.get(record.topology_event_digest)
        if topology is None:
            if record.topology_event_id in topology_events_by_id:
                failures.append(
                    "topology_state_reabsorption_topology_digest_mismatch:"
                    f"{record.topology_state_reabsorption_record_id}"
                )
            else:
                failures.append(
                    "topology_state_reabsorption_unknown_topology_event:"
                    f"{record.topology_state_reabsorption_record_id}"
                )
            continue
        _append_if_false(
            failures,
            _topology_event_id(topology) == record.topology_event_id,
            "topology_state_reabsorption_topology_id_mismatch:"
            f"{record.topology_state_reabsorption_record_id}",
        )
        _append_if_false(
            failures,
            topology.get("topology_event_kind") == record.topology_event_kind,
            "topology_state_reabsorption_topology_kind_mismatch:"
            f"{record.topology_state_reabsorption_record_id}",
        )
        _append_if_false(
            failures,
            int(record.scheduler_event_index)
            >= int(topology.get("scheduler_event_index", -1)),
            "topology_state_reabsorption_order_inversion:"
            f"{record.topology_state_reabsorption_record_id}",
        )
        _append_if_false(
            failures,
            abs(float(record.node_plus_packet_budget_error)) <= budget_tolerance,
            "topology_state_reabsorption_budget_discontinuity:"
            f"{record.topology_state_reabsorption_record_id}",
        )
        _append_if_false(
            failures,
            abs(
                float(record.active_node_state_total_after)
                - float(record.packet_ledger_node_total_after)
            )
            <= budget_tolerance,
            "topology_state_reabsorption_active_ledger_mismatch:"
            f"{record.topology_state_reabsorption_record_id}",
        )
        _append_if_false(
            failures,
            not any(bool(value) for value in record.claim_flags.values()),
            "topology_state_reabsorption_promoted_claim:"
            f"{record.topology_state_reabsorption_record_id}",
        )
        map_key = tuple(sorted((str(k), str(v)) for k, v in record.lineage_transfer_map.items()))
        reabsorption_by_topology_and_map[(record.topology_event_digest, map_key)] = (
            record
        )
        reabsorption_by_digest[record.topology_state_reabsorption_digest] = record

    for artifact in surface_lineage_records:
        raw_id = str(artifact.get("surface_lineage_record_id", "unknown_lineage"))
        try:
            record = restore_lgrc9v3_causal_pulse_substrate_surface_lineage_record_artifact(
                artifact
            )
        except (SnapshotCompatibilityError, ValueError) as exc:
            failures.append(f"corrupted_surface_lineage_record:{raw_id}:{exc}")
            continue
        lineage_records.append(record)

        if record.idempotency_key in seen_lineage_keys:
            failures.append(f"duplicate_surface_lineage_record:{record.idempotency_key}")
            continue
        seen_lineage_keys.add(str(record.idempotency_key))

        source = surface_rows_by_digest.get(record.source_surface_digest)
        if source is None:
            failures.append(
                "surface_lineage_unknown_source_surface:"
                f"{record.surface_lineage_record_id}"
            )
            continue
        _append_if_false(
            failures,
            source.surface_id == record.source_surface_id,
            f"surface_lineage_source_id_mismatch:{record.surface_lineage_record_id}",
        )
        _append_if_false(
            failures,
            tuple(source.surface_nodes) == tuple(record.source_surface_nodes),
            f"surface_lineage_source_nodes_mismatch:{record.surface_lineage_record_id}",
        )

        topology = topology_events_by_digest.get(record.topology_event_digest)
        if topology is None:
            if record.topology_event_id in topology_events_by_id:
                failures.append(
                    "surface_lineage_topology_digest_mismatch:"
                    f"{record.surface_lineage_record_id}"
                )
            else:
                failures.append(
                    "surface_lineage_unknown_topology_event:"
                    f"{record.surface_lineage_record_id}"
                )
            continue
        _append_if_false(
            failures,
            _topology_event_id(topology) == record.topology_event_id,
            f"surface_lineage_topology_id_mismatch:{record.surface_lineage_record_id}",
        )
        _append_if_false(
            failures,
            topology.get("topology_event_kind") == record.topology_event_kind,
            f"surface_lineage_topology_kind_mismatch:{record.surface_lineage_record_id}",
        )

        topology_scheduler = int(topology.get("scheduler_event_index", -1))
        _append_if_false(
            failures,
            int(record.scheduler_event_index) >= topology_scheduler
            and int(record.scheduler_event_index) > int(source.scheduler_event_index),
            f"surface_lineage_order_inversion:{record.surface_lineage_record_id}",
        )
        _append_if_false(
            failures,
            float(record.event_time_key) >= float(source.event_time_key),
            f"surface_lineage_event_time_inversion:{record.surface_lineage_record_id}",
        )
        _append_if_false(
            failures,
            abs(float(record.surface_budget_error)) <= budget_tolerance,
            f"surface_lineage_surface_budget_discontinuity:{record.surface_lineage_record_id}",
        )
        _append_if_false(
            failures,
            abs(float(record.node_plus_packet_budget_error)) <= budget_tolerance,
            "surface_lineage_node_plus_packet_budget_discontinuity:"
            f"{record.surface_lineage_record_id}",
        )
        _append_if_false(
            failures,
            not any(bool(value) for value in record.claim_flags.values()),
            f"surface_lineage_promoted_claim:{record.surface_lineage_record_id}",
        )

        if (
            record.lineage_action
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
        ):
            transported_count += 1
            transported_source_digests.add(record.source_surface_digest)
            lineage_scheduler_by_source_digest[record.source_surface_digest] = int(
                record.scheduler_event_index
            )
            lineage_schedulers_by_source_digest.setdefault(
                record.source_surface_digest,
                [],
            ).append(int(record.scheduler_event_index))
            transported = (
                surface_rows_by_digest.get(str(record.transported_surface_digest))
                if record.transported_surface_digest is not None
                else None
            )
            if transported is None:
                failures.append(
                    "transported_surface_row_missing:"
                    f"{record.surface_lineage_record_id}"
                )
                continue
            transported_successor_by_source_digest[record.source_surface_digest] = (
                transported.surface_digest
            )
            _append_if_false(
                failures,
                transported.surface_id == record.transported_surface_id,
                f"transported_surface_id_mismatch:{record.surface_lineage_record_id}",
            )
            _append_if_false(
                failures,
                int(transported.scheduler_event_index)
                == int(record.scheduler_event_index),
                f"transported_surface_order_mismatch:{record.surface_lineage_record_id}",
            )
            _append_if_false(
                failures,
                tuple(transported.surface_nodes) == tuple(record.target_surface_nodes),
                f"transported_surface_target_nodes_mismatch:{record.surface_lineage_record_id}",
            )
            _append_if_false(
                failures,
                transported.surface_values_before.get("transported_from_surface_digest")
                == record.source_surface_digest,
                f"transported_surface_source_digest_mismatch:{record.surface_lineage_record_id}",
            )
            _append_if_false(
                failures,
                transported.surface_values_after.get(
                    "transported_by_topology_event_digest"
                )
                == record.topology_event_digest,
                f"transported_surface_topology_digest_mismatch:{record.surface_lineage_record_id}",
            )
            if topology_state_reabsorption_records:
                map_key = tuple(
                    sorted(
                        (str(k), str(v))
                        for k, v in record.lineage_transfer_map.items()
                    )
                )
                _append_if_false(
                    failures,
                    (record.topology_event_digest, map_key)
                    in reabsorption_by_topology_and_map,
                    "transported_surface_missing_topology_state_reabsorption:"
                    f"{record.surface_lineage_record_id}",
                )
        else:
            superseded_count += 1
            superseded_source_digests.add(record.source_surface_digest)
            lineage_scheduler_by_source_digest[record.source_surface_digest] = int(
                record.scheduler_event_index
            )
            lineage_schedulers_by_source_digest.setdefault(
                record.source_surface_digest,
                [],
            ).append(int(record.scheduler_event_index))
            _append_if_false(
                failures,
                record.superseded_surface_id == source.surface_id,
                f"superseded_surface_id_mismatch:{record.surface_lineage_record_id}",
            )
            _append_if_false(
                failures,
                record.producer_stale_read_blocker
                == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
                f"superseded_surface_missing_stale_read_blocker:{record.surface_lineage_record_id}",
            )
        validated_record_ids.append(record.surface_lineage_record_id)

    for producer_result, producer_record in _surface_producer_results(
        production_results
    ):
        record_id = str(producer_record.get("record_id", "unknown_producer"))
        causal_digest = producer_record.get("causal_surface_digest")
        producer_scheduler = int(producer_result.get("scheduler_event_index", -1))
        if (
            causal_digest not in superseded_source_digests
            and causal_digest not in transported_source_digests
            and causal_digest not in set(transported_successor_by_source_digest.values())
        ):
            continue
        reason = producer_record.get("reason_code")
        scheduled_event_id = producer_record.get("scheduled_event_id")
        later_lineage_schedulers = [
            scheduler
            for scheduler in lineage_schedulers_by_source_digest.get(
                str(causal_digest),
                [],
            )
            if producer_scheduler >= scheduler
        ]
        if causal_digest in superseded_source_digests and later_lineage_schedulers:
            if (
                reason != LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED
                or (isinstance(scheduled_event_id, str) and scheduled_event_id)
            ):
                failures.append(f"stale_producer_record_after_lineage:{record_id}")
            continue
        if causal_digest in transported_source_digests and later_lineage_schedulers:
            failures.append(f"producer_used_source_surface_after_transport:{record_id}")
            continue
        source_for_successor = next(
            (
                source_digest
                for source_digest, successor_digest in (
                    transported_successor_by_source_digest.items()
                )
                if successor_digest == causal_digest
            ),
            None,
        )
        if source_for_successor is not None:
            _append_if_false(
                failures,
                producer_scheduler
                > lineage_scheduler_by_source_digest.get(source_for_successor, -1),
                f"producer_record_before_transported_surface:{record_id}",
            )
            if isinstance(scheduled_event_id, str) and scheduled_event_id:
                evidence = producer_record.get("observed_evidence", {})
                if not isinstance(evidence, Mapping):
                    evidence = {}
                reabsorption_digest = evidence.get(
                    "topology_state_reabsorption_record_digest"
                )
                _append_if_false(
                    failures,
                    isinstance(reabsorption_digest, str)
                    and reabsorption_digest in reabsorption_by_digest,
                    "producer_missing_topology_state_reabsorption_digest:"
                    f"{record_id}",
                )
                if isinstance(reabsorption_digest, str):
                    record = reabsorption_by_digest.get(reabsorption_digest)
                    if record is not None:
                        _append_if_false(
                            failures,
                            record.topology_event_digest
                            == evidence.get("topology_event_digest"),
                            "producer_topology_state_reabsorption_digest_mismatch:"
                            f"{record_id}",
                        )
                scheduled_payload = packet_payloads.get(scheduled_event_id)
                if scheduled_payload is None:
                    failures.append(f"missing_scheduled_packet_event:{scheduled_event_id}")
                    continue
                processed = scheduled_payload.get("processed_event")
                if not isinstance(processed, Mapping):
                    failures.append(
                        f"scheduled_packet_missing_processed_payload:{scheduled_event_id}"
                    )
                    continue
                _append_if_false(
                    failures,
                    int(processed.get("scheduler_event_index", -1))
                    > producer_scheduler,
                    f"scheduled_packet_before_producer_record:{record_id}",
                )
                _append_if_false(
                    failures,
                    abs(float(scheduled_payload.get("budget_error", 0.0)))
                    <= budget_tolerance,
                    f"scheduled_packet_budget_error:{scheduled_event_id}",
                )

    return {
        "validator": (
            "validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts"
        ),
        "artifact_only": True,
        "runtime_state_used": False,
        "topology_state_reabsorption_digest_fields_checked": bool(
            reabsorption_records
        ),
        "valid": not failures,
        "surface_row_count": len(surface_rows_by_digest),
        "topology_event_count": len(topology_events_by_id),
        "lineage_record_count": len(lineage_records),
        "topology_state_reabsorption_record_count": len(reabsorption_records),
        "transported_record_count": transported_count,
        "superseded_record_count": superseded_count,
        "producer_record_count": sum(
            1 for _ in _surface_producer_results(production_results)
        ),
        "validated_surface_ids": sorted(surface_ids),
        "validated_lineage_record_ids": validated_record_ids,
        "failure_reasons": failures,
        "movement_claim_allowed": False,
        "native_m6": False,
        "native_causal_pulse_substrate_surface_lineage_transport_supported": (
            not failures and bool(lineage_records)
        ),
        "native_topology_state_reabsorption_supported": (
            not failures and bool(reabsorption_records)
        ),
    }


def _topology_payload_from_artifact(
    artifact: Mapping[str, Any],
) -> Mapping[str, Any]:
    payload = artifact.get("payload")
    if isinstance(payload, Mapping):
        return payload
    return artifact


def _native_route_candidate_order_is_valid(
    *,
    candidate_set: LGRC9V3NativeRouteCandidateSetRecord,
    candidates: Sequence[LGRC9V3NativeRouteCandidateRecord],
) -> bool:
    if candidate_set.candidate_set_order_key == (
        LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING
    ):
        expected = tuple(
            sorted(str(record.candidate_route_digest) for record in candidates)
        )
    elif candidate_set.candidate_set_order_key == (
        LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
    ):
        expected = tuple(
            str(record.candidate_route_digest)
            for record in sorted(
                candidates,
                key=lambda record: (
                    -float(record.candidate_route_score),
                    str(record.candidate_order_key),
                    str(record.candidate_route_id),
                ),
            )
        )
    else:
        return False
    return expected == tuple(
        str(digest) for digest in candidate_set.candidate_route_digests
    )


def _native_route_candidate_budget_prediction_is_valid(
    candidate: LGRC9V3NativeRouteCandidateRecord,
    *,
    budget_tolerance: float,
) -> bool:
    prediction = {
        str(key): float(value)
        for key, value in candidate.candidate_budget_prediction.items()
    }
    required = {
        "node_plus_packet_budget_before",
        "node_plus_packet_budget_after",
        "node_plus_packet_budget_error",
    }
    if not required.issubset(prediction):
        return False
    if abs(float(prediction["node_plus_packet_budget_error"])) > budget_tolerance:
        return False
    return (
        abs(
            float(prediction["node_plus_packet_budget_after"])
            - float(prediction["node_plus_packet_budget_before"])
        )
        <= budget_tolerance
    )


def validate_lgrc9v3_native_route_arbitration_artifacts(
    *,
    events: Sequence[Mapping[str, Any]],
    candidate_route_records: Sequence[Mapping[str, Any]],
    candidate_set_records: Sequence[Mapping[str, Any]],
    route_arbitration_records: Sequence[Mapping[str, Any]],
    surface_rows: Sequence[Mapping[str, Any]] = (),
    surface_lineage_records: Sequence[Mapping[str, Any]] = (),
    topology_events: Sequence[Mapping[str, Any]] = (),
    topology_state_reabsorption_records: Sequence[Mapping[str, Any]] = (),
    production_results: Sequence[Mapping[str, Any]] = (),
    budget_tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Validate native route-arbitration replay from artifacts only.

    The validator reconstructs candidate routes, candidate sets, arbitration
    records, the selected topology event, surface lineage, topology-state
    reabsorption, and post-arbitration producer scheduling without reading a
    live runtime object.
    """

    failures: list[str] = []
    control_blockers: list[str] = []
    selected_record_ids: list[str] = []

    def _raw_claim_promotion_blocker(
        artifact: Mapping[str, Any],
        *,
        raw_id: str,
    ) -> None:
        claim_flags = artifact.get("claim_flags", {})
        if isinstance(claim_flags, Mapping) and any(
            bool(value) for value in claim_flags.values()
        ):
            failures.append(
                f"native_route_arbitration_claim_promotion_blocked:{raw_id}"
            )

    def _raw_hidden_input_blocker(
        artifact: Mapping[str, Any],
        *,
        raw_id: str,
    ) -> None:
        score_components = artifact.get("candidate_score_components", {})
        runtime_inputs = artifact.get("candidate_runtime_visible_inputs", ())
        arbitration_inputs = artifact.get("arbitration_runtime_visible_inputs", ())
        hidden_inputs: set[str] = set()
        if isinstance(score_components, Mapping):
            hidden_inputs.update(str(key) for key in score_components)
        if isinstance(runtime_inputs, Sequence) and not isinstance(
            runtime_inputs,
            (str, bytes),
        ):
            hidden_inputs.update(str(value) for value in runtime_inputs)
        if isinstance(arbitration_inputs, Sequence) and not isinstance(
            arbitration_inputs,
            (str, bytes),
        ):
            hidden_inputs.update(str(value) for value in arbitration_inputs)
        hidden_inputs = hidden_inputs.intersection(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS
        )
        if hidden_inputs:
            failures.append(
                f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED}:"
                f"{raw_id}:{sorted(hidden_inputs)}"
            )

    surface_payloads = [
        *_causal_pulse_substrate_surface_payloads(events),
        *surface_rows,
    ]
    committed_surface_digests = {
        str(payload.get("surface_digest"))
        for payload in surface_payloads
        if isinstance(payload.get("surface_digest"), str)
    }

    candidates_by_digest: dict[str, LGRC9V3NativeRouteCandidateRecord] = {}
    for artifact in candidate_route_records:
        raw_id = str(artifact.get("candidate_route_id", "unknown_candidate"))
        _raw_hidden_input_blocker(artifact, raw_id=raw_id)
        _raw_claim_promotion_blocker(artifact, raw_id=raw_id)
        try:
            expected_digest = build_lgrc9v3_native_route_candidate_record_digest(
                {
                    key: value
                    for key, value in artifact.items()
                    if key != "candidate_route_digest"
                }
            )
            record = restore_lgrc9v3_native_route_candidate_record_artifact(
                artifact
            )
        except (SnapshotCompatibilityError, ValueError) as exc:
            failures.append(f"corrupted_native_route_candidate_record:{raw_id}:{exc}")
            continue
        if str(record.candidate_route_digest) != expected_digest:
            failures.append(f"candidate_route_digest_mismatch:{raw_id}")
        if str(record.candidate_route_digest) in candidates_by_digest:
            failures.append(
                f"duplicate_native_route_candidate:{record.candidate_route_digest}"
            )
            continue
        if (
            committed_surface_digests
            and record.candidate_source_surface_digest not in committed_surface_digests
        ):
            failures.append(
                "native_route_candidate_unknown_source_surface:"
                f"{record.candidate_route_id}"
            )
        if not _native_route_candidate_budget_prediction_is_valid(
            record,
            budget_tolerance=budget_tolerance,
        ):
            failures.append(
                f"native_route_candidate_budget_mismatch:{record.candidate_route_id}"
            )
        if any(bool(value) for value in record.claim_flags.values()):
            failures.append(f"native_route_candidate_promoted_claim:{raw_id}")
        candidates_by_digest[str(record.candidate_route_digest)] = record

    candidate_sets_by_digest: dict[str, LGRC9V3NativeRouteCandidateSetRecord] = {}
    seen_candidate_set_keys: set[str] = set()
    for artifact in candidate_set_records:
        raw_id = str(artifact.get("candidate_set_id", "unknown_candidate_set"))
        _raw_claim_promotion_blocker(artifact, raw_id=raw_id)
        try:
            expected_digest = build_lgrc9v3_native_route_candidate_set_record_digest(
                {
                    key: value
                    for key, value in artifact.items()
                    if key != "candidate_set_digest"
                }
            )
            record = restore_lgrc9v3_native_route_candidate_set_record_artifact(
                artifact
            )
        except (SnapshotCompatibilityError, ValueError) as exc:
            failures.append(f"corrupted_native_route_candidate_set_record:{raw_id}:{exc}")
            continue
        if str(record.candidate_set_digest) != expected_digest:
            failures.append(f"candidate_set_digest_mismatch:{raw_id}")
        if record.idempotency_key in seen_candidate_set_keys:
            failures.append(f"duplicate_native_route_candidate_set:{record.idempotency_key}")
            continue
        seen_candidate_set_keys.add(str(record.idempotency_key))
        candidates: list[LGRC9V3NativeRouteCandidateRecord] = []
        for digest in record.candidate_route_digests:
            candidate = candidates_by_digest.get(str(digest))
            if candidate is None:
                failures.append(
                    f"candidate_set_missing_candidate:{record.candidate_set_id}:{digest}"
                )
                continue
            candidates.append(candidate)
            _append_if_false(
                failures,
                candidate.candidate_set_id == record.candidate_set_id,
                "candidate_set_id_mismatch:"
                f"{record.candidate_set_id}:{candidate.candidate_route_id}",
            )
            _append_if_false(
                failures,
                int(candidate.scheduler_event_index) <= int(record.scheduler_event_index),
                "candidate_set_order_inversion:"
                f"{record.candidate_set_id}:{candidate.candidate_route_id}",
            )
            if int(candidate.scheduler_event_index) > int(record.scheduler_event_index):
                failures.append(
                    f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID}:"
                    f"{record.candidate_set_id}:candidate_set_before_candidate"
                )
        if len(candidates) == len(record.candidate_route_digests):
            _append_if_false(
                failures,
                _native_route_candidate_order_is_valid(
                    candidate_set=record,
                    candidates=candidates,
                ),
                f"native_route_candidate_set_order_invalid:{record.candidate_set_id}",
            )
        if any(bool(value) for value in record.claim_flags.values()):
            failures.append(f"native_route_candidate_set_promoted_claim:{raw_id}")
        candidate_sets_by_digest[str(record.candidate_set_digest)] = record

    raw_topology_payloads = [
        *(_topology_payload_from_artifact(artifact) for artifact in topology_events),
        *_topology_event_payloads(events),
    ]
    topology_payloads: list[Mapping[str, Any]] = []
    topology_digest_by_event_id: dict[str, str] = {}
    for payload in raw_topology_payloads:
        event_id = _topology_event_id(payload)
        if event_id is None:
            continue
        digest = build_lgrc9v3_topology_event_digest(payload)
        existing_digest = topology_digest_by_event_id.get(event_id)
        if existing_digest is not None:
            if existing_digest != digest:
                failures.append(f"topology_event_duplicate_digest_mismatch:{event_id}")
            continue
        topology_digest_by_event_id[event_id] = digest
        topology_payloads.append(payload)
    lineage_validation: dict[str, Any] | None = None
    if surface_lineage_records or topology_state_reabsorption_records or production_results:
        lineage_validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
            events=events,
            surface_rows=surface_rows,
            surface_lineage_records=surface_lineage_records,
            topology_events=topology_payloads,
            topology_state_reabsorption_records=topology_state_reabsorption_records,
            production_results=production_results,
            budget_tolerance=budget_tolerance,
        )
        failures.extend(
            f"route_arbitration_lineage_replay:{reason}"
            for reason in lineage_validation.get("failure_reasons", ())
        )

    seen_arbitration_keys: set[str] = set()
    selected_topology_event_count = 0
    linked_producer_count = 0
    for artifact in route_arbitration_records:
        raw_id = str(
            artifact.get(
                "native_route_arbitration_record_id",
                "unknown_route_arbitration",
            )
        )
        _raw_hidden_input_blocker(artifact, raw_id=raw_id)
        _raw_claim_promotion_blocker(artifact, raw_id=raw_id)
        try:
            expected_digest = build_lgrc9v3_native_route_arbitration_record_digest(
                {
                    key: value
                    for key, value in artifact.items()
                    if key != "native_route_arbitration_digest"
                }
            )
            record = restore_lgrc9v3_native_route_arbitration_record_artifact(
                artifact
            )
        except (SnapshotCompatibilityError, ValueError) as exc:
            failures.append(f"corrupted_native_route_arbitration_record:{raw_id}:{exc}")
            continue
        if str(record.native_route_arbitration_digest) != expected_digest:
            failures.append(f"native_route_arbitration_digest_mismatch:{raw_id}")
        if record.idempotency_key in seen_arbitration_keys:
            failures.append(f"duplicate_native_route_arbitration:{record.idempotency_key}")
            continue
        seen_arbitration_keys.add(str(record.idempotency_key))
        candidate_set = candidate_sets_by_digest.get(record.candidate_set_digest)
        if candidate_set is None:
            failures.append(
                f"native_route_arbitration_missing_candidate_set:{raw_id}"
            )
            continue
        _append_if_false(
            failures,
            candidate_set.candidate_set_id == record.candidate_set_id,
            f"native_route_arbitration_candidate_set_id_mismatch:{raw_id}",
        )
        _append_if_false(
            failures,
            int(record.scheduler_event_index) >= int(candidate_set.scheduler_event_index),
            f"native_route_arbitration_order_inversion:{raw_id}",
        )
        if int(record.scheduler_event_index) < int(candidate_set.scheduler_event_index):
            failures.append(
                f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID}:"
                f"{raw_id}:arbitration_before_candidate_set"
            )
        if any(bool(value) for value in record.claim_flags.values()):
            failures.append(f"native_route_arbitration_promoted_claim:{raw_id}")
        selected_reason = (
            record.arbitration_reason_code
            in LGRC9V3_NATIVE_ROUTE_ARBITRATION_SELECTED_REASON_CODES
        )
        if not selected_reason:
            control_blockers.append(record.arbitration_reason_code)
            _append_if_false(
                failures,
                record.selected_candidate_route_digest is None
                and record.selected_topology_event_digest is None,
                f"native_route_arbitration_nonselected_record_selected:{raw_id}",
            )
            continue
        selected_digest = str(record.selected_candidate_route_digest)
        selected_candidate = candidates_by_digest.get(selected_digest)
        if selected_candidate is None:
            failures.append(f"native_route_arbitration_missing_selected_candidate:{raw_id}")
            continue
        selected_record_ids.append(record.native_route_arbitration_record_id)
        _append_if_false(
            failures,
            selected_digest in {str(d) for d in candidate_set.candidate_route_digests},
            f"native_route_arbitration_selected_candidate_outside_set:{raw_id}",
        )
        expected_rejected = {
            str(digest)
            for digest in candidate_set.candidate_route_digests
            if str(digest) != selected_digest
        }
        _append_if_false(
            failures,
            set(record.rejected_candidate_route_digests) == expected_rejected,
            f"native_route_arbitration_rejected_set_mismatch:{raw_id}",
        )
        if (
            record.arbitration_reason_code
            == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE
        ):
            candidate_scores = [
                float(candidates_by_digest[str(digest)].candidate_route_score)
                for digest in candidate_set.candidate_route_digests
                if str(digest) in candidates_by_digest
            ]
            _append_if_false(
                failures,
                candidate_scores
                and math.isclose(
                    float(selected_candidate.candidate_route_score),
                    max(candidate_scores),
                    rel_tol=0.0,
                    abs_tol=budget_tolerance,
                ),
                f"native_route_arbitration_selected_not_highest_score:{raw_id}",
            )
        selected_topology_payloads = [
            payload
            for payload in topology_payloads
            if payload.get("native_route_arbitration_record_id")
            == record.native_route_arbitration_record_id
        ]
        if len(selected_topology_payloads) != 1:
            failures.append(
                f"selected_topology_event_count_mismatch:{raw_id}:"
                f"{len(selected_topology_payloads)}"
            )
            continue
        selected_topology_event_count += 1
        topology_payload = selected_topology_payloads[0]
        topology_digest = build_lgrc9v3_topology_event_digest(topology_payload)
        topology_scheduler_index = int(topology_payload.get("scheduler_event_index", -1))
        if topology_scheduler_index < int(record.scheduler_event_index):
            failures.append(
                f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID}:"
                f"{raw_id}:selected_topology_event_before_arbitration"
            )
        _append_if_false(
            failures,
            topology_digest == record.selected_topology_event_digest,
            f"selected_topology_event_digest_mismatch:{raw_id}",
        )
        _append_if_false(
            failures,
            topology_payload.get("native_route_arbitration_digest")
            == record.native_route_arbitration_digest,
            f"selected_topology_event_arbitration_digest_mismatch:{raw_id}",
        )
        _append_if_false(
            failures,
            topology_payload.get("native_route_selected_candidate_route_digest")
            == selected_digest,
            f"selected_topology_event_candidate_mismatch:{raw_id}",
        )
        _append_if_false(
            failures,
            topology_payload.get("native_route_candidate_set_digest")
            == record.candidate_set_digest,
            f"selected_topology_event_candidate_set_mismatch:{raw_id}",
        )
        _append_if_false(
            failures,
            {
                str(key): str(value)
                for key, value in selected_candidate.candidate_lineage_transfer_map.items()
            }
            == {
                str(key): str(value)
                for key, value in dict(
                    topology_payload.get("lineage_transfer_map", {})
                ).items()
            },
            f"selected_topology_event_lineage_map_mismatch:{raw_id}",
        )
        rejected_commits = [
            payload
            for payload in topology_payloads
            if payload.get("native_route_selected_candidate_route_digest")
            in set(record.rejected_candidate_route_digests)
        ]
        if rejected_commits:
            failures.append(f"rejected_candidate_committed_topology:{raw_id}")

        selected_lineage = [
            record_artifact
            for record_artifact in surface_lineage_records
            if record_artifact.get("topology_event_digest")
            == record.selected_topology_event_digest
        ]
        selected_reabsorption = [
            record_artifact
            for record_artifact in topology_state_reabsorption_records
            if record_artifact.get("topology_event_digest")
            == record.selected_topology_event_digest
        ]
        _append_if_false(
            failures,
            bool(selected_lineage),
            f"selected_topology_event_missing_surface_lineage:{raw_id}",
        )
        _append_if_false(
            failures,
            bool(selected_reabsorption),
            f"selected_topology_event_missing_topology_state_reabsorption:{raw_id}",
        )
        for lineage_record in selected_lineage:
            if int(lineage_record.get("scheduler_event_index", -1)) < topology_scheduler_index:
                failures.append(
                    f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID}:"
                    f"{raw_id}:surface_lineage_before_selected_topology_event"
                )
        for reabsorption_record in selected_reabsorption:
            if int(reabsorption_record.get("scheduler_event_index", -1)) < topology_scheduler_index:
                failures.append(
                    f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID}:"
                    f"{raw_id}:reabsorption_before_selected_topology_event"
                )
        selected_reabsorption_digests = {
            str(item.get("topology_state_reabsorption_digest"))
            for item in selected_reabsorption
            if isinstance(item.get("topology_state_reabsorption_digest"), str)
        }
        selected_reabsorption_scheduler_indexes = [
            int(item.get("scheduler_event_index", -1))
            for item in selected_reabsorption
        ]
        transported_digests = {
            str(item.get("transported_surface_digest"))
            for item in selected_lineage
            if isinstance(item.get("transported_surface_digest"), str)
        }
        for _producer_result, producer_record in _surface_producer_results(
            production_results
        ):
            if producer_record.get("causal_surface_digest") not in transported_digests:
                continue
            producer_scheduler_index = int(
                producer_record.get(
                    "scheduler_event_index",
                    _producer_result.get("scheduler_event_index", -1),
                )
            )
            if (
                selected_reabsorption_scheduler_indexes
                and producer_scheduler_index
                < max(selected_reabsorption_scheduler_indexes)
            ):
                failures.append(
                    f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID}:"
                    f"{producer_record.get('record_id', 'unknown_producer')}:"
                    "producer_before_reabsorption"
                )
            evidence = producer_record.get("observed_evidence", {})
            if not isinstance(evidence, Mapping):
                failures.append(
                    "post_arbitration_producer_evidence_not_mapping:"
                    f"{producer_record.get('record_id', 'unknown_producer')}"
                )
                continue
            if evidence.get("topology_event_digest") != record.selected_topology_event_digest:
                failures.append(
                    "post_arbitration_producer_topology_digest_mismatch:"
                    f"{producer_record.get('record_id', 'unknown_producer')}"
                )
            if (
                evidence.get("topology_state_reabsorption_record_digest")
                not in selected_reabsorption_digests
            ):
                failures.append(
                    "post_arbitration_producer_reabsorption_digest_mismatch:"
                    f"{producer_record.get('record_id', 'unknown_producer')}"
                )
            linked_producer_count += 1

    if not candidate_route_records:
        failures.append("no_native_route_candidate_records")
    if not candidate_set_records:
        failures.append("no_native_route_candidate_set_records")
    if not route_arbitration_records:
        failures.append("no_native_route_arbitration_records")

    supported = not failures and bool(selected_record_ids)
    return {
        "validator": "validate_lgrc9v3_native_route_arbitration_artifacts",
        "artifact_only": True,
        "runtime_state_used": False,
        "valid": not failures,
        "candidate_set_reconstructed": bool(candidate_sets_by_digest),
        "route_arbitration_reconstructed": bool(route_arbitration_records),
        "route_selection_reconstructed_from_artifacts": bool(selected_record_ids),
        "selected_topology_event_reconstructed": selected_topology_event_count > 0,
        "downstream_lineage_reabsorption_producer_chain_reconstructed": (
            bool(selected_record_ids)
            and bool(lineage_validation and lineage_validation.get("valid", False))
            and linked_producer_count > 0
        ),
        "candidate_route_count": len(candidates_by_digest),
        "candidate_set_count": len(candidate_sets_by_digest),
        "route_arbitration_record_count": len(route_arbitration_records),
        "selected_route_arbitration_record_ids": selected_record_ids,
        "selected_topology_event_count": selected_topology_event_count,
        "post_arbitration_linked_producer_count": linked_producer_count,
        "lineage_replay_valid": None
        if lineage_validation is None
        else bool(lineage_validation.get("valid", False)),
        "control_blockers": sorted(set(control_blockers)),
        "failure_reasons": failures,
        "native_lgrc_route_arbitration_supported": supported,
        "native_lgrc_choice_selection_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "agency_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "biological_claim_allowed": False,
        "unrestricted_movement_claim_allowed": False,
    }


def _float_from_mapping(
    mapping: Mapping[str, Any],
    key: str,
    default: float = 0.0,
) -> float:
    value = mapping.get(key, default)
    return float(value)


def validate_lgrc9v3_self_rearm_evidence_artifacts(
    *,
    events: Sequence[Mapping[str, Any]],
    production_results: Sequence[Mapping[str, Any]] = (),
    require_completed: bool = True,
    budget_tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Validate native self-rearm chains from serialized artifacts only.

    The validator links packet processing events, producer records, and
    self-rearm evidence records without reading live runtime objects. A
    completed self-rearm requires parent arrival -> post-arrival surplus
    producer -> child departure processing in route-aspect order.
    """

    packet_payloads = _packet_event_payloads_by_id(events)
    producer_records = _production_records_by_id(production_results)
    self_rearm_payloads = _self_rearm_payloads(events)
    candidates = {
        str(payload["self_rearm_evidence_id"]): payload
        for payload in self_rearm_payloads
        if payload.get("self_rearm_status") == "scheduled_child_pending_departure"
        and isinstance(payload.get("self_rearm_evidence_id"), str)
    }
    completions = [
        payload
        for payload in self_rearm_payloads
        if payload.get("self_rearm_status") == "child_departure_processed"
    ]

    failures: list[str] = []
    validated_ids: list[str] = []
    payloads_to_validate = completions if require_completed else self_rearm_payloads
    if require_completed and not completions:
        failures.append("no_completed_self_rearm_evidence")
    if not require_completed and not self_rearm_payloads:
        failures.append("no_self_rearm_evidence")

    for payload in payloads_to_validate:
        candidate_id = str(
            payload.get(
                "candidate_self_rearm_evidence_id",
                payload.get("self_rearm_evidence_id", ""),
            )
        )
        parent_arrival_event_id = str(payload.get("parent_arrival_event_id", ""))
        child_departure_event_id = str(payload.get("child_departure_event_id", ""))
        producer_record_id = str(payload.get("producer_record_id", ""))

        candidate = candidates.get(candidate_id)
        producer = producer_records.get(producer_record_id)
        parent_event = packet_payloads.get(parent_arrival_event_id)
        child_event = packet_payloads.get(child_departure_event_id)

        _append_if_false(
            failures,
            candidate is not None,
            f"missing_candidate:{candidate_id}",
        )
        _append_if_false(
            failures,
            producer is not None,
            f"missing_producer_record:{producer_record_id}",
        )
        _append_if_false(
            failures,
            parent_event is not None,
            f"missing_parent_arrival_event:{parent_arrival_event_id}",
        )
        _append_if_false(
            failures,
            child_event is not None,
            f"missing_child_departure_event:{child_departure_event_id}",
        )
        if parent_event is None or child_event is None or producer is None:
            continue

        parent_processed = parent_event["processed_event"]
        child_processed = child_event["processed_event"]
        producer_evidence = producer.get("observed_evidence", {})
        if not isinstance(producer_evidence, Mapping):
            failures.append(f"producer_evidence_not_mapping:{producer_record_id}")
            continue

        _append_if_false(
            failures,
            parent_processed.get("event_kind") == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            f"parent_not_arrival:{parent_arrival_event_id}",
        )
        _append_if_false(
            failures,
            child_processed.get("event_kind") == LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            f"child_not_departure:{child_departure_event_id}",
        )
        _append_if_false(
            failures,
            parent_processed.get("packet_id") == payload.get("parent_packet_id"),
            f"parent_packet_mismatch:{parent_arrival_event_id}",
        )
        _append_if_false(
            failures,
            child_processed.get("packet_id") == payload.get("child_packet_id"),
            f"child_packet_mismatch:{child_departure_event_id}",
        )
        _append_if_false(
            failures,
            producer.get("reason_code")
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED,
            f"producer_wrong_reason:{producer_record_id}",
        )
        _append_if_false(
            failures,
            producer.get("scheduled_event_id") == child_departure_event_id,
            f"producer_child_event_mismatch:{producer_record_id}",
        )
        _append_if_false(
            failures,
            producer_evidence.get("scheduled_packet_id") == payload.get("child_packet_id"),
            f"producer_child_packet_mismatch:{producer_record_id}",
        )
        _append_if_false(
            failures,
            producer_evidence.get("self_rearm_evidence_id") == candidate_id,
            f"producer_self_rearm_id_mismatch:{producer_record_id}",
        )

        route_digest = payload.get("route_aspect_digest")
        _append_if_false(
            failures,
            producer_evidence.get("route_aspect_digest") == route_digest,
            f"route_digest_mismatch:{producer_record_id}",
        )
        sequence = tuple(str(value) for value in payload.get("route_channel_sequence", ()))
        parent_channel = str(payload.get("parent_arrival_channel_id", ""))
        trigger_channel = str(payload.get("trigger_channel_id", ""))
        expected_previous = str(payload.get("expected_previous_channel_id", ""))
        expected_next = str(payload.get("expected_next_channel_id", ""))
        _append_if_false(
            failures,
            bool(sequence),
            f"missing_route_channel_sequence:{candidate_id}",
        )
        if sequence and parent_channel in sequence and trigger_channel in sequence:
            parent_index = sequence.index(parent_channel)
            trigger_index = sequence.index(trigger_channel)
            _append_if_false(
                failures,
                sequence[(parent_index + 1) % len(sequence)] == trigger_channel,
                f"route_order_mismatch:{candidate_id}",
            )
            _append_if_false(
                failures,
                sequence[(trigger_index - 1) % len(sequence)] == expected_previous,
                f"expected_previous_mismatch:{candidate_id}",
            )
            _append_if_false(
                failures,
                sequence[(trigger_index + 1) % len(sequence)] == expected_next,
                f"expected_next_mismatch:{candidate_id}",
            )
        else:
            failures.append(f"route_channel_missing:{candidate_id}")

        _append_if_false(
            failures,
            _float_from_mapping(parent_event, "budget_error") <= budget_tolerance,
            f"parent_budget_error:{parent_arrival_event_id}",
        )
        _append_if_false(
            failures,
            _float_from_mapping(child_event, "budget_error") <= budget_tolerance,
            f"child_budget_error:{child_departure_event_id}",
        )
        for key in (
            "parent_arrival_budget_error",
            "producer_budget_error",
            "child_scheduling_budget_error",
            "child_departure_budget_error",
        ):
            _append_if_false(
                failures,
                key in payload
                and abs(_float_from_mapping(payload, key)) <= budget_tolerance,
                f"{key}:{candidate_id}",
            )
        _append_if_false(
            failures,
            _float_from_mapping(payload, "budget_before_producer")
            == _float_from_mapping(payload, "budget_after_producer"),
            f"producer_mutated_budget:{candidate_id}",
        )
        _append_if_false(
            failures,
            _float_from_mapping(payload, "budget_after_producer")
            == _float_from_mapping(payload, "budget_after_child_scheduling_before_departure"),
            f"child_scheduling_mutated_budget:{candidate_id}",
        )

        parent_event_time = _float_from_mapping(parent_processed, "event_time_key")
        producer_event_time = _float_from_mapping(payload, "producer_event_time_key")
        child_event_time = _float_from_mapping(child_processed, "event_time_key")
        parent_scheduler = int(parent_processed.get("scheduler_event_index", -1))
        producer_scheduler = int(payload.get("producer_scheduler_event_index", -1))
        child_scheduler = int(child_processed.get("scheduler_event_index", -1))
        _append_if_false(
            failures,
            parent_event_time <= producer_event_time <= child_event_time,
            f"event_time_ordering_failed:{candidate_id}",
        )
        _append_if_false(
            failures,
            parent_scheduler <= producer_scheduler < child_scheduler,
            f"scheduler_ordering_failed:{candidate_id}",
        )
        _append_if_false(
            failures,
            bool(payload.get("threshold_crossed", False)),
            f"threshold_not_crossed:{candidate_id}",
        )
        _append_if_false(
            failures,
            _float_from_mapping(payload, "surplus_after_arrival")
            >= _float_from_mapping(payload, "trigger_threshold"),
            f"surplus_below_threshold:{candidate_id}",
        )
        _append_if_false(
            failures,
            bool(payload.get("child_departure_processed", False))
            or not require_completed,
            f"child_departure_unprocessed:{candidate_id}",
        )
        _append_if_false(
            failures,
            "node_proper_time_surface" in payload
            and "source_node_proper_time_at_trigger" in payload
            and "child_source_node_proper_time_at_departure" in payload,
            f"missing_proper_time_evidence:{candidate_id}",
        )
        if not any(reason.endswith(candidate_id) for reason in failures):
            validated_ids.append(str(payload.get("self_rearm_evidence_id", "")))

    return {
        "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts",
        "valid": not failures,
        "candidate_count": len(candidates),
        "completed_count": len(completions),
        "validated_self_rearm_evidence_ids": validated_ids,
        "failure_reasons": failures,
        "native_d2_3_equivalent": False,
        "movement_claim_allowed": False,
        "native_grc9v3_loop_evidence": False,
    }


def _runtime_topology_signature(state: LGRC9V3RuntimeState) -> dict[str, Any]:
    """Return a compact pre-event topology signature for causal diagnostics."""

    return {
        "node_ids": [
            int(node_id)
            for node_id in sorted(state.base_state.topology.iter_live_node_ids())
        ],
        "edge_ids": [
            int(edge_id)
            for edge_id in sorted(state.base_state.topology.iter_live_edge_ids())
        ],
        "node_count": int(
            len(tuple(state.base_state.topology.iter_live_node_ids()))
        ),
        "edge_count": int(
            len(tuple(state.base_state.topology.iter_live_edge_ids()))
        ),
    }


def _string_keyed_float_map(values: Mapping[int, float]) -> dict[str, float]:
    return {str(int(key)): float(value) for key, value in sorted(values.items())}


def _nonnegative_finite_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{context} must be a finite number")
    resolved = float(value)
    if not math.isfinite(resolved) or resolved < 0.0:
        raise ValueError(f"{context} must be finite and >= 0")
    return resolved


class LGRC9V3(GRCModel):
    """Executable LGRC9V3 shell with a composed GRC9V3 substrate.

    The runtime owns deterministic packet event-queue orchestration,
    arrival-triggered packetized local updates, causally scheduled Lane A/Lane B
    spark diagnostics, opt-in topology integration, and opt-in identity
    evidence. It still does not call synchronous ``GRC9V3.step()``.
    """

    MODEL_FAMILY = "LGRC9V3"

    def __init__(
        self,
        params: GRCParams,
        state: LGRC9V3RuntimeState,
    ) -> None:
        self._params = params
        self._state = deepcopy(state)
        self._state.packet_ledger = with_ordered_lgrc9v3_event_queue(
            self._state.packet_ledger  # type: ignore[arg-type]
        )
        self._initial_state = deepcopy(self._state)

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "LGRC9V3":
        """Create LGRC9V3 from a nested GRC9V3 config plus causal modes."""

        base_config = config.get("grc9v3_config", config)
        if not isinstance(base_config, Mapping):
            raise InvalidParamsError("grc9v3_config must be a mapping")
        causal_modes = config.get("causal_modes")
        if causal_modes is not None and not isinstance(causal_modes, Mapping):
            raise InvalidParamsError("causal_modes must be a mapping")
        base_model = GRC9V3.from_config(base_config)
        runtime_state = cls._runtime_state_from_base(
            base_model.get_state(),
            causal_modes=causal_modes,
        )
        return cls(base_model.get_params(), runtime_state)

    @classmethod
    def from_state(
        cls,
        state: Mapping[str, Any] | GRC9V3State | LGRC9V3RuntimeState,
        params: Mapping[str, Any] | GRCParams,
    ) -> "LGRC9V3":
        """Create LGRC9V3 from GRC9V3 state or a runtime-state bundle."""

        if isinstance(state, LGRC9V3RuntimeState):
            if isinstance(params, GRCParams):
                resolved_params = params
            else:
                resolved_params = GRC9V3.from_state(
                    state.base_state,
                    params,
                ).get_params()
            return cls(resolved_params, state)

        if isinstance(params, GRCParams):
            if not isinstance(state, GRC9V3State):
                raise SnapshotCompatibilityError(
                    "mapping state restoration requires serialized params, "
                    "not a GRCParams object"
                )
            base_model = GRC9V3(params=params, state=state)
            causal_modes = None
        else:
            causal_modes = params.get("causal_modes")
            if causal_modes is not None and not isinstance(causal_modes, Mapping):
                raise InvalidParamsError("causal_modes must be a mapping")
            base_model = GRC9V3.from_state(state, params)
        runtime_state = cls._runtime_state_from_base(
            base_model.get_state(),
            causal_modes=causal_modes,
        )
        return cls(base_model.get_params(), runtime_state)

    @classmethod
    def from_landscape_seed(
        cls,
        seed: object,
        *,
        params: Mapping[str, Any] | GRCParams | None = None,
        causal_modes: Mapping[str, Any] | None = None,
        validate_seed: bool = True,
    ) -> "LGRC9V3":
        """Construct LGRC9V3 through the library-owned landscape lowering path."""

        from .lgrc_9_v3_construction import build_lgrc9v3_from_landscape_seed

        return build_lgrc9v3_from_landscape_seed(
            seed,  # type: ignore[arg-type]
            params=params,
            causal_modes=causal_modes,
            validate_seed=validate_seed,
        )

    @classmethod
    def load(cls, path: str) -> "LGRC9V3":
        """Restore a native LGRC9V3 runtime snapshot emitted by ``snapshot``."""

        snapshot = load_snapshot(path)
        require_snapshot_family(snapshot, expected_family=cls.MODEL_FAMILY)

        metadata = snapshot.get("metadata")
        if not isinstance(metadata, Mapping):
            raise SnapshotCompatibilityError("snapshot metadata must be a mapping")
        params_payload = metadata.get("params")
        if not isinstance(params_payload, Mapping):
            raise SnapshotCompatibilityError("snapshot metadata.params must be a mapping")

        caches = snapshot.get("caches", {})
        if not isinstance(caches, Mapping):
            raise SnapshotCompatibilityError("snapshot caches must be a mapping")
        base_snapshot = caches.get("base_grc9v3_snapshot")
        if not isinstance(base_snapshot, Mapping):
            raise SnapshotCompatibilityError(
                "LGRC9V3 snapshot caches.base_grc9v3_snapshot is required"
            )
        base_model = GRC9V3._from_snapshot(base_snapshot)
        base_state = base_model.get_state()

        dynamics = snapshot.get("dynamics", {})
        if not isinstance(dynamics, Mapping):
            raise SnapshotCompatibilityError("snapshot dynamics must be a mapping")
        runtime_artifact = dynamics.get("lgrc9v3_runtime")
        if not isinstance(runtime_artifact, Mapping):
            raise SnapshotCompatibilityError(
                "snapshot dynamics.lgrc9v3_runtime must be a mapping"
            )

        runtime_state = restore_lgrc9v3_runtime_state_artifact(
            runtime_artifact,
            base_state=base_state,
        )
        event_payload = snapshot.get("events", [])
        if not isinstance(event_payload, list):
            raise SnapshotCompatibilityError("snapshot events must be a list")
        runtime_state.event_log = [
            restore_lgrc9v3_event_record(
                record if isinstance(record, Mapping) else {}
            )
            for record in event_payload
        ]

        observables_payload = snapshot.get("observables", {})
        if not isinstance(observables_payload, Mapping):
            raise SnapshotCompatibilityError("snapshot observables must be a mapping")
        runtime_state.observables = dict(observables_payload)

        params = GRC9V3.from_state(base_state, dict(params_payload)).get_params()
        model = cls(params=params, state=runtime_state)
        computed_observables = dict(model.compute_observables())
        for key, computed_value in computed_observables.items():
            if key not in observables_payload:
                raise SnapshotCompatibilityError(
                    f"snapshot observables missing {key!r}"
                )
            try:
                snapshot_value = float(observables_payload[key])
            except (TypeError, ValueError) as exc:
                raise SnapshotCompatibilityError(
                    f"snapshot observables[{key!r}] must be numeric"
                ) from exc
            if abs(snapshot_value - float(computed_value)) > 1e-9:
                raise SnapshotCompatibilityError(
                    f"snapshot observables[{key!r}] do not match runtime state"
                )
        model._state.observables = computed_observables
        model._initial_state = deepcopy(model._state)
        return model

    @classmethod
    def _runtime_state_from_base(
        cls,
        base_state: GRC9V3State,
        *,
        causal_modes: Mapping[str, Any] | None = None,
    ) -> LGRC9V3RuntimeState:
        modes = _runtime_default_modes(causal_modes)
        edge_delay = compute_lgrc9v3_edge_causal_delay(
            base_state,
            policy=modes["edge_delay_policy"],
            tau_0=1.0,
        )
        lapse = compute_lgrc9v3_lapse_by_node(
            base_state,
            policy=modes["lapse_policy"],
        )
        live_nodes = tuple(
            sorted(int(node_id) for node_id in base_state.topology.iter_live_node_ids())
        )
        packet_ledger = build_lgrc9v3_packet_ledger(state=base_state)
        return LGRC9V3RuntimeState(
            base_state=base_state,
            scheduler_event_index=0,
            checkpoint_index=0,
            event_time_key=0.0,
            node_proper_time={node_id: 0.0 for node_id in live_nodes},
            node_last_update_proper_time={node_id: 0.0 for node_id in live_nodes},
            node_last_update_event_time_key={node_id: 0.0 for node_id in live_nodes},
            edge_causal_delay=edge_delay,
            lapse=lapse,
            packet_ledger=packet_ledger,
            causal_modes=modes,
            causal_layer_mode=modes["causal_layer_mode"],
            lgrc_runtime_level=modes["lgrc_runtime_level"],
            edge_delay_policy=modes["edge_delay_policy"],
        )

    def get_state(self) -> LGRC9V3RuntimeState:
        return self._state

    def set_state(self, state: LGRC9V3RuntimeState) -> None:
        if not isinstance(state, LGRC9V3RuntimeState):
            raise SnapshotCompatibilityError(
                "state must be an LGRC9V3RuntimeState instance"
            )
        self._state = deepcopy(state)
        self._state.packet_ledger = with_ordered_lgrc9v3_event_queue(
            self._state.packet_ledger  # type: ignore[arg-type]
        )

    def get_params(self) -> GRCParams:
        return self._params

    def list_capabilities(self) -> set[str]:
        return set(GRC9V3.CAPABILITY_PROFILE.required) | {CAUSAL_LAYER}

    def compute_observables(self) -> dict[str, float]:
        ledger = self._state.packet_ledger
        assert ledger is not None
        observables = {
            "node_count": float(
                len(tuple(self._state.base_state.topology.iter_live_node_ids()))
            ),
            "edge_count": float(
                len(tuple(self._state.base_state.topology.iter_live_edge_ids()))
            ),
            "scheduler_event_index": float(self._state.scheduler_event_index),
            "checkpoint_index": float(self._state.checkpoint_index),
            "event_time_key": float(self._state.event_time_key),
            "packet_count": float(len(ledger.packet_records)),
            "event_queue_length": float(len(ledger.event_queue_records)),
            "in_flight_packet_total": float(ledger.in_flight_packet_total),
            "conserved_budget_total": float(ledger.conserved_budget_total),
            "arrival_eligibility_count": float(len(self._state.arrival_eligibility_log)),
            "local_update_count": float(len(self._state.local_update_log)),
            "causal_spark_diagnostic_count": float(
                len(self._state.causal_spark_diagnostic_log)
            ),
            "topology_event_count": float(len(self._state.topology_event_log)),
            "boundary_birth_trial_queue_length": float(
                len(self._state.boundary_birth_trial_queue)
            ),
        }
        if (
            self._causal_pulse_substrate_surface_enabled()
            or self._state.causal_pulse_substrate_surface_log
        ):
            observables["causal_pulse_substrate_surface_count"] = float(
                len(self._state.causal_pulse_substrate_surface_log)
            )
        return observables

    def _causal_pulse_substrate_surface_enabled(self) -> bool:
        return bool(
            self._state.causal_modes.get("causal_pulse_substrate_surface_enabled")
        ) and (
            self._state.causal_modes.get("causal_pulse_substrate_surface_policy")
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
        )

    def _causal_pulse_substrate_surface_keys(self) -> set[str]:
        raw_keys = self._state.cached_quantities.get(
            "lgrc9v3_causal_pulse_substrate_surface_idempotency_keys",
            [],
        )
        if not isinstance(raw_keys, Sequence) or isinstance(raw_keys, str):
            raise InvalidStateTransitionError(
                "causal pulse-substrate surface idempotency cache must be a sequence"
            )
        return {str(key) for key in raw_keys}

    def _store_causal_pulse_substrate_surface_keys(self, keys: set[str]) -> None:
        self._state.cached_quantities[
            "lgrc9v3_causal_pulse_substrate_surface_idempotency_keys"
        ] = sorted(keys)

    def _surface_lineage_transport_enabled(self) -> bool:
        return bool(
            self._state.causal_modes.get(
                "causal_pulse_substrate_surface_lineage_transport_enabled",
                False,
            )
        ) and (
            self._state.causal_modes.get(
                "causal_pulse_substrate_surface_lineage_transport_policy"
            )
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
        )

    def _causal_pulse_substrate_surface_lineage_keys(self) -> set[str]:
        raw_keys = self._state.cached_quantities.get(
            "lgrc9v3_causal_pulse_substrate_surface_lineage_idempotency_keys",
            [],
        )
        if not isinstance(raw_keys, Sequence) or isinstance(raw_keys, str):
            raise InvalidStateTransitionError(
                "causal pulse-substrate surface lineage idempotency cache "
                "must be a sequence"
            )
        return {str(key) for key in raw_keys}

    def _store_causal_pulse_substrate_surface_lineage_keys(
        self,
        keys: set[str],
    ) -> None:
        self._state.cached_quantities[
            "lgrc9v3_causal_pulse_substrate_surface_lineage_idempotency_keys"
        ] = sorted(keys)

    def _topology_event_payload(self, topology_event: GRCEvent | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(topology_event, GRCEvent):
            return {"topology_event_kind": topology_event.kind, **dict(topology_event.payload)}
        mapping = dict(topology_event)
        if "payload" in mapping and isinstance(mapping["payload"], Mapping):
            payload = dict(mapping["payload"])
            payload.setdefault("topology_event_kind", str(mapping.get("kind", "")))
            return payload
        return mapping

    def _topology_event_lineage_transfer_map(
        self,
        topology_artifact: Mapping[str, Any],
    ) -> dict[str, str]:
        for key in (
            "lineage_transfer_map",
            "refinement_lineage_map",
            "parent_to_child_node_lineage",
            "boundary_reassignment_map",
        ):
            raw_map = topology_artifact.get(key)
            if isinstance(raw_map, Mapping) and raw_map:
                return {str(source): str(target) for source, target in raw_map.items()}
        raise InvalidStateTransitionError(
            "surface lineage supersession requires topology lineage evidence"
        )

    def _transported_surface_node_ids(
        self,
        *,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
        lineage_transfer_map: Mapping[str, str],
    ) -> tuple[int, ...]:
        live_nodes = set(self._state.base_state.topology.iter_live_node_ids())
        target_nodes: list[int] = []
        for source_node_id in row.surface_nodes:
            source_key = str(int(source_node_id))
            if source_key not in lineage_transfer_map:
                raise InvalidStateTransitionError(
                    "surface lineage transport requires lineage map coverage "
                    "for every source surface node"
                )
            target_raw = lineage_transfer_map[source_key]
            try:
                target_node_id = int(target_raw)
            except ValueError as exc:
                raise InvalidStateTransitionError(
                    "surface lineage transport requires node-id target values"
                ) from exc
            if target_node_id not in live_nodes:
                raise InvalidStateTransitionError(
                    "surface lineage transport target node is not live"
                )
            target_nodes.append(target_node_id)
        return tuple(sorted(set(target_nodes)))

    def _transported_node_id(
        self,
        *,
        source_node_id: int,
        lineage_transfer_map: Mapping[str, str],
    ) -> int:
        source_key = str(int(source_node_id))
        if source_key not in lineage_transfer_map:
            raise InvalidStateTransitionError(
                "surface lineage transport requires endpoint node coverage"
            )
        try:
            return int(lineage_transfer_map[source_key])
        except ValueError as exc:
            raise InvalidStateTransitionError(
                "surface lineage transport endpoint target must be a node id"
            ) from exc

    def _surface_lineage_claim_flags(self) -> dict[str, bool]:
        return {
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "native_m6": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
        }

    def _topology_state_reabsorption_claim_flags(self) -> dict[str, bool]:
        flags = self._surface_lineage_claim_flags()
        flags["topology_mutating_movement_claim_allowed"] = False
        flags["adaptive_topology_movement_claim_allowed"] = False
        return flags

    def _topology_state_reabsorption_enabled(self) -> bool:
        return (
            bool(
                self._state.causal_modes.get(
                    "causal_topology_state_reabsorption_enabled",
                    False,
                )
            )
            and self._state.causal_modes.get(
                "causal_topology_state_reabsorption_policy",
            )
            == LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
        )

    def _topology_state_reabsorption_keys(self) -> set[str]:
        raw_keys = self._state.cached_quantities.get(
            "lgrc9v3_topology_state_reabsorption_idempotency_keys",
            [],
        )
        if not isinstance(raw_keys, list):
            raise SnapshotCompatibilityError(
                "topology-state reabsorption idempotency cache must be a sequence"
            )
        return {str(key) for key in raw_keys}

    def _store_topology_state_reabsorption_keys(self, keys: set[str]) -> None:
        self._state.cached_quantities[
            "lgrc9v3_topology_state_reabsorption_idempotency_keys"
        ] = sorted(keys)

    def _native_route_arbitration_enabled(self) -> bool:
        return (
            bool(
                self._state.causal_modes.get(
                    "native_lgrc_route_arbitration_enabled",
                    False,
                )
            )
            and self._state.causal_modes.get("native_lgrc_route_arbitration_policy")
            == LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
        )

    def _native_route_candidate_keys(self) -> set[str]:
        raw_keys = self._state.cached_quantities.get(
            "lgrc9v3_native_route_candidate_idempotency_keys",
            [],
        )
        if not isinstance(raw_keys, Sequence) or isinstance(raw_keys, str):
            raise SnapshotCompatibilityError(
                "native route candidate idempotency cache must be a sequence"
            )
        return {str(key) for key in raw_keys}

    def _store_native_route_candidate_keys(self, keys: set[str]) -> None:
        self._state.cached_quantities[
            "lgrc9v3_native_route_candidate_idempotency_keys"
        ] = sorted(keys)

    def _native_route_candidate_set_keys(self) -> set[str]:
        raw_keys = self._state.cached_quantities.get(
            "lgrc9v3_native_route_candidate_set_idempotency_keys",
            [],
        )
        if not isinstance(raw_keys, Sequence) or isinstance(raw_keys, str):
            raise SnapshotCompatibilityError(
                "native route candidate-set idempotency cache must be a sequence"
            )
        return {str(key) for key in raw_keys}

    def _store_native_route_candidate_set_keys(self, keys: set[str]) -> None:
        self._state.cached_quantities[
            "lgrc9v3_native_route_candidate_set_idempotency_keys"
        ] = sorted(keys)

    def _native_route_claim_flags(self) -> dict[str, bool]:
        flags = self._topology_state_reabsorption_claim_flags()
        flags.update(
            {
                "semantic_choice_claim_allowed": False,
                "native_lgrc_choice_selection_claim_allowed": False,
                "rc_identity_collapse_claim_allowed": False,
                "unrestricted_movement_claim_allowed": False,
            }
        )
        return flags

    def _surface_row_for_digest(
        self,
        surface_digest: str,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceRow | None:
        for row in reversed(self._state.causal_pulse_substrate_surface_log):
            if row.surface_digest == surface_digest:
                return row
        return None

    def _topology_state_reabsorption_record_for_digest(
        self,
        topology_state_reabsorption_digest: str,
    ) -> LGRC9V3TopologyStateReabsorptionRecord | None:
        for record in reversed(self._state.topology_state_reabsorption_log):
            if (
                record.topology_state_reabsorption_digest
                == topology_state_reabsorption_digest
            ):
                return record
        return None

    def _native_route_candidate_set_id(
        self,
        *,
        arbitration_window_id: str,
        source_surface_digest: str,
        candidate_routes: Sequence[Mapping[str, Any]],
    ) -> str:
        seed = digest_canonical_data(
            {
                "arbitration_window_id": str(arbitration_window_id),
                "source_surface_digest": str(source_surface_digest),
                "event_time_key": float(self._state.event_time_key),
                "scheduler_event_index": int(self._state.scheduler_event_index),
                "candidate_route_ids": [
                    str(route.get("candidate_route_id", index))
                    for index, route in enumerate(candidate_routes)
                ],
            }
        )
        return f"native-route-candidate-set:{seed[:32]}"

    def _native_route_candidate_from_spec(
        self,
        *,
        candidate_set_id: str,
        source_surface_digest: str,
        source_producer_record_id: str | None,
        source_topology_state_reabsorption_digest: str | None,
        spec: Mapping[str, Any],
        index: int,
    ) -> LGRC9V3NativeRouteCandidateRecord:
        score_components = {
            str(key): float(value)
            for key, value in dict(spec.get("candidate_score_components", {})).items()
        }
        runtime_visible_inputs = tuple(
            str(value)
            for value in spec.get(
                "candidate_runtime_visible_inputs",
                ("source_surface_digest", "candidate_score_components"),
            )
        )
        hidden_inputs = (
            set(score_components)
            | set(runtime_visible_inputs)
            | {str(value) for value in spec.get("candidate_hidden_inputs", ())}
        ).intersection(LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS)
        if hidden_inputs:
            raise InvalidParamsError(
                f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED}: "
                f"{sorted(hidden_inputs)}"
            )
        if not score_components:
            raise InvalidParamsError("native route candidate requires score components")
        candidate_source_surface_digest = str(
            spec.get("candidate_source_surface_digest", source_surface_digest)
        )
        if self._surface_row_for_digest(candidate_source_surface_digest) is None:
            raise InvalidStateTransitionError(
                "native route candidate requires committed source surface evidence"
            )
        candidate_reabsorption_digest = spec.get(
            "candidate_source_topology_state_reabsorption_digest",
            source_topology_state_reabsorption_digest,
        )
        if candidate_reabsorption_digest is not None:
            candidate_reabsorption_digest = str(candidate_reabsorption_digest)
            if (
                self._topology_state_reabsorption_record_for_digest(
                    candidate_reabsorption_digest
                )
                is None
            ):
                raise InvalidStateTransitionError(
                    "native route candidate requires committed topology-state "
                    "reabsorption evidence"
                )
        candidate_route_score = spec.get(
            "candidate_route_score",
            sum(score_components.values()),
        )
        if "candidate_budget_prediction" not in spec:
            raise InvalidParamsError(
                f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID}: "
                "candidate_budget_prediction is required"
            )
        budget_prediction = dict(spec["candidate_budget_prediction"])
        try:
            return LGRC9V3NativeRouteCandidateRecord(
                candidate_route_id=str(
                    spec.get("candidate_route_id", f"native-route-candidate:{index}")
                ),
                native_route_arbitration_policy_id=str(
                    self._state.causal_modes.get("native_lgrc_route_arbitration_policy")
                ),
                native_route_arbitration_enabled=True,
                candidate_set_id=candidate_set_id,
                candidate_source_surface_digest=candidate_source_surface_digest,
                candidate_source_producer_record_id=None
                if spec.get("candidate_source_producer_record_id", source_producer_record_id)
                is None
                else str(
                    spec.get(
                        "candidate_source_producer_record_id",
                        source_producer_record_id,
                    )
                ),
                candidate_source_topology_state_reabsorption_digest=(
                    candidate_reabsorption_digest
                ),
                route_intent=str(
                    spec.get("route_intent", LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE)
                ),
                candidate_topology_event_kind=str(
                    spec.get(
                        "candidate_topology_event_kind",
                        LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
                    )
                ),
                candidate_competing_sink_ids=tuple(
                    int(value)
                    for value in spec.get("candidate_competing_sink_ids", ())
                ),
                candidate_losing_sink_ids=tuple(
                    int(value) for value in spec.get("candidate_losing_sink_ids", ())
                ),
                candidate_selected_sink_id=int(spec["candidate_selected_sink_id"]),
                candidate_transferred_node_ids=tuple(
                    int(value)
                    for value in spec.get("candidate_transferred_node_ids", ())
                ),
                candidate_lineage_transfer_map={
                    str(key): str(value)
                    for key, value in dict(
                        spec.get("candidate_lineage_transfer_map", {})
                    ).items()
                },
                candidate_source_node_ids=tuple(
                    int(value) for value in spec.get("candidate_source_node_ids", ())
                ),
                candidate_target_node_ids=tuple(
                    int(value) for value in spec.get("candidate_target_node_ids", ())
                ),
                candidate_retired_node_ids=tuple(
                    int(value) for value in spec.get("candidate_retired_node_ids", ())
                ),
                candidate_source_edge_ids=tuple(
                    int(value) for value in spec.get("candidate_source_edge_ids", ())
                ),
                candidate_target_edge_ids=tuple(
                    int(value) for value in spec.get("candidate_target_edge_ids", ())
                ),
                candidate_retired_edge_ids=tuple(
                    int(value) for value in spec.get("candidate_retired_edge_ids", ())
                ),
                candidate_route_score=float(candidate_route_score),
                candidate_score_components=score_components,
                candidate_budget_prediction={
                    str(key): float(value) for key, value in budget_prediction.items()
                },
                candidate_order_key=str(
                    spec.get(
                        "candidate_order_key",
                        spec.get("candidate_route_id", f"native-route-candidate:{index}"),
                    )
                ),
                candidate_runtime_visible_inputs=runtime_visible_inputs,
                event_time_key=float(self._state.event_time_key),
                scheduler_event_index=int(self._state.scheduler_event_index),
                lgrc_runtime_level=str(self._state.lgrc_runtime_level),
                causal_layer_mode=str(self._state.causal_layer_mode),
                claim_flags=self._native_route_claim_flags(),
            )
        except ValueError as exc:
            message = str(exc)
            if "hidden input" in message:
                raise InvalidParamsError(
                    f"{LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED}: "
                    f"{message}"
                ) from exc
            raise InvalidParamsError(message) from exc

    def emit_native_route_candidate_set(
        self,
        *,
        arbitration_window_id: str,
        candidate_routes: Sequence[Mapping[str, Any]],
        source_surface_digest: str | None = None,
        source_producer_record_id: str | None = None,
        source_topology_state_reabsorption_digest: str | None = None,
        candidate_set_id: str | None = None,
        candidate_set_order_key: str = (
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
        ),
        unresolved_tie_policy: str = LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    ) -> dict[str, Any]:
        """Emit native route candidate evidence without selecting a route."""

        if not self._native_route_arbitration_enabled():
            return {
                "emitted": False,
                "reason_code": LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
                "candidate_records": (),
                "candidate_set_record": None,
            }
        candidate_specs = tuple(dict(route) for route in candidate_routes)
        if not candidate_specs:
            raise InvalidParamsError("native route candidate set requires candidates")
        resolved_source_digest = source_surface_digest
        if resolved_source_digest is None:
            resolved_source_digest = str(
                candidate_specs[0].get("candidate_source_surface_digest", "")
            )
        if not resolved_source_digest:
            raise InvalidParamsError(
                "native route candidate set requires source surface digest"
            )
        if self._surface_row_for_digest(str(resolved_source_digest)) is None:
            raise InvalidStateTransitionError(
                "native route candidate set requires committed source surface evidence"
            )
        resolved_candidate_set_id = candidate_set_id or self._native_route_candidate_set_id(
            arbitration_window_id=arbitration_window_id,
            source_surface_digest=str(resolved_source_digest),
            candidate_routes=candidate_specs,
        )
        unique_candidates: dict[str, LGRC9V3NativeRouteCandidateRecord] = {}
        for index, spec in enumerate(candidate_specs):
            record = self._native_route_candidate_from_spec(
                candidate_set_id=resolved_candidate_set_id,
                source_surface_digest=str(resolved_source_digest),
                source_producer_record_id=source_producer_record_id,
                source_topology_state_reabsorption_digest=(
                    source_topology_state_reabsorption_digest
                ),
                spec=spec,
                index=index,
            )
            assert record.candidate_route_digest is not None
            unique_candidates.setdefault(record.candidate_route_digest, record)
        if candidate_set_order_key == (
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
        ):
            ordered_candidates = tuple(
                sorted(
                    unique_candidates.values(),
                    key=lambda record: (
                        -float(record.candidate_route_score),
                        str(record.candidate_order_key),
                        str(record.candidate_route_id),
                    ),
                )
            )
        elif (
            candidate_set_order_key
            == LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING
        ):
            ordered_candidates = tuple(
                sorted(
                    unique_candidates.values(),
                    key=lambda record: str(record.candidate_route_digest),
                )
            )
        else:
            raise InvalidParamsError("unsupported native route candidate-set order key")
        candidate_route_digests = tuple(
            str(record.candidate_route_digest) for record in ordered_candidates
        )
        try:
            candidate_set_record = LGRC9V3NativeRouteCandidateSetRecord(
                candidate_set_id=resolved_candidate_set_id,
                native_route_arbitration_policy_id=str(
                    self._state.causal_modes.get("native_lgrc_route_arbitration_policy")
                ),
                native_route_arbitration_enabled=True,
                arbitration_window_id=str(arbitration_window_id),
                event_time_key=float(self._state.event_time_key),
                scheduler_event_index=int(self._state.scheduler_event_index),
                candidate_route_digests=candidate_route_digests,
                candidate_set_order_key=candidate_set_order_key,
                unresolved_tie_policy=unresolved_tie_policy,
                lgrc_runtime_level=str(self._state.lgrc_runtime_level),
                causal_layer_mode=str(self._state.causal_layer_mode),
                claim_flags=self._native_route_claim_flags(),
            )
        except ValueError as exc:
            raise InvalidParamsError(str(exc)) from exc
        candidate_keys = self._native_route_candidate_keys()
        new_candidate_records: list[LGRC9V3NativeRouteCandidateRecord] = []
        for record in ordered_candidates:
            assert record.candidate_route_digest is not None
            if record.candidate_route_digest in candidate_keys:
                continue
            candidate_keys.add(record.candidate_route_digest)
            self._state.native_route_candidate_log.append(record)
            new_candidate_records.append(record)
        self._store_native_route_candidate_keys(candidate_keys)
        set_keys = self._native_route_candidate_set_keys()
        assert candidate_set_record.idempotency_key is not None
        if candidate_set_record.idempotency_key in set_keys:
            return {
                "emitted": False,
                "reason_code": LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
                "candidate_records": tuple(new_candidate_records),
                "candidate_set_record": candidate_set_record,
            }
        set_keys.add(candidate_set_record.idempotency_key)
        self._store_native_route_candidate_set_keys(set_keys)
        self._state.native_route_candidate_set_log.append(candidate_set_record)
        return {
            "emitted": True,
            "reason_code": "native_route_candidate_set_emitted",
            "candidate_records": tuple(new_candidate_records),
            "candidate_set_record": candidate_set_record,
        }

    def _native_route_arbitration_keys(self) -> set[str]:
        raw_keys = self._state.cached_quantities.get(
            "lgrc9v3_native_route_arbitration_idempotency_keys",
            [],
        )
        if not isinstance(raw_keys, Sequence) or isinstance(raw_keys, str):
            raise SnapshotCompatibilityError(
                "native route-arbitration idempotency cache must be a sequence"
            )
        return {str(key) for key in raw_keys}

    def _store_native_route_arbitration_keys(self, keys: set[str]) -> None:
        self._state.cached_quantities[
            "lgrc9v3_native_route_arbitration_idempotency_keys"
        ] = sorted(keys)

    def _native_route_candidate_set_for_digest(
        self,
        candidate_set_digest: str,
    ) -> LGRC9V3NativeRouteCandidateSetRecord | None:
        for record in reversed(self._state.native_route_candidate_set_log):
            if record.candidate_set_digest == candidate_set_digest:
                return record
        return None

    def _native_route_candidates_by_digest(
        self,
    ) -> dict[str, LGRC9V3NativeRouteCandidateRecord]:
        candidates: dict[str, LGRC9V3NativeRouteCandidateRecord] = {}
        for record in self._state.native_route_candidate_log:
            assert record.candidate_route_digest is not None
            candidates[str(record.candidate_route_digest)] = record
        return candidates

    def _native_route_arbitration_record_for_reference(
        self,
        reference: str,
    ) -> LGRC9V3NativeRouteArbitrationRecord | None:
        for record in reversed(self._state.native_route_arbitration_log):
            if reference in {
                record.native_route_arbitration_record_id,
                str(record.native_route_arbitration_digest),
            }:
                return record
        return None

    def _candidate_set_order_is_valid(
        self,
        *,
        candidate_set: LGRC9V3NativeRouteCandidateSetRecord,
        candidates: Sequence[LGRC9V3NativeRouteCandidateRecord],
    ) -> bool:
        if candidate_set.candidate_set_order_key == (
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING
        ):
            expected = tuple(
                sorted(str(record.candidate_route_digest) for record in candidates)
            )
        elif candidate_set.candidate_set_order_key == (
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
        ):
            expected = tuple(
                str(record.candidate_route_digest)
                for record in sorted(
                    candidates,
                    key=lambda record: (
                        -float(record.candidate_route_score),
                        str(record.candidate_order_key),
                        str(record.candidate_route_id),
                    ),
                )
            )
        else:
            return False
        return expected == tuple(str(digest) for digest in candidate_set.candidate_route_digests)

    def _candidate_budget_prediction_is_valid(
        self,
        candidate: LGRC9V3NativeRouteCandidateRecord,
    ) -> bool:
        prediction = {
            str(key): float(value)
            for key, value in candidate.candidate_budget_prediction.items()
        }
        required = {
            "node_plus_packet_budget_before",
            "node_plus_packet_budget_after",
            "node_plus_packet_budget_error",
        }
        if not required.issubset(prediction):
            return False
        if abs(prediction["node_plus_packet_budget_error"]) > 1e-12:
            return False
        return (
            abs(
                prediction["node_plus_packet_budget_after"]
                - prediction["node_plus_packet_budget_before"]
            )
            <= 1e-12
        )

    def _native_route_source_lineage_ids(
        self,
        candidate: LGRC9V3NativeRouteCandidateRecord,
    ) -> dict[int, str]:
        assert candidate.candidate_route_digest is not None
        return {
            int(node_id): f"native-route:{candidate.candidate_route_digest}:{int(node_id)}"
            for node_id in candidate.candidate_transferred_node_ids
        }

    def _selected_topology_event_id_for_candidate(
        self,
        candidate: LGRC9V3NativeRouteCandidateRecord,
    ) -> str:
        if candidate.candidate_topology_event_kind in {
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        }:
            return build_lgrc9v3_collapse_reabsorption_event_id(
                topology_event_kind=candidate.candidate_topology_event_kind,
                selected_sink_id=int(candidate.candidate_selected_sink_id),
                losing_sink_ids=tuple(int(value) for value in candidate.candidate_losing_sink_ids),
                event_time_key=float(candidate.event_time_key),
            )
        assert candidate.candidate_route_digest is not None
        return (
            "native-route-selected-topology-event:"
            f"{candidate.candidate_route_digest[:32]}"
        )

    def _selected_topology_event_artifact_for_candidate(
        self,
        candidate: LGRC9V3NativeRouteCandidateRecord,
        *,
        native_route_arbitration_record_id: str | None,
        native_route_arbitration_digest: str | None = None,
        candidate_set_digest: str,
    ) -> dict[str, Any]:
        if candidate.candidate_topology_event_kind not in {
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        }:
            raise InvalidStateTransitionError(
                "native route arbitration commit supports collapse/reabsorption events"
            )
        assert candidate.candidate_route_digest is not None
        budget = self._runtime_budget_surface()
        result = process_lgrc9v3_collapse_reabsorption(
            topology_event_kind=candidate.candidate_topology_event_kind,
            competing_sink_ids=tuple(
                int(value) for value in candidate.candidate_competing_sink_ids
            ),
            selected_sink_id=int(candidate.candidate_selected_sink_id),
            losing_sink_ids=tuple(
                int(value) for value in candidate.candidate_losing_sink_ids
            ),
            transferred_node_ids=tuple(
                int(value) for value in candidate.candidate_transferred_node_ids
            ),
            lineage_transfer_map={
                int(key): str(value)
                for key, value in candidate.candidate_lineage_transfer_map.items()
            },
            source_lineage_ids=self._native_route_source_lineage_ids(candidate),
            target_lineage_id=str(candidate.candidate_selected_sink_id),
            node_proper_time=self._state.node_proper_time,
            coherence_transfer_amount=0.0,
            budget_before=budget,
            event_time_key=float(candidate.event_time_key),
            scheduler_event_index=int(candidate.scheduler_event_index),
            checkpoint_index=int(self._state.checkpoint_index),
            packet_ledger=self._state.packet_ledger,
            budget_after=budget,
            collapse_reabsorption_allowed=True,
            native_route_arbitration_record_id=native_route_arbitration_record_id,
            native_route_arbitration_digest=native_route_arbitration_digest,
            native_route_selected_candidate_route_id=candidate.candidate_route_id,
            native_route_selected_candidate_route_digest=(
                candidate.candidate_route_digest
            ),
            native_route_candidate_set_digest=candidate_set_digest,
        )
        return result.to_artifact()

    def _selected_topology_event_for_candidate(
        self,
        candidate: LGRC9V3NativeRouteCandidateRecord,
        *,
        native_route_arbitration_record_id: str | None,
        native_route_arbitration_digest: str | None = None,
        candidate_set_digest: str,
    ) -> tuple[str, str]:
        topology_event_artifact = self._selected_topology_event_artifact_for_candidate(
            candidate,
            native_route_arbitration_record_id=native_route_arbitration_record_id,
            native_route_arbitration_digest=native_route_arbitration_digest,
            candidate_set_digest=candidate_set_digest,
        )
        topology_event_id = str(topology_event_artifact["topology_event_id"])
        return topology_event_id, build_lgrc9v3_topology_event_digest(
            topology_event_artifact
        )

    def _emit_native_route_arbitration_record(
        self,
        *,
        candidate_set: LGRC9V3NativeRouteCandidateSetRecord,
        rejected_candidate_route_digests: Sequence[str],
        arbitration_reason_code: str,
        arbitration_score: float,
        arbitration_rule: str,
        arbitration_runtime_visible_inputs: Sequence[str],
        selected_candidate: LGRC9V3NativeRouteCandidateRecord | None = None,
    ) -> LGRC9V3NativeRouteArbitrationRecord:
        selected_topology_event_id: str | None = None
        selected_topology_event_digest: str | None = None
        selected_candidate_route_id: str | None = None
        selected_candidate_route_digest: str | None = None
        if selected_candidate is not None:
            selected_topology_event_id = self._selected_topology_event_id_for_candidate(
                selected_candidate
            )
            selected_candidate_route_id = selected_candidate.candidate_route_id
            selected_candidate_route_digest = selected_candidate.candidate_route_digest
        record_seed = digest_canonical_data(
            {
                "candidate_set_digest": candidate_set.candidate_set_digest,
                "selected_candidate_route_digest": selected_candidate_route_digest,
                "arbitration_reason_code": arbitration_reason_code,
                "arbitration_rule": arbitration_rule,
                "selected_topology_event_id": selected_topology_event_id,
            }
        )
        record_id = f"native-route-arbitration:{record_seed[:32]}"
        if selected_candidate is not None:
            _, selected_topology_event_digest = self._selected_topology_event_for_candidate(
                selected_candidate,
                native_route_arbitration_record_id=record_id,
                native_route_arbitration_digest=None,
                candidate_set_digest=str(candidate_set.candidate_set_digest),
            )
        try:
            record = LGRC9V3NativeRouteArbitrationRecord(
                native_route_arbitration_record_id=record_id,
                native_route_arbitration_policy_id=str(
                    self._state.causal_modes.get("native_lgrc_route_arbitration_policy")
                ),
                native_route_arbitration_enabled=True,
                candidate_set_id=candidate_set.candidate_set_id,
                candidate_set_digest=str(candidate_set.candidate_set_digest),
                selected_candidate_route_id=selected_candidate_route_id,
                selected_candidate_route_digest=selected_candidate_route_digest,
                rejected_candidate_route_digests=tuple(
                    str(digest) for digest in rejected_candidate_route_digests
                ),
                arbitration_reason_code=arbitration_reason_code,
                arbitration_score=float(arbitration_score),
                arbitration_rule=arbitration_rule,
                arbitration_runtime_visible_inputs=tuple(
                    str(value) for value in arbitration_runtime_visible_inputs
                ),
                selected_topology_event_id=selected_topology_event_id,
                selected_topology_event_digest=selected_topology_event_digest,
                event_time_key=float(self._state.event_time_key),
                scheduler_event_index=int(self._state.scheduler_event_index),
                lgrc_runtime_level=str(self._state.lgrc_runtime_level),
                causal_layer_mode=str(self._state.causal_layer_mode),
                claim_flags=self._native_route_claim_flags(),
            )
        except ValueError as exc:
            raise InvalidParamsError(str(exc)) from exc
        keys = self._native_route_arbitration_keys()
        assert record.idempotency_key is not None
        if record.idempotency_key not in keys:
            keys.add(record.idempotency_key)
            self._store_native_route_arbitration_keys(keys)
            self._state.native_route_arbitration_log.append(record)
        return record

    def arbitrate_native_route_candidate_set(
        self,
        *,
        candidate_set_digest: str,
        arbitration_rule: str = "highest_score",
        arbitration_runtime_visible_inputs: Sequence[str] = (
            "candidate_route_score",
            "candidate_order_key",
            "candidate_set_order_key",
        ),
    ) -> dict[str, Any]:
        """Emit a native route-arbitration record without committing topology."""

        if not self._native_route_arbitration_enabled():
            return {
                "emitted": False,
                "reason_code": LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
                "route_arbitration_record": None,
            }
        hidden_inputs = set(str(value) for value in arbitration_runtime_visible_inputs)
        hidden_inputs = hidden_inputs.intersection(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS
        )
        candidate_set = self._native_route_candidate_set_for_digest(
            str(candidate_set_digest)
        )
        if candidate_set is None:
            raise InvalidStateTransitionError(
                "native route arbitration requires a committed candidate set"
            )
        candidates_by_digest = self._native_route_candidates_by_digest()
        missing_digests = [
            str(digest)
            for digest in candidate_set.candidate_route_digests
            if str(digest) not in candidates_by_digest
        ]
        if missing_digests:
            raise InvalidStateTransitionError(
                "native route arbitration requires committed candidate records"
            )
        candidates = tuple(
            candidates_by_digest[str(digest)]
            for digest in candidate_set.candidate_route_digests
        )
        if hidden_inputs:
            record = self._emit_native_route_arbitration_record(
                candidate_set=candidate_set,
                rejected_candidate_route_digests=tuple(
                    str(digest) for digest in candidate_set.candidate_route_digests
                ),
                arbitration_reason_code=(
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED
                ),
                arbitration_score=0.0,
                arbitration_rule=arbitration_rule,
                arbitration_runtime_visible_inputs=("runtime_visible_input_validation",),
            )
            return {
                "emitted": True,
                "reason_code": record.arbitration_reason_code,
                "route_arbitration_record": record,
            }
        if not candidates:
            record = self._emit_native_route_arbitration_record(
                candidate_set=candidate_set,
                rejected_candidate_route_digests=(),
                arbitration_reason_code=(
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES
                ),
                arbitration_score=0.0,
                arbitration_rule=arbitration_rule,
                arbitration_runtime_visible_inputs=arbitration_runtime_visible_inputs,
            )
            return {
                "emitted": True,
                "reason_code": record.arbitration_reason_code,
                "route_arbitration_record": record,
            }
        if not self._candidate_set_order_is_valid(
            candidate_set=candidate_set,
            candidates=candidates,
        ):
            record = self._emit_native_route_arbitration_record(
                candidate_set=candidate_set,
                rejected_candidate_route_digests=tuple(
                    str(digest) for digest in candidate_set.candidate_route_digests
                ),
                arbitration_reason_code=(
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID
                ),
                arbitration_score=0.0,
                arbitration_rule=arbitration_rule,
                arbitration_runtime_visible_inputs=arbitration_runtime_visible_inputs,
            )
            return {
                "emitted": True,
                "reason_code": record.arbitration_reason_code,
                "route_arbitration_record": record,
            }
        invalid_budget = [
            candidate
            for candidate in candidates
            if not self._candidate_budget_prediction_is_valid(candidate)
        ]
        if invalid_budget:
            record = self._emit_native_route_arbitration_record(
                candidate_set=candidate_set,
                rejected_candidate_route_digests=tuple(
                    str(digest) for digest in candidate_set.candidate_route_digests
                ),
                arbitration_reason_code=(
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID
                ),
                arbitration_score=0.0,
                arbitration_rule=arbitration_rule,
                arbitration_runtime_visible_inputs=arbitration_runtime_visible_inputs,
            )
            return {
                "emitted": True,
                "reason_code": record.arbitration_reason_code,
                "route_arbitration_record": record,
            }
        best_score = max(float(candidate.candidate_route_score) for candidate in candidates)
        top_candidates = tuple(
            candidate
            for candidate in candidates
            if abs(float(candidate.candidate_route_score) - best_score) <= 1e-12
        )
        if len(top_candidates) > 1 and (
            candidate_set.unresolved_tie_policy
            == LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED
        ):
            record = self._emit_native_route_arbitration_record(
                candidate_set=candidate_set,
                rejected_candidate_route_digests=tuple(
                    str(digest) for digest in candidate_set.candidate_route_digests
                ),
                arbitration_reason_code=(
                    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE
                ),
                arbitration_score=best_score,
                arbitration_rule=arbitration_rule,
                arbitration_runtime_visible_inputs=arbitration_runtime_visible_inputs,
            )
            return {
                "emitted": True,
                "reason_code": record.arbitration_reason_code,
                "route_arbitration_record": record,
            }
        selected_candidate = top_candidates[0]
        if len(top_candidates) > 1 and (
            candidate_set.unresolved_tie_policy
            == LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_DECLARED_TIEBREAKER
        ):
            reason = (
                LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_DECLARED_LOCAL_PREFERENCE
            )
        else:
            reason = LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE
        selected_digest = str(selected_candidate.candidate_route_digest)
        record = self._emit_native_route_arbitration_record(
            candidate_set=candidate_set,
            selected_candidate=selected_candidate,
            rejected_candidate_route_digests=tuple(
                str(digest)
                for digest in candidate_set.candidate_route_digests
                if str(digest) != selected_digest
            ),
            arbitration_reason_code=reason,
            arbitration_score=float(selected_candidate.candidate_route_score),
            arbitration_rule=arbitration_rule,
            arbitration_runtime_visible_inputs=arbitration_runtime_visible_inputs,
        )
        return {
            "emitted": True,
            "reason_code": record.arbitration_reason_code,
            "route_arbitration_record": record,
        }

    def commit_native_route_arbitration_selection(
        self,
        *,
        native_route_arbitration_reference: str,
    ) -> dict[str, Any]:
        """Commit the selected topology event authorized by route arbitration."""

        record = self._native_route_arbitration_record_for_reference(
            str(native_route_arbitration_reference)
        )
        if record is None:
            raise InvalidStateTransitionError(
                "native route arbitration commit requires committed arbitration record"
            )
        if not record.selected_candidate_route_digest:
            raise InvalidStateTransitionError(
                "native route arbitration commit requires selected candidate"
            )
        for topology_event in self._state.topology_event_log:
            payload = self._topology_event_payload(topology_event)
            if (
                payload.get("native_route_arbitration_record_id")
                == record.native_route_arbitration_record_id
            ):
                return {
                    "committed": False,
                    "reason_code": LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
                    "route_arbitration_record": record,
                    "selected_candidate_route_record": None,
                    "topology_events": (),
                }
        candidates = self._native_route_candidates_by_digest()
        candidate = candidates.get(str(record.selected_candidate_route_digest))
        if candidate is None:
            raise InvalidStateTransitionError(
                "native route arbitration selected candidate is missing"
            )
        candidate_set = self._native_route_candidate_set_for_digest(
            str(record.candidate_set_digest)
        )
        if candidate_set is None:
            raise InvalidStateTransitionError(
                "native route arbitration selected candidate set is missing"
            )
        if str(record.selected_candidate_route_digest) not in {
            str(digest) for digest in candidate_set.candidate_route_digests
        }:
            raise InvalidStateTransitionError(
                "native route arbitration selected candidate is outside candidate set"
            )
        if candidate.candidate_topology_event_kind not in {
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        }:
            raise InvalidStateTransitionError(
                "native route arbitration commit supports collapse/reabsorption events"
            )
        expected_event_id, expected_event_digest = (
            self._selected_topology_event_for_candidate(
                candidate,
                native_route_arbitration_record_id=(
                    record.native_route_arbitration_record_id
                ),
                native_route_arbitration_digest=None,
                candidate_set_digest=str(candidate_set.candidate_set_digest),
            )
        )
        if expected_event_id != record.selected_topology_event_id:
            raise InvalidStateTransitionError(
                "native route arbitration selected topology event id mismatch"
            )
        if expected_event_digest != record.selected_topology_event_digest:
            raise InvalidStateTransitionError(
                "native_route_arbitration_stale_candidate"
            )
        topology_events = self.process_causal_collapse_reabsorption(
            topology_event_kind=candidate.candidate_topology_event_kind,
            competing_sink_ids=tuple(
                int(value) for value in candidate.candidate_competing_sink_ids
            ),
            selected_sink_id=int(candidate.candidate_selected_sink_id),
            losing_sink_ids=tuple(
                int(value) for value in candidate.candidate_losing_sink_ids
            ),
            transferred_node_ids=tuple(
                int(value) for value in candidate.candidate_transferred_node_ids
            ),
            lineage_transfer_map={
                int(key): str(value)
                for key, value in candidate.candidate_lineage_transfer_map.items()
            },
            source_lineage_ids=self._native_route_source_lineage_ids(candidate),
            target_lineage_id=str(candidate.candidate_selected_sink_id),
            coherence_transfer_amount=0.0,
            native_route_arbitration_record_id=(
                record.native_route_arbitration_record_id
            ),
            native_route_arbitration_digest=str(record.native_route_arbitration_digest),
            native_route_selected_candidate_route_id=str(
                record.selected_candidate_route_id
            ),
            native_route_selected_candidate_route_digest=(
                str(record.selected_candidate_route_digest)
            ),
            native_route_candidate_set_digest=str(record.candidate_set_digest),
        )
        committed_event_payload = self._topology_event_payload(topology_events[0])
        committed_event_digest = build_lgrc9v3_topology_event_digest(
            committed_event_payload
        )
        if committed_event_digest != record.selected_topology_event_digest:
            raise InvalidStateTransitionError(
                "native route arbitration committed topology digest mismatch"
            )
        return {
            "committed": True,
            "reason_code": record.arbitration_reason_code,
            "route_arbitration_record": record,
            "selected_candidate_route_record": candidate,
            "topology_events": tuple(topology_events),
            "selected_topology_event_digest": committed_event_digest,
            "surface_lineage_records": tuple(
                self._state.causal_pulse_substrate_surface_lineage_log
            ),
            "topology_state_reabsorption_records": tuple(
                self._state.topology_state_reabsorption_log
            ),
        }

    def _active_node_state_map(self) -> dict[int, float]:
        return {
            int(node_id): float(node.coherence)
            for node_id, node in sorted(self._state.base_state.nodes.items())
        }

    def _edge_state_map_for_edges(
        self,
        edge_ids: Sequence[int],
    ) -> dict[int, dict[int, float]]:
        edge_state: dict[int, dict[int, float]] = {}
        for edge_id in sorted({int(edge_id) for edge_id in edge_ids}):
            edge = self._state.base_state.port_edges.get(edge_id)
            if edge is None:
                continue
            edge_state[edge_id] = {
                0: float(edge.node_u),
                1: float(edge.port_u),
                2: float(edge.node_v),
                3: float(edge.port_v),
                4: float(edge.conductance),
                5: float(edge.flux_uv),
            }
        return edge_state

    def _active_state_digest(self) -> str:
        node_state = {
            str(node_id): value
            for node_id, value in self._active_node_state_map().items()
        }
        edge_state = {
            str(edge_id): {str(key): value for key, value in values.items()}
            for edge_id, values in self._edge_state_map_for_edges(
                tuple(self._state.base_state.port_edges)
            ).items()
        }
        return digest_canonical_data(
            {
                "active_node_state": node_state,
                "active_edge_state": edge_state,
            }
        )

    def _packet_ledger_digest(self, packet_ledger: Any) -> str:
        return digest_canonical_data(
            {"lgrc9v3_packet_ledger": packet_ledger.to_artifact()}
        )

    def _incident_edge_ids_for_nodes(self, node_ids: Sequence[int]) -> tuple[int, ...]:
        edge_ids: set[int] = set()
        for node_id in node_ids:
            if self._state.base_state.topology.has_node(int(node_id)):
                edge_ids.update(
                    int(edge_id)
                    for edge_id in self._state.base_state.topology.incident_edge_ids(
                        int(node_id)
                    )
                )
        return tuple(sorted(edge_ids))

    def _emit_topology_state_reabsorption_record(
        self,
        *,
        topology_event: GRCEvent,
        source_node_ids: Sequence[int],
        target_node_ids: Sequence[int],
        retired_node_ids: Sequence[int],
        lineage_transfer_map: Mapping[int | str, int | str],
        node_state_before: Mapping[int, float],
        edge_state_before: Mapping[int, Mapping[int, float]],
        packet_ledger_before: Any,
        packet_ledger_after: Any,
        active_state_digest_before: str,
        active_state_digest_after: str,
        state_reabsorption_action: str,
    ) -> LGRC9V3TopologyStateReabsorptionRecord | None:
        if not self._topology_state_reabsorption_enabled():
            return None
        topology_artifact = self._topology_event_payload(topology_event)
        topology_event_id = str(topology_artifact.get("topology_event_id") or "")
        if not topology_event_id:
            raise InvalidStateTransitionError(
                "topology-state reabsorption requires committed topology event"
            )
        topology_event_kind = str(
            topology_artifact.get("topology_event_kind") or topology_event.kind
        )
        topology_event_digest = build_lgrc9v3_topology_event_digest(
            topology_artifact
        )
        node_state_after = self._active_node_state_map()
        active_total_before = float(
            sum(float(value) for value in node_state_before.values())
        )
        active_total_after = float(
            sum(float(value) for value in node_state_after.values())
        )
        source_edges = self._incident_edge_ids_for_nodes(source_node_ids)
        target_edges = self._incident_edge_ids_for_nodes(target_node_ids)
        retired_edges = self._incident_edge_ids_for_nodes(retired_node_ids)
        edge_ids = tuple(sorted(set(source_edges) | set(target_edges) | set(retired_edges)))
        record_seed = build_lgrc9v3_topology_state_reabsorption_record_digest(
            {
                "topology_event_digest": topology_event_digest,
                "active_state_digest_before": active_state_digest_before,
                "active_state_digest_after": active_state_digest_after,
            }
        )
        record = LGRC9V3TopologyStateReabsorptionRecord(
            topology_state_reabsorption_record_id=(
                f"topology-state-reabsorption:{record_seed[:32]}"
            ),
            topology_state_reabsorption_policy_id=(
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
            ),
            topology_state_reabsorption_enabled=True,
            topology_state_reabsorption_validated=bool(
                self._state.causal_modes.get(
                    "causal_topology_state_reabsorption_validated",
                    False,
                )
            ),
            lgrc_runtime_level=str(self._state.lgrc_runtime_level),
            causal_layer_mode=str(self._state.causal_layer_mode),
            topology_event_id=topology_event_id,
            topology_event_kind=topology_event_kind,
            topology_event_digest=topology_event_digest,
            topology_event_committed=True,
            event_time_key=float(
                topology_artifact.get("event_time_key", self._state.event_time_key)
            ),
            scheduler_event_index=int(
                topology_artifact.get(
                    "scheduler_event_index",
                    self._state.scheduler_event_index,
                )
            ),
            checkpoint_index=int(
                topology_artifact.get("checkpoint_index", self._state.checkpoint_index)
            ),
            lineage_transfer_map={
                str(source): str(target)
                for source, target in lineage_transfer_map.items()
            },
            source_node_ids=tuple(int(node_id) for node_id in source_node_ids),
            target_node_ids=tuple(int(node_id) for node_id in target_node_ids),
            retired_node_ids=tuple(int(node_id) for node_id in retired_node_ids),
            source_edge_ids=source_edges,
            target_edge_ids=target_edges,
            retired_edge_ids=retired_edges,
            node_state_before=dict(node_state_before),
            node_state_after=node_state_after,
            edge_state_before=dict(edge_state_before),
            edge_state_after=self._edge_state_map_for_edges(edge_ids),
            packet_ledger_digest_before=self._packet_ledger_digest(
                packet_ledger_before
            ),
            packet_ledger_digest_after=self._packet_ledger_digest(packet_ledger_after),
            active_node_state_total_before=active_total_before,
            active_node_state_total_after=active_total_after,
            packet_ledger_node_total_before=float(
                packet_ledger_before.node_coherence_total
            ),
            packet_ledger_node_total_after=float(
                packet_ledger_after.node_coherence_total
            ),
            packet_ledger_in_flight_packet_total_before=float(
                packet_ledger_before.in_flight_packet_total
            ),
            packet_ledger_in_flight_packet_total_after=float(
                packet_ledger_after.in_flight_packet_total
            ),
            packet_ledger_conserved_budget_total_before=float(
                packet_ledger_before.conserved_budget_total
            ),
            packet_ledger_conserved_budget_total_after=float(
                packet_ledger_after.conserved_budget_total
            ),
            node_plus_packet_budget_before=float(
                packet_ledger_before.conserved_budget_total
            ),
            node_plus_packet_budget_after=float(
                packet_ledger_after.conserved_budget_total
            ),
            node_plus_packet_budget_error=float(
                packet_ledger_after.conserved_budget_total
                - packet_ledger_before.conserved_budget_total
            ),
            active_state_digest_before=active_state_digest_before,
            active_state_digest_after=active_state_digest_after,
            state_reabsorption_action=state_reabsorption_action,
            claim_flags=self._topology_state_reabsorption_claim_flags(),
        )
        keys = self._topology_state_reabsorption_keys()
        if str(record.idempotency_key) in keys:
            return None
        keys.add(str(record.idempotency_key))
        self._store_topology_state_reabsorption_keys(keys)
        self._state.topology_state_reabsorption_log.append(record)
        return record

    def _apply_collapse_topology_state_reabsorption(
        self,
        *,
        topology_event: GRCEvent,
        collapse_result: Any,
        transport_result: Any,
        packet_ledger_before: Any,
        packet_ledger_after: Any,
        node_state_before: Mapping[int, float],
        edge_state_before: Mapping[int, Mapping[int, float]],
        active_state_digest_before: str,
    ) -> LGRC9V3TopologyStateReabsorptionRecord | None:
        if not self._topology_state_reabsorption_enabled():
            return None
        settled_amount = float(getattr(transport_result, "settled_amount_total", 0.0))
        transfer_amount = float(
            getattr(collapse_result, "coherence_transfer_amount", 0.0)
        )
        selected_sink_id = int(collapse_result.selected_sink_id)
        if selected_sink_id not in self._state.base_state.nodes:
            raise InvalidStateTransitionError(
                "topology-state reabsorption target node is not live"
            )
        if settled_amount > 0.0:
            self._state.base_state.nodes[selected_sink_id].coherence += settled_amount
        if transfer_amount > 0.0:
            transferred_node_ids = tuple(
                int(node_id) for node_id in collapse_result.transferred_node_ids
            )
            available = sum(
                float(self._state.base_state.nodes[node_id].coherence)
                for node_id in transferred_node_ids
                if node_id in self._state.base_state.nodes
            )
            if transfer_amount > available + 1e-12:
                raise InvalidStateTransitionError(
                    "topology-state reabsorption transfer exceeds source coherence"
                )
            remaining = transfer_amount
            for node_id in transferred_node_ids:
                if node_id not in self._state.base_state.nodes:
                    continue
                debit = min(
                    remaining,
                    float(self._state.base_state.nodes[node_id].coherence),
                )
                self._state.base_state.nodes[node_id].coherence -= debit
                remaining -= debit
                if remaining <= 1e-12:
                    break
            self._state.base_state.nodes[selected_sink_id].coherence += transfer_amount
        active_state_digest_after = self._active_state_digest()
        lineage_targets = {
            str(target) for target in dict(collapse_result.lineage_transfer_map).values()
        }
        state_reabsorption_action = (
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED
            if len(collapse_result.transferred_node_ids) > 1
            or len(lineage_targets) == 1
            else LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED
        )
        return self._emit_topology_state_reabsorption_record(
            topology_event=topology_event,
            source_node_ids=tuple(
                int(node_id) for node_id in collapse_result.transferred_node_ids
            ),
            target_node_ids=(selected_sink_id,),
            retired_node_ids=tuple(
                int(node_id) for node_id in collapse_result.losing_sink_ids
            ),
            lineage_transfer_map=collapse_result.lineage_transfer_map,
            node_state_before=node_state_before,
            edge_state_before=edge_state_before,
            packet_ledger_before=packet_ledger_before,
            packet_ledger_after=packet_ledger_after,
            active_state_digest_before=active_state_digest_before,
            active_state_digest_after=active_state_digest_after,
            state_reabsorption_action=state_reabsorption_action,
        )

    def _build_transported_surface_row(
        self,
        *,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
        topology_artifact: Mapping[str, Any],
        topology_event_id: str,
        topology_event_digest: str,
        lineage_transfer_map: Mapping[str, str],
        target_nodes: Sequence[int],
        scheduler_event_index: int,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceRow:
        source_node_id = self._transported_node_id(
            source_node_id=int(row.source_node_id),
            lineage_transfer_map=lineage_transfer_map,
        )
        target_node_id = self._transported_node_id(
            source_node_id=int(row.target_node_id),
            lineage_transfer_map=lineage_transfer_map,
        )
        surface_state_digest = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "transported_from_surface_digest": row.surface_digest,
                "topology_event_digest": topology_event_digest,
                "target_surface_nodes": tuple(int(node_id) for node_id in target_nodes),
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "checkpoint_index": int(
                    topology_artifact.get(
                        "checkpoint_index",
                        self._state.checkpoint_index,
                    )
                ),
            }
        )
        return LGRC9V3CausalPulseSubstrateSurfaceRow(
            surface_id=f"{row.surface_id}:transported:{topology_event_id}",
            surface_policy_id=row.surface_policy_id,
            surface_policy_enabled=row.surface_policy_enabled,
            surface_policy_validated=row.surface_policy_validated,
            lgrc_runtime_level=str(self._state.lgrc_runtime_level),
            route_aspect_id=row.route_aspect_id,
            route_aspect_digest=row.route_aspect_digest,
            pulse_event_id=row.pulse_event_id,
            pulse_packet_id=row.pulse_packet_id,
            pulse_event_kind=row.pulse_event_kind,
            pulse_channel_id=row.pulse_channel_id,
            pulse_route_step=int(row.pulse_route_step),
            event_time_key=float(
                topology_artifact.get("event_time_key", self._state.event_time_key)
            ),
            scheduler_event_index=scheduler_event_index,
            node_proper_time=dict(self._state.node_proper_time),
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            contact_amount=float(row.contact_amount),
            surface_state_id=f"{row.surface_state_id}:transported:{topology_event_id}",
            surface_state_digest=surface_state_digest,
            surface_kind=row.surface_kind,
            surface_nodes=tuple(int(node_id) for node_id in target_nodes),
            surface_values_before={
                "transported_from_surface_id": row.surface_id,
                "transported_from_surface_digest": row.surface_digest,
                "topology_event_id": topology_event_id,
                "topology_event_digest": topology_event_digest,
            },
            surface_values_after={
                **dict(row.surface_values_after),
                "transported_surface_current": True,
                "transported_from_surface_id": row.surface_id,
                "transported_from_surface_digest": row.surface_digest,
                "transported_by_topology_event_id": topology_event_id,
                "transported_by_topology_event_digest": topology_event_digest,
                "source_surface_nodes": [
                    int(node_id) for node_id in row.surface_nodes
                ],
                "target_surface_nodes": [int(node_id) for node_id in target_nodes],
            },
            runtime_visible_inputs=tuple(
                dict.fromkeys(
                    (
                        *tuple(row.runtime_visible_inputs),
                        "committed_topology_event",
                        "lineage_transfer_map",
                    )
                )
            ),
            surface_update_policy={
                **dict(row.surface_update_policy),
                "lineage_transport_policy": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
                ),
            },
            surface_budget_surface=row.surface_budget_surface,
            surface_budget_before=float(row.surface_budget_after),
            surface_budget_after=float(row.surface_budget_after),
            surface_budget_error=0.0,
            lineage_status=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
            producer_records=(),
            claim_flags=self._surface_lineage_claim_flags(),
        )

    def _build_surface_transport_record(
        self,
        *,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
        topology_event: GRCEvent | Mapping[str, Any],
        transported_row: LGRC9V3CausalPulseSubstrateSurfaceRow | None = None,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceLineageRecord:
        topology_artifact = self._topology_event_payload(topology_event)
        topology_event_id = str(
            topology_artifact.get("topology_event_id")
            or topology_artifact.get("expansion_id")
            or topology_artifact.get("transport_id")
            or ""
        )
        if not topology_event_id:
            raise InvalidStateTransitionError(
                "surface lineage transport requires a committed topology event id"
            )
        topology_event_kind = str(
            topology_artifact.get("topology_event_kind")
            or (topology_event.kind if isinstance(topology_event, GRCEvent) else "")
        )
        if not topology_event_kind:
            raise InvalidStateTransitionError(
                "surface lineage transport requires a topology event kind"
            )
        topology_event_digest = build_lgrc9v3_topology_event_digest(
            topology_artifact
        )
        lineage_transfer_map = self._topology_event_lineage_transfer_map(
            topology_artifact
        )
        target_nodes = self._transported_surface_node_ids(
            row=row,
            lineage_transfer_map=lineage_transfer_map,
        )
        budget = self._runtime_budget_surface()
        transported_surface_seed = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "source_surface_digest": row.surface_digest,
                "topology_event_digest": topology_event_digest,
                "target_surface_nodes": target_nodes,
            }
        )
        record_seed = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "source_surface_digest": row.surface_digest,
                "topology_event_digest": topology_event_digest,
                "lineage_action": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
                ),
                "transported_surface_digest": transported_surface_seed,
            }
        )
        scheduler_event_index = max(
            int(topology_artifact.get("scheduler_event_index", 0)) + 1,
            int(row.scheduler_event_index) + 1,
            int(self._state.scheduler_event_index),
        )
        transported_row = transported_row or self._build_transported_surface_row(
            row=row,
            topology_artifact=topology_artifact,
            topology_event_id=topology_event_id,
            topology_event_digest=topology_event_digest,
            lineage_transfer_map=lineage_transfer_map,
            target_nodes=target_nodes,
            scheduler_event_index=scheduler_event_index,
        )
        return LGRC9V3CausalPulseSubstrateSurfaceLineageRecord(
            surface_lineage_record_id=f"surface-lineage:{record_seed[:32]}",
            surface_lineage_policy_id=(
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
            ),
            surface_lineage_transport_enabled=True,
            surface_lineage_transport_validated=bool(
                self._state.causal_modes.get(
                    "causal_pulse_substrate_surface_lineage_transport_validated",
                    False,
                )
            ),
            lgrc_runtime_level=str(self._state.lgrc_runtime_level),
            causal_layer_mode=str(self._state.causal_layer_mode),
            source_surface_id=row.surface_id,
            source_surface_digest=row.surface_digest,
            topology_event_id=topology_event_id,
            topology_event_kind=topology_event_kind,
            topology_event_digest=topology_event_digest,
            event_time_key=float(
                topology_artifact.get("event_time_key", self._state.event_time_key)
            ),
            scheduler_event_index=scheduler_event_index,
            checkpoint_index=int(
                topology_artifact.get("checkpoint_index", self._state.checkpoint_index)
            ),
            lineage_transfer_map=lineage_transfer_map,
            source_surface_nodes=tuple(int(node_id) for node_id in row.surface_nodes),
            target_surface_nodes=target_nodes,
            lineage_action=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
            lineage_status=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
            surface_budget_surface=row.surface_budget_surface,
            surface_budget_before=float(row.surface_budget_after),
            surface_budget_after=float(row.surface_budget_after),
            surface_budget_error=0.0,
            node_plus_packet_budget_before=budget,
            node_plus_packet_budget_after=budget,
            node_plus_packet_budget_error=0.0,
            transported_surface_id=transported_row.surface_id,
            transported_surface_digest=transported_row.surface_digest,
            claim_flags=self._surface_lineage_claim_flags(),
        )

    def _build_surface_supersession_record(
        self,
        *,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
        topology_event: GRCEvent | Mapping[str, Any],
    ) -> LGRC9V3CausalPulseSubstrateSurfaceLineageRecord:
        topology_artifact = self._topology_event_payload(topology_event)
        topology_event_id = str(
            topology_artifact.get("topology_event_id")
            or topology_artifact.get("expansion_id")
            or topology_artifact.get("transport_id")
            or ""
        )
        if not topology_event_id:
            raise InvalidStateTransitionError(
                "surface lineage supersession requires a committed topology event id"
            )
        topology_event_kind = str(
            topology_artifact.get("topology_event_kind")
            or (topology_event.kind if isinstance(topology_event, GRCEvent) else "")
        )
        if not topology_event_kind:
            raise InvalidStateTransitionError(
                "surface lineage supersession requires a topology event kind"
            )
        topology_event_digest = build_lgrc9v3_topology_event_digest(
            topology_artifact
        )
        lineage_transfer_map = self._topology_event_lineage_transfer_map(
            topology_artifact
        )
        budget = self._runtime_budget_surface()
        record_seed = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "source_surface_digest": row.surface_digest,
                "topology_event_digest": topology_event_digest,
                "lineage_action": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED
                ),
            }
        )
        scheduler_event_index = max(
            int(topology_artifact.get("scheduler_event_index", 0)),
            int(row.scheduler_event_index) + 1,
            int(self._state.scheduler_event_index),
        )
        return LGRC9V3CausalPulseSubstrateSurfaceLineageRecord(
            surface_lineage_record_id=f"surface-lineage:{record_seed[:32]}",
            surface_lineage_policy_id=(
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
            ),
            surface_lineage_transport_enabled=True,
            surface_lineage_transport_validated=bool(
                self._state.causal_modes.get(
                    "causal_pulse_substrate_surface_lineage_transport_validated",
                    False,
                )
            ),
            lgrc_runtime_level=str(self._state.lgrc_runtime_level),
            causal_layer_mode=str(self._state.causal_layer_mode),
            source_surface_id=row.surface_id,
            source_surface_digest=row.surface_digest,
            topology_event_id=topology_event_id,
            topology_event_kind=topology_event_kind,
            topology_event_digest=topology_event_digest,
            event_time_key=float(topology_artifact.get("event_time_key", self._state.event_time_key)),
            scheduler_event_index=scheduler_event_index,
            checkpoint_index=int(
                topology_artifact.get("checkpoint_index", self._state.checkpoint_index)
            ),
            lineage_transfer_map=lineage_transfer_map,
            source_surface_nodes=tuple(int(node_id) for node_id in row.surface_nodes),
            target_surface_nodes=(),
            lineage_action=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED,
            lineage_status=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED,
            surface_budget_surface=row.surface_budget_surface,
            surface_budget_before=float(row.surface_budget_after),
            surface_budget_after=float(row.surface_budget_after),
            surface_budget_error=0.0,
            node_plus_packet_budget_before=budget,
            node_plus_packet_budget_after=budget,
            node_plus_packet_budget_error=0.0,
            superseded_surface_id=row.surface_id,
            producer_stale_read_blocker=(
                LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED
            ),
            claim_flags=self._surface_lineage_claim_flags(),
        )

    def _emit_surface_supersession_for_topology_event(
        self,
        topology_event: GRCEvent | Mapping[str, Any],
    ) -> tuple[LGRC9V3CausalPulseSubstrateSurfaceLineageRecord, ...]:
        if not self._surface_lineage_transport_enabled():
            return ()
        topology_artifact = self._topology_event_payload(topology_event)
        topology_event_id = str(
            topology_artifact.get("topology_event_id")
            or topology_artifact.get("expansion_id")
            or topology_artifact.get("transport_id")
            or ""
        )
        if not topology_event_id:
            return ()
        topology_event_digest = build_lgrc9v3_topology_event_digest(
            topology_artifact
        )
        records: list[LGRC9V3CausalPulseSubstrateSurfaceLineageRecord] = []
        keys = self._causal_pulse_substrate_surface_lineage_keys()
        for row in list(self._state.causal_pulse_substrate_surface_log):
            if (
                row.surface_values_after.get("transported_by_topology_event_digest")
                == topology_event_digest
            ):
                continue
            if self._surface_lineage_record_for_row(row) is not None:
                continue
            transported_row: LGRC9V3CausalPulseSubstrateSurfaceRow | None = None
            try:
                lineage_transfer_map = self._topology_event_lineage_transfer_map(
                    topology_artifact
                )
                target_nodes = self._transported_surface_node_ids(
                    row=row,
                    lineage_transfer_map=lineage_transfer_map,
                )
                topology_event_id = str(
                    topology_artifact.get("topology_event_id")
                    or topology_artifact.get("expansion_id")
                    or topology_artifact.get("transport_id")
                    or ""
                )
                scheduler_event_index = max(
                    int(topology_artifact.get("scheduler_event_index", 0)) + 1,
                    int(row.scheduler_event_index) + 1,
                    int(self._state.scheduler_event_index),
                )
                transported_row = self._build_transported_surface_row(
                    row=row,
                    topology_artifact=topology_artifact,
                    topology_event_id=topology_event_id,
                    topology_event_digest=topology_event_digest,
                    lineage_transfer_map=lineage_transfer_map,
                    target_nodes=target_nodes,
                    scheduler_event_index=scheduler_event_index,
                )
                record = self._build_surface_transport_record(
                    row=row,
                    topology_event=topology_event,
                    transported_row=transported_row,
                )
            except InvalidStateTransitionError:
                record = self._build_surface_supersession_record(
                    row=row,
                    topology_event=topology_event,
                )
            if str(record.idempotency_key) in keys:
                continue
            keys.add(str(record.idempotency_key))
            if transported_row is not None:
                self._state.causal_pulse_substrate_surface_log.append(transported_row)
            self._state.causal_pulse_substrate_surface_lineage_log.append(record)
            records.append(record)
        if records:
            self._store_causal_pulse_substrate_surface_lineage_keys(keys)
        return tuple(records)

    def _surface_lineage_record_for_row(
        self,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceLineageRecord | None:
        for record in reversed(self._state.causal_pulse_substrate_surface_lineage_log):
            if record.source_surface_digest == row.surface_digest:
                return record
        return None

    def _surface_transport_record_for_transported_row(
        self,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceLineageRecord | None:
        for record in reversed(self._state.causal_pulse_substrate_surface_lineage_log):
            if record.transported_surface_digest == row.surface_digest:
                return record
        return None

    def _topology_state_reabsorption_record_for_surface_lineage(
        self,
        lineage_record: LGRC9V3CausalPulseSubstrateSurfaceLineageRecord | None,
    ) -> LGRC9V3TopologyStateReabsorptionRecord | None:
        if lineage_record is None:
            return None
        lineage_map = {
            str(source): str(target)
            for source, target in lineage_record.lineage_transfer_map.items()
        }
        for record in reversed(self._state.topology_state_reabsorption_log):
            if record.topology_event_digest != lineage_record.topology_event_digest:
                continue
            if {
                str(source): str(target)
                for source, target in record.lineage_transfer_map.items()
            } != lineage_map:
                continue
            return record
        return None

    def _producer_result_for_missing_topology_state_reabsorption(
        self,
        *,
        producer_policy: str,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
        lineage_record: LGRC9V3CausalPulseSubstrateSurfaceLineageRecord,
    ) -> LGRC9V3AutonomousProductionResult:
        reason_code = (
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED
        )
        record = self._build_autonomous_production_record(
            producer_policy=producer_policy,
            causal_surface_digest=str(row.surface_digest),
            idempotency_key=(
                f"{producer_policy}:{row.surface_digest}:"
                f"{lineage_record.lineage_record_digest}:state-reabsorption-required"
            ),
            reason_code=reason_code,
            observed_evidence={
                "surface_id": row.surface_id,
                "surface_digest": row.surface_digest,
                "surface_lineage_current": True,
                "producer_reads_transport_successor": True,
                "surface_lineage_record_id": lineage_record.surface_lineage_record_id,
                "surface_lineage_record_digest": (
                    lineage_record.lineage_record_digest
                ),
                "topology_event_id": lineage_record.topology_event_id,
                "topology_event_digest": lineage_record.topology_event_digest,
                "topology_state_reabsorption_verified": False,
                "topology_state_reabsorption_record_digest": None,
                "primary_blocker": reason_code,
                "producer_mutation_ownership": "step_processes_packet_departure",
                "producer_mutated_coherence": False,
                "producer_marked_packet_processed": False,
                "producer_emitted_claim_label": False,
                "direct_coherence_write": False,
                "direct_support_mask_write": False,
                "direct_centroid_write": False,
                "direct_displacement_write": False,
                "direct_topology_write": False,
                "direct_claim_write": False,
                "movement_claim_allowed": False,
                "loop_driven_movement_claim_allowed": False,
                "locomotion_like_claim_allowed": False,
                "adaptive_topology_entry_allowed": False,
            },
        )
        return LGRC9V3AutonomousProductionResult(
            producer_policy=producer_policy,
            scheduler_event_index=int(self._state.scheduler_event_index),
            checkpoint_index=int(self._state.checkpoint_index),
            event_time_key=float(self._state.event_time_key),
            causal_surface_digest=str(row.surface_digest),
            production_records=(record,),
        )

    def _surface_supersession_for_row(
        self,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceLineageRecord | None:
        for record in reversed(self._state.causal_pulse_substrate_surface_lineage_log):
            if (
                record.source_surface_digest == row.surface_digest
                and record.lineage_status
                == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED
            ):
                return record
        return None

    def _latest_lineage_eligible_surface_row(
        self,
        surface_kind: str,
    ) -> tuple[
        LGRC9V3CausalPulseSubstrateSurfaceRow | None,
        LGRC9V3CausalPulseSubstrateSurfaceLineageRecord | None,
    ]:
        stale_transport: tuple[
            LGRC9V3CausalPulseSubstrateSurfaceRow,
            LGRC9V3CausalPulseSubstrateSurfaceLineageRecord,
        ] | None = None
        for row in reversed(self._state.causal_pulse_substrate_surface_log):
            if row.surface_kind != surface_kind:
                continue
            lineage = self._surface_lineage_record_for_row(row)
            if lineage is None:
                return row, None
            if (
                lineage.lineage_action
                == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
            ):
                stale_transport = (row, lineage)
                continue
            return row, lineage
        if stale_transport is not None:
            return stale_transport
        return None, None

    def _surface_update_policy_for_packet_contact(self) -> dict[str, Any]:
        return {
            "policy_id": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED
            ),
            "version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
            "activation_gate": "committed_packet_event",
            "allowed_surface_kinds": [
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT
            ],
        }

    def _build_causal_pulse_substrate_surface_row(
        self,
        processing_result: Any,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceRow:
        processed_event = processing_result.processed_event
        if processed_event.source_node_id is None or processed_event.target_node_id is None:
            raise InvalidStateTransitionError("surface row source event missing nodes")
        if processed_event.edge_id is None:
            raise InvalidStateTransitionError("surface row source event missing edge")
        if processed_event.amount is None:
            raise InvalidStateTransitionError("surface row source event missing amount")
        route_aspect_digest = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "route_aspect_id": "unbound_lgrc2_packet_contact",
                "pulse_event_id": processed_event.event_id,
                "pulse_channel_id": f"edge:{int(processed_event.edge_id)}",
                "source_node_id": int(processed_event.source_node_id),
                "target_node_id": int(processed_event.target_node_id),
            }
        )
        surface_state_digest = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "surface_state": "post_committed_packet_event",
                "pulse_event_id": processed_event.event_id,
                "scheduler_event_index": int(processed_event.scheduler_event_index),
                "checkpoint_index": int(self._state.checkpoint_index),
                "node_proper_time": _string_keyed_float_map(
                    self._state.node_proper_time
                ),
            }
        )
        return LGRC9V3CausalPulseSubstrateSurfaceRow(
            surface_id=f"surface:{processed_event.event_id}:route_local_pulse_contact",
            surface_policy_id=str(
                self._state.causal_modes.get(
                    "causal_pulse_substrate_surface_policy",
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
                )
            ),
            surface_policy_enabled=True,
            surface_policy_validated=bool(
                self._state.causal_modes.get(
                    "causal_pulse_substrate_surface_validated",
                    False,
                )
            ),
            lgrc_runtime_level=str(self._state.lgrc_runtime_level),
            route_aspect_id="unbound_lgrc2_packet_contact",
            route_aspect_digest=route_aspect_digest,
            pulse_event_id=str(processed_event.event_id),
            pulse_packet_id=str(processed_event.packet_id),
            pulse_event_kind=str(processed_event.event_kind),
            pulse_channel_id=f"edge:{int(processed_event.edge_id)}",
            pulse_route_step=0
            if processed_event.event_kind == LGRC9V3_PACKET_EVENT_KIND_DEPARTURE
            else 1,
            event_time_key=float(processed_event.event_time_key),
            scheduler_event_index=int(processed_event.scheduler_event_index) + 1,
            node_proper_time=dict(self._state.node_proper_time),
            source_node_id=int(processed_event.source_node_id),
            target_node_id=int(processed_event.target_node_id),
            contact_amount=float(processed_event.amount),
            surface_state_id=(
                f"surface-state:{processed_event.event_id}:"
                f"{int(self._state.checkpoint_index)}"
            ),
            surface_state_digest=surface_state_digest,
            surface_kind=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
            surface_nodes=(
                int(processed_event.source_node_id),
                int(processed_event.target_node_id),
            ),
            surface_values_before={
                "committed_packet_event_observed": False,
                "surface_contact_mass": 0.0,
            },
            surface_values_after={
                "committed_packet_event_observed": True,
                "surface_contact_mass": float(processed_event.amount),
                "source_event_id": str(processed_event.event_id),
            },
            runtime_visible_inputs=(
                "committed_packet_event",
                "route_aspect_digest",
                "pulse_channel_id",
            ),
            surface_update_policy=self._surface_update_policy_for_packet_contact(),
            surface_budget_surface=(
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_DERIVED_SURFACE
            ),
            surface_budget_before=0.0,
            surface_budget_after=0.0,
            surface_budget_error=0.0,
            lineage_status=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
            producer_records=(),
            claim_flags={
                "movement_claim_allowed": False,
                "loop_driven_movement_claim_allowed": False,
                "locomotion_like_claim_allowed": False,
                "adaptive_topology_entry_allowed": False,
                "native_m6": False,
                "biological_claim_allowed": False,
                "agency_claim_allowed": False,
                "identity_acceptance_claim_allowed": False,
            },
        )

    def _emit_causal_pulse_substrate_surface_event(
        self,
        processing_result: Any,
    ) -> GRCEvent | None:
        if not self._causal_pulse_substrate_surface_enabled():
            return None
        row = self._build_causal_pulse_substrate_surface_row(processing_result)
        idempotency_key = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "source_event_id": row.pulse_event_id,
                "surface_policy_id": row.surface_policy_id,
                "surface_kind": row.surface_kind,
                "route_aspect_digest": row.route_aspect_digest,
            }
        )
        keys = self._causal_pulse_substrate_surface_keys()
        if idempotency_key in keys:
            return None
        keys.add(idempotency_key)
        self._store_causal_pulse_substrate_surface_keys(keys)
        self._state.causal_pulse_substrate_surface_log.append(row)
        return GRCEvent(
            kind=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
            step_index=int(row.scheduler_event_index),
            payload=row.to_artifact(),
            source_family=self.MODEL_FAMILY,
        )

    def _autonomous_producer_surface(self) -> dict[str, Any]:
        ledger = self._state.packet_ledger
        assert ledger is not None
        return {
            "scheduler_event_index": int(self._state.scheduler_event_index),
            "checkpoint_index": int(self._state.checkpoint_index),
            "event_time_key": float(self._state.event_time_key),
            "topology_signature": _runtime_topology_signature(self._state),
            "event_queue_records": [
                event.to_record() for event in ledger.event_queue_records
            ],
            "boundary_birth_trial_queue": [
                dict(trial) for trial in self._state.boundary_birth_trial_queue
            ],
            "causal_flux_routes": {
                str(int(node_id)): [dict(route) for route in routes]
                for node_id, routes in sorted(self._state.causal_flux_routes.items())
            },
            "route_aspect_surplus_trigger_config": dict(
                self._state.cached_quantities.get(
                    LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY,
                    {},
                )
            ),
        }

    def _autonomous_idempotency_keys(self) -> set[str]:
        raw_keys = self._state.cached_quantities.get(
            "lgrc9v3_autonomous_producer_idempotency_keys",
            [],
        )
        if not isinstance(raw_keys, Sequence) or isinstance(raw_keys, str):
            raise InvalidStateTransitionError(
                "autonomous producer idempotency cache must be a sequence"
            )
        return {str(key) for key in raw_keys}

    def _store_autonomous_idempotency_keys(self, keys: set[str]) -> None:
        self._state.cached_quantities[
            "lgrc9v3_autonomous_producer_idempotency_keys"
        ] = sorted(keys)

    def _record_autonomous_production_result(
        self,
        result: LGRC9V3AutonomousProductionResult,
    ) -> LGRC9V3AutonomousProductionResult:
        raw_log = self._state.cached_quantities.setdefault(
            LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
            [],
        )
        if not isinstance(raw_log, list):
            raise InvalidStateTransitionError(
                "autonomous production log must be a list"
            )
        raw_log.append(result.to_artifact())
        return result

    def _autonomous_route_idempotency_key(
        self,
        *,
        producer_policy: str,
        source_node_id: int,
        route_index: int,
        route: Mapping[str, Any],
        amount: float,
        amount_source: str,
    ) -> str:
        return build_lgrc9v3_autonomous_surface_digest(
            {
                "producer_policy": producer_policy,
                "scheduler_event_index": int(self._state.scheduler_event_index),
                "checkpoint_index": int(self._state.checkpoint_index),
                "event_time_key": float(self._state.event_time_key),
                "topology_signature": _runtime_topology_signature(self._state),
                "source_node_id": int(source_node_id),
                "route_index": int(route_index),
                "route": dict(route),
                "amount": float(amount),
                "amount_source": amount_source,
            }
        )

    def _autonomous_boundary_birth_idempotency_key(
        self,
        *,
        producer_policy: str,
        parent_node_id: int,
        parent_port_id: int,
        outward_flux_pressure: float,
        birth_probability: float,
    ) -> str:
        return build_lgrc9v3_autonomous_surface_digest(
            {
                "producer_policy": producer_policy,
                "scheduler_event_index": int(self._state.scheduler_event_index),
                "checkpoint_index": int(self._state.checkpoint_index),
                "event_time_key": float(self._state.event_time_key),
                "topology_signature": _runtime_topology_signature(self._state),
                "parent_node_id": int(parent_node_id),
                "parent_port_id": int(parent_port_id),
                "outward_flux_pressure": float(outward_flux_pressure),
                "birth_probability": float(birth_probability),
            }
        )

    def _build_autonomous_production_record(
        self,
        *,
        producer_policy: str,
        causal_surface_digest: str,
        idempotency_key: str,
        reason_code: str,
        trigger_node_id: int | None = None,
        trigger_edge_id: int | None = None,
        thresholds: Mapping[str, Any] | None = None,
        observed_evidence: Mapping[str, Any] | None = None,
        scheduled_event_kind: str | None = None,
        scheduled_event_time_key: float | None = None,
        scheduled_event_id: str | None = None,
    ) -> LGRC9V3AutonomousProductionRecord:
        record_digest = build_lgrc9v3_autonomous_surface_digest(
            {
                "causal_surface_digest": causal_surface_digest,
                "idempotency_key": idempotency_key,
                "reason_code": reason_code,
                "scheduled_event_id": scheduled_event_id,
            }
        )
        return LGRC9V3AutonomousProductionRecord(
            record_id=build_lgrc9v3_autonomous_production_record_id(
                producer_policy=producer_policy,
                causal_surface_digest=record_digest,
                reason_code=reason_code,
                trigger_node_id=trigger_node_id,
                trigger_edge_id=trigger_edge_id,
                scheduled_event_kind=scheduled_event_kind,
                scheduled_event_time_key=scheduled_event_time_key,
            ),
            producer_policy=producer_policy,
            producer_version=LGRC9V3_AUTONOMY_MODE_VERSION,
            reason_code=reason_code,
            causal_surface_digest=causal_surface_digest,
            idempotency_key=idempotency_key,
            thresholds=dict(thresholds or {}),
            observed_evidence=dict(observed_evidence or {}),
            trigger_node_id=trigger_node_id,
            trigger_edge_id=trigger_edge_id,
            scheduled_event_kind=scheduled_event_kind,
            scheduled_event_time_key=scheduled_event_time_key,
            scheduled_event_id=scheduled_event_id,
        )

    def _route_amount_for_autonomous_departure(
        self,
        *,
        source_node_id: int,
        route: Mapping[str, Any],
    ) -> tuple[float | None, str]:
        if "amount" in route:
            return float(route["amount"]), "fixed_amount"
        if "amount_fraction" in route:
            source_coherence = float(
                self._state.base_state.nodes[int(source_node_id)].coherence
            )
            return (
                source_coherence * float(route["amount_fraction"]),
                "source_coherence_fraction",
            )
        return None, "missing_autonomous_amount_policy"

    def _validate_autonomous_packet_route(
        self,
        *,
        source_node_id: int,
        route: Mapping[str, Any],
    ) -> tuple[int, int]:
        source_id = int(source_node_id)
        target_id = int(route["target_node_id"])
        edge_id = int(route["edge_id"])
        state = self._state.base_state
        if source_id not in state.nodes:
            raise InvalidStateTransitionError(
                f"autonomous route source node {source_id} is not live"
            )
        if target_id not in state.nodes:
            raise InvalidStateTransitionError(
                f"autonomous route target node {target_id} is not live"
            )
        if edge_id not in state.port_edges:
            raise InvalidStateTransitionError(
                f"autonomous route edge {edge_id} is not live"
            )
        edge = state.port_edges[edge_id]
        endpoints = {int(edge.node_u), int(edge.node_v)}
        if endpoints != {source_id, target_id}:
            raise InvalidStateTransitionError(
                "autonomous route edge must connect source and target nodes"
            )
        if edge_id not in self._state.edge_causal_delay:
            raise InvalidStateTransitionError(
                f"autonomous route edge {edge_id} has no causal delay"
            )
        return target_id, edge_id

    def _select_route_aspect_trigger_channel(
        self,
        *,
        route_aspect: LGRC9V3RouteAspect,
        source_pole_id: str,
        eligible_channel_id: str | None,
    ) -> Any:
        channels_by_id = {channel.channel_id: channel for channel in route_aspect.channels}
        if eligible_channel_id is not None:
            if eligible_channel_id not in channels_by_id:
                raise ValueError("eligible_channel_id must name a route-aspect channel")
            channel = channels_by_id[eligible_channel_id]
            if channel.source_pole_id != source_pole_id:
                raise ValueError("eligible channel must originate at source_pole_id")
            return channel
        for channel_id in route_aspect.channel_sequence:
            channel = channels_by_id[channel_id]
            if channel.source_pole_id == source_pole_id:
                return channel
        raise ValueError("source_pole_id has no outgoing route-aspect channel")

    def _route_aspect_channel_by_id(
        self,
        *,
        route_aspect: LGRC9V3RouteAspect,
    ) -> dict[str, Any]:
        return {channel.channel_id: channel for channel in route_aspect.channels}

    def _route_aspect_previous_channel_id(
        self,
        *,
        route_aspect: LGRC9V3RouteAspect,
        channel_id: str,
    ) -> str:
        sequence = tuple(route_aspect.channel_sequence)
        if channel_id not in sequence:
            raise InvalidStateTransitionError("channel_id is not in route-aspect order")
        index = sequence.index(channel_id)
        return str(sequence[(index - 1) % len(sequence)])

    def _route_aspect_surplus_trigger_config(self) -> dict[str, Any] | None:
        raw_config = self._state.cached_quantities.get(
            LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY
        )
        if raw_config is None:
            return None
        if not isinstance(raw_config, Mapping):
            raise InvalidStateTransitionError(
                "route-aspect surplus trigger config must be a mapping"
            )
        config = dict(raw_config)
        route_aspect = restore_lgrc9v3_route_aspect_artifact(
            dict(config.get("route_aspect", {}))
        )
        validate_lgrc9v3_route_aspect(route_aspect, state=self._state.base_state)
        if config.get("route_aspect_digest") != route_aspect.route_aspect_digest:
            raise InvalidStateTransitionError("route-aspect surplus digest mismatch")
        source_pole_id = str(config.get("source_pole_id", ""))
        channel = self._select_route_aspect_trigger_channel(
            route_aspect=route_aspect,
            source_pole_id=source_pole_id,
            eligible_channel_id=str(config.get("eligible_channel_id", "")),
        )
        return {
            "route_aspect": route_aspect,
            "source_pole_id": source_pole_id,
            "reference_mass": _nonnegative_finite_float(
                config.get("reference_mass"),
                context="reference_mass",
            ),
            "trigger_threshold": _nonnegative_finite_float(
                config.get("trigger_threshold"),
                context="trigger_threshold",
            ),
            "packet_amount": _nonnegative_finite_float(
                config.get("packet_amount"),
                context="packet_amount",
            ),
            "eligible_channel": channel,
            "arrival_event_time_key": None
            if config.get("arrival_event_time_key") is None
            else _nonnegative_finite_float(
                config.get("arrival_event_time_key"),
                context="arrival_event_time_key",
            ),
        }

    def _route_aspect_pole_mass(
        self,
        *,
        route_aspect: LGRC9V3RouteAspect,
        pole_id: str,
    ) -> float:
        return sum(
            float(self._state.base_state.nodes[int(node_id)].coherence)
            for node_id in route_aspect.pole_regions[pole_id]
        )

    def _autonomous_route_aspect_surplus_idempotency_key(
        self,
        *,
        producer_policy: str,
        route_aspect: LGRC9V3RouteAspect,
        source_pole_id: str,
        channel_id: str,
        observed_mass: float,
        reference_mass: float,
        trigger_threshold: float,
        packet_amount: float,
    ) -> str:
        return build_lgrc9v3_autonomous_surface_digest(
            {
                "producer_policy": producer_policy,
                "scheduler_event_index": int(self._state.scheduler_event_index),
                "checkpoint_index": int(self._state.checkpoint_index),
                "event_time_key": float(self._state.event_time_key),
                "topology_signature": _runtime_topology_signature(self._state),
                "route_aspect_digest": route_aspect.route_aspect_digest,
                "source_pole_id": source_pole_id,
                "channel_id": channel_id,
                "observed_mass": float(observed_mass),
                "reference_mass": float(reference_mass),
                "trigger_threshold": float(trigger_threshold),
                "packet_amount": float(packet_amount),
            }
        )

    def _latest_arrival_processing_result(self) -> object | None:
        for result in reversed(self._state.packet_processing_log):
            if result.processed_event.event_kind == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL:
                return result
        return None

    def _self_rearm_evidence_log(self) -> list[dict[str, Any]]:
        raw_log = self._state.cached_quantities.setdefault(
            LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY,
            [],
        )
        if not isinstance(raw_log, list):
            raise InvalidStateTransitionError("self-rearm evidence log must be a list")
        return raw_log

    def _build_self_rearm_candidate_evidence(
        self,
        *,
        route_aspect: LGRC9V3RouteAspect,
        source_pole_id: str,
        channel_id: str,
        observed_mass: float,
        reference_mass: float,
        surplus: float,
        trigger_threshold: float,
        child_packet_id: str,
        child_departure_event_id: str,
        child_departure_event_time_key: float,
        child_source_node_id: int,
        child_target_node_id: int,
        producer_record_id: str,
    ) -> dict[str, Any] | None:
        latest_arrival = self._latest_arrival_processing_result()
        if latest_arrival is None:
            return None
        parent_arrival = latest_arrival.processed_event
        channel_by_id = self._route_aspect_channel_by_id(route_aspect=route_aspect)
        previous_channel_id = self._route_aspect_previous_channel_id(
            route_aspect=route_aspect,
            channel_id=channel_id,
        )
        previous_channel = channel_by_id[previous_channel_id]
        if parent_arrival.target_node_id is None:
            return None
        parent_source_node_id = parent_arrival.source_node_id
        parent_edge_id = parent_arrival.edge_id
        if parent_source_node_id is None or parent_edge_id is None:
            return None
        if (
            int(previous_channel.route_hops[-1].source_node_id)
            != int(parent_source_node_id)
            or int(previous_channel.route_hops[-1].target_node_id)
            != int(parent_arrival.target_node_id)
            or int(previous_channel.route_hops[-1].edge_id)
            != int(parent_edge_id)
        ):
            return None
        if int(parent_arrival.target_node_id) not in {
            int(node_id) for node_id in route_aspect.pole_regions[source_pole_id]
        }:
            return None
        if float(parent_arrival.event_time_key) > float(self._state.event_time_key):
            return None
        if int(parent_arrival.scheduler_event_index) > int(
            self._state.scheduler_event_index
        ):
            return None
        if surplus < trigger_threshold:
            return None
        route_step_index = tuple(route_aspect.channel_sequence).index(channel_id)
        producer_budget = self._runtime_budget_surface()
        evidence_id = build_lgrc9v3_autonomous_surface_digest(
            {
                "event_kind": LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND,
                "status": "scheduled_child_pending_departure",
                "parent_packet_id": parent_arrival.packet_id,
                "parent_arrival_event_id": parent_arrival.event_id,
                "child_packet_id": child_packet_id,
                "child_departure_event_id": child_departure_event_id,
                "producer_record_id": producer_record_id,
                "route_aspect_digest": route_aspect.route_aspect_digest,
            }
        )
        evidence = {
            "event_schema_version": LGRC9V3_SELF_REARM_EVIDENCE_EVENT_SCHEMA_VERSION,
            "runtime_family": self.MODEL_FAMILY,
            "self_rearm_evidence_id": evidence_id,
            "self_rearm_status": "scheduled_child_pending_departure",
            "route_aspect_id": route_aspect.route_aspect_id,
            "route_aspect_digest": route_aspect.route_aspect_digest,
            "source_pole_id": source_pole_id,
            "target_pole_id": source_pole_id,
            "trigger_channel_id": channel_id,
            "route_channel_sequence": [str(value) for value in route_aspect.channel_sequence],
            "route_step_index": int(route_step_index),
            "parent_arrival_channel_id": previous_channel_id,
            "expected_previous_channel_id": previous_channel_id,
            "expected_next_channel_id": (
                route_aspect.expected_next_channel_by_channel()[channel_id]
            ),
            "parent_packet_id": parent_arrival.packet_id,
            "parent_arrival_event_id": parent_arrival.event_id,
            "parent_arrival_event_time_key": float(parent_arrival.event_time_key),
            "parent_arrival_scheduler_event_index": int(
                parent_arrival.scheduler_event_index
            ),
            "parent_arrival_target_node_id": int(parent_arrival.target_node_id),
            "producer_record_id": producer_record_id,
            "producer_event_time_key": float(self._state.event_time_key),
            "producer_scheduler_event_index": int(self._state.scheduler_event_index),
            "producer_after_parent_arrival_committed": True,
            "observed_mass_after_arrival": float(observed_mass),
            "reference_mass": float(reference_mass),
            "surplus_after_arrival": float(surplus),
            "trigger_threshold": float(trigger_threshold),
            "threshold_crossed": True,
            "child_packet_id": child_packet_id,
            "child_departure_event_id": child_departure_event_id,
            "child_departure_event_time_key": float(child_departure_event_time_key),
            "child_source_node_id": int(child_source_node_id),
            "child_target_node_id": int(child_target_node_id),
            "budget_after_parent_arrival": float(latest_arrival.budget_after),
            "parent_arrival_budget_error": float(latest_arrival.budget_error),
            "budget_before_producer": float(producer_budget),
            "budget_after_producer": float(producer_budget),
            "producer_budget_error": 0.0,
            "budget_after_child_scheduling_before_departure": float(producer_budget),
            "child_scheduling_budget_error": 0.0,
            "event_time_ordering": {
                "arrival_before_or_at_producer": (
                    float(parent_arrival.event_time_key)
                    <= float(self._state.event_time_key)
                ),
                "producer_before_or_at_child_departure": (
                    float(self._state.event_time_key)
                    <= float(child_departure_event_time_key)
                ),
            },
            "node_proper_time_surface": _string_keyed_float_map(
                self._state.node_proper_time
            ),
            "source_node_proper_time_at_trigger": float(
                self._state.node_proper_time.get(int(child_source_node_id), 0.0)
            ),
            "native_self_rearm_evidence": True,
            "native_d2_3_equivalent": False,
            "movement_claim_allowed": False,
            "native_grc9v3_loop_evidence": False,
        }
        self._self_rearm_evidence_log().append(dict(evidence))
        self._state.event_log.append(
            GRCEvent(
                kind=LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND,
                step_index=int(self._state.scheduler_event_index),
                payload=dict(evidence),
                source_family=self.MODEL_FAMILY,
            )
        )
        return evidence

    def _complete_self_rearm_evidence_for_departure(
        self,
        *,
        processed_event: Any,
        processing_result: Any,
    ) -> list[GRCEvent]:
        if processed_event.event_kind != LGRC9V3_PACKET_EVENT_KIND_DEPARTURE:
            return []
        completed_events: list[GRCEvent] = []
        log = self._self_rearm_evidence_log()
        for record in log:
            if record.get("self_rearm_status") != "scheduled_child_pending_departure":
                continue
            if record.get("child_packet_id") != processed_event.packet_id:
                continue
            if record.get("child_departure_event_id") != processed_event.event_id:
                continue
            completion_id = build_lgrc9v3_autonomous_surface_digest(
                {
                    "event_kind": LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND,
                    "status": "child_departure_processed",
                    "candidate_self_rearm_evidence_id": record[
                        "self_rearm_evidence_id"
                    ],
                    "child_packet_id": processed_event.packet_id,
                    "child_departure_event_id": processed_event.event_id,
                }
            )
            completion = {
                **record,
                "self_rearm_evidence_id": completion_id,
                "candidate_self_rearm_evidence_id": record["self_rearm_evidence_id"],
                "self_rearm_status": "child_departure_processed",
                "child_departure_processed": True,
                "child_departure_processed_event_id": processed_event.event_id,
                "child_departure_processed_event_time_key": float(
                    processed_event.event_time_key
                ),
                "child_departure_scheduler_event_index": int(
                    processed_event.scheduler_event_index
                ),
                "budget_before_child_departure": float(processing_result.budget_before),
                "budget_after_child_departure": float(processing_result.budget_after),
                "child_departure_budget_error": float(
                    processing_result.budget_error
                ),
                "child_source_node_proper_time_at_departure": float(
                    self._state.node_proper_time.get(
                        int(processed_event.source_node_id or 0),
                        0.0,
                    )
                ),
                "event_time_ordering": {
                    **dict(record.get("event_time_ordering", {})),
                    "arrival_before_or_at_child_departure": (
                        float(record["parent_arrival_event_time_key"])
                        <= float(processed_event.event_time_key)
                    ),
                },
            }
            record.update(completion)
            completed_events.append(
                GRCEvent(
                    kind=LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND,
                    step_index=int(processed_event.scheduler_event_index),
                    payload=dict(completion),
                    source_family=self.MODEL_FAMILY,
                )
            )
        return completed_events

    def _produce_packet_departures_from_flux_routes(
        self,
        *,
        producer_policy: str,
        causal_surface_digest: str,
    ) -> LGRC9V3AutonomousProductionResult:
        idempotency_keys = self._autonomous_idempotency_keys()
        records: list[LGRC9V3AutonomousProductionRecord] = []
        scheduled_routes: list[
            tuple[int, int, int, Mapping[str, Any], float, str, str]
        ] = []
        source_totals: dict[int, float] = {}

        for source_node_id, routes in sorted(self._state.causal_flux_routes.items()):
            for route_index, route in enumerate(routes):
                target_id, edge_id = self._validate_autonomous_packet_route(
                    source_node_id=source_node_id,
                    route=route,
                )
                amount, amount_source = self._route_amount_for_autonomous_departure(
                    source_node_id=source_node_id,
                    route=route,
                )
                if amount is None or amount <= 0.0:
                    continue
                idempotency_key = self._autonomous_route_idempotency_key(
                    producer_policy=producer_policy,
                    source_node_id=int(source_node_id),
                    route_index=route_index,
                    route=route,
                    amount=amount,
                    amount_source=amount_source,
                )
                if idempotency_key in idempotency_keys:
                    records.append(
                        self._build_autonomous_production_record(
                            producer_policy=producer_policy,
                            causal_surface_digest=causal_surface_digest,
                            idempotency_key=idempotency_key,
                            reason_code=(
                                LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP
                            ),
                            trigger_node_id=int(source_node_id),
                            trigger_edge_id=edge_id,
                            thresholds=dict(route),
                            observed_evidence={
                                "target_node_id": target_id,
                                "amount": float(amount),
                                "amount_source": amount_source,
                            },
                        )
                    )
                    continue
                scheduled_routes.append(
                    (
                        int(source_node_id),
                        target_id,
                        edge_id,
                        route,
                        float(amount),
                        amount_source,
                        idempotency_key,
                    )
                )
                source_totals[int(source_node_id)] = (
                    source_totals.get(int(source_node_id), 0.0) + float(amount)
                )

        for source_node_id, outbound_total in source_totals.items():
            available = float(self._state.base_state.nodes[source_node_id].coherence)
            if outbound_total > available + 1e-12:
                raise InvalidStateTransitionError(
                    "autonomous packet routes exceed available source coherence"
                )

        for route_index, (
            source_node_id,
            target_node_id,
            edge_id,
            route,
            amount,
            amount_source,
            idempotency_key,
        ) in enumerate(scheduled_routes):
            ledger_before = self._state.packet_ledger
            assert ledger_before is not None
            before_event_ids = {event.event_id for event in ledger_before.event_queue_records}
            self.schedule_packet_departure(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                edge_id=edge_id,
                amount=amount,
                departure_event_time_key=float(self._state.event_time_key),
                arrival_event_time_key=route.get("arrival_event_time_key"),
                scheduler_event_index=(
                    int(self._state.scheduler_event_index)
                    + len(ledger_before.event_queue_records)
                    + route_index
                    + 1
                ),
                packet_index=len(ledger_before.packet_records) + route_index,
            )
            ledger_after = self._state.packet_ledger
            assert ledger_after is not None
            new_events = [
                event
                for event in ledger_after.event_queue_records
                if event.event_id not in before_event_ids
            ]
            if len(new_events) != 1:
                raise InvalidStateTransitionError(
                    "autonomous packet producer expected exactly one queued event"
                )
            queued_event = new_events[0]
            idempotency_keys.add(idempotency_key)
            records.append(
                self._build_autonomous_production_record(
                    producer_policy=producer_policy,
                    causal_surface_digest=causal_surface_digest,
                    idempotency_key=idempotency_key,
                    reason_code=(
                        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PACKET_DEPARTURE_SCHEDULED
                    ),
                    trigger_node_id=source_node_id,
                    trigger_edge_id=edge_id,
                    thresholds=dict(route),
                    observed_evidence={
                        "target_node_id": target_node_id,
                        "amount": float(amount),
                        "amount_source": amount_source,
                        "edge_causal_delay": float(
                            self._state.edge_causal_delay[edge_id]
                        ),
                    },
                    scheduled_event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                    scheduled_event_time_key=float(queued_event.event_time_key),
                    scheduled_event_id=queued_event.event_id,
                )
            )

        if scheduled_routes:
            self._store_autonomous_idempotency_keys(idempotency_keys)
        if not records:
            records.append(
                self._build_autonomous_production_record(
                    producer_policy=producer_policy,
                    causal_surface_digest=causal_surface_digest,
                    idempotency_key=f"{producer_policy}:{causal_surface_digest}",
                    reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
                    observed_evidence={
                        "route_count": sum(
                            len(routes)
                            for routes in self._state.causal_flux_routes.values()
                        )
                    },
                )
            )

        return LGRC9V3AutonomousProductionResult(
            producer_policy=producer_policy,
            scheduler_event_index=int(self._state.scheduler_event_index),
            checkpoint_index=int(self._state.checkpoint_index),
            event_time_key=float(self._state.event_time_key),
            causal_surface_digest=causal_surface_digest,
            production_records=tuple(records),
            state_mutated=bool(scheduled_routes),
        )

    def _produce_packet_departure_from_route_surplus(
        self,
        *,
        producer_policy: str,
        causal_surface_digest: str,
    ) -> LGRC9V3AutonomousProductionResult:
        config = self._route_aspect_surplus_trigger_config()
        if config is None:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=causal_surface_digest,
                idempotency_key=f"{producer_policy}:{causal_surface_digest}",
                reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
                observed_evidence={"route_aspect_surplus_trigger_configured": False},
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=causal_surface_digest,
                production_records=(record,),
            )

        route_aspect = config["route_aspect"]
        channel = config["eligible_channel"]
        source_pole_id = str(config["source_pole_id"])
        reference_mass = float(config["reference_mass"])
        trigger_threshold = float(config["trigger_threshold"])
        packet_amount = float(config["packet_amount"])
        observed_mass = self._route_aspect_pole_mass(
            route_aspect=route_aspect,
            pole_id=source_pole_id,
        )
        surplus = observed_mass - reference_mass
        first_hop = channel.route_hops[0]
        source_node_id = int(first_hop.source_node_id)
        target_node_id = int(first_hop.target_node_id)
        edge_id = int(first_hop.edge_id)
        observed_evidence = {
            "route_aspect_id": route_aspect.route_aspect_id,
            "route_aspect_digest": route_aspect.route_aspect_digest,
            "pole_region_digest": route_aspect.pole_region_digest,
            "channel_sequence_digest": route_aspect.channel_sequence_digest,
            "source_pole_id": source_pole_id,
            "target_pole_id": channel.target_pole_id,
            "eligible_channel_id": channel.channel_id,
            "expected_next_channel_id": (
                route_aspect.expected_next_channel_by_channel()[channel.channel_id]
            ),
            "observed_mass": observed_mass,
            "reference_mass": reference_mass,
            "surplus": surplus,
            "packet_amount": packet_amount,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "edge_id": edge_id,
            "producer_event_time_key": float(self._state.event_time_key),
            "source_node_proper_time_at_evaluation": float(
                self._state.node_proper_time.get(source_node_id, 0.0)
            ),
            "source_node_last_update_event_time_key_at_evaluation": float(
                self._state.node_last_update_event_time_key.get(source_node_id, 0.0)
            ),
            "producer_mutation_ownership": "step_processes_packet_departure",
        }
        thresholds = {
            "trigger_threshold": trigger_threshold,
            "reference_mass": reference_mass,
            "packet_amount": packet_amount,
        }
        if surplus < trigger_threshold:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=causal_surface_digest,
                idempotency_key=f"{producer_policy}:{causal_surface_digest}",
                reason_code=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD
                ),
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence=observed_evidence,
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=causal_surface_digest,
                production_records=(record,),
            )

        available = float(self._state.base_state.nodes[source_node_id].coherence)
        if packet_amount > available + 1e-12:
            raise InvalidStateTransitionError(
                "route-aspect surplus trigger exceeds source-node coherence"
            )
        idempotency_key = self._autonomous_route_aspect_surplus_idempotency_key(
            producer_policy=producer_policy,
            route_aspect=route_aspect,
            source_pole_id=source_pole_id,
            channel_id=channel.channel_id,
            observed_mass=observed_mass,
            reference_mass=reference_mass,
            trigger_threshold=trigger_threshold,
            packet_amount=packet_amount,
        )
        idempotency_keys = self._autonomous_idempotency_keys()
        if idempotency_key in idempotency_keys:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=causal_surface_digest,
                idempotency_key=idempotency_key,
                reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence=observed_evidence,
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=causal_surface_digest,
                production_records=(record,),
            )

        ledger_before = self._state.packet_ledger
        assert ledger_before is not None
        before_event_ids = {event.event_id for event in ledger_before.event_queue_records}
        departure_event_time_key = max(
            [float(self._state.event_time_key)]
            + [
                float(event.event_time_key)
                for event in ledger_before.event_queue_records
            ]
        )
        self.schedule_packet_departure(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_id=edge_id,
            amount=packet_amount,
            departure_event_time_key=departure_event_time_key,
            arrival_event_time_key=config["arrival_event_time_key"],
            scheduler_event_index=(
                int(self._state.scheduler_event_index)
                + len(ledger_before.event_queue_records)
                + 1
            ),
            packet_index=len(ledger_before.packet_records),
        )
        ledger_after = self._state.packet_ledger
        assert ledger_after is not None
        new_events = [
            event
            for event in ledger_after.event_queue_records
            if event.event_id not in before_event_ids
        ]
        if len(new_events) != 1:
            raise InvalidStateTransitionError(
                "route-aspect surplus producer expected exactly one queued event"
            )
        queued_event = new_events[0]
        idempotency_keys.add(idempotency_key)
        self._store_autonomous_idempotency_keys(idempotency_keys)
        record = self._build_autonomous_production_record(
            producer_policy=producer_policy,
            causal_surface_digest=causal_surface_digest,
            idempotency_key=idempotency_key,
            reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED,
            trigger_node_id=source_node_id,
            trigger_edge_id=edge_id,
            thresholds=thresholds,
            observed_evidence={
                **observed_evidence,
                "scheduled_packet_id": queued_event.packet_id,
                "scheduled_departure_event_time_key": float(
                    queued_event.event_time_key
                ),
            },
            scheduled_event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            scheduled_event_time_key=float(queued_event.event_time_key),
            scheduled_event_id=queued_event.event_id,
        )
        self_rearm_evidence = self._build_self_rearm_candidate_evidence(
            route_aspect=route_aspect,
            source_pole_id=source_pole_id,
            channel_id=channel.channel_id,
            observed_mass=observed_mass,
            reference_mass=reference_mass,
            surplus=surplus,
            trigger_threshold=trigger_threshold,
            child_packet_id=queued_event.packet_id,
            child_departure_event_id=queued_event.event_id,
            child_departure_event_time_key=float(queued_event.event_time_key),
            child_source_node_id=source_node_id,
            child_target_node_id=target_node_id,
            producer_record_id=record.record_id,
        )
        if self_rearm_evidence is not None:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=causal_surface_digest,
                idempotency_key=idempotency_key,
                reason_code=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED
                ),
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence={
                    **dict(record.observed_evidence),
                    "native_self_rearm_evidence": True,
                    "self_rearm_evidence": dict(self_rearm_evidence),
                    "self_rearm_evidence_id": self_rearm_evidence[
                        "self_rearm_evidence_id"
                    ],
                    "self_rearm_status": self_rearm_evidence["self_rearm_status"],
                },
                scheduled_event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                scheduled_event_time_key=float(queued_event.event_time_key),
                scheduled_event_id=queued_event.event_id,
            )
        return LGRC9V3AutonomousProductionResult(
            producer_policy=producer_policy,
            scheduler_event_index=int(self._state.scheduler_event_index),
            checkpoint_index=int(self._state.checkpoint_index),
            event_time_key=float(self._state.event_time_key),
            causal_surface_digest=causal_surface_digest,
            production_records=(record,),
            state_mutated=True,
        )

    def _pulse_substrate_coupling_config(self) -> dict[str, Any] | None:
        raw_config = self._state.cached_quantities.get(
            LGRC9V3_PULSE_SUBSTRATE_COUPLING_CONFIG_KEY
        )
        if raw_config is None:
            return None
        if not isinstance(raw_config, Mapping):
            raise InvalidStateTransitionError(
                "pulse-substrate coupling config must be a mapping"
            )
        config = dict(raw_config)
        if not bool(config.get("enabled", False)):
            return None
        source_selector = str(config.get("source_node_selector", "surface_target"))
        if source_selector not in {"surface_target", "surface_source"}:
            raise InvalidStateTransitionError(
                "pulse-substrate coupling source_node_selector is invalid"
            )
        threshold = _nonnegative_finite_float(
            config.get("threshold"),
            context="pulse_substrate_coupling.threshold",
        )
        reference_value = _nonnegative_finite_float(
            config.get("reference_value", 0.0),
            context="pulse_substrate_coupling.reference_value",
        )
        packet_amount = _nonnegative_finite_float(
            config.get("packet_amount"),
            context="pulse_substrate_coupling.packet_amount",
        )
        if packet_amount <= 0.0:
            raise InvalidStateTransitionError(
                "pulse-substrate coupling packet_amount must be > 0"
            )
        target_node_id = int(config.get("target_node_id", -1))
        edge_id = int(config.get("edge_id", -1))
        if target_node_id < 0 or edge_id < 0:
            raise InvalidStateTransitionError(
                "pulse-substrate coupling requires target_node_id and edge_id"
            )
        return {
            "source_node_selector": source_selector,
            "target_node_id": target_node_id,
            "edge_id": edge_id,
            "threshold": threshold,
            "reference_value": reference_value,
            "packet_amount": packet_amount,
            "arrival_event_time_key": None
            if config.get("arrival_event_time_key") is None
            else _nonnegative_finite_float(
                config.get("arrival_event_time_key"),
                context="pulse_substrate_coupling.arrival_event_time_key",
            ),
        }

    def _latest_route_local_pulse_contact_surface_row(
        self,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceRow | None:
        row, _ = self._latest_lineage_eligible_surface_row(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT
        )
        return row

    def _latest_feedback_eligibility_surface_row(
        self,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceRow | None:
        row, _ = self._latest_lineage_eligible_surface_row(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY
        )
        return row

    def _producer_result_for_stale_surface_row(
        self,
        *,
        producer_policy: str,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
        lineage_record: LGRC9V3CausalPulseSubstrateSurfaceLineageRecord,
    ) -> LGRC9V3AutonomousProductionResult:
        superseded = (
            lineage_record.lineage_status
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED
        )
        reason_code = (
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED
            if superseded
            else LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED
        )
        record = self._build_autonomous_production_record(
            producer_policy=producer_policy,
            causal_surface_digest=str(row.surface_digest),
            idempotency_key=(
                f"{producer_policy}:{row.surface_digest}:"
                f"{lineage_record.lineage_record_digest}:stale"
            ),
            reason_code=reason_code,
            observed_evidence={
                "surface_id": row.surface_id,
                "surface_digest": row.surface_digest,
                "surface_superseded": True,
                "surface_lineage_current": False,
                "lineage_action": lineage_record.lineage_action,
                "lineage_status": lineage_record.lineage_status,
                "primary_blocker": (
                    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED
                ),
                "producer_stale_read_blocker": (
                    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED
                ),
                "surface_lineage_record_id": (
                    lineage_record.surface_lineage_record_id
                ),
                "surface_lineage_record_digest": (
                    lineage_record.lineage_record_digest
                ),
                "topology_event_id": lineage_record.topology_event_id,
                "topology_event_digest": lineage_record.topology_event_digest,
                "producer_mutation_ownership": "step_processes_packet_departure",
                "producer_mutated_coherence": False,
                "producer_marked_packet_processed": False,
                "producer_emitted_claim_label": False,
                "direct_coherence_write": False,
                "direct_support_mask_write": False,
                "direct_centroid_write": False,
                "direct_displacement_write": False,
                "direct_topology_write": False,
                "direct_claim_write": False,
                "movement_claim_allowed": False,
                "loop_driven_movement_claim_allowed": False,
                "locomotion_like_claim_allowed": False,
                "adaptive_topology_entry_allowed": False,
                "native_m6": False,
            },
        )
        return LGRC9V3AutonomousProductionResult(
            producer_policy=producer_policy,
            scheduler_event_index=max(
                int(self._state.scheduler_event_index),
                int(row.scheduler_event_index),
                int(lineage_record.scheduler_event_index),
            ),
            checkpoint_index=int(self._state.checkpoint_index),
            event_time_key=float(self._state.event_time_key),
            causal_surface_digest=str(row.surface_digest),
            production_records=(record,),
        )

    def emit_feedback_eligibility_surface_row(
        self,
        *,
        front_node_ids: Sequence[int],
        rear_node_ids: Sequence[int],
        reference_delta: float = 0.0,
        feedback_threshold: float = 0.0,
        expected_next_route_id: str | None = None,
        expected_next_channel_id: str | None = None,
    ) -> LGRC9V3CausalPulseSubstrateSurfaceRow:
        """Record replayable feedback eligibility evidence from live node state.

        The row is derived from the latest committed packet-contact surface row.
        It records boundary-polarity evidence only; it does not mutate
        coherence, enqueue work, or promote claims.
        """

        source_row = self._latest_route_local_pulse_contact_surface_row()
        if source_row is None:
            raise InvalidStateTransitionError(
                "feedback eligibility surface requires a committed pulse-contact row"
            )
        front_nodes = tuple(int(node_id) for node_id in front_node_ids)
        rear_nodes = tuple(int(node_id) for node_id in rear_node_ids)
        if not front_nodes or not rear_nodes:
            raise ValueError("front_node_ids and rear_node_ids must not be empty")
        live_nodes = set(self._state.base_state.topology.iter_live_node_ids())
        if any(node_id not in live_nodes for node_id in (*front_nodes, *rear_nodes)):
            raise ValueError("feedback eligibility masks must reference live nodes")
        reference = float(reference_delta)
        threshold = _nonnegative_finite_float(
            feedback_threshold,
            context="feedback_threshold",
        )
        front_mass = sum(
            float(self._state.base_state.nodes[node_id].coherence)
            for node_id in front_nodes
        )
        rear_mass = sum(
            float(self._state.base_state.nodes[node_id].coherence)
            for node_id in rear_nodes
        )
        polarity_score = (front_mass - rear_mass) - reference
        surface_policy_id = str(
            self._state.causal_modes.get(
                "causal_pulse_substrate_surface_policy",
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
            )
        )
        surface_state_digest = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "surface_state": "feedback_eligibility",
                "source_surface_digest": source_row.surface_digest,
                "front_node_ids": front_nodes,
                "rear_node_ids": rear_nodes,
                "front_mass": front_mass,
                "rear_mass": rear_mass,
                "reference_delta": reference,
                "feedback_threshold": threshold,
                "checkpoint_index": int(self._state.checkpoint_index),
            }
        )
        row = LGRC9V3CausalPulseSubstrateSurfaceRow(
            surface_id=f"surface:{source_row.pulse_event_id}:feedback_eligibility",
            surface_policy_id=surface_policy_id,
            surface_policy_enabled=True,
            surface_policy_validated=bool(
                self._state.causal_modes.get(
                    "causal_pulse_substrate_surface_validated",
                    False,
                )
            ),
            lgrc_runtime_level=str(self._state.lgrc_runtime_level),
            route_aspect_id=source_row.route_aspect_id,
            route_aspect_digest=source_row.route_aspect_digest,
            pulse_event_id=source_row.pulse_event_id,
            pulse_packet_id=source_row.pulse_packet_id,
            pulse_event_kind=source_row.pulse_event_kind,
            pulse_channel_id=source_row.pulse_channel_id,
            pulse_route_step=int(source_row.pulse_route_step),
            event_time_key=float(self._state.event_time_key),
            scheduler_event_index=max(
                int(self._state.scheduler_event_index) + 1,
                int(source_row.scheduler_event_index) + 1,
            ),
            node_proper_time=dict(self._state.node_proper_time),
            source_node_id=int(source_row.source_node_id),
            target_node_id=int(source_row.target_node_id),
            contact_amount=max(abs(polarity_score), 1e-12),
            surface_state_id=(
                f"surface-state:{source_row.pulse_event_id}:"
                f"feedback:{int(self._state.checkpoint_index)}"
            ),
            surface_state_digest=surface_state_digest,
            surface_kind=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY,
            surface_nodes=tuple(sorted(set((*front_nodes, *rear_nodes)))),
            surface_values_before={
                "feedback_surface_observed": False,
                "source_surface_digest": source_row.surface_digest,
            },
            surface_values_after={
                "feedback_surface_observed": True,
                "source_surface_id": source_row.surface_id,
                "source_surface_digest": source_row.surface_digest,
                "front_node_ids": list(front_nodes),
                "rear_node_ids": list(rear_nodes),
                "front_mass": front_mass,
                "rear_mass": rear_mass,
                "reference_delta": reference,
                "boundary_polarity_score": polarity_score,
                "feedback_threshold": threshold,
                "expected_next_route_id": expected_next_route_id,
                "expected_next_channel_id": expected_next_channel_id,
            },
            runtime_visible_inputs=(
                "committed_surface_rows",
                "eligibility_thresholds",
                "producer_policy",
            ),
            surface_update_policy={
                "policy_id": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED
                ),
                "version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
                "activation_gate": "committed_packet_event",
                "allowed_surface_kinds": [
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY
                ],
                "declared_front_node_ids": list(front_nodes),
                "declared_rear_node_ids": list(rear_nodes),
            },
            surface_budget_surface=(
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_DERIVED_SURFACE
            ),
            surface_budget_before=0.0,
            surface_budget_after=0.0,
            surface_budget_error=0.0,
            lineage_status=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
            producer_records=(),
            claim_flags={
                "movement_claim_allowed": False,
                "loop_driven_movement_claim_allowed": False,
                "locomotion_like_claim_allowed": False,
                "adaptive_topology_entry_allowed": False,
                "native_m6": False,
                "biological_claim_allowed": False,
                "agency_claim_allowed": False,
                "identity_acceptance_claim_allowed": False,
            },
        )
        idempotency_key = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            {
                "source_surface_digest": source_row.surface_digest,
                "surface_policy_id": row.surface_policy_id,
                "surface_kind": row.surface_kind,
                "surface_state_digest": row.surface_state_digest,
            }
        )
        keys = self._causal_pulse_substrate_surface_keys()
        if idempotency_key not in keys:
            keys.add(idempotency_key)
            self._store_causal_pulse_substrate_surface_keys(keys)
            self._state.causal_pulse_substrate_surface_log.append(row)
            self._state.event_log.append(
                GRCEvent(
                    kind=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
                    step_index=int(row.scheduler_event_index),
                    payload=row.to_artifact(),
                    source_family=self.MODEL_FAMILY,
                )
            )
        return row

    def _pulse_substrate_coupling_idempotency_key(
        self,
        *,
        producer_policy: str,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
        source_node_id: int,
        target_node_id: int,
        edge_id: int,
        observed_value: float,
        reference_value: float,
        threshold: float,
        packet_amount: float,
    ) -> str:
        return build_lgrc9v3_autonomous_surface_digest(
            {
                "producer_policy": producer_policy,
                "surface_id": row.surface_id,
                "surface_digest": row.surface_digest,
                "source_pulse_event_id": row.pulse_event_id,
                "source_node_id": int(source_node_id),
                "target_node_id": int(target_node_id),
                "edge_id": int(edge_id),
                "observed_value": float(observed_value),
                "reference_value": float(reference_value),
                "threshold": float(threshold),
                "packet_amount": float(packet_amount),
            }
        )

    def _produce_packet_departure_from_pulse_substrate_coupling(
        self,
        *,
        producer_policy: str,
        causal_surface_digest: str,
    ) -> LGRC9V3AutonomousProductionResult:
        config = self._pulse_substrate_coupling_config()
        row, stale_lineage = self._latest_lineage_eligible_surface_row(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT
        )
        if config is None or row is None:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=causal_surface_digest
                if row is None
                else str(row.surface_digest),
                idempotency_key=f"{producer_policy}:{causal_surface_digest}",
                reason_code=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED
                ),
                observed_evidence={
                    "coupling_configured": config is not None,
                    "committed_surface_row_available": row is not None,
                    "producer_mutation_ownership": "step_processes_packet_departure",
                    "producer_mutated_coherence": False,
                    "producer_marked_packet_processed": False,
                    "producer_emitted_claim_label": False,
                    "direct_claim_write": False,
                    "movement_claim_allowed": False,
                },
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=causal_surface_digest
                if row is None
                else str(row.surface_digest),
                production_records=(record,),
            )

        if stale_lineage is not None:
            return self._producer_result_for_stale_surface_row(
                producer_policy=producer_policy,
                row=row,
                lineage_record=stale_lineage,
            )

        transported_lineage = self._surface_transport_record_for_transported_row(row)
        topology_state_reabsorption = (
            self._topology_state_reabsorption_record_for_surface_lineage(
                transported_lineage
            )
        )
        source_node_id = (
            int(row.target_node_id)
            if config["source_node_selector"] == "surface_target"
            else int(row.source_node_id)
        )
        producer_scheduler_event_index = max(
            int(self._state.scheduler_event_index),
            int(row.scheduler_event_index),
        ) + 1
        target_node_id, edge_id = self._validate_autonomous_packet_route(
            source_node_id=source_node_id,
            route={
                "target_node_id": int(config["target_node_id"]),
                "edge_id": int(config["edge_id"]),
            },
        )
        observed_value = float(row.contact_amount)
        reference_value = float(config["reference_value"])
        threshold = float(config["threshold"])
        response_value = observed_value - reference_value
        packet_amount = float(config["packet_amount"])
        thresholds = {
            "reference_value": reference_value,
            "threshold": threshold,
            "packet_amount": packet_amount,
        }
        observed_evidence = {
            "surface_id": row.surface_id,
            "surface_digest": row.surface_digest,
            "source_pulse_event_id": row.pulse_event_id,
            "source_pulse_packet_id": row.pulse_packet_id,
            "source_pulse_event_kind": row.pulse_event_kind,
            "observed_value": observed_value,
            "reference_value": reference_value,
            "response_value": response_value,
            "threshold": threshold,
            "reference_value_source": "serialized_producer_policy",
            "threshold_source": "serialized_producer_policy",
            "packet_amount_source": "serialized_producer_policy",
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "edge_id": edge_id,
            "producer_reads_committed_surface_row": True,
            "surface_lineage_current": True,
            "producer_reads_transport_successor": transported_lineage is not None,
            "surface_lineage_record_id": None
            if transported_lineage is None
            else transported_lineage.surface_lineage_record_id,
            "surface_lineage_record_digest": None
            if transported_lineage is None
            else transported_lineage.lineage_record_digest,
            "topology_event_id": None
            if transported_lineage is None
            else transported_lineage.topology_event_id,
            "topology_event_digest": None
            if transported_lineage is None
            else transported_lineage.topology_event_digest,
            "topology_state_reabsorption_verified": (
                topology_state_reabsorption is not None
            ),
            "topology_state_reabsorption_record_digest": None
            if topology_state_reabsorption is None
            else topology_state_reabsorption.topology_state_reabsorption_digest,
            "producer_mutation_ownership": "step_processes_packet_departure",
            "producer_mutated_coherence": False,
            "producer_marked_packet_processed": False,
            "producer_emitted_claim_label": False,
            "direct_coherence_write": False,
            "direct_support_mask_write": False,
            "direct_centroid_write": False,
            "direct_displacement_write": False,
            "direct_topology_write": False,
            "direct_claim_write": False,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
        }
        if response_value < threshold:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=str(row.surface_digest),
                idempotency_key=f"{producer_policy}:{row.surface_digest}:subthreshold",
                reason_code=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD
                ),
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence=observed_evidence,
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=producer_scheduler_event_index,
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=str(row.surface_digest),
                production_records=(record,),
            )

        available = float(self._state.base_state.nodes[source_node_id].coherence)
        if packet_amount > available + 1e-12:
            raise InvalidStateTransitionError(
                "pulse-substrate coupling exceeds source-node coherence"
            )
        if transported_lineage is not None and topology_state_reabsorption is None:
            return self._producer_result_for_missing_topology_state_reabsorption(
                producer_policy=producer_policy,
                row=row,
                lineage_record=transported_lineage,
            )
        idempotency_key = self._pulse_substrate_coupling_idempotency_key(
            producer_policy=producer_policy,
            row=row,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_id=edge_id,
            observed_value=observed_value,
            reference_value=reference_value,
            threshold=threshold,
            packet_amount=packet_amount,
        )
        idempotency_keys = self._autonomous_idempotency_keys()
        if idempotency_key in idempotency_keys:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=str(row.surface_digest),
                idempotency_key=idempotency_key,
                reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence=observed_evidence,
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=producer_scheduler_event_index,
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=str(row.surface_digest),
                production_records=(record,),
            )

        ledger_before = self._state.packet_ledger
        assert ledger_before is not None
        before_event_ids = {event.event_id for event in ledger_before.event_queue_records}
        departure_event_time_key = max(
            [float(self._state.event_time_key)]
            + [
                float(event.event_time_key)
                for event in ledger_before.event_queue_records
            ]
        )
        self.schedule_packet_departure(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_id=edge_id,
            amount=packet_amount,
            departure_event_time_key=departure_event_time_key,
            arrival_event_time_key=config["arrival_event_time_key"],
            scheduler_event_index=(
                producer_scheduler_event_index
                + len(ledger_before.event_queue_records)
                + 1
            ),
            packet_index=len(ledger_before.packet_records),
        )
        ledger_after = self._state.packet_ledger
        assert ledger_after is not None
        new_events = [
            event
            for event in ledger_after.event_queue_records
            if event.event_id not in before_event_ids
        ]
        if len(new_events) != 1:
            raise InvalidStateTransitionError(
                "pulse-substrate coupling expected exactly one queued event"
            )
        queued_event = new_events[0]
        idempotency_keys.add(idempotency_key)
        self._store_autonomous_idempotency_keys(idempotency_keys)
        record = self._build_autonomous_production_record(
            producer_policy=producer_policy,
            causal_surface_digest=str(row.surface_digest),
            idempotency_key=idempotency_key,
            reason_code=(
                LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
            ),
            trigger_node_id=source_node_id,
            trigger_edge_id=edge_id,
            thresholds=thresholds,
            observed_evidence={
                **observed_evidence,
                "scheduled_packet_id": queued_event.packet_id,
                "scheduled_departure_event_time_key": float(
                    queued_event.event_time_key
                ),
            },
            scheduled_event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            scheduled_event_time_key=float(queued_event.event_time_key),
            scheduled_event_id=queued_event.event_id,
        )
        return LGRC9V3AutonomousProductionResult(
            producer_policy=producer_policy,
            scheduler_event_index=producer_scheduler_event_index,
            checkpoint_index=int(self._state.checkpoint_index),
            event_time_key=float(self._state.event_time_key),
            causal_surface_digest=str(row.surface_digest),
            production_records=(record,),
            state_mutated=True,
        )

    def _feedback_coupled_pulse_config(self) -> dict[str, Any] | None:
        raw_config = self._state.cached_quantities.get(
            LGRC9V3_FEEDBACK_COUPLED_PULSE_CONFIG_KEY
        )
        if raw_config is None:
            return None
        if not isinstance(raw_config, Mapping):
            raise InvalidStateTransitionError(
                "feedback-coupled pulse config must be a mapping"
            )
        config = dict(raw_config)
        if not bool(config.get("enabled", False)):
            return None
        expected_polarity = str(config.get("expected_polarity", "positive"))
        if expected_polarity not in {"positive", "negative"}:
            raise InvalidStateTransitionError(
                "feedback expected_polarity must be positive or negative"
            )
        source_node_id = int(config.get("source_node_id", -1))
        target_node_id = int(config.get("target_node_id", -1))
        edge_id = int(config.get("edge_id", -1))
        if source_node_id < 0 or target_node_id < 0 or edge_id < 0:
            raise InvalidStateTransitionError(
                "feedback producer requires source_node_id, target_node_id, and edge_id"
            )
        threshold = _nonnegative_finite_float(
            config.get("threshold"),
            context="feedback_coupled_pulse.threshold",
        )
        packet_amount = _nonnegative_finite_float(
            config.get("packet_amount"),
            context="feedback_coupled_pulse.packet_amount",
        )
        if packet_amount <= 0.0:
            raise InvalidStateTransitionError(
                "feedback producer packet_amount must be > 0"
            )
        return {
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "edge_id": edge_id,
            "threshold": threshold,
            "packet_amount": packet_amount,
            "expected_polarity": expected_polarity,
            "expected_source_surface_digest": config.get(
                "expected_source_surface_digest"
            ),
            "expected_next_route_id": config.get("expected_next_route_id"),
            "expected_next_channel_id": config.get("expected_next_channel_id"),
            "arrival_event_time_key": None
            if config.get("arrival_event_time_key") is None
            else _nonnegative_finite_float(
                config.get("arrival_event_time_key"),
                context="feedback_coupled_pulse.arrival_event_time_key",
            ),
        }

    def _feedback_idempotency_key(
        self,
        *,
        producer_policy: str,
        row: LGRC9V3CausalPulseSubstrateSurfaceRow,
        source_node_id: int,
        target_node_id: int,
        edge_id: int,
        expected_polarity: str,
        threshold: float,
        packet_amount: float,
    ) -> str:
        return build_lgrc9v3_autonomous_surface_digest(
            {
                "producer_policy": producer_policy,
                "surface_id": row.surface_id,
                "surface_digest": row.surface_digest,
                "source_surface_digest": row.surface_values_after.get(
                    "source_surface_digest"
                ),
                "source_node_id": int(source_node_id),
                "target_node_id": int(target_node_id),
                "edge_id": int(edge_id),
                "expected_polarity": expected_polarity,
                "threshold": float(threshold),
                "packet_amount": float(packet_amount),
            }
        )

    def _produce_packet_departure_from_feedback_eligibility(
        self,
        *,
        producer_policy: str,
        causal_surface_digest: str,
    ) -> LGRC9V3AutonomousProductionResult:
        config = self._feedback_coupled_pulse_config()
        row, stale_lineage = self._latest_lineage_eligible_surface_row(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY
        )
        if config is None or row is None:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=causal_surface_digest
                if row is None
                else str(row.surface_digest),
                idempotency_key=f"{producer_policy}:{causal_surface_digest}",
                reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED,
                observed_evidence={
                    "feedback_configured": config is not None,
                    "committed_feedback_surface_row_available": row is not None,
                    "producer_mutation_ownership": "step_processes_packet_departure",
                    "producer_mutated_coherence": False,
                    "producer_marked_packet_processed": False,
                    "producer_emitted_claim_label": False,
                    "direct_claim_write": False,
                    "native_m6": False,
                    "movement_claim_allowed": False,
                },
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=causal_surface_digest
                if row is None
                else str(row.surface_digest),
                production_records=(record,),
            )

        if stale_lineage is not None:
            return self._producer_result_for_stale_surface_row(
                producer_policy=producer_policy,
                row=row,
                lineage_record=stale_lineage,
            )

        transported_lineage = self._surface_transport_record_for_transported_row(row)
        topology_state_reabsorption = (
            self._topology_state_reabsorption_record_for_surface_lineage(
                transported_lineage
            )
        )
        expected_source_digest = config["expected_source_surface_digest"]
        source_surface_digest = row.surface_values_after.get("source_surface_digest")
        source_node_id = int(config["source_node_id"])
        target_node_id, edge_id = self._validate_autonomous_packet_route(
            source_node_id=int(config["source_node_id"]),
            route={
                "target_node_id": int(config["target_node_id"]),
                "edge_id": int(config["edge_id"]),
            },
        )
        polarity_score = float(row.surface_values_after["boundary_polarity_score"])
        expected_polarity = str(config["expected_polarity"])
        signed_feedback = (
            polarity_score if expected_polarity == "positive" else -polarity_score
        )
        threshold = float(config["threshold"])
        packet_amount = float(config["packet_amount"])
        producer_scheduler_event_index = max(
            int(self._state.scheduler_event_index),
            int(row.scheduler_event_index),
        ) + 1
        thresholds = {
            "threshold": threshold,
            "packet_amount": packet_amount,
            "expected_polarity": expected_polarity,
        }
        observed_evidence = {
            "surface_id": row.surface_id,
            "surface_digest": row.surface_digest,
            "source_surface_digest": source_surface_digest,
            "source_pulse_event_id": row.pulse_event_id,
            "boundary_polarity_score": polarity_score,
            "signed_feedback": signed_feedback,
            "threshold": threshold,
            "threshold_source": "serialized_producer_policy",
            "polarity_policy_source": "serialized_producer_policy",
            "packet_amount_source": "serialized_producer_policy",
            "expected_polarity": expected_polarity,
            "expected_next_route_id": config["expected_next_route_id"],
            "expected_next_channel_id": config["expected_next_channel_id"],
            "regenerated_pulse_source": "feedback_eligibility",
            "copied_from_original_schedule": False,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "edge_id": edge_id,
            "producer_reads_committed_feedback_surface_row": True,
            "surface_lineage_current": True,
            "producer_reads_transport_successor": transported_lineage is not None,
            "surface_lineage_record_id": None
            if transported_lineage is None
            else transported_lineage.surface_lineage_record_id,
            "surface_lineage_record_digest": None
            if transported_lineage is None
            else transported_lineage.lineage_record_digest,
            "topology_event_id": None
            if transported_lineage is None
            else transported_lineage.topology_event_id,
            "topology_event_digest": None
            if transported_lineage is None
            else transported_lineage.topology_event_digest,
            "topology_state_reabsorption_verified": (
                topology_state_reabsorption is not None
            ),
            "topology_state_reabsorption_record_digest": None
            if topology_state_reabsorption is None
            else topology_state_reabsorption.topology_state_reabsorption_digest,
            "producer_mutation_ownership": "step_processes_packet_departure",
            "producer_mutated_coherence": False,
            "producer_marked_packet_processed": False,
            "producer_emitted_claim_label": False,
            "direct_coherence_write": False,
            "direct_support_mask_write": False,
            "direct_centroid_write": False,
            "direct_displacement_write": False,
            "direct_topology_write": False,
            "direct_claim_write": False,
            "native_m6": False,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
        }
        if (
            isinstance(expected_source_digest, str)
            and expected_source_digest
            and expected_source_digest != source_surface_digest
        ):
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=str(row.surface_digest),
                idempotency_key=f"{producer_policy}:{row.surface_digest}:order_mismatch",
                reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH,
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence=observed_evidence,
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=producer_scheduler_event_index,
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=str(row.surface_digest),
                production_records=(record,),
            )
        if signed_feedback < 0.0:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=str(row.surface_digest),
                idempotency_key=f"{producer_policy}:{row.surface_digest}:wrong_polarity",
                reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence=observed_evidence,
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=producer_scheduler_event_index,
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=str(row.surface_digest),
                production_records=(record,),
            )
        if signed_feedback < threshold:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=str(row.surface_digest),
                idempotency_key=f"{producer_policy}:{row.surface_digest}:subthreshold",
                reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence=observed_evidence,
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=producer_scheduler_event_index,
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=str(row.surface_digest),
                production_records=(record,),
            )

        available = float(self._state.base_state.nodes[source_node_id].coherence)
        if packet_amount > available + 1e-12:
            raise InvalidStateTransitionError(
                "feedback-coupled pulse exceeds source-node coherence"
            )
        if transported_lineage is not None and topology_state_reabsorption is None:
            return self._producer_result_for_missing_topology_state_reabsorption(
                producer_policy=producer_policy,
                row=row,
                lineage_record=transported_lineage,
            )
        idempotency_key = self._feedback_idempotency_key(
            producer_policy=producer_policy,
            row=row,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_id=edge_id,
            expected_polarity=expected_polarity,
            threshold=threshold,
            packet_amount=packet_amount,
        )
        idempotency_keys = self._autonomous_idempotency_keys()
        if idempotency_key in idempotency_keys:
            record = self._build_autonomous_production_record(
                producer_policy=producer_policy,
                causal_surface_digest=str(row.surface_digest),
                idempotency_key=idempotency_key,
                reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
                trigger_node_id=source_node_id,
                trigger_edge_id=edge_id,
                thresholds=thresholds,
                observed_evidence=observed_evidence,
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=producer_scheduler_event_index,
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=str(row.surface_digest),
                production_records=(record,),
            )

        ledger_before = self._state.packet_ledger
        assert ledger_before is not None
        before_event_ids = {event.event_id for event in ledger_before.event_queue_records}
        departure_event_time_key = max(
            [float(self._state.event_time_key)]
            + [
                float(event.event_time_key)
                for event in ledger_before.event_queue_records
            ]
        )
        self.schedule_packet_departure(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_id=edge_id,
            amount=packet_amount,
            departure_event_time_key=departure_event_time_key,
            arrival_event_time_key=config["arrival_event_time_key"],
            scheduler_event_index=(
                producer_scheduler_event_index
                + len(ledger_before.event_queue_records)
                + 1
            ),
            packet_index=len(ledger_before.packet_records),
        )
        ledger_after = self._state.packet_ledger
        assert ledger_after is not None
        new_events = [
            event
            for event in ledger_after.event_queue_records
            if event.event_id not in before_event_ids
        ]
        if len(new_events) != 1:
            raise InvalidStateTransitionError(
                "feedback-coupled pulse expected exactly one queued event"
            )
        queued_event = new_events[0]
        idempotency_keys.add(idempotency_key)
        self._store_autonomous_idempotency_keys(idempotency_keys)
        record = self._build_autonomous_production_record(
            producer_policy=producer_policy,
            causal_surface_digest=str(row.surface_digest),
            idempotency_key=idempotency_key,
            reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
            trigger_node_id=source_node_id,
            trigger_edge_id=edge_id,
            thresholds=thresholds,
            observed_evidence={
                **observed_evidence,
                "scheduled_packet_id": queued_event.packet_id,
                "scheduled_departure_event_time_key": float(
                    queued_event.event_time_key
                ),
            },
            scheduled_event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            scheduled_event_time_key=float(queued_event.event_time_key),
            scheduled_event_id=queued_event.event_id,
        )
        return LGRC9V3AutonomousProductionResult(
            producer_policy=producer_policy,
            scheduler_event_index=producer_scheduler_event_index,
            checkpoint_index=int(self._state.checkpoint_index),
            event_time_key=float(self._state.event_time_key),
            causal_surface_digest=str(row.surface_digest),
            production_records=(record,),
            state_mutated=True,
        )

    def _boundary_birth_trial_already_queued(
        self,
        *,
        parent_node_id: int,
        parent_port_id: int,
    ) -> bool:
        return any(
            int(trial["parent_node_id"]) == int(parent_node_id)
            and int(trial["parent_port_id"]) == int(parent_port_id)
            for trial in self._state.boundary_birth_trial_queue
            if trial.get("parent_port_id") is not None
        )

    def _produce_boundary_birth_trials(
        self,
        *,
        producer_policy: str,
        causal_surface_digest: str,
    ) -> LGRC9V3AutonomousProductionResult:
        modes = self._state.causal_modes
        idempotency_keys = self._autonomous_idempotency_keys()
        records: list[LGRC9V3AutonomousProductionRecord] = []

        if (
            not bool(modes.get("causal_boundary_birth_allowed", False))
            or modes.get("causal_boundary_birth_policy")
            != LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
        ):
            records.append(
                self._build_autonomous_production_record(
                    producer_policy=producer_policy,
                    causal_surface_digest=causal_surface_digest,
                    idempotency_key=f"{producer_policy}:{causal_surface_digest}",
                    reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
                    observed_evidence={
                        "causal_boundary_birth_allowed": bool(
                            modes.get("causal_boundary_birth_allowed", False)
                        ),
                        "causal_boundary_birth_policy": modes.get(
                            "causal_boundary_birth_policy"
                        ),
                    },
                )
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=causal_surface_digest,
                production_records=tuple(records),
            )

        lambda_birth = float(self._params.evolution.get("lambda_birth", 0.0))
        if lambda_birth <= 0.0:
            records.append(
                self._build_autonomous_production_record(
                    producer_policy=producer_policy,
                    causal_surface_digest=causal_surface_digest,
                    idempotency_key=f"{producer_policy}:{causal_surface_digest}",
                    reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
                    observed_evidence={"lambda_birth": lambda_birth},
                )
            )
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=causal_surface_digest,
                production_records=tuple(records),
            )

        candidates: list[tuple[int, int, float, float, str]] = []
        skipped_count = 0
        for parent_node_id in sorted(
            self._state.base_state.topology.iter_live_node_ids()
        ):
            inactive_ports = self._inactive_port_ids(int(parent_node_id))
            if not inactive_ports:
                continue
            outward_flux = self._outward_flux_pressure(int(parent_node_id))
            if outward_flux <= 0.0:
                continue
            parent_port_id = int(inactive_ports[0])
            birth_probability = 1.0 - math.exp(-lambda_birth * outward_flux)
            idempotency_key = self._autonomous_boundary_birth_idempotency_key(
                producer_policy=producer_policy,
                parent_node_id=int(parent_node_id),
                parent_port_id=parent_port_id,
                outward_flux_pressure=outward_flux,
                birth_probability=birth_probability,
            )
            if idempotency_key in idempotency_keys or (
                self._boundary_birth_trial_already_queued(
                    parent_node_id=int(parent_node_id),
                    parent_port_id=parent_port_id,
                )
            ):
                skipped_count += 1
                records.append(
                    self._build_autonomous_production_record(
                        producer_policy=producer_policy,
                        causal_surface_digest=causal_surface_digest,
                        idempotency_key=idempotency_key,
                        reason_code=(
                            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP
                        ),
                        trigger_node_id=int(parent_node_id),
                        thresholds={
                            "lambda_birth": lambda_birth,
                            "birth_probability": birth_probability,
                        },
                        observed_evidence={
                            "parent_port_id": parent_port_id,
                            "outward_flux_pressure": outward_flux,
                            "queued_trial_exists": True,
                        },
                    )
                )
                continue
            candidates.append(
                (
                    int(parent_node_id),
                    parent_port_id,
                    outward_flux,
                    birth_probability,
                    idempotency_key,
                )
            )

        if not candidates and not records:
            records.append(
                self._build_autonomous_production_record(
                    producer_policy=producer_policy,
                    causal_surface_digest=causal_surface_digest,
                    idempotency_key=f"{producer_policy}:{causal_surface_digest}",
                    reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
                    observed_evidence={
                        "lambda_birth": lambda_birth,
                        "eligible_parent_count": 0,
                    },
                )
            )

        if candidates:
            rng = random.Random()
            if self._state.base_state.rng_state is None:
                rng.seed(int(self._params.evolution.get("rng_seed", 0)))
            else:
                rng.setstate(self._state.base_state.rng_state)
            event_time_key = float(self._state.event_time_key)
            ledger = self._state.packet_ledger
            assert ledger is not None
            packet_queue_len = len(ledger.event_queue_records)
            birth_queue_len = len(self._state.boundary_birth_trial_queue)
            for candidate_index, (
                parent_node_id,
                parent_port_id,
                outward_flux,
                birth_probability,
                idempotency_key,
            ) in enumerate(candidates):
                scheduler_event_index = (
                    int(self._state.scheduler_event_index)
                    + packet_queue_len
                    + birth_queue_len
                    + candidate_index
                    + 1
                )
                rng_sample = rng.random()
                self.schedule_causal_boundary_birth_trial(
                    parent_node_id=parent_node_id,
                    parent_port_id=parent_port_id,
                    outward_flux_pressure=outward_flux,
                    event_time_key=event_time_key,
                    scheduler_event_index=scheduler_event_index,
                    rng_sample=rng_sample,
                    tau_0=1.0,
                )
                queued_trial = next(
                    trial
                    for trial in self._state.boundary_birth_trial_queue
                    if int(trial["scheduler_event_index"]) == scheduler_event_index
                    and int(trial["parent_node_id"]) == parent_node_id
                    and int(trial["parent_port_id"]) == parent_port_id
                )
                trial_event_id = str(queued_trial["trial_event_id"])
                idempotency_keys.add(idempotency_key)
                records.append(
                    self._build_autonomous_production_record(
                        producer_policy=producer_policy,
                        causal_surface_digest=causal_surface_digest,
                        idempotency_key=idempotency_key,
                        reason_code=(
                            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_BOUNDARY_BIRTH_TRIAL_SCHEDULED
                        ),
                        trigger_node_id=parent_node_id,
                        thresholds={
                            "lambda_birth": lambda_birth,
                            "birth_probability": birth_probability,
                            "rng_sample": rng_sample,
                        },
                        observed_evidence={
                            "parent_port_id": parent_port_id,
                            "outward_flux_pressure": outward_flux,
                            "tau_0": 1.0,
                            "birth_acceptance_deferred_to_step": True,
                        },
                        scheduled_event_kind=LGRC9V3_CAUSAL_BOUNDARY_BIRTH_TRIAL_EVENT_KIND,
                        scheduled_event_time_key=event_time_key,
                        scheduled_event_id=trial_event_id,
                    )
                )
            self._state.base_state.rng_state = rng.getstate()
            self._store_autonomous_idempotency_keys(idempotency_keys)

        return LGRC9V3AutonomousProductionResult(
            producer_policy=producer_policy,
            scheduler_event_index=int(self._state.scheduler_event_index),
            checkpoint_index=int(self._state.checkpoint_index),
            event_time_key=float(self._state.event_time_key),
            causal_surface_digest=causal_surface_digest,
            production_records=tuple(records),
            state_mutated=bool(candidates),
        )

    def produce_events(
        self,
        *,
        policy: str = LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    ) -> LGRC9V3AutonomousProductionResult:
        """Inspect runtime state and schedule eligible causal work.

        Producers enqueue work; only ``step()`` consumes queued work. The
        disabled policy remains a no-op, while active policies must emit
        auditable production records for every scheduled or skipped route.
        """

        producer_policy = validate_lgrc9v3_autonomous_producer_policy(policy)
        surface_digest = build_lgrc9v3_autonomous_surface_digest(
            self._autonomous_producer_surface()
        )
        if producer_policy == LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED:
            return build_lgrc9v3_disabled_autonomous_production_result(
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=surface_digest,
            )
        if producer_policy in {
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
        } and not self._causal_pulse_substrate_surface_enabled():
            return LGRC9V3AutonomousProductionResult(
                producer_policy=producer_policy,
                scheduler_event_index=int(self._state.scheduler_event_index),
                checkpoint_index=int(self._state.checkpoint_index),
                event_time_key=float(self._state.event_time_key),
                causal_surface_digest=surface_digest,
                production_records=(),
            )
        if producer_policy == (
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        ):
            return self._record_autonomous_production_result(
                self._produce_packet_departures_from_flux_routes(
                    producer_policy=producer_policy,
                    causal_surface_digest=surface_digest,
                )
            )
        if producer_policy == (
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        ):
            return self._record_autonomous_production_result(
                self._produce_packet_departure_from_route_surplus(
                    producer_policy=producer_policy,
                    causal_surface_digest=surface_digest,
                )
            )
        if producer_policy == (
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        ):
            return self._record_autonomous_production_result(
                self._produce_packet_departure_from_pulse_substrate_coupling(
                    producer_policy=producer_policy,
                    causal_surface_digest=surface_digest,
                )
            )
        if producer_policy == (
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
        ):
            return self._record_autonomous_production_result(
                self._produce_packet_departure_from_feedback_eligibility(
                    producer_policy=producer_policy,
                    causal_surface_digest=surface_digest,
                )
            )
        if producer_policy == LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL:
            return self._record_autonomous_production_result(
                self._produce_boundary_birth_trials(
                    producer_policy=producer_policy,
                    causal_surface_digest=surface_digest,
                )
            )
        raise InvalidParamsError(
            f"autonomous producer policy {producer_policy!r} is planned but "
            "not implemented yet"
        )

    def set_causal_flux_routes(
        self,
        routes: Mapping[int, Sequence[Mapping[str, Any]]],
    ) -> None:
        """Configure explicit arrival-triggered outbound packet routes.

        Routes are keyed by the arrived packet's target node. Each route must
        name `target_node_id` and `edge_id`. It may name either an absolute
        `amount` or an `amount_fraction` of the arrived packet amount. If
        neither is supplied, the route forwards the arrived packet amount.
        """

        normalized: dict[int, list[dict[str, Any]]] = {}
        for source_node_id, node_routes in routes.items():
            source_id = int(source_node_id)
            if source_id < 0:
                raise ValueError("route source node id must be >= 0")
            normalized_routes: list[dict[str, Any]] = []
            for route in node_routes:
                route_mapping = dict(route)
                if "target_node_id" not in route_mapping:
                    raise ValueError("causal flux route requires target_node_id")
                if "edge_id" not in route_mapping:
                    raise ValueError("causal flux route requires edge_id")
                target_id = int(route_mapping["target_node_id"])
                edge_id = int(route_mapping["edge_id"])
                if target_id < 0 or edge_id < 0:
                    raise ValueError("route target_node_id and edge_id must be >= 0")
                normalized_route: dict[str, Any] = {
                    "target_node_id": target_id,
                    "edge_id": edge_id,
                }
                if "amount" in route_mapping:
                    amount = float(route_mapping["amount"])
                    if amount < 0.0:
                        raise ValueError("route amount must be >= 0")
                    normalized_route["amount"] = amount
                if "amount_fraction" in route_mapping:
                    amount_fraction = float(route_mapping["amount_fraction"])
                    if amount_fraction < 0.0:
                        raise ValueError("route amount_fraction must be >= 0")
                    normalized_route["amount_fraction"] = amount_fraction
                if "arrival_event_time_key" in route_mapping:
                    arrival_key = float(route_mapping["arrival_event_time_key"])
                    if arrival_key < 0.0:
                        raise ValueError("route arrival_event_time_key must be >= 0")
                    normalized_route["arrival_event_time_key"] = arrival_key
                normalized_routes.append(normalized_route)
            normalized[source_id] = normalized_routes
        self._state.causal_flux_routes = normalized

    def set_route_aspect_surplus_trigger(
        self,
        *,
        route_aspect: LGRC9V3RouteAspect,
        source_pole_id: str,
        reference_mass: float,
        trigger_threshold: float,
        packet_amount: float,
        eligible_channel_id: str | None = None,
        arrival_event_time_key: float | None = None,
    ) -> None:
        """Configure a route-aspect surplus trigger producer.

        This stores producer eligibility data only. It does not debit
        coherence, create packets, or emit self-rearm evidence.
        """

        validated = validate_lgrc9v3_route_aspect(
            route_aspect,
            state=self._state.base_state,
        )
        if not isinstance(source_pole_id, str) or not source_pole_id:
            raise ValueError("source_pole_id must be a non-empty string")
        if source_pole_id not in validated.pole_regions:
            raise ValueError("source_pole_id must name a route-aspect pole")
        reference = _nonnegative_finite_float(
            reference_mass,
            context="reference_mass",
        )
        threshold = _nonnegative_finite_float(
            trigger_threshold,
            context="trigger_threshold",
        )
        amount = _nonnegative_finite_float(packet_amount, context="packet_amount")
        if amount <= 0.0:
            raise ValueError("packet_amount must be > 0")
        if arrival_event_time_key is not None:
            _nonnegative_finite_float(
                arrival_event_time_key,
                context="arrival_event_time_key",
            )
        channel = self._select_route_aspect_trigger_channel(
            route_aspect=validated,
            source_pole_id=source_pole_id,
            eligible_channel_id=eligible_channel_id,
        )
        config = {
            "route_aspect": validated.to_artifact(),
            "source_pole_id": str(source_pole_id),
            "reference_mass": float(reference),
            "trigger_threshold": float(threshold),
            "packet_amount": float(amount),
            "eligible_channel_id": channel.channel_id,
            "arrival_event_time_key": None
            if arrival_event_time_key is None
            else float(arrival_event_time_key),
            "route_aspect_digest": validated.route_aspect_digest,
            "pole_region_digest": validated.pole_region_digest,
            "channel_sequence_digest": validated.channel_sequence_digest,
        }
        self._state.cached_quantities[
            LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY
        ] = config

    def set_pulse_substrate_coupling_producer(
        self,
        *,
        target_node_id: int,
        edge_id: int,
        threshold: float,
        packet_amount: float,
        reference_value: float = 0.0,
        source_node_selector: str = "surface_target",
        arrival_event_time_key: float | None = None,
        enabled: bool = True,
    ) -> None:
        """Configure packet scheduling from committed pulse-substrate rows.

        This stores producer eligibility policy only. It does not mutate
        coherence, write support/centroid/displacement/topology state, or emit
        claims. If enabled, `produce_events()` may enqueue packet work that is
        later consumed only by `step()`.
        """

        if source_node_selector not in {"surface_target", "surface_source"}:
            raise ValueError(
                "source_node_selector must be surface_target or surface_source"
            )
        target_id = int(target_node_id)
        edge = int(edge_id)
        if target_id < 0 or edge < 0:
            raise ValueError("target_node_id and edge_id must be >= 0")
        trigger_threshold = _nonnegative_finite_float(
            threshold,
            context="pulse_substrate_coupling.threshold",
        )
        reference = _nonnegative_finite_float(
            reference_value,
            context="pulse_substrate_coupling.reference_value",
        )
        amount = _nonnegative_finite_float(
            packet_amount,
            context="pulse_substrate_coupling.packet_amount",
        )
        if amount <= 0.0:
            raise ValueError("packet_amount must be > 0")
        if arrival_event_time_key is not None:
            _nonnegative_finite_float(
                arrival_event_time_key,
                context="pulse_substrate_coupling.arrival_event_time_key",
            )
        self._state.cached_quantities[LGRC9V3_PULSE_SUBSTRATE_COUPLING_CONFIG_KEY] = {
            "enabled": bool(enabled),
            "source_node_selector": source_node_selector,
            "target_node_id": target_id,
            "edge_id": edge,
            "threshold": float(trigger_threshold),
            "reference_value": float(reference),
            "packet_amount": float(amount),
            "arrival_event_time_key": None
            if arrival_event_time_key is None
            else float(arrival_event_time_key),
        }

    def set_feedback_coupled_pulse_producer(
        self,
        *,
        source_node_id: int,
        target_node_id: int,
        edge_id: int,
        threshold: float,
        packet_amount: float,
        expected_polarity: str = "positive",
        expected_source_surface_digest: str | None = None,
        expected_next_route_id: str | None = None,
        expected_next_channel_id: str | None = None,
        arrival_event_time_key: float | None = None,
        enabled: bool = True,
    ) -> None:
        """Configure feedback eligibility scheduling over native surface rows."""

        source_id = int(source_node_id)
        target_id = int(target_node_id)
        edge = int(edge_id)
        if source_id < 0 or target_id < 0 or edge < 0:
            raise ValueError("source_node_id, target_node_id, and edge_id must be >= 0")
        if expected_polarity not in {"positive", "negative"}:
            raise ValueError("expected_polarity must be positive or negative")
        trigger_threshold = _nonnegative_finite_float(
            threshold,
            context="feedback_coupled_pulse.threshold",
        )
        amount = _nonnegative_finite_float(
            packet_amount,
            context="feedback_coupled_pulse.packet_amount",
        )
        if amount <= 0.0:
            raise ValueError("packet_amount must be > 0")
        if arrival_event_time_key is not None:
            _nonnegative_finite_float(
                arrival_event_time_key,
                context="feedback_coupled_pulse.arrival_event_time_key",
            )
        self._state.cached_quantities[LGRC9V3_FEEDBACK_COUPLED_PULSE_CONFIG_KEY] = {
            "enabled": bool(enabled),
            "source_node_id": source_id,
            "target_node_id": target_id,
            "edge_id": edge,
            "threshold": float(trigger_threshold),
            "packet_amount": float(amount),
            "expected_polarity": expected_polarity,
            "expected_source_surface_digest": expected_source_surface_digest,
            "expected_next_route_id": expected_next_route_id,
            "expected_next_channel_id": expected_next_channel_id,
            "arrival_event_time_key": None
            if arrival_event_time_key is None
            else float(arrival_event_time_key),
        }

    def schedule_causal_boundary_birth_trial(
        self,
        *,
        parent_node_id: int,
        parent_port_id: int | None = None,
        outward_flux_pressure: float | None = None,
        event_time_key: float | None = None,
        scheduler_event_index: int | None = None,
        rng_sample: float | None = None,
        edge_delay: float | None = None,
        tau_0: float = 1.0,
    ) -> None:
        """Schedule one causal frontier birth trial into the runtime loop."""

        trial: dict[str, Any] = {
            "parent_node_id": int(parent_node_id),
            "parent_port_id": None if parent_port_id is None else int(parent_port_id),
            "outward_flux_pressure": None
            if outward_flux_pressure is None
            else float(outward_flux_pressure),
            "event_time_key": float(
                self._state.event_time_key
                if event_time_key is None
                else event_time_key
            ),
            "scheduler_event_index": int(
                self._state.scheduler_event_index
                + len(self._state.boundary_birth_trial_queue)
                + 1
                if scheduler_event_index is None
                else scheduler_event_index
            ),
            "rng_sample": None if rng_sample is None else float(rng_sample),
            "edge_delay": None if edge_delay is None else float(edge_delay),
            "tau_0": float(tau_0),
        }
        if trial["event_time_key"] < 0.0:
            raise ValueError("event_time_key must be >= 0")
        if trial["scheduler_event_index"] < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        trial_digest = build_lgrc9v3_autonomous_surface_digest(
            {
                "trial_kind": LGRC9V3_CAUSAL_BOUNDARY_BIRTH_TRIAL_EVENT_KIND,
                "parent_node_id": trial["parent_node_id"],
                "parent_port_id": trial["parent_port_id"],
                "event_time_key": trial["event_time_key"],
                "scheduler_event_index": trial["scheduler_event_index"],
                "outward_flux_pressure": trial["outward_flux_pressure"],
                "rng_sample": trial["rng_sample"],
            }
        )
        trial["trial_event_id"] = f"lgrc9v3-boundary-birth-trial-{trial_digest[:24]}"
        self._state.boundary_birth_trial_queue.append(trial)
        self._state.boundary_birth_trial_queue.sort(
            key=lambda item: (
                float(item["event_time_key"]),
                int(item["scheduler_event_index"]),
                int(item["parent_node_id"]),
                -1
                if item["parent_port_id"] is None
                else int(item["parent_port_id"]),
            )
        )

    def schedule_packet_departure(
        self,
        *,
        source_node_id: int,
        target_node_id: int,
        edge_id: int,
        amount: float,
        departure_event_time_key: float | None = None,
        arrival_event_time_key: float | None = None,
        scheduler_event_index: int | None = None,
        packet_index: int = 0,
        source_lineage_id: str | None = None,
        target_lineage_id: str | None = None,
    ) -> None:
        """Schedule one packet departure into the model-owned event queue."""

        ledger = self._state.packet_ledger
        assert ledger is not None
        departure_key = (
            float(self._state.event_time_key)
            if departure_event_time_key is None
            else float(departure_event_time_key)
        )
        arrival_key = (
            derive_lgrc9v3_packet_arrival_event_time_key(
                departure_event_time_key=departure_key,
                edge_id=edge_id,
                edge_causal_delay=self._state.edge_causal_delay,
            )
            if arrival_event_time_key is None
            else float(arrival_event_time_key)
        )
        scheduler_index = (
            self._state.scheduler_event_index + len(ledger.event_queue_records) + 1
            if scheduler_event_index is None
            else int(scheduler_event_index)
        )
        self._state.packet_ledger = with_ordered_lgrc9v3_event_queue(
            schedule_lgrc9v3_packet_departure(
                self._state.base_state,
                ledger,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                edge_id=edge_id,
                amount=amount,
                departure_event_time_key=departure_key,
                arrival_event_time_key=arrival_key,
                scheduler_event_index=scheduler_index,
                packet_index=packet_index,
                source_lineage_id=source_lineage_id,
                target_lineage_id=target_lineage_id,
            )
        )

    def _inactive_port_ids(self, node_id: int) -> tuple[int, ...]:
        return tuple(
            port_id
            for port_id in range(1, 10)
            if not self._state.base_state.topology.port_is_occupied(
                int(node_id),
                port_id_to_slot(port_id),
            )
        )

    def _oriented_flux(self, *, edge_id: int, node_id: int) -> float:
        port_edge = self._state.base_state.port_edges[int(edge_id)]
        if int(port_edge.node_u) == int(node_id):
            return float(port_edge.flux_uv)
        if int(port_edge.node_v) == int(node_id):
            return float(-port_edge.flux_uv)
        raise SnapshotCompatibilityError(
            f"edge {edge_id} is not incident to node {node_id}"
        )

    def _outward_flux_pressure(self, node_id: int) -> float:
        return float(
            sum(
                max(0.0, self._oriented_flux(edge_id=edge_id, node_id=node_id))
                for edge_id in self._state.base_state.topology.incident_edge_ids(
                    int(node_id)
                )
            )
        )

    def _runtime_budget_surface(self) -> float:
        ledger = self._state.packet_ledger
        in_flight = 0.0 if ledger is None else float(ledger.in_flight_packet_total)
        return float(
            sum(
                float(node.coherence)
                for node in self._state.base_state.nodes.values()
            )
            + in_flight
        )

    def _assert_boundary_birth_queue_surface(self, *, event_time_key: float) -> None:
        ledger = self._state.packet_ledger
        assert ledger is not None
        earlier_packet_events = [
            event.event_id
            for event in ledger.event_queue_records
            if float(event.event_time_key) < float(event_time_key)
        ]
        if earlier_packet_events:
            raise InvalidStateTransitionError(
                "causal boundary birth cannot bypass earlier packet events"
            )

    def apply_causal_boundary_birth_trial(
        self,
        *,
        parent_node_id: int,
        parent_port_id: int | None = None,
        outward_flux_pressure: float | None = None,
        event_time_key: float | None = None,
        scheduler_event_index: int | None = None,
        rng_sample: float | None = None,
        edge_delay: float | None = None,
        tau_0: float = 1.0,
    ) -> list[GRCEvent]:
        """Try one explicit LGRC9V3 causal boundary birth.

        Boundary birth is disabled by default. When enabled, this method uses
        the same outward-flux probability law as GRC9V3 growth, but records the
        mutation as an LGRC9V3 causal topology event with parent proper-time
        inheritance and explicit edge-delay evidence.
        """

        modes = self._state.causal_modes
        if not bool(modes.get("causal_boundary_birth_allowed", False)):
            self._state.base_state.cached_quantities[
                "last_causal_boundary_birth_status"
            ] = "disabled"
            return []
        if (
            modes.get("causal_layer_mode")
            != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
        ) or modes.get("lgrc_runtime_level") != LGRC_RUNTIME_LEVEL_LGRC3:
            raise InvalidStateTransitionError(
                "causal boundary birth requires LGRC-3 "
                "topology_changing_causal_history mode"
            )
        if (
            modes.get("causal_boundary_birth_policy")
            != LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
        ):
            raise InvalidStateTransitionError(
                "causal boundary birth requires "
                "grc9v3_outward_flux_probability policy"
            )
        if (
            modes.get("causal_boundary_birth_coherence_source")
            != LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT
        ):
            raise InvalidStateTransitionError(
                "causal boundary birth currently supports only parent_debit "
                "coherence source"
            )
        if (
            modes.get("causal_boundary_birth_edge_delay_policy")
            != LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0
        ):
            raise InvalidStateTransitionError(
                "causal boundary birth currently supports only explicit_or_tau0 "
                "edge-delay policy"
            )

        base_state = self._state.base_state
        resolved_parent_id = int(parent_node_id)
        if resolved_parent_id not in base_state.nodes:
            raise InvalidStateTransitionError("parent_node_id is not live")
        if not base_state.topology.has_node(resolved_parent_id):
            raise InvalidStateTransitionError("parent_node_id is not live")

        inactive_ports = self._inactive_port_ids(resolved_parent_id)
        if parent_port_id is None:
            if not inactive_ports:
                base_state.cached_quantities[
                    "last_causal_boundary_birth_status"
                ] = "no_inactive_port"
                return []
            resolved_parent_port_id = inactive_ports[0]
        else:
            resolved_parent_port_id = int(parent_port_id)
            if resolved_parent_port_id not in inactive_ports:
                raise InvalidStateTransitionError(
                    "parent_port_id must be an inactive canonical 1..9 port"
                )

        lambda_birth = float(self._params.evolution.get("lambda_birth", 0.0))
        if lambda_birth <= 0.0:
            base_state.cached_quantities[
                "last_causal_boundary_birth_status"
            ] = "lambda_birth_disabled"
            return []
        outward_flux = (
            self._outward_flux_pressure(resolved_parent_id)
            if outward_flux_pressure is None
            else float(outward_flux_pressure)
        )
        if outward_flux < 0.0 or not math.isfinite(outward_flux):
            raise ValueError("outward_flux_pressure must be finite and >= 0")
        if outward_flux <= 0.0:
            base_state.cached_quantities[
                "last_causal_boundary_birth_status"
            ] = "no_outward_flux_pressure"
            return []
        birth_probability = 1.0 - math.exp(-lambda_birth * outward_flux)
        if rng_sample is None:
            rng = random.Random()
            if base_state.rng_state is None:
                rng.seed(int(self._params.evolution.get("rng_seed", 0)))
            else:
                rng.setstate(base_state.rng_state)
            resolved_rng_sample = rng.random()
            base_state.rng_state = rng.getstate()
        else:
            resolved_rng_sample = float(rng_sample)
        if (
            resolved_rng_sample < 0.0
            or resolved_rng_sample >= 1.0
            or not math.isfinite(resolved_rng_sample)
        ):
            raise ValueError("rng_sample must be finite and in [0, 1)")
        if resolved_rng_sample >= birth_probability:
            base_state.cached_quantities[
                "last_causal_boundary_birth_status"
            ] = "rng_rejected"
            base_state.cached_quantities[
                "last_causal_boundary_birth_probability"
            ] = birth_probability
            return []

        resolved_event_time_key = (
            float(self._state.event_time_key)
            if event_time_key is None
            else float(event_time_key)
        )
        if resolved_event_time_key < 0.0 or not math.isfinite(
            resolved_event_time_key
        ):
            raise ValueError("event_time_key must be finite and >= 0")
        self._assert_boundary_birth_queue_surface(
            event_time_key=resolved_event_time_key
        )
        resolved_scheduler_index = (
            int(self._state.scheduler_event_index) + 1
            if scheduler_event_index is None
            else int(scheduler_event_index)
        )
        if resolved_scheduler_index < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        resolved_edge_delay = float(tau_0 if edge_delay is None else edge_delay)
        if resolved_edge_delay <= 0.0 or not math.isfinite(resolved_edge_delay):
            raise ValueError("edge_delay must be finite and > 0")

        pre_topology_signature = _runtime_topology_signature(self._state)
        budget_before = self._runtime_budget_surface()
        parent_time_before = float(
            self._state.node_proper_time.get(resolved_parent_id, 0.0)
        )
        proper_time_update = self._advance_node_proper_time(
            node_id=resolved_parent_id,
            event_time_key=resolved_event_time_key,
        )
        parent_time_after = float(
            self._state.node_proper_time.get(resolved_parent_id, 0.0)
        )
        alpha_seed = float(self._params.evolution.get("alpha_seed", 0.1))
        w_bond = float(self._params.evolution.get("w_bond", 1.0))
        parent_state = base_state.nodes[resolved_parent_id]
        parent_coherence_before = float(parent_state.coherence)
        transfer = max(
            0.0,
            min(parent_coherence_before, alpha_seed * parent_coherence_before),
        )
        child_node_id = base_state.topology.add_node(
            {
                "role": "lgrc9v3_causal_boundary_child",
                "parent_node_id": resolved_parent_id,
            }
        )
        edge_id = base_state.topology.connect_ports(
            resolved_parent_id,
            port_id_to_slot(resolved_parent_port_id),
            child_node_id,
            port_id_to_slot(1),
            payload={
                "kind": "lgrc9v3_causal_boundary_birth",
                "parent_node_id": resolved_parent_id,
            },
        )
        base_state.port_edges[edge_id] = PortEdge(
            node_u=resolved_parent_id,
            port_u=resolved_parent_port_id,
            node_v=child_node_id,
            port_v=1,
            conductance=w_bond,
            flux_uv=0.0,
        )
        base_state.base_conductance[edge_id] = w_bond
        base_state.geometric_length[edge_id] = 1.0
        base_state.temporal_delay[edge_id] = resolved_edge_delay
        base_state.flux_coupling[edge_id] = 0.0
        base_state.nodes[resolved_parent_id] = GRC9V3NodeState(
            coherence=parent_coherence_before - transfer,
            gradient_row_basis=list(parent_state.gradient_row_basis),
            signed_hessian_row_basis=list(parent_state.signed_hessian_row_basis),
            net_flux_summary=list(parent_state.net_flux_summary),
            basin_mass=parent_state.basin_mass,
            basin_id=parent_state.basin_id,
            parent_id=parent_state.parent_id,
            depth=parent_state.depth,
        )
        base_state.nodes[child_node_id] = GRC9V3NodeState(
            coherence=transfer,
            basin_mass=transfer,
            basin_id=child_node_id,
            parent_id=parent_state.basin_id,
            depth=parent_state.depth + 1,
        )
        base_state.potential[child_node_id] = 0.0
        self._state.node_proper_time[child_node_id] = parent_time_after
        self._state.node_last_update_proper_time[child_node_id] = parent_time_after
        self._state.node_last_update_event_time_key[child_node_id] = (
            resolved_event_time_key
        )
        self._state.lapse[child_node_id] = float(
            self._state.lapse.get(resolved_parent_id, 1.0)
        )
        self._state.edge_causal_delay[edge_id] = resolved_edge_delay
        self._state.scheduler_event_index = resolved_scheduler_index
        self._state.event_time_key = resolved_event_time_key
        self._state.checkpoint_index += 1
        self._state.step_index = resolved_scheduler_index
        self._state.time = resolved_event_time_key
        base_state.step_index = resolved_scheduler_index
        base_state.time = resolved_event_time_key

        budget_after = self._runtime_budget_surface()
        post_topology_signature = _runtime_topology_signature(self._state)
        event_id = (
            "lgrc9v3-causal-boundary-birth-"
            f"{resolved_scheduler_index}-{resolved_parent_id}-"
            f"{resolved_parent_port_id}-{child_node_id}"
        )
        payload = {
            "event_schema_version": LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_SCHEMA_VERSION,
            "runtime_family": self.MODEL_FAMILY,
            "topology_event_id": event_id,
            "causal_boundary_birth_event_id": event_id,
            "scheduler_event_index": resolved_scheduler_index,
            "checkpoint_index": self._state.checkpoint_index,
            "event_time_key": resolved_event_time_key,
            "causal_layer_mode": self._state.causal_layer_mode,
            "lgrc_runtime_level": self._state.lgrc_runtime_level,
            "causal_boundary_birth_allowed": True,
            "causal_boundary_birth_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
            ),
            "causal_boundary_birth_coherence_source": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT
            ),
            "causal_boundary_birth_edge_delay_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0
            ),
            "parent_node_id": resolved_parent_id,
            "child_node_id": int(child_node_id),
            "parent_port_id": resolved_parent_port_id,
            "child_port_id": 1,
            "edge_id": int(edge_id),
            "outward_flux_pressure": outward_flux,
            "lambda_birth": lambda_birth,
            "birth_probability": birth_probability,
            "rng_sample": resolved_rng_sample,
            "birth_accepted": True,
            "alpha_seed": alpha_seed,
            "coherence_transfer": transfer,
            "parent_coherence_before": parent_coherence_before,
            "parent_coherence_after": parent_coherence_before - transfer,
            "child_coherence": transfer,
            "budget_before": budget_before,
            "budget_after": budget_after,
            "budget_error": budget_after - budget_before,
            "parent_proper_time_before": parent_time_before,
            "parent_proper_time_after": parent_time_after,
            "child_proper_time": parent_time_after,
            "proper_time_inheritance_policy": "parent_event_time_surface",
            "proper_time_update": proper_time_update,
            "edge_causal_delay": resolved_edge_delay,
            "pre_topology_signature": pre_topology_signature,
            "post_topology_signature": post_topology_signature,
            "packet_visibility": "packets_scheduled_after_birth_see_child",
            "state_mutated": True,
            "topology_mutated": True,
            "spark_event_emitted": False,
            "mechanical_expansion_emitted": False,
            "identity_acceptance_emitted": False,
        }
        event = GRCEvent(
            kind=LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND,
            step_index=resolved_scheduler_index,
            payload=payload,
            source_family=self.MODEL_FAMILY,
        )
        self._state.topology_event_log.append(event)
        self._state.event_log.append(event)
        ledger = self._state.packet_ledger
        assert ledger is not None
        self._state.packet_ledger = with_ordered_lgrc9v3_event_queue(
            build_lgrc9v3_packet_ledger(
                packet_records=ledger.packet_records,
                packet_event_records=ledger.packet_event_records,
                event_queue_records=ledger.event_queue_records,
                state=base_state,
                policies=dict(ledger.policies),
                budget_before=budget_before,
                budget_after=budget_after,
            )
        )
        base_state.cached_quantities[
            "last_causal_boundary_birth_status"
        ] = "accepted"
        base_state.cached_quantities["last_causal_boundary_birth_event"] = dict(
            payload
        )
        base_state.coarse_cache.clear()
        self.invalidate_causal_spark_diagnostics(reason="causal_boundary_birth")
        self._state.observables = dict(self.compute_observables())
        return [event]

    def _advance_node_proper_time(
        self,
        *,
        node_id: int,
        event_time_key: float,
    ) -> dict[str, Any]:
        resolved_node_id = int(node_id)
        if resolved_node_id < 0:
            raise ValueError("node_id must be >= 0")
        current_event_key = float(event_time_key)
        previous_event_key = float(
            self._state.node_last_update_event_time_key.get(resolved_node_id, 0.0)
        )
        if current_event_key < previous_event_key:
            raise ValueError("node event_time_key moved backward")
        lapse = float(self._state.lapse.get(resolved_node_id, 1.0))
        previous_tau = float(self._state.node_proper_time.get(resolved_node_id, 0.0))
        delta_event_time_key = current_event_key - previous_event_key
        delta_tau = lapse * delta_event_time_key
        new_tau = previous_tau + delta_tau
        self._state.node_proper_time[resolved_node_id] = new_tau
        self._state.node_last_update_proper_time[resolved_node_id] = new_tau
        self._state.node_last_update_event_time_key[resolved_node_id] = (
            current_event_key
        )
        return {
            "node_id": resolved_node_id,
            "previous_event_time_key": previous_event_key,
            "event_time_key": current_event_key,
            "delta_event_time_key": delta_event_time_key,
            "lapse": lapse,
            "previous_node_proper_time": previous_tau,
            "delta_tau": delta_tau,
            "node_proper_time": new_tau,
            "proper_time_accumulation_policy": self._state.causal_modes.get(
                "proper_time_accumulation_policy",
                PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER,
            ),
        }

    def _packet_processing_event(
        self,
        result: object,
        *,
        proper_time_update: Mapping[str, Any] | None = None,
    ) -> GRCEvent:
        processed_event = getattr(result, "processed_event")
        packet_record = getattr(result, "packet_record")
        payload = {
            "event_schema_version": LGRC9V3_RUNTIME_EVENT_SCHEMA_VERSION,
            "runtime_family": self.MODEL_FAMILY,
            "processed_event": _event_record_payload(processed_event),
            "packet_record": packet_record.to_record(),
            "scheduler_event_index": int(processed_event.scheduler_event_index),
            "checkpoint_index": int(self._state.checkpoint_index),
            "event_time_key": float(processed_event.event_time_key),
            "budget_before": float(result.budget_before),
            "budget_after": float(result.budget_after),
            "budget_error": float(result.budget_error),
            "state_mutated": bool(result.state_mutated),
            "topology_mutated": bool(result.topology_mutated),
            "spark_event_emitted": bool(result.spark_event_emitted),
            "mechanical_expansion_emitted": bool(
                result.mechanical_expansion_emitted
            ),
            "identity_acceptance_emitted": bool(
                result.identity_acceptance_emitted
            ),
            "proper_time_update": None
            if proper_time_update is None
            else dict(proper_time_update),
        }
        return GRCEvent(
            kind=processed_event.event_kind,
            step_index=int(processed_event.scheduler_event_index),
            payload=payload,
            source_family=self.MODEL_FAMILY,
        )

    def _route_amount(self, route: Mapping[str, Any], arrival_amount: float) -> float:
        if "amount" in route:
            return float(route["amount"])
        if "amount_fraction" in route:
            return float(arrival_amount) * float(route["amount_fraction"])
        return float(arrival_amount)

    def _apply_arrival_local_update(
        self,
        *,
        eligibility: object,
        proper_time_update: Mapping[str, Any],
    ) -> GRCEvent:
        target_node_id = int(getattr(eligibility, "target_node_id"))
        arrival_amount = float(getattr(eligibility, "amount"))
        arrival_event_id = str(getattr(eligibility, "arrival_event_id"))
        event_time_key = float(getattr(eligibility, "event_time_key"))
        scheduler_event_index = int(getattr(eligibility, "scheduler_event_index"))
        routes = list(self._state.causal_flux_routes.get(target_node_id, []))
        ledger_before = self._state.packet_ledger
        assert ledger_before is not None
        packet_ids_before = {packet.packet_id for packet in ledger_before.packet_records}
        event_ids_before = {
            event.event_id for event in ledger_before.event_queue_records
        }
        resolved_routes: list[tuple[Mapping[str, Any], float]] = []
        for route in routes:
            amount = self._route_amount(route, arrival_amount)
            if amount <= 0.0:
                continue
            resolved_routes.append((route, amount))
        outbound_total = sum(amount for _, amount in resolved_routes)
        available_coherence = float(
            self._state.base_state.nodes[target_node_id].coherence
        )
        if outbound_total > available_coherence + 1e-12:
            raise InvalidStateTransitionError(
                "arrival local update routes exceed available node coherence"
            )
        scheduled_count = 0
        for route_index, (route, amount) in enumerate(resolved_routes):
            ledger_now = self._state.packet_ledger
            assert ledger_now is not None
            self.schedule_packet_departure(
                source_node_id=target_node_id,
                target_node_id=int(route["target_node_id"]),
                edge_id=int(route["edge_id"]),
                amount=amount,
                departure_event_time_key=event_time_key,
                arrival_event_time_key=route.get("arrival_event_time_key"),
                scheduler_event_index=(
                    scheduler_event_index
                    + len(ledger_now.event_queue_records)
                    + scheduled_count
                    + 1
                ),
                packet_index=len(ledger_now.packet_records) + route_index,
            )
            scheduled_count += 1

        ledger_after = self._state.packet_ledger
        assert ledger_after is not None
        scheduled_packet_ids = tuple(
            sorted(
                packet.packet_id
                for packet in ledger_after.packet_records
                if packet.packet_id not in packet_ids_before
            )
        )
        scheduled_departure_event_ids = tuple(
            sorted(
                event.event_id
                for event in ledger_after.event_queue_records
                if event.event_id not in event_ids_before
            )
        )
        local_update_event_id = (
            "lgrc9v3-local-update-"
            f"{scheduler_event_index}-{target_node_id}-{arrival_event_id}"
        )
        payload = {
            "event_schema_version": LGRC9V3_LOCAL_UPDATE_EVENT_SCHEMA_VERSION,
            "runtime_family": self.MODEL_FAMILY,
            "local_update_event_id": local_update_event_id,
            "arrival_event_id": arrival_event_id,
            "scheduler_event_index": scheduler_event_index,
            "checkpoint_index": self._state.checkpoint_index,
            "event_time_key": event_time_key,
            "target_node_id": target_node_id,
            "arrival_amount": arrival_amount,
            "proper_time_update": dict(proper_time_update),
            "packetized_flux_applied": True,
            "delayed_evaluation_applied": False,
            "local_continuity_formula_applied": False,
            "causal_availability_source": "packet_arrival_eligibility",
            "route_count": len(routes),
            "scheduled_packet_count": len(scheduled_packet_ids),
            "scheduled_packet_ids": list(scheduled_packet_ids),
            "scheduled_departure_event_ids": list(scheduled_departure_event_ids),
            "state_mutated": True,
            "topology_mutated": False,
            "spark_event_emitted": False,
            "mechanical_expansion_emitted": False,
            "identity_acceptance_emitted": False,
        }
        self._state.local_update_log.append(dict(payload))
        return GRCEvent(
            kind=LGRC9V3_LOCAL_UPDATE_EVENT_KIND,
            step_index=scheduler_event_index,
            payload=payload,
            source_family=self.MODEL_FAMILY,
        )

    def invalidate_causal_spark_diagnostics(
        self,
        *,
        reason: str,
    ) -> None:
        """Invalidate causal diagnostic history after topology/lineage changes."""

        invalidate_previous_column_h_cache(
            self._state.base_state,
            reason=f"lgrc9v3:{reason}",
        )
        self._state.causal_spark_diagnostic_log.append(
            {
                "diagnostic_event": "invalidate_causal_spark_diagnostics",
                "reason": str(reason),
                "scheduler_event_index": int(self._state.scheduler_event_index),
                "checkpoint_index": int(self._state.checkpoint_index),
                "event_time_key": float(self._state.event_time_key),
                "causal_spark_evaluation_index": int(
                    self._state.causal_spark_evaluation_index
                ),
            }
        )

    def _causal_candidate_event_id(
        self,
        *,
        candidate_node_id: int,
        evaluation_index: int,
        ordinal: int,
    ) -> str:
        return (
            "lgrc9v3-causal-spark-candidate-"
            f"{int(evaluation_index)}-{int(candidate_node_id)}-{int(ordinal)}"
        )

    def _wrap_causal_spark_candidate(
        self,
        candidate: GRCEvent,
        *,
        evaluation_index: int,
        ordinal: int,
        trigger_kind: str,
        trigger_event_id: str | None,
        trigger_source: str,
        trigger_node_id: int | None,
        topology_signature: Mapping[str, Any],
    ) -> GRCEvent:
        payload = dict(candidate.payload)
        candidate_node_id = int(
            payload.get("candidate_node_id", payload.get("sink_node_id", -1))
        )
        causal_candidate_event_id = self._causal_candidate_event_id(
            candidate_node_id=candidate_node_id,
            evaluation_index=evaluation_index,
            ordinal=ordinal,
        )
        source_candidate_event_id = payload.get("candidate_event_id")
        payload.update(
            {
                "event_schema_version": (
                    LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_SCHEMA_VERSION
                ),
                "runtime_family": self.MODEL_FAMILY,
                "candidate_event_id": causal_candidate_event_id,
                "causal_candidate_event_id": causal_candidate_event_id,
                "source_grc9v3_candidate_event_id": source_candidate_event_id,
                "source_grc9v3_candidate_kind": candidate.kind,
                "source_grc9v3_event_schema_version": payload.get(
                    "event_schema_version"
                ),
                "causal_spark_evaluation_index": int(evaluation_index),
                "causal_spark_trigger_kind": str(trigger_kind),
                "causal_spark_trigger_event_id": trigger_event_id,
                "causal_spark_trigger_source": str(trigger_source),
                "causal_spark_trigger_node_id": trigger_node_id,
                "scheduler_event_index": int(self._state.scheduler_event_index),
                "checkpoint_index": int(self._state.checkpoint_index),
                "event_time_key": float(self._state.event_time_key),
                "candidate_node_proper_time": float(
                    self._state.node_proper_time.get(candidate_node_id, 0.0)
                ),
                "trigger_node_proper_time": None
                if trigger_node_id is None
                else float(self._state.node_proper_time.get(trigger_node_id, 0.0)),
                "node_proper_time_surface": _string_keyed_float_map(
                    self._state.node_proper_time
                ),
                "pre_expansion_topology_signature": dict(topology_signature),
                "diagnostic_source": LGRC9V3_CAUSAL_SPARK_DIAGNOSTIC_SOURCE,
                "spark_lane": str(
                    payload.get(
                        "spark_lane",
                        self._params.constitutive_semantic_modes.get(
                            "spark_lane",
                            "current_hybrid_signed_hessian",
                        ),
                    )
                ),
                "causal_diagnostic_history_source": (
                    "causal_spark_evaluation_index"
                ),
                "synchronous_step_index_used_for_history": False,
                "state_mutated": False,
                "topology_mutated": False,
                "mechanical_expansion_emitted": False,
                "identity_acceptance_emitted": False,
                "packet_transport_emitted": False,
            }
        )
        return GRCEvent(
            kind=LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND,
            step_index=int(self._state.scheduler_event_index),
            payload=payload,
            source_family=self.MODEL_FAMILY,
        )

    def _evaluate_causal_spark_diagnostics(
        self,
        *,
        trigger_kind: str,
        trigger_event_id: str | None,
        trigger_source: str,
        trigger_node_id: int | None,
    ) -> list[GRCEvent]:
        """Evaluate Lane A/Lane B spark predicates from a causal event snapshot."""

        self._state.causal_spark_evaluation_index += 1
        evaluation_index = int(self._state.causal_spark_evaluation_index)
        topology_signature = _runtime_topology_signature(self._state)
        previous_step_index = int(self._state.base_state.step_index)
        self._state.base_state.step_index = evaluation_index
        try:
            candidates = detect_hybrid_spark_candidates(
                self._state.base_state,
                evolution=self._params.evolution,
                modes=self._params.constitutive_semantic_modes,
                source_family="GRC9V3",
            )
        finally:
            self._state.base_state.step_index = previous_step_index

        events = [
            self._wrap_causal_spark_candidate(
                candidate,
                evaluation_index=evaluation_index,
                ordinal=ordinal,
                trigger_kind=trigger_kind,
                trigger_event_id=trigger_event_id,
                trigger_source=trigger_source,
                trigger_node_id=trigger_node_id,
                topology_signature=topology_signature,
            )
            for ordinal, candidate in enumerate(candidates)
        ]
        self._state.causal_spark_diagnostic_log.append(
            {
                "diagnostic_event": "evaluate_causal_spark_diagnostics",
                "causal_spark_evaluation_index": evaluation_index,
                "scheduler_event_index": int(self._state.scheduler_event_index),
                "checkpoint_index": int(self._state.checkpoint_index),
                "event_time_key": float(self._state.event_time_key),
                "trigger_kind": str(trigger_kind),
                "trigger_event_id": trigger_event_id,
                "trigger_source": str(trigger_source),
                "trigger_node_id": trigger_node_id,
                "candidate_event_ids": [
                    event.payload["candidate_event_id"] for event in events
                ],
                "candidate_count": len(events),
                "spark_lane": str(
                    self._params.constitutive_semantic_modes.get(
                        "spark_lane",
                        "current_hybrid_signed_hessian",
                    )
                ),
                "topology_signature": dict(topology_signature),
            }
        )
        return events

    def _event_from_artifact(
        self,
        *,
        kind: str,
        artifact: Mapping[str, Any],
        step_index: int | None = None,
    ) -> GRCEvent:
        return GRCEvent(
            kind=kind,
            step_index=(
                int(artifact.get("scheduler_event_index", self._state.scheduler_event_index))
                if step_index is None
                else int(step_index)
            ),
            payload=dict(artifact),
            source_family=self.MODEL_FAMILY,
        )

    def _apply_causal_topology_integration(
        self,
        causal_candidates: Sequence[GRCEvent],
    ) -> list[GRCEvent]:
        """Route causal spark candidates to topology events when enabled."""

        modes = self._state.causal_modes
        if not bool(modes.get("causal_topology_integration_allowed", False)):
            return []
        if not bool(modes.get("causal_spark_expansion_allowed", False)):
            return []
        if (
            modes.get("causal_layer_mode")
            != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
        ) or modes.get("lgrc_runtime_level") != LGRC_RUNTIME_LEVEL_LGRC3:
            raise InvalidStateTransitionError(
                "active topology integration requires LGRC-3 "
                "topology_changing_causal_history mode"
            )

        events: list[GRCEvent] = []
        for candidate_event in causal_candidates:
            candidate_node_id = int(
                candidate_event.payload.get(
                    "sink_node_id",
                    candidate_event.payload.get("candidate_node_id", -1),
                )
            )
            if not self._state.base_state.topology.has_node(candidate_node_id):
                continue
            ledger_before = deepcopy(self._state.packet_ledger)
            assert ledger_before is not None
            parent_time_surface = dict(self._state.node_proper_time)
            expansion_event = apply_mechanical_expansion(
                self._state.base_state,
                candidate_event,
                evolution=self._params.evolution,
                modes=self._params.constitutive_semantic_modes,
                source_family=self.MODEL_FAMILY,
            )
            expansion_event.payload.update(
                {
                    "runtime_family": self.MODEL_FAMILY,
                    "causal_layer_mode": self._state.causal_layer_mode,
                    "lgrc_runtime_level": self._state.lgrc_runtime_level,
                    "scheduler_event_index": int(self._state.scheduler_event_index),
                    "checkpoint_index": int(self._state.checkpoint_index),
                    "event_time_key": float(self._state.event_time_key),
                    "source_causal_candidate_event_id": candidate_event.payload.get(
                        "causal_candidate_event_id",
                        candidate_event.payload.get("candidate_event_id"),
                    ),
                    "state_mutated": True,
                    "topology_mutated": True,
                    "mechanical_expansion_emitted": True,
                    "identity_acceptance_emitted": False,
                }
            )
            events.append(expansion_event)
            self._state.topology_event_log.append(expansion_event)
            self._state.base_state.event_log.append(expansion_event)
            self._emit_surface_supersession_for_topology_event(expansion_event)

            if bool(modes.get("causal_refinement_packet_transport_allowed", False)):
                post_signature = build_lgrc9v3_packet_ledger(
                    state=self._state.base_state
                ).fixed_topology_signature
                transport = transport_lgrc9v3_packets_through_refinement(
                    ledger_before,
                    expansion_event,
                    post_topology_signature=post_signature,
                )
                self._state.packet_ledger = with_ordered_lgrc9v3_event_queue(
                    transport.transported_ledger
                )
                transport_event = self._event_from_artifact(
                    kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
                    artifact=transport.to_artifact(),
                )
                events.append(transport_event)
                self._state.topology_event_log.append(transport_event)
                self._emit_surface_supersession_for_topology_event(transport_event)

            if bool(modes.get("causal_proper_time_inheritance_allowed", False)):
                inheritance = process_lgrc9v3_proper_time_inheritance(
                    expansion_event,
                    parent_node_proper_time=parent_time_surface,
                    tau_0=1.0,
                    scheduler_event_index=int(self._state.scheduler_event_index),
                    checkpoint_index=int(self._state.checkpoint_index),
                    event_time_key=float(self._state.event_time_key),
                )
                for child_node_id, child_time in inheritance.child_proper_time.items():
                    self._state.node_proper_time[int(child_node_id)] = float(child_time)
                    self._state.node_last_update_proper_time[int(child_node_id)] = float(
                        child_time
                    )
                    self._state.node_last_update_event_time_key[int(child_node_id)] = float(
                        self._state.event_time_key
                    )
                    self._state.lapse[int(child_node_id)] = float(
                        self._state.lapse.get(candidate_node_id, 1.0)
                    )
                for edge_id, delay in inheritance.internal_edge_delay.items():
                    self._state.edge_causal_delay[int(edge_id)] = float(delay)
                    self._state.base_state.temporal_delay[int(edge_id)] = float(delay)
                inheritance_event = self._event_from_artifact(
                    kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
                    artifact=inheritance.to_artifact(),
                )
                events.append(inheritance_event)
                self._state.topology_event_log.append(inheritance_event)
                self._emit_surface_supersession_for_topology_event(inheritance_event)

            stabilization_evidence = evaluate_child_basin_stabilization(
                self._state.base_state,
                expansion_event,
            )
            completed_event = register_completed_hybrid_spark(
                self._state.base_state,
                candidate_event,
                expansion_event,
                stabilization_evidence,
                source_family=self.MODEL_FAMILY,
            )
            if completed_event is not None:
                completed_event.payload.update(
                    {
                        "runtime_family": self.MODEL_FAMILY,
                        "scheduler_event_index": int(
                            self._state.scheduler_event_index
                        ),
                        "checkpoint_index": int(self._state.checkpoint_index),
                        "event_time_key": float(self._state.event_time_key),
                        "identity_acceptance_emitted": False,
                    }
                )
                events.append(completed_event)

            self.invalidate_causal_spark_diagnostics(
                reason="causal_topology_integration"
            )

        return events

    def evaluate_causal_spark_diagnostics(
        self,
        *,
        trigger_kind: str = "explicit_diagnostic_event",
        trigger_event_id: str | None = None,
        trigger_source: str = "explicit_api_call",
        trigger_node_id: int | None = None,
    ) -> list[GRCEvent]:
        """Explicitly evaluate causally scheduled Lane A/Lane B spark diagnostics."""

        events = self._evaluate_causal_spark_diagnostics(
            trigger_kind=trigger_kind,
            trigger_event_id=trigger_event_id,
            trigger_source=trigger_source,
            trigger_node_id=trigger_node_id,
        )
        self._state.event_log.extend(events)
        self._state.observables = dict(self.compute_observables())
        return events

    def process_causal_collapse_reabsorption(
        self,
        *,
        topology_event_kind: str,
        competing_sink_ids: Sequence[int],
        selected_sink_id: int,
        losing_sink_ids: Sequence[int],
        transferred_node_ids: Sequence[int],
        lineage_transfer_map: Mapping[int, str],
        source_lineage_ids: Mapping[int, str],
        target_lineage_id: str,
        coherence_transfer_amount: float,
        native_route_arbitration_record_id: str | None = None,
        native_route_arbitration_digest: str | None = None,
        native_route_selected_candidate_route_id: str | None = None,
        native_route_selected_candidate_route_digest: str | None = None,
        native_route_candidate_set_digest: str | None = None,
    ) -> list[GRCEvent]:
        """Route explicit collapse/reabsorption evidence through runtime logs."""

        if not bool(self._state.causal_modes.get("causal_topology_integration_allowed", False)):
            raise InvalidStateTransitionError(
                "collapse/reabsorption requires active topology integration"
            )
        if not bool(self._state.causal_modes.get("causal_collapse_reabsorption_allowed", False)):
            raise InvalidParamsError(
                "collapse/reabsorption requires explicit policy enablement"
            )
        ledger = self._state.packet_ledger
        assert ledger is not None
        if native_route_arbitration_record_id is not None:
            arbitration = self._native_route_arbitration_record_for_reference(
                native_route_arbitration_record_id
            )
            if arbitration is None:
                raise InvalidStateTransitionError(
                    "selected topology event arbitration record mismatch"
                )
            if (
                native_route_arbitration_digest is not None
                and native_route_arbitration_digest
                != arbitration.native_route_arbitration_digest
            ):
                raise InvalidStateTransitionError(
                    "selected topology event arbitration digest mismatch"
                )
            if (
                native_route_selected_candidate_route_id is not None
                and native_route_selected_candidate_route_id
                != arbitration.selected_candidate_route_id
            ):
                raise InvalidStateTransitionError(
                    "selected topology event candidate id mismatch"
                )
            if (
                native_route_selected_candidate_route_digest is not None
                and native_route_selected_candidate_route_digest
                != arbitration.selected_candidate_route_digest
            ):
                raise InvalidStateTransitionError(
                    "selected topology event candidate digest mismatch"
                )
            if (
                native_route_candidate_set_digest is not None
                and native_route_candidate_set_digest != arbitration.candidate_set_digest
            ):
                raise InvalidStateTransitionError(
                    "selected topology event candidate set mismatch"
                )
        budget = self._runtime_budget_surface()
        result = process_lgrc9v3_collapse_reabsorption(
            topology_event_kind=topology_event_kind,
            competing_sink_ids=competing_sink_ids,
            selected_sink_id=selected_sink_id,
            losing_sink_ids=losing_sink_ids,
            transferred_node_ids=transferred_node_ids,
            lineage_transfer_map=lineage_transfer_map,
            source_lineage_ids=source_lineage_ids,
            target_lineage_id=target_lineage_id,
            node_proper_time=self._state.node_proper_time,
            coherence_transfer_amount=coherence_transfer_amount,
            budget_before=budget,
            event_time_key=float(self._state.event_time_key),
            scheduler_event_index=int(self._state.scheduler_event_index),
            checkpoint_index=int(self._state.checkpoint_index),
            packet_ledger=ledger,
            budget_after=budget,
            collapse_reabsorption_allowed=True,
            native_route_arbitration_record_id=native_route_arbitration_record_id,
            native_route_arbitration_digest=native_route_arbitration_digest,
            native_route_selected_candidate_route_id=(
                native_route_selected_candidate_route_id
            ),
            native_route_selected_candidate_route_digest=(
                native_route_selected_candidate_route_digest
            ),
            native_route_candidate_set_digest=native_route_candidate_set_digest,
        )
        event = self._event_from_artifact(
            kind=topology_event_kind,
            artifact=result.to_artifact(),
        )
        self._state.topology_event_log.append(event)
        self._state.event_log.append(event)
        self._emit_surface_supersession_for_topology_event(event)
        if ledger.packet_records:
            topology_state_reabsorption_enabled = (
                self._topology_state_reabsorption_enabled()
            )
            node_state_before: dict[int, float] = {}
            active_state_digest_before = ""
            edge_state_before: dict[int, dict[int, float]] = {}
            if topology_state_reabsorption_enabled:
                node_state_before = self._active_node_state_map()
                active_state_digest_before = self._active_state_digest()
                source_nodes = tuple(
                    int(node_id) for node_id in result.transferred_node_ids
                )
                target_nodes = (int(result.selected_sink_id),)
                retired_nodes = tuple(int(node_id) for node_id in result.losing_sink_ids)
                edge_state_before = self._edge_state_map_for_edges(
                    tuple(
                        sorted(
                            set(self._incident_edge_ids_for_nodes(source_nodes))
                            | set(self._incident_edge_ids_for_nodes(target_nodes))
                            | set(self._incident_edge_ids_for_nodes(retired_nodes))
                        )
                    )
                )
            transport = transport_lgrc9v3_packets_through_collapse_reabsorption(
                ledger,
                result,
            )
            self._state.packet_ledger = with_ordered_lgrc9v3_event_queue(
                transport.transported_ledger
            )
            transport_event = self._event_from_artifact(
                kind=transport.source_topology_event_kind,
                artifact=transport.to_artifact(),
            )
            self._state.topology_event_log.append(transport_event)
            self._state.event_log.append(transport_event)
            self._emit_surface_supersession_for_topology_event(transport_event)
            if topology_state_reabsorption_enabled:
                self._apply_collapse_topology_state_reabsorption(
                    topology_event=event,
                    collapse_result=result,
                    transport_result=transport,
                    packet_ledger_before=ledger,
                    packet_ledger_after=self._state.packet_ledger,
                    node_state_before=node_state_before,
                    edge_state_before=edge_state_before,
                    active_state_digest_before=active_state_digest_before,
                )
            self._state.observables = dict(self.compute_observables())
            return [event, transport_event]
        self._state.observables = dict(self.compute_observables())
        return [event]

    def emit_causal_identity_acceptance(
        self,
        evaluation: object,
    ) -> GRCEvent:
        """Emit identity acceptance only after a passing proper-time evaluation."""

        if not bool(self._state.causal_modes.get("causal_topology_integration_allowed", False)):
            raise InvalidStateTransitionError(
                "identity acceptance requires active topology integration"
            )
        if not bool(self._state.causal_modes.get("causal_identity_acceptance_allowed", False)):
            raise InvalidParamsError(
                "identity acceptance requires explicit policy enablement"
            )
        budget = self._runtime_budget_surface()
        event = emit_lgrc9v3_proper_time_identity_acceptance(
            evaluation,  # type: ignore[arg-type]
            identity_acceptance_allowed=True,
            scheduler_event_index=int(self._state.scheduler_event_index),
            checkpoint_index=int(self._state.checkpoint_index),
            event_time_key=float(self._state.event_time_key),
            budget_before=budget,
            budget_after=budget,
        )
        self._state.topology_event_log.append(event)
        self._state.event_log.append(event)
        self._state.observables = dict(self.compute_observables())
        return event

    def step(self) -> StepResult:
        """Process one deterministic LGRC9V3 queue event."""

        ledger = self._state.packet_ledger
        assert ledger is not None
        ordered_ledger = with_ordered_lgrc9v3_event_queue(ledger)
        self._state.packet_ledger = ordered_ledger
        queue_length_before = len(ordered_ledger.event_queue_records)
        birth_queue_length_before = len(self._state.boundary_birth_trial_queue)
        next_packet_event = (
            None if queue_length_before == 0 else ordered_ledger.event_queue_records[0]
        )
        next_birth_trial = (
            None
            if birth_queue_length_before == 0
            else self._state.boundary_birth_trial_queue[0]
        )
        if next_packet_event is None and next_birth_trial is None:
            observables = self.compute_observables()
            return StepResult(
                step_index=int(self._state.scheduler_event_index),
                time=float(self._state.event_time_key),
                events=[],
                observables=observables,
                bookkeeping={
                    "stop_condition": "event_queue_empty",
                    "scheduler_event_index": self._state.scheduler_event_index,
                    "checkpoint_index": self._state.checkpoint_index,
                    "event_time_key": self._state.event_time_key,
                    "queue_length_before": 0,
                    "queue_length_after": 0,
                    "boundary_birth_trial_queue_before": 0,
                    "boundary_birth_trial_queue_after": 0,
                    "topology_events_routed": 0,
                    "local_update_eligibility_events": 0,
                },
            )
        process_birth_trial = False
        if next_birth_trial is not None:
            if next_packet_event is None:
                process_birth_trial = True
            else:
                process_birth_trial = (
                    float(next_birth_trial["event_time_key"]),
                    int(next_birth_trial["scheduler_event_index"]),
                    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND,
                ) <= (
                    float(next_packet_event.event_time_key),
                    int(next_packet_event.scheduler_event_index),
                    str(next_packet_event.event_kind),
                )
        if process_birth_trial:
            trial = self._state.boundary_birth_trial_queue.pop(0)
            events = self.apply_causal_boundary_birth_trial(
                parent_node_id=int(trial["parent_node_id"]),
                parent_port_id=trial.get("parent_port_id"),
                outward_flux_pressure=trial.get("outward_flux_pressure"),
                event_time_key=float(trial["event_time_key"]),
                scheduler_event_index=int(trial["scheduler_event_index"]),
                rng_sample=trial.get("rng_sample"),
                edge_delay=trial.get("edge_delay"),
                tau_0=float(trial.get("tau_0", 1.0)),
            )
            if not events:
                self._state.scheduler_event_index = int(trial["scheduler_event_index"])
                self._state.event_time_key = float(trial["event_time_key"])
                self._state.checkpoint_index += 1
                self._state.step_index = int(self._state.scheduler_event_index)
                self._state.time = float(self._state.event_time_key)
            observables = self.compute_observables()
            self._state.observables = dict(observables)
            return StepResult(
                step_index=int(self._state.scheduler_event_index),
                time=float(self._state.event_time_key),
                events=events,
                observables=observables,
                bookkeeping={
                    "step_order": (
                        "order_event_queue",
                        "process_causal_boundary_birth_trial",
                        "checkpoint_runtime_state",
                    ),
                    "processed_event_id": None
                    if not events
                    else events[0].payload.get("causal_boundary_birth_event_id"),
                    "processed_event_kind": "lgrc9v3_causal_boundary_birth_trial",
                    "scheduler_event_index": self._state.scheduler_event_index,
                    "checkpoint_index": self._state.checkpoint_index,
                    "event_time_key": self._state.event_time_key,
                    "queue_length_before": queue_length_before,
                    "queue_length_after": len(
                        self._state.packet_ledger.event_queue_records  # type: ignore[union-attr]
                    ),
                    "boundary_birth_trial_queue_before": birth_queue_length_before,
                    "boundary_birth_trial_queue_after": len(
                        self._state.boundary_birth_trial_queue
                    ),
                    "topology_events_routed": len(events),
                    "local_update_eligibility_events": 0,
                    "local_update_events": 0,
                    "causal_spark_diagnostic_events": 0,
                    "causal_topology_integration_events": 0,
                    "packetized_flux_applied": False,
                    "causal_flux_events_processed": 0,
                },
            )

        result = process_lgrc9v3_next_packet_event(
            self._state.base_state,
            ordered_ledger,
        )
        self._state.packet_ledger = with_ordered_lgrc9v3_event_queue(result.ledger)
        processed_event = result.processed_event
        self._state.scheduler_event_index = int(processed_event.scheduler_event_index)
        self._state.event_time_key = float(processed_event.event_time_key)
        self._state.checkpoint_index += 1
        self._state.step_index = int(self._state.scheduler_event_index)
        self._state.time = float(self._state.event_time_key)
        local_clock_node_id = (
            processed_event.target_node_id
            if processed_event.event_kind == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL
            else processed_event.source_node_id
        )
        proper_time_update = (
            None
            if local_clock_node_id is None
            else self._advance_node_proper_time(
                node_id=int(local_clock_node_id),
                event_time_key=float(processed_event.event_time_key),
            )
        )
        self._state.packet_processing_log.append(result)

        events = [
            self._packet_processing_event(
                result,
                proper_time_update=proper_time_update,
            )
        ]
        surface_event = self._emit_causal_pulse_substrate_surface_event(result)
        if surface_event is not None:
            events.append(surface_event)
        events.extend(
            self._complete_self_rearm_evidence_for_departure(
                processed_event=processed_event,
                processing_result=result,
            )
        )
        local_update_eligibility_events = 0
        local_update_events = 0
        if processed_event.event_kind == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL:
            eligibility = derive_lgrc9v3_packet_arrival_eligibility(result)
            self._state.arrival_eligibility_log.append(eligibility)
            events.append(
                GRCEvent(
                    kind=LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
                    step_index=int(processed_event.scheduler_event_index),
                    payload=eligibility.to_artifact(),
                    source_family=self.MODEL_FAMILY,
                )
            )
            local_update_eligibility_events = 1
            events.append(
                self._apply_arrival_local_update(
                    eligibility=eligibility,
                    proper_time_update={}
                    if proper_time_update is None
                    else proper_time_update,
                )
            )
            local_update_events = 1
            local_update_event = events[-1]
            causal_spark_events = self._evaluate_causal_spark_diagnostics(
                trigger_kind=LGRC9V3_LOCAL_UPDATE_EVENT_KIND,
                trigger_event_id=str(
                    local_update_event.payload.get("local_update_event_id")
                ),
                trigger_source="arrival_local_update_completion",
                trigger_node_id=int(processed_event.target_node_id),
            )
            events.extend(causal_spark_events)
            topology_events = self._apply_causal_topology_integration(
                causal_spark_events
            )
            events.extend(topology_events)

        self._state.event_log.extend(events)
        observables = self.compute_observables()
        self._state.observables = dict(observables)
        causal_topology_integration_events = len(
            [
                event
                for event in events
                if event.kind
                in {
                    "hybrid_mechanical_expansion",
                    LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
                    LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
                }
            ]
        )
        return StepResult(
            step_index=int(self._state.scheduler_event_index),
            time=float(self._state.event_time_key),
            events=events,
            observables=observables,
            bookkeeping={
                "step_order": (
                    "order_event_queue",
                    "process_packet_event",
                    "emit_causal_pulse_substrate_surface_row",
                    "route_arrival_eligibility",
                    "apply_packetized_local_update",
                    "evaluate_causal_spark_diagnostics",
                    "checkpoint_runtime_state",
                ),
                "processed_event_id": processed_event.event_id,
                "processed_event_kind": processed_event.event_kind,
                "scheduler_event_index": self._state.scheduler_event_index,
                "checkpoint_index": self._state.checkpoint_index,
                "event_time_key": self._state.event_time_key,
                "queue_length_before": queue_length_before,
                "queue_length_after": len(
                    self._state.packet_ledger.event_queue_records  # type: ignore[union-attr]
                ),
                "boundary_birth_trial_queue_before": birth_queue_length_before,
                "boundary_birth_trial_queue_after": len(
                    self._state.boundary_birth_trial_queue
                ),
                "topology_events_routed": causal_topology_integration_events,
                "local_update_eligibility_events": local_update_eligibility_events,
                "local_update_events": local_update_events,
                "causal_pulse_substrate_surface_rows": 0
                if surface_event is None
                else 1,
                "causal_spark_diagnostic_events": sum(
                    1
                    for event in events
                    if event.kind == LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND
                ),
                "causal_spark_evaluation_index": (
                    self._state.causal_spark_evaluation_index
                ),
                "causal_topology_integration_events": (
                    causal_topology_integration_events
                ),
                "delayed_evaluation_applied": False,
                "packetized_flux_applied": True,
                "causal_flux_events_processed": 1,
            },
        )

    def run_event_queue(self, *, max_events: int) -> list[StepResult]:
        """Process queued packet or topology-trial events until bounded."""

        if int(max_events) < 0:
            raise ValueError("max_events must be >= 0")
        results: list[StepResult] = []
        for _ in range(int(max_events)):
            ledger = self._state.packet_ledger
            assert ledger is not None
            if (
                not ledger.event_queue_records
                and not self._state.boundary_birth_trial_queue
            ):
                break
            results.append(self.step())
        return results

    def _queue_has_work(self) -> bool:
        ledger = self._state.packet_ledger
        assert ledger is not None
        return bool(ledger.event_queue_records) or bool(
            self._state.boundary_birth_trial_queue
        )

    def _autonomous_run_summary(
        self,
        *,
        run_policy: str,
        producer_policies: Sequence[str],
        production_results: Sequence[LGRC9V3AutonomousProductionResult],
        consumed_results: Sequence[StepResult],
        stop_condition: str,
        max_events: int,
    ) -> dict[str, Any]:
        return {
            "run_policy": str(run_policy),
            "producer_policies": [str(policy) for policy in producer_policies],
            "max_events": int(max_events),
            "producer_invocation_count": len(production_results),
            "producer_scheduled_event_count": sum(
                int(result.scheduled_event_count) for result in production_results
            ),
            "producer_state_mutation_count": sum(
                1 for result in production_results if result.state_mutated
            ),
            "producer_idempotent_skip_count": sum(
                1
                for result in production_results
                for record in result.production_records
                if record.reason_code
                == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP
            ),
            "producer_no_eligible_work_count": sum(
                1
                for result in production_results
                for record in result.production_records
                if record.reason_code
                == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK
            ),
            "consumed_step_count": len(consumed_results),
            "consumed_event_count": sum(
                len(result.events) for result in consumed_results
            ),
            "stop_condition": str(stop_condition),
            "queue_has_work_after": self._queue_has_work(),
            "scheduler_event_index": int(self._state.scheduler_event_index),
            "checkpoint_index": int(self._state.checkpoint_index),
            "event_time_key": float(self._state.event_time_key),
            "production_results": [
                result.to_artifact() for result in production_results
            ],
        }

    def run_autonomous(
        self,
        *,
        max_events: int,
        policy: str = LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1,
        producer_policies: Sequence[str] | None = None,
    ) -> list[StepResult]:
        """Run a bounded producer-plus-executor loop.

        Producers only enqueue work. This method consumes work exclusively
        through ``step()`` and records the producer/consumer summary in
        returned step bookkeeping and runtime cached quantities.
        """

        if int(max_events) < 0:
            raise ValueError("max_events must be >= 0")
        if policy != LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1:
            raise InvalidParamsError(
                "autonomous run policy must be "
                f"{LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1!r}"
            )
        resolved_producer_policies = tuple(
            producer_policies
            if producer_policies is not None
            else (
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
            )
        )
        for producer_policy in resolved_producer_policies:
            validate_lgrc9v3_autonomous_producer_policy(str(producer_policy))

        results: list[StepResult] = []
        production_results: list[LGRC9V3AutonomousProductionResult] = []
        stop_condition = "max_events_reached" if int(max_events) == 0 else ""

        for _ in range(int(max_events)):
            if not self._queue_has_work():
                scheduled_before = sum(
                    result.scheduled_event_count for result in production_results
                )
                for producer_policy in resolved_producer_policies:
                    production_results.append(
                        self.produce_events(policy=str(producer_policy))
                    )
                scheduled_after = sum(
                    result.scheduled_event_count for result in production_results
                )
                if scheduled_after == scheduled_before and not self._queue_has_work():
                    stop_condition = "no_autonomous_work_available"
                    break
            if not self._queue_has_work():
                stop_condition = "event_queue_empty"
                break
            step_result = self.step()
            if not step_result.events and (
                step_result.bookkeeping.get("stop_condition") == "event_queue_empty"
            ):
                stop_condition = "event_queue_empty"
                break
            results.append(step_result)
        else:
            stop_condition = "max_events_reached"

        if not stop_condition:
            stop_condition = (
                "queue_drained"
                if not self._queue_has_work()
                else "max_events_reached"
            )
        summary = self._autonomous_run_summary(
            run_policy=policy,
            producer_policies=resolved_producer_policies,
            production_results=production_results,
            consumed_results=results,
            stop_condition=stop_condition,
            max_events=int(max_events),
        )
        self._state.cached_quantities["last_lgrc9v3_autonomous_run"] = dict(summary)
        for result in results:
            result.bookkeeping["autonomous_run"] = dict(summary)
        return results

    def reset(self) -> None:
        self._state = deepcopy(self._initial_state)

    def snapshot(self) -> dict[str, Any]:
        base_snapshot = GRC9V3.from_state(
            self._state.base_state,
            self._params.raw_config,
        ).snapshot()
        return build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family=self.MODEL_FAMILY,
                step_index=self._state.scheduler_event_index,
                params=dict(self._params.raw_config),
                resolved_params=dict(self._params.resolved_config),
                params_hash=self._params.params_hash,
                capabilities=self.list_capabilities(),
            ),
            topology=base_snapshot["topology"],
            basin_attributes=base_snapshot.get("basin_attributes"),
            edge_labels=base_snapshot.get("edge_labels"),
            dynamics={
                "base_grc9v3_model_family": "GRC9V3",
                "lgrc9v3_runtime": self._state.to_artifact(),
            },
            observables=dict(self.compute_observables()),
            events=[
                {
                    "kind": event.kind,
                    "step_index": event.step_index,
                    "payload": dict(event.payload),
                    "source_family": event.source_family,
                }
                for event in self._state.event_log
            ],
            caches={"base_grc9v3_snapshot": base_snapshot},
        )

    def save(self, path: str) -> None:
        save_snapshot(path, self.snapshot())


__all__ = [
    "LGRC9V3",
    "LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND",
    "LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_SCHEMA_VERSION",
    "LGRC9V3_CAUSAL_SPARK_DIAGNOSTIC_SOURCE",
    "LGRC9V3_LOCAL_UPDATE_EVENT_KIND",
    "LGRC9V3_LOCAL_UPDATE_EVENT_SCHEMA_VERSION",
    "LGRC9V3_RUNTIME_EVENT_SCHEMA_VERSION",
    "LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY",
    "LGRC9V3_PULSE_SUBSTRATE_COUPLING_CONFIG_KEY",
    "LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND",
    "LGRC9V3_SELF_REARM_EVIDENCE_EVENT_SCHEMA_VERSION",
    "validate_lgrc9v3_causal_pulse_substrate_surface_artifacts",
    "validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts",
    "validate_lgrc9v3_self_rearm_evidence_artifacts",
]
