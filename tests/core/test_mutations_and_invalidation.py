"""Tests for explicit mutation records and cache invalidation hooks."""

from __future__ import annotations

import unittest

from pygrc.core import (
    CacheInvalidation,
    GRCState,
    MutationAwareStorageProtocol,
    PortGraphBackend,
    TOPOLOGY_MUTATION_INVALIDATION,
    WeightedGraphBackend,
    apply_cache_invalidation,
    invalidate_state_cached_quantities,
)


class MutationAndInvalidationContractTest(unittest.TestCase):
    """Validate the Phase 2 mutation/invalidation contract surface."""

    def test_weighted_backend_is_mutation_aware_and_logs_mutations(self) -> None:
        graph = WeightedGraphBackend()

        self.assertIsInstance(graph, MutationAwareStorageProtocol)

        node_0 = graph.add_node()
        node_1 = graph.add_node()
        edge_0 = graph.add_edge(node_0, node_1)
        graph.remove_edge(edge_0)
        graph.remove_node(node_0)

        mutations = graph.consume_pending_mutations()

        self.assertEqual(
            ("add_node", "add_node", "add_edge", "remove_edge", "remove_node"),
            tuple(mutation.kind for mutation in mutations),
        )
        self.assertEqual((node_0,), mutations[0].node_ids)
        self.assertEqual((edge_0,), mutations[2].edge_ids)
        self.assertEqual((node_0,), mutations[-1].node_ids)
        self.assertEqual((), graph.consume_pending_mutations())

    def test_remove_node_records_cascade_edge_ids(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        edge_0 = graph.add_edge(node_0, node_1)
        edge_1 = graph.add_edge(node_1, node_2)
        graph.consume_pending_mutations()

        graph.remove_node(node_1)

        mutations = graph.consume_pending_mutations()
        self.assertEqual("remove_node", mutations[-1].kind)
        self.assertEqual((edge_0, edge_1), mutations[-1].cascade_edge_ids)

    def test_cache_invalidation_hook_can_clear_state_cached_quantities(self) -> None:
        graph = WeightedGraphBackend()
        state = GRCState(cached_quantities={"neighbors": 1, "coarse": 2})
        graph.set_cache_invalidation_hook(
            lambda invalidation: invalidate_state_cached_quantities(state, invalidation)
        )

        graph.add_node()

        self.assertEqual({}, state.cached_quantities)

    def test_clearing_cache_invalidation_hook_stops_state_cache_mutation(self) -> None:
        graph = WeightedGraphBackend()
        state = GRCState(cached_quantities={"neighbors": 1})
        graph.set_cache_invalidation_hook(
            lambda invalidation: invalidate_state_cached_quantities(state, invalidation)
        )
        graph.clear_cache_invalidation_hook()

        graph.add_node()

        self.assertEqual({"neighbors": 1}, state.cached_quantities)

    def test_apply_cache_invalidation_can_target_specific_cache_keys(self) -> None:
        cached_quantities = {"neighbors": 1, "ports": 2, "other": 3}

        apply_cache_invalidation(
            cached_quantities,
            TOPOLOGY_MUTATION_INVALIDATION,
        )

        self.assertEqual({}, cached_quantities)

        cached_quantities = {"neighbors": 1, "ports": 2, "other": 3}
        apply_cache_invalidation(
            cached_quantities,
            CacheInvalidation(
                cache_keys=frozenset({"neighbors", "ports"})
            ),
        )
        self.assertEqual({"other": 3}, cached_quantities)

    def test_port_backend_logs_connect_rewire_and_remove_mutations(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        graph.consume_pending_mutations()

        edge_0 = graph.connect_ports(node_0, 0, node_1, 1)
        graph.rewire_edge(edge_0, node_0, 2, node_2, 3)
        graph.remove_edge(edge_0)

        mutations = graph.consume_pending_mutations()
        self.assertEqual(
            ("connect_ports", "rewire_edge", "remove_edge"),
            tuple(mutation.kind for mutation in mutations),
        )
        self.assertEqual((edge_0,), mutations[0].edge_ids)
        self.assertEqual((edge_0,), mutations[1].edge_ids)
        self.assertEqual((edge_0,), mutations[2].edge_ids)

    def test_port_remove_node_mutation_records_cascade(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        edge_0 = graph.connect_ports(node_0, 0, node_1, 1)
        edge_1 = graph.connect_ports(node_1, 2, node_2, 3)
        graph.consume_pending_mutations()

        graph.remove_node(node_1)

        mutations = graph.consume_pending_mutations()
        self.assertEqual("remove_node", mutations[-1].kind)
        self.assertEqual((edge_0, edge_1), mutations[-1].cascade_edge_ids)
