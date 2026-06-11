"""Field-backed GRCV3 pressure-boundary selector helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any


SelectorPredicate = Callable[[Mapping[str, Any]], tuple[bool, Any]]


@dataclass(frozen=True)
class GRCV3SelectorResult:
    """One field-backed GRCV3 selector result."""

    selector_id: str
    passed: bool
    field_path: str
    observed_value: Any
    failure_kind: str = "passed"

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "selector_id": self.selector_id,
            "passed": self.passed,
            "field_path": self.field_path,
            "observed_value": self.observed_value,
            "failure_kind": self.failure_kind,
        }


@dataclass(frozen=True)
class GRCV3SelectorDefinition:
    """Minimal selector definition for pressure-boundary GRCV3 evidence."""

    selector_id: str
    field_path: str
    predicate: SelectorPredicate
    required_field_paths: tuple[str, ...]


def _get_path(payload: Mapping[str, Any], field_path: str, default: Any = None) -> Any:
    current: Any = payload
    for part in field_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return default
        current = current[part]
    return current


def _field_present(payload: Mapping[str, Any], field_path: str) -> bool:
    sentinel = object()
    return _get_path(payload, field_path, sentinel) is not sentinel


def _failure_kind(
    payload: Mapping[str, Any],
    selector: GRCV3SelectorDefinition,
    passed: bool,
) -> str:
    if passed:
        return "passed"
    if not all(_field_present(payload, field_path) for field_path in selector.required_field_paths):
        return "missing_surface"
    return "predicate_failed"


def _pressure_boundary_frontier_birth(
    payload: Mapping[str, Any],
) -> tuple[bool, Mapping[str, Any]]:
    summary = _get_path(payload, "family_extensions.grcv3.frontier_birth_summary", {})
    observed = dict(summary) if isinstance(summary, Mapping) else {}
    passed = (
        observed.get("frontier_birth_mode") == "active_frontier_pressure"
        and int(observed.get("pressure_boundary_birth_count", 0)) > 0
        and int(observed.get("frontier_birth_count", 0))
        == int(observed.get("pressure_boundary_birth_count", -1))
        and "pressure_boundary" in tuple(observed.get("frontier_sources_observed", ()))
    )
    return passed, observed


PRESSURE_BOUNDARY_FRONTIER_BIRTH_SELECTOR = GRCV3SelectorDefinition(
    selector_id="grcv3_pressure_boundary_frontier_birth",
    field_path="family_extensions.grcv3.frontier_birth_summary",
    predicate=_pressure_boundary_frontier_birth,
    required_field_paths=(
        "family_extensions.grcv3.frontier_birth_summary.frontier_birth_mode",
        "family_extensions.grcv3.frontier_birth_summary.frontier_birth_count",
        "family_extensions.grcv3.frontier_birth_summary.pressure_boundary_birth_count",
        "family_extensions.grcv3.frontier_birth_summary.frontier_sources_observed",
    ),
)


def validate_grcv3_pressure_boundary_frontier_birth(
    payload: Mapping[str, Any],
) -> GRCV3SelectorResult:
    """Validate pressure-boundary frontier-birth evidence on one run payload."""

    selector = PRESSURE_BOUNDARY_FRONTIER_BIRTH_SELECTOR
    passed, observed = selector.predicate(payload)
    return GRCV3SelectorResult(
        selector_id=selector.selector_id,
        passed=passed,
        field_path=selector.field_path,
        observed_value=observed,
        failure_kind=_failure_kind(payload, selector, passed),
    )


__all__ = [
    "GRCV3SelectorDefinition",
    "GRCV3SelectorResult",
    "PRESSURE_BOUNDARY_FRONTIER_BIRTH_SELECTOR",
    "validate_grcv3_pressure_boundary_frontier_birth",
]
