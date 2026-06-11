"""Explicit mutation and cache-invalidation contracts for graph backends."""

from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass, field
from typing import Any, Callable

from .types import GRCState


@dataclass(frozen=True, slots=True)
class CacheInvalidation:
    """Describe how a topology mutation invalidates derived cached quantities."""

    cache_keys: frozenset[str] = field(default_factory=frozenset)
    clear_all: bool = False
    reasons: tuple[str, ...] = ()


CacheInvalidationHook = Callable[[CacheInvalidation], None]


@dataclass(frozen=True, slots=True)
class GraphMutation:
    """Explicit record of one deterministic graph/storage mutation."""

    kind: str
    node_ids: tuple[int, ...] = ()
    edge_ids: tuple[int, ...] = ()
    cascade_edge_ids: tuple[int, ...] = ()
    invalidation: CacheInvalidation = field(default_factory=CacheInvalidation)


TOPOLOGY_MUTATION_INVALIDATION = CacheInvalidation(
    clear_all=True,
    reasons=("topology_mutation",),
)


def apply_cache_invalidation(
    cached_quantities: MutableMapping[str, Any], invalidation: CacheInvalidation
) -> None:
    """Apply one invalidation description to a cached-quantities mapping."""

    if invalidation.clear_all:
        cached_quantities.clear()
        return

    for cache_key in invalidation.cache_keys:
        cached_quantities.pop(cache_key, None)


def invalidate_state_cached_quantities(
    state: GRCState, invalidation: CacheInvalidation
) -> None:
    """Apply one invalidation description to `GRCState.cached_quantities`."""

    apply_cache_invalidation(state.cached_quantities, invalidation)
