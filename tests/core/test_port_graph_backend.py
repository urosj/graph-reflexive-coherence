"""Tests for the Phase 2 nine-slot port-graph backend."""

from __future__ import annotations

import unittest

from pygrc.core import (
    TOMBSTONE,
    PORTS_PER_NODE,
    PortEdgeRecord,
    PortGraphBackend,
    PortGraphProtocol,
)


class PortGraphBackendTest(unittest.TestCase):
    """Validate the reference nine-slot port-graph substrate."""

    def test_backend_satisfies_port_graph_protocol(self) -> None:
        graph = PortGraphBackend()

        self.assertIsInstance(graph, PortGraphProtocol)

    def test_add_node_exposes_exactly_nine_ordered_ports(self) -> None:
        graph = PortGraphBackend()
        node_id = graph.add_node({"mass": 1.0})

        self.assertEqual((0,), tuple(graph.iter_live_node_ids()))
        self.assertEqual(tuple(range(PORTS_PER_NODE)), tuple(graph.iter_port_slots(node_id)))
        self.assertEqual({"mass": 1.0}, graph.node_payload(node_id))

    def test_row_column_conversion_is_canonical(self) -> None:
        graph = PortGraphBackend()

        self.assertEqual(0, graph.row_column_to_port_slot(0, 0))
        self.assertEqual(5, graph.row_column_to_port_slot(1, 2))
        self.assertEqual((1, 2), graph.port_slot_to_row_column(5))
        with self.assertRaises(ValueError):
            graph.row_column_to_port_slot(3, 0)
        with self.assertRaises(ValueError):
            graph.port_slot_to_row_column(9)

    def test_connect_ports_sets_deterministic_occupancy_and_lookup(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()

        edge_0 = graph.connect_ports(node_0, 0, node_1, 8, {"bond": 0.5})

        self.assertEqual((0,), tuple(graph.iter_live_edge_ids()))
        self.assertTrue(graph.port_is_occupied(node_0, 0))
        self.assertTrue(graph.port_is_occupied(node_1, 8))
        self.assertEqual(0, graph.port_edge_id(node_0, 0))
        self.assertEqual(0, graph.port_edge_id(node_1, 8))
        self.assertEqual(((node_0, 0), (node_1, 8)), graph.edge_ports(edge_0))
        self.assertEqual((1,), tuple(graph.neighbors(node_0)))
        self.assertEqual((0,), tuple(graph.incident_edge_ids(node_0)))
        self.assertEqual({"bond": 0.5}, graph.edge_payload(edge_0))

    def test_rewire_edge_moves_occupancy_without_changing_edge_id(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        edge_0 = graph.connect_ports(node_0, 0, node_1, 1)

        graph.rewire_edge(edge_0, node_0, 2, node_2, 3)

        self.assertFalse(graph.port_is_occupied(node_0, 0))
        self.assertFalse(graph.port_is_occupied(node_1, 1))
        self.assertTrue(graph.port_is_occupied(node_0, 2))
        self.assertTrue(graph.port_is_occupied(node_2, 3))
        self.assertEqual(((node_0, 2), (node_2, 3)), graph.edge_ports(edge_0))
        self.assertEqual((2,), tuple(graph.neighbors(node_0)))

    def test_remove_edge_tombstones_edge_and_clears_ports(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        edge_0 = graph.connect_ports(node_0, 4, node_1, 5)

        graph.remove_edge(edge_0)

        self.assertEqual((), tuple(graph.iter_live_edge_ids()))
        self.assertFalse(graph.port_is_occupied(node_0, 4))
        self.assertFalse(graph.port_is_occupied(node_1, 5))
        self.assertEqual((TOMBSTONE,), graph.raw_edge_slots())
        with self.assertRaises(KeyError):
            graph.edge_ports(edge_0)

    def test_remove_node_cascades_edge_removal_and_clears_port_state(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        edge_0 = graph.connect_ports(node_0, 0, node_1, 1)
        edge_1 = graph.connect_ports(node_1, 2, node_2, 3)

        graph.remove_node(node_1)

        self.assertEqual((0, 2), tuple(graph.iter_live_node_ids()))
        self.assertEqual((), tuple(graph.iter_live_edge_ids()))
        self.assertEqual(TOMBSTONE, graph.raw_node_slots()[1])
        self.assertEqual((TOMBSTONE, TOMBSTONE), graph.raw_edge_slots())
        self.assertFalse(graph.port_is_occupied(node_0, 0))
        self.assertFalse(graph.port_is_occupied(node_2, 3))
        with self.assertRaises(KeyError):
            graph.incident_edge_ids(node_1)
        with self.assertRaises(KeyError):
            graph.port_edge_id(node_1, 1)
        with self.assertRaises(KeyError):
            graph.edge_ports(edge_0)
        with self.assertRaises(KeyError):
            graph.edge_ports(edge_1)

    def test_connect_ports_rejects_already_occupied_slot(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        graph.connect_ports(node_0, 0, node_1, 1)

        with self.assertRaises(ValueError):
            graph.connect_ports(node_0, 0, node_2, 2)

    def test_rewire_rejects_target_slot_occupied_by_different_edge(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        edge_0 = graph.connect_ports(node_0, 0, node_1, 1)
        graph.connect_ports(node_0, 2, node_2, 3)

        with self.assertRaises(ValueError):
            graph.rewire_edge(edge_0, node_0, 2, node_2, 4)

    def test_removed_edge_id_is_not_reused_on_later_connect(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        edge_0 = graph.connect_ports(node_0, 0, node_1, 1)

        graph.remove_edge(edge_0)
        edge_1 = graph.connect_ports(node_0, 2, node_1, 3)

        self.assertEqual(1, edge_1)
        self.assertEqual((1,), tuple(graph.iter_live_edge_ids()))

    def test_restored_backend_rebuilds_occupancy_and_counters(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        edge_0 = graph.connect_ports(node_0, 0, node_1, 8)

        restored = PortGraphBackend(
            node_slots=graph.raw_node_slots(),
            edge_slots=graph.raw_edge_slots(),
            next_node_id=graph.next_node_id,
            next_edge_id=graph.next_edge_id,
        )

        self.assertEqual((0, 1), tuple(restored.iter_live_node_ids()))
        self.assertEqual((edge_0,), tuple(restored.iter_live_edge_ids()))
        self.assertEqual(edge_0, restored.port_edge_id(node_0, 0))
        self.assertEqual(edge_0, restored.port_edge_id(node_1, 8))
        self.assertEqual(2, restored.next_node_id)
        self.assertEqual(1, restored.next_edge_id)

    def test_restored_backend_rejects_duplicate_port_occupancy(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        graph.connect_ports(node_0, 0, node_1, 1)
        edge_slots = list(graph.raw_edge_slots())
        edge_slots.append(PortEdgeRecord(endpoint_a=(node_0, 0), endpoint_b=(node_2, 2)))

        with self.assertRaises(ValueError):
            PortGraphBackend(
                node_slots=graph.raw_node_slots(),
                edge_slots=edge_slots,
                next_node_id=graph.next_node_id,
                next_edge_id=graph.next_edge_id + 1,
            )
