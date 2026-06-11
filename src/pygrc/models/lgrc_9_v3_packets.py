"""LGRC9V3 packet records, ledgers, queue events, and packet processors."""

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


def _packet_sort_key(packet: "LGRC9V3PacketRecord") -> tuple[str, str]:
    return (packet.packet_id, packet.packet_state)


def _queue_event_sort_key(
    event: "LGRC9V3PacketQueueEventRecord",
) -> tuple[float, int, str]:
    return (event.event_time_key, event.scheduler_event_index, event.event_id)


@dataclass(frozen=True)
class LGRC9V3PacketRecord:
    """Passive LGRC-2 packet record.

    A packet record is serialized causal-flux evidence. Creating one does not
    debit a source node, credit a target node, mutate ``GRC9V3State``, or
    process queue events. Iteration 10 owns those transitions.
    """

    packet_id: str
    packet_state: str
    source_node_id: NodeId
    target_node_id: NodeId
    edge_id: EdgeId
    amount: float
    departure_event_time_key: float
    arrival_event_time_key: float
    departure_event_id: str | None = None
    arrival_event_id: str | None = None
    departure_scheduler_event_index: int | None = None
    arrival_scheduler_event_index: int | None = None
    source_lineage_id: str | None = None
    target_lineage_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.packet_id, str) or not self.packet_id:
            raise ValueError("packet_id must be a non-empty string")
        if self.packet_state not in LGRC9V3_PACKET_STATES:
            raise ValueError(
                f"packet_state must be one of {sorted(LGRC9V3_PACKET_STATES)}"
            )
        _positive_float(self.amount, context="packet amount")
        departure = _nonnegative_float(
            self.departure_event_time_key,
            context="departure_event_time_key",
        )
        arrival = _nonnegative_float(
            self.arrival_event_time_key,
            context="arrival_event_time_key",
        )
        if arrival < departure:
            raise ValueError("arrival_event_time_key must be >= departure_event_time_key")
        for field_name in ("source_node_id", "target_node_id", "edge_id"):
            value = getattr(self, field_name)
            if int(value) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        for field_name in (
            "departure_scheduler_event_index",
            "arrival_scheduler_event_index",
        ):
            value = getattr(self, field_name)
            if value is not None and int(value) < 0:
                raise ValueError(f"{field_name} must be >= 0")

    def to_record(self) -> dict[str, Any]:
        """Return a JSON-compatible packet record."""

        record: dict[str, Any] = {
            "packet_id": self.packet_id,
            "packet_state": self.packet_state,
            "source_node_id": int(self.source_node_id),
            "target_node_id": int(self.target_node_id),
            "edge_id": int(self.edge_id),
            "amount": float(self.amount),
            "departure_event_time_key": float(self.departure_event_time_key),
            "arrival_event_time_key": float(self.arrival_event_time_key),
            "departure_event_id": self.departure_event_id,
            "arrival_event_id": self.arrival_event_id,
            "departure_scheduler_event_index": self.departure_scheduler_event_index,
            "arrival_scheduler_event_index": self.arrival_scheduler_event_index,
            "source_lineage_id": self.source_lineage_id,
            "target_lineage_id": self.target_lineage_id,
        }
        return record


@dataclass(frozen=True)
class LGRC9V3PacketQueueEventRecord:
    """Queue/event record for an LGRC-2 packet lifecycle event."""

    event_id: str
    event_kind: str
    event_time_key: float
    scheduler_event_index: int
    packet_id: str
    source_node_id: NodeId | None = None
    target_node_id: NodeId | None = None
    edge_id: EdgeId | None = None
    amount: float | None = None
    budget_before: float | None = None
    budget_after: float | None = None
    budget_error: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValueError("event_id must be a non-empty string")
        if self.event_kind not in LGRC9V3_PACKET_EVENT_KINDS:
            raise ValueError(
                f"event_kind must be one of {sorted(LGRC9V3_PACKET_EVENT_KINDS)}"
            )
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        if not isinstance(self.packet_id, str) or not self.packet_id:
            raise ValueError("packet_id must be a non-empty string")
        for field_name in ("source_node_id", "target_node_id", "edge_id"):
            value = getattr(self, field_name)
            if value is not None and int(value) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        if self.amount is not None:
            _positive_float(self.amount, context="amount")
        for field_name in ("budget_before", "budget_after"):
            value = getattr(self, field_name)
            if value is not None:
                _nonnegative_float(value, context=field_name)
        if self.budget_error is not None:
            _finite_float(self.budget_error, context="budget_error")

    def to_record(self) -> dict[str, Any]:
        """Return a JSON-compatible queue/event record."""

        return {
            "event_id": self.event_id,
            "event_kind": self.event_kind,
            "event_time_key": float(self.event_time_key),
            "scheduler_event_index": int(self.scheduler_event_index),
            "packet_id": self.packet_id,
            "source_node_id": None
            if self.source_node_id is None
            else int(self.source_node_id),
            "target_node_id": None
            if self.target_node_id is None
            else int(self.target_node_id),
            "edge_id": None if self.edge_id is None else int(self.edge_id),
            "amount": None if self.amount is None else float(self.amount),
            "budget_before": None
            if self.budget_before is None
            else float(self.budget_before),
            "budget_after": None
            if self.budget_after is None
            else float(self.budget_after),
            "budget_error": None
            if self.budget_error is None
            else float(self.budget_error),
        }


@dataclass(frozen=True)
class LGRC9V3PacketProcessingResult:
    """Auditable result for one active LGRC-2 packet transition.

    Departure and arrival processing mutate node coherence and packet lifecycle
    evidence only. They do not mutate topology and do not emit spark,
    mechanical-expansion, or identity-acceptance evidence by themselves.
    """

    ledger: LGRC9V3PacketLedger
    processed_event: LGRC9V3PacketQueueEventRecord
    packet_record: LGRC9V3PacketRecord
    budget_before: float
    budget_after: float
    budget_error: float
    topology_signature: dict[str, Any]
    state_mutated: bool = True
    topology_mutated: bool = False
    spark_event_emitted: bool = False
    mechanical_expansion_emitted: bool = False
    identity_acceptance_emitted: bool = False

    def __post_init__(self) -> None:
        _nonnegative_float(self.budget_before, context="budget_before")
        _nonnegative_float(self.budget_after, context="budget_after")
        _finite_float(self.budget_error, context="budget_error")
        if abs((self.budget_after - self.budget_before) - self.budget_error) > 1e-12:
            raise ValueError("budget_error must equal budget_after - budget_before")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible processing result artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC2_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": LGRC9V3_PACKETIZED_EVIDENCE_CLASS,
            "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
            "processed_event": self.processed_event.to_record(),
            "packet_record": self.packet_record.to_record(),
            "ledger": self.ledger.to_artifact(),
            "budget_before": float(self.budget_before),
            "budget_after": float(self.budget_after),
            "budget_error": float(self.budget_error),
            "topology_signature": dict(self.topology_signature),
            "state_mutated": self.state_mutated,
            "topology_mutated": self.topology_mutated,
            "spark_event_emitted": self.spark_event_emitted,
            "mechanical_expansion_emitted": self.mechanical_expansion_emitted,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
        }


@dataclass(frozen=True)
class LGRC9V3PacketArrivalEligibility:
    """Evidence that an arrival can feed local update or diagnostic checks.

    This object is only eligibility evidence. It does not run a local update,
    does not run a spark predicate, and does not emit expansion or identity
    events.
    """

    packet_id: str
    arrival_event_id: str
    scheduler_event_index: int
    event_time_key: float
    source_node_id: NodeId
    target_node_id: NodeId
    edge_id: EdgeId
    amount: float
    topology_signature: dict[str, Any]
    local_update_eligible: bool = True
    spark_diagnostic_eligible: bool = True
    spark_event_emitted: bool = False
    mechanical_expansion_emitted: bool = False
    identity_acceptance_emitted: bool = False
    causal_layer_mode: str = CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC2
    evidence_class: str = LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        if not isinstance(self.packet_id, str) or not self.packet_id:
            raise ValueError("packet_id must be a non-empty string")
        if not isinstance(self.arrival_event_id, str) or not self.arrival_event_id:
            raise ValueError("arrival_event_id must be a non-empty string")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        for field_name in ("source_node_id", "target_node_id", "edge_id"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        _positive_float(self.amount, context="amount")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible arrival eligibility artifact."""

        return {
            "artifact_kind": LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND,
            "artifact_schema_version": (
                LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC2_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "packet_id": self.packet_id,
            "arrival_event_id": self.arrival_event_id,
            "scheduler_event_index": int(self.scheduler_event_index),
            "event_time_key": float(self.event_time_key),
            "source_node_id": int(self.source_node_id),
            "target_node_id": int(self.target_node_id),
            "edge_id": int(self.edge_id),
            "amount": float(self.amount),
            "local_update_eligible": self.local_update_eligible,
            "spark_diagnostic_eligible": self.spark_diagnostic_eligible,
            "spark_event_emitted": self.spark_event_emitted,
            "mechanical_expansion_emitted": self.mechanical_expansion_emitted,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
            "topology_signature": dict(self.topology_signature),
        }


@dataclass(frozen=True)
class LGRC9V3PacketLedger:
    """Passive fixed-topology LGRC-2 packet ledger artifact surface."""

    packet_records: tuple[LGRC9V3PacketRecord, ...]
    packet_event_records: tuple[LGRC9V3PacketQueueEventRecord, ...]
    event_queue_records: tuple[LGRC9V3PacketQueueEventRecord, ...]
    node_coherence_total: float
    in_flight_packet_total: float
    conserved_budget_total: float
    budget_before: float
    budget_after: float
    budget_error: float
    fixed_topology_signature: dict[str, Any]
    policies: dict[str, Any]
    event_queue_tie_break_policy: str = LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY
    packet_budget_invariant: str = LGRC9V3_PACKET_BUDGET_INVARIANT
    causal_layer_mode: str = CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC2
    evidence_class: str = LGRC9V3_PACKETIZED_EVIDENCE_CLASS
    packetized_flux: bool = True
    fixed_topology: bool = True
    topology_change_allowed: bool = False
    packet_transport_through_topology_change: bool = False
    identity_acceptance_allowed: bool = False
    collapse_allowed: bool = False

    def __post_init__(self) -> None:
        packet_records = tuple(sorted(self.packet_records, key=_packet_sort_key))
        packet_event_records = tuple(
            sorted(self.packet_event_records, key=_queue_event_sort_key)
        )
        event_queue_records = tuple(
            sorted(self.event_queue_records, key=_queue_event_sort_key)
        )
        object.__setattr__(self, "packet_records", packet_records)
        object.__setattr__(self, "packet_event_records", packet_event_records)
        object.__setattr__(self, "event_queue_records", event_queue_records)
        for field_name in (
            "node_coherence_total",
            "in_flight_packet_total",
            "conserved_budget_total",
            "budget_before",
            "budget_after",
        ):
            _nonnegative_float(getattr(self, field_name), context=field_name)
        _finite_float(self.budget_error, context="budget_error")
        calculated_in_flight = sum(
            packet.amount
            for packet in packet_records
            if packet.packet_state == LGRC9V3_PACKET_STATE_IN_FLIGHT
        )
        if abs(calculated_in_flight - self.in_flight_packet_total) > 1e-12:
            raise ValueError("in_flight_packet_total must match packet records")
        calculated_budget = self.node_coherence_total + self.in_flight_packet_total
        if abs(calculated_budget - self.conserved_budget_total) > 1e-12:
            raise ValueError(
                "conserved_budget_total must equal node_coherence_total + "
                "in_flight_packet_total"
            )

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible packet ledger artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC2_PACKET_LEDGER_KIND,
            "artifact_schema_version": LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION,
            "mode_version": LGRC9V3_LGRC2_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": self.evidence_class,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "packetized_flux": self.packetized_flux,
            "fixed_topology": self.fixed_topology,
            "topology_change_allowed": self.topology_change_allowed,
            "packet_transport_through_topology_change": (
                self.packet_transport_through_topology_change
            ),
            "identity_acceptance_allowed": self.identity_acceptance_allowed,
            "collapse_allowed": self.collapse_allowed,
            "event_queue_tie_break_policy": self.event_queue_tie_break_policy,
            "packet_budget_invariant": self.packet_budget_invariant,
            "node_coherence_total": float(self.node_coherence_total),
            "in_flight_packet_total": float(self.in_flight_packet_total),
            "conserved_budget_total": float(self.conserved_budget_total),
            "budget_before": float(self.budget_before),
            "budget_after": float(self.budget_after),
            "budget_error": float(self.budget_error),
            "fixed_topology_signature": dict(self.fixed_topology_signature),
            "policies": dict(sorted(self.policies.items())),
            "packet_records": [
                packet.to_record() for packet in self.packet_records
            ],
            "packet_event_records": [
                event.to_record() for event in self.packet_event_records
            ],
            "event_queue_records": [
                event.to_record() for event in self.event_queue_records
            ],
        }


def _pending_flux_entry_sort_key(
    entry: "LGRC9V3PendingFluxEntry",
) -> tuple[int, int, int, float, str, str, str]:
    return (
        entry.edge_id,
        entry.source_node_id,
        entry.target_node_id,
        entry.arrival_event_time_key,
        entry.source_lineage_id or "",
        entry.target_lineage_id or "",
        entry.entry_id,
    )


@dataclass(frozen=True)
class LGRC9V3PendingFluxEntry:
    """Compact pending-flux entry derived from in-flight packet records."""

    entry_id: str
    source_node_id: NodeId
    target_node_id: NodeId
    edge_id: EdgeId
    arrival_event_time_key: float
    source_lineage_id: str | None
    target_lineage_id: str | None
    amount_total: float
    packet_count: int
    packet_ids: tuple[str, ...]
    departure_event_time_keys: tuple[float, ...]
    compaction_policy: str = LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT
    transport_ready_for_refinement: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.entry_id, str) or not self.entry_id:
            raise ValueError("entry_id must be a non-empty string")
        for field_name in ("source_node_id", "target_node_id", "edge_id"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        _nonnegative_float(
            self.arrival_event_time_key,
            context="arrival_event_time_key",
        )
        _positive_float(self.amount_total, context="amount_total")
        if int(self.packet_count) <= 0:
            raise ValueError("packet_count must be > 0")
        if len(self.packet_ids) != int(self.packet_count):
            raise ValueError("packet_ids length must equal packet_count")
        if len(self.departure_event_time_keys) != int(self.packet_count):
            raise ValueError(
                "departure_event_time_keys length must equal packet_count"
            )
        for packet_id in self.packet_ids:
            if not isinstance(packet_id, str) or not packet_id:
                raise ValueError("packet_ids must contain non-empty strings")
        for value in self.departure_event_time_keys:
            _nonnegative_float(value, context="departure_event_time_key")

    def to_record(self) -> dict[str, Any]:
        """Return a JSON-compatible compact pending-flux entry."""

        return {
            "entry_id": self.entry_id,
            "source_node_id": int(self.source_node_id),
            "target_node_id": int(self.target_node_id),
            "edge_id": int(self.edge_id),
            "arrival_event_time_key": float(self.arrival_event_time_key),
            "source_lineage_id": self.source_lineage_id,
            "target_lineage_id": self.target_lineage_id,
            "amount_total": float(self.amount_total),
            "packet_count": int(self.packet_count),
            "packet_ids": list(self.packet_ids),
            "departure_event_time_keys": [
                float(value) for value in self.departure_event_time_keys
            ],
            "compaction_policy": self.compaction_policy,
            "transport_ready_for_refinement": self.transport_ready_for_refinement,
        }


@dataclass(frozen=True)
class LGRC9V3PendingFluxLedger:
    """Compact pending-flux ledger derived from an expanded packet ledger."""

    pending_flux_entries: tuple[LGRC9V3PendingFluxEntry, ...]
    expanded_packet_count: int
    compact_entry_count: int
    node_coherence_total: float
    in_flight_packet_total: float
    pending_flux_total: float
    conserved_budget_total: float
    budget_before: float
    budget_after: float
    budget_error: float
    fixed_topology_signature: dict[str, Any]
    source_packet_ledger_schema_version: str
    policies: dict[str, Any]
    compaction_policy: str = LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT
    canonical_packet_ledger_retained: bool = True
    lineage_preserved: bool = True
    transport_ready_for_refinement: bool = True
    causal_layer_mode: str = CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC2
    evidence_class: str = LGRC9V3_PENDING_FLUX_EVIDENCE_CLASS
    packet_budget_invariant: str = LGRC9V3_PACKET_BUDGET_INVARIANT
    topology_change_allowed: bool = False
    packet_transport_through_topology_change: bool = False

    def __post_init__(self) -> None:
        entries = tuple(
            sorted(self.pending_flux_entries, key=_pending_flux_entry_sort_key)
        )
        object.__setattr__(self, "pending_flux_entries", entries)
        if int(self.expanded_packet_count) < 0:
            raise ValueError("expanded_packet_count must be >= 0")
        if int(self.compact_entry_count) != len(entries):
            raise ValueError("compact_entry_count must match entries")
        for field_name in (
            "node_coherence_total",
            "in_flight_packet_total",
            "pending_flux_total",
            "conserved_budget_total",
            "budget_before",
            "budget_after",
        ):
            _nonnegative_float(getattr(self, field_name), context=field_name)
        _finite_float(self.budget_error, context="budget_error")
        calculated_pending = sum(entry.amount_total for entry in entries)
        if abs(calculated_pending - self.pending_flux_total) > 1e-12:
            raise ValueError("pending_flux_total must match compact entries")
        if abs(self.pending_flux_total - self.in_flight_packet_total) > 1e-12:
            raise ValueError("pending_flux_total must equal in_flight_packet_total")
        calculated_budget = self.node_coherence_total + self.pending_flux_total
        if abs(calculated_budget - self.conserved_budget_total) > 1e-12:
            raise ValueError(
                "conserved_budget_total must equal node_coherence_total + "
                "pending_flux_total"
            )

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible compact pending-flux ledger artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC2_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "compaction_policy": self.compaction_policy,
            "canonical_packet_ledger_retained": self.canonical_packet_ledger_retained,
            "lineage_preserved": self.lineage_preserved,
            "transport_ready_for_refinement": self.transport_ready_for_refinement,
            "packet_budget_invariant": self.packet_budget_invariant,
            "topology_change_allowed": self.topology_change_allowed,
            "packet_transport_through_topology_change": (
                self.packet_transport_through_topology_change
            ),
            "source_packet_ledger_schema_version": (
                self.source_packet_ledger_schema_version
            ),
            "expanded_packet_count": int(self.expanded_packet_count),
            "compact_entry_count": int(self.compact_entry_count),
            "node_coherence_total": float(self.node_coherence_total),
            "in_flight_packet_total": float(self.in_flight_packet_total),
            "pending_flux_total": float(self.pending_flux_total),
            "conserved_budget_total": float(self.conserved_budget_total),
            "budget_before": float(self.budget_before),
            "budget_after": float(self.budget_after),
            "budget_error": float(self.budget_error),
            "fixed_topology_signature": dict(self.fixed_topology_signature),
            "policies": dict(sorted(self.policies.items())),
            "pending_flux_entries": [
                entry.to_record() for entry in self.pending_flux_entries
            ],
        }



def build_lgrc9v3_packet_contract_artifact() -> dict[str, Any]:
    """Return the LGRC-2 packetized causal-flux contract artifact.

    This is a schema/decision-record surface, not packet processing. Iteration
    8 defines the stable field names and boundaries that later packet state and
    queue code must implement.
    """

    return {
        "artifact_kind": LGRC9V3_LGRC2_PACKET_CONTRACT_KIND,
        "artifact_schema_version": LGRC9V3_LGRC2_PACKET_CONTRACT_SCHEMA_VERSION,
        "mode_version": LGRC9V3_LGRC2_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "evidence_class": LGRC9V3_PACKETIZED_EVIDENCE_CLASS,
        "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
        "packetized_flux": True,
        "fixed_topology": True,
        "topology_change_allowed": False,
        "packet_transport_through_topology_change": False,
        "identity_acceptance_allowed": False,
        "collapse_allowed": False,
        "event_queue_tie_break_policy": LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY,
        "normal_arrival_event_time_key_policy": (
            LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_DELAY_DERIVED
        ),
        "explicit_arrival_event_time_key_policy": (
            LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_EXPLICIT
        ),
        "packet_budget_invariant": LGRC9V3_PACKET_BUDGET_INVARIANT,
        "packet_event_kinds": sorted(LGRC9V3_PACKET_EVENT_KINDS),
        "packet_states": sorted(LGRC9V3_PACKET_STATES),
        "packet_required_fields": sorted(LGRC9V3_PACKET_REQUIRED_FIELDS),
        "packet_field_names": dict(vars(LGRC9V3_PACKET_FIELD_NAMES)),
        "packet_ledger_field_names": dict(vars(LGRC9V3_PACKET_LEDGER_FIELD_NAMES)),
    }


def build_lgrc9v3_packet_id(
    *,
    source_node_id: NodeId,
    target_node_id: NodeId,
    edge_id: EdgeId,
    amount: float,
    departure_event_time_key: float,
    arrival_event_time_key: float,
    packet_index: int = 0,
) -> str:
    """Build a deterministic packet id from replay-critical fields."""

    if int(packet_index) < 0:
        raise ValueError("packet_index must be >= 0")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": "packet",
        "source_node_id": int(source_node_id),
        "target_node_id": int(target_node_id),
        "edge_id": int(edge_id),
        "amount": _positive_float(amount, context="amount"),
        "departure_event_time_key": _nonnegative_float(
            departure_event_time_key,
            context="departure_event_time_key",
        ),
        "arrival_event_time_key": _nonnegative_float(
            arrival_event_time_key,
            context="arrival_event_time_key",
        ),
        "packet_index": int(packet_index),
    }
    if payload["arrival_event_time_key"] < payload["departure_event_time_key"]:
        raise ValueError("arrival_event_time_key must be >= departure_event_time_key")
    return f"lgrc9v3-packet-{digest_canonical_data(payload)[:16]}"


def build_lgrc9v3_packet_event_id(
    *,
    event_kind: str,
    packet_id: str,
    event_time_key: float,
    scheduler_event_index: int,
) -> str:
    """Build a deterministic queue event id from replay-critical fields."""

    if event_kind not in LGRC9V3_PACKET_EVENT_KINDS:
        raise ValueError(
            f"event_kind must be one of {sorted(LGRC9V3_PACKET_EVENT_KINDS)}"
        )
    if not isinstance(packet_id, str) or not packet_id:
        raise ValueError("packet_id must be a non-empty string")
    if int(scheduler_event_index) < 0:
        raise ValueError("scheduler_event_index must be >= 0")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": event_kind,
        "packet_id": packet_id,
        "event_time_key": _nonnegative_float(
            event_time_key,
            context="event_time_key",
        ),
        "scheduler_event_index": int(scheduler_event_index),
    }
    return f"lgrc9v3-packet-event-{digest_canonical_data(payload)[:16]}"


def create_lgrc9v3_packet_record(
    *,
    source_node_id: NodeId,
    target_node_id: NodeId,
    edge_id: EdgeId,
    amount: float,
    departure_event_time_key: float,
    arrival_event_time_key: float,
    packet_state: str = LGRC9V3_PACKET_STATE_SCHEDULED,
    packet_index: int = 0,
    packet_id: str | None = None,
    departure_event_id: str | None = None,
    arrival_event_id: str | None = None,
    departure_scheduler_event_index: int | None = None,
    arrival_scheduler_event_index: int | None = None,
    source_lineage_id: str | None = None,
    target_lineage_id: str | None = None,
) -> LGRC9V3PacketRecord:
    """Create a passive packet record with a deterministic id by default."""

    resolved_packet_id = packet_id or build_lgrc9v3_packet_id(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        edge_id=edge_id,
        amount=amount,
        departure_event_time_key=departure_event_time_key,
        arrival_event_time_key=arrival_event_time_key,
        packet_index=packet_index,
    )
    return LGRC9V3PacketRecord(
        packet_id=resolved_packet_id,
        packet_state=packet_state,
        source_node_id=int(source_node_id),
        target_node_id=int(target_node_id),
        edge_id=int(edge_id),
        amount=float(amount),
        departure_event_time_key=float(departure_event_time_key),
        arrival_event_time_key=float(arrival_event_time_key),
        departure_event_id=departure_event_id,
        arrival_event_id=arrival_event_id,
        departure_scheduler_event_index=departure_scheduler_event_index,
        arrival_scheduler_event_index=arrival_scheduler_event_index,
        source_lineage_id=source_lineage_id,
        target_lineage_id=target_lineage_id,
    )


def create_lgrc9v3_packet_queue_event_record(
    *,
    event_kind: str,
    event_time_key: float,
    scheduler_event_index: int,
    packet_id: str,
    event_id: str | None = None,
    source_node_id: NodeId | None = None,
    target_node_id: NodeId | None = None,
    edge_id: EdgeId | None = None,
    amount: float | None = None,
    budget_before: float | None = None,
    budget_after: float | None = None,
    budget_error: float | None = None,
) -> LGRC9V3PacketQueueEventRecord:
    """Create a queue/event record with deterministic id by default."""

    resolved_event_id = event_id or build_lgrc9v3_packet_event_id(
        event_kind=event_kind,
        packet_id=packet_id,
        event_time_key=event_time_key,
        scheduler_event_index=scheduler_event_index,
    )
    return LGRC9V3PacketQueueEventRecord(
        event_id=resolved_event_id,
        event_kind=event_kind,
        event_time_key=float(event_time_key),
        scheduler_event_index=int(scheduler_event_index),
        packet_id=packet_id,
        source_node_id=None if source_node_id is None else int(source_node_id),
        target_node_id=None if target_node_id is None else int(target_node_id),
        edge_id=None if edge_id is None else int(edge_id),
        amount=None if amount is None else float(amount),
        budget_before=None if budget_before is None else float(budget_before),
        budget_after=None if budget_after is None else float(budget_after),
        budget_error=None if budget_error is None else float(budget_error),
    )



def derive_lgrc9v3_packet_arrival_event_time_key(
    *,
    departure_event_time_key: float,
    edge_id: EdgeId,
    edge_causal_delay: Mapping[EdgeId, float],
) -> float:
    """Derive the normal LGRC-2 packet arrival event-time key.

    The returned value is ``T_arrive`` for event-queue ordering:

    ``T_arrive = T_depart + tau_ij``.

    It is not the source or target node's local proper time. The delay mapping
    must be the edge-delay surface captured for the packet scheduling/departure
    decision; later topology or state changes do not retroactively reschedule
    this packet.
    """

    departure_key = _nonnegative_float(
        departure_event_time_key,
        context="departure_event_time_key",
    )
    resolved_edge_id = int(edge_id)
    if resolved_edge_id < 0:
        raise ValueError("edge_id must be >= 0")
    if resolved_edge_id not in edge_causal_delay:
        raise ValueError(f"edge_causal_delay missing edge {resolved_edge_id}")
    delay = _positive_float(
        edge_causal_delay[resolved_edge_id],
        context=f"edge_causal_delay[{resolved_edge_id}]",
    )
    return _finite_float(
        departure_key + delay,
        context="arrival_event_time_key",
    )


def restore_lgrc9v3_packet_record(
    record: Mapping[str, Any],
) -> LGRC9V3PacketRecord:
    """Restore one passive LGRC-2 packet record from JSON-compatible data."""

    mapping = _require_artifact_mapping(record, context="packet_record")
    return LGRC9V3PacketRecord(
        packet_id=_artifact_string(mapping.get("packet_id"), context="packet_id"),
        packet_state=_artifact_string(
            mapping.get("packet_state"),
            context="packet_state",
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
        departure_event_time_key=_artifact_float(
            mapping.get("departure_event_time_key"),
            context="departure_event_time_key",
        ),
        arrival_event_time_key=_artifact_float(
            mapping.get("arrival_event_time_key"),
            context="arrival_event_time_key",
        ),
        departure_event_id=_artifact_optional_string(
            mapping.get("departure_event_id"),
            context="departure_event_id",
        ),
        arrival_event_id=_artifact_optional_string(
            mapping.get("arrival_event_id"),
            context="arrival_event_id",
        ),
        departure_scheduler_event_index=None
        if mapping.get("departure_scheduler_event_index") is None
        else _artifact_int(
            mapping.get("departure_scheduler_event_index"),
            context="departure_scheduler_event_index",
        ),
        arrival_scheduler_event_index=None
        if mapping.get("arrival_scheduler_event_index") is None
        else _artifact_int(
            mapping.get("arrival_scheduler_event_index"),
            context="arrival_scheduler_event_index",
        ),
        source_lineage_id=_artifact_optional_string(
            mapping.get("source_lineage_id"),
            context="source_lineage_id",
        ),
        target_lineage_id=_artifact_optional_string(
            mapping.get("target_lineage_id"),
            context="target_lineage_id",
        ),
    )


def restore_lgrc9v3_packet_queue_event_record(
    record: Mapping[str, Any],
) -> LGRC9V3PacketQueueEventRecord:
    """Restore one passive LGRC-2 packet queue/event record."""

    mapping = _require_artifact_mapping(record, context="packet_queue_event")
    return LGRC9V3PacketQueueEventRecord(
        event_id=_artifact_string(mapping.get("event_id"), context="event_id"),
        event_kind=_artifact_string(mapping.get("event_kind"), context="event_kind"),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        packet_id=_artifact_string(mapping.get("packet_id"), context="packet_id"),
        source_node_id=None
        if mapping.get("source_node_id") is None
        else _artifact_int(mapping.get("source_node_id"), context="source_node_id"),
        target_node_id=None
        if mapping.get("target_node_id") is None
        else _artifact_int(mapping.get("target_node_id"), context="target_node_id"),
        edge_id=None
        if mapping.get("edge_id") is None
        else _artifact_int(mapping.get("edge_id"), context="edge_id"),
        amount=None
        if mapping.get("amount") is None
        else _artifact_float(mapping.get("amount"), context="amount"),
        budget_before=None
        if mapping.get("budget_before") is None
        else _artifact_float(mapping.get("budget_before"), context="budget_before"),
        budget_after=None
        if mapping.get("budget_after") is None
        else _artifact_float(mapping.get("budget_after"), context="budget_after"),
        budget_error=None
        if mapping.get("budget_error") is None
        else _artifact_float(mapping.get("budget_error"), context="budget_error"),
    )


def _restore_packet_sequence(
    artifact: Mapping[str, Any],
    *,
    key: str,
) -> tuple[LGRC9V3PacketRecord, ...]:
    raw_records = artifact.get(key, [])
    if not isinstance(raw_records, list):
        raise SnapshotCompatibilityError(f"{key} must be a list")
    return tuple(restore_lgrc9v3_packet_record(record) for record in raw_records)


def _restore_queue_event_sequence(
    artifact: Mapping[str, Any],
    *,
    key: str,
) -> tuple[LGRC9V3PacketQueueEventRecord, ...]:
    raw_records = artifact.get(key, [])
    if not isinstance(raw_records, list):
        raise SnapshotCompatibilityError(f"{key} must be a list")
    return tuple(
        restore_lgrc9v3_packet_queue_event_record(record)
        for record in raw_records
    )


def build_lgrc9v3_packet_ledger(
    *,
    packet_records: Sequence[LGRC9V3PacketRecord] = (),
    packet_event_records: Sequence[LGRC9V3PacketQueueEventRecord] = (),
    event_queue_records: Sequence[LGRC9V3PacketQueueEventRecord] = (),
    state: GRC9V3State | None = None,
    node_coherence_total: float | None = None,
    fixed_topology_signature: Mapping[str, Any] | None = None,
    policies: Mapping[str, Any] | None = None,
    budget_before: float | None = None,
    budget_after: float | None = None,
    causal_layer_mode: str = CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC2,
    evidence_class: str = LGRC9V3_PACKETIZED_EVIDENCE_CLASS,
    fixed_topology: bool = True,
    topology_change_allowed: bool = False,
    packet_transport_through_topology_change: bool = False,
    identity_acceptance_allowed: bool = False,
    collapse_allowed: bool = False,
) -> LGRC9V3PacketLedger:
    """Build a passive fixed-topology packet ledger without mutating state."""

    packets = tuple(packet_records)
    if state is None and node_coherence_total is None:
        raise ValueError("node_coherence_total is required when state is not provided")
    resolved_node_total = (
        _node_coherence_total(state)
        if state is not None
        else _nonnegative_float(
            node_coherence_total,
            context="node_coherence_total",
        )
    )
    resolved_topology_signature = (
        _topology_signature(state)
        if state is not None
        else dict(fixed_topology_signature or {})
    )
    in_flight_total = sum(
        _positive_float(packet.amount, context=f"packet_amount[{packet.packet_id}]")
        for packet in packets
        if packet.packet_state == LGRC9V3_PACKET_STATE_IN_FLIGHT
    )
    conserved_total = float(resolved_node_total) + float(in_flight_total)
    resolved_budget_before = (
        conserved_total
        if budget_before is None
        else _nonnegative_float(budget_before, context="budget_before")
    )
    resolved_budget_after = (
        conserved_total
        if budget_after is None
        else _nonnegative_float(budget_after, context="budget_after")
    )
    return LGRC9V3PacketLedger(
        packet_records=packets,
        packet_event_records=tuple(packet_event_records),
        event_queue_records=tuple(event_queue_records),
        node_coherence_total=float(resolved_node_total),
        in_flight_packet_total=float(in_flight_total),
        conserved_budget_total=conserved_total,
        budget_before=float(resolved_budget_before),
        budget_after=float(resolved_budget_after),
        budget_error=float(resolved_budget_after - resolved_budget_before),
        fixed_topology_signature=resolved_topology_signature,
        policies=dict(policies or {}),
        causal_layer_mode=causal_layer_mode,
        lgrc_runtime_level=lgrc_runtime_level,
        evidence_class=evidence_class,
        fixed_topology=bool(fixed_topology),
        topology_change_allowed=bool(topology_change_allowed),
        packet_transport_through_topology_change=bool(
            packet_transport_through_topology_change
        ),
        identity_acceptance_allowed=bool(identity_acceptance_allowed),
        collapse_allowed=bool(collapse_allowed),
    )


def build_lgrc9v3_pending_flux_entry_id(
    *,
    source_node_id: NodeId,
    target_node_id: NodeId,
    edge_id: EdgeId,
    arrival_event_time_key: float,
    source_lineage_id: str | None = None,
    target_lineage_id: str | None = None,
    compaction_policy: str = LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT,
) -> str:
    """Build a deterministic id for one compact pending-flux entry."""

    if compaction_policy != LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT:
        raise ValueError(f"unsupported compaction_policy: {compaction_policy}")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": "pending_flux_entry",
        "compaction_policy": compaction_policy,
        "source_node_id": int(source_node_id),
        "target_node_id": int(target_node_id),
        "edge_id": int(edge_id),
        "arrival_event_time_key": _nonnegative_float(
            arrival_event_time_key,
            context="arrival_event_time_key",
        ),
        "source_lineage_id": source_lineage_id,
        "target_lineage_id": target_lineage_id,
    }
    return f"lgrc9v3-pending-flux-{digest_canonical_data(payload)[:16]}"


def compact_lgrc9v3_packet_ledger(
    ledger: LGRC9V3PacketLedger,
    *,
    compaction_policy: str = LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT,
) -> LGRC9V3PendingFluxLedger:
    """Derive a compact pending-flux ledger from in-flight packet records.

    The canonical LGRC-2 packet ledger remains per-packet. This helper creates
    a compact, budget-equivalent view for later LGRC-3 transport planning.
    """

    if compaction_policy != LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT:
        raise ValueError(f"unsupported compaction_policy: {compaction_policy}")

    groups: dict[
        tuple[NodeId, NodeId, EdgeId, float, str | None, str | None],
        list[LGRC9V3PacketRecord],
    ] = {}
    for packet in ledger.packet_records:
        if packet.packet_state != LGRC9V3_PACKET_STATE_IN_FLIGHT:
            continue
        key = (
            packet.source_node_id,
            packet.target_node_id,
            packet.edge_id,
            packet.arrival_event_time_key,
            packet.source_lineage_id,
            packet.target_lineage_id,
        )
        groups.setdefault(key, []).append(packet)

    entries: list[LGRC9V3PendingFluxEntry] = []
    for (
        source_node_id,
        target_node_id,
        edge_id,
        arrival_event_time_key,
        source_lineage_id,
        target_lineage_id,
    ), packets in groups.items():
        ordered_packets = tuple(
            sorted(
                packets,
                key=lambda packet: (
                    packet.departure_event_time_key,
                    packet.packet_id,
                ),
            )
        )
        entry_id = build_lgrc9v3_pending_flux_entry_id(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_id=edge_id,
            arrival_event_time_key=arrival_event_time_key,
            source_lineage_id=source_lineage_id,
            target_lineage_id=target_lineage_id,
            compaction_policy=compaction_policy,
        )
        entries.append(
            LGRC9V3PendingFluxEntry(
                entry_id=entry_id,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                edge_id=edge_id,
                arrival_event_time_key=arrival_event_time_key,
                source_lineage_id=source_lineage_id,
                target_lineage_id=target_lineage_id,
                amount_total=sum(packet.amount for packet in ordered_packets),
                packet_count=len(ordered_packets),
                packet_ids=tuple(packet.packet_id for packet in ordered_packets),
                departure_event_time_keys=tuple(
                    packet.departure_event_time_key for packet in ordered_packets
                ),
                compaction_policy=compaction_policy,
                transport_ready_for_refinement=True,
            )
        )

    pending_total = sum(entry.amount_total for entry in entries)
    if abs(pending_total - ledger.in_flight_packet_total) > 1e-12:
        raise InvalidStateTransitionError(
            "compact pending-flux total does not match packet ledger"
        )
    return LGRC9V3PendingFluxLedger(
        pending_flux_entries=tuple(entries),
        expanded_packet_count=sum(
            1
            for packet in ledger.packet_records
            if packet.packet_state == LGRC9V3_PACKET_STATE_IN_FLIGHT
        ),
        compact_entry_count=len(entries),
        node_coherence_total=ledger.node_coherence_total,
        in_flight_packet_total=ledger.in_flight_packet_total,
        pending_flux_total=pending_total,
        conserved_budget_total=ledger.conserved_budget_total,
        budget_before=ledger.budget_before,
        budget_after=ledger.budget_after,
        budget_error=ledger.budget_error,
        fixed_topology_signature=dict(ledger.fixed_topology_signature),
        source_packet_ledger_schema_version=(
            LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION
        ),
        policies=dict(ledger.policies),
        compaction_policy=compaction_policy,
    )



def _ledger_packet_map(
    ledger: LGRC9V3PacketLedger,
) -> dict[str, LGRC9V3PacketRecord]:
    packets: dict[str, LGRC9V3PacketRecord] = {}
    for packet in ledger.packet_records:
        if packet.packet_id in packets:
            raise InvalidStateTransitionError(
                f"duplicate packet_id in ledger: {packet.packet_id}"
            )
        packets[packet.packet_id] = packet
    return packets


def _replace_packet_record(
    packet_records: Sequence[LGRC9V3PacketRecord],
    updated_packet: LGRC9V3PacketRecord,
) -> tuple[LGRC9V3PacketRecord, ...]:
    replaced = False
    records: list[LGRC9V3PacketRecord] = []
    for packet in packet_records:
        if packet.packet_id == updated_packet.packet_id:
            records.append(updated_packet)
            replaced = True
        else:
            records.append(packet)
    if not replaced:
        raise InvalidStateTransitionError(
            f"packet_id not found in ledger: {updated_packet.packet_id}"
        )
    return tuple(records)


def _remove_queue_event(
    event_records: Sequence[LGRC9V3PacketQueueEventRecord],
    *,
    event_id: str,
) -> tuple[LGRC9V3PacketQueueEventRecord, ...]:
    return tuple(event for event in event_records if event.event_id != event_id)


def _ledger_budget_total(
    state: GRC9V3State,
    ledger: LGRC9V3PacketLedger,
) -> float:
    return _node_coherence_total(state) + ledger.in_flight_packet_total


def _validate_lgrc2_state_ledger_alignment(
    state: GRC9V3State,
    ledger: LGRC9V3PacketLedger,
) -> dict[str, Any]:
    current_signature = _topology_signature(state)
    lineage_aware_topology_change = (
        ledger.lgrc_runtime_level == LGRC_RUNTIME_LEVEL_LGRC3
        and ledger.causal_layer_mode == CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
        and bool(ledger.topology_change_allowed)
        and bool(ledger.packet_transport_through_topology_change)
        and not bool(ledger.fixed_topology)
    )
    if (
        dict(ledger.fixed_topology_signature) != current_signature
        and not lineage_aware_topology_change
    ):
        raise InvalidStateTransitionError(
            "LGRC-2 packet processing requires unchanged fixed topology"
        )
    current_node_total = _node_coherence_total(state)
    if abs(current_node_total - ledger.node_coherence_total) > 1e-12:
        raise InvalidStateTransitionError(
            "LGRC-2 packet ledger node_coherence_total does not match state"
        )
    return current_signature


def _validate_packet_endpoints(
    state: GRC9V3State,
    *,
    source_node_id: NodeId,
    target_node_id: NodeId,
    edge_id: EdgeId,
) -> None:
    source_id = int(source_node_id)
    target_id = int(target_node_id)
    resolved_edge_id = int(edge_id)
    if not state.topology.has_node(source_id):
        raise InvalidStateTransitionError(f"source node {source_id} is not live")
    if not state.topology.has_node(target_id):
        raise InvalidStateTransitionError(f"target node {target_id} is not live")
    if not state.topology.has_edge(resolved_edge_id):
        raise InvalidStateTransitionError(f"edge {resolved_edge_id} is not live")
    endpoint_a, endpoint_b = state.topology.edge_ports(resolved_edge_id)
    endpoint_node_ids = {int(endpoint_a[0]), int(endpoint_b[0])}
    if endpoint_node_ids != {source_id, target_id}:
        raise InvalidStateTransitionError(
            "packet source and target must be the endpoints of edge_id"
        )


def schedule_lgrc9v3_packet_departure(
    state: GRC9V3State,
    ledger: LGRC9V3PacketLedger,
    *,
    source_node_id: NodeId,
    target_node_id: NodeId,
    edge_id: EdgeId,
    amount: float,
    departure_event_time_key: float,
    arrival_event_time_key: float,
    scheduler_event_index: int,
    packet_index: int = 0,
    arrival_scheduler_event_index: int | None = None,
    source_lineage_id: str | None = None,
    target_lineage_id: str | None = None,
) -> LGRC9V3PacketLedger:
    """Schedule one fixed-topology LGRC-2 packet departure without debiting.

    The scheduled packet does not count as in-flight coherence until its
    queued departure event is processed.
    """

    _validate_lgrc2_state_ledger_alignment(state, ledger)
    source_id = int(source_node_id)
    target_id = int(target_node_id)
    resolved_edge_id = int(edge_id)
    amount_value = _positive_float(amount, context="amount")
    departure_key = _nonnegative_float(
        departure_event_time_key,
        context="departure_event_time_key",
    )
    arrival_key = _nonnegative_float(
        arrival_event_time_key,
        context="arrival_event_time_key",
    )
    if arrival_key < departure_key:
        raise ValueError("arrival_event_time_key must be >= departure_event_time_key")
    if int(scheduler_event_index) < 0:
        raise ValueError("scheduler_event_index must be >= 0")
    resolved_arrival_scheduler_index = (
        int(scheduler_event_index) + 1
        if arrival_scheduler_event_index is None
        else int(arrival_scheduler_event_index)
    )
    if resolved_arrival_scheduler_index < 0:
        raise ValueError("arrival_scheduler_event_index must be >= 0")
    _validate_packet_endpoints(
        state,
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
    )
    packet_id = build_lgrc9v3_packet_id(
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
        amount=amount_value,
        departure_event_time_key=departure_key,
        arrival_event_time_key=arrival_key,
        packet_index=packet_index,
    )
    if packet_id in _ledger_packet_map(ledger):
        raise InvalidStateTransitionError(f"packet_id already exists: {packet_id}")
    departure_event_id = build_lgrc9v3_packet_event_id(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
        packet_id=packet_id,
        event_time_key=departure_key,
        scheduler_event_index=int(scheduler_event_index),
    )
    arrival_event_id = build_lgrc9v3_packet_event_id(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        packet_id=packet_id,
        event_time_key=arrival_key,
        scheduler_event_index=resolved_arrival_scheduler_index,
    )
    scheduled_packet = create_lgrc9v3_packet_record(
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
        amount=amount_value,
        departure_event_time_key=departure_key,
        arrival_event_time_key=arrival_key,
        packet_state=LGRC9V3_PACKET_STATE_SCHEDULED,
        packet_index=packet_index,
        packet_id=packet_id,
        departure_event_id=departure_event_id,
        arrival_event_id=arrival_event_id,
        departure_scheduler_event_index=int(scheduler_event_index),
        arrival_scheduler_event_index=resolved_arrival_scheduler_index,
        source_lineage_id=source_lineage_id,
        target_lineage_id=target_lineage_id,
    )
    queued_departure = create_lgrc9v3_packet_queue_event_record(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
        event_time_key=departure_key,
        scheduler_event_index=int(scheduler_event_index),
        packet_id=packet_id,
        event_id=departure_event_id,
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
        amount=amount_value,
    )
    budget_total = _ledger_budget_total(state, ledger)
    return build_lgrc9v3_packet_ledger(
        state=state,
        packet_records=tuple(ledger.packet_records) + (scheduled_packet,),
        packet_event_records=ledger.packet_event_records,
        event_queue_records=tuple(ledger.event_queue_records) + (queued_departure,),
        policies=ledger.policies,
        budget_before=budget_total,
        budget_after=budget_total,
        causal_layer_mode=ledger.causal_layer_mode,
        lgrc_runtime_level=ledger.lgrc_runtime_level,
        evidence_class=ledger.evidence_class,
        fixed_topology=ledger.fixed_topology,
        topology_change_allowed=ledger.topology_change_allowed,
        packet_transport_through_topology_change=(
            ledger.packet_transport_through_topology_change
        ),
        identity_acceptance_allowed=ledger.identity_acceptance_allowed,
        collapse_allowed=ledger.collapse_allowed,
    )


def process_lgrc9v3_packet_departure(
    state: GRC9V3State,
    ledger: LGRC9V3PacketLedger,
    *,
    source_node_id: NodeId,
    target_node_id: NodeId,
    edge_id: EdgeId,
    amount: float,
    departure_event_time_key: float,
    arrival_event_time_key: float,
    scheduler_event_index: int,
    packet_index: int = 0,
    arrival_scheduler_event_index: int | None = None,
    source_lineage_id: str | None = None,
    target_lineage_id: str | None = None,
) -> LGRC9V3PacketProcessingResult:
    """Process one fixed-topology LGRC-2 packet departure.

    This debits source coherence and adds an in-flight packet. It does not
    mutate topology, schedule a spark, expand mechanically, or accept identity.
    """

    topology_signature = _validate_lgrc2_state_ledger_alignment(state, ledger)
    source_id = int(source_node_id)
    target_id = int(target_node_id)
    resolved_edge_id = int(edge_id)
    amount_value = _positive_float(amount, context="amount")
    departure_key = _nonnegative_float(
        departure_event_time_key,
        context="departure_event_time_key",
    )
    arrival_key = _nonnegative_float(
        arrival_event_time_key,
        context="arrival_event_time_key",
    )
    if arrival_key < departure_key:
        raise ValueError("arrival_event_time_key must be >= departure_event_time_key")
    if int(scheduler_event_index) < 0:
        raise ValueError("scheduler_event_index must be >= 0")
    resolved_arrival_scheduler_index = (
        int(scheduler_event_index) + 1
        if arrival_scheduler_event_index is None
        else int(arrival_scheduler_event_index)
    )
    if resolved_arrival_scheduler_index < 0:
        raise ValueError("arrival_scheduler_event_index must be >= 0")
    _validate_packet_endpoints(
        state,
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
    )
    if source_id not in state.nodes:
        raise InvalidStateTransitionError(f"source node state missing: {source_id}")
    source_coherence = _finite_float(
        state.nodes[source_id].coherence,
        context=f"node_coherence[{source_id}]",
    )
    if source_coherence < amount_value:
        raise InvalidStateTransitionError(
            "source coherence is smaller than packet amount"
        )
    packet_id = build_lgrc9v3_packet_id(
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
        amount=amount_value,
        departure_event_time_key=departure_key,
        arrival_event_time_key=arrival_key,
        packet_index=packet_index,
    )
    if packet_id in _ledger_packet_map(ledger):
        raise InvalidStateTransitionError(f"packet_id already exists: {packet_id}")
    departure_event_id = build_lgrc9v3_packet_event_id(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
        packet_id=packet_id,
        event_time_key=departure_key,
        scheduler_event_index=int(scheduler_event_index),
    )
    arrival_event_id = build_lgrc9v3_packet_event_id(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        packet_id=packet_id,
        event_time_key=arrival_key,
        scheduler_event_index=resolved_arrival_scheduler_index,
    )
    budget_before = _ledger_budget_total(state, ledger)
    state.nodes[source_id].coherence = source_coherence - amount_value
    packet = create_lgrc9v3_packet_record(
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
        amount=amount_value,
        departure_event_time_key=departure_key,
        arrival_event_time_key=arrival_key,
        packet_state=LGRC9V3_PACKET_STATE_IN_FLIGHT,
        packet_index=packet_index,
        packet_id=packet_id,
        departure_event_id=departure_event_id,
        arrival_event_id=arrival_event_id,
        departure_scheduler_event_index=int(scheduler_event_index),
        arrival_scheduler_event_index=resolved_arrival_scheduler_index,
        source_lineage_id=source_lineage_id,
        target_lineage_id=target_lineage_id,
    )
    budget_after = _node_coherence_total(state) + ledger.in_flight_packet_total + amount_value
    budget_error = budget_after - budget_before
    departure_event = create_lgrc9v3_packet_queue_event_record(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
        event_time_key=departure_key,
        scheduler_event_index=int(scheduler_event_index),
        packet_id=packet_id,
        event_id=departure_event_id,
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
        amount=amount_value,
        budget_before=budget_before,
        budget_after=budget_after,
        budget_error=budget_error,
    )
    queued_arrival = create_lgrc9v3_packet_queue_event_record(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        event_time_key=arrival_key,
        scheduler_event_index=resolved_arrival_scheduler_index,
        packet_id=packet_id,
        event_id=arrival_event_id,
        source_node_id=source_id,
        target_node_id=target_id,
        edge_id=resolved_edge_id,
        amount=amount_value,
    )
    updated_ledger = build_lgrc9v3_packet_ledger(
        state=state,
        packet_records=tuple(ledger.packet_records) + (packet,),
        packet_event_records=tuple(ledger.packet_event_records) + (departure_event,),
        event_queue_records=tuple(ledger.event_queue_records) + (queued_arrival,),
        policies=ledger.policies,
        budget_before=budget_before,
        budget_after=budget_after,
        causal_layer_mode=ledger.causal_layer_mode,
        lgrc_runtime_level=ledger.lgrc_runtime_level,
        evidence_class=ledger.evidence_class,
        fixed_topology=ledger.fixed_topology,
        topology_change_allowed=ledger.topology_change_allowed,
        packet_transport_through_topology_change=(
            ledger.packet_transport_through_topology_change
        ),
        identity_acceptance_allowed=ledger.identity_acceptance_allowed,
        collapse_allowed=ledger.collapse_allowed,
    )
    return LGRC9V3PacketProcessingResult(
        ledger=updated_ledger,
        processed_event=departure_event,
        packet_record=packet,
        budget_before=budget_before,
        budget_after=budget_after,
        budget_error=budget_error,
        topology_signature=topology_signature,
    )


def _process_lgrc9v3_scheduled_packet_departure(
    state: GRC9V3State,
    ledger: LGRC9V3PacketLedger,
    *,
    queued_departure: LGRC9V3PacketQueueEventRecord,
) -> LGRC9V3PacketProcessingResult:
    topology_signature = _validate_lgrc2_state_ledger_alignment(state, ledger)
    packets = _ledger_packet_map(ledger)
    if queued_departure.packet_id not in packets:
        raise InvalidStateTransitionError(
            f"packet_id not found: {queued_departure.packet_id}"
        )
    packet = packets[queued_departure.packet_id]
    if packet.packet_state != LGRC9V3_PACKET_STATE_SCHEDULED:
        raise InvalidStateTransitionError(
            "queued departure requires a scheduled packet"
        )
    if queued_departure.event_time_key < packet.departure_event_time_key:
        raise InvalidStateTransitionError(
            "departure event_time_key is before packet departure"
        )
    _validate_packet_endpoints(
        state,
        source_node_id=packet.source_node_id,
        target_node_id=packet.target_node_id,
        edge_id=packet.edge_id,
    )
    if packet.source_node_id not in state.nodes:
        raise InvalidStateTransitionError(
            f"source node state missing: {packet.source_node_id}"
        )
    source_coherence = _finite_float(
        state.nodes[packet.source_node_id].coherence,
        context=f"node_coherence[{packet.source_node_id}]",
    )
    if source_coherence < packet.amount:
        raise InvalidStateTransitionError(
            "source coherence is smaller than packet amount"
        )

    budget_before = _ledger_budget_total(state, ledger)
    state.nodes[packet.source_node_id].coherence = source_coherence - packet.amount
    in_flight_packet = LGRC9V3PacketRecord(
        packet_id=packet.packet_id,
        packet_state=LGRC9V3_PACKET_STATE_IN_FLIGHT,
        source_node_id=packet.source_node_id,
        target_node_id=packet.target_node_id,
        edge_id=packet.edge_id,
        amount=packet.amount,
        departure_event_time_key=packet.departure_event_time_key,
        arrival_event_time_key=packet.arrival_event_time_key,
        departure_event_id=queued_departure.event_id,
        arrival_event_id=packet.arrival_event_id,
        departure_scheduler_event_index=queued_departure.scheduler_event_index,
        arrival_scheduler_event_index=packet.arrival_scheduler_event_index,
        source_lineage_id=packet.source_lineage_id,
        target_lineage_id=packet.target_lineage_id,
    )
    budget_after = _node_coherence_total(state) + ledger.in_flight_packet_total + packet.amount
    budget_error = budget_after - budget_before
    departure_event = create_lgrc9v3_packet_queue_event_record(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
        event_time_key=queued_departure.event_time_key,
        scheduler_event_index=queued_departure.scheduler_event_index,
        packet_id=packet.packet_id,
        event_id=queued_departure.event_id,
        source_node_id=packet.source_node_id,
        target_node_id=packet.target_node_id,
        edge_id=packet.edge_id,
        amount=packet.amount,
        budget_before=budget_before,
        budget_after=budget_after,
        budget_error=budget_error,
    )
    if packet.arrival_scheduler_event_index is None:
        raise InvalidStateTransitionError(
            "scheduled packet arrival_scheduler_event_index is unavailable"
        )
    if packet.arrival_event_id is None:
        raise InvalidStateTransitionError(
            "scheduled packet arrival_event_id is unavailable"
        )
    queued_arrival = create_lgrc9v3_packet_queue_event_record(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        event_time_key=packet.arrival_event_time_key,
        scheduler_event_index=packet.arrival_scheduler_event_index,
        packet_id=packet.packet_id,
        event_id=packet.arrival_event_id,
        source_node_id=packet.source_node_id,
        target_node_id=packet.target_node_id,
        edge_id=packet.edge_id,
        amount=packet.amount,
    )
    updated_ledger = build_lgrc9v3_packet_ledger(
        state=state,
        packet_records=_replace_packet_record(
            ledger.packet_records,
            in_flight_packet,
        ),
        packet_event_records=tuple(ledger.packet_event_records) + (departure_event,),
        event_queue_records=_remove_queue_event(
            ledger.event_queue_records,
            event_id=queued_departure.event_id,
        )
        + (queued_arrival,),
        policies=ledger.policies,
        budget_before=budget_before,
        budget_after=budget_after,
        causal_layer_mode=ledger.causal_layer_mode,
        lgrc_runtime_level=ledger.lgrc_runtime_level,
        evidence_class=ledger.evidence_class,
        fixed_topology=ledger.fixed_topology,
        topology_change_allowed=ledger.topology_change_allowed,
        packet_transport_through_topology_change=(
            ledger.packet_transport_through_topology_change
        ),
        identity_acceptance_allowed=ledger.identity_acceptance_allowed,
        collapse_allowed=ledger.collapse_allowed,
    )
    return LGRC9V3PacketProcessingResult(
        ledger=updated_ledger,
        processed_event=departure_event,
        packet_record=in_flight_packet,
        budget_before=budget_before,
        budget_after=budget_after,
        budget_error=budget_error,
        topology_signature=topology_signature,
    )


def process_lgrc9v3_packet_arrival(
    state: GRC9V3State,
    ledger: LGRC9V3PacketLedger,
    *,
    packet_id: str,
    event_time_key: float | None = None,
    scheduler_event_index: int | None = None,
    event_id: str | None = None,
) -> LGRC9V3PacketProcessingResult:
    """Process one fixed-topology LGRC-2 packet arrival."""

    topology_signature = _validate_lgrc2_state_ledger_alignment(state, ledger)
    packets = _ledger_packet_map(ledger)
    if packet_id not in packets:
        raise InvalidStateTransitionError(f"packet_id not found: {packet_id}")
    packet = packets[packet_id]
    if packet.packet_state != LGRC9V3_PACKET_STATE_IN_FLIGHT:
        raise InvalidStateTransitionError("only in-flight packets can arrive")
    matching_events = [
        event
        for event in ledger.event_queue_records
        if event.packet_id == packet_id
        and event.event_kind == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL
    ]
    queued_event = matching_events[0] if matching_events else None
    resolved_event_time_key = (
        packet.arrival_event_time_key
        if event_time_key is None and queued_event is None
        else queued_event.event_time_key
        if event_time_key is None and queued_event is not None
        else _nonnegative_float(event_time_key, context="event_time_key")
    )
    if resolved_event_time_key < packet.arrival_event_time_key:
        raise InvalidStateTransitionError("arrival event_time_key is before packet arrival")
    resolved_scheduler_index = (
        packet.arrival_scheduler_event_index
        if scheduler_event_index is None and queued_event is None
        else queued_event.scheduler_event_index
        if scheduler_event_index is None and queued_event is not None
        else int(scheduler_event_index)
    )
    if resolved_scheduler_index is None:
        raise InvalidStateTransitionError(
            "arrival scheduler_event_index is unavailable"
        )
    if int(resolved_scheduler_index) < 0:
        raise ValueError("scheduler_event_index must be >= 0")
    resolved_event_id = (
        event_id
        or (queued_event.event_id if queued_event is not None else None)
        or build_lgrc9v3_packet_event_id(
            event_kind=LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            packet_id=packet_id,
            event_time_key=resolved_event_time_key,
            scheduler_event_index=int(resolved_scheduler_index),
        )
    )
    _validate_packet_endpoints(
        state,
        source_node_id=packet.source_node_id,
        target_node_id=packet.target_node_id,
        edge_id=packet.edge_id,
    )
    if packet.target_node_id not in state.nodes:
        raise InvalidStateTransitionError(
            f"target node state missing: {packet.target_node_id}"
        )
    target_coherence = _finite_float(
        state.nodes[packet.target_node_id].coherence,
        context=f"node_coherence[{packet.target_node_id}]",
    )
    budget_before = _ledger_budget_total(state, ledger)
    state.nodes[packet.target_node_id].coherence = target_coherence + packet.amount
    arrived_packet = LGRC9V3PacketRecord(
        packet_id=packet.packet_id,
        packet_state=LGRC9V3_PACKET_STATE_ARRIVED,
        source_node_id=packet.source_node_id,
        target_node_id=packet.target_node_id,
        edge_id=packet.edge_id,
        amount=packet.amount,
        departure_event_time_key=packet.departure_event_time_key,
        arrival_event_time_key=packet.arrival_event_time_key,
        departure_event_id=packet.departure_event_id,
        arrival_event_id=resolved_event_id,
        departure_scheduler_event_index=packet.departure_scheduler_event_index,
        arrival_scheduler_event_index=int(resolved_scheduler_index),
        source_lineage_id=packet.source_lineage_id,
        target_lineage_id=packet.target_lineage_id,
    )
    budget_after = _node_coherence_total(state) + (
        ledger.in_flight_packet_total - packet.amount
    )
    budget_error = budget_after - budget_before
    arrival_event = create_lgrc9v3_packet_queue_event_record(
        event_kind=LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        event_time_key=resolved_event_time_key,
        scheduler_event_index=int(resolved_scheduler_index),
        packet_id=packet_id,
        event_id=resolved_event_id,
        source_node_id=packet.source_node_id,
        target_node_id=packet.target_node_id,
        edge_id=packet.edge_id,
        amount=packet.amount,
        budget_before=budget_before,
        budget_after=budget_after,
        budget_error=budget_error,
    )
    updated_packet_records = _replace_packet_record(
        ledger.packet_records,
        arrived_packet,
    )
    updated_queue_records = _remove_queue_event(
        ledger.event_queue_records,
        event_id=resolved_event_id,
    )
    updated_ledger = build_lgrc9v3_packet_ledger(
        state=state,
        packet_records=updated_packet_records,
        packet_event_records=tuple(ledger.packet_event_records) + (arrival_event,),
        event_queue_records=updated_queue_records,
        policies=ledger.policies,
        budget_before=budget_before,
        budget_after=budget_after,
        causal_layer_mode=ledger.causal_layer_mode,
        lgrc_runtime_level=ledger.lgrc_runtime_level,
        evidence_class=ledger.evidence_class,
        fixed_topology=ledger.fixed_topology,
        topology_change_allowed=ledger.topology_change_allowed,
        packet_transport_through_topology_change=(
            ledger.packet_transport_through_topology_change
        ),
        identity_acceptance_allowed=ledger.identity_acceptance_allowed,
        collapse_allowed=ledger.collapse_allowed,
    )
    return LGRC9V3PacketProcessingResult(
        ledger=updated_ledger,
        processed_event=arrival_event,
        packet_record=arrived_packet,
        budget_before=budget_before,
        budget_after=budget_after,
        budget_error=budget_error,
        topology_signature=topology_signature,
    )


def process_lgrc9v3_next_packet_event(
    state: GRC9V3State,
    ledger: LGRC9V3PacketLedger,
) -> LGRC9V3PacketProcessingResult:
    """Process the earliest deterministic queued packet event."""

    if not ledger.event_queue_records:
        raise InvalidStateTransitionError("packet event queue is empty")
    next_event = ledger.event_queue_records[0]
    if next_event.event_kind == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL:
        return process_lgrc9v3_packet_arrival(
            state,
            ledger,
            packet_id=next_event.packet_id,
            event_time_key=next_event.event_time_key,
            scheduler_event_index=next_event.scheduler_event_index,
            event_id=next_event.event_id,
        )
    if next_event.event_kind == LGRC9V3_PACKET_EVENT_KIND_DEPARTURE:
        return _process_lgrc9v3_scheduled_packet_departure(
            state,
            ledger,
            queued_departure=next_event,
        )
    raise InvalidStateTransitionError("unsupported packet event kind")


def derive_lgrc9v3_packet_arrival_eligibility(
    result: LGRC9V3PacketProcessingResult,
    *,
    local_update_eligible: bool = True,
    spark_diagnostic_eligible: bool = True,
) -> LGRC9V3PacketArrivalEligibility:
    """Expose arrival-driven local update / diagnostic eligibility evidence.

    This deliberately stops before running a local update or spark predicate.
    """

    event = result.processed_event
    if event.event_kind != LGRC9V3_PACKET_EVENT_KIND_ARRIVAL:
        raise InvalidStateTransitionError(
            "arrival eligibility requires an arrival processing result"
        )
    if event.source_node_id is None or event.target_node_id is None:
        raise InvalidStateTransitionError("arrival event is missing node ids")
    if event.edge_id is None:
        raise InvalidStateTransitionError("arrival event is missing edge_id")
    if event.amount is None:
        raise InvalidStateTransitionError("arrival event is missing amount")
    return LGRC9V3PacketArrivalEligibility(
        packet_id=event.packet_id,
        arrival_event_id=event.event_id,
        scheduler_event_index=event.scheduler_event_index,
        event_time_key=event.event_time_key,
        source_node_id=event.source_node_id,
        target_node_id=event.target_node_id,
        edge_id=event.edge_id,
        amount=event.amount,
        topology_signature=result.topology_signature,
        local_update_eligible=bool(local_update_eligible),
        spark_diagnostic_eligible=bool(spark_diagnostic_eligible),
    )


def restore_lgrc9v3_packet_ledger_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3PacketLedger | None:
    """Restore an LGRC-2 packet ledger artifact, or ``None`` for other data."""

    mapping = _require_artifact_mapping(artifact, context="packet_ledger_artifact")
    if mapping.get("artifact_kind") != LGRC9V3_LGRC2_PACKET_LEDGER_KIND:
        return None
    schema_version = _artifact_string(
        mapping.get("artifact_schema_version"),
        context="artifact_schema_version",
    )
    if schema_version != LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION:
        raise SnapshotCompatibilityError(
            "unsupported LGRC9V3 packet ledger schema version"
        )
    contract_fields = {
        "mode_version": LGRC9V3_LGRC2_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "event_queue_tie_break_policy": LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY,
        "packet_budget_invariant": LGRC9V3_PACKET_BUDGET_INVARIANT,
    }
    for key, expected in contract_fields.items():
        actual = _artifact_string(mapping.get(key), context=key)
        if actual != expected:
            raise SnapshotCompatibilityError(f"{key} must be {expected!r}")
    evidence_class = _artifact_string(mapping.get("evidence_class"), context="evidence_class")
    if evidence_class not in {
        LGRC9V3_PACKETIZED_EVIDENCE_CLASS,
        LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS,
    }:
        raise SnapshotCompatibilityError("unsupported packet ledger evidence_class")
    causal_layer_mode = _artifact_string(
        mapping.get("causal_layer_mode"),
        context="causal_layer_mode",
    )
    if causal_layer_mode not in {
        CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
        CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    }:
        raise SnapshotCompatibilityError("unsupported packet ledger causal_layer_mode")
    lgrc_runtime_level = _artifact_string(
        mapping.get("lgrc_runtime_level"),
        context="lgrc_runtime_level",
    )
    if lgrc_runtime_level not in {LGRC_RUNTIME_LEVEL_LGRC2, LGRC_RUNTIME_LEVEL_LGRC3}:
        raise SnapshotCompatibilityError("unsupported packet ledger runtime level")
    packetized_flux = _artifact_bool(mapping.get("packetized_flux"), context="packetized_flux")
    fixed_topology = _artifact_bool(mapping.get("fixed_topology"), context="fixed_topology")
    topology_change_allowed = _artifact_bool(
        mapping.get("topology_change_allowed"),
        context="topology_change_allowed",
    )
    packet_transport_through_topology_change = _artifact_bool(
        mapping.get("packet_transport_through_topology_change"),
        context="packet_transport_through_topology_change",
    )
    identity_acceptance_allowed = _artifact_bool(
        mapping.get("identity_acceptance_allowed"),
        context="identity_acceptance_allowed",
    )
    collapse_allowed = _artifact_bool(mapping.get("collapse_allowed"), context="collapse_allowed")
    if not packetized_flux:
        raise SnapshotCompatibilityError("packetized_flux must be true")
    if topology_change_allowed or packet_transport_through_topology_change:
        if (
            fixed_topology
            or causal_layer_mode != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
            or lgrc_runtime_level != LGRC_RUNTIME_LEVEL_LGRC3
        ):
            raise SnapshotCompatibilityError(
                "topology-changing packet ledger requires LGRC-3 non-fixed mode"
            )
    elif (
        not fixed_topology
        or causal_layer_mode != CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY
        or lgrc_runtime_level != LGRC_RUNTIME_LEVEL_LGRC2
    ):
        raise SnapshotCompatibilityError(
            "fixed packet ledger requires LGRC-2 fixed topology mode"
        )
    policies = dict(
        _require_artifact_mapping(mapping.get("policies", {}), context="policies")
    )
    return LGRC9V3PacketLedger(
        packet_records=_restore_packet_sequence(mapping, key="packet_records"),
        packet_event_records=_restore_queue_event_sequence(
            mapping,
            key="packet_event_records",
        ),
        event_queue_records=_restore_queue_event_sequence(
            mapping,
            key="event_queue_records",
        ),
        node_coherence_total=_artifact_float(
            mapping.get("node_coherence_total"),
            context="node_coherence_total",
        ),
        in_flight_packet_total=_artifact_float(
            mapping.get("in_flight_packet_total"),
            context="in_flight_packet_total",
        ),
        conserved_budget_total=_artifact_float(
            mapping.get("conserved_budget_total"),
            context="conserved_budget_total",
        ),
        budget_before=_artifact_float(
            mapping.get("budget_before"),
            context="budget_before",
        ),
        budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
        budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
        fixed_topology_signature=dict(
            _require_artifact_mapping(
                mapping.get("fixed_topology_signature", {}),
                context="fixed_topology_signature",
            )
        ),
        policies=policies,
        causal_layer_mode=causal_layer_mode,
        lgrc_runtime_level=lgrc_runtime_level,
        evidence_class=evidence_class,
        packetized_flux=packetized_flux,
        fixed_topology=fixed_topology,
        topology_change_allowed=topology_change_allowed,
        packet_transport_through_topology_change=(
            packet_transport_through_topology_change
        ),
        identity_acceptance_allowed=identity_acceptance_allowed,
        collapse_allowed=collapse_allowed,
    )


def restore_lgrc9v3_pending_flux_entry_record(
    record: Mapping[str, Any],
) -> LGRC9V3PendingFluxEntry:
    """Restore one compact pending-flux entry from JSON-compatible data."""

    mapping = _require_artifact_mapping(record, context="pending_flux_entry")
    packet_ids_raw = mapping.get("packet_ids", [])
    if not isinstance(packet_ids_raw, list):
        raise SnapshotCompatibilityError("packet_ids must be a list")
    departure_keys_raw = mapping.get("departure_event_time_keys", [])
    if not isinstance(departure_keys_raw, list):
        raise SnapshotCompatibilityError("departure_event_time_keys must be a list")
    compaction_policy = _artifact_string(
        mapping.get("compaction_policy"),
        context="compaction_policy",
    )
    if compaction_policy != LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT:
        raise SnapshotCompatibilityError("unsupported pending-flux compaction policy")
    return LGRC9V3PendingFluxEntry(
        entry_id=_artifact_string(mapping.get("entry_id"), context="entry_id"),
        source_node_id=_artifact_int(
            mapping.get("source_node_id"),
            context="source_node_id",
        ),
        target_node_id=_artifact_int(
            mapping.get("target_node_id"),
            context="target_node_id",
        ),
        edge_id=_artifact_int(mapping.get("edge_id"), context="edge_id"),
        arrival_event_time_key=_artifact_float(
            mapping.get("arrival_event_time_key"),
            context="arrival_event_time_key",
        ),
        source_lineage_id=_artifact_optional_string(
            mapping.get("source_lineage_id"),
            context="source_lineage_id",
        ),
        target_lineage_id=_artifact_optional_string(
            mapping.get("target_lineage_id"),
            context="target_lineage_id",
        ),
        amount_total=_artifact_float(
            mapping.get("amount_total"),
            context="amount_total",
        ),
        packet_count=_artifact_int(mapping.get("packet_count"), context="packet_count"),
        packet_ids=tuple(
            _artifact_string(packet_id, context="packet_ids[]")
            for packet_id in packet_ids_raw
        ),
        departure_event_time_keys=tuple(
            _artifact_float(value, context="departure_event_time_keys[]")
            for value in departure_keys_raw
        ),
        compaction_policy=compaction_policy,
        transport_ready_for_refinement=_artifact_bool(
            mapping.get("transport_ready_for_refinement"),
            context="transport_ready_for_refinement",
        ),
    )


def _restore_pending_flux_entry_sequence(
    artifact: Mapping[str, Any],
    *,
    key: str,
) -> tuple[LGRC9V3PendingFluxEntry, ...]:
    raw_records = artifact.get(key, [])
    if not isinstance(raw_records, list):
        raise SnapshotCompatibilityError(f"{key} must be a list")
    return tuple(
        restore_lgrc9v3_pending_flux_entry_record(record)
        for record in raw_records
    )


def restore_lgrc9v3_pending_flux_ledger_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3PendingFluxLedger | None:
    """Restore a compact pending-flux ledger artifact, or ``None``."""

    mapping = _require_artifact_mapping(artifact, context="pending_flux_ledger")
    if mapping.get("artifact_kind") != LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_KIND:
        return None
    schema_version = _artifact_string(
        mapping.get("artifact_schema_version"),
        context="artifact_schema_version",
    )
    if schema_version != LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_SCHEMA_VERSION:
        raise SnapshotCompatibilityError(
            "unsupported LGRC9V3 pending-flux ledger schema version"
        )
    contract_fields = {
        "mode_version": LGRC9V3_LGRC2_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
        "evidence_class": LGRC9V3_PENDING_FLUX_EVIDENCE_CLASS,
        "compaction_policy": LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT,
        "packet_budget_invariant": LGRC9V3_PACKET_BUDGET_INVARIANT,
        "source_packet_ledger_schema_version": (
            LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION
        ),
    }
    for key, expected in contract_fields.items():
        actual = _artifact_string(mapping.get(key), context=key)
        if actual != expected:
            raise SnapshotCompatibilityError(f"{key} must be {expected!r}")
    bool_contract_fields = {
        "canonical_packet_ledger_retained": True,
        "lineage_preserved": True,
        "transport_ready_for_refinement": True,
        "topology_change_allowed": False,
        "packet_transport_through_topology_change": False,
    }
    for key, expected in bool_contract_fields.items():
        actual = _artifact_bool(mapping.get(key), context=key)
        if actual is not expected:
            raise SnapshotCompatibilityError(f"{key} must be {expected!r}")
    return LGRC9V3PendingFluxLedger(
        pending_flux_entries=_restore_pending_flux_entry_sequence(
            mapping,
            key="pending_flux_entries",
        ),
        expanded_packet_count=_artifact_int(
            mapping.get("expanded_packet_count"),
            context="expanded_packet_count",
        ),
        compact_entry_count=_artifact_int(
            mapping.get("compact_entry_count"),
            context="compact_entry_count",
        ),
        node_coherence_total=_artifact_float(
            mapping.get("node_coherence_total"),
            context="node_coherence_total",
        ),
        in_flight_packet_total=_artifact_float(
            mapping.get("in_flight_packet_total"),
            context="in_flight_packet_total",
        ),
        pending_flux_total=_artifact_float(
            mapping.get("pending_flux_total"),
            context="pending_flux_total",
        ),
        conserved_budget_total=_artifact_float(
            mapping.get("conserved_budget_total"),
            context="conserved_budget_total",
        ),
        budget_before=_artifact_float(
            mapping.get("budget_before"),
            context="budget_before",
        ),
        budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
        budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
        fixed_topology_signature=dict(
            _require_artifact_mapping(
                mapping.get("fixed_topology_signature", {}),
                context="fixed_topology_signature",
            )
        ),
        source_packet_ledger_schema_version=LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION,
        policies=dict(
            _require_artifact_mapping(mapping.get("policies", {}), context="policies")
        ),
        compaction_policy=LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT,
    )


__all__ = [
    'LGRC9V3PacketArrivalEligibility',
    'LGRC9V3PacketFieldNames',
    'LGRC9V3PacketLedger',
    'LGRC9V3PacketLedgerFieldNames',
    'LGRC9V3PacketProcessingResult',
    'LGRC9V3PacketQueueEventRecord',
    'LGRC9V3PacketRecord',
    'LGRC9V3PendingFluxEntry',
    'LGRC9V3PendingFluxFieldNames',
    'LGRC9V3PendingFluxLedger',
    'LGRC9V3_LGRC2_MODE_VERSION',
    'LGRC9V3_LGRC2_PACKET_CONTRACT_KIND',
    'LGRC9V3_LGRC2_PACKET_CONTRACT_SCHEMA_VERSION',
    'LGRC9V3_LGRC2_PACKET_LEDGER_KIND',
    'LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION',
    'LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_KIND',
    'LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_KIND',
    'LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_SCHEMA_VERSION',
    'LGRC9V3_PACKETIZED_EVIDENCE_CLASS',
    'LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_EVIDENCE_CLASS',
    'LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND',
    'LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_SCHEMA_VERSION',
    'LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_DELAY_DERIVED',
    'LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_EXPLICIT',
    'LGRC9V3_PACKET_BUDGET_INVARIANT',
    'LGRC9V3_PACKET_EVENT_KINDS',
    'LGRC9V3_PACKET_EVENT_KIND_ARRIVAL',
    'LGRC9V3_PACKET_EVENT_KIND_DEPARTURE',
    'LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY',
    'LGRC9V3_PACKET_FIELD_NAMES',
    'LGRC9V3_PACKET_LEDGER_FIELD_NAMES',
    'LGRC9V3_PACKET_REQUIRED_FIELDS',
    'LGRC9V3_PACKET_STATES',
    'LGRC9V3_PACKET_STATE_ARRIVED',
    'LGRC9V3_PACKET_STATE_CANCELLED',
    'LGRC9V3_PACKET_STATE_IN_FLIGHT',
    'LGRC9V3_PACKET_STATE_SCHEDULED',
    'LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT',
    'LGRC9V3_PENDING_FLUX_EVIDENCE_CLASS',
    'LGRC9V3_PENDING_FLUX_FIELD_NAMES',
    '_ledger_budget_total',
    '_ledger_packet_map',
    '_packet_sort_key',
    '_pending_flux_entry_sort_key',
    '_process_lgrc9v3_scheduled_packet_departure',
    '_queue_event_sort_key',
    '_remove_queue_event',
    '_replace_packet_record',
    '_restore_packet_sequence',
    '_restore_pending_flux_entry_sequence',
    '_restore_queue_event_sequence',
    '_validate_lgrc2_state_ledger_alignment',
    '_validate_packet_endpoints',
    'build_lgrc9v3_packet_contract_artifact',
    'build_lgrc9v3_packet_event_id',
    'build_lgrc9v3_packet_id',
    'build_lgrc9v3_packet_ledger',
    'build_lgrc9v3_pending_flux_entry_id',
    'compact_lgrc9v3_packet_ledger',
    'create_lgrc9v3_packet_queue_event_record',
    'create_lgrc9v3_packet_record',
    'derive_lgrc9v3_packet_arrival_eligibility',
    'derive_lgrc9v3_packet_arrival_event_time_key',
    'process_lgrc9v3_next_packet_event',
    'process_lgrc9v3_packet_arrival',
    'process_lgrc9v3_packet_departure',
    'restore_lgrc9v3_packet_ledger_artifact',
    'restore_lgrc9v3_packet_queue_event_record',
    'restore_lgrc9v3_packet_record',
    'restore_lgrc9v3_pending_flux_entry_record',
    'restore_lgrc9v3_pending_flux_ledger_artifact',
    'schedule_lgrc9v3_packet_departure',
]
