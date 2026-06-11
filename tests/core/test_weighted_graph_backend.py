"""Tests for the Phase 2 weighted-graph backend."""

from __future__ import annotations

import unittest

from pygrc.core import TOMBSTONE, WeightedGraphBackend, WeightedGraphProtocol


class WeightedGraphBackendTest(unittest.TestCase):
    """Validate the reference weighted-graph substrate."""

    def test_backend_satisfies_weighted_graph_protocol(self) -> None:
        graph = WeightedGraphBackend()

        self.assertIsInstance(graph, WeightedGraphProtocol)

    def test_add_node_and_edge_produce_deterministic_live_iteration(self) -> None:
        graph = WeightedGraphBackend()

        node_0 = graph.add_node({"coherence": 1.0})
        node_1 = graph.add_node()
        edge_0 = graph.add_edge(node_0, node_1, {"base_conductance": 0.25})

        self.assertEqual((0, 1), (node_0, node_1))
        self.assertEqual(0, edge_0)
        self.assertEqual((0, 1), tuple(graph.iter_live_node_ids()))
        self.assertEqual((0,), tuple(graph.iter_live_edge_ids()))
        self.assertEqual((1,), tuple(graph.neighbors(node_0)))
        self.assertEqual((0,), tuple(graph.incident_edge_ids(node_0)))

    def test_neighbor_order_is_by_neighbor_id_then_edge_id(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()

        edge_0 = graph.add_edge(node_0, node_2)
        edge_1 = graph.add_edge(node_0, node_1)
        edge_2 = graph.add_edge(node_0, node_1)

        self.assertEqual((0, 1, 2), (edge_0, edge_1, edge_2))
        self.assertEqual((1, 2), tuple(graph.neighbors(node_0)))
        self.assertEqual((0, 1, 2), tuple(graph.incident_edge_ids(node_0)))

    def test_removed_edges_are_tombstoned_and_not_reused(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()

        edge_0 = graph.add_edge(node_0, node_1)
        graph.remove_edge(edge_0)
        edge_1 = graph.add_edge(node_0, node_1)

        self.assertEqual(1, edge_1)
        self.assertEqual((1,), tuple(graph.iter_live_edge_ids()))
        self.assertEqual((TOMBSTONE, graph.raw_edge_slots()[1]), graph.raw_edge_slots())

    def test_remove_node_cascades_incident_edge_removal(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        edge_0 = graph.add_edge(node_0, node_1)
        edge_1 = graph.add_edge(node_1, node_2)

        graph.remove_node(node_1)

        self.assertEqual((0, 2), tuple(graph.iter_live_node_ids()))
        self.assertEqual((), tuple(graph.iter_live_edge_ids()))
        self.assertEqual((TOMBSTONE,), graph.raw_node_slots()[1:2])
        self.assertEqual((TOMBSTONE, TOMBSTONE), graph.raw_edge_slots())
        with self.assertRaises(KeyError):
            graph.incident_edge_ids(node_1)
        with self.assertRaises(KeyError):
            graph.edge_endpoints(edge_0)
        with self.assertRaises(KeyError):
            graph.edge_endpoints(edge_1)

    def test_payloads_are_stored_in_family_neutral_dict_slots(self) -> None:
        graph = WeightedGraphBackend()
        node_payload = {"coherence": 0.7}
        node_0 = graph.add_node(node_payload)
        node_payload["coherence"] = 0.1
        node_1 = graph.add_node()
        edge_payload = {"flux_coupling": 2.0}
        edge_0 = graph.add_edge(node_0, node_1, edge_payload)
        edge_payload["flux_coupling"] = 1.0

        self.assertEqual({"coherence": 0.7}, graph.node_payload(node_0))
        self.assertEqual({"flux_coupling": 2.0}, graph.edge_payload(edge_0))

    def test_restored_backend_rebuilds_adjacency_and_counters(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        edge_0 = graph.add_edge(node_0, node_1)

        restored = WeightedGraphBackend(
            node_slots=graph.raw_node_slots(),
            edge_slots=graph.raw_edge_slots(),
            next_node_id=graph.next_node_id,
            next_edge_id=graph.next_edge_id,
        )

        self.assertEqual((0, 1), tuple(restored.iter_live_node_ids()))
        self.assertEqual((0,), tuple(restored.iter_live_edge_ids()))
        self.assertEqual((1,), tuple(restored.neighbors(node_0)))
        self.assertEqual((edge_0,), tuple(restored.incident_edge_ids(node_0)))
        self.assertEqual(2, restored.next_node_id)
        self.assertEqual(1, restored.next_edge_id)

    def test_restored_backend_rejects_live_edge_with_dead_endpoint(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        graph.add_edge(node_0, node_1)
        node_slots = list(graph.raw_node_slots())
        node_slots[node_1] = TOMBSTONE

        with self.assertRaises(ValueError):
            WeightedGraphBackend(
                node_slots=node_slots,
                edge_slots=graph.raw_edge_slots(),
                next_node_id=graph.next_node_id,
                next_edge_id=graph.next_edge_id,
            )

    def test_removed_node_id_is_not_reused_on_later_insert(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()

        graph.remove_node(node_0)
        node_2 = graph.add_node()

        self.assertEqual(2, node_2)
        self.assertEqual((1, 2), tuple(graph.iter_live_node_ids()))
