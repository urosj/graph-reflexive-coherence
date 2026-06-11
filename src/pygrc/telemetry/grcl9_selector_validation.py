"""Selector validation for corrected GRCL-9 lowering replay sessions."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .grcl9_replay import (
    GRCL9_REPLAY_ROOT,
    GRCL9_REPLAY_VERSION,
    LEGACY_GROWTH_SOURCE_MODES,
)


GRCL9_SELECTOR_VALIDATION_VERSION = "grcl9_selector_validation_v1"
GRCL9_SELECTOR_SOURCE_REFERENCE = "implementation/GRC9-GRCL9-GrowthCorrection-Plan.md"

SelectorPredicate = Callable[[Mapping[str, Any]], tuple[bool, Any]]


@dataclass(frozen=True)
class GRCL9SelectorResult:
    """One field-backed GRCL-9 selector result."""

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
class GRCL9LaneSelectorValidation:
    """Selector validation record for one GRCL-9 replay lane."""

    source_session_id: str
    lane_name: str
    fixture_name: str
    manifest_entry_id: str
    run_id: str
    requested_steps: int
    selector_report_status: str
    event_counts_by_kind: Mapping[str, int]
    expected_selector_ids: tuple[str, ...]
    selector_results: tuple[GRCL9SelectorResult, ...]
    confidence_score: int
    confidence_label: str
    evidence_status: str
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
            "run_id": self.run_id,
            "requested_steps": self.requested_steps,
            "selector_report_status": self.selector_report_status,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "expected_selector_ids": list(self.expected_selector_ids),
            "selector_results": [result.to_mapping() for result in self.selector_results],
            "passed_selector_ids": list(self.passed_selector_ids),
            "missing_surface_selector_ids": list(self.missing_surface_selector_ids),
            "confidence_score": self.confidence_score,
            "confidence_label": self.confidence_label,
            "evidence_status": self.evidence_status,
            "motif_id": self.motif_id,
            "source_fixture_path": self.source_fixture_path,
            "lowered_state_path": self.lowered_state_path,
            "telemetry_root": self.telemetry_root,
            "notes": dict(self.notes),
        }


@dataclass(frozen=True)
class GRCL9SelectorValidationSession:
    """Selector validation session over GRCL-9 replay artifacts."""

    session_id: str
    source_session_ids: tuple[str, ...]
    validations: tuple[GRCL9LaneSelectorValidation, ...]
    manifest_path: Path
    report_path: Path
    summary_path: Path
    iteration: str = "I05_3_corrected_grcl9_selector_validation"

    @property
    def accepted_count(self) -> int:
        return sum(
            1 for validation in self.validations if validation.evidence_status == "accepted"
        )

    @property
    def superseded_legacy_count(self) -> int:
        return sum(
            1
            for validation in self.validations
            if validation.evidence_status == "legacy_broad_growth_non_evidence"
        )

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
        statuses = Counter(validation.evidence_status for validation in self.validations)
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "validation_version": GRCL9_SELECTOR_VALIDATION_VERSION,
            "source_session_ids": list(self.source_session_ids),
            "lane_count": len(self.validations),
            "motif_count": self.motif_count,
            "accepted_count": self.accepted_count,
            "superseded_legacy_count": self.superseded_legacy_count,
            "missing_surface_count": self.missing_surface_count,
            "confidence_labels": dict(sorted(labels.items())),
            "evidence_statuses": dict(sorted(statuses.items())),
            "validations": [validation.to_mapping() for validation in self.validations],
            "manifest_path": str(self.manifest_path),
            "report_path": str(self.report_path),
            "summary_path": str(self.summary_path),
        }


@dataclass(frozen=True)
class _SelectorDefinition:
    selector_id: str
    field_path: str
    predicate: SelectorPredicate
    required_field_paths: tuple[str, ...]


def run_grcl9_selector_validation(
    *,
    session_id: str = "S0032",
    source_session_ids: Sequence[str] = ("S0031",),
    output_root: str | Path = GRCL9_REPLAY_ROOT,
    force_legacy_growth: bool = False,
) -> GRCL9SelectorValidationSession:
    """Validate corrected GRCL-9 replay sessions with field-backed selectors."""

    _validate_session_id(session_id)
    for source_session_id in source_session_ids:
        _validate_session_id(source_session_id)
    root = Path(output_root)
    session_root = root / "sessions" / session_id
    reports_root = session_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    legacy_source_session_ids = tuple(
        source_session_id
        for source_session_id in source_session_ids
        if _source_session_uses_legacy_growth(root, source_session_id)
    )
    if legacy_source_session_ids and not force_legacy_growth:
        raise ValueError(
            "selector validation refuses legacy broad-growth source sessions "
            f"{', '.join(legacy_source_session_ids)}. Use --force-legacy-growth "
            "only for historical diagnostic comparison; legacy records remain "
            "non-evidence."
        )

    lanes = tuple(
        _load_source_lane(root, source_session_id, lane)
        for source_session_id in source_session_ids
        for lane in _source_lanes(root, source_session_id)
    )
    validations = tuple(_validate_lane(lane) for lane in lanes)

    manifest_path = session_root / "selector_manifest.json"
    report_path = reports_root / "selector_validation_report.json"
    summary_path = reports_root / "selector_validation_summary.md"
    session = GRCL9SelectorValidationSession(
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
    _write_json(
        session_root / "session_manifest.json",
        _session_manifest(
            session,
            root,
            force_legacy_growth=force_legacy_growth,
            legacy_source_session_ids=legacy_source_session_ids,
        ),
    )
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


def _source_session_uses_legacy_growth(root: Path, source_session_id: str) -> bool:
    manifest_path = root / "sessions" / source_session_id / "session_manifest.json"
    payload = _read_json(manifest_path)
    if str(payload.get("source_mode", "")) in LEGACY_GROWTH_SOURCE_MODES:
        return True
    for lane in payload.get("lanes", ()):
        if not isinstance(lane, Mapping):
            continue
        if bool(lane.get("legacy_broad_growth_non_evidence", False)):
            return True
    return False


def _load_source_lane(
    root: Path,
    source_session_id: str,
    lane_report: Mapping[str, Any],
) -> Mapping[str, Any]:
    fixture_name = str(lane_report["fixture_name"])
    artifact_root = Path(str(lane_report["artifact_root"]))
    telemetry_root = artifact_root / "telemetry"
    selector_report_path = Path(str(lane_report["selector_report_path"]))
    summary = _read_json(telemetry_root / "run_summary.json")
    selector_report = _read_json(selector_report_path)
    source_fixture_path = Path(str(lane_report["source_fixture_path"]))
    source_fixture = _read_json(source_fixture_path)
    return {
        "root": str(root),
        "source_session_id": source_session_id,
        "lane_name": fixture_name,
        "fixture_name": fixture_name,
        "manifest_entry_id": str(lane_report["manifest_entry_id"]),
        "run_id": str(lane_report["run_id"]),
        "requested_steps": int(lane_report["requested_steps"]),
        "selector_report_status": str(selector_report.get("status", "missing")),
        "event_counts_by_kind": dict(summary.get("event_counts_by_kind", {})),
        "summary": summary,
        "selector_report": selector_report,
        "expected_selector_ids": tuple(
            str(item) for item in source_fixture.get("expected_selector_ids", ())
        ),
        "source_fixture_path": str(source_fixture_path),
        "lowered_state_path": str(lane_report["lowered_state_path"]),
        "telemetry_root": str(telemetry_root),
        "legacy_broad_growth_non_evidence": bool(
            lane_report.get("legacy_broad_growth_non_evidence", False)
        ),
        "growth_parent_eligibility_mode": str(
            lane_report.get("growth_parent_eligibility_mode", "")
        ),
    }


def _validate_lane(lane: Mapping[str, Any]) -> GRCL9LaneSelectorValidation:
    selector_results = tuple(_run_selector(selector, lane) for selector in _SELECTORS)
    score, label, status = _score_lane(lane, selector_results)
    motif_id = (
        _motif_id(str(lane["source_session_id"]), str(lane["lane_name"]))
        if status == "accepted"
        else None
    )
    return GRCL9LaneSelectorValidation(
        source_session_id=str(lane["source_session_id"]),
        lane_name=str(lane["lane_name"]),
        fixture_name=str(lane["fixture_name"]),
        manifest_entry_id=str(lane["manifest_entry_id"]),
        run_id=str(lane["run_id"]),
        requested_steps=int(lane["requested_steps"]),
        selector_report_status=str(lane["selector_report_status"]),
        event_counts_by_kind=dict(lane["event_counts_by_kind"]),
        expected_selector_ids=tuple(lane["expected_selector_ids"]),
        selector_results=selector_results,
        confidence_score=score,
        confidence_label=label,
        evidence_status=status,
        motif_id=motif_id,
        source_fixture_path=str(lane["source_fixture_path"]),
        lowered_state_path=str(lane["lowered_state_path"]),
        telemetry_root=str(lane["telemetry_root"]),
        notes=_lane_notes(lane, status),
    )


def _run_selector(
    selector: _SelectorDefinition,
    lane: Mapping[str, Any],
) -> GRCL9SelectorResult:
    passed, observed = selector.predicate(lane)
    return GRCL9SelectorResult(
        selector_id=selector.selector_id,
        passed=passed,
        field_path=selector.field_path,
        observed_value=observed,
        failure_kind=_failure_kind(lane, selector, passed),
    )


def _score_lane(
    lane: Mapping[str, Any],
    selector_results: Sequence[GRCL9SelectorResult],
) -> tuple[int, str, str]:
    if _is_legacy_broad_growth(lane):
        return 0, "superseded_legacy", "legacy_broad_growth_non_evidence"
    if any(result.failure_kind == "missing_surface" for result in selector_results):
        passed = sum(1 for result in selector_results if result.passed)
        return (3, "ambiguous", "missing_surface") if passed else (0, "rejected", "missing_surface")
    passed = sum(1 for result in selector_results if result.passed)
    total = len(selector_results)
    if passed == total:
        return 5, "strong_candidate", "accepted"
    if passed / total >= 0.75:
        return 4, "candidate", "needs_review"
    if passed / total >= 0.5:
        return 2, "weak_candidate", "needs_review"
    return 0, "rejected", "rejected"


def _is_legacy_broad_growth(lane: Mapping[str, Any]) -> bool:
    return bool(lane.get("legacy_broad_growth_non_evidence")) or _get_path(
        lane["summary"],
        "family_extensions.grcl9.legacy_broad_growth_non_evidence",
        False,
    ) or _get_path(
        lane["summary"],
        "family_extensions.grcl9.growth_parent_eligibility_mode",
        "",
    ) == "legacy_any_inactive_port"


def _failure_kind(
    lane: Mapping[str, Any],
    selector: _SelectorDefinition,
    passed: bool,
) -> str:
    if passed:
        return "passed"
    if not all(_field_present(lane, field_path) for field_path in selector.required_field_paths):
        return "missing_surface"
    return "predicate_failed"


def _get_path(payload: Mapping[str, Any], path: str, default: Any = None) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        else:
            return default
    return current


def _field_present(lane: Mapping[str, Any], field_path: str) -> bool:
    if field_path == "selector_report.status":
        return "selector_report_status" in lane
    if _get_path(lane["summary"], field_path) is not None:
        return True
    if field_path == "event_counts_by_kind":
        return "event_counts_by_kind" in lane
    return False


def _selector_report_passed(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    status = str(lane.get("selector_report_status", ""))
    return status == "passed", status


def _front_capacity_mode(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    summary_mode = _get_path(
        lane["summary"],
        "family_extensions.grcl9.growth_parent_eligibility_mode",
    )
    backend_mode = _get_path(
        lane["summary"],
        "family_extensions.grc9.backend_summary.growth_parent_eligibility_mode",
    )
    passed = summary_mode == "grc9_front_capacity" and backend_mode == "grc9_front_capacity"
    return passed, {"grcl9_mode": summary_mode, "grc9_backend_mode": backend_mode}


def _no_legacy_broad_growth(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    summary_flag = bool(
        _get_path(
            lane["summary"],
            "family_extensions.grcl9.legacy_broad_growth_non_evidence",
            False,
        )
    )
    legacy_count = int(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.growth_summary.legacy_broad_growth_count",
            0,
        )
        or 0
    )
    lane_flag = bool(lane.get("legacy_broad_growth_non_evidence", False))
    passed = not summary_flag and not lane_flag and legacy_count == 0
    return passed, {
        "summary_legacy_flag": summary_flag,
        "lane_legacy_flag": lane_flag,
        "legacy_broad_growth_count": legacy_count,
    }


def _front_growth_provenance_consistent(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    growth_count = int(lane["event_counts_by_kind"].get("growth", 0))
    front_count = int(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.growth_summary.front_capacity_growth_count",
            0,
        )
        or 0
    )
    legacy_count = int(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.growth_summary.legacy_broad_growth_count",
            0,
        )
        or 0
    )
    status = _get_path(
        lane["summary"],
        "family_extensions.grcl9.growth_semantics_status",
    )
    passed = (
        legacy_count == 0
        and (
            (growth_count == 0 and front_count == 0)
            or (growth_count > 0 and front_count == growth_count and status == "front_capacity")
        )
    )
    return passed, {
        "growth_count": growth_count,
        "front_capacity_growth_count": front_count,
        "legacy_broad_growth_count": legacy_count,
        "growth_semantics_status": status,
    }


def _pressure_boundary_growth_provenance(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    expected = "pressure_boundary_growth_provenance" in lane["expected_selector_ids"]
    eligibility_mode = _get_path(
        lane["summary"],
        "family_extensions.grcl9.growth_parent_eligibility_mode",
    )
    capacity_sources = _get_path(
        lane["summary"],
        "family_extensions.grcl9.growth_parent_capacity_sources",
        {},
    )
    if not isinstance(capacity_sources, Mapping):
        capacity_sources = {}
    pressure_records = {
        str(parent_id): dict(record)
        for parent_id, record in capacity_sources.items()
        if isinstance(record, Mapping)
        and record.get("front_capacity_source") == "pressure_boundary"
    }
    if not expected:
        return True, {
            "status": "not_applicable",
            "pressure_boundary_source_count": len(pressure_records),
        }
    growth_count = int(lane["event_counts_by_kind"].get("growth", 0))
    front_count = int(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.growth_summary.front_capacity_growth_count",
            0,
        )
        or 0
    )
    pressure_count = int(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.growth_summary.pressure_boundary_growth_count",
            0,
        )
        or 0
    )
    passed = (
        eligibility_mode == "grc9_front_capacity"
        and bool(pressure_records)
        and growth_count > 0
        and front_count == growth_count
        and pressure_count == growth_count
    )
    return passed, {
        "status": "checked",
        "growth_count": growth_count,
        "front_capacity_growth_count": front_count,
        "pressure_boundary_growth_count": pressure_count,
        "growth_parent_eligibility_mode": eligibility_mode,
        "pressure_boundary_source_count": len(pressure_records),
        "pressure_boundary_sources": pressure_records,
    }


def _grcl9_source_link_present(lane: Mapping[str, Any]) -> tuple[bool, Any]:
    fixture_name = str(lane["fixture_name"])
    summary_fixture = _get_path(lane["summary"], "family_extensions.grcl9.fixture_name")
    replay_version = _get_path(lane["summary"], "family_extensions.grcl9.replay_version")
    passed = summary_fixture == fixture_name and replay_version == GRCL9_REPLAY_VERSION
    return passed, {"summary_fixture": summary_fixture, "replay_version": replay_version}


def _motif_id(source_session_id: str, lane_name: str) -> str:
    return f"grcl9-corrected-motif-{source_session_id.lower()}-{lane_name.replace('_', '-')}"


def _lane_notes(lane: Mapping[str, Any], status: str) -> Mapping[str, str]:
    if status == "legacy_broad_growth_non_evidence":
        return {
            "interpretation": (
                "legacy broad-growth replay retained for diagnostics only; not accepted as evidence"
            )
        }
    if status == "accepted":
        return {
            "interpretation": "corrected GRCL-9 front-capacity selector evidence accepted"
        }
    return {"interpretation": "selector validation requires review"}


def _build_manifest(session: GRCL9SelectorValidationSession) -> Mapping[str, Any]:
    return {
        "manifest_version": GRCL9_SELECTOR_VALIDATION_VERSION,
        "session_id": session.session_id,
        "source_session_ids": list(session.source_session_ids),
        "source_reference": GRCL9_SELECTOR_SOURCE_REFERENCE,
        "selector_definitions": [
            {
                "selector_id": selector.selector_id,
                "field_path": selector.field_path,
                "required_field_paths": list(selector.required_field_paths),
            }
            for selector in _SELECTORS
        ],
        "motifs": [
            validation.to_mapping()
            for validation in session.validations
            if validation.evidence_status == "accepted"
        ],
        "legacy_records": [
            validation.to_mapping()
            for validation in session.validations
            if validation.evidence_status == "legacy_broad_growth_non_evidence"
        ],
    }


def _session_manifest(
    session: GRCL9SelectorValidationSession,
    root: Path,
    *,
    force_legacy_growth: bool,
    legacy_source_session_ids: Sequence[str],
) -> Mapping[str, Any]:
    source_args = " ".join(f"--source-session-id {item}" for item in session.source_session_ids)
    force_arg = " --force-legacy-growth" if force_legacy_growth else ""
    return {
        "session_id": session.session_id,
        "validation_version": GRCL9_SELECTOR_VALIDATION_VERSION,
        "source_session_ids": list(session.source_session_ids),
        "lane_count": len(session.validations),
        "accepted_count": session.accepted_count,
        "superseded_legacy_count": session.superseded_legacy_count,
        "missing_surface_count": session.missing_surface_count,
        "force_legacy_growth": force_legacy_growth,
        "legacy_source_session_ids": list(legacy_source_session_ids),
        "manifest_path": str(session.manifest_path),
        "report_path": str(session.report_path),
        "summary_path": str(session.summary_path),
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.telemetry.grcl9_selector_validation --session-id {session.session_id} "
            f"{source_args}{force_arg} --output-root {root}"
        ),
    }


def _write_summary_markdown(path: Path, session: GRCL9SelectorValidationSession) -> None:
    lines = [
        f"# GRCL-9 Corrected Selector Validation {session.session_id}",
        "",
        f"- Source sessions: {', '.join(session.source_session_ids)}",
        f"- Lanes: {len(session.validations)}",
        f"- Accepted corrected records: {session.accepted_count}",
        f"- Superseded legacy records: {session.superseded_legacy_count}",
        f"- Missing telemetry surfaces: {session.missing_surface_count}",
        "",
        "| Lane | Evidence status | Confidence | Selectors | Events |",
        "|---|---|---:|---|---|",
    ]
    for validation in session.validations:
        events = ", ".join(
            f"{key}={value}" for key, value in sorted(validation.event_counts_by_kind.items())
        ) or "none"
        lines.append(
            "| "
            f"`{validation.lane_name}` | `{validation.evidence_status}` | "
            f"{validation.confidence_score} | "
            f"{len(validation.passed_selector_ids)}/{len(validation.selector_results)} | "
            f"{events} |"
        )
    lines.extend(
        [
            "",
            "Corrected evidence requires `grc9_front_capacity` in both GRCL-9 and",
            "GRC9 telemetry, zero legacy broad-growth events, and a passing replay",
            "selector report. Legacy `legacy_any_inactive_port` records are retained",
            "only as superseded diagnostic records.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_readme(session_root: Path, session: GRCL9SelectorValidationSession) -> None:
    lines = [
        f"# GRCL-9 Selector Validation {session.session_id}",
        "",
        "This session validates corrected GRCL-9 front-capacity replay evidence.",
        "",
        f"- Report: `{session.report_path}`",
        f"- Summary: `{session.summary_path}`",
        f"- Manifest: `{session.manifest_path}`",
        "",
    ]
    (session_root / "README.md").write_text("\n".join(lines), encoding="utf-8")


def _write_experimental_log(
    path: Path,
    session: GRCL9SelectorValidationSession,
    session_root: Path,
) -> None:
    entry = "\n".join(
        [
            f"## {session.session_id}. Corrected Selector Validation",
            "",
            f"- Session root: `{session_root}`",
            f"- Source sessions: {', '.join(f'`{item}`' for item in session.source_session_ids)}",
            f"- Lanes: {len(session.validations)}",
            f"- Accepted corrected records: {session.accepted_count}",
            f"- Superseded legacy records: {session.superseded_legacy_count}",
            f"- Missing telemetry surfaces: {session.missing_surface_count}",
            "",
        ]
    )
    previous = path.read_text(encoding="utf-8") if path.exists() else "# GRCL-9 Experiments\n\n"
    if f"## {session.session_id}. Corrected Selector Validation" in previous:
        prefix = previous.split(f"## {session.session_id}. Corrected Selector Validation", 1)[0].rstrip()
        path.write_text(prefix + "\n\n" + entry, encoding="utf-8")
    else:
        path.write_text(previous.rstrip() + "\n\n" + entry, encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


_SELECTORS: tuple[_SelectorDefinition, ...] = (
    _SelectorDefinition(
        selector_id="replay_selector_report_passed",
        field_path="selector_report.status",
        predicate=_selector_report_passed,
        required_field_paths=("selector_report.status",),
    ),
    _SelectorDefinition(
        selector_id="grcl9_source_link_present",
        field_path="family_extensions.grcl9.fixture_name",
        predicate=_grcl9_source_link_present,
        required_field_paths=(
            "family_extensions.grcl9.fixture_name",
            "family_extensions.grcl9.replay_version",
        ),
    ),
    _SelectorDefinition(
        selector_id="front_capacity_mode",
        field_path="family_extensions.grcl9.growth_parent_eligibility_mode",
        predicate=_front_capacity_mode,
        required_field_paths=(
            "family_extensions.grcl9.growth_parent_eligibility_mode",
            "family_extensions.grc9.backend_summary.growth_parent_eligibility_mode",
        ),
    ),
    _SelectorDefinition(
        selector_id="no_legacy_broad_growth",
        field_path="family_extensions.grc9.growth_summary.legacy_broad_growth_count",
        predicate=_no_legacy_broad_growth,
        required_field_paths=(
            "family_extensions.grcl9.legacy_broad_growth_non_evidence",
            "family_extensions.grc9.growth_summary.legacy_broad_growth_count",
        ),
    ),
    _SelectorDefinition(
        selector_id="front_growth_provenance_consistent",
        field_path="family_extensions.grc9.growth_summary.front_capacity_growth_count",
        predicate=_front_growth_provenance_consistent,
        required_field_paths=(
            "event_counts_by_kind",
            "family_extensions.grc9.growth_summary.front_capacity_growth_count",
            "family_extensions.grc9.growth_summary.legacy_broad_growth_count",
            "family_extensions.grcl9.growth_semantics_status",
        ),
    ),
    _SelectorDefinition(
        selector_id="pressure_boundary_growth_provenance",
        field_path="family_extensions.grcl9.growth_parent_capacity_sources",
        predicate=_pressure_boundary_growth_provenance,
        required_field_paths=(
            "event_counts_by_kind",
            "family_extensions.grc9.growth_summary.front_capacity_growth_count",
            "family_extensions.grc9.growth_summary.pressure_boundary_growth_count",
            "family_extensions.grcl9.growth_parent_eligibility_mode",
            "family_extensions.grcl9.growth_parent_capacity_sources",
        ),
    ),
)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate corrected GRCL-9 selector evidence."
    )
    parser.add_argument("--session-id", default="S0032")
    parser.add_argument(
        "--source-session-id",
        dest="source_session_ids",
        action="append",
        default=None,
        help="Replay session id to validate. May be provided multiple times.",
    )
    parser.add_argument("--output-root", default=str(GRCL9_REPLAY_ROOT))
    parser.add_argument(
        "--force-legacy-growth",
        action="store_true",
        help=(
            "Allow selector validation to read legacy broad-growth source "
            "sessions. Legacy records remain superseded non-evidence."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    source_session_ids = tuple(args.source_session_ids or ("S0031",))
    session = run_grcl9_selector_validation(
        session_id=args.session_id,
        source_session_ids=source_session_ids,
        output_root=args.output_root,
        force_legacy_growth=args.force_legacy_growth,
    )
    print(json.dumps(session.to_mapping(), sort_keys=True))


if __name__ == "__main__":
    main()
