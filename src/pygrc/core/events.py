"""Shared event datatypes for PyGRC."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GRCEvent:
    """Family-neutral event record emitted by model steps."""

    kind: str
    step_index: int
    payload: dict[str, Any] = field(default_factory=dict)
    source_family: str | None = None
