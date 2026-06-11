"""LGRC9V3 topology-changing causal-history evidence helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import heapq
import math
from typing import Any, Final

from pygrc.core import (
    digest_canonical_data,
    EdgeId,
    GRCEvent,
    InvalidParamsError,
    InvalidStateTransitionError,
    NodeId,
    SnapshotCompatibilityError,
)

from .grc_9_ports import port_to_rc
from .grc_9_v3_state import GRC9V3State

from .lgrc_9_v3_contract import *
from .lgrc_9_v3_packets import *


def _transport_record_sort_key(
    record: "LGRC9V3PacketTransportRecord",
) -> tuple[str, str]:
    return (record.source_packet_id, record.transport_record_id)


@dataclass(frozen=True)
class LGRC9V3PacketTransportRecord:
    """Audit row for one packet considered during refinement transport."""

    transport_record_id: str
    source_packet_id: str
    transported_packet_id: str
    source_pending_flux_entry_ids: tuple[str, ...]
    packet_state: str
    amount: float
    edge_id: EdgeId
    source_node_id_before: NodeId
    source_node_id_after: NodeId
    target_node_id_before: NodeId
    target_node_id_after: NodeId
    source_lineage_id_before: str | None
    source_lineage_id_after: str | None
    target_lineage_id_before: str | None
    target_lineage_id_after: str | None
    endpoint_transported: bool
    old_parent_port: int | None = None
    new_endpoint_port: int | None = None
    old_parent_column: int | None = None
    new_endpoint_column: int | None = None

    def __post_init__(self) -> None:
        for field_name in ("transport_record_id", "source_packet_id", "transported_packet_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.packet_state not in LGRC9V3_PACKET_STATES:
            raise ValueError("packet_state must be a known packet state")
        _positive_float(self.amount, context="amount")
        for field_name in (
            "edge_id",
            "source_node_id_before",
            "source_node_id_after",
            "target_node_id_before",
            "target_node_id_after",
        ):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        for field_name in (
            "old_parent_port",
            "new_endpoint_port",
            "old_parent_column",
            "new_endpoint_column",
        ):
            value = getattr(self, field_name)
            if value is not None and int(value) <= 0:
                raise ValueError(f"{field_name} must be > 0 when present")

    def to_record(self) -> dict[str, Any]:
        """Return a JSON-compatible packet transport record."""

        return {
            "transport_record_id": self.transport_record_id,
            "source_packet_id": self.source_packet_id,
            "transported_packet_id": self.transported_packet_id,
            "source_pending_flux_entry_ids": list(self.source_pending_flux_entry_ids),
            "packet_state": self.packet_state,
            "amount": float(self.amount),
            "edge_id": int(self.edge_id),
            "source_node_id_before": int(self.source_node_id_before),
            "source_node_id_after": int(self.source_node_id_after),
            "target_node_id_before": int(self.target_node_id_before),
            "target_node_id_after": int(self.target_node_id_after),
            "source_lineage_id_before": self.source_lineage_id_before,
            "source_lineage_id_after": self.source_lineage_id_after,
            "target_lineage_id_before": self.target_lineage_id_before,
            "target_lineage_id_after": self.target_lineage_id_after,
            "endpoint_transported": self.endpoint_transported,
            "old_parent_port": self.old_parent_port,
            "new_endpoint_port": self.new_endpoint_port,
            "old_parent_column": self.old_parent_column,
            "new_endpoint_column": self.new_endpoint_column,
        }


@dataclass(frozen=True)
class LGRC9V3RefinementPacketTransportResult:
    """LGRC-3 packet transport evidence for one refinement event."""

    topology_event_id: str
    source_expansion_event_id: str
    source_candidate_event_id: str | None
    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    expanded_node_id: NodeId
    replacement_node_ids: tuple[NodeId, ...]
    pre_topology_signature: dict[str, Any]
    post_topology_signature: dict[str, Any]
    reassignment_map: dict[str, Any]
    packet_transport_records: tuple[LGRC9V3PacketTransportRecord, ...]
    transported_ledger: LGRC9V3PacketLedger
    source_packet_ledger_schema_version: str
    source_pending_flux_ledger_schema_version: str | None
    source_pending_flux_entry_ids: tuple[str, ...]
    source_packet_ids: tuple[str, ...]
    transported_packet_ids: tuple[str, ...]
    amount_total: float
    budget_before: float
    budget_after: float
    budget_error: float
    state_mutated: bool = False
    topology_mutated: bool = False
    spark_event_emitted: bool = False
    mechanical_expansion_emitted: bool = False
    identity_acceptance_emitted: bool = False
    packet_transport_identity_transfer: bool = False
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    evidence_class: str = LGRC9V3_PACKET_TRANSPORT_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        for field_name in ("topology_event_id", "source_expansion_event_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.source_candidate_event_id is not None and not isinstance(
            self.source_candidate_event_id,
            str,
        ):
            raise ValueError("source_candidate_event_id must be a string or None")
        for field_name in ("scheduler_event_index", "checkpoint_index"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.expanded_node_id) < 0:
            raise ValueError("expanded_node_id must be >= 0")
        for node_id in self.replacement_node_ids:
            if int(node_id) < 0:
                raise ValueError("replacement_node_ids must be >= 0")
        records = tuple(
            sorted(self.packet_transport_records, key=_transport_record_sort_key)
        )
        object.__setattr__(self, "packet_transport_records", records)
        _nonnegative_float(self.amount_total, context="amount_total")
        _nonnegative_float(self.budget_before, context="budget_before")
        _nonnegative_float(self.budget_after, context="budget_after")
        _finite_float(self.budget_error, context="budget_error")
        if abs((self.budget_after - self.budget_before) - self.budget_error) > 1e-12:
            raise ValueError("budget_error must equal budget_after - budget_before")
        calculated_amount = sum(record.amount for record in records)
        if abs(calculated_amount - self.amount_total) > 1e-12:
            raise ValueError("amount_total must match packet transport records")
        if self.identity_acceptance_emitted:
            raise ValueError("packet transport must not emit identity acceptance")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible refinement packet transport artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "topology_event_id": self.topology_event_id,
            "topology_event_kind": (
                LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT
            ),
            "source_expansion_event_id": self.source_expansion_event_id,
            "source_candidate_event_id": self.source_candidate_event_id,
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "event_time_key": float(self.event_time_key),
            "expanded_node_id": int(self.expanded_node_id),
            "replacement_node_ids": [int(node_id) for node_id in self.replacement_node_ids],
            "pre_topology_signature": dict(self.pre_topology_signature),
            "post_topology_signature": dict(self.post_topology_signature),
            "reassignment_map": dict(self.reassignment_map),
            "source_packet_ledger_schema_version": (
                self.source_packet_ledger_schema_version
            ),
            "source_pending_flux_ledger_schema_version": (
                self.source_pending_flux_ledger_schema_version
            ),
            "source_pending_flux_entry_ids": list(self.source_pending_flux_entry_ids),
            "source_packet_ids": list(self.source_packet_ids),
            "transported_packet_ids": list(self.transported_packet_ids),
            "amount_total": float(self.amount_total),
            "budget_before": float(self.budget_before),
            "budget_after": float(self.budget_after),
            "budget_error": float(self.budget_error),
            "state_mutated": self.state_mutated,
            "topology_mutated": self.topology_mutated,
            "spark_event_emitted": self.spark_event_emitted,
            "mechanical_expansion_emitted": self.mechanical_expansion_emitted,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
            "packet_transport_identity_transfer": (
                self.packet_transport_identity_transfer
            ),
            "transported_ledger": self.transported_ledger.to_artifact(),
            "packet_transport_records": [
                record.to_record() for record in self.packet_transport_records
            ],
        }


@dataclass(frozen=True)
class LGRC9V3ProperTimeInheritanceRecord:
    """Audit row for one child node created by a refinement event."""

    inheritance_record_id: str
    child_node_id: NodeId
    parent_node_id: NodeId
    parent_proper_time: float
    child_proper_time: float
    proper_time_inheritance_policy: str = (
        LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT
    )

    def __post_init__(self) -> None:
        if not isinstance(self.inheritance_record_id, str) or not self.inheritance_record_id:
            raise ValueError("inheritance_record_id must be a non-empty string")
        for field_name in ("child_node_id", "parent_node_id"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        parent_time = _nonnegative_float(
            self.parent_proper_time,
            context="parent_proper_time",
        )
        child_time = _nonnegative_float(
            self.child_proper_time,
            context="child_proper_time",
        )
        if self.proper_time_inheritance_policy != (
            LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT
        ):
            raise ValueError("unsupported proper_time_inheritance_policy")
        if abs(parent_time - child_time) > 1e-12:
            raise ValueError("uniform_parent_proper_time requires child == parent")

    def to_record(self) -> dict[str, Any]:
        """Return a JSON-compatible proper-time inheritance row."""

        return {
            "inheritance_record_id": self.inheritance_record_id,
            "child_node_id": int(self.child_node_id),
            "parent_node_id": int(self.parent_node_id),
            "parent_proper_time": float(self.parent_proper_time),
            "child_proper_time": float(self.child_proper_time),
            "proper_time_inheritance_policy": self.proper_time_inheritance_policy,
        }


@dataclass(frozen=True)
class LGRC9V3ProperTimeInheritanceResult:
    """LGRC-3 proper-time inheritance evidence for one refinement event."""

    topology_event_id: str
    source_expansion_event_id: str
    source_candidate_event_id: str | None
    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    expanded_node_id: NodeId
    replacement_node_ids: tuple[NodeId, ...]
    internal_edge_ids: tuple[EdgeId, ...]
    proper_time_inheritance_records: tuple[LGRC9V3ProperTimeInheritanceRecord, ...]
    parent_proper_time: float
    child_proper_time: dict[NodeId, float]
    internal_edge_delay: dict[EdgeId, float]
    source_parent_proper_time_surface: dict[NodeId, float]
    explicit_internal_edge_delay_provided: bool = False
    state_mutated: bool = False
    topology_mutated: bool = False
    spark_event_emitted: bool = False
    mechanical_expansion_emitted: bool = False
    identity_acceptance_emitted: bool = False
    refinement_lineage_identity_persistence: bool = False
    proper_time_inheritance_policy: str = (
        LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT
    )
    internal_edge_delay_policy: str = (
        LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0
    )
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    evidence_class: str = LGRC9V3_PROPER_TIME_INHERITANCE_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        for field_name in ("topology_event_id", "source_expansion_event_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        for field_name in ("scheduler_event_index", "checkpoint_index"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.expanded_node_id) < 0:
            raise ValueError("expanded_node_id must be >= 0")
        replacement_ids = tuple(sorted(int(node_id) for node_id in self.replacement_node_ids))
        internal_ids = tuple(sorted(int(edge_id) for edge_id in self.internal_edge_ids))
        if not replacement_ids:
            raise ValueError("replacement_node_ids must not be empty")
        if not internal_ids:
            raise ValueError("internal_edge_ids must not be empty")
        object.__setattr__(self, "replacement_node_ids", replacement_ids)
        object.__setattr__(self, "internal_edge_ids", internal_ids)

        parent_time = _nonnegative_float(
            self.parent_proper_time,
            context="parent_proper_time",
        )
        child_times = {
            int(node_id): _nonnegative_float(
                value,
                context=f"child_proper_time[{node_id}]",
            )
            for node_id, value in self.child_proper_time.items()
        }
        if set(child_times) != set(replacement_ids):
            raise ValueError("child_proper_time must cover replacement_node_ids")
        for node_id, value in child_times.items():
            if abs(value - parent_time) > 1e-12:
                raise ValueError(
                    f"child_proper_time[{node_id}] must equal parent_proper_time"
                )
        object.__setattr__(self, "child_proper_time", dict(sorted(child_times.items())))

        internal_delays = {
            int(edge_id): _positive_float(
                value,
                context=f"internal_edge_delay[{edge_id}]",
            )
            for edge_id, value in self.internal_edge_delay.items()
        }
        if set(internal_delays) != set(internal_ids):
            raise ValueError("internal_edge_delay must cover internal_edge_ids")
        object.__setattr__(
            self,
            "internal_edge_delay",
            dict(sorted(internal_delays.items())),
        )

        records = tuple(
            sorted(
                self.proper_time_inheritance_records,
                key=lambda record: int(record.child_node_id),
            )
        )
        if tuple(int(record.child_node_id) for record in records) != replacement_ids:
            raise ValueError(
                "proper_time_inheritance_records must cover replacement_node_ids"
            )
        object.__setattr__(self, "proper_time_inheritance_records", records)

        source_surface = {
            int(node_id): _nonnegative_float(
                value,
                context=f"source_parent_proper_time_surface[{node_id}]",
            )
            for node_id, value in self.source_parent_proper_time_surface.items()
        }
        if int(self.expanded_node_id) not in source_surface:
            raise ValueError("source parent proper-time surface must include parent")
        object.__setattr__(
            self,
            "source_parent_proper_time_surface",
            dict(sorted(source_surface.items())),
        )

        if self.proper_time_inheritance_policy != (
            LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT
        ):
            raise ValueError("unsupported proper_time_inheritance_policy")
        if self.internal_edge_delay_policy != (
            LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0
        ):
            raise ValueError("unsupported internal_edge_delay_policy")
        for field_name in (
            "state_mutated",
            "topology_mutated",
            "spark_event_emitted",
            "mechanical_expansion_emitted",
        ):
            if getattr(self, field_name):
                raise ValueError(f"{field_name} must be false")
        if self.identity_acceptance_emitted:
            raise ValueError("proper-time inheritance must not emit identity")
        if self.refinement_lineage_identity_persistence:
            raise ValueError("refinement lineage is not identity persistence")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible proper-time inheritance artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "topology_event_id": self.topology_event_id,
            "topology_event_kind": (
                LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE
            ),
            "source_expansion_event_id": self.source_expansion_event_id,
            "source_candidate_event_id": self.source_candidate_event_id,
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "event_time_key": float(self.event_time_key),
            "expanded_node_id": int(self.expanded_node_id),
            "replacement_node_ids": [int(node_id) for node_id in self.replacement_node_ids],
            "internal_edge_ids": [int(edge_id) for edge_id in self.internal_edge_ids],
            "proper_time_inheritance_policy": self.proper_time_inheritance_policy,
            "internal_edge_delay_policy": self.internal_edge_delay_policy,
            "parent_proper_time": float(self.parent_proper_time),
            "child_proper_time": _string_keyed_float_map(self.child_proper_time),
            "internal_edge_delay": _string_keyed_float_map(self.internal_edge_delay),
            "source_parent_proper_time_surface": _string_keyed_float_map(
                self.source_parent_proper_time_surface
            ),
            "proper_time_inheritance_records": [
                record.to_record() for record in self.proper_time_inheritance_records
            ],
            "explicit_internal_edge_delay_provided": (
                self.explicit_internal_edge_delay_provided
            ),
            "state_mutated": self.state_mutated,
            "topology_mutated": self.topology_mutated,
            "spark_event_emitted": self.spark_event_emitted,
            "mechanical_expansion_emitted": self.mechanical_expansion_emitted,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
            "refinement_lineage_identity_persistence": (
                self.refinement_lineage_identity_persistence
            ),
        }


@dataclass(frozen=True)
class LGRC9V3CollapseReabsorptionResult:
    """LGRC-3 collapse/reabsorption evidence with budget and lineage audit."""

    topology_event_id: str
    topology_event_kind: str
    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    node_proper_time: dict[NodeId, float]
    competing_sink_ids: tuple[NodeId, ...]
    selected_sink_id: NodeId
    losing_sink_ids: tuple[NodeId, ...]
    lineage_transfer_map: dict[NodeId, str]
    source_lineage_ids: dict[NodeId, str]
    target_lineage_id: str
    transferred_node_ids: tuple[NodeId, ...]
    transferred_packet_ids: tuple[str, ...]
    transferred_pending_flux_entry_ids: tuple[str, ...]
    coherence_transfer_amount: float
    budget_before: float
    budget_after: float
    budget_error: float
    source_packet_ledger_schema_version: str | None = None
    source_pending_flux_ledger_schema_version: str | None = None
    budget_transfer_policy: str = LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING
    lineage_transfer_policy: str = LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP
    proper_time_transfer_policy: str = (
        LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY
    )
    collapse_reabsorption_allowed: bool = True
    collapse_reabsorption_processing_implemented: bool = True
    state_mutated: bool = False
    topology_mutated: bool = False
    packet_transport_emitted: bool = False
    identity_acceptance_emitted: bool = False
    native_route_arbitration_record_id: str | None = None
    native_route_arbitration_digest: str | None = None
    native_route_selected_candidate_route_id: str | None = None
    native_route_selected_candidate_route_digest: str | None = None
    native_route_candidate_set_digest: str | None = None
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    evidence_class: str = LGRC9V3_COLLAPSE_REABSORPTION_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        if not isinstance(self.topology_event_id, str) or not self.topology_event_id:
            raise ValueError("topology_event_id must be a non-empty string")
        if self.topology_event_kind not in {
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        }:
            raise ValueError("topology_event_kind must be collapse or reabsorption")
        for field_name in ("scheduler_event_index", "checkpoint_index"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        selected_id = int(self.selected_sink_id)
        if selected_id < 0:
            raise ValueError("selected_sink_id must be >= 0")

        competing = tuple(sorted({int(node_id) for node_id in self.competing_sink_ids}))
        losing = tuple(sorted({int(node_id) for node_id in self.losing_sink_ids}))
        transferred = tuple(sorted({int(node_id) for node_id in self.transferred_node_ids}))
        if not losing:
            raise ValueError("losing_sink_ids must not be empty")
        if selected_id in losing:
            raise ValueError("selected_sink_id must not be a losing sink")
        if selected_id not in competing or not set(losing) <= set(competing):
            raise ValueError("competing_sink_ids must include selected and losing sinks")
        if not transferred:
            raise ValueError("transferred_node_ids must not be empty")
        object.__setattr__(self, "selected_sink_id", selected_id)
        object.__setattr__(self, "competing_sink_ids", competing)
        object.__setattr__(self, "losing_sink_ids", losing)
        object.__setattr__(self, "transferred_node_ids", transferred)

        proper_times = {
            int(node_id): _nonnegative_float(
                value,
                context=f"node_proper_time[{node_id}]",
            )
            for node_id, value in self.node_proper_time.items()
        }
        if selected_id not in proper_times:
            raise ValueError("node_proper_time must include selected_sink_id")
        object.__setattr__(self, "node_proper_time", dict(sorted(proper_times.items())))

        if not isinstance(self.target_lineage_id, str) or not self.target_lineage_id:
            raise ValueError("target_lineage_id must be a non-empty string")
        lineage_map = {
            int(node_id): str(target)
            for node_id, target in self.lineage_transfer_map.items()
        }
        if set(lineage_map) != set(transferred):
            raise ValueError("lineage_transfer_map must cover transferred_node_ids")
        for node_id, target in lineage_map.items():
            if not target:
                raise ValueError(f"lineage_transfer_map[{node_id}] must be non-empty")
            if target != self.target_lineage_id:
                raise ValueError(
                    "selected_sink_clock_continuity requires target lineage continuity"
                )
        object.__setattr__(self, "lineage_transfer_map", dict(sorted(lineage_map.items())))

        source_lineages = {
            int(node_id): str(lineage_id)
            for node_id, lineage_id in self.source_lineage_ids.items()
        }
        if set(source_lineages) != set(transferred):
            raise ValueError("source_lineage_ids must cover transferred_node_ids")
        for node_id, lineage_id in source_lineages.items():
            if not lineage_id:
                raise ValueError(f"source_lineage_ids[{node_id}] must be non-empty")
        object.__setattr__(
            self,
            "source_lineage_ids",
            dict(sorted(source_lineages.items())),
        )

        object.__setattr__(self, "transferred_packet_ids", tuple(sorted(self.transferred_packet_ids)))
        object.__setattr__(
            self,
            "transferred_pending_flux_entry_ids",
            tuple(sorted(self.transferred_pending_flux_entry_ids)),
        )
        _nonnegative_float(
            self.coherence_transfer_amount,
            context="coherence_transfer_amount",
        )
        _nonnegative_float(self.budget_before, context="budget_before")
        _nonnegative_float(self.budget_after, context="budget_after")
        _finite_float(self.budget_error, context="budget_error")
        if abs((self.budget_after - self.budget_before) - self.budget_error) > 1e-12:
            raise ValueError("budget_error must equal budget_after - budget_before")
        if abs(self.budget_error) > 1e-12:
            raise ValueError("budget_conserving_transfer requires zero budget error")
        if self.budget_transfer_policy != LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING:
            raise ValueError("unsupported budget_transfer_policy")
        if self.lineage_transfer_policy != LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP:
            raise ValueError("unsupported lineage_transfer_policy")
        if self.proper_time_transfer_policy != (
            LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY
        ):
            raise ValueError("unsupported proper_time_transfer_policy")
        if not self.collapse_reabsorption_allowed:
            raise ValueError("collapse/reabsorption must be explicitly allowed")
        if not self.collapse_reabsorption_processing_implemented:
            raise ValueError("collapse/reabsorption processing must be active")
        for field_name in ("state_mutated", "topology_mutated", "packet_transport_emitted"):
            if getattr(self, field_name):
                raise ValueError(f"{field_name} must be false")
        if self.identity_acceptance_emitted:
            raise ValueError("collapse/reabsorption must not emit identity acceptance")
        for field_name in (
            "native_route_arbitration_record_id",
            "native_route_arbitration_digest",
            "native_route_selected_candidate_route_id",
            "native_route_selected_candidate_route_digest",
            "native_route_candidate_set_digest",
        ):
            value = getattr(self, field_name)
            if value is not None and (not isinstance(value, str) or not value):
                raise ValueError(f"{field_name} must be a non-empty string when set")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible collapse/reabsorption artifact."""

        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "topology_event_id": self.topology_event_id,
            "topology_event_kind": self.topology_event_kind,
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "event_time_key": float(self.event_time_key),
            "node_proper_time": _string_keyed_float_map(self.node_proper_time),
            "competing_sink_ids": [int(node_id) for node_id in self.competing_sink_ids],
            "selected_sink_id": int(self.selected_sink_id),
            "losing_sink_ids": [int(node_id) for node_id in self.losing_sink_ids],
            "lineage_transfer_map": {
                str(int(node_id)): lineage_id
                for node_id, lineage_id in sorted(self.lineage_transfer_map.items())
            },
            "source_lineage_ids": {
                str(int(node_id)): lineage_id
                for node_id, lineage_id in sorted(self.source_lineage_ids.items())
            },
            "target_lineage_id": self.target_lineage_id,
            "transferred_node_ids": [
                int(node_id) for node_id in self.transferred_node_ids
            ],
            "transferred_packet_ids": list(self.transferred_packet_ids),
            "transferred_pending_flux_entry_ids": list(
                self.transferred_pending_flux_entry_ids
            ),
            "source_packet_ledger_schema_version": (
                self.source_packet_ledger_schema_version
            ),
            "source_pending_flux_ledger_schema_version": (
                self.source_pending_flux_ledger_schema_version
            ),
            "coherence_transfer_amount": float(self.coherence_transfer_amount),
            "budget_before": float(self.budget_before),
            "budget_after": float(self.budget_after),
            "budget_error": float(self.budget_error),
            "budget_transfer_policy": self.budget_transfer_policy,
            "lineage_transfer_policy": self.lineage_transfer_policy,
            "proper_time_transfer_policy": self.proper_time_transfer_policy,
            "collapse_reabsorption_allowed": self.collapse_reabsorption_allowed,
            "collapse_reabsorption_processing_implemented": (
                self.collapse_reabsorption_processing_implemented
            ),
            "state_mutated": self.state_mutated,
            "topology_mutated": self.topology_mutated,
            "packet_transport_emitted": self.packet_transport_emitted,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
        }
        if self.native_route_arbitration_record_id is not None:
            artifact["native_route_arbitration_record_id"] = (
                self.native_route_arbitration_record_id
            )
        if self.native_route_arbitration_digest is not None:
            artifact["native_route_arbitration_digest"] = (
                self.native_route_arbitration_digest
            )
        if self.native_route_selected_candidate_route_id is not None:
            artifact["native_route_selected_candidate_route_id"] = (
                self.native_route_selected_candidate_route_id
            )
        if self.native_route_selected_candidate_route_digest is not None:
            artifact["native_route_selected_candidate_route_digest"] = (
                self.native_route_selected_candidate_route_digest
            )
        if self.native_route_candidate_set_digest is not None:
            artifact["native_route_candidate_set_digest"] = (
                self.native_route_candidate_set_digest
            )
        return artifact


@dataclass(frozen=True)
class LGRC9V3CollapsePacketTransportResult:
    """Packet transport evidence through collapse/reabsorption lineage."""

    source_topology_event_id: str
    source_topology_event_kind: str
    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    selected_sink_id: NodeId
    target_lineage_id: str
    lineage_transfer_map: dict[NodeId, str]
    packet_transport_records: tuple[LGRC9V3PacketTransportRecord, ...]
    transported_ledger: LGRC9V3PacketLedger
    transported_pending_flux_ledger: LGRC9V3PendingFluxLedger | None
    source_packet_ledger_schema_version: str
    source_pending_flux_ledger_schema_version: str | None
    source_pending_flux_entry_ids: tuple[str, ...]
    transported_pending_flux_entry_ids: tuple[str, ...]
    settled_pending_flux_entry_ids: tuple[str, ...]
    source_packet_ids: tuple[str, ...]
    transported_packet_ids: tuple[str, ...]
    settled_packet_ids: tuple[str, ...]
    amount_total: float
    settled_amount_total: float
    budget_before: float
    budget_after: float
    budget_error: float
    transport_policy: str = LGRC9V3_COLLAPSE_PACKET_TRANSPORT_POLICY_REDIRECT_OR_SETTLE
    state_mutated: bool = False
    topology_mutated: bool = False
    identity_acceptance_emitted: bool = False
    packet_transport_identity_transfer: bool = False
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    evidence_class: str = LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        if not isinstance(self.source_topology_event_id, str) or not self.source_topology_event_id:
            raise ValueError("source_topology_event_id must be a non-empty string")
        if self.source_topology_event_kind not in {
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        }:
            raise ValueError("source_topology_event_kind must be collapse/reabsorption")
        for field_name in ("scheduler_event_index", "checkpoint_index"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.selected_sink_id) < 0:
            raise ValueError("selected_sink_id must be >= 0")
        if not isinstance(self.target_lineage_id, str) or not self.target_lineage_id:
            raise ValueError("target_lineage_id must be a non-empty string")
        lineage_map = {
            int(node_id): str(lineage_id)
            for node_id, lineage_id in self.lineage_transfer_map.items()
        }
        if not lineage_map:
            raise ValueError("lineage_transfer_map must not be empty")
        if any(not lineage_id for lineage_id in lineage_map.values()):
            raise ValueError("lineage_transfer_map values must be non-empty")
        object.__setattr__(self, "lineage_transfer_map", dict(sorted(lineage_map.items())))
        records = tuple(
            sorted(self.packet_transport_records, key=_transport_record_sort_key)
        )
        object.__setattr__(self, "packet_transport_records", records)
        _nonnegative_float(self.amount_total, context="amount_total")
        _nonnegative_float(self.settled_amount_total, context="settled_amount_total")
        if self.settled_amount_total > self.amount_total + 1e-12:
            raise ValueError("settled_amount_total must be <= amount_total")
        _nonnegative_float(self.budget_before, context="budget_before")
        _nonnegative_float(self.budget_after, context="budget_after")
        _finite_float(self.budget_error, context="budget_error")
        if abs((self.budget_after - self.budget_before) - self.budget_error) > 1e-12:
            raise ValueError("budget_error must equal budget_after - budget_before")
        if abs(self.budget_error) > 1e-12:
            raise ValueError("collapse packet transport must preserve budget")
        calculated_amount = sum(record.amount for record in records)
        if abs(calculated_amount - self.amount_total) > 1e-12:
            raise ValueError("amount_total must match packet transport records")
        if self.transport_policy != (
            LGRC9V3_COLLAPSE_PACKET_TRANSPORT_POLICY_REDIRECT_OR_SETTLE
        ):
            raise ValueError("unsupported collapse packet transport policy")
        for field_name in (
            "state_mutated",
            "topology_mutated",
            "identity_acceptance_emitted",
            "packet_transport_identity_transfer",
        ):
            if getattr(self, field_name):
                raise ValueError(f"{field_name} must be false")
        object.__setattr__(self, "source_packet_ids", tuple(sorted(self.source_packet_ids)))
        object.__setattr__(
            self,
            "transported_packet_ids",
            tuple(sorted(self.transported_packet_ids)),
        )
        object.__setattr__(self, "settled_packet_ids", tuple(sorted(self.settled_packet_ids)))
        object.__setattr__(
            self,
            "source_pending_flux_entry_ids",
            tuple(sorted(self.source_pending_flux_entry_ids)),
        )
        object.__setattr__(
            self,
            "transported_pending_flux_entry_ids",
            tuple(sorted(self.transported_pending_flux_entry_ids)),
        )
        object.__setattr__(
            self,
            "settled_pending_flux_entry_ids",
            tuple(sorted(self.settled_pending_flux_entry_ids)),
        )

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible collapse packet transport artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "source_topology_event_id": self.source_topology_event_id,
            "source_topology_event_kind": self.source_topology_event_kind,
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "event_time_key": float(self.event_time_key),
            "selected_sink_id": int(self.selected_sink_id),
            "target_lineage_id": self.target_lineage_id,
            "lineage_transfer_map": {
                str(int(node_id)): lineage_id
                for node_id, lineage_id in sorted(self.lineage_transfer_map.items())
            },
            "transport_policy": self.transport_policy,
            "source_packet_ledger_schema_version": (
                self.source_packet_ledger_schema_version
            ),
            "source_pending_flux_ledger_schema_version": (
                self.source_pending_flux_ledger_schema_version
            ),
            "source_pending_flux_entry_ids": list(self.source_pending_flux_entry_ids),
            "transported_pending_flux_entry_ids": list(
                self.transported_pending_flux_entry_ids
            ),
            "settled_pending_flux_entry_ids": list(
                self.settled_pending_flux_entry_ids
            ),
            "source_packet_ids": list(self.source_packet_ids),
            "transported_packet_ids": list(self.transported_packet_ids),
            "settled_packet_ids": list(self.settled_packet_ids),
            "amount_total": float(self.amount_total),
            "settled_amount_total": float(self.settled_amount_total),
            "budget_before": float(self.budget_before),
            "budget_after": float(self.budget_after),
            "budget_error": float(self.budget_error),
            "state_mutated": self.state_mutated,
            "topology_mutated": self.topology_mutated,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
            "packet_transport_identity_transfer": (
                self.packet_transport_identity_transfer
            ),
            "transported_ledger": self.transported_ledger.to_artifact(),
            "transported_pending_flux_ledger": None
            if self.transported_pending_flux_ledger is None
            else self.transported_pending_flux_ledger.to_artifact(),
            "packet_transport_records": [
                record.to_record() for record in self.packet_transport_records
            ],
        }



@dataclass(frozen=True)
class LGRC9V3TopologyReplayRecord:
    """One normalized LGRC-3 topology/evidence replay row."""

    replay_record_id: str
    record_kind: str
    topology_event_id: str
    topology_event_kind: str
    event_time_key: float
    scheduler_event_index: int
    checkpoint_index: int
    budget_before: float | None
    budget_after: float | None
    budget_error: float | None
    lineage_ids: tuple[str, ...]
    source_topology_event_ids: tuple[str, ...] = ()
    source_identity_evaluation_id: str | None = None
    identity_acceptance_emitted: bool = False
    creates_topology_event: bool = True

    def __post_init__(self) -> None:
        for field_name in ("replay_record_id", "record_kind", "topology_event_id", "topology_event_kind"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        for field_name in ("scheduler_event_index", "checkpoint_index"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        lineage_ids = tuple(sorted({str(lineage_id) for lineage_id in self.lineage_ids}))
        if any(not lineage_id for lineage_id in lineage_ids):
            raise ValueError("lineage_ids must not contain empty strings")
        object.__setattr__(self, "lineage_ids", lineage_ids)
        source_ids = tuple(
            sorted({str(event_id) for event_id in self.source_topology_event_ids})
        )
        if any(not event_id for event_id in source_ids):
            raise ValueError("source_topology_event_ids must not contain empty strings")
        object.__setattr__(self, "source_topology_event_ids", source_ids)
        if self.source_identity_evaluation_id is not None and not self.source_identity_evaluation_id:
            raise ValueError("source_identity_evaluation_id must be non-empty")
        budget_values = (self.budget_before, self.budget_after, self.budget_error)
        if any(value is None for value in budget_values):
            if any(value is not None for value in budget_values):
                raise ValueError("budget fields must be all present or all absent")
        else:
            assert self.budget_before is not None
            assert self.budget_after is not None
            assert self.budget_error is not None
            _nonnegative_float(self.budget_before, context="budget_before")
            _nonnegative_float(self.budget_after, context="budget_after")
            _finite_float(self.budget_error, context="budget_error")
            if abs((self.budget_after - self.budget_before) - self.budget_error) > 1e-12:
                raise ValueError("budget_error must equal budget_after - budget_before")

    def to_record(self) -> dict[str, Any]:
        """Return a JSON-compatible replay row."""

        return {
            "replay_record_id": self.replay_record_id,
            "record_kind": self.record_kind,
            "topology_event_id": self.topology_event_id,
            "topology_event_kind": self.topology_event_kind,
            "event_time_key": float(self.event_time_key),
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "budget_before": None
            if self.budget_before is None
            else float(self.budget_before),
            "budget_after": None if self.budget_after is None else float(self.budget_after),
            "budget_error": None if self.budget_error is None else float(self.budget_error),
            "lineage_ids": list(self.lineage_ids),
            "source_topology_event_ids": list(self.source_topology_event_ids),
            "source_identity_evaluation_id": self.source_identity_evaluation_id,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
            "creates_topology_event": self.creates_topology_event,
        }


@dataclass(frozen=True)
class LGRC9V3TopologyReplayValidationResult:
    """Validation result for LGRC-3 topology/event evidence replay."""

    replay_records: tuple[LGRC9V3TopologyReplayRecord, ...]
    start_budget: float | None
    end_budget: float | None
    budget_error: float | None
    accepted_artifact_count: int
    event_time_order_valid: bool = True
    lineage_continuity_valid: bool = True
    budget_conservation_valid: bool = True
    replay_valid: bool = True
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    evidence_class: str = LGRC9V3_TOPOLOGY_REPLAY_VALIDATION_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        records = tuple(self.replay_records)
        if not records:
            raise ValueError("replay_records must not be empty")
        object.__setattr__(self, "replay_records", records)
        if int(self.accepted_artifact_count) != len(records):
            raise ValueError("accepted_artifact_count must match replay_records")
        budget_values = (self.start_budget, self.end_budget, self.budget_error)
        if any(value is None for value in budget_values):
            if any(value is not None for value in budget_values):
                raise ValueError("replay budget fields must be all present or all absent")
        else:
            assert self.start_budget is not None
            assert self.end_budget is not None
            assert self.budget_error is not None
            _nonnegative_float(self.start_budget, context="start_budget")
            _nonnegative_float(self.end_budget, context="end_budget")
            _finite_float(self.budget_error, context="budget_error")
            if abs((self.end_budget - self.start_budget) - self.budget_error) > 1e-12:
                raise ValueError("budget_error must equal end_budget - start_budget")
        for field_name in (
            "event_time_order_valid",
            "lineage_continuity_valid",
            "budget_conservation_valid",
            "replay_valid",
        ):
            if getattr(self, field_name) is not True:
                raise ValueError(f"{field_name} must be true for validation result")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible topology replay validation artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "accepted_artifact_count": int(self.accepted_artifact_count),
            "event_time_order_valid": self.event_time_order_valid,
            "lineage_continuity_valid": self.lineage_continuity_valid,
            "budget_conservation_valid": self.budget_conservation_valid,
            "replay_valid": self.replay_valid,
            "start_budget": None
            if self.start_budget is None
            else float(self.start_budget),
            "end_budget": None if self.end_budget is None else float(self.end_budget),
            "budget_error": None
            if self.budget_error is None
            else float(self.budget_error),
            "replay_records": [record.to_record() for record in self.replay_records],
        }


@dataclass(frozen=True)
class LGRC9V3CollapseIdentityPolicyContract:
    """LGRC-3 policy contract for deferred collapse and identity surfaces.

    This contract defines payload fields and first-round policy choices. It is
    not an active collapse/reabsorption processor and does not accept identity.
    """

    collapse_reabsorption_allowed: bool = False
    identity_acceptance_allowed: bool = False
    collapse_reabsorption_processing_implemented: bool = False
    proper_time_identity_processing_implemented: bool = False
    proper_time_transfer_policy: str = (
        LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY
    )
    lineage_transfer_policy: str = LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP
    budget_transfer_policy: str = LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING
    identity_clock_policy: str = LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL
    identity_threshold_calibration_policy: str = (
        LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY
    )
    identity_threshold_multiplier: float = (
        LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER
    )
    mechanical_expansion_is_identity_acceptance: bool = False
    refinement_packet_transport_is_identity_transfer: bool = False
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    evidence_class: str = LGRC9V3_LGRC3_POLICY_CONTRACT_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        bool_fields = (
            "collapse_reabsorption_allowed",
            "identity_acceptance_allowed",
            "collapse_reabsorption_processing_implemented",
            "proper_time_identity_processing_implemented",
            "mechanical_expansion_is_identity_acceptance",
            "refinement_packet_transport_is_identity_transfer",
        )
        for field_name in bool_fields:
            if not isinstance(getattr(self, field_name), bool):
                raise ValueError(f"{field_name} must be a boolean")
        if self.proper_time_transfer_policy not in LGRC9V3_PROPER_TIME_TRANSFER_POLICIES:
            raise ValueError("unsupported proper_time_transfer_policy")
        if self.lineage_transfer_policy not in LGRC9V3_LINEAGE_TRANSFER_POLICIES:
            raise ValueError("unsupported lineage_transfer_policy")
        if self.budget_transfer_policy not in LGRC9V3_BUDGET_TRANSFER_POLICIES:
            raise ValueError("unsupported budget_transfer_policy")
        if self.identity_clock_policy not in LGRC9V3_IDENTITY_CLOCK_POLICIES:
            raise ValueError("unsupported identity_clock_policy")
        if (
            self.identity_threshold_calibration_policy
            not in LGRC9V3_IDENTITY_THRESHOLD_POLICIES
        ):
            raise ValueError("unsupported identity_threshold_calibration_policy")
        _positive_float(
            self.identity_threshold_multiplier,
            context="identity_threshold_multiplier",
        )
        if self.mechanical_expansion_is_identity_acceptance:
            raise ValueError("mechanical expansion must not be identity acceptance")
        if self.refinement_packet_transport_is_identity_transfer:
            raise ValueError("packet transport must not be identity transfer")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible LGRC-3 policy contract artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC3_POLICY_CONTRACT_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "contract_only": True,
            "collapse_reabsorption_allowed": self.collapse_reabsorption_allowed,
            "identity_acceptance_allowed": self.identity_acceptance_allowed,
            "collapse_reabsorption_processing_implemented": (
                self.collapse_reabsorption_processing_implemented
            ),
            "proper_time_identity_processing_implemented": (
                self.proper_time_identity_processing_implemented
            ),
            "collapse_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            "reabsorption_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            "identity_acceptance_event_kind": (
                LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE
            ),
            "collapse_reabsorption_required_fields": sorted(
                LGRC9V3_COLLAPSE_REABSORPTION_REQUIRED_FIELDS
            ),
            "proper_time_identity_required_fields": sorted(
                LGRC9V3_PROPER_TIME_IDENTITY_REQUIRED_FIELDS
            ),
            "collapse_reabsorption_field_names": dict(
                vars(LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES)
            ),
            "proper_time_identity_field_names": dict(
                vars(LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES)
            ),
            "proper_time_transfer_policy": self.proper_time_transfer_policy,
            "lineage_transfer_policy": self.lineage_transfer_policy,
            "budget_transfer_policy": self.budget_transfer_policy,
            "identity_clock_policy": self.identity_clock_policy,
            "identity_clock_policy_choices": sorted(LGRC9V3_IDENTITY_CLOCK_POLICIES),
            "identity_threshold_calibration_policy": (
                self.identity_threshold_calibration_policy
            ),
            "identity_threshold_multiplier": float(
                self.identity_threshold_multiplier
            ),
            "mechanical_expansion_is_identity_acceptance": (
                self.mechanical_expansion_is_identity_acceptance
            ),
            "refinement_packet_transport_is_identity_transfer": (
                self.refinement_packet_transport_is_identity_transfer
            ),
        }


def build_lgrc9v3_topology_contract_artifact() -> dict[str, Any]:
    """Return the LGRC-3 topology-changing causal-history contract.

    This is a decision-record artifact. It names the topology-changing fields
    and event kinds that later LGRC-3 processing must satisfy. It does not
    mutate topology, transport packets, collapse basins, or accept identity.
    """

    return {
        "artifact_kind": LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_KIND,
        "artifact_schema_version": (
            LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_SCHEMA_VERSION
        ),
        "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "evidence_class": LGRC9V3_TOPOLOGY_CONTRACT_EVIDENCE_CLASS,
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "contract_only": True,
        "topology_change_contract_defined": True,
        "topology_change_processing_implemented": False,
        "packet_transport_through_topology_change_implemented": False,
        "collapse_reabsorption_in_scope": False,
        "proper_time_identity_in_scope": False,
        "collapse_reabsorption_policy_defined": True,
        "proper_time_identity_policy_defined": True,
        "collapse_identity_policy_contract_kind": (
            LGRC9V3_LGRC3_POLICY_CONTRACT_KIND
        ),
        "collapse_identity_policy_contract_schema_version": (
            LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION
        ),
        "builds_on_lgrc2_packet_accounting": True,
        "builds_on_pending_flux_compaction": True,
        "source_packet_budget_invariant": LGRC9V3_PACKET_BUDGET_INVARIANT,
        "source_pending_flux_compaction_policy": (
            LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT
        ),
        "topology_event_kinds_in_scope": sorted(
            LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_IN_SCOPE
        ),
        "topology_event_kinds_out_of_scope": sorted(
            LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_OUT_OF_SCOPE
        ),
        "topology_contract_field_names": dict(
            vars(LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES)
        ),
        "refinement_lineage_required_fields": sorted(
            LGRC9V3_REFINEMENT_LINEAGE_REQUIRED_FIELDS
        ),
        "packet_transport_required_fields": sorted(
            LGRC9V3_PACKET_TRANSPORT_REQUIRED_FIELDS
        ),
        "proper_time_inheritance_required_fields": sorted(
            LGRC9V3_PROPER_TIME_INHERITANCE_REQUIRED_FIELDS
        ),
        "collapse_reabsorption_required_fields": sorted(
            LGRC9V3_COLLAPSE_REABSORPTION_REQUIRED_FIELDS
        ),
        "proper_time_identity_required_fields": sorted(
            LGRC9V3_PROPER_TIME_IDENTITY_REQUIRED_FIELDS
        ),
        "collapse_reabsorption_field_names": dict(
            vars(LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES)
        ),
        "proper_time_identity_field_names": dict(
            vars(LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES)
        ),
        "proper_time_inheritance_policy": (
            LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT
        ),
        "internal_edge_delay_policy": (
            LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0
        ),
        "proper_time_transfer_policy": (
            LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY
        ),
        "lineage_transfer_policy": LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP,
        "budget_transfer_policy": LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING,
        "identity_clock_policy": LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL,
        "identity_threshold_calibration_policy": (
            LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY
        ),
        "identity_threshold_multiplier": (
            LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER
        ),
        "candidate_expansion_identity_distinction": (
            "candidate_event != mechanical_expansion != identity_acceptance"
        ),
        "packet_identity_distinction": (
            "packet_transport != semantic_identity_transfer"
        ),
        "refinement_identity_distinction": (
            "refinement_lineage != proof_of_persistent_child_identity"
        ),
    }


def build_lgrc9v3_lgrc3_policy_contract_artifact(
    *,
    collapse_reabsorption_allowed: bool = False,
    identity_acceptance_allowed: bool = False,
    proper_time_transfer_policy: str = (
        LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY
    ),
    lineage_transfer_policy: str = LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP,
    budget_transfer_policy: str = LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING,
    identity_clock_policy: str = LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL,
    identity_threshold_calibration_policy: str = (
        LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY
    ),
    identity_threshold_multiplier: float = (
        LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER
    ),
) -> dict[str, Any]:
    """Return the LGRC-3 collapse/identity policy contract artifact.

    The default contract defines payload and policy fields while keeping
    collapse/reabsorption and proper-time identity execution disabled. Passing
    ``*_allowed=True`` scopes a future policy surface, but this helper still
    does not implement the processing loop.
    """

    return LGRC9V3CollapseIdentityPolicyContract(
        collapse_reabsorption_allowed=collapse_reabsorption_allowed,
        identity_acceptance_allowed=identity_acceptance_allowed,
        proper_time_transfer_policy=proper_time_transfer_policy,
        lineage_transfer_policy=lineage_transfer_policy,
        budget_transfer_policy=budget_transfer_policy,
        identity_clock_policy=identity_clock_policy,
        identity_threshold_calibration_policy=(
            identity_threshold_calibration_policy
        ),
        identity_threshold_multiplier=identity_threshold_multiplier,
    ).to_artifact()


def build_lgrc9v3_topology_event_id(
    *,
    event_kind: str,
    source_expansion_event_id: str,
) -> str:
    """Build a deterministic topology-event id for LGRC-3 evidence."""

    allowed_kinds = (
        LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_IN_SCOPE
        | LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_OUT_OF_SCOPE
    )
    if event_kind not in allowed_kinds:
        raise ValueError(f"unsupported topology event kind: {event_kind}")
    if not isinstance(source_expansion_event_id, str) or not source_expansion_event_id:
        raise ValueError("source_expansion_event_id must be a non-empty string")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": event_kind,
        "source_expansion_event_id": source_expansion_event_id,
    }
    return f"lgrc9v3-topology-{digest_canonical_data(payload)[:16]}"


def build_lgrc9v3_collapse_reabsorption_event_id(
    *,
    topology_event_kind: str,
    selected_sink_id: NodeId,
    losing_sink_ids: Sequence[NodeId],
    event_time_key: float,
) -> str:
    """Build a deterministic topology-event id for collapse/reabsorption."""

    if topology_event_kind not in {
        LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
    }:
        raise ValueError("topology_event_kind must be collapse or reabsorption")
    selected = int(selected_sink_id)
    if selected < 0:
        raise ValueError("selected_sink_id must be >= 0")
    losing = tuple(sorted({int(node_id) for node_id in losing_sink_ids}))
    if not losing:
        raise ValueError("losing_sink_ids must not be empty")
    event_time = _nonnegative_float(event_time_key, context="event_time_key")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": topology_event_kind,
        "selected_sink_id": selected,
        "losing_sink_ids": list(losing),
        "event_time_key": event_time,
    }
    return f"lgrc9v3-topology-{digest_canonical_data(payload)[:16]}"


def build_lgrc9v3_packet_transport_record_id(
    *,
    topology_event_id: str,
    source_packet_id: str,
) -> str:
    """Build a deterministic id for one packet transport audit row."""

    if not isinstance(topology_event_id, str) or not topology_event_id:
        raise ValueError("topology_event_id must be a non-empty string")
    if not isinstance(source_packet_id, str) or not source_packet_id:
        raise ValueError("source_packet_id must be a non-empty string")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": "packet_transport_record",
        "topology_event_id": topology_event_id,
        "source_packet_id": source_packet_id,
    }
    return f"lgrc9v3-packet-transport-{digest_canonical_data(payload)[:16]}"


def build_lgrc9v3_proper_time_inheritance_record_id(
    *,
    topology_event_id: str,
    child_node_id: NodeId,
) -> str:
    """Build a deterministic id for one proper-time inheritance row."""

    if not isinstance(topology_event_id, str) or not topology_event_id:
        raise ValueError("topology_event_id must be a non-empty string")
    if int(child_node_id) < 0:
        raise ValueError("child_node_id must be >= 0")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": "proper_time_inheritance_record",
        "topology_event_id": topology_event_id,
        "child_node_id": int(child_node_id),
    }
    return f"lgrc9v3-proper-time-{digest_canonical_data(payload)[:16]}"



def _lineage_after_refinement(
    previous_lineage: str | None,
    *,
    old_node_id: NodeId,
    new_node_id: NodeId,
) -> str | None:
    if int(old_node_id) == int(new_node_id):
        return previous_lineage
    segment = f"node:{int(old_node_id)}->node:{int(new_node_id)}"
    if previous_lineage:
        return f"{previous_lineage}|{segment}"
    return segment


def _pending_flux_entry_ids_by_packet(
    pending_flux_ledger: LGRC9V3PendingFluxLedger | None,
) -> dict[str, tuple[str, ...]]:
    if pending_flux_ledger is None:
        return {}
    mapping: dict[str, list[str]] = {}
    for entry in pending_flux_ledger.pending_flux_entries:
        for packet_id in entry.packet_ids:
            mapping.setdefault(packet_id, []).append(entry.entry_id)
    return {
        packet_id: tuple(sorted(entry_ids))
        for packet_id, entry_ids in sorted(mapping.items())
    }


def _updated_queue_event_for_transport(
    event: LGRC9V3PacketQueueEventRecord,
    packet: LGRC9V3PacketRecord,
) -> LGRC9V3PacketQueueEventRecord:
    if event.packet_id != packet.packet_id:
        return event
    return LGRC9V3PacketQueueEventRecord(
        event_id=event.event_id,
        event_kind=event.event_kind,
        event_time_key=event.event_time_key,
        scheduler_event_index=event.scheduler_event_index,
        packet_id=event.packet_id,
        source_node_id=packet.source_node_id,
        target_node_id=packet.target_node_id,
        edge_id=packet.edge_id,
        amount=event.amount,
        budget_before=event.budget_before,
        budget_after=event.budget_after,
        budget_error=event.budget_error,
    )


def transport_lgrc9v3_packets_through_refinement(
    ledger: LGRC9V3PacketLedger,
    expansion_event: GRCEvent,
    *,
    post_topology_signature: Mapping[str, Any],
    pending_flux_ledger: LGRC9V3PendingFluxLedger | None = None,
) -> LGRC9V3RefinementPacketTransportResult:
    """Transport in-flight packet evidence through one refinement event.

    The helper consumes a completed GRC9V3 mechanical-expansion event and an
    LGRC-2 packet ledger captured before that expansion. It updates packet
    endpoint and lineage evidence for packets whose source or target was the
    expanded node. It does not mutate a ``GRC9V3State`` and does not emit
    identity acceptance.
    """

    if expansion_event.kind != "hybrid_mechanical_expansion":
        raise InvalidStateTransitionError(
            "refinement packet transport requires a hybrid_mechanical_expansion event"
        )
    payload = expansion_event.payload
    source_expansion_event_id = payload.get("expansion_id")
    if not isinstance(source_expansion_event_id, str) or not source_expansion_event_id:
        raise InvalidStateTransitionError("expansion event missing expansion_id")
    expanded_node_id = int(payload.get("sink_node_id"))
    module_node_ids_raw = payload.get("module_node_ids", [])
    if not isinstance(module_node_ids_raw, list) or not module_node_ids_raw:
        raise InvalidStateTransitionError("expansion event missing module_node_ids")
    replacement_node_ids = tuple(int(node_id) for node_id in module_node_ids_raw)
    reassignment_raw = payload.get("reassignment_map", {})
    if not isinstance(reassignment_raw, Mapping):
        raise InvalidStateTransitionError("expansion reassignment_map must be a mapping")
    reassignment_map: dict[int, Mapping[str, Any]] = {}
    for edge_id_raw, reassignment in reassignment_raw.items():
        if not isinstance(reassignment, Mapping):
            raise InvalidStateTransitionError("reassignment rows must be mappings")
        reassignment_map[int(edge_id_raw)] = reassignment

    topology_event_id = build_lgrc9v3_topology_event_id(
        event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
        source_expansion_event_id=source_expansion_event_id,
    )
    resolved_scheduler_event_index = int(expansion_event.step_index)
    resolved_checkpoint_index = int(expansion_event.step_index)
    resolved_event_time_key = _nonnegative_float(
        payload.get("event_time_key", expansion_event.step_index),
        context="event_time_key",
    )
    pending_ids_by_packet = _pending_flux_entry_ids_by_packet(pending_flux_ledger)

    transported_packets_by_id: dict[str, LGRC9V3PacketRecord] = {}
    records: list[LGRC9V3PacketTransportRecord] = []
    source_packet_ids: list[str] = []
    transported_packet_ids: list[str] = []
    for packet in sorted(ledger.packet_records, key=_packet_sort_key):
        if packet.packet_state != LGRC9V3_PACKET_STATE_IN_FLIGHT:
            continue
        source_packet_ids.append(packet.packet_id)
        source_after = int(packet.source_node_id)
        target_after = int(packet.target_node_id)
        source_lineage_after = packet.source_lineage_id
        target_lineage_after = packet.target_lineage_id
        old_parent_port: int | None = None
        new_endpoint_port: int | None = None
        old_parent_column: int | None = None
        new_endpoint_column: int | None = None
        endpoint_transported = False

        if packet.source_node_id == expanded_node_id or packet.target_node_id == expanded_node_id:
            if packet.edge_id not in reassignment_map:
                raise InvalidStateTransitionError(
                    "packet involving expanded node lacks reassignment evidence"
                )
            reassignment = reassignment_map[int(packet.edge_id)]
            target_node = int(reassignment.get("to_node_id"))
            old_parent_port = int(reassignment.get("from_port_id"))
            new_endpoint_port = int(reassignment.get("to_port_id"))
            _, old_parent_column = port_to_rc(old_parent_port)
            _, new_endpoint_column = port_to_rc(new_endpoint_port)
            if old_parent_column != new_endpoint_column:
                raise InvalidStateTransitionError(
                    "refinement transport requires column-preserving reassignment"
                )
            if packet.source_node_id == expanded_node_id:
                source_after = target_node
                source_lineage_after = _lineage_after_refinement(
                    packet.source_lineage_id,
                    old_node_id=expanded_node_id,
                    new_node_id=source_after,
                )
                endpoint_transported = True
            if packet.target_node_id == expanded_node_id:
                target_after = target_node
                target_lineage_after = _lineage_after_refinement(
                    packet.target_lineage_id,
                    old_node_id=expanded_node_id,
                    new_node_id=target_after,
                )
                endpoint_transported = True

        transported_packet = LGRC9V3PacketRecord(
            packet_id=packet.packet_id,
            packet_state=packet.packet_state,
            source_node_id=source_after,
            target_node_id=target_after,
            edge_id=packet.edge_id,
            amount=packet.amount,
            departure_event_time_key=packet.departure_event_time_key,
            arrival_event_time_key=packet.arrival_event_time_key,
            departure_event_id=packet.departure_event_id,
            arrival_event_id=packet.arrival_event_id,
            departure_scheduler_event_index=packet.departure_scheduler_event_index,
            arrival_scheduler_event_index=packet.arrival_scheduler_event_index,
            source_lineage_id=source_lineage_after,
            target_lineage_id=target_lineage_after,
        )
        transported_packets_by_id[packet.packet_id] = transported_packet
        transported_packet_ids.append(transported_packet.packet_id)
        records.append(
            LGRC9V3PacketTransportRecord(
                transport_record_id=build_lgrc9v3_packet_transport_record_id(
                    topology_event_id=topology_event_id,
                    source_packet_id=packet.packet_id,
                ),
                source_packet_id=packet.packet_id,
                transported_packet_id=transported_packet.packet_id,
                source_pending_flux_entry_ids=pending_ids_by_packet.get(
                    packet.packet_id,
                    (),
                ),
                packet_state=packet.packet_state,
                amount=packet.amount,
                edge_id=packet.edge_id,
                source_node_id_before=packet.source_node_id,
                source_node_id_after=transported_packet.source_node_id,
                target_node_id_before=packet.target_node_id,
                target_node_id_after=transported_packet.target_node_id,
                source_lineage_id_before=packet.source_lineage_id,
                source_lineage_id_after=transported_packet.source_lineage_id,
                target_lineage_id_before=packet.target_lineage_id,
                target_lineage_id_after=transported_packet.target_lineage_id,
                endpoint_transported=endpoint_transported,
                old_parent_port=old_parent_port,
                new_endpoint_port=new_endpoint_port,
                old_parent_column=old_parent_column,
                new_endpoint_column=new_endpoint_column,
            )
        )

    transported_packet_records = tuple(
        transported_packets_by_id.get(packet.packet_id, packet)
        for packet in ledger.packet_records
    )
    transported_queue_records = tuple(
        _updated_queue_event_for_transport(
            event,
            transported_packets_by_id.get(event.packet_id),
        )
        if event.packet_id in transported_packets_by_id
        else event
        for event in ledger.event_queue_records
    )
    transported_ledger = LGRC9V3PacketLedger(
        packet_records=transported_packet_records,
        packet_event_records=ledger.packet_event_records,
        event_queue_records=transported_queue_records,
        node_coherence_total=ledger.node_coherence_total,
        in_flight_packet_total=ledger.in_flight_packet_total,
        conserved_budget_total=ledger.conserved_budget_total,
        budget_before=ledger.conserved_budget_total,
        budget_after=ledger.conserved_budget_total,
        budget_error=0.0,
        fixed_topology_signature=dict(post_topology_signature),
        policies=dict(ledger.policies),
    )
    return LGRC9V3RefinementPacketTransportResult(
        topology_event_id=topology_event_id,
        source_expansion_event_id=source_expansion_event_id,
        source_candidate_event_id=payload.get("source_candidate_event_id"),
        scheduler_event_index=resolved_scheduler_event_index,
        checkpoint_index=resolved_checkpoint_index,
        event_time_key=resolved_event_time_key,
        expanded_node_id=expanded_node_id,
        replacement_node_ids=replacement_node_ids,
        pre_topology_signature=dict(ledger.fixed_topology_signature),
        post_topology_signature=dict(post_topology_signature),
        reassignment_map={str(edge_id): dict(row) for edge_id, row in reassignment_map.items()},
        packet_transport_records=tuple(records),
        transported_ledger=transported_ledger,
        source_packet_ledger_schema_version=LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION,
        source_pending_flux_ledger_schema_version=(
            None
            if pending_flux_ledger is None
            else LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_SCHEMA_VERSION
        ),
        source_pending_flux_entry_ids=tuple(
            sorted({entry_id for ids in pending_ids_by_packet.values() for entry_id in ids})
        ),
        source_packet_ids=tuple(source_packet_ids),
        transported_packet_ids=tuple(transported_packet_ids),
        amount_total=sum(record.amount for record in records),
        budget_before=ledger.conserved_budget_total,
        budget_after=transported_ledger.conserved_budget_total,
        budget_error=transported_ledger.conserved_budget_total - ledger.conserved_budget_total,
    )


def process_lgrc9v3_proper_time_inheritance(
    expansion_event: GRCEvent,
    *,
    parent_node_proper_time: Mapping[NodeId, float],
    explicit_internal_edge_delay: Mapping[EdgeId, float] | None = None,
    tau_0: float = 1.0,
    scheduler_event_index: int | None = None,
    checkpoint_index: int | None = None,
    event_time_key: float | None = None,
) -> LGRC9V3ProperTimeInheritanceResult:
    """Build proper-time inheritance evidence for one refinement event.

    The helper consumes a completed GRC9V3 mechanical-expansion event and the
    parent proper-time surface captured at the refinement event. It returns an
    LGRC-3 evidence artifact under uniform parent proper-time inheritance. It
    does not mutate ``GRC9V3State`` and does not emit identity acceptance.
    """

    if expansion_event.kind != "hybrid_mechanical_expansion":
        raise InvalidStateTransitionError(
            "proper-time inheritance requires a hybrid_mechanical_expansion event"
        )
    payload = expansion_event.payload
    source_expansion_event_id = payload.get("expansion_id")
    if not isinstance(source_expansion_event_id, str) or not source_expansion_event_id:
        raise InvalidStateTransitionError("expansion event missing expansion_id")
    expanded_node_id = int(payload.get("sink_node_id"))
    module_node_ids_raw = payload.get("module_node_ids", [])
    if not isinstance(module_node_ids_raw, list) or not module_node_ids_raw:
        raise InvalidStateTransitionError("expansion event missing module_node_ids")
    replacement_node_ids = tuple(sorted(int(node_id) for node_id in module_node_ids_raw))
    internal_edge_ids_raw = payload.get("internal_edge_ids", [])
    if not isinstance(internal_edge_ids_raw, list) or not internal_edge_ids_raw:
        raise InvalidStateTransitionError("expansion event missing internal_edge_ids")
    internal_edge_ids = tuple(sorted(int(edge_id) for edge_id in internal_edge_ids_raw))

    parent_surface = {
        int(node_id): _nonnegative_float(
            value,
            context=f"parent_node_proper_time[{node_id}]",
        )
        for node_id, value in parent_node_proper_time.items()
    }
    if expanded_node_id not in parent_surface:
        raise InvalidStateTransitionError(
            "parent proper-time surface missing expanded node"
        )
    parent_time = parent_surface[expanded_node_id]

    topology_event_id = build_lgrc9v3_topology_event_id(
        event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
        source_expansion_event_id=source_expansion_event_id,
    )
    records = tuple(
        LGRC9V3ProperTimeInheritanceRecord(
            inheritance_record_id=build_lgrc9v3_proper_time_inheritance_record_id(
                topology_event_id=topology_event_id,
                child_node_id=child_node_id,
            ),
            child_node_id=child_node_id,
            parent_node_id=expanded_node_id,
            parent_proper_time=parent_time,
            child_proper_time=parent_time,
        )
        for child_node_id in replacement_node_ids
    )

    tau_0_value = _positive_float(tau_0, context="tau_0")
    explicit_delays = (
        {}
        if explicit_internal_edge_delay is None
        else {
            int(edge_id): _positive_float(
                value,
                context=f"explicit_internal_edge_delay[{edge_id}]",
            )
            for edge_id, value in explicit_internal_edge_delay.items()
        }
    )
    unknown_explicit_edges = set(explicit_delays) - set(internal_edge_ids)
    if unknown_explicit_edges:
        raise InvalidStateTransitionError(
            f"explicit internal edge delays reference unknown edges: "
            f"{sorted(unknown_explicit_edges)}"
        )
    internal_edge_delay = {
        edge_id: explicit_delays.get(edge_id, tau_0_value)
        for edge_id in internal_edge_ids
    }

    resolved_scheduler_event_index = (
        int(expansion_event.step_index)
        if scheduler_event_index is None
        else int(scheduler_event_index)
    )
    resolved_checkpoint_index = (
        int(expansion_event.step_index) if checkpoint_index is None else int(checkpoint_index)
    )
    if event_time_key is None:
        raw_event_time = payload.get("event_time_key", expansion_event.step_index)
        resolved_event_time_key = _nonnegative_float(
            raw_event_time,
            context="event_time_key",
        )
    else:
        resolved_event_time_key = _nonnegative_float(
            event_time_key,
            context="event_time_key",
        )

    return LGRC9V3ProperTimeInheritanceResult(
        topology_event_id=topology_event_id,
        source_expansion_event_id=source_expansion_event_id,
        source_candidate_event_id=payload.get("source_candidate_event_id"),
        scheduler_event_index=resolved_scheduler_event_index,
        checkpoint_index=resolved_checkpoint_index,
        event_time_key=resolved_event_time_key,
        expanded_node_id=expanded_node_id,
        replacement_node_ids=replacement_node_ids,
        internal_edge_ids=internal_edge_ids,
        proper_time_inheritance_records=records,
        parent_proper_time=parent_time,
        child_proper_time={node_id: parent_time for node_id in replacement_node_ids},
        internal_edge_delay=internal_edge_delay,
        source_parent_proper_time_surface=dict(sorted(parent_surface.items())),
        explicit_internal_edge_delay_provided=explicit_internal_edge_delay is not None,
    )


def _packet_ids_touching_nodes(
    ledger: LGRC9V3PacketLedger | None,
    *,
    node_ids: set[NodeId],
) -> tuple[str, ...]:
    if ledger is None:
        return ()
    return tuple(
        sorted(
            packet.packet_id
            for packet in ledger.packet_records
            if packet.packet_state == LGRC9V3_PACKET_STATE_IN_FLIGHT
            and (
                int(packet.source_node_id) in node_ids
                or int(packet.target_node_id) in node_ids
            )
        )
    )


def _pending_flux_entry_ids_touching_nodes(
    ledger: LGRC9V3PendingFluxLedger | None,
    *,
    node_ids: set[NodeId],
) -> tuple[str, ...]:
    if ledger is None:
        return ()
    return tuple(
        sorted(
            entry.entry_id
            for entry in ledger.pending_flux_entries
            if int(entry.source_node_id) in node_ids
            or int(entry.target_node_id) in node_ids
        )
    )


def process_lgrc9v3_collapse_reabsorption(
    *,
    topology_event_kind: str,
    competing_sink_ids: Sequence[NodeId],
    selected_sink_id: NodeId,
    losing_sink_ids: Sequence[NodeId],
    transferred_node_ids: Sequence[NodeId],
    lineage_transfer_map: Mapping[NodeId, str],
    source_lineage_ids: Mapping[NodeId, str],
    target_lineage_id: str,
    node_proper_time: Mapping[NodeId, float],
    coherence_transfer_amount: float,
    budget_before: float,
    event_time_key: float,
    scheduler_event_index: int,
    checkpoint_index: int,
    packet_ledger: LGRC9V3PacketLedger | None = None,
    pending_flux_ledger: LGRC9V3PendingFluxLedger | None = None,
    budget_after: float | None = None,
    collapse_reabsorption_allowed: bool = False,
    native_route_arbitration_record_id: str | None = None,
    native_route_arbitration_digest: str | None = None,
    native_route_selected_candidate_route_id: str | None = None,
    native_route_selected_candidate_route_digest: str | None = None,
    native_route_candidate_set_digest: str | None = None,
) -> LGRC9V3CollapseReabsorptionResult:
    """Build active LGRC-3 collapse/reabsorption evidence.

    The processor records causal timing, sink selection, explicit lineage
    transfer, and budget-conserving transfer evidence. Packet and pending-flux
    ledgers are consumed only to identify affected in-flight evidence; actual
    packet transport through the lineage map belongs to Iteration 19.
    """

    if not collapse_reabsorption_allowed:
        raise InvalidParamsError(
            "collapse/reabsorption processing requires explicit policy enablement"
        )
    resolved_budget_before = _nonnegative_float(
        budget_before,
        context="budget_before",
    )
    resolved_budget_after = (
        resolved_budget_before
        if budget_after is None
        else _nonnegative_float(budget_after, context="budget_after")
    )
    if abs(resolved_budget_after - resolved_budget_before) > 1e-12:
        raise InvalidStateTransitionError(
            "budget_conserving_transfer requires budget_after == budget_before"
        )

    transferred_nodes = {int(node_id) for node_id in transferred_node_ids}
    losing_nodes = {int(node_id) for node_id in losing_sink_ids}
    affected_nodes = transferred_nodes | losing_nodes
    event_time = _nonnegative_float(event_time_key, context="event_time_key")
    topology_event_id = build_lgrc9v3_collapse_reabsorption_event_id(
        topology_event_kind=topology_event_kind,
        selected_sink_id=selected_sink_id,
        losing_sink_ids=losing_sink_ids,
        event_time_key=event_time,
    )

    return LGRC9V3CollapseReabsorptionResult(
        topology_event_id=topology_event_id,
        topology_event_kind=topology_event_kind,
        scheduler_event_index=int(scheduler_event_index),
        checkpoint_index=int(checkpoint_index),
        event_time_key=event_time,
        node_proper_time=dict(node_proper_time),
        competing_sink_ids=tuple(competing_sink_ids),
        selected_sink_id=selected_sink_id,
        losing_sink_ids=tuple(losing_sink_ids),
        lineage_transfer_map=dict(lineage_transfer_map),
        source_lineage_ids=dict(source_lineage_ids),
        target_lineage_id=target_lineage_id,
        transferred_node_ids=tuple(transferred_node_ids),
        transferred_packet_ids=_packet_ids_touching_nodes(
            packet_ledger,
            node_ids=affected_nodes,
        ),
        transferred_pending_flux_entry_ids=_pending_flux_entry_ids_touching_nodes(
            pending_flux_ledger,
            node_ids=affected_nodes,
        ),
        source_packet_ledger_schema_version=(
            None
            if packet_ledger is None
            else LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION
        ),
        source_pending_flux_ledger_schema_version=(
            None
            if pending_flux_ledger is None
            else LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_SCHEMA_VERSION
        ),
        coherence_transfer_amount=coherence_transfer_amount,
        budget_before=resolved_budget_before,
        budget_after=resolved_budget_after,
        budget_error=resolved_budget_after - resolved_budget_before,
        collapse_reabsorption_allowed=True,
        collapse_reabsorption_processing_implemented=True,
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


def _collapse_endpoint_after(
    node_id: NodeId,
    *,
    lineage_transfer_map: Mapping[NodeId, str],
    selected_sink_id: NodeId,
) -> NodeId:
    if int(node_id) in {int(key) for key in lineage_transfer_map}:
        return int(selected_sink_id)
    return int(node_id)


def _collapse_lineage_after(
    node_id: NodeId,
    previous_lineage: str | None,
    *,
    lineage_transfer_map: Mapping[NodeId, str],
) -> str | None:
    return lineage_transfer_map.get(int(node_id), previous_lineage)


def _updated_pending_flux_entry_for_collapse(
    entry: LGRC9V3PendingFluxEntry,
    *,
    lineage_transfer_map: Mapping[NodeId, str],
    selected_sink_id: NodeId,
) -> tuple[LGRC9V3PendingFluxEntry | None, bool]:
    source_after = _collapse_endpoint_after(
        entry.source_node_id,
        lineage_transfer_map=lineage_transfer_map,
        selected_sink_id=selected_sink_id,
    )
    target_after = _collapse_endpoint_after(
        entry.target_node_id,
        lineage_transfer_map=lineage_transfer_map,
        selected_sink_id=selected_sink_id,
    )
    endpoint_transported = (
        source_after != int(entry.source_node_id)
        or target_after != int(entry.target_node_id)
    )
    if not endpoint_transported:
        return entry, False
    if source_after == target_after == int(selected_sink_id):
        return None, True
    return (
        LGRC9V3PendingFluxEntry(
            entry_id=entry.entry_id,
            source_node_id=source_after,
            target_node_id=target_after,
            edge_id=entry.edge_id,
            arrival_event_time_key=entry.arrival_event_time_key,
            source_lineage_id=_collapse_lineage_after(
                entry.source_node_id,
                entry.source_lineage_id,
                lineage_transfer_map=lineage_transfer_map,
            ),
            target_lineage_id=_collapse_lineage_after(
                entry.target_node_id,
                entry.target_lineage_id,
                lineage_transfer_map=lineage_transfer_map,
            ),
            amount_total=entry.amount_total,
            packet_count=entry.packet_count,
            packet_ids=entry.packet_ids,
            departure_event_time_keys=entry.departure_event_time_keys,
            compaction_policy=entry.compaction_policy,
            transport_ready_for_refinement=entry.transport_ready_for_refinement,
        ),
        True,
    )


def transport_lgrc9v3_packets_through_collapse_reabsorption(
    ledger: LGRC9V3PacketLedger,
    collapse_event: LGRC9V3CollapseReabsorptionResult,
    *,
    pending_flux_ledger: LGRC9V3PendingFluxLedger | None = None,
) -> LGRC9V3CollapsePacketTransportResult:
    """Transport packet evidence through a collapse/reabsorption lineage map.

    Affected in-flight packet endpoints are redirected to the selected sink and
    their lineage ids are updated through the explicit lineage map. If both
    endpoints collapse to the selected sink, the packet is settled into the
    returned ledger's node coherence total and removed from the future queue.
    """

    lineage_transfer_map = dict(collapse_event.lineage_transfer_map)
    selected_sink_id = int(collapse_event.selected_sink_id)
    pending_ids_by_packet = _pending_flux_entry_ids_by_packet(pending_flux_ledger)

    records: list[LGRC9V3PacketTransportRecord] = []
    transported_packets_by_id: dict[str, LGRC9V3PacketRecord] = {}
    settled_packet_ids: list[str] = []
    transported_packet_ids: list[str] = []
    source_packet_ids: list[str] = []
    settled_packet_amount = 0.0
    for packet in sorted(ledger.packet_records, key=_packet_sort_key):
        if packet.packet_state != LGRC9V3_PACKET_STATE_IN_FLIGHT:
            continue
        source_after = _collapse_endpoint_after(
            packet.source_node_id,
            lineage_transfer_map=lineage_transfer_map,
            selected_sink_id=selected_sink_id,
        )
        target_after = _collapse_endpoint_after(
            packet.target_node_id,
            lineage_transfer_map=lineage_transfer_map,
            selected_sink_id=selected_sink_id,
        )
        endpoint_transported = (
            source_after != int(packet.source_node_id)
            or target_after != int(packet.target_node_id)
        )
        if not endpoint_transported:
            continue

        source_packet_ids.append(packet.packet_id)
        source_lineage_after = _collapse_lineage_after(
            packet.source_node_id,
            packet.source_lineage_id,
            lineage_transfer_map=lineage_transfer_map,
        )
        target_lineage_after = _collapse_lineage_after(
            packet.target_node_id,
            packet.target_lineage_id,
            lineage_transfer_map=lineage_transfer_map,
        )
        settled = source_after == target_after == selected_sink_id
        packet_state = (
            LGRC9V3_PACKET_STATE_ARRIVED
            if settled
            else LGRC9V3_PACKET_STATE_IN_FLIGHT
        )
        transported_packet = LGRC9V3PacketRecord(
            packet_id=packet.packet_id,
            packet_state=packet_state,
            source_node_id=source_after,
            target_node_id=target_after,
            edge_id=packet.edge_id,
            amount=packet.amount,
            departure_event_time_key=packet.departure_event_time_key,
            arrival_event_time_key=packet.arrival_event_time_key,
            departure_event_id=packet.departure_event_id,
            arrival_event_id=(
                f"{collapse_event.topology_event_id}:settled:{packet.packet_id}"
                if settled
                else packet.arrival_event_id
            ),
            departure_scheduler_event_index=packet.departure_scheduler_event_index,
            arrival_scheduler_event_index=(
                collapse_event.scheduler_event_index
                if settled
                else packet.arrival_scheduler_event_index
            ),
            source_lineage_id=source_lineage_after,
            target_lineage_id=target_lineage_after,
        )
        transported_packets_by_id[packet.packet_id] = transported_packet
        if settled:
            settled_packet_ids.append(packet.packet_id)
            settled_packet_amount += packet.amount
        else:
            transported_packet_ids.append(packet.packet_id)
        records.append(
            LGRC9V3PacketTransportRecord(
                transport_record_id=build_lgrc9v3_packet_transport_record_id(
                    topology_event_id=collapse_event.topology_event_id,
                    source_packet_id=packet.packet_id,
                ),
                source_packet_id=packet.packet_id,
                transported_packet_id=transported_packet.packet_id,
                source_pending_flux_entry_ids=pending_ids_by_packet.get(
                    packet.packet_id,
                    (),
                ),
                packet_state=packet.packet_state,
                amount=packet.amount,
                edge_id=packet.edge_id,
                source_node_id_before=packet.source_node_id,
                source_node_id_after=transported_packet.source_node_id,
                target_node_id_before=packet.target_node_id,
                target_node_id_after=transported_packet.target_node_id,
                source_lineage_id_before=packet.source_lineage_id,
                source_lineage_id_after=transported_packet.source_lineage_id,
                target_lineage_id_before=packet.target_lineage_id,
                target_lineage_id_after=transported_packet.target_lineage_id,
                endpoint_transported=endpoint_transported,
            )
        )

    transported_packet_records = tuple(
        transported_packets_by_id.get(packet.packet_id, packet)
        for packet in ledger.packet_records
    )
    transported_queue_records = tuple(
        _updated_queue_event_for_transport(
            event,
            transported_packets_by_id.get(event.packet_id),
        )
        if event.packet_id in transported_packets_by_id
        and event.packet_id not in set(settled_packet_ids)
        else event
        for event in ledger.event_queue_records
        if event.packet_id not in set(settled_packet_ids)
    )
    transported_ledger = LGRC9V3PacketLedger(
        packet_records=transported_packet_records,
        packet_event_records=ledger.packet_event_records,
        event_queue_records=transported_queue_records,
        node_coherence_total=ledger.node_coherence_total + settled_packet_amount,
        in_flight_packet_total=ledger.in_flight_packet_total - settled_packet_amount,
        conserved_budget_total=ledger.conserved_budget_total,
        budget_before=ledger.conserved_budget_total,
        budget_after=ledger.conserved_budget_total,
        budget_error=0.0,
        fixed_topology_signature=dict(ledger.fixed_topology_signature),
        policies={
            **dict(ledger.policies),
            "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
            "topology_change_allowed": True,
            "packet_transport_through_topology_change": True,
            "fixed_topology": False,
            "collapse_allowed": True,
        },
        causal_layer_mode=CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        lgrc_runtime_level=LGRC_RUNTIME_LEVEL_LGRC3,
        evidence_class=LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS,
        fixed_topology=False,
        topology_change_allowed=True,
        packet_transport_through_topology_change=True,
        collapse_allowed=True,
    )

    transported_pending_flux_ledger: LGRC9V3PendingFluxLedger | None = None
    source_pending_entry_ids: list[str] = []
    transported_pending_entry_ids: list[str] = []
    settled_pending_entry_ids: list[str] = []
    if pending_flux_ledger is not None:
        pending_entries: list[LGRC9V3PendingFluxEntry] = []
        settled_pending_amount = 0.0
        for entry in pending_flux_ledger.pending_flux_entries:
            updated_entry, touched = _updated_pending_flux_entry_for_collapse(
                entry,
                lineage_transfer_map=lineage_transfer_map,
                selected_sink_id=selected_sink_id,
            )
            if not touched:
                pending_entries.append(entry)
                continue
            source_pending_entry_ids.append(entry.entry_id)
            if updated_entry is None:
                settled_pending_entry_ids.append(entry.entry_id)
                settled_pending_amount += entry.amount_total
            else:
                transported_pending_entry_ids.append(entry.entry_id)
                pending_entries.append(updated_entry)
        transported_pending_flux_ledger = LGRC9V3PendingFluxLedger(
            pending_flux_entries=tuple(pending_entries),
            expanded_packet_count=sum(
                1
                for packet in transported_ledger.packet_records
                if packet.packet_state == LGRC9V3_PACKET_STATE_IN_FLIGHT
            ),
            compact_entry_count=len(pending_entries),
            node_coherence_total=(
                pending_flux_ledger.node_coherence_total + settled_pending_amount
            ),
            in_flight_packet_total=(
                pending_flux_ledger.in_flight_packet_total - settled_pending_amount
            ),
            pending_flux_total=(
                pending_flux_ledger.pending_flux_total - settled_pending_amount
            ),
            conserved_budget_total=pending_flux_ledger.conserved_budget_total,
            budget_before=pending_flux_ledger.conserved_budget_total,
            budget_after=pending_flux_ledger.conserved_budget_total,
            budget_error=0.0,
            fixed_topology_signature=dict(pending_flux_ledger.fixed_topology_signature),
            source_packet_ledger_schema_version=(
                pending_flux_ledger.source_packet_ledger_schema_version
            ),
            policies=dict(pending_flux_ledger.policies),
            compaction_policy=pending_flux_ledger.compaction_policy,
        )

    return LGRC9V3CollapsePacketTransportResult(
        source_topology_event_id=collapse_event.topology_event_id,
        source_topology_event_kind=collapse_event.topology_event_kind,
        scheduler_event_index=collapse_event.scheduler_event_index,
        checkpoint_index=collapse_event.checkpoint_index,
        event_time_key=collapse_event.event_time_key,
        selected_sink_id=selected_sink_id,
        target_lineage_id=collapse_event.target_lineage_id,
        lineage_transfer_map=lineage_transfer_map,
        packet_transport_records=tuple(records),
        transported_ledger=transported_ledger,
        transported_pending_flux_ledger=transported_pending_flux_ledger,
        source_packet_ledger_schema_version=LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION,
        source_pending_flux_ledger_schema_version=(
            None
            if pending_flux_ledger is None
            else LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_SCHEMA_VERSION
        ),
        source_pending_flux_entry_ids=tuple(source_pending_entry_ids),
        transported_pending_flux_entry_ids=tuple(transported_pending_entry_ids),
        settled_pending_flux_entry_ids=tuple(settled_pending_entry_ids),
        source_packet_ids=tuple(source_packet_ids),
        transported_packet_ids=tuple(transported_packet_ids),
        settled_packet_ids=tuple(settled_packet_ids),
        amount_total=sum(record.amount for record in records),
        settled_amount_total=settled_packet_amount,
        budget_before=ledger.conserved_budget_total,
        budget_after=transported_ledger.conserved_budget_total,
        budget_error=transported_ledger.conserved_budget_total - ledger.conserved_budget_total,
    )



def _artifact_string_sequence(
    mapping: Mapping[str, Any],
    *,
    key: str,
) -> tuple[str, ...]:
    raw_values = mapping.get(key, [])
    if not isinstance(raw_values, list):
        raise SnapshotCompatibilityError(f"{key} must be a list")
    return tuple(
        _artifact_string(value, context=f"{key}[]")
        for value in raw_values
    )


def _lineage_ids_from_transport_records(
    records: Sequence[Mapping[str, Any]],
) -> tuple[str, ...]:
    lineage_ids: set[str] = set()
    for record in records:
        mapping = _require_artifact_mapping(record, context="packet_transport_record")
        for key in (
            "source_lineage_id_before",
            "source_lineage_id_after",
            "target_lineage_id_before",
            "target_lineage_id_after",
        ):
            value = mapping.get(key)
            if value is not None:
                lineage_ids.add(_artifact_string(value, context=key))
    return tuple(sorted(lineage_ids))


def _string_values_from_int_keyed_map(
    mapping: Mapping[str, Any],
    *,
    key: str,
) -> tuple[str, ...]:
    raw_mapping = _require_artifact_mapping(mapping.get(key, {}), context=key)
    return tuple(
        sorted(
            _artifact_string(value, context=f"{key}[{raw_key}]")
            for raw_key, value in raw_mapping.items()
        )
    )


def _replay_record_from_mapping(
    mapping: Mapping[str, Any],
) -> LGRC9V3TopologyReplayRecord:
    artifact_kind = mapping.get("artifact_kind")
    if artifact_kind == LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_KIND:
        raw_records = mapping.get("packet_transport_records", [])
        if not isinstance(raw_records, list):
            raise SnapshotCompatibilityError("packet_transport_records must be a list")
        lineage_ids = _lineage_ids_from_transport_records(raw_records)
        if raw_records and not lineage_ids:
            raise InvalidStateTransitionError("refinement replay missing lineage evidence")
        return LGRC9V3TopologyReplayRecord(
            replay_record_id=_artifact_string(
                mapping.get("topology_event_id"),
                context="topology_event_id",
            ),
            record_kind=_artifact_string(mapping.get("artifact_kind"), context="artifact_kind"),
            topology_event_id=_artifact_string(
                mapping.get("topology_event_id"),
                context="topology_event_id",
            ),
            topology_event_kind=_artifact_string(
                mapping.get("topology_event_kind"),
                context="topology_event_kind",
            ),
            event_time_key=_artifact_float(mapping.get("event_time_key"), context="event_time_key"),
            scheduler_event_index=_artifact_int(
                mapping.get("scheduler_event_index"),
                context="scheduler_event_index",
            ),
            checkpoint_index=_artifact_int(
                mapping.get("checkpoint_index"),
                context="checkpoint_index",
            ),
            budget_before=_artifact_float(mapping.get("budget_before"), context="budget_before"),
            budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
            budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
            lineage_ids=lineage_ids,
        )

    if artifact_kind == LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_KIND:
        return LGRC9V3TopologyReplayRecord(
            replay_record_id=_artifact_string(
                mapping.get("topology_event_id"),
                context="topology_event_id",
            ),
            record_kind=_artifact_string(mapping.get("artifact_kind"), context="artifact_kind"),
            topology_event_id=_artifact_string(
                mapping.get("topology_event_id"),
                context="topology_event_id",
            ),
            topology_event_kind=_artifact_string(
                mapping.get("topology_event_kind"),
                context="topology_event_kind",
            ),
            event_time_key=_artifact_float(mapping.get("event_time_key"), context="event_time_key"),
            scheduler_event_index=_artifact_int(
                mapping.get("scheduler_event_index"),
                context="scheduler_event_index",
            ),
            checkpoint_index=_artifact_int(
                mapping.get("checkpoint_index"),
                context="checkpoint_index",
            ),
            budget_before=None,
            budget_after=None,
            budget_error=None,
            lineage_ids=(),
        )

    if artifact_kind == LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_KIND:
        lineage_ids = tuple(
            sorted(
                set(
                    _string_values_from_int_keyed_map(mapping, key="lineage_transfer_map")
                    + _string_values_from_int_keyed_map(mapping, key="source_lineage_ids")
                    + (
                        _artifact_string(
                            mapping.get("target_lineage_id"),
                            context="target_lineage_id",
                        ),
                    )
                )
            )
        )
        if not lineage_ids:
            raise InvalidStateTransitionError("collapse/reabsorption replay missing lineage")
        return LGRC9V3TopologyReplayRecord(
            replay_record_id=_artifact_string(
                mapping.get("topology_event_id"),
                context="topology_event_id",
            ),
            record_kind=_artifact_string(mapping.get("artifact_kind"), context="artifact_kind"),
            topology_event_id=_artifact_string(
                mapping.get("topology_event_id"),
                context="topology_event_id",
            ),
            topology_event_kind=_artifact_string(
                mapping.get("topology_event_kind"),
                context="topology_event_kind",
            ),
            event_time_key=_artifact_float(mapping.get("event_time_key"), context="event_time_key"),
            scheduler_event_index=_artifact_int(
                mapping.get("scheduler_event_index"),
                context="scheduler_event_index",
            ),
            checkpoint_index=_artifact_int(
                mapping.get("checkpoint_index"),
                context="checkpoint_index",
            ),
            budget_before=_artifact_float(mapping.get("budget_before"), context="budget_before"),
            budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
            budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
            lineage_ids=lineage_ids,
        )

    if artifact_kind == LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_KIND:
        raw_records = mapping.get("packet_transport_records", [])
        if not isinstance(raw_records, list):
            raise SnapshotCompatibilityError("packet_transport_records must be a list")
        lineage_ids = tuple(
            sorted(
                set(
                    _string_values_from_int_keyed_map(mapping, key="lineage_transfer_map")
                    + (
                        _artifact_string(
                            mapping.get("target_lineage_id"),
                            context="target_lineage_id",
                        ),
                    )
                    + _lineage_ids_from_transport_records(raw_records)
                )
            )
        )
        if not lineage_ids:
            raise InvalidStateTransitionError("collapse packet replay missing lineage")
        return LGRC9V3TopologyReplayRecord(
            replay_record_id=(
                "collapse-packet-transport:"
                + _artifact_string(
                    mapping.get("source_topology_event_id"),
                    context="source_topology_event_id",
                )
            ),
            record_kind=_artifact_string(mapping.get("artifact_kind"), context="artifact_kind"),
            topology_event_id=_artifact_string(
                mapping.get("source_topology_event_id"),
                context="source_topology_event_id",
            ),
            topology_event_kind=_artifact_string(
                mapping.get("source_topology_event_kind"),
                context="source_topology_event_kind",
            ),
            event_time_key=_artifact_float(mapping.get("event_time_key"), context="event_time_key"),
            scheduler_event_index=_artifact_int(
                mapping.get("scheduler_event_index"),
                context="scheduler_event_index",
            ),
            checkpoint_index=_artifact_int(
                mapping.get("checkpoint_index"),
                context="checkpoint_index",
            ),
            budget_before=_artifact_float(mapping.get("budget_before"), context="budget_before"),
            budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
            budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
            lineage_ids=lineage_ids,
            source_topology_event_ids=(
                _artifact_string(
                    mapping.get("source_topology_event_id"),
                    context="source_topology_event_id",
                ),
            ),
            creates_topology_event=False,
        )

    if artifact_kind == LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND:
        lineage_id = _artifact_string(mapping.get("lineage_id"), context="lineage_id")
        return LGRC9V3TopologyReplayRecord(
            replay_record_id=_artifact_string(
                mapping.get("evaluation_id"),
                context="evaluation_id",
            ),
            record_kind=_artifact_string(mapping.get("artifact_kind"), context="artifact_kind"),
            topology_event_id=_artifact_string(
                mapping.get("topology_event_id"),
                context="topology_event_id",
            ),
            topology_event_kind=_artifact_string(
                mapping.get("topology_event_kind"),
                context="topology_event_kind",
            ),
            event_time_key=_artifact_float(mapping.get("event_time_key"), context="event_time_key"),
            scheduler_event_index=_artifact_int(
                mapping.get("scheduler_event_index"),
                context="scheduler_event_index",
            ),
            checkpoint_index=_artifact_int(
                mapping.get("checkpoint_index"),
                context="checkpoint_index",
            ),
            budget_before=_artifact_float(mapping.get("budget_before"), context="budget_before"),
            budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
            budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
            lineage_ids=(lineage_id,),
            source_topology_event_ids=_artifact_string_sequence(
                mapping,
                key="source_topology_event_ids",
            ),
            creates_topology_event=False,
        )

    raise SnapshotCompatibilityError(
        f"unsupported LGRC9V3 replay artifact kind: {artifact_kind!r}"
    )


def _identity_acceptance_event_payload(item: GRCEvent | Mapping[str, Any]) -> Mapping[str, Any] | None:
    if isinstance(item, GRCEvent):
        if item.kind != LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE:
            return None
        return item.payload
    if isinstance(item, Mapping) and item.get("kind") == (
        LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE
    ):
        return _require_artifact_mapping(item.get("payload"), context="payload")
    if isinstance(item, Mapping) and item.get("topology_event_kind") == (
        LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE
    ):
        return item
    return None


def _replay_record_from_identity_acceptance(
    item: GRCEvent | Mapping[str, Any],
) -> LGRC9V3TopologyReplayRecord | None:
    payload = _identity_acceptance_event_payload(item)
    if payload is None:
        return None
    lineage_id = _artifact_string(payload.get("lineage_id"), context="lineage_id")
    return LGRC9V3TopologyReplayRecord(
        replay_record_id=_artifact_string(payload.get("event_id"), context="event_id"),
        record_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
        topology_event_id=_artifact_string(
            payload.get("topology_event_id"),
            context="topology_event_id",
        ),
        topology_event_kind=_artifact_string(
            payload.get("topology_event_kind"),
            context="topology_event_kind",
        ),
        event_time_key=_artifact_float(payload.get("event_time_key"), context="event_time_key"),
        scheduler_event_index=_artifact_int(
            payload.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        checkpoint_index=_artifact_int(
            payload.get("checkpoint_index"),
            context="checkpoint_index",
        ),
        budget_before=_artifact_float(payload.get("budget_before"), context="budget_before"),
        budget_after=_artifact_float(payload.get("budget_after"), context="budget_after"),
        budget_error=_artifact_float(payload.get("budget_error"), context="budget_error"),
        lineage_ids=(lineage_id,),
        source_topology_event_ids=_artifact_string_sequence(
            payload,
            key="source_topology_event_ids",
        ),
        source_identity_evaluation_id=_artifact_string(
            payload.get("source_identity_evaluation_id"),
            context="source_identity_evaluation_id",
        ),
        identity_acceptance_emitted=_artifact_bool(
            payload.get("identity_acceptance_emitted"),
            context="identity_acceptance_emitted",
        ),
        creates_topology_event=True,
    )


def _topology_replay_record_from_item(
    item: Mapping[str, Any] | GRCEvent,
) -> LGRC9V3TopologyReplayRecord:
    identity_record = _replay_record_from_identity_acceptance(item)
    if identity_record is not None:
        return identity_record
    if not isinstance(item, Mapping):
        raise SnapshotCompatibilityError("replay items must be artifacts or GRCEvents")
    return _replay_record_from_mapping(item)


def validate_lgrc9v3_topology_event_replay(
    replay_items: Sequence[Mapping[str, Any] | GRCEvent],
) -> LGRC9V3TopologyReplayValidationResult:
    """Validate LGRC-3 topology/evidence replay ordering, lineage, and budget."""

    if not replay_items:
        raise InvalidStateTransitionError("topology replay requires at least one item")
    records = tuple(_topology_replay_record_from_item(item) for item in replay_items)

    seen_topology_event_ids: set[str] = set()
    seen_identity_evaluation_ids: set[str] = set()
    previous_event_time_key = -math.inf
    previous_budget_after: float | None = None
    start_budget: float | None = None
    end_budget: float | None = None

    for record in records:
        if record.event_time_key < previous_event_time_key:
            raise InvalidStateTransitionError(
                "LGRC-3 replay violates event-time ordering"
            )
        previous_event_time_key = record.event_time_key

        for source_topology_event_id in record.source_topology_event_ids:
            if source_topology_event_id not in seen_topology_event_ids:
                raise InvalidStateTransitionError(
                    "LGRC-3 replay violates lineage continuity: "
                    f"unknown source topology event {source_topology_event_id!r}"
                )

        if record.source_identity_evaluation_id is not None:
            if record.source_identity_evaluation_id not in seen_identity_evaluation_ids:
                raise InvalidStateTransitionError(
                    "LGRC-3 replay violates lineage continuity: "
                    "unknown identity evaluation"
                )

        if (
            record.record_kind
            == LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND
        ):
            seen_identity_evaluation_ids.add(record.replay_record_id)

        if record.creates_topology_event:
            seen_topology_event_ids.add(record.topology_event_id)

        if record.budget_before is not None:
            assert record.budget_after is not None
            if previous_budget_after is not None:
                if abs(record.budget_before - previous_budget_after) > 1e-12:
                    raise InvalidStateTransitionError(
                        "LGRC-3 replay budget continuity mismatch"
                    )
            if start_budget is None:
                start_budget = record.budget_before
            previous_budget_after = record.budget_after
            end_budget = record.budget_after

    budget_error = None
    if start_budget is not None and end_budget is not None:
        budget_error = end_budget - start_budget
        if abs(budget_error) > 1e-12:
            raise InvalidStateTransitionError(
                "LGRC-3 replay does not conserve budget"
            )

    return LGRC9V3TopologyReplayValidationResult(
        replay_records=records,
        start_budget=start_budget,
        end_budget=end_budget,
        budget_error=budget_error,
        accepted_artifact_count=len(records),
    )



def restore_lgrc9v3_lgrc3_policy_contract_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3CollapseIdentityPolicyContract | None:
    """Restore an LGRC-3 collapse/identity policy contract artifact."""

    mapping = _require_artifact_mapping(artifact, context="lgrc3_policy_contract")
    if mapping.get("artifact_kind") != LGRC9V3_LGRC3_POLICY_CONTRACT_KIND:
        return None
    schema_version = _artifact_string(
        mapping.get("artifact_schema_version"),
        context="artifact_schema_version",
    )
    if schema_version != LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION:
        raise SnapshotCompatibilityError(
            "unsupported LGRC9V3 LGRC-3 policy contract schema version"
        )
    contract_fields = {
        "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "evidence_class": LGRC9V3_LGRC3_POLICY_CONTRACT_EVIDENCE_CLASS,
        "collapse_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        "reabsorption_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
        "identity_acceptance_event_kind": (
            LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE
        ),
    }
    for key, expected in contract_fields.items():
        actual = _artifact_string(mapping.get(key), context=key)
        if actual != expected:
            raise SnapshotCompatibilityError(f"{key} must be {expected!r}")
    if not _artifact_bool(mapping.get("contract_only"), context="contract_only"):
        raise SnapshotCompatibilityError("contract_only must be true")
    for key in (
        "collapse_reabsorption_processing_implemented",
        "proper_time_identity_processing_implemented",
        "mechanical_expansion_is_identity_acceptance",
        "refinement_packet_transport_is_identity_transfer",
    ):
        if _artifact_bool(mapping.get(key), context=key):
            raise SnapshotCompatibilityError(f"{key} must be false")

    collapse_required = mapping.get("collapse_reabsorption_required_fields", [])
    identity_required = mapping.get("proper_time_identity_required_fields", [])
    if not isinstance(collapse_required, list) or not isinstance(identity_required, list):
        raise SnapshotCompatibilityError("required field lists must be lists")
    if set(collapse_required) != LGRC9V3_COLLAPSE_REABSORPTION_REQUIRED_FIELDS:
        raise SnapshotCompatibilityError(
            "collapse/reabsorption required fields do not match contract"
        )
    if set(identity_required) != LGRC9V3_PROPER_TIME_IDENTITY_REQUIRED_FIELDS:
        raise SnapshotCompatibilityError(
            "proper-time identity required fields do not match contract"
        )

    return LGRC9V3CollapseIdentityPolicyContract(
        collapse_reabsorption_allowed=_artifact_bool(
            mapping.get("collapse_reabsorption_allowed"),
            context="collapse_reabsorption_allowed",
        ),
        identity_acceptance_allowed=_artifact_bool(
            mapping.get("identity_acceptance_allowed"),
            context="identity_acceptance_allowed",
        ),
        collapse_reabsorption_processing_implemented=False,
        proper_time_identity_processing_implemented=False,
        proper_time_transfer_policy=_artifact_string(
            mapping.get("proper_time_transfer_policy"),
            context="proper_time_transfer_policy",
        ),
        lineage_transfer_policy=_artifact_string(
            mapping.get("lineage_transfer_policy"),
            context="lineage_transfer_policy",
        ),
        budget_transfer_policy=_artifact_string(
            mapping.get("budget_transfer_policy"),
            context="budget_transfer_policy",
        ),
        identity_clock_policy=_artifact_string(
            mapping.get("identity_clock_policy"),
            context="identity_clock_policy",
        ),
        identity_threshold_calibration_policy=_artifact_string(
            mapping.get("identity_threshold_calibration_policy"),
            context="identity_threshold_calibration_policy",
        ),
        identity_threshold_multiplier=_artifact_float(
            mapping.get("identity_threshold_multiplier"),
            context="identity_threshold_multiplier",
        ),
    )


def restore_lgrc9v3_proper_time_inheritance_record(
    record: Mapping[str, Any],
) -> LGRC9V3ProperTimeInheritanceRecord:
    """Restore one proper-time inheritance record from JSON-compatible data."""

    mapping = _require_artifact_mapping(record, context="proper_time_inheritance_record")
    return LGRC9V3ProperTimeInheritanceRecord(
        inheritance_record_id=_artifact_string(
            mapping.get("inheritance_record_id"),
            context="inheritance_record_id",
        ),
        child_node_id=_artifact_int(
            mapping.get("child_node_id"),
            context="child_node_id",
        ),
        parent_node_id=_artifact_int(
            mapping.get("parent_node_id"),
            context="parent_node_id",
        ),
        parent_proper_time=_artifact_float(
            mapping.get("parent_proper_time"),
            context="parent_proper_time",
        ),
        child_proper_time=_artifact_float(
            mapping.get("child_proper_time"),
            context="child_proper_time",
        ),
        proper_time_inheritance_policy=_artifact_string(
            mapping.get("proper_time_inheritance_policy"),
            context="proper_time_inheritance_policy",
        ),
    )


def restore_lgrc9v3_proper_time_inheritance_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3ProperTimeInheritanceResult | None:
    """Restore an LGRC-3 proper-time inheritance artifact, or ``None``."""

    mapping = _require_artifact_mapping(artifact, context="proper_time_inheritance")
    if mapping.get("artifact_kind") != LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_KIND:
        return None
    schema_version = _artifact_string(
        mapping.get("artifact_schema_version"),
        context="artifact_schema_version",
    )
    if schema_version != LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_SCHEMA_VERSION:
        raise SnapshotCompatibilityError(
            "unsupported LGRC9V3 proper-time inheritance schema version"
        )
    contract_fields = {
        "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "evidence_class": LGRC9V3_PROPER_TIME_INHERITANCE_EVIDENCE_CLASS,
        "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
        "proper_time_inheritance_policy": (
            LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT
        ),
        "internal_edge_delay_policy": (
            LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0
        ),
    }
    for key, expected in contract_fields.items():
        actual = _artifact_string(mapping.get(key), context=key)
        if actual != expected:
            raise SnapshotCompatibilityError(f"{key} must be {expected!r}")
    if _artifact_bool(
        mapping.get("identity_acceptance_emitted"),
        context="identity_acceptance_emitted",
    ):
        raise SnapshotCompatibilityError(
            "proper-time inheritance must not emit identity acceptance"
        )
    if _artifact_bool(
        mapping.get("refinement_lineage_identity_persistence"),
        context="refinement_lineage_identity_persistence",
    ):
        raise SnapshotCompatibilityError(
            "proper-time inheritance must not claim identity persistence"
        )
    records_raw = mapping.get("proper_time_inheritance_records", [])
    if not isinstance(records_raw, list):
        raise SnapshotCompatibilityError("proper_time_inheritance_records must be a list")
    return LGRC9V3ProperTimeInheritanceResult(
        topology_event_id=_artifact_string(
            mapping.get("topology_event_id"),
            context="topology_event_id",
        ),
        source_expansion_event_id=_artifact_string(
            mapping.get("source_expansion_event_id"),
            context="source_expansion_event_id",
        ),
        source_candidate_event_id=_artifact_optional_string(
            mapping.get("source_candidate_event_id"),
            context="source_candidate_event_id",
        ),
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
        expanded_node_id=_artifact_int(
            mapping.get("expanded_node_id"),
            context="expanded_node_id",
        ),
        replacement_node_ids=tuple(
            _artifact_int(node_id, context="replacement_node_ids[]")
            for node_id in mapping.get("replacement_node_ids", [])
        ),
        internal_edge_ids=tuple(
            _artifact_int(edge_id, context="internal_edge_ids[]")
            for edge_id in mapping.get("internal_edge_ids", [])
        ),
        proper_time_inheritance_records=tuple(
            restore_lgrc9v3_proper_time_inheritance_record(record)
            for record in records_raw
        ),
        parent_proper_time=_artifact_float(
            mapping.get("parent_proper_time"),
            context="parent_proper_time",
        ),
        child_proper_time=_parse_artifact_float_map(mapping, key="child_proper_time"),
        internal_edge_delay=_parse_artifact_float_map(
            mapping,
            key="internal_edge_delay",
        ),
        source_parent_proper_time_surface=_parse_artifact_float_map(
            mapping,
            key="source_parent_proper_time_surface",
        ),
        explicit_internal_edge_delay_provided=_artifact_bool(
            mapping.get("explicit_internal_edge_delay_provided"),
            context="explicit_internal_edge_delay_provided",
        ),
        state_mutated=_artifact_bool(mapping.get("state_mutated"), context="state_mutated"),
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
        identity_acceptance_emitted=False,
        refinement_lineage_identity_persistence=False,
    )


def restore_lgrc9v3_collapse_reabsorption_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3CollapseReabsorptionResult | None:
    """Restore an LGRC-3 collapse/reabsorption artifact, or ``None``."""

    mapping = _require_artifact_mapping(artifact, context="collapse_reabsorption")
    if mapping.get("artifact_kind") != LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_KIND:
        return None
    schema_version = _artifact_string(
        mapping.get("artifact_schema_version"),
        context="artifact_schema_version",
    )
    if schema_version != LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_SCHEMA_VERSION:
        raise SnapshotCompatibilityError(
            "unsupported LGRC9V3 collapse/reabsorption schema version"
        )
    contract_fields = {
        "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "evidence_class": LGRC9V3_COLLAPSE_REABSORPTION_EVIDENCE_CLASS,
        "budget_transfer_policy": LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING,
        "lineage_transfer_policy": LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP,
        "proper_time_transfer_policy": (
            LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY
        ),
    }
    for key, expected in contract_fields.items():
        actual = _artifact_string(mapping.get(key), context=key)
        if actual != expected:
            raise SnapshotCompatibilityError(f"{key} must be {expected!r}")
    for key in (
        "collapse_reabsorption_allowed",
        "collapse_reabsorption_processing_implemented",
    ):
        if not _artifact_bool(mapping.get(key), context=key):
            raise SnapshotCompatibilityError(f"{key} must be true")
    for key in (
        "state_mutated",
        "topology_mutated",
        "packet_transport_emitted",
        "identity_acceptance_emitted",
    ):
        if _artifact_bool(mapping.get(key), context=key):
            raise SnapshotCompatibilityError(f"{key} must be false")

    list_fields = (
        "competing_sink_ids",
        "losing_sink_ids",
        "transferred_node_ids",
        "transferred_packet_ids",
        "transferred_pending_flux_entry_ids",
    )
    for key in list_fields:
        if not isinstance(mapping.get(key, []), list):
            raise SnapshotCompatibilityError(f"{key} must be a list")

    return LGRC9V3CollapseReabsorptionResult(
        topology_event_id=_artifact_string(
            mapping.get("topology_event_id"),
            context="topology_event_id",
        ),
        topology_event_kind=_artifact_string(
            mapping.get("topology_event_kind"),
            context="topology_event_kind",
        ),
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
        node_proper_time=_parse_artifact_float_map(mapping, key="node_proper_time"),
        competing_sink_ids=tuple(
            _artifact_int(node_id, context="competing_sink_ids[]")
            for node_id in mapping.get("competing_sink_ids", [])
        ),
        selected_sink_id=_artifact_int(
            mapping.get("selected_sink_id"),
            context="selected_sink_id",
        ),
        losing_sink_ids=tuple(
            _artifact_int(node_id, context="losing_sink_ids[]")
            for node_id in mapping.get("losing_sink_ids", [])
        ),
        lineage_transfer_map=_parse_artifact_string_map(
            mapping,
            key="lineage_transfer_map",
        ),
        source_lineage_ids=_parse_artifact_string_map(
            mapping,
            key="source_lineage_ids",
        ),
        target_lineage_id=_artifact_string(
            mapping.get("target_lineage_id"),
            context="target_lineage_id",
        ),
        transferred_node_ids=tuple(
            _artifact_int(node_id, context="transferred_node_ids[]")
            for node_id in mapping.get("transferred_node_ids", [])
        ),
        transferred_packet_ids=tuple(
            _artifact_string(packet_id, context="transferred_packet_ids[]")
            for packet_id in mapping.get("transferred_packet_ids", [])
        ),
        transferred_pending_flux_entry_ids=tuple(
            _artifact_string(
                entry_id,
                context="transferred_pending_flux_entry_ids[]",
            )
            for entry_id in mapping.get("transferred_pending_flux_entry_ids", [])
        ),
        source_packet_ledger_schema_version=_artifact_optional_string(
            mapping.get("source_packet_ledger_schema_version"),
            context="source_packet_ledger_schema_version",
        ),
        source_pending_flux_ledger_schema_version=_artifact_optional_string(
            mapping.get("source_pending_flux_ledger_schema_version"),
            context="source_pending_flux_ledger_schema_version",
        ),
        coherence_transfer_amount=_artifact_float(
            mapping.get("coherence_transfer_amount"),
            context="coherence_transfer_amount",
        ),
        budget_before=_artifact_float(
            mapping.get("budget_before"),
            context="budget_before",
        ),
        budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
        budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
        collapse_reabsorption_allowed=True,
        collapse_reabsorption_processing_implemented=True,
    )


def restore_lgrc9v3_packet_transport_record(
    record: Mapping[str, Any],
) -> LGRC9V3PacketTransportRecord:
    """Restore one packet transport audit row from JSON-compatible data."""

    mapping = _require_artifact_mapping(record, context="packet_transport_record")
    raw_entry_ids = mapping.get("source_pending_flux_entry_ids", [])
    if not isinstance(raw_entry_ids, list):
        raise SnapshotCompatibilityError(
            "source_pending_flux_entry_ids must be a list"
        )
    return LGRC9V3PacketTransportRecord(
        transport_record_id=_artifact_string(
            mapping.get("transport_record_id"),
            context="transport_record_id",
        ),
        source_packet_id=_artifact_string(
            mapping.get("source_packet_id"),
            context="source_packet_id",
        ),
        transported_packet_id=_artifact_string(
            mapping.get("transported_packet_id"),
            context="transported_packet_id",
        ),
        source_pending_flux_entry_ids=tuple(
            _artifact_string(entry_id, context="source_pending_flux_entry_ids[]")
            for entry_id in raw_entry_ids
        ),
        packet_state=_artifact_string(mapping.get("packet_state"), context="packet_state"),
        amount=_artifact_float(mapping.get("amount"), context="amount"),
        edge_id=_artifact_int(mapping.get("edge_id"), context="edge_id"),
        source_node_id_before=_artifact_int(
            mapping.get("source_node_id_before"),
            context="source_node_id_before",
        ),
        source_node_id_after=_artifact_int(
            mapping.get("source_node_id_after"),
            context="source_node_id_after",
        ),
        target_node_id_before=_artifact_int(
            mapping.get("target_node_id_before"),
            context="target_node_id_before",
        ),
        target_node_id_after=_artifact_int(
            mapping.get("target_node_id_after"),
            context="target_node_id_after",
        ),
        source_lineage_id_before=_artifact_optional_string(
            mapping.get("source_lineage_id_before"),
            context="source_lineage_id_before",
        ),
        source_lineage_id_after=_artifact_optional_string(
            mapping.get("source_lineage_id_after"),
            context="source_lineage_id_after",
        ),
        target_lineage_id_before=_artifact_optional_string(
            mapping.get("target_lineage_id_before"),
            context="target_lineage_id_before",
        ),
        target_lineage_id_after=_artifact_optional_string(
            mapping.get("target_lineage_id_after"),
            context="target_lineage_id_after",
        ),
        endpoint_transported=_artifact_bool(
            mapping.get("endpoint_transported"),
            context="endpoint_transported",
        ),
        old_parent_port=None
        if mapping.get("old_parent_port") is None
        else _artifact_int(mapping.get("old_parent_port"), context="old_parent_port"),
        new_endpoint_port=None
        if mapping.get("new_endpoint_port") is None
        else _artifact_int(mapping.get("new_endpoint_port"), context="new_endpoint_port"),
        old_parent_column=None
        if mapping.get("old_parent_column") is None
        else _artifact_int(mapping.get("old_parent_column"), context="old_parent_column"),
        new_endpoint_column=None
        if mapping.get("new_endpoint_column") is None
        else _artifact_int(mapping.get("new_endpoint_column"), context="new_endpoint_column"),
    )


def restore_lgrc9v3_collapse_packet_transport_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3CollapsePacketTransportResult | None:
    """Restore a collapse/reabsorption packet-transport artifact, or ``None``."""

    mapping = _require_artifact_mapping(artifact, context="collapse_packet_transport")
    if mapping.get("artifact_kind") != LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_KIND:
        return None
    schema_version = _artifact_string(
        mapping.get("artifact_schema_version"),
        context="artifact_schema_version",
    )
    if schema_version != LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION:
        raise SnapshotCompatibilityError(
            "unsupported LGRC9V3 collapse packet transport schema version"
        )
    contract_fields = {
        "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "evidence_class": LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS,
        "transport_policy": (
            LGRC9V3_COLLAPSE_PACKET_TRANSPORT_POLICY_REDIRECT_OR_SETTLE
        ),
    }
    for key, expected in contract_fields.items():
        actual = _artifact_string(mapping.get(key), context=key)
        if actual != expected:
            raise SnapshotCompatibilityError(f"{key} must be {expected!r}")
    for key in (
        "state_mutated",
        "topology_mutated",
        "identity_acceptance_emitted",
        "packet_transport_identity_transfer",
    ):
        if _artifact_bool(mapping.get(key), context=key):
            raise SnapshotCompatibilityError(f"{key} must be false")

    list_fields = (
        "source_pending_flux_entry_ids",
        "transported_pending_flux_entry_ids",
        "settled_pending_flux_entry_ids",
        "source_packet_ids",
        "transported_packet_ids",
        "settled_packet_ids",
        "packet_transport_records",
    )
    for key in list_fields:
        if not isinstance(mapping.get(key, []), list):
            raise SnapshotCompatibilityError(f"{key} must be a list")
    transported_ledger = restore_lgrc9v3_packet_ledger_artifact(
        _require_artifact_mapping(
            mapping.get("transported_ledger"),
            context="transported_ledger",
        )
    )
    if transported_ledger is None:
        raise SnapshotCompatibilityError("transported_ledger is required")
    pending_block = mapping.get("transported_pending_flux_ledger")
    transported_pending_ledger = (
        None
        if pending_block is None
        else restore_lgrc9v3_pending_flux_ledger_artifact(
            _require_artifact_mapping(
                pending_block,
                context="transported_pending_flux_ledger",
            )
        )
    )
    return LGRC9V3CollapsePacketTransportResult(
        source_topology_event_id=_artifact_string(
            mapping.get("source_topology_event_id"),
            context="source_topology_event_id",
        ),
        source_topology_event_kind=_artifact_string(
            mapping.get("source_topology_event_kind"),
            context="source_topology_event_kind",
        ),
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
        selected_sink_id=_artifact_int(
            mapping.get("selected_sink_id"),
            context="selected_sink_id",
        ),
        target_lineage_id=_artifact_string(
            mapping.get("target_lineage_id"),
            context="target_lineage_id",
        ),
        lineage_transfer_map=_parse_artifact_string_map(
            mapping,
            key="lineage_transfer_map",
        ),
        packet_transport_records=tuple(
            restore_lgrc9v3_packet_transport_record(record)
            for record in mapping.get("packet_transport_records", [])
        ),
        transported_ledger=transported_ledger,
        transported_pending_flux_ledger=transported_pending_ledger,
        source_packet_ledger_schema_version=_artifact_string(
            mapping.get("source_packet_ledger_schema_version"),
            context="source_packet_ledger_schema_version",
        ),
        source_pending_flux_ledger_schema_version=_artifact_optional_string(
            mapping.get("source_pending_flux_ledger_schema_version"),
            context="source_pending_flux_ledger_schema_version",
        ),
        source_pending_flux_entry_ids=tuple(
            _artifact_string(entry_id, context="source_pending_flux_entry_ids[]")
            for entry_id in mapping.get("source_pending_flux_entry_ids", [])
        ),
        transported_pending_flux_entry_ids=tuple(
            _artifact_string(entry_id, context="transported_pending_flux_entry_ids[]")
            for entry_id in mapping.get("transported_pending_flux_entry_ids", [])
        ),
        settled_pending_flux_entry_ids=tuple(
            _artifact_string(entry_id, context="settled_pending_flux_entry_ids[]")
            for entry_id in mapping.get("settled_pending_flux_entry_ids", [])
        ),
        source_packet_ids=tuple(
            _artifact_string(packet_id, context="source_packet_ids[]")
            for packet_id in mapping.get("source_packet_ids", [])
        ),
        transported_packet_ids=tuple(
            _artifact_string(packet_id, context="transported_packet_ids[]")
            for packet_id in mapping.get("transported_packet_ids", [])
        ),
        settled_packet_ids=tuple(
            _artifact_string(packet_id, context="settled_packet_ids[]")
            for packet_id in mapping.get("settled_packet_ids", [])
        ),
        amount_total=_artifact_float(mapping.get("amount_total"), context="amount_total"),
        settled_amount_total=_artifact_float(
            mapping.get("settled_amount_total"),
            context="settled_amount_total",
        ),
        budget_before=_artifact_float(mapping.get("budget_before"), context="budget_before"),
        budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
        budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
    )


__all__ = [
    'LGRC9V3CollapseIdentityPolicyContract',
    'LGRC9V3CollapsePacketTransportResult',
    'LGRC9V3CollapseReabsorptionFieldNames',
    'LGRC9V3CollapseReabsorptionResult',
    'LGRC9V3PacketTransportFieldNames',
    'LGRC9V3PacketTransportRecord',
    'LGRC9V3ProperTimeInheritanceRecord',
    'LGRC9V3ProperTimeInheritanceResult',
    'LGRC9V3RefinementPacketTransportResult',
    'LGRC9V3TopologyContractFieldNames',
    'LGRC9V3TopologyReplayRecord',
    'LGRC9V3TopologyReplayValidationResult',
    'LGRC9V3_BUDGET_TRANSFER_POLICIES',
    'LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING',
    'LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS',
    'LGRC9V3_COLLAPSE_PACKET_TRANSPORT_POLICY_REDIRECT_OR_SETTLE',
    'LGRC9V3_COLLAPSE_REABSORPTION_EVIDENCE_CLASS',
    'LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES',
    'LGRC9V3_COLLAPSE_REABSORPTION_REQUIRED_FIELDS',
    'LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER',
    'LGRC9V3_IDENTITY_CLOCK_POLICIES',
    'LGRC9V3_IDENTITY_CLOCK_POLICY_BASIN_AGGREGATE',
    'LGRC9V3_IDENTITY_CLOCK_POLICY_CAUSAL_FRONTIER',
    'LGRC9V3_IDENTITY_CLOCK_POLICY_LINEAGE',
    'LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL',
    'LGRC9V3_IDENTITY_THRESHOLD_POLICIES',
    'LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY',
    'LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0',
    'LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_KIND',
    'LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_KIND',
    'LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_KIND',
    'LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_POLICY_CONTRACT_EVIDENCE_CLASS',
    'LGRC9V3_LGRC3_POLICY_CONTRACT_KIND',
    'LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_KIND',
    'LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_KIND',
    'LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_IN_SCOPE',
    'LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_OUT_OF_SCOPE',
    'LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_KIND',
    'LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_SCHEMA_VERSION',
    'LGRC9V3_LINEAGE_TRANSFER_POLICIES',
    'LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP',
    'LGRC9V3_PACKET_TRANSPORT_EVIDENCE_CLASS',
    'LGRC9V3_PACKET_TRANSPORT_FIELD_NAMES',
    'LGRC9V3_PACKET_TRANSPORT_REQUIRED_FIELDS',
    'LGRC9V3_PROPER_TIME_INHERITANCE_EVIDENCE_CLASS',
    'LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT',
    'LGRC9V3_PROPER_TIME_INHERITANCE_REQUIRED_FIELDS',
    'LGRC9V3_PROPER_TIME_TRANSFER_POLICIES',
    'LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY',
    'LGRC9V3_REFINEMENT_LINEAGE_REQUIRED_FIELDS',
    'LGRC9V3_TOPOLOGY_CONTRACT_EVIDENCE_CLASS',
    'LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_BOUNDARY_BIRTH',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT',
    'LGRC9V3_TOPOLOGY_REPLAY_VALIDATION_EVIDENCE_CLASS',
    '_artifact_string_sequence',
    '_collapse_endpoint_after',
    '_collapse_lineage_after',
    '_identity_acceptance_event_payload',
    '_lineage_after_refinement',
    '_lineage_ids_from_transport_records',
    '_packet_ids_touching_nodes',
    '_pending_flux_entry_ids_by_packet',
    '_pending_flux_entry_ids_touching_nodes',
    '_replay_record_from_identity_acceptance',
    '_replay_record_from_mapping',
    '_string_values_from_int_keyed_map',
    '_topology_replay_record_from_item',
    '_transport_record_sort_key',
    '_updated_pending_flux_entry_for_collapse',
    '_updated_queue_event_for_transport',
    'build_lgrc9v3_collapse_reabsorption_event_id',
    'build_lgrc9v3_lgrc3_policy_contract_artifact',
    'build_lgrc9v3_packet_transport_record_id',
    'build_lgrc9v3_proper_time_inheritance_record_id',
    'build_lgrc9v3_topology_contract_artifact',
    'build_lgrc9v3_topology_event_id',
    'process_lgrc9v3_collapse_reabsorption',
    'process_lgrc9v3_proper_time_inheritance',
    'restore_lgrc9v3_collapse_packet_transport_artifact',
    'restore_lgrc9v3_collapse_reabsorption_artifact',
    'restore_lgrc9v3_lgrc3_policy_contract_artifact',
    'restore_lgrc9v3_packet_transport_record',
    'restore_lgrc9v3_proper_time_inheritance_artifact',
    'restore_lgrc9v3_proper_time_inheritance_record',
    'transport_lgrc9v3_packets_through_collapse_reabsorption',
    'transport_lgrc9v3_packets_through_refinement',
    'validate_lgrc9v3_topology_event_replay',
]
