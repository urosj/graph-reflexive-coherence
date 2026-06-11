"""Tests for the integration-side graph adapter boundary."""

from __future__ import annotations

import unittest
from typing import Any

from pygrc.core import PortGraphBackend, WeightedGraphBackend
from pygrc.integrations import (
    PORT_GRAPH_ADAPTER_BOUNDARY,
    VISUALIZATION_ADAPTER_BOUNDARY,
    WEIGHTED_GRAPH_ADAPTER_BOUNDARY,
    GraphVisualizationAdapter,
    PortGraphInterchangeAdapter,
    WeightedGraphInterchangeAdapter,
)


class DummyWeightedAdapter:
    def export_graph(self, graph: WeightedGraphBackend) -> dict[str, Any]:
        return {"nodes": tuple(graph.iter_live_node_ids())}

    def import_graph(self, external_graph: Any) -> WeightedGraphBackend:
        del external_graph
        return WeightedGraphBackend()


class DummyPortAdapter:
    def export_graph(self, graph: PortGraphBackend) -> dict[str, Any]:
        return {"nodes": tuple(graph.iter_live_node_ids())}

    def import_graph(self, external_graph: Any) -> PortGraphBackend:
        del external_graph
        return PortGraphBackend()


class DummyVisualizationAdapter:
    def export_view(self, graph: Any) -> dict[str, Any]:
        return {
            "nodes": tuple(graph.iter_live_node_ids()),
            "edges": tuple(graph.iter_live_edge_ids()),
        }


class GraphAdapterBoundaryTest(unittest.TestCase):
    """Validate the integration-side adapter attachment surface."""

    def test_adapter_boundaries_are_non_authoritative(self) -> None:
        self.assertFalse(WEIGHTED_GRAPH_ADAPTER_BOUNDARY.execution_authoritative)
        self.assertFalse(PORT_GRAPH_ADAPTER_BOUNDARY.execution_authoritative)
        self.assertFalse(VISUALIZATION_ADAPTER_BOUNDARY.execution_authoritative)

    def test_weighted_adapter_protocol_is_runtime_checkable(self) -> None:
        adapter = DummyWeightedAdapter()

        self.assertIsInstance(adapter, WeightedGraphInterchangeAdapter)

    def test_port_adapter_protocol_is_runtime_checkable(self) -> None:
        adapter = DummyPortAdapter()

        self.assertIsInstance(adapter, PortGraphInterchangeAdapter)

    def test_visualization_adapter_protocol_is_runtime_checkable(self) -> None:
        adapter = DummyVisualizationAdapter()

        self.assertIsInstance(adapter, GraphVisualizationAdapter)

