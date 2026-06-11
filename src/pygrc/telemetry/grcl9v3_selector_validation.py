"""Selector validation for GRCL-9V3 lowered-source replay sessions."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from pygrc.discovery.grc9v3_selector_validation import (
    GRC9V3_SELECTORS,
    GRC9V3SelectorDefinition,
)
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3_SELECTOR_EXPANSION_VERSION,
    GRCL9V3_SOURCE_SELECTOR_EXPANSIONS,
)

from .grcl9v3_replay import GRCL9V3_REPLAY_ROOT


GRCL9V3_SELECTOR_VALIDATION_VERSION = "grcl9v3_selector_validation_v1"
GRCL9V3_SELECTOR_SOURCE_REFERENCE = "implementation/GRCL-9V3-ImplementationPlan.md"

SelectorPredicate = Callable[[Mapping[str, Any]], tuple[bool, Any]]


@dataclass(frozen=True)
class GRCL9V3SelectorResult:
    """One expanded field-backed selector result."""

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
class GRCL9V3LaneSelectorValidation:
    """Selector validation record for one lowered-source replay lane."""

    source_session_id: str
    lane_name: str
    fixture_name: str
    manifest_entry_id: str
    control_role: str
    run_id: str
    requested_steps: int
    event_counts_by_kind: Mapping[str, int]
    source_expected_selector_ids: tuple[str, ...]
    expanded_selector_ids: tuple[str, ...]
    selector_results: tuple[GRCL9V3SelectorResult, ...]
    confidence_score: int
    confidence_label: str
    motif_id: str | None
    source_fixture_path: str
    lowered_state_path: str
    telemetry_root: str
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
            for selector_id in self.expanded_selector_ids
            if selector_id not in passed
        )

    @property
    def missing_surface_selector_ids(self) -> tuple[str, ...]:
        return tuple(
            result.selector_id
            for result in self.selector_results
            if result.failure_kind == "missing_surface"
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "source_session_id": self.source_session_id,
            "lane_name": self.lane_name,
            "fixture_name": self.fixture_name,
            "manifest_entry_id": self.manifest_entry_id,
            "control_role": self.control_role,
            "run_id": self.run_id,
            "requested_steps": self.requested_steps,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "source_expected_selector_ids": list(self.source_expected_selector_ids),
            "expanded_selector_ids": list(self.expanded_selector_ids),
            "selector_results": [result.to_mapping() for result in self.selector_results],
            "passed_selector_ids": list(self.passed_selector_ids),
            "missing_selector_ids": list(self.missing_selector_ids),
            "missing_surface_selector_ids": list(self.missing_surface_selector_ids),
            "confidence_score": self.confidence_score,
            "confidence_label": self.confidence_label,
            "motif_id": self.motif_id,
            "source_fixture_path": self.source_fixture_path,
            "lowered_state_path": self.lowered_state_path,
            "telemetry_root": self.telemetry_root,
            "notes": dict(self.notes),
        }


@dataclass(frozen=True)
class GRCL9V3SelectorValidationSession:
    """Selector validation session over lowered-source replay artifacts."""

    session_id: str
    source_session_ids: tuple[str, ...]
    validations: tuple[GRCL9V3LaneSelectorValidation, ...]
    manifest_path: Path
    report_path: Path
    summary_path: Path
    iteration: str = "I06_field_backed_lowered_source_selectors"

    @property
    def missing_surface_count(self) -> int:
        return sum(
            1
            for validation in self.validations
            for result in validation.selector_results
            if result.failure_kind == "missing_surface"
        )

    @property
    def motif_count(self) -> int:
        return sum(1 for validation in self.validations if validation.motif_id)

    def to_mapping(self) -> Mapping[str, Any]:
        labels = Counter(validation.confidence_label for validation in self.validations)
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "validation_version": GRCL9V3_SELECTOR_VALIDATION_VERSION,
            "source_session_ids": list(self.source_session_ids),
            "lane_count": len(self.validations),
            "motif_count": self.motif_count,
            "strong_candidate_count": labels.get("strong_candidate", 0),
            "candidate_count": labels.get("candidate", 0),
            "ambiguous_count": labels.get("ambiguous", 0),
            "weak_candidate_count": labels.get("weak_candidate", 0),
            "rejected_count": labels.get("rejected", 0),
            "missing_surface_count": self.missing_surface_count,
            "validations": [validation.to_mapping() for validation in self.validations],
            "manifest_path": str(self.manifest_path),
            "report_path": str(self.report_path),
            "summary_path": str(self.summary_path),
        }


@dataclass(frozen=True)
class _LocalSelectorDefinition:
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


def run_grcl9v3_selector_validation(
    *,
    session_id: str = "S0002",
    source_session_ids: Sequence[str] = ("S0001",),
    output_root: str | Path = GRCL9V3_REPLAY_ROOT,
) -> GRCL9V3SelectorValidationSession:
    """Validate lowered-source replay telemetry with field-backed selectors."""

    _validate_session_id(session_id)
    for source_session_id in source_session_ids:
        _validate_session_id(source_session_id)
    root = Path(output_root)
    session_root = root / "sessions" / session_id
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    lanes = tuple(
        _load_source_lane(root, source_session_id, lane)
        for source_session_id in source_session_ids
        for lane in _source_lanes(root, source_session_id)
    )
    validations = tuple(_validate_lane(lane) for lane in lanes)

    manifest_path = session_root / "selector_manifest.json"
    report_path = reports_root / "selector_validation_report.json"
    summary_path = reports_root / "selector_validation_summary.md"
    session = GRCL9V3SelectorValidationSession(
        session_id=session_id,
        source_session_ids=tuple(source_session_ids),
        validations=validations,
        manifest_path=manifest_path,
        report_path=report_path,
        summary_path=summary_path,
    )
    _write_json(manifest_path, _build_manifest(session))
    _write_json(report_path, session.to_mapping())
    _write_summary_markdown(summary_path, session)
    _write_json(session_root / "session_manifest.json", _session_manifest(session, root))
    _write_readme(session_root, session)
    _write_experimental_log(root / "ExperimentalLog.md", session, session_root)
    return session


def _validate_session_id(session_id: str) -> None:
    if not session_id.startswith("S") or not session_id[1:].isdigit():
        raise ValueError("session ids must use S0001-style formatting")


def _source_lanes(root: Path, source_session_id: str) -> tuple[Mapping[str, Any], ...]:
    manifest_path = root / "sessions" / source_session_id / "session_manifest.json"
    payload = _read_json(manifest_path)
    return tuple(payload.get("lanes", ()))


def _load_source_lane(
    root: Path,
    source_session_id: str,
    lane_report: Mapping[str, Any],
) -> Mapping[str, Any]:
    fixture_name = str(lane_report["fixture_name"])
    artifact_root = Path(str(lane_report["artifact_root"]))
    telemetry_root = artifact_root / "telemetry"
    source_fixture_path = Path(str(lane_report["source_fixture_path"]))
    lowered_state_path = Path(str(lane_report["lowered_state_path"]))
    source_fixture = _read_json(source_fixture_path)
    source_notes = source_fixture.get("notes", {})
    diagnostic_selector_ids = (
        source_notes.get("hessian_probe_expected_selector_ids", ())
        if isinstance(source_notes, Mapping)
        else ()
    )
    if not diagnostic_selector_ids and isinstance(source_notes, Mapping):
        diagnostic_selector_ids = source_notes.get("relay_probe_expected_selector_ids", ())
    expected_selector_ids = (
        diagnostic_selector_ids
        if diagnostic_selector_ids
        else source_fixture.get("expected_selector_ids", ())
    )
    summary = _read_json(telemetry_root / "run_summary.json")
    steps = tuple(_read_jsonl(telemetry_root / "steps.jsonl"))
    events = tuple(_read_jsonl(telemetry_root / "events.jsonl"))
    return {
        "source_session_id": source_session_id,
        "lane_name": fixture_name,
        "fixture_name": fixture_name,
        "manifest_entry_id": str(lane_report["manifest_entry_id"]),
        "run_id": str(lane_report["run_id"]),
        "requested_steps": int(lane_report["requested_steps"]),
        "event_counts_by_kind": dict(summary.get("event_counts_by_kind", {})),
        "source_expected_selector_ids": tuple(
            str(item) for item in expected_selector_ids
        ),
        "summary": summary,
        "steps": steps,
        "events": events,
        "source_fixture_path": str(source_fixture_path),
        "lowered_state_path": str(lowered_state_path),
        "telemetry_root": str(telemetry_root),
        "artifact_root": str(artifact_root),
        "control_role": str(
            _get_path(
                summary,
                "family_extensions.grc9v3.lane_context.run_role",
                _control_role_from_name(fixture_name),
            )
        ),
        "root": str(root),
    }


def _control_role_from_name(fixture_name: str) -> str:
    if fixture_name.endswith("_positive_control"):
        return "positive_control"
    if fixture_name.endswith("_negative_control"):
        return "negative_control"
    if fixture_name.endswith("_no_event_control"):
        return "no_event_control"
    return "control"


def _validate_lane(lane: Mapping[str, Any]) -> GRCL9V3LaneSelectorValidation:
    source_expected_selector_ids = tuple(lane["source_expected_selector_ids"])
    expanded_selector_ids = _expand_source_selectors(source_expected_selector_ids)
    selector_results: list[GRCL9V3SelectorResult] = []
    for selector_id in expanded_selector_ids:
        selector = _selector_by_id(selector_id)
        passed, observed_value = selector.predicate(lane)
        selector_results.append(
            GRCL9V3SelectorResult(
                selector_id=selector.selector_id,
                passed=passed,
                field_path=selector.field_path,
                observed_value=observed_value,
                failure_kind=_failure_kind(lane, selector, passed),
            )
        )
    confidence_score, confidence_label = _score_results(
        expanded_selector_ids,
        tuple(selector_results),
    )
    motif_id = (
        _motif_id(str(lane["source_session_id"]), str(lane["lane_name"]))
        if confidence_score >= 3
        else None
    )
    return GRCL9V3LaneSelectorValidation(
        source_session_id=str(lane["source_session_id"]),
        lane_name=str(lane["lane_name"]),
        fixture_name=str(lane["fixture_name"]),
        manifest_entry_id=str(lane["manifest_entry_id"]),
        control_role=str(lane["control_role"]),
        run_id=str(lane["run_id"]),
        requested_steps=int(lane["requested_steps"]),
        event_counts_by_kind=dict(lane["event_counts_by_kind"]),
        source_expected_selector_ids=source_expected_selector_ids,
        expanded_selector_ids=expanded_selector_ids,
        selector_results=tuple(selector_results),
        confidence_score=confidence_score,
        confidence_label=confidence_label,
        motif_id=motif_id,
        source_fixture_path=str(lane["source_fixture_path"]),
        lowered_state_path=str(lane["lowered_state_path"]),
        telemetry_root=str(lane["telemetry_root"]),
        notes=_lane_notes(lane),
    )


def _selector_by_id(
    selector_id: str,
) -> GRC9V3SelectorDefinition | _LocalSelectorDefinition:
    if selector_id in _LOCAL_SELECTORS:
        return _LOCAL_SELECTORS[selector_id]
    return GRC9V3_SELECTORS[selector_id]


def _expand_source_selectors(source_selector_ids: Sequence[str]) -> tuple[str, ...]:
    expanded: list[str] = [
        "contract_version_valid",
        "grcl9v3_source_fixture_link_present",
        "grcl9v3_expected_region_caches_present",
    ]
    for source_selector_id in source_selector_ids:
        if source_selector_id not in GRCL9V3_SOURCE_SELECTOR_EXPANSIONS:
            raise ValueError(f"unknown GRCL-9V3 source selector {source_selector_id!r}")
        expanded.extend(GRCL9V3_SOURCE_SELECTOR_EXPANSIONS[source_selector_id])
    deduped: list[str] = []
    seen: set[str] = set()
    for selector_id in expanded:
        if selector_id not in seen:
            deduped.append(selector_id)
            seen.add(selector_id)
    return tuple(deduped)


def _get_path(payload: Mapping[str, Any], path: str, default: Any = None) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        else:
            return default
    return current


def _step_values(lane: Mapping[str, Any], path: str) -> tuple[Any, ...]:
    return tuple(_get_path(step, path) for step in lane["steps"])


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
    selector: GRC9V3SelectorDefinition | _LocalSelectorDefinition,
    passed: bool,
) -> str:
    if passed:
        return "passed"
    required = selector.required_field_paths or (selector.field_path,)
    if not all(_field_present(lane, field_path) for field_path in required):
        return "missing_surface"
    return "predicate_failed"


def _score_results(
    expanded_selector_ids: Sequence[str],
    selector_results: Sequence[GRCL9V3SelectorResult],
) -> tuple[int, str]:
    if not expanded_selector_ids:
        return 0, "rejected"
    if any(result.failure_kind == "missing_surface" for result in selector_results):
        passed = sum(1 for result in selector_results if result.passed)
        if passed:
            return 3, "ambiguous"
        return 0, "rejected"
    passed = sum(1 for result in selector_results if result.passed)
    total = len(expanded_selector_ids)
    if passed == total:
        return 5, "strong_candidate"
    ratio = passed / total
    if ratio >= 0.75:
        return 4, "candidate"
    if ratio >= 0.5:
        return 2, "weak_candidate"
    return 0, "rejected"


def _motif_id(source_session_id: str, lane_name: str) -> str:
    return f"grcl9v3-motif-{source_session_id.lower()}-{lane_name.replace('_', '-')}"


def _local_selector(
    selector_id: str,
    *,
    surface: str,
    query: str,
    expected_type: str,
    field_path: str,
    predicate: SelectorPredicate,
    required_field_paths: Sequence[str] | None = None,
) -> _LocalSelectorDefinition:
    return _LocalSelectorDefinition(
        selector_id=selector_id,
        surface=surface,
        query=query,
        expected_type=expected_type,
        field_path=field_path,
        predicate=predicate,
        required_field_paths=tuple(required_field_paths or (field_path,)),
    )


def _no_event_count(kind: str) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        count = int(lane["event_counts_by_kind"].get(kind, 0))
        return count == 0, count

    return predicate


def _bounded_event_count(kind: str, *, maximum: int) -> SelectorPredicate:
    def predicate(lane: Mapping[str, Any]) -> tuple[bool, Any]:
        count = int(lane["event_counts_by_kind"].get(kind, 0))
        return 0 <= count <= maximum, {"count": count, "maximum": maximum}

    return predicate


def _source_fixture_link_present(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    expected = str(lane["fixture_name"])
    summary_fixture = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.fixture_name",
    )
    step_fixtures = _step_values(lane, "family_extensions.grcl9v3.fixture_name")
    source_artifact = _get_path(
        lane["summary"],
        "family_extensions.grc9v3.lane_context.source_runtime_artifact",
    )
    passed = (
        summary_fixture == expected
        and bool(step_fixtures)
        and all(value == expected for value in step_fixtures)
        and isinstance(source_artifact, str)
        and expected in source_artifact
    )
    return passed, {
        "summary_fixture": summary_fixture,
        "step_fixtures": list(step_fixtures[:3]),
        "source_runtime_artifact": source_artifact,
    }


def _expected_region_caches_present(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    names = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.expected_region_cache_names",
        (),
    ) or ()
    caches = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.expected_region_caches",
        {},
    ) or {}
    step_names = _step_values(
        lane,
        "family_extensions.grcl9v3.expected_region_cache_names",
    )
    passed = (
        isinstance(names, Sequence)
        and not isinstance(names, str)
        and len(names) > 0
        and isinstance(caches, Mapping)
        and bool(caches)
        and bool(step_names)
    )
    return passed, {"cache_names": list(names), "cache_count": len(caches)}


def _front_growth_provenance_present(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    status = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.growth_semantics_status",
        "none",
    )
    sources = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.growth_parent_capacity_sources",
        {},
    ) or {}
    eligible_ports = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.front_growth_eligible_ports",
        {},
    ) or {}
    legacy_ids = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.legacy_growth_locus_ids",
        (),
    ) or ()
    passed = (
        status == "front_capacity"
        and isinstance(sources, Mapping)
        and bool(sources)
        and isinstance(eligible_ports, Mapping)
        and bool(eligible_ports)
        and not tuple(legacy_ids)
    )
    return passed, {
        "growth_semantics_status": status,
        "capacity_source_count": len(sources) if isinstance(sources, Mapping) else 0,
        "eligible_parent_count": len(eligible_ports)
        if isinstance(eligible_ports, Mapping)
        else 0,
        "legacy_growth_locus_ids": list(legacy_ids)
        if isinstance(legacy_ids, Sequence) and not isinstance(legacy_ids, str)
        else legacy_ids,
    }


def _pressure_boundary_growth_provenance_present(
    lane: Mapping[str, Any],
) -> tuple[bool, Any]:
    status = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.growth_semantics_status",
        "none",
    )
    eligibility_mode = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.growth_parent_eligibility_mode",
        "unknown",
    )
    sources = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.growth_parent_capacity_sources",
        {},
    ) or {}
    eligible_ports = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.front_growth_eligible_ports",
        {},
    ) or {}
    expected_caches = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.expected_region_caches",
        {},
    ) or {}
    lifecycle = _get_path(
        lane["summary"],
        "family_extensions.grc9v3.lifecycle_event_counts",
        {},
    ) or {}
    growth_count = int(lane.get("event_counts_by_kind", {}).get("growth", 0))
    front_count = (
        int(lifecycle.get("front_capacity_growth_count", 0))
        if isinstance(lifecycle, Mapping)
        else 0
    )
    pressure_count = (
        int(lifecycle.get("pressure_boundary_growth_count", 0))
        if isinstance(lifecycle, Mapping)
        else 0
    )
    legacy_count = (
        int(lifecycle.get("legacy_broad_growth_count", 0))
        if isinstance(lifecycle, Mapping)
        else 0
    )
    pressure_records = [
        dict(record)
        for record in sources.values()
        if isinstance(record, Mapping)
        and record.get("front_capacity_source") == "pressure_boundary"
    ] if isinstance(sources, Mapping) else []
    pressure_regions = (
        expected_caches.get("grcl9v3_expected_pressure_boundary_region_ids", ())
        if isinstance(expected_caches, Mapping)
        else ()
    )
    passed = (
        status == "front_capacity"
        and eligibility_mode == "grcl9v3_front_capacity"
        and isinstance(eligible_ports, Mapping)
        and bool(eligible_ports)
        and bool(pressure_records)
        and bool(pressure_regions)
        and growth_count > 0
        and front_count == growth_count
        and pressure_count == growth_count
        and legacy_count == 0
    )
    return passed, {
        "growth_semantics_status": status,
        "growth_parent_eligibility_mode": eligibility_mode,
        "growth_count": growth_count,
        "front_capacity_growth_count": front_count,
        "pressure_boundary_growth_count": pressure_count,
        "legacy_broad_growth_count": legacy_count,
        "pressure_boundary_source_count": len(pressure_records),
        "pressure_boundary_expected_region_ids": list(pressure_regions)
        if isinstance(pressure_regions, Sequence) and not isinstance(pressure_regions, str)
        else pressure_regions,
        "pressure_boundary_sources": pressure_records,
    }


def _no_front_growth_provenance_present(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    status = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.growth_semantics_status",
        "none",
    )
    sources = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.growth_parent_capacity_sources",
        {},
    ) or {}
    eligible_ports = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.front_growth_eligible_ports",
        {},
    ) or {}
    legacy_ids = _get_path(
        lane["summary"],
        "family_extensions.grcl9v3.legacy_growth_locus_ids",
        (),
    ) or ()
    passed = (
        status == "none"
        and isinstance(sources, Mapping)
        and not sources
        and isinstance(eligible_ports, Mapping)
        and not eligible_ports
        and not tuple(legacy_ids)
    )
    return passed, {
        "growth_semantics_status": status,
        "capacity_source_count": len(sources) if isinstance(sources, Mapping) else 0,
        "eligible_parent_count": len(eligible_ports)
        if isinstance(eligible_ports, Mapping)
        else 0,
        "legacy_growth_locus_ids": list(legacy_ids)
        if isinstance(legacy_ids, Sequence) and not isinstance(legacy_ids, str)
        else legacy_ids,
    }


def _growth_before_collapse_observed(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    first_growth_order: tuple[int, int] | None = None
    first_growth_event_index: int | None = None
    first_growth_step_index: int | None = None
    first_collapse_after_growth_event_index: int | None = None
    first_collapse_after_growth_step_index: int | None = None
    for event in lane["events"]:
        event_index = int(event.get("event_index", 0))
        step_index = int(event.get("step_index", 0))
        event_kind = str(event.get("event_kind", ""))
        if event_kind == "growth" and first_growth_order is None:
            first_growth_order = (step_index, event_index)
            first_growth_event_index = event_index
            first_growth_step_index = step_index
        if (
            event_kind == "collapse"
            and first_growth_order is not None
            and (step_index, event_index) > first_growth_order
        ):
            first_collapse_after_growth_step_index = step_index
            first_collapse_after_growth_event_index = event_index
            break
    return (
        first_growth_event_index is not None
        and first_collapse_after_growth_event_index is not None,
        {
            "first_growth_step_index": first_growth_step_index,
            "first_growth_event_index": first_growth_event_index,
            "first_collapse_after_growth_step_index": (
                first_collapse_after_growth_step_index
            ),
            "first_collapse_after_growth_event_index": (
                first_collapse_after_growth_event_index
            ),
        },
    )


def _learning_state_present(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    count = _get_path(
        lane["summary"],
        "family_extensions.grc9v3.final_choice_collapse_summary.learning_state_count",
        0,
    )
    count = int(count) if isinstance(count, int) and not isinstance(count, bool) else 0
    return count > 0, count


def _collapsed_sink_recorded(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    summary_sink = _get_path(
        lane["summary"],
        "family_extensions.grc9v3.final_choice_collapse_summary.last_collapsed_sink_id",
    )
    event_sinks = [
        _get_path(event, "payload.collapsed_sink_id")
        for event in lane["events"]
        if str(event.get("event_kind", "")) == "collapse"
    ]
    passed = summary_sink is not None or any(value is not None for value in event_sinks)
    return passed, {"summary_sink": summary_sink, "event_sinks": event_sinks[:5]}


def _relay_roles(lane: Mapping[str, Any]) -> Mapping[str, Any]:
    first_growth_child: dict[str, tuple[int, int]] = {}
    first_growth_parent: dict[str, tuple[int, int]] = {}
    first_collapsed_sink: dict[str, tuple[int, int]] = {}
    for event in lane["events"]:
        event_index = int(event.get("event_index", -1))
        step_index = int(event.get("step_index", -1))
        event_kind = str(event.get("event_kind", ""))
        if event_kind == "growth":
            child_id = _get_path(event, "payload.child_node_id")
            parent_id = _get_path(event, "payload.parent_node_id")
            if child_id is not None:
                first_growth_child.setdefault(str(child_id), (step_index, event_index))
            if parent_id is not None:
                first_growth_parent.setdefault(str(parent_id), (step_index, event_index))
        elif event_kind == "collapse":
            sink_id = _get_path(event, "payload.collapsed_sink_id")
            if sink_id is not None:
                first_collapsed_sink.setdefault(str(sink_id), (step_index, event_index))

    child_later_sink = [
        {
            "node_id": node_id,
            "growth_child_step_index": child_order[0],
            "growth_child_event_index": child_order[1],
            "collapse_step_index": first_collapsed_sink[node_id][0],
            "collapse_event_index": first_collapsed_sink[node_id][1],
        }
        for node_id, child_order in sorted(first_growth_child.items())
        if node_id in first_collapsed_sink
        and first_collapsed_sink[node_id] > child_order
    ]
    sink_later_parent = [
        {
            "node_id": node_id,
            "collapse_step_index": collapse_order[0],
            "collapse_event_index": collapse_order[1],
            "growth_parent_step_index": first_growth_parent[node_id][0],
            "growth_parent_event_index": first_growth_parent[node_id][1],
        }
        for node_id, collapse_order in sorted(first_collapsed_sink.items())
        if node_id in first_growth_parent
        and first_growth_parent[node_id] > collapse_order
    ]
    full_relay = [
        {
            "node_id": node_id,
            "growth_child_step_index": child_order[0],
            "growth_child_event_index": child_order[1],
            "collapse_step_index": first_collapsed_sink[node_id][0],
            "collapse_event_index": first_collapsed_sink[node_id][1],
            "growth_parent_step_index": first_growth_parent[node_id][0],
            "growth_parent_event_index": first_growth_parent[node_id][1],
        }
        for node_id, child_order in sorted(first_growth_child.items())
        if node_id in first_collapsed_sink
        and node_id in first_growth_parent
        and first_collapsed_sink[node_id] > child_order
        and first_growth_parent[node_id] > first_collapsed_sink[node_id]
    ]
    return {
        "growth_child_later_collapsed_sink_count": len(child_later_sink),
        "collapsed_sink_later_growth_parent_count": len(sink_later_parent),
        "full_growth_collapse_relay_count": len(full_relay),
        "growth_child_later_collapsed_sink_sample": child_later_sink[:5],
        "collapsed_sink_later_growth_parent_sample": sink_later_parent[:5],
        "full_growth_collapse_relay_sample": full_relay[:5],
    }


def _growth_child_later_collapsed_sink(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    roles = _relay_roles(lane)
    return int(roles["growth_child_later_collapsed_sink_count"]) > 0, roles


def _collapsed_sink_later_growth_parent(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    roles = _relay_roles(lane)
    return int(roles["collapsed_sink_later_growth_parent_count"]) > 0, roles


def _full_growth_collapse_relay(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    roles = _relay_roles(lane)
    return int(roles["full_growth_collapse_relay_count"]) > 0, roles


_LOCAL_SELECTORS: Mapping[str, _LocalSelectorDefinition] = {
    item.selector_id: item
    for item in (
        _local_selector(
            "grcl9v3_source_fixture_link_present",
            surface="summary/steps",
            query="GRCL-9V3 extension links telemetry rows to source fixture identity",
            expected_type="mapping",
            field_path="family_extensions.grcl9v3.fixture_name",
            predicate=_source_fixture_link_present,
            required_field_paths=(
                "family_extensions.grcl9v3.fixture_name",
                "family_extensions.grc9v3.lane_context.source_runtime_artifact",
            ),
        ),
        _local_selector(
            "grcl9v3_expected_region_caches_present",
            surface="summary/steps",
            query="GRCL-9V3 expected-region caches are mirrored into telemetry extensions",
            expected_type="mapping",
            field_path="family_extensions.grcl9v3.expected_region_caches",
            predicate=_expected_region_caches_present,
            required_field_paths=(
                "family_extensions.grcl9v3.expected_region_caches",
                "family_extensions.grcl9v3.expected_region_cache_names",
            ),
        ),
        _local_selector(
            "front_growth_provenance_present",
            surface="summary",
            query="corrected GRCL-9V3 growth records explicit front-capacity provenance",
            expected_type="mapping",
            field_path="family_extensions.grcl9v3.growth_parent_capacity_sources",
            predicate=_front_growth_provenance_present,
            required_field_paths=(
                "family_extensions.grcl9v3.growth_semantics_status",
                "family_extensions.grcl9v3.growth_parent_capacity_sources",
                "family_extensions.grcl9v3.front_growth_eligible_ports",
                "family_extensions.grcl9v3.legacy_growth_locus_ids",
            ),
        ),
        _local_selector(
            "pressure_boundary_growth_provenance_present",
            surface="events/summary",
            query=(
                "GRCL-9V3 pressure-boundary growth records corrected "
                "front-capacity provenance"
            ),
            expected_type="mapping",
            field_path="family_extensions.grcl9v3.growth_parent_capacity_sources",
            predicate=_pressure_boundary_growth_provenance_present,
            required_field_paths=(
                "event_counts_by_kind",
                "family_extensions.grcl9v3.growth_semantics_status",
                "family_extensions.grcl9v3.growth_parent_eligibility_mode",
                "family_extensions.grcl9v3.growth_parent_capacity_sources",
                "family_extensions.grcl9v3.front_growth_eligible_ports",
                "family_extensions.grcl9v3.expected_region_caches",
                "family_extensions.grc9v3.lifecycle_event_counts.front_capacity_growth_count",
                "family_extensions.grc9v3.lifecycle_event_counts.pressure_boundary_growth_count",
                "family_extensions.grc9v3.lifecycle_event_counts.legacy_broad_growth_count",
            ),
        ),
        _local_selector(
            "no_front_growth_provenance_present",
            surface="summary",
            query="closed-front GRCL-9V3 control records no growth provenance",
            expected_type="mapping",
            field_path="family_extensions.grcl9v3.growth_parent_capacity_sources",
            predicate=_no_front_growth_provenance_present,
            required_field_paths=(
                "family_extensions.grcl9v3.growth_semantics_status",
                "family_extensions.grcl9v3.growth_parent_capacity_sources",
                "family_extensions.grcl9v3.front_growth_eligible_ports",
                "family_extensions.grcl9v3.legacy_growth_locus_ids",
            ),
        ),
        _local_selector(
            "no_choice_detected_events",
            surface="events/summary",
            query="choice detection lifecycle event count is zero",
            expected_type="int",
            field_path="family_extensions.grc9v3.lifecycle_event_counts.choice_detected_count",
            predicate=_no_event_count("choice_detected"),
            required_field_paths=("event_counts_by_kind",),
        ),
        _local_selector(
            "growth_reduction_observed",
            surface="events/summary",
            query="growth lifecycle event count stays within calibrated low-growth bound",
            expected_type="mapping",
            field_path="event_counts_by_kind.growth",
            predicate=_bounded_event_count("growth", maximum=100),
            required_field_paths=("event_counts_by_kind",),
        ),
        _local_selector(
            "growth_before_collapse_observed",
            surface="events",
            query="at least one growth event occurs before a later collapse event",
            expected_type="mapping",
            field_path="events.growth_before_collapse",
            predicate=_growth_before_collapse_observed,
            required_field_paths=("event_counts_by_kind",),
        ),
        _local_selector(
            "learning_state_present",
            surface="run_summary",
            query="final choice/collapse summary records basin-assignment learning state",
            expected_type="int",
            field_path=(
                "family_extensions.grc9v3.final_choice_collapse_summary."
                "learning_state_count"
            ),
            predicate=_learning_state_present,
        ),
        _local_selector(
            "collapsed_sink_recorded",
            surface="events/run_summary",
            query="collapse evidence records the final collapsed sink or center",
            expected_type="mapping",
            field_path=(
                "family_extensions.grc9v3.final_choice_collapse_summary."
                "last_collapsed_sink_id"
            ),
            predicate=_collapsed_sink_recorded,
            required_field_paths=("event_counts_by_kind",),
        ),
        _local_selector(
            "growth_child_later_collapsed_sink",
            surface="events",
            query="a runtime growth child later appears as a collapsed sink",
            expected_type="mapping",
            field_path="events.growth_child_later_collapsed_sink",
            predicate=_growth_child_later_collapsed_sink,
            required_field_paths=("event_counts_by_kind",),
        ),
        _local_selector(
            "collapsed_sink_later_growth_parent",
            surface="events",
            query="a collapsed sink later appears as a growth parent",
            expected_type="mapping",
            field_path="events.collapsed_sink_later_growth_parent",
            predicate=_collapsed_sink_later_growth_parent,
            required_field_paths=("event_counts_by_kind",),
        ),
        _local_selector(
            "full_growth_collapse_relay",
            surface="events",
            query=(
                "the same runtime node appears as growth child, later collapsed "
                "sink, and later growth parent"
            ),
            expected_type="mapping",
            field_path="events.full_growth_collapse_relay",
            predicate=_full_growth_collapse_relay,
            required_field_paths=("event_counts_by_kind",),
        ),
    )
}


def _lane_notes(lane: Mapping[str, Any]) -> Mapping[str, str]:
    notes = {
        "source_fixture_path": str(lane["source_fixture_path"]),
        "lowered_state_path": str(lane["lowered_state_path"]),
        "telemetry_root": str(lane["telemetry_root"]),
        "source_reference": GRCL9V3_SELECTOR_SOURCE_REFERENCE,
    }
    control_role = str(lane["control_role"])
    if control_role == "no_event_control":
        notes["evidence_mode"] = "absence_evidence"
    elif control_role == "negative_control":
        notes["evidence_mode"] = "negative_control_evidence"
    else:
        notes["evidence_mode"] = "presence_evidence"
    return notes


def _build_manifest(session: GRCL9V3SelectorValidationSession) -> Mapping[str, Any]:
    selector_ids = sorted(
        {
            selector_id
            for validation in session.validations
            for selector_id in validation.expanded_selector_ids
        }
    )
    return {
        "manifest_version": GRCL9V3_SELECTOR_VALIDATION_VERSION,
        "family": "grcl9v3",
        "program": "grcl9v3_lowering",
        "track": "source_seed_layer",
        "source_artifacts": [
            {
                "artifact_role": "lowered_source_replay_session",
                "path": f"{GRCL9V3_REPLAY_ROOT / 'sessions' / source_session_id}/",
                "used_for_selector_validation": True,
            }
            for source_session_id in session.source_session_ids
        ],
        "selector_expansions": {
            key: list(value)
            for key, value in sorted(GRCL9V3_SOURCE_SELECTOR_EXPANSIONS.items())
        },
        "selector_expansion_version": GRCL9V3_SELECTOR_EXPANSION_VERSION,
        "selectors": [_selector_by_id(selector_id).to_mapping() for selector_id in selector_ids],
        "validations": [validation.to_mapping() for validation in session.validations],
        "motifs": [
            _motif_record(validation)
            for validation in session.validations
            if validation.motif_id
        ],
    }


def _motif_record(validation: GRCL9V3LaneSelectorValidation) -> Mapping[str, Any]:
    observed = tuple(
        result.field_path for result in validation.selector_results if result.passed
    )
    missing = tuple(
        result.field_path for result in validation.selector_results if not result.passed
    )
    return {
        "motif_id": validation.motif_id,
        "family": "grcl9v3",
        "phenomenon": _phenomenon_from_lane(validation.lane_name),
        "lane": validation.lane_name,
        "fixture_name": validation.fixture_name,
        "manifest_entry_id": validation.manifest_entry_id,
        "control_role": validation.control_role,
        "run_id": validation.run_id,
        "session_ids": [validation.source_session_id],
        "step_window": [0, validation.requested_steps],
        "source_expected_selector_ids": list(validation.source_expected_selector_ids),
        "expanded_selector_ids": list(validation.expanded_selector_ids),
        "predicted_evidence_fields": [
            _selector_by_id(selector_id).field_path
            for selector_id in validation.expanded_selector_ids
        ],
        "observed_evidence_fields": list(observed),
        "evidence_fields": {
            "predicted": [
                _selector_by_id(selector_id).field_path
                for selector_id in validation.expanded_selector_ids
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
        "source_fixture_path": validation.source_fixture_path,
        "lowered_state_path": validation.lowered_state_path,
        "telemetry_root": validation.telemetry_root,
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
    session: GRCL9V3SelectorValidationSession,
    output_root: Path,
) -> Mapping[str, Any]:
    command = (
        "PYTHONPATH=src python -m pygrc.telemetry.grcl9v3_selector_validation "
        f"--session-id {session.session_id} "
        f"--source-session-ids {','.join(session.source_session_ids)} "
        f"--output-root {output_root}"
    )
    return {
        "session_id": session.session_id,
        "session_kind": "grcl9v3_selector_validation",
        "validation_version": GRCL9V3_SELECTOR_VALIDATION_VERSION,
        "family": "grcl9v3",
        "iteration": session.iteration,
        "source_session_ids": list(session.source_session_ids),
        "source_reference": GRCL9V3_SELECTOR_SOURCE_REFERENCE,
        "replay_command": command,
        "input_paths": [
            str(output_root / "sessions" / source_session_id)
            for source_session_id in session.source_session_ids
        ],
        "output_paths": [
            str(session.manifest_path),
            str(session.report_path),
            str(session.summary_path),
        ],
        "observation_summary": (
            f"Validated {len(session.validations)} lowered-source lanes; "
            f"{session.motif_count} lanes produced candidate motif records; "
            f"{session.missing_surface_count} missing telemetry surfaces were reported."
        ),
    }


def _write_summary_markdown(
    path: Path,
    session: GRCL9V3SelectorValidationSession,
) -> None:
    lines = [
        f"# {session.session_id} GRCL-9V3 Selector Validation Summary",
        "",
        "## Scope",
        "",
        f"- Source sessions: `{', '.join(session.source_session_ids)}`",
        f"- Validated lanes: `{len(session.validations)}`",
        f"- Candidate motifs: `{session.motif_count}`",
        f"- Missing telemetry surfaces: `{session.missing_surface_count}`",
        "",
        "## Lane Results",
        "",
        "| Lane | Source | Control | Score | Label | Source Selectors | Missing Selectors | Missing Surfaces |",
        "|---|---:|---|---:|---|---|---|---|",
    ]
    for validation in sorted(
        session.validations,
        key=lambda item: (item.source_session_id, item.lane_name),
    ):
        source_selectors = ", ".join(
            f"`{selector_id}`" for selector_id in validation.source_expected_selector_ids
        )
        missing = ", ".join(f"`{item}`" for item in validation.missing_selector_ids)
        missing_surfaces = ", ".join(
            f"`{item}`" for item in validation.missing_surface_selector_ids
        )
        lines.append(
            f"| `{validation.lane_name}` | `{validation.source_session_id}` | "
            f"`{validation.control_role}` | {validation.confidence_score} | "
            f"`{validation.confidence_label}` | {source_selectors or 'none'} | "
            f"{missing or 'none'} | {missing_surfaces or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Selector Expansion",
            "",
            "Source selector ids remain vocabulary-facing; this session expands them into concrete Phase T-GRC9V3 telemetry field selectors.",
        ]
    )
    for source_selector_id, expanded in sorted(GRCL9V3_SOURCE_SELECTOR_EXPANSIONS.items()):
        lines.append(
            f"- `{source_selector_id}` -> "
            + ", ".join(f"`{selector_id}`" for selector_id in expanded)
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_readme(root: Path, session: GRCL9V3SelectorValidationSession) -> None:
    lines = [
        f"# {session.session_id}. GRCL-9V3 Lowered-Source Selector Validation",
        "",
        "Status: `completed`",
        "",
        "This session validates lowered-source replay telemetry with field-backed selectors.",
        "",
        "Primary artifacts:",
        "",
        "- `selector_manifest.json`",
        "- `reports/selector_validation_report.json`",
        "- `reports/selector_validation_summary.md`",
    ]
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_experimental_log(
    path: Path,
    session: GRCL9V3SelectorValidationSession,
    session_root: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total_events = sum(
        sum(int(value) for value in validation.event_counts_by_kind.values())
        for validation in session.validations
    )
    row = (
        f"| {session.session_id} | Selector validation over "
        f"{', '.join(session.source_session_ids)} | {len(session.validations)} | "
        f"{total_events} | `{session_root}` |"
    )
    existing_rows: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("| S") and line[3:4].isdigit():
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if cells and cells[0] != session.session_id:
                    existing_rows.append(line)
    lines = [
        "# GRCL-9V3 Lowering Experimental Log",
        "",
        "Sessions are replayable records under `outputs/grcl9v3/lowering/sessions/`.",
        "",
        "| Session | Purpose | Lanes | Events | Root |",
        "|---|---|---:|---:|---|",
        *existing_rows,
        row,
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


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


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate GRCL-9V3 lowered-source telemetry with selectors.",
    )
    parser.add_argument("--session-id", default="S0002")
    parser.add_argument("--source-session-ids", default="S0001")
    parser.add_argument("--output-root", default=str(GRCL9V3_REPLAY_ROOT))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    source_session_ids = tuple(
        item.strip() for item in args.source_session_ids.split(",") if item.strip()
    )
    session = run_grcl9v3_selector_validation(
        session_id=args.session_id,
        source_session_ids=source_session_ids,
        output_root=Path(args.output_root),
    )
    print(json.dumps(session.to_mapping(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "GRCL9V3_SELECTOR_VALIDATION_VERSION",
    "GRCL9V3LaneSelectorValidation",
    "GRCL9V3SelectorResult",
    "GRCL9V3SelectorValidationSession",
    "run_grcl9v3_selector_validation",
]
