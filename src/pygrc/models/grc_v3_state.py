"""GRCV3-specific state datatypes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias

from pygrc.core import EdgeId, GRCState, NodeId, WeightedGraphBackend


OrientedEdgeId: TypeAlias = tuple[EdgeId, NodeId]


@dataclass
class BasinAttributes:
    """Semantic basin-attribute bundle stored on each GRCV3 node."""

    coherence: float
    gradient: list[float] = field(default_factory=list)
    hessian: list[list[float]] = field(default_factory=list)
    net_flux: list[float] = field(default_factory=list)
    basin_mass: float = 0.0
    basin_id: str | int = 0
    parent_id: str | int | None = None
    depth: int = 0


@dataclass
class GRCV3State(GRCState):
    """Concrete state shape for the semantic-rich GRCV3 family."""

    topology: WeightedGraphBackend = field(default_factory=WeightedGraphBackend)
    nodes: dict[NodeId, BasinAttributes] = field(default_factory=dict)
    base_conductance: dict[EdgeId, float] = field(default_factory=dict)
    geometric_length: dict[EdgeId, float] = field(default_factory=dict)
    temporal_delay: dict[EdgeId, float] = field(default_factory=dict)
    flux_coupling: dict[EdgeId, float] = field(default_factory=dict)
    flux: dict[OrientedEdgeId, float] = field(default_factory=dict)
    potential: dict[NodeId, float] = field(default_factory=dict)
    sink_set: set[NodeId] = field(default_factory=set)
    basins: dict[NodeId, set[NodeId]] = field(default_factory=dict)
    hierarchy: dict[str | int, list[str | int]] = field(default_factory=dict)
    choice_registry: dict[str, Any] = field(default_factory=dict)
    collapse_registry: dict[str, Any] = field(default_factory=dict)
    edge_label_computation_mode: dict[str, str] = field(default_factory=dict)
    edge_label_params: dict[str, Any] = field(default_factory=dict)
