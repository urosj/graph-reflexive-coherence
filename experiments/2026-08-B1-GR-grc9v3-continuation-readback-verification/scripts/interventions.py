"""Clone-first intervention helpers; no runtime behavior is modified here."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class InterventionResult:
    state: Any
    changed_paths: tuple[tuple[str, ...], ...]
    rebuild_order: tuple[str, ...]


def apply_clone_intervention(
    state: Any,
    updates: Iterable[tuple[tuple[str, ...], Any]],
    *,
    rebuild_steps: Iterable[tuple[str, Callable[[Any], None]]] = (),
) -> InterventionResult:
    clone = deepcopy(state)
    changed: list[tuple[str, ...]] = []
    for path, value in updates:
        if not path:
            raise ValueError("intervention path must not be empty")
        target = clone
        for component in path[:-1]:
            target = target[component]
        target[path[-1]] = deepcopy(value)
        changed.append(path)
    rebuild_order: list[str] = []
    for name, callback in rebuild_steps:
        callback(clone)
        rebuild_order.append(name)
    return InterventionResult(clone, tuple(changed), tuple(rebuild_order))
