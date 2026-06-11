"""Shared observable contracts for PyGRC."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias


ObservableMap: TypeAlias = dict[str, Any]


@dataclass
class ObservableSnapshot:
    """Typed wrapper for a concrete observable mapping."""

    values: ObservableMap = field(default_factory=dict)
