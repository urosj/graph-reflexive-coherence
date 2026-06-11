"""Contract tests for the Phase 2 graph/storage protocol surface."""

from __future__ import annotations

import unittest
from collections.abc import Iterable

from pygrc.core import (
    PORT_COLUMN_COUNT,
    PORT_ROW_COUNT,
    PORTS_PER_NODE,
    GraphStorageProtocol,
    PortGraphProtocol,
    WeightedGraphProtocol,
)


class DummyWeightedGraph:
    """Minimal structural implementation of the weighted-graph protocol."""

    def __init__(self) -> None:
        self.next_node_id = 2
        self.next_edge_id = 1

    def iter_live_node_ids(self) -> Iterable[int]:
        return (0, 1)

    def iter_live_edge_ids(self) -> Iterable[int]:
        return (0,)

    def has_node(self, node_id: int) -> bool:
        return node_id in {0, 1}

    def has_edge(self, edge_id: int) -> bool:
        return edge_id == 0

    def neighbors(self, node_id: int) -> Iterable[int]:
        return (1,) if node_id == 0 else (0,)

    def incident_edge_ids(self, node_id: int) -> Iterable[int]:
        return (0,) if node_id in {0, 1} else ()

    def edge_endpoints(self, edge_id: int) -> tuple[int, int]:
        if edge_id != 0:
            raise KeyError(edge_id)
        return (0, 1)

    def add_node(self) -> int:
        raise NotImplementedError

    def remove_node(self, node_id: int) -> None:
        del node_id
        raise NotImplementedError

    def add_edge(self, node_a: int, node_b: int) -> int:
        del node_a, node_b
        raise NotImplementedError

    def remove_edge(self, edge_id: int) -> None:
        del edge_id
        raise NotImplementedError


class DummyPortGraph:
    """Minimal structural implementation of the port-graph protocol."""

    def __init__(self) -> None:
        self.next_node_id = 1
        self.next_edge_id = 1

    def iter_live_node_ids(self) -> Iterable[int]:
        return (0,)

    def iter_live_edge_ids(self) -> Iterable[int]:
        return (0,)

    def has_node(self, node_id: int) -> bool:
        return node_id == 0

    def has_edge(self, edge_id: int) -> bool:
        return edge_id == 0

    def neighbors(self, node_id: int) -> Iterable[int]:
        return (0,) if node_id == 0 else ()

    def incident_edge_ids(self, node_id: int) -> Iterable[int]:
        return (0,) if node_id == 0 else ()

    def iter_port_slots(self, node_id: int) -> Iterable[int]:
        if node_id != 0:
            raise KeyError(node_id)
        return tuple(range(PORTS_PER_NODE))

    def row_column_to_port_slot(self, row: int, column: int) -> int:
        return row * PORT_COLUMN_COUNT + column

    def port_slot_to_row_column(self, slot: int) -> tuple[int, int]:
        return divmod(slot, PORT_COLUMN_COUNT)

    def port_is_occupied(self, node_id: int, slot: int) -> bool:
        return node_id == 0 and slot in {0, 1}

    def port_edge_id(self, node_id: int, slot: int) -> int | None:
        if self.port_is_occupied(node_id, slot):
            return 0
        return None

    def edge_ports(self, edge_id: int) -> tuple[tuple[int, int], tuple[int, int]]:
        if edge_id != 0:
            raise KeyError(edge_id)
        return ((0, 0), (0, 1))

    def add_node(self) -> int:
        raise NotImplementedError

    def remove_node(self, node_id: int) -> None:
        del node_id
        raise NotImplementedError

    def connect_ports(
        self, node_a: int, slot_a: int, node_b: int, slot_b: int
    ) -> int:
        del node_a, slot_a, node_b, slot_b
        raise NotImplementedError

    def rewire_edge(
        self, edge_id: int, node_a: int, slot_a: int, node_b: int, slot_b: int
    ) -> None:
        del edge_id, node_a, slot_a, node_b, slot_b
        raise NotImplementedError

    def remove_edge(self, edge_id: int) -> None:
        del edge_id
        raise NotImplementedError


class GraphProtocolContractTest(unittest.TestCase):
    """Validate the Phase 2 graph/storage protocol shapes."""

    def test_fixed_port_chart_constants_match_the_specs(self) -> None:
        self.assertEqual(3, PORT_ROW_COUNT)
        self.assertEqual(3, PORT_COLUMN_COUNT)
        self.assertEqual(9, PORTS_PER_NODE)

    def test_weighted_graph_protocol_is_runtime_checkable(self) -> None:
        graph = DummyWeightedGraph()

        self.assertIsInstance(graph, GraphStorageProtocol)
        self.assertIsInstance(graph, WeightedGraphProtocol)

    def test_port_graph_protocol_is_runtime_checkable(self) -> None:
        graph = DummyPortGraph()

        self.assertIsInstance(graph, GraphStorageProtocol)
        self.assertIsInstance(graph, PortGraphProtocol)

    def test_port_graph_retains_ordered_nine_slot_surface(self) -> None:
        graph = DummyPortGraph()

        self.assertEqual(tuple(range(9)), tuple(graph.iter_port_slots(0)))
        self.assertEqual(5, graph.row_column_to_port_slot(1, 2))
        self.assertEqual((1, 2), graph.port_slot_to_row_column(5))

