"""Field-backed selector validation for GRC9V3 discovery telemetry."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.telemetry import GRC9V3_TELEMETRY_CONTRACT_VERSION

from .grc9_manifest import is_generated_lane_name, is_session_id


GRC9V3_SELECTOR_VALIDATION_VERSION = "grc9v3_selector_validation_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9v3/phenomenology_discovery/sessions")
DISCOVERY_PROGRAM = "grc9v3_phenomenology_discovery"
DISCOVERY_TRACK = "phenomenology_discovery"
DISCOVERY_SOURCE_REFERENCE = "implementation/GRC9V3-PhenomenologyDiscovery-Plan.md"


SelectorPredicate = Callable[[Mapping[str, Any]], tuple[bool, Any]]


@dataclass(frozen=True)
class GRC9V3SelectorDefinition:
    selector_id: str
    surface: str
    query: str
    expected_type: str
    field_path: str
    predicate: SelectorPredicate
    required_field_paths: tuple[str, ...] = ()

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "selector_id": self.selector_id,
            "surface": self.surface,
            "query": self.query,
            "expected_type": self.expected_type,
            "field_path": self.field_path,
            "required_field_paths": list(self.required_field_paths),
        }


@dataclass(frozen=True)
class GRC9V3SelectorResult:
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
class GRC9V3LaneSelectorValidation:
    session_id: str
    lane_name: str
    control_role: str
    run_id: str
    seed_name: str
    profile: str
    requested_steps: int
    event_counts_by_kind: Mapping[str, int]
    expected_selector_ids: tuple[str, ...]
    selector_results: tuple[GRC9V3SelectorResult, ...]
    confidence_score: int
    confidence_label: str
    motif_id: str | None
    notes: Mapping[str, str]

    @property
    def passed_selector_ids(self) -> tuple[str, ...]:
        return tuple(
            result.selector_id for result in self.selector_results if result.passed
        )

    @property
    def missing_selector_ids(self) -> tuple[str, ...]:
        passed = set(self.passed_selector_ids)
        return tuple(
            selector_id
            for selector_id in self.expected_selector_ids
            if selector_id not in passed
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "lane_name": self.lane_name,
            "control_role": self.control_role,
            "run_id": self.run_id,
            "seed_name": self.seed_name,
            "profile": self.profile,
            "requested_steps": self.requested_steps,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "expected_selector_ids": list(self.expected_selector_ids),
            "selector_results": [item.to_mapping() for item in self.selector_results],
            "passed_selector_ids": list(self.passed_selector_ids),
            "missing_selector_ids": list(self.missing_selector_ids),
            "missing_surface_selector_ids": [
                item.selector_id
                for item in self.selector_results
                if item.failure_kind == "missing_surface"
            ],
            "confidence_score": self.confidence_score,
            "confidence_label": self.confidence_label,
            "motif_id": self.motif_id,
            "notes": dict(self.notes),
        }


@dataclass(frozen=True)
class GRC9V3SelectorValidationSession:
    session_id: str
    source_session_ids: tuple[str, ...]
    validations: tuple[GRC9V3LaneSelectorValidation, ...]
    manifest_path: str
    iteration: str = "I06_field_backed_selectors"

    @property
    def no_expectation_lanes(self) -> tuple[str, ...]:
        return tuple(
            f"{validation.session_id}/{validation.lane_name}"
            for validation in self.validations
            if not validation.expected_selector_ids
        )

    def to_mapping(self) -> Mapping[str, Any]:
        labels = Counter(validation.confidence_label for validation in self.validations)
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "source_session_ids": list(self.source_session_ids),
            "lane_count": len(self.validations),
            "motif_count": sum(1 for item in self.validations if item.motif_id),
            "strong_candidate_count": labels.get("strong_candidate", 0),
            "candidate_count": labels.get("candidate", 0),
            "weak_candidate_count": labels.get("weak_candidate", 0),
            "rejected_count": labels.get("rejected", 0),
            "missing_surface_count": sum(
                1
                for validation in self.validations
                for result in validation.selector_results
                if result.failure_kind == "missing_surface"
            ),
            "no_expectation_lane_count": len(self.no_expectation_lanes),
            "no_expectation_lanes": list(self.no_expectation_lanes),
            "validations": [item.to_mapping() for item in self.validations],
            "manifest_path": self.manifest_path,
        }


def _get_path(payload: Mapping[str, Any], path: str, default: Any = None) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        else:
            return default
    return current


def _grc9v3_path(path: str) -> str:
    return f"family_extensions.grc9v3.{path}"


def _summary_path(path: str) -> str:
    return _grc9v3_path(path)


def _step_path(path: str) -> str:
    return _grc9v3_path(path)


def _event_count(kind: str) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        count = int(lane["event_counts_by_kind"].get(kind, 0))
        return count > 0, count

    return predicate


def _event_count_zero(kind: str) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        count = int(lane["event_counts_by_kind"].get(kind, 0))
        return count == 0, count

    return predicate


def _no_lifecycle_events(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    total = sum(int(value) for value in lane["event_counts_by_kind"].values())
    return total == 0, total


def _summary_bool(path: str, expected: bool = True) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        value = _get_path(lane["summary"], path)
        return value is expected, value

    return predicate


def _summary_count_at_least(path: str, count: int) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        value = int(_get_path(lane["summary"], path, 0) or 0)
        return value >= count, value

    return predicate


def _summary_count_zero(path: str) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        value = int(_get_path(lane["summary"], path, 0) or 0)
        return value == 0, value

    return predicate


def _step_values(lane: Mapping[str, Any], path: str) -> tuple[Any, ...]:
    return tuple(_get_path(step, path) for step in lane["steps"])


def _any_step(path: str, test: Callable[[Any], bool]) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        values = _step_values(lane, path)
        matching = [value for value in values if test(value)]
        return bool(matching), matching[0] if matching else list(values[:3])

    return predicate


def _all_steps(path: str, test: Callable[[Any], bool]) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        values = _step_values(lane, path)
        return bool(values) and all(test(value) for value in values), list(values[:5])

    return predicate


def _max_step_float(path: str) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        values = [
            float(value)
            for value in _step_values(lane, path)
            if isinstance(value, int | float) and not isinstance(value, bool)
        ]
        maximum = max(values) if values else None
        return maximum is not None and maximum > 0.0, maximum

    return predicate


def _step_int_max_at_least(path: str, count: int) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        values = [
            int(value)
            for value in _step_values(lane, path)
            if isinstance(value, int) and not isinstance(value, bool)
        ]
        maximum = max(values) if values else 0
        return maximum >= count, maximum

    return predicate


def _field_present(lane: Mapping[str, Any], field_path: str) -> bool:
    if field_path == "event_counts_by_kind":
        return "event_counts_by_kind" in lane
    if "/" in field_path:
        return all(_field_present(lane, part) for part in field_path.split("/"))
    if _get_path(lane["summary"], field_path) is not None:
        return True
    if any(_get_path(step, field_path) is not None for step in lane["steps"]):
        return True
    return any(_get_path(event, field_path) is not None for event in lane["events"])


def _failure_kind(
    lane: Mapping[str, Any],
    selector: GRC9V3SelectorDefinition,
    passed: bool,
) -> str:
    if passed:
        return "passed"
    required = selector.required_field_paths or (selector.field_path,)
    if not all(_field_present(lane, field_path) for field_path in required):
        return "missing_surface"
    return "predicate_failed"


def _contract_version_valid(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    summary_version = _get_path(lane["summary"], _summary_path("contract_version"))
    step_versions = _step_values(lane, _step_path("contract_version"))
    event_versions = tuple(
        _get_path(event, _grc9v3_path("contract_version")) for event in lane["events"]
    )
    all_versions = (summary_version, *step_versions, *event_versions)
    return (
        bool(all_versions)
        and all(
            version == GRC9V3_TELEMETRY_CONTRACT_VERSION for version in all_versions
        ),
        list(all_versions),
    )


def _lane_naming_valid(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    lane_name = str(lane["lane_name"])
    return is_generated_lane_name(lane_name), lane_name


def _appendix_e_absent(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    summary = _get_path(
        lane["summary"],
        _summary_path("representative_appendix_e_summary"),
    )
    completed = int(
        _get_path(
            lane["summary"],
            _summary_path("lifecycle_event_counts.hybrid_spark_completed_count"),
            0,
        )
        or 0
    )
    return summary is None and completed == 0, {
        "summary_present": summary is not None,
        "hybrid_spark_completed_count": completed,
    }


def _appendix_e_hierarchy_recorded(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    summary = _get_path(
        lane["summary"],
        _summary_path("representative_appendix_e_summary"),
        {},
    )
    parent = _get_path(summary, "hierarchy_parent")
    children = tuple(_get_path(summary, "hierarchy_children", ()) or ())
    return parent is not None and len(children) >= 2, {
        "hierarchy_parent": parent,
        "hierarchy_children": list(children),
    }


def _budget_adjustment_observed(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    observations: list[Mapping[str, Any]] = []
    for step in lane["steps"]:
        budget = _get_path(step, _step_path("budget_correction"), {}) or {}
        before = float(budget.get("budget_before", 0.0) or 0.0)
        after = float(budget.get("budget_after", 0.0) or 0.0)
        error = abs(float(budget.get("budget_error", 0.0) or 0.0))
        observations.append(
            {"budget_before": before, "budget_after": after, "budget_error": error}
        )
    passed = any(
        abs(item["budget_before"] - item["budget_after"]) > 1e-9
        and item["budget_error"] < 1e-8
        for item in observations
    )
    return passed, observations[:3]


def _budget_no_adjustment(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    observations: list[Mapping[str, Any]] = []
    for step in lane["steps"]:
        budget = _get_path(step, _step_path("budget_correction"), {}) or {}
        before = float(budget.get("budget_before", 0.0) or 0.0)
        after = float(budget.get("budget_after", 0.0) or 0.0)
        observations.append({"budget_before": before, "budget_after": after})
    return (
        bool(observations)
        and all(
            abs(item["budget_before"] - item["budget_after"]) < 1e-9
            for item in observations
        ),
        observations[:3],
    )


def _budget_balanced(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    value = float(
        _get_path(
            lane["summary"],
            _summary_path("final_budget_summary.budget_error"),
            0.0,
        )
        or 0.0
    )
    return abs(value) < 1e-8, value


def _hessian_backend_is(expected: str) -> SelectorPredicate:
    path = _step_path("backend_config.hessian_backend")

    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        values = _step_values(lane, path)
        return bool(values) and all(value == expected for value in values), list(values)

    return predicate


def _wls_available(expected: bool) -> SelectorPredicate:
    path = _step_path("row_basis_differential.weighted_least_squares_hessian_available")

    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        values = _step_values(lane, path)
        return bool(values) and all(value is expected for value in values), list(values)

    return predicate


def _transport_potential_range(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    observations: list[Mapping[str, float]] = []
    for step in lane["steps"]:
        transport = _get_path(step, _step_path("transport"), {}) or {}
        minimum = transport.get("potential_min")
        maximum = transport.get("potential_max")
        if isinstance(minimum, int | float) and isinstance(maximum, int | float):
            observations.append(
                {"potential_min": float(minimum), "potential_max": float(maximum)}
            )
    return (
        any(item["potential_min"] <= item["potential_max"] for item in observations),
        observations[:3],
    )


def _transport_signature(lane: Mapping[str, Any]) -> Mapping[str, float]:
    flux_values = [
        float(value)
        for value in _step_values(lane, _step_path("transport.flux_abs_sum"))
        if isinstance(value, int | float) and not isinstance(value, bool)
    ]
    potential_spans: list[float] = []
    anisotropy_values: list[float] = []
    for step in lane["steps"]:
        transport = _get_path(step, _step_path("transport"), {}) or {}
        minimum = transport.get("potential_min")
        maximum = transport.get("potential_max")
        if isinstance(minimum, int | float) and isinstance(maximum, int | float):
            potential_spans.append(abs(float(maximum) - float(minimum)))
        tensor_anisotropy = _get_path(
            step,
            _step_path("hybrid_tensor.tensor_anisotropy_max"),
        )
        if isinstance(tensor_anisotropy, int | float) and not isinstance(
            tensor_anisotropy,
            bool,
        ):
            anisotropy_values.append(float(tensor_anisotropy))
    return {
        "flux_abs_sum_max": max(flux_values) if flux_values else 0.0,
        "potential_span_max": max(potential_spans) if potential_spans else 0.0,
        "tensor_anisotropy_max": max(anisotropy_values) if anisotropy_values else 0.0,
    }


def _paired_lane(lane: Mapping[str, Any], lane_name: str) -> Mapping[str, Any] | None:
    return _get_path(lane, f"paired_lanes.{lane_name}")


def _transport_positive_reroute_signature(
    lane: Mapping[str, Any],
) -> tuple[bool, Any]:
    pair = _paired_lane(lane, "transport_basin_rerouting_negative_control")
    if pair is None:
        return False, {"missing_pair": "transport_basin_rerouting_negative_control"}
    current = _transport_signature(lane)
    paired = _transport_signature(pair)
    passed = (
        current["potential_span_max"] > paired["potential_span_max"] * 2.0
        and current["flux_abs_sum_max"] < paired["flux_abs_sum_max"] * 0.5
    )
    return passed, {"current": dict(current), "paired_negative": dict(paired)}


def _transport_negative_balanced_signature(
    lane: Mapping[str, Any],
) -> tuple[bool, Any]:
    pair = _paired_lane(lane, "transport_basin_rerouting_positive_control")
    if pair is None:
        return False, {"missing_pair": "transport_basin_rerouting_positive_control"}
    current = _transport_signature(lane)
    paired = _transport_signature(pair)
    passed = (
        current["potential_span_max"] * 2.0 < paired["potential_span_max"]
        and current["flux_abs_sum_max"] > paired["flux_abs_sum_max"] * 2.0
    )
    return passed, {"current": dict(current), "paired_positive": dict(paired)}


def _coarse_cache_state_recorded(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    values = tuple(
        value
        for value in _step_values(lane, _step_path("coarse_cache.coarse_cache_state"))
        if value is not None
    )
    return bool(values), list(values[:5])


def _coarse_cache_invalidated(expected: bool) -> SelectorPredicate:
    path = _step_path("coarse_cache.coarse_cache_invalidated")

    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        values = _step_values(lane, path)
        if expected:
            return any(value is True for value in values), list(values)
        return bool(values) and all(value is False for value in values), list(values)

    return predicate


def _coarse_cache_invalidation_reason_recorded(
    lane: Mapping[str, Any],
) -> tuple[bool, Any]:
    values = tuple(
        str(value)
        for value in _step_values(
            lane,
            _step_path("coarse_cache.coarse_cache_invalidation_reason"),
        )
        if value is not None
    )
    meaningful = [
        value for value in values if value and value not in {"none", "None"}
    ]
    return bool(meaningful), list(values[:5])


def _candidate_gate_evidence(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    evidence: list[Mapping[str, Any]] = []
    for step in lane["steps"]:
        spark = _get_path(step, _step_path("hybrid_spark_state"), {}) or {}
        evidence.append(
            {
                "candidate_pass_rate": spark.get("candidate_pass_rate"),
                "saturation_gate": spark.get("last_candidate_saturation_gate"),
                "basin_interior_gate": spark.get("last_candidate_basin_interior_gate"),
                "signed_hessian_gate": spark.get("last_candidate_signed_hessian_gate"),
            }
        )
    passed = any(
        bool(item["saturation_gate"])
        and bool(item["basin_interior_gate"])
        and bool(item["signed_hessian_gate"])
        for item in evidence
    )
    return passed, evidence[:3]


def _selector(
    selector_id: str,
    *,
    surface: str,
    query: str,
    expected_type: str,
    field_path: str,
    predicate: SelectorPredicate,
    required_field_paths: Sequence[str] | None = None,
) -> GRC9V3SelectorDefinition:
    return GRC9V3SelectorDefinition(
        selector_id=selector_id,
        surface=surface,
        query=query,
        expected_type=expected_type,
        field_path=field_path,
        predicate=predicate,
        required_field_paths=tuple(required_field_paths or (field_path,)),
    )


GRC9V3_SELECTORS: Mapping[str, GRC9V3SelectorDefinition] = {
    item.selector_id: item
    for item in (
        _selector(
            "contract_version_valid",
            surface="summary/steps/events",
            query="all GRC9V3 extension contract_version fields match the current contract",
            expected_type="bool",
            field_path="family_extensions.grc9v3.contract_version",
            predicate=_contract_version_valid,
        ),
        _selector(
            "lane_naming_valid",
            surface="summary",
            query="lane name follows <seed_family>_<control_role>",
            expected_type="bool",
            field_path="family_extensions.discovery.lane_name",
            predicate=_lane_naming_valid,
        ),
        _selector(
            "hybrid_spark_candidate_present",
            surface="events/summary",
            query="hybrid spark candidate lifecycle event count is positive",
            expected_type="int",
            field_path=_summary_path("lifecycle_event_counts.hybrid_spark_candidate_count"),
            predicate=_event_count("hybrid_spark_candidate"),
        ),
        _selector(
            "hybrid_spark_completed_present",
            surface="events/summary",
            query="hybrid spark completed lifecycle event count is positive",
            expected_type="int",
            field_path=_summary_path("lifecycle_event_counts.hybrid_spark_completed_count"),
            predicate=_event_count("hybrid_spark_completed"),
        ),
        _selector(
            "mechanical_expansion_present",
            surface="events/summary",
            query="hybrid mechanical expansion lifecycle event count is positive",
            expected_type="int",
            field_path=_summary_path("lifecycle_event_counts.hybrid_mechanical_expansion_count"),
            predicate=_event_count("hybrid_mechanical_expansion"),
        ),
        _selector(
            "candidate_gate_evidence_present",
            surface="steps",
            query="last candidate saturation, basin-interior, and signed-Hessian gates pass",
            expected_type="mapping",
            field_path=_step_path("hybrid_spark_state"),
            predicate=_candidate_gate_evidence,
        ),
        _selector(
            "no_lifecycle_events",
            surface="events",
            query="lane emitted no lifecycle events",
            expected_type="int",
            field_path="event_counts_by_kind",
            predicate=_no_lifecycle_events,
            required_field_paths=("event_counts_by_kind",),
        ),
        _selector(
            "appendix_e_completed",
            surface="run_summary",
            query="representative Appendix E summary records completed spark",
            expected_type="bool",
            field_path=_summary_path("representative_appendix_e_summary.spark_completed"),
            predicate=_summary_bool(
                _summary_path("representative_appendix_e_summary.spark_completed")
            ),
        ),
        _selector(
            "appendix_e_daughter_sinks",
            surface="run_summary",
            query="representative Appendix E summary records two daughter sinks",
            expected_type="int",
            field_path=_summary_path("representative_appendix_e_summary.daughter_sink_count"),
            predicate=_summary_count_at_least(
                _summary_path("representative_appendix_e_summary.daughter_sink_count"),
                2,
            ),
        ),
        _selector(
            "appendix_e_hierarchy_recorded",
            surface="run_summary",
            query="representative Appendix E summary records hierarchy parent and children",
            expected_type="mapping",
            field_path=_summary_path("representative_appendix_e_summary"),
            predicate=_appendix_e_hierarchy_recorded,
        ),
        _selector(
            "appendix_e_no_completion",
            surface="run_summary/events",
            query="Appendix E summary is absent and completed spark count is zero",
            expected_type="mapping",
            field_path=_summary_path("representative_appendix_e_summary"),
            predicate=_appendix_e_absent,
            required_field_paths=(
                _summary_path("lifecycle_event_counts.hybrid_spark_completed_count"),
            ),
        ),
        _selector(
            "choice_detected_present",
            surface="events/summary",
            query="choice detection lifecycle event count is positive",
            expected_type="int",
            field_path=_summary_path("lifecycle_event_counts.choice_detected_count"),
            predicate=_event_count("choice_detected"),
        ),
        _selector(
            "collapse_event_present",
            surface="events/summary",
            query="collapse lifecycle event count is positive",
            expected_type="int",
            field_path=_summary_path("lifecycle_event_counts.collapse_count"),
            predicate=_event_count("collapse"),
        ),
        _selector(
            "no_collapse_events",
            surface="events/summary",
            query="collapse lifecycle event count is zero",
            expected_type="int",
            field_path=_summary_path("lifecycle_event_counts.collapse_count"),
            predicate=_event_count_zero("collapse"),
        ),
        _selector(
            "collapse_registry_present",
            surface="run_summary",
            query="final choice/collapse summary records a collapse registry entry",
            expected_type="int",
            field_path=_summary_path(
                "final_choice_collapse_summary.collapse_registry_count"
            ),
            predicate=_summary_count_at_least(
                _summary_path(
                    "final_choice_collapse_summary.collapse_registry_count"
                ),
                1,
            ),
        ),
        _selector(
            "choice_regime_present",
            surface="run_summary",
            query="final choice/collapse summary records an unresolved choice regime",
            expected_type="int",
            field_path=_summary_path("final_choice_collapse_summary.choice_regime_count"),
            predicate=_summary_count_at_least(
                _summary_path("final_choice_collapse_summary.choice_regime_count"),
                1,
            ),
        ),
        _selector(
            "growth_event_present",
            surface="events/summary",
            query="growth lifecycle event count is positive",
            expected_type="int",
            field_path=_summary_path("lifecycle_event_counts.growth_count"),
            predicate=_event_count("growth"),
        ),
        _selector(
            "no_growth_events",
            surface="events/summary",
            query="growth lifecycle event count is zero",
            expected_type="int",
            field_path=_summary_path("lifecycle_event_counts.growth_count"),
            predicate=_event_count_zero("growth"),
        ),
        _selector(
            "birth_probability_recorded",
            surface="steps",
            query="growth step state records a birth probability",
            expected_type="float",
            field_path=_step_path("growth_state.last_birth_probability"),
            predicate=_max_step_float(_step_path("growth_state.last_birth_probability")),
        ),
        _selector(
            "growth_child_recorded",
            surface="steps",
            query="growth step state records the attached child node id",
            expected_type="int",
            field_path=_step_path("growth_state.last_child_node_id"),
            predicate=_any_step(
                _step_path("growth_state.last_child_node_id"),
                lambda value: isinstance(value, int) and not isinstance(value, bool),
            ),
        ),
        _selector(
            "budget_adjustment_observed",
            surface="steps",
            query="budget_correction records a before/after correction with balanced error",
            expected_type="mapping",
            field_path=_step_path("budget_correction"),
            predicate=_budget_adjustment_observed,
        ),
        _selector(
            "budget_no_adjustment",
            surface="steps",
            query="budget_correction before/after values remain unchanged",
            expected_type="mapping",
            field_path=_step_path("budget_correction"),
            predicate=_budget_no_adjustment,
        ),
        _selector(
            "budget_balanced",
            surface="run_summary",
            query="final budget error is near zero",
            expected_type="float",
            field_path=_summary_path("final_budget_summary.budget_error"),
            predicate=_budget_balanced,
        ),
        _selector(
            "post_expansion_budget_check_available",
            surface="steps",
            query="post-expansion budget check was recorded after mechanical refinement",
            expected_type="bool",
            field_path=_step_path(
                "budget_correction.post_expansion_budget_check_available"
            ),
            predicate=_any_step(
                _step_path("budget_correction.post_expansion_budget_check_available"),
                lambda value: value is True,
            ),
        ),
        _selector(
            "hessian_row_basis_backend",
            surface="steps",
            query="backend_config selects row_basis_diagonal Hessian backend",
            expected_type="string",
            field_path=_step_path("backend_config.hessian_backend"),
            predicate=_hessian_backend_is("row_basis_diagonal"),
        ),
        _selector(
            "hessian_weighted_least_squares_backend",
            surface="steps",
            query="backend_config selects weighted_least_squares Hessian backend",
            expected_type="string",
            field_path=_step_path("backend_config.hessian_backend"),
            predicate=_hessian_backend_is("weighted_least_squares"),
        ),
        _selector(
            "weighted_least_squares_unavailable",
            surface="steps",
            query="row_basis_differential reports WLS Hessian unavailable",
            expected_type="bool",
            field_path=_step_path(
                "row_basis_differential.weighted_least_squares_hessian_available"
            ),
            predicate=_wls_available(False),
        ),
        _selector(
            "weighted_least_squares_available",
            surface="steps",
            query="row_basis_differential reports WLS Hessian available",
            expected_type="bool",
            field_path=_step_path(
                "row_basis_differential.weighted_least_squares_hessian_available"
            ),
            predicate=_wls_available(True),
        ),
        _selector(
            "tensor_trace_present",
            surface="steps",
            query="hybrid tensor trace mean is available and positive",
            expected_type="float",
            field_path=_step_path("hybrid_tensor.tensor_trace_mean"),
            predicate=_max_step_float(_step_path("hybrid_tensor.tensor_trace_mean")),
        ),
        _selector(
            "tensor_anisotropy_present",
            surface="steps",
            query="hybrid tensor anisotropy is available and positive",
            expected_type="float",
            field_path=_step_path("hybrid_tensor.tensor_anisotropy_max"),
            predicate=_max_step_float(_step_path("hybrid_tensor.tensor_anisotropy_max")),
        ),
        _selector(
            "row_mismatch_sum_present",
            surface="steps",
            query="hybrid tensor row mismatch sum is available and positive",
            expected_type="float",
            field_path=_step_path("hybrid_tensor.row_mismatch_sum_max"),
            predicate=_max_step_float(_step_path("hybrid_tensor.row_mismatch_sum_max")),
        ),
        _selector(
            "tensor_hotspot_sample_present",
            surface="steps",
            query="hybrid tensor hotspot node id sample is non-empty",
            expected_type="list",
            field_path=_step_path("hybrid_tensor.tensor_hotspot_node_ids_sample"),
            predicate=_any_step(
                _step_path("hybrid_tensor.tensor_hotspot_node_ids_sample"),
                lambda value: isinstance(value, Sequence)
                and not isinstance(value, str)
                and len(value) > 0,
            ),
        ),
        _selector(
            "transport_flux_present",
            surface="steps",
            query="transport flux absolute sum is available and positive",
            expected_type="float",
            field_path=_step_path("transport.flux_abs_sum"),
            predicate=_max_step_float(_step_path("transport.flux_abs_sum")),
        ),
        _selector(
            "transport_potential_range_present",
            surface="steps",
            query="transport potential min/max fields are available",
            expected_type="mapping",
            field_path=_step_path("transport.potential_min/potential_max"),
            predicate=_transport_potential_range,
            required_field_paths=(
                _step_path("transport.potential_min"),
                _step_path("transport.potential_max"),
            ),
        ),
        _selector(
            "transport_positive_reroute_signature",
            surface="paired_steps",
            query="positive transport control has larger potential span and lower flux than its paired negative control",
            expected_type="mapping",
            field_path=_step_path("transport.flux_abs_sum"),
            predicate=_transport_positive_reroute_signature,
            required_field_paths=(
                _step_path("transport.flux_abs_sum"),
                _step_path("transport.potential_min"),
                _step_path("transport.potential_max"),
            ),
        ),
        _selector(
            "transport_negative_balanced_signature",
            surface="paired_steps",
            query="negative transport control preserves the paired opposite transport signature",
            expected_type="mapping",
            field_path=_step_path("transport.flux_abs_sum"),
            predicate=_transport_negative_balanced_signature,
            required_field_paths=(
                _step_path("transport.flux_abs_sum"),
                _step_path("transport.potential_min"),
                _step_path("transport.potential_max"),
            ),
        ),
        _selector(
            "positive_flux_edges_present",
            surface="steps",
            query="transport positive flux edge count is positive",
            expected_type="int",
            field_path=_step_path("transport.positive_flux_edge_count"),
            predicate=_step_int_max_at_least(
                _step_path("transport.positive_flux_edge_count"),
                1,
            ),
        ),
        _selector(
            "negative_flux_edges_present",
            surface="steps",
            query="transport negative flux edge count is positive",
            expected_type="int",
            field_path=_step_path("transport.negative_flux_edge_count"),
            predicate=_step_int_max_at_least(
                _step_path("transport.negative_flux_edge_count"),
                1,
            ),
        ),
        _selector(
            "sink_count_present",
            surface="steps/run_summary",
            query="identity/basin sink count is positive",
            expected_type="int",
            field_path=_summary_path("final_identity_basin_summary.sink_count"),
            predicate=_summary_count_at_least(
                _summary_path("final_identity_basin_summary.sink_count"),
                1,
            ),
        ),
        _selector(
            "basin_count_present",
            surface="steps/run_summary",
            query="identity/basin basin count is positive",
            expected_type="int",
            field_path=_summary_path("final_identity_basin_summary.basin_count"),
            predicate=_summary_count_at_least(
                _summary_path("final_identity_basin_summary.basin_count"),
                1,
            ),
        ),
        _selector(
            "geometric_seed_count_recorded",
            surface="steps/run_summary",
            query="identity/basin geometric seed count is recorded",
            expected_type="int",
            field_path=_summary_path("final_identity_basin_summary.geometric_seed_count"),
            predicate=_summary_count_at_least(
                _summary_path("final_identity_basin_summary.geometric_seed_count"),
                0,
            ),
        ),
        _selector(
            "validated_basin_count_recorded",
            surface="steps/run_summary",
            query="identity/basin validated basin count is recorded",
            expected_type="int",
            field_path=_summary_path("final_identity_basin_summary.validated_basin_count"),
            predicate=_summary_count_at_least(
                _summary_path("final_identity_basin_summary.validated_basin_count"),
                0,
            ),
        ),
        _selector(
            "previous_signed_hessian_available",
            surface="steps",
            query="row_basis_differential reports previous signed-Hessian history available",
            expected_type="bool",
            field_path=_step_path(
                "row_basis_differential.previous_min_signed_hessian_available"
            ),
            predicate=_any_step(
                _step_path(
                    "row_basis_differential.previous_min_signed_hessian_available"
                ),
                lambda value: value is True,
            ),
        ),
        _selector(
            "signed_crossing_status_recorded",
            surface="steps",
            query="hybrid_spark_state records signed crossing capability status; this selector does not claim a successful signed crossing",
            expected_type="string",
            field_path=_step_path("hybrid_spark_state.signed_crossing_status"),
            predicate=_any_step(
                _step_path("hybrid_spark_state.signed_crossing_status"),
                lambda value: isinstance(value, str) and bool(value),
            ),
        ),
        _selector(
            "coarse_cache_state_recorded",
            surface="steps",
            query="coarse_cache_state is recorded",
            expected_type="string",
            field_path=_step_path("coarse_cache.coarse_cache_state"),
            predicate=_coarse_cache_state_recorded,
        ),
        _selector(
            "coarse_cache_invalidated",
            surface="steps",
            query="coarse_cache_invalidated is true on at least one step",
            expected_type="bool",
            field_path=_step_path("coarse_cache.coarse_cache_invalidated"),
            predicate=_coarse_cache_invalidated(True),
        ),
        _selector(
            "coarse_cache_invalidation_reason_recorded",
            surface="steps",
            query="coarse_cache_invalidation_reason records a non-empty invalidation cause",
            expected_type="string",
            field_path=_step_path("coarse_cache.coarse_cache_invalidation_reason"),
            predicate=_coarse_cache_invalidation_reason_recorded,
        ),
        _selector(
            "coarse_cache_not_invalidated",
            surface="steps",
            query="coarse_cache_invalidated stays false on all steps",
            expected_type="bool",
            field_path=_step_path("coarse_cache.coarse_cache_invalidated"),
            predicate=_coarse_cache_invalidated(False),
        ),
    )
}


_COMMON_SELECTORS = (
    "contract_version_valid",
    "lane_naming_valid",
)

EXPECTED_SELECTORS_BY_LANE: Mapping[str, tuple[str, ...]] = {
    "hybrid_spark_gate_positive_control": (
        *_COMMON_SELECTORS,
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
        "candidate_gate_evidence_present",
        "tensor_trace_present",
        "previous_signed_hessian_available",
        "signed_crossing_status_recorded",
        "sink_count_present",
        "basin_count_present",
    ),
    "hybrid_spark_gate_negative_control": (
        *_COMMON_SELECTORS,
        "no_lifecycle_events",
    ),
    "spark_to_expansion_positive_control": (
        *_COMMON_SELECTORS,
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
        "sink_count_present",
        "basin_count_present",
    ),
    "spark_to_expansion_negative_control": (
        *_COMMON_SELECTORS,
        "no_lifecycle_events",
    ),
    "appendix_e_cell_division_positive_control": (
        *_COMMON_SELECTORS,
        "appendix_e_completed",
        "appendix_e_daughter_sinks",
        "appendix_e_hierarchy_recorded",
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
        "negative_flux_edges_present",
    ),
    "appendix_e_cell_division_negative_control": (
        *_COMMON_SELECTORS,
        "appendix_e_no_completion",
        "no_lifecycle_events",
    ),
    "choice_collapse_positive_control": (
        *_COMMON_SELECTORS,
        "collapse_event_present",
        "collapse_registry_present",
        "sink_count_present",
        "basin_count_present",
    ),
    "choice_collapse_negative_control": (
        *_COMMON_SELECTORS,
        "choice_detected_present",
        "no_collapse_events",
        "choice_regime_present",
    ),
    "growth_pressure_positive_control": (
        *_COMMON_SELECTORS,
        "growth_event_present",
        "birth_probability_recorded",
        "growth_child_recorded",
        "transport_flux_present",
        "positive_flux_edges_present",
        "basin_count_present",
    ),
    "growth_pressure_negative_control": (
        *_COMMON_SELECTORS,
        "no_growth_events",
    ),
    "budget_preservation_positive_control": (
        *_COMMON_SELECTORS,
        "budget_adjustment_observed",
        "budget_balanced",
    ),
    "budget_preservation_negative_control": (
        *_COMMON_SELECTORS,
        "budget_no_adjustment",
        "budget_balanced",
    ),
    "hessian_backend_comparison_baseline_control": (
        *_COMMON_SELECTORS,
        "hessian_row_basis_backend",
        "weighted_least_squares_unavailable",
        "tensor_trace_present",
        "previous_signed_hessian_available",
    ),
    "hessian_backend_comparison_positive_control": (
        *_COMMON_SELECTORS,
        "hessian_weighted_least_squares_backend",
        "weighted_least_squares_available",
        "tensor_trace_present",
        "previous_signed_hessian_available",
    ),
    "transport_basin_rerouting_positive_control": (
        *_COMMON_SELECTORS,
        "transport_flux_present",
        "transport_potential_range_present",
        "transport_positive_reroute_signature",
        "positive_flux_edges_present",
        "tensor_anisotropy_present",
        "row_mismatch_sum_present",
        "tensor_hotspot_sample_present",
        "sink_count_present",
        "basin_count_present",
        "geometric_seed_count_recorded",
        "validated_basin_count_recorded",
    ),
    "transport_basin_rerouting_negative_control": (
        *_COMMON_SELECTORS,
        "transport_flux_present",
        "transport_potential_range_present",
        "transport_negative_balanced_signature",
        "positive_flux_edges_present",
        "tensor_anisotropy_present",
        "row_mismatch_sum_present",
        "tensor_hotspot_sample_present",
        "sink_count_present",
        "basin_count_present",
        "geometric_seed_count_recorded",
        "validated_basin_count_recorded",
    ),
    "coarse_cache_invalidation_positive_control": (
        *_COMMON_SELECTORS,
        "coarse_cache_state_recorded",
        "coarse_cache_invalidated",
        "coarse_cache_invalidation_reason_recorded",
    ),
    "coarse_cache_invalidation_negative_control": (
        *_COMMON_SELECTORS,
        "coarse_cache_state_recorded",
        "coarse_cache_not_invalidated",
    ),
    "quiescent_hybrid_control_no_event_control": (
        *_COMMON_SELECTORS,
        "no_lifecycle_events",
    ),
    "complex_spark_expansion_hierarchy_complex_control": (
        *_COMMON_SELECTORS,
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
        "sink_count_present",
        "basin_count_present",
        "tensor_trace_present",
        "transport_flux_present",
    ),
    "complex_spark_expansion_choice_collapse_complex_control": (
        *_COMMON_SELECTORS,
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
        "collapse_event_present",
        "collapse_registry_present",
        "sink_count_present",
        "basin_count_present",
    ),
    "complex_expansion_growth_budget_coarse_complex_control": (
        *_COMMON_SELECTORS,
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
        "growth_event_present",
        "birth_probability_recorded",
        "transport_flux_present",
        "positive_flux_edges_present",
        "post_expansion_budget_check_available",
        "budget_balanced",
        "coarse_cache_state_recorded",
        "coarse_cache_invalidated",
        "coarse_cache_invalidation_reason_recorded",
    ),
    "complex_hessian_row_basis_complex_control": (
        *_COMMON_SELECTORS,
        "hessian_row_basis_backend",
        "weighted_least_squares_unavailable",
        "tensor_trace_present",
        "previous_signed_hessian_available",
    ),
    "complex_hessian_weighted_least_squares_complex_control": (
        *_COMMON_SELECTORS,
        "hessian_weighted_least_squares_backend",
        "weighted_least_squares_available",
        "tensor_trace_present",
        "previous_signed_hessian_available",
    ),
    "complex_spark_choice_no_saturation_perturbation_perturbation_control": (
        *_COMMON_SELECTORS,
        "no_lifecycle_events",
    ),
    "complex_growth_low_birth_perturbation_perturbation_control": (
        *_COMMON_SELECTORS,
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
        "no_growth_events",
        "budget_balanced",
    ),
}


def run_grc9v3_selector_validation(
    *,
    session_id: str = "S0007",
    source_session_ids: Sequence[str] = ("S0006",),
    session_root: str | Path | None = None,
) -> GRC9V3SelectorValidationSession:
    """Validate persisted GRC9V3 discovery lanes with field-backed selectors."""

    if not is_session_id(session_id):
        raise ValueError("session_id must use S0001-style formatting")
    for source_session_id in source_session_ids:
        if not is_session_id(source_session_id):
            raise ValueError("source_session_ids must use S0001-style formatting")

    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    lane_payloads = tuple(
        _load_source_lane(source_id, lane)
        for source_id in source_session_ids
        for lane in _source_lanes(source_id)
    )
    lane_payloads = _attach_pair_context(lane_payloads)
    validations = tuple(_validate_lane(lane) for lane in lane_payloads)

    manifest_path = root / "selector_manifest.json"
    session = GRC9V3SelectorValidationSession(
        session_id=session_id,
        source_session_ids=tuple(source_session_ids),
        validations=validations,
        manifest_path=manifest_path.as_posix(),
    )
    _write_json(manifest_path, _build_manifest(session))
    _write_json(reports_root / "selector_validation_report.json", session.to_mapping())
    _write_summary_markdown(reports_root / "selector_validation_summary.md", session)
    _write_json(root / "session_manifest.json", _session_manifest(session, root))
    _write_readme(root, session)
    _append_experimental_log(session, root)
    return session


def _source_lanes(source_session_id: str) -> tuple[Mapping[str, Any], ...]:
    report_path = DISCOVERY_SESSION_ROOT / source_session_id / "reports" / "run_report.json"
    payload = _read_json(report_path)
    return tuple(payload.get("lanes", ()))


def _load_source_lane(
    source_session_id: str,
    lane_report: Mapping[str, Any],
) -> Mapping[str, Any]:
    lane_name = str(lane_report["lane_name"])
    telemetry_root = (
        DISCOVERY_SESSION_ROOT
        / source_session_id
        / "generated_lanes"
        / lane_name
        / "telemetry"
    )
    summary = _read_json(telemetry_root / "run_summary.json")
    steps = tuple(_read_jsonl(telemetry_root / "steps.jsonl"))
    events = tuple(_read_jsonl(telemetry_root / "events.jsonl"))
    return {
        "source_session_id": source_session_id,
        "lane_name": lane_name,
        "run_id": str(lane_report["run_id"]),
        "seed_name": str(lane_report["seed_name"]),
        "profile": str(lane_report["profile"]),
        "requested_steps": int(lane_report["requested_steps"]),
        "event_counts_by_kind": dict(summary.get("event_counts_by_kind", {})),
        "summary": summary,
        "steps": steps,
        "events": events,
        "artifact_root": str(lane_report["artifact_root"]),
        "expected_outcome": str(lane_report.get("expected_outcome", "")),
        "predicted_event_sequence": tuple(lane_report.get("predicted_event_sequence", ())),
        "actual_event_sequence": tuple(lane_report.get("actual_event_sequence", ())),
        "event_sequence_analysis": dict(
            lane_report.get("event_sequence_analysis", {})
        ),
        "control_role": str(
            _get_path(
                summary,
                "family_extensions.discovery.control_role",
                "",
            )
        ),
    }


def _attach_pair_context(
    lane_payloads: Sequence[Mapping[str, Any]],
) -> tuple[Mapping[str, Any], ...]:
    by_name = {str(lane["lane_name"]): lane for lane in lane_payloads}
    return tuple({**lane, "paired_lanes": by_name} for lane in lane_payloads)


def _validate_lane(lane: Mapping[str, Any]) -> GRC9V3LaneSelectorValidation:
    lane_name = str(lane["lane_name"])
    expected_selector_ids = EXPECTED_SELECTORS_BY_LANE.get(lane_name, ())
    selector_results: list[GRC9V3SelectorResult] = []
    for selector_id in expected_selector_ids:
        selector = GRC9V3_SELECTORS[selector_id]
        passed, observed_value = selector.predicate(lane)
        selector_results.append(
            GRC9V3SelectorResult(
                selector_id=selector.selector_id,
                passed=passed,
                field_path=selector.field_path,
                observed_value=observed_value,
                failure_kind=_failure_kind(lane, selector, passed),
            )
        )
    confidence_score, confidence_label = _score_results(
        expected_selector_ids,
        tuple(selector_results),
    )
    motif_id = (
        _motif_id(str(lane["source_session_id"]), lane_name)
        if confidence_score >= 3
        else None
    )
    return GRC9V3LaneSelectorValidation(
        session_id=str(lane["source_session_id"]),
        lane_name=lane_name,
        control_role=str(lane.get("control_role", "")),
        run_id=str(lane["run_id"]),
        seed_name=str(lane["seed_name"]),
        profile=str(lane["profile"]),
        requested_steps=int(lane["requested_steps"]),
        event_counts_by_kind=dict(lane["event_counts_by_kind"]),
        expected_selector_ids=tuple(expected_selector_ids),
        selector_results=tuple(selector_results),
        confidence_score=confidence_score,
        confidence_label=confidence_label,
        motif_id=motif_id,
        notes=_lane_notes(lane),
    )


def _lane_notes(lane: Mapping[str, Any]) -> Mapping[str, str]:
    lane_name = str(lane["lane_name"])
    notes = {
        "artifact_root": str(lane["artifact_root"]),
        "expected_outcome": str(lane["expected_outcome"]),
        "control_role": str(lane.get("control_role", "")),
    }
    if lane_name == "appendix_e_cell_division_negative_control":
        notes["expected_outcome_original"] = notes["expected_outcome"]
        notes["expected_outcome"] = (
            "completed Appendix E evidence is absent because the refined negative "
            "control removes the saturated-parent completion precondition; this "
            "does not claim a runtime daughter-min-mass evaluator"
        )
    if lane_name == "hybrid_spark_gate_positive_control":
        notes["signed_crossing_selector_scope"] = (
            "signed_crossing_status_recorded validates capability-status telemetry "
            "only; capability_disabled is expected until the signed-crossing "
            "runtime capability is enabled"
        )
    if str(lane.get("control_role", "")) == "no_event_control":
        notes["evidence_mode"] = "absence_evidence"
    elif str(lane.get("control_role", "")) == "negative_control":
        notes["evidence_mode"] = "negative_control_evidence"
    else:
        notes["evidence_mode"] = "presence_evidence"
    sequence_analysis = lane.get("event_sequence_analysis", {})
    if isinstance(sequence_analysis, Mapping) and sequence_analysis.get(
        "has_sequence_delta"
    ):
        notes["event_sequence_delta"] = json.dumps(
            {
                "predicted": list(lane.get("predicted_event_sequence", ())),
                "observed": list(lane.get("actual_event_sequence", ())),
                "missing": dict(
                    sequence_analysis.get("missing_predicted_event_counts", {})
                ),
                "unexpected": dict(sequence_analysis.get("unexpected_event_counts", {})),
                "predicted_order_preserved": bool(
                    sequence_analysis.get("predicted_order_preserved", False)
                ),
            },
            sort_keys=True,
        )
    return notes


def _score_results(
    expected_selector_ids: Sequence[str],
    selector_results: Sequence[GRC9V3SelectorResult],
) -> tuple[int, str]:
    if not expected_selector_ids:
        return 0, "rejected"
    if any(result.failure_kind == "missing_surface" for result in selector_results):
        passed = sum(1 for result in selector_results if result.passed)
        if passed:
            return 2, "weak_candidate"
        return 0, "rejected"
    passed = sum(1 for result in selector_results if result.passed)
    total = len(expected_selector_ids)
    if passed == total:
        return 5, "strong_candidate"
    ratio = passed / total
    if ratio >= 0.75:
        return 4, "candidate"
    if ratio >= 0.5:
        return 2, "weak_candidate"
    return 0, "rejected"


def _motif_id(session_id: str, lane_name: str) -> str:
    return f"grc9v3-motif-{session_id.lower()}-{lane_name.replace('_', '-')}"


def _build_manifest(session: GRC9V3SelectorValidationSession) -> Mapping[str, Any]:
    return {
        "manifest_version": GRC9V3_SELECTOR_VALIDATION_VERSION,
        "family": "grc9v3",
        "program": DISCOVERY_PROGRAM,
        "track": DISCOVERY_TRACK,
        "source_artifacts": [
            {
                "artifact_role": "source_session",
                "path": f"{DISCOVERY_SESSION_ROOT / source_id}/",
                "used_for_discovery": True,
            }
            for source_id in session.source_session_ids
        ],
        "run_scope": {
            "family": "grc9v3",
            "profile_naming": "grc9v3_discovery_<phenomenon>_v<integer>",
            "lane_naming": "<seed_family>_<control_role>",
            "profiles": sorted({item.profile for item in session.validations}),
            "lanes": sorted({item.lane_name for item in session.validations}),
        },
        "selectors": [item.to_mapping() for item in GRC9V3_SELECTORS.values()],
        "validations": [item.to_mapping() for item in session.validations],
        "motifs": [_motif_record(item) for item in session.validations if item.motif_id],
    }


def _motif_record(validation: GRC9V3LaneSelectorValidation) -> Mapping[str, Any]:
    observed = tuple(
        result.field_path for result in validation.selector_results if result.passed
    )
    missing = tuple(
        result.field_path for result in validation.selector_results if not result.passed
    )
    return {
        "motif_id": validation.motif_id,
        "family": "grc9v3",
        "phenomenon": _phenomenon_from_lane(validation.lane_name),
        "profile": validation.profile,
        "lane": validation.lane_name,
        "control_role": validation.control_role,
        "run_id": validation.run_id,
        "seed_name": validation.seed_name,
        "session_ids": [validation.session_id],
        "step_window": [0, validation.requested_steps],
        "predicted_evidence_fields": [
            GRC9V3_SELECTORS[selector_id].field_path
            for selector_id in validation.expected_selector_ids
        ],
        "observed_evidence_fields": list(observed),
        "evidence_fields": {
            "predicted": [
                GRC9V3_SELECTORS[selector_id].field_path
                for selector_id in validation.expected_selector_ids
            ],
            "observed": list(observed),
            "missing": list(missing),
        },
        "missing_surface_fields": [
            result.field_path
            for result in validation.selector_results
            if result.failure_kind == "missing_surface"
        ],
        "confidence_score": validation.confidence_score,
        "confidence_label": validation.confidence_label,
        "review_status": validation.confidence_label,
        "notes": dict(validation.notes),
    }


def _phenomenon_from_lane(lane_name: str) -> str:
    for suffix in (
        "_positive_control",
        "_negative_control",
        "_baseline_control",
        "_no_event_control",
    ):
        if lane_name.endswith(suffix):
            return lane_name[: -len(suffix)]
    return lane_name


def _session_manifest(
    session: GRC9V3SelectorValidationSession,
    root: Path,
) -> Mapping[str, Any]:
    return {
        "session_id": session.session_id,
        "program": DISCOVERY_PROGRAM,
        "family": "grc9v3",
        "track": DISCOVERY_TRACK,
        "iteration": session.iteration,
        "session_kind": "selector_validation",
        "phenomenon": "field-backed selector validation over GRC9V3 generated controls",
        "seed_family": "selector validation only",
        "control_role": "n/a",
        "status": "completed",
        "created_at": "2026-04-26",
        "git_revision": _git_revision(),
        "dirty_worktree": _dirty_worktree(),
        "source_session_ids": list(session.source_session_ids),
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            "pygrc.discovery.grc9v3_selector_validation --session-id "
            f"{session.session_id} --source-session-ids "
            + ",".join(session.source_session_ids)
        ),
        "input_paths": [
            f"{DISCOVERY_SESSION_ROOT / source_id}/"
            for source_id in session.source_session_ids
        ],
        "output_paths": [
            str(root / "selector_manifest.json"),
            str(root / "reports" / "selector_validation_report.json"),
            str(root / "reports" / "selector_validation_summary.md"),
        ],
        "prediction_summary": (
            "Selectors should convert S0006 generated control evidence into field-backed "
            "pass/fail signatures for spark, expansion, Appendix E, choice/collapse, "
            "growth, budget, Hessian backend, transport, coarse cache, and no-event lanes."
        ),
        "observation_summary": (
            f"Validated {len(session.validations)} lanes from "
            f"{', '.join(session.source_session_ids)}; "
            f"{sum(1 for item in session.validations if item.motif_id)} lanes "
            "produced candidate motif records."
        ),
    }


def _write_readme(root: Path, session: GRC9V3SelectorValidationSession) -> None:
    lines = [
        f"# {session.session_id}. GRC9V3 Field-Backed Selector Validation",
        "",
        "Status: `completed`",
        "",
        "This session validates persisted GRC9V3 discovery telemetry with selectors "
        "that query concrete run-summary, step-row, and event-row fields.",
        "",
        "Replay:",
        "",
        "```bash",
        (
            f"PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_selector_validation "
            f"--session-id {session.session_id} --source-session-ids "
            + ",".join(session.source_session_ids)
        ),
        "```",
        "",
        f"Source sessions: `{', '.join(session.source_session_ids)}`",
        f"Validated lanes: `{len(session.validations)}`",
        f"Candidate motifs: `{sum(1 for item in session.validations if item.motif_id)}`",
        "",
        "Primary artifacts:",
        "",
        "- `selector_manifest.json`",
        "- `reports/selector_validation_report.json`",
        "- `reports/selector_validation_summary.md`",
    ]
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary_markdown(
    path: Path,
    session: GRC9V3SelectorValidationSession,
) -> None:
    lines = [
        f"# {session.session_id} Selector Validation Summary",
        "",
        "## Scope",
        "",
        f"- Source sessions: `{', '.join(session.source_session_ids)}`",
        f"- Validated lanes: `{len(session.validations)}`",
        f"- Candidate motifs: `{sum(1 for item in session.validations if item.motif_id)}`",
        f"- Lanes without selector expectations: `{len(session.no_expectation_lanes)}`",
        f"- Missing telemetry surfaces: `{_missing_surface_count(session)}`",
        "",
        "## Lane Results",
        "",
        "| Lane | Source | Control | Score | Label | Missing Selectors | Missing Surfaces |",
        "|---|---:|---|---:|---|---|---|",
    ]
    for validation in sorted(
        session.validations,
        key=lambda item: (item.session_id, item.lane_name),
    ):
        missing = ", ".join(f"`{item}`" for item in validation.missing_selector_ids)
        missing_surfaces = ", ".join(
            f"`{result.selector_id}`"
            for result in validation.selector_results
            if result.failure_kind == "missing_surface"
        )
        lines.append(
            f"| `{validation.lane_name}` | `{validation.session_id}` | "
            f"`{validation.control_role or 'unknown'}` | "
            f"{validation.confidence_score} | `{validation.confidence_label}` | "
            f"{missing or 'none'} | {missing_surfaces or 'none'} |"
        )
    absence = [
        item
        for item in session.validations
        if item.notes.get("evidence_mode") == "absence_evidence"
        and item.confidence_label == "strong_candidate"
    ]
    negative_controls = [
        item
        for item in session.validations
        if item.notes.get("evidence_mode") == "negative_control_evidence"
        and item.confidence_label == "strong_candidate"
    ]
    lines.extend(["", "## Evidence Modes", ""])
    lines.append(
        f"- Strong absence-evidence controls: `{len(absence)}`"
    )
    for validation in absence:
        lines.append(f"  - `{validation.lane_name}`")
    lines.append(
        f"- Strong negative-control evidence records: `{len(negative_controls)}`"
    )
    for validation in negative_controls:
        lines.append(f"  - `{validation.lane_name}`")
    sequence_deltas = [
        item for item in session.validations if "event_sequence_delta" in item.notes
    ]
    lines.extend(["", "## Event Sequence Deltas", ""])
    if sequence_deltas:
        for validation in sequence_deltas:
            lines.append(f"- `{validation.lane_name}`: `{validation.notes['event_sequence_delta']}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Capability-Gated Selectors",
            "",
            (
                "- `signed_crossing_status_recorded` validates that the "
                "capability-status field is present. A value of "
                "`capability_disabled` is status evidence, not a successful "
                "signed-crossing claim."
            ),
            "",
            "## Transport Pair Distinction",
            "",
            (
                "- Transport rerouting controls include paired predicates that "
                "compare positive and negative lanes by potential span and "
                "flux magnitude, so both lanes can pass while preserving "
                "distinct observed signatures."
            ),
        ]
    )
    if session.no_expectation_lanes:
        lines.extend(["", "## Lanes Without Selector Expectations", ""])
        for lane in session.no_expectation_lanes:
            lines.append(f"- `{lane}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _missing_surface_count(session: GRC9V3SelectorValidationSession) -> int:
    return sum(
        1
        for validation in session.validations
        for result in validation.selector_results
        if result.failure_kind == "missing_surface"
    )


def _append_experimental_log(
    session: GRC9V3SelectorValidationSession,
    root: Path,
) -> None:
    log_path = root.parent.parent / "ExperimentalLog.md"
    line = (
        f"| `{session.session_id}` | `completed` | `selector_validation` | "
        f"`{session.iteration}` | field-backed selector validation | "
        f"{', '.join(f'`{source}`' for source in session.source_session_ids)} | "
        f"`{root.as_posix()}/` | Iteration 6 selectors: "
        f"{len(session.validations)} lanes validated, "
        f"{sum(1 for item in session.validations if item.motif_id)} candidate motifs |\n"
    )
    if log_path.exists() and line in log_path.read_text(encoding="utf-8"):
        return
    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            "# GRC9V3 Phenomenology Discovery Experimental Log\n\n"
            "## Session Index\n\n"
            "| Session | Status | Kind | Iteration | Phenomenon | Seed Family | Artifact Root | Notes |\n"
            "|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> tuple[Mapping[str, Any], ...]:
    if not path.exists():
        return ()
    return tuple(
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _dirty_worktree() -> bool:
    try:
        output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return bool(output.strip())
    except (OSError, subprocess.CalledProcessError):
        return True


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate GRC9V3 discovery telemetry with field-backed selectors.",
    )
    parser.add_argument("--session-id", default="S0007")
    parser.add_argument("--source-session-ids", default="S0006")
    args = parser.parse_args(argv)
    source_session_ids = tuple(
        item.strip() for item in args.source_session_ids.split(",") if item.strip()
    )
    session = run_grc9v3_selector_validation(
        session_id=args.session_id,
        source_session_ids=source_session_ids,
    )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
