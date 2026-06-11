"""GRCV2-specific state datatypes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias

from pygrc.core import EdgeId, GRCState, NodeId, WeightedGraphBackend


OrientedEdgeId: TypeAlias = tuple[EdgeId, NodeId]


@dataclass
class GRCV2State(GRCState):
    """Concrete baseline state shape for the executable GRCV2 model."""

    topology: WeightedGraphBackend = field(default_factory=WeightedGraphBackend)
    nodes: dict[NodeId, float] = field(default_factory=dict)
    edges: dict[EdgeId, float] = field(default_factory=dict)
    geometric_length: dict[EdgeId, float] = field(default_factory=dict)
    temporal_delay: dict[EdgeId, float] = field(default_factory=dict)
    flux_coupling: dict[EdgeId, float] = field(default_factory=dict)
    flux: dict[OrientedEdgeId, float] = field(default_factory=dict)
    potential: dict[NodeId, float] = field(default_factory=dict)
    sink_set: set[NodeId] = field(default_factory=set)
    basins: dict[NodeId, set[NodeId]] = field(default_factory=dict)
    split_registry: dict[str, Any] = field(default_factory=dict)

