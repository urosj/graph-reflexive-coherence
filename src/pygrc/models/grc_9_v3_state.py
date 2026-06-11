"""Typed state dataclasses for the GRC9V3 hybrid family."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pygrc.core import EdgeId, GRCState, NodeId, PortGraphBackend

from .grc_9_state import ExpansionRecord, PortEdge


@dataclass
class GRC9V3NodeState:
    """Hybrid node state: GRC9 value on a GRCV3 semantic carrier."""

    coherence: float
    gradient_row_basis: list[float] = field(default_factory=list)
    signed_hessian_row_basis: list[float] = field(default_factory=list)
    net_flux_summary: list[float] = field(default_factory=list)
    basin_mass: float = 0.0
    basin_id: str | int = 0
    parent_id: str | int | None = None
    depth: int = 0


@dataclass
class GRC9V3State(GRCState):
    """Concrete typed state surface for the GRC9V3 model shell."""

    topology: PortGraphBackend = field(default_factory=PortGraphBackend)
    nodes: dict[NodeId, GRC9V3NodeState] = field(default_factory=dict)
    port_edges: dict[EdgeId, PortEdge] = field(default_factory=dict)
    base_conductance: dict[EdgeId, float] = field(default_factory=dict)
    geometric_length: dict[EdgeId, float] = field(default_factory=dict)
    temporal_delay: dict[EdgeId, float] = field(default_factory=dict)
    flux_coupling: dict[EdgeId, float] = field(default_factory=dict)
    potential: dict[NodeId, float] = field(default_factory=dict)
    sink_set: set[NodeId] = field(default_factory=set)
    basins: dict[NodeId, set[NodeId]] = field(default_factory=dict)
    hierarchy: dict[str | int, list[str | int]] = field(default_factory=dict)
    expansion_registry: dict[str, ExpansionRecord] = field(default_factory=dict)
    choice_registry: dict[str, Any] = field(default_factory=dict)
    collapse_registry: dict[str, Any] = field(default_factory=dict)
    coarse_cache: dict[str, Any] = field(default_factory=dict)
    edge_label_computation_mode: dict[str, str] = field(default_factory=dict)
    edge_label_params: dict[str, Any] = field(default_factory=dict)
    rng_state: Any = None


__all__ = ["GRC9V3NodeState", "GRC9V3State"]
