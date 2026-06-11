"""Shared state and step-result datatypes for PyGRC."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .events import GRCEvent
from .observables import ObservableMap


@dataclass
class GRCState:
    """Family-neutral base state for all GRC model implementations."""

    topology: Any = None
    node_values: Any = None
    edge_values: Any = None
    step_index: int = 0
    time: float = 0.0
    budget_target: float = 0.0
    remainder: float = 0.0
    cached_quantities: dict[str, Any] = field(default_factory=dict)
    event_log: list[GRCEvent] = field(default_factory=list)
    observables: ObservableMap = field(default_factory=dict)
    rng_state: Any = None
    params_identity: str | None = None


@dataclass
class StepResult:
    """Minimum shared return type for one simulation step."""

    step_index: int
    time: float
    events: list[GRCEvent]
    observables: ObservableMap
    bookkeeping: dict[str, Any] = field(default_factory=dict)
