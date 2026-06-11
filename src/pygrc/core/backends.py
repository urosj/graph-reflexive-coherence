"""Shared backend-selection primitives for PyGRC families.

The common layer owns:

- backend category vocabulary,
- backend selection representation,
- canonical payload shape for params/snapshots,
- and generic validation helpers.

Actual backend formulas remain family-local.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Final
import re

from .digests import digest_canonical_data
from .serialization import canonicalize_json_value


BACKEND_SELECTIONS_KEY: Final[str] = "backend_selections"

GEOMETRY_BACKEND_CATEGORY: Final[str] = "geometry"
METRIC_BACKEND_CATEGORY: Final[str] = "metric"
CURVATURE_BACKEND_CATEGORY: Final[str] = "curvature"
SPARK_BACKEND_CATEGORY: Final[str] = "spark"
BIRTH_BACKEND_CATEGORY: Final[str] = "birth"
SPLIT_BACKEND_CATEGORY: Final[str] = "split"
BOUNDARY_BACKEND_CATEGORY: Final[str] = "boundary"
DIFFERENTIAL_SUMMARY_BACKEND_CATEGORY: Final[str] = "differential_summary"
HIERARCHY_UPDATE_BACKEND_CATEGORY: Final[str] = "hierarchy_update"
CHOICE_BACKEND_CATEGORY: Final[str] = "choice"
CAUSAL_BACKEND_CATEGORY: Final[str] = "causal"
COARSE_GRAINING_BACKEND_CATEGORY: Final[str] = "coarse_graining"

COMMON_BACKEND_CATEGORIES: Final[tuple[str, ...]] = (
    GEOMETRY_BACKEND_CATEGORY,
    METRIC_BACKEND_CATEGORY,
    CURVATURE_BACKEND_CATEGORY,
    SPARK_BACKEND_CATEGORY,
    BIRTH_BACKEND_CATEGORY,
    SPLIT_BACKEND_CATEGORY,
    BOUNDARY_BACKEND_CATEGORY,
    DIFFERENTIAL_SUMMARY_BACKEND_CATEGORY,
    HIERARCHY_UPDATE_BACKEND_CATEGORY,
    CHOICE_BACKEND_CATEGORY,
    CAUSAL_BACKEND_CATEGORY,
    COARSE_GRAINING_BACKEND_CATEGORY,
)

_BACKEND_TOKEN_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def _normalize_backend_token(value: str, *, context: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{context} must be a string")
    if value != value.strip():
        raise ValueError(f"{context} must not contain leading or trailing whitespace")
    if not value:
        raise ValueError(f"{context} must not be empty")
    if not _BACKEND_TOKEN_PATTERN.fullmatch(value):
        raise ValueError(
            f"{context} must match the snake_case token pattern [a-z][a-z0-9_]*"
        )
    return value


def _freeze_backend_params(
    params: Mapping[str, Any] | None,
) -> MappingProxyType[str, Any]:
    if params is None:
        return MappingProxyType({})
    if not isinstance(params, Mapping):
        raise TypeError("backend params must be a mapping")
    canonical = canonicalize_json_value(dict(params))
    if not isinstance(canonical, dict):
        raise TypeError("backend params must canonicalize to a mapping")
    return MappingProxyType(dict(canonical))


@dataclass(frozen=True)
class BackendSelection:
    """One canonical backend selection for one backend category."""

    category: str
    name: str
    params: MappingProxyType[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        category = _normalize_backend_token(self.category, context="backend category")
        name = _normalize_backend_token(self.name, context="backend name")
        params = _freeze_backend_params(self.params)
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "params", params)

    def canonical_payload(self) -> dict[str, Any]:
        """Return the canonical JSON-safe payload for this selection."""

        return {
            "category": self.category,
            "name": self.name,
            "params": canonicalize_json_value(dict(self.params)),
        }

    def canonical_identity(self) -> str:
        """Return the canonical identity digest for this backend selection."""

        return digest_canonical_data(self.canonical_payload())


def build_backend_selection(
    *,
    category: str,
    name: str,
    params: Mapping[str, Any] | None = None,
) -> BackendSelection:
    """Construct one validated backend selection."""

    return BackendSelection(category=category, name=name, params=_freeze_backend_params(params))


def build_backend_selection_payload(
    selections: Sequence[BackendSelection] | Mapping[str, BackendSelection],
) -> dict[str, dict[str, Any]]:
    """Build the canonical params/snapshot payload for selected backends.

    The payload is keyed by backend category and stores only the backend name
    plus backend params because the category is already carried by the mapping
    key.
    """

    if isinstance(selections, Mapping):
        items = list(selections.items())
    else:
        items = [(selection.category, selection) for selection in selections]

    payload: dict[str, dict[str, Any]] = {}
    for category, selection in sorted(items, key=lambda item: item[0]):
        if not isinstance(selection, BackendSelection):
            raise TypeError("backend selection payload expects BackendSelection values")
        if category != selection.category:
            raise ValueError(
                f"backend selection mapping key {category!r} does not match "
                f"selection.category {selection.category!r}"
            )
        if category in payload:
            raise ValueError(f"duplicate backend selection category {category!r}")
        payload[category] = {
            "name": selection.name,
            "params": canonicalize_json_value(dict(selection.params)),
        }
    return payload


def restore_backend_selections(
    payload: Mapping[str, Any],
) -> dict[str, BackendSelection]:
    """Restore backend selections from one canonical payload mapping."""

    if not isinstance(payload, Mapping):
        raise TypeError("backend selection payload must be a mapping")

    selections: dict[str, BackendSelection] = {}
    for category, value in sorted(payload.items()):
        if not isinstance(category, str):
            raise TypeError("backend selection payload must use string category keys")
        if not isinstance(value, Mapping):
            raise TypeError(
                f"backend selection payload for category {category!r} must be a mapping"
            )
        name = value.get("name")
        params = value.get("params", {})
        if not isinstance(name, str):
            raise TypeError(
                f"backend selection payload for category {category!r} must include string name"
            )
        if not isinstance(params, Mapping):
            raise TypeError(
                f"backend selection payload for category {category!r} must include mapping params"
            )
        selection = build_backend_selection(
            category=category,
            name=name,
            params=dict(params),
        )
        selections[category] = selection
    return selections


def validate_supported_backend_selections(
    selections: Sequence[BackendSelection] | Mapping[str, BackendSelection],
    *,
    allowed_names_by_category: Mapping[str, Sequence[str] | set[str]],
) -> None:
    """Validate selections against one family's supported backend matrix."""

    if isinstance(selections, Mapping):
        items = selections.items()
    else:
        items = ((selection.category, selection) for selection in selections)

    for category, selection in items:
        if category not in allowed_names_by_category:
            raise ValueError(f"unsupported backend category {category!r}")
        if not isinstance(selection, BackendSelection):
            raise TypeError("backend selections must contain BackendSelection values")
        allowed_names = set(allowed_names_by_category[category])
        if selection.name not in allowed_names:
            raise ValueError(
                f"unsupported backend name {selection.name!r} for category "
                f"{category!r}; expected one of {sorted(allowed_names)!r}"
            )


__all__ = [
    "BACKEND_SELECTIONS_KEY",
    "BIRTH_BACKEND_CATEGORY",
    "BOUNDARY_BACKEND_CATEGORY",
    "CAUSAL_BACKEND_CATEGORY",
    "CHOICE_BACKEND_CATEGORY",
    "COMMON_BACKEND_CATEGORIES",
    "COARSE_GRAINING_BACKEND_CATEGORY",
    "CURVATURE_BACKEND_CATEGORY",
    "DIFFERENTIAL_SUMMARY_BACKEND_CATEGORY",
    "GEOMETRY_BACKEND_CATEGORY",
    "HIERARCHY_UPDATE_BACKEND_CATEGORY",
    "METRIC_BACKEND_CATEGORY",
    "SPARK_BACKEND_CATEGORY",
    "SPLIT_BACKEND_CATEGORY",
    "BackendSelection",
    "build_backend_selection",
    "build_backend_selection_payload",
    "restore_backend_selections",
    "validate_supported_backend_selections",
]
