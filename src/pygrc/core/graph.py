"""Protocol surface for deterministic graph and storage backends."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, TypeAlias, runtime_checkable

from .mutations import CacheInvalidationHook, GraphMutation


NodeId: TypeAlias = int
EdgeId: TypeAlias = int
PortSlot: TypeAlias = int
PortCoordinate: TypeAlias = tuple[int, int]
NodeEndpoints: TypeAlias = tuple[NodeId, NodeId]
PortEndpoint: TypeAlias = tuple[NodeId, PortSlot]
PortEndpoints: TypeAlias = tuple[PortEndpoint, PortEndpoint]

PORT_ROW_COUNT = 3
PORT_COLUMN_COUNT = 3
PORTS_PER_NODE = PORT_ROW_COUNT * PORT_COLUMN_COUNT


@runtime_checkable
class GraphStorageProtocol(Protocol):
    """Common deterministic topology behavior shared by all graph backends.

    Implementations must expose live nodes and edges in deterministic order.
    Deleted or tombstoned records must not appear in these live iterators.
    """

    @property
    def next_node_id(self) -> int:
        """Return the next fresh node identifier without reusing prior IDs."""

    @property
    def next_edge_id(self) -> int:
        """Return the next fresh edge identifier without reusing prior IDs."""

    def iter_live_node_ids(self) -> Iterable[NodeId]:
        """Iterate live node IDs in canonical deterministic order."""

    def iter_live_edge_ids(self) -> Iterable[EdgeId]:
        """Iterate live edge IDs in canonical deterministic order."""

    def has_node(self, node_id: NodeId) -> bool:
        """Return whether the node currently exists as a live record."""

    def has_edge(self, edge_id: EdgeId) -> bool:
        """Return whether the edge currently exists as a live record."""

    def neighbors(self, node_id: NodeId) -> Iterable[NodeId]:
        """Iterate neighboring live node IDs in deterministic order."""

    def incident_edge_ids(self, node_id: NodeId) -> Iterable[EdgeId]:
        """Iterate incident live edge IDs in deterministic order."""


@runtime_checkable
class MutationAwareStorageProtocol(Protocol):
    """Protocol for explicit mutation visibility and cache invalidation hooks."""

    def set_cache_invalidation_hook(
        self, hook: CacheInvalidationHook | None
    ) -> None:
        """Register or clear the active cache-invalidation hook."""

    def clear_cache_invalidation_hook(self) -> None:
        """Remove the active cache-invalidation hook if one exists."""

    def consume_pending_mutations(self) -> tuple[GraphMutation, ...]:
        """Return and clear the pending deterministic mutation records."""


@runtime_checkable
class WeightedGraphProtocol(GraphStorageProtocol, Protocol):
    """Protocol for ordinary weighted graph backends used by `GRCV2`/`GRCV3`."""

    def edge_endpoints(self, edge_id: EdgeId) -> NodeEndpoints:
        """Return the live node endpoints for an edge."""

    def add_node(self) -> NodeId:
        """Insert one live node and return its fresh stable ID."""

    def remove_node(self, node_id: NodeId) -> None:
        """Remove a node from live iteration using the backend's tombstone rule."""

    def add_edge(self, node_a: NodeId, node_b: NodeId) -> EdgeId:
        """Insert one live edge between two live nodes and return its fresh ID."""

    def remove_edge(self, edge_id: EdgeId) -> None:
        """Remove an edge from live iteration using the backend's tombstone rule."""


@runtime_checkable
class PortGraphProtocol(GraphStorageProtocol, Protocol):
    """Protocol for fixed nine-slot port graphs used by `GRC9`/`GRC9V3`."""

    def iter_port_slots(self, node_id: NodeId) -> Iterable[PortSlot]:
        """Iterate the node's ordered port slots in canonical slot order."""

    def row_column_to_port_slot(self, row: int, column: int) -> PortSlot:
        """Map a canonical row/column position to one port slot ID."""

    def port_slot_to_row_column(self, slot: PortSlot) -> PortCoordinate:
        """Map one canonical slot ID back to its row/column position."""

    def port_is_occupied(self, node_id: NodeId, slot: PortSlot) -> bool:
        """Return whether one canonical node/slot endpoint is occupied."""

    def port_edge_id(self, node_id: NodeId, slot: PortSlot) -> EdgeId | None:
        """Return the live edge occupying one canonical node/slot endpoint."""

    def edge_ports(self, edge_id: EdgeId) -> PortEndpoints:
        """Return the two canonical node/slot endpoints for one edge."""

    def add_node(self) -> NodeId:
        """Insert one live node with exactly nine ordered ports."""

    def remove_node(self, node_id: NodeId) -> None:
        """Remove a node and clear its live port occupancy deterministically."""

    def connect_ports(
        self,
        node_a: NodeId,
        slot_a: PortSlot,
        node_b: NodeId,
        slot_b: PortSlot,
    ) -> EdgeId:
        """Insert one live edge between two explicit canonical port endpoints."""

    def rewire_edge(
        self,
        edge_id: EdgeId,
        node_a: NodeId,
        slot_a: PortSlot,
        node_b: NodeId,
        slot_b: PortSlot,
    ) -> None:
        """Move one live edge to new canonical port endpoints deterministically."""

    def remove_edge(self, edge_id: EdgeId) -> None:
        """Remove one live edge and clear its occupied port endpoints."""
