"""Reference deterministic storage backends for Phase 2."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from .graph import (
    PORT_COLUMN_COUNT,
    PORT_ROW_COUNT,
    PORTS_PER_NODE,
    EdgeId,
    NodeEndpoints,
    NodeId,
    PortCoordinate,
    PortEndpoint,
    PortEndpoints,
    PortGraphProtocol,
    PortSlot,
    WeightedGraphProtocol,
)
from .ids import TOMBSTONE, TombstoneMarker, TombstoneSlotTable
from .mutations import (
    CacheInvalidationHook,
    GraphMutation,
    TOPOLOGY_MUTATION_INVALIDATION,
)


@dataclass(slots=True)
class WeightedEdgeRecord:
    """Family-neutral weighted-edge storage record."""

    node_a: NodeId
    node_b: NodeId
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PortEdgeRecord:
    """Family-neutral port-edge storage record."""

    endpoint_a: PortEndpoint
    endpoint_b: PortEndpoint
    payload: dict[str, Any] = field(default_factory=dict)


class _MutationAwareBackend:
    """Shared mutation journal and invalidation-hook behavior."""

    def __init__(self) -> None:
        self._pending_mutations: list[GraphMutation] = []
        self._cache_invalidation_hook: CacheInvalidationHook | None = None

    def set_cache_invalidation_hook(
        self, hook: CacheInvalidationHook | None
    ) -> None:
        self._cache_invalidation_hook = hook

    def clear_cache_invalidation_hook(self) -> None:
        self._cache_invalidation_hook = None

    def consume_pending_mutations(self) -> tuple[GraphMutation, ...]:
        mutations = tuple(self._pending_mutations)
        self._pending_mutations.clear()
        return mutations

    def _emit_mutation(self, mutation: GraphMutation) -> None:
        self._pending_mutations.append(mutation)
        if self._cache_invalidation_hook is not None:
            self._cache_invalidation_hook(mutation.invalidation)


class WeightedGraphBackend(_MutationAwareBackend, WeightedGraphProtocol):
    """Deterministic tombstoned weighted-graph backend for graph families."""

    def __init__(
        self,
        *,
        node_slots: Iterable[dict[str, Any] | TombstoneMarker] | None = None,
        edge_slots: Iterable[WeightedEdgeRecord | TombstoneMarker] | None = None,
        next_node_id: int | None = None,
        next_edge_id: int | None = None,
    ) -> None:
        super().__init__()
        self._node_slots = TombstoneSlotTable[dict[str, Any]](
            slots=node_slots, next_id=next_node_id
        )
        self._edge_slots = TombstoneSlotTable[WeightedEdgeRecord](
            slots=edge_slots, next_id=next_edge_id
        )
        self._adjacency: dict[NodeId, set[EdgeId]] = {}
        self._rebuild_adjacency()

    @property
    def next_node_id(self) -> int:
        return self._node_slots.next_id

    @property
    def next_edge_id(self) -> int:
        return self._edge_slots.next_id

    def iter_live_node_ids(self) -> Iterable[NodeId]:
        return self._node_slots.iter_live_ids()

    def iter_live_edge_ids(self) -> Iterable[EdgeId]:
        return self._edge_slots.iter_live_ids()

    def has_node(self, node_id: NodeId) -> bool:
        return self._node_slots.has_live(node_id)

    def has_edge(self, edge_id: EdgeId) -> bool:
        return self._edge_slots.has_live(edge_id)

    def neighbors(self, node_id: NodeId) -> Iterable[NodeId]:
        self._require_live_node(node_id)
        first_edge_by_neighbor: dict[NodeId, EdgeId] = {}
        for edge_id in self.incident_edge_ids(node_id):
            node_a, node_b = self.edge_endpoints(edge_id)
            neighbor_id = node_b if node_a == node_id else node_a
            first_edge_by_neighbor.setdefault(neighbor_id, edge_id)
        return tuple(
            neighbor_id
            for neighbor_id, _ in sorted(
                first_edge_by_neighbor.items(), key=lambda item: (item[0], item[1])
            )
        )

    def incident_edge_ids(self, node_id: NodeId) -> Iterable[EdgeId]:
        self._require_live_node(node_id)
        return tuple(sorted(self._adjacency[node_id]))

    def edge_endpoints(self, edge_id: EdgeId) -> NodeEndpoints:
        record = self._edge_slots.get_live(edge_id)
        return (record.node_a, record.node_b)

    def add_node(self, payload: Mapping[str, Any] | None = None) -> NodeId:
        node_id = self._node_slots.allocate(dict(payload or {}))
        self._adjacency[node_id] = set()
        self._emit_mutation(
            GraphMutation(
                kind="add_node",
                node_ids=(node_id,),
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )
        return node_id

    def remove_node(self, node_id: NodeId) -> None:
        self._require_live_node(node_id)
        incident_edge_ids = tuple(self.incident_edge_ids(node_id))
        for edge_id in incident_edge_ids:
            self.remove_edge(edge_id)
        self._node_slots.tombstone(node_id)
        self._adjacency.pop(node_id, None)
        self._emit_mutation(
            GraphMutation(
                kind="remove_node",
                node_ids=(node_id,),
                cascade_edge_ids=incident_edge_ids,
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )

    def add_edge(
        self, node_a: NodeId, node_b: NodeId, payload: Mapping[str, Any] | None = None
    ) -> EdgeId:
        self._require_live_node(node_a)
        self._require_live_node(node_b)
        edge_id = self._edge_slots.allocate(
            WeightedEdgeRecord(node_a=node_a, node_b=node_b, payload=dict(payload or {}))
        )
        self._adjacency[node_a].add(edge_id)
        self._adjacency[node_b].add(edge_id)
        self._emit_mutation(
            GraphMutation(
                kind="add_edge",
                node_ids=(node_a, node_b),
                edge_ids=(edge_id,),
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )
        return edge_id

    def remove_edge(self, edge_id: EdgeId) -> None:
        record = self._edge_slots.tombstone(edge_id)
        self._adjacency.get(record.node_a, set()).discard(edge_id)
        self._adjacency.get(record.node_b, set()).discard(edge_id)
        self._emit_mutation(
            GraphMutation(
                kind="remove_edge",
                node_ids=(record.node_a, record.node_b),
                edge_ids=(edge_id,),
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )

    def node_payload(self, node_id: NodeId) -> dict[str, Any]:
        return self._node_slots.get_live(node_id)

    def edge_payload(self, edge_id: EdgeId) -> dict[str, Any]:
        return self._edge_slots.get_live(edge_id).payload

    def raw_node_slots(self) -> tuple[dict[str, Any] | TombstoneMarker, ...]:
        return self._node_slots.raw_slots()

    def raw_edge_slots(
        self,
    ) -> tuple[WeightedEdgeRecord | TombstoneMarker, ...]:
        return self._edge_slots.raw_slots()

    def _require_live_node(self, node_id: NodeId) -> None:
        if not self.has_node(node_id):
            raise KeyError(node_id)

    def _rebuild_adjacency(self) -> None:
        self._adjacency = {
            node_id: set() for node_id in self._node_slots.iter_live_ids()
        }
        for edge_id, record in self._edge_slots.iter_live_items():
            if not self.has_node(record.node_a) or not self.has_node(record.node_b):
                raise ValueError(
                    "edge restoration requires live node endpoints for all live edges"
                )
            self._adjacency[record.node_a].add(edge_id)
            self._adjacency[record.node_b].add(edge_id)


class PortGraphBackend(_MutationAwareBackend, PortGraphProtocol):
    """Deterministic tombstoned nine-slot port-graph backend."""

    def __init__(
        self,
        *,
        node_slots: Iterable[dict[str, Any] | TombstoneMarker] | None = None,
        edge_slots: Iterable[PortEdgeRecord | TombstoneMarker] | None = None,
        next_node_id: int | None = None,
        next_edge_id: int | None = None,
    ) -> None:
        super().__init__()
        self._node_slots = TombstoneSlotTable[dict[str, Any]](
            slots=node_slots, next_id=next_node_id
        )
        self._edge_slots = TombstoneSlotTable[PortEdgeRecord](
            slots=edge_slots, next_id=next_edge_id
        )
        self._adjacency: dict[NodeId, set[EdgeId]] = {}
        self._port_edges: dict[NodeId, list[EdgeId | None]] = {}
        self._rebuild_indices()

    @property
    def next_node_id(self) -> int:
        return self._node_slots.next_id

    @property
    def next_edge_id(self) -> int:
        return self._edge_slots.next_id

    def iter_live_node_ids(self) -> Iterable[NodeId]:
        return self._node_slots.iter_live_ids()

    def iter_live_edge_ids(self) -> Iterable[EdgeId]:
        return self._edge_slots.iter_live_ids()

    def has_node(self, node_id: NodeId) -> bool:
        return self._node_slots.has_live(node_id)

    def has_edge(self, edge_id: EdgeId) -> bool:
        return self._edge_slots.has_live(edge_id)

    def neighbors(self, node_id: NodeId) -> Iterable[NodeId]:
        self._require_live_node(node_id)
        first_edge_by_neighbor: dict[NodeId, EdgeId] = {}
        for edge_id in self.incident_edge_ids(node_id):
            endpoint_a, endpoint_b = self.edge_ports(edge_id)
            neighbor_id = endpoint_b[0] if endpoint_a[0] == node_id else endpoint_a[0]
            first_edge_by_neighbor.setdefault(neighbor_id, edge_id)
        return tuple(
            neighbor_id
            for neighbor_id, _ in sorted(
                first_edge_by_neighbor.items(), key=lambda item: (item[0], item[1])
            )
        )

    def incident_edge_ids(self, node_id: NodeId) -> Iterable[EdgeId]:
        self._require_live_node(node_id)
        return tuple(sorted(self._adjacency[node_id]))

    def iter_port_slots(self, node_id: NodeId) -> Iterable[PortSlot]:
        self._require_live_node(node_id)
        return tuple(range(PORTS_PER_NODE))

    def row_column_to_port_slot(self, row: int, column: int) -> PortSlot:
        if row not in range(PORT_ROW_COUNT) or column not in range(PORT_COLUMN_COUNT):
            raise ValueError("row and column must be within the canonical 3x3 chart")
        return row * PORT_COLUMN_COUNT + column

    def port_slot_to_row_column(self, slot: PortSlot) -> PortCoordinate:
        self._require_valid_slot(slot)
        return divmod(slot, PORT_COLUMN_COUNT)

    def port_is_occupied(self, node_id: NodeId, slot: PortSlot) -> bool:
        self._require_live_node(node_id)
        self._require_valid_slot(slot)
        return self._port_edges[node_id][slot] is not None

    def port_edge_id(self, node_id: NodeId, slot: PortSlot) -> EdgeId | None:
        self._require_live_node(node_id)
        self._require_valid_slot(slot)
        return self._port_edges[node_id][slot]

    def edge_ports(self, edge_id: EdgeId) -> PortEndpoints:
        record = self._edge_slots.get_live(edge_id)
        return (record.endpoint_a, record.endpoint_b)

    def add_node(self, payload: Mapping[str, Any] | None = None) -> NodeId:
        node_id = self._node_slots.allocate(dict(payload or {}))
        self._adjacency[node_id] = set()
        self._port_edges[node_id] = [None] * PORTS_PER_NODE
        self._emit_mutation(
            GraphMutation(
                kind="add_node",
                node_ids=(node_id,),
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )
        return node_id

    def remove_node(self, node_id: NodeId) -> None:
        self._require_live_node(node_id)
        incident_edge_ids = tuple(self.incident_edge_ids(node_id))
        for edge_id in incident_edge_ids:
            self.remove_edge(edge_id)
        self._node_slots.tombstone(node_id)
        self._adjacency.pop(node_id, None)
        self._port_edges.pop(node_id, None)
        self._emit_mutation(
            GraphMutation(
                kind="remove_node",
                node_ids=(node_id,),
                cascade_edge_ids=incident_edge_ids,
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )

    def connect_ports(
        self,
        node_a: NodeId,
        slot_a: PortSlot,
        node_b: NodeId,
        slot_b: PortSlot,
        payload: Mapping[str, Any] | None = None,
    ) -> EdgeId:
        self._require_live_node(node_a)
        self._require_live_node(node_b)
        self._require_port_available(node_a, slot_a)
        self._require_port_available(node_b, slot_b)
        edge_id = self._edge_slots.allocate(
            PortEdgeRecord(
                endpoint_a=(node_a, slot_a),
                endpoint_b=(node_b, slot_b),
                payload=dict(payload or {}),
            )
        )
        self._occupy_endpoint(node_a, slot_a, edge_id)
        self._occupy_endpoint(node_b, slot_b, edge_id)
        self._adjacency[node_a].add(edge_id)
        self._adjacency[node_b].add(edge_id)
        self._emit_mutation(
            GraphMutation(
                kind="connect_ports",
                node_ids=(node_a, node_b),
                edge_ids=(edge_id,),
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )
        return edge_id

    def rewire_edge(
        self,
        edge_id: EdgeId,
        node_a: NodeId,
        slot_a: PortSlot,
        node_b: NodeId,
        slot_b: PortSlot,
    ) -> None:
        record = self._edge_slots.get_live(edge_id)
        self._require_live_node(node_a)
        self._require_live_node(node_b)
        self._require_rewire_target(node_a, slot_a, edge_id)
        self._require_rewire_target(node_b, slot_b, edge_id)

        old_endpoint_a, old_endpoint_b = record.endpoint_a, record.endpoint_b
        self._clear_endpoint(*old_endpoint_a)
        self._clear_endpoint(*old_endpoint_b)
        self._adjacency[old_endpoint_a[0]].discard(edge_id)
        self._adjacency[old_endpoint_b[0]].discard(edge_id)

        record.endpoint_a = (node_a, slot_a)
        record.endpoint_b = (node_b, slot_b)

        self._occupy_endpoint(node_a, slot_a, edge_id)
        self._occupy_endpoint(node_b, slot_b, edge_id)
        self._adjacency[node_a].add(edge_id)
        self._adjacency[node_b].add(edge_id)
        self._emit_mutation(
            GraphMutation(
                kind="rewire_edge",
                node_ids=(node_a, node_b),
                edge_ids=(edge_id,),
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )

    def remove_edge(self, edge_id: EdgeId) -> None:
        record = self._edge_slots.tombstone(edge_id)
        self._clear_endpoint(*record.endpoint_a)
        self._clear_endpoint(*record.endpoint_b)
        self._adjacency.get(record.endpoint_a[0], set()).discard(edge_id)
        self._adjacency.get(record.endpoint_b[0], set()).discard(edge_id)
        self._emit_mutation(
            GraphMutation(
                kind="remove_edge",
                node_ids=(record.endpoint_a[0], record.endpoint_b[0]),
                edge_ids=(edge_id,),
                invalidation=TOPOLOGY_MUTATION_INVALIDATION,
            )
        )

    def node_payload(self, node_id: NodeId) -> dict[str, Any]:
        return self._node_slots.get_live(node_id)

    def edge_payload(self, edge_id: EdgeId) -> dict[str, Any]:
        return self._edge_slots.get_live(edge_id).payload

    def raw_node_slots(self) -> tuple[dict[str, Any] | TombstoneMarker, ...]:
        return self._node_slots.raw_slots()

    def raw_edge_slots(self) -> tuple[PortEdgeRecord | TombstoneMarker, ...]:
        return self._edge_slots.raw_slots()

    def _clear_endpoint(self, node_id: NodeId, slot: PortSlot) -> None:
        if node_id in self._port_edges:
            self._port_edges[node_id][slot] = None

    def _occupy_endpoint(self, node_id: NodeId, slot: PortSlot, edge_id: EdgeId) -> None:
        self._require_valid_slot(slot)
        self._port_edges[node_id][slot] = edge_id

    def _rebuild_indices(self) -> None:
        self._adjacency = {
            node_id: set() for node_id in self._node_slots.iter_live_ids()
        }
        self._port_edges = {
            node_id: [None] * PORTS_PER_NODE for node_id in self._node_slots.iter_live_ids()
        }
        for edge_id, record in self._edge_slots.iter_live_items():
            for node_id, slot in (record.endpoint_a, record.endpoint_b):
                if not self.has_node(node_id):
                    raise ValueError(
                        "edge restoration requires live node endpoints for all live edges"
                    )
                self._require_valid_slot(slot)
                if self._port_edges[node_id][slot] is not None:
                    raise ValueError("restored port occupancy must be unique per node/slot")
                self._port_edges[node_id][slot] = edge_id
                self._adjacency[node_id].add(edge_id)

    def _require_live_node(self, node_id: NodeId) -> None:
        if not self.has_node(node_id):
            raise KeyError(node_id)

    def _require_port_available(self, node_id: NodeId, slot: PortSlot) -> None:
        self._require_valid_slot(slot)
        if self.port_is_occupied(node_id, slot):
            raise ValueError("port endpoint is already occupied")

    def _require_rewire_target(
        self, node_id: NodeId, slot: PortSlot, edge_id: EdgeId
    ) -> None:
        self._require_valid_slot(slot)
        current_edge_id = self.port_edge_id(node_id, slot)
        if current_edge_id is not None and current_edge_id != edge_id:
            raise ValueError("rewire target port endpoint is already occupied")

    def _require_valid_slot(self, slot: PortSlot) -> None:
        if slot not in range(PORTS_PER_NODE):
            raise ValueError("port slot must be within the canonical 0..8 range")
