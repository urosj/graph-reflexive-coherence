"""Small numerical-convergence utilities shared by later B1-GR gates."""

from __future__ import annotations

import math
from typing import Sequence


def adjacent_relative_errors(values: Sequence[float]) -> list[float]:
    errors: list[float] = []
    for left, right in zip(values, values[1:], strict=False):
        errors.append(abs(left - right) / max(1.0, abs(right)))
    return errors


def observed_order(errors: Sequence[float], refinement_ratio: float = 2.0) -> list[float]:
    if refinement_ratio <= 1.0:
        raise ValueError("refinement_ratio must exceed one")
    orders: list[float] = []
    for coarse, fine in zip(errors, errors[1:], strict=False):
        if coarse <= 0.0 or fine <= 0.0:
            orders.append(float("inf"))
        else:
            orders.append(math.log(coarse / fine) / math.log(refinement_ratio))
    return orders
