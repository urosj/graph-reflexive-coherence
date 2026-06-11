"""Private telemetry helpers shared across experiment surfaces."""

from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any


def _vector_norm(values: list[float] | tuple[float, ...]) -> float:
    return math.sqrt(sum(float(value) * float(value) for value in values))


def _to_plain_data(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _to_plain_data(inner_value) for key, inner_value in value.items()}
    if isinstance(value, list | tuple):
        return [_to_plain_data(item) for item in value]
    return value
