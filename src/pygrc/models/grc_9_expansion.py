"""Pure helper functions for Phase 6 GRC9 expansion and growth."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
import math


CANONICAL_CORE_SPINE_PORTS = (2, 5, 8)
PRIMARY_SATELLITE_COLUMNS = (1, 2, 3)


def compute_expansion_node_count(target_effective_degree: int) -> int:
    """Return the Eq. (13) node count lower bound for one target capacity."""

    return max(1, math.ceil((int(target_effective_degree) - 2) / 7))


def normalize_expansion_weights(
    *,
    mode: str,
    custom_weights: Sequence[float] | None = None,
) -> tuple[float, float, float]:
    """Return the deterministic three-satellite coherence split."""

    if mode == "equal":
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    if mode != "custom":
        raise ValueError(f"unsupported expansion_distribution_mode {mode!r}")
    if custom_weights is None or len(custom_weights) != 3:
        raise ValueError("custom expansion weights must contain exactly three values")
    normalized = tuple(float(value) for value in custom_weights)
    if any(value < 0.0 for value in normalized):
        raise ValueError("custom expansion weights must be non-negative")
    total = sum(normalized)
    if total <= 0.0:
        raise ValueError("custom expansion weights must sum to a positive value")
    return tuple(value / total for value in normalized)


def aggregate_bond_conductance(
    conductances: Iterable[float],
    *,
    fallback: float,
) -> float:
    """Use a geometric mean when defined and fall back to `w_bond` otherwise."""

    values = [max(1e-12, float(value)) for value in conductances if float(value) > 0.0]
    if not values:
        return float(fallback)
    return float(math.exp(sum(math.log(value) for value in values) / len(values)))


def boundary_reassignment_order(port_ids: Iterable[int]) -> tuple[int, ...]:
    """Prefer exact-preserving ports before the known center-port conflict case."""

    return tuple(sorted({int(port_id) for port_id in port_ids}, key=lambda port_id: (port_id == 5, port_id)))


def round_robin_column_order(extra_node_count: int) -> tuple[int, ...]:
    """Distribute planned extra nodes deterministically across the three columns."""

    return tuple(1 + (index % 3) for index in range(max(0, int(extra_node_count))))


__all__ = [
    "CANONICAL_CORE_SPINE_PORTS",
    "PRIMARY_SATELLITE_COLUMNS",
    "aggregate_bond_conductance",
    "boundary_reassignment_order",
    "compute_expansion_node_count",
    "normalize_expansion_weights",
    "round_robin_column_order",
]
