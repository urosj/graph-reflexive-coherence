"""Composed runtime state for executable LGRC9V3 queue orchestration."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import math
from typing import Any

from pygrc.core import GRCEvent, GRCState, NodeId, SnapshotCompatibilityError

from .grc_9_v3_state import GRC9V3State
from .lgrc_9_v3_contract import (
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LGRC_RUNTIME_LEVEL_LGRC2,
    LGRC9V3_LGRC2_MODE_VERSION,
    LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_KIND,
    LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_SCHEMA_VERSION,
    LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY,
    LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_EVIDENCE_CLASS,
    LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
    LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_SCHEMA_VERSION,
    LGRC9V3_PACKETIZED_EVIDENCE_CLASS,
    LGRC9V3CausalPulseSubstrateSurfaceLineageRecord,
    LGRC9V3CausalPulseSubstrateSurfaceRow,
    LGRC9V3NativeRouteArbitrationRecord,
    LGRC9V3NativeRouteCandidateRecord,
    LGRC9V3NativeRouteCandidateSetRecord,
    LGRC9V3TopologyStateReabsorptionRecord,
    restore_lgrc9v3_causal_pulse_substrate_surface_lineage_record_artifact,
    restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact,
    restore_lgrc9v3_native_route_arbitration_record_artifact,
    restore_lgrc9v3_native_route_candidate_record_artifact,
    restore_lgrc9v3_native_route_candidate_set_record_artifact,
    restore_lgrc9v3_topology_state_reabsorption_record_artifact,
)
from .lgrc_9_v3_packets import (
    LGRC9V3PacketArrivalEligibility,
    LGRC9V3PacketLedger,
    LGRC9V3PacketProcessingResult,
    LGRC9V3PacketQueueEventRecord,
    build_lgrc9v3_packet_ledger,
    restore_lgrc9v3_packet_ledger_artifact,
    restore_lgrc9v3_packet_queue_event_record,
    restore_lgrc9v3_packet_record,
)


LGRC9V3_RUNTIME_STATE_KIND = "lgrc9v3_runtime_state"
LGRC9V3_RUNTIME_STATE_SCHEMA_VERSION = "lgrc9v3_runtime_state_v1"


def ordered_lgrc9v3_event_queue(
    records: tuple[LGRC9V3PacketQueueEventRecord, ...],
) -> tuple[LGRC9V3PacketQueueEventRecord, ...]:
    """Return deterministic LGRC9V3 event-queue order."""

    return tuple(
        sorted(
            records,
            key=lambda event: (
                float(event.event_time_key),
                int(event.scheduler_event_index),
                str(event.event_kind),
                str(event.event_id),
            ),
        )
    )


def with_ordered_lgrc9v3_event_queue(
    ledger: LGRC9V3PacketLedger,
) -> LGRC9V3PacketLedger:
    """Return a ledger copy whose queued events obey the tie-break policy."""

    return LGRC9V3PacketLedger(
        packet_records=ledger.packet_records,
        packet_event_records=ledger.packet_event_records,
        event_queue_records=ordered_lgrc9v3_event_queue(ledger.event_queue_records),
        node_coherence_total=ledger.node_coherence_total,
        in_flight_packet_total=ledger.in_flight_packet_total,
        conserved_budget_total=ledger.conserved_budget_total,
        budget_before=ledger.budget_before,
        budget_after=ledger.budget_after,
        budget_error=ledger.budget_error,
        fixed_topology_signature=dict(ledger.fixed_topology_signature),
        policies=dict(ledger.policies),
        event_queue_tie_break_policy=ledger.event_queue_tie_break_policy,
        packet_budget_invariant=ledger.packet_budget_invariant,
        causal_layer_mode=ledger.causal_layer_mode,
        lgrc_runtime_level=ledger.lgrc_runtime_level,
        evidence_class=ledger.evidence_class,
        packetized_flux=ledger.packetized_flux,
        fixed_topology=ledger.fixed_topology,
        topology_change_allowed=ledger.topology_change_allowed,
        packet_transport_through_topology_change=(
            ledger.packet_transport_through_topology_change
        ),
        identity_acceptance_allowed=ledger.identity_acceptance_allowed,
        collapse_allowed=ledger.collapse_allowed,
    )


def _string_keyed_float_map(values: dict[int, float]) -> dict[str, float]:
    return {str(int(key)): float(value) for key, value in sorted(values.items())}


def _string_keyed_route_map(
    values: dict[int, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    return {
        str(int(key)): [dict(route) for route in routes]
        for key, routes in sorted(values.items())
    }


def _artifact_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return value


def _artifact_sequence(value: Any, *, context: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise SnapshotCompatibilityError(f"{context} must be a list")
    return value


def _artifact_string(value: Any, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise SnapshotCompatibilityError(f"{context} must be a non-empty string")
    return value


def _artifact_int(value: Any, *, context: str) -> int:
    if isinstance(value, bool):
        raise SnapshotCompatibilityError(f"{context} must be an integer")
    try:
        resolved = int(value)
    except (TypeError, ValueError) as exc:
        raise SnapshotCompatibilityError(f"{context} must be an integer") from exc
    return resolved


def _artifact_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool):
        raise SnapshotCompatibilityError(f"{context} must be finite")
    try:
        resolved = float(value)
    except (TypeError, ValueError) as exc:
        raise SnapshotCompatibilityError(f"{context} must be finite") from exc
    if not math.isfinite(resolved):
        raise SnapshotCompatibilityError(f"{context} must be finite")
    return resolved


def _artifact_bool(value: Any, *, context: str) -> bool:
    if not isinstance(value, bool):
        raise SnapshotCompatibilityError(f"{context} must be boolean")
    return value


def _restore_int_float_map(value: Any, *, context: str) -> dict[int, float]:
    mapping = _artifact_mapping(value, context=context)
    return {
        _artifact_int(key, context=f"{context}.key"): _artifact_float(
            raw_value,
            context=f"{context}[{key!r}]",
        )
        for key, raw_value in mapping.items()
    }


def _restore_route_map(value: Any, *, context: str) -> dict[int, list[dict[str, Any]]]:
    mapping = _artifact_mapping(value, context=context)
    routes_by_node: dict[int, list[dict[str, Any]]] = {}
    for key, routes in mapping.items():
        route_records = _artifact_sequence(routes, context=f"{context}[{key!r}]")
        routes_by_node[_artifact_int(key, context=f"{context}.key")] = [
            dict(_artifact_mapping(route, context=f"{context}[{key!r}].route"))
            for route in route_records
        ]
    return routes_by_node


def restore_lgrc9v3_event_record(record: Mapping[str, Any]) -> GRCEvent:
    """Restore one JSON-compatible event record into ``GRCEvent``."""

    mapping = _artifact_mapping(record, context="event_record")
    payload = _artifact_mapping(mapping.get("payload", {}), context="event.payload")
    return GRCEvent(
        kind=_artifact_string(mapping.get("kind"), context="event.kind"),
        step_index=_artifact_int(mapping.get("step_index"), context="event.step_index"),
        payload=dict(payload),
        source_family=None
        if mapping.get("source_family") is None
        else _artifact_string(
            mapping.get("source_family"),
            context="event.source_family",
        ),
    )


def _restore_packet_processing_result(
    record: Mapping[str, Any],
) -> LGRC9V3PacketProcessingResult:
    mapping = _artifact_mapping(record, context="packet_processing_result")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_KIND
    ):
        raise SnapshotCompatibilityError("unsupported packet processing result kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported packet processing result schema version"
        )
    ledger = restore_lgrc9v3_packet_ledger_artifact(
        _artifact_mapping(mapping.get("ledger"), context="packet_processing.ledger")
    )
    if ledger is None:
        raise SnapshotCompatibilityError(
            "packet_processing.ledger must be an LGRC9V3 packet ledger"
        )
    return LGRC9V3PacketProcessingResult(
        ledger=ledger,
        processed_event=restore_lgrc9v3_packet_queue_event_record(
            _artifact_mapping(
                mapping.get("processed_event"),
                context="packet_processing.processed_event",
            )
        ),
        packet_record=restore_lgrc9v3_packet_record(
            _artifact_mapping(
                mapping.get("packet_record"),
                context="packet_processing.packet_record",
            )
        ),
        budget_before=_artifact_float(
            mapping.get("budget_before"),
            context="budget_before",
        ),
        budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
        budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
        topology_signature=dict(
            _artifact_mapping(
                mapping.get("topology_signature", {}),
                context="topology_signature",
            )
        ),
        state_mutated=_artifact_bool(
            mapping.get("state_mutated"),
            context="state_mutated",
        ),
        topology_mutated=_artifact_bool(
            mapping.get("topology_mutated"),
            context="topology_mutated",
        ),
        spark_event_emitted=_artifact_bool(
            mapping.get("spark_event_emitted"),
            context="spark_event_emitted",
        ),
        mechanical_expansion_emitted=_artifact_bool(
            mapping.get("mechanical_expansion_emitted"),
            context="mechanical_expansion_emitted",
        ),
        identity_acceptance_emitted=_artifact_bool(
            mapping.get("identity_acceptance_emitted"),
            context="identity_acceptance_emitted",
        ),
    )


def _restore_arrival_eligibility(
    record: Mapping[str, Any],
) -> LGRC9V3PacketArrivalEligibility:
    mapping = _artifact_mapping(record, context="arrival_eligibility")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND
    ):
        raise SnapshotCompatibilityError("unsupported arrival eligibility kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported arrival eligibility schema version"
        )
    return LGRC9V3PacketArrivalEligibility(
        packet_id=_artifact_string(mapping.get("packet_id"), context="packet_id"),
        arrival_event_id=_artifact_string(
            mapping.get("arrival_event_id"),
            context="arrival_event_id",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        source_node_id=_artifact_int(
            mapping.get("source_node_id"),
            context="source_node_id",
        ),
        target_node_id=_artifact_int(
            mapping.get("target_node_id"),
            context="target_node_id",
        ),
        edge_id=_artifact_int(mapping.get("edge_id"), context="edge_id"),
        amount=_artifact_float(mapping.get("amount"), context="amount"),
        topology_signature=dict(
            _artifact_mapping(
                mapping.get("topology_signature", {}),
                context="topology_signature",
            )
        ),
        local_update_eligible=_artifact_bool(
            mapping.get("local_update_eligible"),
            context="local_update_eligible",
        ),
        spark_diagnostic_eligible=_artifact_bool(
            mapping.get("spark_diagnostic_eligible"),
            context="spark_diagnostic_eligible",
        ),
        spark_event_emitted=_artifact_bool(
            mapping.get("spark_event_emitted"),
            context="spark_event_emitted",
        ),
        mechanical_expansion_emitted=_artifact_bool(
            mapping.get("mechanical_expansion_emitted"),
            context="mechanical_expansion_emitted",
        ),
        identity_acceptance_emitted=_artifact_bool(
            mapping.get("identity_acceptance_emitted"),
            context="identity_acceptance_emitted",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        evidence_class=_artifact_string(
            mapping.get("evidence_class", LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_EVIDENCE_CLASS),
            context="evidence_class",
        ),
    )


def restore_lgrc9v3_runtime_state_artifact(
    artifact: Mapping[str, Any],
    *,
    base_state: GRC9V3State,
) -> LGRC9V3RuntimeState:
    """Restore an executable LGRC9V3 runtime state from snapshot dynamics."""

    mapping = _artifact_mapping(artifact, context="lgrc9v3_runtime")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_RUNTIME_STATE_KIND
    ):
        raise SnapshotCompatibilityError("unsupported LGRC9V3 runtime artifact kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_RUNTIME_STATE_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported LGRC9V3 runtime artifact schema version"
        )
    ledger = restore_lgrc9v3_packet_ledger_artifact(
        _artifact_mapping(mapping.get("packet_ledger"), context="packet_ledger")
    )
    if ledger is None:
        raise SnapshotCompatibilityError("packet_ledger must be an LGRC9V3 ledger")
    return LGRC9V3RuntimeState(
        base_state=base_state,
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        checkpoint_index=_artifact_int(
            mapping.get("checkpoint_index"),
            context="checkpoint_index",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        node_proper_time=_restore_int_float_map(
            mapping.get("node_proper_time", {}),
            context="node_proper_time",
        ),
        node_last_update_proper_time=_restore_int_float_map(
            mapping.get("node_last_update_proper_time", {}),
            context="node_last_update_proper_time",
        ),
        node_last_update_event_time_key=_restore_int_float_map(
            mapping.get("node_last_update_event_time_key", {}),
            context="node_last_update_event_time_key",
        ),
        edge_causal_delay=_restore_int_float_map(
            mapping.get("edge_causal_delay", {}),
            context="edge_causal_delay",
        ),
        lapse=_restore_int_float_map(mapping.get("lapse", {}), context="lapse"),
        packet_ledger=ledger,
        causal_flux_routes=_restore_route_map(
            mapping.get("causal_flux_routes", {}),
            context="causal_flux_routes",
        ),
        boundary_birth_trial_queue=[
            dict(_artifact_mapping(record, context="boundary_birth_trial_queue.record"))
            for record in _artifact_sequence(
                mapping.get("boundary_birth_trial_queue", []),
                context="boundary_birth_trial_queue",
            )
        ],
        topology_event_log=[
            restore_lgrc9v3_event_record(
                _artifact_mapping(record, context="topology_event_log.record")
            )
            for record in _artifact_sequence(
                mapping.get("topology_event_log", []),
                context="topology_event_log",
            )
        ],
        arrival_eligibility_log=[
            _restore_arrival_eligibility(
                _artifact_mapping(record, context="arrival_eligibility_log.record")
            )
            for record in _artifact_sequence(
                mapping.get("arrival_eligibility_log", []),
                context="arrival_eligibility_log",
            )
        ],
        local_update_log=[
            dict(_artifact_mapping(record, context="local_update_log.record"))
            for record in _artifact_sequence(
                mapping.get("local_update_log", []),
                context="local_update_log",
            )
        ],
        causal_spark_diagnostic_log=[
            dict(_artifact_mapping(record, context="causal_spark_diagnostic_log.record"))
            for record in _artifact_sequence(
                mapping.get("causal_spark_diagnostic_log", []),
                context="causal_spark_diagnostic_log",
            )
        ],
        causal_pulse_substrate_surface_log=[
            restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact(
                _artifact_mapping(
                    record,
                    context="causal_pulse_substrate_surface_log.record",
                )
            )
            for record in _artifact_sequence(
                mapping.get("causal_pulse_substrate_surface_log", []),
                context="causal_pulse_substrate_surface_log",
            )
        ],
        causal_pulse_substrate_surface_lineage_log=[
            restore_lgrc9v3_causal_pulse_substrate_surface_lineage_record_artifact(
                _artifact_mapping(
                    record,
                    context="causal_pulse_substrate_surface_lineage_log.record",
                )
            )
            for record in _artifact_sequence(
                mapping.get("causal_pulse_substrate_surface_lineage_log", []),
                context="causal_pulse_substrate_surface_lineage_log",
            )
        ],
        topology_state_reabsorption_log=[
            restore_lgrc9v3_topology_state_reabsorption_record_artifact(
                _artifact_mapping(
                    record,
                    context="topology_state_reabsorption_log.record",
                )
            )
            for record in _artifact_sequence(
                mapping.get("topology_state_reabsorption_log", []),
                context="topology_state_reabsorption_log",
            )
        ],
        native_route_candidate_log=[
            restore_lgrc9v3_native_route_candidate_record_artifact(
                _artifact_mapping(
                    record,
                    context="native_route_candidate_log.record",
                )
            )
            for record in _artifact_sequence(
                mapping.get("native_route_candidate_log", []),
                context="native_route_candidate_log",
            )
        ],
        native_route_candidate_set_log=[
            restore_lgrc9v3_native_route_candidate_set_record_artifact(
                _artifact_mapping(
                    record,
                    context="native_route_candidate_set_log.record",
                )
            )
            for record in _artifact_sequence(
                mapping.get("native_route_candidate_set_log", []),
                context="native_route_candidate_set_log",
            )
        ],
        native_route_arbitration_log=[
            restore_lgrc9v3_native_route_arbitration_record_artifact(
                _artifact_mapping(
                    record,
                    context="native_route_arbitration_log.record",
                )
            )
            for record in _artifact_sequence(
                mapping.get("native_route_arbitration_log", []),
                context="native_route_arbitration_log",
            )
        ],
        causal_spark_evaluation_index=_artifact_int(
            mapping.get("causal_spark_evaluation_index", 0),
            context="causal_spark_evaluation_index",
        ),
        packet_processing_log=[
            _restore_packet_processing_result(
                _artifact_mapping(record, context="packet_processing_log.record")
            )
            for record in _artifact_sequence(
                mapping.get("packet_processing_log", []),
                context="packet_processing_log",
            )
        ],
        cached_quantities=dict(
            _artifact_mapping(
                mapping.get("cached_quantities", {}),
                context="cached_quantities",
            )
        ),
        causal_modes=dict(
            _artifact_mapping(mapping.get("causal_modes", {}), context="causal_modes")
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        edge_delay_policy=_artifact_string(
            mapping.get("causal_modes", {}).get(
                "edge_delay_policy",
                EDGE_DELAY_POLICY_CONSTANT_DELAY,
            )
            if isinstance(mapping.get("causal_modes", {}), Mapping)
            else EDGE_DELAY_POLICY_CONSTANT_DELAY,
            context="edge_delay_policy",
        ),
        event_queue_tie_break_policy=_artifact_string(
            mapping.get("event_queue_tie_break_policy"),
            context="event_queue_tie_break_policy",
        ),
    )


@dataclass
class LGRC9V3RuntimeState(GRCState):
    """Executable LGRC9V3 state bundle composed over a GRC9V3 substrate."""

    base_state: GRC9V3State = field(default_factory=GRC9V3State)
    scheduler_event_index: int = 0
    checkpoint_index: int = 0
    event_time_key: float = 0.0
    node_proper_time: dict[NodeId, float] = field(default_factory=dict)
    node_last_update_proper_time: dict[NodeId, float] = field(default_factory=dict)
    node_last_update_event_time_key: dict[NodeId, float] = field(default_factory=dict)
    edge_causal_delay: dict[int, float] = field(default_factory=dict)
    lapse: dict[NodeId, float] = field(default_factory=dict)
    packet_ledger: LGRC9V3PacketLedger | None = None
    causal_flux_routes: dict[NodeId, list[dict[str, Any]]] = field(default_factory=dict)
    boundary_birth_trial_queue: list[dict[str, Any]] = field(default_factory=list)
    topology_event_log: list[GRCEvent | dict[str, Any]] = field(default_factory=list)
    arrival_eligibility_log: list[LGRC9V3PacketArrivalEligibility] = (
        field(default_factory=list)
    )
    local_update_log: list[dict[str, Any]] = field(default_factory=list)
    causal_spark_diagnostic_log: list[dict[str, Any]] = field(default_factory=list)
    causal_pulse_substrate_surface_log: list[LGRC9V3CausalPulseSubstrateSurfaceRow] = (
        field(default_factory=list)
    )
    causal_pulse_substrate_surface_lineage_log: list[
        LGRC9V3CausalPulseSubstrateSurfaceLineageRecord
    ] = field(default_factory=list)
    topology_state_reabsorption_log: list[
        LGRC9V3TopologyStateReabsorptionRecord
    ] = field(default_factory=list)
    native_route_candidate_log: list[LGRC9V3NativeRouteCandidateRecord] = (
        field(default_factory=list)
    )
    native_route_candidate_set_log: list[LGRC9V3NativeRouteCandidateSetRecord] = (
        field(default_factory=list)
    )
    native_route_arbitration_log: list[LGRC9V3NativeRouteArbitrationRecord] = (
        field(default_factory=list)
    )
    causal_spark_evaluation_index: int = 0
    packet_processing_log: list[LGRC9V3PacketProcessingResult] = (
        field(default_factory=list)
    )
    causal_modes: dict[str, Any] = field(default_factory=dict)
    causal_layer_mode: str = CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC2
    edge_delay_policy: str = EDGE_DELAY_POLICY_CONSTANT_DELAY
    event_queue_tie_break_policy: str = LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY

    def __post_init__(self) -> None:
        if self.packet_ledger is None:
            self.packet_ledger = build_lgrc9v3_packet_ledger(state=self.base_state)
        else:
            self.packet_ledger = with_ordered_lgrc9v3_event_queue(self.packet_ledger)
        self.step_index = int(self.scheduler_event_index)
        self.time = float(self.event_time_key)

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible runtime-state artifact."""

        assert self.packet_ledger is not None
        return {
            "artifact_kind": LGRC9V3_RUNTIME_STATE_KIND,
            "artifact_schema_version": LGRC9V3_RUNTIME_STATE_SCHEMA_VERSION,
            "mode_version": LGRC9V3_LGRC2_MODE_VERSION,
            "runtime_family": "LGRC9V3",
            "evidence_class": LGRC9V3_PACKETIZED_EVIDENCE_CLASS,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "event_time_key": float(self.event_time_key),
            "node_proper_time": _string_keyed_float_map(self.node_proper_time),
            "node_last_update_proper_time": _string_keyed_float_map(
                self.node_last_update_proper_time
            ),
            "node_last_update_event_time_key": _string_keyed_float_map(
                self.node_last_update_event_time_key
            ),
            "edge_causal_delay": _string_keyed_float_map(self.edge_causal_delay),
            "lapse": _string_keyed_float_map(self.lapse),
            "causal_flux_routes": _string_keyed_route_map(self.causal_flux_routes),
            "boundary_birth_trial_queue": [
                dict(trial) for trial in self.boundary_birth_trial_queue
            ],
            "packet_ledger": self.packet_ledger.to_artifact(),
            "event_queue_records": [
                event.to_record() for event in self.packet_ledger.event_queue_records
            ],
            "packet_processing_log": [
                result.to_artifact() for result in self.packet_processing_log
            ],
            "arrival_eligibility_log": [
                eligibility.to_artifact()
                for eligibility in self.arrival_eligibility_log
            ],
            "local_update_log": [dict(record) for record in self.local_update_log],
            "causal_spark_evaluation_index": int(
                self.causal_spark_evaluation_index
            ),
            "causal_spark_diagnostic_log": [
                dict(record) for record in self.causal_spark_diagnostic_log
            ],
            "causal_pulse_substrate_surface_log": [
                row.to_artifact() for row in self.causal_pulse_substrate_surface_log
            ],
            "causal_pulse_substrate_surface_lineage_log": [
                record.to_artifact()
                for record in self.causal_pulse_substrate_surface_lineage_log
            ],
            "topology_state_reabsorption_log": [
                record.to_artifact()
                for record in self.topology_state_reabsorption_log
            ],
            "native_route_candidate_log": [
                record.to_artifact() for record in self.native_route_candidate_log
            ],
            "native_route_candidate_set_log": [
                record.to_artifact() for record in self.native_route_candidate_set_log
            ],
            "native_route_arbitration_log": [
                record.to_artifact() for record in self.native_route_arbitration_log
            ],
            "topology_event_log": [
                event
                if isinstance(event, dict)
                else {
                    "kind": event.kind,
                    "step_index": event.step_index,
                    "payload": dict(event.payload),
                    "source_family": event.source_family,
                }
                for event in self.topology_event_log
            ],
            "cached_quantities": dict(self.cached_quantities),
            "causal_modes": dict(sorted(self.causal_modes.items())),
            "event_queue_tie_break_policy": self.event_queue_tie_break_policy,
        }


__all__ = [
    "LGRC9V3_RUNTIME_STATE_KIND",
    "LGRC9V3_RUNTIME_STATE_SCHEMA_VERSION",
    "LGRC9V3RuntimeState",
    "ordered_lgrc9v3_event_queue",
    "restore_lgrc9v3_event_record",
    "restore_lgrc9v3_runtime_state_artifact",
    "with_ordered_lgrc9v3_event_queue",
]
