"""Interpretation and calibration summaries for motion-inference sessions."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from pygrc.core import canonical_json_dumps, canonicalize_json_value


MOTION_INTERPRETATION_VERSION = "motion_interpretation_iter12_2_v1"
MOTION_DENSE_WINDOW_CALIBRATION_VERSION = "motion_dense_window_calibration_iter12_3_v1"
MOTION_IDENTITY_FISSION_PROMOTION_VERSION = "motion_identity_fission_promotion_iter12_4_v1"
DEFAULT_MOTION_INTERPRETATION_SESSION_ROOT = Path("outputs/motion/sessions/S0004")
DEFAULT_MOTION_INTERPRETATION_DIRNAME = "interpretation"
DEFAULT_DENSE_RECORD_COUNT_THRESHOLD = 500
DEFAULT_DENSE_IDENTITY_SPLIT_RATIO_THRESHOLD = 0.80
DEFAULT_FISSION_MAX_DAUGHTER_COUNT = 4
DEFAULT_FISSION_MIN_CONFIDENCE = 0.80
DEFAULT_FISSION_MIN_PROVENANCE_CONTINUITY = 0.75


@dataclass(frozen=True)
class MotionInterpretationRun:
    """Review-facing interpretation for one motion-over-landscape run."""

    key: str
    runtime_family: str
    checkpoint_count: int
    landscape_primitive_counts: Mapping[str, int]
    landscape_relationship_counts: Mapping[str, int]
    motion_record_counts: Mapping[str, int]
    motion_relationship_counts: Mapping[str, Mapping[str, int]]
    evidence_labels: tuple[str, ...]
    catalog_recommendation: str
    calibration_notes: tuple[str, ...]
    motion_report_dir: str = ""

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "key": self.key,
                "runtime_family": self.runtime_family,
                "checkpoint_count": self.checkpoint_count,
                "landscape_primitive_counts": dict(self.landscape_primitive_counts),
                "landscape_relationship_counts": dict(self.landscape_relationship_counts),
                "motion_record_counts": dict(self.motion_record_counts),
                "motion_relationship_counts": {
                    observer: dict(counts)
                    for observer, counts in self.motion_relationship_counts.items()
                },
                "evidence_labels": list(self.evidence_labels),
                "catalog_recommendation": self.catalog_recommendation,
                "calibration_notes": list(self.calibration_notes),
                "motion_report_dir": self.motion_report_dir,
            }
        )


@dataclass(frozen=True)
class MotionInterpretationSession:
    """Iteration 12.2 interpretation artifact for a motion session."""

    session_id: str
    session_root: Path
    interpretation_root: Path
    source_summary_path: Path
    runs: tuple[MotionInterpretationRun, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "session_version": MOTION_INTERPRETATION_VERSION,
                "session_id": self.session_id,
                "session_root": str(self.session_root),
                "interpretation_root": str(self.interpretation_root),
                "source_summary_path": str(self.source_summary_path),
                "run_count": len(self.runs),
                "runs": [run.to_mapping() for run in self.runs],
                "aggregate": _aggregate_mapping(self.runs),
                "source_runtime_boundary": (
                    "interpretation_reads_existing_motion_and_landscape_summaries_only"
                ),
                "non_claims": [
                    "no_new_motion_record_claim",
                    "no_new_landscape_primitive_claim",
                    "no_visual_only_promotion",
                ],
            }
        )


@dataclass(frozen=True)
class MotionDenseWindowCalibrationRun:
    """Dense-window calibration for one interpreted motion run."""

    key: str
    runtime_family: str
    checkpoint_count: int
    total_motion_record_count: int
    identity_record_count: int
    identity_split_count: int
    identity_split_ratio: float
    representative_stationary_ratio: float | None
    dense_window: bool
    calibration_labels: tuple[str, ...]
    catalog_guidance: str
    sample_motion_report_paths: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "key": self.key,
                "runtime_family": self.runtime_family,
                "checkpoint_count": self.checkpoint_count,
                "total_motion_record_count": self.total_motion_record_count,
                "identity_record_count": self.identity_record_count,
                "identity_split_count": self.identity_split_count,
                "identity_split_ratio": self.identity_split_ratio,
                "representative_stationary_ratio": self.representative_stationary_ratio,
                "dense_window": self.dense_window,
                "calibration_labels": list(self.calibration_labels),
                "catalog_guidance": self.catalog_guidance,
                "sample_motion_report_paths": list(self.sample_motion_report_paths),
            }
        )


@dataclass(frozen=True)
class MotionDenseWindowCalibrationSession:
    """Iteration 12.3 dense-window calibration artifact."""

    session_id: str
    session_root: Path
    interpretation_root: Path
    source_interpretation_path: Path
    record_count_threshold: int
    identity_split_ratio_threshold: float
    runs: tuple[MotionDenseWindowCalibrationRun, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "session_version": MOTION_DENSE_WINDOW_CALIBRATION_VERSION,
                "session_id": self.session_id,
                "session_root": str(self.session_root),
                "interpretation_root": str(self.interpretation_root),
                "source_interpretation_path": str(self.source_interpretation_path),
                "record_count_threshold": self.record_count_threshold,
                "identity_split_ratio_threshold": self.identity_split_ratio_threshold,
                "run_count": len(self.runs),
                "dense_window_count": sum(1 for run in self.runs if run.dense_window),
                "runs": [run.to_mapping() for run in self.runs],
                "aggregate": _dense_aggregate_mapping(self.runs),
                "source_runtime_boundary": (
                    "dense_window_calibration_reads_existing_interpretation_only"
                ),
                "non_claims": [
                    "no_raw_motion_record_rewrite",
                    "no_new_identity_fission_claim",
                    "no_visual_only_promotion",
                ],
            }
        )


@dataclass(frozen=True)
class MotionIdentityFissionPromotionRun:
    """Promotion gate result for dense split-dominant identity records."""

    key: str
    runtime_family: str
    identity_report_path: str
    identity_summary_path: str
    reviewed_split_record_count: int
    compact_candidate_count: int
    provenance_supported_candidate_count: int
    promoted_identity_fission_count: int
    rejected_reason_counts: Mapping[str, int]
    promotion_labels: tuple[str, ...]
    catalog_guidance: str
    sample_promoted_motion_ids: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "key": self.key,
                "runtime_family": self.runtime_family,
                "identity_report_path": self.identity_report_path,
                "identity_summary_path": self.identity_summary_path,
                "reviewed_split_record_count": self.reviewed_split_record_count,
                "compact_candidate_count": self.compact_candidate_count,
                "provenance_supported_candidate_count": self.provenance_supported_candidate_count,
                "promoted_identity_fission_count": self.promoted_identity_fission_count,
                "rejected_reason_counts": dict(self.rejected_reason_counts),
                "promotion_labels": list(self.promotion_labels),
                "catalog_guidance": self.catalog_guidance,
                "sample_promoted_motion_ids": list(self.sample_promoted_motion_ids),
            }
        )


@dataclass(frozen=True)
class MotionIdentityFissionPromotionSession:
    """Iteration 12.4 identity-fission promotion audit."""

    session_id: str
    session_root: Path
    interpretation_root: Path
    source_dense_calibration_path: Path
    max_daughter_count: int
    min_confidence: float
    min_provenance_continuity: float
    runs: tuple[MotionIdentityFissionPromotionRun, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "session_version": MOTION_IDENTITY_FISSION_PROMOTION_VERSION,
                "session_id": self.session_id,
                "session_root": str(self.session_root),
                "interpretation_root": str(self.interpretation_root),
                "source_dense_calibration_path": str(self.source_dense_calibration_path),
                "max_daughter_count": self.max_daughter_count,
                "min_confidence": self.min_confidence,
                "min_provenance_continuity": self.min_provenance_continuity,
                "run_count": len(self.runs),
                "promoted_identity_fission_count": sum(
                    run.promoted_identity_fission_count for run in self.runs
                ),
                "runs": [run.to_mapping() for run in self.runs],
                "aggregate": _promotion_aggregate_mapping(self.runs),
                "source_runtime_boundary": (
                    "identity_fission_promotion_reads_existing_reports_only"
                ),
                "non_claims": [
                    "no_raw_motion_record_rewrite",
                    "no_new_runtime_identity_claim",
                    "promotion_requires_catalog_review",
                ],
            }
        )


def run_motion_interpretation_session(
    *,
    session_root: str | Path = DEFAULT_MOTION_INTERPRETATION_SESSION_ROOT,
    output_dir: str | Path | None = None,
) -> MotionInterpretationSession:
    """Write interpretation artifacts for an existing motion session."""

    root = Path(session_root)
    summary_path = root / "landscape_motion_summary.json"
    summary = _read_json(summary_path)
    interpretation_root = (
        Path(output_dir)
        if output_dir is not None
        else root / DEFAULT_MOTION_INTERPRETATION_DIRNAME
    )
    runs = tuple(_interpret_run(run) for run in _summary_runs(summary))
    session = MotionInterpretationSession(
        session_id=str(summary.get("session_id", root.name)),
        session_root=root,
        interpretation_root=interpretation_root,
        source_summary_path=summary_path,
        runs=runs,
    )
    _write_json(interpretation_root / "motion_interpretation_summary.json", session.to_mapping())
    _write_text(interpretation_root / "motion_interpretation.md", _summary_markdown(session))
    _write_text(
        interpretation_root / "knowledge_graph_motion_case_study.md",
        _knowledge_graph_case_study(session),
    )
    return session


def run_motion_dense_window_calibration_session(
    *,
    session_root: str | Path = DEFAULT_MOTION_INTERPRETATION_SESSION_ROOT,
    output_dir: str | Path | None = None,
    record_count_threshold: int = DEFAULT_DENSE_RECORD_COUNT_THRESHOLD,
    identity_split_ratio_threshold: float = DEFAULT_DENSE_IDENTITY_SPLIT_RATIO_THRESHOLD,
) -> MotionDenseWindowCalibrationSession:
    """Write dense-window calibration artifacts for an existing interpretation."""

    root = Path(session_root)
    interpretation_root = (
        Path(output_dir)
        if output_dir is not None
        else root / DEFAULT_MOTION_INTERPRETATION_DIRNAME
    )
    interpretation_path = interpretation_root / "motion_interpretation_summary.json"
    if not interpretation_path.exists():
        run_motion_interpretation_session(session_root=root, output_dir=interpretation_root)
    interpretation = _read_json(interpretation_path)
    runs = tuple(
        _dense_calibration_run(
            run,
            record_count_threshold=record_count_threshold,
            identity_split_ratio_threshold=identity_split_ratio_threshold,
        )
        for run in _summary_runs(interpretation)
    )
    session = MotionDenseWindowCalibrationSession(
        session_id=str(interpretation.get("session_id", root.name)),
        session_root=root,
        interpretation_root=interpretation_root,
        source_interpretation_path=interpretation_path,
        record_count_threshold=record_count_threshold,
        identity_split_ratio_threshold=identity_split_ratio_threshold,
        runs=runs,
    )
    _write_json(
        interpretation_root / "dense_window_calibration_summary.json",
        session.to_mapping(),
    )
    _write_text(
        interpretation_root / "dense_window_calibration.md",
        _dense_calibration_markdown(session),
    )
    return session


def run_motion_identity_fission_promotion_session(
    *,
    session_root: str | Path = DEFAULT_MOTION_INTERPRETATION_SESSION_ROOT,
    output_dir: str | Path | None = None,
    max_daughter_count: int = DEFAULT_FISSION_MAX_DAUGHTER_COUNT,
    min_confidence: float = DEFAULT_FISSION_MIN_CONFIDENCE,
    min_provenance_continuity: float = DEFAULT_FISSION_MIN_PROVENANCE_CONTINUITY,
) -> MotionIdentityFissionPromotionSession:
    """Audit dense split records for possible identity-fission promotion."""

    root = Path(session_root)
    interpretation_root = (
        Path(output_dir)
        if output_dir is not None
        else root / DEFAULT_MOTION_INTERPRETATION_DIRNAME
    )
    dense_path = interpretation_root / "dense_window_calibration_summary.json"
    if not dense_path.exists():
        run_motion_dense_window_calibration_session(session_root=root, output_dir=interpretation_root)
    dense_payload = _read_json(dense_path)
    runs = tuple(
        _promotion_run(
            run,
            max_daughter_count=max_daughter_count,
            min_confidence=min_confidence,
            min_provenance_continuity=min_provenance_continuity,
        )
        for run in _summary_runs(dense_payload)
    )
    session = MotionIdentityFissionPromotionSession(
        session_id=str(dense_payload.get("session_id", root.name)),
        session_root=root,
        interpretation_root=interpretation_root,
        source_dense_calibration_path=dense_path,
        max_daughter_count=max_daughter_count,
        min_confidence=min_confidence,
        min_provenance_continuity=min_provenance_continuity,
        runs=runs,
    )
    _write_json(
        interpretation_root / "identity_fission_promotion_summary.json",
        session.to_mapping(),
    )
    _write_text(
        interpretation_root / "identity_fission_promotion.md",
        _promotion_markdown(session),
    )
    return session


def _interpret_run(run: Mapping[str, Any]) -> MotionInterpretationRun:
    key = str(run.get("key", "unknown"))
    runtime_family = str(run.get("runtime_family", "unknown"))
    checkpoint_count = int(run.get("checkpoint_count_loaded", 0))
    primitive_counts = _int_mapping(run.get("primitive_counts_by_type", {}))
    landscape_relationships = _int_mapping(run.get("landscape_relationship_counts", {}))
    motion_counts = _int_mapping(run.get("motion_record_counts", {}))
    motion_relationships = {
        observer: _int_mapping(counts)
        for observer, counts in dict(run.get("motion_relationship_counts", {})).items()
    }
    labels = _evidence_labels(
        key=key,
        runtime_family=runtime_family,
        checkpoint_count=checkpoint_count,
        motion_counts=motion_counts,
        motion_relationships=motion_relationships,
        visual_notes=tuple(str(note) for note in run.get("visual_notes", ())),
    )
    notes = _calibration_notes(
        key=key,
        runtime_family=runtime_family,
        checkpoint_count=checkpoint_count,
        labels=labels,
        motion_counts=motion_counts,
        motion_relationships=motion_relationships,
    )
    return MotionInterpretationRun(
        key=key,
        runtime_family=runtime_family,
        checkpoint_count=checkpoint_count,
        landscape_primitive_counts=primitive_counts,
        landscape_relationship_counts=landscape_relationships,
        motion_record_counts=motion_counts,
        motion_relationship_counts=motion_relationships,
        evidence_labels=labels,
        catalog_recommendation=_catalog_recommendation(labels),
        calibration_notes=notes,
        motion_report_dir=str(run.get("motion_report_dir", "")),
    )


def _promotion_run(
    run: Mapping[str, Any],
    *,
    max_daughter_count: int,
    min_confidence: float,
    min_provenance_continuity: float,
) -> MotionIdentityFissionPromotionRun:
    key = str(run.get("key", "unknown"))
    runtime_family = str(run.get("runtime_family", "unknown"))
    report_path = _report_path(run, "identity")
    summary_path = _summary_path(report_path)
    records = _identity_records(report_path)
    matches = _identity_matches(summary_path)
    split_records = tuple(record for record in records if record.get("relationship") == "split")
    rejected: Counter[str] = Counter()
    compact_candidates: list[Mapping[str, Any]] = []
    provenance_supported: list[Mapping[str, Any]] = []
    promoted: list[Mapping[str, Any]] = []
    for record in split_records:
        reasons = _promotion_rejection_reasons(
            record,
            matches,
            max_daughter_count=max_daughter_count,
            min_confidence=min_confidence,
            min_provenance_continuity=min_provenance_continuity,
        )
        if _compact_membership_ok(record, max_daughter_count=max_daughter_count):
            compact_candidates.append(record)
        if _provenance_support_ok(
            record,
            matches,
            min_provenance_continuity=min_provenance_continuity,
        ):
            provenance_supported.append(record)
        if not reasons:
            promoted.append(record)
        else:
            rejected.update(reasons)
    labels: set[str] = set()
    if promoted:
        labels.add("accepted_identity_fission_candidate")
    else:
        labels.add("no_identity_fission_promoted")
    if split_records and not compact_candidates:
        labels.add("compact_membership_missing")
    if compact_candidates and not provenance_supported:
        labels.add("provenance_linkage_missing")
    if rejected.get("new_basin_count_exceeds_limit", 0) > 0:
        labels.add("dense_fanout_rejected")
    if rejected.get("confidence_below_threshold", 0) > 0:
        labels.add("confidence_below_promotion_threshold")
    if not report_path:
        labels.add("identity_report_unavailable")
    if split_records and not promoted:
        labels.add("keep_carrier_branching_diagnostic")
    return MotionIdentityFissionPromotionRun(
        key=key,
        runtime_family=runtime_family,
        identity_report_path=str(report_path),
        identity_summary_path=str(summary_path),
        reviewed_split_record_count=len(split_records),
        compact_candidate_count=len(compact_candidates),
        provenance_supported_candidate_count=len(provenance_supported),
        promoted_identity_fission_count=len(promoted),
        rejected_reason_counts=dict(sorted(rejected.items())),
        promotion_labels=tuple(sorted(labels)),
        catalog_guidance=_promotion_catalog_guidance(labels),
        sample_promoted_motion_ids=tuple(
            str(record.get("motion_id", "")) for record in promoted[:5]
        ),
    )


def _promotion_rejection_reasons(
    record: Mapping[str, Any],
    matches: Sequence[Mapping[str, Any]],
    *,
    max_daughter_count: int,
    min_confidence: float,
    min_provenance_continuity: float,
) -> tuple[str, ...]:
    reasons: list[str] = []
    old_basin_count = len(_carrier_ids(record, "old_carriers", "basin_ids"))
    new_basin_count = len(_carrier_ids(record, "new_carriers", "basin_ids"))
    if old_basin_count != 1:
        reasons.append("old_basin_count_not_one")
    if new_basin_count < 2:
        reasons.append("new_basin_count_below_fission_minimum")
    if new_basin_count > max_daughter_count:
        reasons.append("new_basin_count_exceeds_limit")
    if float(record.get("confidence", 0.0)) < min_confidence:
        reasons.append("confidence_below_threshold")
    if str(record.get("evidence_quality", "")) != "strong":
        reasons.append("evidence_quality_not_strong")
    if float(record.get("transferred_mass", 0.0) or 0.0) <= 0.0:
        reasons.append("transferred_mass_absent")
    if not _provenance_support_ok(
        record,
        matches,
        min_provenance_continuity=min_provenance_continuity,
    ):
        reasons.append("provenance_linkage_insufficient")
    return tuple(sorted(set(reasons)))


def _compact_membership_ok(record: Mapping[str, Any], *, max_daughter_count: int) -> bool:
    old_basin_count = len(_carrier_ids(record, "old_carriers", "basin_ids"))
    new_basin_count = len(_carrier_ids(record, "new_carriers", "basin_ids"))
    return old_basin_count == 1 and 2 <= new_basin_count <= max_daughter_count


def _provenance_support_ok(
    record: Mapping[str, Any],
    matches: Sequence[Mapping[str, Any]],
    *,
    min_provenance_continuity: float,
) -> bool:
    old_ids = _carrier_ids(record, "old_carriers", "basin_ids")
    new_ids = set(_carrier_ids(record, "new_carriers", "basin_ids"))
    if len(old_ids) != 1 or len(new_ids) < 2:
        return False
    old_id = old_ids[0]
    supported_children = {
        str(match.get("new_group_id"))
        for match in matches
        if str(match.get("old_group_id")) == old_id
        and str(match.get("new_group_id")) in new_ids
        and str(match.get("new_group_id")) != old_id
        and float(match.get("hierarchy_provenance_continuity", 0.0)) >= min_provenance_continuity
    }
    return len(supported_children) >= 2


def _carrier_ids(record: Mapping[str, Any], carrier_key: str, id_key: str) -> tuple[str, ...]:
    carriers = record.get(carrier_key, {})
    if not isinstance(carriers, Mapping):
        return ()
    raw = carriers.get(id_key, ())
    if not isinstance(raw, Sequence) or isinstance(raw, str | bytes):
        return ()
    return tuple(str(item) for item in raw)


def _promotion_catalog_guidance(labels: set[str]) -> str:
    if "accepted_identity_fission_candidate" in labels:
        return "promote_supported_identity_fission_candidates"
    if "keep_carrier_branching_diagnostic" in labels:
        return "keep_dense_branching_diagnostic_not_identity_fission"
    if "identity_report_unavailable" in labels:
        return "promotion_unavailable_missing_identity_report"
    return "no_identity_fission_review_needed"


def _report_path(run: Mapping[str, Any], observer: str) -> Path:
    paths = tuple(str(path) for path in run.get("sample_motion_report_paths", ()) if path)
    suffix = f"/{observer}_report.json"
    for path in paths:
        if path.endswith(suffix):
            return Path(path)
    return Path()


def _summary_path(report_path: Path) -> Path:
    if not str(report_path):
        return Path()
    return report_path.with_name(report_path.name.replace("_report.json", "_summary.json"))


def _identity_records(report_path: Path) -> tuple[Mapping[str, Any], ...]:
    if not str(report_path) or not report_path.exists():
        return ()
    report = _read_json(report_path)
    records = report.get("records", ())
    if not isinstance(records, Sequence) or isinstance(records, str | bytes):
        return ()
    return tuple(record for record in records if isinstance(record, Mapping))


def _identity_matches(summary_path: Path) -> tuple[Mapping[str, Any], ...]:
    if not str(summary_path) or not summary_path.exists():
        return ()
    summary = _read_json(summary_path)
    matches = summary.get("matches", ())
    if not isinstance(matches, Sequence) or isinstance(matches, str | bytes):
        return ()
    return tuple(match for match in matches if isinstance(match, Mapping))


def _dense_calibration_run(
    run: Mapping[str, Any],
    *,
    record_count_threshold: int,
    identity_split_ratio_threshold: float,
) -> MotionDenseWindowCalibrationRun:
    key = str(run.get("key", "unknown"))
    runtime_family = str(run.get("runtime_family", "unknown"))
    checkpoint_count = int(run.get("checkpoint_count", run.get("checkpoint_count_loaded", 0)))
    motion_counts = _int_mapping(run.get("motion_record_counts", {}))
    relationships = {
        observer: _int_mapping(counts)
        for observer, counts in dict(run.get("motion_relationship_counts", {})).items()
    }
    total_motion_records = sum(motion_counts.values())
    identity_count = int(motion_counts.get("identity", 0))
    identity_split_count = int(relationships.get("identity", {}).get("split", 0))
    identity_split_ratio = (
        identity_split_count / identity_count if identity_count > 0 else 0.0
    )
    representative = relationships.get("representative", {})
    representative_count = int(motion_counts.get("representative", 0))
    representative_stationary_ratio = (
        representative.get("stationary", 0) / representative_count
        if representative_count > 0
        else None
    )
    dense_window = (
        total_motion_records >= record_count_threshold
        or identity_count >= record_count_threshold
    )
    labels: set[str] = set()
    if dense_window:
        labels.add("dense_branching_field")
    if dense_window and identity_split_count > 0:
        labels.add("dense_identity_split_review_needed")
    if identity_split_ratio >= identity_split_ratio_threshold and identity_count > 0:
        labels.add("identity_split_dominant")
    if dense_window and "identity_split_dominant" in labels:
        labels.add("catalog_as_dense_carrier_branching_not_fission")
        labels.add("needs_identity_membership_linkage")
    if (
        representative_stationary_ratio is not None
        and representative_stationary_ratio >= 0.80
        and identity_split_ratio >= identity_split_ratio_threshold
    ):
        labels.add("representative_stationary_identity_branching")
    if not dense_window and "identity_split_dominant" in labels:
        labels.add("split_dominant_small_window_review")
    if not labels:
        labels.add("no_dense_window_calibration_needed")
    return MotionDenseWindowCalibrationRun(
        key=key,
        runtime_family=runtime_family,
        checkpoint_count=checkpoint_count,
        total_motion_record_count=total_motion_records,
        identity_record_count=identity_count,
        identity_split_count=identity_split_count,
        identity_split_ratio=round(identity_split_ratio, 6),
        representative_stationary_ratio=(
            None
            if representative_stationary_ratio is None
            else round(representative_stationary_ratio, 6)
        ),
        dense_window=dense_window,
        calibration_labels=tuple(sorted(labels)),
        catalog_guidance=_dense_catalog_guidance(labels),
        sample_motion_report_paths=_sample_report_paths(run),
    )


def _dense_catalog_guidance(labels: set[str]) -> str:
    if "catalog_as_dense_carrier_branching_not_fission" in labels:
        return "catalog_dense_carrier_branching_as_diagnostic_not_identity_fission"
    if "dense_identity_split_review_needed" in labels:
        return "review_dense_identity_split_with_promotion_gate"
    if "split_dominant_small_window_review" in labels:
        return "review_split_dominance_before_identity_catalog_acceptance"
    if "no_dense_window_calibration_needed" in labels:
        return "no_dense_window_adjustment_needed"
    return "diagnostic_review_before_catalog"


def _sample_report_paths(run: Mapping[str, Any]) -> tuple[str, ...]:
    report_dir = str(run.get("motion_report_dir", ""))
    if not report_dir:
        return ()
    return tuple(
        f"{report_dir}/{name}_report.json"
        for name in ("identity", "representative", "topological")
    )


def _evidence_labels(
    *,
    key: str,
    runtime_family: str,
    checkpoint_count: int,
    motion_counts: Mapping[str, int],
    motion_relationships: Mapping[str, Mapping[str, int]],
    visual_notes: Sequence[str],
) -> tuple[str, ...]:
    labels: set[str] = {"landscape_motion_cross_summary_ready"}
    coherence_drift = motion_relationships.get("coherence", {}).get("drifted", 0)
    if coherence_drift > 0:
        labels.add("coherence_motion_accepted")
    topological = motion_relationships.get("topological", {})
    if topological.get("collapsed", 0) > 0:
        labels.add("topological_collapse_accepted")
    if topological.get("emerged", 0) > 0:
        labels.add("topological_emergence_accepted")
    if topological.get("split", 0) > 0:
        labels.add("topological_split_accepted")
    if topological.get("dissolved", 0) > 0:
        labels.add("topological_dissolution_accepted")
    boundary = motion_relationships.get("boundary", {})
    if boundary.get("drifted", 0) > 0 or boundary.get("emerged", 0) > 0:
        labels.add("boundary_motion_accepted")
    if runtime_family == "grcv3" and motion_counts.get("boundary", 0) == 0:
        labels.add("boundary_motion_family_limited")
    identity = motion_relationships.get("identity", {})
    identity_total = sum(identity.values())
    identity_split = identity.get("split", 0)
    if identity_split >= 50 or (identity_total >= 20 and identity_split / identity_total >= 0.80):
        labels.add("identity_split_overproduction_review")
    representative = motion_relationships.get("representative", {})
    if representative.get("stationary", 0) > 0 and representative.get("drifted", 0) == 0:
        labels.add("stationary_representative_context")
    if any("dense visual timelines are sampled" in note for note in visual_notes):
        labels.add("dense_timeline_sampled")
    if checkpoint_count >= 20:
        labels.add("long_window_motion_evidence")
    if "relay" in key and "topological_emergence_accepted" in labels:
        labels.add("dynamic_relay_motion_case_study")
    return tuple(sorted(labels))


def _calibration_notes(
    *,
    key: str,
    runtime_family: str,
    checkpoint_count: int,
    labels: Sequence[str],
    motion_counts: Mapping[str, int],
    motion_relationships: Mapping[str, Mapping[str, int]],
) -> tuple[str, ...]:
    notes: list[str] = []
    if "identity_split_overproduction_review" in labels:
        notes.append(
            "Dense identity windows currently emit many split-style carrier records; "
            "catalog review should distinguish structural branching from accepted fission."
        )
    if "boundary_motion_family_limited" in labels:
        notes.append(
            "Boundary motion is diagnostic-only for this GRCV3 run because port/frontier "
            "evidence is not exposed in the same way as GRC9/GRC9V3."
        )
    if "coherence_motion_accepted" in labels:
        notes.append(
            "Coherence drift is the most stable cross-family signal in this interpretation pass."
        )
    if "stationary_representative_context" in labels:
        notes.append(
            "Stationary representatives provide context: carrier identity may branch while "
            "the selected representative remains fixed."
        )
    if checkpoint_count >= 20 and motion_counts.get("coherence", 0) > 0:
        notes.append(
            "Long-window evidence supports temporal interpretation beyond two-checkpoint diagnostics."
        )
    if runtime_family == "grc9v3" and motion_relationships.get("boundary", {}).get("drifted", 0) > 0:
        notes.append(
            "GRC9V3 port/frontier evidence makes boundary drift visible as a motion surface."
        )
    if "collapsed" in motion_relationships.get("topological", {}):
        notes.append(
            "Topological collapse is accepted as topology evidence; identity continuity remains "
            "a separate observer claim."
        )
    if not notes:
        notes.append(f"{key} remains diagnostic until stronger observer agreement is available.")
    return tuple(notes)


def _catalog_recommendation(labels: Sequence[str]) -> str:
    label_set = set(labels)
    if "topological_collapse_accepted" in label_set:
        return "accept_topological_collapse_with_identity_calibration"
    if "identity_split_overproduction_review" in label_set:
        return "review_identity_split_with_promotion_gate"
    if "dynamic_relay_motion_case_study" in label_set:
        return "accept_dynamic_relay_motion_with_identity_split_caveat"
    if "boundary_motion_family_limited" in label_set:
        return "accept_coherence_and_topology_family_limited_boundary"
    if {"coherence_motion_accepted", "boundary_motion_accepted"} <= label_set:
        return "accept_dynamic_landscape_motion_with_caveats"
    if "coherence_motion_accepted" in label_set:
        return "accept_coherence_motion_only"
    return "diagnostic_review_before_catalog"


def _aggregate_mapping(runs: Sequence[MotionInterpretationRun]) -> dict[str, Any]:
    primitive_counts: Counter[str] = Counter()
    landscape_relationships: Counter[str] = Counter()
    observer_counts: Counter[str] = Counter()
    labels: Counter[str] = Counter()
    catalog_recommendations: Counter[str] = Counter()
    runtime_families: Counter[str] = Counter()
    for run in runs:
        primitive_counts.update(run.landscape_primitive_counts)
        landscape_relationships.update(run.landscape_relationship_counts)
        observer_counts.update(run.motion_record_counts)
        labels.update(run.evidence_labels)
        catalog_recommendations.update((run.catalog_recommendation,))
        runtime_families.update((run.runtime_family,))
    return canonicalize_json_value(
        {
            "runtime_family_counts": dict(sorted(runtime_families.items())),
            "landscape_primitive_counts": dict(sorted(primitive_counts.items())),
            "landscape_relationship_counts": dict(sorted(landscape_relationships.items())),
            "motion_record_counts": dict(sorted(observer_counts.items())),
            "evidence_label_counts": dict(sorted(labels.items())),
            "catalog_recommendation_counts": dict(sorted(catalog_recommendations.items())),
            "interpretation_notes": [
                "Motion interpretation does not create new runtime evidence.",
                "Identity split overproduction is a calibration flag, not an automatic rejection.",
                "Boundary motion is family-sensitive because GRC9/GRC9V3 expose port/frontier surfaces.",
            ],
        }
    )


def _dense_aggregate_mapping(runs: Sequence[MotionDenseWindowCalibrationRun]) -> dict[str, Any]:
    labels: Counter[str] = Counter()
    guidance: Counter[str] = Counter()
    for run in runs:
        labels.update(run.calibration_labels)
        guidance.update((run.catalog_guidance,))
    return canonicalize_json_value(
        {
            "calibration_label_counts": dict(sorted(labels.items())),
            "catalog_guidance_counts": dict(sorted(guidance.items())),
            "dense_window_keys": [run.key for run in runs if run.dense_window],
            "identity_split_dominant_keys": [
                run.key for run in runs if "identity_split_dominant" in run.calibration_labels
            ],
            "interpretation_notes": [
                "Dense-window calibration does not rewrite raw motion records.",
                "Dense split-dominant identity output is treated as carrier branching evidence.",
                "Accepted identity fission requires later membership/provenance linkage.",
            ],
        }
    )


def _promotion_aggregate_mapping(runs: Sequence[MotionIdentityFissionPromotionRun]) -> dict[str, Any]:
    labels: Counter[str] = Counter()
    guidance: Counter[str] = Counter()
    rejected: Counter[str] = Counter()
    for run in runs:
        labels.update(run.promotion_labels)
        guidance.update((run.catalog_guidance,))
        rejected.update(run.rejected_reason_counts)
    return canonicalize_json_value(
        {
            "promotion_label_counts": dict(sorted(labels.items())),
            "catalog_guidance_counts": dict(sorted(guidance.items())),
            "rejected_reason_counts": dict(sorted(rejected.items())),
            "promoted_keys": [
                run.key for run in runs if run.promoted_identity_fission_count > 0
            ],
            "not_promoted_keys": [
                run.key
                for run in runs
                if run.reviewed_split_record_count > 0 and run.promoted_identity_fission_count == 0
            ],
            "interpretation_notes": [
                "Promotion is conservative and reads existing identity reports only.",
                "Broad fan-out split records remain carrier-branching diagnostics.",
                "Identity fission promotion requires compact daughters and provenance continuity.",
            ],
        }
    )


def _summary_markdown(session: MotionInterpretationSession) -> str:
    aggregate = _aggregate_mapping(session.runs)
    lines = [
        "# Motion Interpretation Summary",
        "",
        f"- session: `{session.session_id}`",
        f"- version: `{MOTION_INTERPRETATION_VERSION}`",
        f"- source summary: `{session.source_summary_path}`",
        "- authority: interpretation over existing observed landscape and motion summaries",
        "",
        "## Aggregate",
        "",
        f"- runtime families: `{aggregate['runtime_family_counts']}`",
        f"- landscape primitives: `{aggregate['landscape_primitive_counts']}`",
        f"- motion records: `{aggregate['motion_record_counts']}`",
        f"- evidence labels: `{aggregate['evidence_label_counts']}`",
        "",
        "## Runs",
        "",
    ]
    for run in session.runs:
        lines.extend(
            [
                f"### {run.key}",
                "",
                f"- runtime family: `{run.runtime_family}`",
                f"- checkpoints: `{run.checkpoint_count}`",
                f"- landscape primitives: `{dict(run.landscape_primitive_counts)}`",
                f"- motion records: `{dict(run.motion_record_counts)}`",
                f"- motion relationships: `{ {k: dict(v) for k, v in run.motion_relationship_counts.items()} }`",
                f"- evidence labels: `{list(run.evidence_labels)}`",
                f"- catalog recommendation: `{run.catalog_recommendation}`",
                "",
                "Calibration notes:",
                "",
            ]
        )
        lines.extend(f"- {note}" for note in run.calibration_notes)
        lines.append("")
    return "\n".join(lines)


def _promotion_markdown(session: MotionIdentityFissionPromotionSession) -> str:
    aggregate = _promotion_aggregate_mapping(session.runs)
    lines = [
        "# Identity Fission Promotion Audit",
        "",
        f"- session: `{session.session_id}`",
        f"- version: `{MOTION_IDENTITY_FISSION_PROMOTION_VERSION}`",
        f"- source dense calibration: `{session.source_dense_calibration_path}`",
        f"- max daughter count: `{session.max_daughter_count}`",
        f"- min confidence: `{session.min_confidence}`",
        f"- min provenance continuity: `{session.min_provenance_continuity}`",
        "",
        "## Aggregate",
        "",
        f"- promoted keys: `{aggregate['promoted_keys']}`",
        f"- not-promoted keys: `{aggregate['not_promoted_keys']}`",
        f"- promotion labels: `{aggregate['promotion_label_counts']}`",
        f"- rejected reasons: `{aggregate['rejected_reason_counts']}`",
        "",
        "## Runs",
        "",
    ]
    for run in session.runs:
        lines.extend(
            [
                f"### {run.key}",
                "",
                f"- runtime family: `{run.runtime_family}`",
                f"- reviewed split records: `{run.reviewed_split_record_count}`",
                f"- compact candidates: `{run.compact_candidate_count}`",
                f"- provenance-supported candidates: `{run.provenance_supported_candidate_count}`",
                f"- promoted identity fission count: `{run.promoted_identity_fission_count}`",
                f"- rejected reasons: `{dict(run.rejected_reason_counts)}`",
                f"- promotion labels: `{list(run.promotion_labels)}`",
                f"- catalog guidance: `{run.catalog_guidance}`",
                f"- identity report: `{run.identity_report_path}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Catalog Rule",
            "",
            "Identity fission promotion requires compact daughter membership,",
            "strong confidence, positive transferred mass, and provenance linkage",
            "from the old identity to at least two daughter identities. Dense",
            "fan-out records that fail this gate remain carrier-branching",
            "diagnostics.",
            "",
        ]
    )
    return "\n".join(lines)


def _dense_calibration_markdown(session: MotionDenseWindowCalibrationSession) -> str:
    aggregate = _dense_aggregate_mapping(session.runs)
    lines = [
        "# Dense-Window Motion Calibration",
        "",
        f"- session: `{session.session_id}`",
        f"- version: `{MOTION_DENSE_WINDOW_CALIBRATION_VERSION}`",
        f"- source interpretation: `{session.source_interpretation_path}`",
        f"- record-count threshold: `{session.record_count_threshold}`",
        f"- identity split-ratio threshold: `{session.identity_split_ratio_threshold}`",
        "",
        "## Aggregate",
        "",
        f"- dense windows: `{aggregate['dense_window_keys']}`",
        f"- split-dominant windows: `{aggregate['identity_split_dominant_keys']}`",
        f"- calibration labels: `{aggregate['calibration_label_counts']}`",
        f"- catalog guidance: `{aggregate['catalog_guidance_counts']}`",
        "",
        "## Runs",
        "",
    ]
    for run in session.runs:
        lines.extend(
            [
                f"### {run.key}",
                "",
                f"- runtime family: `{run.runtime_family}`",
                f"- checkpoints: `{run.checkpoint_count}`",
                f"- total motion records: `{run.total_motion_record_count}`",
                f"- identity records: `{run.identity_record_count}`",
                f"- identity split ratio: `{run.identity_split_ratio}`",
                f"- representative stationary ratio: `{run.representative_stationary_ratio}`",
                f"- dense window: `{run.dense_window}`",
                f"- calibration labels: `{list(run.calibration_labels)}`",
                f"- catalog guidance: `{run.catalog_guidance}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Catalog Rule",
            "",
            "Dense split-dominant identity records are cataloged as carrier",
            "branching diagnostics unless a later identity-membership/provenance",
            "linkage pass promotes them to accepted identity fission.",
            "",
        ]
    )
    return "\n".join(lines)

def _knowledge_graph_case_study(session: MotionInterpretationSession) -> str:
    run = _case_study_run(session.runs)
    if run is None:
        return "# Knowledge Graph Motion Case Study\n\nNo interpreted runs were available.\n"
    lines = [
        "# Knowledge Graph Motion Case Study",
        "",
        f"Case study run: `{run.key}`.",
        "",
        "A landscape seed describes graph structure in neutral terms such as basins,",
        "valleys, junctions, ridges, and frontiers. Motion interpretation asks how",
        "those observed structures change over a checkpoint window. In this run the",
        "landscape layer provides the static vocabulary, while motion observers add",
        "temporal evidence.",
        "",
        "## Observed Structure",
        "",
        f"- runtime family: `{run.runtime_family}`",
        f"- checkpoints: `{run.checkpoint_count}`",
        f"- landscape primitives: `{dict(run.landscape_primitive_counts)}`",
        f"- landscape relationships: `{dict(run.landscape_relationship_counts)}`",
        "",
        "## Motion Reading",
        "",
        f"- motion records: `{dict(run.motion_record_counts)}`",
        f"- motion relationships: `{ {k: dict(v) for k, v in run.motion_relationship_counts.items()} }`",
        f"- evidence labels: `{list(run.evidence_labels)}`",
        "",
        "Interpretation:",
        "",
    ]
    if "dynamic_relay_motion_case_study" in run.evidence_labels:
        lines.extend(
            [
                "- This is an accepted dynamic relay example: coherence moves across a",
                "  landscape with many inferred basins, valleys, saddles, and junctions.",
                "- Topological emergence shows that the support changes, not just the",
                "  scalar coherence values.",
                "- The identity observer emits many split-style records. That is useful",
                "  diagnostic evidence for branching carriers, but catalog review should",
                "  not equate every split-style carrier record with a fully accepted",
                "  identity fission.",
            ]
        )
    else:
        lines.append(
            "- This run is best read through its strongest accepted labels and the "
            "calibration notes below."
        )
    lines.extend(["", "Calibration notes:", ""])
    lines.extend(f"- {note}" for note in run.calibration_notes)
    lines.extend(
        [
            "",
            "Claim boundary: this case study explains existing observed motion and",
            "landscape summaries. It does not create additional runtime, source, or",
            "visual-only claims.",
            "",
        ]
    )
    return "\n".join(lines)


def _case_study_run(
    runs: Sequence[MotionInterpretationRun],
) -> MotionInterpretationRun | None:
    for run in runs:
        if "dynamic_relay_motion_case_study" in run.evidence_labels:
            return run
    if not runs:
        return None
    return max(runs, key=lambda run: run.checkpoint_count)


def _summary_runs(summary: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    runs = summary.get("runs", ())
    if not isinstance(runs, Sequence) or isinstance(runs, str | bytes):
        raise ValueError("motion landscape summary must contain a runs sequence")
    return tuple(run for run in runs if isinstance(run, Mapping))


def _int_mapping(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    return dict(sorted((str(key), int(raw)) for key, raw in value.items()))


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json_dumps(payload), encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--session-root",
        default=str(DEFAULT_MOTION_INTERPRETATION_SESSION_ROOT),
        help="Motion session root containing landscape_motion_summary.json.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional interpretation output directory.",
    )
    parser.add_argument(
        "--dense-calibration",
        action="store_true",
        help="Also write Iteration 12.3 dense-window calibration artifacts.",
    )
    parser.add_argument(
        "--promote-identity-fission",
        action="store_true",
        help="Also write Iteration 12.4 identity-fission promotion artifacts.",
    )
    args = parser.parse_args(argv)
    session = run_motion_interpretation_session(
        session_root=args.session_root,
        output_dir=args.output_dir,
    )
    if args.dense_calibration:
        run_motion_dense_window_calibration_session(
            session_root=args.session_root,
            output_dir=args.output_dir,
        )
    if args.promote_identity_fission:
        run_motion_identity_fission_promotion_session(
            session_root=args.session_root,
            output_dir=args.output_dir,
        )
    print(str(session.interpretation_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_MOTION_INTERPRETATION_DIRNAME",
    "DEFAULT_MOTION_INTERPRETATION_SESSION_ROOT",
    "MOTION_DENSE_WINDOW_CALIBRATION_VERSION",
    "MOTION_IDENTITY_FISSION_PROMOTION_VERSION",
    "MOTION_INTERPRETATION_VERSION",
    "MotionDenseWindowCalibrationRun",
    "MotionDenseWindowCalibrationSession",
    "MotionIdentityFissionPromotionRun",
    "MotionIdentityFissionPromotionSession",
    "MotionInterpretationRun",
    "MotionInterpretationSession",
    "run_motion_identity_fission_promotion_session",
    "run_motion_dense_window_calibration_session",
    "run_motion_interpretation_session",
]
