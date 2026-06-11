"""Typed state dataclasses for the GRC9 family."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pygrc.core import EdgeId, GRCState, NodeId, PortGraphBackend


@dataclass(frozen=True)
class PortEdge:
    """Canonical occupied port-pair state for one live port edge."""

    node_u: NodeId
    port_u: int
    node_v: NodeId
    port_v: int
    conductance: float
    flux_uv: float


@dataclass(frozen=True)
class AdiabaticExpansionSchedule:
    """Optional in-progress gradualization state for one expansion event."""

    total_substeps: int
    completed_substeps: int = 0
    active: bool = True


@dataclass(frozen=True)
class ExpansionRecord:
    """Typed expansion-registry entry for deterministic replay."""

    parent_sink_id: NodeId
    module_node_ids: tuple[NodeId, ...] = ()
    expansion_step: int = 0
    distribution_weights: tuple[float, ...] = ()
    schedule: AdiabaticExpansionSchedule | None = None


@dataclass
class GRC9State(GRCState):
    """Concrete typed state surface for the GRC9 model shell."""

    topology: PortGraphBackend = field(default_factory=PortGraphBackend)
    node_coherence: dict[NodeId, float] = field(default_factory=dict)
    port_edges: dict[EdgeId, PortEdge] = field(default_factory=dict)
    geometric_length: dict[EdgeId, float] = field(default_factory=dict)
    temporal_delay: dict[EdgeId, float] = field(default_factory=dict)
    flux_coupling: dict[EdgeId, float] = field(default_factory=dict)
    potential: dict[NodeId, float] = field(default_factory=dict)
    sink_set: set[NodeId] = field(default_factory=set)
    basins: dict[NodeId, set[NodeId]] = field(default_factory=dict)
    expansion_registry: dict[str, ExpansionRecord] = field(default_factory=dict)
    coarse_cache: dict[str, Any] = field(default_factory=dict)
    rng_state: Any = None
    prev_column_diagnostic: dict[NodeId, list[float]] = field(default_factory=dict)
    edge_label_computation_mode: dict[str, str] = field(default_factory=dict)
    edge_label_params: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "AdiabaticExpansionSchedule",
    "ExpansionRecord",
    "GRC9State",
    "PortEdge",
]
