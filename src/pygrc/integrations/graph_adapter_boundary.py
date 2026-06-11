"""Integration-side attachment points for future graph and visualization adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from pygrc.core import (
    GraphStorageProtocol,
    PortGraphBackend,
    PortGraphProtocol,
    WeightedGraphBackend,
    WeightedGraphProtocol,
)


@dataclass(frozen=True, slots=True)
class AdapterBoundary:
    """Describe one future adapter attachment point."""

    name: str
    target_protocol: str
    execution_authoritative: bool
    notes: str


WEIGHTED_GRAPH_ADAPTER_BOUNDARY = AdapterBoundary(
    name="weighted_graph_interchange",
    target_protocol="WeightedGraphProtocol",
    execution_authoritative=False,
    notes=(
        "Future interchange or analysis adapters attach here without replacing the "
        "in-house weighted execution backend."
    ),
)

PORT_GRAPH_ADAPTER_BOUNDARY = AdapterBoundary(
    name="port_graph_interchange",
    target_protocol="PortGraphProtocol",
    execution_authoritative=False,
    notes=(
        "Future interchange or analysis adapters attach here without replacing the "
        "in-house nine-slot execution backend."
    ),
)

VISUALIZATION_ADAPTER_BOUNDARY = AdapterBoundary(
    name="visualization_export",
    target_protocol="GraphStorageProtocol",
    execution_authoritative=False,
    notes=(
        "Future visualization/export adapters consume protocol-observable graph "
        "state without participating in authoritative execution."
    ),
)


@runtime_checkable
class WeightedGraphInterchangeAdapter(Protocol):
    """Future integration adapter boundary for weighted-graph interchange."""

    def export_graph(self, graph: WeightedGraphProtocol) -> Any:
        """Export one weighted graph to an external library or interchange form."""

    def import_graph(self, external_graph: Any) -> WeightedGraphBackend:
        """Import one external graph into the authoritative weighted backend."""


@runtime_checkable
class PortGraphInterchangeAdapter(Protocol):
    """Future integration adapter boundary for nine-slot port-graph interchange."""

    def export_graph(self, graph: PortGraphProtocol) -> Any:
        """Export one port graph to an external library or interchange form."""

    def import_graph(self, external_graph: Any) -> PortGraphBackend:
        """Import one external graph into the authoritative port backend."""


@runtime_checkable
class GraphVisualizationAdapter(Protocol):
    """Future integration adapter boundary for read-only visualization/export."""

    def export_view(self, graph: GraphStorageProtocol) -> Any:
        """Export one graph/storage view without becoming the execution substrate."""
